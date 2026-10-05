"""One game process, its port, and its user:// tree -- as one handle.

TWO GAMES AT ONCE, FROM ONE INSTALL. A live experiment (2026-08-29, evidence
`review/qa/two-instance/`) proved the platform half: two `SlayTheSpire2.exe`
processes run side by side out of the SAME Steam install -- Steam initialises
twice on one account with no restart-if-necessary -- and setting `APPDATA` per
process gives each a fully separate user tree: saves, settings, shader cache,
`mod_configs`, logs. Cost is roughly 1.3 GiB of VRAM and 1 GB of RAM per extra
instance.

WHAT THAT EXPERIMENT DID NOT PROVE WAS THE BRIDGE PORT, and it is the one
thing a shared install cannot give you: `STS2_MCP.conf` sits beside the mod
dll INSIDE the game directory, so two processes read one conf and want one
port. The fix is on the mod side -- `vendor/STS2_MCP/gits/GitsPort.cs` reads
`STS2_MCP_PORT` from the environment FIRST, then the conf, then 15526 -- and
this module is the half that sets it.

LANE 1'S PROFILE IS DISPOSABLE, and that is a standing rule rather than an
accident. It is seeded from lane 0's `settings.save` on first use (without it
the mod profile does not load and the game boots vanilla), and nothing else in
it is ever read back: no run of record is ever played on lane 1's saves. If it
goes wrong, delete the directory.

HOW A COMMAND CHOOSES ONE. `--lane N` on `embark`, `soak` and `scenario run`
(`cli_lane` below turns the flag into an instance, and lane 0 into `None`,
which is the no-lane behaviour every run had before this existed); and
`GITS_LANE=1` for the three `blindplay` commands, which are design-blind and
may not import this module at all -- `bridge` reads the variable for them
(`env_label`, `wire_lane`).

Nothing here imports `soak` or `bridge` at module scope; `soak` imports
`bridge`, `bridge` imports this, and the game directory is resolved lazily.
"""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PORT = 15526

#: The environment variable `gits/GitsPort.cs` reads. Pinned here and in the
#: C# by the same name; `test_local_tester` asserts the two agree.
PORT_ENV = "STS2_MCP_PORT"

#: The environment variable that names a lane to the commands which take no
#: `--lane` flag -- `blindplay observe` / `act` / `session`. Those three are
#: design-blind and may not import this module or `soak` at all
#: (`test_understudy_blindplay` pins that line), so the lane reaches them the
#: one way it can: through `bridge`, which reads this. `embark --lane` prints
#: the export line so the operator never has to remember the spelling.
LANE_ENV = "GITS_LANE"

#: The lane everything ran on before lanes existed, and still the default.
DEFAULT_LABEL = "lane0"

#: THE STANDING RULE, IN THE RECORD RATHER THAN IN A COMMENT. Every artefact
#: an above-zero lane writes carries this sentence, the way a dev card grant
#: carries `bridge.GRANT_GUARDRAIL`: a caveat nothing on disk states is a
#: caveat the reader six months from now does not have.
LANE_GUARDRAIL = (
    "lane 1 runs on a DISPOSABLE profile seeded from lane 0's settings: no "
    "run played on it is a run of record, and nothing in its user tree is "
    "ever read back")

#: Where a lane that is not lane 0 keeps its user:// tree. Local, not roaming:
#: it is scratch, it is per-machine, and it must never sync anywhere.
LANE_ROOT = Path(os.environ.get("LOCALAPPDATA")
                 or Path.home() / "AppData" / "Local") / "gits-lanes"

#: `%APPDATA%\SlayTheSpire2\...` -- the game's own user tree, relative to
#: whatever APPDATA the process was launched with.
GAME_APPDATA_DIR = "SlayTheSpire2"
LOG_RELATIVE = (GAME_APPDATA_DIR, "logs", "godot.log")

