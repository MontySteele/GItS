"""`KLEESPARK-R2`'s normalized columns, as arithmetic (R220 pick 6(d)).

The script is an INSTRUMENT and NOT a registration; what is testable about it
is that its columns mean what its header says they mean. Three claims:

  * `spent / available` normalizes the raw rate `KLEESPARK-R1` read, and
    `available` is the bank a turn OPENED with plus what it generated -- not
    the bank at any single instant;
  * SKIPPED counts a Spark-priced card that was affordable AND playable at
    the moment the pilot DECLINED to play, and nothing else;
  * the arms it compares are r1's arms, unchanged, and r1 itself is untouched
    (R101b: a published measurement record stands as published).

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

import pytest

from tier0 import constants as C
from tier0.engine.state import Card
from tier0.tests.conftest import make_state
from tier05 import exp_klee_sparks_r1 as r1
from tier05 import exp_klee_sparks_r2 as r2


def priced(cid, price, damage=5):
    return Card(id=cid, name=cid, cost=0, type="attack",
                effects=[{"op": "spend_spark", "amount": price},
                         {"op": "damage", "amount": damage,
                          "target": "enemy"}])


@pytest.fixture
def alt_cost(monkeypatch):
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    yield


# --- the columns ------------------------------------------------------------

def test_available_is_the_opening_bank_plus_the_turns_generation():
    log = [{"turn": 1, "event": "gain_spark", "amount": 2, "total": 4},
           {"turn": 1, "event": "spend_spark", "amount": 1, "total": 3}]
    records = [(1, 2, 0, True), (1, 3, 0, False)]
    rows = r2._fight_rows(log, records, C.SPARKS_FOR_FREE_ATTACK)
    assert len(rows) == 1
    row = rows[0]
    assert row["opening"] == 2          # the bank at the FIRST decision
    assert row["generated"] == 2
    assert row["spent"] == 1
    assert row["available"] == 4        # opening + generated, not the bank
    assert row["spent"] / row["available"] == pytest.approx(0.25)


def test_the_retired_rules_automatic_consume_is_counted_at_the_threshold():
    """`sparks_spent` prints no amount; the base rule took the threshold, so
    the OFF arm's spend column is comparable with the ON arm's."""
    log = [{"turn": 1, "event": "sparks_spent"}]
    rows = r2._fight_rows(log, [(1, 3, 0, False)], C.SPARKS_FOR_FREE_ATTACK)
    assert rows[0]["spent"] == C.SPARKS_FOR_FREE_ATTACK


def test_skipped_is_read_at_the_decision_the_pilot_declined():
    """The LAST record of a turn is the turn's end, and only a `None` there
    is a choice not to spend."""
    log = [{"turn": 1, "event": "gain_spark", "amount": 1, "total": 1}]
    # played, played, declined-with-two-affordable-sinks
    rows = r2._fight_rows(log, [(1, 3, 1, True), (1, 2, 2, True),
                                (1, 2, 2, False)],
                          C.SPARKS_FOR_FREE_ATTACK)
    assert rows[0]["skipped"] == 2


def test_a_turn_the_instrument_never_saw_end_counts_zero():
    """A fight that ended inside a turn never asked the pilot again, so the
    instrument was not there to look and must not guess."""
    rows = r2._fight_rows([{"turn": 1, "event": "spend_spark", "amount": 1,
                            "total": 0}],
                          [(1, 1, 3, True)], C.SPARKS_FOR_FREE_ATTACK)
    assert rows[0]["skipped"] == 0


# --- the skip snapshot ------------------------------------------------------

def test_the_snapshot_counts_affordable_playable_priced_cards(alt_cost):
    cheap = priced("cheap", 1)
    dear = priced("dear", 9)
    plain = Card(id="plain", name="plain", cost=0, type="attack",
                 effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    state = make_state()
    state.player.hand = [cheap, dear, plain]
    state.player.energy = 3
    state.player.sparks = 2
    # `dear` is unaffordable and `plain` carries no price: neither is a
    # skipped SINK.
    assert r2._sink_snapshot(state) == 1
    state.player.sparks = 0
    assert r2._sink_snapshot(state) == 0


def test_an_energy_starved_sink_is_not_a_skip(alt_cost):
    """The count is a measure of CHOICE, so anything `card_playable` refuses
    is already excluded -- energy included."""
    sink = Card(id="sink", name="sink", cost=2, type="attack",
                effects=[{"op": "spend_spark", "amount": 1},
                         {"op": "damage", "amount": 5, "target": "enemy"}])
    state = make_state()
    state.player.hand = [sink]
    state.player.sparks = 3
    state.player.energy = 0
    assert r2._sink_snapshot(state) == 0
    state.player.energy = 2
    assert r2._sink_snapshot(state) == 1


# --- the arms, and r1 -------------------------------------------------------

def test_r2_compares_r1s_arms():
    """Imported, not retyped: the successor cannot silently re-cast the A/B."""
    assert r2.TIGHT_SET is r1.TIGHT_SET
    assert r2.SHIPPED_SET is r1.SHIPPED_SET
    assert (r2.ENCOUNTER, r2.PILOT) == (r1.ENCOUNTER, r1.PILOT)


def test_the_watcher_does_not_change_the_fight():
    """EMIT-ONLY: the wrapper returns exactly what the pilot returned."""
    sentinel = object()
    watched = r2._watched(lambda state: sentinel)
    state = make_state()
    state.player.hand = []
    assert watched(state) is sentinel
    assert watched.records == [(state.turn, state.player.sparks, 0, True)]
