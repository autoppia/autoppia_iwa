import asyncio
import logging
from typing import List

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent
from autoppia_iwa.src.web_voyager_test.run_web_voyager import generate_tests, load_valid_web_voyager_tasks
from autoppia_iwa.src.web_voyager_test.utils import TaskData, print_rich_performance_statistics, setup_logging

setup_logging()
app_bootstrap = AppBootstrap()

NUM_OF_TASKS_TO_EVALUATE: int = 1

# Agents
AGENTS: List[IWebAgent] = [
    RandomClickerWebAgent(name="Random-Clicker"),
    ApifiedWebAgent(name="Browser-Use-Agent", host="localhost", port=8080, timeout=120),
]


async def evaluate_project_for_agent(agent: IWebAgent, tasks: List["TaskData"], results):
    """
    Evaluate all tasks for a given demo project and agent.

    For each task, the agent will attempt to solve it and the evaluation score
    will be stored both in the agent's global scores and in the project-specific scores.
    """
    for task in tasks:
        tests = await generate_tests(task.web, task.ques)
        current_task = Task(prompt=task.ques, tests=tests, url=task.web, is_web_real=True)

        # Agent solves the task.
        task_solution: TaskSolution = await agent.solve_task(current_task)
        actions: List[BaseAction] = task_solution.actions

        # Prepare evaluator input and configuration.
        evaluator_input = TaskSolution(task=current_task, actions=actions, web_agent_id=agent.id)
        evaluator_config = EvaluatorConfig(save_results_in_db=False)
        evaluator = ConcurrentEvaluator(evaluator_config)

        # Evaluate the task solution.
        evaluation_result: EvaluationResult = await evaluator.evaluate_single_task(evaluator_input)
        score = evaluation_result.final_score

        # Record the score in both global and project-specific results.
        results[agent.id]["global_scores"].append(score)
        results[agent.id]["projects"].setdefault(task.web_name, []).append(score)


async def main():
    from autoppia_iwa.src.benchmark import plot_agent_results

    # ---------------------------
    # 1. Initialize Agents and Results Storage.
    # ---------------------------
    agents: List[IWebAgent] = AGENTS
    results = {agent.id: {"global_scores": [], "projects": {}} for agent in agents}

    # ---------------------------
    # 2. Process Each Demo Web Project.
    # ---------------------------
    all_tasks = load_valid_web_voyager_tasks()
    # tasks = get_random_tasks(all_tasks, NUM_OF_TASKS_TO_EVALUATE)
    tasks = all_tasks[:NUM_OF_TASKS_TO_EVALUATE]

    for agent in agents:
        await evaluate_project_for_agent(agent, tasks, results)

    # ---------------------------
    # 3. Print Performance Statistics.
    # ---------------------------
    print_rich_performance_statistics(results, agents)

    # ---------------------------
    # 4. Plot the Agent Results.
    # ---------------------------
    plot_agent_results(results, agents)


if __name__ == "__main__":
    try:
        asyncio.run(main())
        logging.info("Shutting down...")
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
