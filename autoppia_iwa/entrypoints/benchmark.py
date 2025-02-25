import asyncio
import statistics
from typing import List
import matplotlib.pyplot as plt
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig
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


app = AppBootstrap()
AGENTS: List[BaseAgent] = [RandomClickerWebAgent(name="Random-clicker"), ApifiedWebAgent(name="Text-External-Agent", host="localhost", port=9000)]
iterations = 1  # total_tasks = tasks * iterations
NUM_OF_URLS = 1


async def evaluate_project_for_agent(agent, demo_project, tasks, results):
    """
    Evaluate all tasks for a given demo project and agent.

    For each task, the agent will attempt to solve it and the evaluation score
    will be stored both in the agent's global scores and in the project-specific scores.
    """
    # Initialize project entry in results if not already present.
    if demo_project.name not in results[agent.id]["projects"]:
        results[agent.id]["projects"][demo_project.name] = []

    # Loop over each task in the project.
    for task in tasks:
        task_solution: TaskSolution = await agent.solve_task(task)
        actions: List[BaseAction] = task_solution.actions

        # Prepare evaluator input and configuration.
        task_solution = TaskSolution(task=task, actions=actions, web_agent_id=agent.id)
        evaluator_config = EvaluatorConfig(starting_url=task.url, save_results_in_db=False)
        evaluator = ConcurrentEvaluator(evaluator_config)

        # Evaluate the task solution.
        evaluation_result: EvaluationResult = await evaluator.evaluate_single_task_solution(task=task, task_solution=task_solution)
        score = evaluation_result.final_score

        # Record the score in both global and project-specific results.
        results[agent.id]["global_scores"].append(score)
        results[agent.id]["projects"][demo_project.name].append(score)


def compute_statistics(scores: List[float]) -> dict:
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


async def generate_tasks_for_project(demo_project:WebProject, generate_new_tasks=True):
    """
    Generate tasks for the given demo project.

    If TASKS is provided, it will be used. Otherwise, tasks are generated
    through the TaskGenerationPipeline.
    """
    config = TaskGenerationConfig(web_project=demo_project, 
                                  save_web_analysis_in_db=True, 
                                  save_task_in_db=False,
                                  number_of_prompts_per_task=3,
                                  num_or_urls=NUM_OF_URLS)

    print("Generating Tasks...")
    tasks = []
    for i in range(iterations):
        new_tasks = await TaskGenerationPipeline(web_project=demo_project, config=config).generate()
        tasks.extend(new_tasks.tasks)

    return tasks


def print_performance_statistics(results, agents):
    """
    Print performance statistics for each agent.

    This function iterates over the agents and prints global and per-project statistics.
    """
    print("Agent Performance Metrics:")
    for agent in agents:
        agent_stats = results[agent.id]
        global_stats = compute_statistics(agent_stats["global_scores"])
        print(f"\nAgent: {agent.id}")
        print("  Global Stats:")
        for key, value in global_stats.items():
            print(f"    {key}: {value}")
        print("  Per Project Stats:")
        for project_name, scores in agent_stats["projects"].items():
            project_stats = compute_statistics(scores)
            print(f"    Project: {project_name}")
            for key, value in project_stats.items():
                print(f"      {key}: {value}")


def plot_agent_results(results, agents):
    """
    Plot a bar chart of agents' average global scores.

    Each bar represents an agent (using its id) with its average score displayed
    above the bar. If an agent has no score, a 0 is displayed.
    """
    agent_names = []
    agent_avg_scores = []

    # Calculate average global score for each agent.
    for agent in agents:
        scores = results[agent.id]["global_scores"]
        avg_score = sum(scores) / len(scores) if scores else 0
        agent_names.append(agent.name)
        agent_avg_scores.append(avg_score)

    # Plotting the bar chart.
    plt.figure(figsize=(8, 6))
    bars = plt.bar(agent_names, agent_avg_scores, color='skyblue')
    plt.ylim(0, 10)
    plt.ylabel('Score')
    plt.title('Agent Performance')

    # Add score labels above each bar.
    for bar, score in zip(bars, agent_avg_scores):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{score:.1f}', ha='center', va='bottom')

    # plt.show()
    plt.savefig("output.png")


async def main():
    # ---------------------------
    # 1. Initialize Agents and Results Storage.
    # ---------------------------
    agents: List[BaseAgent] = AGENTS
    results = {}
    for agent in agents:
        results[agent.id] = {"global_scores": [], "projects": {}}

    # ---------------------------
    # 2. Process Each Demo Web Project.
    # ---------------------------
    demo_web_projects: List[WebProject] = await initialize_demo_webs_projects()

    for index, demo_project in enumerate(demo_web_projects):
        tasks = await generate_tasks_for_project(demo_project, generate_new_tasks=True)
        # --- Generate tests for the tasks ---
        llm_service = DIContainer.llm_service()
        test_pipeline = TestGenerationPipeline(llm_service=llm_service, web_project=demo_project)
        tasks = await test_pipeline.add_tests_to_tasks(tasks)
        for agent in agents:
            await evaluate_project_for_agent(agent, demo_project, tasks, results)

    # ---------------------------
    # 3. Print Performance Statistics.
    # ---------------------------
    print_performance_statistics(results, agents)

    # ---------------------------
    # 4. Plot the Agent Results.
    # ---------------------------
    plot_agent_results(results, agents)


if __name__ == "__main__":
    asyncio.run(main())
