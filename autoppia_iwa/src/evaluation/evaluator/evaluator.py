import asyncio
import hashlib
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

from autoppia_iwa.config.config import EVALUATOR_HEADLESS
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult as BaseEvaluationResult
from autoppia_iwa.src.evaluation.classes import Feedback, TestResult
from autoppia_iwa.src.evaluation.evaluator.feedback_generator import FeedbackGenerator
from autoppia_iwa.src.evaluation.evaluator.test_runner import TestRunner
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent


class EvaluationStats(BaseModel):
    """Statistics for a single evaluation"""

    web_agent_id: str
    task_id: str
    action_count: int
    action_types: Dict[str, int] = Field(default_factory=dict)

    # Timing stats
    start_time: float
    total_time: float = 0
    browser_setup_time: float = 0
    action_execution_times: List[float] = Field(default_factory=list)
    test_execution_time: float = 0
    random_clicker_time: float = 0

    # Performance stats
    raw_score: float = 0
    random_clicker_score: float = 0
    final_score: float = 0
    tests_passed: int = 0
    total_tests: int = 0

    # Error tracking
    had_errors: bool = False
    error_message: str = ""

    def get_summary_dict(self) -> Dict[str, Any]:
        """Get a dictionary of summary statistics"""
        action_time = sum(self.action_execution_times) if self.action_execution_times else 0
        return {
            "agent_id": self.web_agent_id,
            "task_id": self.task_id,
            "actions": self.action_count,
            "score": self.final_score,
            "time_total": round(self.total_time, 2),
            "time_browser_setup": round(self.browser_setup_time, 2),
            "time_actions": round(action_time, 2),
            "time_avg_per_action": round(action_time / max(1, len(self.action_execution_times)), 3),
            "time_random": round(self.random_clicker_time, 2),
            "tests_passed": f"{self.tests_passed}/{self.total_tests}",
            "success": not self.had_errors,
        }


class EvaluationResult(BaseEvaluationResult):
    web_agent_id: Optional[str] = None
    raw_score: float = 0.0
    random_clicker_score: float = 0.0
    random_passed_tests: List[int] = Field(default_factory=list)
    evaluation_time: float = 0.0  # Time taken to evaluate this solution
    stats: Optional[EvaluationStats] = None


class EvaluatorConfig(BaseModel):
    save_results_in_db: bool = False
    task_delay_in_seconds: float = Field(default=0.1, gt=0)
    chunk_size: int = Field(default=5, gt=0)
    browser_timeout: float = Field(default=10000, gt=0)
    event_monitor_interval: float = Field(default=0.1, gt=0, le=0.5)
    enable_grouping_tasks: bool = Field(default=True)
    exclude_random_passed_tests: bool = Field(default=True)
    cache_random_clicker_results: bool = Field(default=True)
    normalize_scores: bool = Field(default=True)
    verbose_logging: bool = Field(default=False)  # Default to minimal logging
    debug_mode: bool = Field(default=False)  # Even more minimal logging


