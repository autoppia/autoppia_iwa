import asyncio
import statistics
from typing import List

import matplotlib.pyplot as plt

from autoppia_iwa.src.backend_demo_web.config import demo_web_projects
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, TaskGenerationConfig
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventEmittedTest, FindInHtmlTest
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import Task, TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent
from autoppia_iwa.src.bootstrap import AppBootstrap

app = AppBootstrap()
TASKS = [
    # Task(
    #     prompt="Get the interactive elements from the services by using strictly the 'get_dropdown_options' option only",
    #     url='https://www.w3schools.com/',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[CheckPageViewEventTest(page_view_url='/login'), FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['login', 'log in'])],
    #     milestones=None,
    #     web_analysis=None,
    # ), # ONLY for testing as it throws errors due to service not found
    # Task(
    #     prompt="Click the 'Login' button to access the login page.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[CheckPageViewEventTest(page_view_url='/login'), FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['login', 'log in'])],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    Task(
        prompt="Enter your email and password in the respective fields and click the 'Log in' button to authenticate and access your account. Email:test@test.com, password:test@test.com",
        url='http://localhost:8000',
        specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
        tests=[
            CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='login'),
            FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['logout', 'sign out', 'welcome']),
        ],
        milestones=None,
        web_analysis=None,
    ),
    # Task(
    #     prompt="Click the 'Register' dropdown in the navigation bar and select 'Employee' to register as an employee on the website.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'registration successful', 'welcome aboard']),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    Task(
        prompt="Navigate to the 'About Us' section by clicking on the 'About Us' link in the header menu.",
        url='http://localhost:8000',
        specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
        tests=[],
        milestones=None,
        web_analysis=None,
    ),
    # Task(
    #     prompt='Fill out the contact form by entering your name, email, and message, then submit the form to send your inquiry.',
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='message_sent'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'message sent', 'inquiry received']),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Register' button in the navigation menu and then select 'Employers' to access the employer registration form.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(
    #             description='Find keywords in the current HTML content',
    #             test_type='frontend',
    #             keywords=['new account', 'company name', 'company address', 'email', 'password', 'confirm password', 'register'],
    #         ),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Register' button in the navigation menu to open the employee registration form.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'registration successful', 'welcome aboard']),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Login' button to access the login page.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Register' dropdown in the navigation bar and select 'Employee' to register as an employee on the website.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'registration successful', 'welcome aboard']),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Navigate to the 'About Us' section by clicking on the 'About Us' link in the header menu.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt='Fill out the contact form by entering your name, email, and message, then submit the form to send your inquiry.',
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='message_sent'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'message sent', 'inquiry received']),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Register' button in the navigation menu and then select 'Employers' to access the employer registration form.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(
    #             description='Find keywords in the current HTML content',
    #             test_type='frontend',
    #             keywords=['new account', 'company name', 'company address', 'email', 'password', 'confirm password', 'register'],
    #         ),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Register' button in the navigation menu to open the employee registration form.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'registration successful', 'welcome aboard']),
    #     ],
    #     milestones=None,
    #     web_analysis=None,
    # ),
    # Task(
    #     prompt="Click the 'Login' button to access the login page.",
    #     url='http://localhost:8000',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[],
    #     milestones=None,
    #     web_analysis=None,
    # ),
]


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
        # Agent solves the task.
        task_solution: TaskSolution = await agent.solve_task(task)
        actions: List[BaseAction] = task_solution.actions

        # Prepare evaluator input and configuration.
        evaluator_input = TaskSolution(task=task, actions=actions, web_agent_id=agent.id)
        evaluator_config = EvaluatorConfig(current_url=task.url, save_results_in_db=False)
        evaluator = ConcurrentEvaluator(evaluator_config)

        # Evaluate the task solution.
        evaluation_result: EvaluationResult = await evaluator.evaluate_single_task(evaluator_input)
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


def generate_tasks_for_project(demo_project):
    """
    Generate tasks for the given demo project.

    If TASKS is provided, it will be used. Otherwise, tasks are generated
    through the TaskGenerationPipeline.
    """
    task_input = TaskGenerationConfig(web_project=demo_project, save_web_analysis_in_db=True, save_task_in_db=False)
    # if TASKS:
    #     tasks = TASKS
    # else:
    task_output = TaskGenerationPipeline(task_input).generate()
    tasks = task_output.tasks
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
    agents: List[BaseAgent] = [RandomClickerWebAgent()]  # You can add more agents if desired.
    results = {}
    for agent in agents:
        results[agent.id] = {"global_scores": [], "projects": {}}

    # ---------------------------
    # 2. Process Each Demo Web Project.
    # ---------------------------
    for demo_project in demo_web_projects:
        tasks = generate_tasks_for_project(demo_project)
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
