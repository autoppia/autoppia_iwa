import asyncio
import json
import logging
import random
from typing import Any

from dependency_injector.wiring import Provide
from PIL import Image
from pydantic import ValidationError

from autoppia_iwa.src.data_generation.application.tasks.local.prompts import PHASE1_GENERATION_SYSTEM_PROMPT
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements, get_html_and_screenshot

from .schemas import DraftTaskList

# Set up logging
logger = logging.getLogger(__name__)


class LocalTaskGenerationPipeline:
    def __init__(self, web_project: WebProject, llm_service: "ILLM" = Provide[DIContainer.llm_service]):
        self.web_project: WebProject = web_project
        self.llm_service: ILLM = llm_service
        self.max_retries: int = 3  # Maximum number of retries for LLM calls
        self.retry_delay: float = 0.1  # Delay between retries in seconds

    async def generate(self, number_of_prompts_per_url: int = 3, max_urls=5, random_urls=True):
        """Generate Local Tasks for a Web Project iterating all the urls"""
        all_tasks = []

        # Get the URLs to process based on parameters
        urls = self.web_project.urls

        # Apply random selection if requested
        if random_urls and len(urls) > max_urls:
            import random

            urls = random.sample(urls, max_urls)

        # Otherwise just take the first max_urls
        elif len(urls) > max_urls:
            urls = urls[:max_urls]

        for url in urls:
            logger.info(f"Generating local tasks for url {url}")
            local_tasks = await self.generate_per_url(page_url=url, number_of_prompts_per_url=number_of_prompts_per_url)
            all_tasks.extend(local_tasks)
            logger.info(f"Generated {len(local_tasks)} local tasks")

        return all_tasks  # Fixed the typo all_tasks2 -> all_tasks

    async def generate_per_url(self, page_url: str, number_of_prompts_per_url: int = 15) -> list["Task"]:
        # Fetch the HTML and screenshot
        self.number_of_prompts_per_url = number_of_prompts_per_url
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(page_url)
        interactive_elems = detect_interactive_elements(clean_html)

        # Phase 1: Draft generation
        draft_list = await self._phase1_generate_draft_tasks(page_url, clean_html, screenshot_desc, interactive_elems)

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
                relevant_data=self.web_project.relevant_data,
            )
            for item in draft_list
        ]

        def shuffle_tasks(final_tasks):
            random.shuffle(final_tasks)
            return final_tasks

        return shuffle_tasks(final_tasks)

    async def _phase1_generate_draft_tasks(self, current_url: str, html_text: str, screenshot_text: str, interactive_elems: dict) -> list[dict]:
        """
        Phase 1: Generate a draft list of tasks based on the system prompt + user context.
        With retry mechanism for handling invalid JSON responses.
        """
        # Combine local prompts
        system_prompt = PHASE1_GENERATION_SYSTEM_PROMPT.replace("{number_of_prompts_per_url}", f"{self.number_of_prompts_per_url}")

        # User message with truncated HTML + screenshot text + interactive elements
        user_msg = f"Current url:\n{current_url}\n\nclean_html:\n{html_text[:1500]}\n\nscreenshot_description:\n{screenshot_text}\n\ninteractive_elements:\n{json.dumps(interactive_elems, indent=2)}"

        # Implement retry logic
        for attempt in range(self.max_retries):
            try:
                messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}]
                # Request the LLM to generate tasks (in JSON format)
                resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)

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
                logger.error(f"Attempt {attempt + 1}: Error during LLM prediction: {e!s}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        # If all retries failed, return an empty list
        logger.error(f"All {self.max_retries} attempts failed for {current_url}")
        return []

    async def _parse_llm_response(self, resp_text: str) -> list[dict]:
        """Helper method to parse and validate the LLM response."""
        try:
            # Clean up response text if it's wrapped in Markdown code blocks
            # This handles cases like: '```json\n[...]\n```'
            cleaned_text = resp_text
            if resp_text.strip().startswith("'```") or resp_text.strip().startswith("```"):
                # Extract content between markdown code blocks
                import re

                code_block_pattern = r"```(?:json)?\n([\s\S]*?)\n```"
                matches = re.search(code_block_pattern, resp_text)
                if matches:
                    cleaned_text = matches.group(1)
                else:
                    # If regex doesn't match but we know it starts with backticks,
                    # try a simpler approach
                    lines = resp_text.strip().split("\n")
                    if lines[0].startswith("'```") or lines[0].startswith("```"):
                        # Remove first and last lines if they contain backticks
                        cleaned_text = "\n".join(lines[1:-1] if lines[-1].endswith("```") else lines[1:])

            # Now try to parse the cleaned JSON
            data = json.loads(cleaned_text)

            # Handle the case where data is directly a list of tasks
            if isinstance(data, list) and all(isinstance(item, dict) and "prompt" in item for item in data):
                validated_tasks = []
                for item in data:
                    validated_tasks.append({"prompt": item.get("prompt", ""), "success_criteria": item.get("success_criteria", "")})
                return validated_tasks

            # Handle different possible JSON structures
            if isinstance(data, dict):
                # If there's a 'tasks' or 'result' key containing the actual list
                if "tasks" in data and isinstance(data["tasks"], list):
                    data = data["tasks"]
                elif "result" in data and isinstance(data["result"], list):
                    data = data["result"]
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
            try:
                draft_list = DraftTaskList.model_validate(data)
                validated_tasks = []
                for item in draft_list.root:
                    validated_tasks.append({"prompt": item.prompt, "success_criteria": item.success_criteria or ""})
                return validated_tasks
            except ValidationError as ve:
                logger.warning(f"Pydantic validation error: {ve}, trying basic validation")
                # Basic validation if Pydantic fails
                validated_tasks = []
                for item in data:
                    if isinstance(item, dict) and "prompt" in item:
                        validated_tasks.append({"prompt": item.get("prompt", ""), "success_criteria": item.get("success_criteria", "")})
                return validated_tasks
        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {je}")
            # Attempt another cleanup approach if initial parsing fails
            try:
                # Try to extract just the JSON part using a more aggressive approach
                import re

                json_pattern = r"\[\s*\{.*?\}\s*\]"
                matches = re.search(json_pattern, resp_text, re.DOTALL)
                if matches:
                    extracted_json = matches.group(0)
                    data = json.loads(extracted_json)
                    validated_tasks = []
                    for item in data:
                        if isinstance(item, dict) and "prompt" in item:
                            validated_tasks.append({"prompt": item.get("prompt", ""), "success_criteria": item.get("success_criteria", "")})
                    return validated_tasks
            except Exception:
                pass
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing LLM response: {e!s}")
            return []

    @staticmethod
    def _assemble_task(web_project_id: str, url: str, prompt: str, html: str, clean_html: str, screenshot: Image.Image, screenshot_desc: str, success_criteria: str, relevant_data: Any) -> "Task":
        """
        Assembles a final Task object from the filtered task data.
        """
        return Task(
            scope="local",
            web_project_id=web_project_id,
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
