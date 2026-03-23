"""Unit tests for web_voyager_utils (load_jsonl_file, generate_hash, TaskData)."""

import json

from autoppia_iwa.src.shared.web_voyager_utils import (
    TaskData,
    generate_hash,
    load_jsonl_file,
    load_real_tasks,
    setup_logging,
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


class TestSetupLogging:
    def test_setup_logging_calls_basic_config(self, monkeypatch):
        calls = {}

        def _fake_basic_config(*args, **kwargs):
            calls["args"] = args
            calls["kwargs"] = kwargs

        monkeypatch.setattr("autoppia_iwa.src.shared.web_voyager_utils.logging.basicConfig", _fake_basic_config)

        setup_logging()

        assert "kwargs" in calls
        assert calls["kwargs"]["level"] == 20  # logging.INFO
        assert isinstance(calls["kwargs"]["handlers"], list)
        assert len(calls["kwargs"]["handlers"]) == 1


class TestLoadRealTasks:
    def test_load_real_tasks_with_task_dict(self):
        task = {"url": "https://example.com", "prompt": "Do something"}
        result = load_real_tasks(task=task)
        assert len(result) == 1
        assert result[0].web == task["url"]
        assert result[0].ques == task["prompt"]
        assert result[0].web_name.startswith("custom_web_")

    def test_load_real_tasks_requires_params(self):
        import pytest

        with pytest.raises(ValueError, match="Either num_of_urls or by_indices"):
            load_real_tasks()

    def test_load_real_tasks_by_indices_filters_impossible_ids(self, monkeypatch, tmp_path):
        # Ensure dataset_dir selection prefers primary dir by creating expected file.
        base_dir = tmp_path / "base"
        primary_dir = base_dir / "entrypoints" / "judge_benchmark" / "web_voyager_tasks"
        primary_dir.mkdir(parents=True, exist_ok=True)
        (primary_dir / "web_voyager_data.jsonl").write_text("[]", encoding="utf-8")

        monkeypatch.setattr("autoppia_iwa.src.shared.web_voyager_utils.PROJECT_BASE_DIR", base_dir)

        original_tasks = [
            {"id": "a", "web": "u1", "ques": "q1", "web_name": "n1"},
            {"id": "b", "web": "u2", "ques": "q2", "web_name": "n2"},
        ]
        impossible_raw = ["b"]  # hashable -> set() works

        def _fake_load_jsonl_file(_path):
            # First call => original, second call => impossible list
            if not hasattr(_fake_load_jsonl_file, "i"):
                _fake_load_jsonl_file.i = 0  # type: ignore[attr-defined]
            _fake_load_jsonl_file.i += 1  # type: ignore[attr-defined]
            return original_tasks if _fake_load_jsonl_file.i == 1 else impossible_raw

        monkeypatch.setattr("autoppia_iwa.src.shared.web_voyager_utils.load_jsonl_file", _fake_load_jsonl_file)

        result = load_real_tasks(num_of_urls=10, by_indices=[0, 1])
        assert [t.id for t in result] == ["a"]

    def test_load_real_tasks_impossible_ids_typeerror_is_ignored(self, monkeypatch, tmp_path):
        base_dir = tmp_path / "base"
        primary_dir = base_dir / "entrypoints" / "judge_benchmark" / "web_voyager_tasks"
        primary_dir.mkdir(parents=True, exist_ok=True)
        (primary_dir / "web_voyager_data.jsonl").write_text("[]", encoding="utf-8")

        monkeypatch.setattr("autoppia_iwa.src.shared.web_voyager_utils.PROJECT_BASE_DIR", base_dir)

        original_tasks = [
            {"id": "a", "web": "u1", "ques": "q1", "web_name": "n1"},
            {"id": "b", "web": "u2", "ques": "q2", "web_name": "n2"},
        ]
        impossible_raw = [{"id": "a"}]  # unhashable dict -> set(impossible_raw) raises TypeError

        def _fake_load_jsonl_file(_path):
            if not hasattr(_fake_load_jsonl_file, "i"):
                _fake_load_jsonl_file.i = 0  # type: ignore[attr-defined]
            _fake_load_jsonl_file.i += 1  # type: ignore[attr-defined]
            return original_tasks if _fake_load_jsonl_file.i == 1 else impossible_raw

        monkeypatch.setattr("autoppia_iwa.src.shared.web_voyager_utils.load_jsonl_file", _fake_load_jsonl_file)

        # With impossible_ids ignored due to TypeError, by_indices should return both tasks.
        result = load_real_tasks(num_of_urls=10, by_indices=[0, 1])
        assert [t.id for t in result] == ["a", "b"]