#: WHAT A FRESH LANE INHERITS, AND WHAT IT MUST NOT. Both halves were learned
#: live rather than reasoned out:
#:
#:  * `settings.save` — without it the game boots with NO MOD PROFILE and the
#:    klee mod is not loaded, so the lane's first launch is a vanilla game
#:    wearing the harness's name.
#:  * `profile.save`, `prefs.save`, `progress.save` — without these the lane
#:    is a FIRST-EVER launch, and the game opens on the tutorial prompt. The
#:    driver's embark stops there and files `no_embark_path: menu_screen
#:    'tutorial_prompt' offers none of the embark options; saw ['no', 'yes']`,
#:    which is a correct refusal about a screen the funnel has no verb for.
#:
#: `current_run.save` is DELIBERATELY ABSENT from this list: copying it would
#: resume lane 0's run inside lane 1, which is the one way a disposable
#: profile could reach back into a real one. Nothing here is ever read as
#: data — a lane's profile is scratch (see this module's header).
SETTINGS_RELATIVE = (GAME_APPDATA_DIR, "steam")
SETTINGS_NAME = "settings.save"
SEED_FILES = ("settings.save", "profile.save", "prefs.save", "progress.save")

#: `EB-763`. WHERE THE RUN-HISTORY STORE LIVES, relative to
#: `SETTINGS_RELATIVE`, as a glob rather than a path. The Steam id and the
#: profile number are both the machine's business and neither is knowable
#: here, and `modded/` and the vanilla tree each have their own store -- the
#: cost the game pays at boot is all of them, so the glob takes all of them.
#: Today's machine: `76561197999302235/modded/profile1/saves/history`, 899
#: files, and `76561197999302235/profile1/saves/history`, 330.
HISTORY_GLOB = "**/saves/history"


def run_history_store(appdata: Path | None = None) -> tuple[int, int]:
    """`EB-763`. How many files the profile's run-history store holds, and how
    many bytes, for the APPDATA tree a lane is about to launch under.

    Returns `(files, bytes)` and `(0, 0)` for a tree that has none -- a fresh
    lane, or a machine where the glob finds nothing. `appdata` is `None` for
    lane 0, which runs on the process's own `%APPDATA%`; that is the same
    fallback `Instance.log_path` makes, and for the same reason.

    READ-ONLY, ABSOLUTELY. The caller is a watchdog deciding how long to wait,
    not a cleaner: nothing in this function or its callers deletes, moves,
    prunes or rewrites anything under the profile. The store is the owner's
    play history (`docs/current/operations/understudy-seats.md`, the boot-tax
    paragraph).

    Errors are swallowed to `(0, 0)` rather than raised. This is called on the
    launch path of every session, and a permission error or a file that
    vanished between the walk and the `stat` must degrade to "the base wait",
    never take a round down before it has started.
    """
    root = Path(appdata if appdata is not None
                else os.environ.get("APPDATA", "")).joinpath(
        *SETTINGS_RELATIVE)
    files = 0
    total = 0
    try:
        if not root.is_dir():
            return 0, 0
        for store in root.glob(HISTORY_GLOB):
            if not store.is_dir():
                continue
            for p in store.rglob("*"):
                try:
                    if p.is_file():
                        files += 1
                        total += p.stat().st_size
                except OSError:
                    continue
    except OSError:
        return files, total
    return files, total


