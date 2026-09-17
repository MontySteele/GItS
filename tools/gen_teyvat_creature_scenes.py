#!/usr/bin/env python3
"""Generate the Teyvat arm's STILL ENEMY BODIES from one table (`EB-811`).

WHAT THIS IS
------------
`docs/current/dossiers/content/enemy-dressings.tsv` is the one table. Each row
says: which Genshin BODY (a 240x280 RGBA plate), on which FACE, dresses which
base-game `MonsterModel.Id.Entry`, under which DISPLAY NAME, at which SIZE
CLASS, moving in which MOTION SET. From it this generator writes three things
and nothing else:

  * `klee-mod/pck-src/teyvat/creature_visuals/<body>.tscn` -- one committed
    scene per body (see "one plate, two sizes" below for the exception),
    cloned from the shape `EB-760` proved with Nibbit's
    `hilichurl_guard.tscn`: a script-less `Node2D` carrying `%Visuals` (a
    `Node2D` holding one `Sprite2D`), `%Bounds`, `%IntentPos` and `%CenterPos`,
    which `TeyvatVisuals.RegisterStillPortraits` hands to BaseLib's
    auto-conversion so `MonsterModel.CreateVisuals`'s cast to
    `NCreatureVisuals` succeeds. The four nodes are the ones
    `NCreatureVisuals._Ready` fetches with `GetNode` rather than
    `GetNodeOrNull`, so all four are mandatory and none may be renamed.
    Since the motion pass the scene also carries a `Rig` between `%Visuals`
    and the `Sprite2D`, plus `%AnimationPlayer` and `%AnimationTree` at the
    root -- the shape `Vfx/CreatureAnimationRouter` already drives.

  * `klee-mod/pck-src/teyvat/motion/<set>.tres` -- one AnimationLibrary per
    motion set, five clips each (`RESET`/`idle`/`attack`/`hurt`/`death`),
    shared by every scene whose row names that set. See "MOTION" below.

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

ONE PLATE, TWO SIZES. A size class belongs to the ROW, not to the plate: the
Golden Wolflord dresses Overgrowth's Ceremonial Beast (base `%Bounds` 560, a
boss) and Sumeru's Fabricator (331, a regular), and it is the same picture
either way. A scene fixes ONE scale, so such a body gets `<body>_<class>.tscn`
per class, both pointing at the same `<body>.png`. Every other body -- 121 of
the 122 today -- keeps its plain name. The MOTION column splits a body the same
way and for the same reason (`_assign_scene_ids`). `bodies()` answers "which
plates are packaged" and `scenes()` answers "which .tscn files exist"; they are
no longer the same question.

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
    .venv\\Scripts\\python.exe tools\\gen_teyvat_creature_scenes.py --motions

`--check` writes nothing and exits non-zero on any drift; that is the staleness
gate `tier0/tests/test_teyvat_creature_scenes.py` rides, on
`tools/gen_act_placeholders.py`'s precedent.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, replace
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

# ---------------------------------------------------------------------------
# MOTION -- pass one, five SHARED sets
# ---------------------------------------------------------------------------
#
# WHY A SET AND NOT A CLIP PER BODY. There are 123 scenes. Per-body motion is a
# per-body art decision and nobody has made 123 of them; what a still body
# actually needs first is to STOP BEING A STILL, and the cheapest honest way to
# get there is a small vocabulary of silhouette-level behaviours a row can
# choose from. Five sets cover the table's shapes -- something that stands,
# something that bounces, something that floats, something huge and slow, and
# something mechanical. A body that deserves its own clips can get its own set
# later without any of this moving: the column is per ROW and the library is
# per NAME.
#
# WHY THE LIBRARY IS AN EXTERNAL `.tres`. Inlining five clips in each of 123
# scenes would put the same ~200 lines of keyframes in the repo 25 times over,
# and a motion tweak would rewrite every scene. `AnimationPlayer.libraries`
# takes an `ExtResource` exactly as happily as a `SubResource`, so the clips
# live once at `res://teyvat/motion/<set>.tres` and the scenes reference them.
# `build_pck.ps1` overlays `klee-mod/pck-src` VERBATIM (`:1092-1098`) and the
# pck contract is DERIVED from that work directory after the copy, so a `.tres`
# packs and is contracted with no change to either.
#
# WHAT A CLIP MAY KEY, AND WHY THE LIST IS THIS SHORT.
#
#   * `%Visuals` is the ENGINE'S (`NCreature.ScaleTo`, `SetDefaultScaleTo`,
#     `OstyScaleToSize` write it, `UpdateBounds` reads it back), so nothing we
#     author may touch it -- memory `sts2-creature-visual-invariants` item 2,
#     and the same reason the size-class scale went on the `Sprite2D`.
#   * `Body` carries the SIZE CLASS: its `position` and `scale` are derived
#     from the row's class and are what makes an elite bigger than a regular.
#     A clip that keyed them would flatten every body to one size the moment it
#     played.
#
# That leaves exactly one node a clip may move -- an intermediate `Rig` between
# `%Visuals` and `Body`, which is Furina's own shape
# (`pck-src/furina/model/combat.tscn`: `%Visuals` -> `Facing` -> `Rig` ->
# sprites) -- plus `Body`'s modulate for the hit flash and the death fade,
# which is a colour and carries no geometry.
RIG_POSITION = "Visuals/Rig:position"
RIG_SCALE = "Visuals/Rig:scale"
RIG_ROTATION = "Visuals/Rig:rotation"
BODY_MODULATE = "Visuals/Rig/Body:modulate"

#: The four, as a set, for the pins. Anything else in a committed `.tres` is a
#: defect that would be silent in the game: a track on a node the scene does
#: not have simply never moves.
ALLOWED_TRACKS = (RIG_POSITION, RIG_SCALE, RIG_ROTATION, BODY_MODULATE)

#: The pck namespace the motion libraries land in.
MOTION_RES_ROOT = "res://teyvat/motion"

#: The four states `CreatureAnimationRouter.TriggerToState` travels to, plus
#: the RESET pose Godot writes. Every set carries all five or the router's
#: `Travel` is a silent no-op.
CLIP_NAMES = ("RESET", "idle", "attack", "hurt", "death")

#: WHITE, and the hit flash. Furina flashes blue because she is Hydro; a
#: dressed enemy has no element of its own on this pass, so the flash is the
#: game's own damage red, one value for every set.
WHITE = (1, 1, 1, 1)
FLASH = (1, 0.55, 0.55, 1)
FADED = (1, 1, 1, 0)

#: ENEMIES FACE LEFT. The player stands on the left of the arena and every
#: dressed plate is drawn facing right by the art pipeline, which the game
#: then places on the right-hand side -- so "toward the player" is NEGATIVE x
#: and a hit knocks a body back along POSITIVE x. Furina's own attack lunges
#: +38 for the mirror-image reason.
#: (Both directions are one sign here rather than scattered through the data.)


@dataclass(frozen=True)
class Track:
    """One value track: a node property, and the keys written on it."""

    path: str
    times: tuple[float, ...]
    values: tuple
    interp: int = 1
    transitions: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if self.path not in ALLOWED_TRACKS:
            raise ValueError(f"{self.path} is not one of {ALLOWED_TRACKS}")
        if len(self.times) != len(self.values):
            raise ValueError(f"{self.path}: {len(self.times)} times, "
                             f"{len(self.values)} values")


@dataclass(frozen=True)
class Clip:
    """One animation: a name, a length, whether it loops, and its tracks."""

    name: str
    length: float
    tracks: tuple[Track, ...]
    loop: bool = False


def _reset() -> Clip:
    """The RESET pose: `Rig` at identity and `Body` unmodulated.

    Godot writes this clip back over the scene whenever the editor or the
    player resets, and the state machine's Start node effectively begins from
    it. Every property any clip in the set touches must appear here, or a
    death fade would leave the next body it plays on half-transparent.
    """
    return Clip("RESET", 0.001, (
        Track(RIG_POSITION, (0,), ((0, 0),)),
        Track(RIG_SCALE, (0,), ((1, 1),)),
        Track(RIG_ROTATION, (0,), (0.0,)),
        Track(BODY_MODULATE, (0,), (WHITE,)),
    ))


def _flash(at: float = 0.05, back: float = 0.3) -> Track:
    """The hurt flash: white, red for a frame, white again."""
    return Track(BODY_MODULATE, (0, at, back), (WHITE, FLASH, WHITE))


#: The five sets. Amplitudes are in the spirit of Furina's shipped clips
#: (`pck-src/furina/model/combat.tscn`): an idle of a pixel or three, a lunge
#: of a few dozen, a hurt shake of about ten, a death of about a second.
MOTIONS: dict[str, tuple[Clip, ...]] = {
    # A body with feet. Weight shifts, leans into a swing, staggers, falls over.
    "stand": (
        _reset(),
        Clip("idle", 2.6, (
            Track(RIG_POSITION, (0, 1.3, 2.6), ((0, 0), (0, -2), (0, 0)), interp=2),
            Track(RIG_ROTATION, (0, 0.9, 1.8, 2.6), (0.0, 0.01, -0.01, 0.0), interp=2),
        ), loop=True),
        Clip("attack", 0.5, (
            Track(RIG_POSITION, (0, 0.14, 0.34, 0.5),
                  ((0, 0), (-35, -4), (6, 1), (0, 0)),
                  transitions=(0.5, 1.6, 1, 1)),
            Track(RIG_ROTATION, (0, 0.14, 0.34, 0.5), (0.0, 0.05, -0.02, 0.0)),
        )),
        Clip("hurt", 0.4, (
            Track(RIG_POSITION, (0, 0.06, 0.14, 0.22, 0.32, 0.4),
                  ((0, 0), (10, 0), (-6, 0), (4, 0), (-2, 0), (0, 0))),
            _flash(),
        )),
        Clip("death", 1.2, (
            Track(RIG_POSITION, (0, 0.2, 1.2), ((0, 0), (4, 2), (14, 26))),
            Track(RIG_ROTATION, (0, 0.2, 1.2), (0.0, 0.02, 0.15)),
            Track(BODY_MODULATE, (0, 0.2, 1.2), (WHITE, WHITE, FADED)),
        )),
    ),
    # Slimes, whelps, fungus. Squash and stretch; ends as a puddle.
    "bounce": (
        _reset(),
        Clip("idle", 1.0, (
            Track(RIG_SCALE, (0, 0.25, 0.5, 0.75, 1.0),
                  ((1, 1), (1.04, 0.97), (1, 1), (0.97, 1.04), (1, 1)), interp=2),
        ), loop=True),
        Clip("attack", 0.5, (
            Track(RIG_POSITION, (0, 0.12, 0.28, 0.4, 0.5),
                  ((0, 0), (0, -26), (-35, -10), (-8, 0), (0, 0))),
            Track(RIG_SCALE, (0, 0.12, 0.28, 0.5),
                  ((1, 1), (0.94, 1.08), (1.06, 0.95), (1, 1))),
        )),
        Clip("hurt", 0.4, (
            Track(RIG_POSITION, (0, 0.08, 0.2, 0.4), ((0, 0), (8, 0), (-4, 0), (0, 0))),
            Track(RIG_SCALE, (0, 0.08, 0.18, 0.28, 0.4),
                  ((1, 1), (1.12, 0.9), (0.92, 1.09), (1.05, 0.96), (1, 1))),
            _flash(),
        )),
        Clip("death", 1.2, (
            Track(RIG_SCALE, (0, 0.25, 1.2), ((1, 1), (1.4, 0.3), (1.4, 0.3))),
            Track(BODY_MODULATE, (0, 0.25, 1.2), (WHITE, WHITE, FADED)),
        )),
    ),
    # Specters, cicins, anything with no feet. Floats; darts; drops when killed.
    "hover": (
        _reset(),
        Clip("idle", 2.4, (
            Track(RIG_POSITION, (0, 1.2, 2.4), ((0, 0), (0, -4), (0, 0)), interp=2),
        ), loop=True),
        Clip("attack", 0.5, (
            Track(RIG_POSITION, (0, 0.1, 0.5), ((0, 0), (-35, -6), (0, 0)),
                  transitions=(2.0, 1, 0.45)),
            Track(RIG_ROTATION, (0, 0.1, 0.5), (0.0, 0.06, 0.0)),
        )),
        Clip("hurt", 0.4, (
            Track(RIG_POSITION, (0, 0.08, 0.2, 0.4), ((0, 0), (9, -2), (-4, 1), (0, 0))),
            Track(RIG_ROTATION, (0, 0.08, 0.18, 0.28, 0.4),
                  (0.0, 0.05, -0.05, 0.03, 0.0)),
            _flash(),
        )),
        Clip("death", 1.2, (
            Track(RIG_POSITION, (0, 1.2), ((0, 0), (0, 40))),
            Track(BODY_MODULATE, (0, 0.2, 1.2), (WHITE, WHITE, FADED)),
        )),
    ),
    # Bosses and the very large. Breathes; presses forward; barely notices a
    # hit; sinks rather than falls.
    "loom": (
        _reset(),
        Clip("idle", 3.5, (
            Track(RIG_SCALE, (0, 1.75, 3.5), ((1, 1), (1.015, 1.015), (1, 1)), interp=2),
        ), loop=True),
        Clip("attack", 0.7, (
            Track(RIG_POSITION, (0, 0.26, 0.46, 0.7),
                  ((0, 0), (-25, -3), (4, 2), (0, 0)),
                  transitions=(0.45, 1.5, 1, 1)),
            Track(RIG_ROTATION, (0, 0.26, 0.46, 0.7), (0.0, 0.04, -0.02, 0.0)),
        )),
        Clip("hurt", 0.4, (
            Track(RIG_POSITION, (0, 0.07, 0.16, 0.26, 0.4),
                  ((0, 0), (4, 0), (-3, 0), (2, 0), (0, 0))),
            _flash(),
        )),
        Clip("death", 1.6, (
            Track(RIG_POSITION, (0, 1.6), ((0, 0), (0, 20))),
            Track(RIG_ROTATION, (0, 1.6), (0.0, 0.06)),
            Track(BODY_MODULATE, (0, 0.3, 1.6), (WHITE, WHITE, FADED)),
        )),
    ),
    # Ruin machines and meks. NO BREATH -- the idle holds the pose, which is
    # the whole read: a thing that does not breathe is a thing that is not
    # alive. It still loops, so the tree has a state to rest in.
    "mech": (
        _reset(),
        Clip("idle", 1.0, (
            Track(RIG_POSITION, (0,), ((0, 0),)),
            Track(RIG_SCALE, (0,), ((1, 1),)),
            Track(RIG_ROTATION, (0,), (0.0,)),
            Track(BODY_MODULATE, (0,), (WHITE,)),
        ), loop=True),
        Clip("attack", 0.3, (
            Track(RIG_POSITION, (0, 0.08, 0.16, 0.3),
                  ((0, 0), (-30, 0), (-30, 0), (0, 0))),
        )),
        Clip("hurt", 0.4, (
            Track(RIG_POSITION, (0, 0.06, 0.12, 0.18, 0.26, 0.4),
                  ((0, 0), (3, 0), (-3, 0), (3, 0), (-2, 0), (0, 0))),
            _flash(),
        )),
        Clip("death", 1.2, (
            Track(RIG_POSITION, (0, 1.2), ((0, 0), (0, 6))),
            Track(BODY_MODULATE, (0, 0.35, 1.2),
                  (WHITE, (0.45, 0.45, 0.45, 1), (0.45, 0.45, 0.45, 0))),
        )),
    ),
}

#: The legal values of the table's `motion` column, in the order the sets are
#: written above.
MOTION_SETS = tuple(MOTIONS)


#: The rule that FILLED the column, kept so a row added tomorrow can be given a
#: motion the same way the 158 were. Order matters -- first match wins -- and
#: every clause is a substring test on the body name except the size-class arm.
#: It is a SUGGESTION and never a gate: the committed column is authoritative,
#: so vetoing one row is a one-cell edit and nothing here argues back.
MECH_WORDS = ("ruin", "mek", "construct", "automaton", "breacher", "algorithm",
              "matrix", "reshaper", "prospector", "repulsor", "enhancer")
BOUNCE_WORDS = ("slime", "whelp", "chick", "hare", "fungus", "shroom",
                "jaxfruit", "whopperflower", "crab", "beetle")
HOVER_WORDS = ("specter", "cicin", "jellyfish", "eye_of", "phantasm", "wayob",
               "seelie", "tulpa", "manifestation", "spirit", "ghost")
LOOM_WORDS = ("dragon", "serpent", "geovishap", "azhdaha", "narwhal", "whale",
              "regisvine", "lawachurl", "golem", "terrorshroom", "emperor",
              "lord")


def default_motion(body: str, size_class: str) -> str:
    """The motion the assignment rule gives one row."""
    name = body.lower()
    if any(word in name for word in MECH_WORDS):
        return "mech"
    if any(word in name for word in BOUNCE_WORDS):
        return "bounce"
    if any(word in name for word in HOVER_WORDS):
        return "hover"
    if size_class == "boss" or any(word in name for word in LOOM_WORDS):
        return "loom"
    return "stand"


@dataclass(frozen=True)
class Row:
    """One line of the table."""

    body: str
    face: str
    base_entry: str
    display_name: str
    size_class: str
    motion: str
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

    #: The scene this row draws through, WITHOUT the extension. Normally the
    #: body; a body that dresses a regular on one face and a boss on another
    #: gets one scene per class, because a scene is one plate at ONE scale.
    #: Assigned by `load`, which is the only thing that can see the whole
    #: table (a lone row cannot know whether its body is single-class).
    scene_id: str = ""

    @property
    def scene(self) -> str:
        return f"{RES_ROOT}/{self.scene_id or self.body}.tscn"

    @property
    def motion_library(self) -> str:
        return f"{MOTION_RES_ROOT}/{self.motion}.tres"


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
            motion=(record.get("motion") or "").strip(),
            notes=(record.get("notes") or "").strip(),
        )
        where = f"{path.name}:{line}"
        if not row.body:
            raise ValueError(f"{where}: empty body")
        if row.face not in FACES:
            raise ValueError(f"{where}: {row.face!r} is not one of {FACES}")
        if row.size_class not in SCALES:
            raise ValueError(f"{where}: {row.size_class!r} is not a size class")
        if row.motion not in MOTIONS:
            raise ValueError(
                f"{where}: {row.motion!r} is not a motion set {MOTION_SETS}")
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

    # A body's NAME is the body's, not the row's. Two rows calling one plate
    # two different things is a table defect however you look at it: the plate
    # is a picture of one creature.
    by_body: dict[str, str] = {}
    for row in rows:
        if by_body.setdefault(row.body, row.display_name) != row.display_name:
            raise ValueError(
                f"{path.name}: {row.body} has two display names "
                f"({by_body[row.body]!r} and {row.display_name!r})")

    return _assign_scene_ids(rows)


def _assign_scene_ids(rows: list[Row]) -> list[Row]:
    """Give every row the scene it draws through.

    A SIZE CLASS IS A PROPERTY OF THE ROW, NOT OF THE PLATE, and that is the
    one thing this pass exists for. The Golden Wolflord dresses Overgrowth's
    Ceremonial Beast (base `%Bounds` 560, a boss) and Sumeru's Fabricator (331,
    a regular); the Genshin body is the same picture either way, but a scene
    fixes ONE scale, so the two cannot share one `.tscn`.

    MOTION IS THE ROW'S TOO, and for the same reason: a scene names ONE motion
    library, so a plate that is a boss on one face and a regular on another may
    also want to loom on one and stand on the other. It splits the same way,
    and the suffix names only the axis that actually varies -- so a body whose
    two rows differ in class alone keeps `<body>_<class>` exactly as it reads
    today, a body that differs in motion alone gets `<body>_<motion>`, and one
    that differs in both gets `<body>_<class>_<motion>`. A body whose rows all
    agree keeps its plain name, which is every body but one today and keeps the
    whole directory readable.

    The texture is the same `<body>.png` in every variant, because it is the
    same plate: what differs is the sprite scale, the three markers derived
    from it, and which library the scene's `%AnimationPlayer` loads.
    """
    classes: dict[str, set[str]] = {}
    motions: dict[str, set[str]] = {}
    for row in rows:
        classes.setdefault(row.body, set()).add(row.size_class)
        motions.setdefault(row.body, set()).add(row.motion)

    out: list[Row] = []
    for row in rows:
        parts = [row.body]
        if len(classes[row.body]) > 1:
            parts.append(row.size_class)
        if len(motions[row.body]) > 1:
            parts.append(row.motion)
        out.append(replace(row, scene_id="_".join(parts)))
    return out


def bodies(rows: list[Row]) -> dict[str, Row]:
    """One representative row per body, in first-seen order.

    Keyed by BODY, so it answers "which plates does the table want packaged".
    `scenes` is the other question and they are no longer the same one.
    """
    out: dict[str, Row] = {}
    for row in rows:
        out.setdefault(row.body, row)
    return out


def scenes(rows: list[Row]) -> dict[str, Row]:
    """One representative row per SCENE, in first-seen order.

    Which `.tscn` files exist. Differs from `bodies` only for a body that
    carries more than one size class (`_assign_scene_ids`).
    """
    out: dict[str, Row] = {}
    for row in rows:
        out.setdefault(row.scene_id, row)
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


def _n(value: float) -> str:
    """A COMPACT Godot number, the way the editor writes keyframe data.

    `Vector2(0, -140)`, `1.04`, `-0.05` -- integral values lose the `.0` here,
    which is the opposite of `_f` and is deliberate: `_f` writes the scene's
    own transform literals in the shape the committed scenes already carry, and
    this writes animation keys in the shape `pck-src/furina/model/combat.tscn`
    carries. Matching each file's existing style keeps both diffs readable.
    """
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-", "-0") else text


def _value(value) -> str:
    """One keyframe value: a float, a `Vector2` or a `Color`."""
    if isinstance(value, tuple):
        if len(value) == 2:
            return f"Vector2({_n(value[0])}, {_n(value[1])})"
        if len(value) == 4:
            return "Color(" + ", ".join(_n(v) for v in value) + ")"
        raise ValueError(f"no Godot type for a {len(value)}-tuple")
    # A SCALAR keeps its `.0`. A rotation track's values are floats and Godot
    # writes them as floats; `0` would be an int literal in a float array.
    return _f(value)


def _track_source(index: int, track: Track) -> str:
    transitions = track.transitions or tuple(1 for _ in track.times)
    return (
        f'tracks/{index}/type = "value"\n'
        f"tracks/{index}/imported = false\n"
        f"tracks/{index}/enabled = true\n"
        f'tracks/{index}/path = NodePath("{track.path}")\n'
        f"tracks/{index}/interp = {track.interp}\n"
        f"tracks/{index}/loop_wrap = true\n"
        f"tracks/{index}/keys = {{\n"
        f'"times": PackedFloat32Array({", ".join(_n(t) for t in track.times)}),\n'
        f'"transitions": PackedFloat32Array({", ".join(_n(t) for t in transitions)}),\n'
        f'"update": 0,\n'
        f'"values": [{", ".join(_value(v) for v in track.values)}]\n'
        f"}}\n"
    )


def _clip_source(clip: Clip) -> str:
    head = f'[sub_resource type="Animation" id="Animation_{clip.name}"]\n'
    if clip.name != "RESET":
        head += f'resource_name = "{clip.name}"\n'
    head += f"length = {_f(clip.length)}\n"
    if clip.loop:
        head += "loop_mode = 1\n"
    return head + "".join(
        _track_source(i, track) for i, track in enumerate(clip.tracks))


def motion_source(name: str) -> str:
    """The `.tres` text for one motion set.

    A plain `AnimationLibrary` resource: five `Animation` sub-resources and the
    `_data` dictionary that names them. NO COMMENT LINES, for the same reason
    the scenes carry none -- a resource that fails to parse does not error
    loudly, it just is not there.
    """
    clips = MOTIONS[name]
    body = "\n".join(_clip_source(clip) for clip in clips)
    data = ",\n".join(
        f'&"{clip.name}": SubResource("Animation_{clip.name}")'
        for clip in sorted(clips, key=lambda c: c.name))
    return (
        f'[gd_resource type="AnimationLibrary" load_steps={len(clips) + 1} '
        "format=3]\n\n"
        f"{body}\n"
        "[resource]\n"
        "_data = {\n"
        f"{data}\n"
        "}\n"
    )


def motion_sources() -> dict[str, str]:
    """Every committed motion library, repo-relative path -> exact text."""
    return {
        f"klee-mod/pck-src/teyvat/motion/{name}.tres": motion_source(name)
        for name in sorted(MOTIONS)
    }


#: The state machine every generated scene carries, verbatim from the one
#: `pck-src/furina/model/combat.tscn` ships and the router already drives:
#: Start auto-advances to idle, idle reaches attack / hurt / death on a
#: `Travel`, attack and hurt return to idle AT THE END OF THE CLIP
#: (`switch_mode = 2` is at-end, `advance_mode = 2` is auto), and death goes
#: only to End -- it never returns, which is what makes a corpse stay down.
#: `Travel` to the state you are already in is a no-op, so a repeated "Dead"
#: cannot restart the fall.
_STATE_MACHINE = '''[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_attack"]
animation = &"attack"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_death"]
animation = &"death"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_hurt"]
animation = &"hurt"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_idle"]
animation = &"idle"

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_start_idle"]
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_attack"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_attack_idle"]
switch_mode = 2
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_hurt"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_hurt_idle"]
switch_mode = 2
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_attack_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_hurt_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_death_end"]
switch_mode = 2
advance_mode = 0

[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_creature"]
states/End/position = Vector2(628, 153)
states/Start/position = Vector2(186, 153)
states/attack/node = SubResource("AnimationNodeAnimation_attack")
states/attack/position = Vector2(327, 64)
states/death/node = SubResource("AnimationNodeAnimation_death")
states/death/position = Vector2(470, 153)
states/hurt/node = SubResource("AnimationNodeAnimation_hurt")
states/hurt/position = Vector2(327, 278)
states/idle/node = SubResource("AnimationNodeAnimation_idle")
states/idle/position = Vector2(327, 153)
transitions = ["Start", "idle", SubResource("Transition_start_idle"), \
"idle", "attack", SubResource("Transition_idle_attack"), \
"attack", "idle", SubResource("Transition_attack_idle"), \
"idle", "hurt", SubResource("Transition_idle_hurt"), \
"hurt", "idle", SubResource("Transition_hurt_idle"), \
"idle", "death", SubResource("Transition_idle_death"), \
"attack", "death", SubResource("Transition_attack_death"), \
"hurt", "death", SubResource("Transition_hurt_death"), \
"death", "End", SubResource("Transition_death_end")]
'''

#: `ext` + `sub` + 1, which is what Godot writes and what the scene-deps gate
#: checks. Two ext (the plate and the motion library) and fourteen sub (four
#: `AnimationNodeAnimation`, nine transitions, one state machine).
_LOAD_STEPS = 2 + 14 + 1


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
    ident = row.scene_id.split("_")[0][:5] or "plate"
    # NO COMMENT HEADER, deliberately. A `.tscn` is a Godot text resource, not
    # a `.cfg`: neither the base game's 127 `creature_visuals` scenes nor any
    # scene already committed under `pck-src/` carries a `;` or `#` line, and a
    # scene that fails to parse does not error loudly -- `CreateVisuals` swaps
    # in the pink fallback body, which "works" and looks like a bug. The
    # provenance lives in `pck-src/teyvat/README.md` and the staleness gate
    # lives in `--check`, neither of which has to survive a parser.
    return f"""[gd_scene load_steps={_LOAD_STEPS} format=3]

