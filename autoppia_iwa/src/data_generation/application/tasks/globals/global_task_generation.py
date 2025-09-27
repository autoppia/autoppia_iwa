import asyncio
import json
import random
import re
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger
from PIL import Image

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64

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

    async def generate(self, num_use_cases: int, prompts_per_use_case: int = 5) -> list[Task]:
        """
        Generate tasks for all use cases in the web project.
        """
        all_tasks: list[Task] = []

        # If there are no use cases, just return empty
        if not self.web_project.use_cases:
            logger.warning("No use cases found in web project.")
            return all_tasks

        use_cases = self.web_project.use_cases
        if num_use_cases:
            use_cases = random.sample(use_cases, min(num_use_cases, len(use_cases)))

        logger.info(f"Generating tasks for all use cases with {prompts_per_use_case} tasks each. Selected {len(use_cases)} use cases.")

        for use_case in use_cases:
            logger.info(f"Generating tasks for use case: {use_case.name}")
            try:
                tasks_for_use_case = await self.generate_tasks_for_use_case(use_case, prompts_per_use_case)
                all_tasks.extend(tasks_for_use_case)
                logger.info(f"Generated {len(tasks_for_use_case)} tasks for use case '{use_case.name}'")
            except Exception as e:
                logger.error(f"Error generating tasks for {use_case.name}: {e!s}")
                import traceback

                traceback.print_exc()
                continue

        logger.info(f"Total generated tasks across all use cases: {len(all_tasks)}")
        return all_tasks

    async def generate_tasks_for_use_case(self, use_case: UseCase, number_of_prompts: int = 5) -> list[Task]:
        """
        Generate tasks for a specific use case by calling the LLM with relevant context.
        """
        additional_system_prompt = None

        if hasattr(use_case, "generate_constraints"):
            constraints_info = use_case.generate_constraints()
        else:
            constraints_info = "**IMPORTANT:** Do **NOT** invent, assume, or include any constraints. No constraints are provided for this use case."
            additional_system_prompt = constraints_info

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
        prompt_list = await self._call_llm_with_retry(llm_prompt, additional_system_prompt=additional_system_prompt)
        # For each prompt string, create a Task
        # We'll fetch the HTML and screenshot just once for all tasks
        url = self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url
        # await get_html_and_screenshot(url)
        html, clean_html, screenshot, screenshot_desc = "", "", "", ""

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

    async def _call_llm_with_retry(self, llm_prompt: str, additional_system_prompt: str | None = None) -> list[str]:
        """
        Calls the LLM with the given prompt, parsing the response as a list of strings with retry.
        Returns a list of prompt strings.
        """
        base_system_prompt = "You are a helpful assistant that generates user tasks as a list of strings."
        system_prompt = f"{base_system_prompt} {additional_system_prompt}" if additional_system_prompt else base_system_prompt

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": llm_prompt}]

        for attempt in range(self.max_retries):
            try:
                resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)
                parsed_data = self._parse_llm_response(resp_text)
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

    def _parse_llm_response(self, resp_text: Any) -> list[str]:
        """
        Universal parser: siempre devuelve una lista de strings (prompts),
        limpiando <think> y dicts con claves raras.
        """
        try:
            # Si ya es lista (OpenAI)
            if isinstance(resp_text, list):
                return [str(item) for item in resp_text]

            # Si ya es dict con lista (DeepSeek a veces devuelve {"prompts": [...]} o {"</think>": [...]})
            if isinstance(resp_text, dict):
                for v in resp_text.values():
                    if isinstance(v, list):
                        return [str(item) for item in v]
                return []

            if isinstance(resp_text, str):
                cleaned = resp_text.strip()

                # 1) eliminar <think>...</think>
                cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()

                # 2) buscar primer array JSON válido
                match = re.search(r"\[[\s\S]*\]", cleaned)
                if match:
                    array_str = match.group(0)
                    data = json.loads(array_str)
                    if isinstance(data, list):
                        return [str(item) for item in data]

                # 3) intentar parsear como dict
                data = json.loads(cleaned)
                if isinstance(data, dict):
                    for v in data.values():
                        if isinstance(v, list):
                            return [str(item) for item in v]

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")

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
