from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.benchmark.config import BenchmarkConfig
from autoppia_iwa.src.evaluation.benchmark.utils.metrics import TimingMetrics, compute_statistics
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.web_agents.classes import IWebAgent


def build_task_result(
    *,
    agent: IWebAgent,
    task: Task,
    evaluation_result: EvaluationResult,
    eval_id: str,
    run_idx: int,
) -> dict[str, Any]:
    stats = evaluation_result.stats
    return {
        "run": run_idx,
        "agent_id": agent.id,
        "agent_name": agent.name,
        "task_id": task.id,
        "eval_id": eval_id,
        "prompt": task.prompt,
        "use_case": getattr(task.use_case, "name", "Unknown"),
        "score": float(evaluation_result.final_score),
        "success": bool(float(evaluation_result.final_score) == 1.0),
        "evaluation_time": float(evaluation_result.evaluation_time),
        "action_count": int(getattr(stats, "action_count", 0) or 0),
        "tests_passed": int(getattr(stats, "tests_passed", 0) or 0),
        "total_tests": int(getattr(stats, "total_tests", 0) or 0),
        "error": getattr(stats, "error_message", None),
    }


def aggregate_project_results(
    *,
    project: WebProject,
    agents: list[IWebAgent],
    run_results: list[dict[str, dict[str, dict[str, Any]]]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    agent_scores: dict[str, list[float]] = defaultdict(list)
    task_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for run in run_results:
        for agent_id, tasks in run.items():
            for task_data in tasks.values():
                agent_scores[agent_id].append(float(task_data.get("score", 0.0)))
                task_entries[agent_id].append(task_data)

    summary: dict[str, Any] = {}
    for agent in agents:
        scores = agent_scores.get(agent.id, [])
        total = len(scores)
        passed = sum(1 for score in scores if score == 1.0)
        summary[agent.name] = {
            "success_rate": round(passed / total, 3) if total else 0.0,
            "passed": passed,
            "total": total,
            "avg_score": round(sum(scores) / total, 3) if total else 0.0,
        }

    project_report = {
        "project_id": project.id,
        "summary": summary,
        "tasks_by_agent": {agent.name: task_entries.get(agent.id, []) for agent in agents},
    }
    return summary, project_report


def build_run_report(
    *,
    config: BenchmarkConfig,
    timing: TimingMetrics,
    project_reports: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": timing.get_total_time(),
        "config": config.serialize(),
        "projects": project_reports,
        "summary": summary,
    }


def build_terminal_report(run_report: dict[str, Any], *, config: BenchmarkConfig, results_path: str | None = None) -> str:
    if not run_report:
        return "No benchmark results available."

    lines = [
        "",
        "=== BENCHMARK SUMMARY ===",
        f"Mode: {config.evaluator_mode}",
        f"Runs: {config.runs}",
        f"Parallel: {config.max_parallel_evaluations}",
        f"Duration: {run_report['duration_seconds']:.2f}s",
        "",
    ]

    for project_name, project_data in run_report["projects"].items():
        lines.append(project_name)
        for agent_name, stats in project_data["summary"].items():
            lines.append(f"  {agent_name}: {stats['passed']}/{stats['total']} ({stats['success_rate'] * 100:.1f}%) avg={stats['avg_score']:.3f}")
        lines.append("")

    if results_path:
        lines.append(f"JSON: {results_path}")
    lines.append(f"Log: {config.log_file}")
    return "\n".join(lines)


def save_run_report(report: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))
    return output_path


def build_legacy_results_payload(results, agents, timing_metrics: TimingMetrics) -> dict[str, Any]:
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_execution_time": timing_metrics.get_total_time(),
        "agents": {},
    }

    for agent in agents:
        agent_scores = []
        agent_tasks = {}

        if agent.id in results:
            for task_id, data in results[agent.id].items():
                agent_scores.append(data["score"])
                agent_tasks[task_id] = {
                    "use_case": data.get("task_use_case") or data.get("use_case"),
                    "prompt": data.get("prompt"),
                    "score": data["score"],
                    "solution_time": timing_metrics.solution_times.get(agent.id, {}).get(task_id, 0),
                    "evaluation_time": timing_metrics.evaluation_times.get(agent.id, {}).get(task_id, 0),
                }

        output_data["agents"][agent.name] = {
            "agent-id": agent.id,
            "score_statistics": compute_statistics(agent_scores),
            "avg_solution_time": timing_metrics.get_avg_solution_time(agent.id),
            "avg_evaluation_time": timing_metrics.get_avg_evaluation_time(agent.id),
            "tasks": agent_tasks,
        }

    return output_data


def build_legacy_performance_report(results, agents, timing_metrics: TimingMetrics) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "",
        f"===== PERFORMANCE REPORT ({timestamp}) =====",
        "",
        f"Total test execution time: {timing_metrics.get_total_time():.2f} seconds",
    ]

    for agent in agents:
        lines.append("")
        lines.append(f"== Agent: {agent.name} ({agent.id}) ==")
        agent_scores = []
        if agent.id in results:
            for data in results[agent.id].values():
                agent_scores.append(data["score"])
        stats = compute_statistics(agent_scores)
        lines.append("  Score Statistics:")
        for key, value in stats.items():
            if value is None:
                lines.append(f"    {key}: N/A")
            elif isinstance(value, float):
                lines.append(f"    {key}: {value:.2f}")
            else:
                lines.append(f"    {key}: {value}")
        lines.append(f"  Average solution generation time: {timing_metrics.get_avg_solution_time(agent.id):.2f} seconds")
        lines.append(f"  Average evaluation time: {timing_metrics.get_avg_evaluation_time(agent.id):.2f} seconds")

    return "\n".join(lines)


def has_zero_score(results: dict[str, Any]) -> bool:
    for agent_dict in results.values():
        for task_data in agent_dict.values():
            if task_data.get("score") == 0.0:
                return True
    return False
