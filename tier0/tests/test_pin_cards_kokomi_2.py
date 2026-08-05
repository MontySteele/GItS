"""Behaviour pins for thirteen Kokomi sheet cards (docs/kokomi-cards.yaml).

Each test plays one printed card into a minimal Kokomi combat and asserts the
runtime quantities the card is bought for: Block gained, damage dealt, cards
drawn/discarded/exhausted, Charge and Burst moved, and the powers left behind.
Kokomi's universal exhaust funnel (the Tamakushi Casket) rides several of
these, so the Charge/Burst totals pinned here are printed line + funnel, which
is the number a player actually sees.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, refpowers
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def kokomi_state(enemies=None, seed=0):
    player = loader.build_player("kokomi")
    state = CombatState(player=player,
                        enemies=enemies or [make_enemy(hp=300)],
                        rng=random.Random(seed))
    state.player.energy = 9
    return state


def fodder(cid="fodder", type="skill", cost=1):
    return Card(id=cid, name=cid, cost=cost, type=type, character="kokomi")


def play(state, card_id):
    card = loader.get_card(card_id)
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


# --- basic / common: Block and velocity ---

def test_tide_reading_gives_two_block_and_replaces_itself():
    """Stolen Chapter is poise plus a look ahead: 2 Block and exactly one
    card off the draw pile into hand."""
    state = kokomi_state()
    before = len(state.player.draw_pile)

    play(state, "tide_reading")

    assert state.player.block == 2
    assert len(state.player.hand) == 1
    assert len(state.player.draw_pile) == before - 1


def test_slack_water_splits_its_block_across_two_turns():
    """Slack Water pays half its wall now and banks the other half: 4 Block
    immediately and a 4-stack block_next_turn power for the turn after."""
    state = kokomi_state()

    play(state, "slack_water")

    assert state.player.block == 4
    assert state.player.powers.get("block_next_turn") == 4


def test_steady_the_line_buys_block_with_a_discard():
    """Steady the Line is free cover paid in tempo: 4 Block, and one card
    leaves hand for the discard pile."""
    state = kokomi_state()
    state.player.hand.append(fodder())

    play(state, "steady_the_line")

    assert state.player.block == 4
    assert state.player.hand == []
    assert [c.id for c in state.player.discard_pile] == ["fodder",
                                                         "steady_the_line"]


def test_whispered_word_blocks_and_its_own_sly_bell_draws():
    """A Whispered Word discards a card and gains 3 Block — and when the
    card it discards is another copy of itself, that copy's Sly rider fires
    and draws one."""
    state = kokomi_state()
    state.player.hand.append(loader.get_card("whispered_word"))

    play(state, "whispered_word")

    assert state.player.block == 3
    assert [c.id for c in state.player.discard_pile] == ["whispered_word",
                                                         "whispered_word"]
    assert len(state.player.hand) == 1          # the Sly draw


def test_salt_line_blocks_when_played_and_exhausts_when_discarded():
    """Salt Line is a 5-Block common when played; discarded by someone
    else's churn its Sly rider instead exhausts a card from hand, which the
    Casket funnel pays out as Charge."""
    state = kokomi_state()

    play(state, "salt_line")
    assert state.player.block == 5
    assert state.player.charge == 0             # nothing exhausted yet

    # Now let a discard find a Salt Line in hand: the bell rings into the
    # exhaust pile instead.
    state.player.hand = [loader.get_card("salt_line"),
                         fodder("victim", type="attack", cost=0)]
    driver = Card(id="driver", name="driver", cost=0, type="skill",
                  character="kokomi",
                  effects=[{"op": "discard", "amount": 1,
                            "select": "chosen"}])
    state.player.hand.append(driver)
    combat.play_card(state, driver)

    assert [c.id for c in state.player.exhaust_pile] == ["victim"]
    assert state.player.charge == C.CHARGE_PER_EXHAUST
    assert state.player.hand == []


def test_undertow_shuffle_sees_three_and_loses_two():
    """Daydream of a Quiet Life is raw churn: draw 3, then discard 2 at
    random — a net of one card in hand and three off the draw pile."""
    state = kokomi_state()
    before = len(state.player.draw_pile)

    play(state, "undertow_shuffle")

    assert len(state.player.draw_pile) == before - 3
    assert len(state.player.hand) == 1
    # the two random discards plus the card itself
    assert len(state.player.discard_pile) == 3


# --- the exhaust lane: fuel, walls and velocity off the funnel ---

def test_communion_of_tides_burns_one_and_draws_two():
    """Communion of Tides trades a card in hand for two fresh ones; the
    exhaust it pays with feeds the Casket funnel (Charge and Burst)."""
    state = kokomi_state()
    state.player.hand.append(fodder())

    play(state, "communion_of_tides")

    assert [c.id for c in state.player.exhaust_pile] == ["fodder"]
    assert len(state.player.hand) == 2
    assert state.player.charge == C.CHARGE_PER_EXHAUST
    assert state.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST


def test_pearl_diver_banks_three_charge_for_one_card():
    """Pearl Diver is the free fuel line: exhaust one card for 2 printed
    Charge plus the funnel's 1, and no other board effect."""
    state = kokomi_state()
    state.player.hand.append(fodder())

    play(state, "pearl_diver")

    assert [c.id for c in state.player.exhaust_pile] == ["fodder"]
    assert state.player.charge == 2 + C.CHARGE_PER_EXHAUST
    assert state.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST
    assert state.player.block == 0


