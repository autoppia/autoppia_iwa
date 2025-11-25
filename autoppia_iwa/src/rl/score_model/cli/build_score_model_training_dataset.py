#!/usr/bin/env python3
"""Build a score-model dataset directly from the leaderboard API."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from loguru import logger

from ..pipeline import paths
from ..pipeline.data_preparation import (
    LeaderboardClient,
    LeaderboardDatasetBuilder,
    LeaderboardIngestConfig,
    LeaderboardRecord,
)


def _write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def _parse_success_flags(values: Sequence[str] | None) -> list[bool | None]:
    if not values:
        return [True, False]
    mapping = {"true": True, "false": False, "all": None}
    parsed: list[bool | None] = []
    for chunk in values:
        lowered = chunk.strip().lower()
        if lowered not in mapping:
            raise ValueError(f"Unknown --success value '{chunk}'. Use true, false, or all.")
        parsed.append(mapping[lowered])
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://api-leaderboard.autoppia.com/api/v1/tasks/with-solutions", help="Leaderboard endpoint base URL.")
    parser.add_argument("--api-key", default="AIagent2025", help="API key query parameter.")
    parser.add_argument("--website", action="append", default=None, help="Website filter (repeatable).")
    parser.add_argument("--use-case", action="append", default=None, help="Use case filter (repeatable).")
    parser.add_argument("--miner-uid", action="append", type=int, default=None, help="Miner UID filter (repeatable).")
    parser.add_argument("--success", action="append", help="Success filter true/false/all. Defaults to both true and false.")
    parser.add_argument("--pages-per-filter", type=int, default=5, help="Pages to iterate per filter combination.")
    parser.add_argument("--limit", type=int, default=200, help="Page size (<=500).")
    parser.add_argument("--sort", default="created_at_desc", help="Sort order (see API docs).")
    parser.add_argument("--sleep-ms", type=int, default=100, help="Delay between page requests.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout.")
    parser.add_argument("--max-records", type=int, default=None, help="Optional cap on total rows fetched.")
    parser.add_argument("--dedupe-strategy", choices=["task_solution", "task_agent", "task"], default="task_solution", help="How to deduplicate samples.")
    parser.add_argument("--output-prefix", default=None, help="Optional manual prefix for output files.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    success_flags = _parse_success_flags(args.success)

    config = LeaderboardIngestConfig(
        base_url=args.base_url,
        api_key=args.api_key,
        websites=args.website,
        use_cases=args.use_case,
        miner_uids=args.miner_uid,
        success_states=success_flags,
        limit=args.limit,
        pages_per_filter=args.pages_per_filter,
        sort=args.sort,
        sleep_ms=args.sleep_ms,
        timeout=args.timeout,
        max_records=args.max_records,
    )

    client = LeaderboardClient(config)
    records: list[LeaderboardRecord] = list(client.iter_records())
    logger.info("Fetched {} total raw rows from leaderboard API.", len(records))

    builder = LeaderboardDatasetBuilder(dedupe_strategy=args.dedupe_strategy)
    samples = builder.build(records)
    summary = builder.summarize(samples)
    summary.update(
        {
            "raw_rows": len(records),
            "dedupe_strategy": args.dedupe_strategy,
            "filters": config.filter_grid(),
        }
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    prefix = args.output_prefix or f"leaderboard_{timestamp}"
    raw_path = paths.RAW_DIR / f"{prefix}.jsonl"
    dataset_path = paths.DATASETS_DIR / f"{prefix}.jsonl"
    metrics_path = paths.METRICS_DIR / f"{prefix}.json"

    _write_jsonl(
        raw_path,
        (
            {
                "entry": record.entry,
                "filters": record.filter_params,
                "page": record.page,
                "fetched_at": record.fetched_at,
            }
            for record in records
        ),
    )
    _write_jsonl(dataset_path, (sample.to_dict() for sample in samples))
    summary["output_files"] = {
        "raw": str(raw_path),
        "dataset": str(dataset_path),
        "metrics": str(metrics_path),
    }
    summary["config"] = asdict(config)
    _write_json(metrics_path, summary)

    logger.info("Wrote {} samples to {}", len(samples), dataset_path)
    logger.info("Summary written to {}", metrics_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