@dataclass(frozen=True)
class Instance:
    """One game process's identity: where it runs, and how to reach it.

    `game_dir` is `None` on a WIRE-ONLY handle (`wire_lane` below), which is
    the shape a client that only ever talks to a port needs -- and it is
    `None` rather than a guessed path on purpose: a lane with no game
    directory must fail loudly the moment somebody tries to launch out of it,
    not launch out of the wrong one.
    """

    game_dir: Path | None
    port: int
    appdata: Path | None
    label: str

    @property
    def base(self) -> str:
        """The bridge's base URL for this instance."""
        return f"http://localhost:{self.port}"

    @property
    def is_default(self) -> bool:
        """Lane 0: the machine's own APPDATA and the default port.

        Everything the funnel did before lanes existed runs on this, with no
        flag and no environment change -- which is the compatibility claim
        this whole build rests on.
        """
        return self.appdata is None and self.port == DEFAULT_PORT

    def env(self, base_env: dict[str, str] | None = None) -> dict[str, str]:
        """The launch environment for this instance.

        `APPDATA` is assigned only for a lane that HAS one, so lane 0 keeps
        whatever the operator's shell had -- deleting or rewriting it would
        change where the ordinary, single-instance funnel puts its saves.
        `STS2_MCP_PORT` is assigned ALWAYS, including on lane 0 and including
        with the default value: an operator who exported a stray port in their
        own shell must not be able to move the bridge out from under a lane
        that thinks it knows where it is.
        """
        env = dict(os.environ if base_env is None else base_env)
        if self.appdata is not None:
            env["APPDATA"] = str(self.appdata)
        env[PORT_ENV] = str(self.port)
        return env

    def log_path(self) -> Path:
        """This instance's `godot.log`. Per-lane, because APPDATA is."""
        root = self.appdata if self.appdata is not None else Path(
            os.environ.get("APPDATA", ""))
        return Path(root).joinpath(*LOG_RELATIVE)

    def as_row(self) -> dict[str, str]:
        """What a record row carries so two lanes' rows can be told apart."""
        return {"instance": self.label, "port": str(self.port),
                "appdata": str(self.appdata) if self.appdata else "default"}


# ------------------------------------------------------------- registry ----

#: How many disposable seat lanes exist above lane 0. THE ONE NUMBER: the
#: registry below is derived from it, and so is every port, user tree and
#: refusal message that names the lanes. Raised 4 -> 5 on 2026-10-05.
SEAT_LANE_COUNT = 5


def port_for(label: str) -> int:
    """`laneN` -> `DEFAULT_PORT + N`. The rule the registry is built on, and
    the one `tools/agent_worktree.py` reads ports by (it may not import this
    package)."""
    return DEFAULT_PORT + int(str(label)[len("lane"):])


#: label -> (port, appdata or None). Lane 0 is today's defaults, exactly;
#: lane N above it is port `DEFAULT_PORT + N` and `LANE_ROOT / laneN`.
LANES: dict[str, tuple[int, Path | None]] = {
    "lane0": (DEFAULT_PORT, None),
    **{f"lane{n}": (DEFAULT_PORT + n, LANE_ROOT / f"lane{n}")
       for n in range(1, SEAT_LANE_COUNT + 1)},
}


def lane_labels() -> list[str]:
    """Every lane label in NUMBER order (`lane10` after `lane9`, never after
    `lane1`, which a plain `sorted` would do)."""
    return sorted(LANES, key=lambda label: int(label[len("lane"):]))


def seat_lane_labels() -> list[str]:
    """The disposable lanes a seat may run on: every lane but lane 0."""
    return [label for label in lane_labels() if label != DEFAULT_LABEL]


def default_game_dir() -> Path:
    """`GameDir` from `klee-mod/local.props`, via soak's one reader.

    Imported here rather than at module scope: `soak` imports `bridge` and
    `bridge` imports this file, so a top-level import would be a cycle.
    """
    from understudy import soak
    return soak.game_dir()


def lane(label: str = "lane0", *, game_dir: Path | None = None) -> Instance:
    """The instance for a lane label. Built lazily -- see `default_game_dir`."""
    if label not in LANES:
        raise KeyError(f"unknown lane {label!r}; known lanes: "
                       f"{', '.join(lane_labels())}")
    port, appdata = LANES[label]
    return Instance(game_dir=game_dir if game_dir is not None
                    else default_game_dir(),
                    port=port, appdata=appdata, label=label)


def lanes(count: int, *, game_dir: Path | None = None) -> list[Instance]:
    """The first `count` lanes, in registry order. `count=1` is lane 0 alone."""
    labels = lane_labels()
    if count < 1 or count > len(labels):
        raise ValueError(f"lanes must be 1..{len(labels)}, not {count}")
    return [lane(labels[i], game_dir=game_dir) for i in range(count)]


# ------------------------------------------------- naming one lane --------

