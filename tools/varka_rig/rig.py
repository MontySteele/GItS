"""Varka's combat and merchant scenes: spec + frame manifest -> .tscn.

Pure text generation, no pixels and no engine: `varka.yaml` (each state's
sheet and motion) and `tools/char_render/varka_frames.json` (the committed
manifest tools/char_render/pack.py writes beside his sheets) go in, the scene
text comes out. Klee's generator (tools/klee_rig/rig.py) is the template;
what differs is what the manifest differs in:

  * PAGED, TRIMMED FRAMES. Klee's sheets are uniform grids (hframes x
    vframes). Varka's frames are each cut to their own pixels and
    shelf-packed, so a frame is an AtlasTexture (region = its rect on its
    page, margin = its offset in the clip's cell plus the trimmed remainder)
    and a state steps the sprite's `texture` through them. A clip on several
    pages needs nothing more: each AtlasTexture names its own page.
  * THE ELEMENT LAYER. `fx.attack` and `fx.ascension` are neutral heat
    layers (R=G=B heat, A coverage) drawn over the body from the clip frame
    the manifest names. One ShaderMaterial, local to each scene instance,
    colours them: mix(element, white, smoothstep(0.72, 1, heat)), the review
    sheets' look (tools/char_render/fx.py `tint`). KleeMod.Vfx.ElementTrail
    sets its `element` from the played card's element at runtime; it rests at
    Anemo.
  * THE GROUND BURST. `effects.ground_burst` plays twice from the ascension's
    start frame: %GroundBurst at the blade's point (the manifest's offset from
    his feet), and %TargetBurst, mirrored, which ElementTrail moves under the
    target's feet when the clip starts. The mirror is a negative x scale, so
    it turns about the ground point (a Sprite2D's flip_h would turn about the
    sprite's offset instead).

Every number is rounded and every collection walked in a fixed order, so two
runs are byte-identical. Scalar animation keys are spelled as floats (the
MegaDot 4.5.1 fact tools/klee_rig/rig.py records).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from tools.klee_rig.rig import color, fnum, num, vec2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = HERE / "varka.yaml"
FRAMES = ROOT / "tools" / "char_render" / "varka_frames.json"
SCENE = ROOT / "klee-mod" / "pck-src" / "varka" / "model" / "combat.tscn"
MERCHANT_SCENE = ROOT / "klee-mod" / "pck-src" / "varka" / "model" / "merchant_character.tscn"
MODEL = "Visuals/Facing/Model"
FACING = "Visuals/Facing"
FRAME_DIR = "res://varka/model/frames"
NL = "\n"

#: The router contract (CreatureAnimationRouter.cs) plus `ascension`.
ANIMATION_ORDER = ("idle", "attack", "hurt", "death", "cast", "power", "idle_low", "ascension")
#: The one-shots, at the lengths the clips were rendered to (the manifest's
#: `length`); the death seam measures the clip, so ModdedPlayerDeathSeam
#: follows the death's 2.2 s on its own.
ONE_SHOT_LENGTHS = {"attack": 1.05, "hurt": 0.8, "death": 2.2, "cast": 1.0, "power": 1.0, "ascension": 1.3}
#: Sheet name (manifest key) -> its Sprite2D under Model.
SHEET_NODE = {"idle": "Idle", "idle_low": "IdleLow", "attack": "Attack", "hurt": "Hurt",
              "death": "Death", "cast": "Cast", "ascension": "Ascension"}
#: Clip -> the Sprite2D under Model that draws its element layer. Unique
#: names: KleeMod.Vfx.ElementTrail finds them as %AttackFx / %AscensionFx.
FX_NODE = {"attack": "AttackFx", "ascension": "AscensionFx"}
#: The ground burst's two copies, under %Facing so a turned Varka mirrors them.
BURST_EFFECT = "ground_burst"
BURST_NODE = {"blade_tip": "GroundBurst", "target": "TargetBurst"}
#: Where %TargetBurst rests until ElementTrail places it: the review sheets'
#: dummy target, 550 px to his right at 1080p (visual paper, Round 3).
TARGET_REST = (550.0, 0.0)
#: The element shader's parameter and its resting colour: Anemo, his own
#: (KleeMod.Vfx.ReactionFx.ElementFlashHex, #8fffd6).
ELEMENT_PARAM = "element"
ANEMO_HEX = "#8fffd6"
#: Every element his attacks can carry -> its colour, the mod's one element
#: table (ReactionFx.ElementFlashHex); tools/char_render/fx.py ELEMENTS too.
ELEMENT_HEX = {"anemo": "#8fffd6", "pyro": "#ff9a5c", "hydro": "#5cb8ff", "electro": "#c08cff",
               "cryo": "#a8f0ff"}
#: Two lines of shader: the review sheets' tint. `tint` carries the sprite's
#: modulate x self_modulate from the vertex stage, so the state tracks still
#: show and hide the layer. Body lines are tab-indented (a text-scene reader
#: must never take a shader line for a property).
SHADER_CODE = "\n".join([
    "shader_type canvas_item;",
    "",
    "uniform vec4 element : source_color = vec4(0.560784, 1.0, 0.839216, 1.0);",
    "varying vec4 tint;",
    "",
    "void vertex() {",
    "\ttint = COLOR;",
    "}",
    "",
    "void fragment() {",
    "\tvec4 heat = texture(TEXTURE, UV);",
    "\tCOLOR = vec4(mix(element.rgb, vec3(1.0), smoothstep(0.72, 1.0, heat.r)), heat.a) * tint;",
    "}",
])
SHADER_ID = "Shader_element"
MATERIAL_ID = "ShaderMaterial_element"
PROP_ORDER = [":position", ":rotation", ":modulate", ":self_modulate", ":texture"]


def hex_color(h: str) -> tuple[float, float, float, float]:
    h = h.lstrip("#")
    return tuple(round(int(h[i:i + 2], 16) / 255, 6) for i in (0, 2, 4)) + (1.0,)


# ---------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------


def load_spec(path: Path = SPEC) -> dict:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=loader)


def load_frames(path: Path = FRAMES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# the atlas: one AtlasTexture per frame
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Atlas:
    id: str
    page_id: str
    region: tuple[int, int, int, int]
    margin: tuple[int, int, int, int]


def atlas_margin(rec: dict, frame: dict) -> tuple[int, int, int, int]:
    """AtlasTexture.margin for one trimmed frame: its offset inside the cell,
    and how much of the cell the trim took away, so the texture's size is the
    cell's and its pixels land where the untrimmed cell would put them."""
    cw, ch = rec["cell"]
    x, y, w, h = frame["rect"]
    ox, oy = frame["offset"]
    assert ox + w <= cw and oy + h <= ch, "a frame runs out of its cell"
    return (ox, oy, cw - w, ch - h)


