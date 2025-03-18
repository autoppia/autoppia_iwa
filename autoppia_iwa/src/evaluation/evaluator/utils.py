# evaluation_helper.py
import asyncio
import hashlib
from collections import defaultdict

from loguru import logger
from playwright.async_api import Page

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationStats, EvaluatorConfig, Feedback, TestResult
from autoppia_iwa.src.evaluation.evaluator.feedback_generator import FeedbackGenerator
from autoppia_iwa.src.evaluation.evaluator.test_runner import TestRunner
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

# ---------------------------------------------------------------------------------
# DISPLAY/REPORTING HELPERS
# ---------------------------------------------------------------------------------


def display_single_evaluation_summary(stats: EvaluationStats, debug_mode: bool = False):
    """
    Displays a concise summary of a single evaluation (for a single agent's solution).

    Args:
        stats (EvaluationStats): The statistics object containing all evaluation details.
        debug_mode (bool): If True, we skip or reduce verbosity.
    """
    _ = stats.get_summary_dict()  # Ensure internal stats are calculated

    if debug_mode:
        return  # Skip printing in debug mode

    logger.info(f"\n{'-' * 60}")
    logger.info(f"Evaluation Results for Agent: {stats.web_agent_id}")
    logger.info(f"{'-' * 60}")
    logger.info(f"Task: {stats.task_id}")
    logger.info(f"Score: {stats.final_score:.2f} (Raw: {stats.raw_score:.2f}, Random: {stats.random_clicker_score:.2f})")
    logger.info(f"Tests Passed: {stats.tests_passed}/{stats.total_tests}")
    logger.info(f"Actions: {stats.action_count} ({', '.join(f'{k}: {v}' for k, v in stats.action_types.items())})")
    logger.info(f"{'-' * 40}")

    total_time = stats.total_time
    setup_pct = (stats.browser_setup_time / total_time * 100) if total_time else 0
    action_time = sum(stats.action_execution_times) if stats.action_execution_times else 0
    action_pct = (action_time / total_time * 100) if total_time else 0
    random_pct = (stats.random_clicker_time / total_time * 100) if total_time else 0
    test_pct = (stats.test_execution_time / total_time * 100) if total_time else 0

    logger.info(f"Time: {stats.total_time:.2f}s total")
    logger.info(f" - Browser Setup: {stats.browser_setup_time:.2f}s ({setup_pct:.1f}%)")
    logger.info(f" - Actions Execution: {action_time:.2f}s ({action_pct:.1f}%)")
    logger.info(f" - Test Execution: {stats.test_execution_time:.2f}s ({test_pct:.1f}%)")
    logger.info(f" - Random Evaluation: {stats.random_clicker_time:.2f}s ({random_pct:.1f}%)")

    if stats.action_execution_times:
        avg_time = sum(stats.action_execution_times) / len(stats.action_execution_times)
        max_time = max(stats.action_execution_times)
        logger.info(f"Action Time: {avg_time:.3f}s avg, {max_time:.3f}s max")

    if stats.had_errors:
        logger.error(f"Errors: {stats.error_message}")

    logger.info(f"{'-' * 60}")


