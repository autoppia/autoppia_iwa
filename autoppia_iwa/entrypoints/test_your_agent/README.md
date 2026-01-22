
# test-your-agent Endpoint

This module provides a FastAPI service for benchmarking web agents on demo web projects. It automates task generation, agent evaluation, and returns detailed results including prompts, actions, scores, and timing metrics.

## Features

- **Benchmark Automation**: Runs agents against selected web projects and use cases.
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
  "ip": "127.0.0.1", // or full base URL like "http://127.0.0.1:5000" or "https://agent.example.com"
  "port": 5000,       // optional; omit if ip is a full URL or you want default port
  "projects": ["DemoWeb1"],
  "runs": 3,
  "use_cases": ["Login", "Checkout"],  // optional; if null/empty, uses all available use cases
  "timeout": 120,
  "id": "1",
  "name": "TestAgent",
  "should_record_gif": false,
  "save_results_json": false,
  "plot_results": false,
  "dynamic": false  // optional; if true, tasks will include random seeds for dynamic content
}
```

#### Behavior

- If `ip` includes a scheme (e.g., starts with `http://` or `https://`), the service will use it as the base URL and ignore `port`.
- If `ip` is a plain hostname/IP (e.g., `127.0.0.1`), the service will:
  - include `:port` if `port` is provided
  - omit the port otherwise (e.g., `http://127.0.0.1`).

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
