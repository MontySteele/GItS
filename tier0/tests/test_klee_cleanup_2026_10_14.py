"""The Klee/Varka cleanup batch (2026-10-14), Klee's three rows: the sim half.

`review/active/klee-varka-cleanup-2026-10-14.md`, staged on `klee-next`.
[USER]: "Otherwise agreed on these." Lizard-Tail Gunpowder draws a plain
card, Taste Test exhausts instead of adding two Confiscated (upgrade cost
2 -> 1), Exquisite Compound grows each Bomb by 7 [10]. The C# twin is
`KleeTests/Prototype/KleeCleanup20261014Tests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).
"""

from __future__ import annotations

from tier0.engine import klee_overhaul
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    filler, klee_state, load, overhaul, play, sizes)


def test_lizard_tail_gunpowder_places_eight_and_draws_one_with_nothing_set_off(
        overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.draw_pile = filler()
    hand = len(state.player.hand)
    card = load("proto_ko_ammo_scavenging")
    play(state, card, aim=enemy)
    assert sizes(enemy) == [8]
    assert len(state.player.hand) == hand + 1
    up = load("proto_ko_ammo_scavenging+")
    assert [fx for fx in up.effects if fx["op"] == "draw"] == [
        {"op": "draw", "amount": 1}]


def test_taste_test_exhausts_and_adds_no_confiscated(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 10)
    card, up = load("proto_ko_taste_test"), load("proto_ko_taste_test+")
    assert (card.cost, up.cost) == (2, 1)
    assert card.exhaust and up.exhaust
    assert all(fx["op"] != "add_card" for fx in card.effects)
    play(state, card, aim=enemy)
    assert enemy.hp == 200 - 2 * 10 and sizes(enemy) == [10]
    assert [c for c in state.player.discard_pile
            if c.id == klee_overhaul.CONFISCATED_ID] == []


def test_exquisite_compound_grows_each_bomb_by_seven_ten_upgraded(overhaul):
    for cid, growth in (("proto_ko_careful_arrangement", 7),
                        ("proto_ko_careful_arrangement+", 10)):
        # The play binds its aim to the lowest-HP enemy: b.
        a, b = make_enemy(hp=200, name="a"), make_enemy(hp=100, name="b")
        state = klee_state([a, b])
        klee_overhaul.place(state, a, 5)
        klee_overhaul.place(state, b, 2)
        play(state, load(cid), aim=b)
        assert sizes(a) == []
        assert sorted(sizes(b)) == [2 + growth, 5 + growth], cid
