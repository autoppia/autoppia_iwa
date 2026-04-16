# Benchmark - IWA Agent Evaluation Framework

**Comprehensive system for evaluating web agents across multiple demo websites with automated task generation, execution, and scoring.**

---

## 🚀 Quick Start

### **Prerequisites**

1. **Demo webs running** (see setup below)
2. **Python 3.10+** with dependencies
3. **LLM API key** (OpenAI or DeepSeek)

### **3-Step Setup**

```bash
# 1. Start demo webs
cd ../autoppia_webs_demo
./scripts/setup.sh

# 2. Configure IWA
cd ../autoppia_iwa
echo "DEMO_WEBS_ENDPOINT=http://localhost" >> .env
echo "OPENAI_API_KEY=your-key" >> .env

# 3. Run benchmark
python -m autoppia_iwa.entrypoints.benchmark.run
```

**Results:** `benchmark-output/results/benchmark_results_<timestamp>.json`

---

## 📂 Directory Structure

```
entrypoints/benchmark/
├── __init__.py
├── config.py              # BenchmarkConfig (central configuration)
├── benchmark.py           # Main orchestrator (Benchmark class)
├── run.py                 # Single entry point: configure mode (concurrent/stateful) and run
├── utils/
│   ├── logging.py         # Structured logging utilities
│   ├── metrics.py         # Timing and metrics
│   ├── results.py         # Result serialization & plotting
│   └── task_generation.py # Task loading/generation utilities
└── README.md              # This file
```

**Single entrypoint:** Use only `run.py`. You can run it with no flags (uses defaults in file) or pass CLI flags for pipelines/use cases.

---

## 🏗️ How It Works

### **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    Benchmark Orchestrator                    │
└─────────────────────────────────────────────────────────────┘
                             ↓
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Task         │    │ Agent        │    │ Evaluation   │
│ Generation   │    │ Execution    │    │ System       │
└──────────────┘    └──────────────┘    └──────────────┘
```

### **Execution Flow**

```
For each project in PROJECT_IDS:

  1. Task Generation
     ├─ Check cache (data/outputs/benchmark/cache/tasks/)
     ├─ If not cached: Generate via LLM
     │  ├─ Generate constraints from dataset
     │  ├─ Call LLM with use case prompts
     │  └─ Create Task objects with tests
     └─ Save to cache

  2. Agent Execution
     For each agent in AGENTS:
       For each task:
         ├─ Call agent (POST /act; in concurrent mode once with step_index=0)
         └─ Receive `tool_calls` and build TaskSolution actions

  3. Evaluation
     For each solution:
       ├─ Execute actions in browser (Playwright)
       ├─ Run tests (CheckEventTest, CheckUrlTest, etc.)
       ├─ Calculate score (0.0 to 1.0)
       ├─ Record GIF (optional)
       └─ Save result

  4. Results
     ├─ Aggregate statistics
     ├─ Generate plots (optional)
     ├─ Save JSON report
     └─ Print summary
```

---

## ⚙️ Configuration

### **Main Configuration File: `run.py`**

`run.py` keeps the default configuration in code, and the CLI can override only what you pass.

### **CLI Usage (Simple)**

Default (uses `run.py` config exactly):

```bash
python -m autoppia_iwa.entrypoints.benchmark.run
```

Run only EventTasks:

```bash
python -m autoppia_iwa.entrypoints.benchmark.run \
  --task-types event_only \
  --project-id autocinema \
  --use-case FIND_MOVIE
```

Run only DataExtraction tasks:

```bash
python -m autoppia_iwa.entrypoints.benchmark.run \
  --task-types data_extraction_only \
  --project-id autocinema \
  --de-use-case EXTRACT_MOVIES
```

Run both with explicit filters:

```bash
python -m autoppia_iwa.entrypoints.benchmark.run \
  --task-types both \
  --project-id autocinema \
  --use-cases FIND_MOVIE,BUY_TICKET \
  --data-extraction-use-cases EXTRACT_MOVIES,EXTRACT_TOP_RATED
```

Available pipeline flags:
- `--task-types {both,event_only,data_extraction_only}`
- `--use-cases` / `--use-case` for EventTask use cases
- `--data-extraction-use-cases` / `--de-use-case` for DataExtraction use cases
- `--project-ids` / `--project-id` for project selection

Legacy alias kept for compatibility:
- `--test {both,event_only,data_extraction_only}`

Example default config block:

```python
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
# 1) Agents to evaluate (all expose POST /act)
from autoppia_iwa.src.web_agents.cua import ApifiedWebAgent

