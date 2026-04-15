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
    DataExtractionUseCaseDefinition(name="FIND_SENDER", description="Find the sender of an email."),
    DataExtractionUseCaseDefinition(name="FIND_SUBJECT", description="Find the subject of an email."),
    DataExtractionUseCaseDefinition(name="FIND_TEMPLATE", description="Find an email template."),
    DataExtractionUseCaseDefinition(name="FIND_LABEL", description="Find the label of an email."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_SENDER": DataExtractionCaseConfig(
        answer_keys=("from_name", "from_email", "sender"),
        identifier_keys=("subject", "label_name", "date"),
        answer_label="sender",
        entity_label="email",
    ),
    "FIND_SUBJECT": DataExtractionCaseConfig(
        answer_keys=("subject",),
        identifier_keys=("from_name", "from_email", "label_name", "date"),
        answer_label="subject",
        entity_label="email",
    ),
    "FIND_TEMPLATE": DataExtractionCaseConfig(
        answer_keys=("name", "template_name", "subject"),
        identifier_keys=("subject", "body"),
        answer_label="template",
        entity_label="template",
    ),
    "FIND_LABEL": DataExtractionCaseConfig(
        answer_keys=("label_name", "name"),
        identifier_keys=("subject", "from_name", "from_email"),
        answer_label="label",
        entity_label="email",
    ),
}


async def _load_rows_for_use_case(*, seed: int, use_case_name: str) -> list[dict]:
    if use_case_name == "FIND_TEMPLATE":
        try:
            rows = await fetch_data(
                seed_value=int(seed),
                count=50,
                entity_type="templates",
                method="select",
            )
        except Exception:
            rows = []
        if rows:
            return rows
    return await fetch_data(
        seed_value=int(seed),
        count=80,
        entity_type="emails",
        method="distribute",
        filter_key="category",
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
            project_id="automail",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
