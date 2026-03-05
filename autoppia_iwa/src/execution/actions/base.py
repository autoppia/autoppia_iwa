import json
import re
from enum import Enum
from typing import Any, ClassVar, Optional, Type

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

    def to_playwright_selector(self) -> str:
        """
        Converts the Selector model into a Playwright-compatible selector string.

        Returns:
            The selector string usable with Playwright's page methods.

        Raises:
            ValueError: If the selector type is unsupported.
        """
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

        selector_type = SelectorType(self.type)

        if selector_type == SelectorType.ATTRIBUTE_VALUE_SELECTOR:
            if not self.attribute:
                raise ValueError("Attribute must be specified for ATTRIBUTE_VALUE_SELECTOR")

            if self.attribute == "id":
                # Basic sanitization: remove leading '#' if present
                clean_value = self.value.lstrip("#")
                return f"#{clean_value}"
            elif self.attribute == "class":
                # Handle multiple classes by chaining '.class1.class2'
                classes = self.value.strip().split()
                # Basic sanitization: remove leading '.' if present
                clean_classes = [cls.lstrip(".") for cls in classes]
                return "".join(f".{cls}" for cls in clean_classes)
            elif self.attribute == "custom":
                return self.value
            elif self.attribute in ATTRIBUTE_FORMATS:
                # Use predefined formats for common attributes
                return ATTRIBUTE_FORMATS[self.attribute].format(value=self.value)
            else:
                return f"[{self.attribute}='{self.value}']"

        elif selector_type == SelectorType.TAG_CONTAINS_SELECTOR:
            # Playwright's text selector: https://playwright.dev/docs/selectors#text-selector
            # Handles case sensitivity via options
            options = "" if self.case_sensitive else "i"  # 'i' for case-insensitive
            # Ensure value containing quotes is handled correctly
            quoted_value = repr(self.value)  # Uses appropriate quotes automatically
            return f"text={quoted_value}{' ' + options if options else ''}"

        elif selector_type == SelectorType.XPATH_SELECTOR:
            # Prepend 'xpath=' if not already starting with '//' (common convention)
            if self.value.strip().startswith("//") or self.value.strip().startswith("(//"):
                return f"xpath={self.value}"
            else:
                return f"xpath=//{self.value}"
        else:
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

    @staticmethod
    def _normalize_action_key(action_type: str) -> str:
        key = str(action_type).strip()
        if key.endswith("Action"):
            key = key[: -len("Action")]
        # Allow function/tool style names like "request_user_input" or "request-user-input".
        return re.sub(r"[\s_\-]", "", key).lower()

    @classmethod
    def register(cls, action_type: str, action_class: type["BaseAction"]):
        """Register an action class with a simplified key."""
        action_key = cls._normalize_action_key(action_type)
        cls._registry[action_key] = action_class

    @classmethod
    def get(cls, action_type: str) -> type["BaseAction"]:
        """Retrieve an action class by its simplified key."""
        action_key = cls._normalize_action_key(action_type)
        if action_key not in cls._registry:
            raise ValueError(f"Unsupported action type: {action_key}")
        return cls._registry[action_key]

    @classmethod
    def values(cls) -> list[type["BaseAction"]]:
        """Return registered action classes without duplicates."""
        return list(dict.fromkeys(cls._registry.values()))


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
        action_type = getattr(cls, "type", None)
        if isinstance(action_type, str) and action_type:
            ActionRegistry.register(action_type, cls)

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

        normalized_action_data = cls._normalize_action_data(action_data)
        action_type = str(normalized_action_data.get("type", "")).strip()

        if not action_type:
            logger.error("Missing 'type' in action data.")
            raise ValueError("Action data is missing 'type' field.")
        if action_type == "type" and "text" not in normalized_action_data:
            normalized_action_data["text"] = normalized_action_data.get("value", "")

        try:
            # Retrieve the appropriate action class from the registry
            action_class = ActionRegistry.get(action_type)
            cls._inject_canonical_action_type(normalized_action_data, action_class)
            return action_class(**normalized_action_data)
        except ValueError as ve:
            logger.error(f"Failed to create action of type '{action_type}': {ve!s}")
        except Exception as e:
            logger.error(f"Error creating action of type '{action_type}': {e!s}")
        return None

    @classmethod
    def _normalize_action_data(cls, action_data: dict[str, Any]) -> dict[str, Any]:
        payload = dict(action_data)

        # Legacy wrapper: {"action": {...}, "selector": {...}}
        if isinstance(payload.get("action"), dict):
            action_payload = dict(payload["action"])
            if "selector" in payload and "selector" not in action_payload:
                action_payload["selector"] = payload["selector"]
            payload = action_payload

        # Function-calling payloads:
        # {"name":"navigate","arguments":{...}}
        # {"function":{"name":"navigate","arguments":"{...json...}"}}
        function_payload = payload.get("function")
        if isinstance(function_payload, dict):
            payload = cls._normalize_named_payload(
                {
                    "name": function_payload.get("name"),
                    "arguments": function_payload.get("arguments"),
                }
            )
            return payload

        if "name" in payload and "type" not in payload:
            return cls._normalize_named_payload(payload)

        return payload

    @classmethod
    def _normalize_named_payload(cls, payload: dict[str, Any]) -> dict[str, Any]:
        name = payload.get("name")
        arguments = cls._coerce_arguments(payload.get("arguments"))
        normalized = dict(arguments)
        normalized["type"] = normalized.get("type", name)
        return normalized

    @staticmethod
    def _coerce_arguments(raw_arguments: Any) -> dict[str, Any]:
        if isinstance(raw_arguments, dict):
            return dict(raw_arguments)
        if isinstance(raw_arguments, str):
            raw_arguments = raw_arguments.strip()
            if not raw_arguments:
                return {}
            try:
                parsed = json.loads(raw_arguments)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return {}
        return {}

    @staticmethod
    def _to_snake_case(name: str) -> str:
        base = name[: -len("Action")] if name.endswith("Action") else name
        return re.sub(r"(?<!^)(?=[A-Z])", "_", base).lower()

    @staticmethod
    def _canonical_action_type(action_class: Type["BaseAction"]) -> str | None:
        canonical_type = None
        type_field = getattr(action_class, "model_fields", {}).get("type")
        if type_field is not None:
            canonical_type = getattr(type_field, "default", None)
        if not isinstance(canonical_type, str):
            canonical_type = getattr(action_class, "type", None)
        return canonical_type if isinstance(canonical_type, str) else None

    @classmethod
    def _inject_canonical_action_type(cls, payload: dict[str, Any], action_class: Type["BaseAction"]) -> None:
        canonical_type = cls._canonical_action_type(action_class)
        if canonical_type is not None:
            payload["type"] = canonical_type

    @classmethod
    def tool_name(cls) -> str:
        action_type = getattr(cls, "type", cls.__name__)
        return cls._to_snake_case(action_type)

    @classmethod
    def tool_description(cls) -> str:
        doc = (cls.__doc__ or "").strip().splitlines()
        return doc[0] if doc else f"Execute {cls.tool_name()}."

    @classmethod
    def tool_parameters_schema(cls) -> dict[str, Any]:
        schema = cls.model_json_schema()
        properties = dict(schema.get("properties", {}))
        properties.pop("type", None)
        schema["properties"] = properties

        required = [field for field in schema.get("required", []) if field != "type"]
        if required:
            schema["required"] = required
        else:
            schema.pop("required", None)
        schema.pop("title", None)
        return schema

    @classmethod
    def to_function_definition(cls) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": cls.tool_name(),
                "description": cls.tool_description(),
                "parameters": cls.tool_parameters_schema(),
            },
        }

    @classmethod
    def all_function_definitions(cls) -> list[dict[str, Any]]:
        return [action_cls.to_function_definition() for action_cls in ActionRegistry.values()]

    def to_tool_call(self) -> dict[str, Any]:
        return {
            "name": self.__class__.tool_name(),
            "arguments": self.model_dump(mode="json", exclude={"type"}, exclude_none=True),
        }


class BaseActionWithSelector(BaseAction):
    """
    Base class for actions that require a `Selector` to identify an element.
    """

    selector: Selector = Field(..., description="The selector used to locate the target element for the action. This is mandatory.")

    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        """Execute method placeholder for actions with selectors."""
        raise NotImplementedError("Execute method must be implemented by subclasses of BaseActionWithSelector.")
