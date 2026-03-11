"""Unit tests for shared.visualizator (SubnetVisualizer)."""

import datetime
from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest

from autoppia_iwa.src.shared.visualizator import (
    SubnetVisualizer,
    visualize_evaluation,
    visualize_list_of_evaluations,
    visualize_summary,
    visualize_task,
)


class TestMakeJsonSerializable:
    """Tests for SubnetVisualizer._make_json_serializable (static)."""

    def test_datetime(self):
        dt = datetime.datetime(2025, 6, 15, 10, 30, 0)
        assert SubnetVisualizer._make_json_serializable(dt) == "2025-06-15T10:30:00"

    def test_date(self):
        d = date(2025, 6, 15)
        assert SubnetVisualizer._make_json_serializable(d) == "2025-06-15"

    def test_time(self):
        t = time(14, 30, 0)
        assert SubnetVisualizer._make_json_serializable(t) == "14:30:00"

    def test_dict_recursive(self):
        obj = {"a": date(2025, 1, 1), "b": [datetime.datetime(2025, 1, 1, 12, 0)]}
        result = SubnetVisualizer._make_json_serializable(obj)
        assert result["a"] == "2025-01-01"
        assert result["b"][0] == "2025-01-01T12:00:00"

    def test_list_recursive(self):
        obj = [date(2025, 1, 1), "x"]
        result = SubnetVisualizer._make_json_serializable(obj)
        assert result[0] == "2025-01-01"
        assert result[1] == "x"

    def test_tuple_treated_as_list(self):
        obj = (1, 2)
        result = SubnetVisualizer._make_json_serializable(obj)
        assert result == [1, 2]

    def test_scalar_passthrough(self):
        assert SubnetVisualizer._make_json_serializable(42) == 42
        assert SubnetVisualizer._make_json_serializable("hello") == "hello"
        assert SubnetVisualizer._make_json_serializable(True) is True


