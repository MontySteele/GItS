"""Setup, teardown, and the reversibility ledger between them.

Cut out of `soak.py` by `EB-180`: `Reversibility` and `Session` are the two
classes that file declared, moved whole, and it re-exports both -- so
`soak.Session(...)` still resolves and a
`monkeypatch.setattr(soak, "Session", ...)` still swaps what `soak.soak`
constructs.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from understudy import instances, keepawake
from understudy.soak_lane import bridge_installed, game_is_running
from understudy.soak_shape import (DEPLOY_BRIDGE, GAME_EXE, MENU_TIMEOUT_S,
                                   PROCESS_EXIT_GRACE_S, REPO, SPEED_SIDECAR,
                                   STEAM_APPID, TIME_SCALE)


def _soak():
    """`understudy.soak` itself, imported at CALL time.

    The wire and the dials this seam reads are declared on `soak.py`, which
    is also where a caller (and the harness's own tests) reaches in to swap
    them -- `monkeypatch.setattr(soak, "bridge", fake)`. Binding them at
    import would take a private copy here and the swap would never be seen.
    """
    from understudy import soak
    return soak


def _wire():
    """`soak.bridge`, read at CALL time. Same reason as `_soak`."""
    from understudy import soak
    return soak.bridge


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

# -------------------------------------------------------------- session ----

class Session:
    """Setup, teardown, and the reversibility ledger between them."""

    # CLASS ATTRIBUTES so every construction path has them, including the
    # test doubles built with `Session.__new__` that never run `__init__`.
    # The OFF state is the default: no instance means lane 0's defaults, and
    # a session that launched nothing has no pid.
    instance: Any = None
    install_bridge: bool = True
    proc: Any = None
    # EB-231. The `pid` property reads the launch entry when there is no
    # `Popen`, so a double built with `Session.__new__` needs the attribute to
    # exist and to mean "this session launched nothing".
    _launch_entry: Any = None
    # EB-226. A double built with `Session.__new__` never runs `setup`, so it
    # holds no power request and its `teardown` must not release one.
    _power_counted: bool = False
    _power_held: bool = False

    def __init__(self, stamp: str, do_setup: bool = True,
                 intent: str | None = None,
                 instance: "instances.Instance | None" = None,
                 install_bridge: bool = True):
        self.stamp = stamp
        self.do_setup = do_setup
        # Passed to the launched game so the mod's own hook labels its
        # records with the same declaration the bot feed is stamping.
        self.intent = intent
        # WHICH GAME THIS SESSION IS, and `None` MEANS "WHATEVER THIS THREAD
        # IS ALREADY ON" -- not "lane 0".
        #
        # That distinction is the whole of a defect the first live two-lane
        # stage found. `staged_turn.stage_board` opens its own attach Session
        # with no instance, on the lane worker's thread; a `None` that meant
        # lane 0 made that Session's `wire()` REBIND the thread to port 15526,
        # so lane 1's board was staged into lane 0's game. Both boards came
        # back refused by `exact_hand` -- each holding the other's cards --
        # which is the good failure: the packet was not written.
        #
        # With `None` meaning "inherit", an attach Session on a bound thread
        # stays on that lane, and a Session on an unbound thread behaves
        # exactly as every Session did before lanes existed.
        self.instance = instance
        # TWO LANES SHARE ONE INSTALL, SO ONLY ONE OF THEM MAY DEPLOY.
        # `deploy_bridge.ps1` deletes and rewrites `mods\STS2_MCP` and refuses
        # while a file it is about to rewrite is HELD -- so lane 1, which
        # launches while lane 0's game is already up, must not run it. The
        # teardown half of this flag is gone: no lane's teardown removes the
        # shared directory any more, whether it deployed or not (`EB-310`).
        self.install_bridge = install_bridge
        self.dir = (self.instance.game_dir if self.instance is not None
                    else _soak().game_dir())
        self.ledger = Reversibility(
            _soak().LOG_DIR / f"reversibility-{stamp}.json")
        self.proc: subprocess.Popen | None = None
        self._appid_entry: dict | None = None
        # NO `_bridge_entry`. The bridge row is reverted the moment it is
        # written (`_deploy_bridge`), so there is never anything for a teardown
        # to hold on to -- and an attribute that existed would be an invitation
        # to wire the removal back up. `EB-310`.
        self._speed_entry: dict | None = None
        self._seed_entry: dict | None = None
        self._launch_entry: dict | None = None
        self.speed_before: dict | None = None

    # -- setup ------------------------------------------------------------
    @property
    def label(self) -> str:
        """This session's lane label, or the thread's if it inherited one."""
        if self.instance is not None:
            return self.instance.label
        return _wire().current_label()

    def wire(self) -> None:
        """Bind the CALLING THREAD's bridge calls to this session's game.

        Called at the top of every method that touches the wire, because a
        two-lane round calls those methods from two threads and `bridge`'s
        current-instance is thread-local.
        """
        if self.instance is not None:
            _wire().use(self.instance)

    def setup(self) -> None:
        self.wire()
        # EB-226, AND BEFORE THE `do_setup` BRANCH. From here to `teardown`
        # this process is driving a game, whether it launched it or attached
        # to one, and an idle sleep in that window is a hole in a run rather
        # than a rest -- 2026-08-29 lost 4 h 16 m of a live funnel to exactly
        # that. Refcounted process-wide, so a two-lane round's second session
        # does not take a second hold and the first teardown does not drop
        # the one they share. See `understudy/keepawake.py` for why the flag
        # cannot simply be set on this thread.
        self._power_counted = True
        self._power_held = keepawake.acquire(f"session {self.stamp}")
        if not self.do_setup:
            self._require_bridge()
            return
        # A LANE WITH ITS OWN user:// TREE INHERITS ONE FILE AND NO MORE. The
        # mod profile lives in `settings.save`; without it the lane boots
        # vanilla and the whole round would read a game with no klee mod in it.
        if self.instance is not None:
            for path in instances.seed_profile(self.instance):
                print(f"lane {self.instance.label}: seeded {path}")
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
        """Put the SHARED bridge in front of the launch, and never claim it.

        THE BRIDGE IS INFRASTRUCTURE, NOT THIS RUN'S PROPERTY. Every lane's
        game reads it, and so does the game the owner starts from Steam --
        `deploy_proto.ps1` installs it as its last step precisely so that the
        owner's next launch carries it. So every branch below records the row
        `pre_existing` and reverts it as *shared, left in place*: the ledger
        says what happened, and nothing on it asks a teardown to undo it.
        `EB-310` is the bill for the other rule -- see the lanes block above.
        """
        if not self.install_bridge:
            # Nothing recorded, so nothing is claimed: this lane did not touch
            # the shared mods directory at all.
            print(f"lane {self.label}: bridge deploy skipped "
                  f"(another lane owns the shared mods directory)")
            return
        installed = bridge_installed(self.dir)
        # A GAME UP ON AN EXISTING INSTALL IS THE ONE BRANCH THAT WRITES
        # NOTHING TO DISK. It is what lets a lane start beside a game that has
        # the bridge LOADED (and therefore locked): the deploy would be
        # refused, and it does not need to happen.
        pids = _soak().game_is_running() if installed else ""
        entry = self.ledger.record(
            "Deployed `mods\\STS2_MCP\\` from vendor pin 55e0648",
            "`.\\build\\deploy_bridge.ps1 -Remove`, BY HAND -- no teardown in "
            "this harness removes the shared bridge (`EB-310`)",
            pre_existing=True)
        if pids:
            self.ledger.revert(
                entry, f"shared, left in place: a game was already running "
                       f"(PID {pids}) on this install")
            print(f"lane {self.label}: bridge already installed and a game is "
                  f"up (PID {pids}); reusing it rather than rewriting a dll "
                  f"that game may hold")
            return
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-File", str(DEPLOY_BRIDGE)],
            cwd=str(REPO / "klee-mod"), capture_output=True, text=True)
        if r.returncode != 0:
            self.ledger.fail(
                entry, "deploy failed; the shared install was left as it was "
                       "found")
            raise SystemExit(f"bridge deploy failed:\n{r.stdout}\n{r.stderr}")
        note = ("refreshed from the vendor pin with no game holding the dll"
                if installed else
                "installed here, and left for the owner's next launch and for "
                "every other lane")
        self.ledger.revert(entry, f"shared, left in place: {note}")

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
        # THE LANE'S OWN ENVIRONMENT IS THE BASE. `Instance.env` assigns
        # `APPDATA` (a separate user:// tree: saves, settings, shader cache,
        # mod_configs, logs) and `STS2_MCP_PORT` (which listener this process
        # binds). On lane 0 the APPDATA half is a no-op by construction, so the
        # single-instance path launches exactly the process it always did.
        env = (self.instance.env() if self.instance is not None
               else dict(os.environ))
        env["GITS_TELEMETRY_FEED"] = "bot"
        # THE INTENT LABEL IS PINNED THE SAME WAY, AND THE EMPTY STRING IS
        # LOAD-BEARING. `env` starts as a copy of this shell's environment, so
        # assigning unconditionally is what strips an operator's inherited
        # GITS_TELEMETRY_INTENT. It must be ASSIGNED-EMPTY rather than DELETED:
        # the mod consults the human's persistent
        # `gits_telemetry/intent.txt` only when the variable is ABSENT
        # (PlayTelemetry.Intent()), so deleting it would hand a bot soak
        # whatever archetype a person last declared for their own session.
        # Do not "simplify" this to a conditional set.
        env["GITS_TELEMETRY_INTENT"] = self.intent or ""
        self.proc = subprocess.Popen([str(exe)], cwd=str(self.dir),
                                     env=env,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        # EB-231: THE PID GOES ON THE LEDGER, immediately. `--teardown` rebuilds
        # this session from the ledger file and holds no `Popen`, so without
        # the number written down there is nothing for it to kill and nothing
        # for it to verify -- which is exactly how a REVERTED marker came to
        # be written over a running game.
        self._launch_entry["pid"] = self.proc.pid
        self.ledger.flush()

    def wait_for_menu(self, timeout: float = MENU_TIMEOUT_S) -> dict:
        """R97/5a. Poll for the `options` key on a menu state -- never `GET /`.

        The HTTP server answers ~20 s before the main menu has buttons. This is
        the difference between "the process is up" and "the game is ready", and
        it is the single cheapest bug in this file to have written correctly.
        """
        self.wire()
        deadline = time.time() + timeout
        last = "(no response)"
        while time.time() < deadline:
            if self.proc is not None and self.proc.poll() is not None:
                raise SystemExit(
                    f"the game process exited during boot "
                    f"(code {self.proc.returncode}) -- check godot.log")
            try:
                state = _wire().get_state()
            except _wire().BridgeError as e:
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
        self.wire()
        try:
            _wire().get_state()
        except _wire().BridgeError as e:
            raise SystemExit(f"--no-setup given but no bridge is answering: {e}")

    def _speed_on(self) -> None:
        # THE FIRST CAPTURE OF THE SESSION IS THE SESSION'S ORIGINAL, and a
        # relaunch does not get to overwrite it. `PrefsSave.FastMode` persists
        # to `prefs.save` (NOT `settings.save`, which backs `SettingsSave` and
        # never carries FastMode), so IF anything flushed prefs while the
        # harness held Instant, a second process would capture a value the
        # harness itself put there rather than the user's. The ledger is what
        # a person reads to put their game back; it may not launder a change
        # into a baseline.
        #
        # `GitsSpeed.cs` now persists its own capture across processes (EB-87),
        # so the endpoint would answer correctly on its own. This stays as the
        # belt to that brace: it costs one field and it is what keeps the
        # ledger honest if a sidecar is ever lost with the mod directory.
        self.wire()
        if self.speed_before is None:
            try:
                self.speed_before = _wire().get_speed()
            except _wire().BridgeError:
                self.speed_before = None
        self._speed_entry = self.ledger.record(
            f"Set FastMode=Instant and TimeScale={TIME_SCALE} via "
            f"`POST /api/v1/gits/speed` (captured: "
            f"{json.dumps(self.speed_before)})",
            '`POST {"enabled": false}` restores the captured originals')
        _wire().set_speed(True, TIME_SCALE)

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
        self.wire()
        self._step(self._seed_entry, self._release_seed)
        self._step(self._speed_entry, self._restore_speed)
        # THE SIDECAR IS READ HERE BECAUSE NOTHING DELETES IT ANY MORE. It
        # lives inside `mods/STS2_MCP`, which this teardown no longer removes
        # (`EB-310`), so `GitsSpeed.cs` will restore from it in the next
        # process (EB-87). It is read only to SAY SO: its presence proves the
        # in-process restore above never landed, and the ledger's NOT REVERTED
        # row does not carry the captured value a person would need to set
        # FastMode back by hand. Gated on the speed ENTRY, like every step
        # around it -- a session that never set the speed has nothing to say
        # about a sidecar it did not write.
        if self._speed_entry:
            outstanding = self._read_speed_sidecar()
            if outstanding:
                print(f"WARNING: the in-process FastMode restore never ran, "
                      f"so `{SPEED_SIDECAR}` is still in the game directory. "
                      f"The next launch restores from it; the captured "
                      f"original was {outstanding}.")
        self._step(self._launch_entry, self._stop_game)
        # NO BRIDGE STEP, AND ITS ABSENCE IS THE RULE (`EB-310`): the shared
        # `mods\STS2_MCP` is what the owner's own Steam launch reads, so this
        # harness never takes it out. `deploy_bridge.ps1 -Remove` is the only
        # remover, by hand.
        self._step(self._appid_entry, self._remove_appid)
        # EB-226, LAST and outside the ledger: the power request is not a
        # change to the game directory, it is a change to this machine, and
        # it is given back only once every step that still needs the machine
        # awake has run. Guarded by the flag so a `teardown` without a
        # matching `setup` -- a test double, a half-built session -- cannot
        # decrement a count it never incremented.
        if getattr(self, "_power_counted", False):
            self._power_counted = False
            keepawake.release()

    def _step(self, entry: dict | None, undo) -> None:
        if not entry:
            return
        try:
            self.ledger.revert(entry, undo())
        except Exception as e:                               # noqa: BLE001
            self.ledger.fail(entry, f"{type(e).__name__}: {e}")

    def _release_seed(self) -> str:
        after = _wire().clear_seed()
        return (f"chosen seed released (debug_override="
                f"{after.get('debug_override')!r})")

    def _restore_speed(self) -> str:
        after = _wire().set_speed(False)
        return (f"restored to {after.get('fast_mode')} / "
                f"{after.get('time_scale')}")

    def _stop_game(self) -> str:
        """EB-231: kill, then PROVE the pid is gone, and only then report it.

        The return value of this function becomes a REVERTED marker, so it may
        say nothing it has not checked. A pid that outlives the wait RAISES:
        `_step` writes NOT REVERTED with the image name still holding the
        number, the later steps still run, and the person reading the ledger
        is told the game is up rather than told it is closed.
        """
        return "process terminated -- " + self._kill_and_prove()

    def _kill_and_prove(self) -> str:
        """Kill by pid and return the words that PROVE it, or raise.

        Shared by the ordinary teardown step and the hang watchdog's, because
        both write a REVERTED marker and a marker is a claim.
        """
        pid = self.pid
        self._kill()
        if pid is None:
            # Nothing was ever launched under this entry -- but the entry
            # exists, so something launched a game and did not write down
            # which. That is not a kill and must not be marked as one.
            raise RuntimeError(
                "the launch entry carries no pid, so this teardown cannot "
                "prove any process is gone; find the game's pid, close it, "
                "and re-run `deploy_bridge.ps1 -Remove` by hand")
        # The constant is read HERE rather than taken as a default, so a test
        # (and an operator with a reason) can move the wait without editing a
        # signature.
        alive = _soak().wait_for_exit(pid, _soak().PID_EXIT_TIMEOUT_S,
                              _soak().PID_EXIT_POLL_S)
        if alive is not None:
            raise RuntimeError(
                f"pid {pid} ({alive}) is STILL ALIVE after "
                f"{_soak().PID_EXIT_TIMEOUT_S:.0f}s -- NOT marking this "
                f"reverted. "
                f"The next deploy would fight a running game; close it "
                f"(`taskkill /F /T /PID {pid}`) and run this teardown again")
        return f"pid {pid} verified gone"

    def _read_speed_sidecar(self) -> str | None:
        """The FastMode `GitsSpeed` still says is outstanding, or None."""
        p = self.dir / SPEED_SIDECAR
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8")).get(
                "original_fast_mode")
        except Exception:                                    # noqa: BLE001
            return "unreadable sidecar"

    def _remove_appid(self) -> str:
        p = self.dir / "steam_appid.txt"
        if p.exists():
            p.unlink()
        return "file removed"

    def _kill(self) -> None:
        """Terminate THIS SESSION's process, by pid, and nothing else.

        THE `taskkill /IM` BELT IS GONE, AND ITS REMOVAL IS PART OF THE
        TWO-LANE BUILD. It killed every `SlayTheSpire2.exe` on the machine by
        image NAME; with two lanes running that is one lane tearing down the
        other's game mid-board -- a silent corruption of somebody else's round
        rather than a crash anyone would notice.

        What the belt was FOR is still real: a game left over from an earlier
        crashed soak holds the mod dll and makes the next `deploy_bridge` run
        fail. That is now the deploy script's own refusal, which lists the
        pids, and closing a process this session did not start is the
        operator's call rather than ours.
        """
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            for _ in range(20):
                if self.proc.poll() is not None:
                    break
                time.sleep(0.5)
            if self.proc.poll() is None:
                self.proc.kill()
            # By PID, and with /T for the tree: `Popen.kill` does not promise
            # a child process goes with it.
            subprocess.run(["taskkill", "/F", "/T", "/PID",
                            str(self.proc.pid)],
                           capture_output=True, text=True)
        elif self.proc is None and self.pid is not None:
            # EB-231: the `--teardown` path. There is no `Popen` here -- this
            # session was rebuilt from the ledger on disk -- so the ONLY
            # handle on the game is the pid the launch entry recorded. Still
            # by pid and still with /T; the `taskkill /IM` belt stays gone,
            # for the reason above.
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.pid)],
                           capture_output=True, text=True)

    @property
    def pid(self) -> int | None:
        """This session's game pid, or None when it launched nothing.

        THE LEDGER IS THE FALLBACK, not an alternative source of truth: a live
        session answers from its own `Popen`, and a session rebuilt from disk
        (`embark --teardown`) answers from the number `_launch` wrote onto the
        launch entry. Same pid either way -- one of the two is just the only
        copy that outlives the process that made it (EB-231).
        """
        if self.proc is not None:
            return self.proc.pid
        recorded = (self._launch_entry or {}).get("pid")
        return int(recorded) if isinstance(recorded, int) else None

    def halt_spin(self, why: str) -> dict:
        """Stop a spinning game NOW, and leave the ledger telling the truth.

        THE KILL IS THE TEARDOWN STEP THAT CANNOT WAIT. EB-1's loop writes
        ~1.3 MB/s to `godot.log` for as long as the process lives; the ordinary
        path (finish the run, fall out of `soak()`, walk the ledger) would let
        it write for the rest of the night. So the process is terminated here,
        through the ledger, the moment the watchdog is sure -- and the entry it
        closes is the one that was opened when the game was launched, so the
        row reads `REVERTED` with this reason rather than sitting at `APPLIED`
        over a process that no longer exists.

        THE SPEED ROW IS FAILED, NOT REVERTED, AND THAT IS THE POINT. The wire
        is dead, so `POST {"enabled": false}` cannot run, and the live
        `PrefsSave.FastMode` really is left changed for as long as the process
        lives (it persists to `prefs.save` only if something flushes prefs,
        which a hard kill does not). A ledger that quietly marked it reverted because the process
        it belonged to is gone would be lying in the one direction that costs
        somebody an evening wondering why their game animates strangely. The
        captured original travels in the failure note so it can be put back by
        hand.

        `--no-setup` KILLS NOTHING. That mode promised the game directory it
        would change nothing and it did not launch the process; terminating a
        game somebody else started is not ours to do. It reports instead.
        """
        note = {"killed": False, "why": why}
        if not self.do_setup or self.proc is None:
            note["why"] = (f"{why} -- NOT terminated: --no-setup did not launch "
                           f"this game and may not kill it. The log flood "
                           f"continues until someone closes it by hand.")
            return note

        if self._speed_entry is not None:
            self.ledger.fail(
                self._speed_entry,
                "the wire was dead, so the speed endpoint could not be asked "
                "to restore; the live FastMode is left changed (it reaches "
                "prefs.save only if something flushes prefs). Captured "
                f"original: {json.dumps(self.speed_before)}")
            self._speed_entry = None

        def _terminate() -> str:
            # EB-231: the watchdog's marker is a marker too. A pid that
            # outlives the kill raises here and the row reads NOT REVERTED,
            # which is what a spinning game that would not die looks like.
            return (f"terminated by the hang watchdog: {why} -- "
                    + self._kill_and_prove())

        if self._launch_entry is not None:
            self._step(self._launch_entry, _terminate)
            self._launch_entry = None
        else:
            self._kill()
        note["killed"] = True
        return note

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
                "superseded by a restart; a new launch row and speed row open "
                "below, and the SESSION's captured original is carried "
                "forward rather than re-captured -- PrefsSave.FastMode "
                "persists to prefs.save, so if anything flushed prefs while "
                "Instant was live the second process must not "
                "read the first process's setting back as the original "
                "(EB-87: the bridge persists its capture in a sidecar, and "
                "this session keeps its own copy as well)")
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
