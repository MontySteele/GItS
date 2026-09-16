"""EB-771: END THE CURRENT ACT and land on the next act's map. ATTENDED ONLY.

    python -m understudy.skip_act --why "EB-771 act-2 dressing proof"
    python -m understudy.skip_act --list        # read the act list, write nothing

WHY THIS EXISTS
---------------
The Teyvat frame dresses six acts. Until this op the only way to SEE act 2 or
act 3 was for a bot to survive act 1 and beat its boss: proofs-4 stopped at that
wall, and proofs-5 reached Natlan only by writing HP with `set_hp` and then died
on floor 25 (`review/records/teyvat-proofs-5-2026-09-15.md`). Four dressings --
Natlan, Inazuma, Fontaine, Sumeru -- were unreviewable on demand. This puts a
run on a dressed act-2 or act-3 map in under a minute from embark.

WHAT IT ACTUALLY DOES
---------------------
It presses the game's own button one floor early. `bridge.skip_act` posts the
tenth `debug_state` op, and the endpoint's whole write is
`RunManager.Instance.ActChangeSynchronizer.SetLocalPlayerReady()` -- the call
`NRewardsScreen.OnProceedButtonPressed` makes on a terminal BOSS rewards screen.
In a singleplayer run that vote is unanimous immediately, so the game runs
`RunState.ActFloor++` and `RunManager.EnterNextAct()`, which is
`EnterAct(CurrentActIndex + 1)`: fade out, exit rooms, set the act, preload ITS
assets, generate ITS map, swap the music, open on a `MapRoom`.

No boss is faked, no `ActModel` is constructed, `CurrentActIndex` is never
written by hand and no map is invented. The act entered is
`RunState.Acts[CurrentActIndex + 1]` -- the DRESSED face this seed's own act
roll chose at embark -- so the skip reaches the act exactly as a real transition
would have, and takes no second roll to do it.

WHAT IT DOES NOT DO
-------------------
IT EMBARKS NOTHING and it does not play. There is no lane setup, no seed and no
teardown here: it acts on whatever run the bridge this thread is bound to
already has open, and it stops the moment the new act's map is up. Walking that
map is the caller's, exactly as `force_event.py` stops at the event screen.

THERE IS NO ACT-4 PATH. `RunManager.EnterNextAct` standing on the last act does
not advance -- it opens The Architect's room -- so the endpoint refuses there by
name. The Abyss is reserved as the act-4 face and is not built.

NOTHING MEASURED AFTER A CALL TO THIS IS COMPARABLE TO ANYTHING
---------------------------------------------------------------
Not to another run, and not to this run's own earlier floors. This is the point
where `skip_act` parts company with `force_next_event`, which consumes no rng
and says so: the floors this op skips are floors whose rolls -- room types,
encounters, rewards, card offers, the act's own boss fight -- simply never
happen, so every act-scoped stream is read from a different position afterwards.
`bridge.GRANT_GUARDRAIL`'s sentence is printed with every result. This reaches a
FACE -- an act's art, its music, its events, its enemies' names -- and never a
number, and Guardrail-7 is unchanged: this module emits no claim about look,
legibility or feel, and neither may anything reading its output.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Callable

from understudy import bridge


class SkipActError(RuntimeError):
    """The skip was refused, or the run never reached the next act's map."""


#: How many polls the driver waits for the transition to finish, and how long
#: it sleeps between them. The transition is a fade out, an asset preload, a map
#: generation and a fade in, all of them async, so the first state read after
#: the POST routinely still reports the old act. This is a stall guard and not a
#: budget: on a machine keeping up, the act number changes within two or three.
#:
#: `bridge.settle` is NOT the tool here and the reason is worth a line: it waits
#: for the SCREEN TYPE to change, and the run is standing on a map both before
#: this call and after it. What changes is the act.
MAX_POLLS = 20
POLL_DELAY = 0.6


def act_list() -> dict:
    """The run's acts in order, where it stands, and what is next.

    The GET half of the route: `acts`, `act_index`, `act` and `next_act`,
    beside the event fields the same GET already carried. It is how a caller
    learns WHICH face this seed rolled for act 2 -- Natlan or Inazuma -- before
    deciding whether this is the run worth skipping in, and it writes nothing.
    """
    return bridge.debug_state_info()


