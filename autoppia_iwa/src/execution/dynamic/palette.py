from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, validator


class MutationTemplate(BaseModel):
    """Single mutation template generated offline for a project."""

    id: str
    phase: Literal["d1", "d3", "d4"]
    selector: str = Field(..., description="CSS selector this template applies to")
    operation: str = Field(..., description="Mutation verb (insert_after, append_class, etc.)")
    html: str | None = Field(default=None, description="Optional HTML payload for D1 operations")
    attribute: str | None = None
    value: str | None = None
    text: str | None = None
    new_name: str | None = None
    url_pattern: str | None = Field(default=None, description="Path prefix filter (e.g., /products)")
    weight: float = 1.0
    overlay_type: Literal["modal", "banner", "cookie"] | None = None
    blocking: bool = False
    dismiss_selector: str | None = None
    trigger_after: int | None = None

    @validator("weight")
    def _validate_weight(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("weight must be > 0")
        return value

    def matches_url(self, url: str) -> bool:
        if not self.url_pattern:
            return True
        path = urlsplit(url).path or "/"
        return path.startswith(self.url_pattern)

    def render_payload(self, seed: int) -> dict:
        """Translate template into runtime instruction payload."""

        def _subst(value: str | None) -> str | None:
            if value is None:
                return None
            return value.replace("{{seed}}", str(seed))

        if self.phase == "d4":
            html = _subst(self.html)
            trigger_after = self.trigger_after if isinstance(self.trigger_after, int) else None
            return {
                "html": html or "",
                "overlay_type": self.overlay_type or "modal",
                "blocking": self.blocking,
                "dismiss_selector": self.dismiss_selector,
                "trigger_after": trigger_after or "random",
            }

        payload: dict[str, str] = {"id": self.id, "target": self.selector, "operation": self.operation}
        html = _subst(self.html)
        if html:
            payload["html"] = html
        attribute = _subst(self.attribute)
        if attribute:
            payload["attribute"] = attribute
        value = _subst(self.value)
        if value:
            payload["value"] = value
        text = _subst(self.text)
        if text:
            payload["text"] = text
        new_name = _subst(self.new_name)
        if new_name:
            payload["new_name"] = new_name
        return payload


class MutationPalette(BaseModel):
    """Project-wide palette that can be reused across seeds without extra LLM calls."""

    project_id: str
    version: str = Field(default="v1")
    generated_by: str | None = None
    templates: list[MutationTemplate]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.model_dump(mode="json")
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "MutationPalette":
        return MutationPalette.model_validate_json(path.read_text(encoding="utf-8"))


@dataclass
class PalettePlanGenerator:
    palette: MutationPalette
    seed: int
    max_per_phase: int = 3
    random_seed: int | None = None

    def _rng_for(self, url: str, phase: str) -> random.Random:
        seed_value = self.random_seed if self.random_seed is not None else self.seed
        key = f"{seed_value}:{phase}:{url}"
        return random.Random(key)

    def build_plan(self, url: str) -> dict:
        d1 = self._sample_templates(url, phase="d1")
        d3 = self._sample_templates(url, phase="d3")
        d4 = self._sample_templates(url, phase="d4")
        return {
            "d1": [template.render_payload(self.seed) for template in d1],
            "d3": [template.render_payload(self.seed) for template in d3],
            "d4": [template.render_payload(self.seed) for template in d4],
        }

    def _sample_templates(self, url: str, phase: Literal["d1", "d3"]) -> list[MutationTemplate]:
        candidates = [t for t in self.palette.templates if t.phase == phase and t.matches_url(url)]
        if not candidates:
            return []
        rng = self._rng_for(url, phase)
        weighted = list(candidates)
        rng.shuffle(weighted)
        return weighted[: self.max_per_phase]


def load_palette_for_project(project_id: str, palette_dir: Path | None) -> MutationPalette | None:
    if not palette_dir:
        return None
    path = palette_dir / f"{project_id}.json"
    if not path.exists():
        return None
    return MutationPalette.load(path)


__all__ = ["MutationPalette", "MutationTemplate", "PalettePlanGenerator", "load_palette_for_project"]
