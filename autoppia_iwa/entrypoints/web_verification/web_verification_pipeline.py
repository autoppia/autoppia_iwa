"""
Web Verification Pipeline

Main pipeline that orchestrates:
0. Pre-validation (project setup, events, use cases)
1. Task generation (2 tasks per use case with constraints) + LLM Review (V1)
2. Dataset diversity verification - verify datasets differ with different seeds (V2)
3. IWAP doability check (find any successful solution for use case)
4. Dynamic verification with different seeds (V3)
"""

import json
import re
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

        from .consistence_reviewer import ConsistenceReviewer

        if config.llm_review_enabled:
            if config.reviewer_type == "new":
                self.llm_reviewer = ConsistenceReviewer(
                    llm_service=self.llm_service,
                    temperature=config.llm_temperature,
                )
                logger.info("Using NEW ConsistenceReviewer for validation")
            else:
                self.llm_reviewer = LLMReviewer(
                    llm_service=self.llm_service,
                    timeout_seconds=config.llm_timeout_seconds,
                )
                logger.info("Using OLD LLMReviewer for validation")
        else:
            self.llm_reviewer = None

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
            "dataset_diversity_verification": None,  # V2: Will be set in Step 2
            "doability_check": None,
            "dynamic_verification": None,  # V3: Will be set in Step 4 if solution is available
        }

        # Step 1: Generate tasks (2 per use case) with constraints
        # Generate each task separately with different seeds to ensure variety
        print("\n" + "=" * 80)
        print("📝 STEP 1: TASK GENERATION")
        print("=" * 80)
        print(f"Use Case: {use_case.name}")
        print(f"Generating {self.config.tasks_per_use_case} task(s)...")
        print("=" * 80 + "\n")

        tasks = []

        for task_index in range(self.config.tasks_per_use_case):
            task_num = task_index + 1
            total_tasks = self.config.tasks_per_use_case

            print(f"🔄 Generating task {task_num}/{total_tasks}...")

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
                    logger.debug(f"Created independent use_case copy for task {task_num} with {len(task.use_case.constraints)} constraints")

                tasks.append(task)

                # Print successfully generated task details
                seed_value = self._extract_seed_from_url(task.url)
                constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
                constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

                import sys

                print(f"✅ Task {task_num}/{total_tasks} generated successfully!")
                print(f"   Task ID: {task.id}")
                print(f"   Seed: {seed_value if seed_value else 'N/A'}")
                print(f"   Constraints: {len(constraints) if constraints else 0} constraint(s)")
                if constraints_str:
                    print("   Constraints Details:")
                    for line in constraints_str.split("\n"):
                        if line.strip():
                            print(f"     {line}")
                print(f"   Prompt: {task.prompt[:100]}..." if len(task.prompt) > 100 else f"   Prompt: {task.prompt}")
                print()
                sys.stdout.flush()
            else:
                print(f"❌ Failed to generate task {task_num}/{total_tasks}")
                print()

        if not tasks:
            print("=" * 80)
            print("❌ ERROR: No tasks generated for use case")
            print("=" * 80 + "\n")
            logger.warning(f"No tasks generated for use case: {use_case.name}")
            use_case_results["error"] = "No tasks generated"
            return use_case_results

        import sys

        print("=" * 80)
        print(f"✅ All {len(tasks)} task(s) generated successfully!")
        print("=" * 80)
        sys.stdout.flush()
        print()

        # Step 1: LLM review (no retry logic)
        print("\n" + "=" * 80)
        print("🤖 STEP 1: LLM REVIEW")
        print("=" * 80)
        print(f"Use Case: {use_case.name}")
        print(f"Reviewing {len(tasks)} task(s)...")
        print("=" * 80 + "\n")

        # Review each task once
        task_review_map = {}
        for task_index, task in enumerate(tasks):
            task_num = task_index + 1

            # Extract seed value from task URL
            seed_value = self._extract_seed_from_url(task.url)

            # Get constraints
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Review task with LLM
            if self.llm_reviewer:
                print("=" * 80)
                print(f"📋 Reviewing Task {task_num}/{len(tasks)}")
                print("=" * 80)
                print(f"Giving task {task_num} to LLM for review...")
                print()

                logger.debug(f"Reviewing task {task.id} with LLM: checking if prompt matches constraints")
                review_result = await self.llm_reviewer.review_task_and_constraints(task)
                review_result["task_id"] = task.id
                review_result["retry_count"] = 0

                # Print task details and review result immediately after review
                import sys

                sys.stdout.flush()

                print("-" * 80)
                print("📝 TASK DETAILS:")
                print("-" * 80)
                print(f"Task ID: {task.id}")
                print(f"Use Case: {use_case.name}")
                print(f"Seed: {seed_value if seed_value else 'N/A'}")
                print(f"Constraints: {len(constraints) if constraints else 0} constraint(s)")
                if constraints_str:
                    print("\nConstraints Details:")
                    for line in constraints_str.split("\n"):
                        if line.strip():
                            print(f"  {line}")
                print("\nPrompt:")
                print(f"  {task.prompt}")
                print("-" * 80)
                print("🤖 LLM REVIEW RESULT:")
                print("-" * 80)
                print(f"Valid: {'✅ YES' if review_result.get('valid', False) else '❌ NO'}")
                if review_result.get("issues"):
                    print("\nIssues found:")
                    for issue in review_result.get("issues", []):
                        print(f"  - {issue}")
                if review_result.get("reasoning"):
                    print("\nReasoning:")
                    print(f"  {review_result.get('reasoning')}")
                print("=" * 80)
                sys.stdout.flush()
                print()

                # Print result status
                if review_result.get("valid", False):
                    print(f"✅ Task {task_num} passed LLM review!\n")
                else:
                    print(f"❌ Task {task_num} failed LLM review\n")
                sys.stdout.flush()

                logger.debug(f"Task {task.id} LLM review result: valid={review_result.get('valid', False)}")
            else:
                # LLM reviewer disabled - mark as passed
                review_result = {
                    "valid": True,
                    "task_id": task.id,
                    "retry_count": 0,
                    "skipped": True,
                    "reasoning": "LLM review is disabled",
                }

            # Store task and review result
            task_review_map[task_index] = {
                "task": task,
                "review_result": review_result,
            }

        # Print summary of review results
        import sys

        sys.stdout.flush()
        print("=" * 80)
        print("📊 REVIEW SUMMARY")
        print("=" * 80)
        passed_count = sum(1 for info in task_review_map.values() if info.get("review_result", {}).get("valid", False))
        total_count = len(task_review_map)
        print(f"Tasks Passed: {passed_count}/{total_count}")
        for task_idx, task_info in sorted(task_review_map.items()):
            task_num = task_idx + 1
            review_result = task_info.get("review_result", {})
            is_valid = review_result.get("valid", False)
            status = "✅ PASSED" if is_valid else "❌ FAILED"
            print(f"  Task {task_num}: {status}")
        print("=" * 80 + "\n")
        sys.stdout.flush()

        # Store final results
        for _task_index, task_info in sorted(task_review_map.items()):
            task = task_info["task"]
            review_result = task_info["review_result"]

            # Extract seed value from task URL
            seed_value = self._extract_seed_from_url(task.url)

            # Get constraints
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

            # Serialize constraints to make them JSON-compatible
            serialized_constraints = self._serialize_constraints(constraints) if constraints else None

            task_info_dict = {
                "task_id": task.id,
                "prompt": task.prompt,
                "constraints": serialized_constraints,
                "constraints_str": constraints_str,
                "seed": seed_value,
            }
            use_case_results["tasks"].append(task_info_dict)

            if review_result:
                use_case_results["llm_reviews"].append(review_result)

        # Step 2 (V2): Dataset Diversity Verification - verify that datasets are different with different seeds
        if self.config.dynamic_enabled and self.dynamic_verifier:
            print("\n" + "=" * 80)
            print("🔄 STEP 2 (V2): DATASET DIVERSITY VERIFICATION")
            print("=" * 80)
            print(f"Use Case: {use_case.name}")
            print(f"Project ID: {self.web_project.id}")
            print(f"Seeds to test: {self.config.seed_values}")
            print("Verifying that datasets are different with different seeds...")
            print("Note: This ensures dynamic data generation is working correctly")
            print("-" * 80)

            logger.info(f"Step 2 (V2): Dataset Diversity Verification for {use_case.name}")
            v2_result = await self.dynamic_verifier.verify_dataset_diversity_with_seeds(
                seed_values=self.config.seed_values,
            )

            use_case_results["dataset_diversity_verification"] = v2_result

            # Print V2 results
            print(f"\nV2 Verification Result: {'✓ PASSED' if v2_result.get('passed', False) else '✗ FAILED'}")
            print(f"Seeds tested: {v2_result.get('seeds_tested', [])}")
            print(f"Datasets loaded: {v2_result.get('loaded_count', 0)}/{v2_result.get('expected_count', 0)}")
            print(f"All different: {'✓ YES' if v2_result.get('all_different', False) else '✗ NO'}")

            # Print comparison details
            comparison_results = v2_result.get("comparison_results", [])
            if comparison_results:
                print("\nPairwise comparisons:")
                for comparison in comparison_results:
                    seed1 = comparison.get("seed1")
                    seed2 = comparison.get("seed2")
                    different = comparison.get("different")
                    if different is None:
                        print(f"  Seed {seed1} vs {seed2}: ⚠️  {comparison.get('reason', 'Unknown')}")
                    elif different:
                        print(f"  Seed {seed1} vs {seed2}: ✓ Different (hash1={comparison.get('hash1')}, hash2={comparison.get('hash2')})")
                    else:
                        print(f"  Seed {seed1} vs {seed2}: ✗ IDENTICAL (hash={comparison.get('hash1')})")

            # Print summary
            print(f"\n{v2_result.get('summary', 'No summary available')}")
            print("=" * 80 + "\n")
        else:
            logger.info("V2 Dataset Diversity Verification: Skipped (dynamic mode disabled or verifier unavailable)")
            use_case_results["dataset_diversity_verification"] = {
                "skipped": True,
                "reason": "Dynamic mode disabled or verifier unavailable",
                "passed": None,
            }

        # Step 3: IWAP API call - proceed if enabled and (LLM reviews are valid or review is disabled)
        if self.iwap_client:
            all_reviews_valid = True
            if self.llm_reviewer:
                llm_reviews = use_case_results.get("llm_reviews", [])
                all_reviews_valid = all(review.get("valid", False) for review in llm_reviews) and len(llm_reviews) > 0

            if all_reviews_valid:
                print("\n" + "=" * 80)
                print("🔄 STEP 3: IWAP USE CASE DOABILITY CHECK")
                print("=" * 80)
                print(f"Use Case: {use_case.name}")
                print(f"Project ID: {self.web_project.id}")
                if self.llm_reviewer:
                    print(f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}")
                    print("All LLM Reviews: VALID ✓")
                else:
                    print("LLM Review: DISABLED (proceeding without gating)")
                print("Checking if use case is doable (has successful solution)...")
                print("Note: We don't compare specific constraints, just check if use case has been solved before")
                print("-" * 80)

                logger.info(f"Step 3: IWAP Use Case Doability Check for {use_case.name} (LLM review {'enabled' if self.llm_reviewer else 'disabled'})")
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

                        # Process API response and check use case doability
                        print("\n" + "-" * 80)
                        print("🔍 CHECKING USE CASE DOABILITY")
                        print("-" * 80)
                        print("Looking for ANY successful solution for this use case...")
                        print("(We don't compare specific constraints, just check if use case is doable)")

                        # Get our generated tasks (passed for reference, not for matching)
                        our_tasks = tasks  # tasks list from Step 1

                        # Process and check doability
                        doability_result = self.iwap_client.process_api_response_for_tasks(iwap_result, our_tasks)

                        # Store doability result
                        use_case_results["iwap_match_result"] = doability_result  # Keep key for backward compatibility
                        use_case_results["iwap_doability_result"] = doability_result  # New clearer key

                        # Print doability results
                        if doability_result.get("matched", False):
                            doability_result.get("match_type", "unknown")
                            reason = doability_result.get("reason", "")
                            actions = doability_result.get("actions", [])
                            api_task_id = doability_result.get("api_task_id", "N/A")
                            api_prompt = doability_result.get("api_prompt", "N/A")
                            total_solutions = doability_result.get("total_solutions_found", 0)

                            print("✓ USE CASE IS DOABLE!")
                            print(f"  Reason: {reason}")
                            print(f"  Total Solutions Found: {total_solutions}")
                            print(f"  Using Solution From Task ID: {api_task_id}")
                            print(f"  Solution Prompt: {api_prompt[:80]}..." if len(api_prompt) > 80 else f"  Solution Prompt: {api_prompt}")
                            print(f"  Actions Found: {len(actions) if actions else 0} actions")
                            if actions:
                                print(f"  First Action: {actions[0] if len(actions) > 0 else 'N/A'}")
                        else:
                            reason = doability_result.get("reason", "Unknown reason")
                            print("✗ USE CASE NOT DOABLE")
                            print(f"  ⚠️  WARNING: {reason}")
                    else:
                        error = iwap_result.get("error", "Unknown error")
                        print(f"Error: {error}")
                else:
                    print("IWAP API Call: ✗ FAILED (No response)")

                print("=" * 80 + "\n")

                logger.info(f"IWAP Use Case Doability Check for {use_case.name}: success={iwap_result.get('success', False) if iwap_result else False}")

                # Store Step 2 execution status (IWAP Use Case Doability Check)
                if iwap_result and iwap_result.get("success", False):
                    # Step 2 executed successfully
                    doability_result = use_case_results.get("iwap_match_result", {})  # Backward compatibility key
                    if doability_result.get("matched", False):
                        # Use case is doable - solution found
                        use_case_results["iwap_status"] = {
                            "executed": True,
                            "matched": True,
                            "doable": True,
                            "reason": "Use case is doable - successful solution found from IWAP API",
                        }
                    else:
                        # Use case is not doable - no solution found
                        use_case_results["iwap_status"] = {
                            "executed": True,
                            "matched": False,
                            "doable": False,
                            "reason": doability_result.get("reason", "No successful solution found for this use case"),
                        }
                else:
                    # Step 2 failed
                    use_case_results["iwap_status"] = {
                        "executed": True,
                        "success": False,
                        "reason": iwap_result.get("error", "API call failed") if iwap_result else "No response",
                    }

                # Step 4: Dynamic verification - evaluate solution from Step 3 with different seeds
                # (only if use case is doable and we have a solution)
                doability_result = use_case_results.get("iwap_match_result", {})  # Backward compatibility key

                if doability_result.get("matched", False) and doability_result.get("actions"):
                    # Use case is doable - we have a solution to test with different seeds
                    solution_actions = doability_result.get("actions", [])
                    api_prompt = doability_result.get("api_prompt", "")
                    api_tests = doability_result.get("api_tests", [])
                    api_start_url = doability_result.get("api_start_url", "")

                    print("\n" + "=" * 80)
                    print("🔄 STEP 4: DYNAMIC VERIFICATION")
                    print("=" * 80)
                    print(f"Use Case: {use_case.name}")
                    print(f"Using Solution Prompt: {api_prompt[:100]}..." if len(api_prompt) > 100 else f"Using Solution Prompt: {api_prompt}")
                    print(f"Evaluating solution with {len(solution_actions)} actions against different seeds")
                    print(f"Seeds to test: {self.config.seed_values}")
                    print("Note: Testing if solution works across different dynamic content variations")
                    print("=" * 80 + "\n")

                    # manual testing
                    # if solution_actions:

                    # api_prompt = "Create a matter with the name that is NOT 'Tax Investigation', with client that is NOT equal to 'LegalEase Inc.', and status that is NOT equal to 'Active'."
                    # api_start_url = "http://localhost:8004/matters?seed=1"
                    # api_tests = "1) name not_contains Tax Investigation AND 2) client not_equals LegalEase Inc. AND 3) status not_equals Active"
                    if self.dynamic_verifier and self.config.dynamic_verification_enabled:
                        if api_prompt and api_start_url:
                            logger.info(
                                f"Step 4: Evaluating API solution against API task with different seeds for use case {use_case.name}"  # {use_case.name}
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
                            print("📊 STEP 4 SUMMARY")
                            print("=" * 80)
                            print(dynamic_result.get("summary", "No summary available"))
                            print(f"Passed: {dynamic_result.get('passed_count', 0)}/{dynamic_result.get('total_count', 0)}")

                            # Show warning if solution works for all seeds (suggests non-dynamic use case)
                            if dynamic_result.get("needs_review", False):
                                print("\n" + "=" * 80)
                                print("⚠️  REVIEW RECOMMENDED")
                                print("=" * 80)
                                print(f"Use Case: {use_case.name}")
                                print("⚠️  This use case may not be truly dynamic.")
                                print(f"   The same solution works for all {dynamic_result.get('total_count', 0)} seeds tested.")
                                print("   If the web is dynamic, different seeds should produce different DOM structures,")
                                print("   making it unlikely that the same solution works across all seeds.")
                                print("=" * 80 + "\n")

                            print("=" * 80 + "\n")
                        else:
                            logger.warning("No reference task available for dynamic verification")
                        # Store skip reason for Step 4
                        use_case_results["dynamic_verification"] = {
                            "skipped": True,
                            "reason": "No reference task available (missing api_prompt or api_start_url)",
                            "all_passed": False,
                            "passed_count": 0,
                            "total_count": 0,
                        }
                    else:
                        logger.info("Dynamic verification is disabled")
                        # Store skip reason for Step 4
                        use_case_results["dynamic_verification"] = {
                            "skipped": True,
                            "reason": "Dynamic verification is disabled",
                            "all_passed": False,
                            "passed_count": 0,
                            "total_count": 0,
                        }
                else:
                    print("\n" + "=" * 80)
                    print("⏭️  STEP 4: SKIPPED")
                    print("=" * 80)
                    print(f"Use Case: {use_case.name}")
                    skip_reason = ""
                    if not doability_result.get("matched", False):
                        skip_reason = "Use case is not doable - no successful solution found from IWAP API"
                        print(f"Reason: {skip_reason}")
                    else:
                        skip_reason = "No actions in solution"
                        print(f"Reason: {skip_reason}")
                    print("=" * 80 + "\n")
                    # Store skip reason for Step 4
                    use_case_results["dynamic_verification"] = {
                        "skipped": True,
                        "reason": skip_reason,
                        "all_passed": False,
                        "passed_count": 0,
                        "total_count": 0,
                    }
            else:
                invalid_count = sum(1 for review in use_case_results.get("llm_reviews", []) if not review.get("valid", False))
                print("\n" + "=" * 80)
                print("⏭️  STEP 3: SKIPPED")
                print("=" * 80)
                print(f"Use Case: {use_case.name}")
                print(f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}")
                print(f"Invalid Reviews: {invalid_count}")
                print("Reason: Not all LLM reviews are valid")
                print("=" * 80 + "\n")
                logger.info(f"Step 3: Skipping IWAP Use Case Doability Check for {use_case.name} because not all LLM reviews are valid")
                # Store skip reason for Step 3
                use_case_results["iwap_status"] = {
                    "skipped": True,
                    "reason": "Not all LLM reviews are valid",
                    "invalid_reviews": invalid_count,
                    "total_reviews": len(use_case_results.get("llm_reviews", [])),
                }
                # Also mark Step 4 as skipped since Step 3 was skipped
                use_case_results["dynamic_verification"] = {
                    "skipped": True,
                    "reason": "Step 3 skipped (not all LLM reviews are valid)",
                    "all_passed": False,
                    "passed_count": 0,
                    "total_count": 0,
                }
        else:
            print("\n" + "=" * 80)
            print("⏭️  STEP 2: SKIPPED")
            print("=" * 80)
            print(f"Use Case: {use_case.name}")
            print("Reason: IWAP client is disabled (--no-iwap flag used)")
            print("=" * 80 + "\n")
            logger.info(f"Step 3: Skipping IWAP Use Case Doability Check for {use_case.name} because IWAP client is disabled")
            # Store skip reason for Step 3
            use_case_results["iwap_status"] = {
                "skipped": True,
                "reason": "IWAP client is disabled",
            }
            # Also mark Step 4 as skipped since Step 3 was skipped
            use_case_results["dynamic_verification"] = {
                "skipped": True,
                "reason": "Step 3 skipped (IWAP client disabled)",
                "all_passed": False,
                "passed_count": 0,
                "total_count": 0,
            }

        # Note: IWAP doability check is now done per-task in Step 3 (when LLM review is valid)
        # Keeping this for backward compatibility if needed, but it's now integrated into Step 3
        return use_case_results

    def _format_results_for_storage(self) -> dict[str, Any]:
        """
        Format results in a minimal, readable structure

        Returns:
            Simplified results dictionary with:
            - Generated tasks with matched data
            - Dynamic verification results by seed (not actions)
            - Summary section
        """
        formatted_results = {
            "project_id": self.web_project.id,
            "project_name": self.web_project.name,
            "use_cases": {},
            "summary": {},
        }

        # Process each use case
        for use_case_name, use_case_data in self.results["use_cases"].items():
            formatted_use_case = {
                "use_case_name": use_case_name,
                "tasks": [],
            }

            # Get generated tasks
            tasks = use_case_data.get("tasks", [])
            llm_reviews = use_case_data.get("llm_reviews", [])
            match_result = use_case_data.get("iwap_match_result", {})
            dynamic_verification = use_case_data.get("dynamic_verification", {})

            # Format each task
            for idx, task_info in enumerate(tasks):
                task_id = task_info.get("task_id", "")

                # Get LLM review for this task
                llm_review = None
                if idx < len(llm_reviews):
                    llm_review = llm_reviews[idx]

                formatted_task = {
                    "task_id": task_id,
                    "prompt": task_info.get("prompt", ""),
                    "seed": task_info.get("seed"),
                    "constraints": task_info.get("constraints_str", ""),
                    "llm_review": {
                        "valid": llm_review.get("valid", False) if llm_review else None,
                        "score": llm_review.get("score") if llm_review else None,
                    }
                    if llm_review
                    else None,
                }

                formatted_use_case["tasks"].append(formatted_task)

            # Add matched data at use case level (only if matched)
            if match_result.get("matched", False):
                matched_data = {
                    "match_type": match_result.get("match_type", ""),
                    "api_task_id": match_result.get("api_task_id", ""),
                    "api_prompt": match_result.get("api_prompt", ""),
                    "api_start_url": match_result.get("api_start_url", ""),
                }

                # Add dynamic verification results by seed (not actions)
                if dynamic_verification and not dynamic_verification.get("skipped", False):
                    seed_results = {}
                    results_by_seed = dynamic_verification.get("results", {})
                    for seed, seed_result in results_by_seed.items():
                        evaluation = seed_result.get("evaluation", {})
                        if evaluation:  # Only include if evaluation exists
                            seed_results[str(seed)] = {
                                "evaluation": evaluation,  # Include full evaluation for detailed display
                                "score": evaluation.get("final_score", 0.0),
                                "tests_passed": evaluation.get("tests_passed", 0),
                                "total_tests": evaluation.get("total_tests", 0),
                                "success": evaluation.get("success", False),
                            }
                        else:
                            # If no evaluation, include basic success status
                            seed_results[str(seed)] = {
                                "score": 0.0,
                                "success": seed_result.get("success", False),
                                "error": seed_result.get("error"),
                            }

                    matched_data["dynamic_verification"] = {
                        "seeds_tested": dynamic_verification.get("seeds_tested", []),
                        "results_by_seed": seed_results,
                        "all_passed": dynamic_verification.get("all_passed", False),
                        "passed_count": dynamic_verification.get("passed_count", 0),
                        "total_count": dynamic_verification.get("total_count", 0),
                    }
                elif dynamic_verification and dynamic_verification.get("skipped", False):
                    matched_data["dynamic_verification"] = {
                        "skipped": True,
                        "reason": dynamic_verification.get("reason", ""),
                    }

                formatted_use_case["matched"] = matched_data

            formatted_results["use_cases"][use_case_name] = formatted_use_case

        # Calculate and add summary
        formatted_results["summary"] = self._calculate_summary()

        return formatted_results

    def _calculate_summary(self) -> dict[str, Any]:
        """
        Calculate summary statistics for all use cases

        Returns:
            Dictionary with summary information:
            - task_generation: Pass | Fail
            - number_of_tasks_generated: int
            - llm_review: Pass | Fail
            - dynamic_verification: Pass | Fail
        """
        total_tasks = 0
        all_tasks_generated = True
        all_llm_reviews_passed = True
        all_dynamic_verification_passed = True
        has_dynamic_verification = False

        for _use_case_name, use_case_data in self.results["use_cases"].items():
            tasks = use_case_data.get("tasks", [])
            total_tasks += len(tasks)

            # Check if tasks were generated
            if not tasks or use_case_data.get("error"):
                all_tasks_generated = False

            # Check LLM reviews
            llm_reviews = use_case_data.get("llm_reviews", [])
            if llm_reviews:
                # LLM review is enabled - check if all are valid
                for review in llm_reviews:
                    if not review.get("valid", False):
                        all_llm_reviews_passed = False
                        break
            elif self.llm_reviewer:
                # LLM reviewer is enabled but no reviews (shouldn't happen, but handle it)
                all_llm_reviews_passed = False
            # If LLM reviewer is disabled, consider it as passed (not applicable)

            # Check dynamic verification
            dynamic_verification = use_case_data.get("dynamic_verification", {})
            if dynamic_verification and not dynamic_verification.get("skipped", False):
                # Dynamic verification was executed
                has_dynamic_verification = True
                # Check if all seeds passed (if all seed results have score=1.0, then Pass)
                if not dynamic_verification.get("all_passed", False):
                    all_dynamic_verification_passed = False
            # If skipped, we don't count it as failed (it's just not applicable)

        # Determine summary status
        # Dynamic verification: Pass if all seeds passed (all_passed=True), else Fail
        # If no dynamic verification was executed, we can't determine pass/fail

        summary = {
            "task_generation": "Pass" if all_tasks_generated and total_tasks > 0 else "Fail",
            "number_of_tasks_generated": total_tasks,
            "llm_review": "Pass" if (all_llm_reviews_passed or not self.llm_reviewer) else "Fail",
            "dynamic_verification": "Pass" if (all_dynamic_verification_passed and has_dynamic_verification) else ("Fail" if has_dynamic_verification else "N/A"),
        }

        return summary

    async def _save_results(self):
        """Save verification results to file in minimal, readable format"""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"verification_{self.web_project.id}.json"

        # Format results in minimal structure
        formatted_results = self._format_results_for_storage()

        # Convert to JSON-serializable format
        results_dict = self._serialize_results(formatted_results)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {output_file}")

        # Also save a focused report with misgenerated/suspicious tasks to make manual review easy
        misgenerated_report = self._build_misgenerated_tasks_report()
        misgenerated_file = output_dir / f"misgenerated_tasks_{self.web_project.id}.json"
        with open(misgenerated_file, "w", encoding="utf-8") as f:
            json.dump(self._serialize_results(misgenerated_report), f, indent=2, ensure_ascii=False)
        logger.info(f"Misgenerated tasks report saved to: {misgenerated_file}")

    def _build_misgenerated_tasks_report(self) -> dict[str, Any]:
        """
        Build a compact report containing only tasks that look misgenerated.

        Definition of "misgenerated" in this report:
        - LLM review returned valid=false, OR
        - A lightweight heuristic flags the prompt as suspicious (missing literal constraint values).

        This helps catch both reviewer negatives and potential reviewer false-positives.
        """
        report: dict[str, Any] = {
            "project_id": self.web_project.id,
            "project_name": self.web_project.name,
            "tasks_per_use_case": self.config.tasks_per_use_case,
            "use_cases": {},
            "summary": {
                "use_cases_with_issues": 0,
                "failed_llm_review_tasks": 0,
                "suspicious_tasks": 0,
                "total_tasks": 0,
            },
        }

        for use_case_name, use_case_data in self.results.get("use_cases", {}).items():
            tasks: list[dict[str, Any]] = use_case_data.get("tasks", []) or []
            reviews: list[dict[str, Any]] = use_case_data.get("llm_reviews", []) or []

            # Include use cases where task generation failed (no tasks) for manual inspection.
            if not tasks:
                report["use_cases"][use_case_name] = {
                    "use_case_description": use_case_data.get("use_case_description", ""),
                    "tasks": [],
                    "generation_error": use_case_data.get("error") or "No tasks generated",
                }
                report["summary"]["use_cases_with_issues"] += 1
                continue

            # Map reviews by task_id for stability
            reviews_by_task_id: dict[str, dict[str, Any]] = {str(r.get("task_id")): r for r in reviews if isinstance(r, dict) and r.get("task_id") is not None}

            flagged_tasks: list[dict[str, Any]] = []
            for task in tasks:
                task_id = str(task.get("task_id", ""))
                prompt = task.get("prompt", "") or ""
                constraints = task.get("constraints", None)
                constraints_str = task.get("constraints_str", "") or ""
                seed = task.get("seed", None)

                review = reviews_by_task_id.get(task_id)
                llm_valid = review.get("valid", None) if review else None
                overridden = bool(review.get("overridden_by_heuristic", False)) if review else False

                suspicious_reasons = self._flag_suspicious_prompt_against_constraints(prompt, constraints)

                should_flag = (llm_valid is False) or bool(suspicious_reasons) or overridden
                if not should_flag:
                    continue

                # Clean review result for report
                clean_review = {}
                if review:
                    clean_review = {k: v for k, v in review.items() if k not in ["reasoning", "task_id"]}

                flagged_tasks.append(
                    {
                        "task_id": task_id,
                        "seed": seed,
                        "prompt": prompt,
                        "constraints_str": constraints_str,
                        "constraints": constraints,
                        "llm_review": clean_review,
                    }
                )

                if llm_valid is False:
                    report["summary"]["failed_llm_review_tasks"] += 1
                if suspicious_reasons:
                    report["summary"]["suspicious_tasks"] += 1

            if flagged_tasks:
                report["use_cases"][use_case_name] = {
                    "use_case_description": use_case_data.get("use_case_description", ""),
                    "tasks": flagged_tasks,
                }
                report["summary"]["use_cases_with_issues"] += 1
                report["summary"]["total_tasks"] += len(flagged_tasks)

        return report

    def _flag_suspicious_prompt_against_constraints(self, prompt: str, constraints: Any) -> list[str]:
        """
        Lightweight, deterministic heuristic to flag likely bad generations.

        It does NOT try to validate semantic operator correctness (that's what the LLM reviewer does).
        It only checks whether literal constraint values are present in the prompt text.

        Returns:
            List of human-readable reasons. Empty list means "not suspicious".
        """
        if not constraints or not isinstance(prompt, str) or not prompt.strip():
            return []

        if not isinstance(constraints, list):
            return []

        prompt_norm = self._normalize_text_for_match(prompt)
        reasons: list[str] = []

        for constraint in constraints:
            if not isinstance(constraint, dict):
                continue

            field = str(constraint.get("field", "") or "")
            operator = str(constraint.get("operator", "") or "")
            value = constraint.get("value", None)

            # Values should almost always appear in the prompt (including for negative operators)
            missing = self._missing_constraint_values(prompt_norm, value, operator=operator)
            if missing:
                reasons.append(f"Missing value(s) for constraint '{field} {operator}': {', '.join(missing)}")

        return reasons

    def _missing_constraint_values(self, prompt_norm: str, value: Any, operator: str) -> list[str]:
        """
        Return a list of stringified atomic values that do not appear in the prompt.

        For list-valued constraints (e.g. in_list), require at least one list item to appear.
        """
        # Normalize operator string (Enum already serialized earlier)
        op = (operator or "").strip().lower()

        if value is None:
            return []

        # For list values, treat as "at least one must appear"
        if isinstance(value, list):
            atoms = [self._stringify_atom(v) for v in value if v is not None]
            atoms = [a for a in atoms if a]
            if not atoms:
                return []

            present_any = any(self._normalize_text_for_match(a) in prompt_norm for a in atoms)
            if present_any:
                return []
            # If none of them appear, flag the whole list (shortened to first few)
            return atoms[:5]

        atom = self._stringify_atom(value)
        if not atom:
            return []

        atom_norm = self._normalize_text_for_match(atom)
        if atom_norm and atom_norm not in prompt_norm:
            # For numeric operators, the number should still appear literally
            return [atom]

        # Special case: sometimes equals with float "4.5" may appear as "4,5" in some locales; try a loose match
        if op in {"equals", "greater_than", "less_than", "greater_equal", "less_equal"} and re.fullmatch(r"-?\\d+\\.\\d+", atom.strip()):
            alt = atom.replace(".", ",")
            if self._normalize_text_for_match(alt) in prompt_norm:
                return []

        return []

    @staticmethod
    def _stringify_atom(v: Any) -> str:
        if isinstance(v, int | float | bool):
            return str(v)
        if isinstance(v, str):
            return v
        return str(v)

    @staticmethod
    def _normalize_text_for_match(text: str) -> str:
        # Lowercase, strip quotes/punct, collapse whitespace
        lowered = text.lower()
        lowered = re.sub(r"[\"'`]", "", lowered)
        lowered = re.sub(r"[^a-z0-9<>@._\-\s]", " ", lowered)
        lowered = re.sub(r"\s+", " ", lowered).strip()
        return lowered

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

    def _print_task_details_for_review(self, task: Task, seed: int | None, constraints_str: str):
        """
        Print task details (prompt, constraints, seed) before GPT review

        Args:
            task: The task to print
            seed: Seed value from URL
            constraints_str: String representation of constraints
        """
        print("\n" + "=" * 80)
        print("📋 TASK DETAILS FOR GPT REVIEW")
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

            # Step 0: Pre-validation (project-level, but shown for context)
            # Note: Pre-validation is done once at the start, but we show it here for completeness
            summary_lines.append("  Step 0 (Pre-validation): ✓ Passed")

            # Step 1: Task Generation and LLM Review
            tasks = use_case_data.get("tasks", [])
            summary_lines.append(f"  Step 1 (Task Generation): {len(tasks)} tasks generated")

            # LLM reviews
            reviews = use_case_data.get("llm_reviews", [])
            if reviews:
                valid_reviews = sum(1 for r in reviews if r.get("valid", False))
                if valid_reviews == len(reviews):
                    summary_lines.append(f"  Step 1 (LLM Review): ✓ Passed ({valid_reviews}/{len(reviews)} valid)")
                else:
                    summary_lines.append(f"  Step 1 (LLM Review): ✗ Failed ({valid_reviews}/{len(reviews)} valid)")
            else:
                summary_lines.append("  Step 1 (LLM Review): ⏭️ Skipped")

            # Step 2: V2 Dataset Diversity Verification
            dataset_diversity = use_case_data.get("dataset_diversity_verification")
            if dataset_diversity:
                if dataset_diversity.get("skipped", False):
                    reason = dataset_diversity.get("reason", "Unknown reason")
                    summary_lines.append(f"  Step 2 (V2 Dataset): ⏭️ Skipped ({reason})")
                else:
                    passed = dataset_diversity.get("passed", False)
                    all_different = dataset_diversity.get("all_different", False)
                    loaded_count = dataset_diversity.get("loaded_count", 0)
                    expected_count = dataset_diversity.get("expected_count", 0)

                    if passed and all_different:
                        summary_lines.append(f"  Step 2 (V2 Dataset): ✓ Passed - All datasets different ({loaded_count}/{expected_count} seeds)")
                    elif not passed and loaded_count < expected_count:
                        summary_lines.append(f"  Step 2 (V2 Dataset): ✗ Failed - Only {loaded_count}/{expected_count} datasets loaded")
                    elif not all_different:
                        summary_lines.append("  Step 2 (V2 Dataset): ✗ Failed - Some datasets are identical")
                    else:
                        summary_lines.append(f"  Step 2 (V2 Dataset): ⚠️  {dataset_diversity.get('summary', 'Unknown status')}")
            else:
                summary_lines.append("  Step 2 (V2 Dataset): ⏭️ Skipped (no data)")

            # Step 3: IWAP API / Doability check
            iwap_status = use_case_data.get("iwap_status")
            if iwap_status:
                if iwap_status.get("skipped", False):
                    # Step 3 was skipped
                    reason = iwap_status.get("reason", "Unknown reason")
                    summary_lines.append(f"  Step 3 (IWAP): ⏭️ Skipped ({reason})")
                elif iwap_status.get("executed", False):
                    # Step 3 was executed
                    if iwap_status.get("matched", False):
                        summary_lines.append("  Step 3 (IWAP): ✓ Executed (solution found)")
                    elif iwap_status.get("matched") is False:
                        reason = iwap_status.get("reason", "No solution found")
                        summary_lines.append(f"  Step 3 (IWAP): ✓ Executed ({reason})")
                    elif not iwap_status.get("success", True):
                        reason = iwap_status.get("reason", "API call failed")
                        summary_lines.append(f"  Step 3 (IWAP): ✗ Failed ({reason})")
                    else:
                        summary_lines.append("  Step 3 (IWAP): ✓ Executed")
                else:
                    summary_lines.append("  Step 3 (IWAP): ⏭️ Not executed")
            else:
                # Check for legacy doability_check format
                doability = use_case_data.get("doability_check")
                if doability:
                    is_doable = doability.get("doable", False)
                    success_rate = doability.get("success_rate", 0.0)
                    summary_lines.append(f"  Step 3 (IWAP): {'✓ Doable' if is_doable else '✗ Not doable'} (success rate: {success_rate:.2%})")
                else:
                    summary_lines.append("  Step 3 (IWAP): ⏭️ Not executed")

            # Step 4: Dynamic verification
            dynamic_verification = use_case_data.get("dynamic_verification")
            if dynamic_verification:
                # dynamic_verification is a dict, not a list
                if isinstance(dynamic_verification, dict):
                    skipped = dynamic_verification.get("skipped", False)
                    if skipped:
                        reason = dynamic_verification.get("reason", "Unknown reason")
                        summary_lines.append(f"  Step 4 (Dynamic): ⏭️ Skipped ({reason})")
                    else:
                        all_passed = dynamic_verification.get("all_passed", False)
                        passed_count = dynamic_verification.get("passed_count", 0)
                        total_count = dynamic_verification.get("total_count", 0)
                        seeds_tested = dynamic_verification.get("seeds_tested", [])

                        # Try to get results_by_seed first, fallback to results
                        results_by_seed = dynamic_verification.get("results_by_seed", {})
                        if not results_by_seed:
                            # Fallback: use original results structure
                            original_results = dynamic_verification.get("results", {})
                            results_by_seed = {}
                            for seed_key, seed_result in original_results.items():
                                results_by_seed[str(seed_key)] = seed_result

                        # Build detailed seed results
                        seed_details = []
                        for seed in seeds_tested:
                            seed_result = results_by_seed.get(str(seed), {})
                            # Get score: prefer from evaluation.final_score, fallback to score field
                            score = 0.0
                            if "evaluation" in seed_result and isinstance(seed_result["evaluation"], dict):
                                score = seed_result["evaluation"].get("final_score", 0.0)
                            elif "score" in seed_result:
                                score = seed_result.get("score", 0.0)
                            status = "✓" if score == 1.0 else "✗"
                            seed_details.append(f"{seed}: {status}")

                        if seed_details:
                            seeds_str = ", ".join(seed_details)
                            status_icon = "✓ Passed" if all_passed else "✗ Failed"
                            summary_lines.append(f"  Step 4 (Dynamic): {status_icon} ({passed_count}/{total_count} seeds passed)")
                            summary_lines.append(f"    Solution tested with seeds: {seeds_str}")

                            # Add warning if solution works for all seeds (suggests non-dynamic use case)
                            if dynamic_verification.get("needs_review", False):
                                summary_lines.append(f"    ⚠️  REVIEW RECOMMENDED: Use case may not be truly dynamic (same solution works for all {total_count} seeds)")
                        else:
                            # Fallback if seeds_tested is empty but we have results_by_seed
                            if results_by_seed:
                                seed_details = []
                                for seed_str, seed_result in results_by_seed.items():
                                    score = seed_result.get("score", 0.0)
                                    status = "✓" if score == 1.0 else "✗"
                                    seed_details.append(f"{seed_str}: {status}")
                                if seed_details:
                                    seeds_str = ", ".join(seed_details)
                                    status_icon = "✓ Passed" if all_passed else "✗ Failed"
                                    summary_lines.append(f"  Step 4 (Dynamic): {status_icon} ({passed_count}/{total_count} seeds)")
                                    summary_lines.append(f"    Seeds tested: {seeds_str}")
                                else:
                                    summary_lines.append(f"  Step 4 (Dynamic): {'✓ Passed' if all_passed else '✗ Failed'} ({passed_count}/{total_count} seeds)")
                            else:
                                summary_lines.append(f"  Step 4 (Dynamic): {'✓ Passed' if all_passed else '✗ Failed'} ({passed_count}/{total_count} seeds)")
                elif isinstance(dynamic_verification, list):
                    # Handle legacy list format if it exists
                    all_passed = all(dr.get("all_passed", False) for dr in dynamic_verification if isinstance(dr, dict))
                    summary_lines.append(f"  Step 4 (Dynamic): {'✗ Failed' if all_passed else '✓ Passed'}")
            else:
                # No dynamic verification data at all
                summary_lines.append("  Step 4 (Dynamic): ⏭️ Skipped (no data)")

        # Add final conclusion summary
        summary_lines.append(f"\n{'=' * 60}")
        summary_lines.append("📊 FINAL CONCLUSION")
        summary_lines.append(f"{'=' * 60}")

        # Categorize use cases
        categories = self._categorize_use_cases()

        # Task Generation Quality
        summary_lines.append("\n✅ Task Generation Quality:")
        if categories["generation_ok"]:
            summary_lines.append(f"  ✓ Good generation ({len(categories['generation_ok'])}): {', '.join(categories['generation_ok'])}")
        if categories["generation_failed"]:
            summary_lines.append(f"  ✗ Failed generation ({len(categories['generation_failed'])}): {', '.join(categories['generation_failed'])}")

        # Dataset Diversity (V2)
        summary_lines.append("\n📊 Dataset Diversity (V2):")
        if categories["dataset_diverse"]:
            summary_lines.append(f"  ✓ Datasets are diverse - different data with different seeds ({len(categories['dataset_diverse'])}): {', '.join(categories['dataset_diverse'])}")
        if categories["dataset_not_diverse"]:
            summary_lines.append(f"  ✗ Datasets NOT diverse - same data with different seeds ({len(categories['dataset_not_diverse'])}): {', '.join(categories['dataset_not_diverse'])}")
        if categories["dataset_untested"]:
            summary_lines.append(f"  ⏭️  Dataset diversity not tested ({len(categories['dataset_untested'])}): {', '.join(categories['dataset_untested'])}")

        # Solution Availability (IWAP)
        summary_lines.append("\n🔍 Solution Availability (IWAP):")
        if categories["has_solution"]:
            summary_lines.append(f"  ✓ Has solutions ({len(categories['has_solution'])}): {', '.join(categories['has_solution'])}")
        if categories["no_solution"]:
            summary_lines.append(f"  ✗ No solutions found ({len(categories['no_solution'])}): {', '.join(categories['no_solution'])}")

        # Dynamic System Effectiveness
        summary_lines.append("\n🔄 Dynamic System Effectiveness:")
        if categories["truly_dynamic"]:
            summary_lines.append(f"  ✓ Truly dynamic - solution fails with different seeds ({len(categories['truly_dynamic'])}): {', '.join(categories['truly_dynamic'])}")
        if categories["not_dynamic"]:
            summary_lines.append(f"  ⚠️  Not truly dynamic - same solution works for all seeds ({len(categories['not_dynamic'])}): {', '.join(categories['not_dynamic'])}")
        if categories["dynamic_partial"]:
            summary_lines.append(f"  ⚠️  Partially dynamic - solution works for some seeds ({len(categories['dynamic_partial'])}): {', '.join(categories['dynamic_partial'])}")
        if categories["dynamic_untested"]:
            summary_lines.append(f"  ⏭️  Dynamic not tested ({len(categories['dynamic_untested'])}): {', '.join(categories['dynamic_untested'])}")

        # Overall Status
        summary_lines.append("\n📈 Overall Status:")
        total_use_cases = len(self.results["use_cases"])
        summary_lines.append(f"  Total Use Cases: {total_use_cases}")
        summary_lines.append(f"  - Good generation: {len(categories['generation_ok'])}/{total_use_cases}")
        summary_lines.append(f"  - Dataset diverse (V2): {len(categories['dataset_diverse'])}/{total_use_cases}")
        summary_lines.append(f"  - Has solutions: {len(categories['has_solution'])}/{total_use_cases}")
        summary_lines.append(f"  - Truly dynamic (V3): {len(categories['truly_dynamic'])}/{total_use_cases}")
        summary_lines.append(f"  - Needs review (not dynamic): {len(categories['not_dynamic'])}/{total_use_cases}")

        summary_lines.append(f"\n{'=' * 60}\n")
        return "\n".join(summary_lines)

    def _categorize_use_cases(self) -> dict[str, list[str]]:
        """
        Categorize use cases based on their verification results.

        Returns:
            Dictionary with categorized use case names
        """
        categories = {
            "generation_ok": [],
            "generation_failed": [],
            "dataset_diverse": [],
            "dataset_not_diverse": [],
            "dataset_untested": [],
            "has_solution": [],
            "no_solution": [],
            "truly_dynamic": [],
            "not_dynamic": [],
            "dynamic_partial": [],
            "dynamic_untested": [],
        }

        for use_case_name, use_case_data in self.results["use_cases"].items():
            # Task Generation Quality
            llm_reviews = use_case_data.get("llm_reviews", [])
            if llm_reviews:
                all_valid = all(r.get("valid", False) for r in llm_reviews)
                if all_valid and len(llm_reviews) > 0:
                    categories["generation_ok"].append(use_case_name)
                else:
                    categories["generation_failed"].append(use_case_name)
            else:
                # No LLM reviews means generation might have failed or was skipped
                tasks = use_case_data.get("tasks", [])
                if tasks:
                    categories["generation_ok"].append(use_case_name)
                else:
                    categories["generation_failed"].append(use_case_name)

            # Dataset Diversity (V2)
            dataset_diversity = use_case_data.get("dataset_diversity_verification", {})
            if dataset_diversity and not dataset_diversity.get("skipped", False):
                passed = dataset_diversity.get("passed", False)
                all_different = dataset_diversity.get("all_different", False)

                if passed and all_different:
                    categories["dataset_diverse"].append(use_case_name)
                else:
                    categories["dataset_not_diverse"].append(use_case_name)
            else:
                categories["dataset_untested"].append(use_case_name)

            # Solution Availability (IWAP)
            iwap_status = use_case_data.get("iwap_status", {})
            if iwap_status.get("matched", False) or (iwap_status.get("executed", False) and iwap_status.get("matched") is not False):
                # Check if it actually found a solution (not just executed)
                if iwap_status.get("matched", False):
                    categories["has_solution"].append(use_case_name)
                else:
                    categories["no_solution"].append(use_case_name)
            else:
                categories["no_solution"].append(use_case_name)

            # Dynamic System Effectiveness
            dynamic_verification = use_case_data.get("dynamic_verification", {})
            if dynamic_verification and not dynamic_verification.get("skipped", False):
                passed_count = dynamic_verification.get("passed_count", 0)
                total_count = dynamic_verification.get("total_count", 0)
                needs_review = dynamic_verification.get("needs_review", False)

                if needs_review and passed_count == total_count and total_count >= 3:
                    # Same solution works for all seeds - not truly dynamic
                    categories["not_dynamic"].append(use_case_name)
                elif passed_count == 0 and total_count > 0:
                    # Solution fails for all seeds - truly dynamic (different seeds = different DOM)
                    categories["truly_dynamic"].append(use_case_name)
                elif 0 < passed_count < total_count:
                    # Solution works for some seeds but not all - partially dynamic
                    categories["dynamic_partial"].append(use_case_name)
                else:
                    # Edge case
                    categories["dynamic_untested"].append(use_case_name)
            else:
                # Dynamic verification was skipped
                categories["dynamic_untested"].append(use_case_name)

        return categories
