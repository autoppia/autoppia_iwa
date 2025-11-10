# concurrent_evaluator.py
import asyncio
import contextlib
import time
from collections import defaultdict

from loguru import logger

EVALUATION_LEVEL_NAME = "EVALUATION"
EVALUATION_LEVEL_NO = 25


def _ensure_evaluation_level() -> None:
    """Register the EVALUATION level if it is missing."""
    try:
        logger.level(EVALUATION_LEVEL_NAME)
    except ValueError:
        logger.level(EVALUATION_LEVEL_NAME, EVALUATION_LEVEL_NO)


def _log_evaluation_fallback(message: str) -> None:
    """Fallback logger that emits messages at INFO level with EVALUATION tag."""
    logger.info(f"[EVALUATION] {message}")


def _log_action_execution(message: str, web_agent_id: str | None = None):
    """Helper function to log action execution with EVALUATION level"""
    agent_prefix = f"[agent={web_agent_id}] " if web_agent_id else ""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_action_execution

        log_action_execution(f"{agent_prefix}{message}")
    except ImportError:
        _log_evaluation_fallback(f"[ACTION EXECUTION] {agent_prefix}{message}")


def _log_gif_creation(message: str, web_agent_id: str | None = None):
    """Helper function to log GIF creation with EVALUATION level"""
    agent_prefix = f"[agent={web_agent_id}] " if web_agent_id else ""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_gif_creation

        log_gif_creation(f"{agent_prefix}{message}")
    except ImportError:
        _log_evaluation_fallback(f"[GIF CREATION] {agent_prefix}{message}")


def _log_evaluation_event(message: str, context: str = "GENERAL"):
    """Helper function to log generic evaluation events with EVALUATION level."""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_evaluation_event

        log_evaluation_event(message, context=context)
    except ImportError:
        _log_evaluation_fallback(message if context == "GENERAL" else f"[{context}] {message}")


from playwright.async_api import async_playwright

from autoppia_iwa.config.config import EVALUATOR_HEADLESS, VALIDATOR_ID
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.utils import (
    display_single_evaluation_summary,
    extract_seed_from_url,
    generate_feedback,
    hash_actions,
    initialize_test_results,
    log_progress,
    make_gif_from_screenshots,
    run_global_tests,
)
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.dynamic import DynamicPlaywrightExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.di_container import DIContainer


