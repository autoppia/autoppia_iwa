# RL Web Agent: Project State and How‑To

This document explains what is implemented today for training and evaluating RL‑based web agents in this repository, how pieces fit together, and how to run training/benchmarking locally.

## Current Status

- Functional RL environment with observations, action masking, Top‑K DOM ranking, loop detection, and reward shaping.
- Two browser backends:
  - Mock/toy adapters for fast development without Playwright.
  - Concurrent Playwright adapter for real demo websites.
- Benchmark integration: a local `RLPolicyAgent` is wired into the benchmark to generate `TaskSolution`s.
- Training pipeline stubs: PPO‑RNN trainer, checkpoint evaluation, and BC dataset collection.

> **Note:** The RL codebase now lives under `autoppia_iwa/src/rl/agent/…`. Paths below still refer to their historical locations for quick reference; prepend `agent/` (for example, `autoppia_iwa/src/rl/agent/envs/iwa_gym_env.py`) when navigating the repo.

## Key Components (files)

- Environment and core RL helpers:
  - `autoppia_iwa/src/rl/envs/iwa_gym_env.py`
  - `autoppia_iwa/src/rl/envs/dom_ranker.py`
  - `autoppia_iwa/src/rl/envs/obs_builders.py`
  - `autoppia_iwa/src/rl/envs/rewards.py`
  - Types: `autoppia_iwa/src/rl/envs/types.py`
- Browser adapters:
  - Concurrent (real Playwright): `autoppia_iwa/src/rl/drivers/concurrent_adapter.py`
  - Toy (no Playwright, stateful): `autoppia_iwa/src/rl/drivers/toy_adapter.py`
  - Mock (stateless): `autoppia_iwa/src/rl/drivers/mock_adapter.py`
  - Facade: `autoppia_iwa/src/rl/drivers/browser.py`
- Validator layer:
  - IWA adapter: `autoppia_iwa/src/rl/validator/iwa_evaluator_client.py`
  - Toy validator (binary success): `autoppia_iwa/src/rl/validator/toy_validator.py`
- Web agents:
  - RL planning agent (in‑process): `autoppia_iwa/src/web_agents/rl/rl_policy_agent.py`
  - Re‑export: `autoppia_iwa/src/web_agents/rl/__init__.py`
- Training / evaluation entrypoints:
  - Train PPO: `autoppia_iwa/entrypoints/rl/train_ppo.py`
  - Evaluate checkpoint: `autoppia_iwa/entrypoints/rl/eval_checkpoint.py`
  - Collect BC dataset: `autoppia_iwa/entrypoints/rl/collect_bc.py`
- Benchmark:
  - Orchestrator/config: `autoppia_iwa/entrypoints/benchmark/*.py`
  - RL agent already listed in agents: `autoppia_iwa/entrypoints/benchmark/run.py`

## RL Environment (summary)

- Action space (discrete):
  - `NOOP`, `CLICK_1..K`, `FOCUS_1..K`, `TYPE_CONFIRM`, `SUBMIT`, `SCROLL_UP`, `SCROLL_DOWN`, `BACK`.
- Observations (Dict):
  - `goal_ids`, `dom_ids`, `url_id`, `prev_actions`, `topk_meta`, `topk_text_ids`, `inputs_filled_ratio`, `cart_items`.
- Ranking & masks:
  - `rank_clickables()` ranks DOM elements and builds click/focus masks; environment augments masks with macro feasibility (submit/scroll/back).
- Rewards (`rewards.py`):
  - Dense shaping: +milestones (URL change, input filled, cart increase), −step, −invalid, −loop.
  - Binary success via validator; milestone shaping can also be provided by the validator.
- Termination: success/invalid from validator or truncation at `max_steps`.

## Browser Backends

- Toy adapter: `ToyAdapter` simulates an input + submit workflow for fast PPO smoke training.
- Concurrent adapter: wraps the Playwright executor used in IWA, enabling real demo‑web interaction.
- Mock adapter: static snapshot for unit tests.

## Web Agent for Benchmark

- `RLPolicyAgent` (in `src/web_agents/rl/`): builds a short `TaskSolution` plan without mutating the site.
  - Uses the same Top‑K and masks as the env.
  - Maps to `BaseAction`s: `ClickAction(x,y)`, `TypeAction(text)`, `SendKeysIWAAction('Enter')`, `ScrollAction`, `NavigateAction(go_back=True)`.
  - Already added to `AGENTS` in `entrypoints/benchmark/run.py`.

## Train and Evaluate (toy → fast loop)

Prereq (conda env active): install RL libs

- `pip install stable-baselines3 sb3-contrib torch tensorboard`

Train PPO‑RNN on toy backend

- `python -m autoppia_iwa.entrypoints.rl.train_ppo --adapter toy --n-envs 4 --total-steps 500000 --logdir runs/ppo_iwa_rnn`

Evaluate checkpoint on env

- `python -m autoppia_iwa.entrypoints.rl.eval_checkpoint --adapter toy --ckpt runs/ppo_iwa_rnn/ppo_iwa_rnn.zip --episodes 100 --deterministic`

Collect a small BC dataset (optional)

- `python -m autoppia_iwa.entrypoints.rl.collect_bc --episodes 200 --out runs/bc_toy_dataset.npz`

## Run the Benchmark with the RL Agent

- Ensure Playwright browsers if you plan to use real demos: `playwright install`
- Optional: set a trained model path (defaults to `/data/rl/models/ppo_real.zip`):
  - `export RL_MODEL_PATH=/path/to/ppo_real.zip`
- Run benchmark for the in-repo RL agent:
  - `python -m autoppia_iwa.entrypoints.rl.benchmark`

This uses the standard benchmark orchestrator with `RLModelAgent`, executes on demo web projects, and reports results per project/agent.

## Roadmap (short)

- PPO‑RNN baseline → add action‑masking in policy (maskable PPO or custom masked logits).
- BC warm‑start using collected trajectories; combine with PPO loss.
- Curriculum + domain randomization on demo‑webs; logging of DOM diffs and action heatmaps.
- Planner LLM for subgoals and Top‑K hints at reset/atascos; distill to a small ranker.
- VLM (clip/siglip) for `screen_emb` in observations; fuse with DOM tokens.
- Offline RL (IQL/CQL) on full buffers; PBT for hyperparameters.

## Notes & Limitations

- The training stubs default to the toy adapter. Using the concurrent adapter trains with shaping; binary success is best measured via the benchmark/evaluator.
- `RLPolicyAgent` is a greedy baseline to validate the benchmark path. A trained policy agent can be added alongside, reusing the same mapping to `TaskSolution`.
- Playwright setup (`playwright install`) is required for running real browsers.

---

If you want, we can add Makefile targets for `train-toy`, `eval-toy`, and `bench-rl`, or wire BC warm‑start into the PPO trainer.
