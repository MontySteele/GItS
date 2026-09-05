"""`EB-588`: the player's Weak does not touch a member performance.

WHAT THE SEAT SAW (Furina r15, natural lane, (c) 4). Weak cut a member
performance from 6 to 4 twice, while the Salon paragraph printed on the same
screen says "a performance is not an [gold]Attack[/gold] and not a hit:
[gold]Vulnerable[/gold] moves it, but no [gold]Shatter[/gold] and no when-hit
power fires" -- a sentence that names Vulnerable as the one term that moves a
performance and names no Weak at all. The row's D default is that the text
stands.

THE TEXT WAS RIGHT AND THE PIPELINE WAS THE DEFECT, and the two halves of the
hit had already come apart on their own: a performance reaches the funnel as
`source="salon"` (`EB-548`) and, in the mod, `CreatureCmd.Damage` as
`ValueProp.Unpowered` with `dealer: null` -- while the MIRROR above it was
still running the dealer's modifiers, which is where the Weak was coming from.
`powered=False` is the engines' one flag for exactly that stage
(`deal_damage_to_enemy`'s own docstring), so this is the flag being told the
truth rather than a new rule.

ONE FLAG, SO IT TAKES STRENGTH WITH THE WEAK, and that is the flag's stated
meaning rather than a second decision -- the C# twin's doc calls
`powered: false` "the dealer's Strength and Weak, and with them every flat
attack buff the mirror carries", and refuses a second parameter meaning half
of it. What a member's number IS stays the member's own: the printed base, the
Fanfare Focus term and Grand Salon, through `salon_tick_amount`.

NOT ARM-SCOPED, like `salon_member_act` itself: a performance is not Furina
swinging on the shipped kit either, and there is one implementation of a
member acting to say so in.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, furina_reframe, powers
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

ENEMY_HP = 400


@pytest.fixture(autouse=True)
def manual_on(monkeypatch):
    """A member performs on a play only under the reframe's MANUAL leg; the
    upkeep leg below reaches the same one implementation."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _board(weak=0, strength=0, stage=("crabaletta",)):
    p = loader.build_player("furina")
    p.salon = list(stage)
    p.powers["salon_member"] = len(p.salon)
    p.encore = 9                       # paid, so the question is the CLASS of
    #                                    the modifier and never the dry cut
    if weak:
        p.powers["weak"] = weak
    if strength:
        p.powers["strength"] = strength
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(3))


def _printed(state):
    return effects.salon_tick_amount(state, "crabaletta", paid=True)


def test_a_performance_under_weak_deals_its_printed_number():
    """THE ROW'S ACCEPTANCE, and it is the seat's own board: Weak 1 up, one
    performance, the printed figure lands whole."""
    state = _board(weak=1)
    enemy = state.enemies[0]
    printed = _printed(state)

    effects.salon_member_act(state, "crabaletta")

    assert ENEMY_HP - enemy.hp == printed


def test_the_same_weak_still_cuts_an_attack_card_on_the_same_board():
    """The control that makes the row above a RULE rather than an inert
    debuff: one board, one Weak, the two classes of hit side by side."""
    state = _board(weak=1)
    enemy = state.enemies[0]
    base = 12

    effects.deal_damage_to_enemy(state, enemy, base, source="attack")

    assert ENEMY_HP - enemy.hp == int(base * C.WEAK_DEALT_MULT) < base


def test_the_dealer_s_strength_does_not_enter_a_performance_either():
    """ONE FLAG, BOTH TERMS. `powered=False` is `ValueProp.Unpowered` on the
    dealer's side, and a member's number is the member's -- so the Strength
    that a card would carry is not a term of a performance."""
    state = _board(strength=5)
    enemy = state.enemies[0]
    printed = _printed(state)

    effects.salon_member_act(state, "crabaletta")

    assert ENEMY_HP - enemy.hp == printed


def test_vulnerable_still_moves_a_performance():
    """THE HALF THE SENTENCE PROMISES, and the reason this cannot be written
    as `refpowers.unpowered_damage`: the TARGET's terms are untouched, which is
    what the Salon paragraph says out loud."""
    state = _board()
    enemy = state.enemies[0]
    printed = _printed(state)
    powers.apply_power(state, enemy, "vulnerable", 2)

    effects.salon_member_act(state, "crabaletta")

    assert ENEMY_HP - enemy.hp == int(printed * C.VULNERABLE_TAKEN_MULT)


def test_the_dry_cut_is_still_the_only_thing_that_shrinks_a_performance():
    """A member with no Encore performs at three-quarters, under Weak or not:
    the dry cut is a SIZE the member pays and the Weak is a term that no longer
    reaches it, and the pair is what the r15 seat had to separate by hand."""
    state = _board(weak=1)
    state.player.encore = 0
    enemy = state.enemies[0]

    effects.salon_member_act(state, "crabaletta")

    dry = effects.salon_tick_amount(state, "crabaletta", paid=False)
    assert ENEMY_HP - enemy.hp == dry
