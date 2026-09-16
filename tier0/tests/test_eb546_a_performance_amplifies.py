"""`EB-546`: a member performance into a foreign aura amplifies, paid or dry.

WHAT THE SEAT SAW (Furina r13, assembled lane, fight 1 turn 2). "The salon log
read: *Crabaletta hit Sludge Spinner for 6 Hydro, and left no aura on it.* The
enemy was wearing Pyro Aura 2, and Crabaletta was at full strength (Encore
paid). Vaporize is printed as *this hit deals 1.5x damage and consumes the
aura* -- so 9. The HP bar moved 24 to 18. **Six.** The aura was consumed; the
multiplier was not applied." And in fight 2 the same card into the same aura
while DRY hit for 6 off a 4.5 base, which is 1.5x. The seat could not reconcile
the two, and neither could the round.

WHAT THIS FILE IS. The row asks for the reproduction first: a performance into
a Pyro aura at Encore paid and at Encore dry, with the amplified number pinned
on both. THE SIM AMPLIFIES ON BOTH -- 9 paid and 6 dry -- so the invariant the
seat expected is the invariant this engine has, and it is held here rather than
re-derived the next time the reading comes back. The mod's arithmetic and its
wiring are pinned in `KleeTests/Prototype/Round19Tests.cs`.

THE CAUSE, FOUND 2026-09-16, AND IT WAS NEVER THE AMPLIFIER. The amplifier was
applied. What was also applied, and what no screen in the round said a word
about, was **the DEALER's Weak** -- and the enemy in the seat's own sentence is
the one that hands it out. `SludgeSpinner.OilSprayMove` is
`PowerCmd.Apply<WeakPower>(..., targets, 1m, ...)` off the 0.111.0 decompile,
its opening move carries a `DebuffIntent` beside the attack, and the reading is
fight 1 TURN TWO -- so Furina went into that performance Weak. The round's
pipeline then read, in order: the dealer's terms, the amplifier, the target's.

    paid tick 6 -> Weak 0.75 -> 4.5 -> Vaporize 1.5 -> 6.75
                -> one truncation at the end -> 6 landed, aura consumed

Six, with the aura gone. Every clause of the seat's report is true at once and
nothing was dropped.

AND THE SECOND READING IS THE SAME NUMBER BY A DIFFERENT ROUTE, which is
exactly why the two could not be reconciled: the fight-2 hit was DRY and
unWeakened -- `int(6 * 0.75) = 4`, then `* 1.5 = 6`. Two sixes, one from a
Weak paid performance and one from a dry one, off two arithmetics that share
no term but the amplifier. The seat compared them, saw one multiply and the
other not, and filed the only conclusion the screens supported.

IT IS ALREADY FIXED, BY `EB-588`, WHICH FOUND THE SAME WEAK TWO ROUNDS LATER
from the other end -- as a 6 cut to 4 with no reaction in the picture at all
(Furina r15 lane 2 (c) 4). A performance now asks the funnel for an UNPOWERED
hit in both engines (`effects.salon_member_act`'s `powered=False`, the mod's
`SalonMemberPower.PerformMember`'s `powered: false`), so the dealer's terms do
not enter it. The two rows are one defect seen twice, and the r13 reading is
the earlier sighting.

WHAT IS PINNED FOR THAT BELOW: the seat's exact board, with Weak on, landing
the 9 it expected today; and the pre-`EB-588` arithmetic, spelled out of the
constants, landing the 6 it got. The second is the row's answer and it is
written as arithmetic rather than as a re-plumbed engine, because the pipeline
that produced it is gone and a test that rebuilt it would be pinning a stage
neither engine has.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, powers
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

ENEMY_HP = 400
#: Crabaletta's printed performance and the two multipliers the reading turns
#: on. Read off the constants rather than typed, so a retune moves the pins.
PRINTED = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
DRY = C.SALON_DRY_DAMAGE_MULT
VAPORIZE = C.VAPORIZE_MULT
#: The third term, and the one the round never had on a screen.
WEAK = C.WEAK_DEALT_MULT


def _board(encore: int, weak: int = 0):
    p = loader.build_player("furina")
    p.salon = ["crabaletta"]
    p.powers["salon_member"] = 1
    p.encore = encore
    if weak:
        p.powers["weak"] = weak
    enemy = make_enemy(hp=ENEMY_HP)
    enemy.aura = "pyro"
    enemy.aura_turns = 2
    return CombatState(player=p, enemies=[enemy], rng=random.Random(3))


def test_a_paid_performance_into_pyro_vaporizes():
    """The seat's own board, played: full strength into a Pyro aura."""
    st = _board(encore=9)
    enemy = st.enemies[0]

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - int(PRINTED * VAPORIZE)
    assert enemy.hp == ENEMY_HP - 9, "the number the seat expected and did not get"
    assert enemy.aura is None, "the aura is consumed by the reaction"


