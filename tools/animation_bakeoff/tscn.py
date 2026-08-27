"""Godot 4 `.tscn` text emission.

Small and deliberately dumb: the four approach builders differ in WHICH nodes
and node paths they emit, not in how a `[sub_resource type="Animation"]` block
is spelled, so the spelling lives here once. The output grammar is copied in
shape from the scenes the mod already ships -- see
`klee-mod/pck-src/klee/model/combat.tscn:9-460` for the Animation /
AnimationLibrary / AnimationNodeStateMachine forms and
`klee-mod/pck-src/klee/vfx/dodoco_pop.tscn:6-17` for the
ParticleProcessMaterial form.

Everything is written with `\\n` newlines and ASCII only, and nothing is
ordered by a set or a dict comprehension over unsorted input, so two runs of
the same builder produce byte-identical text.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .spec import Channel, Motion, Track

NL = "\n"


# --------------------------------------------------------------------------
# scalars
# --------------------------------------------------------------------------


def num(value: float) -> str:
    """Godot-ish compact number: integral floats lose the decimal tail."""
    if value == int(value):
        return str(int(value))
    return repr(round(float(value), 6))


def fnum(value: float) -> str:
    """Number in a context where Godot always prints a decimal point."""
    text = repr(round(float(value), 6))
    return text if ("." in text or "e" in text) else text + ".0"


def vec2(value: tuple[float, float]) -> str:
    return f"Vector2({num(value[0])}, {num(value[1])})"


def color(value: tuple[float, float, float, float]) -> str:
    return "Color(" + ", ".join(num(c) for c in value) + ")"


def literal(channel: Channel, value: object) -> str:
    if channel in ("offset", "swell"):
        return vec2(value)  # type: ignore[arg-type]
    if channel == "tint":
        return color(value)  # type: ignore[arg-type]
    if channel == "flag":
        return "true" if value else "false"
    return fnum(value)  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# animation resources
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class BoundTrack:
    """A semantic `Track` after an approach has chosen its node path.

    `path` is the full Godot animation track path, e.g.
    ``Visuals/Facing/Rig/Head:position``. `values` is already in the property's
    own units -- an approach that maps `offset` onto `position` must have added
    the rest position itself, because only the approach knows where its node
    sits.
    """

    path: str
    channel: Channel
    times: tuple[float, ...]
    values: tuple[object, ...]
    interp: int = 1
    transitions: tuple[float, ...] | None = None


def animation_block(anim_id: str, motion: Motion, tracks: list[BoundTrack]) -> str:
    lines = [f'[sub_resource type="Animation" id="{anim_id}"]']
    if motion.name != "RESET":
        lines.append(f'resource_name = "{motion.name}"')
    lines.append(f"length = {fnum(motion.length)}")
    if motion.loop:
        lines.append("loop_mode = 1")
    for i, track in enumerate(tracks):
        transitions = track.transitions or tuple(1.0 for _ in track.times)
        lines += [
            f'tracks/{i}/type = "value"',
            f"tracks/{i}/imported = false",
            f"tracks/{i}/enabled = true",
            f'tracks/{i}/path = NodePath("{track.path}")',
            f"tracks/{i}/interp = {track.interp}",
            "tracks/%d/loop_wrap = true" % i,
            f"tracks/{i}/keys = {{",
            '"times": PackedFloat32Array(' + ", ".join(num(t) for t in track.times) + "),",
            '"transitions": PackedFloat32Array(' + ", ".join(num(t) for t in transitions) + "),",
            '"update": 0,',
            '"values": [' + ", ".join(literal(track.channel, v) for v in track.values) + "]",
            "}",
        ]
    return NL.join(lines)


def animation_library_block(lib_id: str, entries: list[tuple[str, str]]) -> str:
    """`entries` is [(animation name, sub-resource id)], RESET first."""
    rows = ",\n".join(f'&"{name}": SubResource("{sub}")' for name, sub in entries)
    return f'[sub_resource type="AnimationLibrary" id="{lib_id}"]{NL}_data = {{{NL}{rows}{NL}}}'


# --------------------------------------------------------------------------
# the state machine
# --------------------------------------------------------------------------

#: (from, to, switch_mode, advance_mode). advance_mode 2 == Auto, 0 == Manual
#: (a `Travel()` call). switch_mode 2 == AtEnd. Mirrors the shipped graph in
#: `klee-mod/pck-src/klee/model/combat.tscn:340-390`, plus the `intent` state
#: this lane's charter requires.
STATE_GRAPH: tuple[tuple[str, str, int | None, int], ...] = (
    ("Start", "idle", None, 2),
    ("idle", "intent", None, 0),
    ("intent", "idle", None, 0),
    ("idle", "attack", None, 0),
    ("intent", "attack", None, 0),
    ("attack", "idle", 2, 2),
    ("idle", "hurt", None, 0),
    ("intent", "hurt", None, 0),
    ("attack", "hurt", None, 0),
    ("hurt", "idle", 2, 2),
    ("idle", "death", None, 0),
    ("intent", "death", None, 0),
    ("attack", "death", None, 0),
    ("hurt", "death", None, 0),
    ("death", "End", 2, 0),
)

#: Editor graph positions. Cosmetic, but they must be STABLE or every
#: regeneration produces a different file and the repeatability measurement
#: measures the generator instead of the pipeline.
STATE_POS: dict[str, tuple[int, int]] = {
    "Start": (140, 160),
    "idle": (320, 160),
    "intent": (320, 40),
    "attack": (470, 40),
    "hurt": (320, 290),
    "death": (620, 160),
    "End": (780, 160),
}


def state_machine_blocks(sm_id: str, states: list[str]) -> str:
    """AnimationNodeAnimation + transition + state-machine sub-resources."""
    blocks: list[str] = []
    for state in states:
        blocks.append(
            f'[sub_resource type="AnimationNodeAnimation" id="Anim_{state}"]{NL}'
            f'animation = &"{state}"'
        )
    edges = [e for e in STATE_GRAPH if e[0] in states + ["Start"] and e[1] in states + ["End"]]
    for src, dst, switch, advance in edges:
        lines = [f'[sub_resource type="AnimationNodeStateMachineTransition" id="T_{src}_{dst}"]']
        if switch is not None:
            lines.append(f"switch_mode = {switch}")
        lines.append(f"advance_mode = {advance}")
        blocks.append(NL.join(lines))

    sm = [f'[sub_resource type="AnimationNodeStateMachine" id="{sm_id}"]']
    sm.append(f'states/End/position = {vec2(STATE_POS["End"])}')
    sm.append(f'states/Start/position = {vec2(STATE_POS["Start"])}')
    for state in sorted(states):
        sm.append(f'states/{state}/node = SubResource("Anim_{state}")')
        sm.append(f"states/{state}/position = {vec2(STATE_POS[state])}")
    parts = []
    for src, dst, _switch, _advance in edges:
        parts += [f'"{src}"', f'"{dst}"', f'SubResource("T_{src}_{dst}")']
    sm.append("transitions = [" + ", ".join(parts) + "]")
    blocks.append(NL.join(sm))
    return (NL + NL).join(blocks)


# --------------------------------------------------------------------------
# scene assembly
# --------------------------------------------------------------------------


@dataclass
class Node:
    name: str
    type: str
    parent: str | None = None  # None == scene root, "." == child of root
    props: list[str] = field(default_factory=list)

    def render(self) -> str:
        head = f'[node name="{self.name}" type="{self.type}"'
        if self.parent is not None:
            head += f' parent="{self.parent}"'
        head += "]"
        return NL.join([head, *self.props])


@dataclass
class Scene:
    """A `.tscn` under construction: ext resources, sub resources, node tree."""

    ext: list[tuple[str, str, str]] = field(default_factory=list)  # (type, path, id)
    subs: list[str] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)

    def add_ext(self, res_type: str, path: str, res_id: str) -> str:
        self.ext.append((res_type, path, res_id))
        return f'ExtResource("{res_id}")'

    def render(self) -> str:
        load_steps = len(self.ext) + len(self.subs) + 1
        out = [f"[gd_scene load_steps={load_steps} format=3]", ""]
        for res_type, path, res_id in self.ext:
            out.append(f'[ext_resource type="{res_type}" path="{path}" id="{res_id}"]')
        if self.ext:
            out.append("")
        for sub in self.subs:
            out.append(sub)
            out.append("")
        for node in self.nodes:
            out.append(node.render())
            out.append("")
        return NL.join(out).rstrip(NL) + NL


def track_count(scene_text: str) -> int:
    """How many animation value tracks a rendered scene carries."""
    return scene_text.count('/type = "value"')
