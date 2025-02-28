# Corrected TestRunner class
from typing import List
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.evaluation.classes import TestResult
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestRunner:
    def __init__(self, tests: List[BaseTaskTest]):
        self.tests = tests

    def run_tests(self, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot], current_action_index: int) -> List[TestResult]:
        """
        Run all tests for a single snapshot (after a single action).

        Args:
            prompt: The task prompt
            snapshot: The current browser snapshot
            browser_snapshots: All browser snapshots up to the current one
            current_action_index: Index of the current action (for tracking test progress)

        Returns:
            List[TestResult]: Results of all tests for the current snapshot
        """
        snapshot_results = []  # Store results for this snapshot
        for test in self.tests:
            success = test.execute_test(current_iteration=current_action_index, prompt=prompt, snapshot=snapshot, browser_snapshots=browser_snapshots)
            # Create TestResult instance with extra_data
            test_result = TestResult(
                success=success,
                extra_data={key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}},
            )
            snapshot_results.append(test_result)
        return snapshot_results
