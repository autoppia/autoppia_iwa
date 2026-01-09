# Web Verification Pipeline

A comprehensive pipeline for verifying web automation tasks by generating tasks, reviewing them with LLM, checking their doability via IWAP API, and validating solutions across different dynamic seeds.

## Overview

The Web Verification Pipeline is a three-step process designed to:

1. **Generate and Review Tasks**: Create multiple tasks per use case with constraints (tests) and validate them using GPT
2. **Check Doability**: Query the IWAP API to determine if tasks have been successfully solved by others
3. **Dynamic Verification**: Evaluate solutions from the IWAP API against tasks with different seed values to ensure dynamic functionality works correctly

## Pipeline Steps

### Step 1: Task Generation and LLM Review

**Purpose**: Generate tasks with constraints and validate that the task prompts accurately represent their constraints.

**Process**:
- Generates `N` tasks per use case (default: 2) using `SimpleTaskGenerator`
- Each task includes:
  - A natural language prompt describing what the user wants to do
  - Constraints (tests) that define success criteria
  - A dynamically generated seed value (if `dynamic_enabled=True`)
- For each generated task:
  - Prints task details (prompt, constraints, seed) for review
  - Sends task and constraints to GPT for review
  - GPT evaluates whether the prompt accurately represents the constraints
  - Stores review results (valid/invalid with reasoning)

**Output**:
- List of generated tasks with their constraints
- LLM review results for each task (valid/invalid)

### Step 2: IWAP Doability Check

**Purpose**: Query the IWAP API to find solutions for the use case and assess doability.

**Process**:
- Only executes if all LLM reviews for the use case are valid
- Calls IWAP API endpoint: `GET /api/v1/tasks/with-solutions`
- Searches for tasks with:
  - `evaluation.score = 1` and `evaluation.passed = True`
  - Matching tests/constraints or intent/prompt
- Extracts solution actions from matched tasks
- Calculates doability metrics:
  - Number of tasks with solutions
  - Success rate
  - Whether the use case is "doable"

**Output**:
- Doability assessment (doable/not doable)
- Success rate
- Matched solution actions (if found)
- API prompt, tests, and start URL from matched task

**Mock Mode**:
- Can use mock responses when API is unavailable or for testing
- Mock responses use generated task constraints for realistic data
- Enable with `--iwap-use-mock` flag

### Step 3: Dynamic Verification

**Purpose**: Verify that solutions from IWAP API work correctly across different seed values.

**Process**:
- Only executes if a solution was found in Step 2
- Takes the solution actions from the matched IWAP API task
- For each seed value in the configured list (default: [1, 50, 100, 200, 300]):
  - Creates a task using the API prompt and tests
  - Updates the task URL with the current seed value
  - Normalizes and updates NavigateAction URLs to match the seed
  - Evaluates the solution actions against the seeded task using `ConcurrentEvaluator`
  - Records evaluation results (score, tests passed, success)
- Aggregates results across all seeds

**Output**:
- Evaluation results for each seed
- Summary: how many seeds passed (e.g., "4/5 seeds passed")
- Overall pass/fail status

## Features

### Task Generation
- **Dynamic Seed Assignment**: Automatically assigns random seeds (1-999) to task URLs when `dynamic_enabled=True`
- **Constraint Generation**: Generates constraints (tests) that define success criteria for each task
- **Unique Tasks**: Ensures each task gets a fresh set of constraints by resetting use case constraints before generation

### LLM Review
- **Prompt-Constraint Validation**: Uses GPT to verify that task prompts accurately represent their constraints
- **Detailed Feedback**: Provides reasoning when a review is invalid
- **Configurable Timeout**: Adjustable timeout for LLM calls (default: 30 seconds)

### IWAP Integration
- **Flexible Matching**: Matches tasks by:
  - Test/constraint comparison (primary)
  - Intent/prompt similarity (fallback)
- **Robust Error Handling**: Falls back to mock responses when API is unavailable
- **Mock Support**: Built-in mock response generator for testing without live API
- **Debugging**: Extensive print statements for API call debugging

