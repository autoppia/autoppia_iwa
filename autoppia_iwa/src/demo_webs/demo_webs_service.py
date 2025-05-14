import contextlib
import fcntl
import json
import time
from typing import Any

import aiohttp
from aiohttp.client_exceptions import ClientError
from loguru import logger

from autoppia_iwa.config.config import WEB_3_AUTOZONE_JSON_FILEPATH
from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject


class BackendDemoWebService:
    """
    Service for interacting with the backend of demo web endpoints.
    Stores the web_project on initialization and uses its backend_url for API calls.
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

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Lazy creation of aiohttp session, re-using it if open.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """
        Explicitly close the underlying aiohttp session if it's still open.
        Recommended to call once on application shutdown.
        """
        if self._session and not self._session.closed:
            try:
                await self._session.close()
                self._session = None
                logger.debug("Session closed successfully")
            except Exception as e:
                logger.error(f"Error closing session: {e}")

    def __del__(self):
        """Warn if the session was not closed."""
        if self._session and not self._session.closed:
            print("Warning: Unclosed ClientSession detected. Please call `close()` explicitly.")

    async def get_backend_events(self, web_agent_id: str) -> list[BackendEvent]:
        """
        Fetch recent events from either a JSON file (for non-real projects) or return empty list (for real projects).
        Filters events to only those matching the specified web_agent_id.

        Args:
            web_agent_id (str): ID of the web agent to filter events for.

        Returns:
            List[BackendEvent]: List of filtered events or an empty list if any failure occurs.
        """
        if self.web_project.is_web_real:
            return []
        if ":8002" in self.base_url:
            if not WEB_3_AUTOZONE_JSON_FILEPATH:
                logger.error("JSON file path not configured in environment variables")
                return []

            try:
                with open(WEB_3_AUTOZONE_JSON_FILEPATH) as f:
                    with contextlib.suppress(ImportError, ModuleNotFoundError):
                        fcntl.flock(f, fcntl.LOCK_SH)

                    try:
                        events_data = json.load(f)
                    finally:
                        with contextlib.suppress(NameError):
                            fcntl.flock(f, fcntl.LOCK_UN)

                filtered_events = [BackendEvent(**event) for event in events_data if event.get("web_agent_id") == web_agent_id]

                return filtered_events

            except FileNotFoundError:
                logger.warning(f"Events file not found at {WEB_3_AUTOZONE_JSON_FILEPATH}")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from {WEB_3_AUTOZONE_JSON_FILEPATH}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error reading events from file: {e}")
        try:
            endpoint = f"{self.base_url}events/list/"
            headers = {"X-WebAgent-Id": web_agent_id}
            session = await self._get_session()
            async with session.get(endpoint, headers=headers) as response:
                response.raise_for_status()  # Raise on 4xx/5xx
                events_data = await response.json()
                print(events_data, [BackendEvent(**event) for event in events_data])
                return [BackendEvent(**event) for event in events_data]
        except ClientError as e:
            logger.error(f"Network error while fetching backend events: {e}")
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
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

        try:
            session = await self._get_session()
            async with session.delete(endpoint, headers=headers, timeout=10) as response:
                # Try to parse the body for a success message
                try:
                    response_json = await response.json()
                    msg = response_json.get("message", "")
                    if "have been deleted successfully" in msg:
                        logger.info(f"Successfully reset events for web_agent '{web_agent_id}'.")
                        return True
                except Exception:
                    # Fall back to standard checks below
                    pass

                # Raise on status >= 400
                response.raise_for_status()

                if response.status in (200, 204):
                    logger.info(f"Successfully reset events for web_agent '{web_agent_id}'.")
                    return True
                else:
                    logger.warning(f"Reset operation completed with unexpected status: {response.status}")
                    return True

        except ClientError as e:
            # If the error message itself indicates success, handle it
            if "have been deleted successfully" in str(e):
                logger.info(f"Successfully reset events for web_agent '{web_agent_id}' despite error.")
                return True

            error_message = f"Failed to reset events for web_agent '{web_agent_id}': {e}"
            logger.error(error_message)
            return False

        except Exception as e:
            logger.error(f"Unexpected error resetting events: {e}")
            return False

        finally:
            if session:
                await session.close()

    async def reset_all_events(self) -> bool:
        """
        Resets all events in the system regardless of user/web_agent.

        Returns:
            bool: True if reset was successful, False otherwise.
        """
        if self.web_project.is_web_real:
            return False

        endpoint = f"{self.base_url}events/reset/all/"

        try:
            session = await self._get_session()
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
        start_time = time.time()
        if self.web_project.is_web_real:
            logger.info("Not resetting DB as its real website")
            return False

        # Handle port 8002 case - reset JSON file instead of making API call
        if ":8002" in self.base_url:
            if not WEB_3_AUTOZONE_JSON_FILEPATH:
                logger.error("JSON file path not configured in environment variables")
                return False

            try:
                # Acquire exclusive lock and clear the file
                with open(WEB_3_AUTOZONE_JSON_FILEPATH, "w") as f:
                    with contextlib.suppress(ImportError, ModuleNotFoundError):
                        fcntl.flock(f, fcntl.LOCK_EX)

                    json.dump([], f)

                    with contextlib.suppress(NameError):
                        fcntl.flock(f, fcntl.LOCK_UN)

                logger.info(f"Successfully cleared events from JSON file at {WEB_3_AUTOZONE_JSON_FILEPATH}")
                return True

            except Exception as e:
                logger.error(f"Failed to reset JSON file database: {e}")
                return False

        # Original API reset behavior for other ports
        endpoint = override_url or f"{self.base_url}management_admin/reset_db/"

        try:
            session = await self._get_session()
            async with session.post(endpoint, timeout=30) as response:
                response.raise_for_status()

                try:
                    response_json = await response.json()
                    status = response_json.get("status")
                    message = response_json.get("message", "")

                    if status == "success":
                        logger.info(f"Database reset initiated: {message}. Lasted: {time.time() - start_time}")
                        return True
                    else:
                        logger.warning(f"Database reset failed: {message} Lasted: {time.time() - start_time}")
                        return False

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
