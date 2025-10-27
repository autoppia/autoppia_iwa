# User-Friendly RL Environment

A comprehensive framework for training and evaluating reinforcement learning agents for web automation tasks.

## 📦 Installation

### Prerequisites

Make sure you have Python 3.8+ installed.

### Install Dependencies

1. **Install core dependencies:**
   ```bash
   pip install torch>=2.1.0 numpy>=2.0.0 loguru>=0.7.3
   ```

2. **Install web automation dependencies:**
   ```bash
   pip install playwright>=1.49.0 aiohttp>=3.10.0
   playwright install chromium  # Install browser
   ```

3. **Install from requirements file:**
   ```bash
   pip install -r autoppia_iwa/src/rl/user_friendly/requirements.txt
   ```

4. **Note about gymnasium:**
   The user-friendly RL environment uses `AsyncWebAgentEnv` which requires `gymnasium`. If you're using the full IWA system, `gymnasium` should already be installed. If you're using the user-friendly RL environment standalone, you may need:
   ```bash
   pip install gymnasium>=0.29.0
   ```

5. **Or install everything at once:**
   ```bash
   pip install torch numpy loguru playwright aiohttp gymnasium
   playwright install chromium
   ```

### Verify Installation

```python
# Test that all imports work
from autoppia_iwa.src.rl.user_friendly import SimplePolicy, SimpleRewardFunction
print("✅ Installation successful!")
```

## 🚀 Quick Start

```python
from autoppia_iwa.src.rl.user_friendly import SimplePolicy, SimpleRewardFunction
from autoppia_iwa.src.rl.user_friendly.trainer import train_policy
from autoppia_iwa.src.rl.user_friendly.evaluator import evaluate_policy

# 1. Create policy and reward function
policy = SimplePolicy(name="MyPolicy")
reward_function = SimpleRewardFunction(name="MyReward")

# 2. Train the policy
model_path = train_policy(
    policy=policy,
    reward_function=reward_function,
    project_id="work",  # Use demo web project
    headless=True,
    episodes_per_batch=3,
    num_batches=5,
)

# 3. Evaluate the policy
results = evaluate_policy(
    policy=policy,
    reward_function=reward_function,
    project_id="work",
    headless=True,
    num_episodes=3,
)

print(f"Success Rate: {results['summary']['success_rate']:.1%}")
print(f"Average Reward: {results['summary']['avg_reward']:.3f}")
```

## 📚 Key Features

### 1. **Easy Policy Definition**
Define your own policies by inheriting from `UserPolicy`:

```python
class MyCustomPolicy(UserPolicy):
    def __init__(self, name="MyCustomPolicy"):
        super().__init__(name)
        self.actions = [
            {"type": "WaitAction", "time_seconds": 0.5},
            {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "button"}},
            {"type": "TypeAction", "selector": {"type": "attributeValueSelector", "attribute": "placeholder", "value": "Search"}, "text": "hello"},
        ]
    
    async def act(self, obs):
        # Your action selection logic here
        step = obs.get("step", 0)
        return self.actions[step % len(self.actions)]
    
    def update(self, batch_trajectories, **kwargs):
        # Your learning algorithm here
        return {"loss": 0.0, "avg_return": 0.0, "avg_len": 0.0}
```

### 2. **Custom Reward Functions**
Define your own reward functions by inheriting from `UserRewardFunction`:

```python
class MyCustomRewardFunction(UserRewardFunction):
    async def __call__(self, *, task, step_idx, last_action_dict, last_action_obj, 
                      executor, trajectory, obs, result):
        reward = 0.0
        current_url = obs.get("url", "")
        
        # Reward logic here
        if "search" in current_url.lower():
            reward += 0.5
        
        done = step_idx >= 15
        info = {"step": step_idx, "url": current_url, "reward": reward}
        
        return reward, done, info
```

### 3. **Integrated Training**
Train your policies using the task generation system:

```python
from autoppia_iwa.src.rl.user_friendly.trainer import RLTrainer

trainer = RLTrainer(
    policy=policy,
    reward_function=reward_function,
    project_id="work",
    episodes_per_batch=5,
    num_batches=10,
    use_cached_tasks=True,  # Use cached tasks for faster training
)

model_path = await trainer.train()
```

### 4. **Comprehensive Evaluation**
Evaluate your trained policies with detailed metrics:

