"""Placeholder-but-complete act asset sets for the six Teyvat act dressings.

WHY THIS EXISTS. `ActModel.FilePathIdentifier` is `Id.Entry.ToLowerInvariant()`
and five NON-VIRTUAL properties derive every act-dressing path from it: the
combat background scene, the rest-site scene and the three map background PNGs
(`MegaCrit.Sts2.Core.Models/ActModel.cs:52-64`, `:248`).
`Rooms/BackgroundAssets`'s constructor THROWS rather than falls back on a
missing `layers` directory and on a layer file matching neither `_bg_NN` nor
`_fg_`. The spike therefore shipped a Harmony postfix on
`get_FilePathIdentifier` that aliased MONDSTADT to `overgrowth` and LIYUE to
`underdocks` (`review/records/teyvat-spike-build-2026-09-15.md` item 1).

This generator retires that alias for every dressing by producing a COMPLETE
set per face -- act 1's Mondstadt and Liyue, act 2's Natlan and Inazuma, act
3's Fontaine and Sumeru -- so the loaders are satisfied by our own files. The
alias table stays, and stays right, as the fallback for a build whose pck
predates a set.

THE REST SITE IS THE ONE PATH THIS FILE DOES NOT AUTHOR A SCENE FOR, and that
is a fix rather than a gap. We shipped one until 2026-09-17: a `RestSiteBG`
plus an EMPTY `%RestSiteLighting`, which is all `NRestSiteRoom._Ready`'s
`GetNode<Control>("%RestSiteLighting")` asks for. A BASE character's Spine
campfire figure asks for much more, and the game died NATIVELY -- no managed
trace, the log ending at "Preloading 'RestSite Room' Complete" -- the first
time [USER] took the Silent into a Mondstadt campfire. A dressing now wears the
BASE zone's whole campfire scene (`Patches/TeyvatRestSitePatch` aliases
`RestSiteBackgroundPath` unconditionally) and only its PLATE is ours, swapped
into that scene's own `RestSiteBG` by a postfix on
`ActModel.CreateRestSiteBackground`. So the rest-site row below is a PNG and
nothing else. Nothing here is art:
every picture it still writes is a two-stop vertical gradient in the nation's
colours, and a real plate replaces it through an `art/plan.tsv` row recorded in
`media/ACT.tsv` (`docs/current/operations/media.md` sec.1) with no scene
re-authored and no `res://` path moved.

WHAT IT WRITES, AND WHERE. Two trees and only two:

  * `ImageGen/images/teyvat/...`  -- the PNGs. GITIGNORED, Tier F, and the
    directory `tools/build_pck.ps1`'s Teyvat act blocks copy from.
  * `klee-mod/pck-src/scenes/...` -- the `.tscn` sources. COMMITTED, because
    a scene is text and because `pck-src` overlays the export work directory
    verbatim, which is what puts them at the `res://scenes/...` paths the
    engine derives and nothing else can move.

`docs/current/operations/act-assets.md` is the shape in one table and the
command line. Run it with the venv python by absolute path:

    .venv\\Scripts\\python.exe tools\\gen_act_placeholders.py

`--check` writes nothing and exits non-zero if any planned file is missing or
any committed scene source differs from what this file would write; that is
the staleness gate `tier0/tests/test_act_placeholder_plan.py` rides.

REAL ART STANDS THIS GENERATOR DOWN, PATH BY PATH. `art/plan.tsv` is the
producer for any plate a bill claims (`docs/current/research/
teyvat-act-art-sources-2026-09-17.md`), so `plan_owned()` reads that file and
every out-path it names under `ImageGen/images/teyvat/backgrounds|rest_site|
map_bgs` is skipped here -- by `write_all`, so a generator run cannot overwrite
a fetched picture, and by `check`, so `--check` does not demand a file this
file no longer produces. ONE PRODUCER PER OUT-PATH, the rule `art/plan.tsv`
already runs under.

The five plates BESIDE a real `bg_00` stay this generator's job, and they turn
TRANSPARENT rather than gradient: `NCombatBackground` stacks `Layer_00` ..
`Layer_04` and the foreground over one another, so an opaque gradient on
`bg_01` would simply hide the landscape underneath it. Transparency is the
generator's rather than five more plan rows because a transparent plate is not
art -- there is no source to pick, no crop to judge and nothing for a veto to
look at, which is the line `gen_furina_stills.py` and the salon glyphs already
sit on.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# the shape, stated once
# --------------------------------------------------------------------------

#: `BackgroundAssets`'s constructor groups layer files by the `_bg_NN` prefix
#: and picks ONE per group with the combat rng, then makes one further draw
#: over the `_fg_` list. So the number of DRAWS is the number of groups plus
#: one, whatever the variant count -- and matching the base zone's five groups
#: plus a foreground keeps a dressing's rng consumption identical to the zone
#: it stands beside (Overgrowth and Underdocks both ship `bg_00`..`bg_04`).
#: One variant each, `_a`, because a placeholder has nothing to vary.
BG_GROUPS = 5
FG_VARIANT = "a"
BG_VARIANT = "a"

#: The layer `TextureRect`'s own rect in the base game's layer scenes is
#: 2764.8 x 1296 (offsets -1382.4..1382.4, -648..648) with `expand_mode = 1`,
#: which SCALES the texture to the rect -- so the placeholder is authored at
#: half that, exactly on aspect, and the pack carries a quarter of the pixels.
LAYER_RECT = (2764.8, 1296.0)
LAYER_PNG = (1382, 648)

#: The map screen's three `TextureRect`s are `expand_mode = 1`,
#: `stretch_mode = 5` (KEEP_ASPECT_CENTERED) with `custom_minimum_size`
#: (0, 1080), so ASPECT is what has to be right. The base game's four acts all
#: ship 2035x1440 and the placeholder matches them exactly.
MAP_PNG = (2035, 1440)

#: The rest-site background sits in `rest_site_room.tscn`'s `BgContainer` at
#: the same 2764.8 x 1296 rect as a combat layer, with `expand_mode = 1` --
#: and the plate now lands in the BASE zone scene's own `RestSiteBG`, whose
#: rect is the same, so the size is unchanged by the 2026-09-17 fix.
REST_PNG = (1382, 648)


@dataclass(frozen=True)
class Nation:
    """One dressing: its `FilePathIdentifier` and its two gradient stops.

    `FilePathIdentifier` is `Id.Entry.ToLowerInvariant()`, so `id` here is the
    lowercase spelling and `entry` the `MONDSTADT` / `LIYUE` the loc table and
    `TeyvatFrame`'s tables use.
    """

    id: str
    entry: str
    #: top-of-frame stop, RGB
    sky: tuple[int, int, int]
    #: bottom-of-frame stop, RGB
    ground: tuple[int, int, int]


#: Mondstadt is sky-blue over meadow green; Liyue is amber over stone. Two
#: stops per nation and nothing else: the depth reading comes from the per-layer
#: darkening below, not from a second palette.
#:
#: SIX FACES, TWO PER ACT (R273 layout 1). Act 1's pair dresses two base zones
#: (Overgrowth, Underdocks); acts 2 and 3 each have ONE base zone with two
#: faces on it -- the Hive as Natlan or Inazuma, Glory as Fontaine or Sumeru
#: (`review/ruled/teyvat-nation-mapping-2026-09-14.md` sec.1). Nothing in this
#: file knows or cares which: a face is an id and two stops, and it gets the
#: same seventeen files either way, because every path derives from
#: `FilePathIdentifier` and not from the zone underneath it.
NATIONS = (
    Nation(id="mondstadt", entry="MONDSTADT", sky=(122, 176, 214), ground=(96, 138, 74)),
    Nation(id="liyue", entry="LIYUE", sky=(214, 164, 86), ground=(108, 100, 92)),
    # Act 2, the Hive: Natlan warm red over gold, Inazuma violet over indigo.
    Nation(id="natlan", entry="NATLAN", sky=(198, 84, 56), ground=(206, 158, 74)),
    Nation(id="inazuma", entry="INAZUMA", sky=(146, 108, 196), ground=(58, 62, 122)),
    # Act 3, Glory: Fontaine teal over white, Sumeru green over sand.
    Nation(id="fontaine", entry="FONTAINE", sky=(86, 170, 178), ground=(226, 232, 234)),
    Nation(id="sumeru", entry="SUMERU", sky=(92, 156, 88), ground=(206, 184, 132)),
)


@dataclass(frozen=True)
class Planned:
    """One file this generator owns.

    `repo` is relative to the repository root. `res` is the `res://` path the
    file reaches in the merged pack, and is `None` for a source that is not
    itself packed (there are none today -- every row is packed -- but the
    field keeps the contract comparison honest if that ever changes).
    """

    kind: str  # "png" | "scene"
    repo: str
    res: str


def plan() -> list[Planned]:
    """Every file, for every dressing, in one list.

    THIS IS THE PIN. `tier0/tests/test_act_placeholder_plan.py` asserts that
    the `res` column of this list is exactly the set of Teyvat act rows in
    `tools/visual_qa/fixtures/sample.contract.txt`, so a file added here
    without a contract row -- or a row with no producer -- fails headlessly,
    long before a pck build or a deploy could notice.
    """
    rows: list[Planned] = []
    for nation in NATIONS:
        i = nation.id
        # --- combat background: layer textures, layer scenes, the root ----
        for group in range(BG_GROUPS):
            rows.append(Planned(
                "png",
                f"ImageGen/images/teyvat/backgrounds/{i}/{i}_bg_{group:02d}.png",
                f"res://teyvat/backgrounds/{i}/{i}_bg_{group:02d}.png"))
            rows.append(Planned(
                "scene",
                f"klee-mod/pck-src/scenes/backgrounds/{i}/layers/"
                f"{i}_bg_{group:02d}_{BG_VARIANT}.tscn",
                f"res://scenes/backgrounds/{i}/layers/"
                f"{i}_bg_{group:02d}_{BG_VARIANT}.tscn"))
        rows.append(Planned(
            "png",
            f"ImageGen/images/teyvat/backgrounds/{i}/{i}_fg.png",
            f"res://teyvat/backgrounds/{i}/{i}_fg.png"))
        rows.append(Planned(
            "scene",
            f"klee-mod/pck-src/scenes/backgrounds/{i}/layers/{i}_fg_{FG_VARIANT}.tscn",
            f"res://scenes/backgrounds/{i}/layers/{i}_fg_{FG_VARIANT}.tscn"))
        rows.append(Planned(
            "scene",
            f"klee-mod/pck-src/scenes/backgrounds/{i}/{i}_background.tscn",
            f"res://scenes/backgrounds/{i}/{i}_background.tscn"))
        # --- rest site: the PLATE only, never a scene ----------------------
        # A dressing ships NO rest-site scene. It wears the BASE zone's --
        # `Patches/TeyvatRestSitePatch` aliases `RestSiteBackgroundPath`
        # unconditionally -- and a Harmony postfix on
        # `ActModel.CreateRestSiteBackground` swaps this plate into that
        # scene's own `RestSiteBG` TextureRect. Our own scene was a
        # `RestSiteBG` plus an EMPTY `%RestSiteLighting`: it satisfied
        # `NRestSiteRoom._Ready` and then HARD-CRASHED the game -- native, no
        # managed trace, the log ending at "Preloading 'RestSite Room'
        # Complete" -- the moment a BASE character's Spine campfire figure
        # reached for the lighting tree that was not there ([USER],
        # 2026-09-17, the Silent at her first campfire).
        rows.append(Planned(
            "png",
            f"ImageGen/images/teyvat/rest_site/{i}_rest_site_bg.png",
            f"res://teyvat/rest_site/{i}_rest_site_bg.png"))
        # --- map screen ---------------------------------------------------
        for slot in ("top", "middle", "bottom"):
            rows.append(Planned(
                "png",
                f"ImageGen/images/teyvat/map_bgs/{i}/map_{slot}_{i}.png",
                f"res://images/packed/map/map_bgs/{i}/map_{slot}_{i}.png"))
    return rows


# --------------------------------------------------------------------------
# who produces what
# --------------------------------------------------------------------------

#: The three repo directories a dressing's PNGs live in. A plan row claiming an
#: out-path under one of these is claiming a plate this file would otherwise
#: write, and that is the whole test: the surface is decided by the path,
#: because the path is the only thing `ActModel` lets us choose.
PLAN_OWNABLE = (
    "ImageGen/images/teyvat/backgrounds/",
    "ImageGen/images/teyvat/rest_site/",
    "ImageGen/images/teyvat/map_bgs/",
)


def plan_owned() -> set[str]:
    """Repo-relative act plates that `art/plan.tsv` produces, not this file.

    THE BILL IS READ FROM THIS CHECKOUT, never from `--root`. That is the same
    split `tools/art_process.py`'s `--art-root` already runs under and for the
    same reason: a branch adding plan rows renders them against, and into, the
    ART-BEARING checkout's gitignored tree, so the pixels move and the tracked
    plan does not. Reading the bill from `--root` would make a worktree run
    consult main's plan, find no act rows, and paint gradients over the
    landscapes it had just fetched.

    Read tolerantly and by hand rather than through `tools/art_fetch.read_plan`:
    that function `sys.exit`s on a short row and imports nothing this file
    needs, and the only column wanted here is the second one. Same encoding and
    line-ending rules as every other ledger reader in the repo -- UTF-8,
    `newline=""` then strip `\\r`, split on TAB alone.

    A missing `art/plan.tsv` returns the empty set, which is the right answer
    and not a silent one: with no bill, this generator owns every path, exactly
    as it did before any real art existed.
    """
    plan = ROOT / "art" / "plan.tsv"
    if not plan.exists():
        return set()
    owned: set[str] = set()
    with plan.open("r", encoding="utf-8", newline="") as handle:
        for line in handle:
            line = line.rstrip("\r\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            out = parts[1].strip().replace("\\", "/")
            if out.startswith(PLAN_OWNABLE):
                owned.add(out)
    return owned


# --------------------------------------------------------------------------
# the pictures
# --------------------------------------------------------------------------

def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))  # type: ignore[return-value]


def _scale(c: tuple[int, int, int], f: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, round(v * f))) for v in c)  # type: ignore[return-value]


def _gradient(size: tuple[int, int], top: tuple[int, int, int],
              bottom: tuple[int, int, int]):
    """A two-stop vertical gradient, RGBA, opaque.

    Drawn one row at a time onto a 1-pixel-wide image and then resized, which
    is both exact and fast at 2035x1440 -- Pillow's bilinear resize of a 1xH
    strip reproduces the same column H times with no interpolation error in
    the vertical direction (the strip already has one sample per output row).
    """
    from PIL import Image

    height = size[1]
    strip = Image.new("RGBA", (1, height))
    for y in range(height):
        t = y / (height - 1) if height > 1 else 0.0
        strip.putpixel((0, y), (*_mix(top, bottom, t), 255))
    return strip.resize(size, Image.NEAREST)


def _write_png(path: Path, size: tuple[int, int], top: tuple[int, int, int],
               bottom: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _gradient(size, top, bottom).save(path, "PNG")


def _write_clear_png(path: Path, size: tuple[int, int]) -> None:
    """A fully transparent plate: what a layer OVER a real `bg_00` must be.

    Not "no file": the layer scene's `ExtResource` names this path and a
    dangling texture is a load error, and `BackgroundAssets` counts the groups
    in the `layers` directory to keep a dressing's rng draw equal to the base
    zone's. So the plate exists, is the right size, and draws nothing.
    """
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, (0, 0, 0, 0)).save(path, "PNG")


def _layer_stops(nation: Nation, depth: float) -> tuple[tuple[int, int, int],
                                                        tuple[int, int, int]]:
    """A layer's two stops, darkened with depth.

    `depth` runs 0 (the far plate, `bg_00`) to 1 (the foreground). Nearer
    layers are darker and slightly less saturated toward the nation's ground
    colour, which is the only thing that makes five flat gradients read as five
    planes rather than as one.
    """
    factor = 1.0 - 0.45 * depth
    top = _scale(_mix(nation.sky, nation.ground, 0.15 + 0.35 * depth), factor)
    bottom = _scale(_mix(nation.ground, nation.sky, 0.10), factor)
    return top, bottom


# --------------------------------------------------------------------------
# the scenes
# --------------------------------------------------------------------------

def _layer_scene(nation: Nation, texture_res: str) -> str:
    """One background layer: a `TextureRect` at the base game's own rect.

    Instantiated by `NCombatBackground.AddLayer` as a plain `Control`
    (`NCombatBackground.cs:82`), so it carries NO script and needs no
    conversion -- unlike the background root beside it.
    """
    left, top = -LAYER_RECT[0] / 2, -LAYER_RECT[1] / 2
    return f"""[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="{texture_res}" id="1_tex"]

