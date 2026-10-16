"""Yae, the dedupe and the refill (review/active/yae-dedupe-2026-10-16.md and
review/active/yae-refill-2026-10-16.md, ruled 2026-10-16: [USER], "Agreed on
the Yae paper picks!"). Sim half; the C# half is
`klee-mod/KleeTests/Prototype/YaeRefillTests.cs`.

Each new mechanic is pinned once: Falling Blossom's aimed Last Bloom, Hunting
Gaze, Inscribed Thunder's distinct Annotations, Publisher's Deadline's
discount, Sesshou Fang's threshold, Kitsune Barrage's hits, Hide Behind the
Shrine, Rewrite, Dawn Prayer, Kitsune's Blessing and Fox's Shade.
"""

from __future__ import annotations

import random
from collections import Counter

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy

CUT = ("kitsune_flick", "shrine_lantern", "grafted_branch", "shrine_bell",
       "shrine_offering", "deadline", "sacred_spark", "kitsune_flash",
       "print_run", "rooted_shrine", "omikuji")
NEW = {"kitsune_barrage": "common", "sesshou_fang": "common",
       "falling_blossom": "common", "publishers_deadline": "common",
       "foxs_shade": "common", "hide_behind_the_shrine": "common",
       "rewrite": "common", "dawn_prayer": "common",
       "hunting_gaze": "uncommon", "inscribed_thunder": "uncommon",
       "kitsunes_blessing": "uncommon"}


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _enemy(name="e0", hp=100):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=[{"kind": "block", "amount": 0}])


def _state(n_enemies=1, seed=0):
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(10)]
    st = CombatState(player=p,
                     enemies=[_enemy(f"e{i}") for i in range(n_enemies)],
                     rng=random.Random(seed))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card, target=None):
    if isinstance(card, str):
        card = _card(card)
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    if target is None:
        combat.play_card(st, card)
        return card
    # The player's pick: the sim's bound aim is the lowest-HP enemy, so the
    # test names the aim the way a mouse does (`effects.bind_card_aim`).
    orig = effects.bind_card_aim
    effects.bind_card_aim = lambda state, c: target
    try:
        combat.play_card(st, card)
    finally:
        effects.bind_card_aim = orig
    return card


def _led(st):
    return Y.ledger(st.player)


def _hp(st):
    return [e.hp for e in st.enemies]


def _strikes(st):
    return [r for r in st.log if r["event"] == "yae_sakura_strike"]


# --- the pool --------------------------------------------------------------------

def test_the_eleven_are_cut_and_the_eleven_added_pool_78():
    ids = {c.id for c in loader.prototype_cards()}
    for name in CUT:
        assert "proto_ym_" + name not in ids, name
    rows = [c for c in loader.prototype_cards()
            if c.id.startswith(Y.ID_PREFIX) and c.rarity != "basic"]
    assert Counter(c.rarity for c in rows) == {"common": 20, "uncommon": 38,
                                               "rare": 20}
    for name, rarity in NEW.items():
        assert _card(name).rarity == rarity, name


# --- Falling Blossom ----------------------------------------------------------------

def test_falling_blossom_aims_the_last_bloom_at_its_target():
    st = _state(n_enemies=3)
    Y.plant(st, 1)
    _play(st, "falling_blossom", target=st.enemies[2])
    assert not _led(st).sakura
    assert _strikes(st)[-1]["target"] == "e2"
    assert _hp(st) == [100, 100, 100 - 7 - (2 + 1)]


def test_falling_blossoms_foxfire_last_bloom_hits_only_the_target():
    st = _state(n_enemies=3)
    Y.plant(st, 1, kind=Y.FOXFIRE)
    _play(st, "falling_blossom", target=st.enemies[1])
    assert _hp(st) == [100, 100 - 7 - (1 + 1), 100]


def test_falling_blossom_with_no_sakura_only_hits():
    st = _state()
    _play(st, "falling_blossom+")
    assert _hp(st) == [100 - 10] and not _strikes(st)


# --- Hunting Gaze -------------------------------------------------------------------

