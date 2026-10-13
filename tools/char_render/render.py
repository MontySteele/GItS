"""Pose and style-G toon-render one official kit model headless, in Blender.

    blender -b --factory-startup -P tools/char_render/render.py -- \
        --char furina --pmx <【芙宁娜】.pmx> --out <scratch dir> \
        [--prop <武器.pmx>] [--stills rest,stance] [--ppu N]

THE MODEL NEVER ENTERS THE REPO. The PMX is read in place from the
operator's scratch directory (models/<char>/unpacked/); its terms forbid
redistribution and commercial use, so only the rendered PNGs leave it. No
.blend is ever saved.

Writes, per still, <out>/raw/<name>.png with its `style` pass in
<out>/raw/aux/<name>_X.png (R protect, G/B surface-space grain: the same pass
tools/klee_render/post.py reads) and <out>/<name>.json (canvas, the feet
anchor's pixel, ppu, the measured rest height).

WHAT IS COPIED, AND WHAT TO MERGE BACK. The shader half of style G
(toon_material, line_material, add_aovs, uv_noise, add_outline,
setup_render) and the posing/framing helpers are copied from
tools/klee_render/render.py as of 2026-10-13 (#1195), because that file is a
Blender script with its argparse and main() at import time and was being
edited by another workstream. The copies differ only where Klee was
hard-coded: the unlit/no-line material sets come from chars.py, the `+`
overlay shells are hidden (chars.is_overlay), the hand tip falls back to a
finger bone, and a PMX prop (Varka's claymore) is placed per pose. When the
look settles, factor the shared shader and posing into one module both
renderers import (STYLE must stay single-sourced), and let Klee's pose
library and bomb stay Klee's.
"""
import argparse
import json
import math
import os
import random
import sys

