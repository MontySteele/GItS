"""Yae, the pool to 78 (review/active/yae-pool-to-78-2026-10-15.md, ruled
2026-10-15, all picks (a)). Sim half; the C# half is
`klee-mod/KleeTests/Prototype/YaePoolTo78Tests.cs`.

  * pick 2 (a): distinct Annotations coexist on a Sakura, a duplicate does
    nothing, a no-change Edit is not an Edit, Annotations survive refreshes
    and go when the Sakura withers or is replaced;
  * the Foxfire targeting rule: an aimed strike is one hit on the target;
  * the batch's new verbs and powers;
  * sec.3: the Grove / Mooncall swap (Grafted Branch was cut by the dedupe,
    2026-10-16).
"""

from __future__ import annotations

import random
from collections import Counter

import pytest

from tier0.content import loader
from tier0.engine import combat, powers
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


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


def _state(n_enemies=1):
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(10)]
    st = CombatState(player=p, enemies=[_enemy(f"e{i}") for i in range(n_enemies)],
                     rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card):
    if isinstance(card, str):
        card = _card(card)
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _led(st):
    return Y.ledger(st.player)


def _hp(st):
    return [e.hp for e in st.enemies]


# --- the pool ----------------------------------------------------------------

def test_the_pool_is_78_at_20_39_19():
    rows = [c for c in loader.prototype_cards()
            if c.id.startswith(Y.ID_PREFIX) and c.rarity != "basic"]
    assert len(rows) == 78
    assert Counter(c.rarity for c in rows) == {"common": 20, "uncommon": 39,
                                               "rare": 19}
    # The dedupe and the refill (2026-10-16): 4 Attacks and 7 Skills cut,
    # 5 Attacks, 5 Skills and a Power added.
    assert Counter(c.type for c in rows) == {"attack": 29, "skill": 34,
                                             "power": 15}


def test_grove_is_rare_and_mooncall_uncommon_at_1_upgrading_to_2_levels():
    assert _card("sakura_grove").rarity == "rare"
    m = _card("foxs_mooncall")
    assert m.rarity == "uncommon" and m.cost == 1
    up = loader.get_card("proto_ym_foxs_mooncall+")
    assert up.cost == 1
    st = _state()
    _play(st, up)
    Y.plant(st, 1)
    assert _led(st).sakura[0].level == 3


# --- pick 2 (a): Annotations coexist on a Sakura ------------------------------

def test_distinct_annotations_coexist_and_a_duplicate_does_nothing():
    st = _state()
    Y.plant(st, 1)
    s = _led(st).sakura[0]
    assert Y.edit_sakura(st, "fewest_turns_left", 1, Y.RED_INK) == 1
    assert Y.edit_sakura(st, "fewest_turns_left", 1, Y.FOX_FIRE) == 1
    assert Y.edit_sakura(st, "fewest_turns_left", 1, Y.DEADLINE) == 1
    assert s.annotations == [Y.RED_INK, Y.FOX_FIRE, Y.DEADLINE]
    size = Y.act_size(st, s)
    assert Y.edit_sakura(st, "fewest_turns_left", 1, Y.RED_INK) == 0
    assert Y.act_size(st, s) == size             # no second +3


def test_a_no_change_edit_pays_nothing():
    st = _state()
    st.player.powers[Y.SERIALIZATION] = 3
    Y.plant(st, 1)
    Y.edit_sakura(st, "fewest_turns_left", 1, Y.FOX_FIRE)
    edits, block = _led(st).edits, st.player.block
    assert Y.edit_sakura(st, "fewest_turns_left", 1, Y.FOX_FIRE) == 0
    assert _led(st).edits == edits and st.player.block == block


