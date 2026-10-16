#!/usr/bin/env python3
"""Lay out a Steam Workshop upload workspace for the mod (ModUploader's shape).

`review/active/workshop-readiness-2026-10-14.md`, ruled all (a): [USER] runs
the uploader himself, friends-only first, Yae held back from the first
upload. This tool prepares the workspace and never uploads anything.

    python tools/package_workshop.py --variant public --version 0.3.0 --dry-run
    python tools/package_workshop.py --variant public --version 0.3.0
    python tools/package_workshop.py --variant beta   --version 0.3.0
    # then, by hand:  ModUploader.exe upload -w .workshop/public

WHAT IT BUILDS. `dotnet build -c Release -p:WorkshopRelease=true
-p:GitsKits=<kits>` into `.workshop/_build/<variant>/` (its own output and
intermediate folders, so the dev build in `bin/Release` is untouched). No
harness: the seat bridge (`vendor/STS2_MCP`) is never built or copied.
`WorkshopRelease` turns play telemetry off unless `GITS_TELEMETRY_FEED` is
set; `GitsKits` leaves a kit's character unregistered
(`klee-mod/KleeCode/ReleaseVariant.cs`).

THE WORKSPACE, `.workshop/<variant>/` (gitignored):

    workshop.json            title, description, visibility, changeNote,
                             tags, dependencies (BaseLib 3737335127),
                             contentDescriptors, minBranch/maxBranch null
    image.png                the Workshop preview, < 1 MB
    content/<id>/            ONLY the mod: <id>.dll, <id>.pck, manifest.json,
                             images/cards/*.png (the set deploy stages, less a
                             left-out kit's own art)
    mod_id.txt               written by ModUploader on the first upload and
                             KEPT by every later run of this tool (it is how
                             the next upload updates the same item)

THE TWO VARIANTS.

    public   mod id `klee`,      Klee, Kokomi, Furina, Varka   (Yae left out)
    beta     mod id `klee-beta`, every kit, title "(Beta)"

The game loads `<manifest id>.dll` and `<manifest id>.pck` from the mod's
folder (0.111.0 `ModManager.TryLoadMod`), so the beta's files are named
`klee-beta.*`. Its pck keeps its resources at `res://klee/`, and the mod adds
its own loc table when the manifest id is not `klee`
(`Patches/ReleaseKitsPatch.cs`); the Mods-screen badge
(`res://<id>/mod_image.png`) does not follow and shows blank on the beta.

BOTH VARIANTS REGISTER THE SAME CARD AND CHARACTER IDS (`KLEEMOD-...`) from
an assembly named `klee`, so a player enables ONE of them. What the 0.111.0
loader does with both enabled: two mods with the SAME manifest id fail the
second with MOD_ERROR.DUPLICATE_ID; with different ids (ours) it loads both
dlls into one AssemblyLoadContext, and .NET refuses a second assembly with an
already-loaded name, so the second mod's `LoadFromAssemblyPath` throws inside
`TryLoadMod`'s try and it is marked Failed (MOD_ERROR.EXCEPTION) before its
initializer or its pck loads. The first one plays. That last step is .NET's
rule read off the decompile, not yet seen in the game.

THE VERSION is the plain `--version` (`0.3.0`), required, never the dev
build's `0.2.NNNN+dirty`. Co-op peers need the same version AND the same
variant.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import shipped_card_art  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CSPROJ = ROOT / "klee-mod" / "KleeCode" / "KleeCode.csproj"
SOURCE_MANIFEST = ROOT / "klee-mod" / "Klee" / "manifest.json"
PCK = ROOT / "klee-mod" / "assets" / "klee.pck"
PREVIEW = ROOT / "ImageGen" / "images" / "mod_image.png"
SURFACE = ROOT / "docs" / "prototype-surface.yaml"
OUT = ROOT / ".workshop"

BASELIB_WORKSHOP_ID = 3737335127
VISIBILITIES = ("private", "public", "unlisted", "friends_only")
IMAGE_LIMIT = 1024 * 1024  # "Must be less than 1MB" (uploader template README)
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

ALL_KITS = ("klee", "kokomi", "furina", "varka", "yae")


@dataclass(frozen=True)
class Variant:
    name: str
    mod_id: str
    kits: tuple[str, ...]
    title: str


VARIANTS = {
    "public": Variant("public", "klee", ("klee", "kokomi", "furina", "varka"),
                      "Teyvat Spire Roster"),
    "beta": Variant("beta", "klee-beta", ALL_KITS,
                    "Teyvat Spire Roster (Beta)"),
}

# DRAFT for [USER] to edit (the first line says so, so it cannot go up by
# accident unread). Plain text: the Workshop page renders BBCode, none used.
DESCRIPTION_DRAFT = """\
[DRAFT: edit before upload, then delete this line.]
Four Genshin Impact characters as playable characters for Slay the Spire 2, each with their own card pool, starter relic and elemental reactions:

- Klee (Pyro): sets Bombs and sets them off. Fast and fragile.
- Varka (Anemo): his Knights set his element, and every aura he Swirls swears Oath to his blade.
- Furina (Hydro): runs the Stage, a cast of performers who act at the end of her turn.
- Sangonomiya Kokomi (Hydro): plays Plan cards on her Bake-Kurage, which carries them out next turn.

After each fight the card reward offers a fourth choice: a Companion card from the wider cast of Teyvat.

Free. Fan-made, not affiliated with HoYoverse or Mega Crit.
Requires BaseLib.
Co-op: both players need the same version of this mod and the same variant (this one or the Beta)."""

BETA_NOTE = """

BETA: every kit, including Yae Miko (in progress). Enable this or the main release, not both."""


# ------------------------------------------------------------- pure parts ---

def check_version(version: str) -> str:
    if not VERSION_RE.match(version or ""):
        raise SystemExit(f"--version must be plain MAJOR.MINOR.PATCH (0.3.0), "
                         f"got {version!r}")
    return version


def build_args(variant: Variant, version: str, out_dir: Path) -> list[str]:
    """The release build's command line. `+` separates the kits because `;`
    and `,` split an MSBuild `-p:` value."""
    return [
        "dotnet", "build", str(CSPROJ), "-c", "Release", "-v", "minimal",
        "--nologo",
        "-p:WorkshopRelease=true",
        f"-p:GitsKits={'+'.join(variant.kits)}",
        f"-p:AssemblyVersion={version}",
        f"-p:FileVersion={version}",
        f"-p:InformationalVersion={version}+workshop.{variant.name}",
        "-p:IncludeSourceRevisionInInformationalVersion=false",
        f"-p:OutDir={out_dir / 'bin'}/",
        f"-p:IntermediateOutputPath={out_dir / 'obj'}/",
    ]


def manifest_for(variant: Variant, version: str, source: dict) -> dict:
    m = dict(source)
    m["id"] = variant.mod_id
    m["version"] = version
    if variant.name == "beta":
        m["name"] = f"{source.get('name', 'Teyvat Spire Roster')} (Beta)"
        m["description"] = (source.get("description", "")
                            + " Beta: every kit, Yae Miko included (in progress).")
    return m


def workshop_json(variant: Variant, version: str, visibility: str,
                  change_note: str | None) -> dict:
    if visibility not in VISIBILITIES:
        raise SystemExit(f"--visibility must be one of {', '.join(VISIBILITIES)}")
    description = DESCRIPTION_DRAFT + (BETA_NOTE if variant.name == "beta" else "")
    return {
        "title": variant.title,
        "description": description,
        "visibility": visibility,
        "changeNote": change_note or f"Version {version}.",
        "tags": [],
        "dependencies": [BASELIB_WORKSHOP_ID],
        "contentDescriptors": [],
        "minBranch": None,
        "maxBranch": None,
    }


def excluded_kit_art(variant: Variant, ship: dict[str, Path],
                     surface: Path = SURFACE) -> set[str]:
    """Stems a left-out kit owns and no shipped row draws: a png under the
    kit's own `cards/<kit>/` folder, or a surface row of that kit, unless a
    row of a shipped kit (or a Companion) wears the same key."""
    left_out = set(ALL_KITS) - set(variant.kits)
    if not left_out:
        return set()
    rows = yaml.safe_load(surface.read_text(encoding="utf-8")) or []
    kept_keys, dropped_keys = set(), set()
    for row in rows:
        if not isinstance(row, dict) or "id" not in row:
            continue
        key = row.get("art_of") or row["id"]
        (dropped_keys if row.get("character") in left_out else kept_keys).add(key)
    by_dir = {s for s, p in ship.items() if p.parent.name in left_out}
    return (dropped_keys | by_dir) - kept_keys


def placeholder_image(dest: Path, title: str) -> None:
    """A plain stand-in preview, well under 1 MB."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (512, 512), (36, 30, 58))
    draw = ImageDraw.Draw(img)
    draw.rectangle((16, 16, 495, 495), outline=(214, 178, 96), width=4)
    draw.text((40, 236), title, fill=(240, 232, 210))
    draw.text((40, 262), "preview image: placeholder", fill=(170, 160, 190))
    img.save(dest, "PNG", optimize=True)


