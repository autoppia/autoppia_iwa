# file: autoppia_iwa/src/data_generation/application/task_prompt_generator.py

import json
from typing import List, Dict, Any

from dependency_injector.wiring import Provide

from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.infrastructure.llm_service import ILLMService
from autoppia_iwa.src.shared.utils import clean_html, extract_html
from autoppia_iwa.src.web_analysis.domain.analysis_classes import (
    DomainAnalysis,
    SinglePageAnalysis,
)
from autoppia_iwa.src.data_generation.domain.classes import Task, BrowserSpecification
from autoppia_iwa.src.backend_demo_web.classes import WebProject


class TaskPromptGenerator:
    """
    Generates both 'global' (multi-page) and 'local' (single-page) tasks 
    for a given WebProject, which must contain:
      - domain_analysis: DomainAnalysis
      - pages: List[SinglePageAnalysis]

    The pipeline is:
      1) Discover domain-wide use cases (global).
      2) Generate a certain number of global tasks in total.
      3) Generate local tasks for each page, with a given number of tasks per page.
      4) Classify and filter all tasks.
      5) Return a list of Task objects.
    """

    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
        global_tasks_count: int = 2,
        local_tasks_count_per_url: int = 2,
    ) -> None:
        """
        :param web_project: The WebProject containing DomainAnalysis and SinglePageAnalysis data.
        :param llm_service: Injected LLM service for generating and classifying tasks.
        :param global_tasks_count: How many global, multi-page tasks to generate in total.
        :param local_tasks_count_per_url: How many local, single-page tasks to generate per URL.
        """
        self.web_project = web_project
        self.llm_service = llm_service
        self.global_tasks_count = global_tasks_count
        self.local_tasks_count_per_url = local_tasks_count_per_url

    def generate(self) -> List[Task]:
        """
        1) Discovers domain-wide use cases (global).
        2) Generates global tasks (using self.global_tasks_count).
        3) Generates local tasks for each page (using self.local_tasks_count_per_url).
        4) Classifies and filters them.
        5) Returns a list of Task objects.
        """
        all_tasks: List[Task] = []

        # 1) Discover domain-wide use cases
        use_cases = self._discover_domain_use_cases(self.web_project.domain_analysis)

        # 2) Generate a total of self.global_tasks_count tasks across all use cases
        #    (distribute them or simply attempt to generate them for each use case, as you prefer).
        #    Below, we do a simplistic approach:
        global_prompts = self._generate_global_tasks(use_cases, self.web_project.domain_analysis)

        # 3) Generate local tasks for each page, with local_tasks_count_per_url per page
        local_prompts = self._generate_local_tasks_for_all_pages(self.web_project.pages)

        # Combine them (mark each as global or local)
        combined_data = (
            [{"prompt": p, "is_global": True} for p in global_prompts]
            + [{"prompt": p, "is_global": False} for p in local_prompts]
        )

        # 4) Classify/filter
        classified_data = self._classify_and_filter(combined_data)

        # 5) Build final Task objects
        for item in classified_data:
            if item["is_global"]:
                chosen_url = "N/A"
            else:
                # If local, you might store the precise URL or do something more advanced. 
                # Here, we take the first page as an example, but you could store each page's tasks individually.
                chosen_url = self.web_project.pages[0].page_url if self.web_project.pages else "N/A"

            new_task = Task(
                prompt=item["prompt"],
                url=chosen_url,
                specifications=BrowserSpecification(),
                tests=[],
                milestones=None,
                web_analysis=self.web_project.domain_analysis,
                category=item["category"]
            )
            all_tasks.append(new_task)

        return all_tasks

    # ---------------------------------------------------------------------
    # Step 1: Discover Domain Use Cases
    # ---------------------------------------------------------------------
    def _discover_domain_use_cases(self, domain_analysis: DomainAnalysis) -> List[str]:
        """
        Asks the LLM to list typical multi-step workflows or processes 
        for the domain. We'll later use these to generate global tasks.

        :param domain_analysis: The domain analysis object, containing pages & site data.
        :return: A list of global use-case strings.
        """
        summary_text = self._build_domain_summary_text(domain_analysis)
        user_msg = f"""
We have the following domain analysis:

{summary_text}

Please identify typical GLOBAL use cases (complex or multi-page flows) 
a user might want to perform in this domain. Return a JSON array of strings only.
Example: ["Add items to cart and complete checkout", "Register an account and edit profile", ...].
        """

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "You are an expert in web domain analysis."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )
        if not response:
            return []

        try:
            parsed = json.loads(response)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if isinstance(item, str)]
        except json.JSONDecodeError:
            pass

        return []

    def _build_domain_summary_text(self, domain_analysis: DomainAnalysis) -> str:
        """
        Builds a textual summary of the DomainAnalysis for LLM context.

        :param domain_analysis: The DomainAnalysis, including domain, category, page_analyses, etc.
        :return: A string summary describing the domain and pages.
        """
        lines = [
            f"Domain: {domain_analysis.domain}",
            f"Category: {domain_analysis.category}",
            f"Status: {domain_analysis.status}",
            f"Start URL: {domain_analysis.start_url}",
            f"Total Pages Analyzed: {len(domain_analysis.page_analyses)}",
        ]
        # Optionally add details from each SinglePageAnalysis
        for i, page in enumerate(domain_analysis.page_analyses, start=1):
            lines.append(f"\n--- Page {i} ---")
            lines.append(f"URL: {page.page_url}")
            lines.append(f"One-Phrase Summary: {page.web_summary.one_phrase_summary}")
            lines.append(f"Keywords: {page.web_summary.key_words}")
        return "\n".join(lines)

    # ---------------------------------------------------------------------
    # Step 2: Generate Global Tasks
    # ---------------------------------------------------------------------
    def _generate_global_tasks(self, use_cases: List[str], domain_analysis: DomainAnalysis) -> List[str]:
        """
        Generates a total of self.global_tasks_count global tasks based on the discovered use cases.

        In this simple approach, we:
          - If there are no use cases, return an empty list.
          - Otherwise, pick whichever approach you prefer to produce 
            'global_tasks_count' tasks in total. (Here, we just ask for them 
            from the first use case, or attempt to distribute them.)

        :param use_cases: A list of multi-step scenario strings from _discover_domain_use_cases().
        :param domain_analysis: The domain analysis object for context.
        :return: A list of global task prompts (strings).
        """
        if not use_cases or self.global_tasks_count <= 0:
            return []

        # For demonstration, let's just pick the first use case (if it exists) 
        # and generate 'global_tasks_count' tasks for it:
        chosen_use_case = use_cases[0]
        domain_text = self._build_domain_summary_text(domain_analysis)

        user_msg = f"""
We have the following domain info:
{domain_text}

Use case: "{chosen_use_case}"

Generate exactly {self.global_tasks_count} global tasks (JSON array of strings only) 
that align with this use case. These tasks may span multiple pages or steps.
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "You are an expert in generating multi-page web tasks."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        global_prompts = []
        if response:
            try:
                parsed = json.loads(response)
                if isinstance(parsed, list):
                    for p in parsed:
                        if isinstance(p, str):
                            global_prompts.append(p)
            except json.JSONDecodeError:
                pass

        return global_prompts

    # ---------------------------------------------------------------------
    # Step 3: Generate Local Tasks for Each Page
    # ---------------------------------------------------------------------
    def _generate_local_tasks_for_all_pages(self, pages: List[SinglePageAnalysis]) -> List[str]:
        """
        For each page, we generate 'local_tasks_count_per_url' tasks that 
        only involve actions or checks on that single page.

        :param pages: A list of SinglePageAnalysis (each with URL, HTML, etc.).
        :return: A combined list of local prompts across all pages.
        """
        local_prompts: List[str] = []

        if self.local_tasks_count_per_url <= 0:
            return local_prompts

        for page_info in pages:
            local_prompts_for_page = self._generate_local_tasks_for_page(page_info)
            local_prompts.extend(local_prompts_for_page)

        return local_prompts

    def _generate_local_tasks_for_page(self, page_info: SinglePageAnalysis) -> List[str]:
        """
        Generates local tasks for a single page using its HTML and summary data.

        :param page_info: SinglePageAnalysis object with URL, web_summary, etc.
        :return: A list of local task prompts.
        """
        # Ensure we have HTML. Compare stored vs. newly extracted, if needed.
        extracted_html = extract_html(page_info.page_url) or ""
        if page_info.html_source and extracted_html:
            if page_info.html_source.strip() != extracted_html.strip():
                print(f"[WARNING] {page_info.page_url} => HTML mismatch between stored vs. extracted.")

        cleaned_html = clean_html(page_info.html_source or extracted_html)
        summary_text = self._build_page_summary_text(page_info)

        user_msg = f"""
