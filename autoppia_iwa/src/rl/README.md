# RL package layout

The RL stack is now split into two clear projects under `autoppia_iwa/src/rl`:

1. **`score_model/`** – data pipelines and training code that build the reward / score model used for shaping.
2. **`agent/`** – everything required to run the interactive web-environment, SB3 integration, evaluators, and utilities used by the RL agents.

```
src/rl/
├── score_model/
│   ├── cli/            # feature extraction, dataset builders, trainers
│   ├── configs/        # YAML defaults for labelers and training jobs
│   ├── datasets/       # dataset loaders + builders
│   ├── features/       # DOM snapshot encoders
│   ├── llm/            # offline semantic labeling helpers
│   ├── models/         # reward/semantic model definitions
│   ├── rl/             # RewardBlender + VecNormalize hooks
│   ├── training/       # training loops and losses
│   └── utils/          # shared helpers (text encoders, IO, etc.)
└── agent/
    ├── benchmark/      # instrumentation-friendly benchmark wrappers
    ├── data/           # task generators and cached assets
    ├── entrypoints/    # runnable scripts for PPO, trace collection, etc.
    ├── envs/           # Gym environments (e.g., IWAWebEnv)
    ├── evaluators/     # evaluator implementations
    ├── execution/      # action adapters and browser executors
    ├── instrumentation/# Playwright/JS instrumentation helpers
    ├── offline/        # behavior cloning + dataset ingestion
    ├── runtime/        # stateful evaluators, browser manager, etc.
    ├── utils/          # agent-side helpers (solutions, logging, …)
    └── web_agents/     # RL-backed IWebAgent adapters
```

This structure keeps the score-model training loop isolated from the interactive RL
environment so each workflow can evolve independently while sharing only the
RewardBlender interface.
