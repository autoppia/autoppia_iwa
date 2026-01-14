"""
Dynamic Verifier for testing tasks with different seed values

This verifier evaluates solutions from IWAP API against tasks generated with different seed values,
ensuring the solution works correctly across different dynamic content.
"""

from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.actions import BaseAction
from autoppia_iwa.src.web_agents.classes import TaskSolution


class DynamicVerifier:
    """Verifies that dynamic functionality works correctly with different seed values"""

    def __init__(
        self,
        web_project: WebProject,
        llm_reviewer=None,
    ):
        """
        Initialize Dynamic Verifier

        Args:
            web_project: The web project to verify
            llm_reviewer: Optional LLM reviewer for reviewing generated tasks
        """
        self.web_project = web_project
        self.llm_reviewer = llm_reviewer
        self.task_generator = SimpleTaskGenerator(
            web_project=web_project,
            llm_service=DIContainer.llm_service(),
        )

    async def verify_task_with_seeds(
        self,
        api_prompt: str,
        api_tests: list[dict[str, Any]],
        api_start_url: str,
        use_case: Any,
        seed_values: list[int],
        solution_actions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Verify solution from IWAP API against task created from API prompt with different seed values.
        For each seed, creates a task from API prompt with that seed and evaluates the solution against it.

        Args:
            api_prompt: Prompt from IWAP API
            api_tests: Tests from IWAP API
            api_start_url: Start URL from IWAP API
            use_case: Use case object
            seed_values: List of seed values to test
            solution_actions: List of action dictionaries from IWAP API solution (required).

        Returns:
            Dictionary with verification results:
            {
                "use_case_name": str,
                "seeds_tested": List[int],
                "results": Dict[int, Dict],  # Results per seed (includes evaluation)
                "all_passed": bool,
                "summary": str
            }
        """
        if not solution_actions:
            return {
                "error": "No solution actions provided",
                "all_passed": False,
            }

        if not use_case:
            return {
                "error": "No use case provided",
                "all_passed": False,
            }

        if solution_actions:
            logger.info(f"Evaluating solution against tasks with different seeds for use case {use_case.name} with seeds: {seed_values}")
        else:
            logger.info(f"Verifying dynamic generation for use case {use_case.name} with seeds: {seed_values}")

        results = {}
        all_passed = True

        # Convert solution actions to BaseAction objects if provided
        base_actions = None
        if solution_actions:
            try:
                # Normalize actions first, then create BaseAction objects
                normalized_actions = []
                for action in solution_actions:
                    normalized = self._normalize_action(action)
                    if normalized is not None:  # Skip invalid actions
                        normalized_actions.append(normalized)

                base_actions = [BaseAction.create_action(action) for action in normalized_actions]
                base_actions = [a for a in base_actions if a is not None]  # Filter out None values
                logger.info(f"Converted {len(base_actions)} actions from API solution (normalized {len(normalized_actions)} actions)")
            except Exception as e:
                logger.error(f"Error converting solution actions: {e}")
                return {
                    "error": f"Failed to convert solution actions: {e}",
                    "all_passed": False,
                }

        for seed in seed_values:
            try:
                seed_result = await self._evaluate_solution_with_seed(api_prompt, api_tests, api_start_url, use_case, seed, base_actions)
                results[seed] = seed_result

                # Check if evaluation passed
                if solution_actions:
                    evaluation_success = seed_result.get("evaluation", {}).get("final_score", 0) == 1.0
                    if not evaluation_success:
                        all_passed = False
                else:
                    generation_success = seed_result.get("success", False)
                    llm_valid = seed_result.get("llm_review", {}).get("valid", True) if seed_result.get("llm_review") else True
                    if not (generation_success and llm_valid):
                        all_passed = False

            except Exception as e:
                logger.error(f"Error processing task with seed {seed}: {e}")
                results[seed] = {
                    "success": False,
                    "error": str(e),
                }
                all_passed = False

        # Generate summary
        if solution_actions:
            passed_count = sum(1 for r in results.values() if r.get("evaluation", {}).get("final_score", 0) == 1.0)
            total_count = len(results)
            summary = f"Dynamic verification: {passed_count}/{total_count} seeds passed evaluation. Solution works correctly with {passed_count} different seed values."
        else:
            passed_count = sum(1 for r in results.values() if r.get("success", False) and r.get("llm_review", {}).get("valid", True))
            total_count = len(results)
            summary = f"Dynamic verification: {passed_count}/{total_count} seeds passed. Tasks can be generated and validated with {passed_count} different seed values."

        return {
            "use_case_name": use_case.name,
            "seeds_tested": seed_values,
            "results": results,
            "all_passed": all_passed,
            "passed_count": passed_count,
            "total_count": total_count,
            "summary": summary,
        }

    async def _generate_and_review_task_with_seed(self, use_case, seed: int) -> dict[str, Any]:
        """
        Generate a task with a specific seed value, print it, and review with LLM

        Args:
            use_case: The use case to generate task for
            seed: The seed value to use

        Returns:
            Dictionary with generation and review results
        """
        try:
            # Generate task with dynamic=True and specific seed
            # The seed will be added to the URL automatically by the generator
            base_url = self.web_project.frontend_url or self.web_project.urls[0] if self.web_project.urls else ""

            # Add seed to URL
            parsed = urlparse(base_url)
            query_params = parse_qs(parsed.query)
            query_params["seed"] = [str(seed)]
            new_query = urlencode(query_params, doseq=True)
            seeded_url = urlunparse(parsed._replace(query=new_query))

            # Generate task with this seeded URL
            tasks = await self.task_generator.generate_tasks_for_use_case(
                use_case=use_case,
                number_of_prompts=1,  # Generate just 1 task per seed for verification
                dynamic=True,
                base_url=seeded_url,
            )

            if not tasks or len(tasks) == 0:
                return {
                    "success": False,
                    "tasks_generated": 0,
                    "error": "No tasks generated",
                }

            task = tasks[0]

            # Extract seed values from URL
            seed_value = self._extract_seed_from_url(task.url)
            v2_seed_value = self._extract_v2_seed_from_url(task.url)

            # Get constraints
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Print task details before LLM review
            self._print_task_details_for_review(task, seed_value, v2_seed_value, constraints_str, is_dynamic=True)

            # Review with LLM if reviewer is available
            llm_review_result = None
            if self.llm_reviewer:
                logger.info(f"Reviewing dynamically generated task {task.id} (seed={seed}) with LLM")
                llm_review_result = await self.llm_reviewer.review_task_and_constraints(task)
                llm_review_result["task_id"] = task.id

            # Serialize constraints to make them JSON-compatible
            serialized_constraints = self._serialize_constraints(constraints) if constraints else None

            return {
                "success": True,
                "tasks_generated": len(tasks),
                "task_id": task.id,
                "prompt": task.prompt,
                "constraints": serialized_constraints,
                "constraints_str": constraints_str,
                "seed": seed_value,
                "v2_seed": v2_seed_value,
                "has_constraints": bool(constraints),
                "llm_review": llm_review_result,
            }

        except Exception as e:
            logger.error(f"Error generating task with seed {seed}: {e}")
            return {
                "success": False,
                "tasks_generated": 0,
                "error": str(e),
            }

    def _normalize_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize action from API format to format expected by BaseAction.create_action()

        Args:
            action: Action dictionary from API

        Returns:
            Normalized action dictionary
        """
        normalized = action.copy()

        # Handle nested 'attributes' structure: flatten it
        if "attributes" in normalized and isinstance(normalized["attributes"], dict):
            # Merge attributes into the main dict
            attributes = normalized.pop("attributes")
            normalized.update(attributes)

        # Normalize action type
        action_type = normalized.get("type", "").lower()
        type_mapping = {
            "navigate": "NavigateAction",
            "click": "ClickAction",
            "input": "TypeAction",
            "type": "TypeAction",
            "wait": "WaitAction",
            "selectdropdownoption": "SelectDropDownOptionAction",
            "select": "SelectDropDownOptionAction",
        }

        if action_type in type_mapping:
            normalized["type"] = type_mapping[action_type]
        elif not action_type.endswith("Action"):
            # Capitalize and add Action suffix
            normalized["type"] = action_type.capitalize() + "Action"

        # Handle NavigateAction: ensure it has url, go_back, or go_forward
        if normalized["type"] == "NavigateAction" and not normalized.get("url") and not normalized.get("go_back") and not normalized.get("go_forward"):
            # If no url and no navigation flags, skip this action (invalid)
            return None

        # Handle WaitAction: convert timeout_seconds to time_seconds
        if normalized["type"] == "WaitAction":
            if "timeout_seconds" in normalized and "time_seconds" not in normalized:
                normalized["time_seconds"] = normalized.pop("timeout_seconds")
            # Ensure it has either selector or time_seconds
            if not normalized.get("selector") and not normalized.get("time_seconds"):
                # Default to 1 second if nothing specified
                normalized["time_seconds"] = 1.0

        # Handle TypeAction: ensure it has 'text' field (or convert 'value' to 'text')
        if normalized["type"] == "TypeAction":
            if "value" in normalized and "text" not in normalized:
                normalized["text"] = normalized.pop("value")
            # Improvement 3: Handle empty text - skip actions with empty text
            text_value = normalized.get("text")
            if "text" not in normalized or not text_value or (isinstance(text_value, str) and not text_value.strip()):
                # TypeAction requires non-empty text field
                logger.warning(f"TypeAction has empty or missing 'text' field, skipping action: {normalized}")
                return None

        # Improvement 3: Handle SelectDropDownOptionAction - ensure it has non-empty 'text' field
        if normalized["type"] == "SelectDropDownOptionAction":
            text_value = normalized.get("text")
            if "text" not in normalized or not text_value or (isinstance(text_value, str) and not text_value.strip()):
                # SelectDropDownOptionAction requires non-empty text field
                logger.warning(f"SelectDropDownOptionAction has empty or missing 'text' field, skipping action: {normalized}")
                return None

        # Handle ClickAction: ensure it has selector or (x, y) coordinates
        if normalized["type"] == "ClickAction":
            has_selector = "selector" in normalized and normalized["selector"] is not None
            has_coords = "x" in normalized and "y" in normalized and normalized.get("x") is not None and normalized.get("y") is not None

            if not has_selector and not has_coords:
                logger.warning(f"ClickAction missing selector or coordinates, skipping action: {normalized}")
                return None

        # Handle selector: normalize selector dict format
        if "selector" in normalized and normalized["selector"] is not None:
            if isinstance(normalized["selector"], dict):
                selector_dict = normalized["selector"]
                selector_type_str = selector_dict.get("type", "").lower()

                # Map selector types to expected format
                if selector_type_str == "xpathselector" or selector_type_str == "xpath":
                    normalized["selector"]["type"] = "xpathSelector"
                elif selector_type_str == "attributevalueselector" or selector_type_str == "attribute":
                    normalized["selector"]["type"] = "attributeValueSelector"
                elif not selector_type_str:
                    # If no type specified, try to infer from value
                    selector_value = selector_dict.get("value", "")
                    if selector_value and (selector_value.startswith("//") or selector_value.startswith("(//")):
                        normalized["selector"]["type"] = "xpathSelector"
                    else:
                        normalized["selector"]["type"] = "attributeValueSelector"

                # Validate selector value is present and not empty
                selector_value = normalized["selector"].get("value")
                if not selector_value or (isinstance(selector_value, str) and not selector_value.strip()):
                    # Selector has no valid value
                    if normalized["type"] in ["ClickAction", "TypeAction", "SelectDropDownOptionAction"]:
                        # These actions require a valid selector
                        logger.warning(f"{normalized['type']} has invalid selector (empty value), skipping action")
                        return None
                    else:
                        # For other actions, remove invalid selector
                        normalized.pop("selector", None)
            elif normalized["type"] in ["ClickAction", "TypeAction", "SelectDropDownOptionAction"]:
                # Selector is not a dict but action requires it
                logger.warning(f"{normalized['type']} has invalid selector type, skipping action")
                return None

        return normalized

    def _extract_seed_from_url(self, url: str) -> int | None:
        """Extract seed parameter from URL query string"""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if query.get("seed"):
                value = int(str(query["seed"][0]).strip())
                return value
        except Exception:
            pass
        return None

    def _extract_v2_seed_from_url(self, url: str) -> int | None:
        """Extract v2-seed parameter from URL query string"""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if query.get("v2-seed"):
                value = int(str(query["v2-seed"][0]).strip())
                return value
        except Exception:
            pass
        return None

    def _print_task_details_for_review(self, task: Task, seed: int | None, v2_seed: int | None, constraints_str: str, is_dynamic: bool = False):
        """
        Print task details (prompt, constraints, seed) before GPT review

        Args:
            task: The task to print
            seed: Base seed value from URL
            v2_seed: V2 seed value from URL
            constraints_str: String representation of constraints
            is_dynamic: Whether this is for dynamic verification
        """
        prefix = "🔄 DYNAMIC" if is_dynamic else "📋"
        print("\n" + "=" * 80)
        print(f"{prefix} TASK DETAILS FOR GPT REVIEW")
        print("=" * 80)
        print(f"Task ID: {task.id}")
        print(f"Use Case: {task.use_case.name if task.use_case else 'Unknown'}")

        # Print seed values
        seed_info = []
        if seed is not None:
            seed_info.append(f"seed={seed}")
        if v2_seed is not None:
            seed_info.append(f"v2-seed={v2_seed}")
        if seed_info:
            print(f"Seed Values: {', '.join(seed_info)}")
        else:
            print("Seed Values: None (no dynamic seed)")

        # Print constraints (tests)
        print("\n" + "-" * 80)
        print("🧪 CONSTRAINTS (Tests):")
        print("-" * 80)
        if constraints_str:
            print(constraints_str)
        else:
            print("No constraints defined")

        # Print task prompt
        print("\n" + "-" * 80)
        print("📝 TASK PROMPT:")
        print("-" * 80)
        print(task.prompt)

        print("\n" + "=" * 80)
        print("🤖 Sending to GPT for review...")
        print("=" * 80 + "\n")

    async def _evaluate_solution_with_seed(self, api_prompt: str, api_tests: list[dict[str, Any]], api_start_url: str, use_case: Any, seed: int, base_actions: list[BaseAction]) -> dict[str, Any]:
        """
        Create a task from API prompt with a specific seed value and evaluate the solution against it

        Args:
            api_prompt: Prompt from IWAP API
            api_tests: Tests from IWAP API
            api_start_url: Start URL from IWAP API
            use_case: Use case object
            seed: The seed value to use
            base_actions: List of BaseAction objects from IWAP API solution

        Returns:
            Dictionary with evaluation results
        """
        try:
            from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest

            # Update URL with new seed
            parsed = urlparse(api_start_url)
            query_params = parse_qs(parsed.query)
            query_params["seed"] = [str(seed)]
            new_query = urlencode(query_params, doseq=True)
            seeded_url = urlunparse(parsed._replace(query=new_query))

            # Convert API tests to CheckEventTest objects
            tests = []
            for api_test in api_tests:
                # Try to create CheckEventTest from API test structure
                # API test might have different structure, adapt as needed
                test_type = api_test.get("type", "CheckEventTest")
                if test_type == "CheckEventTest" or "CheckEvent" in test_type:
                    event_name = api_test.get("event_name") or api_test.get("eventName") or use_case.name
                    event_criteria = api_test.get("event_criteria") or api_test.get("criteria") or {}
                    tests.append(
                        CheckEventTest(
                            type="CheckEventTest",
                            event_name=event_name,
                            event_criteria=event_criteria,
                        )
                    )

            # Create Task from API prompt
            task = Task(
                use_case=use_case,
                prompt=api_prompt,
                url=seeded_url,
                tests=tests,
                web_project_id=self.web_project.id,
            )

            # Extract seed values from URL
            seed_value = self._extract_seed_from_url(task.url)
            v2_seed_value = self._extract_v2_seed_from_url(task.url)

            # Get constraints
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Print task details before evaluation
            print("\n" + "=" * 80)
            print(f"🔄 STEP 3: DYNAMIC VERIFICATION (Seed: {seed})")
            print("=" * 80)
            print(f"Task ID: {task.id}")
            print(f"Use Case: {use_case.name}")
            print(f"Seed: {seed_value}")
            print(f"V2 Seed: {v2_seed_value}")
            print(f"Constraints: {constraints_str}")
            print(f"Solution Actions: {len(base_actions)}")
            print("-" * 80)

            # Update NavigateAction URLs to match the task seed
            # The evaluator checks that all NavigateAction URLs have the same seed as the task URL
            from autoppia_iwa.src.execution.actions.actions import NavigateAction

            updated_actions = []
            task_seed = self._extract_seed_from_url(task.url)

            for action in base_actions:
                if isinstance(action, NavigateAction) and action.url:
                    # Update the NavigateAction URL to use the same seed as the task
                    parsed = urlparse(action.url)
                    query_params = parse_qs(parsed.query)
                    if task_seed is not None:
                        query_params["seed"] = [str(task_seed)]
                    new_query = urlencode(query_params, doseq=True)
                    updated_url = urlunparse(parsed._replace(query=new_query))
                    # Create a new NavigateAction with updated URL
                    updated_action = NavigateAction(
                        url=updated_url,
                        go_back=action.go_back if hasattr(action, "go_back") else False,
                        go_forward=action.go_forward if hasattr(action, "go_forward") else False,
                    )
                    updated_actions.append(updated_action)
                else:
                    updated_actions.append(action)

            # Create TaskSolution from the updated actions
            task_solution = TaskSolution(
                task_id=task.id,
                actions=updated_actions,
                web_agent_id="iwap_solution",
            )

            # Evaluate the solution
            logger.info(f"Evaluating solution against task {task.id} with seed {seed}")
            evaluator = ConcurrentEvaluator(
                self.web_project,
                EvaluatorConfig(
                    enable_grouping_tasks=False,
                    chunk_size=1,
                    should_record_gif=False,
                    verbose_logging=False,
                ),
            )

            evaluation_result = await evaluator.evaluate_single_task_solution(task, task_solution)

            # Print evaluation results
            score = evaluation_result.final_score
            tests_passed = evaluation_result.stats.tests_passed if evaluation_result.stats else 0
            total_tests = evaluation_result.stats.total_tests if evaluation_result.stats else 0

            print("Evaluation Result:")
            print(f"  Score: {score}")
            print(f"  Tests Passed: {tests_passed}/{total_tests}")
            print(f"  Success: {'✓ YES' if score == 1.0 else '✗ NO'}")
            if evaluation_result.stats and evaluation_result.stats.error_message:
                print(f"  Error: {evaluation_result.stats.error_message}")
            print("=" * 80 + "\n")

            # Serialize constraints
            serialized_constraints = self._serialize_constraints(constraints) if constraints else None

            return {
                "success": True,
                "task_id": task.id,
                "prompt": task.prompt,
                "constraints": serialized_constraints,
                "constraints_str": constraints_str,
                "seed": seed_value,
                "v2_seed": v2_seed_value,
                "evaluation": {
                    "final_score": score,
                    "tests_passed": tests_passed,
                    "total_tests": total_tests,
                    "success": score == 1.0,
                    "error": evaluation_result.stats.error_message if evaluation_result.stats else None,
                },
            }

        except Exception as e:
            logger.error(f"Error evaluating solution with seed {seed}: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _serialize_constraints(self, constraints: list[dict]) -> list[dict]:
        """
        Serialize constraints list, converting Enum operators to strings

        Args:
            constraints: List of constraint dictionaries with Enum operators

        Returns:
            List of serialized constraint dictionaries
        """
        from enum import Enum

        serialized = []
        for constraint in constraints:
            if not isinstance(constraint, dict):
                continue

            serialized_constraint = {}
            for key, value in constraint.items():
                # Convert Enum to its value
                if isinstance(value, Enum):
                    serialized_constraint[key] = value.value
                elif isinstance(value, str | int | float | bool | type(None)):
                    serialized_constraint[key] = value
                elif isinstance(value, list | tuple):
                    # Recursively serialize list items
                    serialized_constraint[key] = [item.value if isinstance(item, Enum) else item for item in value]
                else:
                    # Try to convert to string for other types
                    serialized_constraint[key] = str(value)

            serialized.append(serialized_constraint)

        return serialized
