# Web Verification Entrypoints

This document explains what the `modules.web_verification.entrypoints.*` CLIs validate and how every gate in the pipeline maps to concrete checks. All paths are relative to the repo root.

## Phase Snapshot

| # | Gate | Uses LLMs | Primary scripts |
|---|------|-----------|-----------------|
| 1 | Module Scaffold & Metadata | No | `modules/web_verification/verify_project.py` |
| 2 | Deck Consistency | No | `modules/web_verification/verify_project.py` |
| 3 | Use-Case & Event Integrity | No | `modules/web_verification/verify_project.py` |
| 4 | Frontend Reachability & Code Analysis | No | `modules/web_verification/verify_project.py`, `modules/web_verification/frontend_analysis.py` |
| 5 | Visual Evidence & LLM Review | Yes | `modules/web_verification/visual_inspector.py` |
| 6 | LLM Task/Test Pipeline | Yes | `modules/web_verification/verify_project.py` |
| 7 | Dynamic Mutation Integrity | Yes | `modules/web_verification/dynamic_validation.py` |
| 8 | Random Baseline | Yes | `modules/web_verification/verify_project.py` |

`python -m modules.web_verification.entrypoints.verify` executes phases 1–8 when LLM credentials are available. `python -m modules.web_verification.run_deck_pipeline` runs phases 1, 2, 4, and 5 for quick deck vetting.

## Phase Details & Checks

### 1. Module Scaffold & Metadata Gate
* **Project directory exists** – `src/demo_webs/projects/<slug>` must be present (no hidden rewrites).
* **Required files** – `main.py`, `use_cases.py`, `events.py`, `generation_functions.py` are mandatory (`ensure_required_files`).
* **Module import** – `main.py` must import cleanly; failures halt the pipeline.
* **WebProject exposure** – the module must instantiate `WebProject` with populated `id`, `name`, `frontend_url`, and `use_cases`.

### 2. Deck Consistency Gate
* **Deck file lookup & parse** – finds `<slug>.deck.json` (or override) and validates JSON schema.
* **Metadata harmony** – `project_id`/`project_name` must match the `WebProject` fields.
* **Use-case parity** – deck use-cases match code (no missing/extra names, events align).
* **Page coverage** – `pages` list is non-empty so later Playwright phases know what to load.

### 3. Use-Case & Event Integrity Gate
* **`ALL_USE_CASES` defined** – exported list exists and only contains `UseCase` objects.
* **Name/description hygiene** – unique names, descriptions, and example prompts (each example needs `prompt` and `prompt_for_task_generation`).
* **Event wires** – every use case references an event listed in `EVENTS`; duplicates or missing ValidationCriteria fail the gate.
* **Constraint generators** – any `constraints_generator` attribute must resolve to a callable inside `generation_functions.py`.

### 4. Frontend Reachability & Code Analysis Gate
* **Frontend probe** – `_check_frontend_health` issues an HTTP GET to `web_project.frontend_url` and records the status.
* **Source discovery** – `_locate_frontend_dir` maps the module to `modules/webs_demo/*` so static analysis can run.
* **Event emission scan** – `frontend_analysis.analyze_frontend` ensures each declared event string shows up in the codebase (references capped at 5 per event).
* **Code quality warnings** – any missing frontend directory, unreadable files, or skipped analysis steps are surfaced under `report.web_analysis.issues`.

### 5. Visual Evidence & LLM Review Gate [LLMs]
* **Deck-driven crawling** – `visual_inspector.run_inspector` opens every deck page via Playwright, applying the `url_patterns`/`required_elements` contract.
* **Screenshot capture** – per page we store a PNG + HTML/text snapshot under `data/web_verification/visual_inspector` and attach summaries back to the report.
* **LLM judge (optional)** – when enabled, the captured screenshot + HTML snippet are sent to the configured LLM service to confirm the rendered UI matches the textual deck description.

### 6. LLM Task/Test Pipeline Gate [LLMs]
* **Task generation** – `TaskGenerationPipeline` produces prompts for up to `AUTOPPIA_TASKS_PER_USE_CASE` use cases.
* **Prompt integrity** – `_check_task_prompts` rejects unresolved placeholders (`<constraints_info>`) or prompts that omit declared constraint values.
* **LLM spot-check** – `_llm_validate_tasks` samples prompts so an LLM can flag nonsensical tasks before they reach miners.
* **Test generation** – `GlobalTestGenerationPipeline` adds `CheckEventTest` instances; missing or misaligned events fail the gate.

### 7. Dynamic Mutation Integrity Gate [LLMs]
* **Seed discipline** – `dynamic_validation.py` loads deck pages in Playwright with `seed=None` and deterministic seeds, ensuring seedless requests stay untouched while seeded runs inject variation only when the deck’s `dynamic_profile` demands it.
* **Cross-seed variance** – computes HTML similarity deltas between baseline and each seed (plus seed-vs-seed comparisons) so different seeds must diverge measurably whenever mutations are expected.
* **Reproducibility** – reruns identical seeds and checks similarity ratios stay ≥ the configured threshold; any flaky mutation plans fail the gate.
* **LLM corroboration** – when LLMs are enabled, truncated HTML snapshots and the heuristic deltas are sent to the judge, who confirms (via JSON verdict) that the observed changes align with the deck narrative.

### 8. Random Baseline Gate [LLMs]
* **RandomClicker audit** – ensures the naïve agent never solves a task; any non-zero score indicates selectors are too easy or validation is weak.
* **Semantic LLM review** – if any baseline run reports success, its action trace is summarized and sent to the LLM judge to confirm coherence.

## Running the Pipeline

* **Full verification**: `python -m modules.web_verification.entrypoints.verify <slug> --deck path/to/deck.deck.json`
* **Deck-only fast path**: `python -m modules.web_verification.run_deck_pipeline path/to/deck.deck.json --project-slug <slug> --base-url https://preview/...`

The dynamic gate (#7) lives in `modules/web_verification/dynamic_validation.py` and already shells out to Playwright for multi-seed captures. When the reverse proxy lands, replace the navigation helper there without changing the surrounding checks or LLM review.