def test_hunting_gaze_aims_random_strikes_at_the_last_enemy_attacked():
    st = _state(n_enemies=3, seed=4)
    _play(st, "hunting_gaze")
    Y.plant(st, 3)
    _play(st, loader.get_card("strike"), target=st.enemies[1])
    assert _led(st).last_attacked is st.enemies[1]
    Y.turn_end(st)
    assert {r["target"] for r in _strikes(st)} == {"e1"}


def test_hunting_gaze_falls_back_to_random_when_its_target_is_dead():
    st = _state(n_enemies=3, seed=1)
    _play(st, "hunting_gaze")
    Y.plant(st, 3)
    _play(st, loader.get_card("strike"), target=st.enemies[1])
    st.enemies[1].hp = 0
    Y.turn_end(st)
    targets = {r["target"] for r in _strikes(st)}
    assert targets and "e1" not in targets


def test_hunting_gaze_leaves_aimed_strikes_and_foxfire_all_hits_alone():
    st = _state(n_enemies=2)
    _play(st, "hunting_gaze")
    _play(st, loader.get_card("strike"), target=st.enemies[0])
    Y.plant(st, 1, kind=Y.FOXFIRE)
    Y.turn_end(st)                               # the Foxfire's act: ALL
    assert _strikes(st)[-1]["target"] == "ALL"
    st = _state(n_enemies=2)
    _play(st, "hunting_gaze")
    Y.plant(st, 1)
    _play(st, loader.get_card("strike"), target=st.enemies[0])
    Y.strike_target(st, st.enemies[1])           # an aimed strike stays aimed
    assert _strikes(st)[-1]["target"] == "e1"


def test_hunting_gaze_copies_do_not_stack_and_the_lure_comes_first():
    st = _state(n_enemies=2)
    _play(st, "hunting_gaze")
    _play(st, "hunting_gaze")
    assert st.player.powers[Y.HUNTING_GAZE] >= 1
    Y.plant(st, 2)
    _play(st, loader.get_card("strike"), target=st.enemies[0])
    _play(st, "foxfire_lure", target=st.enemies[1])
    Y.turn_end(st)
    assert {r["target"] for r in _strikes(st)} == {"e1"}


def test_a_sakuras_hit_is_not_her_attack():
    st = _state(n_enemies=2)
    _play(st, loader.get_card("strike"), target=st.enemies[0])
    Y.plant(st, 1)
    Y.strike_target(st, st.enemies[1])
    assert _led(st).last_attacked is st.enemies[0]


# --- Inscribed Thunder ----------------------------------------------------------------

def test_inscribed_thunder_counts_distinct_annotations_published_included():
    st = _state()
    t = _card("inscribed_thunder")
    Y.publish_to(t, [Y.FOOTNOTE, Y.FOOTNOTE])    # one distinct
    Y.annotate(st, t, Y.REPRINT)                 # a second
    assert Y.annotations_on_card(t) == 2
    st.player.draw_pile = []
    hp = st.enemies[0].hp
    _play(st, t)
    # 7 + 5 x 2 on its first hit; Reprint replays it once (and the stacked
    # Footnotes draw nothing from an empty pile).
    assert hp - st.enemies[0].hp == 2 * (7 + 5 * 2)


def test_inscribed_thunder_plain_and_upgraded():
    st = _state()
    _play(st, "inscribed_thunder")
    assert _hp(st) == [100 - 7]
    _play(st, "inscribed_thunder+")
    assert _hp(st) == [100 - 7 - 10]


# --- Publisher's Deadline --------------------------------------------------------------

def test_publishers_deadline_costs_1_less_after_an_edit_this_turn():
    st = _state()
    pd = _card("publishers_deadline")
    st.player.hand.append(pd)
    assert combat.card_cost(st, pd) == 2
    st.player.hand.append(loader.get_card("strike"))
    _play(st, "margin_note")                     # Edits a card: Red Ink
    assert _led(st).edits_this_turn == 1
    assert combat.card_cost(st, pd) == 1
    Y.turn_start(st)
    assert combat.card_cost(st, pd) == 2         # this turn only
    _play(st, pd)
    assert _hp(st) == [100 - 5 - 12]


# --- Sesshou Fang and Kitsune Barrage ----------------------------------------------------

