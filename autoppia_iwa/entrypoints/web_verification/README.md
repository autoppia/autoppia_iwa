# Web Verification Pipeline

A comprehensive, five-step pipeline that:
- **Step 0**: Pre-validates project configuration (events, use cases, URLs)
- **Step 1 (V1)**: Generates web tasks with constraints and reviews them with an LLM
- **Step 2 (V2)**: Verifies that datasets are different with different seeds (dynamic data validation)
- **Step 3**: Checks if anyone has solved the use case via the IWAP API (with mock fallback)
- **Step 4 (V3)**: Replays found solutions across multiple dynamic seeds to prove they generalize

## Quick start

```bash
# Fast path with defaults (dynamic seeds on, writes one JSON result)
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocrm

# Use mock IWAP when offline and keep logs verbose
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocrm --iwap-use-mock --verbose

# Skip LLM review and dynamic verification for speed
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocrm --no-llm-review --no-dynamic-verification
```

**Outputs**: One JSON per project is written to `./verification_results/verification_<project_id>.json` (overwritten on rerun unless you change `--output-dir`).

## Pre-Validation

Before running the pipeline, the system automatically validates the project setup to ensure everything is correctly configured:

- **Project Structure**: Validates that the project has ID, name, and valid URLs
- **Events**: Checks that events are defined and properly registered
- **Use Cases**: Verifies that use cases exist and each has a valid event associated
- **Event Registry**: Ensures all use case events are registered in the EventRegistry
- **Examples**: Warns if use cases are missing examples

If validation fails, the pipeline stops immediately with clear error messages. This prevents wasting time on a misconfigured project.

## Overview

The Web Verification Pipeline is a five-step process designed to:

0. **Pre-Validation**: Automatically validates project setup (events, use cases, URLs) before proceeding
1. **Task Generation and LLM Review (V1)**: Create multiple tasks per use case with constraints (tests) and validate them using GPT
2. **Dataset Diversity Verification (V2)**: Verify that `get_all_data()` returns different datasets with different seeds, ensuring dynamic data generation works correctly
3. **IWAP Use Case Doability Check**: Query the IWAP API to check if the use case is doable (has any successful solution). We don't compare specific constraints - we just need to know if the use case has been solved before.
4. **Dynamic Verification (V3)**: Take the successful solution from Step 3 and test it with different seed values to ensure the solution works across different dynamic content variations

## Pipeline Steps

### Step 0: Pre-Validation

**Purpose**: Validate project configuration before running the pipeline.

**Process**:
- Validates project has ID, name, and valid URLs (frontend and backend)
- Checks that events are defined and properly structured
- Verifies use cases exist and each has a valid event associated
- Ensures all use case events are registered in the EventRegistry
- Validates that use case events match the project's events list
- Warns if use cases are missing examples

**Output**:
- Validation status (pass/fail)
- List of errors (if any)
- List of warnings (if any)
- Project summary (events count, use cases count, URLs)

**Behavior**:
- If validation fails: Pipeline stops immediately with error messages
- If validation passes: Pipeline continues to Step 1
- Warnings don't stop execution but indicate potential issues

### Step 1: Task Generation and LLM Review (V1)

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

### Step 2: Dataset Diversity Verification (V2)

**Purpose**: Verify that the dynamic data generation system works correctly by ensuring different seeds produce different datasets.

**Process**:
- Only executes if `dynamic_enabled=True`
- For each configured seed value (default: [1, 50, 100, 200, 300]):
  1. Calls the project's `get_all_data(seed)` function in `data_utils.py`
  2. Receives a dictionary with all entities (e.g., `{"movies": [...], "actors": [...]}`)
  3. Calculates an MD5 hash of the dataset for comparison
- Compares all datasets pairwise to verify they are different
- Detects whether differences are due to:
  - **Different entities**: The dataset structure changed (different keys)
  - **Different data**: Same entities but different content (same keys, different values)

**Why this matters**:
- Validates that the `get_all_data()` function is implemented correctly
- Ensures the seed parameter actually affects data generation
- Catches bugs where the same data is returned regardless of seed
- Critical for dynamic task generation to work properly

**Output**:
- Per-seed information: hash, entity count, total items, entity names
- Pairwise comparison results showing which datasets differ
- Overall status: `passed=True` if all datasets are different
- Summary indicating if the dynamic system is working

