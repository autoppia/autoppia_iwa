from __future__ import annotations

from typing import Any

from pydantic import Field

from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.demo_webs.classes import BackendEvent

from ..instrumentation.js_events import JsEvent


class InstrumentedBrowserSnapshot(BrowserSnapshot):
    """Browser snapshot extended with runtime JS events."""

    js_events: list[JsEvent] = Field(default_factory=list, description="List of runtime events captured after the action")
    backend_events_before: list[BackendEvent] = Field(default_factory=list, description="Backend events observed prior to executing the action")
    html_diff: str | None = Field(default=None, description="Unified diff between previous and current HTML")

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:  # pragma: no cover - serialization helper
        data = super().model_dump(*args, **kwargs)
        data["js_events"] = [event.model_dump() for event in self.js_events]
        data["backend_events_before"] = [event.model_dump() for event in self.backend_events_before]
        return data
