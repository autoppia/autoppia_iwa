#!/usr/bin/env python
import asyncio
import time
import traceback

from loguru import logger

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.shared.utils_entrypoints.benchmark_utils import BenchmarkConfig, setup_logging
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import (
    plot_results,
    plot_task_comparison,
    print_performance_statistics,
    save_results_to_json,
)
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_list_of_evaluations, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# =========================================================
# CONFIGURATION
# =========================================================

PROJECTS_TO_RUN: list[WebProject] = [
    demo_web_projects[0],
]

PROMPT_PER_USE_CASE_CONST = 1
PLOT_BENCHMARK_RESULTS = False
USE_CACHED_TASKS_CONST = False
USE_CACHED_SOLUTIONS_CONST = False
EVALUATE_REAL_TASKS_CONST = False
LOG_FILE = "benchmark.log"

setup_logging(LOG_FILE)

config = BenchmarkConfig(
    projects_to_run=PROJECTS_TO_RUN,
    prompt_per_use_case=PROMPT_PER_USE_CASE_CONST,
    use_cached_tasks=USE_CACHED_TASKS_CONST,
    use_cached_solutions=USE_CACHED_SOLUTIONS_CONST,
    evaluate_real_tasks=EVALUATE_REAL_TASKS_CONST,
)

solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))

AGENTS: list[IWebAgent] = [
    ApifiedWebAgent(id="1", name="BrowserUseAgent", host="127.0.0.1", port=5000, timeout=120),
    ApifiedWebAgent(id="2", name="BrowserUseAgent", host="127.0.0.1", port=5000, timeout=120),
    ApifiedWebAgent(id="3", name="BrowserUseAgent", host="127.0.0.1", port=5000, timeout=120),
]

# Semaphore to cap concurrent agent calls at 3
SEM = asyncio.Semaphore(3)

visualizer = SubnetVisualizer()

# =========================================================
# TASK AND EVALUATION HELPERS
# =========================================================


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
    """Generate test tasks for a given demo project."""
    if config.evaluate_real_tasks and tasks_data:
        task = Task(url=tasks_data.web, prompt=tasks_data.ques, is_web_real=True)
        return await LocalTestGenerationPipeline(demo_project).add_tests_to_tasks([task])

    return await generate_tasks_for_project(
        demo_project,
        config.use_cached_tasks,
        str(config.tasks_cache_dir),
        prompts_per_use_case=config.prompt_per_use_case,
    )


@visualize_list_of_evaluations(visualizer)
async def evaluate_multiple_solutions(web_project, task, task_solutions, validator_id):
    """Run the evaluator for all solutions of a task."""
    try:
        evaluator = ConcurrentEvaluator(web_project=web_project, config=EvaluatorConfig(enable_grouping_tasks=False, chunk_size=20))
        return await evaluator.evaluate_task_solutions(task, task_solutions)
    except Exception:
        traceback.print_exc()
        return []


async def generate_solution_for_task(
    demo_project: WebProject,
    agent: IWebAgent,
    task: Task,
    timing_metrics: TimingMetrics,
) -> TaskSolution | None:
    """Ask a single agent to solve a single task (concurrency limited by SEM)."""
    async with SEM:  # <-- limits parallelism to 3 agents at a time
        logger.info(f"--- Generating solution | Agent: {agent.name} | Task: {task.id} | Project: {demo_project.name}")
        backend_service = BackendDemoWebService(demo_project)

        try:
            await backend_service.reset_database()

            if config.use_cached_solutions:
                cached_solution = await solution_cache.load_solution(task.id, agent.id)
                if cached_solution and cached_solution.actions:
                    logger.info(f"Loaded cached solution ({len(cached_solution.actions)} actions).")
                    return cached_solution

            start_time = time.time()
            prepared_task = task.prepare_for_agent(agent.id)
            solution = await agent.solve_task(prepared_task)
            solution_action = solution.actions
            processed_task_actions = replace_web_agent_id_in_actions(solution_action, agent.id)
            task_solution = TaskSolution(task_id=task.id, actions=processed_task_actions or [], web_agent_id=agent.id)
            timing_metrics.record_solution_time(agent.id, task.id, time.time() - start_time)

            logger.info(f"Generated solution with {len(task_solution.actions)} actions.")
            if solution_cache.save_solution(task_solution, agent.id, agent.name):
                logger.info("Solution cached successfully.")

            return task_solution
        except Exception as e:
            logger.error(f"Error generating solution for Task {task.id}: {e!r}")
            return None
        finally:
            await backend_service.close()


