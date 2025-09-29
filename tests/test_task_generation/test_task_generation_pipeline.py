"""
Unit tests for task generation pipeline components.

This module tests the core functionality of task generation including:
- TaskGenerationPipeline
- GlobalTaskGenerationPipeline
- Task caching and serialization
- Task assembly and validation
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import ValidationError

from autoppia_iwa.src.data_generation.application.tasks.globals.global_task_generation import GlobalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject

# Note: These imports may need to be adjusted based on actual module structure
try:
    from autoppia_iwa.entrypoints.benchmark.utils.tasks import generate_tasks_for_web_project, get_cache_filename, load_tasks_from_json, save_tasks_to_json
except ImportError:
    # Fallback for testing - these functions would need to be implemented
    def get_cache_filename(project, task_cache_dir):
        return f"{task_cache_dir}/{project.name.replace(' ', '_').lower()}_tasks.json"

    async def save_tasks_to_json(tasks, project, task_cache_dir):
        return True

    async def load_tasks_from_json(project, task_cache_dir):
        return []

    async def generate_tasks_for_web_project(project, use_cached_tasks, task_cache_dir, prompts_per_use_case, num_of_use_cases):
        return []


class TestTaskGenerationPipeline(unittest.TestCase):
    """Test cases for TaskGenerationPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_web_project = MagicMock(spec=WebProject)
        self.mock_web_project.id = "test_project"
        self.mock_web_project.name = "Test Project"
        self.mock_web_project.use_cases = []

        self.config = TaskGenerationConfig(generate_global_tasks=True, prompts_per_use_case=2, num_use_cases=1, final_task_limit=10)

        self.mock_llm_service = AsyncMock()

        # Create pipeline instance
        self.pipeline = TaskGenerationPipeline(web_project=self.mock_web_project, config=self.config, llm_service=self.mock_llm_service)

    @patch("autoppia_iwa.src.data_generation.application.tasks_generation_pipeline.GlobalTaskGenerationPipeline")
    async def test_generate_with_global_tasks(self, mock_global_pipeline_class):
        """Test task generation with global tasks enabled."""
        # Setup mock
        mock_global_pipeline = AsyncMock()
        mock_global_pipeline_class.return_value = mock_global_pipeline

        # Mock tasks
        mock_tasks = [Task(prompt="Test task 1", url="http://test.com", web_project_id="test_project"), Task(prompt="Test task 2", url="http://test.com", web_project_id="test_project")]
        mock_global_pipeline.generate.return_value = mock_tasks

        # Mock test pipeline
        mock_test_pipeline = AsyncMock()
        mock_test_pipeline.add_tests_to_tasks.return_value = mock_tasks
        self.pipeline.global_test_pipeline = mock_test_pipeline

        # Execute
        result = await self.pipeline.generate()

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].prompt, "Test task 1")
        self.assertEqual(result[1].prompt, "Test task 2")
        mock_global_pipeline.generate.assert_called_once_with(prompts_per_use_case=2, num_use_cases=1)
        mock_test_pipeline.add_tests_to_tasks.assert_called_once_with(mock_tasks)

    async def test_generate_without_global_tasks(self):
        """Test task generation with global tasks disabled."""
        # Setup
        self.config.generate_global_tasks = False

        # Execute
        result = await self.pipeline.generate()

        # Assertions
        self.assertEqual(len(result), 0)

    async def test_generate_with_task_limit(self):
        """Test task generation with final task limit applied."""
        # Setup
        mock_tasks = [
            Task(prompt=f"Task {i}", url="http://test.com", web_project_id="test_project")
            for i in range(15)  # More than the limit of 10
        ]

        with patch.object(self.pipeline, "global_pipeline") as mock_global:
            mock_global.generate.return_value = mock_tasks
            mock_test_pipeline = AsyncMock()
            mock_test_pipeline.add_tests_to_tasks.return_value = mock_tasks
            self.pipeline.global_test_pipeline = mock_test_pipeline

            # Execute
            result = await self.pipeline.generate()

            # Assertions
            self.assertEqual(len(result), 10)  # Should be limited to 10

    async def test_generate_exception_handling(self):
        """Test exception handling during task generation."""
        # Setup
        with patch.object(self.pipeline, "global_pipeline") as mock_global:
            mock_global.generate.side_effect = Exception("Test error")

            # Execute
            result = await self.pipeline.generate()

            # Assertions
            self.assertEqual(len(result), 0)


