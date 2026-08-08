"""Pins for twelve Furina card rows that no test referenced (suite-hardening
sweep s15, furina-cards group).

Each test plays ONE card out of Furina's hand into a minimal combat and
asserts the numbers the sim actually moves: printed Block and damage, the
debuffs that land and on whom, the Encore banked, the Fanfare Cap headroom
granted, the cards drawn, and -- for the four conditional rows -- BOTH sides
of the branch, so a predicate that silently stops firing is caught rather
than absorbed into the else arm.
"""

import random

from tier0.content import loader
from tier0.engine import combat, reactions, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy


def furina_state(enemies=None, energy=3, seed=0):
    """A live Furina combat: her real player (skill cadence, Fanfare cap)
    against dummies, with energy topped up so any row is affordable."""
    p = loader.build_player("furina")
    p.energy = energy
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=100)],
                       rng=random.Random(seed))


def play(state, card_id):
    card = loader.get_card(card_id)
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


def seat_salon(state, member="crabaletta"):
    """Put one member on stage. powers['salon_member'] is the count every
    salon read goes through (has_salon_members, the pilot, instruments)."""
    state.player.salon.append(member)
    state.player.powers["salon_member"] = len(state.player.salon)


def drawn(state):
    return sum(ev["amount"] for ev in state.log if ev["event"] == "extra_draw")


# --- debuff glue ---

def test_regal_bearing_blocks_three_and_weakens_only_the_target():
    """Regal Bearing gains 3 Block and applies 1 Weak to a single enemy --
    the second enemy on the field is untouched."""
    state = furina_state(enemies=[make_enemy(hp=100, name="a"),
                                  make_enemy(hp=100, name="b")])

    play(state, "regal_bearing")

    assert state.player.block == 3
    assert state.enemies[0].powers.get("weak") == 1
    assert state.enemies[1].powers.get("weak", 0) == 0


def test_commanding_gaze_blocks_two_and_weakens_every_enemy():
    """Commanding Gaze is the mass version: 2 Block -- one less than the
    single-target stare -- and 1 Weak on EVERY living enemy."""
    state = furina_state(enemies=[make_enemy(hp=100, name="a"),
                                  make_enemy(hp=100, name="b"),
                                  make_enemy(hp=100, name="c")])

    play(state, "commanding_gaze")

    assert state.player.block == 2
    assert [e.powers.get("weak") for e in state.enemies] == [1, 1, 1]


def test_witness_stand_marks_the_target_vulnerable_and_draws_one():
    """The Witness Stand applies 1 Vulnerable to the target and draws
    exactly one card. It grants no Block and deals no damage."""
    state = furina_state()
    hand_before, draw_before = len(state.player.hand), len(state.player.draw_pile)

    play(state, "witness_stand")

    assert state.enemies[0].powers.get("vulnerable") == 1
    assert state.enemies[0].hp == 100
    assert state.player.block == 0
    assert drawn(state) == 1
    assert len(state.player.hand) == hand_before + 1
    assert len(state.player.draw_pile) == draw_before - 1


# --- conditional riders, both arms ---

def test_warmup_act_hits_for_three_and_blocks_only_into_an_attacking_intent():
    """Stage Combat always swings for 3; its 3 Block rider is paid only when
    some living enemy actually intends to attack."""
    attacking = furina_state()
    play(attacking, "warmup_act")
    assert attacking.enemies[0].hp == 100 - 3
    assert attacking.player.block == 3

    blocking = furina_state(enemies=[make_enemy(
        hp=100, intents=[{"kind": "block", "amount": 5}])])
    play(blocking, "warmup_act")
    assert blocking.enemies[0].hp == 100 - 3
    assert blocking.player.block == 0


def test_waters_embrace_walls_nine_and_five_more_with_the_salon_on_stage():
    """The Water's Embrace gains 9 Block, plus 5 more only while at least
    one Salon member is on stage."""
    bare = furina_state()
    play(bare, "waters_embrace")
    assert bare.player.block == 9

    staged = furina_state()
    seat_salon(staged)
    play(staged, "waters_embrace")
    assert staged.player.block == 14


def test_tempo_change_draws_one_and_refunds_energy_only_with_a_salon():
    """Double Time always draws 1 card; it refunds its own Energy only while
    the Salon is staffed, so a bare board pays the full cost."""
    bare = furina_state(energy=3)
    play(bare, "tempo_change")
    assert drawn(bare) == 1
    assert bare.player.energy == 2            # 3 - 1, no refund

    staged = furina_state(energy=3)
    seat_salon(staged)
    play(staged, "tempo_change")
    assert drawn(staged) == 1
    assert staged.player.energy == 3          # 3 - 1 + 1, paid back


