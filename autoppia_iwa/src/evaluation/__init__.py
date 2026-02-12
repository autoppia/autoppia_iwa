"""
Sistema de Evaluación de Autoppia IWA

Este módulo proporciona dos tipos de evaluadores para distintos casos de uso:

1. ConcurrentEvaluator: Para evaluar soluciones completas con todas las acciones generadas
2. StatefulEvaluator: Para evaluación iterativa paso a paso (usado en subnet y modo stateful)

Además, proporciona clases comunes y utilidades compartidas.
"""

# Evaluadores
# Clases e interfaces
from autoppia_iwa.src.evaluation.classes import (
    EvaluationResult,
    EvaluationStats,
    EvaluatorConfig,
    Feedback,
    TestResult,
)
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.interfaces import IEvaluator

# Utilidades compartidas
from autoppia_iwa.src.evaluation.shared import (
    FeedbackGenerator,
    TestRunner,
    generate_feedback,
    run_global_tests,
    run_partial_tests,
)
from autoppia_iwa.src.evaluation.stateful_evaluator import (
    AsyncStatefulEvaluator,
    StatefulEvaluator,
)

__all__ = [
    "AsyncStatefulEvaluator",
    # Evaluadores
    "ConcurrentEvaluator",
    # Clases
    "EvaluationResult",
    "EvaluationStats",
    "EvaluatorConfig",
    "Feedback",
    # Utilidades
    "FeedbackGenerator",
    "IEvaluator",
    "StatefulEvaluator",
    "TestResult",
    "TestRunner",
    "generate_feedback",
    "run_global_tests",
    "run_partial_tests",
]
