import re
from typing import Any


class ConsistenceReviewer:
    """
    New version of the LLM Reviewer that is more lenient with natural language
    and uses deterministic checks for value presence.
    """

    def __init__(self, llm_service):
        """Initializes the reviewer with an LLM service."""
        self.llm_service = llm_service

    async def review_task_and_constraints(self, task: Any) -> dict[str, Any]:
        """
        Main entry point: Reviews if a task's prompt correctly represents its constraints.
        Fulfills the same interface as LLMReviewer for compatibility.
        """
        # --- PHASE 1: Data Preparation ---
        # Handle both Task objects (from the pipeline) and dictionaries (from fallback tools)
        if isinstance(task, dict):
            prompt = task.get("prompt", "")
            constraints = task.get("constraints", [])
        else:
            prompt = getattr(task, "prompt", "")
            constraints = task.use_case.constraints or [] if hasattr(task, "use_case") and task.use_case else []

        issues = []
        reasoning_parts = []
        all_valid = True

        # --- PHASE 2: Iterating through each constraint ---
        for constraint in constraints:
            # Reconstruct constraint data regardless of its original format (Object or Dict)
            if isinstance(constraint, dict):
                field = constraint.get("field")
                operator = constraint.get("operator", "")
                value = constraint.get("value")
            else:
                field = constraint.field
                operator = constraint.operator
                value = constraint.value

            # Standardize operator to its string value (handles Enums and raw strings)
            if hasattr(operator, "value"):
                operator = operator.value
            operator = str(operator)

            # --- PHASE 3: Deterministic Value Check (Safety Filter) ---
            # We check if the literal value of the constraint exists in the prompt text.
            # We skip this for exclusion operators (not_equals, not_contains) because the prompt
            # might express the exclusion by mentioning the opposite (e.g., 'Scroll RIGHT' for 'not LEFT').
            if value is not None and operator not in ["not_equals", "not_contains", "not_in_list"]:
                if isinstance(value, list):
                    # For list values (like IN_LIST), each item must be present.
                    for item in value:
                        item_str = str(item)
                        if item_str.lower() not in prompt.lower() and len(item_str) > 1:
                            all_valid = False
                            issues.append(f"Value '{item_str}' from list in field '{field}' is missing in prompt")
                else:
                    # For atomic values, it must be present in the prompt (lowercased comparison).
                    # We strip trailing punctuation for the check as natural language often omits it.
                    value_str = str(value)
                    check_val = value_str.strip(".,!?;: ")
                    if check_val and check_val.lower() not in prompt.lower() and len(check_val) > 2:
                        all_valid = False
                        issues.append(f"Value '{value_str}' for field '{field}' is missing in prompt")

            # --- PHASE 4: Semantic Operator Check (LLM Intelligence) ---
            # Special bypass for username/password which LLMs often fail to validate in "login with" contexts
            if field in ["username", "password"] and operator == "equals":
                is_valid_op = True
                reason = "Implicitly valid for authentication fields"
            else:
                # If the value exists, we ask the LLM if the prompt correctly expresses the operator's meaning.
                is_valid_op, reason = await self._validate_operator_with_llm(prompt, field, operator, value)

            if not is_valid_op:
                all_valid = False
                issues.append(f"Operator '{operator}' for field '{field}' is poorly represented: {reason}")

            reasoning_parts.append(f"Field '{field}': {reason}")

        return {"valid": all_valid, "score": 1.0 if all_valid else 0.0, "issues": issues, "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "No constraints to check"}

    async def _validate_operator_with_llm(self, prompt: str, field: str, operator: str, value: Any) -> tuple[bool, str]:
        """Communicates with the LLM to validate the semantic representation of an operator."""

        # Human-friendly operator names for the LLM to avoid confusion with internal Enum names
        human_op_map = {
            "equals": "equals",
            "not_equals": "not equals",
            "contains": "contains",
            "not_contains": "does not contain",
            "greater_than": "is greater than",
            "less_than": "is less than",
            "greater_equal": "is greater than or equal to",
            "less_equal": "is less than or equal to",
            "in_list": "is one of",
            "not_in_list": "is not one of",
        }
        human_operator = human_op_map.get(operator, operator.replace("_", " "))

        system_prompt = (
            "You are an AI assistant helping to verify if natural language prompts correctly express structured constraints.\n\n"
            "### EVALUATION CRITERIA\n"
            "1. **Semantic Equivalence**: A prompt is VALID if it conveys the same meaning as the constraint. Be extremely lenient.\n"
            "   - 'Add Item X', 'titled X', 'name X' -> matching title/name\n"
            "   - 'Update to X', 'Change to X', 'Make it X' -> matching value (equals X)\n"
            "   - 'Greater than X', 'More than X', 'Above X' -> matching greater_than X\n"
            "   - 'Less than X', 'Below X', 'Under X' -> matching less_than X\n"
            "   - 'X or more', 'at least X' -> matching greater_equal X\n"
            "   - 'X or less', 'at most X' -> matching less_equal X\n"
            "   - 'NOT X', 'Other than X', 'Different from X' -> matching not_equals X\n"
            "2. **Negation Rule**: 'rating is NOT 4' is a VALID representation of 'rating not_equals 4'. Do NOT reject it just because it mentions '4'. It negates it, which is exactly what 'not_equals' means.\n"
            "3. **Range-Value Compliance**: If the prompt specifies a specific value (e.g., 'on 2026-02-25') and the constraint is a range that includes it (e.g., 'greater_equal 2026-02-25'), it is VALID. The value satisfies the condition.\n"
            "4. **Ignore Conditionals**: If a prompt says 'Update items where Name is Y to Price 10', and you are validating 'price equals 10', it is VALID. The fact that it only applies to 'Y' items does NOT invalidate the price constraint.\n"
            "5. **Isolation**: Only evaluate the 'Target Constraint'. Ignore all other constraints in the prompt. Do not let negations from other fields influence your decision.\n"
            "6. **Direct Mapping**: If you see the words 'greater than 7' in the prompt, and the constraint is 'greater_than 7', it is AUTOMATICALLY VALID. Do not over-analyze.\n\n"
            "### RESPONSE FORMAT\n"
            "You MUST respond with a valid JSON object:\n"
            "{\n"
            '  "valid": true,\n'
            '  "reason": "Brief explanation of why it matches or fails."\n'
            "}"
        )

        user_prompt = (
            f'Prompt: "{prompt}"\n\nTarget Constraint to verify:\n- Field: {field}\n- Operator: {human_operator}\n- Value: {value}\n\nDoes the prompt correctly express this specific constraint?'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            # Request LLM prediction
            response_str = await self.llm_service.async_predict(messages=messages, json_format=True)
            if not response_str:
                return False, "Empty response from LLM"

            # --- JSON Extraction & Repair Logic ---
            try:
                # 1. Try to use json_repair if available for robust parsing
                import json_repair

                data = json_repair.loads(response_str) if isinstance(response_str, str) else response_str
            except ImportError:
                # 2. Fallback to standard json and regex cleaning
                import json

                cleaned = response_str
                if isinstance(cleaned, str):
                    cleaned = cleaned.strip()
                    # Remove potential markdown code blocks
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r"^```(?:json)?\n?|\n?```$", "", cleaned, flags=re.MULTILINE).strip()
                    # Extract the first JSON object using regex
                    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                    if json_match:
                        cleaned = json_match.group(0)
                    data = json.loads(cleaned)
                else:
                    data = cleaned

            return data.get("valid", False), data.get("reason", "No reason provided")
        except Exception as e:
            return False, f"LLM Error: {e!s}"
