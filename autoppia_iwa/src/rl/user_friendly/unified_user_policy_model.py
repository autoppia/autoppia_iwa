#!/usr/bin/env python3
"""
Unified Multi-Project Model using UserPolicy and UserRewardFunction

This script creates a unified model that properly inherits from the base
UserPolicy and UserRewardFunction classes from the user-friendly framework.
"""

import sys
from pathlib import Path
import traceback
import json
from datetime import datetime
from typing import Dict, List, Any
import torch
import torch.nn as nn
import torch.nn.functional as F

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import base classes from user-friendly framework
from autoppia_iwa.src.rl.user_friendly.base import UserPolicy, UserRewardFunction
from autoppia_iwa.src.rl.user_friendly.trainer import train_policy
from autoppia_iwa.src.rl.user_friendly.evaluator import evaluate_policy

# Import project and task generation
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project

# Import required classes for reward function
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult


class MultiProjectModel(nn.Module):
    
    def __init__(self, num_projects: int, num_actions: int = 10, input_size: int = 100):
        """
        Initialize multi-project model.
        
        Args:
            num_projects: Number of projects the model will handle
            num_actions: Number of possible actions
            input_size: Size of input features
        """
        super().__init__()
        
        self.num_projects = num_projects
        self.num_actions = num_actions
        self.input_size = input_size
        
        # Project embedding layer
        self.project_embedding = nn.Embedding(num_projects, 32)
        
        # Input feature processing
        self.feature_processor = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        
        # Combined feature processing
        self.feature_size = 64 + 32  # Processed features + project embedding
        
        # Action head
        self.action_head = nn.Linear(self.feature_size, num_actions)
        
        # Project-specific heads (optional)
        self.project_heads = nn.ModuleList([
            nn.Linear(self.feature_size, num_actions) for _ in range(num_projects)
        ])
        
        # Use project-specific heads or shared head
        self.use_project_heads = True
        
    def forward(self, features, project_id):
        """
        Forward pass.
        
        Args:
            features: Input features tensor (B, input_size)
            project_id: Project ID tensor (B,)
        """
        # Process input features
        processed_features = self.feature_processor(features)
        
        # Get project embedding
        project_emb = self.project_embedding(project_id)
        
        # Combine features
        combined_features = torch.cat([processed_features, project_emb], dim=1)
        
        # Get action logits
        if self.use_project_heads:
            # Use project-specific head
            logits = self.project_heads[project_id[0]](combined_features)
        else:
            # Use shared head
            logits = self.action_head(combined_features)
        
        return logits


