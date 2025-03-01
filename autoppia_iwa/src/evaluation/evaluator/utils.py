
from autoppia_iwa.src.data_generation.domain.classes import Task

from typing import List, Optional, Dict, Tuple, Any
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.evaluation.classes import TestResult


def initialize_test_results_matrix(task:Task, actions: List[BaseAction]):
    """
    Initialize a test results matrix based on the number of tests in the task and actions.
    All test results are initialized with success=False.

    Args:
        task: The Task object containing tests
        actions: List of actions (can be empty)

    Returns:
        List[List[TestResult]]: A matrix of test results
    """
    # Determine the number of rows in the matrix
    # If no actions, use 1 row; otherwise, use the number of actions
    num_rows = 1 if not actions else len(actions)

    # Initialize the test results matrix
    test_results_matrix = []

    # Create each row in the matrix
    for _ in range(num_rows):
        row = []

        # Create a TestResult for each test
        for test in task.tests:
            # Extract extra_data from the test
            extra_data = {
                key: value for key, value in test.model_dump().items() 
                if key not in {"description", "test_type"}
            }

            # Create a TestResult with success=False
            test_result = TestResult(
                success=False,
                extra_data=extra_data
            )

            row.append(test_result)

        test_results_matrix.append(row)

    return test_results_matrix
