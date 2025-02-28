import asyncio
import statistics
import json
import os
import time
from typing import List, Dict, Optional
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

# Importar el visualizador
from autoppia_iwa.src.shared.visualizator import (
    SubnetVisualizer, 
    visualize_task,
    visualize_evaluation,
    visualize_summary
)

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

# Configuración de directorios
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = "results"
LOG_DIR = os.path.join("logs", f"benchmark_{timestamp}")
TASKS_CACHE_DIR = "data/tasks_cache"

# Configuración de caching
USE_CACHED_TASKS = False  # Usar tareas cacheadas si están disponibles

# Configuración del benchmark
ITERATIONS = 1  # Número de iteraciones por tarea

# Inicializar componentes principales
app = AppBootstrap()
visualizer = SubnetVisualizer(log_directory=LOG_DIR)

# Agentes a evaluar
AGENTS: List[BaseAgent] = [
    RandomClickerWebAgent(name="Random-clicker"),
    # ApifiedWebAgent(name="Text-External-Agent", host="localhost", port=9000)
]

# ============================================================
# FUNCIONES DE MANEJO DE TAREAS CACHEADAS
# ============================================================


def get_cache_filename(project: WebProject) -> str:
    """
    Genera un nombre de archivo de caché específico para un proyecto.

    Args:
        project (WebProject): El proyecto web

    Returns:
        str: Ruta al archivo de caché para este proyecto específico
    """
    # Crear directorio de caché si no existe
    os.makedirs(TASKS_CACHE_DIR, exist_ok=True)

    # Usar el nombre o ID del proyecto para crear un nombre de archivo único
    safe_name = project.name.replace(" ", "_").lower()
    return os.path.join(TASKS_CACHE_DIR, f"{safe_name}_tasks.json")


async def load_tasks_from_json(project: WebProject) -> Optional[List[Task]]:
    """
    Carga tareas desde un archivo JSON específico del proyecto.

    Args:
        project (WebProject): Proyecto a asociar con las tareas cargadas

    Returns:
        List[Task]: Lista de objetos Task deserializados o None si no se encuentra/no es válido
    """
    filename = get_cache_filename(project)
    if not os.path.exists(filename):
        print(f"Archivo de caché {filename} no encontrado para el proyecto '{project.name}'")
        return None

    try:
        with open(filename, 'r') as f:
            cache_data = json.load(f)

        # Verificar que esta caché pertenezca al proyecto solicitado
        if cache_data.get("project_id") != project.id and cache_data.get("project_name") != project.name:
            print(f"Archivo de caché existe pero para un proyecto diferente. Esperado '{project.name}', encontrado '{cache_data.get('project_name')}'")
            return None

        # Deserializar las tareas
        tasks = [Task.deserialize(task_data) for task_data in cache_data.get("tasks", [])]

        print(f"Cargadas {len(tasks)} tareas para el proyecto '{project.name}' desde {filename}")
        return tasks
    except Exception as e:
        print(f"Error al cargar tareas desde {filename}: {str(e)}")
        return None


