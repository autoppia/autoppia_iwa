# DataExtractionTest

This is a **standalone README** for the **DataExtractionTest** feature in autoppia_iwa.

---

## 1. What is DataExtractionTest?

**DataExtractionTest** is a test type that validates the **agent's extracted answer** (e.g. a value read from the page) against an **expected value**, **without running the browser**. It is often referred to as **Option B**, in contrast to **Option A** (CheckEventTest + browser execution).

### Behavior

- The task carries an **expected answer** (scalar or list) stored on the test as `expected_answer`.
- The agent returns **extracted_data** (e.g. string or number) in its solution.
- The test compares `extracted_data` to `expected_answer` using:
  - **Scalar:** normalized string comparison.
  - **List:** canonical list comparison; the extracted value can be a comma-separated string (e.g. `"a,b,c"`).
- **No browser execution** and **no backend events** are used for this test; evaluation is based only on `extracted_data` vs `expected_answer`.

### Implementation location

- **Class:** `DataExtractionTest` in `autoppia_iwa/src/data_generation/tests/classes.py` (around lines 422–499).
- **Test runner:** `_execute_partial_test` and `_execute_global_test` both ignore `backend_events` and call `_check_expected_answer(extracted_data)`.

---

## 2. Configuration: How to Select DataExtractionTest

Selection is controlled in the **benchmark config** and flows into task generation.

**File:** `autoppia_iwa/entrypoints/benchmark/config.py`

| Parameter | Purpose |
|-----------|--------|
| **`test_types`** | `"event_only"` → only CheckEventTest (default). **`"data_extraction_only"`** → only DataExtractionTest. |
| **`data_extraction_use_cases`** | Optional **whitelist** of use-case names that may receive DataExtractionTest. If **`None`**, the pipeline uses only **`UseCase.supports_data_extraction`** to decide. |

`test_types` is validated and must be one of: `"event_only"`, `"data_extraction_only"`.

### Example

In `autoppia_iwa/entrypoints/benchmark/run.py` (or your own benchmark entrypoint):

```python
CFG = BenchmarkConfig(
    # ...
    test_types="data_extraction_only",
    data_extraction_use_cases=None,  # Use all use cases with supports_data_extraction=True
)
```

- **`test_types="data_extraction_only"`** — Generate and run only DataExtractionTest for the selected use cases (no CheckEventTest for those tasks).
- **`data_extraction_use_cases=None`** — Rely on `UseCase.supports_data_extraction`; no extra name filter.
- To restrict to specific use cases, set e.g. **`data_extraction_use_cases=["UseCaseA", "UseCaseB"]`**.

---

## 3. Implementation Across Classes

### 3.1 Config layer

- **`BenchmarkConfig`** (`entrypoints/benchmark/config.py`): `test_types`, `data_extraction_use_cases`; validation ensures only `event_only` or `data_extraction_only`.
- **`TaskGenerationConfig`** (`src/data_generation/tasks/classes.py`): Same two fields so the pipeline knows which test type to generate and which use cases are allowed for DataExtractionTest.

### 3.2 UseCase (`src/demo_webs/classes.py`)

- **`supports_data_extraction: bool = False`** — Used together with benchmark/task config to decide where DataExtractionTest is attached. Only use cases with `supports_data_extraction=True` are considered. If `data_extraction_use_cases` is set, the use case name must also be in that list.
- **`question_fields_and_values`** — Used when generating **data_extraction_only** tasks (e.g. in `simple_task_generator.py`) to pass entity/field info into the LLM prompt.

Example: In `src/demo_webs/projects/autostats_15/use_cases.py`, several use cases set `supports_data_extraction=True`.

### 3.3 Task generation

- **`TestGenerationPipeline`** (`src/data_generation/tests/simple/test_generation_pipeline.py`):
  - **`_should_attach_data_extraction_test(task, test_types, data_extraction_use_cases)`** — Returns true only when: `test_types == "data_extraction_only"`, the task has a use case, that use case has `supports_data_extraction`, and (if `data_extraction_use_cases` is not `None`) the use case name is in the list.
  - **`_generate_tests_for_task`** — When the above is true, builds a single **DataExtractionTest** with `expected_answer` from the single constraint's value and appends it to `task.tests`.

- **`SimpleTaskGenerator`** (`src/data_generation/tasks/simple/simple_task_generator.py`):
  - For `test_types == "data_extraction_only"`, filters use cases by `data_extraction_use_cases` (if provided) or by `supports_data_extraction`.
  - Sets `generate_data_extraction` per use case and uses `question_fields_and_values` and the data-extraction prompt when generating data-extraction tasks.

