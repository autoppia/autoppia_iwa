"""Legacy concurrent evaluator re-export.

The active evaluation runtime is stateful. Concurrent evaluation is kept under
`autoppia_iwa.src.evaluation.legacy` for backward compatibility only.
"""

from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import *  # noqa: F403

__all__ = [name for name in globals() if not name.startswith("__")]
