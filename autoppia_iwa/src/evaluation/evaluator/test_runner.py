from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.classes import TestResult
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestRunner:
    def __init__(self, tests: list[BaseTaskTest]):
        self.tests = tests

    async def run_tests(
        self,
        web_project: WebProject,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
        current_action_index: int,
        total_iterations: int,
    ) -> list[TestResult]:
        """
        Run all tests for a single snapshot (after a single action).

        Args:
            web_project: The web project being tested.
            prompt: The task prompt.
            snapshot: The current browser snapshot.
            browser_snapshots: All browser snapshots up to the current one.
            current_action_index: Index of the current action.
            total_iterations: Total number of iterations in the test process.

        Returns:
            List[TestResult]: Results of all tests for the current snapshot.
        """
        snapshot_results = []  # Store results for this snapshot
        for test in self.tests:
            success = await test.execute_test(
                web_project=web_project,
                current_iteration=current_action_index,
                prompt=prompt,
                snapshot=snapshot,
                browser_snapshots=browser_snapshots,
                total_iterations=total_iterations,
            )

            # Create TestResult instance with extra_data
            test_result = TestResult(
                success=success,
                extra_data={key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}},
            )
            snapshot_results.append(test_result)

        return snapshot_results
