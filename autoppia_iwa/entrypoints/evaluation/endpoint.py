"""
Evaluation Endpoint Service

This endpoint allows agents to quickly check if their current solution would pass the task tests.
This is useful for agents to validate their work on-the-fly before timeout (120s) since they
typically take ~10-20s per response.

Usage:
    python -m autoppia_iwa.entrypoints.evaluation.endpoint

The service will start on port 5060 by default and expose:
    POST /evaluate - Evaluate a task solution
    GET /health - Health check
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Any, ClassVar

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import AnyUrl, BaseModel, Field, NonNegativeFloat, constr

from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.classes import TaskSolution

# =====================
# Constants / Settings
# =====================
DEFAULT_PORT: int = 5060
DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_TIMEOUT_SECONDS: float = float(os.getenv("EVAL_ENDPOINT_TIMEOUT", 60))
SUCCESS_THRESHOLD: float = 0.25  # Same threshold as benchmark


# =====================
# Schemas
# =====================

StrId = constr(min_length=1, strip_whitespace=True)


class EvaluationRequest(BaseModel):
    """Request model for task evaluation"""

    task_id: StrId = Field(..., description="Unique identifier for the task")
    prompt: StrId = Field(..., description="The task prompt/description")
    url: AnyUrl = Field(..., description="The URL where the task should be executed")
    tests: list[dict[str, Any]] = Field(..., min_items=0, description="List of tests to validate the solution")
    actions: list[dict[str, Any]] = Field(..., min_items=0, description="List of actions to execute")
    web_agent_id: StrId = Field(..., description="Identifier for the web agent")
    web_project_id: StrId = Field(..., description="Web project ID")
    relevant_data: dict[str, Any] = Field(default_factory=dict, description="Additional contextual data")
    should_record: bool = Field(default=False, description="Whether to record GIF of execution")
    timeout_seconds: NonNegativeFloat | None = Field(None, description="Optional hard timeout for this evaluation (defaults to service timeout)")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "task_id": "021e8bcb-da0b-4ae4-9eac-892a8c441521",
                "prompt": "Retrieve details of the user whose name equals 'Jane Doe'.",
                "url": "http://localhost:8008/",
                "tests": [{"type": "CheckEventTest", "event_name": "VIEW_USER_PROFILE", "event_criteria": {"name": "Jane Doe"}, "description": "Check if specific event was triggered"}],
                "actions": [{"type": "ClickAction", "selector": "#login-btn"}],
                "web_agent_id": "3",
                "web_project_id": "autoconnect",
                "relevant_data": {},
                "should_record": False,
                "timeout_seconds": 60,
            }
        }


class EvaluationResponse(BaseModel):
    """Response model for task evaluation"""

    success: bool = Field(..., description=f"Whether the task passed (score >= {SUCCESS_THRESHOLD})")
    final_score: float = Field(..., ge=0.0, le=1.0, description="Final evaluation score (0-1)")
    raw_score: float = Field(..., ge=0.0, le=1.0, description="Raw score before adjustments (0-1)")
    execution_time: float = Field(..., ge=0.0, description="Time taken to evaluate in seconds")
    tests_passed: int = Field(..., ge=0, description="Number of tests that passed")
    total_tests: int = Field(..., ge=0, description="Total number of tests")
    action_count: int = Field(..., ge=0, description="Number of actions executed")
    had_errors: bool = Field(..., description="Whether any errors occurred during evaluation")
    error_message: str | None = Field(None, description="Error message if any")
    gif_recording: str | None = Field(None, description="Base64-encoded GIF if recording enabled")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "success": True,
                "final_score": 1.0,
                "raw_score": 1.0,
                "execution_time": 2.5,
                "tests_passed": 3,
                "total_tests": 3,
                "action_count": 5,
                "had_errors": False,
                "error_message": None,
                "gif_recording": None,
            }
        }


# =====================
# Service
# =====================


class EvaluationEndpointService:
    """Service for evaluating task solutions on-the-fly."""

    def __init__(self, default_timeout: float = DEFAULT_TIMEOUT_SECONDS):
        self.default_timeout = default_timeout

    def _get_project(self, project_id: str | None) -> WebProject:
        """Resolve a WebProject or raise a 404-like error if missing/unknown."""
        if not project_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="web_project_id is required")
        try:
            projects = get_projects_by_ids(demo_web_projects, [project_id])
            if not projects:
                raise KeyError(project_id)
            return projects[0]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown web_project_id: {project_id}") from e

    async def _evaluate_inner(self, req: EvaluationRequest) -> EvaluationResponse:
        project = self._get_project(req.web_project_id)

        # Build Task
        task = Task(
            id=req.task_id,
            prompt=req.prompt,
            url=str(req.url),
            tests=req.tests,
            relevant_data=req.relevant_data,
            should_record=req.should_record,
            web_project_id=project.id,
        )

        # Parse actions safely
        try:
            actions = [BaseAction.create_action(a) for a in req.actions]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid action payload: {e!s}") from e

        task_solution = TaskSolution(task_id=req.task_id, actions=actions, web_agent_id=req.web_agent_id)

        backend = BackendDemoWebService(project)
        try:
            await backend.reset_database(web_agent_id=req.web_agent_id)

            evaluator_config = EvaluatorConfig(
                enable_grouping_tasks=False,
                chunk_size=1,
                should_record_gif=req.should_record,
            )
            evaluator = ConcurrentEvaluator(project, evaluator_config)

            eval_result: EvaluationResult = await evaluator.evaluate_single_task_solution(task, task_solution)
            stats = getattr(eval_result, "stats", None)
            success = float(eval_result.final_score) >= float(SUCCESS_THRESHOLD)

            response = EvaluationResponse(
                success=success,
                final_score=float(getattr(eval_result, "final_score", 0.0)),
                raw_score=float(getattr(eval_result, "raw_score", 0.0)),
                execution_time=float(getattr(stats, "total_time", 0.0)) if stats else 0.0,
                tests_passed=int(getattr(stats, "tests_passed", 0)) if stats else 0,
                total_tests=int(getattr(stats, "total_tests", 0)) if stats else 0,
                action_count=int(getattr(stats, "action_count", len(actions))) if stats else len(actions),
                had_errors=bool(getattr(stats, "had_errors", False)) if stats else False,
                error_message=str(getattr(stats, "error_message", "")) or None if stats else None,
                gif_recording=getattr(eval_result, "gif_recording", None) if req.should_record else None,
            )

            logger.info(
                "Evaluation completed | task_id={} success={} score={:.2f}",
                req.task_id,
                success,
                response.final_score,
            )
            return response
        finally:
            try:
                await backend.close()
            except Exception:
                logger.warning("Backend close() raised, ignored.")

    async def evaluate_with_timeout(self, req: EvaluationRequest) -> EvaluationResponse:
        timeout = float(req.timeout_seconds or self.default_timeout)
        return await asyncio.wait_for(self._evaluate_inner(req), timeout=timeout)


# =====================
# FastAPI App
# =====================


def _install_logging():
    # Configure loguru once. You could add JSON sink or env-controlled verbosity here.
    logger.remove()
    logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[override]
    _install_logging()
    logger.info("Starting Evaluation Endpoint Service...")

    # Bootstrap application-wide deps
    AppBootstrap()

    # Attach service + uptime
    app.state.service = EvaluationEndpointService()
    app.state.started_at = datetime.now(UTC)

    logger.success("Evaluation Endpoint Service ready!")
    try:
        yield
    finally:
        logger.info("Shutting down Evaluation Endpoint Service...")
        app.state.service = None


app = FastAPI(
    title="Autoppia IWA - Evaluation Endpoint",
    description="Fast evaluation endpoint for agents to check task solutions on-the-fly",
    version="1.0.0",
    lifespan=lifespan,
)

# Optional CORS (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Utilities / Dependencies ----------


def _get_request_id(request: Request) -> str:
    rid = request.headers.get("x-request-id") or request.headers.get("x-amzn-trace-id")
    if not rid:
        rid = f"req-{int(datetime.now().timestamp() * 1000)}"
    return rid


def get_service(request: Request) -> EvaluationEndpointService:
    svc = getattr(request.app.state, "service", None)
    if svc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not initialized")
    return svc


# ---------- Routes ----------


@app.get("/health")
async def health_check(request: Request):
    """Health check with uptime and version."""
    started_at: datetime = getattr(request.app.state, "started_at", datetime.now(UTC))
    uptime_seconds = (datetime.now(UTC) - started_at).total_seconds()
    return {
        "status": "healthy",
        "service": "evaluation-endpoint",
        "version": app.version,
        "uptime_seconds": int(uptime_seconds),
    }


@app.post("/evaluate", response_model=EvaluationResponse, response_model_exclude_none=True)
async def evaluate_task_solution(
    request_model: EvaluationRequest,
    request: Request,
    service: Annotated[EvaluationEndpointService, Depends(get_service)],
) -> EvaluationResponse:
    """
    Evaluate a task solution and return whether it passes.

    Runs the full evaluation pipeline including:
    - Action execution in a browser
    - Running all test cases
    - Computing the final score

    Returns success=True if final_score >= 0.25 (same threshold as benchmark).
    """
    rid = _get_request_id(request)
    logger.bind(request_id=rid).info("/evaluate called for task_id={}", request_model.task_id)
    try:
        return await service.evaluate_with_timeout(request_model)
    except TimeoutError as err:
        logger.error("Evaluation timed out | task_id={} timeout={}s", request_model.task_id, request_model.timeout_seconds or service.default_timeout)
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Evaluation timed out") from err
    except HTTPException as httperr:
        logger.error(httperr)

        raise  # bubble up explicit HTTP errors
    except Exception as e:
        logger.error("Evaluation failed | task_id={} err={}", request_model.task_id, e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Evaluation error: {e!s}") from e


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):  # type: ignore[override]
    """Global exception handler - last resort."""
    # If we've already converted to HTTPException, FastAPI will use that handler.
    logger.error("Unhandled exception: {}", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# =====================
# Entrypoint
# =====================


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Start the evaluation endpoint service."""
    logger.info("Starting Evaluation Endpoint Service on {}:{}", host, port)
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("UVICORN_LOG_LEVEL", "info"))


if __name__ == "__main__":
    # Allow port override from command line
    port_arg: int | None = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(port=port_arg or DEFAULT_PORT)
