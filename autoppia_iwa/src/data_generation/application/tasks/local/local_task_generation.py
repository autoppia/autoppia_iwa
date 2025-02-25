from dependency_injector.wiring import Provide
import json
from typing import List, Dict
from pydantic import ValidationError
from autoppia_iwa.src.data_generation.domain.classes import Task, BrowserSpecification
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot, detect_interactive_elements
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.data_generation.application.tasks.local.prompts import (
    LOCAL_TASKS_CONTEXT_PROMPT,
    PHASE1_GENERATION_SYSTEM_PROMPT,
    PHASE2_FEASIBILITY_FILTER_PROMPT,
    PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT,
    PHASE2_CONCEPT_FILTER_PROMPT
)
from autoppia_iwa.src.di_container import DIContainer
from .schemas import DraftTaskList, FilterTaskList
from autoppia_iwa.src.demo_webs.classes import WebProject


class LocalTaskGenerationPipeline:
    def __init__(self, web_project: WebProject, llm_service: "ILLM" = Provide[DIContainer.llm_service]):
        self.web_project:WebProject = web_project
        self.llm_service:ILLM = llm_service

    async def generate(self, page_url: str) -> List["Task"]:
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(page_url)
        interactive_elems = detect_interactive_elements(clean_html)

        draft_list = await self._phase1_generate_draft_tasks(
            clean_html, screenshot_desc, interactive_elems
        )
        feasible_list = await self._phase2_filter(
            draft_list, PHASE2_FEASIBILITY_FILTER_PROMPT,
            clean_html, screenshot_desc, interactive_elems
        )
        success_list = await self._phase2_filter(
            feasible_list, PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT,
            clean_html, screenshot_desc, interactive_elems
        )
        concept_list = await self._phase2_filter(
            success_list, PHASE2_CONCEPT_FILTER_PROMPT,
            clean_html, screenshot_desc, interactive_elems
        )

        final_tasks = [
            self._assemble_task(
                url=page_url,
                prompt=item.get("prompt", ""),
                html=html,
                clean_html=clean_html,
                screenshot=screenshot,
                screenshot_desc=screenshot_desc,
                success_criteria=item.get("success_criteria", ""),
                relevant_data=self.web_project.relevant_data
            )
            for item in concept_list
        ]
        return final_tasks

    async def _phase1_generate_draft_tasks(
        self,
        html_text: str,
        screenshot_text: str,
        interactive_elems: Dict
    ) -> List[dict]:
        system_prompt = LOCAL_TASKS_CONTEXT_PROMPT + PHASE1_GENERATION_SYSTEM_PROMPT
        user_msg = (
            f"clean_html:\n{html_text[:1500]}\n\n"
            f"screenshot_description:\n{screenshot_text}\n\n"
            f"interactive_elements:\n{json.dumps(interactive_elems, indent=2)}"
        )

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "success_criteria": {"type": "string"}
                },
                "required": ["prompt"]
            }
        }

        try:
            resp_text = await self.llm_service.async_predict(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                json_format=True,
                schema=schema
            )

            try:
                data = json.loads(resp_text)
                if isinstance(data, dict) and data.get("type") == "array" and "items" in data:
                    data = data["items"]
                draft_list = DraftTaskList.model_validate(data)
                validated_tasks = []
                for item in draft_list.root:
                    validated_tasks.append({
                        "prompt": item.prompt,
                        "success_criteria": item.success_criteria or ""
                    })
                return validated_tasks
            except ValidationError as ve:
                print(f"Pydantic validation error (Phase 1): {ve}")
                return []
        except Exception as e:
            print(f"Error processing draft tasks: {e}")
            return []

    async def _phase2_filter(
        self,
        tasks: List[dict],
        filter_prompt: str,
        html_text: str,
        screenshot_text: str,
        interactive_elems: Dict
    ) -> List[dict]:
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

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string", "enum": ["keep", "discard"]},
                    "prompt": {"type": "string"},
                    "success_criteria": {"type": "string"}
                },
                "required": ["decision", "prompt"]
            }
        }

        try:
            resp_text = await self.llm_service.async_predict(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                json_format=True,
                schema=schema
            )

            try:
                data = json.loads(resp_text)
                if isinstance(data, dict) and data.get("type") == "array" and "items" in data:
                    data = data["items"]
                filter_list = FilterTaskList.model_validate(data)
                kept = []
                for item in filter_list.root:
                    if item.decision.strip().lower() == "keep":
                        kept.append({
                            "prompt": item.prompt,
                            "success_criteria": item.success_criteria or ""
                        })
                return kept
            except ValidationError as ve:
                print(f"Pydantic validation error (Phase 2): {ve}")
                return tasks
        except Exception as e:
            print(f"Error in filter process: {e}")
            return tasks

    def _assemble_task(
        self,
        url: str,
        prompt: str,
        html: str,
        clean_html: str,
        screenshot: bytes,
        screenshot_desc: str,
        success_criteria: str,
        relevant_data:str
    ) -> "Task":
        return Task(
            type="local",
            prompt=prompt,
            url=url,
            html=str(html),
            clean_html=str(clean_html),
            screenshot_desc=screenshot_desc,
            screenshot=str(transform_image_into_base64(screenshot)),
            success_criteria=success_criteria,
            specifications=BrowserSpecification(),
            relevant_data=relevant_data)
