import asyncio
import json
import random
import re
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger
from PIL import Image

# Domain & framework imports (adjust paths as needed):
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot

# Prompt template (adjust path if it's in a different folder):
from .prompts import GLOBAL_TASK_GENERATION_PROMPT


class GlobalTaskGenerationPipeline:
    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        max_retries: int = 3,
        retry_delay: float = 0.1,
    ):
        self.web_project = web_project
        self.llm_service = llm_service
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def generate(self, prompts_per_use_case: int = 5) -> list[Task]:
        """
        Generate tasks for all use cases in the web project.
        """
        logger.info(f"Generating tasks for all use cases with {prompts_per_use_case} tasks each.")
        all_tasks: list[Task] = []

        # If there are no use cases, just return empty
        if not self.web_project.use_cases:
            logger.warning("No use cases found in web project.")
            return all_tasks

        for use_case in self.web_project.use_cases:
            logger.info(f"Generating tasks for use case: {use_case.name}")
            try:
                tasks_for_use_case = await self.generate_tasks_for_use_case(use_case, prompts_per_use_case)
                all_tasks.extend(tasks_for_use_case)
                logger.info(f"Generated {len(tasks_for_use_case)} tasks for use case '{use_case.name}'")
            except Exception as e:
                logger.error(f"Error generating tasks for {use_case.name}: {e!s}")
                continue

        logger.info(f"Total generated tasks across all use cases: {len(all_tasks)}")
        return all_tasks

    async def generate_tasks_for_use_case(self, use_case: UseCase, number_of_prompts: int = 5) -> list[Task]:
        """
        Generate tasks for a specific use case by calling the LLM with relevant context.
        """

        constraints_info = ""
        if hasattr(use_case, "generate_constraints"):
            constraints_info = use_case.generate_constraints()

        # Build the LLM prompt using a template
        if not use_case.additional_prompt_info:
            use_case.additional_prompt_info = f"GENERATE PROMPT LIKE: {use_case.get_example_prompts_str()}"
        llm_prompt = GLOBAL_TASK_GENERATION_PROMPT.format(
            use_case_name=use_case.name,
            use_case_description=use_case.description,
            additional_prompt_info=use_case.additional_prompt_info,
            constraints_info=constraints_info,
            number_of_prompts=number_of_prompts,
        )

        # Call the LLM (with retry logic) and parse the list of strings result
        prompt_list = await self._call_llm_with_retry(llm_prompt)
        print(prompt_list)
        # For each prompt string, create a Task
        # We'll fetch the HTML and screenshot just once for all tasks
        url = self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(url)

        tasks: list[Task] = []
        for prompt_text in prompt_list:
            try:
                replaced_prompt = use_case.apply_replacements(prompt_text)
                task_obj = self._assemble_task(
                    web_project_id=self.web_project.id,
                    url=url,
                    prompt=replaced_prompt,
                    html=html,
                    clean_html=clean_html,
                    screenshot=screenshot,
                    screenshot_desc=screenshot_desc,
                    use_case=use_case,
                    relevant_data=self.web_project.relevant_data,
                )
                tasks.append(task_obj)
            except Exception as ex:
                logger.error(f"Could not assemble Task for prompt '{prompt_text}': {ex!s}")

        # Shuffle them if you wish, for variety
        random.shuffle(tasks)
        return tasks

    async def _call_llm_with_retry(self, llm_prompt: str) -> list[str]:
        """
        Calls the LLM with the given prompt, parsing the response as a list of strings with retry.
        Returns a list of prompt strings.
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates user tasks as a list of strings."},
            {"role": "user", "content": llm_prompt},
        ]

        for attempt in range(self.max_retries):
            try:
                resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)
                parsed_data = await self._parse_llm_response(resp_text)
                if parsed_data:
                    return parsed_data
                logger.warning(f"Attempt {attempt + 1}: Could not parse LLM response, retrying...")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                logger.error(f"Error on LLM call attempt {attempt + 1}: {e!s}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        logger.error(f"All {self.max_retries} attempts to parse LLM response have failed.")
        return []

    async def _parse_llm_response(self, resp_text: str) -> list[str]:
        """
        Helper method to parse the LLM response as a list of strings.
        """
        try:
            # Clean up possible Markdown code blocks like ```json ... ```
            cleaned_text = resp_text
            if resp_text.strip().startswith("'```") or resp_text.strip().startswith("```"):
                code_block_pattern = r"```(?:json)?\n([\s\S]*?)\n```"
                matches = re.search(code_block_pattern, resp_text)
                if matches:
                    cleaned_text = matches.group(1)
                else:
                    lines = resp_text.strip().split("\n")
                    if lines[0].startswith("'```") or lines[0].startswith("```"):
                        cleaned_text = "\n".join(lines[1:-1] if lines[-1].endswith("```") else lines[1:])

            # Now parse the cleaned JSON
            data = json.loads(cleaned_text)

            # Ensure we have a list of strings
            if isinstance(data, list):
                # Convert any non-string items to strings if needed
                return [str(item) for item in data]
            else:
                logger.warning(f"Expected a list but got {type(data)}.")
                return []

        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {je}")
            # Attempt a simpler extraction: look for [ ... ]
            try:
                array_pattern = r'\[\s*".*?"\s*(?:,\s*".*?"\s*)*\]'
                array_match = re.search(array_pattern, resp_text, re.DOTALL)
                if array_match:
                    extracted_json = array_match.group(0)
                    data = json.loads(extracted_json)
                    return [str(item) for item in data]
            except Exception:
                pass
            return []

        except Exception as e:
            logger.error(f"Unexpected error parsing LLM response: {e!s}")
            return []

    @staticmethod
    def _assemble_task(
        web_project_id: str, url: str, prompt: str, html: str, clean_html: str, screenshot: Image.Image | None, screenshot_desc: str, use_case: UseCase, relevant_data: dict[str, Any]
    ) -> Task:
        """
        Assembles a final Task object from the prompt string and loaded page info.
        """
        return Task(
            scope="global",
            web_project_id=web_project_id,
            prompt=prompt,
            url=url,
            html=str(html),
            clean_html=str(clean_html),
            screenshot_description=screenshot_desc,
            screenshot=str(transform_image_into_base64(screenshot)) if screenshot else "",
            specifications=BrowserSpecification(),
            relevant_data=relevant_data,
            use_case=use_case,
        )
