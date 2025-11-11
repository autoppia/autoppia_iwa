from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

MODULE_PREFIX = "autoppia_iwa.src.demo_webs.projects"
SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}
EXCLUDED_DIR_PARTS = {"node_modules", ".next", ".turbo", "dist", "build", ".cache"}
EVENT_REF_LIMIT = 5


@dataclass
class EventCoverageResult:
    event_name: str
    references: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.references)


@dataclass
class DynamicLayerResult:
    key: str
    title: str
    passed: bool
    evidence: str | None = None


@dataclass
class ScreenshotReview:
    filename: str
    resolution: str
    size_kb: float
    summary: str


@dataclass
class WebProjectAnalysis:
    frontend_dir: Path | None
    event_results: list[EventCoverageResult] = field(default_factory=list)
    dynamic_layers: list[DynamicLayerResult] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    screenshots: list[ScreenshotReview] = field(default_factory=list)


def analyze_frontend(project_slug: str, frontend_dir: Path | None) -> WebProjectAnalysis:
    """Inspect the React/Next frontend for event emissions and dynamic layers."""
    analysis = WebProjectAnalysis(frontend_dir=frontend_dir)
    event_names, event_issues = _load_event_names(project_slug)
    analysis.issues.extend(event_issues)
    if not frontend_dir or not frontend_dir.exists():
        if not frontend_dir:
            analysis.issues.append("Frontend directory could not be located")
        else:
            analysis.issues.append(f"Frontend directory {frontend_dir} not found on disk")
        analysis.event_results.extend(EventCoverageResult(event_name=name) for name in event_names)
        return analysis

    source_index = list(_iter_source_files(frontend_dir))
    analysis.event_results.extend(_analyze_event_emissions(event_names, source_index, frontend_dir))
    analysis.dynamic_layers.extend(_analyze_dynamic_layers(source_index, frontend_dir))
    return analysis


def _load_event_names(project_slug: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    try:
        events_module = importlib.import_module(f"{MODULE_PREFIX}.{project_slug}.events")
        events_list = getattr(events_module, "EVENTS", None)
    except Exception as exc:  # pragma: no cover - defensive
        issues.append(f"Failed to import events module: {exc}")
        events_list = None

    if not events_list:
        issues.append("No EVENTS defined in IWA module")
        return [], issues

    event_names: list[str] = []
    for event in events_list:
        if not inspect.isclass(event):
            continue
        name = getattr(event, "event_name", None)
        if not isinstance(name, str):
            model_fields = getattr(event, "model_fields", None)
            if model_fields and "event_name" in model_fields:
                default = getattr(model_fields["event_name"], "default", None)
                if isinstance(default, str):
                    name = default
        if not isinstance(name, str) or not name.strip():
            name = event.__name__
        if name:
            event_names.append(name)
    return sorted(set(event_names)), issues


def _iter_source_files(frontend_dir: Path) -> Iterable[tuple[Path, str]]:
    for path in frontend_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel_parts = path.relative_to(frontend_dir).parts
        if any(part in EXCLUDED_DIR_PARTS for part in rel_parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        yield path, text


def _analyze_event_emissions(
    event_names: list[str],
    source_index: list[tuple[Path, str]],
    frontend_dir: Path,
) -> list[EventCoverageResult]:
    results: list[EventCoverageResult] = []
    for event_name in event_names:
        refs: list[str] = []
        needle = event_name
        for path, text in source_index:
            if needle not in text:
                continue
            relative = path.relative_to(frontend_dir)
            line_number = _find_line_number(text, needle)
            refs.append(f"{relative}:{line_number}")
            if len(refs) >= EVENT_REF_LIMIT:
                break
        results.append(EventCoverageResult(event_name=event_name, references=refs))
    return results


def _find_line_number(text: str, needle: str) -> int:
    for idx, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return idx
    return 0


DYNAMIC_RULES = {
    "D1": {
        "title": "D1 – Structural variability via seed/layout",
        "patterns": ["SeedContext.tsx", "useSeedLayout.ts", "LayoutProvider.tsx"],
        "keywords": ["seed", "layout"],
    },
    "D3": {
        "title": "D3 – Dynamic UI tokens (ids/text/labels)",
        "patterns": ["dynamicTokens.ts", "dynamicCopy.ts", "tokenFactory.ts", "DynamicText.ts"],
        "keywords": ["variant", "seed", "text"],
    },
}


def _analyze_dynamic_layers(
    source_index: list[tuple[Path, str]],
    frontend_dir: Path,
) -> list[DynamicLayerResult]:
    results: list[DynamicLayerResult] = []
    lower_cache = {path: text.lower() for path, text in source_index}
    for key, rule in DYNAMIC_RULES.items():
        evidence = _find_dynamic_evidence(rule["patterns"], rule["keywords"], lower_cache, frontend_dir)
        if evidence:
            results.append(DynamicLayerResult(key=key, title=rule["title"], passed=True, evidence=evidence))
        else:
            results.append(
                DynamicLayerResult(
                    key=key,
                    title=rule["title"],
                    passed=False,
                    evidence=f"Missing files containing keywords {rule['keywords']}",
                )
            )
    return results


def _find_dynamic_evidence(
    patterns: List[str],
    keywords: List[str],
    lower_cache: dict[Path, str],
    frontend_dir: Path,
) -> str | None:
    keyword_set = [kw.lower() for kw in keywords]
    for path, text in lower_cache.items():
        rel = path.relative_to(frontend_dir)
        if any(part in EXCLUDED_DIR_PARTS for part in rel.parts):
            continue
        if not any(pattern.lower() in rel.as_posix().lower() for pattern in patterns):
            continue
        if all(kw in text for kw in keyword_set):
            return rel.as_posix()
    return None
