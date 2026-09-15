"""The soak's fixed shapes: paths, watchdog dials, registers, `Defect`.

Cut out of `soak.py` by `EB-180`, and that is the whole of the change: every
name here is the one that file declared, at the value it declared, and
`soak.py` re-exports all of them, so `soak.GAME_EXE` and `soak.Defect` still
resolve. It sits at the BOTTOM of the seam stack -- it imports nothing from
this package -- so every other seam can read a constant off it without an
import cycle.

WHAT IS NOT HERE, AND WHY. The dials a test reaches in and swaps (`LOG_DIR`,
`LOCAL_PROPS`, `SETTLE_S`, `PID_EXIT_*`) stay on `soak.py` itself, together
with the wire: a `monkeypatch.setattr(soak, "bridge", fake)` has to reach the
seam that uses it, so those names have ONE home and the seams read them back
off `soak` at call time (`soak_session._soak`).
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DEPLOY_BRIDGE = REPO / "klee-mod" / "build" / "deploy_bridge.ps1"

# Where `deploy_bridge.ps1` stages the vendored bridge, relative to the game
# directory, and the two files it stages there. ONE directory for every lane
# AND for the owner's own Steam launches -- that is what "shared install" means
# in practice, and it is why no session in this harness ever removes it
# (`EB-310`).
BRIDGE_RELATIVE = Path("mods") / "STS2_MCP"
BRIDGE_DLL = "STS2_MCP.dll"
BRIDGE_MANIFEST = "STS2_MCP.json"

# Where `GitsSpeed.cs` persists the pre-soak `PrefsSave.FastMode` (EB-87),
# relative to the game directory. It is written on enable and deleted by a
# successful disable, so its PRESENCE at teardown means the disable never
# landed and the setting is still changed. JSON content under a `.conf` name:
# ModManager parses every `*.json` under `mods/` as a mod manifest.
SPEED_SIDECAR = BRIDGE_RELATIVE / "GitsSpeed.original.conf"

STEAM_APPID = "2868840"
GAME_EXE = "SlayTheSpire2.exe"
DEFAULT_CHARACTER = "KLEEMOD-FURINA"

# --------------------------------------------------------------- dials ----
# Harness timings. None of these is a balance number; all are watchdog bounds.

# How long to wait for the MENU (not the HTTP server) after launching. Boot to
# a usable bridge measured ~50 s in P0; three times that is a hang.
#
# EB-763 MADE THIS A BASE RATHER THAN THE BOUND. It is the right number for a
# fresh profile and the wrong one for a used one: the game rewrites the
# profile's whole run-history store to the Steam remote store on every boot,
# and the store only grows.
MENU_TIMEOUT_S = 180.0

# ------------------------------------------------- EB-763: the boot tax ----
#
# WHAT HAPPENED. Four of the nine batches of the Teyvat spike's proof round
# died on `menu never became ready within 180s` with the game alive and the
# bridge already answering (`[STS2 MCP] v0.4.0 server started`); the stall
# worsened as the batches themselves added run history, and batches of four
# were the workaround, which is why that round's tally is 14 and not 20
# (`review/records/teyvat-spike-proofs-2026-09-15.md`, "An operational finding
# that is not the arm's"). The store was **869 files, 23 MB** at
# `%APPDATA%\SlayTheSpire2\steam\<id>\modded\profile1\saves\history\`.
#
# NOTHING HERE DELETES IT, PRUNES IT OR MOVES IT. It is the owner's play
# history, and a harness that trims a profile to make its own watchdog pass
# has broken the thing it was measuring. The store is READ, and the watchdog
# is scaled to what it finds.
#
# WHERE THE RATE COMES FROM. Boot to a usable menu is ~50 s on a fresh profile
# (the P0 measurement above), and the observed batches ran PAST 180 s at ~869
# files -- so the store was already costing more than (180 - 50) / 869 =
# 0.15 s per file, and that is a LOWER BOUND rather than a measurement: those
# waits were cut off, not completed. `1 s per 5 files` is 0.2 s per file,
# ~1.35x that lower bound, which is the headroom a watchdog wants and still
# well short of turning itself off: at today's store it asks for 354 s where
# the base asked for 180 s, and a game that really has hung still fails, six
# minutes later instead of three.
#
# THE CAP IS NOT DECORATION. Without it a store that grew without bound would
# take the menu watchdog with it, and an overnight round would spend the night
# waiting on a game that died at boot. 900 s is fifteen minutes, reached at
# 3,600 files -- about four times today's store.
MENU_TIMEOUT_FILES_PER_S = 5.0
MENU_TIMEOUT_MAX_S = 900.0

# ----------------------------------------------- EB-766: the boot stall ----
#
# EB-763 SCALED THE WAIT; IT DID NOT EXPLAIN THE OUTLIERS. The fairness read
# of 2026-09-15 launched 30 times: 24 games reached the menu in about 20 s and
# 6 blew the whole scaled budget -- up to 426 s of an overnight round spent
# waiting on a process that was never going to answer. The two populations do
# not overlap, so the long tail is not "a bigger store took longer". It is a
# different failure wearing the budget's clothes.
#
# WHAT A GOOD BOOT LOOKS LIKE. 25 sessions were measured off
# `understudy/logs/soak/reversibility-*.json` (entry 3's `ts` is the launch,
# entry 4's is the first line after `wait_for_menu` returned): 15.6 s to
# 27.4 s, and the spread does NOT track the store's size. In `godot.log` the
# boot is `[INFO] OVERWRITING cloud saves with local saves.`, then ~811
# `Wrote N bytes to ... in steam remote store` lines, then
# `Profile-scoped data path initialized: user://steam/...` -- which is the
# marker that the profile is up and the menu is close behind.
#
# WHAT A STALLED BOOT LOOKS LIKE. The process is alive. `GET /` answers `ok`.
# `GET /api/v1/singleplayer` never returns, because that route hops to the
# game thread and waits there with no timeout -- the EB-489 shape, which
# `understudy/hangwatch.py` already carries the diagnosis for. The log stops
# growing and the profile marker never lands. A relaunch one second later
# boots normally, every time it was tried.
#
# WHAT PRECEDES ONE. 3 of the 8 launches that followed a game which had lived
# under 40 s and was killed 1.1 s earlier stalled; 0 of the 12 that followed a
# longer session did. Steam is still tearing the previous client session down
# when the next process asks it for the remote store, so the fix has two
# halves: DO NOT RELAUNCH INTO THE TEARDOWN (`RELAUNCH_DEAD_GAP_S`), and when
# it happens anyway, notice in 45 s rather than in 426 (everything else here).
#
# WHY 45 s. It is 1.6x the slowest good boot measured, which is the margin a
# watchdog wants over a population whose spread is 12 s wide. The cost of a
# false positive is one relaunch; the cost of a false negative was the four
# lost batches EB-763 is about.
BOOT_STALL_AFTER_S = 45.0
# HOW LONG A STATE ANSWER COUNTS FOR, and the whole of the 2026-09-15 miss.
#
# The fuse as first written asked "has `/api/v1/singleplayer` EVER answered"
# and read a yes as proof that the game thread was not wedged. That is a
# LATCH, and `wait_for_menu`'s own docstring says why it is the wrong shape:
# "The HTTP server answers ~20 s before the main menu has buttons." So on an
# ordinary boot the latch closes around 20 s -- before the 45 s fuse is ever
# consulted -- and from that moment the fuse is off for the life of the watch
# no matter what the game does next. Launch 6 of
# the deploy proofs of 2026-09-15 are the bill (`git show
# d47d9fcc:review/records/teyvat-proofs-5-2026-09-15.md`, launch 6): the root
# endpoint answered, the profile marker never landed, `godot.log` froze at
# 21,753 bytes, and the watch spent its whole 444 s budget without printing a
# word, because one early pre-menu answer had already disarmed it.
#
# THE SIGNAL IS "ANSWERED RECENTLY", NOT "ANSWERED ONCE". 25 s, because
# `bridge._request` carries a 20 s socket timeout: a single poll that times
# out is already proof of 20 s of silence, and 25 gives that one poll of
# slack before it is called a wedge. A boot that is merely slow answers every
# poll and never goes quiet for that long.
BOOT_STALL_STATE_QUIET_S = 25.0
# How long the log may stand still, once the profile marker HAS landed, before
# a boot with a live root endpoint and a dead state endpoint is called a
# stall. A boot that is merely slow is still writing store lines.
BOOT_STALL_LOG_QUIET_S = 15.0
# Kill-sleep-relaunch this many times before falling back to the full scaled
# budget from `menu_timeout_for`. Two, because the live read never saw a
# second consecutive stall and because three relaunches cost more than the
# budget they are saving.
BOOT_STALL_RETRIES = 2
# The dead gap between killing a game and launching the next one, and the
# first half of EB-766's fix (see the block above: the stalls followed a kill
# 1.1 s before the launch). It is a floor under EVERY relaunch this session
# makes -- the stall retry, `restart()`, and a second `setup()` in the same
# process -- because the thing being waited out is Steam's teardown, not ours.
RELAUNCH_DEAD_GAP_S = 10.0
# How often the boot watch looks at its three signals. `bridge._request`
# carries a 20 s socket timeout of its own, so a hung state endpoint sets the
# real cadence; this is the floor, not the period.
BOOT_POLL_S = 2.0
# The line in `godot.log` that says the profile is up. Matched as a substring:
# the path that follows it is the machine's business.
PROFILE_READY_MARKER = "Profile-scoped data path initialized"
# Where a session's `godot.log` is copied at teardown. Godot keeps five logs
# and a stalled boot is usually diagnosed the morning after, by which time the
# fifth relaunch has rotated the evidence out -- which is why the six stalled
# boots of 2026-09-15 have no logs at all.
GODOT_LOG_ARCHIVE = REPO / "understudy" / "logs" / "godot"

# --------------------------------------- EB-766: the archive is bounded ----
#
# THE ARCHIVER COPIED 2.56 GB. The Punch-Off VFX spin of 2026-09-15 wrote
# 2,561,687,155 bytes of `godot.log` in about two minutes -- 613,190 repeated
# `Parameter "particles" is null` lines -- and the teardown dutifully copied
# every byte of it beside the log it came from. An unattended batch that hit
# that twice would write five gigabytes of log and five gigabytes of archive.
#
# WHAT A TRUNCATED ARCHIVE STILL ANSWERS. The two questions ever asked of one
# of these files are "what did the boot do" (the head: mod load order, the
# port, the bridge's start line, the store rewrite) and "what was it doing
# when it went wrong" (the tail). The megabytes in between a spin are the
# same line repeated and carry nothing the head and tail do not.
ARCHIVE_LOG_MAX_BYTES = 8_000_000
ARCHIVE_LOG_HEAD_BYTES = 1_000_000
ARCHIVE_LOG_TAIL_BYTES = 4_000_000
# Written on its own line between the two halves, so nobody reads the seam as
# the game's own output. `{n}` is the byte count dropped.
ARCHIVE_LOG_TRUNCATION_MARK = (
    "\n\n[understudy] ---- {n} bytes omitted by the archiver (EB-766): this "
    "log exceeded {cap} bytes, so the first {head} and the last {tail} are "
    "kept and the middle is dropped ----\n\n")


def boot_stall_verdict(elapsed_s: float, health_ok: bool, state_recent: bool,
                       marker_seen: bool, log_quiet_s: float) -> bool:
    """`EB-766`. Does this boot look STALLED rather than merely slow?

    Pure, so the judgment is exercised off a test rather than off a night that
    went wrong. The three signals are the root endpoint (answered from a
    ThreadPool worker, so it survives a game-thread stall), whether the state
    endpoint has answered WITHIN THE LAST `BOOT_STALL_STATE_QUIET_S` (the
    block above says why that is not "ever"), and the log -- its size and
    whether the profile marker has landed. The block above also carries the
    provenance of every number here.
    """
    if elapsed_s < BOOT_STALL_AFTER_S:
        return False
    # A state endpoint that is still answering is not stalled on the game
    # thread, and a root endpoint that is silent is a dead process or a dead
    # wire -- neither is this defect, and a relaunch is not its answer.
    if state_recent or not health_ok:
        return False
    return (not marker_seen) or log_quiet_s >= BOOT_STALL_LOG_QUIET_S


def menu_timeout_for(history_files: int) -> float:
    """The menu-ready wait for a profile whose run-history store holds N files.

    `MENU_TIMEOUT_S + N / MENU_TIMEOUT_FILES_PER_S`, capped at
    `MENU_TIMEOUT_MAX_S`. Pure, so the dial is read off a test rather than off
    a night that went wrong; the block above carries the rate and the cap.
    """
    if history_files <= 0:
        return MENU_TIMEOUT_S
    return min(MENU_TIMEOUT_MAX_S,
               MENU_TIMEOUT_S + history_files / MENU_TIMEOUT_FILES_PER_S)

# The state-progress watchdog: if the state FINGERPRINT (screen + floor + hp +
# hand shape + enemy hp) is unchanged across this many consecutive posted
# actions, the run is not progressing. Combat legitimately repeats a screen
# type, which is why the fingerprint is not just `state_type`.
NO_PROGRESS_ACTIONS = 12
# ...and at most this many DISTINCT fingerprints inside that window. 1 catches
# a frozen screen; 2 catches the A-B-A-B bounce between a screen and the
# overlay it keeps reopening, which is the shape a real soak actually hit.
NO_PROGRESS_CYCLE = 2
# Hard ceiling per run. A three-act run is a few thousand actions; ten thousand
# is a spin.
MAX_ACTIONS_PER_RUN = 10000
# Wall-clock ceiling per run, so an overnight soak cannot be eaten by one run.
RUN_TIMEOUT_S = 3600.0
# TimeScale for the speed endpoint. Animation pacing only -- GitsSpeed.cs
# touches no rules code. 3.0 is what Phase 0 ran at without incident.
TIME_SCALE = 3.0
# How long a bridge failure waits before deciding the process is NOT the cause.
# A crashing game resets the socket before the OS reaps it, so "is the process
# alive" asked in the same millisecond answers the wrong question. See
# `Session.died`.
PROCESS_EXIT_GRACE_S = 8.0

# ---------------------------------------------------------- EB-1 guard ----
#
# EVENTS THIS HARNESS WILL NOT DRIVE, and why the register is a register rather
# than a special case in `_mechanical_action`.
#
# `PUNCH_OFF` is EB-1: entering the room hangs the game. `PunchOff` fires
# `PunchEachOther()` from `AfterEventStarted()`, so the hazard is ENTRY, not an
# option -- there is no answer to this screen that avoids it, and picking one
# would be picking blind anyway (the frozen frame carried no options at all).
#
# THE WIRE ID IS READ, NOT GUESSED. `EventRoom.CanonicalEvent.Id.Entry` is
# `ModelDb.GetEntry(type) == StringHelper.Slugify("PunchOff")`, and Slugify
# splits camel case and upper-cases: `PUNCH_OFF`. The event's own loc keys
# (`PUNCH_OFF.pages.INITIAL.options.NAB`) are the same string, which is the
# second reading. The display TITLE is matched too, because a title is loc data
# and a bridge that ever reported one instead of the other should still be
# caught.
#
# WHAT THE GUARD CAN AND CANNOT DO. It fires only if the bridge SURVIVED the
# room entry -- if the spin has already started there is no state to read, and
# `hangwatch` is the leg that catches that. Avoiding the room itself is not
# available from here: the map on the wire carries a node's `type` only
# (`Event`), never which event, so nothing short of refusing every `?` node
# could dodge it, and that would be a route-policy change nobody asked for.
HAZARD_EVENTS = {
    "PUNCH_OFF": "EB-1: entering this room spins the main thread on an "
                 "unbounded engine-error loop (godot.log grew to 2.4 GB in "
                 "~30 min live on 2026-08-08). Root-caused upstream; there is "
                 "no fix on our side and no safe option to pick.",
}
# Display titles, lower-cased, mapping to the id whose note they carry. The
# second reading of the same screen, kept because a screen this harness must
# not drive is worth catching twice.
HAZARD_EVENT_TITLES = {"punch off": "PUNCH_OFF"}

# Telemetry schema version, stamped on every fight record and mirrored by the
# C# human-feed writer (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`). Bump
# on a BREAKING change only -- adding a key is free, renaming one is a
# cross-session change (understudy/README.md).
SCHEMA_VERSION = "1"

# --------------------------------------------------------------- driver ----

COMBAT = ("monster", "elite", "boss")
# Screens that interrupt a fight WITHOUT ending it. Furina's Ethereal Spotlight
# opens `card_select` every turn; treating that as the end of the fight split
# one floor-2 fight into five records in the first validation soak, each with
# its own turn count and its own HP ledger.
MID_FIGHT = ("card_select", "hand_select", "bundle_select", "overlay")
# The subset of MID_FIGHT that ASKS SOMETHING. `overlay` is excluded on
# purpose: it is the shape a soft-lock takes (bridge.py's own docstring says
# so), and a screen nobody can answer has no choice to record.
SELECTOR_SCREENS = ("card_select", "hand_select", "bundle_select")
DECISION_SCREENS = {"monster", "elite", "boss", "card_reward", "map",
                    "rest_site", "shop", "fake_merchant", "relic_select",
                    "card_select", "bundle_select", "hand_select",
                    "crystal_sphere", "event", "game_over"}


class Defect(Exception):
    """A run-ending condition worth a filed record. Not a bug in this file."""

    def __init__(self, kind: str, detail: str, state: dict | None = None):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail
        self.state = state or {}
