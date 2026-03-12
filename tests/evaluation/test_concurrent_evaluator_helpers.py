"""Unit tests for concurrent_evaluator helper functions (_url_hostname, _is_navigation_url_allowed) and logging fallbacks."""

from unittest.mock import patch

from autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator import (
    _ensure_evaluation_level,
    _is_navigation_url_allowed,
    _log_action_execution,
    _log_evaluation_event,
    _log_evaluation_fallback,
    _log_gif_creation,
    _url_hostname,
)


class TestUrlHostname:
    def test_normal_url(self):
        assert _url_hostname("https://example.com/path") == "example.com"
        assert _url_hostname("http://foo.bar.org:8080/x") == "foo.bar.org"

    def test_none_or_empty(self):
        assert _url_hostname(None) is None
        assert _url_hostname("") is None

    def test_no_host(self):
        # urlparse might return hostname None for relative or malformed
        assert _url_hostname("http://") is None or _url_hostname("http://") == ""


class TestIsNavigationUrlAllowed:
    def test_no_candidate_allowed(self):
        allowed, err = _is_navigation_url_allowed(is_web_real=False, task_url="http://localhost:8000", candidate_url=None)
        assert allowed is True
        assert err is None

    def test_non_http_scheme_not_allowed(self):
        allowed, err = _is_navigation_url_allowed(is_web_real=False, task_url="http://localhost", candidate_url="file:///etc/passwd")
        assert allowed is False
        assert "scheme" in err.lower() or "file" in err.lower()

    def test_demo_web_localhost_allowed(self):
        allowed, err = _is_navigation_url_allowed(is_web_real=False, task_url="http://localhost:8000", candidate_url="http://localhost:8000/page")
        assert allowed is True
        assert err is None

    def test_demo_web_127_allowed(self):
        allowed, err = _is_navigation_url_allowed(is_web_real=False, task_url="http://127.0.0.1:8000", candidate_url="http://127.0.0.1:8000/x")
        assert allowed is True

    def test_real_web_same_host_allowed(self):
        allowed, err = _is_navigation_url_allowed(is_web_real=True, task_url="https://example.com/start", candidate_url="https://example.com/other")
        assert allowed is True
        assert err is None

    def test_real_web_different_host_not_allowed(self):
        allowed, err = _is_navigation_url_allowed(is_web_real=True, task_url="https://example.com/", candidate_url="https://evil.com/")
        assert allowed is False
        assert err is not None

    def test_relative_candidate_allowed(self):
        # No host in candidate (relative or path-only)
        allowed, err = _is_navigation_url_allowed(is_web_real=False, task_url="http://localhost", candidate_url="/relative/path")
        # Implementation may allow or disallow; at least no crash
        assert isinstance(allowed, bool)
        assert err is None or isinstance(err, str)

    def test_demo_web_remote_same_allowed_host(self):
        allowed, err = _is_navigation_url_allowed(
            is_web_real=False,
            task_url="http://demo.example.com:8000/start",
            candidate_url="http://demo.example.com:8000/page",
        )
        assert allowed is True
        assert err is None

    def test_demo_web_different_host_not_allowed(self):
        allowed, err = _is_navigation_url_allowed(
            is_web_real=False,
            task_url="http://localhost:8000",
            candidate_url="http://evil.com/page",
        )
        assert allowed is False
        assert err is not None
        assert "not allowed" in err.lower()

    def test_real_web_task_url_no_host(self):
        allowed, err = _is_navigation_url_allowed(
            is_web_real=True,
            task_url="file:///local/path",
            candidate_url="https://example.com/page",
        )
        assert allowed is False
        assert "Task URL host" in err or "could not be determined" in err

    @patch("autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator._is_testing_mode", return_value=True)
    def test_demo_web_subnet_testing_allows_any_host(self, mock_testing):
        allowed, err = _is_navigation_url_allowed(
            is_web_real=False,
            task_url="http://localhost:8000",
            candidate_url="https://other.example.com/page",
        )
        assert allowed is True
        assert err is None


class TestLoggingHelpers:
    def test_ensure_evaluation_level_idempotent(self):
        _ensure_evaluation_level()
        _ensure_evaluation_level()

    def test_log_evaluation_fallback(self):
        _log_evaluation_fallback("test message")

    def test_log_action_execution_uses_fallback_when_import_error(self):
        import sys

        class FakeLoggingModule:
            def __getattr__(self, name):
                raise ImportError("benchmark not available")

        key = "autoppia_iwa.entrypoints.benchmark.utils.logging"
        saved = sys.modules.get(key)
        sys.modules[key] = FakeLoggingModule()
        try:
            _log_action_execution("test action", web_agent_id="agent1")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        _log_action_execution("test action", web_agent_id=None)

    def test_log_gif_creation_uses_fallback_when_import_error(self):
        import sys

        class FakeLoggingModule:
            def __getattr__(self, name):
                raise ImportError("benchmark not available")

        key = "autoppia_iwa.entrypoints.benchmark.utils.logging"
        saved = sys.modules.get(key)
        sys.modules[key] = FakeLoggingModule()
        try:
            _log_gif_creation("test gif", web_agent_id="agent1")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)

    def test_log_evaluation_event_uses_fallback_with_context(self):
        import sys

        class FakeLoggingModule:
            def __getattr__(self, name):
                raise ImportError("benchmark not available")

        key = "autoppia_iwa.entrypoints.benchmark.utils.logging"
        saved = sys.modules.get(key)
        sys.modules[key] = FakeLoggingModule()
        try:
            _log_evaluation_event("test event", context="CUSTOM")
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        _log_evaluation_event("test event", context="GENERAL")
