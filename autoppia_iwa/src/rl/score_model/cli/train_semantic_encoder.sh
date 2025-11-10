#!/usr/bin/env bash
set -e
python -m autoppia_iwa.src.rl.score_model.cli.train_semantic_encoder --config autoppia_iwa/src/rl/score_model/configs/semantic_encoder.yaml
