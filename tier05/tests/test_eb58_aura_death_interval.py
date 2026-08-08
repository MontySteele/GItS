"""EB-58: a hydro-uptime interval ends when its target dies.

`tick_auras` walked `state.living_enemies` only, so an aura left on a corpse
never expired and never emitted anything. `tier05.aura_telemetry` had no
terminator for it and ran the interval to the last turn of the fight: the
ledger fixture read **95.0%** uptime where the identical application on a
surviving target read **15.0%**, while `AURA_DURATION_TURNS = 2` bounds any
honest interval at 3 turns. The docstring called this "a small systematic
overcount, identical across cells"; it is neither -- it scales with post-kill
fight length, which is exactly what differs between the arms
`exp_curtain_call` prints side by side.

Death CLOSES the interval, on the turn of the kill, via a distinct
`aura_ended` event -- NOT via `aura_wasted`, so the published `auras_wasted`
counter keeps measuring what it always measured (a timer that ran out on a
live body).
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.engine import combat, effects, reactions
from tier0.engine.state import CombatState, Enemy, Player
from tier05 import aura_telemetry

FIGHT_TURNS = 20


def _log(*rows: dict) -> list[dict]:
    """A 20-turn fight log: the rows given, plus a turn marker at the end."""
    return [*rows, {"turn": FIGHT_TURNS, "event": "turn_close"}]


def _applied(turn: int, target: str = "victim") -> dict:
    return {"turn": turn, "event": "aura_applied", "element": "hydro",
            "target": target, "source": "hit"}


def test_the_unterminated_interval_is_the_defect():
    """The pre-fix shape, kept as the thing being fixed: an application that
    nothing ever closes runs to the last turn of the fight."""
    t = aura_telemetry.trace(_log(_applied(2)))
    assert t.turns == FIGHT_TURNS
    assert t.hydro_turns == 19
    assert round(t.uptime * 100, 1) == 95.0


def test_a_surviving_target_reads_the_honest_value():
    """The same application on a body that lives: the timer expires and the
    interval is 3 turns, the bound AURA_DURATION_TURNS implies."""
    t = aura_telemetry.trace(_log(
        _applied(2),
        {"turn": 4, "event": "aura_wasted", "element": "hydro",
         "target": "victim"}))
    assert t.hydro_turns == C.AURA_DURATION_TURNS + 1 == 3
    assert round(t.uptime * 100, 1) == 15.0


def test_death_closes_the_interval_at_the_kill():
    """95.0% collapses to the honest value. Same application, same fight
    length; the only difference is that the body's death now terminates it."""
    same_timing = aura_telemetry.trace(_log(
        _applied(2),
        {"turn": 4, "event": "aura_ended", "element": "hydro",
         "target": "victim", "cause": "death"}))
    assert round(same_timing.uptime * 100, 1) == 15.0     # was 95.0

    killing_blow = aura_telemetry.trace(_log(
        _applied(2),
        {"turn": 2, "event": "aura_ended", "element": "hydro",
         "target": "victim", "cause": "death"}))
    assert killing_blow.hydro_turns == 1                  # was 19
    assert round(killing_blow.uptime * 100, 1) == 5.0

    # the application still counts -- only the uptime interval was wrong
    assert same_timing.applications == killing_blow.applications == 1


def _fight_state() -> CombatState:
    return CombatState(
        player=Player(hp=80, max_hp=80),
        enemies=[Enemy(hp=12, max_hp=12, name="victim",
                       intents=[{"kind": "attack", "amount": 0}]),
                 Enemy(hp=99, max_hp=99, name="bystander",
                       intents=[{"kind": "attack", "amount": 0}])],
        rng=random.Random(0))


def test_engine_emits_aura_ended_on_the_turn_of_the_kill():
    st = _fight_state()
    victim = st.enemies[0]
    st.turn = 3
    reactions.apply_aura(st, victim, "hydro")
    effects.deal_damage_to_enemy(st, victim, 40, source="attack")
    assert not victim.alive
    combat._settle_phases(st)                 # the post-HP-drop chokepoint

    ended = [ev for ev in st.log if ev["event"] == "aura_ended"]
    assert len(ended) == 1
    assert ended[0] == {"turn": 3, "event": "aura_ended", "element": "hydro",
                        "target": "victim", "cause": "death"}
    assert victim.aura is None and victim.aura_turns_left == 0
    # death is NOT waste: the published counter keeps its meaning
    assert not [ev for ev in st.log if ev["event"] == "aura_wasted"]

    # re-running the sweep does not double-emit
    combat._settle_phases(st)
    assert len([ev for ev in st.log if ev["event"] == "aura_ended"]) == 1


def test_a_live_aura_is_untouched_by_the_sweep():
    st = _fight_state()
    reactions.apply_aura(st, st.enemies[1], "hydro")
    combat._settle_phases(st)
    reactions.close_dead_auras(st)
    assert st.enemies[1].aura == "hydro"
    assert not [ev for ev in st.log if ev["event"] == "aura_ended"]


def test_the_interval_from_a_real_kill_is_bounded():
    """End to end: apply, kill, let the fight run on. The reader must not
    credit uptime past the corpse."""
    st = _fight_state()
    victim = st.enemies[0]
    st.turn = 2
    reactions.apply_aura(st, victim, "hydro")
    effects.deal_damage_to_enemy(st, victim, 40, source="attack")
    combat._settle_phases(st)
    for turn in range(3, FIGHT_TURNS + 1):    # the fight goes on without it
        st.turn = turn
        reactions.tick_auras(st)
    st.emit("turn_close")

    t = aura_telemetry.trace(st.log)
    assert t.turns == FIGHT_TURNS
    assert t.hydro_turns == 1                 # the turn of the kill, and no more
    assert t.hydro_turns <= C.AURA_DURATION_TURNS + 1
