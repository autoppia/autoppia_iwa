"""
Web Verification Pipeline

Main pipeline that orchestrates:
0. Pre-validation (project setup, events, use cases)
1. Task generation (2 tasks per use case with constraints) + LLM Review (V1)
2. Dataset diversity verification - verify datasets differ with different seeds (V2)
3. IWAP doability check (find any successful solution for use case)
4. Dynamic verification with different seeds (V3)
"""

import asyncio
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

    # Constants
    UNKNOWN_REASON = "Unknown reason"

    # ============================================================================
    # INITIALIZATION AND PUBLIC METHODS
    # ============================================================================

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

            summary_lines.extend(self._get_step_0_and_1_summary(use_case_data))
            summary_lines.extend(self._get_step_2_summary(use_case_data))
            summary_lines.extend(self._get_step_3_summary(use_case_data))
            summary_lines.extend(self._get_step_4_summary(use_case_data))

        categories = self._categorize_use_cases()
        summary_lines.extend(self._get_final_conclusion_summary(categories))

        return "\n".join(summary_lines)

    # ============================================================================
    # MAIN PIPELINE ORCHESTRATION
    # ============================================================================

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
            "dataset_diversity_verification": None,
            "doability_check": None,
            "dynamic_verification": None,
        }

        # Step 1: Generate tasks
        tasks = await self._generate_tasks_for_use_case(use_case)
        if not tasks:
            use_case_results["error"] = "No tasks generated"
            return use_case_results

        # Step 1b: Review tasks with LLM
        task_review_map = await self._review_tasks_with_llm(tasks, use_case)
        self._store_task_results(task_review_map, use_case_results)

        # Step 2: Dataset Diversity Verification
        await self._verify_dataset_diversity(use_case, use_case_results)

        # Step 3: IWAP Doability Check
        await self._check_iwap_doability(use_case, tasks, use_case_results)

        # Step 4: Dynamic Verification
        await self._perform_dynamic_verification(use_case, use_case_results)

        return use_case_results

    # ============================================================================
    # STEP 1: TASK GENERATION
    # ============================================================================

    async def _generate_tasks_for_use_case(self, use_case: UseCase) -> list[Task]:
        """Generate tasks for a use case. Returns empty list if generation fails."""
        print("\n" + "=" * 80)
        print("📝 STEP 1: TASK GENERATION")
        print("=" * 80)
        print(f"Use Case: {use_case.name}")
        print(f"Generating {self.config.tasks_per_use_case} task(s)...")
        print("=" * 80 + "\n")

        tasks = []
        import sys

        for task_index in range(self.config.tasks_per_use_case):
            task_num = task_index + 1
            total_tasks = self.config.tasks_per_use_case
            task = await self._generate_single_task(use_case, task_num, total_tasks)
            if task:
                tasks.append(task)

        if not tasks:
            print("=" * 80)
            print("❌ ERROR: No tasks generated for use case")
            print("=" * 80 + "\n")
            logger.warning(f"No tasks generated for use case: {use_case.name}")
        else:
            print("=" * 80)
            print(f"✅ All {len(tasks)} task(s) generated successfully!")
            print("=" * 80)
            sys.stdout.flush()
            print()

        return tasks

    async def _generate_single_task(self, use_case: UseCase, task_num: int, total_tasks: int) -> Task | None:
        """Generate a single task for a use case."""
        import copy
        import sys

        print(f"🔄 Generating task {task_num}/{total_tasks}...")
        use_case.constraints = None

        task_list = await self.task_generator.generate_tasks_for_use_case(
            use_case=use_case,
            number_of_prompts=1,
            dynamic=self.config.dynamic_enabled,
        )

        if task_list and len(task_list) > 0:
            task = task_list[0]
            if use_case.constraints and task.use_case:
                task.use_case = copy.deepcopy(use_case)
                logger.debug(f"Created independent use_case copy for task {task_num} with {len(task.use_case.constraints)} constraints")

            self._print_task_generation_details(task, task_num, total_tasks)
            sys.stdout.flush()
            return task
        else:
            print(f"❌ Failed to generate task {task_num}/{total_tasks}")
            print()
            return None

    def _print_task_generation_details(self, task: Task, task_num: int, total_tasks: int) -> None:
        """Print details of a generated task."""
        seed_value = self._extract_seed_from_url(task.url)
        constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
        constraints_str = task.use_case.constraints_to_str() if task.use_case else ""

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

    # ============================================================================
    # STEP 1B: LLM REVIEW
    # ============================================================================

    async def _review_tasks_with_llm(self, tasks: list[Task], use_case: UseCase) -> dict[int, dict[str, Any]]:
        """Review tasks with LLM and return task_review_map."""
        print("\n" + "=" * 80)
        print("🤖 STEP 1: LLM REVIEW")
        print("=" * 80)
        print(f"Use Case: {use_case.name}")
        print(f"Reviewing {len(tasks)} task(s)...")
        print("=" * 80 + "\n")

        task_review_map = {}

        for task_index, task in enumerate(tasks):
            task_num = task_index + 1
            total_tasks = len(tasks)
            review_result = await self._perform_single_task_review(task, task_num, total_tasks, use_case)
            task_review_map[task_index] = {
                "task": task,
                "review_result": review_result,
            }

        self._print_review_summary(task_review_map)
        return task_review_map

    async def _perform_single_task_review(self, task: Task, task_num: int, total_tasks: int, use_case: UseCase) -> dict[str, Any]:
        """Perform LLM review for a single task."""
        seed_value = self._extract_seed_from_url(task.url)
        constraints_str = task.use_case.constraints_to_str() if task.use_case else ""
        import sys

        if self.llm_reviewer:
            print("=" * 80)
            print(f"📋 Reviewing Task {task_num}/{total_tasks}")
            print("=" * 80)
            print(f"Giving task {task_num} to LLM for review...")
            print()

            logger.debug(f"Reviewing task {task.id} with LLM: checking if prompt matches constraints")
            review_result = await self.llm_reviewer.review_task_and_constraints(task)
            review_result["task_id"] = task.id
            review_result["retry_count"] = 0

            sys.stdout.flush()
            self._print_task_review_details(task, use_case, seed_value, constraints_str)
            self._print_review_result(review_result, task_num)
            sys.stdout.flush()

            logger.debug(f"Task {task.id} LLM review result: valid={review_result.get('valid', False)}")
        else:
            review_result = {
                "valid": True,
                "task_id": task.id,
                "retry_count": 0,
                "skipped": True,
                "reasoning": "LLM review is disabled",
            }

        return review_result

    def _print_task_review_details(self, task: Task, use_case: UseCase, seed_value: int | None, constraints_str: str) -> None:
        """Print task details for review."""
        print("-" * 80)
        print("📝 TASK DETAILS:")
        print("-" * 80)
        print(f"Task ID: {task.id}")
        print(f"Use Case: {use_case.name}")
        print(f"Seed: {seed_value if seed_value else 'N/A'}")
        constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
        print(f"Constraints: {len(constraints) if constraints else 0} constraint(s)")
        if constraints_str:
            print("\nConstraints Details:")
            for line in constraints_str.split("\n"):
                if line.strip():
                    print(f"  {line}")
        print("\nPrompt:")
        print(f"  {task.prompt}")
        print("-" * 80)

    def _print_review_result(self, review_result: dict[str, Any], task_num: int) -> None:
        """Print LLM review result."""
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
        print()

        if review_result.get("valid", False):
            print(f"✅ Task {task_num} passed LLM review!\n")
        else:
            print(f"❌ Task {task_num} failed LLM review\n")

    def _print_review_summary(self, task_review_map: dict[int, dict[str, Any]]) -> None:
        """Print summary of review results."""
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

    def _store_task_results(self, task_review_map: dict[int, dict[str, Any]], use_case_results: dict[str, Any]) -> None:
        """Store task and review results in use_case_results."""
        for _task_index, task_info in sorted(task_review_map.items()):
            task = task_info["task"]
            review_result = task_info["review_result"]

            seed_value = self._extract_seed_from_url(task.url)
            constraints = task.use_case.constraints if task.use_case and task.use_case.constraints else None
            constraints_str = task.use_case.constraints_to_str() if task.use_case else ""
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

    # ============================================================================
    # STEP 2: DATASET DIVERSITY VERIFICATION
    # ============================================================================

    async def _verify_dataset_diversity(self, use_case: UseCase, use_case_results: dict[str, Any]) -> None:
        """Perform Step 2: Dataset Diversity Verification."""
        if not (self.config.dynamic_enabled and self.dynamic_verifier):
            logger.info("V2 Dataset Diversity Verification: Skipped (dynamic mode disabled or verifier unavailable)")
            use_case_results["dataset_diversity_verification"] = {
                "skipped": True,
                "reason": "Dynamic mode disabled or verifier unavailable",
                "passed": None,
            }
            return

        self._print_dataset_diversity_header(use_case)
        logger.info(f"Step 2 (V2): Dataset Diversity Verification for {use_case.name}")
        v2_result = await self.dynamic_verifier.verify_dataset_diversity_with_seeds(
            seed_values=self.config.seed_values,
        )

        use_case_results["dataset_diversity_verification"] = v2_result
        self._print_dataset_diversity_results(v2_result)

        comparison_results = v2_result.get("comparison_results", [])
        self._print_comparison_results(comparison_results)

        print(f"\n{v2_result.get('summary', 'No summary available')}")
        print("=" * 80 + "\n")

    def _print_dataset_diversity_header(self, use_case: UseCase) -> None:
        """Print header for dataset diversity verification."""
        print("\n" + "=" * 80)
        print("🔄 STEP 2 (V2): DATASET DIVERSITY VERIFICATION")
        print("=" * 80)
        print(f"Use Case: {use_case.name}")
        print(f"Project ID: {self.web_project.id}")
        print(f"Seeds to test: {self.config.seed_values}")
        print("Verifying that datasets are different with different seeds...")
        print("Note: This ensures dynamic data generation is working correctly")
        print("-" * 80)

    def _print_dataset_diversity_results(self, v2_result: dict[str, Any]) -> None:
        """Print dataset diversity verification results."""
        print(f"\nV2 Verification Result: {'✓ PASSED' if v2_result.get('passed', False) else '✗ FAILED'}")
        print(f"Seeds tested: {v2_result.get('seeds_tested', [])}")
        print(f"Datasets loaded: {v2_result.get('loaded_count', 0)}/{v2_result.get('expected_count', 0)}")
        print(f"All different: {'✓ YES' if v2_result.get('all_different', False) else '✗ NO'}")

    def _print_comparison_results(self, comparison_results: list[dict[str, Any]]) -> None:
        """Print pairwise comparison results."""
        if not comparison_results:
            return

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

    # ============================================================================
    # STEP 3: IWAP DOABILITY CHECK
    # ============================================================================

    async def _check_iwap_doability(self, use_case: UseCase, tasks: list[Task], use_case_results: dict[str, Any]) -> None:
        """Perform Step 3: IWAP Use Case Doability Check."""
        if not self.iwap_client:
            self._handle_iwap_skip(use_case, use_case_results, "IWAP client is disabled (--no-iwap flag used)", "STEP 2")
            logger.info(f"Step 3: Skipping IWAP Use Case Doability Check for {use_case.name} because IWAP client is disabled")
            return

        if not self._check_all_reviews_valid(use_case_results):
            self._handle_invalid_reviews_skip(use_case, use_case_results)
            return

        self._print_iwap_doability_header(use_case, use_case_results)
        logger.info(f"Step 3: IWAP Use Case Doability Check for {use_case.name} (LLM review {'enabled' if self.llm_reviewer else 'disabled'})")
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
                self._process_successful_iwap_response(iwap_result, use_case_results)
            else:
                error = iwap_result.get("error", "Unknown error")
                print(f"Error: {error}")
        else:
            print("IWAP API Call: ✗ FAILED (No response)")

        print("=" * 80 + "\n")
        logger.info(f"IWAP Use Case Doability Check for {use_case.name}: success={iwap_result.get('success', False) if iwap_result else False}")
        self._store_iwap_status(iwap_result, use_case_results)

    def _check_all_reviews_valid(self, use_case_results: dict[str, Any]) -> bool:
        """Check if all LLM reviews are valid."""
        if not self.llm_reviewer:
            return True
        llm_reviews = use_case_results.get("llm_reviews", [])
        return all(review.get("valid", False) for review in llm_reviews) and len(llm_reviews) > 0

    def _handle_invalid_reviews_skip(self, use_case: UseCase, use_case_results: dict[str, Any]) -> None:
        """Handle skip when not all LLM reviews are valid."""
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
        use_case_results["iwap_status"] = {
            "skipped": True,
            "reason": "Not all LLM reviews are valid",
            "invalid_reviews": invalid_count,
            "total_reviews": len(use_case_results.get("llm_reviews", [])),
        }
        use_case_results["dynamic_verification"] = {
            "skipped": True,
            "reason": "Step 3 skipped (not all LLM reviews are valid)",
            "all_passed": False,
            "passed_count": 0,
            "total_count": 0,
        }

    def _handle_iwap_skip(self, use_case: UseCase, use_case_results: dict[str, Any], reason: str, skip_step: str = "STEP 3") -> None:
        """Handle IWAP step skip with consistent formatting."""
        print("\n" + "=" * 80)
        print(f"⏭️  {skip_step}: SKIPPED")
        print("=" * 80)
        print(f"Use Case: {use_case.name}")
        print(f"Reason: {reason}")
        print("=" * 80 + "\n")
        use_case_results["iwap_status"] = {
            "skipped": True,
            "reason": reason,
        }
        use_case_results["dynamic_verification"] = {
            "skipped": True,
            "reason": f"{skip_step} skipped ({reason})",
            "all_passed": False,
            "passed_count": 0,
            "total_count": 0,
        }

    def _print_iwap_doability_header(self, use_case: UseCase, use_case_results: dict[str, Any]) -> None:
        """Print header for IWAP doability check."""
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

    def _process_successful_iwap_response(self, iwap_result: dict[str, Any], use_case_results: dict[str, Any]) -> None:
        """Process successful IWAP API response."""
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

        doability_result = self.iwap_client.process_api_response_for_tasks(iwap_result)
        use_case_results["iwap_match_result"] = doability_result
        use_case_results["iwap_doability_result"] = doability_result
        self._print_doability_results(doability_result)

    def _print_doability_results(self, doability_result: dict[str, Any]) -> None:
        """Print doability check results."""
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
            print(f"  Solution Prompt: {api_prompt[:80]}..." if len(api_prompt) > 80 else f"  Solution Prompt: {api_prompt}")
            print(f"  Actions Found: {len(actions) if actions else 0} actions")
            if actions:
                print(f"  First Action: {actions[0] if len(actions) > 0 else 'N/A'}")
        else:
            reason = doability_result.get("reason", self.UNKNOWN_REASON)
            print("✗ USE CASE NOT DOABLE")
            print(f"  ⚠️  WARNING: {reason}")

    def _store_iwap_status(self, iwap_result: dict[str, Any] | None, use_case_results: dict[str, Any]) -> None:
        """Store IWAP execution status in use_case_results."""
        if iwap_result and iwap_result.get("success", False):
            doability_result = use_case_results.get("iwap_match_result", {})
            if doability_result.get("matched", False):
                use_case_results["iwap_status"] = {
                    "executed": True,
                    "matched": True,
                    "doable": True,
                    "reason": "Use case is doable - successful solution found from IWAP API",
                }
            else:
                use_case_results["iwap_status"] = {
                    "executed": True,
                    "matched": False,
                    "doable": False,
                    "reason": doability_result.get("reason", "No successful solution found for this use case"),
                }
        else:
            use_case_results["iwap_status"] = {
                "executed": True,
                "success": False,
                "reason": iwap_result.get("error", "API call failed") if iwap_result else "No response",
            }

    # ============================================================================
    # STEP 4: DYNAMIC VERIFICATION
    # ============================================================================

    async def _perform_dynamic_verification(self, use_case: UseCase, use_case_results: dict[str, Any]) -> None:
        """Perform Step 4: Dynamic Verification."""
        doability_result = use_case_results.get("iwap_match_result", {})

        if not doability_result.get("matched", False) or not doability_result.get("actions"):
            print("\n" + "=" * 80)
            print("⏭️  STEP 4: SKIPPED")
            print("=" * 80)
            print(f"Use Case: {use_case.name}")
            skip_reason = "Use case is not doable - no successful solution found from IWAP API" if not doability_result.get("matched", False) else "No actions in solution"
            print(f"Reason: {skip_reason}")
            print("=" * 80 + "\n")
            use_case_results["dynamic_verification"] = {
                "skipped": True,
                "reason": skip_reason,
                "all_passed": False,
                "passed_count": 0,
                "total_count": 0,
            }
            return

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

        if not (self.dynamic_verifier and self.config.dynamic_verification_enabled):
            logger.info("Dynamic verification is disabled")
            use_case_results["dynamic_verification"] = {
                "skipped": True,
                "reason": "Dynamic verification is disabled",
                "all_passed": False,
                "passed_count": 0,
                "total_count": 0,
            }
            return

        if not (api_prompt and api_start_url):
            logger.warning("No reference task available for dynamic verification")
            use_case_results["dynamic_verification"] = {
                "skipped": True,
                "reason": "No reference task available (missing api_prompt or api_start_url)",
                "all_passed": False,
                "passed_count": 0,
                "total_count": 0,
            }
            return

        logger.info(f"Step 4: Evaluating API solution against API task with different seeds for use case {use_case.name}")
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

    # ============================================================================
    # RESULTS FORMATTING AND STORAGE
    # ============================================================================

    async def _save_results(self):
        """Save verification results to file in minimal, readable format"""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"verification_{self.web_project.id}.json"

        # Format results in minimal structure
        formatted_results = self._format_results_for_storage()

        # Convert to JSON-serializable format
        results_dict = self._serialize_results(formatted_results)

        # Use async file I/O to avoid blocking event loop
        await self._write_json_file_async(output_file, results_dict)

        logger.info(f"Results saved to: {output_file}")

        # Also save a focused report with misgenerated/suspicious tasks to make manual review easy
        misgenerated_report = self._build_misgenerated_tasks_report()
        misgenerated_file = output_dir / f"misgenerated_tasks_{self.web_project.id}.json"
        await self._write_json_file_async(misgenerated_file, self._serialize_results(misgenerated_report))
        logger.info(f"Misgenerated tasks report saved to: {misgenerated_file}")

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
                llm_review = llm_reviews[idx] if idx < len(llm_reviews) else None
                formatted_task = self._format_task_with_review(task_info, llm_review)
                formatted_use_case["tasks"].append(formatted_task)

            # Add matched data at use case level (only if matched)
            matched_data = self._format_matched_data(match_result, dynamic_verification)
            if matched_data:
                formatted_use_case["matched"] = matched_data

            formatted_results["use_cases"][use_case_name] = formatted_use_case

        # Calculate and add summary
        formatted_results["summary"] = self._calculate_summary()

        return formatted_results

    def _format_task_with_review(self, task_info: dict[str, Any], llm_review: dict[str, Any] | None) -> dict[str, Any]:
        """Format a single task with its LLM review."""
        # Extract nested conditionals for clarity
        llm_review_valid = llm_review.get("valid", False) if llm_review else None
        llm_review_score = llm_review.get("score") if llm_review else None
        llm_review_dict = (
            {
                "valid": llm_review_valid,
                "score": llm_review_score,
            }
            if llm_review
            else None
        )

        return {
            "task_id": task_info.get("task_id", ""),
            "prompt": task_info.get("prompt", ""),
            "seed": task_info.get("seed"),
            "constraints": task_info.get("constraints_str", ""),
            "llm_review": llm_review_dict,
        }

    def _format_dynamic_verification_results(self, dynamic_verification: dict[str, Any]) -> dict[str, Any] | None:
        """Format dynamic verification results by seed."""
        if not dynamic_verification or dynamic_verification.get("skipped", False):
            if dynamic_verification and dynamic_verification.get("skipped", False):
                return {
                    "skipped": True,
                    "reason": dynamic_verification.get("reason", ""),
                }
            return None

        seed_results = {}
        results_by_seed = dynamic_verification.get("results", {})
        for seed, seed_result in results_by_seed.items():
            evaluation = seed_result.get("evaluation", {})
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
                    "success": seed_result.get("success", False),
                    "error": seed_result.get("error"),
                }

        return {
            "seeds_tested": dynamic_verification.get("seeds_tested", []),
            "results_by_seed": seed_results,
            "all_passed": dynamic_verification.get("all_passed", False),
            "passed_count": dynamic_verification.get("passed_count", 0),
            "total_count": dynamic_verification.get("total_count", 0),
        }

    def _format_matched_data(self, match_result: dict[str, Any], dynamic_verification: dict[str, Any]) -> dict[str, Any] | None:
        """Format matched data for a use case."""
        if not match_result.get("matched", False):
            return None

        matched_data = {
            "match_type": match_result.get("match_type", ""),
            "api_task_id": match_result.get("api_task_id", ""),
            "api_prompt": match_result.get("api_prompt", ""),
            "api_start_url": match_result.get("api_start_url", ""),
        }

        dynamic_verification_data = self._format_dynamic_verification_results(dynamic_verification)
        if dynamic_verification_data:
            matched_data["dynamic_verification"] = dynamic_verification_data

        return matched_data

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
            total_tasks, all_tasks_generated = self._process_use_case_for_summary(use_case_data, total_tasks, all_tasks_generated)

            if not self._check_llm_reviews_passed(use_case_data):
                all_llm_reviews_passed = False

            dynamic_passed, has_dynamic = self._check_dynamic_verification_passed(use_case_data)
            if has_dynamic:
                has_dynamic_verification = True
                if not dynamic_passed:
                    all_dynamic_verification_passed = False

        dynamic_verification_status = self._determine_dynamic_verification_status(all_dynamic_verification_passed, has_dynamic_verification)

        summary = {
            "task_generation": "Pass" if all_tasks_generated and total_tasks > 0 else "Fail",
            "number_of_tasks_generated": total_tasks,
            "llm_review": "Pass" if (all_llm_reviews_passed or not self.llm_reviewer) else "Fail",
            "dynamic_verification": dynamic_verification_status,
        }

        return summary

    def _check_llm_reviews_passed(self, use_case_data: dict[str, Any]) -> bool:
        """Check if all LLM reviews passed for a use case."""
        llm_reviews = use_case_data.get("llm_reviews", [])
        if llm_reviews:
            return all(review.get("valid", False) for review in llm_reviews)
        return not self.llm_reviewer

    def _check_dynamic_verification_passed(self, use_case_data: dict[str, Any]) -> tuple[bool, bool]:
        """Check dynamic verification status. Returns (all_passed, has_dynamic_verification)."""
        dynamic_verification = use_case_data.get("dynamic_verification", {})
        if dynamic_verification and not dynamic_verification.get("skipped", False):
            return dynamic_verification.get("all_passed", False), True
        return True, False

    def _process_use_case_for_summary(self, use_case_data: dict[str, Any], total_tasks: int, all_tasks_generated: bool) -> tuple[int, bool]:
        """Process a single use case for summary calculation. Returns (updated_total_tasks, updated_all_tasks_generated)."""
        tasks = use_case_data.get("tasks", [])
        total_tasks += len(tasks)

        if not tasks or use_case_data.get("error"):
            all_tasks_generated = False

        return total_tasks, all_tasks_generated

    def _determine_dynamic_verification_status(self, all_dynamic_verification_passed: bool, has_dynamic_verification: bool) -> str:
        """Determine dynamic verification status string."""
        if all_dynamic_verification_passed and has_dynamic_verification:
            return "Pass"
        if has_dynamic_verification:
            return "Fail"
        return "N/A"

    def _write_json_file_sync(self, file_path: Path, data: dict[str, Any]) -> None:
        """Synchronous helper function for writing JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def _write_json_file_async(self, file_path: Path, data: dict[str, Any]) -> None:
        """Asynchronous wrapper for writing JSON file."""
        await asyncio.to_thread(self._write_json_file_sync, file_path, data)

    # ============================================================================
    # MISGENERATED TASKS REPORT
    # ============================================================================

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
                self._process_use_case_without_tasks(use_case_name, use_case_data, report)
                continue

            # Map reviews by task_id for stability
            reviews_by_task_id: dict[str, dict[str, Any]] = {str(r.get("task_id")): r for r in reviews if isinstance(r, dict) and r.get("task_id") is not None}

            flagged_tasks = self._process_flagged_tasks(tasks, reviews_by_task_id, report)

            if flagged_tasks:
                report["use_cases"][use_case_name] = {
                    "use_case_description": use_case_data.get("use_case_description", ""),
                    "flagged_tasks": flagged_tasks,
                }
                report["summary"]["use_cases_with_issues"] += 1
                report["summary"]["total_flagged_tasks"] += len(flagged_tasks)

        return report

    def _process_use_case_without_tasks(self, use_case_name: str, use_case_data: dict[str, Any], report: dict[str, Any]) -> None:
        """Process a use case that has no tasks (generation failed)."""
        report["use_cases"][use_case_name] = {
            "use_case_description": use_case_data.get("use_case_description", ""),
            "flagged_tasks": [],
            "generation_error": use_case_data.get("error") or "No tasks generated",
        }
        report["summary"]["use_cases_with_issues"] += 1

    def _process_flagged_tasks(self, tasks: list[dict[str, Any]], reviews_by_task_id: dict[str, dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
        """Process tasks and return list of flagged tasks."""
        flagged_tasks: list[dict[str, Any]] = []
        for task in tasks:
            task_id = str(task.get("task_id", ""))
            prompt = task.get("prompt", "") or ""
            constraints = task.get("constraints", None)

            review = reviews_by_task_id.get(task_id)
            overridden = bool(review.get("overridden_by_heuristic", False)) if review else False
            suspicious_reasons = self._flag_suspicious_prompt_against_constraints(prompt, constraints)

            if not self._should_flag_task(review, suspicious_reasons, overridden):
                continue

            flagged_task = self._build_flagged_task(task, review, suspicious_reasons, overridden)
            flagged_tasks.append(flagged_task)

            llm_valid = review.get("valid", None) if review else None
            if llm_valid is False:
                report["summary"]["failed_llm_review_tasks"] += 1
            if suspicious_reasons:
                report["summary"]["suspicious_tasks"] += 1

        return flagged_tasks

    def _should_flag_task(self, review: dict[str, Any] | None, suspicious_reasons: list[str], overridden: bool) -> bool:
        """Determine if a task should be flagged as misgenerated."""
        llm_valid = review.get("valid", None) if review else None
        return (llm_valid is False) or bool(suspicious_reasons) or overridden

    def _build_flagged_task(self, task: dict[str, Any], review: dict[str, Any] | None, suspicious_reasons: list[str], overridden: bool) -> dict[str, Any]:
        """Build a flagged task entry for the report."""
        return {
            "task_id": str(task.get("task_id", "")),
            "seed": task.get("seed"),
            "prompt": task.get("prompt", "") or "",
            "constraints_str": task.get("constraints_str", "") or "",
            "constraints": task.get("constraints"),
            "llm_review": review,
            "suspicious_reasons": suspicious_reasons,
            "overridden_by_heuristic": overridden,
        }

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

    # ============================================================================
    # SUMMARY GENERATION
    # ============================================================================

    def _get_step_0_and_1_summary(self, use_case_data: dict[str, Any]) -> list[str]:
        """Get summary lines for Step 0 and Step 1."""
        summary_lines = []
        summary_lines.append("  Step 0 (Pre-validation): ✓ Passed")

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

        return summary_lines

    def _get_step_2_summary(self, use_case_data: dict[str, Any]) -> list[str]:
        """Get summary lines for Step 2 (V2 Dataset Diversity)."""
        summary_lines = []
        dataset_diversity = use_case_data.get("dataset_diversity_verification")
        if dataset_diversity:
            if dataset_diversity.get("skipped", False):
                reason = dataset_diversity.get("reason", self.UNKNOWN_REASON)
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

        return summary_lines

    def _get_step_3_summary(self, use_case_data: dict[str, Any]) -> list[str]:
        """Get summary lines for Step 3 (IWAP)."""
        summary_lines = []
        iwap_status = use_case_data.get("iwap_status")
        if iwap_status:
            summary_lines.append(self._get_iwap_status_summary(iwap_status))
        else:
            doability = use_case_data.get("doability_check")
            if doability:
                summary_lines.append(self._get_legacy_doability_summary(doability))
            else:
                summary_lines.append("  Step 3 (IWAP): ⏭️ Not executed")

        return summary_lines

    def _get_iwap_status_summary(self, iwap_status: dict[str, Any]) -> str:
        """Get summary line for IWAP status."""
        if iwap_status.get("skipped", False):
            reason = iwap_status.get("reason", self.UNKNOWN_REASON)
            return f"  Step 3 (IWAP): ⏭️ Skipped ({reason})"

        if not iwap_status.get("executed", False):
            return "  Step 3 (IWAP): ⏭️ Not executed"

        if iwap_status.get("matched", False):
            return "  Step 3 (IWAP): ✓ Executed (solution found)"

        if iwap_status.get("matched") is False:
            reason = iwap_status.get("reason", "No solution found")
            return f"  Step 3 (IWAP): ✓ Executed ({reason})"

        if not iwap_status.get("success", True):
            reason = iwap_status.get("reason", "API call failed")
            return f"  Step 3 (IWAP): ✗ Failed ({reason})"

        return "  Step 3 (IWAP): ✓ Executed"

    def _get_legacy_doability_summary(self, doability: dict[str, Any]) -> str:
        """Get summary line for legacy doability check format."""
        is_doable = doability.get("doable", False)
        success_rate = doability.get("success_rate", 0.0)
        return f"  Step 3 (IWAP): {'✓ Doable' if is_doable else '✗ Not doable'} (success rate: {success_rate:.2%})"

    def _get_step_4_summary(self, use_case_data: dict[str, Any]) -> list[str]:
        """Get summary lines for Step 4 (Dynamic Verification)."""
        summary_lines = []
        dynamic_verification = use_case_data.get("dynamic_verification")
        if dynamic_verification:
            if isinstance(dynamic_verification, dict):
                summary_lines.extend(self._get_dict_dynamic_verification_summary(dynamic_verification))
            elif isinstance(dynamic_verification, list):
                summary_lines.extend(self._get_list_dynamic_verification_summary(dynamic_verification))
        else:
            summary_lines.append("  Step 4 (Dynamic): ⏭️ Skipped (no data)")

        return summary_lines

    def _get_results_by_seed_from_dynamic_verification(self, dynamic_verification: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract results_by_seed from dynamic_verification, with fallback to results."""
        results_by_seed = dynamic_verification.get("results_by_seed", {})
        if not results_by_seed:
            original_results = dynamic_verification.get("results", {})
            results_by_seed = {str(k): v for k, v in original_results.items()}
        return results_by_seed

    def _build_dynamic_verification_summary_lines(self, dynamic_verification: dict[str, Any], all_passed: bool, passed_count: int, total_count: int) -> list[str]:
        """Build summary lines for dynamic verification results."""
        summary_lines = []
        seeds_tested = dynamic_verification.get("seeds_tested", [])
        results_by_seed = self._get_results_by_seed_from_dynamic_verification(dynamic_verification)

        seed_details = self._build_seed_details(seeds_tested, results_by_seed) if seeds_tested else self._build_seed_details_from_results(results_by_seed)

        if seed_details:
            seeds_str = ", ".join(seed_details)
            status_icon = "✓ Passed" if all_passed else "✗ Failed"
            summary_lines.append(f"  Step 4 (Dynamic): {status_icon} ({passed_count}/{total_count} seeds passed)")
            summary_lines.append(f"    Solution tested with seeds: {seeds_str}")

            if dynamic_verification.get("needs_review", False):
                summary_lines.append(f"    ⚠️  REVIEW RECOMMENDED: Use case may not be truly dynamic (same solution works for all {total_count} seeds)")
        else:
            status_icon = "✓ Passed" if all_passed else "✗ Failed"
            summary_lines.append(f"  Step 4 (Dynamic): {status_icon} ({passed_count}/{total_count} seeds)")

        return summary_lines

    def _get_dict_dynamic_verification_summary(self, dynamic_verification: dict[str, Any]) -> list[str]:
        """Get summary lines for dict format dynamic verification."""
        summary_lines = []
        skipped = dynamic_verification.get("skipped", False)
        if skipped:
            reason = dynamic_verification.get("reason", self.UNKNOWN_REASON)
            summary_lines.append(f"  Step 4 (Dynamic): ⏭️ Skipped ({reason})")
        else:
            all_passed = dynamic_verification.get("all_passed", False)
            passed_count = dynamic_verification.get("passed_count", 0)
            total_count = dynamic_verification.get("total_count", 0)
            summary_lines.extend(self._build_dynamic_verification_summary_lines(dynamic_verification, all_passed, passed_count, total_count))
        return summary_lines

    def _get_list_dynamic_verification_summary(self, dynamic_verification: list[dict[str, Any]]) -> list[str]:
        """Get summary lines for list format dynamic verification (legacy)."""
        all_passed = all(dr.get("all_passed", False) for dr in dynamic_verification if isinstance(dr, dict))
        return [f"  Step 4 (Dynamic): {'✗ Failed' if all_passed else '✓ Passed'}"]

    def _get_seed_status(self, seed_result: dict[str, Any]) -> str:
        """Get status symbol for a seed result."""
        score = 0.0
        if "evaluation" in seed_result and isinstance(seed_result["evaluation"], dict):
            score = seed_result["evaluation"].get("final_score", 0.0)
        elif "score" in seed_result:
            score = seed_result.get("score", 0.0)
        # Usamos tolerancia (1e-9) en lugar de == porque los números flotantes pueden tener errores de precisión
        TOLERANCE = 1e-9
        return "✓" if abs(score - 1.0) < TOLERANCE else "✗"

    def _build_seed_details(self, seeds_tested: list[int], results_by_seed: dict[str, dict[str, Any]]) -> list[str]:
        """Build seed details list from seeds_tested."""
        seed_details = []
        for seed in seeds_tested:
            seed_result = results_by_seed.get(str(seed), {})
            status = self._get_seed_status(seed_result)
            seed_details.append(f"{seed}: {status}")
        return seed_details

    def _build_seed_details_from_results(self, results_by_seed: dict[str, dict[str, Any]]) -> list[str]:
        """Build seed details list from results_by_seed keys."""
        seed_details = []
        for seed_str, seed_result in results_by_seed.items():
            status = self._get_seed_status(seed_result)
            seed_details.append(f"{seed_str}: {status}")
        return seed_details

    def _get_final_conclusion_summary(self, categories: dict[str, list[str]]) -> list[str]:
        """Get final conclusion summary lines."""
        summary_lines = []
        summary_lines.append(f"\n{'=' * 60}")
        summary_lines.append("📊 FINAL CONCLUSION")
        summary_lines.append(f"{'=' * 60}")

        summary_lines.append("\n✅ Task Generation Quality:")
        if categories["generation_ok"]:
            summary_lines.append(f"  ✓ Good generation ({len(categories['generation_ok'])}): {', '.join(categories['generation_ok'])}")
        if categories["generation_failed"]:
            summary_lines.append(f"  ✗ Failed generation ({len(categories['generation_failed'])}): {', '.join(categories['generation_failed'])}")

        summary_lines.append("\n📊 Dataset Diversity (V2):")
        if categories["dataset_diverse"]:
            summary_lines.append(f"  ✓ Datasets are diverse - different data with different seeds ({len(categories['dataset_diverse'])}): {', '.join(categories['dataset_diverse'])}")
        if categories["dataset_not_diverse"]:
            summary_lines.append(f"  ✗ Datasets NOT diverse - same data with different seeds ({len(categories['dataset_not_diverse'])}): {', '.join(categories['dataset_not_diverse'])}")
        if categories["dataset_untested"]:
            summary_lines.append(f"  ⏭️  Dataset diversity not tested ({len(categories['dataset_untested'])}): {', '.join(categories['dataset_untested'])}")

        summary_lines.append("\n🔍 Solution Availability (IWAP):")
        if categories["has_solution"]:
            summary_lines.append(f"  ✓ Has solutions ({len(categories['has_solution'])}): {', '.join(categories['has_solution'])}")
        if categories["no_solution"]:
            summary_lines.append(f"  ✗ No solutions found ({len(categories['no_solution'])}): {', '.join(categories['no_solution'])}")

        summary_lines.append("\n🔄 Dynamic System Effectiveness:")
        if categories["truly_dynamic"]:
            summary_lines.append(f"  ✓ Truly dynamic - solution fails with different seeds ({len(categories['truly_dynamic'])}): {', '.join(categories['truly_dynamic'])}")
        if categories["not_dynamic"]:
            summary_lines.append(f"  ⚠️  Not truly dynamic - same solution works for all seeds ({len(categories['not_dynamic'])}): {', '.join(categories['not_dynamic'])}")
        if categories["dynamic_partial"]:
            summary_lines.append(f"  ⚠️  Partially dynamic - solution works for some seeds ({len(categories['dynamic_partial'])}): {', '.join(categories['dynamic_partial'])}")
        if categories["dynamic_untested"]:
            summary_lines.append(f"  ⏭️  Dynamic not tested ({len(categories['dynamic_untested'])}): {', '.join(categories['dynamic_untested'])}")

        summary_lines.append("\n📈 Overall Status:")
        total_use_cases = len(self.results["use_cases"])
        summary_lines.append(f"  Total Use Cases: {total_use_cases}")
        summary_lines.append(f"  - Good generation: {len(categories['generation_ok'])}/{total_use_cases}")
        summary_lines.append(f"  - Dataset diverse (V2): {len(categories['dataset_diverse'])}/{total_use_cases}")
        summary_lines.append(f"  - Has solutions: {len(categories['has_solution'])}/{total_use_cases}")
        summary_lines.append(f"  - Truly dynamic (V3): {len(categories['truly_dynamic'])}/{total_use_cases}")
        summary_lines.append(f"  - Needs review (not dynamic): {len(categories['not_dynamic'])}/{total_use_cases}")

        summary_lines.append(f"\n{'=' * 60}\n")
        return summary_lines

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
            self._categorize_task_generation(use_case_name, use_case_data, categories)
            self._categorize_dataset_diversity(use_case_name, use_case_data, categories)
            self._categorize_solution_availability(use_case_name, use_case_data, categories)
            self._categorize_dynamic_effectiveness(use_case_name, use_case_data, categories)

        return categories

    def _categorize_task_generation(self, use_case_name: str, use_case_data: dict[str, Any], categories: dict[str, list[str]]) -> None:
        """Categorize task generation quality for a use case."""
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

    def _categorize_dataset_diversity(self, use_case_name: str, use_case_data: dict[str, Any], categories: dict[str, list[str]]) -> None:
        """Categorize dataset diversity for a use case."""
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

    def _categorize_solution_availability(self, use_case_name: str, use_case_data: dict[str, Any], categories: dict[str, list[str]]) -> None:
        """Categorize solution availability for a use case."""
        iwap_status = use_case_data.get("iwap_status", {})
        if iwap_status.get("matched", False) or (iwap_status.get("executed", False) and iwap_status.get("matched") is not False):
            if iwap_status.get("matched", False):
                categories["has_solution"].append(use_case_name)
            else:
                categories["no_solution"].append(use_case_name)
        else:
            categories["no_solution"].append(use_case_name)

    def _categorize_dynamic_effectiveness(self, use_case_name: str, use_case_data: dict[str, Any], categories: dict[str, list[str]]) -> None:
        """Categorize dynamic system effectiveness for a use case."""
        dynamic_verification = use_case_data.get("dynamic_verification", {})
        if dynamic_verification and not dynamic_verification.get("skipped", False):
            passed_count = dynamic_verification.get("passed_count", 0)
            total_count = dynamic_verification.get("total_count", 0)
            needs_review = dynamic_verification.get("needs_review", False)

            if needs_review and passed_count == total_count and total_count >= 3:
                categories["not_dynamic"].append(use_case_name)
            elif passed_count == 0 and total_count > 0:
                categories["truly_dynamic"].append(use_case_name)
            elif 0 < passed_count < total_count:
                categories["dynamic_partial"].append(use_case_name)
            else:
                categories["dynamic_untested"].append(use_case_name)
        else:
            categories["dynamic_untested"].append(use_case_name)

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

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
