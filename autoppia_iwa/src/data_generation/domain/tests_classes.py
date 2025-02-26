import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator
from dependency_injector.wiring import Provide

# Updated import for Task
from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.domain.interfaces import ILLM


class ITest(ABC):
    @abstractmethod
    def _execute_test(
        self,
        current_iteration: int,
        prompt:str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Abstract method to implement the specific logic for the test.

        Args:
            current_iteration (int): The current iteration index.
            task (Task): The task being tested.
            snapshot (BrowserSnapshot): The browser snapshot for the current iteration.
            browser_snapshots (List[BrowserSnapshot]): All available browser snapshots.

        Returns:
            bool: True if the test passes, otherwise False.
        """


class BaseTaskTest(BaseModel, ITest):
    """
    Base class for all task tests.
    """
    class Config:
        arbitrary_types_allowed = True

    def execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Entry point for running the test. It calls the internal `_execute_test`.
        """
        return self._execute_test(current_iteration=current_iteration, prompt=prompt, snapshot=snapshot, browser_snapshots=browser_snapshots)

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Placeholder method to be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def serialize(self) -> dict:
        """
        Serialize a BaseTaskTest object to a dictionary suitable for JSON storage.

        Returns:
            dict: A serialized representation of the test
        """
        # Get basic model data
        serialized = self.model_dump()

        # Ensure type is included for proper deserialization
        if not "type" in serialized:
            serialized["type"] = self.__class__.__name__

        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> "BaseTaskTest":
        """
        Deserialize a dictionary into a BaseTaskTest or its subclass instance.

        Args:
            data (dict): Serialized test data

        Returns:
            BaseTaskTest: A reconstructed test object of the appropriate subclass
        """
        # Get test type
        test_type = data.get("type")

        # Import all test classes dynamically to avoid circular imports
        # This approach assumes all test classes are defined in the same module
        test_classes = {
            "CheckUrlTest": CheckUrlTest,
            "FindInHtmlTest": FindInHtmlTest,
            "CheckEventTest": CheckEventTest,
            "CheckPageViewEventTest": CheckPageViewEventTest,
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
            # Add any additional test classes here
        }

        # Get the appropriate class based on type
        target_class = test_classes.get(test_type, cls)

        # Create and return the instance
        try:
            return target_class.model_validate(data)
        except Exception as e:
            # Fallback if validation fails
            return target_class(**data)


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

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Compares the current snapshot URL to the expected `url`.
        """
        return self.url in snapshot.current_url


class FindInHtmlTest(BaseTaskTest):
    """
    Test class to find specific keywords in the current HTML content.
    """
    type: str = "FindInHtmlTest"
    keywords: List[str] = Field(..., description="List of keywords to search for in the HTML")
    description: str = Field(
        default="Find keywords in HTML",
        description="Description of the test",
    )

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, keywords: List[str]) -> List[str]:
        if not all(keyword.strip() for keyword in keywords):
            raise ValueError("Keywords cannot be empty or consist of only whitespace")
        return [keyword.strip().lower() for keyword in keywords]

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Checks if any of the specified keywords is present in the current snapshot's HTML.
        """
        content = snapshot.current_html.lower()
        return any(keyword in content for keyword in self.keywords)


class CheckEventTest(BaseTaskTest):
    """
    Test class to verify if a specific backend event was emitted.
    """
    type: str = "CheckEventTest"
    event_name: str = Field(..., description="Name of the expected backend event")
    description: str = Field(
        default="Check event",
        description="Description of the test",
    )

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Checks for the presence of the specified event name in the current snapshot's backend events.
        """
        return any(event.event_type == self.event_name for event in snapshot.backend_events)


class CheckPageViewEventTest(BaseTaskTest):
    """
    Test class to verify if a specific page view event was logged in the backend.
    """
    type: str = "CheckPageViewEventTest"
    page_view_url: str = Field(..., description="The URL expected to trigger a page view event")
    description: str = Field(
        default="Check page view event",
        description="Description of the test",
    )

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Looks for a page view event that has 'url' matching `page_view_url`.
        """
        events = snapshot.backend_events
        return self.page_view_url in [event.data.get("url", "") for event in events if event.data]


class JudgeBaseOnHTML(BaseTaskTest):
    """
    Test class to generate an opinion based on changes in HTML before and after an action.
    """
    type: str = "JudgeBaseOnHTML"
    success_criteria: str = Field(..., description="What should the LLM look for to verify success of the task.")
    description: str = Field(
        default="Judge based on HTML changes",
        description="Description of the test",
    )

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Retrieves the HTML before this iteration and compares it to the current iteration's HTML.
        Uses an LLM to determine if the task was successfully completed.
        """
        from autoppia_iwa.src.shared.web_utils import clean_html
        # Guard for current_iteration - 1
        if current_iteration == 0:
            return False  # Or handle differently if needed
        html_before = clean_html(browser_snapshots[current_iteration - 1].current_html)
        html_after = clean_html(snapshot.current_html)
        action = str(snapshot.action)
        return self._analyze_htmls(action, html_before, html_after)

    def _analyze_htmls(self, action: str, html_before: str, html_after: str, llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        system_message = (
            "You are a professional web page analyzer. Your task is to determine whether the given task was completed "
            "with the action given, by analyzing the HTML before and after the action."
        )
        user_message = f"Current action: {action}\nHTML Before:\n{html_before}\n\nHTML After:\n{html_after}"
        payload = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        schema_path = Path(PROJECT_BASE_DIR) / "config" / "schemas" / "eval_html_test.json"
        with schema_path.open(encoding="utf-8") as f:
            json_schema = json.load(f)
        result = llm_service.predict(payload, json_format=True, schema=json_schema)
        parsed_result = json.loads(result)
        return parsed_result["task_completed"]


class JudgeBaseOnScreenshot(BaseTaskTest):
    """
    Test class to generate an opinion based on screenshots before and after an action.
    """
    type: str = "JudgeBaseOnScreenshot"
    success_criteria: str = Field(..., description="What should the LLM look for to verify success of the task.")
    description: str = Field(
        default="Judge based on screenshot changes",
        description="Description of the test",
    )

    class Config:
        arbitrary_types_allowed = True

    def _execute_test(
        self,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: List[BrowserSnapshot]
    ) -> bool:
        """
        Compares screenshots from the previous iteration and the current iteration to see
        if the task was successfully completed based on visual changes.
        """
        if current_iteration == 0:
            return False  # Or raise an exception if a "previous" screenshot is required
        return self._analyze_screenshots(
            screenshot_before=browser_snapshots[current_iteration].screenshot_before,
            screenshot_after=browser_snapshots[current_iteration].screenshot_after,
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
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_after}"}}
                ],
            },
        ]
        schema_path = Path(PROJECT_BASE_DIR) / "config" / "schemas" / "screenshot_test_schema.json"
        with schema_path.open(encoding="utf-8") as f:
            json_schema = json.load(f)
        result = llm_service.predict(payload, json_format=True, schema=json_schema)
        parsed_result = json.loads(result)
        return parsed_result["result"]
