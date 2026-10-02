"""The three Ancient cards, sim-side (EB-30m, executing R127's carve-out).

`tier0/content/cards/ancients.yaml` is a SIDE-SHEET: no codegen reads it, no
`*-cards.yaml` lint sweeps it, and the C# classes it mirrors are hand-written.
That is the right arrangement for cards whose C# twin is hand-written, and it
removes every drift alarm the ratified sheets provide -- so the alarm is
rebuilt here, mechanically, against
`tools/lint_handwritten_parity.ANCIENT_WITNESS`, which reads the C# directly.
A number can then only be changed in both places or in neither.

The other half of the file pins the ORDER of the two income powers'
turn-start tick against the Salon upkeep (their shipped-world payouts left
with the shipped kits, legacy cleanup stage 6). That order is EB-2's
stated parity target, so it is the one thing here that a well-meaning tidy-up
could silently undo.
"""

from __future__ import annotations

import inspect
import random
import sys
from pathlib import Path

import pytest
import yaml

from tier0 import constants as C, roster
from tier0.content import loader, upgrades
from tier0.engine import effects, combat
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

REPO = Path(loader.__file__).resolve().parents[2]

sys.path.insert(0, str(REPO / "tools"))
import lint_handwritten_parity as hwp    # noqa: E402

# sim card id -> the C# class ANCIENT_WITNESS pins it under. Written out
# rather than derived from the id, because the two namespaces are allowed to
# disagree (the C# name is the class, the sim id is the sheet key) and a
# derivation would quietly stop matching the day one of them is renamed.
WITNESSED = {
    "jumpy_dumpty_mk_omega": "JumpyDumptyMkOmega",
    "princess_of_watatsumi": "PrincessOfWatatsumi",
    "all_the_worlds_a_stage": "AllTheWorldsAStage",
}


def _printed_vars(card) -> list[int]:
    """The card's DynamicVar values, in declaration order.

    Mirrors what `extract_cs` reads off the C# `CanonicalVars` list: the
    damage number, then the bomb's ExtraDamage, or the lone PowerAmount.
    Declaration order is load-bearing -- the witness pins a LIST.
    """
    out = []
    for fx in card.effects:
        if fx["op"] == "damage":
            out.append(fx["amount"])
        elif fx["op"] == "place_bomb":
            out.append(fx["bomb_damage"])
        elif fx["op"] == "apply_power":
            out.append(fx["amount"])
    return out


def _hits(card) -> list[int]:
    """`WithHitCount(n)` on the C# side: a damage op's repeat count."""
    return [fx["times"] for fx in card.effects
            if fx["op"] == "damage" and fx.get("times")]


# --- the sheet rows, double-pinned against the C# witness ------------------

def test_the_witness_and_the_side_sheet_name_the_same_three_cards():
    """Both directions, the discipline ANCIENT_WITNESS's own header states.

    A witness entry with no sheet row means the sim never modelled a card the
    mod ships; a sheet row with no witness means a number nothing checks.
    """
    # POOL COMPLETION (2026-10-01): each kit's second Ancient is arm-only and
    # game-side only (`hwp.ARM_ONLY_ANCIENTS`): witnessed, never mirrored.
    assert (set(hwp.ANCIENT_WITNESS) - hwp.ARM_ONLY_ANCIENTS
            == set(WITNESSED.values()))
    assert hwp.ARM_ONLY_ANCIENTS <= set(hwp.ANCIENT_WITNESS)
    # Scoped to the SIDE-SHEET, not to `rarity == "ancient"` across the
    # index: `ancient` is a real base-game rarity and the extracted reference
    # pools carry four of them (Break, Corruption, Suppress, Wraith Form) on
    # a machine that holds `game_ref/`. Those are not ours and have no
    # witness; the file is the boundary this pin is about.
    rows = yaml.safe_load(
        (loader.CONTENT_DIR / "cards" / "ancients.yaml")
        .read_text(encoding="utf-8"))
    assert {r["id"] for r in rows} == set(WITNESSED)
    assert all(r["rarity"] == "ancient" for r in rows)


@pytest.mark.parametrize("cid", sorted(WITNESSED))
def test_every_number_matches_the_c_sharp_witness(cid):
    """Cost, printed vars, hit count and both upgrade deltas.

    The upgrade halves are derived by ACTUALLY UPGRADING the card, so this
    exercises `upgrades.apply_upgrade`'s key bindings as well: a delta that
    bound to the wrong effect would produce the right sheet and the wrong
    card, and only this comparison would notice.
    """
    pin = hwp.ANCIENT_WITNESS[WITNESSED[cid]]
    base = loader.get_card(cid)
    up = loader.get_card(cid + upgrades.SUFFIX)

    # A prototype arm's own var (R276: the Ancient's Stage-arm Raise) is
    # declared inside `#if PROTOTYPE_CARDS` and has no sim twin -- the sheet
    # models the shipped card -- so the pin names it and it is set aside here.
    def shipped(key):
        out = list(pin[key])
        for n in pin.get("arm_only_" + key, []):
            out.remove(n)
        return out

    assert [base.cost] == pin["cost"]
    assert _printed_vars(base) == shipped("vars")
    assert _hits(base) == pin["hits"]
    assert [u - b for b, u in zip(_printed_vars(base), _printed_vars(up))] \
        == shipped("upgrade_vars")
    delta_cost = up.cost - base.cost
    assert ([delta_cost] if delta_cost else []) == pin["upgrade_cost"]


