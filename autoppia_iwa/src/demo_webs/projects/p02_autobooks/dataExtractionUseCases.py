from __future__ import annotations

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.projects.data_extraction_use_cases_common import (
    DataExtractionCaseConfig,
    DataExtractionUseCaseDefinition,
    build_de_task,
    keep_non_empty_rows,
    normalize_selected_use_cases,
    pick_row,
)

from .data_utils import fetch_data

DATA_EXTRACTION_USE_CASES: list[DataExtractionUseCaseDefinition] = [
    DataExtractionUseCaseDefinition(name="FIND_BOOK", description="Find a book title from its identifying details."),
    DataExtractionUseCaseDefinition(name="FIND_AUTHOR", description="Find the author of a selected book."),
    DataExtractionUseCaseDefinition(name="FIND_PAGES", description="Find the page count of a selected book."),
    DataExtractionUseCaseDefinition(name="FIND_RATING", description="Find the rating of a selected book."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_BOOK": DataExtractionCaseConfig(
        answer_keys=("name", "title"),
        identifier_keys=("author", "year", "rating", "page_count", "genres"),
        answer_label="book title",
        entity_label="book",
    ),
    "FIND_AUTHOR": DataExtractionCaseConfig(
        answer_keys=("author",),
        identifier_keys=("name", "year", "rating", "page_count"),
        answer_label="author",
        entity_label="book",
    ),
    "FIND_PAGES": DataExtractionCaseConfig(
        answer_keys=("page_count", "pages"),
        identifier_keys=("name", "author", "year", "rating"),
        answer_label="number of pages",
        entity_label="book",
    ),
    "FIND_RATING": DataExtractionCaseConfig(
        answer_keys=("rating",),
        identifier_keys=("name", "author", "year"),
        answer_label="rating",
        entity_label="book",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    return await fetch_data(seed_value=int(seed), count=80)


async def generate_de_tasks(
    *,
    seed: int,
    task_url: str,
    selected_use_cases: set[str] | None = None,
) -> list[Task]:
    selected = normalize_selected_use_cases(selected_use_cases, DATA_EXTRACTION_USE_CASES)
    tasks: list[Task] = []

    for offset, definition in enumerate(DATA_EXTRACTION_USE_CASES, start=1):
        if definition.name not in selected:
            continue

        rows = keep_non_empty_rows(await _load_rows_for_use_case(seed=int(seed), use_case_name=definition.name))
        if not rows:
            continue

        row = pick_row(rows=rows, seed=int(seed), offset=offset)
        task = build_de_task(
            project_id="autobooks",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
