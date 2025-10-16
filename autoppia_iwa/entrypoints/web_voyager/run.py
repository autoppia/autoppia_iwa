"""
Code-first entrypoint: configure projects, agents, runs, and options here.
Then run with:  python -m entrypoints.benchmark.run
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.web_voyager.test_real_web import WebVoyagerBenchmark, WebVoyagerConfig
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# =========================
# 💡 Code configuration
# =========================

# 1) Agents (ports where your agents are listening)
AGENTS = [
    # ApifiedWebAgent(id="1", name="AutoppiaAgent1", host="127.0.0.1", port=5000, timeout=120),
    # ApifiedWebAgent(id="2", name="AutoppiaAgent2", host="127.0.0.1", port=7000, timeout=120),
    ApifiedWebAgent(id="2", name="BrowserUse-OpenAI", host="127.0.0.1", port=5000, timeout=120),
]

# 2) Benchmark parameters
CFG = WebVoyagerConfig(
    agents=AGENTS,
    # Tasks
    num_of_urls=1,
    task_indices=[1],
)


def main():
    """
    Main entrypoint for the benchmark.
    """
    try:
        logger.info("Initializing benchmark...")

        if not CFG.agents:
            logger.error("No agents configured in AGENTS.")
            return
        tasks = len(CFG.task_indices) if CFG.task_indices else CFG.num_of_urls
        logger.info(f"Configuration: {len(CFG.agents)} agents, {tasks} tasks each")

        # Create and run benchmark
        benchmark = WebVoyagerBenchmark(CFG)
        asyncio.run(benchmark.run())

    except KeyboardInterrupt:
        logger.warning("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
