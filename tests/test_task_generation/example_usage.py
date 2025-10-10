#!/usr/bin/env python3
"""
Example usage of task generation tests.

This script demonstrates how to use the test utilities and run specific tests.
"""

import asyncio
import sys
from pathlib import Path

from test_utils import MockLLMService, TaskGenerationTestUtils

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def example_task_creation():
    """Example of creating and testing tasks."""
    print("🔧 Example: Task Creation and Testing")
    print("=" * 50)

    # Create test utilities
    utils = TaskGenerationTestUtils()

    # Create a mock web project
    web_project = utils.create_mock_web_project(project_id="example_project", project_name="Example Project", urls=["http://example.com"], relevant_data={"username": "test_user"})

    print(f"Created web project: {web_project.name}")
    print(f"Project ID: {web_project.id}")
    print(f"URLs: {web_project.urls}")
    print(f"Relevant data: {web_project.relevant_data}")

    # Create a mock use case
    use_case = utils.create_mock_use_case(name="E-commerce Purchase", description="Purchase items from an online store", additional_prompt_info="Generate tasks for buying products")

    print(f"\nCreated use case: {use_case.name}")
    print(f"Description: {use_case.description}")

    # Create test tasks
    tasks = utils.create_test_tasks(3)

    print(f"\nCreated {len(tasks)} test tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task.prompt} (ID: {task.id})")

    # Create task generation config
    config = utils.create_task_generation_config(generate_global_tasks=True, prompts_per_use_case=2, num_use_cases=1, final_task_limit=10)

    print("\nTask generation config:")
    print(f"  Generate global tasks: {config.generate_global_tasks}")
    print(f"  Prompts per use case: {config.prompts_per_use_case}")
    print(f"  Number of use cases: {config.num_use_cases}")
    print(f"  Final task limit: {config.final_task_limit}")

    return tasks, config


async def example_test_generation():
    """Example of test generation."""
    print("\n🧪 Example: Test Generation")
    print("=" * 50)

    utils = TaskGenerationTestUtils()

    # Create test tasks
    tasks = utils.create_test_tasks(2)

    # Create mock LLM service
    mock_llm = MockLLMService()

    # Set up mock responses for test generation
    test_responses = [
        # Response for first task
        utils.create_mock_test_response(
            [
                {
                    "type": "CheckEventTest",
                    "event_name": "purchase_completed",
                    "event_criteria": {"item_color": {"value": "red", "operator": "equals"}, "price": {"value": 10, "operator": "less_than"}},
                    "reasoning": "Verify red dress purchase under $10",
                }
            ]
        ),
        # Response for second task
        utils.create_mock_test_response([{"type": "CheckUrlTest", "expected_url": "http://success.com", "reasoning": "Verify redirect to success page"}]),
    ]

    mock_llm.set_responses(test_responses)

    print(f"Created {len(tasks)} tasks for test generation")
    print("Mock LLM responses configured")

    # Simulate test generation (this would normally be done by the pipeline)
    print("\nSimulating test generation...")
    for i, task in enumerate(tasks):
        print(f"  Task {i + 1}: {task.prompt}")
        # In real usage, this would call the test generation pipeline
        print(f"    -> Would generate tests using LLM response {i + 1}")

    return tasks


async def example_caching():
    """Example of task caching functionality."""
    print("\n💾 Example: Task Caching")
    print("=" * 50)

    utils = TaskGenerationTestUtils()

    # Create temporary cache directory
    cache_dir = utils.create_temp_cache_dir()
    print(f"Created temporary cache directory: {cache_dir}")

    # Create mock project
    project = utils.create_mock_web_project(project_name="Cache Test Project")

    # Create test tasks
    tasks = utils.create_test_tasks(3)

    # Create cache file content
    cache_content = utils.create_cache_file_content(project_id=project.id, project_name=project.name, tasks=[task.serialize() for task in tasks])

    # Write cache file
    cache_file = utils.write_cache_file(cache_dir, project.name, cache_content)
    print(f"Created cache file: {cache_file}")

    # Verify cache file exists
    if cache_file.exists():
        print("✅ Cache file created successfully")

        # Read and verify content
        import json

        with open(cache_file) as f:
            loaded_content = json.load(f)
            print(f"Cache contains {len(loaded_content['tasks'])} tasks")
    else:
        print("❌ Cache file creation failed")

    return cache_dir


def example_validation():
    """Example of task validation."""
    print("\n✅ Example: Task Validation")
    print("=" * 50)

    utils = TaskGenerationTestUtils()

    # Create valid task
    valid_task = utils.create_test_task(prompt="Valid task", url="http://valid.com")

    print(f"Created valid task: {valid_task.prompt}")
    print(f"Task ID: {valid_task.id}")
    print(f"Task URL: {valid_task.url}")

    # Test task properties
    print(f"Task with relevant data: {valid_task.prompt_with_relevant_data}")
    print(f"Original prompt: {valid_task.original_prompt}")

    # Test task preparation for agent
    prepared_task = valid_task.prepare_for_agent("agent_123")
    print(f"Prepared task prompt: {prepared_task.prompt}")

    # Create test objects
    event_test = utils.create_check_event_test(event_name="test_event", event_criteria={"field1": {"value": "value1", "operator": "equals"}}, reasoning="Test reasoning")

    url_test = utils.create_check_url_test(expected_url="http://expected.com", reasoning="URL test reasoning")

    html_test = utils.create_find_in_html_test(selector="h1", expected_text="Expected Title", reasoning="HTML test reasoning")

    print("\nCreated test objects:")
    print(f"  Event test: {event_test.event_name}")
    print(f"  URL test: {url_test.expected_url}")
    print(f"  HTML test: {html_test.selector}")

    return valid_task, [event_test, url_test, html_test]


async def main():
    """Main function to run all examples."""
    print("🚀 Task Generation Test Examples")
    print("=" * 50)

    try:
        # Example 1: Task creation
        tasks, config = await example_task_creation()

        # Example 2: Test generation
        test_tasks = await example_test_generation()

        # Example 3: Caching
        cache_dir = await example_caching()

        # Example 4: Validation
        valid_task, tests = example_validation()

        print("\n🎉 All examples completed successfully!")
        print(f"Created {len(tasks)} tasks")
        print(f"Generated {len(test_tasks)} test tasks")
        print(f"Cache directory: {cache_dir}")
        print(f"Validated {len(tests)} test objects")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
