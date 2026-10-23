"""FURINA, THE SWEEP in the one-seat sim.

`review/active/furina-sweep-2026-10-14.md` sec.2 and sec.3: fifteen cut,
fifteen new (the second set, ruled 2026-10-14), the pool still 78 at
23 / 35 / 20 with 17 Powers. The five new `furina` kinds
(`furina_stage._sweep_kind`), the six Powers, the HP-loss reads and
`playable_if`. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaSweepTests.cs`.
"""

from __future__ import annotations

import copy
from collections import Counter

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, refpowers, resources
from tier0.tests.conftest import make_enemy, make_state

CUT = ("soloists_solicitation", "spirited_aria", "standing_ovation_all",
       "hydro_lance", "overdraft", "packed_house", "interval_bell",
       "soothing_waters", "balance_the_books", "salons_encore", "ousia_surge",
       "high_stakes", "pneuma_tides", "the_deluge", "hymn_of_renewal")
NEW = {"ousia_pneuma": "common", "objection": "common",
       "tearful_monologue": "common", "stage_directions": "common",
       "opening_number": "common", "facade": "common",
       "trial_by_water": "uncommon", "rainfall_overture": "uncommon",
       "encore_performance": "uncommon", "arkhe_in_balance": "uncommon",
       "crowd_favorite": "uncommon", "the_shows_not_over": "uncommon",
       "understudys_debut": "uncommon",
       "verdict_of_the_oratrice": "rare", "plot_twist": "rare"}
