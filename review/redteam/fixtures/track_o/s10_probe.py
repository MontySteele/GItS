"""Track O slice 10 — adversarial probe of review/redteam/harness.py.

Run from the worktree root:
    python review/redteam/fixtures/track_o/s10_probe.py

Drives the S13 verification harness in-process with synthetic exploit lines
whose claims are deliberately empty, trivial, or unsatisfiable, and reports
which of them the harness returns `verified: True` for.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "review", "redteam"))

import harness  # noqa: E402

LINES = json.load(open(os.path.join(ROOT, "review", "redteam",
                                    "exploit-lines.json")))
REAL = LINES[0]


def base(**kw):
    line = {"character": REAL["character"], "deck": list(REAL["deck"]),
            "encounter_id": REAL["encounter_id"], "seed": REAL.get("seed", 0),
            "script": [], "script_default": "pass"}
    line.update(kw)
    return line


def show(tag, line):
    r = harness.run_line(line)
    print(f"{tag:44s} verified={str(r.get('verified')):5s} "
          f"ok={str(r.get('ok')):5s} executed={str(r.get('executed')):5s} "
          f"plays={r.get('plays_made')} misses={len(r.get('misses') or [])} "
          f"observed={r.get('observed')}")
    if not r.get("ok"):
        print("      error:", (r.get("error") or "").strip().splitlines()[-1])
    return r


print("=" * 100)
print("P1  no-op line: empty script, pilot never plays, claim already true at t=0")
print("=" * 100)
show("P1a empty script, hp_left >= 0",
     base(line_id="P1a", claim={"kind": "metric", "metric": "hp_left",
                                "op": ">=", "value": 0}))
show("P1b empty script, damage_dealt_total >= 0",
     base(line_id="P1b", claim={"kind": "metric",
                                "metric": "damage_dealt_total",
                                "op": ">=", "value": 0}))
show("P1c empty script, turns >= 1",
     base(line_id="P1c", claim={"kind": "metric", "metric": "turns",
                                "op": ">=", "value": 1}))
show("P1d empty script, block_gained_total <= 999999",
     base(line_id="P1d", claim={"kind": "metric",
                                "metric": "block_gained_total",
                                "op": "<=", "value": 999999}))

print()
print("=" * 100)
print("P2  trivially satisfiable / degenerate thresholds")
print("=" * 100)
show("P2a damage_dealt_total >= -1 (negative bound)",
     base(line_id="P2a", script=["auto:40"],
          claim={"kind": "metric", "metric": "damage_dealt_total",
                 "op": ">=", "value": -1}))
show("P2b cards_played_in_turn >= 0 turn 1",
     base(line_id="P2b",
          claim={"kind": "metric", "metric": "cards_played_in_turn",
                 "op": ">=", "value": 0, "turn": 1}))

print()
print("=" * 100)
print("P3  references to things that do not exist")
print("=" * 100)
show("P3a nonexistent card in deck",
     base(line_id="P3a", deck=["no_such_card_xyz"] * 10,
          claim={"kind": "metric", "metric": "hp_left", "op": ">=",
                 "value": 0}))
show("P3b nonexistent relic id",
     base(line_id="P3b", relics=["no_such_relic_xyz"],
          claim={"kind": "metric", "metric": "hp_left", "op": ">=",
                 "value": 0}))
show("P3c nonexistent encounter",
     base(line_id="P3c", encounter_id="no_such_encounter_xyz",
          claim={"kind": "metric", "metric": "hp_left", "op": ">=",
                 "value": 0}))
show("P3d nonexistent card NAMED IN SCRIPT only",
     base(line_id="P3d", script=[["no_such_card_xyz"]],
          claim={"kind": "metric", "metric": "hp_left", "op": ">=",
                 "value": 0}))
show("P3e unknown metric name",
     base(line_id="P3e", claim={"kind": "metric", "metric": "no_such_metric",
                                "op": ">=", "value": 0}))
show("P3f unknown op",
     base(line_id="P3f", claim={"kind": "metric", "metric": "hp_left",
                                "op": "!=", "value": 0}))

print()
print("=" * 100)
print("P4  does the log carry a 'cost' key? (energy_spent_in_turn's input)")
print("=" * 100)
line = base(line_id="P4", script=["auto:40"],
            claim={"kind": "metric", "metric": "energy_spent_in_turn",
                   "op": ">=", "value": 0, "turn": 1})
r = harness.run_line(line)
print("  energy_spent_in_turn turn 1 =", r.get("observed"))
print("  plays_made =", r.get("plays_made"))

print()
print("=" * 100)
print("P5  relics: are RUN-layer effects silently discarded?")
print("=" * 100)
from tier05 import relics as t5relics  # noqa: E402
for rid in ["burning_blood", "bag_of_preparation", "vajrada_amethyst",
            "anemo_sigil"]:
    try:
        combat_eff, run_eff = t5relics.split_effects([rid], REAL["character"])
        print(f"  {rid:24s} combat={combat_eff!r:60s} run={run_eff!r}")
    except Exception as e:  # noqa: BLE001
        print(f"  {rid:24s} -> {type(e).__name__}: {e}")

print()
print("=" * 100)
print("P6  cards_played_in_turn measures the PILOT'S INTENT, not the engine")
print("=" * 100)
print("  harness._metric line 142-143 counts pilot.plays; ScriptPilot appends")
print("  to pilot.plays BEFORE returning the card to run_fight (lines 109,125).")
r = harness.run_line(base(
    line_id="P6", script=["auto:40"],
    claim={"kind": "metric", "metric": "cards_played_in_turn",
           "op": ">=", "value": 1, "turn": 1}))
print("  pilot-counted cards_played_in_turn(1) =", r.get("observed"))

print()
print("=" * 100)
print("P7  'upgraded' is applied to draw_pile ONLY")
print("=" * 100)
from tier0.content import loader  # noqa: E402
loader.reset_caches()
p = loader.build_player_from_ids(REAL["character"], list(REAL["deck"]))
for attr in ("draw_pile", "hand", "discard_pile", "exhaust_pile", "deck",
             "master_deck"):
    v = getattr(p, attr, "<absent>")
    print(f"  player.{attr:14s} -> "
          f"{len(v) if isinstance(v, list) else v}")
