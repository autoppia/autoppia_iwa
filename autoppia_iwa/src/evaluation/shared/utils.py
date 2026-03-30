# evaluation_helper.py
import asyncio
import base64
import copy
import hashlib
import io
from collections import defaultdict

from loguru import logger

# Avoid importing Pillow at module import time; import lazily in functions that need it.
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import BackendEvent, WebProject
from autoppia_iwa.src.demo_webs.data_provider import get_seed_from_url
from autoppia_iwa.src.demo_webs.projects.p01_autocinema.data_utils import fetch_data as fetch_movies_data
from autoppia_iwa.src.demo_webs.projects.p02_autobooks.data_utils import fetch_data as fetch_books_data
from autoppia_iwa.src.evaluation.classes import EvaluationStats, Feedback, TestResult
from autoppia_iwa.src.evaluation.shared.feedback_generator import FeedbackGenerator
from autoppia_iwa.src.evaluation.shared.test_runner import TestRunner
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult

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
    logger.info(f"Score: {stats.final_score:.2f} (Raw: {stats.raw_score:.2f})")
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
async def run_global_tests(task: Task, backend_events: list[BackendEvent], web_agent_id: str | None = None) -> list[TestResult]:
    """
    Runs all task tests once after all actions are executed.

    Args:
        task (Task): The task being evaluated (contains the list of tests).
        backend_events (List[BackendEvent]): Backend events captured during execution.
        web_agent_id (str): The web agent ID being evaluated.

    Returns:
        List[TestResult]: A list of test results (one per test).
    """
    tests_for_run = await _resolve_autobooks_book_placeholders_in_tests(task, web_agent_id)
    tests_for_run = await _resolve_autocinema_film_placeholders_in_tests(task, tests_for_run, web_agent_id)
    test_runner = TestRunner(tests_for_run)
    test_results = await test_runner.run_global_tests(
        backend_events=backend_events,
        web_agent_id=web_agent_id,
    )
    return test_results


def _get_deterministic_user_index(username: str) -> int:
    """Mirror web_2_autobooks username -> index logic."""
    import re

    match = re.match(r"^user(\d+)$", username.strip(), flags=re.IGNORECASE)
    if match:
        parsed = int(match.group(1))
        if parsed > 0:
            return parsed - 1
    return sum(ord(ch) for ch in username)


def _resolve_assigned_book_for_agent(books: list[dict], web_agent_id: str) -> dict | None:
    """Mirror web_2_autobooks seed-dependent assignment from current list."""
    if not books:
        return None
    username = f"user{web_agent_id}"
    user_index = _get_deterministic_user_index(username)
    book_index = ((user_index % len(books)) + len(books)) % len(books)
    return books[book_index] if 0 <= book_index < len(books) else None


def _replace_placeholders_in_criteria(
    value,
    assigned_book_name: str,
    assigned_book_id: str,
    assigned_book_author: str,
):
    """Recursively replace assigned-book placeholders in criteria values."""
    if isinstance(value, str):
        return (
            value.replace("<assigned_book_name>", assigned_book_name)
            .replace("<assigned_book_id>", assigned_book_id)
            .replace("<assigned_book_author>", assigned_book_author)
            .replace("<book_name>", assigned_book_name)
            .replace("<book_id>", assigned_book_id)
            .replace("<book_author>", assigned_book_author)
        )
    if isinstance(value, list):
        return [
            _replace_placeholders_in_criteria(
                v,
                assigned_book_name,
                assigned_book_id,
                assigned_book_author,
            )
            for v in value
        ]
    if isinstance(value, dict):
        return {
            k: _replace_placeholders_in_criteria(
                v,
                assigned_book_name,
                assigned_book_id,
                assigned_book_author,
            )
            for k, v in value.items()
        }
    return value


async def _resolve_autobooks_book_placeholders_in_tests(task: Task, web_agent_id: str | None):
    """
    Clone tests and resolve assigned-book placeholders for autobooks DELETE_BOOK/EDIT_BOOK checks.
    """
    cloned_tests = copy.deepcopy(task.tests)
    if not web_agent_id:
        return cloned_tests
    if getattr(task, "web_project_id", None) != "autobooks":
        return cloned_tests
    target_tests = [test for test in cloned_tests if isinstance(test, CheckEventTest) and getattr(test, "event_name", "") in {"DELETE_BOOK", "EDIT_BOOK"}]
    if not target_tests:
        return cloned_tests

    seed = get_seed_from_url(task.url)
    books = await fetch_books_data(seed_value=seed, count=50)
    if not books:
        return cloned_tests

    assigned_book = _resolve_assigned_book_for_agent(books, web_agent_id)
    if not assigned_book:
        return cloned_tests

    assigned_book_name = str(assigned_book.get("name", ""))
    assigned_book_id = str(assigned_book.get("id", ""))
    assigned_book_author = str(assigned_book.get("author", assigned_book.get("director", "")))
    if not assigned_book_name and not assigned_book_id:
        return cloned_tests

    for test in target_tests:
        test.event_criteria = _replace_placeholders_in_criteria(
            test.event_criteria,
            assigned_book_name,
            assigned_book_id,
            assigned_book_author,
        )

    return cloned_tests


