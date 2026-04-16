from autoppia_iwa.src.evaluation import concurrent_evaluator as public_module
from autoppia_iwa.src.evaluation.legacy import concurrent_evaluator as legacy_module


def test_public_concurrent_evaluator_reexports_legacy_symbols() -> None:
    assert public_module.ConcurrentEvaluator is legacy_module.ConcurrentEvaluator
    assert public_module._ensure_evaluation_level is legacy_module._ensure_evaluation_level
    assert public_module._is_navigation_url_allowed is legacy_module._is_navigation_url_allowed
    assert public_module._url_hostname is legacy_module._url_hostname


def test_public_concurrent_evaluator_dunder_all_exposes_public_names() -> None:
    exported = set(public_module.__all__)

    assert "ConcurrentEvaluator" in exported
    assert "_ensure_evaluation_level" in exported
    assert "__all__" not in exported
