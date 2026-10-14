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


def test_planting_levels_the_standing_sakura_and_a_fourth_only_levels(yae):
    st = _state()
    for _ in range(3):
        _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [3, 2, 1]
    _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [3, 3, 2]
    _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [3, 3, 3]
    Y.turn_end(st)
    assert sum(r["amount"] for r in _strikes(st)) == 15


def test_a_sakura_withers_after_three_strikes_and_tenko_refreshes(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    for _ in range(3):
        Y.turn_end(st)
    assert _led(st).sakura == []
    assert len(_strikes(st)) == 3
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
    _play(st, _ym("shrine_maidens_guard"))       # 6, and Rite: Warding
    assert st.player.block == 6 and _led(st).rite == Y.WARDING


def test_mooncall_plants_at_two_and_caps_at_four(yae):
    st = _state()
    _play(st, _ym("foxs_mooncall"))
    for _ in range(5):
        _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [4, 4, 4]


def _hits(st):
    return [r for r in st.log if r["event"] == "yae_sakura_hit"]


def test_the_powers_pay_on_a_strike(yae):
    st = _state(enemies=[_enemy(name="e0", aura="hydro")])
    _play(st, _ym("sakura_grove"))               # +2
    _play(st, _ym("edict_of_cleansing"))         # +3 on a reacting aura
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)
    assert _strikes(st)[0]["amount"] == 3 + 2
    assert _hits(st)[0]["amount"] == 3 + 2 + 3
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

def test_every_combat_opens_in_thunder(yae):
    st = _state()
    assert _led(st).rite == Y.THUNDER
    Y.open_combat(st.player)
    assert Y.ledger(st.player).rite == Y.THUNDER


def test_thunder_strikes_one_enemy_for_two_plus_level(yae):
    st = _state(n=2)
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)
    hits = _hits(st)
    assert len(hits) == 1 and hits[0]["amount"] == 3 and hits[0]["rite"] == Y.THUNDER
    assert sum(e.hp for e in st.enemies) == 200 - 3


def test_warding_gives_two_plus_level_block_and_no_damage(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("yakan_evocation"))            # levels 2 / 1
    _play(st, _ym("shrine_maidens_guard"))       # 6 Block, Rite: Warding
    st.player.block = 0
    Y.turn_end(st)
    assert st.player.block == (2 + 2) + (2 + 1)
    assert st.enemies[0].hp == 100 and not _hits(st)


def test_wildfire_strikes_all_for_level(yae):
    st = _state(n=3)
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("yakan_evocation"))            # levels 2 / 1
    _play(st, _ym("kitsune_guile"))              # Rite: Wildfire
    hp = [e.hp for e in st.enemies]
    Y.turn_end(st)
    assert [h - e.hp for h, e in zip(hp, st.enemies)] == [3, 3, 3]
    assert len(_strikes(st)) == 2 and len(_hits(st)) == 6


def test_offering_draws_one_a_strike_at_the_next_turn_start(yae):
    st = _state()
    _play(st, _ym("twin_sakura"))
    _play(st, _ym("manuscript_pile"))            # Rite: Offering
    assert _led(st).rite == Y.OFFERING
    st.player.draw_pile = [loader.get_card("defend") for _ in range(5)]
    st.player.hand = []
    Y.turn_end(st)
    assert _led(st).pending_draw == 2 and not _hits(st)
    Y.turn_start(st)
    assert len(st.player.hand) == 2 and _led(st).pending_draw == 0


def test_a_rite_holds_until_another_replaces_it(yae):
    st = _state()
    _play(st, _ym("foxfire_sweep"))              # Rite: Wildfire
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)
    Y.turn_start(st)
    assert _led(st).rite == Y.WILDFIRE
    _play(st, _ym("thunder_rite"))               # Rite: Thunder, then Tenko
    assert _led(st).rite == Y.THUNDER
    assert _strikes(st)[-1]["rite"] == Y.THUNDER


def test_grove_and_mikage_size_three_rites_but_not_offering(yae):
    st = _state()
    _play(st, _ym("sakura_grove"))               # +2
    _play(st, _ym("mikage_thunder"))             # +1 (after its own Tenko)
    _play(st, _ym("yakan_evocation"))
    s = _led(st).sakura[0]
    assert Y.strike_size(st, s, Y.THUNDER) == 3 + 3
    assert Y.strike_size(st, s, Y.WARDING) == 3 + 3
    assert Y.strike_size(st, s, Y.WILDFIRE) == 1 + 3
    assert Y.strike_size(st, s, Y.OFFERING) == 1


