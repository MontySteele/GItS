#!/usr/bin/env python3
"""Generate every kit's card trail scene (the streak a played card leaves).

[USER], 2026-10-23: "Card trail - can we make our own trails?" Each kit's
trail now wears that kit's card colour (`klee-mod/KleeCode/CardFrameColors.cs`,
the `DeckEntry` colour of each `Tint` row), where before every kit borrowed a
base character's trail (Klee the Ironclad's, Yae the Necrobinder's, the other
three the Defect's).

THE SHAPE IS THE BASE GAME'S, UNCHANGED. `TEMPLATE` below is
`res://scenes/vfx/card_trail_necrobinder.tscn` as read out of
`SlayTheSpire2.pck` (v0.107.1, 2026-10-23, `tools/probe_spine_pck/pck_read.py`)
with three edits: the scene's own `uid` is dropped (it would collide with the
base scene's), the root is renamed per kit, and every colour is a slot. The
five base trails differ ONLY in those colours (and their random resource ids),
so nothing about the motion, widths or particle counts is ours.

WHY THIS SCENE REFERENCES BASE-GAME SCRIPTS. `NCardTrailVfx.Create` does
`GetScene(path).Instantiate<NCardTrailVfx>()` -- it casts -- and each trail
line is an `NCardTrail` (a `Line2D` whose `_Process` lays the points down), so
a script-less copy would throw at the cast or draw no line. The scripts,
textures and the additive material stay at their `res://` paths in the game's
own pack (`scene_deps.BASE_GAME_RESOURCES` lists them); nothing of the base
game is copied into ours. Measured 2026-10-23 on MegaDot 4.5.1 headless: a
scratch project holding only this scene imports and exports with a clean
`godot_log_sweep` and the pack carries the `.tscn` alone, byte-identical.

THE COLOURS. One kit colour C (hue h, saturation s) drives every slot, keeping
the base trail's structure: a saturated outer line, a lighter inner core, the
card-silhouette glows near C, and the big-spark ramp fading from a bright C to
a dark C. Alphas are the base scene's. The little sparks keep the base
near-white head and fade to the kit's inner colour instead of yellow.

Usage:
    .venv/Scripts/python tools/gen_card_trails.py [--check]

Writes `klee-mod/pck-src/<kit>/vfx/card_trail.tscn`; `--check` exits 1 if a
committed scene differs from what this would write.
"""
from __future__ import annotations

import argparse
import colorsys
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "klee-mod" / "KleeCode" / "CardFrameColors.cs"
KITS = ("klee", "furina", "kokomi", "varka", "yae")


def out_path(kit: str) -> Path:
    return ROOT / "klee-mod" / "pck-src" / kit / "vfx" / "card_trail.tscn"


def res_path(kit: str) -> str:
    """The path each character's `CustomTrailPath` returns."""
    return f"res://{kit}/vfx/card_trail.tscn"


def kit_colours(table: Path = TABLE) -> dict[str, str]:
    """kit -> its DeckEntry hex, read from CardFrameColors.cs's Tint rows."""
    text = table.read_text(encoding="utf-8")
    rows = dict(re.findall(
        r'new\("([a-z]+)",\s*[0-9.]+f,\s*[0-9.]+f,\s*[0-9.]+f,\s*new Color\("([0-9A-Fa-f]{6})"\)',
        text))
    missing = set(KITS) - set(rows)
    if missing:
        raise SystemExit(f"{table}: no Tint row for {sorted(missing)}")
    return {k: rows[k].upper() for k in KITS}


def _hsv(h: float, s: float, v: float) -> tuple[float, float, float]:
    return colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))


