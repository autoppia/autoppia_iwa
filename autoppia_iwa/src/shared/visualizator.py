import os
from functools import wraps

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class SubnetVisualizer:
    """
    Improved visualizer for Subnet 36, which displays:
    1. The Task with its prompt
    2. Associated Tests with detailed information
    3. The Agent's Actions
    4. Test results (✅/❌)
    5. Scores
    """

    def __init__(self, log_directory: str | None = None):
        self.console = Console()
        if log_directory:
            os.makedirs(log_directory, exist_ok=True)
        self.log_directory = log_directory

    def show_task_with_tests(self, task):
        """
        Displays a task and its configured tests.
        """
        # Panel to show the task prompt
        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"

        self.console.print("\n" + "=" * 80)

        task_panel = Panel(prompt, title=f"[bold cyan]TASK: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 2))
        self.console.print(task_panel)

        # Table of configured tests
        if hasattr(task, "tests") and task.tests:
            tests_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE, expand=True)
            tests_table.add_column("Test #", style="dim", width=6)
            tests_table.add_column("Type", style="cyan", width=22)
            tests_table.add_column("Description", style="yellow")
            tests_table.add_column("Attributes", style="red")

            for idx, test in enumerate(task.tests):
                test_type = type(test).__name__
                description, attributes = self._get_detailed_test_description_and_attributes(test)
                tests_table.add_row(str(idx + 1), test_type, description, attributes)

            self.console.print("\n[bold magenta]CONFIGURED TESTS:[/bold magenta]")
            self.console.print(tests_table)
            self.console.print("-" * 80)

    def show_full_evaluation(
        self,
        agent_id,
        validator_id,
        task,
        actions,
        test_results_matrix,
        evaluation_result=None,
        feedback=None,
    ):
        """
        Displays a full evaluation with all details: task, actions, tests, and results.
        Actions are shown first, followed by tests, each in its own panel.

        Args:
            agent_id: ID of the evaluated agent
            task: The evaluated task
            actions: List of actions taken
            test_results_matrix: Matrix of test results
            evaluation_result: The evaluation result object
            feedback: Optional additional feedback
        """
        self.console.print("\n" + "=" * 80)
        self.console.print(f"\n[bold white on blue]COMPLETE EVALUATION - AGENT: {agent_id}, VALIDATOR:{validator_id}[/bold white on blue]\n")

        # 1. Show task details
        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"

        task_panel = Panel(prompt, title=f"[bold cyan]TASK: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 2))
        self.console.print(task_panel)

        # 2. Table of executed actions (shown first now)
        if actions:
            actions_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
            actions_table.add_column("#", style="dim", width=4)
            actions_table.add_column("Type", style="cyan", width=18)
            actions_table.add_column("Details", style="green")

            for idx, action in enumerate(actions):
                action_type = type(action).__name__ if hasattr(action, "__class__") else "Unknown"
                details = self._format_action_details(action)
                actions_table.add_row(str(idx + 1), action_type, details)

            actions_panel = Panel(actions_table, title="[bold green]ACTIONS EXECUTED[/bold green]", border_style="green", padding=(1, 1))
            self.console.print("\n")
            self.console.print(actions_panel)
        else:
            self.console.print("\n[yellow]No actions were executed[/yellow]")

        # 3. Table of configured tests with their results (now shown after the actions)
        if hasattr(task, "tests") and task.tests and test_results_matrix and len(test_results_matrix) > 0:
            tests_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE, expand=True)
            tests_table.add_column("Test #", style="dim", width=6)
            tests_table.add_column("Type", style="cyan", width=22)
            tests_table.add_column("Description", style="yellow")
            tests_table.add_column("Result", style="bold", width=10)

            for idx, test in enumerate(task.tests):
                # Ensure there's a result for this test
                if idx < len(test_results_matrix[0]):
                    test_passed = False
                    for action_idx in range(len(test_results_matrix)):
                        if isinstance(test_results_matrix[action_idx][idx], dict):
                            if test_results_matrix[action_idx][idx]["success"]:
                                test_passed = True
                                break
                        else:
                            if test_results_matrix[action_idx][idx].success:
                                test_passed = True
                                break

                    # Get detailed test description
                    test_type = type(test).__name__
                    description, attributes = self._get_detailed_test_description_and_attributes(test)

                    # Format the result
                    result_text = "✅ PASS" if test_passed else "❌ FAIL"
                    result_style = "green" if test_passed else "red"

                    tests_table.add_row(str(idx + 1), test_type, description, attributes, Text(result_text, style=result_style))

            tests_panel = Panel(tests_table, title="[bold magenta]TESTS AND RESULTS[/bold magenta]", border_style="magenta", padding=(1, 1))
            self.console.print("\n")
            self.console.print(tests_panel)
        else:
            self.console.print(f"DEBUG: task.tests = {task.tests}")
            self.console.print(f"DEBUG: test_results_matrix = {test_results_matrix}")
            self.console.print("\n[yellow]No configured tests or available results[/yellow]")

        # 4. Show scores
        if evaluation_result:
            scores_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
            scores_table.add_column("Type", style="yellow", justify="right", width=25)
            scores_table.add_column("Value", style="cyan", width=10)

            if isinstance(evaluation_result, dict):
                # Si es un diccionario, accedemos con la notación de diccionario
                raw_score = evaluation_result.get("raw_score", 0.0)
                random_score = evaluation_result.get("random_clicker_score", 0.0)
                final_score = evaluation_result.get("final_score", 0.0)
            else:
                # Si es un objeto, accedemos con la notación de atributos
                raw_score = evaluation_result.raw_score if hasattr(evaluation_result, "raw_score") else 0.0
                random_score = evaluation_result.random_clicker_score if hasattr(evaluation_result, "random_clicker_score") else 0.0
                final_score = evaluation_result.final_score if hasattr(evaluation_result, "final_score") else 0.0

            scores_table.add_row("Raw Score:", f"{raw_score:.4f}")
            scores_table.add_row("Random Clicker Score:", f"{random_score:.4f}")
            scores_table.add_row("Adjusted Score:", Text(f"{final_score:.4f}", style="bold green" if final_score > 0.5 else "bold red"))

            scores_panel = Panel(scores_table, title="[bold blue]SCORES[/bold blue]", border_style="blue", padding=(1, 1))
            self.console.print("\n")
            self.console.print(scores_panel)

        # 5. Additional feedback information, if provided
        if feedback:
            feedback_content = f"""
    [bold]Tests passed:[/bold] {feedback.passed_tests}/{feedback.passed_tests + feedback.failed_tests}
    [bold]Total time:[/bold] {feedback.total_execution_time:.2f}s
            """

            feedback_panel = Panel(feedback_content, title="[bold green]ADDITIONAL FEEDBACK[/bold green]", border_style="green", padding=(1, 1))
            self.console.print("\n")
            self.console.print(feedback_panel)

        # Final separator
        self.console.print("\n" + "=" * 80)

    def show_list_of_evaluations(self, task, task_solutions, evaluation_results, validator_id):
        """
        Displays evaluations for multiple task solutions.

        Args:
            task: The evaluated task
            task_solutions: List of TaskSolution objects to evaluate
            validator_id: The ID of the validator performing the evaluation
        """
        self.console.print("\n" + "=" * 100)
        self.console.print(f"[bold white on blue]MULTIPLE EVALUATIONS FOR TASK: {task.id}[/bold white on blue]\n")

        for sol, evaluation_result in zip(task_solutions, evaluation_results, strict=False):
            self.show_full_evaluation(
                agent_id=sol.web_agent_id,
                validator_id=validator_id,
                task=task,
                actions=sol.actions,
                test_results_matrix=evaluation_result.test_results_matrix if hasattr(evaluation_result, "test_results_matrix") else [],
                evaluation_result=evaluation_result if evaluation_result else None,
                feedback=evaluation_result.feedback if hasattr(evaluation_result, "feedback") else None,
            )

        self.console.print("\n" + "=" * 100)
        self.console.print("[bold green]All evaluations completed![/bold green]")

    def _format_action_details(self, action):
        """
        Formats the details of a single action for display in a readable manner.
        """
        details = ""
        if hasattr(action, "model_dump"):
            # For Pydantic actions
            action_dict = action.model_dump()
            exclude_keys = ["type"]
            for key, value in action_dict.items():
                if key not in exclude_keys and value:
                    if isinstance(value, str) and len(value) > 30:
                        value = f"'{value[:27]}...'"
                    elif isinstance(value, str):
                        value = f"'{value}'"
                    details += f"{key}={value}, "
            details = details.rstrip(", ")
        elif hasattr(action, "__dict__"):
            # For regular objects
            vars_dict = vars(action)
            for key, value in vars_dict.items():
                if not key.startswith("_") and value:
                    if isinstance(value, str) and len(value) > 30:
                        value = f"'{value[:27]}...'"
                    elif isinstance(value, str):
                        value = f"'{value}'"
                    details += f"{key}={value}, "
            details = details.rstrip(", ")
        else:
            details = str(action)
        return details

    def _get_detailed_test_description_and_attributes(self, test):
        """
        Extracts a specific, detailed description of the test based on its type and attributes.
        """
        description = ""
        attributes = {}
        test_type = type(test).__name__

        # Specific information by test type
        if test_type == "CheckUrlTest":
            # For URL tests, show the expected URL or path
            if hasattr(test, "url"):
                description = f"Check navigation to URL: '{test.url}'"
            elif hasattr(test, "expected_url"):
                description = f"Check navigation to URL: '{test.expected_url}'"
            elif hasattr(test, "url_pattern"):
                description = f"Check URL pattern: '{test.url_pattern}'"
            attributes["url"] = test.url if hasattr(test, "url") else test.expected_url if hasattr(test, "expected_url") else test.url_pattern

        if test_type == "FindInHtmlTest":
            # For URL tests, show the expected URL or path
            if hasattr(test, "content"):
                description = f"Find in HTML next substring:: '{test.content}'"

            attributes["content"] = test.content

        elif "HTML" in test_type or test_type == "JudgeBaseOnHTML" or test_type == "OpinionBasedHTMLTest":
            # For HTML opinion tests, show the success criteria
            if hasattr(test, "success_criteria"):
                criteria = test.success_criteria
                if len(criteria) > 60:
                    criteria = criteria[:57] + "..."
                description = f"Success criteria: '{criteria}'"
            elif hasattr(test, "query"):
                description = f"Query: '{test.query}'"

        elif "Event" in test_type or test_type == "CheckEventTest":
            # For event tests, show the event name
            if hasattr(test, "event_name"):
                description = f"Check backend event: '{test.event_name}'"
                attributes["event_name"] = test.event_name

        # If no description was generated with the specific cases, try to extract common attributes
        if not description:
            priority_attrs = ["description", "text", "expected", "target", "selector"]
            for attr in priority_attrs:
                if hasattr(test, attr) and getattr(test, attr):
                    value = getattr(test, attr)
                    if isinstance(value, str) and len(value) > 60:
                        value = value[:57] + "..."
                    description = f"{attr.capitalize()}: '{value}'"
                    break

            # If there is still no description, try to show all relevant attributes
            if not description:
                all_attrs = []
                for attr_name, attr_value in vars(test).items():
                    if not attr_name.startswith("_") and attr_value and attr_name not in ["type"]:
                        if isinstance(attr_value, str) and len(attr_value) > 30:
                            attr_value = attr_value[:27] + "..."
                        all_attrs.append(f"{attr_name}='{attr_value}'")

                description = ", ".join(all_attrs) if all_attrs else f"Test type {test_type}"

        return description, str(attributes)

    def print_summary(self, results, agents):
        """
        Prints a performance summary for each agent.
        """
        self.console.print("\n" + "=" * 80)
        self.console.print(Align.center("[bold white on blue]PERFORMANCE SUMMARY[/bold white on blue]"))
        self.console.print("=" * 80 + "\n")

        summary_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
        summary_table.add_column("Agent", style="cyan")
        summary_table.add_column("Tasks", style="dim")
        summary_table.add_column("Average Score", style="green")
        summary_table.add_column("Max Score", style="yellow")

        for agent in agents:
            scores = results[agent.id]["global_scores"]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0

            summary_table.add_row(agent.id, str(len(scores)), f"{avg_score:.4f}", f"{max_score:.4f}")

        self.console.print(summary_table)

        # Project details
        for agent in agents:
            if not results[agent.id]["projects"]:
                continue

            self.console.print(f"\n[bold cyan]Project Details - Agent: {agent.id}[/bold cyan]")

            project_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
            project_table.add_column("Project", style="magenta")
            project_table.add_column("Tasks", style="dim")
            project_table.add_column("Average Score", style="green")
            project_table.add_column("Max Score", style="yellow")

            for project_name, scores in results[agent.id]["projects"].items():
                if not scores:
                    continue

                avg_score = sum(scores) / len(scores)
                max_score = max(scores)

                project_table.add_row(project_name, str(len(scores)), f"{avg_score:.4f}", f"{max_score:.4f}")

            self.console.print(project_table)

        self.console.print("\n" + "=" * 80)


