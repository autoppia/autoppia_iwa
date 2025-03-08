# Corrected TestRunner class
from typing import List

from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest, JudgeBaseOnScreenshot
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.classes import TestResult
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestRunner:
    def __init__(self, tests: List[BaseTaskTest]):
        self.tests = tests

    def run_tests(
        self,
        web_project: WebProject,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        current_action_index: int,
        total_iterations: int,
    ) -> List[TestResult]:
        """
        Run all tests for a single snapshot (after a single action).

        Args:
            prompt: The task prompt.
            snapshot: The current browser snapshot.
            browser_snapshots: All browser snapshots up to the current one.
            current_action_index: Index of the current action.
            total_iterations: Total number of iterations in the test process.

        Returns:
            List[TestResult]: Results of all tests for the current snapshot.
        """
        snapshot_results = []

        for test in self.tests:
            # Run all tests normally
            if not isinstance(test, JudgeBaseOnScreenshot) or current_action_index < total_iterations - 1:
                result = self._execute_test(web_project, test, prompt, snapshot, browser_snapshots, current_action_index, total_iterations)
                snapshot_results.append(result)

        # Run JudgeBaseOnScreenshot only at the last iteration
        if current_action_index == total_iterations - 1:
            for test in self.tests:
                if isinstance(test, JudgeBaseOnScreenshot):
                    result = self._execute_test(web_project, test, prompt, snapshot, browser_snapshots, current_action_index, total_iterations)
                    snapshot_results.append(result)

        return snapshot_results

    def _execute_test(
        self,
        web_project: WebProject,
        test: BaseTaskTest,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        current_action_index: int,
        total_iteratios: int,
    ) -> TestResult:
        """Helper function to execute a test and return a TestResult object."""
        success = test.execute_test(
            web_project=web_project, current_iteration=current_action_index, prompt=prompt, snapshot=snapshot, browser_snapshots=browser_snapshots, total_iteratios=total_iteratios
        )
        return TestResult(
            success=success,
            extra_data={key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}},
        )
