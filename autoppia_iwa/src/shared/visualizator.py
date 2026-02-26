import json
import os
from datetime import date, datetime, time as datetime_time
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

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    @staticmethod
    def _make_json_serializable(obj):
        """Convert non-JSON-serializable objects (datetime, date) to JSON-compatible types."""
        if isinstance(obj, datetime | date):
            return obj.isoformat()
        if isinstance(obj, datetime_time):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: SubnetVisualizer._make_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list | tuple):
            return [SubnetVisualizer._make_json_serializable(item) for item in obj]
        return obj

    # ============================================================================
    # TASK DISPLAY HELPERS
    # ============================================================================

    def _get_task_info(self, task):
        """Extract task information with fallbacks."""
        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"
        task_url = task.url if hasattr(task, "url") else "No URL available"
        return task_id, prompt, task_url

    def _get_test_json(self, test):
        """Get JSON representation of a test object."""
        if hasattr(test, "model_dump"):
            try:
                return test.model_dump(mode="json")
            except (TypeError, ValueError):
                return test.model_dump()
        if hasattr(test, "dict"):
            return test.dict()
        return vars(test)

    def _display_test_panel(self, test, idx):
        """Display a single test in a panel."""
        test_type = type(test).__name__
        test_json = self._get_test_json(test)
        test_json = self._make_json_serializable(test_json)
        json_str = json.dumps(test_json, indent=2, ensure_ascii=False)
        test_panel = Panel(f"[yellow]{json_str}[/yellow]", title=f"[bold cyan]Test #{idx + 1}: {test_type}[/bold cyan]", border_style="magenta", padding=(1, 2))
        self.console.print(test_panel)

    def show_task_with_tests(self, task):
        """
        Displays a task and its configured tests.
        """
        task_id, prompt, task_url = self._get_task_info(task)

        self.console.print("\n" + "=" * 80)

        task_content = f"{prompt}\n\n[dim]URL: {task_url}[/dim]"
        task_panel = Panel(task_content, title=f"[bold cyan]TASK: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 2))
        self.console.print(task_panel)

        if hasattr(task, "tests") and task.tests:
            self.console.print("\n[bold magenta]CONFIGURED TESTS:[/bold magenta]")
            for idx, test in enumerate(task.tests):
                self._display_test_panel(test, idx)
            self.console.print("-" * 80)

    # ============================================================================
    # EVALUATION DISPLAY HELPERS
    # ============================================================================

    def _display_task_panel(self, task):
        """Display task information in a panel."""
        task_id, prompt, task_url = self._get_task_info(task)
        task_content = f"{prompt}\n\n[dim]URL: {task_url}[/dim]"
        task_panel = Panel(task_content, title=f"[bold cyan]TASK: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 2))
        self.console.print(task_panel)

    def _display_actions_table(self, actions):
        """Display actions in a table."""
        if not actions:
            self.console.print("\n[yellow]No actions were executed[/yellow]")
            return

        actions_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
        actions_table.add_column("#", style="dim", width=4)
        actions_table.add_column("Type", style="cyan", width=18)
        actions_table.add_column("Details", style="green", overflow="fold", no_wrap=False)

        for idx, action in enumerate(actions):
            action_type = type(action).__name__ if hasattr(action, "__class__") else "Unknown"
            details = self._format_action_details(action)
            actions_table.add_row(str(idx + 1), action_type, details)

        actions_panel = Panel(actions_table, title="[bold green]ACTIONS EXECUTED[/bold green]", border_style="green", padding=(1, 1))
        self.console.print("\n")
        self.console.print(actions_panel)

    def _get_test_result_success(self, test_result):
        """Extract success status from test result."""
        if isinstance(test_result, dict):
            return test_result.get("success", False)
        return test_result.success

    def _display_tests_table(self, task, test_results):
        """Display tests and their results in a table."""
        has_tests = hasattr(task, "tests") and task.tests
        has_results = test_results and len(test_results) > 0

        if not (has_tests and has_results):
            self.console.print(f"DEBUG: task.tests = {task.tests}")
            self.console.print(f"DEBUG: test_results = {test_results}")
            self.console.print("\n[yellow]No configured tests or available results[/yellow]")
            return

        tests_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE, expand=True)
        tests_table.add_column("Test #", style="dim", width=6)
        tests_table.add_column("Type", style="cyan", width=22)
        tests_table.add_column("Description", style="yellow")
        tests_table.add_column("Result", style="bold", width=10)

        for idx, test in enumerate(task.tests):
            if idx >= len(test_results):
                continue

            test_result = test_results[idx]
            test_passed = self._get_test_result_success(test_result)
            test_type = type(test).__name__
            description, _ = self._get_detailed_test_description_and_attributes(test)

            result_text = "✅ PASS" if test_passed else "❌ FAIL"
            result_style = "green" if test_passed else "red"
            tests_table.add_row(str(idx + 1), test_type, description, Text(result_text, style=result_style))

        tests_panel = Panel(tests_table, title="[bold magenta]TESTS AND RESULTS[/bold magenta]", border_style="magenta", padding=(1, 1))
        self.console.print("\n")
        self.console.print(tests_panel)

    def _get_final_score(self, evaluation_result):
        """Extract final score from evaluation result."""
        if isinstance(evaluation_result, dict):
            return evaluation_result.get("final_score", 0.0)
        if hasattr(evaluation_result, "final_score"):
            return evaluation_result.final_score
        return 0.0

    def _display_scores_table(self, evaluation_result):
        """Display scores in a table."""
        if not evaluation_result:
            return

        scores_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
        scores_table.add_column("Type", style="yellow", justify="right", width=25)
        scores_table.add_column("Value", style="cyan", width=10)

        final_score = self._get_final_score(evaluation_result)
        score_style = "bold green" if final_score > 0.5 else "bold red"
        scores_table.add_row("Score:", Text(f"{final_score:.4f}", style=score_style))

        scores_panel = Panel(scores_table, title="[bold blue]SCORES[/bold blue]", border_style="blue", padding=(1, 1))
        self.console.print("\n")
        self.console.print(scores_panel)

    def _display_feedback_panel(self, feedback):
        """Display feedback information in a panel."""
        if not feedback:
            return

        feedback_content = f"""
    [bold]Tests passed:[/bold] {feedback.passed_tests}/{feedback.passed_tests + feedback.failed_tests}
    [bold]Total time:[/bold] {feedback.total_execution_time:.2f}s
        """
        feedback_panel = Panel(feedback_content, title="[bold green]ADDITIONAL FEEDBACK[/bold green]", border_style="green", padding=(1, 1))
        self.console.print("\n")
        self.console.print(feedback_panel)

    def show_full_evaluation(
        self,
        agent_id,
        validator_id,
        task,
        actions,
        test_results,
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
            test_results: List of test results
            evaluation_result: The evaluation result object
            feedback: Optional additional feedback
        """
        self.console.print("\n" + "=" * 80)
        self.console.print(f"\n[bold white on blue]COMPLETE EVALUATION - AGENT: {agent_id}, VALIDATOR:{validator_id}[/bold white on blue]\n")

        self._display_task_panel(task)
        self._display_actions_table(actions)
        self._display_tests_table(task, test_results)
        self._display_scores_table(evaluation_result)
        self._display_feedback_panel(feedback)

        self.console.print("\n" + "=" * 80)

    # ============================================================================
    # ACTION FORMATTING HELPERS
    # ============================================================================

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
                test_results=evaluation_result.test_results if hasattr(evaluation_result, "test_results") else [],
                evaluation_result=evaluation_result if evaluation_result else None,
                feedback=evaluation_result.feedback if hasattr(evaluation_result, "feedback") else None,
            )

        self.console.print("\n" + "=" * 100)
        self.console.print("[bold green]All evaluations completed![/bold green]")

    def _format_value_for_display(self, value):
        """Format a value for display in action details."""
        if isinstance(value, str):
            return f"'{value}'"
        return value

    def _format_pydantic_action_details(self, action_dict):
        """Format details from a Pydantic action dictionary."""
        details = ""
        exclude_keys = ["type"]
        for key, value in action_dict.items():
            if key not in exclude_keys and value:
                formatted_value = self._format_value_for_display(value)
                details += f"{key}={formatted_value}, "
        return details.rstrip(", ")

    def _format_regular_action_details(self, vars_dict):
        """Format details from a regular object's vars dictionary."""
        details = ""
        for key, value in vars_dict.items():
            if not key.startswith("_") and value:
                formatted_value = self._format_value_for_display(value)
                details += f"{key}={formatted_value}, "
        return details.rstrip(", ")

    def _format_action_details(self, action):
        """
        Formats the details of a single action for display in a readable manner.
        """
        if hasattr(action, "model_dump"):
            action_dict = action.model_dump()
            return self._format_pydantic_action_details(action_dict)
        if hasattr(action, "__dict__"):
            vars_dict = vars(action)
            return self._format_regular_action_details(vars_dict)
        return str(action)

    # ============================================================================
    # TEST DESCRIPTION HELPERS
    # ============================================================================

    def _get_check_url_test_description(self, test):
        """Get description for CheckUrlTest."""
        if hasattr(test, "url"):
            return f"Check navigation to URL: '{test.url}'", test.url
        if hasattr(test, "expected_url"):
            return f"Check navigation to URL: '{test.expected_url}'", test.expected_url
        if hasattr(test, "url_pattern"):
            return f"Check URL pattern: '{test.url_pattern}'", test.url_pattern
        return "", None

    def _get_find_in_html_test_description(self, test):
        """Get description for FindInHtmlTest."""
        if hasattr(test, "content"):
            return f"Find in HTML next substring:: '{test.content}'", test.content
        return "", None

    def _get_html_test_description(self, test):
        """Get description for HTML-based tests."""
        if hasattr(test, "success_criteria"):
            criteria = test.success_criteria
            if len(criteria) > 60:
                criteria = criteria[:57] + "..."
            return f"Success criteria: '{criteria}'", test.success_criteria
        if hasattr(test, "query"):
            return f"Query: '{test.query}'", test.query
        return "", ""

    def _get_event_test_description(self, test):
        """Get description for event tests."""
        if hasattr(test, "event_name"):
            return f"Check backend event: '{test.event_name}'", test.event_name
        return "", None

    def _get_description_from_priority_attrs(self, test):
        """Try to get description from priority attributes."""
        priority_attrs = ["description", "text", "expected", "target", "selector"]
        for attr in priority_attrs:
            if hasattr(test, attr) and getattr(test, attr):
                value = getattr(test, attr)
                if isinstance(value, str) and len(value) > 60:
                    value = value[:57] + "..."
                return f"{attr.capitalize()}: '{value}'"
        return ""

    def _get_description_from_all_attrs(self, test, test_type):
        """Get description from all relevant attributes."""
        all_attrs = []
        for attr_name, attr_value in vars(test).items():
            if not attr_name.startswith("_") and attr_value and attr_name not in ["type"]:
                all_attrs.append(f"{attr_name}='{attr_value}'")
        if all_attrs:
            return ", ".join(all_attrs)
        return f"Test type {test_type}"

    def _process_specific_test_type(self, test, test_type):
        """Process specific test types and return description and attributes."""
        description = ""
        attributes = {}

        if test_type == "CheckUrlTest":
            description, url_value = self._get_check_url_test_description(test)
            if url_value:
                attributes["url"] = url_value
        elif test_type == "FindInHtmlTest":
            description, content_value = self._get_find_in_html_test_description(test)
            if content_value:
                attributes["content"] = content_value
        elif "HTML" in test_type or test_type in ["JudgeBaseOnHTML", "OpinionBasedHTMLTest", "JudgeBaseOnScreenshot"]:
            description, criteria_value = self._get_html_test_description(test)
            if criteria_value:
                attributes["success_criteria"] = criteria_value
        elif "Event" in test_type or test_type == "CheckEventTest":
            description, event_name = self._get_event_test_description(test)
            if event_name:
                attributes["event_name"] = event_name

        return description, attributes

    def _get_detailed_test_description_and_attributes(self, test):
        """
        Extracts a specific, detailed description of the test based on its type and attributes.
        """
        test_type = type(test).__name__
        description, attributes = self._process_specific_test_type(test, test_type)

        if not description:
            description = self._get_description_from_priority_attrs(test)

        if not description:
            description = self._get_description_from_all_attrs(test, test_type)

        return description, str(attributes)

    # ============================================================================
    # SUMMARY HELPERS
    # ============================================================================

    def _calculate_scores(self, scores):
        """Calculate average and max scores from a list."""
        if not scores:
            return 0.0, 0.0
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        return avg_score, max_score

    def _display_summary_table(self, results, agents):
        """Display the main summary table."""
        summary_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD, expand=True)
        summary_table.add_column("Agent", style="cyan")
        summary_table.add_column("Tasks", style="dim")
        summary_table.add_column("Average Score", style="green")
        summary_table.add_column("Max Score", style="yellow")

        for agent in agents:
            scores = results[agent.id]["global_scores"]
            avg_score, max_score = self._calculate_scores(scores)
            summary_table.add_row(agent.id, str(len(scores)), f"{avg_score:.4f}", f"{max_score:.4f}")

        self.console.print(summary_table)

    def _display_project_details(self, results, agents):
        """Display project details for each agent."""
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

                avg_score, max_score = self._calculate_scores(scores)
                project_table.add_row(project_name, str(len(scores)), f"{avg_score:.4f}", f"{max_score:.4f}")

            self.console.print(project_table)

    def print_summary(self, results, agents):
        """
        Prints a performance summary for each agent.
        """
        self.console.print("\n" + "=" * 80)
        self.console.print(Align.center("[bold white on blue]PERFORMANCE SUMMARY[/bold white on blue]"))
        self.console.print("=" * 80 + "\n")

        self._display_summary_table(results, agents)
        self._display_project_details(results, agents)

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
                test_results=result.test_results if hasattr(result, "test_results") else [],
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
    test_results_list = test_results_matrix[0] if test_results_matrix else []
    visualizer.show_full_evaluation(agent_id=agent_id, validator_id="test", task=task, actions=actions, test_results=test_results_list, evaluation_result=evaluation_result)


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

    class EvaluationResult:
        def __init__(self, raw_score=0.0, final_score=0.0):
            self.raw_score = raw_score
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

    # Create evaluation results list
    evaluation_results = [sol.evaluation_result for sol in task_solutions]

    # Call the visualization function
    visualizer.show_list_of_evaluations(task=task, task_solutions=task_solutions, evaluation_results=evaluation_results, validator_id="test-validator")


if __name__ == "__main__":
    # test_visualization()
    test_multiple_evaluations()
