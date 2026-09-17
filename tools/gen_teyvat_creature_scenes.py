#!/usr/bin/env python3
"""Generate the Teyvat arm's STILL ENEMY BODIES from one table (`EB-811`).

WHAT THIS IS
------------
`docs/current/dossiers/content/enemy-dressings.tsv` is the one table. Each row
says: which Genshin BODY (a 240x280 RGBA plate), on which FACE, dresses which
base-game `MonsterModel.Id.Entry`, under which DISPLAY NAME, at which SIZE
CLASS. From it this generator writes two things and nothing else:

  * `klee-mod/pck-src/teyvat/creature_visuals/<body>.tscn` -- one committed
    scene per body, cloned from the shape `EB-760` proved with Nibbit's
    `hilichurl_guard.tscn`: a script-less `Node2D` carrying `%Visuals` (a
    `Node2D` holding one `Sprite2D`), `%Bounds`, `%IntentPos` and `%CenterPos`,
    which `TeyvatVisuals.RegisterStillPortraits` hands to BaseLib's
    auto-conversion so `MonsterModel.CreateVisuals`'s cast to
    `NCreatureVisuals` succeeds. The four nodes are the ones
    `NCreatureVisuals._Ready` fetches with `GetNode` rather than
    `GetNodeOrNull`, so all four are mandatory and none may be renamed.

  * `klee-mod/KleeCode/Teyvat/TeyvatCreaturesGenerated.cs` -- the two C# tables
    `TeyvatFrame` exposes: `StillPortraits`, keyed `(dressing, Id.Entry)` ->
    `res://` scene path, and `MonsterNames`, keyed `(dressing, "<ENTRY>.name")`
    -> the dressed string. ONE table feeds both, which is the point of the row:
    a body cannot get its picture without also getting its name, and it cannot
    get its name without also getting its picture. This is the codegen pattern
    `tools/gen_teyvat_events.py` / `TeyvatEventsGenerated.cs` already ride.

THE PIXELS ARE NOT HERE. A plate is Tier F and gitignored: it is produced into
`ImageGen/images/teyvat/creature_visuals/<body>.png` by `art/plan.tsv` and
recorded in `media/PORTRAITS.tsv`, and `tools/build_pck.ps1`'s Teyvat block
copies the directory to `res://teyvat/creature_visuals/`. `--check` therefore
never needs the art tree: it compares the COMMITTED scenes and the generated
C# against what this file would write, and says so when a plate is missing
rather than failing on it.

SIZING, AND WHERE THE THREE NUMBERS COME FROM
---------------------------------------------
A 240x280 plate drawn at scale 1 is a small body. The base game's own
`%Bounds` heights, read out of `SlayTheSpire2.pck`'s
`scenes/creature_visuals/*.tscn` for the 52 entries this table dresses, are:

    regular  n=32   median 244.5   (nibbit 146 ... ovicopter 476)
    elite    n=13   median 358     (decimillipede_segment_front 299 ... bygone_effigy 600)
    boss     n=7    median 440     (test_subject 292 ... knowledge_demon 642)

So the scales are the plate height that lands on each median:

    regular 1.0  -> 280 tall   (above the 244.5 median, and the one scale that
                                draws the plate pixel-exact, with no resample)
    elite   1.3  -> 364 tall   (median 358)
    boss    1.6  -> 448 tall   (median 440)

`%Bounds`, `%IntentPos` and `%CenterPos` all move with the scale, because the
engine reads them for the health bar, the block badge, the selection reticle,
the intent marker and every hit VFX: a plate that grew while its bounds did not
would put the intent inside the body and the HP bar across its waist.

`Visuals.Scale` IS NOT WRITTEN. `NCreature` owns it -- `ScaleTo`,
`SetDefaultScaleTo` and `OstyScaleToSize` write it and `UpdateBounds` reads it
back -- so the scale goes on the `Sprite2D` we own, under `%Visuals`, and
`%Visuals` itself stays an identity `Node2D` (memory: `sts2-creature-visual-
invariants`, item 2). There is likewise no facing to set: the game has no flip
concept and every body draws facing right (item 1).

Usage
-----
    .venv\\Scripts\\python.exe tools\\gen_teyvat_creature_scenes.py
    .venv\\Scripts\\python.exe tools\\gen_teyvat_creature_scenes.py --check
    .venv\\Scripts\\python.exe tools\\gen_teyvat_creature_scenes.py --list

`--check` writes nothing and exits non-zero on any drift; that is the staleness
gate `tier0/tests/test_teyvat_creature_scenes.py` rides, on
`tools/gen_act_placeholders.py`'s precedent.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TABLE = ROOT / "docs" / "current" / "dossiers" / "content" / "enemy-dressings.tsv"
SCENE_DIR = ROOT / "klee-mod" / "pck-src" / "teyvat" / "creature_visuals"
GENERATED_CS = ROOT / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatCreaturesGenerated.cs"
ART_DIR = ROOT / "ImageGen" / "images" / "teyvat" / "creature_visuals"

#: The pck namespace the scenes and their plates land in. `res://teyvat/` and
#: not `res://klee/`: a dressed enemy body belongs to the FRAME, not to one
#: character (`klee-mod/pck-src/teyvat/README.md`).
RES_ROOT = "res://teyvat/creature_visuals"

#: The plate every row is cut to, and the size `operations/media.md` sec.3
#: fixes for a portrait.
PLATE_W = 240
PLATE_H = 280

#: Scale by size class; the derivation is in the module docstring.
SCALES = {"regular": 1.0, "elite": 1.3, "boss": 1.6}

#: Pixels the intent marker floats above the top of the bounds box. The one
#: number carried over unchanged from the hand-written Nibbit scene, where the
#: box topped out at -280 and `%IntentPos` sat at -300.
INTENT_CLEARANCE = 20

#: The six faces, in act order. A row naming anything else is a table defect
#: rather than something to generate, because `TeyvatFrame` holds these six as
#: constants and a seventh would compile to nothing.
FACES = ("MONDSTADT", "LIYUE", "NATLAN", "INAZUMA", "FONTAINE", "SUMERU")


@dataclass(frozen=True)
class Row:
    """One line of the table."""

    body: str
    face: str
    base_entry: str
    display_name: str
    size_class: str
    notes: str

    @property
    def live(self) -> bool:
        """Does this row reach the C# tables?

        A row with an empty `base_entry` is a KEPT PLATE WITH NO MONSTER to
        hang on -- an Ancient (an `AncientEventModel`, which has no
        `creature_visuals` scene at all), or the second, third and fourth
        member of a group that the engine models as ONE `Id.Entry`. It still
        earns its scene, so the plate is packaged and one row is all it takes
        to place it later; it just cannot key a dictionary today.
        """
        return bool(self.base_entry)

    @property
    def scale(self) -> float:
        return SCALES[self.size_class]

    @property
    def scene(self) -> str:
        return f"{RES_ROOT}/{self.body}.tscn"


def load(path: Path = TABLE) -> list[Row]:
    """The table, validated. Every failure here is a table defect."""
    with path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.DictReader(handle, delimiter="\t"))

    rows: list[Row] = []
    for line, record in enumerate(raw, start=2):
        row = Row(
            body=(record.get("body") or "").strip(),
            face=(record.get("face") or "").strip(),
            base_entry=(record.get("base_entry") or "").strip(),
            display_name=(record.get("display_name") or "").strip(),
            size_class=(record.get("size_class") or "").strip(),
            notes=(record.get("notes") or "").strip(),
        )
        where = f"{path.name}:{line}"
        if not row.body:
            raise ValueError(f"{where}: empty body")
        if row.face not in FACES:
            raise ValueError(f"{where}: {row.face!r} is not one of {FACES}")
        if row.size_class not in SCALES:
            raise ValueError(f"{where}: {row.size_class!r} is not a size class")
        if not row.display_name:
            raise ValueError(f"{where}: {row.body} has no display_name")
        rows.append(row)

    # One picture and one name per (face, entry), or the dictionary
    # initialiser below throws at runtime instead of here.
    seen: dict[tuple[str, str], str] = {}
    for row in rows:
        if not row.live:
            continue
        key = (row.face, row.base_entry)
        if key in seen:
            raise ValueError(
                f"{path.name}: {row.face}/{row.base_entry} is claimed twice, by "
                f"{seen[key]} and {row.body}; one Id.Entry draws one body")
        seen[key] = row.body

    # A body's size class and name are the body's, not the row's: two rows for
    # one plate that disagreed would write two different scenes to one path.
    for field in ("size_class", "display_name"):
        by_body: dict[str, str] = {}
        for row in rows:
            value = getattr(row, field)
            if by_body.setdefault(row.body, value) != value:
                raise ValueError(
                    f"{path.name}: {row.body} has two values for {field} "
                    f"({by_body[row.body]!r} and {value!r})")
    return rows


def bodies(rows: list[Row]) -> dict[str, Row]:
    """One representative row per body, in first-seen order."""
    out: dict[str, Row] = {}
    for row in rows:
        out.setdefault(row.body, row)
    return out


def _node_name(body: str) -> str:
    """`wooden_shield_hilichurl_guard` -> `WoodenShieldHilichurlGuardVisuals`.

    The root's name is cosmetic -- the conversion reparents every child onto a
    fresh `NCreatureVisuals` and nothing looks the root up by name -- but a
    remote scene tree with seventy-seven nodes called `Node2D` is unreadable,
    which is the whole reason the hand-written one was called
    `HilichurlGuardVisuals`.
    """
    return "".join(part.capitalize() for part in body.split("_")) + "Visuals"


def _f(value: float) -> str:
    """A Godot float literal: integral values keep their `.0`."""
    text = f"{value:.6f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


def scene_source(row: Row) -> str:
    """The `.tscn` text for one body.

    Read it against `NCreatureVisuals._Ready` and `NCreatureVisualsFactory`:
    the factory keeps the four named nodes this scene carries and generates
    only `%FormVfx`; `%OrbPos`, `%TalkPos` and `%PhobiaModeVisuals` fall
    through its switch and stay absent, which `_Ready` tolerates (`%OrbPos`
    falls back to `%IntentPos`). NO SCRIPT, per `pck-src/README.md`'s standing
    rule: behaviour attaches from C#, never from an `ext_resource type="Script"`
    line -- and here it is load-bearing as well as a rule, because a scripted
    root would be the wrong type for the cast this whole mechanism turns on.
    """
    scale = row.scale
    half_w = PLATE_W / 2 * scale
    height = PLATE_H * scale
    feet_to_middle = -height / 2
    ident = row.body.split("_")[0][:5] or "plate"
    # NO COMMENT HEADER, deliberately. A `.tscn` is a Godot text resource, not
    # a `.cfg`: neither the base game's 127 `creature_visuals` scenes nor any
    # scene already committed under `pck-src/` carries a `;` or `#` line, and a
    # scene that fails to parse does not error loudly -- `CreateVisuals` swaps
    # in the pink fallback body, which "works" and looks like a bug. The
    # provenance lives in `pck-src/teyvat/README.md` and the staleness gate
    # lives in `--check`, neither of which has to survive a parser.
    return f"""[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="{RES_ROOT}/{row.body}.png" id="1_{ident}"]

