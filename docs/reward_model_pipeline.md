# Reward Model Pipeline (`autoppia_iwa[rl]`)

This document summarises the end-to-end process for training and integrating the
learned reward model that augments binary test rewards during PPO training.

## Directory overview

```
autoppia_iwa/src/rl/score_model/
  cli/                  # CLI helpers (extract features, build pairs, train models)
  configs/              # YAML defaults for labeler/encoders/reward wrapper
  models/              # Pydantic schemas + neural modules
  features/            # Snapshot → observation utilities
  llm/                 # Offline LLM labelling helpers
  datasets/            # Builders and PyTorch datasets
  training/            # Training loops + losses
  rl/                  # Runtime reward blender + VecNormalize helpers
  utils/               # Hash-based text encoders and IO utilities
data/rm/               # Reward model data (raw dumps, cached artefacts)
```

## Quick data collection

If you have access to the production task API you can mirror fresh evaluations
before running the reward-model builders. See `docs/prod_data_ingestion.md` for
the full API reference and the `fetch_prod_data.py` helper.

Otherwise, run a tiny benchmark batch with JS instrumentation enabled to populate `data/rm/raw_traces`:

```bash
python -m autoppia_iwa.src.rl.agent.entrypoints.collect_js_traces --projects autobooks autocalendar --runs 1 --prompts-per-use-case 1
```

Override `--output-dir` or `--capture-screenshots` to tweak what goes into each JSONL trace.

## Required inputs

1. Export evaluation episodes (`EvaluationEpisode` jsonl) into `data/rm/raw_evaluations/`.
   Each line must include the action results, browser snapshots, and final test
   score for the episode.
2. Provide split definitions in `data/rm/splits/`:
   - `semantic_train.json` / `semantic_val.json`: lists of `"episodeId_step"` ids.
   - `reward_train.json` / `reward_val.json`: lists of `{ "id": str, "success": bool }`.

## Pipeline steps

1. **Extract observations & LLM semantics**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.extract_llm_features
   ```
   - Cleans DOM text, tokenises URLs, and stores observation JSON + cached LLM
     semantic labels in `data/rm/features/`.

2. **Build preference pairs**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.build_pairs
   ```
   - Uses final scores to select positive/negative steps and stores pairs in
     `data/rm/pairs/pairs.jsonl`.

3. **Train semantic encoder (optional but recommended)**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.train_semantic_encoder --config autoppia_iwa/src/rl/score_model/configs/semantic_encoder.yaml
   ```
   - Distils LLM semantic labels into a lightweight encoder. The checkpoint is
     saved under `data/rm/ckpts/semantic_encoder.pt`.

4. **Build DOM + JS event features (new)**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.build_dom_event_features \
       --traces-dir data/rm/raw_traces \
       --output-dir data/rm/features \
       --split-dir data/rm/splits
   ```
   - Converts the instrumented traces into per-step/episode JSONL datasets that
     power reward-model baselines.

4. **Train reward model**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.train_reward_model --config autoppia_iwa/src/rl/score_model/configs/rm_train.yaml
   ```
   - Optimises the preference win-rate and success BCE. Produces the reward model
     checkpoint at `data/rm/ckpts/reward_model.pt`.

5. **(Optional) Train DOM-event baseline**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.train_dom_event_baseline \
       --steps-file data/rm/features/train_dom_event_steps.jsonl
   ```
   - Fits a quick Gradient Boosting classifier on the per-step dataset to sanity-check feature quality; checkpoint saved to `data/rm/ckpts/dom_event_baseline.pkl`.

6. **(Optional) Evaluate baseline**
   ```bash
   python -m autoppia_iwa.src.rl.score_model.cli.eval_dom_event_baseline --split val
   ```
   - Loads the saved model and reports accuracy/precision/recall/F1 on the requested split (`val` or `test`).

5. **Integrate with PPO**
   - Load the checkpoint via `autoppia_iwa.src.rl.score_model.rl.reward_wrapper.RewardBlender`.
   - Blend shaped reward with binary test reward in the training loop:
     ```python
     blender = RewardBlender("data/rm/ckpts/reward_model.pt", alpha=0.5, beta=0.5)
     shaped_reward = blender.compute(url=info["current_url"],
                                     html_text=html_snapshot,
                                     binary_reward=reward,
                                     semantic_hint=None)
     ```
   - Call `blender.reset()` at the beginning of each episode to clear the
     potential term.

## Notes

- The LLM (default `gpt-5`) is used **offline only**; at runtime the PPO model
  sees purely local encodings.
- Hash-based text encoders provide deterministic fixed-size vectors without
  additional dependencies. Swap them with stronger embeddings when ready.
- Cached artefacts (`data/rm/features`, `data/rm/llm_labels`, `data/rm/pairs`) should be
  versioned alongside the checkpoint for reproducibility.
- Preference sampling parameters can be tuned in `autoppia_iwa/src/rl/score_model/configs/rm_train.yaml`.
- The reward wrapper expects HTML and URL at each step; plug into
  `IWAWebEnv.step` after snapshot retrieval.
