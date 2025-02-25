# file: tasks.py

import asyncio
import traceback
from typing import List
import logging

from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
# You might need to import LocalTaskGenerationPipeline if it is in a different module
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import initialize_test_demo_web_projects, initialize_demo_webs_projects

# Import the TestGenerationPipeline from the new location
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import TestGenerationPipeline

# --- ADDED: to get a real LLM service instead of None ---
from autoppia_iwa.src.di_container import DIContainer

logger = logging.getLogger(__name__)

app = AppBootstrap()


async def main():
    try:
        # Create a WebProject (with its web analysis populated)
        demo_web_projects: List[WebProject] = await initialize_demo_webs_projects()
        web_project: WebProject = demo_web_projects[0]

        # Create TaskGenerationConfig if needed by TaskGenerationPipeline
        config = TaskGenerationConfig(
            save_task_in_db=False,
            save_web_analysis_in_db=False,
            enable_crawl=False,
            generate_milestones=False,
            global_tasks_to_generate=0,
            local_tasks_to_generate_per_url=2
        )

        # Instantiate the task generation pipeline.
        pipeline = TaskGenerationPipeline(web_project=web_project, config=config)

        # Generate tasks from a single URL using the frontend_url of the web project.
        tasks = await pipeline.generate_tasks_for_url(web_project.frontend_url)

        # --- Generate tests for the tasks ---
        llm_service = DIContainer.llm_service()
        test_pipeline = TestGenerationPipeline(llm_service=llm_service, web_project=web_project)
        tasks = await test_pipeline.add_tests_to_tasks(tasks)

        # Display results: show tasks along with their tests
        print("=== Generated Tasks and Tests ===")
        for idx, task in enumerate(tasks, start=1):
            print(f"Task {idx}:")
            print(f"  Prompt: {task.prompt}")
            print(f"  URL: {task.url}")
            print(f"  Success Criteria: {task.success_criteria}")
            if hasattr(task, "tests") and task.tests:
                print("  Tests:")
                for tidx, test in enumerate(task.tests, start=1):
                    print(f"    Test {tidx}: {test}")
            else:
                print("  No tests generated.")
            print(f"  Logic Expression: {task.logic_function}\n")

    except Exception as e:
        print(f"Error in main: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
