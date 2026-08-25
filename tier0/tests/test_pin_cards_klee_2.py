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
from tier0.engine.state import Bomb
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

def test_cluster_charge_hits_for_ten_then_arms_a_bomb_on_each_enemy():
    """Cluster Charge deals its 10 damage FIRST and only then arms its
    bombs, so the bombs it places survive the hit that would detonate them:
    the aimed enemy ends at -10 HP holding an armed 5-damage bomb.

    EB-118 §4.2 made it a DISTRIBUTION row -- one Bomb on EACH enemy, where
    it used to roll two at random. The damage half still aims (the card
    keeps `target: enemy` on its attack); only the placement went wide."""
    enemy = make_enemy(hp=60)
    state = make_state(enemies=[enemy])

    _play(state, "cluster_charge")

    assert enemy.hp == 50
    assert [b.damage for b in enemy.bombs] == [5]
    assert [b.element for b in enemy.bombs] == ["pyro"]


def test_cluster_charge_aims_its_damage_but_spreads_its_bombs():
    """The two halves target differently on purpose, which one enemy
    cannot show: the 10 damage lands on the aimed (lowest-HP) enemy alone,
    while every living enemy gets a Bomb."""
    aimed = make_enemy(hp=20, name="aimed")
    other = make_enemy(hp=60, name="other")
    state = make_state(enemies=[aimed, other])

    _play(state, "cluster_charge")

    assert (aimed.hp, other.hp) == (10, 60)
    assert [b.damage for b in aimed.bombs] == [5]
    assert [b.damage for b in other.bombs] == [5]


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


def test_secret_stash_sweeps_for_eight_then_creates_two_free_commons():
    """Secret Stash sweeps the board for 8 and hands you two cards drawn
    from the demolition-common pool, each cost-overridden to 0, exhausting
    itself doing it.

    The 8-to-all body is the R130 dead-card rework (2026-08-07): the card
    was picked 0% in the generic pool and 0% in demolition, its own
    archetype, because a one-shot Exhaust RARE that only hands over two
    commons is a rare slot spent to be two commons. The add clause is
    unchanged -- it is the card's identity -- so this pin covers both the
    new body and the old promise it must not have disturbed.
    """
    enemies = [make_enemy(hp=30), make_enemy(hp=30)]
    state = make_state(enemies=enemies)

    _play(state, "secret_stash", energy=1)

    assert [e.hp for e in enemies] == [22, 22]   # every living enemy, 8 each
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


def test_best_friends_forever_replays_an_upgraded_companion_upgraded():
    """R114/FLAG-2(i): the printed card travels with a copy, and PRINTED
    includes the upgrade.

    The sim expresses it by recording the played card's id -- `foo+` for an
    upgraded companion (combat._finish_play) -- so the replay reloads the
    upgraded sheet row and Barbara's copy still blocks 8. C# had to be taught
    this separately: its ledger stored a base ModelId and `ModelDb.GetById`
    rebuilt the card pristine (BACKLOG BFF-copy).

    One companion, played once: this pins what a copy CARRIES. What counts as
    one pool entry (`foo` vs `foo+`) is BFF-dedupe, ruled 2026-08-06 and
    pinned in the two tests below.
    """
    state = make_state()
    _play(state, "barbara_melody+", energy=1)

    _play(state, "best_friends_forever", energy=1)

    assert [c.id for c in state.player.hand] == ["barbara_melody+"]
    replay = state.player.hand[0]
    assert replay.cost == 0                     # the card's own cost_override
    assert replay.effects == loader.get_card("barbara_melody+").effects
    assert [e["amount"] for e in replay.effects if e["op"] == "block"] == [8]


def test_an_upgraded_companion_is_the_same_pool_entry_as_its_base():
    """BFF-dedupe, RULED 2026-08-06: an upgraded companion IS the same pool
    entry as its base -- Best Friends Forever replays each companion once, no
    surprise duplication.

    The sim used to disagree with the shipped C# here: it recorded INSTANCE
    ids, so `barbara_melody` and `barbara_melody+` were two entries and the
    pool handed back two Barbaras. The ruling made C# (dedupe on the base
    ModelId, at the record site) the correct behaviour, and the sim now
    strips the `+` when it records.

    Base first, so the entry kept is the un-upgraded one: 6 Block, not 8.
    """
    state = make_state()
    _play(state, "barbara_melody", energy=1)
    _play(state, "barbara_melody+", energy=1)

    _play(state, "best_friends_forever", energy=1)

    assert [c.id for c in state.player.hand] == ["barbara_melody"]
    replay = state.player.hand[0]
    assert replay.cost == 0
    assert [e["amount"] for e in replay.effects if e["op"] == "block"] == [6]


