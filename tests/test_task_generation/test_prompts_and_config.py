"""
Unit tests for prompts and configuration components.

This module tests:
- Prompt templates and formatting
- Configuration validation
- Task generation configuration
- Use case handling
"""

import unittest
from unittest.mock import MagicMock

from autoppia_iwa.src.data_generation.application.tasks.composited.prompts import COMPOSITED_TASK_GENERATION_PROMPT
from autoppia_iwa.src.data_generation.application.tasks.globals.prompts import GLOBAL_TASK_GENERATION_PROMPT
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject


class TestTaskGenerationConfig(unittest.TestCase):
    """Test cases for TaskGenerationConfig."""

    def test_default_configuration(self):
        """Test default configuration values."""
        # Execute
        config = TaskGenerationConfig()

        # Assertions
        self.assertTrue(config.generate_global_tasks)
        self.assertEqual(config.prompts_per_use_case, 1)
        self.assertEqual(config.num_use_cases, 3)
        self.assertEqual(config.final_task_limit, 50)

    def test_custom_configuration(self):
        """Test custom configuration values."""
        # Execute
        config = TaskGenerationConfig(generate_global_tasks=False, prompts_per_use_case=5, num_use_cases=2, final_task_limit=20)

        # Assertions
        self.assertFalse(config.generate_global_tasks)
        self.assertEqual(config.prompts_per_use_case, 5)
        self.assertEqual(config.num_use_cases, 2)
        self.assertEqual(config.final_task_limit, 20)

    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid configuration
        config = TaskGenerationConfig(prompts_per_use_case=10, num_use_cases=5, final_task_limit=100)

        # Should not raise any exceptions
        self.assertIsInstance(config, TaskGenerationConfig)

    def test_config_edge_cases(self):
        """Test configuration with edge case values."""
        # Test zero values
        config = TaskGenerationConfig(prompts_per_use_case=0, num_use_cases=0, final_task_limit=0)

        self.assertEqual(config.prompts_per_use_case, 0)
        self.assertEqual(config.num_use_cases, 0)
        self.assertEqual(config.final_task_limit, 0)

    def test_config_negative_values(self):
        """Test configuration with negative values."""
        # Test negative values (should be allowed by Pydantic)
        config = TaskGenerationConfig(prompts_per_use_case=-1, num_use_cases=-1, final_task_limit=-1)

        self.assertEqual(config.prompts_per_use_case, -1)
        self.assertEqual(config.num_use_cases, -1)
        self.assertEqual(config.final_task_limit, -1)


class TestPromptTemplates(unittest.TestCase):
    """Test cases for prompt templates."""

    def test_global_task_generation_prompt_format(self):
        """Test global task generation prompt formatting."""
        # Setup
        use_case_name = "E-commerce Purchase"
        use_case_description = "Purchase items from an online store"
        additional_prompt_info = "Generate tasks for buying products"
        constraints_info = "Price must be under $100"
        number_of_prompts = 3

        # Execute
        formatted_prompt = GLOBAL_TASK_GENERATION_PROMPT.format(
            use_case_name=use_case_name,
            use_case_description=use_case_description,
            additional_prompt_info=additional_prompt_info,
            constraints_info=constraints_info,
            number_of_prompts=number_of_prompts,
        )

        # Assertions
        self.assertIn(use_case_name, formatted_prompt)
        self.assertIn(use_case_description, formatted_prompt)
        self.assertIn(additional_prompt_info, formatted_prompt)
        self.assertIn(constraints_info, formatted_prompt)
        self.assertIn(str(number_of_prompts), formatted_prompt)

    def test_global_task_generation_prompt_placeholders(self):
        """Test that all placeholders are present in the prompt template."""
        # Check for required placeholders
        required_placeholders = ["{use_case_name}", "{use_case_description}", "{additional_prompt_info}", "{constraints_info}", "{number_of_prompts}"]

        for placeholder in required_placeholders:
            self.assertIn(placeholder, GLOBAL_TASK_GENERATION_PROMPT)

    def test_composited_task_generation_prompt_format(self):
        """Test composited task generation prompt formatting."""
        # Setup
        prompts_list = ["Task 1", "Task 2", "Task 3"]
        number_of_composites = 2
        tasks_per_composite = 2

        # Execute
        formatted_prompt = COMPOSITED_TASK_GENERATION_PROMPT.format(prompts_list=prompts_list, number_of_composites=number_of_composites, tasks_per_composite=tasks_per_composite)

        # Assertions
        self.assertIn("Task 1", formatted_prompt)
        self.assertIn("Task 2", formatted_prompt)
        self.assertIn("Task 3", formatted_prompt)
        self.assertIn(str(number_of_composites), formatted_prompt)
        self.assertIn(str(tasks_per_composite), formatted_prompt)

    def test_prompt_template_consistency(self):
        """Test that prompt templates are consistent and well-formed."""
        # Test that templates don't have obvious formatting issues
        self.assertNotIn("{{", GLOBAL_TASK_GENERATION_PROMPT)
        self.assertNotIn("}}", GLOBAL_TASK_GENERATION_PROMPT)
        self.assertNotIn("{{", COMPOSITED_TASK_GENERATION_PROMPT)
        self.assertNotIn("}}", COMPOSITED_TASK_GENERATION_PROMPT)


