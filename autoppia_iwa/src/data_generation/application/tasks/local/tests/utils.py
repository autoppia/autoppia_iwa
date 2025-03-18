import re
from typing import Any


def normalize_test_config(test_config: dict[str, Any]) -> dict[str, Any]:
    """
    Converts LLM-produced test_config (with nested 'fields') into a flattened structure.
    """
    # Get the original test type
    raw_test_type = test_config.get("test_type")

    # Flatten the 'fields' dictionary into the main dictionary
    if "fields" in test_config and isinstance(test_config["fields"], dict):
        fields = test_config.pop("fields")
        test_config.update(fields)

    # Remap test_type based on a predefined mapping
    test_type_mapping = {
        "FindInHtmlTest": "frontend",
        "CheckEventTest": "backend",
        "JudgeBaseOnHTML": "frontend",
        "OpinionBaseOnScreenshot": "frontend",
        "CheckUrlTest": "frontend",
    }

    if raw_test_type in test_type_mapping:
        test_config["test_type"] = test_type_mapping[raw_test_type]
        # Optionally set a name for specific test types
        if raw_test_type in ["JudgeBaseOnHTML", "OpinionBaseOnScreenshot"]:
            test_config["name"] = raw_test_type


def extract_domain(url: str) -> str:
    """Extract domain from a full URL."""
    if not url:
        return ""
    pattern = re.compile(r"https?://([^/]+)")
    match = pattern.match(url)
    return match.group(1).lower() if match else ""
