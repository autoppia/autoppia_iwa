"""
Autoppia IWA Evaluation System

Active runtime:
1. TaskExecutionSession: step-by-step task execution runtime

Legacy concurrent evaluation remains under `autoppia_iwa.src.evaluation.legacy`.
"""

from autoppia_iwa.src.evaluation.classes import (
    EvaluationResult,
    EvaluationStats,
    Feedback,
    TestResult,
)
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
    TaskExecutionSessionConfig,
)

__all__ = [
    "AsyncStatefulEvaluator",
    "EvaluationResult",
    "EvaluationStats",
    "Feedback",
    "FeedbackGenerator",
    "IEvaluator",
    "StatefulEvaluator",
    "TaskExecutionSession",
    "TaskExecutionSessionConfig",
    "TestResult",
    "TestRunner",
    "generate_feedback",
    "run_global_tests",
    "run_partial_tests",
]
