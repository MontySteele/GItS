"""EB-118 §4.5 (Klee): `spend_spark`, the Spark SINK, staged unused.

Sparks were a one-way meter -- gained, and spent only by the engine itself
when an Attack goes free at the threshold. This op makes the bank a resource
with a COMPETING use: a card may charge Sparks for something other than the
free Attack, and paying that price is a real decision because it can drop the
bank under the threshold.

WHAT THIS FILE PINS, and why each half exists:

  * the op drains the bank and EMITS the spend, so a later effect could read
    it (the packet's "expose the spend as an event") ;
  * a short bank pays NOTHING and says so -- the red half. A partial spend
    would leave the payer believing it was paid, which is the silent fire the
    contract forbids;
  * the price is VISIBLE before the play: a card printing the op at top level
    is unplayable below its price (`combat.spark_cost` -> `card_playable`),
    the `encore_cost` gate's shape, so the pilot never reaches the refusal;
  * under True Spark Knight (threshold 2) a spend of 2 FORFEITS the free
    Attack, and it forfeits it immediately -- every threshold read is a live
    read of the bank, never a cached one.

NO SHIPPED CARD PRINTS THE OP. The last test holds that, and it is the
staging discipline, not an accident: pricing and the sink cards themselves
are Phase 2.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_state
from tier05 import draft


def card(cid="sink", type="skill", cost=1, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def sink(price=2, payoff=None):
    """A staged sink in the shape §4.5 describes: a Skill that charges
    Sparks. Built here rather than loaded -- no sheet row prints the op."""
    fx = [{"op": "spend_spark", "amount": price}]
    fx += payoff if payoff is not None else [{"op": "block", "amount": 9}]
    return card("spark_sink", type="skill", cost=1, fx=fx)


def events(state, name):
    """Log rows for one event, minus the turn stamp every row carries."""
    return [{k: v for k, v in e.items() if k != "turn"}
            for e in state.log if e["event"] == name]


# --- registration ----------------------------------------------------------

def test_the_op_is_registered_and_priced():
    """An op the drafter cannot see is worth zero SILENTLY -- the defect
    class tools/lint_op_parity.py exists to end. Registration and price
    arrive together or not at all."""
    assert "spend_spark" in effects.OPS
    assert "spend_spark" in draft.STATIC_OP_PRICING


# --- the spend -------------------------------------------------------------

def test_a_paid_spend_drains_the_bank_and_emits_it():
    state = make_state()
    state.player.sparks = 3

    effects.resolve_card(state, sink(price=2))

    assert state.player.sparks == 1
    assert events(state, "spend_spark") == [
        {"event": "spend_spark", "amount": 2, "total": 1}]
    assert not events(state, "spend_spark_refused")


def test_the_payoff_resolves_on_a_paid_spend():
    state = make_state()
    state.player.sparks = 2

    effects.resolve_card(state, sink(price=2))

    assert state.player.block == 9


# --- the red half: a short bank -------------------------------------------

def test_a_short_bank_pays_nothing_and_says_so():
    """THE RED TEST. Not "spends what it can" -- Sparks have no overdraw
    currency (that grammar is Furina's Encore alone), so the whole price
    fails and the refusal is on the log."""
    state = make_state()
    state.player.sparks = 1

    assert effects.spend_sparks(state, 2) is False
    assert state.player.sparks == 1
    assert not events(state, "spend_spark")
    assert events(state, "spend_spark_refused") == [
        {"event": "spend_spark_refused", "amount": 2, "bank": 1}]


def test_an_empty_bank_pays_nothing():
    state = make_state()

    assert effects.spend_sparks(state, 1) is False
    assert state.player.sparks == 0


def test_a_spend_of_exactly_the_bank_is_paid():
    state = make_state()
    state.player.sparks = 2

    assert effects.spend_sparks(state, 2) is True
    assert state.player.sparks == 0


# --- the cost line is visible before the play ------------------------------

def test_a_sink_is_unplayable_below_its_price():
    """The visibility half. The player is shown "cannot afford" by the card
    being unplayable, exactly as an encore_cost card is -- not by playing it
    and watching nothing happen."""
    state = make_state()
    state.player.energy = 3
    c = sink(price=2)

    state.player.sparks = 1
    assert combat.card_playable(state, c) is False
    state.player.sparks = 2
    assert combat.card_playable(state, c) is True


def test_the_pilot_never_reaches_the_refusal():
    """The gate is on the pilot's own filter, so an unaffordable sink is
    never chosen -- the engine's refusal is a backstop, not the normal
    failure mode."""
    state = make_state()
    state.player.energy = 3
    state.player.sparks = 1
    state.player.hand = [sink(price=2)]
    pilot = make_pilot(loader.pilot_weights("spark"))

    assert pilot(state) is None

    state.player.sparks = 2
    assert pilot(state).id == "spark_sink"


def test_the_cost_line_is_the_top_level_price_only():
    """A spend nested in a conditional branch is a price the player cannot
    be shown at play time, so it is NOT part of the cost line. The op's own
    refusal covers it instead -- loud, at resolve time."""
    nested = card("nested", type="skill", fx=[
        {"op": "conditional", "if": "has_spark",
         "then": [{"op": "spend_spark", "amount": 5}]}])

    assert combat.spark_cost(nested) == 0

    state = make_state()
    state.player.sparks = 1
    effects.resolve_card(state, nested)
    assert state.player.sparks == 1
    assert events(state, "spend_spark_refused")


def test_two_printed_spends_add_up():
    c = card("double", fx=[{"op": "spend_spark", "amount": 1},
                           {"op": "spend_spark", "amount": 2}])
    assert combat.spark_cost(c) == 3


@pytest.mark.parametrize("amount", [0, -1, "X", None, True])
def test_an_unpriceable_spend_raises_rather_than_approximating(amount):
    """The gate reads the printed number with no state in hand. An amount it
    cannot read is a price it cannot show, and showing no price is the
    failure this op is built to prevent."""
    with pytest.raises(ValueError):
        effects.spend_spark_amount({"op": "spend_spark", "amount": amount})


# --- True Spark Knight: the threshold is forfeited, live -------------------

def attack():
    return card("swing", type="attack", cost=1,
                fx=[{"op": "damage", "amount": 6, "target": "enemy"}])


def test_true_spark_knight_lowers_the_threshold_to_two():
    state = make_state()
    state.player.powers["spark_threshold_down"] = 1
    assert combat.spark_threshold(state) == 2
    assert C.SPARKS_FOR_FREE_ATTACK == 3


def test_a_spend_of_two_forfeits_the_free_attack_under_the_knight():
    """The design point of §4.5: at the knight's threshold of 2, spending 2
    is spending the free Attack. The Attack is free BEFORE the sink resolves
    and full price after, inside one turn."""
    state = make_state()
    state.player.energy = 3
    state.player.powers["spark_threshold_down"] = 1
    state.player.sparks = 2

    assert combat.card_cost(state, attack()) == 0

    effects.resolve_card(state, sink(price=2))

    assert state.player.sparks == 0
    assert combat.card_cost(state, attack()) == 1


def test_the_threshold_reads_the_live_bank_at_play_time_too():
    """Not just the cost display: play_card's own spend guard re-reads the
    bank. A cached threshold decision would let the emptied bank pay for an
    Attack it can no longer afford."""
    state = make_state()
    state.player.energy = 3
    state.player.powers["spark_threshold_down"] = 1
    state.player.sparks = 2

    combat.play_card(state, sink(price=2))
    assert state.player.sparks == 0

    swing = attack()
    combat.play_card(state, swing)
    assert state.player.sparks == 0          # nothing left to consume
    assert state.player.energy == 3 - 1 - 1  # the sink, then a PAID Attack


def test_a_bank_above_the_price_keeps_the_free_attack():
    """The competing use is a CHOICE, not a tax: paying 2 out of 4 leaves
    the knight's threshold intact."""
    state = make_state()
    state.player.energy = 3
    state.player.powers["spark_threshold_down"] = 1
    state.player.sparks = 4

    effects.resolve_card(state, sink(price=2))

    assert state.player.sparks == 2
    assert combat.card_cost(state, attack()) == 0


# --- staging discipline ----------------------------------------------------

def test_exactly_the_three_w3_sinks_print_the_op():
    """The staging licence is SPENT, and this test is what records it.

    It used to assert `printed == []`: Route-1 staging landed the op surface
    with no sheet row using it, so no combat and no drafted number moved and
    no version stamp was owed. W3 (EB-118 Phase 3, R211) is the window that
    ends that -- `powder_charge` is the first row on any sheet to print the
    op, and it is what made `STATIC_SPARK_SPEND_COST` load-bearing and the
    `DRAFTER_VERSION` bump due.

    Kept as an EXACT SET rather than deleted, because the useful property is
    unchanged in kind: the op's reach is still enumerable, and a fourth row
    printing it is a window's worth of drafted-number movement that has to be
    said out loud rather than discovered.

    Every one prints its price at TOP LEVEL, which is not decoration: a
    `spend_spark` nested in a conditional branch is invisible to
    `combat.spark_cost` and therefore to the playability gate, so the card's
    payoff would fire without the bank ever being charged.
    """
    printed = sorted(c.id for c in loader._card_index().values()
                     if any(fx.get("op") == "spend_spark"
                            for fx in draft._nested_effects(c.effects)))
    assert printed == ["hold_the_line", "powder_charge", "smoke_and_sparks"]

    for cid in printed:
        assert loader.get_card(cid).effects[0]["op"] == "spend_spark"
