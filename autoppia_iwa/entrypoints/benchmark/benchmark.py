import asyncio
import base64
import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import VALIDATOR_ID
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution

visualizer = SubnetVisualizer()


class Benchmark:
    """
    High-level orchestrator for the benchmark sandbox:
      1) Generate tasks for selected demo web projects.
      2) Dispatch each task to the configured web agents.
      3) Evaluate agent solutions.
      4) Persist results, timings, and optional artifacts (GIFs).
    """

    def __init__(self, config: BenchmarkConfig, log_file: Path | str | None = None) -> None:
        self.config = config
        self._agent_call_semaphore = asyncio.Semaphore(config.max_parallel_agent_calls)
        self._timing_metrics = TimingMetrics()

        # Validate configuration before starting
        self._validate_config()

        resolved_log_path = Path(log_file) if log_file else config.benchmark_log_file
        resolved_log_path.parent.mkdir(parents=True, exist_ok=True)
        setup_logging(str(resolved_log_path))
        self.per_project_results = {}

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
    def _persist_gif_refixcording(b64_gif: str, agent_name: str, task_id: str, run_index: int, recordings_dir) -> None:
        """
        Decode a base64-encoded GIF and store it under benchmark-output/recordings/<agent>/<task>_run_<n>.gif.
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
        Resets the project backend DB for isolation per attempt.
        """
        async with self._agent_call_semaphore:
            backend = None
            try:
                backend = BackendDemoWebService(project)
                await backend.reset_database(web_agent_id=agent.id)

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

            # Call the actual evaluation method (will filter None internally)
            results = await self._evaluate_solutions_for_task(project, task, solutions, run_index)

            # Apply visualization if we have valid results and visualization is enabled
            if results and valid_solutions:
                try:
                    visualizer.show_list_of_evaluations(task, valid_solutions, results, validator_id)
                except Exception as e:
                    logger.warning(f"Visualization failed: {e}")

            return results

        except Exception as e:
            logger.error(f"Evaluation with visualization failed: {e}", exc_info=True)
            # Fallback to regular evaluation without visualization
            return await self._evaluate_solutions_for_task(project, task, solutions, run_index)

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
        # Filter out None solutions defensively
        valid_solutions = [s for s in solutions if s is not None]
        if not valid_solutions:
            logger.warning(f"No valid solutions to evaluate for task {task.id} (run {run_index})")
            return []

        evaluator = ConcurrentEvaluator(
            project,
            EvaluatorConfig(
                enable_grouping_tasks=False,
                chunk_size=20,
                should_record_gif=self.config.record_gif,
            ),
        )
        results = await evaluator.evaluate_task_solutions(task, valid_solutions)

        if self.config.record_gif:
            for res in results:
                if getattr(res, "gif_recording", None):
                    agent_name = next((a.name for a in self.config.agents if a.id == res.web_agent_id), "unknown")
                    self._persist_gif_recording(res.gif_recording, agent_name, task.id, run_index, self.config.recordings_dir)
        return results
    # ---------------------------------------------------------------------
    # Per-project execution
    # ---------------------------------------------------------------------
    async def _generate_tasks_for_project(self, project: WebProject) -> list[Task]:
        from autoppia_iwa.src.data_generation.tasks.classes import TaskGenerationConfig
        from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline

        config = TaskGenerationConfig(
            prompts_per_use_case=self.config.prompts_per_use_case,
            use_cases=self.config.use_cases,
            dynamic=self.config.dynamic,
        )
        pipeline = TaskGenerationPipeline(web_project=project, config=config)
        tasks = await pipeline.generate()

        if tasks:
            try:
                for task in tasks:
                    visualizer.show_task_with_tests(task)
            except Exception as e:
                logger.warning(f"Task visualization failed: {e}")

        return tasks

    async def _execute_single_project_run(self, project: WebProject, run_index: int) -> dict[str, dict]:
        """
        Execute a single benchmark run for a given project:
          - Generate Tasks for the project.
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

        # Configure task settings for this run
        for task in tasks:
            task.should_record = self.config.record_gif

        per_agent_results_for_run: dict[str, dict] = {}

        for task in tasks:
            # Solve with all agents
            task_solutions = await asyncio.gather(*[self._solve_task_with_agent(project, agent, task, run_index) for agent in self.config.agents])

            # Evaluate solutions with visualization
            evaluations = await self._evaluate_solutions_for_task_with_visualization(project, task, task_solutions, VALIDATOR_ID, run_index)

            # Aggregate results by agent
            for ev in evaluations:
                use_case_name = getattr(task.use_case, "name", "Unknown")
                actions = [a.action.model_dump() for a in getattr(ev, "execution_history", [])]
                per_agent_results_for_run.setdefault(ev.web_agent_id, {})[task.id] = {
                    "prompt": task.prompt,
                    "score": ev.final_score,
                    "task_use_case": use_case_name,
                    "actions": actions,
                    "base64_gif": ev.gif_recording if self.config.record_gif else None,
                }

        return per_agent_results_for_run

    # ---------------------------------------------------------------------
    # Results aggregation and persistence
    # ---------------------------------------------------------------------

    def _save_consolidated_results(self) -> None:
        """
        Save all project results to a single consolidated JSON file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.config.output_dir / f"benchmark_results_{timestamp}.json"
        
        consolidated_data = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": self._timing_metrics.get_total_time(),
            "projects": self.per_project_results,
        }
        
        filename.write_text(json.dumps(consolidated_data, indent=2))
        logger.info(f"Consolidated results saved to {filename}")

    def _accumulate_project_stats(self, project: WebProject, project_run_results: list[dict]) -> None:
        """
        Accumulate per-agent statistics for a project.
        Results are stored in self.per_project_results and saved at the end.

        `project_run_results` is a list (one per run) of dicts keyed by agent_id:
            {
              "<agent_id>": {
                "<task_id>": { "prompt": str, "score": float, "task_use_case": str }
              }
            }
        """
        # For logging + global rollup (flat across all use cases)
        per_agent_scores_flat: dict[str, list[float]] = defaultdict(list)
        per_agent_times_flat: dict[str, list[float]] = defaultdict(list)

        # For JSON persistence (nested by use case)
        per_agent_usecase_scores: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_times: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_prompt: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_actions: dict[str, dict[str, list[list]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_task_ids: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_gifs: dict[str, dict[str, list[str | None]]] = defaultdict(lambda: defaultdict(list))

        # Collect data from all runs
        for run_result in project_run_results:
            for agent in self.config.agents:
                a_id = agent.id
                a_name = agent.name
                if a_id not in run_result:
                    continue

                for task_id, res in run_result[a_id].items():
                    use_case = res.get("task_use_case", "Unknown")
                    score = float(res.get("score", 0.0))

                    # Timing per (agent, task) recorded by TimingMetrics
                    t = self._timing_metrics.solution_times.get(a_id, {}).get(task_id, 0.0)

                    # Flat rolls (for logging + global)
                    per_agent_scores_flat[a_name].append(score)
                    per_agent_times_flat[a_name].append(t)

                    # Use-case rolls (for JSON)
                    per_agent_usecase_scores[a_name][use_case].append(score)
                    per_agent_usecase_times[a_name][use_case].append(t)

                    per_agent_usecase_prompt[a_name][use_case].append(res.get("prompt", ""))
                    per_agent_usecase_actions[a_name][use_case].append(res.get("actions", []))
                    per_agent_usecase_task_ids[a_name][use_case].append(task_id)
                    per_agent_usecase_gifs[a_name][use_case].append(res.get("base64_gif", None))

        # Build per-project stats
        project_stats: dict = {}

        for agent in self.config.agents:
            a_name = agent.name

            all_scores: list[float] = []
            all_times: list[float] = []
            new_uc_block: dict[str, dict] = {}

            for uc, scores in per_agent_usecase_scores[a_name].items():
                times = per_agent_usecase_times[a_name][uc]

                new_uc_block[uc] = {}
                for task_id, prompt, action, t, score, gif in zip(
                    per_agent_usecase_task_ids[a_name][uc],
                    per_agent_usecase_prompt[a_name][uc],
                    per_agent_usecase_actions[a_name][uc],
                    per_agent_usecase_times[a_name][uc],
                    per_agent_usecase_scores[a_name][uc],
                    per_agent_usecase_gifs[a_name][uc],
                    strict=False,
                ):
                    new_uc_block[uc][task_id] = {
                        "success": score,
                        "time": round(t, 3),
                        "prompt": prompt,
                        "actions": action,
                        "base64_gif": gif,
                    }

                all_scores.extend(scores)
                all_times.extend(times)

            succ_all = sum(1 for s in all_scores if s == 1.0)
            tot_all = len(all_scores)
            avg_all_time = (sum(all_times) / len(all_times)) if all_times else 0.0
            rate_all = (succ_all / tot_all) if tot_all else 0.0

            project_stats[a_name] = {
                "use_cases": new_uc_block,
                "overall": {
                    "success_count": succ_all,
                    "total": tot_all,
                    "success_rate": round(rate_all, 3),
                    "avg_solution_time": round(avg_all_time, 3),
                },
            }

            logger.info(f"{a_name:<20} | {rate_all * 100:6.2f}% ({succ_all}/{tot_all}) | avg {avg_all_time:.2f}s")

        # Store per-project stats (will be saved in a single file at the end)
        self.per_project_results[project.name] = project_stats

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    async def run(self) -> dict:
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
                        except Exception as e:
                            logger.error(f"Run {run_index} for project {project.name} failed: {e}", exc_info=True)
                            continue

                    if project_run_results:
                        # Accumulate stats for this project
                        self._accumulate_project_stats(project, project_run_results)
                        successful_projects += 1
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

        # Save consolidated results to a single file
        if self.config.save_results_json and self.per_project_results:
            try:
                self._save_consolidated_results()
            except Exception as e:
                logger.error(f"Failed to save consolidated results: {e}")

        logger.success(f"Benchmark finished ✔ - {successful_projects}/{total_projects} projects completed successfully")

        return self.per_project_results

