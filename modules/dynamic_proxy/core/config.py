from __future__ import annotations

from pydantic import BaseModel


class DynamicPhaseConfig(BaseModel):
    """
    Configuration shared by the dynamic proxy and mutation engine.

    Mirrors the knobs available in the Playwright dynamic executor so behavior stays
    consistent regardless of where mutations are applied.
    """

    enable_d1_structure: bool = True
    enable_d3_attributes: bool = True
    enable_d4_overlays: bool = True

    d4_min_action: int = 2
    d4_max_action: int = 5

    instruction_cache_size: int = 32
    html_similarity_threshold: float = 0.95

    palette_dir: str | None = None
    palette_max_per_phase: int = 3
    use_module_palettes: bool = True
    apply_dom_mutations: bool = True
    force_generate_plan: bool = False
    seed_modulus: int = 32

    def any_enabled(self) -> bool:
        return self.enable_d1_structure or self.enable_d3_attributes or self.enable_d4_overlays


__all__ = ["DynamicPhaseConfig"]
