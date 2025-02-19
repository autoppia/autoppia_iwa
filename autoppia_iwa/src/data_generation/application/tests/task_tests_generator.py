import json
from typing import List, Optional

from dependency_injector.wiring import Provide
from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.data_generation.domain.tests_classes import (
    BaseTaskTest,
    CheckEventEmittedTest,
    CheckPageViewEventTest,
    FindInHtmlTest,
    OpinionBaseOnHTML,
)
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.shared.utils import extract_html
from autoppia_iwa.src.web_analysis.application.web_llm_utils import ILLMService
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis, SinglePageAnalysis
from autoppia_iwa.src.backend_demo_web.classes import WebProject

# Import new components
from autoppia_iwa.src.data_generation.application.tests.test_generation_components import (
    CandidateTestGenerator,
    TestParserValidator,
    TestClassifierRanker,
    TestSelectionModule,
)

BASE_SYSTEM_MSG = """
1. IMPORTANT RULES:
    - You are a professional evaluator responsible for generating structured test cases for tasks on a website. 
    - Based on a task description and page analysis, you must classify and generate tests into categories.
    - For CheckEventTest, only mention the valid urls in the web_analysis.
    - If there is any navigation performed then there must be a CheckPageViewTest.
    - In most cases, all three test types—CheckEventTest, CheckHTMLTest, and CheckPageViewTest—are necessary.
    - However, certain scenarios may require only one or two of them instead of all three.

    1.1. OUTPUT FORMAT:
        - Always return the tests as a valid JSON array, without additional text or delimiters. The format must strictly follow this structure:
        [
            {"type": "CheckEventTest","event_name": "<event>"},
            {"type": "CheckHTMLTest","html_keywords": ["<keyword1>", "<keyword2>", ...]},
            {"type": "CheckPageViewTest","url": "<url>"}
        ]
        - For instance, if the task is to change the website's language by clicking a flag button, it is unlikely to trigger any backend events. In such cases, return only a list of CheckHTMLTest without any CheckEventTest. For example, if the task is to view a specific page, a CheckPageViewTest might be sufficient.
"""


class TaskTestGenerator:
    """
    Generates and classifies test cases using a modular pipeline.
    """

    def __init__(
        self,
        web_project: WebProject,
        web_analysis: DomainAnalysis,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
    ) -> None:
        self.web_project = web_project
        self.web_analysis = web_analysis
        self.llm_service = llm_service

    def generate_task_tests(self, task_description: str, page_url: str, page_html: Optional[str] = None) -> List[BaseTaskTest]:
        # 1) Retrieve allowed events from WebProject
        allowed_events = self.web_project.events

        # 2) Prepare the system message and validation schema
        system_message = self._build_system_message(allowed_events)
        tests_schema = self._load_and_modify_schema(allowed_events)

        # 3) Get page analysis and effective HTML
        page_analysis = self._get_page_analysis(page_url)
        effective_html = page_html or extract_html(page_url) or page_analysis.html_source

        print(f"Effective HTML for page {page_url} (first 500 chars):\n{effective_html[:500]}...\n")

        relevant_fields = [
            field 
            for element_analysis in (page_analysis.elements_analysis_result or []) 
            for field in (element_analysis.get("analysis", {}) or {}).get("relevant_fields", []) or []
        ]

        # 4) Use the new pipeline modules
        candidate_generator = CandidateTestGenerator(self.llm_service, system_message, allowed_events)
        raw_candidates = candidate_generator.generate_candidates(task_description, effective_html, page_analysis.web_summary, relevant_fields)

        print("----- Raw Candidate Tests from LLM -----")
        print(json.dumps(raw_candidates, indent=2))

        parser_validator = TestParserValidator(tests_schema)
        valid_tests = parser_validator.validate_tests(raw_candidates)

        print("----- Validated Candidate Tests -----")
        print(json.dumps(valid_tests, indent=2))

        classifier_ranker = TestClassifierRanker(allowed_events)
        ranked_tests = classifier_ranker.classify_and_rank(valid_tests)

        print("----- Ranked Candidate Tests -----")
        print(json.dumps(ranked_tests, indent=2))

        selector = TestSelectionModule()
        selected_tests = selector.select_tests(ranked_tests)

        print("----- Final Selected Tests -----")
        print(json.dumps(selected_tests, indent=2))

        # 5) Map the selected tests into test objects
        final_tests = []
        for test in selected_tests:
            try:
                if test["type"] == "CheckEventTest":
                    final_tests.append(CheckEventEmittedTest(event_name=test["event_name"]))
                elif test["type"] == "CheckHTMLTest":
                    final_tests.append(FindInHtmlTest(keywords=test["html_keywords"]))
                elif test["type"] == "CheckPageViewTest":
                    final_tests.append(CheckPageViewEventTest(page_view_url=test["url"]))
            except (KeyError, ValueError) as e:
                print(f"Test mapping error: {e}")
                continue

        # 6) For real websites, if frontend tests are generated add an additional OpinionBaseOnHTML check.
        if self.web_project.is_real_web:
            real_tests = []
            for test in final_tests:
                if test.test_type == "frontend":
                    real_tests.append(test)
                    real_tests.append(OpinionBaseOnHTML())
            return real_tests
        else:
            return final_tests

    @staticmethod
    def _build_system_message(allowed_events: List[str]) -> str:
        event_list = "\n".join(f'        - "{event}"' for event in allowed_events)
        return BASE_SYSTEM_MSG.replace("{/event_list/}", event_list)

    def _load_and_modify_schema(self, allowed_events: List[str]) -> dict:
        schema = self._load_base_schema()
        self._update_schema_events(schema, allowed_events)
        return schema

    @staticmethod
    def _load_base_schema() -> dict:
        schema_path = PROJECT_BASE_DIR / "config/schemas/task_test_schema.json"
        with schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _update_schema_events(schema: dict, allowed_events: List[str]) -> None:
        for test_type in schema["properties"]["tests"]["items"]["oneOf"]:
            if test_type.get("properties", {}).get("type", {}).get("const") == "CheckEventTest":
                test_type["properties"]["event_name"]["enum"] = allowed_events
                break

    def _get_page_analysis(self, target_url: str) -> SinglePageAnalysis:
        for page in self.web_analysis.page_analyses:
            if page.page_url == target_url:
                return page
        raise ValueError(f"Page analysis not found for URL: {target_url}")
