"""Pose, animate and toon-render the official Klee PMX headless, in Blender.

    blender -b --factory-startup -P tools/klee_render/render.py -- \
        --pmx <可莉2.0.pmx> --out <scratch dir> --ppu 288 \
        [--clips idle,attack,...] [--stills rest,select] [--keys-only] [--pitch 5]

THE MODEL NEVER ENTERS THE REPO. It is the official Klee 2.0 PMX from
Bilibili's Mondstadt model page; its terms forbid redistribution and
commercial use, so it is read in place from the operator's scratch directory
and only the rendered PNGs leave it (review/active/klee-visual-paper-2026-10-12.md).
A .blend that embeds it is never saved by this script.

Writes, per clip, <out>/raw/<clip>/f_000.png ... on one fixed orthographic
camera per clip (so the frames register), each frame's style passes beside it
in <out>/raw/<clip>/aux/f_000_X.png (R protect, G/B grain: see add_aovs), and
<out>/<clip>.json with the canvas size, the pixel the ground origin (her
feet's anchor) projects to, the fps and the frame times. Stills write
<out>/raw/<name>.png (+ aux/<name>_X.png) and <out>/<name>.json the same way.
`tools/klee_render/post.py` paints the raw frames into <out>/<clip>/ and
<out>/<name>.png (the style's 2D half); `pack.py` trims and packs those.

Units: `--ppu` is TEXTURE pixels per model unit. The pose library is
tools/klee_render/clips.py (no bpy; importable anywhere).
"""
import argparse
import json
import math
import os
import sys

import addon_utils
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "char_render"))
import clips as C  # noqa: E402
import toon as T  # noqa: E402  (the shared shader, posing and framing: tools/char_render/toon.py)
from toon import (add_outline, aim, at_time, curl, flat_material, frame_camera, hand_to,  # noqa: E402
                  move, outline_prop, project, render_to, rotate_world, upd, w2a_dir, world_box)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--pmx", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ppu", type=float, required=True)
ap.add_argument("--clips", default="")
ap.add_argument("--stills", default="")
ap.add_argument("--keys-only", action="store_true", help="render each clip's key poses only")
ap.add_argument("--outline-px", type=float, default=2.2, help="outline width in texture px")
ap.add_argument("--pitch", type=float, default=5.0, help="camera looks down this many degrees")
ap.add_argument("--samples", type=int, default=32)
args = ap.parse_args(argv)
os.makedirs(args.out, exist_ok=True)

MMD = T.MMD
LINE_COLOR = T.LINE_COLOR              # the bomb's lines, and a body material with no texture
#: Style H1 + H3 lite's shader half is tools/char_render/toon.py STYLE (one
#: STYLE for every kit); post.py holds the 2D half.
UNLIT_MATS = {"脸", "眼白", "眼睛", "表情"}
NO_LINE_MATS = {"眼白", "眼睛", "表情"}


# ----------------------------------------------------------------- scene
def load_model():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable(MMD, default_set=True)
    bpy.ops.mmd_tools.import_model(filepath=args.pmx, scale=0.08, types={"MESH", "ARMATURE", "MORPHS"})
    root = next(o for o in bpy.data.objects if o.type == "EMPTY" and o.parent is None)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    mesh = next(o for o in bpy.data.objects if o.type == "MESH")
    return root, arm, mesh


def setup_render():
    return T.setup_render(args.samples)


# ----------------------------------------------------------------- the bomb
def _on_sphere(r, x, z, inset=0.0):
    y = -math.sqrt(max(r * r - x * x - z * z, 0.0))
    p = Vector((x, y, z))
    return p * (1.0 - inset), p.normalized()


def _part(kind, mat, loc, scale, normal=None, **kw):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=kw.get("seg", 24), ring_count=kw.get("rings", 12), radius=1)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("seg", 16), radius=1, depth=1)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=kw.get("seg", 16), radius1=1, radius2=kw.get("r2", 0.0), depth=1)
    ob = bpy.context.object
    ob.scale = scale
    ob.location = loc
    if normal is not None:
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = Vector((0, -1, 0)).rotation_difference(normal)
    elif "rot" in kw:
        ob.rotation_euler = tuple(math.radians(a) for a in kw["rot"])
    ob.data.materials.append(mat)
    if kind == "sphere":
        bpy.ops.object.shade_smooth()
    # bake scale and rotation into the mesh, so a prop's own scale is free
    # for the renderer to animate (the held bomb pops in by scale)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return ob


def make_jumpy_dumpty(r, mats, line):
    """A Jumpy-Dumpty-like bomb, modelled here from primitives: a round red
    body with two little ears, a brown cap and fuse with a lit tip, and a face
    (eyes with catchlights, a small mouth, blush). Faces local -Y."""
    body = _part("sphere", mats["bomb"], (0, 0, 0), (r, r, r * 0.94), seg=40, rings=20)
    parts = [body]
    lined = [body]
    cap = _part("cyl", mats["cap"], (0, 0, r * 0.93), (r * 0.30, r * 0.30, r * 0.20), seg=20)
    fuse = _part("cyl", mats["fuse"], (r * 0.06, 0, r * 1.15), (r * 0.06, r * 0.06, r * 0.32), rot=(0, 18, 0))
    tip = _part("sphere", mats["spark"], (r * 0.13, 0, r * 1.33), (r * 0.10,) * 3, seg=12, rings=8)
    parts += [cap, fuse, tip]
    lined += [cap, fuse]
    for sx in (-1, 1):
        ear = _part("sphere", mats["bomb_dark"], (sx * r * 0.58, r * 0.05, r * 0.70),
                    (r * 0.20, r * 0.13, r * 0.34), rot=(0, sx * 32, 0))
        parts.append(ear)
        lined.append(ear)
        p, n = _on_sphere(r, sx * r * 0.32, r * 0.10, inset=0.02)
        parts.append(_part("sphere", mats["eye"], p, (r * 0.10, r * 0.05, r * 0.15), normal=n, seg=16, rings=8))
        p, n = _on_sphere(r, sx * r * 0.29, r * 0.17, inset=-0.02)
        parts.append(_part("sphere", mats["white"], p, (r * 0.035,) * 3, seg=8, rings=6))
        p, n = _on_sphere(r, sx * r * 0.55, -r * 0.12, inset=0.01)
        parts.append(_part("sphere", mats["blush"], p, (r * 0.13, r * 0.03, r * 0.07), normal=n, seg=12, rings=6))
    p, n = _on_sphere(r, 0, -r * 0.16, inset=0.01)
    parts.append(_part("sphere", mats["eye"], p, (r * 0.09, r * 0.03, r * 0.05), normal=n, seg=12, rings=6))
    for ob in parts[1:]:
        ob.parent = body
        ob.matrix_parent_inverse = body.matrix_world.inverted()
    outlines = [outline_prop(ob, line) for ob in lined]
    return body, parts, outlines


# ----------------------------------------------------------------- posing
def reset(root, arm, mesh):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = Matrix.Identity(4)
    for k in mesh.data.shape_keys.key_blocks[1:]:
        k.value = 0.0
    root.rotation_euler = (0, 0, 0)
    root.location = (0, 0, 0)
    upd()


def apply_pose(root, arm, mesh, p):
    reset(root, arm, mesh)
    root.rotation_euler = (0, math.radians(p.get("root_rot", 0.0)), math.radians(p["yaw"]))
    root.location = p.get("root", (0, 0, 0))
    upd()
    keys = mesh.data.shape_keys.key_blocks
    for k, v in p["morphs"].items():
        if k in keys:
            keys[k].value = v
        else:
            print("WARN missing morph", k)
    for op in p["ops"]:
        kind = op[0]
        if kind == "rot":
            rotate_world(arm, op[1], op[2], op[3])
        elif kind == "move":
            move(arm, op[1], op[2])
        elif kind == "rotw":
            rotate_world(arm, op[1], w2a_dir(arm, op[2]), op[3])
        elif kind == "aimw":
            aim(arm, op[1], w2a_dir(arm, op[2]), op[3] if len(op) > 3 else 0.0)
        elif kind == "movew":
            move(arm, op[1], w2a_dir(arm, op[2]))
        elif kind == "hand":
            hand_to(arm, op[1], op[2], op[3], op[4])
        elif kind == "curl":
            curl(arm, op[1], op[2], op[3])
        else:
            raise ValueError(op)
    upd()


def capture(root, arm, mesh, p):
    """Resolve a pose to the numbers the renderer interpolates."""
    apply_pose(root, arm, mesh, p)
    bones = {}
    for pb in arm.pose.bones:
        loc, rot, sc = pb.matrix_basis.decompose()
        bones[pb.name] = (loc.copy(), rot.copy(), sc.copy())
    return {
        "bones": bones,
        "morphs": {k.name: k.value for k in mesh.data.shape_keys.key_blocks[1:] if k.value},
        "root_rot": (0.0, math.radians(p.get("root_rot", 0.0)), math.radians(p["yaw"])),
        "root": Vector(p.get("root", (0, 0, 0))),
        "held": float(p.get("held", 1.0)),
        "thrown": None if p.get("thrown") is None else Vector(p["thrown"]),
        "spin": float(p.get("thrown_spin", 0.0)),
        "big": float(p.get("big", 0.0)),
        "big_thrown": None if p.get("big_thrown") is None else Vector(p["big_thrown"]),
        "big_spin": float(p.get("big_spin", 0.0)),
    }


def prop_scale(a, b, u, raw):
    """A prop's scale between two keys: a drop happens AT the next key; a rise
    grows it in."""
    h = a if b < a and raw < 1.0 else a * (1 - u) + b * u
    return b if raw >= 1.0 else h


def prop_flight(pa, pb_, sa, sb, u, raw):
    """A free prop's (position, spin) between two keys, or (None, 0)."""
    if pa is not None and pb_ is not None:
        return pa.lerp(pb_, u), sa * (1 - u) + sb * u
    if raw >= 1.0 and pb_ is not None:
        return pb_, sb
    if raw <= 0.0 and pa is not None:
        return pa, sa
    return None, 0.0


def place_big(arm, big_ob):
    """The big Jumpy Dumpty sits between her two hands (clips.BIG_AT from the
    midpoint of the fingertips), facing the camera."""
    a = arm.matrix_world @ arm.pose.bones["手先.R"].head
    b = arm.matrix_world @ arm.pose.bones["手先.L"].head
    big_ob.location = (a + b) / 2 + Vector(C.BIG_AT)
    big_ob.rotation_euler = (0, 0, math.radians(C.HELD_YAW))


def set_frame(root, arm, mesh, held_ob, thrown_ob, caps, keys, t, big_ob=None, big_thrown_ob=None):
    i, j, u, raw = at_time(keys, t)
    a, b = caps[i], caps[j]
    for pb in arm.pose.bones:
        la, qa, sa = a["bones"][pb.name]
        lb, qb, sb = b["bones"][pb.name]
        if qa.dot(qb) < 0:
            qb = -qb
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = Matrix.LocRotScale(la.lerp(lb, u), qa.slerp(qb, u), sa.lerp(sb, u))
    names = set(a["morphs"]) | set(b["morphs"])
    kb = mesh.data.shape_keys.key_blocks
    for k in kb[1:]:
        k.value = 0.0
    for n in names:
        va, vb = a["morphs"].get(n, 0.0), b["morphs"].get(n, 0.0)
        # an overlay-eyes morph steps (clips.STEP_MORPHS): part-way, its
        # drawn eyes sit behind the skin and the face reads blank
        kb[n].value = (vb if u >= 0.5 else va) if n in C.STEP_MORPHS else va * (1 - u) + vb * u
    root.rotation_euler = tuple(x * (1 - u) + y * u for x, y in zip(a["root_rot"], b["root_rot"]))
    root.location = a["root"].lerp(b["root"], u)
    # held bomb: a drop to 0 happens AT the next key; a rise grows it in
    if held_ob is not None:
        h = prop_scale(a["held"], b["held"], u, raw)
        held_ob.hide_render = h < 0.02
        held_ob.scale = (max(h, 0.02),) * 3
    if thrown_ob is not None:
        pos, spin = prop_flight(a["thrown"], b["thrown"], a["spin"], b["spin"], u, raw)
        thrown_ob.hide_render = pos is None
        if pos is not None:
            thrown_ob.location = pos
            thrown_ob.rotation_euler = (0, math.radians(spin), math.radians(20))
    upd()
    # the big Jumpy Dumpty: held in both hands, then flown, as the small one
    if big_ob is not None:
        h = prop_scale(a["big"], b["big"], u, raw)
        big_ob.hide_render = h < 0.02
        big_ob.scale = (max(h, 0.02),) * 3
        place_big(arm, big_ob)
    if big_thrown_ob is not None:
        pos, spin = prop_flight(a["big_thrown"], b["big_thrown"], a["big_spin"], b["big_spin"], u, raw)
        big_thrown_ob.hide_render = pos is None
        if pos is not None:
            big_thrown_ob.location = pos
            big_thrown_ob.rotation_euler = (0, math.radians(spin), math.radians(20))
    upd()


