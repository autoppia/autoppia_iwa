#!/usr/bin/env python3
"""
Simplified tests for task generation components.

This module contains basic tests that don't require all project dependencies.
"""

import json
import tempfile
import unittest
from pathlib import Path

# Mock the required classes for testing


class MockTask:
    """Mock Task class for testing."""

    def __init__(self, id: str = "test_task", prompt: str = "Test task", url: str = "http://test.com", web_project_id: str = "test_project"):
        self.id = id
        self.prompt = prompt
        self.url = url
        self.web_project_id = web_project_id
        self.tests = []
        self.is_web_real = False
        self.relevant_data = {}

    def serialize(self):
        """Mock serialize method."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "url": self.url,
            "web_project_id": self.web_project_id,
            "tests": [test.serialize() if hasattr(test, "serialize") else test for test in self.tests],
        }

    def prepare_for_agent(self, web_agent_id: str):
        """Mock prepare_for_agent method."""
        new_task = MockTask(self.id, self.prompt, self.url, self.web_project_id)
        new_task.prompt = self.prompt.replace("<web_agent_id>", web_agent_id)
        new_task.relevant_data = {k: v.replace("<web_agent_id>", web_agent_id) if isinstance(v, str) else v for k, v in self.relevant_data.items()}
        return new_task


class MockCheckEventTest:
    """Mock CheckEventTest class for testing."""

    def __init__(self, event_name: str = "test_event", event_criteria: dict | None = None, reasoning: str = "Test reasoning"):
        self.type = "CheckEventTest"
        self.event_name = event_name
        self.event_criteria = event_criteria or {"field1": {"value": "expected_value", "operator": "equals"}}
        self.reasoning = reasoning

    def serialize(self):
        return {"type": self.type, "event_name": self.event_name, "event_criteria": self.event_criteria, "reasoning": self.reasoning}


class MockWebProject:
    """Mock WebProject class for testing."""

    def __init__(self, id: str = "test_project", name: str = "Test Project", urls: list[str] | None = None):
        self.id = id
        self.name = name
        self.urls = urls or ["http://test.com"]
        self.frontend_url = "http://test.com"
        self.relevant_data = {"key": "value"}
        self.use_cases = []


class MockUseCase:
    """Mock UseCase class for testing."""

    def __init__(self, name: str = "Test Use Case", description: str = "Test description"):
        self.name = name
        self.description = description
        self.additional_prompt_info = "Test additional info"

    def get_example_prompts_str(self):
        return "Example prompts"

    def apply_replacements(self, prompt: str):
        return prompt.replace("<web_agent_id>", "agent_123")

    def generate_constraints(self):
        return "Test constraints"


class MockTaskGenerationConfig:
    """Mock TaskGenerationConfig class for testing."""

    def __init__(self, generate_global_tasks: bool = True, prompts_per_use_case: int = 1, num_use_cases: int = 3, final_task_limit: int = 50):
        self.generate_global_tasks = generate_global_tasks
        self.prompts_per_use_case = prompts_per_use_case
        self.num_use_cases = num_use_cases
        self.final_task_limit = final_task_limit


class TestTaskCreation(unittest.TestCase):
    """Test cases for task creation and basic functionality."""

    def test_mock_task_creation(self):
        """Test creating a mock task."""
        task = MockTask(id="task_1", prompt="Test task", url="http://test.com", web_project_id="test_project")

        self.assertEqual(task.id, "task_1")
        self.assertEqual(task.prompt, "Test task")
        self.assertEqual(task.url, "http://test.com")
        self.assertEqual(task.web_project_id, "test_project")
        self.assertFalse(task.is_web_real)

    def test_task_prepare_for_agent(self):
        """Test task preparation for agent with ID replacement."""
        task = MockTask(prompt="Task for <web_agent_id>")
        task.relevant_data = {"username": "user<web_agent_id>"}

        prepared_task = task.prepare_for_agent("agent_123")

        self.assertEqual(prepared_task.prompt, "Task for agent_123")
        self.assertEqual(prepared_task.relevant_data["username"], "useragent_123")

    def test_task_serialization(self):
        """Test task serialization."""
        task = MockTask()
        serialized = task.serialize()

        self.assertIn("id", serialized)
        self.assertIn("prompt", serialized)
        self.assertIn("url", serialized)
        self.assertIn("web_project_id", serialized)
        self.assertIn("tests", serialized)


class TestTestCreation(unittest.TestCase):
    """Test cases for test creation and functionality."""

    def test_check_event_test_creation(self):
        """Test creating a CheckEventTest."""
        test = MockCheckEventTest(
            event_name="purchase_completed",
            event_criteria={"item_color": {"value": "red", "operator": "equals"}, "price": {"value": 10, "operator": "less_than"}},
            reasoning="Verify red dress purchase under $10",
        )

        self.assertEqual(test.type, "CheckEventTest")
        self.assertEqual(test.event_name, "purchase_completed")
        self.assertEqual(test.event_criteria["item_color"]["value"], "red")
        self.assertEqual(test.event_criteria["price"]["value"], 10)
        self.assertEqual(test.reasoning, "Verify red dress purchase under $10")

    def test_test_serialization(self):
        """Test test serialization."""
        test = MockCheckEventTest()
        serialized = test.serialize()

        self.assertEqual(serialized["type"], "CheckEventTest")
        self.assertEqual(serialized["event_name"], "test_event")
        self.assertIn("event_criteria", serialized)
        self.assertEqual(serialized["reasoning"], "Test reasoning")


class TestWebProjectCreation(unittest.TestCase):
    """Test cases for web project creation and functionality."""

    def test_mock_web_project_creation(self):
        """Test creating a mock web project."""
        project = MockWebProject(id="test_project", name="Test Project", urls=["http://test1.com", "http://test2.com"])

        self.assertEqual(project.id, "test_project")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(len(project.urls), 2)
        self.assertEqual(project.frontend_url, "http://test.com")
        self.assertEqual(project.relevant_data, {"key": "value"})

    def test_web_project_url_handling(self):
        """Test web project URL handling."""
        project = MockWebProject(urls=["http://url1.com", "http://url2.com"])
        first_url = project.urls[0] if project.urls else project.frontend_url
        self.assertEqual(first_url, "http://url1.com")

        project_no_urls = MockWebProject(urls=[])
        fallback_url = project_no_urls.urls[0] if project_no_urls.urls else project_no_urls.frontend_url
        self.assertEqual(fallback_url, "http://test.com")


class TestUseCaseCreation(unittest.TestCase):
    """Test cases for use case creation and functionality."""

    def test_mock_use_case_creation(self):
        """Test creating a mock use case."""
        use_case = MockUseCase(name="E-commerce Purchase", description="Purchase items from an online store")

        self.assertEqual(use_case.name, "E-commerce Purchase")
        self.assertEqual(use_case.description, "Purchase items from an online store")
        self.assertEqual(use_case.additional_prompt_info, "Test additional info")

    def test_use_case_prompt_replacement(self):
        """Test use case prompt replacement functionality."""
        use_case = MockUseCase()
        original_prompt = "Task for <web_agent_id>"
        modified_prompt = use_case.apply_replacements(original_prompt)

        self.assertEqual(modified_prompt, "Task for agent_123")

    def test_use_case_constraints(self):
        """Test use case constraints generation."""
        use_case = MockUseCase()
        constraints = use_case.generate_constraints()

        self.assertEqual(constraints, "Test constraints")


class TestTaskGenerationConfig(unittest.TestCase):
    """Test cases for task generation configuration."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = MockTaskGenerationConfig()

        self.assertTrue(config.generate_global_tasks)
        self.assertEqual(config.prompts_per_use_case, 1)
        self.assertEqual(config.num_use_cases, 3)
        self.assertEqual(config.final_task_limit, 50)

    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = MockTaskGenerationConfig(generate_global_tasks=False, prompts_per_use_case=5, num_use_cases=2, final_task_limit=20)

        self.assertFalse(config.generate_global_tasks)
        self.assertEqual(config.prompts_per_use_case, 5)
        self.assertEqual(config.num_use_cases, 2)
        self.assertEqual(config.final_task_limit, 20)


