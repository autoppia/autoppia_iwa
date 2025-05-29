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
from autoppia_iwa.src.demo_webs.utils import _load_web_analysis, initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.benchmark_utils import BenchmarkConfig, setup_logging
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_list_of_evaluations, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# ==================================
# ==== BENCHMARK CONFIGURATIONS ====
# ==================================
# Parameter: PROJECT_SELECTOR
# "all"                 -> run all available projects
# "N"                   -> run project number N (1-based index)
# "N,M,P"               -> run projects N, M, and P (1-based indices)
# "" (empty string)     -> run no projects
PROJECT_SELECTOR: str = "4"  # Default or example: "1", "1,3", ""

# Script-level constants for configuring BenchmarkConfig instance
PROMPT_PER_USE_CASE_CONST: int = 1

PLOT_BENCHMARK_RESULTS: bool = False

USE_CACHED_TASKS_CONST: bool = False
USE_CACHED_SOLUTIONS_CONST: bool = False

EVALUATE_REAL_TASKS_CONST: bool = False  # If true, demo project selection is bypassed

NUM_URLS_CONST: int = 1
PROMPTS_PER_URL_CONST: int = 1
# M_COPIES_CONST: int = 1 # If you want to configure 'm' from here

LOG_FILE = "benchmark.log"

# Initialize logging first
setup_logging(LOG_FILE)

# Instantiate BenchmarkConfig with constants from this script
config = BenchmarkConfig(
    PROJECT_SELECTOR=PROJECT_SELECTOR,
    prompt_per_use_case=PROMPT_PER_USE_CASE_CONST,
    use_cached_tasks=USE_CACHED_TASKS_CONST,
    use_cached_solutions=USE_CACHED_SOLUTIONS_CONST,
    evaluate_real_tasks=EVALUATE_REAL_TASKS_CONST,
    num_of_urls=NUM_URLS_CONST,
    prompts_per_url=PROMPTS_PER_URL_CONST,
    # m=M_COPIES_CONST # if you want to control 'm' from here, defaults to 1 in BenchmarkConfig
)

solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))

# Define agents
AGENTS: list[IWebAgent] = [
    # RandomClickerWebAgent(id="2", name="Random-clicker"),
    # ApifiedWebAgent(id="1", name="Agent1", host="127.0.0.1", port=7000, timeout=120),
    # ApifiedWebAgent(id="1", name="Agent1", host="127.0.0.1", port=11112, timeout=120),
    # ApifiedWebAgent(id="2", name="Agent2", host="127.0.0.1", port=8005, timeout=120),
    ApifiedWebAgent(id="1", name="Agent1", host="127.0.0.1", port=5000, timeout=120),
]

visualizer = SubnetVisualizer()


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
    """Generate tasks with caching support. Uses global 'config'."""
    if config.evaluate_real_tasks and tasks_data:
        task = Task(url=tasks_data.web, prompt=tasks_data.ques, is_web_real=True)
        return await LocalTestGenerationPipeline(demo_project).add_tests_to_tasks([task])

    return await generate_tasks_for_project(
        demo_project,
        config.use_cached_tasks,
        str(config.tasks_cache_dir),
        config.prompts_per_url,
        config.num_of_urls,
        config.prompt_per_use_case,
    )


@visualize_list_of_evaluations(visualizer)
async def evaluate_multiple_solutions(web_project, task, task_solutions, validator_id):
    try:
        evaluator = ConcurrentEvaluator(web_project=web_project, config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20))

        evaluation_results = await evaluator.evaluate_task_solutions(task, task_solutions)

        return evaluation_results
    except Exception:
        traceback.print_exc()
        return []


async def generate_solution_for_task(demo_project: WebProject, agent: IWebAgent, task: Task, timing_metrics: TimingMetrics) -> TaskSolution | None:
    """
    Generate (or load from cache) the solution for ONE Task with ONE Agent.
    Returns the corresponding TaskSolution. Uses global 'config'.
    """
    logger.info(f"---\nGenerating solution for Agent: {agent.name} | Task: {task.id} (Project: {demo_project.name})")
    backend_service = BackendDemoWebService(demo_project)

    try:
        await backend_service.reset_database()  # (Optional) Reset DB

        # Try loading from cache
        if config.use_cached_solutions:
            cached_solution = await solution_cache.load_solution(task.id, agent.id)
            if cached_solution and cached_solution.actions:
                logger.info(f"Loaded cached solution ({len(cached_solution.actions)} actions).")
                return cached_solution
            logger.warning(f"No cached solution found for {task.id}, generating a new one.")

        # Generate a new solution
        start_time = time.time()
        prepared_task = task.prepare_for_agent(agent.id)
        solution = await agent.solve_task(prepared_task)
        task_solution = TaskSolution(task_id=task.id, actions=solution.actions or [], web_agent_id=agent.id)
        timing_metrics.record_solution_time(agent.id, task.id, time.time() - start_time)
        logger.info(f"Generated solution with {len(task_solution.actions)} actions.")

        # Cache the solution
        if solution_cache.save_solution(task_solution, agent.id, agent.name):
            logger.info("Solution cached successfully.")

        return task_solution

    except Exception as e:
        logger.error(f"Error generating solution for Task {task.id} on project {demo_project.name}: {e!r}")
        return None
    finally:
        await backend_service.close()


