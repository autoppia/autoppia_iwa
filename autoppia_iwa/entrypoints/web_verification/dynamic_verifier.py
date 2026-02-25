"""
Dynamic Verifier for testing tasks with different seed values

This verifier evaluates solutions from IWAP API against tasks generated with different seed values,
ensuring the solution works correctly across different dynamic content.
"""

import hashlib
import json
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
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
        base_actions = self._convert_solution_actions(solution_actions)
        if base_actions is None:
            return {
                "error": "Failed to convert solution actions",
                "all_passed": False,
            }

        # Process each seed
        for seed in seed_values:
            seed_result, seed_passed = await self._process_seed_verification(api_prompt, api_tests, api_start_url, use_case, seed, base_actions, solution_actions)
            results[seed] = seed_result
            if not seed_passed:
                all_passed = False

        # Generate summary
        summary, passed_count, total_count = self._generate_verification_summary(results, solution_actions)

        return {
            "use_case_name": use_case.name,
            "seeds_tested": seed_values,
            "results": results,
            "all_passed": all_passed,
            "passed_count": passed_count,
            "total_count": total_count,
            "summary": summary,
            "needs_review": all_passed and passed_count == total_count and total_count >= 3,
        }

    def _convert_solution_actions(self, solution_actions: list[dict[str, Any]]) -> list[BaseAction] | None:
        """Convert solution actions from API format to BaseAction objects."""
        if not solution_actions:
            return None

        try:
            normalized_actions = []
            for action in solution_actions:
                normalized = self._normalize_action(action)
                if normalized is not None:
                    normalized_actions.append(normalized)

            base_actions = [BaseAction.create_action(action) for action in normalized_actions]
            base_actions = [a for a in base_actions if a is not None]
            logger.info(f"Converted {len(base_actions)} actions from API solution (normalized {len(normalized_actions)} actions)")
            return base_actions
        except Exception as e:
            logger.error(f"Error converting solution actions: {e}")
            return None

    async def _process_seed_verification(
        self,
        api_prompt: str,
        api_tests: list[dict[str, Any]],
        api_start_url: str,
        use_case: Any,
        seed: int,
        base_actions: list[BaseAction],
        solution_actions: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], bool]:
        """Process verification for a single seed and return result with success status."""
        try:
            seed_result = await self._evaluate_solution_with_seed(api_prompt, api_tests, api_start_url, use_case, seed, base_actions)
            seed_passed = self._check_seed_result(seed_result, solution_actions)
            return seed_result, seed_passed
        except Exception as e:
            logger.error(f"Error processing task with seed {seed}: {e}")
            return {
                "success": False,
                "error": str(e),
            }, False

    def _check_seed_result(self, seed_result: dict[str, Any], solution_actions: list[dict[str, Any]]) -> bool:
        """Check if seed result passed evaluation or generation."""
        if solution_actions:
            # Usamos tolerancia (1e-9) en lugar de == porque los números flotantes pueden tener errores de precisión
            final_score = seed_result.get("evaluation", {}).get("final_score", 0)
            return abs(final_score - 1.0) < 1e-9
        else:
            generation_success = seed_result.get("success", False)
            llm_valid = seed_result.get("llm_review", {}).get("valid", True) if seed_result.get("llm_review") else True
            return generation_success and llm_valid

    def _generate_verification_summary(self, results: dict[int, dict[str, Any]], solution_actions: list[dict[str, Any]]) -> tuple[str, int, int]:
        """Generate summary string and counts for verification results."""
        total_count = len(results)
        if solution_actions:
            # Usamos tolerancia (1e-9) en lugar de == porque los números flotantes pueden tener errores de precisión
            passed_count = sum(1 for r in results.values() if abs(r.get("evaluation", {}).get("final_score", 0) - 1.0) < 1e-9)
            summary = f"Dynamic verification: {passed_count}/{total_count} seeds passed evaluation. Solution works correctly with {passed_count} different seed values."
            if passed_count == total_count and total_count >= 3:
                summary += (
                    f"\n⚠️  WARNING: This use case may not be truly dynamic. The same solution works for all {total_count} seeds, suggesting the dynamic system might not be affecting this use case."
                )
        else:
            passed_count = sum(1 for r in results.values() if r.get("success", False) and r.get("llm_review", {}).get("valid", True))
            summary = f"Dynamic verification: {passed_count}/{total_count} seeds passed. Tasks can be generated and validated with {passed_count} different seed values."
        return summary, passed_count, total_count

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

            # Extract seed value from URL
            seed_value = self._extract_seed_from_url(task.url)

            # Get constraints
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Print task details before LLM review
            self._print_task_details_for_review(task, seed_value, constraints_str, is_dynamic=True)

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

    def _normalize_action(self, action: dict[str, Any]) -> dict[str, Any] | None:
        """
        Normalize action from API format to format expected by BaseAction.create_action()

        Args:
            action: Action dictionary from API

        Returns:
            Normalized action dictionary or None if invalid
        """
        normalized = action.copy()

        # Handle nested 'attributes' structure: flatten it
        if "attributes" in normalized and isinstance(normalized["attributes"], dict):
            attributes = normalized.pop("attributes")
            normalized.update(attributes)

        # Normalize action type
        normalized["type"] = self._normalize_action_type(normalized.get("type", ""))

        # Validate and normalize specific action types
        if normalized["type"] == "NavigateAction":
            if not self._validate_navigate_action(normalized):
                return None
        elif normalized["type"] == "WaitAction":
            self._normalize_wait_action(normalized)
        elif normalized["type"] == "TypeAction":
            if not self._validate_type_action(normalized):
                return None
        elif normalized["type"] == "SelectDropDownOptionAction":
            if not self._validate_select_dropdown_action(normalized):
                return None
        elif normalized["type"] == "ClickAction" and not self._validate_click_action(normalized):
            return None

        # Normalize selector
        if not self._normalize_selector(normalized):
            return None

        return normalized

    def _normalize_action_type(self, action_type: str) -> str:
        """Normalize action type string to expected format."""
        action_type_lower = action_type.lower()
        type_mapping = {
            "navigate": "NavigateAction",
            "click": "ClickAction",
            "input": "TypeAction",
            "type": "TypeAction",
            "wait": "WaitAction",
            "selectdropdownoption": "SelectDropDownOptionAction",
            "select": "SelectDropDownOptionAction",
        }

        if action_type_lower in type_mapping:
            return type_mapping[action_type_lower]
        elif not action_type_lower.endswith("action"):
            return action_type_lower.capitalize() + "Action"
        return action_type

    def _validate_navigate_action(self, normalized: dict[str, Any]) -> bool:
        """Validate NavigateAction has required fields."""
        return bool(normalized.get("url") or normalized.get("go_back") or normalized.get("go_forward"))

    def _normalize_wait_action(self, normalized: dict[str, Any]) -> None:
        """Normalize WaitAction fields."""
        if "timeout_seconds" in normalized and "time_seconds" not in normalized:
            normalized["time_seconds"] = normalized.pop("timeout_seconds")
        if not normalized.get("selector") and not normalized.get("time_seconds"):
            normalized["time_seconds"] = 1.0

    def _validate_type_action(self, normalized: dict[str, Any]) -> bool:
        """Validate TypeAction has non-empty text field."""
        if "value" in normalized and "text" not in normalized:
            normalized["text"] = normalized.pop("value")
        text_value = normalized.get("text")
        if "text" not in normalized or not text_value or (isinstance(text_value, str) and not text_value.strip()):
            logger.warning(f"TypeAction has empty or missing 'text' field, skipping action: {normalized}")
            return False
        return True

    def _validate_select_dropdown_action(self, normalized: dict[str, Any]) -> bool:
        """Validate SelectDropDownOptionAction has non-empty text field."""
        text_value = normalized.get("text")
        if "text" not in normalized or not text_value or (isinstance(text_value, str) and not text_value.strip()):
            logger.warning(f"SelectDropDownOptionAction has empty or missing 'text' field, skipping action: {normalized}")
            return False
        return True

    def _validate_click_action(self, normalized: dict[str, Any]) -> bool:
        """Validate ClickAction has selector or coordinates."""
        has_selector = "selector" in normalized and normalized["selector"] is not None
        has_coords = "x" in normalized and "y" in normalized and normalized.get("x") is not None and normalized.get("y") is not None
        if not has_selector and not has_coords:
            logger.warning(f"ClickAction missing selector or coordinates, skipping action: {normalized}")
            return False
        return True

    def _normalize_selector(self, normalized: dict[str, Any]) -> bool:
        """Normalize selector format and validate. Returns False if action should be skipped."""
        if "selector" not in normalized or normalized["selector"] is None:
            return True

        if not isinstance(normalized["selector"], dict):
            if normalized["type"] in ["ClickAction", "TypeAction", "SelectDropDownOptionAction"]:
                logger.warning(f"{normalized['type']} has invalid selector type, skipping action")
                return False
            return True

        selector_dict = normalized["selector"]
        selector_type_str = selector_dict.get("type", "").lower()

        # Map selector types to expected format
        if selector_type_str in ["xpathselector", "xpath"]:
            normalized["selector"]["type"] = "xpathSelector"
        elif selector_type_str in ["attributevalueselector", "attribute"]:
            normalized["selector"]["type"] = "attributeValueSelector"
        elif not selector_type_str:
            # Infer type from value
            selector_value = selector_dict.get("value", "")
            if selector_value and (selector_value.startswith("//") or selector_value.startswith("(//")):
                normalized["selector"]["type"] = "xpathSelector"
            else:
                normalized["selector"]["type"] = "attributeValueSelector"

        # Validate selector value
        selector_value = normalized["selector"].get("value")
        if not selector_value or (isinstance(selector_value, str) and not selector_value.strip()):
            if normalized["type"] in ["ClickAction", "TypeAction", "SelectDropDownOptionAction"]:
                logger.warning(f"{normalized['type']} has invalid selector (empty value), skipping action")
                return False
            normalized.pop("selector", None)

        return True

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

    def _print_task_details_for_review(self, task: Task, seed: int | None, constraints_str: str, is_dynamic: bool = False):
        """
        Print task details (prompt, constraints, seed) before GPT review

        Args:
            task: The task to print
            seed: Seed value from URL
            constraints_str: String representation of constraints
            is_dynamic: Whether this is for dynamic verification
        """
        prefix = "🔄 DYNAMIC" if is_dynamic else "📋"
        print("\n" + "=" * 80)
        print(f"{prefix} TASK DETAILS FOR GPT REVIEW")
        print("=" * 80)
        print(f"Task ID: {task.id}")
        print(f"Use Case: {task.use_case.name if task.use_case else 'Unknown'}")

        # Print seed value
        if seed is not None:
            print(f"Seed: {seed}")
        else:
            print("Seed: None (no dynamic seed)")

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
            # Update URL with new seed
            parsed = urlparse(api_start_url)
            query_params = parse_qs(parsed.query)
            query_params["seed"] = [str(seed)]
            new_query = urlencode(query_params, doseq=True)
            seeded_url = urlunparse(parsed._replace(query=new_query))

            # Convert API tests to CheckEventTest objects and create task
            tests = self._convert_api_tests_to_check_event_tests(api_tests, use_case)
            task = self._create_task_from_api(api_prompt, seeded_url, use_case, tests)

            # Extract seed value and constraints
            seed_value = self._extract_seed_from_url(task.url)
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Print task details before evaluation
            self._print_evaluation_task_details(task, use_case, seed_value, constraints_str, len(base_actions), seed)

            # Update NavigateAction URLs to match the task seed
            updated_actions = self._update_navigate_actions_with_seed(base_actions, task.url)

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
            self._print_evaluation_results(evaluation_result, score)

            # Serialize constraints
            serialized_constraints = self._serialize_constraints(constraints) if constraints else None

            # Serialize actions for analysis
            serialized_actions = self._serialize_actions(updated_actions) if updated_actions else []

            return {
                "success": True,
                "task_id": task.id,
                "prompt": task.prompt,
                "constraints": serialized_constraints,
                "constraints_str": constraints_str,
                "seed": seed_value,
                "actions": serialized_actions,  # Include actions executed
                "evaluation": {
                    "final_score": score,
                    "tests_passed": evaluation_result.stats.tests_passed if evaluation_result.stats else 0,
                    "total_tests": evaluation_result.stats.total_tests if evaluation_result.stats else 0,
                    # Usamos tolerancia (1e-9) en lugar de == porque los números flotantes pueden tener errores de precisión
                    "success": abs(score - 1.0) < 1e-9,
                    "error": evaluation_result.stats.error_message if evaluation_result.stats else None,
                },
            }

        except Exception as e:
            logger.error(f"Error evaluating solution with seed {seed}: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _convert_api_tests_to_check_event_tests(self, api_tests: list[dict[str, Any]], use_case: Any) -> list:
        """Convert API test dictionaries to CheckEventTest objects."""
        from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest

        tests = []
        for api_test in api_tests:
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
        return tests

    def _create_task_from_api(self, api_prompt: str, seeded_url: str, use_case: Any, tests: list) -> Task:
        """Create Task object from API prompt and tests."""
        return Task(
            use_case=use_case,
            prompt=api_prompt,
            url=seeded_url,
            tests=tests,
            web_project_id=self.web_project.id,
        )

    def _print_evaluation_task_details(self, task: Task, use_case: Any, seed_value: int | None, constraints_str: str, num_actions: int, seed: int) -> None:
        """Print task details before evaluation."""
        print("\n" + "=" * 80)
        print(f"🔄 STEP 4: DYNAMIC VERIFICATION (Seed: {seed})")
        print("=" * 80)
        print(f"Task ID: {task.id}")
        print(f"Use Case: {use_case.name}")
        print(f"Seed: {seed_value}")
        print(f"Constraints: {constraints_str}")
        print(f"Solution Actions: {num_actions}")
        print("-" * 80)

    def _update_navigate_actions_with_seed(self, base_actions: list[BaseAction], task_url: str) -> list[BaseAction]:
        """Update NavigateAction URLs to match the task seed."""
        from autoppia_iwa.src.execution.actions.actions import NavigateAction

        updated_actions = []
        task_seed = self._extract_seed_from_url(task_url)

        for action in base_actions:
            if isinstance(action, NavigateAction) and action.url:
                parsed = urlparse(action.url)
                query_params = parse_qs(parsed.query)
                if task_seed is not None:
                    query_params["seed"] = [str(task_seed)]
                new_query = urlencode(query_params, doseq=True)
                updated_url = urlunparse(parsed._replace(query=new_query))
                updated_action = NavigateAction(
                    url=updated_url,
                    go_back=action.go_back if hasattr(action, "go_back") else False,
                    go_forward=action.go_forward if hasattr(action, "go_forward") else False,
                )
                updated_actions.append(updated_action)
            else:
                updated_actions.append(action)

        return updated_actions

    def _print_evaluation_results(self, evaluation_result: Any, score: float) -> None:
        """Print evaluation results to console."""
        tests_passed = evaluation_result.stats.tests_passed if evaluation_result.stats else 0
        total_tests = evaluation_result.stats.total_tests if evaluation_result.stats else 0

        print("Evaluation Result:")
        print(f"  Score: {score}")
        print(f"  Tests Passed: {tests_passed}/{total_tests}")
        # Usamos tolerancia (1e-9) en lugar de == porque los números flotantes pueden tener errores de precisión
        is_success = abs(score - 1.0) < 1e-9
        print(f"  Success: {'✓ YES' if is_success else '✗ NO'}")
        if evaluation_result.stats and evaluation_result.stats.error_message:
            print(f"  Error: {evaluation_result.stats.error_message}")
        print("=" * 80 + "\n")

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

    def _serialize_actions(self, actions: list[BaseAction]) -> list[dict[str, Any]]:
        """
        Serialize actions list to JSON-compatible format

        Args:
            actions: List of BaseAction objects

        Returns:
            List of serialized action dictionaries
        """
        serialized = []
        for action in actions:
            try:
                action_dict = self._get_action_dict(action)
                cleaned_dict = self._clean_action_dict(action_dict)
                serialized.append(cleaned_dict)
            except Exception as e:
                logger.warning(f"Error serializing action {action}: {e}")
                serialized.append({"type": str(type(action).__name__), "error": f"Could not serialize: {e}"})

        return serialized

    def _get_action_dict(self, action: BaseAction) -> dict[str, Any]:
        """Get action dictionary from BaseAction object."""
        if hasattr(action, "model_dump"):
            return action.model_dump()
        elif hasattr(action, "dict"):
            return action.dict()
        else:
            return action.__dict__.copy()

    def _clean_action_dict(self, action_dict: dict[str, Any]) -> dict[str, Any]:
        """Clean action dictionary by removing None values and normalizing selector."""
        cleaned_dict = {}
        for key, value in action_dict.items():
            if value is not None and key not in ["_sa_instance_state"]:
                if key == "selector" and isinstance(value, dict):
                    cleaned_dict["selector"] = {
                        "type": value.get("type"),
                        "value": value.get("value"),
                    }
                else:
                    cleaned_dict[key] = value
        return cleaned_dict

    async def verify_dataset_diversity_with_seeds(
        self,
        seed_values: list[int],
    ) -> dict[str, Any]:
        """
        V2 Verification: Verify that datasets are different with different seeds.

        Makes 3 HTTP requests (via _load_dataset) with different seeds and verifies
        that the returned datasets are actually different, ensuring the dynamic
        data generation is working correctly.

        Args:
            seed_values: List of seed values to test (should be 3)

        Returns:
            Dictionary with verification results:
            {
                "seeds_tested": List[int],
                "all_different": bool,  # True if all datasets are different
                "datasets_info": Dict[int, Dict],  # Info per seed
                "comparison_results": List[Dict],  # Pairwise comparisons
                "passed": bool,  # True if all datasets are different
                "summary": str
            }
        """
        logger.info(f"V2 Verification: Testing dataset diversity for {self.web_project.name} with seeds: {seed_values}")

        # Load datasets for all seeds
        datasets, datasets_info = await self._load_datasets_for_seeds(seed_values)

        # Compare datasets pairwise
        comparison_results, all_different = self._compare_datasets_pairwise(datasets, datasets_info)

        # Generate summary
        summary, passed = self._generate_diversity_summary(datasets, seed_values, all_different)

        return {
            "seeds_tested": seed_values,
            "all_different": all_different,
            "datasets_info": datasets_info,
            "comparison_results": comparison_results,
            "passed": passed,
            "summary": summary,
            "loaded_count": len(datasets),
            "expected_count": len(seed_values),
        }

    async def _load_datasets_for_seeds(self, seed_values: list[int]) -> tuple[dict[int, dict], dict[int, dict[str, Any]]]:
        """Load datasets for all seed values and return datasets and info dictionaries."""
        datasets = {}
        datasets_info = {}

        for seed in seed_values:
            dataset, info = await self._load_dataset_for_seed(seed)
            if dataset is not None:
                datasets[seed] = dataset
            datasets_info[seed] = info

        return datasets, datasets_info

    async def _load_dataset_for_seed(self, seed: int) -> tuple[dict | None, dict[str, Any]]:
        """Load dataset for a single seed and return dataset and info."""
        try:
            dataset = await self.task_generator._load_dataset(seed)

            if dataset is None or dataset == {}:
                return None, {
                    "success": False,
                    "error": "Dataset returned None",
                    "hash": None,
                    "entity_count": 0,
                    "total_items": 0,
                }

            # Calculate hash of dataset for comparison
            # Using SHA256 instead of MD5 for security (SonarCloud S4790)
            dataset_str = json.dumps(dataset, sort_keys=True)
            dataset_hash = hashlib.sha256(dataset_str.encode()).hexdigest()

            # Count entities and items
            entity_count = len(dataset)
            total_items = sum(len(v) for v in dataset.values() if isinstance(v, list))

            info = {
                "success": True,
                "hash": dataset_hash,
                "entity_count": entity_count,
                "total_items": total_items,
                "entities": list(dataset.keys()),
            }

            logger.info(f"  Seed {seed}: loaded {total_items} items across {entity_count} entities (hash: {dataset_hash[:8]}...)")
            return dataset, info

        except Exception as e:
            logger.error(f"Error loading dataset for seed {seed}: {e}")
            return None, {
                "success": False,
                "error": str(e),
                "hash": None,
                "entity_count": 0,
                "total_items": 0,
            }

    def _compare_datasets_pairwise(self, datasets: dict[int, dict], datasets_info: dict[int, dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
        """Compare datasets pairwise and return comparison results and all_different flag."""
        comparison_results = []
        all_different = True

        seed_list = sorted(datasets.keys())
        for i in range(len(seed_list)):
            for j in range(i + 1, len(seed_list)):
                seed1, seed2 = seed_list[i], seed_list[j]
                hash1 = datasets_info[seed1].get("hash")
                hash2 = datasets_info[seed2].get("hash")

                if hash1 is None or hash2 is None:
                    comparison_results.append(
                        {
                            "seed1": seed1,
                            "seed2": seed2,
                            "different": None,
                            "reason": "One or both datasets failed to load",
                        }
                    )
                    all_different = False
                    continue

                are_different = hash1 != hash2
                entities1 = set(datasets_info[seed1].get("entities", []))
                entities2 = set(datasets_info[seed2].get("entities", []))
                entities_differ = entities1 != entities2

                comparison_results.append(
                    {
                        "seed1": seed1,
                        "seed2": seed2,
                        "different": are_different,
                        "hash1": hash1[:8],
                        "hash2": hash2[:8],
                        "entities_differ": entities_differ,
                        "entities1": list(entities1),
                        "entities2": list(entities2),
                    }
                )

                if not are_different:
                    all_different = False
                    logger.warning(f"  ⚠️  Datasets for seeds {seed1} and {seed2} are IDENTICAL (hash: {hash1[:8]})")
                else:
                    if entities_differ:
                        logger.info(f"  ✓ Datasets for seeds {seed1} and {seed2} are different (different entities)")
                    else:
                        logger.info(f"  ✓ Datasets for seeds {seed1} and {seed2} are different (same entities, different data)")

        return comparison_results, all_different

    def _generate_diversity_summary(self, datasets: dict[int, dict], seed_values: list[int], all_different: bool) -> tuple[str, bool]:
        """Generate summary string and passed flag for diversity verification."""
        passed = all_different and len(datasets) == len(seed_values)

        if not datasets:
            summary = "V2 Verification: FAILED - No datasets could be loaded for any seed"
        elif passed:
            summary = f"V2 Verification: PASSED - All {len(seed_values)} datasets are different. Dynamic data generation is working correctly."
        else:
            if not all_different:
                summary = "V2 Verification: FAILED - Some datasets are identical. The dynamic system may not be affecting data generation for this project."
            else:
                summary = f"V2 Verification: FAILED - Only {len(datasets)}/{len(seed_values)} datasets loaded successfully."

        return summary, passed
