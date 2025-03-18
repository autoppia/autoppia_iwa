import statistics
import time


class TimingMetrics:
    """Track timing metrics for tasks and agents."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        # Structure: {agent_id: {task_id: float}} for solution & evaluation times
        self.solution_times: dict[str, dict[str, float]] = {}
        self.evaluation_times: dict[str, dict[str, float]] = {}

    def start(self):
        """Start the overall timing."""
        self.start_time = time.time()

    def end(self):
        """End the overall timing."""
        self.end_time = time.time()

    def record_solution_time(self, agent_id: str, task_id: str, solution_time: float):
        """Record time taken to generate a solution for a specific task."""
        if agent_id not in self.solution_times:
            self.solution_times[agent_id] = {}
        self.solution_times[agent_id][task_id] = solution_time

    def record_evaluation_time(self, agent_id: str, task_id: str, evaluation_time: float):
        """Record time taken for evaluation of a specific task."""
        if agent_id not in self.evaluation_times:
            self.evaluation_times[agent_id] = {}
        self.evaluation_times[agent_id][task_id] = evaluation_time

    def get_total_time(self) -> float:
        """Return total execution time from start to end."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def get_avg_solution_time(self, agent_id: str) -> float:
        """Get the average solution time for a specific agent."""
        times = self.solution_times.get(agent_id, {}).values()
        return statistics.mean(times) if times else 0.0

    def get_avg_evaluation_time(self, agent_id: str) -> float:
        """Get the average evaluation time for a specific agent."""
        times = self.evaluation_times.get(agent_id, {}).values()
        return statistics.mean(times) if times else 0.0


def compute_statistics(values: list[float]) -> dict:
    """
    Compute basic statistics for a list of numeric values.

    Returns:
        dict: A dictionary with count, mean, median, min, max, stdev.
    """
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "stdev": None,
        }

    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }
