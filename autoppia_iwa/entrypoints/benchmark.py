import asyncio
import base64
import json
import time
import traceback
from collections import defaultdict

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.shared.utils_entrypoints.benchmark_utils import BenchmarkConfig, setup_logging
from autoppia_iwa.src.shared.utils_entrypoints.metrics import TimingMetrics
from autoppia_iwa.src.shared.utils_entrypoints.results import plot_results, plot_task_comparison, print_performance_statistics, save_results_to_json
from autoppia_iwa.src.shared.utils_entrypoints.solutions import ConsolidatedSolutionCache
from autoppia_iwa.src.shared.utils_entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_list_of_evaluations, visualize_task
from autoppia_iwa.src.shared.web_voyager_utils import TaskData, load_real_tasks
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# ==========================
# ==== CONFIGURATIONS ====
# ==========================

# Manually select the demo projects
PROJECTS_TO_RUN: list[WebProject] = [
    demo_web_projects[0],
    demo_web_projects[1],
    demo_web_projects[2],
    # demo_web_projects[3],
]

# Number of times to run the benchmark for each project to get average scores
NUM_RUNS_CONST: int = 3

PROMPT_PER_USE_CASE_CONST: int = 1
PLOT_BENCHMARK_RESULTS: bool = False
SAVE_EVALUATION_RESULTS: bool = False
USE_CACHED_TASKS_CONST: bool = False
USE_CACHED_SOLUTIONS_CONST: bool = False
EVALUATE_REAL_TASKS_CONST: bool = False

RETURN_EVALUATION_GIF: bool = True
RECORDINGS_DIR = PROJECT_BASE_DIR / "recordings"
LOG_FILE = "benchmark.log"

# Ensure recordings directory exists
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging
setup_logging(LOG_FILE)

# Benchmark config
config = BenchmarkConfig(
    projects_to_run=PROJECTS_TO_RUN,
    prompt_per_use_case=PROMPT_PER_USE_CASE_CONST,
    use_cached_tasks=USE_CACHED_TASKS_CONST,
    use_cached_solutions=USE_CACHED_SOLUTIONS_CONST,
    evaluate_real_tasks=EVALUATE_REAL_TASKS_CONST,
)

solution_cache = ConsolidatedSolutionCache(str(config.solutions_cache_dir))

# Agents
AGENTS: list[IWebAgent] = [
    # ApifiedWebAgent(id="1", name="AnthropicBrowserUseAgent", host="127.0.0.1", port=5000, timeout=240),
    # ApifiedWebAgent(id="2", name="OpenAIBrowserUseAgent", host="127.0.0.1", port=5005, timeout=240),
    # ApifiedWebAgent(id="3", name="OpenAICUA", host="127.0.0.1", port=5020, timeout=400),
    # ApifiedWebAgent(id="4", name="AnthropicCUA", host="127.0.0.1", port=5010, timeout=240),
    ApifiedWebAgent(id="5", name="AutoppiaAgent", host="127.0.0.1", port=5000, timeout=120),
]

# Semaphore to cap concurrent agent calls at 3
SEM = asyncio.Semaphore(3)

visualizer = SubnetVisualizer()

# =========================================================
# TASK AND EVALUATION HELPERS
# =========================================================


@visualize_task(visualizer)
async def generate_tasks(demo_project: WebProject, tasks_data: TaskData | None = None) -> list[Task]:
    """Generate test tasks for a given demo project."""
    if config.evaluate_real_tasks and tasks_data:
        task = Task(url=tasks_data.web, prompt=tasks_data.ques, is_web_real=True)
        return await LocalTestGenerationPipeline(demo_project).add_tests_to_tasks([task])

    return await generate_tasks_for_project(
        demo_project,
        config.use_cached_tasks,
        str(config.tasks_cache_dir),
        prompts_per_use_case=config.prompt_per_use_case,
    )