def test_annotations_survive_refreshes_and_go_with_the_sakura():
    st = _state()
    Y.plant(st, 3)
    Y.edit_sakura(st, "every", 3, Y.RED_INK)
    Y.edit_sakura(st, "fewest_turns_left", 1, Y.FOX_FIRE)
    oldest = _led(st).sakura[0]
    Y.tenko(st)                                  # Tenko refresh
    assert oldest.annotations == [Y.RED_INK, Y.FOX_FIRE]
    Y.plant(st, 1)                               # same kind: refresh
    assert oldest.annotations == [Y.RED_INK, Y.FOX_FIRE]
    Y.plant(st, 1, kind=Y.KITSUNE)               # another kind: replaced
    assert oldest not in _led(st).sakura
    assert _led(st).sakura[-1].annotations == []


# --- the Foxfire targeting rule -------------------------------------------------

def test_an_aimed_foxfire_strike_hits_the_target_once():
    st = _state(2)
    Y.plant(st, 1, kind=Y.FOXFIRE)
    s = _led(st).sakura[0]
    Y.act(st, s, "test", aim=st.enemies[1])
    assert _hp(st) == [100, 100 - Y.act_size(st, s)]
    Y.act(st, s, "test")                         # its own act: ALL
    assert _hp(st)[0] == 100 - Y.act_size(st, s)


def test_foxs_verdict_one_hit_per_weak_enemy_per_striking_sakura():
    st = _state(2)
    Y.plant(st, 1, kind=Y.FOXFIRE)
    Y.plant(st, 1)
    Y.plant(st, 1, kind=Y.KITSUNE)
    st.enemies[0].powers["weak"] = 1
    _play(st, "foxs_verdict")
    fox, thunder = _led(st).sakura[0], _led(st).sakura[1]
    assert _hp(st) == [100 - Y.act_size(st, fox) - Y.act_size(st, thunder),
                       100]


def test_a_sakura_strikes_it_and_narukami_judgment():
    # "A Sakura strikes it" (Saiguu's Lesson, Kitsune Pounce; Sacred Spark's
    # until the dedupe cut it, 2026-10-16): the highest; on a tie the most
    # turns left, the newest on an equal timer (the user's ruling, 2026-10-20;
    # was the oldest).
    st = _state()
    Y.plant(st, 1)
    Y.plant(st, 1, kind=Y.FOXFIRE)
    Y.level_up(st, 1)
    Y.strike_target(st, st.enemies[0])
    foxfire = _led(st).sakura[1]
    assert _hp(st) == [100 - Y.act_size(st, foxfire)]  # highest, newest
    st = _state()
    Y.plant(st, 1, lasts=1)                       # the Thunder lasts longer
    Y.plant(st, 1, kind=Y.FOXFIRE)
    Y.strike_target(st, st.enemies[0])
    thunder = _led(st).sakura[0]
    assert _hp(st) == [100 - Y.act_size(st, thunder)]  # highest, most turns
    st = _state()
    Y.plant(st, 1)
    Y.plant(st, 1, kind=Y.FOXFIRE)
    Y.plant(st, 1, kind=Y.KITSUNE)
    _play(st, "narukami_judgment")
    a, b = _led(st).sakura[0], _led(st).sakura[1]
    assert _hp(st) == [100 - 6 - Y.act_size(st, a) - Y.act_size(st, b)]
    assert st.player.block == 0                  # the Kitsune does not act


# --- the batch's verbs ----------------------------------------------------------

def test_genre_shift_plants_the_missing_kinds():
    st = _state()
    Y.plant(st, 1, kind=Y.KITSUNE)
    _play(st, "genre_shift")
    assert [s.kind for s in _led(st).sakura] == [Y.KITSUNE, Y.THUNDER,
                                                 Y.FOXFIRE]


def test_narukami_bloom_fills_the_shrine():
    st = _state()
    Y.plant(st, 1)
    _play(st, "narukami_bloom")
    assert len(_led(st).sakura) == Y.SAKURA_CAP


