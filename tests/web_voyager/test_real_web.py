import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import JudgeBaseOnHTML, JudgeBaseOnScreenshot
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.utils import _load_web_analysis
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_evaluation, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, generate_hash, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent


@dataclass
class WebVoyagerConfig:
    """Configuration for the benchmark test."""

    use_cached_solutions: bool = False

    num_of_urls: int = 10

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
config = WebVoyagerConfig()
solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))

# Define agents
AGENTS: list[IWebAgent] = [
    # RandomClickerWebAgent(name="Random-clicker"),
    ApifiedWebAgent(name="Browser-Use", host="localhost", port=5000, timeout=150),
    # ApifiedWebAgent(name="Autoppia-Agent", host="localhost", port=9002, timeout=120),
]

# Setup logging
logger.remove()
logger.add("real_web_evaluation.log", rotation="10 MB", level="DEBUG", format="{time} | {level: <8} | {message}", colorize=True)
visualizer = SubnetVisualizer()


@visualize_task(visualizer)
async def generate_tasks(tasks_data: TaskData) -> list[Task]:
    """Generate tasks with caching support."""
    success_criteria = tasks_data.ques
    tests = [JudgeBaseOnScreenshot(success_criteria=success_criteria), JudgeBaseOnHTML(success_criteria=success_criteria)]
    return [Task(url=tasks_data.web, prompt=tasks_data.ques, is_web_real=True, tests=tests)]


@visualize_evaluation(visualizer)
async def evaluate_task_solution(web_project: WebProject, task: Task, task_solution: TaskSolution) -> EvaluationResult:
    """Evaluate a task solution."""
    evaluator = ConcurrentEvaluator(
        web_project=web_project,
        config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20),
    )
    result = await evaluator.evaluate_single_task_solution(task, task_solution)

    if result is not None and result.feedback:
        evaluation_feedback = result.feedback.model_dump()
        evaluation_feedback.pop("execution_history", None)

        log_file = PROJECT_BASE_DIR / "judge_tests_usage_logs.jsonl"

        if not log_file.exists():
            raise FileNotFoundError(f"the log file {log_file} does not exist")

        task_prompt_hash = generate_hash(task.prompt)
        total_iterations = len(result.execution_history)
        updated_entries = []
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_iterations = entry["total_iteration"]
                    if generate_hash(entry.get("task")) == task_prompt_hash and total_iterations == entry_iterations:
                        entry["evaluation_feedback"] = evaluation_feedback
                    updated_entries.append(entry)
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON line in {log_file}")
                    continue

        with log_file.open("w", encoding="utf-8") as f:
            for entry in updated_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return result


async def generate_solutions(agent: IWebAgent, tasks: list[Task], timing_metrics: TimingMetrics) -> dict[str, TaskSolution]:
    """Generate or load solutions for a given agent and tasks."""
    solutions = {}
    logger.info(f"\nAgent: {agent.name}")

    for task in tasks:
        task_solution: TaskSolution | None = None

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
        solutions[task.id] = task_solution

    return solutions


async def evaluate_solutions(
    agent: IWebAgent,
    tasks: list[Task],
    solutions: dict[str, TaskSolution],
    demo_project: WebProject,
) -> dict[str, dict]:
    """Evaluate task solutions."""
    results = {}
    logger.info(f"\nEvaluating solutions for Agent: {agent.name}")

    for task in tasks:
        logger.info(f"  Evaluating solution for Task {task.id}...")
        task_solution = solutions[task.id]
        eval_result = await evaluate_task_solution(demo_project, task, task_solution)
        results[task.id] = {"score": eval_result.final_score, "evaluation_result": eval_result}
    return results


async def run_evaluation(demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
    """Orchestrate solution generation and evaluation."""
    all_solutions = {agent.id: await generate_solutions(agent, tasks, timing_metrics) for agent in AGENTS}
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

    tasks_data = load_real_tasks(config.num_of_urls)
    web_projects = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}

    for td in tasks_data:
        project = web_projects.get(td.id)
        if project:
            await _load_web_analysis(project)
            tasks = await generate_tasks(td)
            if tasks:
                await run_evaluation(project, tasks, timing_metrics)

    logger.info("Evaluation complete!")


if __name__ == "__main__":
    asyncio.run(main())
