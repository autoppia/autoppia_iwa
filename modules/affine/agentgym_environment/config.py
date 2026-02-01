from __future__ import annotations

import os

from pydantic import BaseModel, Field, validator

try:
    from autoppia_iwa.src.demo_webs.config import demo_web_projects
except ModuleNotFoundError:  # pragma: no cover - source-tree fallback
    from autoppia_iwa.autoppia_iwa.src.demo_webs.config import demo_web_projects


def _default_project_ids() -> list[str]:
    return [project.id for project in demo_web_projects[:3]]


class AffineEnvConfig(BaseModel):
    """Configuration for the Affine-ready AgentGym environment."""

    project_ids: list[str] = Field(default_factory=_default_project_ids, description="Demo web project ids to expose via AgentGym.")
    prompts_per_use_case: int = Field(default=2, gt=0, description="Number of task prompts to generate per use case.")
    enable_dynamic_html: bool = Field(default=False, description="Mirror benchmark setting for deterministic seeds.")

    agent_request_timeout: float = Field(default=180.0, gt=0, description="Timeout applied to miner `/solve_task` calls.")
    browser_timeout: float = Field(default=120.0, gt=0, description="Playwright browser timeout for each evaluation.")
    max_tasks_per_eval: int = Field(default=3, gt=0, description="Maximum number of tasks to run per /evaluate request when ids are omitted.")
    should_record_gif: bool = Field(default=False, description="Whether to request GIF captures from the evaluator.")
    verbose_logging: bool = Field(default=False, description="Enable verbose evaluation logs.")

    dataset_seed: int | None = Field(default=None, description="Optional RNG seed for reproducible task-id sampling.")

    model_config = {"validate_assignment": True}

    @validator("project_ids", pre=True)
    def _strip_project_ids(cls, value: list[str]) -> list[str]:
        cleaned = [pid.strip() for pid in value or [] if pid]
        return cleaned or _default_project_ids()

    @classmethod
    def load_from_env(cls) -> AffineEnvConfig:
        """Build config from environment variables."""

        raw_ids = os.getenv("IWA_AFFINE_PROJECT_IDS")
        project_ids = raw_ids.split(",") if raw_ids else _default_project_ids()

        return cls(
            project_ids=project_ids,
            prompts_per_use_case=int(os.getenv("IWA_AFFINE_PROMPTS_PER_USE_CASE", "2")),
            enable_dynamic_html=os.getenv("IWA_AFFINE_ENABLE_DYNAMIC_HTML", "false").lower() in {"1", "true", "yes"},
            agent_request_timeout=float(os.getenv("IWA_AFFINE_AGENT_TIMEOUT", "180")),
            browser_timeout=float(os.getenv("IWA_AFFINE_BROWSER_TIMEOUT", "120")),
            max_tasks_per_eval=int(os.getenv("IWA_AFFINE_MAX_TASKS_PER_EVAL", "3")),
            should_record_gif=os.getenv("IWA_AFFINE_RECORD_GIF", "false").lower() in {"1", "true", "yes"},
            verbose_logging=os.getenv("IWA_AFFINE_VERBOSE_LOGS", "false").lower() in {"1", "true", "yes"},
            dataset_seed=int(os.getenv("IWA_AFFINE_DATASET_SEED")) if os.getenv("IWA_AFFINE_DATASET_SEED") else None,
        )

    def clamp_requested_tasks(self, requested: int | None) -> int:
        """Limit requested task count to the configured maximum."""

        if not requested or requested <= 0:
            return self.max_tasks_per_eval
        return min(requested, self.max_tasks_per_eval)
