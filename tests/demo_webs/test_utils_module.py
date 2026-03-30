"""Tests for demo_webs.utils helpers."""

import json
from unittest.mock import patch

from autoppia_iwa.src.demo_webs import utils


class _Response:
    def __init__(self, status: int, payload: dict):
        self.status = status
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_get_frontend_url_uses_project_index():
    url = utils.get_frontend_url(2)
    assert url.endswith(":8002/")


def test_get_backend_service_url_uses_shared_port():
    url = utils.get_backend_service_url()
    assert url.endswith(":8090/")


def test_get_web_version_prefers_http_endpoint():
    with patch("urllib.request.urlopen", return_value=_Response(200, {"version": "1.2.3"})):
        version = utils.get_web_version("autocinema", "http://localhost:8000/")
    assert version == "1.2.3"


def test_get_web_version_ignores_unknown_http_version():
    with patch("urllib.request.urlopen", return_value=_Response(200, {"version": "unknown"})):
        version = utils.get_web_version("autocinema", "http://localhost:8000/")
    assert version is not None
    assert version != "unknown"


def test_get_web_version_falls_back_to_package_json_when_http_fails(tmp_path, monkeypatch):
    webs_demo = tmp_path / "autoppia_webs_demo"
    pkg = webs_demo / "web_1_autocinema" / "package.json"
    pkg.parent.mkdir(parents=True)
    pkg.write_text(json.dumps({"version": "9.9.9"}), encoding="utf-8")
    monkeypatch.setenv("WEBS_DEMO_PATH", str(webs_demo))

    with patch("urllib.request.urlopen", side_effect=RuntimeError("boom")):
        version = utils.get_web_version("autocinema", "http://localhost:8000/")

    assert version == "9.9.9"


def test_get_web_version_returns_none_for_unknown_project():
    assert utils.get_web_version("missing-project") is None


def test_get_web_version_returns_none_for_invalid_package_json(tmp_path, monkeypatch):
    webs_demo = tmp_path / "autoppia_webs_demo"
    pkg = webs_demo / "web_1_autocinema" / "package.json"
    pkg.parent.mkdir(parents=True)
    pkg.write_text("{invalid", encoding="utf-8")
    monkeypatch.setenv("WEBS_DEMO_PATH", str(webs_demo))

    version = utils.get_web_version("autocinema", "http://localhost:8000/")
    assert version is not None


def test_log_event_prints_delimiters(capsys):
    utils.log_event({"event": "x"})
    captured = capsys.readouterr()
    assert "=" * 50 in captured.out
    assert "{'event': 'x'}" in captured.out
