# file: autoppia_iwa/src/data_generation/application/task_prompt_generator.py

import json
from typing import List, Optional
from dependency_injector.wiring import Provide
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.infrastructure.llm_service import ILLMService
from autoppia_iwa.src.shared.utils import extract_html
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis, SinglePageAnalysis

from ..domain.classes import TaskDifficultyLevel, TaskPromptForUrl

# Prompt Templates
SYSTEM_MSG = """You are an expert in creating realistic web-based tasks.
Generate tasks that match the given domain context and webpage details."""

# We’ll define some dynamic instructions for each difficulty level
# so the LLM has explicit instructions to produce varied tasks.
TASK_INSTRUCTION = {
    TaskDifficultyLevel.EASY: (
        "Generate short, single-step tasks. For example: clicking a button, filling a single text field, "
        "toggling a dropdown, or logging in if it is only one step. The tasks should be feasible in this context."
    ),
    TaskDifficultyLevel.MEDIUM: (
        "Generate moderate tasks that involve multiple steps. For example: logging in and updating profile info, "
        "searching a product and adding it to cart, or filling a multi-field form. The tasks should remain realistic."
    ),
    TaskDifficultyLevel.HARD: (
        "Generate longer, multi-step tasks or full workflows. For example: from logging in, searching for an item, "
        "adding it to the cart, applying a coupon, and checking out, or any end-to-end process with multiple steps."
    ),
}


class TaskPromptGenerator:
    def __init__(
        self,
        web_analysis: DomainAnalysis,
        num_prompts_per_url: int = 1,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
    ) -> None:
        """
        :param web_analysis: domain-level analysis object
        :param num_prompts_per_url: how many prompts to generate for each URL
        :param llm_service: LLM service injection
        """
        self.web_analysis = web_analysis
        self.llm_service = llm_service
        self.num_prompts_per_url = num_prompts_per_url

    def generate_prompts_for_domain(
        self,
        task_difficulty_level: Optional[TaskDifficultyLevel] = None,
    ) -> List[TaskPromptForUrl]:
        """
        Generate tasks for all pages in the domain. If no difficulty level is provided,
        we generate easy, medium, and hard prompts for each page to ensure variety.

        Returns a list of TaskPromptForUrl objects.
        """
        domain_prompts = []
        difficulty_levels = [task_difficulty_level] if task_difficulty_level else [
            TaskDifficultyLevel.EASY,
            TaskDifficultyLevel.MEDIUM,
            TaskDifficultyLevel.HARD
        ]

        for page_analysis in self.web_analysis.analyzed_urls:
            page_url = page_analysis.page_url
            current_html = page_analysis.html_source or extract_html(page_url)

            # For each difficulty level, generate prompts
            combined_prompts = []
            for lvl in difficulty_levels:
                single_set = self._generate_prompts_for_url_and_level(
                    specific_url=page_url,
                    current_html=current_html,
                    difficulty_level=lvl,
                )
                combined_prompts.extend(single_set)

            # Wrap them into a single TaskPromptForUrl object
            domain_prompts.append(TaskPromptForUrl(
                page_url=page_url,
                task_prompts=combined_prompts
            ))

        return domain_prompts

    def generate_task_prompts_for_url(
        self,
        specific_url: str,
        current_html: Optional[str] = None,
        task_difficulty_level: TaskDifficultyLevel = TaskDifficultyLevel.EASY,
    ) -> TaskPromptForUrl:
        """
        Generate tasks for a single URL at a given difficulty. The standard approach:
        returns a single TaskPromptForUrl object with multiple (num_prompts_per_url) prompts.

        :param specific_url: The URL for which to generate tasks
        :param current_html: The HTML source (optional)
        :param task_difficulty_level: The difficulty level
        """
        if not current_html:
            current_html = extract_html(specific_url)

        prompts = self._generate_prompts_for_url_and_level(
            specific_url=specific_url,
            current_html=current_html,
            difficulty_level=task_difficulty_level,
        )
        return TaskPromptForUrl(
            page_url=specific_url,
            task_prompts=prompts
        )

    def _generate_prompts_for_url_and_level(
        self,
        specific_url: str,
        current_html: str,
        difficulty_level: TaskDifficultyLevel,
    ) -> List[str]:
        """
        Actually calls the LLM to produce a set of tasks for a given URL and difficulty level.
        Returns a list of prompt strings.
        """
        if not current_html:
            current_html = ""

        # Summaries or metadata from SinglePageAnalysis
        page_analysis = self._get_page_analysis(specific_url)
        page_summary = page_analysis.web_summary or {}

        # We can create a domain summary: e.g. domain type, domain features
        domain_summary = f"Domain Type: {self.web_analysis.domain_type or 'Unknown'}, Features: {self.web_analysis.features}"

        # Construct the system/user messages for the LLM
        # We'll ask for strictly JSON array output to parse easily
        system_prompt = SYSTEM_MSG
        user_prompt = f"""
Here is the overall domain information:
{domain_summary}

Here is the page summary:
{json.dumps(page_summary, ensure_ascii=False)}

Here is the HTML content for this specific page (truncated if large):
{current_html[:2000]}  # only first 2000 characters as snippet to avoid super-long prompts

Now, you need to {TASK_INSTRUCTION[difficulty_level]}
Generate {self.num_prompts_per_url} tasks as an array of strings in JSON. 
No additional keys. Only output an array of tasks in JSON. 
These tasks should be anchored in this page's context, 
but you may incorporate cross-page or multi-step flows if relevant.
        """.strip()

        # We request the LLM to return a JSON array of strings: ["task1", "task2", ...]
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            chat_completion_kwargs={
                "temperature": 0.7,
                "top_k": 40, 
                "max_tokens": 512,
                # We specify a response format that demands an array of strings in JSON
                "response_format": {
                    "type": "json_array",
                    "items": {"type": "string"}
                },
            }
        )

        if not response:
            return []

        # Try to parse the response as JSON. The "response_format" param helps ensure correctness,
        # but we still do a try/except in case the LLM returns invalid output.
        try:
            parsed = json.loads(response)
            if not isinstance(parsed, list):
                return []
            # Filter out any non-string items
            return [item for item in parsed if isinstance(item, str)]
        except Exception:
            return []

    def _get_page_analysis(self, target_url: str) -> SinglePageAnalysis:
        """
        Finds and returns the SinglePageAnalysis object for a given URL.
        Raises ValueError if not found.
        """
        for page in self.web_analysis.analyzed_urls:
            if page.page_url == target_url:
                return page
        # If not found, create a dummy one
        return SinglePageAnalysis(page_url=target_url, html_source="", web_summary={})
