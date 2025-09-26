"""
Load a trained BC policy and run it inside the AsyncWebAgentEnv across a few tasks.
Shows per-task summary (steps, final score if available).

Usage:
  python -m autoppia_iwa.src.rl.run_bc_agent
"""

import asyncio
import json
from typing import Any

import torch
from playwright.async_api import async_playwright

from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
from autoppia_iwa.src.rl.policies.bc import ActionVocab, BCPolicy
from autoppia_iwa.src.rl.rewards.step_delta import make_delta_reward

# ====== USER AREA ======
PROJECT_ID = "dining"
WEIGHTS = "bc_policy.pt"
VOCAB = "bc_vocab.json"
MAX_STEPS = 30
NUM_TASKS = 5  # how many tasks to try
# =======================


async def reset_to_home(executor: PlaywrightBrowserExecutor, task):
    if executor.backend_demo_webs_service:
        await executor.backend_demo_webs_service.reset_database()
    start_url = getattr(task, "url", "") or getattr(task, "frontend_url", "") or "about:blank"
    if executor.page:
        await executor.page.goto(start_url)


async def run_task(project, task, policy: BCPolicy) -> dict[str, Any]:
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
            max_steps=MAX_STEPS,
            action_mode="json",
            safe_action_types=["WaitAction", "ScrollAction", "ClickAction", "TypeAction", "HoverAction", "SubmitAction", "NavigateAction"],
            history_k=5,
        )

        try:
            obs, _ = await env.areset(options={"task": task, "prompt": task.prompt})
            total_r = 0.0
            steps = 0
            while steps < MAX_STEPS:
                steps += 1
                a = await policy.act(obs)
                obs, r, d, t, info = await env.astep(json.dumps(a))
                total_r += float(r)
                if d or t:
                    break

            return {
                "task_id": task.id,
                "prompt": task.prompt,
                "steps": steps,
                "total_reward": total_r,
                "final_score": info.get("score", 0.0),
                "tests": (info.get("tests_passed", 0), info.get("tests_total", 0)),
            }
        finally:
            try:
                if executor.backend_demo_webs_service:
                    await executor.backend_demo_webs_service.close()
            finally:
                await context.close()
                await browser.close()


async def main():
    # Load policy + vocab
    with open(VOCAB, encoding="utf-8") as f:
        actions_json: list[str] = json.load(f)

    vocab = ActionVocab([json.loads(s) for s in actions_json])
    policy = BCPolicy(vocab=vocab, lr=3e-3, device="cpu")
    policy.load_state_dict(torch.load(WEIGHTS, map_location="cpu"))

    # Select project + tasks
    project = next((p for p in demo_web_projects if p.id == PROJECT_ID), None)
    assert project, f"Project '{PROJECT_ID}' not found"
    tasks = await generate_tasks_for_project(project, use_cached=True, cache_dir=".", prompts_per_use_case=1, num_use_cases=0)
    tasks = tasks[:NUM_TASKS] if NUM_TASKS else tasks

    # Run
    results = []
    for task in tasks:
        res = await run_task(project, task, policy)
        print(f"[BC] task={res['task_id']} steps={res['steps']} total_r={res['total_reward']:.3f} score={res['final_score']:.3f} tests={res['tests'][0]}/{res['tests'][1]}")
        results.append(res)

    # Simple aggregate
    if results:
        avg_r = sum(r["total_reward"] for r in results) / len(results)
        avg_s = sum(r["final_score"] for r in results) / len(results)
        print(f"\nBC summary: avg_total_reward={avg_r:.3f} avg_final_score={avg_s:.3f} over {len(results)} tasks")


if __name__ == "__main__":
    asyncio.run(main())
