import os
import sys
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from autoppia_iwa.entrypoints.judge_benchmark.test_real_web import WebVoyagerBenchmark, WebVoyagerConfig
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_PORT: int = 5070

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RealWebTaskConfig(BaseModel):
    url: str
    prompt: str
    agent_host: str = "127.0.0.1"
    agent_port: int = 5000
    agent_timeout: int = 120


@app.post("/judge-benchmark/run-real-web-task")
async def run_real_web_task(config: RealWebTaskConfig):
    try:
        # Generate unique agent id and name
        unique_id = str(uuid.uuid4())
        unique_name = f"JudgeAgent_{unique_id[:8]}"

        agent = ApifiedWebAgent(
            id=unique_id,
            name=unique_name,
            host=config.agent_host,
            port=config.agent_port,
            timeout=config.agent_timeout,
        )
        cfg = WebVoyagerConfig(
            agents=[agent],
            url=config.url,
            prompt=config.prompt,
            num_of_urls=1,
            # should_record_gif=True,
            # use_cached_solutions=False,
        )
        benchmark = WebVoyagerBenchmark(cfg)
        response = await benchmark.run()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {e}") from e


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Start the evaluation endpoint service."""
    logger.info("Starting Evaluation Endpoint Service on {}:{}", host, port)
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("UVICORN_LOG_LEVEL", "info"))


if __name__ == "__main__":
    # Allow port override from command line
    port_arg: int | None = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(port=port_arg or DEFAULT_PORT)
