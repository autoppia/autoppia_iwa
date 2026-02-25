import json
import os
from datetime import datetime
from typing import Any

from .metrics import TimingMetrics, compute_statistics


def save_results_to_json(results, agents, timing_metrics: TimingMetrics, output_dir: str) -> dict[str, str | float | dict[Any, Any]]:
    """
    Save comprehensive results to a JSON file and return the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "r-" if _has_zero_score(results) else ""
    filename = os.path.join(output_dir, f"{prefix}benchmark_results_{timestamp}.json")
    output_data = {"timestamp": datetime.now().isoformat(), "total_execution_time": timing_metrics.get_total_time(), "agents": {}}

    for agent in agents:
        agent_scores = []
        agent_tasks = {}

        if agent.id in results:
            for task_id, data in results[agent.id].items():
                agent_scores.append(data["score"])
                agent_tasks[task_id] = {
                    "use_case": data.get("task_use_case"),
                    "prompt": data.get("prompt"),
                    "score": data["score"],
                    "solution_time": timing_metrics.solution_times.get(agent.id, {}).get(task_id, 0),
                    "evaluation_time": timing_metrics.evaluation_times.get(agent.id, {}).get(task_id, 0),
                }

        # Compute statistics on the agent's scores
        score_stats = compute_statistics(agent_scores)

        output_data["agents"][agent.name] = {
            "agent-id": agent.id,
            "score_statistics": score_stats,
            "avg_solution_time": timing_metrics.get_avg_solution_time(agent.id),
            "avg_evaluation_time": timing_metrics.get_avg_evaluation_time(agent.id),
            "tasks": agent_tasks,
        }

    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nDetailed results saved to '{filename}'")
    return output_data


def _collect_agent_scores(results, agent_id: str) -> list[float]:
    """Collect all scores for a given agent."""
    agent_scores = []
    if agent_id in results:
        for _task_id, data in results[agent_id].items():
            agent_scores.append(data["score"])
    return agent_scores


def _print_score_statistics(stats: dict) -> None:
    """Print score statistics in a formatted way."""
    print("  Score Statistics:")
    for key, value in stats.items():
        if value is not None:
            if isinstance(value, float):
                print(f"    {key}: {value:.2f}")
            else:
                print(f"    {key}: {value}")
        else:
            print(f"    {key}: N/A")


def _print_agent_timing_stats(timing_metrics: TimingMetrics, agent_id: str) -> None:
    """Print timing statistics for an agent."""
    avg_solution = timing_metrics.get_avg_solution_time(agent_id)
    avg_evaluation = timing_metrics.get_avg_evaluation_time(agent_id)
    print(f"  Average solution generation time: {avg_solution:.2f} seconds")
    print(f"  Average evaluation time: {avg_evaluation:.2f} seconds")


def print_performance_statistics(results, agents, timing_metrics: TimingMetrics):
    """
    Print performance stats (scores, timings) for each agent.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n===== PERFORMANCE REPORT ({timestamp}) =====")

    total_time = timing_metrics.get_total_time()
    print(f"\nTotal test execution time: {total_time:.2f} seconds")

    for agent in agents:
        print(f"\n== Agent: {agent.name} ({agent.id}) ==")

        agent_scores = _collect_agent_scores(results, agent.id)
        stats = compute_statistics(agent_scores)
        _print_score_statistics(stats)
        _print_agent_timing_stats(timing_metrics, agent.id)


def _has_zero_score(results: dict) -> bool:
    """
    Devuelve True si en el diccionario results hay al menos
    una entrada con score == 0.0, en cualquier agente o tarea.
    """
    # Use tolerance for floating point comparison (SonarCloud S1244)
    # Los números de punto flotante tienen errores de precisión, por lo que
    # comparar directamente con == puede fallar. Usamos abs(score - 0.0) < TOLERANCE
    # para detectar valores muy cercanos a 0.0 (dentro de 1e-9).
    TOLERANCE = 1e-9
    for agent_dict in results.values():
        for task_data in agent_dict.values():
            score = task_data.get("score")
            if score is not None and abs(float(score) - 0.0) < TOLERANCE:
                return True
    return False
