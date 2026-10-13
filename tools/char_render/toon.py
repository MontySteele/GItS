"""The shared Blender half of the model renders: style H1's shader, the
outline hull, the `style` pass, posing, framing. Imported by
tools/klee_render/render.py and tools/char_render/render.py (Blender
scripts); needs bpy, so nothing outside Blender imports it.

Moved out of tools/klee_render/render.py on 2026-10-13 so every kit renders
with one STYLE (review/active/varka-visual-paper-2026-10-13.md). The node
graphs are built in the same order as before, so Klee's frames are unchanged;
what was hard-coded to Klee (her unlit material set, the camera height, the
sample count) is a parameter here.
"""
import math
import os
import random

import bpy
from mathutils import Matrix, Quaternion, Vector

MMD = "bl_ext.user_default.mmd_tools"
LINE_COLOR = (0.13, 0.07, 0.07)        # a hull with no texture to tint (and Klee's bomb lines)
LINE_TINT = (0.42, 0.33, 0.35)         # body lines: the fill's own texture times this
SHADOW_TINT = (0.80, 0.64, 0.68)       # a flat prop's two-tone (Klee's bomb)
#: Style H1 + H3 lite, the shader half (H1; ruled 2026-10-13, review/active/klee-visual-paper-2026-10-12.md):
#: style G's ramp with a deeper shadow band, its steps moved up, and the lit
#: tone capped below white. tools/klee_render/post.py holds the 2D half (G's chain plus H3 lite).
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
FINGERS = ["人指", "中指", "薬指", "小指"]
DIGITS = "１２３"          # the MMD models spell their finger segments with full-width digits


def upd():
    bpy.context.view_layer.update()


# ----------------------------------------------------------------- shading
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
    """Noise in the surface's own space (so it rides the figure), stretched
    along one axis and rotated: a brush direction."""
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
    compositor). R is `protect`: the face (and Klee's bomb), kept out of the
    line fade and the Kuwahara. G and B are the brush grain as noise in the
    surface's own space, so it moves with the figure and never crawls: fine
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


def toon_material(mat, img, unlit):
    """Style H1's shader: a three-step constant ramp (deep, half, light)
    whose terminators are wobbled by stretched UV-space noise, times
    UV-space value grain. `unlit` (the face materials) skips the ramp and is
    protected in the `style` pass."""
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
    add_aovs(nt, unlit, seed)
    # DITHERED for every material, Klee's expression overlay (表情: the drawn
    # > < eyes of はぅ) included: EEVEE writes no AOV from a BLENDED surface,
    # so the overlay fell out of the protect mask and post.py faded its lines
    mat.surface_render_method = "DITHERED"
    mat.use_backface_culling = False


def line_material(mat, img, protect):
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
    # a face material's hull is protected too: where Klee's eyes squeeze shut
    # (はぅ) the face's own hull shows through the closed socket, and left
    # unprotected it punched a hole in the mask right under the "> <"
    add_aovs(nt, protect, random.Random(mat.name).random() * 50)
    lm.use_backface_culling = True
    return lm


def hidden_material(mat):
    """An overlay shell (chars.is_overlay) or a glow card: nothing drawn,
    nothing in the passes."""
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    nt.links.new(tr.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "DITHERED"


def flat_material(name, color, line=False, unlit=False):
    """A two-tone material for a prop modelled from primitives (Klee's bomb)."""
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
    # a prop is protected (Klee's bomb face stays crisp); its grain is in object space
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


def setup_render(samples):
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
        sc.eevee.taa_render_samples = samples
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


def wrist_to(arm, side, T, pole_w):
    """Two-bone IK in armature space: the wrist to T, the elbow bending
    toward pole_w (a world direction)."""
    upd()
    pbs = arm.pose.bones
    sh = pbs[f"腕.{side}"]
    a = (pbs[f"ひじ.{side}"].bone.head_local - sh.bone.head_local).length
    b = (pbs[f"手首.{side}"].bone.head_local - pbs[f"ひじ.{side}"].bone.head_local).length
    S = sh.head.copy()
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


def hand_to(arm, side, anchor, offset_w, pole_w):
    """Two-bone IK: the wrist to anchor-bone head + world offset, the elbow
    bending toward pole_w."""
    upd()
    wrist_to(arm, side, arm.pose.bones[anchor].head + w2a_dir(arm, offset_w), pole_w)


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
    if mesh.data.shape_keys:
        for k in mesh.data.shape_keys.key_blocks[1:]:
            k.value = 0.0
    root.rotation_euler = (0, 0, 0)
    root.location = (0, 0, 0)
    upd()


def run_op(arm, op):
    """One bone op of the pose language (tools/klee_render/clips.py)."""
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


EASE = {
    "io": lambda u: u * u * (3 - 2 * u),
    "out": lambda u: 1 - (1 - u) ** 2,
    "in": lambda u: u * u,
    "lin": lambda u: u,
}


def at_time(keys, t):
    """(k0, k1, eased u, raw u) bracketing t."""
    for i in range(len(keys) - 1):
        t0, t1 = keys[i][0], keys[i + 1][0]
        if t0 <= t <= t1 + 1e-9:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return i, i + 1, EASE[keys[i + 1][2]](max(0.0, min(1.0, u))), u
    return len(keys) - 1, len(keys) - 1, 0.0, 0.0


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


def to_px(cam_ob, ppu, v):
    """A world point's pixel on the framed canvas (x right, y down)."""
    sc = bpy.context.scene
    w, h = sc.render.resolution_x, sc.render.resolution_y
    q = cam_ob.matrix_world.inverted() @ Vector(v)
    return [round((q.x + (w / ppu) / 2) * ppu, 3), round(((h / ppu) / 2 - q.y) * ppu, 3)]


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


def reset_camera(cam_ob, pitch, height=0.55):
    cam_ob.matrix_world = Matrix.Identity(4)
    cam_ob.location = (0, -10, height)
    cam_ob.rotation_euler = (math.radians(90 - pitch), 0, 0)
    upd()