@dataclass
class Clip:
    """One packed clip of the manifest: its key in the scene's ids, its
    pages' ext_resource ids and its frames' AtlasTextures."""
    key: str
    rec: dict
    pages: list[tuple[str, str]]        # (ext id, file)
    atlases: list[Atlas]


def clip_of(key: str, rec: dict, first_ext: int) -> Clip:
    pages = []
    for p, page in enumerate(rec["pages"]):
        suffix = "" if len(rec["pages"]) == 1 else f"_p{p + 1}"
        pages.append((f"{first_ext + p}_{key}{suffix}", page["file"]))
    atlases = []
    for i, fr in enumerate(rec["frames"]):
        atlases.append(Atlas(f"Atlas_{key}_{i}", pages[fr["page"]][0], tuple(fr["rect"]), atlas_margin(rec, fr)))
    assert len(atlases) == rec["count"], key
    return Clip(key, rec, pages, atlases)


def clips_of(spec: dict, frames: dict) -> dict[str, Clip]:
    """Every clip the combat scene draws, in a fixed order: the model sheets,
    the fx layers, the ground burst."""
    out: dict[str, Clip] = {}
    n = 1
    for name in spec["model"]["sheets"]:
        out[name] = clip_of(name, frames["sheets"][name], n)
        n += len(out[name].pages)
    for name in FX_NODE:
        out[f"fx_{name}"] = clip_of(f"fx_{name}", frames["fx"][name], n)
        n += len(out[f"fx_{name}"].pages)
    out["burst"] = clip_of("burst", frames["effects"][BURST_EFFECT], n)
    return out


def atlas_block(a: Atlas) -> str:
    return NL.join([
        f'[sub_resource type="AtlasTexture" id="{a.id}"]',
        f'atlas = ExtResource("{a.page_id}")',
        "region = Rect2(" + ", ".join(num(v) for v in a.region) + ")",
        "margin = Rect2(" + ", ".join(num(v) for v in a.margin) + ")",
        "filter_clip = true",
    ])


