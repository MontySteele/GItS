"""Furina's combat and merchant scenes: spec + frame manifest -> .tscn.

Pure text generation, no pixels and no engine: `furina.yaml` (each state's
sheet and motion) and `tools/char_render/furina_frames.json` (the committed
manifest tools/char_render/pack.py writes beside her sheets) go in, the scene
text comes out. Varka's generator (tools/varka_rig/rig.py) is the template and
lends its primitives (the paged, trimmed AtlasTextures, the tracks, the
animation blocks); what differs is what her manifest differs in:

  * THE SIGNATURE CLIP is `rejoice` (Let the People Rejoice), where his is
    `ascension`, and it places no effect of its own.
  * THE ELEMENT LAYER is the attack's alone: the phantom rapier's trail and
    streak (`fx.attack`), coloured by one scene-local ShaderMaterial that
    KleeMod.Vfx.ElementTrail sets from the played card's element. It rests at
    Hydro, hers, and a card with no element keeps it there (the node's
    `rest_element`).
  * THE STAGE EFFECTS (`effects.spend`, `drain`, `repay`) are no state's:
    each is a Sprite2D under Visuals/Facing/StageFx, at her chest, with an
    AnimationPlayer of its own (a child of the root, beside the state
    machine's), played over whatever she is doing by
    KleeMod.Vfx.FurinaStageFx on the stage event. Each wears its manifest
    tint on a material of its own. Drain and Repay record their `reach` (the
    chest-to-seat run the effect was drawn for) so the game can stretch them
    to the guest who is actually seated.

Every number is rounded and every collection walked in a fixed order, so two
runs are byte-identical.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools.klee_rig.rig import color, fnum, vec2
from tools.varka_rig.rig import (MODEL, NL, PROP_ORDER, SHADER_CODE, Clip, Track, _expand, _shown, _steps,
                                 _transition, _window, animation_block, atlas_block, clip_of, fx_window,
                                 hex_color, sub)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = HERE / "furina.yaml"
FRAMES = ROOT / "tools" / "char_render" / "furina_frames.json"
MODEL_DIR = ROOT / "klee-mod" / "pck-src" / "furina" / "model"
SCENE = MODEL_DIR / "combat.tscn"
MERCHANT_SCENE = MODEL_DIR / "merchant_character.tscn"
FACING = "Visuals/Facing"
FRAME_DIR = "res://furina/model/frames"

#: The router contract (CreatureAnimationRouter.cs) plus `rejoice`.
ANIMATION_ORDER = ("idle", "attack", "hurt", "death", "cast", "power", "idle_low", "rejoice")
#: The one-shots, at the lengths the clips were rendered to (the manifest's
#: `length`); the death seam measures the clip, so ModdedPlayerDeathSeam
#: follows the death's 2.2 s on its own.
ONE_SHOT_LENGTHS = {"attack": 1.0, "hurt": 0.8, "death": 2.2, "cast": 1.0, "power": 1.0, "rejoice": 1.5}
#: Sheet name (manifest key) -> its Sprite2D under Model.
SHEET_NODE = {"idle": "Idle", "idle_low": "IdleLow", "attack": "Attack", "hurt": "Hurt",
              "death": "Death", "cast": "Cast", "rejoice": "Rejoice"}
#: Clip -> the Sprite2D under Model that draws its element layer. A unique
#: name: KleeMod.Vfx.ElementTrail finds it as %AttackFx, as on Varka.
FX_NODE = {"attack": "AttackFx"}
#: Her element, which the attack layer rests at and a card with no element
#: keeps (ElementTrail reads the node's `rest_element`).
REST_ELEMENT = "hydro"
HYDRO_HEX = "#5cb8ff"
ELEMENT_PARAM = "element"
SHADER_ID = "Shader_element"
MATERIAL_ID = "ShaderMaterial_element"

#: The stage effects, in the order the manifest's fx.STAGE_EFFECTS lists
#: them -> the Sprite2D and the AnimationPlayer KleeMod.Vfx.FurinaStageFx
#: finds by unique name. The animation is named for the effect.
STAGE_EFFECTS = ("spend", "drain", "repay")
STAGE_GROUP = "StageFx"
STAGE_NODE = {"spend": "SpendFx", "drain": "DrainFx", "repay": "RepayFx"}
STAGE_PLAYER = {"spend": "SpendFxPlayer", "drain": "DrainFxPlayer", "repay": "RepayFxPlayer"}
#: The two that run between her and the stage, and so stretch to the seat.
REACHING = ("drain", "repay")


# ---------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------


def load_spec(path: Path = SPEC) -> dict:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=loader)


def load_frames(path: Path = FRAMES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def clips_of(spec: dict, frames: dict) -> dict[str, Clip]:
    """Every clip the combat scene draws, in a fixed order: the model sheets,
    the attack's element layer, the three stage effects."""
    out: dict[str, Clip] = {}
    n = 1
    for name in spec["model"]["sheets"]:
        out[name] = clip_of(name, frames["sheets"][name], n)
        n += len(out[name].pages)
    for name in FX_NODE:
        out[f"fx_{name}"] = clip_of(f"fx_{name}", frames["fx"][name], n)
        n += len(out[f"fx_{name}"].pages)
    for name in STAGE_EFFECTS:
        out[f"stage_{name}"] = clip_of(f"stage_{name}", frames["effects"][name], n)
        n += len(out[f"stage_{name}"].pages)
    return out


