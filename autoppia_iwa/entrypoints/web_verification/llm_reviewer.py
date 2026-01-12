"""
LLM Reviewer for validating that generated tests make sense with task prompts
"""

import asyncio
from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.llms.interfaces import ILLM


class LLMReviewer:
    """Reviewer that uses LLM to validate task prompts against generated tests"""

    def __init__(
        self,
        llm_service: ILLM,
        timeout_seconds: float = 30.0,
    ):
        """
        Initialize LLM Reviewer

        Args:
            llm_service: LLM service instance
            timeout_seconds: Timeout for LLM requests
        """
        self.llm_service = llm_service
        self.timeout_seconds = timeout_seconds

    async def review_task_and_constraints(self, task: Task) -> dict[str, Any]:
        """
        Review a task prompt and its constraints to verify the prompt accurately represents the constraints

        Args:
            task: The task to review (contains prompt and use_case with constraints)

        Returns:
            Dictionary with review results:
            {
                "valid": bool,
                "score": float (0.0-1.0),
                "issues": List[str],
                "reasoning": str
            }
        """
        # Get use case and constraints
        use_case = getattr(task, "use_case", None)
        if not use_case:
            return {
                "valid": False,
                "score": 0.0,
                "issues": ["Task has no associated use case"],
                "reasoning": "Cannot review task without use case",
            }

        use_case_name = getattr(use_case, "name", "Unknown")
        use_case_desc = getattr(use_case, "description", "")

        # Get constraints
        constraints = getattr(use_case, "constraints", None)
        constraints_str = use_case.constraints_to_str() if constraints else "No constraints defined"

        # Improvement 1: If no constraints provided, skip LLM review and mark as valid
        if not constraints:
            logger.info(f"No constraints found for use case {use_case_name}. Skipping LLM review and marking as valid.")
            return {
                "valid": True,  # Mark as valid instead of invalid
                "score": 1.0,  # Perfect score since no constraints to validate
                "issues": [],  # No issues since no constraints to check
                "reasoning": "No constraints provided for this use case. Task is automatically valid.",
                "skipped": True,  # Indicate that review was skipped
            }

        # Build the review prompt
        system_prompt = (
            "You are a quality assurance expert reviewing task prompts and their associated constraints. "
            "Your job is to verify that the task prompt accurately represents ALL the constraints. "
            "The constraints are the validation criteria (tests) that the task must satisfy. "
            "Respond strictly in JSON with the following schema:\n"
            "{\n"
            '  "valid": boolean,  // Whether the prompt accurately represents all constraints\n'
            '  "score": float,     // Score from 0.0 to 1.0 indicating how well prompt matches constraints\n'
            '  "issues": [string], // List of issues found (empty if valid is true)\n'
            '  "reasoning": string // Explanation of your assessment\n'
            "}\n"
            "Consider:\n"
            "- Does the prompt include ALL constraints?\n"
            "- Are constraint values correctly represented in the prompt?\n"
            "- Are constraint operators (equals, contains, greater_than, etc.) accurately reflected?\n"
            "- Are there constraints missing from the prompt?\n"
            "- Are there any extra requirements in the prompt that are not in the constraints?"
        )

        user_prompt = (
            f"Use Case: {use_case_name}\n"
            f"Use Case Description: {use_case_desc}\n\n"
            f"Constraints (these are the validation criteria):\n{constraints_str}\n\n"
            f"Task Prompt:\n{task.prompt}\n\n"
            "Review whether the task prompt accurately represents all the constraints. "
            "The prompt should include all constraints in natural language."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            raw_response = await asyncio.wait_for(
                self.llm_service.async_predict(messages=messages, json_format=True, return_raw=False),
                timeout=self.timeout_seconds,
            )

            result = self._parse_llm_response(raw_response)

            logger.info(f"LLM review completed for task {task.id}: valid={result.get('valid')}, score={result.get('score', 0.0):.2f}")

            return result

        except TimeoutError:
            logger.error(f"LLM review timeout for task {task.id}")
            return {
                "valid": False,
                "score": 0.0,
                "issues": ["LLM review request timed out"],
                "reasoning": "Timeout while waiting for LLM response",
            }
        except Exception as e:
            logger.error(f"LLM review error for task {task.id}: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "issues": [f"LLM review error: {e!s}"],
                "reasoning": f"Error during LLM review: {e!s}",
            }

    def _parse_llm_response(self, raw_response: Any) -> dict[str, Any]:
        """Parse LLM JSON response, handling various formats"""
        import json
        import re

        if isinstance(raw_response, dict):
            return raw_response

        if not isinstance(raw_response, str):
            raise ValueError("LLM response is not a JSON string or dict")

        # Try to extract JSON from response
        cleaned = raw_response.strip()

        # Remove code fences if present
        code_fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if code_fence_match:
            cleaned = code_fence_match.group(1)

        # Try to find JSON object
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: return a default structure
            logger.warning(f"Could not parse LLM response as JSON: {raw_response[:200]}")
            return {
                "valid": False,
                "score": 0.0,
                "issues": ["Could not parse LLM response"],
                "reasoning": f"Raw response: {raw_response[:200]}",
            }
