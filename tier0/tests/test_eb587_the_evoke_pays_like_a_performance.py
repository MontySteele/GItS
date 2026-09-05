"""`EB-587`: an Evoke is a performance, and it pays like one.

WHAT THE SEAT SAW (Furina r15, assembled lane, (c) 1). At 0 Encore three
member performances printed and landed DRY -- three-quarters, exactly as the
Salon paragraph says -- and the Evoke on the same turn delivered its full 14.
The one act on the stage that also costs a member was the one act the Encore
economy did not price, and the tip's explanation for that ("the card's Encore
price pays for it", `F7` (1)) fails on Curtain Rises, which Evokes by
deploying onto a full stage and prints no Encore price at all.

THE RULE, taken at the row's D default: the Evoke spends the upkeep's 1
Encore, or resolves at three-quarters when the pool is dry -- a performance's
bill, because an Evoke is a performance that also costs the member. The
card's own printed Encore price is untouched and still gated and spent at the
play (`F7` (1)); this is a SECOND bill from the same pool, taken inside
`_salon_bow` where the one implementation of a member bowing lives.

ARM-SCOPED, like the Focus multiplier beside it: a SHIPPED bow is the
displaced member's payoff and is not a performance, so a release build's bow
is byte-identical. The C# twin is `SalonMemberPower.Bow`'s `evokePaid`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, furina_reframe
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

ENEMY_HP = 400


@pytest.fixture(autouse=True)
def evoke_on(monkeypatch):
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_EVOKE"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _board(member, encore, fanfare=0):
    p = loader.build_player("furina")
    p.salon = [member]
    p.powers["salon_member"] = 1
    p.encore = encore
    p.fanfare = fanfare
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(5))


def _full(state, member):
    """What the Evoke is worth PAID: the printed bow through the Focus term,
    read off the same expression `_salon_bow` resolves through."""
    spec = C.SALON_MEMBERS[member]["bow"]
    base = spec.get("damage", 0) or spec.get("block", 0)
    return effects._salon_amount(
        state, base, focus_mult=furina_reframe.evoke_focus_mult(state.player))


def test_an_evoke_at_zero_encore_resolves_at_three_quarters():
    """THE ROW'S ACCEPTANCE. The seat's own board: a dry pool, and the Evoke
    takes the cut every performance beside it takes."""
    state = _board("crabaletta", encore=0)
    enemy = state.enemies[0]
    full = _full(state, "crabaletta")

    effects._salon_bow(state, "crabaletta", evoked=True)

    assert ENEMY_HP - enemy.hp == int(full * C.SALON_DRY_DAMAGE_MULT) < full


def test_an_evoke_that_can_pay_spends_one_encore_and_lands_whole():
    state = _board("crabaletta", encore=4)
    enemy = state.enemies[0]
    full = _full(state, "crabaletta")

    effects._salon_bow(state, "crabaletta", evoked=True)

    assert state.player.encore == 4 - C.SALON_TICK_ENCORE_COST
    assert ENEMY_HP - enemy.hp == full


def test_the_dry_cut_reaches_a_block_evoke_as_well():
    """The Usher prints Block where Crabaletta prints damage, and the cut is
    about the member's NUMERIC rather than about damage -- the same split
    `salon_tick_amount` already makes for a performance."""
    state = _board("usher", encore=0)
    full = _full(state, "usher")

    effects._salon_bow(state, "usher", evoked=True)

    assert state.player.block == int(full * C.SALON_DRY_DAMAGE_MULT) < full


def test_a_shipped_bow_pays_nothing_and_takes_no_cut():
    """THE ARM SCOPE, and it is the whole reason the bill lives behind
    `evoked`: the shipped bow is the displaced member's payoff, not a
    performance, and a release build must be byte-identical."""
    state = _board("crabaletta", encore=0)
    enemy = state.enemies[0]
    spec = C.SALON_MEMBERS["crabaletta"]["bow"]
    printed = effects._salon_amount(state, spec["damage"])

    effects._salon_bow(state, "crabaletta")          # evoked=False

    assert state.player.encore == 0
    assert ENEMY_HP - enemy.hp == printed


def test_an_evoke_pays_the_same_upkeep_a_performance_does():
    """ONE PRICE, NOT TWO. The number spent is the tick's constant, read off
    `SALON_TICK_ENCORE_COST` rather than a literal, so a repricing of the
    upkeep moves both acts together."""
    for member in ("crabaletta", "usher"):
        state = _board(member, encore=6)

        effects._salon_bow(state, member, evoked=True)

        assert state.player.encore == 6 - C.SALON_TICK_ENCORE_COST
