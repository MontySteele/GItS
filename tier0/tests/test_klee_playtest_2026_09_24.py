"""THE OWNER'S CO-OP PLAYTEST OF 2026-09-24 (build 0.2.3737+proto; arms Klee,
Companion, Kokomi and Furina Stage), the rulings that came out of it, and the
Klee balance review (pick 4a, 2026-09-25,
`review/records/klee-balance-2026-09-25.md`).

The C# is FIRST and this is its twin, case for case with
`klee-mod/KleeTests/Prototype/KleePlaytest20260924Tests.cs`: where a pin is
STRUCTURAL there (an explosion needs a live combat the headless harness does
not have), it is a real board here.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): every number is a starting value.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, klee_overhaul
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

ATTACKER = [{"kind": "attack", "amount": 5}]


@pytest.fixture
def overhaul(monkeypatch):
    """The flag on, with the arm's caches cleared on the way in and out --
    `test_klee_overhaul.overhaul`'s fixture, for its reasons."""
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


@pytest.fixture
def companions(monkeypatch):
    """The Companion arm on, `test_companion_overhaul.overhaul`'s fixture."""
    def clear():
        loader.reset_arm_caches()
        rewards._companion_roster.cache_clear()
        rewards.companion_pool.cache_clear()
        rewards.five_star_roster.cache_clear()
        rewards.designed_nations.cache_clear()
    clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    yield
    clear()


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


def sizes(enemy):
    return [c.size for c in enemy.ko_charges]


def play(state, card, aim=None):
    if aim is not None:
        state.card_aim, state.card_aim_bound = aim, True
    effects.resolve_card(state, card)


def filler(n=6):
    return [Card(id=f"filler{i}", name="filler", cost=1, type="skill",
                 effects=[]) for i in range(n)]


# ---------------------------------------------------------------------------
# POCKET MATCH: "Set off only your largest Bomb on the enemy. Deal 3 damage."
# ---------------------------------------------------------------------------

def test_pocket_match_is_free_retained_and_prices_no_spark(overhaul):
    card = load("proto_ko_pocket_match")
    assert card.cost == 0 and card.type == "attack" and card.rarity == "common"
    assert card.retain is True
    assert combat.spark_cost(card) == 0
    assert klee_overhaul.is_set_off_card(card)
    up = load("proto_ko_pocket_match+")
    assert [fx.get("damage") for fx in card.effects] == [3]
    assert [fx.get("damage") for fx in up.effects] == [5]


