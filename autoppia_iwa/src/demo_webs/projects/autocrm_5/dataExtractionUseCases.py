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
    DataExtractionUseCaseDefinition(name="FIND_CLIENT", description="Find a client from CRM records."),
    DataExtractionUseCaseDefinition(name="FIND_BILLING", description="Find billing information from CRM logs."),
    DataExtractionUseCaseDefinition(name="FIND_MATTER", description="Find a matter from CRM records."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_CLIENT": DataExtractionCaseConfig(
        answer_keys=("name", "client"),
        identifier_keys=("email", "status", "matters", "last"),
        answer_label="client name",
        entity_label="client",
    ),
    "FIND_BILLING": DataExtractionCaseConfig(
        answer_keys=("hours", "status", "date"),
        identifier_keys=("client", "matter", "description"),
        answer_label="billing value",
        entity_label="billing log",
    ),
    "FIND_MATTER": DataExtractionCaseConfig(
        answer_keys=("name", "matter"),
        identifier_keys=("client", "status", "updated"),
        answer_label="matter name",
        entity_label="matter",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    if use_case_name == "FIND_CLIENT":
        return await fetch_data(
            entity_type="clients",
            method="distribute",
            filter_key="status",
            seed_value=int(seed),
            count=80,
        )
    if use_case_name == "FIND_BILLING":
        return await fetch_data(entity_type="logs", seed_value=int(seed), count=80)
    return await fetch_data(
        entity_type="matters",
        method="distribute",
        filter_key="status",
        seed_value=int(seed),
        count=80,
    )


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
            project_id="autocrm",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
