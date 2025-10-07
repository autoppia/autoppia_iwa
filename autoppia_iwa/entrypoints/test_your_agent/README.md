
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
  "ip": "127.0.0.1",
  "port": 5000,
  "projects": ["DemoWeb1"],
  "num_use_cases": 5,
  "runs": 3,
  "use_cases": ["Login", "Checkout"],
  "timeout": 120,
  "id": "1",
  "name": "TestAgent",
  "should_record_gif": false,
  "save_results_json": false,
  "plot_results": false
}
```

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
