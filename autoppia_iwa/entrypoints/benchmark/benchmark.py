import asyncio
import base64
import time
from collections import defaultdict

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.entrypoints.benchmark.utils.results import (
    plot_results,
    save_results_to_json,
)
from autoppia_iwa.entrypoints.benchmark.utils.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

from .config import BenchmarkConfig
from .task_generation import generate_tasks_for_project

visualizer = SubnetVisualizer()


class Benchmark:
    """
    High-level orchestrator for the benchmark sandbox:
      1) Generate (or load cached) tasks for selected demo web projects.
      2) Dispatch each task to the configured web agents.
      3) Evaluate agent solutions.
      4) Persist results, timings, and optional artifacts (GIFs/plots).
    """

    def __init__(self, config: BenchmarkConfig, log_file: str = "benchmark.log") -> None:
        self.config = config
        self._agent_call_semaphore = asyncio.Semaphore(config.max_parallel_agent_calls)
        self._solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))
        self._timing_metrics = TimingMetrics()

        # Per-agent global rollup across all projects and runs.
        self._global_agent_rollup: dict[str, dict[str, float | int]] = defaultdict(lambda: {"success": 0, "total": 0, "time_sum": 0.0, "time_cnt": 0})

        # Validate configuration before starting
        self._validate_config()

        setup_logging(log_file)

    def _validate_config(self) -> None:
        """
        Validate the benchmark configuration before starting execution.
        """
        if not self.config.projects:
            raise ValueError("No projects configured. Please add at least one project to PROJECT_IDS.")

        if not self.config.agents:
            raise ValueError("No agents configured. Please add at least one agent to AGENTS.")

        if self.config.runs <= 0:
            raise ValueError("Number of runs must be greater than 0.")

        if self.config.max_parallel_agent_calls <= 0:
            raise ValueError("max_parallel_agent_calls must be greater than 0.")

        # Validate agent uniqueness
        agent_ids = [agent.id for agent in self.config.agents]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("Agent IDs must be unique.")

        logger.info(f"Configuration validated: {len(self.config.projects)} projects, {len(self.config.agents)} agents, {self.config.runs} runs")

    # ---------------------------------------------------------------------
    # Artifact helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _persist_gif_recording(b64_gif: str, agent_name: str, task_id: str, run_index: int, recordings_dir) -> None:
        """
        Decode a base64-encoded GIF and store it under recordings/<agent>/<task>_run_<n>.gif.
        """
        agent_dir = recordings_dir / agent_name
        agent_dir.mkdir(exist_ok=True)
        (agent_dir / f"{task_id}_run_{run_index}.gif").write_bytes(base64.b64decode(b64_gif))
        logger.info(f"GIF saved: {agent_name} -> {task_id} (run {run_index})")

    # ---------------------------------------------------------------------
    # Core per-task/per-agent execution
    # ---------------------------------------------------------------------

    async def _solve_task_with_agent(
        self,
        project: WebProject,
        agent: IWebAgent,
        task: Task,
        run_index: int,
    ) -> TaskSolution | None:
        """
        Resolve a single Task with a single Agent.
        Optionally uses a cached solution when configured.
        Resets the project backend DB for isolation per attempt.
        """
        async with self._agent_call_semaphore:
            backend = None
            try:
                backend = BackendDemoWebService(project)
                await backend.reset_database()

                # Prefer cached solution if enabled and present
                if self.config.use_cached_solutions:
                    try:
                        cached = await self._solution_cache.load_solution(task.id, agent.id)
                        if cached and cached.actions:
                            logger.info(f"Using cached solution for {agent.name} on task {task.id}")
                            return cached
                    except Exception as e:
                        logger.warning(f"Failed to load cached solution for {agent.name} on task {task.id}: {e}")

                start_ts = time.time()

                prepared_task = task.prepare_for_agent(agent.id)
                solution = await agent.solve_task(prepared_task)

                if not solution:
                    logger.warning(f"{agent.name} returned empty solution for task {task.id}")
                    return None

                task_solution = TaskSolution(
                    task_id=task.id,
                    actions=solution.actions or [],
                    web_agent_id=agent.id,
                )
                # Normalize any embedded agent IDs inside actions if needed
                task_solution.actions = task_solution.replace_web_agent_id()

                solution_time = time.time() - start_ts
                self._timing_metrics.record_solution_time(agent.id, task.id, solution_time)

                # Save solution to cache with error handling
                try:
                    self._solution_cache.save_solution(task_solution, agent.id, agent.name)
                except Exception as e:
                    logger.warning(f"Failed to save solution to cache: {e}")

                logger.debug(f"{agent.name} solved task {task.id} in {solution_time:.2f}s")
                return task_solution

            except Exception as exc:
                logger.error(f"{agent.name} failed on task {task.id} (run {run_index}): {exc!r}", exc_info=True)
                return None
            finally:
                if backend:
                    try:
                        await backend.close()
                    except Exception as e:
                        logger.warning(f"Error closing backend for {project.name}: {e}")

    async def _evaluate_solutions_for_task(
        self,
        project: WebProject,
        task: Task,
        solutions: list[TaskSolution | None],
        run_index: int,
    ):
        """
        Evaluate all agent solutions produced for a single Task.
        Stores GIF recordings if evaluation returns them and recording is enabled.
        """
        evaluator = ConcurrentEvaluator(project, EvaluatorConfig(enable_grouping_tasks=False, chunk_size=20))
        results = await evaluator.evaluate_task_solutions(task, solutions)

        if self.config.record_gif:
            for res in results:
                if getattr(res, "gif_recording", None):
                    agent_name = next((a.name for a in self.config.agents if a.id == res.web_agent_id), "unknown")
                    self._persist_gif_recording(res.gif_recording, agent_name, task.id, run_index, self.config.recordings_dir)
        return results

    async def _evaluate_solutions_for_task_with_visualization(
        self,
        project: WebProject,
        task: Task,
        solutions: list[TaskSolution | None],
        validator_id: str,
        run_index: int = 1,
    ):
        """
        Wrapper method for evaluation with visualization support.
        This method matches the expected signature for the visualize_list_of_evaluations decorator.
        """
        try:
            # Filter out None solutions for visualization
            valid_solutions = [sol for sol in solutions if sol is not None]

            # Call the actual evaluation method
            results = await self._evaluate_solutions_for_task(project, task, solutions, run_index)

            # Apply visualization if we have valid results and visualization is enabled
            if self.config.enable_visualization and results and valid_solutions:
                try:
                    visualizer.show_list_of_evaluations(task, valid_solutions, results, validator_id)
                except Exception as e:
                    logger.warning(f"Visualization failed: {e}")

            return results

        except Exception as e:
            logger.error(f"Evaluation with visualization failed: {e}", exc_info=True)
            # Fallback to regular evaluation without visualization
            return await self._evaluate_solutions_for_task(project, task, solutions, run_index)

    # ---------------------------------------------------------------------
    # Per-project execution
    # ---------------------------------------------------------------------
    async def _generate_tasks_for_project(self, project: WebProject) -> list[Task]:
        tasks = await generate_tasks_for_project(
            project=project,
            use_cached=self.config.use_cached_tasks,
            cache_dir=str(self.config.tasks_cache_dir),
            prompts_per_use_case=self.config.prompts_per_use_case,
            num_use_cases=self.config.num_use_cases,
        )

        # Apply visualization if we have tasks and visualization is enabled
        if self.config.enable_visualization and tasks:
            try:
                for task in tasks:
                    visualizer.show_task_with_tests(task)
            except Exception as e:
                logger.warning(f"Task visualization failed: {e}")

        return tasks

    async def _execute_single_project_run(self, project: WebProject, run_index: int) -> dict[str, dict]:
        """
        Execute a single benchmark run for a given project:
          - Generate or load cached Tasks for the project.
          - Solve each Task with all configured Agents.
          - Evaluate all produced solutions.
          - Return a per-agent result mapping for this run.

        Returns a dict keyed by agent_id, each containing task results:
            {
              "<agent_id>": {
                "<task_id>": { "prompt": str, "score": float, "task_use_case": str }
              },
              ...
            }
        """
        tasks = await self._generate_tasks_for_project(project)
        if not tasks:
            logger.warning(f"No tasks for project '{project.name}' — skipping run {run_index}")
            return {}

        # Inform evaluator whether to record GIFs
        for task in tasks:
            task.should_record = self.config.record_gif

        per_agent_results_for_run: dict[str, dict] = {}

        for task in tasks:
            # Solve with all agents
            task_solutions = await asyncio.gather(*[self._solve_task_with_agent(project, agent, task, run_index) for agent in self.config.agents])

            # Evaluate solutions with visualization
            evaluations = await self._evaluate_solutions_for_task_with_visualization(project, task, task_solutions, "benchmark_evaluator", run_index)

            # Aggregate results by agent
            for ev in evaluations:
                use_case_name = getattr(task.use_case, "name", "Unknown")
                per_agent_results_for_run.setdefault(ev.web_agent_id, {})[task.id] = {
                    "prompt": task.prompt,
                    "score": ev.final_score,
                    "task_use_case": use_case_name,
                }

        return per_agent_results_for_run

    # ---------------------------------------------------------------------
    # Global rollups and persistence
    # ---------------------------------------------------------------------

    def _accumulate_global_agent_rollup(self, project_run_results: list[dict]) -> None:
        """
        Update global per-agent rollups (success/total/avg-time) using
        the list of per-run results for the current project.
        """
        per_agent_scores: dict[str, list[float]] = defaultdict(list)
        per_agent_solution_times: dict[str, list[float]] = defaultdict(list)

        for run_result in project_run_results:
            for agent in self.config.agents:
                if agent.id not in run_result:
                    continue
                for task_id, res in run_result[agent.id].items():
                    per_agent_scores[agent.name].append(res["score"])
                    t = self._timing_metrics.solution_times.get(agent.id, {}).get(task_id, 0.0)
                    per_agent_solution_times[agent.name].append(t)

        # Update the global rollup state and log a one-line summary per agent
        for agent in self.config.agents:
            scores = per_agent_scores[agent.name]
            times = per_agent_solution_times[agent.name]

            success_count = sum(1 for s in scores if s == 1.0)
            total_count = len(scores)

            rollup = self._global_agent_rollup[agent.name]
            rollup["success"] += success_count
            rollup["total"] += total_count
            rollup["time_sum"] += sum(times)
            rollup["time_cnt"] += len(times)

            success_rate = (success_count / total_count) if total_count else 0.0
            avg_time = (sum(times) / len(times)) if times else 0.0
            logger.info(f"{agent.name:<20} | {success_rate * 100:6.2f}% ({success_count}/{total_count}) | avg {avg_time:.2f}s")

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    async def run(self) -> None:
        """
        Execute the complete benchmark across all configured projects and runs.
        This is the main entrypoint you should call.
        """
        logger.info("Starting benchmark…")
        self._timing_metrics.start()

        total_projects = len(self.config.projects)
        successful_projects = 0

        try:
            for project_index, project in enumerate(self.config.projects, 1):
                logger.info(f"\n=== Project {project_index}/{total_projects}: {project.name} ===")
                project_run_results: list[dict] = []

                try:
                    for run_index in range(1, self.config.runs + 1):
                        logger.info(f"Run {run_index}/{self.config.runs}")
                        try:
                            run_result = await self._execute_single_project_run(project, run_index)
                            if run_result:
                                project_run_results.append(run_result)
                            else:
                                logger.warning(f"Run {run_index} for project {project.name} returned no results")
                                import traceback

                                traceback.print_exc()
                        except Exception as e:
                            logger.error(f"Run {run_index} for project {project.name} failed: {e}", exc_info=True)
                            continue

                    if project_run_results:
                        # Update global stats and persist artifacts for the last run of this project
                        self._accumulate_global_agent_rollup(project_run_results)
                        successful_projects += 1

                        last_run_result = project_run_results[-1]
                        if self.config.save_results_json:
                            try:
                                save_results_to_json(last_run_result, self.config.agents, self._timing_metrics, str(self.config.output_dir))
                            except Exception as e:
                                logger.error(f"Failed to save results JSON for project {project.name}: {e}")

                        if self.config.plot_results:
                            try:
                                plot_results(last_run_result, self.config.agents, self._timing_metrics, str(self.config.output_dir))
                            except Exception as e:
                                logger.error(f"Failed to generate plots for project {project.name}: {e}")
                    else:
                        logger.warning(f"No successful runs for project {project.name}")

                except Exception as e:
                    logger.error(f"Project {project.name} failed completely: {e}", exc_info=True)
                    continue

        except Exception as e:
            logger.error(f"Critical error during benchmark execution: {e}", exc_info=True)
            raise
        finally:
            self._timing_metrics.end()

        logger.success(f"Benchmark finished ✔ - {successful_projects}/{total_projects} projects completed successfully")

    # Optional convenience alias if you prefer a more explicit public name
    async def execute(self) -> None:
        """
        Alias to `run()` for a more explicit call site name.
        """
        await self.run()
