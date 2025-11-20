import asyncio
from urllib.parse import parse_qs, urljoin, urlparse, urlunparse

try:
    import aiohttp
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore


from loguru import logger


# ─────────────────────────── Seed Resolution ───────────────────────────
async def resolve_v2_seed_from_url(task_url: str | None, webs_server_url: str = "http://localhost:8090") -> int:
    """
    Call /seeds/resolve endpoint to get v2 seed from base seed in URL.

    This is the proper way to derive seeds - it calls the centralized
    webs_server endpoint instead of duplicating the formula.

    Args:
        task_url: URL with ?seed=X parameter
        webs_server_url: Base URL of webs_server (default: http://localhost:8090)

    Returns:
        Derived v2 seed (1-300), defaults to 1 if any error occurs
    """
    if not task_url:
        return 1

    try:
        # Extract base seed from URL
        parsed = urlparse(task_url)
        query = parse_qs(parsed.query)

        if not query.get("seed"):
            return 1

        base_seed = int(str(query["seed"][0]).strip())

        # Call /seeds/resolve endpoint
        resolve_url = urljoin(webs_server_url, "/seeds/resolve")

        if aiohttp is None:
            logger.error("aiohttp is not installed, cannot resolve seeds from endpoint")
            return 1

        async with (
            aiohttp.ClientSession() as session,
            session.get(
                resolve_url,
                params={
                    "seed": str(base_seed),
                    "v1_enabled": "false",
                    "v2_enabled": "true",
                    "v3_enabled": "false",
                },
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp,
        ):
            resp.raise_for_status()
            data = await resp.json()
            v2_seed = data.get("v2")

            if v2_seed is not None and isinstance(v2_seed, int):
                return v2_seed

            logger.warning(f"Invalid v2 seed from endpoint: {v2_seed}")
            return 1

    except Exception as e:
        logger.warning(f"Failed to resolve v2 seed from URL {task_url}: {e}")
        return 1


def extract_seed_from_url(url: str | None) -> int | None:
    """
    DEPRECATED: Use resolve_v2_seed_from_url() instead.

    This function extracted ?seed=X but didn't derive v2. The new system
    uses resolve_v2_seed_from_url() which calls /seeds/resolve endpoint.
    """
    logger.warning("extract_seed_from_url() is DEPRECATED. Use resolve_v2_seed_from_url() instead to call /seeds/resolve endpoint.")
    if not url:
        return None
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if query.get("seed"):
            value = int(str(query["seed"][0]).strip())
            return value
    except Exception:
        return None
    return None


# ─────────────────────────── Async-compatible API ───────────────────────────
_ASYNC_SESSION: "aiohttp.ClientSession | None" = None  # type: ignore
_ASYNC_CACHE: dict[tuple, list[dict]] = {}
_ASYNC_LOCK = asyncio.Lock()


async def _get_async_session() -> "aiohttp.ClientSession":  # type: ignore
    if aiohttp is None:
        raise RuntimeError("aiohttp is not installed but load_dataset_data was called")
    global _ASYNC_SESSION
    if _ASYNC_SESSION is None or _ASYNC_SESSION.closed:
        _ASYNC_SESSION = aiohttp.ClientSession()
    return _ASYNC_SESSION


async def load_dataset_data(
    backend_url: str,
    project_key: str,
    entity_type: str,
    seed_value: int,
    limit: int,
    method: str = "select",
    filter_key: str | None = None,
    filter_values: str | None = None,
) -> list[dict]:
    """
    Async loader for /datasets/load using aiohttp with a simple in-memory cache.
    """

    # Ensure backend URL uses port 8090 regardless of the provided port
    def _ensure_port_8090(base_url: str) -> str:
        try:
            parsed = urlparse(base_url)
            # If URL is malformed or missing components, return as-is
            if not parsed.scheme or not parsed.netloc:
                return base_url
            hostname = parsed.hostname
            if not hostname:
                return base_url
            # Preserve auth if present
            auth = ""
            if parsed.username:
                auth = parsed.username
                if parsed.password:
                    auth += f":{parsed.password}"
                auth += "@"
            netloc = f"{auth}{hostname}:8090"
            updated = parsed._replace(netloc=netloc)
            return urlunparse(updated)
        except Exception:
            return base_url

    base = _ensure_port_8090(backend_url)
    url = urljoin(base, "datasets/load")
    params: dict[str, str | int] = {
        "project_key": project_key,
        "entity_type": entity_type,
        "seed_value": seed_value,
        "limit": limit,
    }
    # Only add method, filter_key, and filter_values if they are not None
    if method is not None:
        params["method"] = method
    if filter_key is not None:
        params["filter_key"] = filter_key
    if filter_values is not None:
        params["filter_values"] = filter_values  # CSV string

    cache_key = (
        url,
        params.get("project_key"),
        params.get("entity_type"),
        params.get("seed_value"),
        params.get("limit"),
        params.get("method"),
        params.get("filter_key"),
        params.get("filter_values"),
    )

    # Fast-path cache check
    async with _ASYNC_LOCK:
        if cache_key in _ASYNC_CACHE:
            return _ASYNC_CACHE[cache_key]

    try:
        session = await _get_async_session()
        async with session.get(url, params=params, timeout=10) as resp:
            resp.raise_for_status()
            body = await resp.json()
            data = body.get("data") if isinstance(body, dict) else None
            if isinstance(data, list):
                async with _ASYNC_LOCK:
                    _ASYNC_CACHE[cache_key] = data
                return data
            logger.warning("Unexpected response structure from /datasets/load: {}", type(body))
            return []
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.warning("Failed to fetch dataset (async) from {} with params {}: {}", url, params, e)
        return []


async def close_async_session() -> None:
    """Close the shared aiohttp session if open."""
    global _ASYNC_SESSION
    if _ASYNC_SESSION is not None and not _ASYNC_SESSION.closed:
        try:
            await _ASYNC_SESSION.close()
        except Exception:
            pass
        finally:
            _ASYNC_SESSION = None
