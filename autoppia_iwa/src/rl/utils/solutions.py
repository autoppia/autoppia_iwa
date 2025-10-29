from __future__ import annotations

from typing import List

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution


def history_to_task_solution(task: Task, history: List[ActionExecutionResult], web_agent_id: str = "rl-policy") -> TaskSolution:
    """Adapt a rollout history to a TaskSolution compatible with the evaluator/benchmark.

    - Copies the BaseAction sequence from the execution history
    - Sets task_id from the provided Task
    - Attaches the provided web_agent_id and applies placeholder replacements
    """
    actions = [r.action for r in history if getattr(r, "action", None) is not None]
    sol = TaskSolution(task_id=task.id, actions=actions, web_agent_id=web_agent_id)
    sol.replace_web_agent_id()
    return sol

