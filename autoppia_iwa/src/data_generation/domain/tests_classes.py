# file: data_generation/domain/tests_classes.py

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Literal  # <-- move the import here
from pydantic import BaseModel, Field, field_validator
from dependency_injector.wiring import Provide

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from bs4 import BeautifulSoup
import re
from typing import List


class ITest(ABC):
    @abstractmethod
    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        """
        Abstract method to implement the specific logic for the test.
        """


class BaseTaskTest(BaseModel, ITest):
    """
    Base class for all task tests.
    """

    class Config:
        arbitrary_types_allowed = True

    def execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        return self._execute_test(current_iteration, prompt, snapshot, browser_snapshots)

    @abstractmethod
    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        """
        Must be overridden by subclasses.
        """

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
        test_classes = {
            "CheckUrlTest": CheckUrlTest,
            "FindInHtmlTest": FindInHtmlTest,
            "CheckEventTest": CheckEventTest,
            "CheckPageViewEventTest": CheckPageViewEventTest,
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
        }
        target_class = test_classes.get(test_type, cls)
        try:
            return target_class.model_validate(data)
        except Exception:
            return target_class(**data)


class CheckUrlTest(BaseTaskTest):
    # We define the 'type' field with a Pydantic Literal
    type: Literal["CheckUrlTest"] = "CheckUrlTest"
    url: str
    description: str = Field(default="Check URL")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        return self.url in snapshot.current_url


class FindInHtmlTest(BaseTaskTest):
    """
    Test class to find a specific substring in the current HTML content.
    This version performs direct substring matching rather than semantic similarity.
    """
    type: str = "FindInHtmlTest"
    substring: str = Field(..., description="substring to look for in the HTML")
    description: str = Field(
        default="Find substring in HTML using direct matching",
        description="Description of the test",
    )

    @field_validator('substring')
    @classmethod
    def validate_substring(cls, substring: str) -> str:
        if not substring.strip():
            raise ValueError("Substring cannot be empty or consist of only whitespace")
        return substring.strip()

    def extract_text_from_html(self, html: str) -> str:
        """Extract readable text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Checks if the specified substring is present in the current snapshot's HTML.
        Returns True if the substring is found, False otherwise.
        """
        case_sensitive = False
        # Extract text from HTML
        content = self.extract_text_from_html(snapshot.current_html)
        # If case-insensitive matching is requested, convert content to lowercase
        if not case_sensitive:
            content = content.lower()

        # Apply case conversion if needed
        search_substring = self.substring if case_sensitive else self.substring.lower()

        if search_substring in content:
            return True
        else:
            return False


class CheckEventTest(BaseTaskTest):
    type: Literal["CheckEventTest"] = "CheckEventTest"
    event_name: str
    description: str = Field(default="Check event")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        return any(event.event_type == self.event_name for event in snapshot.backend_events)


class CheckPageViewEventTest(BaseTaskTest):
    type: Literal["CheckPageViewEventTest"] = "CheckPageViewEventTest"
    page_view_url: str
    description: str = Field(default="Check page view event")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        events = snapshot.backend_events
        return self.page_view_url in [e.data.get("url", "") for e in events if e.data]


class JudgeBaseOnHTML(BaseTaskTest):
    type: Literal["JudgeBaseOnHTML"] = "JudgeBaseOnHTML"
    success_criteria: str
    description: str = Field(default="Judge based on HTML changes")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        from autoppia_iwa.src.shared.web_utils import clean_html

        if current_iteration == 0:
            return False
        html_before = clean_html(browser_snapshots[current_iteration - 1].current_html)
        html_after = clean_html(snapshot.current_html)
        action = str(snapshot.action)
        return self._analyze_htmls(action, html_before, html_after)

    def _analyze_htmls(self, action: str, html_before: str, html_after: str, llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        system_message = (
            "You are a professional web page analyzer. Your task is to determine whether the given task was completed " "with the action given, by analyzing the HTML before and after the action."
        )
        user_message = f"Current action: {action}\nHTML Before:\n{html_before}\n\nHTML After:\n{html_after}"
        payload = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]  # load schema
        schema_path = Path(PROJECT_BASE_DIR) / "config" / "schemas" / "eval_html_test.json"
        json_schema = {}
        if schema_path.exists():
            with schema_path.open(encoding="utf-8") as f:
                json_schema = json.load(f)
        result_str = llm_service.predict(payload, json_format=True, schema=json_schema)
        parsed = json.loads(result_str)
        return parsed["task_completed"]


class JudgeBaseOnScreenshot(BaseTaskTest):
    type: Literal["JudgeBaseOnScreenshot"] = "JudgeBaseOnScreenshot"
    success_criteria: str
    description: str = Field(default="Judge based on screenshot changes")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        if current_iteration == 0:
            return False
        return self._analyze_screenshots(screenshot_before=browser_snapshots[current_iteration].screenshot_before, screenshot_after=browser_snapshots[current_iteration].screenshot_after)

    def _analyze_screenshots(self, screenshot_before: str, screenshot_after: str, llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        system_msg = "You are a professional web page analyzer..."
        user_msg = f"Task: '{self.success_criteria}'"
        payload = [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_msg},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_before}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_after}"}},
                ],
            },
        ]
        schema_path = Path(PROJECT_BASE_DIR) / "config" / "schemas" / "screenshot_test_schema.json"
        json_schema = {}
        if schema_path.exists():
            with schema_path.open(encoding="utf-8") as f:
                json_schema = json.load(f)
        result_str = llm_service.predict(payload, json_format=True, schema=json_schema)
        parsed = json.loads(result_str)
        return parsed["result"]
