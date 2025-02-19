# file: examples/run_task_generation.py

from autoppia_iwa.src.data_generation.domain.classes import (
    TaskGenerationConfig,
    TasksGenerationOutput,
)
from autoppia_iwa.src.backend_demo_web.classes import WebProject
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.backend_demo_web.config import initialize_test_demo_web_projects
from typing import List

# Bootstrap the application and its DI container.
app = AppBootstrap()

# 1) Create a WebProject (we let web analysis fill in domain_analysis & pages).
#    Here we pick the first available demo web project.
my_web_project: List[WebProject] = initialize_test_demo_web_projects()[0]

# 2) Create a TaskGenerationConfig specifying how many tasks we want.
my_config = TaskGenerationConfig(
    save_task_in_db=False,
    save_web_analysis_in_db=True,
    enable_crawl=True,
    generate_milestones=False,
    # Global and local task counts:
    global_tasks_to_generate=3,
    local_tasks_to_generate_per_url=2,
)


# 3) Instantiate the pipeline with the project and configuration.
pipeline = TaskGenerationPipeline(web_project=my_web_project, config=my_config)

# 4) Run the pipeline to generate tasks.
output: TasksGenerationOutput = pipeline.generate()
print(f"Tasks: {output.tasks}")

# 5) Log and manually inspect the generated tasks and corresponding tests.
print("----- Generated Tasks and Tests -----")
for idx, task in enumerate(output.tasks, 1):
    print(f"\nTask {idx}:")
    print(f"  URL: {task.url}")
    print(f"  Prompt: {task.prompt}")
    # Assuming each test has a meaningful model_dump() representation.
    if task.tests:
        print("  Tests:")
        for test in task.tests:
            print(f"    - {test.model_dump()}")
    else:
        print("  No tests generated.")

input("\nReview the above tasks and tests. Press Enter to proceed to the final judgment...")

# 6) Use the OpenAI 03-mini model (o3) to judge the overall output.
judge_input = "Here is a summary of the generated tasks and tests:\n\n"
for idx, task in enumerate(output.tasks, 1):

    judge_input += f"Task {idx}:\n"
    judge_input += f"  Prompt: {task.prompt}\n"
    judge_input += f"  URL: {task.url}\n"
    if task.tests:
        judge_input += "  Tests:\n"
        for test in task.tests:
            judge_input += f"    - {test.model_dump()}\n"
    else:
        judge_input += "  No tests generated.\n"
    judge_input += "\n"
judge_input += (
    "Please evaluate whether these tasks and tests are sensible, actionable, and sufficiently "
    "detailed for further automated evaluation. Provide a brief opinion and any suggestions for improvements."
)

# Retrieve the llm_service instance from the DI container.
llm_service = app.container.llm_service()

judge_response = llm_service.make_request(
    message_payload=[{"role": "user", "content": judge_input}],
    chat_completion_kwargs={
        "temperature": 0.5,
        "top_k": 40,
        "model": "03-mini",  # Force using the 03-mini model for judgment,
    },
)

print("\n----- O3 Judge's Opinion -----")
print(judge_response)
input("\nReview the judge's opinion. Press Enter to finish.")
