from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig
from autoppia_iwa.src.backend_demo_web.classes import WebProject
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import TaskDifficultyLevel
from autoppia_iwa.src.bootstrap import AppBootstrap

app = AppBootstrap()

# Suppose you have a WebProject object
my_web_project = WebProject(
    name="SampleStore",
    backend_url="",
    frontend_url="https://wikipedia.com",
    is_real_web=True,
    events=[],
    web_analysis=[],
    urls=[],
    data_classes={}
)

# Then create a config:
my_config = TaskGenerationConfig(
    web_project=my_web_project,
    save_task_in_db=False,
    save_web_analysis_in_db=False,
    enable_crawl=True,
    generate_milestones=False,
    number_of_prompts_per_task=1  # generate 3 tasks per URL
)

pipeline = TaskGenerationPipeline(config=my_config)
output = pipeline.generate(task_difficulty_level=TaskDifficultyLevel.MEDIUM)

print("Generated tasks:", [t.prompt for t in output.tasks])
