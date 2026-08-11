"""Hydro-application uptime telemetry (Curtain Call sweep, R85 Track D).

Reads the combat event log; changes nothing (the fanfare_telemetry
contract). The metric definition is REGISTERED in
docs/archive/curtain-call-sprint-log-2026-07-27.md §4 and fixed for the sweep:

- uptime      fraction of PLAYER TURNS during which at least one enemy
              carried a LIVE hydro aura at any point in the turn. An aura
              interval opens at its `aura_applied` (element == hydro) and
              closes at the first later `reaction` consuming that target's
              aura, an `aura_wasted` expiry on that target, an `aura_ended`
              on that target (EB-58: the body died -- death CLOSES the
              interval on the turn of the kill, it is not counted as waste,
              because an aura on a corpse is no uptime at all), or fight end.

              EB-58 CORRECTION. Before that fix nothing closed a dead
              target's interval and the reader ran it to the last turn of the
              fight. That was not a small overcount and it was not identical
              across cells: it scaled with post-kill fight length, which is
              exactly what differs between the arms `exp_curtain_call` prints
              side by side. The ledger fixture read 95.0% where the identical
              application on a surviving target read 15.0%; AURA_DURATION_TURNS
              = 2 bounds any honest interval at 3 turns. Uptime numbers read
              before this fix are not comparable to numbers read after it.
- applications  count of hydro `aura_applied` events per combat (the raw
              application rate, cell-comparable the same way).

R14: diagnostics feeding a ruling. No acceptance targets live here -- the
bound lives in the sprint log's prediction 7. (The log retired from HEAD;
read it at `git show 230ab3b:docs/curtain-call-sprint-log-2026-07-27.md`.)

PREDICTION 7 CLOSED -- baseline accepted (R130 item 11); the accepted
residual (spotlight -11.5% / fanfare -17.3% post-shrink) rides the same
sitting's compensation tracks. Numbers and ruling: `git show a64297d`.

Re-run: `python -m tier05.exp_curtain_call` (add `--seed 12 --runs 1000`
for the rider). Numbers after a stamp move are a NEW baseline, not a
comparison against this one, unless labeled.
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
        elif ev in ("aura_wasted", "aura_ended") and e.get("element") == "hydro":
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
