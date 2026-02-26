# concurrent_evaluator.py
import asyncio
import contextlib
import os
import time
from collections import defaultdict
from urllib.parse import urlparse

try:
    from autoppia_web_agents_subnet.validator.config import TESTING as SUBNET_TESTING
except Exception:
    SUBNET_TESTING = False

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.config.config import EVALUATOR_HEADLESS, VALIDATOR_ID
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, EvaluatorConfig
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.evaluation.shared.utils import (
    display_single_evaluation_summary,
    extract_seed_from_url,
    generate_feedback,
    hash_actions,
    initialize_test_results,
    log_progress,
    make_gif_from_screenshots,
    run_global_tests,
)
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.execution.dynamic import DynamicPlaywrightExecutor
from autoppia_iwa.src.web_agents.classes import TaskSolution

EVALUATION_LEVEL_NAME = "EVALUATION"
EVALUATION_LEVEL_NO = 25


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def _is_testing_mode() -> bool:
    return bool(SUBNET_TESTING)


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


# ============================================================================
# URL VALIDATION HELPERS
# ============================================================================


def _url_hostname(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    return parsed.hostname.lower() if parsed.hostname else None


def _is_navigation_url_allowed(*, is_web_real: bool, task_url: str | None, candidate_url: str | None) -> tuple[bool, str | None]:
    # Relative/invalid URLs (no host) are allowed to preserve compatibility with
    # action payloads that may use local-only or in-page navigation semantics.
    if not candidate_url:
        return True, None

    parsed = urlparse(candidate_url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return False, f"NavigateAction scheme '{parsed.scheme}' is not allowed"

    target_host = parsed.hostname.lower() if parsed.hostname else None
    if target_host is None:
        return True, None

    if not is_web_real:
        if _is_testing_mode():
            return True, None
        if target_host in {"localhost", "127.0.0.1", "::1"}:
            return True, None
        return False, f"NavigateAction host '{target_host}' is not allowed for demo webs"

    allowed_host = _url_hostname(task_url)
    if allowed_host is None:
        return False, "Task URL host could not be determined"
    if target_host != allowed_host:
        return False, f"NavigateAction to host '{target_host}' not allowed for task host '{allowed_host}'"
    return True, None


# ============================================================================
# EVALUATION RESULT BUILDERS
# ============================================================================


def _create_error_evaluation_result(web_agent_id: str, stats: EvaluationStats, test_results: list, evaluation_time: float = 0.0, gif_recording: str = "") -> EvaluationResult:
    """Create an error evaluation result."""
    return EvaluationResult(
        web_agent_id=web_agent_id,
        final_score=0,
        raw_score=0,
        test_results=test_results,
        feedback=None,
        execution_history=[],
        evaluation_time=evaluation_time,
        stats=stats,
        gif_recording=gif_recording,
    )


def _create_no_actions_result(web_agent_id: str, stats: EvaluationStats, task: Task) -> EvaluationResult:
    """Create evaluation result for no actions case."""
    stats.had_errors = True
    stats.error_message = "No actions provided"
    stats.total_time = time.time() - stats.start_time
    test_results = initialize_test_results(task)
    return _create_error_evaluation_result(web_agent_id, stats, test_results, evaluation_time=0.1)


# ============================================================================
# NAVIGATION VALIDATION HELPERS
# ============================================================================


def _validate_navigation_actions(actions: list, task: Task, stats: EvaluationStats, web_agent_id: str) -> tuple[bool, EvaluationResult | None]:
    """Validate NavigateAction URLs and return (is_valid, error_result)."""
    try:
        assigned_seed = extract_seed_from_url(task.url)
    except Exception:
        assigned_seed = None

    for action in actions:
        if not isinstance(action, NavigateAction):
            continue
        target_url = action.url
        if not target_url:
            continue

        is_allowed, reason = _is_navigation_url_allowed(
            is_web_real=bool(getattr(task, "is_web_real", False)),
            task_url=task.url,
            candidate_url=target_url,
        )
        if not is_allowed:
            stats.total_time = time.time() - stats.start_time
            stats.had_errors = False
            stats.error_message = "NavigateAction target violates task domain constraints."
            _log_evaluation_event(
                f"NAVIGATE BLOCKED - {reason} | Skipping browser execution (expected host={_url_hostname(task.url)}, got={_url_hostname(target_url)})",
                context=f"ACTION EXECUTION | agent={web_agent_id}",
            )
            test_results = initialize_test_results(task)
            return False, _create_error_evaluation_result(web_agent_id, stats, test_results, evaluation_time=stats.total_time)

        if assigned_seed is not None:
            nav_seed = extract_seed_from_url(target_url)
            if nav_seed is None or nav_seed != assigned_seed:
                stats.total_time = time.time() - stats.start_time
                stats.had_errors = False
                stats.error_message = "Seed missing or mismatched in NavigateAction URL(s)."
                _log_evaluation_event(
                    f"SEED MISMATCH - Skipping browser execution (expected seed={assigned_seed}, received={nav_seed})",
                    context=f"ACTION EXECUTION | agent={web_agent_id}",
                )
                test_results = initialize_test_results(task)
                return False, _create_error_evaluation_result(web_agent_id, stats, test_results, evaluation_time=stats.total_time)

    return True, None


# ============================================================================
# GIF CREATION HELPERS
# ============================================================================


def _create_evaluation_gif(execution_history: list, web_agent_id: str) -> str | None:
    """Create GIF from execution history screenshots."""
    all_screenshots = []
    if execution_history:
        all_screenshots.append(execution_history[0].browser_snapshot.screenshot_before)
        for h in execution_history:
            all_screenshots.append(h.browser_snapshot.screenshot_after)

    if not all_screenshots:
        _log_gif_creation("❌ GIF CREATION ERROR", web_agent_id=web_agent_id)
        return None

    evaluation_gif = make_gif_from_screenshots(all_screenshots)
    if evaluation_gif:
        _log_gif_creation("✅ GIF CREATION SUCCESS", web_agent_id=web_agent_id)
    else:
        _log_gif_creation("❌ GIF CREATION ERROR", web_agent_id=web_agent_id)
    return evaluation_gif


# ============================================================================
# SCORE CALCULATION HELPERS
# ============================================================================


def _count_passed_tests(test_results: list, debug_mode: bool) -> int:
    """Count number of passed tests."""
    tests_passed_count = 0
    for test_index, test_result in enumerate(test_results):
        if debug_mode:
            logger.debug(f"   - Test {test_index + 1}: {'✅ PASSED' if test_result.success else '❌ FAILED'}")
        if test_result.success:
            tests_passed_count += 1
    return tests_passed_count


def _calculate_raw_score(test_results: list, stats: EvaluationStats, debug_mode: bool) -> float:
    """Calculate raw score from test results."""
    if not test_results:
        if debug_mode:
            logger.warning("   ⚠️  No tests to evaluate (empty test results)")
        return 0.0

    num_tests = len(test_results)
    stats.total_tests = num_tests

    if debug_mode:
        logger.debug(f"   - Number of tests: {num_tests}")

    tests_passed_count = _count_passed_tests(test_results, debug_mode)
    stats.tests_passed = tests_passed_count

    if num_tests > 0:
        raw_score = 1.0 if tests_passed_count > 0 else 0.0
        if debug_mode:
            logger.debug(f"   - Tests passed: {tests_passed_count}/{num_tests}")
            logger.debug(f"   - Raw score (binary): {raw_score:.4f} (at least one test passed: {tests_passed_count > 0})")
        return raw_score

    return 0.0


def _log_debug_backend_events(backend_events: list, debug_mode: bool) -> None:
    """Log backend events in debug mode."""
    if not debug_mode:
        return
    logger.debug("🔍 DEBUG - Backend Events Retrieved:")
    logger.debug(f"   - Number of events: {len(backend_events) if backend_events else 0}")
    if backend_events:
        for idx, event in enumerate(backend_events, 1):
            logger.debug(f"   - Event {idx}: {event.event_name if hasattr(event, 'event_name') else 'unknown'}")


def _log_debug_test_results(test_results: list, debug_mode: bool) -> None:
    """Log test results in debug mode."""
    if not debug_mode:
        return
    logger.debug("🔍 DEBUG - Test Results:")
    logger.debug(f"   - Number of tests: {len(test_results) if test_results else 0}")
    logger.debug(f"   - Test results: {test_results}")


def _log_debug_score_calculation(test_results: list | None, debug_mode: bool) -> None:
    """Log score calculation details in debug mode."""
    if not debug_mode:
        return
    logger.debug("🔍 DEBUG - Calculating Raw Score:")
    logger.debug(f"   - test_results exists: {test_results is not None}")
    logger.debug(f"   - test_results length: {len(test_results) if test_results else 0}")


# ============================================================================
# GROUPING HELPERS
# ============================================================================


def _group_solutions_by_hash(task_solutions: list[TaskSolution], enable_grouping: bool) -> dict[str, list[int]]:
    """Group solutions by action hash."""
    grouped_indices = defaultdict(list)
    if enable_grouping:
        for idx, solution in enumerate(task_solutions):
            hash_key = hash_actions(solution.actions)
            grouped_indices[hash_key].append(idx)
    else:
        for idx, solution in enumerate(task_solutions):
            unique_hash = hash_actions(solution.actions) + f"_{idx}"
            grouped_indices[unique_hash].append(idx)
    return grouped_indices


def _create_error_result_for_group(task: Task, sol: TaskSolution, error: Exception) -> EvaluationResult:
    """Create error evaluation result for a solution in a group."""
    error_stats = EvaluationStats(
        web_agent_id=sol.web_agent_id or "unknown_agent",
        task_id=task.id,
        action_count=len(sol.actions),
        start_time=time.time(),
        had_errors=True,
        error_message=str(error),
    )
    return _create_error_evaluation_result(
        sol.web_agent_id or "unknown_agent",
        error_stats,
        initialize_test_results(task),
        evaluation_time=0,
    )


# ============================================================================
# BROWSER EXECUTION HELPERS
# ============================================================================


def _setup_network_debugging(page, debug_network: bool) -> dict[str, list[str]]:
    """Setup network debugging handlers if enabled."""
    network_log: dict[str, list[str]] = {"requests": [], "responses": []}
    if not debug_network:
        return network_log

    def _on_request(req):
        url = req.url
        if "log-event" in url or ":8090" in url:
            entry = f"{req.method} {url}"
            network_log["requests"].append(entry)

    def _on_response(res):
        url = res.url
        if "log-event" in url or ":8090" in url:
            entry = f"{res.status} {url}"
            network_log["responses"].append(entry)

    page.on("request", _on_request)
    page.on("response", _on_response)
    return network_log


def _create_browser_executor(
    task: Task,
    page,
    backend_service: BackendDemoWebService,
    dynamic_config,
    web_project: WebProject,
) -> PlaywrightBrowserExecutor | DynamicPlaywrightExecutor:
    """Create appropriate browser executor based on configuration."""
    browser_specifications = task.specifications or BrowserSpecification()
    dynamic_enabled = dynamic_config.any_enabled() if dynamic_config else False

    if dynamic_enabled:
        try:
            seed_value = extract_seed_from_url(task.url)
        except Exception:
            seed_value = None
        return DynamicPlaywrightExecutor(
            browser_specifications,
            page,
            backend_service,
            dynamic_config=dynamic_config,
            project_id=web_project.id,
            seed=seed_value,
        )
    return PlaywrightBrowserExecutor(browser_specifications, page, backend_service)


def _handle_action_failure(
    consecutive_failures: int,
    max_consecutive_failures: int,
    action_index: int,
    elapsed: float,
    result: ActionExecutionResult,
    web_agent_id: str,
) -> tuple[int, str | None]:
    """Handle action failure and check for early stop condition."""
    consecutive_failures += 1
    _log_action_execution(
        f"❌ Action {action_index + 1} FAILED in {elapsed:.2f}s - Error: {getattr(result, 'error', 'unknown')} (Consecutive failures: {consecutive_failures}/{max_consecutive_failures})",
        web_agent_id=web_agent_id,
    )

    if consecutive_failures >= max_consecutive_failures:
        early_stop_reason = f"Task marked as failed after {consecutive_failures} consecutive action failures (limit: {max_consecutive_failures})"
        _log_action_execution(f"🛑 Stopping execution: {early_stop_reason}", web_agent_id=web_agent_id)
        return consecutive_failures, early_stop_reason

    return consecutive_failures, None


def _handle_action_exception(
    consecutive_failures: int,
    max_consecutive_failures: int,
    action_index: int,
    total_actions: int,
    error: Exception,
    web_agent_id: str,
) -> tuple[int, str | None]:
    """Handle exception during action execution."""
    consecutive_failures += 1
    _log_action_execution(
        f"❌ Action {action_index + 1}/{total_actions} EXCEPTION: {error} (Consecutive failures: {consecutive_failures}/{max_consecutive_failures})",
        web_agent_id=web_agent_id,
    )

    if consecutive_failures >= max_consecutive_failures:
        early_stop_reason = f"Task marked as failed after {consecutive_failures} consecutive action failures (limit: {max_consecutive_failures})"
        _log_action_execution(f"🛑 Stopping execution: {early_stop_reason}", web_agent_id=web_agent_id)
        return consecutive_failures, early_stop_reason

    return consecutive_failures, None


async def _execute_single_action(
    browser_executor: PlaywrightBrowserExecutor | DynamicPlaywrightExecutor,
    action: BaseAction,
    action_index: int,
    total_actions: int,
    web_agent_id: str,
    is_web_real: bool,
    should_record: bool,
    max_consecutive_failures: int,
    consecutive_failures: int,
    action_type_timing: dict,
) -> tuple[ActionExecutionResult | None, float, int, str | None]:
    """Execute a single action and return result, elapsed time, updated consecutive failures, and stop reason."""
    start_time_action = time.time()
    try:
        result = await browser_executor.execute_single_action(action, web_agent_id, iteration=action_index, is_web_real=is_web_real, should_record=should_record)
        elapsed = time.time() - start_time_action

        if result and not result.successfully_executed:
            consecutive_failures, stop_reason = _handle_action_failure(consecutive_failures, max_consecutive_failures, action_index, elapsed, result, web_agent_id)
            if stop_reason:
                return result, elapsed, consecutive_failures, stop_reason
        else:
            consecutive_failures = 0

        action_type_timing[action.type].append(elapsed)
        return result, elapsed, consecutive_failures, None

    except Exception as e:
        elapsed = time.time() - start_time_action
        consecutive_failures, stop_reason = _handle_action_exception(consecutive_failures, max_consecutive_failures, action_index, total_actions, e, web_agent_id)
        return None, elapsed, consecutive_failures, stop_reason


async def _execute_action_loop(
    browser_executor: PlaywrightBrowserExecutor | DynamicPlaywrightExecutor,
    actions: list[BaseAction],
    web_agent_id: str,
    is_web_real: bool,
    should_record: bool,
    task_delay: float,
    max_consecutive_failures: int,
    action_type_timing: dict,
) -> tuple[list[ActionExecutionResult], list[float], str | None]:
    """Execute all actions in a loop and track failures."""
    action_execution_times: list[float] = []
    action_results: list[ActionExecutionResult] = []
    consecutive_failures = 0
    early_stop_reason: str | None = None

    _log_action_execution(f"🎬 Starting execution of {len(actions)} actions", web_agent_id=web_agent_id)

    for i, action in enumerate(actions):
        result, elapsed, consecutive_failures, stop_reason = await _execute_single_action(
            browser_executor, action, i, len(actions), web_agent_id, is_web_real, should_record, max_consecutive_failures, consecutive_failures, action_type_timing
        )

        if result:
            action_results.append(result)
        action_execution_times.append(elapsed)

        if stop_reason:
            early_stop_reason = stop_reason
            break

        if i < len(actions) - 1 and task_delay > 0:
            await asyncio.sleep(task_delay)

    if early_stop_reason:
        _log_action_execution(f"🏁 Finished executing {len(action_results)}/{len(actions)} actions (stopped early due to consecutive failures)", web_agent_id=web_agent_id)
    else:
        _log_action_execution(f"🏁 Finished executing {len(action_results)}/{len(actions)} actions", web_agent_id=web_agent_id)

    return action_results, action_execution_times, early_stop_reason


# ============================================================================
# CONCURRENT EVALUATOR CLASS
# ============================================================================


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
        web_agent_id = task_solution.web_agent_id or "unknown_agent"
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
            return _create_no_actions_result(web_agent_id, stats, task)

        # Validate NavigateAction target host and seed usage against task.url
        is_valid, error_result = _validate_navigation_actions(actions, task, stats, web_agent_id)
        if not is_valid:
            return error_result

        _log_evaluation_event("Executing actions in browser", context=f"ACTION EXECUTION | agent={web_agent_id}")
        evaluation_gif = ""
        try:
            browser_setup_start = time.time()
            browser_execution_start = time.time()
            stats.browser_setup_time = browser_execution_start - browser_setup_start

            execution_history, action_execution_times, early_stop_reason = await self._evaluate_in_browser(task, web_agent_id, actions, is_web_real)

            task_failed_due_to_consecutive_failures = False
            if early_stop_reason:
                stats.had_errors = True
                stats.error_message = early_stop_reason
                task_failed_due_to_consecutive_failures = True
                _log_evaluation_event(f"Task marked as FAILED: {early_stop_reason}", context=f"ACTION EXECUTION | agent={web_agent_id}")

            if self.config.should_record_gif:
                _log_gif_creation("🎬 GIF ENABLED", web_agent_id=web_agent_id)
                evaluation_gif = _create_evaluation_gif(execution_history, web_agent_id)
            else:
                _log_evaluation_event("📷 GIF Recording disabled (should_record_gif=False)", context="GIF")

            stats.action_execution_times = action_execution_times

            test_start_time = time.time()
            backend_events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)
            _log_debug_backend_events(backend_events, self.config.debug_mode)

            test_results = await run_global_tests(task, backend_events=backend_events, web_agent_id=web_agent_id)
            _log_debug_test_results(test_results, self.config.debug_mode)

            stats.test_execution_time = time.time() - test_start_time

            _log_debug_score_calculation(test_results, self.config.debug_mode)
            raw_score = _calculate_raw_score(test_results, stats, self.config.debug_mode)
            stats.raw_score = raw_score

            if task_failed_due_to_consecutive_failures:
                final_score = 0.0
                stats.raw_score = 0.0
            else:
                final_score = raw_score

            stats.final_score = final_score
            stats.total_time = time.time() - stats.start_time

            feedback = generate_feedback(task, execution_history, test_results)

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=final_score,
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
            test_results = initialize_test_results(task)
            return _create_error_evaluation_result(web_agent_id, stats, test_results, evaluation_time=0, gif_recording=evaluation_gif)

    async def _group_and_evaluate_task_solutions(self, task: Task, task_solutions: list[TaskSolution]) -> list[EvaluationResult]:
        """
        Groups identical solutions by hashing their actions, evaluates them, and clones results.
        """
        start_time = time.time()
        final_results: list[EvaluationResult | None] = [None] * len(task_solutions)

        grouped_indices = _group_solutions_by_hash(task_solutions, self.config.enable_grouping_tasks)
        if self.config.verbose_logging and self.config.enable_grouping_tasks:
            _log_evaluation_event(f"Grouped {len(task_solutions)} solutions into {len(grouped_indices)} groups", context="GROUPING")

        for key, g_indices in grouped_indices.items():
            _log_evaluation_event(
                f"Group key={key}, indices={g_indices}, web_agent_ids={[task_solutions[i].web_agent_id for i in g_indices]}",
                context="GROUPING TASK SOLUTIONS",
            )

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
                    cloned.web_agent_id = sol.web_agent_id or "unknown_agent"
                    if cloned.stats:
                        stats_copy = cloned.stats.model_copy(deep=True)
                        stats_copy.web_agent_id = sol.web_agent_id or "unknown_agent"
                        cloned.stats = stats_copy

                    final_results[idx] = cloned

                # logger.info(f"Group evaluation complete for representative web_agent_id: {representative.web_agent_id}")
            except Exception as e:
                logger.error(f"Error evaluating group actions: {e}")
                self.errors.append(str(e))
                for idx in group_indices:
                    sol = task_solutions[idx]
                    final_results[idx] = _create_error_result_for_group(task, sol, e)

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: list[BaseAction], is_web_real: bool) -> tuple[list[ActionExecutionResult], list[float], str | None]:
        """
        Executes all actions in a Playwright browser context and returns the results + times + early stop reason.

        Returns:
            Tuple of (action_results, action_execution_times, early_stop_reason)
            early_stop_reason is None if execution completed normally, or a string explaining why it stopped early
        """
        action_execution_times: list[float] = []
        action_results: list[ActionExecutionResult] = []
        max_consecutive_failures = self.config.max_consecutive_action_failures

        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                browser_specifications = task.specifications or BrowserSpecification()
                headless = self.config.headless if self.config.headless is not None else EVALUATOR_HEADLESS
                browser = await playwright.chromium.launch(headless=headless, args=[f"--window-size={browser_specifications.screen_width},{browser_specifications.screen_height}"])
                # browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS, slow_mo=2000)
                context = await browser.new_context(
                    extra_http_headers={"X-WebAgent-Id": web_agent_id, "X-Validator-Id": VALIDATOR_ID},
                    no_viewport=True,
                )
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()

                debug_network = os.getenv("IWA_DEBUG_NETWORK", "").lower() in ("1", "true", "yes")
                _setup_network_debugging(page, debug_network)

                browser_executor = _create_browser_executor(
                    task,
                    page,
                    self.backend_demo_webs_service,
                    self.config.dynamic_phase_config,
                    self.web_project,
                )

                action_results, action_execution_times, early_stop_reason = await _execute_action_loop(
                    browser_executor,
                    actions,
                    web_agent_id,
                    is_web_real,
                    self.config.should_record_gif,
                    self.config.task_delay_in_seconds,
                    max_consecutive_failures,
                    self.action_type_timing,
                )

                return action_results, action_execution_times, early_stop_reason

            except Exception as e:
                logger.error(f"Browser evaluation error: {e}")
                return [], [], f"Browser evaluation error: {e}"
            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()
