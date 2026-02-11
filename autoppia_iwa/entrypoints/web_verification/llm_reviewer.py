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
            "You are a quality assurance expert reviewing task prompts and their associated constraints. "
            "Your ONLY job is to verify that the task prompt accurately represents ALL constraints by checking:\n"
            "1. FIELD: Is the constraint field mentioned/referenced in the prompt?\n"
            "2. OPERATOR: Is the constraint operator correctly reflected (semantic meaning matches)?\n"
            "3. VALUE: Does the constraint value match (exact for equals, equivalent for others)?\n\n"
            "CRITICAL: FORMATTING DOES NOT MATTER\n"
            "- Quotation marks (single or double) around values or fields are OPTIONAL - IGNORE them\n"
            "- Example: Constraint 'username equals <web_agent_id>' → Prompt 'using username <web_agent_id>' is VALID (quotes not needed)\n"
            "- Example: Constraint 'title equals Movie Name' → Prompt 'title equals Movie Name' or 'title equals \"Movie Name\"' are BOTH VALID\n"
            "- Focus ONLY on whether the FIELD, OPERATOR, and VALUE are correctly represented, NOT on formatting\n\n"
            "KEY PRINCIPLES:\n"
            "- Check SEMANTIC MEANING, not exact wording - natural language variations are VALID\n"
            "- Quotation marks, formatting, and style variations are IRRELEVANT - ignore them\n"
            "- DO NOT suggest improvements or judge operator quality - only verify accuracy\n"
            "- SHORT constraint values (e.g. single chars, substrings like 'ti', 'hen') are VALID if they appear in the prompt as in the constraints - do NOT reject for 'too vague', 'ambiguous', or 'not specific enough'\n"
            "- Your ONLY job: verify FIELD, OPERATOR, and VALUE match - do NOT judge whether the constraint is 'good' or 'useful' in practice\n\n"
            "COMPARISON OPERATORS AND ACCEPTABLE VARIATIONS:\n"
            "The following operators can be expressed in natural language. ALL variations listed are VALID:\n\n"
            "1. equals:\n"
            "   Constraint format: 'field equals value'\n"
            "   Valid prompt variations: 'equals', 'is', 'is equal to', '=' (symbol), 'exactly', 'precisely'\n"
            "   CRITICAL: For 'equals', the prompt can simply MENTION the exact value without using the word 'equals' explicitly.\n"
            "   If the prompt specifies the exact value in context, it is VALID. Common patterns:\n"
            "   - 'set X to Y' → means 'X equals Y' ✓\n"
            "   - 'update X to Y' → means 'X equals Y' ✓\n"
            "   - 'change X to Y' → means 'X equals Y' ✓\n"
            "   - 'using X Y' → means 'X equals Y' ✓\n"
            "   - 'with X Y' → means 'X equals Y' ✓\n"
            "   Example: Constraint 'year equals 2010' → Valid prompts: 'year equals 2010', 'year is 2010', 'year = 2010', 'movie from 2010', '2010 movie'\n"
            "   Example: Constraint 'username equals <web_agent_id>' → Valid prompts: 'username equals <web_agent_id>', 'using username <web_agent_id>', 'log in with username <web_agent_id>'\n"
            "   Example: Constraint 'password equals password123' → Valid prompts: 'password equals password123', 'using password password123', 'with password password123'\n"
            "   Example: Constraint 'location equals light' → Valid prompts: 'location equals light', 'set location to light', 'update location to light', 'location to light' ✓\n\n"
            "2. not_equals:\n"
            "   Constraint format: 'field not_equals value'\n"
            "   Valid prompt variations: 'NOT', 'not equals', 'not equal to', 'is not', '!=' (symbol), 'different from', 'excluding', 'other than', 'anything but'\n"
            "   Example: Constraint 'year not_equals 2010' → Valid prompts: 'year NOT 2010', 'year not equals 2010', 'year is not 2010', 'year different from 2010'\n\n"
            "3. contains:\n"
            "   Constraint format: 'field contains value'\n"
            "   Valid prompt variations: 'contains', 'includes', 'has', 'with', 'containing', 'that includes', 'which contains'\n"
            "   CRITICAL: 'include' or 'to include' means the same as 'contains' - they are semantically equivalent\n"
            "   Example: Constraint 'director contains Dav' → Valid prompts: 'director contains Dav', 'director includes Dav', 'director with Dav', 'director that includes Dav'\n"
            "   Example: Constraint 'website contains https://moviereviews.example.net' → Valid prompts:\n"
            "     - 'website contains https://moviereviews.example.net' ✓\n"
            "     - 'website includes https://moviereviews.example.net' ✓\n"
            "     - 'update website to include https://moviereviews.example.net' ✓ (to include = contains)\n"
            "     - 'website to include https://moviereviews.example.net' ✓ (to include = contains)\n\n"
            "4. not_contains:\n"
            "   Constraint format: 'field not_contains value'\n"
            "   Valid prompt variations: 'NOT contains', 'not contains', 'does not contain', 'excluding', 'without', 'not including', 'that does not contain'\n"
            "   Example: Constraint 'name not_contains Tax' → Valid prompts: 'name NOT contains Tax', 'name not contains Tax', 'name without Tax', 'name excluding Tax'\n\n"
            "5. greater_than:\n"
            "   Constraint format: 'field greater_than value'\n"
            "   Valid prompt variations: 'greater than', 'more than', 'above', 'over', 'exceeds', '>' (symbol), 'higher than', 'at least' (if context allows)\n"
            "   Example: Constraint 'price greater_than 100' → Valid prompts: 'price greater than 100', 'price more than 100', 'price above 100', 'price > 100'\n\n"
            "6. less_than:\n"
            "   Constraint format: 'field less_than value'\n"
            "   Valid prompt variations: 'less than', 'below', 'under', 'lower than', '<' (symbol), 'fewer than', 'smaller than'\n"
            "   Example: Constraint 'quantity less_than 10' → Valid prompts: 'quantity less than 10', 'quantity below 10', 'quantity < 10', 'quantity under 10'\n\n"
            "7. greater_equal:\n"
            "   Constraint format: 'field greater_equal value'\n"
            "   Valid prompt variations: 'greater than or equal to', 'at least', '>=' (symbol), 'minimum', 'or more', 'not less than'\n"
            "   CRITICAL: 'greater than or equal to' is EXACTLY EQUIVALENT to 'greater_equal' - they mean the SAME thing\n"
            "   Example: Constraint 'year greater_equal 2024' → Valid prompts:\n"
            "     - 'year greater than or equal to 2024' ✓ (EXACTLY EQUIVALENT to greater_equal)\n"
            "     - 'year >= 2024' ✓\n"
            "     - 'year at least 2024' ✓\n"
            "     - 'the year is greater than or equal to 2024' ✓ (same semantic meaning)\n"
            "   DO NOT mark as invalid if prompt says 'greater than or equal to' - it IS the correct representation of 'greater_equal'\n\n"
            "8. less_equal:\n"
            "   Constraint format: 'field less_equal value'\n"
            "   Valid prompt variations: 'less than or equal to', 'at most', '<=' (symbol), 'maximum', 'or less', 'not more than'\n"
            "   Example: Constraint 'age less_equal 18' → Valid prompts: 'age <= 18', 'age at most 18', 'age less than or equal to 18'\n\n"
            "9. in_list:\n"
            "   Constraint format: 'field in_list [value1, value2, ...]'\n"
            "   Valid prompt variations: 'in', 'is one of', 'is in', 'belongs to', 'one of', 'either ... or', 'among', 'in the list'\n"
            "   Example: Constraint 'status in_list [Active, Pending]' → Valid prompts: 'status in [Active, Pending]', 'status is one of Active or Pending', 'status is Active or Pending'\n\n"
            "10. not_in_list:\n"
            "    Constraint format: 'field not_in_list [value1, value2, ...]'\n"
            "    Valid prompt variations: 'NOT in', 'not in', 'not one of', 'not in the list', 'excluding', 'other than', 'anything but', 'neither ... nor'\n"
            "    Example: Constraint 'status not_in_list [Archived, On Hold]' → Valid prompts: 'status NOT in [Archived, On Hold]', 'status not one of Archived or On Hold', 'status excluding Archived and On Hold'\n\n"
            "KEY EXAMPLES:\n\n"
            "✅ VALID: Multiple constraints with natural language\n"
            "Constraints: username equals <web_agent_id> AND password equals password123 AND location equals light AND website contains https://moviereviews.example.net\n"
            "Prompt: 'Login for the following username equals <web_agent_id> and password equals password123. Modify your profile to set your location to 'light' and update your website to include 'https://moviereviews.example.net'.'\n"
            "✓ VALID: All constraints present - 'set location to light' = 'location equals light', 'website to include X' = 'website contains X'\n\n"
            "✅ VALID: Operator variations\n"
            "Constraint: year greater_equal 2024 → Prompt 'the year is greater than or equal to 2024' ✓ (same meaning)\n"
            "Constraint: location equals light → Prompt 'set location to light' ✓ (same meaning)\n"
            "Constraint: website contains X → Prompt 'website to include X' ✓ (same meaning)\n\n"
            "❌ INVALID: Missing constraints, wrong values, or wrong operators\n"
            "Constraint 'username equals X AND password equals Y' → Prompt 'username X' ✗ (missing password)\n"
            "Constraint 'username equals X' → Prompt 'username Y' ✗ (wrong value)\n"
            "Constraint 'year not_equals 2010' → Prompt 'year equals 2010' ✗ (contradicts)\n\n"
            "Respond strictly in JSON with the following schema:\n"
            "{\n"
            '  "valid": boolean,  // TRUE if prompt includes ALL constraints correctly, FALSE otherwise\n'
            '  "score": float,     // MUST be 1.0 if valid=true, 0.0 if valid=false (NO intermediate scores)\n'
            '  "issues": [string], // List of issues found (empty if valid is true)\n'
            '  "reasoning": string // Explanation of your assessment\n'
            "}\n\n"
            "CRITICAL: BINARY EVALUATION ONLY\n"
            "- valid=true, score=1.0: Prompt includes ALL constraints correctly\n"
            "- valid=false, score=0.0: Prompt is missing constraints OR misrepresents them\n"
            "- NO intermediate scores (0.7, 0.75, 0.8, etc.) are allowed\n"
            "- DO NOT penalize for 'too many constraints' or 'may not be fulfillable' - that's not your concern\n"
            "- Your ONLY job: Check if prompt accurately represents all constraints - that's it\n\n"
            "EVALUATION PROCESS (STRICT BINARY - valid=true/score=1.0 OR valid=false/score=0.0):\n\n"
            "STEP 1: Validate constraint well-formedness\n"
            "   - Check if CONSTRAINT fields are in the available fields list\n"
            "   - Check if CONSTRAINT operators are supported by those fields\n"
            "   - If constraints are invalid → valid=false, score=0.0\n"
            "   - If constraints are valid → proceed to STEP 2\n\n"
            "STEP 2: Verify prompt represents all constraints\n"
            "   For EACH constraint, check THREE things:\n"
            "   1. FIELD: Is the constraint field mentioned/referenced in the prompt?\n"
            "      - Prompt can mention fields in ANY way - IGNORE quotation marks\n"
            "   2. OPERATOR: Is the constraint operator correctly reflected?\n"
            "      - Check SEMANTIC MEANING, not exact wording\n"
            "      - Key equivalences: 'greater than or equal to' = 'greater_equal', 'set X to Y' = 'X equals Y', 'to include X' = 'contains X'\n"
            "   3. VALUE: Does the constraint value match?\n"
            "      - For 'equals': Exact value match (can be 'using X', 'with Y', 'set to Y', etc.)\n"
            "      - For others: Semantic equivalence\n"
            "      - IGNORE quotation marks around values\n"
            "   If ALL constraints pass all three checks → valid=true, score=1.0\n"
            "   If ANY constraint fails ANY check → valid=false, score=0.0\n\n"
            "WHAT TO IGNORE:\n"
            "- Quotation marks (single or double) around fields or values - IGNORE completely\n"
            "- Formatting differences (spaces, punctuation) - focus on content\n"
            "- Extra information in prompt (preconditions, context) - this is VALID\n"
            "- Verb variations (Show/Share, Modify/Edit) - synonyms are VALID\n"
            "- Placeholders (<name>, <web_agent_id>) - valid in both prompt and constraint\n"
            "- Operator quality judgments - if constraint uses an operator and prompt reflects it semantically, it's VALID\n"
            "- Short or generic values (e.g. 'ti', 'hen', 'e') - if the prompt mentions the exact value, it is VALID; do NOT reject for vagueness\n\n"
            "FINAL CHECKLIST:\n"
            "✓ Check ONLY: FIELD, OPERATOR, VALUE for each constraint\n"
            "✓ Semantic meaning matters, NOT exact wording\n"
            "✓ If ALL constraints correctly represented → valid=true, score=1.0\n"
            "✓ If ANY constraint missing or misrepresented → valid=false, score=0.0\n"
            "✓ NO intermediate scores - strictly binary (1.0 or 0.0)"
        )

        user_prompt = (
            f"Use Case: {use_case_name}\n"
            f"Use Case Description: {use_case_desc}\n\n"
            f"{available_fields_info}\n"
            f"Constraints (these are the validation criteria):\n{constraints_str}\n\n"
            f"Task Prompt:\n{task.prompt}\n\n"
            "Review whether the task prompt accurately represents all constraints.\n\n"
            "EVALUATION:\n"
            "1. Check constraint well-formedness: Are constraint fields in available fields? Are operators supported?\n"
            "2. For EACH constraint, verify:\n"
            "   - FIELD: Is the constraint field mentioned/referenced in the prompt? (IGNORE quotation marks)\n"
            "   - OPERATOR: Is the constraint operator correctly reflected? (semantic meaning, not exact wording)\n"
            "   - VALUE: Does the constraint value match? (IGNORE quotation marks around values)\n"
            "3. If ALL constraints pass → valid=true, score=1.0\n"
            "4. If ANY constraint fails → valid=false, score=0.0\n\n"
            "REMEMBER: Quotation marks (single or double) around fields or values are IRRELEVANT - ignore them completely.\n"
            "Focus ONLY on whether FIELD, OPERATOR, and VALUE are correctly represented.\n"
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

            # Deterministic sanity check to reduce LLM reviewer false positives/negatives.
            heuristic = self._heuristic_value_presence_check(task.prompt, constraints)
            result["heuristic"] = heuristic

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

            if isinstance(value, list):
                atoms = [self._normalize_for_match(str(v)) for v in value if v is not None and str(v).strip()]
                atoms = [a for a in atoms if a]
                if atoms and not any(a in prompt_norm for a in atoms):
                    issues.append(f"Missing any listed value for field '{field}'")
                continue

            atom = self._normalize_for_match(str(value))
            if atom and atom not in prompt_norm:
                issues.append(f"Missing value '{value}' for field '{field}'")

        return {"pass": len(issues) == 0, "issues": issues}

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
