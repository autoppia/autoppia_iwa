import asyncio
import json
from typing import Dict, List, Optional

from dependency_injector.wiring import Provide

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.data_generation.domain.classes import TaskDifficultyLevel, TaskPromptForUrl
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.infrastructure.llm_service import ILLMService
from autoppia_iwa.src.shared.utils import extract_html
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis, SinglePageAnalysis

# Constants
SCHEMA_FILE_NAMES = {
    TaskDifficultyLevel.EASY: "task_prompt_generation_schema_easy.json",
    TaskDifficultyLevel.MEDIUM: "task_prompt_generation_schema_medium.json",
    TaskDifficultyLevel.HARD: "task_prompt_generation_schema_hard.json",
}

# Prompt Templates
SYSTEM_MSG = """You are an expert in analyzing websites to identify manual tasks users can perform. Your task is to generate high-level, actionable 
instructions for tasks a user can do using a mouse and/or keyboard. 

Rules for generating tasks:
1. Focus only on manual actions (e.g., clicking buttons, filling forms).
2. Do not include visual tasks (e.g., reading content, reviewing images).
3. Avoid dummy actions like navigating to the homepage or refreshing the page.
4. Group related or follow-up actions into a single prompt when appropriate.
5. Ensure all tasks are clear, actionable, and concise, and match the specified difficulty level."""

# User Message Template
USER_MSG_TEMPLATE = """Generate {num_prompts} {difficulty_level}-level tasks that a user can perform on the webpage. Use the following information to create the tasks:

1. **HTML Content**: {html_source}
2. **Summary of Analysis**: {summary_page_url}

Guidelines for task generation:
- Ensure tasks are specific and actionable.
- Match the difficulty level: {difficulty_level}.
- Avoid dummy actions like navigating to the homepage or refreshing the page.
- Combine related or follow-up actions into a single task when appropriate."""


class TaskPromptGenerator:
    def __init__(
        self,
        web_analysis: DomainAnalysis,
        num_prompts_per_url: int = 1,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
    ) -> None:
        self.web_analysis = web_analysis
        self.llm_service = llm_service
        self.num_prompts_per_url = num_prompts_per_url

    def generate_prompts_for_domain(
        self,
        task_difficulty_level: TaskDifficultyLevel = TaskDifficultyLevel.EASY,
    ) -> List[TaskPromptForUrl]:
        """
        Generates prompts for ALL pages in the domain by calling the single-URL method for each.

        Args:
            task_difficulty_level (TaskDifficultyLevel): The difficulty level for tasks. Defaults to TaskDifficultyLevel.EASY.

        Returns:
            List[TaskPromptForUrl]: A list of TaskPromptForUrl objects, each containing a page URL and its associated task prompts.
        """
        domain_prompts = []
        for page_analysis in self.web_analysis.analyzed_urls:
            prompts_for_url = asyncio.run(self.generate_task_prompts_for_url(page_analysis.page_url, page_analysis.html_source, task_difficulty_level))
            domain_prompts.append(prompts_for_url)
        return domain_prompts

    async def generate_task_prompts_for_url(
        self,
        specific_url: str,
        current_html: Optional[str] = None,
        task_difficulty_level: TaskDifficultyLevel = TaskDifficultyLevel.EASY,
    ) -> TaskPromptForUrl:
        """
        Generates prompts for a SINGLE specific URL.

        Args:
            specific_url (str): The URL for which to generate prompts.
            current_html (Optional[str]): HTML for the current URL. If not provided, it will be extracted.
            task_difficulty_level (TaskDifficultyLevel): The difficulty level for tasks. Defaults to TaskDifficultyLevel.EASY.

        Returns:
            A dict with:
                - "page_url": The URL
                - "task_prompts": List of generated/refined tasks
        """
        page_analysis = self._get_page_analysis(specific_url)
        if not current_html:
            current_html = await extract_html(specific_url)

        raw_content = self._call_llm_for_raw_tasks(
            html_source=current_html,
            summary_page_url=page_analysis.web_summary,
            task_difficulty_level=task_difficulty_level,
        )
        # raw_content_dict = json.loads(raw_content.replace("\n", "\\n"))
        # TODO - SEEMS WE MISSING AN OUTPUT HERE
        tasks_list = raw_content_dict["tasks"]
        return TaskPromptForUrl(page_url=specific_url, task_prompts=tasks_list)

    def _call_llm_for_raw_tasks(
        self,
        html_source: str,
        summary_page_url: Dict,
        task_difficulty_level: TaskDifficultyLevel,
    ) -> str:
        # Format the user message with dynamic inputs
        user_message = USER_MSG_TEMPLATE.format(
            num_prompts=self.num_prompts_per_url,
            difficulty_level=task_difficulty_level.value,
            html_source=html_source,
            summary_page_url=summary_page_url,
        )

        messages = [{"role": "system", "content": SYSTEM_MSG}, {"role": "user", "content": user_message}]

        response = self.llm_service.make_request(
            message_payload=messages,
            chat_completion_kwargs={"temperature": 0.1, "top_k": 40, "response_format": {"type": "json_object", "schema": self._load_task_schema(task_difficulty_level)}},
        )

        if not response:
            raise ValueError("The LLM response is empty or invalid.")

        return response

    def _get_page_analysis(self, target_url: str) -> SinglePageAnalysis:
        """
        Finds and returns the SinglePageAnalysis object for a given URL.
        Raises ValueError if not found.
        """
        for page in self.web_analysis.analyzed_urls:
            if page.page_url == target_url:
                return page
        raise ValueError(f"URL '{target_url}' not found in domain analysis.")

    @staticmethod
    def _load_task_schema(task_difficulty_level: TaskDifficultyLevel) -> Dict:
        """Loads the task schema based on the difficulty level."""
        schema_file_name = SCHEMA_FILE_NAMES[task_difficulty_level]
        task_schema_path = PROJECT_BASE_DIR / f"config/schemas/task_prompt_generator/{schema_file_name}"
        with task_schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)
