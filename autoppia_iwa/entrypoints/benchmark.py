import asyncio
import statistics
import json
import os
import time
from typing import List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig, Task
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import initialize_demo_webs_projects
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import (
    TestGenerationPipeline)

# Importar el visualizador
from autoppia_iwa.src.shared.visualizator import (
    SubnetVisualizer, 
    visualize_task,
    visualize_evaluation,
    visualize_summary
)
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

# Directory configuration
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = "results"
LOG_DIR = os.path.join("logs", f"benchmark_{timestamp}")
TASKS_CACHE_DIR = "data/tasks_cache"

# Caching configuration
USE_CACHED_TASKS = True  # Use cached tasks if available

# Benchmark configuration
ITERATIONS = 1  # Number of iterations per task

# Initialize main components
app = AppBootstrap()
visualizer = SubnetVisualizer(log_directory=LOG_DIR)

# Agents to evaluate
AGENTS: List[IWebAgent] = [
    # RandomClickerWebAgent(name="Random-clicker"),
    ApifiedWebAgent(name="Text-External-Agent", host="localhost", port=9000)
]

# ============================================================
# TASK CACHING FUNCTIONS
# ============================================================


def get_cache_filename(project: WebProject) -> str:
    """
    Generates a cache filename specific to a project.

    Args:
        project (WebProject): The web project.

    Returns:
        str: Path to the cache file for this specific project.
    """
    os.makedirs(TASKS_CACHE_DIR, exist_ok=True)
    safe_name = project.name.replace(" ", "_").lower()
    return os.path.join(TASKS_CACHE_DIR, f"{safe_name}_tasks.json")


async def load_tasks_from_json(project: WebProject) -> Optional[List[Task]]:
    """
    Loads tasks from a project-specific JSON file.

    Args:
        project (WebProject): The project associated with the tasks.

    Returns:
        List[Task]: List of deserialized Task objects or None if not found/invalid.
    """
    filename = get_cache_filename(project)
    if not os.path.exists(filename):
        print(f"Cache file {filename} not found for project '{project.name}'")
        return None

    try:
        with open(filename, 'r') as f:
            cache_data = json.load(f)

        if cache_data.get("project_id") != project.id and cache_data.get("project_name") != project.name:
            print(f"Cache file exists but for a different project. Expected '{project.name}', found '{cache_data.get('project_name')}'")
            return None

        tasks = [Task.deserialize(task_data) for task_data in cache_data.get("tasks", [])]
        print(f"Loaded {len(tasks)} tasks for project '{project.name}' from {filename}")
        return tasks
    except Exception as e:
        print(f"Error loading tasks from {filename}: {str(e)}")
        return None


