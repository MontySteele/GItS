"""The three Ancient cards, sim-side (EB-30m, executing R127's carve-out).

`tier0/content/cards/ancients.yaml` is a SIDE-SHEET: no codegen reads it, no
`*-cards.yaml` lint sweeps it, and the C# classes it mirrors are hand-written.
That is the right arrangement for cards whose C# twin is hand-written, and it
removes every drift alarm the ratified sheets provide -- so the alarm is
rebuilt here, mechanically, against
`tools/lint_handwritten_parity.ANCIENT_WITNESS`, which reads the C# directly.
A number can then only be changed in both places or in neither.

The other half of the file pins the two income powers, and in particular the
ORDER of their turn-start tick against the Salon upkeep. That order is EB-2's
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
    assert set(hwp.ANCIENT_WITNESS) == set(WITNESSED.values())
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

    assert [base.cost] == pin["cost"]
    assert _printed_vars(base) == pin["vars"]
    assert _hits(base) == pin["hits"]
    assert [u - b for b, u in zip(_printed_vars(base), _printed_vars(up))] \
        == pin["upgrade_vars"]
    delta_cost = up.cost - base.cost
    assert ([delta_cost] if delta_cost else []) == pin["upgrade_cost"]


def test_the_ancients_stay_out_of_the_ratified_sheets():
    """The whole reason for the side-sheet: codegen must never see them.

    `tools/gen_klee_cards.py` reads the three `docs/<char>-cards.yaml` files
    and would try to emit a C# class for any row it finds; these three
    classes are hand-written. The upgrade sheet is registered in the sim's
    applier only, on the ref-ironclad precedent.
    """
    for sheet in loader.DOCS_CARD_SHEETS:
        text = (loader.DOCS_DIR / sheet).read_text(encoding="utf-8")
        for cid in WITNESSED:
            assert cid not in text, f"{cid} reached {sheet}"
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


def test_charge_per_turn_pays_every_turn_and_never_decays():
    st = _state("kokomi")
    _play(st, "princess_of_watatsumi")
    assert st.player.charge == 0            # a Power that pays on the CLOCK
    for turn in range(1, 5):
        effects.player_turn_start_triggers(st)
        assert st.player.charge == 3 * turn
        # Permanent: absent from powers.DECAYING and powers.EXPIRING, so the
        # stack count is the same on turn 4 as on turn 1.
        assert st.player.powers["charge_per_turn"] == 3


def test_encore_per_turn_pays_every_turn_and_never_decays():
    st = _state("furina")
    _play(st, "all_the_worlds_a_stage")
    start = st.player.encore
    for turn in range(1, 5):
        effects.player_turn_start_triggers(st)
        assert st.player.encore == start + 5 * turn
        assert st.player.powers["encore_per_turn"] == 5


def test_the_upgraded_forms_pay_the_upgraded_amounts():
    """The Dusty Tome grants the UPGRADED card, so these are the numbers a
    run actually meets -- the base rows exist for smith-less paths only."""
    st = _state("kokomi")
    _play(st, "princess_of_watatsumi+")
    effects.player_turn_start_triggers(st)
    assert st.player.charge == 4

    st = _state("furina")
    _play(st, "all_the_worlds_a_stage+")
    before = st.player.encore
    effects.player_turn_start_triggers(st)
    assert st.player.encore == before + 7


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


def test_the_stage_funds_the_same_turn_s_salon_ticks():
    """The behavioural half: income before upkeep is worth a real tick.

    With an empty buffer and one member, the printed "at the start of your
    turn" has to arrive first or the member goes dry and resolves at the
    reduced rate. The `paid` flag on the member's own emit is the reading,
    and the net Encore is the arithmetic that has to agree with it.
    """
    st = _state("furina")
    _play(st, "all_the_worlds_a_stage")
    st.player.salon = ["crabaletta"]
    st.player.encore = 0

    effects.player_turn_start_triggers(st)

    ticks = [e for e in st.log if e["event"] == "salon_tick"]
    assert [e["paid"] for e in ticks] == [True]
    assert st.player.encore == 5 - C.SALON_TICK_ENCORE_COST
    # Log order is the same claim read a second way.
    kinds = [e["event"] for e in st.log]
    assert kinds.index("gain_encore") < kinds.index("salon_upkeep")


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


def test_the_furina_spotlight_divergence_is_known_and_pinned():
    """The evidence behind the sheet's characterless decision, half (b).

    AllTheWorldsAStage is an `ICharacterCard { CharacterId: "furina" }` in
    C#, so a Center Stage designation Spotlights it there. Here it carries no
    `character:`, deliberately -- tagging the row would admit an
    acquisition-only card into every per-character pool census in the repo.

    THIS TEST EXISTS TO KEEP THAT COST VISIBLE, not to bless it. It fails the
    day someone adds the tag, which is exactly when the sheet header's
    argument and the composition pins need re-reading together.
    """
    st = _state("furina")
    st.player.spotlight = st.player.character_id
    ancient = loader.get_card("all_the_worlds_a_stage")
    assert ancient.character is None
    assert not effects.is_spotlighted(st, ancient)
    # Her ordinary cards are unaffected -- the divergence is scoped to the
    # three untagged rows and nothing else.
    assert effects.is_spotlighted(st, loader.get_card("an_invitation"))


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
