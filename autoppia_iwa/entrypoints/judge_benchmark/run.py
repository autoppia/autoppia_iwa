"""
Simple code-first entrypoint.
Edit the configuration below, then run:
    python -m autoppia_iwa.entrypoints.judge_benchmark.run
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.judge_benchmark.test_real_web import WebVoyagerBenchmark, WebVoyagerConfig
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =========================
# 💡 Configuration
# =========================

# 1) Agent (where your agent is listening)
AGENTS = [
    ApifiedWebAgent(id="1", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=250),
]

# 2) Choose how to select tasks
#    - If True: use the custom URL + prompt below
#    - If False: select tasks from dataset using NUM_OF_URLS or TASK_INDICES
USE_CUSTOM_TASK = True

# 2a) Custom task (used when USE_CUSTOM_TASK=True)
CUSTOM_URL = "https://www.allrecipes.com/"
CUSTOM_PROMPT = "Provide a recipe for vegetarian lasagna with more than 100 reviews and a rating of at least 4.5 stars suitable for 6 people."

# 2b) Dataset selection (used when USE_CUSTOM_TASK=False)
#     Set one of the following:
#     - NUM_OF_URLS: first N tasks from dataset
#     - TASK_INDICES: explicit indices from dataset, e.g. [0, 2, 5]
NUM_OF_URLS = 1
TASK_INDICES: list[int] = []

# 3) Run options
RECORD_GIF = True


def main():
    """
    Main entrypoint for the benchmark.
    """
    try:
        logger.info("Initializing benchmark...")

        # Assemble configuration from in-file settings
        if USE_CUSTOM_TASK:
            cfg = WebVoyagerConfig(
                agents=AGENTS,
                url=CUSTOM_URL,
                prompt=CUSTOM_PROMPT,
                num_of_urls=1,
                task_indices=[],
                should_record_gif=RECORD_GIF,
            )
            tasks_for_log = 1
        else:
            cfg = WebVoyagerConfig(
                agents=AGENTS,
                url=None,
                prompt=None,
                num_of_urls=NUM_OF_URLS,
                task_indices=TASK_INDICES,
                should_record_gif=RECORD_GIF,
            )
            tasks_for_log = len(TASK_INDICES) if TASK_INDICES else NUM_OF_URLS

        if not cfg.agents:
            logger.error("No agents configured.")
            return
        logger.info(f"Configuration: {len(cfg.agents)} agent(s), {tasks_for_log} task(s)")

        # Create and run benchmark
        benchmark = WebVoyagerBenchmark(cfg)
        asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
