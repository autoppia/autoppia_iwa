# file: data_generation/domain/classes.py

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


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
    Represents a task with a unique id, prompt, URL, browser specs, tests, milestones, and web analysis.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task")
    type: Literal["global", "local"] = "local"
    is_web_real: bool = False
    prompt: str = Field(..., description="Prompt for the task")
    url: str = Field(..., description="URL where the task is to be performed")
    html: str = Field(default_factory=str, description="HTML content associated with the task")
    screenshot: Optional[Any] = None
    specifications: BrowserSpecification = Field(
        default_factory=BrowserSpecification,
        description="Browser specifications for the task"
    )
    tests: List[BaseTaskTest] = Field(
        default_factory=list,
        description="List of tests associated with the task"
    )
    milestones: Optional[List["Task"]] = Field(
        None,
        description="List of milestone tasks"
    )
    relevant_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of relevant data for this task"
    )
    success_criteria: Optional[str] = Field(
        None,
        description="A concise definition of what determines successful completion."
    )
    logic_function: Optional[str] = Field(
        None,
        description="Boolean formula referencing T1..Tn for final success determination."
    )

    def nested_model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["tests"] = [test.model_dump() for test in self.tests]
        base_dump.pop("web_analysis", None)
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
    return cls(
        id=data.get("id", str(uuid.uuid4())),  # Ensures unique ID if missing
        prompt=data["prompt"],  # Required field
        url=data["url"],  # Required field
        html=data.get("html", ""),
        screenshot=data.get("screenshot"),
        specifications=BrowserSpecification.model_validate(data.get("specifications", {})),
        tests=[BaseTaskTest.model_validate(test) for test in data.get("tests", [])],
        milestones=[cls.from_dict(m) for m in data.get("milestones", [])] if data.get("milestones") else None,
        web_analysis=DomainAnalysis.model_validate(data["web_analysis"]) if "web_analysis" in data else None,
        relevant_data=data.get("relevant_data", {}),
        is_web_real=data.get("is_web_real", False),
    )


class TaskGenerationConfig(BaseModel):
    save_task_in_db: bool = False
    save_web_analysis_in_db: bool = True
    enable_crawl: bool = True
    generate_milestones: bool = False
    number_of_prompts_per_task: int = 1
    global_tasks_to_generate: int = 2
    local_tasks_to_generate_per_url: int = 2


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
