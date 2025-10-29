from __future__ import annotations

"""
Train a real RL policy (MaskablePPO) on the demo websites via IWAWebEnv.

Requires:
  pip install sb3-contrib stable-baselines3 torch gymnasium
  playwright install

This script is code-configured: edit TrainCfg below and run directly.
"""

from dataclasses import dataclass
import os
import pprint

from loguru import logger
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback

from autoppia_iwa.src.rl.envs.iwa_env import IWAWebEnv
from autoppia_iwa.entrypoints.benchmark.task_generation import (
    get_projects_by_ids,
    generate_tasks_for_project,
)
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging


@dataclass(slots=True)
class TrainCfg:
    # Env
    topk: int = 12
    max_steps: int = 20
    # Skip first two demo websites; start from index 2
    project_start_index: int = 2
    tasks_cache_dir: str = "data/tasks_cache"
    use_cached_tasks: bool = True

    # PPO
    total_steps: int = 20_000
    n_steps: int = 1_024
    batch_size: int = 128
    n_epochs: int = 5
    gamma: float = 0.99
    gae_lambda: float = 0.95
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    lr_start: float = 3e-4
    lr_end: float = 1e-4
    ent_start: float = 0.03
    ent_end: float = 0.005
    clip_start: float = 0.2
    clip_end: float = 0.1

    # Logging / outputs
    tensorboard_log: str = "runs/tb"
    save_dir: str = "/data/rl_models"  # align with RL benchmark hardcoded path
    save_name: str = "ppo_real.zip"
    checkpoint_every: int = 10_000  # save every N steps


def make_env(cfg: TrainCfg):
    env = IWAWebEnv(
        {
            "topk": int(cfg.topk),
            "max_steps": int(cfg.max_steps),
            "project_start_index": int(cfg.project_start_index),
            "tasks_cache_dir": cfg.tasks_cache_dir,
            "use_cached_tasks": bool(cfg.use_cached_tasks),
            "goal_vocab_size": 4096,
            "dom_vocab_size": 8192,
            "url_vocab_size": 1024,
            "max_goal_tokens": 48,
            "max_dom_tokens": 200,
            "max_element_tokens": 12,
            "action_history": 10,
        }
    )

    def mask_fn(e):
        return e.get_action_mask()

    return ActionMasker(env, mask_fn)


def linear_schedule(v0: float, v1: float):
    def f(progress_remaining: float):
        return v1 + (v0 - v1) * progress_remaining

    return f


