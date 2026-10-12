"""Debug pins (2026-10-08): Perfect Timing replays and Wait For It... pays
on a Bomb that reacted, whichever Bomb it was and whenever in the turn."""

from tier0.engine import klee_overhaul
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    filler, klee_state, load, overhaul, play)


def _pt_hits(state, enemy):
    before = enemy.hp
    play(state, load("proto_ko_perfect_timing"), aim=enemy)
    return before - enemy.hp


def test_perfect_timing_replays_on_its_own_reacting_bomb(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    enemy.aura = "cryo"
    klee_overhaul.place(state, enemy, 4)
    dealt = _pt_hits(state, enemy)
    assert state.ko_reacted_this_turn == 1
    # The Melted Bomb, then two card hits of 8: the replay landed.
    assert dealt - 16 > 4


def test_perfect_timing_replays_on_an_earlier_reacting_bomb(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    enemy.aura = "hydro"
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.set_off(state, enemy)
    assert state.ko_reacted_this_turn == 1
    assert _pt_hits(state, enemy) == 16


def test_perfect_timing_does_not_replay_on_a_card_reaction(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 4)
    assert _pt_hits(state, enemy) == 4 + 8
    assert state.ko_reacted_this_turn == 0


def test_wait_for_it_pays_on_a_mine_reacting(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.draw_pile = filler()
    energy = state.player.energy
    play(state, load("proto_ko_wait_for_it"))
    enemy.aura = "cryo"
    klee_overhaul.place(state, enemy, 3, is_mine=True) if "is_mine" in \
        klee_overhaul.place.__code__.co_varnames else klee_overhaul.place(state, enemy, 3)
    klee_overhaul.set_off(state, enemy)
    assert len(state.player.hand) == 2
    assert state.player.energy == energy + 1
