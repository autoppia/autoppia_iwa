from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest


class TaskDifficultyLevel(Enum):
    """
    Enum representing the difficulty level of a task.
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskPromptForUrl(BaseModel):
    """
    Represents a task prompt associated with a specific URL.
    """

    page_url: str = Field(..., description="URL of the page where the task is to be performed")
    task_prompts: List[str] = Field(..., description="List of task prompts for the given URL")


class BrowserSpecification(BaseModel):
    """
    A class to represent the browser details with sensible default values.
    """

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
    Represents a task with a prompt, URL, browser specifications, tests, milestones, and web analysis.
    """
    type: Literal["global", "local"] = "local"
    prompt: str = Field(..., description="Prompt for the task")
    url: str = Field(..., description="URL where the task is to be performed")
    specifications: BrowserSpecification = Field(default_factory=BrowserSpecification,
                                                 description="Browser specifications for the task")
    tests: List[BaseTaskTest] = Field(default_factory=list, description="List of tests associated with the task")
    milestones: Optional[List["Task"]] = Field(None, description="List of milestone tasks")
    category: Optional[str] = None
    success_criteria: Optional[str] = Field(
        None, description="A concise definition of what determines successful completion."
    )

    # DONT MODIFY BASE MODEL_DUMP METHOD!
    def nested_model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Serializes the Task model to a dictionary, including nested models.
        """
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["tests"] = [test.model_dump() for test in self.tests]
        return base_dump

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Creates a Task instance from a dictionary, including nested test instances.

        Args:
            data (Dict[str, Any]): Dictionary containing the Task attributes.

        Returns:
            Task: The Task object created from the dictionary.
        """
        # Extract and construct tests
        test_data = data.get("tests", [])
        tests = BaseTaskTest.assign_tests(test_data)

        # Handle milestones recursively if provided
        milestones = data.get("milestones", [])

        # Create and return Task instance
        return cls(
            prompt=data.get("prompt"),
            url=data.get("url"),
            specifications=BrowserSpecification.model_validate(data.get("specifications", {})),
            tests=tests,
            milestones=milestones,
            web_analysis=DomainAnalysis.model_validate(data.get("web_analysis", {})) if data.get("web_analysis") else None,
        )


class TaskGenerationConfig(BaseModel):
    save_task_in_db: bool = False
    save_web_analysis_in_db: bool = True
    enable_crawl: bool = True
    generate_milestones: bool = False
    number_of_prompts_per_task: int = 1  # (Optional, if needed in older code)

    # New fields controlling how many tasks to generate:
    global_tasks_to_generate: int = 2
    local_tasks_to_generate_per_url: int = 2


class TasksGenerationOutput(BaseModel):
    """
    Represents the output of task generation, including the generated tasks, total phase time, and timestamp.
    """

    tasks: List[Task] = Field(..., description="List of generated tasks")
    total_phase_time: float = Field(..., description="Total time taken for the task generation phase")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of task generation")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the TasksGenerationOutput model to a dictionary.
        """
        return {
            "tasks": [task.model_dump() for task in self.tasks],
            "total_phase_time": self.total_phase_time,
            "timestamp": self.timestamp,
        }
