"""Pose, animate and toon-render one official kit model headless, in Blender.

    blender -b --factory-startup -P tools/char_render/render.py -- \
        --char varka --models <scratch>/models --out <scratch dir> --ppu N \
        [--clips idle,attack,...] [--stills stance_a,rest,...] [--keys-only] [--outline-px 2.2]

    (first look, any kit:  --char furina --pmx <pmx> [--prop <pmx>] --stills rest,stance)

THE MODELS NEVER ENTER THE REPO. Each pack is read in place from the
operator's scratch directory (models/<char>/unpacked/); its terms forbid
redistribution and commercial use, so only the rendered PNGs leave it. No
.blend is ever saved.

The same contract as tools/klee_render/render.py, which this mirrors for any
kit whose chars.CHARS entry names a pose library (`clips`): per clip,
<out>/raw/<clip>/f_NNN.png with its `style` pass in aux/, and <out>/<clip>.json
(canvas, the feet anchor's pixel, fps, frame times); per still <out>/raw/<name>.png
and <out>/<name>.json. tools/klee_render/post.py paints them and
tools/char_render/pack.py packs them. The shader, posing and framing are
tools/char_render/toon.py, shared with Klee's renderer (one STYLE).

What a kit adds over Klee: its unlit and line-less material sets come from
chars.py, the `+` overlay shells are hidden, the hand tip falls back to a
finger bone, and it may carry BLADES (Varka's two claymores): PMX props placed
per pose, each closed in its hand by IK (grip_hand). Each clip's json also
records, per blade, where the blade's base and tip project (`blades`, SUBSTEPS
samples per frame interval), which fx.py turns into the slash trails, and the
clip's marked `events` (the impact times) and `effects` (separate sprite
clips the game places, such as the Ascension's ground burst).
"""
import argparse
import importlib
import json
import math
import os
import sys

import addon_utils
import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chars as CH  # noqa: E402
import toon as T  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--char", required=True, choices=sorted(CH.CHARS))
ap.add_argument("--models", default="", help="scratch models root (models/<char>/unpacked/...)")
ap.add_argument("--pmx", default="", help="the body PMX (default: <models>/chars.CHARS[char]['pmx'])")
ap.add_argument("--out", required=True)
ap.add_argument("--prop", default="", help="first look only: a single prop PMX placed by the stance's `prop`")
ap.add_argument("--clips", default="")
ap.add_argument("--stills", default="")
ap.add_argument("--keys-only", action="store_true", help="render each clip's key poses only")
ap.add_argument("--ppu", type=float, default=0.0, help="texture px per unit; 0 = solve from canon height")
ap.add_argument("--outline-px", type=float, default=CH.OUTLINE_PX)
ap.add_argument("--pitch", type=float, default=5.0)
ap.add_argument("--samples", type=int, default=32)
args = ap.parse_args(argv)
os.makedirs(args.out, exist_ok=True)
CFG = CH.CHARS[args.char]
LIB = importlib.import_module(CFG["clips"]) if CFG.get("clips") else None
#: blade samples per frame interval, recorded for the trails
SUBSTEPS = 4


def model_path(rel):
    return os.path.join(args.models, rel)


# ----------------------------------------------------------------- scene
def import_pmx(path):
    before = set(bpy.data.objects)
    bpy.ops.mmd_tools.import_model(filepath=path, scale=CH.IMPORT_SCALE, types={"MESH", "ARMATURE", "MORPHS"})
    new = [o for o in bpy.data.objects if o not in before]
    root = next(o for o in new if o.type == "EMPTY" and o.parent is None)
    arm = next(o for o in new if o.type == "ARMATURE")
    mesh = next(o for o in new if o.type == "MESH")
    return root, arm, mesh