class TestSubnetVisualizerInit:
    def test_init_no_log_directory(self):
        v = SubnetVisualizer(log_directory=None)
        assert v.log_directory is None
        assert v.console is not None

    def test_init_with_log_directory(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        v = SubnetVisualizer(log_directory=log_dir)
        assert v.log_directory == log_dir
        assert (tmp_path / "logs").exists()


class TestFormatActionDetails:
    """Tests for _format_action_details."""

    def test_action_with_model_dump(self):
        v = SubnetVisualizer()
        action = MagicMock()
        action.model_dump.return_value = {"type": "click", "x": 10, "y": 20}
        result = v._format_action_details(action)
        assert "x=10" in result and "y=20" in result
        assert "type" not in result

    def test_action_with_dict(self):
        v = SubnetVisualizer()

        class SimpleAction:
            pass

        action = SimpleAction()
        action.x = 5
        action.y = 10
        result = v._format_action_details(action)
        assert "5" in result and "10" in result

    def test_action_fallback_str(self):
        v = SubnetVisualizer()
        action = object()
        result = v._format_action_details(action)
        assert isinstance(result, str)


class TestGetDetailedTestDescriptionAndAttributes:
    """Tests for _get_detailed_test_description_and_attributes."""

    def test_check_url_test_with_url(self):
        v = SubnetVisualizer()
        test = MagicMock()
        test.__class__.__name__ = "CheckUrlTest"
        test.url = "/about/"
        test.expected_url = None
        test.url_pattern = None
        desc, attrs = v._get_detailed_test_description_and_attributes(test)
        assert "about" in desc
        assert "url" in attrs

    def test_find_in_html_test(self):
        v = SubnetVisualizer()
        test = MagicMock()
        test.__class__.__name__ = "FindInHtmlTest"
        test.content = "expected text"
        desc, attrs = v._get_detailed_test_description_and_attributes(test)
        assert "expected text" in desc

    def test_generic_fallback_description(self):
        v = SubnetVisualizer()
        test = MagicMock()
        test.__class__.__name__ = "UnknownTest"
        test.description = "My description"
        del test.url
        del test.content
        del test.success_criteria
        desc, _ = v._get_detailed_test_description_and_attributes(test)
        assert "description" in desc.lower() or "My description" in desc

    def test_opinion_based_html_test_success_criteria(self):
        v = SubnetVisualizer()
        test = MagicMock()
        test.__class__.__name__ = "OpinionBasedHTMLTest"
        test.success_criteria = "Page must show confirmation"
        test.query = None
        desc, attrs = v._get_detailed_test_description_and_attributes(test)
        assert "confirmation" in desc
        assert "success_criteria" in attrs

    def test_opinion_based_html_test_long_criteria_truncated(self):
        v = SubnetVisualizer()
        test = MagicMock()
        test.__class__.__name__ = "JudgeBaseOnHTML"
        test.success_criteria = "A" * 70
        test.query = None
        desc, _ = v._get_detailed_test_description_and_attributes(test)
        assert "..." in desc

    def test_check_event_test_event_name(self):
        v = SubnetVisualizer()
        test = MagicMock()
        test.__class__.__name__ = "CheckEventTest"
        test.event_name = "FILM_DETAIL"
        desc, attrs = v._get_detailed_test_description_and_attributes(test)
        assert "FILM_DETAIL" in desc
        assert "event_name" in attrs


class TestShowTaskWithTests:
    """Tests for show_task_with_tests (no console output)."""

    def test_show_task_with_tests_minimal_task(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "task-1"
        task.prompt = "Do something"
        task.url = "http://example.com"
        task.tests = []
        with patch.object(v.console, "print"):
            v.show_task_with_tests(task)

    def test_show_task_with_tests_and_tests_with_model_dump(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        test = MagicMock()
        test.model_dump.return_value = {"type": "CheckUrlTest", "url": "/ok"}
        task.tests = [test]
        with patch.object(v.console, "print"):
            v.show_task_with_tests(task)

    def test_show_task_with_tests_fallback_dict(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        test = MagicMock()
        del test.model_dump
        test.dict.return_value = {"type": "Test"}
        task.tests = [test]
        with patch.object(v.console, "print"):
            v.show_task_with_tests(task)


class TestShowFullEvaluation:
    """Tests for show_full_evaluation (mocked console)."""

    def test_show_full_evaluation_no_actions(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        task.tests = []
        with patch.object(v.console, "print"):
            v.show_full_evaluation("agent-1", "validator-1", task, [], [], evaluation_result=None, feedback=None)

    def test_show_full_evaluation_with_evaluation_result_dict(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        task.tests = []
        eval_result = {"final_score": 0.75}
        with patch.object(v.console, "print"):
            v.show_full_evaluation("agent-1", "v", task, [], [], evaluation_result=eval_result, feedback=None)

    def test_show_full_evaluation_with_evaluation_result_object(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        task.tests = []
        eval_result = MagicMock()
        eval_result.final_score = 0.5
        with patch.object(v.console, "print"):
            v.show_full_evaluation("agent-1", "v", task, [], [], evaluation_result=eval_result, feedback=None)

    def test_show_full_evaluation_with_feedback(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        task.tests = []
        feedback = MagicMock()
        feedback.passed_tests = 2
        feedback.failed_tests = 1
        feedback.total_execution_time = 5.0
        with patch.object(v.console, "print"):
            v.show_full_evaluation("agent-1", "v", task, [], [], evaluation_result=None, feedback=feedback)

    def test_show_full_evaluation_with_tests_and_test_results(self):
        """Covers branch that builds tests table when task.tests and test_results exist."""
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        task.prompt = "P"
        task.url = "http://x.com"
        test_mock = MagicMock()
        test_mock.__class__.__name__ = "CheckUrlTest"
        test_mock.url = "/about/"
        task.tests = [test_mock]
        test_results = [{"success": True}, {"success": False}]
        with patch.object(v.console, "print"):
            v.show_full_evaluation(
                "agent-1",
                "v",
                task,
                [MagicMock()],
                test_results,
                evaluation_result=MagicMock(final_score=0.5),
                feedback=None,
            )


class TestPrintSummary:
    def test_print_summary_minimal(self):
        v = SubnetVisualizer()
        results = {"agent-1": {"global_scores": [0.5, 0.8], "projects": {}}}
        agents = [MagicMock()]
        agents[0].id = "agent-1"
        with patch.object(v.console, "print"):
            v.print_summary(results, agents)

    def test_print_summary_with_projects(self):
        v = SubnetVisualizer()
        results = {
            "agent-1": {
                "global_scores": [0.5, 0.8],
                "projects": {"autocinema": [0.6, 0.9], "autobooks": [0.4]},
            }
        }
        agents = [MagicMock()]
        agents[0].id = "agent-1"
        with patch.object(v.console, "print"):
            v.print_summary(results, agents)


class TestShowListOfEvaluations:
    def test_show_list_of_evaluations_minimal(self):
        v = SubnetVisualizer()
        task = MagicMock()
        task.id = "t1"
        sol1 = MagicMock()
        sol1.web_agent_id = "agent-1"
        sol1.actions = []
        sol1.evaluation_result = MagicMock(test_results=[], feedback=None, final_score=0.0)
        sol2 = MagicMock()
        sol2.web_agent_id = "agent-2"
        sol2.actions = []
        sol2.evaluation_result = MagicMock(test_results=[], feedback=None, final_score=0.0)
        with patch.object(v.console, "print"):
            v.show_list_of_evaluations(task, [sol1, sol2], [sol1.evaluation_result, sol2.evaluation_result], "validator")


class TestVisualizeDecorators:
    """Tests for visualize_task, visualize_evaluation, visualize_list_of_evaluations, visualize_summary."""

    @pytest.mark.asyncio
    async def test_visualize_task_single_result(self):
        v = SubnetVisualizer()
        with patch.object(v, "show_task_with_tests") as show:

            @visualize_task(v)
            async def fn():
                task = MagicMock()
                task.id = "t1"
                task.prompt = "P"
                task.url = "http://x.com"
                task.tests = []
                return task

            result = await fn()
        show.assert_called_once_with(result)

    @pytest.mark.asyncio
    async def test_visualize_task_list_result(self):
        v = SubnetVisualizer()
        with patch.object(v, "show_task_with_tests") as show:

            @visualize_task(v)
            async def fn():
                t1 = MagicMock(id="a", prompt="P", url="u", tests=[])
                t2 = MagicMock(id="b", prompt="Q", url="u", tests=[])
                return [t1, t2]

            result = await fn()
        assert len(result) == 2
        assert show.call_count == 2
        show.assert_any_call(result[0])
        show.assert_any_call(result[1])

    @pytest.mark.asyncio
    async def test_visualize_evaluation(self):
        v = SubnetVisualizer()
        with patch.object(v, "show_full_evaluation") as show:

            @visualize_evaluation(v)
            async def fn(web_project, task, task_solution, validator_id):
                res = MagicMock()
                res.test_results = []
                res.feedback = None
                return res

            task = MagicMock()
            task_solution = MagicMock(web_agent_id="agent-1", actions=[])
            await fn(MagicMock(), task, task_solution, "validator-id")
            show.assert_called_once()
            call_kw = show.call_args[1]
            assert call_kw["agent_id"] == "agent-1"
            assert call_kw["validator_id"] == "validator-id"
            assert call_kw["task"] == task

    @pytest.mark.asyncio
    async def test_visualize_list_of_evaluations(self):
        v = SubnetVisualizer()
        with patch.object(v, "show_list_of_evaluations") as show:

            @visualize_list_of_evaluations(v)
            async def fn(web_project, task, task_solutions, validator_id):
                return [MagicMock(), MagicMock()]

            task = MagicMock()
            solutions = [MagicMock(), MagicMock()]
            result = await fn(MagicMock(), task, solutions, "vid")
            show.assert_called_once_with(task, solutions, result, "vid")

    def test_visualize_summary(self):
        v = SubnetVisualizer()
        with patch.object(v, "print_summary") as print_summary:

            @visualize_summary(v)
            def fn(results, agents):
                pass

            results = {"a": {"global_scores": [0.5], "projects": {}}}
            agents = [MagicMock()]
            agents[0].id = "a"
            fn(results, agents)
            print_summary.assert_called_once_with(results, agents)
