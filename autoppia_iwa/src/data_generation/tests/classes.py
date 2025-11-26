# file: data_generation/domain/tests_classes.py
import json
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Literal

try:  # Optional: allow running without dependency_injector (e.g., Py3.13 wheels)
    from dependency_injector.wiring import Provide  # type: ignore
except Exception:  # pragma: no cover - lightweight fallback for environments without the package

    class Provide:  # type: ignore
        """Minimal stub so annotations like Provide[DIContainer.llm_service] don't break imports.

        Note: Tests that rely on DI-injected services (e.g., LLM-based judge tests)
        should not run when this stub is active. Simpler tests such as CheckUrlTest
        and FindInHtmlTest will continue to work.
        """

        def __class_getitem__(cls, item):
            return None


from loguru import logger

try:  # Optional: avoid forcing openai dependency for non-LLM tests
    from openai.types.chat import ChatCompletion  # type: ignore
except Exception:  # pragma: no cover - fallback type stub

    class ChatCompletion:  # type: ignore
        pass


from pydantic import BaseModel, Field, ValidationError

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject

try:  # Optional: avoid importing DI machinery when not installed
    from autoppia_iwa.src.di_container import DIContainer  # type: ignore
except Exception:  # pragma: no cover - fallback DI stub

    class DIContainer:  # type: ignore
        llm_service = object()


from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.interfaces import ILLM

# Avoid importing heavy optional deps (e.g., Pillow) at module import time.
# Import helpers locally inside methods that need them.
from .prompts import OPINION_BASED_HTML_TEST_SYS_MSG, SCREENSHOT_TEST_SYSTEM_PROMPT

# Moved from schemas.py - consolidated into classes.py


