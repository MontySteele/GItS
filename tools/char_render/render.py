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
ap.add_argument("--guests", default="", help="Furina's guest stars (chars.GUESTS), one still each, at --ppu "
                                             "(Furina's combat ppu) scaled by chars.guest_ppu")
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


def drop_overlays(mesh, cfg):
    """Delete the faces of the overlay shells (chars.is_overlay) and hidden
    materials outright. A guest's 颜+ blush overlay, merely hidden, still
    rendered as a black mask over the whole face (Sigewinne, Escoffier,
    Navia; probed 2026-10-13); with its faces gone the face reads. Vertex
    groups and shape keys ride through BMesh."""
    import bmesh
    hide = cfg.get("hide_mats", set())
    drop = [i for i, m in enumerate(mesh.data.materials) if CH.is_overlay(m.name) or m.name in hide]
    if not drop:
        return
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in drop], context="FACES_ONLY")
    bm.to_mesh(mesh.data)
    bm.free()
    mesh.data.update()


def shade(mesh, cfg=None):
    """Style H1 on every material of one imported mesh, plus its hull."""
    cfg = cfg or CFG
    face, no_line = cfg["face_mats"], set(cfg["no_line_mats"])
    hide = cfg.get("hide_mats", set())
    lines = []
    for m in mesh.data.materials:
        if CH.is_overlay(m.name) or m.name in hide:
            T.hidden_material(m)
            no_line.add(m.name)
            lines.append(T.line_material(m, None, False))
            continue
        img = T.base_image(m)
        T.toon_material(m, img, m.name in face, m.name in cfg.get("alpha_mats", ()))
        lines.append(T.line_material(m, img, m.name in face))
    hull = T.add_outline(mesh, lines, no_line)
    if CFG.get("mouth_mat"):
        unline_mouth(mesh, CFG["mouth_mat"])
    return hull


#: the margin round the mouth's own geometry inside which the face's skin
#: draws no outline (units; x across the face, z up)
MOUTH_UNLINE = (0.012, 0.006)


def unline_mouth(mesh, mouth_mat):
    """The face's hull folds into the lips, so at select scale it draws dark
    ticks at the mouth's corners and a heavy upper lip (a grimace, whatever
    the morphs say). Take the skin round the mouth (the mouth material's
    rest box, widened by MOUTH_UNLINE) out of the outline's vertex group."""
    mats = [m.name if m else "" for m in mesh.data.materials]
    if mouth_mat not in mats:          # a blade, or a guest's body
        return
    mi = mats.index(mouth_mat)
    vs = {i for p in mesh.data.polygons if p.material_index == mi for i in p.vertices}
    xs = [mesh.data.vertices[i].co.x for i in vs]
    zs = [mesh.data.vertices[i].co.z for i in vs]
    ys = [mesh.data.vertices[i].co.y for i in vs]
    mx, mz = MOUTH_UNLINE
    x0, x1, z0, z1 = min(xs) - mx, max(xs) + mx, min(zs) - mz, max(zs) + mz
    y0, y1 = min(ys) - 0.05, max(ys) + 0.05
    vg = mesh.vertex_groups["outline_w"]
    face = {i for i, n in enumerate(mats) if n in CFG["face_mats"]}
    drop = {i for p in mesh.data.polygons if p.material_index in face for i in p.vertices
            if x0 <= mesh.data.vertices[i].co.x <= x1 and z0 <= mesh.data.vertices[i].co.z <= z1
            and y0 <= mesh.data.vertices[i].co.y <= y1}
    vg.remove(list(drop))
    print("UNLINE mouth", len(drop), "verts")


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


#: ARMS CROSSED (stance B: the shop loop and the select close-up). [USER],
#: 2026-10-13: "I dont think the "hands over sword" thing is working for
#: Varka. Can we have him cross his arms instead, with his swords infront of
#: him?" His arms are posed by the pose's own ops (varka_clips.regal), each
#: hand tucked into the crossed arms; both claymores stand free, planted
#: point-down in front of him. arms_crossed() measures the result on the
#: deformed mesh, for the manifest and its test: how far any forearm or hand
#: vertex sinks behind the surface of the other arm or of the body (a
#: forearm through a forearm, a gauntlet through his chest), and where the
#: blades' tops sit on the canvas against his chin and his crossed forearms.
SINK_REACH = 0.08        # a vertex further than this from a surface is not "in" it (units)
_PARTS = {}


