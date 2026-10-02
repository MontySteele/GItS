"""FURINA, THE STAGE -- three fixes (2026-09-27), the sim engine's pins.

[USER]: "For the furina Fix items - I like your default," and "I think that
Wriothesley needs a buff. Perhaps he also reflects the Blocked damage. so 2."

  1. A Five-Century Act returns a performer once a turn, however many copies;
     the latch clears at the start of her turn.
  2. Echoing Hall moved HALF the fade's loss to the front, rounded down.
     (The 2026-09-29 fade pass cut the card; its pin left with it.)
  3. Wriothesley always attacks: 4, plus 2 per Fanfare hits took from him,
     plus 1 per damage her Block stopped while he stood in front.

C# twin: `klee-mod/KleeTests/Prototype/FurinaLoopFixes20260927Tests.cs`.
NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0.engine import combat, furina_stage
from tier0.engine.state import CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    yield


def _enemy(hp=100, intents=None):
    return Enemy(hp=hp, max_hp=hp, name="paper",
                 intents=intents or [{"kind": "block", "amount": 0}])


def _state(stage=(), enemies=None):
    player = Player(hp=200, max_hp=200, fanfare_cap=99,
                    character_id="furina")
    st = CombatState(player=player, enemies=enemies or [_enemy()],
                     rng=random.Random(0))
    st.turn = 2
    st.player.stage = [list(pair) for pair in stage]
    return st


# ---- 1. A Five-Century Act, once a turn ------------------------------------

def test_a_five_century_act_returns_once_a_turn_and_clears_at_her_turn(arm):
    st = _state([["usher", 1], ["crabaletta", 1], ["chevalmarin", 9]])
    st.player.powers[FS.FIVE_CENTURY_ACT] = 2      # two copies: one return
    FS.absorb(st, 1)                               # Usher emptied, Bows
    FS.settle_hit(st)
    assert [m for m, _f in st.player.stage] == [
        "crabaletta", "chevalmarin", "usher"]
    FS.absorb(st, 1)                               # Crabaletta emptied, Bows
    FS.settle_hit(st)
    assert [m for m, _f in st.player.stage] == ["chevalmarin", "usher"]
    FS.turn_start_rest(st)
    assert st.player.stage_returned is False
    FS.absorb(st, 9)                               # a new turn: it returns
    FS.settle_hit(st)
    assert [m for m, _f in st.player.stage] == ["usher", "chevalmarin"]


# ---- 3. Wriothesley always attacks -----------------------------------------

def test_wriothesley_with_nothing_hit_deals_his_floor(arm):
    st = _state([["wriothesley", 8], ["usher", 3]])
    FS.perform(st, "wriothesley")
    assert st.enemies[0].hp == 100 - FS.ACT_WRIOTHESLEY_BASE == 96


def test_her_block_counts_for_him_only_while_he_is_in_front(arm):
    st = _state([["wriothesley", 8], ["usher", 3]])
    FS.credit_blocked(st, 6)
    assert st.player.stage_blocked == {"wriothesley": 6}
    behind = _state([["usher", 3], ["wriothesley", 8]])
    FS.credit_blocked(behind, 6)
    assert behind.player.stage_blocked == {}
    FS.perform(st, "wriothesley")
    assert st.enemies[0].hp == 100 - (4 + 6)
    FS.perform(st, "wriothesley")                  # the act reset it
    assert st.enemies[0].hp == 100 - (4 + 6) - 4


def test_a_real_hit_through_the_enemy_turn_feeds_his_bow_both_counts(arm):
    """End to end: an enemy's 12 into her 5 Block while he stands in front
    at 3. Her Block stops 5, he loses 3 and Bows, the other 4 reach her --
    and his Bow deals 4 + 2 x 3 + 1 x 5."""
    enemy = _enemy(intents=[{"kind": "attack", "amount": 12}])
    st = _state([["wriothesley", 3], ["usher", 3]], enemies=[enemy])
    st.player.block = 5
    hp = st.player.hp
    combat._enemy_turn(st, enemy)
    assert [m for m, _f in st.player.stage] == ["usher"]
    assert st.player.hp == hp - 4
    assert enemy.hp == 100 - (4 + 2 * 3 + 1 * 5)
