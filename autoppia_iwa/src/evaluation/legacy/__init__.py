"""Legacy evaluation components kept for backward compatibility only."""

from autoppia_iwa.src.evaluation.legacy.concurrent_config import EvaluatorConfig
from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import ConcurrentEvaluator

__all__ = ["ConcurrentEvaluator", "EvaluatorConfig"]
