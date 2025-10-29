#!/usr/bin/env bash
set -e
python -m autoppia_rm.cli.train_reward_model --config autoppia_rm/configs/rm_train.yaml
