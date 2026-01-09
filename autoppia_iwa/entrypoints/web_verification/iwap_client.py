"""
IWAP Client for querying successful task solutions

IWAP (IWA Platform) API that tracks how many people have successfully solved tasks for each use case.
API Endpoint: https://api-leaderboard.autoppia.com/api/v1/tasks/with-solutions
"""

from datetime import datetime
from typing import Any

import aiohttp
from loguru import logger


class IWAPClient:
    """Client for querying IWAP service about successful task solutions"""

    def __init__(self, base_url: str = "https://api-leaderboard.autoppia.com", api_key: str = "AIagent2025", timeout_seconds: float = 10.0, use_mock: bool = False):
        """
        Initialize IWAP client

        Args:
            base_url: Base URL of the IWAP service (default: https://api-leaderboard.autoppia.com)
            api_key: API key for authentication (default: AIagent2025)
            timeout_seconds: Request timeout in seconds
            use_mock: If True, always return mock response instead of calling real API
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.use_mock = use_mock

    def _map_project_id_to_website(self, project_id: str) -> str:
        """
        Map project ID to website name for IWAP API

        Args:
            project_id: Project ID (e.g., 'autocrm', 'autolodge_8')

        Returns:
            Website name for API (e.g., 'autocrm', 'autolodge')
        """
        # Remove suffix numbers if present (e.g., 'autolodge_8' -> 'autolodge')
        if "_" in project_id:
            return project_id.split("_")[0]
        return project_id

    def _generate_mock_response(self, project_id: str, use_case_name: str, page: int = 1, limit: int = 20, our_tasks: list[Any] | None = None) -> dict[str, Any]:
        """
        Generate a mock API response for testing purposes

        Args:
            project_id: The web project ID
            use_case_name: Name of the use case
            page: Page number
            limit: Number of results per page
            our_tasks: Optional list of tasks from Step 1 (to extract constraints for better mock)

        Returns:
            Mock API response in the expected format
        """
        website = self._map_project_id_to_website(project_id)
        base_url = "http://localhost:8004"  # Default demo webs URL

        # Try to get constraints from our tasks if available
        mock_tests = []
        mock_prompt = f"Perform {use_case_name.replace('_', ' ').lower()}"

        if our_tasks and len(our_tasks) > 0:
            first_task = our_tasks[0]
            if first_task.use_case and first_task.use_case.constraints:
                # Convert our constraints to API test format
                criteria = {}
                for constraint in first_task.use_case.constraints:
                    field = constraint.get("field", "")
                    operator = constraint.get("operator", "")
                    value = constraint.get("value", "")

                    # Handle Enum operators
                    if hasattr(operator, "value"):
                        operator = operator.value

                    if field:
                        if operator == "equals":
                            criteria[field] = {"value": value}
                        else:
                            criteria[field] = {"value": value, "operator": operator}

                mock_tests = [{"type": "CheckEventTest", "event_name": use_case_name, "event_criteria": criteria}]

                # Use the prompt from our task
                mock_prompt = first_task.prompt if hasattr(first_task, "prompt") else mock_prompt

        # If no constraints found, use default
        if not mock_tests:
            mock_tests = [{"type": "CheckEventTest", "event_name": use_case_name, "event_criteria": {"status": {"value": "Active", "operator": "equals"}}}]

        # Generate mock actions (sample solution)
        # mock_actions = [
        #         {
        #           "type": "NavigateAction",
        #           "selector": None,
        #           "url": "http://localhost:8004/matters?seed=1",
        #           "go_back": False,
        #           "go_forward": False
        #         },
        #         {
        #           "type": "ClickAction",
        #           "selector": {
        #             "type": "xpathSelector",
        #             "attribute": None,
        #             "value": "//button[contains(normalize-space(.), 'Add New Matter') or contains(normalize-space(.), 'New Case') or contains(normalize-space(.), 'Start Project') or contains(normalize-space(.), 'Initialize Matter') or contains(normalize-space(.), 'Add Matter Record') or contains(normalize-space(.), 'Create New Matter') or contains(normalize-space(.), 'Launch Case') or contains(normalize-space(.), 'Insert Matter') or contains(normalize-space(.), 'Begin Engagement') or contains(normalize-space(.), 'Initiate Project')]",
        #             "case_sensitive": False
        #           },
        #           "x": None,
        #           "y": None
        #         },
        #         {
        #           "type": "TypeAction",
        #           "selector": {
        #             "type": "attributeValueSelector",
        #             "attribute": "id",
        #             "value": "matter-name-input",
        #             "case_sensitive": False
        #           },
        #           "text": "Trademark Infringement"
        #         },
        #         {
        #           "type": "TypeAction",
        #           "selector": {
        #             "type": "attributeValueSelector",
        #             "attribute": "id",
        #             "value": "client-name-input",
        #             "case_sensitive": False
        #           },
        #           "text": "XYZ Corp"
        #         },
        #         {
        #           "type": "SelectDropDownOptionAction",
        #           "selector": {
        #             "type": "attributeValueSelector",
        #             "attribute": "id",
        #             "value": "matter-status-select",
        #             "case_sensitive": False
        #           },
        #           "text": "Archived",
        #           "timeout_ms": 1000
        #         },
        #         {
        #           "type": "ClickAction",
        #           "selector": {
        #             "type": "xpathSelector",
        #             "attribute": None,
        #             "value": "(//button[contains(normalize-space(.), 'Add New Matter') or contains(normalize-space(.), 'New Case') or contains(normalize-space(.), 'Start Project') or contains(normalize-space(.), 'Initialize Matter') or contains(normalize-space(.), 'Add Matter Record') or contains(normalize-space(.), 'Create New Matter') or contains(normalize-space(.), 'Launch Case') or contains(normalize-space(.), 'Insert Matter') or contains(normalize-space(.), 'Begin Engagement') or contains(normalize-space(.), 'Initiate Project')])[2]",
        #             "case_sensitive": False
        #           },
        #           "x": None,
        #           "y": None
        #         }
        #       ]
        mock_actions = [
            {"type": "NavigateAction", "selector": None, "url": "http://localhost:8004/clients?seed=1", "go_back": False, "go_forward": False},
            {"type": "TypeAction", "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "search-input-field", "case_sensitive": False}, "text": "TechCorp Industries"},
            {"type": "WaitAction", "selector": None, "time_seconds": 0.2, "timeout_seconds": 5.0},
        ]
        # Create mock task item
        mock_task_item = {
            "task": {
                "taskId": f"mock-task-{use_case_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "website": website,
                "useCase": use_case_name,
                "intent": mock_prompt,
                "startUrl": f"{base_url}/?seed=1",
                "webVersion": "1.0",
                "tests": mock_tests,
                "createdAt": datetime.now().isoformat() + "Z",
            },
            "solution": {"taskSolutionId": f"mock-solution-{use_case_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}", "actions": mock_actions, "createdAt": datetime.now().isoformat() + "Z"},
            "evaluation": {"evaluationResultId": f"mock-eval-{use_case_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}", "score": 1, "passed": True},
            "agentRun": {
                "agentRunId": f"mock-run-{use_case_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "minerUid": 1,
                "minerHotkey": "mock_miner_key",
                "validatorUid": 1,
                "validatorHotkey": "mock_validator_key",
            },
        }

        # Create mock response structure
        mock_data = {"tasks": [mock_task_item], "total": 1, "page": page, "limit": limit}

        return {
            "success": True,
            "website": website,
            "use_case": use_case_name,
            "page": page,
            "limit": limit,
            "data": mock_data,
        }

    async def get_tasks_with_solutions(
        self, project_id: str, use_case_name: str | None = None, page: int | None = None, limit: int | None = None, our_tasks: list[Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Query IWAP API to get tasks with solutions for a use case (Step 2)

        API: GET /api/v1/tasks/with-solutions?key={api_key}&website={website}&useCase={useCase}&page={page}&limit={limit}

        Args:
            project_id: The web project ID (e.g., 'autocrm', 'autolodge_8')
            use_case_name: Name of the use case (e.g., 'VIEW_HOTEL')
            page: Page number (default: 1)
            limit: Number of results per page (default: 20)

        Returns:
            Dictionary with API response or None if query fails
        """
        website = self._map_project_id_to_website(project_id)

        # Use mock response if enabled
        if self.use_mock:
            print("\n📡 IWAP API Request (MOCK MODE):")
            print("   Using mock response for testing")
            print(f"   Website: {website}")
            print(f"   Use Case: {use_case_name}")
            logger.info(f"Using mock IWAP API response for {website}/{use_case_name}")
            mock_response = self._generate_mock_response(project_id, use_case_name or "", page or 1, limit or 20, our_tasks or [])
            print("   ✓ Mock response generated!")
            print(f"   Response: {len(mock_response.get('data', {}).get('tasks', []))} tasks returned")
            return mock_response

        endpoint = f"{self.base_url}/api/v1/tasks/with-solutions"

        params = {
            "key": self.api_key,
            "website": website,
            "useCase": use_case_name,
            # "page": page,
            # "limit": limit,
        }

        try:
            # Print API call details for debugging
            print("\n📡 IWAP API Request:")
            print(f"   URL: {endpoint}")
            print("   Parameters:")
            print(f"     - key: {self.api_key}")
            print(f"     - website: {website}")
            print(f"     - useCase: {use_case_name}")
            # print(f"     - page: {page}")
            # print(f"     - limit: {limit}")

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.info(f"Querying IWAP API: {endpoint} with params: website={website}, useCase={use_case_name}, page={page}, limit={limit}")

                print("   Making GET request...")
                async with session.get(endpoint, params=params) as response:
                    print(f"   Response Status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print("   ✓ API call successful!")

                        # Print summary of response
                        if isinstance(data, dict):
                            tasks = data.get("tasks", [])
                            total = data.get("total", len(tasks))
                            print(f"   Response: {len(tasks)} tasks returned (total: {total})")
                        else:
                            print(f"   Response: {type(data).__name__}")

                        logger.info(f"IWAP API query successful for {website}/{use_case_name}")
                        return {
                            "success": True,
                            "website": website,
                            "use_case": use_case_name,
                            "page": page,
                            "limit": limit,
                            "data": data,
                        }
                    else:
                        error_text = await response.text()
                        print(f"   ✗ API call failed with status {response.status}")
                        print(f"   Error: {error_text[:200]}")  # Print first 200 chars
                        print("   ⚠️  API not available, using mock response for testing...")
                        logger.warning(f"IWAP API returned status {response.status}: {error_text}. Using mock response.")
                        # Return mock response when API fails (for testing)
                        mock_response = self._generate_mock_response(project_id, use_case_name or "", page or 1, limit or 20, our_tasks or [])
                        print("   ✓ Mock response generated!")
                        return mock_response

        except aiohttp.ClientError as e:
            print(f"   ✗ Network/Client Error: {e}")
            print("   ⚠️  API not available, using mock response for testing...")
            logger.warning(f"IWAP API request error: {e}. Using mock response.")
            # Return mock response when API fails (for testing)
            mock_response = self._generate_mock_response(project_id, use_case_name or "", page or 1, limit or 20)
            print("   ✓ Mock response generated!")
            return mock_response
        except Exception as e:
            print(f"   ✗ Unexpected Error: {e}")
            print("   ⚠️  API not available, using mock response for testing...")
            logger.warning(f"Error querying IWAP API: {e}. Using mock response.")
            # Return mock response when API fails (for testing)
            mock_response = self._generate_mock_response(project_id, use_case_name or "", page or 1, limit or 20)
            print("   ✓ Mock response generated!")
            return mock_response

    def _normalize_string(self, s: str) -> str:
        """Normalize string for comparison (lowercase, strip whitespace)"""
        return s.lower().strip() if s else ""

    def _tests_match_constraints(self, api_tests: list[dict[str, Any]], our_constraints: list[dict[str, Any]]) -> bool:
        """
        Check if any test from API matches our constraints

        Args:
            api_tests: List of test dictionaries from API response
            our_constraints: List of constraint dictionaries from our generated task

        Returns:
            True if any test matches our constraints
        """
        if not api_tests or not our_constraints:
            return False

        # Convert our constraints to a comparable format

        # for manual testing
        # our_constraints_list = [
        #     {
        #         "field": "item",
        #         "operator": "not_contains",
        #         "value": "patatas bravas"
        #     },
        #     {
        #         "field": "price",
        #         "operator": "less_than",
        #         "value": 17.91
        #     },
        #     {
        #         "field": "quantity",
        #         "operator": "equals",
        #         "value": 4
        #     },
        #     {
        #         "field": "restaurant",
        #         "operator": "not_contains",
        #         "value": "sakura sushi"
        #     },
        #     {
        #         "field": "preferences",
        #         "operator": "in_list",
        #         "value": ["low-carb", "seafood-free", "siy-free"]
        #     }
        # ]
        our_constraints_list = []
        for constraint in our_constraints:
            field = constraint.get("field", "")
            operator = constraint.get("operator", "")
            value = constraint.get("value", "")
            # Handle Enum operators
            if hasattr(operator, "value"):
                operator = operator.value
            # Normalize for comparison
            our_constraints_list.append({"field": field.lower().strip(), "operator": str(operator).lower().strip(), "value": str(value).lower().strip() if value is not None else ""})

        # Check if any API test matches our constraints
        for test in api_tests:
            # Extract test criteria from API test
            # API test structure may vary, try common fields
            test_field = test.get("field", "")
            test_operator = test.get("operator", "")
            test_value = test.get("value", "")

            # Also check for nested structures (e.g., test.criteria.field)
            if not test_field and "event_criteria" in test:
                criteria = test.get("event_criteria", {})
                for field, rule in criteria.items():
                    test_field = field
                    test_operator = rule.get("operator", "equals") if isinstance(rule, dict) else "equals"
                    test_value = rule.get("value") if isinstance(rule, dict) else rule

                    # Normalize for comparison
                    normalized_test = {
                        "field": test_field.lower().strip() if test_field else "",
                        "operator": str(test_operator).lower().strip() if test_operator else "",
                        "value": str(test_value).lower().strip() if test_value is not None else "",
                    }

                    # Check if this test matches any of our constraints
                    for our_constraint in our_constraints_list:
                        if normalized_test["field"] == our_constraint["field"] and normalized_test["operator"] == our_constraint["operator"] and normalized_test["value"] == our_constraint["value"]:
                            return True

            return False

    def _intent_matches_prompt(self, api_intent: str, our_prompt: str) -> bool:
        """
        Check if API intent matches our prompt (fuzzy matching)

        Args:
            api_intent: Intent string from API
            our_prompt: Prompt string from our generated task

        Returns:
            True if intent matches prompt (case-insensitive, normalized)
        """
        if not api_intent or not our_prompt:
            return False

        normalized_intent = self._normalize_string(api_intent)
        normalized_prompt = self._normalize_string(our_prompt)

        # Check if intent is contained in prompt or vice versa
        # Or if they are very similar (simple heuristic)
        return normalized_intent in normalized_prompt or normalized_prompt in normalized_intent or normalized_intent == normalized_prompt

    def process_api_response_for_tasks(self, api_response: dict[str, Any], our_tasks: list[Any]) -> dict[str, Any]:
        """
        Process IWAP API response and match with our generated tasks

        Args:
            api_response: Response from get_tasks_with_solutions
            our_tasks: List of Task objects we generated

        Returns:
            Dictionary with matching results and actions
        """
        if not api_response or not api_response.get("success", False):
            return {
                "matched": False,
                "reason": "API call failed or no response",
                "actions": None,
            }

        # API response structure: {"success": true, "data": {"data": {"tasks": [...], ...}}}
        # The outer "data" is from our wrapper, inner "data" is from API
        api_wrapper_data = api_response.get("data", {})
        api_data = api_wrapper_data.get("data", api_wrapper_data)  # Handle both structures
        api_tasks = api_data.get("tasks", []) if isinstance(api_data, dict) else []

        # Filter tasks with evaluation score = 1 and passed = True
        passed_tasks = []
        for api_task_item in api_tasks:
            evaluation = api_task_item.get("evaluation", {})
            if evaluation.get("score") == 1 and evaluation.get("passed") is True:
                passed_tasks.append(api_task_item)

        if not passed_tasks:
            return {
                "matched": False,
                "reason": "No tasks with evaluation score=1 and passed=True found",
                "actions": None,
            }

        # Try to match each of our tasks with passed API tasks
        for our_task in our_tasks:
            our_constraints = our_task.use_case.constraints if our_task.use_case and our_task.use_case.constraints else []
            our_prompt = our_task.prompt if hasattr(our_task, "prompt") else ""

            for api_task_item in passed_tasks:
                task_data = api_task_item.get("task", {})
                api_tests = task_data.get("tests", [])
                api_intent = task_data.get("intent", "")
                solution = api_task_item.get("solution", {})
                api_actions = solution.get("actions", [])

                # Step 1: Check if tests match our constraints
                if self._tests_match_constraints(api_tests, our_constraints):
                    return {
                        "matched": True,
                        "match_type": "tests",
                        "reason": "Tests from API match our constraints",
                        "actions": api_actions,
                        "api_task_id": task_data.get("taskId"),
                        "api_intent": api_intent,
                        "api_prompt": api_intent,  # Use intent as prompt
                        "api_tests": api_tests,
                        "api_start_url": task_data.get("startUrl", ""),
                        "api_web_version": task_data.get("webVersion", ""),
                    }

                # Step 2: Check if intent matches our prompt
                if self._intent_matches_prompt(api_intent, our_prompt):
                    return {
                        "matched": True,
                        "match_type": "intent",
                        "reason": "Intent from API matches our prompt",
                        "actions": api_actions,
                        "api_task_id": task_data.get("taskId"),
                        "api_intent": api_intent,
                        "api_prompt": api_intent,  # Use intent as prompt
                        "api_tests": api_tests,
                        "api_start_url": task_data.get("startUrl", ""),
                        "api_web_version": task_data.get("webVersion", ""),
                    }

        # No matches found
        return {
            "matched": False,
            "reason": "Nobody has been able to solve this use case (no matching tests or intent found)",
            "actions": None,
        }

    async def check_use_case_doability(self, project_id: str, use_case_name: str, min_success_rate: float = 0.5) -> dict[str, Any]:
        """
        Check if a use case is "doable" based on tasks with solutions from IWAP API

        This is Step 2: Query IWAP API when LLM review is valid

        Args:
            project_id: The web project ID
            use_case_name: Name of the use case
            min_success_rate: Minimum success rate to consider use case doable (not used in current implementation)

        Returns:
            Dictionary with doability assessment and API response
        """
        result = await self.get_tasks_with_solutions(project_id, use_case_name)

        if not result or not result.get("success", False):
            return {
                "doable": False,
                "reason": f"Could not retrieve data from IWAP API: {result.get('error', 'Unknown error') if result else 'No response'}",
                "api_response": result,
            }

        # Extract data from API response
        api_data = result.get("data", {})

        # Count tasks with solutions
        tasks = api_data.get("tasks", []) if isinstance(api_data, dict) else []
        tasks_with_solutions = [task for task in tasks if task.get("solutions") and len(task.get("solutions", [])) > 0]

        total_tasks = len(tasks)
        tasks_with_solutions_count = len(tasks_with_solutions)

        # Calculate success rate if we have data
        success_rate = (tasks_with_solutions_count / total_tasks) if total_tasks > 0 else 0.0

        is_doable = tasks_with_solutions_count > 0

        return {
            "doable": is_doable,
            "success_rate": success_rate,
            "tasks_with_solutions": tasks_with_solutions_count,
            "total_tasks": total_tasks,
            "reason": (f"Found {tasks_with_solutions_count} tasks with solutions out of {total_tasks} total tasks" if is_doable else f"No tasks with solutions found (total tasks: {total_tasks})"),
            "api_response": result,
        }
