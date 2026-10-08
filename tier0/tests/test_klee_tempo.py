"""THE KLEE TEMPO PAPER (2026-10-07, ruled): the sim half.

`review/active/klee-tempo-paper-2026-10-07.md` sec.3. [USER]: "I personally
found Blast Shield and Kitchen Alchemy quite useful in my runs, so I'm not
sure I buy that they should go. Otherwise agreed." Five out (It Wasn't Me!,
Sorry, Jean..., Grounded, Sit Tight, Experiment in Progress), five in. The
C# twin is `KleeTests/Prototype/KleeTempoTests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B).
"""

from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import klee_overhaul
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    filler, klee_state, load, overhaul, play, sizes)

CUT = ("proto_ko_it_wasnt_me", "proto_ko_sorry_jean", "proto_ko_grounded",
       "proto_ko_sit_tight", "proto_ko_patience_klee")


def _statuses(state, cid):
    return [c for c in state.player.discard_pile if c.id == cid]


def test_five_out_five_in_and_the_split_holds(overhaul):
    ids = C.KLEE_OVERHAUL_POOL_IDS
    assert len(ids) == 78 and len(set(ids)) == 78
    rows = {c.id for c in loader.prototype_cards()}
    for cid in CUT:
        assert cid not in ids and cid not in rows, cid
    assert ids[-8:-3] == C.KLEE_TEMPO_IDS
    rarity = collections.Counter(load(cid).rarity for cid in ids)
    assert rarity == {"common": 25, "uncommon": 32, "rare": 21}
    shapes = {cid: (load(cid).type, load(cid).cost, load(cid).rarity)
              for cid in C.KLEE_TEMPO_IDS}
    assert shapes == {
        "proto_ko_simmer": ("attack", 1, "common"),
        "proto_ko_taste_test": ("attack", 2, "uncommon"),
        "proto_ko_tinkering": ("skill", 0, "uncommon"),
        "proto_ko_dodoco_tag": ("attack", 1, "uncommon"),
        "proto_ko_explosive_spark": ("attack", 0, "common"),
    }


# --- Simmer -------------------------------------------------------------------

def test_simmer_with_no_bomb_deals_its_flat_four(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_simmer"), aim=enemy)
    assert enemy.hp == 196
    assert len(_statuses(state, "status_dazed")) == 1


def test_simmer_adds_half_the_largest_bomb_rounded_down_and_keeps_it(overhaul):
    """The largest Bomb is read off the whole board; the hit lands on the aimed
    enemy. Nothing goes off: the charges stay, no Spark is minted."""
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 6)
    klee_overhaul.place(state, b, 21)
    play(state, load("proto_ko_simmer"), aim=a)
    assert a.hp == 200 - (4 + 10)
    assert sizes(a) == [6] and sizes(b) == [21]
    assert state.player.sparks == 0


def test_simmer_upgraded_is_six_flat(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 20)
    play(state, load("proto_ko_simmer+"), aim=enemy)
    assert enemy.hp == 200 - (6 + 10)


def test_simmer_is_card_damage_and_takes_strength(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers["strength"] = 3
    klee_overhaul.place(state, enemy, 8)
    play(state, load("proto_ko_simmer"), aim=enemy)
    assert enemy.hp == 200 - (4 + 4 + 3)


# --- Taste Test ---------------------------------------------------------------

def test_taste_test_deals_every_bomb_on_the_enemy_and_keeps_them(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 12)
    klee_overhaul.place(state, a, 5, is_mine=True)
    klee_overhaul.place(state, b, 30)
    play(state, load("proto_ko_taste_test"), aim=a)
    assert a.hp == 200 - 17                 # 12 + the Mine 5; b's not read
    assert sizes(a) == [12, 5] and sizes(b) == [30]
    assert state.player.sparks == 0
    assert len(_statuses(state, klee_overhaul.CONFISCATED_ID)) == 2


def test_taste_test_on_a_bare_enemy_deals_nothing(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_taste_test"), aim=enemy)
    assert enemy.hp == 200
    assert len(_statuses(state, klee_overhaul.CONFISCATED_ID)) == 2


def test_taste_test_upgraded_adds_one_confiscated(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 9)
    play(state, load("proto_ko_taste_test+"), aim=enemy)
    assert enemy.hp == 191
    assert len(_statuses(state, klee_overhaul.CONFISCATED_ID)) == 1


# --- Tinkering, Dodoco Tag, Explosive Spark --------------------------------------

def test_tinkering_mints_two_sparks_three_upgraded(overhaul):
    state = klee_state()
    play(state, load("proto_ko_tinkering"))
    assert state.player.sparks == 2
    assert len(_statuses(state, klee_overhaul.CONFISCATED_ID)) == 1
    state = klee_state()
    play(state, load("proto_ko_tinkering+"))
    assert state.player.sparks == 3


def test_dodoco_tag_hits_blocks_and_adds_a_dazed(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_dodoco_tag"), aim=enemy)
    assert enemy.hp == 193 and state.player.block == 5
    assert len(_statuses(state, "status_dazed")) == 1
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_dodoco_tag+"), aim=enemy)
    assert enemy.hp == 190 and state.player.block == 7


def test_explosive_spark_costs_a_spark_for_twelve(overhaul):
    from tier0.engine import combat
    card = load("proto_ko_explosive_spark")
    assert combat.spark_cost(card) == 1
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.sparks = 1
    play(state, card, aim=enemy)
    assert enemy.hp == 188 and state.player.sparks == 0
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.sparks = 1
    play(state, load("proto_ko_explosive_spark+"), aim=enemy)
    assert enemy.hp == 184
