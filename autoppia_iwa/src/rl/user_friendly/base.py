"""
User-friendly RL framework base classes.

This module provides base classes and interfaces that make it easy for users
to define their own policies and reward functions for web automation tasks.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Protocol

import torch
import torch.nn as nn
from loguru import logger

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult


class UserPolicy(ABC):
    """
    Base class for user-defined policies.
    
    Users should inherit from this class and implement the required methods
    to define their own policy for web automation tasks.
    """
    
    def __init__(self, name: str = "UserPolicy"):
        self.name = name
        self.device = "cpu"
        
    @abstractmethod
    async def act(self, obs: dict[str, Any]) -> dict[str, Any] | str:
        """
        Select an action based on the current observation.
        
        Args:
            obs: Dictionary containing observation data (image, url, task_prompt, etc.)
            
        Returns:
            Action dictionary or JSON string compatible with BaseAction.create_action()
        """
        pass
    
    @abstractmethod
    def update(self, batch_trajectories: list[dict[str, Any]], **kwargs) -> dict[str, float]:
        """
        Update the policy based on a batch of trajectories.
        
        Args:
            batch_trajectories: List of trajectory dictionaries containing obs, acts, rews
            **kwargs: Additional training parameters
            
        Returns:
            Dictionary with training statistics (loss, avg_return, etc.)
        """
        pass
    
    def save(self, path: str) -> None:
        """Save the policy to a file."""
        if hasattr(self, 'model') and isinstance(self.model, nn.Module):
            torch.save(self.model.state_dict(), path)
            logger.info(f"Policy saved to {path}")
        else:
            logger.warning(f"Policy {self.name} has no model to save")
    
    def load(self, path: str) -> None:
        """Load the policy from a file."""
        if hasattr(self, 'model') and isinstance(self.model, nn.Module):
            state_dict = torch.load(path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            logger.info(f"Policy loaded from {path}")
        else:
            logger.warning(f"Policy {self.name} has no model to load")


class UserRewardFunction(ABC):
    """
    Base class for user-defined reward functions.
    
    Users should inherit from this class and implement the required methods
    to define their own reward function for web automation tasks.
    """
    
    def __init__(self, name: str = "UserRewardFunction"):
        self.name = name
        
    @abstractmethod
    async def __call__(
        self,
        *,
        task: Any,
        step_idx: int,
        last_action_dict: dict[str, Any],
        last_action_obj: BaseAction | None,
        executor: PlaywrightBrowserExecutor,
        trajectory: list[dict[str, Any]],
        obs: dict[str, Any],
        result: ActionExecutionResult | None,
    ) -> tuple[float, bool, dict[str, Any]]:
        """
        Compute reward for the current step.
        
        Args:
            task: Current task object
            step_idx: Current step index
            last_action_dict: Last action taken (as dictionary)
            last_action_obj: Last action object (if available)
            executor: Browser executor
            trajectory: Full trajectory so far
            obs: Current observation
            result: Result of last action execution
            
        Returns:
            Tuple of (reward, done, info_dict)
        """
        pass
    
    def reset_episode_state(self) -> None:
        """Reset any episode-specific state."""
        pass


class SimplePolicy(UserPolicy):
    """
    Simple example policy that users can use as a starting point.
    
    This policy uses a basic neural network to select from predefined actions.
    """
    
    def __init__(
        self, 
        actions: list[dict[str, Any]] | None = None,
        hidden_size: int = 32,
        learning_rate: float = 3e-3,
        name: str = "SimplePolicy"
    ):
        super().__init__(name)
        
        # Default actions for web automation
        self.actions = actions or [
            {"type": "WaitAction", "time_seconds": 0.2},
            {"type": "ScrollAction", "down": True, "value": None},
            {"type": "ScrollAction", "up": True, "value": None},
            {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Search"}},
            {"type": "TypeAction", "selector": {"type": "attributeValueSelector", "attribute": "placeholder", "value": "Search"}, "text": "search"},
            {"type": "NavigateAction", "url": "about:blank"},
        ]
        
        # Store the number of actions at initialization
        self.num_actions = len(self.actions)
        
        # Simple neural network - use stored num_actions to prevent size mismatches
        self.model = nn.Sequential(
            nn.Linear(self._get_feature_size(), hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, self.num_actions)
        ).to(self.device)
        
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Validate that everything is consistent
        self._validate_model_consistency()
        
    def _validate_model_consistency(self):
        """Validate that the model and actions are consistent."""
        if len(self.actions) != self.num_actions:
            raise ValueError(f"Actions list size ({len(self.actions)}) doesn't match stored num_actions ({self.num_actions})")
        
        # Test the model with a dummy input
        dummy_input = torch.zeros(self._get_feature_size(), dtype=torch.float32)
        try:
            output = self.model(dummy_input)
            if output.shape[0] != self.num_actions:
                raise ValueError(f"Model output size ({output.shape[0]}) doesn't match num_actions ({self.num_actions})")
        except Exception as e:
            raise ValueError(f"Model validation failed: {e}")
        
    def _get_feature_size(self) -> int:
        """Get the size of the feature vector."""
        return 6  # url_features + step + task_features
        
    def _featurize(self, obs: dict[str, Any]) -> torch.Tensor:
        """Convert observation to feature vector."""
        url = (obs.get("url") or "")[:256].lower()
        prompt = (obs.get("task_prompt") or "")[:512].lower()
        step = int(obs.get("step") or 0)
        
        # Simple features
        features = [
            "search" in prompt or "search" in url,
            "book" in prompt or "book" in url,
            "click" in prompt or "click" in url,
            "navigate" in prompt or "navigate" in url,
            "submit" in prompt or "submit" in url,
            float(step),
        ]
        
        return torch.tensor([float(x) for x in features], dtype=torch.float32)
    
    async def act(self, obs: dict[str, Any]) -> dict[str, Any]:
        """Select action using the neural network."""
        x = self._featurize(obs).to(self.device)
        logits = self.model(x)
        probs = torch.softmax(logits, dim=-1)
        idx = torch.distributions.Categorical(probs).sample().item()
        return self.actions[idx]
    
    def action_index(self, action_dict: dict[str, Any]) -> int:
        """Find the index of an action in the actions list."""
        if not action_dict:
            return 0
        
        # First try exact match
        try:
            return self.actions.index(action_dict)
        except ValueError:
            pass
        
        # If exact match fails, try to find by action type
        action_type = action_dict.get("type", "")
        if action_type:
            for i, action in enumerate(self.actions):
                if action.get("type", "") == action_type:
                    return i
        
        # If still no match, try partial matching for common action types
        if action_type == "WaitAction":
            for i, action in enumerate(self.actions):
                if action.get("type") == "WaitAction":
                    return i
        elif action_type == "ScrollAction":
            for i, action in enumerate(self.actions):
                if action.get("type") == "ScrollAction":
                    return i
        elif action_type == "ClickAction":
            for i, action in enumerate(self.actions):
                if action.get("type") == "ClickAction":
                    return i
        elif action_type == "TypeAction":
            for i, action in enumerate(self.actions):
                if action.get("type") == "TypeAction":
                    return i
        elif action_type == "NavigateAction":
            for i, action in enumerate(self.actions):
                if action.get("type") == "NavigateAction":
                    return i
        
        # Default to first action if no match found
        logger.warning(f"Could not find action index for {action_dict}, using index 0")
        return 0
    
    def update(self, batch_trajectories: list[dict[str, Any]], gamma: float = 0.99) -> dict[str, float]:
        """Update policy using REINFORCE algorithm."""
        losses = []
        total_return = 0.0
        total_len = 0
        
        for traj in batch_trajectories:
            obs_seq, act_idx, rews = traj["obs"], traj["acts"], traj["rews"]
            
            # Validate trajectory data
            if not obs_seq or not act_idx or not rews:
                logger.warning("Empty trajectory data, skipping")
                continue
            
            if len(obs_seq) != len(act_idx) or len(obs_seq) != len(rews):
                logger.warning(f"Trajectory length mismatch: obs={len(obs_seq)}, acts={len(act_idx)}, rews={len(rews)}")
                continue
            
            # Calculate returns
            G = 0.0
            returns = []
            for r in reversed(rews):
                G = r + gamma * G
                returns.append(G)
            returns.reverse()
            
            R = torch.tensor(returns, dtype=torch.float32, device=self.device)
            if len(R) > 1:
                R = (R - R.mean()) / (R.std() + 1e-6)
            
            # Calculate loss with safety checks
            logps = []
            for ob, ai in zip(obs_seq, act_idx, strict=False):
                # Validate action index
                if ai < 0 or ai >= self.num_actions:
                    logger.warning(f"Invalid action index {ai}, clamping to valid range [0, {self.num_actions-1}]")
                    ai = max(0, min(ai, self.num_actions - 1))
                
                x = self._featurize(ob).to(self.device)
                logits = self.model(x)
                
                # Validate logits shape
                if logits.shape[0] != self.num_actions:
                    logger.error(f"Model output size ({logits.shape[0]}) doesn't match num_actions ({self.num_actions})")
                    continue
                
                logp = torch.log_softmax(logits, dim=-1)[ai]
                logps.append(logp)
            
            if not logps:
                logger.warning("No valid log probabilities calculated, skipping trajectory")
                continue
            
            logps = torch.stack(logps)
            loss = -(logps * R).sum()
            losses.append(loss)
            
            total_return += float(sum(rews))
            total_len += len(rews)
        
        if not losses:
            return {"loss": 0.0, "avg_return": 0.0, "avg_len": 0.0}
        
        # Update model
        L = torch.stack(losses).mean()
        self.optimizer.zero_grad()
        L.backward()
        self.optimizer.step()
        
        return {
            "loss": float(L.detach().cpu()),
            "avg_return": total_return / len(batch_trajectories),
            "avg_len": total_len / len(batch_trajectories)
        }


class SimpleRewardFunction(UserRewardFunction):
    """
    Simple example reward function that users can use as a starting point.
    
    This reward function provides basic feedback based on action success and progress.
    """
    
    def __init__(self, name: str = "SimpleRewardFunction"):
        super().__init__(name)
        
    async def __call__(
        self,
        *,
        task: Any,
        step_idx: int,
        last_action_dict: dict[str, Any],
        last_action_obj: BaseAction | None,
        executor: PlaywrightBrowserExecutor,
        trajectory: list[dict[str, Any]],
        obs: dict[str, Any],
        result: ActionExecutionResult | None,
    ) -> tuple[float, bool, dict[str, Any]]:
        """Compute simple reward based on action success and progress."""
        
        # Base reward for taking a step
        reward = 0.01
        
        # Penalty for failed actions
        if result and not result.successfully_executed:
            reward = -0.01
            
        # Bonus for meaningful actions
        if last_action_dict:
            action_type = last_action_dict.get("type", "")
            if action_type in ["ClickAction", "TypeAction", "NavigateAction", "SubmitAction"]:
                reward += 0.05
                
        # Check for progress (URL changes)
        if len(trajectory) > 1:
            prev_url = trajectory[-2].get("obs_meta", {}).get("url", "")
            current_url = obs.get("url", "")
            if current_url != prev_url and current_url != "about:blank":
                reward += 0.02
                
        # Simple done condition
        done = step_idx >= 10  # End after 10 steps
        
        info = {
            "step": step_idx,
            "url": obs.get("url", ""),
            "reward": reward,
            "done": done,
            "action_type": last_action_dict.get("type", "") if last_action_dict else "",
        }
        
        return reward, done, info


class RandomPolicy(UserPolicy):
    """
    Random policy for testing and comparison.
    """
    
    def __init__(self, actions: list[dict[str, Any]] | None = None, name: str = "RandomPolicy"):
        super().__init__(name)
        self.actions = actions or [
            {"type": "WaitAction", "time_seconds": 0.2},
            {"type": "ScrollAction", "down": True, "value": None},
            {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "button"}},
        ]
        
    async def act(self, obs: dict[str, Any]) -> dict[str, Any]:
        """Select random action."""
        import random
        return random.choice(self.actions)
    
    def action_index(self, action_dict: dict[str, Any]) -> int:
        """Find the index of an action in the actions list."""
        try:
            return self.actions.index(action_dict)
        except ValueError:
            # If exact match fails, try to find by action type
            action_type = action_dict.get("type", "")
            for i, action in enumerate(self.actions):
                if action.get("type", "") == action_type:
                    return i
            # Default to first action if no match found
            return 0
    
    def update(self, batch_trajectories: list[dict[str, Any]], **kwargs) -> dict[str, float]:
        """Random policy doesn't learn."""
        return {"loss": 0.0, "avg_return": 0.0, "avg_len": 0.0}
