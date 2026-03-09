"""Unit tests for llms.utils (OpenAIUtilsMixin)."""

from autoppia_iwa.src.llms.utils import OpenAIUtilsMixin


class TestOpenAIUtilsMixin:
    def test_num_tokens_from_string_empty(self):
        n = OpenAIUtilsMixin.num_tokens_from_string("")
        assert n == 0

    def test_num_tokens_from_string_short(self):
        n = OpenAIUtilsMixin.num_tokens_from_string("hello")
        assert n >= 1

    def test_num_tokens_from_string_with_disallowed_special_false(self):
        n = OpenAIUtilsMixin.num_tokens_from_string("hello", disallowed_special=False)
        assert n >= 1

    def test_num_tokens_from_string_different_model(self):
        n = OpenAIUtilsMixin.num_tokens_from_string("test", model="gpt-4o-mini")
        assert n >= 1
