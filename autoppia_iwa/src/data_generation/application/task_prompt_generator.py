import json
import re
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
    Generates both 'global' (multi-page) and 'local' tasks 
    for a given WebProject, which must contain domain_analysis & pages.
    """

    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
        global_tasks_count: int = 2,
        local_tasks_count_per_url: int = 2,
    ) -> None:
        self.web_project = web_project
        self.llm_service = llm_service
        self.global_tasks_count = global_tasks_count
        self.local_tasks_count_per_url = local_tasks_count_per_url

    def generate(self) -> List[Task]:
        all_tasks: List[Task] = []

        use_cases = self._discover_domain_use_cases(self.web_project.web_analysis)
        global_prompts = self._generate_global_tasks(use_cases, self.web_project.web_analysis)
        local_prompts = self._generate_local_tasks_for_all_pages(self.web_project.web_analysis.page_analyses)

        combined_data = (
            [{"prompt": p, "is_global": True} for p in global_prompts]
            + [{"prompt": p, "is_global": False} for p in local_prompts]
        )

        classified_data = self._classify_and_filter(combined_data)

        for item in classified_data:
            ttype = "global" if item["is_global"] else "local"
            chosen_url = "N/A" if ttype == "global" else self.web_project.web_analysis.start_url
            new_task = Task(
                type=ttype,
                prompt=item["prompt"],
                url=chosen_url,
                specifications=BrowserSpecification(),
                tests=[],
                milestones=None,
                web_analysis=self.web_project.web_analysis,
                category=item["category"]
            )
            all_tasks.append(new_task)

        return all_tasks

    def _parse_json_response(self, response: str) -> Any:
        if not response:
            return None
        response = response.strip()
        md_pattern = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)
        match = md_pattern.match(response)
        if match:
            response = match.group(1)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    # ---------------------------------------------------------
    # Discover Domain Use Cases
    # ---------------------------------------------------------
    def _discover_domain_use_cases(self, domain_analysis: DomainAnalysis) -> List[str]:
        summary_text = self._build_domain_summary_text(domain_analysis)
        user_msg = f"""
We have the following domain analysis:

{summary_text}

Identify typical GLOBAL multi-step goals or workflows a user might want to accomplish on this website.
Return a JSON array of short textual descriptions (strings). 
These should be realistic actions: signups, custom setups, or multi-page flows.
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "You are an expert in web domain analysis."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )
        parsed = self._parse_json_response(response)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if isinstance(item, str)]
        return []

    def _build_domain_summary_text(self, domain_analysis: DomainAnalysis) -> str:
        lines = [
            f"Domain: {domain_analysis.domain}",
            f"Category: {domain_analysis.category}",
            f"Status: {domain_analysis.status}",
            f"Start URL: {domain_analysis.start_url}",
            f"Total Pages Analyzed: {len(domain_analysis.page_analyses)}",
        ]
        for i, page in enumerate(domain_analysis.page_analyses, start=1):
            lines.append(f"\n--- Page {i} ---")
            lines.append(f"URL: {page.page_url}")
            lines.append(f"One-Phrase Summary: {page.web_summary.one_phrase_summary}")
            lines.append(f"Keywords: {page.web_summary.key_words}")
        return "\n".join(lines)

    # ---------------------------------------------------------
    # Generate Global Tasks
    # ---------------------------------------------------------
    def _generate_global_tasks(self, use_cases: List[str], domain_analysis: DomainAnalysis) -> List[str]:
        if not use_cases or self.global_tasks_count <= 0:
            return []

        chosen_use_cases = use_cases[: self.global_tasks_count]
        domain_text = self._build_domain_summary_text(domain_analysis)

        user_msg = f"""
We have the following domain info:
{domain_text}

We want multi-step tasks that are goal-oriented, reference real site features, 
and reflect actual usage scenarios. We have these use cases:
{json.dumps(chosen_use_cases, indent=2)}

Generate {len(chosen_use_cases)} tasks in a JSON array (strings). 
Each should be more detailed, specifying 2-3 steps or sub-actions. 
Be realistic: e.g. "Sign up -> Configure X -> Submit feedback."
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "Generate multi-step tasks referencing site capabilities."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        global_prompts = []
        parsed = self._parse_json_response(response)
        if isinstance(parsed, list):
            for p in parsed:
                if isinstance(p, str):
                    global_prompts.append(p)
        return global_prompts

    # ---------------------------------------------------------
    # Generate Local Tasks
    # ---------------------------------------------------------
    def _generate_local_tasks_for_all_pages(self, pages: List[SinglePageAnalysis]) -> List[str]:
        local_prompts = []
        if self.local_tasks_count_per_url <= 0:
            return local_prompts

        for page_info in pages:
            local_prompts_for_page = self._generate_local_tasks_for_page(page_info)
            local_prompts.extend(local_prompts_for_page)
        return local_prompts

    def _generate_local_tasks_for_page(self, page_info: SinglePageAnalysis) -> List[str]:
        extracted_html = extract_html(page_info.page_url) or page_info.html_source
        cleaned_html = clean_html(extracted_html)
        summary_text = self._build_page_summary_text(page_info)

        user_msg = f"""
Below is the page analysis summary, plus truncated HTML content:
--- Page Summary ---
{summary_text}

--- HTML (truncated) ---
{cleaned_html[:1500]}

Generate {self.local_tasks_count_per_url} single-page tasks that are realistic or interactive. 
Include small details (e.g., "Click on X section, fill Y form, check for Z"). 
Return them as a JSON array of strings.
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "You are an expert at generating local tasks for a web page."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        result = []
        parsed = self._parse_json_response(response)
        if isinstance(parsed, list):
            result = [str(p) for p in parsed if isinstance(p, str)]
        return result

    def _build_page_summary_text(self, page_info: SinglePageAnalysis) -> str:
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

    # ---------------------------------------------------------
    # Classify and Filter
    # ---------------------------------------------------------
    def _classify_and_filter(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

        classified_map = [{"task": p, "category": "Other"} for p in prompts]
        parsed = self._parse_json_response(response)
        if isinstance(parsed, list):
            cleaned = []
            for item in parsed:
                if isinstance(item, dict) and "task" in item and "category" in item:
                    cleaned.append({
                        "task": item["task"],
                        "category": item["category"]
                    })
            if len(cleaned) == len(prompts):
                classified_map = cleaned

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
        return True
