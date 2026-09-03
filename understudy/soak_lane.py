"""One install, many lanes: is the bridge staged, is a game up, whose lane.

Cut out of `soak.py` by `EB-180`. `bridge_installed`, `game_is_running` and
`lane_setup` are the functions that file declared, moved whole, and it
re-exports them -- so `soak.game_is_running()` still resolves.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from understudy import instances
from understudy.soak_shape import (BRIDGE_DLL, BRIDGE_MANIFEST,
                                   BRIDGE_RELATIVE, GAME_EXE)


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


# ----------------------------------------------------------- the lanes ----
#
# ONE INSTALL, TWO PROCESSES, AND THE SHARED HALVES ARE NOBODY'S TO TAKE AWAY.
# Three things live in the game DIRECTORY rather than in a lane's own user
# tree, so they are one copy for every lane AND for the game the owner launches
# from Steam: `steam_appid.txt`, the bridge under `mods\STS2_MCP`, and the
# deployed klee build under `mods\klee`.
#
# `steam_appid.txt` is refcounted BY PRE-EXISTENCE -- a lane that finds one
# already there records nothing to revert -- which is how a `--lane 1` run, a
# whole process later than the lane 0 that wrote it, can know something else
# holds it. (The in-memory version of the same rule is
# `local_tester._live_lanes`'s `install_bridge=(i == 0)`, which is a two-lane
# ROUND deciding it once for both its lanes; the flag still exists and still
# binds.)
#
# THE BRIDGE IS NOT REFCOUNTED, BECAUSE IT IS NOT A LANE'S TO OWN, AND `EB-310`
# IS WHAT THE OTHER RULE COST. It used to count as pre-existing only when a
# game was UP on it, so on 2026-09-02, with no game running and the bridge
# already staged by `deploy_proto.ps1`, an `embark --lane 1` re-deployed it and
# wrote it down as ITS OWN install -- and the matching `--teardown --lane 1`
# printed "Deployed mods\STS2_MCP ... REVERTED" and took it out. The owner's
# next Steam launch would have had no bridge. The rule now has no such window:
# a session REFRESHES the shared install when nothing holds the dll, records
# that as `pre_existing` -- *shared, left in place* -- and NOTHING in this
# harness removes it. `deploy_bridge.ps1 -Remove` is the only remover, run by
# hand by whoever decides the machine is done with it.
#
# THE THIRD IS NOT REFCOUNTED AND CANNOT BE: `mods\klee` is ONE deployed build
# for every lane, so a lane cannot be given a different one. `deploy_proto.ps1`
# refuses while ANY `SlayTheSpire2` process is up, by image name -- and that is
# why it must stay by image name rather than by pid.
#
# AND THE REFUSAL THAT USED TO STAND HERE IS GONE, BECAUSE A LIVE ATTEMPT SHOWED
# IT WAS OURS. `deploy_bridge.ps1` refused whenever ANY game process existed,
# on the assumption that a running game holds the bridge dll. An install with
# no `mods\STS2_MCP` in it holds nothing, so that refusal blocked a lane that
# was in no danger -- and Steam's tolerance of a second instance went untested
# for a reason that was never Steam's. The script now asks the only question
# that matters, whether the files it is about to rewrite are LOCKED, and this
# module's job is to not ask it to rewrite an install that is already there
# with a game up on it.
#
# WHICH IS THE WHOLE OF THE REUSE RULE, AND ITS SAFETY ARGUMENT IS THAT IT
# FIRES NOWHERE A DEPLOY USED TO SUCCEED. A session refreshes the bridge every
# time, as it always has, EXCEPT when the bridge is already installed AND a
# game is running -- which until today was a hard failure, not a fresh deploy.
# So nothing that worked before is now reusing a stale install; the only
# behaviour that changed is the behaviour that was a `SystemExit`. What the
# refresh no longer buys is a claim on the directory: see `EB-310` above.


def bridge_installed(where: Path | None = None) -> bool:
    """Is the vendored bridge staged in the shared game directory?

    BOTH files, because both are what `deploy_bridge.ps1` stages: a directory
    holding one of them is a half-install and not an install.
    """
    root = Path(where if where is not None else _soak().game_dir())
    return ((root / BRIDGE_RELATIVE / BRIDGE_DLL).is_file()
            and (root / BRIDGE_RELATIVE / BRIDGE_MANIFEST).is_file())


def game_is_running(probe=None) -> str:
    """The pids of every live `SlayTheSpire2.exe`, or `""` when there are none.

    THE ONE PLACE IN THIS MODULE THAT STILL ASKS BY IMAGE NAME, and it is the
    question that needs it: a kill takes a pid (`_kill`, and `EB-206` is why),
    but "is ANY game up" is asked about a DIRECTORY every lane shares, and a
    pid cannot answer it.

    AN UNREADABLE PROBE ANSWERS YES, the same way `pid_image` treats a failed
    probe as alive. This is asked in order NOT to rewrite files a running game
    might hold; a probe that could not run has not shown that nothing is
    running.
    """
    run = probe if probe is not None else subprocess.run
    try:
        done = run(["tasklist", "/FI", f"IMAGENAME eq {GAME_EXE}", "/NH",
                    "/FO", "CSV"], capture_output=True, text=True, timeout=30)
    except Exception as exc:                                 # noqa: BLE001
        return f"<probe failed: {type(exc).__name__}: {exc}>"
    if getattr(done, "returncode", 1) != 0:
        return f"<probe exited {done.returncode}>"
    # `"SlayTheSpire2.exe","4740","Console","1","1,234,567 K"`, and the
    # not-found answer is a prose line with no quotes in it at all.
    return ", ".join(row.split('","')[1]
                     for row in (done.stdout or "").splitlines()
                     if row.lower().startswith(f'"{GAME_EXE.lower()}"')
                     and '","' in row)


def lane_setup(value: object, *,
               game_dir_override: Path | None = None
               ) -> tuple[Any, bool]:
    """`--lane N` -> `(instance, install_bridge)`.

    Lane 0 answers `(None, True)`: no instance, so the session binds no
    thread, stamps no lane infix on its logs, and behaves in every respect as
    it did before lanes existed.

    EVERY LANE ASKS FOR THE BRIDGE AND NO LANE EVER OWNS IT: an install with a
    game already up on it is left alone, an install with nothing holding it is
    refreshed, and either way the row is recorded `pre_existing` -- *shared,
    left in place* -- so no teardown removes it (`EB-310`). The second lane's
    request therefore costs a `stat` and a `tasklist` and changes nothing. What
    a higher lane must NEVER do is rewrite an install another lane's game has
    loaded, and the last lock on that is the deploy script's own -- it is the
    only party that can see whether a file is actually held.
    """
    inst = instances.cli_lane(value, game_dir=game_dir_override)
    return (None, True) if inst is None else (inst, True)
