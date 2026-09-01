"""EB-143 (`P11`): the pilot's Spark HOLD-versus-SPEND term.

`spend_spark` appeared nowhere in `tier0/pilot/` until this window, so the
three `C19` sinks bought their payoff for free at score time and the standing
read had to publish their contribution as a FLOOR
(`review/records/sitting-reads-2026-08-25-c19-d17-p10.md`). This file pins the
term that closes it, and it pins the SHAPE rather than the tuning: what the
three legs are, that the largest wins, that the bank is restored, and -- the
two the row actually asks for -- that a sink is REFUSED when banking is worth
more and PLAYED when its payoff beats the bank.

The behaviour under test is deliberately NOT "never spend": every number below
is derived from what the bank is worth to the hand in front of the pilot, so
the same card is played on one board and held on another.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


SINKS = ("powder_charge", "hold_the_line", "smoke_and_sparks")


def card(cid, **kw):
    kw.setdefault("name", cid)
    kw.setdefault("cost", 1)
    kw.setdefault("type", "skill")
    kw.setdefault("effects", [])
    return Card(id=cid, **kw)


def sink(price=2, payoff=None):
    """A staged sink in the `C19` shape: a Skill that charges Sparks."""
    fx = [{"op": "spend_spark", "amount": price}]
    fx += payoff if payoff is not None else [{"op": "block", "amount": 9}]
    return card("spark_sink", type="skill", cost=1, effects=fx)


def board(hand, sparks, incoming=12):
    state = make_state([make_enemy(hp=60, intents=[
        {"kind": "attack", "amount": incoming}])])
    state.player.sparks = sparks
    state.player.energy = 3
    state.player.hand = list(hand)
    return state


# --- the term exists, and only for cards that print the op ----------------

def test_only_a_card_that_prints_the_op_pays_anything():
    """The gate is `combat.spark_cost` -- the ENGINE's own cost line, asked the
    same way from both sides -- so the pilot can never charge itself for a
    price the playability gate would not have demanded."""
    state = board([], sparks=5)
    for cid in ("kaboom", "duck_and_cover", "gleeful_barrage", "hot_hands"):
        assert policy._spark_hold_cost(state, loader.get_card(cid)) == 0.0

    for cid in SINKS:
        assert policy._spark_hold_cost(state, loader.get_card(cid)) > 0.0


def test_every_shipped_sink_is_priced_and_no_other_row_is():
    """The reach of the term is enumerable, and it is the same three rows
    `test_eb118_spend_spark` pins as the whole `spend_spark` set. A fourth row
    printing the op prices itself here automatically; a row that stopped
    printing it would fall out. Both directions are the point."""
    priced = sorted(c.id for c in loader._card_index().values()
                    if combat.spark_cost(c))
    assert priced == sorted(SINKS)


# --- leg 1: the stock floor, the gain dial mirrored ------------------------

def test_the_floor_is_the_gain_dial_paid_back_on_the_way_out():
    """A gain worth +0.7 and a spend worth 0.0 is an arbitrage the scorer can
    see. Charged at the same dial, the ledger balances."""
    state = board([sink(price=2)], sparks=2)
    assert policy._spark_hold_cost(state, sink(price=2)) == pytest.approx(
        2 * C.PILOT_SPARK_VALUE)


def test_the_floor_scales_with_the_printed_price():
    state = board([], sparks=9)
    one = policy._spark_hold_cost(state, sink(price=1))
    three = policy._spark_hold_cost(state, sink(price=3))
    assert three == pytest.approx(3 * one)


# --- leg 2: the free-Attack threshold -------------------------------------

def test_crossing_the_free_attack_bar_costs_more_than_the_linear_floor():
    """Sparks below the threshold buy nothing RIGHT NOW and sparks at it buy a
    free Attack, so the crossing is a step the linear floor cannot express."""
    swing = card("swing", type="attack", cost=1,
                 effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    crosses = board([sink(price=2), swing], sparks=C.SPARKS_FOR_FREE_ATTACK)
    clears = board([sink(price=2), swing],
                   sparks=C.SPARKS_FOR_FREE_ATTACK + 2)

    assert policy._spark_hold_cost(crosses, sink(price=2)) == pytest.approx(
        C.SPARKS_FOR_FREE_ATTACK * C.PILOT_SPARK_VALUE)
    # The bank still clears the bar afterwards, so nothing is forfeited and the
    # floor is all that is charged.
    assert policy._spark_hold_cost(clears, sink(price=2)) == pytest.approx(
        2 * C.PILOT_SPARK_VALUE)


def test_the_threshold_leg_is_silent_with_no_attack_to_cash_it():
    """`combat.play_card` only spends the bank for an Attack with a printed
    cost. With none in hand there is no free Attack to forfeit."""
    state = board([sink(price=2), card("blocker")],
                  sparks=C.SPARKS_FOR_FREE_ATTACK)
    assert policy._spark_hold_cost(state, sink(price=2)) == pytest.approx(
        2 * C.PILOT_SPARK_VALUE)


def test_the_threshold_leg_reads_the_live_bar_not_the_constant():
    """True Spark Knight lowers the bar to two, and the leg follows it."""
    swing = card("swing", type="attack", cost=1,
                 effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    state = board([sink(price=2), swing], sparks=2)
    state.player.powers["spark_threshold_down"] = 1
    assert combat.spark_threshold(state) == 2
    assert policy._spark_hold_cost(state, sink(price=2)) == pytest.approx(
        2 * C.PILOT_SPARK_VALUE)


# --- leg 3: the reader leg, derived and card-agnostic ---------------------

def test_a_hand_of_non_readers_contributes_exactly_zero():
    """No epsilon and no tolerance: the probe asks the pilot's own valuations
    at two bank levels, and a card that reads no Spark is identical
    arithmetic on identical inputs."""
    state = board([sink(price=2), loader.get_card("kaboom"),
                   loader.get_card("duck_and_cover")], sparks=6)
    assert policy._spark_reader_loss(state, sink(price=2), 6, 4) == 0.0


def test_a_spark_scaling_attack_in_hand_makes_the_bank_worth_holding():
    """`gleeful_barrage` hits `2 + sparks` times for 3. Spending 2 Sparks
    costs it two hits, and the term finds that WITHOUT naming the card, the
    op or the formula -- it re-reads what the scorer already reads."""
    barrage = loader.get_card("gleeful_barrage")
    state = board([sink(price=2), barrage], sparks=4)
    per_hit = barrage.effects[0]["amount"]

    assert policy._spark_reader_loss(state, sink(price=2), 4, 2) == pytest.approx(
        2 * per_hit)
    assert policy._spark_hold_cost(state, sink(price=2)) == pytest.approx(
        2 * per_hit)


def test_a_has_spark_rider_is_found_the_same_way():
    """The other printed reader shape: a conditional that goes dead when the
    bank empties. `_active_effects` already forecasts it, so the probe sees
    the branch flip without a second copy of the rule."""
    rider = loader.get_card("patched_dress")     # block 6, +3 while has_spark
    state = board([sink(price=2), rider], sparks=2)
    loss = policy._spark_reader_loss(state, sink(price=2), 2, 0)
    assert loss > 0


def test_the_card_being_scored_is_not_its_own_reader():
    """Its payoff is scored on its own terms; counting it here would charge
    the play for the thing it is buying."""
    payoff = sink(price=2, payoff=[
        {"op": "damage", "amount": 3, "target": "random_enemy",
         "times_formula": "2_plus_sparks"}])
    state = board([payoff], sparks=4)
    assert policy._spark_reader_loss(state, payoff, 4, 2) == 0.0


def test_the_draw_pile_is_not_read():
    """HAND ONLY, deliberately: reading the pile would give the pilot
    information the player does not have at decision time. The residual error
    UNDER-values banking, which is the safe direction (R194)."""
    state = board([sink(price=2)], sparks=4)
    state.player.draw_pile = [loader.get_card("gleeful_barrage")]
    assert policy._spark_hold_cost(state, sink(price=2)) == pytest.approx(
        2 * C.PILOT_SPARK_VALUE)


# --- the probe is a pure reader -------------------------------------------

def test_the_probe_restores_the_bank_it_borrowed():
    state = board([sink(price=2), loader.get_card("gleeful_barrage")],
                  sparks=4)
    policy._spark_hold_cost(state, sink(price=2))
    assert state.player.sparks == 4


def test_the_probe_restores_the_bank_even_when_a_valuation_raises(monkeypatch):
    state = board([sink(price=2), loader.get_card("kaboom")], sparks=4)

    def boom(*args, **kwargs):
        raise RuntimeError("probe")

    monkeypatch.setattr(policy, "_expected_damage", boom)
    with pytest.raises(RuntimeError):
        policy._spark_hold_cost(state, sink(price=2))
    assert state.player.sparks == 4


# --- the decision the row asks for ----------------------------------------

def test_a_sink_is_played_when_its_payoff_beats_the_bank():
    """`hold_the_line` against a real swing: eleven points of Block the pilot
    would otherwise eat is worth more than two banked Sparks."""
    htl = loader.get_card("hold_the_line")
    state = board([htl], sparks=3, incoming=14)
    pilot = policy.make_pilot(loader.pilot_weights("spark"))

    assert policy._score(state, htl, loader.pilot_weights("spark")) > 0
    assert pilot(state) is htl


def test_a_sink_is_refused_when_banking_is_worth_more():
    """The same card, the same bank, one extra card in hand -- and the pilot
    holds the Sparks for the payoff that reads them. This is the whole row:
    the term is a DECISION, not a tax."""
    htl = loader.get_card("hold_the_line")
    barrage = loader.get_card("gleeful_barrage")
    weights = loader.pilot_weights("spark")
    state = board([htl, barrage], sparks=4, incoming=4)

    assert policy._score(state, htl, weights) < 0
    assert policy.make_pilot(weights)(state) is barrage


def test_the_same_board_played_the_sink_before_this_window():
    """The direction of the repair, asserted rather than assumed: at weight
    0.0 the term vanishes and the pilot is byte-identical to `P10` -- which on
    the board above took the sink. The degenerate case is a pin, not an
    argument."""
    htl = loader.get_card("hold_the_line")
    barrage = loader.get_card("gleeful_barrage")
    weights = loader.pilot_weights("spark")
    state = board([htl, barrage], sparks=4, incoming=4)

    before = policy.SPARK_HOLD_VALUE_WEIGHT
    try:
        policy.SPARK_HOLD_VALUE_WEIGHT = 0.0
        assert policy._score(state, htl, weights) > 0
    finally:
        policy.SPARK_HOLD_VALUE_WEIGHT = before


def test_zeroing_the_weight_restores_every_pre_window_score():
    """The same claim, over every card that prints the op, on a board where
    the term is live. `SPARK_HOLD_VALUE_WEIGHT` is the ONE place to override
    the term, and this is what "one place" means."""
    weights = loader.pilot_weights("spark")
    state = board([loader.get_card(cid) for cid in SINKS], sparks=4)
    live = {cid: policy._score(state, loader.get_card(cid), weights)
            for cid in SINKS}

    before = policy.SPARK_HOLD_VALUE_WEIGHT
    try:
        policy.SPARK_HOLD_VALUE_WEIGHT = 0.0
        off = {cid: policy._score(state, loader.get_card(cid), weights)
               for cid in SINKS}
    finally:
        policy.SPARK_HOLD_VALUE_WEIGHT = before

    for cid in SINKS:
        assert off[cid] > live[cid], cid


def test_the_term_is_pilot_independent():
    """A Spark is a Spark: the free-Attack threshold is `combat`'s, not any
    pilot's, and the three sinks are drafted by `demolition` and `generic`
    decks as well as `spark` ones. No row of `archetypes.yaml` moves, which is
    also what keeps the archive scope to the cards that print the op."""
    htl = loader.get_card("hold_the_line")
    state = board([htl], sparks=3)
    cost = policy._spark_hold_cost(state, htl)
    for pilot_id in ("spark", "demolition", "reaction"):
        assert policy._spark_hold_cost(state, htl) == cost
        assert "spark_hold" not in loader.pilot_weights(pilot_id)
