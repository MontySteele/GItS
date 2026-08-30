"""Both lanes up, one frame each, captured BY PID (`EB-206`).

Separate from the staging proof because it is a different claim: that the
capture helper photographs the window it was asked for when two identical
windows are on the screen. `Get-Process -Name` takes whichever the OS lists
first, so a two-lane capture by name is right about half the time.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from understudy import bridge, frames, instances, local_tester, soak

QA = Path(__file__).resolve().parents[1] / "review" / "qa" / "two-instance"


def main() -> int:
    lanes = []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for i, inst in enumerate(instances.lanes(2)):
        lanes.append(local_tester.GameLane(
            session=soak.Session(f"{stamp}-{inst.label}", do_setup=True,
                                 intent="EB-206 two-lane frames",
                                 instance=inst, install_bridge=(i == 0)),
            state_reader=bridge.get_state, log=print, instance=inst))
    out = []
    try:
        for lane in lanes:
            lane.launch()
        for lane in lanes:
            r = frames.capture(label=f"eb202-{lane.label}",
                               note=(f"EB-206: both lanes up, this is "
                                     f"{lane.label} on port "
                                     f"{lane.instance.port}"),
                               pid=lane.session.pid, instance=lane.label,
                               out_dir=QA)
            out.append({"lane": lane.label, "pid": lane.session.pid,
                        "port": lane.instance.port, **r})
    finally:
        for lane in reversed(lanes):
            lane.close()
    print(json.dumps(out, indent=1, default=str))
    (QA / "frames.json").write_text(
        json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