@visualize_list_of_evaluations(visualizer)
async def evaluate_multiple_solutions(web_project, task, task_solutions, validator_id):
    try:
        evaluator = ConcurrentEvaluator(web_project=web_project, config=EvaluatorConfig(save_results_in_db=False, enable_grouping_tasks=False, chunk_size=20))
        evaluation_results = await evaluator.evaluate_task_solutions(task, task_solutions)

        # Save recordings if they exist
        if RETURN_EVALUATION_GIF:
            for result in evaluation_results:
                if result.gif_recording:
                    # Get agent name
                    web_agent_name = "unknown_agent"
                    for agent in AGENTS:
                        if agent.id == result.web_agent_id:
                            web_agent_name = agent.name
                            break

                    # Create directory structure
                    agent_dir = RECORDINGS_DIR / web_agent_name
                    os.makedirs(agent_dir, exist_ok=True)

                    # Save GIF
                    recording_path = agent_dir / f"{task.id}.gif"
                    with open(recording_path, "wb") as f:
                        f.write(base64.b64decode(result.gif_recording))
                    logger.info(f"Saved recording to: {recording_path}")

        return evaluation_results
    except Exception:
        traceback.print_exc()
        return []


async def generate_solution_for_task(demo_project: WebProject, agent: IWebAgent, task: Task, timing_metrics: TimingMetrics) -> TaskSolution | None:
    logger.info(f"---\nGenerating solution for Agent: {agent.name} | Task: {task.id} (Project: {demo_project.name})")
    backend_service = BackendDemoWebService(demo_project)

    try:
        await backend_service.reset_database()

        if config.use_cached_solutions:
            cached_solution = await solution_cache.load_solution(task.id, agent.id)
            if cached_solution and cached_solution.actions:
                logger.info(f"Loaded cached solution ({len(cached_solution.actions)} actions).")
                return cached_solution
            logger.warning(f"No cached solution found for {task.id}, generating a new one.")

        start_time = time.time()
        prepared_task = task.prepare_for_agent(agent.id)
        solution = await agent.solve_task(prepared_task)
        task_solution = TaskSolution(task_id=task.id, actions=solution.actions or [], web_agent_id=agent.id)
        timing_metrics.record_solution_time(agent.id, task.id, time.time() - start_time)

        logger.info(f"Generated solution with {len(task_solution.actions)} actions.")
        if solution_cache.save_solution(task_solution, agent.id, agent.name):
            logger.info("Solution cached successfully.")

        return task_solution
    except Exception as e:
        logger.error(f"Error generating solution for Task {task.id} on project {demo_project.name}: {e!r}")
        return None
    finally:
        await backend_service.close()


async def save_recordings(evaluation_results: list, task: Task, run_number: int):
    for result in evaluation_results:
        if result.gif_recording:
            web_agent_name = "unknown_agent"
            for agent in AGENTS:
                if agent.id == result.web_agent_id:
                    web_agent_name = agent.name
                    break

            agent_dir = RECORDINGS_DIR / web_agent_name
            agent_dir.mkdir(exist_ok=True)

            recording_path = agent_dir / f"{task.id}_run_{run_number}.gif"
            with open(recording_path, "wb") as f:
                f.write(base64.b64decode(result.gif_recording))
            logger.info(f"Saved recording to: {recording_path}")


