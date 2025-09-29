"""
Test utilities for task generation tests.

This module provides common utilities and fixtures for task generation tests.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckUrlTest, FindInHtmlTest
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject


class TaskGenerationTestUtils:
    """Utility class for task generation tests."""

    @staticmethod
    def create_mock_web_project(
        project_id: str = "test_project",
        project_name: str = "Test Project",
        urls: list[str] | None = None,
        frontend_url: str = "http://test.com",
        relevant_data: dict[str, Any] | None = None,
        use_cases: list[UseCase] | None = None,
    ) -> MagicMock:
        """Create a mock WebProject for testing."""
        if urls is None:
            urls = ["http://test.com"]
        if relevant_data is None:
            relevant_data = {"key": "value"}
        if use_cases is None:
            use_cases = []

        mock_project = MagicMock(spec=WebProject)
        mock_project.id = project_id
        mock_project.name = project_name
        mock_project.urls = urls
        mock_project.frontend_url = frontend_url
        mock_project.relevant_data = relevant_data
        mock_project.use_cases = use_cases

        return mock_project

    @staticmethod
    def create_mock_use_case(
        name: str = "Test Use Case", description: str = "Test description", additional_prompt_info: str = "Test additional info", example_prompts: str = "Example prompts"
    ) -> MagicMock:
        """Create a mock UseCase for testing."""
        mock_use_case = MagicMock(spec=UseCase)
        mock_use_case.name = name
        mock_use_case.description = description
        mock_use_case.additional_prompt_info = additional_prompt_info
        mock_use_case.get_example_prompts_str.return_value = example_prompts
        mock_use_case.apply_replacements.return_value = "Modified prompt"
        mock_use_case.generate_constraints.return_value = "Test constraints"

        return mock_use_case

    @staticmethod
    def create_test_task(
        task_id: str = "test_task",
        prompt: str = "Test task",
        url: str = "http://test.com",
        web_project_id: str = "test_project",
        scope: str = "local",
        is_web_real: bool = False,
        relevant_data: dict[str, Any] | None = None,
    ) -> Task:
        """Create a test Task object."""
        if relevant_data is None:
            relevant_data = {"key": "value"}

        return Task(id=task_id, prompt=prompt, url=url, web_project_id=web_project_id, scope=scope, is_web_real=is_web_real, relevant_data=relevant_data)

    @staticmethod
    def create_test_tasks(count: int = 3) -> list[Task]:
        """Create multiple test tasks."""
        return [TaskGenerationTestUtils.create_test_task(task_id=f"task_{i}", prompt=f"Test task {i}", url=f"http://test{i}.com") for i in range(count)]

    @staticmethod
    def create_check_event_test(event_name: str = "test_event", event_criteria: dict[str, Any] | None = None, reasoning: str = "Test reasoning") -> CheckEventTest:
        """Create a CheckEventTest object."""
        if event_criteria is None:
            event_criteria = {"field1": {"value": "expected_value", "operator": "equals"}}

        return CheckEventTest(type="CheckEventTest", event_name=event_name, event_criteria=event_criteria, reasoning=reasoning)

    @staticmethod
    def create_check_url_test(expected_url: str = "http://expected.com", reasoning: str = "URL test reasoning") -> CheckUrlTest:
        """Create a CheckUrlTest object."""
        return CheckUrlTest(type="CheckUrlTest", expected_url=expected_url, reasoning=reasoning)

    @staticmethod
    def create_find_in_html_test(selector: str = "h1", expected_text: str = "Expected Title", reasoning: str = "HTML test reasoning") -> FindInHtmlTest:
        """Create a FindInHtmlTest object."""
        return FindInHtmlTest(type="FindInHtmlTest", selector=selector, expected_text=expected_text, reasoning=reasoning)

    @staticmethod
    def create_task_generation_config(generate_global_tasks: bool = True, prompts_per_use_case: int = 1, num_use_cases: int = 3, final_task_limit: int = 50) -> TaskGenerationConfig:
        """Create a TaskGenerationConfig object."""
        return TaskGenerationConfig(generate_global_tasks=generate_global_tasks, prompts_per_use_case=prompts_per_use_case, num_use_cases=num_use_cases, final_task_limit=final_task_limit)

    @staticmethod
    def create_browser_specification(
        viewport_width: int = 1920, viewport_height: int = 1080, screen_width: int = 1920, screen_height: int = 1080, device_pixel_ratio: float = 1.0
    ) -> BrowserSpecification:
        """Create a BrowserSpecification object."""
        return BrowserSpecification(viewport_width=viewport_width, viewport_height=viewport_height, screen_width=screen_width, screen_height=screen_height, device_pixel_ratio=device_pixel_ratio)

    @staticmethod
    def create_mock_llm_response(prompts: list[str]) -> str:
        """Create a mock LLM response with the given prompts."""
        return json.dumps(prompts)

    @staticmethod
    def create_mock_test_response(tests: list[dict[str, Any]]) -> str:
        """Create a mock LLM response with test data."""
        return json.dumps(tests)

    @staticmethod
    def create_temp_cache_dir() -> str:
        """Create a temporary directory for cache testing."""
        return tempfile.mkdtemp()

    @staticmethod
    def create_cache_file_content(project_id: str = "test_project", project_name: str = "Test Project", tasks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Create cache file content for testing."""
        if tasks is None:
            tasks = []

        return {"project_id": project_id, "project_name": project_name, "timestamp": "2024-01-01T00:00:00", "tasks": tasks}

    @staticmethod
    def write_cache_file(cache_dir: str, project_name: str, content: dict[str, Any]) -> Path:
        """Write cache file content to disk."""
        cache_file = Path(cache_dir) / f"{project_name.replace(' ', '_').lower()}_tasks.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_file, "w") as f:
            json.dump(content, f, indent=2)

        return cache_file

    @staticmethod
    def assert_task_equality(task1: Task, task2: Task, exclude_fields: list[str] | None = None):
        """Assert that two tasks are equal, excluding specified fields."""
        if exclude_fields is None:
            exclude_fields = ["id", "timestamp"]

        # Convert to dict and remove excluded fields
        dict1 = task1.model_dump()
        dict2 = task2.model_dump()

        for field in exclude_fields:
            dict1.pop(field, None)
            dict2.pop(field, None)

        assert dict1 == dict2, f"Tasks are not equal: {dict1} != {dict2}"

    @staticmethod
    def assert_test_equality(test1: Any, test2: Any):
        """Assert that two test objects are equal."""
        dict1 = test1.model_dump()
        dict2 = test2.model_dump()

        assert dict1 == dict2, f"Tests are not equal: {dict1} != {dict2}"


