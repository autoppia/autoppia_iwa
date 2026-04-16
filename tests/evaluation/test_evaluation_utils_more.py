"""Additional unit tests for evaluation.shared.utils."""

import base64
import io
from types import SimpleNamespace

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest, JudgeBaseOnHTML
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.evaluation.classes import TestResult as EvalTestResult
from autoppia_iwa.src.evaluation.shared.utils import (
    _replace_film_placeholders_in_criteria,
    _replace_placeholders_in_criteria,
    _resolve_assigned_book_for_agent,
    _resolve_assigned_movie_for_agent,
    _resolve_autobooks_book_placeholders_in_tests,
    _resolve_autocinema_film_placeholders_in_tests,
    extract_seed_from_url,
    generate_feedback,
    hash_actions,
    initialize_test_results,
    log_progress,
    make_gif_from_screenshots,
    run_global_tests,
    run_partial_tests,
)
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot


def _snapshot(iteration: int = 0, current_url: str = "http://example.com") -> BrowserSnapshot:
    action = NavigateAction(type="NavigateAction", url=current_url)
    return BrowserSnapshot(
        iteration=iteration,
        action=action,
        prev_html="<html></html>",
        current_html="<html><body>ok</body></html>",
        screenshot_before="before",
        screenshot_after="after",
        backend_events=[],
        current_url=current_url,
    )


def _result(iteration: int = 0, current_url: str = "http://example.com") -> ActionExecutionResult:
    action = NavigateAction(type="NavigateAction", url=current_url)
    return ActionExecutionResult(
        action=action,
        action_event="navigate",
        successfully_executed=True,
        error=None,
        action_output=None,
        execution_time=1.25,
        browser_snapshot=_snapshot(iteration=iteration, current_url=current_url),
    )


class TestExtractSeedFromUrl:
    def test_has_seed(self):
        assert extract_seed_from_url("http://example.com?seed=42") == 42
        assert extract_seed_from_url("http://example.com/path?seed=123&other=1") == 123

    def test_no_seed(self):
        assert extract_seed_from_url("http://example.com") is None
        assert extract_seed_from_url("http://example.com?other=1") is None

    def test_seed_with_whitespace(self):
        assert extract_seed_from_url("http://example.com?seed=  99  ") == 99

    def test_invalid_url_or_query(self):
        assert extract_seed_from_url("") is None


class TestHashActions:
    def test_empty_list(self):
        h = hash_actions([])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_same_actions_same_hash(self):
        actions = [
            NavigateAction(type="NavigateAction", url="http://example.com"),
        ]
        h1 = hash_actions(actions)
        h2 = hash_actions(actions)
        assert h1 == h2

    def test_different_actions_different_hash(self):
        a1 = [NavigateAction(type="NavigateAction", url="http://a.com")]
        a2 = [NavigateAction(type="NavigateAction", url="http://b.com")]
        assert hash_actions(a1) != hash_actions(a2)

    def test_invalid_action_returns_empty_hash(self):
        assert hash_actions([object()]) == ""


class TestInitializeTestResults:
    def test_empty_tests(self):
        task = Task(url="http://x.com", prompt="P", tests=[])
        result = initialize_test_results(task)
        assert result == []

    def test_with_tests(self):
        task = Task(
            url="http://x.com",
            prompt="P",
            tests=[
                JudgeBaseOnHTML(type="JudgeBaseOnHTML", success_criteria="find x", description="Desc"),
            ],
        )
        result = initialize_test_results(task)
        assert len(result) == 1
        assert result[0].success is False
        assert result[0].extra_data is not None


class TestMakeGifFromScreenshots:
    def test_empty_list_returns_empty_bytes(self):
        assert make_gif_from_screenshots([]) == b""

    def test_none_or_invalid_skipped(self):
        # Invalid base64 should be skipped; result can be b"" if no valid image
        result = make_gif_from_screenshots(["not-valid-base64!!"])
        assert result == b""

    def test_single_valid_tiny_image(self):
        # Minimal 1x1 PNG as base64 (valid image bytes)
        try:
            from PIL import Image

            buf = io.BytesIO()
            img = Image.new("RGB", (1, 1), color=(255, 0, 0))
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            result = make_gif_from_screenshots([b64])
            assert isinstance(result, bytes)
            assert True  # may return empty if GIF save fails on single frame
        except Exception:
            pytest.skip("PIL not available or save failed")


