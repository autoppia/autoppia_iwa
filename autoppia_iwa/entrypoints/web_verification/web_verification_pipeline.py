"""
Web Verification Pipeline

Main pipeline that orchestrates:
1. Task generation (2 tasks per use case with constraints)
2. GPT review of tasks and constraints (does prompt accurately represent constraints?)
3. IWAP doability check
4. Dynamic verification with different seeds
"""

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer

from .config import WebVerificationConfig
from .dynamic_verifier import DynamicVerifier
from .iwap_client import IWAPClient
from .llm_reviewer import LLMReviewer


class WebVerificationPipeline:
    """Main pipeline for web verification"""

    def __init__(
        self,
        web_project: WebProject,
        config: WebVerificationConfig,
        llm_service=None,
    ):
        """
        Initialize Web Verification Pipeline

        Args:
            web_project: The web project to verify
            config: Configuration for the pipeline
            llm_service: Optional LLM service (will use DIContainer if not provided)
        """
        self.web_project = web_project
        self.config = config
        self.llm_service = llm_service or DIContainer.llm_service()

        # Initialize components
        self.task_generator = SimpleTaskGenerator(
            web_project=web_project,
            llm_service=self.llm_service,
        )

        self.iwap_client = (
            IWAPClient(
                base_url=config.iwap_base_url or "https://api-leaderboard.autoppia.com",
                api_key=config.iwap_api_key,
                timeout_seconds=config.iwap_timeout_seconds,
                use_mock=config.iwap_use_mock,
            )
            if config.iwap_enabled
            else None
        )

        self.llm_reviewer = (
            LLMReviewer(
                llm_service=self.llm_service,
                timeout_seconds=config.llm_timeout_seconds,
            )
            if config.llm_review_enabled
            else None
        )

        self.dynamic_verifier = (
            DynamicVerifier(
                web_project=web_project,
                llm_reviewer=self.llm_reviewer,
            )
            if config.dynamic_verification_enabled
            else None
        )

        # Results storage
        self.results: dict[str, Any] = {
            "project_id": web_project.id,
            "project_name": web_project.name,
            "use_cases": {},
        }

    async def run(self) -> dict[str, Any]:
        """
        Run the complete verification pipeline

        Returns:
            Dictionary with complete verification results
        """
        logger.info(f"Starting web verification pipeline for project: {self.web_project.name} ({self.web_project.id})")

        if not self.web_project.use_cases:
            logger.warning(f"No use cases found for project {self.web_project.id}")
            return self.results

        # Process each use case
        for use_case in self.web_project.use_cases:
            logger.info(f"Processing use case: {use_case.name}")
            use_case_results = await self._process_use_case(use_case)
            self.results["use_cases"][use_case.name] = use_case_results

        # Save results
        await self._save_results()

        logger.info("Web verification pipeline completed")
        return self.results

    async def _process_use_case(self, use_case: UseCase) -> dict[str, Any]:
        """
        Process a single use case through all verification steps

        Args:
            use_case: The use case to process

        Returns:
            Dictionary with results for this use case
        """
        use_case_results = {
            "use_case_name": use_case.name,
            "use_case_description": getattr(use_case, "description", ""),
            "tasks": [],
            "llm_reviews": [],
            "doability_check": None,
            "dynamic_verification": None,  # Will be set in Step 3 if solution is available
        }

        # Step 1: Generate tasks (2 per use case) with constraints
        # Generate each task separately with different seeds to ensure variety
        logger.info(f"Generating {self.config.tasks_per_use_case} tasks for use case: {use_case.name}")
        tasks = []

        for task_index in range(self.config.tasks_per_use_case):
            # Clear constraints from use_case before generating new task
            # This ensures each task gets fresh constraints based on its own seed
            use_case.constraints = None

            # Generate one task at a time - each will get a different random seed
            task_list = await self.task_generator.generate_tasks_for_use_case(
                use_case=use_case,
                number_of_prompts=1,  # Generate one at a time
                dynamic=self.config.dynamic_enabled,
            )

            if task_list and len(task_list) > 0:
                task = task_list[0]
                # IMPORTANT: The task.use_case is a reference to the shared use_case object.
                # We need to create a copy of the use_case for this task to preserve the constraints
                # that were just generated, before they get overwritten by the next task generation.
                if use_case.constraints and task.use_case:
                    import copy

                    # Create a copy of the use_case object so each task has its own independent use_case
                    # with its own constraints. This prevents constraints from being overwritten.
                    task.use_case = copy.deepcopy(use_case)
                    logger.debug(f"Created independent use_case copy for task {task_index + 1} with {len(task.use_case.constraints)} constraints")

                tasks.append(task)
                logger.debug(f"Generated task {task_index + 1}/{self.config.tasks_per_use_case} for use case: {use_case.name} with seed: {self._extract_seed_from_url(task.url)}")

        if not tasks:
            logger.warning(f"No tasks generated for use case: {use_case.name}")
            use_case_results["error"] = "No tasks generated"
            return use_case_results

        logger.info(f"Generated {len(tasks)} tasks for use case: {use_case.name}")

        # Step 1: LLM review - check if prompts accurately represent constraints (review all tasks first)
        for task in tasks:
            # Extract seed value from task URL
            seed_value = self._extract_seed_from_url(task.url)
            # v2_seed_value = self._extract_v2_seed_from_url(task.url)

            # Get constraints
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Serialize constraints to make them JSON-compatible
            serialized_constraints = self._serialize_constraints(constraints) if constraints else None

            task_info = {
                "task_id": task.id,
                "prompt": task.prompt,
                "constraints": serialized_constraints,
                "constraints_str": constraints_str,
                "seed": seed_value,
                # "v2_seed": v2_seed_value,
            }
            use_case_results["tasks"].append(task_info)

            # Print task details before GPT review
            if self.llm_reviewer:
                self._print_task_details_for_review(task=task, seed=seed_value, constraints_str=constraints_str)
                logger.info(f"Reviewing task {task.id} with LLM: checking if prompt matches constraints")
                review_result = await self.llm_reviewer.review_task_and_constraints(task)
                review_result["task_id"] = task.id
                use_case_results["llm_reviews"].append(review_result)

        # Step 2: IWAP API call - proceed if enabled and (LLM reviews are valid or review is disabled)
        if self.iwap_client:
            all_reviews_valid = True
            if self.llm_reviewer:
                llm_reviews = use_case_results.get("llm_reviews", [])
                all_reviews_valid = all(review.get("valid", False) for review in llm_reviews) and len(llm_reviews) > 0

            if all_reviews_valid:
                print("\n" + "=" * 80)
                print("🔄 STEP 2: IWAP API CALL")
                print("=" * 80)
                print(f"Use Case: {use_case.name}")
                print(f"Project ID: {self.web_project.id}")
                if self.llm_reviewer:
                    print(f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}")
                    print("All LLM Reviews: VALID ✓")
                else:
                    print("LLM Review: DISABLED (proceeding without gating)")
                print("Calling IWAP API...")
                print("-" * 80)

                logger.info(f"Step 2: Proceeding to IWAP for use case {use_case.name} (LLM review {'enabled' if self.llm_reviewer else 'disabled'})")
                iwap_result = await self.iwap_client.get_tasks_with_solutions(
                    project_id=self.web_project.id,
                    use_case_name=use_case.name,
                    our_tasks=tasks,  # Pass tasks from Step 1 for better mock generation
                    page=1,
                    limit=50,
                )

                # Store IWAP result in use case results
                use_case_results["iwap_api_response"] = iwap_result

                # Print API response details
                if iwap_result:
                    success = iwap_result.get("success", False)
                    print(f"IWAP API Call: {'✓ SUCCESS' if success else '✗ FAILED'}")
                    if success:
                        api_data = iwap_result.get("data", {})
                        tasks_count = len(api_data.get("tasks", [])) if isinstance(api_data, dict) else 0
                        print(f"Tasks returned: {tasks_count}")
                        print(f"Website: {iwap_result.get('website', 'N/A')}")
                        print(f"Use Case: {iwap_result.get('use_case', 'N/A')}")

                        # Process API response and match with our generated tasks
                        print("\n" + "-" * 80)
                        print("🔍 PROCESSING API RESPONSE AND MATCHING WITH OUR TASKS")
                        print("-" * 80)

                        # Get our generated tasks
                        our_tasks = tasks  # tasks list from Step 1

                        # Process and match
                        match_result = self.iwap_client.process_api_response_for_tasks(iwap_result, our_tasks)

                        # Store match result
                        use_case_results["iwap_match_result"] = match_result

                        # Print match results
                        if match_result.get("matched", False):
                            match_type = match_result.get("match_type", "unknown")
                            reason = match_result.get("reason", "")
                            actions = match_result.get("actions", [])
                            api_task_id = match_result.get("api_task_id", "N/A")
                            api_intent = match_result.get("api_intent", "N/A")

                            print("✓ MATCH FOUND!")
                            print(f"  Match Type: {match_type}")
                            print(f"  Reason: {reason}")
                            print(f"  API Task ID: {api_task_id}")
                            print(f"  API Intent: {api_intent}")
                            print(f"  Actions Found: {len(actions) if actions else 0} actions")
                            if actions:
                                print(f"  First Action: {actions[0] if len(actions) > 0 else 'N/A'}")
                        else:
                            reason = match_result.get("reason", "Unknown reason")
                            print("✗ NO MATCH FOUND")
                            print(f"  ⚠️  WARNING: {reason}")
                            print(f"  ⚠️  WARNING: {reason}")
                    else:
                        error = iwap_result.get("error", "Unknown error")
                        print(f"Error: {error}")
                else:
                    print("IWAP API Call: ✗ FAILED (No response)")

                print("=" * 80 + "\n")

                logger.info(f"IWAP API response for {use_case.name}: success={iwap_result.get('success', False) if iwap_result else False}")

                # Step 3: Dynamic verification - evaluate solution with different seeds (if we got a solution)
                match_result = use_case_results.get("iwap_match_result", {})

                if match_result.get("matched", False) and match_result.get("actions"):
                    solution_actions = match_result.get("actions", [])
                    api_prompt = match_result.get("api_prompt", "")
                    api_tests = match_result.get("api_tests", [])
                    api_start_url = match_result.get("api_start_url", "")

                    print("\n" + "=" * 80)
                    print("🔄 STEP 3: DYNAMIC VERIFICATION")
                    print("=" * 80)
                    print(f"Use Case: {use_case.name}")
                    print(f"Using API Task Prompt: {api_prompt[:100]}..." if len(api_prompt) > 100 else f"Using API Task Prompt: {api_prompt}")
                    print(f"Evaluating solution with {len(solution_actions)} actions against different seeds")
                    print(f"Seeds to test: {self.config.seed_values}")
                    print("=" * 80 + "\n")

                    # manual testing
                    # if solution_actions:

                    # api_prompt = "Create a matter with the name that is NOT 'Tax Investigation', with client that is NOT equal to 'LegalEase Inc.', and status that is NOT equal to 'Active'."
                    # api_start_url = "http://localhost:8004/matters?seed=1"
                    # api_tests = "1) name not_contains Tax Investigation AND 2) client not_equals LegalEase Inc. AND 3) status not_equals Active"
                    if self.dynamic_verifier and self.config.dynamic_verification_enabled:
                        if api_prompt and api_start_url:
                            logger.info(
                                f"Step 3: Evaluating API solution against API task with different seeds for use case {use_case.name}"  # {use_case.name}
                            )
                            dynamic_result = await self.dynamic_verifier.verify_task_with_seeds(
                                api_prompt=api_prompt,
                                api_tests=api_tests,
                                api_start_url=api_start_url,
                                use_case=use_case,
                                seed_values=self.config.seed_values,
                                solution_actions=solution_actions,
                            )
                            use_case_results["dynamic_verification"] = dynamic_result

                            # Print summary
                            print("\n" + "=" * 80)
                            print("📊 STEP 3 SUMMARY")
                            print("=" * 80)
                            print(dynamic_result.get("summary", "No summary available"))
                            print(f"Passed: {dynamic_result.get('passed_count', 0)}/{dynamic_result.get('total_count', 0)}")
                            print("=" * 80 + "\n")
                        else:
                            logger.warning("No reference task available for dynamic verification")
                    else:
                        logger.info("Dynamic verification is disabled")
                else:
                    print("\n" + "=" * 80)
                    print("⏭️  STEP 3: SKIPPED")
                    print("=" * 80)
                    print(f"Use Case: {use_case.name}")
                    if not match_result.get("matched", False):
                        print("Reason: No solution found from IWAP API")
                    else:
                        print("Reason: No actions in solution")
                    print("=" * 80 + "\n")
            else:
                invalid_count = sum(1 for review in use_case_results.get("llm_reviews", []) if not review.get("valid", False))
                print("\n" + "=" * 80)
                print("⏭️  STEP 2: SKIPPED")
                print("=" * 80)
                print(f"Use Case: {use_case.name}")
                print(f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}")
                print(f"Invalid Reviews: {invalid_count}")
                print("Reason: Not all LLM reviews are valid")
                print("=" * 80 + "\n")
                logger.info(f"Step 2: Skipping IWAP API call for use case {use_case.name} because not all LLM reviews are valid")
        else:
            print("\n" + "=" * 80)
            print("⏭️  STEP 2: SKIPPED")
            print("=" * 80)
            print(f"Use Case: {use_case.name}")
            print("Reason: IWAP client is disabled (--no-iwap flag used)")
            print("=" * 80 + "\n")
            logger.info(f"Step 2: Skipping IWAP API call for use case {use_case.name} because IWAP client is disabled")

        # Note: IWAP doability check is now done per-task in Step 2 (when LLM review is valid)
        # Keeping this for backward compatibility if needed, but it's now integrated into Step 2
        return use_case_results

    async def _save_results(self):
        """Save verification results to file"""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"verification_{self.web_project.id}.json"

        # Convert results to JSON-serializable format
        results_dict = self._serialize_results(self.results)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {output_file}")

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
                else:
                    serialized_constraint[key] = self._serialize_results(value)

            serialized.append(serialized_constraint)

        return serialized

    def _serialize_results(self, results: Any) -> Any:
        """Recursively serialize results to JSON-compatible format"""
        import types
        from enum import Enum

        # Handle None
        if results is None:
            return None

        # Handle Enum objects (convert to their value)
        if isinstance(results, Enum):
            return results.value

        # Handle mappingproxy (e.g., from Enum.__dict__)
        if isinstance(results, types.MappingProxyType):
            return dict(results)

        # Handle dictionaries
        if isinstance(results, dict):
            return {k: self._serialize_results(v) for k, v in results.items()}

        # Handle lists and tuples
        if isinstance(results, list | tuple):
            return [self._serialize_results(item) for item in results]

        # Handle Pydantic models
        if hasattr(results, "model_dump"):
            return self._serialize_results(results.model_dump())

        # Handle objects with __dict__
        if hasattr(results, "__dict__"):
            return self._serialize_results(results.__dict__)

        # Handle basic JSON-serializable types
        if isinstance(results, str | int | float | bool):
            return results

        # For any other type, try to convert to string
        try:
            # Try to get string representation
            return str(results)
        except Exception:
            # If all else fails, return None
            return None

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

    def _print_task_details_for_review(self, task: Task, seed: int | None, constraints_str: str, v2_seed: int | None | None = None):
        """
        Print task details (prompt, constraints, seed) before GPT review

        Args:
            task: The task to print
            seed: Base seed value from URL
            v2_seed: V2 seed value from URL
            constraints_str: String representation of constraints
        """
        print("\n" + "=" * 80)
        print("📋 TASK DETAILS FOR GPT REVIEW")
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

    def get_summary(self) -> str:
        """
        Get a human-readable summary of verification results

        Returns:
            Summary string
        """
        summary_lines = [
            f"\n{'=' * 60}",
            f"Web Verification Summary: {self.web_project.name}",
            f"{'=' * 60}",
        ]

        for use_case_name, use_case_data in self.results["use_cases"].items():
            summary_lines.append(f"\nUse Case: {use_case_name}")

            # Task results
            tasks = use_case_data.get("tasks", [])
            summary_lines.append(f"  Tasks Generated: {len(tasks)}")

            # LLM reviews
            reviews = use_case_data.get("llm_reviews", [])
            if reviews:
                valid_reviews = sum(1 for r in reviews if r.get("valid", False))
                avg_score = sum(r.get("score", 0.0) for r in reviews) / len(reviews) if reviews else 0.0
                summary_lines.append(f"  LLM Reviews: {valid_reviews}/{len(reviews)} valid (avg score: {avg_score:.2f})")

            # Doability check
            doability = use_case_data.get("doability_check")
            if doability:
                is_doable = doability.get("doable", False)
                success_rate = doability.get("success_rate", 0.0)
                summary_lines.append(f"  Doability: {'✓ Doable' if is_doable else '✗ Not doable'} (success rate: {success_rate:.2%})")

            # Dynamic verification
            dynamic_verification = use_case_data.get("dynamic_verification")
            if dynamic_verification:
                # dynamic_verification is a dict, not a list
                if isinstance(dynamic_verification, dict):
                    all_passed = dynamic_verification.get("all_passed", False)
                    passed_count = dynamic_verification.get("passed_count", 0)
                    total_count = dynamic_verification.get("total_count", 0)
                    summary_lines.append(f"  Dynamic Verification: {'✓ Passed' if all_passed else '✗ Failed'} ({passed_count}/{total_count} seeds)")
                elif isinstance(dynamic_verification, list):
                    # Handle legacy list format if it exists
                    all_passed = all(dr.get("all_passed", False) for dr in dynamic_verification if isinstance(dr, dict))
                    summary_lines.append(f"  Dynamic Verification: {'✓ Passed' if all_passed else '✗ Failed'}")

        summary_lines.append(f"\n{'=' * 60}\n")
        return "\n".join(summary_lines)
