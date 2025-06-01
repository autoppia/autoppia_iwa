# **composited_tasks_generator.py**

import asyncio
import json
import re
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger
from PIL import Image

# Import your existing GlobalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.globals.global_task_generation import GlobalTaskGenerationPipeline

# Adjust imports to match your actual project structure
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot

# Import the composited prompt template
from .prompts import COMPOSITED_TASK_GENERATION_PROMPT


class CompositedTasksGenerationPipeline:
    """
    Pipeline that:
    1) Invokes GlobalTaskGenerationPipeline to get individual tasks for each use case.
    2) Dynamically creates new multi-step tasks by combining them.
    3) Uses LLM to produce a cohesive, final prompt for the multi-step scenario.
    """

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
        # Reuse the existing GlobalTaskGenerationPipeline for the base tasks:
        self.global_task_pipeline = GlobalTaskGenerationPipeline(
            web_project=web_project,
            llm_service=llm_service,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    async def generate_composited_tasks(
        self,
        prompts_per_use_case: int = 5,
        number_of_composites: int = 5,
        tasks_per_composite: int = 2,
    ) -> list[Task]:
        """
        1) Generate individual tasks from all use cases (via GlobalTaskGenerationPipeline).
        2) Combine them into multi-step tasks using the LLM.
        3) Return the newly created composited tasks.

        :param prompts_per_use_case: how many tasks (prompts) to generate for each use case
        :param number_of_composites: how many composite tasks (scenarios) to create
        :param tasks_per_composite: how many base tasks to merge into each composite
        :return: list of assembled composited tasks
        """
        logger.info("Starting CompositedTasksGenerationPipeline...")

        # 1) Generate base tasks using the global pipeline
        logger.info(f"Fetching individual tasks with {prompts_per_use_case} prompts per use case...")
        base_tasks = await self.global_task_pipeline.generate(prompts_per_use_case=prompts_per_use_case)
        if not base_tasks:
            logger.warning("No base tasks were generated. Cannot create composited tasks.")
            return []

        # 2) Prepare the data for LLM
        prompts_list = [t.prompt for t in base_tasks]

        # 3) Request composite prompts from the LLM
        combined_prompts = await self._create_composite_prompts_with_llm(
            prompts_list,
            number_of_composites=number_of_composites,
            tasks_per_composite=tasks_per_composite,
        )

        # 4) Build new composited tasks from these prompts
        final_composited_tasks = []
        chosen_url = self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(chosen_url)

        for composite_prompt in combined_prompts:
            try:
                task_obj = self._assemble_composite_task(
                    composite_prompt=composite_prompt,
                    url=chosen_url,
                    html=html,
                    clean_html=clean_html,
                    screenshot=screenshot,
                    screenshot_desc=screenshot_desc,
                    relevant_data=self.web_project.relevant_data,
                )
                final_composited_tasks.append(task_obj)
            except Exception as e:
                logger.error(f"Error assembling composite task for prompt '{composite_prompt}': {e!s}")

        logger.info(f"Generated {len(final_composited_tasks)} composite tasks successfully.")
        return final_composited_tasks

    async def _create_composite_prompts_with_llm(
        self,
        base_task_prompts: list[str],
        number_of_composites: int,
        tasks_per_composite: int,
    ) -> list[str]:
        """
        Calls the LLM to create multi-step prompts from a list of base prompts.
        Returns a list of new prompt strings (each describing a multi-step scenario).
        """

        tasks_list_json = json.dumps(base_task_prompts, indent=2)
        llm_prompt = COMPOSITED_TASK_GENERATION_PROMPT.format(
            tasks_list_json=tasks_list_json,
            number_of_composites=number_of_composites,
            tasks_per_composite=tasks_per_composite,
        )

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that returns a JSON array of prompts.",
            },
            {
                "role": "user",
                "content": llm_prompt,
            },
        ]

        for attempt in range(self.max_retries):
            try:
                response_text = await self.llm_service.async_predict(messages=messages, json_format=True)
                parsed_data = self._parse_llm_list_of_strings(response_text)
                if parsed_data:
                    return parsed_data
                logger.warning(f"Attempt {attempt + 1}: Could not parse composite prompts, retrying...")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

            except Exception as e:
                logger.error(f"Error on LLM call attempt {attempt + 1}: {e!s}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        logger.error(f"All {self.max_retries} attempts to parse LLM composite prompts have failed.")
        return []

    def _parse_llm_list_of_strings(self, resp_text: str) -> list[str]:
        """
        Attempt to parse the given LLM response as a JSON list of strings.
        """
        try:
            # Remove any potential ```json blocks
            if resp_text.strip().startswith("```"):
                match = re.search(r"```(?:json)?\n([\s\S]*?)\n```", resp_text)
                if match:
                    resp_text = match.group(1)

            parsed = json.loads(resp_text)
            # Ensure it's a list of strings
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            logger.warning("Composite LLM response was not a list.")
            return []
        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error in composite prompt parsing: {je}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing composite LLM response: {e!s}")
            return []

    def _assemble_composite_task(
        self,
        composite_prompt: str,
        url: str,
        html: str,
        clean_html: str,
        screenshot: Image.Image | None,
        screenshot_desc: str,
        relevant_data: dict[str, Any],
    ) -> Task:
        """
        Builds a new Task object that merges multiple sub-tasks into one multi-step prompt.
        You can optionally store which tasks contributed to this composite in `milestones`.
        """
        return Task(
            scope="global",  # or "composite", if you prefer
            web_project_id=self.web_project.id,
            url=url,
            prompt=composite_prompt,
            html=str(html),
            clean_html=str(clean_html),
            screenshot_description=screenshot_desc,
            screenshot=str(transform_image_into_base64(screenshot)) if screenshot else "",
            specifications=BrowserSpecification(),
            relevant_data=relevant_data,
            use_case=None,  # Typically no single use_case for a composite
        )
