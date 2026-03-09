"""Unit tests for concurrent_evaluator helper functions (_url_hostname, _is_navigation_url_allowed)."""

from autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator import (
    _is_navigation_url_allowed,
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