def test_pocket_match_fires_only_the_largest_charge_and_the_rest_stay(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    for size in (4, 9, 6):
        klee_overhaul.place(state, enemy, size)
    sparks = state.player.sparks

    play(state, load("proto_ko_pocket_match"), aim=enemy)

    assert sizes(enemy) == [4, 6], "only the 9 went off"
    assert 200 - enemy.hp == 9 + 3, "the charge, then the card's own 3"
    assert state.player.sparks == sparks + 1, "a normal explosion pays 1 Spark"
    assert state.ko_set_off_this_turn == 1
    # The two left behind keep growing like any other charge.
    klee_overhaul.turn_start(state)
    assert sizes(enemy) == [4 + C.KLEE_OVERHAUL_BOMB_GROWTH,
                            6 + C.KLEE_OVERHAUL_BOMB_GROWTH]


def test_pocket_match_breaks_a_tie_to_the_oldest_charge(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 7, is_mine=True)
    klee_overhaul.place(state, enemy, 3)
    klee_overhaul.place(state, enemy, 7)
    play(state, load("proto_ko_pocket_match"), aim=enemy)
    assert sizes(enemy) == [3, 7]
    assert klee_overhaul.mine_count(enemy) == 0, "the OLDEST 7, the Mine, went"


def test_pocket_matchs_mine_answers_frags_and_second_surprise(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.MINE_FRAGS] = 2
    state.player.powers[klee_overhaul.SECOND_SURPRISE] = 1
    klee_overhaul.place(state, enemy, 3)
    klee_overhaul.place(state, enemy, 8, is_mine=True)
    play(state, load("proto_ko_pocket_match"), aim=enemy)
    assert enemy.powers.get("vulnerable", 0) == 2
    # Second Surprise's half-size Bomb joins the 3 that stayed.
    assert sorted(sizes(enemy)) == [3, 4]


def test_pocket_match_kill_sends_the_rest_of_the_pile_to_a_survivor(overhaul):
    a, b = make_enemy(hp=8, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 5)
    klee_overhaul.place(state, a, 10)
    play(state, load("proto_ko_pocket_match"), aim=a)
    assert not a.alive
    assert sizes(b) == [5], "the charge left behind jumped"


def test_pocket_match_is_a_set_off_card_to_every_reader(overhaul):
    """Once More!, Grounded, Patience Klee!, Where Did I Put It? and Treasure
    Map all read `is_set_off_card` / the Set off card note."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 5)
    card = load("proto_ko_pocket_match")
    play(state, card, aim=enemy)
    assert state.ko_set_off_cards_this_turn == 1
    assert state.ko_last_set_off_card is card


def test_pocket_match_on_an_empty_enemy_is_just_its_hit(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, b, 9)
    play(state, load("proto_ko_pocket_match"), aim=a)
    assert 200 - a.hp == 3
    assert sizes(b) == [9], "another enemy's pile is not this card's"


# ---------------------------------------------------------------------------
# BOOM BADGE: "The next time you Set off this turn, your Bombs deal double."
# ---------------------------------------------------------------------------

def test_boom_badge_prices_two_sparks_and_one_upgraded(overhaul):
    card, up = load("proto_ko_boom_badge"), load("proto_ko_boom_badge+")
    assert card.cost == 0
    assert combat.spark_cost(card) == 2
    assert combat.spark_cost(up) == 1


def test_boom_badge_doubles_the_bombs_of_the_next_set_off(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.sparks = 2
    play(state, load("proto_ko_boom_badge"))
    assert state.player.powers.get(klee_overhaul.BOOM_BADGE) == 1
    klee_overhaul.place(state, enemy, 5)
    play(state, load("proto_ko_kapow"), aim=enemy)
    assert 200 - enemy.hp == 5 * 2 + 4, "the Bomb doubled; Ka-pow!'s 4 did not"
    assert klee_overhaul.BOOM_BADGE not in state.player.powers

    # Spent: the next Set off is plain again.
    before = enemy.hp
    klee_overhaul.place(state, enemy, 5)
    play(state, load("proto_ko_kapow"), aim=enemy)
    assert before - enemy.hp == 5 + 4


def test_boom_badge_and_the_big_one_multiply_to_eight(overhaul):
    enemy = make_enemy(hp=500)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.BOOM_BADGE] = 1
    klee_overhaul.place(state, enemy, 5)
    play(state, load("proto_ko_the_big_one"), aim=enemy)
    assert 500 - enemy.hp == 5 * 8


def test_boom_badge_doubles_every_enemy_one_set_off_card_reaches(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    state.player.sparks = 3
    state.player.powers[klee_overhaul.BOOM_BADGE] = 1
    klee_overhaul.place(state, a, 5)
    klee_overhaul.place(state, b, 6)
    play(state, load("proto_ko_tinder_toss"))
    assert 200 - a.hp == 5 * 2 + 3
    assert 200 - b.hp == 6 * 2 + 3


def test_boom_badge_doubles_pocket_matchs_one_charge(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.BOOM_BADGE] = 1
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.place(state, enemy, 9)
    play(state, load("proto_ko_pocket_match"), aim=enemy)
    assert 200 - enemy.hp == 9 * 2 + 3
    assert sizes(enemy) == [4]


def test_two_badges_double_the_same_next_set_off_twice(overhaul):
    assert klee_overhaul.boom_badge_factor(0) == 1
    assert klee_overhaul.boom_badge_factor(1) == 2
    assert klee_overhaul.boom_badge_factor(2) == 4


def test_a_mine_answering_an_attack_does_not_spend_the_badge(overhaul):
    enemy = make_enemy(hp=200, intents=ATTACKER)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.BOOM_BADGE] = 1
    klee_overhaul.place(state, enemy, 5, is_mine=True)
    klee_overhaul.mines_answer_attack(state, enemy)
    assert 200 - enemy.hp == 5
    assert state.player.powers.get(klee_overhaul.BOOM_BADGE) == 1


def test_boom_badge_expires_at_the_end_of_the_turn(overhaul):
    state = klee_state()
    state.player.powers[klee_overhaul.BOOM_BADGE] = 1
    klee_overhaul._turn_end_expansion(state)
    assert klee_overhaul.BOOM_BADGE not in state.player.powers


def test_boom_badge_no_longer_replays_a_card(overhaul):
    import inspect
    assert "take_boom_badge" not in inspect.getsource(combat)


# ---------------------------------------------------------------------------
# SPARK KNIGHT: cost 1, "deal 3 damage to ALL enemies" per Spark gained
# ---------------------------------------------------------------------------

def test_spark_knight_costs_one_and_upgrades_to_four(overhaul):
    card, up = load("proto_ko_spark_knight"), load("proto_ko_spark_knight+")
    assert card.cost == 1
    assert card.effects[0]["amount"] == 3
    assert up.effects[0]["amount"] == 4


def test_spark_knight_hits_every_enemy_once_per_spark(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    state.player.powers[klee_overhaul.SPARK_KNIGHT] = 3
    effects.gain_sparks(state, 2, source="test")
    assert 200 - a.hp == 6
    assert 200 - b.hp == 6


# ---------------------------------------------------------------------------
# THE TWO COMPANION ROWS THAT HAD NO UPGRADE
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cid", ["proto_mc_lisa_violet_arc",
                                 "proto_mc_sucrose_gust"])
def test_the_two_companion_rows_upgrade_to_draw_two(companions, cid):
    draws = [fx["amount"] for fx in load(cid).effects if fx["op"] == "draw"]
    up = [fx["amount"] for fx in load(cid + "+").effects if fx["op"] == "draw"]
    assert draws == [1] and up == [2]


# ---------------------------------------------------------------------------
# HAIR TRIGGER'S MINES (the playtest's "the mines didn't actually detonate")
# ---------------------------------------------------------------------------

def test_hair_trigger_then_the_enemy_attacks_klee_and_every_mine_fires(overhaul):
    """The owner's board, end to end: charges placed at different times, one
    of them the product of a merge (Careful Arrangement) and one carrying
    Jumpy Dumpty's rider, all converted by Hair Trigger. The enemy's attack
    lands on Klee and every converted Mine goes off before it."""
    enemy = make_enemy(hp=300, name="attacker", intents=ATTACKER)
    other = make_enemy(hp=300, name="other")
    state = klee_state([enemy, other])
    state.player.draw_pile = filler()
    klee_overhaul.place(state, other, 6)
    klee_overhaul.place(state, enemy, 4)
    play(state, load("proto_ko_careful_arrangement"), aim=enemy)
    merged = sizes(enemy)
    assert len(merged) == 1
    klee_overhaul.place(state, enemy, 3)
    klee_overhaul.place(state, enemy, 8, payload_mine_all=2)
    play(state, load("proto_ko_hair_trigger"), aim=enemy)
    assert klee_overhaul.mine_count(enemy) == 3

    fired = sum(merged) + 3 + 8
    before = enemy.hp
    combat._enemy_turn(state, enemy)

    assert before - enemy.hp == fired
    # The rider's Mines landed after the pile went; nothing of the original
    # three is left on it.
    assert all(c.size == 2 for c in enemy.ko_charges)
    assert sum(1 for e in state.log if e.get("event") == "ko_explosion") >= 3


# ---------------------------------------------------------------------------
# KLEE BALANCE REVIEW, pick 4a, 2026-09-25 -- the "This review" table
# ---------------------------------------------------------------------------

def _first(card, op):
    return next(fx for fx in card.effects if fx["op"] == op)


def test_balance_review_numbers(overhaul):
    g = load
    assert _first(g("proto_ko_countdown"), "draw")["amount"] == 2
    assert _first(g("proto_ko_countdown+"), "draw")["amount"] == 3
    assert _first(g("proto_ko_fish_blasting"), "damage")["amount"] == 8
    assert _first(g("proto_ko_fish_blasting+"), "damage")["amount"] == 11
    assert g("proto_ko_where_did_i_put_it").cost == 0
    assert _first(g("proto_ko_stoke_the_fuse"), "grow_largest_bomb")["per_spark"] == 5
    assert _first(g("proto_ko_stoke_the_fuse+"), "grow_largest_bomb")["per_spark"] == 7
    one_more = _first(g("proto_ko_one_more_charge"), "grow_largest")
    assert one_more["amount"] == 8 and one_more["draw_if_at_least"] == 20
    assert _first(g("proto_ko_one_more_charge+"), "grow_largest")["amount"] == 11
    wait, wait_up = g("proto_ko_wait_for_it"), g("proto_ko_wait_for_it+")
    assert wait.cost == 0 and wait_up.cost == 0
    assert _first(wait, "apply_power")["amount"] == 2
    assert _first(wait_up, "apply_power")["amount"] == 3
    assert _first(g("proto_ko_party_poppers"), "apply_power")["amount"] == 3
    assert _first(g("proto_ko_party_poppers+"), "apply_power")["amount"] == 4
    assert _first(g("proto_ko_look_out"), "apply_power")["amount"] == 4
    assert _first(g("proto_ko_look_out+"), "apply_power")["amount"] == 6
    assert combat.spark_cost(g("proto_ko_blast_shield")) == 1
    assert combat.spark_cost(g("proto_ko_return_to_sender")) == 0
    for cid, base in (("proto_ko_once_more", 2), ("proto_ko_sparkling_burst", 2),
                      ("proto_ko_blazing_delight", 3)):
        assert combat.spark_cost(g(cid)) == base
        assert combat.spark_cost(g(cid + "+")) == base - 1


def test_wait_for_it_draws_its_stack_and_one_energy(overhaul):
    """The upgrade moves the cards (2 -> 3); the Energy is one per payout."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.draw_pile = filler()
    energy = state.player.energy
    play(state, load("proto_ko_wait_for_it+"))
    assert state.player.powers.get(klee_overhaul.WAIT_FOR_IT) == 3
    enemy.aura = "hydro"
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.set_off(state, enemy)
    assert len(state.player.hand) == 3
    assert state.player.energy == energy + 1
