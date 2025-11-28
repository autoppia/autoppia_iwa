# Benchmark - IWA Agent Evaluation

**Evaluate web agents against demo websites with automated scoring.**

## 🚀 Quick Start (3 Steps)

### **1. Start Demo Webs**

```bash
# Clone and run demo webs (separate repository)
cd ..
git clone https://github.com/autoppia/autoppia_webs_demo
cd autoppia_webs_demo
./scripts/setup.sh
```

This starts 13 demo websites on ports 8100-8112 and backend on 8090.

### **2. Configure IWA**

```bash
cd ../autoppia_iwa

# Add to .env:
echo "DEMO_WEBS_ENDPOINT=http://localhost" >> .env
echo "OPENAI_API_KEY=your-api-key" >> .env
```

### **3. Run Benchmark**

```bash
python -m autoppia_iwa.entrypoints.benchmark.run
```

**Done!** Results saved to `data/outputs/benchmark/results/`

---

## 📋 What It Does

```
1. Generate tasks → "Login to autocinema"
2. Send to agent → POST /solve_task
3. Execute actions → Click, type, navigate
4. Validate tests → Did it work?
5. Calculate score → 0.0 to 1.0
```

---

## ⚙️ Configuration

Edit `run.py`:

```python
# Your agents
AGENTS = [
    ApifiedWebAgent(
        id="1",
        name="MyAgent",
        host="127.0.0.1",
        port=7000,
        timeout=120
    ),
]

# Projects to test
PROJECT_IDS = [
    "autocinema",    # Movie booking
    "autobooks",     # Library management
    # ...add more
]

# Benchmark config
CFG = BenchmarkConfig(
    projects=get_projects_by_ids(demo_web_projects, PROJECT_IDS),
    agents=AGENTS,
    runs=3,                      # Test runs per task
    max_parallel_agent_calls=1,  # Concurrency
    save_results_json=True,
)
```

---

## 🌐 Demo Webs Deployment

### **Option A: Local (Development)**

```bash
# 1. Clone webs repo
git clone https://github.com/autoppia/autoppia_webs_demo

# 2. Run setup
cd autoppia_webs_demo && ./scripts/setup.sh

# 3. Configure IWA
echo "DEMO_WEBS_ENDPOINT=http://localhost" >> .env
```

### **Option B: Remote (Production)**

```bash
# Point to deployed webs
echo "DEMO_WEBS_ENDPOINT=http://your-server.com" >> .env
```

**Verify connection:**
```bash
curl http://localhost:8090/health  # Backend
curl http://localhost:8100/        # Web 1
```

---

## 📊 Output Files

| File | Location | Description |
|------|----------|-------------|
| Results | `data/outputs/benchmark/results/` | JSON with scores |
| Logs | `data/outputs/benchmark/logs/` | Execution logs |
| Cache | `data/outputs/benchmark/cache/` | Tasks/solutions |
| Per-project | `data/outputs/benchmark/per_project/` | Project stats |

---

## 🎯 Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `use_cached_tasks` | `False` | Reuse generated tasks |
| `prompts_per_use_case` | `1` | Tasks per use case |
| `runs` | `1` | Test runs per task |
| `max_parallel_agent_calls` | `1` | Concurrent requests |
| `record_gif` | `False` | Save execution videos |
| `save_results_json` | `True` | Save results |

---

## 🧪 Testing Your Agent

### **Minimal Agent Example**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/solve_task', methods=['POST'])
def solve_task():
    task = request.get_json()

    # Your logic here
    actions = [
        {"type": "NavigateAction", "url": task["url"]},
        {"type": "ClickAction", "x": 100, "y": 200},
    ]

    return jsonify({
        "task_id": task["id"],
        "actions": actions
    })

app.run(port=7000)
```

**Start and test:**
```bash
python my_agent.py &
python -m autoppia_iwa.entrypoints.benchmark.run
```

---

## 📝 Available Actions

Your agent returns a list of action objects:

| Action | Fields | Example |
|--------|--------|---------|
| `NavigateAction` | `url` | Navigate to page |
| `ClickAction` | `x, y` | Click coordinates |
| `TypeAction` | `text` | Type text |
| `ScrollAction` | `down/up` | Scroll page |
| `WaitAction` | `seconds` | Wait time |

See `src/execution/actions/` for full action specs.

---

## 🐛 Troubleshooting

### **"Connection refused"**
```bash
# Check webs are running:
docker ps | grep web_

# Restart if needed:
cd autoppia_webs_demo
docker-compose restart
```

### **"No tasks generated"**
```bash
# Check OpenAI API key:
echo $OPENAI_API_KEY

# Test LLM:
python -c "import openai; print(openai.api_key)"
```

### **"Agent timeout"**
```bash
# Check agent is running:
curl http://localhost:7000/health

# Increase timeout in run.py:
timeout=180  # seconds
```

---

## 📖 Further Reading

- [Main README](../../readme.md) - IWA overview
- [Demo Webs Setup](../../docs/demo_webs_setup.md) - Deployment guide
- [Agent Examples](../../src/web_agents/examples/) - Sample implementations

---

## 💡 Key Points

- **IWA evaluates, doesn't train** - Pure benchmark system
- **Agent-agnostic** - Works with any agent (LLM, RL, rules)
- **Demo webs separate** - Clone and run independently
- **Simple setup** - 3 commands to start testing
- **Rich evaluation** - Automated tests, scores, logs

**Main file to edit:** `run.py` (configure agents, projects, settings)
