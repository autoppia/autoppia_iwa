from __future__ import annotations

import asyncio
import json
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import urljoin, urlsplit, urlunsplit

from loguru import logger
from playwright.async_api import Browser, Page, async_playwright

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.execution.dynamic.executor import DynamicPhaseConfig, DynamicPlaywrightExecutor, MutationAuditRecord
from autoppia_iwa.src.llms.interfaces import ILLM, LLMConfig
from autoppia_iwa.src.llms.service import LLMFactory


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"https?://", "", value)
    value = value.replace("?", "_").replace("=", "_").replace("&", "_")
    value = re.sub(r"[^a-z0-9._/-]+", "_", value)
    return value[:80] or "home"


def _attach_seed(url: str, seed: int | None) -> str:
    if seed is None:
        return url
    if "seed=" in url:
        return url
    join = "&" if "?" in url else "?"
    return f"{url}{join}seed={seed}"


def _normalize_url(base_url: str, href: str) -> str:
    if href.startswith(("http://", "https://")):
        return href
    return urljoin(base_url, href)


async def _discover_routes(page: Page, start_url: str, max_pages: int) -> list[str]:
    origin = urlsplit(start_url)
    origin_netloc = origin.netloc
    pending = [start_url]
    seen: set[str] = set()
    discovered: list[str] = []

    while pending and len(discovered) < max_pages:
        url = pending.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            continue
        discovered.append(url)
        anchors = await page.eval_on_selector_all("a[href]", "els => els.map(a => a.href)")
        for href in anchors:
            normalized = _normalize_url(start_url, href)
            parsed = urlsplit(normalized)
            if parsed.netloc and parsed.netloc != origin_netloc:
                continue
            normalized = urlunsplit((origin.scheme, origin.netloc, parsed.path, parsed.query, parsed.fragment))
            if normalized in seen or normalized in pending:
                continue
            if len(discovered) + len(pending) >= max_pages:
                continue
            pending.append(normalized)
    return discovered


@dataclass
class DynamicAuditOptions:
    output_dir: Path
    browser_name: str = "chromium"
    headless: bool = True
    max_pages: int = 8
    passes_per_url: int = 2
    wait_after_ms: int = 750
    navigation_timeout_ms: int = 60000
    record_timeout_s: float = 6.0
    seeds: list[int] = field(default_factory=lambda: [0])
    project_ids: set[str] | None = None
    enable_d1: bool = True
    enable_d3: bool = True
    enable_d4: bool = False
    instruction_cache_size: int = 32
    html_similarity_threshold: float = 0.95
    llm_service: ILLM | None = None
    llm_sample_size: int = 0
    llm_summary_max_chars: int = 2000
    palette_dir: Path | None = None


@dataclass
class SummaryEntry:
    record_id: str
    project_id: str
    url: str
    seed: int
    run_index: int
    plan_source: str
    plan_duration_ms: float
    mutation_duration_ms: float
    navigation_duration_ms: float
    delta_bytes: int
    cache_key: str | None
    phases: dict[str, bool]
    metrics: dict[str, int]
    before_path: str
    after_path: str
    plan_path: str

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "project_id": self.project_id,
            "url": self.url,
            "seed": self.seed,
            "run_index": self.run_index,
            "plan_source": self.plan_source,
            "plan_duration_ms": self.plan_duration_ms,
            "mutation_duration_ms": self.mutation_duration_ms,
            "navigation_duration_ms": self.navigation_duration_ms,
            "delta_bytes": self.delta_bytes,
            "cache_key": self.cache_key,
            "phases": self.phases,
            "metrics": self.metrics,
            "before_path": self.before_path,
            "after_path": self.after_path,
            "plan_path": self.plan_path,
        }


class MutationCapture:
    def __init__(self):
        self._pending_future: asyncio.Future | None = None
        self._pending_url: str | None = None
        self.latest_record: MutationAuditRecord | None = None

    def expect(self, url: str) -> asyncio.Future:
        if self._pending_future and not self._pending_future.done():
            raise RuntimeError("Pending capture already in progress")
        loop = asyncio.get_running_loop()
        self._pending_future = loop.create_future()
        self._pending_url = url
        return self._pending_future

    def handle_record(self, record: MutationAuditRecord) -> None:
        self.latest_record = record
        if self._pending_future and not self._pending_future.done():
            expected = self._pending_url or ""
            if record.url.rstrip("/") == expected.rstrip("/"):
                self._pending_future.set_result(record)