def label_for(value: object) -> str:
    """`1`, `"1"`, `"lane1"` -> `"lane1"`. Anything else is a `ValueError`.

    ONE SPELLING FOR EVERY DOOR. `--lane 1`, `GITS_LANE=1` and `GITS_LANE=lane1`
    are the same request, and a typo is refused HERE, naming the lanes that
    exist -- rather than reaching a port nobody is listening on and being
    reported as an unreachable bridge, which is a true sentence about the
    wrong problem.
    """
    raw = str(value).strip()
    label = raw if raw.startswith("lane") else f"lane{raw}"
    if label not in LANES:
        raise ValueError(
            f"{value!r} is not a lane; known lanes: "
            f"{', '.join(lane_labels())} (or the bare number)")
    return label


def env_label(env: dict[str, str] | None = None) -> str:
    """The lane `GITS_LANE` names, or `lane0` when it is unset or empty.

    An empty string is lane 0 and not an error: `GITS_LANE=` is how a shell
    unsets it in a script, and refusing that would make the variable harder
    to turn off than to turn on.
    """
    raw = str((os.environ if env is None else env).get(LANE_ENV, "")).strip()
    return DEFAULT_LABEL if not raw else label_for(raw)


def wire_lane(label: str = DEFAULT_LABEL) -> Instance:
    """A handle for the CLIENT half of a lane: its port, its tree, its label.

    NO GAME DIRECTORY, and that is the whole reason this is not `lane()`.
    `lane()` resolves `GameDir` out of `klee-mod/local.props` and `SystemExit`s
    when there is none -- correct for anything that will LAUNCH a game, and
    wrong for `bridge`, which is imported by every test on a machine that has
    no game installed and only ever needs to know which port to talk to and
    which user tree that port's game writes into.
    """
    if label not in LANES:
        raise ValueError(f"unknown lane {label!r}; known lanes: "
                         f"{', '.join(lane_labels())}")
    port, appdata = LANES[label]
    return Instance(game_dir=None, port=port, appdata=appdata, label=label)


def cli_lane(value: object, *, game_dir: Path | None = None) -> Instance | None:
    """The instance a `--lane N` flag names, and **`None` for lane 0**.

    `None` RATHER THAN lane 0's own `Instance`, and the difference is not
    cosmetic. A `Session` with an instance binds its thread, stamps the lane
    into `soak-<stamp>-lane0-run001.jsonl`, and writes an `appdata` into its
    record rows; a `Session` with `None` does exactly what every run before
    lanes existed did. Lane 0 has to be the second of those, or "the default
    is unchanged" is a claim no file on disk agrees with.
    """
    return (None if label_for(value) == DEFAULT_LABEL
            else lane(label_for(value), game_dir=game_dir))


# ---------------------------------------------------------- seeding -------

def seed_profile(inst: Instance,
                 source_appdata: Path | None = None) -> list[Path]:
    """Copy the `SEED_FILES` out of lane 0's tree into this lane's, once.

    Returns the files it wrote (empty on a lane that already has them, and on
    lane 0, which has nothing to seed). Every file keeps its path RELATIVE to
    `SlayTheSpire2/steam/`, because that path is how the game finds it — the
    same name means different things under `steam/<id>/` and under
    `steam/<id>/modded/profile1/saves/`.

    AN EXISTING FILE IS NEVER OVERWRITTEN. A lane that has been used has its
    own settings and its own progress, and those are what its next launch
    should read; re-seeding would silently roll it back to lane 0's.
    """
    if inst.appdata is None:
        return []
    src_root = Path(source_appdata if source_appdata is not None
                    else os.environ.get("APPDATA", "")).joinpath(
        *SETTINGS_RELATIVE)
    written: list[Path] = []
    if not src_root.is_dir():
        return written
    for src in sorted(p for p in src_root.rglob("*")
                      if p.is_file() and p.name in SEED_FILES):
        dest = inst.appdata.joinpath(*SETTINGS_RELATIVE,
                                     *src.relative_to(src_root).parts)
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        written.append(dest)
    return written


# ------------------------------------------------ pending epochs ----------

#: The epoch states that park the main menu. The bridge reports these as
#: `manual_epoch_reveal_required` (`McpMod.StateBuilder.cs`, the main-menu
#: block reads `EpochState.Obtained` and `ObtainedNoSlot`), and with one of
#: them pending the menu offers only Settings and Quit, so `embark` has no
#: path. The save spells them in snake case.
PENDING_EPOCH_STATES = frozenset({"obtained", "obtained_no_slot"})
REVEALED_EPOCH_STATE = "revealed"
PROGRESS_NAME = "progress.save"


