"""Legacy concurrent evaluator re-export.

The active evaluation runtime is stateful. Concurrent evaluation is kept under
`autoppia_iwa.src.evaluation.legacy` for backward compatibility only.
"""

from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import *  # noqa: F403
from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import (
    _ensure_evaluation_level,
    _is_navigation_url_allowed,
    _is_testing_mode,
    _log_action_execution,
    _log_evaluation_event,
    _log_evaluation_fallback,
    _log_gif_creation,
    _url_hostname,
)

__all__ = [name for name in globals() if not name.startswith("__")]
