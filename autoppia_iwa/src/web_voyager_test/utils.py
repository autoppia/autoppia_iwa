import json
import logging
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel
from rich.columns import Columns
from rich.console import Console
from rich.table import Table


class TaskData(BaseModel):
    """Data model for tasks."""

    id: str
    web: str
    ques: str
    web_name: str


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO, handlers=[logging.StreamHandler()])


def load_jsonl_file(file_path: Path, json_only: bool = False) -> List[Dict]:
    """Load tasks from a JSONL file."""
    if not file_path.exists():
        logging.warning(f"File {file_path} not found.")
        return []

    tasks = []
    with file_path.open("r", encoding="utf-8") as f:
        if not json_only:
            for line in f:
                try:
                    tasks.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logging.warning(f"Skipping invalid JSON line in {file_path}: {e}")
            return tasks
        else:
            return json.load(f)


def print_rich_performance_statistics(results, agents):
    """
    Print performance statistics for each agent using rich.

    This function iterates over the agents and prints global and per-project statistics.
    """
    from autoppia_iwa.src.benchmark import compute_statistics

    console = Console()

    console.print("[bold underline]Agent Performance Metrics:[/bold underline]")

    # Create a list to hold all agent statistics tables.
    agent_columns = []

    for agent in agents:
        agent_stats = results[agent.id]
        global_stats = compute_statistics(agent_stats["global_scores"])

        # Create a table for global stats.
        global_table = Table(title=f"[bold]{agent.id} - Global Stats[/bold]", show_header=True, header_style="bold magenta")
        global_table.add_column("Metric", style="cyan")
        global_table.add_column("Value", style="green")
        for key, value in global_stats.items():
            global_table.add_row(key, str(value))

        # Create a table for per-project stats.
        project_tables = []
        for project_name, scores in agent_stats["projects"].items():
            project_stats = compute_statistics(scores)
            project_table = Table(title=f"[bold]{project_name}[/bold]", show_header=True, header_style="bold blue")
            project_table.add_column("Metric", style="cyan")
            project_table.add_column("Value", style="green")
            for key, value in project_stats.items():
                project_table.add_row(key, str(value))
            project_tables.append(project_table)

        # Combine global and project tables into a single column for the agent.
        agent_column = [global_table] + project_tables
        agent_columns.append(Columns(agent_column, expand=True))

    # Print all agent columns side by side.
    console.print(Columns(agent_columns, equal=True, expand=True))
