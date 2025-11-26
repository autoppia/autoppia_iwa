#!/usr/bin/env python3
"""
Train PPO agent using Score Model as reward function, with optional BC warm-start.

This script:
1. Optionally pre-trains the policy using Behavior Cloning (BC) on expert trajectories
2. Trains a PPO agent using the trained Score Model for reward shaping
3. Saves checkpoints periodically during training
4. Logs metrics to TensorBoard

Usage:
    python -m autoppia_iwa.src.rl.agent.entrypoints.train_ppo_with_score_model \
        --config autoppia_iwa/src/rl/agent/configs/ppo_with_score_model.yaml

The config should specify:
    - env.reward_model_path: Path to trained score model checkpoint
    - bc.enabled: Whether to warm-start with BC
    - bc.trajectory_source: Path/URL to expert trajectories
    - train: PPO hyperparameters
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback, EvalCallback
    from stable_baselines3.common.monitor import Monitor
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError("stable-baselines3 required for PPO training. Install requirements-rl.txt (pip install stable-baselines3).") from exc

from autoppia_iwa.src.rl.agent.envs.iwa_env import IWAWebEnv
from autoppia_iwa.src.rl.agent.offline.bc_trainer import BehaviorCloningConfig, BehaviorCloningTrainer
from autoppia_iwa.src.rl.agent.offline.http_provider import HttpTrajectoryProvider


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="YAML config file for training",
    )
    parser.add_argument(
        "--skip-bc",
        action="store_true",
        help="Skip BC warm-start even if enabled in config",
    )
    parser.add_argument(
        "--tensorboard-log",
        type=str,
        default="data/rl/tensorboard",
        help="TensorBoard log directory",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML configuration file."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_env(env_cfg: dict[str, Any]) -> IWAWebEnv:
    """Build the IWA environment with score model reward shaping."""
    logger.info("Building IWA environment with Score Model reward shaping")

    # Validate reward model path
    reward_model_path = env_cfg.get("reward_model_path")
    if not reward_model_path:
        raise ValueError("env.reward_model_path must be specified in config")

    if not Path(reward_model_path).exists():
        raise FileNotFoundError(f"Score model not found: {reward_model_path}")

    logger.info(f"Using score model: {reward_model_path}")

    env = IWAWebEnv(env_cfg)
    env = Monitor(env)  # Wrap for logging
    return env


def run_bc_warmstart(
    policy: MaskableActorCriticPolicy,
    bc_cfg: dict[str, Any],
) -> None:
    """Pre-train policy using Behavior Cloning on expert trajectories."""
    logger.info("=" * 60)
    logger.info("BEHAVIOR CLONING WARM-START")
    logger.info("=" * 60)

    # Parse BC config
    trajectory_source = bc_cfg.get("trajectory_source")
    if not trajectory_source:
        raise ValueError("bc.trajectory_source must be specified when BC is enabled")

    # Determine if HTTP or local file
    if trajectory_source.startswith("http://") or trajectory_source.startswith("https://"):
        logger.info(f"Fetching trajectories from HTTP: {trajectory_source}")
        provider = HttpTrajectoryProvider(
            base_url=trajectory_source,
            timeout=bc_cfg.get("timeout", 60.0),
        )
    else:
        # For local files, we'd need a FileTrajectoryProvider (not implemented here)
        raise NotImplementedError(f"Local file trajectory provider not implemented. Use HTTP endpoint. Got: {trajectory_source}")

    # Build BC trainer config
    trainer_cfg = BehaviorCloningConfig(
        batch_size=bc_cfg.get("batch_size", 128),
        epochs=bc_cfg.get("epochs", 5),
        learning_rate=bc_cfg.get("learning_rate", 3e-4),
        grad_clip=bc_cfg.get("grad_clip", 0.5),
        validation_split=bc_cfg.get("validation_split", 0.1),
        max_trajectories=bc_cfg.get("max_trajectories"),
        max_steps=bc_cfg.get("max_steps"),
        shuffle=bc_cfg.get("shuffle", True),
        seed=bc_cfg.get("seed", 1337),
        num_workers=bc_cfg.get("num_workers", 0),
        log_interval=bc_cfg.get("log_interval", 20),
    )

    # Run BC training
    trainer = BehaviorCloningTrainer(policy, trainer_cfg)
    history = trainer.fit(provider)

    logger.info("=" * 60)
    logger.info("BC WARM-START COMPLETE")
    logger.info(f"  Train Loss: {history['train_loss']:.4f}")
    logger.info(f"  Train Acc:  {history['train_acc']:.4f}")
    logger.info(f"  Val Loss:   {history.get('val_loss', float('nan')):.4f}")
    logger.info(f"  Val Acc:    {history.get('val_acc', float('nan')):.4f}")
    logger.info(f"  Steps:      {int(history['num_steps'])}")
    logger.info("=" * 60)


def setup_callbacks(
    train_cfg: dict[str, Any],
    checkpoint_dir: Path,
    eval_env: IWAWebEnv | None = None,
) -> CallbackList:
    """Setup training callbacks for checkpointing and evaluation."""
    callbacks = []

    # Checkpoint callback
    checkpoint_freq = train_cfg.get("checkpoint_freq", 10000)
    checkpoint_callback = CheckpointCallback(
        save_freq=checkpoint_freq,
        save_path=str(checkpoint_dir),
        name_prefix="ppo_checkpoint",
        save_replay_buffer=False,
        save_vecnormalize=False,
    )
    callbacks.append(checkpoint_callback)
    logger.info(f"Checkpointing every {checkpoint_freq} steps to {checkpoint_dir}")

    # Evaluation callback (optional)
    if eval_env is not None and train_cfg.get("eval_freq", 0) > 0:
        eval_freq = train_cfg["eval_freq"]
        n_eval_episodes = train_cfg.get("n_eval_episodes", 5)
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=str(checkpoint_dir / "best"),
            log_path=str(checkpoint_dir / "eval"),
            eval_freq=eval_freq,
            n_eval_episodes=n_eval_episodes,
            deterministic=True,
            render=False,
        )
        callbacks.append(eval_callback)
        logger.info(f"Evaluating every {eval_freq} steps ({n_eval_episodes} episodes)")

    return CallbackList(callbacks)


def train_ppo(
    args: argparse.Namespace,
    cfg: dict[str, Any],
) -> MaskablePPO:
    """Main PPO training loop with score model and optional BC."""

    # Parse config sections
    env_cfg = cfg.get("env", {})
    bc_cfg = cfg.get("bc", {})
    train_cfg = cfg.get("train", {})

    # Build environment
    env = build_env(env_cfg)

    # Initialize PPO model
    logger.info("=" * 60)
    logger.info("INITIALIZING PPO MODEL")
    logger.info("=" * 60)

    policy = train_cfg.get("policy", "MlpPolicy")
    policy_kwargs = train_cfg.get("policy_kwargs", {})

    model = PPO(
        policy,
        env,
        learning_rate=float(train_cfg.get("learning_rate", 3e-4)),
        n_steps=int(train_cfg.get("n_steps", 2048)),
        batch_size=int(train_cfg.get("batch_size", 64)),
        n_epochs=int(train_cfg.get("n_epochs", 10)),
        gamma=float(train_cfg.get("gamma", 0.99)),
        gae_lambda=float(train_cfg.get("gae_lambda", 0.95)),
        clip_range=float(train_cfg.get("clip_range", 0.2)),
        ent_coef=float(train_cfg.get("ent_coef", 0.0)),
        vf_coef=float(train_cfg.get("vf_coef", 0.5)),
        max_grad_norm=float(train_cfg.get("max_grad_norm", 0.5)),
        policy_kwargs=policy_kwargs,
        tensorboard_log=args.tensorboard_log,
        verbose=int(train_cfg.get("verbose", 1)),
    )

    logger.info(f"Policy: {policy}")
    logger.info(f"Learning rate: {model.learning_rate}")
    logger.info(f"Batch size: {model.batch_size}")
    logger.info(f"Gamma: {model.gamma}")

    # Optional: BC warm-start
    if bc_cfg.get("enabled", False) and not args.skip_bc:
        try:
            run_bc_warmstart(model.policy, bc_cfg)
        except Exception as e:
            logger.error(f"BC warm-start failed: {e}")
            if bc_cfg.get("required", False):
                raise
            logger.warning("Continuing without BC warm-start")
    elif bc_cfg.get("enabled", False) and args.skip_bc:
        logger.info("BC warm-start skipped (--skip-bc flag)")

    # Setup callbacks
    checkpoint_dir = Path(train_cfg.get("checkpoint_path", "data/rl/checkpoints/ppo"))
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Optional: Create eval environment
    eval_env = None
    if train_cfg.get("eval_freq", 0) > 0:
        eval_env = build_env(env_cfg)

    callbacks = setup_callbacks(train_cfg, checkpoint_dir, eval_env)

    # Train PPO
    logger.info("=" * 60)
    logger.info("STARTING PPO TRAINING")
    logger.info("=" * 60)

    total_timesteps = int(train_cfg.get("total_timesteps", 100000))
    logger.info(f"Total timesteps: {total_timesteps}")

    model.learn(
        total_timesteps=total_timesteps,
        callback=callbacks,
        progress_bar=True,
    )

    # Save final model
    final_path = checkpoint_dir / "ppo_final"
    model.save(str(final_path))
    logger.info(f"Final model saved to {final_path}")

    # Cleanup
    env.close()
    if eval_env is not None:
        eval_env.close()

    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)

    return model


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    logger.info(f"Config loaded from: {args.config}")
    logger.info(f"TensorBoard logs: {args.tensorboard_log}")

    train_ppo(args, cfg)

    logger.info("Training finished successfully!")


if __name__ == "__main__":
    main()
