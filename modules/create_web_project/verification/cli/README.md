# CLI Commands

This directory contains CLI command wrappers for the web verification system. Each command is a lightweight wrapper that parses arguments and calls the appropriate phase module.

## 📋 Available Commands

Run any command via:

```bash
python -m modules.web_verification <command> [options]
```

## Commands Overview

| Command | Purpose | Uses LLMs | Primary Module |
|---------|---------|-----------|----------------|
| `verify` | Full pipeline (phases 1–8) | Yes | `phases/procedural/verify_project.py` |
| `run-deck` | Procedural + visual deck vetting | No | `phases/procedural/run_deck_pipeline.py` |
| `flow-screenshots` | Capture canned demo flows | No | `phases/visual/screenshot_capture.py` |
| `project-screenshots` | Auto-discover project pages and capture screenshots | No | `phases/visual/site_capture.py` |
| `analyze-sandbox` | Aggregate miner datasets | No | `phases/sandbox/__init__.py` |
| `generate-module` | Bootstrap a demo_webs module from config | No | `phases/procedural/module_generator.py` |
| `verify-template` | Verify template matches actual project | No | `phases/procedural/template_validation.py` |

## Command Details

### `verify`

Run the full verification pipeline for one or more projects (8 phases).

**Usage**:
```bash
python -m modules.web_verification verify <project_slug> [options]
```

**Options**:
- `--deck <path>` - Path to deck JSON file
- `--config <path>` - Path to config.yaml (auto-generates module before verification)
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

# Verify with template (auto-generates module)
python -m modules.web_verification verify autodining --deck decks/autodining.deck.json

# Code checks only (no LLM required)
python -m modules.web_verification verify autodining --code-checks

# Full verification with frontend override
python -m modules.web_verification verify autodining \
  --deck decks/autodining.deck.json \
  --frontend-root autoppia_webs_demo \
  --frontend-port 8000
```

**What it does**:
1. **Phase 1**: Module Scaffold & Metadata Gate
2. **Phase 2**: Deck Consistency Gate
3. **Phase 3**: Use-Case & Event Integrity Gate
4. **Phase 4**: Frontend Reachability & Code Analysis Gate
5. **Phase 5**: Visual Evidence & LLM Review Gate
6. **Phase 6**: LLM Task/Test Pipeline Gate
7. **Phase 7**: Dynamic Mutation Integrity Gate
8. **Phase 8**: Random Baseline Gate

**Implementation**: `phases/procedural/verify_project.py`

---

### `run-deck`

Execute procedural + visual checks for a deck file (phases 1, 2, 4, 5).

**Usage**:
```bash
python -m modules.web_verification run-deck <deck_path> [options]
```

**Options**:
- `--project-slug <slug>` - Project slug (if not in deck)
- `--base-url <url>` - Base URL for frontend
- `--seed <seed>` - Seed value for dynamic system
- `--timeout <ms>` - Timeout in milliseconds
- `--headed` - Run browser in headed mode
- `--enable-llm-judge` - Enable LLM visual validation

**Example**:
```bash
python -m modules.web_verification run-deck decks/autodining.deck.json \
  --project-slug autodining \
  --base-url http://localhost:8000
```

**What it does**:
- Validates deck JSON structure
- Checks deck matches Python module
- Opens pages with Playwright
- Verifies required elements exist
- Captures screenshots

**Implementation**: `phases/procedural/run_deck_pipeline.py`

---

### `generate-module`

Bootstrap a Python module from a YAML/JSON config file.

**Usage**:
```bash
python -m modules.web_verification generate-module --config <config_path> [options]
```

**Options**:
- `--config <path>` - Path to config.yaml or config.json (required)
- `--output-root <path>` - Output directory (default: `src/demo_webs/projects`)
- `--force` - Overwrite existing module directory

**Example**:
```bash
python -m modules.web_verification generate-module \
  --config template/projects/autodining/config.yaml \
  --output-root src/demo_webs/projects \
  --force
```

**What it generates**:
- `main.py` - WebProject instance
- `events.py` - Event classes
- `use_cases.py` - UseCase definitions
- `generation_functions.py` - Constraint generators
- `pages.json` - Page definitions (optional)

**Implementation**: `phases/procedural/module_generator.py`  
**CLI Wrapper**: `cli/bootstrap_generate_module.py`

---

### `verify-template`

Verify that the autodining template matches the actual web_4_autodining project.

**Usage**:
```bash
python -m modules.web_verification verify-template
```

**What it checks**:
- Directory structure matches
- Key files match (checksums)
- Dynamic system files match
- Test files match

**Example**:
```bash
python -m modules.web_verification verify-template
```

**Output**:
```
🔍 Validating template against web_4_autodining...

📊 Validation Results:

