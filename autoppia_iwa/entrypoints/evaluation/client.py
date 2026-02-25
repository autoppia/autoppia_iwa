"""
Evaluation Client

Simple client for agents to call the evaluation endpoint and check if their solutions will pass.

Usage in your agent:
    from autoppia_iwa.entrypoints.evaluation.client import EvaluationClient

    client = EvaluationClient()
    result = await client.check_solution(task, actions, web_agent_id)

    if result.success:
        print("Solution will pass!")
    else:
        print(f"Solution will fail. Score: {result.final_score}")
"""

import asyncio
from typing import Any

import httpx
from loguru import logger
from pydantic import BaseModel

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.execution.actions.actions import NavigateAction, WaitAction
from autoppia_iwa.src.execution.actions.base import BaseAction


class EvaluationResult(BaseModel):
    """Result from evaluation endpoint"""

    success: bool
    final_score: float
    raw_score: float
    execution_time: float
    tests_passed: int
    total_tests: int
    action_count: int
    had_errors: bool
    error_message: str | None = None
    gif_recording: str | None = None


class EvaluationClient:
    """Client for calling the evaluation endpoint"""

    def __init__(self, base_url: str = "http://localhost:5060", timeout: float = 30.0):
        """
        Initialize the evaluation client.

        Args:
            base_url: Base URL of the evaluation endpoint service
            timeout: Request timeout in seconds (default: 30s)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """
        Check if the evaluation endpoint is healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                logger.debug(f"Health check passed: {response.json()}")
                return True
            logger.warning(f"Health check returned status {response.status_code}")
            return False
        except httpx.ConnectError:
            logger.error(f"Cannot connect to evaluation service at {self.base_url}. Is it running?")
            return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def check_solution(
        self,
        task: Task,
        actions: list[BaseAction],
        web_agent_id: str,
        should_record: bool = False,
    ) -> EvaluationResult:
        """
        Check if a solution will pass the task tests.

        Args:
            task: The Task object containing prompt, url, tests, etc.
            actions: List of actions to execute
            web_agent_id: Identifier for the web agent
            should_record: Whether to record GIF of execution (slower)

        Returns:
            EvaluationResult with success status and detailed metrics

        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            client = self._get_client()

            # Prepare request payload
            payload = {
                "task_id": task.id,
                "prompt": task.prompt,
                "url": task.url,
                "tests": [test.model_dump() for test in task.tests],
                "actions": [action.model_dump() for action in actions],
                "web_agent_id": web_agent_id,
                "web_project_id": task.web_project_id,
                "should_record": should_record,
            }

            # Make request
            response = await client.post(f"{self.base_url}/evaluate", json=payload)
            response.raise_for_status()

            # Parse response
            result_data = response.json()
            return EvaluationResult(**result_data)

        except httpx.ConnectError:
            logger.error(f"Cannot connect to evaluation service at {self.base_url}. Is it running?")
            raise
        except httpx.TimeoutException:
            logger.error(f"Evaluation request timed out after {self.timeout}s")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Evaluation failed with status {e.response.status_code}: {e.response.text}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Evaluation request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during evaluation: {e}")
            raise

    async def check_solution_dict(self, payload: dict[str, Any]) -> EvaluationResult:
        """
        Check solution using a raw dictionary payload.

        This is useful if you want full control over the request format.

        Args:
            payload: Dictionary matching EvaluationRequest schema

        Returns:
            EvaluationResult with success status and detailed metrics
        """
        try:
            client = self._get_client()
            response = await client.post(f"{self.base_url}/evaluate", json=payload)
            response.raise_for_status()
            result_data = response.json()
            return EvaluationResult(**result_data)
        except httpx.ConnectError:
            logger.error(f"Cannot connect to evaluation service at {self.base_url}. Is it running?")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Evaluation request failed: {e}")
            raise


# ==============
# CONVENIENCE FUNCTIONS
# ==============


async def quick_check(
    task: Task,
    actions: list[BaseAction],
    web_agent_id: str,
    endpoint_url: str = "http://localhost:5060",
) -> bool:
    """
    Quick check if a solution will pass (returns only success boolean).

    Args:
        task: The Task object
        actions: List of actions to execute
        web_agent_id: Agent identifier
        endpoint_url: Evaluation endpoint URL

    Returns:
        True if solution will pass, False otherwise
    """
    async with EvaluationClient(endpoint_url) as client:
        result = await client.check_solution(task, actions, web_agent_id)
        return result.success


# ==============
# EXAMPLE USAGE
# ==============


async def example_usage():
    """Example of how to use the evaluation client in an agent"""

    prompt = "Show me details about a 'bluetooth speaker' priced at 79.99, with category 'Electronics', rated at 4.6 with brand 'JBL'. Navigate to its product detail page."
    actions = [NavigateAction(url="http://localhost:8002/tech-6"), WaitAction(time_seconds=0.2)]
    criteria = [
        {"field": "title", "operator": "contains", "value": "bluetooth speaker"},
        {"field": "price", "operator": "equals", "value": 79.99},
        {"field": "category", "operator": "equals", "value": "Electronics"},
        {"field": "rating", "operator": "greater_equal", "value": 4.6},
        {"field": "brand", "operator": "equals", "value": "JBL"},
    ]
    event_criteria = {}
    for crit in criteria:
        event_criteria[crit["field"]] = {"operator": crit["operator"], "value": crit["value"]}
    task = Task(
        id="example-task",
        prompt=prompt,
        url="http://localhost:8002/",
        web_project_id="autozone",
        tests=[
            CheckEventTest(
                **{
                    "type": "CheckEventTest",
                    "event_name": "VIEW_DETAIL",
                    "event_criteria": event_criteria,
                }
            )
        ],
    )

    web_agent_id = "agent-1"

    # Method 1: Using context manager (recommended)
    async with EvaluationClient() as client:
        # Check if service is running
        if not await client.health_check():
            logger.error("Evaluation service is not running!")
            return

        # Evaluate solution
        result = await client.check_solution(task, actions, web_agent_id)

        if result.success:
            logger.success(f"✓ Solution will PASS! (score: {result.final_score})")
        else:
            logger.warning(f"✗ Solution will FAIL. Score: {result.final_score}, Tests passed: {result.tests_passed}/{result.total_tests}")

    # Method 2: Quick check (if you only need success/fail)
    will_pass = await quick_check(task, actions, web_agent_id)
    logger.info(f"Will pass: {will_pass}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
