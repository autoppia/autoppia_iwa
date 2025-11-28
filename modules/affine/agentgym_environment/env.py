from __future__ import annotations

from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl

from .agent_client import RemoteAgentClient
from .config import AffineEnvConfig
from .dataset import AffineTaskDataset
from .evaluator import EvaluationRunner, TaskEvaluationDetail

app = FastAPI(title="Autoppia IWA AgentGym Environment", version="0.1.0")

CONFIG = AffineEnvConfig.load_from_env()
DATASET = AffineTaskDataset(CONFIG)
RUNNER = EvaluationRunner(CONFIG)


class EvaluateRequest(BaseModel):
    model: str = Field(..., description="Miner model identifier (HF repo, metadata, etc.)")
    base_url: HttpUrl = Field(..., description="Base URL of the miner's /solve_task API (Chutes endpoint).")
    temperature: float = Field(0.0, description="Unused; present for AgentGym compatibility.")
    timeout: float | None = Field(None, description="Override the default request timeout (seconds).")
    ids: list[int] | None = Field(None, description="Specific task ids to evaluate. Defaults to random sampling.")
    max_tasks: int | None = Field(None, description="Limit number of tasks when ids are omitted.")
    max_round: int | None = Field(None, description="Unused placeholder to mimic AgentGym API.")


class EvaluateResponse(BaseModel):
    environment: str = "autoppia_iwa_agentgym"
    total_score: float
    success_rate: float
    evaluated: int
    dataset_size: int
    project_ids: list[str]
    details: list[TaskEvaluationDetail]


@app.on_event("startup")
async def _startup_event() -> None:
    logger.info("Booting Autoppia ↔ Affine environment...")
    await DATASET.initialize()
    logger.info("Dataset ready with %d tasks.", DATASET.size)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "tasks": str(DATASET.size)}


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    if DATASET.size == 0:
        raise HTTPException(status_code=503, detail="Dataset not initialized yet.")

    clamp = CONFIG.clamp_requested_tasks(request.max_tasks)
    try:
        task_ids = DATASET.normalize_ids(request.ids, clamp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    entries = DATASET.get_entries(task_ids)
    timeout = request.timeout or CONFIG.agent_request_timeout
    client = RemoteAgentClient(base_url=str(request.base_url), timeout=timeout, web_agent_name=request.model)

    details = await RUNNER.evaluate_tasks(entries, client)

    total_score = sum(detail.score for detail in details)
    success_rate = sum(1 for detail in details if detail.success) / len(details) if details else 0.0

    return EvaluateResponse(
        total_score=total_score,
        success_rate=success_rate,
        evaluated=len(details),
        dataset_size=DATASET.size,
        project_ids=CONFIG.project_ids,
        details=details,
    )
