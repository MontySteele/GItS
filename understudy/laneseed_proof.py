"""LIVE PROOF for `EB-210`: two lanes, two pinned seeds, each read back its own.

`EB-206`'s proof (`understudy/twolane_proof.py`) staged one board per lane and
never asked what seed each run was on. `KLEESPARK-R2` did ask, on the first
graded two-lane attempt, and the answer was the other lane's seed -- so this is
the narrower thing that failure needs: two boards with DISTINCT pinned seeds,
staged at once, and each packet's `run_seed` compared against the seed its own
turn file asked for.

IT WRITES INTO A SCRATCH DIRECTORY AND NEVER INTO `review/qa/<turn>/`. The
boards it uses are `KLEESPARK-R2`'s, whose records are SEALED (R101b): nothing
here re-grades, re-reads or overwrites one. `staged_turn.QA_DIR` is pointed at
the scratch tree for the duration, which is what `turn_dir` and `export_packet`
read, so the packets land beside this report instead.

Not a graded round and not a measurement: no model is called, nothing is
graded and nothing is replayed. Guardrail-7 and the packet guardrail are
unchanged.

Run with the game free and the game lock held:

    python -m understudy.laneseed_proof <t01> <t03> [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from understudy import bridge, instances, local_tester, soak, staged_turn

REPO = Path(__file__).resolve().parents[1]
WHY = "EB-210 live proof: two lanes, two pinned seeds, each read back its own"


class StageOnly(local_tester.RoundSteps):
    """stage, with the seed passed explicitly. No model, no grade, no replay."""

    def __init__(self, marks, lanes=None):
        self.marks = marks
        self.lanes = {l.label: l for l in (lanes or [])}

    def stage(self, row):
        t0 = time.monotonic()
        argv = ["stage", str(row["path"]), "--why", WHY, "--hold",
                "--seed", str(row["seed"])]
        rc = staged_turn.main(argv)
        retried = False
        if rc != 0:
            # ONE RETRY, for `EB-191` and nothing else (a chosen seed reads
            # back None on some fraction of launches). The restart is part of
            # it: a failed stage leaves the game mid-run and the wire has no
            # in-run exit.
            retried = True
            lane = self.lanes.get(bridge.current_label())
            if lane is not None and lane.session is not None:
                lane.session.restart()
            rc = staged_turn.main(argv)
        self.marks.append({"turn": row["turn_id"], "lane": bridge.current_label(),
                           "base": bridge.current_base(),
                           "seconds": round(time.monotonic() - t0, 1),
                           "rc": rc, "eb191_retry": retried})
        if rc != 0:
            raise local_tester.LocalTesterError(
                f"stage {row['turn_id']} = {rc}")

    def read(self, row):
        return {"turn_id": row["turn_id"], "form": "", "refused": "",
                "seat_review_required": False}

    def execute(self, row, record):
        return None


def rows(ids):
    index = staged_turn.all_turns()
    out = []
    for i, tid in enumerate(ids, 1):
        path = next(p for p in index if staged_turn.load(p).id == tid)
        out.append({"turn_id": tid, "path": str(path), "position": i,
                    "seed": staged_turn.load(path).seed})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("turn_ids", nargs=2)
    ap.add_argument("--out", default="",
                    help="scratch directory for the packets and the report")
    args = ap.parse_args(argv)

    scratch = Path(args.out) if args.out else (
        REPO / "review" / "qa" / "two-instance" / "eb210-scratch")
    scratch.mkdir(parents=True, exist_ok=True)

    wanted = rows(args.turn_ids)
    seeds = {r["turn_id"]: r["seed"] for r in wanted}
    if len(set(seeds.values())) != len(seeds):
        raise SystemExit(f"the two boards must pin DIFFERENT seeds: {seeds}")

    marks: list[dict] = []
    lanes = []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for i, inst in enumerate(instances.lanes(2)):
        session = soak.Session(f"{stamp}-{inst.label}", do_setup=True,
                               intent="EB-210 lane-seed proof",
                               instance=inst, install_bridge=(i == 0))
        lanes.append(local_tester.GameLane(session=session,
                                           state_reader=bridge.get_state,
                                           log=print, instance=inst))
    report = {"what": WHY, "seeds_requested": seeds, "lanes": [],
              "boards": [], "timings": {}, "scratch": str(scratch)}
    sealed = staged_turn.QA_DIR
    staged_turn.QA_DIR = scratch          # the sealed records stay untouched
    try:
        t0 = time.monotonic()
        for lane in lanes:
            lane.launch()
            report["lanes"].append(
                {"label": lane.label, "port": lane.instance.port,
                 "pid": lane.session.pid,
                 "appdata": str(lane.instance.appdata or "default"),
                 "up_at_s": round(time.monotonic() - t0, 1)})
        report["timings"]["both_bridges_up_s"] = round(time.monotonic() - t0, 1)

        t0 = time.monotonic()
        local_tester.run_pipeline(wanted, lanes=lanes,
                                  steps=StageOnly(marks, lanes))
        report["timings"]["two_boards_concurrent_s"] = round(
            time.monotonic() - t0, 1)

        for tid in args.turn_ids:
            blob = json.loads(
                (scratch / tid / "packet.json").read_text(encoding="utf-8"))
            got = blob.get("run_seed")
            report["boards"].append(
                {"turn_id": tid, "seed_requested": seeds[tid],
                 "seed_read_back": got, "honoured": got == seeds[tid],
                 "sha256": blob.get("packet_sha256"),
                 "cards": len(blob.get("hand") or [])})
        report["marks"] = marks
        report["events"] = [dict(e) for lane in lanes for e in lane.events]
        report["verdict"] = ("PASS" if all(b["honoured"]
                                           for b in report["boards"])
                             else "CROSSED")
    finally:
        staged_turn.QA_DIR = sealed
        for lane in reversed(lanes):
            try:
                lane.close()
            except Exception as exc:                          # noqa: BLE001
                report.setdefault("teardown_errors", []).append(str(exc))

    out = scratch / "eb210-live-proof.json"
    out.write_text(json.dumps(report, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print(json.dumps(report, indent=1, default=str))
    print(f"\nreport: {out}")
    return 0 if report.get("verdict") == "PASS" else 1


if __name__ == "__main__":                                    # pragma: no cover
    sys.exit(main(sys.argv[1:]))
