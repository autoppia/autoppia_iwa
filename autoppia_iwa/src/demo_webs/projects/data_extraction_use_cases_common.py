from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest


@dataclass(frozen=True)
class DataExtractionUseCaseDefinition:
    name: str
    description: str


@dataclass(frozen=True)
class DataExtractionCaseConfig:
    answer_keys: tuple[str, ...]
    identifier_keys: tuple[str, ...] = ()
    answer_label: str | None = None
    entity_label: str | None = None


def pick_row(*, rows: list[dict[str, Any]], seed: int, offset: int) -> dict[str, Any]:
    idx = abs((int(seed) * 131) + (offset * 17)) % len(rows)
    return rows[idx]


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list | tuple | set | dict):
        return len(value) == 0
    return False


def _scalarize(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, int | float | bool):
        return str(value)
    if isinstance(value, dict):
        for key in ("name", "title", "label", "value", "text", "email", "id", "earnings", "price", "rate", "amount", "hours", "jobs"):
            if key in value:
                nested = _scalarize(value.get(key))
                if nested:
                    return nested
        return None
    if isinstance(value, list | tuple | set):
        for item in value:
            nested = _scalarize(item)
            if nested:
                return nested
        return None
    return None


def extract_value_from_row(row: dict[str, Any], keys: tuple[str, ...]) -> tuple[str | None, str | None]:
    for key in keys:
        if key not in row:
            continue
        scalar = _scalarize(row.get(key))
        if scalar:
            return key, scalar
    return None, None


def pick_identifiers(
    *,
    row: dict[str, Any],
    preferred_keys: tuple[str, ...],
    excluded_keys: set[str],
    max_pairs: int = 3,
) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add_pair(key: str, value: Any) -> None:
        if key in seen or key in excluded_keys:
            return
        scalar = _scalarize(value)
        if not scalar:
            return
        seen.add(key)
        pairs.append((key, scalar))

    for key in preferred_keys:
        if key in row:
            add_pair(key, row.get(key))
            if len(pairs) >= max_pairs:
                return pairs

    for key, value in row.items():
        add_pair(key, value)
        if len(pairs) >= max_pairs:
            break

    return pairs


def _humanize(key: str) -> str:
    return str(key or "value").replace("_", " ").strip()


def build_question(*, entity_label: str, answer_label: str, identifiers: list[tuple[str, str]]) -> str:
    if not identifiers:
        return f"What is the {answer_label} for this {entity_label}?"

    clauses = [f"{_humanize(key)} is '{value}'" for key, value in identifiers]
    constraints = " and ".join(clauses)
    return f"For the {entity_label} where {constraints}, what is the {answer_label}?"


def build_de_task(
    *,
    project_id: str,
    task_url: str,
    seed: int,
    use_case_name: str,
    row: dict[str, Any],
    config: DataExtractionCaseConfig,
) -> Task | None:
    answer_key, answer_value = extract_value_from_row(row, config.answer_keys)
    if not answer_key or not answer_value:
        return None

    identifier_pairs = pick_identifiers(
        row=row,
        preferred_keys=config.identifier_keys,
        excluded_keys={answer_key},
        max_pairs=3,
    )

    question = build_question(
        entity_label=config.entity_label or "record",
        answer_label=config.answer_label or _humanize(answer_key),
        identifiers=identifier_pairs,
    )

    task = Task(
        web_project_id=project_id,
        url=task_url,
        prompt=question,
        tests=[DataExtractionTest(expected_answer=answer_value)],
    )
    task.assign_seed_to_url(seed_value=int(seed))
    task.de_use_case_name = use_case_name
    task.task_type = "DEtask"
    task.de_expected_answer = answer_value
    return task


def normalize_selected_use_cases(
    selected_use_cases: set[str] | None,
    definitions: list[DataExtractionUseCaseDefinition],
) -> set[str]:
    if not selected_use_cases:
        return {item.name for item in definitions}
    return {name.strip().upper() for name in selected_use_cases if str(name).strip()}


def keep_non_empty_rows(rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not rows:
        return []
    return [row for row in rows if isinstance(row, dict) and any(not _is_empty(value) for value in row.values())]
