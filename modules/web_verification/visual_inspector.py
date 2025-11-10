from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin

from loguru import logger
from playwright.async_api import Browser, Page, TimeoutError as PlaywrightTimeoutError, async_playwright

from autoppia_iwa.src.di_container import DIContainer
from .deck.models import DeckPage, DeckRequiredElement, WebProjectDeck

DECKS_BASE = Path(__file__).resolve().parent / "deck"
SCREENSHOT_DIR = Path("data") / "web_verification" / "visual_inspector"

try:  # pragma: no cover - DI optional in CLI
    DI = DIContainer()
except Exception:  # noqa: S110
    DI = None


def _candidate_deck_paths(project_slug: str) -> list[Path]:
    if not DECKS_BASE.exists():
        return []
    roots = [DECKS_BASE]
    examples = DECKS_BASE / "examples"
    if examples.exists():
        roots.append(examples)
    suffixes = (".deck.json", ".json")
    matches: list[Path] = []
    for root in roots:
        for suffix in suffixes:
            candidate = root / f"{project_slug}{suffix}"
            if candidate.exists():
                matches.append(candidate)
        matches.extend(root.glob(f"{project_slug}*.deck.json"))
    return matches


def _resolve_deck_path(project_slug: str, deck_arg: str | None) -> Path:
    if deck_arg:
        explicit = Path(deck_arg)
        if not explicit.exists():
            raise FileNotFoundError(f"Deck file '{explicit}' not found")
        return explicit
    candidates = _candidate_deck_paths(project_slug)
    if not candidates:
        raise FileNotFoundError(f"No deck file found under {DECKS_BASE} for slug '{project_slug}'")
    return candidates[0]


def _build_url(base_url: str, pattern: str, seed: str | None) -> str:
    placeholder_value = seed or ""
    replacements = {
        "<seed>": placeholder_value,
        "<slug>": placeholder_value,
        "<id>": placeholder_value,
    }
    for placeholder, value in replacements.items():
        pattern = pattern.replace(placeholder, value)
    if pattern.startswith("http://") or pattern.startswith("https://"):
        return pattern
    base = base_url.rstrip("/") + "/"
    path = pattern.lstrip("/")
    return urljoin(base, path)


async def _check_required_elements(page: Page, elements: Iterable[DeckRequiredElement], timeout: float) -> list[str]:
    issues: list[str] = []
    for element in elements:
        selector = element.selector
        text = element.text_contains
        try:
            if selector:
                locator = page.locator(selector)
                await locator.first.wait_for(state="visible", timeout=timeout)
                if text:
                    locator = locator.filter(has_text=text)
                    count = await locator.count()
                    if count == 0:
                        issues.append(f"No element matching {element.describe()}")
            elif text:
                locator = page.get_by_text(text, exact=False)
                await locator.first.wait_for(state="visible", timeout=timeout)
            else:
                issues.append("Element spec missing selector/text")
        except PlaywrightTimeoutError:
            issues.append(f"Timeout waiting for {element.describe()}")
    return issues


async def _inspect_page(
    browser: Browser,
    project_slug: str,
    base_url: str,
    page_spec: DeckPage,
    timeout: float,
    seed: str | None,
    capture_dir: Path | None,
) -> dict:
    context = await browser.new_context()
    page = await context.new_page()
    result = {
        "page_id": page_spec.id,
        "title": page_spec.title,
        "ok": False,
        "url_attempted": None,
        "errors": [],
        "missing_elements": [],
    }
    try:
        for pattern in page_spec.url_patterns or ["/"]:
            candidate_url = _build_url(base_url, pattern, seed)
            result["url_attempted"] = candidate_url
            try:
                response = await page.goto(candidate_url, wait_until="domcontentloaded", timeout=timeout)
            except PlaywrightTimeoutError:
                result["errors"].append(f"Timeout navigating to {candidate_url}")
                continue
            status = response.status if response else None
            if status and status >= 400:
                result["errors"].append(f"{candidate_url} returned status {status}")
                continue
            missing = await _check_required_elements(page, page_spec.required_elements, timeout)
            if missing:
                result["missing_elements"] = missing
                continue
            if capture_dir:
                capture_dir.mkdir(parents=True, exist_ok=True)
                filename = f"{page_spec.id}_{seed or 'default'}.png"
                file_path = capture_dir / project_slug / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(file_path), full_page=True)
                result["screenshot_path"] = str(file_path)
                try:
                    html_snapshot = await page.content()
                    if len(html_snapshot) > 4000:
                        html_snapshot = html_snapshot[:4000] + "..."
                    result["html_snapshot"] = html_snapshot
                except Exception as exc:  # noqa: BLE001
                    result["html_snapshot"] = f"<!-- Failed to capture HTML: {exc} -->"
                try:
                    text_snapshot = await page.inner_text("body")
                    if len(text_snapshot) > 2000:
                        text_snapshot = text_snapshot[:2000] + "..."
                    result["page_text"] = text_snapshot
                except Exception as exc:  # noqa: BLE001
                    result["page_text"] = f"(Unable to capture body text: {exc})"
            result["ok"] = True
            break
        if not page_spec.required_elements and not result["errors"]:
            result["ok"] = True
    finally:
        await context.close()
    return result