def display_batch_evaluation_summary(
    task_id: str,
    evaluation_stats: list[EvaluationStats],
    debug_mode: bool,
    action_type_timing: dict[str, list[float]],
    errors: list[str],
):
    """
    Displays a concise summary of all evaluations for a single task (batch of solutions).

    Args:
        task_id (str): The ID of the task being evaluated.
        evaluation_stats (List[EvaluationStats]): A list of all evaluation statistics.
        debug_mode (bool): If True, skip or reduce verbosity.
        action_type_timing (Dict[str, List[float]]): Maps action types to recorded execution times.
        errors (List[str]): A list of errors encountered during evaluations.
    """
    if debug_mode or not evaluation_stats:
        return  # Skip if debug mode is enabled or there are no stats

    # Filter stats for the given task
    task_stats = [s for s in evaluation_stats if s.task_id == task_id]
    if not task_stats:
        return

    total_agents = len(task_stats)
    successful_agents = sum(1 for s in task_stats if not s.had_errors)
    avg_score = sum(s.final_score for s in task_stats) / max(1, total_agents)
    avg_time = sum(s.total_time for s in task_stats) / max(1, total_agents)

    # Group by agent "type" (prefix before '-') or by entire agent_id if no dash
    agent_groups = defaultdict(list)
    for stat in task_stats:
        agent_id = stat.web_agent_id
        agent_type = agent_id.split("-")[0] if "-" in agent_id else agent_id
        agent_groups[agent_type].append(stat)

    logger.info(f"\n{'=' * 80}")
    logger.info(f"EVALUATION SUMMARY FOR TASK: {task_id}")
    logger.info(f"{'=' * 80}")
    logger.info(f"Total Agents: {total_agents}, Success Rate: {successful_agents}/{total_agents} ({successful_agents / total_agents * 100:.1f}%)")
    logger.info(f"Average Score: {avg_score:.4f}, Average Time: {avg_time:.2f}s")

    # Per-agent-type summaries
    for agent_type, stats_list in agent_groups.items():
        avg_group_score = sum(s.final_score for s in stats_list) / max(1, len(stats_list))
        avg_group_time = sum(s.total_time for s in stats_list) / max(1, len(stats_list))

        logger.info(f"\n{'-' * 60}")
        logger.info(f"Web Agent ID: {agent_type} ({len(stats_list)} solutions)")
        logger.info(f"Average Score: {avg_group_score:.4f}, Average Time: {avg_group_time:.2f}s")

        # Collect all action execution times in this agent_type group
        all_action_times = []
        for s in stats_list:
            all_action_times.extend(s.action_execution_times)

        if all_action_times:
            avg_action_time = sum(all_action_times) / len(all_action_times)
            max_action_time = max(all_action_times)
            logger.info(f"Actions: {sum(s.action_count for s in stats_list)}, Avg Time: {avg_action_time:.3f}s, Max: {max_action_time:.3f}s")

        # Test results
        total_tests = stats_list[0].total_tests if stats_list else 0
        if total_tests > 0:
            tests_passed = [s.tests_passed for s in stats_list]
            avg_passed = sum(tests_passed) / len(tests_passed)
            logger.info(f"Tests Passed: {avg_passed:.1f}/{total_tests} on average")

    # Overall timing breakdown
    all_browser_setup = sum(s.browser_setup_time for s in task_stats)
    all_action_time = sum(sum(s.action_execution_times) for s in task_stats)
    all_test_time = sum(s.test_execution_time for s in task_stats)
    all_random_time = sum(s.random_clicker_time for s in task_stats)
    all_total_time = sum(s.total_time for s in task_stats)

    logger.info(f"\n{'-' * 60}")
    logger.info("TIMING BREAKDOWN (across all agents)")
    logger.info(f"Total Evaluation Time: {all_total_time:.2f}s")
    if all_total_time > 0:
        logger.info(f"Browser Setup: {all_browser_setup:.2f}s ({all_browser_setup / all_total_time * 100:.1f}%)")
        logger.info(f"Action Execution: {all_action_time:.2f}s ({all_action_time / all_total_time * 100:.1f}%)")
        logger.info(f"Test Execution: {all_test_time:.2f}s ({all_test_time / all_total_time * 100:.1f}%)")
        logger.info(f"Random Evaluation: {all_random_time:.2f}s ({all_random_time / all_total_time * 100:.1f}%)")
    else:
        logger.info("Browser Setup: 0.00s (0.0%)")
        logger.info("Action Execution: 0.00s (0.0%)")
        logger.info("Test Execution: 0.00s (0.0%)")
        logger.info("Random Evaluation: 0.00s (0.0%)")

    # Action type performance
    if action_type_timing:
        logger.info(f"\n{'-' * 60}")
        logger.info("ACTION TYPE PERFORMANCE")
        for a_type, times in sorted(action_type_timing.items(), key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0, reverse=True):
            if times:
                avg_t = sum(times) / len(times)
                max_t = max(times)
                min_t = min(times)
                logger.info(f"{a_type}: {len(times)} actions, {avg_t:.3f}s avg ({min_t:.3f}s - {max_t:.3f}s)")

    # Display errors if any
    if errors:
        logger.info(f"\n{'-' * 60}")
        logger.info(f"ERRORS ({len(errors)})")
        for i, error in enumerate(errors[:5]):
            logger.info(f"{i + 1}. {error}")
        if len(errors) > 5:
            logger.info(f"... and {len(errors) - 5} more errors")

    logger.info(f"{'=' * 80}")


