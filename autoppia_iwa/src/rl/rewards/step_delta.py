from typing import Any

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.rl.eval import RLEvaluator


def make_delta_reward(
    *,
    success_threshold: float = 1.0,
    success_bonus: float = 1.0,
    exec_fail_penalty: float = 0.02,
):
    rl_eval: RLEvaluator | None = None
    prev_score: float = 0.0

    async def reward_fn(
        *,
        task: Any,
        step_idx: int,
        last_action_dict: dict[str, Any],
        last_action_obj: BaseAction | None,
        executor: PlaywrightBrowserExecutor,
        trajectory: list[dict[str, Any]],
        obs: dict[str, Any],
        result: ActionExecutionResult | None,
    ) -> tuple[float, bool, dict[str, Any]]:
        nonlocal rl_eval, prev_score
        if rl_eval is None:
            if not executor.backend_demo_webs_service:
                raise RuntimeError("Executor has no backend_demo_webs_service")
            rl_eval = RLEvaluator(executor.backend_demo_webs_service, "env")
            await rl_eval.attach_task(task)

        score, _ = await rl_eval.partial_score()
        delta = score - prev_score
        prev_score = score

        r, done = float(delta), (score >= success_threshold)

        # Enriched info for debugging; suppress “no tests” noise gracefully
        info: dict[str, Any] = {
            "score": float(score),
            "delta": float(delta),
            "events": list(rl_eval.last_events_meta),
            "tests_total": int(rl_eval.last_num_tests),
            "tests_passed": int(rl_eval.last_passed),
        }
        if rl_eval.last_error and "no attribute 'tests'" not in rl_eval.last_error and "no_task_attached" not in rl_eval.last_error:
            info["rl_eval_error"] = rl_eval.last_error

        if result and not result.successfully_executed:
            r -= exec_fail_penalty
            info["exec_error"] = result.error

        if done:
            r += success_bonus
            info["success"] = True

        return r, done, info

    def reset_episode_state():
        nonlocal rl_eval, prev_score
        rl_eval, prev_score = None, 0.0

    reward_fn.reset = reset_episode_state  # type: ignore[attr-defined]
    return reward_fn