async def run_evaluation(demo_project: WebProject, tasks: list[Task], timing_metrics: TimingMetrics):
    final_results = {}
    for task in tasks:
        logger.info(f"\n=== Processing Task {task.id} for Project {demo_project.name} ===")

        # Build one coroutine per agent and run them concurrently
        coroutines = [generate_solution_for_task(demo_project, agent, task, timing_metrics) for agent in AGENTS]
        solutions_for_this_task = await asyncio.gather(*coroutines, return_exceptions=True)

        # Replace exceptions with None to keep list aligned
        clean_solutions = []
        for sol in solutions_for_this_task:
            if isinstance(sol, Exception):
                logger.error(f"Agent coroutine raised: {sol!r}")
                clean_solutions.append(None)
            else:
                clean_solutions.append(sol)
        await save_recordings(evaluation_results, task)

        for eval_result in evaluation_results:
            # Safely get the use case name
            use_case_name = "Unknown Use Case"
            try:
                use_case_name = task.use_case.name
            except AttributeError:
                logger.warning(f"Task with ID {task.id} does not have a 'use_case.name' attribute.")

            final_results.setdefault(eval_result.web_agent_id, {})[task.id] = {
                "score": eval_result.final_score,
                "evaluation_result": eval_result,
                "task_use_case": use_case_name,
            }

    print_performance_statistics(final_results, AGENTS, timing_metrics)
    if PLOT_BENCHMARK_RESULTS:
        plot_results(final_results, AGENTS, timing_metrics, str(config.output_dir))
        plot_task_comparison(final_results, AGENTS, tasks, str(config.output_dir))
    if SAVE_EVALUATION_RESULTS:
        save_results_to_json(final_results, AGENTS, timing_metrics, str(config.output_dir))
    return final_results


# --- NEW: Replaces previous statistics function with a more detailed one ---
def show_per_use_case_statistics(all_results: list[dict], agents: list[IWebAgent], project: WebProject, save_json: bool = True):
    """
    Aggregates and displays detailed statistics, grouped by use case and then by agent.
    """
    logger.info(f"\n\n{'=' * 25} FINAL STATISTICS for Project: {project.name} {'=' * 25}")

    # {(agent_id, use_case_name): [list of scores]}
    use_case_scores = defaultdict(list)
    all_use_cases = set()

    # Step 1: Aggregate all scores from all runs
    for run_result in all_results:
        for agent_id, task_results in run_result.items():
            for _task_id, result_details in task_results.items():
                use_case_name = result_details.get("task_use_case", "Unknown")
                score = result_details.get("score")
                if score is not None:
                    use_case_scores[(agent_id, use_case_name)].append(score)
                    all_use_cases.add(use_case_name)

    stats_summary = {"project": project.name, "use_cases": {}, "overall": {}}

    for use_case in sorted(all_use_cases):
        stats_summary["use_cases"][use_case] = {}
        logger.info(f"\n--- Use Case: {use_case} ---")
        for agent in agents:
            scores = use_case_scores.get((agent.id, use_case), [])
            total = len(scores)
            if total > 0:
                success = sum(1 for s in scores if s == 1.0)
                avg_score = sum(scores) / total
                success_rate = success / total
                stats_summary["use_cases"][use_case][agent.name] = {"avg_score": round(avg_score, 3), "success_rate": round(success_rate, 3), "success_count": success, "total": total}
                logger.info(f"    Agent: {agent.name:<20} | Avg Score: {avg_score:.2f} | Success Rate: {success_rate:>7.2%} ({success}/{total})")
            else:
                stats_summary["use_cases"][use_case][agent.name] = {"avg_score": None, "success_rate": None, "success_count": 0, "total": 0}
                logger.info(f"    Agent: {agent.name:<20} | No results for this use case.")

    # Overall agent stats
    logger.info(f"\n{'-' * 70}\n--- Overall Agent Performance for {project.name} ---")
    for agent in agents:
        all_scores = [s for (aid, _), scores in use_case_scores.items() if aid == agent.id for s in scores]
        total = len(all_scores)
        if total > 0:
            success = sum(1 for s in all_scores if s == 1.0)
            avg_score = sum(all_scores) / total
            success_rate = success / total
            stats_summary["overall"][agent.name] = {"avg_score": round(avg_score, 3), "success_rate": round(success_rate, 3), "success_count": success, "total": total}
            logger.info(f"    Agent: {agent.name:<20} | Avg Score: {avg_score:.2f} | Success Rate: {success_rate:>7.2%} ({success}/{total})")
        else:
            stats_summary["overall"][agent.name] = {"avg_score": None, "success_rate": None, "success_count": 0, "total": 0}
            logger.info(f"    Agent: {agent.name:<20} | No results for this agent.")

    logger.info(f"\n{'=' * 80}\n")

    if save_json:
        output_path = PROJECT_BASE_DIR / f"{project.name.lower().replace(' ', '_')}_use_case_stats.json"
        with open(output_path, "w") as f:
            json.dump(stats_summary, f, indent=4)
        logger.info(f"Saved use-case statistics to {output_path}")

    return stats_summary


