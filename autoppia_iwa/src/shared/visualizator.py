import os
from typing import Any, Dict, List, Optional

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class SubnetVisualizer:
    """
    Enhanced visualizer for Subnet 36 that displays:
    1. Task with its prompt
    2. Associated tests with detailed information
    3. Agent actions
    4. Test results (✅/❌)
    5. Scores
    """

    def __init__(self, log_directory: Optional[str] = None):
        """
        Initialize the visualizer.

        Args:
            log_directory (Optional[str]): Directory to save logs. If None, logs are not saved.
        """
        self.console = Console()
        if log_directory:
            os.makedirs(log_directory, exist_ok=True)
        self.log_directory = log_directory

    def show_task_with_tests(self, task: Any) -> None:
        """
        Display a task and its configured tests.

        Args:
            task (Any): The task to display.
        """
        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"

        self.console.print("\n" + "=" * 80)

        task_panel = Panel(prompt, title=f"[bold cyan]TASK: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 2))
        self.console.print(task_panel)

        if hasattr(task, "tests") and task.tests:
            self._display_tests_table(task.tests)

    def _display_tests_table(self, tests: List[Any]) -> None:
        """
        Display a table of configured tests.

        Args:
            tests (List[Any]): List of tests to display.
        """
        tests_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        tests_table.add_column("Test #", style="dim", width=6)
        tests_table.add_column("Type", style="cyan", width=22)
        tests_table.add_column("Description", style="yellow")

        for idx, test in enumerate(tests):
            test_type = type(test).__name__
            description = self._get_detailed_test_description(test)
            tests_table.add_row(str(idx + 1), test_type, description)

        self.console.print("\n[bold magenta]CONFIGURED TESTS:[/bold magenta]")
        self.console.print(tests_table)
        self.console.print("-" * 80)

    def show_agent_evaluation(self, agent_id: str, task: Any, actions: List[Any], test_results_matrix: List[List[Any]], evaluation_result: Optional[Any] = None) -> None:
        """
        Display the evaluation results for a specific agent.

        Args:
            agent_id (str): The ID of the agent.
            task (Any): The task being evaluated.
            actions (List[Any]): List of actions performed by the agent.
            test_results_matrix (List[List[Any]]): Matrix of test results.
            evaluation_result (Optional[Any]): The evaluation result.
        """
        self.console.print(f"\n[bold white on blue]AGENT EVALUATION: {agent_id}[/bold white on blue]\n")

        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"

        task_panel = Panel(prompt, title=f"[bold cyan]TASK: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 1))
        self.console.print(task_panel)

        self._display_actions_table(actions)
        self._display_test_results_table(task, test_results_matrix)

        if evaluation_result:
            self._display_scores_table(evaluation_result)

        self.console.print("\n" + "=" * 80)

    def _display_actions_table(self, actions: List[Any]) -> None:
        """
        Display a table of actions performed by the agent.

        Args:
            actions (List[Any]): List of actions to display.
        """
        actions_table = Table(title="[bold green]EXECUTED ACTIONS[/bold green]", show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
        actions_table.add_column("#", style="dim", width=4)
        actions_table.add_column("Type", style="cyan", width=18)
        actions_table.add_column("Details", style="green")

        for idx, action in enumerate(actions):
            action_type = type(action).__name__ if hasattr(action, "__class__") else "Unknown"
            details = self._format_action_details(action)
            actions_table.add_row(str(idx + 1), action_type, details)

        self.console.print("\n")
        self.console.print(actions_table)

    def _display_test_results_table(self, task: Any, test_results_matrix: List[List[Any]]) -> None:
        """
        Display a table of test results.

        Args:
            task (Any): The task being evaluated.
            test_results_matrix (List[List[Any]]): Matrix of test results.
        """
        if not test_results_matrix or not test_results_matrix[0]:
            return

        results_table = Table(title="[bold yellow]TEST RESULTS[/bold yellow]", show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
        results_table.add_column("Test #", style="dim", width=6)
        results_table.add_column("Type", style="cyan", width=22)
        results_table.add_column("Description", style="yellow")
        results_table.add_column("Result", style="bold", width=10)

        num_tests = len(test_results_matrix[0])

        for test_idx in range(num_tests):
            test_passed = any(test_results_matrix[action_idx][test_idx].success for action_idx in range(len(test_results_matrix)))

            test_type = "Unknown"
            description = ""

            if hasattr(task, "tests") and test_idx < len(task.tests):
                test = task.tests[test_idx]
                test_type = type(test).__name__
                description = self._get_detailed_test_description(test)

            result_text = "✅ PASS" if test_passed else "❌ FAIL"
            result_style = "green" if test_passed else "red"

            results_table.add_row(str(test_idx + 1), test_type, description, Text(result_text, style=result_style))

        self.console.print("\n")
        self.console.print(results_table)

    def _display_scores_table(self, evaluation_result: Any) -> None:
        """
        Display a table of scores.

        Args:
            evaluation_result (Any): The evaluation result.
        """
        scores_table = Table(title="[bold blue]SCORES[/bold blue]", show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
        scores_table.add_column("Type", style="yellow", justify="right", width=25)
        scores_table.add_column("Value", style="cyan", width=10)

        raw_score = evaluation_result.raw_score if hasattr(evaluation_result, "raw_score") else 0.0
        random_score = evaluation_result.random_clicker_score if hasattr(evaluation_result, "random_clicker_score") else 0.0
        final_score = evaluation_result.final_score if hasattr(evaluation_result, "final_score") else 0.0

        scores_table.add_row("Raw Score:", f"{raw_score:.4f}")
        scores_table.add_row("Random Clicker Score:", f"{random_score:.4f}")
        scores_table.add_row("Adjusted Score:", Text(f"{final_score:.4f}", style="bold green" if final_score > 0.5 else "bold red"))

        self.console.print("\n")
        self.console.print(scores_table)

    def _format_action_details(self, action: Any) -> str:
        """
        Format the details of an action for display.

        Args:
            action (Any): The action to format.

        Returns:
            str: Formatted action details.
        """
        details = ""
        if hasattr(action, "model_dump"):
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

    def _get_detailed_test_description(self, test: Any) -> str:
        """
        Extract a detailed description of the test based on its type and attributes.

        Args:
            test (Any): The test to describe.

        Returns:
            str: Detailed description of the test.
        """
        description = ""
        test_type = type(test).__name__

        if test_type == "CheckUrlTest":
            if hasattr(test, "url"):
                description = f"Verify navigation to URL: '{test.url}'"
            elif hasattr(test, "expected_url"):
                description = f"Verify navigation to URL: '{test.expected_url}'"
            elif hasattr(test, "url_pattern"):
                description = f"Verify URL pattern: '{test.url_pattern}'"

        elif "HTML" in test_type or test_type == "JudgeBaseOnHTML" or test_type == "OpinionBasedHTMLTest":
            if hasattr(test, "success_criteria"):
                criteria = test.success_criteria
                if len(criteria) > 60:
                    criteria = criteria[:57] + "..."
                description = f"Success criteria: '{criteria}'"
            elif hasattr(test, "query"):
                description = f"Query: '{test.query}'"

        elif "Event" in test_type or test_type == "CheckEventTest":
            if hasattr(test, "event_name"):
                description = f"Verify backend event: '{test.event_name}'"
            elif hasattr(test, "event_type"):
                description = f"Verify event type: '{test.event_type}'"

        elif test_type == "CheckPageViewEventTest":
            if hasattr(test, "url_path"):
                description = f"Verify page access: '{test.url_path}'"
            elif hasattr(test, "page_name"):
                description = f"Verify page view: '{test.page_name}'"

        if not description:
            priority_attrs = ["description", "text", "expected", "target", "selector"]
            for attr in priority_attrs:
                if hasattr(test, attr) and getattr(test, attr):
                    value = getattr(test, attr)
                    if isinstance(value, str) and len(value) > 60:
                        value = value[:57] + "..."
                    description = f"{attr.capitalize()}: '{value}'"
                    break

            if not description:
                all_attrs = []
                for attr_name, attr_value in vars(test).items():
                    if not attr_name.startswith("_") and attr_value and attr_name not in ["type"]:
                        if isinstance(attr_value, str) and len(attr_value) > 30:
                            attr_value = attr_value[:27] + "..."
                        all_attrs.append(f"{attr_name}='{attr_value}'")

                if all_attrs:
                    description = ", ".join(all_attrs)
                else:
                    description = f"Test type {test_type}"

        return description

    def print_summary(self, results: Dict[str, Any], agents: List[Any]) -> None:
        """
        Print a performance summary for each agent.

        Args:
            results (Dict[str, Any]): Dictionary of results.
            agents (List[Any]): List of agents.
        """
        self.console.print("\n" + "=" * 80)
        self.console.print(Align.center("[bold white on blue]PERFORMANCE SUMMARY[/bold white on blue]"))
        self.console.print("=" * 80 + "\n")

        summary_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
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

        for agent in agents:
            if not results[agent.id]["projects"]:
                continue

            self.console.print(f"\n[bold cyan]Project Details - Agent: {agent.id}[/bold cyan]")

            project_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
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


# Decorators for integration into the benchmark


def visualize_task(visualizer: SubnetVisualizer):
    """
    Decorator to visualize a task and its tests.

    Args:
        visualizer (SubnetVisualizer): The visualizer instance.
    """

    def decorator(func):
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


def visualize_evaluation(visualizer: SubnetVisualizer):
    """
    Decorator to visualize the evaluation of an agent.

    Args:
        visualizer (SubnetVisualizer): The visualizer instance.
    """

    def decorator(func):
        async def wrapper(web_project, task, task_solution, *args, **kwargs):
            result = await func(web_project, task, task_solution, *args, **kwargs)
            visualizer.show_agent_evaluation(
                agent_id=task_solution.web_agent_id,
                task=task,
                actions=task_solution.actions,
                test_results_matrix=result.test_results_matrix if hasattr(result, "test_results_matrix") else [],
                evaluation_result=result,
            )
            return result

        return wrapper

    return decorator


def visualize_summary(visualizer: SubnetVisualizer):
    """
    Decorator to visualize the final summary.

    Args:
        visualizer (SubnetVisualizer): The visualizer instance.
    """

    def decorator(func):
        def wrapper(results, agents, *args, **kwargs):
            func(results, agents, *args, **kwargs)
            visualizer.print_summary(results, agents)
            return None

        return wrapper

    return decorator