### Dynamic Verification
- **Seed Testing**: Tests solutions with multiple seed values to ensure dynamic content handling
- **Action Normalization**: Automatically normalizes actions from API format:
  - Handles nested `attributes` structure
  - Converts action types (e.g., `'input'` → `'TypeAction'`)
  - Normalizes selectors
  - Updates NavigateAction URLs to match task seeds
- **Comprehensive Evaluation**: Uses `ConcurrentEvaluator` for full task evaluation

## Configuration Parameters

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--project-id` | str | **Required** | ID of the web project to verify (e.g., `'autocinema_1'`, `'autocrm'`) |
| `--tasks-per-use-case` | int | `2` | Number of tasks to generate per use case |
| `--dynamic` | flag | `True` | Enable dynamic seed generation |
| `--no-llm-review` | flag | `False` | Disable LLM review of tasks and tests |
| `--no-iwap` | flag | `False` | Disable IWAP doability check |
| `--iwap-use-mock` | flag | `False` | Use mock IWAP API response instead of real API |
| `--no-dynamic-verification` | flag | `False` | Disable dynamic verification with different seeds |
| `--iwap-url` | str | From env/config | Base URL for IWAP service (default: `https://api-leaderboard.autoppia.com`) |
| `--seeds` | str | `"1,50,100,200,300"` | Comma-separated list of seed values to test |
| `--output-dir` | str | `"./verification_results"` | Directory to save results JSON files |
| `--verbose` | flag | `False` | Enable verbose logging |

### Environment Variables

- `IWAP_BASE_URL`: Base URL for IWAP API (default: `https://api-leaderboard.autoppia.com`)

### Configuration Class

The `WebVerificationConfig` dataclass provides programmatic configuration:

```python
@dataclass
class WebVerificationConfig:
    # Task generation
    tasks_per_use_case: int = 2
    dynamic_enabled: bool = True

    # LLM review
    llm_review_enabled: bool = True
    llm_timeout_seconds: float = 30.0

    # IWAP client
    iwap_enabled: bool = True
    iwap_base_url: Optional[str] = None
    iwap_api_key: str = "AIagent2025"
    iwap_timeout_seconds: float = 10.0
    iwap_use_mock: bool = False

    # Dynamic verification
    dynamic_verification_enabled: bool = True
    seed_values: list[int] = [1, 50, 100, 200, 300]

    # Output
    output_dir: str = "./verification_results"
    verbose: bool = False
```

## How to Run

### From Terminal

```bash
# Basic usage
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocrm

# With custom parameters
python -m autoppia_iwa.entrypoints.web_verification.run \
    --project-id autocrm \
    --tasks-per-use-case 3 \
    --seeds "1,50,100,200,300,400" \
    --output-dir ./my_results \
    --verbose

# Using mock IWAP API (for testing)
python -m autoppia_iwa.entrypoints.web_verification.run \
    --project-id autocrm \
    --iwap-use-mock

# Disable specific steps
python -m autoppia_iwa.entrypoints.web_verification.run \
    --project-id autocrm \
    --no-llm-review \
    --no-dynamic-verification
```

### From PyCharm

1. **Create Run Configuration**:
   - Go to `Run` → `Edit Configurations...`
   - Click `+` → `Python`
   - Set:
     - **Name**: `Web Verification Pipeline`
     - **Script path**: `path/to/autoppia_iwa/autoppia_iwa/entrypoints/web_verification/run.py`
     - **Parameters**: `--project-id autocrm [other options]`
     - **Working directory**: `path/to/autoppia_iwa`
     - **Python interpreter**: Select your project interpreter

2. **Run or Debug**:
   - Click `Run` or `Debug` button
   - Use breakpoints in the pipeline code for debugging

3. **Alternative: Use Wrapper Script**:
   - Create a wrapper script at project root (e.g., `run_web_verification.py`)
   - Configure it to call the pipeline module
   - Run the wrapper script from PyCharm

## Output Structure

Results are saved as JSON files in the output directory (default: `./verification_results/`).

