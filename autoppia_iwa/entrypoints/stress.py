import asyncio
import statistics
import time
import json
import os
from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig, Task
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import initialize_demo_webs_projects
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import (
    TestGenerationPipeline)

# Configuration for the stress test
USE_CACHED_TASKS = True  # Set to True to use cached tasks from JSON file
TASKS_CACHE_DIR = "data/tasks_cache"  # Directory to store task cache files
OUTPUT_DIR = "results"  # Directory to store test results
M = 1  # Set this to your desired number of copies
NUMBER_OF_TASKS = 10

# Initialize the app
app = AppBootstrap()

# Define agents for the stress test
AGENTS: List[BaseAgent] = [
    RandomClickerWebAgent(name="Random-clicker"),
    ApifiedWebAgent(name="browser-use", host="localhost", port=9000)
]


class TimingMetrics:
    """Track timing metrics for tasks and agents"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        # Structure: {agent_id: {task_id: time}} for both solution and evaluation times
        self.solution_times = {}  
        self.evaluation_times = {}

    def start(self):
        """Start the overall timing"""
        self.start_time = time.time()

    def end(self):
        """End the overall timing"""
        self.end_time = time.time()

    def record_solution_time(self, agent_id: str, task_id: str, solution_time: float):
        """Record time taken to generate a solution for a specific task"""
        if agent_id not in self.solution_times:
            self.solution_times[agent_id] = {}
        self.solution_times[agent_id][task_id] = solution_time

    def record_evaluation_time(self, agent_id: str, task_id: str, evaluation_time: float):
        """Record time taken for evaluation for a specific task"""
        if agent_id not in self.evaluation_times:
            self.evaluation_times[agent_id] = {}
        self.evaluation_times[agent_id][task_id] = evaluation_time

    def get_total_time(self) -> float:
        """Get total execution time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def get_avg_solution_time(self, agent_id: str) -> float:
        """Get the average solution time across all tasks for a specific agent"""
        if agent_id not in self.solution_times or not self.solution_times[agent_id]:
            return 0.0
        return statistics.mean(self.solution_times[agent_id].values())

    def get_avg_evaluation_time(self, agent_id: str) -> float:
        """Get the average evaluation time across all tasks for a specific agent"""
        if agent_id not in self.evaluation_times or not self.evaluation_times[agent_id]:
            return 0.0
        return statistics.mean(self.evaluation_times[agent_id].values())


def get_cache_filename(project: WebProject) -> str:
    """
    Generate a project-specific cache filename based on the project's name or ID.

    Args:
        project (WebProject): The web project
    Returns:
        str: Path to the cache file for this specific project
    """
    # Create cache directory if it doesn't exist
    os.makedirs(TASKS_CACHE_DIR, exist_ok=True)

    # Use the project name or ID to create a unique filename
    safe_name = project.name.replace(" ", "_").lower()
    return os.path.join(TASKS_CACHE_DIR, f"{safe_name}_tasks.json")


async def save_tasks_to_json(tasks, project: WebProject):
    """
    Save tasks to a project-specific JSON file using the serialize method.

    Args:
        tasks (List[Task]): List of task objects to serialize and save
        project (WebProject): The web project these tasks belong to
    Returns:
        bool: True if saved successfully, False otherwise
    """
    filename = get_cache_filename(project)
    try:
        # Create a structure that includes both project info and tasks
        cache_data = {
            "project_id": project.id,
            "project_name": project.name,
            "timestamp": datetime.now().isoformat(),
            "tasks": [task.serialize() for task in tasks]
        }

        with open(filename, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"Tasks for project '{project.name}' saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving tasks to {filename}: {str(e)}")
        return False


