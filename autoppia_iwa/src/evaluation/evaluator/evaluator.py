import asyncio
import hashlib
import traceback
from collections import defaultdict
from typing import List, Union

from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

from autoppia_iwa.src.backend_demo_web.backend_demo_web_service import BackendDemoWebService
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.evaluation.classes import EvaluationResult, Feedback
from autoppia_iwa.src.evaluation.evaluator.feedback_generator import FeedbackGenerator
from autoppia_iwa.src.evaluation.evaluator.test_runner import TestRunner
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution


class EvaluatorConfig(BaseModel):
    current_url: str
    save_results_in_db: bool = False
    task_delay_in_seconds: float = Field(default=0.2, gt=0, description="Delay between tasks in seconds")
    chunk_size: int = Field(default=3, gt=0, description="Number of tasks to process per chunk")
    browser_timeout: float = Field(default=10000, gt=0, description="Timeout for browser actions in milliseconds")
    event_monitor_interval: float = Field(default=0.1, gt=0, le=0.5, description="Interval in seconds to monitor events, must be > 0 and <= 0.5")


class ConcurrentEvaluator(IEvaluator):
    def __init__(self, config: EvaluatorConfig):
        """
        Initializes the evaluator with configuration settings.

        Args:
            config (EvaluatorConfig): Configuration object with parameters like concurrency limit, browser timeout, etc.
        """
        self.config = config

    async def evaluate_single_task(self, task_solution: TaskSolution) -> EvaluationResult:
        """
        Synchronously evaluates a single task (blocking). This method runs
        an internal event loop to call the async logic.

        Args:
            task_solution (TaskSolution): Contains task data, actions, and web_agent_id.

        Returns:
            EvaluationResult: The result of the evaluation.
        """
        return await self._evaluate_single_task(task_solution.task, task_solution.actions, task_solution.web_agent_id)

    async def evaluate_all_tasks(self, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        """
        Synchronously evaluates a list of tasks. Uses asyncio internally with a semaphore
        to limit the concurrency to the configured chunk_size.

        Args:
            task_solutions (List[TaskSolution]): List of tasks/responses from multiple miners.

        Returns:
            List[EvaluationResult]: Evaluation results for each web_agent response.
        """
        return await self._group_and_evaluate_tasks(task_solutions)

    async def _group_and_evaluate_tasks(self, task_solutions: List[TaskSolution]) -> List[EvaluationResult]:
        """
        Groups identical action lists from tasks and evaluates them only once.
        Assigns results to all tasks with the same actions.

        Args:
            task_solutions (List[TaskSolution]): List of web_agent responses containing tasks and actions.

        Returns:
            List[EvaluationResult]: Evaluation results for each web_agent response.
        """
        # Group tasks by the hash of their actions
        grouped_tasks = defaultdict(list)
        for task_solution in task_solutions:
            grouped_tasks[self._hash_actions(task_solution.actions)].append(task_solution)

        # Semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.config.chunk_size)

        # Create a list of coroutines to evaluate groups concurrently
        group_tasks = [self._evaluate_group_with_semaphore(group, semaphore) for group in grouped_tasks.values()]

        # Gather all results, handle exceptions if any
        raw_results = await asyncio.gather(*group_tasks, return_exceptions=True)

        final_results = []
        for result in raw_results:
            if isinstance(result, Exception):
                print(f"Exception occurred: {type(result).__name__}, {result}")
            else:
                final_results.extend(result)

        print(f"All tasks processed. Total tasks evaluated: {len(final_results)} / {len(task_solutions)}")
        return final_results

    async def _evaluate_group_with_semaphore(self, group: List[TaskSolution], semaphore: asyncio.Semaphore) -> List[EvaluationResult]:
        """
        Evaluates a group of tasks (with identical actions) concurrently using the semaphore.
        """
        async with semaphore:
            # Pick one representative web_agent response for the group to evaluate
            representative = group[0]
            try:
                result = await self._evaluate_single_task(representative.task, representative.actions, representative.web_agent_id)

                # Assign the result to all tasks in the group with their respective web_agent_id
                results = [{**result, "web_agent_id": task_solution.web_agent_id} for task_solution in group]

                return results
            except Exception as e:
                print(f"Error evaluating actions for group: {e}")
                print(traceback.format_exc())
                return [None] * len(group)

    @staticmethod
    def _hash_actions(actions: List[BaseAction]) -> str:
        """
        Generates a hash for a list of actions to identify identical action sets.

        Args:
            actions (List[Action]): List of actions to hash.]

        Returns:
            str: A unique hash for the action list.
        """
        try:
            return hashlib.sha256("|".join(str(action.model_dump()) for action in actions).encode()).hexdigest()
        except Exception:
            print("Error generating hash for actions.")
            return ""

    async def _evaluate_single_task(self, task: Task, actions: List[BaseAction], web_agent_id: str, delay: float = None) -> Union[EvaluationResult, dict]:
        """
        Asynchronously evaluates a single task:
          1) Resets events in the backend
          2) Executes actions in a headless browser
          3) Runs the tests on each snapshot
          4) Generates feedback
          5) Returns an EvaluationResult (or a dict if save_results_in_db=True)

        Args:
            task (Task): The task to be evaluated.
            actions (List[Action]): The actions the web_agent proposes.
            web_agent_id (str): Unique identifier for the web_agent.
            delay (float): Optional delay before starting.

        Returns:
            EvaluationResult or dict: If save_results_in_db=True, returns a dict from .model_dump().
                                          Otherwise, returns an EvaluationResult.
        """
        if not actions:
            return EvaluationResult(final_score=0, test_results=[], feedback=None, execution_history=[])

        if delay:
            await asyncio.sleep(delay)

        # Step 0: Reset backend events for a clean start
        backend_service = BackendDemoWebService(task.url)
        backend_service.reset_backend_events_db(web_agent_id)

        # Step 1: Execute actions via browser
        execution_history = await self._evaluate_in_browser(task, web_agent_id, actions, backend_service)

        # Step 2: Run tests on each snapshot
        test_results = self._run_tests(task, execution_history)

        # Step 3: Generate feedback
        feedback = self._generate_feedback(task, execution_history, test_results)

        # Build final result
        result = EvaluationResult(
            final_score=feedback.final_score,
            test_results=test_results,
            feedback=feedback,
            execution_history=execution_history,
        )

        # If config says we save to DB, return a dict for JSON serialization
        return result.model_dump() if self.config.save_results_in_db else result

    async def _evaluate_in_browser(self, task: Task, web_agent_id: str, actions: List[BaseAction], backend_service: BackendDemoWebService) -> List[ActionExecutionResult]:
        """
        Launches a headless browser with Playwright, executes the actions,
        and returns ActionExecutionResults.

        Args:
            task (Task): The task associated with these actions.
            web_agent_id (str): ID for the web_agent.
            actions (List[Action]): List of actions to execute in the

        Returns:
            List[ActionExecutionResult]: The results, including snapshots/logs for each action.
        """
        async with async_playwright() as playwright:
            browser, context = None, None
            try:
                browser = await playwright.chromium.launch(headless=False)
                context = await browser.new_context(extra_http_headers={"X-WebAgent-Id": web_agent_id})
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()
                print(f"Started evaluation for task URL: {task.url}, Miner ID: {web_agent_id}")

                # Start monitoring for frame navigations
                monitor_task = asyncio.create_task(self._monitor_browser(task.url, page, web_agent_id))
                browser_specs = BrowserSpecification()
                browser_executor = PlaywrightBrowserExecutor(browser_specs, backend_service, page)

                try:
                    results = await browser_executor.execute_actions_standalone(actions, web_agent_id)
                finally:
                    # Cancel monitor task to stop any background loops
                    monitor_task.cancel()
                    await asyncio.gather(monitor_task, return_exceptions=True)

                print(f"Completed evaluation for task URL: {task.url}, Miner ID: {web_agent_id}")
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
        """
        Monitors URL or frame changes asynchronously, sending a page_view_event whenever
        a navigation occurs.

        Args:
            task_url (str): The reference URL of the task.
            page: The Playwright Page object.
            web_agent_id (str): ID of the web_agent who is being evaluated.
        """

        def on_frame_navigated(frame):
            try:
                if frame.url:
                    # Asynchronously send a page_view event
                    asyncio.create_task(BackendDemoWebService(task_url).send_page_view_event(frame.url, web_agent_id))
            except Exception as e:
                print(f"Error handling frame navigation: {e}")

        page.on("framenavigated", on_frame_navigated)

        # Keep monitoring until the page is closed or the task is cancelled
        try:
            while not page.is_closed():
                await asyncio.sleep(self.config.event_monitor_interval)
        except asyncio.CancelledError:
            print("Monitoring stopped.")

    @staticmethod
    def _run_tests(task: Task, execution_history: List[ActionExecutionResult]) -> List:
        """
        Runs tests on each action snapshot in the execution history.

        Args:
            task (Task): The task, which includes test definitions.
            execution_history (List[ActionExecutionResult]): Snapshots and logs from the

        Returns:
            List: Aggregated test results across all actions.
        """
        all_test_results = []
        for action_result in execution_history:
            snapshot = action_result.browser_snapshot
            test_runner = TestRunner(task.tests, snapshot)
            all_test_results.extend(test_runner.run_tests())

        return all_test_results

    @staticmethod
    def _generate_feedback(task: Task, execution_history: List[ActionExecutionResult], test_results: List) -> Feedback:
        """
        Generates feedback based on the entire run of actions/tests.

        Args:
            task (Task): The original Task.
            execution_history (List[ActionExecutionResult]): Action results from the
            test_results (List): List of all test outcomes.

        Returns:
            Feedback: A structured feedback object with messages and possibly a final score.
        """
        return FeedbackGenerator().generate_feedback(task_prompt=task.prompt, execution_history=execution_history, test_results=test_results)