def sub(a: Atlas) -> str:
    return f'SubResource("{a.id}")'


# ---------------------------------------------------------------------------
# animations
# ---------------------------------------------------------------------------


@dataclass
class Track:
    path: str
    kind: str                 # "vec2" | "float" | "color" | "res"
    times: list[float]
    values: list
    transitions: list[float]
    interp: int = 1
    update: int = 0           # 1 = discrete


def _expand(anim: dict, tr: dict) -> Track:
    length = float(anim["length"])
    prop = tr["prop"]
    node = tr["model"]
    path = MODEL + (f"/{node}" if node else "") + f":{prop}"
    kind = {"position": "vec2", "rotation": "float", "modulate": "color"}[prop]
    conv = (lambda v: (float(v[0]), float(v[1]))) if kind == "vec2" else \
           (lambda v: tuple(float(c) for c in v)) if kind == "color" else float
    times, values, trans = [], [], []
    for key in tr["keys"]:
        times.append(float(key[0]))
        values.append(conv(key[1]))
        trans.append(float(key[2]) if len(key) > 2 else 1.0)
    assert times == sorted(times) and times[-1] <= length + 1e-9, path
    return Track(path, kind, times, values, trans)


def _shown(path: str, on: bool) -> Track:
    return Track(f"{path}:self_modulate", "color", [0.0], [(1.0, 1.0, 1.0, 1.0 if on else 0.0)], [1.0])


def _window(path: str, t_on: float, t_off: float) -> Track:
    """Hidden, shown from t_on, hidden again from t_off: discrete, so the
    layer never fades in on a linear key."""
    return Track(f"{path}:self_modulate", "color", [0.0, t_on, t_off],
                 [(1.0, 1.0, 1.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0)], [1.0] * 3,
                 interp=0, update=1)


def _steps(path: str, times: list[float], atlases: list[Atlas]) -> Track:
    return Track(f"{path}:texture", "res", times, [sub(a) for a in atlases], [1.0] * len(times),
                 interp=0, update=1)


def fx_window(frames: dict, clip: str) -> tuple[list[float], float]:
    """The clip times the element layer's frames show at (fx frame i is the
    clip's frame first_frame + i), and the time it is gone."""
    rec = frames["sheets"][clip]
    fx = frames["fx"][clip]
    first, count = int(fx["first_frame"]), int(fx["count"])
    times = [float(t) for t in rec["times"]]
    assert first + count <= len(times), f"{clip}: fx runs past the clip"
    shown = times[first:first + count]
    end = times[first + count] if first + count < len(times) else shown[-1] + 1.0 / fx["fps"]
    return shown, end


def burst_use(frames: dict) -> dict:
    uses = frames["effects"][BURST_EFFECT]["uses"]
    assert len(uses) == 1, "the ground burst has one use: the ascension"
    return uses[0]


def burst_window(frames: dict) -> tuple[str, list[float], float]:
    """(clip, the times its frames show, the time it is gone): from the
    placing clip's start frame at the burst's own fps."""
    use = burst_use(frames)
    eff = frames["effects"][BURST_EFFECT]
    clip = use["clip"]
    t0 = float(frames["sheets"][clip]["times"][int(use["start_frame"])])
    fps = float(eff["fps"])
    shown = [round(t0 + i / fps, 6) for i in range(int(eff["count"]))]
    end = round(t0 + int(eff["count"]) / fps, 6)
    return clip, shown, end