class DatasetWriter:
    def __init__(self, root: Path, project_id: str, seed: int):
        self.root = root
        self.project_id = project_id
        self.seed = seed
        self.dataset_dir = self.root / project_id / f"seed_{seed}"
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0
        self.summary: list[SummaryEntry] = []

    def write(self, record: MutationAuditRecord, nav_ms: float, run_index: int) -> SummaryEntry:
        self._counter += 1
        slug = _slugify(record.url)
        base_name = f"{self._counter:03d}_{slug}_run{run_index}"
        before_path = self.dataset_dir / f"{base_name}_before.html"
        after_path = self.dataset_dir / f"{base_name}_after.html"
        plan_path = self.dataset_dir / f"{base_name}_plan.json"
        before_path.parent.mkdir(parents=True, exist_ok=True)
        before_path.write_text(record.html_before, encoding="utf-8")
        after_path.parent.mkdir(parents=True, exist_ok=True)
        after_path.write_text(record.html_after, encoding="utf-8")
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps(record.plan, ensure_ascii=False, indent=2), encoding="utf-8")

        summary = SummaryEntry(
            record_id=f"{self.project_id}-{self.seed}-{self._counter}-{run_index}",
            project_id=self.project_id,
            url=record.url,
            seed=record.seed,
            run_index=run_index,
            plan_source=record.plan_source,
            plan_duration_ms=record.plan_duration_ms,
            mutation_duration_ms=record.mutation_duration_ms,
            navigation_duration_ms=nav_ms,
            delta_bytes=record.delta_bytes,
            cache_key=record.cache_key,
            phases=record.phases,
            metrics=record.metrics,
            before_path=str(before_path.relative_to(self.root)),
            after_path=str(after_path.relative_to(self.root)),
            plan_path=str(plan_path.relative_to(self.root)),
        )
        self.summary.append(summary)
        return summary


def _select_projects(project_ids: set[str] | None) -> list[WebProject]:
    if not project_ids:
        return list(demo_web_projects)
    wanted = {pid.lower() for pid in project_ids}
    return [project for project in demo_web_projects if project.id.lower() in wanted]


async def _discover_urls(playwright, browser_name: str, headless: bool, start_url: str, max_pages: int) -> list[str]:
    browser_launcher = getattr(playwright, browser_name)
    browser: Browser = await browser_launcher.launch(headless=headless)
    page: Page = await browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        urls = await _discover_routes(page, start_url, max_pages)
        return urls
    finally:
        await browser.close()


async def _run_seed_capture(
    playwright,
    options: DynamicAuditOptions,
    project: WebProject,
    seed: int,
    urls: Sequence[str],
    writer: DatasetWriter,
) -> list[SummaryEntry]:
    browser_launcher = getattr(playwright, options.browser_name)
    browser: Browser = await browser_launcher.launch(headless=options.headless)
    page: Page = await browser.new_page(viewport={"width": 1440, "height": 900})
    capture = MutationCapture()
    phase_config = DynamicPhaseConfig(
        enable_d1_structure=options.enable_d1,
        enable_d3_attributes=options.enable_d3,
        enable_d4_overlays=options.enable_d4,
        instruction_cache_size=options.instruction_cache_size,
        html_similarity_threshold=options.html_similarity_threshold,
        palette_dir=str(options.palette_dir) if options.palette_dir else None,
    )
    executor = DynamicPlaywrightExecutor(
        browser_config=BrowserSpecification(),
        page=page,
        backend_demo_webs_service=None,
        dynamic_config=phase_config,
        project_id=project.id,
        seed=seed,
        audit_callback=capture.handle_record,
    )
    await executor._ensure_route()

    collected: list[SummaryEntry] = []
    for url in urls:
        target_url = _attach_seed(url, seed)
        for run_idx in range(options.passes_per_url):
            future = capture.expect(target_url)
            nav_start = time.perf_counter()
            try:
                await page.goto(target_url, wait_until="networkidle", timeout=options.navigation_timeout_ms)
                await page.wait_for_timeout(options.wait_after_ms)
            except Exception as exc:  # pragma: no cover - diagnostics only
                logger.warning(f"[{project.id}] navigation failed for {target_url}: {exc}")
                if not future.done():
                    future.cancel()
                break
            nav_ms = (time.perf_counter() - nav_start) * 1000
            try:
                record: MutationAuditRecord = await asyncio.wait_for(future, timeout=options.record_timeout_s)
            except asyncio.TimeoutError:  # pragma: no cover - diagnostics only
                logger.warning(f"[{project.id}] timed out waiting for audit record on {target_url}")
                continue
            summary = writer.write(record, nav_ms, run_idx)
            collected.append(summary)
    await browser.close()
    return collected


