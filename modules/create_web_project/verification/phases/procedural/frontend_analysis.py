from __future__ import annotations

import importlib
import inspect
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

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
class EventCoverageStats:
    total_events: int = 0
    used_events: int = 0
    unused_events: list[str] = field(default_factory=list)
    coverage_percent: float = 0.0


@dataclass
class DynamicUsageStats:
    v1_add_wrap_decoy: int = 0
    v1_change_order: int = 0
    v3_ids: int = 0
    v3_classes: int = 0
    v3_texts: int = 0

    @property
    def total_v1(self) -> int:
        return self.v1_add_wrap_decoy + self.v1_change_order

    @property
    def total_v3(self) -> int:
        return self.v3_ids + self.v3_classes + self.v3_texts


@dataclass
class SeedContextValidation:
    exists: bool = False
    has_seed_provider: bool = False
    has_use_seed: bool = False
    uses_search_params: bool = False
    reads_seed_from_url: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class TestsStructureValidation:
    tests_dir_exists: bool = False
    has_dynamic_test: bool = False
    has_events_test: bool = False
    has_readme: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class VariantJsonValidation:
    id_variants_exists: bool = False
    class_variants_exists: bool = False
    text_variants_exists: bool = False
    id_variants_keys: int = 0
    class_variants_keys: int = 0
    text_variants_keys: int = 0
    issues: list[str] = field(default_factory=list)


@dataclass
class WebProjectAnalysis:
    frontend_dir: Path | None
    event_results: list[EventCoverageResult] = field(default_factory=list)
    dynamic_layers: list[DynamicLayerResult] = field(default_factory=list)
    event_coverage: EventCoverageStats | None = None
    dynamic_usage: DynamicUsageStats | None = None
    seed_context: SeedContextValidation | None = None
    tests_structure: TestsStructureValidation | None = None
    variant_jsons: VariantJsonValidation | None = None
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

    # Calculate event coverage statistics
    analysis.event_coverage = _calculate_event_coverage(analysis.event_results)

    # Calculate dynamic usage statistics (V1/V3 real usage counts)
    analysis.dynamic_usage = _calculate_dynamic_usage(source_index)

    # MEDIA PRIORITY: Validate SeedContext
    analysis.seed_context = _validate_seed_context(frontend_dir, source_index)

    # MEDIA PRIORITY: Validate tests structure
    analysis.tests_structure = _validate_tests_structure(frontend_dir)

    # MEDIA PRIORITY: Validate variant JSONs
    analysis.variant_jsons = _validate_variant_jsons(frontend_dir)

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
    """
    Analyze event emissions in the frontend code.

    Looks for:
    1. Direct event name string usage in logEvent() calls
    2. EVENT_TYPES.XXX references
    3. EVENT_TYPES['XXX'] references
    """
    results: list[EventCoverageResult] = []

    # First, try to find events.ts file in the frontend
    events_file_path = None
    frontend_event_names = []

    for path, text in source_index:
        rel = path.relative_to(frontend_dir)
        rel_str = rel.as_posix().lower()
        if ("events.ts" in rel_str or "event.ts" in rel_str) and ("library" in rel_str or "lib" in rel_str):
            events_file_path = path
            # Extract EVENT_TYPES from frontend
            frontend_event_names = _extract_event_types_from_frontend(text)
            break

    # Use frontend events if found, otherwise use backend events
    events_to_check = frontend_event_names if frontend_event_names else event_names

    for event_name in events_to_check:
        refs: list[str] = []

        # Pattern 1: Direct string usage in logEvent() calls
        # logEvent("EVENT_NAME", ...) or logEvent('EVENT_NAME', ...)
        pattern1 = f"logEvent\\([^)]*[\"']{event_name}[\"'][^)]*\\)"

        # Pattern 2: EVENT_TYPES.XXX
        # Extract the key name from event_name (e.g., "LOGIN" -> "LOGIN")
        event_key = event_name
        pattern2 = f"EVENT_TYPES\\.{event_key}"
        pattern3 = f"EVENT_TYPES\\['{event_key}'\\]"
        pattern4 = f'EVENT_TYPES\\["{event_key}"\\]'

        for path, text in source_index:
            # Skip the events.ts file itself
            if path == events_file_path:
                continue

            relative = path.relative_to(frontend_dir)

            # Check all patterns
            matches = []
            if re.search(pattern1, text, re.IGNORECASE):
                matches.append("logEvent call")
            if re.search(pattern2, text):
                matches.append("EVENT_TYPES.XXX")
            if re.search(pattern3, text) or re.search(pattern4, text):
                matches.append("EVENT_TYPES['XXX']")

            if matches:
                line_number = _find_line_number(text, event_name)
                if line_number == 0:
                    # Try to find any of the patterns
                    for pattern in [pattern1, pattern2, pattern3, pattern4]:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            line_number = text[: match.start()].count("\n") + 1
                            break

                refs.append(f"{relative}:{line_number} ({', '.join(matches)})")
                if len(refs) >= EVENT_REF_LIMIT:
                    break

        results.append(EventCoverageResult(event_name=event_name, references=refs))

    return results


