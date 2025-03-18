import asyncio
import logging
import os

# Autoppia/third-party imports
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(), logging.FileHandler("stress_test.log")])
logger = logging.getLogger("stress_test")

# -----------------------------------------------------------------------------
# Configuration for the stress test
# -----------------------------------------------------------------------------
USE_CACHED_TASKS = False  # Set to True to use cached tasks from JSON file
TASKS_CACHE_DIR = "data/tasks_cache"  # Directory to store task cache files
M = 1  # Number of copies of each solution to evaluate
PROMPTS_PER_URL = 15
NUM_OF_URLS = 10

# Create output/cache directories if needed
os.makedirs(TASKS_CACHE_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Define the agents for the stress test
# -----------------------------------------------------------------------------
AGENTS: list[BaseAgent] = [RandomClickerWebAgent(name="Random-clicker"), ApifiedWebAgent(name="browser-use", host="localhost", port=9000)]

# Identifier for the browser-use agent
BROWSER_USE_AGENT_ID = "ApifiedWebAgent-browser-use"


async def main():
    """Main function to run the multi-task agent evaluation (stress test)."""
    logger.info("Starting comprehensive multi-task agent evaluation with batch processing...")

    # Initialize the application
    AppBootstrap()

    # Initialize timing metrics
    timing_metrics = TimingMetrics()
    timing_metrics.start()

    # Container to store results: { agent_id: { task_id: {"score": ...} } }

    # Load or create demo web projects
    web_projects = await initialize_demo_webs_projects(demo_web_projects)
    if not web_projects:
        logger.error("No demo web projects available.")
        return

    # Use the first project for demonstration
    demo_project = web_projects[0]
    logger.info(f"Using project: {demo_project.name}")

    # Generate or load tasks for the project
    tasks = await generate_tasks_for_project(
        demo_project,
        use_cached_tasks=USE_CACHED_TASKS,
        task_cache_dir=TASKS_CACHE_DIR,
        prompts_per_url=PROMPTS_PER_URL,
        num_of_urls=NUM_OF_URLS,
    )

    if not tasks:
        logger.error("No tasks available.")
        return

    logger.info(f"Evaluating {len(tasks)} tasks with {len(AGENTS)} agents, {M} solution copies each...")

    for task in tasks:
        print(task.prompt)
        for test in task.tests:
            print(test)


if __name__ == "__main__":
    asyncio.run(main())
