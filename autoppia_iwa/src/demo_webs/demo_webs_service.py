import json
import os
import time
from contextlib import suppress
from typing import Any

import aiohttp
from aiohttp.client_exceptions import ClientError
from loguru import logger

from autoppia_iwa.config.config import WEB_3_AUTOZONE_JSON_FILEPATH
from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject


class BackendDemoWebService:
    """
    Service for interacting with the backend of demo web endpoints.
    Manages API calls, JSON file caching, and event operations efficiently.

    Features:
    - Automatic JSON parser selection (orjson if available, falls back to standard json)
    - Caching mechanism for JSON file data with invalidation on file changes
    - Thread-safe operations with proper resource cleanup
    - Comprehensive error handling and logging
    - Support for both real and demo web projects

    Usage:
    async with BackendDemoWebService(web_project) as service:
        events = await service.get_backend_events("agent123")
    """

    def __init__(self, web_project: WebProject) -> None:
        """
        Initialize a single aiohttp session holder and store the web_project.

        Args:
            web_project: The web project containing the backend_url to use
        """
        self._session: aiohttp.ClientSession | None = None
        self.web_project: WebProject = web_project
        self.base_url = web_project.backend_url

        # Cache attributes for port 8002 JSON data
        self._cached_json_data_8002: list[dict[str, Any]] | None = None
        self._indexed_events_8002: dict[str, list[BackendEvent]] | None = None
        self._cached_json_file_mtime_8002: float | None = None

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
            self._json_decode_error = orjson.JSONDecodeError  # type: ignore
            self._read_mode = "rb"
            logger.debug("Using orjson for faster JSON processing")

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Lazy creation of aiohttp session, re-using it if open.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(json_serialize=self._json_parser.dumps)
            logger.debug("Created new aiohttp session")
        return self._session

    async def close(self) -> None:
        """
        Close the underlying aiohttp session if it exists.
        Safe to call multiple times.
        """
        if self._session is not None:
            with suppress(Exception):
                await self._session.close()
                self._session = None
                logger.debug("Closed aiohttp session")

    def _invalidate_json_cache_8002(self) -> None:
        """Invalidate the cache for port 8002/8003 JSON data."""
        logger.debug("Invalidating JSON cache for port 8002/8003")
        self._cached_json_data_8002 = None
        self._indexed_events_8002 = None
        self._cached_json_file_mtime_8002 = None

    async def _load_and_cache_json_8002(self) -> bool:
        """
        Load and cache JSON data from file for ports 8002/8003.

        Returns:
            bool: True if loading was successful, False otherwise
        """
        if not WEB_3_AUTOZONE_JSON_FILEPATH:
            logger.error("JSON file path not configured")
            return False

        try:
            current_mtime = os.path.getmtime(WEB_3_AUTOZONE_JSON_FILEPATH)
            if self._cached_json_file_mtime_8002 == current_mtime and self._indexed_events_8002 is not None:
                logger.debug("JSON cache is up-to-date")
                return True

            logger.info(f"Loading JSON data from {WEB_3_AUTOZONE_JSON_FILEPATH}")
            with open(WEB_3_AUTOZONE_JSON_FILEPATH, self._read_mode) as f:
                raw_data = self._json_parser.loads(f.read())

            if not isinstance(raw_data, list):
                logger.error("JSON data is not a list")
                self._invalidate_json_cache_8002()
                return False

            # Process and index the data
            indexed_events: dict[str, list[BackendEvent]] = {}
            valid_events = 0
            invalid_events = 0

            for event_dict in raw_data:
                if not isinstance(event_dict, dict):
                    invalid_events += 1
                    continue

                agent_id = event_dict.get("web_agent_id")
                if agent_id is None:
                    invalid_events += 1
                    continue

                try:
                    event = BackendEvent(**event_dict)
                    indexed_events.setdefault(agent_id, []).append(event)
                    valid_events += 1
                except Exception as e:
                    logger.warning(f"Invalid event data: {e}")
                    invalid_events += 1

            # Update cache
            self._cached_json_data_8002 = raw_data
            self._indexed_events_8002 = indexed_events
            self._cached_json_file_mtime_8002 = current_mtime

            logger.info(f"Loaded {valid_events} valid events for {len(indexed_events)} agents. Skipped {invalid_events} invalid entries.")
            return True

        except FileNotFoundError:
            logger.warning(f"JSON file not found: {WEB_3_AUTOZONE_JSON_FILEPATH}")
            self._invalidate_json_cache_8002()
            return False
        except self._json_decode_error as e:
            logger.error(f"JSON parsing error: {e}")
            self._invalidate_json_cache_8002()
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading JSON: {e}")
            self._invalidate_json_cache_8002()
            return False

    async def get_backend_events(self, web_agent_id: str) -> list[BackendEvent]:
        """
        Get events for a specific web agent.

        Args:
            web_agent_id: The agent ID to get events for

        Returns:
            List of BackendEvent objects for the specified agent
        """
        if self.web_project.is_web_real:
            return []

        if ":8002" in self.base_url or ":8003" in self.base_url:
            # Option 1: Use local API endpoint
            try:
                endpoint = "http://localhost:8080/get_events/"
                params = {"web_url": self.base_url, "web_agent_id": web_agent_id}
                session = await self._get_session()

                async with session.get(endpoint, params=params) as response:
                    response.raise_for_status()
                    events_data = await response.json(loads=self._json_parser.loads)
                    return [BackendEvent(**event.get("data", {})) for event in events_data]

            except Exception as e:
                logger.warning(f"Failed to get events from API: {e}. Falling back to file cache.")

            # Option 2: Fall back to file cache
            if await self._load_and_cache_json_8002() and self._indexed_events_8002:
                return self._indexed_events_8002.get(web_agent_id, [])
            return []

        # Standard endpoint for other ports
        try:
            endpoint = f"{self.base_url}events/list/"
            headers = {"X-WebAgent-Id": web_agent_id}
            session = await self._get_session()

            async with session.get(endpoint, headers=headers) as response:
                response.raise_for_status()  # Raise on 4xx/5xx
                events_data = await response.json(loads=self._json_parser.loads)  # Can specify custom decoder
                print(events_data, [BackendEvent(**event) for event in events_data])
                return [BackendEvent(**event) for event in events_data]
        except ClientError as e:
            logger.error(f"Network error while fetching backend events: {e}")
        except self._json_decode_error as e:
            logger.error(f"Error parsing JSON response from network: {e}")
        except ValueError as e:
            logger.error(f"Error parsing JSON response (ValueError): {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching backend events: {e}")
        return []

    async def reset_web_agent_events(self, web_agent_id: str) -> bool:
        """
        Resets events for a specific user/web_agent.

        Args:
            web_agent_id (str): Identifier for the web_agent.

        Returns:
            bool: True if reset was successful, False otherwise.
        """
        if self.web_project.is_web_real:
            return False

        endpoint = f"{self.base_url}events/reset/"
        headers = {"X-WebAgent-Id": web_agent_id}
        session = await self._get_session()

        try:
            async with session.delete(endpoint, headers=headers, timeout=10) as response:
                if response.status in (200, 204):
                    logger.info(f"Successfully reset events for web_agent '{web_agent_id}'. Status: {response.status}")
                    return True

                try:
                    response_json = await response.json(loads=self._json_parser.loads)
                    msg = response_json.get("message", "")
                    if "have been deleted successfully" in msg.lower():
                        logger.info(f"Backend confirmed successful reset for '{web_agent_id}' (via message). Status: {response.status}")
                        return True
                    else:
                        logger.error(f"Reset operation returned non-success status {response.status} with message: '{msg}'")

                except Exception as json_parse_error:
                    logger.error(f"Reset operation failed for '{web_agent_id}'. Status: {response.status}. Could not parse JSON response body: {json_parse_error}")

                response.raise_for_status()
        except ClientError as e:
            logger.error(f"Network or HTTP error resetting events for web_agent '{web_agent_id}' at {endpoint}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error resetting events for web_agent '{web_agent_id}': {e}")

        return False

    async def reset_all_events(self) -> bool:
        """
        Resets all events in the system regardless of user/web_agent.

        Returns:
            bool: True if reset was successful, False otherwise.
        """
        if self.web_project.is_web_real:
            return False

        endpoint = f"{self.base_url}events/reset/all/"
        session = await self._get_session()

        try:
            async with session.delete(endpoint, timeout=10) as response:
                response.raise_for_status()

                if response.status in (200, 204):
                    logger.info("Successfully reset all events.")
                    return True
                else:
                    logger.warning(f"Reset all events operation completed with unexpected status: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Failed to reset all events: {e}")
            return False
        finally:
            if session:
                await session.close()

    async def reset_database(self, override_url: str | None = None) -> bool:
        """
        Resets the entire database (requires admin/superuser permissions).

        Args:
            override_url (Optional[str]): If provided, use this full endpoint URL
                (e.g., 'http://localhost:5435/management_admin/reset_db/')
                instead of self.base_url.

        Returns:
            bool: True if reset was successful, False otherwise.
        """
        logger.info("Starting Reset Database")
        time.time()
        if self.web_project.is_web_real:
            logger.info("Not resetting DB as its real website")
            return False

        # Handle port 8002 case - reset JSON file instead of making API call
        if ":8002" in self.base_url or ":8003" in self.base_url:
            # Option 1: Use local API endpoint
            try:
                endpoint = "http://localhost:8080/reset_events/"
                params = {"web_url": self.base_url}
                session = await self._get_session()

                async with session.delete(endpoint, params=params) as response:
                    if response.status in (200, 202):
                        logger.info("Database reset via API successful")
                        return True
            except Exception as e:
                logger.warning(f"API reset failed: {e}. Falling back to file reset.")

            # Option 2: Reset JSON file directly
            if not WEB_3_AUTOZONE_JSON_FILEPATH:
                logger.error("No JSON file path configured")
                return False

            try:
                with open(WEB_3_AUTOZONE_JSON_FILEPATH, "w") as f:
                    f.write("[]")
                self._invalidate_json_cache_8002()
                logger.info("Reset JSON file successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to reset JSON file database: {e}")
                return False

        # Original API reset behavior for other ports
        endpoint = override_url or f"{self.base_url}management_admin/reset_db/"
        session = await self._get_session()  # Re-use session
        try:
            async with session.post(endpoint, timeout=30) as response:
                response.raise_for_status()

                try:
                    response_data = await response.json(loads=self._json_parser.loads)
                    if response_data.get("status") == "success":
                        logger.info(f"Database reset: {response_data.get('message')}")
                        return True
                except Exception:
                    # If we can't parse JSON, check status code
                    if response.status in (200, 202):
                        logger.info("Database reset initiated successfully.")
                        return True
                    else:
                        logger.warning(f"Database reset completed with unexpected status: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
        finally:
            if session:
                await session.close()

    async def send_event(self, event_name: str, data: dict[str, Any], web_agent_id: str) -> bool:
        """
        Sends an event to the backend for a given web_agent_id.

        Args:
            event_name (str): Type of the event (e.g., "page_view", "button_click")
            data (Dict[str, Any]): Additional data related to the event
            web_agent_id (str): The ID of the web agent

        Returns:
            bool: True if the event was sent successfully, False otherwise.
        """
        if self.web_project.is_web_real:
            return False

        payload = {
            "event_name": event_name,
            "data": data,
            "web_agent_id": web_agent_id,
        }

        endpoint = f"{self.base_url}events/add/"
        headers = {"X-WebAgent-Id": web_agent_id}

        try:
            session = await self._get_session()
            async with session.post(endpoint, json=payload, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return True

        except ClientError as e:
            logger.error(f"Failed to send {event_name} event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while sending {event_name} event: {e}")

        return False
