from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from autoppia_iwa.config.config import PROJECT_BASE_DIR

PROJECTS_ROOT = PROJECT_BASE_DIR / "src" / "demo_webs" / "projects"

PRIMITIVE_TYPES = {
    "str": "str",
    "string": "str",
    "int": "int",
    "integer": "int",
    "float": "float",
    "bool": "bool",
    "boolean": "bool",
    "list[str]": "list[str]",
    "list[int]": "list[int]",
    "list[float]": "list[float]",
    "list[bool]": "list[bool]",
}

OPERATOR_MAP = {
    "equals": "ComparisonOperator.EQUALS",
    "not_equals": "ComparisonOperator.NOT_EQUALS",
    "contains": "ComparisonOperator.CONTAINS",
    "not_contains": "ComparisonOperator.NOT_CONTAINS",
    "gt": "ComparisonOperator.GREATER_THAN",
    "gte": "ComparisonOperator.GTE",
    "lt": "ComparisonOperator.LESS_THAN",
    "lte": "ComparisonOperator.LTE",
}


class ConfigError(Exception):
    """Raised when a deck configuration file is invalid."""


def snake_case(value: str) -> str:
    tokens = re.split(r"[^a-zA-Z0-9]+", value.strip())
    tokens = [tok for tok in tokens if tok]
    if not tokens:
        return ""
    head, *tail = tokens
    result = head.lower()
    for tok in tail:
        result += "_" + tok.lower()
    return result


def pascal_case(value: str) -> str:
    tokens = re.split(r"[^a-zA-Z0-9]+", value.strip())
    return "".join(tok.capitalize() for tok in tokens if tok)


def normalize_field_name(value: str) -> str:
    candidate = snake_case(value)
    candidate = re.sub(r"^\d+", "", candidate)
    return candidate or value


def python_type(type_name: str, optional: bool) -> str:
    base = PRIMITIVE_TYPES.get(type_name.lower())
    if not base:
        base = type_name
    if optional and base != "Any":
        return f"{base} | None"
    return base