def _extract_event_types_from_frontend(content: str) -> list[str]:
    """
    Extract event names from EVENT_TYPES object in frontend events.ts file.

    Looks for patterns like:
    export const EVENT_TYPES = {
      EVENT_NAME: "EVENT_NAME",
      ...
    }
    """
    # Find EVENT_TYPES = { ... }
    match = re.search(r"export\s+const\s+EVENT_TYPES\s*=\s*\{([^}]+)\}", content, re.DOTALL)
    if not match:
        return []

    event_types_block = match.group(1)
    event_names = []

    # Extract KEY: "VALUE" or KEY: 'VALUE'
    pattern = r'(\w+)\s*:\s*["\']([^"\']+)["\']'
    for match in re.finditer(pattern, event_types_block):
        match.group(1)
        event_value = match.group(2)
        # Use the value (the actual event name string)
        if event_value:
            event_names.append(event_value)

    # Also check commented out events
    commented_pattern = r'//\s*(\w+)\s*:\s*["\']([^"\']+)["\']'
    for match in re.finditer(commented_pattern, event_types_block):
        event_value = match.group(2)
        if event_value and event_value not in event_names:
            event_names.append(event_value)

    return sorted(set(event_names))


def _find_line_number(text: str, needle: str) -> int:
    for idx, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return idx
    return 0


