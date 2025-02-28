# file: data_generation/domain/tests_classes.py

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator
from dependency_injector.wiring import Provide

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.domain.interfaces import ILLM


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
        """Public method that calls the internal _execute_test."""
        return self._execute_test(current_iteration, prompt, snapshot, browser_snapshots)

    @abstractmethod
    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        """
        Must be overridden by subclasses.
        """

    def serialize(self) -> dict:
        """
        Serialize a BaseTaskTest (or subclass) to a dict for JSON.
        Ensures 'type' is included.
        """
        serialized = self.model_dump()
        if "type" not in serialized:
            # if the subclass doesn't define a literal type, fallback
            serialized["type"] = self.__class__.__name__
        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> "BaseTaskTest":
        """
        Generic manual approach if needed.
        If using Union approach in `Task`, you typically won't call this.
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
    from typing import Literal

    type: Literal["CheckUrlTest"] = "CheckUrlTest"
    url: str
    description: str = Field(default="Check URL")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        return self.url in snapshot.current_url


class FindInHtmlTest(BaseTaskTest):
    from typing import Literal

    type: Literal["FindInHtmlTest"] = "FindInHtmlTest"
    keywords: List[str] = Field(..., description="List of keywords to search in the HTML")
    description: str = Field(default="Find keywords in HTML")

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, keywords: List[str]) -> List[str]:
        if not all(k.strip() for k in keywords):
            raise ValueError("Keywords cannot be empty or whitespace.")
        return [k.strip().lower() for k in keywords]

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        content = snapshot.current_html.lower()
        return any(k in content for k in self.keywords)


class CheckEventTest(BaseTaskTest):
    from typing import Literal

    type: Literal["CheckEventTest"] = "CheckEventTest"
    event_name: str
    description: str = Field(default="Check event")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        return any(event.event_type == self.event_name for event in snapshot.backend_events)


class CheckPageViewEventTest(BaseTaskTest):
    from typing import Literal

    type: Literal["CheckPageViewEventTest"] = "CheckPageViewEventTest"
    page_view_url: str
    description: str = Field(default="Check page view event")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        events = snapshot.backend_events
        return self.page_view_url in [e.data.get("url", "") for e in events if e.data]


class JudgeBaseOnHTML(BaseTaskTest):
    from typing import Literal

    type: Literal["JudgeBaseOnHTML"] = "JudgeBaseOnHTML"
    success_criteria: str = Field(..., description="What should the LLM look for to verify success of the task.")
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
    from typing import Literal

    type: Literal["JudgeBaseOnScreenshot"] = "JudgeBaseOnScreenshot"
    success_criteria: str = Field(..., description="What should the LLM look for to verify success of the task.")
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