def ensure_dir(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except Exception as e:
        logger.warning(
            f"Failed to create {path}: {e}. Falling back to local ./data/rl_models")
        fallback = os.path.join("data", "rl_models")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def train(cfg: TrainCfg) -> str:
    # Resolve selected project like the benchmark and warm up cached tasks
    try:
        idx = max(0, min(len(demo_web_projects)
                  - 1, int(cfg.project_start_index)))
        selected_id = demo_web_projects[idx].id
        projects = get_projects_by_ids(demo_web_projects, [selected_id])
        project = projects[0]
        logger.info(f"Training on project: {project.name} (id={project.id})")

        import asyncio as _asyncio

        async def _warmup():
            tasks = await generate_tasks_for_project(
                project,
                use_cached=bool(cfg.use_cached_tasks),
                cache_dir=cfg.tasks_cache_dir,
                prompts_per_use_case=1,
                num_use_cases=1,
                use_cases=None,
                enable_dynamic_html=False,
            )
            logger.info(
                f"Task cache ready: {len(tasks)} task(s) in {cfg.tasks_cache_dir}")

        _asyncio.run(_warmup())
    except Exception as e:
        logger.warning(f"Could not warm up task cache: {e}")

    env = make_env(cfg)

    def _has_tensorboard() -> bool:
        try:
            import tensorboard as _tb  # noqa: F401
            return True
        except Exception:
            return False
    model = MaskablePPO(
        "MultiInputPolicy",
        env,
        verbose=1,
        learning_rate=linear_schedule(cfg.lr_start, cfg.lr_end),
        ent_coef=cfg.ent_start,
        clip_range=linear_schedule(cfg.clip_start, cfg.clip_end),
        n_steps=cfg.n_steps,
        batch_size=cfg.batch_size,
        n_epochs=cfg.n_epochs,
        gamma=cfg.gamma,
        gae_lambda=cfg.gae_lambda,
        vf_coef=cfg.vf_coef,
        max_grad_norm=cfg.max_grad_norm,
        tensorboard_log=(cfg.tensorboard_log if _has_tensorboard() else None),
    )

    # Periodic checkpoints
    ckpt_dir = ensure_dir(os.path.join(cfg.save_dir, "checkpoints"))
    checkpoint_cb = CheckpointCallback(
        save_freq=cfg.checkpoint_every, save_path=ckpt_dir, name_prefix="ppo_real")

    # Episode/step logger for quick visibility
    class TrainingLoggerCallback(BaseCallback):
        def __init__(self):
            super().__init__()
            self.ep_idx = 0
            self.ep_reward = 0.0
            self.ep_len = 0
            self.ep_invalids = 0
            # Hardcoded debugging: always pause on each step and episode and print summaries
            self.debug_pause = "both"  # values previously: none|step|episode|both
            self.debug_verbose = True   # pretty-print full info dict each step
            self.debug_summary = True   # print compact step/episode summaries

        def _print_step_summary(self, info: dict, reward: float, step_idx: int) -> None:
            try:
                mask = info.get("action_mask") or []
                mask_true = int(sum(bool(x)
                                for x in mask)) if mask is not None else 0
                # Last 5 entries correspond to macros in this env (TYPE_CONFIRM, SUBMIT, SCROLL_DOWN, SCROLL_UP, BACK)
                macros = list(
                    mask[-5:]) if mask is not None and len(mask) >= 5 else []
                enabled_macros = []
                names = ["type_confirm", "submit", "scroll_down",
                         "scroll_up", "back"][: len(macros)]
                for i, m in enumerate(macros):
                    if m:
                        enabled_macros.append(names[i])
                tp = int(info.get("tests_passed", 0))
                tt = int(info.get("total_tests", 0))
                print(
                    "[DBG] step summary: "
                    f"step={step_idx} idx={info.get('selected_action_index')} kind={info.get('selected_action_kind')} "
                    f"desc={info.get('action_desc')} invalid={bool(info.get('invalid_action', False))} "
                    f"r={reward:.3f} ep_r={self.ep_reward:.3f} tests={tp}/{tt} raw={float(info.get('raw_score', 0.0)):.3f} "
                    f"url={info.get('current_url', '')} events={info.get('backend_event_names', [])} "
                    f"mask_true={mask_true} macros_on={enabled_macros}"
                )
            except Exception:
                pass

        def _print_episode_summary(self, info: dict) -> None:
            try:
                tp = int(info.get("tests_passed", 0))
                tt = int(info.get("total_tests", 0))
                rs = float(info.get("raw_score", 0.0))
                succ = bool(tp > 0 and tp == tt) if tt else False
                print(
                    "[DBG] episode summary: "
                    f"ep={self.ep_idx} len={self.ep_len} ep_r={self.ep_reward:.3f} tests={tp}/{tt} raw={rs:.3f} "
                    f"success={succ} invalids={self.ep_invalids} url={info.get('current_url','')}"
                )
            except Exception:
                pass

        def _on_training_start(self) -> None:
            logger.info("Training started: logging per-episode summaries")

        def _on_step(self) -> bool:
            infos = self.locals.get("infos", [])
            rewards = self.locals.get("rewards", [])
            dones = self.locals.get("dones", [])
            # Single env assumptions
            r = float(rewards[0]) if rewards else 0.0
            self.ep_reward += r
            self.ep_len += 1
            if infos:
                info = infos[0] or {}
                if info.get("invalid_action"):
                    self.ep_invalids += 1
                # Step-level action trace
                desc = info.get("action_desc", "")
                raw = info.get("raw_score", 0.0)
                tp = int(info.get("tests_passed", 0))
                tt = int(info.get("total_tests", 0))
                url = info.get("current_url", "")
                evs = info.get("backend_event_names", []) or []
                evs_str = ",".join(evs[:3])
                logger.info(
                    f"[STEP {self.ep_len}] a={desc} raw={raw:.3f} tests={tp}/{tt} url={url} events=[{evs_str}] reward={r:.3f}")
                if self.debug_summary:
                    self._print_step_summary(info, r, self.ep_len)
                if self.debug_verbose:
                    print("[DBG] info:")
                    pprint.pprint(info, width=100)

            # Always allow pausing every step, even if infos is empty
            if self.debug_pause in ("step", "both"):
                try:
                    input("[DBG] Press Enter to continue (step)… ")
                except EOFError:
                    pass

            if dones and bool(dones[0]):
                tp = int(info.get("tests_passed", 0)) if infos else 0
                tt = int(info.get("total_tests", 0)) if infos else 0
                rs = float(info.get("raw_score", 0.0)) if infos else 0.0
                succ = bool(tp > 0 and tp == tt) if tt else False
                self.ep_idx += 1
                logger.info(
                    f"[EP {self.ep_idx}] len={self.ep_len} reward={self.ep_reward:.3f} tests={tp}/{tt} raw={rs:.3f} success={succ} invalids={self.ep_invalids}"
                )
                if self.debug_summary and infos:
                    self._print_episode_summary(infos[0] or {})
                if self.debug_verbose and infos:
                    print("[DBG] episode final info:")
                    pprint.pprint(infos[0] or {}, width=100)
                if self.debug_pause in ("episode", "both"):
                    try:
                        input("[DBG] Press Enter to continue (episode)… ")
                    except EOFError:
                        pass
                # reset counters
                self.ep_reward = 0.0
                self.ep_len = 0
                self.ep_invalids = 0
            return True

    out_path: str | None = None
    try:
        model.learn(total_timesteps=int(cfg.total_steps), callback=[
                    checkpoint_cb, TrainingLoggerCallback()])

        # Final save
        save_dir = ensure_dir(cfg.save_dir)
        out_path = os.path.join(save_dir, cfg.save_name)
        model.save(out_path)
        logger.info(f"Saved final model to: {out_path}")

        # Also save a copy to repo-local path for convenience
        try:
            local_dir = ensure_dir(os.path.join("data", "rl_models"))
            local_out = os.path.join(local_dir, cfg.save_name)
            model.save(local_out)
            logger.info(f"Saved local copy to: {local_out}")
        except Exception:
            pass

        return out_path
    finally:
        # Ensure all envs/processes are closed even on error/interrupt
        try:
            vec = getattr(model, "env", None)
            if vec is not None:
                try:
                    vec.close()
                except Exception as e:
                    logger.warning(f"VecEnv close failed: {e}")
        except Exception:
            pass
        try:
            env.close()
        except Exception as e:
            logger.warning(f"Env close failed: {e}")


def main():
    # Align logging with benchmark so EVALUATION/TEST logs look the same
    try:
        setup_logging("benchmark.log")
    except Exception:
        pass
    cfg = TrainCfg()
    logger.info(f"Starting training with config: {cfg}")
    try:
        out = train(cfg)
        print(f"Saved {out}")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