def test_replanting_withers_the_oldest_and_plants_its_kind_higher():
    st = _state()
    Y.plant(st, 1, kind=Y.KITSUNE)
    Y.level_up(st, 2)                            # Level 3
    Y.plant(st, 1)
    _play(st, "replanting")
    assert [(s.kind, s.level) for s in _led(st).sakura] == [
        (Y.THUNDER, 1), (Y.KITSUNE, 4)]
    _play(st, loader.get_card("proto_ym_replanting+"))
    assert [(s.kind, s.level) for s in _led(st).sakura] == [
        (Y.KITSUNE, 4), (Y.THUNDER, 3)]


def test_daisesshou_withers_all_and_hits_all_per_level():
    # The pool sweep (2026-10-18, review/active/pool-sweep-2026-10-18.md
    # sec.1): 3 [4] to ALL per Level the withered Sakura had, read before
    # they wither. Kitsune Sakura (their bloom is Block) at Levels 1, 2, 3.
    st = _state(2)
    Y.plant(st, 1, kind=Y.KITSUNE, level=1)
    Y.plant(st, 1, kind=Y.KITSUNE, level=2)
    Y.plant(st, 1, kind=Y.KITSUNE, level=3)
    assert [s.level for s in _led(st).sakura] == [1, 2, 3]
    _play(st, "forbidden_art_daisesshou")
    assert not _led(st).sakura
    assert _hp(st) == [100 - 18, 100 - 18]
    st = _state(2)
    Y.plant(st, 1, kind=Y.KITSUNE, level=1)
    Y.plant(st, 1, kind=Y.KITSUNE, level=2)
    Y.plant(st, 1, kind=Y.KITSUNE, level=3)
    _play(st, loader.get_card("proto_ym_forbidden_art_daisesshou+"))
    assert _hp(st) == [100 - 24, 100 - 24]


def test_daisesshou_on_an_empty_shrine_does_not_hit():
    st = _state(2)
    _play(st, "forbidden_art_daisesshou")
    assert _hp(st) == [100, 100]


def test_kitsune_shelter_and_veil():
    st = _state()
    Y.plant(st, 1, kind=Y.KITSUNE)
    Y.plant(st, 1)
    _play(st, "kitsune_veil")
    assert [s.level for s in _led(st).sakura] == [3, 1]
    st.player.block = 0
    _play(st, "kitsunes_shelter")
    assert st.player.block == Y.KITSUNE_BASE + 3


def test_offertory_box_and_torii_ward_and_late_night_reading():
    st = _state()
    Y.plant(st, 2)
    st.player.energy = 0
    c = _card("offertory_box")
    st.player.hand.append(c)
    combat.play_card(st, c)
    assert st.player.energy == 2
    hand = len(st.player.hand)
    _play(st, "torii_ward")                      # 2 of 3: no draw
    assert len(st.player.hand) == hand
    Y.plant(st, 1)
    _play(st, "torii_ward")
    assert len(st.player.hand) == hand + 2
    hand = len(st.player.hand)
    _play(st, "late_night_reading")              # 3 Sakura: 2 + 1
    assert len(st.player.hand) == hand + 3


@pytest.mark.parametrize("annotated, drawn", [(0, 0), (1, 1), (2, 2), (4, 2)])
def test_hold_the_presses_draws_per_annotated_card_up_to_two(annotated,
                                                             drawn):
    """Redesigned 2026-10-19: "Gain 8 Block. Draw 1 card for each Annotated
    card in your Hand, up to 2." The hand at resolution; an Annotated Hold
    the Presses does not count itself."""
    st = _state()
    marked = [loader.get_card("strike") for _ in range(annotated)]
    for c in marked:
        Y.annotate(st, c, Y.RED_INK)
    st.player.hand = [*marked, loader.get_card("defend")]
    htp = _card("hold_the_presses")
    Y.annotate(st, htp, Y.ROYALTIES)
    before = len(st.player.hand)
    _play(st, htp)
    assert len(st.player.hand) == before + drawn
    assert st.player.block == 8
    assert htp.cost == 1


