import base64
import random
import re
import string
from io import BytesIO

from PIL import Image


def generate_random_web_agent_id(length: int = 16) -> str:
    """
    Generates a random alphanumeric string for the web_agent ID.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))


def extract_json_in_markdown(text: str) -> str:
    """
    Extract the first fenced code block (```json ... ``` or just ``` ... ```).
    If none is found, return text.strip() as a fallback.
    """
    pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def transform_image_into_base64(image: Image.Image) -> str:
    """
    Converts a PIL Image into a base64 encoded string.

    Args:
        image (Image.Image): The image to be converted.

    Returns:
        str: The base64 encoded string of the image.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64
