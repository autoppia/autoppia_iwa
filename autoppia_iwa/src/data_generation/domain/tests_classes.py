# file: data_generation/domain/tests_classes.py
import json
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Type

from bs4 import BeautifulSoup
from dependency_injector.wiring import Provide
from pydantic import BaseModel, Field, ValidationError, field_validator

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.domain.interfaces import ILLM

from ...shared.web_utils import generate_html_differences
from .tests_prompts import OPINION_BASED_HTML_TEST_SYS_MSG, SCREENSHOT_TEST_SYSTEM_PROMPT
from .tests_schemas import HTMLBasedTestResponse, ScreenshotTestResponse


class ITest(ABC):
    @abstractmethod
    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Abstract method to implement the specific logic for the test.
        """


class BaseTaskTest(BaseModel, ITest):
    """
    Base class for all task tests.
    """

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    async def execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Executes the test by delegating to the _execute_test method.
        """
        return await self._execute_test(web_project, current_iteration, prompt, snapshot, browser_snapshots, total_iterations)

    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Method not implemented")

    def serialize(self) -> dict:
        """
        Serialize a BaseTaskTest (or subclass) to a dict, ensuring 'type' is included.
        """
        serialized = self.model_dump()
        if "type" not in serialized:
            serialized["type"] = self.__class__.__name__
        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> "BaseTaskTest":
        """
        A fallback manual approach if needed,
        in case you do not rely on the 'Union[...]' approach in your Task model.
        """
        test_type = data.get("type", "")
        test_classes: Dict[str, Type[BaseTaskTest]] = {
            "CheckUrlTest": CheckUrlTest,
            "FindInHtmlTest": FindInHtmlTest,
            "CheckEventTest": CheckEventTest,
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
        }
        target_class = test_classes.get(test_type, cls)
        try:
            return target_class.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Failed to deserialize data: {e}") from e


class CheckUrlTest(BaseTaskTest):
    """
    Test that checks if the browser navigated to a specific URL with different matching options.
    """

    type: Literal["CheckUrlTest"] = "CheckUrlTest"
    url: str
    match_type: Literal["exact", "contains", "regex"] = "contains"
    description: str = Field(default="Check if browser navigated to URL")

    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Execute the test on the given snapshots with the specified matching strategy.
        """
        current_url = snapshot.current_url

        if self.match_type == "exact":
            return current_url == self.url
        elif self.match_type == "contains":
            return self.url in current_url
        elif self.match_type == "regex":
            return bool(re.search(self.url, current_url))

        return False


class FindInHtmlTest(BaseTaskTest):
    """
    Test class to find content in the current HTML with different matching strategies.
    """

    type: Literal["FindInHtmlTest"] = "FindInHtmlTest"
    content: str = Field(..., description="Content to look for in the HTML")
    match_type: Literal["exact", "contains", "regex"] = "contains"
    description: str = Field(
        default="Find content in HTML using specified matching strategy",
        description="Description of the test",
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, content: str) -> str:
        if not content.strip():
            raise ValueError("Content cannot be empty or consist of only whitespace")
        return content.strip()

    def extract_text_from_html(self, html: str) -> str:
        """Extract readable text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        # Get text
        text = soup.get_text(separator=" ", strip=True)
        return re.sub(r'\s+', ' ', text).strip()

    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Checks if the specified content is present in the current snapshot's HTML
        using the specified matching strategy.
        """
        html = snapshot.current_html

        if self.match_type == "exact":
            return self.content == html
        elif self.match_type == "contains":
            # Extract text for contains match to avoid HTML tag issues
            extracted_text = self.extract_text_from_html(html)
            return self.content in extracted_text
        elif self.match_type == "regex":
            return bool(re.search(self.content, html))

        return False


class CheckEventTest(BaseTaskTest):
    """
    Test that checks if specific events were triggered based on event type and criteria.
    """

    type: Literal["CheckEventTest"] = "CheckEventTest"
    event_name: str
    event_criteria: Dict = Field(default_factory=dict)
    description: str = Field(default="Check if specific event was triggered")

    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Execute the test on the given snapshots by checking for specific events.
        """
        if (current_iteration + 1) < total_iterations:
            return False

        parsed_events: List[Event] = Event.parse_all(snapshot.backend_events)
        valid_events: List[Event] = []
        for event in parsed_events:
            if event.event_name == self.event_name:
                valid_events.append(event)

        for event in valid_events:
            validation_model = event.ValidationCriteria

            try:
                parsed_criteria = validation_model(**self.event_criteria)
            except ValidationError as e:
                print(f"Invalid validation criteria: {e}")
                return False

            if event.validate_criteria(parsed_criteria):
                return True

        return False


