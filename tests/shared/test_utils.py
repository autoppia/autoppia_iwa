"""Unit tests for shared utils (e.g. generate_random_web_agent_id)."""

import re

from autoppia_iwa.src.shared.utils import generate_random_web_agent_id


class TestGenerateRandomWebAgentId:
    """Tests for generate_random_web_agent_id()."""

    def test_default_length_is_16(self):
        result = generate_random_web_agent_id()
        assert len(result) == 16

    def test_custom_length(self):
        result = generate_random_web_agent_id(length=8)
        assert len(result) == 8

    def test_only_alphanumeric(self):
        result = generate_random_web_agent_id(length=32)
        assert re.match(r"^[A-Za-z0-9]+$", result), "should contain only letters and digits"

    def test_different_calls_give_different_ids(self):
        ids = [generate_random_web_agent_id(length=24) for _ in range(10)]
        assert len(set(ids)) == 10, "each call should produce a different value (with high probability)"

    def test_length_zero(self):
        result = generate_random_web_agent_id(length=0)
        assert result == ""
