#!/usr/bin/env python3
"""
Evaluation Script for Unified Multi-Project Model

This script provides various ways to evaluate the trained unified model.
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the unified model components
from unified_user_policy_model import (
    UnifiedMultiProjectPolicy,
    UnifiedMultiProjectRewardFunction,
    UnifiedMultiProjectTrainer,
)
from autoppia_iwa.src.rl.user_friendly.evaluator import evaluate_policy


class UnifiedModelEvaluator:
    """Evaluator for unified multi-project model."""
    
    def __init__(self, model_path: str):
        """
        Initialize evaluator with model path.
        
        Args:
            model_path: Path to the trained unified model
        """
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Load the model
        self.policy = UnifiedMultiProjectPolicy(name="EvaluationPolicy")
        self.policy.load(str(self.model_path))
        
        self.reward_function = UnifiedMultiProjectRewardFunction(name="EvaluationReward")
        
        print(f"🚀 Unified Model Evaluator Initialized")
        print(f"📁 Model: {self.model_path}")
        print(f"📊 Training Stats: {self.policy.training_stats}")
    
    def evaluate_single_project(
        self,
        project_id: str,
        num_episodes: int = 5,
        max_steps_per_episode: int = 20,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate model on a single project.
        
        Args:
            project_id: Project ID to evaluate on
            num_episodes: Number of episodes to run
            max_steps_per_episode: Maximum steps per episode
            headless: Whether to run browser in headless mode
            
        Returns:
            Evaluation results
        """
        print(f"\n📊 Evaluating on project: {project_id}")
        print("=" * 50)
        
        try:
            results = evaluate_policy(
                policy=self.policy,
                reward_function=self.reward_function,
                project_id=project_id,
                headless=headless,
                num_episodes=num_episodes,
                max_steps_per_episode=max_steps_per_episode,
            )
            
            print(f"✅ Evaluation completed!")
            print(f"   Success Rate: {results['summary']['success_rate']:.1%}")
            print(f"   Average Reward: {results['summary']['avg_reward']:.3f}")
            print(f"   Average Length: {results['summary']['avg_episode_length']:.1f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            return {"error": str(e)}
    
    def evaluate_multiple_projects(
        self,
        project_ids: List[str],
        num_episodes: int = 3,
        max_steps_per_episode: int = 20,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate model on multiple projects.
        
        Args:
            project_ids: List of project IDs to evaluate on
            num_episodes: Number of episodes per project
            max_steps_per_episode: Maximum steps per episode
            headless: Whether to run browser in headless mode
            
        Returns:
            Evaluation results for all projects
        """
        print(f"\n📊 Evaluating on Multiple Projects")
        print(f"📋 Projects: {project_ids}")
        print("=" * 60)
        
        results = {}
        
        for project_id in project_ids:
            project_results = self.evaluate_single_project(
                project_id=project_id,
                num_episodes=num_episodes,
                max_steps_per_episode=max_steps_per_episode,
                headless=headless,
            )
            results[project_id] = project_results
        
        # Summary
        print(f"\n🎯 Evaluation Summary:")
        print("=" * 30)
        
        successful_projects = 0
        total_success_rate = 0.0
        total_avg_reward = 0.0
        
        for project_id, project_results in results.items():
            if "error" not in project_results:
                successful_projects += 1
                success_rate = project_results['summary']['success_rate']
                avg_reward = project_results['summary']['avg_reward']
                total_success_rate += success_rate
                total_avg_reward += avg_reward
                
                print(f"   {project_id}: {success_rate:.1%} success, {avg_reward:.3f} avg reward")
            else:
                print(f"   {project_id}: ❌ Failed ({project_results['error']})")
        
        if successful_projects > 0:
            avg_success_rate = total_success_rate / successful_projects
            avg_reward = total_avg_reward / successful_projects
            
            print(f"\n📈 Overall Performance:")
            print(f"   Average Success Rate: {avg_success_rate:.1%}")
            print(f"   Average Reward: {avg_reward:.3f}")
            print(f"   Successful Projects: {successful_projects}/{len(project_ids)}")
        
        return results
    
    def evaluate_all_projects(
        self,
        num_episodes: int = 3,
        max_steps_per_episode: int = 20,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate model on all available projects.
        
        Args:
            num_episodes: Number of episodes per project
            max_steps_per_episode: Maximum steps per episode
            headless: Whether to run browser in headless mode
            
        Returns:
            Evaluation results for all projects
        """
        all_project_ids = self.policy.project_ids
        
        print(f"📋 Evaluating on ALL projects: {all_project_ids}")
        
        return self.evaluate_multiple_projects(
            project_ids=all_project_ids,
            num_episodes=num_episodes,
            max_steps_per_episode=max_steps_per_episode,
            headless=headless,
        )
    
    def save_evaluation_results(
        self,
        results: Dict[str, Any],
        output_file: str = None,
    ) -> str:
        """
        Save evaluation results to file.
        
        Args:
            results: Evaluation results dictionary
            output_file: Output file path (optional)
            
        Returns:
            Path to saved file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"evaluation_results_{timestamp}.json"
        
        output_path = Path(output_file)
        
        # Add metadata
        save_data = {
            "model_path": str(self.model_path),
            "evaluation_time": datetime.now().isoformat(),
            "training_stats": self.policy.training_stats,
            "results": results,
        }
        
        with open(output_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"💾 Evaluation results saved to: {output_path}")
        return str(output_path)


def evaluate_single_project_cli():
    """CLI for evaluating on a single project."""
    print("🚀 Single Project Evaluation")
    print("=" * 40)
    
    # Get model path
    model_path = input("Enter model path (default: trained_models_unified/unified_multi_project_model.pt): ").strip()
    if not model_path:
        model_path = "trained_models_unified/unified_multi_project_model.pt"
    
    # Get project ID
    project_id = input("Enter project ID (work, dining, cinema, books, etc.): ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return
    
    # Get number of episodes
    try:
        num_episodes = int(input("Number of episodes (default: 5): ") or "5")
    except ValueError:
        num_episodes = 5
    
    try:
        # Initialize evaluator
        evaluator = UnifiedModelEvaluator(model_path)
        
        # Evaluate
        results = evaluator.evaluate_single_project(
            project_id=project_id,
            num_episodes=num_episodes,
        )
        
        # Save results
        if "error" not in results:
            evaluator.save_evaluation_results(results)
        
    except Exception as e:
        print(f"💥 Evaluation failed: {e}")


def evaluate_multiple_projects_cli():
    """CLI for evaluating on multiple projects."""
    print("🚀 Multiple Projects Evaluation")
    print("=" * 40)
    
    # Get model path
    model_path = input("Enter model path (default: trained_models_unified/unified_multi_project_model.pt): ").strip()
    if not model_path:
        model_path = "trained_models_unified/unified_multi_project_model.pt"
    
    # Get project IDs
    project_input = input("Enter project IDs (comma-separated, default: work,dining,cinema): ").strip()
    if not project_input:
        project_ids = ["work", "dining", "cinema"]
    else:
        project_ids = [pid.strip() for pid in project_input.split(",")]
    
    # Get number of episodes
    try:
        num_episodes = int(input("Number of episodes per project (default: 3): ") or "3")
    except ValueError:
        num_episodes = 3
    
    try:
        # Initialize evaluator
        evaluator = UnifiedModelEvaluator(model_path)
        
        # Evaluate
        results = evaluator.evaluate_multiple_projects(
            project_ids=project_ids,
            num_episodes=num_episodes,
        )
        
        # Save results
        evaluator.save_evaluation_results(results)
        
    except Exception as e:
        print(f"💥 Evaluation failed: {e}")


def evaluate_all_projects_cli():
    """CLI for evaluating on all projects."""
    print("🚀 All Projects Evaluation")
    print("=" * 40)
    
    # Get model path
    model_path = input("Enter model path (default: trained_models_unified/unified_multi_project_model.pt): ").strip()
    if not model_path:
        model_path = "trained_models_unified/unified_multi_project_model.pt"
    
    # Get number of episodes
    try:
        num_episodes = int(input("Number of episodes per project (default: 2): ") or "2")
    except ValueError:
        num_episodes = 2
    
    try:
        # Initialize evaluator
        evaluator = UnifiedModelEvaluator(model_path)
        
        # Evaluate
        results = evaluator.evaluate_all_projects(
            num_episodes=num_episodes,
        )
        
        # Save results
        evaluator.save_evaluation_results(results)
        
    except Exception as e:
        print(f"💥 Evaluation failed: {e}")


def main():
    """Main function with evaluation options."""
    print("🚀 Unified Multi-Project Model Evaluation")
    print("=" * 60)
    
    print("📋 Evaluation Options:")
    print("1. Evaluate on single project")
    print("2. Evaluate on multiple projects")
    print("3. Evaluate on all projects")
    print("4. Quick evaluation (work, dining, cinema)")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice == "1":
        evaluate_single_project_cli()
    elif choice == "2":
        evaluate_multiple_projects_cli()
    elif choice == "3":
        evaluate_all_projects_cli()
    elif choice == "4":
        # Quick evaluation
        try:
            evaluator = UnifiedModelEvaluator("trained_models_unified/unified_multi_project_model.pt")
            results = evaluator.evaluate_multiple_projects(
                project_ids=["work", "dining", "cinema"],
                num_episodes=2,
            )
            evaluator.save_evaluation_results(results)
        except Exception as e:
            print(f"💥 Quick evaluation failed: {e}")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
