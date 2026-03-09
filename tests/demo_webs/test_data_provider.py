"""Unit tests for demo_webs.projects.data_provider."""

import pytest

from autoppia_iwa.src.demo_webs.projects.data_provider import (
    close_async_session,
    get_seed_from_url,
    load_dataset_data,
)


class TestGetSeedFromUrl:
    def test_none_url_returns_1(self):
        assert get_seed_from_url(None) == 1

    def test_empty_url_returns_1(self):
        assert get_seed_from_url("") == 1

    def test_no_seed_param_returns_1(self):
        assert get_seed_from_url("http://localhost:8001/") == 1

    def test_seed_in_query(self):
        assert get_seed_from_url("http://localhost:8001/?seed=42") == 42

    def test_seed_clamped_to_999(self):
        assert get_seed_from_url("http://localhost:8001/?seed=9999") == 999

    def test_seed_clamped_to_1(self):
        assert get_seed_from_url("http://localhost:8001/?seed=0") == 1

    def test_invalid_seed_returns_1(self):
        assert get_seed_from_url("http://localhost:8001/?seed=abc") == 1


@pytest.mark.asyncio
async def test_load_dataset_data_uses_cache():
    """When cache has the key, load_dataset_data returns cached data without HTTP."""
    from autoppia_iwa.src.demo_webs.projects import data_provider

    cache_key = (
        "http://example.com/datasets/load",
        "proj",
        "movies",
        42,
        50,
        "select",
        None,
        None,
    )
    data_provider._ASYNC_CACHE[cache_key] = [{"id": 1, "name": "Cached"}]
    try:
        result = await load_dataset_data(
            backend_url="http://example.com/",
            project_key="proj",
            entity_type="movies",
            seed_value=42,
        )
        assert result == [{"id": 1, "name": "Cached"}]
    finally:
        data_provider._ASYNC_CACHE.pop(cache_key, None)


@pytest.mark.asyncio
async def test_close_async_session_no_op_when_none():
    """close_async_session does nothing when session is None."""
    from autoppia_iwa.src.demo_webs.projects import data_provider

    orig = data_provider._ASYNC_SESSION
    data_provider._ASYNC_SESSION = None
    try:
        await close_async_session()
    finally:
        data_provider._ASYNC_SESSION = orig