AGENTS = [
    ApifiedWebAgent(base_url="http://localhost:5000", id="1", name="MyAgent", timeout=120),
]

# 2) Projects to test
PROJECT_IDS = [
    "autocinema",
    "autobooks",
    # Available: autozone, autodining, autocrm, automail,
    # autodelivery, autolodge, autoconnect, autowork,
    # autocalendar, autolist, autodrive
]

# 3) Configuration
CFG = BenchmarkConfig(
    projects=get_projects_by_ids(demo_web_projects, PROJECT_IDS),
    agents=AGENTS,

    # Task generation
    prompts_per_use_case=1,
    use_cases=None,  # None = all use cases, or specify list like ["USE_CASE_1", "USE_CASE_2"]

    # Execution
    runs=1,
    max_parallel_agent_calls=1,
    record_gif=False,

    # Output
    save_results_json=True,

    # Dynamic features
    dynamic=True,  # Enable seed-based variations
)
```

### **BenchmarkConfig Options**

| Parameter                  | Type      | Default | Description                                 |
| -------------------------- | --------- | ------- | ------------------------------------------- |
| **Task Generation**        |           |         |                                             |
| `prompts_per_use_case`     | int       | `1`     | Number of tasks per use case                |
| `use_cases`                | list[str] | `None`  | Specific use cases to test. If None, tests all available use cases. |
| **Execution**              |           |         |                                             |
| `runs`                     | int       | `1`     | Number of test runs per task                |
| `max_parallel_agent_calls` | int       | `1`     | Concurrent agent requests                   |
| `record_gif`               | bool      | `False` | Save execution GIFs                         |
| **Output**                 |           |         |                                             |
| `save_results_json`        | bool      | `True`  | Save results to JSON                        |
| **Features**               |           |         |                                             |
| `dynamic`                  | bool      | `False` | Enable seed-based web variations            |

| **Evaluator mode**        |           |         |                                             |
| `evaluator_mode`          | str       | `"concurrent"` | `"concurrent"` or `"stateful"` (see below) |
| `max_steps_per_task`      | int       | `50`    | Max steps per task (stateful only)          |

### **Evaluator mode: Concurrent vs Stateful**

There is **one entrypoint**, `run.py`. All agents expose **POST /act**; you choose how the benchmark calls it.

| Aspect | Concurrent | Stateful |
|--------|------------|----------|
| **Agent API** | `POST /act` (same for all) | `POST /act` |
| **Calls** | Once per task: `step_index=0`, agent returns full `tool_calls` plan | Repeated: each call gets current `snapshot_html`, agent returns next `tool_calls` |
| **Typical use** | Agent plans full sequence in one go | Agent decides step-by-step (same as subnet miners) |

**How to switch in `run.py`:** Set `EVALUATOR_MODE` (`"concurrent"` or `"stateful"`). In both cases use `ApifiedWebAgent` with your agent’s base URL (agent must expose `POST /act`).

**`/act` endpoint (POST) — used for both modes:**

Request body:
```json
{
  "task_id": "uuid",
  "prompt": "Login with username X and password Y",
  "url": "http://localhost:8000/login",
  "snapshot_html": "<html>...</html>",
  "step_index": 0,
  "web_project_id": "autobooks",
  "history": [],
  "state_in": {},
  "allowed_tools": [
    {"name": "browser.navigate", "description": "Navigate browser", "parameters": {"type": "object"}}
  ],
  "include_reasoning": true
}
```

Response:
```json
{
  "tool_calls": [
    {"name": "browser.click", "arguments": {"selector": {"type": "css", "value": "#login"}}},
    {"name": "browser.input", "arguments": {"selector": {"type": "css", "value": "#username"}, "text": "user1"}},
    {"name": "browser.input", "arguments": {"selector": {"type": "css", "value": "#password"}, "text": "Passw0rd!"}}
  ],
  "content": "Filled login credentials.",
  "done": false,
  "state_out": {"phase": "login_submitted"},
  "reasoning": "Login form detected and fields completed."
}
```

Use `tool_calls` as canonical output. `actions` is accepted only as an alias for `tool_calls` (same shape: `[{name, arguments}]`).
When the task is done, return `done: true` and optionally include final user-facing text in `content`.

### **Paths (Auto-configured)**

Paths are automatically set in `__post_init__()`:

```python
base_dir/               # autoppia_iwa/
└── data/outputs/benchmark/
    ├── results/        # Benchmark results (JSON)
    ├── per_project/    # Per-project statistics
    ├── logs/           # Execution logs
    ├── recordings/     # GIF recordings
    └── cache/
        └── tasks/      # Cached tasks
