"""
Tests for DataExtractionTest: comparison of agent's extracted_data vs expected_answer.
Covers _check_expected_answer, execute_global_test, run_global_tests with extracted_data, and TaskSolution.extracted_data.
"""

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest
from autoppia_iwa.src.evaluation.shared.utils import run_global_tests
from autoppia_iwa.src.web_agents.classes import TaskSolution

# -----------------------------------------------------------------------------
# DataExtractionTest._check_expected_answer (scalar and list)
# -----------------------------------------------------------------------------


def test_data_extraction_test_expected_none_always_passes():
    """When expected_answer is None, _check_expected_answer returns True regardless of extracted_data."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer=None,
        answer_criteria={"field": "value"},
    )
    assert test._check_expected_answer(None) is True
    assert test._check_expected_answer("anything") is True


def test_data_extraction_test_extracted_none_fails_when_expected_set():
    """When expected_answer is set and extracted_data is None, _check_expected_answer returns False."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer="subnet_1",
        answer_criteria={"subnet_name": "subnet_1"},
    )
    assert test._check_expected_answer(None) is False


def test_data_extraction_test_scalar_match_passes():
    """When extracted_data matches expected_answer (scalar), _check_expected_answer returns True."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer="subnet_1",
        answer_criteria={"subnet_name": "subnet_1"},
    )
    assert test._check_expected_answer("subnet_1") is True
    assert test._check_expected_answer("  SUBNET_1  ") is True  # normalized


def test_data_extraction_test_scalar_mismatch_fails():
    """When extracted_data does not match expected_answer, _check_expected_answer returns False."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer="subnet_1",
        answer_criteria={"subnet_name": "subnet_1"},
    )
    assert test._check_expected_answer("subnet_2") is False
    assert test._check_expected_answer("") is False


def test_data_extraction_test_numeric_match_passes():
    """Numeric expected_answer matches extracted_data (normalized to string)."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer=42,
        answer_criteria={"rank": 42},
    )
    assert test._check_expected_answer(42) is True
    assert test._check_expected_answer("42") is True


def test_data_extraction_test_list_expected_comma_separated_extracted_passes():
    """When expected_answer is a list, extracted_data as comma-separated string matches."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer=["a", "b", "c"],
        answer_criteria={},
    )
    assert test._check_expected_answer("a,b,c") is True
    assert test._check_expected_answer("a, b, c") is True


def test_data_extraction_test_list_expected_mismatch_fails():
    """When expected_answer is a list and extracted does not match, returns False."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer=["a", "b"],
        answer_criteria={},
    )
    assert test._check_expected_answer("a,b,c") is False
    assert test._check_expected_answer("a") is False


# -----------------------------------------------------------------------------
# DataExtractionTest.execute_global_test (ignores backend_events, uses extracted_data)
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_data_extraction_test_execute_global_test_uses_extracted_data_only():
    """execute_global_test ignores backend_events and uses only extracted_data."""
    test = DataExtractionTest(
        type="DataExtractionTest",
        expected_answer="correct_value",
        answer_criteria={"key": "correct_value"},
    )
    # backend_events can be empty or anything; only extracted_data matters
    success = await test.execute_global_test(backend_events=[], extracted_data="correct_value")
    assert success is True

    success = await test.execute_global_test(backend_events=[], extracted_data="wrong_value")
    assert success is False


# -----------------------------------------------------------------------------
# run_global_tests with DataExtractionTest and extracted_data
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_global_tests_data_extraction_only_passes_when_match():
    """run_global_tests with only DataExtractionTest and matching extracted_data returns pass."""
    task = Task(
        url="https://example.com",
        prompt="What is the subnet name?",
        tests=[
            DataExtractionTest(
                type="DataExtractionTest",
                expected_answer="alpha_subnet",
                answer_criteria={"subnet_name": "alpha_subnet"},
            )
        ],
    )
    results = await run_global_tests(
        task,
        backend_events=[],
        extracted_data="alpha_subnet",
    )
    assert len(results) == 1
    assert results[0].success is True


@pytest.mark.asyncio
async def test_run_global_tests_data_extraction_only_fails_when_mismatch():
    """run_global_tests with only DataExtractionTest and mismatched extracted_data returns fail."""
    task = Task(
        url="https://example.com",
        prompt="What is the subnet name?",
        tests=[
            DataExtractionTest(
                type="DataExtractionTest",
                expected_answer="alpha_subnet",
                answer_criteria={"subnet_name": "alpha_subnet"},
            )
        ],
    )
    results = await run_global_tests(
        task,
        backend_events=[],
        extracted_data="wrong_subnet",
    )
    assert len(results) == 1
    assert results[0].success is False


@pytest.mark.asyncio
async def test_run_global_tests_data_extraction_extracted_none_fails():
    """run_global_tests with DataExtractionTest and extracted_data=None returns fail when expected is set."""
    task = Task(
        url="https://example.com",
        prompt="What is the subnet name?",
        tests=[
            DataExtractionTest(
                type="DataExtractionTest",
                expected_answer="alpha_subnet",
                answer_criteria={"subnet_name": "alpha_subnet"},
            )
        ],
    )
    results = await run_global_tests(
        task,
        backend_events=[],
        extracted_data=None,
    )
    assert len(results) == 1
    assert results[0].success is False


# -----------------------------------------------------------------------------
# TaskSolution.extracted_data
# -----------------------------------------------------------------------------


def test_task_solution_has_extracted_data_field():
    """TaskSolution accepts and stores extracted_data (for DataExtractionTest path)."""
    solution = TaskSolution(
        task_id="t1",
        actions=[],
        web_agent_id="agent_1",
        extracted_data="subnet_xyz",
    )
    assert solution.extracted_data == "subnet_xyz"


def test_task_solution_extracted_data_default_none():
    """TaskSolution.extracted_data defaults to None."""
    solution = TaskSolution(task_id="t1", actions=[], web_agent_id="agent_1")
    assert solution.extracted_data is None
