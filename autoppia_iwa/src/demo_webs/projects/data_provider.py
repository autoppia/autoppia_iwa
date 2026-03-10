import asyncio
from urllib.parse import parse_qs, urljoin, urlparse

try:
    import aiohttp
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore


from loguru import logger


# ─────────────────────────── Seed Extraction ───────────────────────────
def get_seed_from_url(task_url: str | None) -> int:
    """
    Extrae el seed del parámetro ?seed=X de la URL.

    Args:
        task_url: URL con parámetro ?seed=X (ej: "http://localhost:8001/?seed=5")

    Returns:
        Seed value (1-999), defaults to 1 if not found
    """
    if not task_url:
        return 1

    try:
        parsed = urlparse(task_url)
        query = parse_qs(parsed.query)

        if not query.get("seed"):
            return 1

        seed = int(str(query["seed"][0]).strip())

        # Clamp to valid range
        return max(1, min(seed, 999))

    except (ValueError, IndexError, KeyError, AttributeError) as e:
        logger.warning(f"Failed to extract seed from URL {task_url}: {e}")
        return 1


# ─────────────────────────── Async-compatible API ───────────────────────────
_ASYNC_SESSION: "aiohttp.ClientSession | None" = None  # type: ignore
_ASYNC_CACHE: dict[tuple, list[dict]] = {}
_ASYNC_LOCK = asyncio.Lock()


def _get_async_session() -> "aiohttp.ClientSession":  # type: ignore
    """Get or create the shared aiohttp session. Synchronous function as ClientSession creation is synchronous."""
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
    limit: int = 50,
    method: str = "select",
    filter_key: str | None = None,
    filter_values: str | None = None,
) -> list[dict]:
    """
    Async loader for /datasets/load using aiohttp with a simple in-memory cache.

    Args:
        limit: Number of items to fetch. Defaults to 50 and will be enforced to exactly 50.
    """
    # Enforce exactly 50 items
    limit = 50

    # Construir URL directamente usando el backend_url proporcionado
    url = urljoin(backend_url.rstrip("/"), "datasets/load")
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
        session = _get_async_session()
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
        logger.exception("Failed to fetch dataset (async) from {} with params {}: {}", url, params, e)
        return []


async def close_async_session() -> None:
    """Close the shared aiohttp session if open."""
    global _ASYNC_SESSION
    if _ASYNC_SESSION is not None and not _ASYNC_SESSION.closed:
        try:
            await _ASYNC_SESSION.close()
        except Exception:  # Catch all exceptions when closing session to ensure cleanup
            pass
        finally:
            _ASYNC_SESSION = None