def deformed_world(mesh):
    """Every vertex of the deformed body (the outline hull off), world space."""
    import numpy as np
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
    mw = np.array(mesh.matrix_world)
    return co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]


def _arm_group(name, side):
    """A bone of one arm from the shoulder down: upper arm, forearm, hand."""
    return name.endswith(f".{side}") and any(k in name for k in ("腕", "ひじ", "手", "指"))


def _fore_group(name, side):
    return _arm_group(name, side) and not name.startswith("腕")


def body_parts(mesh):
    """Vertex masks, cached per mesh: per side the forearm and hand
    (`fore`: the vertices those bones move most), the whole arm (`arm`: any
    weight on it), and `body` (no weight on either arm)."""
    import numpy as np
    if mesh.name in _PARTS:
        return _PARTS[mesh.name]
    # bone weights only (mmd_tools adds its own groups, mmd_edge_scale and the like, at full weight)
    names = {g.index: g.name for g in mesh.vertex_groups if not g.name.startswith("mmd_")}
    n = len(mesh.data.vertices)
    fore = {s: np.zeros(n, bool) for s in "LR"}
    armw = {s: np.zeros(n, bool) for s in "LR"}
    for v in mesh.data.vertices:
        best, bw = None, 0.0
        for g in v.groups:
            nm = names.get(g.group)
            if nm is None:
                continue
            for s in "LR":
                if g.weight > 0.02 and _arm_group(nm, s):
                    armw[s][v.index] = True
            if g.weight > bw:
                best, bw = nm, g.weight
        for s in "LR":
            if best and _fore_group(best, s):
                fore[s][v.index] = True
    out = {"fore": fore, "arm": armw, "body": ~(armw["L"] | armw["R"])}
    _PARTS[mesh.name] = out
    return out


def sink_depth(P, co, mesh, mask):
    """How far the points P sink behind the surface made of the polygons
    whose vertices all lie in `mask`: (deepest, how many deeper than 0.01)."""
    from mathutils.bvhtree import BVHTree
    polys = [tuple(p.vertices) for p in mesh.data.polygons if all(mask[i] for i in p.vertices)]
    if not polys:
        return 0.0, 0
    tree = BVHTree.FromPolygons([Vector(c) for c in co], polys)
    deep, n = 0.0, 0
    for p in P:
        v = Vector(p)
        hit = tree.find_nearest(v, SINK_REACH)
        if hit[0] is None:
            continue
        d = -(v - hit[0]).dot(hit[1])
        if d > deep:
            deep = d
        if d > 0.01:
            n += 1
    return round(deep, 4), n


#: px of background each hilt keeps from his silhouette (dilation of the hilt
#: before the overlap count)
HILT_GAP_PX = 3


def _hilt_local(ob, base):
    """(guard bottom, guard top) in the blade's local Y. The guard runs from
    `base` (chars.py: the blade just past the guard) up to the top of the
    blade's widest part (|x| over 3/4 of the widest: the crossguard's fins),
    so the hilt is the guard and everything above it (grip, pommel)."""
    if "hilt_y" not in ob:
        xs = [abs(v.co.x) for v in ob.data.vertices]
        wide = max(xs) * 0.75
        ys = [v.co.y for v in ob.data.vertices if abs(v.co.x) > wide]
        ob["hilt_y"] = (min(min(ys), base), max(ys))
    return tuple(ob["hilt_y"])


