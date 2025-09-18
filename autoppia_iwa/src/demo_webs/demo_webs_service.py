import json
from contextlib import suppress
from typing import Any

import aiohttp
from aiohttp.client_exceptions import ClientError
from loguru import logger

from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject


class BackendDemoWebService:
    """
    Service for interacting with the backend of demo web endpoints.
    Manages API calls and event operations efficiently.

    Features:
    - Automatic JSON parser selection (orjson if available)
    - Thread-safe aiohttp session management
    - Error handling and logging
    - Support for both real and demo web projects
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

    def _should_use_proxy_api(self) -> bool:
        """
        Determines whether the proxy API (e.g., port 80002, 8003, 8004 ...) should be used based on the base_url port.
        """
        from urllib.parse import urlparse

        parsed = urlparse(self.base_url)
        return bool(parsed.port and parsed.port > 8001)

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

        if self._should_use_proxy_api():
            try:
                endpoint = "http://localhost:8090/get_events/"
                params = {"web_url": self.base_url, "web_agent_id": web_agent_id}

                session = await self._get_session()

                async with session.get(endpoint, params=params) as response:
                    response.raise_for_status()
                    events_data = await response.json(loads=self._json_parser.loads)
                    print(events_data, [BackendEvent(**event.get("data", {})) for event in events_data])
                    return [BackendEvent(**event.get("data", {})) for event in events_data]

            except Exception as e:
                logger.warning(f"Failed to get events from API: {e}. Falling back to file cache.")

        try:
            endpoint = f"{self.base_url}events/list/"
            headers = {"X-WebAgent-Id": web_agent_id}
            session = await self._get_session()

            async with session.get(endpoint, headers=headers) as response:
                response.raise_for_status()  # Raise on 4xx/5xx
                events_data = await response.json(loads=self._json_parser.loads)
                logger.info(f"FETCH events for {web_agent_id}: {len(events_data)} encontrados")

                # print(events_data, [BackendEvent(**event) for event in events_data])
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
        if self.web_project.is_web_real:
            logger.info("Not resetting DB as its real website")
            return False

        if self._should_use_proxy_api():
            try:
                endpoint = "http://localhost:8090/reset_events/"
                params = {"web_url": self.base_url}
                session = await self._get_session()

                async with session.delete(endpoint, params=params) as response:
                    if response.status in (200, 202):
                        logger.info("Database reset via API successful")
                        return True
            except Exception as e:
                logger.warning(f"API reset failed: {e}. Falling back to file reset.")

        endpoint = override_url or f"{self.base_url}management_admin/reset_db/"
        session = await self._get_session()
        try:
            async with session.post(endpoint, timeout=30) as response:
                response.raise_for_status()

                try:
                    response_data = await response.json(loads=self._json_parser.loads)
                    if response_data.get("status") == "success":
                        logger.info(f"Database reset: {response_data.get('message')}")
                        return True
                except Exception:
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
            logger.error(f"Unexpected error sending {event_name} event: {e}")
        return False