def act_number(state: dict[str, Any]) -> int | None:
    """The 1-BASED act number the wire is reporting, or None.

    `McpMod.StateBuilder` writes `run.act = CurrentActIndex + 1` on every
    screen, which is the one act fact that is always on the wire. The act ID is
    not: the state does not carry it, so the arrival check is made on the
    NUMBER the endpoint's `next_act_index` predicts, and the id is what the
    caller is told it should be looking at.
    """
    run = state.get("run") or {}
    value = run.get("act", state.get("act"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def skip_to_next_act(why: str, *, max_polls: int = MAX_POLLS,
                     delay: float = POLL_DELAY,
                     log: Callable[[str], None] = print) -> dict:
    """End the act, wait for the new act's map, and return the state there.

    Raises `SkipActError` when the op is refused and when the transition does
    not land within `max_polls` -- each with what was actually seen, because a
    driver that fails silently against a live game costs a session.
    """
    state = bridge.get_state()
    where = str(state.get("state_type") or "unknown")
    if where == "menu":
        raise SkipActError(
            "No run is open (the bridge is on a menu screen). This driver "
            "acts on a run that already exists; embark one first.")

    report = bridge.skip_act(why)
    if str(report.get("status")) != "ok":
        raise SkipActError(
            "the bridge refused the skip: "
            f"{(report.get('error') or report.get('message'))!r}")

    want_id = str(report.get("next_act") or "")
    try:
        want_number = int(report.get("next_act_index")) + 1
    except (TypeError, ValueError):
        want_number = None
    log(f"SKIPPED: {report.get('act')} (index {report.get('act_index')}) -> "
        f"{want_id} (index {report.get('next_act_index')})")
    log(f"GUARDRAIL: {bridge.GRANT_GUARDRAIL}")

    # THE ANSWER IS `queued: true`, SO THE CONFIRMATION IS A READ. The endpoint
    # returns the moment the vote is enqueued; the fade, the preload and the map
    # generation run over the frames after it. What proves the skip landed is
    # `run.act` on the wire reaching the number the report predicted -- not the
    # screen type, because the run was standing on a map before the call and is
    # standing on a map after it.
    seen = act_number(state)
    for _ in range(max(1, int(max_polls))):
        time.sleep(max(0.0, float(delay)))
        state = bridge.get_state()
        seen = act_number(state)
        if want_number is not None and seen == want_number:
            log(f"ARRIVED: act {seen} ({want_id}), screen "
                f"{str(state.get('state_type') or 'unknown')!r}")
            return state

    raise SkipActError(
        f"the op was accepted but the run never reported act {want_number} "
        f"({want_id}) within {max_polls} polls; it last reported act {seen} on "
        f"a {str(state.get('state_type') or 'unknown')!r} screen. The "
        "transition is asynchronous -- look at the game before calling again, "
        "because a second skip would move the run two acts.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m understudy.skip_act",
        description=("EB-771: end the current act and land on the next act's "
                     "map. ATTENDED ONLY; nothing measured after it is "
                     "comparable to anything, this run's own earlier floors "
                     "included."))
    ap.add_argument("--why", default="",
                    help="the reason, logged with the write by the endpoint")
    ap.add_argument("--list", action="store_true",
                    help=("print the run's act list, where it stands and what "
                          "is next, and exit without writing anything"))
    ap.add_argument("--max-polls", type=int, default=MAX_POLLS)
    args = ap.parse_args(argv)

    if args.list:
        info = act_list()
        acts = info.get("acts") or []
        index = info.get("act_index")
        print(f"act_index={index} act={info.get('act')!r} "
              f"next_act={info.get('next_act')!r}")
        for i, entry in enumerate(acts):
            print(f"  [{i}]{' <-- here' if i == index else ''} {entry}")
        if not acts:
            print("  (no run is up, so there is no act list to read)")
        return 0

    if not args.why.strip():
        ap.error("--why is required: the endpoint logs every write with its "
                 "reason and refuses one without")

    try:
        state = skip_to_next_act(args.why, max_polls=args.max_polls)
    except (SkipActError, bridge.BridgeError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