# Decorators to integrate with the benchmark


def visualize_task(visualizer):
    """Decorator to visualize a task and its tests."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if isinstance(result, list):
                for task in result:
                    visualizer.show_task_with_tests(task)
            else:
                visualizer.show_task_with_tests(result)
            return result

        return wrapper

    return decorator


def visualize_evaluation(visualizer):
    """Decorator to visualize an agent's evaluation."""

    def decorator(func):
        @wraps(func)
        async def wrapper(web_project, task, task_solution, validator_id, *args, **kwargs):
            result = await func(web_project, task, task_solution, validator_id, *args, **kwargs)
            visualizer.show_full_evaluation(
                agent_id=task_solution.web_agent_id,
                task=task,
                validator_id=validator_id,
                actions=task_solution.actions,
                test_results_matrix=result.test_results_matrix if hasattr(result, "test_results_matrix") else [],
                evaluation_result=result,
                feedback=result.feedback if hasattr(result, "feedback") else None,
            )
            return result

        return wrapper

    return decorator


def visualize_list_of_evaluations(visualizer):
    """Decorator to visualize multiple agents' evaluations for a given task."""

    def decorator(func):
        @wraps(func)
        async def wrapper(web_project, task, task_solutions, validator_id, *args, **kwargs):
            evaluation_results = await func(web_project, task, task_solutions, validator_id, *args, **kwargs)
            visualizer.show_list_of_evaluations(task, task_solutions, evaluation_results, validator_id)

            return evaluation_results

        return wrapper

    return decorator