```

---

## 🌐 Demo Webs Setup

IWA requires demo websites to evaluate agents. Choose your deployment mode:

### **Option A: Local Development** 🏠

**Use case:** Developing/testing on your local machine

**What happens:** You clone the webs repository and run them locally on your machine.

**Steps:**

```bash
# 1. Clone demo webs repository (separate from IWA)
cd ..
git clone https://github.com/autoppia/autoppia_webs_demo
cd autoppia_webs_demo

# 2. Run setup script
./scripts/setup.sh

# This script will:
# ✅ Install Docker & Docker Compose (if needed)
# ✅ Build and start 13 demo websites
# ✅ Start webs_server (shared backend)
# ⏱️  Takes ~5-10 minutes first time

# 3. Configure IWA to connect to local webs
cd ../autoppia_iwa
echo "DEMO_WEBS_ENDPOINT=http://localhost" >> .env
```

**Result:**
- ✅ webs_server running on `localhost:8090`
- ✅ web_1 to web_13 running on `localhost:8000-8012`
- ✅ IWA benchmark ready to run

---

### **Option B: Remote (Production)** 🌍

**Use case:** Webs already deployed on your production server

**What happens:** IWA connects to your existing deployed webs via HTTP.

**Steps:**

```bash
# Just configure the remote endpoint
cd autoppia_iwa
echo "DEMO_WEBS_ENDPOINT=http://your-production-server.com" >> .env

# Or if using custom domain:
echo "DEMO_WEBS_ENDPOINT=https://webs.autoppia.com" >> .env
```

**That's it!** IWA connects to remote webs. No need to clone or run anything locally.

**Requirements:**
- ✅ webs_server accessible on `<endpoint>:8090`
- ✅ Demo webs accessible on `<endpoint>:8000-8012`

---

### **Verify Connection**

Test that webs are accessible:

```bash
# For local:
curl http://localhost:8090/health       # Backend → 200 OK
curl http://localhost:8000/             # Web 1 → 200 OK

# For remote:
curl http://your-server.com:8090/health
curl http://your-server.com:8000/
```

**Troubleshooting:**
- Connection refused? Check `docker ps` (local) or server status (remote)
- Wrong endpoint? Verify `DEMO_WEBS_ENDPOINT` in `.env`

### **Port Mapping**

| Service               | Port | URL                   |
| --------------------- |------| --------------------- |
| webs_server (backend) | 8090 | http://localhost:8090 |
| autocinema            | 8000 | http://localhost:8000 |
| autobooks             | 8001 | http://localhost:8001 |
| autozone              | 8002 | http://localhost:8002 |
| autodining            | 8003 | http://localhost:8003 |
| autocrm               | 8004 | http://localhost:8004 |
| automail              | 8005 | http://localhost:8005 |
| autodelivery          | 8006 | http://localhost:8006 |
| autolodge             | 8007 | http://localhost:8007 |
| autoconnect           | 8008 | http://localhost:8008 |
| autowork              | 8009 | http://localhost:8009 |
| autocalendar          | 8010 | http://localhost:8010 |
| autolist              | 8011 | http://localhost:8011 |
| autodrive             | 8012 | http://localhost:8012 |

**Verify connection:**

```bash
curl http://localhost:8090/health  # Backend
curl http://localhost:8000/        # Web 1
```

---

## 🕷️ Web Agent Interface

### **What is a Web Agent?**

A web agent is an application that:

1. Receives tasks from IWA
2. Analyzes the requirements
3. Returns `tool_calls` for browser execution (plus optional `content/reasoning/state_out`)

### **Task Structure**

```python
{
  "id": "uuid",
  "url": "http://localhost:8000/?seed=42",
  "prompt": "Login to autocinema with username agent_123",
  "tests": [
    {
      "type": "CheckEventTest",
      "event_name": "UserLoggedIn",
      ...
    }
  ]
}
```

### **TaskSolution Structure**

```python
{
  "task_id": "uuid",
  "web_agent_id": "agent_1",
  "actions": [
    {
      "type": "NavigateAction",
      "url": "http://localhost:8000/login"
    },
    {
      "type": "ClickAction",
      "x": 150,
      "y": 300
    },
    {
      "type": "TypeAction",
      "text": "agent_123"
    }
  ]
}
```

### **Available Actions**

| Action           | Fields                     | Description                         |
| ---------------- | -------------------------- | ----------------------------------- |
| `NavigateAction` | `url, go_back, go_forward` | Navigate to URL or history          |
| `ClickAction`    | `x, y`                     | Click at coordinates                |
| `TypeAction`     | `text`                     | Type text (current focused element) |
| `ScrollAction`   | `down, up`                 | Scroll page                         |
| `WaitAction`     | `seconds`                  | Wait time                           |
| `HoldKeyAction`  | `key`                      | Press key (Enter, Tab, etc.)        |

See `src/execution/actions/actions.py` for complete specs.

---

## 🧪 Creating Your Agent

### **Minimal Agent Example**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/act', methods=['POST'])
def act():
    req = request.get_json() or {}

    # Your agent logic here
    # Analyze task and decide next tool calls.

    return jsonify({
        "tool_calls": [
            {
                "name": "browser.navigate",
                "arguments": {"url": req.get("url")}
            },
            {
                "name": "browser.click",
                "arguments": {"x": 150, "y": 200}
            }
        ],
        "content": "Navigating and clicking first CTA.",
        "done": False,
        "state_out": {}
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
```

