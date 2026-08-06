"""Track AN spike (2026-08-06): build a Skeleton2D+Polygon2D combat rig for
Kokomi -- OUTSIDE the repo -- and everything needed to validate it offline.

WHAT THIS IS FOR
    Path B (Godot-native Skeleton2D) has zero working examples anywhere in
    reach (animation-capability-memo.md section 2). This spike builds one, as a
    scratch Godot project shaped exactly like the tools/probe_spine_pck
    apparatus, so the same two MegaDot steps tools/build_pck.ps1 runs can be
    run over it and the pack read back. Nothing here is wired into the
    pipeline; Path C stays the shipped fallback.

THE ATTACHED IDEA: COMPUTED WEIGHTS FROM LAYER MASKS
    Instead of hand-painting Polygon2D vertex weights in the editor GUI (the
    reproducibility problem F1 section 6 item 11 records), this tool derives
    them: each rig region has a LAYER MASK image; every mask is Gaussian-
    blurred into a soft ownership field; a vertex's weight for bone B is the
    normalized blurred-mask value of B's layer at that vertex. Blur width is
    the blend zone. The whole rig is therefore regenerable from committed
    code + mask images -- the same invariant Path C's --check enforces.

KOKOMI HAS NO PATH C LAYERS (inventory finding, recorded in the spike memo).
    Klee and Furina have fence configs + cut layers; Kokomi has only the
    4900x5700 portrait cutout (ImageGen/images/kokomi/model/
    kokomi_portrait_cutout.png, Tier F, machine-local) and a static 240x280
    combat_model.png. So this tool SYNTHESIZES spike-grade masks from the
    cutout's alpha (horizontal bands with overlap). They stand in for the
    fence-cut masks a real Path C character already has; the weight
    computation is identical either way. The masks are spike apparatus, not
    shipped art.

WHAT IT WRITES  (all under --out; REFUSED inside the repo -- the texture is
derived from Tier F pixels, which never enter the tracked tree)
    project.godot, export_presets.cfg   "strict" preset, byte-equivalent to
                                        the one tools/build_pck.ps1 writes
    kokomi_spike/kokomi_tex.png         downscaled cutout (single atlas page)
    kokomi_spike/masks/mask_<r>.png     the four synthesized layer masks
    kokomi_spike/combat.tscn            the rig scene, shaped like the shipped
                                        furina/model/combat.tscn contract:
                                        root/Visuals/Facing/Rig + Bounds +
                                        CenterPos + IntentPos +
                                        AnimationPlayer + AnimationTree
                                        (5 clips, same 4-state machine) --
                                        but Rig holds Skeleton2D + 4 weighted
                                        Polygon2D instead of 4 Sprite2D
    spike_check.gd                      SceneTree script: loads + instantiates
                                        the scene in-project, prints observables
    packcheck/project.godot             a SECOND minimal project that mounts
    packcheck/pack_check.gd             the exported .pck and loads the
                                        CONVERTED scene out of it
    preview_deform.png                  offline LBS render, rest|posed, to
                                        eyeball tearing on cut-from-splash art

Usage (from the repo root; scratch dir must be outside the repo):
    python tools/skeleton2d_spike/gen_kokomi_rig.py --out <scratch> \
        [--cutout <path to kokomi_portrait_cutout.png>]
Then: powershell -File tools/skeleton2d_spike/build_spike_pck.ps1 -ProjectDir <scratch>
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

# ---------------------------------------------------------------------------
# Rig parameters. Fractions are of the subject's alpha-bbox HEIGHT, measured
# from the TOP. Bands overlap on purpose: the overlap is the blend zone the
# blurred masks turn into split weights.
# ---------------------------------------------------------------------------
DOWNSCALE = 8            # 4900x5700 -> ~613x713 texture; combat box is 240x280
ALPHA_THRESHOLD = 10     # alpha above this counts as subject
REGIONS = [              # (name, band_top_frac, band_bot_frac, bone_path)
    ("head", 0.00, 0.26, "Hips/Chest/Neck/Head"),
    ("chest", 0.22, 0.50, "Hips/Chest"),
    ("hips", 0.46, 0.74, "Hips"),
    ("legs", 0.70, 1.00, "Hips/Legs"),
]
# Draw order, back to front (legs behind skirt behind chest behind head).
DRAW_ORDER = ["legs", "hips", "chest", "head"]
JOINTS = {               # y-fraction from top of subject bbox
    "hip": 0.70, "chest": 0.44, "neck": 0.24, "head": 0.10, "feet": 1.00,
}
BLUR_FRAC = 0.045        # Gaussian sigma as a fraction of subject height
ROW_STEP_FRAC = 1 / 44   # mesh outline sampling: one row pair per ~2.3% height
SPAN_PAD_PX = 2          # dilate each row span so the outline clears the art
TARGET_BODY_H = 272.0    # feet-to-crown in rig units (280 box, 8px headroom)

PROJECT_GODOT = """; Throwaway project for the Track AN Skeleton2D spike. Its only job is to
; import a PNG and export a pack, exactly as tools/build_pck.ps1's scratch
; project does.
config_version=5