# ---------------------------------------------------------------------------
# the state animations
# ---------------------------------------------------------------------------


def state_tracks(spec: dict, frames: dict, clips: dict[str, Clip], anim: dict) -> list[Track]:
    """Show this state's sheet (every other sheet hidden) and step it at the
    times the renderer drew; show the element layer only in its own clip."""
    sheet = anim["sheet"]
    rec = frames["sheets"][sheet]
    length = float(anim["length"])
    out = [_shown(f"{MODEL}/{SHEET_NODE[name]}", name == sheet) for name in spec["model"]["sheets"]]
    times = [float(t) for t in rec["times"]]
    assert times[-1] < length + 1e-9, f"{sheet}: frames run past the state's length"
    if anim.get("loop"):
        assert abs(rec["length"] - length) < 1e-6 and length - times[-1] <= 1.0 / rec["fps"] + 1e-6, \
            f"{sheet}: the loop's length is not the rendered one"
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


def node_clip(node: str) -> str:
    leaf = node.rsplit("/", 1)[-1]
    for name, n in SHEET_NODE.items():
        if n == leaf:
            return name
    for name, n in FX_NODE.items():
        if n == leaf:
            return f"fx_{name}"
    raise AssertionError(node)


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
# the stage effects: one AnimationPlayer each
# ---------------------------------------------------------------------------


def stage_times(frames: dict, name: str) -> tuple[list[float], float]:
    """(the times the effect's frames show, the time it is gone)."""
    eff = frames["effects"][name]
    fps = float(eff["fps"])
    count = int(eff["count"])
    shown = [round(i / fps, 6) for i in range(count)]
    end = round(count / fps, 6)
    assert abs(end - float(eff["length"])) < 1e-6, f"{name}: frames and length disagree"
    return shown, end


def stage_reach(frames: dict, name: str) -> float:
    """The run, in scene px, from her chest to the guest seat the effect was
    drawn for (its `to` less its origin, at the combat scale)."""
    eff = frames["effects"][name]
    sc = frames["combat_scale"]
    (ox, oy), (tx, ty) = eff["origin"], eff["to"]
    assert oy == ty, f"{name}: the run is level in the sheet"
    return round((tx - ox) * sc, 4)


def stage_path(name: str) -> str:
    """The effect sprite's path from the scene root, where its player sits."""
    return f"{FACING}/{STAGE_GROUP}/{STAGE_NODE[name]}"


def stage_animation(frames: dict, clips: dict[str, Clip], name: str) -> str:
    """The effect's one-shot: shown from 0, stepped at its own fps, hidden at
    its end. Discrete, so it never fades in."""
    shown, end = stage_times(frames, name)
    node = stage_path(name)
    tracks = [
        Track(f"{node}:self_modulate", "color", [0.0, end], [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0)],
              [1.0, 1.0], interp=0, update=1),
        _steps(node, shown, clips[f"stage_{name}"].atlases),
    ]
    return animation_block(f"Animation_stage_{name}", name, end, False, tracks)


