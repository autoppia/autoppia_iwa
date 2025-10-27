from __future__ import annotations

import json
from typing import Any, ClassVar

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.rl.actions import guard_safe, to_action
from autoppia_iwa.src.rl.rewards.base import RewardFn
from autoppia_iwa.src.rl.utils import b64jpeg_to_np


class AsyncWebAgentEnv(gym.Env):
    """
    Entorno asíncrono para web RL.
    Obs:
      - image (H,W,3), html (opcional), url, task_prompt, step, history (JSON compacto)
    Acciones: dict/JSON compatibles con tus BaseAction.*Action
    """

    metadata: ClassVar[dict[str, object]] = {
        "render_modes": ["rgb_array"],
        "render_fps": 5,
    }

    def __init__(
        self,
        *,
        executor: PlaywrightBrowserExecutor,
        task_sampler,
        reward_fn: RewardFn,
        reset_fn=None,  # async def(executor, task)
        H: int = 320,
        W: int = 320,
        include_html: bool = True,
        max_steps: int = 50,
        action_mode: str = "json",  # "json" | "dict"
        safe_action_types: list[str] | None = None,
        obs_builder=None,  # async def(executor, task, H, W, step, task_prompt)->obs
        history_k: int = 5,
        disallowed_penalty: float = 0.02,  # penalización por acción no permitida
    ):
        super().__init__()
        self.executor = executor
        self.task_sampler = task_sampler
        self.reward_fn = reward_fn
        self.reset_fn = reset_fn
        self.obs_builder = obs_builder

        self.H, self.W = H, W
        self.include_html = include_html
        self.max_steps = max_steps
        self.action_mode = action_mode
        self.history_k = history_k
        self.disallowed_penalty = float(disallowed_penalty)

        self.safe = set(safe_action_types or ["NavigateAction", "ClickAction", "TypeAction", "ScrollAction", "SubmitAction", "WaitAction", "HoverAction"])

        self.observation_space = spaces.Dict(
            {
                "image": spaces.Box(0, 255, shape=(H, W, 3), dtype=np.uint8),
                "url": spaces.Text(max_length=2048),
                "html": spaces.Text(max_length=500_000) if include_html else spaces.Text(max_length=1),
                "task_prompt": spaces.Text(max_length=4096),
                "step": spaces.Box(low=0, high=max_steps, shape=(), dtype=np.int32),
                "history": spaces.Text(max_length=20000) if history_k > 0 else spaces.Text(max_length=1),
            }
        )
        self.action_space = spaces.Text(max_length=16384) if action_mode == "json" else spaces.Dict({"type": spaces.Text(max_length=64)})

        self._task = None
        self._task_prompt = ""
        self._steps = 0
        self._traj: list[dict[str, Any]] = []
        self._last_obs: dict[str, Any] | None = None

    # ---------------- Helpers ----------------
    def _extract_task_prompt(self, task: Any, options: dict[str, Any] | None) -> str:
        if options and "prompt" in options:
            return str(options["prompt"])
        if hasattr(task, "prompt") and task.prompt:
            return str(task.prompt)
        if hasattr(task, "title") and task.title:
            return str(task.title)
        return ""

    def _compact_history(self) -> str:
        if self.history_k <= 0 or not self._traj:
            return ""
        tail = self._traj[-self.history_k :]
        lite = []
        for t in tail:
            a_raw = (t.get("action") or {}).get("raw") or {}
            a_type = a_raw.get("type") or a_raw.get("action", {}).get("type") or ""
            lite.append(
                {
                    "step": t.get("step"),
                    "url": t.get("obs_meta", {}).get("url", ""),
                    "action_type": a_type,
                    "reward": t.get("reward", 0.0),
                }
            )
        return json.dumps(lite, separators=(",", ":"), ensure_ascii=False)

    async def _default_obs(self) -> dict[str, Any]:
        snap = await self.executor._capture_snapshot()
        img = b64jpeg_to_np(snap.get("screenshot", ""), self.W, self.H)
        url = snap.get("url", "")
        html = snap.get("html", "") if self.include_html else ""
        return {
            "image": img,
            "url": url,
            "html": html,
            "task_prompt": self._task_prompt,
            "step": np.int32(self._steps),
            "history": self._compact_history(),
        }

    async def _obs(self) -> dict[str, Any]:
        if self.obs_builder:
            obs = await self.obs_builder(self.executor, self._task, self.H, self.W, self._steps, self._task_prompt)
            obs.setdefault("task_prompt", self._task_prompt)
            obs.setdefault("step", np.int32(self._steps))
            if self.history_k > 0 and "history" not in obs:
                obs["history"] = self._compact_history()
            return obs
        return await self._default_obs()

    def _coerce(self, a: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(a, str):
            return json.loads(a)
        if not isinstance(a, dict):
            raise ValueError("Action must be dict or JSON str.")
        return a

    # ---------------- API ----------------
    async def areset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        self._steps, self._traj = 0, []
        self._task = (options or {}).get("task") or self.task_sampler()
        self._task_prompt = self._extract_task_prompt(self._task, options)
        if hasattr(self.reward_fn, "reset"):
            self.reward_fn.reset()  # type: ignore[attr-defined]

        if callable(self.reset_fn):
            maybe = self.reset_fn(self.executor, self._task)
            if hasattr(maybe, "__await__"):
                await maybe

        obs = await self._obs()
        self._last_obs = obs
        self._traj.append({"step": 0, "obs_meta": {"url": obs["url"]}, "action": None, "reward": 0.0})
        return obs, {"step": 0, "url": obs["url"]}

    async def astep(self, action_in: str | dict[str, Any]):
        if self._task is None:
            raise RuntimeError("Call areset() first.")
        self._steps += 1

        raw = self._coerce(action_in)

        # ---- Guard safe-list (robusto: no crashea si no permitido) ----
        disallowed_type: str | None = None
        try:
            guard_safe(raw, list(self.safe))
            allowed = True
        except Exception as e:
            allowed = False
            # Detecta tipo para registrar
            t = raw.get("type") or raw.get("action", {}).get("type")
            disallowed_type = str(t) if t else "UnknownAction"
            str(e)

        err, result, action_obj = None, None, None

        if allowed:
            # Continuar con ejecución normal
            try:
                action_obj = to_action(raw)
                result = await self.executor.execute_single_action(action=action_obj, web_agent_id="env", iteration=self._steps, is_web_real=False)
            except Exception as e:
                err = str(e)

            # Construye obs y recompensa normal
            obs = await self._obs()
            try:
                reward, done, extra = await self.reward_fn(
                    task=self._task, step_idx=self._steps, last_action_dict=raw, last_action_obj=action_obj, executor=self.executor, trajectory=self._traj, obs=obs, result=result
                )
            except Exception as e:
                reward, done, extra = -0.01, False, {"reward_fn_error": str(e)}

            truncated = self._steps >= self.max_steps and not done
            info = {"step": self._steps, "url": obs["url"], **(extra or {})}

            if err:
                reward -= 0.02
                info["action_error"] = err
            if done:
                reward += 1.0
            if truncated and not done:
                reward -= 0.1

        else:
            # Acción no permitida: no ejecutar, penalización suave y seguir
            obs = await self._obs()
            try:
                # Aun así llamamos reward_fn para mantener consistencia de scoring
                reward, done, extra = await self.reward_fn(
                    task=self._task, step_idx=self._steps, last_action_dict=raw, last_action_obj=None, executor=self.executor, trajectory=self._traj, obs=obs, result=None
                )
            except Exception as e:
                reward, done, extra = 0.0, False, {"reward_fn_error": str(e)}

            # Penalización por deshabilitada
            reward -= self.disallowed_penalty
            truncated = self._steps >= self.max_steps and not done
            info = {"step": self._steps, "url": obs["url"], **(extra or {})}
            info["disallowed_action_type"] = disallowed_type
            info["safe_action_types"] = sorted(list(self.safe))
            # No bonus/penalty por done/trunc más allá de lo normal
            if done:
                reward += 1.0
            if truncated and not done:
                reward -= 0.1

        # Trayectoria
        self._traj.append(
            {
                "step": self._steps,
                "obs_meta": {"url": obs["url"]},
                "action": {"raw": raw, "built": (action_obj.model_dump() if action_obj else None)},
                "reward": float(reward),
            }
        )
        self._last_obs = obs
        return obs, float(reward), bool(done), bool(truncated), info

    def render(self):
        return None if self._last_obs is None else self._last_obs["image"]
