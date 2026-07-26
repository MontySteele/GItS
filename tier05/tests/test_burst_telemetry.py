"""C5: burst income by source, and the distinction P8 turns on.

The instrument's whole value is that `exhaust_muster` is separable from
`exhaust`. Without that split the report answers a question nobody asked --
her entire pool exhausts, so a single bucket is top-one for every plan and
confirms nothing. With it, P8 ("mustered-companion exhausts are top-two burst
income in commander decks") became gradeable, and graded NULL.

R14: these pin the MEASUREMENT, not a target. No threshold is asserted here
and none should be added.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from tier05 import burst_telemetry as bt


def _state():
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(0))


def test_income_is_stamped_with_its_source():
    st = _state()
    resources.gain_burst(st, 5, "reaction")
    resources.gain_burst(st, 2, "exhaust_muster")
    traced = bt.trace(st.log)
    assert traced == {"reaction": (5, 1), "exhaust_muster": (2, 1)}


def test_a_zero_gain_is_not_an_event():
    """Mirrors gain_charge: a no-op must not inflate the event count, or
    'how often does this fire' stops meaning anything."""
    st = _state()
    resources.gain_burst(st, 0, "reaction")
    assert bt.trace(st.log) == {}


def test_energy_and_events_are_tracked_separately():
    """The two disagree on purpose. A source that fires often for 1 and one
    that fires rarely for 5 are different answers to 'what fills the meter',
    and an event count flatters the first."""
    st = _state()
    for _ in range(5):
        resources.gain_burst(st, 1, "skill_tag")
    resources.gain_burst(st, 5, "reaction")
    traced = bt.trace(st.log)
    assert traced["skill_tag"] == (5, 5)
    assert traced["reaction"] == (5, 1)

    tallied = bt.tally([_FakeResult([(0, traced)])])
    by = tallied["by_source"]
    assert by["skill_tag"]["share"] == by["reaction"]["share"] == 0.5
    assert by["skill_tag"]["events"] == 5
    assert by["reaction"]["events"] == 1


def test_share_is_of_energy_not_of_events():
    st = _state()
    resources.gain_burst(st, 9, "reaction")
    for _ in range(9):
        resources.gain_burst(st, 1, "exhaust")
    tallied = bt.tally([_FakeResult([(0, bt.trace(st.log))])])
    # Equal energy, wildly unequal event counts -> equal share.
    assert tallied["by_source"]["reaction"]["share"] == 0.5


def test_unknown_sources_appear_as_rows_rather_than_being_bucketed():
    """Deliberately not an allowlist: a new income site must show up as a new
    row, not vanish into 'other'. A fixed schema would hide exactly the thing
    this instrument exists to notice."""
    st = _state()
    resources.gain_burst(st, 3, "a_source_invented_later")
    tallied = bt.tally([_FakeResult([(0, bt.trace(st.log))])])
    assert "a_source_invented_later" in tallied["by_source"]


def test_silent_for_characters_with_no_meter():
    """format_block returns '' rather than a row of zeroes -- the same rule
    the Kurage block follows, for the same reason: a block everyone learns to
    skip is a block nobody reads when it matters."""
    assert bt.format_block({}) == ""
    assert bt.tally([]) == {}


def test_the_muster_split_is_what_makes_p8_gradeable():
    """The load-bearing distinction, pinned by name.

    Collapsing exhaust_muster back into exhaust would not fail any other test
    and would silently make P8 unanswerable -- the bucket would be top-one for
    every plan, which is the null result wearing a confirmation's clothes.
    """
    st = _state()
    resources.gain_burst(st, C.KOKOMI_BURST_PER_EXHAUST, "exhaust")
    resources.gain_burst(st, C.KOKOMI_BURST_PER_EXHAUST, "exhaust_muster")
    traced = bt.trace(st.log)
    assert "exhaust" in traced and "exhaust_muster" in traced, (
        "the mustered-recruit rotation must stay separable from every other "
        "exhaust; P8 is a claim about the first and her whole pool does the "
        "second")


class _FakeResult:
    """Minimal stand-in for RunResult: only burst_traces is read."""

    def __init__(self, traces):
        self.burst_traces = traces
