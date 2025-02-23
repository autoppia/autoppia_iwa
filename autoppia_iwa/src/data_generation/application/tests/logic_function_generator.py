# file: test_generation_pipeline.py
import json
from typing import List, Dict, Any
from loguru import logger

# Depending on your project structure, adjust these imports:
from autoppia_iwa.src.llms.domain.interfaces import ILLMService
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.shared.utils import extract_json_in_markdown
from autoppia_iwa.src.di_container import DIContainer
from dependency_injector.wiring import Provide


class TestLogicGenerator:
    """
    Generates executable logic expressions for test evaluation.
    The new format uses a JSON structure that can be directly translated to executable code.
    """

    LOGIC_SYSTEM_PROMPT = """
    You are an expert at creating precise, executable logic expressions for test evaluation.
    
    Given a matrix M where:
    - Rows (i) represent steps/actions (1 to N)
    - Columns (j) represent tests (1 to M)
    - M[i][j] is True if test j passes at step i
    
    Generate a logic expression in the following JSON format:
    {
        "type": "operation",
        "operator": "<operator>",  # AND, OR, SEQUENCE, EXISTS, ALL
        "conditions": [
            {
                "type": "test",
                "test_id": 1,      # References T1, T2, etc.
                "constraints": {    # Optional
                    "min_step": 1,  # Test must pass at/after this step
                    "max_step": 3,  # Test must pass at/before this step
                    "before": [2],  # Must pass before test_ids in this list
                    "after": [1]    # Must pass after test_ids in this list
                }
            },
            # More conditions...
        ]
    }

    Examples:
    1. "All tests must pass by the final step":
    {
        "type": "operation",
        "operator": "AND",
        "conditions": [
            {"type": "test", "test_id": 1},
            {"type": "test", "test_id": 2}
        ]
    }

    2. "Test 1 must pass before Test 2":
    {
        "type": "operation",
        "operator": "SEQUENCE",
        "conditions": [
            {"type": "test", "test_id": 1},
            {"type": "test", "test_id": 2}
        ]
    }

    3. "Either Test 1 or Test 2 must pass within first 3 steps":
    {
        "type": "operation",
        "operator": "OR",
        "conditions": [
            {
                "type": "test",
                "test_id": 1,
                "constraints": {"max_step": 3}
            },
            {
                "type": "test",
                "test_id": 2,
                "constraints": {"max_step": 3}
            }
        ]
    }
    """

    def __init__(self, llm_service: ILLMService = Provide[DIContainer.llm_service],):
        self.llm_service = llm_service

    async def generate_logic(self, task: Task, tests: List[BaseTaskTest]) -> Dict[str, Any]:
        """
        Generate a logic expression for the given task and tests.
        Returns a JSON structure that can be evaluated against the results matrix.
        """
        tests_summary = "\n".join(
            f"T{idx + 1}: {test.__class__.__name__} - {test.description}"
            for idx, test in enumerate(tests)
        )

        user_content = f"""
        Task: {task.prompt}
        Success Criteria: {task.success_criteria}
        
        Available Tests:
        {tests_summary}

        Generate a minimal but precise logic expression that confirms ALL success criteria 
        are met. Consider:
        1. Order requirements (if any steps must happen in sequence)
        2. Timing constraints (if something must happen within X steps)
        3. Dependencies between tests
        4. The most definitive way to confirm success

        Return a JSON object matching the specified format.
        """

        response = await self.llm_service.async_make_request(
            message_payload=[
                {"role": "system", "content": self.LOGIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            chat_completion_kwargs={"temperature": 0.2},
            json_format=True
        )

        try:
            logic_expr = json.loads(extract_json_in_markdown(response))
            return self._validate_logic_expression(logic_expr)
        except Exception as e:
            logger.error(f"Error parsing logic expression: {e}")
            # Fallback to simple AND of all tests
            return {
                "type": "operation",
                "operator": "AND",
                "conditions": [
                    {"type": "test", "test_id": i + 1}
                    for i in range(len(tests))
                ]
            }

    def _validate_logic_expression(self, expr: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structure of the logic expression."""
        valid_operators = {"AND", "OR", "SEQUENCE", "EXISTS", "ALL"}

        if not isinstance(expr, dict):
            raise ValueError("Expression must be a dictionary")

        if expr.get("type") != "operation":
            raise ValueError("Root expression must be an operation")

        if expr.get("operator") not in valid_operators:
            raise ValueError(f"Invalid operator: {expr.get('operator')}")

        if not isinstance(expr.get("conditions"), list):
            raise ValueError("Conditions must be a list")

        return expr


class LogicEvaluator:
    """
    Evaluates a logic expression against a test results matrix.
    """

    def evaluate(self, logic_expr: Dict[str, Any], results_matrix: List[List[bool]]) -> bool:
        """
        Evaluate the logic expression against the test results matrix.

        Args:
            logic_expr: The logic expression in our JSON format
            results_matrix: List[List[bool]] where results_matrix[i][j] is
                          True if test j passed at step i

        Returns:
            bool: True if the logic expression is satisfied
        """
        if not results_matrix or not logic_expr:
            return False

        N = len(results_matrix)      # Number of steps
        M = len(results_matrix[0])   # Number of tests

        def evaluate_test(condition: Dict[str, Any]) -> bool:
            test_id = condition["test_id"] - 1  # Convert to 0-based index
            if test_id >= M:
                return False

            constraints = condition.get("constraints", {})
            min_step = constraints.get("min_step", 1) - 1  # Convert to 0-based
            max_step = constraints.get("max_step", N) - 1  # Convert to 0-based
            before = [t - 1 for t in constraints.get("before", [])]
            after = [t - 1 for t in constraints.get("after", [])]

            # Find the first step where this test passes
            test_pass_step = next(
                (i for i in range(min_step, max_step + 1)
                 if results_matrix[i][test_id]),
                None
            )

            if test_pass_step is None:
                return False

            # Check before/after constraints
            for other_test in before:
                other_pass_step = next(
                    (i for i in range(N) if results_matrix[i][other_test]),
                    None
                )
                if other_pass_step is None or test_pass_step >= other_pass_step:
                    return False

            for other_test in after:
                other_pass_step = next(
                    (i for i in range(N) if results_matrix[i][other_test]),
                    None
                )
                if other_pass_step is None or test_pass_step <= other_pass_step:
                    return False

            return True

        def evaluate_operation(expr: Dict[str, Any]) -> bool:
            operator = expr["operator"]
            conditions = expr["conditions"]

            if operator == "AND":
                return all(
                    evaluate_test(c) if c["type"] == "test"
                    else evaluate_operation(c)
                    for c in conditions
                )
            elif operator == "OR":
                return any(
                    evaluate_test(c) if c["type"] == "test"
                    else evaluate_operation(c)
                    for c in conditions
                )
            elif operator == "SEQUENCE":
                last_pass_step = -1
                for condition in conditions:
                    test_id = condition["test_id"] - 1
                    pass_step = next(
                        (i for i in range(last_pass_step + 1, N)
                         if results_matrix[i][test_id]),
                        None
                    )
                    if pass_step is None:
                        return False
                    last_pass_step = pass_step
                return True
            elif operator == "EXISTS":
                # At least one step where all conditions are true
                return any(
                    all(results_matrix[i][c["test_id"] - 1] for c in conditions)
                    for i in range(N)
                )
            elif operator == "ALL":
                # All conditions must be true at every step
                return all(
                    all(results_matrix[i][c["test_id"] - 1] for c in conditions)
                    for i in range(N)
                )
            return False

        return evaluate_operation(logic_expr)
