"""Optional CLIP-based image embeddings with graceful fallback."""

from __future__ import annotations

import base64
import io

from PIL import Image

try:
    from sentence_transformers import SentenceTransformer

    _img_model = SentenceTransformer("clip-ViT-B-32")
except Exception:  # pragma: no cover - optional dependency
    _img_model = None


def b64_to_pil(b64: str) -> Image.Image:
    """Decode a base64 screenshot (data URI or raw) into a PIL image."""

    payload = b64.split(",")[-1]
    return Image.open(io.BytesIO(base64.b64decode(payload))).convert("RGB")


def embed_image_b64(b64: str) -> list[float]:
    """Return CLIP embedding for the provided screenshot."""

    if _img_model is None:
        return [0.0] * 512
    image = b64_to_pil(b64)
    emb = _img_model.encode([image])[0]
    return emb.astype("float32").tolist()


def maybe_embed_image(b64: str | None) -> list[float]:
    """Embed screenshot when available; otherwise return zero vector."""

    return embed_image_b64(b64) if b64 else [0.0] * 512
