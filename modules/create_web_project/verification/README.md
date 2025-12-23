# Web Verification System

Complete verification pipeline for IWA web projects. This system validates web projects from multiple angles: code structure, frontend implementation, dynamic system, event coverage, and more.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Verification Pipeline](#verification-pipeline)
- [Template Support](#template-support)
- [Commands](#commands)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The verification system performs **8 phases** of validation:

1. **Module Scaffold & Metadata** - Validates Python module structure
2. **Deck Consistency** - Validates deck JSON matches module
3. **Use-Case & Event Integrity** - Validates use cases and events
4. **Frontend Analysis** - Analyzes frontend code (events, dynamic system, tests)
5. **Visual Evidence** - Captures screenshots and validates UI
6. **LLM Task Pipeline** - Generates and validates tasks
7. **Dynamic Validation** - Validates dynamic system (seeds, mutations)
8. **Random Baseline** - Validates random agent cannot solve tasks

## 🚀 Quick Start

### Verify a Project

```bash
# Verify existing project
python -m modules.web_verification verify autodining --deck path/to/deck.deck.json

# Verify template (auto-generates module)
python -m modules.web_verification verify autodining --deck path/to/deck.deck.json
# System automatically detects template and generates module if needed
```

### Verify Template

```bash
# Compare template with actual project
python -m modules.web_verification verify-template
```

### Generate Module from Config

```bash
# Generate Python module from config.yaml
python -m modules.web_verification generate-module \
  --config template/projects/autodining/config.yaml \
  --output-root src/demo_webs/projects \
  --force
```

## 🏗️ Architecture

### Directory Structure

```
verification/
├── __init__.py              # Public API exports
├── __main__.py              # CLI entry point
├── README.md                # This file
├── CLI.md                   # CLI command documentation
├── PIPELINE.md              # Detailed pipeline documentation
│
├── cli/                     # CLI command wrappers
│   ├── bootstrap_analyze_sandbox.py
│   ├── bootstrap_generate_module.py
│   ├── bootstrap_verify_template.py
│   └── visual/
│       ├── flow_screenshots.py
│       └── project_screenshots.py
│
└── phases/                  # Core verification logic
    ├── deck/                # Deck validation
    ├── dynamic/             # Dynamic system validation
    ├── procedural/          # Procedural checks (phases 1-4)
    ├── sandbox/             # Production dataset analysis
    └── visual/              # Visual inspection
```

### How It Works

1. **CLI (`__main__.py`)** - Routes commands to appropriate modules
2. **CLI Wrappers (`cli/`)** - Parse arguments, format output
3. **Phases (`phases/`)** - Core verification logic
4. **Public API (`__init__.py`)** - Exports for programmatic use

## 📊 Verification Pipeline

### Phase 1: Module Scaffold & Metadata Gate

**Purpose**: Validates Python module structure

**Checks**:
- ✅ Project directory exists (`src/demo_webs/projects/<slug>`)
- ✅ Required files present (`main.py`, `use_cases.py`, `events.py`, `generation_functions.py`)
- ✅ Module imports correctly
- ✅ `WebProject` instance exposed with required fields

**Auto-generation**: If module doesn't exist, system automatically looks for `config.yaml` in template and generates module.

### Phase 2: Deck Consistency Gate

**Purpose**: Validates deck JSON matches Python module

**Checks**:
- ✅ Deck JSON parses correctly
- ✅ `project_id` matches `WebProject.id`
- ✅ `project_name` matches `WebProject.name`
- ✅ Use cases match between deck and code
- ✅ Events align correctly
- ✅ Pages list is non-empty

### Phase 3: Use-Case & Event Integrity Gate

**Purpose**: Validates use cases and events are properly defined

**Checks**:
- ✅ `ALL_USE_CASES` defined and contains only `UseCase` objects
- ✅ Names are unique
- ✅ Descriptions present
- ✅ Examples have `prompt` and `prompt_for_task_generation`
- ✅ Each use case references an event in `EVENTS`
- ✅ `constraints_generator` functions exist

### Phase 4: Frontend Reachability & Code Analysis Gate

**Purpose**: Analyzes frontend code and validates implementation

**Checks**:
- ✅ Frontend URL responds (HTTP GET)
- ✅ Frontend directory located
- ✅ **Event coverage 100%** (all events used)
- ✅ **Dynamic system V1/V3** detected
- ✅ **Real usage counts** (addWrapDecoy, changeOrderElements, getVariant)
- ✅ **SeedContext** validated (exists, exports SeedProvider/useSeed, uses useSearchParams)
- ✅ **Tests structure** validated (tests/, test-dynamic-system.js, test-events.js, README.md)
- ✅ **Variant JSONs** validated (id-variants.json, class-variants.json, text-variants.json)
- ✅ **Node.js tests** executed (test-dynamic-system.js, test-events.js)

**New Validations (2025-01-27)**:
- Real V1/V3 usage counting
- 100% event coverage enforcement
- Node.js test integration
- SeedContext validation
- Tests structure validation
- Variant JSONs validation

### Phase 5: Visual Evidence & LLM Review Gate

**Purpose**: Validates UI matches deck description

**Requirements**: Frontend running, LLM service (optional)

**Checks**:
- ✅ Opens each deck page with Playwright
- ✅ Verifies `required_elements` exist
- ✅ Captures screenshot + HTML snapshot
- ✅ LLM judge validates UI vs deck (optional)

### Phase 6: LLM Task/Test Pipeline Gate

**Purpose**: Generates and validates tasks for miners

**Requirements**: LLM service

**Checks**:
- ✅ Generates prompts for use cases
- ✅ Verifies placeholders resolved
- ✅ Verifies prompts mention constraint values
- ✅ LLM spot-check validates tasks
- ✅ Generates `CheckEventTest` for each task
- ✅ Tests aligned with expected events

### Phase 7: Dynamic Mutation Integrity Gate

**Purpose**: Validates dynamic system works correctly

**Requirements**: Frontend running, LLM service (optional)

**Checks**:
- ✅ Loads pages with `seed=None` (baseline)
- ✅ Loads pages with deterministic seeds (13, 23)
- ✅ Verifies determinism (same seed = same result)
- ✅ Verifies variation (different seeds = different results)
- ✅ Verifies seedless stable (no seed = stable)
- ✅ LLM validates observed changes (optional)

### Phase 8: Random Baseline Gate

**Purpose**: Validates random agent cannot solve tasks

**Requirements**: LLM service

**Checks**:
- ✅ `RandomClickerWebAgent` attempts to solve tasks
- ✅ Verifies score = 0 (should not solve anything)
- ✅ If score > 0, LLM reviews trace

## 🎨 Template Support

The system **automatically detects and works with templates**.

### What is a Template?

A template is a project structure that contains:
- `config.yaml` - Metadata to generate Python module
- `frontend/` - Next.js application code
- `docker-compose.yml` - Deployment configuration

**Templates do NOT have**:
- Python module (`src/demo_webs/projects/<slug>/`)
- `main.py`, `use_cases.py`, `events.py`

### Automatic Template Handling

When you verify a project, the system:

1. **Checks if module exists** in `src/demo_webs/projects/<slug>/`
2. **If not found**, looks for `config.yaml` in template directory
3. **Auto-generates module** from `config.yaml`
4. **Locates frontend** in template's `frontend/` directory
5. **Runs all 8 phases** on the generated module

### Template Directory Structure

```
template/projects/<project_name>/
├── config.yaml              # Module generation config
├── docker-compose.yml       # Deployment config
└── frontend/                 # Next.js application
    ├── src/
    │   ├── dynamic/         # Dynamic system (V1, V3)
    │   ├── context/         # SeedContext
    │   ├── library/        # Events
    │   └── ...
    ├── tests/               # Node.js tests
    │   ├── test-dynamic-system.js
    │   ├── test-events.js
    │   └── README.md
    └── ...
```

### Verifying Templates

```bash
# System automatically detects template and generates module
python -m modules.web_verification verify autodining --deck path/to/deck.deck.json

# Or explicitly verify template structure
python -m modules.web_verification verify-template
```

## 🛠️ Commands

### `verify`

Run full verification pipeline (8 phases).

```bash
python -m modules.web_verification verify <project_slug> [options]
```

**Options**:
- `--deck <path>` - Path to deck JSON file
- `--config <path>` - Path to config.yaml (auto-generates module)
- `--force-config` - Overwrite existing module when using --config
- `--code-checks` - Run only phases 1-4 (procedural/deck/frontend)
- `--results-checks` - Run only phases 5-8 (LLM/dynamic/agent)
- `--frontend-root <path>` - Override frontend directory location
- `--frontend-base-url <url>` - Override frontend URL
- `--frontend-port <port>` - Override frontend port

**Examples**:
```bash
# Verify existing project
python -m modules.web_verification verify autodining --deck decks/autodining.deck.json

# Verify with template (auto-generates)
python -m modules.web_verification verify autodining --deck decks/autodining.deck.json

# Code checks only (no LLM required)
python -m modules.web_verification verify autodining --code-checks
```

### `verify-template`

Compare template with actual project (checksums, structure).

```bash
python -m modules.web_verification verify-template
```

**Checks**:
- Directory structure matches
- Key files match (checksums)
- Dynamic system files match
- Test files match

### `generate-module`

Generate Python module from `config.yaml`.

```bash
python -m modules.web_verification generate-module \
  --config template/projects/autodining/config.yaml \
  --output-root src/demo_webs/projects \
  --force
```

### `run-deck`

Quick deck validation (phases 1, 2, 4, 5).

```bash
python -m modules.web_verification run-deck path/to/deck.deck.json \
  --project-slug autodining \
  --base-url http://localhost:8000
```

### Other Commands

- `flow-screenshots` - Capture screenshots of demo flows
- `project-screenshots` - Auto-discover and capture project pages
- `analyze-sandbox` - Analyze production datasets

## ⚙️ Configuration

### Environment Variables

- `AUTOPPIA_WEB_FRONTENDS_ROOT` - Path to `autoppia_webs_demo` directory
- `AUTOPPIA_TASKS_PER_USE_CASE` - Number of tasks per use case (default: 2)
- `AUTOPPIA_DYNAMIC_MAX_PAGES` - Max pages for dynamic validation (default: 2)
- `AUTOPPIA_DYNAMIC_TIMEOUT_MS` - Page load timeout (default: 15000)
- `AUTOPPIA_DYNAMIC_SIM_THRESHOLD` - Similarity threshold for determinism (default: 0.995)
- `AUTOPPIA_DYNAMIC_MIN_DELTA` - Minimum delta to detect mutation (default: 0.02)

### Frontend Directory Detection

The system searches for frontend in this order:

1. `--frontend-root` argument
2. `AUTOPPIA_WEB_FRONTENDS_ROOT` environment variable
3. Template directory (`template/projects/<name>/frontend/`)
4. `modules/webs_demo/`
5. `../autoppia_webs_demo/`

## 🔍 What Gets Validated

### Code Structure
- ✅ Python module structure
- ✅ Required files present
- ✅ Module imports correctly
- ✅ WebProject instance valid

### Frontend Code
- ✅ Event coverage (100% required)
- ✅ Dynamic system implementation (V1, V3)
- ✅ Real usage counts (addWrapDecoy, changeOrderElements, getVariant)
- ✅ SeedContext properly implemented
- ✅ Tests structure complete
- ✅ Variant JSONs valid
- ✅ Node.js tests pass

### Deck Compliance
- ✅ Deck JSON valid
- ✅ Metadata matches module
- ✅ Use cases match
- ✅ Events align

### Dynamic System
- ✅ Determinism (same seed = same result)
- ✅ Variation (different seeds = different results)
- ✅ Seedless stability

### LLM Validation
- ✅ Task prompts valid
- ✅ Tests generated correctly
- ✅ Visual UI matches deck

## 🐛 Troubleshooting

### Module Not Found

**Problem**: `Project directory exists: Missing directory src/demo_webs/projects/<slug>`

**Solution**: 
- System will auto-generate from template if `config.yaml` exists
- Or manually generate: `python -m modules.web_verification generate-module --config <path>`

### Frontend Not Found

**Problem**: `Frontend directory could not be located`

**Solution**:
- Set `AUTOPPIA_WEB_FRONTENDS_ROOT` environment variable
- Use `--frontend-root` argument
- Ensure template's `frontend/` directory exists

### Frontend Not Responding

**Problem**: `Frontend health check: Unreachable`

**Solution**:
- Start frontend server
- Use `--frontend-base-url` to override URL
- Use `--frontend-port` to override port

### LLM Service Unavailable

**Problem**: Phases 5-8 require LLM service

**Solution**:
- Configure LLM in `DIContainer` or environment variables
- Use `--code-checks` to run only phases 1-4 (no LLM required)

### Node.js Tests Fail

**Problem**: `Node.js dynamic system test: test-dynamic-system.js failed`

**Solution**:
- Ensure Node.js is in PATH
- Run manually: `cd frontend && node tests/test-dynamic-system.js`
- Check test output for specific errors

### Event Coverage < 100%

**Problem**: `Event coverage must be 100%: Only X/Y events used`

**Solution**:
- Ensure all events in `events.ts` are used in code
- Check for `logEvent(EVENT_TYPES.XXX)` or `EVENT_TYPES.XXX` references
- Review unused events list in report

## 📚 Additional Documentation

- **`CLI.md`** - Detailed CLI command documentation
- **`PIPELINE.md`** - Complete pipeline flow and phase details
- **`ANALISIS_VERIFICATION.md`** - Analysis and improvements implemented
- **`TEMPLATE_VS_MODULO.md`** - Template vs Python module differences

## 🔄 Workflow Examples

### Complete Verification Workflow

```bash
# 1. Verify template (auto-generates module if needed)
python -m modules.web_verification verify autodining \
  --deck decks/autodining.deck.json \
  --frontend-root autoppia_webs_demo

# 2. Check template matches actual project
python -m modules.web_verification verify-template

# 3. Generate module manually (optional)
python -m modules.web_verification generate-module \
  --config template/projects/autodining/config.yaml \
  --output-root src/demo_webs/projects \
  --force
```

### Development Workflow

```bash
# Quick code checks (no LLM, fast)
python -m modules.web_verification verify autodining \
  --code-checks \
  --frontend-root autoppia_webs_demo

# Full verification (requires LLM)
python -m modules.web_verification verify autodining \
  --deck decks/autodining.deck.json
```

## ✅ Validation Checklist

Before submitting a project, ensure:

- [ ] Module structure valid (Phase 1)
- [ ] Deck matches module (Phase 2)
- [ ] Use cases properly defined (Phase 3)
- [ ] Event coverage 100% (Phase 4)
- [ ] Dynamic system implemented (Phase 4)
- [ ] SeedContext implemented (Phase 4)
- [ ] Tests structure complete (Phase 4)
- [ ] Variant JSONs valid (Phase 4)
- [ ] Node.js tests pass (Phase 4)
- [ ] Frontend responds (Phase 4)
- [ ] Visual elements match deck (Phase 5)
- [ ] Tasks generate correctly (Phase 6)
- [ ] Dynamic system works (Phase 7)
- [ ] Random agent fails (Phase 8)

## 🎯 Key Features

### Automatic Template Detection & Generation
- **Auto-detects templates**: System automatically finds `config.yaml` in template directory
- **Auto-generates module**: If Python module doesn't exist, generates it from `config.yaml`
- **Auto-locates frontend**: Searches template directory first, then webs_demo
- **Seamless workflow**: You can verify templates directly without manual steps

**How it works**:
1. System checks if module exists in `src/demo_webs/projects/<slug>/`
2. If not found, searches for `config.yaml` in `template/projects/<slug>/` or `template/projects/autodining/`
3. Auto-generates Python module from `config.yaml`
4. Locates frontend in template's `frontend/` directory
5. Runs all 8 phases on generated module

### Comprehensive Frontend Analysis
- **Event coverage validation** (100% required - pipeline fails if < 100%)
- **Dynamic system usage counting** (real usage of addWrapDecoy, changeOrderElements, getVariant)
- **SeedContext validation** (exists, exports SeedProvider/useSeed, uses useSearchParams)
- **Tests structure validation** (tests/, test-dynamic-system.js, test-events.js, README.md)
- **Variant JSONs validation** (id-variants.json, class-variants.json, text-variants.json with content)
- **Node.js test integration** (executes test-dynamic-system.js and test-events.js automatically)

### Flexible Execution
- Run all phases or selective phases
- Code checks only (no LLM required) - phases 1-4
- Results checks only (LLM required) - phases 5-8
- Template verification (compare template vs actual project)

## 📝 Notes

- **Template auto-generation**: System automatically generates module from template if module doesn't exist
- **Frontend detection**: System checks template directory first, then webs_demo
- **Event coverage**: 100% is **required** - pipeline fails if < 100%
- **Node.js tests**: Executed automatically if found in `tests/` directory
- **Dynamic system**: Validated through both static analysis and runtime tests

---

**Last Updated**: 2025-01-27  
**Version**: Includes all ALTA, MEDIA, and BAJA priority improvements

