import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List
from dependency_injector.wiring import Provide
from pydantic import BaseModel, Field, field_validator
from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.data_generation.domain.classes import Task


class ITest(ABC):
    @abstractmethod
    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        """
        Abstract method to implement the specific logic for the test.

        Args:
            task (Any): The task being tested.
            browser_states (List[BrowserSnapshot]): A list of browser states.
            current_iteration (int): The current iteration number.

        Returns:
            bool: True if the test passes, otherwise False.
        """


class BaseTaskTest(BaseModel, ITest):
    """
    Base class for all task tests.
    """

    class Config:
        arbitrary_types_allowed = True

    def execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        return self._execute_test(task, browser_states, current_iteration)

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")


class CheckUrlTest(BaseTaskTest):
    """
    Test class to verify the current browser URL matches a specified target URL.
    """
    type: str = "CheckUrlTest"
    url: str
    description: str = Field(
        default="Check URL",
        description="Description of the test",
    )

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        """
        Compares the current browser URL to the expected `url`.

        Args:
            browser_states (List[BrowserSnapshot]): Contains the current browser states.

        Returns:
            bool: True if the current URL matches the expected `url`, otherwise False.
        """
        return self.url in browser_states[current_iteration].current_url


class FindInHtmlTest(BaseTaskTest):
    """
    Test class to find specific keywords in the current HTML content.
    """
    type: str = "FindInHtmlTest"
    keywords: List[str] = Field(..., description="List of keywords to search for in the HTML")

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, keywords: List[str]) -> List[str]:
        if not all(keyword.strip() for keyword in keywords):
            raise ValueError("Keywords cannot be empty or consist of only whitespace")
        return [keyword.strip().lower() for keyword in keywords]

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        content = browser_states[current_iteration].current_html.lower()
        return any(keyword in content for keyword in self.keywords)


class CheckEventEmittedTest(BaseTaskTest):
    """
    Test class to verify if a specific backend event was emitted.
    """
    type: str = "CheckEventEmittedTest"
    event_name: str = Field(..., description="Name of the expected backend event")

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        return any(event.event_type == self.event_name for event in browser_states[current_iteration].backend_events)


class CheckPageViewEventTest(BaseTaskTest):
    """
    Test class to verify if a specific page view event was logged in the backend.
    """

    type: str = "CheckPageViewEventTest"
    page_view_url: str = Field(..., description="The URL expected to trigger a page view event")

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        events = browser_states[current_iteration].backend_events
        return self.page_view_url in [event.data.get("url", "") for event in events if event.data]


class JudgeBaseOnHTML(BaseTaskTest):
    """
    Test class to generate an opinion based on changes in HTML before and after an action.
    """
    type: str = "JudgeBaseOnHTML"
    success_criteria: str = Field(..., description="What should the LLM look for to verify success of the task.")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.llm_service = Provide[DIContainer.llm_service]

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        from autoppia_iwa.src.shared.web_utils import clean_html
        html_before = clean_html(browser_states[current_iteration - 1].current_html)
        html_after = clean_html(browser_states[current_iteration].current_html)
        action = str(browser_states[current_iteration].action)
        return self._analyze_htmls(action, html_before, html_after)

    def _analyze_htmls(self, action: str, html_before: str, html_after: str) -> bool:
        system_message = (
            "You are a professional web page analyzer. Your task is to determine whether the given task was completed "
            "with the action given, by analyzing the HTML before and after the action."
        )
        user_message = f"Current action: {action}\nHTML Before:\n{html_before}\n\nHTML After:\n{html_after}"
        payload = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
        with Path(PROJECT_BASE_DIR / "config/schemas/eval_html_test.json").open(encoding="utf-8") as f:
            json_schema = json.load(f)
        result = self.llm_service.predict(payload, json_format=True, schema=json_schema)
        parsed_result = json.loads(result)
        return parsed_result["task_completed"]


class JudgeBaseOnScreenshot(BaseTaskTest):
    """
    Test class to generate an opinion based on screenshots before and after an action.
    """
    type: str = "JudgeBaseOnScreenshot"
    success_criteria: str = Field(..., description="What should the LLM look for to verify success of the task.")

    class Config:
        arbitrary_types_allowed = True

    def _execute_test(self, task: Any, browser_states: List[BrowserSnapshot], current_iteration: int) -> bool:
        return self._analyze_screenshots(
            browser_states[current_iteration - 1].screenshot,
            browser_states[current_iteration].screenshot
        )

    def _analyze_screenshots(self, screenshot_before: str, screenshot_after: str, llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        system_message = (
            "You are a professional web page analyzer. Your task is to determine whether the given task was completed "
            "by analyzing the screenshots before and after the action. Your response must be a JSON object with a single "
            "key 'result' containing either `true` or `false`."
        )
        user_message = f"Task: '{self.success_criteria}'"
        payload = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_before}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_after}"}},
                ],
            },
        ]
        schema_path = Path(PROJECT_BASE_DIR) / "config/schemas/screenshot_test_schema.json"
        with schema_path.open(encoding="utf-8") as f:
            json_schema = json.load(f)
        result = llm_service.predict(payload, json_format=True, schema=json_schema)
        parsed_result = json.loads(result)
        return parsed_result["result"]
