"""
Pytest configuration for task generation tests.

This module provides pytest fixtures and configuration for task generation tests.
"""

import tempfile
from collections.abc import Generator

import pytest

from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject


@pytest.fixture
def temp_cache_dir() -> Generator[str, None, None]:
    """Create a temporary directory for cache testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_web_project() -> WebProject:
    """Create a mock WebProject for testing."""
    return WebProject(id="test_project", name="Test Project", urls=["http://test.com"], frontend_url="http://test.com", relevant_data={"key": "value"}, use_cases=[])


@pytest.fixture
def mock_use_case() -> UseCase:
    """Create a mock UseCase for testing."""
    return UseCase(name="Test Use Case", description="Test description", additional_prompt_info="Test additional info")


@pytest.fixture
def test_task() -> Task:
    """Create a test Task for testing."""
    return Task(id="test_task", prompt="Test task", url="http://test.com", web_project_id="test_project")


@pytest.fixture
def task_generation_config() -> TaskGenerationConfig:
    """Create a TaskGenerationConfig for testing."""
    return TaskGenerationConfig(generate_global_tasks=True, prompts_per_use_case=2, num_use_cases=1, final_task_limit=10)


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    from unittest.mock import AsyncMock

    mock_service = AsyncMock()
    mock_service.async_predict.return_value = '["Test task 1", "Test task 2"]'
    return mock_service
