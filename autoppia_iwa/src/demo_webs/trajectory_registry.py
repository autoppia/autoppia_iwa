"""
URL remapping helpers for deterministic trajectory replay.
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

__all__ = [
    "remap_url_to_frontend",
]


def remap_url_to_frontend(url: str, frontend_url: str) -> str:
    """
    Replace scheme+netloc in ``url`` with those from ``frontend_url``,
    preserving path/query/fragment.
    """

    if not url or not frontend_url:
        return url

    src = urlsplit(url)
    dst = urlsplit(frontend_url)
    return urlunsplit((dst.scheme, dst.netloc, src.path, src.query, src.fragment))