FIRST_SET = ("rain_of_tears", "rehearsal", "silence_in_the_court",
             "pirouette", "spotlight_grab", "costume_fitting", "quick_change",
             "read_the_script", "practiced_grace", "mise_en_scene",
             "intermission", "second_act", "solo_recital", "pneuma_and_ousia",
             "stand_in")


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, enemies=None):
    st = make_state(enemies=enemies or [make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.in_player_turn = True
    st.turn = 2
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


def _pull(st, card):
    for pile in (st.player.hand, st.player.discard_pile,
                 st.player.exhaust_pile, st.player.draw_pile):
        if any(c is card for c in pile):
            pile[:] = [c for c in pile if c is not card]


# ---- the pool -------------------------------------------------------------

def test_the_pool_is_78_at_23_35_20_with_17_powers():
    pool = [loader.get_card(cid) for cid in FS.POOL_IDS]
    assert len(pool) == 78 == len(set(FS.POOL_IDS))
    assert Counter(c.rarity for c in pool) == {
        "common": 23, "uncommon": 35, "rare": 20}
    assert sum(c.type == "power" for c in pool) == 17
    ids = {c.id for c in loader.prototype_cards()}
    for gone in CUT + FIRST_SET:
        assert "proto_fs_" + gone not in ids, gone
    for new, rarity in NEW.items():
        assert "proto_fs_" + new in FS.POOL_IDS, new
        assert loader.get_card("proto_fs_" + new).rarity == rarity, new


# ---- Ousia / Pneuma --------------------------------------------------------

def test_ousia_pneuma_hits_then_blocks_then_hits():
    # Furina's card pass (2026-10-15): Ousia "Drain 2. Deal 10 [13] damage.",
    # Pneuma "Repay 2. Gain 8 [11] Block." (was 8 [11] and 7 [10]).
    st = _furina()
    card = _card("proto_fs_ousia_pneuma")
    hp = st.enemies[0].hp
    mine = st.player.hp
    _play(st, card)
    assert hp - st.enemies[0].hp == 10 and st.player.block == 0
    assert st.player.hp == mine - 2
    assert card.flipped
    _pull(st, card)
    _play(st, card)
    assert st.player.block == 8 and not card.flipped
    assert st.player.hp == mine
    st = _furina()
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_ousia_pneuma+"))
    assert hp - st.enemies[0].hp == 13


def test_a_new_combat_starts_every_card_on_ousia():
    st = _furina()
    card = _card("proto_fs_ousia_pneuma")
    card.flipped = True
    st.player.draw_pile = [card]
    st.turn = 1
    FS.turn_start(st)
    assert not card.flipped


# ---- the HP-loss reads -----------------------------------------------------

def test_tearful_monologue_draws_off_last_turns_hp_loss():
    st = _furina()
    st.player.draw_pile = [_card("strike") for _ in range(4)]
    _play(st, _card("proto_fs_tearful_monologue"))
    assert st.player.block == 6 and len(st.player.hand) == 0
    resources.note_player_hp_loss(st, 3)
    refpowers.reset_turn_counters(st)               # the turn rolls
    assert st.hp_lost_last_turn == 3
    _play(st, _card("proto_fs_tearful_monologue"))
    assert len(st.player.hand) == 2


def test_facade_blocks_the_hp_lost_this_combat_up_to_its_cap():
    st = _furina()
    resources.note_player_hp_loss(st, 5)
    _play(st, _card("proto_fs_facade"))
    assert st.player.block == 5
    st = _furina()
    resources.note_player_hp_loss(st, 30)
    _play(st, _card("proto_fs_facade"))
    assert st.player.block == 12
    st = _furina()
    resources.note_player_hp_loss(st, 30)
    _play(st, _card("proto_fs_facade+"))
    assert st.player.block == 16


def test_the_shows_not_over_needs_hp_lost_this_turn():
    st = _furina()
    card = _card("proto_fs_the_shows_not_over")
    st.player.hand.append(card)
    assert not combat.card_playable(st, card)
    resources.note_player_hp_loss(st, 1)
    assert combat.card_playable(st, card)
    energy = st.player.energy
    combat.play_card(st, card)
    assert st.player.energy == energy + 2 and card.exhaust
    up = _card("proto_fs_the_shows_not_over+")
    assert up.exhaust and up.effects[0]["amount"] == 3


def test_understudys_debut_below_half_hits_twice_and_blocks():
    st = _furina(hp=78)
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_understudys_debut"))
    assert hp - st.enemies[0].hp == 6 and st.player.block == 0
    st = _furina(hp=30)
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_understudys_debut+"))
    assert hp - st.enemies[0].hp == 16 and st.player.block == 8


def test_opening_number_is_innate_and_doubles_on_turn_one():
    assert _card("proto_fs_opening_number").innate
    st = _furina()
    st.turn = 1
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_opening_number"))
    assert hp - st.enemies[0].hp == 14
    st = _furina()
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_opening_number"))
    assert hp - st.enemies[0].hp == 7


# ---- the kinds -------------------------------------------------------------

def test_stage_directions_tops_a_card_free_next_turn():
    st = _furina()
    other = _card("proto_fs_facade")
    st.player.hand = [other]
    _play(st, _card("proto_fs_stage_directions"))
    assert st.player.block == 5
    assert st.player.draw_pile[0] is other and other.free_next_turn
    st.turn = 3
    FS.turn_start(st)
    assert other.free_this_turn and not other.free_next_turn


def test_encore_performance_plays_the_top_discard_free_and_exhausts_it():
    st = _furina()
    top = _card("proto_fs_facade")
    resources.note_player_hp_loss(st, 4)
    st.player.discard_pile = [_card("strike"), top]
    energy = st.player.energy
    _play(st, _card("proto_fs_encore_performance"))
    assert st.player.block == 4
    assert any(c is top for c in st.player.exhaust_pile)
    assert st.player.energy == energy - 1
    assert _card("proto_fs_encore_performance+").cost == 0


def test_verdict_executes_at_or_below_fanfare_else_deals_it():
    st = _furina(enemies=[make_enemy(hp=10)])
    FS.T.gain(st, 10, "test")
    _play(st, _card("proto_fs_verdict_of_the_oratrice"))
    assert not st.enemies[0].alive
    assert FS.T._f(st).fanfare == 10                 # not spent
    st = _furina(enemies=[make_enemy(hp=50)])
    FS.T.gain(st, 10, "test")
    _play(st, _card("proto_fs_verdict_of_the_oratrice"))
    assert st.enemies[0].hp == 40
    assert _card("proto_fs_verdict_of_the_oratrice+").cost == 1


# ---- the Powers ------------------------------------------------------------

def test_arkhe_in_balance_blocks_on_attacks_and_hits_on_skills():
    st = _furina()
    _play(st, _card("proto_fs_arkhe_in_balance"))
    assert st.player.powers[FS.ARKHE_IN_BALANCE] == 2
    _play(st, _card("strike"))
    assert st.player.block == 2
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_tearful_monologue"))
    assert hp - st.enemies[0].hp == 2
    st = _furina()
    _play(st, _card("proto_fs_arkhe_in_balance+"))
    assert st.player.powers[FS.ARKHE_IN_BALANCE] == 3


def test_objection_answers_the_next_hp_losing_hit_double_once():
    st = _furina()
    _play(st, _card("proto_fs_objection"))
    assert st.player.block == 5
    enemy = st.enemies[0]
    hp = enemy.hp
    FS.objection(st, enemy, 6)
    assert hp - enemy.hp == 12
    FS.objection(st, enemy, 6)
    assert hp - enemy.hp == 12                       # once


def test_trial_by_water_pays_fanfare_per_damage_this_turn():
    st = _furina()
    _play(st, _card("proto_fs_trial_by_water"))
    enemy = st.enemies[0]
    assert enemy.powers.get("vulnerable") == 2
    before = FS.T._f(st).fanfare
    _play(st, _card("strike"))
    assert FS.T._f(st).fanfare == before + 2
    FS.turn_end(st)
    assert not enemy.powers.get(FS.TRIAL_BY_WATER)


def test_rainfall_overture_widens_the_next_attack_only():
    st = _furina(enemies=[make_enemy(hp=50), make_enemy(hp=50)])
    _play(st, _card("proto_fs_rainfall_overture"))
    assert all(e.aura == "hydro" for e in st.enemies)
    _play(st, _card("strike"))
    assert all(e.hp < 50 for e in st.enemies)
    hp = [e.hp for e in st.enemies]
    _play(st, _card("strike"))
    assert sum(a != b for a, b in zip(hp, (e.hp for e in st.enemies))) == 1
    # The upgrade census (2026-10-23): it draws 1, at the same cost.
    assert _card("proto_fs_rainfall_overture+").cost == 1


def test_crowd_favorite_pays_energy_below_half_only():
    st = _furina(hp=30)
    _play(st, _card("proto_fs_crowd_favorite"))
    assert FS.crowd_favorite(st) == 1
    st.player.hp = 60
    assert FS.crowd_favorite(st) == 0
    assert _card("proto_fs_crowd_favorite+").innate


def test_plot_twist_turns_the_attack_on_its_attacker():
    st = _furina()
    card = _card("proto_fs_plot_twist")
    assert card.playable_if == "enemy_intends_attack" and card.exhaust
    enemy = st.enemies[0]
    enemy.powers[FS.PLOT_TWIST] = 1
    hp = enemy.hp
    assert FS.plot_twist(st, enemy, 9)
    assert hp - enemy.hp == 9
    FS.turn_start(st)
    assert not FS.plot_twist(st, enemy, 9)