Here is the local page analysis data:
{summary_text}

Here is the (cleaned) HTML content:
{cleaned_html}

Generate {self.local_tasks_count_per_url} local tasks for this single page, 
returned in a JSON array of strings. These tasks must be relevant only to this page (no multi-page flow).
"""

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "You are an expert in generating single-page tasks."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        result = []
        if response:
            try:
                parsed = json.loads(response)
                if isinstance(parsed, list):
                    result = [str(p) for p in parsed if isinstance(p, str)]
            except json.JSONDecodeError:
                pass

        return result

    def _build_page_summary_text(self, page_info: SinglePageAnalysis) -> str:
        """
        Constructs an overview text from the SinglePageAnalysis data.

        :param page_info: SinglePageAnalysis with web_summary, URL, etc.
        :return: A string summarizing this page for LLM context.
        """
        ws = page_info.web_summary
        lines = [
            f"Page URL: {page_info.page_url}",
            f"One-Phrase Summary: {ws.one_phrase_summary}",
            f"Detailed Summary: {ws.summary}",
            f"Categories: {ws.categories}",
            f"Functionality: {ws.functionality}",
            f"Key Words: {ws.key_words}",
            f"Curiosities: {ws.curiosities}",
            f"User Experience: {ws.user_experience}"
        ]
        return "\n".join(lines)

    # ---------------------------------------------------------------------
    # Step 4: Classify and Filter
    # ---------------------------------------------------------------------
    def _classify_and_filter(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of dicts like: 
            [{ "prompt": str, "is_global": bool }, ...]
        Calls the LLM to categorize each prompt. Then filters out invalid tasks if desired.

        :return: A list of dicts, each with "prompt", "is_global", "category".
        """
        if not tasks_data:
            return []

        prompts = [x["prompt"] for x in tasks_data]
        system_msg = "You are an expert in classifying user tasks by their action type."
        user_msg = (
            "Classify each task into one of these categories:\n"
            " - Reading/Research\n"
            " - Navigation/Exploration\n"
            " - E-commerce/Purchasing\n"
            " - Data Entry\n"
            " - Multi-step Workflow\n"
            " - Other\n\n"
            "Return a JSON array of objects: {\"task\": \"...\", \"category\": \"...\"}.\n\n"
            "Tasks:\n"
        )
        for t in prompts:
            user_msg += f"- {t}\n"

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={
                "temperature": 0.0,
                "max_tokens": 800,
            }
        )

        # Default classification => "Other"
        classified_map = [{"task": p, "category": "Other"} for p in prompts]
        if response:
            try:
                parsed = json.loads(response)
                if isinstance(parsed, list):
                    cleaned = []
                    for item in parsed:
                        if (
                            isinstance(item, dict)
                            and "task" in item
                            and "category" in item
                        ):
                            cleaned.append({
                                "task": item["task"],
                                "category": item["category"]
                            })
                    if len(cleaned) == len(prompts):
                        classified_map = cleaned
            except json.JSONDecodeError:
                pass

        final_list = []
        for original_data, cat_item in zip(tasks_data, classified_map):
            if self._filter_task(cat_item["task"]):
                final_list.append({
                    "prompt": cat_item["task"],
                    "is_global": original_data["is_global"],
                    "category": cat_item["category"],
                })

        return final_list

    def _filter_task(self, task_text: str) -> bool:
        """
        Placeholder for filtering tasks if they are off-topic, duplicates, or invalid.
        For now, returns True for all.
        """
        return True