class TestUseCaseIntegration(unittest.TestCase):
    """Test cases for UseCase integration with task generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_use_case = MagicMock(spec=UseCase)
        self.mock_use_case.name = "Test Use Case"
        self.mock_use_case.description = "Test description"
        self.mock_use_case.additional_prompt_info = "Test additional info"
        self.mock_use_case.get_example_prompts_str.return_value = "Example prompts"
        self.mock_use_case.apply_replacements.return_value = "Modified prompt"

    def test_use_case_with_constraints(self):
        """Test use case with constraints generation."""
        # Setup
        self.mock_use_case.generate_constraints.return_value = "Test constraints"

        # Execute
        constraints = self.mock_use_case.generate_constraints()

        # Assertions
        self.assertEqual(constraints, "Test constraints")

    def test_use_case_without_constraints(self):
        """Test use case without constraints."""
        # Setup
        self.mock_use_case.generate_constraints.side_effect = AttributeError("No constraints method")

        # Execute & Assert
        with self.assertRaises(AttributeError):
            self.mock_use_case.generate_constraints()

    def test_use_case_prompt_replacement(self):
        """Test use case prompt replacement functionality."""
        # Setup
        original_prompt = "Task for <web_agent_id>"
        self.mock_use_case.apply_replacements.return_value = "Task for agent_123"

        # Execute
        modified_prompt = self.mock_use_case.apply_replacements(original_prompt)

        # Assertions
        self.assertEqual(modified_prompt, "Task for agent_123")

    def test_use_case_example_prompts(self):
        """Test use case example prompts generation."""
        # Setup
        self.mock_use_case.get_example_prompts_str.return_value = "Example 1, Example 2"

        # Execute
        examples = self.mock_use_case.get_example_prompts_str()

        # Assertions
        self.assertEqual(examples, "Example 1, Example 2")

    def test_use_case_additional_prompt_info(self):
        """Test use case additional prompt info handling."""
        # Test with existing additional_prompt_info
        self.mock_use_case.additional_prompt_info = "Existing info"
        self.assertEqual(self.mock_use_case.additional_prompt_info, "Existing info")

        # Test without additional_prompt_info
        self.mock_use_case.additional_prompt_info = None
        self.assertIsNone(self.mock_use_case.additional_prompt_info)


class TestWebProjectIntegration(unittest.TestCase):
    """Test cases for WebProject integration with task generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_web_project = MagicMock(spec=WebProject)
        self.mock_web_project.id = "test_project"
        self.mock_web_project.name = "Test Project"
        self.mock_web_project.urls = ["http://test.com"]
        self.mock_web_project.frontend_url = "http://test.com"
        self.mock_web_project.relevant_data = {"key": "value"}

    def test_web_project_basic_properties(self):
        """Test basic web project properties."""
        # Assertions
        self.assertEqual(self.mock_web_project.id, "test_project")
        self.assertEqual(self.mock_web_project.name, "Test Project")
        self.assertEqual(self.mock_web_project.urls, ["http://test.com"])
        self.assertEqual(self.mock_web_project.frontend_url, "http://test.com")
        self.assertEqual(self.mock_web_project.relevant_data, {"key": "value"})

    def test_web_project_url_handling(self):
        """Test web project URL handling."""
        # Test with URLs list
        self.mock_web_project.urls = ["http://url1.com", "http://url2.com"]
        first_url = self.mock_web_project.urls[0] if self.mock_web_project.urls else self.mock_web_project.frontend_url
        self.assertEqual(first_url, "http://url1.com")

        # Test with empty URLs list
        self.mock_web_project.urls = []
        fallback_url = self.mock_web_project.urls[0] if self.mock_web_project.urls else self.mock_web_project.frontend_url
        self.assertEqual(fallback_url, "http://test.com")

    def test_web_project_relevant_data(self):
        """Test web project relevant data handling."""
        # Test with relevant data
        self.mock_web_project.relevant_data = {"username": "test_user", "password": "test_pass"}
        self.assertEqual(self.mock_web_project.relevant_data["username"], "test_user")

        # Test with empty relevant data
        self.mock_web_project.relevant_data = {}
        self.assertEqual(len(self.mock_web_project.relevant_data), 0)


