import json
import random
from typing import Any, Dict, List

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot

from .prompts import GLOBAL_TASK_GENERATION_PROMPT


class GlobalTaskGenerationPipeline:
    def __init__(self, web_project: WebProject, llm_service: ILLM = Provide[DIContainer.llm_service]):
        self.web_project = web_project
        self.llm_service = llm_service

    async def generate(self, tasks_per_use_case: int = 10) -> List[Task]:
        """
        Generate tasks for all use cases in the web project.

        Args:
            tasks_per_use_case: Number of task variations to generate per use case

        Returns:
            List of Task objects across all use cases
        """
        logger.info(f"Generating tasks for all use cases with {tasks_per_use_case} tasks per use case")

        all_tasks = []

        # Check if we have use cases in the web project
        if not self.web_project.use_cases:
            logger.warning("No use cases found in web project")
            return all_tasks

        # Generate tasks for each use case directly from web_project
        for use_case in self.web_project.use_cases:
            logger.info(f"Generating tasks for use case: {use_case.name}")

            try:
                use_case_tasks = await self.generate_tasks_for_use_case(use_case=use_case, num_prompts=tasks_per_use_case)

                all_tasks.extend(use_case_tasks)
                logger.info(f"Generated {len(use_case_tasks)} tasks for use case: {use_case.name}")

            except Exception as e:
                logger.error(f"Error generating tasks for use case {use_case.name}: {str(e)}")
                # Continue with next use case instead of stopping the process
                continue

        logger.info(f"Generated {len(all_tasks)} global tasks across all use cases")
        return all_tasks

    async def generate_tasks_for_use_case(self, use_case: UseCase, num_prompts: int = 10) -> List[Task]:
        """
        Generate tasks for a specific use case.

        Args:
            use_case: The UseCase object to generate tasks for
            num_prompts: Number of task variations to generate

        Returns:
            List of Task objects
        """
        logger.debug(f"Generating {num_prompts} tasks for use case: {use_case.name}")

        # Generate examples string for the prompt
        examples_str = self._get_examples_for_use_case(use_case, num_prompts)

        # Generate prompts using LLM
        tasks = await self._generate_llm_prompts(use_case, examples_str, num_prompts)

        # Shuffle tasks to ensure randomness
        random.shuffle(tasks)

        return tasks

    def _get_examples_for_use_case(self, use_case: UseCase, num_prompts: int) -> str:
        """Get formatted examples for a use case"""
        # Generate model instances for task examples
        model_class = use_case.event

        if self.web_project.random_generation_function:
            # For movie app example
            if use_case.name == "Search film":
                films = [self.web_project.random_generation_function(model_class) for _ in range(num_prompts)]
                examples_str = self._format_film_examples(films)
            else:
                # For other use cases, provide relevant data from the web project
                examples_str = self._format_use_case_data(use_case.name)
        else:
            examples_str = f"Use case: {use_case.name}\nSuccess criteria: {use_case.success_criteria}"

        return examples_str

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
        if not self.web_project.relevant_data:
            return f"Use case: {use_case_name}"

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
        tests = use_case.test_examples

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
            num_prompts=num_prompts,
        )

        messages = [{"role": "system", "content": "Generate realistic user task prompts based on the provided use case."}, {"role": "user", "content": llm_prompt}]

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
        url = self._get_representative_url()

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
                    tests=use_case.test_examples,
                )
                tasks.append(task)

            except Exception as e:
                logger.exception(f"Error creating task from prompt: {str(e)}")

        return tasks

    def _get_representative_url(self) -> str:
        """Get a representative URL for the tasks"""
        # Default to frontend URL
        url = self.web_project.frontend_url

        # Try to get a more specific URL if available
        if hasattr(self.web_project, "urls") and self.web_project.urls:
            url = self.web_project.urls[0]

        return url
