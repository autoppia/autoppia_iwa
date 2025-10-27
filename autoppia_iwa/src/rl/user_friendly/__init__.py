"""
User-friendly RL environment package.

This package provides a user-friendly interface for training and evaluating
reinforcement learning agents for web automation tasks.

Key Components:
- base.py: Base classes for policies and reward functions
- trainer.py: Training interface with task generation integration
- evaluator.py: Evaluation interface with benchmark integration
- examples.py: Example implementations of policies and reward functions

Quick Start:
    from autoppia_iwa.src.rl.user_friendly import SimplePolicy, SimpleRewardFunction
    from autoppia_iwa.src.rl.user_friendly.trainer import train_policy
    from autoppia_iwa.src.rl.user_friendly.evaluator import evaluate_policy
    
    # Create policy and reward function
    policy = SimplePolicy(name="MyPolicy")
    reward_function = SimpleRewardFunction(name="MyReward")
    
    # Train the policy
    model_path = train_policy(policy, reward_function, project_id="work")
    
    # Evaluate the policy
    results = evaluate_policy(policy, reward_function, project_id="work")
"""

from .base import (
    UserPolicy,
    UserRewardFunction,
    SimplePolicy,
    SimpleRewardFunction,
    RandomPolicy,
)
from .trainer import RLTrainer, train_policy
from .evaluator import RLEvaluator, evaluate_policy, load_and_evaluate_policy
from .examples import (
    CNNPolicy,
    EpsilonGreedyPolicy,
    ProgressRewardFunction,
    SparseRewardFunction,
    CuriosityRewardFunction,
)

__all__ = [
    # Base classes
    "UserPolicy",
    "UserRewardFunction",
    "SimplePolicy",
    "SimpleRewardFunction",
    "RandomPolicy",
    
    # Training
    "RLTrainer",
    "train_policy",
    
    # Evaluation
    "RLEvaluator",
    "evaluate_policy",
    "load_and_evaluate_policy",
    
    # Example implementations
    "CNNPolicy",
    "EpsilonGreedyPolicy",
    "ProgressRewardFunction",
    "SparseRewardFunction",
    "CuriosityRewardFunction",
]
