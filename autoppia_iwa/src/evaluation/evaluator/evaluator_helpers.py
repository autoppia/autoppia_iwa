# evaluation_helper.py
from collections import defaultdict
from typing import List, Dict
from loguru import logger

from autoppia_iwa.src.evaluation.classes import EvaluationStats, Feedback, TestResult
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.evaluation.evaluator.test_runner import TestRunner
from autoppia_iwa.src.evaluation.evaluator.feedback_generator import FeedbackGenerator
from autoppia_iwa.src.data_generation.domain.classes import Task


def display_single_evaluation_summary(stats: EvaluationStats, debug_mode: bool = False):
    """
    Displays a concise summary of a single evaluation (for a single agent's solution).

    Args:
        stats (EvaluationStats): The statistics object containing all evaluation details.
        debug_mode (bool): If True, we skip or reduce verbosity.
    """
    # Force stats to compute internal values if needed
    _ = stats.get_summary_dict()

    if debug_mode:
        return  # Skip printing in debug mode

    logger.info(f"\n{'-' * 60}")
    logger.info(f"Evaluation Results for Agent: {stats.web_agent_id}")
    logger.info(f"{'-' * 60}")
    logger.info(f"Task: {stats.task_id}")
    logger.info(
        f"Score: {stats.final_score:.2f} "
        f"(Raw: {stats.raw_score:.2f}, Random: {stats.random_clicker_score:.2f})"
    )
    logger.info(f"Tests Passed: {stats.tests_passed}/{stats.total_tests}")
    logger.info(
        f"Actions: {stats.action_count} "
        f"({', '.join(f'{k}: {v}' for k, v in stats.action_types.items())})"
    )
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
    evaluation_stats: List[EvaluationStats],
    debug_mode: bool,
    action_type_timing: Dict[str, List[float]],
    errors: List[str],
):
    """
    Displays a concise summary of all evaluations for a single task (batch of solutions).

    Args:
        task_id (str): The ID of the task being evaluated.
        evaluation_stats (List[EvaluationStats]): A list of all evaluation statistics.
        debug_mode (bool): If True, skip or reduce verbosity.
        action_type_timing (Dict[str, List[float]]): Maps action types to their recorded execution times.
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

    # Group by agent "type" (prefix before a dash) or by agent_id if no dash
    agent_groups = defaultdict(list)
    for stat in task_stats:
        agent_id = stat.web_agent_id
        agent_type = agent_id.split('-')[0] if '-' in agent_id else agent_id
        agent_groups[agent_type].append(stat)

    logger.info(f"\n{'=' * 80}")
    logger.info(f"EVALUATION SUMMARY FOR TASK: {task_id}")
    logger.info(f"{'=' * 80}")
    logger.info(
        f"Total Agents: {total_agents}, "
        f"Success Rate: {successful_agents}/{total_agents} "
        f"({successful_agents / total_agents * 100:.1f}%)"
    )
    logger.info(f"Average Score: {avg_score:.4f}, Average Time: {avg_time:.2f}s")

    # Per-agent-type summaries
    for agent_type, stats_list in agent_groups.items():
        avg_group_score = sum(s.final_score for s in stats_list) / max(1, len(stats_list))
        avg_group_time = sum(s.total_time for s in stats_list) / max(1, len(stats_list))

        logger.info(f"\n{'-' * 60}")
        logger.info(f"Web Agent ID: {agent_type} ({len(stats_list)} solutions)")
        logger.info(f"Average Score: {avg_group_score:.4f}, Average Time: {avg_group_time:.2f}s")

        # Collect all action execution times within this agent_type group
        all_action_times = []
        for s in stats_list:
            all_action_times.extend(s.action_execution_times)

        if all_action_times:
            avg_action_time = sum(all_action_times) / len(all_action_times)
            max_action_time = max(all_action_times)
            logger.info(
                f"Actions: {sum(s.action_count for s in stats_list)}, "
                f"Avg Time: {avg_action_time:.3f}s, Max: {max_action_time:.3f}s"
            )

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
        for a_type, times in sorted(
            action_type_timing.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        ):
            if times:
                avg_t = sum(times) / len(times)
                max_t = max(times)
                min_t = min(times)
                logger.info(
                    f"{a_type}: {len(times)} actions, {avg_t:.3f}s avg "
                    f"({min_t:.3f}s - {max_t:.3f}s)"
                )

    # Display errors if any
    if errors:
        logger.info(f"\n{'-' * 60}")
        logger.info(f"ERRORS ({len(errors)})")
        for i, error in enumerate(errors[:5]):
            logger.info(f"{i+1}. {error}")
        if len(errors) > 5:
            logger.info(f"... and {len(errors) - 5} more errors")

    logger.info(f"{'=' * 80}")


def run_tests(task: Task, execution_history: List[ActionExecutionResult]) -> List[List[TestResult]]:
    """
    Runs all task tests after each action, building a test results matrix.

    Args:
        task (Task): The task being evaluated (contains the list of tests).
        execution_history (List[ActionExecutionResult]): History of all executed actions.

    Returns:
        List[List[TestResult]]: A matrix where each row corresponds to an action and
                                each column to a test, indicating pass/fail results.
    """
    test_runner = TestRunner(task.tests)
    test_results_matrix: List[List[TestResult]] = []

    # We'll store snapshots to allow context across actions
    browser_snapshots = []

    for i, action_result in enumerate(execution_history):
        snapshot = action_result.browser_snapshot
        browser_snapshots.append(snapshot)

        # Run the entire test suite for the current action
        test_results = test_runner.run_tests(
            prompt=task.prompt,
            snapshot=snapshot,
            browser_snapshots=browser_snapshots,
            current_action_index=i
        )
        test_results_matrix.append(test_results)

    return test_results_matrix


def generate_feedback(
    task: Task,
    execution_history: List[ActionExecutionResult],
    test_results_matrix: List[List[TestResult]]
) -> Feedback:
    """
    Generates feedback based on the given test results.

    Args:
        task (Task): The task being evaluated (contains the prompt or description).
        execution_history (List[ActionExecutionResult]): History of all executed actions.
        test_results_matrix (List[List[TestResult]]): The matrix of test results.

    Returns:
        Feedback: Generated feedback for this task solution.
    """
    return FeedbackGenerator.generate_feedback(
        task_prompt=task.prompt,
        execution_history=execution_history,
        test_results_matrix=test_results_matrix
    )
