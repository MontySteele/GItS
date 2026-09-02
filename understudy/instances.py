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

import os
import shutil
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

#: label -> (port, appdata or None). Lane 0 is today's defaults, exactly.
LANES: dict[str, tuple[int, Path | None]] = {
    "lane0": (DEFAULT_PORT, None),
    "lane1": (DEFAULT_PORT + 1, LANE_ROOT / "lane1"),
    "lane2": (DEFAULT_PORT + 2, LANE_ROOT / "lane2"),
}


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
                       f"{', '.join(sorted(LANES))}")
    port, appdata = LANES[label]
    return Instance(game_dir=game_dir if game_dir is not None
                    else default_game_dir(),
                    port=port, appdata=appdata, label=label)


def lanes(count: int, *, game_dir: Path | None = None) -> list[Instance]:
    """The first `count` lanes, in registry order. `count=1` is lane 0 alone."""
    labels = sorted(LANES)
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
            f"{', '.join(sorted(LANES))} (or the bare number, 0 / 1)")
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
                         f"{', '.join(sorted(LANES))}")
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
