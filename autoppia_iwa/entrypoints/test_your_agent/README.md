
# test-your-agent Endpoint

This module provides a FastAPI service for benchmarking web agents on demo web projects. It automates task generation, agent evaluation, and returns detailed results including prompts, actions, scores, and timing metrics.

## Features

- **Benchmark Automation**: Runs agents against selected web projects and use cases.
- **Same /act endpoint**: The service calls your agent via **POST /act** (same contract as the main benchmark).
- **Evaluator selection**: Choose `evaluator_mode`: **concurrent** (one /act call per task, full action list) or **stateful** (repeated /act with browser snapshot each step).
- **Detailed Results**: Returns per-agent, per-task results with prompt, actions, score, use case, and timing.
- **Configurable**: Supports custom agent configuration, number of runs, use cases, and result recording options.
- **JSON Output**: Results are structured for easy consumption and analysis.

## Usage

### Start the Service

```bash
python -m autoppia_iwa.entrypoints.test_your_agent.api_endpoint [PORT]
```

Or use the provided deployment script to deploy with PM2:

```bash
./autoppia_iwa/entrypoints/test_your_agent/deploy_endpoint.sh [PORT]
```

### API Endpoint

- **POST** `/test-your-agent`

#### Request Body (`AgentConfig`)

```json
{
  "ip": "127.0.0.1",
  "port": 5000,
  "projects": ["DemoWeb1"],
  "runs": 3,
  "use_cases": ["Login", "Checkout"],
  "timeout": 120,
  "should_record_gif": false,
  "dynamic": false,
  "evaluator_mode": "concurrent",
  "max_steps_per_task": 50
}
```

| Field | Description |
|-------|-------------|
| `ip` | Agent base URL (e.g. `http://127.0.0.1:5000`) or hostname/IP. |
| `port` | Optional; used only when `ip` is hostname/IP. Omit if `ip` is a full URL. |
| `projects` | List of demo project IDs to run. |
| `runs` | Number of runs per project. |
| `use_cases` | Optional; if null/empty, all use cases are used. |
| `timeout` | Request timeout in seconds (default 120). |
| `should_record_gif` | Whether to record GIFs of evaluation. |
| `dynamic` | If true, tasks include random seeds for dynamic content. |
| `evaluator_mode` | `"concurrent"` (default): one **POST /act** per task, agent returns full action list. `"stateful"`: **POST /act** called repeatedly with browser snapshot and `step_index` 0, 1, 2, … |
| `max_steps_per_task` | Max steps per task when `evaluator_mode` is `"stateful"` (default 50). Ignored in concurrent mode. |

**Your agent must expose POST /act** with payload including `task_id`, `prompt`, `url`, `snapshot_html`, `step_index`, and optional `web_project_id`. Response: `{ "actions": [ ... ] }`.

#### Behavior

- If `ip` includes a scheme (e.g. `http://` or `https://`), the service uses it as the base URL and ignores `port`.
- If `ip` is a plain hostname/IP (e.g. `127.0.0.1`), the service will include `:port` if `port` is provided, or omit the port otherwise.

#### Response

Returns a JSON object with per-project, per-agent results including prompts, actions, scores, use cases, and timing statistics.

## File Structure

- `__init__.py`: Package marker.
- `api_endpoint.py`: FastAPI service and endpoint implementation.
- `deploy_endpoint.sh`: Deployment script using PM2.
- `requirements.txt`: Python dependencies for the endpoint.
- `README.md`: Documentation for usage, features, and API details.

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- PM2 (for deployment, optional)
- Other dependencies as specified in the project

## License

See the main repository for license details.
