from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from difflib import SequenceMatcher, unified_diff
from typing import Any, Iterable, Sequence
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from loguru import logger
from aiohttp import ClientSession, ClientError
from playwright.async_api import (
    Browser,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from .deck.models import DeckPage, WebProjectDeck


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:  # noqa: BLE001
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:  # noqa: BLE001
        return default


DEFAULT_SEEDS = [13, 23]
DEFAULT_MAX_PAGES = _env_int("AUTOPPIA_DYNAMIC_MAX_PAGES", 2)
DEFAULT_TIMEOUT_MS = _env_int("AUTOPPIA_DYNAMIC_TIMEOUT_MS", 15000)
DEFAULT_WAIT_MS = _env_int("AUTOPPIA_DYNAMIC_WAIT_AFTER_MS", 800)
SIMILARITY_SAME_THRESHOLD = _env_float("AUTOPPIA_DYNAMIC_SIM_THRESHOLD", 0.995)
MIN_MUTATION_DELTA = _env_float("AUTOPPIA_DYNAMIC_MIN_DELTA", 0.02)  # 2% diff
MAX_STATIC_DELTA = _env_float("AUTOPPIA_DYNAMIC_MAX_STATIC_DELTA", 0.01)
LLM_DIFF_SAMPLE_CHARS = _env_int("AUTOPPIA_DYNAMIC_LLM_SAMPLE", 1800)


@dataclass
class DynamicGateConfig:
    seeds: list[int] = field(default_factory=lambda: DEFAULT_SEEDS.copy())
    seedless_repeats: int = 2
    repeats_per_seed: int = 2
    max_pages: int = DEFAULT_MAX_PAGES
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    wait_after_ms: int = DEFAULT_WAIT_MS
    headless: bool = True


@dataclass
class DynamicPageResult:
    page_id: str
    url_used: str | None
    expect_mutations: bool
    base_similarity: float | None
    reproducibility: list[tuple[int | None, float]]
    base_deltas: list[tuple[int, float]]
    cross_seed_deltas: list[tuple[tuple[int, int], float]]
    issues: list[str] = field(default_factory=list)
    llm_pass: bool | None = None
    llm_feedback: str | None = None

    @property
    def seedless_stable(self) -> bool:
        if self.base_similarity is None:
            return False
        return self.base_similarity >= SIMILARITY_SAME_THRESHOLD

    @property
    def reproducibility_ok(self) -> bool:
        if not self.reproducibility:
            return False
        return all(score >= SIMILARITY_SAME_THRESHOLD for _, score in self.reproducibility if score is not None)

    @property
    def mutation_detected(self) -> bool:
        if not self.base_deltas:
            return False
        if not self.expect_mutations:
            return all(delta <= MAX_STATIC_DELTA for _, delta in self.base_deltas)
        return any(delta >= MIN_MUTATION_DELTA for _, delta in self.base_deltas)

    @property
    def cross_seed_variance(self) -> bool:
        if not self.cross_seed_deltas:
            return not self.expect_mutations
        if not self.expect_mutations:
            return all(delta <= MAX_STATIC_DELTA for _, delta in self.cross_seed_deltas)
        return any(delta >= MIN_MUTATION_DELTA for _, delta in self.cross_seed_deltas)

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "url": self.url_used,
            "expect_mutations": self.expect_mutations,
            "base_similarity": self.base_similarity,
            "reproducibility": self.reproducibility,
            "base_deltas": self.base_deltas,
            "cross_seed_deltas": self.cross_seed_deltas,
            "issues": self.issues,
            "llm_pass": self.llm_pass,
            "llm_feedback": self.llm_feedback,
        }


