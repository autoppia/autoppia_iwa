import pytest

from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.web_verification.dynamic_verifier import DynamicVerifier


class _DummyGenerator:
    def __init__(self, *args, **kwargs):
        pass


def _build_project():
    return WebProject(
        id="autocinema",
        name="Autocinema",
        backend_url="http://localhost:8001",
        frontend_url="http://localhost:8000/movies",
        urls=["http://localhost:8000/movies"],
        use_cases=[],
    )


def test_normalize_action_flattens_attributes_and_maps_aliases(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.dynamic_verifier.SimpleTaskGenerator",
        _DummyGenerator,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.dynamic_verifier.DIContainer.llm_service",
        lambda: object(),
    )
    verifier = DynamicVerifier(web_project=_build_project())

    normalized = verifier._normalize_action(
        {
            "type": "input",
            "attributes": {
                "selector": {"value": "search-input", "attribute": "id"},
                "value": "Inception",
            },
        }
    )

    assert normalized["type"] == "TypeAction"
    assert normalized["text"] == "Inception"
    assert normalized["selector"]["type"] == "attributeValueSelector"


@pytest.mark.asyncio
async def test_verify_dataset_diversity_with_seeds_uses_loaded_datasets(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.dynamic_verifier.SimpleTaskGenerator",
        _DummyGenerator,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.dynamic_verifier.DIContainer.llm_service",
        lambda: object(),
    )
    verifier = DynamicVerifier(web_project=_build_project())

    async def fake_load(seed_values):
        return (
            {
                1: {"movies": [{"id": 1, "title": "Inception"}]},
                2: {"movies": [{"id": 2, "title": "Interstellar"}]},
            },
            {
                1: {"success": True, "entity_count": 1, "hash": "hash-one", "entities": ["movies"]},
                2: {"success": True, "entity_count": 1, "hash": "hash-two", "entities": ["movies"]},
            },
        )

    monkeypatch.setattr(verifier, "_load_datasets_for_seeds", fake_load)

    result = await verifier.verify_dataset_diversity_with_seeds([1, 2])

    assert result["all_different"] is True
    assert result["passed"] is True
    assert result["loaded_count"] == 2