class TaskGenerationTestBase(unittest.TestCase):
    """Base test class for task generation tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.utils = TaskGenerationTestUtils()
        self.temp_dir = self.utils.create_temp_cache_dir()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_mock_web_project(self, **kwargs):
        """Create a mock web project for testing."""
        return self.utils.create_mock_web_project(**kwargs)

    def create_mock_use_case(self, **kwargs):
        """Create a mock use case for testing."""
        return self.utils.create_mock_use_case(**kwargs)

    def create_test_task(self, **kwargs):
        """Create a test task for testing."""
        return self.utils.create_test_task(**kwargs)

    def create_test_tasks(self, count: int = 3):
        """Create multiple test tasks for testing."""
        return self.utils.create_test_tasks(count)

    def create_task_generation_config(self, **kwargs):
        """Create a task generation config for testing."""
        return self.utils.create_task_generation_config(**kwargs)

    def assert_task_equality(self, task1: Task, task2: Task, exclude_fields: list[str] | None = None):
        """Assert that two tasks are equal."""
        self.utils.assert_task_equality(task1, task2, exclude_fields)

    def assert_test_equality(self, test1: Any, test2: Any):
        """Assert that two test objects are equal."""
        self.utils.assert_test_equality(test1, test2)


class MockLLMService:
    """Mock LLM service for testing."""

    def __init__(self, responses: list[str] | None = None):
        """Initialize with optional predefined responses."""
        self.responses = responses or []
        self.call_count = 0

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False) -> str:
        """Mock async predict method."""
        self.call_count += 1

        if self.responses:
            # Return predefined response
            response_index = (self.call_count - 1) % len(self.responses)
            return self.responses[response_index]

        # Default response
        return json.dumps(["Default task prompt"])

    def set_responses(self, responses: list[str]):
        """Set predefined responses."""
        self.responses = responses
        self.call_count = 0

    def reset(self):
        """Reset call count."""
        self.call_count = 0


class MockWebProject:
    """Mock WebProject for testing."""

    def __init__(
        self,
        project_id: str = "test_project",
        project_name: str = "Test Project",
        urls: list[str] | None = None,
        frontend_url: str = "http://test.com",
        relevant_data: dict[str, Any] | None = None,
        use_cases: list[UseCase] | None = None,
    ):
        """Initialize mock web project."""
        if urls is None:
            urls = ["http://test.com"]
        if relevant_data is None:
            relevant_data = {"key": "value"}
        if use_cases is None:
            use_cases = []

        self.id = project_id
        self.name = project_name
        self.urls = urls
        self.frontend_url = frontend_url
        self.relevant_data = relevant_data
        self.use_cases = use_cases


class MockUseCase:
    """Mock UseCase for testing."""

    def __init__(self, name: str = "Test Use Case", description: str = "Test description", additional_prompt_info: str = "Test additional info", example_prompts: str = "Example prompts"):
        """Initialize mock use case."""
        self.name = name
        self.description = description
        self.additional_prompt_info = additional_prompt_info
        self.example_prompts = example_prompts

    def get_example_prompts_str(self) -> str:
        """Get example prompts string."""
        return self.example_prompts

    def apply_replacements(self, prompt: str) -> str:
        """Apply replacements to prompt."""
        return prompt.replace("<web_agent_id>", "agent_123")

    def generate_constraints(self) -> str:
        """Generate constraints for use case."""
        return "Test constraints"


if __name__ == "__main__":
    # Run tests
    unittest.main()