def test_cleansing_tide_burns_two_cards_for_ten_block():
    """Cleansing Tide is the big burn: two cards out of hand into the
    exhaust pile, 10 Block, and two funnel payouts."""
    state = kokomi_state()
    state.player.hand += [fodder("f1"), fodder("f2")]

    play(state, "cleansing_tide")

    assert sorted(c.id for c in state.player.exhaust_pile) == ["f1", "f2"]
    assert state.player.block == 10
    assert state.player.charge == 2 * C.CHARGE_PER_EXHAUST
    assert state.player.burst_energy == 2 * C.KOKOMI_BURST_PER_EXHAUST


def test_prayer_to_the_moon_pays_eight_charge_and_exhausts_itself():
    """Prayer to the Moon is the meter's rare accelerant: 7 printed Charge
    plus 1 from its own self-exhaust, and a 4-Block moment's calm."""
    state = kokomi_state()

    play(state, "prayer_to_the_moon")

    assert state.player.charge == 7 + C.CHARGE_PER_EXHAUST
    assert state.player.block == 4
    assert [c.id for c in state.player.exhaust_pile] == ["prayer_to_the_moon"]
    assert state.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST


def test_mercy_of_the_deep_turns_every_later_exhaust_into_block():
    """Mercy of the Currents installs Feel No Pain 3: it grants no Block on
    play, and every exhaust afterwards pays 3 Block. As a Power it leaves
    combat entirely rather than routing to a pile."""
    state = kokomi_state()

    card = play(state, "mercy_of_the_deep")

    assert state.player.powers.get("feel_no_pain") == 3
    assert state.player.block == 0
    assert card not in state.player.discard_pile
    assert card not in state.player.exhaust_pile

    refpowers.exhaust_card(state, fodder())
    assert state.player.block == 3
    assert state.player.charge == C.CHARGE_PER_EXHAUST


# --- the Commander verb ---

def test_grand_conscription_musters_three_recruits_and_two_charge():
    """General Muster of Watatsumi transforms three cards in hand into
    Inazuma recruits (each discounted and given Exhaust), banks 2 printed
    Charge, and stands itself down into the exhaust pile for one more."""
    state = kokomi_state()
    state.player.hand += [fodder("f1"), fodder("f2"), fodder("f3")]

    play(state, "grand_conscription")

    assert len(state.player.hand) == 3
    for recruit in state.player.hand:
        assert recruit.is_companion and recruit.conscripted
        assert recruit.exhaust
        assert recruit.nation == "inazuma"
        # the standard conscription discount, floored at 0
        printed = loader.peek_card(recruit.id).cost
        assert recruit.cost == max(0, printed + C.CONSCRIPT_COST_DELTA)
    assert state.player.charge == 2 + C.CHARGE_PER_EXHAUST
    assert [c.id for c in state.player.exhaust_pile] == ["grand_conscription"]


def test_press_the_advantage_hits_for_seven_and_recruits_at_cost_zero():
    """Press the Advantage swings for 7 (applying Kokomi's catalyst Hydro
    aura) and conscripts one card in hand into a recruit that costs 0 this
    copy — a flat override, not the standard one-energy discount."""
    enemy = make_enemy(hp=300)
    # seed 13 draws a printed-3 recruit, so 0 can only come from the override
    state = kokomi_state(enemies=[enemy], seed=13)
    state.player.hand.append(fodder())

    play(state, "press_the_advantage")

    assert enemy.hp == 300 - 7
    assert enemy.aura == "hydro"
    assert len(state.player.hand) == 1
    recruit = state.player.hand[0]
    assert recruit.is_companion and recruit.conscripted
    assert loader.peek_card(recruit.id).cost == 3
    assert recruit.cost == 0
    assert recruit.exhaust
