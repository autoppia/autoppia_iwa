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


app = AppBootstrap()

# 1) Create a WebProject (we let web analysis fill in domain_analysis & pages).
my_web_project:List[WebProject] = initialize_test_demo_web_projects()[0]

# 2) Create a TaskGenerationConfig specifying how many tasks we want.
my_config = TaskGenerationConfig(
    save_task_in_db=False,
    save_web_analysis_in_db=True,
    enable_crawl=True,
    generate_milestones=False,
    # We'll specify how many tasks we want in total (global) and per URL (local):
    global_tasks_to_generate=3,
    local_tasks_to_generate_per_url=2,
)

# 3) Instantiate the pipeline with that config.
pipeline = TaskGenerationPipeline(web_project=my_web_project, config=my_config)

# 4) Run the pipeline.
output: TasksGenerationOutput = pipeline.generate()

# 5) Print or process the tasks.
print("Generated tasks:")
for t in output.tasks:
    print(f"- Category: {t.category} | URL: {t.url} | Prompt: {t.prompt}")