**Start agent:**

```bash
pip install flask
python my_agent.py
```

---

## 📊 Output Files

### **Results**

**Main results:** `data/outputs/benchmark/results/benchmark_results_<timestamp>.json`

```json
{
  "timestamp": "2025-11-28T10:30:00",
  "agents": {
    "MyAgent": {
      "score_statistics": {
        "mean": 0.85,
        "median": 1.0,
        "min": 0.0,
        "max": 1.0
      },
      "avg_solution_time": 3.5,
      "tasks": {
        "task_uuid": {
          "use_case": "LOGIN",
          "prompt": "Login to autocinema...",
          "score": 1.0,
          "solution_time": 3.2
        }
      }
    }
  }
}
```

### **Per-Project Stats**

`data/outputs/benchmark/per_project/autoppia_<project>_stats.json`

Contains detailed statistics for each project:

- Use case breakdown
- Action sequences
- Success/failure analysis

### **Cache**

- **Tasks:** `data/outputs/benchmark/cache/tasks/<project>_tasks.json`

### **Logs**

- **Main log:** `data/outputs/benchmark/logs/benchmark.log`
- **Structured logging** with levels: TASK_GENERATION, EVALUATION, etc.

---

## 🎯 Advanced Configuration

### **Select Specific Use Cases**

```python
CFG = BenchmarkConfig(
    use_cases=["LOGIN", "SEARCH_FILM", "ADD_TO_CART"],  # Specific use cases to test
)
```

### **Enable GIF Recording**

```python
CFG = BenchmarkConfig(
    record_gif=True,
)
# Saves to: data/outputs/benchmark/recordings/<agent>/<task>_run_<n>.gif
```

### **Multiple Test Runs**

```python
CFG = BenchmarkConfig(
    runs=5,  # Run each task 5 times
)
# Calculates: mean, median, min, max scores
```

### **Parallel Execution**

```python
CFG = BenchmarkConfig(
    max_parallel_agent_calls=3,  # 3 concurrent requests
)
```

### **Dynamic Web Variations**

```python
CFG = BenchmarkConfig(
    dynamic=True,  # Enables seed-based variations
)
# Each task gets: url?seed=X (different data/layout per seed)
```

---

## 📋 Task Generation

### **Process**

```
1. Select use cases for project
   ↓
2. Generate constraints (from dataset with seed)
   ↓
3. Call LLM to generate task prompts
   ↓
4. Create Task objects
   ↓
5. Generate tests for each task
   ↓
6. Save to cache
```

### **Task Components**

Each generated task includes:

- **prompt:** Natural language description
- **url:** Target URL (with seed if dynamic)
- **tests:** Automated validation tests
  - `CheckEventTest` - Verify backend event fired
  - `JudgeBaseOnScreenshot` - LLM judges screenshot
  - `JudgeBaseOnHTML` - LLM judges HTML changes

### **Task Generation**

Tasks are always generated fresh for each benchmark run. No caching is used.

---

## 🤖 Agent Integration

### **ApifiedOneShotWebAgent**

HTTP-based agent (recommended approach):

```python
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent

agent = ApifiedOneShotWebAgent(
    id="1",
    name="MyAgent",
    host="127.0.0.1",  # or remote server
    port=7000,
    timeout=120,       # seconds
    base_url=None      # or full URL: "http://agent.com/api"
)
```

**Agent must implement:**

