import asyncio
import unittest

import httpx

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest


class TestConcurrentTaskExecution(unittest.TestCase):
    """Test concurrent execution of /solve_task endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up shared task data for all tests."""
        cls.url = "http://127.0.0.1:9000/solve_task"

        # Task 1 Data
        task1_data = {
            "prompt": "Click on the 'Login' link in the header, fill credentials, and login.",
            "url": "http://localhost:8000/",
            "tests": [{"type": "CheckEventTest", "event_name": "login"}, {"type": "FindInHtmlTest", "substring": "login"}],
            "relevant_data": {"authorization": {"email": "employee@employee.com", "password": "employee"}},
        }
        task1_data["tests"] = [BaseTaskTest.deserialize(test) for test in task1_data["tests"]]
        cls.task1_json = Task(**task1_data).model_dump()

        # Task 2 Data
        task2_data = {
            "prompt": "Navigate to the 'Jobs' section and verify the listed job postings.",
            "url": "http://localhost:8000/jobs",
            "tests": [{"type": "FindInHtmlTest", "substring": "Jobs"}, {"type": "FindInHtmlTest", "substring": "Apply Now"}],
        }
        task2_data["tests"] = [BaseTaskTest.deserialize(test) for test in task2_data["tests"]]
        cls.task2_json = Task(**task2_data).model_dump()

    async def send_request(self, task_json):
        """Send an asynchronous request to the /solve_task endpoint."""
        async with httpx.AsyncClient(timeout=150) as client:
            response = await client.post(self.url, json=task_json)
            return response.json()

    def test_concurrent_separate_tasks(self):
        """Test execution of two separate tasks concurrently."""

        async def run_test():
            task1 = self.send_request(self.task1_json)  # Task 1
            await asyncio.sleep(0.1)  # Small delay (100ms)
            task2 = self.send_request(self.task2_json)  # Task 2

            responses = await asyncio.gather(task1, task2)
            print("Task 1: ", responses[0])
            print("\n" * 5)
            print("Task 2: ", responses[1])

            # Assertions to check valid responses
            self.assertIsNotNone(responses[0], "Task 1 request failed!")
            self.assertIsNotNone(responses[1], "Task 2 request failed!")
            self.assertIn("actions", responses[0], "Task 1 response missing 'actions'!")
            self.assertIn("actions", responses[1], "Task 2 response missing 'actions'!")

            print("✅ Both separate tasks executed successfully!")

        asyncio.run(run_test())  # Run the async test inside unittest


if __name__ == "__main__":
    unittest.main()
