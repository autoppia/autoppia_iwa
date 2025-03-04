import random
import json
import logging
from typing import List
from dependency_injector.wiring import Provide

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.utils import transform_image_into_base64
from autoppia_iwa.src.shared.web_utils import get_html_and_screenshot
logger = logging.getLogger(__name__)


class GlobalTaskGenerationPipeline:
    def __init__(self, web_project: WebProject, llm_service: ILLM = Provide[DIContainer.llm_service]):
        self.web_project = web_project
        self.llm_service = llm_service

    async def generate_tasks(self, use_case_name: str, num_prompts: int = 5) -> List[Task]:
        use_case = next(uc for uc in self.web_project.use_cases if uc["name"] == use_case_name)

        films = [self.web_project.random_generation_function(use_case["model_class"]) for _ in range(num_prompts)]

        examples_str = '\n\n'.join(
            f"{idx + 1}. Title: {film.title}\nGenre: {film.genre}\nDirector: {film.director}\nYear: {film.release_year}"
            for idx, film in enumerate(films)
        )

        llm_prompt = f"""
        Here are film examples:\n\n{examples_str}\n\nGenerate realistic user prompts for the use case: '{use_case_name}'.
        """

        messages = [
            {"role": "system", "content": "Generate realistic user task prompts."},
            {"role": "user", "content": llm_prompt}
        ]

        resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)
        prompts = json.loads(resp_text)

        tasks = []
        for prompt, film in zip(prompts, films):
            html, clean_html, screenshot, screenshot_desc = await get_html_and_screenshot(
                f"{self.web_project.frontend_url}/film/{film.id}"
            )

            task = Task(
                scope="global",
                web_project_id=self.web_project.id,
                prompt=prompt,
                url=f"{self.web_project.frontend_url}/film/{film.id}",
                html=str(html),
                clean_html=str(clean_html),
                screenshot_description=screenshot_desc,
                screenshot=str(transform_image_into_base64(screenshot)),
                success_criteria=f"Film '{film.title}' detail page is loaded.",
                specifications=BrowserSpecification(),
                relevant_data={"film_id": film.id},
                tests=use_case["tests"]
            )
            tasks.append(task)

        random.shuffle(tasks)
        return tasks
