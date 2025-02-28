from dependency_injector.wiring import Provide
import json
from typing import List, Dict
from pydantic import ValidationError
import asyncio
import logging
from autoppia_iwa.src.data_generation.domain.classes import Task, BrowserSpecification
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot, detect_interactive_elements
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.data_generation.application.tasks.local.prompts import (
    PHASE1_GENERATION_SYSTEM_PROMPT
)
from autoppia_iwa.src.di_container import DIContainer
from .schemas import DraftTaskList
from autoppia_iwa.src.demo_webs.classes import WebProject
import random

# Set up logging
logger = logging.getLogger(__name__)


class LocalTaskGenerationPipeline:
    def __init__(self, web_project: WebProject, llm_service: "ILLM" = Provide[DIContainer.llm_service]):
        self.web_project: WebProject = web_project
        self.llm_service: ILLM = llm_service
        self.max_retries: int = 3  # Maximum number of retries for LLM calls
        self.retry_delay: float = 0.1  # Delay between retries in seconds

    async def generate(self, page_url: str) -> List["Task"]:
        # Fetch the HTML and screenshot
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(page_url)
        interactive_elems = detect_interactive_elements(clean_html)

        # Phase 1: Draft generation
        draft_list = await self._phase1_generate_draft_tasks(
            page_url, clean_html, screenshot_desc, interactive_elems
        )

        # Construct final tasks
        final_tasks = [
            self._assemble_task(
                web_project_id=self.web_project.id,
                url=self.web_project.frontend_url,
                prompt=item.get("prompt", ""),
                html=html,
                clean_html=clean_html,
                screenshot=screenshot,
                screenshot_desc=screenshot_desc,
                success_criteria=item.get("success_criteria", ""),
                relevant_data=self.web_project.relevant_data
            )
            for item in draft_list
        ]

        def shuffle_tasks(final_tasks):
            random.shuffle(final_tasks)
            return final_tasks

        return shuffle_tasks(final_tasks)

    async def _phase1_generate_draft_tasks(
        self,
        current_url: str, 
        html_text: str,
        screenshot_text: str,
        interactive_elems: Dict
    ) -> List[dict]:
        """
        Phase 1: Generate a draft list of tasks based on the system prompt + user context.
        With retry mechanism for handling invalid JSON responses.
        """
        # Combine local prompts
        number_of_prompts = 20
        system_prompt = PHASE1_GENERATION_SYSTEM_PROMPT.replace("{number_of_prompts}", f"{number_of_prompts}")

        # User message with truncated HTML + screenshot text + interactive elements
        user_msg = (
            f"Current url:\n{current_url}\n\n"
            f"clean_html:\n{html_text[:1500]}\n\n"
            f"screenshot_description:\n{screenshot_text}\n\n"
            f"interactive_elements:\n{json.dumps(interactive_elems, indent=2)}"
        )

        # JSON schema for the response
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

        # Implement retry logic
        for attempt in range(self.max_retries):
            try:
                # Request the LLM to generate tasks (in JSON format)
                resp_text = await self.llm_service.async_predict(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    json_format=True,
                    schema=schema
                )

                # Try to parse the response
                validated_tasks = await self._parse_llm_response(resp_text)
                if validated_tasks:
                    logger.info(f"Successfully generated tasks for {current_url} on attempt {attempt + 1}")
                    for task in validated_tasks:
                        logger.debug(f"Generated task: {task}")
                    return validated_tasks

                # If we couldn't parse the response, log and retry
                logger.warning(f"Attempt {attempt + 1}: Failed to parse LLM response, retrying...")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Error during LLM prediction: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        # If all retries failed, return an empty list
        logger.error(f"All {self.max_retries} attempts failed for {current_url}")
        return []

    async def _parse_llm_response(self, resp_text: str) -> List[dict]:
        """Helper method to parse and validate the LLM response."""
        try:
            # First, ensure we have valid JSON
            data = json.loads(resp_text)

            # Handle different possible JSON structures
            if isinstance(data, dict):
                # If there's a 'tasks' or 'result' key containing the actual list
                if 'tasks' in data and isinstance(data['tasks'], list):
                    data = data['tasks']
                elif 'result' in data and isinstance(data['result'], list):
                    data = data['result']
                # Or if it has the JSON schema structure
                elif data.get("type") == "array" and "items" in data:
                    data = data["items"]
                # Fallback: wrap non-list data in a list if it's a dict with a prompt
                elif "prompt" in data:
                    data = [data]
                else:
                    logger.warning(f"Unexpected JSON structure: {data}")
                    return []

            # Ensure data is a list at this point
            if not isinstance(data, list):
                logger.warning(f"Expected list but got {type(data)}")
                return []

            # Validate the data using Pydantic
            draft_list = DraftTaskList.model_validate(data)
            validated_tasks = []

            for item in draft_list.root:
                validated_tasks.append({
                    "prompt": item.prompt,
                    "success_criteria": item.success_criteria or ""
                })

            return validated_tasks

        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {je}")
            return []
        except ValidationError as ve:
            logger.error(f"Pydantic validation error: {ve}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing LLM response: {str(e)}")
            return []

    def _assemble_task(
        self,
        web_project_id: int, 
        url: str,
        prompt: str,
        html: str,
        clean_html: str,
        screenshot: bytes,
        screenshot_desc: str,
        success_criteria: str,
        relevant_data: str
    ) -> "Task":
        """
        Assembles a final Task object from the filtered task data.
        """
        return Task(
            type="local",
            web_project_id=web_project_id,
            prompt=prompt,
            url=url,
            html=str(html),
            clean_html=str(clean_html),
            screenshot_desc=screenshot_desc,
            screenshot=str(transform_image_into_base64(screenshot)),
            success_criteria=success_criteria,
            specifications=BrowserSpecification(),
            relevant_data=relevant_data
        )
