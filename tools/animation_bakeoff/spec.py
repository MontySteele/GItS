"""The synthetic rig and the required-motion suite -- ONE source for all four
approaches.

Two things live here and nowhere else:

* `PARTS` / `BONES` -- an original geometric figure ("Sprig"), described as
  primitives with rest offsets and a parent chain. No fetched or game art.
* `MOTIONS` -- the required-motion suite (idle / intent / attack / hurt /
  death) written in SEMANTIC channels, not in Godot node paths.

The semantic channel vocabulary is deliberately tiny, because every approach
has to be able to express it or admit that it cannot:

    offset  Vector2  translation away from the part's rest position
    spin    float    rotation in radians
    tint    Color    multiply colour (alpha carries fades)
    swell   Vector2  scale

`RIG` is the reserved part name for "the whole figure", matching the `Rig`
node the mod's shipped scenes animate (`klee-mod/pck-src/klee/model/
combat.tscn:401`).

State names are the shipped ones. `CreatureAnimationRouter` maps seven game
triggers onto exactly four states -- idle / attack / hurt / death
(`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:45-54`). `intent` is
REQUIRED BY THIS LANE'S CHARTER and has NO game trigger routed to it today;
it is built here as an authoring-cost sample and as the evidence for the
numbered question in the handoff, not as a claim that it should ship.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

RIG = "rig"

Shape = Literal["ellipse", "capsule", "roundrect", "diamond"]

#: `flag` is NOT part of the shared suite -- no motion below uses it. It exists
#: so an approach that has to author extra boolean tracks of its own (the
#: particle emitters) can render them through the same emitter, and so those
#: extra numbers land in that approach's source-burden column instead of
#: disappearing.
Channel = Literal["offset", "spin", "tint", "swell", "flag"]

# --------------------------------------------------------------------------
# The figure
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Part:
    """One drawn piece of the rig.

    `rest` is the part's position relative to the `Rig` node, in the same
    y-up-is-negative convention the shipped combat scenes use. `size` is the
    pixel footprint of the part's own PNG; `bone` names the Bone2D that drives
    it in the cutout and mesh approaches.
    """

    name: str
    shape: Shape
    size: tuple[int, int]
    rest: tuple[float, float]
    color: tuple[int, int, int, int]
    bone: str
    z: int  # draw order, low first


@dataclass(frozen=True)
class Bone:
    """One Bone2D in the cutout/mesh skeleton."""

    name: str
    parent: str | None
    rest: tuple[float, float]  # position relative to the parent bone
    length: float


# Palette: four flat values plus one accent. Chosen to be obviously synthetic
# (nothing here is a character colour) and to keep the parts distinguishable in
# a greyscale contact sheet.
_INK = (58, 62, 78, 255)
_MID = (96, 104, 128, 255)
_LIT = (168, 178, 204, 255)
_ACCENT = (232, 176, 84, 255)
_SHADE = (0, 0, 0, 90)

PARTS: tuple[Part, ...] = (
    Part("shadow", "ellipse", (96, 22), (0.0, 96.0), _SHADE, "root", 0),
    Part("leg_back", "capsule", (22, 54), (-14.0, 66.0), _INK, "leg_back", 1),
    Part("arm_back", "capsule", (18, 50), (-34.0, 6.0), _INK, "arm_back", 2),
    Part("leg_front", "capsule", (22, 54), (14.0, 66.0), _MID, "leg_front", 3),
    Part("torso", "roundrect", (64, 76), (0.0, 20.0), _MID, "spine", 4),
    Part("head", "ellipse", (56, 56), (0.0, -34.0), _LIT, "neck", 5),
    Part("arm_front", "capsule", (18, 50), (34.0, 6.0), _MID, "arm_front", 6),
    Part("prop", "diamond", (34, 34), (46.0, 28.0), _ACCENT, "prop", 7),
)

# Bone rests are PARENT-RELATIVE. The chain is root -> hip -> spine -> neck
# with four limbs off it; `prop` hangs off the front arm so the tell and the
# lunge move the held object without a second track.
BONES: tuple[Bone, ...] = (
    Bone("root", None, (0.0, 96.0), 40.0),
    Bone("hip", "root", (0.0, -30.0), 36.0),
    Bone("spine", "hip", (0.0, -46.0), 54.0),
    Bone("neck", "spine", (0.0, -54.0), 28.0),
    Bone("leg_back", "hip", (-14.0, 6.0), 54.0),
    Bone("leg_front", "hip", (14.0, 6.0), 54.0),
    Bone("arm_back", "spine", (-34.0, -14.0), 50.0),
    Bone("arm_front", "spine", (34.0, -14.0), 50.0),
    Bone("prop", "arm_front", (12.0, 22.0), 24.0),
)

PART_BY_NAME = {p.name: p for p in PARTS}
BONE_BY_NAME = {b.name: b for b in BONES}


def bone_chain(name: str) -> list[str]:
    """Root-first list of bone names from the skeleton root down to `name`."""
    chain: list[str] = []
    cur: str | None = name
    while cur is not None:
        chain.append(cur)
        cur = BONE_BY_NAME[cur].parent
    chain.reverse()
    return chain


# --------------------------------------------------------------------------
# The motion suite
# --------------------------------------------------------------------------

Key = tuple[float, object]


@dataclass(frozen=True)
class Track:
    """One semantic channel of one part over time.

    `interp` is Godot's track interpolation enum: 0 nearest, 1 linear,
    2 cubic. `transitions` is the per-key easing curve Godot stores alongside
    the times; it is omitted (all 1.0) unless a motion actually shapes it.
    """

    part: str
    channel: Channel
    keys: tuple[Key, ...]
    interp: int = 1
    transitions: tuple[float, ...] | None = None

    @property
    def times(self) -> tuple[float, ...]:
        return tuple(t for t, _ in self.keys)

    @property
    def values(self) -> tuple[object, ...]:
        return tuple(v for _, v in self.keys)


@dataclass(frozen=True)
class Motion:
    name: str
    length: float
    loop: bool
    tracks: tuple[Track, ...] = field(default_factory=tuple)


WHITE = (1.0, 1.0, 1.0, 1.0)
CLEAR = (1.0, 1.0, 1.0, 0.0)
HURT_RED = (1.0, 0.45, 0.4, 1.0)
CHARGED = (1.0, 0.93, 0.72, 1.0)

# Rest values per channel. RESET is DERIVED from the union of every track
# below (see `reset_motion`), so a new track cannot leave a stale property
# behind -- the failure mode that a hand-written RESET always eventually has.
REST_VALUE: dict[Channel, object] = {
    "offset": (0.0, 0.0),
    "spin": 0.0,
    "tint": WHITE,
    "swell": (1.0, 1.0),
}


IDLE = Motion(
    "idle",
    2.4,
    True,
    (
        Track("torso", "offset", ((0.0, (0.0, 0.0)), (1.2, (0.0, -3.0)), (2.4, (0.0, 0.0))), interp=2),
        Track("head", "offset", ((0.0, (0.0, 0.0)), (1.2, (0.0, -4.0)), (2.4, (0.0, 0.0))), interp=2),
        Track("head", "spin", ((0.0, 0.0), (0.6, 0.04), (1.2, 0.0), (1.8, -0.04), (2.4, 0.0)), interp=2),
        Track("arm_front", "spin", ((0.0, 0.0), (1.2, -0.09), (2.4, 0.0)), interp=2),
        Track("arm_back", "spin", ((0.0, 0.0), (1.2, 0.07), (2.4, 0.0)), interp=2),
        Track("prop", "offset", ((0.0, (0.0, 0.0)), (1.2, (0.0, -5.0)), (2.4, (0.0, 0.0))), interp=2),
        Track("shadow", "swell", ((0.0, (1.0, 1.0)), (1.2, (0.94, 1.0)), (2.4, (1.0, 1.0))), interp=2),
    ),
)

# The tell. Loops so a queued intent can hold for an arbitrary number of
# frames without the state machine needing a duration it cannot know.
INTENT = Motion(
    "intent",
    0.9,
    True,
    (
        Track("prop", "swell", ((0.0, (1.0, 1.0)), (0.45, (1.35, 1.35)), (0.9, (1.0, 1.0))), interp=2),
        Track("prop", "tint", ((0.0, WHITE), (0.45, CHARGED), (0.9, WHITE)), interp=2),
        Track("arm_front", "spin", ((0.0, 0.0), (0.3, -0.5), (0.9, -0.45)), interp=2),
        Track("head", "spin", ((0.0, 0.0), (0.3, 0.08), (0.9, 0.08)), interp=2),
        Track("torso", "offset", ((0.0, (0.0, 0.0)), (0.45, (-4.0, 0.0)), (0.9, (0.0, 0.0))), interp=2),
    ),
)

ATTACK = Motion(
    "attack",
    0.5,
    False,
    (
        Track(
            RIG,
            "offset",
            ((0.0, (0.0, 0.0)), (0.15, (42.0, 0.0)), (0.35, (-5.0, 0.0)), (0.5, (0.0, 0.0))),
            transitions=(0.5, 1.6, 1.0, 1.0),
        ),
        Track("arm_front", "spin", ((0.0, -0.45), (0.15, 0.9), (0.35, 0.2), (0.5, 0.0))),
        Track("torso", "spin", ((0.0, 0.0), (0.15, 0.12), (0.5, 0.0))),
        Track("prop", "offset", ((0.0, (0.0, 0.0)), (0.15, (30.0, -10.0)), (0.35, (0.0, 0.0)))),
        Track("prop", "tint", ((0.0, CHARGED), (0.2, CLEAR), (0.5, WHITE))),
    ),
)

HURT = Motion(
    "hurt",
    0.4,
    False,
    (
        Track(
            RIG,
            "offset",
            (
                (0.0, (0.0, 0.0)),
                (0.06, (-10.0, 0.0)),
                (0.14, (7.0, 0.0)),
                (0.22, (-4.0, 0.0)),
                (0.32, (2.0, 0.0)),
                (0.4, (0.0, 0.0)),
            ),
        ),
        Track("torso", "tint", ((0.0, WHITE), (0.05, HURT_RED), (0.35, WHITE))),
        Track("head", "tint", ((0.0, WHITE), (0.05, HURT_RED), (0.35, WHITE))),
        Track("head", "spin", ((0.0, 0.0), (0.06, -0.15), (0.4, 0.0))),
    ),
)

DEATH = Motion(
    "death",
    1.0,
    False,
    (
        Track(RIG, "spin", ((0.0, 0.0), (0.35, -0.25), (1.0, -0.9)), interp=2),
        Track(RIG, "offset", ((0.0, (0.0, 0.0)), (0.35, (-4.0, 4.0)), (1.0, (-10.0, 26.0))), interp=2),
        Track(RIG, "tint", ((0.0, WHITE), (0.5, WHITE), (1.0, CLEAR))),
        Track("shadow", "tint", ((0.0, WHITE), (0.5, CLEAR))),
        Track("prop", "offset", ((0.0, (0.0, 0.0)), (0.5, (-24.0, 18.0)), (1.0, (-40.0, 40.0))), interp=2),
        Track("prop", "spin", ((0.0, 0.0), (1.0, 2.2))),
    ),
)

MOTIONS: tuple[Motion, ...] = (IDLE, INTENT, ATTACK, HURT, DEATH)

#: The five motions this lane's charter requires, in the order it names them.
REQUIRED_MOTIONS: tuple[str, ...] = ("idle", "intent", "attack", "hurt", "death")

#: States the shipped router can reach today
#: (`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:45-54`).
ROUTED_STATES: tuple[str, ...] = ("idle", "attack", "hurt", "death")


def reset_motion() -> Motion:
    """Derive RESET from the union of every (part, channel) any motion touches.

    A hand-written RESET is a list that goes stale the first time somebody adds
    a track; deriving it means the stale case cannot exist. Ordering is stable
    (motion order, then track order) so re-generation is byte-identical.
    """
    seen: list[tuple[str, Channel]] = []
    for motion in MOTIONS:
        for track in motion.tracks:
            key = (track.part, track.channel)
            if key not in seen:
                seen.append(key)
    tracks = tuple(
        Track(part, channel, ((0.0, REST_VALUE[channel]),), interp=1) for part, channel in seen
    )
    return Motion("RESET", 0.001, False, tracks)


def all_motions() -> tuple[Motion, ...]:
    """RESET first, then the required suite in charter order."""
    return (reset_motion(),) + MOTIONS


def hand_authored_numbers() -> int:
    """Count every literal a human had to choose in the motion suite.

    Times, scalar values, vector components, colour components, transitions.
    This is the SOURCE BURDEN denominator: it is identical for all four
    approaches by construction, which is what makes the per-approach
    file/line/number counts in `measure.py` comparable at all.
    """
    total = 0
    for motion in MOTIONS:
        for track in motion.tracks:
            for time, value in track.keys:
                total += 1  # the time
                if isinstance(value, tuple):
                    total += len(value)
                else:
                    total += 1
            if track.transitions is not None:
                total += len(track.transitions)
    return total