def shade(mesh):
    """Style H1 on every material of one imported mesh, plus its hull."""
    face, no_line = CFG["face_mats"], set(CFG["no_line_mats"])
    hide = CFG.get("hide_mats", set())
    lines = []
    for m in mesh.data.materials:
        if CH.is_overlay(m.name) or m.name in hide:
            T.hidden_material(m)
            no_line.add(m.name)
            lines.append(T.line_material(m, None, False))
            continue
        img = T.base_image(m)
        T.toon_material(m, img, m.name in face)
        lines.append(T.line_material(m, img, m.name in face))
    return T.add_outline(mesh, lines, no_line)


# ----------------------------------------------------------------- posing
def palm(arm, side):
    """The palm centre in armature space: between the wrist and the hand tip
    (手先 where the model has one, else chars' finger-bone stand-in)."""
    pbs = arm.pose.bones
    tip = f"手先.{side}" if f"手先.{side}" in pbs else f"{CFG['hand_tip']}.{side}"
    return (pbs[f"手首.{side}"].head + pbs[tip].head) / 2


def apply_pose(root, arm, mesh, p):
    T.reset(root, arm, mesh)
    root.rotation_euler = (0, math.radians(p.get("root_rot", 0.0)), math.radians(p["yaw"]))
    root.location = p.get("root", (0, 0, 0))
    T.upd()
    keys = mesh.data.shape_keys.key_blocks
    for k, v in p["morphs"].items():
        if k in keys:
            keys[k].value = v
        else:
            print("WARN missing morph", k)
    for op in p["ops"]:
        T.run_op(arm, op)
    T.upd()


def blade_frame(spec):
    """The blade's world rotation: local -Y along spec['dir'] (guard to
    tip), the flat (local Z) turned toward the viewer, then rolled
    spec['roll'] degrees about the blade."""
    d = Vector(spec["dir"]).normalized()
    view = Vector((0, -1, 0))
    zf = view - view.dot(d) * d
    zf = zf.normalized() if zf.length > 1e-6 else Vector((1, 0, 0))
    zf = Matrix.Rotation(math.radians(spec.get("roll", 0.0)), 3, d) @ zf
    yl = -d
    xl = yl.cross(zf).normalized()
    zf = xl.cross(yl).normalized()
    return Matrix((xl, yl, zf)).transposed().to_quaternion()


def anchor_point(arm, anchor):
    if anchor == "ground":
        return Vector((0, 0, 0))
    return arm.matrix_world @ arm.pose.bones[anchor].head


def place_blade(ob, grip_w, rot, g):
    """The blade object so its point local +Y `g` (where the hand closes)
    sits at grip_w."""
    R = rot.to_matrix().to_4x4()
    ob.matrix_world = Matrix.Translation(grip_w - (R @ Vector((0, g, 0, 0))).to_3d()) @ R
    T.upd()


def grip_hand(arm, side, grip_w, rot, pole):
    """IK the arm so the palm closes on the handle at grip_w, the hand turned
    across the handle (knuckles square to the blade). A few passes: the palm
    offset depends on where the forearm ends up."""
    inv = arm.matrix_world.inverted()
    G = inv @ grip_w
    blade = (inv.to_3x3() @ (rot.to_matrix() @ Vector((0, -1, 0)))).normalized()
    target = G.copy()
    for _ in range(4):
        T.wrist_to(arm, side, target, pole)
        pbs = arm.pose.bones
        fore = (pbs[f"手首.{side}"].head - pbs[f"ひじ.{side}"].head).normalized()
        across = fore - fore.dot(blade) * blade
        if across.length > 1e-4:
            T.aim(arm, f"手首.{side}", across.normalized())
        err = G - palm(arm, side)
        if err.length < 1e-4:
            break
        target = target + err
    T.upd()


