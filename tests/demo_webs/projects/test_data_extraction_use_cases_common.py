from __future__ import annotations

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest
from autoppia_iwa.src.demo_webs.projects import data_extraction_use_cases_common as common


def test_extract_value_and_pick_identifiers_and_question_helpers():
    row = {
        "name": "Interstellar",
        "director": "Christopher Nolan",
        "year": 2014,
        "rating": 8.7,
        "genres": ["Sci-Fi", "Drama"],
    }

    answer_key, answer_value = common.extract_value_from_row(row, ("title", "name"))
    assert answer_key == "name"
    assert answer_value == "Interstellar"

    identifiers = common.pick_identifiers(
        row=row,
        preferred_keys=("director", "year"),
        excluded_keys={"name"},
        max_pairs=3,
    )
    assert identifiers
    assert identifiers[0][0] == "director"

    question = common.build_question(
        entity_label="movie",
        answer_label="director",
        identifiers=identifiers,
    )
    assert "movie" in question
    assert "director" in question


def test_build_de_task_success_sets_expected_fields():
    row = {
        "name": "Up",
        "director": "Pete Docter",
        "year": 2009,
        "rating": 8.3,
    }
    config = common.DataExtractionCaseConfig(
        answer_keys=("director",),
        identifier_keys=("name", "year"),
        answer_label="director",
        entity_label="movie",
    )

    task = common.build_de_task(
        project_id="autocinema",
        task_url="http://localhost:8000",
        seed=7,
        use_case_name="FIND_DIRECTOR",
        row=row,
        config=config,
    )

    assert isinstance(task, Task)
    assert task.web_project_id == "autocinema"
    assert "seed=7" in task.url
    assert task.de_use_case_name == "FIND_DIRECTOR"
    assert task.de_expected_answer == "Pete Docter"
    assert task.task_type == "DEtask"
    assert len(task.tests) == 1
    assert isinstance(task.tests[0], DataExtractionTest)
    assert task.tests[0].expected_answer == "Pete Docter"


def test_build_de_task_returns_none_when_answer_missing():
    row = {"name": "Only Name"}
    config = common.DataExtractionCaseConfig(
        answer_keys=("director",),
        identifier_keys=("name",),
    )

    task = common.build_de_task(
        project_id="autocinema",
        task_url="http://localhost:8000",
        seed=1,
        use_case_name="FIND_DIRECTOR",
        row=row,
        config=config,
    )

    assert task is None


def test_normalize_and_keep_non_empty_rows_and_pick_row():
    defs = [
        common.DataExtractionUseCaseDefinition(name="FIND_A", description="A"),
        common.DataExtractionUseCaseDefinition(name="FIND_B", description="B"),
    ]

    selected_all = common.normalize_selected_use_cases(None, defs)
    assert selected_all == {"FIND_A", "FIND_B"}

    selected_subset = common.normalize_selected_use_cases({" find_a "}, defs)
    assert selected_subset == {"FIND_A"}

    rows = common.keep_non_empty_rows(
        [
            {},
            {"name": ""},
            {"name": "valid"},
            None,
            {"count": 0},
        ]
    )
    assert {"name": "valid"} in rows
    assert {"count": 0} in rows

    picked = common.pick_row(rows=[{"x": 1}, {"x": 2}, {"x": 3}], seed=2, offset=1)
    assert picked in [{"x": 1}, {"x": 2}, {"x": 3}]
