import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import TestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.config import initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.shared.entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_evaluation, visualize_task
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent
from autoppia_iwa.src.web_voyager_test.utils import TaskData, load_jsonl_file


@dataclass
class BenchmarkConfig:
    """Configuration for the benchmark test."""

    use_cached_tasks: bool = False  # Set to True to use cached tasks from JSON file
    use_cached_solutions: bool = False  # Set to True to use cached solutions when available
    evaluate_real_tasks: bool = True

    base_dir: Path = PROJECT_BASE_DIR.parent
    data_dir: Path = base_dir / "data"
    tasks_cache_dir: str = str(data_dir / "tasks_cache")  # Directory to store task cache files
    solutions_cache_dir: str = str(data_dir / "solutions_cache")  # Directory to store solution cache files
    output_dir: str = str(base_dir / "results")  # Directory to store test results

    m: int = 1  # Number of copies of each solution to evaluate
    prompts_per_url: int = 1
    num_of_urls: int = 1

    def __post_init__(self):
        """Post-initialization logic to ensure directories exist."""
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """Ensure that all necessary directories exist."""
        for directory in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir):
            Path(directory).mkdir(parents=True, exist_ok=True)


# Initialize configuration
config = BenchmarkConfig()

# Initialize the solution cache manager (single file for all solutions)
solution_cache = ConsolidatedSolutionCache(config.solutions_cache_dir)

# -----------------------------------------------------------------------------
# Define the agents for the stress test
# -----------------------------------------------------------------------------
AGENTS: List[BaseAgent] = [
    RandomClickerWebAgent(name="Random-clicker"),
    ApifiedWebAgent(name="browser-use", host="localhost", port=9000),
]

# Visualizer
visualizer = SubnetVisualizer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("benchmark.log"),
    ],
)
logger = logging.getLogger("benchmark")


@visualize_task(visualizer)
async def generate_tasks(demo_project) -> List[Task]:
    """Generate or load tasks for evaluation."""
    if config.evaluate_real_tasks:
        logger.info("Loading real tasks...")
        original_tasks = load_jsonl_file(config.data_dir / "WebVoyager_data.jsonl")
        impossible_tasks_ids = load_jsonl_file(config.data_dir / "WebVoyagerImpossibleTasks.json")
        tasks_data = [TaskData(**task) for task in original_tasks if task["id"] not in impossible_tasks_ids]
        tasks = [Task(url=t.web, prompt=t.ques, is_web_real=True) for t in tasks_data][:config.num_of_urls]
        return await TestGenerationPipeline(demo_project).add_tests_to_tasks(tasks)
    return await generate_tasks_for_project(
        demo_project,
        config.use_cached_tasks,
        config.tasks_cache_dir,
        config.prompts_per_url,
        config.num_of_urls,
    )


@visualize_evaluation(visualizer)
async def evaluate_task_solution(web_project, task: Task, task_solution: TaskSolution) -> EvaluationResult:
    """Evaluate a single task solution."""
    evaluator = ConcurrentEvaluator(
        web_project=web_project,
        config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20),
    )
    return await evaluator.evaluate_single_task_solution(task, task_solution)


async def generate_solutions(agent: BaseAgent, tasks: List[Task], timing_metrics: TimingMetrics) -> Dict[str, TaskSolution]:
    """Generate or load solutions for a given agent and tasks."""
    solutions = {}
    logger.info(f"\nAgent: {agent.name}")

    for task in tasks:
        task_solution: Optional[TaskSolution] = None

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

    return solutions


async def evaluate_solutions(agent: BaseAgent, tasks: List[Task], solutions: Dict[str, TaskSolution], demo_project) -> Dict[str, Dict]:
    """Evaluate solutions for a given agent and tasks."""
    results = {}
    logger.info(f"\nEvaluating solutions for Agent: {agent.name}")

    for task in tasks:
        logger.info(f"  Evaluating solution for Task {task.id}...")
        task_solution = solutions[task.id]
        eval_result = await evaluate_task_solution(demo_project, task, task_solution)
        results[task.id] = {"score": eval_result.final_score, "evaluation_result": eval_result}

    return results


async def main():
    """Main function to run the multi-task agent evaluation."""
    logger.info("Starting multi-task agent evaluation...")
    AppBootstrap()

    timing_metrics = TimingMetrics()
    timing_metrics.start()

    # Container to store results: { agent_id: { task_id: {"score": ...} } }
    results: Dict[str, Dict[str, Dict]] = {}

    # Load or create demo web projects
    demo_web_projects = await initialize_demo_webs_projects()
    if not demo_web_projects:
        logger.error("No demo web projects available.")
        return

    # Use the first project for demonstration
    demo_project = demo_web_projects[0]
    logger.info(f"Using project: {demo_project.name}")

    # Generate or load tasks with visualization
    tasks = await generate_tasks(demo_project)
    if not tasks:
        logger.error("No tasks available.")
        return

    logger.info(f"Evaluating {len(tasks)} tasks with {len(AGENTS)} agents, {config.m} solution copies each...")

    # Phase 1: Generate solutions (once per agent per task)
    all_solutions: Dict[str, Dict[str, TaskSolution]] = {}
    logger.info("\n--- Phase 1: Generating Solutions ---")

    for agent in AGENTS:
        all_solutions[agent.id] = await generate_solutions(agent, tasks, timing_metrics)

    # Phase 2: Evaluate M copies of each solution
    logger.info("\n--- Phase 2: Evaluating Solutions in Batches ---")

    for agent in AGENTS:
        results[agent.id] = await evaluate_solutions(agent, tasks, all_solutions[agent.id], demo_project)

    # End timing and summarize results with visualization
    timing_metrics.end()

    # Print summary and generate plots
    print_performance_statistics(results, AGENTS, timing_metrics)
    plot_results(results, AGENTS, timing_metrics, config.output_dir)
    plot_task_comparison(results, AGENTS, tasks, config.output_dir)
    save_results_to_json(results, AGENTS, timing_metrics, config.output_dir)

    logger.info(f"\nEvaluation complete! Results have been saved to {config.output_dir}.")
    logger.info(f"Agent solutions have been cached to {config.solutions_cache_dir}/solutions.json")


if __name__ == "__main__":
    asyncio.run(main())