async def _llm_judge_page(
    llm_service: Any,
    deck: WebProjectDeck,
    page_spec: DeckPage,
    entry: dict,
) -> dict:
    screenshot_path = entry.get("screenshot_path")
    html_snapshot = entry.get("html_snapshot", "")
    if not screenshot_path or not Path(screenshot_path).exists():
        return {"llm_pass": True, "llm_feedback": "LLM judge skipped (no screenshot provided)."}

    file_path = Path(screenshot_path)
    file_size_kb = round(file_path.stat().st_size / 1024, 1)
    width = height = "unknown"
    try:
        from PIL import Image  # type: ignore

        with Image.open(file_path) as img:
            width, height = img.size
    except Exception:  # noqa: BLE001
        pass

    deck_summary = deck.metadata.summary or ""
    required_elements = "\n".join(f"- {element.describe()}" for element in page_spec.required_elements) or "N/A"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a QA judge verifying that a rendered page matches a deck specification."
                " Structural selectors already passed automated checks; DO NOT mark elements as missing."
                " Ignore <title> tags and focus on the visible body content."
                " Use the HTML snippet (truncated), body text excerpt, and screenshot metadata to reason."
                " Fail only if the UI appears broken, empty, or clearly contradicts the deck description."
                " Respond strictly in JSON: {\"pass\": bool, \"reasons\": [\"...\"]}."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "project_summary": deck_summary,
                    "page_id": page_spec.id,
                    "page_title": page_spec.title,
                    "page_description": page_spec.description,
                    "required_elements": required_elements,
                    "url_attempted": entry.get("url_attempted"),
                    "html_excerpt": html_snapshot,
                    "body_text_excerpt": entry.get("page_text", "")[:2000],
                    "screenshot_metadata": {
                        "path": str(file_path),
                        "resolution": f"{width}x{height}",
                        "size_kb": file_size_kb,
                    },
                }
            ),
        },
    ]

    try:
        raw = await llm_service.async_predict(messages=messages, json_format=True, return_raw=False)
    except Exception as exc:  # noqa: BLE001
        return {"llm_pass": False, "llm_feedback": f"LLM judge failed: {exc}"}

    verdict = {"pass": False, "reasons": ["LLM returned empty response."]}

    def _attempt_parse(text: str) -> dict | None:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except Exception:  # noqa: BLE001
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:  # noqa: BLE001
                    return None
        return None

    parsed: dict | None = None
    if isinstance(raw, dict):
        parsed = raw
    elif isinstance(raw, str):
        parsed = _attempt_parse(raw)

    if parsed:
        verdict["pass"] = bool(parsed.get("pass"))
        reasons = parsed.get("reasons")
        if isinstance(reasons, list):
            verdict["reasons"] = [str(r) for r in reasons[:5]]
        elif isinstance(reasons, str):
            verdict["reasons"] = [reasons]
    else:
        verdict["reasons"] = [str(raw)[:200]]
        verdict["pass"] = False
    feedback = "; ".join(verdict.get("reasons", []))
    return {"llm_pass": verdict.get("pass", False), "llm_feedback": feedback or "LLM returned no feedback."}


def _heuristic_keyword_pass(page_spec: DeckPage, entry: dict) -> bool:
    text = (entry.get("page_text") or "").lower()
    if not text:
        return False
    keyword_map = {
        "home": ["collection", "movie", "film"],
        "detail": ["synopsis", "cast", "comment", "rating"],
        "cms": ["save movie", "movie form", "add movie"],
        "login": ["login", "sign in"],
        "register": ["register", "sign up"],
    }
    keywords = keyword_map.get(page_spec.id)
    if not keywords:
        return True
    return any(keyword in text for keyword in keywords)


