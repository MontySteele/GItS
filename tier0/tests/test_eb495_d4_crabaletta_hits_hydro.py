"""`EB-495` D4 -- Crabaletta's act and bow, FLIPPED by Furina Stage draft 3.

D4 was a parity repair: the C# act and bow passed `Elements.Element.Hydro`
and the sim passed none, so the sim was brought up to the game. On
2026-09-25 [USER] ruled the element off every act ("removing the Hydro
application from the end-of-turn effects on Chevalmarin and Crabaletta"), and
the Bow became the act once more. So both engines now deal PLAIN damage: the
C# through `ElementalHit.DealUnelemented`, the sim with `element=None`. This
file keeps D4's shapes and pins the new answer: no aura set, none consumed,
no reaction -- including the Electro-Charged cell D4 was about.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B): these are shape
assertions about an engine, not numbers about a game.
"""

from __future__ import annotations

import random

import pytest

from tier0.engine import furina_stage
from tier0.engine.state import CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _state(aura=None, enemy_hp=99):
    player = Player(hp=200, max_hp=200, fanfare_cap=99, character_id="furina")
    enemy = Enemy(hp=enemy_hp, max_hp=enemy_hp, name="paper",
                  intents=[{"kind": "block", "amount": 0}])
    enemy.aura = aura
    st = CombatState(player=player, enemies=[enemy], rng=random.Random(0))
    st.turn = 1
    return st


def test_crabalettas_act_leaves_no_aura(arm):
    st = _state()
    st.player.stage = [["crabaletta", 4]]
    FS.perform(st, "crabaletta")
    assert st.enemies[0].aura is None
    assert st.enemies[0].hp == 99 - FS.ACT_CRABALETTA_DAMAGE


def test_crabalettas_bow_leaves_no_aura(arm):
    st = _state()
    st.player.stage = [["crabaletta", 1]]
    FS.spend(st, 1)
    assert st.player.stage == []
    assert st.enemies[0].aura is None


@pytest.mark.parametrize("member", ["crabaletta", "chevalmarin"])
def test_an_act_into_an_electro_aura_does_not_react(arm, member):
    """The cell D4 was about, flipped: Electro standing, a plain hit landing.
    No Electro-Charged, no DoT, and the aura is still there."""
    st = _state(aura="electro")
    st.player.stage = [[member, 4]]
    FS.perform(st, member)
    enemy = st.enemies[0]
    assert enemy.powers.get("dot", 0) == 0
    assert enemy.aura == "electro"
    assert not [e for e in st.log if e["event"] == "reaction"]


def test_a_crabaletta_bow_into_an_electro_aura_does_not_react(arm):
    st = _state(aura="electro")
    st.player.stage = [["crabaletta", 1]]
    FS.spend(st, 1)
    assert st.enemies[0].powers.get("dot", 0) == 0
    assert st.enemies[0].aura == "electro"


def test_a_blocked_act_leaves_nothing_behind(arm):
    st = _state()
    st.enemies[0].block = 50
    st.player.stage = [["crabaletta", 4]]
    FS.perform(st, "crabaletta")
    assert st.enemies[0].aura is None
    assert st.enemies[0].hp == 99
