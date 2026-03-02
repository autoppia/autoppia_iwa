from __future__ import annotations

import ast
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from types import ModuleType

from autoppia_iwa.src.demo_webs.classes import WebProject
from modules.dynamic_proxy.core.palette import MutationPalette

CONFIG_PATH = Path(__file__).resolve().parents[3] / "autoppia_iwa" / "src" / "demo_webs" / "config.py"
PROJECTS_PACKAGE = "autoppia_iwa.src.demo_webs.projects"


@lru_cache(maxsize=1)
def _attr_slug_map() -> dict[str, str]:
    source = CONFIG_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    mapping: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.lstrip(".").startswith("projects"):
            module_path = node.module.lstrip(".")
            parts = module_path.split(".")
            if len(parts) < 2:
                continue
            slug = parts[1]
            for alias in node.names:
                mapping[alias.asname or alias.name] = slug
    return mapping


@lru_cache(maxsize=1)
def project_slug_map() -> dict[str, str]:
    from autoppia_iwa.src.demo_webs import config

    attr_to_slug = _attr_slug_map()
    mapping: dict[str, str] = {}
    for attr_name, slug in attr_to_slug.items():
        project_obj = getattr(config, attr_name, None)
        if isinstance(project_obj, WebProject):
            mapping[project_obj.id] = slug
    return mapping


def load_palette_from_module(project_id: str) -> MutationPalette | None:
    slug = project_slug_map().get(project_id)
    if not slug:
        return None
    try:
        module: ModuleType = import_module(f"{PROJECTS_PACKAGE}.{slug}.mutations")
    except ModuleNotFoundError:
        return None
    palette = getattr(module, "palette", None)
    if isinstance(palette, MutationPalette):
        return palette
    data = getattr(module, "PALETTE_DATA", None)
    if data:
        try:
            return MutationPalette.model_validate(data)
        except Exception:
            return None
    return None


__all__ = ["load_palette_from_module", "project_slug_map"]
