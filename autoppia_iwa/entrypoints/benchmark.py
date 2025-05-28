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

# ==========================
# ==== CONFIGURACIONES ====
# ==========================

PROJECTS_TO_RUN: list[WebProject] = [demo_web_projects[0], demo_web_projects[1]]

PROMPT_PER_USE_CASE_CONST: int = 1
PLOT_BENCHMARK_RESULTS: bool = False
USE_CACHED_TASKS_CONST: bool = False
USE_CACHED_SOLUTIONS_CONST: bool = False
EVALUATE_REAL_TASKS_CONST: bool = False
LOG_FILE = "benchmark.log"

# Logging
setup_logging(LOG_FILE)

# Benchmark config
config = BenchmarkConfig(
    projects_to_run=PROJECTS_TO_RUN,
    prompt_per_use_case=PROMPT_PER_USE_CASE_CONST,
    use_cached_tasks=USE_CACHED_TASKS_CONST,
    use_cached_solutions=USE_CACHED_SOLUTIONS_CONST,
    evaluate_real_tasks=EVALUATE_REAL_TASKS_CONST,
)

solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))

# Agents
AGENTS: list[IWebAgent] = [
    ApifiedWebAgent(id="1", name="Agent1", host="127.0.0.1", port=7000, timeout=120),
]

visualizer = SubnetVisualizer()


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
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
    try:
        evaluator = ConcurrentEvaluator(web_project=web_project, config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20))
        return await evaluator.evaluate_task_solutions(task, task_solutions)
    except Exception:
        traceback.print_exc()
        return []


async def generate_solution_for_task(demo_project: WebProject, agent: IWebAgent, task: Task, timing_metrics: TimingMetrics) -> TaskSolution | None:
    logger.info(f"---\nGenerating solution for Agent: {agent.name} | Task: {task.id} (Project: {demo_project.name})")
    backend_service = BackendDemoWebService(demo_project)

    try:
        await backend_service.reset_database()

        if config.use_cached_solutions:
            cached_solution = await solution_cache.load_solution(task.id, agent.id)
            if cached_solution and cached_solution.actions:
                logger.info(f"Loaded cached solution ({len(cached_solution.actions)} actions).")
                return cached_solution
            logger.warning(f"No cached solution found for {task.id}, generating a new one.")

        start_time = time.time()
        prepared_task = task.prepare_for_agent(agent.id)
        solution = await agent.solve_task(prepared_task)
        task_solution = TaskSolution(task_id=task.id, actions=solution.actions or [], web_agent_id=agent.id)
        timing_metrics.record_solution_time(agent.id, task.id, time.time() - start_time)

        logger.info(f"Generated solution with {len(task_solution.actions)} actions.")
        if solution_cache.save_solution(task_solution, agent.id, agent.name):
            logger.info("Solution cached successfully.")

        return task_solution
    except Exception as e:
        logger.error(f"Error generating solution for Task {task.id} on project {demo_project.name}: {e!r}")
        return None
    finally:
        await backend_service.close()


async def run_evaluation(demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
    final_results = {}
    for task in tasks:
        logger.info(f"\n=== Processing Task {task.id} for Project {demo_project.name} ===")
        solutions_for_this_task = []
        for agent in AGENTS:
            sol = await generate_solution_for_task(demo_project, agent, task, timing_metrics)
            solutions_for_this_task.append(sol)

        evaluation_results = await evaluate_multiple_solutions(demo_project, task, solutions_for_this_task, "test_visualizer")
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


async def main():
    logger.info("Starting evaluation...")
    try:
        AppBootstrap()
        timing_metrics = TimingMetrics()
        timing_metrics.start()

        if not config.evaluate_real_tasks:
            logger.info("Mode: Evaluating demo web projects.")
            await initialize_demo_webs_projects(demo_web_projects)
            projects_to_run = config.projects_to_run

            logger.info(f"Will run {len(projects_to_run)} project(s): {[p.name for p in projects_to_run]}")

            for project in projects_to_run:
                logger.info(f"===== Starting evaluation for project: {project.name} (ID: {project.id}) =====")
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
                    logger.info(f"===== Starting evaluation for real task project: {project.name} =====")
                    tasks = await generate_tasks(project, td)
                    if tasks:
                        await run_evaluation(project, tasks, timing_metrics)
                    else:
                        logger.warning(f"No tasks generated for real project {project.name}. Skipping.")
                else:
                    logger.warning(f"Could not find a matching project for real task ID: {td.id}")

        logger.info("Evaluation process complete!")
    except Exception as e:
        logger.exception(f"Unexpected error in main execution: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
        logger.critical(f"Critical error in script execution: {e}", exc_info=True)
