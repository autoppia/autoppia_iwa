"""
User-friendly RL evaluation interface.

This module provides a unified interface for evaluating trained RL agents
using the benchmark system.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

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


class RLEvaluator:
    """
    Unified evaluation interface for RL agents.
    
    This class provides a simple interface for evaluating trained RL agents
    using the benchmark system and task generation.
    """
    
    def __init__(
        self,
        policy: UserPolicy,
        reward_function: UserRewardFunction,
        project_id: str,
        headless: bool = True,
        max_steps_per_episode: int = 30,
        num_episodes: int = 5,
        use_cached_tasks: bool = True,
        prompts_per_use_case: int = 1,
        num_use_cases: int = 1,
        record_gif: bool = False,
    ):
        """
        Initialize the RL evaluator.
        
        Args:
            policy: Trained policy to evaluate
            reward_function: Reward function to use
            project_id: ID of the demo web project to use
            headless: Whether to run browser in headless mode
            max_steps_per_episode: Maximum steps per episode
            num_episodes: Number of episodes to run
            use_cached_tasks: Whether to use cached tasks
            prompts_per_use_case: Number of prompts per use case
            num_use_cases: Number of use cases to use (0 = all)
            record_gif: Whether to record GIFs of episodes
        """
        self.policy = policy
        self.reward_function = reward_function
        self.project_id = project_id
        self.headless = headless
        self.max_steps_per_episode = max_steps_per_episode
        self.num_episodes = num_episodes
        self.use_cached_tasks = use_cached_tasks
        self.prompts_per_use_case = prompts_per_use_case
        self.num_use_cases = num_use_cases
        self.record_gif = record_gif
        
        # Find project
        self.project = next((p for p in demo_web_projects if p.id == project_id), None)
        if not self.project:
            available_ids = [p.id for p in demo_web_projects]
            raise ValueError(f"Project '{project_id}' not found. Available: {available_ids}")
        
        logger.info(f"Evaluating on project: {self.project.name}")
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
        max_steps: int,
        episode_idx: int
    ) -> Dict[str, Any]:
        """Run a single episode and return detailed results."""
        traj = {"obs": [], "acts": [], "rews": [], "actions": [], "info": []}
        task = env.task_sampler()
        
        try:
            obs, _ = await asyncio.wait_for(
                env.areset(options={"task": task, "prompt": getattr(task, "prompt", "")}), 
                timeout=20.0
            )
        except asyncio.TimeoutError:
            logger.warning("Environment reset timed out")
            obs = {"url": "about:blank", "task_prompt": "", "step": 0}
        
        logger.info(f"Episode {episode_idx + 1}: Task = '{getattr(task, 'prompt', 'No prompt')}'")
        
        for step in range(max_steps):
            try:
                # Get action from policy
                a_dict = await asyncio.wait_for(policy.act(obs), timeout=2.0)
                a_json = json.dumps(a_dict)
                
                # Store trajectory data
                traj["obs"].append(obs)
                traj["actions"].append(a_dict)
                
                # Find action index
                if hasattr(policy, 'action_index'):
                    act_idx = policy.action_index(a_dict)
                elif hasattr(policy, 'actions'):
                    try:
                        act_idx = policy.actions.index(a_dict)
                    except ValueError:
                        act_idx = 0
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
                
                logger.info(f"Step {step + 1}: Action = {a_dict.get('type', 'Unknown')}")
                
                # Execute action
                obs, r, d, t, info = await asyncio.wait_for(env.astep(a_json), timeout=5.0)
                traj["rews"].append(float(r))
                traj["info"].append(info)
                
                current_url = obs.get("url", "")
                logger.info(f"Step {step + 1}: Reward = {r:.3f}, URL = {current_url}")
                
                if d or t:
                    logger.info(f"Episode ended at step {step + 1}")
                    break
                    
            except asyncio.TimeoutError:
                logger.warning(f"Step {step} timed out")
                break
            except Exception as e:
                logger.warning(f"Step {step} failed: {e}")
                break
        
        return traj
    
    async def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate the policy and return detailed results.
        
        Returns:
            Dictionary containing evaluation results
        """
        logger.info(f"Starting evaluation for policy: {self.policy.name}")
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
        
        # Evaluation results
        results = {
            "policy_name": self.policy.name,
            "reward_function_name": self.reward_function.name,
            "project_id": self.project_id,
            "project_name": self.project.name,
            "episodes": [],
            "summary": {}
        }
        
        # Run evaluation episodes
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
                history_k=2,
                include_html=False,
            )
            
            # Run episodes
            success_count = 0
            total_rewards = []
            episode_lengths = []
            
            for episode_idx in range(self.num_episodes):
                logger.info(f"\n{'='*60}")
                logger.info(f"Running Episode {episode_idx + 1}/{self.num_episodes}")
                logger.info(f"{'='*60}")
                
                try:
                    traj = await asyncio.wait_for(
                        self._run_episode(env, self.policy, self.max_steps_per_episode, episode_idx),
                        timeout=120
                    )
                    
                    total_reward = sum(traj["rews"])
                    episode_length = len(traj["rews"])
                    
                    # Store episode results
                    episode_result = {
                        "episode": episode_idx + 1,
                        "total_reward": total_reward,
                        "episode_length": episode_length,
                        "actions_taken": [action.get('type', 'Unknown') for action in traj['actions']],
                        "final_url": traj["obs"][-1].get("url", "") if traj["obs"] else "",
                        "task_prompt": traj["obs"][0].get("task_prompt", "") if traj["obs"] else "",
                    }
                    results["episodes"].append(episode_result)
                    
                    total_rewards.append(total_reward)
                    episode_lengths.append(episode_length)
                    
                    logger.info(f"\n📊 Episode {episode_idx + 1} Results:")
                    logger.info(f"   Total Reward: {total_reward:.3f}")
                    logger.info(f"   Episode Length: {episode_length} steps")
                    logger.info(f"   Actions Taken: {episode_result['actions_taken']}")
                    
                    # Determine success
                    if total_reward > 0.1:  # Positive reward indicates some success
                        success_count += 1
                        logger.info(f"   ✅ Episode {episode_idx + 1} showed positive progress!")
                    else:
                        logger.info(f"   ❌ Episode {episode_idx + 1} needs improvement")
                    
                except asyncio.TimeoutError:
                    logger.error(f"⏰ Episode {episode_idx + 1} timed out after 120 seconds")
                    # Add failed episode result
                    episode_result = {
                        "episode": episode_idx + 1,
                        "total_reward": 0.0,
                        "episode_length": 0,
                        "actions_taken": [],
                        "final_url": "",
                        "task_prompt": "",
                        "error": "timeout"
                    }
                    results["episodes"].append(episode_result)
                    
                except Exception as e:
                    logger.error(f"💥 Episode {episode_idx + 1} failed: {e}")
                    # Add failed episode result
                    episode_result = {
                        "episode": episode_idx + 1,
                        "total_reward": 0.0,
                        "episode_length": 0,
                        "actions_taken": [],
                        "final_url": "",
                        "task_prompt": "",
                        "error": str(e)
                    }
                    results["episodes"].append(episode_result)
            
            # Calculate summary statistics
            results["summary"] = {
                "success_rate": success_count / self.num_episodes,
                "avg_reward": sum(total_rewards) / len(total_rewards) if total_rewards else 0.0,
                "avg_episode_length": sum(episode_lengths) / len(episode_lengths) if episode_lengths else 0.0,
                "total_episodes": self.num_episodes,
                "successful_episodes": success_count,
                "failed_episodes": self.num_episodes - success_count,
            }
            
            # Print final results
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 EVALUATION RESULTS")
            logger.info(f"{'='*60}")
            logger.info(f"Success Rate: {results['summary']['success_rate']:.1%}")
            logger.info(f"Average Reward: {results['summary']['avg_reward']:.3f}")
            logger.info(f"Average Episode Length: {results['summary']['avg_episode_length']:.1f}")
            logger.info(f"Successful Episodes: {success_count}/{self.num_episodes}")
            
            await context.close()
            await browser.close()
            
            return results