def palette(hex_colour: str) -> dict[str, tuple[float, float, float]]:
    """Every colour slot of the trail, from one kit colour."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, s, _ = colorsys.rgb_to_hsv(r, g, b)
    # Additive lines wash a pale colour out to white, so a pale kit (Kokomi's
    # pearl coral, saturation 0.42) is drawn at 0.55: still pale, still coral.
    s = max(s, 0.55)
    return {
        # The two lines: saturated outer, a lighter core (base: Ironclad red
        # over yellow, Necrobinder pink over peach, Defect blue over cyan).
        "outer": _hsv(h, s, 1.0),
        "inner": _hsv(h + 0.02, s * 0.55, 1.0),
        # The card-silhouette glows behind the card.
        "glow_a": _hsv(h, s, 0.95),
        "glow_b": _hsv(h + 0.02, s * 0.75, 0.9),
        # The big-spark ramp: bright, then fading darker.
        "ramp0": _hsv(h, s * 0.8, 1.0),
        "ramp1": _hsv(h, s, 0.82),
        "ramp2": _hsv(h, s, 0.55),
        "ramp3": _hsv(h, s, 0.6),
        # The little sparks: the base's near-white head, then the core colour.
        "spark_head": (1.0, 0.976442, 0.851033),
        "spark_tail": _hsv(h + 0.02, s * 0.55, 1.0),
    }


def _c(rgb: tuple[float, float, float]) -> str:
    return ", ".join(f"{x:.6g}" for x in rgb)


TEMPLATE = """\
[gd_scene load_steps=15 format=3]

[ext_resource type="Script" uid="uid://bb3fwupsnhf43" path="res://src/Core/Nodes/Vfx/NCardTrailVfx.cs" id="1_0fgej"]
[ext_resource type="Texture2D" uid="uid://b7vqn8f75qh4x" path="res://images/packed/vfx/trail.png" id="2_360vg"]
[ext_resource type="Script" uid="uid://cl44l3vqar6tb" path="res://src/Core/Nodes/Vfx/NCardTrail.cs" id="3_83agq"]
[ext_resource type="Texture2D" uid="uid://co4rdu87x6mcr" path="res://images/packed/vfx/trail2.png" id="4_2sraa"]
[ext_resource type="Texture2D" uid="uid://1wc3p3n7fakr" path="res://images/vfx/brush_particle_2.png" id="5_h5m5l"]
[ext_resource type="Texture2D" uid="uid://bexbor35725ag" path="res://images/vfx/vfx_ghostly_power_up/sparkle.png" id="6_w5ewp"]
[ext_resource type="Texture2D" uid="uid://bk4gpfmy1awke" path="res://images/packed/vfx/small_card_silhouette.png" id="7_myqnw"]
[ext_resource type="CanvasItemMaterial" uid="uid://c4ycqv0gdxvmr" path="res://themes/canvas_item_material_additive_shared.tres" id="shared_additive_mat"]

[sub_resource type="Curve" id="Curve_0ojw2"]
_data = [Vector2(0, 0.111037), 0.0, 0.0, 0, 0, Vector2(0.839578, 0.663793), -2.61019, -2.61019, 0, 0, Vector2(0.922468, 0.94341), 0.0, 0.0, 0, 0, Vector2(1, 0.685611), 0.0, 0.0, 0, 0]
point_count = 4

[sub_resource type="Gradient" id="Gradient_6eyfw"]
offsets = PackedFloat32Array(0, 0.141431, 0.522463)
colors = PackedColorArray(0, 0, 0, 0, 0.25, 0.25, 0.25, 0.305882, 1, 1, 1, 1)

[sub_resource type="Curve" id="Curve_eaky7"]
_data = [Vector2(0, 0), 0.0, 0.0, 0, 0, Vector2(0.801075, 0.571397), -3.15833, -3.15833, 0, 0, Vector2(0.900922, 0.367031), 0.0, 0.0, 0, 0, Vector2(0.938291, 0.930834), 0.0, 0.0, 0, 0, Vector2(1, 0.742201), 0.0, 0.0, 0, 0]
point_count = 5

[sub_resource type="Gradient" id="Gradient_fdg7u"]
offsets = PackedFloat32Array(0.261231, 0.647255, 0.821549)
colors = PackedColorArray(0, 0, 0, 0, 0.25, 0.25, 0.25, 0.305882, 1, 1, 1, 1)

[sub_resource type="Gradient" id="Gradient_miu0s"]
offsets = PackedFloat32Array(0, 0.554377, 0.806366, 1)
colors = PackedColorArray({ramp0}, 1, {ramp1}, 0.447059, {ramp2}, 0.482353, {ramp3}, 0)

[sub_resource type="Gradient" id="Gradient_ytddg"]
colors = PackedColorArray({spark_head}, 1, {spark_tail}, 0)

