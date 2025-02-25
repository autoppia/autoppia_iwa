import asyncio
import hashlib
import time
import traceback
from collections import defaultdict
from typing import List, Optional, Dict, Tuple
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
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
    # Extend the base model if needed to hold the web_agent_id
    web_agent_id: Optional[str] = None
    # Add fields to track original and adjusted scores
    raw_score: float = 0.0
    random_clicker_score: float = 0.0
    random_passed_tests: List[int] = Field(default_factory=list)


class EvaluatorConfig(BaseModel):
    save_results_in_db: bool = False
    task_delay_in_seconds: float = Field(default=0.2, gt=0)
    chunk_size: int = Field(default=5, gt=0)
    browser_timeout: float = Field(default=10000, gt=0)
    event_monitor_interval: float = Field(default=0.1, gt=0, le=0.5)
    enable_grouping_tasks: bool = Field(default=True)
    # Add configuration for random clicker evaluation
    exclude_random_passed_tests: bool = Field(default=True)
    cache_random_clicker_results: bool = Field(default=True)
    normalize_scores: bool = Field(default=True)  # Whether to normalize scores after subtraction


class ConcurrentEvaluator(IEvaluator):
    def __init__(self, config: EvaluatorConfig):
        self.config = config
        # Cache for random clicker results by task ID
        self._random_clicker_cache: Dict[str, Tuple[List[int], float]] = {}

    async def evaluate_single_task(self, task_solution: TaskSolution) -> EvaluationResult:
        return await self._evaluate_single_task(task_solution)

    async def evaluate_all_tasks(self, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        return await self._group_and_evaluate_tasks(task_solutions)

    async def _group_and_evaluate_tasks(self, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        start_time = time.time()
        grouped_tasks = defaultdict(list)
        if self.config.enable_grouping_tasks:
            for task_solution in task_solutions:
                grouped_tasks[self._hash_actions(task_solution.actions)].append(task_solution)
        else:
            for i, task_solution in enumerate(task_solutions):
                unique_hash = self._hash_actions(task_solution.actions) + f"_{i}"
                grouped_tasks[unique_hash].append(task_solution)

        semaphore = asyncio.Semaphore(self.config.chunk_size)
        group_tasks = [self._evaluate_group_with_semaphore(group, semaphore) for group in grouped_tasks.values()]
        raw_results = await asyncio.gather(*group_tasks, return_exceptions=True)

        final_results = []
        for result in raw_results:
            if isinstance(result, Exception):
                print(f"Exception occurred: {type(result).__name__}, {result}")
            else:
                final_results.extend(result)

        print(f"All tasks processed. Total tasks evaluated: {len(final_results)} / {len(task_solutions)}")
        print(f"Evaluation took {time.time() - start_time}s")
        return final_results

    async def _evaluate_group_with_semaphore(self, group: List[TaskSolution], semaphore: asyncio.Semaphore) -> List[EvaluationResult]:
        async with semaphore:
            representative = group[0]
            try:
                # Evaluate the representative actions
                rep_result = await self._evaluate_single_task(representative)

                # Clone results for each web_agent in the group
                results: List[EvaluationResult] = []
                for task_solution in group:
                    cloned_result = rep_result.model_copy(deep=True)
                    cloned_result.web_agent_id = task_solution.web_agent_id
                    results.append(cloned_result)

                return results
            except Exception as e:
                print(f"Error evaluating actions for group: {e}")
                print(traceback.format_exc())
                return [
                    EvaluationResult(
                        web_agent_id=ts.web_agent_id,
                        final_score=0,
                        raw_score=0,
                        random_clicker_score=0,
                        test_results_matrix=[],
                        feedback=None,
                        execution_history=[],
                        random_passed_tests=[]
                    ) for ts in group
                ]

    @staticmethod
    def _hash_actions(actions: List[BaseAction]) -> str:
        try:
            return hashlib.sha256("|".join(str(action.model_dump()) for action in actions).encode()).hexdigest()
        except Exception:
            print("Error generating hash for actions.")
            return ""

    async def _evaluate_single_task(self, task_solution: TaskSolution, delay: float = None) -> EvaluationResult:
        task = task_solution.task
        actions = task_solution.actions
        web_agent_id = task_solution.web_agent_id
        is_web_real = task.is_web_real

        print(f"Evaluating task: {task.id}, Web Agent ID: {web_agent_id}, Is Web Real: {is_web_real}")

        if not actions:
            print(f"No actions provided for task {task.id}. Returning default result.")
            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                random_clicker_score=0,
                test_results_matrix=[],
                feedback=None,
                execution_history=[],
                random_passed_tests=[]
            )

        if delay:
            await asyncio.sleep(delay)

        # First evaluate the agent's actions
        backend_service = BackendDemoWebService(task.url)
        if not is_web_real:
            backend_service.reset_backend_events_db(web_agent_id)

        # Execute agent actions in browser
        execution_history: List[ActionExecutionResult] = await self._evaluate_in_browser(
            task, web_agent_id, actions, backend_service, is_web_real
        )

        # Run tests on agent's actions
        test_results_matrix: List[List[TestResult]] = self._run_tests(task, execution_history)

        print(f"=== Test Result Matrix for AgentID: {task_solution.web_agent_id} ===")
        for row in test_results_matrix:
            print([result.success for result in row])
        print("===========================")

        # Get or compute random clicker performance
        random_passed_tests, random_clicker_score = await self._get_random_clicker_performance(task)

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

            print(f"Random clicker score: {random_clicker_score:.4f}")
            print(f"Agent raw score: {raw_score:.4f}")
            print(f"Adjusted score (raw - random): {final_score:.4f}")
        else:
            print(f"Final score: {final_score:.4f} ({tests_passed_count}/{num_tests} tests passed)")

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
            random_passed_tests=random_passed_tests
        )

        if self.config.save_results_in_db:
            print(f"Saving result for Web Agent {web_agent_id} to DB")

        return result

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
        backend_service = BackendDemoWebService(task.url)
        if not task.is_web_real:
            backend_service.reset_backend_events_db(random_web_agent_id)

        random_execution_history = await self._evaluate_in_browser(
            task, random_web_agent_id, random_actions, backend_service, task.is_web_real
        )

        # Run tests on random clicker actions
        random_test_results = self._run_tests(task, random_execution_history)

        print("=== Random Clicker Test Results Matrix ===")
        for row in random_test_results:
            print([result.success for result in row])
        print("=========================================")

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

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: List[BaseAction], 
                                   backend_service: BackendDemoWebService, is_web_real: bool) -> List[ActionExecutionResult]:
        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS)
                context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()
                print(f"Started evaluation for task URL: {task.url}, Miner ID: {web_agent_id}")

                if not is_web_real:
                    monitor_task = asyncio.create_task(self._monitor_browser(task.url, page, web_agent_id))

                browser_executor = PlaywrightBrowserExecutor(BrowserSpecification(), backend_service, page)
                try:
                    results = await browser_executor.execute_actions_standalone(actions, web_agent_id, is_web_real=is_web_real)
                finally:
                    if not is_web_real:
                        monitor_task.cancel()
                        await asyncio.gather(monitor_task, return_exceptions=True)

                return results
            except Exception as e:
                print(f"Error during browser evaluation for task URL: {task.url}, Miner ID: {web_agent_id}")
                print(f"Exception: {e}__{traceback.format_exc()}")
                return []
            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()

    async def _monitor_browser(self, task_url, page, web_agent_id):
        def on_frame_navigated(frame):
            try:
                if frame.url:
                    asyncio.create_task(BackendDemoWebService(task_url).send_page_view_event(frame.url, web_agent_id))
            except Exception as e:
                print(f"Error handling frame navigation: {e}")

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
        return FeedbackGenerator.generate_feedback(
            task_prompt=task.prompt, 
            execution_history=execution_history, 
            test_results_matrix=test_results_matrix
        )
