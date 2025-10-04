# 🧪 Task Generation Tests

This directory contains comprehensive unit tests for the task generation components of the Autoppia IWA system.

## 📁 Test Structure

```
test_task_generation/
├── __init__.py                          # Package initialization
├── conftest.py                          # Pytest configuration and fixtures
├── test_task_generation_pipeline.py     # Core pipeline tests
├── test_test_generation.py              # Test generation tests
├── test_prompts_and_config.py           # Prompts and configuration tests
├── test_utils.py                        # Test utilities and helpers
├── run_tests.py                         # Test runner script
└── README.md                            # This file
```

## 🚀 Running Tests

### Run All Tests
```bash
# From the project root
python -m pytest tests/test_task_generation/

# Or using the test runner
python tests/test_task_generation/run_tests.py
```

### Run Specific Test Classes
```bash
# Run only pipeline tests
python tests/test_task_generation/run_tests.py pipeline

# Run only test generation tests
python tests/test_task_generation/run_tests.py test_generation

# Run only configuration tests
python tests/test_task_generation/run_tests.py config
```

### Run Individual Test Files
```bash
# Run pipeline tests
python -m pytest tests/test_task_generation/test_task_generation_pipeline.py

# Run test generation tests
python -m pytest tests/test_task_generation/test_test_generation.py

# Run prompts and config tests
python -m pytest tests/test_task_generation/test_prompts_and_config.py
```

## 📋 Test Coverage

### 1. Task Generation Pipeline (`test_task_generation_pipeline.py`)
- **TaskGenerationPipeline**: Main pipeline orchestration
- **GlobalTaskGenerationPipeline**: Global task generation logic
- **Task Caching**: JSON serialization and caching
- **Task Integration**: End-to-end task generation
- **Task Validation**: Model validation and constraints

### 2. Test Generation (`test_test_generation.py`)
- **GlobalTestGenerationPipeline**: Test generation logic
- **Test Classes**: CheckEventTest, CheckUrlTest, FindInHtmlTest
- **Test Integration**: End-to-end test generation
- **Test Validation**: Test object validation

### 3. Prompts and Configuration (`test_prompts_and_config.py`)
- **TaskGenerationConfig**: Configuration validation
- **Prompt Templates**: Template formatting and validation
- **UseCase Integration**: Use case handling
- **WebProject Integration**: Web project handling
- **Task Model**: Task model validation
- **BrowserSpecification**: Browser configuration

## 🔧 Test Utilities

The `test_utils.py` module provides:

### TaskGenerationTestUtils
- `create_mock_web_project()`: Create mock web projects
- `create_mock_use_case()`: Create mock use cases
- `create_test_task()`: Create test tasks
- `create_test_tasks()`: Create multiple test tasks
- `create_check_event_test()`: Create CheckEventTest objects
- `create_check_url_test()`: Create CheckUrlTest objects
- `create_find_in_html_test()`: Create FindInHtmlTest objects
- `create_task_generation_config()`: Create configuration objects
- `create_browser_specification()`: Create browser specs
- `create_mock_llm_response()`: Create mock LLM responses
- `create_temp_cache_dir()`: Create temporary cache directories
- `assert_task_equality()`: Assert task equality
- `assert_test_equality()`: Assert test equality

### TaskGenerationTestBase
Base test class with common setup and teardown methods.

### Mock Classes
- `MockLLMService`: Mock LLM service for testing
- `MockWebProject`: Mock web project for testing
- `MockUseCase`: Mock use case for testing

## 📊 Test Examples

### Basic Task Generation Test
```python
async def test_generate_with_global_tasks(self):
    """Test task generation with global tasks enabled."""
    # Setup
    mock_tasks = [Task(prompt="Test task", url="http://test.com")]
    mock_global_pipeline.generate.return_value = mock_tasks

    # Execute
    result = await self.pipeline.generate()

    # Assertions
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].prompt, "Test task")
```

### Test Generation Test
```python
async def test_add_tests_to_tasks_success(self):
    """Test successfully adding tests to tasks."""
    # Setup
    tasks = [Task(prompt="Test task", url="http://test.com")]
    mock_test_data = [{"type": "CheckEventTest", "event_name": "test_event"}]
    self.mock_llm_service.async_predict.return_value = json.dumps(mock_test_data)

    # Execute
    result = await self.pipeline.add_tests_to_tasks(tasks, self.mock_llm_service)

    # Assertions
    self.assertEqual(len(result[0].tests), 1)
    self.assertIsInstance(result[0].tests[0], CheckEventTest)
```

### Configuration Test
```python
def test_custom_configuration(self):
    """Test custom configuration values."""
    config = TaskGenerationConfig(
        generate_global_tasks=False,
        prompts_per_use_case=5,
        num_use_cases=2,
        final_task_limit=20
    )

    self.assertFalse(config.generate_global_tasks)
    self.assertEqual(config.prompts_per_use_case, 5)
```

## 🐛 Debugging Tests

### Verbose Output
```bash
python -m pytest tests/test_task_generation/ -v
```

### Stop on First Failure
```bash
python -m pytest tests/test_task_generation/ -x
```

### Run Specific Test Method
```bash
python -m pytest tests/test_task_generation/test_task_generation_pipeline.py::TestTaskGenerationPipeline::test_generate_with_global_tasks
```

### Coverage Report
```bash
python -m pytest tests/test_task_generation/ --cov=autoppia_iwa.src.data_generation --cov-report=html
```

## 📝 Writing New Tests

### 1. Use the Base Test Class
```python
from test_utils import TaskGenerationTestBase

class TestMyNewFeature(TaskGenerationTestBase):
    def test_my_feature(self):
        # Your test code here
        pass
```

### 2. Use Test Utilities
```python
def test_my_feature(self):
    # Create test data using utilities
    mock_project = self.create_mock_web_project()
    test_task = self.create_test_task()

    # Your test logic here
    pass
```

### 3. Follow Naming Conventions
- Test methods should start with `test_`
- Use descriptive names: `test_generate_tasks_with_valid_config`
- Group related tests in the same class

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the project root is in the Python path
2. **Mock Issues**: Ensure mocks are properly configured before use
3. **Async Issues**: Use `await` for async test methods
4. **File Path Issues**: Use absolute paths or ensure working directory is correct

### Debug Tips

1. Add print statements to see what's happening
2. Use `pytest.set_trace()` to debug interactively
3. Check mock call counts and arguments
4. Verify test data is properly formatted

## 📈 Performance Considerations

- Tests use temporary directories that are cleaned up automatically
- Mock objects are lightweight and don't make real network calls
- Async tests are properly handled with pytest-asyncio
- Large test datasets are avoided to keep tests fast

## 🤝 Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use the provided test utilities
3. Add proper docstrings
4. Include both positive and negative test cases
5. Test edge cases and error conditions
6. Ensure tests are isolated and don't depend on each other
