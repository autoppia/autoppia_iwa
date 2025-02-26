# file: evaluation.py

import asyncio
import statistics
from typing import List

import matplotlib.pyplot as plt

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import demo_web_projects, initialize_test_demo_web_projects
from autoppia_iwa.src.data_generation.domain.classes import (
    TaskGenerationConfig,
    TasksGenerationOutput,
)
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline

from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import (
    ConcurrentEvaluator,
    EvaluatorConfig,
)
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent


# Bootstrap the application and its DI container.
app = AppBootstrap()


async def generate_tasks(num_tasks: int = 3):
    test_projects = await initialize_test_demo_web_projects()
    web_project = test_projects[0]
    config = TaskGenerationConfig(
        save_task_in_db=False,
        save_web_analysis_in_db=True,
        enable_crawl=True,
        generate_milestones=False,
        global_tasks_to_generate=num_tasks,
        local_tasks_to_generate_per_url=1,
    )
    pipeline = TaskGenerationPipeline(web_project=web_project, config=config)
    output: TasksGenerationOutput = await pipeline.generate()
    return output.tasks


async def evaluate_project_for_agent(agent: BaseAgent, project, tasks, results):
    if project.name not in results[agent.id]["projects"]:
        results[agent.id]["projects"][project.name] = []

    for task in tasks:
        task_solution: TaskSolution = await agent.solve_task(task)
        evaluator_input = TaskSolution(
            task=task,
            actions=task_solution.actions,
            web_agent_id=agent.id
        )
        evaluator_config = EvaluatorConfig(
            current_url=task.url,
            save_results_in_db=False
        )
        evaluator = ConcurrentEvaluator(evaluator_config)
        evaluation_result: EvaluationResult = await evaluator.evaluate_single_task(evaluator_input)
        score = evaluation_result.final_score
        results[agent.id]["global_scores"].append(score)
        results[agent.id]["projects"][project.name].append(score)


def compute_statistics(scores: List[float]) -> dict:
    if scores:
        return {
            "count": len(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "min": min(scores),
            "max": max(scores),
            "stdev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        }
    return {
        "count": 0,
        "mean": None,
        "median": None,
        "min": None,
        "max": None,
        "stdev": None,
    }


def print_performance_statistics(results, agents):
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
            for key, val in project_stats.items():
                print(f"      {key}: {val}")


def plot_agent_results(results, agents):
    agent_names = []
    agent_avg_scores = []

    for agent in agents:
        scores = results[agent.id]["global_scores"]
        avg_score = sum(scores) / len(scores) if scores else 0
        agent_names.append(agent.name)
        agent_avg_scores.append(avg_score)

    plt.figure(figsize=(8, 6))
    bars = plt.bar(agent_names, agent_avg_scores, color='skyblue')
    plt.ylim(0, 10)
    plt.ylabel('Score')
    plt.title('Agent Performance')
    for bar, score in zip(bars, agent_avg_scores):
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            f'{score:.1f}',
            ha='center',
            va='bottom'
        )
    plt.savefig("output.png")


def judge_tasks_feasibility(tasks, results, agents):
    judge_input = "Summary of generated tasks and results:\n\n"
    for idx, task in enumerate(tasks, start=1):
        judge_input += f"Task {idx}:\n"
        judge_input += f"  Prompt: {task.prompt}\n"
        judge_input += f"  URL: {task.url}\n"
        if task.tests:
            judge_input += "  Tests:\n"
            for test in task.tests:
                judge_input += f"    - {test.model_dump()}\n"
        else:
            judge_input += "  No tests.\n"
        judge_input += "\n"

    judge_input += "Agent Performance:\n"
    for agent in agents:
        agent_scores = results[agent.id]["global_scores"]
        judge_input += f"  {agent.name} => Scores: {agent_scores}\n"
    judge_input += (
        "\nPlease evaluate if these tasks were feasible, whether the tests seem valid, and "
        "offer suggestions for improving task/test generation."
    )

    app = AppBootstrap()
    llm_service = app.container.llm_service()

    judge_response = llm_service.make_request(
        message_payload=[{"role": "user", "content": judge_input}],
        chat_completion_kwargs={
            "temperature": 0.5,
            "top_k": 40,
            "model": "03-mini",
        },
    )
    print("\n----- LLM Feasibility Assessment -----")
    print(judge_response)


async def main():
    tasks = generate_tasks(num_tasks=3)

    agents: List[BaseAgent] = [
        RandomClickerWebAgent(),
        ApifiedWebAgent(name="Autoppia-agent", host="localhost", port=8080)
    ]
    results = {agent.id: {"global_scores": [], "projects": {}} for agent in agents}

    for demo_project in demo_web_projects:
        for agent in agents:
            await evaluate_project_for_agent(agent, demo_project, tasks, results)

    print_performance_statistics(results, agents)
    plot_agent_results(results, agents)
    judge_tasks_feasibility(tasks, results, agents)


if __name__ == "__main__":
    asyncio.run(main())
