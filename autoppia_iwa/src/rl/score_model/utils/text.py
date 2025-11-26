"""Text encoding helpers with SentenceTransformer fallback."""

from __future__ import annotations

from typing import List, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer

    _txt_model: Optional[SentenceTransformer] = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:  # pragma: no cover - optional dependency
    _txt_model = None


def encode_text(text: str, extra_tokens: Optional[List[str]] = None) -> list[float]:
    """Encode text plus optional tokens into a fixed-length vector."""

    sentence = text or ""
    if extra_tokens:
        sentence = " ".join(extra_tokens) + " || " + sentence
    if _txt_model is not None:
        embedding = _txt_model.encode([sentence])[0]
        return embedding.astype("float32").tolist()
    # Fallback: hash into sparse indicator vector
    vec = np.zeros(384, dtype="float32")
    if sentence:
        idx = hash(sentence) % 384
        vec[idx] = 1.0
    return vec.tolist()
