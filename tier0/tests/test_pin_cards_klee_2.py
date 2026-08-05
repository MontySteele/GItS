"""Behavioural pins for twelve Klee card rows that no test drove before.

Each test plays one real sheet card through combat.play_card against a
minimal combat and asserts the observable result: damage landed, bombs
armed, block gained, sparks banked, powers stuck on the enemy, cards
created and where they went. The rules pinned here are the ones a player
reads off the card, so a silent change to an op's arithmetic, its target
spec, or its ordering has to break a test before it can ship.
"""

from tier0.content import loader
from tier0.engine import combat
from tier0.tests.conftest import make_enemy, make_state


def _play(state, card_id, energy=3):
    """Put the real card in hand with energy to spare and play it."""
    card = loader.get_card(card_id)
    state.player.energy = energy
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


# --- demolition ---

def test_cluster_charge_hits_for_ten_then_arms_two_five_damage_bombs():
    """Cluster Charge deals its 10 damage FIRST and only then arms its two
    bombs, so the bombs it places survive the hit that would detonate them:
    the enemy ends at -10 HP holding two armed 5-damage bombs."""
    enemy = make_enemy(hp=60)
    state = make_state(enemies=[enemy])

    _play(state, "cluster_charge")

    assert enemy.hp == 50
    assert [b.damage for b in enemy.bombs] == [5, 5]
    assert [b.element for b in enemy.bombs] == ["pyro", "pyro"]


def test_all_my_treasures_arms_six_bombs_and_banks_two_sparks():
    """All of My Treasures! is pure setup: six 6-damage bombs and 2 Sparks,
    with no damage of its own, and the card exhausts on play."""
    enemy = make_enemy(hp=80)
    state = make_state(enemies=[enemy])

    card = _play(state, "all_my_treasures")

    assert enemy.hp == 80                      # no damage op on the row
    assert [b.damage for b in enemy.bombs] == [6] * 6
    assert state.player.sparks == 2
    assert [c.id for c in state.player.exhaust_pile] == ["all_my_treasures"]
    assert card not in state.player.hand


def test_secret_stash_creates_two_free_demolition_commons_in_hand():
    """Secret Stash hands you two cards drawn from the demolition-common
    pool, each cost-overridden to 0, and exhausts itself doing it."""
    state = make_state()

    _play(state, "secret_stash", energy=1)

    pool_ids = {c.id for c in loader.cards_in_pool("demolition_commons")}
    assert len(state.player.hand) == 2
    assert all(c.id in pool_ids for c in state.player.hand)
    assert [c.cost for c in state.player.hand] == [0, 0]
    assert [ev["to"] for ev in _events(state, "add_card")] == ["hand", "hand"]
    assert [c.id for c in state.player.exhaust_pile] == ["secret_stash"]


# --- spark ---

def test_flame_on_the_wick_deals_a_flat_six_for_zero_energy():
    """Flame on the Wick is a free 6-damage poke: it costs nothing, so the
    energy bank is untouched and the enemy simply loses 6 HP."""
    enemy = make_enemy(hp=40)
    state = make_state(enemies=[enemy])

    _play(state, "flame_on_the_wick", energy=2)

    assert enemy.hp == 34
    assert state.player.energy == 2            # printed cost 0, nothing paid


def test_cant_catch_me_gives_two_block_one_spark_and_one_card():
    """Can't Catch Me! pays out all three of its printed lines: 2 Block,
    1 Spark, and one card off the top of the draw pile."""
    state = make_state()
    state.player.draw_pile = [loader.get_card("strike"),
                              loader.get_card("defend")]

    _play(state, "cant_catch_me", energy=1)

    assert state.player.block == 2
    assert state.player.sparks == 1
    assert [c.id for c in state.player.hand] == ["strike"]
    assert len(state.player.draw_pile) == 1


def test_da_da_da_lands_three_separate_four_damage_hits_and_one_spark():
    """Da-da-da! is three discrete 4-damage hits (not one 12), plus a
    Spark, and the card exhausts."""
    enemy = make_enemy(hp=50)
    state = make_state(enemies=[enemy])

    _play(state, "da_da_da", energy=1)

    assert [ev["amount"] for ev in _events(state, "damage")] == [4, 4, 4]
    assert enemy.hp == 38
    assert state.player.sparks == 1
    assert [c.id for c in state.player.exhaust_pile] == ["da_da_da"]