# ---------------------------------------------------------------------------------
# TEST / FEEDBACK HELPERS
# ---------------------------------------------------------------------------------


async def run_tests(web_project: WebProject, task: Task, execution_history: list[ActionExecutionResult]) -> list[list[TestResult]]:
    """
    Runs all task tests after each action, building a test results matrix.

    Args:
        web_project: The web project being tested.
        task (Task): The task being evaluated (contains the list of tests).
        execution_history (List[ActionExecutionResult]): History of all executed actions.

    Returns:
        List[List[TestResult]]: A matrix where each row corresponds to an action and
                                each column to a test, indicating pass/fail results.
    """
    test_runner = TestRunner(task.tests)
    total_iterations = len(execution_history)
    test_results_matrix: list[list[TestResult]] = []
    browser_snapshots = []
    for i, action_result in enumerate(execution_history):
        snapshot = action_result.browser_snapshot
        browser_snapshots.append(snapshot)

        # Run the test suite for the current action
        test_results = await test_runner.run_tests(
            web_project=web_project,
            prompt=task.prompt,
            snapshot=snapshot,
            browser_snapshots=browser_snapshots,
            current_action_index=i,
            total_iterations=total_iterations,
        )
        test_results_matrix.append(test_results)

    return test_results_matrix


def generate_feedback(task: Task, execution_history: list[ActionExecutionResult], test_results_matrix: list[list[TestResult]]) -> Feedback:
    """
    Generates feedback based on the given test results.

    Args:
        task (Task): The task being evaluated (contains the prompt or description).
        execution_history (List[ActionExecutionResult]): History of executed actions.
        test_results_matrix (List[List[TestResult]]): The matrix of pass/fail test results.

    Returns:
        Feedback: The generated feedback for this task solution.
    """
    return FeedbackGenerator.generate_feedback(task_prompt=task.prompt, execution_history=execution_history, test_results_matrix=test_results_matrix)


# ---------------------------------------------------------------------------------
# ASYNC HELPERS
# ---------------------------------------------------------------------------------


async def log_progress(total_groups: int, interval: int = 10):
    """
    Periodically logs minimal progress updates for large batch evaluations.

    Args:
        total_groups (int): The total number of groups to evaluate.
        interval (int): How often (in seconds) to log progress.
    """
    try:
        while True:
            await asyncio.sleep(interval)
            completed = sum(1 for t in asyncio.all_tasks() if t.done() and "evaluate_group_with_semaphore" in str(t))
            logger.info(f"Progress: {completed}/{total_groups} groups ({completed / total_groups * 100:.0f}%)")
    except asyncio.CancelledError:
        pass


async def monitor_browser(web_project: WebProject, task_url: str, page: Page, web_agent_id: str, monitor_interval: float = 1.0):
    """
    Monitors browser navigation events and sends them to the backend.

    Args:
        web_project (WebProject): The web project being evaluated
        task_url (str): URL of the task
        page (Page): Playwright page object
        web_agent_id (str): ID of the web agent
        monitor_interval (float): Interval in seconds to check page status
    """

    # def on_frame_navigated(frame):
    #     if frame.url:
    #         asyncio.create_task(_handle_frame_navigation(web_project, frame.url, task_url, web_agent_id))

    # async def _handle_frame_navigation(web_project, url, task_url, web_agent_id):
    #     try:
    #         backend_demo_web_service = BackendDemoWebService(web_project)
    #         # await backend_demo_web_service.send_event(url, web_agent_id)
    #         await backend_demo_web_service.close()
    #     except Exception as e:
    #         logger.error(f"Error handling frame navigation: {e}")

    # page.on("framenavigated", on_frame_navigated)
    try:
        while not page.is_closed():
            await asyncio.sleep(monitor_interval)
    except asyncio.CancelledError:
        pass


