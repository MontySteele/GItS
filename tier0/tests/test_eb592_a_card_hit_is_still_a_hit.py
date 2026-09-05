"""`EB-592`: a card hit fires a when-hit power, a performance does not, and a
KILLING hit fires nothing -- which is what the r15 seat actually watched.

WHAT THE SEAT SAW (Furina r15, natural lane, (c) 1, the four-Gardener elite).
"Skittish 6 never fired. B was at 12, took the 13-damage Chevreuse and died --
12 + 6 Block would have been 18. On the same turn, a dry 4-damage performance
took A from 25 to exactly 21. I never once saw a Gardener gain the 6 Block its
own buff line promised." Round 14, on `0.2.2753+proto`, had seen the same
power fire on card hits and not on performances, so the round-15 reading was
that a card hit had STOPPED counting as a hit somewhere between the builds.

IT HAD NOT, AND THE DIFF IS WHERE THAT WAS SETTLED. Between the two builds
nothing in the arm's card-damage path moved: `git diff` over
`klee-mod/KleeCode` across that range touches tips, the R260 opening arrival
(`EB-553`/`EB-558`), the Evoke's log row (`EB-564`) and the Spotlight window
line (`EB-567`), and not one line of the door a Companion Attack goes through
-- `DamageCmd.Attack(...).FromCard(...)`, a POWERED hit with a dealer, which
is what a when-hit power answers.

BOTH OF THE SEAT'S OWN OBSERVATIONS ARE THE TWO RULES, and each is already the
engines':

  * the 13-damage card hit KILLED a 12-HP body, and a body that is not alive
    gains no Block. The gate is `enemy.alive` in this engine and the base
    game's own `IsDead` guard in the mod, and it is not a Furina rule at all.
  * the 4-damage performance is `EB-548`: a performance is `source="salon"`,
    not `"attack"`, so no when-hit power fires. The Salon paragraph says so.

So the pin this row asks for is the THIRD case standing beside those two: a
card hit that lands on a body that survives it still fires the power. The
`EB-548` file already pins the pair; this one adds the killing hit, which is
the case the seat's own evidence was made of.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import effects, furina_reframe
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

SKITTISH = 6


@pytest.fixture(autouse=True)
def manual_on(monkeypatch):
    """Under the arm, so the claim is about the arm's board and not a
    flag-off one."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _gardener(hp):
    enemy = make_enemy(hp=hp)
    enemy.skittish = SKITTISH
    return enemy


def _board(hp):
    p = loader.build_player("furina")
    p.salon = ["crabaletta"]
    p.powers["salon_member"] = 1
    p.encore = 9
    return CombatState(player=p, enemies=[_gardener(hp)],
                       rng=random.Random(11))


def test_a_card_hit_on_a_surviving_body_fires_the_when_hit_power():
    """THE ROW'S ACCEPTANCE, half one. Nothing about the arm suppresses it."""
    state = _board(hp=60)
    enemy = state.enemies[0]

    effects.deal_damage_to_enemy(state, enemy, 13, source="attack")

    assert enemy.alive
    assert enemy.block == SKITTISH
    assert any(row["event"] == "skittish_block" for row in state.log)


def test_a_performance_on_the_same_body_does_not():
    """THE ROW'S ACCEPTANCE, half two -- `EB-548`'s rule, re-read here so the
    pair the seat compared lives in one file."""
    state = _board(hp=60)
    enemy = state.enemies[0]

    effects.salon_member_act(state, "crabaletta")

    assert enemy.alive and enemy.hp < 60
    assert enemy.block == 0


def test_a_killing_card_hit_fires_nothing_and_that_is_the_seats_own_witness():
    """THE SEAT'S 12-HP BODY, played. A when-hit power grants BLOCK, and a
    corpse gains none: the latch is not even set, so the reading "the card hit
    stopped counting" cannot be taken off a fight whose card hits all killed.
    """
    state = _board(hp=12)
    enemy = state.enemies[0]

    effects.deal_damage_to_enemy(state, enemy, 13, source="attack")

    assert not enemy.alive
    assert enemy.block == 0
    assert not enemy.skittish_fired
    assert not any(row["event"] == "skittish_block" for row in state.log)


def test_the_latch_is_per_turn_and_a_second_card_hit_pays_nothing():
    """The other half of "I never once saw it": the power is once per turn per
    body, so a turn that opens with a card hit shows the Block once and every
    hit after it shows none."""
    state = _board(hp=60)
    enemy = state.enemies[0]

    effects.deal_damage_to_enemy(state, enemy, 5, source="attack")
    assert enemy.block == SKITTISH
    enemy.block = 0                      # the enemy spent it absorbing

    effects.deal_damage_to_enemy(state, enemy, 5, source="attack")

    assert enemy.block == 0