```python
from autoppia_iwa.src.rl.user_friendly.evaluator import RLEvaluator

evaluator = RLEvaluator(
    policy=policy,
    reward_function=reward_function,
    project_id="work",
    num_episodes=5,
    record_gif=True,  # Record episodes as GIFs
)

results = await evaluator.evaluate()
```

## 🎯 Available Projects

The framework supports multiple demo web projects:

- **work**: Work management application
- **dining**: Restaurant booking system
- **cinema**: Movie ticket booking
- **books**: Online bookstore
- **omnizone**: E-commerce platform
- **crm**: Customer relationship management
- **automail**: Email automation
- **autodelivery**: Delivery management
- **lodge**: Hotel booking
- **connect**: Social networking

## 🧠 Example Policies

### Simple Policy
Basic neural network policy with predefined actions:

```python
from autoppia_iwa.src.rl.user_friendly import SimplePolicy

policy = SimplePolicy(
    actions=[...],  # Your action space
    hidden_size=64,
    learning_rate=3e-3,
)
```

### CNN Policy
Convolutional neural network for image-based decisions:

```python
from autoppia_iwa.src.rl.user_friendly.examples import CNNPolicy

policy = CNNPolicy(
    actions=[...],  # Your action space
    learning_rate=3e-3,
)
```

### Epsilon-Greedy Policy
Q-learning with epsilon-greedy exploration:

```python
from autoppia_iwa.src.rl.user_friendly.examples import EpsilonGreedyPolicy

policy = EpsilonGreedyPolicy(
    actions=[...],  # Your action space
    epsilon=0.1,
    epsilon_decay=0.995,
)
```

## 🎁 Example Reward Functions

### Progress Reward
Rewards progress towards task completion:

```python
from autoppia_iwa.src.rl.user_friendly.examples import ProgressRewardFunction

reward_function = ProgressRewardFunction(
    progress_bonus=0.1,
    action_bonus=0.05,
    step_penalty=0.01,
)
```

### Sparse Reward
Only rewards task completion:

```python
from autoppia_iwa.src.rl.user_friendly.examples import SparseRewardFunction

reward_function = SparseRewardFunction(
    completion_reward=1.0,
    step_penalty=0.001,
)
```

### Curiosity Reward
Rewards exploration and novelty:

```python
from autoppia_iwa.src.rl.user_friendly.examples import CuriosityRewardFunction

reward_function = CuriosityRewardFunction(
    exploration_bonus=0.1,
    novelty_bonus=0.2,
)
```

## 🔧 Advanced Usage

### Custom Training Configuration

```python
trainer = RLTrainer(
    policy=policy,
    reward_function=reward_function,
    project_id="work",
    output_dir="my_models",
    headless=False,  # Show browser window
    max_steps_per_episode=30,
    episodes_per_batch=10,
    num_batches=20,
    use_cached_tasks=True,
    prompts_per_use_case=2,
    num_use_cases=3,  # Use first 3 use cases
)
```

### Custom Evaluation Configuration

```python
evaluator = RLEvaluator(
    policy=policy,
    reward_function=reward_function,
    project_id="work",
    headless=False,  # Show browser window
    max_steps_per_episode=50,
    num_episodes=10,
    use_cached_tasks=True,
    record_gif=True,  # Record episodes
)
```

### Loading and Evaluating Saved Models

```python
from autoppia_iwa.src.rl.user_friendly.evaluator import load_and_evaluate_policy

results = load_and_evaluate_policy(
    policy_class=MyCustomPolicy,
    model_path="trained_model.pt",
    reward_function=reward_function,
    project_id="work",
    num_episodes=5,
)
```

## 📊 Benchmark Integration

The framework integrates with the existing benchmark system:

```python
# Train on multiple projects
projects = ["work", "dining", "cinema"]

for project_id in projects:
    model_path = train_policy(
        policy=policy,
        reward_function=reward_function,
        project_id=project_id,
        episodes_per_batch=5,
        num_batches=10,
    )
    print(f"Trained on {project_id}: {model_path}")

# Cross-project evaluation
for project_id in projects:
    results = evaluate_policy(
        policy=policy,
        reward_function=reward_function,
        project_id=project_id,
        num_episodes=3,
    )
    print(f"{project_id}: {results['summary']['success_rate']:.1%} success rate")
```

## 🛠️ Development

