### 🧠 Browser-use Agent — Infinite Web Arena (IWA)
Simple, Playwright-powered browser agent integrated with IWA.

This agent wraps `browser-use` to execute real browser actions during IWA benchmarks.

### ⚙️ Requirements
- `playwright` and browser binaries
- `browser-use` (version pinned in root `requirements.txt`)

Install everything via the root setup script:
```bash
bash setup.sh
```

Or manually:
```bash
pip install -r requirements.txt
playwright install --with-deps
```

### 🚀 Quickstart
The agent class lives at `autoppia_iwa/src/web_agents/browser-use/agent.py` as `BrowserUseWebAgent`.

Minimal usage inside IWA flows:
```python
from autoppia_iwa.src.web_agents.browser_use.agent import BrowserUseWebAgent, BrowserUseConfig

agent = BrowserUseWebAgent(BrowserUseConfig(headless=True))
solution = await agent.solve_task(task)  # returns TaskSolution with recording=AgentHistoryList
```

Config fields:
- `llm_provider`: "openai" | "anthropic" (default: openai)
- `llm_model`: model string (default from `OPENAI_MODEL`)
- `max_steps`: int (default 15)
- `use_vision`: bool (default False)
- `headless`: bool (default False)

Environment configuration for LLMs is defined in `autoppia_iwa/config/config.py`.

### 🧪 IWA Integration
- Accepts `Task` with viewport from `Task.specifications`.
- Returns `TaskSolution` with `recording` containing the `AgentHistoryList`.
- Resources are cleaned after each run; call `await agent.stop()` to cancel early.

### 🔧 Adapting IWA Actions for Evaluation
IWA evaluators consume lists of actions derived from `BaseAction` (see `autoppia_iwa/src/execution/actions/base.py`).

If you want evaluation to replay or analyze actions, adapt `AgentHistoryList` into IWA actions before returning the `TaskSolution`:
```python
# sketch only: map browser-use history into IWA BaseAction instances
from autoppia_iwa.src.execution.actions.base import BaseAction  # and concrete actions

def history_to_actions(history) -> list[BaseAction]:
    mapped = []
    for step in history or []:  # step structure depends on browser-use version
        # Example: convert a "click" or "navigate" step into your action types
        # mapped.append(ClickAction(selector=step.selector))
        # mapped.append(NavigateAction(url=step.url))
        pass
    return mapped

# In solve_task():
# actions = history_to_actions(history)
# return TaskSolution(task_id=task.id, actions=actions, web_agent_id=self.id, recording=history)
```

Notes:
- Choose or create concrete actions that match your evaluator needs.
- Keep text/URL fields aligned with evaluation assertions so tests can validate outcomes.

### 📝 Notes
- Keep `requirements.txt` in sync with your local environment.
- If Playwright install fails with `--with-deps`, retry without it (the setup script does this automatically).