async def load_tasks_from_json(project: WebProject):
    """
    Load tasks from a project-specific JSON file.

    Args:
        project (WebProject): Project to associate with the loaded tasks
    Returns:
        List[Task]: List of deserialized Task objects or None if not found/valid
    """
    filename = get_cache_filename(project)
    if not os.path.exists(filename):
        print(f"Cache file {filename} not found for project '{project.name}'")
        return None

    try:
        with open(filename, 'r') as f:
            cache_data = json.load(f)

        # Verify this cache belongs to the requested project
        if cache_data.get("project_id") != project.id and cache_data.get("project_name") != project.name:
            print(f"Cache file exists but for a different project. Expected '{project.name}', found '{cache_data.get('project_name')}'")
            return None

        # Deserialize the tasks
        tasks = [Task.deserialize(task_data) for task_data in cache_data.get("tasks", [])]

        # Set web_project on each task
        for task in tasks:
            if hasattr(task, "web_project"):
                task.web_project = project

        print(f"Loaded {len(tasks)} tasks for project '{project.name}' from {filename}")
        return tasks
    except Exception as e:
        print(f"Error loading tasks from {filename}: {str(e)}")
        return None


async def generate_tasks_for_project(demo_project: WebProject, num_of_urls: int = 7):
    """
    Generate tasks for the given demo project.
    If USE_CACHED_TASKS is True, tries to load from project-specific cache first.

    Args:
        demo_project: The web project to generate tasks for
        num_of_urls: Number of URLs to include in task generation

    Returns:
        List of Task objects
    """
    # Try to load from cache if configured
    if USE_CACHED_TASKS:
        cached_tasks = await load_tasks_from_json(demo_project)
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for project '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for project '{demo_project.name}', generating new tasks...")

    # Generate new tasks
    config = TaskGenerationConfig(
        web_project=demo_project, 
        save_web_analysis_in_db=True, 
        save_task_in_db=False,
        number_of_prompts_per_task=3,
        num_or_urls=num_of_urls
    )

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    task_results = await pipeline.generate()

    # Save generated tasks to project-specific cache for future use
    if task_results.tasks:
        await save_tasks_to_json(task_results.tasks, demo_project)

    return task_results.tasks


async def generate_agent_solution(agent: BaseAgent, task: Task, timing_metrics: TimingMetrics):
    """
    Generate a solution for a task with the given agent and measure time taken.

    Args:
        agent: The agent to generate the solution
        task: The task to solve
        timing_metrics: Metrics tracker to record timing information

    Returns:
        A TaskSolution object
    """
    print(f"Generating solution for task {task.id} with {agent.name}...")
    start_time = time.time()

    # Generate a solution
    task_solution: TaskSolution = await agent.solve_task(task)
    actions: List[BaseAction] = task_solution.actions

    # Create task solution object
    task_solution = TaskSolution(task=task, actions=actions, web_agent_id=agent.id)

    # Record timing information
    solution_time = time.time() - start_time
    timing_metrics.record_solution_time(agent.id, task.id, solution_time)
    print(f"  Solution generated in {solution_time:.2f} seconds")

    return task_solution


