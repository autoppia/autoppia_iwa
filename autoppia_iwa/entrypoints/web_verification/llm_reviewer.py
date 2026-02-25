"""
LLM Reviewer for validating that generated tests make sense with task prompts
"""

import asyncio
import re
from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.llms.interfaces import ILLM


class LLMReviewer:
    """Reviewer that uses LLM to validate task prompts against generated tests"""

    # Constants for operator strings
    STRING_OPERATORS = "[equals, not_equals, contains, not_contains]"
    NUMERIC_OPERATORS = "[equals, not_equals, greater_than, less_than, greater_equal, less_equal]"
    LIST_OPERATORS = "[contains, not_contains, in_list, not_in_list]"
    BOOLEAN_OPERATORS = "[equals, not_equals]"

    def __init__(
        self,
        llm_service: ILLM,
        timeout_seconds: float = 30.0,
        temperature: float = 0.0,
    ):
        """
        Initialize LLM Reviewer

        Args:
            llm_service: LLM service instance
            timeout_seconds: Timeout for LLM requests
            temperature: Temperature for LLM calls (default 0.0 for deterministic QA validation)
        """
        self.llm_service = llm_service
        self.temperature = temperature
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

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(use_case_name, use_case_desc, available_fields_info, constraints_str, task.prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Log the prompt being sent to LLM for debugging
        logger.debug(f"LLM Review Prompt for task {task.id}:")
        logger.debug(f"  System: {system_prompt[:200]}...")
        logger.debug(f"  User: {user_prompt[:500]}...")

        # Print temperature being used for LLM reviewer
        print(f"🌡️  LLM Reviewer: Calling LLM with temperature={self.temperature}")

        try:
            raw_response = await asyncio.wait_for(
                self.llm_service.async_predict(messages=messages, json_format=True, return_raw=False, temperature=self.temperature),
                timeout=self.timeout_seconds,
            )

            result = self._parse_llm_response(raw_response)

            # Deterministic sanity check to reduce LLM reviewer false positives/negatives.
            heuristic = self._heuristic_value_presence_check(task.prompt, constraints)
            result["heuristic"] = heuristic

            # Apply heuristic corrections
            self._apply_heuristic_corrections(result, heuristic)

            # Validate and fix score consistency
            self._validate_and_fix_score(result, task.id)

            # Log review result
            self._log_review_result(result, task.id)

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

    def _build_user_prompt(self, use_case_name: str, use_case_desc: str, available_fields_info: str, constraints_str: str, task_prompt: str) -> str:
        """Build user prompt for LLM review."""
        return (
            f"Use Case: {use_case_name}\n"
            f"Description: {use_case_desc}\n\n"
            f"Available Fields:\n"
            f"{available_fields_info}\n"
            f"Constraints:\n"
            f"{constraints_str}\n\n"
            f"Task Prompt:\n"
            f"{task_prompt}\n\n"
            "Validate whether the task prompt correctly represents ALL constraints.\n"
        )

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM review."""
        return (
            "You are a QA validator that checks whether a task prompt correctly represents a set of constraints.\n\n"
            "Your ONLY responsibility is to verify, for EACH constraint, whether the task prompt correctly represents:\n\n"
            "1. FIELD\n"
            "    - The field associated with each constraint must be represented in the prompt.\n"
            "    - The field may be expressed explicitly (e.g., 'year') or implicitly via natural language that clearly refers to the field (e.g., 'not released in 2022' → 'year').\n"
            "    - Fields should NOT be inferred or substituted ambiguously. Only clear semantic references are valid.\n"
            "    - For numeric or date fields, natural language expressions like 'after 1866', 'from 1866 or later', or 'up to 13.99' are acceptable if they clearly convey the same operator and value.\n"
            "    - For string/list fields, plural/singular forms or minor synonyms are allowed if they unambiguously represent the same value.\n"
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
            "- First, read the entire task prompt carefully to understand how all constraints are represented collectively.\n"
            "- Then, for each constraint, check if the FIELD, OPERATOR, and VALUE are represented somewhere in the prompt, allowing for natural language variations, semantic expressions, and formatting differences.\n"
            "- Do not reject a constraint simply because it does not appear verbatim in the same order as listed; focus on whether the meaning is fully captured in the prompt.\n"
            "- Perform the following steps **internally** and do NOT include them in the output:\n"
            "1. For each constraint, check the FIELD is explicitly or implicitly mentioned via natural language that clearly refers to the field in the prompt.\n"
            "   - Accept variations in field formatting, such as underscores, spaces, hyphens, or camelCase, as long as the semantic meaning matches the constraint.\n"
            "2. Verify the OPERATOR is explicitly or semantically represented (natural language variations are allowed for all OPERATORS).\n"
            "3. Verify the VALUE exactly matches the constraint (ignore quotation marks, formatting differences, or minor natural language phrasing).\n"
            "- Constraints may appear in a single sentence or across multiple sentences; ensure none are skipped.\n"
            "- Consider each constraint independently, but also check for combined expressions in the prompt.\n"
            "- Only after evaluating all constraints, produce the final JSON with the keys: valid, score, issues, reasoning.\n"
            "- Ignore any extra information in the prompt unrelated to the listed constraints (style, verbosity, punctuation).\n"
            "Evaluation rules:\n"
            "- If ALL constraints satisfy FIELD, OPERATOR, and VALUE → valid=true, score=1.0\n"
            "- If ANY constraint fails → valid=false, score=0.0\n"
            "- No intermediate or partial scores are allowed.\n\n"
            "Respond ONLY in the following JSON format:\n"
            "{\n"
            '  "valid": boolean,\n'
            '  "score": float,\n'
            '  "issues": [string],\n'
            '  "reasoning": string\n'
            "}"
        )

    def _apply_heuristic_corrections(self, result: dict[str, Any], heuristic: dict[str, Any]) -> None:
        """Apply heuristic corrections to LLM review result."""
        # If the LLM says it's valid but values are missing, treat it as invalid (likely false positive).
        if result.get("valid", False) and not heuristic.get("pass", True):
            result["valid"] = False
            result["score"] = 0.0
            result.setdefault("issues", [])
            result["issues"].extend([f"Heuristic: {msg}" for msg in heuristic.get("issues", [])])
            result["reasoning"] = (result.get("reasoning", "") + "\n\nHeuristic check failed: missing constraint value(s).").strip()

        # If the LLM says it's invalid but all values are present, treat it as valid (likely false negative).
        elif not result.get("valid", False) and heuristic.get("pass", False):
            result["valid"] = True
            result["score"] = 1.0
            result["overridden_by_heuristic"] = True
            result.setdefault("issues", [])
            result["issues"].append("Heuristic override: all constraint values were found in the prompt.")
            result["reasoning"] = (result.get("reasoning", "") + "\n\nHeuristic override applied: all constraint values present.").strip()

    def _validate_and_fix_score(self, result: dict[str, Any], task_id: str) -> None:
        """Validate and fix score consistency with valid field."""
        valid = result.get("valid", False)
        score = result.get("score", 0.0)

        # Final validation: ensure score matches valid field
        # Usamos tolerancia (1e-9) en lugar de == porque los números flotantes pueden tener errores de precisión
        TOLERANCE = 1e-9
        score_mismatch = (valid and abs(score - 1.0) >= TOLERANCE) or (not valid and abs(score - 0.0) >= TOLERANCE)
        if score_mismatch:
            logger.error(f"LLM review for task {task_id} has inconsistent valid/score: valid={valid}, score={score}. This should not happen after parsing correction.")
            # Force consistency
            result["score"] = 1.0 if valid else 0.0

    def _log_review_result(self, result: dict[str, Any], task_id: str) -> None:
        """Log the review result."""
        logger.info(f"LLM review completed for task {task_id}: valid={result.get('valid')}, score={result.get('score', 0.0):.1f}")

        # Add detailed logging for invalid reviews
        if not result.get("valid", False):
            issues = result.get("issues", [])
            reasoning = result.get("reasoning", "No reasoning provided")
            logger.warning(f"LLM review INVALID for task {task_id}")
            logger.warning(f"  Issues found: {issues}")
            logger.warning(f"  Reasoning: {reasoning}")
        else:
            # Log valid reviews at debug level
            logger.debug(f"LLM review VALID for task {task_id}: {result.get('reasoning', 'No reasoning')[:100]}...")

    def _heuristic_value_presence_check(self, prompt: str, constraints: list[dict[str, Any]] | None) -> dict[str, Any]:
        """
        Lightweight deterministic check: ensure each constraint VALUE appears in the prompt text.

        This intentionally does NOT try to fully validate operator semantics or field mention.
        It exists to:
        - Flag likely false positives when values are missing
        - Recover from likely false negatives when the LLM reviewer misreads formatting
        """
        if not constraints:
            return {"pass": True, "issues": []}
        if not isinstance(prompt, str) or not prompt.strip():
            return {"pass": False, "issues": ["Empty prompt text"]}

        prompt_norm = self._normalize_for_match(prompt)
        issues: list[str] = []

        for constraint in constraints:
            if not isinstance(constraint, dict):
                continue
            field = str(constraint.get("field", "") or "")
            value = constraint.get("value", None)
            if value is None:
                continue

            issue = self._check_constraint_value_presence(constraint, field, value, prompt_norm)
            if issue:
                issues.append(issue)

        return {"pass": len(issues) == 0, "issues": issues}

    def _check_constraint_value_presence(self, constraint: dict[str, Any], field: str, value: Any, prompt_norm: str) -> str | None:
        """Check if constraint value is present in normalized prompt. Returns issue message if missing, None otherwise."""
        if isinstance(value, list):
            return self._check_list_value_presence(field, value, prompt_norm)
        return self._check_single_value_presence(field, value, prompt_norm)

    def _check_list_value_presence(self, field: str, value: list[Any], prompt_norm: str) -> str | None:
        """Check if any value in list is present in normalized prompt."""
        atoms = [self._normalize_for_match(str(v)) for v in value if v is not None and str(v).strip()]
        atoms = [a for a in atoms if a]
        if atoms and not any(a in prompt_norm for a in atoms):
            return f"Missing any listed value for field '{field}'"
        return None

    def _check_single_value_presence(self, field: str, value: Any, prompt_norm: str) -> str | None:
        """Check if single value is present in normalized prompt."""
        atom = self._normalize_for_match(str(value))
        if atom and atom not in prompt_norm:
            return f"Missing value '{value}' for field '{field}'"
        return None

    @staticmethod
    def _normalize_for_match(text: str) -> str:
        lowered = text.lower()
        lowered = re.sub(r"[\"'`]", "", lowered)
        lowered = re.sub(r"[^a-z0-9<>@._\-\s]", " ", lowered)
        lowered = re.sub(r"\s+", " ", lowered).strip()
        return lowered

    def _parse_llm_response(self, raw_response: Any) -> dict[str, Any]:
        """
        Parse LLM JSON response, handling various formats and enforcing binary scores.

        This method ensures that:
        1. The response is valid JSON
        2. The score is strictly binary (1.0 or 0.0) based on the valid field
        3. Any intermediate scores are corrected
        """

        result = self._extract_json_from_response(raw_response)
        if result is None:
            return {
                "valid": False,
                "score": 0.0,
                "issues": ["Could not parse LLM response"],
                "reasoning": f"Raw response: {str(raw_response)[:200]}",
            }

        # CRITICAL: Enforce binary scores based on valid field
        self._enforce_binary_score(result)
        return result

    def _extract_json_from_response(self, raw_response: Any) -> dict[str, Any] | None:
        """Extract JSON dict from raw LLM response (dict, string with code fences, or plain string)."""
        import json

        if isinstance(raw_response, dict):
            return raw_response

        if not isinstance(raw_response, str):
            raise ValueError("LLM response is not a JSON string or dict")

        # Try to extract JSON from response
        cleaned = raw_response.strip()

        # Remove code fences if present
        cleaned = self._remove_code_fences(cleaned)

        # Try to find JSON object
        cleaned = self._extract_json_object(cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse LLM response as JSON: {raw_response[:200]}")
            return None

    def _remove_code_fences(self, text: str) -> str:
        """Remove code fences from text if present."""
        import re

        code_fence_match = re.search(r"```(?:json)?\s*(\{[^\}]*\})\s*```", text, re.DOTALL)
        if code_fence_match:
            return code_fence_match.group(1)
        return text

    def _extract_json_object(self, text: str) -> str:
        """Extract JSON object from text."""
        import re

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return text

    def _enforce_binary_score(self, result: dict[str, Any]) -> None:
        """Enforce binary score (1.0 or 0.0) based on valid field."""
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
            fields_info = self._extract_fields_from_validation_criteria(event_class)
            if fields_info:
                return fields_info

            # Fallback: try to extract from event_source_code
            event_source = getattr(use_case, "event_source_code", "")
            fields_info = self._extract_fields_from_source_code(event_source)
            if fields_info:
                return fields_info

            return "Available fields: (could not extract from event)"

        except Exception as e:
            logger.debug(f"Could not extract available fields for {use_case_name}: {e}")
            return "Available fields: (extraction failed)"

    def _extract_fields_from_validation_criteria(self, event_class: Any) -> str | None:
        """Extract fields from ValidationCriteria.model_fields."""
        if not hasattr(event_class, "ValidationCriteria"):
            return None

        validation_criteria = event_class.ValidationCriteria
        if not hasattr(validation_criteria, "model_fields"):
            return None

        fields = list(validation_criteria.model_fields.keys())
        if not fields:
            return None

        field_info = []
        for field_name in fields:
            field_obj = validation_criteria.model_fields.get(field_name)
            if field_obj:
                field_type = str(field_obj.annotation) if hasattr(field_obj, "annotation") else "unknown"
                operators = self._infer_operators_from_type(field_type, field_name)
                field_info.append(f"  - {field_name}: {operators}")

        return "Available fields for this use case:\n" + "\n".join(field_info) + "\n"

    def _extract_fields_from_source_code(self, event_source: str) -> str | None:
        """Extract fields from event_source_code using regex (with security limits)."""
        import re

        if not event_source or "class ValidationCriteria" not in event_source:
            return None

        # Limit input size to prevent DoS (max 10KB for criteria section)
        MAX_CRITERIA_SECTION_SIZE = 10000
        criteria_section = event_source.split("class ValidationCriteria")[1].split("def _validate_criteria")[0]
        if len(criteria_section) > MAX_CRITERIA_SECTION_SIZE:
            logger.warning(f"Criteria section too large ({len(criteria_section)} chars), truncating to prevent DoS")
            criteria_section = criteria_section[:MAX_CRITERIA_SECTION_SIZE]

        # Use safer regex pattern - match word characters only (no special regex chars in field names)
        field_matches = re.findall(r"(\w+):\s*(?:str|int|float|bool)", criteria_section)

        if not field_matches:
            return None

        # Remove duplicates and common base fields
        fields = [f for f in set(field_matches) if f not in ["event_name", "timestamp", "web_agent_id", "user_id"]]

        # Infer operators for each field
        field_info = []
        for field_name in fields:
            # Escape field_name to prevent regex injection, then use in pattern
            # Since field_name comes from \w+ match, it's already safe, but we escape for extra safety
            escaped_field_name = re.escape(field_name)
            type_match = re.search(rf"{escaped_field_name}:\s*(str|int|float|bool)", criteria_section)
            field_type = type_match.group(1) if type_match else "str"
            operators = self._infer_operators_from_type(field_type, field_name)
            field_info.append(f"  - {field_name}: {operators}")

        return "Available fields for this use case:\n" + "\n".join(field_info) + "\n"

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
            return self.LIST_OPERATORS

        # String fields
        if "str" in field_type.lower():
            # Check if it's a name/title field (usually equals/contains)
            if any(x in field_name.lower() for x in ["name", "title", "email", "username", "query", "subject", "message", "content", "body", "description", "director", "author", "cast"]):
                return self.STRING_OPERATORS
            # Generic string
            return self.STRING_OPERATORS

        # Numeric fields
        elif any(x in field_type.lower() for x in ["int", "float"]):
            # Check if it's a year/rating/count field
            if any(x in field_name.lower() for x in ["year", "rating", "price", "count", "duration", "quantity", "hour", "minute", "reviews", "bookings", "page"]):
                return self.NUMERIC_OPERATORS
            return self.NUMERIC_OPERATORS

        # Boolean fields
        elif "bool" in field_type.lower():
            return self.BOOLEAN_OPERATORS

        # Default
        return self.STRING_OPERATORS
