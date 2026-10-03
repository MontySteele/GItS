"""THE AoE TRIM (2026-10-03, `review/active/aoe-trim-2026-10-03.md`) in the
sim: Klee's seven swaps (sec.2), Furina's two (sec.3), Durin split in two
(sec.5) and Yoimiya's Aurous Blaze (sec.6).

Sim first: the C# twin is built after the sim reads well. NOTHING MEASURED
HERE IS QUOTABLE (R215 B): these are shape assertions about the rows.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, klee_overhaul, reactions
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards


@pytest.fixture(autouse=True)
def caches():
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


def klee_state(enemies=None, hp=62):
    st = make_state(enemies=enemies or [make_enemy(hp=200)], hp=hp)
    st.player.character_id = "klee"
    st.player.element = "pyro"
    st.player.cadence = "catalyst"
    st.player.relic_hooks.append(klee_overhaul.SPARK_RELIC_HOOK)
    st.in_player_turn = True
    st.player.energy = 5
    return st


def load(cid):
    return loader.get_card(cid)


def play(state, card, aim=None):
    """Resolve a card with the play bound to `aim` (the human's pick; the
    engine's own bind is the lowest-HP enemy)."""
    if aim is None:
        effects.resolve_card(state, card)
        return
    bind = effects.bind_card_aim
    effects.bind_card_aim = lambda _state, _card: aim
    try:
        effects.resolve_card(state, card)
    finally:
        effects.bind_card_aim = bind


def sizes(enemy):
    return [c.size for c in enemy.ko_charges]


def three():
    return [make_enemy(hp=200, name=n) for n in "abc"]


# ---------------------------------------------------------------------------
# KLEE (sec.2)
# ---------------------------------------------------------------------------

def test_no_klee_swap_reaches_all_enemies():
    for cid in ("proto_ko_bombs_away", "proto_ko_mine_toss",
                "proto_ko_mine_all_mine", "proto_ko_team_effort",
                "proto_ko_coven_errand", "proto_ko_red_knight"):
        for card in (load(cid), load(cid + "+")):
            for fx in effects_walk(card.effects):
                assert fx.get("target") != "all_enemies", (cid, fx)
                assert "wide_if" not in fx, (cid, fx)


def effects_walk(fxs):
    for fx in fxs:
        yield fx
        for arm in ("then", "else"):
            yield from effects_walk(fx.get(arm) or [])
        for mode in fx.get("modes") or []:
            yield from effects_walk(mode.get("effects") or [])


def test_bombs_away_is_a_skill_whose_block_counts_bombed_enemies():
    a, b, c = three()
    st = klee_state([a, b, c])
    card = load("proto_ko_bombs_away")
    assert card.type == "skill" and card.cost == 1
    play(st, card, aim=a)
    # Its own Bomb counts: 4 + 2 x 1.
    assert sizes(a) == [4] and sizes(b) == [] and sizes(c) == []
    assert st.player.block == 6
    klee_overhaul.place(st, b, 3, is_mine=True)       # a Mine is a Bomb
    st.player.block = 0
    play(st, card, aim=c)
    assert st.player.block == 4 + 2 * 3


def test_bombs_away_upgrade_moves_the_bomb():
    a = make_enemy(hp=200)
    st = klee_state([a])
    play(st, load("proto_ko_bombs_away+"), aim=a)
    assert sizes(a) == [6] and st.player.block == 6


def test_mine_toss_places_one_mine_seven_on_one_enemy():
    a, b, c = three()
    st = klee_state([a, b, c])
    play(st, load("proto_ko_mine_toss"), aim=b)
    assert sizes(a) == [] and sizes(c) == []
    assert [(ch.size, ch.is_mine) for ch in b.ko_charges] == [(7, True)]
    play(st, load("proto_ko_mine_toss+"), aim=a)
    assert sizes(a) == [10]


# Mine, All Mine!'s mines-only Set off left in the Klee finish-line batch
# (2026-10-03), with its engine piece; the card's new body is pinned in
# `test_klee_finish_batch.py`.


def test_team_effort_sets_off_the_target_only_and_pays_six_more():
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    klee_overhaul.place(st, a, 5)
    klee_overhaul.place(st, b, 5)
    play(st, load("proto_ko_team_effort"), aim=a)
    plain = 200 - a.hp
    assert sizes(a) == [] and sizes(b) == [5] and b.hp == 200

    a2, b2 = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a2, b2])
    klee_overhaul.place(st, a2, 5)
    klee_overhaul.place(st, b2, 5)
    st.ko_companion_this_turn = 1
    play(st, load("proto_ko_team_effort"), aim=a2)
    assert sizes(b2) == [5] and b2.hp == 200
    assert (200 - a2.hp) - plain == 6