[node name="A" type="TextureRect"]
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = {left}
offset_top = {top}
offset_right = {-left}
offset_bottom = {-top}
grow_horizontal = 2
grow_vertical = 2
texture = ExtResource("1_tex")
expand_mode = 1
"""


def _background_scene(nation: Nation) -> str:
    """The background ROOT, and the one scene in this set that is converted.

    `NCombatBackground.Create` does `GetScene(path).Instantiate<NCombatBackground>()`
    -- it CASTS, it does not adapt -- and `NCombatBackground`'s script lives in
    the game's own pack at `res://src/Core/Nodes/Rooms/NCombatBackground.cs`,
    which a mod pck cannot reference (a scene source with an
    `ext_resource type="Script"` row is `SD-SCRIPT`, and the export would carry
    a dependency the scratch project cannot resolve). So the root here is a
    plain `Control` and `KleeCode/Teyvat/NCombatBackgroundFactory.cs` teaches
    BaseLib to convert it, exactly as `TeyvatVisuals` already does for the
    still portrait -- the same EB-760 mechanism, a second type.

    The children are the contract with `NCombatBackground.AddLayer`, which
    does `GetNodeOrNull("Layer_00")` .. `GetNodeOrNull($"Layer_{{i:D2}}")` for
    each chosen bg layer and `GetNodeOrNull("Foreground")` for the fg, and
    THROWS on a miss. Five plus one, matching `BG_GROUPS`.
    """
    layers = "\n".join(
        f'[node name="Layer_{n:02d}" type="Control" parent="."]\nanchors_preset = 0\n'
        for n in range(BG_GROUPS)
    )
    return f"""[gd_scene load_steps=1 format=3]

