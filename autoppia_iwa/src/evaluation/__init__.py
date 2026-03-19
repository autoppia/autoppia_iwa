"""
Autoppia IWA Evaluation System

Two runtime/evaluation modes:
1. ConcurrentEvaluator: Evaluates complete solutions with all actions pre-generated
2. TaskExecutionSession: Step-by-step task execution runtime
"""

from autoppia_iwa.src.evaluation.classes import (
    EvaluationResult,
    EvaluationStats,
    EvaluatorConfig,
    Feedback,
    TestResult,
)
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.evaluation.shared import (
    FeedbackGenerator,
    TestRunner,
    generate_feedback,
    run_global_tests,
    run_partial_tests,
)
from autoppia_iwa.src.evaluation.stateful_evaluator import (
    TaskExecutionSession,
    AsyncStatefulEvaluator,
    StatefulEvaluator,
)

__all__ = [
    "AsyncStatefulEvaluator",
    "ConcurrentEvaluator",
    "EvaluationResult",
    "EvaluationStats",
    "EvaluatorConfig",
    "Feedback",
    "FeedbackGenerator",
    "IEvaluator",
    "StatefulEvaluator",
    "TaskExecutionSession",
    "TestResult",
    "TestRunner",
    "generate_feedback",
    "run_global_tests",
    "run_partial_tests",
]
