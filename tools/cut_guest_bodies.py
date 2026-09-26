"""Cut the eight Guest Stars' stage bodies from their Wish renders.

The Guest Cast (2026-09-25, review/active/furina-guest-batch-2026-09-25.md)
put eight Fontaine characters on Furina's stage as performers. Until this tool
each one wore the base game's Osty rig. This gives them what the Salon trio
has: a pre-scaled sprite and a scene with the trio's four animations.

Produces the gitignored art (Tier F, private builds only):

    ImageGen/images/furina/salon/guest_<name>.png   (one per guest)
    ImageGen/images/furina/salon/guests.json        (sizes, the shape of
                                                     members.json)

and the git-tracked scenes:

    klee-mod/pck-src/furina/model/guest_<name>.tscn

from art/raw/Character_<Name>_Full_Wish.png -- each guest's own transparent
full-body Wish render, the file the `proto_fs_guest_star_<name>` r2 candidate
rows in art/SOURCES.tsv were fetched from. The render's own alpha is the
matte: no polygon, no keying. The trio's tool (tools/cut_salon_members.py)
stays as it is; one producer per out-path.

HEIGHT. The guests are people standing beside Furina, so they are sized off
HER body, not off the trio's 144 px creatures: Furina's combat scene
(klee-mod/pck-src/furina/model/combat.tscn) is 280 px tall (Bounds offset_top
-280, body layer 280 px), and a guest is 80% of that, 224 px. The WHOLE alpha
bounding box is scaled to that height, so a render whose splash FX reach above
the head or below the feet (every Wish render carries some) shows a smaller
figure inside a 224 px sprite. Nothing is cropped off: no knees, no props.

EDGES. Resampled in PREMULTIPLIED alpha, so a transparent pixel's colour
cannot bleed into its neighbours as a fringe, then every pixel under
ALPHA_FLOOR is cleared to transparent black. The bounding box is measured at
BBOX_ALPHA so a near-invisible haze does not widen the crop.

SCENES. One template (SCENE_TEMPLATE below), filled per guest: the trio's
usher.tscn with the Rig at half the sprite height, Bounds the sprite's width
and height, and the animation offsets scaled by TARGET_H / 144.

`--art-root` points the source and the ImageGen output at the art-bearing
main checkout (a worktree has no ImageGen tree and must not link one); the
scenes are always written under this checkout.

Usage: .venv/Scripts/python tools/cut_guest_bodies.py [--check] [--art-root PATH]
"""
from __future__ import annotations

import argparse
import filecmp
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_REL = Path("art") / "raw"
OUT_REL = Path("ImageGen") / "images" / "furina" / "salon"
SCENE_DIR = ROOT / "klee-mod" / "pck-src" / "furina" / "model"
FURINA_SCENE = SCENE_DIR / "combat.tscn"

# The eight guests in StagePerformer order (FurinaStage.cs). The key is the
# file stem; the value is the wiki name in the render's file name.
GUESTS = {
    "neuvillette": "Neuvillette",
    "clorinde": "Clorinde",
    "navia": "Navia",
    "chevreuse": "Chevreuse",
    "wriothesley": "Wriothesley",
    "sigewinne": "Sigewinne",
    "charlotte": "Charlotte",
    "lynette": "Lynette",
}

# Furina's body height in creature space (combat.tscn Bounds, -280..0). Read
# back from the scene on every run so the 80% cannot drift from her.
FURINA_BODY_H = 280
GUEST_SHARE = 0.8
TARGET_H = 224  # round(GUEST_SHARE * FURINA_BODY_H)

# The trio's height, which the usher.tscn animation offsets were authored at.
TRIO_H = 144

BBOX_ALPHA = 16    # alpha >= this counts toward the crop box
ALPHA_FLOOR = 8    # alpha below this is cleared after the resize


def source_path(art_root: Path, name: str) -> Path:
    return art_root / RAW_REL / f"Character_{GUESTS[name]}_Full_Wish.png"


def furina_body_height() -> int:
    """Furina's scene height, from her Bounds node."""
    text = FURINA_SCENE.read_text(encoding="utf-8")
    block = text[text.index('[node name="Bounds"'):]
    top = next(line for line in block.splitlines()
               if line.startswith("offset_top = "))
    return round(-float(top.split("=")[1]))


