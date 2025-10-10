# file: data_generation/domain/classes.py

import uuid
from typing import Annotated, Any

from pydantic import BaseModel, Field, PrivateAttr

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
    is_web_real: bool = Field(default=False, description="Indicates if the task operates on a real web environment versus simulation")
    web_project_id: str | None = Field(default=None, description="Web project ID")
    url: str = Field(..., description="Target URL where the task will be executed")
    prompt: str = Field(..., description="Natural language description of the task objectives and requirements")
    specifications: BrowserSpecification = Field(default_factory=BrowserSpecification, description="Browser configuration and requirements for task execution")
    tests: list[TestUnion] = Field(default_factory=list, description="Collection of validation tests that verify the task")
    relevant_data: dict[str, Any] = Field(default_factory=dict, description="Additional contextual data required for task execution")
    use_case: Any = Field(default=None, description="UseCase instance associated with this task")
    should_record: bool = False

    _original_prompt: str = PrivateAttr()

    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    def __init__(self, **data):
        original_prompt = data.get("original_prompt", data.get("prompt", ""))
        super().__init__(**data)
        object.__setattr__(self, "_original_prompt", original_prompt)

    @property
    def prompt_with_relevant_data(self) -> str:
        if self.relevant_data:
            return f"{self.prompt}\n Relevant data you may need: {self.relevant_data}"
        return self.prompt

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

        if "use_case" in data:
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
    # save_task_in_db: bool = False

    # Task generation controls
    generate_global_tasks: bool = True  # Generate global use case tasks

    # Task quantity controls
    prompts_per_use_case: int = 1  # Number of task variations to generate per use case
    num_use_cases: int = 3  # Number of use_cases to consider for global task generation
    final_task_limit: int = 50  # Total maximum tasks to return from the pipeline
