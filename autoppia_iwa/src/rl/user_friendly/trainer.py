"""
User-friendly RL training interface.

This module provides a unified interface for training RL agents with user-defined
policies and reward functions using the task generation system.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Callable

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.actions.actions import *  # Import all actions
from autoppia_iwa.src.rl.env import AsyncWebAgentEnv
from autoppia_iwa.src.rl.user_friendly.base import UserPolicy, UserRewardFunction
from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project


class RLTrainer:
    """
    Unified training interface for RL agents.
    
    This class provides a simple interface for training RL agents with user-defined
    policies and reward functions using the task generation system.
    """
    
    def __init__(
        self,
        policy: UserPolicy,
        reward_function: UserRewardFunction,
        project_id: str,
        output_dir: str = "trained_models",
        headless: bool = True,
        max_steps_per_episode: int = 20,
        episodes_per_batch: int = 5,
        num_batches: int = 10,
        use_cached_tasks: bool = True,
        prompts_per_use_case: int = 1,
        num_use_cases: int = 1,
    ):
        """
        Initialize the RL trainer.
        
        Args:
            policy: User-defined policy to train
            reward_function: User-defined reward function
            project_id: ID of the demo web project to use
            output_dir: Directory to save trained models
            headless: Whether to run browser in headless mode
            max_steps_per_episode: Maximum steps per episode
            episodes_per_batch: Number of episodes per training batch
            num_batches: Number of training batches
            use_cached_tasks: Whether to use cached tasks
            prompts_per_use_case: Number of prompts per use case
            num_use_cases: Number of use cases to use (0 = all)
        """
        self.policy = policy
        self.reward_function = reward_function
        self.project_id = project_id
        self.output_dir = Path(output_dir)
        self.headless = headless
        self.max_steps_per_episode = max_steps_per_episode
        self.episodes_per_batch = episodes_per_batch
        self.num_batches = num_batches
        self.use_cached_tasks = use_cached_tasks
        self.prompts_per_use_case = prompts_per_use_case
        self.num_use_cases = num_use_cases
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find project
        self.project = next((p for p in demo_web_projects if p.id == project_id), None)
        if not self.project:
            available_ids = [p.id for p in demo_web_projects]
            raise ValueError(f"Project '{project_id}' not found. Available: {available_ids}")
        
        logger.info(f"Using project: {self.project.name}")
        logger.info(f"Frontend URL: {self.project.frontend_url}")
        
    async def _reset_environment(self, executor: PlaywrightBrowserExecutor, task: Any) -> None:
        """Reset the environment to the task's starting state."""
        if executor.backend_demo_webs_service:
            try:
                await asyncio.wait_for(
                    executor.backend_demo_webs_service.reset_database(), 
                    timeout=10.0
                )
                logger.debug("Database reset successful")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Database reset failed: {e}")
        
        # Navigate to task URL
        start_url = getattr(task, "url", "") or getattr(task, "frontend_url", "") or self.project.frontend_url
        if executor.page:
            try:
                await asyncio.wait_for(executor.page.goto(start_url), timeout=15.0)
                logger.debug(f"Navigated to {start_url}")
            except Exception as e:
                logger.warning(f"Navigation failed: {e}")
    
    async def _run_episode(
        self, 
        env: AsyncWebAgentEnv, 
        policy: UserPolicy, 
        max_steps: int
    ) -> dict[str, Any]:
        """Run a single episode and return trajectory."""
        traj = {"obs": [], "acts": [], "rews": []}
        task = env.task_sampler()
        
        try:
            obs, _ = await asyncio.wait_for(
                env.areset(options={"task": task, "prompt": getattr(task, "prompt", "")}), 
                timeout=20.0
            )
        except asyncio.TimeoutError:
            logger.warning("Environment reset timed out")
            obs = {"url": "about:blank", "task_prompt": "", "step": 0}
        
        for step in range(max_steps):
            try:
                # Get action from policy
                a_dict = await asyncio.wait_for(policy.act(obs), timeout=5.0)
                a_json = json.dumps(a_dict)
                
                # Store trajectory data
                traj["obs"].append(obs)
                
                # Find action index (for policies that need it)
                if hasattr(policy, 'action_index'):
                    act_idx = policy.action_index(a_dict)
                elif hasattr(policy, 'actions'):
                    try:
                        act_idx = policy.actions.index(a_dict)
                    except ValueError:
                        act_idx = 0  # Default to first action if not found
                else:
                    act_idx = 0
                
                # Validate action index
                if hasattr(policy, 'num_actions'):
                    if act_idx < 0 or act_idx >= policy.num_actions:
                        logger.warning(f"Invalid action index {act_idx}, clamping to valid range [0, {policy.num_actions-1}]")
                        act_idx = max(0, min(act_idx, policy.num_actions - 1))
                elif hasattr(policy, 'actions'):
                    if act_idx < 0 or act_idx >= len(policy.actions):
                        logger.warning(f"Invalid action index {act_idx}, clamping to valid range [0, {len(policy.actions)-1}]")
                        act_idx = max(0, min(act_idx, len(policy.actions) - 1))
                
                traj["acts"].append(act_idx)
                
                # Execute action
                obs, r, d, t, info = await asyncio.wait_for(env.astep(a_json), timeout=15.0)
                traj["rews"].append(float(r))
                
                if d or t:
                    break
                    
            except asyncio.TimeoutError:
                logger.warning(f"Step {step} timed out")
                break
            except Exception as e:
                logger.warning(f"Step {step} failed: {e}")
                break
        
        return traj
    
    async def train(self) -> str:
        """
        Train the policy using the specified reward function.
        
        Returns:
            Path to the saved model file
        """
        logger.info(f"Starting training for policy: {self.policy.name}")
        logger.info(f"Using reward function: {self.reward_function.name}")
        
        # Load tasks
        logger.info("Loading tasks...")
        tasks = await generate_tasks_for_project(
            project=self.project,
            use_cached=self.use_cached_tasks,
            cache_dir="data/tasks_cache",
            prompts_per_use_case=self.prompts_per_use_case,
            num_use_cases=self.num_use_cases,
        )
        
        if not tasks:
            logger.warning("No tasks found, creating simple tasks...")
            # Create simple fallback tasks
            class SimpleTask:
                def __init__(self, prompt, project):
                    self.prompt = prompt
                    self.url = project.frontend_url
                    self.frontend_url = project.frontend_url
                    self.project = project
            
            tasks = [
                SimpleTask("Navigate to the homepage", self.project),
                SimpleTask("Search for content", self.project),
                SimpleTask("Click on a link", self.project),
            ]
        
        logger.info(f"Loaded {len(tasks)} tasks")
        
        # Task sampler
        idx = -1
        def task_sampler():
            nonlocal idx
            idx = (idx + 1) % len(tasks)
            return tasks[idx]
        
        # Training loop
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()
            
            # Create executor and environment
            backend_service = BackendDemoWebService(self.project)
            executor = PlaywrightBrowserExecutor(
                browser_config=BrowserSpecification(),
                page=page,
                backend_demo_webs_service=backend_service,
            )
            
            env = AsyncWebAgentEnv(
                executor=executor,
                task_sampler=task_sampler,
                reward_fn=self.reward_function,
                reset_fn=self._reset_environment,
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
                logger.info(f"Training batch {batch_idx + 1}/{self.num_batches}")
                
                batch = []
                for episode_idx in range(self.episodes_per_batch):
                    logger.info(f"Running episode {episode_idx + 1}/{self.episodes_per_batch}")
                    
                    try:
                        traj = await asyncio.wait_for(
                            self._run_episode(env, self.policy, self.max_steps_per_episode),
                            timeout=60
                        )
                        batch.append(traj)
                        
                        total_reward = sum(traj["rews"])
                        logger.info(f"Episode {episode_idx + 1}: Return={total_reward:.3f}, Length={len(traj['rews'])}")
                        
                    except asyncio.TimeoutError:
                        logger.error(f"Episode {episode_idx + 1} timed out")
                        # Add dummy trajectory to continue training
                        dummy_traj = {
                            "obs": [{"url": "about:blank", "task_prompt": "", "step": 0}],
                            "acts": [0],
                            "rews": [0.0]
                        }
                        batch.append(dummy_traj)
                    except Exception as e:
                        logger.error(f"Episode {episode_idx + 1} failed: {e}")
                        # Add dummy trajectory to continue training
                        dummy_traj = {
                            "obs": [{"url": "about:blank", "task_prompt": "", "step": 0}],
                            "acts": [0],
                            "rews": [0.0]
                        }
                        batch.append(dummy_traj)
                
                # Update policy
                if batch:
                    logger.info(f"Updating policy with {len(batch)} episodes...")
                    stats = self.policy.update(batch, gamma=0.99)
                    logger.info(f"Batch {batch_idx + 1}: Loss={stats.get('loss', 0):.4f} | "
                              f"Return={stats.get('avg_return', 0):.3f} | "
                              f"Length={stats.get('avg_len', 0):.1f}")
            
            # Save trained model
            model_path = self.output_dir / f"trained_{self.project_id}_{self.policy.name.lower()}.pt"
            self.policy.save(str(model_path))
            logger.info(f"Training completed! Model saved to {model_path}")
            
            await context.close()
            await browser.close()
            
            return str(model_path)


def train_policy(
    policy: UserPolicy,
    reward_function: UserRewardFunction,
    project_id: str = "work",
    **kwargs
) -> str:
    """
    Convenience function to train a policy.
    
    Args:
        policy: User-defined policy to train
        reward_function: User-defined reward function
        project_id: ID of the demo web project to use
        **kwargs: Additional arguments passed to RLTrainer
        
    Returns:
        Path to the saved model file
    """
    trainer = RLTrainer(policy, reward_function, project_id, **kwargs)
    return asyncio.run(trainer.train())


# Example usage
if __name__ == "__main__":
    from autoppia_iwa.src.rl.user_friendly.base import SimplePolicy, SimpleRewardFunction
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    
    # Create policy and reward function
    policy = SimplePolicy(name="MyPolicy")
    reward_function = SimpleRewardFunction(name="MyReward")
    
    # Train the policy
    model_path = train_policy(
        policy=policy,
        reward_function=reward_function,
        project_id="work",
        headless=True,
        episodes_per_batch=3,
        num_batches=5,
    )
    
    print(f"Training completed! Model saved to: {model_path}")
