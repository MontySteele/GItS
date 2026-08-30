"""THE PILOT CAN PLAY A PRICED SPARK ECONOMY (R220 pick 6(d), first half).

[USER], 2026-08-29, pick 6(d): *"fix pilot playability, then re-register the
probe on normalized metrics ... rather than the raw per-turn spend rate."*
This file pins the first half. The second half is an instrument
(`tier05/exp_klee_sparks_r2.py`) and is NOT registered here or anywhere yet.

WHAT WAS BROKEN, and it was two things, both inside the pilot's Spark ledger:

  1. `policy._score` gated the whole hold-cost lookup on `spark_cost` -- the
     PRINTED price. Under the strict Rare Power a converted Attack prints no
     price and still drains three Sparks, so the pilot paid three Sparks and
     was charged nothing for them.
  2. `_spark_hold_cost`'s three legs all price WORTH. `_spark_bank_probe`
     answers "what is this card worth at bank N", and an Attack's expected
     damage is the same float at bank 0 and bank 9, so the one consequence a
     human prices first -- paying for the small sink means the big sink in
     the same hand cannot be PLAYED this turn -- scored exactly 0.0.
     `_spark_unit_value`'s own docstring named this as blind spot (3).

WHAT WAS NOT BROKEN, and is pinned here so the diagnosis stays legible: the
AFFORDABILITY GATE and the PAYMENT were correct all along
(`combat.card_playable` refuses a short bank; the printed op and
`combat.play_card`'s Power debit take exactly the price). The 0.72-per-turn
figure `KLEESPARK-R1` read was not an affordability failure.

`POLICY_VERSION` DOES NOT MOVE. Both repairs are gated on
`C.SPARK_ALT_COST_ENABLED`, which ships off: leg 4 returns 0.0 on the flag-off
branch and the `_score` disjunct is dead there, so every shipped number is
byte-identical and there is nothing for a version bump to label. That claim is
a test in this file, not a sentence.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.combat import card_playable, play_card, spark_price
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_state
from tier0.tests.test_spark_alt_cost import alt_cost, proto   # noqa: F401


def priced_attack(cid, price, damage):
    """An Attack that prints its own Spark price, the surface's shape."""
    return Card(id=cid, name=cid, cost=0, type="attack",
                effects=[{"op": "spend_spark", "amount": price},
                         {"op": "damage", "amount": damage,
                          "target": "enemy"}])


# --- the affordability and payment rule ------------------------------------

def test_a_priced_card_is_affordable_exactly_at_its_price(alt_cost):
    """bank >= price, and not one Spark less. The gate, from both sides."""
    card = priced_attack("sink", 2, 9)
    state = make_state()
    state.player.hand = [card]
    for bank, playable in ((0, False), (1, False), (2, True), (5, True)):
        state.player.sparks = bank
        assert card_playable(state, card) is playable


def test_playing_a_priced_card_spends_exactly_the_price(alt_cost):
    """The printed op is the payment; nothing else leaves the bank."""
    card = priced_attack("sink", 2, 9)
    state = make_state()
    state.player.hand = [card]
    state.player.sparks = 5
    state.player.energy = 3
    play_card(state, card)
    assert state.player.sparks == 3
    assert state.player.energy == 3      # 0 Energy, priced in Sparks