def state_tracks(spec: dict, frames: dict, clips: dict[str, Clip], anim: dict) -> list[Track]:
    """Show this state's sheet (every other sheet hidden) and step it at the
    times the renderer drew; show the element layer and the ground bursts
    only where this state's clip places them."""
    sheet = anim["sheet"]
    rec = frames["sheets"][sheet]
    length = float(anim["length"])
    out = [_shown(f"{MODEL}/{SHEET_NODE[name]}", name == sheet) for name in spec["model"]["sheets"]]
    times = [float(t) for t in rec["times"]]
    assert times[-1] < length + 1e-9, f"{sheet}: frames run past the state's length"
    if anim.get("loop"):
        # the loop wraps one frame interval (or less) after its last frame
        # (idle: 34 frames at 12 fps in the rendered 2.8 s)
        assert abs(rec["length"] - length) < 1e-6 and length - times[-1] <= 1.0 / rec["fps"] + 1e-6,             f"{sheet}: the loop's length is not the rendered one"
    out.append(_steps(f"{MODEL}/{SHEET_NODE[sheet]}", times, clips[sheet].atlases))
    for clip, node in FX_NODE.items():
        path = f"{MODEL}/{node}"
        if clip == sheet:
            shown, end = fx_window(frames, clip)
            assert end <= length + 1e-9
            out.append(_window(path, shown[0], end))
            out.append(_steps(path, shown, clips[f"fx_{clip}"].atlases))
        else:
            out.append(_shown(path, False))
    bclip, bshown, bend = burst_window(frames)
    for node in BURST_NODE.values():
        path = f"{FACING}/{node}"
        if bclip == sheet:
            assert bend <= length + 1e-9, "the ground burst outlasts its clip"
            out.append(_window(path, bshown[0], bend))
            out.append(_steps(path, bshown, clips["burst"].atlases))
        else:
            out.append(_shown(path, False))
    return out


def build_animations(spec: dict, frames: dict, clips: dict[str, Clip]) -> dict[str, tuple[dict, list[Track]]]:
    out = {}
    for name in ANIMATION_ORDER:
        anim = spec["animations"][name]
        tracks = [_expand(anim, tr) for tr in anim.get("tracks", ())]
        tracks += state_tracks(spec, frames, clips, anim)
        paths = [t.path for t in tracks]
        assert len(paths) == len(set(paths)), f"{name}: duplicate track"
        out[name] = (anim, tracks)
    return out


def rest_value(path: str, clips: dict[str, Clip]):
    node, prop = path.split(":")
    if prop == "position":
        return (0.0, 0.0)
    if prop == "rotation":
        return 0.0
    if prop == "self_modulate":
        return (1.0, 1.0, 1.0, 1.0 if node == f"{MODEL}/Idle" else 0.0)
    if prop == "texture":
        return sub(clips[node_clip(node)].atlases[0])
    return (1.0, 1.0, 1.0, 1.0)


def node_clip(node: str) -> str:
    """The clip whose frames a sprite node draws."""
    leaf = node.rsplit("/", 1)[-1]
    for name, n in SHEET_NODE.items():
        if n == leaf:
            return name
    for name, n in FX_NODE.items():
        if n == leaf:
            return f"fx_{name}"
    assert leaf in BURST_NODE.values(), node
    return "burst"


def reset_tracks(anims, clips: dict[str, Clip]) -> list[Track]:
    """RESET is derived: every property any animation drives, at rest."""
    seen: list[str] = []
    for _anim, tracks in anims.values():
        for t in tracks:
            if t.path not in seen:
                seen.append(t.path)
    seen.sort(key=lambda p: (p.count("/"), PROP_ORDER.index(p[p.index(":"):]), p))
    out = []
    for p in seen:
        prop = p.split(":")[1]
        kind = {"position": "vec2", "rotation": "float", "texture": "res"}.get(prop, "color")
        discrete = kind == "res"
        out.append(Track(p, kind, [0.0], [rest_value(p, clips)], [1.0],
                         interp=0 if discrete else 1, update=1 if discrete else 0))
    return out


# ---------------------------------------------------------------------------
# scene text
# ---------------------------------------------------------------------------


def _lit(kind: str, v) -> str:
    if kind == "vec2":
        return vec2(v)
    if kind == "color":
        return color(v)
    if kind == "res":
        return v
    return fnum(v)


def animation_block(anim_id: str, name: str | None, length: float, loop: bool, tracks: list[Track]) -> str:
    lines = [f'[sub_resource type="Animation" id="{anim_id}"]']
    if name:
        lines.append(f'resource_name = "{name}"')
    lines.append(f"length = {fnum(length)}")
    if loop:
        lines.append("loop_mode = 1")
    for i, t in enumerate(tracks):
        lines += [
            f'tracks/{i}/type = "value"',
            f"tracks/{i}/imported = false",
            f"tracks/{i}/enabled = true",
            f'tracks/{i}/path = NodePath("{t.path}")',
            f"tracks/{i}/interp = {t.interp}",
            f"tracks/{i}/loop_wrap = true",
            f"tracks/{i}/keys = {{",
            '"times": PackedFloat32Array(' + ", ".join(num(x) for x in t.times) + "),",
            '"transitions": PackedFloat32Array(' + ", ".join(num(x) for x in t.transitions) + "),",
            f'"update": {t.update},',
            '"values": [' + ", ".join(_lit(t.kind, v) for v in t.values) + "]",
            "}",
        ]
    return NL.join(lines)