class UnifiedMultiProjectPolicy(UserPolicy):
    """Unified multi-project policy that inherits from UserPolicy."""
    
    def __init__(self, name: str = "UnifiedMultiProjectPolicy", learning_rate: float = 1e-3):
        """
        Initialize unified multi-project policy.
        
        Args:
            name: Policy name
            learning_rate: Learning rate for optimizer
        """
        super().__init__(name)
        self.learning_rate = learning_rate
        
        # Get project information
        self.projects = demo_web_projects
        self.project_ids = [p.id for p in self.projects]
        self.project_to_id = {pid: i for i, pid in enumerate(self.project_ids)}
        
        # Initialize model
        self.model = MultiProjectModel(
            num_projects=len(self.projects),
            num_actions=10,  # Default action space size
            input_size=100,  # Default input feature size
        ).to(self.device)
        
        # Initialize optimizer
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Training statistics
        self.training_stats = {
            "total_episodes": 0,
            "total_steps": 0,
            "project_episodes": {pid: 0 for pid in self.project_ids},
            "project_steps": {pid: 0 for pid in self.project_ids},
        }
        
        print(f"🚀 Unified Multi-Project Policy Initialized")
        print(f"📋 Projects: {self.project_ids}")
        print(f"🔧 Model: {self.model}")
    
    def _extract_features(self, obs: Dict[str, Any]) -> torch.Tensor:
        """Extract features from observation."""
        try:
            features = []
            
            # Extract URL features (simple hash-based)
            if "url" in obs:
                url = obs["url"]
                url_hash = hash(url) % 1000
                features.append(float(url_hash) / 1000.0)
            else:
                features.append(0.0)
            
            # Extract step features
            if "step" in obs:
                step = obs["step"]
                features.append(float(step) / 100.0)  # Normalize
            else:
                features.append(0.0)
            
            # Extract task prompt features (simple length-based)
            if "task_prompt" in obs:
                prompt = obs["task_prompt"]
                prompt_length = len(prompt) if prompt else 0
                features.append(float(prompt_length) / 1000.0)  # Normalize
            else:
                features.append(0.0)
            
            # Add more features based on observation content
            for key in ["timestamp", "page_title", "element_count"]:
                if key in obs:
                    value = obs[key]
                    if isinstance(value, (int, float)):
                        features.append(float(value) / 1000.0)
                    else:
                        features.append(float(len(str(value))) / 100.0)
                else:
                    features.append(0.0)
            
            # Pad or truncate to fixed size
            target_size = 100
            while len(features) < target_size:
                features.append(0.0)
            
            if len(features) > target_size:
                features = features[:target_size]
            
            return torch.tensor(features, dtype=torch.float32)
                    
        except Exception as e:
            print(f"⚠️ Error extracting features: {e}")
            return torch.zeros(100, dtype=torch.float32)
    
    def _get_project_id(self, obs: Dict[str, Any]) -> int:
        """Get project ID from observation."""
        try:
            # Try to extract project ID from observation
            if "project_id" in obs:
                project_id = obs["project_id"]
            elif "task" in obs and hasattr(obs["task"], "project_id"):
                project_id = obs["task"].project_id
            else:
                # Default to first project
                project_id = self.project_ids[0]
            
            # Convert to integer ID
            if project_id in self.project_to_id:
                return self.project_to_id[project_id]
            else:
                print(f"⚠️ Unknown project ID: {project_id}, using default")
                return 0
                
        except Exception as e:
            print(f"⚠️ Error getting project ID: {e}")
            return 0
    
    async def act(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get action from policy.
        
        Args:
            obs: Observation dictionary
            
        Returns:
            Action dictionary
        """
        try:
            # Extract features
            features_tensor = self._extract_features(obs).to(self.device).unsqueeze(0)
            
            # Get project ID
            project_id = self._get_project_id(obs)
            project_id_tensor = torch.tensor([project_id], device=self.device)
            
            # Get action logits
            with torch.no_grad():
                logits = self.model(features_tensor, project_id_tensor)
                action_probs = F.softmax(logits, dim=-1)
                action_idx = torch.multinomial(action_probs, 1).item()
            
            # Convert action index to action dictionary
            action = {
                "action_type": "click",
                "x": 100 + action_idx * 50,  # Simple mapping
                "y": 100 + action_idx * 30,
            }
            
            return action
            
        except Exception as e:
            print(f"❌ Error in act(): {e}")
            # Return default action
            return {
                "action_type": "click",
                "x": 100,
                "y": 100,
            }
    
    def update(self, batch_trajectories: List[Dict[str, Any]], gamma: float = 0.99) -> Dict[str, float]:
        """
        Update policy using REINFORCE algorithm.
        
        Args:
            batch_trajectories: List of trajectory dictionaries
            gamma: Discount factor
            
        Returns:
            Dictionary with training statistics
        """
        if not batch_trajectories:
            return {"loss": 0.0, "avg_return": 0.0, "avg_len": 0.0}
        
        losses = []
        total_return = 0.0
        total_len = 0
        project_stats = {pid: {"episodes": 0, "steps": 0, "returns": 0.0} for pid in self.project_ids}
        
        for traj in batch_trajectories:
            obs_seq, act_idx, rews = traj["obs"], traj["acts"], traj["rews"]
            
            # Validate trajectory data
            if not obs_seq or not act_idx or not rews:
                continue
            
            # Calculate returns
            returns = []
            R = 0.0
            for r in reversed(rews):
                R = r + gamma * R
                returns.insert(0, R)
            
            returns = torch.tensor(returns, dtype=torch.float32)
            
            # Calculate log probabilities
            logps = []
            for ob, ai in zip(obs_seq, act_idx, strict=False):
                try:
                    # Extract features
                    features_tensor = self._extract_features(ob).to(self.device).unsqueeze(0)
                    
                    # Get project ID
                    project_id = self._get_project_id(ob)
                    project_id_tensor = torch.tensor([project_id], device=self.device)
                    
                    # Get logits and log probability
                    logits = self.model(features_tensor, project_id_tensor)
                    logp = torch.log_softmax(logits, dim=-1)[0, ai]
                    logps.append(logp)
                    
                    # Update project statistics
                    if project_id < len(self.project_ids):
                        project_stats[self.project_ids[project_id]]["steps"] += 1
                    
                except Exception as e:
                    print(f"⚠️ Error processing step: {e}")
                    continue
            
            if not logps:
                continue
            
            # Calculate loss
            logps = torch.stack(logps)
            loss = -(logps * returns).sum()
            losses.append(loss)
            
            # Update statistics
            total_return += returns.sum().item()
            total_len += len(obs_seq)
            
            # Update project statistics
            project_id = self._get_project_id(obs_seq[0]) if obs_seq else 0
            if project_id < len(self.project_ids):
                project_stats[self.project_ids[project_id]]["episodes"] += 1
                project_stats[self.project_ids[project_id]]["returns"] += returns.sum().item()
        
        if not losses:
            return {"loss": 0.0, "avg_return": 0.0, "avg_len": 0.0}
        
        # Update model
        total_loss = torch.stack(losses).mean()
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()
        
        # Update training statistics
        self.training_stats["total_episodes"] += len(batch_trajectories)
        self.training_stats["total_steps"] += total_len
        
        for pid, stats in project_stats.items():
            self.training_stats["project_episodes"][pid] += stats["episodes"]
            self.training_stats["project_steps"][pid] += stats["steps"]
        
        return {
            "loss": total_loss.item(),
            "avg_return": total_return / len(batch_trajectories),
            "avg_len": total_len / len(batch_trajectories),
            "project_stats": project_stats,
        }
    
    def save(self, path: str) -> None:
        """Save model and training statistics."""
        save_data = {
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "training_stats": self.training_stats,
            "project_ids": self.project_ids,
            "project_to_id": self.project_to_id,
            "model_config": {
                "num_projects": len(self.projects),
                "num_actions": 10,
                "learning_rate": self.learning_rate,
            }
        }
        
        torch.save(save_data, path)
        print(f"💾 Unified multi-project model saved to {path}")
    
    def load(self, path: str) -> None:
        """Load model and training statistics."""
        save_data = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(save_data["model_state_dict"])
        self.optimizer.load_state_dict(save_data["optimizer_state_dict"])
        self.training_stats = save_data["training_stats"]
        
        print(f"📂 Unified multi-project model loaded from {path}")
        print(f"📊 Training stats: {self.training_stats}")


class UnifiedMultiProjectRewardFunction(UserRewardFunction):
    """Unified multi-project reward function that inherits from UserRewardFunction."""
    
    def __init__(self, name: str = "UnifiedMultiProjectReward"):
        """
        Initialize unified multi-project reward function.
        
        Args:
            name: Reward function name
        """
        super().__init__(name)
        
        # Project-specific reward parameters
        self.project_rewards = {
            "work": {"progress_bonus": 0.1, "completion_bonus": 2.0},
            "dining": {"progress_bonus": 0.15, "completion_bonus": 1.5},
            "cinema": {"progress_bonus": 0.12, "completion_bonus": 1.8},
            "books": {"progress_bonus": 0.08, "completion_bonus": 2.2},
            "omnizone": {"progress_bonus": 0.1, "completion_bonus": 2.0},
            "crm": {"progress_bonus": 0.1, "completion_bonus": 2.0},
            "automail": {"progress_bonus": 0.1, "completion_bonus": 2.0},
            "autodelivery": {"progress_bonus": 0.1, "completion_bonus": 2.0},
            "lodge": {"progress_bonus": 0.1, "completion_bonus": 2.0},
            "connect": {"progress_bonus": 0.1, "completion_bonus": 2.0},
        }
        
        # Default parameters
        self.default_progress_bonus = 0.1
        self.default_completion_bonus = 2.0
        self.step_penalty = 0.01
        
        print(f"🎯 Unified Multi-Project Reward Function Initialized")
        print(f"📋 Projects: {list(self.project_rewards.keys())}")
    
    def _get_project_id(self, task: Any) -> str:
        """Get project ID from task."""
        try:
            if hasattr(task, 'project_id'):
                return task.project_id
            else:
                return "work"  # Default project
        except:
            return "work"
    
    async def __call__(
        self,
        *,
        task: Any,
        step_idx: int,
        last_action_dict: Dict[str, Any],
        last_action_obj: BaseAction | None,
        executor: PlaywrightBrowserExecutor,
        trajectory: List[Dict[str, Any]],
    ) -> float:
        """
        Calculate reward for the given step.
        
        Args:
            task: Current task
            step_idx: Current step index
            last_action_dict: Last action dictionary
            last_action_obj: Last action object
            executor: Browser executor
            trajectory: Current trajectory
            
        Returns:
            Calculated reward
        """
        try:
            # Get project-specific parameters
            project_id = self._get_project_id(task)
            project_params = self.project_rewards.get(project_id, {
                "progress_bonus": self.default_progress_bonus,
                "completion_bonus": self.default_completion_bonus
            })
            
            # Base reward (from environment)
            base_reward = 0.0
            
            # Progress bonus
            progress_bonus = 0.0
            if step_idx > 0:
                # Simple progress bonus based on step
                progress_bonus = min(step_idx * 0.01, 0.1) * project_params["progress_bonus"]
            
            # Completion bonus
            completion_bonus = 0.0
            if step_idx > 5:  # Assume completion after 5 steps
                completion_bonus = project_params["completion_bonus"]
            
            # Step penalty
            step_penalty = self.step_penalty
            
            # Total reward
            total_reward = base_reward + progress_bonus + completion_bonus - step_penalty
            
            return total_reward
            
        except Exception as e:
            print(f"⚠️ Error calculating reward: {e}")
            return 0.0


class UnifiedMultiProjectTrainer:
    """Trainer for unified multi-project model using base classes."""
    
    def __init__(
        self,
        output_dir: str = "trained_models_unified",
        headless: bool = True,
        episodes_per_batch: int = 5,
        num_batches: int = 10,
        max_steps_per_episode: int = 20,
        prompts_per_use_case: int = 2,
        use_cached_tasks: bool = True,
        cache_dir: str = "data/tasks_cache",
    ):
        """
        Initialize unified multi-project trainer.
        
        Args:
            output_dir: Directory to save trained models
            headless: Whether to run browser in headless mode
            episodes_per_batch: Number of episodes per training batch
            num_batches: Number of training batches
            max_steps_per_episode: Maximum steps per episode
            prompts_per_use_case: Number of prompts per use case
            use_cached_tasks: Whether to use cached tasks
            cache_dir: Directory for task caching
        """
        self.output_dir = Path(output_dir)
        self.headless = headless
        self.episodes_per_batch = episodes_per_batch
        self.num_batches = num_batches
        self.max_steps_per_episode = max_steps_per_episode
        self.prompts_per_use_case = prompts_per_use_case
        self.use_cached_tasks = use_cached_tasks
        self.cache_dir = cache_dir
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Available projects
        self.available_projects = demo_web_projects
        self.project_ids = [p.id for p in self.available_projects]
        
        # Training results
        self.training_results = {}
        
        print(f"🚀 Unified Multi-Project Trainer Initialized")
        print(f"📁 Output Directory: {self.output_dir}")
        print(f"🌐 Available Projects: {len(self.available_projects)}")
        print(f"📋 Project IDs: {self.project_ids}")
    
    async def _train_on_project(
        self,
        policy,
        reward_function,
        project,
    ):
        """
        Train on a single project without saving intermediate models.
        
        This method trains the unified policy on a single project without creating
        separate .pt files for each project. The policy weights are accumulated
        across all projects, and only the final unified model is saved.
        
        Previously, calling train_policy() would save intermediate models like:
        - trained_books_unifiedmultiprojectpolicy.pt
        - trained_cinema_unifiedmultiprojectpolicy.pt
        etc.
        
        Now, we only save one final unified model.
        """
        from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project
        from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
        from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
        from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
        from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
        from playwright.async_api import async_playwright
        from loguru import logger
        
        # Generate or load tasks
        if self.use_cached_tasks:
            cache_file = Path(self.cache_dir) / f"{project.id}_tasks.jsonl"
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            if cache_file.exists():
                with open(cache_file) as f:
                    tasks = [json.loads(line) for line in f]
                    tasks = [task for task in tasks[:len(tasks)]]  # Use up to num_use_cases
            else:
                tasks = []
        else:
            tasks = []
        
        # Generate tasks if needed
        if not tasks:
            tasks = await generate_tasks_for_project(
                project=project,
                use_cached=self.use_cached_tasks,
                cache_dir=self.cache_dir,
                prompts_per_use_case=self.prompts_per_use_case,
                num_use_cases=0,  # Use all use cases
            )
        
        # Create simple task wrapper
        class SimpleTask:
            def __init__(self, prompt, project):
                self.prompt = prompt
                self.url = project.frontend_url
                self.frontend_url = project.frontend_url
                self.project = project
        
        # Wrap tasks
        wrapped_tasks = [
            SimpleTask(task["task_prompt"], project) 
            if isinstance(task, dict) else task
            for task in tasks[:self.num_batches * self.episodes_per_batch]
        ]
        
        # Task sampler
        idx = -1
        def task_sampler():
            nonlocal idx
            idx = (idx + 1) % len(wrapped_tasks) if wrapped_tasks else 0
            return wrapped_tasks[idx] if wrapped_tasks else SimpleTask("Navigate to homepage", project)
        
        # Training loop
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()
            
            # Create executor and environment
            backend_service = BackendDemoWebService(project)
            executor = PlaywrightBrowserExecutor(
                browser_config=BrowserSpecification(),
                page=page,
                backend_demo_webs_service=backend_service,
            )
            
            env = AsyncWebAgentEnv(
                executor=executor,
                task_sampler=task_sampler,
                reward_fn=reward_function,
                reset_fn=lambda task: None,
                H=320,
                W=320,
                max_steps=self.max_steps_per_episode,
                action_mode="json",
                safe_action_types=["WaitAction", "ScrollAction", "ClickAction", "TypeAction", "NavigateAction", "SubmitAction", "HoverAction"],
                history_k=0,
                include_html=False,
            )
            
            # Training batches
            for batch_idx in range(self.num_batches):
                logger.info(f"Batch {batch_idx + 1}/{self.num_batches}")
                batch = []
                
                # Generate episodes for this batch
                for episode_idx in range(self.episodes_per_batch):
                    try:
                        obs = await env.reset()
                        done = False
                        step = 0
                        
                        obs_seq = []
                        act_seq = []
                        rew_seq = []
                        
                        while not done and step < self.max_steps_per_episode:
                            action = await policy.act(obs)
                            act_seq.append(0)  # Simplified action index
                            
                            result = await env.step(action)
                            reward = result["reward"]
                            done = result["done"]
                            
                            obs_seq.append(obs)
                            rew_seq.append(reward)
                            
                            obs = result["obs"]
                            step += 1
                        
                        batch.append({
                            "obs": obs_seq,
                            "acts": act_seq,
                            "rews": rew_seq,
                        })
                    except Exception as e:
                        logger.error(f"Episode {episode_idx + 1} failed: {e}")
                        batch.append({
                            "obs": [{"url": "about:blank", "task_prompt": "", "step": 0}],
                            "acts": [0],
                            "rews": [0.0]
                        })
                
                # Update policy
                if batch:
                    stats = policy.update(batch, gamma=0.99)
                    logger.info(f"Batch {batch_idx + 1}: Loss={stats.get('loss', 0):.4f}")
            
            await context.close()
            await browser.close()
    
    async def train_unified_model_async(
        self,
        project_configs: Dict[str, Dict[str, Any]] = None,
        learning_rate: float = 1e-3,
    ) -> Dict[str, Any]:
        """
        Train unified model on multiple projects (async version).
        
        Args:
            project_configs: Project configurations
            learning_rate: Learning rate for training
            
        Returns:
            Training results
        """
        if project_configs is None:
            # Default: use all projects with all use cases
            project_configs = {pid: {"num_use_cases": 0} for pid in self.project_ids}
        
        print(f"\n🚀 Training Unified Multi-Project Model")
        print(f"📋 Projects: {list(project_configs.keys())}")
        print("=" * 80)
        
        # Display project configurations
        for project_id, config in project_configs.items():
            num_use_cases = config.get("num_use_cases", 0)
            use_case_ids = config.get("use_case_ids", None)
            if use_case_ids:
                print(f"   {project_id}: Use cases {use_case_ids}")
            else:
                print(f"   {project_id}: {'All' if num_use_cases == 0 else num_use_cases} use cases")
        
        try:
            # Create unified policy and reward function
            policy = UnifiedMultiProjectPolicy(
                name="UnifiedMultiProjectPolicy",
                learning_rate=learning_rate,
            )
            
            reward_function = UnifiedMultiProjectRewardFunction(
                name="UnifiedMultiProjectReward",
            )
            
            # Train on all projects
            for project_id, config in project_configs.items():
                print(f"\n📍 Training on project: {project_id}")
                
                # Generate tasks for this project
                project = next((p for p in self.available_projects if p.id == project_id), None)
                if not project:
                    print(f"⚠️ Project {project_id} not found, skipping")
                    continue
                
                # Train on this project using async training loop
                await self._train_on_project(
                    policy=policy,
                    reward_function=reward_function,
                    project=project,
                )
                
                print(f"✅ Training completed on {project_id}")
            
            # Save unified model
            unified_model_path = self.output_dir / "unified_multi_project_model.pt"
            policy.save(str(unified_model_path))
            
            result = {
                "success": True,
                "unified_model_path": str(unified_model_path),
                "project_configs": project_configs,
                "training_stats": policy.training_stats,
                "timestamp": datetime.now().isoformat(),
            }
            
            print(f"\n🎉 Unified Multi-Project Training Completed!")
            print(f"📁 Unified model saved to: {unified_model_path}")
            print(f"📊 Training stats: {policy.training_stats}")
            
            return result
            
        except Exception as e:
            error_msg = f"Unified training failed: {e}"
            print(f"❌ {error_msg}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
            }
    
    def train_unified_model(
        self,
        project_configs: Dict[str, Dict[str, Any]] = None,
        learning_rate: float = 1e-3,
    ) -> Dict[str, Any]:
        """
        Train unified model on multiple projects (synchronous wrapper).
        
        Args:
            project_configs: Project configurations
            learning_rate: Learning rate for training
            
        Returns:
            Training results
        """
        import asyncio
        return asyncio.run(self.train_unified_model_async(project_configs, learning_rate))
    
    def evaluate_unified_model(
        self,
        model_path: str,
        project_ids: List[str] = None,
        num_episodes: int = 3,
    ) -> Dict[str, Any]:
        """
        Evaluate unified model on multiple projects.
        
        Args:
            model_path: Path to the unified model
            project_ids: List of project IDs to evaluate on
            num_episodes: Number of episodes per project
            
        Returns:
            Evaluation results
        """
        if project_ids is None:
            project_ids = self.project_ids
        
        print(f"\n📊 Evaluating Unified Model")
        print(f"📋 Projects: {project_ids}")
        print(f"📁 Model: {model_path}")
        print("=" * 80)
        
        try:
            # Load unified model
            policy = UnifiedMultiProjectPolicy(name="UnifiedMultiProjectPolicy_Eval")
            policy.load(model_path)
            
            reward_function = UnifiedMultiProjectRewardFunction(name="UnifiedMultiProjectReward_Eval")
            
            # Evaluate on each project
            evaluation_results = {}
            
            for project_id in project_ids:
                print(f"\n📍 Evaluating on project: {project_id}")
                
                try:
                    results = evaluate_policy(
                        policy=policy,
                        reward_function=reward_function,
                        project_id=project_id,
                        headless=self.headless,
                        num_episodes=num_episodes,
                        max_steps_per_episode=self.max_steps_per_episode,
                    )
                    
                    evaluation_results[project_id] = results
                    print(f"✅ Evaluation completed on {project_id}")
                    print(f"   Success Rate: {results['summary']['success_rate']:.1%}")
                    print(f"   Average Reward: {results['summary']['avg_reward']:.3f}")
                    
                except Exception as e:
                    print(f"❌ Evaluation failed on {project_id}: {e}")
                    evaluation_results[project_id] = {"error": str(e)}
            
            # Save evaluation results
            results_file = self.output_dir / "unified_model_evaluation.json"
            with open(results_file, 'w') as f:
                json.dump(evaluation_results, f, indent=2)
            
            print(f"\n📊 Unified Model Evaluation Completed!")
            print(f"📁 Results saved to: {results_file}")
            
            return evaluation_results
            
        except Exception as e:
            error_msg = f"Unified evaluation failed: {e}"
            print(f"❌ {error_msg}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            
            return {"error": error_msg}


def main():
    """Main function demonstrating unified multi-project training."""
    print("🚀 Unified Multi-Project Training with UserPolicy and UserRewardFunction")
    print("=" * 80)
    
    # Initialize trainer
    trainer = UnifiedMultiProjectTrainer(
        output_dir="trained_models_unified",
        headless=True,
        episodes_per_batch=3,
        num_batches=5,
        max_steps_per_episode=15,
    )
    
    # Define project configurations
    project_configs = {
        "work": {"num_use_cases": 2},
        "dining": {"num_use_cases": 1},
        "cinema": {"num_use_cases": 0},  # All use cases
        "books": {"num_use_cases": 1},
    }
    
    print(f"📋 Project Configurations:")
    for project_id, config in project_configs.items():
        num_use_cases = config.get("num_use_cases", 0)
        print(f"   {project_id}: {'All' if num_use_cases == 0 else num_use_cases} use cases")
    
    try:
        # Train unified model
        results = trainer.train_unified_model(
            project_configs=project_configs,
            learning_rate=1e-3,
        )
        
        if results["success"]:
            # Evaluate unified model
            evaluation_results = trainer.evaluate_unified_model(
                model_path=results["unified_model_path"],
                project_ids=list(project_configs.keys()),
                num_episodes=2,
            )
            
            print(f"\n🎯 Unified Multi-Project Training Summary:")
            print(f"📁 Model: {results['unified_model_path']}")
            print(f"📊 Training Stats: {results['training_stats']}")
            
            if "error" not in evaluation_results:
                print(f"📈 Evaluation Results:")
                for project_id, eval_results in evaluation_results.items():
                    if "error" not in eval_results:
                        success_rate = eval_results['summary']['success_rate']
                        avg_reward = eval_results['summary']['avg_reward']
                        print(f"   {project_id}: {success_rate:.1%} success, {avg_reward:.3f} avg reward")
        
        print(f"\n🎉 Unified Multi-Project Training Completed!")
        
    except Exception as e:
        print(f"💥 Training failed: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    main()
