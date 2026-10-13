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
import random
import sys

import addon_utils
import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clips as C  # noqa: E402

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

MMD = "bl_ext.user_default.mmd_tools"
SHADOW_TINT = (0.80, 0.64, 0.68)       # the bomb's flat two-tone
LINE_COLOR = (0.13, 0.07, 0.07)        # the bomb's lines, and a body material with no texture
LINE_TINT = (0.42, 0.33, 0.35)         # body lines: the fill's own texture times this
#: Style H1 + H3 lite, the shader half (H1; ruled 2026-10-13, review/active/klee-visual-paper-2026-10-12.md):
#: style G's ramp with a deeper shadow band, its steps moved up, and the lit
#: tone capped below white. post.py holds the 2D half (G's chain plus H3 lite).
STYLE = {
    "shadow": (0.52, 0.37, 0.40),      # deep tone: warm purple-brown (G: 0.66, 0.52, 0.62)
    "mid": (0.84, 0.71, 0.70),         # half tone (G: 0.90, 0.80, 0.82)
    "light": (0.94, 0.92, 0.91),       # lit tone: highlights capped below white (G: 1, 1, 1)
    "mid_at": 0.30, "light_at": 0.52,  # the ramp's steps (G: 0.22 / 0.40)
    "terminator_noise": 0.26,          # +- wobble of the light/shadow boundaries
    "noise_scale": 22.0, "noise_stretch": 4.0, "noise_detail": 6.0, "noise_angle": 28.0,
    "grain": 0.10,                     # +- value grain multiplied into the fill
    # the `grain` AOV post.py grains with: fine stretched strokes, plus a coarse mottle
    "grain2d_scale": 30.0, "grain2d_stretch": 4.0, "grain2d_angle": 62.0, "grain2d_mottle": 9.0,
}
UNLIT_MATS = {"脸", "眼白", "眼睛", "表情"}
NO_LINE_MATS = {"眼白", "眼睛", "表情"}
FINGERS = ["人指", "中指", "薬指", "小指"]
DIGITS = "１２３"          # the model spells its finger segments with full-width digits


def upd():
    bpy.context.view_layer.update()


# ----------------------------------------------------------------- scene
def load_model():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable(MMD, default_set=True)
    bpy.ops.mmd_tools.import_model(filepath=args.pmx, scale=0.08, types={"MESH", "ARMATURE", "MORPHS"})
    root = next(o for o in bpy.data.objects if o.type == "EMPTY" and o.parent is None)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    mesh = next(o for o in bpy.data.objects if o.type == "MESH")
    return root, arm, mesh


def base_image(mat):
    """The material's own colour texture (mmd_tools' base slot, else the
    first image that is not a toon or sphere map)."""
    nt = mat.node_tree
    base = nt.nodes.get("mmd_base_tex")
    img = base.image if base else None
    if img is None:
        for n in nt.nodes:
            if n.type == "TEX_IMAGE" and n.image and "toon" not in n.image.name and "mc3" not in n.image.name:
                return n.image
    return img


def uv_noise(nt, scale, stretch, detail, seed_off, angle=None, coord="UV"):
    """Noise in the surface's own space (so it rides her), stretched along
    one axis and rotated: a brush direction."""
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
    """The one pass post.py reads, `style` (written beside each frame by the
    compositor). R is `protect`: the face and the bomb, kept out of the line
    fade and the Kuwahara. G and B are the brush grain as noise in the
    surface's own space, so it moves with her and never crawls: fine
    stretched strokes in G, a coarse mottle in B. One colour AOV, because a
    VALUE AOV beside a COLOR one comes out black (Blender 5.2, measured)."""
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


def toon_material(mat, img):
    """Style G's shader: a three-step constant ramp (deep, half, light)
    whose terminators are wobbled by stretched UV-space noise, times
    UV-space value grain. The face materials stay unlit."""
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
    # value grain multiplied into the fill
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
    if mat.name in UNLIT_MATS:
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
        e[1].color = (*STYLE["light"], 1)
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
    add_aovs(nt, mat.name in UNLIT_MATS, seed)
    # DITHERED for every material, the expression overlay (表情: the drawn
    # > < eyes of はぅ) included: EEVEE writes no AOV from a BLENDED surface,
    # so the overlay fell out of the protect mask and post.py faded its lines
    mat.surface_render_method = "DITHERED"
    mat.use_backface_culling = False