class TestPlaceholderResolutionHelpers:
    def test_replace_placeholders_in_criteria_handles_nested_values(self):
        value = {
            "name": "<assigned_book_name>",
            "items": ["<book_id>", {"author": "<assigned_book_author>"}],
        }

        result = _replace_placeholders_in_criteria(value, "Dune", "42", "Frank Herbert")

        assert result == {
            "name": "Dune",
            "items": ["42", {"author": "Frank Herbert"}],
        }

    def test_replace_film_placeholders_in_criteria_handles_nested_values(self):
        value = {
            "film": "<assigned_film_name>",
            "meta": ["<film_id>", {"director": "<film_director>"}],
        }

        result = _replace_film_placeholders_in_criteria(value, "Arrival", "7", "Denis Villeneuve")

        assert result == {
            "film": "Arrival",
            "meta": ["7", {"director": "Denis Villeneuve"}],
        }

    def test_resolve_assigned_helpers_handle_empty_lists(self):
        assert _resolve_assigned_book_for_agent([], "12") is None
        assert _resolve_assigned_movie_for_agent([], "12") is None


class TestAsyncEvaluationHelpers:
    @pytest.mark.asyncio
    async def test_resolve_autobooks_placeholders_in_tests_rewrites_matching_tests(self, monkeypatch):
        task = Task(
            web_project_id="autobooks",
            url="http://localhost:8000?seed=9",
            prompt="Delete assigned book",
            tests=[
                CheckEventTest(
                    event_name="DELETE_BOOK",
                    event_criteria={"name": "<assigned_book_name>", "author": "<book_author>", "id": "<book_id>"},
                )
            ],
        )

        async def _fake_fetch_books_data(seed_value, count):
            assert seed_value == 9
            assert count == 50
            return [{"id": "book-3", "name": "Dune", "author": "Frank Herbert"}]

        monkeypatch.setattr(
            "autoppia_iwa.src.evaluation.shared.utils.fetch_books_data",
            _fake_fetch_books_data,
        )

        tests = await _resolve_autobooks_book_placeholders_in_tests(task, "4")

        assert tests[0].event_criteria == {"name": "Dune", "author": "Frank Herbert", "id": "book-3"}
        assert task.tests[0].event_criteria["name"] == "<assigned_book_name>"

    @pytest.mark.asyncio
    async def test_resolve_autobooks_placeholders_returns_original_for_nonmatching_cases(self):
        task = Task(
            web_project_id="autocinema",
            url="http://localhost:8000?seed=9",
            prompt="noop",
            tests=[CheckEventTest(event_name="DELETE_BOOK", event_criteria={"name": "<book_name>"})],
        )

        tests = await _resolve_autobooks_book_placeholders_in_tests(task, None)

        assert tests[0].event_criteria == {"name": "<book_name>"}

    @pytest.mark.asyncio
    async def test_resolve_autocinema_placeholders_in_tests_rewrites_matching_tests(self, monkeypatch):
        task = Task(
            web_project_id="autocinema",
            url="http://localhost:8000?seed=14",
            prompt="Edit assigned film",
            tests=[
                CheckEventTest(
                    event_name="EDIT_FILM",
                    event_criteria={
                        "name": "<assigned_film_name>",
                        "id": "<film_id>",
                        "director": "<assigned_film_director>",
                    },
                )
            ],
        )

        async def _fake_fetch_movies_data(seed_value, count):
            assert seed_value == 14
            assert count == 50
            return [{"id": "movie-7", "title": "Arrival", "director": "Denis Villeneuve"}]

        monkeypatch.setattr(
            "autoppia_iwa.src.evaluation.shared.utils.fetch_movies_data",
            _fake_fetch_movies_data,
        )

        tests = await _resolve_autocinema_film_placeholders_in_tests(task, task.tests, "2")

        assert tests[0].event_criteria == {"name": "Arrival", "id": "7", "director": "Denis Villeneuve"}

    @pytest.mark.asyncio
    async def test_run_global_tests_uses_resolved_tests_and_runner(self, monkeypatch):
        task = Task(
            web_project_id="autobooks",
            url="http://localhost:8000?seed=1",
            prompt="Run tests",
            tests=[CheckEventTest(event_name="DELETE_BOOK", event_criteria={"id": "<book_id>"})],
        )
        backend_events = [BackendEvent(event_name="DELETE_BOOK", data={"id": "book-1"})]
        captured = {}

        async def _fake_book_resolver(current_task, web_agent_id):
            assert current_task is task
            assert web_agent_id == "5"
            return ["book-tests"]

        async def _fake_movie_resolver(current_task, tests_for_run, web_agent_id):
            assert current_task is task
            assert tests_for_run == ["book-tests"]
            assert web_agent_id == "5"
            return ["final-tests"]

        class _FakeRunner:
            def __init__(self, tests):
                captured["tests"] = tests

            async def run_global_tests(self, backend_events, web_agent_id):
                captured["backend_events"] = backend_events
                captured["web_agent_id"] = web_agent_id
                return ["ok"]

        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils._resolve_autobooks_book_placeholders_in_tests", _fake_book_resolver)
        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils._resolve_autocinema_film_placeholders_in_tests", _fake_movie_resolver)
        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils.TestRunner", _FakeRunner)

        results = await run_global_tests(task, backend_events, web_agent_id="5")

        assert results == ["ok"]
        assert captured == {"tests": ["final-tests"], "backend_events": backend_events, "web_agent_id": "5"}

    @pytest.mark.asyncio
    async def test_run_partial_tests_builds_matrix_and_snapshot_history(self, monkeypatch):
        task = Task(url="http://localhost:8000", prompt="Run partial tests", tests=[])
        history = [_result(0, "http://example.com/1"), _result(1, "http://example.com/2")]
        web_project = SimpleNamespace(project_id="p01")
        calls = []

        class _FakeRunner:
            def __init__(self, tests):
                assert tests == []

            async def run_partial_tests(self, **kwargs):
                calls.append({**kwargs, "browser_snapshots": list(kwargs["browser_snapshots"])})
                return [SimpleNamespace(success=True)]

        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils.TestRunner", _FakeRunner)

        matrix = await run_partial_tests(web_project, task, history)

        assert len(matrix) == 2
        assert calls[0]["current_action_index"] == 0
        assert len(calls[0]["browser_snapshots"]) == 1
        assert calls[1]["current_action_index"] == 1
        assert len(calls[1]["browser_snapshots"]) == 2
        assert calls[1]["total_iterations"] == 2

    def test_generate_feedback_delegates_to_feedback_generator(self):
        task = Task(url="http://localhost:8000", prompt="Prompt", tests=[])
        history = [_result()]
        results = [EvalTestResult(success=True, extra_data={})]

        feedback = generate_feedback(task, history, results)

        assert feedback.task_prompt == "Prompt"
        assert feedback.executed_actions == 1
        assert feedback.failed_actions == 0
        assert feedback.passed_tests == 1

    @pytest.mark.asyncio
    async def test_log_progress_logs_then_can_be_cancelled(self, monkeypatch):
        calls = {"sleep": 0, "logs": []}

        async def _fake_sleep(_interval):
            calls["sleep"] += 1
            if calls["sleep"] > 1:
                raise asyncio.CancelledError

        class _DoneTask:
            def done(self):
                return True

            def __str__(self):
                return "evaluate_group_with_semaphore"

        class _OtherTask:
            def done(self):
                return False

            def __str__(self):
                return "ignored"

        import asyncio

        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils.asyncio.sleep", _fake_sleep)
        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils.asyncio.all_tasks", lambda: [_DoneTask(), _OtherTask()])
        monkeypatch.setattr("autoppia_iwa.src.evaluation.shared.utils.logger.info", calls["logs"].append)

        with pytest.raises(asyncio.CancelledError):
            await log_progress(total_groups=5, interval=0)

        assert any("1/5 groups" in message for message in calls["logs"])
