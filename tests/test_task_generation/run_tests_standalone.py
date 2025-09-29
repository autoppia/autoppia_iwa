#!/usr/bin/env python3
"""
Standalone test runner for task generation tests.

This script runs task generation tests without interfering with other test modules.
"""

import sys
import unittest
from pathlib import Path

from tests.test_task_generation.test_prompts_and_config import (
    TestBrowserSpecification,
    TestPromptTemplates,
    TestTaskGenerationConfig,
    TestTaskModelValidation,
    TestUseCaseIntegration,
    TestWebProjectIntegration,
)
from tests.test_task_generation.test_task_generation_pipeline import TestGlobalTaskGenerationPipeline, TestTaskCaching, TestTaskGenerationIntegration, TestTaskGenerationPipeline, TestTaskValidation
from tests.test_task_generation.test_test_generation import TestGlobalTestGenerationPipeline, TestTestClasses, TestTestGenerationIntegration

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import test modules directly


def run_all_tests():
    """Run all task generation tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        # Task generation pipeline tests
        TestTaskGenerationPipeline,
        TestGlobalTaskGenerationPipeline,
        TestTaskCaching,
        TestTaskGenerationIntegration,
        TestTaskValidation,
        # Test generation tests
        TestGlobalTestGenerationPipeline,
        TestTestClasses,
        TestTestGenerationIntegration,
        # Prompts and config tests
        TestTaskGenerationConfig,
        TestPromptTemplates,
        TestUseCaseIntegration,
        TestWebProjectIntegration,
        TestTaskModelValidation,
        TestBrowserSpecification,
    ]

    # Add all test methods to the suite
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'=' * 50}")
    print("TEST SUMMARY")
    print(f"{'=' * 50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    return result.wasSuccessful()


def run_specific_test_class(test_class_name: str):
    """Run tests for a specific test class."""
    test_class_map = {
        "pipeline": TestTaskGenerationPipeline,
        "global": TestGlobalTaskGenerationPipeline,
        "caching": TestTaskCaching,
        "integration": TestTaskGenerationIntegration,
        "validation": TestTaskValidation,
        "test_generation": TestGlobalTestGenerationPipeline,
        "test_classes": TestTestClasses,
        "test_integration": TestTestGenerationIntegration,
        "config": TestTaskGenerationConfig,
        "prompts": TestPromptTemplates,
        "use_case": TestUseCaseIntegration,
        "web_project": TestWebProjectIntegration,
        "task_model": TestTaskModelValidation,
        "browser": TestBrowserSpecification,
    }

    if test_class_name not in test_class_map:
        print(f"Unknown test class: {test_class_name}")
        print(f"Available classes: {', '.join(test_class_map.keys())}")
        return False

    test_class = test_class_map[test_class_name]
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """Main function to run tests."""
    if len(sys.argv) > 1:
        # Run specific test class
        test_class = sys.argv[1]
        success = run_specific_test_class(test_class)
    else:
        # Run all tests
        success = run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
