# Dynamic Mutations, Proxy & Verification Report

## Context
- **Objective**: Deliver deterministic-yet-diverse demo webs so the benchmark can stress agents on DOM selectors, attribute churn, and surprise overlays without forking each project’s codebase.
- **Scope**: Mutation generation (`modules/web_verification/phases/dynamic`), the dynamic proxy container (`modules/dynamic_proxy`), and the multi‑gate verification pipeline (`modules/web_verification`).

## Iteration Timeline
### 1. Universal Runtime
- The proxy-injected `runtime.js` now owns D1 (structural wrappers/spacers), D3 (deterministic id/name churn), and D4 (seeded banners/modals) for every site; per-project `mutations.py` are gone.
- Overlay injection uses the same deterministic PRNG and exposes telemetry through `window.__DYNAMIC_MAP__` so verification can capture which variant fired.
- Issues hit:
  - We had to throttle overlay creation (interaction counter + timeout) to avoid stacking multiple dialogs in SPAs.
  - Removing project palettes required ensuring the proxy never falls back to server-side D1/D3/D4 when `inject_client_runtime` is enabled.

### 2. Dynamic Proxy Stability
- Proxy now strips `content-encoding` only when responses are mutated and forces upstream `Accept-Encoding: identity`, fixing the browser’s `ERR_CONTENT_DECODING_FAILED` errors.
- Client-side runtime injects DOM diffs for SPAs so server mutations remain minimal.
- Issues hit:
  - Movies/books projects (Django) caused container crashes due to malformed `mutations.py`; palette fixes resolved JSON decode errors.
  - Host‑network proxy originally bound to 6000–6012, but browsers expected 9000+, so we rebuilt the image and config to align with the 9000-range mapping.
### 3. Verification Pipeline Reorganization
- Moved the entire web verification module under `modules/web_verification/phases/*` (procedural, visual, dynamic, sandbox, deck) and exposed subcommands (`verify`, `run-deck`, `flow-screenshots`, `project-screenshots`, `generate-module`, `analyze-sandbox`) via `python -m modules.web_verification …`.
- Updated docs/tests to use the unified `python -m modules.web_verification <command>` entrypoint and refreshed deck/sandbox references.
- Issues hit:
  - Running `python -m pytest` still fails without RL extras (`stable_baselines3`); install `requirements-rl.txt` to exercise the benchmark tests.
  - Verification CLI halts at phase 2 whenever demo-web containers or the proxy aren’t up, so reports like `omnizone_3` remain “frontend unreachable” until the stack is running.

## Outstanding Risks
- **Environment parity**: The proxy/runtime still assumes the demo-web fleet + host-network proxy are running locally; without them, verification halts at the frontend health gate.
- **Dependency footprint**: Benchmark tests import the RL stack by default; set up the RL environment or mark those suites as optional in CI to avoid repeated `ModuleNotFoundError`.
- **Report freshness**: Dynamic audit markdowns still reference older runs (many lack screenshots); rerun `python -m modules.web_verification project-screenshots …` per slug after the proxy is confirmed healthy.

## Next Recommended Steps
1. Install RL extras (`pip install -r requirements-rl.txt`) and rerun `python -m pytest` so the benchmark smoke tests are green.
2. Bring up the demo-web Docker compose stack + dynamic proxy (ports 9000–9012), then run `python -m modules.web_verification verify <slug>` to refresh `data/web_verification/reports`.
3. Consider adding a lightweight health check script under `modules/web_verification/phases/procedural` to ensure each 900x port responds before launching long verification jobs.