def test_the_ancients_stay_out_of_the_ratified_sheets():
    """The whole reason for the side-sheet: codegen must never see them.

    The codegen reads the prototype surface (the per-character sheets left
    at legacy cleanup stage 6) and would try to emit a C# class for any row it
    finds; these three classes are hand-written. The upgrade sheet is
    registered in the sim's applier only, on the ref-ironclad precedent.
    """
    surface_ids = {c.id for c in loader.prototype_cards()}
    for cid in WITNESSED:
        assert cid not in surface_ids, f"{cid} reached the prototype surface"
    from tools import gen_klee_cards as gen
    assert not any(p.name == "ancient-upgrades.yaml"
                   for p in gen.UPGRADE_SHEETS)
    assert any(p.name == "ancient-upgrades.yaml"
               for p in upgrades.UPGRADE_SHEETS)
    # Codegen has no CardRarity mapping for `ancient`, and that KeyError is
    # the second lock rather than an oversight.
    assert "ancient" not in gen.RARITY_CS


# --- the income powers -----------------------------------------------------

def _state(character, seed=0, enemies=None):
    return CombatState(player=loader.build_player(character),
                       enemies=enemies or [make_enemy(hp=400)],
                       rng=random.Random(seed))


def _play(state, cid):
    card = loader.get_card(cid)
    state.player.hand.append(card)
    state.player.energy = 9
    combat.play_card(state, card)
    return card


# --- THE EB-2 ORDER PIN ----------------------------------------------------

def test_ancient_income_is_sourced_above_the_salon_upkeep():
    """EB-2's parity target, pinned at the SITE (test_a7_port idiom).

    The C# race is between SalonPowers' upkeep and FurinaResources' Encore
    income inside one `AfterPlayerTurnStart` broadcast, with no guaranteed
    order. The sim is what says which way it should fall, so the ordering
    has to be asserted where a reader would otherwise "tidy" it: both ticks
    sit above `salon_tick`, and above the whole per-turn income group that
    follows it.
    """
    src = inspect.getsource(effects.player_turn_start_triggers)
    upkeep = src.index("salon_tick(state)")
    # The READS, not the words: the comment block at the insertion point
    # names every power in this test, so matching bare names would pass on
    # the prose alone.
    assert src.index('p.powers.get("charge_per_turn"') < upkeep
    assert src.index('p.powers.get("encore_per_turn"') < upkeep
    # And genuinely ABOVE the group, not merely above one member of it.
    assert upkeep < src.index('p.powers.get("spark_per_turn"')
    assert upkeep < src.index('p.powers.get("celestial_gift"')


# --- Jumpy Dumpty Mk.Omega in combat ---------------------------------------

def test_jumpy_lands_three_random_hits_and_bombs_every_enemy():
    enemies = [make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b"),
               make_enemy(hp=200, name="c")]
    st = _state("klee", seed=3, enemies=enemies)
    _play(st, "jumpy_dumpty_mk_omega")

    hits = [e for e in st.log if e["event"] == "damage"
            and e["source"] == "attack"]
    assert len(hits) == 3
    assert all(e["base"] == 12 for e in hits)
    # Targets are RE-PICKED per hit, so the three land on whoever the stream
    # names rather than all on one enemy by construction.
    assert {e["target"] for e in hits} <= {"a", "b", "c"}
    assert all(len(e.bombs) == 1 and e.bombs[0].damage == 12 for e in enemies)


def test_jumpy_upgraded_is_sixteen_and_sixteen():
    enemies = [make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")]
    st = _state("klee", seed=3, enemies=enemies)
    _play(st, "jumpy_dumpty_mk_omega+")
    hits = [e for e in st.log if e["event"] == "damage"
            and e["source"] == "attack"]
    assert [e["base"] for e in hits] == [16, 16, 16]
    assert all(e.bombs[0].damage == 16 for e in enemies)


def test_jumpy_applies_pyro_the_way_klee_s_catalyst_grade_does():
    """The evidence behind the sheet's characterless decision, half (a).

    `_element_for` keys on the PLAYER's cadence and element, never on
    `card.character`, so an untagged attack in Klee's deck applies Pyro
    exactly as JumpyDumptyMkOmega's `Element => Element.Pyro` demands.
    """
    enemies = [make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")]
    st = _state("klee", seed=3, enemies=enemies)
    _play(st, "jumpy_dumpty_mk_omega")
    assert {e["target"] for e in st.log
            if e["event"] == "aura_applied" and e["element"] == "pyro"}


# --- vocabulary guards -----------------------------------------------------

def test_every_rarity_in_the_index_is_declared_in_one_of_the_two_tables():
    """A rarity in NEITHER table is a typo, and a typo'd rarity is invisible.

    `ancient`'s absence from RARITY_ODDS is what keeps it out of draft,
    reward and shop generation -- but so is a misspelling, and a misspelling
    would take a real card out of every pool with every gate green. The pair
    of tables makes the intentional half declared and the accidental half
    loud.
    """
    known = set(C.RARITY_ODDS) | C.ACQUISITION_ONLY_RARITIES
    seen = {c.rarity for c in loader._card_index().values()}
    assert seen <= known, sorted(seen - known)
    assert not (set(C.RARITY_ODDS) & C.ACQUISITION_ONLY_RARITIES)


def test_every_roster_character_has_a_resolvable_ancient():
    """Both directions, mirroring RosterAncientCards.cs's own invariant: a
    character with no Ancient is what softlocked the act-2 Darv event."""
    assert set(roster.ANCIENTS) == set(roster.IDS)
    for character, cid in roster.ANCIENTS.items():
        assert loader.get_card(cid).rarity == "ancient"
        assert loader.get_card(cid + upgrades.SUFFIX).id.startswith(cid)
        # And nobody is holding someone else's card by accident.
        assert sum(1 for v in roster.ANCIENTS.values() if v == cid) == 1
