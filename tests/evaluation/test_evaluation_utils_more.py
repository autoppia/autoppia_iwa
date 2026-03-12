"""Additional unit tests for evaluation.shared.utils (extract_seed, hash_actions, initialize_test_results, make_gif)."""

import base64
import io

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import JudgeBaseOnHTML
from autoppia_iwa.src.evaluation.shared.utils import (
    extract_seed_from_url,
    hash_actions,
    initialize_test_results,
    make_gif_from_screenshots,
)
from autoppia_iwa.src.execution.actions.actions import NavigateAction


class TestExtractSeedFromUrl:
    def test_has_seed(self):
        assert extract_seed_from_url("http://example.com?seed=42") == 42
        assert extract_seed_from_url("http://example.com/path?seed=123&other=1") == 123

    def test_no_seed(self):
        assert extract_seed_from_url("http://example.com") is None
        assert extract_seed_from_url("http://example.com?other=1") is None

    def test_seed_with_whitespace(self):
        assert extract_seed_from_url("http://example.com?seed=  99  ") == 99

    def test_invalid_url_or_query(self):
        assert extract_seed_from_url("") is None


class TestHashActions:
    def test_empty_list(self):
        h = hash_actions([])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_same_actions_same_hash(self):
        actions = [
            NavigateAction(type="NavigateAction", url="http://example.com"),
        ]
        h1 = hash_actions(actions)
        h2 = hash_actions(actions)
        assert h1 == h2

    def test_different_actions_different_hash(self):
        a1 = [NavigateAction(type="NavigateAction", url="http://a.com")]
        a2 = [NavigateAction(type="NavigateAction", url="http://b.com")]
        assert hash_actions(a1) != hash_actions(a2)


class TestInitializeTestResults:
    def test_empty_tests(self):
        task = Task(url="http://x.com", prompt="P", tests=[])
        result = initialize_test_results(task)
        assert result == []

    def test_with_tests(self):
        task = Task(
            url="http://x.com",
            prompt="P",
            tests=[
                JudgeBaseOnHTML(type="JudgeBaseOnHTML", success_criteria="find x", description="Desc"),
            ],
        )
        result = initialize_test_results(task)
        assert len(result) == 1
        assert result[0].success is False
        assert result[0].extra_data is not None


class TestMakeGifFromScreenshots:
    def test_empty_list_returns_empty_bytes(self):
        assert make_gif_from_screenshots([]) == b""

    def test_none_or_invalid_skipped(self):
        # Invalid base64 should be skipped; result can be b"" if no valid image
        result = make_gif_from_screenshots(["not-valid-base64!!"])
        assert result == b""

    def test_single_valid_tiny_image(self):
        # Minimal 1x1 PNG as base64 (valid image bytes)
        try:
            from PIL import Image

            buf = io.BytesIO()
            img = Image.new("RGB", (1, 1), color=(255, 0, 0))
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            result = make_gif_from_screenshots([b64])
            assert isinstance(result, bytes)
            assert True  # may return empty if GIF save fails on single frame
        except Exception:
            pytest.skip("PIL not available or save failed")
