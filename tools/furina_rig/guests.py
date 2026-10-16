"""The eleven guest stars' stage bodies, from their rendered stills.

Phase B of Furina's model art (review/active/furina-visual-paper-2026-10-13.md):
each guest stands as the still `tools/char_render` rendered from the guest's
official model, in a calm rest of their own, at Furina's px per inch. The
stills are Tier F (ImageGen/images/furina/model/guests/guest_<name>.png); the
manifest's `guests` block (tools/char_render/furina_frames.json) records each
one's texture size, feet anchor and measured heights, and is all this reads.

The scene is the Salon trio's (usher.tscn), as the flat 224 px cutouts'
scenes were (tools/cut_guest_bodies.py, which no longer writes them): the
same four states and keys, the motion offsets scaled by the guest's own
height over the trio's 144 px. What changed is where the body stands:

  * THE FEET ON THE ORIGIN. The still is drawn uncentred with its feet anchor
    at the Rig's origin, and the Rig rests at (0, 0), so a guest's height on
    screen is the height the renderer measured (`full_px`), not a fixed share
    of Furina's box. The motion pivots at the feet.
  * THE BOX IS THE STILL'S. Bounds is the still's width and its height above
    the feet, centred on the node: FurinaStagePlacement packs the line by
    each body's own Bounds width, so the still is centred across its box
    (its offset is half its width) rather than on its feet, which sit a few
    px off centre in a contrapposto.

Byte-identical on every run; `python -m tools.furina_rig gen` writes them.
"""
from __future__ import annotations

from tools.furina_rig.rig import MODEL_DIR, load_frames
from tools.klee_rig.rig import num

#: The trio's height, which the usher.tscn animation offsets were authored at.
TRIO_H = 144


def scene_path(name: str):
    return MODEL_DIR / f"guest_{name}.tscn"


def _n(v: float) -> str:
    """A Godot scene number: integers bare, else one decimal."""
    v = round(v, 1)
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def _vec(x: float, y: float) -> str:
    return f"Vector2({_n(x)}, {_n(y)})"


def geometry(rec: dict, sc: float) -> dict:
    """One guest's box in scene px: its height above the feet, its width,
    and the texture offset that centres the still across the box with its
    feet on the ground line."""
    w, _h = rec["size"]
    _fx, fy = rec["feet"]
    return {"height": round(fy * sc, 1), "width": round(w * sc, 1),
            "offset": (-w / 2, -fy)}


def scene_text(name: str, rec: dict, sc: float) -> str:
    g = geometry(rec, sc)
    k = g["height"] / TRIO_H

    def at(dx=0.0, dy=0.0):
        return _vec(dx * k, dy * k)

    return SCENE_TEMPLATE.format(
        name=name,
        Title=name.capitalize(),
        rest=at(),
        idle=", ".join(at(dy=d) for d in (0, -3, 0, 1, 0)),
        attack=", ".join(at(dx=d) for d in (0, 30, -4, 0)),
        hurt=", ".join(at(dx=d) for d in (0, -8, 6, -3, 2, 0)),
        death=", ".join(at(dy=d) for d in (0, 10)),
        offset=f"Vector2({num(g['offset'][0])}, {num(g['offset'][1])})",
        scale=f"Vector2({num(sc)}, {num(sc)})",
        left=_n(-g["width"] / 2),
        right=_n(g["width"] / 2),
        top=_n(-g["height"]),
    )


def render_guests(frames: dict | None = None) -> dict:
    """guest name -> its scene text, in the manifest's order."""
    frames = frames or load_frames()
    sc = frames["combat_scale"]
    return {name: scene_text(name, rec, sc) for name, rec in frames["guests"].items()}


