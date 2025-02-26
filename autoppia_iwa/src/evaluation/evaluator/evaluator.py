import asyncio
from dependency_injector.wiring import Provide
import hashlib
import time
import traceback
from collections import defaultdict
from typing import List, Optional, Dict, Tuple
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from loguru import logger
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.evaluation.classes import EvaluationResult as BaseEvaluationResult, TestResult
from autoppia_iwa.src.evaluation.classes import Feedback
from autoppia_iwa.src.evaluation.evaluator.feedback_generator import FeedbackGenerator
from autoppia_iwa.src.evaluation.evaluator.test_runner import TestRunner
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.config.config import EVALUATOR_HEADLESS
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent


class EvaluationResult(BaseEvaluationResult):
    web_agent_id: Optional[str] = None
    raw_score: float = 0.0
    random_clicker_score: float = 0.0
    random_passed_tests: List[int] = Field(default_factory=list)
    evaluation_time: float = 0.0  # Time taken to evaluate this solution


class EvaluatorConfig(BaseModel):
    save_results_in_db: bool = False
    task_delay_in_seconds: float = Field(default=0.2, gt=0)
    chunk_size: int = Field(default=5, gt=0)
    browser_timeout: float = Field(default=10000, gt=0)
    event_monitor_interval: float = Field(default=0.1, gt=0, le=0.5)
    enable_grouping_tasks: bool = Field(default=True)
    exclude_random_passed_tests: bool = Field(default=True)
    cache_random_clicker_results: bool = Field(default=True)
    normalize_scores: bool = Field(default=True)
    verbose_logging: bool = Field(default=True)  # Control detailed logging


