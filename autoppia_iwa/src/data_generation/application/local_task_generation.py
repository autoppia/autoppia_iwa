# file: local_task_generation_pipeline.py

import re
import json
from typing import List
from autoppia_iwa.src.data_generation.domain.classes import Task, BrowserSpecification
from autoppia_iwa.src.llms.domain.interfaces import ILLMService

# [MODIFIED] Import detect_interactive_elements
from autoppia_iwa.src.shared.utils import get_html_and_screenshot, detect_interactive_elements

################################################################################
# Utility to extract raw JSON from fenced ```json ... ```
################################################################################


def extract_json_in_markdown(text: str) -> str:
    pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()

################################################################################
# Prompts
################################################################################


LOCAL_TASKS_CONTEXT_PROMPT = """
You generate and refine single-page user tasks for a website, using:
1) Draft generation
2) Feasibility & success criteria filtering
3) Concept/off-topic filtering
"""

# -----------------------------------------------------------------------------
# [MODIFIED] Enhanced Phase 1 prompt with instructions for more variety:
# -----------------------------------------------------------------------------
PHASE1_GENERATION_SYSTEM_PROMPT = """
You are a local tasks generator for a website page. 
You have:
 - A 'clean_html' snippet.
 - A 'screenshot_description'.
 - A list of 'interactive_elements' (forms, links, buttons, toggles, inputs).

**Requirements**:
1. Generate 4-6 user tasks for this page. 
2. Each task must be a real user scenario (no developer or code editing steps).
3. Enforce variety:
   - If there is at least one form, create a task that fills and submits the form.
   - If there's a search bar, create a task that performs a search.
   - If toggles/accordions exist, create a task to toggle or expand them.
   - Limit link-click tasks to at most 2.
4. Each task must be testable:
   - "prompt": brief user instruction
   - "success_criteria": how we know the user succeeded
5. Return valid JSON array:
[
  {
    "prompt": "...",
    "success_criteria": "..."
  },
  ...
]

Be sure each prompt references actual, existing elements from the snippet or 'interactive_elements'.
"""

PHASE2_FEASIBILITY_FILTER_PROMPT = """
Remove tasks referencing elements that definitely do not exist 
in 'clean_html' or the 'interactive_elements'.
If a task might be referencing something that partially matches 
(e.g., a form with name 'search_form' vs 'searchForm'), keep it.

Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove","reason":"..."},
  ...
]
"""


PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT = """
Remove tasks with vague or missing success criteria.
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove"},
  ...
]
"""

PHASE2_CONCEPT_FILTER_PROMPT = """
Remove off-topic or dev-oriented tasks.
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove"},
  ...
]
"""

################################################################################
# LocalTaskGenerationPipeline
################################################################################


class LocalTaskGenerationPipeline:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    async def generate_local_tasks(self, page_url: str) -> List[Task]:
        # 1) Get HTML & screenshot
        clean_html, screenshot_desc = await get_html_and_screenshot(page_url)
        # [ADDED] Parse interactive elements
        interactive_elems = detect_interactive_elements(clean_html)

        # 2) Phase 1: Draft
        draft_list = self._phase1_generate_draft_tasks(clean_html, screenshot_desc, interactive_elems)

        # 3) Filter chain
        feasible_list = self._phase2_filter(draft_list, PHASE2_FEASIBILITY_FILTER_PROMPT, clean_html, screenshot_desc, interactive_elems)
        success_list = self._phase2_filter(feasible_list, PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT, clean_html, screenshot_desc, interactive_elems)
        concept_list = self._phase2_filter(success_list, PHASE2_CONCEPT_FILTER_PROMPT, clean_html, screenshot_desc, interactive_elems)

        # 4) Final assembly
        final_tasks = [self._assemble_task(page_url, item) for item in concept_list]
        return final_tasks

    # -----------------------------------------------------------------------------
    # [MODIFIED] Phase 1: add "interactive_elements" in the user message
    # -----------------------------------------------------------------------------
    def _phase1_generate_draft_tasks(self, html_text: str, screenshot_text: str, interactive_elems: dict) -> List[dict]:
        system_prompt = LOCAL_TASKS_CONTEXT_PROMPT + PHASE1_GENERATION_SYSTEM_PROMPT
        user_msg = (
            f"clean_html:\n{html_text[:1500]}\n\n"
            f"screenshot_description:\n{screenshot_text}\n\n"
            f"interactive_elements:\n{json.dumps(interactive_elems, indent=2)}"
        )

        # Try higher temperature for more variety
        resp = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            chat_completion_kwargs={"temperature": 0.9, "max_tokens": 1500},
        )

        resp_clean = extract_json_in_markdown(resp or "")
        try:
            parsed = json.loads(resp_clean)
            if isinstance(parsed, list):
                return parsed
        except Exception as e:
            print(f"Error parsing draft tasks response: {e}")
        return []
    # -----------------------------------------------------------------------------
    # [MODIFIED] Phase 2 feasibility check: also pass interactive elements
    # -----------------------------------------------------------------------------

    def _phase2_filter(self, tasks: List[dict], filter_prompt: str,
                       html_text: str, screenshot_text: str, interactive_elems: dict) -> List[dict]:
        if not tasks:
            return []
        tasks_json = json.dumps(tasks, indent=2)
        user_msg = (
            f"clean_html:\n{html_text[:1500]}\n\n"
            f"screenshot_description:\n{screenshot_text}\n\n"
            f"interactive_elements:\n{json.dumps(interactive_elems, indent=2)}\n\n"
            f"Current tasks:\n{tasks_json}"
        )
        system_prompt = LOCAL_TASKS_CONTEXT_PROMPT + filter_prompt
        resp = self._call_llm(system_prompt, user_msg)
        resp_clean = extract_json_in_markdown(resp)

        kept = []
        try:
            result = json.loads(resp_clean)
            for item in result:
                if item.get("decision", "").lower() == "keep":
                    kept.append({
                        "prompt": item.get("prompt", ""),
                        "success_criteria": item.get("success_criteria", "")
                    })
        except Exception as e:
            print(f"Error parsing filter LLM response: {e}")
            kept = tasks
        return kept

    def _assemble_task(self, url: str, data: dict) -> Task:
        return Task(
            type="local",
            prompt=data.get("prompt", ""),
            url=url,
            success_criteria=data.get("success_criteria", ""),
            specifications=BrowserSpecification()
        )

    def _call_llm(self, system_prompt: str, user_content: str) -> str:
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 1000},
        )
        return response or ""
