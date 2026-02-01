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
Tests constraint generation with the optimized dataset system:
- Tests autocinema constraints
- Tests autobooks constraints
- Verifies constraints contain values from dataset
- Tests dataset pre-loading optimization

**Run:**
```bash
python3 tests/integration/test_constraint_generation.py
```

**Requirements:** webs_server must be running (port 8090)

---

### **test_full_tasks.py**
Tests complete task generation pipeline:
- Generates tasks for autocinema
- Generates tasks for autobooks
- Verifies tasks have seeds in URLs
- Verifies tasks have tests attached
- Saves analysis to `generated_tasks_analysis.json`

**Run:**
```bash
python3 tests/integration/test_full_tasks.py
```

**Output:** `generated_tasks_analysis.json`

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
