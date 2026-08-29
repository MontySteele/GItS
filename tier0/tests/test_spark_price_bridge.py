"""The per-card Spark price on the observed board (the Klee Sparks arm).

`EB-185` put the BANK on the wire. That was enough while the bank had exactly
one destination and the engine chose it. Under the alternative cost it is not,
for three reasons the bridge comment states and these tests pin:

  * a Spark price is a PRINTED cost and the wire's `cost` is the ENERGY cost,
    which is 0 for every one of these cards -- so an observed board without the
    new keys shows a hand of free cards and says nothing about what they charge;
  * under the strict Rare Power the price is not on the card at all: it is
    state, contributed by a power, and no other wire key carries it;
  * `can_play` folds every reason a card is unplayable into one boolean, so a
    seat cannot tell "I cannot afford this" from "there is no legal target".

C# side: `vendor/STS2_MCP/gits/GitsSparkPrice.cs` and the two lines it adds to
`McpMod.StateBuilder.BuildCardState`, reading `KleeMod.Powers.SparkCost` -- the
same expression the card's `IsPlayable` gate and the cost badge read. Python
side: `understudy/adapter.build_combat_state`.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader
from understudy import adapter


@pytest.fixture
def alt_cost(monkeypatch):
    """The flag ON, with the id-resolving cache cleared on both sides.

    Same fixture and the same reason as `test_spark_alt_cost.py`'s:
    `_card_prototype` is memoized and its answer for a `proto_` id depends on
    the flag.
    """
    loader._card_prototype.cache_clear()
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    yield
    loader._card_prototype.cache_clear()


def board(hand, status=None):
    """A one-enemy Klee board in the bridge's own shape."""
    return {
        "state_type": "monster",
        "battle": {"round": 1, "enemies": [
            {"name": "Seapunk", "hp": 45, "max_hp": 45, "block": 0,
             "intents": [{"type": "Attack", "label": "11",
                          "description": "Attack for 11 damage."}]}]},
        "player": {
            "hp": 42, "max_hp": 62, "block": 0, "energy": 3,
            "character": "klee",
            "resources": {},
            "status": list(status or []),
            "hand": list(hand),
        },
    }


def priced(card_id, price, affordable=True, **extra):
    entry = {
        "id": "KLEEMOD-" + card_id.upper(),
        "name": card_id, "type": "Attack", "cost": "0",
        "can_play": affordable, "is_upgraded": False,
        "description": f"Spend {price} Spark. Deal damage.",
        "spark_price": price, "spark_affordable": affordable,
    }
    entry.update(extra)
    return entry


SPARK_BANK = {"id": "SPARK_POWER", "name": "Spark", "amount": 1,
              "type": "Buff", "description": "A resource."}

KNIGHT = {"id": "SPARK_ATTACK_COST_POWER", "name": "True Spark Knight",
          "amount": 1, "type": "Buff",
          "description": "Your Attacks that do not already cost Spark cost 3 "
                         "Spark instead of their Energy cost."}


# --------------------------------------------------------- the plain read ---

def test_the_observed_board_carries_each_hand_card_s_spark_price(alt_cost):
    """The read itself. Both keys land, per card, keyed by the SIM's id -- the
    id a grader's line and the falsifier both name -- and not by the wire's."""
    state = board([priced("proto_spark_strike", 1),
                   priced("proto_spark_finisher", 3, affordable=False)],
                  status=[SPARK_BANK])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_prices"] == {"proto_spark_strike": 1,
                                     "proto_spark_finisher": 3}
    assert notes["spark_unaffordable"] == ["proto_spark_finisher"]
    assert notes["spark_price_disagreements"] == []


def test_a_card_that_charges_nothing_carries_no_price_keys(alt_cost):
    """The ABSENT case, which is almost every card in the game. The bridge omits
    the pair rather than writing 0, so the board stays the size it was and the
    reader can tell "charges none" from "charges zero"."""
    state = board([{"id": "KLEEMOD-KABOOM", "name": "Kaboom!", "type": "Attack",
                    "cost": "1", "can_play": True, "is_upgraded": False,
                    "description": "Deal 7 damage."}])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_prices"] == {}
    assert notes["spark_unaffordable"] == []
    assert notes["spark_price_disagreements"] == []


# ------------------------------------------------------- the cross-check ---

def test_a_wire_price_that_disagrees_with_the_sim_is_reported_by_name(alt_cost):
    """The whole reason the keys are worth carrying. `SparkCost.PriceOf` and
    `combat.spark_price` are two implementations of one rule in two languages;
    a divergence is a defect in one of them and is invisible unless something
    asks. It is REPORTED, never repaired -- the posture `unmapped_statuses`
    takes, and for the same reason."""
    state = board([priced("proto_spark_strike", 2)], status=[SPARK_BANK])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_prices"] == {"proto_spark_strike": 2}
    assert notes["spark_price_disagreements"] == [
        "proto_spark_strike: wire 2, sim 1"]


# ------------------------------------ the price that is not on the card ---

def test_the_strict_power_s_price_crosses_and_agrees(alt_cost):
    """The case no other wire key could carry. `kaboom` prints NO Spark price;
    under True Spark Knight it costs 3, and that 3 exists only as state. The
    status row has to map or the sim would price it at 0 while the game charged
    3 -- a silent disagreement on every Attack in hand."""
    state = board([priced("kaboom", 3, affordable=False, cost="0")],
                  status=[SPARK_BANK, KNIGHT])

    cs, notes = adapter.build_combat_state(state, prototype=True)

    assert "true_spark_knight" not in notes["unmapped_statuses"]
    assert cs.player.powers.get("spark_attack_cost") == 1
    assert notes["spark_prices"] == {"kaboom": 3}
    assert notes["spark_unaffordable"] == ["kaboom"]
    assert notes["spark_price_disagreements"] == []


def test_without_the_knight_the_same_attack_prices_at_nothing(alt_cost):
    """The other direction, which is what makes the test above about the POWER
    and not about the card: drop the status row and the sim charges 0, so a wire
    that still claimed 3 would be caught."""
    state = board([priced("kaboom", 3, affordable=False, cost="0")],
                  status=[SPARK_BANK])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_price_disagreements"] == [
        "kaboom: wire 3, sim 0"]


# ------------------------------------------------------------- flag off ---

def test_with_the_flag_off_the_printed_price_still_crosses():
    """The bridge is NOT behind the flag and must not be: three shipped Klee
    Skills print a Spark price today, and their price was as invisible on an
    observed board as a prototype's. Only the POWER's contribution is flagged."""
    state = board([priced("smoke_and_sparks", 2)], status=[SPARK_BANK])

    _, notes = adapter.build_combat_state(state)

    assert notes["spark_prices"] == {"smoke_and_sparks": 2}
    assert notes["spark_price_disagreements"] == []
