"""
Web verification utilities (deck module generation, screenshot capture, etc.).
"""

import sys as _sys

# Provide a stable alias so callers can import `modules.web_verification` even
# though the canonical package path lives under modules.create_web_project.verification.
_sys.modules.setdefault("modules.web_verification", _sys.modules[__name__])

from .phases.procedural.module_generator import ConfigError, ModuleGenerator, generate_module_from_config, load_config
from .phases.procedural.run_deck_pipeline import evaluate_project
from .phases.procedural.verify_project import (
    SECTION_DECK,
    SECTION_DYNAMIC,
    SECTION_LLM_TASKS,
    SECTION_LLM_TESTS,
    SECTION_PROCEDURAL,
    SECTION_TITLES,
    SECTION_USE_CASES,
    AnalysisSection,
    ProjectReport,
    verify_project,
)
from .phases.sandbox import (
    DatasetEntry,
    SolutionRecord,
    compute_project_metrics,
    compute_seed_variability,
    detect_agent_memorization,
    find_trivial_tasks,
    find_unresolved_tasks,
    load_dataset,
)
from .phases.visual.screenshot_capture import capture_pages, capture_sync
from .phases.visual.visual_inspector import SCREENSHOT_DIR as VISUAL_INSPECTOR_SCREENSHOT_DIR, run_inspector

__all__ = [
    "SECTION_DECK",
    "SECTION_DYNAMIC",
    "SECTION_LLM_TASKS",
    "SECTION_LLM_TESTS",
    "SECTION_PROCEDURAL",
    "SECTION_TITLES",
    "SECTION_USE_CASES",
    "VISUAL_INSPECTOR_SCREENSHOT_DIR",
    "AnalysisSection",
    "ConfigError",
    "DatasetEntry",
    "ModuleGenerator",
    "ProjectReport",
    "SolutionRecord",
    "capture_pages",
    "capture_sync",
    "compute_project_metrics",
    "compute_seed_variability",
    "detect_agent_memorization",
    "evaluate_project",
    "find_trivial_tasks",
    "find_unresolved_tasks",
    "generate_module_from_config",
    "load_config",
    "load_dataset",
    "run_inspector",
    "verify_project",
]
