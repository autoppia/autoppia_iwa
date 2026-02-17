import os
import sys
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from autoppia_iwa.entrypoints.judge_benchmark.test_real_web import WebVoyagerBenchmark, WebVoyagerConfig
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent

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
    url: str = ""
    prompt: str = ""
    agent_host: str = "127.0.0.1"
    agent_port: int = 5000
    agent_timeout: int = 120
    task_indices: list = []
    num_of_urls: int = 1

    def validate_payload(self):
        errors = []
        # Custom task mode: url and prompt must be non-empty
        if self.url and self.prompt:
            if not isinstance(self.url, str) or not self.url.strip():
                errors.append("`url` must be a non-empty string.")
            if not isinstance(self.prompt, str) or not self.prompt.strip():
                errors.append("`prompt` must be a non-empty string.")
        # Dataset selection mode: at least one of num_of_urls or task_indices must be set
        else:
            if (not self.num_of_urls or self.num_of_urls < 1) and not self.task_indices:
                errors.append("Either `num_of_urls` must be >= 1 or `task_indices` must be a non-empty list.")
            if self.task_indices and not all(isinstance(i, int) and i >= 0 for i in self.task_indices):
                errors.append("All `task_indices` must be non-negative integers.")

        if not isinstance(self.agent_port, int) or self.agent_port <= 0:
            errors.append("`agent_port` must be a positive integer.")
        if not isinstance(self.agent_timeout, int) or self.agent_timeout <= 0:
            errors.append("`agent_timeout` must be a positive integer.")
        if not isinstance(self.num_of_urls, int) or self.num_of_urls < 0:
            errors.append("`num_of_urls` must be a non-negative integer.")

        if errors:
            raise ValueError("Payload validation failed: " + "; ".join(errors))


@app.post("/test-judge-agent")
async def run_real_web_task(config: RealWebTaskConfig):
    try:
        # Generate unique agent id and name
        unique_id = str(uuid.uuid4())
        unique_name = f"JudgeAgent_{unique_id[:8]}"

        agent = ApifiedOneShotWebAgent(
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
            num_of_urls=config.num_of_urls,
            task_indices=config.task_indices,
            # should_record_gif=True,
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
