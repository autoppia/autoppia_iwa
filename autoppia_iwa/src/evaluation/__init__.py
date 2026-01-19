"""
Sistema de Evaluación de Autoppia IWA

Este módulo proporciona tres tipos de evaluadores diferentes para distintos casos de uso:

1. ConcurrentEvaluator: Para evaluar soluciones completas con todas las acciones generadas
2. IterativeEvaluator: Para evaluar agentes de forma iterativa, acción por acción
3. StatefulEvaluator: Para Reinforcement Learning y entrenamiento de agentes (interfaz WebCUA)

Además, proporciona clases comunes y utilidades compartidas.
"""

# Evaluadores
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.iterative_evaluator import IterativeEvaluator
from autoppia_iwa.src.evaluation.stateful_evaluator import (
    AsyncStatefulEvaluator,
    StatefulEvaluator,
)

# Clases e interfaces
from autoppia_iwa.src.evaluation.classes import (
    EvaluationResult,
    EvaluationStats,
    EvaluatorConfig,
    Feedback,
    TestResult,
)
from autoppia_iwa.src.evaluation.interfaces import IEvaluator

# Utilidades compartidas
from autoppia_iwa.src.evaluation.shared import (
    FeedbackGenerator,
    TestRunner,
    generate_feedback,
    run_global_tests,
    run_partial_tests,
)

__all__ = [
    # Evaluadores
    "ConcurrentEvaluator",
    "IterativeEvaluator",
    "AsyncStatefulEvaluator",
    "StatefulEvaluator",
    # Clases
    "EvaluationResult",
    "EvaluationStats",
    "EvaluatorConfig",
    "Feedback",
    "TestResult",
    "IEvaluator",
    # Utilidades
    "FeedbackGenerator",
    "TestRunner",
    "generate_feedback",
    "run_global_tests",
    "run_partial_tests",
]
