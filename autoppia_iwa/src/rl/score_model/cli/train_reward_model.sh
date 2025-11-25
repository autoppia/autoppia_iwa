#!/usr/bin/env bash
set -e
python -m autoppia_iwa.src.rl.score_model.cli.train_reward_model --config autoppia_iwa/src/rl/score_model/configs/rm_train.yaml
