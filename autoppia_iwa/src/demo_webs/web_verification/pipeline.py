"""
Web Verification Pipeline

Main pipeline that orchestrates:
0. Pre-validation (project setup, events, use cases)
1. Task generation (2 tasks per use case with constraints) + LLM Review (V1)
2. Dataset diversity verification - verify datasets differ with different seeds (V2)
3. Reference-solution doability: registered trajectories (preferred) or IWAP API fallback
4. Dynamic verification with different seeds (V3)
"""

import asyncio
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.trajectory_registry import get_trajectory_map, supported_trajectory_project_ids
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.interfaces import ILLM

from .config import WebVerificationConfig
from .dynamic_verifier import DynamicVerifier
from .iwap_client import IWAPClient
from .llm_reviewer import LLMReviewer
from .trajectory_doability import doability_result_from_trajectory

# Constants
UNKNOWN_REASON = "Unknown reason"


class _TrajectoryOnlyLlmStub(ILLM):
    """Placeholder LLM when ``evaluate_trajectories_only``; task generation must not run."""

    def predict(self, *args, **kwargs) -> str:
        raise RuntimeError(
            "Task generation requires an LLM. This run uses trajectories-only mode "
            "(no OpenAI). Use a full verification run with OPENAI_API_KEY set, or pass "
            "``--trajectories-only`` intentionally without calling task generation.",
        )

    async def async_predict(self, *args, **kwargs) -> str:
        raise RuntimeError(
            "Task generation requires an LLM. This run uses trajectories-only mode "
            "(no OpenAI). Use a full verification run with OPENAI_API_KEY set, or pass "
            "``--trajectories-only`` intentionally without calling task generation.",
        )


