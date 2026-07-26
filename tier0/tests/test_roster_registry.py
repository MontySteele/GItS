"""The roster registry, and the gate that holds it shut. (F1, audit sec.5.)

Dual-wired with `validate.ps1` S11 for the reason `test_sheet_lints.py` gives
about its own family: the deploy gate runs on one Windows machine, and the
person who adds character #4 may never touch it.

The point of the registry is not tidiness. Adding a character touches ~26
sites, 4 gated and **22 silent**, and two of those silences have already cost
real numbers: R66 (an archetype registry naming three tags that existed on zero
cards -- every adaptive Kokomi number ever taken went through it) and Kokomi's
card art never being staged because `deploy.ps1`'s array did not list her.
Neither failed anything.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

from tier0 import roster                                     # noqa: E402
from tier0.content import loader                             # noqa: E402
from tier05 import draft, runner                             # noqa: E402

import lint_roster_registry as lint                          # noqa: E402


# --- the gate ------------------------------------------------------------

def test_the_shipped_roster_is_fully_wired():
    findings = lint.check()
    assert not findings, "\n".join(findings)


def test_the_gate_is_not_vacuous():
    """A lint that sweeps nothing reports the same clean line as one that
    sweeps everything -- the audit's sec.3.1/sec.3.7 dead-gate class, and the
    reason S8 passed for its entire life."""
    assert len(roster.ROSTER) >= 3
    assert len(lint.CLOSED_LISTS) >= 10


def test_an_unregistered_character_is_a_structural_failure(monkeypatch):
    """The whole deliverable, exercised: slot 4 with nothing wired.

    This is what "22 silent gaps become one loud failure" means in practice,
    and it is the pre-Zhongli gate the sprint doc names.
    """
    slot4 = roster.Character(
        id="zhongli", display="Zhongli", cs_class="Zhongli", nation="liyue",
        default_plan="geo", plans={"geo": "geo"}, archetypes=("geo",))
    monkeypatch.setattr(roster, "ROSTER", roster.ROSTER + (slot4,))
    monkeypatch.setitem(roster.BY_ID, "zhongli", slot4)

    findings = lint.check()
    assert len(findings) >= 15, findings
    joined = "\n".join(findings)
    # Named individually rather than by count: the count is the headline, but
    # the VALUE is that each finding tells you a specific file to go edit.
    for expected in ("Zhongli.cs", "ZhongliCardPool.cs", "zhongli.yaml",
                     "zhongli-cards.yaml", "KleeSelfCheck", "deploy.ps1",
                     "build_pck.ps1", "art_coverage", "lint_pool_membership",
                     "RosterAncientCards", "gen_klee_cards"):
        assert expected in joined, f"{expected} not covered by the sweep"


# --- R66, in both directions --------------------------------------------

@pytest.mark.parametrize("character", roster.ROSTER, ids=lambda c: c.id)
def test_declared_archetypes_are_exactly_the_tags_her_cards_carry(character):
    """R66's defect, made impossible.

    It stays DECLARED rather than derived from the cards, because deriving
    would let a typo'd tag on one card silently invent an archetype. It is
    then cross-checked, which closes the direction declaring alone leaves
    open. Both halves are needed; either alone is a registry that can lie.
    """
    tags = set()
    for card in loader._card_index().values():
        if card.character == character.id:
            tags.update(card.archetypes)
    tags.discard("generic")     # everyone has it; nobody IS it
    assert set(character.archetypes) == tags, (
        f"{character.id}: registry {sorted(character.archetypes)} vs card "
        f"tags {sorted(tags)}")


def test_the_kokomi_regression_would_be_caught_today(monkeypatch):
    """The literal R66 value, replayed against the gate that now exists."""
    broken = roster.Character(
        id="kokomi", display="Sangonomiya Kokomi", cs_class="Kokomi",
        nation="inazuma", default_plan="priest",
        plans={"generic": "generic", "commander": "commander",
               "priest": "priest", "assist": "assist"},
        archetypes=("garment", "ward", "conscript"))
    patched = tuple(broken if c.id == "kokomi" else c for c in roster.ROSTER)
    monkeypatch.setattr(roster, "ROSTER", patched)

    findings = [f for f in lint.check() if "archetype registry" in f]
    assert findings, "R66's exact value passed the gate"
    joined = "\n".join(findings)
    for phantom in ("garment", "ward", "conscript"):
        assert phantom in joined
    for orphan in ("priest", "commander", "assist"):
        assert orphan in joined, (
            "the orphan direction must fire too -- her real tags are declared "
            "by nobody in this scenario")


# --- consumers actually consume it ---------------------------------------

def test_the_drafter_reads_the_registry_rather_than_a_copy():
    assert draft.ROSTER_ARCHETYPES == {
        c.id: c.archetypes for c in roster.ROSTER}


def test_the_plan_registry_reads_the_registry_rather_than_a_copy():
    for character in roster.ROSTER:
        assert runner.CHARACTER_PLANS[character.id] == character.plans
        assert runner.DEFAULT_PLAN[character.id] == character.default_plan
        # And the default must be one of the plans, which nothing checked.
        assert character.default_plan in character.plans


def test_reference_anchors_are_not_roster_members():
    """They have no art, no pool, no C# class and no plans beyond generic.

    Folding them in would make every sweep in the lint either wrong or full
    of exceptions, so the distinction is on record rather than implied by
    their absence -- and `runner` keeps their literals for exactly this.
    """
    for ref in roster.REFERENCE_IDS:
        assert ref not in roster.BY_ID
        assert ref not in draft.ROSTER_ARCHETYPES
    assert "ref_ironclad" in runner.CHARACTER_PLANS


def test_get_fails_loudly_and_names_the_roster():
    """`.get()`-shaped lookup would let an unregistered id travel a layer."""
    with pytest.raises(KeyError, match="not a registered character"):
        roster.get("zhongli")
    assert roster.get("klee").cs_class == "Klee"


def test_every_declared_path_resolves_for_every_character():
    """The registry's paths are properties, so a typo is invisible until read."""
    for character in roster.ROSTER:
        for prop in ("character_yaml", "card_sheet", "upgrade_sheet",
                     "character_cs", "card_pool_cs", "relic_pool_cs"):
            path = getattr(character, prop)
            assert path.exists(), f"{character.id}.{prop} -> {path}"
        # card_art_dir is gitignored Tier F and legitimately absent on a bare
        # clone, so it is checked for SHAPE rather than existence.
        assert character.card_art_dir.name == character.id