### Creating Your Own Policy

1. Inherit from `UserPolicy`
2. Implement `act()` method for action selection
3. Implement `update()` method for learning
4. Optionally implement `save()` and `load()` methods

### Creating Your Own Reward Function

1. Inherit from `UserRewardFunction`
2. Implement `__call__()` method for reward calculation
3. Optionally implement `reset_episode_state()` method

### Testing Your Implementation

```python
# Test your policy
policy = MyCustomPolicy()
obs = {"url": "http://example.com", "step": 0, "task_prompt": "test"}
action = await policy.act(obs)
print(f"Selected action: {action}")

# Test your reward function
reward_function = MyCustomRewardFunction()
reward, done, info = await reward_function(
    task=task,
    step_idx=0,
    last_action_dict=action,
    last_action_obj=None,
    executor=executor,
    trajectory=[],
    obs=obs,
    result=None,
)
print(f"Reward: {reward}, Done: {done}")
```

## 📝 Examples

See the `examples.py` file for complete working examples of:

- Custom policy implementations
- Custom reward function implementations
- Complete training workflows
- Evaluation and comparison
- Benchmark integration

## 🤝 Contributing

To add new example policies or reward functions:

1. Add your implementation to `examples.py`
2. Update the `__all__` list in `__init__.py`
3. Add documentation and examples
4. Test with different projects and configurations

## 🌐 Unified Multi-Project Training

The framework now supports unified multi-project training, allowing you to train a single model that can work across multiple web automation projects.

### 🚀 Quick Start - Unified Training

```python
from autoppia_iwa.src.rl.user_friendly import (
    train_unified_multi_project,
    evaluate_unified_model,
)

# Define project configurations
project_configs = {
    "work": {"num_use_cases": 2},
    "dining": {"num_use_cases": 1},
    "cinema": {"num_use_cases": 0},  # All use cases
    "books": {"num_use_cases": 1},
}

# Train unified model
results = train_unified_multi_project(
    project_configs=project_configs,
    output_dir="trained_models_unified",
    learning_rate=1e-3,
    episodes_per_batch=3,
    num_batches=5,
)

# Evaluate the unified model
evaluation_results = evaluate_unified_model(
    model_path=results["unified_model_path"],
    project_ids=["work", "dining", "cinema"],
    num_episodes=2,
)
```

### 🔧 Advanced Unified Training

```python
from autoppia_iwa.src.rl.user_friendly import (
    UnifiedMultiProjectPolicy,
    UnifiedMultiProjectRewardFunction,
    UnifiedMultiProjectTrainer,
)

# Create trainer
trainer = UnifiedMultiProjectTrainer(
    output_dir="my_unified_models",
    episodes_per_batch=5,
    num_batches=10,
    max_steps_per_episode=20,
)

# Train with custom configuration
results = trainer.train_unified_model(
    project_configs={
        "work": {"num_use_cases": 3},
        "dining": {"num_use_cases": 2},
        "cinema": {"num_use_cases": 0},  # All use cases
    },
    learning_rate=1e-4,
)

# Evaluate on specific projects
evaluation_results = trainer.evaluate_unified_model(
    model_path=results["unified_model_path"],
    project_ids=["work", "dining"],
    num_episodes=5,
)
```

### 🎯 Unified Model Components

#### UnifiedMultiProjectPolicy
A policy that can work across multiple projects using project embeddings and shared/project-specific heads.

**Key Features:**
- Project-aware action selection
- Shared feature processing
- Project-specific decision heads
- Training statistics tracking

#### UnifiedMultiProjectRewardFunction
A reward function that provides project-specific reward parameters.

**Key Features:**
- Project-specific reward scaling
- Progress and completion bonuses
- Configurable reward parameters

#### UnifiedMultiProjectTrainer
A trainer that orchestrates training across multiple projects.

**Key Features:**
- Multi-project training coordination
- Flexible project configuration
- Training progress tracking
- Model saving and loading

### 📊 Unified Evaluation

#### Single Project Evaluation
```python
from autoppia_iwa.src.rl.user_friendly import evaluate_single_project

results = evaluate_single_project(
    model_path="trained_models_unified/unified_multi_project_model.pt",
    project_id="work",
    num_episodes=5,
    headless=True,
)
```