[node name="{nation.entry.capitalize()}Background" type="Control"]
layout_mode = 3
anchors_preset = 0

{layers}
[node name="Foreground" type="Control" parent="."]
anchors_preset = 0
"""


def scene_sources() -> dict[str, str]:
    """Every committed `.tscn`, repo-relative path -> exact text.

    Separated from the PNG half so `--check` can compare the committed files
    without needing Pillow or the gitignored ImageGen tree.
    """
    out: dict[str, str] = {}
    for nation in NATIONS:
        i = nation.id
        for group in range(BG_GROUPS):
            out[f"klee-mod/pck-src/scenes/backgrounds/{i}/layers/"
                f"{i}_bg_{group:02d}_{BG_VARIANT}.tscn"] = _layer_scene(
                    nation, f"res://teyvat/backgrounds/{i}/{i}_bg_{group:02d}.png")
        out[f"klee-mod/pck-src/scenes/backgrounds/{i}/layers/"
            f"{i}_fg_{FG_VARIANT}.tscn"] = _layer_scene(
                nation, f"res://teyvat/backgrounds/{i}/{i}_fg.png")
        out[f"klee-mod/pck-src/scenes/backgrounds/{i}/"
            f"{i}_background.tscn"] = _background_scene(nation)
    return out


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def write_all(root: Path) -> list[str]:
    written: list[str] = []
    for relative, text in sorted(scene_sources().items()):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        # LF, explicitly: a `.tscn` is a Godot text resource and the rest of
        # pck-src is LF. Newline is stated rather than defaulted so a Windows
        # run cannot rewrite every committed scene with CRLF and show sixteen
        # files as modified.
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written.append(relative)

    owned = plan_owned()
    for nation in NATIONS:
        i = nation.id
        # A dressing whose bg_00 comes from the bill has a real landscape on
        # the far plate, so the four layers and the foreground over it stop
        # being gradients and become transparent -- see the module docstring.
        real_bg = (f"ImageGen/images/teyvat/backgrounds/{i}/{i}_bg_00.png"
                   in owned)
        for group in range(BG_GROUPS):
            relative = f"ImageGen/images/teyvat/backgrounds/{i}/{i}_bg_{group:02d}.png"
            if relative in owned:
                continue
            if real_bg:
                _write_clear_png(root / relative, LAYER_PNG)
            else:
                depth = group / max(1, BG_GROUPS)  # 0.0 .. 0.8
                top, bottom = _layer_stops(nation, depth)
                _write_png(root / relative, LAYER_PNG, top, bottom)
            written.append(relative)
        relative = f"ImageGen/images/teyvat/backgrounds/{i}/{i}_fg.png"
        if relative not in owned:
            if real_bg:
                _write_clear_png(root / relative, LAYER_PNG)
            else:
                top, bottom = _layer_stops(nation, 1.0)
                _write_png(root / relative, LAYER_PNG, top, bottom)
            written.append(relative)

        relative = f"ImageGen/images/teyvat/rest_site/{i}_rest_site_bg.png"
        if relative not in owned:
            _write_png(root / relative, REST_PNG,
                       _scale(_mix(nation.sky, nation.ground, 0.55), 0.45),
                       _scale(nation.ground, 0.35))
            written.append(relative)

        # The three map plates read top -> bottom as one continuous wall, so
        # each takes a third of the nation's ramp rather than the whole of it.
        for index, slot in enumerate(("top", "middle", "bottom")):
            relative = f"ImageGen/images/teyvat/map_bgs/{i}/map_{slot}_{i}.png"
            if relative in owned:
                continue
            a = _mix(nation.sky, nation.ground, index / 3)
            b = _mix(nation.sky, nation.ground, (index + 1) / 3)
            _write_png(root / relative, MAP_PNG, a, b)
            written.append(relative)
    return written


def check(root: Path) -> list[str]:
    problems: list[str] = []
    for relative, text in sorted(scene_sources().items()):
        path = root / relative
        if not path.exists():
            problems.append(f"missing committed scene source {relative}")
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            actual = handle.read().replace("\r\n", "\n")
        if actual != text:
            problems.append(
                f"{relative} differs from what tools/gen_act_placeholders.py "
                "would write; re-run the generator or move the change into it")
    owned = plan_owned()
    for row in plan():
        if row.kind != "png" or row.repo in owned:
            # A plan-owned plate is art_process's to write and art_process's
            # to be missing; asking for it here would make this gate fail on
            # any checkout that has not run the art pass, and would make it
            # fail for a reason this file cannot fix.
            continue
        if not (root / row.repo).exists():
            problems.append(
                f"missing placeholder texture {row.repo} (gitignored; run the "
                "generator on the art-bearing checkout)")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="write nothing; report drift and missing files")
    parser.add_argument("--list", action="store_true",
                        help="print the planned res:// rows, one per line")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    root = Path(args.root)

    if args.list:
        for row in plan():
            print(row.res)
        return 0

    if args.check:
        problems = check(root)
        for problem in problems:
            print(problem)
        print(f"{len(plan())} planned file(s); {len(problems)} problem(s).")
        return 1 if problems else 0

    written = write_all(root)
    scenes = sum(1 for w in written if w.endswith(".tscn"))
    print(f"Wrote {len(written)} file(s): {scenes} committed scene source(s) "
          f"under klee-mod/pck-src/scenes, {len(written) - scenes} gitignored "
          f"texture(s) under ImageGen/images/teyvat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
