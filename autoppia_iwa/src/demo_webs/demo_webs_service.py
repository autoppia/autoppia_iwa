from __future__ import annotations

import json
import os
from contextlib import suppress

import aiohttp
from loguru import logger

from autoppia_iwa.config.config import VALIDATOR_ID
from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject

EVALUATION_LEVEL_NAME = "EVALUATION"
EVALUATION_LEVEL_NO = 25


def _log_evaluation_event(message: str, context: str = "GENERAL") -> None:
    """Log generic evaluation events with INFO level."""

    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_evaluation_event

        log_evaluation_event(message, context=context)
    except ImportError:
        # Fallback to INFO level with EVALUATION tag
        if context == "GENERAL":
            logger.info(f"[EVALUATION] {message}")
        else:
            logger.info(f"[EVALUATION] [{context}] {message}")


def _log_backend_test(message: str, web_agent_id: str | None = None) -> None:
    """Helper function to log backend test messages with EVALUATION level."""

    agent_prefix = f"[agent={web_agent_id}] " if web_agent_id else ""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_backend_test

        log_backend_test(f"{agent_prefix}{message}")
    except ImportError:
        _log_evaluation_event(f"[GET BACKEND TEST] {agent_prefix}{message}", context="GET_BACKEND_TEST")


class BackendDemoWebService:
    """
    Service for interacting with the backend of demo web endpoints.

    Features:
    - Automatic JSON parser selection (orjson if available)
    - Thread-safe aiohttp session management
    - Error handling and logging
    - Support for both real and demo web projects
    """

    def __init__(self, web_project: WebProject, web_agent_id: str = "unknown_agent") -> None:
        self._session: aiohttp.ClientSession | None = None
        self.web_project = web_project
        self.base_url = web_project.backend_url
        self.web_agent_id = web_agent_id
        # Allow environment overrides for validator id to ease local testing
        self.validator_id = os.getenv("VALIDATOR_ID", VALIDATOR_ID or "validator_001")

        # Configure JSON parser (prefer orjson for performance)
        self._configure_json_parser()

    def _configure_json_parser(self) -> None:
        """Configure the JSON parser, preferring orjson if available."""

        self._json_parser = json
        self._json_decode_error = json.JSONDecodeError
        self._read_mode = "r"

        with suppress(ImportError):
            import orjson

            self._json_parser = orjson
            self._json_decode_error = orjson.JSONDecodeError  # type: ignore[attr-defined]
            self._read_mode = "rb"
            logger.debug("Using orjson for faster JSON processing")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy creation of aiohttp session, re-using it if open."""

        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(json_serialize=self._json_parser.dumps)
            logger.debug("Created new aiohttp session")
        return self._session

    async def close(self) -> None:
        """Close the underlying aiohttp session if it exists."""

        if self._session is not None:
            with suppress(Exception):
                await self._session.close()
            self._session = None
            logger.debug("Closed aiohttp session")

    async def get_backend_events(self, web_agent_id: str) -> list[BackendEvent]:
        """
        Get events for a specific web agent.

        Args:
            web_agent_id: The agent ID to get events for.
        """

        if self.web_project.is_web_real:
            return []

        try:
            endpoint = f"{DEMO_WEBS_ENDPOINT}:8090/get_events/"
            params = {"web_url": self.base_url, "web_agent_id": web_agent_id, "validator_id": VALIDATOR_ID}

            session = await self._get_session()

            async with session.get(endpoint, params=params) as response:
                response.raise_for_status()
                events_data = await response.json(loads=self._json_parser.loads)
                if not events_data:
                    print("No events received.")
                # print(events_data, [BackendEvent(**event.get("data", {})) for event in events_data])
                return [BackendEvent(**event.get("data", {})) for event in events_data]

        except Exception as e:
            logger.warning(f"Failed to get events from API: {e}. Falling back to file cache.")
            return []

    async def reset_database(self, override_url: str | None = None, web_agent_id: str | None = None) -> bool:
        """
        Reset the entire database (requires admin/superuser permissions).

        Args:
            override_url: Optional endpoint override (e.g., http://.../reset_db/).
            web_agent_id: Optional agent id; defaults to the instance's id.
        """

        _log_evaluation_event("Starting Reset Database", context="RESETTING DB")
        if self.web_project.is_web_real:
            _log_evaluation_event("Not resetting DB as it's a real website", context="RESETTING DB")
            return False

        try:
            endpoint = f"{DEMO_WEBS_ENDPOINT}:8090/reset_events/"
            params = {"web_url": self.base_url, "web_agent_id": web_agent_id or self.web_agent_id, "validator_id": VALIDATOR_ID}
            session = await self._get_session()

            async with session.delete(endpoint, params=params) as response:
                if response.status in (200, 202):
                    _log_evaluation_event("Database reset via API successful", context="RESETTING DB")
                    return True
        except Exception as e:
            logger.warning(f"API reset failed: {e}. Falling back to file reset.")
            return False
