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
                operator = constraint.operator if isinstance(constraint.operator, str) else constraint.operator.value
                value = constraint.value

            # --- PHASE 3: Deterministic Value Check (Safety Filter) ---
            # We check if the literal value of the constraint exists in the prompt text.
            if value is not None:
                if isinstance(value, list):
                    # For list values (like IN_LIST), each item must be present.
                    for item in value:
                        item_str = str(item)
                        if item_str.lower() not in prompt.lower() and len(item_str) > 1:
                            all_valid = False
                            issues.append(f"Value '{item_str}' from list in field '{field}' is missing in prompt")
                else:
                    # For atomic values, it must be present in the prompt (lowercased comparison).
                    value_str = str(value)
                    if value_str and value_str.lower() not in prompt.lower() and len(value_str) > 2:
                        all_valid = False
                        issues.append(f"Value '{value_str}' for field '{field}' is missing in prompt")

            # --- PHASE 4: Semantic Operator Check (LLM Intelligence) ---
            # If the value exists, we ask the LLM if the prompt correctly expresses the operator's meaning.
            is_valid_op, reason = await self._validate_operator_with_llm(prompt, field, operator, value)
            if not is_valid_op:
                all_valid = False
                issues.append(f"Operator '{operator}' for field '{field}' is poorly represented: {reason}")

            reasoning_parts.append(f"Field '{field}': {reason}")

        # --- PHASE 5: Aggregating Results ---
        return {"valid": all_valid, "score": 1.0 if all_valid else 0.0, "issues": issues, "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "No constraints to check"}

    async def _validate_operator_with_llm(self, prompt: str, field: str, operator: str, value: Any) -> tuple[bool, str]:
        """Communicates with the LLM to validate the semantic representation of an operator."""

        # Crafting the instruction prompt (The knowledge base of the reviewer)
        system_prompt = (
            "You are a validation expert. Your task is to verify if a natural language prompt "
            "accurately represents a specific constraint, especially the semantic meaning of the operator.\n\n"
            "KEY PRINCIPLE: FOCUS ON SEMANTIC MEANING, NOT EXACT WORDING.\n"
            "Auxiliary verbs (is, was, should be), formatting, and common actions (login, authenticate) are VALID ways to express constraints.\n\n"
            "Common operators and their meanings (ALL these variations are VALID):\n"
            "- equals: refers to an exact match. VALID: 'name is X', 'set name to X', 'using name X', 'with name X', 'authenticate with X', 'login with X', 'X equals Y', 'X is Y'.\n"
            "  IMPORTANT: Actions like 'authenticate with password <password>' or 'login with username <username>' implicitly mean 'password equals <password>' and 'username equals <username>'. These are VALID.\n"
            "- not_equals: excludes the value. VALID: 'name is NOT X', 'name NOT X', 'other than X', 'different from X', 'anything but X', 'everything except X'.\n"
            "- contains: value is part of the field. VALID: 'name includes X', 'name has X', 'containing X', 'with X somewhere in it', 'X is in name'.\n"
            "- not_contains: value is NOT part of the field. VALID: 'not containing X', 'excluding X', 'without X', 'does not have X'.\n"
            "- greater_than/less_than: numeric comparisons. VALID: 'above', 'under', 'more than', 'higher than', 'strictly less than', 'below'.\n"
            "- greater_equal/less_equal: VALID: 'at least', 'at most', 'minimum', 'maximum', 'X or more', 'X or less', 'not less than X'.\n"
            "- in_list/not_in_list: VALID: 'one of [X, Y]', 'either X or Y', 'not in the list [X, Y]', 'is NOT one of [X, Y]', 'not published in years X, Y'.\n\n"
            "BE LENIENT: If a human would understand that the constraint is being applied, it is VALID.\n"
            "Respond strictly in JSON format:\n"
            "{\n"
            '  "valid": boolean,\n'
            '  "reason": "A short explanation of why the operator is correctly or incorrectly represented."\n'
            "}"
        )

        user_prompt = f"Prompt: \"{prompt}\"\nConstraint: {field} {operator} '{value}'\n\nDoes the prompt accurately reflect this constraint's operator and value?"

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