async def save_tasks_to_json(project: WebProject, tasks: List[Task]) -> bool:
    """
    Saves tasks to a project-specific JSON file.

    Args:
        project (WebProject): The project associated with the tasks.
        tasks (List[Task]): List of tasks to save.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    filename = get_cache_filename(project)

    try:
        cache_data = {
            "project_id": project.id,
            "project_name": project.name,
            "created_at": datetime.now().isoformat(),
            "tasks": [task.serialize() for task in tasks],
        }

        with open(filename, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"Saved {len(tasks)} tasks for project '{project.name}' to {filename}")
        return True
    except Exception as e:
        print(f"Error saving tasks to {filename}: {str(e)}")
        return False


# ============================================================
# TASK AND TEST GENERATION FUNCTIONS
# ============================================================


async def generate_tasks_for_project(demo_project: WebProject, num_of_urls: int = 1) -> List[Task]:
    """
    Generates tasks for the given demo project.
    If USE_CACHED_TASKS is True, attempts to load from the project-specific cache first.

    Args:
        demo_project: The web project for which to generate tasks.
        num_of_urls: Number of URLs to include in task generation.

    Returns:
        List of Task objects.
    """
    if USE_CACHED_TASKS:
        cached_tasks = await load_tasks_from_json(demo_project)
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for project '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for project '{demo_project.name}', generating new tasks...")

    config = TaskGenerationConfig(
        save_web_analysis_in_db=True,
        save_task_in_db=False,
        number_of_prompts_per_task=3,
        num_or_urls=num_of_urls,
    )

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    task_results = await pipeline.generate()

    test_pipeline = TestGenerationPipeline(llm_service=DIContainer.llm_service(), web_project=demo_project)
    tasks_with_tests = await add_tests_to_tasks(task_results.tasks, test_pipeline)

    if USE_CACHED_TASKS:
        await save_tasks_to_json(demo_project, tasks_with_tests)

    return tasks_with_tests


@visualize_task(visualizer)
async def add_tests_to_tasks(tasks: List[Task], test_pipeline: TestGenerationPipeline) -> List[Task]:
    """
    Adds tests to the generated tasks and visualizes them.

    Args:
        tasks: List of tasks to add tests to.
        test_pipeline: Pipeline for test generation.

    Returns:
        List of tasks with added tests.
    """
    print(f"Generating tests for {len(tasks)} tasks...")
    return await test_pipeline.add_tests_to_tasks(tasks)


# ============================================================
# EVALUATION FUNCTIONS
# ============================================================


@visualize_evaluation(visualizer)
async def evaluate_task_solution(web_project: WebProject, task: Task, task_solution: TaskSolution) -> EvaluationResult:
    """
    Evaluates a single task solution with visualization.

    Args:
        web_project: The associated web project.
        task: The task to evaluate.
        task_solution: The task solution proposed by the agent.

    Returns:
        Evaluation result.
    """
    evaluator_config = EvaluatorConfig(save_results_in_db=False)
    evaluator = ConcurrentEvaluator(web_project=web_project, config=evaluator_config)
    return await evaluator.evaluate_single_task_solution(task=task, task_solution=task_solution)


async def evaluate_project_for_agent(agent: IWebAgent, demo_project: WebProject, tasks: List[Task], results: Dict):
    """
    Evaluates all tasks of a project for a given agent.

    Args:
        agent: The agent to evaluate.
        demo_project: The web project to evaluate.
        tasks: List of tasks.
        results: Dictionary to store the results.
    """
    if demo_project.name not in results[agent.id]["projects"]:
        results[agent.id]["projects"][demo_project.name] = []

    for task in tasks:
        start_time = time.time()
        task_solution: TaskSolution = await agent.solve_task(task)
        actions: List[BaseAction] = task_solution.actions

        task_solution = TaskSolution(task_id=task.id, actions=actions, web_agent_id=agent.id)
        evaluation_result: EvaluationResult = await evaluate_task_solution(web_project=demo_project, task=task, task_solution=task_solution)

        score = evaluation_result.final_score
        results[agent.id]["global_scores"].append(score)
        results[agent.id]["projects"][demo_project.name].append(score)

        elapsed_time = time.time() - start_time
        print(f"Task {task.id} evaluated in {elapsed_time:.2f} seconds. Score: {score:.4f}")


# ============================================================
# RESULT ANALYSIS AND VISUALIZATION FUNCTIONS
# ============================================================


def compute_statistics(scores: List[float]) -> Dict:
    """
    Computes basic statistics for a list of scores.

    Args:
        scores: List of scores.

    Returns:
        Dictionary with computed statistics.
    """
    if scores:
        stats = {
            "count": len(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "min": min(scores),
            "max": max(scores),
            "stdev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        }
    else:
        stats = {"count": 0, "mean": None, "median": None, "min": None, "max": None, "stdev": None}
    return stats


@visualize_summary(visualizer)
def print_performance_statistics(results: Dict, agents: List[IWebAgent]):
    """
    Prints performance statistics for each agent.

    Args:
        results: Dictionary containing results.
        agents: List of evaluated agents.
    """
    print("\n" + "=" * 50)
    print("AGENT PERFORMANCE STATISTICS")
    print("=" * 50)

    for agent in agents:
        agent_stats = results[agent.id]
        global_stats = compute_statistics(agent_stats["global_scores"])
        print(f"\nAgent: {agent.id}")
        print("  Global Statistics:")
        print(f"    Tasks completed: {global_stats['count']}")
        print(f"    Average score: {global_stats['mean']:.2f}")
        print(f"    Maximum score: {global_stats['max']:.2f}")

        print("  Project Statistics:")
        for project_name, scores in agent_stats["projects"].items():
            project_stats = compute_statistics(scores)
            print(f"    Project: {project_name}")
            print(f"      Tasks completed: {project_stats['count']}")
            print(f"      Average score: {project_stats['mean']:.2f}")
            print(f"      Maximum score: {project_stats['max']:.2f}")


def plot_agent_results(results: Dict, agents: List[IWebAgent]):
    """
    Creates a bar chart with the average scores of the agents.

    Args:
        results: Dictionary containing results.
        agents: List of evaluated agents.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    agent_names = []
    agent_avg_scores = []

    for agent in agents:
        scores = results[agent.id]["global_scores"]
        avg_score = sum(scores) / len(scores) if scores else 0
        agent_names.append(agent.id)
        agent_avg_scores.append(avg_score)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(agent_names, agent_avg_scores, color='skyblue')
    plt.ylim(0, 1.0)
    plt.ylabel('Score')
    plt.title('Agent Performance')

    for bar, score in zip(bars, agent_avg_scores):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{score:.2f}', ha='center', va='bottom')

    plt.savefig(os.path.join(LOG_DIR, "agent_performance.png"))
    print(f"Chart saved to: {os.path.join(LOG_DIR, 'agent_performance.png')}")


