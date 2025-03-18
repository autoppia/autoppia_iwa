from autoppia_iwa.src.evaluation.classes import Feedback, TestResult
from autoppia_iwa.src.execution.classes import ActionExecutionResult


class FeedbackGenerator:
    @staticmethod
    def calculate_score(success_count: int, total_count: int, scale: int = 10) -> float:
        """Calculate a score based on the ratio of successes to the total count."""
        return (success_count / total_count) * scale if total_count > 0 else 0

    @staticmethod
    def calculate_time_penalty(total_execution_time: float, expected_time: float) -> float:
        """
        Calculate the time penalty based on the extra execution time.
        For every 5 extra seconds beyond the expected time, 0.5 points are subtracted.
        """
        extra_time = total_execution_time - expected_time
        return max(0, (extra_time / 5.0) * 0.5)

    @staticmethod
    def flatten_test_results_matrix(test_results_matrix: list[list["TestResult"]]) -> list["TestResult"]:
        """
        Flatten a matrix of test results into a single list.

        Args:
            test_results_matrix: A matrix where each row corresponds to an action
                                and each column corresponds to a test.

        Returns:
            A flattened list of test results.
        """
        return [test for action_tests in test_results_matrix for test in action_tests]

    @staticmethod
    def generate_feedback(
        task_prompt: str,
        execution_history: list["ActionExecutionResult"],
        test_results_matrix: list[list["TestResult"]],
        expected_time: float = 50.0,
    ) -> "Feedback":
        """
        Generates structured feedback for the task evaluation.
        Args:
            task_prompt (str): The description of the evaluated task.
            execution_history (List[ActionExecutionResult]): History of executed actions.
            test_results_matrix (List[List[TestResult]]): Matrix of test results where each row
                corresponds to an action and each column corresponds to a test.
            expected_time (float): The expected time to complete the task (in seconds).
        Returns:
            Feedback: Structured feedback object summarizing the evaluation.
        """
        # ---------------------------
        # Action execution metrics
        # ---------------------------
        total_actions = len(execution_history)
        successful_actions = sum(1 for record in execution_history if record.successfully_executed)
        failed_actions = total_actions - successful_actions

        # Adjust expected time based on the number of actions
        if total_actions > 5:
            expected_time = total_actions * 5  # Allow 5 seconds per action

        # ---------------------------
        # Test results processing
        # ---------------------------
        # Flatten the test results matrix for processing
        flattened_test_results = FeedbackGenerator.flatten_test_results_matrix(test_results_matrix)

        # Count passed and failed tests directly from the flattened list
        passed_tests = sum(1 for test in flattened_test_results if test.success)
        total_tests = len(flattened_test_results)
        failed_tests = total_tests - passed_tests

        # Calculate test score
        test_score = FeedbackGenerator.calculate_score(passed_tests, total_tests)

        # Count critical failures
        critical_failures = sum(1 for test in flattened_test_results if test.extra_data and "event_name" in test.extra_data and not test.success)
        critical_penalty = critical_failures * 2

        # ---------------------------
        # Time penalty calculation
        # ---------------------------
        total_execution_time = sum(record.execution_time for record in execution_history if record.execution_time)
        time_penalty = FeedbackGenerator.calculate_time_penalty(total_execution_time, expected_time)

        # ---------------------------
        # Final score calculation
        # ---------------------------
        final_score = test_score  # - critical_penalty - time_penalty
        final_score = max(0, min(10, final_score))
        final_score = round(final_score, 1)

        # ---------------------------
        # Return the structured feedback
        # ---------------------------
        return Feedback(
            task_prompt=task_prompt,
            final_score=final_score,
            executed_actions=successful_actions,
            failed_actions=failed_actions,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_execution_time=total_execution_time,
            time_penalty=round(time_penalty, 1),
            critical_test_penalty=critical_penalty,
            test_results=flattened_test_results,
            execution_history=execution_history,
        )