async def save_tasks_to_json(project: WebProject, tasks: List[Task]) -> bool:
    """
    Guarda las tareas en un archivo JSON específico del proyecto.

    Args:
        project (WebProject): El proyecto asociado con las tareas
        tasks (List[Task]): Lista de tareas a guardar

    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    filename = get_cache_filename(project)

    try:
        cache_data = {
            "project_id": project.id,
            "project_name": project.name,
            "created_at": datetime.now().isoformat(),
            "tasks": [task.serialize() for task in tasks]
        }

        with open(filename, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"Guardadas {len(tasks)} tareas para el proyecto '{project.name}' en {filename}")
        return True
    except Exception as e:
        print(f"Error al guardar tareas en {filename}: {str(e)}")
        return False

# ============================================================
# FUNCIONES DE GENERACIÓN DE TAREAS Y TESTS
# ============================================================


async def generate_tasks_for_project(demo_project: WebProject, num_of_urls: int = 1) -> List[Task]:
    """
    Genera tareas para el proyecto demo dado.
    Si USE_CACHED_TASKS es True, intenta cargar primero desde la caché específica del proyecto.

    Args:
        demo_project: El proyecto web para el que generar tareas
        num_of_urls: Número de URLs a incluir en la generación de tareas

    Returns:
        Lista de objetos Task
    """
    # Intentar cargar desde caché si está configurado
    if USE_CACHED_TASKS:
        cached_tasks = await load_tasks_from_json(demo_project)
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Usando {len(cached_tasks)} tareas cacheadas para el proyecto '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No se encontraron tareas cacheadas válidas para el proyecto '{demo_project.name}', generando nuevas tareas...")

    # Generar nuevas tareas
    config = TaskGenerationConfig(
        web_project=demo_project,
        save_web_analysis_in_db=True, 
        save_task_in_db=False,
        number_of_prompts_per_task=1,
        num_or_urls=num_of_urls
    )

    print(f"Generando tareas para {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)

    # Generar tareas
    task_results = await pipeline.generate()

    # Generar tests para las tareas
    test_pipeline = TestGenerationPipeline(llm_service=DIContainer.llm_service(), web_project=demo_project)
    tasks_with_tests = await add_tests_to_tasks(task_results, test_pipeline)

    # Guardar en caché para uso futuro
    if USE_CACHED_TASKS:
        await save_tasks_to_json(demo_project, tasks_with_tests)

    return tasks_with_tests


# Aplicar visualización a la generación de tests
@visualize_task(visualizer)
async def add_tests_to_tasks(tasks, test_pipeline):
    """
    Añade tests a las tareas generadas y las visualiza

    Args:
        tasks: Lista de tareas a las que añadir tests
        test_pipeline: Pipeline para la generación de tests

    Returns:
        Lista de tareas con tests añadidos
    """
    print(f"Generando tests para {len(tasks)} tareas...")
    return await test_pipeline.add_tests_to_tasks(tasks)

# ============================================================
# FUNCIONES DE EVALUACIÓN
# ============================================================


@visualize_evaluation(visualizer)
async def evaluate_task_solution(web_project, task, task_solution):
    """
    Evalúa una tarea individual con visualización

    Args:
        web_project: Proyecto web asociado
        task: Tarea a evaluar
        task_solution: Solución de la tarea propuesta por el agente

    Returns:
        Resultado de la evaluación
    """
    evaluator_config = EvaluatorConfig(save_results_in_db=False)
    evaluator = ConcurrentEvaluator(web_project=web_project, config=evaluator_config)
    return await evaluator.evaluate_single_task_solution(task=task, task_solution=task_solution)


async def evaluate_project_for_agent(agent, demo_project, tasks, results):
    """
    Evalúa todas las tareas de un proyecto para un agente.

    Args:
        agent: Agente a evaluar
        demo_project: Proyecto web a evaluar
        tasks: Lista de tareas
        results: Diccionario donde almacenar los resultados
    """
    # Inicializar entrada de proyecto en resultados si no existe
    if demo_project.name not in results[agent.id]["projects"]:
        results[agent.id]["projects"][demo_project.name] = []

    # Evaluar cada tarea
    for task in tasks:
        start_time = time.time()

        # El agente genera la solución
        task_solution: TaskSolution = await agent.solve_task(task)
        actions: List[BaseAction] = task_solution.actions

        # Preparar evaluación
        task_solution = TaskSolution(task_id=task.id, actions=actions, web_agent_id=agent.id)

        # Usar método decorado para evaluar
        evaluation_result: EvaluationResult = await evaluate_task_solution(
            web_project=demo_project, 
            task=task, 
            task_solution=task_solution
        )

        # Registrar puntuación
        score = evaluation_result.final_score
        results[agent.id]["global_scores"].append(score)
        results[agent.id]["projects"][demo_project.name].append(score)

        # Mostrar tiempo de evaluación
        elapsed_time = time.time() - start_time
        print(f"Tarea {task.id} evaluada en {elapsed_time:.2f} segundos. Puntuación: {score:.4f}")

# ============================================================
# FUNCIONES DE ANÁLISIS Y PRESENTACIÓN DE RESULTADOS
# ============================================================


def compute_statistics(scores: List[float]) -> dict:
    """
    Calcula estadísticas básicas para una lista de puntuaciones

    Args:
        scores: Lista de puntuaciones

    Returns:
        Diccionario con estadísticas calculadas
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
def print_performance_statistics(results, agents):
    """
    Imprime estadísticas de rendimiento para cada agente.

    Args:
        results: Diccionario con resultados
        agents: Lista de agentes evaluados
    """
    print("\n" + "=" * 50)
    print("ESTADÍSTICAS DE RENDIMIENTO DE AGENTES")
    print("=" * 50)

    for agent in agents:
        agent_stats = results[agent.id]
        global_stats = compute_statistics(agent_stats["global_scores"])
        print(f"\nAgente: {agent.id}")
        print("  Estadísticas Globales:")
        print(f"    Tareas completadas: {global_stats['count']}")
        print(f"    Puntuación media: {global_stats['mean']:.2f}")
        print(f"    Puntuación máxima: {global_stats['max']:.2f}")

        print("  Estadísticas por Proyecto:")
        for project_name, scores in agent_stats["projects"].items():
            project_stats = compute_statistics(scores)
            print(f"    Proyecto: {project_name}")
            print(f"      Tareas completadas: {project_stats['count']}")
            print(f"      Puntuación media: {project_stats['mean']:.2f}")
            print(f"      Puntuación máxima: {project_stats['max']:.2f}")