✅ Directory structure matches
✅ Key files match (checksums identical)
✅ Dynamic system files match
✅ Test files match

✅ Template validation PASSED
```

**Implementation**: `phases/procedural/template_validation.py`  
**CLI Wrapper**: `cli/bootstrap_verify_template.py`

---

### `analyze-sandbox`

Summarize miner/agent datasets for unresolved or trivial tasks.

**Usage**:
```bash
python -m modules.web_verification analyze-sandbox <dataset_path> [options]
```

**Options**:
- `<dataset_path>` - Path to JSON/JSONL dataset file (required)
- `--report <path>` - Path to write aggregated report (default: `data/sandbox_analysis_report.json`)
- `--success-threshold <float>` - Score treated as success (default: 0.99)
- `--sample <int>` - How many flagged entries to print per category (default: 5)

**Example**:
```bash
python -m modules.web_verification analyze-sandbox data/sandbox_results.jsonl \
  --report data/analysis.json \
  --success-threshold 0.95
```

**What it analyzes**:
- Project metrics
- Unresolved tasks
- Trivial tasks
- Agent memorization
- Seed variability

**Implementation**: `phases/sandbox/__init__.py`  
**CLI Wrapper**: `cli/bootstrap_analyze_sandbox.py`

---

### `flow-screenshots`

Capture screenshots of canned demo flows (autozone/autocrm).

**Usage**:
```bash
python -m modules.web_verification flow-screenshots --project <project> [options]
```

**Options**:
- `--project <name>` - Project name (autozone, autocrm, etc.)
- `--base-url <url>` - Base URL for frontend
- `--output-dir <path>` - Output directory for screenshots

**Example**:
```bash
python -m modules.web_verification flow-screenshots \
  --project autozone \
  --base-url http://localhost:8000
```

**Implementation**: `phases/visual/screenshot_capture.py`  
**CLI Wrapper**: `cli/visual/flow_screenshots.py`

---

### `project-screenshots`

Auto-discover a project's pages and capture screenshots.

**Usage**:
```bash
python -m modules.web_verification project-screenshots [options]
```

**Options**:
- `--project-slug <slug>` - Project slug
- `--base-url <url>` - Base URL for frontend
- `--output-dir <path>` - Output directory for screenshots

**Example**:
```bash
python -m modules.web_verification project-screenshots \
  --project-slug autodining \
  --base-url http://localhost:8000
```

**What it does**:
- Discovers pages from deck or module
- Opens each page with Playwright
- Captures screenshots
- Saves to output directory

**Implementation**: `phases/visual/site_capture.py`  
**CLI Wrapper**: `cli/visual/project_screenshots.py`

---

## Command Execution Flow

```
User executes:
  python -m modules.web_verification <command>

┌─────────────────────────────────┐
│ __main__.py                     │
│  - Reads command                │
│  - Looks up in COMMANDS dict    │
│  - Loads module                 │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ cli/bootstrap_*.py              │
│  - Parses arguments              │
│  - Calls phase module            │
│  - Formats output                │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ phases/*/                       │
│  - Core verification logic      │
│  - Returns results               │
└─────────────────────────────────┘
```

## Adding a New Command

### 1. Create Phase Module

```python
# phases/my_module/my_validation.py
def validate_something() -> ValidationResult:
    # Core logic
    return result
```

### 2. Create CLI Wrapper

```python
# cli/bootstrap_my_validation.py
from ...phases.my_module.my_validation import validate_something

def parse_args(argv):
    parser = argparse.ArgumentParser(...)
    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    result = validate_something()
    # Format and display
    return 0 if result.passed else 1
```

### 3. Register in __main__.py

```python
# verification/__main__.py
COMMANDS = {
    # ... existing commands
    "my-validation": (
        "Description",
        "modules.web_verification.cli.bootstrap_my_validation"
    ),
}
```

## CLI vs Phases

**CLI (`cli/`)**:
- Lightweight wrappers
- Parse arguments
- Format output for terminal
- Handle errors gracefully

**Phases (`phases/`)**:
- Core verification logic
- Reusable functions
- Can be imported programmatically
- Return structured data

## Common Patterns

### Error Handling

```python
def main(argv):
    try:
        result = phase_function()
        if result.passed:
            print("✅ Success")
            return 0
        else:
            print("❌ Failed")
            return 1
    except Exception as exc:
        print(f"❌ Error: {exc}")
        return 1
```

### Progress Display

```python
from tqdm import tqdm

with tqdm(total=steps, desc="Processing") as bar:
    for step in steps:
        process(step)
        bar.update(1)
```

### Output Formatting

```python
def format_results(result):
    if result.passed:
        return f"✅ {result.message}"
    else:
        return f"❌ {result.message}: {result.error}"
```

---

**Last Updated**: 2025-01-27






