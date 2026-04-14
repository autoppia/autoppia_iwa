import asyncio
import base64
import contextlib
import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from autoppia_iwa.config.config import VALIDATOR_ID
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.logging import log_step, log_task_end, log_task_start, setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.evaluation.stateful_evaluator.evaluator import BrowserSnapshot, StepResult
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer
from autoppia_iwa.src.web_agents.act_response_utils import actions_to_act_response
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution, sanitize_snapshot_html

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
        # When using tasks_json_path, (project, tasks) loaded once at start of run()
        self._custom_tasks_cache: tuple[WebProject, list[Task]] | None = None

    def _validate_config(self) -> None:
        """
        Validate the benchmark configuration before starting execution.
        """
        if not getattr(self.config, "tasks_json_path", None) and not self.config.projects:
            raise ValueError("No projects configured. Please add at least one project to PROJECT_IDS or set tasks_json_path.")

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

        logger.info(f"Configuration validated: {len(self.config.projects)} projects, {len(self.config.agents)} agents, {self.config.runs} runs, evaluator_mode={self.config.evaluator_mode}")

        if self.config.evaluator_mode == "stateful":
            logger.info(f"Stateful mode: max {self.config.max_steps_per_task} steps per task")

    @staticmethod
    def _build_compact_history(execution_history: list[Any]) -> list[dict[str, Any]]:
        """Build a compact history payload for /act requests."""
        out: list[dict[str, Any]] = []
        for idx, event in enumerate(execution_history):
            action_payload: dict[str, Any] | None = None
            with contextlib.suppress(Exception):
                raw_action = getattr(event, "action", None)
                if raw_action is not None and hasattr(raw_action, "model_dump"):
                    action_payload = raw_action.model_dump()

            browser_url = None
            browser_timestamp = None
            snapshot = getattr(event, "browser_snapshot", None)
            if snapshot is not None:
                browser_url = getattr(snapshot, "current_url", None)
                ts = getattr(snapshot, "timestamp", None)
                if ts is not None:
                    browser_timestamp = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)

            out.append(
                {
                    "index": idx,
                    "action": action_payload,
                    "success": bool(getattr(event, "successfully_executed", False)),
                    "error": getattr(event, "error", None),
                    "url": browser_url,
                    "timestamp": browser_timestamp,
                }
            )
        return out

    # ---------------------------------------------------------------------
    # Evaluator creation
    # ---------------------------------------------------------------------
    def _create_evaluator(self, project: WebProject) -> ConcurrentEvaluator:
        """
        Create the ConcurrentEvaluator to evaluate complete solutions.
        For stateful mode, AsyncStatefulEvaluator is used directly in _evaluate_task_with_agents.
        """
        evaluator_config = EvaluatorConfig(
            should_record_gif=self.config.record_gif,
            enable_grouping_tasks=False,
            chunk_size=20,
            max_consecutive_action_failures=2,
            verbose_logging=False,
            debug_mode=False,
            headless=self.config.headless,
        )

        logger.debug(f"Creating ConcurrentEvaluator for project {project.id}")
        return ConcurrentEvaluator(web_project=project, config=evaluator_config)

    @staticmethod
    def _get_usage_from_agent(agent: IWebAgent) -> dict[str, Any]:
        """
        Get usage (input_tokens, output_tokens, cost_usd) from the agent's last act() response.
        Agents that include usage in their /act response (e.g. ApifiedWebAgent) expose it via get_last_usage().
        Returns dict with keys input_tokens, output_tokens, cost_usd (values may be None).
        """
        if hasattr(agent, "get_last_usage") and callable(agent.get_last_usage):
            return agent.get_last_usage()
        return {"input_tokens": None, "output_tokens": None, "cost_usd": None}

    async def _evaluate_with_stateful_evaluator(
        self,
        task: Task,
        agent: IWebAgent,
        max_steps: int,
    ) -> EvaluationResult:
        """
        Evaluate an agent using AsyncStatefulEvaluator in iterative mode.

        The agent must implement IWebAgent with an act() method.
        Typically this is an ApifiedWebAgent (HTTP agent) running on a server.

        The agent must be running on an HTTP server and respond at:
        POST /act with: {task, snapshot_html, url, step_index, history, state_in, allowed_tools}
        Response: {tool_calls: [...], content, done, state_out, reasoning}
        """
        # Verify that the agent has an act() method
        if not hasattr(agent, "act") or not callable(getattr(agent, "act", None)):
            raise ValueError(
                f"Agent '{agent.name}' does not implement IWebAgent correctly.\nIt must have an act() method that receives the browser state.\nUse: ApifiedWebAgent(base_url='http://localhost:PORT')"
            )

        evaluator = AsyncStatefulEvaluator(
            task=task,
            web_agent_id=agent.id,
            should_record_gif=self.config.record_gif,
            capture_screenshot=False,
            headless=self.config.headless,
        )

        start_ts = time.time()
        final_score = 0.0
        tests_passed = 0
        total_tests = 0
        execution_history = []
        # Track usage from each act() response (no separate API call)
        cum_input_tokens: int = 0
        cum_output_tokens: int = 0
        cum_cost_usd: float = 0.0
        had_any_usage: bool = False

        try:
            step_index = 0  # Number of CALLS to the agent
            total_actions_executed = 0  # Number of ACTIONS executed

            step_result = await evaluator.reset()
            final_score = step_result.score.raw_score
            tests_passed = step_result.score.tests_passed
            total_tests = step_result.score.total_tests

            # Use total_actions_executed as the limit (same as the subnet)
            while total_actions_executed < max_steps and not bool(step_result.score.success):
                snapshot = step_result.snapshot
                html = sanitize_snapshot_html(snapshot.html or "", agent.id)
                current_url = snapshot.url or task.url

                try:
                    # Call the agent's HTTP /act endpoint (same as the subnet with miners)
                    # ✅ Llamar al endpoint /act del agente HTTP (IGUAL que la subnet con miners)
                    act_result = await agent.act(
                        task=task,
                        snapshot_html=html,
                        url=current_url,
                        step_index=step_index,
                        history=self._build_compact_history(execution_history),
                    )
                except Exception as exc:
                    logger.warning(f"[stateful_eval] agent {agent.name} /act failed: {exc}")
                    act_result = []

                if isinstance(act_result, dict):
                    actions = act_result.get("actions", [])
                    if "extracted_data" in act_result:
                        evaluator.latest_extracted_data = act_result["extracted_data"]
                else:
                    actions = act_result

                # Accumulate usage from this act() response (benchmark-side tracking)
                usage = self._get_usage_from_agent(agent)
                if usage.get("input_tokens") is not None:
                    had_any_usage = True
                    cum_input_tokens += usage["input_tokens"]
                if usage.get("output_tokens") is not None:
                    had_any_usage = True
                    cum_output_tokens += usage["output_tokens"]
                if usage.get("cost_usd") is not None:
                    had_any_usage = True
                    cum_cost_usd += float(usage["cost_usd"])

                if not actions:
                    # No actions = agent finished or error
                    if self.config.test_types == "data_extraction_only" and isinstance(act_result, dict) and "extracted_data" in act_result:
                        score_details = await evaluator.get_score_details()
                        final_score = score_details.raw_score
                        tests_passed = score_details.tests_passed
                        total_tests = score_details.total_tests
                        snap = step_result.snapshot
                        page = evaluator.page
                        if page:
                            with contextlib.suppress(Exception):
                                snap = BrowserSnapshot(
                                    html=await page.content() or "",
                                    url=page.url or task.url,
                                    screenshot=None,
                                )
                        step_result = StepResult(score=score_details, snapshot=snap, action_result=None)
                        logger.debug(f"[stateful_eval] agent {agent.name} no actions, data_extraction re-score raw={final_score} success={score_details.success}")
                        if score_details.success:
                            logger.info(f"[stateful_eval] agent {agent.name} completed task (data extraction)!")
                            break
                        step_index += 1
                        continue
                    logger.debug(f"[stateful_eval] agent {agent.name} returned no actions, terminating")
                    break

                log_step(agent.id or "", task.id or "", step_index, len(actions))

                # Compute limit with total_actions_executed (same as subnet)
                actions_to_execute = actions[: min(len(actions), max_steps - total_actions_executed)]

                logger.debug(f"[stateful_eval] agent {agent.name} returned {len(actions)} actions, executing {len(actions_to_execute)}")

                # Execute ALL actions in batch (the evaluator replaces placeholders internally)
                for action in actions_to_execute:
                    step_result = await evaluator.step(action)
                    final_score = step_result.score.raw_score
                    tests_passed = step_result.score.tests_passed
                    total_tests = step_result.score.total_tests
                    total_actions_executed += 1

                    # Store the action result
                    if step_result.action_result:
                        execution_history.append(step_result.action_result)

                    # If the task was completed, stop
                    if step_result.score.success:
                        logger.info(f"[stateful_eval] agent {agent.name} completed task!")
                        break

                # If completed, exit the main loop
                if step_result.score.success:
                    break

                step_index += 1

        except Exception as exc:
            logger.error(f"[stateful_eval] agent {agent.name} evaluation error: {exc}")
            final_score = 0.0
        finally:
            with contextlib.suppress(Exception):
                await evaluator.close()

        elapsed = time.time() - start_ts

        # Use benchmark-tracked usage (from act() responses); no separate API call
        cost_usd = cum_cost_usd if had_any_usage else None
        input_tokens = cum_input_tokens if had_any_usage else None
        output_tokens = cum_output_tokens if had_any_usage else None
        if cost_usd is not None or input_tokens is not None or output_tokens is not None:
            logger.debug(f"Task {task.id} usage: cost_usd={cost_usd} in={input_tokens} out={output_tokens}")

        return EvaluationResult(
            final_score=max(0.0, min(final_score, 1.0)),
            raw_score=final_score,
            web_agent_id=agent.id,
            execution_history=execution_history,
            evaluation_time=elapsed,
            cost_usd=cost_usd,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            stats=EvaluationStats(
                web_agent_id=agent.id,
                task_id=task.id,
                action_count=total_actions_executed,
                start_time=start_ts,
                total_time=elapsed,
                raw_score=final_score,
                final_score=max(0.0, min(final_score, 1.0)),
                tests_passed=tests_passed,
                total_tests=total_tests,
            ),
        )

    # ---------------------------------------------------------------------
    # Artifact helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _persist_gif_recording(b64_gif: str, agent_name: str, task_id: str, run_index: int, recordings_dir) -> None:
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
        Solve a single Task with a single Agent using act().

        All agents use act() now (both concurrent and stateful).
        In concurrent mode, we call act() once with the initial state.

        Optionally uses a cached solution when configured.
        Resets the project backend DB for isolation per attempt.
        """
        async with self._agent_call_semaphore:
            backend = None
            try:
                backend = BackendDemoWebService(project)
                await backend.reset_database(web_agent_id=agent.id)

                start_ts = time.time()

                # Use act() instead of solve_task()
                # In concurrent mode, we call once with an empty initial snapshot
                # Send task WITH placeholders - agent should return actions with placeholders
                # Agent may return list[BaseAction] or dict with "actions" and optionally "extracted_data" (for DataExtractionTest)
                act_result = await agent.act(
                    task=task,  # Send task with placeholders, NOT replaced
                    snapshot_html="",  # Empty in concurrent mode (agent does not need to see HTML)
                    url=task.url,
                    step_index=0,  # Always 0 in concurrent mode
                )

                if isinstance(act_result, dict):
                    actions = act_result.get("actions", [])
                    extracted_data = act_result.get("extracted_data")
                else:
                    actions = act_result
                    extracted_data = None

                if not actions:
                    logger.warning(f"{agent.name} returned empty actions for task {task.id}")
                    return None

                task_solution = TaskSolution(
                    task_id=task.id,
                    actions=actions,
                    web_agent_id=agent.id,
                    extracted_data=extracted_data,
                )
                # Track usage from this single act() response (benchmark-side, no API call)
                usage = self._get_usage_from_agent(agent)
                if usage.get("input_tokens") is not None:
                    task_solution.input_tokens = usage["input_tokens"]
                if usage.get("output_tokens") is not None:
                    task_solution.output_tokens = usage["output_tokens"]
                if usage.get("cost_usd") is not None:
                    task_solution.cost_usd = float(usage["cost_usd"])
                # Replace credential placeholders in actions BEFORE evaluation
                task_solution.replace_credentials(agent.id)
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
        Supports both concurrent and stateful evaluation modes.
        """
        # Evaluate according to the configured mode
        if self.config.evaluator_mode == "concurrent":
            # Filter out None solutions defensively (only needed for concurrent mode)
            valid_solutions = [s for s in solutions if s is not None]
            if not valid_solutions:
                logger.warning(f"No valid solutions to evaluate for task {task.id} (run {run_index})")
                return []
            # CONCURRENT mode: evaluate all complete solutions
            evaluator = self._create_evaluator(project)
            logger.debug(f"Evaluating task {task.id} with {len(valid_solutions)} solutions (CONCURRENT mode)")
            results = await evaluator.evaluate_task_solutions(task, valid_solutions)

        elif self.config.evaluator_mode == "stateful":
            # STATEFUL mode: evaluate each agent iteratively
            # In stateful mode, we don't use pre-generated solutions
            # Instead, we call agents directly and let the evaluator call them iteratively
            logger.info(f"Evaluating task {task.id} with {len(self.config.agents)} agents (STATEFUL mode)")
            results = []

            # Iterate over agents directly (not solutions)
            for agent in self.config.agents:
                logger.info(f"Evaluating task {task.id} with agent {agent.name} (stateful, max {self.config.max_steps_per_task} steps)")

                # Use AsyncStatefulEvaluator for iterative evaluation
                # The evaluator will call agent.act() iteratively with step_index 0, 1, 2, ...
                result = await self._evaluate_with_stateful_evaluator(task=task, agent=agent, max_steps=self.config.max_steps_per_task)
                results.append(result)
        else:
            raise ValueError(f"Invalid evaluator_mode: {self.config.evaluator_mode}")

        # Record evaluation time (and solution time in stateful mode) per (agent, task)
        for ev in results:
            agent_id = getattr(ev, "web_agent_id", None)
            task_id = getattr(task, "id", None)
            if agent_id and task_id:
                eval_time = getattr(ev, "evaluation_time", None) or (getattr(ev, "stats", None) and getattr(ev.stats, "total_time", 0)) or 0
                eval_time_f = float(eval_time)
                self._timing_metrics.record_evaluation_time(agent_id, task_id, eval_time_f)
                if self.config.evaluator_mode == "stateful":
                    # In stateful mode solution is generated during evaluation; use same time for both
                    self._timing_metrics.record_solution_time(agent_id, task_id, eval_time_f)
            else:
                if not agent_id or not task_id:
                    logger.warning(f"Skipping evaluation_time record: missing web_agent_id or task.id (agent_id={agent_id!r}, task_id={task_id!r})")

        # Store GIF recordings if enabled
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

    # ---------------------------------------------------------------------
    # Per-project execution
    # ---------------------------------------------------------------------
    async def _get_tasks_for_project(self, project: WebProject, run_index: int) -> list[Task]:
        """Return tasks for this project: from custom JSON cache if applicable, else generate or load from cache."""
        if self._custom_tasks_cache is not None:
            cached_project, cached_tasks = self._custom_tasks_cache
            if cached_project.id == project.id:
                return cached_tasks
        return await self._generate_tasks_for_project(project)

    def _get_task_cache_dir(self) -> str:
        """
        Return the cache directory for generated tasks.

        Keeps event tasks and data-extraction tasks separated:
        - event_only -> benchmark-output/cache/tasks
        - data_extraction_only -> benchmark-output/cache/DataExtraction
        """
        cache_root = self.config.base_dir / "benchmark-output" / "cache"
        if getattr(self.config, "test_types", "event_only") == "data_extraction_only":
            return str(cache_root / "DataExtraction")
        return str(cache_root / "tasks")

    async def _generate_tasks_for_project(self, project: WebProject) -> list[Task]:
        from autoppia_iwa.entrypoints.benchmark.utils.task_generation import load_tasks_from_json, save_tasks_to_json
        from autoppia_iwa.src.data_generation.tasks.classes import TaskGenerationConfig
        from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline

        # Check if we should use cached tasks
        use_cached = getattr(self.config, "use_cached_tasks", False)
        cache_dir = self._get_task_cache_dir()

        if use_cached:
            cached_tasks = await load_tasks_from_json(project, cache_dir)
            if cached_tasks:
                logger.info(f"Using {len(cached_tasks)} cached tasks for '{project.name}'")
                return cached_tasks
            else:
                logger.info(f"No cached tasks found for '{project.name}', generating new tasks...")

        # Generate new tasks
        config = TaskGenerationConfig(
            prompts_per_use_case=self.config.prompts_per_use_case,
            use_cases=self.config.use_cases,
            dynamic=self.config.dynamic,
            test_types=self.config.test_types,
            data_extraction_use_cases=self.config.data_extraction_use_cases,
        )
        pipeline = TaskGenerationPipeline(web_project=project, config=config)
        tasks = await pipeline.generate()

        if tasks:
            # Save generated tasks to cache so they can be reused (e.g. via use_cached_tasks or tasks_json_path)
            saved = await save_tasks_to_json(tasks, project, cache_dir)
            if saved:
                logger.info(f"Saved {len(tasks)} generated tasks for '{project.name}' to cache")

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
        tasks = await self._get_tasks_for_project(project, run_index)
        if not tasks:
            logger.warning(f"No tasks for project '{project.name}' — skipping run {run_index}")
            return {}

        # Configure task settings for this run
        for task in tasks:
            task.should_record = self.config.record_gif

        per_agent_results_for_run: dict[str, dict] = {}

        for task in tasks:
            # Solve with all agents (skip in stateful mode - evaluator will call agents directly)
            if self.config.evaluator_mode == "stateful":
                # In stateful mode, don't pre-generate solutions
                # The evaluator will call agents directly and iteratively
                task_solutions = [None] * len(self.config.agents)
            else:
                # In concurrent mode, generate solutions first
                task_solutions = await asyncio.gather(*[self._solve_task_with_agent(project, agent, task, run_index) for agent in self.config.agents])

            # Structured log: task start per agent
            for agent in self.config.agents:
                log_task_start(
                    getattr(project, "id", "") or "",
                    getattr(task, "id", "") or "",
                    getattr(agent, "id", "") or "",
                    run_index,
                )

            # Evaluate solutions with visualization
            evaluations = await self._evaluate_solutions_for_task_with_visualization(project, task, task_solutions, VALIDATOR_ID, run_index)

            # Aggregate results by agent (include metrics for report) and log task_end
            for _idx, ev in enumerate(evaluations):
                use_case_name = getattr(task.use_case, "name", getattr(task, "de_use_case_name", "Unknown"))
                execution_history = getattr(ev, "execution_history", [])
                # Store actions in IWA format (tool_calls: list of {name, arguments})
                if execution_history:
                    base_actions = [e.action for e in execution_history if getattr(e, "action", None) is not None]
                    act_resp = actions_to_act_response(base_actions, done=False)
                    actions = [{"name": tc.name, "arguments": tc.arguments} for tc in act_resp.tool_calls]
                else:
                    actions = []
                eval_time = getattr(ev, "evaluation_time", None) or (getattr(ev, "stats", None) and getattr(ev.stats, "total_time", None))
                steps_count = len(execution_history) if execution_history else (getattr(ev, "stats", None) and getattr(ev.stats, "action_count", None))
                cost_usd = getattr(ev, "cost_usd", None)
                input_tokens = getattr(ev, "input_tokens", None)
                output_tokens = getattr(ev, "output_tokens", None)
                # Concurrent mode: attach cost/tokens from solution if available (match by web_agent_id)
                if self.config.evaluator_mode == "concurrent":
                    sol = next((s for s in task_solutions if s is not None and getattr(s, "web_agent_id", None) == ev.web_agent_id), None)
                    if sol is not None:
                        if cost_usd is None and hasattr(sol, "cost_usd"):
                            cost_usd = getattr(sol, "cost_usd", None)
                        if input_tokens is None and hasattr(sol, "input_tokens"):
                            input_tokens = getattr(sol, "input_tokens", None)
                        if output_tokens is None and hasattr(sol, "output_tokens"):
                            output_tokens = getattr(sol, "output_tokens", None)
                per_agent_results_for_run.setdefault(ev.web_agent_id, {})[task.id] = {
                    "prompt": task.prompt,
                    "score": ev.final_score,
                    "task_use_case": use_case_name,
                    "actions": actions,
                    "base64_gif": ev.gif_recording if self.config.record_gif else None,
                    "evaluation_time": eval_time,
                    "cost_usd": cost_usd,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "steps_count": steps_count,
                }

                solution_time_s = self._timing_metrics.solution_times.get(ev.web_agent_id, {}).get(task.id, 0.0)
                eval_time_s = float(eval_time) if eval_time is not None else 0.0
                log_task_end(
                    getattr(project, "id", "") or "",
                    getattr(task, "id", "") or "",
                    ev.web_agent_id or "",
                    run_index,
                    ev.final_score,
                    solution_time_s,
                    eval_time_s,
                    cost_usd=cost_usd,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

        return per_agent_results_for_run

    # ---------------------------------------------------------------------
    # Results aggregation and persistence
    # ---------------------------------------------------------------------

    def _save_consolidated_results(self) -> Path | None:
        """
        Save all project results to a single consolidated JSON file.
        Uses UTF-8 and default=str for serialization; creates output dir if needed.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.config.output_dir / f"benchmark_results_{timestamp}.json"

        tasks_source = "custom_json" if getattr(self.config, "tasks_json_path", None) else ("cached" if getattr(self.config, "use_cached_tasks", False) else "generated")
        config_summary: dict[str, Any] = {
            "evaluator_mode": self.config.evaluator_mode,
            "tasks_source": tasks_source,
        }
        if getattr(self.config, "tasks_json_path", None):
            config_summary["tasks_json_path"] = str(self.config.tasks_json_path)

        consolidated_data: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": self._timing_metrics.get_total_time(),
            "config_summary": config_summary,
            "projects": self.per_project_results,
        }

        try:
            filename.parent.mkdir(parents=True, exist_ok=True)
            filename.write_text(
                json.dumps(consolidated_data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            logger.info(f"Consolidated results saved to {filename}")
            return filename
        except OSError as e:
            logger.error(f"Failed to save consolidated results to {filename}: {e}")
            raise

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
        per_agent_usecase_eval_times: dict[str, dict[str, list[float | None]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_cost: dict[str, dict[str, list[float | None]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_input_tokens: dict[str, dict[str, list[int | None]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_output_tokens: dict[str, dict[str, list[int | None]]] = defaultdict(lambda: defaultdict(list))
        per_agent_usecase_steps_count: dict[str, dict[str, list[int | None]]] = defaultdict(lambda: defaultdict(list))

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
                    per_agent_usecase_eval_times[a_name][use_case].append(res.get("evaluation_time"))
                    per_agent_usecase_cost[a_name][use_case].append(res.get("cost_usd"))
                    per_agent_usecase_input_tokens[a_name][use_case].append(res.get("input_tokens"))
                    per_agent_usecase_output_tokens[a_name][use_case].append(res.get("output_tokens"))
                    per_agent_usecase_steps_count[a_name][use_case].append(res.get("steps_count"))

        # Build per-project stats
        project_stats: dict = {}

        for agent in self.config.agents:
            a_name = agent.name

            all_scores: list[float] = []
            all_times: list[float] = []
            all_costs: list[float] = []
            all_input_tokens: list[int] = []
            all_output_tokens: list[int] = []
            new_uc_block: dict[str, dict] = {}

            for uc, scores in per_agent_usecase_scores[a_name].items():
                times = per_agent_usecase_times[a_name][uc]

                new_uc_block[uc] = {}
                for task_id, prompt, action, t, score, gif, eval_t, cost, in_tok, out_tok, steps in zip(
                    per_agent_usecase_task_ids[a_name][uc],
                    per_agent_usecase_prompt[a_name][uc],
                    per_agent_usecase_actions[a_name][uc],
                    per_agent_usecase_times[a_name][uc],
                    per_agent_usecase_scores[a_name][uc],
                    per_agent_usecase_gifs[a_name][uc],
                    per_agent_usecase_eval_times[a_name][uc],
                    per_agent_usecase_cost[a_name][uc],
                    per_agent_usecase_input_tokens[a_name][uc],
                    per_agent_usecase_output_tokens[a_name][uc],
                    per_agent_usecase_steps_count[a_name][uc],
                    strict=False,
                ):
                    entry: dict[str, Any] = {
                        "success": score,
                        "time": round(t, 3),
                        "prompt": prompt,
                        "actions": action,
                        "base64_gif": gif,
                    }
                    if eval_t is not None:
                        entry["evaluation_time"] = round(float(eval_t), 3) if isinstance(eval_t, int | float) else eval_t
                    if cost is not None:
                        entry["cost_usd"] = round(float(cost), 6) if isinstance(cost, int | float) else cost
                    if in_tok is not None:
                        entry["input_tokens"] = int(in_tok)
                    if out_tok is not None:
                        entry["output_tokens"] = int(out_tok)
                    if steps is not None:
                        entry["steps_count"] = int(steps)
                    new_uc_block[uc][task_id] = entry

                    if cost is not None and isinstance(cost, int | float):
                        all_costs.append(float(cost))
                    if in_tok is not None:
                        all_input_tokens.append(int(in_tok))
                    if out_tok is not None:
                        all_output_tokens.append(int(out_tok))

                all_scores.extend(scores)
                all_times.extend(times)

            succ_all = sum(1 for s in all_scores if s == 1.0)
            tot_all = len(all_scores)
            avg_all_time = (sum(all_times) / len(all_times)) if all_times else 0.0
            rate_all = (succ_all / tot_all) if tot_all else 0.0
            total_cost = round(sum(all_costs), 6) if all_costs else None
            total_in_tok = sum(all_input_tokens) if all_input_tokens else None
            total_out_tok = sum(all_output_tokens) if all_output_tokens else None
            avg_cost_per_task = round(total_cost / tot_all, 6) if (total_cost is not None and tot_all) else None
            avg_input_tokens = round(sum(all_input_tokens) / len(all_input_tokens)) if all_input_tokens else None
            avg_output_tokens = round(sum(all_output_tokens) / len(all_output_tokens)) if all_output_tokens else None

            overall: dict[str, Any] = {
                "success_count": succ_all,
                "total": tot_all,
                "success_rate": round(rate_all, 3),
                "avg_solution_time": round(avg_all_time, 3),
            }
            if total_cost is not None:
                overall["total_cost_usd"] = total_cost
            if avg_cost_per_task is not None:
                overall["avg_cost_per_task_usd"] = avg_cost_per_task
            if total_in_tok is not None:
                overall["total_input_tokens"] = total_in_tok
            if total_out_tok is not None:
                overall["total_output_tokens"] = total_out_tok
            if avg_input_tokens is not None:
                overall["avg_input_tokens"] = avg_input_tokens
            if avg_output_tokens is not None:
                overall["avg_output_tokens"] = avg_output_tokens

            project_stats[a_name] = {
                "use_cases": new_uc_block,
                "overall": overall,
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

        tasks_source = "custom_json" if getattr(self.config, "tasks_json_path", None) else ("cached" if getattr(self.config, "use_cached_tasks", False) else "generated")
        logger.info(f"Tasks source: {tasks_source}" + (f", tasks_json_path={self.config.tasks_json_path}" if getattr(self.config, "tasks_json_path", None) else ""))

        projects_to_run: list[WebProject] = []
        if getattr(self.config, "tasks_json_path", None):
            from autoppia_iwa.entrypoints.benchmark.utils.task_generation import load_tasks_from_custom_json
            from autoppia_iwa.src.demo_webs.config import demo_web_projects

            projects_by_id = {p.id: p for p in self.config.projects} if self.config.projects else {p.id: p for p in demo_web_projects}
            if not projects_by_id:
                raise RuntimeError("No projects available to resolve project_id from tasks file. Configure PROJECT_IDS or add demo_web_projects.")
            try:
                custom_project, custom_tasks = load_tasks_from_custom_json(self.config.tasks_json_path, projects_by_id)
                self._custom_tasks_cache = (custom_project, custom_tasks)
                projects_to_run = [custom_project]
            except (FileNotFoundError, ValueError, OSError) as e:
                logger.exception("Failed to load tasks from custom JSON")
                raise RuntimeError(f"Failed to load tasks from {self.config.tasks_json_path}: {e}") from e
        else:
            self._custom_tasks_cache = None
            projects_to_run = list(self.config.projects)

        total_projects = len(projects_to_run)
        successful_projects = 0

        try:
            for project_index, project in enumerate(projects_to_run, 1):
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
        saved_path: Path | None = None
        if self.config.save_results_json and self.per_project_results:
            try:
                saved_path = self._save_consolidated_results()
            except Exception as e:
                logger.error(f"Failed to save consolidated results: {e}")

        # Metrics report (default behaviour); do not fail run if report raises
        if saved_path and saved_path.exists():
            try:
                from autoppia_iwa.entrypoints.benchmark.utils.metrics_report import run_report

                run_report(results_path=saved_path, write_summary_file=True)
            except Exception as e:
                logger.warning(f"Metrics report failed (results already saved): {e}")

        logger.success(f"Benchmark finished ✔ - {successful_projects}/{total_projects} projects completed successfully")

        return self.per_project_results
