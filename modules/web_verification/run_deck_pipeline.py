from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from loguru import logger

from autoppia_iwa.src.di_container import DIContainer
from .deck.models import WebProjectDeck
from .visual_inspector import run_inspector as run_visual_inspector, SCREENSHOT_DIR
from .verify_project import (
    SECTION_DECK,
    SECTION_PROCEDURAL,
    ProjectReport,
    verify_project,
)


class PhaseResult:
    def __init__(self, phase: str, message: str, report: ProjectReport, visual_details: list[dict] | None = None):
        self.phase = phase
        self.message = message
        self.report = report
        self.visual_details = visual_details or []

    def render(self) -> str:
        lines = [f"Pipeline result → {self.phase}: {self.message}", ""]
        lines.append(self.report.render())
        lines.append("")
        if self.visual_details:
            lines.append("==== Visual Inspection ====")
            for entry in self.visual_details:
                status = "PASS" if entry.get("ok") else "FAIL"
                url = entry.get("url_attempted")
                lines.append(f"- [{status}] {entry.get('page_id')} ({entry.get('title')}) ⇒ {url}")
                for err in entry.get("errors", []):
                    lines.append(f"    Error: {err}")
                for missing in entry.get("missing_elements", []):
                    lines.append(f"    Missing: {missing}")
                if entry.get("llm_feedback"):
                    llm_status = "PASS" if entry.get("llm_pass") else "FAIL"
                    lines.append(f"    LLM: {llm_status} – {entry['llm_feedback']}")
        return "\n".join(lines)


def _procedural_passed(report: ProjectReport) -> bool:
    procedural = report.sections.get(SECTION_PROCEDURAL)
    deck_section = report.sections.get(SECTION_DECK)
    return bool(procedural and procedural.ok and deck_section and deck_section.ok)


def _obtain_llm_service():
    try:
        container = DIContainer()
        return container.llm_service()
    except Exception:  # noqa: BLE001
        return None


def evaluate_project(
    deck_path: Path,
    project_slug: str | None,
    base_url: str | None,
    seed: str,
    timeout_ms: float,
    headed: bool,
    enable_llm_judge: bool,
) -> PhaseResult:
    deck = WebProjectDeck.load(deck_path)
    slug = project_slug or deck.metadata.project_id

    logger.info(f"Running procedural verification for '{slug}'")
    report, _ = verify_project(slug, deck_path=deck_path)

    if not _procedural_passed(report):
        return PhaseResult("PHASE_1", "Procedural checks failed. Fix IWA module/deck before proceeding.", report)

    target_base = base_url or (deck.metadata.deployment.preview_base_url if deck.metadata.deployment else None)
    if not target_base:
        return PhaseResult("PHASE_2", "Deck misses deployment.preview_base_url and no --base-url provided.", report)

    logger.info(f"Running visual inspector against {target_base} (seed={seed})")
    llm_service = _obtain_llm_service() if enable_llm_judge else None
    if enable_llm_judge and llm_service is None:
        logger.warning("LLM judge enabled but service unavailable. Continuing without visual AI review.")
    visual_results = asyncio.run(
        run_visual_inspector(
            deck=deck,
            project_slug=slug,
            base_url=target_base,
            timeout=timeout_ms,
            seed=seed,
            headless=not headed,
            screenshot_dir=SCREENSHOT_DIR,
            llm_service=llm_service,
            enable_llm_judge=enable_llm_judge,
        )
    )
    visual_ok = all(entry.get("ok") for entry in visual_results)

    if not visual_ok:
        return PhaseResult("PHASE_2", "Visual inspection failed. Fix required pages before sandbox.", report, visual_results)

    return PhaseResult("PHASE_3", "Ready for sandbox deployment. Proceed with miner evaluation (Phase 3).", report, visual_results)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="End-to-end deck pipeline (procedural + visual).")
    parser.add_argument("deck", type=Path, help="Path to deck JSON.")
    parser.add_argument("--project-slug", help="Override project slug (defaults to deck.metadata.project_id).")
    parser.add_argument("--base-url", help="Override base URL for visual inspection.")
    parser.add_argument("--seed", default="42", help="Seed placeholder for URLs (default: 42).")
    parser.add_argument("--timeout", type=float, default=8000, help="Playwright timeout (ms).")
    parser.add_argument("--headed", action="store_true", help="Run Playwright with visible browser.")
    parser.add_argument("--disable-llm-judge", action="store_true", help="Skip LLM visual judgement.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    result = evaluate_project(
        deck_path=args.deck,
        project_slug=args.project_slug,
        base_url=args.base_url,
        seed=args.seed,
        timeout_ms=args.timeout,
        headed=args.headed,
        enable_llm_judge=not args.disable_llm_judge,
    )
    print(result.render())
    if result.phase != "PHASE_3":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
