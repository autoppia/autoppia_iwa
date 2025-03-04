import random
import json
from typing import List, Dict, Any
from dependency_injector.wiring import Provide
from loguru import logger
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject, UseCase
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot
from .prompts import GLOBAL_TASK_GENERATION_PROMPT


class GlobalTaskGenerationPipeline:
    def __init__(
        self, 
        web_project: WebProject, 
        llm_service: ILLM = Provide[DIContainer.llm_service]
    ):
        self.web_project = web_project
        self.llm_service = llm_service

    async def generate_tasks_for_use_case(self, use_case: UseCase, num_prompts: int = 10) -> List[Task]:
        """
        Generate tasks for a specific use case.
        Args:
            use_case: The UseCase object to generate tasks for
            num_prompts: Number of task variations to generate (default: 10)
        Returns:
            List of Task objects
        """
        logger.debug(f"Generating {num_prompts} tasks for use case: {use_case.name}")

        # Generate model instances for task examples
        model_class = use_case.event.__class__ if hasattr(use_case, "event") else None

        if not model_class and hasattr(self.web_project, "random_generation_function"):
            # For movie app example
            if use_case.name == "Search film":
                films = [self.web_project.random_generation_function(model_class) for _ in range(num_prompts)]
                examples_str = self._format_film_examples(films)
            else:
                # For other use cases, provide relevant data from the web project
                examples_str = self._format_use_case_data(use_case.name)
        else:
            examples_str = f"Use case: {use_case.name}\nSuccess criteria: {use_case.success_criteria}"

        # Generate prompts using LLM
        tasks = await self._generate_llm_prompts(use_case, examples_str, num_prompts)

        # Shuffle tasks to ensure randomness
        random.shuffle(tasks)
        return tasks

    def _format_film_examples(self, films: List[Any]) -> str:
        """Format film examples for LLM prompt"""
        return '\n\n'.join(
            f"{idx + 1}. Title: {film.title if hasattr(film, 'title') else film.name}\n"
            f"Genre: {film.genre if hasattr(film, 'genre') else 'Drama'}\n"
            f"Director: {film.director}\n"
            f"Year: {film.release_year if hasattr(film, 'release_year') else film.year}"
            for idx, film in enumerate(films)
        )

    def _format_use_case_data(self, use_case_name: str) -> str:
        """Format relevant data for a use case"""
        relevant_data = self.web_project.relevant_data.get(use_case_name, {})
        if not relevant_data:
            return f"Use case: {use_case_name}"

        formatted_data = []
        for key, value in relevant_data.items():
            if isinstance(value, dict):
                formatted_data.append(f"{key}:\n" + "\n".join(f"  - {k}: {v}" for k, v in value.items()))
            else:
                formatted_data.append(f"{key}: {value}")

        return "\n\n".join(formatted_data)

    async def _generate_llm_prompts(self, use_case: UseCase, examples_str: str, num_prompts: int) -> List[Task]:
        """Generate task prompts using LLM and create Task objects"""
        event_validation = None
        tests = use_case.test_examples if hasattr(use_case, "test_examples") else []

        for test in tests:
            if test.get("type") == "CheckEventTest":
                event_validation = test.get("validation_schema", {})
                break

        llm_prompt = GLOBAL_TASK_GENERATION_PROMPT.format(
            use_case_name=use_case.name,
            use_case_description=use_case.prompt_template,
            success_criteria=use_case.success_criteria,
            examples_str=examples_str,
            validation_schema=json.dumps(event_validation, indent=2) if event_validation else "No specific validation schema",
            num_prompts=num_prompts
        )

        messages = [
            {"role": "system", "content": "Generate realistic user task prompts based on the provided use case."},
            {"role": "user", "content": llm_prompt}
        ]

        logger.debug("Calling LLM to generate task prompts")
        try:
            resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)
            prompts = json.loads(resp_text)
            if not isinstance(prompts, list):
                logger.error(f"LLM returned invalid format for prompts: {type(prompts)}")
                return []

            logger.debug(f"Generated {len(prompts)} prompts for use case: {use_case.name}")

            # Create Task objects for each prompt
            tasks = await self._create_tasks_from_prompts(prompts, use_case)
            return tasks
        except Exception as e:
            logger.exception(f"Error generating prompts: {str(e)}")
            return []

    async def _create_tasks_from_prompts(self, prompts: List[Dict[str, str]], use_case: UseCase) -> List[Task]:
        """Create Task objects from the generated prompts"""
        tasks = []

        # Choose a representative URL for the tasks
        url = self.web_project.frontend_url
        if hasattr(self.web_project, "urls") and self.web_project.urls:
            # Use the first URL if available
            url = self.web_project.urls[0]

        # For each prompt, create a Task object
        for prompt_data in prompts:
            try:
                # Get the page HTML and screenshot
                html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(url)

                # Create the Task object
                task = Task(
                    scope="global",
                    web_project_id=self.web_project.id,
                    prompt=prompt_data.get("prompt", ""),
                    success_criteria=prompt_data.get("success_criteria", use_case.success_criteria),
                    url=url,
                    html=str(html),
                    clean_html=str(clean_html),
                    screenshot=str(transform_image_into_base64(screenshot)) if screenshot else "",
                    screenshot_description=screenshot_desc,
                    specifications=BrowserSpecification(),
                    relevant_data={},
                    tests=use_case.test_examples if hasattr(use_case, "test_examples") else []
                )
                tasks.append(task)
            except Exception as e:
                logger.exception(f"Error creating task from prompt: {str(e)}")

        return tasks
