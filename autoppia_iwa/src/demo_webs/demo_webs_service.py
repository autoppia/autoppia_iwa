from __future__ import annotations

import json
import os
from contextlib import suppress
from typing import Any
from urllib.parse import urlparse

import aiohttp
from aiohttp.client_exceptions import ClientError
from loguru import logger

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, VALIDATOR_ID
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
        self._backend_port = self._extract_backend_port()
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

    def _extract_backend_port(self) -> int | None:
        parsed = urlparse(self.base_url)
        return parsed.port

    def _should_use_proxy_api(self) -> bool:
        """Determine whether we should proxy backend calls via the shared webs_server."""

        return bool(self._backend_port and self._backend_port == DEMO_WEB_SERVICE_PORT)

    def _proxy_base_url(self) -> str:
        return self.base_url.rstrip("/")

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

        validator_id = self.validator_id

        if self._should_use_proxy_api():
            try:
                endpoint = f"{self._proxy_base_url()}/get_events/"
                params = {
                    "web_url": self.base_url.rstrip("/"),
                    "web_agent_id": web_agent_id,
                    "validator_id": validator_id,
                }

                session = await self._get_session()
                async with session.get(endpoint, params=params) as response:
                    response.raise_for_status()
                    events_data = await response.json(loads=self._json_parser.loads)
                    return [BackendEvent(**event.get("data", {})) for event in events_data]

            except Exception as exc:
                logger.warning("Failed to get events from proxy API (%s). Falling back to backend.", exc)

        try:
            endpoint = f"{self.base_url}events/list/"
            headers = {"X-WebAgent-Id": web_agent_id, "X-Validator-Id": validator_id}
            session = await self._get_session()

            async with session.get(endpoint, headers=headers) as response:
                response.raise_for_status()
                events_data = await response.json(loads=self._json_parser.loads)
                _log_backend_test(f"FETCH events: {len(events_data)} encontrados", web_agent_id=web_agent_id)
                return [BackendEvent(**event) for event in events_data]
        except ClientError as exc:
            logger.error(f"Network error while fetching backend events: {exc}")
        except self._json_decode_error as exc:
            logger.error(f"Error parsing JSON response from network: {exc}")
        except ValueError as exc:
            logger.error(f"Error parsing JSON response (ValueError): {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error fetching backend events: {exc}")
        return []

    async def reset_web_agent_events(self, web_agent_id: str) -> bool:
        """Reset events for a specific user/web_agent."""

        if self.web_project.is_web_real:
            return False

        endpoint = f"{self.base_url}events/reset/"
        headers = {"X-WebAgent-Id": web_agent_id, "X-Validator-Id": self.validator_id}
        session = await self._get_session()

        try:
            async with session.delete(endpoint, headers=headers, timeout=10) as response:
                if response.status in (200, 204):
                    _log_evaluation_event(
                        f"Successfully reset events for web_agent '{web_agent_id}'. Status: {response.status}",
                        context="EVENTS_RESET",
                    )
                    return True

                try:
                    response_json = await response.json(loads=self._json_parser.loads)
                    msg = response_json.get("message", "")
                    if "have been deleted successfully" in msg.lower():
                        _log_evaluation_event(
                            f"Backend confirmed successful reset for '{web_agent_id}' (via message). Status: {response.status}",
                            context="EVENTS_RESET",
                        )
                        return True
                    logger.error(
                        f"Reset operation returned non-success status {response.status} with message: '{msg}'",
                    )
                except Exception as json_parse_error:
                    logger.error(
                        f"Reset operation failed for '{web_agent_id}'. Status: {response.status}. "
                        f"Could not parse JSON response body: {json_parse_error}",
                    )

        except ClientError as exc:
            logger.error(f"Network error resetting events for '{web_agent_id}' at {endpoint}: {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error resetting events for '{web_agent_id}': {exc}")

        return False

    async def reset_all_events(self) -> bool:
        """Reset all events in the system regardless of user/web_agent."""

        if self.web_project.is_web_real:
            return False

        endpoint = f"{self.base_url}events/reset/all/"
        session = await self._get_session()

        try:
            async with session.delete(endpoint, headers={"X-Validator-Id": self.validator_id}, timeout=10) as response:
                response.raise_for_status()
                if response.status in (200, 204):
                    _log_evaluation_event("Successfully reset all events.", context="EVENTS_RESET")
                    return True
                logger.warning(f"Reset all events completed with unexpected status: {response.status}")
        except Exception as exc:
            logger.error(f"Failed to reset all events: {exc}")
        return False

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

        agent_id = web_agent_id or self.web_agent_id
        validator_id = self.validator_id

        if self._should_use_proxy_api():
            try:
                endpoint = f"{self._proxy_base_url()}/reset_events/"
                params = {
                    "web_url": self.base_url.rstrip("/"),
                    "web_agent_id": agent_id,
                    "validator_id": validator_id,
                }
                session = await self._get_session()

                async with session.delete(endpoint, params=params) as response:
                    if response.status in (200, 202):
                        _log_evaluation_event("Database reset via proxy API successful", context="RESETTING DB")
                        return True
            except Exception as exc:
                logger.warning("Proxy API reset failed (%s). Falling back to backend reset.", exc)

        endpoint = override_url or f"{self.base_url}management_admin/reset_db/"
        headers = {"X-WebAgent-Id": agent_id, "X-Validator-Id": validator_id}
        session = await self._get_session()

        try:
            async with session.post(endpoint, headers=headers, timeout=30) as response:
                response.raise_for_status()
                try:
                    response_data = await response.json(loads=self._json_parser.loads)
                except Exception:
                    response_data = None

                if isinstance(response_data, dict) and response_data.get("status") == "success":
                    _log_evaluation_event(
                        f"Database reset: {response_data.get('message')}",
                        context="RESETTING DB",
                    )
                    return True

                if response.status in (200, 202):
                    _log_evaluation_event("Database reset initiated successfully.", context="RESETTING DB")
                    return True

                logger.warning(f"Database reset completed with unexpected status: {response.status}")
        except Exception as exc:
            logger.error(f"Failed to reset database: {exc}")
        return False

    async def send_event(self, event_name: str, data: dict[str, Any], web_agent_id: str) -> bool:
        """Send an event to the backend for a given web_agent_id."""

        if self.web_project.is_web_real:
            return False

        payload = {
            "event_name": event_name,
            "data": data,
            "web_agent_id": web_agent_id,
            "validator_id": self.validator_id,
        }

        endpoint = f"{self.base_url}events/add/"
        headers = {"X-WebAgent-Id": web_agent_id, "X-Validator-Id": self.validator_id}

        try:
            session = await self._get_session()
            async with session.post(endpoint, json=payload, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return True
        except ClientError as exc:
            logger.error(f"Failed to send event '{event_name}': {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error sending event '{event_name}': {exc}")
        return False
