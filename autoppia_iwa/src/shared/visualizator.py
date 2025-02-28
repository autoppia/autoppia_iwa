import os
from typing import Optional

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class SubnetVisualizer:
    """
    Visualizador mejorado para Subnet 36 que muestra:
    1. Tarea con su prompt
    2. Tests asociados con información detallada
    3. Acciones del agente
    4. Resultados de tests (✅/❌)
    5. Puntuaciones
    """

    def __init__(self, log_directory: Optional[str] = None):
        self.console = Console()
        if log_directory:
            os.makedirs(log_directory, exist_ok=True)
        self.log_directory = log_directory

    def show_task_with_tests(self, task):
        """Muestra una tarea y sus tests configurados"""
        # Panel para mostrar el prompt de la tarea
        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"

        self.console.print("\n" + "=" * 80)

        task_panel = Panel(prompt, title=f"[bold cyan]TAREA: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 2))
        self.console.print(task_panel)

        # Tabla de tests configurados
        if hasattr(task, "tests") and task.tests:
            tests_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
            tests_table.add_column("Test #", style="dim", width=6)
            tests_table.add_column("Tipo", style="cyan", width=22)
            tests_table.add_column("Descripción", style="yellow")

            for idx, test in enumerate(task.tests):
                test_type = type(test).__name__
                description = self._get_detailed_test_description(test)
                tests_table.add_row(str(idx + 1), test_type, description)

            self.console.print("\n[bold magenta]TESTS CONFIGURADOS:[/bold magenta]")
            self.console.print(tests_table)
            self.console.print("-" * 80)

    def show_agent_evaluation(self, agent_id, task, actions, test_results_matrix, evaluation_result=None):
        """Muestra los resultados de evaluación para un agente específico"""
        self.console.print(f"\n[bold white on blue]EVALUACIÓN AGENTE: {agent_id}[/bold white on blue]\n")

        # Mostrar prompt de la tarea
        task_id = task.id if hasattr(task, "id") else "Unknown"
        prompt = task.prompt if hasattr(task, "prompt") else "No prompt available"

        task_panel = Panel(prompt, title=f"[bold cyan]TAREA: {task_id}[/bold cyan]", border_style="cyan", padding=(1, 1))
        self.console.print(task_panel)

        # Tabla de acciones
        actions_table = Table(title="[bold green]ACCIONES EJECUTADAS[/bold green]", show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
        actions_table.add_column("#", style="dim", width=4)
        actions_table.add_column("Tipo", style="cyan", width=18)
        actions_table.add_column("Detalles", style="green")

        for idx, action in enumerate(actions):
            action_type = type(action).__name__ if hasattr(action, "__class__") else "Unknown"
            details = self._format_action_details(action)
            actions_table.add_row(str(idx + 1), action_type, details)

        self.console.print("\n")
        self.console.print(actions_table)

        # Tabla de resultados de tests
        if test_results_matrix and len(test_results_matrix) > 0:
            results_table = Table(title="[bold yellow]RESULTADOS DE TESTS[/bold yellow]", show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
            results_table.add_column("Test #", style="dim", width=6)
            results_table.add_column("Tipo", style="cyan", width=22)
            results_table.add_column("Descripción", style="yellow")
            results_table.add_column("Resultado", style="bold", width=10)

            num_tests = len(test_results_matrix[0]) if test_results_matrix[0] else 0

            for test_idx in range(num_tests):
                # Verificar si el test pasó en alguna acción
                test_passed = False
                for action_idx in range(len(test_results_matrix)):
                    if test_results_matrix[action_idx][test_idx].success:
                        test_passed = True
                        break

                test_type = "Unknown"
                description = ""

                # Obtener información del test
                if hasattr(task, "tests") and test_idx < len(task.tests):
                    test = task.tests[test_idx]
                    test_type = type(test).__name__
                    description = self._get_detailed_test_description(test)

                result_text = "✅ PASS" if test_passed else "❌ FAIL"
                result_style = "green" if test_passed else "red"

                results_table.add_row(str(test_idx + 1), test_type, description, Text(result_text, style=result_style))

            self.console.print("\n")
            self.console.print(results_table)

        # Mostrar puntuaciones
        if evaluation_result:
            scores_table = Table(title="[bold blue]PUNTUACIONES[/bold blue]", show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
            scores_table.add_column("Tipo", style="yellow", justify="right", width=25)
            scores_table.add_column("Valor", style="cyan", width=10)

            raw_score = evaluation_result.raw_score if hasattr(evaluation_result, "raw_score") else 0.0
            random_score = evaluation_result.random_clicker_score if hasattr(evaluation_result, "random_clicker_score") else 0.0
            final_score = evaluation_result.final_score if hasattr(evaluation_result, "final_score") else 0.0

            scores_table.add_row("Raw Score:", f"{raw_score:.4f}")
            scores_table.add_row("Random Clicker Score:", f"{random_score:.4f}")
            scores_table.add_row("Adjusted Score:", Text(f"{final_score:.4f}", style="bold green" if final_score > 0.5 else "bold red"))

            self.console.print("\n")
            self.console.print(scores_table)

        # Separador
        self.console.print("\n" + "=" * 80)

    def _format_action_details(self, action):
        """Formatea los detalles de una acción para mostrarlos de forma legible"""
        details = ""
        if hasattr(action, "model_dump"):
            # Para acciones Pydantic
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
            # Para objetos regulares
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

    def _get_detailed_test_description(self, test):
        """
        Extrae una descripción detallada y específica del test
        basada en su tipo y atributos
        """
        description = ""
        test_type = type(test).__name__

        # Mostrar información específica por tipo de test
        if test_type == "CheckUrlTest":
            # Para tests de URL, mostrar la URL o path esperado
            if hasattr(test, "url"):
                description = f"Verificar navegación a URL: '{test.url}'"
            elif hasattr(test, "expected_url"):
                description = f"Verificar navegación a URL: '{test.expected_url}'"
            elif hasattr(test, "url_pattern"):
                description = f"Verificar patrón de URL: '{test.url_pattern}'"

        elif "HTML" in test_type or test_type == "JudgeBaseOnHTML" or test_type == "OpinionBasedHTMLTest":
            # Para tests de opinión HTML, mostrar el criterio de éxito
            if hasattr(test, "success_criteria"):
                criteria = test.success_criteria
                if len(criteria) > 60:
                    criteria = criteria[:57] + "..."
                description = f"Criterio de éxito: '{criteria}'"
            elif hasattr(test, "query"):
                description = f"Consulta: '{test.query}'"

        elif "Event" in test_type or test_type == "CheckEventTest":
            # Para tests de eventos, mostrar el nombre del evento
            if hasattr(test, "event_name"):
                description = f"Verificar evento backend: '{test.event_name}'"
            elif hasattr(test, "event_type"):
                description = f"Verificar tipo de evento: '{test.event_type}'"

        elif test_type == "CheckPageViewEventTest":
            # Para tests de eventos de vista de página
            if hasattr(test, "url_path"):
                description = f"Verificar acceso a página: '{test.url_path}'"
            elif hasattr(test, "page_name"):
                description = f"Verificar vista de página: '{test.page_name}'"

        # Si no se ha generado descripción con los casos específicos, intentar extraer atributos importantes
        if not description:
            # Verificar otros atributos comunes
            priority_attrs = ["description", "text", "expected", "target", "selector"]
            for attr in priority_attrs:
                if hasattr(test, attr) and getattr(test, attr):
                    value = getattr(test, attr)
                    if isinstance(value, str) and len(value) > 60:
                        value = value[:57] + "..."
                    description = f"{attr.capitalize()}: '{value}'"
                    break

            # Si todavía no hay descripción, intentar mostrar todos los atributos relevantes
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
                    # Si no se encontraron atributos, usar el tipo de test
                    description = f"Test tipo {test_type}"

        return description

    def print_summary(self, results, agents):
        """Imprime un resumen de rendimiento por agente"""
        self.console.print("\n" + "=" * 80)
        self.console.print(Align.center("[bold white on blue]RESUMEN DE RENDIMIENTO[/bold white on blue]"))
        self.console.print("=" * 80 + "\n")

        summary_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
        summary_table.add_column("Agente", style="cyan")
        summary_table.add_column("Tareas", style="dim")
        summary_table.add_column("Puntuación Media", style="green")
        summary_table.add_column("Puntuación Máxima", style="yellow")

        for agent in agents:
            scores = results[agent.id]["global_scores"]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0

            summary_table.add_row(agent.id, str(len(scores)), f"{avg_score:.4f}", f"{max_score:.4f}")

        self.console.print(summary_table)

        # Detalles por proyecto
        for agent in agents:
            if not results[agent.id]["projects"]:
                continue

            self.console.print(f"\n[bold cyan]Detalles por Proyecto - Agente: {agent.id}[/bold cyan]")

            project_table = Table(show_header=True, header_style="bold", box=box.SIMPLE_HEAD)
            project_table.add_column("Proyecto", style="magenta")
            project_table.add_column("Tareas", style="dim")
            project_table.add_column("Puntuación Media", style="green")
            project_table.add_column("Puntuación Máxima", style="yellow")

            for project_name, scores in results[agent.id]["projects"].items():
                if not scores:
                    continue

                avg_score = sum(scores) / len(scores)
                max_score = max(scores)

                project_table.add_row(project_name, str(len(scores)), f"{avg_score:.4f}", f"{max_score:.4f}")

            self.console.print(project_table)

        self.console.print("\n" + "=" * 80)


# Decoradores para integrar en el benchmark


def visualize_task(visualizer):
    """Decorator para visualizar una tarea y sus tests"""

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


def visualize_evaluation(visualizer):
    """Decorator para visualizar la evaluación de un agente"""

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


def visualize_summary(visualizer):
    """Decorator para visualizar el resumen final"""

    def decorator(func):
        def wrapper(results, agents, *args, **kwargs):
            func(results, agents, *args, **kwargs)
            visualizer.print_summary(results, agents)
            return None

        return wrapper

    return decorator