def test_hold_the_presses_retains_nothing_now():
    from tier0.engine import refpowers
    st = _state()
    _play(st, "hold_the_presses")
    cards = [loader.get_card("strike")]
    assert refpowers.retain_at_flush(st, cards) == []


def test_afterword_returns_every_annotated_card():
    st = _state()
    a, b, c = (loader.get_card("strike") for _ in range(3))
    Y.annotate(st, a, Y.RED_INK)
    Y.annotate(st, b, Y.FOOTNOTE)
    st.player.discard_pile = [a, b, c]
    _play(st, "afterword")
    assert a in st.player.hand and b in st.player.hand
    assert st.player.discard_pile == [c]


# --- the powers -----------------------------------------------------------------

def test_enlightened_blessing_draws_per_wither():
    st = _state()
    st.player.powers[Y.ENLIGHTENED_BLESSING] = 1
    Y.plant(st, 2)
    hand = len(st.player.hand)
    Y.wither_next(st)
    assert len(st.player.hand) == hand + 1


def test_saiguus_lesson_strikes_an_enemy_she_makes_weak():
    st = _state()
    st.player.powers[Y.SAIGUUS_LESSON] = 1
    Y.plant(st, 1)
    powers.apply_power(st, st.enemies[0], "weak", 1)
    assert _hp(st) == [100 - Y.act_size(st, _led(st).sakura[0])]


def test_sacred_shade_gives_block_per_sakura_at_turn_end():
    st = _state()
    st.player.powers[Y.SACRED_SHADE] = 2
    Y.plant(st, 2, kind=Y.FOXFIRE)
    Y.turn_end(st)
    assert st.player.block == 4


def test_editorial_priority_frees_the_first_annotated_card_a_turn():
    st = _state()
    st.player.powers[Y.EDITORIAL_PRIORITY] = 1
    a, b = loader.get_card("strike"), loader.get_card("strike")
    Y.annotate(st, a, Y.RED_INK)
    Y.annotate(st, b, Y.RED_INK)
    st.player.hand += [a, b]
    assert combat.card_cost(st, a) == 0
    combat.play_card(st, a)
    assert combat.card_cost(st, b) == 1
    Y.turn_start(st)
    assert combat.card_cost(st, b) == 0


def test_eternity_stops_the_timers():
    st = _state()
    st.player.powers[Y.ETERNITY] = 1
    Y.plant(st, 1)
    for _ in range(5):
        Y.turn_end(st)
    assert len(_led(st).sakura) == 1


# --- the pool sweep (2026-10-18): Eternity, "Their Levels count twice" -------

def test_eternity_doubles_the_levels_effects_read_not_the_stored_level():
    st = _state(2)
    Y.plant(st, 1, level=2)
    s = _led(st).sakura[0]
    assert Y.act_size(st, s) == 1 + 2 * 2
    st.player.powers[Y.ETERNITY] = 1
    assert Y.effective_level(st, s) == 4
    assert Y.act_size(st, s) == 1 + 2 * 4          # 9, not 5
    assert s.level == 2                             # the stored Level


def test_eternity_doubles_daisesshou_and_counts_for_sesshou_fang():
    st = _state(2)
    st.player.powers[Y.ETERNITY] = 1
    Y.plant(st, 1, kind=Y.KITSUNE, level=1)
    Y.plant(st, 1, kind=Y.KITSUNE, level=2)
    _play(st, "forbidden_art_daisesshou")
    assert _hp(st) == [100 - 3 * 6, 100 - 3 * 6]    # (1 + 2) x 2 Levels
    st = _state()
    Y.plant(st, 1, kind=Y.KITSUNE, level=2)
    _play(st, "sesshou_fang")
    plain = 100 - st.enemies[0].hp
    st = _state()
    st.player.powers[Y.ETERNITY] = 1
    Y.plant(st, 1, kind=Y.KITSUNE, level=2)
    _play(st, "sesshou_fang")
    assert 100 - st.enemies[0].hp == plain + 6      # Level 2 reads as 4 >= 3