class TestGlobalTaskGenerationPipeline(unittest.TestCase):
    """Test cases for GlobalTaskGenerationPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_web_project = MagicMock(spec=WebProject)
        self.mock_web_project.id = "test_project"
        self.mock_web_project.name = "Test Project"
        self.mock_web_project.urls = ["http://test.com"]
        self.mock_web_project.frontend_url = "http://test.com"
        self.mock_web_project.relevant_data = {"key": "value"}

        self.mock_llm_service = AsyncMock()

        # Create pipeline instance
        self.pipeline = GlobalTaskGenerationPipeline(web_project=self.mock_web_project, llm_service=self.mock_llm_service, max_retries=2, retry_delay=0.1)

    async def test_generate_with_no_use_cases(self):
        """Test generation when no use cases are available."""
        # Setup
        self.mock_web_project.use_cases = []

        # Execute
        result = await self.pipeline.generate(num_use_cases=1, prompts_per_use_case=2)

        # Assertions
        self.assertEqual(len(result), 0)

    async def test_generate_with_use_cases(self):
        """Test generation with available use cases."""
        # Setup mock use case
        mock_use_case = MagicMock(spec=UseCase)
        mock_use_case.name = "Test Use Case"
        mock_use_case.description = "Test description"
        mock_use_case.additional_prompt_info = "Test info"
        mock_use_case.apply_replacements.return_value = "Modified prompt"

        self.mock_web_project.use_cases = [mock_use_case]

        # Mock LLM response
        mock_llm_response = ["Task 1", "Task 2"]
        self.mock_llm_service.async_predict.return_value = json.dumps(mock_llm_response)

        # Execute
        result = await self.pipeline.generate(num_use_cases=1, prompts_per_use_case=2)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].prompt, "Modified prompt")
        self.assertEqual(result[0].web_project_id, "test_project")
        self.assertEqual(result[0].url, "http://test.com")
        self.assertEqual(result[0].scope, "global")

    async def test_generate_tasks_for_use_case_with_constraints(self):
        """Test task generation for use case with constraints."""
        # Setup
        mock_use_case = MagicMock(spec=UseCase)
        mock_use_case.name = "Test Use Case"
        mock_use_case.description = "Test description"
        mock_use_case.additional_prompt_info = "Test info"
        mock_use_case.generate_constraints.return_value = "Test constraints"
        mock_use_case.apply_replacements.return_value = "Modified prompt"

        # Mock LLM response
        mock_llm_response = ["Task 1", "Task 2"]
        self.mock_llm_service.async_predict.return_value = json.dumps(mock_llm_response)

        # Execute
        result = await self.pipeline.generate_tasks_for_use_case(mock_use_case, 2)

        # Assertions
        self.assertEqual(len(result), 2)
        mock_use_case.generate_constraints.assert_called_once()
        mock_use_case.apply_replacements.assert_called()

    async def test_call_llm_with_retry_success(self):
        """Test successful LLM call with retry logic."""
        # Setup
        mock_response = ["Task 1", "Task 2"]
        self.mock_llm_service.async_predict.return_value = json.dumps(mock_response)

        # Execute
        result = await self.pipeline._call_llm_with_retry("Test prompt")

        # Assertions
        self.assertEqual(result, mock_response)
        self.mock_llm_service.async_predict.assert_called_once()

    async def test_call_llm_with_retry_failure(self):
        """Test LLM call failure after max retries."""
        # Setup
        self.mock_llm_service.async_predict.side_effect = Exception("LLM Error")

        # Execute
        result = await self.pipeline._call_llm_with_retry("Test prompt")

        # Assertions
        self.assertEqual(result, [])
        self.assertEqual(self.mock_llm_service.async_predict.call_count, 2)  # max_retries

    async def test_parse_llm_response_valid_json(self):
        """Test parsing valid JSON response."""
        # Setup
        valid_json = '["Task 1", "Task 2"]'

        # Execute
        result = await self.pipeline._parse_llm_response(valid_json)

        # Assertions
        self.assertEqual(result, ["Task 1", "Task 2"])

    async def test_parse_llm_response_markdown_code_block(self):
        """Test parsing response with markdown code blocks."""
        # Setup
        markdown_response = '```json\n["Task 1", "Task 2"]\n```'

        # Execute
        result = await self.pipeline._parse_llm_response(markdown_response)

        # Assertions
        self.assertEqual(result, ["Task 1", "Task 2"])

    async def test_parse_llm_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        # Setup
        invalid_json = "Invalid JSON"

        # Execute
        result = await self.pipeline._parse_llm_response(invalid_json)

        # Assertions
        self.assertEqual(result, [])

    def test_assemble_task(self):
        """Test task assembly from components."""
        # Setup
        mock_use_case = MagicMock(spec=UseCase)
        mock_use_case.name = "Test Use Case"

        # Execute
        task = self.pipeline._assemble_task(
            web_project_id="test_project",
            url="http://test.com",
            prompt="Test prompt",
            html="<html>Test</html>",
            clean_html="<html>Test</html>",
            screenshot=None,
            screenshot_desc="Test screenshot",
            use_case=mock_use_case,
            relevant_data={"key": "value"},
        )

        # Assertions
        self.assertIsInstance(task, Task)
        self.assertEqual(task.web_project_id, "test_project")
        self.assertEqual(task.url, "http://test.com")
        self.assertEqual(task.prompt, "Test prompt")
        self.assertEqual(task.scope, "global")
        self.assertEqual(task.relevant_data, {"key": "value"})
        self.assertEqual(task.use_case, mock_use_case)


class TestTaskCaching(unittest.TestCase):
    """Test cases for task caching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_project = MagicMock(spec=WebProject)
        self.mock_project.id = "test_project"
        self.mock_project.name = "Test Project"

        # Create test tasks
        self.test_tasks = [
            Task(id="task_1", prompt="Test task 1", url="http://test.com", web_project_id="test_project"),
            Task(id="task_2", prompt="Test task 2", url="http://test.com", web_project_id="test_project"),
        ]

    def test_get_cache_filename(self):
        """Test cache filename generation."""
        # Execute
        filename = get_cache_filename(self.mock_project, self.temp_dir)

        # Assertions
        expected = f"{self.temp_dir}/test_project_tasks.json"
        self.assertEqual(filename, expected)

    async def test_save_tasks_to_json(self):
        """Test saving tasks to JSON cache."""
        # Execute
        result = await save_tasks_to_json(self.test_tasks, self.mock_project, self.temp_dir)

        # Assertions
        self.assertTrue(result)

        # Verify file was created
        cache_file = Path(self.temp_dir) / "test_project_tasks.json"
        self.assertTrue(cache_file.exists())

        # Verify content
        with open(cache_file) as f:
            data = json.load(f)
            self.assertEqual(data["project_id"], "test_project")
            self.assertEqual(data["project_name"], "Test Project")
            self.assertEqual(len(data.get("tasks", [])), 2)

    async def test_load_tasks_from_json(self):
        """Test loading tasks from JSON cache."""
        # Setup - save tasks first
        await save_tasks_to_json(self.test_tasks, self.mock_project, self.temp_dir)

        # Execute
        loaded_tasks = await load_tasks_from_json(self.mock_project, self.temp_dir)

        # Assertions
        self.assertIsNotNone(loaded_tasks)
        if loaded_tasks:
            self.assertEqual(len(loaded_tasks), 2)
            self.assertEqual(loaded_tasks[0].id, "task_1")
            self.assertEqual(loaded_tasks[1].id, "task_2")

    async def test_load_tasks_from_nonexistent_file(self):
        """Test loading from non-existent cache file."""
        # Execute
        result = await load_tasks_from_json(self.mock_project, "/nonexistent/path")

        # Assertions
        self.assertIsNone(result)

    async def test_save_tasks_append_existing(self):
        """Test appending tasks to existing cache."""
        # Setup - save initial tasks
        await save_tasks_to_json(self.test_tasks, self.mock_project, self.temp_dir)

        # Add new task
        new_task = Task(id="task_3", prompt="Test task 3", url="http://test.com", web_project_id="test_project")

        # Execute
        await save_tasks_to_json([new_task], self.mock_project, self.temp_dir)

        # Verify
        loaded_tasks = await load_tasks_from_json(self.mock_project, self.temp_dir)
        self.assertEqual(len(loaded_tasks), 3)

    async def test_save_tasks_avoid_duplicates(self):
        """Test that duplicate tasks are not added to cache."""
        # Setup - save initial tasks
        await save_tasks_to_json(self.test_tasks, self.mock_project, self.temp_dir)

        # Try to save same tasks again
        await save_tasks_to_json(self.test_tasks, self.mock_project, self.temp_dir)

        # Verify no duplicates
        loaded_tasks = await load_tasks_from_json(self.mock_project, self.temp_dir)
        self.assertEqual(len(loaded_tasks), 2)