def stage_library(name: str) -> str:
    return (f'[sub_resource type="AnimationLibrary" id="AnimationLibrary_stage_{name}"]' + NL
            + "_data = {" + NL + f'&"{name}": SubResource("Animation_stage_{name}")' + NL + "}")


# ---------------------------------------------------------------------------
# the state machine (Varka's graph with `rejoice` where his has `ascension`)
# ---------------------------------------------------------------------------
SM_STATES = {"idle": (327, 153), "attack": (327, 64), "hurt": (327, 278), "death": (470, 153),
             "cast": (186, 64), "power": (470, 64), "idle_low": (327, 365), "rejoice": (470, 278)}
SM_ONE_SHOTS = ("attack", "hurt", "cast", "power", "rejoice")
SM_SOURCES = ("idle", "idle_low", "attack", "hurt", "cast", "power", "rejoice")
SM_TARGETS = ("attack", "hurt", "death", "cast", "power", "rejoice")


def xfade(src: str, dst: str) -> float:
    """Klee's cross-fades (the base skeletons' SpineAnimationMix): 0.05 s by
    default, 0.1 s from idle into a strike, ~0.03 s into a hurt, 0.1 s out of
    one, and a hurt cuts straight to death. The flourish starts from the idle
    like the attack, so it fades in like one."""
    if src == "hurt" and dst == "death":
        return 0.0
    if dst == "hurt":
        return 0.03
    if dst in ("attack", "rejoice") and src in ("idle", "idle_low"):
        return 0.1
    if src == "hurt" and dst == "idle":
        return 0.1
    return 0.05


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
    sm = ['[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_furina"]',
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

#: Bounds/CenterPos/IntentPos are her old rig's, kept as Varka kept his:
#: FurinaStagePlacement packs the guest line out from this box's edge, and
#: the stage's whole layout was tuned against it. Standing she is 220.2 px in
#: full, 214.7 in stance A (the manifest's `measure` and `stance_a`).
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
&"": SubResource("AnimationLibrary_furina")
}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_furina")
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


def _sprite(name: str, parent: str, clip: Clip, sc: float, *, shown: bool, unique: bool = False,
            material: str | None = None, meta: dict | None = None) -> str:
    ox, oy = clip.rec["origin"]
    lines = [f'[node name="{name}" type="Sprite2D" parent="{parent}"]']
    if unique:
        lines.append("unique_name_in_owner = true")
    if not shown:
        lines.append("self_modulate = Color(1, 1, 1, 0)")
    if material:
        lines.append(f'material = SubResource("{material}")')
    lines += [
        f"texture = {sub(clip.atlases[0])}",
        "centered = false",
        f"offset = {vec2((-ox, -oy))}",
        f"scale = {vec2((sc, sc))}",
    ]
    for k, v in (meta or {}).items():
        lines.append(f"metadata/{k} = {v}")
    return NL.join(lines)


def _material(mid: str, hexc: str, *, local: bool) -> str:
    lines = [f'[sub_resource type="ShaderMaterial" id="{mid}"]']
    if local:
        # one per Furina on the field: two can strike in two elements at once
        lines.append("resource_local_to_scene = true")
    lines += [f'shader = SubResource("{SHADER_ID}")',
              f"shader_parameter/{ELEMENT_PARAM} = {color(hex_color(hexc))}"]
    return NL.join(lines)


def stage_material_id(name: str) -> str:
    return f"ShaderMaterial_{name}"