def test_coven_errand_places_five_or_eight_on_one_enemy():
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    play(st, load("proto_ko_coven_errand"), aim=a)
    assert sizes(a) == [5] and sizes(b) == []
    st.ko_companion_this_turn = 1
    play(st, load("proto_ko_coven_errand"), aim=b)
    assert sizes(b) == [8] and sizes(a) == [5]
    play(st, load("proto_ko_coven_errand+"), aim=b)
    assert sizes(b) == [8, 10]


def test_red_knight_is_34_to_one_enemy_and_two_confiscated():
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    card = load("proto_ko_red_knight")
    assert card.cost == 2 and card.rarity == "rare"
    play(st, card, aim=a)
    assert b.hp == 200 and 200 - a.hp >= 34
    assert sum(c.id == "confiscated" for c in st.player.discard_pile) == 2
    hit = next(fx for fx in load("proto_ko_red_knight+").effects
               if fx["op"] == "damage")
    assert hit["amount"] == 40


def test_damage_report_gains_block_per_status_drawn_and_deals_nothing():
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    st = klee_state([a, b])
    play(st, load("proto_ko_damage_report"))
    status = Card(id="dazed", name="Dazed", cost=0, type="status",
                  rarity="status", effects=[])
    klee_overhaul.damage_report(st, status)
    klee_overhaul.damage_report(st, status)
    assert st.player.block == 8
    assert a.hp == 200 and b.hp == 200
    klee_overhaul.damage_report(st, Card(id="x", name="x", cost=1,
                                         type="skill", effects=[]))
    assert st.player.block == 8
    up = next(fx for fx in load("proto_ko_damage_report+").effects
              if fx["op"] == "apply_power")
    assert up["amount"] == 6


# ---------------------------------------------------------------------------
# FURINA (sec.3)
# ---------------------------------------------------------------------------

def test_undercurrent_is_three_hits_of_three_on_one_enemy():
    card = load("proto_fs_undercurrent")
    assert card.effects == [{"op": "damage", "amount": 3, "target": "enemy",
                             "times": 3}]


def test_endless_waltz_is_eighteen_to_one_enemy():
    hit = load("proto_fs_endless_waltz").effects[0]
    assert hit == {"op": "damage", "amount": 18, "target": "enemy"}
    assert load("proto_fs_endless_waltz+").effects[0]["amount"] == 22


# ---------------------------------------------------------------------------
# DURIN, SPLIT IN TWO (sec.5)
# ---------------------------------------------------------------------------

def test_durin_is_two_rows_in_the_mondstadt_roster():
    assert {"proto_mc_durin_binary_form",
            "proto_mc_durin_principle_of_purity"} <= set(
                C.MONDSTADT_OVERHAUL_POOL_IDS)
    bf = load("proto_mc_durin_binary_form")
    pp = load("proto_mc_durin_principle_of_purity")
    assert (bf.type, bf.cost, bf.rarity) == ("attack", 1, "uncommon")
    assert (pp.type, pp.cost, pp.rarity) == ("power", 2, "rare")


def _force_mode(monkeypatch, index):
    monkeypatch.setattr(effects, "_chosen_mode",
                        lambda state, modes, card: index)


def test_binary_form_white_hits_all_and_draws(monkeypatch):
    _force_mode(monkeypatch, 0)
    st = make_state(enemies=[make_enemy(hp=50, name="a"),
                             make_enemy(hp=50, name="b")])
    st.player.draw_pile = [Card(id="f", name="f", cost=1, type="skill",
                                effects=[])]
    play(st, load("proto_mc_durin_binary_form"))
    assert [e.hp for e in st.enemies] == [44, 44]
    assert len(st.player.hand) == 1


def test_binary_form_dark_hits_one_enemy_three_times(monkeypatch):
    _force_mode(monkeypatch, 1)
    a, b = make_enemy(hp=50, name="a"), make_enemy(hp=50, name="b")
    st = make_state(enemies=[a, b])
    play(st, load("proto_mc_durin_binary_form"), aim=a)
    assert a.hp == 50 - 12 and b.hp == 50


def test_binary_form_upgrade_moves_each_mode_by_its_own_number():
    modes = load("proto_mc_durin_binary_form+").effects[0]["modes"]
    assert modes[0]["effects"][0]["amount"] == 8
    assert modes[1]["effects"][0]["amount"] == 5