async def run_inspector(
    deck: WebProjectDeck,
    project_slug: str,
    base_url: str,
    timeout: float,
    seed: str | None,
    headless: bool,
    screenshot_dir: Path | None = None,
    llm_service: Any | None = None,
    enable_llm_judge: bool = False,
) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        try:
            tasks = [
                _inspect_page(
                    browser,
                    project_slug=project_slug,
                    base_url=base_url,
                    page_spec=page_spec,
                    timeout=timeout,
                    seed=seed,
                    capture_dir=screenshot_dir,
                )
                for page_spec in deck.pages
            ]
            results = await asyncio.gather(*tasks)
            if enable_llm_judge:
                if llm_service is None:
                    logger.warning("LLM judge requested but service unavailable. Skipping LLM stage.")
                    for entry in results:
                        entry["llm_pass"] = None
                        entry["llm_feedback"] = "LLM judge skipped (service unavailable)."
                else:
                    for entry, page_spec in zip(results, deck.pages):
                        if not entry.get("ok"):
                            entry["llm_pass"] = False
                            entry["llm_feedback"] = "Skipped (structural checks failed)."
                            continue
                        review = await _llm_judge_page(llm_service, deck, page_spec, entry)
                        entry.update(review)
                        if not review.get("llm_pass", False):
                            if _heuristic_keyword_pass(page_spec, entry):
                                entry["llm_pass"] = True
                                entry["llm_feedback"] = f"{entry.get('llm_feedback', '')} (Heuristic keyword override)"
                                continue
                            entry["ok"] = False
            return results
        finally:
            await browser.close()


def _obtain_llm_service():
    if DI is None:
        return None
    try:
        return DI.llm_service()
    except Exception:  # noqa: BLE001
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 2 visual inspection for deck-defined pages.")
    parser.add_argument("project_slug", help="Project slug (e.g. autocinema)")
    parser.add_argument(
        "--deck",
        help="Ruta al archivo deck (JSON). Si no se indica se busca en modules/web_verification/deck.",
    )
    parser.add_argument("--base-url", help="URL base a inspeccionar. Por defecto se usa la del deck.")
    parser.add_argument("--seed", help="Seed para reemplazar <seed> en URLs. Por defecto se genera aleatoriamente.")
    parser.add_argument("--timeout", type=float, default=8000, help="Timeout Playwright en ms (default: 8000).")
    parser.add_argument("--headed", action="store_true", help="Lanza navegador en modo visible.")
    parser.add_argument("--llm-judge", action="store_true", help="Activa el juicio LLM basado en screenshots.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    deck_path = _resolve_deck_path(args.project_slug, args.deck)
    deck = WebProjectDeck.load(deck_path)
    base_url = args.base_url or (deck.metadata.deployment.preview_base_url if deck.metadata.deployment else None)
    if not base_url:
        raise ValueError("No base URL provided. Use --base-url or configure metadata.deployment.preview_base_url in the deck.")
    seed = args.seed or str(random.randint(1, 9999))
    screenshot_dir = SCREENSHOT_DIR
    llm_service = _obtain_llm_service() if args.llm_judge else None
    logger.info(f"Using deck {deck_path} with base URL {base_url} and seed {seed}")
    results = asyncio.run(
        run_inspector(
            deck,
            project_slug=args.project_slug,
            base_url=base_url,
            timeout=args.timeout,
            seed=seed,
            headless=not args.headed,
            screenshot_dir=screenshot_dir,
            llm_service=llm_service,
            enable_llm_judge=args.llm_judge,
        )
    )
    ok_pages = [r for r in results if r["ok"]]
    failed_pages = [r for r in results if not r["ok"]]
    logger.info("==== Visual inspection report ====")
    for entry in results:
        status = "PASS" if entry["ok"] else "FAIL"
        logger.info(f"[{status}] {entry['page_id']} -> {entry.get('url_attempted')}")
        for err in entry.get("errors", []):
            logger.info(f"    Error: {err}")
        for missing in entry.get("missing_elements", []):
            logger.info(f"    Missing: {missing}")
        if entry.get("llm_feedback"):
            logger.info(f"    LLM: {'PASS' if entry.get('llm_pass') else 'FAIL'} - {entry['llm_feedback']}")
    logger.info(f"Summary: {len(ok_pages)}/{len(results)} pages passed.")
    if failed_pages:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
