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
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_evaluation, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, load_real_tasks
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

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
    RandomClickerWebAgent(id="2", name="Random-clicker"),
    # ApifiedWebAgent(id='1', name="Browser-Use", host="127.0.0.1", port=5000, timeout=120),
    # ApifiedWebAgent(name="Autoppia-Agent", host="localhost", port=9002, timeout=120),
]

visualizer = SubnetVisualizer()


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: Optional[TaskData] = None) -> List[Task]:
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
    )


@visualize_evaluation(visualizer)
async def evaluate_task_solution(web_project: WebProject, task: Task, task_solution: TaskSolution) -> EvaluationResult:
    """Evaluate a task solution."""
    evaluator = ConcurrentEvaluator(
        web_project=web_project,
        config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20),
    )
    return await evaluator.evaluate_single_task_solution(task, task_solution)


async def generate_solutions(demo_project: WebProject, agent: BaseAgent, tasks: List[Task], timing_metrics: TimingMetrics) -> Dict[str, TaskSolution]:
    """Generate or load solutions for a given agent and tasks."""
    solutions = {}
    logger.info(f"\nAgent: {agent.name}")
    backend_service = BackendDemoWebService(demo_project)
    try:
        for task in tasks:
            task_solution: Optional[TaskSolution] = None
            # Restart db
            await backend_service.reset_database()

            # Check if solution should be loaded from cache
            if config.use_cached_solutions and solution_cache.solution_exists(task.id, agent.id):
                logger.info(f"  Loading cached solution for Task {task.id}...")
                try:
                    task_solution = await solution_cache.load_solution(task.id, agent.id)
                    if task_solution:
                        logger.info(f"    Successfully loaded cached solution with {len(task_solution.actions)} actions")
                    else:
                        logger.warning(f"    Failed to load cached solution for {task.id}, will generate new one")
                except Exception as e:
                    logger.error(f"    Error loading cached solution: {str(e)}")

            # Generate new solution if needed
            if task_solution is None:
                logger.info(f"  Generating new solution for Task {task.id}...")
                start_time = time.time()
                # CAPA DE MINER
                task = task.prepare_for_agent(agent.id)
                # Solve the task
                solution = await agent.solve_task(task)
                actions = solution.actions or []
                task_solution = TaskSolution(task_id=task.id, actions=actions, web_agent_id=agent.id)

                # Measure solution time
                end_time = time.time()
                solution_time = end_time - start_time
                timing_metrics.record_solution_time(agent.id, task.id, solution_time)
                logger.info(f"    Solution generated in {solution_time:.2f} seconds with {len(actions)} actions")

                # Cache the solution for future use
                try:
                    success = solution_cache.save_solution(task_solution=task_solution, agent_id=agent.id, agent_name=agent.name)
                    if success:
                        logger.info("Solution cached successfully for future runs")
                    else:
                        logger.warning("Failed to cache solution")
                except Exception as e:
                    logger.error(f"Error caching solution: {str(e)}")

            # Store solution for evaluation phase
            solutions[task.id] = task_solution
    finally:
        if backend_service:
            await backend_service.close()
    return solutions


async def evaluate_solutions(
    agent: BaseAgent,
    tasks: List[Task],
    solutions: Dict[str, TaskSolution],
    demo_project: WebProject,
) -> Dict[str, Dict]:
    """Evaluate task solutions."""
    results = {}
    logger.info(f"\nEvaluating solutions for Agent: {agent.name}")

    for task in tasks:
        logger.info(f"  Evaluating solution for Task {task.id}...")
        task_solution = solutions[task.id]
        eval_result = await evaluate_task_solution(demo_project, task, task_solution)
        results[task.id] = {"score": eval_result.final_score, "evaluation_result": eval_result}
    return results


async def run_evaluation(demo_project: WebProject, tasks: List[Task], timing_metrics: TimingMetrics):
    """Orchestrate solution generation and evaluation."""
    all_solutions = {agent.id: await generate_solutions(demo_project, agent, tasks, timing_metrics) for agent in AGENTS}
    results = {agent.id: await evaluate_solutions(agent, tasks, all_solutions[agent.id], demo_project) for agent in AGENTS}

    print_performance_statistics(results, AGENTS, timing_metrics)
    plot_results(results, AGENTS, timing_metrics, str(config.output_dir))
    plot_task_comparison(results, AGENTS, tasks, str(config.output_dir))
    save_results_to_json(results, AGENTS, timing_metrics, str(config.output_dir))


async def main():
    """Main function to run multi-task agent evaluation."""
    logger.info("Starting evaluation...")
    AppBootstrap()

    timing_metrics = TimingMetrics()
    timing_metrics.start()
    if not config.evaluate_real_tasks:
        # web_projects = demo_web_projects
        web_projects = await initialize_demo_webs_projects(demo_web_projects)
        web_projects = [web_projects[0]]
        for project in web_projects:
            tasks = await generate_tasks(project)
            if tasks:
                await run_evaluation(project, tasks, timing_metrics)
    else:
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
