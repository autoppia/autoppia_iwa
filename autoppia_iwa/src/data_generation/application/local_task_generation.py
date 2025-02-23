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
Context: 
You are responsible for generating, refining, and validating single-page user tasks for a website through a structured, multi-phase process. This process is inspired by advanced autonomous evaluation frameworks like Infinite Web Arena (IWA) and consists of the following phases:

1. Draft Generation
   - **What:** Create initial task drafts using generative AI techniques to simulate realistic user interactions (e.g., navigation, search, filtering, and transactions) on a single-page interface.
   - **Why:** To generate a diverse set of scenarios that challenge web agents by mimicking dynamic, real-world website behaviors.
   - **How:** Leverage meta-programming and LLMs to produce a broad range of tasks that cover both common and edge-case interactions.

2. Feasibility & Success Criteria Filtering
   - **What:** Evaluate each task draft against predefined feasibility metrics and success criteria.
   - **Why:** To ensure that every task is executable within a real browser environment and that success can be objectively measured through both frontend (DOM analysis, network monitoring, visual verification) and backend (event tracking, state validation) tests.
   - **How:** Automatically filter out tasks that do not meet the criteria, refining the list to include only those with clear, testable outcomes.

3. Concept and Off-Topic Filtering
   - **What:** Review the refined tasks for conceptual coherence and alignment with the website’s objectives.
   - **Why:** To eliminate tasks that are off-topic or that fail to contribute meaningfully to evaluating user-agent interactions, ensuring the focus remains on realistic and valuable web scenarios.
   - **How:** Apply logical checks and thematic filtering to validate that each task contributes to a robust, scalable evaluation framework, similar to how IWA continuously introduces novel challenges to prevent overfitting and memorization.

Overall, your role is to create high-quality, executable tasks that:
- Reflect the complexities of modern web environments.
- Are grounded in both synthetic generation and logical validation.
- Provide clear, measurable outcomes for autonomous testing.
"""


# -----------------------------------------------------------------------------
# [MODIFIED] Enhanced Phase 1 prompt with instructions for more variety:
# -----------------------------------------------------------------------------
PHASE1_GENERATION_SYSTEM_PROMPT = """
We are on Phase 1: Task Prompts Generation
You are a local tasks generator for a website page. Local mean you generate tasks that can be complete within this website. 
You will be provided with:
 - Url of the website
 - A 'clean_html' snippet.
 - A 'screenshot_description' (done by a ML model that parses the UI into text for you to 'see')
 - A list of 'interactive_elements' (forms, links, buttons, toggles, inputs) so you can filter better whats important on the DOM.

**Requirements**:
1. Generate 6 user tasks for this page. 
2. Each task must be a real user scenario (no developer or code editing steps). Should be something a user may ask a 'Web Agent' to do on behalf of him.
3. Enforce variety:
   - If there is at least one form, create a task that fills and submits the form.
   - If there's a search bar, create a task that performs a search.
   - If toggles/accordions exist, create a task to toggle or expand them.
   - Asking to find a way to go to 'X' other url. 
   - Completing the core use-cases that website is for. For example, if we are in a ecommerce product page, adding to cart is the obvious use case. 
   - 

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
6. Do not include task like testing the functionality itself or developers stuff. this is for Users who want to automate or who want help when using the website.
7. Do not create tasks about 'knowledge' or finding info as we dont have a way to know in later phases if that task was completed. This include subjective tasks or opinions. 
This can be part of a more general task bun never the whole purpose. So, in summary, avoid fact checking, subjective, opinionated tast. 

Be sure each prompt references actual, existing elements from the snippet or 'interactive_elements'. 
Be sure the task is relevant to the contect the website is is. Do not ask ecommerce related task in wikipedia. 
"""

PHASE2_FEASIBILITY_FILTER_PROMPT = """
We are in Phase 2: Feasibility Filter.
Remove tasks referencing elements that definitely do not exist 
in 'clean_html' or the 'interactive_elements'.
If a task might be referencing something that partially matches 
(e.g., a form with name 'search_form' vs 'searchForm'), keep it.

#Output format:
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove","reason":"..."},
  ...
]
"""


PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT = """
We Are in Phase 2: Success Criteria Filtering. 
Remove tasks with vague or missing success criteria.
Success Criterial should be enough to verify if the Web Agent who will be in charge of completing this charge has actually completed it. 
So it cant be abstract or subjective. 

#Output format:
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove"},
  ...
]
"""

PHASE2_CONCEPT_FILTER_PROMPT = """So 
We Are in Phase 2: Contextual and concept Filtering
You need to Remove off-topic, dev-oriented task, task unrelated to what the website is about tasks. 
For example, if the task is about buying a product but we are in Wikipedia.com its unrelated and should be removed.
#Output format:
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

    async def generate(self, page_url: str) -> List[Task]:
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
