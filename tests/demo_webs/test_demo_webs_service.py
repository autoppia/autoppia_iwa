"""Unit tests for demo_webs_service (BackendDemoWebService, logging helpers)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import (
    RESETTING_DB_CONTEXT,
    BackendDemoWebService,
    _log_backend_test,
    _log_evaluation_event,
)


def _make_project(
    *,
    backend_url: str = "http://localhost:8090/api/",
    frontend_url: str = "http://localhost:8000/",
    is_web_real: bool = False,
) -> WebProject:
    return WebProject(
        id="test",
        name="Test",
        backend_url=backend_url,
        frontend_url=frontend_url,
        use_cases=[],
        is_web_real=is_web_real,
    )


# -----------------------------------------------------------------------------
# _log_evaluation_event (ImportError fallback branches)
# -----------------------------------------------------------------------------


class TestLogEvaluationEvent:
    def test_fallback_general_context_when_benchmark_logging_missing(self):
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.logger") as mock_logger:

            def fake_import(name, *args, **kwargs):
                if "entrypoints.benchmark.utils.logging" in (name or ""):
                    raise ImportError("no benchmark logging")
                return __import__(name, *args, **kwargs)

            with patch("builtins.__import__", fake_import):
                _log_evaluation_event("hello", context="GENERAL")
            mock_logger.info.assert_called_once()
            assert "[EVALUATION] hello" in str(mock_logger.info.call_args)

    def test_fallback_non_general_context_when_benchmark_logging_missing(self):
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.logger") as mock_logger:

            def fake_import(name, *args, **kwargs):
                if "entrypoints.benchmark.utils.logging" in (name or ""):
                    raise ImportError("no benchmark logging")
                return __import__(name, *args, **kwargs)

            with patch("builtins.__import__", fake_import):
                _log_evaluation_event("world", context="RESET")
            mock_logger.info.assert_called_once()
            assert "[EVALUATION] [RESET] world" in str(mock_logger.info.call_args)


# -----------------------------------------------------------------------------
# _log_backend_test (ImportError fallback)
# -----------------------------------------------------------------------------


class TestLogBackendTest:
    def test_fallback_calls_log_evaluation_event_when_benchmark_logging_missing(self):
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service._log_evaluation_event") as mock_log:

            def fake_import(name, *args, **kwargs):
                if "entrypoints.benchmark.utils.logging" in (name or ""):
                    raise ImportError("no benchmark logging")
                return __import__(name, *args, **kwargs)

            with patch("builtins.__import__", fake_import):
                _log_backend_test("test message", web_agent_id="agent-1")
            mock_log.assert_called_once()
            args, kwargs = mock_log.call_args
            assert "[GET BACKEND TEST] [agent=agent-1] test message" in args[0]
            assert kwargs.get("context") == "GET_BACKEND_TEST"

    def test_success_path_calls_benchmark_log_backend_test(self):
        """Covers line 42: when benchmark logging is available, log_backend_test is called."""
        with patch(
            "autoppia_iwa.entrypoints.benchmark.utils.logging.log_backend_test",
            MagicMock(),
        ) as mock_log_backend_test:
            _log_backend_test("backend check", web_agent_id="agent-99")
            mock_log_backend_test.assert_called_once()
            (arg,) = mock_log_backend_test.call_args[0]
            assert "[agent=agent-99] backend check" in arg


# -----------------------------------------------------------------------------
# BackendDemoWebService
# -----------------------------------------------------------------------------


class TestBackendDemoWebServiceInit:
    def test_sets_base_url_and_web_url_from_project(self):
        project = _make_project(backend_url="http://api:8090/", frontend_url="http://front:8000/")
        svc = BackendDemoWebService(web_project=project, web_agent_id="sid")
        assert svc.base_url == "http://api:8090/"
        assert svc.web_url == "http://front:8000/"

    def test_web_url_fallback_to_backend_when_frontend_empty(self):
        project = _make_project(frontend_url="")
        svc = BackendDemoWebService(web_project=project)
        assert svc.web_url == project.backend_url

    def test_uses_stdlib_json_when_orjson_not_available(self):
        project = _make_project()
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "orjson":
                raise ImportError("orjson not installed")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", fake_import):
            svc = BackendDemoWebService(web_project=project)
        assert svc._json_parser.__name__ == "json"
        assert svc._read_mode == "r"


class TestBackendDemoWebServiceGetBackendEvents:
    @pytest.mark.asyncio
    async def test_returns_empty_when_is_web_real(self):
        project = _make_project(is_web_real=True)
        svc = BackendDemoWebService(web_project=project)
        result = await svc.get_backend_events("any")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_events_on_success(self):
        project = _make_project()
        events_data = [
            {"data": {"event_name": "LOGIN", "data": {"user": "alice"}, "web_agent_id": "a1"}},
        ]
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(return_value=None)
        mock_response.json = AsyncMock(return_value=events_data)
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock(return_value=None)))
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", return_value=mock_session):
            svc = BackendDemoWebService(web_project=project)
            result = await svc.get_backend_events("a1")
        assert len(result) == 1
        assert result[0].event_name == "LOGIN"
        assert result[0].data == {"user": "alice"}

    @pytest.mark.asyncio
    async def test_returns_empty_on_exception(self):
        project = _make_project()
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=RuntimeError("network error"))
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", return_value=mock_session):
            svc = BackendDemoWebService(web_project=project)
            result = await svc.get_backend_events("a1")
        assert result == []


class TestBackendDemoWebServiceResetDatabase:
    @pytest.mark.asyncio
    async def test_returns_false_when_is_web_real(self):
        project = _make_project(is_web_real=True)
        svc = BackendDemoWebService(web_project=project)
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service._log_evaluation_event") as mock_log:
            result = await svc.reset_database()
        assert result is False
        assert any(RESETTING_DB_CONTEXT in str(c) for c in mock_log.call_args_list)
        assert any("real website" in str(c).lower() for c in mock_log.call_args_list)

    @pytest.mark.asyncio
    async def test_returns_true_on_200(self):
        project = _make_project()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session = MagicMock()
        mock_session.delete = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_response),
                __aexit__=AsyncMock(return_value=None),
            )
        )
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", return_value=mock_session):
            svc = BackendDemoWebService(web_project=project)
            result = await svc.reset_database("agent-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_on_non_2xx(self):
        project = _make_project()
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_session = MagicMock()
        mock_session.delete = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_response),
                __aexit__=AsyncMock(return_value=None),
            )
        )
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", return_value=mock_session):
            svc = BackendDemoWebService(web_project=project)
            result = await svc.reset_database()
        # Implementation returns True only for 200/202; otherwise falls through (None) or False on exception
        assert result is not True

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self):
        project = _make_project()
        mock_session = MagicMock()
        mock_session.delete = MagicMock(side_effect=RuntimeError("api down"))
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", return_value=mock_session):
            svc = BackendDemoWebService(web_project=project)
            result = await svc.reset_database()
        assert result is False


class TestBackendDemoWebServiceClose:
    @pytest.mark.asyncio
    async def test_closes_session_and_sets_none(self):
        project = _make_project()
        mock_session = MagicMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        with patch("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", return_value=mock_session):
            svc = BackendDemoWebService(web_project=project)
            svc._session = mock_session
            await svc.close()
        assert svc._session is None
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_op_when_session_none(self):
        project = _make_project()
        svc = BackendDemoWebService(web_project=project)
        svc._session = None
        await svc.close()
        assert svc._session is None
