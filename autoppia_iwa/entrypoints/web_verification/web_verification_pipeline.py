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
                
                # Show detailed feedback when review is invalid
                if not review_result.get("valid", False):
                    print("\n" + "=" * 80)
                    print("⚠️  LLM REVIEW: INVALID")
                    print("=" * 80)
                    print(f"Task ID: {task.id}")
                    print(f"Score: {review_result.get('score', 0.0):.2f}")
                    if review_result.get("issues"):
                        print(f"\nIssues found:")
                        for issue in review_result.get("issues", []):
                            print(f"  - {issue}")
                    if review_result.get("reasoning"):
                        print(f"\nReasoning: {review_result.get('reasoning')}")
                    print("=" * 80 + "\n")

        # Step 2: IWAP API call - proceed if enabled and (LLM reviews are valid or review is disabled)
        if self.iwap_client:
            all_reviews_valid = True
            if self.llm_reviewer:
                llm_reviews = use_case_results.get("llm_reviews", [])
                all_reviews_valid = all(review.get("valid", False) for review in llm_reviews) and len(llm_reviews) > 0

            if all_reviews_valid:
                print("\n" + "=" * 80)
                print("🔄 STEP 2: IWAP USE CASE DOABILITY CHECK")
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

                logger.info(f"Step 2: IWAP Use Case Doability Check for {use_case.name} (LLM review {'enabled' if self.llm_reviewer else 'disabled'})")
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
                            match_type = doability_result.get("match_type", "unknown")
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

                # Step 3: Dynamic verification - evaluate solution from Step 2 with different seeds
                # (only if use case is doable and we have a solution)
                doability_result = use_case_results.get("iwap_match_result", {})  # Backward compatibility key

                if doability_result.get("matched", False) and doability_result.get("actions"):
                    # Use case is doable - we have a solution to test with different seeds
                    solution_actions = doability_result.get("actions", [])
                    api_prompt = doability_result.get("api_prompt", "")
                    api_tests = doability_result.get("api_tests", [])
                    api_start_url = doability_result.get("api_start_url", "")

                    print("\n" + "=" * 80)
                    print("🔄 STEP 3: DYNAMIC VERIFICATION")
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
                            
                            # Show warning if solution works for all seeds (suggests non-dynamic use case)
                            if dynamic_result.get("needs_review", False):
                                print("\n" + "=" * 80)
                                print("⚠️  REVIEW RECOMMENDED")
                                print("=" * 80)
                                print(f"Use Case: {use_case.name}")
                                print(f"⚠️  This use case may not be truly dynamic.")
                                print(f"   The same solution works for all {dynamic_result.get('total_count', 0)} seeds tested.")
                                print(f"   If the web is dynamic, different seeds should produce different DOM structures,")
                                print(f"   making it unlikely that the same solution works across all seeds.")
                                print("=" * 80 + "\n")
                            
                            print("=" * 80 + "\n")
                        else:
                            logger.warning("No reference task available for dynamic verification")
                            # Store skip reason for Step 3
                            use_case_results["dynamic_verification"] = {
                                "skipped": True,
                                "reason": "No reference task available (missing api_prompt or api_start_url)",
                                "all_passed": False,
                                "passed_count": 0,
                                "total_count": 0,
                            }
                    else:
                        logger.info("Dynamic verification is disabled")
                        # Store skip reason for Step 3
                        use_case_results["dynamic_verification"] = {
                            "skipped": True,
                            "reason": "Dynamic verification is disabled",
                            "all_passed": False,
                            "passed_count": 0,
                            "total_count": 0,
                        }
                else:
                    print("\n" + "=" * 80)
                    print("⏭️  STEP 3: SKIPPED")
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
                    # Store skip reason for Step 3
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
                print("⏭️  STEP 2: SKIPPED")
                print("=" * 80)
                print(f"Use Case: {use_case.name}")
                print(f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}")
                print(f"Invalid Reviews: {invalid_count}")
                print("Reason: Not all LLM reviews are valid")
                print("=" * 80 + "\n")
                logger.info(f"Step 2: Skipping IWAP Use Case Doability Check for {use_case.name} because not all LLM reviews are valid")
                # Store skip reason for Step 2
                use_case_results["iwap_status"] = {
                    "skipped": True,
                    "reason": "Not all LLM reviews are valid",
                    "invalid_reviews": invalid_count,
                    "total_reviews": len(use_case_results.get("llm_reviews", [])),
                }
                # Also mark Step 3 as skipped since Step 2 was skipped
                use_case_results["dynamic_verification"] = {
                    "skipped": True,
                    "reason": "Step 2 skipped (not all LLM reviews are valid)",
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
            logger.info(f"Step 2: Skipping IWAP Use Case Doability Check for {use_case.name} because IWAP client is disabled")
            # Store skip reason for Step 2
            use_case_results["iwap_status"] = {
                "skipped": True,
                "reason": "IWAP client is disabled",
            }
            # Also mark Step 3 as skipped since Step 2 was skipped
            use_case_results["dynamic_verification"] = {
                "skipped": True,
                "reason": "Step 2 skipped (IWAP client disabled)",
                "all_passed": False,
                "passed_count": 0,
                "total_count": 0,
            }

        # Note: IWAP doability check is now done per-task in Step 2 (when LLM review is valid)
        # Keeping this for backward compatibility if needed, but it's now integrated into Step 2
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

            # Step 2: IWAP API / Doability check
            iwap_status = use_case_data.get("iwap_status")
            if iwap_status:
                if iwap_status.get("skipped", False):
                    # Step 2 was skipped
                    reason = iwap_status.get("reason", "Unknown reason")
                    summary_lines.append(f"  Step 2 (IWAP): ⏭️ Skipped ({reason})")
                elif iwap_status.get("executed", False):
                    # Step 2 was executed
                    if iwap_status.get("matched", False):
                        summary_lines.append("  Step 2 (IWAP): ✓ Executed (solution found)")
                    elif iwap_status.get("matched") is False:
                        reason = iwap_status.get("reason", "No solution found")
                        summary_lines.append(f"  Step 2 (IWAP): ✓ Executed ({reason})")
                    elif not iwap_status.get("success", True):
                        reason = iwap_status.get("reason", "API call failed")
                        summary_lines.append(f"  Step 2 (IWAP): ✗ Failed ({reason})")
                    else:
                        summary_lines.append("  Step 2 (IWAP): ✓ Executed")
                else:
                    summary_lines.append("  Step 2 (IWAP): ⏭️ Not executed")
            else:
                # Check for legacy doability_check format
                doability = use_case_data.get("doability_check")
                if doability:
                    is_doable = doability.get("doable", False)
                    success_rate = doability.get("success_rate", 0.0)
                    summary_lines.append(f"  Step 2 (IWAP): {'✓ Doable' if is_doable else '✗ Not doable'} (success rate: {success_rate:.2%})")
                else:
                    summary_lines.append("  Step 2 (IWAP): ⏭️ Not executed")

            # Step 3: Dynamic verification
            dynamic_verification = use_case_data.get("dynamic_verification")
            if dynamic_verification:
                # dynamic_verification is a dict, not a list
                if isinstance(dynamic_verification, dict):
                    skipped = dynamic_verification.get("skipped", False)
                    if skipped:
                        reason = dynamic_verification.get("reason", "Unknown reason")
                        summary_lines.append(f"  Step 3 (Dynamic): ⏭️ Skipped ({reason})")
                    else:
                        all_passed = dynamic_verification.get("all_passed", False)
                        passed_count = dynamic_verification.get("passed_count", 0)
                        total_count = dynamic_verification.get("total_count", 0)
                        seeds_tested = dynamic_verification.get("seeds_tested", [])
                        results_by_seed = dynamic_verification.get("results_by_seed", {})
                        
                        # Build detailed seed results
                        seed_details = []
                        for seed in seeds_tested:
                            seed_result = results_by_seed.get(str(seed), {})
                            # Try to get score from evaluation or directly from seed_result
                            score = seed_result.get("score", 0.0)
                            if "evaluation" in seed_result:
                                score = seed_result["evaluation"].get("final_score", score)
                            status = "✓" if score == 1.0 else "✗"
                            seed_details.append(f"{seed}: {status}")
                        
                        if seed_details:
                            seeds_str = ", ".join(seed_details)
                            status_icon = "✓ Passed" if all_passed else "✗ Failed"
                            summary_lines.append(f"  Step 3 (Dynamic): {status_icon} ({passed_count}/{total_count} seeds passed)")
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
                                    summary_lines.append(f"  Step 3 (Dynamic): {status_icon} ({passed_count}/{total_count} seeds)")
                                    summary_lines.append(f"    Seeds tested: {seeds_str}")
                                else:
                                    summary_lines.append(f"  Step 3 (Dynamic): {'✓ Passed' if all_passed else '✗ Failed'} ({passed_count}/{total_count} seeds)")
                            else:
                                summary_lines.append(f"  Step 3 (Dynamic): {'✓ Passed' if all_passed else '✗ Failed'} ({passed_count}/{total_count} seeds)")
                elif isinstance(dynamic_verification, list):
                    # Handle legacy list format if it exists
                    all_passed = all(dr.get("all_passed", False) for dr in dynamic_verification if isinstance(dr, dict))
                    summary_lines.append(f"  Step 3 (Dynamic): {'✗ Failed' if all_passed else '✓ Passed'}")
            else:
                # No dynamic verification data at all
                summary_lines.append("  Step 3 (Dynamic): ⏭️ Skipped (no data)")

        summary_lines.append(f"\n{'=' * 60}\n")
        return "\n".join(summary_lines)
