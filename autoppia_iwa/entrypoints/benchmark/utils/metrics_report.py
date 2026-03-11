"""
Metrics report: load consolidated benchmark JSON and print/write summary.

Can be run standalone (path to JSON or default latest) or called from Benchmark.run().
Uses Rich for aligned tables and panels when available; falls back to plain text.
Uses defensive .get() and try/except so malformed data does not crash the script.
"""

import io
import json
import sys
from pathlib import Path
from typing import Any

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table


def _safe_float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _safe_int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def load_consolidated_results(path: Path | str) -> dict[str, Any]:
    """
    Load consolidated benchmark JSON. Raises FileNotFoundError or ValueError on failure.
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Results file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise OSError(f"Failed to read {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object; got {type(data).__name__}")

    return data


def _fmt_cost(v: Any) -> str:
    if v is None:
        return "—"
    return f"${_safe_float(v):.6f}"


def _render_report(data: dict[str, Any], console: Console) -> None:
    """Render full benchmark report to the given Rich console."""
    total_time = data.get("total_execution_time") or 0
    config_summary = data.get("config_summary") or {}
    projects = data.get("projects")

    if projects is None:
        console.print("[yellow]Warning: missing 'projects' key in results.[/yellow]")
        return
    if not isinstance(projects, dict):
        console.print("[yellow]Warning: 'projects' is not an object.[/yellow]")
        return

    # Header
    ts = data.get("timestamp", "")
    tasks_src = config_summary.get("tasks_source", "")
    tasks_path = config_summary.get("tasks_json_path")
    header_lines = [
        f"Timestamp:        [bold]{ts}[/bold]",
        f"Total execution:  [bold]{_safe_float(total_time):.2f}s[/bold]",
        f"Tasks source:     [bold]{tasks_src}[/bold]",
    ]
    if tasks_path:
        header_lines.append(f"Tasks JSON path:  {tasks_path}")
    console.print(
        Panel(
            "\n".join(header_lines),
            title="[bold]BENCHMARK METRICS REPORT[/bold]",
            border_style="blue",
            padding=(0, 1),
        )
    )
    console.print()

    # Executive summary table
    summary_table = Table(
        title="Executive summary (all agents)",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 1),
    )
    summary_table.add_column("Agent", style="bold", min_width=24, max_width=40)
    summary_table.add_column("Tasks", justify="right", style="dim")
    summary_table.add_column("Success", justify="right", style="dim")
    summary_table.add_column("Rate", justify="right")
    summary_table.add_column("Avg time", justify="right", style="dim")
    summary_table.add_column("Avg cost", justify="right")
    summary_table.add_column("Total cost", justify="right")
    summary_table.add_column("Tokens (in / out)", justify="right", style="dim")

    for _project_name, project_data in projects.items():
        if not isinstance(project_data, dict):
            continue
        for agent_name, agent_data in project_data.items():
            if not isinstance(agent_data, dict):
                continue
            overall = agent_data.get("overall") or {}
            total = _safe_int(overall.get("total"), 0)
            if total == 0:
                continue
            succ = _safe_int(overall.get("success_count"), 0)
            rate = _safe_float(overall.get("success_rate"), 0)
            avg_time = _safe_float(overall.get("avg_solution_time"), 0)
            avg_cost = overall.get("avg_cost_per_task_usd")
            total_cost = overall.get("total_cost_usd")
            tin = overall.get("total_input_tokens")
            tout = overall.get("total_output_tokens")
            avg_c = _fmt_cost(avg_cost) if avg_cost is not None else "—"
            tot_c = _fmt_cost(total_cost) if total_cost is not None else "—"
            tok_s = f"{_safe_int(tin)} / {_safe_int(tout)}" if (tin is not None or tout is not None) else "—"
            rate_style = "green" if rate >= 0.5 else ("yellow" if rate > 0 else "red")
            summary_table.add_row(
                agent_name,
                str(total),
                str(succ),
                f"[{rate_style}]{rate:.1%}[/{rate_style}]",
                f"{avg_time:.2f}s",
                avg_c,
                tot_c,
                tok_s,
            )

    console.print(summary_table)
    console.print()

    # Per-project panels
    for project_name, project_data in projects.items():
        if not isinstance(project_data, dict):
            continue
        try:
            inner: list[Table | str] = []
            for agent_name, agent_data in project_data.items():
                if not isinstance(agent_data, dict):
                    continue
                overall = agent_data.get("overall") or {}
                total = _safe_int(overall.get("total"), 0)
                if total == 0:
                    continue
                success_count = _safe_int(overall.get("success_count"), 0)
                rate = _safe_float(overall.get("success_rate"), 0)
                avg_sol = _safe_float(overall.get("avg_solution_time"), 0)
                avg_cost = overall.get("avg_cost_per_task_usd")
                total_cost = overall.get("total_cost_usd")
                total_in = overall.get("total_input_tokens")
                total_out = overall.get("total_output_tokens")

                agent_table = Table(show_header=False, box=None, padding=(0, 0, 0, 2))
                agent_table.add_column("key", style="dim")
                agent_table.add_column("value")
                agent_table.add_row(
                    "Agent",
                    f"[bold]{agent_name}[/bold]",
                )
                agent_table.add_row(
                    "Success",
                    f"{success_count}/{total} ([bold]{rate:.1%}[/bold])",
                )
                agent_table.add_row("Avg time", f"{avg_sol:.2f}s")
                agent_table.add_row("Avg cost/task", _fmt_cost(avg_cost))
                agent_table.add_row("Total cost", _fmt_cost(total_cost))
                agent_table.add_row("Tokens", f"{_safe_int(total_in)} / {_safe_int(total_out)}")
                inner.append(agent_table)

                use_cases = agent_data.get("use_cases") or {}
                if use_cases:
                    uc_table = Table(
                        title="Per use case",
                        show_header=True,
                        header_style="dim",
                        box=None,
                        padding=(0, 0, 0, 2),
                    )
                    uc_table.add_column("Use case", style="dim")
                    uc_table.add_column("Success", justify="right")
                    uc_table.add_column("Avg time", justify="right")
                    uc_table.add_column("Avg cost", justify="right")
                    for uc_name, uc_data in use_cases.items():
                        if not isinstance(uc_data, dict):
                            continue
                        tasks_list = list(uc_data.values())
                        n = len(tasks_list)
                        scores = [_safe_float(t.get("success")) for t in tasks_list if isinstance(t, dict)]
                        times = [_safe_float(t.get("time")) for t in tasks_list if isinstance(t, dict)]
                        costs = [_safe_float(t.get("cost_usd")) for t in tasks_list if isinstance(t, dict) and t.get("cost_usd") is not None]
                        succ_uc = sum(1 for s in scores if s == 1.0)
                        avg_t = (sum(times) / len(times)) if times else 0
                        avg_c_uc = (sum(costs) / len(costs)) if costs else None
                        c_str = _fmt_cost(avg_c_uc) if avg_c_uc is not None else "—"
                        uc_table.add_row(uc_name, f"{succ_uc}/{n}", f"{avg_t:.2f}s", c_str)
                    inner.append(uc_table)
                    inner.append("")

            console.print(
                Panel(
                    Group(*inner),
                    title=f"[bold]Project: {project_name}[/bold]",
                    border_style="green",
                    padding=(0, 1),
                )
            )
            console.print()
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print()

    # Per-task detail table
    detail_table = Table(
        title="Per-task detail",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 1),
    )
    detail_table.add_column("Project / Agent", style="dim", max_width=36)
    detail_table.add_column("Task id", style="dim")
    detail_table.add_column("Use case", style="dim")
    detail_table.add_column("Score", justify="right")
    detail_table.add_column("Time", justify="right", style="dim")
    detail_table.add_column("Eval time", justify="right", style="dim")
    detail_table.add_column("Cost", justify="right")
    detail_table.add_column("Tokens", justify="right", style="dim")
    detail_table.add_column("Steps", justify="right", style="dim")

    for project_name, project_data in projects.items():
        if not isinstance(project_data, dict):
            continue
        for agent_name, agent_data in project_data.items():
            if not isinstance(agent_data, dict):
                continue
            use_cases = agent_data.get("use_cases") or {}
            if not use_cases:
                continue
            section = f"[{project_name}] {agent_name}"
            first = True
            for uc_name, uc_data in use_cases.items():
                if not isinstance(uc_data, dict):
                    continue
                for task_id, task_data in uc_data.items():
                    if not isinstance(task_data, dict):
                        continue
                    score = _safe_float(task_data.get("success"))
                    time_s = _safe_float(task_data.get("time"))
                    eval_t = task_data.get("evaluation_time")
                    cost = task_data.get("cost_usd")
                    in_tok = task_data.get("input_tokens")
                    out_tok = task_data.get("output_tokens")
                    steps = task_data.get("steps_count")
                    eval_s = _safe_float(eval_t) if eval_t is not None else None
                    cost_s = _fmt_cost(cost) if cost is not None else "—"
                    tok_s = f"{_safe_int(in_tok)} / {_safe_int(out_tok)}" if (in_tok is not None or out_tok is not None) else "—"
                    steps_s = str(steps) if steps is not None else "—"
                    eval_str = f"{eval_s:.2f}s" if eval_s is not None else "—"
                    score_style = "green" if score >= 1.0 else ("yellow" if score > 0 else "red")
                    proj_agent = section if first else ""
                    first = False
                    detail_table.add_row(
                        proj_agent,
                        f"{task_id[:8]}…",
                        uc_name,
                        f"[{score_style}]{score}[/{score_style}]",
                        f"{time_s:.2f}s",
                        eval_str,
                        cost_s,
                        tok_s,
                        steps_s,
                    )
            detail_table.add_row("", "", "", "", "", "", "", "", "")

    console.print(detail_table)
    console.print()


def print_and_collect_report(data: dict[str, Any]) -> list[str]:
    """
    Print full benchmark report to terminal (with Rich) and return plain-text lines
    for writing to the summary file. Uses .get() throughout; one bad section does not crash the rest.
    """
    # Terminal: Rich with color
    console = Console()
    _render_report(data, console)

    # Capture same layout without ANSI for summary file
    buf = io.StringIO()
    file_console = Console(file=buf, force_terminal=False, no_color=True, width=120)
    _render_report(data, file_console)
    text = buf.getvalue()
    lines = text.splitlines()
    return lines


def run_report(
    results_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    write_summary_file: bool = True,
) -> None:
    """
    Load consolidated results, print report, optionally write summary file.
    If results_path is None and output_dir is given, find latest benchmark_results_*.json in output_dir.
    On error (file not found, invalid JSON), raises. When writing summary file, OSError is caught and warned.
    """
    if results_path is None and output_dir is not None:
        out_dir = Path(output_dir)
        if out_dir.exists():
            candidates = sorted(out_dir.glob("benchmark_results_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if candidates:
                results_path = candidates[0]

    if results_path is None:
        raise FileNotFoundError("No results path provided and no benchmark_results_*.json found in output_dir")

    data = load_consolidated_results(results_path)
    lines = print_and_collect_report(data)

    if write_summary_file and lines:
        summary_name = f"metrics_summary_{Path(results_path).stem}.txt"
        summary_path = Path(results_path).parent / summary_name
        try:
            summary_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"\nSummary written to {summary_path}")
        except OSError as e:
            print(f"\nWarning: could not write summary file to {summary_path}: {e}", file=sys.stderr)


def main() -> int:
    """Standalone entrypoint: python -m autoppia_iwa.entrypoints.benchmark.utils.metrics_report [path]"""
    args = sys.argv[1:]
    if args:
        path: Path | str | None = args[0]
        output_dir = None
    else:
        path = None
        try:
            from autoppia_iwa.config.config import PROJECT_BASE_DIR

            output_dir = PROJECT_BASE_DIR.parent / "benchmark-output" / "results"
        except Exception:
            output_dir = Path("benchmark-output") / "results"

    try:
        run_report(results_path=path, output_dir=str(output_dir) if output_dir else None, write_summary_file=True)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