[application]

config/name="SkeletonSpike"
"""

# Byte-equivalent to the preset tools/build_pck.ps1 writes (same source as the
# spine probe's "strict" arm): all core-type resources, no include_filter.
EXPORT_PRESETS ="""[preset.0]

name="strict"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="spike_strict.pck"
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

binary_format/embed_pck=false
"""

SPIKE_CHECK_GD = """# Track AN spike: in-project observables. Run with
#   MegaDot --headless --path <scratch> --script res://spike_check.gd
# Checks run on the FIRST PROCESS FRAME, not in _initialize: the root window
# only enters the tree when iteration starts, and Skeleton2D refuses
# get_bone_count() outside the tree (measured).
extends SceneTree

var _done := false


func _process(_delta: float) -> bool:
	if _done:
		return true
	_done = true
	var ps: PackedScene = load("res://kokomi_spike/combat.tscn")
	print("[spike] LOADED=", ps != null)
	if ps == null:
		quit(1)
		return true
	var scene_root := ps.instantiate()
	get_root().add_child(scene_root)
	print("[spike] ROOT=", scene_root.get_class(), " name=", scene_root.name)
	var rig := scene_root.get_node_or_null("Visuals/Facing/Rig")
	print("[spike] RIG=", rig != null)
	var skel := scene_root.get_node_or_null("Visuals/Facing/Rig/Skeleton2D") as Skeleton2D
	print("[spike] SKELETON=", skel != null,
			" bones=", skel.get_bone_count() if skel != null else -1,
			" rid_valid=", skel.get_skeleton().is_valid() if skel != null else false)
	var polys := 0
	for child in rig.get_children():
		if child is Polygon2D:
			polys += 1
			var p := child as Polygon2D
			var skel_ok := p.get_node_or_null(p.skeleton) != null
			var wsum_ok := true
			var bone_paths_ok := true
			for bi in p.get_bone_count():
				if p.get_bone_weights(bi).size() != p.polygon.size():
					wsum_ok = false
				if skel_ok and p.get_node_or_null(p.skeleton).get_node_or_null(p.get_bone_path(bi)) == null:
					bone_paths_ok = false
			print("[spike] POLY ", p.name, " verts=", p.polygon.size(),
					" bones=", p.get_bone_count(), " skeleton_resolves=", skel_ok,
					" bone_paths_resolve=", bone_paths_ok,
					" weight_arrays_match=", wsum_ok)
	print("[spike] POLY_COUNT=", polys)
	var ap := scene_root.get_node_or_null("AnimationPlayer") as AnimationPlayer
	print("[spike] ANIMS=", ap.get_animation_list() if ap != null else PackedStringArray())
	var at := scene_root.get_node_or_null("AnimationTree") as AnimationTree
	print("[spike] TREE=", at != null)
	if ap != null and skel != null:
		if at != null:
			at.active = false  # manual stepping below; the tree owns it in-game
		ap.play("idle")
		ap.advance(0.6)
		print("[spike] IDLE_ADVANCED chest_rot=", skel.get_node("Hips/Chest").rotation)
	print("[spike] done.")
	quit(0)
	return true
"""

PACK_CHECK_GD = """# Track AN spike: mounts the exported pack and loads the CONVERTED scene out
# of it -- the same resolution path the game's own pck mount uses. Run with
#   MegaDot --headless --path <scratch>/packcheck --script res://pack_check.gd
extends SceneTree


func _initialize():
	var pck := "PCK_PATH"
	var mounted := ProjectSettings.load_resource_pack(pck)
	print("[packcheck] PACK_MOUNTED=", mounted, " (", pck, ")")
	print("[packcheck] EXISTS=", ResourceLoader.exists("res://kokomi_spike/combat.tscn"))
	var ps: PackedScene = load("res://kokomi_spike/combat.tscn")
	print("[packcheck] LOADED=", ps != null)
	if ps != null:
		var root := ps.instantiate()
		print("[packcheck] ROOT=", root.get_class(), " name=", root.name)
		var skel := root.get_node_or_null("Visuals/Facing/Rig/Skeleton2D") as Skeleton2D
		print("[packcheck] SKELETON=", skel != null)
		# The binary .scn conversion must have carried the skinning data.
		for child in root.get_node("Visuals/Facing/Rig").get_children():
			if child is Polygon2D:
				var p := child as Polygon2D
				print("[packcheck] POLY ", p.name, " verts=", p.polygon.size(),
						" bones=", p.get_bone_count())
		root.queue_free()
	print("[packcheck] done.")
	quit(0)
"""

PACKCHECK_PROJECT = """; Minimal host project for pack_check.gd (Track AN spike).
config_version=5

[application]

config/name="SpikePackCheck"
"""


def refuse_inside_repo(out: str) -> None:
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.commonpath([os.path.abspath(out), repo]) == repo:
        print(f"REFUSED: --out {out} is inside the repo {repo}.", file=sys.stderr)
        print("The texture derives from Tier F pixels; they never enter the tree.",
              file=sys.stderr)
        raise SystemExit(2)


def alpha_bbox(a: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(a > ALPHA_THRESHOLD)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def fmt(v: float) -> str:
    """Compact float for .tscn text: 2 decimals, no trailing zeros."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def pv2(points) -> str:
    return "PackedVector2Array(" + ", ".join(
        f"{fmt(x)}, {fmt(y)}" for x, y in points) + ")"


def pf32(vals) -> str:
    return "PackedFloat32Array(" + ", ".join(fmt(v) for v in vals) + ")"


def build_masks(alpha: np.ndarray):
    """The synthesized layer masks: subject alpha cut into overlapping bands."""
    h = alpha.shape[0]
    masks = {}
    for name, top, bot, _bone in REGIONS:
        m = np.zeros_like(alpha)
        r0, r1 = int(top * h), int(math.ceil(bot * h))
        m[r0:r1] = alpha[r0:r1]
        masks[name] = m
    return masks


def weight_fields(masks: dict, h: int):
    """Blur each mask into a soft ownership field, then normalize per pixel."""
    sigma = max(2.0, BLUR_FRAC * h)
    blurred = {}
    for name, m in masks.items():
        img = Image.fromarray(m, mode="L").filter(ImageFilter.GaussianBlur(sigma))
        blurred[name] = np.asarray(img, dtype=np.float64)
    total = sum(blurred.values())
    total[total == 0] = 1.0
    return {n: b / total for n, b in blurred.items()}, sigma


def region_outline(mask: np.ndarray, h: int):
    """Row-span outline: for sampled rows, [min_x, max_x] of the mask, padded.
    Left edge top-to-bottom then right edge bottom-to-top -> one simple
    polygon per region. Spike-grade silhouette; concavities in x are bridged."""
    step = max(6, int(ROW_STEP_FRAC * h))
    rows_with = np.nonzero(mask.max(axis=1) > 127)[0]
    if rows_with.size == 0:
        return []
    r0, r1 = int(rows_with[0]), int(rows_with[-1])
    sample_rows = list(range(r0, r1, step)) + [r1]
    left, right = [], []
    for r in sample_rows:
        xs = np.nonzero(mask[r] > 127)[0]
        if xs.size == 0:
            continue
        left.append((float(xs[0] - SPAN_PAD_PX), float(r)))
        right.append((float(xs[-1] + SPAN_PAD_PX), float(r)))
    return left + right[::-1]


