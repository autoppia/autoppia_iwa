import json
import logging
import time
from pathlib import Path

from pydantic import BaseModel, Field, RootModel

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.classes import TaskSolution

# Set up logging
logger = logging.getLogger(__name__)


class SolutionData(BaseModel):
    """Model for caching solution data"""

    agent_id: str
    agent_name: str
    timestamp: float = Field(default_factory=time.time)
    solution: TaskSolution


class TaskCache(RootModel):
    """Model for task cache entries"""

    root: dict[str, SolutionData] = {}

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, value):
        self.root[key] = value

    def __contains__(self, key):
        return key in self.root

    def keys(self):
        return self.root.keys()


class SolutionsCache(RootModel):
    """Model for the entire solutions cache"""

    root: dict[str, TaskCache] = {}

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, value):
        self.root[key] = value

    def __contains__(self, key):
        return key in self.root

    def keys(self):
        return self.root.keys()


class ConsolidatedSolutionCache:
    """
    Class to handle caching of task solutions in a single JSON file.
    Uses Pydantic models for data validation and serialization.
    """

    def __init__(self, cache_dir: str):
        """
        Initialize the solution cache.
        Args:
            cache_dir: Directory where solution cache file will be stored
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "solutions.json"

        # Initialize the cache file if it doesn't exist
        if not self.cache_file.exists():
            self._write_cache(SolutionsCache())

    def _read_cache(self) -> SolutionsCache:
        """
        Read all solutions from the cache file.
        Returns:
            Pydantic model of all cached solutions
        """
        try:
            if not self.cache_file.exists():
                return SolutionsCache()

            with open(self.cache_file) as f:
                data = json.load(f)

                # Deserialize the solutions
                solutions_cache = SolutionsCache(root={})

                # Process each task and agent to recreate TaskSolution objects
                for task_id, task_data in data.items():
                    solutions_cache[task_id] = TaskCache(root={})

                    for agent_id, agent_data in task_data.items():
                        # Create a TaskSolution from the serialized data
                        if "solution" in agent_data:
                            solution_data = agent_data["solution"]

                            # Create the TaskSolution object
                            task_solution = TaskSolution(task_id=solution_data.get("task_id", task_id), web_agent_id=solution_data.get("web_agent_id"))

                            # Handle actions - create the BaseAction objects
                            if solution_data.get("actions"):
                                for action_data in solution_data["actions"]:
                                    action = BaseAction.create_action(action_data)
                                    if action:
                                        task_solution.actions.append(action)

                            # Store in the cache
                            solutions_cache[task_id][agent_id] = SolutionData(
                                agent_id=agent_data["agent_id"], agent_name=agent_data["agent_name"], timestamp=agent_data["timestamp"], solution=task_solution
                            )

                return solutions_cache

        except json.JSONDecodeError:
            logger.warning("Corrupted solutions file, creating new one")
            return SolutionsCache()

        except Exception as e:
            logger.error(f"Error reading solutions file: {e!s}")
            return SolutionsCache()

    def _write_cache(self, data: SolutionsCache) -> None:
        """
        Write solutions to the cache file.
        Args:
            data: Pydantic model of all solutions to write
        """
        try:
            # Custom serialization to handle nested models with actions
            serialized_data = data.model_dump()

            # Process each task and agent solution to use nested_model_dump for TaskSolution
            for task_id, task_cache in serialized_data.items():
                for agent_id, solution_data in task_cache.items():
                    if "solution" in solution_data:
                        # Replace the solution with its nested_model_dump version
                        solution_obj = data[task_id][agent_id].solution
                        solution_data["solution"] = solution_obj.nested_model_dump()

            with open(self.cache_file, "w") as f:
                json.dump(serialized_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error writing to solutions file: {e!s}")
            raise

    def solution_exists(self, task_id: str, agent_id: str) -> bool:
        """
        Check if a solution exists in the cache.
        Args:
            task_id: ID of the task
            agent_id: ID of the agent
        Returns:
            True if the solution exists, False otherwise
        """
        cache = self._read_cache()
        return task_id in cache and agent_id in cache[task_id]

    def save_solution(self, task_solution: TaskSolution, agent_id: str, agent_name: str) -> bool:
        """
        Save a solution to the cache.
        Args:
            task_solution: The TaskSolution object to save
            agent_id: ID of the agent that generated the solution
            agent_name: Name of the agent
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Get existing solutions
            cache = self._read_cache()

            # Create solution data using the Pydantic model
            solution_data = SolutionData(agent_id=agent_id, agent_name=agent_name, timestamp=time.time(), solution=task_solution)

            # Initialize task entry if needed
            task_id = task_solution.task_id
            if task_id not in cache:
                cache[task_id] = TaskCache()

            # Add/update the solution for this agent
            cache[task_id][agent_id] = solution_data

            # Write back to file
            self._write_cache(cache)
            logger.debug(f"Solution for task {task_id} by agent {agent_id} cached successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving solution to cache: {e!s}")
            return False

    async def load_solution(self, task_id: str, agent_id: str) -> TaskSolution | None:
        """
        Load a solution from the cache.
        Args:
            task_id: ID of the task
            agent_id: ID of the agent
        Returns:
            TaskSolution object or None if not found
        """
        try:
            cache = self._read_cache()
            if task_id not in cache or agent_id not in cache[task_id]:
                return None

            solution_data = cache[task_id][agent_id]
            return solution_data.solution

        except Exception as e:
            logger.error(f"Error loading solution from cache: {e!s}")
            return None

    # Serialization is handled by TaskSolution.nested_model_dump()

    def clear_cache(self) -> bool:
        """
        Clear all solutions from the cache.
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            self._write_cache(SolutionsCache())
            logger.info("Solution cache cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Error clearing solution cache: {e!s}")
            return False

    def get_all_task_ids(self) -> list[str]:
        """
        Get all task IDs in the cache.
        Returns:
            List of task IDs
        """
        cache = self._read_cache()
        return list(cache.keys())

    def get_all_agent_ids_for_task(self, task_id: str) -> list[str]:
        """
        Get all agent IDs for a specific task.
        Args:
            task_id: ID of the task
        Returns:
            List of agent IDs
        """
        cache = self._read_cache()
        if task_id not in cache:
            return []

        return list(cache[task_id].keys())


# No longer needed as we're using TaskSolution directly


async def load_task_solution(solution_data: SolutionData) -> TaskSolution:
    """
    Load a TaskSolution from cached SolutionData.
    Args:
        solution_data: The cached solution data
    Returns:
        TaskSolution object
    """
    return solution_data.solution