async def run_evaluation(demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
    """Evaluate every task for a project against all agents, max 3 in parallel."""
    final_results = {}

    for task in tasks:
        logger.info(f"\n=== Processing Task {task.id} for Project {demo_project.name} ===")

        # Build one coroutine per agent and run them concurrently
        coroutines = [generate_solution_for_task(demo_project, agent, task, timing_metrics) for agent in AGENTS]
        solutions_for_this_task = await asyncio.gather(*coroutines, return_exceptions=True)

        # Replace exceptions with None to keep list aligned
        clean_solutions = []
        for sol in solutions_for_this_task:
            if isinstance(sol, Exception):
                logger.error(f"Agent coroutine raised: {sol!r}")
                clean_solutions.append(None)
            else:
                clean_solutions.append(sol)

        evaluation_results = await evaluate_multiple_solutions(demo_project, task, clean_solutions, "test_visualizer")
        for eval_result in evaluation_results:
            final_results.setdefault(eval_result.web_agent_id, {})[task.id] = {
                "score": eval_result.final_score,
                "evaluation_result": eval_result,
            }

    print_performance_statistics(final_results, AGENTS, timing_metrics)
    if PLOT_BENCHMARK_RESULTS:
        plot_results(final_results, AGENTS, timing_metrics, str(config.output_dir))
        plot_task_comparison(final_results, AGENTS, tasks, str(config.output_dir))
        save_results_to_json(final_results, AGENTS, timing_metrics, str(config.output_dir))


def replace_web_agent_id_in_actions(actions: list[BaseAction], web_agent_id: str) -> list[BaseAction]:
    """
    Replaces occurrences of '<web_agent_id>' in the text, url, or value fields of each action
    with the provided web_agent_id.

    Args:
        actions: List of BaseAction instances (e.g., NavigateAction, TypeAction, ClickAction).
        web_agent_id: The integer ID to substitute for the <web_agent_id> placeholder.

    Returns:
        List of updated BaseAction instances.
    """
    for action in actions:
        for field in ["text", "url", "value"]:
            if hasattr(action, field):
                value = getattr(action, field)
                if isinstance(value, str) and "<web_agent_id>" in value:
                    setattr(action, field, value.replace("<web_agent_id>", str(web_agent_id)).replace("your_book_id", str(web_agent_id)))
    return actions


# =========================================================
# MAIN ENTRY
# =========================================================
async def main():
    logger.info("Starting evaluation...")
    try:
        AppBootstrap()
        timing_metrics = TimingMetrics()
        timing_metrics.start()

        if not config.evaluate_real_tasks:
            await initialize_demo_webs_projects(demo_web_projects)
            projects_to_run = config.projects_to_run
            logger.info(f"Will run {len(projects_to_run)} project(s): {[p.name for p in projects_to_run]}")

            for project in projects_to_run:
                logger.info(f"===== Starting evaluation for project: {project.name} ({project.id}) =====")
                tasks = await generate_tasks(project)
                if tasks:
                    await run_evaluation(project, tasks, timing_metrics)
                else:
                    logger.warning(f"No tasks generated for project {project.name}. Skipping.")
        else:
            logger.info("Mode: Evaluating real tasks.")
            tasks_data = load_real_tasks(1)
            real_projects = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}

            for td in tasks_data:
                project = real_projects.get(td.id)
                if project:
                    logger.info(f"===== Starting evaluation for real project: {project.name} =====")
                    tasks = await generate_tasks(project, td)
                    if tasks:
                        await run_evaluation(project, tasks, timing_metrics)
                    else:
                        logger.warning(f"No tasks generated for real project {project.name}. Skipping.")
                else:
                    logger.warning(f"Could not find project for real task ID: {td.id}")

        logger.info("Evaluation process complete!")
    except Exception as e:
        logger.exception(f"Unexpected error in main execution: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
        logger.critical(f"Critical error in script execution: {e}", exc_info=True)
