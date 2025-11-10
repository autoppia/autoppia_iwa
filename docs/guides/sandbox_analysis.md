# Sandbox Dataset Analysis

Use `python -m modules.web_verification.entrypoints.analyze_sandbox` to audit datasets collected from sandbox miners/agents.

## Dataset format

- JSON array (`[ ... ]`), object with `entries: [ ... ]`, or JSONL (one record per line).
- Required keys per entry:
  - `project_id`, `use_case`, `task_id`
  - `url`, `prompt`, optional `seed`
  - `solutions`: list of objects containing `agent_id`, `final_score` (or `score`), optional `actions`, `action_count`, `evaluation_time`
  - optional `task`: serialized `Task` payload (kept for future re-evaluation)

## Running the analyzer

```bash
python -m modules.web_verification.entrypoints.analyze_sandbox data/sandbox_dump.json \
  --report data/sandbox_analysis_report.json \
  --success-threshold 0.99 \
  --sample 5
```

The script computes:

- per-project/use-case averages (`overview`)
- unresolved tasks (0 % success)
- trivial tasks (≈100 % success with ≤3 actions)
- agent action diversity (detect memorization)
- seed variability (flags low variance → possible broken dynamics)

Outputs:

- JSON report (`--report`) for downstream pipelines
- Console previews of the main findings

## Next steps

The dataset loader preserves `task` payloads and full action lists so we can later plug re-evaluation and GIF generation. The current stage focuses on statistical analysis; replays will be added once we plug the production DB directly.*** End Patch*** End Patch
