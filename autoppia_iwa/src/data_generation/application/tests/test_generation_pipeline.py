# file: test_generation_pipeline.py

import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger

from pydantic import ValidationError

# Depending on your project structure, adjust these imports:
from autoppia_iwa.src.llms.domain.interfaces import ILLMService
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis

from autoppia_iwa.src.shared.utils import get_html_and_screenshot, detect_interactive_elements
from dependency_injector.wiring import Provide
from autoppia_iwa.src.di_container import DIContainer

################################################################################
# PART 1: Utility for extracting JSON from markdown
################################################################################


def extract_json_in_markdown(text: str) -> str:
    """
    Extract the first fenced code block (```json ... ``` or just ``` ... ```).
    If none is found, return text.strip() as a fallback.
    """
    pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


################################################################################
# PART 2: PROMPTS
################################################################################

TEST_GENERATION_SYSTEM_PROMPT = """
You are a QA test generator, specialized in verifying whether a specific user task was completed.

## Context & Goal
- Each 'task' is a short user instruction (e.g. "Click on the 'Home' link to return to the homepage").
- The 'success criteria' says how we know the user completed the task (e.g. "User is redirected to the homepage").
- We have:
  - A truncated HTML snippet of the page,
  - A screenshot summary,
  - A list of possible interactive elements (links, forms, etc.),
  - Optional project-level context (like relevant backend events).
- We want to propose **1 or 2 minimal tests** that verify the user actually reached the success criteria.

## Available Test Classes
1) FindInHtmlTest
   - test_type = "frontend"
   - fields: { "keywords": [...], "description": "..." }
2) CheckEventEmittedTest
   - test_type = "backend"
   - fields: { "event_name": "...", "description": "..." }
3) CheckPageViewEventTest
   - test_type = "backend"
   - fields: { "page_view_url": "...", "description": "..." }
4) OpinionBaseOnHTML
   - test_type = "frontend"
   - fields: { "name": "OpinionBaseOnHTML", "description": "..." }
5) OpinionBaseOnScreenshot
   - test_type = "frontend"
   - fields: { "name": "OpinionBaseOnScreenshot", "task": "...", "description": "..." }

## Requirements
- Generate minimal tests that confirm the *exact* success criteria.
- Usually 1 test is enough if the criteria is purely front-end (e.g., user sees a certain page).
- If success criteria reference a backend event, propose a second test (CheckEventEmittedTest or CheckPageViewEventTest).
- Return strictly valid JSON array, with **no extra keys**.
"""

FINAL_LOGIC_SYSTEM_PROMPT = """
You are an expert in multi-step, multi-test logic. 

- We have N actions (steps), numbered i = 1..N.
- We have M tests T1..TM. Each test Tj is run after each action i, producing a pass/fail result x(i,j).
- We want a single final boolean formula f(x(i,j)) telling us if the task is considered complete.

### Explanation
- For each action i, we run each test j. So we get a pass/fail matrix x(1,1), x(1,2), ..., x(N,M).
- We often want to see if **there exists** an action i where all the relevant tests pass. 
  For example: "∃ i in [1..N]: T1_i AND T2_i"
- Or we might want all tests to pass **at the final action** (i = N), e.g.: "T1_N AND T2_N"

### Instructions
- Propose a minimal formula referencing the test indexes T1..Tn and their pass/fail at some i.
- Use notation like T1_i, T2_i, etc. 
- Return JSON with a single key "logic". For example:
  {
    "logic": "∃ i in [1..N]: T1_i AND T2_i"
  }
If there's only one test, you might say:
  {
    "logic": "∃ i: T1_i"
  }
"""

################################################################################
# PART 3: Normalizing LLM's output
################################################################################