# ---------------------------------------------------------------------------
# the state machine (Klee's graph with `ascension` where hers has her two)
# ---------------------------------------------------------------------------
SM_STATES = {"idle": (327, 153), "attack": (327, 64), "hurt": (327, 278), "death": (470, 153),
             "cast": (186, 64), "power": (470, 64), "idle_low": (327, 365), "ascension": (470, 278)}
SM_ONE_SHOTS = ("attack", "hurt", "cast", "power", "ascension")
SM_SOURCES = ("idle", "idle_low", "attack", "hurt", "cast", "power", "ascension")
SM_TARGETS = ("attack", "hurt", "death", "cast", "power", "ascension")


def xfade(src: str, dst: str) -> float:
    """Klee's cross-fades (the base skeletons' SpineAnimationMix, census 1c):
    0.05 s by default, 0.1 s from idle into a strike, ~0.03 s into a hurt,
    0.1 s out of one, and a hurt cuts straight to death. The ascension starts
    from the guard like the attack, so it fades in like one."""
    if src == "hurt" and dst == "death":
        return 0.0
    if dst == "hurt":
        return 0.03
    if dst in ("attack", "ascension") and src in ("idle", "idle_low"):
        return 0.1
    if src == "hurt" and dst == "idle":
        return 0.1
    return 0.05


def _transition(tid: str, xf: float, switch: int, advance: int, cond: str | None = None) -> str:
    lines = [f'[sub_resource type="AnimationNodeStateMachineTransition" id="{tid}"]']
    if xf:
        lines.append(f"xfade_time = {fnum(xf)}")
    if switch:
        lines.append(f"switch_mode = {switch}")
    lines.append(f"advance_mode = {advance}")
    if cond:
        lines.append(f'advance_condition = &"{cond}"')
    return NL.join(lines)


def state_machine() -> str:
    blocks = []
    for st in SM_STATES:
        blocks.append(f'[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_{st}"]'
                      + NL + f'animation = &"{st}"')
    edges = [("Start", "idle", _transition("Transition_start_idle", 0, 0, 2))]
    for src in SM_SOURCES:
        for dst in SM_TARGETS:
            if src != dst:
                edges.append((src, dst, _transition(f"Transition_{src}_{dst}", xfade(src, dst), 0, 1)))
    for src in SM_ONE_SHOTS:
        edges.append((src, "idle", _transition(f"Transition_{src}_idle", xfade(src, "idle"), 2, 2)))
    edges.append(("idle", "idle_low", _transition("Transition_idle_idle_low", 0.4, 0, 2, "low_hp")))
    edges.append(("idle_low", "idle", _transition("Transition_idle_low_idle", 0.4, 0, 2, "healthy")))
    edges.append(("death", "End", _transition("Transition_death_end", 0, 2, 0)))
    blocks += [e[2] for e in edges]
    sm = ['[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_varka"]',
          "states/End/position = Vector2(628, 153)",
          "states/Start/position = Vector2(186, 153)"]
    for st in sorted(SM_STATES):
        x, y = SM_STATES[st]
        sm.append(f'states/{st}/node = SubResource("AnimationNodeAnimation_{st}")')
        sm.append(f"states/{st}/position = Vector2({x}, {y})")
    ids = [e[2].split('id="')[1].split('"')[0] for e in edges]
    sm.append("transitions = [" + ", ".join(f'"{e[0]}", "{e[1]}", SubResource("{i}")'
                                             for e, i in zip(edges, ids)) + "]")
    blocks.append(NL.join(sm))
    return (NL + NL).join(blocks)


STATE_MACHINE = state_machine()

#: Bounds/CenterPos/IntentPos are his old rig's, which fit a 280 px figure;
#: standing he is 270.5 px in full, 249.9 in the guard (the manifest's
#: `measure` and `stance_a`).
TAIL_NODES = """[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = -120.0
offset_top = -280.0
offset_right = 120.0
offset_bottom = 0.0
mouse_filter = 2

[node name="CenterPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, -112)

[node name="IntentPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, -350)

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {
&"": SubResource("AnimationLibrary_varka")
}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_varka")
anim_player = NodePath("../AnimationPlayer")
metadata/idle_desync = true"""