def test_mikage_thunder_tenkos_then_stacks_per_play(yae):
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("mikage_thunder"))
    assert _strikes(st)[-1]["reason"] == "tenko"
    assert _strikes(st)[-1]["amount"] == 3       # the Tenko came first
    _play(st, _ym("mikage_thunder"))
    assert st.player.powers[Y.MIKAGE_THUNDER] == 2
    assert _strikes(st)[-1]["amount"] == 3 + 1


def test_channeling_adds_a_thunder_strike_in_any_other_rite(yae):
    st = _state()
    _play(st, _ym("sakura_channeling"))
    _play(st, _ym("yakan_evocation"))
    Y.turn_end(st)                               # Thunder: nothing more
    assert len(_hits(st)) == 1
    _play(st, _ym("shrine_maidens_guard"))       # Warding
    st.player.block = 0
    hp = st.enemies[0].hp
    Y.tenko(st)
    assert st.player.block == 3                  # Warding, 2 + 1
    assert hp - st.enemies[0].hp == 3            # and Thunder, 2 + 1
    assert _hits(st)[-1]["reason"] == "channeling"


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
        Y.validate_op("x", {"op": "yae", "kind": "rite", "rite": "storm"})


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
    assert [s.level for s in _led(st).sakura] == [3, 3]


def test_kitsune_pounce_strikes_a_weak_enemy(yae):
    st = _state(n=2)
    _play(st, _ym("yakan_evocation"))
    _play(st, _ym("kitsune_pounce"))             # e0 not Weak: no strike
    assert not _strikes(st)
    st.enemies[0].powers["weak"] = 1
    _play(st, _ym("kitsune_pounce"))
    assert _strikes(st)[-1]["reason"] == "pounce"
    assert _strikes(st)[-1]["target"] == "e0"


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
    _play(st, _ym("proofread"))
    assert strike.ym_annotation == Y.RED_INK and Y.is_annotated(strike)
    assert st.player.block == 0                  # Proofread gives no Block (pick 3)
    _play(st, strike)
    assert st.enemies[0].hp == 100 - 6 - 3
    defend = loader.get_card("defend")
    st.player.hand.append(defend)
    _play(st, _ym("proofread"))
    _play(st, defend)
    assert st.player.block == 5 + 3


def test_an_edit_never_targets_itself_a_status_or_an_annotated_card_first(yae):
    st = _state()
    a, b = loader.get_card("strike"), loader.get_card("strike")
    st.player.hand += [a, b]
    _play(st, _ym("proofread"))
    _play(st, _ym("proofread"))
    assert Y.is_annotated(a) and Y.is_annotated(b)
    assert _led(st).edits == 2


def test_an_edit_overwrites_and_deadline_retains(yae):
    st = _state()
    c = loader.get_card("strike")
    st.player.hand.append(c)
    _play(st, _ym("proofread"))
    _play(st, _ym("deadline"))
    assert c.ym_annotation == Y.DEADLINE and c.retain
    assert c.enchant_damage == 0
    _play(st, _ym("proofread"))
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
    _play(st, _ym("proofread"))
    _play(st, _ym("bestseller"))                 # 5 + 3 x 1
    assert st.enemies[0].hp == 100 - 8
    _play(st, _ym("print_run"))                  # 6 + 2 x 1
    assert st.player.block == 8
    flash = loader.get_card(_ym("kitsune_flash"))
    st.player.hand.append(flash)
    _play(st, _ym("proofread"))                  # Red Ink on the Flash
    assert flash.ym_annotation == Y.RED_INK
    _play(st, flash)                             # 6 + 3 (annotated) + 3 ink
    assert st.enemies[0].hp == 100 - 8 - 12


def test_serialization_pays_block_per_edit_and_reborn_edits_the_hand(yae):
    st = _state()
    _play(st, _ym("serialization"))
    st.player.hand += [loader.get_card("strike"), loader.get_card("defend")]
    _play(st, _ym("reborn_as_guuji_yae"))
    assert st.player.block == 6                  # 3 Block an Edit, twice
    assert all(c.ym_annotation == Y.SAKURA_SEAL for c in st.player.hand)


def test_editor_in_chief_strikes_on_an_annotated_play(yae):
    st = _state()
    _play(st, _ym("editor_in_chief"))
    _play(st, _ym("twin_sakura"))
    a = loader.get_card("strike")
    st.player.hand.append(a)
    _play(st, _ym("proofread"))
    _play(st, a)
    hits = _strikes(st)
    assert len(hits) == 1 and hits[0]["reason"] == "editor_in_chief"
    assert hits[0]["level"] == 2                 # the highest Level struck


def test_publish_marks_the_best_annotated_card_and_drafts_are_recorded(yae):
    st = _state()
    a, b = loader.get_card("strike"), loader.get_card("strike")
    a.ym_slot, b.ym_slot = 10, 11
    st.player.hand += [a, b]
    _play(st, _ym("proofread"))                  # a: Red Ink
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
