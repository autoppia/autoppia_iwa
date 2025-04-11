import asyncio
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.demo_webs.utils import _load_web_analysis, initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_list_of_evaluations, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# Setup Loguru
LOG_FILE = "benchmark.log"

logger.remove()
logger.add(LOG_FILE, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", colorize=True)


@dataclass
class BenchmarkConfig:
    """Configuration for the benchmark test."""

    use_cached_tasks: bool = False
    use_cached_solutions: bool = False
    evaluate_real_tasks: bool = False

    m: int = 1  # Number of copies of each solution to evaluate
    prompts_per_url: int = 1
    num_of_urls: int = 1
    prompt_per_use_case: int = 1

    # Paths
    base_dir: Path = PROJECT_BASE_DIR.parent
    data_dir: Path = base_dir / "data"
    tasks_cache_dir: Path = data_dir / "tasks_cache"
    solutions_cache_dir: Path = data_dir / "solutions_cache"
    output_dir: Path = base_dir / "results"

    def __post_init__(self):
        for directory in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)


# Initialize configuration & solution cache
config = BenchmarkConfig()
solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))

# Define agents
AGENTS: list[IWebAgent] = [
    # RandomClickerWebAgent(id="2", name="Random-clicker"),
    ApifiedWebAgent(id="1", name="Agent1", host="127.0.0.1", port=7000, timeout=120),
    # ApifiedWebAgent(id="1", name="Agent1", host="127.0.0.1", port=11112, timeout=120),
    # ApifiedWebAgent(id="2", name="Agent2", host="127.0.0.1", port=8005, timeout=120),
    # ApifiedWebAgent(id="3", name="Agent3", host="127.0.0.1",
    #                 port=5000, timeout=120),
]

visualizer = SubnetVisualizer()


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
    """Generate tasks with caching support."""
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


async def generate_solution_for_task(demo_project: WebProject, agent: IWebAgent, task: Task, timing_metrics: TimingMetrics) -> TaskSolution | None:
    """
    Generate (or load from cache) the solution for ONE Task with ONE Agent.
    Returns the corresponding TaskSolution.
    """
    logger.info(f"---\nGenerating solution for Agent: {agent.name} | Task: {task.id}")
    backend_service = BackendDemoWebService(demo_project)

    try:
        # (Optional) Reset DB
        await backend_service.reset_database()

        # Load from cache if available
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
        logger.opt(exception=True).error(f"Error generating solution for Task {task.id}: {e!r}")
        return None
    finally:
        await backend_service.close()


async def run_evaluation(demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
    """
    For each Task:
      - Generate solutions from ALL Agents
      - Pass them to the ConcurrentEvaluator in a single call:
         evaluator.evaluate_task_solutions(task, solutions_for_this_task)

    Then collect results in a structure for final reporting and plotting.
    """
    final_results = {}

    # Evaluate each task (with all agent solutions)
    for task in tasks:
        logger.info(f"\n=== Processing Task {task.id} ===")

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

        if not config.evaluate_real_tasks:
            # Load/Initialize demo projects
            web_projects = await initialize_demo_webs_projects(demo_web_projects)
            # For simplicity, only take the first project (or however many you want)
            web_projects = [web_projects[0]]

            for project in web_projects:
                tasks = await generate_tasks(project)
                if tasks:
                    await run_evaluation(project, tasks, timing_metrics)
        else:
            # Evaluate 'real tasks'
            tasks_data = load_real_tasks(config.num_of_urls)
            web_projects = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}

            for td in tasks_data:
                project = web_projects.get(td.id)
                if project:
                    await _load_web_analysis(project)
                    tasks = await generate_tasks(project, td)
                    if tasks:
                        await run_evaluation(project, tasks, timing_metrics)

        logger.info("Evaluation complete!")
    except Exception as e:
        import sys

        exc_info = sys.exc_info()
        logger.opt(exception=e).error(f"Failed to process task: {e!s}", exc_info=exc_info, stack_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
        logger.opt(exception=e).error(f"Error: {e}", stace_info=True)
