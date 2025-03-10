# concurrent_evaluator.py
import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.config.config import EVALUATOR_HEADLESS
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, EvaluatorConfig

# Import all needed helpers from evaluation_helper.py
from autoppia_iwa.src.evaluation.evaluator.utils import (
    display_batch_evaluation_summary,
    display_single_evaluation_summary,
    generate_feedback,
    get_random_clicker_performance,
    hash_actions,
    initialize_test_results_matrix,
    log_progress,
    run_tests,
)
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution


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

        logger.info(f"Evaluating Single task solution for task {task.id}...")

        logger.info("Resetting Project Environment & Database.")
        await self.backend_demo_webs_service.reset_database()

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

        logger.info("Resetting Project Environment & Database.")
        await self.backend_demo_webs_service.reset_database()

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

        # If no actions, return an immediate error
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
            # If simulated, reset the DB first
            browser_setup_start = time.time()
            if not is_web_real:
                await self.backend_demo_webs_service.reset_web_agent_events(web_agent_id)

            # Start browser usage
            browser_execution_start = time.time()
            stats.browser_setup_time = browser_execution_start - browser_setup_start

            execution_history, action_execution_times = await self._evaluate_in_browser(task, web_agent_id, actions, is_web_real)
            stats.action_execution_times = action_execution_times

            # Run tests
            test_start_time = time.time()
            test_results_matrix = await run_tests(self.web_project, task, execution_history)
            stats.test_execution_time = time.time() - test_start_time

            # Random clicker baseline
            random_start_time = time.time()
            random_clicker_passed, random_clicker_score = await get_random_clicker_performance(
                web_project=self.web_project,
                task=task,
                config=self.config,
                random_clicker_cache=self._random_clicker_cache,
                backend_demo_webs_service=self.backend_demo_webs_service,
                evaluate_in_browser_func=self._evaluate_in_browser,
            )
            stats.random_clicker_time = time.time() - random_start_time
            stats.random_clicker_score = random_clicker_score

            # Calculate raw score (# tests passed / total tests)
            raw_score = 0.0
            tests_passed_count = 0
            num_tests = 0

            if test_results_matrix and len(test_results_matrix[0]) > 0:
                num_tests = len(test_results_matrix[0])
                stats.total_tests = num_tests

                for test_index in range(num_tests):
                    if any(row[test_index].success for row in test_results_matrix):
                        tests_passed_count += 1

                if num_tests > 0:
                    raw_score = tests_passed_count / num_tests

            stats.tests_passed = tests_passed_count
            stats.raw_score = raw_score

            # Adjust final score relative to random clicker
            final_score = raw_score
            if self.config.normalize_score_with_random_clicker and num_tests > 0:
                final_score = max(0, raw_score - random_clicker_score)
                if self.config.normalize_scores and random_clicker_score < 1.0:
                    final_score = final_score / (1.0 - random_clicker_score)

            stats.final_score = final_score
            stats.total_time = time.time() - stats.start_time

            # Generate feedback
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

    async def _group_and_evaluate_task_solutions(self, task: Task, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        """
        Groups identical solutions by hashing their actions, evaluates them, and clones results.
        """
        start_time = time.time()

        grouped_tasks = defaultdict(list)
        if self.config.enable_grouping_tasks:
            for solution in task_solutions:
                hash_key = hash_actions(solution.actions)
                grouped_tasks[hash_key].append(solution)
            if self.config.verbose_logging:
                logger.info(f"Grouped {len(task_solutions)} solutions into {len(grouped_tasks)} groups")
        else:
            # Treat every solution as unique
            for i, solution in enumerate(task_solutions):
                unique_hash = hash_actions(solution.actions) + f"_{i}"
                grouped_tasks[unique_hash].append(solution)

        semaphore = asyncio.Semaphore(self.config.chunk_size)
        tasks = [self._evaluate_group_with_semaphore(task, group, semaphore) for group in grouped_tasks.values()]

        # If large, log minimal progress in background
        if len(tasks) > 5 and self.config.verbose_logging:
            progress_tracker = asyncio.create_task(log_progress(len(tasks), interval=10))
        else:
            progress_tracker = None

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Cancel progress tracker if used
        if progress_tracker:
            progress_tracker.cancel()
            try:
                await progress_tracker
            except asyncio.CancelledError:
                pass

        final_results: List[EvaluationResult] = []
        for item in raw_results:
            if isinstance(item, Exception):
                self.errors.append(str(item))
                if self.config.verbose_logging:
                    logger.error(f"Evaluation error: {item}")
            else:
                final_results.extend(item)

        elapsed = time.time() - start_time
        self.total_evaluation_time += elapsed
        self.evaluation_count += len(final_results)

        return final_results

    async def _evaluate_group_with_semaphore(self, task: Task, group: List[TaskSolution], semaphore: asyncio.Semaphore) -> List[EvaluationResult]:
        """
        Evaluates a group of identical solutions (all share the same actions).
        """
        async with semaphore:
            representative = group[0]
            try:
                rep_result = await self._evaluate_single_task_solution(task, representative)

                # Clone rep_result for all solutions in the group
                results: List[EvaluationResult] = []
                for sol in group:
                    cloned = rep_result.model_copy(deep=True)
                    cloned.web_agent_id = sol.web_agent_id
                    if cloned.stats:
                        stats_copy = cloned.stats.model_copy(deep=True)
                        stats_copy.web_agent_id = sol.web_agent_id
                        cloned.stats = stats_copy
                    results.append(cloned)

                logger.info(f"Group evaluation complete for representative: {representative.web_agent_id}")
                return results

            except Exception as e:
                logger.error(f"Error evaluating group actions: {e}")
                self.errors.append(str(e))
                # Return error results for each solution in the group
                return [
                    EvaluationResult(
                        web_agent_id=sol.web_agent_id,
                        final_score=0,
                        raw_score=0,
                        random_clicker_score=0,
                        test_results_matrix=initialize_test_results_matrix(task, len(sol.actions)),
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

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: List[BaseAction], is_web_real: bool) -> Tuple[List[ActionExecutionResult], List[float]]:
        """
        Executes all actions in a Playwright browser context and returns the results + times.
        """
        action_execution_times: List[float] = []
        action_results: List[ActionExecutionResult] = []

        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS)
                context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()

                # NOT NECESSARY FOR NOW
                # if not is_web_real:
                # Start monitoring the browser
                # monitor_task = asyncio.create_task(
                #     monitor_browser(
                #         self.web_project,
                #         task.url,
                #         page,
                #         web_agent_id,
                #         self.config.event_monitor_interval
                #     )
                # )

                browser_executor = PlaywrightBrowserExecutor(BrowserSpecification(), page, self.backend_demo_webs_service)

                try:
                    for i, action in enumerate(actions):
                        start_time_action = time.time()
                        try:
                            result = await browser_executor.execute_single_action(action, web_agent_id, iteration=i, is_web_real=is_web_real)
                            action_results.append(result)
                            elapsed = time.time() - start_time_action
                            action_execution_times.append(elapsed)

                            # Track timing by action type
                            self.action_type_timing[action.type].append(elapsed)

                            # Optional delay
                            if i < len(actions) - 1 and self.config.task_delay_in_seconds > 0:
                                await asyncio.sleep(self.config.task_delay_in_seconds)

                        except Exception as e:
                            logger.error(f"Action {i + 1}/{len(actions)} failed: {e}")
                            elapsed = time.time() - start_time_action
                            action_execution_times.append(elapsed)

                            # Insert placeholder if needed
                            if action_results:
                                error_result = action_results[-1].model_copy()
                                action_results.append(error_result)
                            break

                finally:
                    #     if not is_web_real and monitor_task:
                    #         monitor_task.cancel()
                    #         await asyncio.gather(monitor_task, return_exceptions=True)
                    pass
                return action_results, action_execution_times

            except Exception as e:
                logger.error(f"Browser evaluation error: {e}")
                return [], []

            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()