def test_directors_cut_draws_one_or_pays_energy_and_two_on_a_re_aimed_stage():
    """Director's Cut draws 1 on an ordinary turn; on a turn where the
    Spotlight was re-aimed it instead refunds 1 Energy and draws 2."""
    quiet = furina_state(energy=3)
    play(quiet, "directors_cut")
    assert drawn(quiet) == 1
    assert quiet.player.energy == 2
    assert quiet.spotlight_moved_this_turn is False

    moved = furina_state(energy=3)
    play(moved, "ethereal_spotlight")         # her selector aims the light
    assert moved.spotlight_moved_this_turn is True
    play(moved, "directors_cut")
    assert drawn(moved) == 2
    assert moved.player.energy == 3           # 3 - 1 + 1


def test_audience_participation_pays_double_on_a_reaction_turn():
    """The Crowd Answers banks 2 Encore and draws 1 normally, and 4 Encore
    plus 2 cards when an elemental reaction already fired this turn."""
    quiet = furina_state()
    play(quiet, "audience_participation")
    assert quiet.player.encore == 2
    assert drawn(quiet) == 1

    loud = furina_state()
    loud.enemies[0].aura = "pyro"
    reactions.resolve_hit(loud, loud.enemies[0], "hydro", 0)   # vaporize
    assert loud.reactions_this_turn == 1
    loud.log.clear()
    play(loud, "audience_participation")
    assert loud.player.encore == 4
    assert drawn(loud) == 2


# --- application, meter and payoff rows ---

def test_rain_of_roses_soaks_every_enemy_in_hydro_and_banks_five_encore():
    """Rain of Roses applies a hydro aura to EVERY enemy and gains 5 Encore.
    It deals no damage -- the application is the whole offensive half."""
    state = furina_state(enemies=[make_enemy(hp=100, name="a"),
                                  make_enemy(hp=100, name="b")])

    play(state, "rain_of_roses")

    assert [e.aura for e in state.enemies] == ["hydro", "hydro"]
    assert [e.hp for e in state.enemies] == [100, 100]
    assert state.player.encore == 5


def test_lasting_impression_raises_the_cap_banks_encore_and_exhausts():
    """Lasting Impression raises the Fanfare CAP by 5 -- headroom only, the
    meter itself does not move -- gains 4 Encore, and exhausts on play.

    R135 (2026-08-08) added the third clause, the ruled body: Block 0 on the
    commons rate. At an empty meter that is ZERO Block, which is the half of
    the card that has to be asserted rather than assumed -- a base-0 reader
    reads as "no Block clause at all" on every empty-meter pin, so the paying
    case lives in the test below it.
    """
    state = furina_state()
    cap_before = state.player.fanfare_cap

    play(state, "lasting_impression")

    assert state.player.fanfare_cap == cap_before + 5
    assert state.player.fanfare == 0          # cap is headroom, not a grant
    assert state.player.encore == 4
    assert state.player.block == 0            # base 0, empty meter (R135)
    assert [c.id for c in state.player.exhaust_pile] == ["lasting_impression"]
    assert state.player.discard_pile == []


def test_lasting_impression_pays_block_off_the_meter_it_raises():
    """R135 (2026-08-08), the ruled body -- candidate A, the Block reader.

    The point of the clause is that the card finally touches the meter it
    moves: the cap raise is headroom, and the Block line is what reads the
    Fanfare already banked. At 14 (the meter's working range) the commons
    rate pays 3. Mutation: drop the `bonus_formula` from the sheet row and
    this goes 3 == 0 while the pin above stays green.
    """
    state = furina_state()
    state.player.fanfare = 14

    play(state, "lasting_impression")

    assert state.player.block == 14 // 4      # commons rate, 1 per 4
    assert state.player.fanfare == 14         # a read never spends the meter


def test_prima_donna_installs_both_spotlight_powers_and_raises_the_cap():
    """Prima Donna installs one stack each of the Spotlight discount and the
    Spotlight draw, raises the Fanfare Cap by 8 without moving the meter, and
    -- being a Power -- leaves combat entirely instead of hitting a pile."""
    state = furina_state()
    cap_before = state.player.fanfare_cap

    play(state, "prima_donna")

    assert state.player.powers["spotlight_discount"] == 1
    assert state.player.powers["spotlight_draw"] == 1
    assert state.player.fanfare_cap == cap_before + 8
    assert state.player.fanfare == 0
    assert state.player.discard_pile == [] and state.player.exhaust_pile == []


def test_standing_room_only_hits_all_for_five_plus_one_per_four_fanfare():
    """The House Rises hits every enemy for 5, plus 1 more per full 4 points
    of Fanfare on the meter -- 9 Fanfare is two steps, so 7 apiece."""
    cold = furina_state(enemies=[make_enemy(hp=100, name="a"),
                                 make_enemy(hp=100, name="b")])
    play(cold, "standing_room_only")
    assert [e.hp for e in cold.enemies] == [95, 95]

    hot = furina_state(enemies=[make_enemy(hp=100, name="a"),
                                make_enemy(hp=100, name="b")])
    resources.gain_fanfare(hot, 9, "test")
    play(hot, "standing_room_only")
    assert hot.player.fanfare == 9            # read, never spent
    assert [e.hp for e in hot.enemies] == [93, 93]
