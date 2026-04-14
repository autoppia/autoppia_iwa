# Data Extraction Guide

This guide explains how Data Extraction works in `autoppia_iwa`, including:
- DE use-case definitions
- DE task generation (`DEtasks`)
- DE validation in Benchmark and Web Verification Pipeline
- where outputs are stored

Assumption: your virtual environment is already activated.

## 1. Concepts

### 1.1 DE use-cases
DE use-cases are dedicated extraction intents (for example `FIND_DIRECTOR`, `FIND_YEAR`) and are intentionally separated from normal interaction/event use-cases.

### 1.2 DEtasks
A DEtask is a task focused on extracting a value from the seeded dataset. It should include:
- `prompt`: extraction question
- `de_use_case_name`: DE use-case identifier
- `de_expected_answer`: expected value
- `DataExtractionTest(expected_answer=...)` in `tests`
- `task_type = "DEtask"`

### 1.3 Two DE validations
There are two independent DE checks in Web Verification:
- Step 2.5: verifies curated DE trajectories
- Step 2.6: verifies DE task generation quality (one generated DEtask per DE use-case)

## 2. Where to define DE use-cases

Per project, DE logic lives in:
- `autoppia_iwa/src/demo_webs/projects/<project_module>/dataExtractionUseCases.py`

This module must provide:
- `DATA_EXTRACTION_USE_CASES`: list of DE use-case definitions
- `generate_de_tasks(seed, task_url, selected_use_cases)`: DEtask generator

Project registration is wired in:
- `autoppia_iwa/src/demo_webs/projects/<project_module>/main.py`

with:
- `data_extraction_use_cases=[item.name for item in DATA_EXTRACTION_USE_CASES]`

## 3. How DEtasks are generated

### 3.1 Main generation path
`SimpleTaskGenerator.generate(...)` uses a dedicated DE path when:
- `test_types == "data_extraction_only"`

It imports and calls:
- `...projects.<project_module>.dataExtractionUseCases.generate_de_tasks(...)`

If a project does not expose that module/function, it falls back to the legacy DE-compatible generation path.

### 3.2 Deterministic generation
The recommended DE generator design is deterministic by seed:
- pick a row from seeded dataset
- build one question per DE use-case
- set expected answer from that row

Shared helper utilities for this are in:
- `autoppia_iwa/src/demo_webs/projects/data_extraction_use_cases_common.py`

## 4. Generate DEtasks with Benchmark

Edit:
- `autoppia_iwa/entrypoints/benchmark/run.py`

Set at least:
- `test_types="data_extraction_only"`
- desired `PROJECT_IDS`
- `prompts_per_use_case` as needed

Run:

```bash
python -m autoppia_iwa.entrypoints.benchmark.run
```

Generated DEtasks are cached in:

```text
benchmark-output/cache/DataExtraction/<project_id>_DE_tasks.json
```

Normal event tasks remain in:

```text
benchmark-output/cache/tasks/<project_id>_tasks.json
```

## 5. Verify DE in Web Verification Pipeline

Run full pipeline:

```bash
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocinema
```

Useful focused command (fast DE check):

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
  --project-id autocinema \
  --tasks-per-use-case 0 \
  --no-llm-review \
  --no-iwap \
  --no-dynamic-verification
```

### 5.1 Step 2.5: DE trajectories
`DataExtractionTrajectoryVerifier` validates curated trajectories for the selected DE seed (`--data-extraction-seed`, default `1`).

### 5.2 Step 2.6: DE task generation
`DataExtractionTaskGenerationVerifier` generates and validates DEtasks per DE use-case.

Checks include:
- exactly one task per expected DE use-case
- prompt exists
- expected answer exists
- use-case name matches
- task URL seed matches the verified seed
- expected answer appears in the seed dataset
- task includes `DataExtractionTest`

## 6. Where to see results

Pipeline writes:

```text
verification_results/verification_<project_id>.json
```

DE sections:
- `data_extraction_project_verification` (Step 2.5)
- `data_extraction_task_generation_verification` (Step 2.6)

Quick inspect:

```bash
jq '.data_extraction_task_generation_verification' verification_results/verification_autocinema.json
jq '.data_extraction_project_verification' verification_results/verification_autocinema.json
```

Key fields in `data_extraction_task_generation_verification`:
- `expected_use_cases`
- `generated_count`
- `generated_use_cases`
- `passed_count`
- `total_count`
- `all_passed`
- `results[]` with per-use-case `checks`

## 7. DE trajectories debug script

For trajectory-level debugging:

```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema
python scripts/debug_data_extraction_trajectories.py -p autocinema -t <trajectory_id>
```

## 8. File map (who does what)

- `autoppia_iwa/src/demo_webs/projects/*/dataExtractionUseCases.py`
  - DE use-case definitions and DEtask creation
- `autoppia_iwa/src/demo_webs/projects/data_extraction_use_cases_common.py`
  - shared DE generation helpers
- `autoppia_iwa/src/data_generation/tasks/simple/simple_task_generator.py`
  - generation orchestrator; DE path selection
- `autoppia_iwa/entrypoints/benchmark/benchmark.py`
  - benchmark DEtask cache routing (`cache/DataExtraction`)
- `autoppia_iwa/entrypoints/web_verification/data_extraction_verifier.py`
  - Step 2.5 trajectory verification
- `autoppia_iwa/entrypoints/web_verification/data_extraction_task_generation_verifier.py`
  - Step 2.6 DEtask generation verification
- `autoppia_iwa/entrypoints/web_verification/web_verification_pipeline.py`
  - pipeline integration and final report sections
- `autoppia_iwa/entrypoints/web_verification/run.py`
  - CLI entrypoint and exit code behavior

## 9. Recommended quick validation sequence

1. Generate DEtasks with benchmark (`data_extraction_only`).
2. Confirm file exists in `benchmark-output/cache/DataExtraction/`.
3. Run focused Web Verification command (DE-centric).
4. Inspect `data_extraction_task_generation_verification` JSON block.
5. If failures exist, fix `dataExtractionUseCases.py` for affected use-case and repeat.
