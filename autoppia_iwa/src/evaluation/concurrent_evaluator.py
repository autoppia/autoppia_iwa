"""Legacy concurrent evaluator re-export.

The active evaluation runtime is stateful. Concurrent evaluation is kept under
`autoppia_iwa.src.evaluation.legacy` for backward compatibility only.
"""

from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import *  # noqa: F403
from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import (  # noqa: F401
    _ensure_evaluation_level,
    _is_navigation_url_allowed,
    _url_hostname,
)

__all__ = [name for name in globals() if not name.startswith("__")]
