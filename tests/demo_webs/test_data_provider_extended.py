from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs import data_provider


class _FakeResponse:
    def __init__(self, body):
        self._body = body

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        return None

    async def json(self):
        return self._body


class _FakeSession:
    def __init__(self, response=None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls = []
        self.closed = False

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        if self.error:
            raise self.error
        return self.response


@pytest.mark.asyncio
async def test_load_dataset_data_fetches_response_and_populates_cache(monkeypatch):
    data_provider._ASYNC_CACHE.clear()
    session = _FakeSession(response=_FakeResponse({"data": [{"id": 7}]}))
    monkeypatch.setattr(data_provider, "_get_async_session", lambda: session)

    result = await data_provider.load_dataset_data(
        backend_url="http://example.com/api/",
        project_key="proj",
        entity_type="films",
        seed_value=12,
        limit=999,
        filter_key="genre",
        filter_values="thriller",
    )

    assert result == [{"id": 7}]
    assert len(session.calls) == 1
    url, params, timeout = session.calls[0]
    assert url == "http://example.com/datasets/load"
    assert params["limit"] == 50
    assert params["filter_key"] == "genre"
    assert params["filter_values"] == "thriller"
    assert timeout == 10


@pytest.mark.asyncio
async def test_load_dataset_data_returns_empty_for_unexpected_response(monkeypatch):
    data_provider._ASYNC_CACHE.clear()
    session = _FakeSession(response=_FakeResponse({"unexpected": []}))
    monkeypatch.setattr(data_provider, "_get_async_session", lambda: session)

    result = await data_provider.load_dataset_data(
        backend_url="http://example.com/",
        project_key="proj",
        entity_type="films",
        seed_value=12,
    )

    assert result == []


@pytest.mark.asyncio
async def test_load_dataset_data_returns_empty_when_request_raises(monkeypatch):
    data_provider._ASYNC_CACHE.clear()
    session = _FakeSession(error=RuntimeError("boom"))
    monkeypatch.setattr(data_provider, "_get_async_session", lambda: session)

    result = await data_provider.load_dataset_data(
        backend_url="http://example.com/",
        project_key="proj",
        entity_type="films",
        seed_value=12,
    )

    assert result == []


@pytest.mark.asyncio
async def test_close_async_session_closes_and_resets_session():
    session = type("Session", (), {"closed": False, "close": AsyncMock()})()
    original = data_provider._ASYNC_SESSION
    data_provider._ASYNC_SESSION = session
    try:
        await data_provider.close_async_session()
    finally:
        data_provider._ASYNC_SESSION = original

    session.close.assert_awaited_once()
    assert data_provider._ASYNC_SESSION is original