def _truncate_for_display(text: str, max_length: int) -> str:
    """Return text truncated to max_length with '...' if longer. Reusable for prompts and messages."""
    if not text or max_length <= 0:
        return text
    return (text[:max_length] + "...") if len(text) > max_length else text


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
        if llm_service is not None:
            self.llm_service = llm_service
        elif config.evaluate_trajectories_only:
            self.llm_service = _TrajectoryOnlyLlmStub()
        else:
            self.llm_service = DIContainer.llm_service()

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
                llm_service_for_tasks=self.llm_service if config.evaluate_trajectories_only else None,
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

        use_cases_to_run = self._use_cases_matching_filter()
        if not use_cases_to_run:
            logger.warning(
                f"No use cases to verify for project {self.web_project.id} (filter={self.config.use_case_filter!r})",
            )
            return self.results

        # Process each use case
        for use_case in use_cases_to_run:
            logger.info(f"Processing use case: {use_case.name}")
            use_case_results = await self._process_use_case(use_case)
            self.results["use_cases"][use_case.name] = use_case_results

        # Save results
        await self._save_results()

        logger.info("Web verification pipeline completed")
        return self.results

    def _use_cases_matching_filter(self) -> list[UseCase]:
        """Return project use cases to run, applying ``config.use_case_filter`` when set."""
        all_uc = list(self.web_project.use_cases or [])
        filt = self.config.use_case_filter
        if not filt:
            return all_uc
        wanted = set(filt)
        out = [uc for uc in all_uc if uc.name in wanted]
        found_names = {uc.name for uc in out}
        missing = wanted - found_names
        if missing:
            logger.warning(
                "Use case filter name(s) not defined on project %s: %s",
                self.web_project.id,
                sorted(missing),
            )
        return out

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
            "trajectory_verification": None,
        }

        tasks: list[Task] = []

        if self.config.evaluate_trajectories_only:
            self._print_step_banner(
                "⏭️ STEP 1 (TASK GEN) & LLM REVIEW: SKIPPED",
                f"Use Case: {use_case.name}",
                "Trajectories-only: no OpenAI; Step 2 (bulk dataset load) skipped; trajectory replay only.",
                "For full verification with task generation and V2 diversity checks, omit --trajectories-only.",
            )
            logger.info(f"evaluate_trajectories_only: skipping Step 1 and LLM for {use_case.name}")
        else:
            # Step 1: Generate tasks (2 per use case) with constraints
            # Generate each task separately with different seeds to ensure variety
            self._print_step_banner(
                "📝 STEP 1: TASK GENERATION",
                f"Use Case: {use_case.name}",
                f"Generating {self.config.tasks_per_use_case} task(s)...",
            )

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
                        # Create a copy of the use_case object so each task has its own independent use_case
                        # with its own constraints. This prevents constraints from being overwritten.
                        task.use_case = copy.deepcopy(use_case)
                        logger.debug(f"Created independent use_case copy for task {task_num} with {len(task.use_case.constraints)} constraints")

                    tasks.append(task)

                    # Print successfully generated task details
                    seed_value, constraints, constraints_str = self._get_task_seed_and_constraints(task)
                    print(f"✅ Task {task_num}/{total_tasks} generated successfully!")
                    self._print_task_info_block(
                        task.id,
                        task.prompt,
                        seed_value,
                        constraints,
                        constraints_str,
                        line_indent="   ",
                        prompt_max_length=100,
                    )
                    print()
                    sys.stdout.flush()
                else:
                    print(f"❌ Failed to generate task {task_num}/{total_tasks}")
                    print()

            if not tasks:
                self._print_step_banner("❌ ERROR: No tasks generated for use case", trailing_newline=True)
                logger.warning(f"No tasks generated for use case: {use_case.name}")
                use_case_results["error"] = "No tasks generated"
                return use_case_results

            self._print_step_banner(f"✅ All {len(tasks)} task(s) generated successfully!", leading_newline=False, trailing_newline=True)
            sys.stdout.flush()

            # Step 1: LLM review (no retry logic)
            self._print_step_banner("🤖 STEP 1: LLM REVIEW", f"Use Case: {use_case.name}", f"Reviewing {len(tasks)} task(s)...")

            # Review each task once
            task_review_map = {}
            for task_index, task in enumerate(tasks):
                task_num = task_index + 1
                seed_value, constraints, constraints_str = self._get_task_seed_and_constraints(task)

                # Review task with LLM
                if self.llm_reviewer:
                    self._print_step_banner(f"📋 Reviewing Task {task_num}/{len(tasks)}", f"Giving task {task_num} to LLM for review...", leading_newline=False, trailing_newline=True)

                    logger.debug(f"Reviewing task {task.id} with LLM: checking if prompt matches constraints")
                    review_result = await self.llm_reviewer.review_task_and_constraints(task)
                    review_result["task_id"] = task.id
                    review_result["retry_count"] = 0

                    sys.stdout.flush()
                    print("-" * 80)
                    print("📝 TASK DETAILS:")
                    print("-" * 80)
                    self._print_task_info_block(
                        task.id,
                        task.prompt,
                        seed_value,
                        constraints,
                        constraints_str,
                        use_case_name=use_case.name,
                        line_indent="  ",
                        constraints_header="\nConstraints Details:",
                        prompt_max_length=None,
                        prompt_on_new_line=True,
                    )
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
            sys.stdout.flush()
            self._print_step_banner("📊 REVIEW SUMMARY", leading_newline=False, trailing_newline=False)
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
                seed_value, constraints, constraints_str = self._get_task_seed_and_constraints(task)

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
        if self.config.evaluate_trajectories_only:
            self._print_step_banner(
                "⏭️ STEP 2 (V2): DATASET DIVERSITY — SKIPPED",
                f"Use Case: {use_case.name}",
                "Trajectories-only: skipping bulk get_all_data() loads (same path as task-generation dataset cache).",
                "Trajectory replay uses only the seed(s) embedded in the scripted flow URLs.",
            )
            logger.info(
                "evaluate_trajectories_only: skipping V2 dataset diversity for %s (no bulk data generation)",
                use_case.name,
            )
            use_case_results["dataset_diversity_verification"] = {
                "skipped": True,
                "reason": "Skipped in trajectories-only mode (avoids loading full datasets per seed)",
                "passed": None,
            }
        elif self.config.dynamic_enabled and self.dynamic_verifier:
            self._print_step_banner(
                "🔄 STEP 2 (V2): DATASET DIVERSITY VERIFICATION",
                f"Use Case: {use_case.name}",
                f"Project ID: {self.web_project.id}",
                f"Seeds to test: {self.config.seed_values}",
                "Verifying that datasets are different with different seeds...",
                "Note: This ensures dynamic data generation is working correctly",
            )
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
                self._print_v2_comparison_results(comparison_results)

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

        # Trajectory verification (repo-local golden flows; independent of IWAP)
        if self.config.evaluate_trajectories:
            if not self.dynamic_verifier or not self.config.dynamic_verification_enabled:
                use_case_results["trajectory_verification"] = {
                    "skipped": True,
                    "reason": "Dynamic verifier unavailable or dynamic verification disabled",
                }
            else:
                traj_map = get_trajectory_map(self.web_project.id)
                if traj_map is None:
                    supported = ", ".join(sorted(supported_trajectory_project_ids()))
                    use_case_results["trajectory_verification"] = {
                        "skipped": True,
                        "reason": f"Project '{self.web_project.id}' has no trajectory definitions (supported: {supported})",
                    }
                elif use_case.name not in traj_map:
                    use_case_results["trajectory_verification"] = {
                        "skipped": True,
                        "reason": f"No trajectory registered for use case '{use_case.name}'",
                    }
                else:
                    self._print_step_banner(
                        "🎯 TRAJECTORY VERIFICATION",
                        f"Use Case: {use_case.name}",
                        "Seed: from trajectory URL (?seed=…)",
                        f"Project ID: {self.web_project.id}",
                    )
                    traj = traj_map[use_case.name]
                    tv = await self.dynamic_verifier.verify_trajectory(traj, use_case)
                    use_case_results["trajectory_verification"] = tv
                    print(f"\nTrajectory verification: {'✓ PASSED' if tv.get('all_passed') else '✗ FAILED'}")
                    print(tv.get("summary", ""))
                    print("=" * 80 + "\n")

        # Step 3: Reference solution doability — trajectory (if registered) else IWAP
        all_reviews_valid = True
        if self.llm_reviewer:
            llm_reviews = use_case_results.get("llm_reviews", [])
            all_reviews_valid = all(review.get("valid", False) for review in llm_reviews) and len(llm_reviews) > 0

        if not all_reviews_valid:
            invalid_count = sum(1 for review in use_case_results.get("llm_reviews", []) if not review.get("valid", False))
            self._print_step_banner(
                "⏭️  STEP 3: SKIPPED",
                f"Use Case: {use_case.name}",
                f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}",
                f"Invalid Reviews: {invalid_count}",
                "Reason: Not all LLM reviews are valid",
            )
            logger.info(f"Step 3: Skipping reference doability check for {use_case.name} because not all LLM reviews are valid")
            use_case_results["iwap_status"] = {
                "skipped": True,
                "reason": "Not all LLM reviews are valid",
                "invalid_reviews": invalid_count,
                "total_reviews": len(use_case_results.get("llm_reviews", [])),
            }
            use_case_results["dynamic_verification"] = self._make_skipped_dynamic_verification("Step 3 skipped (not all LLM reviews are valid)")
        else:
            trajectory = None
            if self.config.trajectory_doability_enabled:
                tmap = get_trajectory_map(self.web_project.id)
                if tmap:
                    trajectory = tmap.get(use_case.name)

            step3_with_trajectory = trajectory is not None
            step3_with_iwap = self.iwap_client is not None

            if step3_with_trajectory:
                step3_lines = [
                    "🔄 STEP 3: REFERENCE SOLUTION (TRAJECTORY)",
                    f"Use Case: {use_case.name}",
                    f"Project ID: {self.web_project.id}",
                ]
                if self.llm_reviewer:
                    step3_lines.extend(
                        [
                            f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}",
                            "All LLM Reviews: VALID ✓",
                        ]
                    )
                else:
                    step3_lines.append("LLM Review: DISABLED (proceeding without gating)")
                step3_lines.append("Using in-repo trajectory as the reference solution (no IWAP call for this use case).")
                self._print_step_banner(*step3_lines)
                print("-" * 80)

                logger.info(f"Step 3: Trajectory reference doability for {use_case.name}")
                doability_result = doability_result_from_trajectory(trajectory, fallback_start_url=self.web_project.frontend_url)
                use_case_results["reference_solution_source"] = "trajectory"
                use_case_results["iwap_api_response"] = {
                    "success": True,
                    "source": "trajectory",
                    "use_case": use_case.name,
                    "website": self.web_project.id,
                    "data": {"tasks": []},
                }
                use_case_results["iwap_match_result"] = doability_result
                use_case_results["iwap_doability_result"] = doability_result
                print("\n" + "-" * 80)
                print("🔍 CHECKING USE CASE DOABILITY (trajectory)")
                print("-" * 80)
                self._print_doability_result(doability_result)
                print("=" * 80 + "\n")

                if doability_result.get("matched", False):
                    use_case_results["iwap_status"] = {
                        "executed": True,
                        "matched": True,
                        "doable": True,
                        "source": "trajectory",
                        "reason": "Use case is doable — reference trajectory is registered",
                    }
                else:
                    use_case_results["iwap_status"] = {
                        "executed": True,
                        "matched": False,
                        "doable": False,
                        "source": "trajectory",
                        "reason": doability_result.get("reason", "Trajectory could not be converted to a reference solution"),
                    }

                await self._run_step4_dynamic_verification(use_case, use_case_results)

            elif step3_with_iwap:
                step3_lines = [
                    "🔄 STEP 3: IWAP USE CASE DOABILITY CHECK",
                    f"Use Case: {use_case.name}",
                    f"Project ID: {self.web_project.id}",
                ]
                if self.llm_reviewer:
                    step3_lines.extend(
                        [
                            f"Total Tasks Reviewed: {len(use_case_results.get('llm_reviews', []))}",
                            "All LLM Reviews: VALID ✓",
                        ]
                    )
                else:
                    step3_lines.append("LLM Review: DISABLED (proceeding without gating)")
                step3_lines.extend(
                    [
                        "Checking if use case is doable (has successful solution)...",
                        "Note: We don't compare specific constraints, just check if use case has been solved before",
                    ]
                )
                self._print_step_banner(*step3_lines)
                print("-" * 80)

                logger.info(f"Step 3: IWAP Use Case Doability Check for {use_case.name} (LLM review {'enabled' if self.llm_reviewer else 'disabled'})")
                use_case_results["reference_solution_source"] = "iwap"
                iwap_result = await self.iwap_client.get_tasks_with_solutions(
                    project_id=self.web_project.id,
                    use_case_name=use_case.name,
                    our_tasks=tasks,
                    page=1,
                    limit=50,
                )

                use_case_results["iwap_api_response"] = iwap_result

                if iwap_result:
                    success = iwap_result.get("success", False)
                    print(f"IWAP API Call: {'✓ SUCCESS' if success else '✗ FAILED'}")
                    if success:
                        api_data = iwap_result.get("data", {})
                        tasks_count = len(api_data.get("tasks", [])) if isinstance(api_data, dict) else 0
                        print(f"Tasks returned: {tasks_count}")
                        print(f"Website: {iwap_result.get('website', 'N/A')}")
                        print(f"Use Case: {iwap_result.get('use_case', 'N/A')}")

                        print("\n" + "-" * 80)
                        print("🔍 CHECKING USE CASE DOABILITY")
                        print("-" * 80)
                        print("Looking for ANY successful solution for this use case...")
                        print("(We don't compare specific constraints, just check if use case is doable)")

                        our_tasks = tasks
                        doability_result = self.iwap_client.process_api_response_for_tasks(iwap_result, our_tasks)

                        use_case_results["iwap_match_result"] = doability_result
                        use_case_results["iwap_doability_result"] = doability_result

                        self._print_doability_result(doability_result)
                    else:
                        error = iwap_result.get("error", "Unknown error")
                        print(f"Error: {error}")
                else:
                    print("IWAP API Call: ✗ FAILED (No response)")

                print("=" * 80 + "\n")

                logger.info(f"IWAP Use Case Doability Check for {use_case.name}: success={iwap_result.get('success', False) if iwap_result else False}")

                if iwap_result and iwap_result.get("success", False):
                    doability_result = use_case_results.get("iwap_match_result", {})
                    if doability_result.get("matched", False):
                        use_case_results["iwap_status"] = {
                            "executed": True,
                            "matched": True,
                            "doable": True,
                            "source": "iwap",
                            "reason": "Use case is doable - successful solution found from IWAP API",
                        }
                    else:
                        use_case_results["iwap_status"] = {
                            "executed": True,
                            "matched": False,
                            "doable": False,
                            "source": "iwap",
                            "reason": doability_result.get("reason", "No successful solution found for this use case"),
                        }
                else:
                    use_case_results["iwap_status"] = {
                        "executed": True,
                        "success": False,
                        "source": "iwap",
                        "reason": iwap_result.get("error", "API call failed") if iwap_result else "No response",
                    }

                await self._run_step4_dynamic_verification(use_case, use_case_results)

            else:
                self._print_step_banner(
                    "⏭️  STEP 3: SKIPPED",
                    f"Use Case: {use_case.name}",
                    "Reason: No trajectory registered for this use case and IWAP is disabled",
                )
                print("=" * 80)
                print(f"Use Case: {use_case.name}")
                print("Enable trajectories in trajectory_registry or enable IWAP (omit --trajectories-only / configure iwap_enabled).")
                logger.info(f"Step 3: Skipping reference doability for {use_case.name} (no trajectory, IWAP disabled)")
                use_case_results["iwap_status"] = {
                    "skipped": True,
                    "reason": "No trajectory for use case and IWAP client disabled",
                }
                use_case_results["dynamic_verification"] = self._make_skipped_dynamic_verification("Step 3 skipped (no trajectory and IWAP disabled)")

        # Step 3: trajectory preferred, else IWAP (when LLM gating passes)
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

                # Extract nested conditional expression
                llm_review_data = None
                if llm_review:
                    llm_review_data = {
                        "valid": llm_review.get("valid", False),
                        "score": llm_review.get("score"),
                    }

                formatted_task = {
                    "task_id": task_id,
                    "prompt": task_info.get("prompt", ""),
                    "seed": task_info.get("seed"),
                    "constraints": task_info.get("constraints_str", ""),
                    "llm_review": llm_review_data,
                }

                formatted_use_case["tasks"].append(formatted_task)

            traj_raw = use_case_data.get("trajectory_verification")
            if traj_raw is not None:
                formatted_use_case["trajectory_verification"] = self._compact_trajectory_results_for_storage(traj_raw)

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

    def _compact_trajectory_results_for_storage(self, traj_raw: dict[str, Any]) -> dict[str, Any]:
        """Minimal trajectory block for JSON output (mirrors dynamic_verification shape)."""
        if traj_raw.get("skipped"):
            return {
                "skipped": True,
                "reason": traj_raw.get("reason", ""),
            }
        if traj_raw.get("error"):
            return {
                "error": traj_raw.get("error"),
                "all_passed": False,
            }
        seed_results: dict[str, Any] = {}
        for seed, seed_result in (traj_raw.get("results") or {}).items():
            evaluation = seed_result.get("evaluation", {}) if isinstance(seed_result, dict) else {}
            if evaluation:
                seed_results[str(seed)] = {
                    "evaluation": evaluation,
                    "score": evaluation.get("final_score", 0.0),
                    "tests_passed": evaluation.get("tests_passed", 0),
                    "total_tests": evaluation.get("total_tests", 0),
                    "success": evaluation.get("success", False),
                }
            else:
                seed_results[str(seed)] = {
                    "score": 0.0,
                    "success": seed_result.get("success", False) if isinstance(seed_result, dict) else False,
                    "error": seed_result.get("error") if isinstance(seed_result, dict) else None,
                }
        return {
            "trajectory_name": traj_raw.get("trajectory_name"),
            "seeds_tested": traj_raw.get("seeds_tested", []),
            "results_by_seed": seed_results,
            "all_passed": traj_raw.get("all_passed", False),
            "passed_count": traj_raw.get("passed_count", 0),
            "total_count": traj_raw.get("total_count", 0),
            "needs_review": traj_raw.get("needs_review", False),
        }

    def _calculate_summary(self) -> dict[str, Any]:
        """
        Calculate summary statistics for all use cases

        Returns:
            Dictionary with summary information:
            - task_generation: Pass | Fail
            - number_of_tasks_generated: int
            - llm_review: Pass | Fail
            - dynamic_verification: Pass | Fail
            - trajectory_verification: Pass | Fail | N/A
        """
        total_tasks = 0
        all_tasks_generated = True
        all_llm_reviews_passed = True
        all_dynamic_verification_passed = True
        has_dynamic_verification = False
        has_trajectory_verification = False
        all_trajectory_verification_passed = True

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

            traj = use_case_data.get("trajectory_verification")
            if traj is not None and self.config.evaluate_trajectories:
                if traj.get("skipped"):
                    pass
                elif traj.get("error"):
                    has_trajectory_verification = True
                    all_trajectory_verification_passed = False
                else:
                    has_trajectory_verification = True
                    if not traj.get("all_passed", False):
                        all_trajectory_verification_passed = False

        # Determine summary status
        # Dynamic verification: Pass if all seeds passed (all_passed=True), else Fail
        # If no dynamic verification was executed, we can't determine pass/fail

        # Extract nested conditional expression for dynamic_verification
        dynamic_verification_status = "N/A"
        if has_dynamic_verification:
            dynamic_verification_status = "Pass" if all_dynamic_verification_passed else "Fail"

        trajectory_verification_status = "N/A"
        if self.config.evaluate_trajectories and has_trajectory_verification:
            trajectory_verification_status = "Pass" if all_trajectory_verification_passed else "Fail"

        if self.config.evaluate_trajectories_only:
            summary = {
                "task_generation": "Skipped",
                "number_of_tasks_generated": 0,
                "llm_review": "Skipped",
                "dynamic_verification": dynamic_verification_status,
                "trajectory_verification": trajectory_verification_status,
            }
        else:
            summary = {
                "task_generation": "Pass" if all_tasks_generated and total_tasks > 0 else "Fail",
                "number_of_tasks_generated": total_tasks,
                "llm_review": "Pass" if (all_llm_reviews_passed or not self.llm_reviewer) else "Fail",
                "dynamic_verification": dynamic_verification_status,
                "trajectory_verification": trajectory_verification_status,
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

        # Use asyncio.to_thread for synchronous file I/O
        def _write_results_file(file_path: Path, data: dict) -> None:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        await asyncio.to_thread(_write_results_file, output_file, results_dict)
        logger.info(f"Results saved to: {output_file}")

        # Also save a focused report with misgenerated/suspicious tasks to make manual review easy
        misgenerated_report = self._build_misgenerated_tasks_report()
        misgenerated_file = output_dir / f"misgenerated_tasks_{self.web_project.id}.json"
        await asyncio.to_thread(_write_results_file, misgenerated_file, self._serialize_results(misgenerated_report))
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
                "total_flagged_tasks": 0,
            },
        }

        for use_case_name, use_case_data in self.results.get("use_cases", {}).items():
            tasks: list[dict[str, Any]] = use_case_data.get("tasks", []) or []
            reviews: list[dict[str, Any]] = use_case_data.get("llm_reviews", []) or []

            # Include use cases where task generation failed (no tasks) for manual inspection.
            if not tasks:
                if self.config.evaluate_trajectories_only:
                    continue
                report["use_cases"][use_case_name] = {
                    "use_case_description": use_case_data.get("use_case_description", ""),
                    "flagged_tasks": [],
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

                flagged_tasks.append(
                    {
                        "task_id": task_id,
                        "seed": seed,
                        "prompt": prompt,
                        "constraints_str": constraints_str,
                        "constraints": constraints,
                        "llm_review": review,
                        "suspicious_reasons": suspicious_reasons,
                        "overridden_by_heuristic": overridden,
                    }
                )

                if llm_valid is False:
                    report["summary"]["failed_llm_review_tasks"] += 1
                if suspicious_reasons:
                    report["summary"]["suspicious_tasks"] += 1

            if flagged_tasks:
                report["use_cases"][use_case_name] = {
                    "use_case_description": use_case_data.get("use_case_description", ""),
                    "flagged_tasks": flagged_tasks,
                }
                report["summary"]["use_cases_with_issues"] += 1
                report["summary"]["total_flagged_tasks"] += len(flagged_tasks)

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

    def _get_task_seed_and_constraints(self, task: Task) -> tuple[int | None, list | None, str]:
        """
        Extract seed and constraint data from a task for display/serialization.
        Returns (seed_value, constraints_list, constraints_str).
        """
        seed_value = self._extract_seed_from_url(task.url)
        constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
        constraints_str = task.use_case.constraints_to_str() if task.use_case else ""
        return seed_value, constraints, constraints_str

    def _print_step_banner(self, *lines: str, leading_newline: bool = True, trailing_newline: bool = True) -> None:
        """Print a section banner with separator lines (80 chars). Reduces duplicated banner code."""
        if leading_newline:
            print()
        print("=" * 80)
        for line in lines:
            print(line)
        print("=" * 80 + ("\n" if trailing_newline else ""))

    def _print_constraints_details(self, constraints_str: str, line_indent: str = "     ", header: str = "   Constraints Details:") -> None:
        """Print constraints string line-by-line with optional header. Reusable for task/review output."""
        if not constraints_str or not constraints_str.strip():
            return
        print(header)
        for line in constraints_str.split("\n"):
            if line.strip():
                print(f"{line_indent}{line}")

    def _print_task_info_block(
        self,
        task_id: str,
        prompt: str,
        seed_value: int | None,
        constraints: list | None,
        constraints_str: str,
        *,
        use_case_name: str = "",
        line_indent: str = "   ",
        constraints_header: str = "   Constraints Details:",
        prompt_max_length: int | None = 100,
        prompt_on_new_line: bool = False,
    ) -> None:
        """Print task ID, use case, seed, constraints count/details, and prompt. Reused for task generation and LLM review."""
        print(f"{line_indent}Task ID: {task_id}")
        if use_case_name:
            print(f"{line_indent}Use Case: {use_case_name}")
        print(f"{line_indent}Seed: {seed_value if seed_value is not None else 'N/A'}")
        print(f"{line_indent}Constraints: {len(constraints) if constraints else 0} constraint(s)")
        self._print_constraints_details(constraints_str, line_indent=line_indent, header=constraints_header)
        display_prompt = _truncate_for_display(prompt, prompt_max_length) if prompt_max_length else prompt
        if prompt_on_new_line:
            print("\nPrompt:")
            print(f"  {display_prompt}")
        else:
            print(f"{line_indent}Prompt: {display_prompt}")

    async def _run_step4_dynamic_verification(self, use_case: UseCase, use_case_results: dict[str, Any]) -> None:
        """Step 4: replay reference solution (IWAP or trajectory) across seeds."""
        doability_result = use_case_results.get("iwap_match_result", {})
        if doability_result.get("matched", False) and doability_result.get("actions"):
            solution_actions = doability_result.get("actions", [])
            api_prompt = doability_result.get("api_prompt", "")
            api_tests = doability_result.get("api_tests", [])
            api_start_url = doability_result.get("api_start_url", "")

            self._print_step_banner(
                "🔄 STEP 4: DYNAMIC VERIFICATION",
                f"Use Case: {use_case.name}",
                f"Using Solution Prompt: {_truncate_for_display(api_prompt, 100)}",
                f"Evaluating solution with {len(solution_actions)} actions against different seeds",
                f"Seeds to test: {self.config.seed_values}",
                "Note: Testing if solution works across different dynamic content variations",
            )

            if self.dynamic_verifier and self.config.dynamic_verification_enabled:
                if api_prompt and api_start_url:
                    logger.info(f"Step 4: Evaluating reference solution with different seeds for use case {use_case.name}")
                    dynamic_result = await self.dynamic_verifier.verify_task_with_seeds(
                        api_prompt=api_prompt,
                        api_tests=api_tests,
                        api_start_url=api_start_url,
                        use_case=use_case,
                        seed_values=self.config.seed_values,
                        solution_actions=solution_actions,
                    )
                    use_case_results["dynamic_verification"] = dynamic_result

                    print("\n" + "=" * 80)
                    print("📊 STEP 4 SUMMARY")
                    print("=" * 80)
                    print(dynamic_result.get("summary", "No summary available"))
                    print(f"Passed: {dynamic_result.get('passed_count', 0)}/{dynamic_result.get('total_count', 0)}")

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
                    use_case_results["dynamic_verification"] = self._make_skipped_dynamic_verification("No reference task available (missing api_prompt or api_start_url)")
            else:
                logger.info("Dynamic verification is disabled")
                use_case_results["dynamic_verification"] = self._make_skipped_dynamic_verification("Dynamic verification is disabled")
        else:
            skip_reason = "Use case is not doable — no matched reference solution (trajectory or IWAP)" if not doability_result.get("matched", False) else "No actions in solution"
            self._print_step_banner("⏭️  STEP 4: SKIPPED", f"Use Case: {use_case.name}", f"Reason: {skip_reason}")
            use_case_results["dynamic_verification"] = self._make_skipped_dynamic_verification(skip_reason)

    def _print_doability_result(self, doability_result: dict[str, Any]) -> None:
        """Print use case doability result (matched vs not matched). Centralizes IWAP doability output."""
        if doability_result.get("matched", False):
            reason = doability_result.get("reason", "")
            actions = doability_result.get("actions", [])
            api_task_id = doability_result.get("api_task_id", "N/A")
            api_prompt = doability_result.get("api_prompt", "N/A")
            total_solutions = doability_result.get("total_solutions_found", 0)
            print("✓ USE CASE IS DOABLE!")
            print(f"  Reason: {reason}")
            print(f"  Total Solutions Found: {total_solutions}")
            print(f"  Using Solution From Task ID: {api_task_id}")
            print(f"  Solution Prompt: {_truncate_for_display(api_prompt, 80)}")
            print(f"  Actions Found: {len(actions) if actions else 0} actions")
            print(f"  First Action: {actions[0] if actions else 'N/A'}")
        else:
            reason = doability_result.get("reason", UNKNOWN_REASON)
            print("✗ USE CASE NOT DOABLE")
            print(f"  ⚠️  WARNING: {reason}")

    def _print_v2_comparison_results(self, comparison_results: list[dict[str, Any]]) -> None:
        """Print pairwise seed comparison results for V2 dataset diversity. Reduces duplicated comparison output."""
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

    def _make_skipped_dynamic_verification(self, reason: str) -> dict[str, Any]:
        """Build the standard dict for a skipped dynamic verification step. Centralizes structure."""
        return {
            "skipped": True,
            "reason": reason,
            "all_passed": False,
            "passed_count": 0,
            "total_count": 0,
        }

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
            if self.config.evaluate_trajectories_only:
                summary_lines.append("  Step 1 (Task Generation): ⏭️ Skipped (trajectories-only)")
                summary_lines.append("  Step 1 (LLM Review): ⏭️ Skipped (trajectories-only)")
            else:
                tasks = use_case_data.get("tasks", [])
                summary_lines.append(f"  Step 1 (Task Generation): {len(tasks)} tasks generated")

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
                    reason = dataset_diversity.get("reason", UNKNOWN_REASON)
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

            # Trajectory verification (optional)
            traj_v = use_case_data.get("trajectory_verification")
            if traj_v is not None and self.config.evaluate_trajectories:
                if traj_v.get("skipped"):
                    summary_lines.append(f"  Trajectory replay: ⏭️ Skipped ({traj_v.get('reason', UNKNOWN_REASON)})")
                elif traj_v.get("error"):
                    summary_lines.append(f"  Trajectory replay: ✗ Error ({traj_v.get('error')})")
                else:
                    ok = traj_v.get("all_passed", False)
                    pc, tc = traj_v.get("passed_count", 0), traj_v.get("total_count", 0)
                    summary_lines.append(
                        f"  Trajectory replay: {'✓ Passed' if ok else '✗ Failed'} ({pc}/{tc} seeds)",
                    )

            # Step 3: IWAP API / Doability check
            iwap_status = use_case_data.get("iwap_status")
            if iwap_status:
                if iwap_status.get("skipped", False):
                    # Step 3 was skipped
                    reason = iwap_status.get("reason", UNKNOWN_REASON)
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
                        reason = dynamic_verification.get("reason", UNKNOWN_REASON)
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
        if categories["generation_skipped"]:
            summary_lines.append(
                f"  ⏭️  Skipped — trajectories-only ({len(categories['generation_skipped'])}): {', '.join(categories['generation_skipped'])}",
            )
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
        if categories["iwap_skipped"]:
            summary_lines.append(
                f"  ⏭️  IWAP not run ({len(categories['iwap_skipped'])}): {', '.join(categories['iwap_skipped'])}",
            )
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
        if categories["generation_skipped"]:
            summary_lines.append(f"  - Task gen skipped (trajectories-only): {len(categories['generation_skipped'])}/{total_use_cases}")
            summary_lines.append("  - V2 dataset diversity: skipped (trajectories-only)")
        else:
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
            "generation_skipped": [],
            "dataset_diverse": [],
            "dataset_not_diverse": [],
            "dataset_untested": [],
            "has_solution": [],
            "no_solution": [],
            "iwap_skipped": [],
            "truly_dynamic": [],
            "not_dynamic": [],
            "dynamic_partial": [],
            "dynamic_untested": [],
        }

        for use_case_name, use_case_data in self.results["use_cases"].items():
            # Task Generation Quality
            if self.config.evaluate_trajectories_only:
                categories["generation_skipped"].append(use_case_name)
            else:
                llm_reviews = use_case_data.get("llm_reviews", [])
                if llm_reviews:
                    all_valid = all(r.get("valid", False) for r in llm_reviews)
                    if all_valid and len(llm_reviews) > 0:
                        categories["generation_ok"].append(use_case_name)
                    else:
                        categories["generation_failed"].append(use_case_name)
                else:
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
            iwap_status = use_case_data.get("iwap_status") or {}
            if iwap_status.get("skipped"):
                categories["iwap_skipped"].append(use_case_name)
            elif iwap_status.get("matched", False):
                categories["has_solution"].append(use_case_name)
            elif iwap_status.get("executed", False):
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
