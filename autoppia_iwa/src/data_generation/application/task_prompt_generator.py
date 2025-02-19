import json
import re
import asyncio
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
    Generates usage-based tasks from an end-user perspective, then uses LLM-based filtering
    to remove tasks that mention development/code changes or have insufficient success criteria.
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

    async def generate(self) -> List[Task]:
        all_tasks: List[Task] = []

        # 1) Identify typical user flows
        use_cases = self._discover_domain_use_cases(self.web_project.web_analysis)

        # 2) Generate multi-page tasks
        global_data = self._generate_global_tasks(use_cases, self.web_project.web_analysis)

        # 3) Generate single-page tasks (await async functions)
        local_data = await self._generate_local_tasks_for_all_pages(self.web_project.web_analysis.page_analyses)

        # Combine
        combined_data = (
            [{"is_global": True, **obj} for obj in global_data]
            + [{"is_global": False, **obj} for obj in local_data]
        )

        # 4) Classify tasks
        classified_data = self._classify_and_filter(combined_data)

        # 5) LLM-based filtering (remove dev tasks or tasks with insufficient success_criteria)
        filtered_data = self._llm_filter_tasks(classified_data)

        # 6) Build final Task objects
        for item in filtered_data:
            ttype = "global" if item["is_global"] else "local"
            chosen_url = "N/A" if ttype == "global" else self.web_project.web_analysis.start_url

            new_task = Task(
                type=ttype,
                prompt=item["prompt"],
                success_criteria=item.get("success_criteria", None),
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

    # ---------------------------------------------------------------------
    # Step 1: Discover Domain Use Cases
    # ---------------------------------------------------------------------
    def _discover_domain_use_cases(self, domain_analysis: DomainAnalysis) -> List[str]:
        summary_text = self._build_domain_summary_text(domain_analysis)
        user_msg = f"""
We have the following domain analysis:

{summary_text}

Identify typical GLOBAL user flows from an end-user perspective (no dev changes). 
Return a JSON array of short textual descriptions (strings).
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "You are an expert in usage-based web tasks."},
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

    # ---------------------------------------------------------------------
    # Step 2: Generate Global (Multi-page) Tasks
    # ---------------------------------------------------------------------
    def _generate_global_tasks(self, use_cases: List[str], domain_analysis: DomainAnalysis) -> List[Dict[str, str]]:
        if not use_cases or self.global_tasks_count <= 0:
            return []

        chosen_use_cases = use_cases[: self.global_tasks_count]
        domain_text = self._build_domain_summary_text(domain_analysis)

        user_msg = f"""
Domain info:
{domain_text}

We want multi-step tasks from an end-user perspective, focusing on exploring or using existing site features.

For each use case below, produce a JSON object with:
  "prompt": "<multi-step instructions for the user>",
  "success_criteria": "<how to know the steps were successful>"

Use cases:
{json.dumps(chosen_use_cases, indent=2)}
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "Generate usage tasks with success criteria."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        parsed_objs = self._parse_json_response(response)
        results: List[Dict[str, str]] = []
        if isinstance(parsed_objs, list):
            for obj in parsed_objs:
                if isinstance(obj, dict) and "prompt" in obj and "success_criteria" in obj:
                    results.append({
                        "prompt": obj["prompt"],
                        "success_criteria": obj["success_criteria"]
                    })
        return results

    # ---------------------------------------------------------------------
    # Step 3: Generate Local (Single-page) Tasks
    # ---------------------------------------------------------------------
    async def _generate_local_tasks_for_all_pages(self, pages: List[SinglePageAnalysis]) -> List[Dict[str, str]]:
        tasks = [self._generate_local_tasks_for_page(page_info) for page_info in pages]
        results = await asyncio.gather(*tasks)
        local_data = []
        for res in results:
            local_data.extend(res)
        return local_data

    async def _generate_local_tasks_for_page(self, page_info: SinglePageAnalysis) -> List[Dict[str, str]]:
        extracted_html = await extract_html(page_info.page_url) or page_info.html_source
        cleaned_html = clean_html(extracted_html)
        summary_text = self._build_page_summary_text(page_info)

        user_msg = f"""
Page analysis:
--- Page Summary ---
{summary_text}

--- Truncated HTML ---
{cleaned_html[:1500]}

Generate {self.local_tasks_count_per_url} usage-based tasks (no dev or code changes).
Return a JSON array of objects:
  "prompt": ...
  "success_criteria": ...
"""
        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": "Generate usage-based single-page tasks with success criteria."},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        parsed_objs = self._parse_json_response(response)
        results: List[Dict[str, str]] = []
        if isinstance(parsed_objs, list):
            for obj in parsed_objs:
                if (
                    isinstance(obj, dict)
                    and "prompt" in obj
                    and "success_criteria" in obj
                ):
                    results.append({
                        "prompt": obj["prompt"],
                        "success_criteria": obj["success_criteria"]
                    })
        return results

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

    # ---------------------------------------------------------------------
    # Step 4: Classify Tasks
    # ---------------------------------------------------------------------
    def _classify_and_filter(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not tasks_data:
            return []

        prompts = [x["prompt"] for x in tasks_data]
        system_msg = "You are an expert in classifying usage-based user tasks."
        user_msg = (
            "Classify each usage-based task into one of these categories:\n"
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
                if "task" in item and "category" in item:
                    cleaned.append({"task": item["task"], "category": item["category"]})
            if len(cleaned) == len(prompts):
                classified_map = cleaned

        final_list = []
        for original_data, cat_item in zip(tasks_data, classified_map):
            final_list.append({
                "prompt": cat_item["task"],
                "success_criteria": original_data.get("success_criteria", ""),
                "is_global": original_data["is_global"],
                "category": cat_item["category"],
            })
        return final_list

    # ---------------------------------------------------------------------
    # Step 5: LLM-based Filter to Exclude Dev-based or Low-Quality Tasks
    # ---------------------------------------------------------------------
    def _llm_filter_tasks(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not tasks_data:
            return []

        tasks_array = []
        for td in tasks_data:
            tasks_array.append({
                "prompt": td["prompt"],
                "success_criteria": td["success_criteria"],
            })

        system_msg = "You are a filter for usage-based tasks. We do NOT want tasks that mention development or code changes. We also require decent success criteria."
        user_msg = (
            "Below is a JSON array of tasks. For each item, you must return an object:\n"
            "{\n"
            "  \"prompt\": <same prompt text>,\n"
            "  \"decision\": \"keep\" or \"remove\",\n"
            "  \"reason\": \"explain briefly why\"\n"
            "}\n\n"
            "Rules:\n"
            "1) If the prompt implies developing or coding features, remove.\n"
            "2) If success criteria is missing or too vague (<10 chars), remove.\n"
            "3) Otherwise, keep.\n\n"
            "Tasks:\n"
            f"{json.dumps(tasks_array, indent=2)}\n"
        )

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            chat_completion_kwargs={
                "temperature": 0.0,
                "max_tokens": 1200,
            }
        )

        filtered_results = self._parse_json_response(response)
        if not isinstance(filtered_results, list):
            return tasks_data

        keep_decisions = {}
        for item in filtered_results:
            prompt = item.get("prompt", "").strip()
            decision = item.get("decision", "keep")
            keep_decisions[prompt] = (decision == "keep")

        final_list = []
        for td in tasks_data:
            p = td["prompt"].strip()
            if keep_decisions.get(p) is True:
                final_list.append(td)
        return final_list
