"""
Web verification utilities (deck module generation, screenshot capture, etc.).
"""

from .phases.procedural.module_generator import ConfigError, ModuleGenerator, generate_module_from_config, load_config
from .phases.procedural.run_deck_pipeline import evaluate_project
from .phases.procedural.verify_project import (
    AnalysisSection,
    ProjectReport,
    SECTION_DECK,
    SECTION_DYNAMIC,
    SECTION_LLM_TASKS,
    SECTION_LLM_TESTS,
    SECTION_PROCEDURAL,
    SECTION_TITLES,
    SECTION_USE_CASES,
    verify_project,
)
from .phases.visual.screenshot_capture import capture_pages, capture_sync
from .phases.visual.visual_inspector import SCREENSHOT_DIR as VISUAL_INSPECTOR_SCREENSHOT_DIR, run_inspector
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

__all__ = [
    "ConfigError",
    "ModuleGenerator",
    "AnalysisSection",
    "ProjectReport",
    "SECTION_DECK",
    "SECTION_DYNAMIC",
    "SECTION_LLM_TASKS",
    "SECTION_LLM_TESTS",
    "SECTION_PROCEDURAL",
    "SECTION_TITLES",
    "SECTION_USE_CASES",
    "VISUAL_INSPECTOR_SCREENSHOT_DIR",
    "capture_pages",
    "capture_sync",
    "evaluate_project",
    "compute_project_metrics",
    "compute_seed_variability",
    "find_trivial_tasks",
    "find_unresolved_tasks",
    "detect_agent_memorization",
    "load_dataset",
    "DatasetEntry",
    "SolutionRecord",
    "generate_module_from_config",
    "load_config",
    "run_inspector",
    "verify_project",
]
