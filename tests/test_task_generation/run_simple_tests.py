#!/usr/bin/env python3
"""
Simple test runner for task generation tests.

This script runs the simplified tests that don't require all project dependencies.
"""

import sys
import unittest
from pathlib import Path

from tests.test_task_generation.test_simple import (
    TestLLMIntegration,
    TestTaskCaching,
    TestTaskCreation,
    TestTaskGenerationConfig,
    TestTaskGenerationIntegration,
    TestTestCreation,
    TestUseCaseCreation,
    TestWebProjectCreation,
)

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the simple test module


def run_simple_tests():
    """Run all simple task generation tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [TestTaskCreation, TestTestCreation, TestWebProjectCreation, TestUseCaseCreation, TestTaskGenerationConfig, TestTaskCaching, TestLLMIntegration, TestTaskGenerationIntegration]

    # Add all test methods to the suite
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'=' * 50}")
    print("SIMPLE TESTS SUMMARY")
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
        "task_creation": TestTaskCreation,
        "test_creation": TestTestCreation,
        "web_project": TestWebProjectCreation,
        "use_case": TestUseCaseCreation,
        "config": TestTaskGenerationConfig,
        "caching": TestTaskCaching,
        "llm": TestLLMIntegration,
        "integration": TestTaskGenerationIntegration,
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


def print_usage():
    """Print usage information."""
    print("""
🧪 Task Generation Tests Runner

USAGE:
    python3 run_simple_tests.py                    # Run all simple tests
    python3 run_simple_tests.py <test_class>      # Run specific test class

AVAILABLE TEST CLASSES:
    task_creation    - Test task creation and basic functionality
    test_creation    - Test test creation and functionality
    web_project      - Test web project creation and functionality
    use_case         - Test use case creation and functionality
    config           - Test task generation configuration
    caching          - Test task caching functionality
    llm              - Test LLM integration and response parsing
    integration      - Test end-to-end task generation integration

EXAMPLES:
    python3 run_simple_tests.py                    # Run all tests
    python3 run_simple_tests.py task_creation      # Run only task creation tests
    python3 run_simple_tests.py integration        # Run only integration tests

NOTE:
    These are simplified tests that don't require all project dependencies.
    For full tests with all dependencies, install the required packages first:

    pip install -r requirements.txt

    Then you can run the complete test suite:
    python3 -m pytest tests/test_task_generation/
    """)


def main():
    """Main function to run tests."""
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage()
            return

        # Run specific test class
        test_class = sys.argv[1]
        success = run_specific_test_class(test_class)
    else:
        # Run all tests
        success = run_simple_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