def _normalize_test_config(test_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts LLM-produced test_config like:
      {"test_type": "FindInHtmlTest", "fields": {"keywords": [...], "description": "..."}}
    into the standard shape your pipeline expects:
      {"test_type": "frontend", "keywords": [...], "description": "..."}

    Extend similarly for any other "test_type" variations from the LLM.
    """
    # Example: LLM gave "FindInHtmlTest" but we want "frontend"
    # Also flatten "fields" into the top-level.
    raw_test_type = test_config.get("test_type")

    # If there's a "fields" dict, flatten it
    if "fields" in test_config and isinstance(test_config["fields"], dict):
        fields = test_config.pop("fields")
        test_config.update(fields)

    # Map "FindInHtmlTest" => "frontend", etc.
    # You can add more mappings as needed if the LLM produces other variants.
    if raw_test_type == "FindInHtmlTest":
        test_config["test_type"] = "frontend"
    elif raw_test_type == "CheckEventEmittedTest":
        test_config["test_type"] = "backend"
    elif raw_test_type == "CheckPageViewEventTest":
        test_config["test_type"] = "backend"
    elif raw_test_type == "OpinionBaseOnHTML":
        test_config["test_type"] = "frontend"
        test_config["name"] = "OpinionBaseOnHTML"
    elif raw_test_type == "OpinionBaseOnScreenshot":
        test_config["test_type"] = "frontend"
        test_config["name"] = "OpinionBaseOnScreenshot"

    return test_config


################################################################################
# PART 4: TestGenerationPipeline
################################################################################

class TestGenerationPipeline:
    """
    A pipeline that, for each Task, uses an LLM to:
      1) Propose 1–2 minimal test definitions referencing the relevant test classes.
      2) Propose a final Boolean expression referencing x(i,j) for overall success.
    """

    def __init__(
        self,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
        truncate_html_chars: int = 1500
    ):
        """
        Args:
            llm_service: An LLM service implementing ILLMService.
            truncate_html_chars: Limit for how many characters of HTML to include in prompts.
        """
        self.llm_service = llm_service
        self.truncate_html_chars = truncate_html_chars

    async def generate_tests_for_tasks(
        self,
        tasks: List[Task],
        domain_analysis: Optional[DomainAnalysis] = None,
        project_context: Optional[Dict[str, Any]] = None,
    ) -> List[Task]:
        """
        Given a list of tasks, generate a minimal set of tests for each task
        that confirm the user completed the scenario described in the prompt
        (according to the success criteria).

        Args:
            tasks: List of tasks (with .prompt, .success_criteria, .url, etc.).
            domain_analysis: Optional domain-level analysis with pre-fetched data.
            project_context: Additional project-level context (like known backend events).

        Returns:
            The same list of tasks, each enriched with test definitions and a final logic expression.
        """
        for task in tasks:
            try:
                # 1) Attempt to find existing analysis for this page
                page_analysis = None
                if domain_analysis and domain_analysis.page_analyses:
                    page_analysis = next(
                        (p for p in domain_analysis.page_analyses if p.page_url == task.url),
                        None
                    )

                # 2) Get HTML, screenshot, interactive elements 
                if page_analysis:
                    truncated_html = page_analysis.clean_html[:self.truncate_html_chars]
                    screenshot_desc = page_analysis.screenshot_description or ""
                    interactive_summary = detect_interactive_elements(page_analysis.clean_html)
                else:
                    fetched_html, fetched_screenshot_desc = await get_html_and_screenshot(task.url)
                    truncated_html = fetched_html[:self.truncate_html_chars]
                    screenshot_desc = fetched_screenshot_desc
                    interactive_summary = detect_interactive_elements(fetched_html)

                # 3) Build a JSON representation of optional project context
                context_data = project_context or {}
                context_json = json.dumps(context_data, indent=2)

                # 4) Generate minimal test definitions
                generation_user_content = (
                    f"Task Prompt: {task.prompt}\n\n"
                    f"Success Criteria: {task.success_criteria or 'N/A'}\n\n"
                    f"HTML snippet:\n{truncated_html}\n\n"
                    f"Screenshot summary:\n{screenshot_desc}\n\n"
                    f"Interactive elements:\n{json.dumps(interactive_summary, indent=2)}\n\n"
                    f"Project context:\n{context_json}\n\n"
                    "Return strictly valid JSON array of minimal test definitions."
                )
                test_generation_response = self._call_llm(
                    TEST_GENERATION_SYSTEM_PROMPT,
                    generation_user_content
                )
                raw_json = extract_json_in_markdown(test_generation_response)
                proposed_tests = self._parse_test_definitions(raw_json)

                # 5) Convert the parsed dicts into typed test objects
                test_objects = BaseTaskTest.assign_tests(proposed_tests)
                task.tests.extend(test_objects)

                # 6) Generate the final multi-step logic formula referencing x(i,j)
                tests_summary = "\n".join(
                    [f"T{idx + 1}: {test.__class__.__name__}" for idx, test in enumerate(task.tests)]
                )
                # We let the LLM see how many tests we ended up with (n), and name them T1..Tn
                logic_user_content = (
                    "We have an NxM pass/fail matrix x(i,j), where i ∈ {1..N} are actions, j ∈ {1..M} are tests.\n"
                    f"Number of tests: {len(task.tests)}\n\n"
                    f"The tests are:\n{tests_summary}\n\n"
                    "Generate a minimal formula f(x(i,j)) that determines if the task was completed. "
                    "Use notation like T1_i, T2_i, etc. Return JSON: {\"logic\": \"...\"}."
                )
                logic_generation_response = self._call_llm(
                    FINAL_LOGIC_SYSTEM_PROMPT,
                    logic_user_content
                )
                logic_json_str = extract_json_in_markdown(logic_generation_response)
                final_logic_expr = self._parse_logic_expression(logic_json_str)

                # If the LLM doesn't produce anything valid, default to "T1"
                task.logic_function = final_logic_expr or "T1"

            except Exception as e:
                logger.error(f"Failed to generate tests/logic for task {task.id}: {e}")

        return tasks

    def _call_llm(self, system_prompt: str, user_content: str) -> str:
        """
        Helper method to call the LLM with a system prompt and user content.
        Expects the underlying llm_service to accept `message_payload` as a list of dicts.
        """
        message_payload = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = self.llm_service.make_request(
            message_payload=message_payload,
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 1200}
        )
        return response or ""

    def _parse_test_definitions(self, text: str) -> List[Dict[str, Any]]:
        """
        Safely parse a JSON array of test definitions from the LLM's output.

        Returns:
            A list of dicts describing each test. If parsing fails, returns an empty list.
            Also normalizes them to the shape the pipeline expects.
        """
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                normalized = []
                for item in parsed:
                    norm_item = _normalize_test_config(item)
                    normalized.append(norm_item)
                return normalized
        except (ValueError, TypeError, ValidationError) as e:
            logger.warning(f"Error parsing test definitions: {e}")
        return []

    def _parse_logic_expression(self, text: str) -> str:
        """
        Parse JSON of the form {"logic": "<expr>"} and return "<expr>".

        If parsing fails, return "T1" as a fallback.
        """
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "logic" in data:
                return data["logic"]
        except (ValueError, TypeError, ValidationError) as e:
            logger.warning(f"Error parsing logic expression: {e}")
        return "T1"

################################################################################
# PART 5: Evaluating the NxM matrix logic in Python
################################################################################


def logic_function(matrix: List[List[bool]], formula: str) -> bool:
    """
    Evaluates a simplified logic expression referencing x(i,j), 
    where i is the action index in [1..N], j is the test index in [1..M].
    matrix[i][j] indicates if test T(j+1) passes after action i+1.

    Example formula patterns:
      "∃ i in [1..N]: T1_i AND T2_i"
      "T1_N AND T2_N"
      "∃ i in [1..N]: (T1_i OR T2_i)"
      "T1_1"
    """
    formula = formula.strip()

    # Check for existential quantifier: "∃ i in [1..N]:"
    exist_pattern = re.compile(r'^∃ i in \[1\.\.N\]:\s*(.*)$')
    match = exist_pattern.match(formula)
    if match:
        inner_expr = match.group(1).strip()
        n = len(matrix)  # number of actions
        for i in range(n):
            if _evaluate_row_expr(matrix, i, inner_expr):
                return True
        return False
    else:
        # Otherwise, evaluate a formula that references explicit row indices (e.g. T2_3).
        return _evaluate_row_expr_no_i(matrix, formula)


def _evaluate_row_expr(matrix: List[List[bool]], row_i: int, expr: str) -> bool:
    """
    Evaluate an expression referencing Tj_i (like "T1_i AND T2_i" or "T1_i OR T2_i")
    for a specific row 'row_i' (0-based).
    """
    # Replace T(j)_i with either True or False, based on matrix[row_i][j-1].
    pattern = re.compile(r'T(\d+)_i')
    replaced_expr = expr

    matches = pattern.findall(expr)  # e.g. ["1", "2"]
    for j_str in matches:
        j_idx = int(j_str) - 1
        # If out-of-range, we fail
        if row_i < 0 or row_i >= len(matrix) or j_idx < 0 or j_idx >= len(matrix[row_i]):
            return False
        value_str = str(matrix[row_i][j_idx])  # "True" or "False"
        replaced_expr = replaced_expr.replace(f"T{j_str}_i", value_str)

    # Evaluate a simple AND/OR expression
    return _evaluate_simple_boolean_expr(replaced_expr)


def _evaluate_row_expr_no_i(matrix: List[List[bool]], formula: str) -> bool:
    """
    Evaluate an expression referencing Tj_k explicitly, e.g. "T1_2 AND T2_2", 
    which means "test #1 at row #2" and "test #2 at row #2".
    """
    replaced_expr = formula

    pattern = re.compile(r'T(\d+)_(\d+)')
    # This finds references like T1_2 => means test 1 at action 2
    # but zero-based => row=1, col=0
    matches = pattern.findall(formula)

    for (j_str, k_str) in matches:
        col = int(j_str) - 1
        row = int(k_str) - 1
        if row < 0 or row >= len(matrix):
            return False
        if col < 0 or col >= len(matrix[row]):
            return False
        value_str = str(matrix[row][col])  # "True"/"False"
        replaced_expr = replaced_expr.replace(f"T{j_str}_{k_str}", value_str)

    return _evaluate_simple_boolean_expr(replaced_expr)


def _evaluate_simple_boolean_expr(expr: str) -> bool:
    """
    Naive parser for expressions like "True AND False", "True OR True", or single "True"/"False".
    Splits on ' AND ' or ' OR ' and evaluates left-to-right.
    """
    expr = expr.strip()

    # AND:
    if " AND " in expr:
        parts = expr.split(" AND ")
        return all(_parse_bool_token(part.strip()) for part in parts)

    # OR:
    if " OR " in expr:
        parts = expr.split(" OR ")
        return any(_parse_bool_token(part.strip()) for part in parts)

    # Single token "True" or "False"
    return _parse_bool_token(expr)


def _parse_bool_token(token: str) -> bool:
    """
    Convert "True" -> True, "False" -> False, else warn and return False.
    """
    if token == "True":
        return True
    elif token == "False":
        return False
    else:
        logger.warning(f"Unexpected token in boolean expr: {token}")
        return False
