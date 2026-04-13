# DE Verification In Pipeline (Seed 1)

This document explains how the new Data Extraction (DE) trajectory verification works in the web verification pipeline.

## Why `--data-extraction-seed` exists

Short answer: the seed in the command is a **selector**, not a replacement of the seed stored in trajectories.

- Each DE trajectory already has its own `seed` field (for example `seed=1`).
- The pipeline flag `--data-extraction-seed` tells the verifier which trajectory group to run.
- In `dataset_only` mode, that same seed is also used to load the dataset for validation.

So both are needed:
- trajectory seed = metadata in each trajectory
- CLI seed = which seed group to execute now

If all your trajectories are seed 1 (current situation), you usually do not need to pass the flag because default is already `1`.

## Current behavior

Step 2.5 is now **project-level**:

- It runs once per project.
- It executes all DE trajectories for that project and selected seed.
- It prints one boolean result in console:
  - `DataExtraction trajectories passed: YES`
  - `DataExtraction trajectories passed: NO`
  - `N/A` if skipped (for example, no trajectories for that seed).

## Validation modes per trajectory

- `dataset_only`: trajectory has `actions=None`; verifier checks `expected_answer` inside dataset loaded with the selected seed.
- `replay`: trajectory has browser actions; verifier replays actions and compares extracted output with `expected_answer`.

## End-to-end flow

1. Load project trajectories from registry.
2. Filter by `trajectory.seed == --data-extraction-seed`.
3. Execute each selected trajectory (`dataset_only` or `replay`).
4. Aggregate a single project result:
   - `all_passed` boolean
   - `passed_count/total_count`
5. Print `DataExtraction trajectories passed` in pipeline summary.

## Command examples

From repo root:

```bash
.venv/bin/python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocinema
```

Explicit seed (only needed if you want another seed group):

```bash
.venv/bin/python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocinema --data-extraction-seed 1
```

