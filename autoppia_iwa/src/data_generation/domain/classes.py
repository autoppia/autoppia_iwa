# file: data_generation/domain/classes.py

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest


class TaskDifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskPromptForUrl(BaseModel):
    page_url: str = Field(..., description="URL of the page where the task is to be performed")
    task_prompts: List[str] = Field(..., description="List of task prompts for the given URL")


class BrowserSpecification(BaseModel):
    viewport_width: int = Field(1920, description="Width of the viewport in pixels")
    viewport_height: int = Field(1080, description="Height of the viewport in pixels")
    screen_width: int = Field(1920, description="Total width of the physical screen in pixels")
    screen_height: int = Field(1080, description="Total height of the physical screen in pixels")
    device_pixel_ratio: float = Field(1.0, description="Ratio of physical pixels to CSS pixels")
    scroll_x: int = Field(0, description="Horizontal scroll offset in pixels")
    scroll_y: int = Field(0, description="Vertical scroll offset in pixels")
    browser_x: int = Field(0, description="X position of the browser window on the screen")
    browser_y: int = Field(0, description="Y position of the browser window on the screen")


class Task(BaseModel):
    """
    Represents a task with associated metadata, specifications, and success criteria.
    This model captures all necessary information for task execution and validation,
    including browser specifications, test cases, and milestone subtasks.
    """
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the task, auto-generated using UUID4"
    )
    type: Literal["global", "local"] = Field(
        default="local",
        description="Task scope: 'global' for system-wide tasks, 'local' for specific context tasks"
    )
    is_web_real: bool = Field(
        default=False,
        description="Indicates if the task operates on a real web environment versus simulation"
    )
    web_project_id: Optional[str] = Field(default=None, description="Web project ID")
    url: str = Field(
        ...,
        description="Target URL where the task will be executed"
    )
    prompt: str = Field(
        ...,
        description="Natural language description of the task objectives and requirements"
    )
    html: str = Field(
        default_factory=str,
        description="Complete HTML content of the target page"
    )
    clean_html: str = Field(
        default_factory=str,
        description="Optimized HTML content with reduced overhead for processing"
    )
    interactive_elements: Optional[str] = Field(
        default=None,
        description="Mapping of interactive elements found in the HTML content, including buttons, forms, etc."
    )
    screenshot: Optional[str] = Field(
        default=None,
        description="Pil Image of the task environment or webpage encoded in base64 and stringify"
    )
    screenshot_description: Optional[str] = Field(
        default=None,
        description="Textual description of the screenshot content and relevant elements"
    )
    specifications: BrowserSpecification = Field(
        default_factory=BrowserSpecification,
        description="Browser configuration and requirements for task execution"
    )
    tests: List[BaseTaskTest] = Field(
        default_factory=list,
        description="Collection of validation tests that verify task completion"
    )
    milestones: Optional[List["Task"]] = Field(
        default=None,
        description="Ordered list of Subtasks that must be completed sequentially"
    )
    relevant_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional contextual data required for task execution"
    )
    success_criteria: Optional[str] = Field(
        default=None,
        description="Clear definition of conditions that indicate successful task completion"
    )
    logic_function: Optional[dict] = Field(
        default=None,
        description="Boolean expression using T1..Tn notation to evaluate overall task success"
    )

    @property
    def prompt_with_relevant_data(self) -> str:
        if self.relevant_data:
            return f"{self.prompt} /n Relevant data you may need: {self.relevant_data}"
        return self.prompt

    # def __str__(self):
    #     pass

    def model_dump(self, *args, **kargs):
        dump = super().model_dump(*args, **kargs)
        dump["screenshot"] = "None"
        return dump

    def nested_model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["tests"] = [test.model_dump() for test in self.tests]
        base_dump.pop("web_analysis", None)
        return base_dump

    def serialize(self) -> dict:
        """
        Serialize a Task object to a dictionary format suitable for JSON storage.
        Handles all nested elements including tests and milestones.

        Returns:
            dict: A serialized representation of the Task
        """
        # Start with basic model dump
        serialized = self.model_dump(exclude={"web_analysis"})

        # Specially handle tests
        serialized["tests"] = [test.serialize() for test in self.tests]

        # Recursively serialize milestones if they exist
        if self.milestones:
            serialized["milestones"] = [milestone.serialize() for milestone in self.milestones]

        # Handle screenshot data (potentially large)
        if serialized.get("screenshot") and isinstance(serialized["screenshot"], bytes):
            serialized["screenshot"] = serialized["screenshot"].decode("utf-8")

        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> "Task":
        """
        Deserialize a dictionary into a Task object.
        Handles all nested elements including tests and milestones.

        Args:
            data (dict): Serialized task data

        Returns:
            Task: A reconstructed Task object
        """
        # Create a copy to avoid modifying the input data
        task_data = data.copy()

        # Handle tests - convert to appropriate test objects
        if "tests" in task_data:
            task_data["tests"] = [BaseTaskTest.deserialize(test) for test in task_data["tests"]]

        # Handle milestones recursively
        if task_data.get("milestones"):
            task_data["milestones"] = [cls.deserialize(milestone) for milestone in task_data["milestones"]]

        # Handle BrowserSpecification
        if "specifications" in task_data:
            task_data["specifications"] = BrowserSpecification.model_validate(task_data["specifications"])

        # Handle potential naming incompatibilities
        if "test_cases" in task_data and "tests" not in task_data:
            task_data["tests"] = task_data.pop("test_cases")

        if "description" in task_data and not task_data.get("prompt"):
            task_data["prompt"] = task_data.pop("description")

        # Create the Task object
        return cls(**task_data)


class TaskGenerationConfig(BaseModel):
    save_task_in_db: bool = False
    save_web_analysis_in_db: bool = True
    enable_crawl: bool = True
    generate_milestones: bool = False
    num_or_urls:int = None
    random_urls:bool = True
    prompts_per_url:int = 20
    num_or_urls:int = None


class TasksGenerationOutput(BaseModel):
    tasks: List[Task] = Field(..., description="List of generated tasks")
    total_phase_time: float = Field(..., description="Total time taken for the task generation phase")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of task generation")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tasks": [task.model_dump() for task in self.tasks],
            "total_phase_time": self.total_phase_time,
            "timestamp": self.timestamp,
        }
