# Ensure benchmark.utils.logging is imported once before any evaluator test runs.
# That module registers logger.level("EVALUATION", ...) at import time. If we don't
# import it first, evaluator code may call _ensure_evaluation_level() and register
# the level, then later "from ... import log_evaluation_event" loads the real module
# which tries to register "EVALUATION" again and loguru raises ValueError.
# Pre-importing here (when this conftest is loaded for tests/evaluation/) registers
# the level once; then both _ensure_evaluation_level() and the real logging helpers
# work without conflict. Same approach as test_logging.py: use the real module.


def pytest_configure(config):
    import autoppia_iwa.entrypoints.benchmark.utils.logging  # noqa: F401
    # Module is now in sys.modules; EVALUATION level is registered once.