async def get_random_clicker_performance(
    web_project: WebProject,
    task: Task,
    config: EvaluatorConfig,
    random_clicker_cache: dict[str, tuple[list[int], float]],
    backend_demo_webs_service: BackendDemoWebService,
    evaluate_in_browser_func,
) -> tuple[list[int], float]:
    """
    Returns the random clicker baseline performance (passing test indices, and score),
    either from cache or by computing it.

    Args:
        task (Task): The task to evaluate.
        config (EvaluatorConfig): Global evaluator configuration (caching, timeouts, etc.).
        random_clicker_cache (Dict[str, Tuple[List[int], float]]): A cache dict to avoid re-evaluating.
        backend_demo_webs_service (BackendDemoWebService): Service to reset backend DB for simulated tasks.
        evaluate_in_browser_func (callable): A function to execute actions in the browser,
                                             with signature: (task, web_agent_id, actions, is_web_real).

    Returns:
        Tuple[List[int], float]: A tuple of (list of passed test indices, random clicker score).
    """
    # Check cache first
    if config.cache_random_clicker_results and task.id in random_clicker_cache:
        if config.verbose_logging:
            logger.debug(f"Using cached random clicker results for task {task.id}")
        return random_clicker_cache[task.id]

    # Build a random clicker solution
    random_clicker = RandomClickerWebAgent(name="Random-clicker")
    task_solution = await random_clicker.solve_task(task=task)
    random_actions = task_solution.actions

    if not random_actions:
        return [], 0.0

    random_web_agent_id = f"random-clicker-{task.id}"

    # Reset backend if needed
    # if not task.is_web_real:
    #     await backend_demo_webs_service.reset_all_events(random_web_agent_id)

    # Execute random clicker actions in browser
    random_execution_history, _ = await evaluate_in_browser_func(task, random_web_agent_id, random_actions, task.is_web_real)

    # Run tests
    random_test_results = await run_tests(web_project, task, random_execution_history)

    passed_tests: list[int] = []
    random_score = 0.0
    if random_test_results and len(random_test_results[0]) > 0:
        num_tests = len(random_test_results[0])
        passed_count = 0
        for test_index in range(num_tests):
            for action_idx in range(len(random_test_results)):
                if random_test_results[action_idx][test_index].success:
                    passed_tests.append(test_index)
                    passed_count += 1
                    break
        if num_tests > 0:
            random_score = passed_count / num_tests

    # Cache if needed
    if config.cache_random_clicker_results:
        random_clicker_cache[task.id] = (passed_tests, random_score)

    return passed_tests, random_score


def hash_actions(actions: list[BaseAction]) -> str:
    """
    Hash a list of actions so we can identify identical solutions by comparing their hash.

    Args:
        actions (List[BaseAction]): The list of actions to hash

    Returns:
        str: A hash string representing the actions
    """
    try:
        action_repr = "|".join(str(a.model_dump()) for a in actions)
        return hashlib.sha256(action_repr.encode()).hexdigest()
    except Exception:
        logger.error("Error generating hash for actions.")
        return ""


def initialize_test_results_matrix(task: Task, num_actions: int):
    """
    Initialize a test results matrix based on the number of tests in the task and actions.
    All test results are initialized with success=False.

    Args:
        task (Task): The Task object containing tests
        num_actions (int): Number of actions

    Returns:
        List[List[TestResult]]: A matrix of test results
    """
    # Determine the number of rows in the matrix
    num_rows = num_actions if num_actions else 1

    test_results_matrix = []
    for _ in range(num_rows):
        row = []
        for test in task.tests:
            # Build a TestResult with success=False; copy any extra info from the test if needed
            extra_data = {key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}}
            row.append(TestResult(success=False, extra_data=extra_data))
        test_results_matrix.append(row)

    return test_results_matrix
