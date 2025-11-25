from __future__ import annotations

from stable_baselines3.common.callbacks import BaseCallback


class EpisodeDiagnostics(BaseCallback):
    def __init__(self, verbose: int = 0):
        super().__init__(verbose)

    def _on_step(self) -> bool:  # type: ignore[override]
        infos = self.locals.get("infos", []) or []
        for info in infos:
            if "invalid_action" in info:
                self.logger.record("env/invalid_action", int(bool(info["invalid_action"])))
            if "success" in info:
                self.logger.record("env/success_flag", int(bool(info["success"])))
            if "milestones" in info:
                try:
                    self.logger.record("env/milestone_count", int(len(info["milestones"])))
                except Exception:  # pragma: no cover - best effort logging
                    pass
            if "rnd_intrinsic" in info:
                try:
                    self.logger.record("env/rnd_intrinsic", float(info["rnd_intrinsic"]))
                except Exception:  # pragma: no cover - best effort logging
                    pass
        return True


__all__ = ["EpisodeDiagnostics"]
