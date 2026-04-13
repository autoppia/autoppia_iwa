# Data Extraction Trajectories Testing

This guide explains how to run and validate data-extraction (DE) trajectories.

## Prerequisites

- Run commands from repo root: `AUTOPPIA/Autoppia_repos/autoppia_iwa`
- Virtualenv exists at `.venv`
- Demo backend/frontend services are running if you test replay trajectories

## Main Runner

Use:

```bash
.venv/bin/python scripts/debug_data_extraction_trajectories.py ...
```

Environment variables (provider/API key) must already be available in your shell.

## DE Modes

The runner supports two DE trajectory modes:

- `replay`: trajectory has `actions` and replays browser steps (needs running demo web)
- `dataset_only`: trajectory has `actions=None` and validates `expected_answer` directly against dataset of the trajectory seed

Most projects now use `dataset_only`.
`autodiscord` remains `replay` fallback because its seed dataset API is not available in the local backend.

## Run By Project

Runs all DE trajectories in the project:

```bash
.venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema
```

## Run By Project + Use Case

Runs only DE trajectories for the requested use case(s):

```bash
.venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema -u FILM_DETAIL
```

Multiple use cases:

```bash
.venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema -u FILM_DETAIL -u SEARCH_FILM
```

`--use-case` matching is case-insensitive.

## Run By Project + Trajectory ID

Runs one concrete trajectory:

```bash
.venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema -t <trajectory_id>
```

`id` is now auto-generated for DE trajectories.

You can combine `-t` and `-u`; filters are applied together.

## Exit Codes

- `0`: all selected trajectories succeeded
- `1`: at least one selected trajectory failed, or filters/project are invalid

## Quick Registry Test

Validates DE registry and payload shape:

```bash
.venv/bin/pytest tests/integration/test_data_extraction_trajectories.py -q
```
