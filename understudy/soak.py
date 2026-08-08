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
  * the seeds are READ-BACK, not chosen (R95), so no soak number is comparable
    to another build's soak number until the Custom-screen arm exists;
  * a JSON-state agent cannot see the screen, so nothing here is evidence
    about fun, legibility, or readability, ever.

Winrate, floors reached, HP curves and damage tables from this harness are
DEFECT-HUNTING INSTRUMENTS and telemetry. They are not balance evidence, they
do not grade a character, and they may not be quoted against a floor.

SEEDS (R95). Read-back: the game generates the seed, we record it from
`GET /api/v1/compendium` after embarking, and it identifies the run for a
defect report. The recorded seed is NEVER fed to a policy stream --
`understudy.rng.policy_rng` refuses a label shaped like one, and the refusal is
the enforcement.

READINESS (R97/5a). The launcher watches for the `options` key in the menu
state, NEVER the HTTP health endpoint. `GET /` answers about 5 s after launch;
the main menu has no buttons for another ~20. A launcher that trusts the health
check acts into an empty menu, which is a soft-lock we would then have to
diagnose as if it were the game's fault.

REVERSIBILITY. Every game-dir write is recorded in a ledger with its undo, the
ledger is written to disk BEFORE the change is made, and teardown walks it in
reverse. Appendix A of `docs/archive/understudy-phase0-report.md` is the format this
inherits and the checklist it is measured against.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from understudy import bridge, deckwatch, naming, policy_v1

REPO = Path(__file__).resolve().parent.parent
LOG_DIR = Path(__file__).resolve().parent / "logs" / "soak"
LOCAL_PROPS = REPO / "klee-mod" / "local.props"
DEPLOY_BRIDGE = REPO / "klee-mod" / "build" / "deploy_bridge.ps1"

STEAM_APPID = "2868840"
GAME_EXE = "SlayTheSpire2.exe"
DEFAULT_CHARACTER = "KLEEMOD-FURINA"

# --------------------------------------------------------------- dials ----
# Harness timings. None of these is a balance number; all are watchdog bounds.

# How long to wait for the MENU (not the HTTP server) after launching. Boot to
# a usable bridge measured ~50 s in P0; three times that is a hang.
MENU_TIMEOUT_S = 180.0
# A single action's settle poll.
SETTLE_S = 0.7
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

# Telemetry schema version, stamped on every fight record and mirrored by the
# C# human-feed writer (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`). Bump
# on a BREAKING change only -- adding a key is free, renaming one is a
# cross-session change (understudy/README.md).
SCHEMA_VERSION = "1"


# ------------------------------------------------------------- ledger ----

@dataclass
class Reversibility:
    """The game-dir change log, written BEFORE each change lands.

    Written first on purpose: a ledger that is written after the change is a
    ledger that is empty exactly when the process dies mid-change, which is the
    one moment anybody needs it.
    """
    path: Path
    entries: list = field(default_factory=list)

    def record(self, change: str, undo: str, pre_existing: bool = False) -> dict:
        entry = {"n": len(self.entries) + 1, "change": change, "undo": undo,
                 "pre_existing": pre_existing, "state": "APPLIED",
                 "ts": time.time()}
        self.entries.append(entry)
        self.flush()
        return entry

    def revert(self, entry: dict, note: str = "") -> None:
        entry["state"] = "REVERTED"
        if note:
            entry["note"] = note
        self.flush()

    def fail(self, entry: dict, why: str) -> None:
        entry["state"] = "NOT REVERTED"
        entry["error"] = why
        self.flush()

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.entries, indent=1),
                             encoding="utf-8")

    def table(self) -> str:
        rows = ["| # | Change | Undo | State |", "|---|---|---|---|"]
        for e in self.entries:
            rows.append(f"| {e['n']} | {e['change']} | {e['undo']} | "
                        f"**{e['state']}**"
                        + (f" -- {e['error']}" if e.get("error") else "") + " |")
        return "\n".join(rows)


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


# -------------------------------------------------------------- session ----