#: HANDS ON THE POMMELS (a blade spec's `rest`: stance B, [USER]
#: 2026-10-13: "the way he's holding the claymores looks kinda weird, like
#: they're going through his hands"). The plain grip puts the palm's centre
#: ON the handle's axis, so on a planted blade the hilt runs through the hand.
#: A resting hand lies palm-down on top of the pommel instead: the hand
#: level and pointing out from his shoulder, its palm turned down the blade,
#: lifted (fit_rest) until no hand vertex is inside the pommel, with
#: REST_CLEAR to spare, and the fingers draped over its far side.
REST_LIFTS = tuple(round(0.005 * i, 3) for i in range(25))   # units the palm's centre sits over the pommel top
REST_CURLS = (50, 42, 34, 26, 18, 10)
REST_CLEAR = 0.003
POMMEL_CAP = 0.06        # the tapering cap at a pommel's top (the gem), units
POMMEL_TIP_R = 0.012     # the cap's point: the footprint a resting palm must clear
_PALM = {}
_HAND_IDX = {}


def _hand_frame(arm, side):
    """(hand length h, hinge axis z, palm normal n), armature space. The
    curl turns a finger about its local Z, so its tip moves across h toward
    the palm; which way z x h points is the model's convention, measured once
    per hand (palm_side) and kept in _PALM."""
    pbs = arm.pose.bones
    z = pbs[f"中指１.{side}"].matrix.col[2].to_3d().normalized()
    h = (pbs[f"中指１.{side}"].head - pbs[f"手首.{side}"].head).normalized()
    return h, z, (z.cross(h) * _PALM.get(side, 1.0)).normalized()


def palm_side(arm, side):
    """Straight, then curled: the middle fingertip's move across the hand
    fixes the sign of the palm normal."""
    pbs = arm.pose.bones
    tip = f"中指先.{side}" if f"中指先.{side}" in pbs else f"中指３.{side}"
    T.curl(arm, side, 0, 0)
    t0 = pbs[tip].head.copy()
    T.curl(arm, side, 80, 0)
    t1 = pbs[tip].head.copy()
    _PALM[side] = 1.0
    _h, _z, n = _hand_frame(arm, side)
    _PALM[side] = 1.0 if (t1 - t0).dot(n) > 0 else -1.0
    T.curl(arm, side, 0, 0)


def rest_hand(arm, side, top_w, rot, pole, lift):
    """IK the arm so the palm's centre sits `lift` over the pommel's top
    (top_w, world), the hand level and pointing out from the shoulder, its
    palm turned down the blade."""
    inv = arm.matrix_world.inverted()
    down = (inv.to_3x3() @ (rot.to_matrix() @ Vector((0, -1, 0)))).normalized()
    G = inv @ top_w - down * lift
    target = G.copy()
    for _ in range(6):
        T.wrist_to(arm, side, target, pole)
        pbs = arm.pose.bones
        # level, and out from his shoulder over the pommel: the whole hand
        # shows from the front, laid across the pommel's top
        out = G - pbs[f"腕.{side}"].head
        level = out - out.dot(down) * down
        if level.length > 1e-4:
            T.aim(arm, f"手首.{side}", level.normalized())
        h, _z, n = _hand_frame(arm, side)
        a, t = n - n.dot(h) * h, down - down.dot(h) * h
        if a.length > 1e-6 and t.length > 1e-6:
            a, t = a.normalized(), t.normalized()
            T.rotate_world(arm, f"手首.{side}", h, math.degrees(math.atan2(a.cross(t).dot(h), a.dot(t))))
        pal = (pbs[f"手首.{side}"].head + pbs[f"中指１.{side}"].head) / 2
        err = G - pal
        if err.length < 1e-4:
            break
        target = target + err
    T.upd()