class ITest(ABC):
    @abstractmethod
    async def _execute_partial_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
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
        browser_snapshots: list[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Executes the test by delegating to the _execute_partial_test method.
        """

        return await self._execute_partial_test(web_project, current_iteration, prompt, snapshot, browser_snapshots, total_iterations)

    async def execute_global_test(
        self,
        backend_events: list[BackendEvent],
    ) -> bool:
        """
        Executes the test by delegating to the _execute_partial_test method.
        """

        return await self._execute_global_test(backend_events)

    async def _execute_partial_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Method not implemented")

    async def _execute_global_test(
        self,
        backend_events: list[BackendEvent],
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
        test_classes: dict[str, type[BaseTaskTest]] = {
            "CheckEventTest": CheckEventTest,
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
        }
        target_class = test_classes.get(test_type, cls)
        try:
            return target_class.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Failed to deserialize data: {e}") from e


class CheckEventTest(BaseTaskTest):
    """
    Test that checks if specific events were triggered based on event type and criteria.
    """

    type: Literal["CheckEventTest"] = "CheckEventTest"
    event_name: str
    event_criteria: dict = Field(default_factory=dict)
    description: str = Field(default="Check if specific event was triggered")

    async def _execute_partial_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        """
        Execute the test on the given snapshots by checking for specific events.
        """
        from autoppia_iwa.src.demo_webs.projects.base_events import Event

        if (current_iteration + 1) < total_iterations:
            return False
        parsed_events: list[Event] = Event.parse_all(snapshot.backend_events)
        valid_events: list[Event] = []
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

    async def _execute_global_test(
        self,
        backend_events: list[BackendEvent],
    ) -> bool:
        """
        Execute the test on the given snapshots by checking for specific events.
        """
        from autoppia_iwa.src.demo_webs.projects.base_events import Event

        parsed_events: list[Event] = Event.parse_all(backend_events)
        valid_events: list[Event] = []
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

    async def _execute_partial_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        if current_iteration != total_iterations - 1:
            return False

        all_htmls = self._collect_all_htmls(browser_snapshots)
        if not all_htmls:
            logger.warning("No HTML content found in browser snapshots.")
            return False

        # Local import to avoid heavy deps during non-LLM tests
        from autoppia_iwa.src.shared.web_utils import generate_html_differences

        differences = generate_html_differences(all_htmls)
        # differences = generate_html_differences_with_xmldiff(all_htmls)
        if not differences:
            logger.info("No significant HTML differences detected.")
            return False

        return await self._analyze_htmls(prompt, total_iterations, differences)

    @staticmethod
    def _collect_all_htmls(browser_snapshots: list[BrowserSnapshot]) -> list[str]:
        """
        Collects all HTMLs in order from the browser snapshots and cleans them.
        Returns a list of cleaned HTML strings.
        """
        if not browser_snapshots:
            logger.warning("No browser snapshots provided.")
            return []

        all_htmls = [html for snap in browser_snapshots for html in ([snap.prev_html, snap.current_html] if snap == browser_snapshots[0] else [snap.current_html]) if html]

        # Local import to avoid heavy deps during non-LLM tests
        from autoppia_iwa.src.shared.web_utils import clean_html

        cleaned_htmls = []
        for html in all_htmls:
            try:
                cleaned_html = clean_html(html)
                if cleaned_html:
                    cleaned_htmls.append(cleaned_html)
            except Exception as e:
                logger.warning(f"Failed to clean HTML: {e}")

        return cleaned_htmls

    async def _analyze_htmls(self, task_prompt: str, total_iteration: int, differences: list[str], llm_service: ILLM = Provide[DIContainer.llm_service]) -> bool:
        """
        Analyzes HTML changes using an LLM to determine success.
        """
        json_schema = HTMLBasedTestResponse.model_json_schema()
        formatted_sys_msg = OPINION_BASED_HTML_TEST_SYS_MSG.format(json_schema=json_schema)
        user_message = f"Task: {task_prompt}\n\nHTML differences:\n{' '.join(differences[:-3])}"
        payload = [{"role": "system", "content": formatted_sys_msg}, {"role": "user", "content": user_message}]

        start_time = time.perf_counter()

        try:
            result = await llm_service.async_predict(payload, json_format=True, return_raw=True)
        except Exception as e:
            logger.error(f"LLM service failed to predict: {e}")
            return False

        end_time = time.perf_counter()
        duration = round(end_time - start_time, 3)
        try:
            result_str = result.choices[0].message.content
        except Exception:
            result_str = result

        logger.info(f"HTML Judge LLM response: {result_str}")

        match = re.search(r'"evaluation_result"\s*:\s*(true|false)', result_str, re.IGNORECASE)
        final_result = match.group(1).lower() == "true" if match else False
        save_usage_record(task_prompt, result, duration, self.type, final_result=final_result, total_iteration=total_iteration)

        return final_result


class JudgeBaseOnScreenshot(BaseTaskTest):
    type: Literal["JudgeBaseOnScreenshot"] = "JudgeBaseOnScreenshot"
    success_criteria: str
    description: str = Field(default="Judge based on screenshot changes")

    async def _execute_partial_test(
        self,
        web_project: WebProject,
        current_iteration: int,
        prompt: str,
        snapshot: BrowserSnapshot,
        browser_snapshots: list[BrowserSnapshot],
        total_iterations: int,
    ) -> bool:
        if current_iteration != total_iterations - 1:
            return False
        return await self._analyze_screenshots(prompt, total_iterations, browser_snapshots)

    async def _analyze_screenshots(
        self,
        prompt: str,
        total_iteration: int,
        browser_snapshots: list[BrowserSnapshot],
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ) -> bool:
        """
        Analyzes screenshots to determine success based on LLM evaluation.
        """
        user_msg = f"Task: '{prompt}'\nSuccess Criteria: '{self.success_criteria}'"

        screenshots_after = [snap.screenshot_after for snap in browser_snapshots[-4:] if snap.screenshot_after]
        if not screenshots_after:
            logger.warning("No screenshots found in the latest browser snapshots.")
            return False

        screenshot_content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot}"}} for screenshot in screenshots_after]
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
        try:
            result_str = result.choices[0].message.content
        except Exception:
            result_str = result

        logger.info(f"Screenshots Judge LLM response: {result_str}")

        match = re.search(r'"evaluation_result"\s*:\s*(true|false)', result_str, re.IGNORECASE)
        final_result = match.group(1).lower() == "true" if match else False
        save_usage_record(prompt, result, duration, self.type, final_result=final_result, total_iteration=total_iteration)

        return final_result


def save_usage_record(prompt, response: "ChatCompletion", time_taken, test_type, final_result: bool, total_iteration, log_file: Path = PROJECT_BASE_DIR / "judge_tests_usage_logs.jsonl"):
    """Saves basic test execution info to log file."""
    try:
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        model_name = response.model
    except Exception:
        input_tokens = output_tokens = total_tokens = 0
        model_name = "unknown"

    log_entry = {
        "test_type": test_type,
        "final_test_result": final_result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": prompt,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "duration_seconds": time_taken,
        "model": model_name,
        "total_iteration": total_iteration,
    }

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[ERROR] Failed to write to log file: {e}")


class ScreenshotTestResponse(BaseModel):
    """Represents the evaluation result for a screenshot-based test."""

    evaluation_result: bool = Field(..., description="Indicates whether the task execution was successful.")
    justification: str | None = Field(None, description="Optional explanation supporting the evaluation decision.")


class HTMLBasedTestResponse(BaseModel):
    """Represents the evaluation result for an HTML-based test."""

    evaluation_result: bool = Field(..., description="Indicates whether the task execution was successful.")
    justification: str | None = Field(None, description="Optional explanation supporting the evaluation decision.")
