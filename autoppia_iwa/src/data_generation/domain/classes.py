# file: data_generation/domain/classes.py

import uuid
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

# Import your test classes:
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckUrlTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot
from autoppia_iwa.src.demo_webs.classes import UseCase


class BrowserSpecification(BaseModel):
    viewport_width: int = 1920
    viewport_height: int = 1080
    screen_width: int = 1920
    screen_height: int = 1080
    device_pixel_ratio: float = 1.0
    scroll_x: int = 0
    scroll_y: int = 0
    browser_x: int = 0
    browser_y: int = 0


# The union of test classes for polymorphic deserialization
TestUnion = Annotated[CheckUrlTest | FindInHtmlTest | CheckEventTest | JudgeBaseOnHTML | JudgeBaseOnScreenshot, Field(discriminator="type")]


class Task(BaseModel):
    """
    Represents a task with associated metadata, specs, tests, etc.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task")
    scope: Literal["global", "local"] = Field(default="local", description="Task scope: 'global' for system-wide tasks, 'local' for specific context tasks")
    is_web_real: bool = Field(default=False, description="Indicates if the task operates on a real web environment versus simulation")
    web_project_id: str | None = Field(default=None, description="Web project ID")
    url: str = Field(..., description="Target URL where the task will be executed")
    prompt: str = Field(..., description="Natural language description of the task objectives and requirements")
    html: str = Field(default_factory=str, description="Complete HTML content of the target page")
    clean_html: str = Field(default_factory=str, description="Optimized HTML content with reduced overhead for processing")
    interactive_elements: str | None = Field(default=None, description="Mapping of interactive elements found in the HTML content, including buttons, forms, etc.")
    screenshot: str | None = Field(default=None, description="Pil Image of the task environment or webpage encoded in base64 and stringify")
    screenshot_description: str | None = Field(default=None, description="Textual description of the screenshot content and relevant elements")
    specifications: BrowserSpecification = Field(default_factory=BrowserSpecification, description="Browser configuration and requirements for task execution")
    tests: list[TestUnion] = Field(default_factory=list, description="Collection of validation tests that verify the task")
    milestones: list["Task"] | None = Field(default=None, description="Ordered list of Subtasks that must be completed sequentially")
    relevant_data: dict[str, Any] = Field(default_factory=dict, description="Additional contextual data required for task execution")
    success_criteria: str | None = Field(default=None, description="Clear definition of conditions that indicate successful task completion")
    use_case: UseCase | None = None

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    @property
    def prompt_with_relevant_data(self) -> str:
        if self.relevant_data:
            return f"{self.prompt}\n Relevant data you may need: {self.relevant_data}"
        return self.prompt

    def model_dump(self, *args, **kwargs) -> dict:
        # Example override to hide screenshot if needed
        dump = super().model_dump(*args, **kwargs)
        if "screenshot" in dump:
            dump["screenshot"] = "None"
        return dump

    def nested_model_dump(self, *args, **kwargs) -> dict[str, Any]:
        base_dump = self.model_dump(*args, **kwargs)
        # If you want to ensure tests are fully serialized
        base_dump["tests"] = [test.model_dump() for test in self.tests]
        return base_dump

    def serialize(self) -> dict:
        """
        Serialize a Task object to a dictionary.
        """
        serialized = self.model_dump()
        # For sub-tests:
        serialized["tests"] = [test.model_dump() for test in self.tests]
        # If you have sub-tasks in milestones
        if self.milestones:
            serialized["milestones"] = [m.serialize() for m in self.milestones]
        if self.use_case:
            serialized["use_case"] = self.use_case.serialize()
        serialized.pop("html", None)
        serialized.pop("clean_html", None)
        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> "Task":
        """
        Optionally custom method, but normally you can do Task(**data).
        """
        # # Create a copy to avoid modifying the input data
        # task_data = data.copy()

        # # Handle tests - convert to appropriate test objects
        # if "tests" in task_data:
        #     task_data["tests"] = [BaseTaskTest.deserialize(test) for test in task_data["tests"]]

        # # Handle milestones recursively
        # if task_data.get("milestones"):
        #     task_data["milestones"] = [cls.deserialize(milestone) for milestone in task_data["milestones"]]

        # # Handle BrowserSpecification
        # if "specifications" in task_data:
        #     task_data["specifications"] = BrowserSpecification.model_validate(task_data["specifications"])

        # # Handle potential naming incompatibilities
        # if "test_cases" in task_data and "tests" not in task_data:
        #     task_data["tests"] = task_data.pop("test_cases")

        # if "description" in task_data and not task_data.get("prompt"):
        #     task_data["prompt"] = task_data.pop("description")

        if "use_case" in data:
            data["use_case"] = UseCase.deserialize(data["use_case"])

        # # Create the Task object
        return cls(**data)

    def clean_task(self) -> dict:
        """
        Create a minimal version of the task for serialization.
        Removes all verbose fields including tests, milestones, use_case, HTML content, and other non-essential data.
        """
        # Start with a basic model dump but exclude many fields
        cleaned = self.model_dump(
            exclude={
                "tests",  # Remove all tests
                "html",  # HTml content of the page
                "clean_html",  # Also large
                "milestones",  # Remove nested tasks completely
                "use_case",  # Remove use case completely
                "interactive_elements",  # Remove interactive elements
            }
        )

        # Remove any None values to make the output cleaner
        return {k: v for k, v in cleaned.items() if v is not None}

    def prepare_for_agent(self, web_agent_id: str) -> "Task":
        """
        Creates and returns a copy of the task with web_agent_id replacements applied.
        The original task remains unmodified.
        Args:
            web_agent_id: The web agent ID to replace placeholders with
        Returns:
            A new Task instance with replacements applied
        """
        # Create a deep copy of the current task
        import copy

        task_copy = copy.deepcopy(self)

        # Update relevant_data in the copy
        for key, value in task_copy.relevant_data.items():
            if isinstance(value, str):
                task_copy.relevant_data[key] = value.replace("<web_agent_id>", web_agent_id)
            elif isinstance(value, dict):
                # Si el valor es un diccionario, procesamos sus elementos
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        value[sub_key] = sub_value.replace("<web_agent_id>", web_agent_id)
            elif isinstance(value, list):
                # Si el valor es una lista, procesamos sus elementos
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        value[i] = item.replace("<web_agent_id>", web_agent_id)

        # Update prompt in the copy
        if isinstance(task_copy.prompt, str):
            task_copy.prompt = task_copy.prompt.replace("<web_agent_id>", web_agent_id)

        return task_copy


class TaskGenerationConfig(BaseModel):
    # Database saving options
    save_task_in_db: bool = False

    # URL handling
    num_of_urls: int = 5  # Number of URLs to process
    random_urls: bool = True  # Whether to randomly select URLs

    # Task generation controls
    generate_local_tasks: bool = False  # Generate page-specific tasks
    generate_global_tasks: bool = True  # Generate global use case tasks

    # Task quantity controls
    prompts_per_url: int = 20  # Maximum tasks to return per URL
    prompts_per_use_case: int = 1  # Number of task variations to generate per use case
    final_task_limit: int = 50  # Total maximum tasks to return from the pipeline