- **`TaskGenerationPipeline`** (`src/data_generation/tasks/pipeline.py`): Passes `data_extraction_use_cases` from config into the generator and test pipeline.

### 3.4 Task / test types

- **`Task`** (`src/data_generation/tasks/classes.py`): **`TestUnion`** includes `DataExtractionTest` (discriminated by `type`).
- **`BaseTaskTest.deserialize`** (`src/data_generation/tests/classes.py`): Registers `DataExtractionTest` in the test class map for deserialization.

### 3.5 Evaluation (concurrent evaluator)

- **`evaluator.py`** (`src/evaluation/concurrent_evaluator/evaluator.py`): **Option B** — If the task has **no** CheckEventTest (only DataExtractionTest), it **skips browser execution**:
  - Reads `extracted_data` from `task_solution`.
  - Calls `run_global_tests(task, backend_events=[], extracted_data=extracted_data)`.
  - Score is derived from test results only (no backend events, no browser GIF).

### 3.6 `run_global_tests` / TestRunner

- **`run_global_tests`** (`src/evaluation/shared/utils.py`): Accepts **`extracted_data`** and forwards it to the test runner.
- **`TestRunner.run_global_tests`** (`src/evaluation/shared/test_runner.py`): Passes **`extracted_data`** into each test's **`execute_global_test(..., extracted_data=extracted_data)`**.

### 3.7 Agent / TaskSolution

- **`TaskSolution`** (`src/web_agents/classes.py`): Field **`extracted_data: Any | None`** holds the agent's extracted answer for DataExtractionTest.
- **Benchmark** (`entrypoints/benchmark/benchmark.py`): When the agent returns a dict with `"actions"` and optionally `"extracted_data"`, builds `TaskSolution(..., extracted_data=extracted_data)`.
- **ApifiedOneShotAgent** (`src/web_agents/apified_one_shot_agent.py`): When `solution.extracted_data is not None`, **`act()`** returns **`{"actions": solution.actions, "extracted_data": solution.extracted_data}`** so the benchmark can set it on `TaskSolution`.

### 3.8 UI

- **`visualizator.py`** (`src/shared/visualizator.py`): For test type **`"DataExtractionTest"`**, the expected answer is **not** exposed in the UI to avoid leaking the solution.

---

## 4. End-to-end flow (data_extraction_only)

1. **Config:** Set `test_types="data_extraction_only"` and optionally `data_extraction_use_cases`.
2. **Task generation:** Only use cases with `supports_data_extraction` (and in `data_extraction_use_cases` if set) get tasks; each such task gets a **DataExtractionTest** with `expected_answer` from the single verify-field.
3. **Benchmark run:** Agent is invoked; it may return `{"actions": [...], "extracted_data": <value>}`; benchmark stores that in `TaskSolution.extracted_data`.
4. **Evaluation:** Evaluator sees no CheckEventTest → skips browser, calls `run_global_tests(..., extracted_data=task_solution.extracted_data)`; DataExtractionTest compares `extracted_data` to `expected_answer`.

---

## 5. Quick reference

| Goal | Config / change |
|------|------------------|
| Use only DataExtractionTest | `test_types="data_extraction_only"` in `BenchmarkConfig` |
| Limit to specific use cases | `data_extraction_use_cases=["Name1", "Name2"]` |
| Allow a use case for data extraction | Set `supports_data_extraction=True` on the `UseCase` |
| Agent provides the answer | Return `{"actions": [...], "extracted_data": <value>}` from `act()` or have your agent set `TaskSolution.extracted_data` |

---

## 6. Related files

- **Test class:** `autoppia_iwa/src/data_generation/tests/classes.py` — `DataExtractionTest`
- **Benchmark config:** `autoppia_iwa/entrypoints/benchmark/config.py` — `BenchmarkConfig`
- **Task config:** `autoppia_iwa/src/data_generation/tasks/classes.py` — `TaskGenerationConfig`
- **UseCase:** `autoppia_iwa/src/demo_webs/classes.py` — `supports_data_extraction`, `question_fields_and_values`
- **Test attachment:** `autoppia_iwa/src/data_generation/tests/simple/test_generation_pipeline.py` — `_should_attach_data_extraction_test`, `_generate_tests_for_task`
- **Evaluator:** `autoppia_iwa/src/evaluation/concurrent_evaluator/evaluator.py` — Option B (DataExtractionTest-only path)
- **Unit tests:** `autoppia_iwa/tests/test_data_extraction_test/test_data_extraction_test.py`