class TestTaskCaching(unittest.TestCase):
    """Test cases for task caching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_project = MockWebProject()
        self.test_tasks = [MockTask(id="task_1", prompt="Test task 1", url="http://test.com"), MockTask(id="task_2", prompt="Test task 2", url="http://test.com")]

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_filename_generation(self):
        """Test cache filename generation."""
        filename = f"{self.temp_dir}/{self.mock_project.name.replace(' ', '_').lower()}_tasks.json"
        expected = f"{self.temp_dir}/test_project_tasks.json"
        self.assertEqual(filename, expected)

    def test_task_serialization_for_cache(self):
        """Test task serialization for caching."""
        task = MockTask()
        serialized = task.serialize()

        self.assertIn("id", serialized)
        self.assertIn("prompt", serialized)
        self.assertIn("url", serialized)
        self.assertIn("web_project_id", serialized)

    def test_cache_file_creation(self):
        """Test cache file creation."""
        cache_file = Path(self.temp_dir) / "test_project_tasks.json"

        # Create cache content
        cache_content = {"project_id": self.mock_project.id, "project_name": self.mock_project.name, "timestamp": "2024-01-01T00:00:00", "tasks": [task.serialize() for task in self.test_tasks]}

        # Write cache file
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump(cache_content, f, indent=2)

        # Verify file was created
        self.assertTrue(cache_file.exists())

        # Verify content
        with open(cache_file) as f:
            data = json.load(f)
            self.assertEqual(data["project_id"], "test_project")
            self.assertEqual(data["project_name"], "Test Project")
            self.assertEqual(len(data["tasks"]), 2)


class TestLLMIntegration(unittest.TestCase):
    """Test cases for LLM integration and response parsing."""

    def test_llm_response_parsing(self):
        """Test parsing LLM responses."""
        # Test valid JSON response
        valid_response = json.dumps(["Task 1", "Task 2", "Task 3"])
        parsed = json.loads(valid_response)

        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], "Task 1")
        self.assertEqual(parsed[1], "Task 2")
        self.assertEqual(parsed[2], "Task 3")

    def test_llm_test_response_parsing(self):
        """Test parsing LLM test responses."""
        test_response = json.dumps(
            [{"type": "CheckEventTest", "event_name": "purchase_completed", "event_criteria": {"item_color": {"value": "red", "operator": "equals"}}, "reasoning": "Verify red dress purchase"}]
        )

        parsed = json.loads(test_response)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["type"], "CheckEventTest")
        self.assertEqual(parsed[0]["event_name"], "purchase_completed")
        self.assertEqual(parsed[0]["event_criteria"]["item_color"]["value"], "red")

    def test_markdown_code_block_parsing(self):
        """Test parsing responses with markdown code blocks."""
        markdown_response = '```json\n["Task 1", "Task 2"]\n```'

        # Extract JSON from markdown
        if markdown_response.strip().startswith("```"):
            lines = markdown_response.strip().split("\n")
            cleaned_text = "\n".join(lines[1:-1] if lines[-1].endswith("```") else lines[1:]) if lines[0].startswith("```") else markdown_response
        else:
            cleaned_text = markdown_response

        parsed = json.loads(cleaned_text)

        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], "Task 1")
        self.assertEqual(parsed[1], "Task 2")


class TestTaskGenerationIntegration(unittest.TestCase):
    """Integration tests for task generation."""

    def test_end_to_end_task_creation(self):
        """Test complete end-to-end task creation process."""
        # Create web project
        project = MockWebProject(id="integration_test", name="Integration Test Project")

        # Create use case
        MockUseCase(name="Integration Use Case", description="Test integration scenario")

        # Create configuration
        MockTaskGenerationConfig(generate_global_tasks=True, prompts_per_use_case=2, num_use_cases=1, final_task_limit=5)

        # Create tasks
        tasks = [MockTask(id=f"task_{i}", prompt=f"Integration task {i}", url="http://integration.com", web_project_id=project.id) for i in range(3)]

        # Add tests to tasks
        for task in tasks:
            test = MockCheckEventTest(event_name=f"task_{task.id}_completed", event_criteria={"status": {"value": "completed", "operator": "equals"}}, reasoning=f"Verify completion of {task.prompt}")
            task.tests.append(test)

        # Verify results
        self.assertEqual(len(tasks), 3)
        self.assertEqual(len(tasks[0].tests), 1)
        self.assertEqual(tasks[0].tests[0].event_name, "task_task_0_completed")

        # Test task preparation for agent
        prepared_task = tasks[0].prepare_for_agent("agent_123")
        self.assertEqual(prepared_task.prompt, "Integration task 0")

        # Test serialization
        serialized_tasks = [task.serialize() for task in tasks]
        self.assertEqual(len(serialized_tasks), 3)
        self.assertIn("id", serialized_tasks[0])
        self.assertIn("tests", serialized_tasks[0])


if __name__ == "__main__":
    # Run tests
    unittest.main()