def visualize_summary(visualizer):
    """Decorator to visualize the final summary."""

    def decorator(func):
        @wraps(func)
        def wrapper(results, agents, *args, **kwargs):
            func(results, agents, *args, **kwargs)
            visualizer.print_summary(results, agents)
            return None

        return wrapper

    return decorator


def test_visualization():
    # Simplified classes for this example
    class Task:
        def __init__(self, id, prompt, tests):
            self.id = id
            self.prompt = prompt
            self.tests = tests

    class CheckUrlTest:
        def __init__(self, type, url, description):
            self.type = type
            self.url = url
            self.description = description

    class ClickAction:
        def __init__(self, type, x, y, selector=None):
            self.type = type
            self.x = x
            self.y = y
            self.selector = selector

        def __str__(self):
            return f"ClickAction(x={self.x}, y={self.y})"

        def model_dump(self):
            return {"type": self.type, "x": self.x, "y": self.y, "selector": self.selector}

    class TestResult:
        def __init__(self, success, message):
            self.success = success
            self.message = message

    class EvaluationResult:
        def __init__(self):
            self.raw_score = 0.0
            self.random_clicker_score = 0.0
            self.final_score = 0.0

    # Create a visualizer
    visualizer = SubnetVisualizer()

    # Example data
    task = Task(id="41b0f865-d1f1-47bb-8ab7-9572dea9ca4a", prompt="Navigate to the 'About Us' page.", tests=[CheckUrlTest(type="CheckUrlTest", url="/about/", description="Check URL")])

    agent_id = "browser-agent-1"

    actions = [ClickAction(type="ClickAction", x=1711, y=978)]

    # Create a simulated test results matrix
    test_result = TestResult(success=False, message="URL does not match /about/")
    test_results_matrix = [[test_result]]

    # Create a simulated evaluation result object
    evaluation_result = EvaluationResult()

    # Call the visualization function
    visualizer.show_full_evaluation(agent_id=agent_id, validator_id="test", task=task, actions=actions, test_results_matrix=test_results_matrix, evaluation_result=evaluation_result)