def compute_statistics(values: List[float]) -> dict:
    """
    Compute statistics for a list of values.

    Args:
        values: List of numeric values

    Returns:
        Dictionary with statistics
    """
    if not values:
        return {
            "count": 0, 
            "mean": None, 
            "median": None, 
            "min": None, 
            "max": None, 
            "stdev": None
        }

    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def save_results_to_json(results, agents, timing_metrics):
    """
    Save comprehensive results to a JSON file.

    Args:
        results: Results data by agent and task
        agents: List of agents
        timing_metrics: Timing metrics collected during evaluation
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Format timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"stress_test_results_{timestamp}.json")

    # Prepare data structure for JSON
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_execution_time": timing_metrics.get_total_time(),
        "agents": {}
    }

    # Add data for each agent
    for agent in agents:
        agent_scores = []
        agent_tasks = {}

        # Collect all scores and task-specific data
        if agent.id in results:
            for task_id, result in results[agent.id].items():
                agent_scores.append(result["score"])
                agent_tasks[task_id] = {
                    "score": result["score"],
                    "solution_time": timing_metrics.solution_times.get(agent.id, {}).get(task_id, 0),
                    "evaluation_time": timing_metrics.evaluation_times.get(agent.id, {}).get(task_id, 0)
                }

        # Compute statistics
        score_stats = compute_statistics(agent_scores)

        # Add to output data
        output_data["agents"][agent.id] = {
            "name": agent.name,
            "score_statistics": score_stats,
            "avg_solution_time": timing_metrics.get_avg_solution_time(agent.id),
            "avg_evaluation_time": timing_metrics.get_avg_evaluation_time(agent.id),
            "tasks": agent_tasks
        }

    # Save to file
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nDetailed results saved to '{filename}'")
    return filename


def print_performance_statistics(results, agents, timing_metrics):
    """
    Print comprehensive performance statistics for each agent.

    Args:
        results: Results data organized by agent and task
        agents: List of agents
        timing_metrics: Timing metrics collected during evaluation
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n===== PERFORMANCE REPORT ({timestamp}) =====")

    # Print overall timing information
    print(f"\nTotal test execution time: {timing_metrics.get_total_time():.2f} seconds")

    # Print agent-specific statistics
    for agent in agents:
        print(f"\n== Agent: {agent.name} ({agent.id}) ==")

        # Collect all scores for this agent
        agent_scores = []
        if agent.id in results:
            for task_id, result in results[agent.id].items():
                agent_scores.append(result["score"])

        # Calculate and print score statistics
        score_stats = compute_statistics(agent_scores)
        print("  Score Statistics:")
        for key, value in score_stats.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"    {key}: {value:.2f}")
                else:
                    print(f"    {key}: {value}")
            else:
                print(f"    {key}: N/A")

        # Print timing information
        avg_solution_time = timing_metrics.get_avg_solution_time(agent.id)
        avg_evaluation_time = timing_metrics.get_avg_evaluation_time(agent.id)
        print(f"  Average solution generation time: {avg_solution_time:.2f} seconds")
        print(f"  Average evaluation time: {avg_evaluation_time:.2f} seconds")


def plot_results(results, agents, timing_metrics):
    """
    Generate plots comparing agent performance and timing across all tasks.

    Args:
        results: Results data organized by agent and task
        agents: List of agents
        timing_metrics: Timing metrics collected during evaluation

    Returns:
        Path to the saved plot file
    """
    agent_names = [agent.name for agent in agents]
    agent_ids = [agent.id for agent in agents]

    # Prepare data
    avg_scores = []
    solution_times = []
    evaluation_times = []

    for agent_id in agent_ids:
        # Calculate average score across all tasks
        if agent_id in results:
            scores = [result["score"] for task_id, result in results[agent_id].items()]
            avg_score = statistics.mean(scores) if scores else 0
        else:
            avg_score = 0
        avg_scores.append(avg_score)

        # Get average times
        solution_times.append(timing_metrics.get_avg_solution_time(agent_id))
        evaluation_times.append(timing_metrics.get_avg_evaluation_time(agent_id))

    # Create a figure with three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    # Plot 1: Average Scores
    bars1 = ax1.bar(agent_names, avg_scores, color=['skyblue', 'lightgreen'])
    ax1.set_ylim(0, 10)
    ax1.set_ylabel('Average Score')
    ax1.set_title('Agent Performance: Average Scores')
    for bar, score in zip(bars1, avg_scores):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                 f'{score:.2f}', ha='center', va='bottom')

    # Plot 2: Solution Generation Times
    bars2 = ax2.bar(agent_names, solution_times, color=['coral', 'khaki'])
    ax2.set_ylabel('Average Solution Time (seconds)')
    ax2.set_title('Agent Performance: Solution Generation Times')
    for bar, time_val in zip(bars2, solution_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                 f'{time_val:.2f}s', ha='center', va='bottom')

    # Plot 3: Evaluation Times
    bars3 = ax3.bar(agent_names, evaluation_times, color=['lightblue', 'lightgreen'])
    ax3.set_ylabel('Average Evaluation Time (seconds)')
    ax3.set_title('Agent Performance: Evaluation Times')
    for bar, time_val in zip(bars3, evaluation_times):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                 f'{time_val:.2f}s', ha='center', va='bottom')

    plt.tight_layout()

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate results filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(OUTPUT_DIR, f"stress_test_chart_{timestamp}.png")
    plt.savefig(results_filename)

    print(f"\nCharts have been saved to '{results_filename}'")
    return results_filename


