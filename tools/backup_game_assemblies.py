#!/usr/bin/env python3
"""EB-172: keep a copy of the PINNED managed assemblies where Steam cannot reach it.

WHY, IN ONE SENTENCE FROM [USER] (2026-08-28, on the v0.111.0 update that
broke every C# build mid-sitting): *"This implies a patch update could also
brick us."* It does, and it did. Every assembly `KleeCode`, `KleeTests` and the
vendored bridge compile against lives under Steam's control:

  * `sts2.dll`, `0Harmony.dll`, `GodotSharp.dll` -- the game's own
    `data_sts2_windows_x86_64`, replaced by any patch on any branch;
  * `BaseLib.dll` -- a Steam Workshop item, replaced whenever its author
    publishes.

Nothing warns first. On 2026-08-28 the install moved from v0.107.1 to v0.111.0
because a co-op session had switched the app to `public-beta`, and from that
moment the repo could not compile at all.

WHAT THIS BUYS, STATED NARROWLY. **A Steam update can still stop a live RUN,
and no local copy fixes that** -- a run needs the game, and the game is what
moved. What it must never again be able to do is stop the BUILD. With this
mirror in place and `-p:UsePinnedAssemblies=true`, `dotnet build` keeps working
against the pin while the port is decided and written, instead of the tree
being dead until it lands.

THE VAULT IS THE ONEDRIVE ONE, and deliberately the same one `game_ref` uses:
`C:\\Users\\Monty\\OneDrive\\GItS-vault\\game_assemblies`, beside
`.../GItS-vault/game_ref`, ruled by [USER] 2026-08-24 ("Agreed on the backup in
OneDrive"). OneDrive because it is NOT a directory git or a worktree teardown
can reach -- see `tools/backup_game_ref.py`'s header for the four losses that
rule came out of. **Backups never live in worktrees.**

HOW THIS DIFFERS FROM `backup_game_ref`, which it otherwise mirrors:

  * The source is an EXACT SET of four named files from TWO roots, not a tree,
    so the guard is "all four present" rather than a file-count floor. A
    partial set is refused: three of four assemblies is not a buildable pin,
    and a mirror that copied what it found would leave one that looks fine.
  * It writes `PIN.json` beside them -- game version, commit, buildid, branch,
    BaseLib version, and each file's size and sha256. WITHOUT THAT FILE THE
    BACKUP IS ANONYMOUS: four dlls in a folder cannot say which build they
    are, and "build against the pin" is unverifiable. The lint reads it.
  * It never deletes. `game_ref`'s mirror prunes because its source is the
    authority; here the vault IS the authority for a build the live install no
    longer has, so an old generation is data, not litter. Superseding one is a
    deliberate re-run after a deliberate re-pin.

    python -m tools.backup_game_assemblies              # mirror
    python -m tools.backup_game_assemblies --dry-run    # say what it would do

Exit 0 (mirrored), 2 (refused). Windows-only for the same reason and by the
same check as its sibling: off Windows the hard-coded vault string is a
RELATIVE path and an unguarded mirror would build a faux `C:\\Users\\...`
directory under the working directory and call it a backup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parent.parent

# Same vault root as game_ref's, one directory over. Hard-coded for the same
# reason: a configurable backup root can be pointed at a temp directory and
# quietly stop being a backup.
VAULT_SPEC = r"C:\Users\Monty\OneDrive\GItS-vault\game_assemblies"
VAULT_WINDOWS = PureWindowsPath(VAULT_SPEC)
VAULT = Path(VAULT_SPEC)

# The reference set, read off klee-mod/KleeCode/KleeCode.csproj rather than
# invented: three `$(GameDataDir)\...` references and one `$(BaseLibDll)`.
# KleeTests and the vendored bridge reference the same four.
GAME_ASSEMBLIES = ("sts2.dll", "0Harmony.dll", "GodotSharp.dll")
BASELIB_ASSEMBLY = "BaseLib.dll"
ASSEMBLIES = GAME_ASSEMBLIES + (BASELIB_ASSEMBLY,)

PIN_FILE = "PIN.json"

LOCAL_PROPS = ROOT / "klee-mod" / "local.props"


# --- reading the machine ---------------------------------------------------

def _prop(text: str, name: str) -> str | None:
    m = re.search(rf"<{name}>(.*?)</{name}>", text, re.S)
    return m.group(1).strip() if m else None


def local_props_paths() -> tuple[Path | None, Path | None]:
    """(game data dir, BaseLib.dll) as `local.props` resolves them, or Nones.

    Deliberately a re-read of the same file MSBuild reads rather than a second
    place to configure the paths: two sources of truth for "where is the game"
    is exactly the drift this repo keeps writing lints about.
    """
    if not LOCAL_PROPS.is_file():
        return None, None
    text = LOCAL_PROPS.read_text(encoding="utf-8")
    baselib = _prop(text, "BaseLibDll")
    data = _prop(text, "GameDataDir")
    if data is None:
        game_dir = _prop(text, "GameDir")
        if game_dir:
            # The Windows arm of Directory.Build.props' own resolution order.
            cand = Path(game_dir) / "data_sts2_windows_x86_64"
            data = str(cand) if (cand / "sts2.dll").is_file() else None
    return (Path(data) if data else None,
            Path(baselib) if baselib else None)


def release_info(data_dir: Path) -> dict:
    """`release_info.json` from the install root above `data_dir`, or {}."""
    f = data_dir.parent / "release_info.json"
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def baselib_version(baselib_dll: Path) -> str | None:
    """`version` out of the Workshop item's own `BaseLib.json`, or None."""
    f = baselib_dll.with_name("BaseLib.json")
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8-sig")).get("version")
    except (OSError, ValueError):
        return None


