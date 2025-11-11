"""Fetch task + solution records from the leaderboard API."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional

import requests
from loguru import logger

DEFAULT_BASE_URL = "https://api-leaderboard.autoppia.com/api/v1/tasks/with-solutions"
DEFAULT_API_KEY = "AIagent2025"


def _as_query_bool(value: bool | None) -> str | None:
    if value is None:
        return None
    return "true" if value else "false"


@dataclass
class LeaderboardIngestConfig:
    """Configuration for leaderboard ingestion."""

    base_url: str = DEFAULT_BASE_URL
    api_key: str = DEFAULT_API_KEY
    websites: list[str] | None = field(default_factory=list)
    use_cases: list[str] | None = field(default_factory=list)
    miner_uids: list[int] | None = field(default_factory=list)
    success_states: list[bool | None] | None = field(default_factory=list)
    limit: int = 100
    pages_per_filter: int = 5
    sort: str = "created_at_desc"
    sleep_ms: int = 100
    timeout: float = 30.0
    max_records: int | None = None
    max_retries: int = 3
    retry_backoff: float = 1.5

    def filter_grid(self) -> list[dict[str, Any]]:
        websites = self.websites or [None]
        use_cases = self.use_cases or [None]
        success_states = self.success_states or [None]
        miner_uids = self.miner_uids or [None]
        combos: list[dict[str, Any]] = []
        for website in websites:
            for use_case in use_cases:
                for success in success_states:
                    for miner_uid in miner_uids:
                        combo: dict[str, Any] = {}
                        if website:
                            combo["website"] = website
                        if use_case:
                            combo["useCase"] = use_case
                        if success is not None:
                            combo["success"] = success
                        if miner_uid is not None:
                            combo["minerUid"] = miner_uid
                        combos.append(combo)
        return combos or [{}]


@dataclass
class LeaderboardRecord:
    """Single leaderboard response row plus metadata."""

    entry: dict[str, Any]
    filter_params: dict[str, Any]
    page: int
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LeaderboardClient:
    """Thin REST client around the leaderboard API."""

    def __init__(self, config: LeaderboardIngestConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "autoppia-score-model-pipeline",
            }
        )

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                resp = self.session.get(
                    self.config.base_url,
                    params=params,
                    timeout=self.config.timeout,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                last_exc = exc
                logger.warning(
                    "Leaderboard request failed (attempt {}/{}) :: {}",
                    attempt,
                    self.config.max_retries,
                    exc,
                )
                if attempt >= self.config.max_retries:
                    break
                sleep_seconds = self.config.retry_backoff** (attempt - 1)
                time.sleep(sleep_seconds)
        assert last_exc is not None
        raise last_exc

    def _iter_page(
        self,
        base_filters: dict[str, Any],
        page: int,
    ) -> list[dict[str, Any]]:
        params = {
            "key": self.config.api_key,
            "page": page,
            "limit": self.config.limit,
            "sort": self.config.sort,
        }
        if base_filters.get("website"):
            params["website"] = base_filters["website"]
        if base_filters.get("useCase"):
            params["useCase"] = base_filters["useCase"]
        if base_filters.get("minerUid") is not None:
            params["minerUid"] = base_filters["minerUid"]
        success_flag = base_filters.get("success")
        success_param = _as_query_bool(success_flag) if success_flag is not None else None
        if success_param is not None:
            params["success"] = success_param

        payload = self._request(params)
        data = payload.get("data") or {}
        tasks = data.get("tasks") or []
        limit = data.get("limit", self.config.limit)
        logger.info(
            "Fetched {} rows (page={} limit={} filters={})",
            len(tasks),
            page,
            limit,
            {k: v for k, v in params.items() if k not in {"key", "limit", "page", "sort"}},
        )
        return tasks

    def iter_records(self) -> Iterator[LeaderboardRecord]:
        total = 0
        for filter_params in self.config.filter_grid():
            for page in range(1, self.config.pages_per_filter + 1):
                rows = self._iter_page(filter_params, page)
                if not rows:
                    break
                for entry in rows:
                    yield LeaderboardRecord(entry=entry, filter_params=filter_params, page=page)
                    total += 1
                    if self.config.max_records and total >= self.config.max_records:
                        return
                if self.config.sleep_ms:
                    time.sleep(self.config.sleep_ms / 1000.0)