def test_a_dry_performance_into_pyro_vaporizes_too():
    """The other half, and the one the seat DID see: the dry cut is a size and
    the amplifier is a separate term, so a member with no Encore still
    multiplies what it deals."""
    st = _board(encore=0)
    enemy = st.enemies[0]

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - int(int(PRINTED * DRY) * VAPORIZE)
    assert enemy.hp == ENEMY_HP - 6
    assert enemy.aura is None


def test_the_log_carries_the_landed_number_and_not_the_tick():
    """`EB-511`'s rule, which is what makes the two tests above readable off a
    screen: the row a seat reconciles the fight's HP against is the number that
    LANDED, after the dealer's terms, the amplifier and the target's."""
    st = _board(encore=9)

    effects.salon_member_act(st, "crabaletta")

    hit = next(ev for ev in st.log if ev["event"] == "damage")
    assert hit["base"] == PRINTED
    assert hit["amount"] == int(PRINTED * VAPORIZE)


def test_a_performance_into_a_bare_body_applies_its_own_element():
    """The board the paid reading would look like if the aura had expired, and
    it is here because it is the one reading that produces the seat's 6 without
    a defect -- and it is EXCLUDED by the seat's own log line, which said the
    body was left wearing nothing. A bare body comes out wearing Hydro."""
    st = _board(encore=9)
    enemy = st.enemies[0]
    enemy.aura = None
    enemy.aura_turns = 0

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - PRINTED
    assert enemy.aura == "hydro"


# ---------------------------------------------------------------------------
# The cause, 2026-09-16.
# ---------------------------------------------------------------------------


def test_the_seats_own_board_had_weak_on_it_and_lands_nine_today():
    """THE BOARD AS IT ACTUALLY STOOD: Sludge Spinner's opening Oil Spray
    carries a `DebuffIntent` and applies `WeakPower` 1, and the reading is
    turn TWO -- so the Weak was on Furina when Crabaletta performed.

    Today it costs nothing, because `EB-588` took the dealer's terms out of a
    performance in both engines. This is the arm that says the r13 board is no
    longer reachable, rather than that it never was."""
    st = _board(encore=9, weak=1)
    enemy = st.enemies[0]

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - int(PRINTED * VAPORIZE)
    assert enemy.hp == ENEMY_HP - 9
    assert enemy.aura is None


def test_the_dry_cut_is_likewise_untouched_by_weak():
    """The same statement on the other half, so "Weak does not enter a
    performance" is pinned at both sizes rather than at the one that happens
    to be bigger."""
    st = _board(encore=0, weak=1)
    enemy = st.enemies[0]

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - 6


def test_the_pre_eb588_pipeline_is_exactly_the_six_the_seat_got():
    """THE ROW'S ANSWER, and it is arithmetic rather than a re-plumbed engine
    because the stage that produced it is gone from both engines.

    `powers.modify_damage_dealt` IS that stage, still here and still used by
    every hit that really is a dealer's -- so the pre-`EB-588` performance is
    exactly this call in front of the amplifier. Run it on the seat's numbers
    and the answer is six, with the aura consumed by the branch that reacted.

    AND THE OTHER SIX, from the fight-2 dry reading, off terms that share only
    the amplifier: that is why the two readings could not be reconciled from
    the screens."""
    weakened = _board(encore=9, weak=1)
    dealer_stage = powers.modify_damage_dealt(weakened.player, PRINTED)

    # The seat's fight-1 six: a PAID tick, Weak, then Vaporize. The dealer
    # stage keeps its halves -- 4.5, not 4 -- and the single truncation the
    # funnel takes at the end is what turns 6.75 into the six on the bar. The
    # mod's `SimDamagePipeline.Resolve` composes the same three terms in the
    # same order and lands on the same number.
    assert dealer_stage == PRINTED * WEAK == 4.5
    assert int(dealer_stage * VAPORIZE) == 6

    # The seat's fight-2 six: a DRY tick, no Weak, then Vaporize.
    assert int(int(PRINTED * DRY) * VAPORIZE) == 6

    # And the number the seat expected, which is what the same board lands now.
    assert int(PRINTED * VAPORIZE) == 9