#### Multi-Project Evaluation
```python
from autoppia_iwa.src.rl.user_friendly import evaluate_unified_model

results = evaluate_unified_model(
    model_path="trained_models_unified/unified_multi_project_model.pt",
    project_ids=["work", "dining", "cinema"],
    num_episodes=3,
    headless=True,
)
```

#### Evaluation Results
The evaluation returns detailed results including:
- **Success Rate**: Percentage of successful episodes
- **Average Reward**: Mean reward across episodes
- **Average Episode Length**: Mean number of steps per episode
- **Per-Project Performance**: Individual results for each project

### 🔍 Unified Model Architecture

The unified model uses a simple feedforward neural network architecture:

1. **Feature Extraction**: Extracts features from observations (URL, step, task prompt, etc.)
2. **Project Embedding**: Embeds project ID into a 32-dimensional vector
3. **Feature Processing**: Processes input features through a 2-layer MLP
4. **Project-Specific Heads**: Uses project-specific decision heads for action selection

### 💾 Unified Model Management

#### Saving Unified Models
```python
from autoppia_iwa.src.rl.user_friendly import UnifiedMultiProjectPolicy

policy = UnifiedMultiProjectPolicy(name="MyUnifiedPolicy")
# ... training ...
policy.save("my_unified_model.pt")
```

#### Loading Unified Models
```python
policy = UnifiedMultiProjectPolicy(name="MyUnifiedPolicy")
policy.load("my_unified_model.pt")
```

The saved model includes:
- Model state dictionary
- Optimizer state dictionary
- Training statistics
- Project mappings
- Model configuration

### 🎛️ Project Configuration

#### Project Configuration Format
```python
project_configs = {
    "project_id": {
        "num_use_cases": 0,  # 0 = all use cases, >0 = specific number
        "use_case_ids": None,  # Optional: specific use case IDs
    }
}
```

#### Example Configurations
```python
# Train on all use cases for work and dining, specific use cases for others
project_configs = {
    "work": {"num_use_cases": 0},  # All use cases
    "dining": {"num_use_cases": 0},  # All use cases
    "cinema": {"num_use_cases": 2},  # First 2 use cases
    "books": {"num_use_cases": 1},  # First use case only
}

# Train on specific use cases
project_configs = {
    "work": {"use_case_ids": [0, 2, 4]},  # Specific use case IDs
    "dining": {"use_case_ids": [1, 3]},  # Specific use case IDs
}
```

### 🚨 Unified Training Error Handling

The unified components include comprehensive error handling:

- **Feature Extraction**: Graceful handling of missing observation fields
- **Project ID Resolution**: Default fallback for unknown project IDs
- **Training Validation**: Validation of trajectory data before processing
- **Evaluation Robustness**: Error handling for failed evaluations

### 📈 Unified Training Statistics

The unified model tracks detailed training statistics:

- Total episodes and steps across all projects
- Per-project episode and step counts
- Training loss and returns
- Project-specific performance metrics

### 🔧 Unified Model Customization

#### Custom Feature Extraction
```python
class CustomUnifiedPolicy(UnifiedMultiProjectPolicy):
    def _extract_features(self, obs):
        features = super()._extract_features(obs)
        # Add custom features
        if "custom_field" in obs:
            features = torch.cat([features, torch.tensor([obs["custom_field"]])])
        return features
```

#### Custom Reward Parameters
```python
from autoppia_iwa.src.rl.user_friendly import UnifiedMultiProjectRewardFunction

reward_function = UnifiedMultiProjectRewardFunction()
reward_function.project_rewards["work"]["progress_bonus"] = 0.2
reward_function.project_rewards["work"]["completion_bonus"] = 3.0
```

### 🎉 Unified Training Benefits

1. **Cross-Project Learning**: Single model learns from multiple projects
2. **Knowledge Transfer**: Skills learned in one project can help in others
3. **Efficient Training**: Train once, use across multiple projects
4. **Unified Evaluation**: Compare performance across projects
5. **Scalable Architecture**: Easy to add new projects to existing model

### 📚 Integration with Existing Framework

The unified components are fully integrated with the existing user-friendly framework:

- Inherit from base `UserPolicy` and `UserRewardFunction` classes
- Use the same training and evaluation interfaces
- Compatible with existing task generation and benchmark systems
- Follow the same naming and interface conventions

## 📄 License

This framework is part of the Autoppia IWA project and follows the same license terms.