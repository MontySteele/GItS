"""The per-card Spark price on the observed board (Klee's Sparks currency).

`EB-185` put the BANK on the wire. A Spark price is a PRINTED cost and the
wire's `cost` is the ENERGY cost, so an observed board without the price keys
says nothing about what a card charges; and `can_play` folds every reason a card is unplayable into one boolean, so a
    seat cannot tell "I cannot afford this" from "there is no legal target".

C# side: `vendor/STS2_MCP/gits/GitsSparkPrice.cs` and the two lines it adds to
`McpMod.StateBuilder.BuildCardState`, reading `KleeMod.Powers.SparkCost` -- the
same expression the card's `IsPlayable` gate and the cost badge read. Python
side: `understudy/adapter.build_combat_state`.
"""

from __future__ import annotations

from understudy import adapter


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


# --------------------------------------------------------- the plain read ---

def test_the_observed_board_carries_each_hand_card_s_spark_price():
    """The read itself. Both keys land, per card, keyed by the SIM's id -- the
    id a grader's line and the falsifier both name -- and not by the wire's."""
    # Two current Klee rows that print a Spark price (Spark is a currency).
    state = board([priced("proto_ko_bang_bang", 2),
                   priced("proto_ko_sparkling_burst", 2, affordable=False)],
                  status=[SPARK_BANK])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_prices"] == {"proto_ko_bang_bang": 2,
                                     "proto_ko_sparkling_burst": 2}
    assert notes["spark_unaffordable"] == ["proto_ko_sparkling_burst"]
    assert notes["spark_price_disagreements"] == []


def test_a_card_that_charges_nothing_carries_no_price_keys():
    """The ABSENT case, which is almost every card in the game. The bridge omits
    the pair rather than writing 0, so the board stays the size it was and the
    reader can tell "charges none" from "charges zero"."""
    state = board([{"id": "KLEEMOD-PROTO_KO_KAPOW", "name": "Ka-pow!",
                    "type": "Attack", "cost": "0", "can_play": True,
                    "is_upgraded": False,
                    "description": "Set off. Deal 4 damage."}])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_prices"] == {}
    assert notes["spark_unaffordable"] == []
    assert notes["spark_price_disagreements"] == []


# ------------------------------------------------------- the cross-check ---

def test_a_wire_price_that_disagrees_with_the_sim_is_reported_by_name():
    """The whole reason the keys are worth carrying. `SparkCost.PriceOf` and
    `combat.spark_price` are two implementations of one rule in two languages;
    a divergence is a defect in one of them and is invisible unless something
    asks. It is REPORTED, never repaired -- the posture `unmapped_statuses`
    takes, and for the same reason."""
    state = board([priced("proto_ko_bang_bang", 3)],
                  status=[SPARK_BANK])

    _, notes = adapter.build_combat_state(state, prototype=True)

    assert notes["spark_prices"] == {"proto_ko_bang_bang": 3}
    assert notes["spark_price_disagreements"] == [
        "proto_ko_bang_bang: wire 3, sim 2"]