def steam_buildid(data_dir: Path) -> tuple[str | None, str | None]:
    """(buildid, betakey) from Steam's app manifest, or (None, None).

    Best effort and stated as such: the manifest is found by walking up from
    the install to `steamapps`, which is the layout on this machine and not a
    guarantee. A missing value is recorded as null in PIN.json rather than
    guessed -- an anonymous field beats a wrong one.
    """
    for parent in data_dir.parents:
        acf = parent / "appmanifest_2868840.acf"
        if acf.is_file():
            text = acf.read_text(encoding="utf-8", errors="replace")
            bid = re.search(r'"buildid"\s+"(\d+)"', text)
            key = re.search(r'"BetaKey"\s+"([^"]*)"', text)
            return (bid.group(1) if bid else None,
                    key.group(1) if key else "public")
    return None, None


# --- the mirror ------------------------------------------------------------

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sources(data_dir: Path | None, baselib_dll: Path | None
            ) -> dict[str, Path]:
    """{file name: absolute source path} for the four, as configured."""
    out: dict[str, Path] = {}
    if data_dir is not None:
        for name in GAME_ASSEMBLIES:
            out[name] = data_dir / name
    if baselib_dll is not None:
        out[BASELIB_ASSEMBLY] = baselib_dll
    return out


def guard(src: dict[str, Path]) -> str | None:
    """The refusal reason, or None when mirroring is safe.

    Split out from `main` so the suite (and a reader) can see the refusal
    without running a mirror -- `backup_game_ref`'s shape.
    """
    missing = [n for n in ASSEMBLIES if n not in src or not src[n].is_file()]
    if missing:
        return ("the reference set is incomplete on this machine; missing "
                + ", ".join(missing))
    return None


def platform_refusal(vault: Path) -> str | None:
    """None, or why `vault` is not a destination this host can back up to.

    Identical in shape and reasoning to `backup_game_ref.platform_refusal`;
    duplicated rather than imported because the two tools must be able to
    disagree about their vaults without one silently retargeting the other.
    """
    if vault == Path(VAULT_SPEC) and sys.platform != "win32":
        return (f"the configured vault is a Windows path and this host is "
                f"{sys.platform}, where it is a RELATIVE path: {vault}")
    if not vault.is_absolute():
        return f"vault path is not absolute on {sys.platform}: {vault}"
    return None


def build_pin(src: dict[str, Path], data_dir: Path,
              baselib_dll: Path) -> dict:
    """The PIN.json body: what these four files ARE."""
    info = release_info(data_dir)
    buildid, betakey = steam_buildid(data_dir)
    return {
        "why": ("EB-172 / R218 C. The managed assemblies the repo compiles "
                "against, copied out of Steam's reach so a game update can "
                "stop a run but never the build."),
        "game_version": info.get("version"),
        "game_commit": info.get("commit"),
        "game_date": info.get("date"),
        "main_assembly_hash": info.get("main_assembly_hash"),
        "steam_buildid": buildid,
        "steam_branch": betakey,
        "baselib_version": baselib_version(baselib_dll),
        "files": {
            name: {"size": src[name].stat().st_size, "sha256": sha256(src[name])}
            for name in ASSEMBLIES
        },
    }


def mirror(src: dict[str, Path], vault: Path, pin: dict,
           dry_run: bool = False) -> tuple[list[str], list[str]]:
    """Return (written, unchanged) as sorted name lists. Never deletes."""
    written, unchanged = [], []
    for name in ASSEMBLIES:
        dst = vault / name
        s = src[name].stat()
        if dst.exists() and dst.stat().st_size == s.st_size \
                and sha256(dst) == pin["files"][name]["sha256"]:
            unchanged.append(name)
            continue
        written.append(name)
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src[name], dst)        # copy2 keeps mtime
    if not dry_run:
        vault.mkdir(parents=True, exist_ok=True)
        (vault / PIN_FILE).write_text(
            json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    return sorted(written), sorted(unchanged)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args(argv)

    data_dir, baselib_dll = local_props_paths()
    src = sources(data_dir, baselib_dll)

    print(f"backup_game_assemblies: game  ={data_dir}")
    print(f"                        baselib={baselib_dll}")
    print(f"                        vault ={VAULT}")

    refusal = platform_refusal(VAULT)
    if refusal is not None:
        print()
        print("  REFUSING TO MIRROR -- " + refusal)
        print("  Mirroring here would not reach any vault: it would CREATE a")
        print("  directory of that literal name under the working directory")
        print("  and report success. The vault was NOT touched.")
        return 2

    refusal = guard(src)
    if refusal is not None:
        print()
        print("  REFUSING TO MIRROR -- " + refusal)
        print("  Three of four assemblies is not a buildable pin, and a")
        print("  partial vault is worse than none: it looks like a backup.")
        print("  Fix klee-mod/local.props, or install the missing piece.")
        return 2

    assert data_dir is not None and baselib_dll is not None
    pin = build_pin(src, data_dir, baselib_dll)
    written, unchanged = mirror(src, VAULT, pin, dry_run=args.dry_run)

    print()
    if args.dry_run:
        print("  DRY RUN -- nothing was written; counts are what WOULD happen")
    print(f"  pin: game {pin['game_version']} ({pin['game_commit']}), "
          f"buildid {pin['steam_buildid']}, branch {pin['steam_branch']}, "
          f"BaseLib {pin['baselib_version']}")
    print("  " + "count".rjust(6) + "  action")
    print(f"  {len(written):6d}  written to vault")
    print(f"  {len(unchanged):6d}  already current")
    for name in written:
        print(f"    write  {name}")
    print()
    print("  Build against it with:")
    print("    dotnet build klee-mod/KleeCode/KleeCode.csproj "
          "-p:UsePinnedAssemblies=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
