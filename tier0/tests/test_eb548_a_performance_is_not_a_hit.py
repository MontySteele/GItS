"""`EB-548`: a member performance is not a HIT, and the Salon paragraph now
says so in the words a player already met on Klee's *Set off*.

WHAT THE SEAT SAW (Furina r13, assembled lane, the four-Gardener elite). All
four bodies carried *Skittish 6* -- "the first time it is hit each turn, it
gains 6 Block" -- and a performance never triggered it: "Chevalmarin hit C for
2 and C's HP moved by 2 with no Block gained. So the correct line against
Skittish is to spend the free perform first and then attack." The seat called
it "the most useful thing I learned and effectively invisible", and it is what
won the elite.

THE RULE WAS BUILT AND THE WORDS NAMED THE WRONG SIDE OF THE BOARD. `EB-476`
put the class on the arm's Salon paragraph -- "a performance is not an Attack:
Vulnerable moves it, Shatter and on-Attack triggers do not" -- which is exactly
the wording `EB-490` had to fix one kit over: "on-Attack trigger" reads as
something on the PLAYER's own side, and a player looking for the rule about the
thing on the ENEMY's status bar does not find it there. The sentence now says
"and not a hit ... no when-hit power fires", which is `ForSetOff`'s and the
Plan tip's (`EB-538`) sentence at the same call.

WHAT THIS FILE PINS is the tier-0 half of that call: a performance's damage
carries `source="salon"`, which is not `"attack"`, and `"attack"` is what gates
Shatter, the on-hit detonation and Skittish in this engine -- the same split
`ElementalHit.Deal`'s `ValueProp.Unpowered` makes in the mod. The WORDS are
pinned in the C# suite, where they live
(`KleeTests/Prototype/Round19Tests.cs`).

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
SKITTISH = 6


@pytest.fixture(autouse=True)
def manual_on(monkeypatch):
    """A member performs on a play only under the reframe's MANUAL leg."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _board(stage=("crabaletta",)):
    p = loader.build_player("furina")
    p.salon = list(stage)
    p.powers["salon_member"] = len(p.salon)
    p.encore = 9                       # paid, so the question is the CLASS of
    #                                    the hit and never its size
    enemy = make_enemy(hp=ENEMY_HP)
    enemy.skittish = SKITTISH
    return CombatState(player=p, enemies=[enemy], rng=random.Random(3))


def test_a_performance_hits_and_skittish_does_not_fire():
    """The seat's own reading, played: HP moves and no Block appears."""
    state = _board()
    enemy = state.enemies[0]

    effects.salon_member_act(state, "crabaletta")

    hit = next(row for row in state.log if row["event"] == "damage")
    assert hit["source"] == "salon" != "attack"
    assert enemy.hp < ENEMY_HP
    assert enemy.block == 0, "Skittish is an Attack-card rule and did not fire"


def test_the_same_body_pays_skittish_to_an_attack_card_in_the_same_fight():
    """The control that makes the first test a RULE rather than an inert
    enemy, and it is the seat's own comparison: the performance first, then the
    Attack, on one body in one turn."""
    state = _board()
    enemy = state.enemies[0]

    effects.salon_member_act(state, "crabaletta")
    assert enemy.block == 0

    effects.deal_damage_to_enemy(state, enemy, 6, source="attack")

    assert enemy.block == SKITTISH


def test_a_dry_performance_is_the_same_class_of_hit():
    """A member with no Encore performs at three-quarters and it is still not
    an Attack: the dry cut is a size and this row is about the class, which is
    the pair the r13 seat had to separate for itself."""
    state = _board()
    state.player.encore = 0
    enemy = state.enemies[0]

    effects.salon_member_act(state, "crabaletta")

    printed = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
    assert enemy.hp == ENEMY_HP - int(printed * C.SALON_DRY_DAMAGE_MULT)
    assert enemy.block == 0
