"""The guest stars' effects, one scene each: manifest -> guest_fx_<name>.tscn.

Furina's plan item "guest-star pizazz" ([USER]: "unique particle effects or
similar for each guest"; review/active/furina-guest-fx-2026-10-16.md). Each
guest plays one short effect when it acts (or, for Navia, Neuvillette and
Chevreuse, when its line fires). tools/char_render/fx.py draws them
(GUEST_EFFECTS), pack.py packs them into the manifest's `guest_fx` block, and
this writes one small scene per guest that KleeMod.Vfx.FurinaGuestFx
instantiates on the creature it plays on -- an enemy, Furina or the guest --
and frees when it ends. A scene of its own, not a node on Furina's rig as the
stage effects are, because most of them play on enemies, whose scenes are
the base game's, and an effect to ALL plays once per enemy at once.

THE SCENE CONTRACT (FurinaGuestFx reads it):

  GuestFx (Node2D, the root)      metadata/guest, metadata/anchor ("feet" or
                                  "center"), metadata/length (seconds)
    %Fx (Sprite2D)                the frames, hidden at rest, its origin on
                                  the root's, on a ShaderMaterial wearing the
                                  manifest tint (the element shader)
    %FxPlayer (AnimationPlayer)   one animation named for the guest, which it
                                  autoplays: shown from 0, stepped at the
                                  effect's fps, hidden at its end

Byte-identical on every run; `python -m tools.furina_rig gen` writes them.
"""
from __future__ import annotations

from tools.furina_rig.rig import FRAME_DIR, MODEL_DIR, NL, SHADER_CODE, Track, animation_block, atlas_block, \
    clip_of, color, fnum, hex_color, load_frames, sub, vec2

ROOT_NODE = "GuestFx"
SPRITE = "Fx"
PLAYER = "FxPlayer"
SHADER_ID = "Shader_element"
MATERIAL_ID = "ShaderMaterial_tint"
ELEMENT_PARAM = "element"
ANCHORS = ("feet", "center")


def scene_path(name: str):
    return MODEL_DIR / f"guest_fx_{name}.tscn"


def times_of(rec: dict) -> tuple[list[float], float]:
    """(the times the effect's frames show, the time it is gone)."""
    fps = float(rec["fps"])
    count = int(rec["count"])
    end = round(count / fps, 6)
    assert abs(end - float(rec["length"])) < 1e-6, "frames and length disagree"
    return [round(i / fps, 6) for i in range(count)], end


def scene_text(name: str, rec: dict, sc: float) -> str:
    assert rec["anchor"] in ANCHORS, name
    clip = clip_of(name, rec, 1)
    shown, end = times_of(rec)
    anim = animation_block(f"Animation_{name}", name, end, False, [
        Track(f"{SPRITE}:self_modulate", "color", [0.0, end], [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0)],
              [1.0, 1.0], interp=0, update=1),
        Track(f"{SPRITE}:texture", "res", shown, [sub(a) for a in clip.atlases], [1.0] * len(shown),
              interp=0, update=1),
    ])
    code = SHADER_CODE.replace("\\", "\\\\").replace('"', '\\"')
    subs = [atlas_block(a) for a in clip.atlases]
    subs += [
        NL.join([f'[sub_resource type="Shader" id="{SHADER_ID}"]', f'code = "{code}"']),
        NL.join([f'[sub_resource type="ShaderMaterial" id="{MATERIAL_ID}"]',
                 f'shader = SubResource("{SHADER_ID}")',
                 f"shader_parameter/{ELEMENT_PARAM} = {color(hex_color(rec['tint']))}"]),
        anim,
        f'[sub_resource type="AnimationLibrary" id="AnimationLibrary_{name}"]' + NL
        + "_data = {" + NL + f'&"{name}": SubResource("Animation_{name}")' + NL + "}",
    ]
    out = [f"[gd_scene load_steps={len(clip.pages) + len(subs) + 1} format=3]", ""]
    for ext_id, file in clip.pages:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{file}" id="{ext_id}"]')
    out.append("")
    for s in subs:
        out += [s, ""]
    ox, oy = rec["origin"]
    nodes = [
        NL.join([f'[node name="{ROOT_NODE}" type="Node2D"]',
                 f'metadata/guest = "{name}"',
                 f'metadata/anchor = "{rec["anchor"]}"',
                 f"metadata/length = {fnum(end)}"]),
        NL.join([f'[node name="{SPRITE}" type="Sprite2D" parent="."]',
                 "unique_name_in_owner = true",
                 "self_modulate = Color(1, 1, 1, 0)",
                 f'material = SubResource("{MATERIAL_ID}")',
                 f"texture = {sub(clip.atlases[0])}",
                 "centered = false",
                 f"offset = {vec2((-ox, -oy))}",
                 f"scale = {vec2((sc, sc))}"]),
        NL.join([f'[node name="{PLAYER}" type="AnimationPlayer" parent="."]',
                 "unique_name_in_owner = true",
                 "libraries = {",
                 f'&"": SubResource("AnimationLibrary_{name}")',
                 "}",
                 f'autoplay = "{name}"']),
    ]
    for n in nodes:
        out += [n, ""]
    return NL.join(out).rstrip(NL) + NL


def render_guest_fx(frames: dict | None = None) -> dict[str, str]:
    """{guest: scene text} for every guest effect in the manifest."""
    frames = frames or load_frames()
    sc = frames["combat_scale"]
    return {name: scene_text(name, rec, sc) for name, rec in frames.get("guest_fx", {}).items()}
