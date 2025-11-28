# Data Directory

This directory contains **all data** used by the system (both inputs and outputs).

## 📁 Structure

```
data/
├── inputs/               # INPUT data (stable, required)
│   ├── web_voyager/     # Reference dataset (643 tasks)
│   └── reward_model/    # RM training data and checkpoints
│
└── outputs/              # OUTPUT data (generated, temporary)
    ├── benchmark/        # Benchmark results
    │   ├── results/
    │   ├── per_project/
    │   ├── logs/
    │   ├── recordings/
    │   └── cache/
    └── dynamic_mutations_verification/
```

## 🎯 Purpose

Centralizes all data (inputs and outputs) in one location for:
- ✅ Easier backup (tar -czf backup.tar.gz data/)
- ✅ Simpler Docker volumes (mount only data/)
- ✅ Clear gitignore (data/outputs/**)
- ✅ Logical grouping

## 📊 Inputs vs Outputs

| Directory | Type | Changes? | Version Control? |
|-----------|------|----------|------------------|
| `data/inputs/` | Inputs | Rarely | ✅ Yes (or download) |
| `data/outputs/` | Outputs | Every run | ❌ No (gitignored) |

## 🧹 Cleanup

```bash
# Clean all outputs (safe - can regenerate)
rm -rf data/outputs/*

# Keep inputs (important reference data)
# data/inputs/ should be backed up or version controlled
```

## 🔄 Relationship

```
data/inputs/              data/outputs/
(what system needs)  →   (what system generates)

web_voyager/         →   benchmark/results/
reward_model/ckpts/  →   benchmark/logs/
```

The system reads from `data/inputs/` and writes to `data/outputs/`.
