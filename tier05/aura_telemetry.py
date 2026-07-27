"""Hydro-application uptime telemetry (Curtain Call sweep, R85 Track D).

Reads the combat event log; changes nothing (the fanfare_telemetry
contract). The metric definition is REGISTERED in
docs/curtain-call-sprint-log-2026-07-27.md §4 and fixed for the sweep:

- uptime      fraction of PLAYER TURNS during which at least one enemy
              carried a LIVE hydro aura at any point in the turn. An aura
              interval opens at its `aura_applied` (element == hydro) and
              closes at the first later `reaction` consuming that target's
              aura, an `aura_wasted` expiry on that target, or fight end.
              Enemy death mid-aura is not separately tracked; the small
              systematic overcount is identical across cells, which is what
              the pre-registered ±10% bound compares.
- applications  count of hydro `aura_applied` events per combat (the raw
              application rate, cell-comparable the same way).

R14: diagnostics feeding a ruling. No acceptance targets live here -- the
bound lives in the sprint log's prediction 7.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AuraTrace:
    turns: int = 0
    hydro_turns: int = 0          # turns with >=1 live hydro interval
    applications: int = 0         # hydro aura_applied events

    @property
    def uptime(self) -> float:
        return self.hydro_turns / self.turns if self.turns else 0.0


def trace(log: list[dict]) -> AuraTrace:
    t = AuraTrace()
    if not log:
        return t
    t.turns = max(e.get("turn", 0) for e in log)
    # open hydro intervals per target -> opening turn
    open_at: dict[str, int] = {}
    hydro_turns: set[int] = set()

    def _close(target: str, upto_turn: int) -> None:
        start = open_at.pop(target, None)
        if start is not None:
            hydro_turns.update(range(start, upto_turn + 1))

    for e in log:
        ev, turn = e.get("event"), e.get("turn", 0)
        tgt = e.get("target")
        if ev == "aura_applied":
            if e.get("element") == "hydro":
                open_at.setdefault(tgt, turn)
            else:
                # a different element landing on this target replaced or
                # reacted away whatever was there (one aura per enemy)
                _close(tgt, turn)
        elif ev == "reaction" and e.get("aura") == "hydro":
            _close(tgt, turn)
        elif ev == "aura_wasted" and e.get("element") == "hydro":
            _close(tgt, turn)
    for tgt in list(open_at):
        _close(tgt, t.turns)
    t.hydro_turns = len([x for x in hydro_turns if 1 <= x <= t.turns])
    t.applications = sum(1 for e in log if e.get("event") == "aura_applied"
                         and e.get("element") == "hydro")
    return t


def aggregate(traces: list[AuraTrace]) -> dict:
    turns = sum(t.turns for t in traces)
    hydro = sum(t.hydro_turns for t in traces)
    apps = sum(t.applications for t in traces)
    fights = len(traces) or 1
    return {
        "uptime": hydro / turns if turns else 0.0,
        "applications_per_fight": apps / fights,
        "fights": len(traces),
    }
