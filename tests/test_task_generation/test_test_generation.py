"""
Unit tests for test generation pipeline components.

This module tests the functionality of test generation including:
- GlobalTestGenerationPipeline
- Test parsing and validation
- Test criteria formatting
- Test execution logic
"""

import json
import unittest
from unittest.mock import AsyncMock

from pydantic import ValidationError

from autoppia_iwa.src.data_generation.application.tasks.globals.tests.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckUrlTest, FindInHtmlTest


class TestGlobalTestGenerationPipeline(unittest.TestCase):
    """Test cases for GlobalTestGenerationPipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm_service = AsyncMock()
        self.pipeline = GlobalTestGenerationPipeline()

    async def test_add_tests_to_tasks_success(self):
        """Test successfully adding tests to tasks."""
        # Setup
        tasks = [Task(prompt="Test task 1", url="http://test.com", web_project_id="test_project"), Task(prompt="Test task 2", url="http://test.com", web_project_id="test_project")]

        # Mock LLM response with test data
        mock_test_data = [{"type": "CheckEventTest", "event_name": "test_event", "event_criteria": {"field1": {"value": "expected_value", "operator": "equals"}}, "reasoning": "Test reasoning"}]

        self.mock_llm_service.async_predict.return_value = json.dumps(mock_test_data)

        # Execute
        result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0].tests), 1)
        self.assertEqual(len(result[1].tests), 1)
        self.assertIsInstance(result[0].tests[0], CheckEventTest)

    async def test_add_tests_to_tasks_empty_list(self):
        """Test adding tests to empty task list."""
        # Execute
        result = await self.pipeline.add_tests_to_tasks([], self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 0)

    async def test_add_tests_to_tasks_llm_failure(self):
        """Test handling LLM service failure."""
        # Setup
        tasks = [Task(prompt="Test task", url="http://test.com", web_project_id="test_project")]
        self.mock_llm_service.async_predict.side_effect = Exception("LLM Error")

        # Execute
        result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 1)
        # No tests added due to error
        self.assertEqual(len(result[0].tests), 0)

    async def test_add_tests_to_tasks_invalid_response(self):
        """Test handling invalid LLM response."""
        # Setup
        tasks = [Task(prompt="Test task", url="http://test.com", web_project_id="test_project")]
        self.mock_llm_service.async_predict.return_value = "Invalid JSON"

        # Execute
        result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 1)
        # No tests added due to invalid response
        self.assertEqual(len(result[0].tests), 0)

    async def test_parse_llm_response_valid_json(self):
        """Test parsing valid JSON response."""
        # Setup
        valid_response = json.dumps([{"type": "CheckEventTest", "event_name": "test_event", "event_criteria": {"field1": {"value": "expected_value"}}, "reasoning": "Test reasoning"}])

        # Execute
        result = await self.pipeline._parse_llm_response(valid_response)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "CheckEventTest")

    async def test_parse_llm_response_markdown_code_block(self):
        """Test parsing response with markdown code blocks."""
        # Setup
        markdown_response = '```json\n[{"type": "CheckEventTest", "event_name": "test_event", "event_criteria": {"field1": {"value": "expected_value"}}, "reasoning": "Test reasoning"}]\n```'

        # Execute
        result = await self.pipeline._parse_llm_response(markdown_response)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "CheckEventTest")

    async def test_parse_llm_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        # Setup
        invalid_response = "Invalid JSON"

        # Execute
        result = await self.pipeline._parse_llm_response(invalid_response)

        # Assertions
        self.assertEqual(len(result), 0)

    async def test_create_tests_from_llm_data_success(self):
        """Test creating test objects from LLM data."""
        # Setup
        llm_data = [
            {"type": "CheckEventTest", "event_name": "test_event", "event_criteria": {"field1": {"value": "expected_value", "operator": "equals"}}, "reasoning": "Test reasoning"},
            {"type": "CheckUrlTest", "expected_url": "http://expected.com", "reasoning": "URL test reasoning"},
        ]

        # Execute
        result = await self.pipeline._create_tests_from_llm_data(llm_data)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], CheckEventTest)
        self.assertIsInstance(result[1], CheckUrlTest)

    async def test_create_tests_from_llm_data_invalid_type(self):
        """Test handling invalid test type."""
        # Setup
        llm_data = [{"type": "InvalidTestType", "event_name": "test_event", "event_criteria": {"field1": {"value": "expected_value"}}, "reasoning": "Test reasoning"}]

        # Execute
        result = await self.pipeline._create_tests_from_llm_data(llm_data)

        # Assertions
        self.assertEqual(len(result), 0)  # Invalid type should be skipped

    async def test_create_tests_from_llm_data_validation_error(self):
        """Test handling validation errors in test creation."""
        # Setup
        llm_data = [
            {
                "type": "CheckEventTest",
                # Missing required fields
                "event_criteria": {"field1": {"value": "expected_value"}},
            }
        ]

        # Execute
        result = await self.pipeline._create_tests_from_llm_data(llm_data)

        # Assertions
        # Validation error should be handled gracefully
        self.assertEqual(len(result), 0)


class TestTestClasses(unittest.TestCase):
    """Test cases for test class validation and functionality."""

    def test_check_event_test_creation(self):
        """Test creating CheckEventTest with valid data."""
        # Setup
        test_data = {
            "type": "CheckEventTest",
            "event_name": "test_event",
            "event_criteria": {"field1": {"value": "expected_value", "operator": "equals"}, "field2": {"value": "another_value"}},
            "reasoning": "Test reasoning",
        }

        # Execute
        test = CheckEventTest(**test_data)

        # Assertions
        self.assertEqual(test.type, "CheckEventTest")
        self.assertEqual(test.event_name, "test_event")
        self.assertEqual(len(test.event_criteria), 2)
        self.assertEqual(test.reasoning, "Test reasoning")

    def test_check_event_test_flat_structure(self):
        """Test CheckEventTest with flat criteria structure."""
        # Setup
        test_data = {
            "type": "CheckEventTest",
            "event_name": "test_event",
            "event_criteria": {
                "field1": {"value": "expected_value", "operator": "equals"},
                "field2": {"value": "another_value"},  # Default operator
            },
            "reasoning": "Test reasoning",
        }

        # Execute
        test = CheckEventTest(**test_data)

        # Assertions
        self.assertEqual(test.event_criteria["field1"]["operator"], "equals")
        self.assertEqual(test.event_criteria["field1"]["value"], "expected_value")
        self.assertEqual(test.event_criteria["field2"]["value"], "another_value")

    def test_check_event_test_nested_structure_error(self):
        """Test CheckEventTest validation with invalid nested structure."""
        # Setup - This should fail validation
        test_data = {
            "type": "CheckEventTest",
            "event_name": "test_event",
            "event_criteria": {
                "field1": {
                    "value": {  # Invalid nested structure
                        "operator": "equals",
                        "value": "expected_value",
                    }
                }
            },
            "reasoning": "Test reasoning",
        }

        # Execute & Assert
        # Should raise validation error
        with self.assertRaises((ValueError, TypeError, ValidationError)):
            CheckEventTest(**test_data)

    def test_check_url_test_creation(self):
        """Test creating CheckUrlTest with valid data."""
        # Setup
        test_data = {"type": "CheckUrlTest", "expected_url": "http://expected.com", "reasoning": "URL test reasoning"}

        # Execute
        test = CheckUrlTest(**test_data)

        # Assertions
        self.assertEqual(test.type, "CheckUrlTest")
        self.assertEqual(test.expected_url, "http://expected.com")
        self.assertEqual(test.reasoning, "URL test reasoning")

    def test_find_in_html_test_creation(self):
        """Test creating FindInHtmlTest with valid data."""
        # Setup
        test_data = {"type": "FindInHtmlTest", "selector": "h1", "expected_text": "Expected Title", "reasoning": "HTML test reasoning"}

        # Execute
        test = FindInHtmlTest(**test_data)

        # Assertions
        self.assertEqual(test.type, "FindInHtmlTest")
        self.assertEqual(test.selector, "h1")
        self.assertEqual(test.expected_text, "Expected Title")
        self.assertEqual(test.reasoning, "HTML test reasoning")

    def test_test_operators_validation(self):
        """Test validation of different operators in event criteria."""
        # Setup
        test_data = {
            "type": "CheckEventTest",
            "event_name": "test_event",
            "event_criteria": {
                "string_field": {"value": "test", "operator": "contains"},
                "numeric_field": {"value": 100, "operator": "greater_than"},
                "list_field": {"value": ["option1", "option2"], "operator": "in_list"},
                "default_field": {"value": "default"},  # Default operator
            },
            "reasoning": "Test reasoning",
        }

        # Execute
        test = CheckEventTest(**test_data)

        # Assertions
        self.assertEqual(test.event_criteria["string_field"]["operator"], "contains")
        self.assertEqual(test.event_criteria["numeric_field"]["operator"], "greater_than")
        self.assertEqual(test.event_criteria["list_field"]["operator"], "in_list")
        self.assertEqual(test.event_criteria["default_field"]["value"], "default")

    def test_test_serialization(self):
        """Test test object serialization."""
        # Setup
        test_data = {"type": "CheckEventTest", "event_name": "test_event", "event_criteria": {"field1": {"value": "expected_value", "operator": "equals"}}, "reasoning": "Test reasoning"}

        test = CheckEventTest(**test_data)

        # Execute
        serialized = test.model_dump()

        # Assertions
        self.assertEqual(serialized["type"], "CheckEventTest")
        self.assertEqual(serialized["event_name"], "test_event")
        self.assertIn("event_criteria", serialized)
        self.assertEqual(serialized["reasoning"], "Test reasoning")


class TestTestGenerationIntegration(unittest.TestCase):
    """Integration tests for test generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm_service = AsyncMock()
        self.pipeline = GlobalTestGenerationPipeline()

    async def test_end_to_end_test_generation(self):
        """Test complete end-to-end test generation process."""
        # Setup
        tasks = [Task(prompt="Buy a red dress for less than $10", url="http://ecommerce.com", web_project_id="test_project")]

        # Mock LLM response
        mock_response = json.dumps(
            [
                {
                    "type": "CheckEventTest",
                    "event_name": "purchase_completed",
                    "event_criteria": {"item_color": {"value": "red", "operator": "equals"}, "price": {"value": 10, "operator": "less_than"}},
                    "reasoning": "Verify red dress purchase under $10",
                }
            ]
        )

        self.mock_llm_service.async_predict.return_value = mock_response

        # Execute
        result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].tests), 1)

        test = result[0].tests[0]
        self.assertIsInstance(test, CheckEventTest)
        self.assertEqual(test.event_name, "purchase_completed")
        self.assertEqual(test.event_criteria["item_color"]["value"], "red")
        self.assertEqual(test.event_criteria["price"]["value"], 10)

    async def test_multiple_tasks_test_generation(self):
        """Test test generation for multiple tasks."""
        # Setup
        tasks = [Task(prompt="Task 1", url="http://test1.com", web_project_id="test_project"), Task(prompt="Task 2", url="http://test2.com", web_project_id="test_project")]

        # Mock LLM responses for each task
        mock_responses = [
            json.dumps([{"type": "CheckEventTest", "event_name": "task1_completed", "event_criteria": {"field1": {"value": "value1"}}, "reasoning": "Task 1 reasoning"}]),
            json.dumps([{"type": "CheckEventTest", "event_name": "task2_completed", "event_criteria": {"field2": {"value": "value2"}}, "reasoning": "Task 2 reasoning"}]),
        ]

        self.mock_llm_service.async_predict.side_effect = mock_responses

        # Execute
        result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0].tests), 1)
        self.assertEqual(len(result[1].tests), 1)
        self.assertEqual(result[0].tests[0].event_name, "task1_completed")
        self.assertEqual(result[1].tests[0].event_name, "task2_completed")

    async def test_mixed_test_types_generation(self):
        """Test generation of mixed test types."""
        # Setup
        tasks = [Task(prompt="Test task", url="http://test.com", web_project_id="test_project")]

        # Mock LLM response with multiple test types
        mock_response = json.dumps(
            [
                {"type": "CheckEventTest", "event_name": "event_test", "event_criteria": {"field1": {"value": "value1"}}, "reasoning": "Event test reasoning"},
                {"type": "CheckUrlTest", "expected_url": "http://expected.com", "reasoning": "URL test reasoning"},
                {"type": "FindInHtmlTest", "selector": "h1", "expected_text": "Expected Title", "reasoning": "HTML test reasoning"},
            ]
        )

        self.mock_llm_service.async_predict.return_value = mock_response

        # Execute
        result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].tests), 3)

        # Check test types
        test_types = [test.type for test in result[0].tests]
        self.assertIn("CheckEventTest", test_types)
        self.assertIn("CheckUrlTest", test_types)
        self.assertIn("FindInHtmlTest", test_types)


if __name__ == "__main__":
    # Run tests
    unittest.main()
