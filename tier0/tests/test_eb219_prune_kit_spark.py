"""EB-219 -- Prune's Sparks moved from her face to Klee's kit, at parity.

LAW:145, countersigned R224 (2026-08-30):

    Companion cards may not themselves grant signature resources. A
    character-owned engine may respond to a Companion play and generate its
    resource where that character's kit explicitly declares the trigger and
    bounds the amount generated per Companion play.

`prune_witch_hunt` used to print `gain_spark 1` inside a
`reaction_triggered_by_this` conditional AND `gain_spark 1` unconditionally at
top level, upgrading the second one -- so she paid 1 / 2 / 2 / 3 Sparks across
(base, no reaction) / (base, reaction) / (upgraded, no reaction) / (upgraded,
reaction). Both ops are gone; the grant is Klee's kit declaration
("Little Hexenzirkul", `constants.KLEE_COMPANION_SPARK_*`,
`effects.klee_personal_companion_spark`).

THE POINT OF THIS FILE IS THE PARITY LOCK. Every one of those four numbers is
asserted BEFORE/AFTER-style: the "before" side is not a fixture that could drift
with the code, it is the four literals the shipped face paid, written out here
and in the constants block, so a future edit to either the kit or the sheet has
to walk past them.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import effects
from tier0.engine.combat import play_card
from tier0.tests.conftest import make_enemy, make_state


# The four yields Prune's SHIPPED FACE paid, per play, before EB-219 moved
# them. (upgraded, reaction) -> Sparks. Nothing derives these; they are the
# arithmetic of the row as it stood at `f3bb301`, and they are the acceptance
# line ("the same Sparks") written as data.
FACE_PARITY = {
    (False, False): 1,
    (False, True): 2,
    (True, False): 2,
    (True, True): 3,
}


def _klee_state(with_aura: bool):
    """A board where Prune's Swirl either finds an aura to consume, or does not.

    Two enemies in the aura case, because the pilot aims a Swirl at the lowest-HP
    AURA BEARER (R211) and a board with one bare body is the honest "whiffed
    Swirl" shape.
    """
    if with_aura:
        state = make_state(enemies=[make_enemy(hp=20, name="low"),
                                    make_enemy(hp=30, name="aura")])
        state.enemies[1].aura = "hydro"
    else:
        state = make_state()
    state.player.character_id = "klee"
    return state


@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("reacted", [False, True])
def test_prune_pays_exactly_what_her_face_used_to_pay(upgraded, reacted):
    """The parity lock, all four cases."""
    card = loader.get_card(
        "prune_witch_hunt" + (upgrades.SUFFIX if upgraded else ""))
    state = _klee_state(with_aura=reacted)
    state.player.hand = [card]

    play_card(state, card)

    assert state.player.sparks == FACE_PARITY[(upgraded, reacted)]
    # The Block half never moved: it is on the no-reaction branch and Block is
    # not a signature resource, so LAW:145 does not reach it.
    assert state.player.block == (0 if reacted else 5)


def test_prunes_row_carries_no_gain_spark_anywhere():
    """`EB-219`'s acceptance line, first clause: no `gain_spark`.

    Walked over the WHOLE effect tree, branches included, rather than the top
    level -- one of the two ops that left was inside a conditional, so a
    top-level-only check would have passed on the card as it shipped.
    """
    def walk(effs):
        for fx in effs:
            yield fx
            for branch in ("then", "else"):
                yield from walk(fx.get(branch, []))

    for cid in ("prune_witch_hunt", "prune_witch_hunt" + upgrades.SUFFIX):
        ops = [fx["op"] for fx in walk(loader.get_card(cid).effects)]
        assert "gain_spark" not in ops, cid
        # ...and the rest of her face is untouched.
        assert "swirl" in ops and "block" in ops


def test_a_shared_pool_companions_swirl_mints_nothing():
    """The trigger is the PERSONAL pool, not "a companion that Swirled".

    `sucrose_gust` is a shared Mondstadt companion with an aimed Swirl -- the
    nearest neighbour Prune has. It reacts and it mints no Sparks, which is what
    keeps the declaration a KIT declaration rather than a rule about Anemo.
    """
    sucrose = loader.get_card("sucrose_gust")
    assert sucrose.is_companion and sucrose.personal_pool is None

    state = _klee_state(with_aura=True)
    state.player.hand = [sucrose]
    play_card(state, sucrose)

    assert state.reactions_this_card > 0, "the board must actually react"
    assert state.player.sparks == 0


def test_the_mint_is_once_per_play_not_once_per_turn():
    """Two Prune plays in one turn mint twice. The bound is per PLAY."""
    prune = loader.get_card("prune_witch_hunt")
    state = _klee_state(with_aura=False)
    state.player.hand = [prune, prune]

    play_card(state, prune)
    assert state.player.sparks == 1
    play_card(state, prune)
    assert state.player.sparks == 2


def test_a_replayed_companion_is_one_play_not_two():
    """The other half of "once per play", and the half LAW:145 forces.

    Study Buddy (`replay_next_companion`) resolves the next Companion a second
    time inside ONE card play. Her face used to mint on every resolution, so
    that combination paid twice; the kit mints once, because a per-play bound a
    replay can double is not a bound. Recorded in packet section 15.5 as the one
    deliberate divergence from the shipped face.
    """
    prune = loader.get_card("prune_witch_hunt")
    state = _klee_state(with_aura=False)
    state.player.hand = [prune]
    state.replay_next_companion = 1

    play_card(state, prune)

    # The card really did resolve twice -- 5 Block per resolution.
    assert state.player.block == 10
    # ...and minted once.
    assert state.player.sparks == 1


def test_the_declaration_is_bounded_and_the_bound_is_the_arithmetic_ceiling():
    """LAW:145's "bounds the amount generated per Companion play", as a number.

    The cap is not a fifth tunable: it is exactly the sum of the three limbs, so
    it can only ever bite if someone raises a limb without re-reading the clause
    -- which is the moment it is supposed to bite.
    """
    assert C.KLEE_COMPANION_SPARK_MAX_PER_PLAY == (
        C.KLEE_COMPANION_SPARK_BASE
        + C.KLEE_COMPANION_SPARK_REACTION_BONUS
        + C.KLEE_COMPANION_SPARK_UPGRADED_BONUS)
    assert C.KLEE_COMPANION_SPARK_MAX_PER_PLAY == max(FACE_PARITY.values())


def test_the_upgrade_sheet_and_the_kit_constant_are_one_number():
    """`kit_spark` is the sheet's writing of the kit's upgraded limb.

    Two writings of one fact drift; this is the assertion that stops them. The
    applier raises on a mismatch too (`upgrades.apply`), so this test is the
    cheap witness and that raise is the load-bearing one.
    """
    row = upgrades._upgrade_index()["prune_witch_hunt"]
    assert row == {"kit_spark": C.KLEE_COMPANION_SPARK_UPGRADED_BONUS}
    assert upgrades.has_upgrade("prune_witch_hunt"), \
        "her campfire choice is real -- it is paid by the kit, not by her face"


def test_exactly_one_personal_companion_exists_so_the_reach_is_stated_not_guessed():
    """The declaration is general in form and Prune-only in fact.

    If a second Personal Companion is ever authored this fails, and the packet's
    section 15.4 (which says "Prune-only") gets corrected rather than silently
    outgrown -- the same discipline the aimed-Swirl enumeration uses.
    """
    import yaml
    personal = []
    for sheet in loader.DOCS_CARD_SHEETS:
        rows = yaml.safe_load(
            (loader.DOCS_DIR / sheet).read_text(encoding="utf-8")) or []
        personal += [row["id"] for row in rows
                     if isinstance(row, dict) and row.get("personal_pool")]
    assert sorted(personal) == ["prune_witch_hunt"], personal


def test_a_personal_companion_in_the_wrong_deck_mints_nothing():
    """The kit-scoping half: it is KLEE's kit that declared the trigger."""
    prune = loader.get_card("prune_witch_hunt")
    state = _klee_state(with_aura=True)
    state.player.character_id = "furina"
    state.player.hand = [prune]

    play_card(state, prune)

    assert state.player.sparks == 0


def test_the_kit_trigger_is_the_only_spark_source_prune_touches():
    """No other generator moved (packet section 15.4).

    The emit is the witness: one `klee_companion_spark` event per play, and the
    `gain_spark` beneath it is the shared bank writer every other source uses.
    """
    prune = loader.get_card("prune_witch_hunt")
    state = _klee_state(with_aura=True)
    state.player.hand = [prune]
    play_card(state, prune)

    kinds = [e["event"] for e in state.log if e["event"].endswith("spark")
             or e["event"] == "klee_companion_spark"]
    assert kinds.count("klee_companion_spark") == 1
    assert effects.klee_personal_companion_spark.__module__.endswith("effects")