def save_benchmark_results(results: Dict, agents: List[IWebAgent], demo_web_projects: List[WebProject]):
    """
    Saves benchmark results to a JSON file for further analysis.

    Args:
        results: Dictionary containing results.
        agents: List of evaluated agents.
        demo_web_projects: List of evaluated projects.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "results": {},
        "projects": [p.name for p in demo_web_projects],
        "agents": [a.id for a in agents],
    }

    for agent_id, agent_results in results.items():
        output_data["results"][agent_id] = {
            "global_scores": agent_results["global_scores"],
            "projects": agent_results["projects"],
            "statistics": compute_statistics(agent_results["global_scores"]),
        }

    filename = os.path.join(OUTPUT_DIR, f"benchmark_results_{timestamp}.json")
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Benchmark results saved to: {filename}")


# ============================================================
# MAIN BENCHMARK FUNCTION
# ============================================================


async def main():
    print("\n" + "=" * 50)
    print("WEB AGENT BENCHMARK - SUBNET 36")
    print("=" * 50)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        # Initialize agents and results storage
        agents: List[BaseAgent] = AGENTS
        results = {}
        for agent in agents:
            results[agent.id] = {"global_scores": [], "projects": {}}
            print(f"Registered agent: {agent.id}")

        # Initialize demo web projects
        print("\nInitializing demo web projects...")
        demo_web_projects: List[WebProject] = await initialize_demo_webs_projects()
        print(f"Available projects: {', '.join([p.name for p in demo_web_projects])}")

        # Process each demo web project
        for index, demo_project in enumerate(demo_web_projects):
            print(f"\n{'=' * 40}")
            print(f"Processing project {index + 1}/{len(demo_web_projects)}: {demo_project.name}")
            print(f"{'=' * 40}")

            start_time = time.time()
            tasks = await generate_tasks_for_project(demo_project)
            tasks = tasks[0:NUM_OF_TASKS]
            elapsed_time = time.time() - start_time

            print(f"Tasks obtained: {len(tasks)} in {elapsed_time:.2f} seconds")

            total_tests = sum(len(task.tests) if hasattr(task, "tests") else 0 for task in tasks)
            print(f"Tests generated: {total_tests} (average: {total_tests / len(tasks):.1f} per task)")

            # Evaluate each agent on the current project
            for agent in agents:
                print(f"\n{'-' * 30}")
                print(f"Evaluating agent: {agent.id}")
                print(f"{'-' * 30}")

                start_time = time.time()
                await evaluate_project_for_agent(agent, demo_project, tasks, results)
                elapsed_time = time.time() - start_time

                project_scores = results[agent.id]["projects"].get(demo_project.name, [])
                avg_score = sum(project_scores) / len(project_scores) if project_scores else 0

                print(f"Evaluation completed in {elapsed_time:.2f} seconds")
                print(f"Average score: {avg_score:.4f}")

        # Print performance statistics
        print_performance_statistics(results, agents)

        # Plot agent results
        plot_agent_results(results, agents)

        # Save benchmark results
        save_benchmark_results(results, agents, demo_web_projects)

        print("\n" + "=" * 50)
        print("EVALUATION COMPLETED")
        print(f"Results and logs available in: {LOG_DIR}")
        print(f"Charts available in: {OUTPUT_DIR}")
        print("=" * 50)

    except Exception as e:
        import traceback

        print(f"\n[ERROR] During execution: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