class ConcurrentEvaluator(IEvaluator):
    def __init__(self, web_project: WebProject, config: EvaluatorConfig):
        self.config = config
        self._random_clicker_cache: dict[str, tuple[list[int], float]] = {}
        self.total_evaluation_time = 0.0
        self.evaluation_count = 0
        self.web_project = web_project
        self.backend_demo_webs_service = BackendDemoWebService(web_project=web_project)

        # Statistics collection
        self.evaluation_stats: list[EvaluationStats] = []
        self.action_type_timing = defaultdict(list)
        self.errors: list[str] = []

        # Configure logs minimally if not verbose
        if not self.config.verbose_logging:
            logger.remove()
            logger.add(
                lambda msg: print(msg, end=""),
                level="WARNING" if self.config.debug_mode else "INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            )

    async def evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Evaluate a single task solution (actions + agent) for a given task.
        """
        try:
            _log_evaluation_event(f"Evaluating single task solution for task {task.id}...")

            _log_evaluation_event("Resetting Project Environment & Database.", context="RESETTING DATABASE")
            await self.backend_demo_webs_service.reset_database(web_agent_id=task_solution.web_agent_id)

            result = await self._evaluate_single_task_solution(task, task_solution)

            # Display final report for this single solution
            if result.stats:
                display_single_evaluation_summary(result.stats, debug_mode=self.config.debug_mode)
                self.evaluation_stats.append(result.stats)

            return result
        finally:
            if self.backend_demo_webs_service:
                await self.backend_demo_webs_service.close()

    async def evaluate_task_solutions(self, task: Task, task_solutions: list[TaskSolution]) -> list[EvaluationResult]:
        """
        Evaluate multiple solutions for the same task, optionally grouping identical ones.
        """
        try:
            _log_evaluation_event(f"Evaluating {len(task_solutions)} solutions for task {task.id}...")

            _log_evaluation_event("Resetting Project Environment & Database.", context="RESETTING DATABASE")
            web_agent_ids = {sol.web_agent_id for sol in task_solutions if sol.web_agent_id}
            for web_agent_id in web_agent_ids:
                await self.backend_demo_webs_service.reset_database(web_agent_id=web_agent_id)

            results = await self._group_and_evaluate_task_solutions(task, task_solutions)

            # Save stats
            for r in results:
                if r and r.stats:
                    self.evaluation_stats.append(r.stats)

            return results
        finally:
            if self.backend_demo_webs_service:
                await self.backend_demo_webs_service.close()

    async def _evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Internal logic to evaluate a single TaskSolution.
        """

        actions = task_solution.actions
        web_agent_id = task_solution.web_agent_id
        is_web_real = task.is_web_real

        stats = EvaluationStats(
            web_agent_id=web_agent_id,
            task_id=task.id,
            action_count=len(actions),
            start_time=time.time(),
        )

        # Count action types
        for action in actions:
            stats.action_types[action.type] = stats.action_types.get(action.type, 0) + 1

        # If no actions, return an immediate error
        if not actions:
            stats.had_errors = True
            stats.error_message = "No actions provided"
            stats.total_time = time.time() - stats.start_time
            test_results = initialize_test_results(task)
            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                test_results=test_results,
                feedback=None,
                execution_history=[],
                evaluation_time=0.1,
                stats=stats,
                gif_recording="",
            )

        # Validate NavigateAction seed usage against assigned seed in task.url
        try:
            assigned_seed = extract_seed_from_url(task.url)
        except Exception:
            assigned_seed = None

        if assigned_seed is not None:
            has_navigate = any(isinstance(a, NavigateAction) for a in actions)
            if has_navigate:
                violation = False
                for a in actions:
                    if isinstance(a, NavigateAction) and getattr(a, "url", None):
                        nav_seed = extract_seed_from_url(a.url)  # type: ignore[arg-type]
                        if nav_seed is None or nav_seed != assigned_seed:
                            violation = True
                            break
                if violation:
                    stats.total_time = time.time() - stats.start_time
                    stats.had_errors = False
                    stats.error_message = "Seed missing or mismatched in NavigateAction URL(s)."

                    # Log seed mismatch early return
                    _log_evaluation_event(f"SEED MISMATCH - Skipping browser execution (expected seed={assigned_seed})", context=f"ACTION EXECUTION | agent={web_agent_id}")

                    test_results = initialize_test_results(task)
                    return EvaluationResult(
                        web_agent_id=web_agent_id,
                        final_score=0,
                        raw_score=0,
                        test_results=test_results,
                        feedback=None,
                        execution_history=[],
                        evaluation_time=stats.total_time,
                        stats=stats,
                        gif_recording="",
                    )

        _log_evaluation_event("Executing actions in browser", context=f"ACTION EXECUTION | agent={web_agent_id}")
        evaluation_gif = ""
        try:
            # If simulated, reset the DB first
            browser_setup_start = time.time()

            # Start browser usage
            browser_execution_start = time.time()
            stats.browser_setup_time = browser_execution_start - browser_setup_start

            execution_history, action_execution_times = await self._evaluate_in_browser(task, web_agent_id, actions, is_web_real)

            if self.config.should_record_gif:
                _log_gif_creation("🎬 GIF ENABLED", web_agent_id=web_agent_id)
                all_screenshots = []
                if execution_history:
                    all_screenshots.append(execution_history[0].browser_snapshot.screenshot_before)

                    for h in execution_history:
                        all_screenshots.append(h.browser_snapshot.screenshot_after)

                if all_screenshots:
                    evaluation_gif = make_gif_from_screenshots(all_screenshots)
                    if evaluation_gif:
                        _log_gif_creation("✅ GIF CREATION SUCCESS", web_agent_id=web_agent_id)
                    else:
                        _log_gif_creation("❌ GIF CREATION ERROR", web_agent_id=web_agent_id)
                        evaluation_gif = None
                else:
                    _log_gif_creation("❌ GIF CREATION ERROR", web_agent_id=web_agent_id)
                    evaluation_gif = None
            else:
                _log_evaluation_event("📷 GIF Recording disabled (should_record_gif=False)", context="GIF")

            stats.action_execution_times = action_execution_times

            # Run tests
            test_start_time = time.time()
            backend_events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)

            # 🔍 DEBUG: Log backend events (simplified)
            if self.config.debug_mode:
                logger.debug("🔍 DEBUG - Backend Events Retrieved:")
                logger.debug(f"   - Number of events: {len(backend_events) if backend_events else 0}")
                if backend_events:
                    for idx, event in enumerate(backend_events, 1):
                        logger.debug(f"   - Event {idx}: {event.event_name if hasattr(event, 'event_name') else 'unknown'}")

            test_results = await run_global_tests(task, backend_events=backend_events, web_agent_id=web_agent_id)

            # 🔍 DEBUG: Log test results (simplified)
            if self.config.debug_mode:
                logger.debug("🔍 DEBUG - Test Results:")
                logger.debug(f"   - Number of tests: {len(test_results) if test_results else 0}")
                logger.debug(f"   - Test results: {test_results}")

            stats.test_execution_time = time.time() - test_start_time

            # Calculate raw score (# tests passed / total tests)
            raw_score = 0.0
            tests_passed_count = 0
            num_tests = 0

            # 🔍 DEBUG: Log test calculation details (simplified)
            if self.config.debug_mode:
                logger.debug("🔍 DEBUG - Calculating Raw Score:")
                logger.debug(f"   - test_results exists: {test_results is not None}")
                logger.debug(f"   - test_results length: {len(test_results) if test_results else 0}")

            if test_results:
                num_tests = len(test_results)
                stats.total_tests = num_tests

                if self.config.debug_mode:
                    logger.debug(f"   - Number of tests: {num_tests}")

                for test_index, test_result in enumerate(test_results):
                    if self.config.debug_mode:
                        logger.debug(f"   - Test {test_index + 1}: {'✅ PASSED' if test_result.success else '❌ FAILED'}")
                    if test_result.success:
                        tests_passed_count += 1

                if num_tests > 0:
                    raw_score = tests_passed_count / num_tests
                    if self.config.debug_mode:
                        logger.debug(f"   - Tests passed: {tests_passed_count}/{num_tests}")
                        logger.debug(f"   - Raw score: {raw_score:.4f}")
            else:
                if self.config.debug_mode:
                    logger.warning("   ⚠️  No tests to evaluate (empty test results)")

            stats.tests_passed = tests_passed_count
            stats.raw_score = raw_score

            # Adjust final score relative to random clicker
            final_score = raw_score

            stats.final_score = final_score
            stats.total_time = time.time() - stats.start_time

            # Generate feedback
            feedback = generate_feedback(task, execution_history, test_results)

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=final_score,  # Use actual score, don't artificially boost to 1.0
                raw_score=raw_score,
                test_results=test_results,
                feedback=feedback,
                execution_history=execution_history,
                evaluation_time=stats.total_time,
                stats=stats,
                gif_recording=evaluation_gif,
            )

        except Exception as e:
            stats.had_errors = True
            stats.error_message = str(e)
            stats.total_time = time.time() - stats.start_time

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                test_results=initialize_test_results(task),
                feedback=None,
                execution_history=[],
                evaluation_time=0,
                stats=stats,
                gif_recording=evaluation_gif,
            )

    async def _group_and_evaluate_task_solutions(self, task: Task, task_solutions: list[TaskSolution]) -> list[EvaluationResult]:
        """
        Groups identical solutions by hashing their actions, evaluates them, and clones results.
        """
        start_time = time.time()
        # We create a final array of results aligned with the original list
        final_results: list[EvaluationResult | None] = [None] * len(task_solutions)

        # Group according to HASH of actions
        grouped_indices = defaultdict(list)
        if self.config.enable_grouping_tasks:
            for idx, solution in enumerate(task_solutions):
                hash_key = hash_actions(solution.actions)
                grouped_indices[hash_key].append(idx)
            if self.config.verbose_logging:
                _log_evaluation_event(f"Grouped {len(task_solutions)} solutions into {len(grouped_indices)} groups", context="GROUPING")
        else:
            for idx, solution in enumerate(task_solutions):
                unique_hash = hash_actions(solution.actions) + f"_{idx}"
                grouped_indices[unique_hash].append(idx)

        for key, g_indices in grouped_indices.items():
            _log_evaluation_event(
                f"Group key={key}, indices={g_indices}, web_agent_ids={[task_solutions[i].web_agent_id for i in g_indices]}",
                context="GROUPING TASK SOLUTIONS",
            )

        # Shuffle grouped tasks for random evaluation order
        grouped_task_list = list(grouped_indices.values())
        # random.shuffle(grouped_task_list)

        semaphore = asyncio.Semaphore(self.config.chunk_size)
        tasks = [self._evaluate_group_with_semaphore(task, task_solutions, group_indices, final_results, semaphore) for group_indices in grouped_task_list]

        # If large, log minimal progress in background
        progress_tracker = asyncio.create_task(log_progress(len(tasks), interval=10)) if len(tasks) > 5 and self.config.verbose_logging else None

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Cancel progress tracker if used
        if progress_tracker:
            progress_tracker.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await progress_tracker

        for item in raw_results:
            if isinstance(item, Exception):
                self.errors.append(str(item))
                if self.config.verbose_logging:
                    logger.error(f"Evaluation error: {item}")

        elapsed = time.time() - start_time
        self.total_evaluation_time += elapsed

        return final_results

    async def _evaluate_group_with_semaphore(
        self,
        task: Task,
        task_solutions: list[TaskSolution],
        group_indices: list[int],
        final_results: list[EvaluationResult | None],
        semaphore: asyncio.Semaphore,
    ) -> None:
        """
        Evaluates a group of identical solutions (all share the same actions).
        """
        async with semaphore:
            rep_index = group_indices[0]
            representative = task_solutions[rep_index]

            # Log which group is being evaluated
            web_agent_ids = [task_solutions[i].web_agent_id for i in group_indices]
            if len(group_indices) > 1:
                _log_evaluation_event(
                    f"Evaluating group (identical actions) - representative={representative.web_agent_id}, cloning for {len(group_indices) - 1} others: {web_agent_ids[1:]}", context="GROUPING TASK"
                )
            else:
                _log_evaluation_event(f"Evaluating unique solution - web_agent_id={representative.web_agent_id}", context="GROUPING TASK")

            try:
                rep_result = await self._evaluate_single_task_solution(task, representative)

                # For each index in the group, we clone the rep_result
                for idx in group_indices:
                    sol = task_solutions[idx]
                    cloned = rep_result.model_copy(deep=True)
                    cloned.web_agent_id = sol.web_agent_id
                    if cloned.stats:
                        stats_copy = cloned.stats.model_copy(deep=True)
                        stats_copy.web_agent_id = sol.web_agent_id
                        cloned.stats = stats_copy

                    final_results[idx] = cloned

                # logger.info(f"Group evaluation complete for representative web_agent_id: {representative.web_agent_id}")
            except Exception as e:
                logger.error(f"Error evaluating group actions: {e}")
                self.errors.append(str(e))
                # Return error in final_results for each solution
                for idx in group_indices:
                    sol = task_solutions[idx]
                    error_stats = EvaluationStats(
                        web_agent_id=sol.web_agent_id,
                        task_id=task.id,
                        action_count=len(sol.actions),
                        start_time=time.time(),
                        had_errors=True,
                        error_message=str(e),
                    )
                    error_result = EvaluationResult(
                        web_agent_id=sol.web_agent_id,
                        final_score=0,
                        raw_score=0,
                        test_results=initialize_test_results(task),
                        feedback=None,
                        execution_history=[],
                        evaluation_time=0,
                        stats=error_stats,
                        gif_recording="",
                    )
                    final_results[idx] = error_result

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: list[BaseAction], is_web_real: bool) -> tuple[list[ActionExecutionResult], list[float]]:
        """
        Executes all actions in a Playwright browser context and returns the results + times.
        """
        action_execution_times: list[float] = []
        action_results: list[ActionExecutionResult] = []

        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                browser_specifications = task.specifications or BrowserSpecification()
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS, args=[f"--window-size={browser_specifications.screen_width},{browser_specifications.screen_height}"])
                # browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS, slow_mo=2000)
                context = await browser.new_context(
                    extra_http_headers={"X-WebAgent-Id": web_agent_id, "X-Validator-Id": VALIDATOR_ID},
                    no_viewport=True,
                )
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()

                dynamic_config = self.config.dynamic_phase_config
                dynamic_enabled = dynamic_config.any_enabled() if dynamic_config else False
                if dynamic_enabled:
                    try:
                        seed_value = extract_seed_from_url(task.url)
                    except Exception:
                        seed_value = None
                    browser_executor = DynamicPlaywrightExecutor(
                        browser_specifications,
                        page,
                        self.backend_demo_webs_service,
                        dynamic_config=dynamic_config,
                        project_id=self.web_project.id,
                        seed=seed_value,
                    )
                else:
                    browser_executor = PlaywrightBrowserExecutor(browser_specifications, page, self.backend_demo_webs_service)

                _log_action_execution(f"🎬 Starting execution of {len(actions)} actions", web_agent_id=web_agent_id)

                for i, action in enumerate(actions):
                    start_time_action = time.time()
                    try:
                        result = await browser_executor.execute_single_action(action, web_agent_id, iteration=i, is_web_real=is_web_real, should_record=self.config.should_record_gif)
                        action_results.append(result)
                        elapsed = time.time() - start_time_action
                        action_execution_times.append(elapsed)

                        # Log only errors when actions fail
                        if result and not result.successfully_executed:
                            _log_action_execution(f"❌ Action {i + 1} FAILED in {elapsed:.2f}s - Error: {getattr(result, 'error', 'unknown')}", web_agent_id=web_agent_id)

                        self.action_type_timing[action.type].append(elapsed)

                        # Optional pause between actions
                        if i < len(actions) - 1 and self.config.task_delay_in_seconds > 0:
                            await asyncio.sleep(self.config.task_delay_in_seconds)

                    except Exception as e:
                        _log_action_execution(f"❌ Action {i + 1}/{len(actions)} EXCEPTION: {e}", web_agent_id=web_agent_id)
                        elapsed = time.time() - start_time_action
                        action_execution_times.append(elapsed)

                        break

                _log_action_execution(f"🏁 Finished executing {len(action_results)}/{len(actions)} actions", web_agent_id=web_agent_id)

                return action_results, action_execution_times

            except Exception as e:
                logger.error(f"Browser evaluation error: {e}")
                return [], []
            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()