# ----------------------------------------------------------------- framing
def reset_camera(cam_ob):
    T.reset_camera(cam_ob, args.pitch, 0.55)


# ----------------------------------------------------------------- main
def main():
    root, arm, mesh = load_model()
    cam_ob = setup_render()
    body_lines = []
    for m in mesh.data.materials:
        img = T.base_image(m)
        T.toon_material(m, img, m.name in UNLIT_MATS)
        body_lines.append(T.line_material(m, img, m.name in UNLIT_MATS))
    line = flat_material("line", LINE_COLOR, line=True)
    mats = {
        "bomb": flat_material("bomb", (0.86, 0.13, 0.08)),
        "bomb_dark": flat_material("bomb_dark", (0.72, 0.09, 0.06)),
        "cap": flat_material("cap", (0.34, 0.18, 0.10)),
        "fuse": flat_material("fuse", (0.80, 0.68, 0.48)),
        "spark": flat_material("spark", (1.0, 0.80, 0.30), unlit=True),
        "eye": flat_material("eye", (0.10, 0.05, 0.05), unlit=True),
        "white": flat_material("white", (1.0, 1.0, 1.0), unlit=True),
        "blush": flat_material("blush", (0.98, 0.55, 0.55), unlit=True),
    }
    body_outline = add_outline(mesh, body_lines, NO_LINE_MATS)
    t_world = args.outline_px / args.ppu
    body_outline.thickness = t_world

    # the held bomb rides the near wrist; its offset is set once, in the
    # stance-A pose (clips.HELD_AT: on her palm, held out toward the enemy),
    # so it sits in her hand in every clip
    held, held_parts, held_lines = make_jumpy_dumpty(C.BOMB_R, mats, line)
    apply_pose(root, arm, mesh, C.STILLS["stance_a"])
    tip = arm.matrix_world @ arm.pose.bones["手先.R"].head
    want = (Matrix.Translation(tip + Vector(C.HELD_AT)) @ Matrix.Rotation(math.radians(C.HELD_YAW), 4, "Z"))
    held.parent = arm
    held.parent_type = "BONE"
    held.parent_bone = "手首.R"
    upd()
    held.matrix_world = want
    thrown, thrown_parts, thrown_lines = make_jumpy_dumpty(C.BOMB_R, mats, line)
    cradled, cradled_parts, cradled_lines = make_jumpy_dumpty(C.BOMB_R, mats, line)
    # Jumpy Dumpty's own, head-sized: held in both hands, then thrown (clips.JUMPY)
    big, big_parts, big_lines = make_jumpy_dumpty(C.JUMPY_R, mats, line)
    big_thrown, big_thrown_parts, big_thrown_lines = make_jumpy_dumpty(C.JUMPY_R, mats, line)
    for m_ in held_lines + thrown_lines + cradled_lines + big_lines + big_thrown_lines:
        m_.thickness = t_world
    upd()

    def show(ob, parts, on):
        ob.hide_render = not on
        for p in parts:
            p.hide_render = not on

    def sync_parts():
        """Each bomb's face, ears and fuse follow its body's visibility."""
        for ob, parts in ((held, held_parts), (thrown, thrown_parts), (big, big_parts),
                          (big_thrown, big_thrown_parts)):
            for p in parts:
                p.hide_render = ob.hide_render

    props = [held, thrown, big, big_thrown]
    prop_parts = held_parts[1:] + thrown_parts[1:] + big_parts[1:] + big_thrown_parts[1:]

    meta_all = {}
    clip_names = [c for c in args.clips.split(",") if c]
    for name in clip_names:
        spec = C.CLIPS.get(name) or C.SELECT_LOOPS[name]
        keys = spec["keys"]
        caps = [capture(root, arm, mesh, k[1]) for k in keys]
        is_cradle = bool(spec.get("cradle"))
        show(held, held_parts, not is_cradle)
        show(thrown, thrown_parts, not is_cradle)
        show(big, big_parts, False)
        show(big_thrown, big_thrown_parts, False)
        show(cradled, cradled_parts, is_cradle)
        if is_cradle:
            # cradled between both hands at the chest; re-seated per frame
            pass
        fps = spec["fps"]
        if args.keys_only:
            times = [k[0] for k in keys]
        else:
            if spec.get("motion_end"):
                n = int(round(spec["motion_end"] * fps)) + 1     # motion, then hold the last frame
            else:
                n = int(round(spec["length"] * fps))             # a loop never repeats frame 0
            times = [round(i / fps, 6) for i in range(n)]

        def frame_objs():
            objs = [mesh]
            if not is_cradle:
                objs += props + prop_parts
            else:
                objs += [cradled] + cradled_parts[1:]
            return objs

        def pose_at(t):
            set_frame(root, arm, mesh, None if is_cradle else held, None if is_cradle else thrown,
                      caps, keys, t, None if is_cradle else big, None if is_cradle else big_thrown)
            if not is_cradle:
                sync_parts()
            place_cradle()

        def place_cradle():
            if is_cradle:
                a = arm.matrix_world @ arm.pose.bones["手先.R"].head
                b = arm.matrix_world @ arm.pose.bones["手先.L"].head
                cradled.location = (a + b) / 2 + Vector((0.0, -0.035, 0.03))
                cradled.rotation_euler = (0, 0, math.radians(30))
                upd()

        reset_camera(cam_ob)
        pts = []
        for t in times:
            pose_at(t)
            pts += world_box(frame_objs())
        box = project(cam_ob, pts)
        w, h, origin, _c = frame_camera(cam_ob, box, args.ppu)
        d = os.path.join(args.out, "raw", name)
        os.makedirs(d, exist_ok=True)
        sc = bpy.context.scene
        for i, t in enumerate(times):
            pose_at(t)
            render_to(os.path.join(d, f"f_{i:03d}.png"))
        meta = {"clip": name, "fps": fps, "length": spec["length"], "loop": spec["loop"],
                "motion_end": spec.get("motion_end"), "times": times, "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": args.ppu,
                "pitch": args.pitch, "keys_only": args.keys_only}
        with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        meta_all[name] = meta
        print("CLIP", name, len(times), "frames", (w, h), "origin", origin)

    for name in [s for s in args.stills.split(",") if s]:
        p = C.STILLS[name]
        is_cradle = bool(p.get("cradle"))
        cap = capture(root, arm, mesh, p)
        show(held, held_parts, not is_cradle)
        show(thrown, thrown_parts, not is_cradle)
        show(big, big_parts, False)
        show(big_thrown, big_thrown_parts, False)
        show(cradled, cradled_parts, is_cradle)
        set_frame(root, arm, mesh, None if is_cradle else held, None if is_cradle else thrown,
                  [cap], [(0.0, p, "io")], 0.0)
        if not is_cradle:
            sync_parts()
        else:
            a = arm.matrix_world @ arm.pose.bones["手先.R"].head
            b = arm.matrix_world @ arm.pose.bones["手先.L"].head
            cradled.location = (a + b) / 2 + Vector((0.0, -0.035, 0.03))
            cradled.rotation_euler = (0, 0, math.radians(30))
            upd()
        reset_camera(cam_ob)
        objs = [mesh, cradled] + props + prop_parts + cradled_parts[1:]
        box = project(cam_ob, world_box(objs))
        w, h, origin, _c = frame_camera(cam_ob, box, args.ppu)
        render_to(os.path.join(args.out, "raw", f"{name}.png"))
        # where her hips (the seat) and head land, for anchoring stills
        inv = cam_ob.matrix_world.inverted()

        def px(v):
            q = inv @ v
            return [round((q.x + (w / args.ppu) / 2) * args.ppu, 3), round(((h / args.ppu) / 2 - q.y) * args.ppu, 3)]

        hips = arm.matrix_world @ arm.pose.bones["下半身"].head
        head = arm.matrix_world @ arm.pose.bones["頭"].head      # the neck joint, under her chin
        meta = {"still": name, "canvas": [w, h], "origin_px": [round(origin[0], 3), round(origin[1], 3)],
                "hips_px": px(hips), "head_px": px(head), "ppu": args.ppu, "pitch": args.pitch}
        with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        print("STILL", name, (w, h), origin)


main()