@dataclass
class DynamicValidationOutcome:
    page_results: list[DynamicPageResult]
    expect_mutations: bool
    errors: list[str] = field(default_factory=list)

    def _collect_metric(self, attr: str) -> list[tuple[str, float]]:
        collected: list[tuple[str, float]] = []
        for result in self.page_results:
            value = getattr(result, attr, None)
            if value is None:
                continue
            collected.append((result.page_id, value))
        return collected

    def seedless_stable(self) -> bool:
        if not self.page_results:
            return False
        return all(res.seedless_stable for res in self.page_results)

    def reproducible(self) -> bool:
        if not self.page_results:
            return False
        return all(res.reproducibility_ok for res in self.page_results)

    def mutations_behave(self) -> bool:
        if not self.page_results:
            return False
        return all(res.mutation_detected for res in self.page_results)

    def cross_seed_ok(self) -> bool:
        if not self.page_results:
            return False
        return all(res.cross_seed_variance for res in self.page_results)

    def llm_review_pass(self) -> bool | None:
        verdicts = [res.llm_pass for res in self.page_results if res.llm_pass is not None]
        if not verdicts:
            return None
        return all(verdicts)

    def llm_feedback(self) -> str | None:
        feedbacks = [res.llm_feedback for res in self.page_results if res.llm_feedback]
        if not feedbacks:
            return None
        return "; ".join(feedbacks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "expect_mutations": self.expect_mutations,
            "pages": [res.to_dict() for res in self.page_results],
            "errors": self.errors,
        }


