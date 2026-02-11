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

        # Extract available fields from event ValidationCriteria
        available_fields_info = self._extract_available_fields(use_case, use_case_name)

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
            "You are a QA validator that checks whether a task prompt correctly represents a set of constraints.\n\n"
            "Your ONLY responsibility is to verify, for EACH constraint, whether the task prompt correctly represents:\n\n"
            "1. FIELD\n"
            "    - The field associated with each constraint must be represented in the prompt.\n"
            "    - The field may be expressed explicitly (e.g., 'year') or implicitly via natural language that clearly refers to the field (e.g., 'not released in 2022' → 'year').\n"
            "    - Fields should NOT be inferred or substituted ambiguously. Only clear semantic references are valid.\n\n"
            "2. OPERATOR\n"
            "   - The operator must be represented SEMANTICALLY.\n"
            "   - Natural language variations for each OPERATOR are allowed. So please double check them before making prediction.\n"
            "   - For all operators, the exact word may not appear; accept implicit semantic expressions that clearly match the operator meaning.\n"
            "   - Do NOT judge whether an operator is appropriate for a field.\n"
            "   - Do NOT replace, reinterpret, normalize, or correct the operator.\n"
            "   - The constraint operator is authoritative; only check semantic alignment.\n"
            "   - Do not skip fields even if multiple constraints appear in the same sentence.\n\n"
            "3. VALUE\n"
            "   - The value must match EXACTLY.\n"
            "   - Field values may appear in quotes or not; quotation marks should be ignored for all operators.\n"
            "   - Do NOT compute or guess values, but allow natural language expressions that clearly convey the same value (e.g., 'from 1866 or later' → greater_than 1866).\n"
            "   - Ignore other formatting differences (spaces, punctuation).\n\n"
            "IMPORTANT:\n"
            "- This is NOT runtime validation.\n"
            "- Do NOT evaluate truth, logic, or correctness of values.\n"
            "- Only verify that the prompt EXPRESSLY references the SAME field, operator meaning, and exact value(s).\n\n"
            "Operator semantics (short form):\n\n"
            "- equals:\n"
            "  The prompt assigns the field to the exact constraint value.\n"
            '  The word "equals" may appear or may be implicit.\n\n'
            "- not_equals:\n"
            "  The prompt states that the field is different from the exact constraint value.\n\n"
            "- contains:\n"
            "  The prompt states that the field includes the exact constraint value.\n\n"
            "- not_contains:\n"
            "  The prompt states that the field excludes the exact constraint value.\n\n"
            "- greater_than:\n"
            "  The prompt expresses a comparison using the exact constraint value,\n"
            "  indicating the field is greater than that value.\n\n"
            "- less_than:\n"
            "  The prompt expresses a comparison using the exact constraint value,\n"
            "  indicating the field is less than that value.\n\n"
            "- greater_equal:\n"
            "  The prompt expresses a comparison using the exact constraint value,\n"
            "  indicating the field is greater than or equal to that value.\n\n"
            "- less_equal:\n"
            "  The prompt expresses a comparison using the exact constraint value,\n"
            "  indicating the field is less than or equal to that value.\n\n"
            "- in_list:\n"
            "  The prompt states that the field is one of the exact listed values.\n\n"
            "- not_in_list:\n"
            "  The prompt states that the field is none of the exact listed values.\n\n"
            "Internal reasoning instructions:\n"
            "- For each task prompt, evaluate ALL constraints carefully before producing the output.\n"
            "- Perform the following steps **internally** and do NOT include them in the output:\n"
            "1. For each constraint, check the FIELD is explicitly or implicitly via natural language that clearly refers to the field mentioned in the prompt.\n"
            "2. Verify the OPERATOR is explicitly or semantically represented (natural language variations are allowed for all OPERATORS).\n"
            "3. Verify the VALUE exactly matches the constraint (ignore quotation marks or formatting differences).\n"
            "- Constraints may appear in a single sentence or across multiple sentences; ensure none are skipped.\n"
            "- Consider each constraint independently, but also check for combined expressions in the prompt.\n"
            "- Only after evaluating all constraints, produce the final JSON with the keys: valid, score, issues, reasoning.\n"
            "Evaluation rules:\n"
            "- If ALL constraints satisfy FIELD, OPERATOR, and VALUE → valid=true, score=1.0\n"
            "- If ANY constraint fails → valid=false, score=0.0\n"
            "- No intermediate or partial scores are allowed.\n\n"
            "Ignore completely:\n"
            "- Quotation marks\n"
            "- Formatting or punctuation\n"
            "- Extra or unrelated information in the prompt\n"
            "- Writing style or verbosity\n\n"
            "Respond ONLY in the following JSON format:\n"
            "{\n"
            '  "valid": boolean,\n'
            '  "score": float,\n'
            '  "issues": [string],\n'
            '  "reasoning": string\n'
            "}"
        )

        user_prompt = (
            f"Use Case: {use_case_name}\n"
            f"Description: {use_case_desc}\n\n"
            f"Available Fields:\n"
            f"{available_fields_info}\n"
            f"Constraints:\n"
            f"{constraints_str}\n\n"
            f"Task Prompt:\n"
            f"{task.prompt}\n\n"
            "Validate whether the task prompt correctly represents ALL constraints.\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Log the prompt being sent to LLM for debugging
        logger.debug(f"LLM Review Prompt for task {task.id}:")
        logger.debug(f"  System: {system_prompt[:200]}...")
        logger.debug(f"  User: {user_prompt[:500]}...")

        try:
            raw_response = await asyncio.wait_for(
                self.llm_service.async_predict(messages=messages, json_format=True, return_raw=False),
                timeout=self.timeout_seconds,
            )

            result = self._parse_llm_response(raw_response)

            # Verify binary score
            valid = result.get("valid", False)
            score = result.get("score", 0.0)

            # Final validation: ensure score matches valid field
            if (valid and score != 1.0) or (not valid and score != 0.0):
                logger.error(f"LLM review for task {task.id} has inconsistent valid/score: valid={valid}, score={score}. This should not happen after parsing correction.")
                # Force consistency
                result["score"] = 1.0 if valid else 0.0

            logger.info(f"LLM review completed for task {task.id}: valid={result.get('valid')}, score={result.get('score', 0.0):.1f}")

            # Add detailed logging for invalid reviews
            if not result.get("valid", False):
                issues = result.get("issues", [])
                reasoning = result.get("reasoning", "No reasoning provided")
                logger.warning(f"LLM review INVALID for task {task.id}")
                logger.warning(f"  Issues found: {issues}")
                logger.warning(f"  Reasoning: {reasoning}")
            else:
                # Log valid reviews at debug level
                logger.debug(f"LLM review VALID for task {task.id}: {result.get('reasoning', 'No reasoning')[:100]}...")

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
        """
        Parse LLM JSON response, handling various formats and enforcing binary scores.

        This method ensures that:
        1. The response is valid JSON
        2. The score is strictly binary (1.0 or 0.0) based on the valid field
        3. Any intermediate scores are corrected
        """
        import json
        import re

        result = None

        if isinstance(raw_response, dict):
            result = raw_response
        elif isinstance(raw_response, str):
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
                result = json.loads(cleaned)
            except json.JSONDecodeError:
                # Fallback: return a default structure
                logger.warning(f"Could not parse LLM response as JSON: {raw_response[:200]}")
                return {
                    "valid": False,
                    "score": 0.0,
                    "issues": ["Could not parse LLM response"],
                    "reasoning": f"Raw response: {raw_response[:200]}",
                }
        else:
            raise ValueError("LLM response is not a JSON string or dict")

        # CRITICAL: Enforce binary scores based on valid field
        if result:
            valid = result.get("valid", False)
            score = result.get("score", 0.0)

            # Calculate expected binary score
            expected_score = 1.0 if valid else 0.0

            # Check if score is not binary or doesn't match valid field
            if score != expected_score:
                original_score = score
                result["score"] = expected_score
                logger.warning(f"LLM Reviewer returned non-binary score. Correcting: valid={valid}, original_score={original_score:.2f}, corrected_score={expected_score:.1f}")

            # Ensure score is exactly 1.0 or 0.0 (no floating point errors)
            if result["score"] not in [0.0, 1.0]:
                result["score"] = 1.0 if result["score"] > 0.5 else 0.0
                logger.warning(f"Score was not exactly 0.0 or 1.0, rounded to {result['score']}")

        return result

    def _extract_available_fields(self, use_case, use_case_name: str) -> str:
        """
        Extract available fields and their allowed operators from the use case event.

        This information helps the LLM understand what fields are valid for this use case
        and what operators can be used with each field.

        Args:
            use_case: UseCase object with event information
            use_case_name: Name of the use case for logging

        Returns:
            Formatted string with available fields information
        """
        try:
            event_class = getattr(use_case, "event", None)
            if not event_class:
                return "Available fields: (not available for this use case)"

            # Try to get ValidationCriteria from event class
            if hasattr(event_class, "ValidationCriteria"):
                validation_criteria = event_class.ValidationCriteria

                # Get fields from ValidationCriteria
                if hasattr(validation_criteria, "model_fields"):
                    fields = list(validation_criteria.model_fields.keys())

                    if fields:
                        # Try to infer operators from field types
                        field_info = []
                        for field_name in fields:
                            field_obj = validation_criteria.model_fields.get(field_name)
                            if field_obj:
                                # Get field type
                                field_type = str(field_obj.annotation) if hasattr(field_obj, "annotation") else "unknown"

                                # Infer operators based on type
                                operators = self._infer_operators_from_type(field_type, field_name)

                                field_info.append(f"  - {field_name}: {operators}")

                        return "Available fields for this use case:\n" + "\n".join(field_info) + "\n"

            # Fallback: try to extract from event_source_code
            event_source = getattr(use_case, "event_source_code", "")
            if event_source and "class ValidationCriteria" in event_source:
                # Simple extraction of field names from source code
                import re

                criteria_section = event_source.split("class ValidationCriteria")[1].split("def _validate_criteria")[0]
                field_matches = re.findall(r"(\w+):\s*(?:str|int|float|bool)", criteria_section)

                if field_matches:
                    # Remove duplicates and common base fields
                    fields = [f for f in set(field_matches) if f not in ["event_name", "timestamp", "web_agent_id", "user_id"]]

                    # Infer operators for each field
                    field_info = []
                    for field_name in fields:
                        # Try to get type from source code
                        type_match = re.search(rf"{field_name}:\s*(str|int|float|bool)", criteria_section)
                        field_type = type_match.group(1) if type_match else "str"
                        operators = self._infer_operators_from_type(field_type, field_name)
                        field_info.append(f"  - {field_name}: {operators}")

                    return "Available fields for this use case:\n" + "\n".join(field_info) + "\n"

            return "Available fields: (could not extract from event)"

        except Exception as e:
            logger.debug(f"Could not extract available fields for {use_case_name}: {e}")
            return "Available fields: (extraction failed)"

    def _infer_operators_from_type(self, field_type: str, field_name: str) -> str:
        """
        Infer likely operators based on field type and name.

        Args:
            field_type: String representation of field type
            field_name: Name of the field

        Returns:
            String describing likely operators
        """
        # List/array fields (like genres, amenities) - check first
        # Note: In ValidationCriteria, field might be 'genre' (singular) but in constraints it's 'genres' (plural)
        if "list" in field_type.lower() or any(x in field_name.lower() for x in ["genre", "amenity", "amenities", "tag", "categories", "skill"]):
            return "[contains, not_contains, in_list, not_in_list]"

        # String fields
        if "str" in field_type.lower():
            # Check if it's a name/title field (usually equals/contains)
            if any(x in field_name.lower() for x in ["name", "title", "email", "username", "query", "subject", "message", "content", "body", "description", "director", "author", "cast"]):
                return "[equals, not_equals, contains, not_contains]"
            # Generic string
            return "[equals, not_equals, contains, not_contains]"

        # Numeric fields
        elif any(x in field_type.lower() for x in ["int", "float"]):
            # Check if it's a year/rating/count field
            if any(x in field_name.lower() for x in ["year", "rating", "price", "count", "duration", "quantity", "hour", "minute", "reviews", "bookings", "page"]):
                return "[equals, not_equals, greater_than, less_than, greater_equal, less_equal, in_list, not_in_list]"
            return "[equals, not_equals, greater_than, less_than, greater_equal, less_equal]"

        # Boolean fields
        elif "bool" in field_type.lower():
            return "[equals, not_equals]"

        # Default
        return "[equals, not_equals, contains, not_contains]"
