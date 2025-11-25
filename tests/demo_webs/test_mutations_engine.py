from __future__ import annotations

from modules.dynamic_proxy.core.config import DynamicPhaseConfig
from modules.dynamic_proxy.core.engine import MutationEngine


def _build_engine(**overrides) -> MutationEngine:
    config = DynamicPhaseConfig(
        enable_d1_structure=True,
        enable_d3_attributes=True,
        enable_d4_overlays=True,
        use_module_palettes=False,
        **overrides,
    )
    return MutationEngine(project_id="autotest", phase_config=config)


def test_engine_applies_all_phases():
    engine = _build_engine()
    html = "<html><body><div id='root'><button>Pay</button></div></body></html>"
    result = engine.mutate_html(html, "http://example.com/home", seed=3)
    assert result.audit_record is not None
    mutated = result.html
    assert "iwa-wrapper" in mutated  # D1
    assert "mut-" in mutated or "data-iwa-" in mutated  # D3 attribute modifications
    assert "data-iwa-overlay-bootstrap" in mutated  # D4 script injected


def test_engine_reuses_plan_from_cache():
    engine = _build_engine()
    html = "<html><body><div class='card'>Alpha<button>Pay</button></div></body></html>"
    first = engine.mutate_html(html, "http://example.com/products", seed=9)
    second = engine.mutate_html(html, "http://example.com/products", seed=9)
    assert first.audit_record is not None
    assert second.audit_record is not None
    assert second.audit_record.plan_source in {"cache", "similar"}