def hand_clearance(mesh, side, base, top, r):
    """The deformed hand (outline hull off) against a pommel from `base` to
    `top` (world) of radius r: the nearest hand vertex's distance from its
    axis along that span (none may be under r), and how high the hand's
    lowest vertex over the pommel's footprint sits above its top (the rest)."""
    import numpy as np
    if side not in _HAND_IDX:
        names = {f"手首.{side}"} | {f"{f}{d}.{side}" for f in T.FINGERS + ["親指"] for d in "０１２３"}
        gi = {g.index for g in mesh.vertex_groups if g.name in names}
        _HAND_IDX[side] = np.array([v.index for v in mesh.data.vertices
                                    if any(g.group in gi and g.weight > 0.3 for g in v.groups)], dtype=np.int64)
    hull = mesh.modifiers.get("outline")
    if hull:
        hull.show_viewport = False
    T.upd()
    dg = bpy.context.evaluated_depsgraph_get()
    me = mesh.evaluated_get(dg).to_mesh()
    assert len(me.vertices) == len(mesh.data.vertices), "the hull is off: one deformed vertex per body vertex"
    co = np.empty(len(me.vertices) * 3, np.float64)
    me.vertices.foreach_get("co", co)
    mesh.evaluated_get(dg).to_mesh_clear()
    if hull:
        hull.show_viewport = True
    T.upd()
    P = co.reshape(-1, 3)[_HAND_IDX[side]]
    mw = np.array(mesh.matrix_world)
    P = P @ mw[:3, :3].T + mw[:3, 3]
    b, t = np.array(base), np.array(top)
    ax = t - b
    span = np.linalg.norm(ax)
    ax /= span
    s = (P - b) @ ax
    d = np.linalg.norm((P - b) - np.outer(s, ax), axis=1)
    # the pommel's body is a cylinder up to its cap; the cap tapers to a
    # point (the gem), so over it only the point's own footprint counts
    on = (s >= 0) & (s <= span - POMMEL_CAP)
    over = d <= POMMEL_TIP_R
    return {"min_axis_dist": round(float(d[on].min()), 4) if on.any() else None, "pommel_r": r,
            "rest_gap": round(float((s[over] - span).min()), 4) if over.any() else None,
            "hand_verts_on_pommel": int(on.sum())}


def pommel_span(spec, at_w, rot, grip):
    """The pommel's ends in the world for a blade whose local Y `grip` is at
    at_w: local Y runs from the tip (-) to the pommel (+)."""
    up = rot.to_matrix() @ Vector((0, 1, 0))
    return at_w + up * (spec["pommel"][0] - grip), at_w + up * (spec["pommel"][1] - grip)


def fit_rest(arm, mesh, side, top_w, rot, pole, grip, curl):
    """Rest the hand on its pommel: the lowest lift (REST_LIFTS) at which
    some finger curl (REST_CURLS, most draped first) leaves every hand vertex
    at least REST_CLEAR outside the pommel. Returns (lift, finger curl)."""
    spec = CFG["blades"][side]
    base, top = pommel_span(spec, top_w, rot, grip)
    if side not in _PALM:
        palm_side(arm, side)
    best = None
    for lift in REST_LIFTS:
        rest_hand(arm, side, top_w, rot, pole, lift)
        for c in REST_CURLS:
            T.curl(arm, side, min(c, curl[0]), curl[1])
            m = hand_clearance(mesh, side, base, top, spec["pommel_r"])
            if m["min_axis_dist"] is None or m["min_axis_dist"] >= spec["pommel_r"] + REST_CLEAR:
                if m["rest_gap"] is None or m["rest_gap"] >= REST_CLEAR:
                    best = (lift, min(c, curl[0]))
                    break
        if best:
            break
    if best is None:
        print("WARN rest: no clear rest for", side)
        best = (REST_LIFTS[-1], REST_CURLS[-1])
    rest_hand(arm, side, top_w, rot, pole, best[0])
    T.curl(arm, side, best[1], curl[1])
    print(f"REST {side} lift {best[0]} curl {best[1]} palm {_PALM[side]:+.0f}")
    return best


