import base64
from io import BytesIO

import numpy as np
from PIL import Image


def b64jpeg_to_np(img_b64: str, w: int, h: int) -> np.ndarray:
    if not img_b64:
        return np.zeros((h, w, 3), dtype=np.uint8)
    raw = base64.b64decode(img_b64)
    img = Image.open(BytesIO(raw)).convert("RGB")
    if img.size != (w, h):
        img = img.resize((w, h))
    return np.asarray(img, dtype=np.uint8)
