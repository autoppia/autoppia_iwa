from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class DeckDeploymentProfile(BaseModel):
    preview_base_url: str | None = Field(default=None, description="URL base para verificaciones locales/sandbox")
    notes: str | None = None


class DeckMetadata(BaseModel):
    project_id: str
    project_name: str
    summary: str | None = None
    owner: str | None = None
    deck_contact: str | None = None
    deployment: DeckDeploymentProfile | None = None


class DeckDynamicProfile(BaseModel):
    html_mutates: bool = Field(default=False, description="D1: estructura del DOM varía con seed")
    data_mutates: bool = Field(default=False, description="D2: datasets/respuestas cambian con seed")
    ui_identifiers_mutate: bool = Field(default=False, description="D3: IDs/classes/textos varían")
    seed_notes: str | None = None


class DeckRequiredElement(BaseModel):
    selector: str | None = Field(default=None, description="CSS selector para localizar el elemento")
    text_contains: str | None = Field(default=None, description="Fragmento de texto que debe existir")
    description: str | None = None

    def describe(self) -> str:
        if self.selector and self.text_contains:
            return f"{self.selector} (text~={self.text_contains})"
        if self.selector:
            return self.selector
        if self.text_contains:
            return f"text~={self.text_contains}"
        return "unspecified element"


class DeckPage(BaseModel):
    id: str
    title: str
    description: str | None = None
    url_patterns: list[str] = Field(default_factory=list)
    required_elements: list[DeckRequiredElement] = Field(default_factory=list)
    optional_elements: list[DeckRequiredElement] = Field(default_factory=list)


class DeckUseCase(BaseModel):
    name: str
    event: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    critical: bool = False


class DeckTasksPolicy(BaseModel):
    min_examples_per_use_case: int | None = None
    recommended_difficulty_curve: list[str] = Field(default_factory=list)
    notes: str | None = None


class WebProjectDeck(BaseModel):
    version: str
    metadata: DeckMetadata
    dynamic_profile: DeckDynamicProfile
    use_cases: list[DeckUseCase]
    pages: list[DeckPage]
    tasks_policy: DeckTasksPolicy | None = None

    @staticmethod
    def load(path: Path) -> "WebProjectDeck":
        data = path.read_text()
        try:
            import json

            raw: Any = json.loads(data)
        except Exception as exc:
            raise ValueError(f"Failed to parse deck JSON '{path}': {exc}") from exc
        try:
            return WebProjectDeck.model_validate(raw)
        except ValidationError as exc:  # pragma: no cover - validation errors bubble up
            raise ValueError(f"Deck '{path}' is invalid: {exc}") from exc