def _is_real_profile(appdata: Path) -> bool:
    """True when `appdata` is, or sits inside, the process's own `%APPDATA%`.

    The owner's profile lives there. A lane's tree never does; this is the
    second lock on the door after `appdata is None`.
    """
    real = os.environ.get("APPDATA")
    if not real:
        return False
    try:
        mine = Path(appdata).resolve()
        theirs = Path(real).resolve()
    except OSError:
        return True
    return mine == theirs or theirs in mine.parents


def reveal_pending_epochs(inst: Instance) -> list[tuple[Path, list[str]]]:
    """Mark every obtained-but-unrevealed epoch in a LANE's `progress.save`
    as revealed, so the lane's main menu offers Singleplayer again.

    WHY. A base-game run that unlocks a timeline epoch leaves the menu with
    only Settings and Quit until someone clicks the reveal, and the bridge
    refuses to click it from automation (`McpMod.Actions.cs`, "not forcing
    timeline reveal"). Lanes are disposable, so the lane's own save is edited
    to the state the one click would leave. Re-seeding from lane 0 is not the
    fix: lane 0's `progress.save` can be parked on the same reveal
    (`teyvat-proofs-7`), and then a fresh lane inherits the blocker.

    LANES ONLY. Lane 0 (`appdata is None`) and any tree inside the process's
    own `%APPDATA%` are refused and return `[]`: the owner's profile is never
    written. Only the `state` field of pending epochs changes; the rest of the
    file is written back byte for byte (same key order, indent and line
    endings). A file that does not parse is left alone.

    Returns `(path, [epoch ids revealed])` for each file it changed.
    """
    if inst.appdata is None or _is_real_profile(inst.appdata):
        return []
    root = Path(inst.appdata).joinpath(*SETTINGS_RELATIVE)
    if not root.is_dir():
        return []
    changed: list[tuple[Path, list[str]]] = []
    for path in sorted(root.rglob(PROGRESS_NAME)):
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
            data = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        epochs = data.get("epochs") if isinstance(data, dict) else None
        if not isinstance(epochs, list):
            continue
        revealed = []
        for epoch in epochs:
            if (isinstance(epoch, dict)
                    and str(epoch.get("state", "")).lower()
                    in PENDING_EPOCH_STATES):
                epoch["state"] = REVEALED_EPOCH_STATE
                revealed.append(str(epoch.get("id", "?")))
        if not revealed:
            continue
        text = json.dumps(data, indent=2, ensure_ascii=False)
        if b"\r\n" in raw:
            text = text.replace("\n", "\r\n")
        tmp = path.with_name(path.name + ".gits-tmp")
        tmp.write_bytes(text.encode("utf-8"))
        os.replace(tmp, path)
        changed.append((path, revealed))
    return changed


#: The game's own `unlock all` (`UnlockConsoleCmd.UnlockEpochs` and
#: `UnlockAscensions`) sets these. 10 is the game's top ascension.
UNLOCKED_ASCENSION = 10


