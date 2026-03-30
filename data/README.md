# Data Directory

This directory is gitignored. All generated/cached data goes here, organized by the module that produces it.

## Structure

```
data/
├── benchmark/           # Benchmark runs (results, logs, recordings, task cache)
├── verification/        # Web verification pipeline reports
└── evaluation/          # Evaluator artifacts (GIFs, snapshots)
```

All subdirectories are created automatically by their respective modules at runtime.

## Cleanup

```bash
# Clean everything (safe - all data is regenerable)
rm -rf data/benchmark data/verification data/evaluation
```

Note: Benchmark output is also written to `../benchmark-output/` by the benchmark entrypoint (configurable via `BenchmarkConfig.base_dir`).
