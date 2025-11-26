"""Hashing helpers for lightweight text feature extraction."""

from __future__ import annotations

import hashlib


def stable_hash(text: str) -> int:
    """Return a deterministic 64-bit hash for ``text``."""

    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def feature_index(token: str, dim: int) -> int:
    """Map token to a bucket in ``[0, dim)``."""

    return stable_hash(token) % dim
