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
reverse. Appendix A of `docs/understudy-phase0-report.md` is the format this
inherits and the checklist it is measured against.
"""

from __future__ import annotations

import argparse
import json
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
# Hard ceiling per run. A three-act run is a few thousand actions; ten thousand
# is a spin.
MAX_ACTIONS_PER_RUN = 10000
# Wall-clock ceiling per run, so an overnight soak cannot be eaten by one run.
RUN_TIMEOUT_S = 3600.0
# TimeScale for the speed endpoint. Animation pacing only -- GitsSpeed.cs
# touches no rules code. 3.0 is what Phase 0 ran at without incident.
TIME_SCALE = 3.0


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

    def __init__(self, stamp: str, do_setup: bool = True):
        self.stamp = stamp
        self.do_setup = do_setup
        self.dir = game_dir()
        self.ledger = Reversibility(LOG_DIR / f"reversibility-{stamp}.json")
        self.proc: subprocess.Popen | None = None
        self._appid_entry: dict | None = None
        self._bridge_entry: dict | None = None
        self._speed_entry: dict | None = None
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
        self.proc = subprocess.Popen([str(exe)], cwd=str(self.dir),
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

    # -- teardown ---------------------------------------------------------
    def teardown(self) -> None:
        if self._speed_entry:
            try:
                after = bridge.set_speed(False)
                self.ledger.revert(self._speed_entry,
                                   f"restored to {after.get('fast_mode')} / "
                                   f"{after.get('time_scale')}")
            except bridge.BridgeError as e:
                self.ledger.fail(self._speed_entry, f"speed restore failed: {e}")
        if self._launch_entry:
            self._kill()
            self.ledger.revert(self._launch_entry, "process terminated")
        if self._bridge_entry:
            r = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive",
                 "-ExecutionPolicy", "Bypass", "-File", str(DEPLOY_BRIDGE),
                 "-Remove"],
                cwd=str(REPO / "klee-mod"), capture_output=True, text=True)
            if r.returncode == 0:
                self.ledger.revert(self._bridge_entry, "mods/STS2_MCP removed")
            else:
                self.ledger.fail(self._bridge_entry, r.stderr.strip()[:300])
        if self._appid_entry:
            p = self.dir / "steam_appid.txt"
            try:
                if p.exists():
                    p.unlink()
                self.ledger.revert(self._appid_entry, "file removed")
            except OSError as e:
                self.ledger.fail(self._appid_entry, str(e))

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

    def alive(self) -> bool:
        if self.proc is None:
            return True                      # --no-setup: not ours to judge
        return self.proc.poll() is None


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
    enemies: list = field(default_factory=list)
    hp_start: int = 0
    max_hp: int = 0
    turns: int = 0
    hp_trajectory: list = field(default_factory=list)     # [(round, hp, block)]
    incoming_by_turn: list = field(default_factory=list)  # [(round, dmg, n_atk)]
    cards_played: list = field(default_factory=list)      # [(round, name)]
    potions_used: list = field(default_factory=list)
    damage_by_source: dict = field(default_factory=dict)
    damage_taken: int = 0
    hp_end: int = 0
    outcome: str = "unknown"

    def as_record(self) -> dict:
        return {
            "record": "fight", "act": self.act, "floor": self.floor,
            "kind": self.kind, "enemies": self.enemies,
            "hp_start": self.hp_start, "hp_end": self.hp_end,
            "max_hp": self.max_hp, "hp_lost": self.hp_start - self.hp_end,
            "turns": self.turns, "outcome": self.outcome,
            "hp_trajectory": self.hp_trajectory,
            "incoming_by_turn": self.incoming_by_turn,
            "cards_played": self.cards_played,
            "n_cards_played": len(self.cards_played),
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


def _enemy_pool(state: dict[str, Any]) -> int:
    from understudy import adapter
    return sum(max(0, int(e.get("hp", 0))) + max(0, int(e.get("block", 0)))
               for e in adapter.enemy_blobs(state))


# --------------------------------------------------------------- driver ----

COMBAT = ("monster", "elite", "boss")
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
                 character: str = DEFAULT_CHARACTER):
        self.session = session
        self.run_index = run_index
        self.character = character
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
        if len(recent) == NO_PROGRESS_ACTIONS and len(set(recent)) == 1:
            raise Defect("no_progress",
                         f"the state fingerprint has been identical across "
                         f"{NO_PROGRESS_ACTIONS} posted actions: {fp}", state)

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
            if action.get("action") == "play_card" and names.get("card_name"):
                self.fight.cards_played.append([rb, names["card_name"]])
            if action.get("action") == "use_potion" and names.get("potion_name"):
                self.fight.potions_used.append([rb, names["potion_name"]])

        if st_b in COMBAT and st_a not in COMBAT:
            self._close_fight(after, "survived")

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
            hp_start=int(p.get("hp", 0)), max_hp=int(p.get("max_hp", 1)))
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
                       "note": "game-generated; R95 read-back arm"})
            outcome, detail = self._drive(state)
        except Defect as d:
            self.file_defect(d.kind, d.detail, d.state)
            outcome, detail = "defect", f"{d.kind}: {d.detail}"
        except bridge.BridgeError as e:
            self.file_defect("bridge_unreachable", str(e),
                             self._last_state or {})
            outcome, detail = "defect", f"bridge_unreachable: {e}"
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

        No `seed` parameter anywhere: R95's read-back arm. Passing a seed on
        this path returns "Seeded embark is not supported for standard
        singleplayer from this API", and the Custom screen that WOULD take one
        is unmodelled by the bridge and soft-locks -- which is exactly why the
        Custom arm is P1.5 and not here.
        """
        for _ in range(30):
            self._last_state = state
            st = str(state.get("state_type"))
            if st != "menu":
                return state
            screen = str(state.get("menu_screen") or "")
            opts = _option_names(state)
            if screen == "character_select":
                if self.character.lower() in [o.lower() for o in opts]:
                    state = self.post(state,
                                      {"action": "menu_select",
                                       "option": self.character},
                                      mechanical=True)
                    continue
                pick = _first_of(opts, ("confirm", "embark"))
                if pick is None:
                    raise Defect("no_embark",
                                 f"character select offers no confirm/embark; "
                                 f"options were {opts}", state)
                state = self.post(state,
                                  {"action": "menu_select", "option": pick},
                                  mechanical=True)
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

    def _drive(self, state: dict) -> tuple[str, str]:
        while True:
            self._last_state = state
            self._check(state)
            st = str(state.get("state_type"))

            if st == "game_over":
                won = _game_over_won(state)
                self._close_fight(state, "died" if not won else "won")
                self.emit({"record": "game_over", "won": won,
                           "detail": _trim_state(state)})
                return ("won" if won else "died"), json.dumps(
                    state.get("game_over") or state.get("message") or "")[:300]

            mech = _mechanical_action(state)
            if mech is not None:
                state = self.post(state, mech, mechanical=True)
                continue

            decision = policy_v1.decide(state, self.memo)
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