**Example output**:
```
Step 2 (V2): Dataset Diversity Verification
Seeds tested: [1, 50, 100]
Datasets loaded: 3/3

Seed 1: loaded 50 items across 2 entities (hash: a3b4c5d6...)
Seed 2: loaded 50 items across 2 entities (hash: e7f8g9h0...)
Seed 3: loaded 50 items across 2 entities (hash: i1j2k3l4...)

Pairwise comparisons:
  Seed 1 vs 50: ✓ Different (same entities, different data)
  Seed 1 vs 100: ✓ Different (same entities, different data)
  Seed 50 vs 100: ✓ Different (same entities, different data)

V2 Verification: PASSED - All 3 datasets are different. Dynamic data generation is working correctly.
```

**Note**: This step is **independent** and does not affect other steps. If V2 fails, the pipeline continues normally.

### Step 3: IWAP Use Case Doability Check

**Purpose**: Check if the use case is doable by finding ANY successful solution for it in the IWAP database.

**Important**: We don't compare specific constraints. We only check if the use case has been successfully solved before. For example:
- Use case: "Search movie"
- We don't care if constraints are "year 1986" or "director pepe"
- We only care: has someone successfully solved "Search movie" before?

**Process**:
- Only executes if all LLM reviews for the use case are valid
- Calls IWAP API endpoint: `GET /api/v1/tasks/with-solutions`
  - API already filters by `use_case_name`, so all returned tasks are for the same use case
- Searches for tasks with:
  - `evaluation.score = 1` and `evaluation.passed = True`
  - These are successful solutions for this use case
- Takes the **first successful solution** found (we don't match specific constraints)
- Extracts from the successful solution:
  - **Solution actions**: The sequence of actions that solved the task
  - **API prompt**: The prompt from the successful task
  - **API tests**: The test criteria from the successful task
  - **API start URL**: The starting URL (will be modified with different seeds in Step 4)

**Output**:
- Doability assessment: `matched=True` if use case is doable (has successful solution)
- Solution actions: Actions to test with different seeds in Step 4
- API prompt: Prompt to use for creating tasks with different seeds
- API tests: Test criteria to validate against
- API start URL: Base URL to modify with different seeds
- Total solutions found: Number of successful solutions available for this use case

**Mock Mode**:
- Can use mock responses when API is unavailable or for testing
- Mock responses generate realistic solution data
- Enable with `--iwap-use-mock` flag

### Step 4: Dynamic Verification (V3)

**Purpose**: Verify that the solution from Step 3 works correctly across different seed values.

**Process**:
- Only executes if a solution was found in Step 3 (use case is doable)
- Takes the solution actions, prompt, and tests from the successful IWAP task
- For each seed value in the configured list (default: [1, 50, 100, 200, 300]):
  1. Creates a new task using:
     - The **API prompt** from Step 3 (not our generated prompt)
     - The **API tests** from Step 3 (not our generated constraints)
     - A URL with the current seed value (e.g., `?seed=50`)
  2. Updates all NavigateAction URLs in the solution to use the current seed
  3. Evaluates the solution actions against the seeded task using `ConcurrentEvaluator`
  4. Records evaluation results (score, tests passed, success)
- Aggregates results across all seeds

**Why this matters**:
- Proves that the use case solution works regardless of the seed value
- Validates that the dynamic system doesn't break existing solutions
- Ensures the use case is truly doable across different dynamic content variations

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
- **Use Case Doability Check**: Checks if use case is doable by finding ANY successful solution
  - Does NOT compare specific constraints
  - Takes the first successful solution found (score=1, passed=True)
  - Uses that solution's prompt and actions for dynamic verification
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

## Output Structure

Results are saved as JSON files in the output directory (default: `./verification_results/`).

File naming: `verification_{project_id}.json` (for example `verification_autocrm.json`), written under the configured `--output-dir`.

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

Useful when the IWAP API is unavailable or when you want to exercise Step 3 (dynamic verification) even if the live API cannot return solutions.

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

## Practical tips

- Use `--iwap-use-mock` when offline or the leaderboard service is flaky; the pipeline still exercises matching and dynamic verification.
- Keep seeds short while debugging (for example, `--seeds "1,5"`); expand once the flow is stable.
- Skip `--no-dynamic-verification` when you only need generation + IWAP matching and want faster cycles.
- Change `--output-dir` if you want to keep historical runs; otherwise a single JSON per project is overwritten by default.

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
Step 0: Pre-Validation
  ↓
Step 1: Generate Tasks → LLM Review (V1)
  ↓
Step 2: Dataset Diversity → Verify Different Seeds (V2)
  ↓ (if all reviews valid)
Step 3: IWAP API Query → Match Solution
  ↓ (if solution found)
Step 4: Dynamic Verification → Evaluate with Seeds (V3)
  ↓
Results JSON
```
