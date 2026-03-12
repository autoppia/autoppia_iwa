"""Unit tests for web_voyager_utils (load_jsonl_file, generate_hash, TaskData)."""

import json

from autoppia_iwa.src.shared.web_voyager_utils import (
    TaskData,
    generate_hash,
    load_jsonl_file,
)


class TestLoadJsonlFile:
    """Tests for load_jsonl_file()."""

    def test_missing_file_returns_empty_list(self, tmp_path):
        path = tmp_path / "nonexistent.jsonl"
        assert not path.exists()
        result = load_jsonl_file(path)
        assert result == []

    def test_jsonl_file_parses_lines(self, tmp_path):
        path = tmp_path / "tasks.jsonl"
        path.write_text('{"id": "1", "name": "a"}\n{"id": "2", "name": "b"}\n', encoding="utf-8")
        result = load_jsonl_file(path)
        assert len(result) == 2
        assert result[0]["id"] == "1" and result[0]["name"] == "a"
        assert result[1]["id"] == "2" and result[1]["name"] == "b"

    def test_json_file_returns_single_object_or_list(self, tmp_path):
        path = tmp_path / "data.json"
        data = [{"id": "1"}, {"id": "2"}]
        path.write_text(json.dumps(data), encoding="utf-8")
        result = load_jsonl_file(path)
        assert result == data

    def test_invalid_json_line_skipped(self, tmp_path, caplog):
        path = tmp_path / "bad.jsonl"
        path.write_text('{"valid": true}\nnot json\n{"also": true}\n', encoding="utf-8")
        result = load_jsonl_file(path)
        assert len(result) == 2
        assert result[0]["valid"] is True
        assert result[1]["also"] is True

    def test_unsupported_suffix_returns_empty_list(self, tmp_path):
        path = tmp_path / "file.txt"
        path.write_text("hello", encoding="utf-8")
        result = load_jsonl_file(path)
        assert result == []


class TestGenerateHash:
    """Tests for generate_hash()."""

    def test_deterministic(self):
        s = "hello world"
        assert generate_hash(s) == generate_hash(s)

    def test_sha256_hex_length(self):
        h = generate_hash("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_inputs_different_hashes(self):
        assert generate_hash("a") != generate_hash("b")

    def test_empty_string(self):
        h = generate_hash("")
        assert len(h) == 64


class TestTaskData:
    """Tests for TaskData model."""

    def test_valid_task_data(self):
        t = TaskData(id="1", web="https://example.com", ques="Do something", web_name="example")
        assert t.id == "1"
        assert t.web == "https://example.com"
        assert t.ques == "Do something"
        assert t.web_name == "example"

    def test_model_dump_roundtrip(self):
        t = TaskData(id="x", web="u", ques="q", web_name="n")
        d = t.model_dump()
        t2 = TaskData(**d)
        assert t2.id == t.id and t2.web == t.web