def _resize_premultiplied(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """LANCZOS in premultiplied space; returns float RGBA in 0..255."""
    a = rgba[..., 3:4] / 255.0
    pre = rgba[..., :3] * a
    chans = [pre[..., i] for i in range(3)] + [rgba[..., 3]]
    out = [np.asarray(Image.fromarray(c.astype(np.float32), "F")
                      .resize(size, Image.LANCZOS)) for c in chans]
    alpha = np.clip(out[3], 0, 255)
    safe = np.where(alpha > 0, alpha / 255.0, 1.0)
    rgb = np.stack([np.clip(out[i] / safe, 0, 255) for i in range(3)], -1)
    return np.concatenate([rgb, alpha[..., None]], -1)


def cut_one(src: Image.Image) -> Image.Image:
    rgba = np.asarray(src.convert("RGBA")).astype(np.float64)
    mask = Image.fromarray(((rgba[..., 3] >= BBOX_ALPHA) * 255).astype(np.uint8))
    box = mask.getbbox()
    if box is None:
        raise SystemExit("render has no opaque pixels")
    x0, y0, x1, y1 = box
    crop = rgba[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    size = (max(1, round(w * TARGET_H / h)), TARGET_H)
    out = _resize_premultiplied(crop, size)
    clear = out[..., 3] < ALPHA_FLOOR
    out[clear] = 0
    return Image.fromarray(np.rint(out).astype(np.uint8), "RGBA")


def build_art(art_root: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name in GUESTS:
        src = source_path(art_root, name)
        if not src.exists():
            raise SystemExit(f"source missing: {src}")
        sprite = cut_one(Image.open(src))
        path = out_dir / f"guest_{name}.png"
        sprite.save(path)
        meta[name] = {"file": path.name, "w": sprite.width, "h": sprite.height}
        fill = (np.asarray(sprite)[..., 3] > 128).mean()
        print(f"  {name:12s} {sprite.width:3d}x{sprite.height:3d}  "
              f"fill {fill * 100:.0f}%")
    (out_dir / "guests.json").write_text(
        json.dumps({"target_h": TARGET_H, "guests": meta}, indent=2),
        encoding="utf-8")
    return meta


# --------------------------------------------------------------- scenes --

def _n(v: float) -> str:
    """A Godot scene number: integers bare, else one decimal."""
    v = round(v, 1)
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def _vec(x: float, y: float) -> str:
    return f"Vector2({_n(x)}, {_n(y)})"


def scene_text(name: str, w: int, h: int) -> str:
    """usher.tscn, re-proportioned for a w x h sprite."""
    k = h / TRIO_H
    rest = -h / 2

    def at(dx=0.0, dy=0.0):
        return _vec(dx * k, rest + dy * k)

    return SCENE_TEMPLATE.format(
        name=name,
        Title=name.capitalize(),
        rest=at(),
        idle=", ".join(at(dy=d) for d in (0, -3, 0, 1, 0)),
        attack=", ".join(at(dx=d) for d in (0, 30, -4, 0)),
        hurt=", ".join(at(dx=d) for d in (0, -8, 6, -3, 2, 0)),
        death=", ".join(at(dy=d) for d in (0, 10)),
        half_w=_n(w / 2),
        top=_n(-h),
    )


def build_scenes(meta: dict, scene_dir: Path) -> None:
    scene_dir.mkdir(parents=True, exist_ok=True)
    for name, m in meta.items():
        (scene_dir / f"guest_{name}.tscn").write_text(
            scene_text(name, m["w"], m["h"]), encoding="utf-8", newline="\n")


# ----------------------------------------------------------------- main --

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild to a temp dir and diff against shipped files")
    ap.add_argument("--art-root", default=str(ROOT),
                    help="checkout holding art/raw and ImageGen")
    args = ap.parse_args()
    art_root = Path(args.art_root).resolve()
    out_dir = art_root / OUT_REL

    measured = furina_body_height()
    if measured != FURINA_BODY_H or round(GUEST_SHARE * measured) != TARGET_H:
        raise SystemExit(
            f"Furina's scene is {measured} px tall; FURINA_BODY_H/TARGET_H "
            f"({FURINA_BODY_H}/{TARGET_H}) are stale")

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            meta = build_art(art_root, tmp / "art")
            build_scenes(meta, tmp / "scenes")
            bad = []
            for produced, shipped_dir in (
                    *((p, out_dir) for p in (tmp / "art").iterdir()),
                    *((p, SCENE_DIR) for p in (tmp / "scenes").iterdir())):
                shipped = shipped_dir / produced.name
                if not shipped.exists():
                    bad.append(f"MISSING on disk: {shipped}")
                elif not filecmp.cmp(produced, shipped, shallow=False):
                    bad.append(f"DIFFERS: {shipped}")
            for line in bad:
                print("  " + line)
            print("byte-identical" if not bad else f"{len(bad)} mismatch(es)")
            return 1 if bad else 0

    print(f"{art_root / RAW_REL} -> {out_dir}")
    meta = build_art(art_root, out_dir)
    build_scenes(meta, SCENE_DIR)
    print(f"scenes -> {SCENE_DIR}")
    return 0


SCENE_TEMPLATE = """\
[gd_scene load_steps=22 format=3]

[ext_resource type="Texture2D" path="res://furina/salon/guest_{name}.png" id="1_{name}"]

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

[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = -{half_w}
offset_top = {top}
offset_right = {half_w}
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


if __name__ == "__main__":
    sys.exit(main())