def test_principle_of_purity_hits_a_random_enemy_each_turn_start(monkeypatch):
    _force_mode(monkeypatch, 0)
    st = make_state(enemies=[make_enemy(hp=50)])
    play(st, load("proto_mc_durin_principle_of_purity"))
    assert st.player.powers["mc_purity_strike"] == 4
    effects.companion_overhaul_turn_start(st)
    assert st.enemies[0].hp == 46
    assert st.enemies[0].aura == "pyro"


def test_principle_of_purity_white_is_the_team_reaction_multiplier(
        monkeypatch):
    _force_mode(monkeypatch, 0)
    st = make_state(enemies=[make_enemy(hp=90)])
    play(st, load("proto_mc_durin_principle_of_purity"))
    assert st.player.powers["mc_purity_white"] == 50
    assert effects.companion_overhaul_reaction_mult(st) == pytest.approx(1.5)
    st.enemies[0].aura = "hydro"
    plain = 10 * C.VAPORIZE_MULT
    amped = reactions.resolve_hit(st, st.enemies[0], "pyro", 10)
    assert amped == 10 + (plain - 10) * 1.5


def test_principle_of_purity_upgrade_moves_all_three_numbers():
    fx = load("proto_mc_durin_principle_of_purity+").effects
    assert fx[0]["amount"] == 6
    assert fx[1]["modes"][0]["effects"][0]["amount"] == 75
    assert fx[1]["modes"][1]["effects"][0]["amount"] == 6


def test_dark_adds_to_every_pyro_hit_bombs_included():
    st = klee_state([make_enemy(hp=200)])
    st.player.powers["mc_purity_dark"] = 4
    e = st.enemies[0]
    effects.deal_damage_to_enemy(st, e, 10, element="pyro", source="attack")
    assert e.hp == 186
    effects.deal_damage_to_enemy(st, e, 10, element="pyro", source="card")
    assert e.hp == 172
    # A Bomb: unpowered, and still her Pyro damage.
    klee_overhaul.place(st, e, 5)
    klee_overhaul.set_off(st, e)
    assert e.hp == 172 - 9
    # Not Pyro: nothing (the aura cleared so no reaction muddies it).
    e.aura = None
    effects.deal_damage_to_enemy(st, e, 10, element="hydro", source="attack")
    assert e.hp == 163 - 10


# ---------------------------------------------------------------------------
# YOIMIYA, AUROUS BLAZE (sec.6)
# ---------------------------------------------------------------------------

def _skill():
    return Card(id="s", name="s", cost=1, type="skill", effects=[])


def test_aurous_blaze_hits_now_then_answers_each_skill_on_its_enemy():
    a, b = make_enemy(hp=90, name="a"), make_enemy(hp=90, name="b")
    st = make_state(enemies=[a, b])
    card = load("proto_mi_yoimiya_aurous_blaze")
    assert card.type == "skill"
    play(st, card, aim=a)
    effects.companion_overhaul_card_played(st, card)   # not its own trigger
    assert a.hp == 84 and b.hp == 90
    assert a.powers["mi_aurous_blaze"] == 2
    s = _skill()
    effects.companion_overhaul_card_played(st, s)
    assert a.hp == 81 and b.hp == 90
    atk = Card(id="t", name="t", cost=1, type="attack", effects=[])
    effects.companion_overhaul_card_played(st, atk)
    assert a.hp == 81


def test_aurous_blaze_lasts_two_turns():
    a = make_enemy(hp=90)
    st = make_state(enemies=[a])
    play(st, load("proto_mi_yoimiya_aurous_blaze"), aim=a)
    effects.inazuma_overhaul_turn_end(st)
    assert a.powers["mi_aurous_blaze"] == 1
    effects.inazuma_overhaul_turn_end(st)
    assert "mi_aurous_blaze" not in a.powers
    hp = a.hp
    effects.companion_overhaul_card_played(st, _skill())
    assert a.hp == hp


def test_aurous_blaze_no_longer_answers_non_attack_damage():
    a, b = make_enemy(hp=90, name="a"), make_enemy(hp=90, name="b")
    st = make_state(enemies=[a, b])
    play(st, load("proto_mi_yoimiya_aurous_blaze"), aim=a)
    effects.deal_damage_to_enemy(st, a, 5, source="card")
    assert a.hp == 84 - 5 and b.hp == 90


# ---------------------------------------------------------------------------
# THE RIDER'S LOAD CHECK
# ---------------------------------------------------------------------------

def test_bonus_if_with_an_unknown_predicate_is_refused_at_load():
    with pytest.raises(ValueError, match="bonus_if"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "damage", "amount": 1, "target": "enemy",
                       "bonus_if": {"if": "no_such_thing", "amount": 2}}])
