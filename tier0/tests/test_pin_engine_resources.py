"""Pin tests for the Encore-spend resource economy (engine/resources.py).

Locks down the rate at which spending Encore pays the BURST meter: burst
income off a spend is per POINT drained, never a flat grant per spend event.
The Fanfare half of the same pair is already pinned elsewhere; these tests
pin the burst half, including the amount carried on the ``burst_income``
telemetry event and the behaviour when the requested spend exceeds the
buffer.

Every test states the rule it pins in its docstring and asserts the current
behaviour of the code.
"""

from tier0 import constants as C
from tier0.engine import resources
from tier0.tests.conftest import make_state


def _burst_player(st, encore, burst_max=70):
    """A player holding an Encore buffer and an ACTIVE burst meter."""
    p = st.player
    p.encore = encore
    p.burst_max = burst_max
    p.burst_energy = 0
    return p


def _burst_income(st):
    """Every ``burst_income`` event credited to the encore spend."""
    return [e for e in st.log
            if e["event"] == "burst_income" and e["source"] == "encore_spent"]


def test_encore_spend_pays_burst_per_point_not_per_spend_event():
    """Spending Encore charges the burst meter once per POINT drained: a
    5-point spend grants 5 x BURST_PER_ENCORE_SPENT burst energy, not a
    single flat grant for the spend event."""
    st = make_state()
    p = _burst_player(st, encore=5)

    spent = resources.spend_encore(st, 5)

    assert spent == 5
    assert p.encore == 0
    assert p.burst_energy == 5 * C.BURST_PER_ENCORE_SPENT
    # ...and the telemetry carries the same per-point amount in ONE event.
    income = _burst_income(st)
    assert len(income) == 1
    assert income[0]["amount"] == 5 * C.BURST_PER_ENCORE_SPENT
    assert income[0]["total"] == 5 * C.BURST_PER_ENCORE_SPENT


def test_encore_spend_pays_burst_only_for_points_actually_drained():
    """A spend larger than the buffer drains only what is there, and burst
    income is paid at the per-point rate on that DRAINED amount -- the
    requested size never inflates (or flattens) the grant."""
    st = make_state()
    p = _burst_player(st, encore=3)

    spent = resources.spend_encore(st, 9)

    assert spent == 3
    assert p.encore == 0
    assert p.burst_energy == 3 * C.BURST_PER_ENCORE_SPENT
    assert [e["amount"] for e in _burst_income(st)] == [
        3 * C.BURST_PER_ENCORE_SPENT]