def grip_metrics(arm, mesh, side, ob, spec):
    """hand_clearance on a placed blade object's pommel."""
    bw = ob.matrix_world
    return hand_clearance(mesh, side, bw @ Vector((0, spec["pommel"][0], 0)), bw @ Vector((0, spec["pommel"][1], 0)),
                          spec["pommel_r"])


def rest_metrics(arm, mesh, blade_obs, p):
    """grip_metrics for every resting hand of pose p ({} when none rests)."""
    return {side: grip_metrics(arm, mesh, side, blade_obs[side], CFG["blades"][side])
            for side, b in (p.get("blades") or {}).items() if b.get("rest") and b.get("hand", True)}


def capture(root, arm, mesh, p):
    """Resolve a pose to the numbers the renderer interpolates."""
    apply_pose(root, arm, mesh, p)
    blades = {}
    for side, spec in (p.get("blades") or {}).items():
        bl = {"anchor": spec.get("anchor", "上半身2"), "at": Vector(spec["at"]), "rot": blade_frame(spec),
              "hand": bool(spec.get("hand", True)), "pole": Vector(spec.get("pole", (0.0, 0.5, -1.0))),
              # where on the handle the hand closes: the grip, or the pommel to rest on
              "grip": float(spec.get("grip", CFG["blades"][side]["grip"])), "rest": bool(spec.get("rest"))}
        blades[side] = bl
        if bl["hand"] and bl["rest"]:
            bl["lift"], _c = fit_rest(arm, mesh, side, anchor_point(arm, bl["anchor"]) + bl["at"], bl["rot"],
                                      bl["pole"], bl["grip"], spec.get("curl", (80, 40)))
        elif bl["hand"]:
            grip_hand(arm, side, anchor_point(arm, bl["anchor"]) + bl["at"], bl["rot"], bl["pole"])
            T.curl(arm, side, *spec.get("curl", (80, 40)))
    bones = {}
    for pb in arm.pose.bones:
        loc, rot, sc = pb.matrix_basis.decompose()
        bones[pb.name] = (loc.copy(), rot.copy(), sc.copy())
    return {
        "bones": bones,
        "morphs": {k.name: k.value for k in mesh.data.shape_keys.key_blocks[1:] if k.value},
        "root_rot": (0.0, math.radians(p.get("root_rot", 0.0)), math.radians(p["yaw"])),
        "root": Vector(p.get("root", (0, 0, 0))),
        "blades": blades,
    }


def set_frame(root, arm, mesh, blade_obs, caps, keys, t):
    i, j, u, _raw = T.at_time(keys, t)
    a, b = caps[i], caps[j]
    for pb in arm.pose.bones:
        la, qa, sa = a["bones"][pb.name]
        lb, qb, sb = b["bones"][pb.name]
        if qa.dot(qb) < 0:
            qb = -qb
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = Matrix.LocRotScale(la.lerp(lb, u), qa.slerp(qb, u), sa.lerp(sb, u))
    kb = mesh.data.shape_keys.key_blocks
    for k in kb[1:]:
        k.value = 0.0
    step = getattr(LIB, "STEP_MORPHS", set())
    for n in set(a["morphs"]) | set(b["morphs"]):
        va, vb = a["morphs"].get(n, 0.0), b["morphs"].get(n, 0.0)
        kb[n].value = (vb if u >= 0.5 else va) if n in step else va * (1 - u) + vb * u
    ru = tuple(x * (1 - u) + y * u for x, y in zip(a["root_rot"], b["root_rot"]))
    root.rotation_euler = ru
    root.location = a["root"].lerp(b["root"], u)
    T.upd()
    # The blades interpolate in the root's own frame, so a key pair that turns
    # him (a spin: the root's yaw changes) carries the blades round with his
    # body instead of cutting the chord; for keys at one root rotation this is
    # the plain world lerp.
    Ra, Rb, Ru = (Euler(e, "XYZ").to_matrix() for e in (a["root_rot"], b["root_rot"], ru))
    Ia, Ib = Ra.transposed(), Rb.transposed()
    qIa, qIb, qRu = Ia.to_quaternion(), Ib.to_quaternion(), Ru.to_quaternion()
    for side, ob in blade_obs.items():
        ba, bb = a["blades"].get(side), b["blades"].get(side)
        if ba is None and bb is None:
            ob.hide_render = True
            continue
        ob.hide_render = False
        ba, bb = ba or bb, bb or ba
        at = Ru @ (Ia @ ba["at"]).lerp(Ib @ bb["at"], u)
        if ba["anchor"] == bb["anchor"]:
            g = anchor_point(arm, ba["anchor"]) + at
        else:
            g = (anchor_point(arm, ba["anchor"]) + ba["at"]).lerp(anchor_point(arm, bb["anchor"]) + bb["at"], u)
        qa, qb = qIa @ ba["rot"], qIb @ bb["rot"]
        if qa.dot(qb) < 0:
            qb = -qb
        r = qRu @ qa.slerp(qb, u)
        place_blade(ob, g, r, ba["grip"] * (1 - u) + bb["grip"] * u)
        if ba["hand"] and bb["hand"]:
            pole = Ru @ (Ia @ ba["pole"]).lerp(Ib @ bb["pole"], u)
            if ba["rest"] and bb["rest"]:
                rest_hand(arm, side, g, r, pole, ba["lift"] * (1 - u) + bb["lift"] * u)
            else:
                grip_hand(arm, side, g, r, pole)
    T.upd()


