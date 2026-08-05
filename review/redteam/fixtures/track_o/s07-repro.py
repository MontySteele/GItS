"""SLICE 7 reproducer (Track O red-team): Track D telemetry under partial fights.

Run from the repo root:  python review/redteam/fixtures/track_o/s07-repro.py

Prints OBSERVED vs EXPECTED for every finding in the slice-07 report. Adds
nothing to the suite and modifies no instrument.
"""
from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tier05 import aura_telemetry, encore_telemetry, fanfare_telemetry  # noqa: E402
from tier05 import overlap_telemetry  # noqa: E402
from tier0 import constants as C  # noqa: E402

FIX = json.loads((pathlib.Path(__file__).with_name("s07-partial-fights.json"))
                 .read_text(encoding="utf-8"))


def log(name: str) -> list[dict]:
    return FIX[name]["log"]


def fan_log(turns: int, held: int, cap: int) -> list[dict]:
    return [{"turn": t, "event": "fanfare_turn", "total": held, "cap": cap,
             "floor": 0, "at_cap": held >= cap, "at_floor": held == 0}
            for t in range(1, turns + 1)]


print("S07-01  aura interval on a DEAD enemy runs to fight end")
dead = aura_telemetry.trace(log("aura_enemy_dies_mid_aura"))
alive = aura_telemetry.trace(log("aura_enemy_survives_aura_expires"))
print(f"  observed uptime (target died turn 2) : {dead.uptime:.1%}"
      f"  ({dead.hydro_turns}/{dead.turns} turns)")
print(f"  same application, target survives    : {alive.uptime:.1%}"
      f"  ({alive.hydro_turns}/{alive.turns} turns)")
print(f"  ceiling on a real interval           : "
      f"AURA_DURATION_TURNS={C.AURA_DURATION_TURNS} -> at most "
      f"{C.AURA_DURATION_TURNS + 1} turn indices")

print()
print("S07-02  applications_per_fight counts a partial fight as a whole fight")
full = aura_telemetry.trace(log("aura_complete_fight"))
part = aura_telemetry.trace(log("aura_partial_fight_death_turn_1"))
print("  4 complete fights          :", aura_telemetry.aggregate([full] * 4))
print("  4 complete + 4 partial     :",
      aura_telemetry.aggregate([full] * 4 + [part] * 4))
print("  1 complete + 1 EMPTY trace :",
      aura_telemetry.aggregate([full, aura_telemetry.trace([])]))

print()
print("S07-03  fanfare mean_held_fraction / peak_fraction average per-combat "
      "ratios (the docstring promises pooling)")
long_t = fanfare_telemetry.trace(fan_log(20, 10, 10))
short = [fanfare_telemetry.trace(fan_log(1, 0, 10)) for _ in range(9)]
agg = fanfare_telemetry.aggregate([long_t] + short)
print(f"  mean_held_fraction observed {agg['mean_held_fraction']:.4f}"
      f"   pooled-by-turn truth {(20 * 10) / (20 + 9) / 10:.4f}")
print(f"  peak_fraction      observed {agg['peak_fraction']:.4f}")
print(f"  time_at_cap (pooled, same dict) {agg['time_at_cap']:.4f}")

print()
print("S07-04  overlap watch: a run that died on floor 1 holding the card "
      "is a 'drafted but never played' run")


@dataclass
class FakeRun:
    won: bool
    deck_ids: list
    overlap_traces: list = field(default_factory=list)


def otrace(n: int) -> "overlap_telemetry.OverlapTrace":
    t = overlap_telemetry.OverlapTrace()
    if n:
        t.plays["honor_guard"] = n
    return t


survivors = [FakeRun(False, ["honor_guard"], [(0, otrace(3))] * 9)
             for _ in range(10)]
deaths = [FakeRun(False, ["honor_guard"], [(0, otrace(0))]) for _ in range(10)]
a = overlap_telemetry.aggregate(survivors)["cards"]["honor_guard"]
b = overlap_telemetry.aggregate(survivors + deaths)["cards"]["honor_guard"]
print(f"  survivors only : mean_plays {a['mean_plays']:.2f}"
      f"  never_played {a['never_played_runs']}")
print(f"  + 10 first-fight deaths: mean_plays {b['mean_plays']:.2f}"
      f"  never_played {b['never_played_runs']}"
      "   (plays per FIGHT is 3.0 in both populations)")

print()
print("S07-05  liveness filters discard fights that carry real content")
fp = fanfare_telemetry.trace(log("fanfare_reads_without_turn_snapshot"))
print(f"  trace alone: reads {fp.reads}  requested {fp.requested}"
      f"  wasted {fp.wasted}  overflow {fp.overflow:.1%}")
mixed = fanfare_telemetry.aggregate(
    [fanfare_telemetry.trace(fan_log(1, 6, 10)), fp])
print(f"  aggregate  : reads {mixed['reads']}  requested {mixed['requested']}"
      f"  wasted {mixed['wasted']}  overflow {mixed['overflow']:.1%}"
      f"  combats {mixed['combats']}")
et = encore_telemetry.trace(log("encore_gain_without_end"))
print(f"  encore twin: gained {et.gained} spent {et.spent}"
      f" -> aggregate {encore_telemetry.aggregate([et])}")

print()
print("S07-06  all-ticked prints 0.0% when every upkeep was TRUNCATED")
trunc = encore_telemetry.trace(log("encore_death_mid_upkeep"))
whole = encore_telemetry.trace(log("encore_complete_upkeep"))
a_tr = encore_telemetry.aggregate([trunc])
print(f"  truncated-only: complete={trunc.upkeeps_complete} "
      f"truncated={trunc.upkeeps_truncated} "
      f"all_ticked_rate={a_tr['all_ticked_rate']:.1%}")
print("  rendered:", encore_telemetry.format_row("died mid-upkeep", a_tr))
print("  rendered:", encore_telemetry.format_row(
    "stage never ticked",
    encore_telemetry.aggregate([encore_telemetry.trace([
        {"turn": 5, "event": "salon_upkeep", "members": 3, "encore": 0,
         "cost": 3},
        {"turn": 5, "event": "salon_tick", "member": "m1", "paid": False},
        {"turn": 5, "event": "salon_tick", "member": "m2", "paid": False},
        {"turn": 5, "event": "salon_tick", "member": "m3", "paid": False},
        {"turn": 5, "event": "encore_end", "encore": 0, "members": 3,
         "won": True}])])))
print("  (the two lines above are different worlds; truncated_upkeeps and "
      "upkeeps_complete are computed and never rendered)")
print("  control, complete upkeep:", whole.upkeeps_complete, "complete /",
      whole.upkeeps_truncated, "truncated")