def evaluate_policy(
    policy: UserPolicy,
    reward_function: UserRewardFunction,
    project_id: str = "work",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to evaluate a policy.
    
    Args:
        policy: Trained policy to evaluate
        reward_function: Reward function to use
        project_id: ID of the demo web project to use
        **kwargs: Additional arguments passed to RLEvaluator
        
    Returns:
        Dictionary containing evaluation results
    """
    evaluator = RLEvaluator(policy, reward_function, project_id, **kwargs)
    return asyncio.run(evaluator.evaluate())


def load_and_evaluate_policy(
    policy_class: type,
    model_path: str,
    reward_function: UserRewardFunction,
    project_id: str = "work",
    **kwargs
) -> Dict[str, Any]:
    """
    Load a trained policy and evaluate it.
    
    Args:
        policy_class: Policy class to instantiate
        model_path: Path to the saved model
        reward_function: Reward function to use
        project_id: ID of the demo web project to use
        **kwargs: Additional arguments passed to RLEvaluator
        
    Returns:
        Dictionary containing evaluation results
    """
    # Create policy instance
    policy = policy_class()
    
    # Load the trained model
    policy.load(model_path)
    
    # Evaluate
    return evaluate_policy(policy, reward_function, project_id, **kwargs)


# Example usage
if __name__ == "__main__":
    from autoppia_iwa.src.rl.user_friendly.base import SimplePolicy, SimpleRewardFunction
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    
    # Create policy and reward function
    policy = SimplePolicy(name="MyPolicy")
    reward_function = SimpleRewardFunction(name="MyReward")
    
    # Evaluate the policy
    results = evaluate_policy(
        policy=policy,
        reward_function=reward_function,
        project_id="work",
        headless=True,
        num_episodes=3,
    )
    
    print(f"Evaluation completed!")
    print(f"Success Rate: {results['summary']['success_rate']:.1%}")
    print(f"Average Reward: {results['summary']['avg_reward']:.3f}")