def line_material(mat, img):
    """The outline hull for one body material: that material's own texture
    times LINE_TINT, so each line is a darker shade of the fill it rims
    rather than one flat brown."""
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
    # a face material's hull is protected too: where her eyes squeeze shut
    # (はぅ) the face's own hull shows through the closed socket, and left
    # unprotected it punched a hole in the mask right under the "> <"
    add_aovs(nt, mat.name in UNLIT_MATS, random.Random(mat.name).random() * 50)
    lm.use_backface_culling = True
    return lm


def flat_material(name, color, line=False, unlit=False):
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emis = nt.nodes.new("ShaderNodeEmission")
    if line or unlit:
        emis.inputs["Color"].default_value = (*color, 1)
        mat.use_backface_culling = bool(line)
    else:
        diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
        s2r = nt.nodes.new("ShaderNodeShaderToRGB")
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        ramp.color_ramp.elements[0].color = tuple(c * s for c, s in zip(color, SHADOW_TINT)) + (1,)
        ramp.color_ramp.elements[1].position = 0.32
        ramp.color_ramp.elements[1].color = (*color, 1)
        nt.links.new(diff.outputs[0], s2r.inputs[0])
        nt.links.new(s2r.outputs["Color"], bw.inputs[0])
        nt.links.new(bw.outputs[0], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], emis.inputs["Color"])
    nt.links.new(emis.outputs[0], out.inputs["Surface"])
    # the bomb is protected (its face stays crisp); its grain is in object space
    add_aovs(nt, not line, random.Random(name).random() * 50, coord="Object")
    return mat


def add_outline(obj, line_mats, no_line_mats=()):
    """An inverted-hull outline: a Solidify shell whose faces take the line
    material of the body material they came from (material_offset)."""
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


def outline_prop(obj, line_mat):
    obj.data.materials.append(line_mat)
    mod = obj.modifiers.new("outline", "SOLIDIFY")
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = len(obj.data.materials) - 1
    return mod


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
    # the compositor writes the pass as a PNG beside each frame:
    # R = protect, G = fine grain, B = coarse grain, A = the frame's alpha
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
    """Two-bone IK: the wrist to anchor-bone head + world offset, the elbow
    bending toward pole_w."""
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
    """Curl the four fingers toward the palm (local Z), the thumb across (local X)."""
    sgn = 1 if side == "L" else -1
    for i, f in enumerate(FINGERS):
        spread = 1.0 + 0.12 * i        # the little finger curls a touch more
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


EASE = {
    "io": lambda u: u * u * (3 - 2 * u),
    "out": lambda u: 1 - (1 - u) ** 2,
    "in": lambda u: u * u,
    "lin": lambda u: u,
}


def at_time(keys, t):
    """(k0, k1, eased u) bracketing t."""
    for i in range(len(keys) - 1):
        t0, t1 = keys[i][0], keys[i + 1][0]
        if t0 <= t <= t1 + 1e-9:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return i, i + 1, EASE[keys[i + 1][2]](max(0.0, min(1.0, u))), u
    return len(keys) - 1, len(keys) - 1, 0.0, 0.0


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
    return w, h, origin, (cx, cy)


def render_to(path):
    """Render the frame to `path`, and its passes to `aux/<stem>_X.png`
    beside it (post.py's input)."""
    sc = bpy.context.scene
    fo = sc.compositing_node_group.nodes["aux_out"]
    d, base = os.path.split(path)
    fo.directory = os.path.join(d, "aux") + os.sep
    fo.file_name = os.path.splitext(base)[0] + "_"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def reset_camera(cam_ob):
    cam_ob.matrix_world = Matrix.Identity(4)
    cam_ob.location = (0, -10, 0.55)
    cam_ob.rotation_euler = (math.radians(90 - args.pitch), 0, 0)
    upd()


# ----------------------------------------------------------------- main
def main():
    root, arm, mesh = load_model()
    cam_ob = setup_render()
    body_lines = []
    for m in mesh.data.materials:
        img = base_image(m)
        toon_material(m, img)
        body_lines.append(line_material(m, img))
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
        spec = C.CLIPS[name]
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
