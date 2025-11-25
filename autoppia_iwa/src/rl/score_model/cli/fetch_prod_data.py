#!/usr/bin/env python3
"""Fetch tasks and task solutions from the production API into local JSONL dumps."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Iterable, Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from requests import Response, Session


def _env_default(name: str, fallback: str | None = None) -> str | None:
    """Return environment variable or fallback value."""

    value = os.getenv(name)
    if value:
        return value
    return fallback


def _extract_list(payload: Any) -> list:
    """Try to extract a list of items from common API response shapes."""

    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []

    for key in ("results", "items", "data", "tasks"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def _next_page_hint(payload: Any) -> bool:
    """Return True if payload hints at more paginated results."""

    if not isinstance(payload, dict):
        return False
    for key in ("next", "has_next", "hasNext"):
        value = payload.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return bool(value)
        if isinstance(value, int | float):
            return value > 0
    return False


def _build_session(token: str | None, timeout: float, api_key: str | None, api_key_param: str) -> Session:
    session = requests.Session()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    session.headers.update(headers)
    if api_key:
        session.params = {api_key_param: api_key}  # type: ignore[attr-defined]
    session.timeout = timeout  # type: ignore[attr-defined]
    return session


def _request(session: Session, method: str, url: str, **kwargs) -> Response:
    resp = session.request(method, url, **kwargs)
    resp.raise_for_status()
    return resp


def iter_tasks(
    session: Session,
    base_url: str,
    statuses: Sequence[str],
    page_size: int,
    max_tasks: int | None,
    sleep_seconds: float,
) -> Iterator[dict[str, Any]]:
    """Yield tasks across statuses with generic page-based pagination."""

    total = 0
    for status in statuses:
        page = 1
        while True:
            params = {"status": status, "page": page, "page_size": page_size}
            url = f"{base_url.rstrip('/')}/tasks"
            resp = _request(session, "GET", url, params=params)
            payload = resp.json()
            items = _extract_list(payload)
            if not items:
                break
            for task in items:
                yield task
                total += 1
                if max_tasks is not None and total >= max_tasks:
                    return
            page += 1
            if not _next_page_hint(payload):
                break
            if sleep_seconds:
                time.sleep(sleep_seconds)


def iter_solutions_for_task(
    session: Session,
    base_url: str,
    task_id: str,
    page_size: int,
    max_pages: int | None,
    sleep_seconds: float,
) -> Iterator[dict[str, Any]]:
    """Yield all solutions for a given task id."""

    page = 1
    while True:
        params = {"page": page, "page_size": page_size}
        url = f"{base_url.rstrip('/')}/tasks/{task_id}/solutions"
        resp = _request(session, "GET", url, params=params)
        payload = resp.json()
        items = _extract_list(payload)
        if not items:
            break
        yield from items
        page += 1
        if max_pages is not None and page > max_pages:
            break
        if not _next_page_hint(payload):
            break
        if sleep_seconds:
            time.sleep(sleep_seconds)


def write_records(records: Iterable[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False))
            handle.write("\n")


def build_records(
    session: Session,
    base_url: str,
    statuses: Sequence[str],
    task_page_size: int,
    solution_page_size: int,
    max_tasks: int | None,
    max_solution_pages: int | None,
    sleep_seconds: float,
    include_empty: bool,
) -> Iterator[dict[str, Any]]:
    """Combine tasks and solutions into serialisable records."""

    for task in iter_tasks(session, base_url, statuses, task_page_size, max_tasks, sleep_seconds):
        task_id = task.get("id") or task.get("task_id")
        if not task_id:
            continue
        solutions = list(
            iter_solutions_for_task(
                session,
                base_url,
                task_id=str(task_id),
                page_size=solution_page_size,
                max_pages=max_solution_pages,
                sleep_seconds=sleep_seconds,
            )
        )
        if not solutions and not include_empty:
            continue
        yield {
            "task": task,
            "solutions": solutions,
            "fetched_at": datetime.now(UTC).isoformat(),
        }


def parse_statuses(raw: Sequence[str]) -> list[str]:
    statuses: list[str] = []
    for chunk in raw:
        statuses.extend(part.strip() for part in chunk.split(",") if part.strip())
    return statuses or ["done"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download tasks/solutions from production API.")
    parser.add_argument("--base-url", default=_env_default("AUTOPPIA_PROD_BASE_URL"), help="API base URL (env AUTOPPIA_PROD_BASE_URL).")
    parser.add_argument("--token", default=_env_default("AUTOPPIA_PROD_API_TOKEN"), help="Optional Bearer token (env AUTOPPIA_PROD_API_TOKEN).")
    parser.add_argument("--api-key", default=_env_default("AUTOPPIA_PROD_API_KEY"), help="Optional query-string API key (env AUTOPPIA_PROD_API_KEY).")
    parser.add_argument("--api-key-param", default="key", help="Query parameter name for --api-key (default: key).")
    parser.add_argument("--task-status", action="append", default=None, help="Task status filter(s). Repeat or comma-separate. Defaults to 'done'.")
    parser.add_argument("--task-page-size", type=int, default=100, help="Tasks page size.")
    parser.add_argument("--solution-page-size", type=int, default=100, help="Solutions page size.")
    parser.add_argument("--max-tasks", type=int, default=None, help="Optional limit on number of tasks to fetch.")
    parser.add_argument("--max-solution-pages", type=int, default=None, help="Optional limit on pages per task when listing solutions.")
    parser.add_argument("--sleep-ms", type=int, default=0, help="Optional delay between paginated requests.")
    parser.add_argument("--include-empty", action="store_true", help="Keep tasks that have zero solutions.")
    parser.add_argument("--output", type=Path, default=Path("data/inputs/reward_model/raw_evaluations/prod_tasks.jsonl"), help="Destination JSONL path.")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout per request.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.base_url:
        parser.error("--base-url (or AUTOPPIA_PROD_BASE_URL) is required.")

    statuses = parse_statuses(args.task_status or [])
    sleep_seconds = max(0.0, args.sleep_ms / 1000.0)

    session = _build_session(
        token=args.token,
        timeout=args.timeout,
        api_key=args.api_key,
        api_key_param=args.api_key_param,
    )
    records = build_records(
        session=session,
        base_url=args.base_url,
        statuses=statuses,
        task_page_size=args.task_page_size,
        solution_page_size=args.solution_page_size,
        max_tasks=args.max_tasks,
        max_solution_pages=args.max_solution_pages,
        sleep_seconds=sleep_seconds,
        include_empty=args.include_empty,
    )
    write_records(records, args.output)
    print(f"[fetch_prod_data] wrote dataset to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
