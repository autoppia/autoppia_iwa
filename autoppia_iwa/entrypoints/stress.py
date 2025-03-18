import asyncio
import logging
import os
import time

# Autoppia/third-party imports
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json

# Import the consolidated solution cache system
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache

# Local imports (within the same "entrypoints" directory)
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(), logging.FileHandler("stress_test.log")])
logger = logging.getLogger("stress_test")

# -----------------------------------------------------------------------------
# Configuration for the stress test
# -----------------------------------------------------------------------------
USE_CACHED_TASKS = False  # Set to True to use cached tasks from JSON file
USE_CACHED_SOLUTIONS = False  # Set to True to use cached solutions when available
TASKS_CACHE_DIR = "data/tasks_cache"  # Directory to store task cache files
SOLUTIONS_CACHE_DIR = "data/solutions_cache"  # Directory to store solution cache files
OUTPUT_DIR = "results"  # Directory to store test results
M = 1  # Number of copies of each solution to evaluate
PROMPTS_PER_URL = 2
NUM_OF_URLS = 2

# Create output/cache directories if needed
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TASKS_CACHE_DIR, exist_ok=True)
os.makedirs(SOLUTIONS_CACHE_DIR, exist_ok=True)

# Initialize the solution cache manager (single file for all solutions)
solution_cache = ConsolidatedSolutionCache(SOLUTIONS_CACHE_DIR)

# -----------------------------------------------------------------------------
# Define the agents for the stress test
# -----------------------------------------------------------------------------
AGENTS: list[BaseAgent] = [RandomClickerWebAgent(name="Random-clicker"), ApifiedWebAgent(name="browser-use", host="localhost", port=9000)]

# Identifier for the browser-use agent
BROWSER_USE_AGENT_ID = "ApifiedWebAgent-browser-use"


async def main():
    """Main function to run the multi-task agent evaluation (stress test)."""
    logger.info("Starting comprehensive multi-task agent evaluation with batch processing...")

    # Initialize the application
    AppBootstrap()

    # Initialize timing metrics
    timing_metrics = TimingMetrics()
    timing_metrics.start()

    # Container to store results: { agent_id: { task_id: {"score": ...} } }
    results = {}

    # Load or create demo web projects
    demo_web_projects = await initialize_demo_webs_projects()
    if not demo_web_projects:
        logger.error("No demo web projects available.")
        return

    # Use the first project for demonstration
    demo_project = demo_web_projects[0]
    logger.info(f"Using project: {demo_project.name}")

    # Generate or load tasks for the project
    tasks = await generate_tasks_for_project(demo_project, use_cached_tasks=USE_CACHED_TASKS, task_cache_dir=TASKS_CACHE_DIR, prompts_per_url=PROMPTS_PER_URL, num_of_urls=NUM_OF_URLS)

    if not tasks:
        logger.error("No tasks available.")
        return

    logger.info(f"Evaluating {len(tasks)} tasks with {len(AGENTS)} agents, {M} solution copies each...")

    # Phase 1: Generate solutions (once per agent per task)
    all_solutions = {}  # {agent_id: {task_id: TaskSolution}}
    logger.info("\n--- Phase 1: Generating Solutions ---")

    for agent in AGENTS:
        all_solutions[agent.id] = {}
        logger.info(f"\nAgent: {agent.name}")

        for task in tasks:
            task_solution: TaskSolution | None = None

            # Check if solution should be loaded from cache
            if USE_CACHED_SOLUTIONS and solution_cache.solution_exists(task.id, agent.id):
                logger.info(f"  Loading cached solution for Task {task.id}...")
                try:
                    # Load cached solution - now returns TaskSolution directly
                    task_solution = await solution_cache.load_solution(task.id, agent.id)
                    if task_solution:
                        logger.info(f"    Successfully loaded cached solution with {len(task_solution.actions)} actions")
                    else:
                        logger.warning(f"    Failed to load cached solution for {task.id}, will generate new one")
                except Exception as e:
                    logger.error(f"    Error loading cached solution: {e!s}")

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
                    logger.error(f"Error caching solution: {e!s}")

            # Store solution for evaluation phase
            all_solutions[agent.id][task.id] = task_solution

    # Phase 2: Evaluate M copies of each solution
    logger.info("\n--- Phase 2: Evaluating Solutions in Batches ---")

    for agent in AGENTS:
        results[agent.id] = {}

    for agent in AGENTS:
        logger.info(f"\nEvaluating solutions for Agent: {agent.name}")

        for task in tasks:
            logger.info(f"  Evaluating solution for Task {task.id}...")
            original_solution = all_solutions[agent.id][task.id]

            # Make M copies of that solution
            solution_copies = []
            for _ in range(M):
                copy_solution = TaskSolution(task_id=task.id, actions=original_solution.actions.copy() if original_solution.actions else [], web_agent_id=agent.id)
                solution_copies.append(copy_solution)

            evaluator_config = EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20)
            evaluator = ConcurrentEvaluator(web_project=demo_project, config=evaluator_config)

            start_eval_time = time.time()
            evaluation_results = await evaluator.evaluate_task_solutions(task, solution_copies)
            end_eval_time = time.time()
            eval_time = end_eval_time - start_eval_time
            timing_metrics.record_evaluation_time(agent.id, task.id, eval_time / M)

            # Compute average score
            if evaluation_results:
                avg_score = sum(er.final_score for er in evaluation_results) / len(evaluation_results)
                results[agent.id][task.id] = {"score": avg_score, "num_solutions_evaluated": M, "total_evaluation_time": eval_time, "per_solution_time": eval_time / M}
                logger.info(f"    Batch evaluation in {eval_time:.2f} seconds; Avg score = {avg_score:.2f}")
            else:
                logger.warning(f"    No evaluation results returned for task {task.id}")
                results[agent.id][task.id] = {"score": 0.0, "num_solutions_evaluated": 0, "total_evaluation_time": eval_time, "per_solution_time": 0.0}

    # End timing
    timing_metrics.end()

    # Print summary and generate plots
    print_performance_statistics(results, AGENTS, timing_metrics)
    plot_results(results, AGENTS, timing_metrics, OUTPUT_DIR)
    plot_task_comparison(results, AGENTS, tasks, OUTPUT_DIR)
    save_results_to_json(results, AGENTS, timing_metrics, OUTPUT_DIR)

    logger.info(f"\nEvaluation complete! Results have been saved to {OUTPUT_DIR}.")
    logger.info(f"Agent solutions have been cached to {SOLUTIONS_CACHE_DIR}/solutions.json")


if __name__ == "__main__":
    asyncio.run(main())
