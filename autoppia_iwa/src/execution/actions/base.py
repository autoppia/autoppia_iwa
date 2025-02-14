import inspect
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Type
from playwright.async_api import Page
from pydantic import BaseModel, Field, ValidationError, field_validator

# -----------------------------------------
# Logger Setup
# -----------------------------------------
logger = logging.getLogger(__name__)

# -----------------------------------------
# Selector and related definitions
# -----------------------------------------
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


class SelectorType(str, Enum):
    ATTRIBUTE_VALUE_SELECTOR = "attributeValueSelector"
    TAG_CONTAINS_SELECTOR = "tagContainsSelector"
    XPATH_SELECTOR = "xpathSelector"


class Selector(BaseModel):
    type: SelectorType = Field(..., description="The type of selector.")
    attribute: Optional[str] = Field(None, description="The attribute name.")
    value: str = Field(..., description="The value for this selector.")
    case_sensitive: bool = Field(False, description="Whether the match is case-sensitive.")

    @field_validator("attribute")
    @classmethod
    def validate_attribute(cls, value: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values.data.get("type") == SelectorType.ATTRIBUTE_VALUE_SELECTOR and not value:
            raise ValueError("Attribute must be provided for ATTRIBUTE_VALUE_SELECTOR.")
        return value

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str, values: Dict[str, Any]) -> str:
        if values.data.get("type") == SelectorType.XPATH_SELECTOR:
            cls._validate_xpath(value)
        return value

    @staticmethod
    def _validate_xpath(xpath: str):
        from lxml import etree

        try:
            etree.XPath(xpath)
        except ImportError:
            raise ValueError("lxml library is required for XPath validation.")
        except etree.XPathSyntaxError as e:
            raise ValueError(f"Invalid XPath: {xpath}. Error: {e}")

    def to_playwright_selector(self) -> str:
        match self.type:
            case SelectorType.ATTRIBUTE_VALUE_SELECTOR:
                if self.attribute in ATTRIBUTE_FORMATS:
                    if self.attribute in ["id", "class"]:
                        return f"{ATTRIBUTE_FORMATS[self.attribute]}{self.value}"
                    return ATTRIBUTE_FORMATS[self.attribute].format(value=self.value)
                return f"[{self.attribute}='{self.value}']"
            case SelectorType.TAG_CONTAINS_SELECTOR:
                if self.case_sensitive:
                    return f'text="{self.value}"'
                return f"text={self.value}"
            case SelectorType.XPATH_SELECTOR:
                if not self.value.startswith("//"):
                    return f"xpath=//{self.value}"
                return f"xpath={self.value}"
            case _:
                raise ValueError(f"Unsupported selector type: {self.type}")


# -----------------------------------------
# BaseAction interface
# -----------------------------------------


class BaseAction(BaseModel):
    """
    Base class for all actions.
    """

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the action."""
        return f"{self.__class__.__name__}(type={self.__class__.__name__})"

    # def __repr__(self) -> str:
    #     """Returns a detailed string representation useful for debugging."""
    #     return f"{self.__class__.__name__}({self.model_dump()})"

    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        raise NotImplementedError("Execute method must be implemented by subclasses.")

    @classmethod
    def from_response(cls, actions_response: List[Dict[str, Any]], action_class_map: Dict[str, Type["BaseAction"]]) -> List["BaseAction"]:
        """
        Converts raw action data into instances of BaseAction subclasses.

        :param actions_response: List of raw action data.
        :param action_class_map: Mapping of action types to their corresponding classes.
        :return: List of instantiated BaseAction subclasses.
        """
        actions: List[BaseAction] = []
        for action_data in actions_response:
            try:
                action = cls._parse_action_data(action_data, action_class_map)
                if action:
                    actions.append(action)
            except ValidationError as e:
                logger.error(f"[Validation Error] Failed to process action data: {action_data}. Exception: {e}")
            except Exception as e:
                logger.error(f"[Processing Error] Unexpected error for action data: {action_data}. Exception: {e}")
        return actions

    @classmethod
    def _parse_action_data(cls, action_data: Dict[str, Any], action_class_map: Dict[str, Type["BaseAction"]]) -> Optional["BaseAction"]:
        """
        Parses a single action data dictionary into a BaseAction instance.

        Args:
            action_data: Raw action data.
            action_class_map: Mapping of action types to their corresponding classes.

        Returns:
            Optional[BaseAction]: An instance of the appropriate action class, or None if parsing fails.
        """
        action_info = action_data.get("action", {})
        action_type = action_info.get("type")
        if not action_type:
            logger.warning("Action type is missing in action data.")
            return None

        action_class = action_class_map.get(action_type)
        if not action_class or not issubclass(action_class, BaseAction):
            logger.warning(f"Unsupported or invalid action type '{action_type}' encountered.")
            return None

        action_params = cls._prepare_action_parameters(action_info, action_data.get("selector"), action_class)
        return action_class(**action_params)

    @staticmethod
    def _prepare_action_parameters(action_info: Dict[str, Any], selector_data: Optional[Dict[str, Any]], action_class: Type["BaseAction"]) -> Dict[str, Any]:
        """
        Prepares the parameters for instantiating an action class.

        Args:
            action_info: The action information dictionary.
            selector_data: The selector data dictionary.
            action_class: The action class to instantiate.

        Returns:
            Dict[str, Any]: A dictionary of parameters for the action class.
        """
        action_params = {**action_info.get("parameters", {}), **{k: v for k, v in action_info.items() if k != "type"}}

        # Add default values for specific action types
        defaults = {
            "type": {"value": ""},
            "navigate": {"url": ""},
            "dragAndDrop": {"sourceSelector": "", "targetSelector": ""},
            "scroll": {"direction": ""},
            "assert": {"assertion": ""},
        }
        if not action_params:
            action_params.update(defaults.get(action_info.get("type"), {}))

        # Keep only required parameters
        required_params = set(inspect.signature(action_class).parameters.keys())
        filtered_params = {k: v for k, v in action_params.items() if k in required_params}

        # Include selector if required
        if "selector" in required_params and selector_data:
            filtered_params["selector"] = Selector(**selector_data)

        return filtered_params

    # def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
    #     """Generate a structured dictionary representation of the model."""
    #     return {"type": self.__class__.__name__, **super().model_dump(mode="json", *args, **kwargs)}


class BaseActionWithSelector(BaseAction):
    selector: Optional[Selector] = None

    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        raise NotImplementedError("This action requires an execution implementation.")

    def validate_selector(self):
        if not self.selector:
            raise ValueError("Selector is required for this action.")
        return self.selector.to_playwright_selector()
