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
    """One game process's identity: where it runs, and how to reach it."""

    game_dir: Path
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