import addon_utils
import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chars as CH  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--char", required=True, choices=sorted(CH.CHARS))
ap.add_argument("--pmx", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--prop", default="", help="the character's prop PMX (chars.CHARS[...]['prop'])")
ap.add_argument("--stills", default="rest,stance")
ap.add_argument("--ppu", type=float, default=0.0, help="texture px per unit; 0 = solve from canon height")
ap.add_argument("--outline-px", type=float, default=CH.OUTLINE_PX)
ap.add_argument("--pitch", type=float, default=5.0)
ap.add_argument("--samples", type=int, default=32)
args = ap.parse_args(argv)
os.makedirs(args.out, exist_ok=True)
CFG = CH.CHARS[args.char]

MMD = "bl_ext.user_default.mmd_tools"
LINE_COLOR = (0.13, 0.07, 0.07)
LINE_TINT = (0.42, 0.33, 0.35)
#: Style G, the shader half -- a copy of tools/klee_render/render.py STYLE
#: (ruled 2026-10-13). Keep the two equal until they are merged.
STYLE = {
    "shadow": (0.66, 0.52, 0.62),
    "mid": (0.90, 0.80, 0.82),
    "mid_at": 0.22, "light_at": 0.40,
    "terminator_noise": 0.26,
    "noise_scale": 22.0, "noise_stretch": 4.0, "noise_detail": 6.0, "noise_angle": 28.0,
    "grain": 0.10,
    "grain2d_scale": 30.0, "grain2d_stretch": 4.0, "grain2d_angle": 62.0, "grain2d_mottle": 9.0,
}
FINGERS = ["人指", "中指", "薬指", "小指"]
DIGITS = "１２３"


def upd():
    bpy.context.view_layer.update()


# ----------------------------------------------------------------- scene
def import_pmx(path):
    before = set(bpy.data.objects)
    bpy.ops.mmd_tools.import_model(filepath=path, scale=CH.IMPORT_SCALE, types={"MESH", "ARMATURE", "MORPHS"})
    new = [o for o in bpy.data.objects if o not in before]
    root = next(o for o in new if o.type == "EMPTY" and o.parent is None)
    arm = next(o for o in new if o.type == "ARMATURE")
    mesh = next(o for o in new if o.type == "MESH")
    return root, arm, mesh


def base_image(mat):
    nt = mat.node_tree
    base = nt.nodes.get("mmd_base_tex")
    img = base.image if base else None
    if img is None:
        for n in nt.nodes:
            if n.type == "TEX_IMAGE" and n.image and "toon" not in n.image.name and "mc3" not in n.image.name:
                return n.image
    return img


# ----------------------------------------------------------------- style G (copied)
def uv_noise(nt, scale, stretch, detail, seed_off, angle=None, coord="UV"):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale * stretch, scale)
    mp.inputs["Location"].default_value = (seed_off, seed_off * 0.37, 0)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(STYLE["noise_angle"] if angle is None else angle))
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = 0.62
    nt.links.new(tc.outputs[coord], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    return nz


def add_aovs(nt, protect, seed, coord="UV"):
    fine = uv_noise(nt, STYLE["grain2d_scale"], STYLE["grain2d_stretch"], 2.0, seed + 23,
                    angle=STYLE["grain2d_angle"], coord=coord)
    coarse = uv_noise(nt, STYLE["grain2d_mottle"], 1.0, 2.0, seed + 41, coord=coord)
    cc = nt.nodes.new("ShaderNodeCombineColor")
    cc.inputs["Red"].default_value = 1.0 if protect else 0.0
    nt.links.new(fine.outputs["Fac"], cc.inputs["Green"])
    nt.links.new(coarse.outputs["Fac"], cc.inputs["Blue"])
    aov = nt.nodes.new("ShaderNodeOutputAOV")
    aov.aov_name = "style"
    nt.links.new(cc.outputs["Color"], aov.inputs["Color"])


def hidden_material(mat):
    """An overlay shell (chars.is_overlay): nothing drawn, nothing in the passes."""
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    nt.links.new(tr.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "DITHERED"


def toon_material(mat, img, unlit):
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    seed = random.Random(mat.name).random() * 50
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    emis = nt.nodes.new("ShaderNodeEmission")
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    gz = uv_noise(nt, STYLE["noise_scale"] * 2.2, STYLE["noise_stretch"], 2.0, seed + 11)
    gmap = nt.nodes.new("ShaderNodeMapRange")
    gmap.inputs["From Min"].default_value = 0.3
    gmap.inputs["From Max"].default_value = 0.7
    gmap.inputs["To Min"].default_value = 1 - STYLE["grain"]
    gmap.inputs["To Max"].default_value = 1 + STYLE["grain"]
    nt.links.new(gz.outputs["Fac"], gmap.inputs["Value"])
    gcol = nt.nodes.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        nt.links.new(gmap.outputs["Result"], gcol.inputs[k])
    grained = nt.nodes.new("ShaderNodeMix")
    grained.data_type = "RGBA"
    grained.blend_type = "MULTIPLY"
    grained.inputs["Factor"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], grained.inputs[6])
    nt.links.new(gcol.outputs["Color"], grained.inputs[7])
    if unlit:
        nt.links.new(tex.outputs["Color"], emis.inputs["Color"])
    else:
        diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
        s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nz = uv_noise(nt, STYLE["noise_scale"], STYLE["noise_stretch"], STYLE["noise_detail"], seed)
        wob = nt.nodes.new("ShaderNodeMath")
        wob.operation = "MULTIPLY_ADD"
        nt.links.new(nz.outputs["Fac"], wob.inputs[0])
        wob.inputs[1].default_value = 2 * STYLE["terminator_noise"]
        wob.inputs[2].default_value = -STYLE["terminator_noise"]
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        nt.links.new(bw.outputs[0], add.inputs[0])
        nt.links.new(wob.outputs[0], add.inputs[1])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        e = ramp.color_ramp.elements
        e[0].position = 0.0
        e[0].color = (*STYLE["shadow"], 1)
        e[1].position = STYLE["light_at"]
        e[1].color = (1, 1, 1, 1)
        e.new(STYLE["mid_at"]).color = (*STYLE["mid"], 1)
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        nt.links.new(diff.outputs[0], s2r.inputs[0])
        nt.links.new(s2r.outputs["Color"], bw.inputs[0])
        nt.links.new(add.outputs[0], ramp.inputs["Fac"])
        nt.links.new(grained.outputs[2], mul.inputs[6])
        nt.links.new(ramp.outputs["Color"], mul.inputs[7])
        nt.links.new(mul.outputs[2], emis.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(emis.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    add_aovs(nt, unlit, seed)
    # DITHERED everywhere: EEVEE writes no AOV from a BLENDED surface, so a
    # blended material falls out of the protect mask (Klee's 表情, 2026-10-13)
    mat.surface_render_method = "DITHERED"
    mat.use_backface_culling = False


def line_material(mat, img, protect):
    lm = bpy.data.materials.new("line_" + mat.name)
    nt = lm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emis = nt.nodes.new("ShaderNodeEmission")
    if img is None:
        emis.inputs["Color"].default_value = (*LINE_COLOR, 1)
        nt.links.new(emis.outputs[0], out.inputs["Surface"])
    else:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        mul.inputs[7].default_value = (*LINE_TINT, 1)
        nt.links.new(tex.outputs["Color"], mul.inputs[6])
        nt.links.new(mul.outputs[2], emis.inputs["Color"])
        transp = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
        nt.links.new(transp.outputs[0], mix.inputs[1])
        nt.links.new(emis.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        lm.surface_render_method = "DITHERED"
    add_aovs(nt, protect, random.Random(mat.name).random() * 50)
    lm.use_backface_culling = True
    return lm


def add_outline(obj, line_mats, no_line_mats=()):
    me = obj.data
    n = len(me.materials)
    for lm in line_mats:
        me.materials.append(lm)
    vg = obj.vertex_groups.new(name="outline_w")
    skip = {i for i, m in enumerate(me.materials[:n]) if m and m.name in no_line_mats}
    keep = set()
    for p in me.polygons:
        if p.material_index not in skip:
            keep.update(p.vertices)
    vg.add(list(keep), 1.0, "REPLACE")
    mod = obj.modifiers.new("outline", "SOLIDIFY")
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = n
    mod.vertex_group = "outline_w"
    mod.thickness_vertex_group = 0.0
    mod.use_quality_normals = True
    return mod


def shade(mesh):
    """Style G on every material of one imported mesh, plus its hull."""
    face, no_line = CFG["face_mats"], set(CFG["no_line_mats"])
    lines = []
    for m in mesh.data.materials:
        if CH.is_overlay(m.name):
            hidden_material(m)
            no_line.add(m.name)
            lines.append(line_material(m, None, False))
            continue
        img = base_image(m)
        toon_material(m, img, m.name in face)
        lines.append(line_material(m, img, m.name in face))
    return add_outline(mesh, lines, no_line)


def setup_render():
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
    vl = sc.view_layers[0]
    aov = vl.aovs.add()
    aov.name = "style"
    aov.type = "COLOR"
    ng = bpy.data.node_groups.new("aux", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    sep = ng.nodes.new("CompositorNodeSeparateColor")
    cc = ng.nodes.new("CompositorNodeCombineColor")
    ng.links.new(rl.outputs["style"], sep.inputs[0])
    for ch in ("Red", "Green", "Blue"):
        ng.links.new(sep.outputs[ch], cc.inputs[ch])
    ng.links.new(rl.outputs["Alpha"], cc.inputs["Alpha"])
    fo = ng.nodes.new("CompositorNodeOutputFile")
    fo.name = "aux_out"
    fo.format.media_type = "IMAGE"
    fo.format.file_format = "PNG"
    fo.format.color_mode = "RGBA"
    fo.format.color_depth = "8"
    fo.file_output_items.new("RGBA", "X")
    ng.links.new(cc.outputs[0], fo.inputs[0])
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = world
    sun = bpy.data.lights.new("key", "SUN")
    sun.energy = 3.2
    sun.use_shadow = False
    sun_ob = bpy.data.objects.new("key", sun)
    sc.collection.objects.link(sun_ob)
    sun_ob.rotation_euler = (math.radians(50), 0, math.radians(-40))
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam_ob = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(cam_ob)
    sc.camera = cam_ob
    return cam_ob


# ----------------------------------------------------------------- posing (copied)
def rotate_world(arm, name, axis, deg):
    upd()
    pb = arm.pose.bones[name]
    M = pb.matrix.copy()
    loc = M.translation.copy()
    R = Matrix.Rotation(math.radians(deg), 4, Vector(axis).normalized())
    pb.matrix = Matrix.Translation(loc) @ R @ Matrix.Translation(-loc) @ M
    upd()


def aim(arm, name, direction, twist=0.0):
    upd()
    pb = arm.pose.bones[name]
    cur = (pb.tail - pb.head).normalized()
    d = Vector(direction).normalized()
    q = cur.rotation_difference(d)
    M = pb.matrix.copy()
    loc = M.translation.copy()
    R = q.to_matrix().to_4x4()
    if twist:
        R = Matrix.Rotation(math.radians(twist), 4, d) @ R
    pb.matrix = Matrix.Translation(loc) @ R @ Matrix.Translation(-loc) @ M
    upd()


def move(arm, name, delta):
    upd()
    pb = arm.pose.bones[name]
    M = pb.matrix.copy()
    M.translation += Vector(delta)
    pb.matrix = M
    upd()


def w2a_dir(arm, v):
    return arm.matrix_world.to_3x3().normalized().inverted() @ Vector(v)


def hand_to(arm, side, anchor, offset_w, pole_w):
    upd()
    pbs = arm.pose.bones
    sh = pbs[f"腕.{side}"]
    a = (pbs[f"ひじ.{side}"].bone.head_local - sh.bone.head_local).length
    b = (pbs[f"手首.{side}"].bone.head_local - pbs[f"ひじ.{side}"].bone.head_local).length
    S = sh.head.copy()
    T = pbs[anchor].head + w2a_dir(arm, offset_w)
    dv = T - S
    d = min(dv.length, (a + b) * 0.995)
    u = dv.normalized()
    cos_a = max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))
    sin_a = math.sqrt(1 - cos_a * cos_a)
    P = w2a_dir(arm, pole_w)
    p = (P - P.dot(u) * u).normalized()
    E = S + a * (cos_a * u + sin_a * p)
    Tc = S + u * d
    aim(arm, f"腕.{side}", E - S)
    upd()
    aim(arm, f"ひじ.{side}", Tc - pbs[f"ひじ.{side}"].head)


def curl(arm, side, finger_deg, thumb_deg):
    sgn = 1 if side == "L" else -1
    for i, f in enumerate(FINGERS):
        spread = 1.0 + 0.12 * i
        for seg, dg in enumerate(DIGITS):
            n = f"{f}{dg}.{side}"
            if n in arm.pose.bones:
                pb = arm.pose.bones[n]
                pb.rotation_mode = "QUATERNION"
                k = (1.0, 1.1, 0.8)[seg]
                pb.rotation_quaternion = Quaternion((0, 0, 1), math.radians(finger_deg * spread * k * sgn))
    for seg, dg in enumerate("１２"):
        n = f"親指{dg}.{side}"
        if n in arm.pose.bones:
            pb = arm.pose.bones[n]
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = Quaternion((1, 0, 0), math.radians(thumb_deg))
    upd()


def reset(root, arm, mesh):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = Matrix.Identity(4)
    if mesh.data.shape_keys:
        for k in mesh.data.shape_keys.key_blocks[1:]:
            k.value = 0.0
    root.rotation_euler = (0, 0, 0)
    root.location = (0, 0, 0)
    upd()


def apply_pose(root, arm, mesh, p):
    reset(root, arm, mesh)
    root.rotation_euler = (0, 0, math.radians(p["yaw"]))
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


def hand_point(arm, side):
    """The palm centre in world space: between the wrist and the hand tip
    (手先 where the model has one, else chars' finger-bone stand-in)."""
    pbs = arm.pose.bones
    tip = f"手先.{side}" if f"手先.{side}" in pbs else f"{CFG['hand_tip']}.{side}"
    return arm.matrix_world @ ((pbs[f"手首.{side}"].head + pbs[tip].head) / 2)


def place_prop(prop_root, arm, spec):
    """Blade along local -Y (tip), flat faces along local Z. The grip point
    (local +Y spec['grip']) goes to the palm, the blade along spec['dir'],
    the flat turned toward the viewer, then rolled by spec['roll']."""
    d = Vector(spec["dir"]).normalized()
    view = Vector((0, -1, 0))
    zf = (view - view.dot(d) * d)
    zf = zf.normalized() if zf.length > 1e-6 else Vector((1, 0, 0))
    zf = Matrix.Rotation(math.radians(spec.get("roll", 0.0)), 3, d) @ zf
    yl = -d
    xl = yl.cross(zf).normalized()
    R = Matrix((xl, yl, zf)).transposed().to_4x4()
    grip_w = R @ Vector((0, spec["grip"], 0))
    prop_root.matrix_world = Matrix.Translation(hand_point(arm, spec["side"]) - grip_w.to_3d()) @ R
    upd()


# ----------------------------------------------------------------- framing (copied)
def world_box(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        if o.hide_render:
            continue
        oe = o.evaluated_get(dg)
        mw = oe.matrix_world
        pts += [mw @ Vector(c) for c in oe.bound_box]
    return pts


def project(cam_ob, pts):
    inv = cam_ob.matrix_world.inverted()
    xs, ys = [], []
    for p in pts:
        q = inv @ p
        xs.append(q.x)
        ys.append(q.y)
    return min(xs), max(xs), min(ys), max(ys)


def frame_camera(cam_ob, box, ppu, margin_px=8):
    sc = bpy.context.scene
    x0, x1, y0, y1 = box
    m = margin_px / ppu
    x0, x1, y0, y1 = x0 - m, x1 + m, y0 - m, y1 + m
    w = max(2, int(math.ceil((x1 - x0) * ppu)))
    h = max(2, int(math.ceil((y1 - y0) * ppu)))
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    cam_ob.data.ortho_scale = max(w, h) / ppu
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cam_ob.matrix_world = cam_ob.matrix_world @ Matrix.Translation((cx, cy, 0))
    upd()
    inv = cam_ob.matrix_world.inverted()
    g = inv @ Vector((0, 0, 0))
    origin = ((g.x + (w / ppu) / 2) * ppu, ((h / ppu) / 2 - g.y) * ppu)
    return w, h, origin


def render_to(path):
    sc = bpy.context.scene
    fo = sc.compositing_node_group.nodes["aux_out"]
    d, base = os.path.split(path)
    fo.directory = os.path.join(d, "aux") + os.sep
    fo.file_name = os.path.splitext(base)[0] + "_"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def reset_camera(cam_ob):
    cam_ob.matrix_world = Matrix.Identity(4)
    cam_ob.location = (0, -10, 0.8)
    cam_ob.rotation_euler = (math.radians(90 - args.pitch), 0, 0)
    upd()


# ----------------------------------------------------------------- main
def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable(MMD, default_set=True)
    root, arm, mesh = import_pmx(args.pmx)
    prop = None
    if args.prop:
        prop = import_pmx(args.prop)
    cam_ob = setup_render()

    # the rest height, measured before any shading or hull, sets the scale
    upd()
    zs = [p.z for p in world_box([mesh])]
    rest_h = max(zs) - min(zs)
    ppu = args.ppu or CH.target_ppu(args.char, rest_h)
    print(f"SCALE rest height {rest_h:.4f} u -> ppu {ppu:.2f} -> {rest_h * ppu * CH.COMBAT_SCALE:.1f} px at 1080p")

    shade(mesh).thickness = args.outline_px / ppu
    if prop:
        shade(prop[2]).thickness = args.outline_px / ppu

    poses = {"rest": CH.REST, "stance": CFG["stance"]}
    for name in [s for s in args.stills.split(",") if s]:
        p = poses[name]
        apply_pose(root, arm, mesh, p)
        objs = [mesh]
        if prop:
            on = p.get("prop") is not None
            prop[2].hide_render = not on
            if on:
                place_prop(prop[0], arm, p["prop"])
                objs.append(prop[2])
        reset_camera(cam_ob)
        box = project(cam_ob, world_box(objs))
        w, h, origin = frame_camera(cam_ob, box, ppu)
        render_to(os.path.join(args.out, "raw", f"{name}.png"))
        meta = {"still": name, "char": args.char, "canvas": [w, h],
                "origin_px": [round(origin[0], 3), round(origin[1], 3)], "ppu": round(ppu, 4),
                "rest_height_units": round(rest_h, 5), "pitch": args.pitch, "combat_scale": CH.COMBAT_SCALE}
        with open(os.path.join(args.out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
        print("STILL", name, (w, h), origin)


main()
