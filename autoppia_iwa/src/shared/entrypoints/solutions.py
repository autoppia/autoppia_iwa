import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType
from autoppia_iwa.src.web_agents.classes import TaskSolution

# Set up logging
logger = logging.getLogger(__name__)


class SolutionData(BaseModel):
    """Model for caching solution data"""
    agent_id: str
    agent_name: str
    timestamp: float = Field(default_factory=time.time)
    actions: List[Dict[str, Any]] = []


class TaskCache(BaseModel):
    """Model for task cache entries"""
    __root__: Dict[str, SolutionData] = {}

    def __getitem__(self, key):
        return self.__root__[key]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __contains__(self, key):
        return key in self.__root__

    def keys(self):
        return self.__root__.keys()


class SolutionsCache(BaseModel):
    """Model for the entire solutions cache"""
    __root__: Dict[str, TaskCache] = {}

    def __getitem__(self, key):
        return self.__root__[key]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __contains__(self, key):
        return key in self.__root__

    def keys(self):
        return self.__root__.keys()


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

            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                return SolutionsCache.parse_obj(data)

        except json.JSONDecodeError:
            logger.warning("Corrupted solutions file, creating new one")
            return SolutionsCache()

        except Exception as e:
            logger.error(f"Error reading solutions file: {str(e)}")
            return SolutionsCache()

    def _write_cache(self, data: SolutionsCache) -> None:
        """
        Write solutions to the cache file.
        Args:
            data: Pydantic model of all solutions to write
        """
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data.dict(), f, indent=2)

        except Exception as e:
            logger.error(f"Error writing to solutions file: {str(e)}")
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

            # Serialize actions
            serialized_actions = self._serialize_actions(task_solution.actions) if task_solution.actions else []

            # Create solution data using the Pydantic model
            solution_data = SolutionData(
                agent_id=agent_id,
                agent_name=agent_name,
                timestamp=time.time(),
                actions=serialized_actions
            )

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
            logger.error(f"Error saving solution to cache: {str(e)}")
            return False

    async def load_solution(self, task_id: str, agent_id: str) -> Optional[SolutionData]:
        """
        Load a solution from the cache.
        Args:
            task_id: ID of the task
            agent_id: ID of the agent
        Returns:
            SolutionData model containing the solution data or None if not found
        """
        try:
            cache = self._read_cache()
            if task_id not in cache or agent_id not in cache[task_id]:
                return None

            return cache[task_id][agent_id]

        except Exception as e:
            logger.error(f"Error loading solution from cache: {str(e)}")
            return None

    def _serialize_actions(self, actions: List[BaseAction]) -> List[Dict[str, Any]]:
        """
        Serialize a list of actions for storage using Pydantic's dict() method.
        Args:
            actions: List of BaseAction objects
        Returns:
            List of serialized action dictionaries
        """
        serialized_actions = []
        for action in actions:
            try:
                # Convert action to dict using Pydantic's built-in method
                action_dict = action.dict()

                # Handle selector serialization using Pydantic's dict()
                if hasattr(action, 'selector') and action.selector:
                    action_dict['selector'] = action.selector.dict()

                serialized_actions.append(action_dict)

            except Exception as e:
                logger.error(f"Error serializing action {action}: {str(e)}")

        return serialized_actions

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
            logger.error(f"Error clearing solution cache: {str(e)}")
            return False

    def get_all_task_ids(self) -> List[str]:
        """
        Get all task IDs in the cache.
        Returns:
            List of task IDs
        """
        cache = self._read_cache()
        return list(cache.keys())

    def get_all_agent_ids_for_task(self, task_id: str) -> List[str]:
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


class ActionModel(BaseModel):
    """Model for deserializing action data"""
    type: str
    selector: Optional[Dict[str, Any]] = None


async def deserialize_actions(action_data_list: List[Dict[str, Any]]) -> List[BaseAction]:
    """
    Deserialize a list of action dictionaries back into BaseAction objects.
    Args:
        action_data_list: List of serialized action dictionaries
    Returns:
        List of BaseAction objects
    """
    actions = []
    for action_data in action_data_list:
        try:
            # Validate the action data with Pydantic
            action_model = ActionModel.parse_obj(action_data)

            # Handle selector deserialization if present
            if action_model.selector:
                selector_data = action_model.selector
                action_data['selector'] = Selector(
                    type=SelectorType(selector_data['type']),
                    attribute=selector_data.get('attribute'),
                    value=selector_data['value'],
                    case_sensitive=selector_data.get('case_sensitive', False)
                )

            # Create action using BaseAction's factory method
            action = BaseAction.create_action(action_data)
            if action:
                actions.append(action)
            else:
                logger.warning(f"Failed to deserialize action: {action_data}")

        except Exception as e:
            logger.error(f"Error deserializing action {action_data}: {str(e)}")

    return actions