SCENE_TEMPLATE = """\
[gd_scene load_steps=22 format=3]

[ext_resource type="Texture2D" path="res://furina/model/guests/guest_{name}.png" id="1_{name}"]

[sub_resource type="Animation" id="Animation_reset"]
length = 0.001
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0),
"transitions": PackedFloat32Array(1),
"update": 0,
"values": [{rest}]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:rotation")
tracks/1/interp = 1
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0),
"transitions": PackedFloat32Array(1),
"update": 0,
"values": [0.0]
}}
tracks/2/type = "value"
tracks/2/imported = false
tracks/2/enabled = true
tracks/2/path = NodePath("Visuals/Rig:modulate")
tracks/2/interp = 1
tracks/2/loop_wrap = true
tracks/2/keys = {{
"times": PackedFloat32Array(0),
"transitions": PackedFloat32Array(1),
"update": 0,
"values": [Color(1, 1, 1, 1)]
}}

[sub_resource type="Animation" id="Animation_idle"]
resource_name = "idle"
length = 3.0
loop_mode = 1
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 2
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.75, 1.5, 2.25, 3),
"transitions": PackedFloat32Array(1, 1, 1, 1, 1),
"update": 0,
"values": [{idle}]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:rotation")
tracks/1/interp = 2
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0, 0.75, 1.5, 2.25, 3),
"transitions": PackedFloat32Array(1, 1, 1, 1, 1),
"update": 0,
"values": [0.0, 0.018, 0.0, -0.018, 0.0]
}}

[sub_resource type="Animation" id="Animation_attack"]
resource_name = "attack"
length = 0.5
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.15, 0.35, 0.5),
"transitions": PackedFloat32Array(0.5, 1.6, 1, 1),
"update": 0,
"values": [{attack}]
}}

[sub_resource type="Animation" id="Animation_hurt"]
resource_name = "hurt"
length = 0.4
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.06, 0.14, 0.22, 0.32, 0.4),
"transitions": PackedFloat32Array(1, 1, 1, 1, 1, 1),
"update": 0,
"values": [{hurt}]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:modulate")
tracks/1/interp = 1
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0, 0.05, 0.35),
"transitions": PackedFloat32Array(1, 1, 1),
"update": 0,
"values": [Color(1, 1, 1, 1), Color(1, 0.45, 0.4, 1), Color(1, 1, 1, 1)]
}}

[sub_resource type="Animation" id="Animation_death"]
resource_name = "death"
length = 1.0
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:modulate")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.15, 1),
"transitions": PackedFloat32Array(1, 1, 1),
"update": 0,
"values": [Color(1, 1, 1, 1), Color(1, 0.62, 0.6, 1), Color(1, 1, 1, 0)]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:rotation")
tracks/1/interp = 1
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0, 1),
"transitions": PackedFloat32Array(1, 1),
"update": 0,
"values": [0.0, 0.22]
}}
tracks/2/type = "value"
tracks/2/imported = false
tracks/2/enabled = true
tracks/2/path = NodePath("Visuals/Rig:position")
tracks/2/interp = 1
tracks/2/loop_wrap = true
tracks/2/keys = {{
"times": PackedFloat32Array(0, 1),
"transitions": PackedFloat32Array(1, 1),
"update": 0,
"values": [{death}]
}}

[sub_resource type="AnimationLibrary" id="AnimationLibrary_{name}"]
_data = {{
&"RESET": SubResource("Animation_reset"),
&"attack": SubResource("Animation_attack"),
&"death": SubResource("Animation_death"),
&"hurt": SubResource("Animation_hurt"),
&"idle": SubResource("Animation_idle")
}}

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_attack"]
animation = &"attack"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_death"]
animation = &"death"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_hurt"]
animation = &"hurt"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_idle"]
animation = &"idle"

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_start_idle"]
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_hurt"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_hurt_idle"]
switch_mode = 2
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_death_end"]
switch_mode = 2
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_hurt_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_attack"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_attack_idle"]
switch_mode = 2
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_attack_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_{name}"]
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
transitions = ["Start", "idle", SubResource("Transition_start_idle"), "idle", "death", SubResource("Transition_idle_death"), "idle", "hurt", SubResource("Transition_idle_hurt"), "hurt", "idle", SubResource("Transition_hurt_idle"), "death", "End", SubResource("Transition_death_end"), "hurt", "death", SubResource("Transition_hurt_death"), "idle", "attack", SubResource("Transition_idle_attack"), "attack", "idle", SubResource("Transition_attack_idle"), "attack", "death", SubResource("Transition_attack_death")]

[node name="Guest{Title}Visuals" type="Node2D"]

[node name="Visuals" type="Node2D" parent="."]
unique_name_in_owner = true

[node name="Rig" type="Node2D" parent="Visuals"]
position = {rest}

[node name="Body" type="Sprite2D" parent="Visuals/Rig"]
texture = ExtResource("1_{name}")
centered = false
offset = {offset}
scale = {scale}

[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = {left}
offset_top = {top}
offset_right = {right}
offset_bottom = 0.0
mouse_filter = 2

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {{
&"": SubResource("AnimationLibrary_{name}")
}}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_{name}")
anim_player = NodePath("../AnimationPlayer")
"""

