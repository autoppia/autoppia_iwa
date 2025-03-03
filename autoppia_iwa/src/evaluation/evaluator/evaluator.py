# concurrent_evaluator.py
import asyncio
import hashlib
import time
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.config.config import EVALUATOR_HEADLESS
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import (
    EvaluationResult,
    EvaluatorConfig,
    EvaluationStats,
    Feedback,
    TestResult
)
from autoppia_iwa.src.evaluation.evaluator.utils import initialize_test_results_matrix
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

# Import from evaluation_helper (renamed from evaluation_reporter)
from autoppia_iwa.src.evaluation.evaluator.evaluation_helper import (
    display_single_evaluation_summary,
    display_batch_evaluation_summary,
    run_tests,
    generate_feedback,
)


class ConcurrentEvaluator(IEvaluator):
    def __init__(self, web_project: WebProject, config: EvaluatorConfig):
        self.config = config
        self._random_clicker_cache: Dict[str, Tuple[List[int], float]] = {}
        self.total_evaluation_time = 0.0
        self.evaluation_count = 0
        self.web_project = web_project
        self.backend_demo_webs_service = BackendDemoWebService(web_project=web_project)

        # Statistics collection
        self.evaluation_stats: List[EvaluationStats] = []
        self.action_type_timing = defaultdict(list)
        self.errors: List[str] = []

        # Configure loguru (minimal logs if not verbose)
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
        result = await self._evaluate_single_task_solution(task, task_solution)

        # Display final report for this single solution
        if result.stats:
            display_single_evaluation_summary(result.stats, debug_mode=self.config.debug_mode)
            self.evaluation_stats.append(result.stats)

        await self.backend_demo_webs_service.close()
        return result

    async def evaluate_task_solutions(self, task: Task, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        """
        Evaluate multiple solutions for the same task, optionally grouping identical ones.
        """
        logger.info(f"Evaluating {len(task_solutions)} solutions for task {task.id}...")

        results = await self._group_and_evaluate_task_solutions(task, task_solutions)

        # Save stats
        for r in results:
            if r.stats:
                self.evaluation_stats.append(r.stats)

        # Display final report after all evaluations for this task
        display_batch_evaluation_summary(
            task_id=task.id,
            evaluation_stats=self.evaluation_stats,
            debug_mode=self.config.debug_mode,
            action_type_timing=self.action_type_timing,
            errors=self.errors,
        )

        await self.backend_demo_webs_service.close()
        return results

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

        # If there are no actions, return an immediate error result
        if not actions:
            stats.had_errors = True
            stats.error_message = "No actions provided"
            stats.total_time = time.time() - stats.start_time
            test_results_matrix = initialize_test_results_matrix(task, 0)
            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                random_clicker_score=0,
                test_results_matrix=test_results_matrix,
                feedback=None,
                execution_history=[],
                random_clicker_passed_tests_indexes=[],
                evaluation_time=0.1,
                stats=stats,
            )

        try:
            # Optionally reset backend DB for simulated tasks
            browser_setup_start = time.time()
            if not is_web_real:
                await self.backend_demo_webs_service.reset_backend_events_db(web_agent_id)

            # Execute actions in browser
            browser_execution_start = time.time()
            stats.browser_setup_time = browser_execution_start - browser_setup_start

            execution_history, action_execution_times = await self._evaluate_in_browser(
                task, web_agent_id, actions, is_web_real
            )
            stats.action_execution_times = action_execution_times

            # Run tests using our helper method
            test_start_time = time.time()
            test_results_matrix = run_tests(task, execution_history)
            stats.test_execution_time = time.time() - test_start_time

            # Compute random clicker baseline
            random_start_time = time.time()
            random_clicker_passed, random_clicker_score = await self._get_random_clicker_performance(task)
            stats.random_clicker_time = time.time() - random_start_time
            stats.random_clicker_score = random_clicker_score

            # Calculate the raw score (# of tests passed / total tests)
            raw_score = 0.0
            tests_passed_count = 0
            num_tests = 0

            if test_results_matrix and len(test_results_matrix[0]) > 0:
                num_tests = len(test_results_matrix[0])
                stats.total_tests = num_tests

                for test_index in range(num_tests):
                    # If any action in the chain passed this test, consider it passed
                    if any(test_results_matrix[a_idx][test_index].success
                           for a_idx in range(len(test_results_matrix))):
                        tests_passed_count += 1

                if num_tests > 0:
                    raw_score = tests_passed_count / num_tests

            stats.tests_passed = tests_passed_count
            stats.raw_score = raw_score

            # Adjust the score relative to random clicker
            final_score = raw_score
            if self.config.normalize_score_with_random_clicker and num_tests > 0:
                final_score = max(0, raw_score - random_clicker_score)
                if self.config.normalize_scores and random_clicker_score < 1.0:
                    final_score = final_score / (1.0 - random_clicker_score)

            stats.final_score = final_score
            stats.total_time = time.time() - stats.start_time

            # Generate feedback with our helper
            feedback = generate_feedback(task, execution_history, test_results_matrix)

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=1 if final_score >= 0.25 else final_score,
                raw_score=raw_score,
                random_clicker_score=random_clicker_score,
                test_results_matrix=test_results_matrix,
                feedback=feedback,
                execution_history=execution_history,
                random_clicker_passed_tests_indexes=random_clicker_passed,
                evaluation_time=stats.total_time,
                stats=stats,
            )

        except Exception as e:
            stats.had_errors = True
            stats.error_message = str(e)
            stats.total_time = time.time() - stats.start_time
            logger.error(f"Error evaluating task solution: {e}")

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                random_clicker_score=0,
                test_results_matrix=initialize_test_results_matrix(task, len(actions)),
                feedback=None,
                execution_history=[],
                random_clicker_passed_tests_indexes=[],
                evaluation_time=0,
                stats=stats,
            )

    async def _group_and_evaluate_task_solutions(
        self, task: Task, task_solutions: List[TaskSolution]
    ) -> List[EvaluationResult]:
        """
        Groups identical solutions, evaluates them once, and clones the result for efficiency.
        """
        start_time = time.time()

        grouped_tasks = defaultdict(list)
        if self.config.enable_grouping_tasks:
            for solution in task_solutions:
                hash_key = self._hash_actions(solution.actions)
                grouped_tasks[hash_key].append(solution)

            if self.config.verbose_logging:
                logger.info(
                    f"Grouped {len(task_solutions)} solutions into {len(grouped_tasks)} action groups"
                )
        else:
            # Every solution is considered unique
            for i, solution in enumerate(task_solutions):
                unique_hash = self._hash_actions(solution.actions) + f"_{i}"
                grouped_tasks[unique_hash].append(solution)

        semaphore = asyncio.Semaphore(self.config.chunk_size)
        group_tasks = [
            self._evaluate_group_with_semaphore(task, group, semaphore)
            for group in grouped_tasks.values()
        ]

        # Optional progress tracker
        if len(group_tasks) > 5 and self.config.verbose_logging:
            progress_tracker = asyncio.create_task(self._log_progress(len(group_tasks)))
        else:
            progress_tracker = None

        results = await asyncio.gather(*group_tasks, return_exceptions=True)

        if progress_tracker:
            progress_tracker.cancel()
            try:
                await progress_tracker
            except asyncio.CancelledError:
                pass

        final_results: List[EvaluationResult] = []
        for item in results:
            if isinstance(item, Exception):
                # Register the error
                self.errors.append(str(item))
                if self.config.verbose_logging:
                    logger.error(f"Evaluation error: {item}")
            else:
                final_results.extend(item)

        eval_time = time.time() - start_time
        self.total_evaluation_time += eval_time
        self.evaluation_count += len(final_results)

        return final_results

    async def _log_progress(self, total_groups: int):
        """
        Logs progress updates every 10 seconds while evaluating large batches.
        """
        try:
            while True:
                await asyncio.sleep(10)
                completed = sum(
                    1
                    for t in asyncio.all_tasks()
                    if t.done() and "evaluate_group_with_semaphore" in str(t)
                )
                logger.info(
                    f"Progress: {completed}/{total_groups} groups "
                    f"({completed / total_groups * 100:.0f}%)"
                )
        except asyncio.CancelledError:
            pass

    async def _evaluate_group_with_semaphore(
        self,
        task: Task,
        group: List[TaskSolution],
        semaphore: asyncio.Semaphore,
    ) -> List[EvaluationResult]:
        """
        Evaluates a group of identical solutions (they share the same actions).
        """
        async with semaphore:
            representative = group[0]
            try:
                rep_result = await self._evaluate_single_task_solution(task, representative)

                # Clone the result for all solutions in the same group
                final: List[EvaluationResult] = []
                for sol in group:
                    cloned = rep_result.model_copy(deep=True)
                    cloned.web_agent_id = sol.web_agent_id
                    # Clone stats for each agent
                    if cloned.stats:
                        stats_copy = cloned.stats.model_copy(deep=True)
                        stats_copy.web_agent_id = sol.web_agent_id
                        cloned.stats = stats_copy

                    final.append(cloned)

                logger.info(f"Group evaluation done for representative: {representative.web_agent_id}")
                return final

            except Exception as e:
                logger.error(f"Error evaluating actions in group: {e}")
                self.errors.append(str(e))
                return [
                    EvaluationResult(
                        web_agent_id=sol.web_agent_id,
                        final_score=0,
                        raw_score=0,
                        random_clicker_score=0,
                        test_results_matrix=initialize_test_results_matrix(
                            task, len(sol.actions)
                        ),
                        feedback=None,
                        execution_history=[],
                        random_clicker_passed_tests_indexes=[],
                        evaluation_time=0,
                        stats=EvaluationStats(
                            web_agent_id=sol.web_agent_id,
                            task_id=task.id,
                            action_count=len(sol.actions),
                            start_time=time.time(),
                            had_errors=True,
                            error_message=str(e),
                        ),
                    )
                    for sol in group
                ]

    @staticmethod
    def _hash_actions(actions: List[BaseAction]) -> str:
        """
        Hashes a list of actions to identify identical solutions.
        """
        try:
            return hashlib.sha256(
                "|".join(str(a.model_dump()) for a in actions).encode()
            ).hexdigest()
        except Exception:
            logger.error("Error generating hash for actions.")
            return ""

    async def _evaluate_in_browser(
        self,
        task: Task,
        web_agent_id: str,
        actions: List[BaseAction],
        is_web_real: bool,
    ) -> Tuple[List[ActionExecutionResult], List[float]]:
        """
        Executes all actions in a Playwright browser context and records timing.
        """
        action_execution_times: List[float] = []
        action_results: List[ActionExecutionResult] = []

        async with async_playwright() as playwright:
            browser = None
            context = None
            try:
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS)
                context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()

                monitor_task = None
                if not is_web_real:
                    monitor_task = asyncio.create_task(
                        self._monitor_browser(self.web_project, task.url, page, web_agent_id)
                    )

                browser_executor = PlaywrightBrowserExecutor(
                    BrowserSpecification(),
                    page,
                    self.backend_demo_webs_service
                )

                try:
                    for i, action in enumerate(actions):
                        action_start = time.time()
                        try:
                            result = await browser_executor.execute_single_action(
                                action,
                                web_agent_id,
                                iteration=i,
                                is_web_real=is_web_real
                            )
                            action_results.append(result)
                            elapsed = time.time() - action_start
                            action_execution_times.append(elapsed)

                            # Track timing by action type globally
                            self.action_type_timing[action.type].append(elapsed)

                            # Optional delay between actions
                            if i < len(actions) - 1 and self.config.task_delay_in_seconds > 0:
                                await asyncio.sleep(self.config.task_delay_in_seconds)

                        except Exception as e:
                            logger.error(f"Action {i+1}/{len(actions)} failed: {e}")
                            # Even if an action fails, record timing so far
                            elapsed = time.time() - action_start
                            action_execution_times.append(elapsed)

                            # Create a placeholder result if needed
                            if action_results:
                                error_result = action_results[-1].model_copy()
                                action_results.append(error_result)
                            break

                finally:
                    if not is_web_real and monitor_task:
                        monitor_task.cancel()
                        await asyncio.gather(monitor_task, return_exceptions=True)

                return action_results, action_execution_times

            except Exception as e:
                logger.error(f"Browser evaluation error: {e}")
                return [], []

            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()

    async def _monitor_browser(self, web_project, task_url, page, web_agent_id):
        """
        Monitors browser navigation events and sends them to the backend.
        """
        def on_frame_navigated(frame):
            if frame.url:
                asyncio.create_task(_handle_frame_navigation(web_project, frame.url, task_url, web_agent_id))

        async def _handle_frame_navigation(web_project, url, task_url, web_agent_id):
            try:
                backend_demo_web_service = BackendDemoWebService(web_project)
                await backend_demo_web_service.send_page_view_event(url, web_agent_id)
                await backend_demo_web_service.close()
            except Exception as e:
                logger.error(f"Error handling frame navigation: {e}")

        page.on("framenavigated", on_frame_navigated)
        try:
            while not page.is_closed():
                await asyncio.sleep(self.config.event_monitor_interval)
        except asyncio.CancelledError:
            pass

    async def _get_random_clicker_performance(self, task: Task) -> Tuple[List[int], float]:
        """
        Returns random clicker baseline test performance (from cache if available).
        """
        if self.config.cache_random_clicker_results and task.id in self._random_clicker_cache:
            if self.config.verbose_logging:
                logger.debug(f"Using cached random clicker results for task {task.id}")
            return self._random_clicker_cache[task.id]

        # Build random clicker solution
        random_clicker = RandomClickerWebAgent(name="Random-clicker")
        task_solution = await random_clicker.solve_task(task=task)
        random_actions = task_solution.actions

        if not random_actions:
            return [], 0.0

        random_web_agent_id = f"random-clicker-{task.id}"

        if not task.is_web_real:
            await self.backend_demo_webs_service.reset_backend_events_db(random_web_agent_id)

        # Execute random clicker actions
        random_execution_history, _ = await self._evaluate_in_browser(
            task, random_web_agent_id, random_actions, task.is_web_real
        )

        # Use our helper to run the tests
        random_test_results = run_tests(task, random_execution_history)

        passed_tests: List[int] = []
        random_score = 0.0
        if random_test_results and len(random_test_results[0]) > 0:
            num_tests = len(random_test_results[0])
            passed_count = 0
            for test_index in range(num_tests):
                for action_idx in range(len(random_test_results)):
                    if random_test_results[action_idx][test_index].success:
                        passed_tests.append(test_index)
                        passed_count += 1
                        break
            if num_tests > 0:
                random_score = passed_count / num_tests

        # Cache if needed
        if self.config.cache_random_clicker_results:
            self._random_clicker_cache[task.id] = (passed_tests, random_score)

        return passed_tests, random_score