# Dynamic system rules - based on actual implementation structure
DYNAMIC_RULES = {
    "V1": {
        "title": "V1 - DOM Structure Modification (wrappers and order)",
        "patterns": [
            "**/dynamic/v1/add-wrap-decoy.ts",
            "**/dynamic/v1/change-order-elements.ts",
        ],
        "keywords": ["addWrapDecoy", "changeOrderElements", "wrapper", "decoy"],
    },
    "V3": {
        "title": "V3 - Attribute and Text Variation (IDs, classes, texts)",
        "patterns": [
            "**/dynamic/v3/utils/variant-selector.ts",
            "**/dynamic/v3/data/id-variants.json",
            "**/dynamic/v3/data/class-variants.json",
            "**/dynamic/v3/data/text-variants.json",
        ],
        "keywords": ["getVariant", "ID_VARIANTS_MAP", "CLASS_VARIANTS_MAP", "TEXT_VARIANTS_MAP"],
    },
    "Core": {
        "title": "Core Dynamic System (seed management and variant selection)",
        "patterns": [
            "**/dynamic/shared/core.ts",
            "**/context/SeedContext.tsx",
        ],
        "keywords": ["selectVariantIndex", "hashString", "seed", "useSeed"],
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
    patterns: list[str],
    keywords: list[str],
    lower_cache: dict[Path, str],
    frontend_dir: Path,
) -> str | None:
    """
    Find evidence of dynamic system implementation.

    Looks for files matching patterns AND containing all keywords.
    Patterns can use ** for glob matching (e.g., "**/dynamic/v1/*.ts").
    """
    keyword_set = [kw.lower() for kw in keywords]
    for path, text in lower_cache.items():
        rel = path.relative_to(frontend_dir)
        rel_str = rel.as_posix()

        if any(part in EXCLUDED_DIR_PARTS for part in rel.parts):
            continue

        # Check if path matches any pattern
        # Support simple glob patterns: ** matches any path segment
        pattern_matched = False
        for pattern in patterns:
            # Convert glob pattern to simple string matching
            # **/dynamic/v1/add-wrap-decoy.ts -> check if "dynamic/v1/add-wrap-decoy.ts" in path
            pattern_normalized = pattern.replace("**/", "").replace("**", "")
            if pattern_normalized.lower() in rel_str.lower():
                pattern_matched = True
                break

        if not pattern_matched:
            continue

        # Check if all keywords are present in the file
        if all(kw in text for kw in keyword_set):
            return rel_str

    return None


def _calculate_event_coverage(event_results: list[EventCoverageResult]) -> EventCoverageStats:
    """Calculate event coverage statistics."""
    total = len(event_results)
    used = sum(1 for result in event_results if result.passed)
    unused = [result.event_name for result in event_results if not result.passed]

    coverage_percent = (used / total * 100.0) if total > 0 else 0.0

    return EventCoverageStats(
        total_events=total,
        used_events=used,
        unused_events=unused,
        coverage_percent=coverage_percent,
    )


def _calculate_dynamic_usage(source_index: list[tuple[Path, str]]) -> DynamicUsageStats:
    """
    Count real usage of dynamic system functions in the codebase.

    Similar to testRealUsage() in test-dynamic-system.js, this counts:
    - V1: addWrapDecoy, changeOrderElements
    - V3: getVariant calls for IDs, classes, and texts
    """
    stats = DynamicUsageStats()

    # Patterns for V1: addWrapDecoy
    # Matches: .v1.addWrapDecoy or addWrapDecoy(
    add_wrap_decoy_pattern = re.compile(r"\.v1\.addWrapDecoy|addWrapDecoy\s*\(", re.IGNORECASE)

    # Patterns for V1: changeOrderElements
    # Matches: .v1.changeOrderElements or changeOrderElements(
    change_order_pattern = re.compile(r"\.v1\.changeOrderElements|changeOrderElements\s*\(", re.IGNORECASE)

    # Patterns for V3: IDs (getVariant with ID_VARIANTS_MAP)
    # Matches: .v3.getVariant(..., ID_VARIANTS_MAP, ...) or getVariant(..., ID_VARIANTS_MAP, ...)
    id_pattern = re.compile(r"\.v3\.getVariant\s*\([^)]*ID_VARIANTS_MAP|getVariant\s*\([^)]*ID_VARIANTS_MAP", re.IGNORECASE)

    # Patterns for V3: Classes (getVariant with CLASS_VARIANTS_MAP)
    # Matches: .v3.getVariant(..., CLASS_VARIANTS_MAP, ...) or getVariant(..., CLASS_VARIANTS_MAP, ...)
    class_pattern = re.compile(r"\.v3\.getVariant\s*\([^)]*CLASS_VARIANTS_MAP|getVariant\s*\([^)]*CLASS_VARIANTS_MAP", re.IGNORECASE)

    # Patterns for V3: Texts (getVariant with undefined, TEXT_VARIANTS_MAP, or text variants)
    # Matches multiple patterns for text variants
    text_pattern1 = re.compile(r"\.v3\.getVariant\s*\([^)]*,\s*undefined|getVariant\s*\([^)]*,\s*undefined", re.IGNORECASE)
    text_pattern2 = re.compile(r"\.v3\.getVariant\s*\([^)]*TEXT_VARIANTS_MAP|getVariant\s*\([^)]*TEXT_VARIANTS_MAP", re.IGNORECASE)
    text_pattern3 = re.compile(r"\.v3\.getVariant\s*\([^)]*[Tt]ext[^)]*Variants|getVariant\s*\([^)]*[Tt]ext[^)]*Variants", re.IGNORECASE)

    for path, text in source_index:
        # Skip test files
        if "test" in path.name.lower() or "spec" in path.name.lower():
            continue

        # Count V1: addWrapDecoy
        matches = add_wrap_decoy_pattern.findall(text)
        stats.v1_add_wrap_decoy += len(matches)

        # Count V1: changeOrderElements
        matches = change_order_pattern.findall(text)
        stats.v1_change_order += len(matches)

        # Count V3: IDs
        matches = id_pattern.findall(text)
        stats.v3_ids += len(matches)

        # Count V3: Classes
        matches = class_pattern.findall(text)
        stats.v3_classes += len(matches)

        # Count V3: Texts (sum of all text patterns)
        matches1 = text_pattern1.findall(text)
        matches2 = text_pattern2.findall(text)
        matches3 = text_pattern3.findall(text)
        stats.v3_texts += len(matches1) + len(matches2) + len(matches3)

    return stats


def _validate_seed_context(frontend_dir: Path, source_index: list[tuple[Path, str]]) -> SeedContextValidation:
    """
    MEDIA PRIORITY: Validate that SeedContext exists and is properly implemented.

    Checks:
    - SeedContext.tsx exists in src/context/
    - Exports SeedProvider and useSeed
    - Uses useSearchParams from Next.js
    - Reads seed from URL (?seed=X)
    """
    validation = SeedContextValidation()

    # Find SeedContext.tsx
    seed_context_content = None

    for path, _ in source_index:
        rel = path.relative_to(frontend_dir)
        if "context" in rel.parts and "SeedContext" in path.name:
            try:
                seed_context_content = path.read_text(encoding="utf-8")
                validation.exists = True
                break
            except Exception:
                pass

    if not validation.exists:
        validation.issues.append("SeedContext.tsx not found in src/context/")
        return validation

    # Check for SeedProvider export
    if "export" in seed_context_content and "SeedProvider" in seed_context_content:
        # Check if it's actually exported (not just mentioned)
        if re.search(r"export\s+(const|function|)\s*SeedProvider", seed_context_content):
            validation.has_seed_provider = True
        else:
            validation.issues.append("SeedProvider not exported")
    else:
        validation.issues.append("SeedProvider not found")

    # Check for useSeed export
    if "export" in seed_context_content and "useSeed" in seed_context_content:
        if re.search(r"export\s+(const|function|)\s*useSeed", seed_context_content):
            validation.has_use_seed = True
        else:
            validation.issues.append("useSeed not exported")
    else:
        validation.issues.append("useSeed not found")

    # Check for useSearchParams import
    if "useSearchParams" in seed_context_content:
        if re.search(r'from\s+["\']next/navigation["\']', seed_context_content) or re.search(r"import.*useSearchParams.*from", seed_context_content):
            validation.uses_search_params = True
        else:
            validation.issues.append("useSearchParams not imported from next/navigation")
    else:
        validation.issues.append("useSearchParams not used")

    # Check for seed reading from URL
    if "seed" in seed_context_content.lower() and ("searchParams" in seed_context_content or 'get("seed")' in seed_context_content):
        if re.search(r'searchParams\.get\(["\']seed["\']\)', seed_context_content) or re.search(r'params\.get\(["\']seed["\']\)', seed_context_content):
            validation.reads_seed_from_url = True
        else:
            validation.issues.append("Seed not read from URL searchParams")
    else:
        validation.issues.append("Seed reading from URL not detected")

    return validation


def _validate_tests_structure(frontend_dir: Path) -> TestsStructureValidation:
    """
    MEDIA PRIORITY: Validate that tests directory structure is correct.

    Checks:
    - tests/ directory exists
    - test-dynamic-system.js exists
    - test-events.js exists
    - README.md exists
    """
    validation = TestsStructureValidation()

    tests_dir = frontend_dir / "tests"
    validation.tests_dir_exists = tests_dir.exists()

    if not validation.tests_dir_exists:
        validation.issues.append("tests/ directory not found")
        return validation

    # Check for test-dynamic-system.js
    dynamic_test = tests_dir / "test-dynamic-system.js"
    validation.has_dynamic_test = dynamic_test.exists()
    if not validation.has_dynamic_test:
        validation.issues.append("test-dynamic-system.js not found in tests/")

    # Check for test-events.js
    events_test = tests_dir / "test-events.js"
    validation.has_events_test = events_test.exists()
    if not validation.has_events_test:
        validation.issues.append("test-events.js not found in tests/")

    # Check for README.md
    readme = tests_dir / "README.md"
    validation.has_readme = readme.exists()
    if not validation.has_readme:
        validation.issues.append("README.md not found in tests/")

    return validation


def _validate_variant_jsons(frontend_dir: Path) -> VariantJsonValidation:
    """
    MEDIA PRIORITY: Validate that variant JSON files exist and have content.

    Checks:
    - id-variants.json exists
    - class-variants.json exists
    - text-variants.json exists
    - Each JSON has keys (non-empty)
    """
    validation = VariantJsonValidation()

    v3_data_dir = frontend_dir / "src" / "dynamic" / "v3" / "data"

    if not v3_data_dir.exists():
        validation.issues.append("src/dynamic/v3/data/ directory not found")
        return validation

    # Check id-variants.json
    id_variants_path = v3_data_dir / "id-variants.json"
    validation.id_variants_exists = id_variants_path.exists()
    if validation.id_variants_exists:
        try:
            import json

            content = json.loads(id_variants_path.read_text(encoding="utf-8"))
            if isinstance(content, dict):
                validation.id_variants_keys = len(content)
            else:
                validation.issues.append("id-variants.json is not a valid JSON object")
        except Exception as exc:
            validation.issues.append(f"Error reading id-variants.json: {exc}")
    else:
        validation.issues.append("id-variants.json not found")

    # Check class-variants.json
    class_variants_path = v3_data_dir / "class-variants.json"
    validation.class_variants_exists = class_variants_path.exists()
    if validation.class_variants_exists:
        try:
            import json

            content = json.loads(class_variants_path.read_text(encoding="utf-8"))
            if isinstance(content, dict):
                validation.class_variants_keys = len(content)
            else:
                validation.issues.append("class-variants.json is not a valid JSON object")
        except Exception as exc:
            validation.issues.append(f"Error reading class-variants.json: {exc}")
    else:
        validation.issues.append("class-variants.json not found")

    # Check text-variants.json
    text_variants_path = v3_data_dir / "text-variants.json"
    validation.text_variants_exists = text_variants_path.exists()
    if validation.text_variants_exists:
        try:
            import json

            content = json.loads(text_variants_path.read_text(encoding="utf-8"))
            if isinstance(content, dict):
                validation.text_variants_keys = len(content)
            else:
                validation.issues.append("text-variants.json is not a valid JSON object")
        except Exception as exc:
            validation.issues.append(f"Error reading text-variants.json: {exc}")
    else:
        validation.issues.append("text-variants.json not found")

    return validation
