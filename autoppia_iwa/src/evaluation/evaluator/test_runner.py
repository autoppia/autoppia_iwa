from typing import List

from autoppia_iwa.src.data_generation.domain.classes import BaseTaskTest, Task
from autoppia_iwa.src.evaluation.classes import TestResult
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestRunner:
    def __init__(self, tests: List[BaseTaskTest]):
        self.tests = tests

    def run_tests(self, task: Task, browser_snapshots:List[BrowserSnapshot]) -> List[TestResult]:
        results = []
        for test in self.tests:
            success = test.execute_test(self.browser_snapshot)

            # Create TestResult instance with extra_data
            test_result = TestResult(
                is_success=success,
                extra_data={key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}},
            )
            results.append(test_result)

        return results
