import asyncio
import json
import re
import asyncio
from typing import List, Dict, Any

from dependency_injector.wiring import Provide

from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.infrastructure.llm_service import ILLMService
from autoppia_iwa.src.shared.utils import clean_html, extract_html
from autoppia_iwa.src.shared.prompt_importer import PromptImporter
from autoppia_iwa.src.web_analysis.domain.analysis_classes import (
    DomainAnalysis,
    SinglePageAnalysis,
)
from autoppia_iwa.src.data_generation.domain.classes import Task, BrowserSpecification
from autoppia_iwa.src.demo_webs.classes import WebProject


class TaskPromptGenerator:
    """
    Generates usage-based tasks (global + local) and applies three LLM-based filters:
      1) Feasibility & Context Filter
      2) Success Criteria Filter
      3) Concept Filter

    Returns a final list of valid tasks.
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

        # Example usage of a single "PromptImporter":
        # If you want to import different files per filter, you can create three instances
        # or swap the file path. 
        self.domain_prompt_importer = PromptImporter("domain_analysis_prompt.txt")
        self.global_prompt_importer = PromptImporter("global_tasks_prompt.txt")
        self.local_prompt_importer = PromptImporter("local_tasks_prompt.txt")

        self.feasibility_filter_importer = PromptImporter("feasibility_context_filter_prompt.txt")
        self.success_filter_importer = PromptImporter("success_criteria_filter_prompt.txt")
        self.concept_filter_importer = PromptImporter("concept_filter_prompt.txt")

    async def generate(self) -> List[Task]:
        # 1) Identify typical user flows
        use_cases = self._discover_domain_use_cases(self.web_project.web_analysis)

        # 2) Generate multi-page tasks
        global_data = self._generate_global_tasks(use_cases, self.web_project.web_analysis)

        # 3) Generate single-page tasks
        local_data = await self._generate_for_all_pages(self.web_project.web_analysis.page_analyses)

        # 4) Merge
        combined_data = (
            [{"is_global": True, **obj} for obj in global_data]
            + [{"is_global": False, **obj} for obj in local_data]
        )

        # 5) Filter chain
        feasible_data = self._llm_feasibility_context_filter(combined_data)
        success_ok_data = self._llm_success_criteria_filter(feasible_data)
        concept_ok_data = self._llm_concept_filter(success_ok_data)

        # 6) Build final Task objects
        final_tasks = self._build_task_objects(concept_ok_data)
        return final_tasks

    # ---------------------------------------------------------------------
    # Step 1: Discover Domain Use Cases
    # ---------------------------------------------------------------------
    def _discover_domain_use_cases(self, domain_analysis: DomainAnalysis) -> List[str]:
        summary_text = self._build_domain_summary_text(domain_analysis)

        # Example usage of an external prompt:
        domain_prompt = self.domain_prompt_importer.get_prompt()
        system_message = domain_prompt.format(domain_info=summary_text)

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ""},
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

        domain_text = self._build_domain_summary_text(domain_analysis)
        chosen_use_cases = use_cases[:self.global_tasks_count]

        # Example usage of an external prompt:
        global_prompt = self.global_prompt_importer.get_prompt()
        system_message = global_prompt.format(domain_info=domain_text, use_cases=json.dumps(chosen_use_cases))

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ""},
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
    async def _generate_for_all_pages(self, pages: List[SinglePageAnalysis]) -> List[Dict[str, str]]:
        tasks = [self._generate_for_page(p) for p in pages]
        results = await asyncio.gather(*tasks)
        local_data = []
        for res in results:
            local_data.extend(res)
        return local_data

    async def _generate_for_page(self, page_info: SinglePageAnalysis) -> List[Dict[str, str]]:
        extracted_html = await extract_html(page_info.page_url) or page_info.html_source
        cleaned_html = clean_html(extracted_html)
        page_summary = self._build_page_summary_text(page_info)

        local_prompt = self.local_prompt_importer.get_prompt()
        system_message = local_prompt.format(
            page_summary=page_summary,
            truncated_html=cleaned_html[:1500],
            num_tasks=self.local_tasks_count_per_url
        )

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ""},
            ],
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 800},
        )

        parsed_objs = self._parse_json_response(response)
        results: List[Dict[str, str]] = []
        if isinstance(parsed_objs, list):
            for obj in parsed_objs:
                if "prompt" in obj and "success_criteria" in obj:
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
    # Step 4 & 5: LLM Filters
    # ---------------------------------------------------------------------
    def _llm_feasibility_context_filter(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pass domain info and raw tasks to LLM; keep only feasible tasks in context.
        """
        if not tasks_data:
            return tasks_data

        filter_prompt = self.feasibility_filter_importer.get_prompt()
        domain_info = f"Category: {self.web_project.web_analysis.category}, Features: {self.web_project.web_analysis.features}"

        # Prepare data for LLM
        tasks_array = [{"prompt": t["prompt"], "success_criteria": t["success_criteria"]} for t in tasks_data]
        system_message = filter_prompt.format(domain_info=domain_info, tasks=json.dumps(tasks_array, indent=2))

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ""},
            ],
            chat_completion_kwargs={"temperature": 0.0, "max_tokens": 1200},
        )

        parsed = self._parse_json_response(response)
        if not isinstance(parsed, list):
            return tasks_data

        keep_decisions = {}
        for item in parsed:
            pr = item.get("prompt", "").strip()
            decision = item.get("decision", "keep")
            keep_decisions[pr] = (decision.lower() == "keep")

        final_list = []
        for td in tasks_data:
            if keep_decisions.get(td["prompt"].strip()) is True:
                final_list.append(td)
        return final_list

    def _llm_success_criteria_filter(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pass tasks to LLM to check if the success criteria is adequate or too vague.
        """
        if not tasks_data:
            return tasks_data

        filter_prompt = self.success_filter_importer.get_prompt()
        tasks_array = [{"prompt": t["prompt"], "success_criteria": t["success_criteria"]} for t in tasks_data]
        system_message = filter_prompt.format(tasks=json.dumps(tasks_array, indent=2))

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ""},
            ],
            chat_completion_kwargs={"temperature": 0.0, "max_tokens": 1200},
        )

        parsed = self._parse_json_response(response)
        if not isinstance(parsed, list):
            return tasks_data

        keep_decisions = {}
        for item in parsed:
            pr = item.get("prompt", "").strip()
            decision = item.get("decision", "keep")
            keep_decisions[pr] = (decision.lower() == "keep")

        final_list = []
        for td in tasks_data:
            if keep_decisions.get(td["prompt"].strip()) is True:
                final_list.append(td)
        return final_list

    def _llm_concept_filter(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pass tasks to LLM to remove tasks that are not usage-based or that mention dev/code changes, etc.
        """
        if not tasks_data:
            return tasks_data

        filter_prompt = self.concept_filter_importer.get_prompt()
        tasks_array = [{"prompt": t["prompt"], "success_criteria": t["success_criteria"]} for t in tasks_data]
        system_message = filter_prompt.format(tasks=json.dumps(tasks_array, indent=2))

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ""},
            ],
            chat_completion_kwargs={"temperature": 0.0, "max_tokens": 1200},
        )

        parsed = self._parse_json_response(response)
        if not isinstance(parsed, list):
            return tasks_data

        keep_decisions = {}
        for item in parsed:
            pr = item.get("prompt", "").strip()
            decision = item.get("decision", "keep")
            keep_decisions[pr] = (decision.lower() == "keep")

        final_list = []
        for td in tasks_data:
            if keep_decisions.get(td["prompt"].strip()) is True:
                final_list.append(td)
        return final_list

    # ---------------------------------------------------------------------
    # Step 6: Build Final Task Objects
    # ---------------------------------------------------------------------
    def _build_task_objects(self, filtered_data: List[Dict[str, Any]]) -> List[Task]:
        all_tasks: List[Task] = []
        for item in filtered_data:
            ttype = "global" if item.get("is_global") else "local"
            chosen_url = "N/A" if ttype == "global" else self.web_project.web_analysis.start_url

            new_task = Task(
                type=ttype,
                prompt=item["prompt"],
                success_criteria=self._ensure_string(item.get("success_criteria", "")),
                url=chosen_url,
                specifications=BrowserSpecification(),
                tests=[],
                milestones=None,
                web_analysis=self.web_project.web_analysis,
                category="N/A"  # No classification
            )
            all_tasks.append(new_task)
        return all_tasks

    def _ensure_string(self, value: Any) -> str:
        if isinstance(value, list):
            return " ".join(str(x) for x in value)
        if isinstance(value, str):
            return value
        return str(value) if value is not None else ""

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
