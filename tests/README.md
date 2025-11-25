# Tests Directory

Organized test suite following the main system architecture.

## 📁 Structure

```
tests/
├── generation/            # Task & Test Generation
│   └── tasks/            # Task generation pipeline tests
│
├── execution/            # Action Execution
│   └── actions/          # Action execution tests
│
├── benchmark/            # Complete Benchmark Tests
│   ├── test_benchmark_smoke.py
│   └── test_caches.py
│
├── demo_webs/            # Demo Web Tests
│   ├── mutations/        # Dynamic mutation tests (D1/D3/D4)
│   │   ├── test_mutations_engine.py
│   │   └── test_mutations_proxy.py
│   └── verification/     # Web project verification tests
│       ├── test_verify_decks.py
│       └── test_verify_projects.py
│
├── web_agents/           # Web Agent Tests
│   └── test_apified_agent.py
│
├── _deprecated/          # Old/Deprecated Tests
│
├── conftest.py           # Pytest configuration
└── test_di_container.py  # DI container tests
```

## 🎯 Test Categories

### **generation/** - Task & Test Generation
Tests for the task generation pipeline:
- Task creation from use cases
- Constraint generation
- Test (CheckEventTest) generation
- LLM prompt generation

**Run:**
```bash
pytest tests/generation/
```

---

### **execution/** - Action Execution
Tests for browser action execution:
- Individual actions (click, type, etc.)
- Form interactions
- Scroll behavior
- Browser executor

**Run:**
```bash
pytest tests/execution/
```

---


### **benchmark/** - Complete Benchmark
Integration tests for the full benchmark flow:
- End-to-end benchmark execution
- Cache management
- Result generation

**Run:**
```bash
pytest tests/benchmark/
```

---

### **demo_webs/** - Demo Web Tests
Tests for demo web systems:

#### **mutations/** - Dynamic Mutation Tests
Tests for the dynamic mutation system (D1/D3/D4):
- MutationEngine logic
- Proxy mutations
- DOM transformations

#### **verification/** - Web Project Verification
Tests for the web project verification pipeline:
- Deck validation
- Project structure checks
- 8-phase verification process

**Run:**
```bash
pytest tests/demo_webs/mutations/      # Mutation tests
pytest tests/demo_webs/verification/   # Verification tests
pytest tests/demo_webs/                # All demo web tests
```

---

### **web_agents/** - Web Agent Tests
Tests for different web agent implementations:
- ApifiedWebAgent
- BrowserUse agent
- RL agents

**Run:**
```bash
pytest tests/web_agents/
```

---


## 🧪 Running Tests

```bash
# All tests
pytest tests/

# Specific category
pytest tests/generation/
pytest tests/execution/
pytest tests/evaluation/

# Specific file
pytest tests/benchmark/test_benchmark_smoke.py

# With verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=autoppia_iwa
```

## 📝 Test Organization Principles

Tests mirror the main code structure:
- `autoppia_iwa/src/data_generation/` → `tests/generation/`
- `autoppia_iwa/src/execution/` → `tests/execution/`
- `autoppia_iwa/entrypoints/benchmark/` → `tests/benchmark/`
- `modules/dynamic_proxy/` → `tests/demo_webs/mutations/`
- `modules/create_web_project/verification/` → `tests/demo_webs/verification/`

---

## 🔧 Adding New Tests

When adding tests, follow this structure:

```python
# tests/generation/tasks/test_my_feature.py

import pytest
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline

def test_my_feature():
    # Your test here
    pass
```

Place the test in the category that matches the code being tested.
