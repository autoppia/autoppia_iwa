import json
from typing import Dict, List, Any

from dependency_injector.wiring import Provide
from pydantic import ValidationError
from PIL import Image
from autoppia_iwa.src.data_generation.application.tasks.local.prompts import (
    LOCAL_TASKS_CONTEXT_PROMPT,
    PHASE1_GENERATION_SYSTEM_PROMPT,
    PHASE2_CONCEPT_FILTER_PROMPT,
    PHASE2_FEASIBILITY_FILTER_PROMPT,
    PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT,
)
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements, get_html_and_screenshot

from .schemas import DraftTaskList, FilterTaskList


class LocalTaskGenerationPipeline:
    def __init__(self, web_project: WebProject, llm_service: "ILLM" = Provide[DIContainer.llm_service]):
        self.web_project: WebProject = web_project
        self.llm_service: ILLM = llm_service

    async def generate(self, page_url: str) -> List["Task"]:
        # Fetch the HTML and screenshot
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(page_url)
        interactive_elems = detect_interactive_elements(clean_html)

        # Phase 1: Draft generation
        draft_list = await self._phase1_generate_draft_tasks(clean_html, screenshot_desc, interactive_elems)

        # Phase 2: Three successive filters
        feasible_list = await self._phase2_filter(draft_list, PHASE2_FEASIBILITY_FILTER_PROMPT, clean_html, screenshot_desc, interactive_elems)
        success_list = await self._phase2_filter(feasible_list, PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT, clean_html, screenshot_desc, interactive_elems)
        concept_list = await self._phase2_filter(success_list, PHASE2_CONCEPT_FILTER_PROMPT, clean_html, screenshot_desc, interactive_elems)

        # Construct final tasks
        final_tasks = [
            self._assemble_task(
                url=self.web_project.frontend_url,
                prompt=item.get("prompt", ""),
                html=html,
                clean_html=clean_html,
                screenshot=screenshot,
                screenshot_desc=screenshot_desc,
                success_criteria=item.get("success_criteria", ""),
                relevant_data=self.web_project.relevant_data,
            )
            for item in concept_list
        ]
        return final_tasks

    async def _phase1_generate_draft_tasks(self, html_text: str, screenshot_text: str, interactive_elems: Dict) -> List[dict]:
        """
        Phase 1: Generate a draft list of tasks based on the system prompt + user context.
        """
        # Combine local prompts
        system_prompt = LOCAL_TASKS_CONTEXT_PROMPT + PHASE1_GENERATION_SYSTEM_PROMPT

        # User message with truncated HTML + screenshot text + interactive elements
        user_msg = f"clean_html:\n{html_text[:1500]}\n\n" f"screenshot_description:\n{screenshot_text}\n\n" f"interactive_elements:\n{json.dumps(interactive_elems, indent=2)}"

        # JSON schema for the response
        schema = {"type": "array", "items": {"type": "object", "properties": {"prompt": {"type": "string"}, "success_criteria": {"type": "string"}}, "required": ["prompt"]}}

        try:
            # Request the LLM to generate tasks (in JSON format)
            resp_text = await self.llm_service.async_predict(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}], json_format=True, schema=schema)

            # Parse and handle different possible JSON structures
            try:
                data = json.loads(resp_text)
                if isinstance(data, dict):
                    # If there's a 'result' key containing the actual list
                    if 'result' in data and isinstance(data['result'], list):
                        data = data['result']
                    # Or if it has the JSON schema structure
                    elif data.get("type") == "array" and "items" in data:
                        data = data["items"]
                    else:
                        # Fallback: wrap non-list data in a list if it's a dict
                        data = [data]

                # At this point, data should be a list
                draft_list = DraftTaskList.model_validate(data)

                validated_tasks = []
                for item in draft_list.root:
                    validated_tasks.append({"prompt": item.prompt, "success_criteria": item.success_criteria or ""})
                return validated_tasks
            except ValidationError as ve:
                print(f"Pydantic validation error (Phase 1): {ve}")
                return []
        except Exception as e:
            print(f"Error processing draft tasks: {e}")
            return []

    async def _phase2_filter(self, tasks: List[dict], filter_prompt: str, html_text: str, screenshot_text: str, interactive_elems: Dict) -> List[dict]:
        """
        Phase 2: Filter out tasks in 3 steps (feasibility, success criteria, concept).
        Each step uses a system prompt and the current tasks as the user context.
        The LLM is expected to respond with an array of objects,
        each specifying "decision" (keep|discard), "prompt", and "success_criteria".
        """
        if not tasks:
            return []

        # Convert the current list of tasks to JSON
        tasks_json = json.dumps(tasks, indent=2)

        # Combine the system prompt
        system_prompt = LOCAL_TASKS_CONTEXT_PROMPT + filter_prompt

        # The user message provides the truncated HTML, screenshot text,
        # interactive elements, and the current tasks to be filtered
        user_msg = (
            f"clean_html:\n{html_text[:1500]}\n\n"
            f"screenshot_description:\n{screenshot_text}\n\n"
            f"interactive_elements:\n{json.dumps(interactive_elems, indent=2)}\n\n"
            f"Current tasks:\n{tasks_json}"
        )

        # Define the expected JSON schema
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"decision": {"type": "string", "enum": ["keep", "discard"]}, "prompt": {"type": "string"}, "success_criteria": {"type": "string"}},
                "required": ["decision", "prompt"],
            },
        }

        try:
            # Request the LLM to filter the tasks
            resp_text = await self.llm_service.async_predict(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}], json_format=True, schema=schema)
            try:
                # Parse the JSON response
                data = json.loads(resp_text)

                # Handle different response formats
                if isinstance(data, dict):
                    # If the response is a dict and has a "result" key
                    if 'result' in data and isinstance(data['result'], list):
                        data = data['result']
                    # Or if it has the JSON schema structure
                    elif data.get("type") == "array" and "items" in data:
                        data = data["items"]
                    else:
                        # Fallback: wrap non-list data in a list if it's a dict
                        data = [data]

                # Now data should be a list. Validate it.
                filter_list = FilterTaskList.model_validate(data)

                # Keep tasks with decision == "keep"
                kept = []
                for item in filter_list.root:
                    if item.decision.strip().lower() == "keep":
                        kept.append({"prompt": item.prompt, "success_criteria": item.success_criteria or ""})
                return kept

            except ValidationError as ve:
                print(f"Pydantic validation error (Phase 2): {ve}")
                # If there's a validation error, return the original tasks unfiltered
                return tasks
        except Exception as e:
            print(f"Error in filter process: {e}")
            # Return the original tasks if something else breaks
            return tasks

    @staticmethod
    def _assemble_task(url: str, prompt: str, html: str, clean_html: str, screenshot: Image.Image, screenshot_desc: str, success_criteria: str, relevant_data: Dict[str, Any]) -> "Task":
        """
        Assembles a final Task object from the filtered task data.
        """
        return Task(
            type="local",
            prompt=prompt,
            url=url,
            html=str(html),
            clean_html=str(clean_html),
            screenshot_description=screenshot_desc,
            screenshot=str(transform_image_into_base64(screenshot)),
            success_criteria=success_criteria,
            specifications=BrowserSpecification(),
            relevant_data=relevant_data,
        )