def test_sesshou_fang_reads_a_level_3_sakura():
    st = _state()
    Y.plant(st, 1, level=2)
    _play(st, "sesshou_fang")
    assert _hp(st) == [100 - 6]
    Y.plant(st, 1, level=3, kind=Y.KITSUNE)      # any kind counts
    _play(st, "sesshou_fang")
    assert _hp(st) == [100 - 6 - 12]
    _play(st, "sesshou_fang+")
    assert _hp(st) == [100 - 6 - 12 - 16]


def test_kitsune_barrage_hits_twice_or_three_times_with_3_sakura():
    st = _state()
    Y.plant(st, 2)
    _play(st, "kitsune_barrage")
    assert _hp(st) == [100 - 8]
    Y.plant(st, 1)
    _play(st, "kitsune_barrage+")
    assert _hp(st) == [100 - 8 - 15]
    assert Y.barrage_hits(2) == 2 and Y.barrage_hits(5) == 3


# --- Hide Behind the Shrine --------------------------------------------------------------

def test_hide_behind_the_shrine_withers_the_newest_for_5_more():
    st = _state()
    Y.plant(st, 1)
    Y.plant(st, 1, kind=Y.KITSUNE)
    _play(st, "hide_behind_the_shrine")
    # 7, the Kitsune's Last Bloom (2 + 1 Block), then 5 more.
    assert st.player.block == 7 + 3 + 5
    assert [s.kind for s in _led(st).sakura] == [Y.THUNDER]


def test_hide_behind_the_shrine_with_no_sakura_is_7_block():
    st = _state()
    _play(st, "hide_behind_the_shrine")
    assert st.player.block == 7
    st.player.block = 0
    _play(st, "hide_behind_the_shrine+")
    assert st.player.block == 9


# --- Rewrite -------------------------------------------------------------------------------

def test_rewrite_discards_up_to_2_draws_as_many_then_edits_red_ink():
    st = _state()
    st.player.hand = [loader.get_card("strike"), loader.get_card("strike"),
                      loader.get_card("strike")]
    st.player.draw_pile = [loader.get_card("defend") for _ in range(5)]
    _play(st, "rewrite")
    assert len(st.player.discard_pile) >= 2
    assert sum(1 for c in st.player.hand if c.id == "defend") == 2
    assert len(st.player.hand) == 3
    assert sum(1 for c in st.player.hand if Y.temp(c) == Y.RED_INK) == 1
    assert _led(st).edits == 1


def test_rewrite_upgraded_is_up_to_3():
    st = _state()
    st.player.hand = [loader.get_card("strike") for _ in range(4)]
    st.player.draw_pile = [loader.get_card("defend") for _ in range(5)]
    _play(st, "rewrite+")
    assert sum(1 for c in st.player.hand if c.id == "defend") == 3


# --- Dawn Prayer and Kitsune's Blessing --------------------------------------------------

def test_dawn_prayer_levels_the_newest():
    st = _state()
    Y.plant(st, 2)
    _play(st, "dawn_prayer")
    assert [s.level for s in _led(st).sakura] == [1, 3]
    _play(st, "dawn_prayer+")
    assert [s.level for s in _led(st).sakura] == [1, 6]
    st = _state()
    _play(st, "dawn_prayer")                     # none standing: nothing
    assert not _led(st).sakura


def test_kitsunes_blessing_picks_the_highest_the_oldest_on_a_tie():
    st = _state()
    Y.plant(st, 1, level=2)
    Y.plant(st, 1, level=2, kind=Y.KITSUNE)
    Y.plant(st, 1)
    _play(st, "kitsunes_blessing")
    a, b, c = _led(st).sakura
    assert (a.level, a.turns_left) == (5, Y.SAKURA_TURNS + 2)   # the oldest
    assert (b.level, b.turns_left) == (2, Y.SAKURA_TURNS)
    assert c.level == 1
    _play(st, "kitsunes_blessing+")              # now a is highest alone
    assert _led(st).sakura[0].level == 9


# --- Fox's Shade -----------------------------------------------------------------------------

def test_foxs_shade_is_8_and_4_more_with_a_weak_enemy():
    st = _state(n_enemies=2)
    _play(st, "foxs_shade")
    assert st.player.block == 8
    st.enemies[1].powers["weak"] = 1
    st.player.block = 0
    _play(st, "foxs_shade")
    assert st.player.block == 12
    st.player.block = 0
    _play(st, "foxs_shade+")
    assert st.player.block == 15