class JudgeBaseOnHTML(BaseTaskTest):
    type: Literal["JudgeBaseOnHTML"] = "JudgeBaseOnHTML"
    success_criteria: str
    description: str = Field(default="Judge based on HTML changes")

    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        if current_iteration != total_iterations - 1:
            return False

        all_htmls = self._collect_all_htmls(browser_snapshots)
        if not all_htmls:
            return False

        differences = generate_html_differences(all_htmls)
        if not differences:
            return False

        return await self._analyze_htmls(prompt, differences)

    @staticmethod
    def _collect_all_htmls(browser_snapshots: List[BrowserSnapshot]) -> List[str]:
        """
        Collects all HTMLs in order from the browser snapshots.
        """
        if not browser_snapshots:
            return []

        all_htmls = [browser_snapshots[0].prev_html, browser_snapshots[0].current_html]
        for snap in browser_snapshots[1:]:
            all_htmls.append(snap.current_html)
        return all_htmls

    async def _analyze_htmls(self, task_prompt: str, differences: List[str], llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        """
        Analyzes HTML changes using an LLM to determine success.
        """
        json_schema = HTMLBasedTestResponse.model_json_schema()
        formatted_sys_msg = OPINION_BASED_HTML_TEST_SYS_MSG.format(json_schema=json_schema)
        user_message = f"Task: {task_prompt}\n\nHTML differences:\n{' '.join(differences)}"
        payload = [{"role": "system", "content": formatted_sys_msg}, {"role": "user", "content": user_message}]

        start_time = time.perf_counter()
        result = await llm_service.async_predict(payload, json_format=True, return_raw=True)
        end_time = time.perf_counter()
        duration = round(end_time - start_time, 3)
        save_usage_record(task_prompt, result, duration, self.type)
        try:
            result_str = result.choices[0].message.content
        except Exception:
            result_str = result
        match = re.search(r'"evaluation_result"\s*:\s*(true|false)', result_str, re.IGNORECASE)

        return match.group(1).lower() == "true" if match else False


class JudgeBaseOnScreenshot(BaseTaskTest):
    type: Literal["JudgeBaseOnScreenshot"] = "JudgeBaseOnScreenshot"
    success_criteria: str
    description: str = Field(default="Judge based on screenshot changes")

    async def _execute_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        if current_iteration != total_iterations - 1:
            return False
        return await self._analyze_screenshots(prompt, browser_snapshots)

    async def _analyze_screenshots(
        self,
        prompt: str,
        browser_snapshots: List[BrowserSnapshot],
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ) -> bool:
        """
        Analyzes screenshots to determine success based on LLM evaluation.
        """
        user_msg = f"Task: '{prompt}'\nSuccess Criteria: '{self.success_criteria}'"

        screenshots_after = [snap.screenshot_after for snap in browser_snapshots[-4:]]
        screenshot_content = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot}"}} for screenshot in screenshots_after]
        json_schema = ScreenshotTestResponse.model_json_schema()
        formatted_sys_msg = SCREENSHOT_TEST_SYSTEM_PROMPT.format(json_schema=json_schema)
        payload = [
            {"role": "system", "content": formatted_sys_msg},
            {"role": "user", "content": [{"type": "text", "text": user_msg}, *screenshot_content]},
        ]
        start_time = time.perf_counter()
        result = await llm_service.async_predict(payload, json_format=True, return_raw=True)
        end_time = time.perf_counter()
        duration = round(end_time - start_time, 4)

        save_usage_record(prompt, result, duration, self.type)
        try:
            result_str = result.choices[0].message.content
        except Exception:
            result_str = result
        match = re.search(r'"evaluation_result"\s*:\s*(true|false)', result_str, re.IGNORECASE)

        return match.group(1).lower() == "true" if match else False


def save_usage_record(prompt, response, time_taken, test_type, log_file: Path = PROJECT_BASE_DIR / "judge_tests_usage_logs"):
    """Saves token usage and execution time to log file."""
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    log_entry = {
        "test_type": test_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": prompt,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_seconds": time_taken,
    }
    with log_file.open("a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")
