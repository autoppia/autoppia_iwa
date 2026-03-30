from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import RESETTING_DB_CONTEXT, BackendDemoWebService


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


class _AsyncContextManager:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, exc_type, exc, tb):
        return None


def test_init_uses_frontend_url_for_web_url():
    service = BackendDemoWebService(_make_project(frontend_url="http://front:8000/"), web_agent_id="agent-1")
    assert service.base_url == "http://localhost:8090/api/"
    assert service.web_url == "http://front:8000/"
    assert service.web_agent_id == "agent-1"


def test_get_session_reuses_open_session(monkeypatch):
    created = []

    def _make_session(**kwargs):
        session = Mock()
        session.closed = False
        created.append((session, kwargs))
        return session

    monkeypatch.setattr("autoppia_iwa.src.demo_webs.demo_webs_service.aiohttp.ClientSession", _make_session)
    service = BackendDemoWebService(_make_project())

    first = service._get_session()
    second = service._get_session()

    assert first is second
    assert len(created) == 1
    assert "json_serialize" in created[0][1]


@pytest.mark.asyncio
async def test_get_backend_events_builds_expected_request(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json = AsyncMock(
        return_value=[
            {"data": {"event_name": "LOGIN", "data": {"user": "alice"}, "web_agent_id": "agent-1"}},
        ]
    )
    session = Mock()
    session.closed = False
    session.get = Mock(return_value=_AsyncContextManager(response))

    service = BackendDemoWebService(_make_project(frontend_url="http://front:8000/"), web_agent_id="agent-1", validator_id="validator-x")
    service._session = session

    events = await service.get_backend_events("agent-2")

    assert len(events) == 1
    assert events[0].event_name == "LOGIN"
    assert events[0].data == {"user": "alice"}
    session.get.assert_called_once()
    _, kwargs = session.get.call_args
    assert kwargs["params"] == {
        "web_url": "http://front:8000",
        "web_agent_id": "agent-2",
        "validator_id": "validator-x",
    }


@pytest.mark.asyncio
async def test_get_backend_events_returns_empty_on_client_error(monkeypatch):
    session = Mock()
    session.closed = False
    session.get = Mock(side_effect=aiohttp.ClientError("boom"))

    service = BackendDemoWebService(_make_project())
    service._session = session

    assert await service.get_backend_events("agent-1") == []


@pytest.mark.asyncio
async def test_get_backend_events_returns_empty_for_real_web():
    service = BackendDemoWebService(_make_project(is_web_real=True))
    assert await service.get_backend_events("agent-1") == []


@pytest.mark.asyncio
async def test_reset_database_uses_instance_agent_id_when_not_overridden():
    response = Mock()
    response.status = 202
    session = Mock()
    session.closed = False
    session.delete = Mock(return_value=_AsyncContextManager(response))

    service = BackendDemoWebService(_make_project(frontend_url="http://front:8000/"), web_agent_id="agent-1", validator_id="validator-x")
    service._session = session

    result = await service.reset_database()

    assert result is True
    session.delete.assert_called_once()
    _, kwargs = session.delete.call_args
    assert kwargs["params"] == {
        "web_url": "http://front:8000",
        "web_agent_id": "agent-1",
        "validator_id": "validator-x",
    }


@pytest.mark.asyncio
async def test_reset_database_returns_false_for_real_web(monkeypatch):
    log_event = Mock()
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.demo_webs_service._log_evaluation_event", log_event)

    service = BackendDemoWebService(_make_project(is_web_real=True))

    assert await service.reset_database() is False
    assert any(RESETTING_DB_CONTEXT in str(call) for call in log_event.call_args_list)


@pytest.mark.asyncio
async def test_reset_database_returns_false_on_client_error():
    session = Mock()
    session.closed = False
    session.delete = Mock(side_effect=aiohttp.ClientError("boom"))

    service = BackendDemoWebService(_make_project())
    service._session = session

    assert await service.reset_database() is False


@pytest.mark.asyncio
async def test_close_closes_open_session():
    session = Mock()
    session.close = AsyncMock()
    service = BackendDemoWebService(_make_project())
    service._session = session

    await service.close()

    session.close.assert_awaited_once()
    assert service._session is None
