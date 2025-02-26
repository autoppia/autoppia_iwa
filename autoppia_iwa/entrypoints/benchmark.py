import asyncio
import statistics
from typing import List
import matplotlib.pyplot as plt
import os
from datetime import datetime

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

# Importar el visualizador simple
from autoppia_iwa.src.shared.visualizator import SimpleSubnetVisualizer, visualize_evaluation

# Inicializar el visualizador
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = os.path.join("logs", f"benchmark_{timestamp}")
visualizer = SimpleSubnetVisualizer(log_directory=log_dir)

app = AppBootstrap()
AGENTS: List[BaseAgent] = [RandomClickerWebAgent(name="Random-clicker")]  # , ApifiedWebAgent(name="Text-External-Agent", host="localhost", port=9000)]
iterations = 1  # total_tasks = tasks * iterations


# Aplicar decorador al método de evaluación original
@visualize_evaluation(visualizer)
async def evaluate_task_solution(task, task_solution):
    evaluator_config = EvaluatorConfig(save_results_in_db=False)
    evaluator = ConcurrentEvaluator(evaluator_config)
    return await evaluator.evaluate_single_task_solution(task=task, task_solution=task_solution)


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

        # Prepare evaluator input
        task_solution = TaskSolution(task=task, actions=actions, web_agent_id=agent.id)

        # Usar el método decorado para evaluar la tarea
        evaluation_result: EvaluationResult = await evaluate_task_solution(task=task, task_solution=task_solution)
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
                                  num_or_urls=1)

    print("Generando tareas para: ", demo_project.name)
    tasks = []
    for i in range(iterations):
        new_tasks = await TaskGenerationPipeline(web_project=demo_project, config=config).generate()
        tasks.extend(new_tasks.tasks)

    return tasks


async def add_tests_to_tasks(tasks, test_pipeline):
    """Añade tests a las tareas generadas"""
    print(f"Generando tests para {len(tasks)} tareas...")
    return await test_pipeline.add_tests_to_tasks(tasks)


def print_performance_statistics(results, agents):
    """
    Print performance statistics for each agent.

    This function iterates over the agents and prints global and per-project statistics.
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

    print("\n" + "=" * 50)


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
    plt.ylim(0, 1.0)  # Ajustar a escala 0-1
    plt.ylabel('Puntuación')
    plt.title('Rendimiento de Agentes')

    # Add score labels above each bar.
    for bar, score in zip(bars, agent_avg_scores):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{score:.2f}', ha='center', va='bottom')

    plt.savefig(os.path.join(log_dir, "rendimiento_agentes.png"))
    print(f"Gráfico guardado en: {os.path.join(log_dir, 'rendimiento_agentes.png')}")


async def main():
    print("\n" + "=" * 50)
    print("BENCHMARK DE WEB AGENTS - SUBNET 36")
    print("=" * 50)

    try:
        # ---------------------------
        # 1. Initialize Agents and Results Storage.
        # ---------------------------
        agents: List[BaseAgent] = AGENTS
        results = {}
        for agent in agents:
            results[agent.id] = {"global_scores": [], "projects": {}}
            print(f"Agente registrado: {agent.id}")

        # ---------------------------
        # 2. Process Each Demo Web Project.
        # ---------------------------
        print("\nInicializando proyectos web demo...")
        demo_web_projects: List[WebProject] = await initialize_demo_webs_projects()
        print(f"Proyectos disponibles: {', '.join([p.name for p in demo_web_projects])}")

        for index, demo_project in enumerate(demo_web_projects):
            print(f"\nProcesando proyecto {index+1}/{len(demo_web_projects)}: {demo_project.name}")

            # Generar tareas para el proyecto actual
            tasks = await generate_tasks_for_project(demo_project, generate_new_tasks=True)
            print(f"Tareas generadas: {len(tasks)}")

            # Generar tests para las tareas
            llm_service = DIContainer.llm_service()
            test_pipeline = TestGenerationPipeline(llm_service=llm_service, web_project=demo_project)
            tasks = await add_tests_to_tasks(tasks, test_pipeline)

            # Contar cuántos tests se generaron en total
            total_tests = sum(len(task.tests) if hasattr(task, "tests") else 0 for task in tasks)
            print(f"Tests generados: {total_tests} (promedio de {total_tests/len(tasks):.1f} por tarea)")

            # Evaluar cada agente en las tareas generadas
            for agent in agents:
                print(f"\nEvaluando agente: {agent.id}")
                await evaluate_project_for_agent(agent, demo_project, tasks, results)

        # ---------------------------
        # 3. Print Performance Statistics.
        # ---------------------------
        print_performance_statistics(results, agents)

        # ---------------------------
        # 4. Plot the Agent Results.
        # ---------------------------
        plot_agent_results(results, agents)

    except Exception as e:
        import traceback
        print(f"Error durante la ejecución: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