def unlock_lane_progress(inst: Instance) -> list[tuple[Path, list[str]]]:
    """Reveal every epoch and open every ascension in a LANE's saves.

    WHY (2026-10-05). The modded profile the lanes seed from had 22 character
    epochs never obtained (Ironclad 3-7, Defect 2-7, Necrobinder 3-7, Regent
    2-7), and those epochs unlock cards and relics (`Ironclad3Epoch`: Red
    Skull, Paper Phrog, Ruined Helmet; `Defect2Epoch`: Loop, Null, Consuming
    Shadow). Every base-character seat played with cut-down pools, and only A0
    could be chosen for most of them. This writes what the game's own
    dev-console `unlock all` writes for epochs and ascensions: each epoch
    `revealed`, each character's `max_ascension` and the multiplayer one 10.

    LANES ONLY, on the same two locks as `reveal_pending_epochs`; the owner's
    profile is never written. Idempotent. Returns `(path, [what changed])`.
    """
    if inst.appdata is None or _is_real_profile(inst.appdata):
        return []
    root = Path(inst.appdata).joinpath(*SETTINGS_RELATIVE)
    if not root.is_dir():
        return []
    changed: list[tuple[Path, list[str]]] = []
    now = int(time.time())
    for path in sorted(root.rglob(PROGRESS_NAME)):
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
            data = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        what: list[str] = []
        for epoch in data.get("epochs") or []:
            if (isinstance(epoch, dict)
                    and str(epoch.get("state", "")).lower()
                    != REVEALED_EPOCH_STATE):
                epoch["state"] = REVEALED_EPOCH_STATE
                if not epoch.get("obtain_date"):
                    epoch["obtain_date"] = now
                what.append(str(epoch.get("id", "?")))
        for stats in data.get("character_stats") or []:
            if (isinstance(stats, dict)
                    and int(stats.get("max_ascension") or 0)
                    < UNLOCKED_ASCENSION):
                stats["max_ascension"] = UNLOCKED_ASCENSION
                what.append(f"{stats.get('id', '?')} ascension")
        if (int(data.get("max_multiplayer_ascension") or 0)
                < UNLOCKED_ASCENSION):
            data["max_multiplayer_ascension"] = UNLOCKED_ASCENSION
            what.append("multiplayer ascension")
        if not what:
            continue
        text = json.dumps(data, indent=2, ensure_ascii=False)
        if b"\r\n" in raw:
            text = text.replace("\n", "\r\n")
        tmp = path.with_name(path.name + ".gits-tmp")
        tmp.write_bytes(text.encode("utf-8"))
        os.replace(tmp, path)
        changed.append((path, what))
    return changed


# ------------------------------------------ the shared install's lock -----
#
# CONCURRENT EMBARKS, AND WHAT THEY SHARE (2026-10-05). Each lane's user tree,
# port, budget file and run log are its own, and so is each game's
# `NGame.DebugSeedOverride` -- it is global to a PROCESS, and every lane is
# its own process. What is NOT a lane's own is the game DIRECTORY: one
# `steam_appid.txt`, one `mods\STS2_MCP` and one `mods\klee` for every lane.
#
# THE DEFECT (BACKLOG, the 2026-09-25 round: "two lanes embarked at the same
# moment: the second lane's game never came up, its port refused every
# call"). `Session._deploy_bridge` asks "is a game up?" and, with none up,
# runs `deploy_bridge.ps1`, which builds for tens of seconds and then
# `Remove-Item`s `mods\STS2_MCP` and copies it back. Two embarks started
# together both see no game, both deploy, and one's `Remove-Item` lands while
# the other's freshly launched game is booting -- before it has loaded (and
# so locked) the dll. That game boots with no bridge mod at all, and its port
# refuses every call until a teardown and a relaunch. The same window lets
# two embarks both find `steam_appid.txt` absent, both record it as their
# own creation, and the first teardown delete it from under the rest.
#
# THE FIX IS A SHORT CRITICAL SECTION, MACHINE-WIDE. Every write to the game
# directory and every LAUNCH out of it runs inside `install_lock()`: an
# OS-level lock on one file under `LOCK_ROOT`, so it spans processes,
# checkouts and worktrees (they all share one install), and the OS drops it
# when its holder dies -- there is no stale lock to clean up. Inside it,
# a second lane's `_deploy_bridge` sees the first lane's game ALREADY
# RUNNING and reuses the bridge rather than rewriting it, which is the rule
# that was always meant to fire. The wait for the menu is OUTSIDE the lock,
# so N lanes boot in parallel; only the seconds around each launch are
# serialised.
#
# AND THE LAUNCHES ARE STAGGERED. Every launch initialises Steam and asks it
# for the profile's remote store; `EB-766` found that a launch landing on
# Steam while it is still busy with another session is what stalls a boot.
# `LAUNCH_STAGGER_S` is the minimum gap between any two launches on this
# machine, recorded in `LAST_LAUNCH_NAME` beside the lock, so a lone embark
# never waits and the fifth of five waits four gaps.

