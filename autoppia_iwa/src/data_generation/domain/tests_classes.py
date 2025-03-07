# file: data_generation/domain/tests_classes.py
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Literal

from bs4 import BeautifulSoup
from dependency_injector.wiring import Provide
from pydantic import BaseModel, Field, field_validator

from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.domain.interfaces import ILLM

from .tests_prompts import OPINION_BASED_HTML_TEST_SYS_MSG, SCREENSHOT_TEST_SYSTEM_PROMPT
from .tests_schemas import HTMLBasedTestResponse, ScreenshotTestResponse


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
        extra = "allow"
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
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
        }
        target_class = test_classes.get(test_type, cls)
        try:
            return target_class.model_validate(data)
        except Exception:
            return target_class(**data)


class CheckUrlTest(BaseTaskTest):
    """
    Test that checks if the browser navigated to a specific URL with different matching options.
    """

    type: Literal["CheckUrlTest"] = "CheckUrlTest"
    url: str
    match_type: Literal["exact", "contains", "regex"] = "contains"
    description: str = Field(default="Check if browser navigated to URL")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
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
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
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

    def _execute_test(self, web_project: WebProject, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        """
        Execute the test on the given snapshots by checking for specific events.
        """
        # This version requires the web_project parameter
        # We'll need to adapt this for the current interface

        # Assuming the snapshot contains backend_events and we can access the event classes
        # from somewhere accessible in this context
        events = web_project.events

        # Get the event class matching event_name
        event_class = next((event_cls for event_cls in events if event_cls.__name__ == self.event_name), None)
        if not event_class:
            return False

        # Get the validation criteria class from the event class
        validation_model = event_class.ValidationCriteria

        # Parse the criteria using the appropriate Pydantic model
        try:
            parsed_criteria = validation_model(**self.event_criteria)
        except Exception as e:
            print(f"Invalid validation criteria: {e}")
            return False
        from autoppia_iwa.src.demo_webs.projects.base_events import Event

        # Check if any event of the correct type matches our criteria
        for event in Event.parse_all(snapshot.backend_events):
            if isinstance(event, event_class) and event.validate_criteria(parsed_criteria):
                return True

        return False


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
        json_schema = HTMLBasedTestResponse.model_json_schema()
        formatted_sys_msg = OPINION_BASED_HTML_TEST_SYS_MSG.format(json_schema=json_schema)
        user_message = f"Current action: {action}\nHTML Before:\n{html_before}\n\nHTML After:\n{html_after}"
        payload = [{"role": "system", "content": formatted_sys_msg}, {"role": "user", "content": user_message}]

        result_str = llm_service.predict(payload, json_format=True)
        match = re.search(r'"evaluation_result"\s*:\s*(true|false)', result_str, re.IGNORECASE)

        return match.group(1) == "true" if match else False


class JudgeBaseOnScreenshot(BaseTaskTest):
    type: Literal["JudgeBaseOnScreenshot"] = "JudgeBaseOnScreenshot"
    success_criteria: str
    description: str = Field(default="Judge based on screenshot changes")

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        if current_iteration == 0:
            return False
        return self._analyze_screenshots(prompt, browser_snapshots)

    def _analyze_screenshots(self, prompt: str, browser_snapshots: List[BrowserSnapshot], llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        """Analyzes screenshots to determine success based on LLM evaluation."""
        user_msg = f"Task: '{prompt}'\nSuccess Criteria: '{self.success_criteria}'"

        screenshots_after = [snap.screenshot_after for snap in browser_snapshots[-4:]]
        screenshot_content = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot}"}} for screenshot in screenshots_after]
        json_schema = ScreenshotTestResponse.model_json_schema()
        formatted_sys_msg = SCREENSHOT_TEST_SYSTEM_PROMPT.format(json_schema=json_schema)
        payload = [
            {"role": "system", "content": formatted_sys_msg},
            {"role": "user", "content": [{"type": "text", "text": user_msg}, *screenshot_content]},
        ]

        result_str = llm_service.predict(payload, json_format=True)
        match = re.search(r'"evaluation_result"\s*:\s*(true|false)', result_str, re.IGNORECASE)

        return match.group(1) == "true" if match else False


class WebProjectCheckEventTest(BaseTaskTest):
    """
    Test that checks if specific events were triggered with access to WebProject
    """

    type: Literal["WebProjectCheckEventTest"] = "WebProjectCheckEventTest"
    event_name: str
    event_criteria: Dict = Field(default_factory=dict)
    description: str = Field(default="Check if specific event was triggered (with WebProject)")

    def execute_test(self, web_project: WebProject, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        """
        Special version of execute_test that accepts web_project parameter
        """
        events = web_project.events
        # Get the event class matching event_name
        event_class = next((event_cls for event_cls in events if event_cls.__name__ == self.event_name), None)
        if not event_class:
            return False
        # Check if any event of the correct type matches our criteria
        for event in snapshot.backend_events:
            if isinstance(event, event_class) and event.matches_criteria(self.event_criteria):
                return True
        return False

    def _execute_test(self, current_iteration: int, prompt: str, snapshot: BrowserSnapshot, browser_snapshots: List[BrowserSnapshot]) -> bool:
        """
        Fallback implementation when web_project is not available
        """
        print("Warning: WebProjectCheckEventTest requires web_project parameter")
        return False
