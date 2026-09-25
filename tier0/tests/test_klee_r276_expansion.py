"""THE R276 POOL EXPANSION (QUARANTINED, `C.KLEE_OVERHAUL`) -- thirty rows
toward the 78-card pool R276 ruled, designed by the main session and built as
specified.

The C# is FIRST and this is its twin, case for case with
`klee-mod/KleeTests/Prototype/KleeR276ExpansionTests.cs`: where a pin is
STRUCTURAL there (a hit, a placement, a draw, a pile move needs a live combat
the headless harness does not have), it is a real board here, which is the
point of having a twin at all.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): every number is a starting value.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, klee_overhaul
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards

EXPANSION = C.KLEE_OVERHAUL_POOL_IDS[-30:]


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
    """Resolve a card's body, aimed at `aim` when it aims."""
    if aim is not None:
        state.card_aim, state.card_aim_bound = aim, True
    effects.resolve_card(state, card)


def friend(cid="proto_mc_friend", ctype="skill", cost=1):
    """A Companion card by the sheet's own mark (`role_c`)."""
    card = Card(id=cid, name="friend", cost=cost, type=ctype, effects=[])
    card.role_c = "applier"
    return card


def filler(n=5):
    return [Card(id=f"filler{i}", name="filler", cost=1, type="skill",
                 effects=[]) for i in range(n)]


# ---------------------------------------------------------------------------
# THE POOL
# ---------------------------------------------------------------------------

def test_the_thirty_are_the_specs_rows_at_the_specs_shape(overhaul):
    rows = {cid: load(cid) for cid in EXPANSION}
    assert len(rows) == 30
    by_rarity = {}
    for card in rows.values():
        by_rarity[card.rarity] = by_rarity.get(card.rarity, 0) + 1
    assert by_rarity == {"common": 2, "uncommon": 18, "rare": 10}
    shape = {cid: (c.cost, c.type) for cid, c in rows.items()}
    assert shape["proto_ko_hiding_spot"] == (1, "skill")
    assert shape["proto_ko_fish_fry"] == (2, "attack")
    assert shape["proto_ko_half_a_mountain"] == (1, "skill")
    assert shape["proto_ko_alices_detonator"] == (1, "power")
    assert shape["proto_ko_second_surprise"] == (1, "power")
    assert shape["proto_ko_dodoco"] == (2, "power")
    assert not rows["proto_ko_half_a_mountain"].exhaust
    assert rows["proto_ko_sit_tight"].retain
    assert rows["proto_ko_wait_for_it"].retain
    assert rows["proto_ko_tag_along"].exhaust
    assert rows["proto_ko_adventure_club"].exhaust


def test_every_expansion_row_and_its_upgrade_resolves(overhaul):
    """Played against a loaded board -- two enemies, a Bomb and a Mine, a
    bank, a draw pile, a Set off card and a Companion card in the discard --
    every row and every `+` row resolves without raising."""
    for cid in EXPANSION:
        for suffix in ("", "+"):
            a = make_enemy(hp=400, name="a")
            b = make_enemy(hp=400, name="b")
            state = klee_state([a, b])
            state.player.sparks = 5
            state.sparks_at_play = 5
            state.player.draw_pile = filler()
            state.player.discard_pile = [load("proto_ko_kapow"), friend()]
            klee_overhaul.place(state, a, 6)
            klee_overhaul.place(state, b, 4, is_mine=True)
            play(state, load(cid + suffix), aim=a)


# ---------------------------------------------------------------------------
# "YOUR LARGEST BOMB"
# ---------------------------------------------------------------------------

def test_the_largest_bomb_is_the_largest_charge_and_the_older_on_a_tie(
        overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 7)
    klee_overhaul.place(state, a, 7)
    klee_overhaul.place(state, b, 5)
    assert klee_overhaul.grow_largest(state, 5) == 12
    assert sizes(a) == [12, 7] and sizes(b) == [5]


def test_one_more_charge_grows_eight_and_draws_at_twenty(overhaul):
    # Klee balance review, pick 4a, 2026-09-25: 5 -> 8 (11 upgraded).
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.draw_pile = filler()
    klee_overhaul.place(state, enemy, 10)
    play(state, load("proto_ko_one_more_charge"))
    assert sizes(enemy) == [18] and len(state.player.hand) == 0
    play(state, load("proto_ko_one_more_charge"))
    assert sizes(enemy) == [26] and len(state.player.hand) == 1
    # Upgraded: grows 11.
    play(state, load("proto_ko_one_more_charge+"))
    assert sizes(enemy) == [37]


