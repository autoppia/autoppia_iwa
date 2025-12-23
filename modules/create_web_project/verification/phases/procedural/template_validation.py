"""
MEDIA PRIORITY: Template validation.

Validates that the template in autoppia_iwa matches the actual project structure
in autoppia_webs_demo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

TEMPLATE_BASE = Path(__file__).resolve().parents[4] / "template" / "projects" / "autodining" / "frontend"
WEBS_DEMO_BASE = Path(__file__).resolve().parents[5] / "autoppia_webs_demo" / "web_4_autodining"


@dataclass
class TemplateValidationResult:
    template_exists: bool = False
    webs_demo_exists: bool = False
    structure_matches: bool = False
    key_files_match: bool = False
    dynamic_system_matches: bool = False
    tests_match: bool = False
    issues: list[str] = field(default_factory=list)
    differences: list[str] = field(default_factory=list)


def validate_template() -> TemplateValidationResult:
    """
    Validate that the template matches the actual web_4_autodining project.
    
    Checks:
    - Template directory exists
    - webs_demo directory exists
    - Key directories match (src/dynamic/, tests/, etc.)
    - Key files match (checksums)
    - Dynamic system files match
    - Tests files match
    """
    result = TemplateValidationResult()
    
    # Check if directories exist
    result.template_exists = TEMPLATE_BASE.exists()
    result.webs_demo_exists = WEBS_DEMO_BASE.exists()
    
    if not result.template_exists:
        result.issues.append(f"Template directory not found: {TEMPLATE_BASE}")
        return result
    
    if not result.webs_demo_exists:
        result.issues.append(f"Webs demo directory not found: {WEBS_DEMO_BASE}")
        return result
    
    # Check key directories
    key_dirs = [
        "src/dynamic",
        "src/dynamic/v1",
        "src/dynamic/v3",
        "src/dynamic/shared",
        "src/context",
        "tests",
        "src/library",
    ]
    
    for dir_path in key_dirs:
        template_dir = TEMPLATE_BASE / dir_path
        webs_dir = WEBS_DEMO_BASE / dir_path
        
        if not template_dir.exists():
            result.issues.append(f"Template missing directory: {dir_path}")
        if not webs_dir.exists():
            result.issues.append(f"Webs demo missing directory: {dir_path}")
        if template_dir.exists() and webs_dir.exists():
            result.structure_matches = True
    
    # Check key files
    key_files = [
        "src/context/SeedContext.tsx",
        "src/library/events.ts",
        "tests/test-dynamic-system.js",
        "tests/test-events.js",
        "tests/README.md",
        "src/dynamic/shared/core.ts",
        "src/dynamic/v1/add-wrap-decoy.ts",
        "src/dynamic/v1/change-order-elements.ts",
        "src/dynamic/v3/utils/variant-selector.ts",
        "src/dynamic/v3/data/id-variants.json",
        "src/dynamic/v3/data/class-variants.json",
        "src/dynamic/v3/data/text-variants.json",
    ]
    
    matching_files = 0
    for file_path in key_files:
        template_file = TEMPLATE_BASE / file_path
        webs_file = WEBS_DEMO_BASE / file_path
        
        if not template_file.exists():
            result.issues.append(f"Template missing file: {file_path}")
            continue
        if not webs_file.exists():
            result.issues.append(f"Webs demo missing file: {file_path}")
            continue
        
        # Compare checksums
        try:
            template_hash = _file_checksum(template_file)
            webs_hash = _file_checksum(webs_file)
            
            if template_hash == webs_hash:
                matching_files += 1
            else:
                result.differences.append(f"{file_path}: checksums differ")
        except Exception as exc:
            result.issues.append(f"Error comparing {file_path}: {exc}")
    
    if matching_files == len(key_files):
        result.key_files_match = True
    
    # Check dynamic system specifically
    dynamic_files = [
        "src/dynamic/v1/add-wrap-decoy.ts",
        "src/dynamic/v1/change-order-elements.ts",
        "src/dynamic/v3/utils/variant-selector.ts",
        "src/dynamic/shared/core.ts",
    ]
    
    dynamic_match = True
    for file_path in dynamic_files:
        template_file = TEMPLATE_BASE / file_path
        webs_file = WEBS_DEMO_BASE / file_path
        
        if template_file.exists() and webs_file.exists():
            try:
                if _file_checksum(template_file) != _file_checksum(webs_file):
                    dynamic_match = False
                    result.differences.append(f"Dynamic system file differs: {file_path}")
            except Exception:
                dynamic_match = False
        else:
            dynamic_match = False
    
    result.dynamic_system_matches = dynamic_match
    
    # Check tests specifically
    test_files = [
        "tests/test-dynamic-system.js",
        "tests/test-events.js",
        "tests/README.md",
    ]
    
    tests_match = True
    for file_path in test_files:
        template_file = TEMPLATE_BASE / file_path
        webs_file = WEBS_DEMO_BASE / file_path
        
        if template_file.exists() and webs_file.exists():
            try:
                if _file_checksum(template_file) != _file_checksum(webs_file):
                    tests_match = False
                    result.differences.append(f"Test file differs: {file_path}")
            except Exception:
                tests_match = False
        else:
            tests_match = False
    
    result.tests_match = tests_match
    
    return result


def _file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