async def run_evaluation(demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
    """
    For each Task:
      - Generate solutions from ALL Agents
      - Pass them to the ConcurrentEvaluator
    Then collect results for reporting.
    """
    final_results = {}
    for task in tasks:
        logger.info(f"\n=== Processing Task {task.id} for Project {demo_project.name} ===")
        # 1) Generate solutions for this Task from ALL agents
        solutions_for_this_task: list[TaskSolution] = []
        for agent in AGENTS:
            sol = await generate_solution_for_task(demo_project, agent, task, timing_metrics)
            solutions_for_this_task.append(sol)

        # 2) Evaluate these solutions in a single call
        logger.info(f"Evaluating {len(solutions_for_this_task)} solutions for Task {task.id}...")
        evaluation_results: list[EvaluationResult] = await evaluate_multiple_solutions(demo_project, task, solutions_for_this_task, "test_visualizer")

        # 3) Store the results in a dict for final stats/plots
        for eval_result in evaluation_results:
            agent_id = eval_result.web_agent_id
            if agent_id not in final_results:
                final_results[agent_id] = {}
            final_results[agent_id][task.id] = {"score": eval_result.final_score, "evaluation_result": eval_result}

    # 4) Print and plot results
    print_performance_statistics(final_results, AGENTS, timing_metrics)
    if PLOT_BENCHMARK_RESULTS:
        plot_results(final_results, AGENTS, timing_metrics, str(config.output_dir))
        plot_task_comparison(final_results, AGENTS, tasks, str(config.output_dir))
        save_results_to_json(final_results, AGENTS, timing_metrics, str(config.output_dir))


async def main():
    """Main function to run multi-task agent evaluation."""
    logger.info("Starting evaluation...")
    try:
        AppBootstrap()

        timing_metrics = TimingMetrics()
        timing_metrics.start()

        if not config.evaluate_real_tasks:  # Global config
            logger.info("Mode: Evaluating demo web projects.")
            all_available_demo_projects = await initialize_demo_webs_projects(demo_web_projects)

            if not isinstance(all_available_demo_projects, list):
                logger.error(f"initialize_demo_webs_projects did not return a list. Got: {type(all_available_demo_projects)}. Cannot proceed with project selection.")
                return

            # Get the specific list of projects to run based on PROJECT_SELECTOR
            projects_to_run: list[WebProject] = config.get_projects_to_run(all_available_demo_projects)

            logger.info("--- Effective Project Selection ---")
            logger.info(f"Project Selector: '{config.PROJECT_SELECTOR}'")
            logger.info(f"Total demo projects loaded: {len(all_available_demo_projects)}")
            if not projects_to_run:
                logger.warning("No projects selected to run based on the current PROJECT_SELECTOR.")
                if config.PROJECT_SELECTOR and all_available_demo_projects:  # If selector was specific but yielded nothing
                    logger.info(f"Details of available projects:\n{BenchmarkConfig.get_available_project_details_static(all_available_demo_projects)}")
            else:
                logger.info(f"Will run {len(projects_to_run)} project(s): {[p.name for p in projects_to_run]}")
            logger.info("---------------------------------")

            for project in projects_to_run:
                logger.info(f"===== Starting evaluation for project: {project.name} (ID: {project.id}) =====")
                tasks = await generate_tasks(project)
                if tasks:
                    await run_evaluation(project, tasks, timing_metrics)
                else:
                    logger.warning(f"No tasks generated for project {project.name}. Skipping evaluation run for this project.")
        else:
            logger.info("Mode: Evaluating real tasks.")
            tasks_data = load_real_tasks(config.num_of_urls)  # Uses num_of_urls from global config

            web_projects_real_map = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}
            logger.info(f"Loaded {len(tasks_data)} real task definitions.")

            for td in tasks_data:
                project = web_projects_real_map.get(td.id)
                if project:
                    logger.info(f"===== Starting evaluation for real task based project: {project.name} (URL: {project.frontend_url}) =====")
                    await _load_web_analysis(project)
                    tasks = await generate_tasks(project, td)
                    if tasks:
                        await run_evaluation(project, tasks, timing_metrics)
                    else:
                        logger.warning(f"No tasks generated for real task project {project.name}. Skipping.")
                else:
                    logger.warning(f"Could not find or create a project for real task data ID: {td.id}")

        logger.info("Evaluation process complete!")
    except ValueError as ve:
        logger.error(f"Configuration or Project Selection Error: {ve}")
    except Exception as e:
        import sys

        exc_info = sys.exc_info()
        logger.opt(exception=True).error(f"An unexpected error occurred in main execution: {e!s}", exc_info=exc_info)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
        logger.critical(f"Critical error in script execution: {e}", exc_info=True)
