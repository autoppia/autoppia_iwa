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
    DataExtractionUseCaseDefinition(name="FIND_PROJECTS", description="Find project information from AutoList data."),
    DataExtractionUseCaseDefinition(name="FIND_TEAMS", description="Find team information from AutoList data."),
    DataExtractionUseCaseDefinition(name="FIND_CHAT", description="Find chat/channel information from AutoList data."),
    DataExtractionUseCaseDefinition(name="FIND_TASK", description="Find a task from AutoList data."),
]

CASE_CONFIGS: dict[str, DataExtractionCaseConfig] = {
    "FIND_PROJECTS": DataExtractionCaseConfig(
        answer_keys=("project", "project_name", "workspace", "name"),
        identifier_keys=("team", "team_name", "priority", "date"),
        answer_label="project",
        entity_label="task record",
    ),
    "FIND_TEAMS": DataExtractionCaseConfig(
        answer_keys=("team", "team_name", "name"),
        identifier_keys=("project", "project_name", "priority", "date"),
        answer_label="team",
        entity_label="task record",
    ),
    "FIND_CHAT": DataExtractionCaseConfig(
        answer_keys=("chat", "channel", "conversation", "description"),
        identifier_keys=("project", "team", "name", "date"),
        answer_label="chat",
        entity_label="task record",
    ),
    "FIND_TASK": DataExtractionCaseConfig(
        answer_keys=("name", "task", "task_name"),
        identifier_keys=("project", "team", "priority", "date"),
        answer_label="task",
        entity_label="task record",
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
            project_id="autolist",
            task_url=task_url,
            seed=int(seed),
            use_case_name=definition.name,
            row=row,
            config=CASE_CONFIGS[definition.name],
        )
        if task:
            tasks.append(task)

    return tasks
