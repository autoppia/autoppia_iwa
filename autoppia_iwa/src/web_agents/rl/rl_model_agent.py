from __future__ import annotations

from dataclasses import dataclass
import asyncio
from pathlib import Path
from typing import Optional

from loguru import logger

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.rl.envs.iwa_env import IWAWebEnv
from autoppia_iwa.src.rl.utils.solutions import history_to_task_solution
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


@dataclass(slots=True)
class RLModelAgentConfig:
    model_path: str = "/data/rl_models/ppo_real.zip"
    topk: int = 12
    max_steps: int = 30
    deterministic: bool = True
    random_fallback: bool = True  # if model not found or libs missing, use random/NOOP


class RLModelAgent(IWebAgent):
    """IWebAgent wrapper around a trained SB3 MaskablePPO policy over IWAWebEnv.

    solve_task() runs an on-policy rollout inside the env to produce actions
    and adapts the execution history into a TaskSolution for the evaluator.
    """

    def __init__(self, id: Optional[str] = None, name: Optional[str] = None, config: Optional[RLModelAgentConfig] = None):
        self.id = id or "rl-model"
        self.name = name or "RLModelAgent"
        self.config = config or RLModelAgentConfig()

    async def solve_task(self, task: Task) -> TaskSolution:
        """Run the rollout in a background thread to avoid nested asyncio issues.

        The IWAWebEnv uses async browser calls under the hood and bridges them
        via a sync helper. Executing in a separate thread ensures it can create
        and control its own event loop without clashing with the benchmark's
        running loop.
        """
        try:
            return await asyncio.to_thread(self._rollout_sync, task)
        except Exception as e:
            logger.error(f"[{self.name}] Rollout failed: {e}", exc_info=True)
            # Guarantee a well-formed empty solution on failure
            return TaskSolution(task_id=task.id, actions=[], web_agent_id=self.id)

    def _rollout_sync(self, task: Task) -> TaskSolution:
        cfg = {
            "topk": int(self.config.topk),
            "max_steps": int(self.config.max_steps),
            "goal_vocab_size": 4096,
            "dom_vocab_size": 8192,
            "url_vocab_size": 1024,
            "max_goal_tokens": 48,
            "max_dom_tokens": 200,
            "max_element_tokens": 12,
            "action_history": 10,
        }
        env = IWAWebEnv(cfg)

        # Try to import sb3-contrib and load the trained model
        model = None
        env_wrapped = env
        try:
            from sb3_contrib import MaskablePPO  # type: ignore
            from sb3_contrib.common.wrappers import ActionMasker  # type: ignore

            def mask_fn(e):
                return e.get_action_mask()

            env_wrapped = ActionMasker(env, mask_fn)
            model_path = Path(self.config.model_path)
            if model_path.exists():
                model = MaskablePPO.load(str(model_path), env=env_wrapped, print_system_info=False)
                logger.info(f"[{self.name}] Loaded RL model from {model_path}")
            else:
                logger.warning(f"[{self.name}] Model path not found: {model_path}. Using fallback policy.")
        except Exception as e:
            logger.warning(f"[{self.name}] SB3 not available or failed to load model: {e}. Using fallback policy.")
            model = None

        # Rollout
        import numpy as _np

        try:
            obs, _ = env_wrapped.reset(options={"task": task})  # type: ignore[arg-type]
            done = False
            trunc = False
            rng = _np.random.default_rng(0)

            while not (done or trunc):
                if model is not None:
                    action, _state = model.predict(obs, deterministic=self.config.deterministic)
                else:
                    # Fallback: random valid action if available
                    mask = env.get_action_mask()
                    valid = _np.where(mask)[0]
                    action = int(rng.choice(valid)) if valid.size else 0

                obs, _rew, done, trunc, _info = env_wrapped.step(int(action))

            history = env.get_execution_history()
            solution = history_to_task_solution(task, history, web_agent_id=self.id)
            return solution
        finally:
            try:
                env.close()
            except Exception:
                pass


__all__ = ["RLModelAgent", "RLModelAgentConfig"]
