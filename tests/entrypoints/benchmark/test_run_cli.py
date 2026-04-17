from __future__ import annotations

from autoppia_iwa.entrypoints.benchmark import run


def test_build_config_without_args_uses_run_py_defaults():
    cfg = run.build_config()

    assert [p.id for p in cfg.projects] == run.PROJECT_IDS
    assert cfg.use_cases == run.USE_CASES
    assert cfg.data_extraction_use_cases == run.DATA_EXTRACTION_USE_CASES
    assert cfg.enable_event_tasks is True
    assert cfg.enable_data_extraction_tasks is True


def test_cli_event_only_enables_only_event_pipeline():
    args = run.parse_args(
        [
            "-t",
            "event_only",
            "-p",
            "autocinema",
            "-u",
            "FIND_MOVIE",
        ]
    )

    cfg = run.build_config(args)

    assert [p.id for p in cfg.projects] == ["autocinema"]
    assert cfg.use_cases == ["FIND_MOVIE"]
    assert cfg.enable_event_tasks is True
    assert cfg.enable_data_extraction_tasks is False


def test_cli_data_extraction_only_enables_only_de_pipeline_with_legacy_alias():
    args = run.parse_args(
        [
            "--test",
            "data_extraction_only",
            "-p",
            "autocinema",
            "-d",
            "EXTRACT_MOVIES",
        ]
    )

    cfg = run.build_config(args)

    assert [p.id for p in cfg.projects] == ["autocinema"]
    assert cfg.data_extraction_use_cases == ["EXTRACT_MOVIES"]
    assert cfg.enable_event_tasks is False
    assert cfg.enable_data_extraction_tasks is True
