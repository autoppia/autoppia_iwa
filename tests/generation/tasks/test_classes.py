"""Unit tests for data_generation.tasks.classes (Task, TaskGenerationConfig, BrowserSpecification)."""

from autoppia_iwa.src.data_generation.tasks.classes import (
    BrowserSpecification,
    Task,
    TaskGenerationConfig,
)
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import UseCase


def test_browser_specification_defaults():
    spec = BrowserSpecification()
    assert spec.viewport_width == 1920
    assert spec.viewport_height == 1080
    assert spec.device_pixel_ratio == 1.0


def test_task_original_prompt_from_prompt():
    task = Task(url="https://example.com", prompt="Do something")
    assert task.original_prompt == "Do something"


def test_task_original_prompt_from_original_prompt_arg():
    task = Task(url="https://example.com", prompt="Short", original_prompt="Long original")
    assert task.original_prompt == "Long original"


def test_task_model_dump_hides_screenshot():
    task = Task(url="https://example.com", prompt="p", specifications=BrowserSpecification())
    dump = task.model_dump()
    if "screenshot" in dump:
        assert dump["screenshot"] == "None"


def test_task_model_dump_replaces_screenshot_with_placeholder():
    """Covers classes.py line 61: when dump contains screenshot (extra field), it is replaced with 'None'."""
    task = Task(url="https://example.com", prompt="p", screenshot="base64data")
    dump = task.model_dump()
    assert dump.get("screenshot") == "None"


def test_task_nested_model_dump_serializes_tests():
    task = Task(
        url="https://example.com",
        prompt="p",
        tests=[CheckEventTest(type="CheckEventTest", event_name="E1", event_criteria={}, description="d")],
    )
    nested = task.nested_model_dump()
    assert "tests" in nested
    assert len(nested["tests"]) == 1
    assert nested["tests"][0]["event_name"] == "E1"


def test_task_serialize_includes_original_prompt_and_use_case():
    """Serialize includes original_prompt and use_case with event name."""
    from autoppia_iwa.src.demo_webs.base_events import Event

    class FakeEvent(Event):
        event_name: str = "FAKE"

    use_case = UseCase(
        name="UC1",
        description="desc",
        event=FakeEvent,
        event_source_code="",
        examples=[],
    )
    task = Task(
        url="https://example.com",
        prompt="p",
        original_prompt="orig",
        use_case=use_case,
        tests=[CheckEventTest(type="CheckEventTest", event_name="E1", event_criteria={}, description="d")],
    )
    serialized = task.serialize()
    assert serialized["original_prompt"] == "orig"
    assert "use_case" in serialized
    assert serialized["use_case"]["name"] == "UC1"
    assert len(serialized["tests"]) == 1


def test_task_deserialize_roundtrip():
    task = Task(
        url="https://example.com/?a=1",
        prompt="p",
        tests=[CheckEventTest(type="CheckEventTest", event_name="E1", event_criteria={"k": "v"}, description="d")],
    )
    data = task.serialize()
    # Clear use_case for simple roundtrip (optional)
    data["use_case"] = None
    restored = Task.deserialize(data)
    assert restored.url == task.url
    assert restored.prompt == task.prompt
    assert len(restored.tests) == 1
    assert restored.tests[0].event_name == "E1"


def test_task_clean_task_excludes_tests_and_use_case():
    task = Task(
        url="https://example.com",
        prompt="p",
        tests=[CheckEventTest(type="CheckEventTest", event_name="E1", event_criteria={}, description="d")],
    )
    cleaned = task.clean_task()
    assert "tests" not in cleaned
    assert "use_case" not in cleaned
    assert cleaned["original_prompt"] == "p"
    assert "url" in cleaned
    assert "prompt" in cleaned


def test_task_assign_seed_to_url_adds_seed():
    task = Task(url="https://example.com/page", prompt="p")
    task.assign_seed_to_url(seed_value=42)
    assert "seed=42" in task.url


def test_task_assign_seed_to_url_existing_seed_unchanged():
    task = Task(url="https://example.com/?seed=99", prompt="p")
    task.assign_seed_to_url(seed_value=42)
    assert "seed=99" in task.url


def test_task_assign_seed_to_url_empty_url_no_op():
    task = Task(url="", prompt="p")
    task.assign_seed_to_url(seed_value=42)
    assert task.url == ""


def test_task_assign_seed_to_url_none_uses_random():
    task = Task(url="https://example.com/", prompt="p")
    task.assign_seed_to_url(seed_value=None)
    assert "seed=" in task.url
    # value should be in 1-999
    import re

    m = re.search(r"seed=(\d+)", task.url)
    assert m
    assert 1 <= int(m.group(1)) <= 999


def test_task_generation_config_prompts_per_use_case_int():
    config = TaskGenerationConfig(prompts_per_use_case=5, use_cases=["A"])
    assert config.prompts_per_use_case == 5
    assert config.use_cases == ["A"]
    assert config.dynamic is False


def test_task_assign_seed_to_url_exception_fallback():
    """Covers lines 146-150: when urlparse/parse_qs fails, seed is appended with ? or &."""
    from unittest.mock import patch

    task = Task(url="https://example.com/page", prompt="p")
    with patch("autoppia_iwa.src.data_generation.tasks.classes.urlparse", side_effect=Exception("parse error")):
        task.assign_seed_to_url(seed_value=100)
    assert "seed=100" in task.url


def test_task_serialize_drops_top_level_seed_legacy():
    """Seed is only in url; a legacy top-level seed key must not appear in output."""
    task = Task(url="https://example.com/?seed=77", prompt="p")
    assert "seed" not in task.serialize()


def test_task_deserialize_ignores_top_level_seed():
    data = {
        "url": "https://example.com/?seed=88",
        "prompt": "p",
        "tests": [],
        "use_case": None,
        "seed": 999,
    }
    restored = Task.deserialize(data)
    assert restored.url == "https://example.com/?seed=88"
    assert "seed" not in restored.serialize()