# ------------------------------------------------------------------ plan ---

@dataclass
class Entry:
    path: str          # workspace-relative
    size: int | None   # bytes, None = produced later (by the build)
    source: str


def plan(variant: Variant, version: str, *, dll: Path, pck: Path,
         images_root: Path, image: Path | None) -> tuple[list[Entry], list[str], dict]:
    """(entries, notes, art) for one workspace. Reads, never writes."""
    notes: list[str] = []
    cid = f"content/{variant.mod_id}"
    entries = [
        Entry("workshop.json", None, "generated"),
        Entry(f"{cid}/manifest.json", None, f"{SOURCE_MANIFEST.relative_to(ROOT)}, id/version set"),
        Entry(f"{cid}/{variant.mod_id}.dll", dll.stat().st_size if dll.exists() else None,
              "release build" + ("" if dll.exists() else " (not built yet)")),
    ]
    if not pck.exists():
        notes.append(f"NO PCK at {pck}: run tools/build_pck.ps1 on the main checkout")
    entries.append(Entry(f"{cid}/{variant.mod_id}.pck",
                         pck.stat().st_size if pck.exists() else None, str(pck)))

    ship, _dropped, missing = shipped_card_art.plan(images_root)
    left_out = excluded_kit_art(variant, ship)
    art = {s: p for s, p in ship.items() if s not in left_out}
    art_size = sum(p.stat().st_size for p in art.values())
    entries.append(Entry(f"{cid}/images/cards/ ({len(art)} png)", art_size,
                         str(images_root)))
    if left_out & set(ship):
        notes.append(f"left out {len(left_out & set(ship))} png of the kit(s) "
                     f"{', '.join(sorted(set(ALL_KITS) - set(variant.kits)))}")
    if missing:
        notes.append(f"{len(missing)} card key(s) have no png and draw the blank portrait")

    if image and image.exists():
        size = image.stat().st_size
        entries.append(Entry("image.png", size, str(image)))
        if size >= IMAGE_LIMIT:
            notes.append(f"PREVIEW TOO BIG: {image} is {size} bytes (limit 1 MB)")
        if image.name == PREVIEW.name:
            notes.append("image.png is the Mods-screen badge (Klee, Furina, Kokomi; "
                         "no Varka), a stand-in until real preview art exists")
    else:
        entries.append(Entry("image.png", None, "generated placeholder"))
        notes.append("NO PREVIEW ART: image.png is a generated placeholder")
    return entries, notes, art


def print_plan(variant: Variant, version: str, workspace: Path,
               entries: list[Entry], notes: list[str]) -> None:
    print(f"workspace {workspace}  (variant {variant.name}, mod id {variant.mod_id}, "
          f"version {version}, kits {'+'.join(variant.kits)})")
    total = 0
    for e in entries:
        size = "--" if e.size is None else f"{e.size / 1e6:9.2f} MB"
        total += e.size or 0
        print(f"  {e.path:<46} {size:>12}  {e.source}")
    print(f"  {'total (known sizes)':<46} {total / 1e6:9.2f} MB")
    for n in notes:
        print(f"  note: {n}")


# ----------------------------------------------------------------- write ---

def _blob(text: str) -> bytes:
    """A short string as a custom-attribute blob stores it: one length byte,
    then UTF-8. Exact, so `klee+kokomi+furina+varka` does not match inside
    the beta's `...+varka+yae`."""
    raw = text.encode()
    assert len(raw) < 128
    return bytes([len(raw)]) + raw


