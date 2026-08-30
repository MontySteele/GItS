"""LIVE PROOF for `EB-206`: two lanes, two bridges, two boards at once.

Not a graded round and not a measurement -- it stages one board on each lane
CONCURRENTLY through the real `staged_turn stage` verb, reads both packets
back, and times the same two boards serially for comparison. Guardrail-7 and
the packet guardrail are unchanged: nothing here is a number about the game.

Run with the game free and the game lock held.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from understudy import bridge, frames, instances, local_tester, soak, staged_turn

REPO = Path(__file__).resolve().parents[1]
QA = REPO / "review" / "qa"
WHY = "EB-206 live proof: two lanes staging two boards at once"


class StageOnly(local_tester.RoundSteps):
    """stage, and nothing else. No model, no grade, no replay."""

    def __init__(self, marks, lanes=None):
        self.marks = marks
        self.lanes = {l.label: l for l in (lanes or [])}

    def stage(self, row):
        t0 = time.monotonic()
        # ONE RETRY, for `EB-191` and nothing else: a chosen seed reads back
        # None on some fraction of launches and a retry always works. Two
        # lanes make each process slower and the race likelier, so the proof
        # would otherwise be measuring a filed defect rather than the lanes.
        rc = staged_turn.main(["stage", str(row["path"]), "--why", WHY,
                               "--hold"])
        retried = False
        if rc != 0:
            # THE RESTART IS PART OF THE RETRY. A failed stage leaves the game
            # mid-run (the seed check fires at Neow), and the wire has no
            # in-run exit -- so a bare second attempt refuses with
            # `unexpected_start_state: expected a menu, found 'event'`.
            retried = True
            lane = self.lanes.get(bridge.current_label())
            if lane is not None and lane.session is not None:
                lane.session.restart()
            rc = staged_turn.main(["stage", str(row["path"]), "--why", WHY,
                                   "--hold"])
        self.marks.append(("stage", row["turn_id"], bridge.current_label(),
                           bridge.current_base(), t0, time.monotonic(),
                           rc, retried))
        if rc != 0:
            raise local_tester.LocalTesterError(f"stage {row['turn_id']} = {rc}")

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
        out.append({"turn_id": tid, "path": str(path), "position": i})
    return out


def packet_back(tid):
    p = QA / tid / "packet.json"
    blob = json.loads(p.read_text(encoding="utf-8"))
    return {"turn_id": tid, "sha256": blob.get("packet_sha256"),
            "run_seed": blob.get("run_seed"),
            "cards": len(blob.get("hand") or []),
            "path": str(p)}


def main(argv):
    ids = argv[:2]
    marks = []
    lanes = []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for i, inst in enumerate(instances.lanes(2)):
        session = soak.Session(f"{stamp}-{inst.label}", do_setup=True,
                               intent="EB-206 two-lane proof",
                               instance=inst, install_bridge=(i == 0))
        lanes.append(local_tester.GameLane(session=session,
                                           state_reader=bridge.get_state,
                                           log=print, instance=inst))
    report = {"lanes": [], "boards": [], "timings": {}}
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

        # Both bridges answer, at once, on their own ports.
        for lane in lanes:
            bridge.use(lane.instance)
            state = bridge.get_state()
            report["lanes"][[l.label for l in lanes].index(lane.label)][
                "state_type"] = state.get("state_type")
        bridge.use_default()

        # A frame of each window, by PID.
        for lane in lanes:
            r = frames.capture(label=f"eb202-{lane.label}",
                               note="EB-206 live proof: both lanes up",
                               pid=lane.session.pid, instance=lane.label,
                               out_dir=QA / "two-instance")
            report["lanes"][[l.label for l in lanes].index(lane.label)][
                "frame"] = r

        # CONCURRENT: one board per lane.
        t0 = time.monotonic()
        local_tester.run_pipeline(rows(ids), lanes=lanes,
                                  steps=StageOnly(marks, lanes))
        report["timings"]["two_boards_concurrent_s"] = round(
            time.monotonic() - t0, 1)
        report["boards"] = [packet_back(t) for t in ids]

        # SERIAL, the same two boards on ONE lane, for the comparison.
        t0 = time.monotonic()
        local_tester.run_pipeline(rows(ids), lanes=[lanes[0]],
                                  steps=StageOnly(marks, lanes), serial=True)
        report["timings"]["two_boards_serial_one_lane_s"] = round(
            time.monotonic() - t0, 1)

        report["marks"] = [
            {"kind": k, "turn": t, "lane": lab, "base": base,
             "seconds": round(e - s, 1), "rc": rc, "eb191_retry": retried}
            for k, t, lab, base, s, e, rc, retried in marks]
        report["events"] = [dict(e) for lane in lanes for e in lane.events]
    finally:
        for lane in reversed(lanes):
            try:
                lane.close()
            except Exception as exc:                          # noqa: BLE001
                report.setdefault("teardown_errors", []).append(str(exc))

    out = QA / "two-instance" / "live-proof.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print(json.dumps(report, indent=1, default=str))
    print(f"\nreport: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
