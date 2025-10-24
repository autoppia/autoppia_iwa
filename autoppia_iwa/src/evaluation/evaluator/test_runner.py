from loguru import logger

from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest


def _log_backend_test(message: str):
    """Helper function to log backend test messages with EVALUATION level"""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_backend_test
        log_backend_test(message)
    except ImportError:
        # Fallback to regular debug logging if import fails
        logger.debug(f"[GET BACKEND TEST] {message}")


from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject
from autoppia_iwa.src.evaluation.classes import TestResult
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestRunner:
    def __init__(self, tests: list[BaseTaskTest]):
        self.tests = tests

    async def run_partial_tests(
        self,
        web_project: WebProject,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
        current_action_index: int | None = None,
        total_iterations: int | None = None,
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
        for test_idx, test in enumerate(self.tests, 1):
            from loguru import logger

            logger.info(f"  🧪 Running Test {test_idx}/{len(self.tests)}: {test.type}")
            logger.info(f"     Description: {test.description}")
            logger.info(f"     Criteria: {getattr(test, 'event_criteria', 'N/A')}")

            success = await test.execute_test(
                web_project=web_project,
                current_iteration=current_action_index,
                prompt=prompt,
                snapshot=snapshot,
                browser_snapshots=browser_snapshots,
                total_iterations=total_iterations,
            )

            # Log test result
            if success:
                logger.info(f"  ✅ Test {test_idx} PASSED")
            else:
                logger.warning(f"  ❌ Test {test_idx} FAILED")

            # Create TestResult instance with extra_data
            test_result = TestResult(
                success=success,
                extra_data={key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}},
            )
            snapshot_results.append(test_result)

        return snapshot_results

    async def run_global_tests(
        self,
        backend_events: list[BackendEvent] | None = None,
    ) -> list[TestResult]:
        """
        Run all tests after executing the
        """
        # 🔍 DEBUG: Log test execution details
        _log_backend_test("🔍 DEBUG - TestRunner.run_global_tests:")
        _log_backend_test(f"   - Number of tests to run: {len(self.tests)}")
        _log_backend_test(f"   - Backend events available: {len(backend_events) if backend_events else 0}")

        snapshot_results = []  # Store results for this snapshot
        for test_idx, test in enumerate(self.tests, 1):
            test_name = getattr(test, "event_name", "Unknown")
            test_criteria = getattr(test, "event_criteria", {})

            _log_backend_test(f"   🧪 Test {test_idx}/{len(self.tests)}: {test_name}")
            _log_backend_test(f"      - Criteria: {test_criteria}")
            _log_backend_test(f"      - Test type: {type(test).__name__}")
            _log_backend_test(f"      - Test description: {getattr(test, 'description', 'No description')}")

            # 🔍 DEBUG: Log what we're looking for vs what we have
            if backend_events:
                for event_idx, event in enumerate(backend_events, 1):
                    _log_backend_test(f"      - Available Event {event_idx}: {event.event_name if hasattr(event, 'event_name') else 'unknown'}")
                    _log_backend_test(f"         - Event data: {getattr(event, 'data', 'No data')}")
                    _log_backend_test(f"         - Event metadata: {getattr(event, 'metadata', 'No metadata')}")
                    _log_backend_test(f"         - Event attributes: {vars(event)}")

            success = await test.execute_global_test(
                backend_events=backend_events,
            )

            _log_backend_test(f"      - Result: {'✅ PASSED' if success else '❌ FAILED'}")

            # Create TestResult instance with extra_data
            test_result = TestResult(
                success=success,
                extra_data={key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}},
            )
            snapshot_results.append(test_result)

        _log_backend_test(f"   - Total results: {len(snapshot_results)}")
        return snapshot_results
