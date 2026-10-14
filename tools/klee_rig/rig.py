"""Klee's combat scene: spec + frame manifest -> combat.tscn.

Pure text generation, no pixels and no engine: `klee.yaml` (the sheets and
each state's motion) and `klee_frames.json` (the committed manifest of the
frame sheets tools/klee_render renders from the official model) go in, the
scene text comes out.

The scene draws one figure, `Visuals/Facing/Model`: one Sprite2D per frame
sheet, cross-faded by self_modulate and stepped by a discrete `frame` track.
Every state, `setoff` included, plays a sheet rendered from the official
model. (Until 2026-10-13 `setoff` cross-faded to `Visuals/Facing/Rig`, a
skinned-mesh rig of the old floating-bombs splash; the owner: "I tried doing
a Set off that triggered the old splash art, and I regret keeping that
around - let's pivot to animations based on the new model instead." The rig
and its cut layers are gone.) Every number is rounded and every collection is
walked in a fixed order, so two runs are byte-identical.

Engine fact this file is written around (MegaDot 4.5.1, the animation
bake-off, commit 09864c273): scalar animation keys must be spelled as floats
(`0.0`, not `0`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = HERE / "klee.yaml"
FRAMES = HERE / "klee_frames.json"
SCENE = ROOT / "klee-mod" / "pck-src" / "klee" / "model" / "combat.tscn"
MODEL = "Visuals/Facing/Model"
FRAME_DIR = "res://klee/model/frames"
NL = "\n"

#: The router contract (CreatureAnimationRouter.cs) plus `setoff` and `jumpy`.
ANIMATION_ORDER = ("idle", "attack", "hurt", "death", "cast", "power", "idle_low", "setoff", "jumpy")
#: The one-shots on the base game's clock (the paper's census: attack
#: 0.93-1.5 s, cast 0.97-1.8, hurt 0.73-1.0, die 1.87-4.17). The death seam
#: measures the clip, so ModdedPlayerDeathSeam follows this number on its own.
ONE_SHOT_LENGTHS = {"attack": 1.0, "hurt": 0.8, "death": 2.0, "cast": 1.0, "power": 1.0, "setoff": 0.85,
                    "jumpy": 1.2}
#: Sheet name (manifest key) -> its Sprite2D under Model.
SHEET_NODE = {"idle": "Idle", "idle_low": "IdleLow", "attack": "Attack", "hurt": "Hurt",
              "death": "Death", "cast": "Cast", "setoff": "SetOff", "jumpy": "Jumpy"}
PROP_KIND = {":position": "vec2", ":rotation": "float", ":modulate": "color",
             ":self_modulate": "color", ":frame": "int"}
PROP_ORDER = [":position", ":rotation", ":modulate", ":self_modulate", ":frame"]


def node_rest(path: str):
    """RESET value of a node track: the model rests on its idle sheet's
    first frame, every other sheet hidden."""
    node, prop = path.split(":")
    prop = ":" + prop
    if prop == ":position":
        return (0.0, 0.0)
    if prop == ":rotation":
        return 0.0
    if prop == ":frame":
        return 0
    if prop == ":self_modulate":
        return (1.0, 1.0, 1.0, 1.0 if node == f"{MODEL}/Idle" else 0.0)
    return (1.0, 1.0, 1.0, 1.0)


# ---------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------


def num(v: float) -> str:
    v = round(float(v), 4)
    if v == 0:
        return "0"
    if v == int(v):
        return str(int(v))
    return repr(v)


def fnum(v: float) -> str:
    text = repr(round(float(v), 6))
    if text == "-0.0":
        text = "0.0"
    return text if ("." in text or "e" in text) else text + ".0"


def vec2(v) -> str:
    return f"Vector2({num(v[0])}, {num(v[1])})"


def color(v) -> str:
    return "Color(" + ", ".join(num(c) for c in v) + ")"


# ---------------------------------------------------------------------------
# spec
# ---------------------------------------------------------------------------


def load_spec(path: Path = SPEC) -> dict:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=loader)


def load_frames(path: Path = FRAMES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# animations
# ---------------------------------------------------------------------------


@dataclass
class Track:
    path: str
    kind: str                 # "vec2" | "float" | "color" | "int"
    times: list[float]
    values: list
    transitions: list[float]
    interp: int = 1
    update: int = 0           # 1 = discrete (the sheet's frame index)


def _expand(anim: dict, tr: dict) -> Track:
    """One `model:` track: a property of Model ("") or a node under it."""
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
    return Track(path, kind, times, values, trans, interp=1)


def sheet_tracks(spec: dict, frames: dict, anim: dict) -> list[Track]:
    """Show this state's sheet (self_modulate alpha 1, every other sheet 0)
    and step its frame at the times the renderer drew them."""
    sheet = anim["sheet"]
    rec = frames["sheets"][sheet]
    length = float(anim["length"])
    out = []
    for name in spec["model"]["sheets"]:
        a = 1.0 if name == sheet else 0.0
        out.append(Track(f"{MODEL}/{SHEET_NODE[name]}:self_modulate", "color", [0.0], [(1.0, 1.0, 1.0, a)], [1.0]))
    if "hold_frame" in anim:
        times, values = [0.0], [int(anim["hold_frame"])]
    else:
        times = [float(t) for t in rec["times"]]
        values = list(range(len(times)))
        assert times[-1] < length + 1e-9, f"{sheet}: frames run past the state's length"
        if anim.get("loop"):
            assert abs(len(times) / rec["fps"] - length) < 1e-6, f"{sheet}: loop length != frames / fps"
    out.append(Track(f"{MODEL}/{SHEET_NODE[sheet]}:frame", "int", times, values, [1.0] * len(times),
                     interp=0, update=1))
    return out


def build_animations(spec: dict, frames: dict | None = None) -> dict[str, tuple[dict, list[Track]]]:
    frames = frames or load_frames()
    out = {}
    for name in ANIMATION_ORDER:
        anim = spec["animations"][name]
        tracks = [_expand(anim, tr) for tr in anim.get("tracks", ())]
        tracks += sheet_tracks(spec, frames, anim)
        paths = [t.path for t in tracks]
        assert len(paths) == len(set(paths)), f"{name}: duplicate track"
        out[name] = (anim, tracks)
    return out


def reset_tracks(anims) -> list[Track]:
    """RESET is derived: every property any animation drives, at rest."""
    seen: list[str] = []
    for _anim, tracks in anims.values():
        for t in tracks:
            if t.path not in seen:
                seen.append(t.path)
    seen.sort(key=lambda p: (p.count("/"), PROP_ORDER.index(p[p.index(":"):]), p))
    out = []
    for p in seen:
        kind = PROP_KIND[p[p.index(":"):]]
        if kind == "int":
            out.append(Track(p, kind, [0.0], [node_rest(p)], [1.0], interp=0, update=1))
        else:
            out.append(Track(p, kind, [0.0], [node_rest(p)], [1.0]))
    return out


# ---------------------------------------------------------------------------
# scene text
# ---------------------------------------------------------------------------


def _lit(kind: str, v) -> str:
    if kind == "vec2":
        return vec2(v)
    if kind == "color":
        return color(v)
    if kind == "int":
        return str(int(v))
    return fnum(v)


def animation_block(anim_id: str, name: str | None, length: float, loop: bool,
                    tracks: list[Track]) -> str:
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
# the state machine
# ---------------------------------------------------------------------------
#: States as the router names them, with their editor positions.
SM_STATES = {"idle": (327, 153), "attack": (327, 64), "hurt": (327, 278), "death": (470, 153),
             "cast": (186, 64), "power": (470, 64), "idle_low": (327, 365), "setoff": (186, 278),
             "jumpy": (470, 278)}
#: One-shots the router travels to; each returns to idle at its end.
SM_ONE_SHOTS = ("attack", "hurt", "cast", "power", "setoff", "jumpy")
#: Every live state can cut straight to any one-shot or to death, so a hit
#: during a throw shows at once rather than queueing behind it.
SM_SOURCES = ("idle", "idle_low", "attack", "hurt", "cast", "power", "setoff", "jumpy")
SM_TARGETS = ("attack", "hurt", "death", "cast", "power", "setoff", "jumpy")


def xfade(src: str, dst: str) -> float:
    """Cross-fade times from the base skeletons' SpineAnimationMix (census
    1c): default 0.05 s, 0.1 s from idle into an attack, ~0.03 s into a hurt,
    0.1 s out of one. A hurt cuts straight to death as the base does. Set Off
    starts and ends in stance A, so it fades like a cast."""
    if src == "hurt" and dst == "death":
        return 0.0
    if dst == "hurt":
        return 0.03
    if dst in ("attack", "jumpy") and src in ("idle", "idle_low"):
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
    """The AnimationTree graph. advance_mode 1 (enabled) is what lets
    `Travel` use a transition and so cross-fade; the old scene's were 0
    (disabled), so every Travel teleported and every clip snapped."""
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
    sm = ['[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_klee"]',
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

#: Bounds/CenterPos/IntentPos fit the figure (about 177 px to the feather at
#: 1080p, klee_frames.json "measure"): the base Silent's are a 244 px box for
#: a 224 px figure, CenterPos at ~0.65 of the height.
TAIL_NODES = """[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = -120.0
offset_top = -200.0
offset_right = 120.0
offset_bottom = 0.0
mouse_filter = 2

[node name="CenterPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, -100)

[node name="IntentPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, -270)

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {
&"": SubResource("AnimationLibrary_klee")
}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_klee")
anim_player = NodePath("../AnimationPlayer")
metadata/idle_desync = true"""


def _model_nodes(spec: dict, frames: dict) -> list[str]:
    """Visuals/Facing/Model and one Sprite2D per sheet. The sprite's offset
    puts the cell's feet anchor on the node origin; scale 0.5 because the
    sheets are drawn at 2x for a 4K screen."""
    sc = frames["combat_scale"]
    out = ['[node name="Model" type="Node2D" parent="Visuals/Facing"]']
    for name in spec["model"]["sheets"]:
        rec = frames["sheets"][name]
        node = SHEET_NODE[name]
        ox, oy = rec["origin"]
        lines = [f'[node name="{node}" type="Sprite2D" parent="{MODEL}"]']
        if name != "idle":
            lines.append("self_modulate = Color(1, 1, 1, 0)")
        lines += [
            f'texture = ExtResource("{SHEET_IDS[name]}")',
            "centered = false",
            f"offset = {vec2((-ox, -oy))}",
            f"scale = {vec2((sc, sc))}",
            f"hframes = {rec['hframes']}",
            f"vframes = {rec['vframes']}",
        ]
        out.append(NL.join(lines))
    return out


SHEET_IDS = {name: f"{1 + i}_{name}" for i, name in enumerate(
    ("idle", "idle_low", "attack", "hurt", "death", "cast", "setoff", "jumpy"))}

#: The thrown bomb (klee_frames.json "thrown", cut by klee_render/pack.py).
PROJECTILE_ID = "8_bomb"
#: KleeMod.Vfx.ThrownProjectile's scene contract: a hidden sprite at the hand
#: as of the release frame, under %Facing so a flipped Klee throws from the
#: mirrored hand, with the release time of its clip as metadata.
PROJECTILE_NODE = "ThrownProjectile"
PROJECTILE_RELEASE_META = "release"
#: Every clip that throws: (its state, the node, the texture's id). Jumpy
#: Dumpty's head-sized bomb is the jumpy clip's (2026-10-13).
PROJECTILES = (("attack", PROJECTILE_NODE, PROJECTILE_ID),
               ("jumpy", "JumpyProjectile", "10_bomb_big"))


def thrown_of(frames: dict, clip: str = "attack") -> dict | None:
    rec = frames["sheets"].get(clip)
    return rec.get("thrown") if rec else None


def _projectile_node(frames: dict, clip: str = "attack") -> list[str]:
    """A thrown bomb, drawn by the game from the release frame to the
    target (the base's NVfxProjectileHandler shape), never by the cells."""
    thrown = thrown_of(frames, clip)
    if thrown is None:
        return []
    node, ext_id = next((n, i) for c, n, i in PROJECTILES if c == clip)
    sc = frames["combat_scale"]
    ox, oy = frames["sheets"][clip]["origin"]
    ax, ay = thrown["at"]
    return [NL.join([
        f'[node name="{node}" type="Sprite2D" parent="Visuals/Facing"]',
        "unique_name_in_owner = true",
        "visible = false",
        f"position = {vec2(((ax - ox) * sc, (ay - oy) * sc))}",
        f"scale = {vec2((sc, sc))}",
        f'texture = ExtResource("{ext_id}")',
        f"metadata/{PROJECTILE_RELEASE_META} = {fnum(thrown['time'])}",
    ])]


#: Her ground shadow (klee_frames.json "shadow", drawn by klee_render/pack.py).
#: The base cast each draw theirs as a `shadow` region inside their own Spine
#: skeleton, under the figure, at the feet; Klee's figure is sprites, so hers
#: is a Sprite2D at the feet anchor, first under %Facing so it draws behind her
#: and mirrors with her. Nothing animates it: it holds through the attack, the
#: death sit and the flip, as the base shadows (on the root) do.
SHADOW_ID = "9_shadow"
SHADOW_NODE = "Shadow"


def shadow_of(frames: dict) -> dict | None:
    return frames.get("shadow")


def _shadow_sprite(parent: str, shadow: dict, where: dict, ext_id: str) -> str:
    tw, th = shadow["texture"]
    w, h = where["size"]
    return NL.join([
        f'[node name="{SHADOW_NODE}" type="Sprite2D" parent="{parent}"]',
        f"position = {vec2(where['center'])}",
        f"scale = {vec2((w / tw, h / th))}",
        f'texture = ExtResource("{ext_id}")',
    ])


def render_scene(spec: dict | None = None, frames: dict | None = None) -> str:
    spec = spec or load_spec()
    frames = frames or load_frames()
    anims = build_animations(spec, frames)
    for name, length in ONE_SHOT_LENGTHS.items():
        assert float(anims[name][0]["length"]) == length, f"{name} length changed"

    subs = [animation_block("Animation_reset", None, 0.001, False, reset_tracks(anims))]
    for name in ANIMATION_ORDER:
        anim, tracks = anims[name]
        subs.append(animation_block(f"Animation_{name}", name, float(anim["length"]),
                                    bool(anim.get("loop")), tracks))
    lib = sorted(["RESET", *ANIMATION_ORDER], key=lambda n: (n != "RESET", n))
    subs.append('[sub_resource type="AnimationLibrary" id="AnimationLibrary_klee"]' + NL
                + "_data = {" + NL
                + ("," + NL).join(f'&"{n}": SubResource("Animation_{"reset" if n == "RESET" else n}")' for n in lib)
                + NL + "}")
    subs.append(STATE_MACHINE)

    sheets = spec["model"]["sheets"]
    throws = [(clip, ext_id, thrown_of(frames, clip)) for clip, _n, ext_id in PROJECTILES
              if thrown_of(frames, clip) is not None]
    shadow = shadow_of(frames)
    load_steps = (len(sheets) + len(throws) + (shadow is not None)
                  + sum(s.count("[sub_resource") for s in subs) + 1)
    out = [f"[gd_scene load_steps={load_steps} format=3]", ""]
    for name in sheets:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{frames["sheets"][name]["file"]}" '
                   f'id="{SHEET_IDS[name]}"]')
    for _clip, ext_id, thrown in throws:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{thrown["file"]}" id="{ext_id}"]')
    if shadow is not None:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{shadow["file"]}" id="{SHADOW_ID}"]')
    out.append("")
    for s in subs:
        out += [s, ""]
    nodes = [
        '[node name="KleeCombat" type="Node2D"]',
        '[node name="Visuals" type="Node2D" parent="."]\nunique_name_in_owner = true',
        '[node name="Facing" type="Node2D" parent="Visuals"]\nunique_name_in_owner = true',
        *([_shadow_sprite("Visuals/Facing", shadow, shadow["combat"], SHADOW_ID)] if shadow else []),
        *_model_nodes(spec, frames),
        *(n for clip, _n, _i in PROJECTILES for n in _projectile_node(frames, clip)),
        TAIL_NODES,
    ]
    for n in nodes:
        out += [n, ""]
    return NL.join(out).rstrip(NL) + NL


# ---------------------------------------------------------------------------
# the merchant scene
# ---------------------------------------------------------------------------
MERCHANT_SCENE = ROOT / "klee-mod" / "pck-src" / "klee" / "model" / "merchant_character.tscn"


def render_merchant_scene(frames: dict | None = None) -> str:
    """Klee at the shop: stance B (the bomb cradled) breathing on a loop.

    The base merchant rig is the combat skeleton at ~1.7x with its own
    `relaxed_loop` (census T2); its feet sit on the node origin, its
    `shadow` region under them (hers: the Shadow sprite, first so it draws
    behind). BaseLib adds
    this scene's ROOT as the NMerchantCharacter's first child and also copies
    the root's transform onto the merchant node itself, so the root is a bare
    Node2D and the scale lives on the sheet sprite below it. The idle needs no
    script: the AnimationPlayer autoplays it (MerchantSpineBindingPatch skips
    the base's Spine binding, which would otherwise try to play it).
    """
    frames = frames or load_frames()
    rec = frames["sheets"]["merchant"]
    sc = frames["merchant_scale"]
    ox, oy = rec["origin"]
    times = [float(t) for t in rec["times"]]
    assert abs(len(times) / rec["fps"] - rec["length"]) < 1e-6
    anim = animation_block("Animation_relaxed", "relaxed_loop", float(rec["length"]), True,
                           [Track("Sheet:frame", "int", times, list(range(len(times))), [1.0] * len(times),
                                  interp=0, update=1)])
    reset = animation_block("Animation_reset", None, 0.001, False,
                            [Track("Sheet:frame", "int", [0.0], [0], [1.0], interp=0, update=1)])
    lib = ('[sub_resource type="AnimationLibrary" id="AnimationLibrary_merchant"]' + NL + "_data = {" + NL
           + '&"RESET": SubResource("Animation_reset"),' + NL
           + '&"relaxed_loop": SubResource("Animation_relaxed")' + NL + "}")
    shadow = shadow_of(frames)
    out = [
        f"[gd_scene load_steps={5 + (shadow is not None)} format=3]", "",
        f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{rec["file"]}" id="1_sheet"]',
        *([f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{shadow["file"]}" id="2_shadow"]']
          if shadow else []), "",
        reset, "", anim, "", lib, "",
        '[node name="KleeMerchant" type="Node2D"]', "",
        *([_shadow_sprite(".", shadow, shadow["merchant"], "2_shadow"), ""] if shadow else []),
        NL.join([
            '[node name="Sheet" type="Sprite2D" parent="."]',
            'texture = ExtResource("1_sheet")',
            "centered = false",
            f"offset = {vec2((-ox, -oy))}",
            f"scale = {vec2((sc, sc))}",
            f"hframes = {rec['hframes']}",
            f"vframes = {rec['vframes']}",
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


# ---------------------------------------------------------------------------
# the character-select background
# ---------------------------------------------------------------------------

#: The select scene this generator is the one producer of (build_pck.ps1 only
#: overlays it): the backdrop, the close-up breathing on a loop and the
#: Pyro emitters (tools/select_bg.py, 2026-10-14).
SELECT_SCENE = ROOT / "klee-mod" / "pck-src" / "klee" / "ui" / "char_select_bg_klee.tscn"
#: The backdrop tint (as the scene carried it in build_pck.ps1).
SELECT_TINT = (0.52, 0.42, 0.42, 1.0)
SELECT_ELEMENT = "pyro"
#: The figure's horizontal centre in select_closeup.png (its opaque columns
#: span x 883-1616 in the 2026-10-14 render): the breath's pivot and the glow.
SELECT_FIGURE_X = 1250.0


def render_select_scene() -> str:
    from tools.select_bg import render_select_scene as _render

    return _render("klee", "KleeBg", SELECT_TINT, SELECT_ELEMENT, SELECT_FIGURE_X)
