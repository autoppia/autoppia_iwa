from __future__ import annotations

"""
Tiny FastAPI service exposing `/evaluate` for Affine validators.

Flow per request:
- Pick a deterministic task (cached JSON or generated on startup).
- Call the remote agent at `base_url/solve_task` (OpenAI-style) via ApifiedOneShotWebAgent.
- Evaluate the returned actions with ConcurrentEvaluator against remote demo webs.
- Respond with `{score, success, error, extra}`.
"""

import asyncio
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from autoppia_iwa.entrypoints.benchmark.utils.task_generation import generate_tasks_for_project
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent


class EvaluateRequest(BaseModel):
    model: str = Field(..., description="Model identifier (HF repo or friendly name)")
    base_url: HttpUrl = Field(..., description="Base URL for the model service (e.g. https://foo.chutes.ai/v1)")
    task_id: int | None = Field(None, description="Optional task index for deterministic selection")
    temperature: float | None = Field(0.7, ge=0, le=2, description="Sampling temperature forwarded to the model")
    timeout: int | None = Field(600, gt=0, description="Overall timeout in seconds for solving")
    seed: int | None = Field(None, description="Optional seed propagated to the agent")


class EvaluateResponse(BaseModel):
    score: float
    success: bool
    error: str | None = None
    extra: dict[str, object] = Field(default_factory=dict)


class _TaskStore:
    """
    Lazy task cache shared across requests.
    """

    def __init__(self) -> None:
        self._tasks: list[tuple[Task, WebProject]] = []
        self._lock = asyncio.Lock()

    @staticmethod
    def _wanted_project_ids() -> list[str]:
        raw = os.getenv("AFFINE_PROJECT_IDS", "")
        ids = [s.strip().lower() for s in raw.split(",") if s.strip()]
        return ids

    @staticmethod
    @lru_cache(maxsize=1)
    def _projects_by_id() -> dict[str, WebProject]:
        return {str(p.id).lower(): p for p in demo_web_projects}

    async def _generate_for_project(self, project: WebProject) -> list[Task]:
        default_cache = Path(__file__).resolve().parents[1] / "data" / "affine" / "tasks"
        cache_dir = os.getenv("AFFINE_TASK_CACHE_DIR", str(default_cache))
        use_cached = bool(int(os.getenv("AFFINE_USE_CACHED_TASKS", "1")))
        prompts_per_use_case = int(os.getenv("AFFINE_PROMPTS_PER_USE_CASE", "1"))
        # Removed num_use_cases: use use_cases=None to get all use cases
        enable_dynamic_html = bool(int(os.getenv("AFFINE_ENABLE_DYNAMIC_HTML", "0")))

        tasks = await generate_tasks_for_project(
            project,
            use_cached=use_cached,
            cache_dir=cache_dir,
            prompts_per_use_case=prompts_per_use_case,
            use_cases=None,
            enable_dynamic_html=enable_dynamic_html,
        )
        if tasks:
            return tasks
        raise RuntimeError(f"No tasks available for project {project.id}. Ensure cache exists under {cache_dir}.")

    async def ensure_tasks(self) -> None:
        if self._tasks:
            return
        async with self._lock:
            if self._tasks:
                return

            wanted_ids = self._wanted_project_ids()
            projects = [self._projects_by_id()[pid] for pid in wanted_ids if pid in self._projects_by_id()] if wanted_ids else list(demo_web_projects)
            tasks: list[tuple[Task, WebProject]] = []
            for project in projects:
                project_tasks = await self._generate_for_project(project)
                for t in project_tasks:
                    tasks.append((t, project))

            if not tasks:
                raise RuntimeError("No tasks available. Check task generation or cache settings.")

            self._tasks = tasks

    def get(self, idx: int | None) -> tuple[Task, WebProject, int]:
        if not self._tasks:
            raise RuntimeError("Task store not initialized")
        if idx is None:
            idx = 0
        safe_idx = idx % len(self._tasks)
        task, project = self._tasks[safe_idx]
        return task, project, safe_idx


app = FastAPI(title="Affine /evaluate for Autoppia IWA", version="0.1.0")
task_store = _TaskStore()


@app.on_event("startup")
async def _startup() -> None:
    await task_store.ensure_tasks()


@app.get("/healthz", responses={500: {"description": "Internal server error during health check"}})
async def health() -> dict:
    try:
        await task_store.ensure_tasks()
        return {"status": "ok", "tasks": len(task_store._tasks)}
    except Exception as exc:  # pragma: no cover - best effort
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/evaluate", responses={503: {"description": "Task loading failed"}})
async def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    try:
        await task_store.ensure_tasks()
        task, project, resolved_idx = task_store.get(req.task_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Task loading failed: {exc}") from exc

    agent = ApifiedOneShotWebAgent(base_url=str(req.base_url), timeout=req.timeout or 600)

    try:
        task_solution = await agent.solve_task(task)
    except Exception as exc:
        return EvaluateResponse(score=0.0, success=False, error=f"solve_task failed: {exc}", extra={"task_index": resolved_idx})

    cfg = EvaluatorConfig(
        should_record_gif=False,
        verbose_logging=False,
        debug_mode=False,
        browser_timeout=float(req.timeout or 600) * 1000,  # playwright expects ms
    )

    evaluator = ConcurrentEvaluator(web_project=project, config=cfg)

    try:
        result = await evaluator.evaluate_single_task_solution(task, task_solution)
        score = float(result.final_score or result.raw_score or 0.0)
        success = bool(result.stats and not result.stats.had_errors and score > 0.0)
        error = result.stats.error_message if result.stats and result.stats.had_errors else None
        extra = {
            "task_index": resolved_idx,
            "task_id": task.id,
            "web_project_id": project.id,
            "raw_score": result.raw_score,
            "final_score": result.final_score,
            "tests_passed": getattr(result.stats, "tests_passed", None),
            "tests_total": getattr(result.stats, "total_tests", None),
        }
        return EvaluateResponse(score=score, success=success, error=error, extra=extra)
    except Exception as exc:
        return EvaluateResponse(score=0.0, success=False, error=f"evaluation failed: {exc}", extra={"task_index": resolved_idx})


def run() -> None:
    """CLI entrypoint: python -m autoppia_iwa.affine_service.server"""
    import uvicorn

    uvicorn.run(
        "autoppia_iwa.affine_service.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":  # pragma: no cover
    run()
