# Evaluation Tests

Tests for **ConcurrentEvaluator** and **AsyncStatefulEvaluator**: mock-based tests run without services; real-server (integration) tests require the demo webs stack to be deployed.

## Test types

- **Mock tests** — Real Playwright browser, mock HTML (data URL), mock backend. No server required. Run in CI.
- **Real-server tests** — Real browser, real demo frontend and backend. Require the server and **web 1 (autocinema)** to be running; otherwise they are **skipped**.

## Requirements for real-server tests

To run the real-server evaluation tests you must have:

1. **Demo webs server deployed**
   - Backend (webs_server) reachable, e.g. `http://localhost:8090`
   - Health check: `curl http://localhost:8090/health`

2. **Web 1 – Autocinema**
   - Frontend for autocinema (web 1) reachable, e.g. `http://localhost:8000`
   - The real-server tests use the autocinema app and the **FILM_DETAIL** event (search → open film detail).

If the backend is not reachable, real-server tests are **skipped** so the suite still passes (e.g. in CI without services).

## Running tests

```bash
# All evaluation tests (mock tests run; real-server tests skip if server down)
pytest tests/evaluation/ -v

# Mock-only (no server required)
pytest tests/evaluation/ -v -k "not real_server"

# Real-server integration tests only (server + web 1 autocinema required)
pytest tests/evaluation/ -v -k "real_server" -m integration
```

## Files

| File | Description |
|------|-------------|
| `test_concurrent_evaluator.py` | ConcurrentEvaluator: mock tests + real-server FILM_DETAIL tests |
| `test_stateful_evaluator.py`   | AsyncStatefulEvaluator: mock tests + real-server FILM_DETAIL tests (step-based) |
| `test_concurrent_evaluator_helpers.py` | Helpers for URL/navigation checks |

## Real-server test flow

- **Concurrent:** One solution (Navigate → Type "Inception" → Click search → Click view details); evaluator runs all actions then scores using backend events. Pass test expects FILM_DETAIL with `name: "Inception"`; fail test uses `name: "The Matrix"` and expects score 0.
- **Stateful:** Same actions in two logical steps (step 1: type + search submit; step 2: view details). A short `WaitAction` after the view-details click can be added so the backend has time to receive the FILM_DETAIL event before scoring.
