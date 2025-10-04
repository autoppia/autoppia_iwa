# Evaluation Service

Fast validation endpoint for agents to check if their solutions will pass task tests **before** timeout.

## Quick Start

### 1. Start the Service

```bash
python -m autoppia_iwa.entrypoints.evaluation.endpoint
```

Service starts on `http://localhost:5060` by default.

### 2. Use in Your Agent

```python
from autoppia_iwa.entrypoints.evaluation.client import EvaluationClient

async with EvaluationClient() as client:
    result = await client.check_solution(task, actions, web_agent_id)

    if result.success:
        print(f"✓ Solution will pass! (score: {result.final_score})")
    else:
        print(f"✗ Solution will fail (score: {result.final_score})")
```

## API Endpoints

### `POST /evaluate`

Validates a task solution and returns success status.

**Request:**
```json
{
  "task_id": "task-123",
  "prompt": "Retrieve user details for 'Jane Doe'",
  "url": "http://localhost:8008/",
  "tests": [{"type": "CheckEventTest", "event_name": "VIEW_USER_PROFILE", ...}],
  "actions": [{"type": "ClickAction", "selector": "#login-btn"}],
  "web_agent_id": "agent-1",
  "web_project_id": "autoconnect",
  "relevant_data": {},
  "should_record": false,
  "timeout_seconds": 60
}
```

**Response:**
```json
{
  "success": true,
  "final_score": 1.0,
  "raw_score": 1.0,
  "execution_time": 2.5,
  "tests_passed": 3,
  "total_tests": 3,
  "action_count": 5,
  "had_errors": false,
  "error_message": null
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "evaluation-endpoint",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

## Testing

### Test with curl

```bash
# Health check
curl http://localhost:5060/health

# Evaluate solution
curl -X POST http://localhost:5060/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-task",
    "prompt": "Navigate to homepage",
    "url": "http://localhost:8000/",
    "tests": [],
    "actions": [{"type": "NavigateAction", "url": "http://localhost:8000/"}],
    "web_agent_id": "test-agent",
    "web_project_id": "autozone"
  }'
```

### Test with Python

```python
from autoppia_iwa.entrypoints.evaluation.client import quick_check

# Quick boolean check
will_pass = await quick_check(task, actions, "agent-1")
```

## Configuration

- **Port:** Set via CLI: `python -m autoppia_iwa.entrypoints.evaluation.endpoint 8080`
- **Timeout:** Set via env: `EVAL_ENDPOINT_TIMEOUT=120` (default: 60s)
- **Log Level:** Set via env: `LOG_LEVEL=DEBUG` (default: INFO)

## Success Threshold

Solutions pass when `final_score >= 0.25` (same threshold as benchmark).