[node name="{root}" type="Node2D"]
show_behind_parent = true
script = ExtResource("1_0fgej")

[node name="Trails" type="Node2D" parent="."]

[node name="OuterTrail" type="Line2D" parent="Trails"]
modulate = Color({outer}, 0.752941)
material = ExtResource("shared_additive_mat")
width = 96.0
width_curve = SubResource("Curve_0ojw2")
default_color = Color(1, 1, 1, 0.752941)
gradient = SubResource("Gradient_6eyfw")
texture = ExtResource("2_360vg")
texture_mode = 2
joint_mode = 2
script = ExtResource("3_83agq")

[node name="InnerTrail" type="Line2D" parent="Trails"]
modulate = Color({inner}, 0.501961)
material = ExtResource("shared_additive_mat")
width = 64.0
width_curve = SubResource("Curve_eaky7")
gradient = SubResource("Gradient_fdg7u")
texture = ExtResource("4_2sraa")
texture_mode = 2
joint_mode = 2
script = ExtResource("3_83agq")

[node name="Sprites" type="Node2D" parent="."]

[node name="BigSparks" type="CPUParticles2D" parent="Sprites"]
material = ExtResource("shared_additive_mat")
amount = 64
lifetime = 2.0
randomness = 0.5
lifetime_randomness = 1.0
fract_delta = false
texture = ExtResource("5_h5m5l")
emission_shape = 3
emission_rect_extents = Vector2(24, 24)
direction = Vector2(5, -5)
gravity = Vector2(0, 0)
initial_velocity_min = 16.0
initial_velocity_max = 32.0
angular_velocity_min = -32.0
angular_velocity_max = 32.0
damping_min = 1.0
damping_max = 5.0
angle_min = -180.0
angle_max = 180.0
scale_amount_min = 0.2
scale_amount_max = 0.8
color_ramp = SubResource("Gradient_miu0s")

[node name="LittleSparks" type="CPUParticles2D" parent="Sprites"]
material = ExtResource("shared_additive_mat")
amount = 64
lifetime = 0.3
explosiveness = 0.35
randomness = 1.0
lifetime_randomness = 1.0
fract_delta = false
texture = ExtResource("6_w5ewp")
emission_shape = 3
emission_rect_extents = Vector2(24, 24)
particle_flag_align_y = true
direction = Vector2(0, -5)
gravity = Vector2(0, 1960)
initial_velocity_max = 480.0
angular_velocity_min = -50.0
angular_velocity_max = 50.0
angle_min = -180.0
angle_max = 180.0
scale_amount_min = 0.02
scale_amount_max = 0.05
color_ramp = SubResource("Gradient_ytddg")

[node name="Sprite2D2" type="Sprite2D" parent="Sprites"]
modulate = Color({glow_a}, 0.752941)
material = ExtResource("shared_additive_mat")
scale = Vector2(1.1, 1.054)
texture = ExtResource("7_myqnw")

[node name="Sprite2D3" type="Sprite2D" parent="Sprites"]
modulate = Color({glow_b}, 0.501961)
material = ExtResource("shared_additive_mat")
scale = Vector2(0.9, 0.9)
texture = ExtResource("7_myqnw")
"""


def _fill(template: str, **slots: str) -> str:
    out = template
    for key, value in slots.items():
        out = out.replace("{" + key + "}", value)
    leftover = re.findall(r"\{[a-z_0-9]+\}", out)
    if leftover:
        raise SystemExit(f"unfilled slots: {leftover}")
    return out


def render(kit: str, hex_colour: str) -> str:
    slots = {k: _c(v) for k, v in palette(hex_colour).items()}
    return _fill(TEMPLATE, root="CardTrail" + kit.capitalize(), **slots)


def plan() -> dict[Path, str]:
    return {out_path(kit): render(kit, hexc) for kit, hexc in kit_colours().items()}


def check() -> list[str]:
    problems = []
    for path, text in plan().items():
        rel = path.relative_to(ROOT).as_posix()
        if not path.exists():
            problems.append(f"missing {rel}")
        elif path.read_text(encoding="utf-8") != text:
            problems.append(f"{rel} differs from tools/gen_card_trails.py")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        problems = check()
        for p in problems:
            print(p)
        return 1 if problems else 0
    for path, text in plan().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