#: Where the lock and the last-launch record live. Machine-wide on purpose
#: (beside the lanes' own trees), never in a checkout. Swappable for tests.
LOCK_ROOT = LANE_ROOT
INSTALL_LOCK_NAME = "install.lock"
LAST_LAUNCH_NAME = "last-launch.json"

#: How long an embark waits for another to finish with the install. A first
#: lane's bridge deploy builds the bridge (`dotnet build`) inside it.
INSTALL_LOCK_TIMEOUT_S = 900.0
INSTALL_LOCK_POLL_S = 0.25

#: The minimum gap between two game launches on this machine (seconds).
LAUNCH_STAGGER_S = 8.0


class InstallLockTimeout(RuntimeError):
    """Another embark held the shared install for longer than the timeout."""


_lock_guard = threading.RLock()
_lock_depth = 0
_lock_handle = None


def _try_os_lock(fh) -> bool:
    """One non-blocking attempt at an exclusive OS lock on byte 0 of `fh`."""
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _os_unlock(fh) -> None:
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


@contextmanager
def install_lock(timeout_s: float | None = None, *, why: str = ""):
    """Hold the machine-wide lock on the shared game install.

    REENTRANT within a process (a `setup` that holds it calls `_launch`,
    which takes it too) and SERIALISING across threads (a two-lane round in
    one process takes it one lane at a time), and exclusive across processes
    through the OS lock. Raises `InstallLockTimeout` after `timeout_s`.
    """
    global _lock_depth, _lock_handle
    limit = INSTALL_LOCK_TIMEOUT_S if timeout_s is None else float(timeout_s)
    deadline = time.monotonic() + limit
    if not _lock_guard.acquire(timeout=max(0.0, limit)):
        raise InstallLockTimeout(
            f"another thread held the shared game install for {limit:.0f}s")
    try:
        if _lock_depth == 0:
            root = Path(LOCK_ROOT)
            root.mkdir(parents=True, exist_ok=True)
            fh = os.fdopen(os.open(root / INSTALL_LOCK_NAME,
                                   os.O_RDWR | os.O_CREAT), "r+b")
            waited = False
            while not _try_os_lock(fh):
                if time.monotonic() >= deadline:
                    fh.close()
                    raise InstallLockTimeout(
                        f"another embark held the shared game install "
                        f"({root / INSTALL_LOCK_NAME}) for {limit:.0f}s"
                        + (f" while {why}" if why else ""))
                if not waited:
                    waited = True
                    print(f"waiting for the shared game install "
                          f"(another embark holds it){': ' + why if why else ''}")
                time.sleep(INSTALL_LOCK_POLL_S)
            _lock_handle = fh
        _lock_depth += 1
        try:
            yield
        finally:
            _lock_depth -= 1
            if _lock_depth == 0 and _lock_handle is not None:
                _os_unlock(_lock_handle)
                _lock_handle.close()
                _lock_handle = None
    finally:
        _lock_guard.release()


def last_launch_at() -> float | None:
    """When any lane on this machine last launched a game (epoch seconds)."""
    try:
        blob = json.loads((Path(LOCK_ROOT) / LAST_LAUNCH_NAME).read_text(
            encoding="utf-8"))
        return float(blob["at"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def await_launch_stagger(now=time.time, sleep=time.sleep) -> float:
    """Sleep out the rest of `LAUNCH_STAGGER_S` since the last launch on this
    machine. Returns the seconds slept. Call it holding `install_lock`."""
    last = last_launch_at()
    if last is None:
        return 0.0
    owed = LAUNCH_STAGGER_S - (now() - last)
    if owed <= 0 or owed > LAUNCH_STAGGER_S:      # a clock that went back
        return 0.0
    sleep(owed)
    return owed


def note_launch(label: str, pid: int | None, now=time.time) -> None:
    """Record a launch for the next one's stagger. Never raises."""
    try:
        root = Path(LOCK_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        (root / LAST_LAUNCH_NAME).write_text(
            json.dumps({"at": now(), "lane": label, "pid": pid}),
            encoding="utf-8")
    except OSError:
        pass
