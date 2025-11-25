# Affine Integration for Autoppia IWA

This directory contains integrations for the **Affine protocol**, which enables distributed training and evaluation of web agents.

## 📁 Structure

```
modules/affine/
├── agentgym_environment/   # 🚀 PRODUCTION - Full AgentGym environment
│   ├── env.py             # Main FastAPI app
│   ├── agent_client.py    # Calls miner /solve_task endpoints
│   ├── config.py          # Configuration management
│   ├── dataset.py         # Task dataset with AgentGym IDs
│   ├── evaluator.py       # Evaluation runner
│   ├── prepare_tasks.py   # Task pre-generation script
│   └── tests/             # Integration tests
│
└── service_deprecated/     # ⚠️ DEPRECATED - Simple single-task service
    ├── server.py          # Minimal evaluation endpoint
    └── Dockerfile         # Basic container
```

## 🚀 Which One to Use?

### **Use `agentgym_environment/` (Recommended)** ✅

For production Affine integration:
- Evaluates **multiple tasks** per request
- Full **AgentGym protocol** compatibility
- Robust dataset management
- Proper error handling
- Tests included

**Run it:**
```bash
uvicorn modules.affine.agentgym_environment.env:app --host 0.0.0.0 --port 8000
```

### **Use `service_deprecated/` (Legacy)** ⚠️

Only for:
- Quick local testing
- Single task evaluation
- Simple debugging

**This will be removed in future versions.**

---

## 🔄 Migration Path

If you're using `affine_service`:

**Old:**
```python
from autoppia_iwa.affine_service.server import app
```

**New:**
```python
from modules.affine.agentgym_environment.env import app
```

**API changes:**
- `task_id` (singular) → `ids` (plural array)
- Response now includes `success_rate`, `details` array, `dataset_size`

---

## 🎯 What is Affine?

**Affine** is a distributed training protocol where:
- **Miners** train/run web agents
- **Validators** evaluate agent performance
- **AgentGym** provides the standard API contract

The `agentgym_environment/` module is the **validator-side** implementation that:
1. Exposes tasks to miners
2. Receives agent solutions
3. Evaluates with IWA system
4. Returns scores to Affine network

---

## 📝 See Also

- [AgentGym Documentation](https://github.com/thudm/agentgym)
- [Affine Protocol](https://affine.ai)
- [IWA Evaluation System](../../autoppia_iwa/src/evaluation/)