def plot_task_comparison(results, agents, tasks):
    """
    Generate a chart comparing agent performance across different tasks.

    Args:
        results: Results data organized by agent and task
        agents: List of agents
        tasks: List of tasks

    Returns:
        Path to the saved plot file
    """
    # If we have more than 10 tasks, limit to 10 for readability
    max_tasks_to_show = min(10, len(tasks))
    selected_tasks = tasks[:max_tasks_to_show]

    # Setup the chart
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create x positions for the bars
    bar_width = 0.35
    x = range(len(selected_tasks))

    # Track legend items
    legend_handles = []

    # Plot bars for each agent
    for i, agent in enumerate(agents):
        agent_scores = []

        for task in selected_tasks:
            if agent.id in results and task.id in results[agent.id]:
                agent_scores.append(results[agent.id][task.id]["score"])
            else:
                agent_scores.append(0)

        # Plot bars with offset for this agent
        bars = ax.bar([pos + (i * bar_width) for pos in x], 
                      agent_scores, 
                      width=bar_width, 
                      label=agent.name)
        legend_handles.append(bars[0])

    # Set x-axis labels to task IDs or shortened task descriptions
    task_labels = [f"Task {i+1}" for i in range(len(selected_tasks))]
    ax.set_xticks([pos + bar_width / 2 for pos in x])
    ax.set_xticklabels(task_labels, rotation=45, ha='right')

    # Add labels and legend
    ax.set_ylabel('Score')
    ax.set_title('Agent Performance by Task')
    ax.set_ylim(0, 10)
    ax.legend(handles=legend_handles, labels=[agent.name for agent in agents])

    plt.tight_layout()

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate results filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(OUTPUT_DIR, f"task_comparison_{timestamp}.png")
    plt.savefig(results_filename)

    print(f"\nTask comparison chart saved to '{results_filename}'")
    return results_filename