# --- reaction ---

def test_perfect_timing_repeats_itself_only_when_its_own_hit_reacted():
    """Perfect Timing hits for 8 and replays that hit only if the play
    itself triggered an elemental reaction. Off-element, the rider is dead
    and the card is a flat 8; into a Hydro aura the Pyro hit Vaporizes for
    12 and the replay adds a fresh 8 on top."""
    quiet = make_enemy(hp=60)
    state = make_state(enemies=[quiet])

    _play(state, "perfect_timing", energy=1)

    assert quiet.hp == 52                       # 8, no repeat
    assert [ev["fired"] for ev in _events(state, "conditional")] == [False]

    reactive = make_enemy(hp=60)
    reactive.aura = "hydro"
    hot = make_state(enemies=[reactive])
    hot.player.element = "pyro"
    hot.player.cadence = "catalyst"

    _play(hot, "perfect_timing", energy=1)

    assert [ev["fired"] for ev in _events(hot, "conditional")] == [True]
    assert [ev["amount"] for ev in _events(hot, "damage")] == [12, 8]
    assert reactive.hp == 40
    assert reactive.aura == "pyro"              # the replayed hit re-applies


def test_best_friends_forever_copies_each_companion_played_this_combat():
    """Best Friends Forever returns one free copy of every Companion played
    this combat -- once each, however many times it was played -- into hand
    at cost 0, and exhausts itself."""
    state = make_state()
    for _ in range(2):                          # same companion, twice
        _play(state, "barbara_melody", energy=1)

    _play(state, "best_friends_forever", energy=1)

    assert [c.id for c in state.player.hand] == ["barbara_melody"]
    assert state.player.hand[0].cost == 0
    assert [c.id for c in state.player.exhaust_pile] == ["best_friends_forever"]


# --- generic ---

def test_spirited_away_is_a_flat_twelve_block():
    """Spirited Away grants exactly 12 Block and nothing else."""
    state = make_state()

    _play(state, "spirited_away", energy=2)

    assert state.player.block == 12
    assert [ev["amount"] for ev in _events(state, "block")] == [12]


def test_dodge_roll_blocks_six_and_exhausts_one_status_from_hand():
    """Dodge Roll gives 6 Block and eats exactly one STATUS card out of
    hand -- ordinary cards sitting beside it are never the victim."""
    state = make_state()
    keeper = loader.get_card("strike")
    status = loader.get_card("confiscated")
    state.player.hand.extend([keeper, status])

    _play(state, "dodge_roll", energy=1)

    assert state.player.block == 6
    assert [c.id for c in state.player.exhaust_pile] == ["confiscated"]
    assert [c.id for c in state.player.hand] == ["strike"]


def test_surprise_visit_applies_two_vulnerable_to_the_enemy():
    """Surprise Visit is a pure debuff: 2 Vulnerable on the target, no
    damage and no block."""
    enemy = make_enemy(hp=50)
    state = make_state(enemies=[enemy])

    _play(state, "surprise_visit", energy=1)

    assert enemy.powers.get("vulnerable") == 2
    assert enemy.hp == 50
    assert state.player.block == 0


def test_fish_blasting_hits_every_enemy_x_times_and_adds_a_confiscated():
    """Fish Blasting spends the whole energy bank as X, then hits EVERY
    enemy 8 damage X times -- at X=3 that is 24 apiece -- and pays for it
    with a Confiscated status dropped into the discard pile."""
    left, right = make_enemy(hp=100, name="left"), make_enemy(hp=100,
                                                              name="right")
    state = make_state(enemies=[left, right])

    _play(state, "fish_blasting", energy=3)

    assert state.current_x == 3
    assert state.player.energy == 0
    assert left.hp == 76 and right.hp == 76
    # The token is created mid-resolution; the spent card only reaches the
    # pile afterwards, so Confiscated sits UNDER it.
    assert [c.id for c in state.player.discard_pile] == ["confiscated",
                                                         "fish_blasting"]