class ConcurrentEvaluator(IEvaluator):
    def __init__(self, web_project, config: EvaluatorConfig):
        self.config = config
        self._random_clicker_cache: Dict[str, Tuple[List[int], float]] = {}
        self.total_evaluation_time = 0.0
        self.evaluation_count = 0
        self.web_project = web_project
        self.backend_demo_webs_service:BackendDemoWebService = BackendDemoWebService(web_project=web_project)

    async def evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Evaluate a single task solution given both the task and task solution.
        Args:
            task: The Task object containing task details
            task_solution: The TaskSolution object with actions and web_agent_id
        Returns:
            EvaluationResult: The evaluation result
        """
        result = await self._evaluate_single_task_solution(task, task_solution)
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
        result = await self._group_and_evaluate_task_solutions(task, task_solutions)
        await self.backend_demo_webs_service.close()
        return result

    async def _group_and_evaluate_task_solutions(self, task: Task, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        start_time = time.time()
        logger.info(f"Starting evaluation for task {task.id} with {len(task_solutions)} solutions")
        # Group task solutions by action hash
        grouped_tasks = defaultdict(list)
        if self.config.enable_grouping_tasks:
            for task_solution in task_solutions:
                grouped_tasks[self._hash_actions(task_solution.actions)].append(task_solution)
            logger.info(f"Grouped {len(task_solutions)} task solutions into {len(grouped_tasks)} unique action groups")
        else:
            for i, task_solution in enumerate(task_solutions):
                unique_hash = self._hash_actions(task_solution.actions) + f"_{i}"
                grouped_tasks[unique_hash].append(task_solution)
        # Use semaphore to limit concurrent evaluations
        semaphore = asyncio.Semaphore(self.config.chunk_size)
        group_tasks = [self._evaluate_group_with_semaphore(task, group, semaphore) for group in grouped_tasks.values()]
        # Gather all results
        raw_results = await asyncio.gather(*group_tasks, return_exceptions=True)
        final_results = []
        exceptions_count = 0
        for result in raw_results:
            if isinstance(result, Exception):
                exceptions_count += 1
                logger.error(f"Exception occurred: {type(result).__name__}, {result}")
                logger.error(traceback.format_exc())
            else:
                final_results.extend(result)
        total_time = time.time() - start_time
        self.total_evaluation_time += total_time
        self.evaluation_count += len(final_results)
        avg_time_per_solution = total_time / max(1, len(final_results))
        logger.success(f"✅ All tasks processed. Total solutions evaluated: {len(final_results)}/{len(task_solutions)}")
        logger.info(f"⏱️ Evaluation time: {total_time:.2f}s total, {avg_time_per_solution:.2f}s per solution")
        logger.warning(f"⚠️ Exceptions: {exceptions_count}")
        # Calculate and display average scores
        if final_results:
            avg_raw_score = sum(r.raw_score for r in final_results) / len(final_results)
            avg_final_score = sum(r.final_score for r in final_results) / len(final_results)
            logger.info(f"📊 Average raw score: {avg_raw_score:.4f}, Average final score: {avg_final_score:.4f}")
        return final_results

    async def _evaluate_group_with_semaphore(self, task: Task, group: List[TaskSolution], semaphore: asyncio.Semaphore) -> List[EvaluationResult]:
        async with semaphore:
            representative = group[0]
            evaluation_start = time.time()
            try:
                # Evaluate the representative actions
                rep_result = await self._evaluate_single_task_solution(task, representative)
                evaluation_time = time.time() - evaluation_start
                rep_result.evaluation_time = evaluation_time
                # Clone results for each web_agent in the group
                results: List[EvaluationResult] = []
                for task_solution in group:
                    cloned_result = rep_result.model_copy(deep=True)
                    cloned_result.web_agent_id = task_solution.web_agent_id
                    results.append(cloned_result)
                logger.info(f"Group evaluation completed in {evaluation_time:.2f}s for {len(group)} solutions")
                return results
            except Exception as e:
                logger.error(f"Error evaluating actions for group: {e}")
                logger.error(traceback.format_exc())
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
                        evaluation_time=time.time() - evaluation_start
                    ) for ts in group
                ]

    @staticmethod
    def _hash_actions(actions: List[BaseAction]) -> str:
        try:
            return hashlib.sha256("|".join(str(action.model_dump()) for action in actions).encode()).hexdigest()
        except Exception:
            logger.error("Error generating hash for actions.")
            return ""

    async def _evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution, delay: float = None) -> EvaluationResult:
        """
        Evaluate a single task solution.
        Args:
            task: The Task object containing task details
            task_solution: The TaskSolution object with actions and web_agent_id
            delay: Optional delay between actions
        Returns:
            EvaluationResult: The evaluation result
        """
        actions = task_solution.actions
        web_agent_id = task_solution.web_agent_id
        is_web_real = task.is_web_real
        solution_start_time = time.time()
        logger.info(f"⚙️ Evaluating task: {task.id}, Web Agent ID: {web_agent_id}, Actions: {len(actions)}")
        if not actions:
            logger.warning(f"No actions provided for task {task.id}. Returning default result.")
            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                random_clicker_score=0,
                test_results_matrix=[],
                feedback=None,
                execution_history=[],
                random_passed_tests=[],
                evaluation_time=0
            )
        if delay:
            await asyncio.sleep(delay)
        # First evaluate the agent's actions
        browser_start_time = time.time()

        if not is_web_real:
            await self.backend_demo_webs_service.reset_backend_events_db(web_agent_id)

        # Execute agent actions in browser
        execution_history: List[ActionExecutionResult] = await self._evaluate_in_browser(
            task, web_agent_id, actions, is_web_real
        )
        browser_time = time.time() - browser_start_time
        logger.info(f"Browser execution completed in {browser_time:.2f}s")
        # Run tests on agent's actions
        test_start_time = time.time()
        test_results_matrix: List[List[TestResult]] = self._run_tests(task, execution_history)
        test_time = time.time() - test_start_time
        # Format and print test results matrix
        logger.info(f"Tests completed in {test_time:.2f}s")
        self._print_test_matrix(f"Agent: {web_agent_id}", test_results_matrix)
        # Get or compute random clicker performance for baseline score
        random_start_time = time.time()
        random_passed_tests, random_clicker_score = await self._get_random_clicker_performance(task)
        random_time = time.time() - random_start_time
        logger.info(f"Random clicker evaluation completed in {random_time:.2f}s")
        # Calculate agent's raw score (without accounting for random clicker)
        raw_score = 0
        tests_passed_count = 0
        num_tests = 0
        if test_results_matrix and test_results_matrix[0]:
            # Get the number of tests (columns in the matrix)
            num_tests = len(test_results_matrix[0])
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
        # Calculate final adjusted score by subtracting random clicker score
        final_score = raw_score
        # Adjust score by subtracting random clicker score
        if self.config.exclude_random_passed_tests and num_tests > 0:
            # Simple subtraction approach: agent score - random clicker score
            # If result is negative, set to 0
            final_score = max(0, raw_score - random_clicker_score)
            # Option to normalize the result to a 0-1 scale
            if self.config.normalize_scores and random_clicker_score < 1.0:  # Avoid division by zero if random gets everything
                # Normalize to range from 0.0 to 1.0
                # This maps the possible score range (random_score to 1.0) to (0.0 to 1.0)
                normalized_score = final_score / (1.0 - random_clicker_score)
                final_score = normalized_score
        total_evaluation_time = time.time() - solution_start_time
        # Print summary of performance statistics
        self._print_performance_summary(
            web_agent_id, raw_score, random_clicker_score, final_score, 
            tests_passed_count, num_tests, total_evaluation_time,
            browser_time, test_time, random_time
        )
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
            evaluation_time=total_evaluation_time
        )
        if self.config.save_results_in_db:
            logger.info(f"Saving result for Web Agent {web_agent_id} to DB")
        return result

    def _print_performance_summary(self, web_agent_id, raw_score, random_clicker_score, final_score,
                                   tests_passed_count, num_tests, total_time, browser_time, test_time, random_time):
        """Print a formatted summary of agent performance"""
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 PERFORMANCE SUMMARY FOR AGENT: {web_agent_id}")
        logger.info("-" * 80)
        logger.info(f"🎯 Test Results: {tests_passed_count}/{num_tests} tests passed ({raw_score:.4f})")
        logger.info(f"🎲 Random Clicker: {random_clicker_score:.4f}")
        logger.info(f"⭐ Final Adjusted Score: {final_score:.4f}")
        logger.info("-" * 80)
        logger.info(f"⏱️ Evaluation time breakdown:")
        logger.info(f"   - Browser execution: {browser_time:.2f}s ({browser_time/total_time*100:.1f}%)")
        logger.info(f"   - Test execution:    {test_time:.2f}s ({test_time/total_time*100:.1f}%)")
        logger.info(f"   - Random evaluation: {random_time:.2f}s ({random_time/total_time*100:.1f}%)")
        logger.info(f"   - Total time:        {total_time:.2f}s")
        logger.info("=" * 80 + "\n")

    def _print_test_matrix(self, title, test_matrix):
        """Print a formatted test matrix with colored output"""
        if not test_matrix or not test_matrix[0]:
            logger.info(f"{title}: No test results available")
            return
        rows = len(test_matrix)
        cols = len(test_matrix[0])
        logger.info(f"\n📋 TEST MATRIX: {title}")
        logger.info(f"Actions: {rows}, Tests: {cols}")
        # Create header row
        header = "Action |" + "".join(f" T{i+1:02d} |" for i in range(cols))
        logger.info("-" * len(header))
        logger.info(header)
        logger.info("-" * len(header))
        # Create rows with colored status
        for i, row in enumerate(test_matrix):
            row_str = f"{i+1:6d} |"
            for result in row:
                if result.success:
                    row_str += "  ✅  |"
                else:
                    row_str += "  ❌  |"
            logger.info(row_str)
        logger.info("-" * len(header))
        # Create summary row showing which tests passed at least once
        summary = "Result |"
        passed_count = 0
        for col in range(cols):
            passed = any(test_matrix[row][col].success for row in range(rows))
            if passed:
                summary += "  ✅  |"
                passed_count += 1
            else:
                summary += "  ❌  |"
        logger.info(summary)
        logger.info("-" * len(header))
        logger.info(f"Passed: {passed_count}/{cols} tests ({passed_count/cols*100:.1f}%)")
        logger.info("")

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
            logger.info(f"Using cached random clicker results for task {task.id}")
            return self._random_clicker_cache[task.id]
        logger.info(f"Random clicker cache miss for task {task.id} - running new evaluation")
        random_start_time = time.time()

        # Generate random clicker actions
        random_clicker = RandomClickerWebAgent(name="Random-clicker")
        task_solution = await random_clicker.solve_task(task=task)
        random_actions = task_solution.actions

        # Exit early if no actions were generated
        if not random_actions:
            logger.warning("Random clicker generated no actions")
            return [], 0.0

        # Create a temporary web_agent_id for the random clicker
        random_web_agent_id = f"random-clicker-{task.id}"

        # Execute random clicker actions
        logger.info(f"Executing {len(random_actions)} random clicker actions")

        if not task.is_web_real:
            await self.backend_demo_webs_service.reset_backend_events_db(random_web_agent_id)
        random_execution_history = await self._evaluate_in_browser(
            task, random_web_agent_id, random_actions, task.is_web_real
        )

        # Run tests on random clicker actions
        random_test_results = self._run_tests(task, random_execution_history)
        self._print_test_matrix("Random Clicker", random_test_results)

        # Calculate which tests the random clicker passed
        random_passed_tests = []
        random_score = 0.0
        if random_test_results and random_test_results[0]:
            num_tests = len(random_test_results[0])
            passed_count = 0
            # For each test, check if random clicker passed it
            for test_index in range(num_tests):
                test_passed = False
                for action_index in range(len(random_test_results)):
                    if random_test_results[action_index][test_index].success:
                        random_passed_tests.append(test_index)
                        passed_count += 1
                        test_passed = True
                        break
            if num_tests > 0:
                random_score = passed_count / num_tests
        random_time = time.time() - random_start_time
        logger.info(f"Random clicker evaluation completed in {random_time:.2f}s with score {random_score:.4f}")
        # Cache the results
        if self.config.cache_random_clicker_results:
            logger.info(f"Caching random clicker results for task {task.id}")
            self._random_clicker_cache[task.id] = (random_passed_tests, random_score)
        return random_passed_tests, random_score

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: List[BaseAction], is_web_real: bool) -> List[ActionExecutionResult]:
        """
        Execute actions in a browser and get the results.
        Args:
            task: The task being evaluated
            web_agent_id: ID of the web agent
            actions: List of actions to execute
            backend_demo_webs_service: Service for interacting with backend
            is_web_real: Whether the web is real or simulated
        Returns:
            List[ActionExecutionResult]: Results of executing each action
        """
        browser_start_time = time.time()
        logger.info(f"Starting browser evaluation for {len(actions)} actions")
        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS)
                context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()
                logger.info(f"Browser launched for task URL: {task.url}, Agent ID: {web_agent_id}")
                monitor_task = None
                if not is_web_real:
                    monitor_task = asyncio.create_task(self._monitor_browser(self.web_project, task.url, page, web_agent_id))
                browser_executor = PlaywrightBrowserExecutor(BrowserSpecification(), page, self.backend_demo_webs_service)
                action_times = []
                action_start = time.time()
                try:
                    results = await browser_executor.execute_actions_standalone(actions, web_agent_id, is_web_real=is_web_real)
                    # Calculate individual action execution times if results available
                    if results:
                        for i, result in enumerate(results):
                            action_end = time.time()
                            action_time = action_end - action_start
                            action_times.append(action_time)
                            logger.debug(f"Action {i+1}/{len(actions)} executed in {action_time:.3f}s")
                            action_start = action_end
                finally:
                    if not is_web_real and monitor_task:
                        monitor_task.cancel()
                        await asyncio.gather(monitor_task, return_exceptions=True)
                browser_time = time.time() - browser_start_time
                avg_action_time = sum(action_times) / max(len(action_times), 1)
                logger.info(f"Browser evaluation completed in {browser_time:.2f}s, avg action time: {avg_action_time:.3f}s")
                return results
            except Exception as e:
                logger.error(f"Error during browser evaluation for task URL: {task.url}, Agent ID: {web_agent_id}")
                logger.error(f"Exception: {e}")
                logger.error(traceback.format_exc())
                return []
            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()
        # Fixed monitor_browser method

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
                asyncio.create_task(
                    _handle_frame_navigation(web_project, frame.url, task_url, web_agent_id)
                )

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
            test_results = test_runner.run_tests(
                prompt=task.prompt, 
                snapshot=snapshot, 
                browser_snapshots=browser_snapshots,
                current_action_index=i
            )
            # Add the results for this snapshot to the matrix
            test_results_matrix.append(test_results)
        return test_results_matrix

    @staticmethod
    def _generate_feedback(task: Task, execution_history: List[ActionExecutionResult], 
                           test_results_matrix: List[List[TestResult]]) -> Feedback:
        """
        Generate feedback based on test results.
        Args:
            task: The task being evaluated
            execution_history: History of executed actions
            test_results_matrix: Matrix of test results
        Returns:
            Feedback: Generated feedback
        """
        return FeedbackGenerator.generate_feedback(
            task_prompt=task.prompt, 
            execution_history=execution_history, 
            test_results_matrix=test_results_matrix
        )

    def print_evaluation_summary(self):
        """Print a summary of all evaluations performed"""
        if self.evaluation_count == 0:
            logger.info("No evaluations performed yet")
            return
        avg_time = self.total_evaluation_time / self.evaluation_count
        logger.info("\n" + "=" * 80)
        logger.info("📊 OVERALL EVALUATION SUMMARY")
        logger.info("-" * 80)
        logger.info(f"Total solutions evaluated: {self.evaluation_count}")
        logger.info(f"Total evaluation time: {self.total_evaluation_time:.2f}s")
        logger.info(f"Average time per solution: {avg_time:.2f}s")
        logger.info("=" * 80 + "\n")