def test_one_more_charge_with_no_bomb_grows_nothing_and_draws_nothing(
        overhaul):
    state = klee_state()
    state.player.draw_pile = filler()
    play(state, load("proto_ko_one_more_charge"))
    assert state.player.hand == []


def test_half_a_mountain_doubles_the_largest_bomb_repeatably(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.place(state, enemy, 9)
    play(state, load("proto_ko_half_a_mountain"))
    play(state, load("proto_ko_half_a_mountain"))
    assert sizes(enemy) == [5, 36]


def test_favonius_escort_removes_the_largest_for_twice_its_size(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.place(state, enemy, 9)
    play(state, load("proto_ko_favonius_escort"))
    assert sizes(enemy) == [5]
    assert state.player.block == 18


# ---------------------------------------------------------------------------
# THE HITS
# ---------------------------------------------------------------------------

def test_mk_iii_hits_three_times_and_plants_a_bomb_per_hit(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    play(state, load("proto_ko_jumpy_dumpty_mk_iii"))
    assert sum(len(e.ko_charges) for e in (a, b)) == 3
    assert all(s == 2 for e in (a, b) for s in sizes(e))
    assert (200 - a.hp) + (200 - b.hp) >= 9


def test_mk_iii_upgraded_hits_four_and_plants_three(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_jumpy_dumpty_mk_iii+"))
    assert sizes(enemy) == [3, 3, 3]


def test_spinning_sparkler_grows_the_bomb_on_each_hit(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 3)
    klee_overhaul.place(state, enemy, 7)
    play(state, load("proto_ko_spinning_sparkler"), aim=enemy)
    assert sizes(enemy) == [3, 11]
    assert enemy.hp < 200
    # A plain Attack: nothing went off.
    assert state.ko_set_off_this_turn == 0


def test_spinning_sparkler_grows_nothing_on_a_bombless_enemy(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_spinning_sparkler"), aim=enemy)
    assert sizes(enemy) == []


def test_mine_all_mine_hits_only_the_mined_enemies(overhaul):
    a, b, c = (make_enemy(hp=200, name=n) for n in "abc")
    state = klee_state([a, b, c])
    klee_overhaul.place(state, a, 4, is_mine=True)
    klee_overhaul.place(state, b, 9)
    play(state, load("proto_ko_mine_all_mine"))
    assert a.hp < 200
    assert b.hp == 200 and c.hp == 200


def test_fish_fry_adds_the_bonus_to_bombed_enemies_only(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 2)
    play(state, load("proto_ko_fish_fry"))
    assert (200 - a.hp) - (200 - b.hp) == 5


def test_team_effort_sets_off_the_target_alone_without_a_companion(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 5)
    klee_overhaul.place(state, b, 5)
    play(state, load("proto_ko_team_effort"), aim=a)
    assert sizes(a) == [] and sizes(b) == [5]


def test_team_effort_sets_off_every_enemy_after_a_companion_play(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 5)
    klee_overhaul.place(state, b, 5)
    state.ko_companion_this_turn = 1
    play(state, load("proto_ko_team_effort"), aim=a)
    assert sizes(a) == [] and sizes(b) == []
    # The card's own 6 lands on the target only: b took its Bomb and no more.
    assert 200 - b.hp == 5
    assert 200 - a.hp > 200 - b.hp


def test_windblume_fireworks_sets_off_then_hits_then_plants(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    klee_overhaul.place(state, a, 5)
    play(state, load("proto_ko_windblume_fireworks"))
    assert sizes(a) == [6] and sizes(b) == [6]
    assert 200 - b.hp == 10
    assert 200 - a.hp == 15


def test_fireworks_finale_hits_once_per_spark_spent(overhaul):
    a, b = make_enemy(hp=200, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    state.player.sparks = 3
    state.player.hand = [load("proto_ko_fireworks_finale")]
    combat.play_card(state, state.player.hand[0])
    assert state.player.sparks == 0
    assert 200 - b.hp == 15


def test_fireworks_finale_is_unplayable_at_an_empty_bank(overhaul):
    state = klee_state()
    state.player.sparks = 0
    assert combat.spark_cost(load("proto_ko_fireworks_finale")) == 1


def test_duck_and_run_blocks_and_sets_off(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 6)
    play(state, load("proto_ko_duck_and_run"), aim=enemy)
    assert state.player.block == 7 and sizes(enemy) == []


def test_hiding_spot_blocks_and_places_a_mine(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_hiding_spot+"))
    assert state.player.block == 8
    assert sizes(enemy) == [5] and klee_overhaul.mine_count(enemy) == 1


# ---------------------------------------------------------------------------
# THE COMPANION ROUTE
# ---------------------------------------------------------------------------

def test_playdate_takes_one_off_the_next_companion_card(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    buddy = friend(cost=2)
    play(state, load("proto_ko_playdate"), aim=enemy)
    assert sizes(enemy) == [3]
    assert combat.card_cost(state, buddy) == 1
    assert combat.card_cost(state, load("proto_ko_pop")) == 0
    klee_overhaul.spend_playdate(state, buddy)
    assert combat.card_cost(state, buddy) == 2


def test_playdate_expires_at_the_end_of_the_turn(overhaul):
    state = klee_state()
    state.player.powers[klee_overhaul.PLAYDATE] = 1
    klee_overhaul.turn_end(state)
    assert klee_overhaul.PLAYDATE not in state.player.powers


def test_treasure_map_fetches_a_set_off_card_and_grows(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    kapow, pop = load("proto_ko_kapow"), load("proto_ko_pop")
    state.player.discard_pile = [pop, kapow]
    klee_overhaul.place(state, enemy, 4)
    play(state, load("proto_ko_treasure_map"))
    assert state.player.hand == [kapow]
    assert state.player.discard_pile == [pop]
    assert sizes(enemy) == [7]


def test_treasure_map_with_no_set_off_card_still_grows(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.discard_pile = [load("proto_ko_pop")]
    klee_overhaul.place(state, enemy, 4)
    play(state, load("proto_ko_treasure_map"))
    assert state.player.hand == [] and sizes(enemy) == [7]


def test_come_back_and_play_fetches_a_companion_and_the_upgrade_draws(
        overhaul):
    state = klee_state()
    buddy = friend()
    state.player.discard_pile = [load("proto_ko_pop"), buddy]
    state.player.draw_pile = filler()
    play(state, load("proto_ko_come_back_and_play+"))
    assert buddy in state.player.hand and len(state.player.hand) == 2


def test_tag_along_and_adventure_club_add_free_companions(overhaul):
    state = klee_state()
    play(state, load("proto_ko_tag_along"))
    assert len(state.player.hand) == 1
    assert state.player.hand[0].is_companion
    assert state.player.hand[0].free_this_turn
    play(state, load("proto_ko_adventure_club"))
    assert len(state.player.hand) == 3
    assert all(c.free_this_turn for c in state.player.hand)


def test_friendship_bracelet_grows_the_largest_bomb_per_companion_play(
        overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.FRIENDSHIP_BRACELET] = 3
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.note_card_played(state, friend())
    klee_overhaul.note_card_played(state, load("proto_ko_pop"))
    assert sizes(enemy) == [7]


# ---------------------------------------------------------------------------
# THE SPARK-SUPPORTED COOK
# ---------------------------------------------------------------------------

def test_boom_badge_doubles_the_bombs_of_the_next_set_off_card(overhaul):
    # Playtest 2026-09-24 ([USER]: "seems weak"): the old replay found the
    # Bombs gone; the badge now doubles them, and costs 2 Sparks.
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.sparks = 2
    state.player.hand = [load("proto_ko_boom_badge"), load("proto_ko_pop"),
                         load("proto_ko_kapow")]
    combat.play_card(state, state.player.hand[0])
    assert state.player.sparks == 0
    # Pop! is not a Set off card: the badge waits.
    combat.play_card(state, state.player.hand[0])
    assert state.player.powers.get(klee_overhaul.BOOM_BADGE) == 1
    before = enemy.hp
    combat.play_card(state, state.player.hand[0])
    assert klee_overhaul.BOOM_BADGE not in state.player.powers
    # The Bomb 5 went off doubled, once; Ka-pow!'s own 4 landed once.
    assert before - enemy.hp == 5 * 2 + 4


def sit_tight_board():
    """One enemy holding a Bomb 5, and a bank for Sit Tight's Spark."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.sparks = 2
    klee_overhaul.place(state, enemy, 5)
    return state, enemy


def test_sit_tight_then_kapow_pays_no_bonus(overhaul):
    state, enemy = sit_tight_board()
    play(state, load("proto_ko_sit_tight"))
    assert state.player.block == 5
    play(state, load("proto_ko_kapow"), aim=enemy)
    klee_overhaul.sit_tight_turn_end(state)
    assert state.player.block == 5
    assert klee_overhaul.SIT_TIGHT not in state.player.powers


def test_kapow_then_sit_tight_pays_no_bonus(overhaul):
    state, enemy = sit_tight_board()
    play(state, load("proto_ko_kapow"), aim=enemy)
    play(state, load("proto_ko_sit_tight"))
    klee_overhaul.sit_tight_turn_end(state)
    assert state.player.block == 5


def test_sit_tight_with_no_detonation_pays_at_the_end_of_the_turn(overhaul):
    state, enemy = sit_tight_board()
    play(state, load("proto_ko_sit_tight"))
    # The bonus is not paid at play time any more.
    assert state.player.block == 5
    klee_overhaul.sit_tight_turn_end(state)
    assert state.player.block == 5 + 4
    assert klee_overhaul.SIT_TIGHT not in state.player.powers
    assert sizes(enemy) == [5]


def test_sit_tight_is_switched_off_by_a_mine_answering_an_attack(overhaul):
    state, enemy = sit_tight_board()
    klee_overhaul.place(state, enemy, 3, is_mine=True)
    play(state, load("proto_ko_sit_tight"))
    klee_overhaul.mines_answer_attack(state, enemy)
    klee_overhaul.sit_tight_turn_end(state)
    assert state.player.block == 5


def test_sit_tight_copies_each_pay(overhaul):
    state, _ = sit_tight_board()
    play(state, load("proto_ko_sit_tight"))
    play(state, load("proto_ko_sit_tight"))
    klee_overhaul.sit_tight_turn_end(state)
    assert state.player.block == 5 + 5 + 4 + 4


def test_sit_tight_upgraded_is_seven_and_five(overhaul):
    state = klee_state()
    state.player.sparks = 1
    play(state, load("proto_ko_sit_tight+"))
    assert state.player.block == 7
    klee_overhaul.sit_tight_turn_end(state)
    assert state.player.block == 12


def test_sit_tight_pays_before_the_shipped_turn_end_triggers():
    """The mod pays it as a POWER tenant of `BeforeSideTurnEnd`, ahead of the
    model-driven `TurnEndSequencer`; the sim's call sits ahead of
    `player_turn_end_triggers` for the same reason."""
    import inspect
    body = inspect.getsource(combat._player_turn)
    assert (body.index("klee_overhaul.sit_tight_turn_end(state)")
            < body.index("effects.player_turn_end_triggers(state)"))


def test_wait_for_it_pays_once_on_a_reacting_bomb(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.draw_pile = filler()
    energy = state.player.energy
    play(state, load("proto_ko_wait_for_it"))
    enemy.aura = "hydro"
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.set_off(state, enemy)
    assert len(state.player.hand) == 2
    assert state.player.energy == energy + 1
    assert klee_overhaul.WAIT_FOR_IT not in state.player.powers


def test_wait_for_it_ignores_a_plain_explosion_and_expires(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    play(state, load("proto_ko_wait_for_it"))
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.set_off(state, enemy)
    assert klee_overhaul.WAIT_FOR_IT in state.player.powers
    klee_overhaul.turn_end(state)
    assert klee_overhaul.WAIT_FOR_IT not in state.player.powers


def test_party_poppers_pays_a_bomb_per_spark_priced_play(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.PARTY_POPPERS] = 3
    # Pocket Match lost its price on 2026-09-24; Tinder Toss still charges 1.
    klee_overhaul.note_card_played(state, load("proto_ko_tinder_toss"))
    klee_overhaul.note_card_played(state, load("proto_ko_fireworks_finale"))
    klee_overhaul.note_card_played(state, load("proto_ko_pop"))
    klee_overhaul.note_card_played(state, load("proto_ko_pocket_match"))
    assert sizes(enemy) == [3, 3]


def test_patience_grows_on_a_turn_with_no_set_off_card_after_the_echo(
        overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.PATIENCE] = 4
    state.player.powers[klee_overhaul.BOMB_ECHO] = 1
    klee_overhaul.place(state, enemy, 5)
    klee_overhaul.turn_end(state)
    # The echo paid the 5, THEN Patience grew it.
    assert 200 - enemy.hp == 5
    assert sizes(enemy) == [9]
    state.ko_set_off_cards_this_turn = 1
    klee_overhaul.turn_end(state)
    assert sizes(enemy) == [9]


# ---------------------------------------------------------------------------
# START OF TURN
# ---------------------------------------------------------------------------

def test_secret_base_reads_the_board_before_dodocos_mine(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.turn = 2
    state.player.powers[klee_overhaul.SECRET_BASE] = 5
    state.player.powers[klee_overhaul.DODOCO] = 4
    klee_overhaul.turn_start_late(state)
    assert sizes(enemy) == [5, 4]
    assert klee_overhaul.mine_count(enemy) == 1
    klee_overhaul.turn_start_late(state)
    # A Bomb is on the board now: no second Secret Base Bomb.
    assert sizes(enemy) == [5, 4, 4]


def test_alices_detonator_adds_a_kapow_and_the_plus_an_upgraded_one(
        overhaul):
    state = klee_state()
    state.turn = 2
    play(state, load("proto_ko_alices_detonator"))
    play(state, load("proto_ko_alices_detonator+"))
    klee_overhaul.turn_start_late(state)
    ids = sorted(c.id for c in state.player.hand)
    assert ids == ["proto_ko_kapow", "proto_ko_kapow+"]


# ---------------------------------------------------------------------------
# THE EXPLOSION'S CHARGE-AWARE DOOR
# ---------------------------------------------------------------------------

def test_look_out_blocks_when_a_mine_goes_off(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.LOOK_OUT] = 3
    klee_overhaul.place(state, enemy, 4)
    klee_overhaul.set_off(state, enemy)
    assert state.player.block == 0
    klee_overhaul.place(state, enemy, 4, is_mine=True)
    klee_overhaul.mines_answer_attack(state, enemy)
    assert state.player.block == 3


def test_second_surprise_leaves_half_a_mine_on_its_enemy(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.SECOND_SURPRISE] = 1
    klee_overhaul.place(state, enemy, 7, is_mine=True)
    klee_overhaul.mines_answer_attack(state, enemy)
    assert sizes(enemy) == [3]
    assert klee_overhaul.mine_count(enemy) == 0
    # Half of 1 is 0: nothing placed.
    klee_overhaul.take_all(enemy)
    klee_overhaul.place(state, enemy, 1, is_mine=True)
    klee_overhaul.set_off(state, enemy)
    assert sizes(enemy) == []


def test_second_surprise_jumps_if_the_mine_killed(overhaul):
    a, b = make_enemy(hp=3, name="a"), make_enemy(hp=200, name="b")
    state = klee_state([a, b])
    state.player.powers[klee_overhaul.SECOND_SURPRISE] = 1
    klee_overhaul.place(state, a, 8, is_mine=True)
    klee_overhaul.set_off(state, a)
    assert not a.alive
    assert sizes(b) == [4]


def test_aftershock_copies_the_first_reacting_bomb_each_turn(overhaul):
    enemy = make_enemy(hp=400)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.AFTERSHOCK] = 1
    enemy.aura = "hydro"
    klee_overhaul.place(state, enemy, 6)
    klee_overhaul.set_off(state, enemy)
    assert sizes(enemy) == [6]
    enemy.aura = "hydro"
    klee_overhaul.set_off(state, enemy)
    assert sizes(enemy) == []          # once per turn


def test_spark_knight_hits_once_per_spark_gained(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.SPARK_KNIGHT] = 2
    effects.gain_sparks(state, 3, source="test")
    assert 200 - enemy.hp == 6


def test_spark_knight_hit_leaves_hydro_standing(overhaul):
    """No element: the Hydro a companion laid down survives the hit, applies
    no Pyro and triggers no reaction (a Vaporize would have amplified it)."""
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    enemy.aura = "hydro"
    enemy.aura_turns_left = 2
    state.player.powers[klee_overhaul.SPARK_KNIGHT] = 2
    effects.gain_sparks(state, 1, source="test")
    assert enemy.aura == "hydro"
    assert 200 - enemy.hp == 2
    assert not any(e.get("event") == "reaction" for e in state.log
                   if isinstance(e, dict))


def test_spark_knight_hit_applies_no_aura(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    state.player.powers[klee_overhaul.SPARK_KNIGHT] = 2
    effects.gain_sparks(state, 1, source="test")
    assert enemy.aura is None
