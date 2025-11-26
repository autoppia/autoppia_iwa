from __future__ import annotations

import time
from typing import Any, Callable, Dict, List

from loguru import logger
from playwright.async_api import Page, Request, Response
from pydantic import BaseModel, Field


class JsEvent(BaseModel):
    """Normalized runtime event emitted by Playwright for instrumentation."""

    event_type: str = Field(..., description="Type of event, e.g., console/request/response")
    timestamp: float = Field(default_factory=lambda: time.time(), description="Unix timestamp when captured")
    data: Dict[str, Any] = Field(default_factory=dict, description="Lightweight payload for the event")


class JsEventCollector:
    """Attach listeners to a Playwright page and buffer runtime events by action."""

    def __init__(self, page: Page, max_buffer: int = 200):
        self._page = page
        self._max_buffer = max_buffer
        self._buffer: List[JsEvent] = []
        self._listeners: list[tuple[str, Callable]] = []
        self._setup_handlers()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def rollover(self) -> None:
        """Reset the buffer for the next action."""
        self._buffer = []

    def flush(self) -> list[JsEvent]:
        events = self._buffer
        self._buffer = []
        return events

    def dispose(self) -> None:
        for event_name, handler in self._listeners:
            try:
                self._page.off(event_name, handler)  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - best effort cleanup
                logger.debug("Failed to detach handler %s", event_name)
        self._listeners.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _setup_handlers(self) -> None:
        self._attach("console", self._on_console)
        self._attach("pageerror", self._on_page_error)
        self._attach("request", self._on_request)
        self._attach("response", self._on_response)
        self._attach("framenavigated", self._on_navigation)

    def _attach(self, event_name: str, handler: Callable) -> None:
        self._page.on(event_name, handler)
        self._listeners.append((event_name, handler))

    def _record(self, event_type: str, data: Dict[str, Any]) -> None:
        if len(self._buffer) >= self._max_buffer:
            self._buffer.pop(0)
        self._buffer.append(JsEvent(event_type=event_type, data=data))

    # Event callbacks ---------------------------------------------------
    def _on_console(self, msg) -> None:
        try:
            self._record(
                "console",
                {
                    "text": msg.text,
                    "type": msg.type,
                    "location": getattr(msg, "location", None),
                },
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Console hook failed: %s", exc)

    def _on_page_error(self, error) -> None:
        self._record("pageerror", {"message": str(error)})

    def _on_navigation(self, frame) -> None:
        try:
            self._record("navigation", {"url": frame.url})
        except Exception as exc:
            logger.debug("Navigation hook failed: %s", exc)

    def _on_request(self, request: Request) -> None:
        self._record(
            "request",
            {
                "method": request.method,
                "url": request.url,
                "resource_type": request.resource_type,
            },
        )

    def _on_response(self, response: Response) -> None:
        try:
            self._record(
                "response",
                {
                    "status": response.status,
                    "url": response.url,
                    "ok": response.ok,
                },
            )
        except Exception as exc:
            logger.debug("Response hook failed: %s", exc)
