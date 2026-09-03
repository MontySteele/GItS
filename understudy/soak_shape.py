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
MENU_TIMEOUT_S = 180.0

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
