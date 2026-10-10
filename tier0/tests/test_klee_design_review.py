"""THE KLEE DESIGN REVIEW (2026-10-08, ruled): the sim half.

`review/active/klee-design-review-2026-10-08.md`, all five picks at the
defaults. [USER]: "Nope, this all looks good. I'm now in agreement with all
picks." Rule 1 grows 2, rule 4 opens with 3, every drafted placer prints 2
bigger, Fire! Fire! and Blasting Spree in for Playdate and Pop! (Pop! kept
off-pool for Klee Can Explain!). The C# twin is
`KleeTests/Prototype/KleeDesignReviewTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).
"""

from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import klee_overhaul
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    klee_state, load, overhaul, play, sizes)


def _first(card, op):
    return next(fx for fx in card.effects if fx.get("op") == op)


# --- The rules ----------------------------------------------------------------

def test_rule_1_grows_two_and_alice_still_doubles_it(overhaul):
    assert C.KLEE_OVERHAUL_BOMB_GROWTH == 2
    assert C.KLEE_OVERHAUL_BOMB_GROWTH * C.KLEE_OVERHAUL_ALICE_MULTIPLIER == 4
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.turn = 2
    klee_overhaul.place(state, enemy, 8)
    klee_overhaul.turn_start(state)
    assert sizes(enemy) == [10]


def test_rule_4_opens_with_three_sparks(overhaul):
    assert C.KLEE_OVERHAUL_OPENING_SPARK == 3
    state = klee_state([make_enemy(hp=200)])
    state.turn = 1
    klee_overhaul.turn_start_late(state)
    assert state.player.sparks == 3


# --- The pool -----------------------------------------------------------------

def test_two_out_two_in_and_the_split_holds(overhaul):
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 78 and len(set(ids)) == 78
    assert "proto_ko_playdate" not in ids
    assert "proto_ko_playdate" not in {c.id for c in loader.prototype_cards()}
    assert "proto_ko_pop" not in ids
    assert C.KLEE_OFF_POOL_ROW_IDS == ("proto_ko_pop",)
    assert load("proto_ko_pop").rarity == "common"     # the row stays
    assert ids[-5:-3] == C.KLEE_DESIGN_REVIEW_IDS == (
        "proto_ko_fire_fire", "proto_ko_blasting_spree")
    rarity = collections.Counter(load(cid).rarity for cid in ids)
    assert rarity == {"common": 25, "uncommon": 32, "rare": 21}
    shapes = {cid: (load(cid).type, load(cid).cost, load(cid).rarity)
              for cid in C.KLEE_DESIGN_REVIEW_IDS}
    assert shapes == {
        "proto_ko_fire_fire": ("attack", 1, "common"),
        "proto_ko_blasting_spree": ("skill", 1, "common"),
    }


#: Sec.4.2: every drafted placer in the 78, (base, upgraded), after the +2.
PLACERS = {
    "proto_ko_mine_toss": ("plant_bomb", "size", 9, 12),
    "proto_ko_bang_bang": ("plant_bomb", "size", 6, 8),
    "proto_ko_ammo_scavenging": ("plant_bomb", "size", 6, 9),
    "proto_ko_booby_trap": ("plant_bomb", "size", 7, 10),
    "proto_ko_coven_errand": ("plant_bomb", "size", 10, 12),
    "proto_ko_witches_circle": ("apply_power", "amount", 5, 7),
    "proto_ko_bombs_away": ("plant_bomb", "size", 6, 8),
    "proto_ko_hiding_spot": ("plant_bomb", "size", 5, 7),
    "proto_ko_jumpy_dumpty_mk_iii": ("damage", "plant_on_hit", 4, 5),
    "proto_ko_mine_all_mine": ("plant_bomb", "size", 6, 8),
    "proto_ko_party_poppers": ("apply_power", "amount", 5, 6),
    "proto_ko_secret_base": ("apply_power", "amount", 6, 8),
    "proto_ko_windblume_fireworks": ("plant_bomb", "size", 8, 10),
    "proto_ko_dodoco": ("apply_power", "amount", 5, 7),
    "proto_ko_finders_keepers": ("apply_power", "amount", 6, 8),
}


def test_every_drafted_placer_prints_two_bigger(overhaul):
    for cid, (op, key, base, up) in PLACERS.items():
        assert cid in C.KLEE_OVERHAUL_POOL_IDS, cid
        assert _first(load(cid), op)[key] == base, cid
        assert _first(load(cid + "+"), op)[key] == up, cid
    # Coven Errand's companion rider rides the printed size: 14, and 16.
    assert _first(load("proto_ko_coven_errand"), "plant_bomb")[
        "bonus_if"]["amount"] == 4


def test_the_starter_and_pop_do_not_move(overhaul):
    assert _first(load("proto_ko_jumpy_dumpty"), "plant_bomb")["size"] == 8
    assert _first(load("proto_ko_pop"), "plant_bomb")["size"] == 5


# --- Fire! Fire! --------------------------------------------------------------

def test_fire_fire_places_seven_and_sets_the_enemy_off(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_fire_fire"), aim=enemy)
    assert enemy.hp == 193
    assert sizes(enemy) == []
    assert state.player.sparks == 1
    assert enemy.aura == "pyro"


def test_fire_fire_cashes_what_is_already_cooking(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 8)
    klee_overhaul.place(state, b, 8)
    play(state, load("proto_ko_fire_fire+"), aim=a)
    assert a.hp == 200 - (8 + 10)
    assert sizes(a) == [] and sizes(b) == [8]
    assert state.player.sparks == 2


# --- Blasting Spree -----------------------------------------------------------

def test_blasting_spree_places_four_on_all_and_adds_a_dazed(overhaul):
    a, b, c = (make_enemy(hp=200, name=n) for n in "abc")
    state = klee_state([a, b, c])
    play(state, load("proto_ko_blasting_spree"))
    assert sizes(a) == sizes(b) == sizes(c) == [4]
    assert (a.hp, b.hp, c.hp) == (200, 200, 200)
    assert [x.id for x in state.player.discard_pile] == ["status_dazed"]


def test_blasting_spree_upgraded_places_six(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    play(state, load("proto_ko_blasting_spree+"))
    assert sizes(a) == sizes(b) == [6]
