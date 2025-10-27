"""
Example implementations of custom policies and reward functions.

This module provides several example implementations that users can use as
starting points for their own custom policies and reward functions.
"""

import random
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.rl.user_friendly.base import UserPolicy, UserRewardFunction


class CNNPolicy(UserPolicy):
    """
    Example policy using a Convolutional Neural Network for image-based decisions.
    
    This policy processes the screenshot image to make action decisions,
    useful for visual web automation tasks.
    """
    
    def __init__(
        self,
        actions: list[dict[str, Any]] | None = None,
        learning_rate: float = 3e-3,
        name: str = "CNNPolicy"
    ):
        super().__init__(name)
        
        # Default actions
        self.actions = actions or [
            {"type": "WaitAction", "time_seconds": 0.2},
            {"type": "ScrollAction", "down": True, "value": None},
            {"type": "ScrollAction", "up": True, "value": None},
            {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "button"}},
            {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "link"}},
            {"type": "TypeAction", "selector": {"type": "attributeValueSelector", "attribute": "placeholder", "value": "Search"}, "text": "search"},
        ]
        
        # CNN model for image processing
        self.model = nn.Sequential(
            # Convolutional layers
            nn.Conv2d(3, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
            # Fully connected layers
            nn.Linear(64 * 7 * 7, 512),  # Assuming 320x320 input -> 7x7 after conv layers
            nn.ReLU(),
            nn.Linear(512, len(self.actions))
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
    def _process_image(self, obs: dict[str, Any]) -> torch.Tensor:
        """Process the image observation."""
        image = obs.get("image")
        if image is None:
            # Return zero tensor if no image
            return torch.zeros(3, 320, 320, dtype=torch.float32)
        
        # Convert to tensor and normalize
        if isinstance(image, torch.Tensor):
            return image.float() / 255.0
        else:
            # Convert numpy array to tensor
            import numpy as np
            if isinstance(image, np.ndarray):
                return torch.from_numpy(image).float().permute(2, 0, 1) / 255.0
            else:
                return torch.zeros(3, 320, 320, dtype=torch.float32)
    
    async def act(self, obs: dict[str, Any]) -> dict[str, Any]:
        """Select action using CNN."""
        image_tensor = self._process_image(obs).to(self.device)
        
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        
        logits = self.model(image_tensor)
        probs = torch.softmax(logits, dim=-1)
        idx = torch.distributions.Categorical(probs).sample().item()
        
        return self.actions[idx]
    
    def update(self, batch_trajectories: list[dict[str, Any]], gamma: float = 0.99) -> dict[str, float]:
        """Update policy using REINFORCE."""
        losses = []
        total_return = 0.0
        total_len = 0
        
        for traj in batch_trajectories:
            obs_seq, act_idx, rews = traj["obs"], traj["acts"], traj["rews"]
            
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
            
            # Calculate loss
            logps = []
            for ob, ai in zip(obs_seq, act_idx, strict=False):
                image_tensor = self._process_image(ob).to(self.device).unsqueeze(0)
                logits = self.model(image_tensor)
                logp = torch.log_softmax(logits, dim=-1)[0, ai]
                logps.append(logp)
            
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


class EpsilonGreedyPolicy(UserPolicy):
    """
    Example policy using epsilon-greedy exploration.
    
    This policy balances exploration and exploitation by randomly
    selecting actions with probability epsilon.
    """
    
    def __init__(
        self,
        actions: list[dict[str, Any]] | None = None,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        min_epsilon: float = 0.01,
        learning_rate: float = 3e-3,
        name: str = "EpsilonGreedyPolicy"
    ):
        super().__init__(name)
        
        self.actions = actions or [
            {"type": "WaitAction", "time_seconds": 0.2},
            {"type": "ScrollAction", "down": True, "value": None},
            {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "button"}},
            {"type": "TypeAction", "selector": {"type": "attributeValueSelector", "attribute": "placeholder", "value": "Search"}, "text": "search"},
        ]
        
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        
        # Simple Q-network
        self.model = nn.Sequential(
            nn.Linear(self._get_feature_size(), 64),
            nn.ReLU(),
            nn.Linear(64, len(self.actions))
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
    def _get_feature_size(self) -> int:
        return 5  # url_features + step
        
    def _featurize(self, obs: dict[str, Any]) -> torch.Tensor:
        """Convert observation to feature vector."""
        url = (obs.get("url") or "")[:256].lower()
        step = int(obs.get("step") or 0)
        
        features = [
            "search" in url,
            "book" in url,
            "click" in url,
            "navigate" in url,
            float(step),
        ]
        
        return torch.tensor([float(x) for x in features], dtype=torch.float32)
    
    async def act(self, obs: dict[str, Any]) -> dict[str, Any]:
        """Select action using epsilon-greedy strategy."""
        if random.random() < self.epsilon:
            # Explore: random action
            return random.choice(self.actions)
        else:
            # Exploit: best action according to Q-network
            x = self._featurize(obs).to(self.device)
            q_values = self.model(x)
            idx = torch.argmax(q_values).item()
            return self.actions[idx]
    
    def update(self, batch_trajectories: list[dict[str, Any]], gamma: float = 0.99) -> dict[str, float]:
        """Update Q-network using Q-learning."""
        losses = []
        total_return = 0.0
        total_len = 0
        
        for traj in batch_trajectories:
            obs_seq, act_idx, rews = traj["obs"], traj["acts"], traj["rews"]
            
            # Q-learning update
            for i in range(len(obs_seq) - 1):
                obs = obs_seq[i]
                action_idx = act_idx[i]
                reward = rews[i]
                next_obs = obs_seq[i + 1]
                
                # Current Q-value
                x = self._featurize(obs).to(self.device)
                q_values = self.model(x)
                current_q = q_values[action_idx]
                
                # Target Q-value
                next_x = self._featurize(next_obs).to(self.device)
                next_q_values = self.model(next_x)
                target_q = reward + gamma * torch.max(next_q_values)
                
                # Loss
                loss = nn.MSELoss()(current_q, target_q.detach())
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
        
        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        return {
            "loss": float(L.detach().cpu()),
            "avg_return": total_return / len(batch_trajectories),
            "avg_len": total_len / len(batch_trajectories),
            "epsilon": self.epsilon
        }


class ProgressRewardFunction(UserRewardFunction):
    """
    Example reward function that rewards progress towards task completion.
    
    This reward function gives higher rewards for actions that move closer
    to completing the task based on URL changes and action types.
    """
    
    def __init__(
        self,
        progress_bonus: float = 0.1,
        action_bonus: float = 0.05,
        step_penalty: float = 0.01,
        success_bonus: float = 1.0,
        name: str = "ProgressRewardFunction"
    ):
        super().__init__(name)
        self.progress_bonus = progress_bonus
        self.action_bonus = action_bonus
        self.step_penalty = step_penalty
        self.success_bonus = success_bonus
        
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
        """Compute reward based on progress towards task completion."""
        
        reward = 0.0
        current_url = obs.get("url", "")
        task_prompt = getattr(task, 'prompt', '').lower()
        
        # Step penalty to encourage efficiency
        reward -= self.step_penalty
        
        # Action bonus for meaningful actions
        if last_action_dict:
            action_type = last_action_dict.get("type", "")
            if action_type in ["ClickAction", "TypeAction", "NavigateAction", "SubmitAction"]:
                reward += self.action_bonus
        
        # Progress bonus for URL changes
        if len(trajectory) > 1:
            prev_url = trajectory[-2].get("obs_meta", {}).get("url", "")
            if current_url != prev_url and current_url != "about:blank":
                reward += self.progress_bonus
        
        # Task-specific rewards
        if "search" in task_prompt and "search" in current_url.lower():
            reward += 0.2
        elif "book" in task_prompt and "book" in current_url.lower():
            reward += 0.2
        elif "navigate" in task_prompt and current_url != "about:blank":
            reward += 0.1
        
        # Success condition
        done = False
        if step_idx >= 15:  # Max steps
            done = True
        elif reward > 0.3:  # High reward indicates success
            reward += self.success_bonus
            done = True
        
        info = {
            "step": step_idx,
            "url": current_url,
            "reward": reward,
            "done": done,
            "action_type": last_action_dict.get("type", "") if last_action_dict else "",
            "task_prompt": task_prompt,
        }
        
        return reward, done, info


class SparseRewardFunction(UserRewardFunction):
    """
    Example sparse reward function that only gives rewards at task completion.
    
    This reward function gives minimal feedback during the episode and
    a large reward only when the task is successfully completed.
    """
    
    def __init__(
        self,
        completion_reward: float = 1.0,
        step_penalty: float = 0.001,
        max_steps: int = 20,
        name: str = "SparseRewardFunction"
    ):
        super().__init__(name)
        self.completion_reward = completion_reward
        self.step_penalty = step_penalty
        self.max_steps = max_steps
        
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
        """Compute sparse reward."""
        
        reward = -self.step_penalty  # Small penalty for each step
        current_url = obs.get("url", "")
        task_prompt = getattr(task, 'prompt', '').lower()
        
        # Check for task completion
        done = False
        if step_idx >= self.max_steps:
            done = True
        else:
            # Simple completion detection based on URL and task
            if "search" in task_prompt and "search" in current_url.lower():
                reward = self.completion_reward
                done = True
            elif "book" in task_prompt and "book" in current_url.lower():
                reward = self.completion_reward
                done = True
            elif "navigate" in task_prompt and current_url != "about:blank":
                reward = self.completion_reward
                done = True
        
        info = {
            "step": step_idx,
            "url": current_url,
            "reward": reward,
            "done": done,
            "task_prompt": task_prompt,
        }
        
        return reward, done, info


class CuriosityRewardFunction(UserRewardFunction):
    """
    Example curiosity-driven reward function that rewards exploration.
    
    This reward function gives rewards for visiting new URLs and taking
    diverse actions, encouraging exploration of the environment.
    """
    
    def __init__(
        self,
        exploration_bonus: float = 0.1,
        novelty_bonus: float = 0.2,
        step_penalty: float = 0.01,
        name: str = "CuriosityRewardFunction"
    ):
        super().__init__(name)
        self.exploration_bonus = exploration_bonus
        self.novelty_bonus = novelty_bonus
        self.step_penalty = step_penalty
        self.visited_urls = set()
        self.taken_actions = set()
        
    def reset_episode_state(self) -> None:
        """Reset episode-specific state."""
        self.visited_urls.clear()
        self.taken_actions.clear()
        
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
        """Compute curiosity-driven reward."""
        
        reward = -self.step_penalty
        current_url = obs.get("url", "")
        
        # Novelty bonus for new URLs
        if current_url not in self.visited_urls and current_url != "about:blank":
            reward += self.novelty_bonus
            self.visited_urls.add(current_url)
        
        # Exploration bonus for new actions
        if last_action_dict:
            action_type = last_action_dict.get("type", "")
            if action_type not in self.taken_actions:
                reward += self.exploration_bonus
                self.taken_actions.add(action_type)
        
        # Done condition
        done = step_idx >= 20
        
        info = {
            "step": step_idx,
            "url": current_url,
            "reward": reward,
            "done": done,
            "visited_urls": len(self.visited_urls),
            "unique_actions": len(self.taken_actions),
        }
        
        return reward, done, info