SHADOW_ID = "0_shadow"
SHADOW_NODE = "Shadow"


def _shadow_sprite(parent: str, shadow: dict, where: dict, ext_id: str) -> str:
    tw, th = shadow["texture"]
    w, h = where["size"]
    return NL.join([
        f'[node name="{SHADOW_NODE}" type="Sprite2D" parent="{parent}"]',
        f"position = {vec2(where['center'])}",
        f"scale = {vec2((w / tw, h / th))}",
        f'texture = ExtResource("{ext_id}")',
    ])


def _sprite(name: str, parent: str, clip: Clip, sc: tuple[float, float], *, shown: bool,
            unique: bool = False, fx: bool = False, position=None, meta: dict | None = None) -> str:
    ox, oy = clip.rec["origin"]
    lines = [f'[node name="{name}" type="Sprite2D" parent="{parent}"]']
    if unique:
        lines.append("unique_name_in_owner = true")
    if not shown:
        lines.append("self_modulate = Color(1, 1, 1, 0)")
    if fx:
        lines.append(f'material = SubResource("{MATERIAL_ID}")')
    if position is not None:
        lines.append(f"position = {vec2(position)}")
    lines += [
        f"texture = {sub(clip.atlases[0])}",
        "centered = false",
        f"offset = {vec2((-ox, -oy))}",
        f"scale = {vec2(sc)}",
    ]
    for k, v in (meta or {}).items():
        lines.append(f"metadata/{k} = {v}")
    return NL.join(lines)


def burst_places(frames: dict) -> dict[str, dict]:
    """Each copy of the ground burst: its node, its resting position under
    %Facing (scene px) and its x scale sign."""
    sc = frames["combat_scale"]
    out = {}
    for place in burst_use(frames)["places"]:
        node = BURST_NODE[place["at"]]
        if place["at"] == "blade_tip":
            dx, dy = place["offset_px"]
            pos = (dx * sc, dy * sc)
        else:
            pos = TARGET_REST
        out[node] = {"at": place["at"], "position": pos, "mirror": bool(place["flip_h"])}
    assert set(out) == set(BURST_NODE.values()), "the ground burst plays at the blade and the target"
    return out


def material_blocks() -> list[str]:
    code = SHADER_CODE.replace("\\", "\\\\").replace('"', '\\"')
    return [
        NL.join([f'[sub_resource type="Shader" id="{SHADER_ID}"]', f'code = "{code}"']),
        NL.join([
            f'[sub_resource type="ShaderMaterial" id="{MATERIAL_ID}"]',
            # one per Varka on the field: two can strike in two elements at once
            "resource_local_to_scene = true",
            f'shader = SubResource("{SHADER_ID}")',
            f"shader_parameter/{ELEMENT_PARAM} = {color(hex_color(ANEMO_HEX))}",
        ]),
    ]


