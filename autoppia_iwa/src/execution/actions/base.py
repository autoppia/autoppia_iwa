# base.py
from enum import Enum
from typing import Any, ClassVar, Optional

from loguru import logger
from playwright.async_api import Page
from pydantic import BaseModel, ConfigDict, Field

# ------------------------------------------------------
# SELECTOR DEFINITIONS
# ------------------------------------------------------


class SelectorType(str, Enum):
    """Enumeration of supported selector strategies."""

    ATTRIBUTE_VALUE_SELECTOR = "attributeValueSelector"
    TAG_CONTAINS_SELECTOR = "tagContainsSelector"
    XPATH_SELECTOR = "xpathSelector"


class Selector(BaseModel):
    """
    Represents a strategy for locating elements on a web page.
    """

    type: SelectorType
    attribute: str | None = None
    value: str
    case_sensitive: bool = False

    model_config = ConfigDict(use_enum_values=True)

    def _format_id_selector(self) -> str:
        """Format ID selector with sanitization."""
        clean_value = self.value.lstrip("#")
        return f"#{clean_value}"

    def _format_class_selector(self) -> str:
        """Format class selector handling multiple classes."""
        classes = self.value.strip().split()
        clean_classes = [cls.lstrip(".") for cls in classes]
        return "".join(f".{cls}" for cls in clean_classes)

    def _format_attribute_selector(self) -> str:
        """Format attribute-based selector."""
        ATTRIBUTE_FORMATS = {
            "id": "#{value}",
            "class": ".{value}",  # Placeholder, handled specially below
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
            "title": "[title='{value}']",
        }

        if self.attribute == "id":
            return self._format_id_selector()
        if self.attribute == "class":
            return self._format_class_selector()
        if self.attribute == "custom":
            return self.value
        if self.attribute in ATTRIBUTE_FORMATS:
            return ATTRIBUTE_FORMATS[self.attribute].format(value=self.value)
        return f"[{self.attribute}='{self.value}']"

    def _format_text_selector(self) -> str:
        """Format text selector with case sensitivity handling."""
        options = "" if self.case_sensitive else "i"
        quoted_value = repr(self.value)
        return f"text={quoted_value}{' ' + options if options else ''}"

    def _format_xpath_selector(self) -> str:
        """Format XPath selector."""
        value_stripped = self.value.strip()
        if value_stripped.startswith("//") or value_stripped.startswith("(//"):
            return f"xpath={self.value}"
        return f"xpath=//{self.value}"

    def to_playwright_selector(self) -> str:
        """
        Converts the Selector model into a Playwright-compatible selector string.

        Returns:
            The selector string usable with Playwright's page methods.

        Raises:
            ValueError: If the selector type is unsupported.
        """
        selector_type = SelectorType(self.type)

        if selector_type == SelectorType.ATTRIBUTE_VALUE_SELECTOR:
            if not self.attribute:
                raise ValueError("Attribute must be specified for ATTRIBUTE_VALUE_SELECTOR")
            return self._format_attribute_selector()

        if selector_type == SelectorType.TAG_CONTAINS_SELECTOR:
            return self._format_text_selector()

        if selector_type == SelectorType.XPATH_SELECTOR:
            return self._format_xpath_selector()

        raise ValueError(f"Unsupported selector type: {self.type}")


# ------------------------------------------------------
# BASE ACTION CLASSES
# ------------------------------------------------------


class ActionRegistry:
    """
    Registry to store and retrieve action subclasses based on their type name.

    Action classes are automatically registered when they are defined,
    thanks to the `__init_subclass__` mechanism in `BaseAction`.
    """

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
    Abstract base class for all browser automation actions.

    Subclasses must define a `type` attribute (usually using `Literal`)
    and implement the `execute` method.
    They are automatically registered in the `ActionRegistry`.
    """

    type: str = Field(..., description="Discriminating field for the action type.")
    selector: Selector | None = Field(None, description="The selector to locate the target element. Optional for actions not targeting specific elements.")

    model_config = ConfigDict(extra="allow", use_enum_values=True)

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses in the ActionRegistry."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "type") and cls.type:
            ActionRegistry.register(cls.type, cls)

    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        """
        Executes the action.

        This method must be implemented by concrete subclasses.

        Args:
            page: The Playwright Page object to interact with, or None if the action doesn't require a page.
            backend_service: A placeholder for any backend service interaction needed.
            web_agent_id: An identifier for the web agent instance.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
            ValueError: If `page` is required but is `None`.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.execute method must be implemented by subclasses.")

    def get_playwright_selector(self) -> str:
        """
        Validates that the selector exists and returns its Playwright representation.

        Returns:
            The Playwright-compatible selector string.

        Raises:
            ValueError: If the selector is missing or invalid. (Shouldn't happen if pydantic validation passed)
        """
        if not self.selector:
            raise ValueError(f"Selector is required for {self.type} action but is missing.")
        try:
            return self.selector.to_playwright_selector()
        except ValueError as e:
            logger.error(f"Invalid selector configuration: {self.selector}. Error: {e}")
            raise ValueError(f"Invalid selector configuration. Error: {e}") from e

    @classmethod
    def create_action(cls, action_data: dict) -> Optional["BaseAction"]:
        """
        Factory method to create an action instance from a dictionary.

        Uses the 'type' field in the dictionary to determine which
        action subclass to instantiate via the ActionRegistry.

        Args:
            action_data: Dictionary containing action type and relevant fields.

        Returns:
            An instance of the appropriate BaseAction subclass.

        Raises:
            ValueError: If action_data is not a dictionary, is missing the 'type' field,
                        or if the action type is unsupported.
            pydantic.ValidationError: If the data fails validation for the specific action model.
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
    """
    Base class for actions that require a `Selector` to identify an element.
    """

    selector: Selector = Field(..., description="The selector used to locate the target element for the action. This is mandatory.")

    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        """Execute method placeholder for actions with selectors."""
        raise NotImplementedError("Execute method must be implemented by subclasses of BaseActionWithSelector.")