def bone_decl(name: str, parent: str, rel: tuple, length: float, angle: float) -> str:
    return (
        f'[node name="{name}" type="Bone2D" parent="{parent}"]\n'
        f"position = Vector2({fmt(rel[0])}, {fmt(rel[1])})\n"
        f"rest = Transform2D(1, 0, 0, 1, {fmt(rel[0])}, {fmt(rel[1])})\n"
        f"auto_calculate_length_and_angle = false\n"
        f"length = {fmt(length)}\n"
        f"bone_angle = {fmt(angle)}\n"
    )


def anim_value_track(idx: int, path: str, times, values, fmt_value) -> str:
    return (
        f'tracks/{idx}/type = "value"\n'
        f"tracks/{idx}/imported = false\n"
        f"tracks/{idx}/enabled = true\n"
        f'tracks/{idx}/path = NodePath("{path}")\n'
        f"tracks/{idx}/interp = 1\n"
        f"tracks/{idx}/loop_wrap = true\n"
        f"tracks/{idx}/keys = {{\n"
        f'"times": {pf32(times)},\n'
        f'"transitions": {pf32([1] * len(times))},\n'
        f'"update": 0,\n'
        f'"values": [{", ".join(fmt_value(v) for v in values)}]\n'
        f"}}\n"
    )


def build_animations(bone_rig_paths: dict) -> str:
    """Five clips + the shipped 4-state machine. Bone ROTATION tracks are the
    point: they only mean anything if the skeleton actually deforms the mesh."""
    rp = bone_rig_paths  # name -> full track path prefix
    # Bare scalars in a value track's "values" array MUST carry a decimal
    # point: "0" parses as an int Variant, the array becomes mixed int/float,
    # and interpolation silently yields 0.0 (measured on MegaDot 4.5).
    f = lambda v: str(float(v))  # noqa: E731
    vec = lambda v: f"Vector2({fmt(v[0])}, {fmt(v[1])})"  # noqa: E731
    col = lambda c: f"Color({', '.join(fmt(x) for x in c)})"  # noqa: E731

    out = ['[sub_resource type="Animation" id="Animation_reset"]', "length = 0.001"]
    i = 0
    for name in ("Hips", "Chest", "Neck", "Head", "Legs"):
        out.append(anim_value_track(i, f"{rp[name]}:rotation", [0], [0.0], f))
        i += 1
    out.append(anim_value_track(i, "Visuals/Facing/Rig:position", [0], [(0, 0)], vec)); i += 1
    out.append(anim_value_track(i, "Visuals/Facing/Rig:modulate", [0], [(1, 1, 1, 1)], col))

    out += ['[sub_resource type="Animation" id="Animation_idle"]',
            "length = 2.4", "loop_mode = 1"]
    idle = {
        "Hips": ([0, 1.2, 2.4], [0.0, 0.015, 0.0]),
        "Chest": ([0, 0.6, 1.8, 2.4], [0.0, -0.03, 0.03, 0.0]),
        "Head": ([0, 0.9, 2.1, 2.4], [0.0, 0.04, -0.03, 0.0]),
    }
    i = 0
    for name, (times, vals) in idle.items():
        out.append(anim_value_track(i, f"{rp[name]}:rotation", times, vals, f))
        i += 1

    out += ['[sub_resource type="Animation" id="Animation_attack"]', "length = 0.5"]
    out.append(anim_value_track(0, f"{rp['Chest']}:rotation",
                                [0, 0.15, 0.35, 0.5], [0.0, -0.14, 0.06, 0.0], f))
    out.append(anim_value_track(1, "Visuals/Facing/Rig:position",
                                [0, 0.15, 0.5], [(0, 0), (14, 0), (0, 0)], vec))

    out += ['[sub_resource type="Animation" id="Animation_hurt"]', "length = 0.35"]
    out.append(anim_value_track(0, f"{rp['Hips']}:rotation",
                                [0, 0.1, 0.35], [0.0, 0.08, 0.0], f))
    out.append(anim_value_track(1, "Visuals/Facing/Rig:modulate",
                                [0, 0.1, 0.35],
                                [(1, 1, 1, 1), (1, 0.55, 0.55, 1), (1, 1, 1, 1)], col))

    out += ['[sub_resource type="Animation" id="Animation_death"]', "length = 0.8"]
    out.append(anim_value_track(0, f"{rp['Hips']}:rotation", [0, 0.8], [0.0, 0.3], f))
    out.append(anim_value_track(1, "Visuals/Facing/Rig:modulate",
                                [0, 0.8], [(1, 1, 1, 1), (1, 1, 1, 0)], col))

    out += ["""[sub_resource type="AnimationLibrary" id="AnimationLibrary_kokomi"]
_data = {
&"RESET": SubResource("Animation_reset"),
&"attack": SubResource("Animation_attack"),
&"death": SubResource("Animation_death"),
&"hurt": SubResource("Animation_hurt"),
&"idle": SubResource("Animation_idle")
}

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

[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_kokomi"]
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
"""]
    return "\n".join(out)