def plot_agent_results(results, agents):
    """
    Crea un gráfico de barras con las puntuaciones promedio de los agentes.

    Args:
        results: Diccionario con resultados
        agents: Lista de agentes evaluados
    """
    # Asegurar que existe el directorio de resultados
    os.makedirs(LOG_DIR, exist_ok=True)

    agent_names = []
    agent_avg_scores = []

    # Calcular puntuación promedio para cada agente
    for agent in agents:
        scores = results[agent.id]["global_scores"]
        avg_score = sum(scores) / len(scores) if scores else 0
        agent_names.append(agent.id)
        agent_avg_scores.append(avg_score)

    # Crear gráfico de barras
    plt.figure(figsize=(10, 6))
    bars = plt.bar(agent_names, agent_avg_scores, color='skyblue')
    plt.ylim(0, 1.0)
    plt.ylabel('Puntuación')
    plt.title('Rendimiento de Agentes')

    # Añadir etiquetas sobre cada barra
    for bar, score in zip(bars, agent_avg_scores):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{score:.2f}', ha='center', va='bottom')

    # Guardar el gráfico
    plt.savefig(os.path.join(LOG_DIR, "rendimiento_agentes.png"))
    print(f"Gráfico guardado en: {os.path.join(LOG_DIR, 'rendimiento_agentes.png')}")


def save_benchmark_results(results, agents, demo_web_projects):
    """
    Guarda los resultados del benchmark en un archivo JSON para análisis posterior.

    Args:
        results: Diccionario con resultados
        agents: Lista de agentes evaluados
        demo_web_projects: Lista de proyectos evaluados
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "results": {},
        "projects": [p.name for p in demo_web_projects],
        "agents": [a.id for a in agents]
    }

    # Convertir resultados a formato serializable
    for agent_id, agent_results in results.items():
        output_data["results"][agent_id] = {
            "global_scores": agent_results["global_scores"],
            "projects": agent_results["projects"],
            "statistics": compute_statistics(agent_results["global_scores"])
        }

    # Guardar resultados
    filename = os.path.join(OUTPUT_DIR, f"benchmark_results_{timestamp}.json")
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Resultados del benchmark guardados en: {filename}")

# ============================================================
# FUNCIÓN PRINCIPAL DEL BENCHMARK
# ============================================================


async def main():
    print("\n" + "=" * 50)
    print("BENCHMARK DE WEB AGENTS - SUBNET 36")
    print("=" * 50)

    try:
        # Crear directorios necesarios
        os.makedirs(LOG_DIR, exist_ok=True)

        # ---------------------------
        # 1. Inicializar Agentes y Almacenamiento de Resultados
        # ---------------------------
        agents: List[BaseAgent] = AGENTS
        results = {}
        for agent in agents:
            results[agent.id] = {"global_scores": [], "projects": {}}
            print(f"Agente registrado: {agent.id}")

        # ---------------------------
        # 2. Inicializar Proyectos Web Demo
        # ---------------------------
        print("\nInicializando proyectos web demo...")
        demo_web_projects: List[WebProject] = await initialize_demo_webs_projects()
        print(f"Proyectos disponibles: {', '.join([p.name for p in demo_web_projects])}")

        # ---------------------------
        # 3. Procesar Cada Proyecto Web Demo
        # ---------------------------
        for index, demo_project in enumerate(demo_web_projects):
            print(f"\n{'=' * 40}")
            print(f"Procesando proyecto {index+1}/{len(demo_web_projects)}: {demo_project.name}")
            print(f"{'=' * 40}")

            # Generar o cargar tareas para el proyecto actual
            start_time = time.time()
            tasks = await generate_tasks_for_project(demo_project)
            elapsed_time = time.time() - start_time

            print(f"Tareas obtenidas: {len(tasks)} en {elapsed_time:.2f} segundos")

            # Contar cuántos tests se generaron en total
            total_tests = sum(len(task.tests) if hasattr(task, "tests") else 0 for task in tasks)
            print(f"Tests generados: {total_tests} (promedio: {total_tests/len(tasks):.1f} por tarea)")

            # ---------------------------
            # 4. Evaluar Cada Agente en el Proyecto Actual
            # ---------------------------
            for agent in agents:
                print(f"\n{'-' * 30}")
                print(f"Evaluando agente: {agent.id}")
                print(f"{'-' * 30}")

                start_time = time.time()
                await evaluate_project_for_agent(agent, demo_project, tasks, results)
                elapsed_time = time.time() - start_time

                # Calcular estadísticas del proyecto para este agente
                project_scores = results[agent.id]["projects"].get(demo_project.name, [])
                avg_score = sum(project_scores) / len(project_scores) if project_scores else 0

                print(f"Evaluación completada en {elapsed_time:.2f} segundos")
                print(f"Puntuación media: {avg_score:.4f}")

        # ---------------------------
        # 5. Imprimir Estadísticas de Rendimiento
        # ---------------------------
        print_performance_statistics(results, agents)

        # ---------------------------
        # 6. Generar Gráfico de Resultados
        # ---------------------------
        plot_agent_results(results, agents)

        # ---------------------------
        # 7. Guardar Resultados
        # ---------------------------
        save_benchmark_results(results, agents, demo_web_projects)

        print("\n" + "=" * 50)
        print("EVALUACIÓN FINALIZADA")
        print(f"Resultados y logs disponibles en: {LOG_DIR}")
        print(f"Gráficos disponibles en: {OUTPUT_DIR}")
        print("=" * 50)

    except Exception as e:
        import traceback
        print(f"\n[ERROR] Durante la ejecución: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
