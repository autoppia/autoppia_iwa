# Score Model Pipeline

This document explains the new pipeline structure that powers the reward/score
model dataset. The goal is to keep each phase isolated, reproducible, and easy
to run end-to-end.

```
autoppia_iwa/src/rl/score_model/pipeline/
  data_preparation/   # ingestion, dedupe, feature prep
  training/           # reward-model training shims
  evaluation/         # offline eval helpers
  paths.py            # shared directory conventions
  phases.py           # phase enums + helper dataclass
```

`data/score_model_pipeline/` mirrors the pipeline phases:

```
data/score_model_pipeline/
  raw/            # Exact API dumps
  processed/      # Intermediate parquet/JSONL artifacts
  datasets/       # Final training splits
  metrics/        # Run summaries + stats
```

## Phase overview

1. **Data preparation** – `pipeline/data_preparation` covers ingestion +
   dedupe + feature prep (leaderboard pulls, DOM/event features, semantic labels).
2. **Training** – `pipeline/training` re-exports reward-model shims so CLIs can
   grab configs/checkpoints without digging through nested packages.
3. **Evaluation** – `pipeline/evaluation` bundles the offline score/eval helpers
   to report ROC-AUC, pref win-rate, etc., into the metrics directory.

## Building a dataset from the leaderboard

Use the new CLI to ingest leaderboard data and build a deduplicated dataset in
one step. Filters are applied per website/use-case/success combination to avoid
re-downloading the same datapoints.

```bash
python -m autoppia_iwa.src.rl.score_model.cli.build_score_model_training_dataset \
    --website autocinema --website autobooks \
    --success true --success false \
    --pages-per-filter 5 \
    --limit 200 \
    --dedupe-strategy task_solution
```

Key options:

- `--website/--use-case/--miner-uid` – limit the grid of filters to avoid
  clashing pulls.
- `--success true|false|all` – fetch successes and failures separately.
- `--dedupe-strategy task_solution|task_agent|task` – control how duplicates are
  collapsed before writing the dataset.
- `--output-prefix` – override the default timestamp-based filenames when
  building multiple splits in the same run.

Outputs:

- `data/score_model_pipeline/raw/<prefix>.jsonl` – raw API entries.
- `data/score_model_pipeline/datasets/<prefix>.jsonl` – flattened samples.
- `data/score_model_pipeline/metrics/<prefix>.json` – dataset summary (counts by
  website/use-case, pass/fail ratio, etc.).

From here the existing scripts in `score_model/cli/` can consume the prepared
dataset and move into the feature extraction + training stages without wading
through ad-hoc folders.

## Replay solutions & capture traces

Use the instrumented evaluator to re-run leaderboard solutions and persist DOM /
JS snapshots per action. This is required to build richer features than the
baseline text summary.

```bash
python -m autoppia_iwa.src.rl.score_model.cli.replay_leaderboard_solutions \
  --dataset data/score_model_pipeline/datasets/leaderboard_full_20251110_234743.jsonl \
  --output-dir data/score_model_pipeline/raw_traces/leaderboard_full_20251110_234743 \
  --limit 2000 --per-website-limit 300
```

Tips:
- Ensure the demo web server (ports 8000+) is running before replaying.
- Increase `--limit`/`--per-website-limit` as you scale collection.
- Add `--capture-screenshots` if you want per-action screenshots inside the
  trace JSONL.

Once traces exist, extract structured DOM/JS features:

```bash
python -m autoppia_iwa.src.rl.score_model.cli.build_dom_event_features \
  --traces-dir data/score_model_pipeline/raw_traces/leaderboard_full_20251110_234743 \
  --output-dir data/score_model_pipeline/features/leaderboard_full_20251110_234743 \
  --split-dir data/score_model_pipeline/features/leaderboard_full_20251110_234743/splits
```

These per-step / per-episode JSONL files can feed a stronger reward model that
looks at actual DOM diffs, backend events, and JS signals rather than the
lightweight text features used for smoke tests.
