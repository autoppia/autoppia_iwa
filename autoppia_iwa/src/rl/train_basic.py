import asyncio
import json
from typing import Any

from playwright.async_api import async_playwright

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
from autoppia_iwa.src.rl.policies.basic import BasicPolicy
from autoppia_iwa.src.rl.rewards.step_delta import make_delta_reward


async def reset_to_home(executor, task):
    if executor.backend_demo_webs_service:
        await executor.backend_demo_webs_service.reset_database()
    start_url = getattr(task, "url", "") or getattr(task, "frontend_url", "") or "about:blank"
    if executor.page:
        await executor.page.goto(start_url)


async def rollout(env: AsyncWebAgentEnv, policy: BasicPolicy, max_steps: int = 20) -> dict[str, Any]:
    traj = {"obs": [], "acts": [], "rews": []}
    # Toma la task actual del sampler
    task = env.task_sampler()
    obs, _ = await env.areset(options={"task": task, "prompt": getattr(task, "prompt", "")})
    for _ in range(max_steps):
        a_dict = await policy.act(obs)
        a_json = json.dumps(a_dict)
        traj["obs"].append(obs)
        act_idx = policy.action_index(a_dict)
        traj["acts"].append(act_idx)
        obs, r, d, t, info = await env.astep(a_json)
        traj["rews"].append(float(r))
        if d or t:
            break
    return traj


async def main():
    project = next((p for p in demo_web_projects if p.id == "dining"), None)
    assert project, "Dining project not found"

    # Construye una Task simple
    class T:
        pass

    taskA = T()
    taskA.prompt = "Search restaurants"
    taskA.url = project.frontend_url
    taskB = T()
    taskB.prompt = "Book a restaurant"
    taskB.url = project.frontend_url
    tasks = [taskA, taskB]
    idx = -1

    def task_sampler():
        nonlocal idx
        idx = (idx + 1) % len(tasks)
        return tasks[idx]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        executor = PlaywrightBrowserExecutor(
            browser_config=BrowserSpecification(),
            page=page,
            backend_demo_webs_service=BackendDemoWebService(project),
        )

        reward_fn = make_delta_reward(success_threshold=1.0)
        env = AsyncWebAgentEnv(
            executor=executor,
            task_sampler=task_sampler,
            reward_fn=reward_fn,
            reset_fn=reset_to_home,
            H=320,
            W=320,
            max_steps=20,
            action_mode="json",
            safe_action_types=["WaitAction", "ScrollAction", "ClickAction", "TypeAction", "HoverAction", "SubmitAction"],
            history_k=5,
        )

        policy = BasicPolicy(lr=3e-3, seed=0)

        EPISODES = 20
        BATCH = 5
        for ep in range(0, EPISODES, BATCH):
            batch = []
            for _ in range(BATCH):
                traj = await rollout(env, policy, max_steps=20)
                batch.append(traj)
            stats = policy.update(batch, gamma=0.99)
            print(f"[train] ep={ep + BATCH:04d} loss={stats['loss']:.4f} avg_return={stats['avg_return']:.3f} avg_len={stats['avg_len']:.1f}")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
