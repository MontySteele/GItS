"""P1 -- the soak harness. N policy_v1 runs through the REAL game, unattended.

    python -m understudy.soak --runs 3
    python -m understudy.soak --runs 20 --character KLEEMOD-FURINA
    python -m understudy.soak --runs 1 --no-setup      # attach to a live game

WHAT THIS IS FOR, IN ONE SENTENCE
Move jank-filtering off [USER]'s play hours: a broken build should be caught by
the soak, not by his evening. That is the brief's acceptance bar for P1 and it
is why the crash/softlock detector -- not the winrate -- is the load-bearing
half of this file.

WHAT NO NUMBER FROM THIS FILE MEANS (Guardrail-7, and it is not a formality)
Every figure a soak produces is a **bot-limited floor**, in exactly the sense
"pilot-limited" already means in tier 0.5, and stacked on top of that:

  * policy_v1 is a heuristic with two declared reductions of its own (the map
    arm sees two plies, the draft arm is the sim's and R96 routed three known
    scoring gaps in it);
  * on the DEFAULT arm the seeds are read-back, not chosen (R95), so two soaks
    are two different sets of runs and their numbers are not each other's
    comparators (see SEEDS below for the arm that fixes this, and for what it
    does not fix);
  * a JSON-state agent cannot see the screen, so nothing here is evidence
    about fun, legibility, or readability, ever.

Winrate, floors reached, HP curves and damage tables from this harness are
DEFECT-HUNTING INSTRUMENTS and telemetry. They are not balance evidence, they
do not grade a character, and they may not be quoted against a floor.

SEEDS -- TWO ARMS, AND THIS FILE FLIES BOTH.

  read-back (R95, the DEFAULT, `--seed` absent)
      The game generates the seed; we record it from `GET /api/v1/compendium`
      after embarking, and it identifies the run for a defect report. Nothing
      is chosen, so two soaks are two different sets of runs.

  chosen (P1.5 item 1, R104, `--seed SEED` -- repeatable, run i takes seed i)
      The seed goes on through the forked bridge's own endpoint,
      `POST /api/v1/gits/seed`, at the one moment that works: character select
      up, a character picked, the embark confirm not yet fired. No seed is
      passed on the embark verb in EITHER arm -- upstream's `menu_select(seed=)`
      is untouched (`vendor/STS2_MCP/gits/GitsSeed.cs` says why). The channel is
      declared on the reversibility ledger before the first seed lands, because
      `NGame.DebugSeedOverride` is global and sticky, and teardown clears it
      unconditionally.

      THE READ-BACK IS STILL TAKEN, and on this arm it is the VERIFICATION: a
      run whose recorded seed disagrees with the seed it asked for files
      `seed_not_honoured` and stops. That kind sits on the HARNESS side of the
      line -- a game that rolled its own seed is a game behaving normally, and
      what failed is this file's claim to have chosen one. The comparison is
      against the CANONICAL form the endpoint reports back, not against what
      was typed: `SeedHelper.CanonicalizeSeed` upper-cases and maps 'O'->'0',
      'I'->'1', so comparing against the typed string would file the defect
      against a seed the game honoured exactly.

A chosen seed fixes WHICH RUN, and that is all it fixes. It does not make a
soak number a balance number, and Guardrail-7 above is unchanged by it.

CHARACTER -- THE SAME DISCIPLINE, AND FOR THE SAME REASON (EB-117).
`--character` names a character-select OPTION ID (`KLEEMOD-FURINA`), not a
roster id, and a string that matched nothing used to be silent: the pick never
fired, the game embarked on whatever the screen had highlighted, and the report
was headed with the REQUESTED name. So the request is checked against the
select screen BEFORE the embark (`character_not_offered`), the character the
run actually started with is read back off `player.character` AFTER it
(`character_mismatch`, `character_unverified`), and the READ-BACK is what every
record, index and report header carries. All three kinds are harness-side and
halt the soak on a second occurrence, exactly like `seed_not_honoured`.

ON NEITHER ARM IS THE SEED A POLICY INPUT. It is stamped on the log and, on the
chosen arm, compared against the read-back. `understudy.rng.policy_rng` refuses
a stream label shaped like a game seed, and that refusal is the enforcement.

READINESS (R97/5a). The launcher watches for the `options` key in the menu
state, NEVER the HTTP health endpoint. `GET /` answers about 5 s after launch;
the main menu has no buttons for another ~20. A launcher that trusts the health
check acts into an empty menu, which is a soft-lock we would then have to
diagnose as if it were the game's fault.

REVERSIBILITY. Every game-dir write is recorded in a ledger with its undo, the
ledger is written to disk BEFORE the change is made, and teardown walks it in
reverse. Appendix A of `docs/archive/understudy-phase0-report.md` is the format this
inherits and the checklist it is measured against.

EB-1, THE SOFT-LOCK THIS FILE IS EXPECTED TO SURVIVE. Two legs, because the
hazard has two faces. `HAZARD_EVENTS` below is a register of screens the driver
refuses to drive at all, and `understudy.hangwatch` is the watchdog for the
case where the game hangs before there is a screen to refuse -- process alive,
wire dead, log growing at megabytes a second. The second files
`unresponsive_spin` rather than `bridge_unreachable`, which matters because
`bridge_unreachable` is a HARNESS-side kind and this failure is not the
harness's. Neither leg fixes anything: the defect is upstream's and stays open
as a live-play hazard.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# `hangwatch`, `keepawake` and `naming` are used by the seams rather than
# here, and are imported anyway: `soak.hangwatch` is part of this module's
# surface, and the suite reaches for it (`soak.hangwatch.diagnose`).
from understudy import (bridge, deckwatch, hangwatch, instances,  # noqa: F401
                        keepawake, naming, policy_v1)


REPO = Path(__file__).resolve().parent.parent
LOG_DIR = Path(__file__).resolve().parent / "logs" / "soak"
LOCAL_PROPS = REPO / "klee-mod" / "local.props"

# A single action's settle poll.
SETTLE_S = 0.7

# EB-231. How long teardown waits for the game's pid to leave the process
# table before it REFUSES to write REVERTED. Generous, because the alternative
# to waiting is a marker that lies: `KLEESPARK-W3`'s teardown reported the
# process terminated, the bridge removal then failed on that live pid twice,
# and the operator finished it by hand.
PID_EXIT_TIMEOUT_S = 30.0
PID_EXIT_POLL_S = 0.5

# --------------------------------------------------- EB-231, the pid probe --
#
# A TEARDOWN MAY NOT REPORT A KILL IT DID NOT MAKE. `--teardown` rebuilds the
# session from the ledger ON DISK, so `self.proc` is None and `_kill` had
# nothing to terminate -- and `_stop_game` returned "process terminated"
# anyway, which the ledger wrote as REVERTED over a running game. The next
# step then tried to delete `mods/STS2_MCP` out from under a process holding
# the dll, and the marker had already said the process was gone.
#
# Two halves fix it, and they are separate on purpose. The pid is RECORDED on
# the launch entry, so a session rebuilt from disk knows which process it
# owns and can kill it by number; and the exit is PROVEN by the process table
# before the marker is written. On a timeout `_stop_game` raises, `_step`
# records NOT REVERTED with what is still alive, and nobody is told the game
# is closed while it is on screen.


def pid_image(pid: int) -> str | None:
    """The image name of a live pid, or None when nothing holds that number.

    THE UNKNOWN ANSWER COUNTS AS ALIVE. A probe that cannot run -- no
    `tasklist`, a non-zero exit, a permission wall -- has not proved the
    process gone, and this function exists to prove it gone. So a failed probe
    returns a string saying so, which every caller reads as "still there".
    """
    try:
        done = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/NH", "/FO", "CSV"],
            capture_output=True, text=True, timeout=30)
    except Exception as exc:                                 # noqa: BLE001
        return f"<pid probe failed: {type(exc).__name__}: {exc}>"
    if done.returncode != 0:
        return (f"<pid probe exited {done.returncode}: "
                f"{(done.stderr or '').strip()[:120]}>")
    for row in (done.stdout or "").splitlines():
        # `"SlayTheSpire2.exe","31448","Console","1","1,234,567 K"`. The pid is
        # matched inside its own quotes so 3144 cannot match 31448.
        if f'"{int(pid)}"' in row:
            name = row.split('","')[0].lstrip('"')
            return name or "unknown.exe"
    return None


def wait_for_exit(pid: int, timeout_s: float = PID_EXIT_TIMEOUT_S,
                  poll_s: float = PID_EXIT_POLL_S) -> str | None:
    """Poll until the pid is gone. None when it left, the image when it stayed."""
    deadline = time.time() + float(timeout_s)
    while True:
        image = pid_image(pid)
        if image is None:
            return None
        if time.time() >= deadline:
            return image
        time.sleep(poll_s)


def game_dir() -> Path:
    if not LOCAL_PROPS.exists():
        raise SystemExit(
            f"local.props not found at {LOCAL_PROPS}. Copy local.props.example "
            f"and set GameDir; the soak writes to the game directory and will "
            f"not guess where it is.")
    root = ET.parse(LOCAL_PROPS).getroot()
    for pg in root.iter("PropertyGroup"):
        node = pg.find("GameDir")
        if node is not None and (node.text or "").strip():
            return Path(node.text.strip())
    raise SystemExit("GameDir is empty in local.props.")


# ------------------------------------------------------------- the seams ----
#
# `EB-180`. This file was 2,811 lines carrying four concerns; the four now
# live one to a module and are re-exported here, so every name a caller,
# a test or the CLI reached for on `understudy.soak` still resolves off
# `understudy.soak`. Nothing below is new: each name is the definition that
# used to stand in this file, at the line the seam module now keeps it.
#
#   soak_shape      the fixed shapes -- paths, dials, registers, `Defect`
#   soak_lane       is the bridge staged, is a game up, whose lane
#   soak_session    launch and teardown, and the ledger between them
#   soak_telemetry  one fight's numbers, off the state deltas
#   soak_screens    what one screen is, and the forced move on it
#   soak_navigate   the route to the first fight, and who embarked
#   soak_driver     one run, with a watchdog on every action
#
# THE WIRE AND THE SWAPPABLE DIALS STAY HERE. `bridge`, `LOG_DIR`,
# `LOCAL_PROPS`, `SETTLE_S`, `PID_EXIT_*`, `pid_image`, `wait_for_exit` and
# `game_dir` are declared above rather than in a seam, because they are the
# names a caller reaches in and swaps -- and a seam that bound its own copy
# at import would never see the swap. The seams read them back off this
# module at call time (`soak_session._soak`).

from understudy.soak_shape import (        # noqa: E402,F401  (re-export)
    BRIDGE_DLL, BRIDGE_MANIFEST, BRIDGE_RELATIVE, COMBAT, DECISION_SCREENS,
    DEFAULT_CHARACTER, DEPLOY_BRIDGE, Defect, GAME_EXE, HAZARD_EVENT_TITLES,
    HAZARD_EVENTS, MAX_ACTIONS_PER_RUN, MENU_TIMEOUT_S, MID_FIGHT,
    NO_PROGRESS_ACTIONS, NO_PROGRESS_CYCLE, PROCESS_EXIT_GRACE_S,
    RUN_TIMEOUT_S, SCHEMA_VERSION, SELECTOR_SCREENS, SPEED_SIDECAR,
    STEAM_APPID, TIME_SCALE)
from understudy.soak_lane import (         # noqa: E402,F401  (re-export)
    bridge_installed, game_is_running, lane_setup)
from understudy.soak_session import (      # noqa: E402,F401  (re-export)
    Reversibility, Session)
from understudy.soak_telemetry import (    # noqa: E402,F401  (re-export)
    ENCORE_UNSEEN, FightTelemetry, METER_UNSEEN, SALON_PRINTED_CAP,
    _enemy_pool, _meters, _telegraphed)
from understudy.soak_screens import (      # noqa: E402,F401  (re-export)
    _escape, _first_of, _game_over_won, _hazard_event, _last_resort,
    _mechanical_action, _option_names, _trim_state)
from understudy.soak_navigate import (     # noqa: E402,F401  (re-export)
    Navigation, canonical_character, character_matches,
    _selectable_characters)
from understudy.soak_driver import RunDriver    # noqa: E402,F401 (re-export)


# --------------------------------------------- one run, someone else's -----
#
# THE FIXED-SCRIPT SEAM, FACTORED (EB-142). `probe_block.py` and
# `probe_corpse.py` each carried a byte-for-byte copy of the same eleven lines:
# build a Session, swap this module's `policy_v1` name for a scripted object,
# run ONE RunDriver, restore the name in a `finally`, tear down. A third caller
# (`scenario.py`) made the duplication a rule rather than a coincidence, so it
# lives here once, where the two objects it drives already live.
#
# WHAT IT IS NOT. It is not a policy, a second driver, or a way into the soak:
# the soak's own entry point below does not call it, and nothing here grants a
# card or writes a board. It is the SETUP-AND-TEARDOWN half a fixed script
# needs in order to reach an in-combat state at all -- the embark, the character
# verification, the seed read-back and the route to the first fight are
# `RunDriver`'s, unchanged, and the caller's object only decides what to do once
# a screen is in front of it.
#
# THE SWAP IS GONE, AND A LIVE TWO-LANE RUN IS WHY (`EB-206`, 2026-08-29).
# It used to rebind this MODULE'S `policy_v1` name for the duration of the run
# and restore it in a `finally`. That is safe for one run at a time and wrong
# the moment there are two: the funnel's first concurrent stage had lane 0's
# driver calling LANE 1'S policy, whose Runner had already closed its log --
# `I/O operation on closed file`, a cross-wired run wearing a harness
# exception, on a board nobody could have diagnosed from the log it did not
# write. The policy is now a FIELD on the driver that flies it, so two drivers
# in one process cannot see each other's, and no `finally` has to hold a
# global right. `run_begin` still records the FLYING policy's
# `POLICY_VERSION`, which is why every script here PREFIXES that string
# rather than replacing it.


def run_scripted(policy: Any, stamp: str,
                 character: str = DEFAULT_CHARACTER,
                 max_fights: int | None = 1,
                 chosen_seed: str | None = None,
                 do_setup: bool = True,
                 intent: str = "",
                 instance: "instances.Instance | None" = None,
                 install_bridge: bool = True) -> dict:
    """Drive ONE run with `policy` standing in for `policy_v1`.

    `policy` must offer what `RunDriver` reaches through the module for:
    `decide(state, memo, commit=None)`, `Memo`, `POLICY_VERSION`, and the two
    dial names the run record stamps. Delegating those to `policy_v1` rather
    than reimplementing them is the probes' pattern, and the reason a script
    overrides WHAT is chosen and never the bookkeeping around it.
    """
    session = Session(stamp, do_setup=do_setup, intent=intent,
                      instance=instance, install_bridge=install_bridge)
    try:
        session.setup()
        driver = RunDriver(session, 1, stamp, character=character,
                           max_fights=max_fights, chosen_seed=chosen_seed,
                           policy=policy)
        return driver.run()
    finally:
        session.teardown()


# ----------------------------------------------------------------- main ----

def soak(runs: int, character: str, do_setup: bool,
         commit: str | None = None,
         seeds: list[str] | None = None,
         max_fights: int | None = None,
         hazard_guard: bool = True,
         p2_capture: bool = False,
         lane: object = 0) -> dict:
    from understudy import committed as _committed
    commit = _committed.normalise(commit)          # refuses an unknown word
    stamp = time.strftime("%Y%m%d-%H%M%S")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    # `--lane N`. Lane 0 is `(None, True)` -- no instance, so everything below
    # is byte-for-byte the soak that ran before lanes existed, file names
    # included.
    instance, install_bridge = lane_setup(lane)
    # THE LANE KWARGS ARE PASSED ONLY WHEN THERE IS A LANE, the same way
    # `p2_capture` is passed to `RunDriver` below: a lane-0 soak calls this
    # constructor with the argument list it used before the flag existed,
    # which is what keeps the `Session` doubles in the pins working -- and is
    # the same claim as "lane 0 is unchanged", made where it can be checked.
    session = Session(stamp, do_setup=do_setup, intent=commit,
                      **({} if instance is None
                         else {"instance": instance,
                               "install_bridge": install_bridge}))
    summaries: list[dict] = []
    # THE LANE IS IN THIS NAME TOO, for the reason `RunDriver.log` carries it:
    # two soaks starting in the same second would otherwise write one index
    # over the other. A lane-0 soak adds no infix.
    infix = f"-{instance.label}" if instance is not None else ""
    index = LOG_DIR / f"soak-{stamp}{infix}-index.json"
    # READ OFF THE INSTANCE AND NOT OFF THE SESSION, because a soak's Session
    # is a test double in half a dozen pins and a double has no `label`. Same
    # answer either way: `Session.label` is its instance's, or the thread's.
    lane_label = (instance.label if instance is not None
                  else bridge.current_label())
    shapes: dict[str, int] = {}
    stopped = None
    # EB-117. The character the runs ACTUALLY flew, read off the wire by the
    # first run that got far enough to be asked. Stays `None` for a soak that
    # never embarked, and `None` is what the index and the report header then
    # carry -- the requested string is recorded separately and never promoted
    # to the name of the thing that was measured.
    verified: str | None = None
    try:
        session.setup()
        for i in range(1, runs + 1):
            print(f"--- run {i}/{runs} ---", flush=True)
            deckwatch.reset()
            # P1.5: run i takes seed i, cycling if fewer seeds than runs were
            # named. `None` throughout is the read-back arm, unchanged.
            chosen = seeds[(i - 1) % len(seeds)] if seeds else None
            driver = RunDriver(session, i, stamp, character, commit=commit,
                               chosen_seed=chosen, max_fights=max_fights,
                               hazard_guard=hazard_guard,
                               **({"p2_capture": True} if p2_capture else {}))
            s = driver.run()
            verified = verified or driver.character_actual
            s["defect_kinds"] = [d["kind"] for d in driver.defects]
            summaries.append(s)
            print(f"    {s['outcome']}  seed={s['seed']}  "
                  f"actions={s['actions']}  fights={s['fights']}  "
                  f"defects={s['defects']}", flush=True)
            index.write_text(json.dumps(
                {"stamp": stamp, "character": verified,
                 "character_requested": character,
                 "policy": policy_v1.POLICY_VERSION, "commit": commit,
                 "seeds": seeds, "instance": lane_label,
                 "requested_runs": runs, "runs": summaries}, indent=1),
                encoding="utf-8")

            # STOP-AND-SURFACE: two failures of the same HARNESS-side shape is
            # a broken instrument, not a found bug, and continuing would fill
            # the night with the same row.
            for kind in s["defect_kinds"]:
                if kind in _HARNESS_SIDE:
                    shapes[kind] = shapes.get(kind, 0) + 1
                    if shapes[kind] >= 2:
                        stopped = kind
            if stopped:
                print(f"    STOP-AND-SURFACE: two harness-side '{stopped}' "
                      f"failures; soak halted", flush=True)
                break
            # A DEFECT RUN IS NOT TRUSTED TO LEAVE A CLEAN STATE, and the
            # first validation soak proved why: a run that stalled inside a
            # `card_select` left the game sitting in it, and the NEXT run's
            # first read was `unexpected_start_state` -- one defect
            # manufacturing another, which is how a soak report fills with
            # rows that are all the same row. Relaunching is the only recovery
            # the wire actually offers: there is no verb that escapes an
            # arbitrary mid-run screen.
            needs_restart = _needs_restart(s["outcome"], session.alive())
            if needs_restart and i < runs:
                if do_setup:
                    print("    restarting the game to clear the run state",
                          flush=True)
                    session.restart()
                else:
                    # --no-setup MAY NOT RESTART -- it promised the game dir
                    # it would change nothing -- so the one thing it can do
                    # is say out loud that the runs after this one start
                    # from a run state it did not clear.
                    print(f"    WARNING: run {i} ended '{s['outcome']}' and "
                          f"needs a restart, but --no-setup forbids one; the "
                          f"remaining runs start from an uncleared game",
                          flush=True)
    finally:
        session.teardown()

    result = {"stamp": stamp, "character": verified,
              "character_requested": character,
              "policy": policy_v1.POLICY_VERSION, "commit": commit,
              "seeds": seeds, "instance": lane_label,
              "requested_runs": runs, "runs": summaries,
              "hazard_guard": hazard_guard,
              "stopped_on": stopped,
              "reversibility": session.ledger.entries}
    index.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print()
    print("REVERSIBILITY LOG (game dir)")
    print(session.ledger.table())
    return result


# Outcomes that leave the game PARKED INSIDE A RUN. `died` and `won` walk out
# through game-over on their own; these two do not, and the next run's first
# read is then `unexpected_start_state` -- one run manufacturing the next
# one's defect.
#
# `bounded` is here because `--max-fights` stops mid-run BY DESIGN: the run
# ends on a rewards screen with the map still open. The first version of this
# gate listed `defect` only, so a bounded soak restarted for nothing and
# killed every even-numbered run -- a `runs=6, max_fights=4` drive measured
# seeds 1 and 3 and reported six. A clean stop still leaves an unclean game.
_PARKED_OUTCOMES = frozenset({"defect", "bounded"})


def _needs_restart(outcome: str, alive: bool) -> bool:
    """Whether the NEXT run can start from what this run left behind."""
    return (outcome in _PARKED_OUTCOMES) or not alive


# Defect kinds that indicate the HARNESS is broken rather than the build.
# A game crash or a soft-lock is the soak working; these are the soak failing.
# `seed_not_honoured` is HERE and not on the build's side of the line: the
# game rolling its own seed is the game behaving normally, and the thing that
# failed is this harness's claim to have chosen one.
# `state_type_missing` sits here for the same reason `bridge_unreachable` does:
# not because the wire is the harness's fault, but because a soak that keeps
# arriving at a state it cannot name produces no telemetry, and two of them is
# the signal to stop rather than to burn the night.
#
# `unresponsive_spin` and `hazard_event` are DELIBERATELY ABSENT. Both are the
# soak catching EB-1, which is the soak working; a second one is a second
# observation of a live-play hazard, not a broken instrument. `hazard_event`
# in particular costs one run and recovers on its own -- the restart path's
# `abandon_run` is the recorded recovery for the poisoned save.
# EB-117's three kinds join `seed_not_honoured` here, which is the same shape
# exactly: the instrument was told to measure one thing and measured another,
# so a second occurrence halts the soak instead of filling the night with runs
# nobody can quote.
_HARNESS_SIDE = {"no_embark_path", "no_embark", "embark_loop", "menu_loop",
                 "unexpected_start_state", "bridge_unreachable", "no_action",
                 "seed_not_honoured", "state_type_missing",
                 "character_not_offered", "character_mismatch",
                 "character_unverified"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--character", default=DEFAULT_CHARACTER,
                    help="the character-select OPTION ID, not a roster id "
                         "(KLEEMOD-FURINA, KLEEMOD-KLEE, KLEEMOD-KOKOMI). "
                         "EB-117: a name the select screen does not offer "
                         "fails before the embark, and the character the run "
                         "actually starts with is read back and stamped")
    ap.add_argument("--no-setup", action="store_true",
                    help="attach to an already-running game; make no game-dir "
                         "changes and revert none")
    ap.add_argument("--report", action="store_true",
                    help="print the morning report for this soak when it ends")
    ap.add_argument("--commit", default=None,
                    help="R99/4b: declare an archetype and draft with its "
                         "cards prioritised (fanfare / salon / spotlight). "
                         "OFF by default -- without it this is the baseline "
                         "arm R98 validated, unchanged")
    ap.add_argument("--max-fights", type=int, default=None, metavar="N",
                    help="P1.5: stop the run cleanly after N closed fights. "
                         "Off by default; a bounded run is for COMPARING two "
                         "recordings of one seed, not for soaking")
    ap.add_argument("--seed", action="append", default=None, metavar="SEED",
                    help="P1.5: run on a CHOSEN seed instead of one the game "
                         "rolls. Repeatable; run i takes seed i, cycling. A "
                         "run whose read-back disagrees with its choice files "
                         "a `seed_not_honoured` defect rather than continuing")
    ap.add_argument("--p2-capture", action="store_true",
                    help="P2 leg one (R94): at every combat TURN OPENING that "
                         "trips the hard-state triggers, write the state and "
                         "both policies' decisions to understudy/logs/p2/ for "
                         "later LLM comparison. CAPTURE ONLY -- no model is "
                         "called from the run loop. The thresholds are a "
                         "PLACEHOLDER, not a ratified definition, and every "
                         "record says so (understudy/p2capture.py)")
    ap.add_argument("--lane", default=0, metavar="N",
                    help="which game instance to run in. 0 (the default) is "
                         "the machine's own %%APPDATA%% and port 15526 -- the "
                         "single-instance soak exactly as it was. 1 launches "
                         "a SECOND game out of the same install, on port "
                         "15527 and its own disposable user tree "
                         "(%%LOCALAPPDATA%%\\gits-lanes\\lane1), so a run can "
                         "play beside a game somebody else is playing. A "
                         "lane-1 run is NOT a run of record")
    ap.add_argument("--allow-hazard-events", action="store_true",
                    help="EB-1: drive the events on the hazard register "
                         "instead of stopping the run at them. It exists for "
                         "deliberately reproducing a known soft-lock; an "
                         "unattended soak wants the guard on, which is the "
                         "default")
    args = ap.parse_args(argv)

    # EB-93: declare the CONSOLE's encoding before anything prints a card
    # title. The soak's own progress lines quote resolved names too, so this
    # sits above the run and not just above the report.
    from understudy import report as _report
    _report.console_safe()

    try:
        # THE LANE IS CHECKED BEFORE ANYTHING HAPPENS. A typo'd number should
        # not create a log directory, resolve a game directory or open a
        # Session before it is refused.
        instances.label_for(args.lane)
        result = soak(args.runs, args.character, do_setup=not args.no_setup,
                      commit=args.commit, seeds=args.seed,
                      max_fights=args.max_fights,
                      hazard_guard=not args.allow_hazard_events,
                      p2_capture=args.p2_capture, lane=args.lane)
    except ValueError as exc:
        print(f"lane error: {exc}", file=sys.stderr)
        return 2
    if args.report:
        from understudy import report
        print()
        print(report.render(result["stamp"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
