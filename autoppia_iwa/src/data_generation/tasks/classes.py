# file: data_generation/domain/classes.py
import uuid
from typing import Annotated, Any

from pydantic import BaseModel, Field, PrivateAttr, field_validator

# Import your test classes:
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot
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
TestUnion = Annotated[CheckEventTest | JudgeBaseOnHTML | JudgeBaseOnScreenshot, Field(discriminator="type")]


class Task(BaseModel):
    """
    Represents a task with associated metadata, specs, tests, etc.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task")
    is_web_real: bool = Field(default=False, description="Indicates if the task operates on a real web environment versus simulation")
    web_project_id: str | None = Field(default=None, description="Web project ID")
    url: str = Field(..., description="Target URL where the task will be executed")
    prompt: str = Field(..., description="Natural language description of the task objectives and requirements")
    specifications: BrowserSpecification = Field(default_factory=BrowserSpecification, description="Browser configuration and requirements for task execution")
    tests: list[TestUnion] = Field(default_factory=list, description="Collection of validation tests that verify the task")
    use_case: Any = Field(default=None, description="UseCase instance associated with this task")
    should_record: bool = False
    _original_prompt: str = PrivateAttr()

    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    def __init__(self, **data):
        original_prompt = data.get("original_prompt", data.get("prompt", ""))
        super().__init__(**data)
        object.__setattr__(self, "_original_prompt", original_prompt)

    @property
    def original_prompt(self) -> str:
        return self._original_prompt

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
        if self.use_case:
            serialized["use_case"] = self.use_case.serialize()
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

        if data.get("use_case"):
            data["use_case"] = UseCase.deserialize(data["use_case"])
        task = cls(**data)
        object.__setattr__(task, "_original_prompt", data.get("prompt", ""))
        return task

    def clean_task(self) -> dict:
        """
        Create a minimal version of the task for serialization.
        Removes all verbose fields including tests, use_case, and other non-essential data.
        """
        # Start with a basic model dump but exclude many fields
        cleaned = self.model_dump(
            exclude={
                "tests",  # Remove all tests
                "use_case",  # Remove use case completely
            }
        )

        cleaned["original_prompt"] = self.original_prompt

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

        # Update prompt in the copy
        if isinstance(task_copy.prompt, str):
            task_copy.prompt = task_copy.prompt.replace("<web_agent_id>", web_agent_id)

        return task_copy


class TaskGenerationConfig(BaseModel):
    # Task quantity controls
    prompts_per_use_case: int  = 1  # Number of task variations to generate per use case (<=0/None => auto)
    # Specific use cases to focus on. If None, generates for all available use cases.
    use_cases: list[str] | None = None
    dynamic: bool = False

    @field_validator("prompts_per_use_case", mode="before")
    @classmethod
    def _empty_prompts_mean_auto(cls, value):
        """Map empty strings or explicit 'None' to actual None so callers can opt-in via config/env."""
        if value in ("", None, "None", "none"):
            return None
        return value
