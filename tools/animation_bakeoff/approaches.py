"""The four approaches, each compiling the SAME semantic motion suite.

    layered    Sprite2D per part, value tracks straight onto node properties
    cutout     Skeleton2D / Bone2D chain, sprites parented to bones
    mesh       the same skeleton, Polygon2D with per-vertex bone weights
    particles  one composite billboard plus GPUParticles2D emitters

Each builder returns the scene text AND a fidelity report: which semantic
tracks it expressed as written, which it had to RELOCATE onto a different node
or property, and which it could not express at all. The report is the honest
half of the bake-off -- a scene that is small because it silently dropped four
tracks is not cheaper, it is less.

Scene contract, identical across all four so a consumer cannot tell them apart
by node lookup: root `Node2D`, `%Visuals` -> `Facing` -> `Rig`, plus `Bounds`,
`%CenterPos`, `%IntentPos`, `%AnimationPlayer`, `%AnimationTree`. That is the
contract the shipped scenes already satisfy (`klee-mod/pck-src/klee/model/
combat.tscn:393-453`) and the one `CreatureAnimationRouter` looks up
(`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:64`).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import geometry, tscn
from .art import PAD, layer_size
from .spec import (
    BONE_BY_NAME,
    BONES,
    PARTS,
    RIG,
    Channel,
    Motion,
    Part,
    Track,
    all_motions,
)

#: Where the `Rig` node sits inside `Facing`. Same 140px lift the shipped
#: scenes use so the figure stands on the creature's base line
#: (`klee-mod/pck-src/klee/model/combat.tscn:402`).
RIG_BASE = (0.0, -140.0)

CHANNEL_PROPERTY: dict[Channel, str] = {
    "offset": "position",
    "spin": "rotation",
    "tint": "modulate",
    "swell": "scale",
}

APPROACH_KEYS = ("layered", "cutout", "mesh", "particles")


@dataclass
class Fidelity:
    expressed: list[str] = field(default_factory=list)
    relocated: list[tuple[str, str]] = field(default_factory=list)  # (track, why)
    dropped: list[tuple[str, str]] = field(default_factory=list)  # (track, why)

    def as_dict(self) -> dict[str, object]:
        return {
            "expressed": len(self.expressed),
            "relocated": [{"track": t, "why": w} for t, w in self.relocated],
            "dropped": [{"track": t, "why": w} for t, w in self.dropped],
        }


@dataclass
class ApproachResult:
    key: str
    scene_text: str
    textures: tuple[str, ...]
    fidelity: Fidelity
    node_count: int
    extra_numbers: int = 0  # hand-authored numbers this approach needs ON TOP


def node_name(part_name: str) -> str:
    return "".join(word.capitalize() for word in part_name.split("_"))


def _track_id(motion: Motion, track: Track) -> str:
    return f"{motion.name}:{track.part}.{track.channel}"


def _offset_value(base: tuple[float, float], value: object) -> tuple[float, float]:
    dx, dy = value  # type: ignore[misc]
    return base[0] + dx, base[1] + dy


def _common_nodes(scene: tscn.Scene, rig_children: list[tscn.Node]) -> None:
    """The contract nodes every approach shares, in a fixed order."""
    scene.nodes.append(tscn.Node("SprigCombat", "Node2D"))
    scene.nodes.append(tscn.Node("Visuals", "Node2D", ".", ["unique_name_in_owner = true"]))
    scene.nodes.append(tscn.Node("Facing", "Node2D", "Visuals", ["unique_name_in_owner = true"]))
    scene.nodes.append(
        tscn.Node("Rig", "Node2D", "Visuals/Facing", [f"position = {tscn.vec2(RIG_BASE)}"])
    )
    scene.nodes.extend(rig_children)
    scene.nodes.append(
        tscn.Node(
            "Bounds",
            "Control",
            ".",
            [
                "unique_name_in_owner = true",
                "layout_mode = 3",
                "anchors_preset = 0",
                "offset_left = -120.0",
                "offset_top = -280.0",
                "offset_right = 120.0",
                "offset_bottom = 0.0",
                "mouse_filter = 2",
            ],
        )
    )
    scene.nodes.append(
        tscn.Node(
            "CenterPos",
            "Marker2D",
            ".",
            ["unique_name_in_owner = true", "position = Vector2(0, -112)"],
        )
    )
    scene.nodes.append(
        tscn.Node(
            "IntentPos",
            "Marker2D",
            ".",
            ["unique_name_in_owner = true", "position = Vector2(0, -350)"],
        )
    )


def _finish(
    scene: tscn.Scene,
    key: str,
    bound: dict[str, list[tscn.BoundTrack]],
    fidelity: Fidelity,
    textures: tuple[str, ...],
    extra_numbers: int = 0,
) -> ApproachResult:
    """Attach the AnimationPlayer/AnimationTree and render."""
    entries: list[tuple[str, str]] = []
    for motion in all_motions():
        anim_id = f"Animation_{motion.name}"
        scene.subs.append(tscn.animation_block(anim_id, motion, bound[motion.name]))
        entries.append((motion.name, anim_id))
    scene.subs.append(tscn.animation_library_block(f"AnimationLibrary_{key}", entries))
    states = [name for name, _ in entries if name != "RESET"]
    scene.subs.append(tscn.state_machine_blocks(f"StateMachine_{key}", states))

    scene.nodes.append(
        tscn.Node(
            "AnimationPlayer",
            "AnimationPlayer",
            ".",
            [
                "unique_name_in_owner = true",
                "libraries = {",
                f'&"": SubResource("AnimationLibrary_{key}")',
                "}",
            ],
        )
    )
    scene.nodes.append(
        tscn.Node(
            "AnimationTree",
            "AnimationTree",
            ".",
            [
                "unique_name_in_owner = true",
                "active = true",
                "callback_mode_discrete = 0",
                f'tree_root = SubResource("StateMachine_{key}")',
                'anim_player = NodePath("../AnimationPlayer")',
            ],
        )
    )
    text = scene.render()
    return ApproachResult(
        key=key,
        scene_text=text,
        textures=textures,
        fidelity=fidelity,
        node_count=text.count("[node name="),
        extra_numbers=extra_numbers,
    )


# --------------------------------------------------------------------------
# 1. layered sprites
# --------------------------------------------------------------------------


def build_layered(tex_dir: str) -> ApproachResult:
    scene = tscn.Scene()
    children: list[tscn.Node] = []
    textures: list[str] = []
    for i, part in enumerate(sorted(PARTS, key=lambda p: p.z), start=1):
        path = f"{tex_dir}/sprig_{part.name}.png"
        textures.append(path)
        ref = scene.add_ext("Texture2D", path, f"{i}_{part.name}")
        children.append(
            tscn.Node(
                node_name(part.name),
                "Sprite2D",
                "Visuals/Facing/Rig",
                [f"position = {tscn.vec2(part.rest)}", f"texture = {ref}"],
            )
        )
    _common_nodes(scene, children)

    fidelity = Fidelity()
    bound: dict[str, list[tscn.BoundTrack]] = {}
    for motion in all_motions():
        rows: list[tscn.BoundTrack] = []
        for track in motion.tracks:
            prop = CHANNEL_PROPERTY[track.channel]
            if track.part == RIG:
                node_path, base = "Visuals/Facing/Rig", RIG_BASE
            else:
                part = next(p for p in PARTS if p.name == track.part)
                node_path, base = f"Visuals/Facing/Rig/{node_name(part.name)}", part.rest
            values = track.values
            if track.channel == "offset":
                values = tuple(_offset_value(base, v) for v in values)
            rows.append(
                tscn.BoundTrack(
                    f"{node_path}:{prop}",
                    track.channel,
                    track.times,
                    values,
                    track.interp,
                    track.transitions,
                )
            )
            if motion.name != "RESET":
                fidelity.expressed.append(_track_id(motion, track))
        bound[motion.name] = rows
    return _finish(scene, "layered", bound, fidelity, tuple(textures))


# --------------------------------------------------------------------------
# 2. cutout / skeletal 2D
# --------------------------------------------------------------------------


def _skeleton_nodes(parent: str) -> list[tscn.Node]:
    """Skeleton2D plus the Bone2D chain, parents before children."""
    nodes = [tscn.Node("Skeleton", "Skeleton2D", parent)]
    for bone in BONES:
        chain = geometry.bone_path(bone.name)
        bone_parent = f"{parent}/Skeleton"
        if "/" in chain:
            bone_parent += "/" + chain.rsplit("/", 1)[0]
        x, y = bone.rest
        nodes.append(
            tscn.Node(
                geometry.bone_node_name(bone.name),
                "Bone2D",
                bone_parent,
                [
                    f"position = {tscn.vec2((x, y))}",
                    f"rest = Transform2D(1, 0, 0, 1, {tscn.num(x)}, {tscn.num(y)})",
                    "auto_calculate_length_and_angle = false",
                    f"length = {tscn.fnum(bone.length)}",
                    "bone_angle = 1.5708",
                ],
            )
        )
    return nodes


def build_cutout(tex_dir: str) -> ApproachResult:
    scene = tscn.Scene()
    children = _skeleton_nodes("Visuals/Facing/Rig")
    textures: list[str] = []
    for i, part in enumerate(sorted(PARTS, key=lambda p: p.z), start=1):
        path = f"{tex_dir}/sprig_{part.name}.png"
        textures.append(path)
        ref = scene.add_ext("Texture2D", path, f"{i}_{part.name}")
        bone_parent = f"Visuals/Facing/Rig/Skeleton/{geometry.bone_path(part.bone)}"
        children.append(
            tscn.Node(
                node_name(part.name),
                "Sprite2D",
                bone_parent,
                [
                    f"position = {tscn.vec2(geometry.sprite_offset(part))}",
                    f"z_index = {part.z}",
                    f"texture = {ref}",
                ],
            )
        )
    _common_nodes(scene, children)

    fidelity = Fidelity()
    bound: dict[str, list[tscn.BoundTrack]] = {}
    for motion in all_motions():
        rows: list[tscn.BoundTrack] = []
        for track in motion.tracks:
            prop = CHANNEL_PROPERTY[track.channel]
            tid = _track_id(motion, track)
            if track.part == RIG:
                node_path, base = "Visuals/Facing/Rig", RIG_BASE
            else:
                part = next(p for p in PARTS if p.name == track.part)
                sprite_path = (
                    f"Visuals/Facing/Rig/Skeleton/{geometry.bone_path(part.bone)}"
                    f"/{node_name(part.name)}"
                )
                if track.channel in ("offset", "spin"):
                    node_path = f"Visuals/Facing/Rig/Skeleton/{geometry.bone_path(part.bone)}"
                    base = BONE_BY_NAME[part.bone].rest
                else:
                    # Bone2D has no modulate, and scaling a bone scales every
                    # bone under it. Colour and scale therefore ride the SPRITE.
                    node_path, base = sprite_path, geometry.sprite_offset(part)
                    if motion.name != "RESET":
                        fidelity.relocated.append(
                            (tid, f"Bone2D carries no {prop}; moved onto the child Sprite2D")
                        )
            values = track.values
            if track.channel == "offset":
                values = tuple(_offset_value(base, v) for v in values)
            rows.append(
                tscn.BoundTrack(
                    f"{node_path}:{prop}",
                    track.channel,
                    track.times,
                    values,
                    track.interp,
                    track.transitions,
                )
            )
            if motion.name != "RESET" and not any(t == tid for t, _ in fidelity.relocated):
                fidelity.expressed.append(tid)
        bound[motion.name] = rows
    return _finish(scene, "cutout", bound, fidelity, tuple(textures))


# --------------------------------------------------------------------------
# 3. mesh deformation
# --------------------------------------------------------------------------


def _polygon_node(scene: tscn.Scene, part: Part, ref: str) -> tscn.Node:
    """One skinned Polygon2D.

    The bone weights are serialised as a FLAT `bones = [path, weights, ...]`
    array, which is the only spelling this engine accepts. The older
    `bones/0/path` / `bones/0/weights` form is not merely deprecated here: on
    MegaDot 4.5.1 it is not a settable property at all, and the scene parser
    DISCARDS IT WITHOUT AN ERROR -- import exits 0, export exits 0, the scene
    loads, and `Polygon2D.get_bone_count()` is 0, so the mesh never deforms.
    Measured directly against the editor rather than taken from documentation;
    `Polygon2D.get_property_list()` on 4.5.1 exposes one `bones` property
    (usage 10 = STORAGE|INTERNAL), and `PackedScene.pack` round-trips it in the
    flat form used below.
    """
    polygon = geometry.polygon_for(part)
    uv = geometry.uv_for(part, polygon)
    bones: list[str] = []
    for bone, weights in geometry.weights_for(part, polygon):
        bones.append(f'"{geometry.bone_path(bone)}"')
        bones.append("PackedFloat32Array(" + ", ".join(tscn.num(w) for w in weights) + ")")
    return tscn.Node(
        node_name(part.name),
        "Polygon2D",
        "Visuals/Facing/Rig",
        [
            f"z_index = {part.z}",
            f"texture = {ref}",
            "polygon = PackedVector2Array("
            + ", ".join(f"{tscn.num(x)}, {tscn.num(y)}" for x, y in polygon)
            + ")",
            "uv = PackedVector2Array("
            + ", ".join(f"{tscn.num(x)}, {tscn.num(y)}" for x, y in uv)
            + ")",
            'skeleton = NodePath("../Skeleton")',
            "bones = [" + ", ".join(bones) + "]",
        ],
    )


def build_mesh(tex_dir: str) -> ApproachResult:
    scene = tscn.Scene()
    children = _skeleton_nodes("Visuals/Facing/Rig")
    textures: list[str] = []
    for i, part in enumerate(sorted(PARTS, key=lambda p: p.z), start=1):
        path = f"{tex_dir}/sprig_{part.name}.png"
        textures.append(path)
        ref = scene.add_ext("Texture2D", path, f"{i}_{part.name}")
        children.append(_polygon_node(scene, part, ref))
    _common_nodes(scene, children)

    has_children = {b.parent for b in BONES if b.parent is not None}

    fidelity = Fidelity()
    bound: dict[str, list[tscn.BoundTrack]] = {}
    for motion in all_motions():
        rows: list[tscn.BoundTrack] = []
        for track in motion.tracks:
            prop = CHANNEL_PROPERTY[track.channel]
            tid = _track_id(motion, track)
            if track.part == RIG:
                node_path, base = "Visuals/Facing/Rig", RIG_BASE
            else:
                part = next(p for p in PARTS if p.name == track.part)
                bone = part.bone
                if track.channel in ("offset", "spin"):
                    node_path = f"Visuals/Facing/Rig/Skeleton/{geometry.bone_path(bone)}"
                    base = BONE_BY_NAME[bone].rest
                elif track.channel == "tint":
                    node_path, base = (
                        f"Visuals/Facing/Rig/{node_name(part.name)}",
                        (0.0, 0.0),
                    )
                    if motion.name != "RESET":
                        fidelity.relocated.append(
                            (tid, "colour rides the Polygon2D; the bone has no modulate")
                        )
                else:  # swell
                    if bone in has_children:
                        # A skinned Polygon2D ignores its own scale, so the only
                        # place left is the bone -- which would scale every bone
                        # under it too. Not expressible without a rig change.
                        if motion.name != "RESET":
                            fidelity.dropped.append(
                                (
                                    tid,
                                    f"skinned Polygon2D ignores node scale and bone "
                                    f"'{bone}' has children",
                                )
                            )
                        continue
                    node_path = f"Visuals/Facing/Rig/Skeleton/{geometry.bone_path(bone)}"
                    base = (0.0, 0.0)
                    if motion.name != "RESET":
                        fidelity.relocated.append(
                            (tid, "scale moved onto the leaf Bone2D; skinned polygons ignore theirs")
                        )
            values = track.values
            if track.channel == "offset":
                values = tuple(_offset_value(base, v) for v in values)
            rows.append(
                tscn.BoundTrack(
                    f"{node_path}:{prop}",
                    track.channel,
                    track.times,
                    values,
                    track.interp,
                    track.transitions,
                )
            )
            touched = {t for t, _ in fidelity.relocated} | {t for t, _ in fidelity.dropped}
            if motion.name != "RESET" and tid not in touched:
                fidelity.expressed.append(tid)
        bound[motion.name] = rows
    return _finish(scene, "mesh", bound, fidelity, tuple(textures))


# --------------------------------------------------------------------------
# 4. particles / tweens
# --------------------------------------------------------------------------

#: emitter name -> (motion that fires it, amount, lifetime, one_shot)
EMITTERS: tuple[tuple[str, str, int, float, bool], ...] = (
    ("Charge", "intent", 10, 0.6, False),
    ("Burst", "attack", 18, 0.45, True),
    ("Motes", "death", 24, 1.0, True),
)

_PROCESS_MATERIAL = {
    "Charge": [
        "particle_flag_disable_z = true",
        "direction = Vector3(0, -1, 0)",
        "spread = 25.0",
        "initial_velocity_min = 20.0",
        "initial_velocity_max = 60.0",
        "gravity = Vector3(0, -40, 0)",
        "scale_min = 0.5",
        "scale_max = 1.5",
        "color = Color(1, 0.93, 0.72, 1)",
    ],
    "Burst": [
        "particle_flag_disable_z = true",
        "direction = Vector3(1, 0, 0)",
        "spread = 60.0",
        "initial_velocity_min = 90.0",
        "initial_velocity_max = 220.0",
        "gravity = Vector3(0, 180, 0)",
        "scale_min = 0.6",
        "scale_max = 2.0",
        "color = Color(1, 0.85, 0.4, 1)",
    ],
    "Motes": [
        "particle_flag_disable_z = true",
        "direction = Vector3(0, -1, 0)",
        "spread = 180.0",
        "initial_velocity_min = 10.0",
        "initial_velocity_max = 70.0",
        "gravity = Vector3(0, -30, 0)",
        "scale_min = 0.4",
        "scale_max = 1.2",
        "color = Color(0.66, 0.7, 0.8, 1)",
    ],
}


def build_particles(tex_dir: str) -> ApproachResult:
    scene = tscn.Scene()
    body_tex = scene.add_ext("Texture2D", f"{tex_dir}/sprig_composite.png", "1_body")
    mote_tex = scene.add_ext("Texture2D", f"{tex_dir}/sprig_mote.png", "2_mote")
    textures = (f"{tex_dir}/sprig_composite.png", f"{tex_dir}/sprig_mote.png")

    children = [
        tscn.Node(
            "Body",
            "Sprite2D",
            "Visuals/Facing/Rig",
            ["unique_name_in_owner = true", "position = Vector2(0, 20)", f"texture = {body_tex}"],
        )
    ]
    for name, _motion, amount, lifetime, one_shot in EMITTERS:
        scene.subs.append(
            f'[sub_resource type="ParticleProcessMaterial" id="Material_{name}"]'
            + tscn.NL
            + tscn.NL.join(_PROCESS_MATERIAL[name])
        )
        children.append(
            tscn.Node(
                name,
                "GPUParticles2D",
                "Visuals/Facing/Rig",
                [
                    "unique_name_in_owner = true",
                    "position = Vector2(28, 20)",
                    "emitting = false",
                    f"amount = {amount}",
                    f"texture = {mote_tex}",
                    f"lifetime = {tscn.fnum(lifetime)}",
                    f"one_shot = {str(one_shot).lower()}",
                    "explosiveness = 0.8" if one_shot else "explosiveness = 0.0",
                    "fixed_fps = 60",
                    "local_coords = true",
                    f'process_material = SubResource("Material_{name}")',
                ],
            )
        )
    _common_nodes(scene, children)

    fidelity = Fidelity()
    bound: dict[str, list[tscn.BoundTrack]] = {}
    extra_numbers = 0
    for motion in all_motions():
        rows: list[tscn.BoundTrack] = []
        used: set[str] = set()
        for track in motion.tracks:
            prop = CHANNEL_PROPERTY[track.channel]
            tid = _track_id(motion, track)
            if track.part == RIG:
                node_path, base = "Visuals/Facing/Rig", RIG_BASE
                relocated_why = None
            elif track.part == "torso":
                node_path, base = "Visuals/Facing/Rig/Body", (0.0, 20.0)
                relocated_why = "no per-part nodes exist; the torso channel drives the billboard"
            else:
                if motion.name != "RESET":
                    fidelity.dropped.append((tid, "billboard approach has no node for this part"))
                continue
            key = f"{node_path}:{prop}"
            if key in used:
                if motion.name != "RESET":
                    fidelity.dropped.append(
                        (tid, f"path collision: {key} is already driven in this motion")
                    )
                continue
            used.add(key)
            values = track.values
            if track.channel == "offset":
                values = tuple(_offset_value(base, v) for v in values)
            rows.append(
                tscn.BoundTrack(
                    key, track.channel, track.times, values, track.interp, track.transitions
                )
            )
            if motion.name != "RESET":
                if relocated_why:
                    fidelity.relocated.append((tid, relocated_why))
                else:
                    fidelity.expressed.append(tid)
        # Emitter toggles: the compensation this approach has to hand-author on
        # top of the shared suite, and the reason its number count does not fall
        # as far as its node count suggests.
        for name, fires_on, _amount, _lifetime, _one_shot in EMITTERS:
            on = motion.name == fires_on
            if motion.name == "RESET" or on:
                rows.append(
                    tscn.BoundTrack(
                        f"Visuals/Facing/Rig/{name}:emitting",
                        "flag",
                        (0.0,),
                        (on,),
                        interp=0,
                    )
                )
                extra_numbers += 2
        bound[motion.name] = rows

    return _finish(scene, "particles", bound, fidelity, textures, extra_numbers)


BUILDERS = {
    "layered": build_layered,
    "cutout": build_cutout,
    "mesh": build_mesh,
    "particles": build_particles,
}


def build(key: str, tex_dir: str) -> ApproachResult:
    return BUILDERS[key](tex_dir)


def texture_footprint() -> dict[str, tuple[int, int]]:
    """Per-part final layer sizes, for the package-cost table."""
    return {p.name: layer_size(p) for p in PARTS}


__all__ = [
    "APPROACH_KEYS",
    "ApproachResult",
    "Fidelity",
    "PAD",
    "RIG_BASE",
    "build",
    "texture_footprint",
]
