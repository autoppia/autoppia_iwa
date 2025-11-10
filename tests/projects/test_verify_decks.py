from __future__ import annotations

from pathlib import Path

from modules.web_verification.verify_project import SECTION_DECK, verify_project

DECKS_DIR = Path(__file__).resolve().parents[2] / "modules" / "web_verification" / "deck" / "examples"


def _deck(slug: str) -> Path:
    return DECKS_DIR / f"{slug}.deck.json"


def test_matching_deck_passes_for_project():
    report, project = verify_project("autodining", deck_path=_deck("autodining"))
    assert project is not None, "Expected WebProject to load"
    deck_section = report.sections.get(SECTION_DECK)
    assert deck_section is not None
    assert deck_section.ok, "Deck checks should pass for matching project"


def test_deck_fails_when_used_with_wrong_project():
    report, _ = verify_project("autolodge_8", deck_path=_deck("autodining"))
    deck_section = report.sections.get(SECTION_DECK)
    assert deck_section is not None, report.render()
    assert not deck_section.ok

    mismatch_checks = [
        check for check in deck_section.checks if check.description == "Deck project_id matches WebProject.id"
    ]
    assert mismatch_checks, "Expected project id mismatch to be recorded"
    assert mismatch_checks[0].passed is False
    assert "autodining" in (mismatch_checks[0].details or "")
