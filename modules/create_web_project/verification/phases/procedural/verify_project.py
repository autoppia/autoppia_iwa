from __future__ import annotations

import argparse
import asyncio
import importlib
import inspect
import json
import os
import random
import re
import sys
from urllib.parse import urlsplit, urlunsplit
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
from tqdm import tqdm

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.tests.multi_step.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.llms.interfaces import LLMConfig
from autoppia_iwa.src.llms.service import LLMFactory
from autoppia_iwa.src.web_agents.examples.random_clicker.agent import RandomClickerWebAgent

from ..deck.models import WebProjectDeck
from ..dynamic.dynamic_validation import DynamicGateConfig, DynamicValidationOutcome, run_dynamic_validation
from ..visual.screenshot_analysis import summarize_screenshots
from .frontend_analysis import ScreenshotReview, WebProjectAnalysis, analyze_frontend
from .module_generator import ConfigError as ModuleConfigError, generate_module_from_config

PROJECTS_BASE = PROJECT_BASE_DIR / "src" / "demo_webs" / "projects"
DECKS_BASE = Path(__file__).resolve().parents[1] / "deck"
DECK_ALIASES = {
    "autocrm_5": "autocrm",
    "autocalender_11": "autocalendar",
    "autoconnect_9": "autoconnect",
    "autodelivery_7": "autodelivery",
    "autodrive_13": "autodrive",
    "autolist_12": "autolist",
    "autolodge_8": "autolodge",
    "automail_6": "automail",
    "autowork_10": "autowork",
    "books_2": "autobooks",
    "cinema_1": "autocinema",
    "dining_4": "autodining",
    "omnizone_3": "autozone",
}
MODULE_PREFIX = "autoppia_iwa.src.demo_webs.projects"
LLM_SAMPLE_SIZE = 1
LLM_TIMEOUT_SECONDS = 10
TASKS_PER_USE_CASE = int(os.getenv("AUTOPPIA_TASKS_PER_USE_CASE", "2"))
DEFAULT_AGENT_HOST = os.getenv("AUTOPPIA_AGENT_HOST", "84.247.180.192")
DEFAULT_AGENT_PORT = int(os.getenv("AUTOPPIA_AGENT_PORT", "6789"))
DEFAULT_AGENT_TIMEOUT = int(os.getenv("AUTOPPIA_AGENT_TIMEOUT", "120"))
CODE_FENCE_RE = re.compile(r"```(?:\w+)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
DI_ERROR: Exception | None = None
try:  # pragma: no cover - DI wiring may fail if optional deps missing
    DI = DIContainer()
except Exception as exc:  # pragma: no cover - degrade gracefully
    DI = None
    DI_ERROR = exc
REPORT_DIR = Path("data") / "web_verification" / "reports"
SECTION_PROCEDURAL = "procedural"
SECTION_DECK = "deck"
SECTION_USE_CASES = "use_cases"
SECTION_LLM_TASKS = "llm_task_pipeline"
SECTION_LLM_TESTS = "llm_test_pipeline"
SECTION_DYNAMIC = "dynamic_validation"

SECTION_TITLES = {
    SECTION_PROCEDURAL: "IWA Web Project Procedural Analysis",
    SECTION_DECK: "Deck Compliance",
    SECTION_USE_CASES: "Use Cases Analysis",
    SECTION_LLM_TASKS: "LLM Task Generation Pipeline Analysis",
    SECTION_LLM_TESTS: "LLM Test Generation Pipeline Analysis",
    SECTION_DYNAMIC: "Dynamic Mutation Integrity Analysis",
}
SECTION_ORDER = [
    SECTION_PROCEDURAL,
    SECTION_DECK,
    SECTION_USE_CASES,
    SECTION_LLM_TASKS,
    SECTION_LLM_TESTS,
    SECTION_DYNAMIC,
]


@dataclass
class CheckResult:
    passed: bool
    description: str
    details: str | None = None


@dataclass
class AnalysisSection:
    key: str
    title: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        if not self.checks:
            return True
        return all(check.passed for check in self.checks)

    def add(self, passed: bool, description: str, details: str | None = None) -> None:
        self.checks.append(CheckResult(passed=passed, description=description, details=details))


@dataclass
class ProjectReport:
    project_name: str
    sections: dict[str, AnalysisSection] = field(default_factory=dict)
    web_analysis: WebProjectAnalysis | None = None
    frontend_dir: Path | None = None
    random_stats: dict[str, Any] | None = None
    miner_stats: dict[str, Any] | None = None
    dynamic_stats: dict[str, Any] | None = None
    deck: WebProjectDeck | None = None

    @property
    def ok(self) -> bool:
        if not self.sections:
            return False
        return all(section.ok for section in self.sections.values())

    def _get_section(self, key: str) -> AnalysisSection:
        if key not in self.sections:
            title = SECTION_TITLES.get(key, key.replace("_", " ").title())
            self.sections[key] = AnalysisSection(key=key, title=title)
        return self.sections[key]

    def add(self, passed: bool, description: str, details: str | None = None, *, section: str = SECTION_PROCEDURAL) -> None:
        self._get_section(section).add(passed=passed, description=description, details=details)

    def render(self) -> str:
        lines: list[str] = [f"Verification report for '{self.project_name}':", "==== IWA Analysis (autoppia_iwa) ===="]
        for section_key in SECTION_ORDER:
            section = self.sections.get(section_key)
            title = SECTION_TITLES.get(section_key, section_key.replace("_", " ").title())
            if not section:
                lines.append(f"- {title}: ⚪ Not run")
                continue
            lines.append(f"- {title}: {'PASS' if section.ok else 'FAIL'}")
            for check in section.checks:
                flag = "✅" if check.passed else "❌"
                details = f" ({check.details})" if check.details else ""
                lines.append(f"    {flag} {check.description}{details}")
        lines.append("\n==== Web Project Analysis (modules/webs_demo) ====")
        if not self.web_analysis:
            lines.append("- ⚪ Not run (see markdown report for frontend findings)")
        else:
            frontend_dir = self.web_analysis.frontend_dir
            lines.append(f"- Frontend source: {'✅ ' + str(frontend_dir) if frontend_dir else '❌ Not located'}")
            total_events = len(self.web_analysis.event_results)
            missing_events = [res.event_name for res in self.web_analysis.event_results if not res.passed]
            if total_events:
                lines.append(f"- Event emissions: ✅ {total_events - len(missing_events)}/{total_events} matched")
                if missing_events:
                    preview = ", ".join(missing_events[:5])
                    suffix = " ..." if len(missing_events) > 5 else ""
                    lines.append(f"    Missing: {preview}{suffix}")
            else:
                lines.append("- Event emissions: ⚪ No events defined")
            for layer in self.web_analysis.dynamic_layers:
                flag = "✅" if layer.passed else "❌"
                detail = f" ({layer.evidence})" if layer.evidence else ""
                lines.append(f"- {layer.title}: {flag}{detail}")
            for issue in self.web_analysis.issues:
                lines.append(f"- ⚠️ {issue}")
        lines.append("\n==== Random Baseline ====")
        if self.random_stats:
            attempts = self.random_stats.get("attempts", 0)
            successes = self.random_stats.get("successes", 0)
            check = "✅ " if successes == 0 else ""
            lines.append(f"- {check}RandomClicker: {successes}/{attempts} successes (goal 0)")
            errors = self.random_stats.get("errors")
            if errors:
                lines.append(f"    Errors: {errors}")
        else:
            lines.append("- RandomClicker: ⚪ Not run")
        if self.miner_stats:
            lines.append("- Miner agent: ⚪ Not run (legacy field)")
        lines.append("\n==== Dynamic Validation ====")
        if not self.dynamic_stats:
            lines.append("- ⚪ Not run")
        else:
            expect = "yes" if self.dynamic_stats.get("expect_mutations") else "no"
            lines.append(f"- Expect mutations per deck: {expect}")
            for entry in self.dynamic_stats.get("pages", []):
                page_id = entry.get("page_id")
                details: list[str] = []
                base_sim = entry.get("base_similarity")
                if base_sim is not None:
                    details.append(f"base sim={base_sim:.4f}")
                deltas = entry.get("base_deltas") or []
                if deltas:
                    preview = ", ".join(f"s{seed}:{delta:.3f}" for seed, delta in deltas[:3])
                    details.append(f"Δ(base→seed)={preview}")
                llm_pass = entry.get("llm_pass")
                if llm_pass is not None:
                    details.append(f"LLM={'PASS' if llm_pass else 'FAIL'}")
                issues = entry.get("issues")
                if issues:
                    details.append(f"issues={'; '.join(issues[:2])}")
                lines.append(f"- {page_id}: " + ("; ".join(details) if details else "⚪ No metrics"))
        lines.append(f"\nOverall result: {'PASS' if self.ok else 'FAIL'}")
        if self.sections:
            failing_sections = [title for key, title in SECTION_TITLES.items() if key in self.sections and not self.sections[key].ok]
            if failing_sections:
                notes = "; ".join(failing_sections)
                lines.append(f"Notes: ❌ Issues detected in {notes}")
            else:
                lines.append("Notes: ✅ All gates passed. Review web analysis warnings if any.")
        return "\n".join(lines)


def _deck_candidate_paths(project_slug: str) -> list[Path]:
    candidates: list[Path] = []
    if not DECKS_BASE.exists():
        return candidates
    slug_options: list[str] = []
    alias = DECK_ALIASES.get(project_slug)
    if alias:
        slug_options.append(alias)
    slug_options.append(project_slug)
    slug_options = list(dict.fromkeys(slug_options))
    search_roots = [DECKS_BASE]
    examples_dir = DECKS_BASE / "examples"
    if examples_dir.exists():
        search_roots.append(examples_dir)
    suffixes = (".deck.json", ".json")
    for root in search_roots:
        for slug in slug_options:
            for suffix in suffixes:
                direct = root / f"{slug}{suffix}"
                if direct.exists():
                    candidates.append(direct)
            candidates.extend(root.glob(f"{slug}*.deck.json"))
    return candidates


def _read_float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _read_int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _bootstrap_llm_from_env():
    provider = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    if not provider:
        return None, RuntimeError("LLM_PROVIDER environment variable is not configured")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, RuntimeError("OPENAI_API_KEY is not configured")
        config = LLMConfig(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=_read_float_env("OPENAI_TEMPERATURE", 0.7),
            max_tokens=_read_int_env("OPENAI_MAX_TOKENS", 2000),
        )
        return LLMFactory.create_llm("openai", config, api_key=api_key), None

    if provider == "chutes":
        base_url = os.getenv("CHUTES_BASE_URL")
        api_key = os.getenv("CHUTES_API_KEY")
        if not base_url or not api_key:
            return None, RuntimeError("CHUTES_BASE_URL/CHUTES_API_KEY are not configured")
        config = LLMConfig(
            model=os.getenv("CHUTES_MODEL", "unsloth/Llama-3.2-3B-Instruct"),
            temperature=_read_float_env("CHUTES_TEMPERATURE", 0.7),
            max_tokens=_read_int_env("CHUTES_MAX_TOKENS", 2048),
        )
        use_bearer = os.getenv("CHUTES_USE_BEARER", "false").strip().lower() in {"1", "true", "yes"}
        return LLMFactory.create_llm("chutes", config, base_url=base_url, api_key=api_key, use_bearer=use_bearer), None

    if provider == "local":
        endpoint = os.getenv("LOCAL_LLM_ENDPOINT")
        if not endpoint:
            return None, RuntimeError("LOCAL_LLM_ENDPOINT is not configured for local provider")
        config = LLMConfig(
            model=os.getenv("LOCAL_LLM_MODEL", "local-model"),
            temperature=_read_float_env("LOCAL_LLM_TEMPERATURE", 0.7),
            max_tokens=_read_int_env("LOCAL_LLM_MAX_TOKENS", 1024),
        )
        return LLMFactory.create_llm("local", config, endpoint_url=endpoint), None

    return None, RuntimeError(f"Unsupported LLM_PROVIDER '{provider}'")


def _load_deck_for_project(project_slug: str, report: ProjectReport, deck_override: Path | None = None) -> tuple[WebProjectDeck | None, Path | None]:
    deck_path = deck_override
    if deck_path is None:
        candidates = _deck_candidate_paths(project_slug)
        if not candidates:
            report.add(False, "Deck file exists", f"No deck file found under {DECKS_BASE}", section=SECTION_DECK)
            return None, None
        deck_path = candidates[0]
    try:
        deck = WebProjectDeck.load(deck_path)
    except Exception as exc:  # pragma: no cover - parsing errors bubble up in CLI
        report.add(False, "Deck parses correctly", f"{deck_path}: {exc}", section=SECTION_DECK)
        return None, deck_path
    report.add(True, "Deck parses correctly", str(deck_path), section=SECTION_DECK)
    return deck, deck_path


def _validate_deck_against_project(deck: WebProjectDeck | None, web_project: WebProject | None, report: ProjectReport) -> None:
    if not deck:
        return
    if not web_project:
        report.add(False, "WebProject loaded to compare deck", "Procedural phase failed", section=SECTION_DECK)
        return

    matches_id = deck.metadata.project_id == web_project.id
    report.add(matches_id, "Deck project_id matches WebProject.id", f"{deck.metadata.project_id} vs {web_project.id}" if not matches_id else None, section=SECTION_DECK)

    matches_name = deck.metadata.project_name == web_project.name
    report.add(matches_name, "Deck project_name matches WebProject.name", None if matches_name else f"{deck.metadata.project_name} vs {web_project.name}", section=SECTION_DECK)

    deck_use_cases = {uc.name: uc for uc in deck.use_cases}
    project_use_cases = {uc.name: uc for uc in (web_project.use_cases or [])}

    missing_in_code = sorted(deck_use_cases.keys() - project_use_cases.keys())
    extra_in_code = sorted(project_use_cases.keys() - deck_use_cases.keys())
    report.add(
        not missing_in_code,
        "All deck use cases exist in WebProject",
        None if not missing_in_code else ", ".join(missing_in_code),
        section=SECTION_DECK,
    )
    report.add(
        not extra_in_code,
        "No extra use cases beyond deck definition",
        None if not extra_in_code else ", ".join(extra_in_code),
        section=SECTION_DECK,
    )

    event_mismatch: list[str] = []
    for name, spec in deck_use_cases.items():
        if name not in project_use_cases:
            continue
        project_event_name = getattr(project_use_cases[name].event, "__name__", "")
        if project_event_name != spec.event:
            event_mismatch.append(f"{name} (deck={spec.event}, code={project_event_name})")
    report.add(not event_mismatch, "Use case events match deck", None if not event_mismatch else "; ".join(event_mismatch), section=SECTION_DECK)

    report.add(bool(deck.pages), "Deck declares required pages", None if deck.pages else "pages list is empty", section=SECTION_DECK)


def _obtain_llm_service() -> tuple[Any | None, Exception | None]:
    di_error: Exception | None = None
    if DI is not None:
        try:
            service = DI.llm_service()
            if service is not None:
                return service, None
            di_error = RuntimeError("LLM service not configured in DI container")
        except Exception as exc:
            di_error = exc
    else:
        di_error = DI_ERROR or RuntimeError("DI container unavailable")

    env_service, env_error = _bootstrap_llm_from_env()
    if env_service is not None:
        return env_service, None
    return None, env_error or di_error


def discover_web_project(module: Any) -> WebProject | None:
    for _, value in inspect.getmembers(module):
        if isinstance(value, WebProject):
            return value
    return None


def load_module(path_fragment: str):
    return importlib.import_module(f"{MODULE_PREFIX}.{path_fragment}")


def ensure_required_files(project_dir: Path, required: Iterable[str]) -> list[str]:
    missing = []
    for fname in required:
        if not (project_dir / fname).exists():
            missing.append(fname)
    return missing


def verify_project(project_slug: str, deck_path: Path | None = None) -> tuple[ProjectReport, WebProject | None]:
    report = ProjectReport(project_name=project_slug)
    web_project: WebProject | None = None

    project_dir = PROJECTS_BASE / project_slug
    if not project_dir.exists():
        report.add(False, "Project directory exists", f"Missing directory {project_dir}", section=SECTION_PROCEDURAL)
        return report, None

    required_files = ("main.py", "use_cases.py", "events.py", "generation_functions.py")
    missing = ensure_required_files(project_dir, required_files)
    if missing:
        report.add(False, "Required files present", f"Missing: {', '.join(missing)}", section=SECTION_PROCEDURAL)
    else:
        report.add(True, "Required files present", section=SECTION_PROCEDURAL)

    # Import modules
    try:
        main_module = load_module(f"{project_slug}.main")
    except Exception as exc:  # pragma: no cover - defensive
        report.add(False, "Import main module", f"{exc}", section=SECTION_PROCEDURAL)
        return report, None

    web_project = discover_web_project(main_module)
    if not web_project:
        report.add(False, "Main module exposes WebProject instance", "No WebProject object found", section=SECTION_PROCEDURAL)
        return report, None

    web_project_checks = [
        (bool(web_project.id), "WebProject has id"),
        (bool(web_project.name), "WebProject has name"),
        (bool(getattr(web_project, "frontend_url", "")), "WebProject has frontend_url"),
        (web_project.use_cases is not None, "WebProject attaches use cases"),
    ]
    for ok, desc in web_project_checks:
        report.add(ok, desc, section=SECTION_PROCEDURAL)

    deck, _ = _load_deck_for_project(project_slug, report, deck_override=deck_path)
    report.deck = deck
    _validate_deck_against_project(deck, web_project, report)

    try:
        use_cases_module = load_module(f"{project_slug}.use_cases")
    except Exception as exc:
        report.add(False, "Import use_cases module", f"{exc}", section=SECTION_USE_CASES)
        return report, web_project

    use_cases: list[UseCase] | None = getattr(use_cases_module, "ALL_USE_CASES", None)
    if not use_cases:
        report.add(False, "ALL_USE_CASES defined", "ALL_USE_CASES missing or empty", section=SECTION_USE_CASES)
        return report, web_project
    if not all(isinstance(uc, UseCase) for uc in use_cases):
        report.add(False, "ALL_USE_CASES contains only UseCase instances", section=SECTION_USE_CASES)
    else:
        report.add(True, "ALL_USE_CASES contains UseCase instances", section=SECTION_USE_CASES)

    names = [uc.name for uc in use_cases]
    duplicates = {name for name in names if names.count(name) > 1}
    report.add(
        not duplicates,
        "Use case names are unique",
        f"Duplicates: {', '.join(sorted(duplicates))}" if duplicates else None,
        section=SECTION_USE_CASES,
    )

    missing_examples = [uc.name for uc in use_cases if not getattr(uc, "examples", None)]
    report.add(
        not missing_examples,
        "Each use case declares example prompts",
        f"Missing examples: {', '.join(missing_examples)}" if missing_examples else None,
        section=SECTION_USE_CASES,
    )
    missing_descriptions = [uc.name for uc in use_cases if not getattr(uc, "description", "").strip()]
    report.add(
        not missing_descriptions,
        "Each use case has a description",
        f"Missing descriptions: {', '.join(missing_descriptions)}" if missing_descriptions else None,
        section=SECTION_USE_CASES,
    )

    bad_example_fields: list[str] = []
    for uc in use_cases:
        for idx, example in enumerate(getattr(uc, "examples", []) or []):
            if not isinstance(example, dict):
                bad_example_fields.append(f"{uc.name}[{idx}] not a dict")
                continue
            if not example.get("prompt"):
                bad_example_fields.append(f"{uc.name}[{idx}] missing prompt")
            if not example.get("prompt_for_task_generation"):
                bad_example_fields.append(f"{uc.name}[{idx}] missing prompt_for_task_generation")

    report.add(
        not bad_example_fields,
        "Example prompts include prompt & prompt_for_task_generation",
        "; ".join(bad_example_fields) if bad_example_fields else None,
        section=SECTION_USE_CASES,
    )

    try:
        events_module = load_module(f"{project_slug}.events")
        events_list = getattr(events_module, "EVENTS", None)
    except Exception as exc:
        report.add(False, "Import events module", f"{exc}", section=SECTION_USE_CASES)
        events_list = None

    if events_list is None:
        report.add(False, "EVENTS list defined", "EVENTS missing", section=SECTION_USE_CASES)
    else:
        report.add(True, "EVENTS list defined", section=SECTION_USE_CASES)
        event_classes = {event.__name__: event for event in events_list if inspect.isclass(event)}
        uc_without_event = [uc.name for uc in use_cases if not getattr(uc, "event", None)]
        report.add(
            not uc_without_event,
            "Each use case references an event",
            f"No event for: {', '.join(uc_without_event)}" if uc_without_event else None,
            section=SECTION_USE_CASES,
        )

        mismatch = [uc.name for uc in use_cases if getattr(uc, "event", None) and getattr(uc.event, "__name__", None) not in event_classes]
        report.add(
            not mismatch,
            "Use case events exist in EVENTS",
            f"Missing event classes: {', '.join(mismatch)}" if mismatch else None,
            section=SECTION_USE_CASES,
        )
        slug_prefix = project_slug.split("_")[0].lower()
        seen_event_names: set[str] = set()
        duplicate_issues: list[str] = []
        namespace_notes: list[str] = []
        schema_notes: list[str] = []
        ALLOW_SCHEMALESS_EVENTS = {"VIEW_CART"}
        for uc in use_cases:
            event_class = getattr(uc, "event", None)
            if not event_class:
                continue
            event_name = getattr(event_class, "event_name", getattr(event_class, "__name__", ""))
            if event_name in seen_event_names:
                duplicate_issues.append(f"{uc.name}: duplicate event_name '{event_name}'")
            seen_event_names.add(event_name)
            if slug_prefix and slug_prefix not in (event_name or "").lower():
                namespace_notes.append(f"{uc.name}: event '{event_name}' lacks slug prefix '{slug_prefix}'")
            constraints_defined = bool(getattr(uc, "constraints", None))
            constraints_generator = getattr(uc, "constraints_generator", None)
            generator_defined = constraints_generator not in (None, False)
            requires_schema = constraints_defined or generator_defined
            if event_name in ALLOW_SCHEMALESS_EVENTS or not requires_schema:
                continue
            criteria_cls = getattr(event_class, "ValidationCriteria", None)
            if not criteria_cls:
                schema_notes.append(f"{uc.name}: ValidationCriteria missing")
                continue
            fields = getattr(criteria_cls, "model_fields", None)
            if fields is None:
                fields = getattr(criteria_cls, "__fields__", None)
            if not fields:
                schema_notes.append(f"{uc.name}: ValidationCriteria empty")

        report.add(
            not duplicate_issues,
            "Event names unique",
            "; ".join(duplicate_issues) if duplicate_issues else None,
            section=SECTION_USE_CASES,
        )
        report.add(
            not schema_notes,
            "Event schemas declared",
            "; ".join(schema_notes) if schema_notes else None,
            section=SECTION_USE_CASES,
        )

    try:
        generation_module = load_module(f"{project_slug}.generation_functions")
        generation_symbols = set(name for name, obj in inspect.getmembers(generation_module, inspect.isfunction))
    except Exception as exc:
        report.add(False, "Import generation_functions module", f"{exc}", section=SECTION_USE_CASES)
        generation_symbols = set()

    missing_generators = []
    for uc in use_cases:
        generator = getattr(uc, "constraints_generator", None)
        if generator and generator is not False:
            gen_name = getattr(generator, "__name__", None)
            if gen_name not in generation_symbols:
                missing_generators.append(f"{uc.name} -> {gen_name}")
    report.add(
        not missing_generators,
        "Constraint generators resolve to generation_functions",
        f"Missing generators: {', '.join(missing_generators)}" if missing_generators else None,
        section=SECTION_USE_CASES,
    )

    return report, web_project


async def _generate_tasks_via_pipeline(web_project: WebProject) -> list[Task]:
    use_case_names = [uc.name for uc in (web_project.use_cases or [])]
    selected_names = use_case_names[:3] if use_case_names else None
    config = TaskGenerationConfig(
        prompts_per_use_case=1,
        num_use_cases=min(3, len(use_case_names)) if use_case_names else 1,
        use_cases=selected_names,
    )
    llm_service, llm_error = _obtain_llm_service()
    if llm_service is None:
        raise RuntimeError(f"LLM service unavailable: {llm_error}")
    pipeline = TaskGenerationPipeline(web_project=web_project, config=config, llm_service=llm_service)
    tasks = await pipeline.generate()
    return tasks or []


def _ensure_task_entry(task_summaries: dict[str, dict], task: Task) -> dict:
    entry = task_summaries.setdefault(
        task.id,
        {
            "use_case": getattr(task.use_case, "name", "Unknown"),
            "prompt": task.prompt,
            "prompt_status": "PROMPT_PENDING",
            "test_status": "TEST_PENDING",
            "test_generation_status": "NOT_RUN",
            "random_status": "NOT_RUN",
            "agent_status": "NOT_RUN",
            "semantic_status": "NOT_RUN",
        },
    )
    return entry


def _limit_tasks_per_use_case(tasks: list[Task], per_use_case: int) -> list[Task]:
    if per_use_case <= 0:
        return tasks
    grouped: dict[str, list[Task]] = defaultdict(list)
    selected: list[Task] = []
    for task in tasks:
        uc_name = getattr(task.use_case, "name", "Unknown")
        if len(grouped[uc_name]) < per_use_case:
            grouped[uc_name].append(task)
            selected.append(task)
    return selected


async def _check_frontend_health(url: str) -> tuple[bool, str]:
    if not url:
        return False, "frontend_url not configured"
    try:
        async with aiohttp.ClientSession() as session, session.get(url, timeout=5) as resp:
            if resp.status == 200:
                return True, "HTTP 200"
            return False, f"Status {resp.status}"
    except Exception as exc:
        return False, str(exc)


def _check_task_prompts(
    tasks: list,
    report: ProjectReport,
    task_summaries: dict[str, dict],
    *,
    section: str = SECTION_LLM_TASKS,
) -> None:
    if not tasks:
        report.add(False, "Generated tasks available", "No tasks available for validation", section=section)
        return

    placeholder_failures: list[str] = []
    constraint_failures: list[str] = []
    prompt_states: dict[str, str] = {task.id: "PROMPT_OK" for task in tasks}

    for task in tasks:
        _ensure_task_entry(task_summaries, task)
        prompt_lower = (task.prompt or "").lower()
        if "<constraints_info>" in prompt_lower:
            placeholder_failures.append(task.id)
            prompt_states[task.id] = "PROMPT_FAIL"

        use_case = getattr(task, "use_case", None)
        constraints = getattr(use_case, "constraints", None) if use_case else None
        if constraints:
            for constraint in constraints:
                value = constraint.get("value")
                field = constraint.get("field")
                if _is_sensitive_field(field):
                    continue
                values = value if isinstance(value, list) else [value]
                for val in values:
                    if val is None:
                        continue
                    sval = str(val).strip().lower()
                    if sval and sval not in prompt_lower:
                        constraint_failures.append(f"{task.id}:{field}->{val}")
                        prompt_states[task.id] = "PROMPT_FAIL"

    report.add(
        not placeholder_failures,
        "Task prompts have constraints resolved",
        f"Tasks with unresolved placeholders: {', '.join(placeholder_failures)}" if placeholder_failures else None,
        section=section,
    )
    report.add(
        not constraint_failures,
        "Task prompts mention constraint values",
        f"Issues: {', '.join(constraint_failures[:20])}" + (" ..." if len(constraint_failures) > 20 else "") if constraint_failures else None,
        section=section,
    )
    for task_id, state in prompt_states.items():
        entry = task_summaries.get(task_id)
        if entry:
            entry["prompt_status"] = state


def _validate_check_event_tests(
    tasks: list,
    report: ProjectReport,
    task_summaries: dict[str, dict],
    *,
    section: str = SECTION_LLM_TESTS,
) -> None:
    from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest

    if not tasks:
        report.add(False, "LLM tests available", "No tasks available for test validation", section=section)
        return

    test_failures: list[str] = []
    test_states: dict[str, str] = {task.id: "TEST_OK" for task in tasks}

    for task in tasks:
        _ensure_task_entry(task_summaries, task)
        use_case = getattr(task, "use_case", None)
        check_tests = [t for t in task.tests if isinstance(t, CheckEventTest)]
        if not check_tests:
            test_failures.append(f"{task.id}:missing CheckEventTest")
            test_states[task.id] = "TEST_FAIL"
            continue

        if use_case:
            expected_variants = {
                getattr(use_case.event, "__name__", None),
                getattr(use_case.event, "event_name", None),
                getattr(use_case, "name", None),
            }
            expected_variants = {v for v in expected_variants if v}
            for t in check_tests:
                if expected_variants and t.event_name not in expected_variants:
                    exp = ", ".join(sorted(expected_variants))
                    test_failures.append(f"{task.id}:expected {exp}, got {t.event_name}")
                    test_states[task.id] = "TEST_FAIL"

    report.add(
        not test_failures,
        "Tasks include aligned CheckEventTest",
        f"Issues: {', '.join(test_failures)}" if test_failures else None,
        section=section,
    )
    for task_id, state in test_states.items():
        entry = task_summaries.get(task_id)
        if entry:
            entry["test_status"] = state


def _run_llm_test_generation_pipeline(
    web_project: WebProject,
    tasks: list[Task],
    report: ProjectReport,
    task_summaries: dict[str, dict],
) -> None:
    section = SECTION_LLM_TESTS
    if not tasks:
        report.add(False, "LLM test generation tasks available", "No tasks available for test generation", section=section)
        return

    llm_service, llm_error = _obtain_llm_service()
    if llm_service is None:
        report.add(False, "Initialize LLM service for test generation", f"{llm_error}", section=section)
        return

    pipeline = GlobalTestGenerationPipeline(web_project=web_project, llm_service=llm_service)
    before_counts = {task.id: len(task.tests) for task in tasks}
    try:
        asyncio.run(pipeline.add_tests_to_tasks(tasks))
    except Exception as exc:
        report.add(False, "LLM test generation pipeline execution", f"{exc}", section=section)
        return

    tasks_with_new_tests: list[str] = []
    tasks_without_tests: list[str] = []
    for task in tasks:
        entry = _ensure_task_entry(task_summaries, task)
        before = before_counts.get(task.id, 0)
        after = len(task.tests)
        if after > before:
            tasks_with_new_tests.append(task.id)
            entry["test_generation_status"] = "TESTS_ADDED"
        elif after > 0:
            entry["test_generation_status"] = "ALREADY_PRESENT"
        else:
            tasks_without_tests.append(task.id)
            entry["test_generation_status"] = "NO_TESTS"

    details: list[str] = []
    if tasks_with_new_tests:
        details.append(f"Tests added for {len(tasks_with_new_tests)} task(s)")
    if tasks_without_tests:
        preview = ", ".join(tasks_without_tests[:5])
        suffix = " ..." if len(tasks_without_tests) > 5 else ""
        details.append(f"No tests produced for: {preview}{suffix}")

    report.add(
        not tasks_without_tests,
        "LLM test generation pipeline",
        "; ".join(details) if details else None,
        section=section,
    )
    _validate_check_event_tests(tasks, report, task_summaries, section=section)


def _execute_dynamic_gate(report: ProjectReport, web_project: WebProject) -> None:
    base_url = _resolve_dynamic_base_url(web_project, report.deck)
    llm_service, _ = _obtain_llm_service()
    try:
        outcome = asyncio.run(
            run_dynamic_validation(
                deck=report.deck,
                base_url=base_url,
                llm_service=llm_service,
                config=DynamicGateConfig(),
            )
        )
    except Exception as exc:
        report.add(False, "Dynamic validation execution", str(exc), section=SECTION_DYNAMIC)
        return
    _apply_dynamic_outcome(report, outcome)


def _apply_dynamic_outcome(report: ProjectReport, outcome: DynamicValidationOutcome) -> None:
    report.dynamic_stats = outcome.to_dict()
    llm_pass = outcome.llm_review_pass()
    llm_feedback = outcome.llm_feedback()
    llm_override = bool(llm_pass and outcome.expect_mutations)
    if outcome.errors:
        for err in outcome.errors:
            report.add(False, "Dynamic validation prerequisites", err, section=SECTION_DYNAMIC)
        return
    if not outcome.page_results:
        report.add(False, "Dynamic validation data points", "No pages evaluated", section=SECTION_DYNAMIC)
        return

    report.add(
        outcome.seedless_stable(),
        "Seedless views remain stable",
        _format_base_similarity(outcome),
        section=SECTION_DYNAMIC,
    )
    report.add(
        outcome.reproducible(),
        "Seeded runs reproducible",
        _format_reproducibility(outcome),
        section=SECTION_DYNAMIC,
    )
    if outcome.expect_mutations:
        mutation_pass = outcome.mutations_behave()
        mutation_details = _format_base_deltas(outcome)
        if not mutation_pass and llm_override:
            mutation_pass = True
            mutation_details = _with_llm_override_note(mutation_details)
        report.add(
            mutation_pass,
            "Seeded runs mutate DOM per deck",
            mutation_details,
            section=SECTION_DYNAMIC,
        )
        cross_seed_pass = outcome.cross_seed_ok()
        cross_seed_details = _format_cross_seed_deltas(outcome)
        if not cross_seed_pass and llm_override:
            cross_seed_pass = True
            cross_seed_details = _with_llm_override_note(cross_seed_details)
        report.add(
            cross_seed_pass,
            "Different seeds diverge",
            cross_seed_details,
            section=SECTION_DYNAMIC,
        )
    else:
        report.add(
            outcome.mutations_behave(),
            "Seeded runs stay stable (deck says no mutations)",
            _format_base_deltas(outcome),
            section=SECTION_DYNAMIC,
        )

    llm_pass = outcome.llm_review_pass()
    if llm_pass is not None:
        report.add(llm_pass, "LLM dynamic review", llm_feedback, section=SECTION_DYNAMIC)


def _format_base_similarity(outcome: DynamicValidationOutcome) -> str | None:
    parts = []
    for result in outcome.page_results:
        if result.base_similarity is None:
            continue
        parts.append(f"{result.page_id}:{result.base_similarity:.4f}")
    return ", ".join(parts) if parts else None


def _format_reproducibility(outcome: DynamicValidationOutcome) -> str | None:
    parts = []
    for result in outcome.page_results:
        if not result.reproducibility:
            continue
        entries = []
        for seed, ratio in result.reproducibility:
            label = "no-seed" if seed is None else f"s{seed}"
            entries.append(f"{label}:{ratio:.4f}")
        parts.append(f"{result.page_id}({', '.join(entries)})")
    return "; ".join(parts) if parts else None


def _format_base_deltas(outcome: DynamicValidationOutcome) -> str | None:
    parts = []
    for result in outcome.page_results:
        if not result.base_deltas:
            continue
        entries = [f"s{seed}:{delta:.3f}" for seed, delta in result.base_deltas]
        parts.append(f"{result.page_id}({', '.join(entries)})")
    return "; ".join(parts) if parts else None


def _format_cross_seed_deltas(outcome: DynamicValidationOutcome) -> str | None:
    parts = []
    for result in outcome.page_results:
        if not result.cross_seed_deltas:
            continue
        entries = [f"s{pair[0]}-s{pair[1]}:{delta:.3f}" for pair, delta in result.cross_seed_deltas]
        parts.append(f"{result.page_id}({', '.join(entries)})")
    return "; ".join(parts) if parts else None


def _with_llm_override_note(details: str | None) -> str:
    note = "LLM override: heuristics saw low delta but review passed"
    return f"{details}; {note}" if details else note


def _resolve_dynamic_base_url(web_project: WebProject | None, deck: WebProjectDeck | None) -> str | None:
    if web_project and getattr(web_project, "frontend_url", ""):
        return web_project.frontend_url
    deployment = getattr(deck.metadata, "deployment", None) if deck and deck.metadata else None
    if deployment and getattr(deployment, "preview_base_url", None):
        return deployment.preview_base_url
    return None


def _format_constraints(use_case: UseCase | None) -> str:
    if not use_case or not getattr(use_case, "constraints", None):
        return "None"
    fragments = []
    for c in use_case.constraints:
        field = c.get("field")
        op = c.get("operator")
        val = c.get("value")
        fragments.append(f"{field} {op} {val}")
    return "; ".join(fragments)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    match = CODE_FENCE_RE.search(stripped)
    if match:
        return match.group(1).strip()
    return stripped


SENSITIVE_FIELD_KEYS = {"password", "pass", "pwd", "token", "otp", "secret"}


def _is_sensitive_field(field: str | None) -> bool:
    if not field:
        return False
    lower = field.lower()
    return any(key in lower for key in SENSITIVE_FIELD_KEYS)


def _parse_llm_json_response(raw_response: Any) -> dict[str, Any]:
    if isinstance(raw_response, dict):
        return raw_response
    if not isinstance(raw_response, str):
        raise ValueError("LLM response is not a JSON string")

    cleaned = _strip_code_fences(raw_response)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        fallback = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if fallback:
            return json.loads(fallback.group(0))
        raise


async def _llm_validate_tasks(
    tasks: list,
    sample_size: int,
    report: ProjectReport,
    task_summaries: dict[str, dict],
    *,
    section: str = SECTION_LLM_TASKS,
) -> None:
    llm_service, llm_error = _obtain_llm_service()
    if llm_service is None:
        report.add(False, "Initialize LLM service", f"{llm_error}", section=section)
        return

    if not tasks:
        report.add(False, "LLM validation tasks available", "No tasks to validate", section=section)
        return

    selected = tasks
    if sample_size > 0:
        selected = random.sample(tasks, min(sample_size, len(tasks)))

    failures: list[tuple[str, str]] = []

    system_prompt = (
        "You are verifying that a benchmark task prompt correctly restates every business constraint. "
        'Respond strictly in JSON with the shape {"compliant": bool, "issues": ["..."]}. '
        "If the prompt is missing any constraint or adds unrelated instructions, set compliant to false and explain."
    )

    for task in selected:
        use_case = getattr(task, "use_case", None)
        constraints_str = _format_constraints(use_case)
        description = getattr(use_case, "description", "")
        user_prompt = f"Use case name: {getattr(use_case, 'name', 'unknown')}\nUse case description: {description}\nConstraints: {constraints_str}\nTask prompt:\n{task.prompt}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_response: Any = None
        try:
            raw_response = await asyncio.wait_for(
                llm_service.async_predict(messages=messages, json_format=True, return_raw=False),
                timeout=LLM_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            failures.append((task.id, f"LLM request error: {exc}"))
            print(f"    -> LLM request failed for task {task.id}: {exc}")
            continue

        try:
            result = _parse_llm_json_response(raw_response)
            compliant = bool(result.get("compliant"))
            issues = result.get("issues") or []
        except Exception as exc:
            snippet = raw_response if isinstance(raw_response, str) else str(raw_response)
            snippet = (snippet[:200] + "...") if snippet and len(snippet) > 200 else snippet
            failures.append((task.id, f"LLM parse error: {exc} | raw={snippet!r}"))
            print(f"    -> LLM parse error for task {task.id}: {exc}. Raw response: {snippet!r}")
            entry = task_summaries.get(task.id)
            if entry and entry.get("prompt_status") == "PROMPT_OK":
                entry["prompt_status"] = "PROMPT_WARN"
            continue

        if not compliant:
            reason = "; ".join(str(issue) for issue in issues) if issues else "LLM flagged mismatch"
            failures.append((task.id, reason))

    report.add(
        not failures,
        "LLM validation of prompts",
        f"Issues: {', '.join(f'{task_id}: {reason}' for task_id, reason in failures[:10])}" + (" ..." if len(failures) > 10 else "") if failures else None,
        section=section,
    )
    for task_id, _ in failures:
        entry = task_summaries.get(task_id)
        if entry and entry.get("prompt_status") == "PROMPT_OK":
            entry["prompt_status"] = "PROMPT_WARN"


async def _evaluate_tasks_with_agent(web_project: WebProject, tasks: list[Task], agent) -> tuple[list[tuple[Task, Any]], list[str]]:
    if not tasks:
        return [], []
    evaluator = ConcurrentEvaluator(
        web_project,
        EvaluatorConfig(
            enable_grouping_tasks=False,
            chunk_size=max(1, len(tasks)),
            should_record_gif=False,
            verbose_logging=False,
        ),
    )
    evaluations: list[tuple[Task, Any]] = []
    errors: list[str] = []
    for task in tasks:
        try:
            solution = await agent.solve_task(task)
            if not getattr(solution, "web_agent_id", None):
                solution.web_agent_id = getattr(agent, "id", getattr(agent, "name", "unknown_agent"))
            print(f"    -> Agent '{getattr(agent, 'name', 'agent')}' produced {len(solution.actions)} actions for task {task.id}")
            result = await evaluator.evaluate_single_task_solution(task, solution)
            evaluations.append((task, result))
        except Exception as exc:
            dummy = type("Result", (), {"final_score": 0, "stats": None, "execution_history": [], "error": str(exc)})
            evaluations.append((task, dummy))
            print(f"    -> Agent '{getattr(agent, 'name', 'agent')}' failed on task {task.id}: {exc}")
            errors.append(f"{task.id}: {exc}")
    return evaluations, errors


def _summarize_execution(history) -> str:
    if not history:
        return "No actions executed"
    lines = []
    for record in history[:10]:
        action = getattr(record, "action_event", "action")
        success = getattr(record, "successfully_executed", False)
        lines.append(f"{action} -> {'OK' if success else 'FAIL'}")
    if len(history) > 10:
        lines.append("... (truncated)")
    return "\n".join(lines)


async def _semantic_check_solutions(success_results: list[tuple[Task, Any]], task_summaries: dict[str, dict]) -> None:
    if not success_results:
        return

    llm_service, llm_error = _obtain_llm_service()
    if llm_service is None:
        for task, _ in success_results:
            entry = task_summaries.get(task.id)
            if entry:
                entry["semantic_status"] = "WARNING"
                entry["semantic_details"] = f"LLM unavailable ({llm_error})"
        return

    system_prompt = 'You are validating whether a sequence of browser actions makes sense for a given task prompt.\nReply in JSON: {"coherent": bool, "warnings": ["..."]}.'

    for task, result in success_results:
        history_summary = _summarize_execution(getattr(result, "execution_history", []))
        user_prompt = f"Task prompt:\n{task.prompt}\n\nUse case: {getattr(task.use_case, 'name', 'unknown')}\nAction trace:\n{history_summary}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        verdict = {"coherent": True, "warnings": []}
        try:
            raw = await asyncio.wait_for(
                llm_service.async_predict(messages=messages, json_format=True, return_raw=False),
                timeout=LLM_TIMEOUT_SECONDS,
            )
            verdict = json.loads(raw) if isinstance(raw, str) else raw
        except Exception as exc:
            verdict = {"coherent": False, "warnings": [f"LLM error: {exc}"]}

        entry = task_summaries.get(task.id)
        if not entry:
            continue
        if verdict.get("coherent", True):
            entry["semantic_status"] = "PASS"
        else:
            entry["semantic_status"] = "WARNING"
        warnings_list = verdict.get("warnings") or []
        if warnings_list:
            entry["semantic_details"] = "; ".join(str(w) for w in warnings_list)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify demo web projects")
    parser.add_argument("projects", nargs="*", help="Optional project slugs; leave empty to verify all projects")
    parser.add_argument("--deck", type=Path, help="Optional path to deck file when validating a single project")
    parser.add_argument("--config", type=Path, help="Path to config YAML/JSON to auto-generate the IWA module before verification.")
    parser.add_argument("--force-config", action="store_true", help="Overwrite existing module directory when --config is provided.")
    parser.add_argument("--code-checks", "--code_checks", action="store_true", help="Run code checks (procedural/deck/frontend). If neither flag is provided, both code and results checks run.")
    parser.add_argument("--results-checks", "--results_checks", action="store_true", help="Run results checks (LLM/dynamic/agent). If neither flag is provided, both code and results checks run.")
    parser.add_argument("--frontend-root", type=Path, help="Override the frontend/demo webs root directory (defaults to modules/webs_demo or ../autoppia_webs_demo).")
    parser.add_argument("--frontend-port", type=int, help="Override the frontend_url port (e.g., 8000 to hit a local dev server).")
    parser.add_argument("--frontend-base-url", help="Override the entire frontend_url (e.g., http://localhost:8000).")
    return parser.parse_args(list(argv))


def run_full_verification(
    project_slug: str,
    deck_path: Path | None = None,
    *,
    enable_code_checks: bool = True,
    enable_results_checks: bool = True,
    frontend_root: Path | None = None,
    override_frontend_url: str | None = None,
    override_frontend_port: int | None = None,
) -> tuple[ProjectReport, dict[str, dict], WebProject | None]:
    total_steps = 1  # procedural/deck/use-case checks always run to load the project
    if enable_code_checks:
        total_steps += 1  # frontend reachability probe
    if enable_results_checks:
        total_steps += 4  # task/test pipeline, dynamic, random, semantic
    if enable_code_checks:
        total_steps += 1  # frontend static analysis

    phase_bar = tqdm(total=total_steps, desc=f"{project_slug} phases", unit="phase", leave=False)
    step_idx = 1
    try:
        print(f"  [{step_idx}/{total_steps}] Metadata & deck checks…")
        report, web_project = verify_project(project_slug, deck_path=deck_path)
        print(f"    -> {'PASS' if report.ok else 'ISSUES DETECTED'} (see report below)")
        phase_bar.update(1)
        step_idx += 1
        task_summaries: dict[str, dict] = {}

        if not web_project:
            report.add(False, "Load WebProject for task validation", "No WebProject available", section=SECTION_PROCEDURAL)
            report.frontend_dir = _locate_frontend_dir(None, frontend_root)
            analysis = analyze_frontend(project_slug, report.frontend_dir)
            _attach_screenshot_reviews(analysis, getattr(web_project, "id", project_slug) if web_project else project_slug)
            report.web_analysis = analysis
            return report, task_summaries, None

        _apply_frontend_overrides(web_project, override_frontend_url, override_frontend_port)

        if enable_code_checks:
            print(f"  [{step_idx}/{total_steps}] Frontend reachability probe…")
            frontend_ok, frontend_detail = asyncio.run(_check_frontend_health(getattr(web_project, "frontend_url", "")))
            report.add(
                frontend_ok,
                "Frontend health check",
                frontend_detail if frontend_ok else f"Unreachable: {frontend_detail}",
                section=SECTION_PROCEDURAL,
            )
            print(f"    -> {'Reachable' if frontend_ok else 'Unavailable'} ({frontend_detail})")
            phase_bar.update(1)
            step_idx += 1
            if not frontend_ok:
                print("    -> Skipping remaining phases because frontend is unreachable.")
                report.frontend_dir = _locate_frontend_dir(web_project, frontend_root)
                analysis = analyze_frontend(project_slug, report.frontend_dir)
                _attach_screenshot_reviews(analysis, getattr(web_project, "id", project_slug) if web_project else project_slug)
                report.web_analysis = analysis
                return report, task_summaries, web_project

        tasks_for_checks: list[Task] = []
        generation_error = None

        if enable_results_checks:
            print(f"  [{step_idx}/{total_steps}] Task generation & prompt/test validation…")
            try:
                tasks_for_checks = asyncio.run(_generate_tasks_via_pipeline(web_project))
                if tasks_for_checks:
                    report.add(True, "Generate tasks via pipeline", section=SECTION_LLM_TASKS)
                    print(f"    -> Generated {len(tasks_for_checks)} tasks via pipeline")
                else:
                    generation_error = "Pipeline returned no tasks (LLM unavailable or misconfigured)"
                    report.add(False, "Generate tasks via pipeline", generation_error, section=SECTION_LLM_TASKS)
                    print(f"    -> Failed: {generation_error}")
            except Exception as exc:
                generation_error = str(exc)
                report.add(False, "Generate tasks via pipeline", generation_error, section=SECTION_LLM_TASKS)
                print(f"    -> Failed: {generation_error}")
            if tasks_for_checks:
                tasks_for_checks = _limit_tasks_per_use_case(tasks_for_checks, TASKS_PER_USE_CASE)
                for task in tasks_for_checks:
                    _ensure_task_entry(task_summaries, task)
                _check_task_prompts(tasks_for_checks, report, task_summaries, section=SECTION_LLM_TASKS)
                asyncio.run(_llm_validate_tasks(tasks_for_checks, LLM_SAMPLE_SIZE, report, task_summaries, section=SECTION_LLM_TASKS))
                _run_llm_test_generation_pipeline(web_project, tasks_for_checks, report, task_summaries)
            else:
                report.add(False, "Task validation skipped", generation_error or "No tasks available", section=SECTION_LLM_TASKS)
                print("    -> Skipping downstream phases (no tasks)")
            phase_bar.update(1)
            step_idx += 1

            print(f"  [{step_idx}/{total_steps}] Dynamic mutation validation…")
            _execute_dynamic_gate(report, web_project)
            phase_bar.update(1)
            step_idx += 1

            print(f"  [{step_idx}/{total_steps}] RandomClicker evaluation…")
            if tasks_for_checks:
                random_results, random_errors = asyncio.run(_evaluate_tasks_with_agent(web_project, tasks_for_checks, RandomClickerWebAgent(id="random_clicker", name="RandomClicker")))
                anomalies = [task.id for task, result in random_results if getattr(result, "final_score", 0) >= 1]
                for task, result in random_results:
                    entry = _ensure_task_entry(task_summaries, task)
                    entry["random_status"] = "RANDOM_OK" if getattr(result, "final_score", 0) == 0 else "RANDOM_ANOMALY"
                    entry["random_score"] = getattr(result, "final_score", 0)
                report.add(
                    not anomalies,
                    "RandomClicker evaluation",
                    None if not anomalies else f"Unexpected success on tasks: {', '.join(anomalies)}",
                    section=SECTION_LLM_TASKS,
                )
                report.random_stats = {
                    "attempts": len(random_results),
                    "successes": len(anomalies),
                    "errors": len(random_errors),
                }
                if random_errors:
                    report.add(False, "RandomClicker execution errors", "; ".join(random_errors), section=SECTION_LLM_TASKS)
                    print(f"    -> RandomClicker errors: {'; '.join(random_errors)}")
                if anomalies:
                    print(f"    -> RandomClicker anomalies on tasks: {', '.join(anomalies)}")
                else:
                    print("    -> RandomClicker produced 0 successes (expected)")
            else:
                print("    -> Skipped (no tasks)")
            phase_bar.update(1)
            step_idx += 1

            print(f"  [{step_idx}/{total_steps}] Semantic review of successful solutions…")
            if tasks_for_checks:
                success_pairs: list[tuple[Task, Any]] = []
                asyncio.run(_semantic_check_solutions(success_pairs, task_summaries))
            else:
                print("    -> Skipped (no agent successes)")
            phase_bar.update(1)
            step_idx += 1

        if enable_code_checks:
            print(f"  [{step_idx}/{total_steps}] Frontend source analysis & screenshots…")
            report.frontend_dir = _locate_frontend_dir(web_project, frontend_root)
            analysis = analyze_frontend(project_slug, report.frontend_dir)
            _attach_screenshot_reviews(analysis, getattr(web_project, "id", project_slug) if web_project else project_slug)
            report.web_analysis = analysis
            phase_bar.update(1)
        return report, task_summaries, web_project
    finally:
        phase_bar.close()


def _list_all_projects() -> list[str]:
    slugs = []
    for entry in sorted(PROJECTS_BASE.iterdir()):
        if entry.is_dir() and entry.name != "__pycache__":
            slugs.append(entry.name)
    return slugs


def _print_task_summary(task_summaries: dict[str, dict]) -> None:
    if not task_summaries:
        return
    print("\nTask summary:")
    for task_id, info in task_summaries.items():
        print(
            f"- {task_id} | UC={info.get('use_case')} | PROMPT={info.get('prompt_status')} | "
            f"TEST={info.get('test_status')} | TEST_GEN={info.get('test_generation_status')} | RANDOM={info.get('random_status')} | "
            f"AGENT={info.get('agent_status')} | SEMANTIC={info.get('semantic_status')}"
        )
        if info.get("semantic_details"):
            print(f"    Semantic notes: {info['semantic_details']}")


def _locate_frontend_dir(web_project: WebProject | None, frontend_root: Path | None = None) -> Path | None:
    if web_project is None:
        return None
    project_id = (getattr(web_project, "id", "") or "").lower()
    if not project_id:
        return None

    candidate_roots: list[Path] = []
    if frontend_root:
        candidate_roots.append(Path(frontend_root))
    env_root = os.getenv("AUTOPPIA_WEB_FRONTENDS_ROOT")
    if env_root:
        candidate_roots.append(Path(env_root))
    candidate_roots.append(Path("modules") / "webs_demo")
    candidate_roots.append(PROJECT_BASE_DIR.parent.parent / "autoppia_webs_demo")

    seen: set[Path] = set()
    for root in candidate_roots:
        root = Path(root)
        if root in seen:
            continue
        seen.add(root)
        if not root.exists():
            continue
        matches = [path for path in root.iterdir() if path.is_dir() and project_id in path.name.lower()]
        if matches:
            return matches[0]
    return None


def _apply_frontend_overrides(web_project: WebProject, override_url: str | None, override_port: int | None) -> None:
    """Override frontend_url via CLI flags without mutating the module files."""
    if not web_project:
        return
    if override_url:
        web_project.frontend_url = override_url
        return
    if override_port and getattr(web_project, "frontend_url", ""):
        parsed = urlsplit(web_project.frontend_url)
        scheme = parsed.scheme or "http"
        host = parsed.hostname or ""
        auth = ""
        if parsed.username:
            auth = parsed.username
            if parsed.password:
                auth += f":{parsed.password}"
            auth += "@"
        netloc = f"{auth}{host}:{override_port}"
        web_project.frontend_url = urlunsplit((scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def _attach_screenshot_reviews(analysis: WebProjectAnalysis, project_id: str | None) -> None:
    if project_id is None:
        return
    project_key = (project_id or "").lower()
    screenshot_dir = Path("data") / "screenshots" / project_key
    llm_service, _ = _obtain_llm_service()
    reviews = summarize_screenshots(screenshot_dir, project_key, llm_service)
    analysis.screenshots = [
        ScreenshotReview(
            filename=str(review["filename"]),
            resolution=str(review["resolution"]),
            size_kb=float(review["size_kb"]),
            summary=str(review["summary"]),
        )
        for review in reviews
    ]


def _write_codex_report(
    project_slug: str,
    report: ProjectReport,
    task_summaries: dict[str, dict],
    web_project: WebProject | None,
    frontend_dir: Path | None,
    frontend_analysis: WebProjectAnalysis | None,
    frontend_root: Path | None,
    run_code_checks: bool,
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{project_slug}_audit.md"

    ok_states = {
        "prompt_status": {"PROMPT_OK", "PROMPT_PENDING"},
        "test_status": {"TEST_OK", "TEST_PENDING"},
        "test_generation_status": {"TESTS_ADDED", "ALREADY_PRESENT", "NOT_RUN"},
        "random_status": {"RANDOM_OK", "NOT_RUN"},
        "agent_status": {"CORRECT", "NOT_RUN"},
        "semantic_status": {"PASS", "NOT_RUN"},
    }
    task_issue_lines: list[str] = []
    for task_id, info in task_summaries.items():
        notes: list[str] = []
        for _field, ok_values in ok_states.items():
            value = info.get(_field)
            if value and value not in ok_values:
                notes.append(f"{_field.replace('_status', '')}={value}")
        if info.get("semantic_details"):
            notes.append(f"notes={info['semantic_details']}")
        if notes:
            task_issue_lines.append(f"- `{task_id}` ({info.get('use_case')}): {', '.join(notes)}")
    next_steps: list[str] = []
    lines = [
        f"# {project_slug} Final Report",
        f"_Updated: {timestamp}_",
        "",
        f"**Overall**: {'✅ PASS' if report.ok else '❌ FAIL'}",
        "",
        "## IWA Analysis",
    ]
    for section_key in SECTION_ORDER:
        title = SECTION_TITLES.get(section_key, section_key.replace("_", " ").title())
        section = report.sections.get(section_key)
        lines.append(f"### {title}")
        if not section:
            lines.append("- ⚪ Not run")
            next_steps.append(f"- IWA / {title}: Section not run")
            continue
        lines.append(f"- `Overall`: {'✅ PASS' if section.ok else '❌ FAIL'}")
        for check in section.checks:
            verdict = "✅" if check.passed else "❌"
            details = f" — {check.details}" if check.details else ""
            lines.append(f"- `{check.description}`: {verdict}{details}")
            if not check.passed:
                detail_msg = check.details or "Fix required."
                next_steps.append(f"- IWA / {check.description}: {detail_msg}")

    if task_issue_lines:
        lines.extend(["", "### Task Notes", *task_issue_lines])
        next_steps.extend(task_issue_lines)

    lines.extend(["", "## Web Project Analysis"])
    if frontend_analysis is None and run_code_checks:
        frontend_dir = frontend_dir or _locate_frontend_dir(web_project, frontend_root)
        frontend_analysis = analyze_frontend(project_slug, frontend_dir)

    lines.append("### Source Discovery")
    if not run_code_checks:
        lines.append("- `Frontend directory`: ⚪ Not run (code checks disabled)")
        lines.extend(
            [
                "",
                "### Event Emissions",
                "- ⚪ Not run (code checks disabled)",
                "",
                "### Dynamic Layers (D1-D3)",
                "- ⚪ Not run (code checks disabled)",
                "",
                "### Screenshots",
                "- ⚪ Not run (code checks disabled)",
            ]
        )
    else:
        codex_lines: list[str] = []
        if frontend_dir is None:
            codex_lines.append("- `Frontend directory`: ❌ Could not locate matching directory in modules/webs_demo")
            next_steps.append("- Web Project / Source Discovery: Frontend directory missing")
        else:
            codex_lines.append(f"- `Frontend directory`: ✅ {frontend_dir}")
            file_checks = [
                ("SeedContext.tsx", frontend_dir / "src" / "context" / "SeedContext.tsx"),
                ("Events module", frontend_dir / "src" / "library" / "events.ts"),
                ("Log-event API route", frontend_dir / "src" / "app" / "api" / "log-event" / "route.ts"),
                ("Dynamic data provider", frontend_dir / "src" / "utils" / "dynamicDataProvider.ts"),
            ]
            for label, path in file_checks:
                verdict = "✅ Found" if path.exists() else "❌ Missing"
                codex_lines.append(f"- `{label}`: {verdict}{' — ' + str(path) if verdict.startswith('❌') else ''}")
                if verdict.startswith("❌"):
                    next_steps.append(f"- Web Project / {label}: Missing file {path}")
        for issue in frontend_analysis.issues:
            codex_lines.append(f"- ⚠️ {issue}")
            next_steps.append(f"- Web Project / Source Discovery: {issue}")
        if codex_lines:
            lines.extend(codex_lines)
        else:
            lines.append("- ⚪ Not run")

        lines.append("")
        lines.append("### Event Emissions")
        if frontend_analysis.event_results:
            for result in frontend_analysis.event_results:
                if result.passed:
                    refs = ", ".join(result.references[:3])
                    if len(result.references) > 3:
                        refs += " ..."
                    lines.append(f"- `{result.event_name}`: ✅ {refs}")
                else:
                    lines.append(f"- `{result.event_name}`: ❌ No emission detected in frontend code")
                    next_steps.append(f"- Web Project / Event `{result.event_name}`: Ensure logEvent is triggered in React")
        else:
            lines.append("- ⚪ Not run (no events defined)")

        lines.append("")
        lines.append("### Dynamic Layers (D1-D3)")
        if frontend_analysis.dynamic_layers:
            for layer in frontend_analysis.dynamic_layers:
                flag = "✅" if layer.passed else "❌"
                detail = f" — {layer.evidence}" if layer.evidence else ""
                lines.append(f"- `{layer.title}`: {flag}{detail}")
                if not layer.passed:
                    next_steps.append(f"- Web Project / {layer.title}: {layer.evidence or 'Implement missing dynamic layer'}")
        else:
            lines.append("- ⚪ Not run")

        lines.append("")
        lines.append("### Screenshots")
        screenshot_reviews = frontend_analysis.screenshots if frontend_analysis else []
        if screenshot_reviews:
            lines.append(f"- `Analyzed`: {len(screenshot_reviews)} screenshot(s)")
            for review in screenshot_reviews[:10]:
                lines.append(f"  - {review.filename} ({review.resolution}, {review.size_kb:.0f}KB): {review.summary}")
            if len(screenshot_reviews) > 10:
                lines.append(f"  - … {len(screenshot_reviews) - 10} more")
        else:
            base_url = getattr(web_project, "frontend_url", "") if web_project else ""
            missing_cmd = (
                f"`python -m modules.web_verification project-screenshots --project-slug {project_slug} --browser firefox`"
                if base_url
                else "`python -m modules.web_verification project-screenshots --project-slug <slug>`"
            )
            lines.append(f"- `Screenshots`: ❌ None — run {missing_cmd}")
            next_steps.append(f"- Web Project / Screenshots: Capture screenshots via {missing_cmd}")

    lines.extend(["", "## Agent Results"])
    if report.random_stats:
        attempts = report.random_stats.get("attempts", 0)
        successes = report.random_stats.get("successes", 0)
        lines.append(f"- `RandomClicker`: {successes}/{attempts} successes (goal 0)")
        if report.random_stats.get("errors"):
            lines.append(f"  - Errors: {report.random_stats['errors']}")
    else:
        lines.append("- `RandomClicker`: ⚪ Not run")
    if report.miner_stats:
        attempts = report.miner_stats.get("attempts", 0)
        successes = report.miner_stats.get("successes", 0)
        median = report.miner_stats.get("median_actions", 0)
        lines.append(f"- `Miner agent`: {successes}/{attempts} successes, median actions={median}")
        if report.miner_stats.get("errors"):
            lines.append(f"  - Errors: {report.miner_stats['errors']}")
    else:
        lines.append("- `Miner agent`: ⚪ Not run")
    if next_steps:
        unique_steps = list(dict.fromkeys(next_steps))
        lines.extend(["", "## Next Steps", *unique_steps])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"    -> Codex report written to {report_path}")


def _print_final_summary(entries: list[tuple[str, ProjectReport]], overall_status: str, total: int) -> None:
    if not entries:
        return
    print("\n==== Final Summary ====")
    for slug, report in entries:
        status = "PASS" if report.ok else "FAIL"
        failing_sections = [SECTION_TITLES.get(key, key.replace("_", " ").title()) for key in SECTION_ORDER if key in report.sections and not report.sections[key].ok]
        if failing_sections:
            notes = "; ".join(failing_sections)
            print(f"- {slug}: {status} — Issues detected in {notes}")
        else:
            print(f"- {slug}: {status} — All gates passed")
    print(f"- Overall: {overall_status} ({total} project{'s' if total != 1 else ''} checked)")


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    project_slugs = args.projects or _list_all_projects()
    run_code_checks = args.code_checks
    run_results_checks = args.results_checks
    if not run_code_checks and not run_results_checks:
        run_code_checks = True
        run_results_checks = True

    if args.config:
        try:
            generated_dir = generate_module_from_config(args.config, output_root=PROJECTS_BASE, force=args.force_config)
        except ModuleConfigError as exc:
            print(f"❌ Failed to generate module from config: {exc}")
            return 1
        slug = generated_dir.name
        if args.projects and slug not in project_slugs:
            print(f"⚠️  Overriding provided project list with config slug '{slug}'.")
        project_slugs = [slug]
        print(f"✅ Generated module for '{slug}' at {generated_dir}")

    deck_override = args.deck if (args.deck and len(project_slugs) == 1) else None
    if args.deck and len(project_slugs) != 1:
        print("⚠️  Ignoring --deck because multiple projects were requested.")
    overall_ok = True
    project_summaries: list[tuple[str, ProjectReport]] = []

    for slug in project_slugs:
        print(f"\n=== Verifying '{slug}' ===")
        report, task_summaries, web_project = run_full_verification(
            slug,
            deck_path=deck_override,
            enable_code_checks=run_code_checks,
            enable_results_checks=run_results_checks,
            frontend_root=args.frontend_root,
            override_frontend_url=args.frontend_base_url,
            override_frontend_port=args.frontend_port,
        )
        print(report.render())
        _print_task_summary(task_summaries)
        _write_codex_report(
            slug,
            report,
            task_summaries,
            web_project,
            report.frontend_dir,
            report.web_analysis,
            args.frontend_root,
            run_code_checks,
        )
        overall_ok = overall_ok and report.ok
        project_summaries.append((slug, report))

    total = len(project_slugs)
    status_text = "PASS" if overall_ok else "FAIL"
    print(f"\nOverall verification result: {status_text} ({total} project{'s' if total != 1 else ''} checked)")
    _print_final_summary(project_summaries, status_text, total)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
