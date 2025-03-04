import base64
import random
import re
import string
from io import BytesIO
from typing import Dict, List

from PIL import Image

from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest


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


def assign_tests(test_configs: List[Dict]) -> List["BaseTaskTest"]:
    """
    Assigns and instantiates tests based on the provided test configurations.

    Args:
        test_configs (List[Dict]): A list of test configurations.

    Returns:
        List[BaseTaskTest]: A list of instantiated test objects.
    """
    from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot

    assigned_tests = []

    for config in test_configs:
        test_type = config.get("test_type")

        # Instantiate the appropriate class based on test_type and configuration
        if test_type == "frontend":
            if "keywords" in config:
                assigned_tests.append(FindInHtmlTest(**config))
            elif "name" in config:
                if config["name"] == "JudgeBaseOnHTML":
                    assigned_tests.append(JudgeBaseOnHTML(**config))
                elif config["name"] == "JudgeBaseOnScreenshot":
                    assigned_tests.append(JudgeBaseOnScreenshot(**config))
        elif test_type == "backend":
            if "event_type" in config:
                assigned_tests.append(CheckEventTest(**config))
        else:
            raise ValueError(f"Unsupported test configuration: {config}")

    return assigned_tests
