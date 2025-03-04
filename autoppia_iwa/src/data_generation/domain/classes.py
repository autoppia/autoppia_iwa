# file: data_generation/domain/classes.py

import uuid
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

# Import your test classes:
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckUrlTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot


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
TestUnion = Annotated[Union[CheckUrlTest, FindInHtmlTest, CheckEventTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot], Field(discriminator="type")]


class Task(BaseModel):
    """
    Represents a task with associated metadata, specs, tests, etc.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task")
    scope: Literal["global", "local"] = Field(default="local", description="Task scope: 'global' for system-wide tasks, 'local' for specific context tasks")
    is_web_real: bool = Field(default=False, description="Indicates if the task operates on a real web environment versus simulation")
    web_project_id: Optional[str] = Field(default=None, description="Web project ID")
    url: str = Field(..., description="Target URL where the task will be executed")
    prompt: str = Field(..., description="Natural language description of the task objectives and requirements")
    html: str = Field(default_factory=str, description="Complete HTML content of the target page")
    clean_html: str = Field(default_factory=str, description="Optimized HTML content with reduced overhead for processing")
    interactive_elements: Optional[str] = Field(default=None, description="Mapping of interactive elements found in the HTML content, including buttons, forms, etc.")
    screenshot: Optional[str] = Field(default=None, description="Pil Image of the task environment or webpage encoded in base64 and stringify")
    screenshot_description: Optional[str] = Field(default=None, description="Textual description of the screenshot content and relevant elements")
    specifications: BrowserSpecification = Field(default_factory=BrowserSpecification, description="Browser configuration and requirements for task execution")

    tests: List[TestUnion] = Field(default_factory=list, description="Collection of validation tests that verify the task")

    milestones: Optional[List["Task"]] = Field(default=None, description="Ordered list of Subtasks that must be completed sequentially")
    relevant_data: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual data required for task execution")
    success_criteria: Optional[str] = Field(default=None, description="Clear definition of conditions that indicate successful task completion")
    logic_function: Optional[dict] = Field(default=None, description="Boolean expression using T1..Tn notation to evaluate overall task success")

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    @property
    def prompt_with_relevant_data(self) -> str:
        if self.relevant_data:
            return f"{self.prompt}\nRelevant data: {self.relevant_data}"
        return self.prompt

    def model_dump(self, *args, **kwargs) -> dict:
        # Example override to hide screenshot if needed
        dump = super().model_dump(*args, **kwargs)
        if "screenshot" in dump:
            dump["screenshot"] = "None"
        return dump

    def nested_model_dump(self, *args, **kwargs) -> Dict[str, Any]:
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

        # # Create the Task object
        return cls(**data)


class TaskGenerationConfig(BaseModel):
    save_task_in_db: bool = False
    save_web_analysis_in_db: bool = True
    enable_crawl: bool = True
    generate_milestones: bool = False
    num_or_urls: int = None
    random_urls: bool = True
    prompts_per_url: int = 20