def blade_points(cam_ob, ppu, blade_obs):
    """Per blade: the base (past the guard) and the tip, in canvas px."""
    out = {}
    for side, ob in blade_obs.items():
        if ob.hide_render:
            out[side] = None
            continue
        spec = CFG["blades"][side]
        mw = ob.matrix_world
        out[side] = [T.to_px(cam_ob, ppu, mw @ Vector((0, spec["base"], 0))),
                     T.to_px(cam_ob, ppu, mw @ Vector((0, spec["tip"], 0)))]
    return out


# ----------------------------------------------------------------- first look (one prop)
def place_prop(prop_root, arm, spec):
    """The first look's single prop: its grip (local +Y spec['grip']) at the palm."""
    R = blade_frame(spec).to_matrix().to_4x4()
    grip_w = R @ Vector((0, spec["grip"], 0, 0))
    prop_root.matrix_world = Matrix.Translation(arm.matrix_world @ palm(arm, spec["side"]) - grip_w.to_3d()) @ R
    T.upd()


# ----------------------------------------------------------------- main
def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable(T.MMD, default_set=True)
    root, arm, mesh = import_pmx(args.pmx or model_path(CFG["pmx"]))
    blade_obs = {}
    if LIB is not None and CFG.get("blades"):
        for side, spec in CFG["blades"].items():
            _r, _a, m_ = import_pmx(model_path(spec["pmx"]))
            m_.parent = None
            m_.modifiers.clear()            # a rigid prop: no armature to follow
            m_.matrix_world = Matrix.Identity(4)
            blade_obs[side] = m_
    prop = import_pmx(args.prop) if args.prop else None
    cam_ob = T.setup_render(args.samples)

    # the rest height, measured before any shading or hull, sets the scale
    T.upd()
    zs = [p.z for p in T.world_box([mesh])]
    rest_h = max(zs) - min(zs)
    ppu = args.ppu or CH.target_ppu(args.char, rest_h)
    print(f"SCALE rest height {rest_h:.4f} u -> ppu {ppu:.2f} -> {rest_h * ppu * CH.COMBAT_SCALE:.1f} px at 1080p")

    shade(mesh).thickness = args.outline_px / ppu
    for ob in blade_obs.values():
        shade(ob).thickness = args.outline_px / ppu
    if prop:
        shade(prop[2]).thickness = args.outline_px / ppu
    cam_h = CFG.get("camera_height", 0.8)
    objs = [mesh] + list(blade_obs.values())

    for name in [c for c in args.clips.split(",") if c]:
        spec = LIB.CLIPS[name]
        keys = spec["keys"]
        caps = [capture(root, arm, mesh, k[1]) for k in keys]
        fps = spec["fps"]
        if args.keys_only:
            times = [k[0] for k in keys]
        elif spec.get("motion_end"):
            times = [round(i / fps, 6) for i in range(int(round(spec["motion_end"] * fps)) + 1)]
        else:
            times = [round(i / fps, 6) for i in range(int(round(spec["length"] * fps)))]
        T.reset_camera(cam_ob, args.pitch, cam_h)
        pts = []
        for t in times:
            set_frame(root, arm, mesh, blade_obs, caps, keys, t)
            pts += T.world_box(objs)
        w, h, origin, _c = T.frame_camera(cam_ob, T.project(cam_ob, pts), ppu)
        d = os.path.join(args.out, "raw", name)
        os.makedirs(d, exist_ok=True)
        grip = {}
        for i, t in enumerate(times):
            set_frame(root, arm, mesh, blade_obs, caps, keys, t)
            if i == 0:
                grip = rest_metrics(arm, mesh, blade_obs, keys[0][1])
            T.render_to(os.path.join(d, f"f_{i:03d}.png"))
        track = []
        if blade_obs and not args.keys_only:
            for i in range((len(times) - 1) * SUBSTEPS + 1):
                t = round(i / (fps * SUBSTEPS), 6)
                set_frame(root, arm, mesh, blade_obs, caps, keys, t)
                track.append({"t": t, **blade_points(cam_ob, ppu, blade_obs)})
        meta = {"clip": name, "char": args.char, "fps": fps, "length": spec["length"], "loop": spec["loop"],
                "motion_end": spec.get("motion_end"), "times": times, "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": round(ppu, 4),
                "pitch": args.pitch, "keys_only": args.keys_only, "events": dict(spec.get("events", {})),
                "trails": spec.get("trails", []), "bursts": spec.get("bursts", []),
                "effects": spec.get("effects", []),
                "substeps": SUBSTEPS, "blades": track}
        if grip:
            meta["grip"] = grip
        with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        print("CLIP", name, len(times), "frames", (w, h), "origin", origin)

    stills = dict(getattr(LIB, "STILLS", {}))
    stills.setdefault("rest", CH.REST)
    stills.setdefault("stance", CFG["stance"])
    for name in [s for s in args.stills.split(",") if s]:
        p = stills[name]
        cap = capture(root, arm, mesh, p)
        set_frame(root, arm, mesh, blade_obs, [cap], [(0.0, p, "io")], 0.0)
        fobjs = list(objs)
        if prop:
            on = p.get("prop") is not None
            prop[2].hide_render = not on
            if on:
                place_prop(prop[0], arm, p["prop"])
                fobjs.append(prop[2])
        T.reset_camera(cam_ob, args.pitch, cam_h)
        w, h, origin, _c = T.frame_camera(cam_ob, T.project(cam_ob, T.world_box(fobjs)), ppu)
        grip = rest_metrics(arm, mesh, blade_obs, p)
        T.render_to(os.path.join(args.out, "raw", f"{name}.png"))
        hips = arm.matrix_world @ arm.pose.bones["下半身"].head
        head = arm.matrix_world @ arm.pose.bones["頭"].head      # the neck joint, under the chin
        meta = {"still": name, "char": args.char, "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": round(ppu, 4),
                "hips_px": T.to_px(cam_ob, ppu, hips), "head_px": T.to_px(cam_ob, ppu, head),
                "rest_height_units": round(rest_h, 5), "pitch": args.pitch, "combat_scale": CH.COMBAT_SCALE}
        if grip:
            meta["grip"] = grip
        with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        print("STILL", name, (w, h), origin)


main()