def _raster(cam_ob, ppu, pts, tris, size):
    """A bool mask (rows, cols) of the triangles `tris` (index tuples into the
    world points pts, fans for quads) on the canvas, and the points' px."""
    import numpy as np
    w, h = size
    px = np.array([T.to_px(cam_ob, ppu, p) for p in pts], np.float64)
    m = np.zeros((h, w), bool)
    for t in tris:
        for j in range(1, len(t) - 1):
            a, b, c = px[t[0]], px[t[j]], px[t[j + 1]]
            x0, x1 = int(max(0, np.floor(min(a[0], b[0], c[0])))), int(min(w - 1, np.ceil(max(a[0], b[0], c[0]))))
            y0, y1 = int(max(0, np.floor(min(a[1], b[1], c[1])))), int(min(h - 1, np.ceil(max(a[1], b[1], c[1]))))
            if x1 < x0 or y1 < y0:
                continue
            d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(d) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / d
            l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / d
            m[y0:y1 + 1, x0:x1 + 1] |= (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
    return m, px.tolist()


def _grow(m, r):
    """The mask grown by r px (a square)."""
    import numpy as np
    out = m.copy()
    h, w = m.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            src = m[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
            out[max(0, dy):max(0, dy) + src.shape[0], max(0, dx):max(0, dx) + src.shape[1]] |= src
    return out


def hilts(mesh, blade_obs, cam_ob, ppu, co):
    """Per blade on the canvas (px): the hilt's box, the guard's box, and how
    many px of the hilt (grown by HILT_GAP_PX) fall on his body's silhouette."""
    sc = bpy.context.scene
    size = (sc.render.resolution_x, sc.render.resolution_y)
    B, _ = _raster(cam_ob, ppu, [Vector(c) for c in co], [tuple(p.vertices) for p in mesh.data.polygons], size)
    out = {}
    for side, ob in blade_obs.items():
        if ob.hide_render:
            continue
        g0, g1 = _hilt_local(ob, CFG["blades"][side]["base"])
        mw = ob.matrix_world
        keep = [v.index for v in ob.data.vertices if v.co.y >= g0]
        ks = set(keep)
        pts = [mw @ v.co for v in ob.data.vertices]
        tris = [tuple(p.vertices) for p in ob.data.polygons if all(i in ks for i in p.vertices)]
        H, px = _raster(cam_ob, ppu, pts, tris, size)
        H = _grow(H, HILT_GAP_PX)
        hp = [px[i] for i in keep]
        gp = [px[v.index] for v in ob.data.vertices if g0 <= v.co.y <= g1]

        def box(q):
            return [round(min(p[0] for p in q), 1), round(min(p[1] for p in q), 1),
                    round(max(p[0] for p in q), 1), round(max(p[1] for p in q), 1)]
        out[side] = {"hilt_box_px": box(hp), "guard_box_px": box(gp), "on_body_px": int((H & B).sum())}
    return out


def arms_crossed(arm, mesh, blade_obs, cam_ob, ppu):
    """Stance B's measure (the manifest's `arms_crossed`): each forearm's
    deepest sink into the other arm and into the body; where his forearms
    span on the canvas (y px, down), the chin, and each blade's top."""
    co = deformed_world(mesh)
    parts = body_parts(mesh)
    out = {}
    for s, o in (("L", "R"), ("R", "L")):
        P = co[parts["fore"][s]]
        d_arm, n_arm = sink_depth(P, co, mesh, parts["arm"][o] & ~parts["arm"][s])
        d_body, n_body = sink_depth(P, co, mesh, parts["body"])
        out[s] = {"into_other_arm": d_arm, "into_other_arm_n": n_arm, "into_body": d_body, "into_body_n": n_body}
    ys = [T.to_px(cam_ob, ppu, Vector(p))[1] for s in "LR" for p in co[parts["fore"][s]][::5]]
    out["forearms_px"] = [round(min(ys), 1), round(max(ys), 1)]
    out["chin_px"] = T.to_px(cam_ob, ppu, arm.matrix_world @ arm.pose.bones["頭"].head)[1]
    tops = {}
    for side, ob in blade_obs.items():
        if not ob.hide_render:
            tops[side] = round(min(T.to_px(cam_ob, ppu, c)[1] for c in T.world_box([ob])), 1)
    out["blade_top_px"] = tops
    out["hilts"] = hilts(mesh, blade_obs, cam_ob, ppu, co)
    return out


def capture(root, arm, mesh, p):
    """Resolve a pose to the numbers the renderer interpolates."""
    apply_pose(root, arm, mesh, p)
    blades = {}
    for side, spec in (p.get("blades") or {}).items():
        bl = {"anchor": spec.get("anchor", "上半身2"), "at": Vector(spec["at"]), "rot": blade_frame(spec),
              "hand": bool(spec.get("hand", True)), "pole": Vector(spec.get("pole", (0.0, 0.5, -1.0))),
              # where on the handle the hand closes (a free blade: the point set at `at`)
              "grip": float(spec.get("grip", CFG["blades"][side]["grip"]))}
        blades[side] = bl
        if bl["hand"]:
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
            grip_hand(arm, side, g, r, pole)
    T.upd()


def phantom_points(cam_ob, ppu, arm):
    """Per phantom blade (the pose library's PHANTOM, {side: length}): a line
    from the hand's knuckles along the hand, as if it held a blade, in canvas
    px -- Furina's empty-handed rapier."""
    out = {}
    pbs = arm.pose.bones
    for side, length in getattr(LIB, "PHANTOM", {}).items():
        w = arm.matrix_world @ pbs[f"手首.{side}"].head
        k = arm.matrix_world @ pbs[f"{CFG['hand_tip']}.{side}"].head
        d = (k - w).normalized()
        out[side] = [T.to_px(cam_ob, ppu, k), T.to_px(cam_ob, ppu, k + d * length)]
    return out


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


# ----------------------------------------------------------------- the guest stars
def _fore_group(name, side):
    """A forearm or hand bone of one side (elbow, wrist twist, wrist, fingers)."""
    return name.endswith(f".{side}") and not name.startswith("腕") and any(k in name for k in ("ひじ", "手", "指"))


def forearms_visible(arm, mesh, cam_ob):
    """Per side, the share of the forearm and hand (the vertices those bones
    move most) that the camera sees: a vertex is seen when the ray from it
    toward the camera meets nothing, or only that same forearm, on the way
    ([USER], 2026-10-13: "where are Siegwinne and Neuvillette's arms?")."""
    import numpy as np
    from mathutils.bvhtree import BVHTree
    hull = mesh.modifiers.get("outline")
    if hull:
        hull.show_viewport = False
    T.upd()
    dg = bpy.context.evaluated_depsgraph_get()
    me = mesh.evaluated_get(dg).to_mesh()
    assert len(me.vertices) == len(mesh.data.vertices), "the hull is off: one deformed vertex per body vertex"
    mw = mesh.matrix_world
    co = [mw @ v.co for v in me.vertices]
    mesh.evaluated_get(dg).to_mesh_clear()
    if hull:
        hull.show_viewport = True
    T.upd()
    names = {g.index: g.name for g in mesh.vertex_groups if not g.name.startswith("mmd_") and g.name != "outline_w"}
    dom = []
    for v in mesh.data.vertices:
        best, bw = "", 0.0
        for g in v.groups:
            if g.group in names and g.weight > bw:
                best, bw = names[g.group], g.weight
        dom.append(best)
    polys = list(mesh.data.polygons)        # drop_overlays already removed the hidden shells
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in polys])
    to_cam = (cam_ob.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    out = {}
    for side in ("L", "R"):
        idx = [i for i, n in enumerate(dom) if _fore_group(n, side)]
        own = set(idx)
        seen = 0
        for i in idx:
            o = co[i] + to_cam * 0.002
            hit = tree.ray_cast(o, to_cam)
            while hit[0] is not None and all(j in own for j in polys[hit[2]].vertices):
                hit = tree.ray_cast(hit[0] + to_cam * 0.001, to_cam)
            if hit[0] is None:
                seen += 1
        out[side] = round(seen / len(idx), 3) if idx else None
    return out


def render_guests(names, furina_ppu):
    """Each guest star in ONE neutral resting pose (the pose library's
    guest_pose), shaded and outlined as Furina is, at chars.guest_ppu, as
    <out>/raw/guest_<name>.png and its json. A fresh scene per guest."""
    global CFG
    base = CFG
    for name in names:
        g = CH.GUESTS[name]
        CFG = {**base, "face_mats": base["face_mats"] | g.get("face", set()),
               "no_line_mats": base["no_line_mats"] | g.get("face", set()),
               "hide_mats": set(g.get("hide", set()))}
        bpy.ops.wm.read_factory_settings(use_empty=True)
        addon_utils.enable(T.MMD, default_set=True)
        root, arm, mesh = import_pmx(model_path(g["pmx"]))
        missing = [b for b in ("センター", "足ＩＫ.L", "足ＩＫ.R", "上半身", "上半身2", "首", "頭", "足.L", "足.R",
                               "腕.L", "腕.R", "ひじ.L", "ひじ.R", "手首.L", "手首.R", "中指１.L", "中指１.R")
                   if b not in arm.pose.bones]
        if missing:
            print("WARN guest", name, "missing bones", missing)
            continue
        cam_ob = T.setup_render(args.samples)
        T.upd()
        zs = [p.z for p in T.world_box([mesh])]
        rest_h = max(zs) - min(zs)
        head_u = (arm.matrix_world @ arm.pose.bones["頭"].head).z - min(zs)
        ppu = CH.guest_ppu(name, furina_ppu)
        drop_overlays(mesh, CFG)
        shade(mesh).thickness = args.outline_px / ppu
        k = g["head"] / CH.FURINA_HEAD
        p = LIB.guest_pose(k, name)
        cap = capture(root, arm, mesh, p)
        set_frame(root, arm, mesh, {}, [cap], [(0.0, p, "io")], 0.0)
        T.reset_camera(cam_ob, args.pitch, CFG.get("camera_height", 0.8) * k)
        w, h, origin, _c = T.frame_camera(cam_ob, T.project(cam_ob, T.world_box([mesh])), ppu)
        still = f"guest_{name}"
        seen = forearms_visible(arm, mesh, cam_ob)
        T.render_to(os.path.join(args.out, "raw", f"{still}.png"))
        head = arm.matrix_world @ arm.pose.bones["頭"].head
        meta = {"still": still, "guest": name, "char": "furina", "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": round(ppu, 4),
                "head_px": T.to_px(cam_ob, ppu, head), "rest_height_units": round(rest_h, 5),
                "head_units": round(head_u, 5), "height_in": CH.GUEST_HEIGHTS_IN[name], "pitch": args.pitch,
                "combat_scale": CH.COMBAT_SCALE, "forearms_visible": seen}
        with open(os.path.join(args.out, f"{still}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        print("STILL", still, (w, h), origin, f"ppu {ppu:.2f}", "forearms seen", seen,
              f"head {head_u * ppu * CH.COMBAT_SCALE:.1f} px at 1080p")
    CFG = base


# ----------------------------------------------------------------- main
def main():
    if args.guests:
        render_guests([g for g in args.guests.split(",") if g], args.ppu)
        return
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
        spec = LIB.CLIPS.get(name) or LIB.SELECT_LOOPS[name]
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
        crossed = {}
        for i, t in enumerate(times):
            set_frame(root, arm, mesh, blade_obs, caps, keys, t)
            if i == 0 and keys[0][1].get("arms_crossed"):
                crossed = arms_crossed(arm, mesh, blade_obs, cam_ob, ppu)
            T.render_to(os.path.join(d, f"f_{i:03d}.png"))
        track = []
        if (blade_obs or getattr(LIB, "PHANTOM", None)) and not args.keys_only:
            for i in range((len(times) - 1) * SUBSTEPS + 1):
                t = round(i / (fps * SUBSTEPS), 6)
                set_frame(root, arm, mesh, blade_obs, caps, keys, t)
                track.append({"t": t, **blade_points(cam_ob, ppu, blade_obs), **phantom_points(cam_ob, ppu, arm)})
        meta = {"clip": name, "char": args.char, "fps": fps, "length": spec["length"], "loop": spec["loop"],
                "motion_end": spec.get("motion_end"), "times": times, "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": round(ppu, 4),
                "pitch": args.pitch, "keys_only": args.keys_only, "events": dict(spec.get("events", {})),
                "trails": spec.get("trails", []), "bursts": spec.get("bursts", []),
                "effects": spec.get("effects", []),
                "substeps": SUBSTEPS, "blades": track}
        if crossed:
            meta["arms_crossed"] = crossed
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
        crossed = arms_crossed(arm, mesh, blade_obs, cam_ob, ppu) if p.get("arms_crossed") else {}
        T.render_to(os.path.join(args.out, "raw", f"{name}.png"))
        hips = arm.matrix_world @ arm.pose.bones["下半身"].head
        head = arm.matrix_world @ arm.pose.bones["頭"].head      # the neck joint, under the chin
        meta = {"still": name, "char": args.char, "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": round(ppu, 4),
                "hips_px": T.to_px(cam_ob, ppu, hips), "head_px": T.to_px(cam_ob, ppu, head),
                "rest_height_units": round(rest_h, 5), "pitch": args.pitch, "combat_scale": CH.COMBAT_SCALE}
        if crossed:
            meta["arms_crossed"] = crossed
        with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        print("STILL", name, (w, h), origin)


main()
