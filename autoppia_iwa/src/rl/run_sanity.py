import asyncio
import json
from typing import Any

from playwright.async_api import async_playwright

# ---- pretty printing with rich ----
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
from autoppia_iwa.src.rl.rewards.step_delta import make_delta_reward

console = Console()


def _short(s: str, n: int = 120) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def _state_table(obs: dict[str, Any]) -> Table:
    step_val = int(obs.get("step") or 0)
    t = Table(title=f"STATE — Step {step_val}", expand=True, show_header=False)
    t.add_row("URL", _short(obs.get("url", ""), 140))
    t.add_row("Prompt", _short(obs.get("task_prompt", ""), 140))
    t.add_row("Step", str(step_val))
    html = obs.get("html") or ""
    t.add_row("HTML size", f"{len(html):,} chars" if html else "0")
    return t


def _action_panel(action_dict: dict[str, Any]) -> Panel:
    return Panel.fit(
        JSON.from_data(action_dict),
        title="ACTION (agent output)",
        border_style="cyan",
    )


def _eval_table(info: dict[str, Any]) -> Table:
    t = Table(title="EVAL / REWARD", expand=True)
    t.add_column("Field", style="bold")
    t.add_column("Value")

    t.add_row("score", f"{info.get('score', 0.0):.3f}")
    t.add_row("delta", f"{info.get('delta', 0.0):.3f}")
    t.add_row("tests", f"{info.get('tests_passed', 0)} / {info.get('tests_total', 0)}")

    events = info.get("events") or []
    if events:
        t.add_row("events", ", ".join(events))
    if "exec_error" in info:
        t.add_row("exec_error", Text(str(info["exec_error"]), style="red"))
    if "rl_eval_error" in info:
        t.add_row("rl_eval_error", Text(str(info["rl_eval_error"]), style="yellow"))
    if "reward_fn_error" in info:
        t.add_row("reward_fn_error", Text(str(info["reward_fn_error"]), style="yellow"))

    return t


async def reset_to_home(executor: PlaywrightBrowserExecutor, task):
    if executor.backend_demo_webs_service:
        await executor.backend_demo_webs_service.reset_database()
    start_url = getattr(task, "url", "") or getattr(task, "frontend_url", "") or "about:blank"
    if executor.page:
        await executor.page.goto(start_url)


async def main():
    # 1) Selecciona proyecto
    project = next((p for p in demo_web_projects if p.id == "dining"), None)
    assert project, "Dining project not found"

    # 2) Task mínima (puede no tener tests; el evaluador ya lo tolera)
    class T: ...

    task = T()
    task.prompt = "Scroll the homepage and wait briefly"
    task.url = project.frontend_url
    task.frontend_url = project.frontend_url

    # 3) Abre Playwright y crea executor
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        backend = BackendDemoWebService(project)
        executor = PlaywrightBrowserExecutor(
            browser_config=BrowserSpecification(),
            page=page,
            backend_demo_webs_service=backend,
        )

        reward_fn = make_delta_reward(success_threshold=1.0)

        env = AsyncWebAgentEnv(
            executor=executor,
            task_sampler=lambda: task,
            reward_fn=reward_fn,
            reset_fn=reset_to_home,
            H=320,
            W=320,
            max_steps=8,
            action_mode="json",
            safe_action_types=["WaitAction", "ScrollAction"],  # evitamos clicks frágiles en sanity
            history_k=3,
        )

        try:
            # ---- RESET ----
            obs, info = await env.areset(options={"task": task, "prompt": task.prompt})
            console.rule("[bold green]RESET")
            console.print(_state_table(obs))

            # ---- ROLLOUT (acciones de ejemplo robustas) ----
            actions = [
                {"type": "WaitAction", "time_seconds": 0.2},
                {"type": "ScrollAction", "down": True, "value": None},
                {"type": "WaitAction", "time_seconds": 0.2},
            ]
            for a in actions:
                console.rule(f"[bold blue]STEP {int(obs.get('step') or 0) + 1}")
                console.print(_state_table(obs))
                console.print(_action_panel(a))

                # Ejecuta paso
                obs, r, d, t, step_info = await env.astep(json.dumps(a))

                # Eval view
                eval_tbl = _eval_table(step_info)
                footer = Table.grid()
                footer.add_row(f"[bold]reward[/]: {r:.3f}   [bold]done[/]: {d}   [bold]truncated[/]: {t}")
                console.print(eval_tbl)
                console.print(Panel(footer, title="Step summary", border_style="magenta"))

                if d or t:
                    console.rule("[bold red]TERMINATED")
                    break

        finally:
            # Cierre limpio (evita aiohttp warnings)
            try:
                if executor.backend_demo_webs_service:
                    await executor.backend_demo_webs_service.close()
            finally:
                await context.close()
                await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
