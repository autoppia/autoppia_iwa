import json
import os
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

        # Cache attributes for port 8002 JSON data
        self._cached_json_data_8002: list[dict[str, Any]] | None = None
        self._indexed_events_8002: dict[str, list[BackendEvent]] | None = None
        self._cached_json_file_mtime_8002: float | None = None

        self._json_parser = json
        self._json_decode_error = json.JSONDecodeError
        self._read_mode = "r"
        try:
            import orjson

            self._json_parser = orjson
            self._json_decode_error = orjson.JSONDecodeError  # type: ignore
            self._read_mode = "rb"
        except ImportError:
            logger.warning("orjson not found, falling back to standard json. For faster JSON processing, consider installing orjson.")

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
            logger.warning("Unclosed ClientSession detected in BackendDemoWebService.__del__. Please call `close()` explicitly.")

    def _invalidate_json_cache_8002(self):
        """Invalidates the cache for the port 8002 JSON file."""
        logger.debug("Invalidating JSON cache for port 8002.")
        self._cached_json_data_8002 = None
        self._indexed_events_8002 = None
        self._cached_json_file_mtime_8002 = None

    async def _load_and_cache_json_8002(self) -> bool:
        """
        Loads data from WEB_3_AUTOZONE_JSON_FILEPATH, parses it,
        and populates the cache and index.
        Returns True on success, False on failure.
        """
        if not WEB_3_AUTOZONE_JSON_FILEPATH:
            logger.error("JSON file path (WEB_3_AUTOZONE_JSON_FILEPATH) not configured.")
            return False
        try:
            current_mtime = os.path.getmtime(WEB_3_AUTOZONE_JSON_FILEPATH)
            # Check if cache is still valid (e.g., another concurrent call might have updated it)
            if self._cached_json_file_mtime_8002 == current_mtime and self._indexed_events_8002 is not None:
                logger.debug("JSON cache for port 8002 already up-to-date by another process/task.")
                return True

            logger.debug(f"Loading and caching JSON from {WEB_3_AUTOZONE_JSON_FILEPATH}")
            with open(WEB_3_AUTOZONE_JSON_FILEPATH, self._read_mode) as f:
                # Add fcntl.flock(f.fileno(), fcntl.LOCK_SH) here if concurrent access is an issue
                # and ensure it's released in a finally block.
                file_content = f.read()

            raw_events_data = self._json_parser.loads(file_content)

            if not isinstance(raw_events_data, list):
                logger.error(f"JSON data at {WEB_3_AUTOZONE_JSON_FILEPATH} is not a list.")
                self._invalidate_json_cache_8002()
                return False

            self._cached_json_data_8002 = raw_events_data  # Cache raw data if needed elsewhere
            self._cached_json_file_mtime_8002 = current_mtime

            # Build the indexed cache
            temp_indexed_events: dict[str, list[BackendEvent]] = {}
            for event_dict in raw_events_data:
                if not isinstance(event_dict, dict):
                    logger.warning(f"Skipping non-dictionary event item: {event_dict}")
                    continue
                agent_id = event_dict.get("web_agent_id")
                if agent_id is not None:
                    try:
                        event = BackendEvent(**event_dict)
                        if agent_id not in temp_indexed_events:
                            temp_indexed_events[agent_id] = []
                        temp_indexed_events[agent_id].append(event)
                    except Exception as e:
                        logger.warning(f"Error instantiating BackendEvent for event: {event_dict}. Error: {e}")
                else:
                    logger.debug(f"Event missing 'web_agent_id' or it's None: {event_dict}")
            self._indexed_events_8002 = temp_indexed_events
            logger.info(f"Successfully loaded and indexed JSON data for port 8002. {len(raw_events_data)} events, {len(self._indexed_events_8002)} unique agent IDs.")
            return True

        except FileNotFoundError:
            logger.warning(f"Events file not found at {WEB_3_AUTOZONE_JSON_FILEPATH}")
            self._invalidate_json_cache_8002()
            return False
        except self._json_decode_error as e:
            logger.error(f"Error parsing JSON from {WEB_3_AUTOZONE_JSON_FILEPATH}: {e}")
            self._invalidate_json_cache_8002()
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading/caching JSON for port 8002: {e}")
            self._invalidate_json_cache_8002()
            return False

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
                current_mtime: float | None = None
                if os.path.exists(WEB_3_AUTOZONE_JSON_FILEPATH):
                    current_mtime = os.path.getmtime(WEB_3_AUTOZONE_JSON_FILEPATH)
                else:  # File doesn't exist
                    if self._cached_json_file_mtime_8002 is not None or self._indexed_events_8002 is not None:
                        logger.warning(f"Previously cached file {WEB_3_AUTOZONE_JSON_FILEPATH} no longer exists. Invalidating cache.")
                        self._invalidate_json_cache_8002()
                    return []  # File not found, no events

                # Check cache validity:
                # 1. Is indexed cache populated?
                # 2. Does the file modification time match the cached one?
                # 3. Was the file present (current_mtime is not None)?
                if self._indexed_events_8002 is not None and self._cached_json_file_mtime_8002 == current_mtime and current_mtime is not None:
                    logger.debug(f"Using cached and indexed JSON data for port 8002, agent ID: {web_agent_id}")
                    return self._indexed_events_8002.get(web_agent_id, [])
                else:
                    logger.info(f"Cache miss or file update for port 8002 (cached_mtime={self._cached_json_file_mtime_8002}, current_mtime={current_mtime}). Reloading.")
                    if await self._load_and_cache_json_8002() and self._indexed_events_8002 is not None:
                        return self._indexed_events_8002.get(web_agent_id, [])
                    return []  # Loading failed or resulted in no data for agent

            except FileNotFoundError:
                logger.warning(f"Events file not found at {WEB_3_AUTOZONE_JSON_FILEPATH} during get_backend_events check.")
                self._invalidate_json_cache_8002()
                return []
            except Exception as e:
                logger.error(f"Unexpected error in get_backend_events for port 8002 before loading: {e}")
                self._invalidate_json_cache_8002()
                return []

        # Original logic for non-8002 ports or if the 8002 branch doesn't return
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
                # Ensure fcntl is available and handle appropriately if not.
                with open(WEB_3_AUTOZONE_JSON_FILEPATH, "w") as f:  # Open in text mode for json.dump
                    # Example with fcntl (ensure fcntl is imported and available)
                    # with contextlib.suppress(ImportError, ModuleNotFoundError, AttributeError):
                    #     fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        json.dump([], f)  # Standard json.dump for writing an empty list
                    finally:
                        # with contextlib.suppress(ImportError, ModuleNotFoundError, AttributeError):
                        #     fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        pass  # Placeholder for fcntl unlock

                logger.info(f"Successfully cleared events from JSON file at {WEB_3_AUTOZONE_JSON_FILEPATH}")
                self._invalidate_json_cache_8002()  # Crucial: Invalidate cache
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
                    response_json = await response.json(loads=self._json_parser.loads)
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
