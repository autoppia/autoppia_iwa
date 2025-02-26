import os
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text


class SimpleSubnetVisualizer:
    """
    Visualizador simple para la evaluación de tareas de Subnet 36 Web Agents.
    Muestra información clara sobre las tareas, acciones y resultados de tests.
    """

    def __init__(self, log_directory: Optional[str] = None):
        self.console = Console()
        self.log_directory = log_directory

        # Si se proporciona directorio para logs, asegurarse que existe
        if self.log_directory:
            os.makedirs(self.log_directory, exist_ok=True)

    def print_evaluation_summary(self, task, agent_id, actions, test_results_matrix):
        """
        Imprime un resumen de la evaluación para un agente en una tarea específica.

        Args:
            task: La tarea evaluada
            agent_id: ID del agente que realizó la tarea
            actions: Lista de acciones ejecutadas
            test_results_matrix: Matriz de resultados de tests
        """
        # Panel para la tarea
        task_panel = Panel(
            f"{task.prompt}",
            title=f"[bold cyan]Tarea: {task.id}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(task_panel)

        # Información de las acciones del agente
        agent_panel = Panel(
            self._create_actions_table(agent_id, actions),
            title=f"[bold green]Agente: {agent_id}[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(agent_panel)

        # Tabla de resultados de tests
        tests_table = self._create_tests_table(task, test_results_matrix)
        self.console.print(tests_table)

        # Línea divisoria para separar tareas
        self.console.print("─" * 100)
        self.console.print()

        # Guardar log si está configurado
        if self.log_directory:
            self._log_evaluation(task, agent_id, actions, test_results_matrix)

    def _create_actions_table(self, agent_id, actions):
        """Crea una tabla con las acciones ejecutadas por el agente."""
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Tipo", style="cyan")
        table.add_column("Detalles", style="green")

        for i, action in enumerate(actions):
            # Extraer tipo de acción
            action_type = type(action).__name__ if hasattr(action, "__class__") else "Unknown"

            # Generar detalles legibles de la acción
            details = ""
            if hasattr(action, "model_dump"):
                # Para acciones Pydantic
                action_dict = action.model_dump()
                # Excluir campos comunes o no informativos
                exclude_keys = ["type"]
                for key, value in action_dict.items():
                    if key not in exclude_keys and value:
                        if isinstance(value, str) and len(value) > 30:
                            value = value[:27] + "..."
                        details += f"{key}={value}, "
                details = details.rstrip(", ")
            elif hasattr(action, "__dict__"):
                # Para objetos regulares
                vars_dict = vars(action)
                for key, value in vars_dict.items():
                    if not key.startswith("_") and value:
                        if isinstance(value, str) and len(value) > 30:
                            value = value[:27] + "..."
                        details += f"{key}={value}, "
                details = details.rstrip(", ")
            else:
                details = str(action)

            table.add_row(str(i + 1), action_type, details)

        return table

    def _create_tests_table(self, task, test_results_matrix):
        """Crea una tabla con los resultados de los tests."""
        table = Table(title="Resultados de Tests", box=box.SIMPLE_HEAD)
        table.add_column("Test #", style="dim", width=6)
        table.add_column("Tipo", style="cyan")
        table.add_column("Descripción", style="yellow")
        table.add_column("Resultado", style="bold")

        # Procesar la matriz de resultados de tests
        # La matriz tiene una fila por cada acción y una columna por cada test
        if test_results_matrix and len(test_results_matrix) > 0:
            # Determinar cuántos tests hay (número de columnas)
            num_tests = len(test_results_matrix[0]) if test_results_matrix[0] else 0

            for test_idx in range(num_tests):
                # Verificar si el test pasó en alguna acción
                test_passed = False
                for action_idx in range(len(test_results_matrix)):
                    if test_results_matrix[action_idx][test_idx].success:
                        test_passed = True
                        break

                # Obtener información del test del primer resultado
                test_result = test_results_matrix[0][test_idx]
                test_type = type(test_result).__name__

                # Intentar obtener una descripción para el test
                description = ""
                if hasattr(task, "tests") and len(task.tests) > test_idx:
                    test = task.tests[test_idx]
                    if hasattr(test, "description"):
                        description = test.description
                    elif hasattr(test, "event_name"):
                        description = f"Verificar evento: {test.event_name}"
                    elif hasattr(test, "url_path"):
                        description = f"Verificar URL: {test.url_path}"
                    elif hasattr(test, "text"):
                        description = f"Verificar texto: {test.text[:30]}..." if len(test.text) > 30 else f"Verificar texto: {test.text}"

                # Si no tenemos descripción, intentar extraer datos del resultado
                if not description and hasattr(test_result, "extra_data"):
                    extra_data = test_result.extra_data
                    if isinstance(extra_data, dict):
                        for key, value in extra_data.items():
                            if key not in ["type", "success"]:
                                if isinstance(value, str) and len(value) > 30:
                                    value = value[:27] + "..."
                                description += f"{key}: {value}, "
                        description = description.rstrip(", ")

                # Colorear el resultado según pasó o falló
                result_text = "✅ PASSED" if test_passed else "❌ FAILED"
                result_style = "green" if test_passed else "red"

                table.add_row(
                    str(test_idx + 1),
                    test_type,
                    description,
                    Text(result_text, style=result_style)
                )

        return table

    def _log_evaluation(self, task, agent_id, actions, test_results_matrix):
        """Guarda un log de la evaluación en un archivo JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_directory, f"eval_{task.id}_{agent_id}_{timestamp}.json")

        # Preparar datos para el log
        log_data = {
            "timestamp": timestamp,
            "task_id": task.id,
            "task_prompt": task.prompt,
            "agent_id": agent_id,
            "url": task.url
        }

        # Agregar acciones
        log_data["actions"] = []
        for i, action in enumerate(actions):
            if hasattr(action, "model_dump"):
                log_data["actions"].append(action.model_dump())
            elif hasattr(action, "__dict__"):
                log_data["actions"].append(vars(action))
            else:
                log_data["actions"].append(str(action))

        # Agregar resultados de tests
        log_data["test_results"] = []
        if test_results_matrix and len(test_results_matrix) > 0:
            num_tests = len(test_results_matrix[0]) if test_results_matrix[0] else 0

            for test_idx in range(num_tests):
                # Verificar si el test pasó en alguna acción
                test_passed = False
                for action_idx in range(len(test_results_matrix)):
                    if test_results_matrix[action_idx][test_idx].success:
                        test_passed = True
                        break

                # Obtener información del test del primer resultado
                test_result = test_results_matrix[0][test_idx]
                test_type = type(test_result).__name__

                # Intentar obtener una descripción para el test
                description = ""
                if hasattr(task, "tests") and len(task.tests) > test_idx:
                    test = task.tests[test_idx]
                    if hasattr(test, "description"):
                        description = test.description
                    elif hasattr(test, "event_name"):
                        description = f"Verificar evento: {test.event_name}"
                    elif hasattr(test, "url_path"):
                        description = f"Verificar URL: {test.url_path}"
                    elif hasattr(test, "text"):
                        text_value = test.text
                        description = f"Verificar texto: {text_value[:30]}..." if len(text_value) > 30 else f"Verificar texto: {text_value}"

                log_data["test_results"].append({
                    "test_index": test_idx,
                    "test_type": test_type,
                    "description": description,
                    "passed": test_passed
                })

        # Guardar el log
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)


# Decorator para integrar el visualizador en el flujo de evaluación
def visualize_evaluation(visualizer: SimpleSubnetVisualizer):
    """
    Decorador para visualizar el proceso de evaluación de tareas.

    Args:
        visualizer: Instancia de SimpleSubnetVisualizer

    Returns:
        Función decorada
    """
    def decorator(func):
        async def wrapper(task, task_solution, *args, **kwargs):
            # Ejecutar la función original de evaluación
            result = await func(task, task_solution, *args, **kwargs)

            # Visualizar el resultado
            visualizer.print_evaluation_summary(
                task=task,
                agent_id=task_solution.web_agent_id,
                actions=task_solution.actions,
                test_results_matrix=result.test_results_matrix if hasattr(result, "test_results_matrix") else []
            )

            return result
        return wrapper
    return decorator