def render_scene(spec: dict | None = None, frames: dict | None = None) -> str:
    spec = spec or load_spec()
    frames = frames or load_frames()
    clips = clips_of(spec, frames)
    anims = build_animations(spec, frames, clips)
    for name, length in ONE_SHOT_LENGTHS.items():
        assert float(anims[name][0]["length"]) == length, f"{name} length changed"
    for name in spec["model"]["sheets"]:
        if name in ONE_SHOT_LENGTHS:
            assert abs(frames["sheets"][name]["length"] - ONE_SHOT_LENGTHS[name]) < 1e-6, name

    subs = [atlas_block(a) for c in clips.values() for a in c.atlases]
    subs += material_blocks()
    subs.append(animation_block("Animation_reset", None, 0.001, False, reset_tracks(anims, clips)))
    for name in ANIMATION_ORDER:
        anim, tracks = anims[name]
        subs.append(animation_block(f"Animation_{name}", name, float(anim["length"]),
                                    bool(anim.get("loop")), tracks))
    lib = sorted(["RESET", *ANIMATION_ORDER], key=lambda n: (n != "RESET", n))
    subs.append('[sub_resource type="AnimationLibrary" id="AnimationLibrary_varka"]' + NL
                + "_data = {" + NL
                + ("," + NL).join(f'&"{n}": SubResource("Animation_{"reset" if n == "RESET" else n}")' for n in lib)
                + NL + "}")
    subs.append(STATE_MACHINE)

    shadow = frames["shadow"]
    exts = [(SHADOW_ID, shadow["file"])] + [p for c in clips.values() for p in c.pages]
    load_steps = len(exts) + sum(s.count("[sub_resource") for s in subs) + 1
    out = [f"[gd_scene load_steps={load_steps} format=3]", ""]
    for ext_id, file in exts:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{file}" id="{ext_id}"]')
    out.append("")
    for s in subs:
        out += [s, ""]

    sc = frames["combat_scale"]
    nodes = [
        '[node name="VarkaCombat" type="Node2D"]',
        '[node name="Visuals" type="Node2D" parent="."]\nunique_name_in_owner = true',
        f'[node name="Facing" type="Node2D" parent="Visuals"]\nunique_name_in_owner = true',
        _shadow_sprite(FACING, shadow, shadow["combat"], SHADOW_ID),
        f'[node name="Model" type="Node2D" parent="{FACING}"]',
    ]
    for name in spec["model"]["sheets"]:
        nodes.append(_sprite(SHEET_NODE[name], MODEL, clips[name], (sc, sc), shown=name == "idle"))
    for clip, node in FX_NODE.items():
        nodes.append(_sprite(node, MODEL, clips[f"fx_{clip}"], (sc, sc), shown=False, unique=True, fx=True))
    bclip, bshown, _bend = burst_window(frames)
    for node, place in burst_places(frames).items():
        nodes.append(_sprite(node, FACING, clips["burst"], (-sc if place["mirror"] else sc, sc), shown=False,
                             unique=True, fx=True, position=place["position"],
                             meta={"place": f'"{place["at"]}"', "start": fnum(bshown[0])}))
    nodes.append(TAIL_NODES)
    for n in nodes:
        out += [n, ""]
    return NL.join(out).rstrip(NL) + NL


# ---------------------------------------------------------------------------
# the merchant scene
# ---------------------------------------------------------------------------


def render_merchant_scene(frames: dict | None = None) -> str:
    """Varka at the shop: stance B, both claymores planted, breathing on a
    loop. Klee's shape (tools/klee_rig/rig.py render_merchant_scene): a bare
    Node2D root (BaseLib copies the root's transform onto the merchant node),
    the shadow first so it draws behind, the sheet sprite at the merchant
    scale with its feet on the origin, and an autoplaying AnimationPlayer --
    no Spine and no script (MerchantSpineBindingPatch skips the binding)."""
    frames = frames or load_frames()
    rec = frames["sheets"]["merchant"]
    clip = clip_of("merchant", rec, 1)
    sc = frames["merchant_scale"]
    times = [float(t) for t in rec["times"]]
    assert times[-1] < rec["length"] <= times[-1] + 1.0 / rec["fps"] + 1e-6
    anim = animation_block("Animation_relaxed", "relaxed_loop", float(rec["length"]), True,
                           [_steps("Sheet", times, clip.atlases)])
    reset = animation_block("Animation_reset", None, 0.001, False,
                            [_steps("Sheet", [0.0], clip.atlases[:1])])
    lib = ('[sub_resource type="AnimationLibrary" id="AnimationLibrary_merchant"]' + NL + "_data = {" + NL
           + '&"RESET": SubResource("Animation_reset"),' + NL
           + '&"relaxed_loop": SubResource("Animation_relaxed")' + NL + "}")
    shadow = frames["shadow"]
    exts = [(SHADOW_ID, shadow["file"])] + clip.pages
    subs = [atlas_block(a) for a in clip.atlases] + [reset, anim, lib]
    out = [f"[gd_scene load_steps={len(exts) + len(subs) + 1} format=3]", ""]
    for ext_id, file in exts:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{file}" id="{ext_id}"]')
    out.append("")
    for s in subs:
        out += [s, ""]
    ox, oy = rec["origin"]
    out += [
        '[node name="VarkaMerchant" type="Node2D"]', "",
        _shadow_sprite(".", shadow, shadow["merchant"], SHADOW_ID), "",
        NL.join([
            '[node name="Sheet" type="Sprite2D" parent="."]',
            f"texture = {sub(clip.atlases[0])}",
            "centered = false",
            f"offset = {vec2((-ox, -oy))}",
            f"scale = {vec2((sc, sc))}",
        ]), "",
        NL.join([
            '[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
            "libraries = {",
            '&"": SubResource("AnimationLibrary_merchant")',
            "}",
            'autoplay = "relaxed_loop"',
        ]),
    ]
    return NL.join(out) + NL