[node name="{_node_name(row.body)}" type="Node2D"]

[node name="Visuals" type="Node2D" parent="."]
unique_name_in_owner = true

[node name="Body" type="Sprite2D" parent="Visuals"]
position = Vector2(0, {_f(feet_to_middle)})
scale = Vector2({_f(scale)}, {_f(scale)})
texture = ExtResource("1_{ident}")

[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = {_f(-half_w)}
offset_top = {_f(-height)}
offset_right = {_f(half_w)}
offset_bottom = 0.0
mouse_filter = 2

[node name="IntentPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, {_f(-height - INTENT_CLEARANCE)})

[node name="CenterPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, {_f(feet_to_middle)})
"""


def scene_sources(rows: list[Row]) -> dict[str, str]:
    """Every committed `.tscn`, repo-relative path -> exact text."""
    return {
        f"klee-mod/pck-src/teyvat/creature_visuals/{body}.tscn": scene_source(row)
        for body, row in sorted(bodies(rows).items())
    }


def _cs_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def generated_cs(rows: list[Row]) -> str:
    """`TeyvatCreaturesGenerated.cs`."""
    live = [r for r in rows if r.live]
    order = {face: i for i, face in enumerate(FACES)}
    live.sort(key=lambda r: (order[r.face], r.base_entry))

    portrait_lines: list[str] = []
    name_lines: list[str] = []
    face = None
    for row in live:
        if row.face != face:
            face = row.face
            portrait_lines.append(f"            // {face}")
            name_lines.append(f"            // {face}")
        portrait_lines.append(
            f"            [(TeyvatFrame.{face.capitalize()}, "
            f"{_cs_string(row.base_entry)})] =")
        portrait_lines.append(f"                {_cs_string(row.scene)},")
        name_lines.append(
            f"            [(TeyvatFrame.{face.capitalize()}, "
            f"{_cs_string(row.base_entry + '.name')})] =")
        name_lines.append(f"                {_cs_string(row.display_name)},")
    portraits = "\n".join(portrait_lines)
    names = "\n".join(name_lines)

    plates = len(bodies(rows))
    scene_only = sorted({r.body for r in rows} - {r.body for r in live})
    scene_only_note = "\n".join(
        f"///   * {b}" for b in scene_only) or "///   * (none)"

    return f"""// <auto-generated>
//     GENERATED by tools/gen_teyvat_creature_scenes.py from
//     docs/current/dossiers/content/enemy-dressings.tsv
//     Do not edit by hand: `python tools/gen_teyvat_creature_scenes.py --check`
//     fails on any drift, and the next run overwrites it.
// </auto-generated>

using System.Collections.Generic;

namespace KleeMod.Teyvat;

/// <summary>
/// THE DRESSED ENEMY BODIES, generated from the one table (`EB-811`).
///
/// A PICTURE AND A NAME ARE ONE ROW. `StillPortraits` is what
/// `Patches/MonsterVisualsPathPatch` swaps a `MonsterModel.VisualsPath` for,
/// and `MonsterNames` is what `Patches/MonsterNamePatch` and
/// `TeyvatLoc.Inject` turn into the dressed `monsters` loc rows. Both come out
/// of the same TSV line, so a body cannot reach the arena wearing its own
/// picture under the Spire's name, or the reverse -- which is exactly what
/// hand-maintaining two tables was going to cost.
///
/// {plates} plate(s) in the table; {len(live)} (face, Id.Entry) row(s) below.
/// A kept plate with no live row has a scene and a packaged texture but
/// nothing to key on -- an Ancient is an `AncientEventModel` and has no
/// `creature_visuals` scene at all, and a four-body elite is ONE `Id.Entry`,
/// so only one of its plates can draw. Today those are:
{scene_only_note}
///
/// EVERY ROW IS INERT WITHOUT THE ARM. `TeyvatFrame.CurrentActEntry` returns
/// null when `Enabled` is false, both patches return early on null, and
/// `TeyvatLoc.Inject` merges nothing -- so a release package's creature
/// visuals and loc tables are byte-identical to the base game's.
/// </summary>
internal static class TeyvatGeneratedCreatures
{{
    /// <summary>
    /// `(dressing, monster Id.Entry)` -> the pck scene that draws it.
    ///
    /// A row whose base enemy the face never rolls is INERT, not wrong: the
    /// lookup simply never fires. Act 1's two faces stand on two DIFFERENT
    /// base zones (Mondstadt on Overgrowth, Liyue on Underdocks), so a handful
    /// of act-1 rows are inert by construction; the table's `notes` column
    /// names each one.
    /// </summary>
    internal static readonly IReadOnlyDictionary<(string Dressing, string Entry), string> StillPortraits =
        new Dictionary<(string, string), string>
        {{
{portraits}
        }};

    /// <summary>
    /// `(dressing, monster loc key)` -> the dressed string. The key is what
    /// `MonsterModel.L10NMonsterLookup` is called with, which for a display
    /// name is `Id.Entry + ".name"`.
    /// </summary>
    internal static readonly IReadOnlyDictionary<(string Dressing, string Key), string> MonsterNames =
        new Dictionary<(string, string), string>
        {{
{names}
        }};
}}
"""


def write_all(root: Path, rows: list[Row]) -> list[str]:
    written: list[str] = []
    scene_dir = root / "klee-mod" / "pck-src" / "teyvat" / "creature_visuals"
    scene_dir.mkdir(parents=True, exist_ok=True)
    for relative, text in sorted(scene_sources(rows).items()):
        path = root / relative
        # LF, explicitly: `pck-src` is LF and a Windows run must not rewrite
        # seventy-seven committed scenes with CRLF.
        with (path).open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written.append(relative)

    cs = root / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatCreaturesGenerated.cs"
    with cs.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(generated_cs(rows))
    written.append(str(cs.relative_to(root)).replace("\\", "/"))
    return written


def stale_scenes(root: Path, rows: list[Row]) -> list[str]:
    """Committed scenes under our directory that the table no longer names."""
    directory = root / "klee-mod" / "pck-src" / "teyvat" / "creature_visuals"
    if not directory.is_dir():
        return []
    planned = {f"{body}.tscn" for body in bodies(rows)}
    return sorted(p.name for p in directory.glob("*.tscn") if p.name not in planned)


def check(root: Path, rows: list[Row]) -> list[str]:
    problems: list[str] = []
    for relative, text in sorted(scene_sources(rows).items()):
        path = root / relative
        if not path.exists():
            problems.append(f"missing committed scene {relative}")
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            actual = handle.read().replace("\r\n", "\n")
        if actual != text:
            problems.append(
                f"{relative} differs from what tools/gen_teyvat_creature_scenes.py "
                "would write; re-run the generator or move the change into it")

    cs = root / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatCreaturesGenerated.cs"
    if not cs.exists():
        problems.append("missing klee-mod/KleeCode/Teyvat/TeyvatCreaturesGenerated.cs")
    else:
        with cs.open("r", encoding="utf-8", newline="") as handle:
            actual = handle.read().replace("\r\n", "\n")
        if actual != generated_cs(rows):
            problems.append(
                "klee-mod/KleeCode/Teyvat/TeyvatCreaturesGenerated.cs is stale; "
                "re-run tools/gen_teyvat_creature_scenes.py")

    for name in stale_scenes(root, rows):
        problems.append(
            f"klee-mod/pck-src/teyvat/creature_visuals/{name} is not in the "
            "table; delete it or give it a row")
    return problems


def missing_plates(root: Path, rows: list[Row]) -> list[str]:
    """Bodies with no PNG on this checkout. Reported, never fatal.

    A worktree has no `ImageGen/images` at all (`operations/worktrees.md`), and
    the build itself only ever warns about a missing plate -- `build_pck.ps1`
    `Note-Skip`s the directory and both the path patch and the registrar ask
    `ResourceLoader.Exists` first -- so this is a report, not a gate.
    """
    directory = root / "ImageGen" / "images" / "teyvat" / "creature_visuals"
    if not directory.is_dir():
        return []
    return sorted(b for b in bodies(rows) if not (directory / f"{b}.png").exists())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="write nothing; report drift")
    parser.add_argument("--list", action="store_true",
                        help="print the planned res:// scene rows, one per line")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    root = Path(args.root)
    rows = load(root / "docs" / "current" / "dossiers" / "content"
                / "enemy-dressings.tsv")

    if args.list:
        for body in sorted(bodies(rows)):
            print(f"{RES_ROOT}/{body}.tscn")
        return 0

    if args.check:
        problems = check(root, rows)
        for problem in problems:
            print(problem)
        gaps = missing_plates(root, rows)
        if gaps:
            print(f"note: {len(gaps)} body/bodies have no plate on this "
                  f"checkout ({', '.join(gaps)})")
        print(f"{len(bodies(rows))} body/bodies, {len(rows)} table row(s); "
              f"{len(problems)} problem(s).")
        return 1 if problems else 0

    written = write_all(root, rows)
    live = sum(1 for r in rows if r.live)
    print(f"Wrote {len(written)} file(s): {len(written) - 1} scene(s) under "
          f"klee-mod/pck-src/teyvat/creature_visuals and the C# table "
          f"({live} live (face, Id.Entry) row(s)).")
    for name in stale_scenes(root, rows):
        print(f"stale: klee-mod/pck-src/teyvat/creature_visuals/{name} is not "
              "in the table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
