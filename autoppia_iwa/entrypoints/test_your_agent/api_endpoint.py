import os
import sys
import uuid
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =====================
# Constants / Settings
# =====================
DEFAULT_PORT: int = 5050
DEFAULT_HOST: str = "0.0.0.0"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentConfig(BaseModel):
    ip: str
    port: int | None = None
    projects: list[str]
    num_use_cases: int
    runs: int
    use_cases: list[str] | None = None
    timeout: int = 120
    should_record_gif: bool = False
    enable_dynamic_html: bool = True


@app.post("/test-your-agent")
async def test_your_agent(config: AgentConfig):
    """
    Endpoint to test a web agent against specified projects and use cases.

    Args:
        config (AgentConfig): Configuration for the agent and benchmark.

    Returns:
        dict: Benchmark results.
    """
    try:
        # Validate projects
        projects = get_projects_by_ids(demo_web_projects, config.projects)
        if not projects:
            raise HTTPException(status_code=400, detail="Invalid project IDs provided.")

        # Generate unique id and name for each agent
        unique_id = str(uuid.uuid4())
        unique_name = f"TestAgent_{unique_id[:8]}"

        # Configure the agent
        # If ip is a full URL (has scheme) or contains a path, use it directly as base_url.
        # If ip is a hostname/IP and port is provided, include port; otherwise omit.
        parsed = urlparse(config.ip)
        if parsed.scheme:
            base_url = config.ip.rstrip("/")
            agent = ApifiedWebAgent(id=unique_id, name=unique_name, timeout=config.timeout, base_url=base_url)
        else:
            # Treat ip as host
            agent = ApifiedWebAgent(id=unique_id, name=unique_name, host=config.ip, port=config.port, timeout=config.timeout)

        benchmark_config = BenchmarkConfig(
            projects=projects,
            agents=[agent],
            use_cached_tasks=False,
            prompts_per_use_case=1,
            num_use_cases=config.num_use_cases,
            use_cases=config.use_cases,
            runs=config.runs,
            max_parallel_agent_calls=1,
            use_cached_solutions=False,
            record_gif=config.should_record_gif,
            save_results_json=False,
            plot_results=False,
            enable_dynamic_html=config.enable_dynamic_html,
        )

        # Run the benchmark
        benchmark = Benchmark(benchmark_config)
        per_project_results = await benchmark.run()

        return per_project_results

    except Exception as e:
        logger.error(f"Error during benchmark: {e}")
        error_msg = f"Benchmark failed: {e}"
        raise HTTPException(status_code=500, detail=error_msg) from e


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Start the evaluation endpoint service."""
    logger.info("Starting Evaluation Endpoint Service on {}:{}", host, port)
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("UVICORN_LOG_LEVEL", "info"))


if __name__ == "__main__":
    # Allow port override from command line
    port_arg: int | None = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(port=port_arg or DEFAULT_PORT)
