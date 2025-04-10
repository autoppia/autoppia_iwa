# base.py
from enum import Enum
from typing import Any, ClassVar, Optional

from loguru import logger
from playwright.async_api import Page
from pydantic import BaseModel, Field

# ------------------------------------------------------
# SELECTOR LOGIC
# ------------------------------------------------------


class SelectorType(str, Enum):
    ATTRIBUTE_VALUE_SELECTOR = "attributeValueSelector"
    TAG_CONTAINS_SELECTOR = "tagContainsSelector"
    XPATH_SELECTOR = "xpathSelector"


class Selector(BaseModel):
    type: SelectorType
    attribute: str | None = None
    value: str
    case_sensitive: bool = False

    def to_playwright_selector(self) -> str:
        """
        Returns the final selector string for use with Playwright.
        """
        ATTRIBUTE_FORMATS = {
            "id": "#",
            "class": ".",
            "placeholder": "[placeholder='{value}']",
            "name": "[name='{value}']",
            "role": "[role='{value}']",
            "value": "[value='{value}']",
            "type": "[type='{value}']",
            "aria-label": "[aria-label='{value}']",
            "aria-labelledby": "[aria-labelledby='{value}']",
            "data-testid": "[data-testid='{value}']",
            "data-custom": "[data-custom='{value}']",
            "href": "a[href='{value}']",
        }

        if self.type == SelectorType.ATTRIBUTE_VALUE_SELECTOR:
            if self.attribute in ATTRIBUTE_FORMATS:
                fmt = ATTRIBUTE_FORMATS[self.attribute]
                if self.attribute in ["id", "class"]:
                    # #id or .class
                    return f"{fmt}{self.value}"
                return fmt.format(value=self.value)
            return f"[{self.attribute}='{self.value}']"

        elif self.type == SelectorType.TAG_CONTAINS_SELECTOR:
            if self.case_sensitive:
                return f'text="{self.value}"'
            return f"text={self.value}"

        elif self.type == SelectorType.XPATH_SELECTOR:
            if not self.value.startswith("//"):
                return f"xpath=//{self.value}"
            return f"xpath={self.value}"

        else:
            raise ValueError(f"Unsupported selector type: {self.type}")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Custom model dump that properly handles enums."""
        dump = super().model_dump(**kwargs)
        if "type" in dump:
            dump["type"] = dump["type"].value
        return dump


# ------------------------------------------------------
# BASE ACTION CLASSES
# ------------------------------------------------------


class ActionRegistry:
    """Registry to store and retrieve action subclasses."""

    _registry: ClassVar[dict[str, type["BaseAction"]]] = {}

    @classmethod
    def register(cls, action_type: str, action_class: type["BaseAction"]):
        """Register an action class with a simplified key."""
        # Register with a lowercase version of action_type without "Action"
        action_key = action_type.replace("Action", "").lower()
        cls._registry[action_key] = action_class

    @classmethod
    def get(cls, action_type: str) -> type["BaseAction"]:
        """Retrieve an action class by its simplified key."""
        action_key = action_type.replace("Action", "").lower()
        if action_key not in cls._registry:
            raise ValueError(f"Unsupported action type: {action_key}")
        return cls._registry[action_key]


# ------------------------------------------------------
# BASE ACTION CLASSES
# ------------------------------------------------------


class BaseAction(BaseModel):
    """
    Base for all actions with a discriminating 'type' field.
    """

    type: str = Field(..., description="Discriminated action type")

    class Config:
        extra = "allow"

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses in the ActionRegistry."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "type") and cls.type:
            ActionRegistry.register(cls.type, cls)

    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        """Each subclass must implement its own `execute` logic."""
        raise NotImplementedError("Execute method must be implemented by subclasses.")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Custom model dump that properly handles enums and nested models."""
        dump = super().model_dump(**kwargs)
        if "selector" in dump and isinstance(dump["selector"], dict):
            selector = dump["selector"]
            if "type" in selector and isinstance(selector["type"], Enum):
                selector["type"] = selector["type"].value
        return dump

    @classmethod
    def create_action(cls, action_data: dict) -> Optional["BaseAction"]:
        """
        Create an action instance from action_data.

        Args:
            action_data: Dictionary containing action type and relevant fields.

        Returns:
            An instance of the appropriate BaseAction subclass.
        """
        if not isinstance(action_data, dict):
            logger.error(f"Invalid action_data: {action_data}. Expected a dictionary.")
            raise ValueError("action_data must be a dictionary.")

        new_action_data = {}

        if "selector" in action_data:
            new_action_data["selector"] = action_data["selector"]
        if "action" in action_data:
            new_action_data.update({**action_data["action"]})
        else:
            new_action_data = action_data
        action_type = new_action_data.get("type", "")

        if not action_type:
            logger.error("Missing 'type' in action data.")
            raise ValueError("Action data is missing 'type' field.")
        if action_type == "type":
            new_action_data["text"] = new_action_data.get("value", "")

        # Ensure the action type ends with "Action" for consistency
        if not action_type.endswith("Action"):
            new_action_data["type"] = f"{action_type.capitalize()}Action"

        try:
            # Retrieve the appropriate action class from the registry
            action_class = ActionRegistry.get(action_type)
            return action_class(**new_action_data)
        except ValueError as ve:
            logger.error(f"Failed to create action of type '{action_type}': {ve!s}")
        except Exception as e:
            logger.error(f"Error creating action of type '{action_type}': {e!s}")


class BaseActionWithSelector(BaseAction):
    selector: Selector | None = None

    def validate_selector(self) -> str:
        if not self.selector:
            raise ValueError("Selector is required for this action.")
        return self.selector.to_playwright_selector()

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Custom model dump that handles the Selector field."""
        dump = super().model_dump(**kwargs)
        if "selector" in dump and isinstance(self.selector, Selector):
            dump["selector"] = self.selector.model_dump(**kwargs)
        return dump