def test_the_powers_price_is_charged_too(alt_cost):
    """The strict Rare Power's three Sparks are not on the card, so
    `spark_price` is the number both the gate and the payment read."""
    card = Card(id="plain", name="plain", cost=1, type="attack",
                effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    state = make_state()
    state.player.hand = [card]
    state.player.powers["spark_attack_cost"] = 1
    state.player.sparks = 2
    assert spark_price(state, card) == C.SPARK_ATTACK_POWER_PRICE
    assert card_playable(state, card) is False
    state.player.sparks = 3
    assert card_playable(state, card) is True
    state.player.energy = 3
    play_card(state, card)
    assert state.player.sparks == 0
    assert state.player.energy == 3       # "...instead of their Energy cost"


# --- leg 4: the sink this spend makes unplayable ----------------------------

def test_the_pilot_is_charged_for_the_sink_it_locks_out(alt_cost):
    """THE REPAIR. Bank 3, a cheap sink priced 1 and a big sink priced 3:
    spending on the cheap one drops the bank to 2 and the big one becomes
    unplayable, so the big one's whole payoff is the hold cost."""
    cheap = priced_attack("cheap", 1, 4)
    big = priced_attack("big", 3, 30)
    state = make_state()
    state.player.hand = [cheap, big]
    state.player.sparks = 3
    loss = policy._spark_playability_loss(state, cheap, 3, 2)
    assert loss > 0
    assert loss == pytest.approx(policy._spark_bank_probe(state, big, 3))
    # And it reaches the hold cost, which is the max of the four legs.
    assert policy._spark_hold_cost(state, cheap) >= loss


def test_no_lockout_no_charge(alt_cost):
    """A bank that still covers the other sink afterwards forfeits nothing,
    so the term cannot invent a hold."""
    cheap = priced_attack("cheap", 1, 4)
    other = priced_attack("other", 1, 30)
    state = make_state()
    state.player.hand = [cheap, other]
    state.player.sparks = 4
    assert policy._spark_playability_loss(state, cheap, 4, 3) == 0.0


def test_an_unaffordable_sink_is_not_forfeited(alt_cost):
    """A sink the bank could not pay for BEFORE the spend was never
    available, so losing it costs nothing."""
    cheap = priced_attack("cheap", 1, 4)
    unreachable = priced_attack("huge", 9, 99)
    state = make_state()
    state.player.hand = [cheap, unreachable]
    state.player.sparks = 2
    assert policy._spark_playability_loss(state, cheap, 2, 1) == 0.0


def test_leg_one_is_capped_by_what_the_hand_can_actually_buy(alt_cost):
    """THE SECOND HALF OF THE REPAIR, and the one that stopped the pilot
    passing its whole turn.

    Leg 1 is a per-Spark RATE times the whole price. With a 1-priced sink
    setting the rate at 12/Spark, a 3-Spark play was charged 36 -- three
    copies of a card the hand holds once -- which drove EVERY score in the
    hand negative and made `pilot()` return `None` on a hand full of playable
    Attacks. Capped at the best single alternative, the charge is 12."""
    x = priced_attack("x", 1, 12)
    junk = priced_attack("junk", 1, 2)
    big = priced_attack("big", 3, 30)
    state = make_state()
    state.player.hand = [x, junk, big]
    state.player.sparks = 3
    uncapped = 3 * policy._spark_unit_value(state, big)
    capped = policy._spark_hold_cost(state, big)
    assert uncapped > capped
    assert capped == pytest.approx(
        policy._spark_best_alternative(state, big, 3))


def test_the_pilot_holds_the_bank_for_the_bigger_sink(alt_cost):
    """END TO END, at the seam that matters: `pilot()`'s own choice.

    Bank 3; a 1-priced 12-damage Attack, a 1-priced 2-damage Attack and a
    3-priced 30-damage Attack, all three playable. Spending on either cheap
    row locks the big one out for the turn. THE PILOT MUST TAKE THE BIG ONE
    -- the spend-versus-hold trade `KLEESPARK-R1` sec.11.5 says it could not
    see. Before the repair it scored the whole hand negative and played
    nothing at all."""
    weights = loader.pilot_weights("demolition")
    x = priced_attack("x", 1, 12)
    junk = priced_attack("junk", 1, 2)
    big = priced_attack("big", 3, 30)
    state = make_state()
    state.player.hand = [x, junk, big]
    state.player.sparks = 3
    state.player.energy = 3
    chosen = policy.make_pilot(weights)(state)
    assert chosen is not None, "the pilot must not pass a hand it can play"
    assert chosen.id == "big"


# --- the flag-off half: nothing moves --------------------------------------

def test_leg_four_is_dead_with_the_flag_off():
    """The gate, stated as arithmetic rather than as an intention."""
    assert C.SPARK_ALT_COST_ENABLED is False
    cheap = priced_attack("cheap", 1, 4)
    big = priced_attack("big", 3, 30)
    state = make_state()
    state.player.hand = [cheap, big]
    state.player.sparks = 3
    assert policy._spark_playability_loss(state, cheap, 3, 2) == 0.0


def test_policy_version_did_not_move():
    """Both repairs are flag-gated, so there is no window to label. If a
    later change makes either of them fire with the flag off, this test is
    the reminder that the integer -- and a re-baseline -- comes with it."""
    from tier05 import draft
    assert draft.POLICY_VERSION == 11
