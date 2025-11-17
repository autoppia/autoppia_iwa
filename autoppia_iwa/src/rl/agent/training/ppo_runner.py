from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

import yaml
import gymnasium as gym
try:  # pragma: no cover - optional dependency for RL training
    from sb3_contrib import MaskablePPO
    from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "sb3-contrib is required for PPO training. Install requirements-rl.txt (pip install sb3-contrib)."
    ) from exc

# In sb3-contrib 2.x, MaskableEnv is just a type hint for gymnasium.Env
MaskableEnv = gym.Env

from autoppia_iwa.src.rl.agent.envs.iwa_env import IWAWebEnv


def build_env(env_cfg: Dict[str, Any] | None = None) -> MaskableEnv:
    """Instantiate the wrapped IWA environment ready for MaskablePPO."""

    base_env = IWAWebEnv(env_cfg or {})
    return MaskableEnv(base_env)


def train_agent(cfg: Dict[str, Any]) -> MaskablePPO:
    """Train MaskablePPO according to the provided config dictionary."""

    env_cfg = cfg.get("env", {})
    train_cfg = cfg.get("train", {})

    env = build_env(env_cfg)
    policy = train_cfg.get("policy", "MlpPolicy")
    # Ensure policy class resolves correctly
    if isinstance(policy, str) and policy != "MlpPolicy":
        policy_class: type[MaskableActorCriticPolicy] | str = policy
    else:
        policy_class = "MlpPolicy"

    model = MaskablePPO(
        policy_class,
        env,
        learning_rate=float(train_cfg.get("learning_rate", 3e-4)),
        n_steps=int(train_cfg.get("n_steps", 64)),
        batch_size=int(train_cfg.get("batch_size", 32)),
        gamma=float(train_cfg.get("gamma", 0.99)),
        verbose=int(train_cfg.get("verbose", 1)),
    )

    total_timesteps = int(train_cfg.get("total_timesteps", 1024))
    checkpoint_path = train_cfg.get("checkpoint_path")
    start = time.time()
    model.learn(total_timesteps=total_timesteps)
    duration = time.time() - start
    if checkpoint_path:
        ckpt = Path(checkpoint_path)
        ckpt.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(ckpt))
    env.close()
    print(f"[train_agent] finished {total_timesteps} steps in {duration:.1f}s")
    return model


def run_episode(model_path: str | Path, env_cfg: Dict[str, Any] | None = None, deterministic: bool = True) -> dict[str, Any]:
    """Roll out a single episode with a trained model and return trajectory stats."""

    env = build_env(env_cfg or {})
    model = MaskablePPO.load(model_path, env=env)
    obs, info = env.reset()
    done = False
    truncated = False
    rewards: list[float] = []
    actions: list[int] = []
    step = 0
    while not (done or truncated):
        mask = env.env.get_action_mask() if hasattr(env.env, "get_action_mask") else None
        action, _ = model.predict(obs, action_masks=mask, deterministic=deterministic)
        obs, reward, done, truncated, info = env.step(action)
        rewards.append(float(reward))
        actions.append(int(action))
        step += 1
        if info.get("selected_action_kind"):
            print(f"[run_episode] step={step} action={info['action_desc']} reward={reward:.4f}")

    env.close()
    return {
        "steps": step,
        "episode_return": sum(rewards),
        "actions": actions,
        "success": bool(info.get("raw_score", 0) >= 1.0 or info.get("shaped_reward") == 1.0),
    }


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
