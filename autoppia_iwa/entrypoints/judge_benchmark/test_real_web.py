import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.entrypoints.benchmark.utils.results import (
    plot_results,
    print_performance_statistics,
    save_results_to_json,
)
from autoppia_iwa.entrypoints.benchmark.utils.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.tasks import Task
from autoppia_iwa.src.data_generation.tests import JudgeBaseOnHTML, JudgeBaseOnScreenshot
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, generate_hash, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution


@dataclass
class WebVoyagerConfig:
    """Configuration for the benchmark test."""

    url: str | None = None
    prompt: str | None = None
    num_of_urls: int = 1
    agents: list[IWebAgent] = field(default_factory=list)
    task_indices: list[int] = field(default_factory=list)  # e.g., [0, 2, 5] to select specific tasks by index and override num_of_urls
    should_record_gif: bool = True
    use_cached_solutions: bool = False

    base_dir: Path = PROJECT_BASE_DIR.parent
    data_dir: Path = base_dir / "data"
    tasks_cache_dir: Path = data_dir / "tasks_cache"
    solutions_cache_dir: Path = data_dir / "solutions_cache"
    output_dir: Path = base_dir / "results"

    def __post_init__(self):
        for directory in (self.tasks_cache_dir, self.solutions_cache_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)


# Define agents
AGENTS: list[IWebAgent] = [
    # RandomClickerWebAgent(name="Random-clicker"),
    ApifiedWebAgent(name="Browser-Use", host="localhost", port=5000, timeout=250),
    # ApifiedWebAgent(name="OpenAI-CUA", host="localhost", port=5000, timeout=400),
    # ApifiedWebAgent(name="Autoppia-Agent", host="localhost", port=9002, timeout=120),
]

visualizer = SubnetVisualizer()