def _resolve_assigned_movie_for_agent(movies: list[dict], web_agent_id: str) -> dict | None:
    """Mirror web_1_autocinema seed-dependent assignment from current list."""
    if not movies:
        return None
    username = f"user{web_agent_id}"
    user_index = _get_deterministic_user_index(username)
    movie_index = ((user_index % len(movies)) + len(movies)) % len(movies)
    return movies[movie_index] if 0 <= movie_index < len(movies) else None


def _replace_film_placeholders_in_criteria(
    value,
    assigned_film_name: str,
    assigned_film_id: str,
    assigned_film_director: str,
):
    """Recursively replace assigned-film placeholders in criteria values."""
    if isinstance(value, str):
        return (
            value.replace("<assigned_film_name>", assigned_film_name)
            .replace("<assigned_film_id>", assigned_film_id)
            .replace("<assigned_film_director>", assigned_film_director)
            .replace("<film_name>", assigned_film_name)
            .replace("<film_id>", assigned_film_id)
            .replace("<film_director>", assigned_film_director)
        )
    if isinstance(value, list):
        return [
            _replace_film_placeholders_in_criteria(
                v,
                assigned_film_name,
                assigned_film_id,
                assigned_film_director,
            )
            for v in value
        ]
    if isinstance(value, dict):
        return {
            k: _replace_film_placeholders_in_criteria(
                v,
                assigned_film_name,
                assigned_film_id,
                assigned_film_director,
            )
            for k, v in value.items()
        }
    return value


async def _resolve_autocinema_film_placeholders_in_tests(task: Task, tests_for_run, web_agent_id: str | None):
    """
    Resolve assigned-film placeholders for autocinema DELETE_FILM/EDIT_FILM checks.
    """
    if not web_agent_id:
        return tests_for_run
    if getattr(task, "web_project_id", None) != "autocinema":
        return tests_for_run
    target_tests = [test for test in tests_for_run if isinstance(test, CheckEventTest) and getattr(test, "event_name", "") in {"DELETE_FILM", "EDIT_FILM"}]
    if not target_tests:
        return tests_for_run

    seed = get_seed_from_url(task.url)
    movies = await fetch_movies_data(seed_value=seed, count=50)
    if not movies:
        return tests_for_run

    assigned_movie = _resolve_assigned_movie_for_agent(movies, web_agent_id)
    if not assigned_movie:
        return tests_for_run

    assigned_film_name = str(assigned_movie.get("name", assigned_movie.get("title", "")))
    assigned_film_id_in_str = str(assigned_movie.get("id", ""))
    assigned_film_id = str(int(assigned_film_id_in_str.rsplit("-", 1)[-1]))

    assigned_film_director = str(assigned_movie.get("director", ""))
    if not assigned_film_name and not assigned_film_id:
        return tests_for_run

    for test in target_tests:
        test.event_criteria = _replace_film_placeholders_in_criteria(
            test.event_criteria,
            assigned_film_name,
            assigned_film_id,
            assigned_film_director,
        )

    return tests_for_run


async def run_partial_tests(web_project: WebProject, task: Task, execution_history: list[ActionExecutionResult]) -> list[list[TestResult]]:
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
        test_results = await test_runner.run_partial_tests(
            web_project=web_project,
            prompt=task.prompt,
            snapshot=snapshot,
            browser_snapshots=browser_snapshots,
            current_action_index=i,
            total_iterations=total_iterations,
        )
        test_results_matrix.append(test_results)

    return test_results_matrix


def generate_feedback(task: Task, execution_history: list[ActionExecutionResult], test_results: list[TestResult]) -> Feedback:
    """
    Generates feedback based on the given test results.

    Args:
        task (Task): The task being evaluated (contains the prompt or description).
        execution_history (List[ActionExecutionResult]): History of executed actions.
        test_results (List[TestResult]): The list of test results.

    Returns:
        Feedback: The generated feedback for this task solution.
    """
    return FeedbackGenerator.generate_feedback(task_prompt=task.prompt, execution_history=execution_history, test_results=test_results)


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
    while True:
        await asyncio.sleep(interval)
        completed = sum(1 for t in asyncio.all_tasks() if t.done() and "evaluate_group_with_semaphore" in str(t))
        logger.info(f"Progress: {completed}/{total_groups} groups ({completed / total_groups * 100:.0f}%)")


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