### File Naming
- Format: `verification_{project_id}.json`
- Example: `verification_autocrm.json`

### Result Structure

```json
{
  "project_id": "autocrm",
  "project_name": "AutoCRM",
  "use_cases": {
    "ADD_NEW_MATTER": {
      "tasks": [
        {
          "task_id": "...",
          "prompt": "...",
          "constraints": [...],
          "constraints_str": "...",
          "seed": 123,
          "llm_review": {
            "valid": true,
            "reasoning": "..."
          }
        }
      ],
      "llm_reviews": [...],
      "doability_check": {
        "doable": true,
        "success_rate": 0.75,
        "tasks_with_solutions": 3,
        "total_tasks": 4
      },
      "iwap_match_result": {
        "matched": true,
        "match_type": "tests",
        "actions": [...],
        "api_prompt": "...",
        "api_tests": [...],
        "api_start_url": "..."
      },
      "dynamic_verification": {
        "all_passed": true,
        "passed_count": 5,
        "total_count": 5,
        "results": {
          "1": {...},
          "50": {...},
          ...
        },
        "summary": "..."
      }
    }
  }
}
```

## Examples

### Example 1: Basic Verification

```bash
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocinema
```

This will:
- Generate 2 tasks per use case
- Review each task with GPT
- Check doability via IWAP API
- Verify solutions with seeds [1, 50, 100, 200, 300]

### Example 2: Testing with Mock API

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
    --project-id autocrm \
    --iwap-use-mock \
    --verbose
```

Useful when:
- IWAP API is under development
- Testing pipeline without network access
- Debugging pipeline logic

### Example 3: Custom Seed Values

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
    --project-id autolodge \
    --seeds "10,25,50,75,100,125,150"
```

Tests solutions with custom seed values.

### Example 4: Skip LLM Review

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
    --project-id autocrm \
    --no-llm-review
```

Useful for:
- Faster execution when LLM review is not needed
- Testing other pipeline steps independently

## Troubleshooting

### Common Issues

1. **"Project not found"**
   - Check available projects: The error message lists available project IDs
   - Verify project ID spelling and format

2. **"IWAP API not available"**
   - Pipeline will automatically use mock responses
   - Use `--iwap-use-mock` to explicitly enable mock mode
   - Check network connectivity if using real API

3. **"No actions converted from API solution"**
   - Check action normalization logs
   - Verify API response format matches expected structure
   - Actions with invalid selectors or missing required fields are filtered out

4. **"Seed mismatch in NavigateAction"**
   - Pipeline automatically updates NavigateAction URLs to match task seeds
   - If error persists, check action normalization logic

### Debugging Tips

1. **Enable Verbose Logging**:
   ```bash
   --verbose
   ```

2. **Check Logs**: Look for:
   - `📡 IWAP API Request` - API call details
   - `🔄 STEP 3: DYNAMIC VERIFICATION` - Dynamic verification progress
   - `WARNING` messages - Filtered actions or validation issues

3. **Inspect Results JSON**: Check the output file for detailed results

4. **Use Mock Mode**: Test pipeline logic without API dependencies

## Architecture

### Components

- **WebVerificationPipeline**: Main orchestrator
- **SimpleTaskGenerator**: Generates tasks with constraints
- **LLMReviewer**: Reviews tasks using GPT
- **IWAPClient**: Communicates with IWAP API
- **DynamicVerifier**: Verifies solutions with different seeds

### Data Flow

```
Use Case
  ↓
Step 1: Generate Tasks → LLM Review
  ↓ (if all reviews valid)
Step 2: IWAP API Query → Match Solution
  ↓ (if solution found)
Step 3: Dynamic Verification → Evaluate with Seeds
  ↓
Results JSON
```

## Dependencies

- `autoppia_iwa`: Core IWA framework
- `loguru`: Logging
- `aiohttp`: Async HTTP client for IWAP API
- `pydantic`: Data validation
- LLM service (via DIContainer)

## License

Part of the Autoppia IWA project.
