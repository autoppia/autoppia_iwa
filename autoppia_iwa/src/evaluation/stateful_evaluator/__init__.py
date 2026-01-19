"""
Evaluador Stateful - AsyncStatefulEvaluator y StatefulEvaluator

Evaluadores diseñados para Reinforcement Learning y entornos PPO.
Implementan la interfaz WebCUA para entrenamiento de agentes.

Uso:
    # Versión asíncrona
    from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
    
    evaluator = AsyncStatefulEvaluator(task=task, web_agent_id="agent_id")
    step_result = await evaluator.reset()
    step_result = await evaluator.step(action)
    
    # Versión síncrona (para RL/PPO)
    from autoppia_iwa.src.evaluation.stateful_evaluator import StatefulEvaluator
    
    with StatefulEvaluator(task=task) as evaluator:
        result = evaluator.reset()
        result = evaluator.step(action)

Características:
- Interfaz compatible con WebCUA
- Diseñado para RL y entrenamiento de agentes
- Mantiene estado del browser entre steps
- Versiones async y sync disponibles
"""

from autoppia_iwa.src.evaluation.stateful_evaluator.evaluator import (
    AsyncStatefulEvaluator,
    BrowserSnapshot,
    EvaluatorConfig,
    ScoreDetails,
    StatefulEvaluator,
    StepResult,
)

__all__ = [
    "AsyncStatefulEvaluator",
    "StatefulEvaluator",
    "ScoreDetails",
    "BrowserSnapshot",
    "StepResult",
    "EvaluatorConfig",
]