class TestTaskModelValidation(unittest.TestCase):
    """Test cases for Task model validation and behavior."""

    def test_task_minimal_creation(self):
        """Test creating a task with minimal required fields."""
        # Execute
        task = Task(prompt="Test task", url="http://test.com")

        # Assertions
        self.assertEqual(task.prompt, "Test task")
        self.assertEqual(task.url, "http://test.com")
        self.assertFalse(task.is_web_real)
        self.assertIsInstance(task.specifications, BrowserSpecification)

    def test_task_with_use_case(self):
        """Test creating a task with use case."""
        # Setup
        use_case = MagicMock(spec=UseCase)
        use_case.name = "Test Use Case"

        # Execute
        task = Task(prompt="Test task", url="http://test.com", use_case=use_case)

        # Assertions
        self.assertEqual(task.use_case, use_case)
        if task.use_case:
            self.assertEqual(task.use_case.name, "Test Use Case")

    def test_task_relevant_data_handling(self):
        """Test task relevant data handling."""
        # Setup
        relevant_data = {"username": "user<web_agent_id>", "nested": {"key": "value<web_agent_id>"}, "list": ["item<web_agent_id>", "other"]}

        # Execute
        task = Task(prompt="Test task", url="http://test.com", relevant_data=relevant_data)

        # Assertions
        self.assertEqual(task.relevant_data["username"], "user<web_agent_id>")
        self.assertEqual(task.relevant_data["nested"]["key"], "value<web_agent_id>")
        self.assertEqual(task.relevant_data["list"][0], "item<web_agent_id>")

    def test_task_prompt_with_relevant_data(self):
        """Test task prompt with relevant data property."""
        # Setup
        task = Task(prompt="Test task", url="http://test.com", relevant_data={"key": "value"})

        # Execute
        prompt_with_data = task.prompt_with_relevant_data

        # Assertions
        self.assertIn("Test task", prompt_with_data)
        self.assertIn("Relevant data you may need", prompt_with_data)
        self.assertIn("key", prompt_with_data)

    def test_task_prompt_without_relevant_data(self):
        """Test task prompt without relevant data."""
        # Setup
        task = Task(prompt="Test task", url="http://test.com")

        # Execute
        prompt_with_data = task.prompt_with_relevant_data

        # Assertions
        self.assertEqual(prompt_with_data, "Test task")

    def test_task_original_prompt_tracking(self):
        """Test task original prompt tracking."""
        # Setup
        task = Task(prompt="Modified task", url="http://test.com", original_prompt="Original task")

        # Assertions
        self.assertEqual(task.prompt, "Modified task")
        self.assertEqual(task.original_prompt, "Original task")

    def test_task_clean_task_method(self):
        """Test task clean_task method."""
        # Setup
        task = Task(prompt="Test task", url="http://test.com", html="<html>Test</html>", clean_html="<html>Test</html>", tests=[], relevant_data={"key": "value"})

        # Execute
        cleaned = task.clean_task()

        # Assertions
        self.assertIn("prompt", cleaned)
        self.assertIn("url", cleaned)
        self.assertIn("original_prompt", cleaned)
        self.assertNotIn("html", cleaned)
        self.assertNotIn("clean_html", cleaned)
        self.assertNotIn("tests", cleaned)

    def test_task_prepare_for_agent(self):
        """Test task preparation for agent with ID replacement."""
        # Setup
        task = Task(
            prompt="Task for <web_agent_id>", url="http://test.com", relevant_data={"username": "user<web_agent_id>", "nested": {"key": "value<web_agent_id>"}, "list": ["item<web_agent_id>", "other"]}
        )

        # Execute
        prepared_task = task.prepare_for_agent("agent_123")

        # Assertions
        self.assertEqual(prepared_task.prompt, "Task for agent_123")
        self.assertEqual(prepared_task.relevant_data["username"], "useragent_123")
        self.assertEqual(prepared_task.relevant_data["nested"]["key"], "valueagent_123")
        self.assertEqual(prepared_task.relevant_data["list"][0], "itemagent_123")

        # Original task should be unchanged
        self.assertEqual(task.prompt, "Task for <web_agent_id>")


class TestBrowserSpecification(unittest.TestCase):
    """Test cases for BrowserSpecification model."""

    def test_browser_specification_defaults(self):
        """Test browser specification default values."""
        # Execute
        spec = BrowserSpecification()

        # Assertions
        self.assertEqual(spec.viewport_width, 1920)
        self.assertEqual(spec.viewport_height, 1080)
        self.assertEqual(spec.screen_width, 1920)
        self.assertEqual(spec.screen_height, 1080)
        self.assertEqual(spec.device_pixel_ratio, 1.0)
        self.assertEqual(spec.scroll_x, 0)
        self.assertEqual(spec.scroll_y, 0)
        self.assertEqual(spec.browser_x, 0)
        self.assertEqual(spec.browser_y, 0)

    def test_browser_specification_custom_values(self):
        """Test browser specification with custom values."""
        # Execute
        spec = BrowserSpecification(viewport_width=1366, viewport_height=768, screen_width=1366, screen_height=768, device_pixel_ratio=2.0, scroll_x=100, scroll_y=200, browser_x=50, browser_y=75)

        # Assertions
        self.assertEqual(spec.viewport_width, 1366)
        self.assertEqual(spec.viewport_height, 768)
        self.assertEqual(spec.screen_width, 1366)
        self.assertEqual(spec.screen_height, 768)
        self.assertEqual(spec.device_pixel_ratio, 2.0)
        self.assertEqual(spec.scroll_x, 100)
        self.assertEqual(spec.scroll_y, 200)
        self.assertEqual(spec.browser_x, 50)
        self.assertEqual(spec.browser_y, 75)


if __name__ == "__main__":
    # Run tests
    unittest.main()