def test_the_pool_entry_keeps_the_first_plays_upgrade_state():
    """The other order, and the half of BFF-dedupe that decides what the one
    copy CARRIES (2026-08-06 ruling; R114/FLAG-2(i) for the copy state).

    Upgraded first, so the single entry is the upgraded one and the copy
    blocks 8 -- the base play that follows does not downgrade it. This is C#
    exactly: `CompanionPlays.Record` adds `(owner, card.Id, card.IsUpgraded)`
    on the FIRST play and the `(Owner, Id)` guard drops every later play of
    the same base card, upgraded or not.
    """
    state = make_state()
    _play(state, "barbara_melody+", energy=1)
    _play(state, "barbara_melody", energy=1)

    _play(state, "best_friends_forever", energy=1)

    assert [c.id for c in state.player.hand] == ["barbara_melody+"]
    replay = state.player.hand[0]
    assert replay.cost == 0
    assert [e["amount"] for e in replay.effects if e["op"] == "block"] == [8]


def test_two_different_companions_are_still_two_pool_entries():
    """The dedupe is per COMPANION, not a global cap: BFF-dedupe collapses
    `foo`/`foo+`, and nothing else. Pinned beside the two above so a future
    key change (say, deduping on something coarser) cannot pass by making
    the pool smaller everywhere.
    """
    state = make_state()
    _play(state, "barbara_melody", energy=1)
    _play(state, "fischl_oz", energy=1)

    _play(state, "best_friends_forever", energy=1)

    assert [c.id for c in state.player.hand] == ["barbara_melody", "fischl_oz"]


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


# --- R208 / W2b ratified body: Sparkly Explosion ---

def test_sparkly_explosion_gathers_detonates_at_plus_three_then_swings():
    """R208's W2b body, in the ruled ORDER: move every Bomb on the board onto
    the target, detonate that target's pile at +3 each, and only then deal 14.

    The order is the whole ruling. Klee's implicit pop is guarded on the
    target surviving AND on hp damage being nonzero, so a detonation placed
    AFTER the swing is thrown away on a kill or against Block; an explicit
    `detonate` placed before it is immune to both.
    """
    left = make_enemy(hp=200, name="left")
    right = make_enemy(hp=100, name="right")
    right.bombs.append(Bomb(damage=6))
    state = make_state(enemies=[left, right])
    left.bombs.append(Bomb(damage=5))
    left.bombs.append(Bomb(damage=5))

    _play(state, "sparkly_explosion")

    # All three ops resolve against ONE creature -- the aim bound at card-play
    # construction, `right` at 100 HP -- so the board's Bombs gather there,
    # pop at +3 each (5+3, 5+3, 6+3 = 25) and the 14 lands on the same body.
    # EB-136 / R210 (`C18`) is what makes that a STATEMENT rather than a
    # coincidence: before the binding each op re-picked the lowest-HP living
    # enemy independently and agreed here only because nothing died mid-card.
    # The kill case is pinned in `test_eb136_same_target_binding.py`, and the
    # DIAGNOSTIC caveat this comment used to carry is cleared.
    assert right.hp == 100 - 25 - 14
    assert left.hp == 200
    assert left.bombs == [] and right.bombs == []


def test_sparkly_explosion_is_a_plain_fourteen_on_an_empty_board():
    """The measured floor of the ruled body: with no Bombs anywhere,
    `move_bombs` moves nothing, `detonate` does nothing, and the card
    resolves as a 14-damage two-cost Rare."""
    enemy = make_enemy(hp=100)
    state = make_state(enemies=[enemy])

    _play(state, "sparkly_explosion")

    assert enemy.hp == 86
    assert enemy.bombs == []
    assert state.player.sparks == 0        # the gain_spark rider is gone


def test_sparkly_explosion_upgrade_moves_the_printed_damage_only():
    """`{damage: +5}` runs `_bump_first` over top-level damage effects, so
    14 -> 19 and neither the gather nor the detonation bonus moves."""
    up = loader.get_card("sparkly_explosion+")
    assert up.effects == [
        {"op": "move_bombs", "target": "enemy"},
        {"op": "detonate", "target": "enemy", "bonus": 3},
        {"op": "damage", "amount": 19, "target": "enemy"}]
    assert up.archetypes == ["demolition"]     # the spark tag stays dropped