def replace_web_agent_id_in_actions(actions: list[BaseAction], web_agent_id: str) -> list[BaseAction]:
    """
    Replaces occurrences of '<web_agent_id>' in the text, url, or value fields of each action
    with the provided web_agent_id.

    Args:
        actions: List of BaseAction instances (e.g., NavigateAction, TypeAction, ClickAction).
        web_agent_id: The integer ID to substitute for the <web_agent_id> placeholder.

    Returns:
        List of updated BaseAction instances.
    """
    for action in actions:
        for field in ["text", "url", "value"]:
            if hasattr(action, field):
                value = getattr(action, field)
                if isinstance(value, str) and "<web_agent_id>" in value:
                    setattr(action, field, value.replace("<web_agent_id>", str(web_agent_id)).replace("your_book_id", str(web_agent_id)))
    return actions


# =========================================================
# MAIN ENTRY
# =========================================================
async def main():
    logger.info("Starting evaluation...")
    try:
        AppBootstrap()
        timing_metrics = TimingMetrics()
        timing_metrics.start()

        if not config.evaluate_real_tasks:
            logger.info("Mode: Evaluating demo web projects.")
            await initialize_demo_webs_projects(demo_web_projects)
            projects_to_run = config.projects_to_run

            logger.info(f"Will run {len(projects_to_run)} project(s): {[p.name for p in projects_to_run]}")

            for project in projects_to_run:
                logger.info(f"\n===== Starting evaluation for project: {project.name} (ID: {project.id}) =====")

                project_results = []
                for i in range(NUM_RUNS_CONST):
                    run_number = i + 1
                    timing_metrics.start()

                    # Generate new tasks for each run to test generalization
                    tasks = await generate_tasks(project)
                    if tasks:
                        for t in tasks:
                            t.should_record = RETURN_EVALUATION_GIF

                        evaluation = await run_evaluation(project, tasks, timing_metrics, run_number)
                        project_results.append(evaluation)
                    else:
                        logger.warning(f"No tasks generated for project {project.name} on run {run_number}. Skipping run.")

                if project_results:
                    show_per_use_case_statistics(project_results, AGENTS, project)
                else:
                    logger.warning(f"No results were collected for project {project.name}. Cannot show statistics.")

        else:
            logger.info("Mode: Evaluating real tasks.")
            tasks_data = load_real_tasks(1)
            real_projects = {t.id: WebProject(id=t.id, name=t.web_name, frontend_url=t.web, backend_url=t.web, is_web_real=True) for t in tasks_data}

            for td in tasks_data:
                project = real_projects.get(td.id)
                if project:
                    logger.info(f"===== Starting evaluation for real task project: {project.name} =====")
                    tasks = await generate_tasks(project, td)
                    if tasks:
                        # Set recording flag for all tasks
                        for t in tasks:
                            t.should_record = RETURN_EVALUATION_GIF
                        # For real tasks, we still do one run
                        results = await run_evaluation(project, tasks, timing_metrics, 1)
                        # Call the new function for real tasks as well
                        show_per_use_case_statistics([results], AGENTS, project)
                    else:
                        logger.warning(f"No tasks generated for real project {project.name}. Skipping.")
                else:
                    logger.warning(f"Could not find a matching project for real task ID: {td.id}")

        logger.info("Evaluation process complete!")
    except Exception as e:
        logger.exception(f"Unexpected error in main execution: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