def check_dll(dll: Path, variant: Variant) -> None:
    """The built dll carries the release flag and this variant's kit list."""
    data = dll.read_bytes()
    lost = [w for w in ("GitsWorkshopRelease", "GitsKits", "+".join(variant.kits))
            if _blob(w) not in data]
    if lost:
        raise SystemExit(f"{dll} lacks {lost}: not a workshop build of {variant.name}")


def write_workspace(variant: Variant, version: str, workspace: Path, *,
                    dll: Path, pck: Path, art: dict[str, Path],
                    image: Path | None, visibility: str,
                    change_note: str | None) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    content = workspace / "content"
    if content.exists():
        shutil.rmtree(content)
    mod = content / variant.mod_id
    cards = mod / "images" / "cards"
    cards.mkdir(parents=True)

    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    with open(mod / "manifest.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest_for(variant, version, source), f, indent=2, ensure_ascii=False)
        f.write("\n")
    shutil.copy2(dll, mod / f"{variant.mod_id}.dll")
    shutil.copy2(pck, mod / f"{variant.mod_id}.pck")
    for stem, path in sorted(art.items()):
        shutil.copy2(path, cards / f"{stem}.png")

    # The game parses EVERY .json under a mod folder as a manifest.
    stray = [p for p in content.rglob("*.json") if p != mod / "manifest.json"]
    if stray:
        raise SystemExit(f"stray json in content: {stray}")

    with open(workspace / "workshop.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(workshop_json(variant, version, visibility, change_note), f,
                  indent=2, ensure_ascii=False)
        f.write("\n")
    target = workspace / "image.png"
    if image and image.exists():
        shutil.copy2(image, target)
    else:
        placeholder_image(target, variant.title)
    if target.stat().st_size >= IMAGE_LIMIT:
        raise SystemExit(f"{target} is {target.stat().st_size} bytes; the limit is 1 MB")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    ap.add_argument("--version", required=True, help="plain MAJOR.MINOR.PATCH")
    ap.add_argument("--visibility", default="friends_only", choices=VISIBILITIES)
    ap.add_argument("--change-note")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the layout and sizes; build and write nothing")
    ap.add_argument("--skip-build", action="store_true",
                    help="reuse this variant's last workshop build")
    ap.add_argument("--pck", type=Path, default=PCK)
    ap.add_argument("--images-root", type=Path, default=shipped_card_art.IMAGES)
    ap.add_argument("--image", type=Path, default=PREVIEW,
                    help="preview png (< 1 MB); a placeholder if absent")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    variant = VARIANTS[args.variant]
    version = check_version(args.version)
    workspace = args.out / variant.name
    build_dir = args.out / "_build" / variant.name
    dll = build_dir / "bin" / "klee.dll"

    if not args.dry_run and not args.skip_build:
        cmd = build_args(variant, version, build_dir.resolve())
        print("building:", " ".join(cmd[1:]), flush=True)
        if subprocess.run(cmd, cwd=ROOT).returncode != 0:
            print("build failed", file=sys.stderr)
            return 1

    entries, notes, art = plan(variant, version, dll=dll, pck=args.pck,
                               images_root=args.images_root, image=args.image)
    print_plan(variant, version, workspace, entries, notes)
    if args.dry_run:
        print("dry run: nothing built or written")
        return 0

    if not dll.exists():
        print(f"no build at {dll}", file=sys.stderr)
        return 1
    if not args.pck.exists():
        print(f"no pck at {args.pck}", file=sys.stderr)
        return 1
    check_dll(dll, variant)
    write_workspace(variant, version, workspace, dll=dll, pck=args.pck, art=art,
                    image=args.image, visibility=args.visibility,
                    change_note=args.change_note)
    print(f"wrote {workspace}")
    if (workspace / "mod_id.txt").exists():
        print(f"  mod_id.txt kept: the upload updates item "
              f"{(workspace / 'mod_id.txt').read_text(encoding='utf-8').strip()}")
    print(f"  next, by hand: ModUploader.exe upload -w {workspace}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
