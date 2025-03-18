from abc import ABC, abstractmethod

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.web_agents.classes import TaskSolution


class IEvaluator(ABC):
    """
    The design allows for multiple web agents to implement this interface, ensuring standardized inputs and behaviors across different agents.
    Every web agent that implements this interface must define the required methods and properties, ensuring consistency and compatibility.

    Example:
    - An 'Autopilot Web Agent' would implement this interface, adhering to the standardized inputs and outputs specified here.

    The goal is to provide a common structure that all web agents will follow, facilitating integration and interoperability among them.
    """

    @abstractmethod
    async def evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Evaluates a single task solution and returns the evaluation result.

        Args:
            task (Task): The task containing the details and tests.
            task_solution (TaskSolution): The task solution containing actions and web_agent_id.

        Returns:
            EvaluationResult: The result of the evaluation.
        """

    @abstractmethod
    async def evaluate_task_solutions(self, task: Task, task_solutions: list[TaskSolution]) -> list[EvaluationResult]:
        """
        Evaluates multiple task solutions for a single task and returns a list of evaluation results.

        Args:
            task (Task): The task containing the details and tests.
            task_solutions (List[TaskSolution]): The list of task solutions to evaluate.

        Returns:
            List[EvaluationResult]: A list of evaluation results.
        """