def test_multiple_evaluations():
    # Simplified classes for this example
    class Task:
        def __init__(self, id, prompt, tests):
            self.id = id
            self.prompt = prompt
            self.tests = tests

    class CheckUrlTest:
        def __init__(self, type, url, description):
            self.type = type
            self.url = url
            self.description = description

    class ClickAction:
        def __init__(self, type, x, y, selector=None):
            self.type = type
            self.x = x
            self.y = y
            self.selector = selector

        def __str__(self):
            return f"ClickAction(x={self.x}, y={self.y})"

        def model_dump(self):
            return {"type": self.type, "x": self.x, "y": self.y, "selector": self.selector}

    class TestResult:
        def __init__(self, success, message):
            self.success = success
            self.message = message

    class EvaluationResult:
        def __init__(self, raw_score=0.0, random_clicker_score=0.0, final_score=0.0):
            self.raw_score = raw_score
            self.random_clicker_score = random_clicker_score
            self.final_score = final_score

    class TaskSolution:
        def __init__(self, web_agent_id, actions, evaluation_result):
            self.web_agent_id = web_agent_id
            self.actions = actions
            self.evaluation_result = evaluation_result

    visualizer = SubnetVisualizer()

    # Example task
    task = Task(id="41b0f865-d1f1-47bb-8ab7-9572dea9ca4a", prompt="Navigate to the 'About Us' page.", tests=[CheckUrlTest(type="CheckUrlTest", url="/about/", description="Check URL")])

    # Example solutions
    task_solutions = [
        TaskSolution(web_agent_id="browser-agent-1", actions=[ClickAction(type="ClickAction", x=1711, y=978)], evaluation_result=EvaluationResult(raw_score=0.5, final_score=0.7)),
        TaskSolution(web_agent_id="browser-agent-2", actions=[ClickAction(type="ClickAction", x=1000, y=500)], evaluation_result=EvaluationResult(raw_score=0.2, final_score=0.3)),
    ]

    # Call the visualization function
    visualizer.show_list_of_evaluations(task=task, task_solutions=task_solutions, validator_id="test-validator")


if __name__ == "__main__":
    # test_visualization()
    test_multiple_evaluations()