class WebVoyagerBenchmark:
    """Encapsulates the full benchmarking process for WebVoyager agents."""

    def __init__(self, config: WebVoyagerConfig):
        self.config = config
        self.solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))
        self._visualizer = visualizer
        self.agents: list[IWebAgent] = config.agents

        # Configure logging
        logger.remove()
        logger.add(
            str(PROJECT_BASE_DIR / "real_web_evaluation.log"),
            rotation="10 MB",
            level="DEBUG",
            format="{time} | {level: <8} | {message}",
            colorize=True,
        )

    # ------------------------------------------------------------------------
    # TASK GENERATION
    # ------------------------------------------------------------------------
    @visualize_task(visualizer)
    async def generate_tasks(self, tasks_data: TaskData) -> list[Task]:
        """Generate tasks with caching support."""
        success_criteria = tasks_data.ques
        tests = [
            JudgeBaseOnScreenshot(success_criteria=success_criteria),
            JudgeBaseOnHTML(success_criteria=success_criteria),
        ]
        return [Task(url=tasks_data.web, prompt=tasks_data.ques, is_web_real=True, tests=tests)]

    # ------------------------------------------------------------------------
    # EVALUATION
    # ------------------------------------------------------------------------
    async def evaluate_task_solution(self, web_project: WebProject, task: Task, task_solution: TaskSolution, validator_id: str) -> EvaluationResult:
        """Evaluate a task solution."""
        evaluator = ConcurrentEvaluator(
            web_project=web_project,
            config=EvaluatorConfig(
                # save_results_in_db=False,
                enable_grouping_tasks=False,
                chunk_size=20,
                should_record_gif=self.config.should_record_gif,
            ),
        )
        result = await evaluator.evaluate_single_task_solution(task, task_solution)

        # Apply visualization if we have valid results and visualization is enabled
        if result and task_solution:
            try:
                visualizer.show_list_of_evaluations(task, [task_solution], [result], validator_id)
            except Exception as e:
                logger.warning(f"Visualization failed: {e}")

        if result and result.feedback:
            await self._update_judge_feedback_log(task, result)
        return result

    async def _update_judge_feedback_log(self, task: Task, result: EvaluationResult):
        """Update the judge feedback log with evaluation feedback."""
        evaluation_feedback = result.feedback.model_dump()
        evaluation_feedback.pop("execution_history", None)

        log_file = PROJECT_BASE_DIR / "judge_tests_usage_logs.jsonl"
        if not log_file.exists():
            logger.warning(f"Judge usage log not found at {log_file}; skipping feedback update.")
            return

        task_prompt_hash = generate_hash(task.prompt)
        total_iterations = len(result.execution_history)
        updated_entries = []

        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if generate_hash(entry.get("task")) == task_prompt_hash and entry["total_iteration"] == total_iterations:
                        entry["evaluation_feedback"] = evaluation_feedback
                    updated_entries.append(entry)
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON line in {log_file}")

        with log_file.open("w", encoding="utf-8") as f:
            for entry in updated_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------------
    # SOLUTION GENERATION
    # ------------------------------------------------------------------------
    async def generate_solutions(self, agent: IWebAgent, tasks: list[Task], timing_metrics: TimingMetrics) -> dict[str, TaskSolution]:
        """Generate or load solutions for a given agent and tasks."""
        solutions = {}
        logger.info(f"\nAgent: {agent.name}")

        for task in tasks:
            task_solution: TaskSolution | None = None

            # Load cached solution if available
            if self.config.use_cached_solutions and self.solution_cache.solution_exists(task.id, agent.id):
                try:
                    logger.info(f"  Loading cached solution for Task {task.id}...")
                    task_solution = await self.solution_cache.load_solution(task.id, agent.id)
                    if task_solution:
                        logger.info(f"    Loaded cached solution with {len(task_solution.actions)} actions")
                except Exception as e:
                    logger.error(f"    Error loading cached solution: {e!s}")

            # Generate new solution if needed
            if task_solution is None:
                logger.info(f"  Generating new solution for Task {task.id}...")
                start_time = time.time()
                solution = await agent.solve_task(task)
                task_solution = TaskSolution(task_id=task.id, actions=solution.actions or [], web_agent_id=agent.id)
                duration = time.time() - start_time
                timing_metrics.record_solution_time(agent.id, task.id, duration)
                logger.info(f"    Solution generated in {duration:.2f}s with {len(task_solution.actions)} actions")

                try:
                    success = self.solution_cache.save_solution(task_solution=task_solution, agent_id=agent.id, agent_name=agent.name)
                    if success:
                        logger.info("Solution cached successfully for future runs")
                    else:
                        logger.warning("Failed to cache solution")
                except Exception as e:
                    logger.error(f"Error caching solution: {e!s}")

            solutions[task.id] = task_solution

        return solutions

    # ------------------------------------------------------------------------
    # EVALUATE SOLUTIONS
    # ------------------------------------------------------------------------
    async def evaluate_solutions(self, agent: IWebAgent, tasks: list[Task], solutions: dict[str, TaskSolution], demo_project: WebProject) -> dict[str, dict]:
        """Evaluate task solutions."""
        results = {}
        logger.info(f"\nEvaluating solutions for Agent: {agent.name}")

        for task in tasks:
            logger.info(f"  Evaluating Task {task.id}...")
            task_solution = solutions[task.id]
            eval_result = await self.evaluate_task_solution(demo_project, task, task_solution, "benchmark_evaluator")
            results[task.id] = {"score": eval_result.final_score, "evaluation_result": eval_result}
        return results

    # ------------------------------------------------------------------------
    # ORCHESTRATE FULL RUN
    # ------------------------------------------------------------------------
    async def run_evaluation(self, demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
        """Run the full evaluation process."""
        all_solutions = {agent.id: await self.generate_solutions(agent, tasks, timing_metrics) for agent in self.agents}
        results = {agent.id: await self.evaluate_solutions(agent, tasks, all_solutions[agent.id], demo_project) for agent in self.agents}

        print_performance_statistics(results, self.agents, timing_metrics)
        plot_results(results, self.agents, timing_metrics, str(self.config.output_dir))
        # plot_task_comparison(results, self.agents, tasks, str(self.config.output_dir))
        results = save_results_to_json(results, self.agents, timing_metrics, str(self.config.output_dir))
        return results

    # ------------------------------------------------------------------------
    # MAIN EXECUTION ENTRYPOINT
    # ------------------------------------------------------------------------
    async def run(self):
        """Main entrypoint for the benchmark process."""
        logger.info("Starting WebVoyager Benchmark...")
        AppBootstrap()
        timing_metrics = TimingMetrics()
        timing_metrics.start()
        results = {}

        task = {"url": self.config.url, "prompt": self.config.prompt}
        tasks_data = load_real_tasks(num_of_urls=self.config.num_of_urls, task=task, by_indices=self.config.task_indices)
        web_projects = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}

        for td in tasks_data:
            project = web_projects.get(td.id)
            if project:
                tasks = await self.generate_tasks(td)
                if tasks:
                    results[td.id] = await self.run_evaluation(project, tasks, timing_metrics)

        logger.info("Benchmark Evaluation Complete!")
        return results


# ------------------------------------------------------------------------
# RUN SCRIPT
# ------------------------------------------------------------------------
if __name__ == "__main__":
    config = WebVoyagerConfig()
    benchmark = WebVoyagerBenchmark(config)
    asyncio.run(benchmark.run())