[ext_resource type="Texture2D" path="{RES_ROOT}/{row.body}.png" id="1_{ident}"]
[ext_resource type="AnimationLibrary" path="{row.motion_library}" id="2_motion"]

{_STATE_MACHINE}
[node name="{_node_name(row.scene_id)}" type="Node2D"]

[node name="Visuals" type="Node2D" parent="."]
unique_name_in_owner = true

[node name="Rig" type="Node2D" parent="Visuals"]

[node name="Body" type="Sprite2D" parent="Visuals/Rig"]
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

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {{
&"": ExtResource("2_motion")
}}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_creature")
anim_player = NodePath("../AnimationPlayer")
"""


def scene_sources(rows: list[Row]) -> dict[str, str]:
    """Every committed `.tscn`, repo-relative path -> exact text."""
    return {
        f"klee-mod/pck-src/teyvat/creature_visuals/{name}.tscn": scene_source(row)
        for name, row in sorted(scenes(rows).items())
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

    motion_dir = root / "klee-mod" / "pck-src" / "teyvat" / "motion"
    motion_dir.mkdir(parents=True, exist_ok=True)
    for relative, text in sorted(motion_sources().items()):
        with (root / relative).open("w", encoding="utf-8", newline="\n") as handle:
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
    planned = {f"{name}.tscn" for name in scenes(rows)}
    return sorted(p.name for p in directory.glob("*.tscn") if p.name not in planned)


def stale_motion(root: Path) -> list[str]:
    """Committed `.tres` under the motion directory that no set names."""
    directory = root / "klee-mod" / "pck-src" / "teyvat" / "motion"
    if not directory.is_dir():
        return []
    planned = {f"{name}.tres" for name in MOTIONS}
    return sorted(p.name for p in directory.glob("*.tres") if p.name not in planned)


def check(root: Path, rows: list[Row]) -> list[str]:
    problems: list[str] = []
    for relative, text in sorted(
            {**scene_sources(rows), **motion_sources()}.items()):
        path = root / relative
        if not path.exists():
            problems.append(f"missing committed file {relative}")
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
    for name in stale_motion(root):
        problems.append(
            f"klee-mod/pck-src/teyvat/motion/{name} is not a motion set; "
            "delete it or add it to MOTIONS")
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
    parser.add_argument("--motions", action="store_true",
                        help="print `body<TAB>motion` for every body, plus the "
                             "count per set; the table a review reads")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    root = Path(args.root)
    rows = load(root / "docs" / "current" / "dossiers" / "content"
                / "enemy-dressings.tsv")

    if args.list:
        for name in sorted(scenes(rows)):
            print(f"{RES_ROOT}/{name}.tscn")
        return 0

    if args.motions:
        per_body: dict[str, set[str]] = {}
        for row in rows:
            per_body.setdefault(row.body, set()).add(row.motion)
        for body in sorted(per_body):
            print(f"{body}\t{'/'.join(sorted(per_body[body]))}")
        counts = {name: sum(1 for r in rows if r.motion == name)
                  for name in MOTION_SETS}
        print("")
        for name in MOTION_SETS:
            print(f"{name}\t{counts[name]} row(s)")
        return 0

    if args.check:
        problems = check(root, rows)
        for problem in problems:
            print(problem)
        gaps = missing_plates(root, rows)
        if gaps:
            print(f"note: {len(gaps)} body/bodies have no plate on this "
                  f"checkout ({', '.join(gaps)})")
        print(f"{len(bodies(rows))} plate(s), {len(scenes(rows))} scene(s), "
              f"{len(rows)} table row(s); {len(problems)} problem(s).")
        return 1 if problems else 0

    written = write_all(root, rows)
    live = sum(1 for r in rows if r.live)
    print(f"Wrote {len(written)} file(s): {len(scenes(rows))} scene(s) for "
          f"{len(bodies(rows))} plate(s) under "
          f"klee-mod/pck-src/teyvat/creature_visuals, {len(MOTIONS)} motion "
          f"library/libraries under klee-mod/pck-src/teyvat/motion, and the C# "
          f"table ({live} live (face, Id.Entry) row(s)).")
    for name in stale_scenes(root, rows):
        print(f"stale: klee-mod/pck-src/teyvat/creature_visuals/{name} is not "
              "in the table")
    for name in stale_motion(root):
        print(f"stale: klee-mod/pck-src/teyvat/motion/{name} is not a motion set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
