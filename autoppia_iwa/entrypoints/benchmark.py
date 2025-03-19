import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.demo_webs.utils import _load_web_analysis, initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("benchmark.log")],
)
logger = logging.getLogger("benchmark")


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
AGENTS: List[BaseAgent] = [
    ApifiedWebAgent(id='1', name="Trick Agent1", host="127.0.0.1", port=8005, timeout=120),
    ApifiedWebAgent(id='2', name="Trick Agent2", host="127.0.0.1", port=5000, timeout=120),
    ApifiedWebAgent(id='3', name="Trick Agent3", host="127.0.0.1", port=5000, timeout=120),
]

visualizer = SubnetVisualizer()


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: Optional[TaskData] = None) -> List[Task]:
    """Generate tasks, using cache if enabled."""
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


async def generate_solution_for_task(demo_project: WebProject, agent: BaseAgent, task: Task, timing_metrics: TimingMetrics) -> TaskSolution:
    """
    Generate (or load from cache) the solution for ONE Task with ONE Agent.
    Returns the corresponding TaskSolution.
    """
    logger.info(f"---\nGenerating solution for Agent: {agent.name} | Task: {task.id}")
    backend_service = BackendDemoWebService(demo_project)
    task_solution: Optional[TaskSolution] = None

    try:
        # (Optional) Reset DB
        await backend_service.reset_database()

        # 1) Check if solution is cached
        if config.use_cached_solutions and solution_cache.solution_exists(task.id, agent.id):
            logger.info(f"  * Loading cached solution for Task {task.id}...")
            try:
                task_solution = await solution_cache.load_solution(task.id, agent.id)
                if task_solution and task_solution.actions:
                    logger.info(f"    Loaded cached solution ({len(task_solution.actions)} actions).")
                else:
                    logger.warning(f"    No solution found for {task.id} in cache, generating a new one.")
                    task_solution = None
            except Exception as e:
                logger.error(f"    Error loading solution from cache: {str(e)}")
                task_solution = None

        # 2) If not found in cache, generate a new solution
        if task_solution is None:
            logger.info(f"  * Generating new solution for Task {task.id}...")
            start_time = time.time()

            # Prepare the task for the agent (if needed)
            prepared_task = task.prepare_for_agent(agent.id)
            # Solve the task
            solution = await agent.solve_task(prepared_task)
            actions = solution.actions or []
            task_solution = TaskSolution(task_id=task.id, actions=actions, web_agent_id=agent.id)

            # Record solution time
            end_time = time.time()
            solution_time = end_time - start_time
            timing_metrics.record_solution_time(agent.id, task.id, solution_time)
            logger.info(f"    Solution generated in {solution_time:.2f} s with {len(actions)} actions.")

            # 3) Cache the new solution
            try:
                success = solution_cache.save_solution(task_solution=task_solution, agent_id=agent.id, agent_name=agent.name)
                if success:
                    logger.info("    Successfully cached the solution.")
                else:
                    logger.warning("    Failed to cache the solution.")
            except Exception as e:
                logger.error(f"Error caching the solution: {str(e)}")

    finally:
        # Close backend service
        await backend_service.close()

    return task_solution


async def run_evaluation(demo_project: WebProject, tasks: List[Task], timing_metrics: TimingMetrics):
    """
    Orchestrate the solution generation for each (Task, Agent) pair,
    then evaluate ALL tasks at once via the ConcurrentEvaluator's
    `evaluate_all_tasks_solutions(...)` method.
    """
    from collections import defaultdict

    # Dictionary mapping: task_id -> list of TaskSolution (one solution per Agent)
    solutions_by_task: Dict[str, List[TaskSolution]] = defaultdict(list)
    task_solutions = []
    evaluator = ConcurrentEvaluator(
        web_project=demo_project,
        config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20),
    )
    # 1) Generate solutions for each Task and Agent
    for task in tasks:
        for agent in AGENTS:
            task_solution = await generate_solution_for_task(demo_project, agent, task, timing_metrics)
            solutions_by_task[task.id].append(task_solution)
            task_solutions.append(task_solution)
        evaluation_results = await evaluator.evaluate_task_solutions(task, task_solutions)
        print(evaluation_results)
    final_results: Dict[str, Dict[str, Dict]] = {}

    # for task_id, eval_results in evaluation_results.items():
    #     for eval_result in eval_results:
    #         agent_id = eval_result.web_agent_id
    #         if agent_id not in final_results:
    #             final_results[agent_id] = {}
    #         final_results[agent_id][task_id] = {
    #             "score": eval_result.final_score,
    #             "evaluation_result": eval_result
    #         }

    # 4) Print and plot results
    print_performance_statistics(final_results, AGENTS, timing_metrics)
    plot_results(final_results, AGENTS, timing_metrics, str(config.output_dir))
    plot_task_comparison(final_results, AGENTS, tasks, str(config.output_dir))
    save_results_to_json(final_results, AGENTS, timing_metrics, str(config.output_dir))


async def main():
    """Main function to run multi-task agent evaluation."""
    logger.info("Starting evaluation...")
    AppBootstrap()

    timing_metrics = TimingMetrics()
    timing_metrics.start()

    if not config.evaluate_real_tasks:
        # Load/Initialize demo projects
        web_projects = await initialize_demo_webs_projects(demo_web_projects)
        # For simplicity, only take the first one (or any subset you need)
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


if __name__ == "__main__":
    asyncio.run(main())
