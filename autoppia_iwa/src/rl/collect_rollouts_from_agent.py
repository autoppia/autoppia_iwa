"""
Collect trajectories from your external IWebAgent (heuristics) and write a JSONL dataset.

Each JSONL line:
{
  "project_id": str,
  "task_id": str,
  "prompt": str,
  "transitions": [
    {
      "obs": {"url","task_prompt","step","html_size"},
      "action": <dict>,
      "reward": float,
      "done": bool,
      "eval_info": {"score","delta","events","tests_total","tests_passed"}
    }
  ]
}
"""

import asyncio
import contextlib
import json
from typing import Any

from playwright.async_api import async_playwright

from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
from autoppia_iwa.src.rl.rewards.step_delta import make_delta_reward
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# ====== USER CONFIG ======
PROJECT_ID = "dining"
OUTPUT_JSONL = "heuristic_rollouts.jsonl"
MAX_STEPS_PER_TASK = 40
SAFE_ACTION_TYPES = [
    "WaitAction",
    "ScrollAction",
    "ClickAction",
    "TypeAction",
    "HoverAction",
    "SubmitAction",
    "NavigateAction",
    # allow dropdown helpers produced by your external agent:
    "GetDropDownOptionsAction",
    "SelectDropDownOptionAction",
]
AGENT_NAME = "autoppia_agent"
AGENT_HOST = "http://84.247.180.192"
AGENT_PORT = 6789
AGENT_TIMEOUT = 180
# =========================


def _sanitize_host(h: str) -> str:
    return h.replace("http://", "").replace("https://", "").rstrip("/")


def _obs_min(obs: dict[str, Any]) -> dict[str, Any]:
    html = obs.get("html") or ""
    return {
        "url": obs.get("url", ""),
        "task_prompt": obs.get("task_prompt", ""),
        "step": int(obs.get("step") or 0),
        "html_size": len(html),
    }


def _action_to_dict(a: Any) -> dict[str, Any]:
    """
    Normalize any action (Pydantic model or already-dict) to a plain dict safe for JSON and Env.
    - If it's a Pydantic model (v2), use .model_dump().
    - Ensure 'type' discriminator is present.
    - Strip private attrs if any.
    """
    if isinstance(a, dict):
        # Make a shallow copy to avoid side-effects
        out = dict(a)
        if "type" not in out and "action" in out and isinstance(out["action"], dict):
            t = out["action"].get("type")
            if t:
                out["type"] = t
        return out

    # Pydantic v2 BaseModel support
    if hasattr(a, "model_dump") and callable(a.model_dump):
        out = a.model_dump()
        # Some models keep the type as a class attribute or field; enforce presence
        t = out.get("type", None) or getattr(a, "type", None)
        if t:
            out["type"] = t
        # Remove Pydantic private fields if any slipped in
        for k in list(out.keys()):
            if k.startswith("_"):
                out.pop(k, None)
        # Normalize nested models (selector, etc.) if they are BaseModels
        if "selector" in out and hasattr(out["selector"], "model_dump"):
            out["selector"] = out["selector"].model_dump()
        if "action" in out and hasattr(out["action"], "model_dump"):
            out["action"] = out["action"].model_dump()
        return out

    # Fallback: try generic attribute dict
    d = getattr(a, "__dict__", None)
    if isinstance(d, dict):
        out = {k: v for k, v in d.items() if not k.startswith("_")}
        t = out.get("type", None) or getattr(a, "type", None)
        if t:
            out["type"] = t
        # Best effort for nested selector
        sel = out.get("selector")
        if sel is not None and hasattr(sel, "model_dump"):
            out["selector"] = sel.model_dump()
        return out

    # Last resort: string round-trip if it's a JSON-ish object (avoid if possible)
    try:
        return json.loads(str(a))
    except Exception as err:
        raise TypeError(f"Unsupported action type for serialization: {type(a)}") from err


async def reset_to_home(executor: PlaywrightBrowserExecutor, task):
    if executor.backend_demo_webs_service:
        await executor.backend_demo_webs_service.reset_database()
    start_url = getattr(task, "url", "") or getattr(task, "frontend_url", "") or "about:blank"
    if executor.page:
        await executor.page.goto(start_url)


async def _replay_solution_for_task(project, task, agent: ApifiedWebAgent, fjsonl):
    # Ask the agent for a solution (actions list)
    prepared = task.prepare_for_agent(agent.id) if hasattr(task, "prepare_for_agent") else task
    solution = await agent.solve_task(prepared)
    if not solution or not solution.actions:
        return

    # Build a small one-off env for this task (fresh page/context), replay solution into env (so we get rewards/events)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        backend = BackendDemoWebService(project)
        executor = PlaywrightBrowserExecutor(BrowserSpecification(), page, backend)

        reward_fn = make_delta_reward(success_threshold=1.0)
        env = AsyncWebAgentEnv(
            executor=executor,
            task_sampler=lambda: task,
            reward_fn=reward_fn,
            reset_fn=reset_to_home,
            H=320,
            W=320,
            max_steps=MAX_STEPS_PER_TASK,
            action_mode="json",
            safe_action_types=SAFE_ACTION_TYPES,
            history_k=5,
        )

        transitions = []
        try:
            obs, _ = await env.areset(options={"task": task, "prompt": task.prompt})

            for steps, a in enumerate(solution.actions or [], start=1):
                if steps > MAX_STEPS_PER_TASK:
                    break

                a_dict = _action_to_dict(a)  # <-- normalize to dict
                obs, r, d, t, info = await env.astep(a_dict)

                transitions.append(
                    {
                        "obs": _obs_min(obs),
                        "action": a_dict,  # store normalized dict
                        "reward": float(r),
                        "done": bool(d or t),
                        "eval_info": {k: v for k, v in info.items() if k in ("score", "delta", "events", "tests_total", "tests_passed")},
                    }
                )

                if d or t:
                    break

        finally:
            # Ensure resources are always closed
            with contextlib.suppress(Exception):
                await env.aclose()
            with contextlib.suppress(Exception):
                await context.close()
            with contextlib.suppress(Exception):
                await browser.close()

        rec = {
            "project_id": project.id,
            "task_id": task.id,
            "prompt": task.prompt,
            "transitions": transitions,
        }
        fjsonl.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"Saved task {task.id}: {len(transitions)} steps")


async def main():
    project = next((p for p in demo_web_projects if p.id == PROJECT_ID), None)
    assert project, f"Project '{PROJECT_ID}' not found"

    host = _sanitize_host(AGENT_HOST)
    agent = ApifiedWebAgent(id="heur-1", name=AGENT_NAME, host=host, port=AGENT_PORT, timeout=AGENT_TIMEOUT)

    tasks = await generate_tasks_for_project(
        project=project,
        use_cached=True,
        cache_dir=".",
        prompts_per_use_case=1,
        num_use_cases=0,  # all
    )
    if not tasks:
        print("No tasks generated.")
        return

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as fjsonl:
        # Iterate tasks and replay
        for task in tasks:
            await _replay_solution_for_task(project, task, agent, fjsonl)

    print(f"\nDataset saved to {OUTPUT_JSONL}")


if __name__ == "__main__":
    asyncio.run(main())