def dump_python(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ConfigError("Config root must be an object.")
    return data


@dataclass
class EventField:
    name: str
    source: str
    type_hint: str
    base_type: str


class ModuleGenerator:
    def __init__(self, config: dict[str, Any], target_dir: Path, force: bool) -> None:
        self.config = config
        self.project = config.get("project") or {}
        self.deployment = config.get("deployment") or {}
        self.events = config.get("events") or []
        self.use_cases = config.get("use_cases") or []
        self.pages = config.get("pages") or []
        self.target_dir = target_dir
        self.force = force

        if not self.project.get("slug"):
            raise ConfigError("project.slug is required")

    @property
    def slug(self) -> str:
        return self.project["slug"]

    def generate(self) -> None:
        if self.target_dir.exists():
            if not self.force:
                raise ConfigError(f"Directory {self.target_dir} already exists. Use --force to overwrite.")
        else:
            self.target_dir.mkdir(parents=True, exist_ok=True)

        (self.target_dir / "__init__.py").write_text(f'"""Auto-generated module for {self.slug}."""\n', encoding="utf-8")
        (self.target_dir / "main.py").write_text(self._render_main(), encoding="utf-8")
        (self.target_dir / "events.py").write_text(self._render_events(), encoding="utf-8")
        (self.target_dir / "generation_functions.py").write_text(self._render_generation_functions(), encoding="utf-8")
        (self.target_dir / "use_cases.py").write_text(self._render_use_cases(), encoding="utf-8")
        if self.pages:
            pages_path = self.target_dir / "pages.json"
            pages_path.write_text(json.dumps(self.pages, indent=2, ensure_ascii=False), encoding="utf-8")

    def _render_main(self) -> str:
        frontend_expr = self._url_expression("frontend")
        backend_expr = self._url_expression("backend")
        project_instance = f"{self.slug}_project"
        project_id = self.project.get("deck_id") or self.slug

        imports = ["from autoppia_iwa.src.demo_webs.classes import WebProject"]
        utils_imports = []
        if frontend_expr.startswith("get_frontend_url("):
            utils_imports.append("get_frontend_url")
        if backend_expr.startswith("get_backend_service_url("):
            utils_imports.append("get_backend_service_url")
        if utils_imports:
            imports.append(f"from ...utils import {', '.join(sorted(set(utils_imports)))}")
        imports.extend(
            [
                "from .events import EVENTS",
                "from .use_cases import ALL_USE_CASES",
                "",
                f"{project_instance} = WebProject(",
                f'    id="{project_id}",',
                f'    name="{self.project.get("name", self.slug)}",',
                f"    frontend_url={frontend_expr},",
                f"    backend_url={backend_expr},",
                "    events=EVENTS,",
                "    use_cases=ALL_USE_CASES,",
                ")",
            ]
        )
        return "\n".join(imports) + "\n"

    def _url_expression(self, kind: str) -> str:
        explicit = self.deployment.get(f"{kind}_url")
        index = self.deployment.get(f"{kind}_port_index")
        if explicit:
            return f'"{explicit.rstrip("/")}/"'
        if index is not None:
            if kind == "frontend":
                return f"get_frontend_url(index={index})"
            else:
                # All backends use shared service (no index needed)
                return "get_backend_service_url()"
        raise ConfigError(f"deployment.{kind}_url or {kind}_port_index must be provided")

    def _render_events(self) -> str:
        if not self.events:
            raise ConfigError("At least one event must be defined under events[]")

        class_defs = []
        event_class_names = []
        for spec in self.events:
            name = spec.get("name")
            if not name:
                raise ConfigError("Event name missing.")
            class_name = spec.get("class_name") or f"{pascal_case(name)}Event"
            event_class_names.append(class_name)
            description = spec.get("description", "")
            fields = []
            for field in spec.get("fields", []):
                field_name = normalize_field_name(field["name"])
                base_type = PRIMITIVE_TYPES.get(field.get("type", "str").lower(), field.get("type", "str"))
                optional = field.get("optional", True)
                type_hint = python_type(field.get("type", "str"), optional)
                fields.append(
                    EventField(
                        name=field_name,
                        source=field.get("source") or field["name"],
                        type_hint=type_hint,
                        base_type=base_type,
                    )
                )
            validation_fields = [normalize_field_name(f.get("field", "")) for f in spec.get("validation", []) if f.get("field")]
            if not validation_fields:
                validation_fields = [f.name for f in fields]
            class_defs.append(self._render_event_class(class_name, name, description, fields, validation_fields))

        events_block = ",\n    ".join(event_class_names)
        return (
            "from __future__ import annotations\n\n"
            "from pydantic import BaseModel\n\n"
            "from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event\n"
            "from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue\n\n" + "\n\n".join(class_defs) + f"\n\nEVENTS = [\n    {events_block}\n]\n"
        )

    def _render_event_class(
        self,
        class_name: str,
        event_name: str,
        description: str,
        fields: list[EventField],
        validation_fields: list[str],
    ) -> str:
        field_lines = [f"    {field.name}: {field.type_hint} = None" for field in fields]
        criteria_lines = [f"            self._validate_field(self.{field}, criteria.{field})," for field in validation_fields]
        parse_lines = [f"            {field.name}=data.get('{field.source}')," for field in fields]
        criteria_fields = "\n".join(f"        {field.name}: {field.base_type} | CriterionValue | None = None" for field in fields) or "        pass"
        validator_block = "        return all([\n" + "\n".join(criteria_lines) + "\n        ])" if criteria_lines else "        return True"
        parse_block = "\n".join(parse_lines) if parse_lines else ""

        return f'''class {class_name}(Event, BaseEventValidator):
    """{description or f"Event for {event_name}."}"""

    event_name: str = "{event_name}"
{chr(10).join(field_lines) if field_lines else "    pass"}

    class ValidationCriteria(BaseModel):
{criteria_fields}

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
{validator_block}

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "{class_name}":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {{}}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
{parse_block}
        )
'''

    def _render_generation_functions(self) -> str:
        lines = [
            "from __future__ import annotations",
            "",
            "from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator",
            "",
        ]
        has_function = False
        for uc in self.use_cases:
            constraints = uc.get("constraints") or {}
            examples = constraints.get("examples") or []
            if not examples:
                continue
            has_function = True
            func_name = f"generate_{snake_case(uc.get('name', 'use_case'))}_constraints"
            rows = []
            for item in examples:
                field = item.get("field")
                value = dump_python(item.get("value"))
                operator_key = (item.get("operator") or constraints.get("operator") or "equals").lower()
                operator_expr = OPERATOR_MAP.get(operator_key, "ComparisonOperator.EQUALS")
                rows.append(f"        {{'field': '{field}', 'operator': {operator_expr}, 'value': {value}}},")
            body = "\n".join(rows)
            lines.append(f"def {func_name}():")
            lines.append("    return [")
            lines.append(body)
            lines.append("    ]\n")

        if not has_function:
            lines.append("def placeholder_constraints():\n    return []\n")

        return "\n".join(lines)

    def _render_use_cases(self) -> str:
        lines = [
            "from __future__ import annotations",
            "",
            "from autoppia_iwa.src.demo_webs.classes import UseCase",
            "from autoppia_iwa.src.demo_webs.projects.base_events import Event",
            "from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator",
            "from .generation_functions import *  # noqa: F401,F403",
            "",
        ]
        uc_defs = []
        for uc in self.use_cases:
            event_name = uc.get("event")
            if not event_name:
                raise ConfigError(f"use_cases entry missing 'event': {uc}")
            event_class = f"{event_name}"
            template = {
                "name": uc.get("name", "USE_CASE").upper(),
                "description": uc.get("description", ""),
                "event": event_class,
                "event_source_code": uc.get("event_source_code", ""),
                "constraints": uc.get("constraints") or {},
                "examples": uc.get("examples") or [],
            }
            uc_defs.append(
                "UseCase(\n"
                f'    name="{template["name"]}",\n'
                f"    description={dump_python(template['description'])},\n"
                f"    event={template['event']},\n"
                f"    event_source_code={dump_python(template['event_source_code'])},\n"
                f"    examples={dump_python(template['examples'])},\n"
                ")\n"
            )
        lines.append("ALL_USE_CASES = [")
        lines.extend(f"    {uc_def}," for uc_def in uc_defs)
        lines.append("]\n")
        return "\n".join(lines)


def generate_module_from_config(config_path: Path, output_root: Path | None = None, force: bool = False) -> Path:
    config = load_config(config_path)
    target_dir = (output_root or PROJECTS_ROOT) / config["project"]["slug"]
    generator = ModuleGenerator(config, target_dir, force=force)
    generator.generate()
    return target_dir
