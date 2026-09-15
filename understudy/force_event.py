"""EB-761: reach ONE NAMED EVENT in a live run, on demand. ATTENDED ONLY.

    python -m understudy.force_event ROOM_FULL_OF_CHEESE \
        --why "EB-761 item-2 re-proof"

WHY THIS IS A DRIVER AND NOT A SCENARIO STEP
--------------------------------------------
`understudy/scenario.py` is the obvious home for a setup verb, and it cannot
hold this one. Its runner delegates every menu, character-select and MAP screen
to `policy_v1` untouched and wakes up only when a COMBAT screen appears; steps
run from there. `force_next_event` is a decision taken on a map, floors before
that, about a room a scenario will never walk to -- a scenario ends with its
fight. Holding it would mean a second driver inside the first: a pre-combat
phase, run before `policy_v1` is handed the map, outside the watchdog and the
JSONL that are both written around the combat loop, and acquired by every
existing scenario file that does not want it. `scenario.NON_SCENARIO_OPS`
records that decision beside the verb list, and
`tier0/tests/test_understudy_scenario.py` pins it so the op cannot go missing
quietly.

So this module is the small thing instead: given an OPEN RUN standing on a map,
it calls the op and then walks to the next `?` room through the bridge's own
`choose_map_node`, and hands back the event screen's state.

WHAT IT DOES NOT DO, AND WILL NOT BE TAUGHT TO DO
-------------------------------------------------
IT DOES NOT FIGHT, SHOP, REST OR CLAIM. It walks map screens and it stops at
the first screen that is not a map and not the event -- naming it -- rather
than playing the run for you. A driver that could fight its way to a `?` room
would be `soak.py` with a destination, and `soak.py` is the file whose whole
claim is that its runs are runs the game generated. Put the run on a map with
a `?` on the next floor (a fresh embark is one), then call this.

IT EMBARKS NOTHING. There is no lane setup, no seed and no teardown here: it
acts on whatever run the bridge this thread is bound to already has open.

NOTHING MEASURED AFTER A CALL TO THIS IS COMPARABLE TO ANY RUN
--------------------------------------------------------------
`bridge.GRANT_GUARDRAIL`'s sentence, and it is printed with every result. The
run's `?` rooms are no longer the ones its seed produced. This reaches a FACE
-- the event's text, its options, the relic an option hands over -- and never a
number, and Guardrail-7 is unchanged: this module emits no claim about look,
legibility or feel, and neither may anything reading its output.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from tier05.maps import UNKNOWN
from understudy import bridge, policy_v0


class ForceEventError(RuntimeError):
    """The walk could not get there, and the message says where it stopped."""


#: How many screens the walk will step through before giving up. A `?` room is
#: normally one or two nodes away on the floor the caller is standing on; this
#: is a stall guard, not a budget to be spent.
MAX_SCREENS = 12


def _map_options(state: dict[str, Any]) -> list[Any]:
    """`next_options`, from either of the two places the wire has put it.

    The same two reads `policy_v1._path` makes, for the same reason: the key
    moved once already and a driver that knew only the new place would answer
    "no options" against an older bridge.
    """
    return ((state.get("map") or {}).get("next_options")
            or state.get("next_options") or [])


def _question_rooms(options: list[Any]) -> list[int]:
    """The indices of the `?` nodes among `options`.

    `policy_v0._room_kind` is ASKED rather than copied -- a second table of
    room words here is a second thing to forget when the wire renames one --
    and a `?` room is its `UNKNOWN`. That folding is the game's own: an event
    node is drawn as a question mark precisely because what is behind it is
    not announced.
    """
    return [i for i, opt in enumerate(options)
            if policy_v0._room_kind(opt) == UNKNOWN]


def walk_to_event(event_id: str, why: str, *,
                  max_screens: int = MAX_SCREENS,
                  log: Callable[[str], None] = print) -> dict:
    """Force `event_id`, walk to the next `?` room, return the event state.

    Raises `ForceEventError` when the force is refused, when the map on the
    current floor offers no `?`, or when the walk lands on a screen that is
    neither a map nor an event -- each with what was actually seen, because a
    driver that fails silently against a live game costs a session.
    """
    state = bridge.get_state()
    where = str(state.get("state_type") or "unknown")
    if where == "menu":
        raise ForceEventError(
            "No run is open (the bridge is on a menu screen). This driver "
            "acts on a run that already exists; embark one first.")

    report = bridge.force_next_event(event_id, why)
    if str(report.get("status")) != "ok":
        raise ForceEventError(
            f"the bridge refused the force: {(report.get('error') or report.get('message'))!r}")
    log(f"FORCED: {report.get('event')} in act {report.get('act')} "
        f"(index {report.get('before')} -> slot {report.get('after')}, "
        f"moved={report.get('moved')})")
    log(f"GUARDRAIL: {bridge.GRANT_GUARDRAIL}")

    for _ in range(max(1, int(max_screens))):
        state = bridge.get_state()
        where = str(state.get("state_type") or "unknown")
        if where == "event":
            return state
        if where != "map":
            raise ForceEventError(
                f"the walk stopped on a {where!r} screen. This driver walks "
                "map screens only -- it does not fight, shop, rest or claim "
                "a reward. Put the run back on a map and call it again.")
        options = _map_options(state)
        if not options:
            raise ForceEventError(
                "a map screen with no `next_options` on the wire; there is "
                "nothing to walk to.")
        wanted = _question_rooms(options)
        if not wanted:
            kinds = ", ".join(policy_v0._room_kind(o) for o in options)
            raise ForceEventError(
                "no `?` room among the next nodes on this floor "
                f"(offered: {kinds}). The forced event stays at the head of "
                "the act's list, so walking to any later `?` still reaches "
                "it -- but this driver will not play the fights in between.")
        # THE FIRST `?` AND NOT A SCORED PICK. Which node is taken is not a
        # judgement here: the destination is the room type, the event behind
        # it is already decided, and `policy_v1`'s want-table would be
        # choosing on grounds this call has no interest in. Ties break on the
        # offered index, the convention every other path decision in the
        # harness uses.
        idx = wanted[0]
        log(f"WALK: node {idx} (? room) of {len(options)}")
        answer = bridge.post("choose_map_node", index=idx)
        if str(answer.get("status")) == "error":
            raise ForceEventError(
                f"choose_map_node {idx} was refused: {(answer.get('error') or answer.get('message'))!r}")
        bridge.settle("map")

    raise ForceEventError(
        f"gave up after {max_screens} screens without reaching an event "
        "screen.")


def pending_events() -> dict:
    """What the act has pending, and what the next `?` room opens on today.

    The GET half of the route: `events` in the order they will be read,
    `events_visited`, and `next_event`. It is how a caller learns the SPELLING
    of an id rather than guessing at one with a run up.
    """
    return bridge.debug_state_info()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m understudy.force_event",
        description=("EB-761: force one named event and walk to it. "
                     "ATTENDED ONLY; nothing measured after it is comparable "
                     "to any run."))
    ap.add_argument("event", nargs="?", default="",
                    help="the event's wire id, e.g. ROOM_FULL_OF_CHEESE")
    ap.add_argument("--why", default="",
                    help="the reason, logged with the write by the endpoint")
    ap.add_argument("--list", action="store_true",
                    help="print the act's pending event list and exit")
    ap.add_argument("--max-screens", type=int, default=MAX_SCREENS)
    args = ap.parse_args(argv)

    if args.list:
        info = pending_events()
        print(f"act events_visited={info.get('events_visited')} "
              f"next_event={info.get('next_event')!r}")
        for entry in info.get("events") or []:
            print(f"  {entry}")
        return 0

    if not args.event:
        ap.error("an event id is required (or --list)")
    if not args.why.strip():
        ap.error("--why is required: the endpoint logs every write with its "
                 "reason and refuses one without")

    try:
        state = walk_to_event(args.event, args.why,
                              max_screens=args.max_screens)
    except (ForceEventError, bridge.BridgeError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    raise SystemExit(main())
