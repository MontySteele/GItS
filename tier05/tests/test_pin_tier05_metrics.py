"""Pin tests for the two boundary literals in `tier05.run_metrics`.

Both instruments below are read as acceptance surfaces and both hinge on a
single comparison whose edge case nothing exercised:

  - `act_funnel()` decides whether a run "reached" an act from its death node,
    and the interesting runs are the ones that die on an act's very first
    floor;
  - `route_profile()` scores an act as inside the §11 routing band from its
    elite count, and the interesting acts are the ones sitting on the top of
    that band.
"""

from __future__ import annotations

from tier0 import constants as C
from tier05 import model
from tier05.run_metrics import act_funnel, route_profile


def _run(*, death_node, acts_completed=0, node_kinds=(), n_acts=1,
         hp_by_node=()):
    """A RunResult carrying only the fields these two metrics read."""
    return model.RunResult(seed=0, won=death_node is None,
                           death_node=death_node,
                           hp_by_node=list(hp_by_node), deck_ids=[],
                           node_kinds=list(node_kinds), n_acts=n_acts,
                           acts_completed=acts_completed)


def _act_kinds(n_elites: int) -> list[str]:
    """One act's worth of walked rooms with exactly `n_elites` elites."""
    return ["E"] * n_elites + ["N"] * (C.MAP_FLOORS - n_elites)


# --- act_funnel: the reached boundary ---------------------------------------

def test_a_run_that_dies_on_an_acts_first_floor_still_reached_that_act():
    """Reaching an act is judged inclusively: a run whose death node is
    exactly the act's first floor (act index * MAP_FLOORS) counts toward that
    act's `reached`, on act 1's floor 0 as much as on act 2's floor 16."""
    died_on_floor_0 = _run(death_node=0, acts_completed=0, n_acts=2)
    died_entering_act_2 = _run(death_node=C.MAP_FLOORS, acts_completed=1,
                               n_acts=2)

    funnel = act_funnel([died_on_floor_0, died_entering_act_2])

    assert [f["act"] for f in funnel] == [1, 2]
    # Both runs reached act 1 -- including the one that died on floor 0.
    assert funnel[0]["reached"] == 2
    assert funnel[0]["reached_rate"] == 1.0
    # The run that died on floor 16 reached act 2; the other did not.
    assert funnel[1]["reached"] == 1
    assert funnel[1]["reached_rate"] == 0.5
    # Clearing stays a separate question: dying on an act's first floor
    # reaches it without clearing it.
    assert [f["cleared"] for f in funnel] == [1, 0]


# --- route_profile: the top of the §11 elite band ---------------------------

def test_an_act_with_five_elites_falls_outside_the_target_band():
    """The §11 acceptance band is 1-4 elites per completed act: an act with
    exactly 4 elites is in band and an act with 5 is not, so `in_target_band`
    reports the share of acts at 4 or fewer (and at least one)."""
    four = _run(death_node=None, acts_completed=1, node_kinds=_act_kinds(4))
    five = _run(death_node=None, acts_completed=1, node_kinds=_act_kinds(5))

    prof = route_profile([four, five])

    assert prof["acts_measured"] == 2
    assert prof["elites_distribution"] == {4: 1, 5: 1}
    assert prof["in_target_band"] == 0.5
    # And the 4-elite act alone is fully in band.
    assert route_profile([four])["in_target_band"] == 1.0
    assert route_profile([five])["in_target_band"] == 0.0
