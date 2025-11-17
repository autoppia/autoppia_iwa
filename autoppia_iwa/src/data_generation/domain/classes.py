# file: data_generation/domain/classes.py
import random
import uuid
from typing import Annotated, Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from pydantic import BaseModel, Field, PrivateAttr, field_validator

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
    dynamic: list[str] = Field(default_factory=list, description="Array of dynamic features to apply: v1 (assign seed), v2 (assign v2-seed), v3 (assign seed structure). Can select any combination.")

    _original_prompt: str = PrivateAttr()
    _seed_value: int = PrivateAttr()
    _v2_seed_value: int = PrivateAttr()
    _seed_structure_value: int = PrivateAttr()

    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    @field_validator("dynamic")
    @classmethod
    def validate_dynamic(cls, v: list[str]) -> list[str]:
        """Validate that dynamic array only contains v1, v2, or v3."""
        valid_values = {"v1", "v2", "v3"}
        if not isinstance(v, list):
            raise ValueError("dynamic must be a list")
        invalid_values = [val for val in v if val not in valid_values]
        if invalid_values:
            raise ValueError(f"dynamic array can only contain 'v1', 'v2', or 'v3'. Found invalid values: {invalid_values}")
        # Remove duplicates while preserving order
        seen = set()
        unique_list = []
        for val in v:
            if val not in seen:
                seen.add(val)
                unique_list.append(val)
        return unique_list

    def __init__(self, **data):
        original_prompt = data.get("original_prompt", data.get("prompt", ""))
        super().__init__(**data)
        object.__setattr__(self, "_original_prompt", original_prompt)
        # Don't add seed automatically - let the benchmark decide when to add it
        object.__setattr__(self, "_seed_value", None)
        object.__setattr__(self, "_v2_seed_value", None)
        object.__setattr__(self, "_seed_structure_value", None)
        # Automatically apply dynamic features to URL
        self._apply_dynamic_to_url()

    @property
    def prompt_with_relevant_data(self) -> str:
        if self.relevant_data:
            return f"{self.prompt}\n Relevant data you may need: {self.relevant_data}"
        return self.prompt

    @property
    def original_prompt(self) -> str:
        return self._original_prompt

    def _apply_dynamic_to_url(self) -> None:
        """
        Automatically apply all dynamic features to the URL based on the dynamic array.
        This is called automatically after Task initialization.
        """
        if "v1" in self.dynamic:
            self.assign_seed_to_url()
        if "v2" in self.dynamic:
            self.assign_v2_seed_to_url()
        if "v3" in self.dynamic:
            self.assign_seed_structure_to_url()

    def assign_seed_to_url(self) -> None:
        """
        Assign a random seed to the task URL if v1 is in dynamic array.
        Avoids overwriting an existing seed or breaking query structure.
        """
        if "v1" in self.dynamic:
            if self._seed_value is None:
                object.__setattr__(self, "_seed_value", random.randint(0, 300))

            parsed = urlparse(self.url)
            query_params = parse_qs(parsed.query)

            # Only add if 'seed' not already in URL
            if "seed" not in query_params:
                query_params["seed"] = [str(self._seed_value)]

                new_query = urlencode(query_params, doseq=True)
                new_url = urlunparse(parsed._replace(query=new_query))
                object.__setattr__(self, "url", new_url)

    def assign_v2_seed_to_url(self) -> None:
        """
        Assign a random seed to the task URL if v2 is in dynamic array.
        Avoids overwriting an existing v2-seed or breaking query structure.
        If v2-seed is already in the URL, extracts it and sets _v2_seed_value.
        """
        if "v2" in self.dynamic:
            parsed = urlparse(self.url)
            query_params = parse_qs(parsed.query)

            # If v2-seed is already in URL, extract it and set _v2_seed_value
            if "v2-seed" in query_params and self._v2_seed_value is None:
                try:
                    extracted_seed = int(query_params["v2-seed"][0])
                    object.__setattr__(self, "_v2_seed_value", extracted_seed)
                except (ValueError, IndexError):
                    # If extraction fails, generate a new one
                    object.__setattr__(self, "_v2_seed_value", random.randint(1, 300))
            elif self._v2_seed_value is None:
                # Generate a new v2-seed if not already set
                object.__setattr__(self, "_v2_seed_value", random.randint(1, 300))

            # Only add if 'v2-seed' not already in URL
            if "v2-seed" not in query_params:
                query_params["v2-seed"] = [str(self._v2_seed_value)]

                new_query = urlencode(query_params, doseq=True)
                new_url = urlunparse(parsed._replace(query=new_query))
                object.__setattr__(self, "url", new_url)

    def assign_seed_structure_to_url(self) -> None:
        """
        Assign a random seed-structure to the task URL if v3 is in dynamic array.
        Avoids overwriting an existing seed-structure or breaking query structure.
        """
        if "v3" in self.dynamic:
            if self._seed_structure_value is None:
                object.__setattr__(self, "_seed_structure_value", random.randint(0, 300))

            parsed = urlparse(self.url)
            query_params = parse_qs(parsed.query)

            # Only add if 'seed-structure' not already in URL
            if "seed-structure" not in query_params:
                query_params["seed-structure"] = [str(self._seed_structure_value)]

                new_query = urlencode(query_params, doseq=True)
                new_url = urlunparse(parsed._replace(query=new_query))
                object.__setattr__(self, "url", new_url)

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
    # Specific use cases to focus on, will override num_use_cases if set, for current project
    use_cases: list[str] | None = None
    dynamic: list[str] | None = None  # Dynamic features to apply (v1, v2, v3) - used to pre-compute URLs with seeds