class Session:
    """Setup, teardown, and the reversibility ledger between them."""

    def __init__(self, stamp: str, do_setup: bool = True,
                 intent: str | None = None):
        self.stamp = stamp
        self.do_setup = do_setup
        # Passed to the launched game so the mod's own hook labels its
        # records with the same declaration the bot feed is stamping.
        self.intent = intent
        self.dir = game_dir()
        self.ledger = Reversibility(LOG_DIR / f"reversibility-{stamp}.json")
        self.proc: subprocess.Popen | None = None
        self._appid_entry: dict | None = None
        self._bridge_entry: dict | None = None
        self._speed_entry: dict | None = None
        self._seed_entry: dict | None = None
        self._launch_entry: dict | None = None
        self.speed_before: dict | None = None

    # -- setup ------------------------------------------------------------
    def setup(self) -> None:
        if not self.do_setup:
            self._require_bridge()
            return
        self._steam_appid()
        self._deploy_bridge()
        self._launch()
        self.wait_for_menu()
        self._speed_on()

    def _steam_appid(self) -> None:
        p = self.dir / "steam_appid.txt"
        pre = p.exists()
        self._appid_entry = self.ledger.record(
            f"Created `steam_appid.txt` ({STEAM_APPID}) at the game root",
            "`Remove-Item steam_appid.txt`", pre_existing=pre)
        if pre:
            self.ledger.revert(self._appid_entry,
                               "pre-existing, left in place")
            self._appid_entry = None
            return
        p.write_text(STEAM_APPID, encoding="ascii")

    def _deploy_bridge(self) -> None:
        self._bridge_entry = self.ledger.record(
            "Deployed `mods\\STS2_MCP\\` from vendor pin 55e0648",
            "`.\\build\\deploy_bridge.ps1 -Remove`")
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-File", str(DEPLOY_BRIDGE)],
            cwd=str(REPO / "klee-mod"), capture_output=True, text=True)
        if r.returncode != 0:
            self.ledger.fail(self._bridge_entry,
                             "deploy failed; nothing was installed")
            self._bridge_entry = None
            raise SystemExit(f"bridge deploy failed:\n{r.stdout}\n{r.stderr}")

    def _launch(self) -> None:
        exe = self.dir / GAME_EXE
        if not exe.exists():
            raise SystemExit(f"game exe not found: {exe}")
        self._launch_entry = self.ledger.record(
            f"Launched `{GAME_EXE}` directly (Steam must be running)",
            "process terminated at teardown")
        # THE FEED LABEL IS SET HERE, NOT IN WHOEVER'S SHELL RAN THE SOAK.
        # The mod's own telemetry hook writes a record for every fight it sees,
        # labelled `human` unless told otherwise -- so a soak launched from a
        # shell that did not happen to export this variable writes bot-driven
        # play into the HUMAN feed, which is the one feed whose whole value is
        # that a person produced it. The README already claimed this happened
        # here; as of 2026-08-04 (late) it actually does.
        env = dict(os.environ)
        env["GITS_TELEMETRY_FEED"] = "bot"
        env["GITS_TELEMETRY_INTENT"] = self.intent or ""
        self.proc = subprocess.Popen([str(exe)], cwd=str(self.dir),
                                     env=env,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)

    def wait_for_menu(self, timeout: float = MENU_TIMEOUT_S) -> dict:
        """R97/5a. Poll for the `options` key on a menu state -- never `GET /`.

        The HTTP server answers ~20 s before the main menu has buttons. This is
        the difference between "the process is up" and "the game is ready", and
        it is the single cheapest bug in this file to have written correctly.
        """
        deadline = time.time() + timeout
        last = "(no response)"
        while time.time() < deadline:
            if self.proc is not None and self.proc.poll() is not None:
                raise SystemExit(
                    f"the game process exited during boot "
                    f"(code {self.proc.returncode}) -- check godot.log")
            try:
                state = bridge.get_state()
            except bridge.BridgeError as e:
                last = str(e)[:120]
                time.sleep(2.0)
                continue
            if state.get("state_type") == "menu" and state.get("options"):
                return state
            last = (f"state_type={state.get('state_type')} "
                    f"menu_screen={state.get('menu_screen')} options=absent")
            time.sleep(1.5)
        raise SystemExit(f"menu never became ready within {timeout:.0f}s; "
                         f"last read: {last}")

    def _require_bridge(self) -> None:
        try:
            bridge.get_state()
        except bridge.BridgeError as e:
            raise SystemExit(f"--no-setup given but no bridge is answering: {e}")

    def _speed_on(self) -> None:
        try:
            self.speed_before = bridge.get_speed()
        except bridge.BridgeError:
            self.speed_before = None
        self._speed_entry = self.ledger.record(
            f"Set FastMode=Instant and TimeScale={TIME_SCALE} via "
            f"`POST /api/v1/gits/speed` (captured: "
            f"{json.dumps(self.speed_before)})",
            '`POST {"enabled": false}` restores the captured originals')
        bridge.set_speed(True, TIME_SCALE)

    def note_seed_channel(self) -> None:
        """Declare the seed channel in the ledger, BEFORE the first seed lands.

        Recorded lazily rather than in `setup` for a reason `--no-setup` makes
        concrete: that mode deliberately makes no game-dir changes and runs no
        setup, but a chosen seed set through it is still a global, sticky
        property on a game somebody else launched. The undo has to be on the
        ledger in that mode too, so the trigger is the first CHOICE, not the
        setup. Idempotent -- N runs share one entry.
        """
        if self._seed_entry is not None:
            return
        self._seed_entry = self.ledger.record(
            "May set a chosen run seed via `POST /api/v1/gits/seed` "
            "(NGame.DebugSeedOverride is global and sticky)",
            '`POST {"seed": null}` clears both seed channels')

    # -- teardown ---------------------------------------------------------
    def teardown(self) -> None:
        """Walk the ledger in reverse. EVERY step runs, whatever the last did.

        A TEARDOWN THAT ABANDONS ITS OWN LEDGER IS WORSE THAN NO TEARDOWN, and
        this one did: the game died mid-run, `bridge.set_speed(False)` raised a
        `ConnectionResetError` (which is not a `BridgeError`), the exception
        left `teardown` at its first step, and `steam_appid.txt` and
        `mods/STS2_MCP` stayed in the game directory. The socket bug is fixed
        in `bridge._request`; this is the belt to its braces. Each step is
        independently guarded, every failure is recorded rather than raised,
        and the ledger is the report.
        """
        # THE SEED RELEASE GOES FIRST, and it runs unconditionally. The
        # `debug_override` route is a GLOBAL, STICKY property on NGame: left
        # set, every later run in the session -- including one a person starts
        # by hand -- is the same run. It is cheap and idempotent when no seed
        # was ever chosen, which is why it is not conditional on having chosen
        # one; the one moment a ledger matters is the moment nobody remembers
        # what was set.
        self._step(self._seed_entry, self._release_seed)
        self._step(self._speed_entry, self._restore_speed)
        self._step(self._launch_entry, self._stop_game)
        self._step(self._bridge_entry, self._remove_bridge)
        self._step(self._appid_entry, self._remove_appid)

    def _step(self, entry: dict | None, undo) -> None:
        if not entry:
            return
        try:
            self.ledger.revert(entry, undo())
        except Exception as e:                               # noqa: BLE001
            self.ledger.fail(entry, f"{type(e).__name__}: {e}")

    def _release_seed(self) -> str:
        after = bridge.clear_seed()
        return (f"chosen seed released (debug_override="
                f"{after.get('debug_override')!r})")

    def _restore_speed(self) -> str:
        after = bridge.set_speed(False)
        return (f"restored to {after.get('fast_mode')} / "
                f"{after.get('time_scale')}")

    def _stop_game(self) -> str:
        self._kill()
        return "process terminated"

    def _remove_bridge(self) -> str:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-File", str(DEPLOY_BRIDGE),
             "-Remove"],
            cwd=str(REPO / "klee-mod"), capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip()[:300] or "deploy_bridge -Remove failed")
        return "mods/STS2_MCP removed"

    def _remove_appid(self) -> str:
        p = self.dir / "steam_appid.txt"
        if p.exists():
            p.unlink()
        return "file removed"

    def _kill(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            for _ in range(20):
                if self.proc.poll() is not None:
                    break
                time.sleep(0.5)
            if self.proc.poll() is None:
                self.proc.kill()
        # Belt and braces: a game launched by an earlier crashed soak holds the
        # dll lock and would make the NEXT deploy_bridge run fail with a
        # message about a running game.
        subprocess.run(["taskkill", "/F", "/IM", GAME_EXE],
                       capture_output=True, text=True)

    def restart(self) -> None:
        """Kill and relaunch, keeping the ledger honest about the extra launch.

        Used after a defect run: the game may be parked on a screen no verb
        escapes, and a fresh process plus `abandon_run` is the only reliable
        way back to the main menu.
        """
        # THE SUPERSEDED ENTRIES ARE CLOSED BEFORE NEW ONES OPEN. A restart
        # reassigns `_launch_entry` and `_speed_entry`, so without this the old
        # rows sit at APPLIED forever and the ledger over-reports what is still
        # outstanding in the game directory. A reversibility log that cries
        # wolf is one nobody reads.
        self._step(self._launch_entry,
                   lambda: "process terminated (superseded by a restart)")
        if self._speed_entry:
            self.ledger.revert(
                self._speed_entry,
                "superseded by a restart; the setting does not survive the "
                "process and is re-captured below")
            self._speed_entry = None
        self._kill()
        self._launch()
        self.wait_for_menu()
        self._speed_on()

    def alive(self) -> bool:
        if self.proc is None:
            return True                      # --no-setup: not ours to judge
        return self.proc.poll() is None

    def died(self, grace: float = PROCESS_EXIT_GRACE_S) -> bool:
        """Has the game process exited -- allowing for one that is mid-crash?

        A CRASHING PROCESS IS NOT YET AN EXITED PROCESS, and the validation
        soak of 2026-08-04 was decided by that distinction. The game died
        inside a Punch Off event, the socket reset under the very next request,
        and `alive()` -- asked in the same millisecond -- still read True
        because the OS had not reaped the process yet. The failure was
        therefore filed as `bridge_unreachable`, which is a HARNESS-side kind:
        the instrument blamed its own wire for a build defect it had just
        caught, which is the one misreading that makes a soak report worse than
        no soak report.

        `alive()` is deliberately left instantaneous -- the per-action watchdog
        calls it on a hot path and a sleeping watchdog is a slow soak. This is
        the slow twin, called only where a failure has ALREADY happened and the
        question is who to blame.
        """
        if self.proc is None:
            return False                     # --no-setup: not ours to judge
        deadline = time.time() + max(0.0, grace)
        while True:
            if self.proc.poll() is not None:
                return True
            if time.time() >= deadline:
                return False
            time.sleep(0.25)

    @property
    def exit_code(self) -> int | None:
        return None if self.proc is None else self.proc.poll()


# ------------------------------------------------------------ telemetry ----
#
# THE SCHEMA IS DOCUMENTED IN `understudy/README.md` AND IS A SHARED SURFACE
# TO BE: Track B wants the same per-fight numbers out of the sim. Renaming a
# key here is a cross-session change once Track B reads it.

@dataclass
class FightTelemetry:
    """One fight's numbers, accumulated from state deltas.

    ATTRIBUTION RULE, stated because it is an approximation and a reader who
    does not know that would over-read the damage table:

      * damage BY SOURCE is the total enemy (hp + block) drop observed across
        the state read immediately after an action, attributed to the card or
        potion that action named. Anything that resolves later in the same
        frame batch lands on the play that triggered it, which is usually what
        you want (a summon's hit is the summon card's) and is occasionally
        wrong (a bomb detonating on a later play).
      * damage TAKEN is the player hp drop observed across a ROUND boundary,
        attributed to the enemy turn as a whole rather than per enemy -- the
        wire does not narrate which enemy landed which hit.
      * INCOMING per turn is the sum of the telegraphed attack intents read at
        the start of the player's turn, before any block.

    All three are floors on truth, not estimates of it: they under-attribute
    rather than invent.
    """
    act: int
    floor: int
    kind: str
    # R99/4a. The DECLARED deck intent for the run this fight belongs to: the
    # committed archetype on the bot feed, whatever the person wrote in
    # `intent.txt` on the human feed, `""` when nobody declared anything. It is
    # a declaration, never an inference -- nothing reads the deck and guesses.
    intent: str = ""
    enemies: list = field(default_factory=list)
    hp_start: int = 0
    max_hp: int = 0
    turns: int = 0
    hp_trajectory: list = field(default_factory=list)     # [(round, hp, block)]
    incoming_by_turn: list = field(default_factory=list)  # [(round, dmg, n_atk)]
    # TRACK B ADDITIONS (2026-08-04). Keys only ADDED -- nothing renamed, which
    # is what the shared-schema rule in understudy/README.md costs and permits.
    enemy_pool_by_turn: list = field(default_factory=list)  # [(round, pool)]
    meters_by_turn: list = field(default_factory=list)  # [(rnd, fanfare, salon,
    #                                                     salon_cap, encore)]
    block_at_turn_end: list = field(default_factory=list)   # [(round, block)]
    cards_played: list = field(default_factory=list)      # [(round, name)]
    # P1.5 ADDITION (2026-08-05), spec item 3. Every SELECTOR screen resolved
    # inside this fight: [round, screen_type, index, chosen name, offered names].
    #
    # WHY THE OFFERED LIST IS IN THE ROW. A choice is not reconstructible from
    # what was taken alone -- "Center Stage" means one thing against
    # [Center Stage, Guest Cast] and nothing at all against a list that did not
    # contain Guest Cast. This is the same denominator rule `hand` already
    # applies to a card play, for the same reason.
    #
    # `-1` in the index slot is a selector resolved without one (a confirm, a
    # skip); the verb is legible from `screen_type` plus the empty chosen name.
    selectors: list = field(default_factory=list)
    potions_used: list = field(default_factory=list)
    damage_by_source: dict = field(default_factory=dict)
    damage_taken: int = 0
    hp_end: int = 0
    outcome: str = "unknown"

    def as_record(self) -> dict:
        return {
            "record": "fight", "schema": SCHEMA_VERSION,
            # THE FEED LABEL IS PART OF THE RECORD, not part of the filename.
            # Guardrail 7 says every Track B curve is labelled with its feed;
            # a label that lives in a path is a label that is lost the first
            # time somebody concatenates two files.
            "feed": "bot", "source": "soak", "intent": self.intent,
            "seats": 1, "seat_index": 0,
            "act": self.act, "floor": self.floor,
            "kind": self.kind, "enemies": self.enemies,
            "hp_start": self.hp_start, "hp_end": self.hp_end,
            "max_hp": self.max_hp, "hp_lost": self.hp_start - self.hp_end,
            "turns": self.turns, "outcome": self.outcome,
            "hp_trajectory": self.hp_trajectory,
            "incoming_by_turn": self.incoming_by_turn,
            "enemy_pool_by_turn": self.enemy_pool_by_turn,
            "meters_by_turn": self.meters_by_turn,
            "block_at_turn_end": self.block_at_turn_end,
            "cards_played": self.cards_played,
            "n_cards_played": len(self.cards_played),
            "selectors": self.selectors,
            "potions_used": self.potions_used,
            "damage_by_source": {k: round(v, 1)
                                 for k, v in sorted(self.damage_by_source.items())},
            "damage_dealt": round(sum(self.damage_by_source.values()), 1),
            "damage_taken": self.damage_taken,
        }


_INTENT_LABEL = re.compile(r"^(\d+)(?:\s*[x×]\s*(\d+))?$")


def _telegraphed(state: dict[str, Any]) -> tuple[int, int]:
    """(total telegraphed damage, number of attacking enemies) this turn."""
    from understudy import adapter
    total = attackers = 0
    for e in adapter.enemy_blobs(state):
        if int(e.get("hp", 0)) <= 0:
            continue
        blob = e.get("intents") or e.get("intent")
        if isinstance(blob, list):
            blob = blob[0] if blob else None
        if not isinstance(blob, dict):
            continue
        if str(blob.get("type", "")).lower() != "attack":
            continue
        m = _INTENT_LABEL.match(str(blob.get("label") or "").strip())
        if not m:
            continue
        dmg = int(m.group(1)) * (int(m.group(2)) if m.lastindex and m.lastindex >= 2
                                 and m.group(2) else 1)
        total += dmg
        attackers += 1
    return total, attackers


_METER_IDS = {
    "FANFARE_METER_POWER": 0,
    "SALON_MEMBER_POWER": 1,
}

# UNSEEN, NOT EMPTY. -1 is what this file records for a meter the wire did not
# carry on the read it was taken from. A zero would be a measurement claiming
# the meter was empty in fights where it demonstrably was not.
#
# ENCORE WAS UNSEEN ON EVERY BOT FIGHT UNTIL P1.5, and the sentence that used
# to stand here -- "Encore is not on the wire and cannot be" -- was right about
# the wire and wrong about "cannot". `EncoreMeterPower` was retired as a
# display in animation sprint 2 (E1), so Encore left `creature.Powers`, which
# is the only place the bridge's state builder looked. The P1.5 fork adds
# `player.resources` (`vendor/STS2_MCP/gits/GitsResources.cs`), a read of
# BaseLib's own custom-resource registry, and Encore is in it by construction.
#
# -1 SURVIVES AS THE ANSWER FOR AN OLD BRIDGE. A run driven against a
# pre-P1.5 bridge has no `resources` key at all, and its logs must keep saying
# "unseen" rather than start saying "0".
METER_UNSEEN = -1
ENCORE_UNSEEN = METER_UNSEEN   # the P1-era name, kept for readers of old logs

# Wire ids of the custom RESOURCES, which are the canonical values -- the badge
# powers below are a display of them. Both are read: the resource when the
# bridge carries it, the badge as the fallback for an older one.
_ENCORE_RESOURCE_ID = "KLEEMOD_ENCORE"
_FANFARE_RESOURCE_ID = "KLEEMOD_FANFARE"

# The live cap is the printed base plus Casting Call's raises, and
# `SalonCapUpPower` is an ordinary PowerModel -- so the raise HAS been on the
# wire all along, in the status strip, next to the meter whose cap it moves.
# The P1 note said the cap "is not on the wire at all"; that was true of the
# CAP and false of its only addend.
_SALON_CAP_UP_ID = "SALON_CAP_UP_POWER"


def _meters(state: dict[str, Any]) -> list[int]:
    """[fanfare, salon, salon_cap, encore] for one turn opening.

    Read by ID rather than by title everywhere: a display name is loc data and
    moves with a wording pass, an id is the thing itself. A number this file
    cannot see is recorded as unseen, not guessed.
    """
    player = state.get("player") or {}
    out = [0, 0, SALON_PRINTED_CAP, METER_UNSEEN]

    for st in (player.get("status") or []):
        if not isinstance(st, dict):
            continue
        wire_id = str(st.get("id") or "").strip().upper()
        try:
            amount = int(st.get("amount"))
        except (TypeError, ValueError):
            continue
        slot = _METER_IDS.get(wire_id)
        if slot is not None:
            out[slot] = amount
        elif wire_id == _SALON_CAP_UP_ID:
            out[2] = SALON_PRINTED_CAP + amount

    # P1.5: the resource map, when the bridge carries one. It is authoritative
    # over the badge for Fanfare -- the badge is synced from the resource at
    # known hook sites, and the resource is the value those sites are syncing.
    resources = player.get("resources")
    if isinstance(resources, dict):
        for key, slot in ((_FANFARE_RESOURCE_ID, 0), (_ENCORE_RESOURCE_ID, 3)):
            if key in resources:
                try:
                    out[slot] = int(resources[key])
                except (TypeError, ValueError):
                    pass
        # A live combat with a resources map but no Encore in it is not an
        # unseen meter -- it is a player who has no Encore. Only the ABSENCE of
        # the map leaves the column unseen.
        if out[3] == METER_UNSEEN and _ENCORE_RESOURCE_ID not in resources:
            out[3] = 0
    return out


# The PRINTED salon cap (SalonConstants.MemberSlots). Not a balance constant
# here -- it is the label on a telemetry column, and the C# side owns the
# number. A run that raises the live cap is legible from its card plays.
SALON_PRINTED_CAP = 3


def _enemy_pool(state: dict[str, Any]) -> int:
    from understudy import adapter
    return sum(max(0, int(e.get("hp", 0))) + max(0, int(e.get("block", 0)))
               for e in adapter.enemy_blobs(state))


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


class RunDriver:
    """One run, start to game_over, with a watchdog on every action."""

    def __init__(self, session: Session, run_index: int, stamp: str,
                 character: str = DEFAULT_CHARACTER,
                 commit: str | None = None,
                 chosen_seed: str | None = None,
                 max_fights: int | None = None):
        self.session = session
        self.run_index = run_index
        self.character = character
        # P1.5 item 1. `None` is the R95 read-back arm -- the game rolls, we
        # record. A string is a CHOSEN seed, and the run verifies the choice
        # took rather than trusting the endpoint's answer.
        self.chosen_seed = chosen_seed
        # P1.5: stop cleanly after N closed fights. `None` is a full run.
        self.max_fights = max_fights
        # R99/4b. `None` is baseline -- the arm the R98 validation ran, and the
        # only arm whose numbers are comparable to R98's.
        self.commit = commit
        self.stamp = stamp
        self.memo = policy_v1.Memo()
        self.seed: str | None = None
        self.log = LOG_DIR / f"soak-{stamp}-run{run_index:03d}.jsonl"
        self.actions = 0
        self.started = time.time()
        self.fights: list[FightTelemetry] = []
        self.fight: FightTelemetry | None = None
        self.defects: list[dict] = []
        self._fingerprints: list[str] = []
        self._last_state: dict[str, Any] | None = None
        self._forced_defaults = 0
        self._last_mech: tuple | None = None
        self._mech_repeats = 0

    # -- logging ----------------------------------------------------------
    def emit(self, record: dict) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        record.setdefault("ts", time.time())
        record.setdefault("run", self.run_index)
        record.setdefault("seed", self.seed)
        with self.log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def file_defect(self, kind: str, detail: str, state: dict) -> dict:
        rec = {
            "record": "defect", "kind": kind, "detail": detail,
            "seed": self.seed, "run": self.run_index,
            "act": (state.get("run") or {}).get("act"),
            "floor": (state.get("run") or {}).get("floor"),
            "state_type": state.get("state_type"),
            "actions_taken": self.actions,
            # Recorded on EVERY defect, not just the process ones: "was the
            # game still running when this was filed" is the first question
            # asked of any row in this table, and reconstructing it afterwards
            # from a killed process is impossible.
            "proc_exit_code": self.session.exit_code,
            "state_dump": _trim_state(state),
            "recent": self._fingerprints[-NO_PROGRESS_ACTIONS:],
        }
        self.defects.append(rec)
        self.emit(rec)
        return rec

    # -- watchdog ---------------------------------------------------------
    def _fingerprint(self, state: dict[str, Any]) -> str:
        from understudy import adapter
        p = state.get("player") or {}
        run = state.get("run") or {}
        b = state.get("battle") or {}
        return "|".join(str(x) for x in (
            state.get("state_type"), state.get("menu_screen"),
            run.get("act"), run.get("floor"), b.get("round"),
            p.get("hp"), p.get("energy"), len(p.get("hand") or []),
            _enemy_pool(state) if state.get("state_type") in COMBAT else "-",
            len(state.get("options") or []),
        ))

    def _check(self, state: dict[str, Any]) -> None:
        if not self.session.alive():
            raise Defect("process_died",
                         "the game process exited while the run was in "
                         "progress; godot.log holds the stack trace", state)
        if state.get("state_type") == "overlay":
            raise Defect("overlay_softlock",
                         "state_type 'overlay' is the bridge's catch-all for a "
                         "screen it cannot drive; no verb is accepted here",
                         state)
        if self.actions >= MAX_ACTIONS_PER_RUN:
            raise Defect("action_ceiling",
                         f"{MAX_ACTIONS_PER_RUN} actions posted without "
                         f"reaching game_over", state)
        if time.time() - self.started > RUN_TIMEOUT_S:
            raise Defect("run_timeout",
                         f"run exceeded {RUN_TIMEOUT_S:.0f}s of wall clock",
                         state)
        fp = self._fingerprint(state)
        self._fingerprints.append(fp)
        recent = self._fingerprints[-NO_PROGRESS_ACTIONS:]
        # A STALL IS A SMALL CYCLE, NOT ONLY A FROZEN FRAME, and the fourth
        # validation soak proved it: the shop arm bought a card-removal service,
        # the remove screen was declined and cancelled, and the run bounced
        # shop -> card_select -> shop forever. Two distinct fingerprints, so a
        # `len(set(...)) == 1` test never fired and the run would have spun to
        # the action ceiling three hours later.
        #
        # The bar is "at most NO_PROGRESS_CYCLE distinct states across a full
        # window". Real play cannot do that: the fingerprint carries floor,
        # round, HP, hand size and the enemy HP pool, and one of those moves on
        # essentially every action that accomplishes anything.
        if (len(recent) == NO_PROGRESS_ACTIONS
                and len(set(recent)) <= NO_PROGRESS_CYCLE):
            distinct = sorted(set(recent))
            raise Defect("no_progress",
                         f"{len(distinct)} distinct state fingerprint(s) across "
                         f"{NO_PROGRESS_ACTIONS} posted actions "
                         f"({'cycle' if len(distinct) > 1 else 'frozen'}): "
                         + " <-> ".join(distinct), state)

    # -- acting -----------------------------------------------------------
    def post(self, state: dict[str, Any], action: dict[str, Any],
             decision: policy_v1.Decision | None = None,
             mechanical: bool = False) -> dict[str, Any]:
        names = naming.describe(state, action)
        before = dict(state)
        result = bridge.post(**action)
        self.actions += 1
        rec = {
            "record": "decision", "i": self.actions,
            "state_type": state.get("state_type"),
            "act": (state.get("run") or {}).get("act"),
            "floor": (state.get("run") or {}).get("floor"),
            "round": (state.get("battle") or {}).get("round"),
            "hp": (state.get("player") or {}).get("hp"),
            "action": action,
            "names": names,                       # revision #7, on every row
            "hand": naming.hand_names(state),
            "mechanical": mechanical,
            "status": result.get("status"),
            "message": result.get("message") or result.get("error"),
        }
        if decision is not None:
            rec["policy"] = decision.as_log()
        self.emit(rec)
        # A PLAY THE GAME REFUSED IS NOT OFFERED AGAIN THIS TURN. Without this
        # the policy re-picks its highest-scoring card, the bridge rejects it
        # for a reason tier0 cannot see, and the run bounces until the
        # watchdog stops it -- which is how an Act 1 boss ended a run at 379
        # actions with "Card 'Stage Presence' cannot be played".
        if (result.get("status") == "error"
                and action.get("action") == "play_card"
                and names.get("card_id")):
            self.memo.rejected.add(
                (self.memo.turn_key(state), str(names["card_id"])))
        time.sleep(SETTLE_S)
        after = bridge.get_state()
        deckwatch.record(after)
        self._observe(before, after, names, action)
        return after

    # -- telemetry --------------------------------------------------------
    def _observe(self, before: dict, after: dict, names: dict,
                 action: dict) -> None:
        st_b, st_a = before.get("state_type"), after.get("state_type")
        pb = before.get("player") or {}
        pa = after.get("player") or {}

        if st_a in COMBAT and (self.fight is None
                               or self.fight.floor != (after.get("run") or {}).get("floor")):
            self._open_fight(after)
        if self.fight is None:
            return

        # END-OF-TURN BLOCK, not turn-opening block. The trajectory samples
        # block at the top of the player's turn, which is whatever SURVIVED the
        # enemy's -- a different quantity wearing the same word, and the wrong
        # one for an output curve.
        if st_b in COMBAT and action.get("action") == "end_turn":
            self.fight.block_at_turn_end.append(
                [(before.get("battle") or {}).get("round"),
                 int((pb or {}).get("block", 0) or 0)])

        if st_b in COMBAT and st_a in COMBAT:
            dealt = _enemy_pool(before) - _enemy_pool(after)
            if dealt > 0 and action.get("action") in ("play_card", "use_potion"):
                src = (names.get("card_name") or names.get("potion_name")
                       or action.get("action"))
                self.fight.damage_by_source[src] = \
                    self.fight.damage_by_source.get(src, 0.0) + dealt
            lost = int(pb.get("hp", 0)) - int(pa.get("hp", 0))
            if lost > 0:
                self.fight.damage_taken += lost
            rb = (before.get("battle") or {}).get("round")
            ra = (after.get("battle") or {}).get("round")
            if ra != rb and ra is not None:
                self._open_turn(after)

        # A PLAY IS RECORDED ON THE STATE IT WAS MADE FROM, never on where the
        # game went next (S7 family A, R101). This block used to live inside
        # the `st_a in COMBAT` arm above, which silently keyed the counter on
        # the AFTER-state: a play that opened a mid-fight overlay or ended the
        # fight was posted, answered `ok`, and then never written down. It cost
        # 707 Ethereal Spotlights -- Furina's starter relic grants one every
        # turn and playing it opens the Center Stage / Guest Cast `card_select`
        # -- plus exactly one play per fight, whichever card landed the killing
        # blow. Damage attribution stays inside the arm above on purpose: a
        # pool drop cannot be read across a screen change, and the enemy pool
        # is the honest damage curve anyway.
        if st_b in COMBAT:
            rnd_b = (before.get("battle") or {}).get("round")
            if action.get("action") == "play_card" and names.get("card_name"):
                self.fight.cards_played.append([rnd_b, names["card_name"]])
            if action.get("action") == "use_potion" and names.get("potion_name"):
                self.fight.potions_used.append([rnd_b, names["potion_name"]])

        # P1.5 item 3: THE SELECTOR CHANNEL, which the fight record was blind
        # to. Furina's Ethereal Spotlight opens a `card_select` every turn and
        # the Center Stage / Guest Cast answer is the whole of that turn's
        # Fanfare posture -- probe B3 (R103(b)) and family B's turn-1 gap both
        # stall on exactly this. It is recorded on the state it was made from,
        # for the same reason `cards_played` is (S7 family A, R101): the screen
        # a selector closes into is not where the choice happened.
        #
        # Recorded whether or not the fight is the reason the screen is up --
        # a selector that opens mid-fight belongs to the fight, and MID_FIGHT
        # is the set that already says so.
        if self.fight is not None and st_b in SELECTOR_SCREENS:
            self.fight.selectors.append(self._selector_row(before, action, names))

        if st_b in COMBAT and st_a not in COMBAT and st_a not in MID_FIGHT:
            self._close_fight(after, "survived")

    def _selector_row(self, before: dict, action: dict, names: dict) -> list:
        """One selector choice, with the list it was chosen from.

        The ROUND comes from the fight's own turn counter rather than from
        `battle.round`: a selector screen is an overlay, and the state the
        bridge builds for it carries no `battle` block at all. `self.fight.turns`
        is the highest round this fight has opened, which is the round the
        overlay is standing on.
        """
        assert self.fight is not None
        blob = before.get(str(before.get("state_type"))) or {}
        offered = blob.get("cards")
        if not isinstance(offered, list):
            offered = blob.get("bundles") if isinstance(blob, dict) else None
        offered_names = [
            (o.get("name") if isinstance(o, dict) else None) or ""
            for o in (offered or [])
        ]
        idx = action.get("index", action.get("card_index"))
        try:
            idx = int(idx)
        except (TypeError, ValueError):
            idx = -1
        # LOWERCASED, and it is not cosmetic. `naming.describe` lowercases the
        # screen type and this fallback reads it raw, so the SAME screen
        # reached by two verbs was writing `NCombatPileCardSelectScreen` on one
        # row and `ncombatpilecardselectscreen` on the next -- two spellings of
        # one screen in a channel whose whole job is to be compared.
        return [
            self.fight.turns,
            str(names.get("screen_type")
                or (blob.get("screen_type") if isinstance(blob, dict) else "")
                or before.get("state_type") or "").lower(),
            idx,
            names.get("card_name") or "",
            offered_names,
        ]

    def _open_fight(self, state: dict) -> None:
        from understudy import adapter
        if self.fight is not None:
            self._close_fight(state, "superseded")
        p = state.get("player") or {}
        run = state.get("run") or {}
        self.fight = FightTelemetry(
            act=int(run.get("act", 0) or 0), floor=int(run.get("floor", 0) or 0),
            kind=str(state.get("state_type")),
            enemies=[{"name": e.get("name"), "max_hp": e.get("max_hp")}
                     for e in adapter.enemy_blobs(state)],
            hp_start=int(p.get("hp", 0)), max_hp=int(p.get("max_hp", 1)),
            intent=self.commit or "")
        self._open_turn(state)

    def _open_turn(self, state: dict) -> None:
        if self.fight is None:
            return
        p = state.get("player") or {}
        rnd = (state.get("battle") or {}).get("round")
        dmg, n = _telegraphed(state)
        self.fight.turns = max(self.fight.turns, int(rnd or 0))
        self.fight.hp_trajectory.append([rnd, p.get("hp"), p.get("block", 0)])
        self.fight.incoming_by_turn.append([rnd, dmg, n])
        # THE POOL IS THE HONEST OUTPUT CURVE. `damage_by_source` credits the
        # play the harness happened to read next and under-counts everything
        # that resolves off a play (salon ticks, auras, bombs); the enemy pool's
        # own drop between two turn openings cannot.
        self.fight.enemy_pool_by_turn.append([rnd, _enemy_pool(state)])
        self.fight.meters_by_turn.append([rnd] + _meters(state))

    def _close_fight(self, state: dict, outcome: str) -> None:
        if self.fight is None:
            return
        p = state.get("player") or {}
        self.fight.hp_end = int(p.get("hp", self.fight.hp_start))
        self.fight.outcome = outcome
        self.fights.append(self.fight)
        self.emit(self.fight.as_record())
        self.fight = None

    # -- the run ----------------------------------------------------------
    def run(self) -> dict:
        self.emit({"record": "run_begin", "character": self.character,
                   "policy": policy_v1.POLICY_VERSION,
                   # The arm, recorded per run for the same reason the dials
                   # are: a log has to stay self-describing when the flag moves.
                   "commit": self.commit,
                   "dials": {"BLOCK_MATTERS_FRACTION":
                             policy_v1.BLOCK_MATTERS_FRACTION,
                             "COMPANION_SHARE_FOR_GUEST_CAST":
                             policy_v1.COMPANION_SHARE_FOR_GUEST_CAST,
                             "TIME_SCALE": TIME_SCALE}})
        outcome, detail = "unknown", ""
        try:
            state = self._to_main_menu()
            state = self._embark(state)
            self.seed = bridge.current_seed()
            self.emit({"record": "seed_read_back", "seed": self.seed,
                       "chosen": self.chosen_seed,
                       "honoured": (None if not self.chosen_seed
                                    else self.seed == self.chosen_seed),
                       "note": ("chosen; P1.5 arm" if self.chosen_seed
                                else "game-generated; R95 read-back arm")})
            # THE READ-BACK IS THE VERIFICATION, and it is a defect rather than
            # a warning. A chosen-seed soak whose runs quietly rolled their own
            # seeds is the exact failure that a build-vs-build comparison
            # cannot survive and cannot detect afterwards -- both builds would
            # simply be measured on different runs. Stopping here is cheap;
            # discovering it in the numbers is not.
            if self.chosen_seed and self.seed != self.chosen_seed:
                raise Defect(
                    "seed_not_honoured",
                    f"asked for seed {self.chosen_seed!r}, the run reads back "
                    f"{self.seed!r}", self._last_state or {})
            outcome, detail = self._drive(state)
        except Defect as d:
            self.file_defect(d.kind, d.detail, d.state)
            outcome, detail = "defect", f"{d.kind}: {d.detail}"
        except bridge.BridgeError as e:
            # THE GRACE PERIOD IS THE WHOLE POINT (see `Session.died`): asked
            # instantly, a game that is crashing right now still reads alive,
            # and the build defect gets filed under a harness-side kind.
            kind = ("process_died" if self.session.died()
                    else "bridge_unreachable")
            detail_ = f"{e} [exit code {self.session.exit_code}]"
            self.file_defect(kind, detail_, self._last_state or {})
            outcome, detail = "defect", f"{kind}: {detail_}"
        except Exception as e:                               # noqa: BLE001
            # The harness itself fell over. That is a defect record like any
            # other -- the alternative is an exception that escapes `soak()`
            # and skips the teardown, which is how a game directory keeps a
            # mod it was promised it would not keep.
            self.file_defect("harness_exception",
                             f"{type(e).__name__}: {e}", self._last_state or {})
            outcome, detail = "defect", f"harness_exception: {e}"
        finally:
            if self.fight is not None:
                self._close_fight(self._last_state or {}, "interrupted")

        summary = {
            "record": "run_end", "outcome": outcome, "detail": detail,
            "seed": self.seed, "run": self.run_index,
            "actions": self.actions,
            "wall_s": round(time.time() - self.started, 1),
            "fights": len(self.fights),
            "final_act": self.fights[-1].act if self.fights else None,
            "final_floor": self.fights[-1].floor if self.fights else None,
            "defects": len(self.defects),
            "forced_defaults": self._forced_defaults,
            "log": str(self.log),
        }
        self.emit(summary)
        return summary

    def _to_main_menu(self) -> dict:
        """Reach the main menu, abandoning any resumable run on the way.

        R97/5b: the profile's leftover run may be abandoned freely. The soak
        does not negotiate with a save -- a resumable run on the profile would
        otherwise make `continue` the first option and quietly resume someone
        else's measurement.
        """
        state = bridge.get_state()
        for _ in range(40):
            self._last_state = state
            st = str(state.get("state_type"))
            if st == "game_over":
                state = self.post(state, {"action": "menu_select",
                                          "option": "main_menu"},
                                  mechanical=True)
                continue
            if st != "menu":
                # Mid-run somewhere. Get to the menu the only way the wire
                # offers: there is none, so this is a stop-and-surface.
                raise Defect("unexpected_start_state",
                             f"expected a menu at run start, found '{st}'",
                             state)
            opts = _option_names(state)
            screen = str(state.get("menu_screen") or "")
            if screen == "main" and "abandon_run" in opts:
                state = self.post(state, {"action": "menu_select",
                                          "option": "abandon_run"},
                                  mechanical=True)
                continue
            if screen == "main":
                return state
            pick = _first_of(opts, ("back", "main_menu", "ignore", "confirm",
                                    "yes", "ok"))
            if pick is None:
                return state
            state = self.post(state, {"action": "menu_select", "option": pick},
                              mechanical=True)
        raise Defect("menu_loop",
                     "could not reach the main menu in 40 menu actions",
                     state)

    def _embark(self, state: dict) -> dict:
        """main -> singleplayer -> standard -> character -> confirm.

        NO `seed` PARAMETER IS PASSED ON THIS PATH, AND THAT IS STILL TRUE ON
        THE CHOSEN-SEED ARM. Upstream's `menu_select(seed=...)` returns "Seeded
        embark is not supported for standard singleplayer from this API",
        behind a `charSelect.Lobby == null` guard that the decompile
        contradicts -- `InitializeSingleplayer` builds a lobby and `SetSeed`
        accepts singleplayer. P1.5 did not rewrite that arm, because a fork
        that rewrites an upstream refusal owns the refusal forever. It fires
        its own endpoint instead, below, between the character pick and the
        confirm.

        So there are two arms here and one embark verb:

          chosen_seed is None  -- R95's read-back arm, byte-for-byte unchanged
          chosen_seed is set   -- P1.5: `POST /api/v1/gits/seed` before the
                                  confirm, verified by the read-back in `run`
        """
        picks = 0
        for _ in range(30):
            self._last_state = state
            st = str(state.get("state_type"))
            if st != "menu":
                return state
            screen = str(state.get("menu_screen") or "")
            opts = _option_names(state)
            if screen == "character_select":
                # ORDER MATTERS AND IT COST A RUN TO LEARN. `KLEEMOD-FURINA`
                # stays in `options` after it has been chosen -- the verb is
                # idempotent and the bridge answers "Selected Furina. Use
                # 'confirm' to embark." every time. A loop that prefers the
                # character over the confirm therefore re-selects her forever
                # and never embarks, which is the `embark_loop` defect the
                # first validation soak filed.
                #
                # So: pick the character exactly once, then take `confirm`.
                # The confirm button only appears in `options` while it is
                # enabled (`_option_names` drops disabled entries), so it is
                # absent until a character is chosen and cannot fire early.
                if picks == 0 and self.character.lower() in [o.lower()
                                                             for o in opts]:
                    picks += 1
                    state = self.post(state,
                                      {"action": "menu_select",
                                       "option": self.character},
                                      mechanical=True)
                    continue
                pick = _first_of(opts, ("confirm", "embark"))
                if pick is not None and self.chosen_seed:
                    # P1.5 item 1, AND THE MOMENT IS THE WHOLE TRICK. The seed
                    # goes on HERE -- character select is up, a character is
                    # chosen, the embark has not fired. Earlier is wasted:
                    # `NCharacterSelectScreen.AfterInitialized()` clears the
                    # debug override as this screen opens. Later does not
                    # exist: the run is generated inside the confirm.
                    #
                    # This is a separate endpoint rather than upstream's
                    # `menu_select(seed=...)` because that arm refuses
                    # singleplayer on a guard the decompile contradicts; see
                    # vendor/STS2_MCP/gits/GitsSeed.cs.
                    self.session.note_seed_channel()
                    # EB-15: WHICH ROUTE FIRED IS NOT ENOUGH TO DIAGNOSE WHY.
                    # Three live runs took `debug_override` and the record
                    # could not say whether the character-select screen was
                    # missed or the lobby on it was null, because `route` was
                    # the only key kept off a report that answers both. The
                    # endpoint's own precondition -- `charSelect != null` and
                    # `charSelect.Lobby != null` (vendor/STS2_MCP/gits/
                    # GitsSeed.cs, GitsSeedApply) -- is read once BEFORE the
                    # POST and once from the POST's own report, so a fourth
                    # observation says which half of the guard failed.
                    try:
                        before = bridge.get_seed()
                    except bridge.BridgeError as exc:
                        before = {"error": str(exc)}
                    report = bridge.set_seed(self.chosen_seed)
                    # THE CANONICAL FORM COMES BACK FROM THE GAME, and it is
                    # taken rather than computed. `SeedHelper.CanonicalizeSeed`
                    # upper-cases, maps 'O'->'0' and 'I'->'1', and the run
                    # reads back the CANONICAL string -- so a harness that
                    # compared the read-back against what a person typed would
                    # file `seed_not_honoured` against a seed the game honoured
                    # exactly. Retyping the mapping here would be a second copy
                    # of somebody else's rule; asking for it is one copy.
                    requested = self.chosen_seed
                    self.chosen_seed = report.get("chosen") or self.chosen_seed
                    self.emit({"record": "seed_chosen",
                               "requested": requested,
                               "seed": self.chosen_seed,
                               "route": report.get("route"),
                               "status": report.get("status"),
                               "message": report.get("message"),
                               # EB-15 diagnosis keys. Adding keys to a log
                               # record is free; these are read, not driven on.
                               "on_char_select": report.get("on_char_select"),
                               "lobby_seed": report.get("lobby_seed"),
                               "debug_override": report.get("debug_override"),
                               "before_on_char_select":
                                   before.get("on_char_select"),
                               "before_lobby_seed": before.get("lobby_seed")})
                if pick is None:
                    if picks < 3 and self.character.lower() in [o.lower()
                                                                for o in opts]:
                        # The selection did not take. Retry a bounded number of
                        # times rather than spinning; three is enough to ride
                        # out a frame the screen was still settling on.
                        picks += 1
                        state = self.post(state,
                                          {"action": "menu_select",
                                           "option": self.character},
                                          mechanical=True)
                        continue
                    raise Defect("no_embark",
                                 f"character select offers no confirm/embark "
                                 f"after {picks} selection(s); options were "
                                 f"{opts}", state)
                self.post(state, {"action": "menu_select", "option": pick},
                          mechanical=True)
                # EMBARKING IS NOT INSTANT, AND THE SECOND VALIDATION SOAK
                # PROVED IT. `confirm` returns "Embarking on run" and the very
                # next GET still reads `character_select`, because the run is
                # generated over several frames. A driver that trusts the
                # post-action read re-selects the character and files
                # `no_embark` on a run that in fact started. So this is the one
                # place with a transition wait rather than a settle.
                state = self._await_leaving_menu()
                continue
            pick = _first_of(opts, ("standard", "singleplayer", "confirm",
                                    "ignore", "ok"))
            if pick is None:
                raise Defect("no_embark_path",
                             f"menu_screen '{screen}' offers none of the "
                             f"embark options; saw {opts}", state)
            state = self.post(state, {"action": "menu_select", "option": pick},
                              mechanical=True)
        raise Defect("embark_loop", "could not embark in 30 menu actions", state)

    def _settle_transient(self, state: dict[str, Any],
                          tries: int = 60,
                          delay: float = 0.5) -> dict[str, Any]:
        """Ride out a state that is a MOMENT, not a screen.

        Two shapes qualify, and they are the same moment wearing two faces:

          `state_type: "unknown"`  -- the bridge documents it as "unrecognized
            room or null state", and the instant after embarking is exactly
            that: act 1, floor 0, the run generated and no room entered yet.
            The third validation soak embarked cleanly and then filed
            `no_action` against it within a second, because the driver treated
            a transition as a screen it could not drive.

          NO `state_type` KEY AT ALL (EB-11 / understudy defect 13) -- the same
            transition read one frame earlier, before `StateBuilder` has a room
            to name. `str(state.get("state_type"))` renders that as the string
            `"None"`, which matched neither the `unknown` test above nor any
            screen below it, so the missing key fell all the way through to
            `policy_v1` declining and `_last_resort` returning None: a run
            ended by `no_action` against a state that was never a screen.
            Riding it out is the same answer the `unknown` face already gets.

        A settle that never lands is NOT swallowed. `unknown` is handed back
        for the no-progress watchdog to catch with a fingerprint history behind
        it, which is a better record than an instant refusal. A missing
        `state_type` cannot be caught that way -- nothing downstream can post an
        action against it, so the watchdog never gets a second sample -- and it
        is therefore filed here, under its own kind, with the settle it was
        given stated. Loud, classified, and not disguised as `no_action`.
        """
        st = state.get("state_type")
        if st is not None and str(st) != "unknown":
            return state
        waited = 0.0
        for _ in range(tries):
            time.sleep(delay)
            waited += delay
            state = bridge.get_state()
            st = state.get("state_type")
            if st is not None and str(st) != "unknown":
                self.emit({"record": "transient_settled",
                           "waited_s": round(waited, 1),
                           "settled_to": str(st)})
                return state
        if state.get("state_type") is None:
            raise Defect(
                "state_type_missing",
                f"the bridge answered with no `state_type` key for "
                f"{waited:.0f}s ({tries} reads); a state with no screen name "
                f"cannot be driven and no action can be posted against it, so "
                f"the no-progress watchdog would never see a second sample",
                state)
        return state

    def _await_leaving_menu(self, tries: int = 60,
                            delay: float = 0.5) -> dict[str, Any]:
        """Poll until the game is off the menu, or give the menu back.

        Deliberately returns the menu state rather than raising when the wait
        runs out: the caller's loop is the retry, and a wait that raises would
        turn a slow machine into a filed defect.
        """
        state = bridge.get_state()
        for _ in range(tries):
            if str(state.get("state_type")) != "menu":
                return state
            time.sleep(delay)
            state = bridge.get_state()
        return state

    def _drive(self, state: dict) -> tuple[str, str]:
        while True:
            state = self._settle_transient(state)
            self._last_state = state
            self._check(state)
            st = str(state.get("state_type"))

            # A BOUNDED RUN, ADDED BY P1.5 FOR ITS OWN ACCEPTANCE. Comparing
            # two recordings of one seed needs a run that ENDS at a stated
            # point in both, and "when the bot happened to die" is not one.
            # This is a clean stop, not a defect: the fight that is open has
            # already closed by the time the count reaches the bound, so the
            # records the comparison reads are complete records.
            #
            # OFF BY DEFAULT (`None`), so a soak is a soak.
            if (self.max_fights is not None
                    and len(self.fights) >= self.max_fights
                    and self.fight is None):
                self.emit({"record": "bounded_stop",
                           "fights": len(self.fights),
                           "max_fights": self.max_fights})
                return "bounded", f"stopped after {len(self.fights)} fight(s)"

            if st == "game_over":
                won = _game_over_won(state)
                self._close_fight(state, "died" if not won else "won")
                self.emit({"record": "game_over", "won": won,
                           "detail": _trim_state(state)})
                return ("won" if won else "died"), json.dumps(
                    state.get("game_over") or state.get("message") or "")[:300]

            mech = _mechanical_action(state)
            if mech is not None:
                # A MECHANICAL ACTION THAT CHANGES NOTHING IS NOT MECHANICAL.
                # With a full potion belt, `claim_reward` on a potion returns
                # ok and does nothing -- the reward stays, the screen stays,
                # and the walker re-claims it forever. Repeating the same
                # forced action on an unchanged screen is the tell, and the
                # escape is the verb every one of these screens advertises.
                fp = self._fingerprint(state)
                if (fp, json.dumps(mech, sort_keys=True)) == self._last_mech:
                    self._mech_repeats += 1
                else:
                    self._last_mech = (fp, json.dumps(mech, sort_keys=True))
                    self._mech_repeats = 0
                if self._mech_repeats >= 3:
                    escape = _escape(state)
                    if escape is not None:
                        self._forced_defaults += 1
                        self.emit({"record": "forced_default",
                                   "state_type": st,
                                   "why": f"{mech} repeated with no state "
                                          f"change; taking the screen's exit",
                                   "action": escape})
                        self._mech_repeats = 0
                        state = self.post(state, escape, mechanical=True)
                        continue
                state = self.post(state, mech, mechanical=True)
                continue

            decision = policy_v1.decide(state, self.memo, commit=self.commit)
            if not decision.available or decision.action is None:
                fallback = _last_resort(state)
                if fallback is None:
                    raise Defect(
                        "no_action",
                        f"policy_v1 has no action for '{st}' and no mechanical "
                        f"fallback exists: {decision.rationale}", state)
                self._forced_defaults += 1
                self.emit({"record": "forced_default", "state_type": st,
                           "why": decision.rationale, "action": fallback})
                state = self.post(state, fallback, decision, mechanical=True)
                continue
            if decision.notes.get("forced_default"):
                self._forced_defaults += 1
            state = self.post(state, decision.action, decision)


def _option_names(state: dict) -> list[str]:
    out = []
    for o in state.get("options") or []:
        if isinstance(o, str):
            out.append(o)
        elif isinstance(o, dict) and o.get("name"):
            if o.get("enabled") is False:
                continue
            out.append(str(o["name"]))
    return out


def _first_of(options: list[str], preferred: tuple[str, ...]) -> str | None:
    low = {o.lower(): o for o in options}
    for p in preferred:
        if p in low:
            return low[p]
    return None


def _game_over_won(state: dict) -> bool:
    blob = state.get("game_over") or {}
    if isinstance(blob, dict):
        for k in ("victory", "won", "is_victory"):
            if k in blob:
                return bool(blob[k])
    return "victor" in json.dumps(blob).lower()


def _mechanical_action(state: dict) -> dict | None:
    """The one forced action on a screen where the game asks nothing.

    Same set the Phase-0 harness's `auto` verb walked, plus the event screens
    policy_v1 still declines (R93 did not add an event arm -- `tier05.events`
    scores by sim event id and the wire carries prose, so an invented answer
    would be noise wearing a policy's clothes).
    """
    st = str(state.get("state_type"))
    if st == "event":
        ev = state.get("event") or {}
        if ev.get("in_dialogue"):
            return {"action": "advance_dialogue"}
        opts = [o for o in (ev.get("options") or []) if not o.get("is_locked")]
        if opts:
            # Deterministic and declared: the FIRST unlocked option, always.
            # Not a policy -- a coin that always lands the same way, so an
            # event's contribution to a soak is at least constant across runs.
            return {"action": "choose_event_option",
                    "index": opts[0].get("index", 0)}
        return {"action": "advance_dialogue"}
    if st == "rewards":
        blob = state.get("rewards")
        items = blob.get("items") if isinstance(blob, dict) else (blob or [])
        return ({"action": "claim_reward", "index": 0} if items
                else {"action": "proceed"})
    if st == "treasure":
        relics = state.get("relics") or state.get("options") or []
        return ({"action": "claim_treasure_relic", "index": 0} if relics
                else {"action": "proceed"})
    if st == "relic_select":
        relics = state.get("relics") or state.get("options") or []
        return ({"action": "select_relic", "index": 0} if relics
                else {"action": "skip_relic_selection"})
    if st == "bundle_select":
        # SELECTING A BUNDLE OPENS A PREVIEW; IT DOES NOT TAKE THE BUNDLE, and
        # the second `select_bundle` is refused in as many words ("A bundle
        # preview is already open - confirm or cancel it first"). Without the
        # confirm the walker re-picks index 0 forever, which is how Neow's
        # Scroll Boxes ended a run at sixteen actions. Same shape as the
        # Enchant screen (defect 6) and the removal grid (defect 4): a screen
        # whose select is a preview, not a choice.
        blob = state.get("bundle_select") or {}
        if blob.get("preview_showing"):
            return {"action": "confirm_bundle_selection"}
        return {"action": "select_bundle", "index": 0}
    if st == "hand_select":
        blob = state.get("hand_select") or {}
        if blob.get("can_confirm"):
            return {"action": "combat_confirm_selection"}
        cards = blob.get("cards") or (state.get("player") or {}).get("hand") or []
        return ({"action": "combat_select_card", "card_index": 0} if cards
                else {"action": "combat_confirm_selection"})
    if st == "crystal_sphere":
        return {"action": "crystal_sphere_proceed"}
    if st in DECISION_SCREENS:
        return None
    if st == "menu":
        opts = _option_names(state)
        pick = _first_of(opts, ("ignore", "ok", "confirm", "back"))
        return {"action": "menu_select", "option": pick} if pick else None
    return None


def _escape(state: dict) -> dict | None:
    """The verb that leaves a screen a forced action could not finish.

    Every one of these screens advertises a way out; the walker just never had
    a reason to use it until a full potion belt made `claim_reward` a no-op.
    """
    return {
        "rewards": {"action": "proceed"},
        "treasure": {"action": "proceed"},
        "relic_select": {"action": "skip_relic_selection"},
        "hand_select": {"action": "combat_confirm_selection"},
        "crystal_sphere": {"action": "crystal_sphere_proceed"},
    }.get(str(state.get("state_type")))


def _last_resort(state: dict) -> dict | None:
    """When policy_v1 declines and the screen is a real one, keep moving.

    Every use is counted and logged as `forced_default`, because a run that
    proceeds by shrugging is a run whose telemetry is worth less and the report
    has to be able to say so.
    """
    st = str(state.get("state_type"))
    if st == "card_select":
        # A SCREEN THAT CANNOT BE CANCELLED MUST BE ANSWERED. The in-combat
        # "Choose a card." overlay reports `can_cancel: false` and
        # `can_skip: false`, and the bridge rejects the cancel with "No skip
        # option available - a card must be chosen" -- so cancelling as a last
        # resort is a guaranteed loop, which is exactly what it produced.
        blob = state.get("card_select") or {}
        if blob.get("can_cancel") or blob.get("can_skip"):
            return {"action": "cancel_selection"}
        if blob.get("can_confirm"):
            return {"action": "confirm_selection"}
        return {"action": "select_card", "index": 0}
    if st == "rest_site":
        # EB-13, AND THE SAME LESSON AS `card_select` ABOVE: a screen that
        # refuses the exit must be answered, not exited. A rest site reports
        # `can_proceed: false` until its one option has been spent, and the
        # bridge says so in as many words ("No proceed button available or
        # enabled"). `proceed` used to be the unconditional answer here, so a
        # rest site whose options the policy could not match spent every
        # remaining action of the run posting a verb the screen had already
        # refused -- the `no_progress` defect filed against seed `43MLG7MG9L`.
        #
        # The answer is the screen's own: take the first ENABLED option, in
        # offered order. Deterministic and declared -- not a policy, the same
        # always-heads coin `_mechanical_action` spends on events, and counted
        # as a `forced_default` so the telemetry says the choice was not the
        # sim's.
        blob = state.get("rest_site") or {}
        options = ((blob.get("options") if isinstance(blob, dict) else None)
                   or state.get("options") or [])
        for i, opt in enumerate(options):
            if not isinstance(opt, dict) or opt.get("is_enabled") is not False:
                return {"action": "choose_rest_option", "index": i}
        return {"action": "proceed"}
    return {
        "card_reward": {"action": "skip_card_reward"},
        "shop": {"action": "proceed"},
        "fake_merchant": {"action": "proceed"},
        "monster": {"action": "end_turn"},
        "elite": {"action": "end_turn"},
        "boss": {"action": "end_turn"},
    }.get(st)


def _trim_state(state: dict) -> dict:
    """A state dump small enough to sit in a defect record and complete enough
    to diagnose from. The piles go; everything a screen turns on stays."""
    out = {k: v for k, v in state.items()
           if k not in ("player", "map", "compendium")}
    p = dict(state.get("player") or {})
    for pile in ("draw_pile", "discard_pile", "exhaust_pile", "deck"):
        if pile in p:
            p[pile] = f"<{len(p[pile])} cards>"
    out["player"] = p
    m = state.get("map") or {}
    if m:
        out["map"] = {k: m.get(k) for k in ("next_options", "boss")}
    return out


# ----------------------------------------------------------------- main ----

def soak(runs: int, character: str, do_setup: bool,
         commit: str | None = None,
         seeds: list[str] | None = None,
         max_fights: int | None = None) -> dict:
    from understudy import committed as _committed
    commit = _committed.normalise(commit)          # refuses an unknown word
    stamp = time.strftime("%Y%m%d-%H%M%S")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    session = Session(stamp, do_setup=do_setup, intent=commit)
    summaries: list[dict] = []
    index = LOG_DIR / f"soak-{stamp}-index.json"
    shapes: dict[str, int] = {}
    stopped = None
    try:
        session.setup()
        for i in range(1, runs + 1):
            print(f"--- run {i}/{runs} ---", flush=True)
            deckwatch.reset()
            # P1.5: run i takes seed i, cycling if fewer seeds than runs were
            # named. `None` throughout is the read-back arm, unchanged.
            chosen = seeds[(i - 1) % len(seeds)] if seeds else None
            driver = RunDriver(session, i, stamp, character, commit=commit,
                               chosen_seed=chosen, max_fights=max_fights)
            s = driver.run()
            s["defect_kinds"] = [d["kind"] for d in driver.defects]
            summaries.append(s)
            print(f"    {s['outcome']}  seed={s['seed']}  "
                  f"actions={s['actions']}  fights={s['fights']}  "
                  f"defects={s['defects']}", flush=True)
            index.write_text(json.dumps(
                {"stamp": stamp, "character": character,
                 "policy": policy_v1.POLICY_VERSION, "commit": commit,
                 "seeds": seeds,
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

    result = {"stamp": stamp, "character": character,
              "policy": policy_v1.POLICY_VERSION, "commit": commit,
              "seeds": seeds,
              "requested_runs": runs, "runs": summaries,
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
_HARNESS_SIDE = {"no_embark_path", "no_embark", "embark_loop", "menu_loop",
                 "unexpected_start_state", "bridge_unreachable", "no_action",
                 "seed_not_honoured", "state_type_missing"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--character", default=DEFAULT_CHARACTER)
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
    args = ap.parse_args(argv)

    result = soak(args.runs, args.character, do_setup=not args.no_setup,
                  commit=args.commit, seeds=args.seed,
                  max_fights=args.max_fights)
    if args.report:
        from understudy import report
        print()
        print(report.render(result["stamp"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