async def run_dynamic_validation(
    *,
    deck: WebProjectDeck | None,
    base_url: str | None,
    llm_service,
    config: DynamicGateConfig | None = None,
) -> DynamicValidationOutcome:
    cfg = config or DynamicGateConfig()
    expect_mutations = _expect_mutations(deck)
    if not base_url:
        return DynamicValidationOutcome(page_results=[], expect_mutations=expect_mutations, errors=["Missing base URL for dynamic validation"])

    page_specs = _select_pages(deck, cfg.max_pages)
    if not page_specs:
        return DynamicValidationOutcome(page_results=[], expect_mutations=expect_mutations, errors=["Deck provides no pages for dynamic validation"])

    results: list[DynamicPageResult] = []
    async with async_playwright() as playwright:
        browser: Browser = await playwright.chromium.launch(headless=cfg.headless)
        try:
            for page_spec in page_specs:
                context = await browser.new_context()
                page = await context.new_page()
                try:
                    page_result = await _evaluate_single_page(
                        page=page,
                        base_url=base_url,
                        page_spec=page_spec,
                        config=cfg,
                        expect_mutations=expect_mutations,
                        llm_service=llm_service,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Dynamic gate failed for page %s: %s", page_spec.id, exc)
                    page_result = DynamicPageResult(
                        page_id=page_spec.id or "unknown",
                        url_used=None,
                        expect_mutations=expect_mutations,
                        base_similarity=None,
                        reproducibility=[],
                        base_deltas=[],
                        cross_seed_deltas=[],
                        issues=[f"Unexpected error: {exc}"],
                    )
                results.append(page_result)
                await context.close()
        finally:
            await browser.close()

    return DynamicValidationOutcome(page_results=results, expect_mutations=expect_mutations)


async def _evaluate_single_page(
    *,
    page: Page,
    base_url: str,
    page_spec: DeckPage,
    config: DynamicGateConfig,
    expect_mutations: bool,
    llm_service,
) -> DynamicPageResult:
    working_pattern = None
    resolved_url = None
    issues: list[str] = []
    html_runs: dict[int | None, list[str]] = {}

    candidate_patterns = list(_candidate_patterns(page_spec))
    for pattern in candidate_patterns:
        html, url, error = await _capture_html(page, base_url, pattern, seed=None, config=config)
        if error:
            issues.append(f"{pattern}: {error}")
            continue
        working_pattern = pattern
        resolved_url = url
        html_runs.setdefault(None, []).append(html)
        break

    if not working_pattern:
        return DynamicPageResult(
            page_id=page_spec.id or "unknown",
            url_used=None,
            expect_mutations=expect_mutations,
            base_similarity=None,
            reproducibility=[],
            base_deltas=[],
            cross_seed_deltas=[],
            issues=issues or ["Unable to capture baseline HTML"],
        )

    # Additional seedless runs
    await _collect_runs(page, base_url, working_pattern, None, config.seedless_repeats - 1, config, html_runs)

    # Seeded runs
    for seed in config.seeds:
        await _collect_runs(page, base_url, working_pattern, seed, config.repeats_per_seed, config, html_runs)

    base_similarity = _compute_similarity(html_runs.get(None))
    reproducibility = _compute_reproducibility(html_runs)
    base_deltas = _compute_base_deltas(html_runs)
    cross_seed_deltas = _compute_cross_seed_deltas(html_runs)

    llm_pass = None
    llm_feedback = None
    if llm_service and html_runs.get(None) and any(html_runs.get(seed) for seed in config.seeds):
        llm_pass, llm_feedback = await _llm_assess_variation(
            llm_service=llm_service,
            page_id=page_spec.id or resolved_url or "page",
            base_html=html_runs.get(None, [""])[0],
            seed_htmls=[(seed, runs[0]) for seed, runs in html_runs.items() if seed is not None and runs],
            heuristics={
                "base_similarity": base_similarity,
                "base_deltas": base_deltas,
                "cross_seed_deltas": cross_seed_deltas,
                "expect_mutations": expect_mutations,
            },
        )

    return DynamicPageResult(
        page_id=page_spec.id or "unknown",
        url_used=resolved_url,
        expect_mutations=expect_mutations,
        base_similarity=base_similarity,
        reproducibility=reproducibility,
        base_deltas=base_deltas,
        cross_seed_deltas=cross_seed_deltas,
        issues=issues,
        llm_pass=llm_pass,
        llm_feedback=llm_feedback,
    )


async def _collect_runs(
    page: Page,
    base_url: str,
    pattern: str,
    seed: int | None,
    repeats: int,
    config: DynamicGateConfig,
    storage: dict[int | None, list[str]],
) -> None:
    if repeats <= 0:
        return
    for _ in range(repeats):
        html, _, error = await _capture_html(page, base_url, pattern, seed=seed, config=config)
        if error:
            storage.setdefault(seed, [])
            storage[seed].append("")
            logger.warning("Dynamic capture failed for seed=%s pattern=%s: %s", seed, pattern, error)
            continue
        storage.setdefault(seed, [])
        storage[seed].append(html)


async def _capture_html(
    page: Page,
    base_url: str,
    pattern: str,
    *,
    seed: int | None,
    config: DynamicGateConfig,
) -> tuple[str | None, str | None, str | None]:
    url = _build_url(base_url, pattern, seed)
    try:
        await page.goto(url, wait_until="networkidle", timeout=config.timeout_ms)
        if config.wait_after_ms:
            await page.wait_for_timeout(config.wait_after_ms)
        html = await page.content()
        if not (html or "").strip():
            fallback = await _http_fetch(url, config.timeout_ms)
            if fallback:
                html = fallback
        return html, url, None
    except PlaywrightTimeoutError as exc:
        return None, url, f"Timeout after {config.timeout_ms}ms ({exc})"
    except Exception as exc:  # noqa: BLE001
        return None, url, str(exc)


def _build_url(base_url: str, pattern: str, seed: int | None) -> str:
    if pattern.startswith("http://") or pattern.startswith("https://"):
        url = pattern
    else:
        base = base_url.rstrip("/") + "/"
        url = urljoin(base, pattern.lstrip("/"))

    token = str(seed) if seed is not None else ""
    for placeholder in ("<seed>", "<id>", "<slug>"):
        url = url.replace(placeholder, token)

    return _with_seed_param(url, seed)


def _with_seed_param(url: str, seed: int | None) -> str:
    if seed is None:
        return url
    parsed = urlsplit(url)
    params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() != "seed"]
    params.append(("seed", str(seed)))
    new_query = urlencode(params)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))


async def _http_fetch(url: str, timeout_ms: int) -> str | None:
    timeout = max(1, timeout_ms / 1000)
    headers = {"accept-encoding": "identity"}
    try:
        async with ClientSession() as session:
            async with session.get(url, timeout=timeout, headers=headers) as resp:
                if resp.status >= 400:
                    logger.warning(f"HTTP fallback returned {resp.status} for {url}")
                    return None
                return await resp.text()
    except ClientError as exc:
        logger.warning(f"HTTP fallback error for {url}: {exc}")
        return None


