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
            "You are a quality assurance expert reviewing task prompts and their associated constraints. "
            "Your job is to verify that the task prompt accurately represents ALL the constraints. "
            "The constraints are BACKEND VALIDATION TESTS (not exact specifications) that verify the task result satisfies certain conditions.\n\n"
            "CRITICAL UNDERSTANDING:\n"
            "- Constraints are VALIDATION CHECKS, not exact action specifications\n"
            "- If constraint is 'greater_than 9', the prompt can say 'greater than 9' without specifying exact value (10, 11, etc.)\n"
            "- If constraint is 'equals X', the prompt should mention the exact value X\n"
            "- Use case names (like TOGGLE) describe the action type, but prompts can be specific if constraints specify a state\n"
            "- Prompts can use natural language variations (e.g., 'greater than', 'more than', 'above', 'exceeds') for comparison operators\n"
            "- Prompts can use 'NOT', 'different from', 'excluding' for negative operators\n"
            "- The prompt should be readable and natural while accurately conveying all constraints\n"
            "- YOUR ONLY JOB: Verify that the prompt reflects the constraints. DO NOT suggest improvements or judge if operators are 'good' or 'bad'\n"
            "- If a constraint uses 'contains', and the prompt correctly reflects 'contains' (or equivalent), it is VALID - even if you think 'contains' might not be ideal\n\n"
            "COMPARISON OPERATORS AND ACCEPTABLE VARIATIONS:\n"
            "The following operators can be expressed in natural language. ALL variations listed are VALID:\n\n"
            "1. equals:\n"
            "   Constraint format: 'field equals value'\n"
            "   Valid prompt variations: 'equals', 'is', 'is equal to', '=' (symbol), 'exactly', 'precisely'\n"
            "   CRITICAL: For 'equals', the prompt can simply MENTION the exact value without using the word 'equals' explicitly.\n"
            "   If the prompt specifies the exact value in context (e.g., 'using username X', 'with password Y', 'for product Z'), it is VALID.\n"
            "   Example: Constraint 'year equals 2010' → Valid prompts: 'year equals 2010', 'year is 2010', 'year = 2010', 'movie from 2010', '2010 movie'\n"
            "   Example: Constraint 'username equals <web_agent_id>' → Valid prompts: 'username equals <web_agent_id>', 'using username <web_agent_id>', 'log in with username <web_agent_id>'\n"
            "   Example: Constraint 'password equals password123' → Valid prompts: 'password equals password123', 'using password password123', 'with password password123'\n\n"
            "2. not_equals:\n"
            "   Constraint format: 'field not_equals value'\n"
            "   Valid prompt variations: 'NOT', 'not equals', 'not equal to', 'is not', '!=' (symbol), 'different from', 'excluding', 'other than', 'anything but'\n"
            "   Example: Constraint 'year not_equals 2010' → Valid prompts: 'year NOT 2010', 'year not equals 2010', 'year is not 2010', 'year different from 2010'\n\n"
            "3. contains:\n"
            "   Constraint format: 'field contains value'\n"
            "   Valid prompt variations: 'contains', 'includes', 'has', 'with', 'containing', 'that includes', 'which contains'\n"
            "   Example: Constraint 'director contains Dav' → Valid prompts: 'director contains Dav', 'director includes Dav', 'director with Dav', 'director that includes Dav'\n"
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
            "   Example: Constraint 'rating greater_equal 4.5' → Valid prompts: 'rating >= 4.5', 'rating at least 4.5', 'rating greater than or equal to 4.5'\n\n"
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
            "KEY PRINCIPLE: If the prompt correctly reflects the semantic meaning of the constraint operator (even with natural language variations), it is VALID.\n"
            "You are NOT evaluating whether the operator choice is 'good' or 'bad' - you are ONLY checking if the prompt accurately represents the constraint.\n\n"
            "EXAMPLES OF VALID PROMPTS VS CONSTRAINTS:\n\n"
            "✅ EXAMPLE 1: Comparison operators (greater_than, less_than, etc.)\n"
            "Constraint: new_quantity greater_than 9\n"
            "Valid Prompts:\n"
            "  - 'Update quantity to be greater than 9' ✓ (exact value not required)\n"
            "  - 'Change quantity to more than 9' ✓ (natural variation)\n"
            "  - 'Set quantity above 9' ✓ (natural variation)\n"
            "Invalid:\n"
            "  - 'Update quantity' ✗ (missing constraint)\n"
            "  - 'Update quantity to 5' ✗ (contradicts constraint - 5 is not > 9)\n\n"
            "✅ EXAMPLE 2: Equals constraint (exact value required)\n"
            "Constraint: title equals 'Precision Noise Cancelling Headphones 936'\n"
            "Valid Prompts:\n"
            "  - 'Update quantity of Precision Noise Cancelling Headphones 936 to be greater than 9' ✓ (includes exact title)\n"
            "Invalid:\n"
            "  - 'Update quantity of headphones to be greater than 9' ✗ (missing exact title)\n\n"
            "✅ EXAMPLE 2B: Equals constraint - values can be mentioned without 'equals' word\n"
            "Constraints: username equals <web_agent_id> AND password equals password123\n"
            "Valid Prompts:\n"
            "  - 'Please log in using username <web_agent_id> and password password123 to access your account' ✓ (mentions exact values)\n"
            "  - 'First, authenticate using username <web_agent_id> and password password123' ✓ (mentions exact values, 'using' indicates equals)\n"
            "  - 'Log in with username <web_agent_id> and password password123' ✓ (mentions exact values)\n"
            "  - 'Authenticate using username equals <web_agent_id> and password equals password123' ✓ (explicit equals)\n"
            "  - 'First, authenticate with username equals <web_agent_id> and password equals password123' ✓ (explicit equals)\n"
            "  - 'Login: username <web_agent_id>, password password123' ✓ (mentions exact values)\n"
            "Invalid:\n"
            "  - 'Please log in' ✗ (missing both constraints)\n"
            "  - 'Log in with username <web_agent_id>' ✗ (missing password constraint)\n"
            "  - 'Log in with password password123' ✗ (missing username constraint)\n"
            "  - 'Log in with username admin and password password123' ✗ (wrong username value)\n"
            "CRITICAL NOTES:\n"
            "1. For 'equals' constraints, the prompt can simply mention the exact value in natural language context.\n"
            "   Phrases like 'using username X', 'with password Y', 'authenticate using X and Y' all indicate equals.\n"
            "2. The word 'equals' does NOT need to appear explicitly if the exact value is clearly specified.\n"
            "3. Field validation: Check if CONSTRAINT fields (username, password) are in available fields list.\n"
            "   Do NOT check if the prompt mentions fields in a specific way - the prompt can use natural language.\n"
            "4. If constraints say 'username equals X AND password equals Y', and prompt mentions both exact values, it is VALID.\n\n"
            "✅ EXAMPLE 3: Contains constraint (partial match) - CONTAINS IS VALID\n"
            "Constraint: director contains 'Dav'\n"
            "Valid Prompts:\n"
            "  - 'Show details for a movie directed by someone whose name CONTAINS Dav' ✓\n"
            "  - 'Find a film where director name includes Dav' ✓ (natural variation)\n"
            "  - 'Display movie with director containing Dav' ✓ (natural variation)\n"
            "  - 'Get movie where director has Dav' ✓ (natural variation)\n"
            "  - 'Show movie with director that includes Dav' ✓ (natural variation)\n"
            "Invalid:\n"
            "  - 'Show details for a movie directed by Dav' ✗ (implies exact match, not contains)\n"
            "  - 'Find movie directed by exactly Dav' ✗ (implies exact match, not contains)\n"
            "IMPORTANT: If constraint says 'contains' and prompt correctly reflects 'contains' (or equivalent like 'includes', 'has'), it is VALID.\n"
            "Do NOT mark it as invalid just because you think 'contains' might not be ideal - that's not your job.\n\n"
            "✅ EXAMPLE 4: NOT operators (negative constraints) - VARIATIONS ARE VALID\n"
            "Constraint: year not_equals 2010\n"
            "Valid Prompts:\n"
            "  - 'Find movie where year NOT 2010' ✓ (NOT is valid variation of not_equals)\n"
            "  - 'Show movie with year not equals 2010' ✓\n"
            "  - 'Display movie where year is not 2010' ✓\n"
            "  - 'Get movie with year different from 2010' ✓ (natural variation)\n"
            "  - 'Show movie excluding year 2010' ✓ (natural variation)\n"
            "Constraint: category not_equals Fitness\n"
            "Valid Prompts:\n"
            "  - 'Expand details section for product where category is NOT Fitness' ✓\n"
            "  - 'Show product details excluding Fitness category' ✓ (natural variation)\n"
            "  - 'Open product where category not equals Fitness' ✓\n"
            "Invalid:\n"
            "  - 'Expand details section for Fitness product' ✗ (contradicts constraint)\n"
            "  - 'Show Fitness product details' ✗ (contradicts constraint)\n\n"
            "✅ EXAMPLE 5: Use case TOGGLE with specific action\n"
            "Use Case: DETAILS_TOGGLE\n"
            "Constraints: price greater_equal 577.32 AND category not_equals Fitness\n"
            "Valid Prompts:\n"
            "  - 'Expand the details section for product where price >= 577.32 and category is NOT Fitness' ✓\n"
            "  - 'Open details section for product with price at least 577.32, excluding Fitness' ✓\n"
            "Note: Even though use case is TOGGLE, prompt can be specific about action (Expand/Collapse) if natural\n\n"
            "✅ EXAMPLE 6: Placeholders (<name>, <web_agent_id>) are VALID\n"
            "Constraint: body equals Hello <name>, I wanted to check in...\n"
            "Valid Prompts:\n"
            "  - 'Update body text where body equals Hello <name>, I wanted to check in...' ✓\n"
            "  - 'Set body to Hello <name>, I wanted to check in...' ✓\n"
            "Note: Placeholders like <name>, <web_agent_id> are normal and valid in both prompt and constraint\n\n"
            "✅ EXAMPLE 7: Text format variations (spaces, line breaks) are ACCEPTABLE\n"
            "Constraint: body equals Hello <name>, Here's a recap...\n"
            "Valid Prompts (if content is equivalent):\n"
            "  - 'body equals Hello <name>, Here's a recap...' ✓ (same content, format may vary slightly)\n"
            "  - 'body equals Hello <name>, Here\\'s a recap...' ✓ (same content, apostrophe format may differ)\n"
            "Note: Minor format differences (spaces, line breaks) are acceptable if content is equivalent\n\n"
            "✅ EXAMPLE 8: Contextual field references (from X inbox → from_email)\n"
            "Constraint: from_email contains yahoo.c\n"
            "Valid Prompts:\n"
            "  - 'Archive the email from yahoo.c inbox' ✓ (context indicates it's about sender email)\n"
            "  - 'Archive email where sender contains yahoo.c' ✓ (explicit sender reference)\n"
            "Note: 'from X inbox' can refer to sender email if context is clear\n\n"
            "✅ EXAMPLE 9: Extra information (preconditions/context) is VALID\n"
            "Constraint: username equals <web_agent_id>\n"
            "Valid Prompts:\n"
            "  - 'First, authenticate with username <web_agent_id> and password password123 before logging out' ✓\n"
            "  - 'Authenticate with username <web_agent_id> and password PASSWORD, then end session' ✓\n"
            "Note: Prompts can include preconditions/context (like authentication) even if not in constraints. Constraints are validation checks, not exact specifications.\n\n"
            "✅ EXAMPLE 10: Verb synonyms are VALID (Show/Share, Modify/Edit)\n"
            "Use Case: SHARE_BOOK\n"
            "Constraint: page_count greater_equal 432\n"
            "Valid Prompts:\n"
            "  - 'Share details for a book with page count >= 432' ✓\n"
            "  - 'Show me details for a book with page count >= 432' ✓ (Show is synonym of Share in this context)\n"
            "  - 'Share a book with page count >= 432' ✓\n"
            "Note: Verb variations (Show/Share, Modify/Edit, View/Display) are valid synonyms. Use case name describes intent, not exact verb.\n\n"
            "✅ EXAMPLE 11: Action specificity in generic use cases is VALID\n"
            "Use Case: DETAILS_TOGGLE (can be Expand or Collapse)\n"
            "Constraints: price greater_equal 577.32 AND category not_equals Fitness\n"
            "Valid Prompts:\n"
            "  - 'Expand the details section for product where price >= 577.32 and category is NOT Fitness' ✓\n"
            "  - 'Collapse the details section for product where price >= 577.32 and category is NOT Fitness' ✓\n"
            "Note: Generic use cases (TOGGLE, OPEN) can have specific actions (Expand/Collapse, Open/Close) if natural. Constraints validate the result, not the action.\n\n"
            "✅ EXAMPLE 12: Additional details not contradicting constraints are VALID\n"
            "Constraint: priority not_equals Highest\n"
            "Valid Prompts:\n"
            "  - 'Change priority to Medium where priority is NOT Highest' ✓ (Medium satisfies not_equals Highest)\n"
            "  - 'Set priority to Low where priority is NOT Highest' ✓\n"
            "Note: Prompt can be more specific than constraint if it satisfies the constraint. Constraint only validates the condition, not exact values.\n\n"
            "❌ EXAMPLE 6: Missing constraints (INVALID)\n"
            "Constraints: username equals <web_agent_id> AND password equals password123\n"
            "Invalid Prompts:\n"
            "  - 'Log in with username <web_agent_id>' ✗ (missing password constraint)\n"
            "  - 'Log in successfully' ✗ (missing all constraints)\n\n"
            "❌ EXAMPLE 7: Direct contradictions (INVALID)\n"
            "Constraint: target_name equals Joseph Jackson\n"
            "Invalid Prompts:\n"
            "  - 'Connect with user Jane Doe' ✗ (contradicts constraint - says Jane but constraint says Joseph)\n"
            "Constraint: from_email not_equals laura.nguyen@startup.io\n"
            "Invalid Prompts:\n"
            "  - 'Mark as spam the email from laura.nguyen@startup.io' ✗ (contradicts constraint - says that email but constraint says not_equals that email)\n\n"
            "❌ EXAMPLE 8: Constraints with invalid values (INVALID)\n"
            "Constraint: matters greater_than 1-2\n"
            "Invalid: This constraint itself is invalid (1-2 is not a number). But if constraint is provided, prompt must represent it.\n"
            "Note: If constraint value is clearly invalid (like '1-2' for greater_than), mark as invalid.\n\n"
            "❌ EXAMPLE 9: Wrong operator representation (INVALID)\n"
            "Constraint: status not_in_list [Archived, On Hold]\n"
            "Invalid Prompts:\n"
            "  - 'Delete matter where status equals Active' ✗ (prompt says 'equals Active' but constraint says 'not_in_list [Archived, On Hold]' - not equivalent, Active might not be the only valid option)\n"
            "Note: If prompt specifies a value that may not satisfy constraint (Active may not be the only non-Archived/On-Hold option), it's invalid.\n\n"
            "❌ EXAMPLE 10: Invalid field or operator for use case (INVALID)\n"
            "Available fields: genres [contains, not_contains, in_list, not_in_list]\n"
            "Constraint: genres equals Sci-Fi\n"
            "Invalid: The field 'genres' does NOT support 'equals' operator. Only [contains, not_contains, in_list, not_in_list] are valid.\n"
            "Note: Check that constraint fields and operators match the available fields list provided.\n\n"
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
            "EVALUATION CRITERIA (STRICT BINARY):\n"
            "STEP 1: Check constraint well-formedness (fields and operators in constraints must be valid)\n"
            "   - Are constraint FIELDS among the available fields? (Check the CONSTRAINT fields, not how prompt mentions them)\n"
            "   - Are constraint OPERATORS supported by the field type? (Check the CONSTRAINT operators)\n"
            "   - If constraints are well-formed, proceed to STEP 2. If not → valid=false, score=0.0\n\n"
            "STEP 2: Check if prompt accurately represents all constraints\n"
            "1. Does the prompt include ALL constraints? (If NO → valid=false, score=0.0)\n"
            "   - For 'equals': Check if prompt mentions the exact value (can be 'using X', 'with Y', 'equals X', etc.)\n"
            "   - For 'not_equals': Check if prompt indicates exclusion of the value\n"
            "   - For 'contains': Check if prompt indicates partial match\n"
            "   - And so on for other operators\n"
            "2. Are constraint operators accurately reflected?\n"
            "   - 'equals' → prompt mentions exact value (can use: equals, is, =, exactly, precisely, OR simply mention the value in context like 'using username X', 'with password Y')\n"
            "     CRITICAL: For 'equals', the prompt does NOT need to use the word 'equals' explicitly. Simply mentioning the exact value is sufficient.\n"
            "   - 'not_equals' → prompt indicates exclusion (can use: NOT, not equals, is not, !=, different from, excluding, other than)\n"
            "   - 'contains' → prompt indicates partial match (can use: contains, includes, has, with, containing)\n"
            "   - 'not_contains' → prompt indicates exclusion of partial match (can use: NOT contains, not contains, without, excluding)\n"
            "   - 'greater_than' → prompt expresses greater comparison (can use: greater than, more than, above, over, exceeds, >)\n"
            "   - 'less_than' → prompt expresses less comparison (can use: less than, below, under, <, fewer than)\n"
            "   - 'greater_equal' → prompt expresses >= comparison (can use: >=, at least, greater than or equal to, minimum)\n"
            "   - 'less_equal' → prompt expresses <= comparison (can use: <=, at most, less than or equal to, maximum)\n"
            "   - 'in_list' → prompt indicates value is in list (can use: in, is one of, is in, belongs to, either ... or)\n"
            "   - 'not_in_list' → prompt indicates value is not in list (can use: NOT in, not in, not one of, excluding, other than)\n"
            "   CRITICAL: Natural language variations are VALID. If semantic meaning matches, operator is correctly reflected.\n"
            "   (If operators are wrong → valid=false, score=0.0)\n"
            "3. Do constraint values match? (If NO → valid=false, score=0.0)\n"
            "   - For 'equals': Value must match exactly (but prompt can mention it as 'using X', 'with Y', 'equals X', etc.)\n"
            "   - For other operators: Check semantic equivalence\n\n"
            "IMPORTANT CLARIFICATION:\n"
            "- Field validation (STEP 1) checks if CONSTRAINT fields are in available fields list\n"
            "- The prompt can mention fields in ANY natural language way ('using username', 'with password', 'username field', etc.)\n"
            "- Do NOT check if prompt mentions fields in a specific format - only check if prompt reflects constraint values correctly\n"
            "- Example: If constraint is 'username equals X', prompt can say 'using username X', 'with username X', 'username X', etc. - ALL are VALID\n"
            "- Example: If constraint is 'password equals Y', prompt can say 'password Y', 'with password Y', 'using password Y', etc. - ALL are VALID\n\n"
            "DO NOT EVALUATE:\n"
            "- Whether constraints are too specific or complex (e.g., 'too many constraints')\n"
            "- Whether constraints may not be fulfillable in some seeds\n"
            "- Whether the prompt sounds 'too detailed' or 'too simple'\n"
            "- Whether prompt includes extra information (preconditions, context, authentication) - this is VALID\n"
            "- Whether verb matches use case name exactly (Show vs Share, Modify vs Edit) - synonyms are VALID\n"
            "- Whether action is specific in generic use cases (Expand in TOGGLE) - this is VALID if constraints don't specify state\n"
            "- Minor format differences (spaces, line breaks, apostrophes) in text values - only check if content is equivalent\n"
            "- Whether placeholders (<name>, <web_agent_id>) are present - they're valid in both prompt and constraint\n"
            "- Exact punctuation or whitespace in long text fields - focus on content equivalence\n"
            "- Whether prompt is 'more specific' than constraint (e.g., 'Medium' when constraint says 'not_equals Highest') - this is VALID if it satisfies constraint\n"
            "- Whether operator choice is 'good' or 'bad' (e.g., 'contains' is valid if constraint uses 'contains')\n"
            "- Whether a different operator would be better - that's not your concern\n"
            "- These are NOT validation issues - only check representation accuracy\n\n"
            "CRITICAL REMINDER:\n"
            "- Your job is ONLY to verify that the prompt accurately represents the constraints\n"
            "- You are NOT a prompt optimizer or suggestion engine\n"
            "- If constraint says 'year not_equals 2010' and prompt says 'year NOT 2010', that is VALID (NOT is valid variation of not_equals)\n"
            "- If constraint says 'director contains Dav' and prompt says 'director contains Dav' (or 'includes Dav'), that is VALID\n"
            "- If constraints say 'username equals X AND password equals Y' and prompt says 'using username X and password Y', that is VALID\n"
            "- If constraints say 'username equals X AND password equals Y' and prompt says 'authenticate using username equals X and password equals Y', that is VALID\n"
            "- Field validation: Check CONSTRAINT fields against available fields list, NOT how prompt mentions fields\n"
            "- The prompt can mention fields in ANY natural way ('using', 'with', 'for', etc.) - what matters is that values match\n"
            "- Do NOT mark as invalid because you think the operator could be better - that's not your job\n"
            "- Do NOT suggest improvements - only verify accuracy\n"
            "- Do NOT confuse: Validating constraint fields ≠ Validating how prompt mentions fields\n\n"
            "CRITICAL RULES:\n"
            "1. Prompt MUST include ALL constraints from the constraint list\n"
            "2. Constraint operators MUST be accurately represented using natural language variations (see operator variations list above)\n"
            "   - Example: 'equals' can be written as 'equals', 'is', '=' OR simply mention the value (e.g., 'using username X', 'with password Y') - ALL are VALID\n"
            "   - Example: 'not_equals' can be written as 'NOT', 'not equals', 'is not', 'different from', 'excluding' - ALL are VALID\n"
            "   - Example: 'contains' can be written as 'contains', 'includes', 'has', 'with' - ALL are VALID\n"
            "   - DO NOT require exact operator name match - semantic equivalence is sufficient\n"
            "   - For 'equals': If prompt mentions the exact value in context, it is VALID even without the word 'equals'\n"
            "3. Constraint values MUST match (exact values for equals, equivalent content for text fields)\n"
            "4. Constraint FIELDS must be among the available fields for this use case (check the field list provided)\n"
            "5. Constraint OPERATORS should be appropriate for the field type (will be provided in field list)\n"
            "6. Prompt CAN include extra information (authentication, context) if not contradicting constraints\n"
            "7. Prompt CAN use verb synonyms (Show/Share, Modify/Edit) - use case name is intent, not exact verb\n"
            "8. Prompt CAN be more specific than constraint if it satisfies the constraint\n"
            "9. Contradictions (prompt says X but constraint says not_X or different_X) are INVALID\n"
            "10. Missing constraints are INVALID\n"
            "11. Constraints with fields NOT in the available fields list are INVALID\n"
            "12. Constraints with operators NOT supported by the field type are INVALID (e.g., 'equals' on a list field like genres)\n"
            "13. DO NOT judge operator quality - if constraint uses 'contains' and prompt correctly reflects 'contains', it is VALID\n"
            "14. DO NOT suggest improvements - your job is ONLY to verify representation accuracy, not to improve the prompt\n\n"
            "VALIDATION OF CONSTRAINT WELL-FORMEDNESS (STEP 1 - Check CONSTRAINTS, not prompt):\n"
            "- Check if CONSTRAINT fields (from the constraints list) are in the available fields list\n"
            "- Check if CONSTRAINT operators (from the constraints list) are supported by those fields\n"
            "- DO NOT check how the prompt mentions fields - the prompt can use any natural language\n"
            "- Example: Constraint 'genres equals Sci-Fi' where genres only supports [contains, not_contains, in_list, not_in_list] → INVALID constraint\n"
            "- Example: Constraint 'name equals Old' where name supports [equals, not_equals, contains, not_contains] → VALID constraint\n"
            "- Example: Constraints 'username equals X AND password equals Y' where both username and password are in available fields → VALID constraints\n"
            "  Then check if prompt reflects these constraints (can say 'using username X and password Y' or 'username equals X and password equals Y' - both VALID)\n\n"
            "If ALL constraints are present, correctly represented, AND well-formed → valid=true, score=1.0\n"
            "If ANY constraint is missing, misrepresented, OR uses invalid field/operator → valid=false, score=0.0"
        )

        user_prompt = (
            f"Use Case: {use_case_name}\n"
            f"Use Case Description: {use_case_desc}\n\n"
            f"{available_fields_info}\n"
            f"Constraints (these are the validation criteria):\n{constraints_str}\n\n"
            f"Task Prompt:\n{task.prompt}\n\n"
            "Review whether the task prompt accurately represents all the constraints.\n\n"
            "EVALUATION STEPS:\n"
            "1. First, check if the CONSTRAINT fields (from the constraints list above) are in the available fields list.\n"
            "   - Check the fields IN THE CONSTRAINTS, not how the prompt mentions them.\n"
            "   - If constraint fields are not in available fields → valid=false, score=0.0\n"
            "2. Then, check if the CONSTRAINT operators are supported by those fields.\n"
            "   - Check the operators IN THE CONSTRAINTS, not how the prompt expresses them.\n"
            "   - If constraint operators are not supported → valid=false, score=0.0\n"
            "3. Finally, check if the prompt accurately represents all constraints.\n"
            "   - Does the prompt include ALL constraint values? (For 'equals', prompt can say 'using X', 'with Y', 'equals X', etc.)\n"
            "   - Are constraint operators correctly reflected? (Natural language variations are VALID)\n"
            "   - Do constraint values match? (Exact match for 'equals', semantic equivalence for others)\n"
            "   - The prompt can mention fields in ANY natural way - what matters is that values are correctly represented.\n"
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
