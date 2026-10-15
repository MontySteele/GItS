"""YAE MIKO, the card stage's sim twin (`tier0/engine/yae_shrine.py`) --
the engine's pins.

Design: `review/active/yae-card-paper-2026-10-13.md` (sec.2 readings);
rows: `docs/prototype-surface.yaml` (`proto_ym_`), built in both engines
since 2026-10-13 (C#: `Powers/Prototype/YaeShrine.cs`). No
switch: every hook is dead for anyone who is not Yae.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
        loader.reset_arm_caches()


def _enemy(hp=100, name="e", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left = aura, 2
    return e


def _state(n=1, extra=(), published=None, **kw):
    enemies = kw.pop("enemies", None) or [_enemy(name=f"e{i}")
                                          for i in range(n)]
    p = Y.build_player(extra=tuple(extra), published=published)
    p.draw_pile = []
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _led(st):
    return Y.ledger(st.player)


def _play(st, card):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _ym(name):
    return "proto_ym_" + name


def _red_ink_edit():
    """A bare "Edit a card in your hand: Red Ink" (Proofread's face until
    2026-10-14, when it became Reprint): the Red Ink Edit with nothing else
    on the card, so a test reads Red Ink alone."""
    card = loader.get_card(_ym("proofread"))
    card.effects = [{"op": "yae", "kind": "edit", "annotation": Y.RED_INK,
                     "amount": 1}]
    return card


def _strikes(st):
    return [r for r in st.log if r["event"] == "yae_sakura_strike"]


# ---------------------------------------------------------------------------
# 0. The sheet and the seams
# ---------------------------------------------------------------------------

def test_her_surface_rows_load_with_the_paper_counts(yae):
    by = {}
    for c in loader.prototype_cards():
        if not c.id.startswith(Y.ID_PREFIX):
            continue
        assert c.character == Y.CHARACTER
        by[c.rarity] = by.get(c.rarity, 0) + 1
    assert by == {"basic": 2, "common": 15, "uncommon": 16, "rare": 9}


def test_her_rows_resolve_through_get_card_and_the_staging_sheet_is_gone(yae):
    c = loader.get_card(_ym("twin_sakura"))
    assert c.name == "Twin Sakura"
    assert loader.STAGING_SHEETS == ()


def test_her_starter_is_the_base_eight_and_two_of_her_own(yae):
    ids = Y.starter_ids()
    assert ids.count("strike") == 4 and ids.count("defend") == 4
    assert ids[8:] == [_ym("yakan_evocation"), _ym("proofread")]
    p = Y.build_player()
    assert p.character_id == "yae" and p.max_hp == Y.HP
    assert Y.MEDITATIONS in p.relic_hooks


def test_the_yae_op_is_dead_for_anyone_else(yae):
    from tier0.tests.conftest import make_state
    st = make_state()
    with pytest.raises(NotImplementedError):
        effects.OPS["yae"](st, {"op": "yae", "kind": "plant", "amount": 1},
                           loader.get_card("strike"))
    Y.turn_end(st)                       # no-op, no raise
    assert not getattr(st.player, "yae_ledger", None)


def test_validate_op_refuses_a_wrong_shape(yae):
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "plant"})
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "edit", "amount": 1})
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "edit", "amount": 1,
                            "annotation": "blue_ink"})
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "lure"})
    Y.validate_op("x", {"op": "yae", "kind": "lure", "target": "enemy"})


# ---------------------------------------------------------------------------
# 1. The shrine
# ---------------------------------------------------------------------------

def test_a_plant_strikes_at_the_end_of_the_turn_for_base_plus_level(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [1]
    Y.turn_end(st)
    hits = _strikes(st)
    assert len(hits) == 1 and hits[0]["amount"] == Y.SAKURA_BASE + 1
    assert st.enemies[0].hp == 100 - 3
    assert st.enemies[0].aura == "electro"


def test_a_plant_does_not_level_the_others_and_a_full_shrine_feeds_the_oldest(yae):
    # Shrine r2 (ruled 2026-10-14): each plant at its own Level; with 3
    # standing the OLDEST refreshes and gains a Level, no cap.
    st = _state()
    for _ in range(3):
        _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [1, 1, 1]
    _led(st).sakura[0].turns_left = 1
    oldest = _led(st).sakura[0]
    _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [2, 1, 1]
    assert _led(st).sakura[0] is oldest
    assert oldest.turns_left == Y.SAKURA_TURNS
    _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [3, 1, 1]
    # 2026-10-14: each full-shrine plant struck the oldest first, at 1 then 2.
    assert [r["amount"] for r in _strikes(st)] == [3, 4]
    Y.turn_end(st)
    assert sum(r["amount"] for r in _strikes(st)
               if r["reason"] != "full_shrine") == 5 + 3 + 3


def test_twin_sakura_with_two_standing_plants_one_then_feeds_the_oldest(yae):
    st = _state()
    _play(st, _ym("twin_sakura"))
    assert [s.level for s in _led(st).sakura] == [1, 1]
    first = _led(st).sakura[0]
    first.turns_left = 1
    _play(st, _ym("twin_sakura"))
    assert len(_led(st).sakura) == 3
    assert [s.level for s in _led(st).sakura] == [2, 1, 1]
    assert first.turns_left == Y.SAKURA_TURNS


def test_a_sakura_withers_after_three_strikes_and_tenko_refreshes(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    for _ in range(3):
        Y.turn_end(st)
    assert _led(st).sakura == []
    assert len(_strikes(st)) == 3 + 1                # and its Last Bloom
    assert _strikes(st)[-1]["reason"] == "bloom"
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)
    Y.turn_end(st)
    assert _led(st).sakura[0].turns_left == 1
    _play(st, _ym("kitsune_rite"))               # Tenko: strike now, reset
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS
    assert _strikes(st)[-1]["reason"] == "tenko"


def test_tenko_with_no_sakura_does_nothing_and_thunder_rite_still_hits(yae):
    st = _state()
    _play(st, _ym("thunder_rite"))
    assert st.enemies[0].hp == 92 and not _strikes(st)


def test_shrine_offering_extends_and_rooted_shrine_levels(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("shrine_offering"))
    assert _led(st).sakura[0].turns_left == 4 and st.player.block == 6
    _play(st, _ym("rooted_shrine"))              # 6 Block, then the Level
    assert _led(st).sakura[0].level == 2 and st.player.block == 12


def test_the_lure_aims_every_strike_this_turn_and_expires(yae):
    st = _state(n=3)
    _play(st, _ym("twin_sakura"))
    _play(st, _ym("foxfire_lure"))
    assert _led(st).lure is st.enemies[0]
    Y.turn_end(st)
    assert {r["target"] for r in _strikes(st)} == {"e0"}
    Y.turn_start(st)
    assert _led(st).lure is None


def test_sakura_readers_count_the_standing(yae):
    st = _state()
    _play(st, _ym("twin_sakura"))
    _play(st, _ym("thunderbolt_tithe"))          # 3 + 4 x 2
    assert st.enemies[0].hp == 100 - 11
    _play(st, _ym("shrine_maidens_guard"))       # 6, then Tenko (Warding)
    assert st.player.block == 6 + 3 + 3


def test_mooncall_plants_one_higher_and_levels_have_no_cap(yae):
    st = _state()
    _play(st, _ym("foxs_mooncall"))
    for _ in range(5):
        _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [4, 2, 2]


def _hits(st):
    return [r for r in st.log if r["event"] == "yae_sakura_hit"]


def test_the_powers_pay_on_a_strike(yae):
    st = _state(enemies=[_enemy(name="e0", aura="hydro")])
    _play(st, _ym("edict_of_cleansing"))         # +3 on a reacting aura
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)
    assert _strikes(st)[0]["amount"] == 3
    assert _hits(st)[0]["amount"] == 3 + 3
    assert st.enemies[0].aura is None            # the reaction consumed it


def test_edict_pays_on_a_weak_enemy_solo(yae):
    st = _state()
    _play(st, _ym("edict_of_cleansing"))
    _play(st, _ym("yakan_evocation"))
    st.enemies[0].powers["weak"] = 1
    Y.turn_end(st)
    assert _hits(st)[0]["amount"] == 3 + 3


# ---------------------------------------------------------------------------
# The design axes (ruled 2026-10-14): Rites, Sakura Annotations, batch two
# ---------------------------------------------------------------------------

def test_the_shrine_has_no_rite_any_more(yae):
    # Shrine r2: the persistent Rite is gone; "Rite: X" became Tenko (X).
    st = _state()
    assert not hasattr(_led(st), "rite")
    assert not hasattr(Y, "RITES") and not hasattr(Y, "set_rite")


def test_thunder_strikes_one_enemy_for_two_plus_level(yae):
    st = _state(n=2)
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)
    hits = _hits(st)
    assert len(hits) == 1 and hits[0]["amount"] == 3 and hits[0]["rite"] == Y.THUNDER
    assert sum(e.hp for e in st.enemies) == 200 - 3


def test_tenko_warding_strikes_and_gives_two_plus_level_block(yae):
    # [USER], 2026-10-14: "Hmm, the double strike makes Tenko effects quite
    # strong, but let's try it and see what happens": a typed Tenko's
    # Sakura strike as Thunder AND add the kind.
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("grafted_branch"))             # levels 1 / 2
    _led(st).sakura[0].turns_left = 1
    _play(st, _ym("shrine_maidens_guard"))       # 6 Block, Tenko (Warding)
    assert st.player.block == 6 + (2 + 1) + (2 + 2)
    assert st.enemies[0].hp == 100 - (2 + 1) - (2 + 2)
    assert len(_hits(st)) == 2
    # Tenko still resets every timer ([USER], 2026-10-14).
    assert [s.turns_left for s in _led(st).sakura] == [Y.SAKURA_TURNS] * 2
    st.player.block = 0
    Y.turn_end(st)                               # the turn end is Thunder
    assert st.player.block == 0 and len(_hits(st)) == 2 + 2


def test_tenko_warding_reads_red_ink_and_fox_fire(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("inked_branches"))             # Red Ink: +3
    _play(st, _ym("shrine_maidens_guard"))
    assert st.player.block == 6 + (2 + 1 + 3)
    _play(st, _ym("fox_fire_draft"))             # Fox Fire replaces it
    st.player.block = 0
    hp = st.enemies[0].hp
    Y.tenko(st, Y.WARDING)
    assert st.player.block == 3
    assert hp - st.enemies[0].hp == 3 + Y.FOX_FIRE_DAMAGE   # Fox Fire once


def test_tenko_wildfire_strikes_all_for_level_and_red_ink(yae):
    st = _state(n=3)
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("grafted_branch"))             # levels 1 / 2
    hp = [e.hp for e in st.enemies]
    _play(st, _ym("kitsune_guile"))              # Tenko (Wildfire)
    lost = [h - e.hp for h, e in zip(hp, st.enemies)]
    # Each strike: Thunder (2 + Level) at one enemy, then Level to ALL.
    assert sum(lost) == (3 + 4) + 3 * 3 and min(lost) >= 3
    assert len(_strikes(st)) == 2 and len(_hits(st)) == 2 + 6
    assert {r["rite"] for r in _strikes(st)} == {Y.WILDFIRE}
    _play(st, _ym("inked_branches"))
    hp = [e.hp for e in st.enemies]
    Y.tenko(st, Y.WILDFIRE)
    lost = [h - e.hp for h, e in zip(hp, st.enemies)]
    assert sum(lost) == (6 + 7) + 3 * 9 and min(lost) >= 9


def test_tenko_offering_draws_one_a_sakura_at_the_next_turn_start(yae):
    st = _state()
    _play(st, _ym("twin_sakura"))
    _play(st, _ym("inked_branches"))             # Red Ink skips Offering
    st.player.draw_pile = [loader.get_card("defend") for _ in range(9)]
    _play(st, _ym("manuscript_pile"))            # draw 2, Tenko (Offering)
    assert _led(st).pending_draw == 2 and len(_hits(st)) == 2
    st.player.hand = []
    Y.turn_start(st)
    assert len(st.player.hand) == 2 and _led(st).pending_draw == 0


def test_a_typed_tenko_holds_nothing_the_turn_end_stays_thunder(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("foxfire_sweep"))              # Tenko (Wildfire), now
    assert _strikes(st)[-1]["rite"] == Y.WILDFIRE
    Y.turn_end(st)
    assert _strikes(st)[-1]["rite"] == Y.THUNDER
    _play(st, _ym("thunder_rite"))               # plain Tenko: Thunder
    assert _strikes(st)[-1]["rite"] == Y.THUNDER




def test_channeling_lets_you_have_2_more_sakura_per_copy(yae):
    # Designed 2026-10-14: "You can have 2 more Sakura."
    st = _state()
    assert Y.sakura_cap(st.player) == 3
    _play(st, _ym("sakura_channeling"))
    assert Y.sakura_cap(st.player) == 5
    _play(st, _ym("sakura_channeling"))
    assert Y.sakura_cap(st.player) == 7
    Y.plant(st, 7)
    assert [s.level for s in _led(st).sakura] == [1] * 7
    Y.turn_end(st)
    assert len(_hits(st)) == 7


def test_the_full_shrine_rule_fires_at_channelings_cap(yae):
    st = _state()
    _play(st, _ym("sakura_channeling"))
    Y.plant(st, 5)
    assert len(_led(st).sakura) == 5
    _led(st).sakura[0].turns_left = 1
    Y.plant(st, 1)                               # full: the oldest feeds
    assert len(_led(st).sakura) == 5
    assert [s.level for s in _led(st).sakura] == [2, 1, 1, 1, 1]
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS


def test_without_channeling_the_shrine_still_holds_3(yae):
    st = _state()
    Y.plant(st, 4)
    assert [s.level for s in _led(st).sakura] == [2, 1, 1]


def test_sakura_annotations_each_reading(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("inked_branches"))             # Red Ink on every Sakura
    s = _led(st).sakura[0]
    assert s.annotation == Y.RED_INK
    assert Y.strike_size(st, s, Y.THUNDER) == 3 + 3
    assert Y.strike_size(st, s, Y.WARDING) == 3 + 3
    assert Y.strike_size(st, s, Y.WILDFIRE) == 1 + 3
    assert Y.strike_size(st, s, Y.OFFERING) == 1       # not in Offering
    _play(st, _ym("fox_fire_draft"))             # Fox Fire on the newest
    assert s.annotation == Y.FOX_FIRE            # replaces the Red Ink
    hp = st.enemies[0].hp
    Y.turn_end(st)
    assert hp - st.enemies[0].hp == 3 + Y.FOX_FIRE_DAMAGE
    assert any(r["event"] == "yae_fox_fire" for r in st.log)


def test_an_unannotated_sakura_does_only_the_rite(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    assert _led(st).sakura[0].annotation is None
    Y.turn_end(st)
    assert not any(r["event"] == "yae_fox_fire" for r in st.log)


def test_newest_oldest_and_every(yae):
    st = _state()
    for _ in range(3):
        _play(st, _ym("yakan_evocation"))
    _play(st, _ym("fox_fire_draft"))
    assert [s.annotation for s in _led(st).sakura] == [None, None, Y.FOX_FIRE]
    _play(st, _ym("evergreen_charm"))
    assert [s.annotation for s in _led(st).sakura] == [Y.DEADLINE, None, Y.FOX_FIRE]
    up = loader.get_card(_ym("fox_fire_draft") + "+")
    _play(st, up)                                # upgraded: every Sakura
    assert [s.annotation for s in _led(st).sakura] == [Y.FOX_FIRE] * 3


def test_deadline_extension_never_withers(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("evergreen_charm"))
    assert st.player.block == 5
    for _ in range(6):
        Y.turn_end(st)
        Y.turn_start(st)
    assert len(_led(st).sakura) == 1
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS


def test_a_sakura_edit_needs_a_sakura_reading(yae):
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "edit_sakura", "which": "newest",
                            "annotation": "footnote", "amount": 1})
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "tenko", "as": "storm"})
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "plant", "amount": 1,
                            "as": "warding"})
    with pytest.raises(ValueError):
        Y.validate_op("x", {"op": "yae", "kind": "tenko", "as": "thunder"})


def test_fallen_petals_pays_energy_next_turn_and_its_upgrade_draws(yae):
    st = _state()
    _play(st, _ym("fallen_petals"))
    _play(st, loader.get_card(_ym("fallen_petals") + "+"))
    _play(st, _ym("yakan_evocation"))
    for _ in range(2):
        Y.turn_end(st)
        Y.turn_start(st)
    st.player.energy = 0
    st.player.hand = []
    st.player.draw_pile = [loader.get_card("defend") for _ in range(3)]
    Y.turn_end(st)                               # the third strike: withers
    assert not _led(st).sakura and _led(st).pending_withers == 1
    Y.turn_start(st)
    assert st.player.energy == 2                 # 1 + 1 (both powers)
    assert len(st.player.hand) == 1              # the upgrade's card


def test_grafted_branch_plants_at_its_level(yae):
    st = _state()
    _play(st, _ym("grafted_branch"))
    assert [s.level for s in _led(st).sakura] == [2]
    _play(st, loader.get_card(_ym("grafted_branch") + "+"))
    assert [s.level for s in _led(st).sakura] == [2, 3]     # no levelling


def test_kitsune_pounce_strikes_a_weak_enemy(yae):
    st = _state(n=2)
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("kitsune_pounce"))             # e0 not Weak: no strike
    assert not _strikes(st)
    st.enemies[0].powers["weak"] = 1
    _play(st, _ym("kitsune_pounce"))
    assert _strikes(st)[-1]["reason"] == "pounce"
    assert _strikes(st)[-1]["target"] == "e0"


def test_proofread_edits_reprint_and_the_first_play_each_combat_is_twice(yae):
    """[USER] 2026-10-14: "Let's bump it to 'Play it twice.'" Proofread
    Edits Reprint; the card's first play this combat resolves twice (Glam's
    rule), every later play once."""
    st = _state()
    strike = loader.get_card("strike")
    st.player.hand.append(strike)
    _play(st, _ym("proofread"))
    assert strike.ym_annotation == Y.REPRINT
    assert st.player.block == 0
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 6 - 6
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 6 - 6 - 6
    assert [r["card"] for r in st.log
            if r["event"] == "yae_reprint"] == ["strike"]


def test_a_fresh_reprint_edit_plays_twice_again(yae):
    st = _state()
    strike = loader.get_card("strike")
    st.player.hand.append(strike)
    Y.annotate(st, strike, Y.REPRINT)
    _play(st, strike)
    Y.annotate(st, strike, Y.REPRINT)            # a new Edit, a new Reprint
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 4 * 6


def test_a_published_reprint_plays_twice_once_every_combat(yae):
    c = Y.build_player(published={0: Y.REPRINT}).draw_pile[0]
    assert c.ym_annotation == Y.REPRINT and c.ym_published
    for _ in range(2):                           # two fights, the same card
        st = _state()
        _play(st, c)
        _play(st, c)
        assert st.enemies[0].hp == 100 - 3 * 6


def test_reprint_reaches_any_playable_card_never_junk(yae):
    lure = loader.get_card(_ym("foxfire_lure"))
    assert Y.affects(lure, Y.REPRINT)
    from tier0.engine import statuses
    assert not Y.affects(statuses.make_status("dazed"), Y.REPRINT)


def test_royalties_annotation_gains_energy(yae):
    st = _state()
    a = loader.get_card("strike")
    st.player.hand.append(a)
    _play(st, _ym("royalties"))
    assert a.ym_annotation == Y.ROYALTIES
    st.player.energy = 5
    combat.play_card(st, a)
    assert st.player.energy == 5 - 1 + 1


def test_yakan_offering_plants_at_the_start_of_the_turn(yae):
    st = _state()
    _play(st, _ym("yakan_offering"))
    Y.turn_start(st)
    assert len(_led(st).sakura) == 1


def test_count_scaling_is_the_proposals_table_and_tenko_raises_it(yae):
    Y.SCALING = "count"
    st = _state()
    for _ in range(4):
        _play(st, _ym("yakan_evocation"))
    assert len(_led(st).sakura) == 3             # the oldest went
    Y.turn_end(st)
    assert [r["amount"] for r in _strikes(st)] == [5, 5, 5]
    _play(st, _ym("kitsune_rite"))               # the Tenko strikes at 5,
    assert _strikes(st)[-1]["amount"] == 5       # then the bonus rises
    Y.turn_end(st)
    assert _strikes(st)[-1]["amount"] == 5 + Y.COUNT_TENKO_BONUS


# ---------------------------------------------------------------------------
# 2. The publishing house
# ---------------------------------------------------------------------------

def test_red_ink_rides_the_edited_cards_hits_and_block(yae):
    st = _state()
    strike = loader.get_card("strike")
    st.player.hand.append(strike)
    _play(st, _red_ink_edit())
    assert strike.ym_annotation == Y.RED_INK and Y.is_annotated(strike)
    assert st.player.block == 0                  # Proofread gives no Block (pick 3)
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 6 - 3
    defend = loader.get_card("defend")
    st.player.hand.append(defend)
    _play(st, _red_ink_edit())
    _play(st, defend)
    assert st.player.block == 5 + 3


def test_an_edit_never_targets_itself_a_status_or_an_annotated_card_first(yae):
    st = _state()
    a, b = loader.get_card("strike"), loader.get_card("strike")
    st.player.hand += [a, b]
    _play(st, _red_ink_edit())
    _play(st, _red_ink_edit())
    assert Y.is_annotated(a) and Y.is_annotated(b)
    assert _led(st).edits == 2


def test_an_edit_overwrites_and_deadline_retains(yae):
    st = _state()
    c = loader.get_card("strike")
    st.player.hand.append(c)
    _play(st, _red_ink_edit())
    _play(st, _ym("deadline"))
    assert c.ym_annotation == Y.DEADLINE and c.retain
    assert c.enchant_damage == 0
    _play(st, _red_ink_edit())
    assert c.ym_annotation == Y.RED_INK and not c.retain


def test_footnote_fox_fire_and_sakura_seal_fire_after_the_cards_own_effects(yae):
    st = _state(n=2)
    st.player.draw_pile = [loader.get_card("defend")]
    a = loader.get_card("strike")
    st.player.hand.append(a)
    _play(st, _ym("footnote"))
    _play(st, a)
    assert any(c.id == "defend" for c in st.player.hand)
    st.player.hand = [c for c in st.player.hand if c.id != "defend"]
    b = loader.get_card("strike")
    st.player.hand.append(b)
    Y.annotate(st, b, Y.FOX_FIRE)                # (Fox Fire Draft edits Sakura now)
    hp_before = sum(e.hp for e in st.enemies)
    _play(st, b)
    assert sum(e.hp for e in st.enemies) == hp_before - 6 - Y.FOX_FIRE_DAMAGE
    assert any(r["event"] == "yae_fox_fire" for r in st.log)
    c = loader.get_card("strike")
    st.player.hand.append(c)
    _play(st, _ym("sakura_seal"))
    _play(st, c)
    assert len(_led(st).sakura) == 1


def test_annotated_readers_count_the_hand_and_the_card_itself(yae):
    st = _state()
    a = loader.get_card("strike")
    st.player.hand.append(a)
    _play(st, _red_ink_edit())
    _play(st, _ym("bestseller"))                 # 5 + 3 x 1
    assert st.enemies[0].hp == 100 - 8
    _play(st, _ym("print_run"))                  # 6 + 2 x 1
    assert st.player.block == 8
    flash = loader.get_card(_ym("kitsune_flash"))
    st.player.hand.append(flash)
    _play(st, _red_ink_edit())                  # Red Ink on the Flash
    assert flash.ym_annotation == Y.RED_INK
    _play(st, flash)                             # 6 + 3 (annotated) + 3 ink
    assert st.enemies[0].hp == 100 - 8 - 12


def test_serialization_pays_block_per_annotated_play_not_per_edit(yae):
    # Shrine r2, (b) (ruled 2026-10-14).
    st = _state()
    _play(st, _ym("serialization"))
    st.player.hand += [loader.get_card("strike"), loader.get_card("defend")]
    _play(st, _ym("reborn_as_guuji_yae"))
    assert st.player.block == 0                  # Editing pays nothing now
    assert all(c.ym_annotation == Y.SAKURA_SEAL for c in st.player.hand)
    strike = st.player.hand[0]
    combat.play_card(st, strike)
    assert st.player.block == 3                  # an Annotated play pays
    plain = loader.get_card("strike")
    _play(st, plain)
    assert st.player.block == 3


def test_editor_in_chief_strikes_on_an_annotated_play(yae):
    st = _state()
    _play(st, _ym("editor_in_chief"))
    _play(st, _ym("twin_sakura"))
    a = loader.get_card("strike")
    st.player.hand.append(a)
    _play(st, _red_ink_edit())
    _play(st, a)
    hits = _strikes(st)
    assert len(hits) == 1 and hits[0]["reason"] == "editor_in_chief"
    assert hits[0]["level"] == 1                 # the highest (oldest on a tie)


def test_publish_marks_the_best_annotated_card_and_drafts_are_recorded(yae):
    st = _state()
    a, b = loader.get_card("strike"), loader.get_card("strike")
    a.ym_slot, b.ym_slot = 10, 11
    st.player.hand += [a, b]
    _play(st, _red_ink_edit())                  # a: Red Ink
    _play(st, _ym("sakura_seal"))                # b: Sakura Seal
    _play(st, _ym("the_seven_glamours"))
    assert getattr(b, "ym_published", False) and not getattr(
        a, "ym_published", False)
    Y.turn_end(st)
    assert _led(st).drafts == {10: Y.RED_INK, 11: Y.SAKURA_SEAL}


def test_a_published_annotation_enters_the_next_fight(yae):
    p = Y.build_player(published={0: Y.SAKURA_SEAL})
    c = p.draw_pile[0]
    assert c.id == "strike" and c.ym_annotation == Y.SAKURA_SEAL
    assert c.ym_published


# ---------------------------------------------------------------------------
# 3. A whole fight, and the harness
# ---------------------------------------------------------------------------

def test_a_whole_fight_runs_and_the_shrine_strikes(yae):
    from tools import yae_expansion_sim as S
    S.enable("level")
    r = S.fight([_ym("twin_sakura"), _ym("thunder_rite"),
                 _ym("sakura_seal")],
                [_enemy(hp=40, name="a"), _enemy(hp=40, name="b")],
                seed=3, hp=72)
    assert r["error"] is None, r.get("trace")
    assert r["won"] and r["strikes"] > 0
    assert r["turn_rows"]


def test_the_harness_pool_is_the_staged_pool(yae):
    from tools import yae_expansion_sim as S
    pl = S.pool()
    assert {k: len(v) for k, v in pl.items()} == {
        "common": 15, "uncommon": 16, "rare": 9}
    for d in S.DECKS.values():
        for cid in d["core"] + d["support"]:
            loader.get_card(cid)


def test_a_full_shrine_plant_strikes_the_oldest_as_its_last_bloom(yae):
    # [USER] (2026-10-14): "when you plant a Sakura with 3 already on the
    # field, do you think the outgoing Sakura should strike as though
    # withered?" It strikes first (Thunder, Red Ink and Fox Fire as usual),
    # then refreshes and gains a Level.
    st = _state()
    Y.plant(st, 3)
    _led(st).sakura[0].annotation = Y.RED_INK
    hp = st.enemies[0].hp
    Y.plant(st, 1)
    assert [r["reason"] for r in _strikes(st)] == ["full_shrine"]
    assert hp - st.enemies[0].hp == 2 + 1 + Y.RED_INK_AMOUNT   # its old Level
    assert [s.level for s in _led(st).sakura] == [2, 1, 1]
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS


def test_twin_sakura_into_a_full_shrine_strikes_per_plant(yae):
    st = _state()
    Y.plant(st, 3)
    _play(st, _ym("twin_sakura"))
    # Plant one feeds the oldest (now the newest-refreshed, still first);
    # plant two feeds it again: two strikes, at Levels 1 then 2.
    assert [r["level"] for r in _strikes(st)] == [1, 2]
    assert [s.level for s in _led(st).sakura] == [3, 1, 1]


def test_a_plant_below_the_cap_strikes_nothing(yae):
    st = _state()
    _play(st, _ym("sakura_channeling"))
    Y.plant(st, 5)
    assert not _strikes(st)
    Y.plant(st, 1)
    assert len(_strikes(st)) == 1


def test_tenko_refreshes_every_timer_to_at_least_three(yae):
    # Main session, 2026-10-14 (after a GPT design review): Tenko never
    # shortens a timer extended past 3; a shorter one comes back up to 3.
    st = _state()
    Y.plant(st, 2)
    Y.extend(st, 2)                              # 5, 5
    _led(st).sakura[1].turns_left = 1
    Y.tenko(st)
    assert [s.turns_left for s in _led(st).sakura] == [5, Y.SAKURA_TURNS]


def test_a_full_shrine_plant_never_shortens_the_oldests_timer(yae):
    st = _state()
    Y.plant(st, 3)
    _led(st).sakura[0].turns_left = 6
    Y.plant(st, 1)
    assert _led(st).sakura[0].turns_left == 6
    _led(st).sakura[0].turns_left = 1
    Y.plant(st, 1)
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS
