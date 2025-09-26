from __future__ import annotations

import json
from typing import Any, Protocol

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


class AsyncPolicy(Protocol):
    async def act(self, obs: dict[str, Any]) -> dict[str, Any] | str:
        """Devuelve una acción (dict/JSON) compatible con BaseAction.create_action(...)."""


class RLWebAgent(IWebAgent):
    """
    IWebAgent que ejecuta una Task dentro de AsyncWebAgentEnv y devuelve TaskSolution.
    """

    def __init__(
        self,
        id: str,
        name: str,
        env_factory,
        policy: AsyncPolicy,
        max_steps: int = 50,
        stop_on_invalid_action: bool = False,
    ):
        self.id = id
        self.name = name
        self._env_factory = env_factory
        self._policy = policy
        self._max_steps = max_steps
        self._stop_on_invalid_action = stop_on_invalid_action

    async def solve_task(self, task: Task) -> TaskSolution:
        env: AsyncWebAgentEnv = self._env_factory(task)
        actions: list[dict[str, Any]] = []

        obs, info = await env.areset(options={"task": task, "prompt": getattr(task, "prompt", "")})

        for _ in range(self._max_steps):
            act_out = await self._policy.act(obs)
            act_dict = act_out if isinstance(act_out, dict) else json.loads(act_out)
            actions.append(act_dict)

            obs, r, d, t, step_info = await env.astep(act_out)
            if self._stop_on_invalid_action and "action_error" in step_info:
                break
            if d or t:
                break

        return TaskSolution(task_id=task.id, actions=actions, web_agent_id=self.id)