def _candidate_patterns(page_spec: DeckPage) -> Iterable[str]:
    if page_spec.url_patterns:
        return page_spec.url_patterns
    return ["/"]


def _compute_similarity(html_runs: Sequence[str] | None) -> float | None:
    if not html_runs or len(html_runs) < 2:
        return None
    return SequenceMatcher(None, html_runs[0], html_runs[1]).ratio()


def _compute_reproducibility(html_runs: dict[int | None, list[str]]) -> list[tuple[int | None, float]]:
    scores: list[tuple[int | None, float]] = []
    for seed, runs in html_runs.items():
        if len(runs) < 2:
            continue
        ratio = SequenceMatcher(None, runs[0], runs[1]).ratio()
        scores.append((seed, ratio))
    return scores


def _compute_base_deltas(html_runs: dict[int | None, list[str]]) -> list[tuple[int, float]]:
    base_runs = html_runs.get(None)
    if not base_runs:
        return []
    baseline = base_runs[0]
    deltas: list[tuple[int, float]] = []
    for seed, runs in html_runs.items():
        if seed is None or not runs:
            continue
        ratio = SequenceMatcher(None, baseline, runs[0]).ratio()
        deltas.append((seed, 1 - ratio))
    return deltas


def _compute_cross_seed_deltas(html_runs: dict[int | None, list[str]]) -> list[tuple[tuple[int, int], float]]:
    seeds = [seed for seed in html_runs.keys() if seed is not None and html_runs.get(seed)]
    deltas: list[tuple[tuple[int, int], float]] = []
    for i, seed_a in enumerate(seeds):
        html_a = html_runs[seed_a][0]
        for seed_b in seeds[i + 1 :]:
            html_b = html_runs[seed_b][0]
            ratio = SequenceMatcher(None, html_a, html_b).ratio()
            deltas.append(((seed_a, seed_b), 1 - ratio))
    return deltas


async def _llm_assess_variation(llm_service, page_id: str, base_html: str, seed_htmls: list[tuple[int, str]], heuristics: dict) -> tuple[bool | None, str | None]:
    base_excerpt = _trim_html(base_html)
    chunks = []
    for seed, html in seed_htmls:
        chunks.append(f"Seed {seed}:\n{_trim_html(html)}")
    user_content = (
        f"Page: {page_id}\n"
        f"Heuristics: {json.dumps(heuristics)}\n"
        f"Baseline HTML:\n{base_excerpt}\n"
        f"{'-'*40}\n"
        f"{chr(10).join(chunks)}"
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You validate whether different seeds produce deterministic yet distinct HTML mutations.\n"
                "Respond strictly as JSON: {\"pass\": bool, \"reasons\": [\"...\"]}.\n"
                "Use the heuristics as the primary signal: if they report sizable deltas, presume PASS unless the HTML snippets clearly prove they are identical."
            ),
        },
        {"role": "user", "content": user_content},
    ]
    try:
        raw = await asyncio.wait_for(
            llm_service.async_predict(messages=messages, json_format=True, return_raw=False),
            timeout=10,
        )
        data = json.loads(raw) if isinstance(raw, str) else raw
        return bool(data.get("pass", False)), "; ".join(data.get("reasons") or [])
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM dynamic assessment failed: %s", exc)
        return None, f"LLM error: {exc}"


def _trim_html(html: str) -> str:
    snippet = (html or "").strip()
    if len(snippet) > LLM_DIFF_SAMPLE_CHARS:
        return snippet[:LLM_DIFF_SAMPLE_CHARS] + "\n... (truncated)"
    return snippet


def _expect_mutations(deck: WebProjectDeck | None) -> bool:
    if not deck or not deck.dynamic_profile:
        return False
    profile = deck.dynamic_profile
    return any(
        getattr(profile, attr, False)
        for attr in ("html_mutates", "data_mutates", "ui_identifiers_mutate")
    )


def _select_pages(deck: WebProjectDeck | None, limit: int) -> list[DeckPage]:
    if deck and deck.pages:
        return list(deck.pages[:limit])
    placeholder = DeckPage(id="root", title="Root", url_patterns=["/"], description=None, required_elements=[])
    return [placeholder]
