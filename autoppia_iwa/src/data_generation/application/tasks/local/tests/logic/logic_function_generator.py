import json
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import extract_json_in_markdown

from .prompts import LOGIC_SYSTEM_PROMPT


class TestLogicGenerator:
    """
    Generates executable logic expressions for test evaluation.
    Uses a structured JSON format that can be directly translated to executable code.
    """

    def __init__(self, llm_service: ILLM = Provide[DIContainer.llm_service]):
        self.llm_service = llm_service

    async def generate_logic(self, task: Task, tests: list[BaseTaskTest]) -> dict[str, Any]:
        """
        Generate a logic expression for the given task and tests.
        Returns a JSON structure that can be evaluated against the results matrix.
        """
        return {}
        # Create test descriptions using the full test configuration
        tests_summary = "\n".join(f"T{idx + 1}: {test.__class__.__name__} - {json.dumps(test.dict(), indent=2)}" for idx, test in enumerate(tests))

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

        try:
            # Call LLM with the improved API
            response = await self.llm_service.async_predict(
                messages=[{"role": "system", "content": LOGIC_SYSTEM_PROMPT}, {"role": "user", "content": user_content}], json_format=True, schema=self._get_logic_schema()
            )

            # Parse and validate the response
            logic_expr = json.loads(extract_json_in_markdown(response))
            return self._validate_logic_expression(logic_expr)

        except Exception as e:
            logger.error(f"Error generating logic expression: {e}")
            # Fallback to simple AND of all tests
            return {"type": "operation", "operator": "AND", "conditions": [{"type": "test", "test_id": i + 1} for i in range(len(tests))]}

    def _get_logic_schema(self) -> dict[str, Any]:
        """Define the JSON schema for logic expressions."""
        return {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["operation"]},
                "operator": {"type": "string", "enum": ["AND", "OR", "SEQUENCE", "EXISTS", "ALL"]},
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["test"]},
                            "test_id": {"type": "integer", "minimum": 1},
                            "constraints": {
                                "type": "object",
                                "properties": {
                                    "min_step": {"type": "integer", "minimum": 1},
                                    "max_step": {"type": "integer", "minimum": 1},
                                    "before": {"type": "array", "items": {"type": "integer"}},
                                    "after": {"type": "array", "items": {"type": "integer"}},
                                },
                            },
                        },
                        "required": ["type", "test_id"],
                    },
                },
            },
            "required": ["type", "operator", "conditions"],
        }

    def _validate_logic_expression(self, expr: dict[str, Any]) -> dict[str, Any]:
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
