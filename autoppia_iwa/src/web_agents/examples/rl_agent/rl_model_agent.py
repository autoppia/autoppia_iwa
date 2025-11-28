"""
RL Agent Example - Interface Template

This is a REFERENCE IMPLEMENTATION showing how to build an RL-based web agent.
The actual RL training code has been moved to a separate repository.

For full implementation, see: autoppia-rl-agent repository
"""

from __future__ import annotations

from dataclasses import dataclass

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution


@dataclass(slots=True)
class RLModelAgentConfig:
    """Configuration for RL agent (example)."""

    model_path: str = "/data/rl/models/ppo_real.zip"
    topk: int = 12
    max_steps: int = 30
    deterministic: bool = True
    random_fallback: bool = True


class RLModelAgent(IWebAgent):
    """
    Example RL agent interface.

    This is a STUB implementation. The actual RL agent with training code
    is in a separate repository.

    To implement your own RL agent:
    1. Create Gymnasium environment (IWAWebEnv)
    2. Train with PPO/BC algorithms
    3. Load trained model
    4. Implement solve_task() to run policy

    Full implementation: See autoppia-rl-agent repository
    """

    def __init__(self, id: str, name: str, config: RLModelAgentConfig):
        self.id = id
        self.name = name
        self.config = config

    async def solve_task(self, task: Task) -> TaskSolution:
        """
        Solve task using trained RL policy.

        NOTE: This is a stub. Full implementation in separate repo.
        """
        raise NotImplementedError(
            "RL agent implementation moved to separate repository.\n"
            "This is just an interface example.\n\n"
            "To use RL agents:\n"
            "1. See: autoppia-rl-agent repository\n"
            "2. Or implement your own using this interface\n"
            "3. Or use ApifiedWebAgent to call your trained model via HTTP"
        )


# ============================================================================
# REFERENCE IMPLEMENTATION (Commented)
# ============================================================================
#
# Below is the original implementation showing how it worked.
# This is kept as REFERENCE for developers building RL agents.
#
# """
# from autoppia_iwa.src.rl.agent.envs.iwa_env import IWAWebEnv
# from autoppia_iwa.src.rl.agent.utils.solutions import history_to_task_solution
#
# class RLModelAgent(IWebAgent):
#     def __init__(self, id: str, name: str, config: RLModelAgentConfig):
#         self.id = id
#         self.name = name
#         self.config = config
#         self._model = None
#         self._env = None
#
#     async def solve_task(self, task: Task) -> TaskSolution:
#         # 1. Create Gymnasium environment
#         self._env = IWAWebEnv(cfg={
#             "topk": self.config.topk,
#             "max_steps": self.config.max_steps,
#             "project_start_index": 0,
#         })
#
#         # 2. Load trained PPO model
#         from sb3_contrib import MaskablePPO
#         self._model = MaskablePPO.load(self.config.model_path)
#
#         # 3. Run episode with trained policy
#         obs, info = await self._env.reset()
#         history = []
#
#         for step in range(self.config.max_steps):
#             # Get action from policy
#             mask = info.get("action_mask")
#             action, _states = self._model.predict(
#                 obs,
#                 action_masks=mask,
#                 deterministic=self.config.deterministic
#             )
#
#             # Execute action in environment
#             obs, reward, done, truncated, info = await self._env.step(action)
#             history.append({"action": action, "obs": obs, "reward": reward})
#
#             if done or truncated:
#                 break
#
#         # 4. Convert environment history to TaskSolution
#         solution = history_to_task_solution(history, task_id=task.id, web_agent_id=self.id)
#
#         return solution
# """
