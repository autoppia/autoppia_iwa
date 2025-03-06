import logging
from typing import List, Optional

import aiohttp
from aiohttp.client_exceptions import ClientError

from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject

logger = logging.getLogger(__name__)


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
        self._session: Optional[aiohttp.ClientSession] = None
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

    async def get_backend_events(self, web_agent_id: str) -> List[BackendEvent]:
        """
        Fetch recent events from the backend for the specified web_agent_id.

        Args:
            web_agent_id (str): ID of the web agent to filter events for.

        Returns:
            List[BackendEvent]: List of events from the backend or an empty list if any failure occurs.
        """
        endpoint = f"{self.base_url}api/events/list/"
        headers = {"X-WebAgent-Id": web_agent_id}

        try:
            session = await self._get_session()
            async with session.get(endpoint, headers=headers) as response:
                response.raise_for_status()  # Raise on 4xx/5xx
                events_data = await response.json()
                return [BackendEvent(**event) for event in events_data]
        except ClientError as e:
            logger.error(f"Network error while fetching backend events: {e}")
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching backend events: {e}")

        return []

    async def reset_backend_events_db(self, web_agent_id: str) -> bool:
        """
        Resets backend events for the given web_agent_id.

        Args:
            web_agent_id (str): Identifier for the web_agent.

        Returns:
            bool: True if reset was successful, False otherwise.

        Raises:
            RuntimeError: If the reset operation fails with an unhandled error condition.
        """
        endpoint = f"{self.base_url}api/events/reset/"
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

                # Additional logic if needed
                if response.status == 204:
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

            error_message = f"Failed to reset backend events for web_agent '{web_agent_id}': {e}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e
        except Exception:
            return False

    async def send_page_view_event(self, url: str, web_agent_id: str) -> bool:
        """
        Sends a PageView event to the backend for a given web_agent_id.

        Args:
            url (str): The current page URL viewed by the agent.
            web_agent_id (str): The ID of the web agent.

        Returns:
            bool: True if the event was sent successfully, False otherwise.
        """
        return True
        # We check Url in the forntend for now
        # parsed_url = urlparse(url)
        # path_only = parsed_url.path

        # payload = {
        #     "event_type": "page_view",
        #     "description": "Page viewed",
        #     "data": {
        #         "url": path_only,
        #         "timestamp": datetime.datetime.now().isoformat(),
        #     },
        #     "web_agent_id": web_agent_id,
        # }

        # endpoint = f"{self.base_url}api/events/add/"
        # headers = {"X-WebAgent-Id": web_agent_id}

        # try:
        #     session = await self._get_session()
        #     async with session.post(endpoint, json=payload, headers=headers, timeout=10) as response:
        #         response.raise_for_status()
        #         return True
        # except ClientError as e:
        #     logger.error(f"Failed to send PageView event: {e}")
        # except Exception as e:
        #     logger.error(f"Unexpected error while sending PageView event: {e}")

        # return False
