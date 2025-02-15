# file: base.py

import inspect
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod

from playwright.async_api import Page
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)

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


class IAction(ABC):
    @abstractmethod
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        pass


class BaseAction(BaseModel, IAction):
    # Removed discriminator=True
    type: str = Field("", description="Action type identifier")

    class Config:
        # Let Pydantic store extra/unknown fields
        extra = "allow"
        from_attributes = True

    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = self.__class__.__name__
        super().__init__(**data)

    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        raise NotImplementedError("Execute method must be implemented by subclasses.")

    @classmethod
    def from_response(cls, actions_response: List[Dict[str, Any]], action_class_map: Dict[str, Type["BaseAction"]]) -> List["BaseAction"]:
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
        action_info = action_data
        if "type" not in action_data:
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

        required_params = set(inspect.signature(action_class).parameters.keys())
        filtered_params = {k: v for k, v in action_params.items() if k in required_params}

        if "selector" in required_params and selector_data:
            filtered_params["selector"] = Selector(**selector_data)

        return filtered_params


class BaseActionWithSelector(BaseAction):
    selector: Optional[Selector] = None

    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        raise NotImplementedError("This action requires an execution implementation.")

    def validate_selector(self):
        if not self.selector:
            raise ValueError("Selector is required for this action.")
        return self.selector.to_playwright_selector()