- `POST /solve_task` - Receives Task, returns TaskSolution
- `GET /health` - Health check (optional but recommended)

### **Other Agent Types**

```python
# Random clicker (baseline)
from autoppia_iwa.src.web_agents.examples.random_clicker.agent import RandomAgent
agent = RandomAgent(id="random", name="RandomClicker")

# Browser-use wrapper (example)
from autoppia_iwa.src.web_agents.examples.browser_use.agent import BrowserUseAgent
# (requires browser-use library)
```

---

## 📊 Evaluation System

### **Test Types**

**1. CheckEventTest** - Validates backend events

```python
{
  "type": "CheckEventTest",
  "event_name": "UserLoggedIn",
  "event_criteria": {
    "username": {"operator": "equals", "value": "agent_123"}
  }
}
```


**4. LLM-based Tests** - Semantic validation

- `JudgeBaseOnScreenshot` - Analyzes screenshots
- `JudgeBaseOnHTML` - Analyzes HTML changes

### **Scoring**

```python
score = tests_passed / total_tests

Example:
  3 tests, 2 passed → score = 0.67
  All passed → score = 1.0
  None passed → score = 0.0
```

---

## 🛠️ Customization Examples

### **Test Single Project Quickly**

```python
PROJECT_IDS = ["autocinema"]
CFG = BenchmarkConfig(
    prompts_per_use_case=1,
    runs=1,
)
```

### **Stress Test Multiple Agents**

```python
AGENTS = [
    ApifiedOneShotWebAgent(id="1", name="Agent1", port=7000),
    ApifiedOneShotWebAgent(id="2", name="Agent2", port=7001),
    ApifiedOneShotWebAgent(id="3", name="Agent3", port=7002),
]
CFG = BenchmarkConfig(
    runs=10,
    max_parallel_agent_calls=3,
)
```

### **Debug with GIFs**

```python
CFG = BenchmarkConfig(
    record_gif=True,
    runs=1,
)
# GIFs saved to: data/outputs/benchmark/recordings/
```

---

## 🐛 Troubleshooting

### **"Connection refused to agent"**

```bash
# Check agent is running:
curl http://localhost:7000/health

# Check port is correct:
lsof -i :7000

# Start your agent:
python my_agent.py
```

### **"Demo webs not accessible"**

```bash
# Check webs are running:
docker ps | grep web_

# Check endpoint in .env:
cat .env | grep DEMO_WEBS_ENDPOINT

# Restart webs:
cd autoppia_webs_demo
docker-compose restart
```

### **"Task generation failed"**

```bash
# Check LLM API key:
cat .env | grep OPENAI_API_KEY

# Test LLM:
python -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ LLM configured')
"

# Check logs:
tail -f data/outputs/benchmark/logs/benchmark.log
```

### **"Import errors"**

```bash
# Install dependencies:
pip install -r requirements.txt

# Verify installation:
python -c "from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark"
```

---

## 📈 Reading Results

### **Console Output**

```
================================================================================
📊 BENCHMARK RESULTS
================================================================================

Agent: MyAgent (ID: 1)
  ✅ Score: 0.85 (17/20 tasks passed)
  ⏱️  Avg time: 3.2s per task

Tasks:
  • LOGIN: 3/3 ✅
  • SEARCH: 5/6 ⚠️
  • CHECKOUT: 9/11 ⚠️
```

### **JSON Results**

Detailed results in `data/outputs/benchmark/results/`:

- Complete task-by-task breakdown
- Action sequences
- Timestamps
- Error messages

---

## 💡 Best Practices

1. **Start small:** Test 1 project, 1 agent first
2. **Debug with GIFs:** Enable `record_gif=True` to see what happened
3. **Check logs:** `tail -f data/outputs/benchmark/logs/benchmark.log`
4. **Iterate:** Adjust agent, rerun, compare scores

---

## 🔗 Related Documentation

- [Main README](../../readme.md) - IWA overview
- [Task Generation](../../src/data_generation/) - How tasks are created
- [Evaluation System](../../src/evaluation/) - How tests work
- [Web Agents](../../src/web_agents/) - Agent interface examples

---

## ✅ Summary

**IWA Benchmark provides:**

- ✅ Automated task generation (LLM-based)
- ✅ Multi-agent evaluation (parallel execution)
- ✅ Comprehensive testing (multiple test types)
- ✅ Rich outputs (JSON, GIFs, plots, logs)
- ✅ Task caching for faster iterations
- ✅ Flexible configuration (code-based)

**Main file to edit:** `run.py` - Configure agents, projects, and settings here.
