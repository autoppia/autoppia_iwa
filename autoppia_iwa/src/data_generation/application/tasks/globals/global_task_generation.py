import asyncio
import json
import random
import re
from typing import Dict, List, Optional

from dependency_injector.wiring import Provide
from loguru import logger
from PIL import Image
from pydantic import ValidationError

# Domain & framework imports (adjust paths as needed):
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot

# Prompt template (adjust path if it's in a different folder):
from .prompts import GLOBAL_TASK_GENERATION_PROMPT

# Adjust the import below to match where DraftTaskList is located in your codebase
from .schemas import DraftTaskList


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

    async def generate(self, prompts_per_use_case: int = 5) -> List[Task]:
        """
        Generate tasks for all use cases in the web project.
        """
        logger.info(f"Generating tasks for all use cases with {prompts_per_use_case} tasks each.")
        all_tasks: List[Task] = []

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
                logger.error(f"Error generating tasks for {use_case.name}: {str(e)}")
                continue

        logger.info(f"Total generated tasks across all use cases: {len(all_tasks)}")
        return all_tasks

    async def generate_tasks_for_use_case(self, use_case: UseCase, num_prompts: int = 5) -> List[Task]:
        """
        Generate tasks for a specific use case by calling the LLM with relevant context.
        """
        # 1) Gather random model instances to inject into the prompt (if applicable)
        random_instances_str = await self._gather_random_instances(use_case, num_prompts)

        # 2) Build the LLM prompt using a template
        prompt_examples_str = "\n".join(use_case.prompt_examples)

        # Luego usas esta variable en tu formato
        llm_prompt = GLOBAL_TASK_GENERATION_PROMPT.format(
            use_case_name=use_case.name,
            use_case_description=use_case.description,
            prompt_template=use_case.prompt_template,
            prompt_examples=prompt_examples_str,
            random_generated_instances_str=random_instances_str,
        )
        # 3) Call the LLM (with retry logic) and parse the JSON result
        tasks_data: List[Dict[str, str]] = await self._call_llm_with_retry(llm_prompt)

        # 4) For each parsed JSON object, create a Task
        #    We'll fetch the HTML and screenshot just once for all tasks
        url = self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url
        html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(url)

        tasks: List[Task] = []
        for item in tasks_data:
            prompt_text = item.get("prompt", "")

            try:
                task_obj = self._assemble_task(
                    web_project_id=self.web_project.id,
                    url=url,
                    prompt=prompt_text,
                    html=html,
                    clean_html=clean_html,
                    screenshot=screenshot,
                    screenshot_desc=screenshot_desc,
                )
                tasks.append(task_obj)
            except Exception as ex:
                logger.error(f"Could not assemble Task for prompt '{prompt_text}': {str(ex)}")

        # Shuffle them if you wish, for variety
        random.shuffle(tasks)
        return tasks

    async def _gather_random_instances(self, use_case: UseCase, num_prompts: int) -> str:
        """
        Example method to generate random instance data from your domain models,
        then return them as a JSON string for the LLM to reference.
        """
        if hasattr(self.web_project, "random_generation_function") and self.web_project.random_generation_function and getattr(use_case, "event", None) is not None:
            try:
                model_class = use_case.event
                generated_list = []
                for _ in range(num_prompts):
                    instance = self.web_project.random_generation_function(model_class)
                    # Convert to dict if possible
                    if hasattr(instance, "model_dump"):
                        instance_data = instance.model_dump()
                    elif hasattr(instance, "dict"):
                        instance_data = instance.dict()
                    else:
                        instance_data = {k: getattr(instance, k) for k in dir(instance) if not k.startswith("_") and not callable(getattr(instance, k))}
                    generated_list.append(instance_data)

                return "Random Generated Instances:\n" + json.dumps(generated_list, indent=2)
            except Exception as ex:
                logger.warning(f"Failed to gather random instances: {str(ex)}")

        return "No random instances available."

    async def _call_llm_with_retry(self, llm_prompt: str) -> List[Dict[str, str]]:
        """
        Calls the LLM with the given prompt, parsing JSON in a loop with retry.
        Returns a list of dict objects with at least {"prompt": ..., "success_criteria": ...}.
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates user tasks in strict JSON."},
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
                logger.error(f"Error on LLM call attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        logger.error(f"All {self.max_retries} attempts to parse LLM response have failed.")
        return []

    async def _parse_llm_response(self, resp_text: str) -> List[dict]:
        """
        Helper method to parse and validate the LLM response as a JSON array of tasks,
        each with "prompt" and "success_criteria" fields.
        """
        try:
            # Clean up possible Markdown code blocks like ```json ... ```
            cleaned_text = resp_text
            if resp_text.strip().startswith("'```") or resp_text.strip().startswith("```"):
                code_block_pattern = r'```(?:json)?\n([\s\S]*?)\n```'
                matches = re.search(code_block_pattern, resp_text)
                if matches:
                    cleaned_text = matches.group(1)
                else:
                    lines = resp_text.strip().split('\n')
                    if lines[0].startswith("'```") or lines[0].startswith("```"):
                        cleaned_text = '\n'.join(lines[1:-1] if lines[-1].endswith("```") else lines[1:])

            # Now parse the cleaned JSON
            data = json.loads(cleaned_text)

            # If data is a dict with known keys
            if isinstance(data, dict):
                if 'tasks' in data and isinstance(data['tasks'], list):
                    data = data['tasks']
                elif 'result' in data and isinstance(data['result'], list):
                    data = data['result']
                elif data.get("type") == "array" and "items" in data:
                    data = data["items"]
                elif "prompt" in data:
                    # It's a single-task dict
                    data = [data]
                else:
                    logger.warning(f"Unexpected JSON structure: {data}")
                    return []

            # At this point we expect data to be a list
            if not isinstance(data, list):
                logger.warning(f"Expected a list but got {type(data)}.")
                return []

            # Optionally validate with Pydantic DraftTaskList
            try:
                draft_list = DraftTaskList.model_validate(data)
                validated_tasks = []
                for item in draft_list.root:
                    validated_tasks.append({"prompt": item.prompt, "success_criteria": item.success_criteria or ""})
                return validated_tasks
            except ValidationError as ve:
                logger.warning(f"Pydantic validation error: {ve}, doing basic fallback validation.")
                # Fallback: just pull out "prompt" and "success_criteria"
                validated_tasks = []
                for i in data:
                    if isinstance(i, dict) and "prompt" in i:
                        validated_tasks.append({"prompt": i.get("prompt", ""), "success_criteria": i.get("success_criteria", "")})
                return validated_tasks

        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {je}")

            # Attempt a simpler extraction: look for [ { ... } ]
            try:
                json_pattern = r'\[\s*\{.*?\}\s*\]'
                array_match = re.search(json_pattern, resp_text, re.DOTALL)
                if array_match:
                    extracted_json = array_match.group(0)
                    data = json.loads(extracted_json)
                    validated_tasks = []
                    for i in data:
                        if isinstance(i, dict) and "prompt" in i:
                            validated_tasks.append({"prompt": i.get("prompt", ""), "success_criteria": i.get("success_criteria", "")})
                    return validated_tasks
            except Exception:
                pass
            return []

        except Exception as e:
            logger.error(f"Unexpected error parsing LLM response: {str(e)}")
            return []

    @staticmethod
    def _assemble_task(
        web_project_id: str,
        url: str,
        prompt: str,
        html: str,
        clean_html: str,
        screenshot: Optional[Image.Image],
        screenshot_desc: str,
    ) -> Task:
        """
        Assembles a final Task object from the filtered LLM data and loaded page info.
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
            relevant_data={},
        )