async def main():
    """Main function to run the comprehensive multi-task agent evaluation with batch evaluation"""
    print("Starting comprehensive multi-task agent evaluation with batch processing...")
    # Initialize timing metrics tracker
    timing_metrics = TimingMetrics()
    timing_metrics.start()
    # Initialize results storage: {agent_id: {task_id: {"score": score}}}
    results = {}

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load demo web projects
    demo_web_projects: List[WebProject] = await initialize_demo_webs_projects()
    if not demo_web_projects:
        print("Error: No demo web projects available.")
        return

    # Use the first project for the evaluation
    demo_project = demo_web_projects[0]
    print(f"Using project: {demo_project.name}")

    # Generate or load tasks for the project
    tasks = await generate_tasks_for_project(demo_project)
    if not tasks:
        print("Error: No tasks available.")
        return

    tasks = tasks[0:NUMBER_OF_TASKS]

    # Add tests to the tasks if they don't already have them
    if not all(hasattr(task, 'tests') and task.tests for task in tasks):
        print("Adding tests to tasks...")
        llm_service = DIContainer.llm_service()
        test_pipeline = TestGenerationPipeline(llm_service=llm_service, web_project=demo_project)
        tasks_with_tests = await test_pipeline.add_tests_to_tasks(tasks)
        # Save the tasks with tests
        if tasks_with_tests:
            await save_tasks_to_json(tasks_with_tests, demo_project)
            tasks = tasks_with_tests
    else:
        print("Tasks already have test cases.")

    if not tasks:
        print("Error: Failed to process tasks.")
        return

    # Number of solution copies to evaluate in batch

    print(f"Evaluating {len(tasks)} tasks with {len(AGENTS)} agents, {M} copies per solution...")

    # First generate all solutions for all agents across all tasks (ONCE per combination)
    all_solutions = {}  # {agent_id: {task_id: TaskSolution}}

    print("\n--- Phase 1: Generating Solutions (ONCE per agent per task) ---")
    for agent in AGENTS:
        all_solutions[agent.id] = {}
        print(f"\nGenerating solutions for {agent.name} agent...")

        for task in tasks:
            print(f"Generating solution for task {task.id}...")

            # Generate the solution ONCE
            start_time = time.time()
            solution: TaskSolution = await agent.solve_task(task)
            actions: List[BaseAction] = solution.actions
            task_solution = TaskSolution(task=task, actions=actions, web_agent_id=agent.id)
            solution_time = time.time() - start_time
            timing_metrics.record_solution_time(agent.id, task.id, solution_time)
            print(f"  Solution generated in {solution_time:.2f} seconds")

            # Store the solution for later use
            all_solutions[agent.id][task.id] = task_solution

    print("\n--- Phase 2: Evaluating Solutions in Batches ---")
    # Initialize results for each agent
    for agent in AGENTS:
        if agent.id not in results:
            results[agent.id] = {}

    # Now evaluate M copies of each solution for each agent/task
    for agent in AGENTS:
        print(f"\nEvaluating solutions for {agent.name} agent...")

        for task in tasks:
            print(f"Evaluating solution for task {task.id}...")

            # Get the original solution generated earlier
            original_solution = all_solutions[agent.id][task.id]

            # Create M copies of the solution
            solution_copies = []
            for i in range(M):
                # Create a copy with the same actions
                copy_solution = TaskSolution(
                    task=task,
                    actions=original_solution.actions.copy() if original_solution.actions else [],
                    web_agent_id=agent.id
                )
                solution_copies.append(copy_solution)

            # Evaluate all M copies together
            print(f"Evaluating {M} copies of solution for task {task.id}...")
            start_eval_time = time.time()

            # Prepare evaluator configuration
            evaluator_config = EvaluatorConfig(
                save_results_in_db=False,
                enable_grouping_tasks=False,
                chunk_size=20
            )
            evaluator = ConcurrentEvaluator(web_project=demo_project, config=evaluator_config)

            # Evaluate all solution copies together in ONE batch
            evaluation_results: List[EvaluationResult] = await evaluator.evaluate_task_solutions(
                task=task, 
                task_solutions=solution_copies
            )

            # Record timing information
            evaluation_time = time.time() - start_eval_time
            timing_metrics.record_evaluation_time(agent.id, task.id, evaluation_time / M)  # Per-solution time

            # Calculate average score across all copies
            avg_score = sum(result.final_score for result in evaluation_results) / len(evaluation_results)
            print(f"  Batch evaluation of {M} copies completed in {evaluation_time:.2f} seconds")
            print(f"  Average score: {avg_score:.2f}")

            # Store the result
            results[agent.id][task.id] = {
                "score": avg_score,
                "num_solutions_evaluated": M,
                "total_evaluation_time": evaluation_time,
                "per_solution_time": evaluation_time / M
            }

    # Record the end time
    timing_metrics.end()

    # Print statistics and create plots
    print_performance_statistics(results, AGENTS, timing_metrics)
    chart_path = plot_results(results, AGENTS, timing_metrics)
    task_chart_path = plot_task_comparison(results, AGENTS, tasks)
    json_path = save_results_to_json(results, AGENTS, timing_metrics)

    print(f"\nEvaluation complete! Results saved to {OUTPUT_DIR} directory.")

if __name__ == "__main__":
    asyncio.run(main())
