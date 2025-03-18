import json
import os
from datetime import datetime

import matplotlib.pyplot as plt

from .metrics import TimingMetrics, compute_statistics


def save_results_to_json(results, agents, timing_metrics: TimingMetrics, output_dir: str) -> str:
    """
    Save comprehensive results to a JSON file and return the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"stress_test_results_{timestamp}.json")

    output_data = {"timestamp": datetime.now().isoformat(), "total_execution_time": timing_metrics.get_total_time(), "agents": {}}

    for agent in agents:
        agent_scores = []
        agent_tasks = {}

        if agent.id in results:
            for task_id, data in results[agent.id].items():
                agent_scores.append(data["score"])
                agent_tasks[task_id] = {
                    "score": data["score"],
                    "solution_time": timing_metrics.solution_times.get(agent.id, {}).get(task_id, 0),
                    "evaluation_time": timing_metrics.evaluation_times.get(agent.id, {}).get(task_id, 0),
                    "has_cached_solution": False,  # Will be updated for browser-use agent later
                }

                # Add indicator if this is the browser-use agent with cached solution
                if agent.name == "browser-use":
                    # This would need to be determined based on your solution cache logic
                    # For now, we're assuming all browser-use solutions get cached
                    agent_tasks[task_id]["has_cached_solution"] = True

        # Compute statistics on the agent's scores
        score_stats = compute_statistics(agent_scores)

        output_data["agents"][agent.id] = {
            "name": agent.name,
            "score_statistics": score_stats,
            "avg_solution_time": timing_metrics.get_avg_solution_time(agent.id),
            "avg_evaluation_time": timing_metrics.get_avg_evaluation_time(agent.id),
            "tasks": agent_tasks,
        }

    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nDetailed results saved to '{filename}'")
    return filename


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

        agent_scores = []
        if agent.id in results:
            for _task_id, data in results[agent.id].items():
                agent_scores.append(data["score"])

        stats = compute_statistics(agent_scores)

        print("  Score Statistics:")
        for key, value in stats.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"    {key}: {value:.2f}")
                else:
                    print(f"    {key}: {value}")
            else:
                print(f"    {key}: N/A")

        avg_solution = timing_metrics.get_avg_solution_time(agent.id)
        avg_evaluation = timing_metrics.get_avg_evaluation_time(agent.id)

        print(f"  Average solution generation time: {avg_solution:.2f} seconds")
        print(f"  Average evaluation time: {avg_evaluation:.2f} seconds")

        # Print caching info for browser-use agent
        if agent.name == "browser-use" and agent.id in results:
            # Count tasks with solutions
            num_tasks = len(results[agent.id])
            print(f"  Number of tasks with browser-use solutions cached: {num_tasks}")


def plot_results(results, agents, timing_metrics: TimingMetrics, output_dir: str) -> str:
    """
    Plot average score, solution time, and evaluation time for each agent.
    Returns the path to the saved plot image.
    """
    import statistics

    os.makedirs(output_dir, exist_ok=True)

    agent_names = [agent.name for agent in agents]
    agent_ids = [agent.id for agent in agents]

    avg_scores = []
    solution_times = []
    evaluation_times = []

    for agent_id in agent_ids:
        # Scores
        if agent_id in results:
            scores = [data["score"] for data in results[agent_id].values()]
            avg_score = statistics.mean(scores) if scores else 0
        else:
            avg_score = 0
        avg_scores.append(avg_score)

        # Times
        solution_times.append(timing_metrics.get_avg_solution_time(agent_id))
        evaluation_times.append(timing_metrics.get_avg_evaluation_time(agent_id))

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    # 1) Average Scores
    bars1 = ax1.bar(agent_names, avg_scores, color=["skyblue", "lightgreen"])
    ax1.set_ylim(0, 10)
    ax1.set_ylabel("Average Score")
    ax1.set_title("Agent Performance: Average Scores")

    for bar, score in zip(bars1, avg_scores, strict=False):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, height + 0.1, f"{score:.2f}", ha="center", va="bottom")

    # 2) Average Solution Times
    bars2 = ax2.bar(agent_names, solution_times, color=["coral", "khaki"])
    ax2.set_ylabel("Average Solution Time (seconds)")
    ax2.set_title("Agent Performance: Solution Times")

    for bar, time_val in zip(bars2, solution_times, strict=False):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, height + 0.1, f"{time_val:.2f}s", ha="center", va="bottom")

    # 3) Average Evaluation Times
    bars3 = ax3.bar(agent_names, evaluation_times, color=["lightblue", "lightgreen"])
    ax3.set_ylabel("Average Evaluation Time (seconds)")
    ax3.set_title("Agent Performance: Evaluation Times")

    for bar, time_val in zip(bars3, evaluation_times, strict=False):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2.0, height + 0.1, f"{time_val:.2f}s", ha="center", va="bottom")

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_path = os.path.join(output_dir, f"stress_test_chart_{timestamp}.png")
    plt.savefig(chart_path)

    print(f"\nCharts have been saved to '{chart_path}'")
    return chart_path


def plot_task_comparison(results, agents, tasks, output_dir: str) -> str:
    """
    Plot each agent's score on each task (up to 10 tasks).
    Returns the path to the saved plot image.
    """

    os.makedirs(output_dir, exist_ok=True)

    max_tasks_to_show = min(10, len(tasks))
    selected_tasks = tasks[:max_tasks_to_show]

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.35
    x = range(len(selected_tasks))
    legend_handles = []

    for i, agent in enumerate(agents):
        agent_scores = []

        for task in selected_tasks:
            if (agent.id in results) and (task.id in results[agent.id]):
                agent_scores.append(results[agent.id][task.id]["score"])
            else:
                agent_scores.append(0)

        # Offset each agent's bars
        bars = ax.bar([pos + (i * bar_width) for pos in x], agent_scores, width=bar_width, label=agent.name)
        legend_handles.append(bars[0])

    task_labels = [f"Task {i + 1}" for i in range(len(selected_tasks))]
    ax.set_xticks([pos + bar_width / 2 for pos in x])
    ax.set_xticklabels(task_labels, rotation=45, ha="right")
    ax.set_ylabel("Score")
    ax.set_title("Agent Performance by Task")
    ax.set_ylim(0, 10)
    ax.legend(handles=legend_handles, labels=[agent.name for agent in agents])

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_path = os.path.join(output_dir, f"task_comparison_{timestamp}.png")
    plt.savefig(comparison_path)

    print(f"\nTask comparison chart saved to '{comparison_path}'")
    return comparison_path