def material_blocks(frames: dict) -> list[str]:
    code = SHADER_CODE.replace("\\", "\\\\").replace('"', '\\"')
    out = [NL.join([f'[sub_resource type="Shader" id="{SHADER_ID}"]', f'code = "{code}"']),
           _material(MATERIAL_ID, HYDRO_HEX, local=True)]
    for name in STAGE_EFFECTS:
        out.append(_material(stage_material_id(name), frames["effects"][name]["tint"], local=False))
    return out


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
    assert tuple(frames["effects"]) == STAGE_EFFECTS, "the manifest's stage effects changed"

    subs = [atlas_block(a) for c in clips.values() for a in c.atlases]
    subs += material_blocks(frames)
    subs.append(animation_block("Animation_reset", None, 0.001, False, reset_tracks(anims, clips)))
    for name in ANIMATION_ORDER:
        anim, tracks = anims[name]
        subs.append(animation_block(f"Animation_{name}", name, float(anim["length"]),
                                    bool(anim.get("loop")), tracks))
    lib = sorted(["RESET", *ANIMATION_ORDER], key=lambda n: (n != "RESET", n))
    subs.append('[sub_resource type="AnimationLibrary" id="AnimationLibrary_furina"]' + NL
                + "_data = {" + NL
                + ("," + NL).join(f'&"{n}": SubResource("Animation_{"reset" if n == "RESET" else n}")' for n in lib)
                + NL + "}")
    for name in STAGE_EFFECTS:
        subs.append(stage_animation(frames, clips, name))
        subs.append(stage_library(name))
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
        '[node name="FurinaCombat" type="Node2D"]',
        '[node name="Visuals" type="Node2D" parent="."]\nunique_name_in_owner = true',
        '[node name="Facing" type="Node2D" parent="Visuals"]\nunique_name_in_owner = true',
        _shadow_sprite(FACING, shadow, shadow["combat"], SHADOW_ID),
        f'[node name="Model" type="Node2D" parent="{FACING}"]',
    ]
    for name in spec["model"]["sheets"]:
        nodes.append(_sprite(SHEET_NODE[name], MODEL, clips[name], sc, shown=name == "idle"))
    for clip, node in FX_NODE.items():
        nodes.append(_sprite(node, MODEL, clips[f"fx_{clip}"], sc, shown=False, unique=True,
                             material=MATERIAL_ID, meta={"rest_element": f'"{REST_ELEMENT}"'}))
    # The stage effects: drawn over her, from her chest, under %Facing so a
    # turned Furina throws them the other way.
    group = f"{FACING}/{STAGE_GROUP}"
    nodes.append(f'[node name="{STAGE_GROUP}" type="Node2D" parent="{FACING}"]\n'
                 f"unique_name_in_owner = true\n"
                 f"position = {vec2(frames['stance_a']['chest_px'])}")
    for name in STAGE_EFFECTS:
        meta = {"effect": f'"{name}"'}
        if name in REACHING:
            meta["reach"] = fnum(stage_reach(frames, name))
        nodes.append(_sprite(STAGE_NODE[name], group, clips[f"stage_{name}"], sc, shown=False, unique=True,
                             material=stage_material_id(name), meta=meta))
    nodes.append(TAIL_NODES)
    # One player per effect, beside the state machine's: a child of the root,
    # so its tracks are the root's paths, as the main player's are.
    for name in STAGE_EFFECTS:
        nodes.append(NL.join([
            f'[node name="{STAGE_PLAYER[name]}" type="AnimationPlayer" parent="."]',
            "unique_name_in_owner = true",
            "libraries = {",
            f'&"": SubResource("AnimationLibrary_stage_{name}")',
            "}",
        ]))
    for n in nodes:
        out += [n, ""]
    return NL.join(out).rstrip(NL) + NL


# ---------------------------------------------------------------------------
# the merchant scene
# ---------------------------------------------------------------------------


def render_merchant_scene(frames: dict | None = None) -> str:
    """Furina at the shop: stance B, the near hand on her hip and the far
    hand presenting the wares, breathing on a loop. Varka's shape
    (tools/varka_rig/rig.py render_merchant_scene): a bare Node2D root, the
    shadow first so it draws behind, the sheet sprite at the merchant scale
    with its feet on the origin, and an autoplaying AnimationPlayer -- no
    Spine and no script (MerchantSpineBindingPatch skips the binding)."""
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
        '[node name="FurinaMerchant" type="Node2D"]', "",
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