class ConcurrentEvaluator(IEvaluator):
    def __init__(self, web_project, config: EvaluatorConfig):
        self.config = config
        self._random_clicker_cache: Dict[str, Tuple[List[int], float]] = {}
        self.total_evaluation_time = 0.0
        self.evaluation_count = 0
        self.web_project = web_project
        self.backend_demo_webs_service = BackendDemoWebService(web_project=web_project)

        # Statistics collection
        self.evaluation_stats = []  # List of completed evaluation stats
        self.action_type_timing = defaultdict(list)  # Track timing by action type
        self.errors = []  # Track evaluation errors

        # Configure loguru levels
        if not self.config.verbose_logging:
            logger.remove()
            logger.add(lambda msg: print(msg, end=""), level="WARNING" if self.config.debug_mode else "INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

    async def evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Evaluate a single task solution given both the task and task solution.
        Args:
            task: The Task object containing task details
            task_solution: The TaskSolution object with actions and web_agent_id
        Returns:
            EvaluationResult: The evaluation result
        """
        # Minimal logging during evaluation
        result = await self._evaluate_single_task_solution(task, task_solution)

        # Only display the final report
        if hasattr(result, 'stats') and result.stats:
            self._display_single_evaluation_summary(result.stats)
            self.evaluation_stats.append(result.stats)

        await self.backend_demo_webs_service.close()
        return result

    async def evaluate_task_solutions(self, task: Task, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        """
        Evaluate multiple task solutions for a single task.
        Args:
            task: The Task object containing task details
            task_solutions: List of TaskSolution objects with actions and web_agent_id
        Returns:
            List[EvaluationResult]: List of evaluation results
        """
        # Minimal progress info
        logger.info(f"Evaluating {len(task_solutions)} solutions for task {task.id}...")

        # Run the evaluations
        result = await self._group_and_evaluate_task_solutions(task, task_solutions)

        # Extract evaluation stats from results
        for r in result:
            if hasattr(r, 'stats') and r.stats:
                self.evaluation_stats.append(r.stats)

        # Display the final report after all evaluations
        self._display_batch_evaluation_summary(task.id)

        await self.backend_demo_webs_service.close()
        return result

    async def _group_and_evaluate_task_solutions(self, task: Task, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        """Group similar task solutions and evaluate them together for efficiency."""
        start_time = time.time()

        # Group task solutions by action hash
        grouped_tasks = defaultdict(list)
        if self.config.enable_grouping_tasks:
            for task_solution in task_solutions:
                grouped_tasks[self._hash_actions(task_solution.actions)].append(task_solution)

            if self.config.verbose_logging:
                logger.info(f"Grouped {len(task_solutions)} solutions into {len(grouped_tasks)} action groups")
        else:
            for i, task_solution in enumerate(task_solutions):
                unique_hash = self._hash_actions(task_solution.actions) + f"_{i}"
                grouped_tasks[unique_hash].append(task_solution)

        # Use semaphore to limit concurrent evaluations
        semaphore = asyncio.Semaphore(self.config.chunk_size)
        group_tasks = [self._evaluate_group_with_semaphore(task, group, semaphore) for group in grouped_tasks.values()]

        # Show minimal progress for large batches
        if len(group_tasks) > 5 and self.config.verbose_logging:
            progress_tracker = asyncio.create_task(self._log_progress(len(group_tasks)))
        else:
            progress_tracker = None

        # Gather all results
        raw_results = await asyncio.gather(*group_tasks, return_exceptions=True)

        # Cancel progress tracker if it exists
        if progress_tracker:
            progress_tracker.cancel()
            try:
                await progress_tracker
            except asyncio.CancelledError:
                pass

        # Process results
        final_results = []
        exceptions_count = 0
        for result in raw_results:
            if isinstance(result, Exception):
                exceptions_count += 1
                self.errors.append(str(result))
                if self.config.verbose_logging:
                    logger.error(f"Evaluation error: {result}")
            else:
                final_results.extend(result)

        # Update aggregate statistics
        total_time = time.time() - start_time
        self.total_evaluation_time += total_time
        self.evaluation_count += len(final_results)

        return final_results

    async def _log_progress(self, total_groups):
        """Log minimal progress updates for large batch evaluations"""
        try:
            completed = 0
            while True:
                await asyncio.sleep(10)  # Only update every 10 seconds
                completed = sum(1 for t in asyncio.all_tasks() if t.done() and "evaluate_group_with_semaphore" in str(t))
                logger.info(f"Progress: {completed} / {total_groups} groups ({completed / total_groups * 100:.0f}%)")
        except asyncio.CancelledError:
            pass

    async def _evaluate_group_with_semaphore(self, task: Task, group: List[TaskSolution], semaphore: asyncio.Semaphore) -> List[EvaluationResult]:
        """Evaluate a group of identical task solutions with semaphore for concurrency control."""
        async with semaphore:
            representative = group[0]

            try:
                # Evaluate the representative actions
                rep_result = await self._evaluate_single_task_solution(task, representative)

                # Clone results for each web_agent in the group
                results: List[EvaluationResult] = []
                for task_solution in group:
                    cloned_result = rep_result.model_copy(deep=True)
                    cloned_result.web_agent_id = task_solution.web_agent_id

                    # Create a copy of the stats for each agent
                    if hasattr(cloned_result, 'stats') and cloned_result.stats:
                        stats_copy = cloned_result.stats.model_copy(deep=True)
                        stats_copy.web_agent_id = task_solution.web_agent_id
                        cloned_result.stats = stats_copy

                    results.append(cloned_result)

                return results

            except Exception as e:
                logger.error(f"Error evaluating actions: {e}")
                self.errors.append(str(e))

                # Return empty results for each agent in the group
                return [
                    EvaluationResult(
                        web_agent_id=ts.web_agent_id,
                        final_score=0,
                        raw_score=0,
                        random_clicker_score=0,
                        test_results_matrix=[],
                        feedback=None,
                        execution_history=[],
                        random_passed_tests=[],
                        evaluation_time=0,
                        stats=EvaluationStats(web_agent_id=ts.web_agent_id, task_id=task.id, action_count=len(ts.actions), start_time=time.time(), had_errors=True, error_message=str(e)),
                    )
                    for ts in group
                ]

    @staticmethod
    def _hash_actions(actions: List[BaseAction]) -> str:
        """Create a hash of the actions list for grouping identical solutions."""
        try:
            return hashlib.sha256("|".join(str(action.model_dump()) for action in actions).encode()).hexdigest()
        except Exception:
            logger.error("Error generating hash for actions.")
            return ""

    async def _evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Evaluate a single task solution.
        Args:
            task: The Task object containing task details
            task_solution: The TaskSolution object with actions and web_agent_id
        Returns:
            EvaluationResult: The evaluation result
        """
        actions = task_solution.actions
        web_agent_id = task_solution.web_agent_id
        is_web_real = task.is_web_real

        # Create stats object to track this evaluation
        stats = EvaluationStats(web_agent_id=web_agent_id, task_id=task.id, action_count=len(actions), start_time=time.time())

        # Count action types
        for action in actions:
            stats.action_types[action.type] = stats.action_types.get(action.type, 0) + 1

        if not actions:
            stats.had_errors = True
            stats.error_message = "No actions provided"
            stats.total_time = time.time() - stats.start_time

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                random_clicker_score=0,
                test_results_matrix=[],
                feedback=None,
                execution_history=[],
                random_passed_tests=[],
                evaluation_time=0,
                stats=stats,
            )

        try:
            # First evaluate the agent's actions
            browser_setup_start = time.time()
            if not is_web_real:
                await self.backend_demo_webs_service.reset_backend_events_db(web_agent_id)

            # Execute agent actions in browser
            browser_execution_start = time.time()
            stats.browser_setup_time = browser_execution_start - browser_setup_start

            execution_history, action_execution_times = await self._evaluate_in_browser(task, web_agent_id, actions, is_web_real)

            stats.action_execution_times = action_execution_times

            # Run tests on agent's actions
            test_start_time = time.time()
            test_results_matrix = self._run_tests(task, execution_history)
            stats.test_execution_time = time.time() - test_start_time

            # Get or compute random clicker performance for baseline score
            random_start_time = time.time()
            random_passed_tests, random_clicker_score = await self._get_random_clicker_performance(task)
            stats.random_clicker_time = time.time() - random_start_time
            stats.random_clicker_score = random_clicker_score

            # Calculate agent's raw score (without accounting for random clicker)
            raw_score = 0
            tests_passed_count = 0
            num_tests = 0

            if test_results_matrix and test_results_matrix[0]:
                # Get the number of tests (columns in the matrix)
                num_tests = len(test_results_matrix[0])
                stats.total_tests = num_tests

                # For each test, check if it was passed at least once
                for test_index in range(num_tests):
                    test_passed = False
                    for action_index in range(len(test_results_matrix)):
                        if test_results_matrix[action_index][test_index].success:
                            test_passed = True
                            break
                    if test_passed:
                        tests_passed_count += 1

                # Calculate raw score
                if num_tests > 0:
                    raw_score = tests_passed_count / num_tests

            stats.tests_passed = tests_passed_count
            stats.raw_score = raw_score

            # Calculate final adjusted score by subtracting random clicker score
            final_score = raw_score

            # Adjust score by subtracting random clicker score
            if self.config.exclude_random_passed_tests and num_tests > 0:
                # Simple subtraction approach: agent score - random clicker score
                # If result is negative, set to 0
                final_score = max(0, raw_score - random_clicker_score)

                # Option to normalize the result to a 0-1 scale
                if self.config.normalize_scores and random_clicker_score < 1.0:
                    # Normalize to range from 0.0 to 1.0
                    # This maps the possible score range (random_score to 1.0) to (0.0 to 1.0)
                    normalized_score = final_score / (1.0 - random_clicker_score)
                    final_score = normalized_score

            stats.final_score = final_score

            # Calculate total evaluation time
            stats.total_time = time.time() - stats.start_time

            # Generate feedback
            feedback = self._generate_feedback(task, execution_history, test_results_matrix)

            # Create the result
            result = EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=final_score,
                raw_score=raw_score,
                random_clicker_score=random_clicker_score,
                test_results_matrix=test_results_matrix,
                feedback=feedback,
                execution_history=execution_history,
                random_passed_tests=random_passed_tests,
                evaluation_time=stats.total_time,
                stats=stats,
            )

            return result

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
                test_results_matrix=[],
                feedback=None,
                execution_history=[],
                random_passed_tests=[],
                evaluation_time=0,
                stats=stats,
            )

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: List[BaseAction], is_web_real: bool) -> Tuple[List[ActionExecutionResult], List[float]]:
        """
        Execute actions in a browser and get the results.
        Args:
            task: The task being evaluated
            web_agent_id: ID of the web agent
            actions: List of actions to execute
            is_web_real: Whether the web is real or simulated
        Returns:
            Tuple[List[ActionExecutionResult], List[float]]: Results of executing each action and execution times
        """
        action_execution_times = []
        action_results = []

        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                # Start browser
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS)
                context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()

                monitor_task = None
                if not is_web_real:
                    monitor_task = asyncio.create_task(self._monitor_browser(self.web_project, task.url, page, web_agent_id))

                browser_executor = PlaywrightBrowserExecutor(BrowserSpecification(), page, self.backend_demo_webs_service)

                try:
                    # Execute actions and measure time
                    for i, action in enumerate(actions):
                        action_start = time.time()

                        # Execute single action
                        try:
                            result = await browser_executor.execute_single_action(action, web_agent_id, iteration=i, is_web_real=is_web_real)
                            action_results.append(result)

                            action_end = time.time()
                            action_time = action_end - action_start
                            action_execution_times.append(action_time)

                            # Update global action type timing stats
                            self.action_type_timing[action.type].append(action_time)

                            # Add delay between actions if configured
                            if i < len(actions) - 1 and self.config.task_delay_in_seconds > 0:
                                await asyncio.sleep(self.config.task_delay_in_seconds)

                        except Exception as e:
                            logger.error(f"Action {i + 1}/{len(actions)}: {action.type} failed with error: {e}")

                            # Add a placeholder for timing
                            action_end = time.time()
                            action_time = action_end - action_start
                            action_execution_times.append(action_time)

                            # Create an error result
                            if len(action_results) > 0:
                                # Clone the last result with error info
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
        Monitor browser events and send them to the backend.
        Args:
            task_url: URL of the task
            page: Playwright page object
            web_agent_id: ID of the web agent
        """

        def on_frame_navigated(frame):
            if frame.url:
                # Create a task to run the async code without awaiting it directly
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
        Get random clicker performance, either from cache or by evaluating.
        Args:
            task: The task to evaluate
        Returns:
            Tuple[List[int], float]: List of test indices passed by random clicker and its score
        """
        # Check if we have cached results for this task
        if self.config.cache_random_clicker_results and task.id in self._random_clicker_cache:
            if self.config.verbose_logging:
                logger.debug(f"Using cached random clicker results for task {task.id}")
            return self._random_clicker_cache[task.id]

        # Generate random clicker actions
        random_clicker = RandomClickerWebAgent(name="Random-clicker")
        task_solution = await random_clicker.solve_task(task=task)
        random_actions = task_solution.actions

        # Exit early if no actions were generated
        if not random_actions:
            return [], 0.0

        # Create a temporary web_agent_id for the random clicker
        random_web_agent_id = f"random-clicker-{task.id}"

        # Execute random clicker actions
        if not task.is_web_real:
            await self.backend_demo_webs_service.reset_backend_events_db(random_web_agent_id)

        random_execution_history, _ = await self._evaluate_in_browser(task, random_web_agent_id, random_actions, task.is_web_real)

        # Run tests on random clicker actions
        random_test_results = self._run_tests(task, random_execution_history)

        # Calculate which tests the random clicker passed
        random_passed_tests = []
        random_score = 0.0
        if random_test_results and random_test_results[0]:
            num_tests = len(random_test_results[0])
            passed_count = 0
            # For each test, check if random clicker passed it
            for test_index in range(num_tests):
                for action_index in range(len(random_test_results)):
                    if random_test_results[action_index][test_index].success:
                        random_passed_tests.append(test_index)
                        passed_count += 1
                        break
            if num_tests > 0:
                random_score = passed_count / num_tests

        # Cache the results
        if self.config.cache_random_clicker_results:
            self._random_clicker_cache[task.id] = (random_passed_tests, random_score)

        return random_passed_tests, random_score

    @staticmethod
    def _run_tests(task: Task, execution_history: List[ActionExecutionResult]) -> List[List[TestResult]]:
        """
        Run all tests after each action, building a test results matrix.
        Args:
            task: The task being evaluated
            execution_history: History of executed actions
        Returns:
            List[List[TestResult]]: A matrix where each row contains test results after each action
        """
        test_results_matrix = []
        browser_snapshots = []

        for i, action_result in enumerate(execution_history):
            snapshot = action_result.browser_snapshot
            browser_snapshots.append(snapshot)

            test_runner = TestRunner(task.tests)

            # Run tests for the current snapshot, giving it access to all snapshots up to this point
            test_results = test_runner.run_tests(prompt=task.prompt, snapshot=snapshot, browser_snapshots=browser_snapshots, current_action_index=i)

            # Add the results for this snapshot to the matrix
            test_results_matrix.append(test_results)

        return test_results_matrix

    @staticmethod
    def _generate_feedback(task: Task, execution_history: List[ActionExecutionResult], test_results_matrix: List[List[TestResult]]) -> Feedback:
        """
        Generate feedback based on test results.
        Args:
            task: The task being evaluated
            execution_history: History of executed actions
            test_results_matrix: Matrix of test results
        Returns:
            Feedback: Generated feedback
        """
        return FeedbackGenerator.generate_feedback(task_prompt=task.prompt, execution_history=execution_history, test_results_matrix=test_results_matrix)

    def _display_single_evaluation_summary(self, stats: EvaluationStats):
        """Display a concise summary for a single evaluation"""
        stats.get_summary_dict()

        if self.config.debug_mode:
            return  # Skip display in debug mode

        # Calculate timing percentages
        total = stats.total_time
        setup_pct = stats.browser_setup_time / total * 100 if total > 0 else 0
        action_time = sum(stats.action_execution_times) if stats.action_execution_times else 0
        action_pct = action_time / total * 100 if total > 0 else 0
        random_pct = stats.random_clicker_time / total * 100 if total > 0 else 0
        test_pct = stats.test_execution_time / total * 100 if total > 0 else 0

        logger.info(f"\n{'-' * 60}")
        logger.info(f"Evaluation Results for Agent: {stats.web_agent_id}")
        logger.info(f"{'-' * 60}")
        logger.info(f"Task: {stats.task_id}")
        logger.info(f"Score: {stats.final_score:.2f} (Raw: {stats.raw_score:.2f}, Random: {stats.random_clicker_score:.2f})")
        logger.info(f"Tests Passed: {stats.tests_passed}/{stats.total_tests}")
        logger.info(f"Actions: {stats.action_count} ({', '.join(f'{k}: {v}' for k, v in stats.action_types.items())})")
        logger.info(f"{'-' * 40}")
        logger.info(f"Time: {stats.total_time:.2f}s total")
        logger.info(f" - Browser Setup: {stats.browser_setup_time:.2f}s ({setup_pct:.1f}%)")
        logger.info(f" - Actions Execution: {action_time:.2f}s ({action_pct:.1f}%)")
        logger.info(f" - Test Execution: {stats.test_execution_time:.2f}s ({test_pct:.1f}%)")
        logger.info(f" - Random Evaluation: {stats.random_clicker_time:.2f}s ({random_pct:.1f}%)")

        if stats.action_execution_times:
            avg_time = sum(stats.action_execution_times) / len(stats.action_execution_times)
            max_time = max(stats.action_execution_times)
            logger.info(f"Action Time: {avg_time:.3f}s avg, {max_time:.3f}s max")

        if stats.had_errors:
            logger.error(f"Errors: {stats.error_message}")

        logger.info(f"{'-' * 60}")

    def _display_batch_evaluation_summary(self, task_id):
        """Display a concise summary of all evaluations in the batch"""
        if self.config.debug_mode or not self.evaluation_stats:
            return  # Skip in debug mode or if no stats

        # Get stats for this task only
        task_stats = [s for s in self.evaluation_stats if s.task_id == task_id]
        if not task_stats:
            return

        # Calculate aggregate statistics
        total_agents = len(task_stats)
        successful_agents = sum(1 for s in task_stats if not s.had_errors)
        avg_score = sum(s.final_score for s in task_stats) / max(1, total_agents)
        avg_time = sum(s.total_time for s in task_stats) / max(1, total_agents)

        # Group by agent type (extract prefix before first hyphen)
        agent_groups = defaultdict(list)
        for stat in task_stats:
            agent_id = stat.web_agent_id
            agent_type = agent_id.split('-')[0] if '-' in agent_id else agent_id
            agent_groups[agent_type].append(stat)

        # Output formatted table for batch summary
        logger.info(f"\n{'=' * 80}")
        logger.info(f"EVALUATION SUMMARY FOR TASK: {task_id}")
        logger.info(f"{'=' * 80}")
        logger.info(f"Total Agents: {total_agents}, Success Rate: {successful_agents}/{total_agents} ({successful_agents / total_agents * 100:.1f}%)")
        logger.info(f"Average Score: {avg_score:.4f}, Average Time: {avg_time:.2f}s")

        # Create a summary table for each agent group
        for agent_type, stats in agent_groups.items():
            avg_group_score = sum(s.final_score for s in stats) / max(1, len(stats))
            avg_group_time = sum(s.total_time for s in stats) / max(1, len(stats))

            logger.info(f"\n{'-' * 60}")
            logger.info(f"Agent Hash: {agent_type} ({len(stats)} agents)")
            logger.info(f"Average Score: {avg_group_score:.4f}, Average Time: {avg_group_time:.2f}s")

            # Action timing statistics
            all_action_times = []
            for s in stats:
                all_action_times.extend(s.action_execution_times)

            if all_action_times:
                avg_action_time = sum(all_action_times) / len(all_action_times)
                max_action_time = max(all_action_times)
                logger.info(f"Actions: {sum(s.action_count for s in stats)}, Avg Time: {avg_action_time:.3f}s, Max: {max_action_time:.3f}s")

            # Test results
            total_tests = stats[0].total_tests if stats else 0
            if total_tests > 0:
                tests_passed = [s.tests_passed for s in stats]
                avg_passed = sum(tests_passed) / len(tests_passed)
                logger.info(f"Tests Passed: {avg_passed:.1f}/{total_tests} on average")

        # Display timing breakdown across all agents
        all_browser_setup = sum(s.browser_setup_time for s in task_stats)
        all_action_time = sum(sum(s.action_execution_times) for s in task_stats)
        all_test_time = sum(s.test_execution_time for s in task_stats)
        all_random_time = sum(s.random_clicker_time for s in task_stats)
        all_total_time = sum(s.total_time for s in task_stats)

        logger.info(f"\n{'-' * 60}")
        logger.info("TIMING BREAKDOWN (across all agents)")
        logger.info(f"Total Evaluation Time: {all_total_time:.2f}s")
        logger.info(f"Browser Setup: {all_browser_setup:.2f}s ({all_browser_setup / all_total_time* 100:.1f}%)")
        logger.info(f"Action Execution: {all_action_time:.2f}s ({all_action_time / all_total_time * 100:.1f}%)")
        logger.info(f"Test Execution: {all_test_time:.2f}s ({all_test_time / all_total_time * 100:.1f}%)")
        logger.info(f"Random Evaluation: {all_random_time:.2f}s ({all_random_time / all_total_time * 100:.1f}%)")

        # Display action type timing statistics
        if self.action_type_timing:
            logger.info(f"\n{'-' * 60}")
            logger.info("ACTION TYPE PERFORMANCE")
            for action_type, times in sorted(self.action_type_timing.items(), key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0, reverse=True):
                if times:
                    avg = sum(times) / len(times)
                    max_time = max(times)
                    min_time = min(times)
                    logger.info(f"{action_type}: {len(times)} actions, {avg:.3f}s avg ({min_time:.3f}s - {max_time:.3f}s)")

        # Display any errors that occurred during evaluation
        if self.errors:
            logger.info(f"\n{'-' * 60}")
            logger.info(f"ERRORS ({len(self.errors)})")
            for i, error in enumerate(self.errors[:5]):  # Show first 5 errors only
                logger.info(f"{i + 1}. {error}")
            if len(self.errors) > 5:
                logger.info(f"... and {len(self.errors) - 5} more errors")

        logger.info(f"{'=' * 80}")

    def print_evaluation_summary(self):
        """Print a summary of all evaluations performed"""
        if self.evaluation_count == 0:
            logger.info("No evaluations performed yet")
            return

        # Group stats by task
        task_groups = defaultdict(list)
        for stat in self.evaluation_stats:
            task_groups[stat.task_id].append(stat)

        # For each task, display a summary
        logger.info(f"\n{'=' * 80}")
        logger.info("OVERALL EVALUATION SUMMARY")
        logger.info(f"{'=' * 80}")
        logger.info(f"Total solutions evaluated: {self.evaluation_count}")
        logger.info(f"Total evaluation time: {self.total_evaluation_time:.2f}s")

        for task_id, stats in task_groups.items():
            logger.info(f"\n{'-' * 60}")
            logger.info(f"Task: {task_id}")
            logger.info(f"Agents: {len(stats)}")

            # Group by agent type
            agent_types = defaultdict(list)
            for stat in stats:
                agent_type = stat.web_agent_id.split('-')[0] if '-' in stat.web_agent_id else stat.web_agent_id
                agent_types[agent_type].append(stat.final_score)

            # Display score by agent type
            for agent_type, scores in agent_types.items():
                avg_score = sum(scores) / len(scores)
                logger.info(f"  {agent_type}: {avg_score:.4f} avg score ({len(scores)} agents)")

        logger.info(f"{'=' * 80}")