def initialize_test_results(task: Task):
    """
    Initialize test results list with all tests marked as failed.
    Used when an error occurs before tests can be run.

    Args:
        task (Task): The Task object containing tests

    Returns:
        List[TestResult]: A list of test results initialized with success=False
    """
    test_results = []
    for test in task.tests:
        # Build a TestResult with success=False; copy any extra info from the test if needed
        extra_data = {key: value for key, value in test.model_dump().items() if key not in {"description", "test_type"}}
        test_results.append(TestResult(success=False, extra_data=extra_data))
    return test_results


def make_gif_from_screenshots(all_base64_strings, duration_ms=500, loop_count=0):
    """
    Creates an animated GIF from a list of base64 encoded image strings.

    Args:
        all_base64_strings: A list of strings, where each string is a
                            base64-encoded representation of an image.
        duration_ms: The display duration for each frame in the GIF,
                     in milliseconds.
        loop_count: The number of times the GIF should loop.
                    Set to 0 for infinite looping. Defaults to 0.

    Returns:
        str: The base64 encoded content of the generated GIF image. Returns empty bytes (b"") if an error occurs
               or no images are processed.
    """
    # Local import to avoid hard dependency when GIF generation is unused
    from PIL import Image, UnidentifiedImageError  # type: ignore

    pil_images: list = []

    if not all_base64_strings:
        return b""

    for idx, b64_string in enumerate(all_base64_strings):
        try:
            if not isinstance(b64_string, str):
                logger.warning(f"Item at index {idx} is not a string (type: {type(b64_string)}). Skipping.")
                continue

            # Decode the base64 string. It must be ASCII bytes for b64decode.
            image_data_bytes = base64.b64decode(b64_string.encode("ascii"))

            # Create a PIL Image object from the image bytes
            image_file_like = io.BytesIO(image_data_bytes)
            img = Image.open(image_file_like)

            # Ensure the image is in a mode compatible with GIF.
            # Converting to RGBA handles various input modes and alpha transparency.
            # Pillow will convert RGBA to P (palette) mode when saving as GIF.
            # L: Luminance (grayscale), P: Palette, RGB: Truecolor
            if img.mode not in ("L", "P", "RGB"):
                logger.debug(f"Converting image {idx} from mode {img.mode} to RGBA for GIF compatibility.")
                img = img.convert("RGBA")
            elif img.mode == "P" and "transparency" in img.info:
                # If it's already a palette image with transparency, ensure it's handled correctly.
                # Often, converting to RGBA and letting PIL re-palette for GIF is more robust.
                logger.debug(f"Image {idx} is in Palette mode with transparency. Converting to RGBA to preserve alpha.")
                img = img.convert("RGBA")

            pil_images.append(img)

        except UnicodeEncodeError:
            logger.warning(f"Base64 string at index {idx} contains non-ASCII characters and could not be encoded. Skipping.")
            continue
        # ValueError for incorrect padding etc.
        except (base64.binascii.Error, ValueError) as e_b64:
            logger.warning(f"Could not decode base64 string at index {idx}: {e_b64}. Skipping.")
            continue
        except UnidentifiedImageError:
            logger.warning(f"Pillow could not identify image format from base64 string at index {idx}. Skipping.")
            continue
        except OSError as e_pil:
            logger.warning(f"Pillow I/O error for image from base64 string at index {idx}: {e_pil}. Skipping.")
            continue
        except Exception as e_general:
            logger.error(f"Unexpected error processing base64 string at index {idx}: {e_general}.", exc_info=True)
            continue

    if not pil_images:
        return b""
    gif_buffer = io.BytesIO()
    try:
        pil_images[0].save(
            gif_buffer,
            format="GIF",
            save_all=True,  # Important: save all frames
            append_images=pil_images[1:],  # Append the rest of the images
            duration=duration_ms,  # Time per frame in milliseconds
            loop=loop_count,  # 0 for infinite loop
            optimize=True,  # Optimize for smaller file size (ENABLED to avoid 413 errors)
            # 2: Graphic is to be restored to background color before rendering next frame.
            disposal=1,
            # Use 1 if frames should not be disposed (e.g., drawn on top of each other).
        )
        raw_gif_bytes = gif_buffer.getvalue()
    except Exception as e_gif:
        logger.error(f"❌ GIF CREATION ERROR: {e_gif}", exc_info=True)
        return b""
    finally:
        for img_obj in pil_images:
            img_obj.close()
        if not gif_buffer.closed:
            gif_buffer.close()

    encoded_gif = base64.b64encode(raw_gif_bytes)
    return encoded_gif


def extract_seed_from_url(url: str) -> int | None:
    """Extract seed parameter from URL query string."""
    from urllib.parse import parse_qs, urlparse

    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if query.get("seed"):
            value = int(str(query["seed"][0]).strip())
            return value
    except Exception:
        return None
    return None
