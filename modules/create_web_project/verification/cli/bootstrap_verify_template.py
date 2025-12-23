"""
CLI command to verify that the template matches the actual web project.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

from ...phases.procedural.template_validation import TemplateValidationResult, validate_template


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that the autodining template matches web_4_autodining.",
    )
    return parser.parse_args(list(argv) if argv is not None else [])


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    
    print("🔍 Validating template against web_4_autodining...")
    print("")
    
    result = validate_template()
    
    if not result.template_exists:
        print(f"❌ Template directory not found")
        return 1
    
    if not result.webs_demo_exists:
        print(f"❌ Webs demo directory not found")
        return 1
    
    print("📊 Validation Results:")
    print("")
    
    # Structure
    if result.structure_matches:
        print("✅ Directory structure matches")
    else:
        print("❌ Directory structure differs")
        for issue in result.issues:
            if "directory" in issue.lower():
                print(f"   - {issue}")
    
    # Key files
    if result.key_files_match:
        print("✅ Key files match (checksums identical)")
    else:
        print("⚠️  Some key files differ")
        for diff in result.differences[:5]:
            print(f"   - {diff}")
        if len(result.differences) > 5:
            print(f"   ... and {len(result.differences) - 5} more differences")
    
    # Dynamic system
    if result.dynamic_system_matches:
        print("✅ Dynamic system files match")
    else:
        print("❌ Dynamic system files differ")
        for diff in result.differences:
            if "Dynamic system" in diff:
                print(f"   - {diff}")
    
    # Tests
    if result.tests_match:
        print("✅ Test files match")
    else:
        print("❌ Test files differ")
        for diff in result.differences:
            if "Test file" in diff:
                print(f"   - {diff}")
    
    print("")
    
    if result.key_files_match and result.dynamic_system_matches and result.tests_match:
        print("✅ Template validation PASSED")
        return 0
    else:
        print("❌ Template validation FAILED")
        if result.issues:
            print("\nIssues:")
            for issue in result.issues[:10]:
                print(f"  - {issue}")
        return 1