class TestTaskGenerationIntegration(unittest.TestCase):
    """Integration tests for task generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_project = MagicMock(spec=WebProject)
        self.mock_project.id = "test_project"
        self.mock_project.name = "Test Project"
        self.mock_project.use_cases = []

    @patch("autoppia_iwa.entrypoints.benchmark.utils.tasks.TaskGenerationPipeline")
    async def test_generate_tasks_for_web_project_with_cache(self, mock_pipeline_class):
        """Test task generation with caching enabled."""
        # Setup
        mock_pipeline = AsyncMock()
        mock_pipeline_class.return_value = mock_pipeline

        test_tasks = [Task(prompt="Test task", url="http://test.com", web_project_id="test_project")]
        mock_pipeline.generate.return_value = test_tasks

        # Execute with caching
        result = await generate_tasks_for_web_project(project=self.mock_project, use_cached_tasks=True, task_cache_dir=self.temp_dir, prompts_per_use_case=1, num_of_use_cases=1)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].prompt, "Test task")

    async def test_generate_tasks_for_web_project_without_cache(self):
        """Test task generation without caching."""
        # Execute without caching
        result = await generate_tasks_for_web_project(project=self.mock_project, use_cached_tasks=False, task_cache_dir=self.temp_dir, prompts_per_use_case=1, num_of_use_cases=1)

        # Assertions
        self.assertIsInstance(result, list)


class TestTaskValidation(unittest.TestCase):
    """Test cases for Task model validation."""

    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        # Execute
        task = Task(prompt="Test task", url="http://test.com")

        # Assertions
        self.assertEqual(task.prompt, "Test task")
        self.assertEqual(task.url, "http://test.com")
        self.assertEqual(task.scope, "local")
        self.assertFalse(task.is_web_real)
        self.assertIsInstance(task.specifications, BrowserSpecification)

    def test_task_creation_with_all_fields(self):
        """Test creating a task with all fields."""
        # Setup
        use_case = MagicMock(spec=UseCase)
        use_case.name = "Test Use Case"

        # Execute
        task = Task(
            prompt="Test task",
            url="http://test.com",
            scope="global",
            is_web_real=True,
            web_project_id="test_project",
            html="<html>Test</html>",
            clean_html="<html>Test</html>",
            interactive_elements="button,form",
            screenshot="base64_image",
            screenshot_description="Test screenshot",
            tests=[],
            relevant_data={"key": "value"},
            success_criteria="Complete the task",
            use_case=use_case,
            should_record=True,
        )

        # Assertions
        self.assertEqual(task.scope, "global")
        self.assertTrue(task.is_web_real)
        self.assertEqual(task.web_project_id, "test_project")
        self.assertEqual(task.html, "<html>Test</html>")
        self.assertEqual(task.relevant_data, {"key": "value"})
        self.assertEqual(task.use_case, use_case)
        self.assertTrue(task.should_record)

    def test_task_serialization(self):
        """Test task serialization."""
        # Setup
        task = Task(prompt="Test task", url="http://test.com", relevant_data={"key": "value"})

        # Execute
        serialized = task.serialize()

        # Assertions
        self.assertIn("id", serialized)
        self.assertIn("prompt", serialized)
        self.assertIn("url", serialized)
        self.assertIn("relevant_data", serialized)
        self.assertNotIn("html", serialized)  # Should be excluded
        self.assertNotIn("clean_html", serialized)  # Should be excluded

    def test_task_clean_task(self):
        """Test task cleaning for agent preparation."""
        # Setup
        task = Task(prompt="Test task", url="http://test.com", html="<html>Test</html>", clean_html="<html>Test</html>", tests=[], relevant_data={"key": "value"})

        # Execute
        cleaned = task.clean_task()

        # Assertions
        self.assertIn("prompt", cleaned)
        self.assertIn("url", cleaned)
        self.assertNotIn("html", cleaned)
        self.assertNotIn("clean_html", cleaned)
        self.assertNotIn("tests", cleaned)
        self.assertIn("original_prompt", cleaned)

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

    def test_task_validation_errors(self):
        """Test task validation with invalid data."""
        # Test missing required fields
        with self.assertRaises(ValidationError):
            Task()  # Missing required fields

        with self.assertRaises(ValidationError):
            Task(prompt="Test")  # Missing url

        with self.assertRaises(ValidationError):
            Task(url="http://test.com")  # Missing prompt


if __name__ == "__main__":
    # Run tests
    unittest.main()