def _aggregate_metrics(entries: Iterable[SummaryEntry]) -> dict:
    totals: dict[str, dict[str, float | int]] = {}
    for entry in entries:
        project_stats = totals.setdefault(
            entry.project_id,
            {
                "count": 0,
                "avg_plan_duration_ms": 0.0,
                "avg_mutation_ms": 0.0,
                "avg_navigation_ms": 0.0,
                "plan_sources": {},
            },
        )
        project_stats["count"] += 1
        project_stats["avg_plan_duration_ms"] += entry.plan_duration_ms
        project_stats["avg_mutation_ms"] += entry.mutation_duration_ms
        project_stats["avg_navigation_ms"] += entry.navigation_duration_ms
        source_counts = project_stats["plan_sources"]
        source_counts[entry.plan_source] = source_counts.get(entry.plan_source, 0) + 1

    for stats in totals.values():
        count = stats.get("count", 1) or 1
        stats["avg_plan_duration_ms"] = stats["avg_plan_duration_ms"] / count
        stats["avg_mutation_ms"] = stats["avg_mutation_ms"] / count
        stats["avg_navigation_ms"] = stats["avg_navigation_ms"] / count
    return totals


async def run_dynamic_audit(options: DynamicAuditOptions) -> dict:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_root = options.output_dir / timestamp
    output_root.mkdir(parents=True, exist_ok=True)
    logger.info(f"Dynamic audit output: {output_root}")

    project_entries: list[SummaryEntry] = []
    async with async_playwright() as playwright:
        for project in _select_projects(options.project_ids):
            if not project.frontend_url:
                logger.warning(f"Skipping {project.id}: missing frontend_url")
                continue
            for seed in options.seeds:
                start_url = _attach_seed(project.frontend_url, seed)
                urls = await _discover_urls(playwright, options.browser_name, options.headless, start_url, options.max_pages)
                if not urls:
                    logger.warning(f"[{project.id}] no URLs discovered from {start_url}")
                    continue
                writer = DatasetWriter(output_root, project.id, seed)
                summaries = await _run_seed_capture(playwright, options, project, seed, urls, writer)
                project_entries.extend(summaries)

    summary_path = output_root / "summary.jsonl"
    with summary_path.open("w", encoding="utf-8") as fh:
        for entry in project_entries:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    metrics = _aggregate_metrics(project_entries)
    (output_root / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {"output_dir": str(output_root), "summary_path": str(summary_path), "metrics": metrics}
    if options.llm_service and options.llm_sample_size > 0:
        llm_path = await _run_llm_spot_check(options, output_root, project_entries)
        result["llm_report"] = str(llm_path)
    return result


async def _run_llm_spot_check(options: DynamicAuditOptions, output_root: Path, entries: Sequence[SummaryEntry]) -> Path:
    if not entries:
        return output_root / "llm_report.json"
    sample_size = min(options.llm_sample_size, len(entries))
    chosen = random.sample(entries, sample_size)
    records = []
    for entry in chosen:
        before = (output_root / entry.before_path).read_text(encoding="utf-8")[: options.llm_summary_max_chars]
        after = (output_root / entry.after_path).read_text(encoding="utf-8")[: options.llm_summary_max_chars]
        plan = json.loads((output_root / entry.plan_path).read_text(encoding="utf-8"))
        messages = [
            {
                "role": "system",
                "content": "You review DOM mutation quality. Highlight risks or confirm if mutations look realistic.",
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "url": entry.url,
                        "plan_source": entry.plan_source,
                        "plan": plan,
                        "before_html": before,
                        "after_html": after,
                    },
                    ensure_ascii=False,
                ),
            },
        ]
        try:
            response = await options.llm_service.async_predict(messages)
        except Exception as exc:  # pragma: no cover - diagnostics only
            response = f"LLM call failed: {exc}"
        records.append({"record_id": entry.record_id, "analysis": response})

    report_path = output_root / "llm_report.json"
    report_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def build_llm_from_args(llm_type: str | None, *, api_key: str | None = None, endpoint: str | None = None, base_url: str | None = None, use_bearer: bool = False, model: str = "gpt-3.5-turbo", temperature: float = 0.2, max_tokens: int = 1024) -> ILLM | None:
    if not llm_type:
        return None
    config = LLMConfig(model=model, temperature=temperature, max_tokens=max_tokens)
    kwargs: dict = {}
    if api_key:
        kwargs["api_key"] = api_key
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    if base_url:
        kwargs["base_url"] = base_url
    if use_bearer is not None:
        kwargs["use_bearer"] = use_bearer
    return LLMFactory.create_llm(llm_type, config, **kwargs)


__all__ = [
    "DynamicAuditOptions",
    "DatasetWriter",
    "MutationCapture",
    "SummaryEntry",
    "build_llm_from_args",
    "run_dynamic_audit",
]
