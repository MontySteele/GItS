"""P2 runaway telemetry (playtest sprint, Track P).

These lock the three properties that make the column trustworthy: it reads the
log rather than re-deriving the pulse, it pools over PULSES so the percentile
is a percentile, and it stays silent for characters that never field a Kurage.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from tier05 import kurage_telemetry as kt


def _state(charge=0):
    p = loader.build_player("kokomi")
    p.charge = charge
    return CombatState(player=p, enemies=[make_enemy(hp=300)],
                       rng=random.Random(0))


def test_the_pulse_emits_its_size_and_the_bank_that_made_it():
    st = _state(charge=5)
    st.player.powers["kurage_summon"] = 1
    effects.player_turn_end_triggers(st)
    (ev,) = [e for e in st.log if e["event"] == "kurage_pulse"]
    assert ev["amount"] == C.KURAGE_PULSE_BASE + 5 * C.KURAGE_PULSE_PER_CHARGE
    assert ev["charge"] == 5 and ev["landed"] is True


def test_a_pulse_into_an_empty_board_is_still_a_sample():
    """Deliberate: filtering these out would bias the tail DOWN exactly when
    the kit is strongest (fights ending fast). It is a sample of the curve,
    flagged as not-landed so a reader can still separate the two."""
    st = _state(charge=3)
    st.enemies[0].hp = 0
    st.player.powers["kurage_summon"] = 1
    effects.player_turn_end_triggers(st)
    (ev,) = [e for e in st.log if e["event"] == "kurage_pulse"]
    assert ev["landed"] is False
    assert kt.trace(st.log).pulses == 1


def test_trace_reads_the_log_and_does_not_recompute():
    log = [{"turn": 1, "event": "kurage_pulse", "amount": 40, "charge": 9,
            "landed": True},
           {"turn": 2, "event": "block", "amount": 5},
           {"turn": 2, "event": "kurage_pulse", "amount": 8, "charge": 1,
            "landed": False}]
    t = kt.trace(log)
    assert t.amounts == [40, 8] and t.charges == [9, 1] and t.landed == 1


def test_aggregate_pools_over_pulses_not_over_combats():
    """A mean of per-combat p95s is not a p95 of anything. One combat with a
    single huge pulse must not outweigh a combat with twenty small ones."""
    big = kt.KurageTrace(amounts=[500], charges=[100], landed=1)
    small = kt.KurageTrace(amounts=[4] * 19, charges=[0] * 19, landed=19)
    agg = kt.aggregate([big, small])
    assert agg["pulses"] == 20
    assert agg["max"] == 500
    assert agg["p50"] == 4          # pooled: the mass is in the small combat
    # RE-HOMED, sim-hygiene sprint 2026-07-29: this read 500 while
    # kurage_telemetry carried its own NEAREST-RANK percentile under a
    # docstring claiming it matched run_metrics (which interpolates). One
    # percentile now, tier05.stats, linear -- so p95 of these 20 pulses
    # interpolates between the 19th and 20th sample instead of snapping to the
    # top one. The CLAIM this test makes is unchanged and still holds: pooling
    # over pulses, not over combats (a mean of per-combat p95s would be 252).
    # `max` is what asserts the huge pulse is still visible at all.
    assert round(agg["p95"], 1) == 28.8


def test_by_act_keeps_the_acts_apart():
    a1 = kt.KurageTrace(amounts=[10, 12], charges=[1, 2])
    a3 = kt.KurageTrace(amounts=[200], charges=[49])
    per_act = kt.by_act([(0, a1), (2, a3)])
    assert set(per_act) == {0, 2}
    assert per_act[0]["max"] == 12 and per_act[2]["max"] == 200


def test_it_is_silent_for_a_roster_that_never_fields_a_kurage():
    """Every other character must pay nothing -- not a row of zeroes that
    readers learn to skip past."""
    assert kt.aggregate([kt.KurageTrace()]) == {}
    assert kt.by_act([(0, kt.KurageTrace())]) == {}
    assert kt.format_block({}) == ""