def _last_resort(state: dict) -> dict | None:
    """When policy_v1 declines and the screen is a real one, keep moving.

    Every use is counted and logged as `forced_default`, because a run that
    proceeds by shrugging is a run whose telemetry is worth less and the report
    has to be able to say so.
    """
    st = str(state.get("state_type"))
    return {
        "card_reward": {"action": "skip_card_reward"},
        "rest_site": {"action": "proceed"},
        "shop": {"action": "proceed"},
        "fake_merchant": {"action": "proceed"},
        "card_select": {"action": "cancel_selection"},
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

def soak(runs: int, character: str, do_setup: bool) -> dict:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    session = Session(stamp, do_setup=do_setup)
    summaries: list[dict] = []
    index = LOG_DIR / f"soak-{stamp}-index.json"
    shapes: dict[str, int] = {}
    stopped = None
    try:
        session.setup()
        for i in range(1, runs + 1):
            print(f"--- run {i}/{runs} ---", flush=True)
            deckwatch.reset()
            driver = RunDriver(session, i, stamp, character)
            s = driver.run()
            s["defect_kinds"] = [d["kind"] for d in driver.defects]
            summaries.append(s)
            print(f"    {s['outcome']}  seed={s['seed']}  "
                  f"actions={s['actions']}  fights={s['fights']}  "
                  f"defects={s['defects']}", flush=True)
            index.write_text(json.dumps(
                {"stamp": stamp, "character": character,
                 "policy": policy_v1.POLICY_VERSION,
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
            if not session.alive() and do_setup:
                print("    game process is gone; relaunching", flush=True)
                session._launch()
                session.wait_for_menu()
                session._speed_on()
    finally:
        session.teardown()

    result = {"stamp": stamp, "character": character,
              "policy": policy_v1.POLICY_VERSION,
              "requested_runs": runs, "runs": summaries,
              "stopped_on": stopped,
              "reversibility": session.ledger.entries}
    index.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print()
    print("REVERSIBILITY LOG (game dir)")
    print(session.ledger.table())
    return result


# Defect kinds that indicate the HARNESS is broken rather than the build.
# A game crash or a soft-lock is the soak working; these are the soak failing.
_HARNESS_SIDE = {"no_embark_path", "no_embark", "embark_loop", "menu_loop",
                 "unexpected_start_state", "bridge_unreachable", "no_action"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--character", default=DEFAULT_CHARACTER)
    ap.add_argument("--no-setup", action="store_true",
                    help="attach to an already-running game; make no game-dir "
                         "changes and revert none")
    ap.add_argument("--report", action="store_true",
                    help="print the morning report for this soak when it ends")
    args = ap.parse_args(argv)

    result = soak(args.runs, args.character, do_setup=not args.no_setup)
    if args.report:
        from understudy import report
        print()
        print(report.render(result["stamp"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
