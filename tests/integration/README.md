# Integration Tests

These are **integration tests** that verify the complete system works end-to-end.

## 📁 Tests

### **test_all_projects.py**
Verifies all 13 web projects have the optimized seed system:
- Checks each project uses `resolve_seed_from_url()`
- Verifies no deprecated functions (`extract_seed_from_url`)
- Counts functions with `dataset` parameter
- Generates `projects_status.json` report

**Run:**
```bash
python3 tests/integration/test_all_projects.py
```

**Output:** `projects_status.json` with status of all 13 projects.

---

### **test_seed_guard.py**
Tests the seed validation guard that prevents miners from cheating:
- Tests actions with correct seed → Should pass
- Tests actions with wrong seed → Should detect violation
- Tests actions without seed → Should detect violation
- Tests multiple NavigateActions with mixed seeds → Should catch

**Run:**
```bash
python3 tests/integration/test_seed_guard.py
```

**Purpose:** Ensures the anti-cheating guard works correctly.

---

### **test_constraint_generation.py**
Integration tests for constraint generation using **real data from the demo webs backend** (no mocks):
- Tests autocinema constraints (real `fetch_data` from backend)
- Tests autobooks constraints (real `fetch_data` from backend)
- Verifies constraints contain values from the dataset
- Tests dataset pre-loading optimization

**Run:**
```bash
python3 tests/integration/test_constraint_generation.py
# or with pytest (skips when backend unavailable):
pytest tests/integration/test_constraint_generation.py -v
```

**Requirements:** Demo webs backend must be running (e.g. port 8090). If the backend is not reachable, tests are **skipped** so the suite still passes (e.g. in CI without services).

---

### **test_full_tasks.py**
Integration tests for the **full task generation pipeline with real LLM and real backend** (no mocks):
- Generates tasks for autocinema using real OpenAI (or configured LLM)
- Generates tasks for autobooks
- Verifies tasks have seeds in URLs and tests attached
- Saves analysis to `generated_tasks_analysis.json`

**Run:**
```bash
export OPENAI_API_KEY=your-key   # required for real LLM
python3 tests/integration/test_full_tasks.py
# or with pytest (skipped when OPENAI_API_KEY not set or dummy):
pytest tests/integration/test_full_tasks.py -v
```

**Requirements:** `OPENAI_API_KEY` set (and demo webs backend running for constraint data). If the key is missing or is the test placeholder (`dummy-for-tests`), tests are **skipped** so the suite passes in CI without secrets.

---

## 🚀 Run All Integration Tests

Use the helper script:

```bash
./scripts/wait_for_services_and_run_tests.sh
```

This script:
1. Waits for services to be ready (webs_server, webs)
2. Runs all integration tests in sequence
3. Provides colored output with status

---

## 📋 vs Unit Tests

| Integration Tests | Unit Tests (pytest) |
|-------------------|---------------------|
| `tests/integration/` | `tests/generation/`, `tests/execution/`, etc. |
| End-to-end verification | Individual component testing |
| Requires services running | Can run standalone |
| Script-based | Pytest-based |
| Manual execution | CI/CD automated |

---

## 🔧 Requirements

Most integration tests require:
- ✅ webs_server running (port 8090)
- ⚠️ Some tests require demo webs (ports 8001, 8002)

Check service status:
```bash
curl http://localhost:8090/health  # webs_server
curl http://localhost:8001/        # autocinema
```
