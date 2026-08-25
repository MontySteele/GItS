"""Behavioural pins for thirteen Klee card rows that no test drove before.

Each test builds a minimal combat, plays one real sheet card through
combat.play_card, and asserts what a player would read off the card:
damage landed, bombs armed or moved or detonated, Block gained, Sparks
banked, Burst energy metered, Weak stuck on the board, cards drawn and
scried away. The ordering between a card's own rows is pinned too, since
several of these cards only work because their damage resolves before
their bombs are armed.
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

def test_fish_flavored_bait_hits_for_five_and_leaves_its_bomb_armed():
    """Fish-Flavored Bait hits for 5 BEFORE it arms its bomb, so the attack
    that would set the bomb off cannot: the enemy ends 5 HP down and still
    holding one live 5-damage pyro bomb."""
    enemy = make_enemy(hp=40)
    state = make_state(enemies=[enemy])

    _play(state, "fish_flavored_bait")

    assert enemy.hp == 35
    assert [b.damage for b in enemy.bombs] == [5]
    assert [b.element for b in enemy.bombs] == ["pyro"]


def test_ammo_scavenging_arms_one_five_damage_bomb_and_draws_a_card():
    """Ammo Scavenging is pure setup with a cantrip attached: one 5-damage
    bomb on the board and exactly one card off the top of the draw pile,
    with no damage of its own."""
    enemy = make_enemy(hp=40)
    state = make_state(enemies=[enemy])
    state.player.draw_pile = [loader.get_card("strike"),
                              loader.get_card("defend")]

    _play(state, "ammo_scavenging")

    assert enemy.hp == 40                      # no damage op on the row
    assert [b.damage for b in enemy.bombs] == [5]
    assert [c.id for c in state.player.hand] == ["strike"]
    assert len(state.player.draw_pile) == 1


def test_careful_arrangement_gathers_every_other_bomb_onto_one_enemy():
    """Careful Arrangement sweeps the bombs off every OTHER enemy onto the
    aimed one (lowest HP) and pays each moved bomb +2 damage. Bombs already
    sitting on the destination are not moved, so they get no bonus."""
    dest = make_enemy(hp=10, name="dest")
    mid = make_enemy(hp=50, name="mid")
    far = make_enemy(hp=60, name="far")
    dest.bombs = [Bomb(damage=4)]
    mid.bombs = [Bomb(damage=5), Bomb(damage=6)]
    far.bombs = [Bomb(damage=3)]
    state = make_state(enemies=[dest, mid, far])

    _play(state, "careful_arrangement")

    assert [b.damage for b in dest.bombs] == [4, 7, 8, 5]
    assert mid.bombs == []
    assert far.bombs == []
    assert [ev["count"] for ev in _events(state, "bombs_moved")] == [3]


def test_jumpy_dumpty_mk2_lands_two_eights_then_arms_one_bomb_per_enemy():
    """Jumpy Dumpty Mk.II is two discrete 8-damage hits (not one 16), and
    its 6-damage bomb is armed after the hits land, so the card never
    detonates its own payload.

    EB-118 §4.2 made it a DISTRIBUTION row -- one Bomb on EACH enemy, where
    it used to roll two Bombs at random enemies. Against a single enemy
    that is one Bomb and not two: the count is now a fact about the board.
    """
    enemy = make_enemy(hp=60)
    state = make_state(enemies=[enemy])

    _play(state, "jumpy_dumpty_mk2")

    assert [ev["amount"] for ev in _events(state, "damage")] == [8, 8]
    assert enemy.hp == 44
    assert [b.damage for b in enemy.bombs] == [6]


def test_jumpy_dumpty_mk2_arms_every_enemy_when_the_board_is_wide():
    """The other half of the distribution shape, and the reason §4.2 calls
    it a width profile: three enemies, three Bombs, one each. The two-enemy
    median is what the old random roll produced; the tails moved in both
    directions, and only a multi-enemy board can see that."""
    enemies = [make_enemy(hp=60, name=n) for n in ("a", "b", "c")]
    state = make_state(enemies=enemies)

    _play(state, "jumpy_dumpty_mk2")

    assert [[b.damage for b in e.bombs] for e in enemies] == [[6], [6], [6]]


def test_remote_detonator_sets_off_every_board_bomb_at_plus_two_each():
    """Remote Detonator clears the bombs off the WHOLE board at once and
    pays +2 damage per bomb, so a two-bomb enemy takes 5+2 and 4+2 while a
    one-bomb enemy takes 6+2, and no bomb survives."""
    left = make_enemy(hp=30, name="left")
    right = make_enemy(hp=40, name="right")
    left.bombs = [Bomb(damage=5), Bomb(damage=4)]
    right.bombs = [Bomb(damage=6)]
    state = make_state(enemies=[left, right])

    _play(state, "remote_detonator")

    assert [ev["damage"] for ev in _events(state, "bomb_detonation")] == [7, 6, 8]
    assert left.hp == 17
    assert right.hp == 32
    assert left.bombs == [] and right.bombs == []
    assert state.detonations_total == 3


# --- spark ---

def test_spark_collection_banks_exactly_two_sparks():
    """Spark Collection does one thing: it puts 2 Sparks in the bank, in a
    single gain (not two of one)."""
    state = make_state()

    _play(state, "spark_collection")

    assert state.player.sparks == 2
    assert [ev["amount"] for ev in _events(state, "gain_spark")] == [2]


def test_tail_of_flame_adds_its_rider_only_when_the_play_itself_cost_zero():
    """Tail of Flame hits for 5, and pays its extra 4 only when THIS play
    resolved at zero cost. Paid at 1 energy it is a flat 5; freed by the
    Spark threshold (which the attack spends) it is 5 + 4."""
    paid_enemy = make_enemy(hp=40)
    paid = make_state(enemies=[paid_enemy])
    _play(paid, "tail_of_flame", energy=3)

    assert [ev["amount"] for ev in _events(paid, "damage")] == [5]
    assert paid_enemy.hp == 35
    assert paid.player.energy == 2

    free_enemy = make_enemy(hp=40)
    free = make_state(enemies=[free_enemy])
    free.player.sparks = 3
    _play(free, "tail_of_flame", energy=3)

    assert [ev["amount"] for ev in _events(free, "damage")] == [5, 4]
    assert free_enemy.hp == 31
    assert free.player.energy == 3             # spent Sparks, not energy
    assert free.player.sparks == 0


# --- reaction ---

def test_combustion_study_meters_ten_burst_plus_its_skill_tag_and_draws_one():
    """Combustion Study pays 10 Burst energy from its own row and another 5
    for being Skill-tagged, for 15 on a character who has a Burst meter, and
    draws one card. Both Burst rows are gated on the meter existing: with no
    meter the card banks nothing and only its draw happens."""
    state = make_state()
    state.player.burst_max = 100
    state.player.draw_pile = [loader.get_card("strike"),
                              loader.get_card("defend")]

    _play(state, "combustion_study")

    assert state.player.burst_energy == 15
    assert [(ev["source"], ev["amount"])
            for ev in _events(state, "burst_income")] == [("skill_tag", 5),
                                                          ("card", 10)]
    assert [c.id for c in state.player.hand] == ["strike"]

    meterless = make_state()
    meterless.player.draw_pile = [loader.get_card("strike")]

    _play(meterless, "combustion_study")

    assert meterless.player.burst_energy == 0
    assert _events(meterless, "burst_energy") == []
    assert [c.id for c in meterless.player.hand] == ["strike"]


def test_study_of_explosions_pokes_for_four_and_meters_ten_burst_for_free():
    """Study of Explosions costs nothing, throws 4 at a random enemy, then
    meters 5 Burst from its row plus 5 for its Skill tag.

    R130 dead-card rework (2026-08-07): the row used to open with
    `scry_discard 2`, and the card was picked 0% of the time in the generic
    pool AND 0% in its own reaction archetype -- a cost-0 skill whose visible
    half is deck manipulation reads as doing nothing. The scry is gone and a
    small aimed hit takes its place. What did NOT change is what the card is
    FOR: cost 0, and 10 Burst, because `skill_tag` still contributes its +5
    on top of the printed 5. Both halves are asserted here so a retype or a
    tag drop cannot quietly halve the meter.
    """
    enemy = make_enemy(hp=40)
    state = make_state(enemies=[enemy])
    state.player.burst_max = 100

    _play(state, "study_of_explosions", energy=2)

    assert state.player.energy == 2            # printed cost 0
    assert enemy.hp == 36                      # 4, to the only enemy alive
    assert _events(state, "scry_discard") == []
    assert state.player.burst_energy == 10     # printed 5 + skill_tag 5


# --- generic block / utility ---

def test_hide_and_seek_gives_seven_block_and_bins_one_of_the_top_two():
    """Hide and Seek is 7 Block plus a look at the top 2 cards, one of which
    (the worse) goes to the discard pile; the draw pile keeps the other."""
    state = make_state()
    state.player.draw_pile = [loader.get_card("strike"),
                              loader.get_card("defend"),
                              loader.get_card("bash")]

    _play(state, "hide_and_seek")

    assert state.player.block == 7
    assert [ev["card"] for ev in _events(state, "scry_discard")] == ["defend"]
    assert [c.id for c in state.player.draw_pile] == ["strike", "bash"]
    assert state.player.discard_pile[0].id == "defend"
    assert state.player.hand == []             # a scry is not a draw


def test_spooked_gives_three_block_and_weakens_the_whole_board():
    """Spooked! is 3 Block and 1 Weak on EVERY living enemy, not just the
    aimed one."""
    left = make_enemy(hp=30, name="left")
    right = make_enemy(hp=40, name="right")
    state = make_state(enemies=[left, right])

    _play(state, "spooked")

    assert state.player.block == 3
    assert left.powers == {"weak": 1}
    assert right.powers == {"weak": 1}
    assert left.hp == 30 and right.hp == 40    # no damage on the row


def test_run_away_gives_four_block_for_no_energy():
    """Run Away! is a free 4 Block: the energy bank is untouched and nothing
    else on the board moves."""
    enemy = make_enemy(hp=30)
    state = make_state(enemies=[enemy])

    _play(state, "run_away", energy=1)

    assert state.player.block == 4
    assert state.player.energy == 1            # printed cost 0
    assert enemy.hp == 30


def test_imaginary_friend_gives_five_block_and_eight_burst_energy():
    """Imaginary Friend (clockwork_toy) is 5 Block plus 3 Burst energy from
    its own row, on top of the 5 every Skill-tagged card meters — 8 in
    total for a character with a Burst meter."""
    state = make_state()
    state.player.burst_max = 100

    _play(state, "clockwork_toy")

    assert state.player.block == 5
    assert state.player.burst_energy == 8
    assert [(ev["source"], ev["amount"])
            for ev in _events(state, "burst_income")] == [("skill_tag", 5),
                                                          ("card", 3)]
