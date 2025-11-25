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
├── evaluation/           # Evaluation System (future)
│
├── benchmark/            # Complete Benchmark Tests
│   ├── test_benchmark_smoke.py
│   └── test_caches.py
│
├── demo_webs/            # Demo Web Tests
│   ├── test_mutations_engine.py
│   └── test_mutations_proxy.py
│
├── web_agents/           # Web Agent Tests
│   └── test_apified_agent.py
│
├── projects/             # Web Project Verification Tests
│   ├── test_verify_decks.py
│   └── test_verify_projects.py
│
├── rl/                   # RL System Tests (future)
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

### **evaluation/** - Evaluation System
Tests for the evaluation pipeline:
- Evaluator logic
- Test execution
- Score calculation
- Backend event validation

**Run:**
```bash
pytest tests/evaluation/
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
Tests specific to demo web features:
- Dynamic mutations (D1/D3/D4)
- Mutation engine
- Proxy mutations

**Run:**
```bash
pytest tests/demo_webs/
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

### **projects/** - Web Project Verification
Tests for the web project verification pipeline:
- Deck validation
- Project structure verification
- Module generation

**Run:**
```bash
pytest tests/projects/
```

---

### **rl/** - Reinforcement Learning
Tests for RL training system:
- RL environment
- Reward model
- Training loops
- Episode collection

**Run:**
```bash
pytest tests/rl/
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
- `autoppia_iwa/src/evaluation/` → `tests/evaluation/`
- `autoppia_iwa/entrypoints/benchmark/` → `tests/benchmark/`
- `autoppia_iwa/src/rl/` → `tests/rl/`

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
