"""Build the Bake-Kurage in Blender from primitives and render its clips, headless.

    blender -b --factory-startup -P tools/kurage_render/render.py -- --out <scratch dir> [--clips idle,attack]

No model is read: the jellyfish is made here (clips.py says what and why),
so nothing licensed enters the render. Per clip it writes
<out>/raw/<clip>/f_NNN.png and <out>/<clip>.json (fps, length, times, the
canvas and the anchor's pixel); tools/kurage_render/pack.py outlines and
packs them. No .blend is saved.

THE LOOK. Unlit and translucent, so it reads as water beside the toon-shaded
kits without a light rig: every surface is an emission blended over
transparency. The bell is pale at its centre and deep Hydro blue at its
silhouette (a facing ramp), with its back faces drawn so the inside of the
bell shows through the front; the coral-pink band runs round the rim; a
pearly core sits inside it, a glint on its shoulder. The tentacles are
camera-facing ribbons whose alpha fades toward the tip. The outline is drawn
in 2D by pack.py, round the silhouette only (an inverted hull would show
through a translucent bell).

Every mesh keeps one topology; each frame only moves vertices, from the
clip's eased bell state (clips.at) plus the breathing pulse and the
tentacles' travelling wave. Deterministic: same clips, same pixels.
"""
import argparse
import importlib.util
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("kurage_clips", os.path.join(HERE, "clips.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--clips", default=",".join(C.CLIPS))
ap.add_argument("--samples", type=int, default=16)
args = ap.parse_args(argv)

NA = 40                  # bell: segments round
NS = 16                  # bell: rings from the crown to the rim
NSEG = 20                # ribbon segments
RIM_FROM = 0.84          # the bell rings past this fraction are the pink band


def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


# ----------------------------------------------------------------- materials
def _nodes(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(mat, attr, val)
            break
        except (AttributeError, TypeError):
            continue
    mat.use_backface_culling = False
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return mat, nt, mix, em


def math_node(nt, op, a, b=None, clamp=True):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def facing_material(name, inner, outer, a_inner, a_outer, blend=0.35, power=1.0):
    """Colour and alpha ramped from where the surface faces the camera
    (inner) to its silhouette (outer)."""
    mat, nt, mix, em = _nodes(name)
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = blend
    f = math_node(nt, "POWER", lw.outputs["Facing"], power)
    col = nt.nodes.new("ShaderNodeMix")
    col.data_type = "RGBA"
    nt.links.new(f, col.inputs["Factor"])
    col.inputs[6].default_value = lin(inner)
    col.inputs[7].default_value = lin(outer)
    nt.links.new(col.outputs[2], em.inputs["Color"])
    a = math_node(nt, "MULTIPLY_ADD", f, a_outer - a_inner)
    a.node.inputs[2].default_value = a_inner
    nt.links.new(a, mix.inputs[0])
    return mat


def ribbon_material(name, color, alpha):
    """Flat colour; alpha from the mesh's `fade` attribute (1 at the root)."""
    mat, nt, mix, em = _nodes(name)
    em.inputs["Color"].default_value = lin(color)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "fade"
    nt.links.new(math_node(nt, "MULTIPLY", at.outputs["Fac"], alpha), mix.inputs[0])
    return mat


def flat_material(name, color, alpha):
    mat, nt, mix, em = _nodes(name)
    em.inputs["Color"].default_value = lin(color)
    mix.inputs[0].default_value = alpha
    return mat


# ----------------------------------------------------------------- meshes
def new_object(name, verts, faces, mats, fade=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for m in mats:
        me.materials.append(m)
    if fade is not None:
        at = me.attributes.new("fade", "FLOAT", "POINT")
        at.data.foreach_set("value", fade)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def bell_rest():
    """The bell's rest vertices as (s, theta) pairs and its faces: a dome from
    the crown (s=0) to the rim (s=1), scalloped at the rim."""
    params = [(0.0, 0.0)]
    for i in range(1, NS + 1):
        for j in range(NA):
            params.append((i / NS, 2 * math.pi * j / NA))
    faces, mats = [], []
    for j in range(NA):
        faces.append((0, 1 + j, 1 + (j + 1) % NA))
        mats.append(0)
    for i in range(1, NS):
        for j in range(NA):
            a, b = 1 + (i - 1) * NA + j, 1 + (i - 1) * NA + (j + 1) % NA
            faces.append((a, a + NA, b + NA, b))
            mats.append(1 if i / NS >= RIM_FROM else 0)
    return params, faces, mats


def sphere(name, rings, segs, mat):
    verts = [(0, 0, 1)]
    for i in range(1, rings):
        a = math.pi * i / rings
        for j in range(segs):
            b = 2 * math.pi * j / segs
            verts.append((math.sin(a) * math.cos(b), math.sin(a) * math.sin(b), math.cos(a)))
    verts.append((0, 0, -1))
    faces = [(0, 1 + j, 1 + (j + 1) % segs) for j in range(segs)]
    for i in range(rings - 2):
        for j in range(segs):
            a, b = 1 + i * segs + j, 1 + i * segs + (j + 1) % segs
            faces.append((a, a + segs, b + segs, b))
    last = len(verts) - 1
    base = 1 + (rings - 2) * segs
    faces += [(base + j, last, base + (j + 1) % segs) for j in range(segs)]
    return new_object(name, verts, faces, [mat])


def ribbon(name, mat, fade_alpha):
    verts = [(0, 0, 0)] * (2 * (NSEG + 1))
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(NSEG)]
    fade = []
    for i in range(NSEG + 1):
        s = i / NSEG
        fade += [fade_alpha(s)] * 2
    return new_object(name, verts, faces, [mat], fade)


# ----------------------------------------------------------------- the pose
def body_xf(st, t):
    """The bell's frame transform at time t: (fn mapping a rest point, the
    down direction, the screen-right direction, the effective pinch)."""
    p = C.pulse(t)
    sx = st["sx"] * (1 - 0.05 * p)
    sz = st["sz"] * (1 + 0.06 * p)
    pinch = min(1.0, st["pinch"] + 0.5 * p)
    phi = math.radians(st["tilt"])
    cphi, sphi = math.cos(phi), math.sin(phi)
    cz = C.BELL_CENTRE

    def xf(x, y, z):
        x, y, z = x * sx, y * sx, cz + (z - cz) * sz
        dz = z - cz
        return (x * cphi + dz * sphi, y, cz - x * sphi + dz * cphi + st["lift"])
    # the tentacles hang along the bell's axis; limp (droop) they hang plumb
    g = st["droop"]
    dx, dz = -sphi * (1 - g), -cphi * (1 - g) - g
    n = math.hypot(dx, dz)
    down = (dx / n, 0.0, dz / n)
    right = (-down[2], 0.0, down[0])
    return xf, down, right, pinch


def bell_point(s, th, pinch, droop):
    a = s * math.pi / 2
    r = C.BELL_R * math.sin(a) * (1 + 0.05 * s ** 4 * math.cos(8 * th)) * (1 - 0.24 * pinch * s * s)
    r *= 1 + 0.18 * droop * s * s
    z = C.BELL_RIM + (C.BELL_TOP - C.BELL_RIM) * math.cos(a) - 0.12 * droop * s * s
    return r * math.cos(th), r * math.sin(th), z


def set_verts(ob, pts):
    flat = [c for p in pts for c in p]
    ob.data.vertices.foreach_set("co", flat)
    ob.data.update()


def pose_frame(objs, clip, t):
    st = C.at(clip, t)
    xf, down, right, pinch = body_xf(st, t)
    bell, pearl, glint, tents, orals = objs
    set_verts(bell, [xf(*bell_point(s, th, pinch, st["droop"])) for s, th in BELL_PARAMS])
    # the pearly core and the glint ride the bell
    for ob, at, rad in ((pearl, (0.0, 0.02, 1.0), (0.19, 0.19, 0.17)), (glint, (-0.27, -0.42, 1.12), (0.07, 0.03, 0.045))):
        cx, cy, cz = xf(*at)
        k = (st["sx"], st["sx"], st["sz"])
        ob.matrix_world = Matrix.Translation((cx, cy, cz)) @ Matrix.Diagonal((rad[0] * k[0], rad[1] * k[1], rad[2] * k[2], 1))
    for n, (ob, length, th, phase, width, frill) in enumerate(tents + orals):
        base_r = (0.80 if not frill else 0.22) * C.BELL_R
        bx, by, bz = xf(*bell_point(1.0, th, pinch, st["droop"])) if not frill else xf(
            base_r * math.cos(th), base_r * math.sin(th), C.BELL_RIM + 0.06)
        if not frill:
            # from just inside the rim
            cx, cy, _ = xf(0.0, 0.0, C.BELL_RIM)
            bx, by = cx + (bx - cx) * 0.8, cy + (by - cy) * 0.8
        pts = []
        for i in range(NSEG + 1):
            s = i / NSEG
            L = length * s * (1 - 0.16 * abs(st["trail"]) * s) * (1 - 0.15 * st["droop"] * s)
            side = st["sway"] * (0.16 if not frill else 0.07) * s ** 1.2 * C.wave(t, s, phase)
            if frill:
                side += 0.045 * s * math.sin(16 * s - 4 * math.pi * t / C.LOOP + phase)
            side -= st["trail"] * 0.46 * s ** 1.6
            px = bx + down[0] * L + right[0] * side
            pz = bz + down[2] * L + right[2] * side
            w = width * (1 - (0.72 if not frill else 0.45) * s) / 2
            pts += [(px - right[0] * w, by, pz - right[2] * w), (px + right[0] * w, by, pz + right[2] * w)]
        set_verts(ob, pts)
    bpy.context.view_layer.update()


# ----------------------------------------------------------------- scene
def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    try:
        sc.eevee.taa_render_samples = args.samples
    except AttributeError:
        pass
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = world
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam_ob = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(cam_ob)
    sc.camera = cam_ob
    w = int(round((C.VIEW_X[1] - C.VIEW_X[0]) * C.PPU))
    h = int(round((C.VIEW_Z[1] - C.VIEW_Z[0]) * C.PPU))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    cam.ortho_scale = max(w, h) / C.PPU
    cx, cz = sum(C.VIEW_X) / 2, sum(C.VIEW_Z) / 2
    p = math.radians(C.PITCH)
    # looking down by PITCH, aimed so the window's centre is the image's
    cam_ob.matrix_world = Matrix.Translation((cx, -10 * math.cos(p), cz + 10 * math.sin(p))) @ \
        Matrix.Rotation(math.radians(90 - C.PITCH), 4, "X")
    bpy.context.view_layer.update()
    return cam_ob, w, h


def to_px(cam_ob, w, h, v):
    q = cam_ob.matrix_world.inverted() @ Vector(v)
    return [round((q.x + (w / C.PPU) / 2) * C.PPU, 3), round(((h / C.PPU) / 2 - q.y) * C.PPU, 3)]


def build():
    col = C.COLORS
    bell_mat = facing_material("bell", col["bell_core"], col["bell_edge"], 0.46, 0.94, blend=0.4, power=1.3)
    rim_mat = flat_material("rim", col["rim"], 0.94)
    pearl_mat = facing_material("pearl", col["pearl"], (0.55, 0.82, 1.0), 0.92, 0.85, blend=0.5)
    glint_mat = flat_material("glint", col["glint"], 0.9)
    tent_mat = ribbon_material("tentacle", col["tentacle"], 0.9)
    oral_mat = ribbon_material("oral", col["oral"], 0.92)
    params, faces, mats = bell_rest()
    bell = new_object("bell", [(0, 0, 0)] * len(params), faces, [bell_mat, rim_mat])
    bell.data.polygons.foreach_set("material_index", mats)
    pearl = sphere("pearl", 10, 20, pearl_mat)
    glint = sphere("glint", 6, 12, glint_mat)
    tents = []
    lo, hi = C.TENTACLE_LEN
    for j in range(C.TENTACLES):
        th = 2 * math.pi * (j + 0.5) / C.TENTACLES
        length = lo + (hi - lo) * ((j * 3) % C.TENTACLES) / (C.TENTACLES - 1)
        ob = ribbon(f"tentacle_{j}", tent_mat, lambda s: 1 - 0.85 * s ** 1.6)
        tents.append((ob, length, th, 1.1 * j, 0.085, False))
    orals = []
    for j in range(C.ORAL_ARMS):
        th = 2 * math.pi * j / C.ORAL_ARMS + 0.3
        ob = ribbon(f"oral_{j}", oral_mat, lambda s: 1 - 0.7 * s ** 2)
        orals.append((ob, C.ORAL_LEN * (0.9 + 0.1 * j), th, 2.0 + 1.7 * j, 0.15, True))
    return params, (bell, pearl, glint, tents, orals)


cam_ob, W, H = setup()
BELL_PARAMS, OBJS = build()
origin = to_px(cam_ob, W, H, (0.0, 0.0, 0.0))
for name in [c for c in args.clips.split(",") if c]:
    clip = C.CLIPS[name]
    ts = C.times(clip)
    d = os.path.join(args.out, "raw", name)
    os.makedirs(d, exist_ok=True)
    for i, t in enumerate(ts):
        pose_frame(OBJS, clip, t)
        bpy.context.scene.render.filepath = os.path.join(d, f"f_{i:03d}.png")
        bpy.ops.render.render(write_still=True)
    meta = {"clip": name, "fps": clip["fps"], "length": clip["length"], "loop": clip["loop"], "times": ts,
            "canvas": [W, H], "origin_px": origin, "ppu": C.PPU, "pitch": C.PITCH}
    with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print("CLIP", name, len(ts), "frames", (W, H), "origin", origin)