def render_preview(tex: np.ndarray, fields: dict, joints_px: dict, out_path: str):
    """Offline linear-blend-skinning render: rest pose next to a posed frame
    (chest -10deg, head +8deg, FK-chained), to eyeball whether flat painted
    cut-from-splash art tears under mesh deformation (F1 sec.6 item 10)."""
    h, w = tex.shape[:2]
    pose = {"head": math.radians(8.0), "chest": math.radians(-10.0),
            "hips": 0.0, "legs": 0.0}
    # FK: chest rotation carries the head region too.
    pivots = {"legs": joints_px["hip"], "hips": joints_px["hip"],
              "chest": joints_px["chest"], "head": joints_px["head"]}
    chain = {"legs": ["legs"], "hips": ["hips"], "chest": ["chest"],
             "head": ["chest", "head"]}

    def bone_matrix(name):
        m = np.eye(3)
        for link in chain[name]:
            th, (px, py) = pose[link], pivots[link]
            c, s = math.cos(th), math.sin(th)
            rot = np.array([[c, -s, px - c * px + s * py],
                            [s, c, py - s * px - c * py],
                            [0, 0, 1]])
            m = rot @ m
        return m

    ys, xs = np.mgrid[0:h, 0:w]
    pts = np.stack([xs.ravel(), ys.ravel(), np.ones(h * w)])
    new = np.zeros((2, h * w))
    for name in fields:
        wv = fields[name].ravel()
        new += wv * (bone_matrix(name) @ pts)[:2]
    canvas = np.zeros_like(tex)
    nx = np.clip(np.round(new[0]).astype(int), 0, w - 1)
    ny = np.clip(np.round(new[1]).astype(int), 0, h - 1)
    vis = tex[..., 3].ravel() > ALPHA_THRESHOLD
    for dx in (0, 1):
        for dy in (0, 1):
            canvas[np.clip(ny[vis] + dy, 0, h - 1),
                   np.clip(nx[vis] + dx, 0, w - 1)] = tex.reshape(-1, 4)[vis]
    side = np.concatenate([tex, canvas], axis=1)
    Image.fromarray(side, mode="RGBA").save(out_path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="scratch project dir, OUTSIDE the repo")
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--cutout", default=os.path.join(
        repo, "ImageGen", "images", "kokomi", "model", "kokomi_portrait_cutout.png"),
        help="Kokomi portrait cutout (Tier F, machine-local; in a worktree "
             "pass the main checkout's copy)")
    args = ap.parse_args()
    refuse_inside_repo(args.out)
    if not os.path.exists(args.cutout):
        print(f"source missing: {args.cutout}", file=sys.stderr)
        return 2

    out = os.path.abspath(args.out)
    rig_dir = os.path.join(out, "kokomi_spike")
    mask_dir = os.path.join(rig_dir, "masks")
    os.makedirs(mask_dir, exist_ok=True)

    # -- texture ------------------------------------------------------------
    src = Image.open(args.cutout).convert("RGBA")
    a_full = np.asarray(src)[..., 3]
    x0, y0, x1, y1 = alpha_bbox(a_full)
    pad = 8
    crop = src.crop((max(0, x0 - pad), max(0, y0 - pad),
                     min(src.width, x1 + pad), min(src.height, y1 + pad)))
    tex_img = crop.resize((crop.width // DOWNSCALE, crop.height // DOWNSCALE),
                          Image.LANCZOS)
    tex_img.save(os.path.join(rig_dir, "kokomi_tex.png"))
    tex = np.asarray(tex_img)
    alpha = tex[..., 3]
    H, W = alpha.shape
    print(f"texture: {W}x{H} (cutout {src.width}x{src.height}, bbox "
          f"{x1 - x0}x{y1 - y0}, /{DOWNSCALE})")

    # -- masks + weight fields ---------------------------------------------
    masks = build_masks(alpha)
    for name, m in masks.items():
        Image.fromarray(m, mode="L").save(os.path.join(mask_dir, f"mask_{name}.png"))
    fields, sigma = weight_fields(masks, H)
    print(f"masks: {len(masks)} bands, blur sigma {sigma:.1f}px")

    # -- rig geometry -------------------------------------------------------
    # Body column: alpha centroid x of the head band (the figure's most
    # central feature; the companion fish and fin skew a whole-image centroid).
    head_mask = masks["head"]
    ys_h, xs_h = np.nonzero(head_mask > 127)
    cx = float(xs_h.mean())
    S = TARGET_BODY_H / H
    to_rig = lambda px, py: ((px - cx) * S, (py - H) * S)  # noqa: E731

    jpx = {n: (cx, JOINTS[n] * H) for n in ("hip", "chest", "neck", "head")}
    jr = {n: to_rig(*jpx[n]) for n in jpx}
    feet = to_rig(cx, H)

    # -- polygons + computed weights ---------------------------------------
    region_bone = {name: bone for name, _t, _b, bone in REGIONS}
    poly_nodes, stats = [], []
    for name in DRAW_ORDER:
        outline_px = region_outline(masks[name], H)
        if len(outline_px) < 3:
            raise SystemExit(f"region {name}: degenerate outline")
        verts = [to_rig(px, py) for px, py in outline_px]
        uv = outline_px
        weights = {rn: [] for rn in fields}
        for px, py in outline_px:
            xi = int(np.clip(px, 0, W - 1))
            yi = int(np.clip(py, 0, H - 1))
            vals = {rn: fields[rn][yi, xi] for rn in fields}
            tot = sum(vals.values())
            if tot < 1e-6:
                vals = {rn: (1.0 if rn == name else 0.0) for rn in fields}
                tot = 1.0
            for rn in fields:
                weights[rn].append(vals[rn] / tot)
        lines = [f'[node name="Layer{name.capitalize()}" type="Polygon2D" '
                 f'parent="Visuals/Facing/Rig"]',
                 'texture = ExtResource("1_tex")',
                 'skeleton = NodePath("../Skeleton2D")',
                 f"polygon = {pv2(verts)}",
                 f"uv = {pv2(uv)}"]
        # Godot 4 spelling, MEASURED against MegaDot 4.5: the Godot-3-era
        # bones/N/path dynamic properties are gone (set() is a silent no-op);
        # the live surface is one "bones" Array alternating NodePath and
        # PackedFloat32Array, applied via _set_bones -> add_bone().
        bone_entries = ", ".join(
            f'NodePath("{bone}"), {pf32(weights[rn])}'
            for rn, _t, _b, bone in REGIONS)
        lines.append(f"bones = [{bone_entries}]")
        poly_nodes.append("\n".join(lines) + "\n")
        shared = sum(1 for i in range(len(outline_px))
                     if sorted((weights[rn][i] for rn in fields), reverse=True)[1] > 0.05)
        stats.append((name, len(verts), shared))
        print(f"region {name}: {len(verts)} verts, {shared} blended (>5% second bone)")

    # -- skeleton ----------------------------------------------------------
    rig_base = "Visuals/Facing/Rig/Skeleton2D"
    bone_rig_paths = {
        "Hips": f"{rig_base}/Hips",
        "Chest": f"{rig_base}/Hips/Chest",
        "Neck": f"{rig_base}/Hips/Chest/Neck",
        "Head": f"{rig_base}/Hips/Chest/Neck/Head",
        "Legs": f"{rig_base}/Hips/Legs",
    }
    up = -math.pi / 2
    down = math.pi / 2
    dist = lambda a, b: math.hypot(b[0] - a[0], b[1] - a[1])  # noqa: E731
    bones = [
        bone_decl("Hips", "Visuals/Facing/Rig/Skeleton2D",
                  jr["hip"], dist(jr["hip"], jr["chest"]), up),
        bone_decl("Chest", "Visuals/Facing/Rig/Skeleton2D/Hips",
                  (0, jr["chest"][1] - jr["hip"][1]),
                  dist(jr["chest"], jr["neck"]), up),
        bone_decl("Neck", "Visuals/Facing/Rig/Skeleton2D/Hips/Chest",
                  (0, jr["neck"][1] - jr["chest"][1]),
                  dist(jr["neck"], jr["head"]), up),
        bone_decl("Head", "Visuals/Facing/Rig/Skeleton2D/Hips/Chest/Neck",
                  (0, jr["head"][1] - jr["neck"][1]), 30.0, up),
        bone_decl("Legs", "Visuals/Facing/Rig/Skeleton2D/Hips",
                  (0, 0), dist(jr["hip"], feet), down),
    ]

    # -- scene text ---------------------------------------------------------
    n_layers = len(REGIONS)
    scene = [
        f"[gd_scene load_steps={20 + 1} format=3]",
        "",
        '[ext_resource type="Texture2D" path="res://kokomi_spike/kokomi_tex.png" id="1_tex"]',
        "",
        build_animations(bone_rig_paths),
        '[node name="KokomiCombat" type="Node2D"]',
        "",
        '[node name="Visuals" type="Node2D" parent="."]',
        "unique_name_in_owner = true",
        "",
        '[node name="Facing" type="Node2D" parent="Visuals"]',
        "unique_name_in_owner = true",
        "",
        '[node name="Rig" type="Node2D" parent="Visuals/Facing"]',
        "position = Vector2(0, 0)",
        "",
        '[node name="Skeleton2D" type="Skeleton2D" parent="Visuals/Facing/Rig"]',
        "",
        "\n".join(bones),
        "\n".join(poly_nodes),
        '[node name="Bounds" type="Control" parent="."]',
        "unique_name_in_owner = true",
        "layout_mode = 3",
        "anchors_preset = 0",
        "offset_left = -120.0",
        "offset_top = -280.0",
        "offset_right = 120.0",
        "offset_bottom = 0.0",
        "mouse_filter = 2",
        "",
        '[node name="CenterPos" type="Marker2D" parent="."]',
        "unique_name_in_owner = true",
        "position = Vector2(0, -112)",
        "",
        '[node name="IntentPos" type="Marker2D" parent="."]',
        "unique_name_in_owner = true",
        "position = Vector2(0, -350)",
        "",
        '[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
        "unique_name_in_owner = true",
        "libraries = {",
        '&"": SubResource("AnimationLibrary_kokomi")',
        "}",
        "",
        '[node name="AnimationTree" type="AnimationTree" parent="."]',
        "unique_name_in_owner = true",
        "active = true",
        "callback_mode_discrete = 0",
        'tree_root = SubResource("AnimationNodeStateMachine_kokomi")',
        'anim_player = NodePath("../AnimationPlayer")',
        "",
    ]
    with open(os.path.join(rig_dir, "combat.tscn"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(scene))

    # -- project + validation scripts --------------------------------------
    with open(os.path.join(out, "project.godot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(PROJECT_GODOT)
    with open(os.path.join(out, "export_presets.cfg"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(EXPORT_PRESETS)
    with open(os.path.join(out, "spike_check.gd"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(SPIKE_CHECK_GD)
    pc_dir = os.path.join(out, "packcheck")
    os.makedirs(pc_dir, exist_ok=True)
    with open(os.path.join(pc_dir, "project.godot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(PACKCHECK_PROJECT)
    pck_path = os.path.join(out, "spike_strict.pck").replace("\\", "/")
    with open(os.path.join(pc_dir, "pack_check.gd"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(PACK_CHECK_GD.replace("PCK_PATH", pck_path))

    # -- offline deform preview --------------------------------------------
    render_preview(tex, fields, {k: jpx[k] for k in ("hip", "chest", "head")},
                   os.path.join(out, "preview_deform.png"))
    print(f"preview: {os.path.join(out, 'preview_deform.png')} (rest | posed)")

    total_verts = sum(v for _n, v, _s in stats)
    print(f"RIG SUMMARY: 5 bones (4 weighted), {n_layers} regions, "
          f"{total_verts} weighted vertices, all weights computed from masks")
    print(f"Spike project written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
