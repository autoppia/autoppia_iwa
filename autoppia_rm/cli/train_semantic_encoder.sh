#!/usr/bin/env bash
set -e
python -m autoppia_rm.cli.train_semantic_encoder --config autoppia_rm/configs/semantic_encoder.yaml
