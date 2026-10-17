"""Klee's poses and clips, in WORLD terms, for tools/klee_render/render.py.

Pure data plus a few builders; no bpy, so it imports anywhere. +X is screen
right (toward the enemy), -Y is toward the viewer, +Z is up. The root yaw turns
her front toward screen right, so her right side (.R) is nearest the camera.

A POSE is a dict:
  yaw     root yaw in degrees (her facing; 0 = facing the camera)
  morphs  {shape key: value}
  ops     ordered bone ops, applied to a pose cleared to rest:
            ("rotw", bone, world_axis, deg)      rotate about the bone head
            ("aimw", bone, world_dir[, twist])   point head->tail along a world dir
            ("movew", bone, world_delta)
            ("move", bone, armature_delta)
            ("rot", bone, armature_axis, deg)
            ("hand", side, anchor_bone, world_offset, elbow_pole_world)
            ("curl", side, finger_deg, thumb_deg)
  held    scale of the bomb parented to her near (right) hand, 0..1
  thrown  world position of the free bomb, or None (hidden)
  thrown_spin  degrees of spin on the free bomb
  big     scale of the big Jumpy Dumpty held in BOTH hands, 0..1 (seated
          between her two hands each frame; only the jumpy clip shows it)
  big_thrown, big_spin  the big bomb in flight, as thrown / thrown_spin

A CLIP is {length, fps, loop, keys: [(t, pose, ease)]}. Every key's pose must
carry the same op list SHAPE (same kinds and bones in the same order); the
renderer resolves each key to bone matrices and interpolates those, so the
shapes only need to agree for the props and morphs. `ease` names the curve
INTO that key: "io" (smoothstep), "out", "in", "lin".

The model is the official Klee 2.0 PMX (Bilibili, model editor 神帝宇). It is
read in place from wherever the operator keeps it and NEVER enters the repo:
its terms forbid redistribution.
"""
from __future__ import annotations

import math

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
CH = "上半身2"          # hand anchor: the upper chest bone head
YAW = 14                # her facing: chest toward the viewer (milestone 1 used 30)
BAG = "+BagB CB A01"    # the backpack root; tucked so it reads behind her, not beside her
PIG_L, PIG_R = "+HairS L D01", "+HairS R D01"
PIG_L2, PIG_R2 = "+HairS L D02", "+HairS R D02"


def fwd(yaw, d):
    r = math.radians(yaw)
    return (math.sin(r) * d, -math.cos(r) * d, 0)


def stance(drop=0.055, lean=4.0, twist=-14.0, head_turn=50.0, head_nod=3.0,
           head_tilt=0.0, front=0.11, back=0.10, sway=0.0):
    """Feet planted (far foot toward the enemy), chest toward the viewer,
    head to the right. `twist` turns the upper body toward the camera."""
    return [
        ("move", "センター", (sway, 0, -drop)),
        ("movew", "足ＩＫ.L", (front, 0.015, 0)),
        ("movew", "足ＩＫ.R", (-back, -0.01, 0)),
        ("rotw", "上半身", Y, lean),
        ("rotw", "上半身", Z, twist),
        ("rotw", "首", Z, head_turn * 0.4),
        ("rotw", "頭", Z, head_turn * 0.6),
        ("rot", "頭", X, head_nod),
        ("rotw", "頭", Y, head_tilt),
        ("rotw", BAG, Z, -25),
    ]


def pigtails(swing=0.0, lift=0.0):
    """Secondary motion: both pigtails swing about the world Y axis."""
    return [
        ("rotw", PIG_L, Y, swing + lift),
        ("rotw", PIG_R, Y, swing - lift),
        ("rotw", PIG_L2, Y, swing * 0.6),
        ("rotw", PIG_R2, Y, swing * 0.6),
    ]


def arms(near, far, near_pole=(-0.6, 0.4, -0.2), far_pole=(0.2, 0.5, -1.0),
         near_curl=(50, 20), far_curl=(38, 14), near_anchor=CH):
    """near = (dx, dy, dz) of the near (right) wrist from `near_anchor` (the
    chest by default; her right hip, HIP, for an arm hanging at her side);
    far likewise for the far (left) wrist, from the chest."""
    return [
        ("hand", "R", near_anchor, near, near_pole),
        ("curl", "R", near_curl[0], near_curl[1]),
        ("hand", "L", CH, far, far_pole),
        ("curl", "L", far_curl[0], far_curl[1]),
    ]


def pose(ops, morphs=None, yaw=YAW, held=1.0, thrown=None, thrown_spin=0.0, root=(0, 0, 0),
         root_rot=0.0, big=0.0, big_thrown=None, big_spin=0.0):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "held": held,
            "thrown": thrown, "thrown_spin": thrown_spin, "root": root, "root_rot": root_rot,
            "big": big, "big_thrown": big_thrown, "big_spin": big_spin}


# --------------------------------------------------------------------- stance A
# Battle idle ([USER], 2026-10-13: "Agreed on the Silhouette change"): a wider,
# lower stance than milestone 2's, the upper body leaning toward the enemy
# (screen right), the chest still turned a little off-centre toward the viewer
# as the base cast's are; the near (right) hand holds her bomb out in front of
# her, the far hand forward beside it. The bomb is her normal-attack size, about
# 60% of her head's width ([USER], 2026-10-13: "the new attack is probably too
# big. ... It's noticeably smaller than her head. I think the increased size
# would be fitting for her Jumpty Dumpty skill usage."); the head-sized one is
# the Jumpy Dumpty clip's (JUMPY below).
# Every combat clip plants her feet where stance A does (A_FRONT / A_BACK), so
# a clip that starts or ends in idle never slides them.
#
# The near hand is placed in FRONT of her chest, the arm reaching toward the
# enemy, so it reads on its own: milestone 2 placed it across her belly from the
# chest, the upper arm hid behind the coat, and screen-left read as armless
# ([USER], 2026-10-13: "why do the idle loop ones have no right arm (Left side)?").
A_DROP = 0.12           # hips lowered (milestone 2: 0.055)
A_LEAN = 13.0           # upper body toward the enemy, degrees (milestone 2: 4)
A_FRONT = 0.17          # far foot toward the enemy (milestone 2: 0.11)
A_BACK = 0.15           # near foot back (milestone 2: 0.10)
A_HEAD_TILT = -4.0      # the head takes back part of the lean
NEAR_HOLD = (0.12, -0.065, -0.13)     # the bomb hand, from the chest
HOLD_POLE = (-0.4, 0.6, -1.0)
NEAR_HOLD_CURL = (34, 16)             # closed in around the smaller bomb (the head-sized one: 22, 12)
#: Her head's width at render, model units: the hair and face (the vertices the
#: 頭 bone carries; hat brim and pigtails left out) across the screen in
#: stance A, measured on the model in Blender, 2026-10-13. The hat brim spans
#: 0.294, the face alone 0.166.
HEAD_W = 0.217
#: The normal bomb: its diameter 60% of her head's width, as her normal
#: attack's is in the owner's reference shot from Genshin. Radius in model
#: units (PR #1210's was 0.115, milestone 2's 0.052). Where it sits on her near
#: hand in stance A, from the 手先.R bone head (render.py parents it to the
#: wrist there).
BOMB_R = round(0.6 * HEAD_W / 2, 3)   # 0.065
HELD_AT = (0.035, 0.025, 0.05)
HELD_YAW = 20.0
#: Jumpy Dumpty's bomb: about her head's size, thrown two-handed by JUMPY.
JUMPY_R = 0.115
HIP = "足.R"
NEAR_HANG = (-0.09, -0.06, 0.06)
HANG_POLE = (-1.0, 0.5, 0.0)
FAR_READY = (0.29, -0.015, 0.0)
FAR_CURL = (55, 30)
SMIRK = {"にやり": 0.6}
#: The morphs that swap her eyes for the drawn overlay (the 表情 material):
#: はぅ is the squeezed-shut "> <", なごみ and はちゅ目 its siblings. The
#: overlay slides out from behind the face skin, so at any value short of 1
#: it is half buried and her eyes read blank (the hurt sheet, 2026-10-13).
#: render.py steps these between keys instead of blending them, and a pose
#: sets them to 0 or 1 only.
STEP_MORPHS = {"はぅ", "なごみ", "はちゅ目"}


def idle_pose(breath=0.0, sway=0.0, blink=0.0, swing=0.0):
    """breath 0..1: in-breath raises the chest a hair and lifts the arms."""
    b = breath
    m = dict(SMIRK)
    if blink:
        m["ウィンク"] = blink
        m["ウィンク右"] = blink
    return pose(
        stance(drop=A_DROP + 0.006 * (1 - b), lean=A_LEAN + 1.5 * (1 - b), head_nod=3.0 + 1.5 * (1 - b),
               head_tilt=A_HEAD_TILT, front=A_FRONT, back=A_BACK, sway=0.004 * sway)
        + arms((NEAR_HOLD[0], NEAR_HOLD[1], NEAR_HOLD[2] - 0.010 * (1 - b)),
               (FAR_READY[0] - 0.006 * (1 - b), FAR_READY[1], FAR_READY[2] - 0.014 * (1 - b)),
               near_pole=HOLD_POLE, near_curl=NEAR_HOLD_CURL, far_curl=FAR_CURL)
        + pigtails(swing=swing),
        m)


IDLE = {
    "length": 2.0, "fps": 20, "loop": True,
    "keys": [
        (0.0, idle_pose(0.0, swing=-3), "io"),
        (1.0, idle_pose(1.0, swing=3), "io"),
        (1.3, idle_pose(0.85, swing=2.2), "io"),
        (1.36, idle_pose(0.8, swing=2.0, blink=1.0), "io"),
        (1.44, idle_pose(0.75, swing=1.6), "io"),
        (2.0, idle_pose(0.0, swing=-3), "io"),
    ],
}


def low_pose(breath=0.0, swing=0.0):
    b = breath
    return pose(
        stance(drop=A_DROP + 0.02 + 0.006 * (1 - b), lean=A_LEAN + 7 + 2 * (1 - b), twist=-12, head_turn=40,
               head_nod=13 + 2 * (1 - b), head_tilt=A_HEAD_TILT, front=A_FRONT, back=A_BACK)
        + arms((NEAR_HOLD[0] - 0.01, NEAR_HOLD[1], NEAR_HOLD[2] - 0.05 - 0.006 * (1 - b)),
               (FAR_READY[0] - 0.03, FAR_READY[1], FAR_READY[2] - 0.08 - 0.01 * (1 - b)),
               near_pole=HOLD_POLE, near_curl=NEAR_HOLD_CURL, far_pole=(0.4, 0.4, -1.0), far_curl=(55, 28))
        + pigtails(swing=swing),
        {"困る": 0.8, "Eye_Tired": 0.7, "あ": 0.15})


IDLE_LOW = {
    "length": 2.4, "fps": 15, "loop": True,
    "keys": [
        (0.0, low_pose(0.0, swing=-1.5), "io"),
        (1.2, low_pose(1.0, swing=1.5), "io"),
        (2.4, low_pose(0.0, swing=-1.5), "io"),
    ],
}

# --------------------------------------------------------------------- attack
# Wind-up, overarm throw toward the enemy, follow-through, and a fresh bomb
# popped back into the hand. The free bomb leaves the frame quickly: the hit
# itself is the game's VFX.


def windup(k=1.0):
    return pose(
        stance(drop=A_DROP + 0.015, lean=-6 * k + A_LEAN * (1 - k), twist=-6, head_turn=50,
               front=A_FRONT, back=A_BACK)
        + arms((-0.20, -0.06, 0.25), (0.27, -0.02, 0.10), near_pole=(-0.4, -0.6, -0.6), far_curl=(30, 12))
        + pigtails(swing=-6 * k),
        {"にやり": 0.9, "あ": 0.2})


def release(held=1.0, thrown=None):
    return pose(
        stance(drop=A_DROP + 0.025, lean=A_LEAN + 8, twist=4, head_turn=34, head_tilt=A_HEAD_TILT,
               front=A_FRONT, back=A_BACK)
        + arms((0.24, -0.08, 0.16), (-0.08, 0.06, -0.12), near_pole=(0, 0.3, -1),
               far_pole=(0.6, 0.3, -0.5), near_curl=(12, 4), far_curl=(45, 15))
        + pigtails(swing=8),
        {"にやり": 1.0, "あ": 0.6}, held=held, thrown=thrown)


def follow(held=0.0):
    return pose(
        stance(drop=A_DROP + 0.02, lean=A_LEAN + 6, twist=0, head_turn=40, head_tilt=A_HEAD_TILT,
               front=A_FRONT, back=A_BACK)
        + arms((0.20, -0.10, -0.02), (-0.04, 0.05, -0.12), near_pole=(0, 0.3, -1),
               far_pole=(0.6, 0.3, -0.5), near_curl=(30, 10), far_curl=(45, 15))
        + pigtails(swing=4),
        {"にやり": 0.8, "あ": 0.3}, held=held)


ATTACK = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.30, windup(1.0), "io"),
        (0.40, release(1.0), "in"),
        (0.45, release(0.0, thrown=(0.45, -0.06, 0.92)), "lin"),
        (0.55, follow(0.0) | {"thrown": (0.95, -0.06, 0.98)}, "out"),
        (0.60, follow(0.0), "io"),
        (0.75, follow(0.0), "io"),
        (0.88, idle_pose(0.5) | {"held": 1.0}, "out"),
        (1.0, idle_pose(0.5), "io"),
    ],
}

# --------------------------------------------------------------------- hurt


def recoil(k=1.0):
    return pose(
        [("movew", "センター", (-0.03 * k, 0, -A_DROP - 0.01 * k)),
         ("movew", "足ＩＫ.L", (A_FRONT, 0.015, 0)),
         ("movew", "足ＩＫ.R", (-A_BACK, -0.01, 0)),
         ("rotw", "上半身", Y, A_LEAN - 26 * k),
         ("rotw", "上半身", Z, -14 - 4 * k),
         ("rotw", "首", Z, 20 - 4 * k),
         ("rotw", "頭", Z, 30 - 6 * k),
         ("rot", "頭", X, 3 + 4 * k),
         ("rotw", "頭", Y, A_HEAD_TILT * (1 - k) - 10 * k),
         ("rotw", BAG, Z, -25)]
        + arms((0.06 - 0.01 * k, -0.11, -0.16 + 0.20 * k), (0.24 - 0.10 * k, -0.04, 0.02 + 0.06 * k),
               near_pole=(-0.6, 0.2, -0.6), far_pole=(0.6, 0.3, -1), near_curl=(55, 25), far_curl=(55, 25))
        + pigtails(swing=-12 * k, lift=6 * k),
        {"はぅ": 1.0, "あ": 0.4 * k, "にやり": 0.6 * (1 - k)})


HURT = {
    "length": 0.8, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.08, recoil(1.0), "out"),
        (0.30, recoil(0.85), "io"),
        (0.80, idle_pose(0.5), "io"),
    ],
}

# --------------------------------------------------------------------- death
# Recoil, knees buckle, she sits down hard with a little bounce and slumps;
# the bomb rolls out of her hand. The motion ends at 1.4 s and holds.


def death_pose(kind):
    if kind == "kneel":
        ops = [("movew", "センター", (-0.05, 0, -0.30)),
               ("movew", "足ＩＫ.L", (0.12, 0.02, 0)),
               ("movew", "足ＩＫ.R", (-0.06, -0.02, 0)),
               ("rotw", "上半身", Y, 14),
               ("rotw", "上半身", Z, -14),
               ("rotw", "首", Z, 16),
               ("rotw", "頭", Z, 20),
               ("rot", "頭", X, 18),
               ("rotw", "頭", Y, 6),
               ("rotw", BAG, Z, -25)]
        ops += arms((0.05, -0.12, -0.26), (0.12, -0.02, -0.24), near_pole=(-0.6, 0.2, -0.6),
                    far_pole=(0.6, 0.3, -1), near_curl=(30, 10), far_curl=(30, 10))
        ops += pigtails(swing=6)
        return pose(ops, {"はぅ": 1.0, "あ": 0.3}, held=0.0,
                    thrown=(0.14, -0.14, BOMB_R))
    # sat down hard on the ground, legs out in front, slumped and dizzy
    ops = [("move", "センター", (-0.02, 0, -0.45)),
           ("movew", "足ＩＫ.L", (0.20, -0.16, 0)),
           ("movew", "足ＩＫ.R", (0.04, -0.22, 0)),
           ("rotw", "上半身", Y, -10),
           ("rotw", "上半身", X, 10),
           ("rotw", "上半身", Z, -10),
           ("rotw", "首", Z, 12),
           ("rotw", "頭", Z, 16),
           ("rot", "頭", X, 22),
           ("rotw", "頭", Y, -10),
           ("rotw", BAG, Z, -25)]
    # the near hand props her up on the ground beside her hip, so the arm
    # stays visible on screen-left instead of folding behind her knees
    ops += arms((-0.11, -0.03, -0.05), (0.13, -0.06, -0.33), near_pole=(-1.0, 0.3, 0.3),
                far_pole=(0.6, 0.3, 0.2), near_curl=(25, 8), far_curl=(25, 8), near_anchor=HIP)
    ops += pigtails(swing=-5)
    return pose(ops, {"はぅ": 1.0, "あ": 0.35, "困る": 0.6}, held=0.0, thrown=(0.34, -0.16, BOMB_R),
                thrown_spin=200)


DEATH = {
    "length": 2.0, "fps": 20, "loop": False, "motion_end": 1.4,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.12, recoil(1.0), "out"),
        (0.25, recoil(1.0) | {"held": 0.0, "thrown": (0.20, -0.14, 0.45)}, "io"),
        (0.62, death_pose("kneel"), "in"),
        (0.95, death_pose("sit"), "in"),
        (1.10, death_pose("sit") | {"root": (0, 0, 0.025)}, "out"),
        (1.25, death_pose("sit"), "in"),
        (1.4, death_pose("sit"), "io"),
    ],
}

# --------------------------------------------------------------------- cast
# A little hop with the free hand raised: Klee cheering a trick on.


def cheer(k=1.0, crouch=0.0):
    return pose(
        stance(drop=A_DROP + 0.05 * crouch, lean=A_LEAN - 12 * k, twist=-16, head_turn=46, head_nod=3 - 8 * k,
               head_tilt=A_HEAD_TILT * (1 - k), front=A_FRONT, back=A_BACK)
        + arms((NEAR_HOLD[0] - 0.02 * k, NEAR_HOLD[1], NEAR_HOLD[2] + 0.03 * k),
               (0.20 - 0.04 * k, -0.06, 0.02 + 0.30 * k),
               near_pole=HOLD_POLE, near_curl=NEAR_HOLD_CURL, far_pole=(0.4, 0.4, -1), far_curl=(40 - 22 * k, 14))
        + pigtails(swing=-4 * k + 4 * crouch, lift=8 * k),
        {"にこり": 0.6 + 0.4 * k, "あ": 0.5 * k})


CAST = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.18, cheer(0.2, crouch=1.0), "io"),
        (0.38, cheer(1.0) | {"root": (0, 0, 0.06)}, "out"),
        (0.55, cheer(1.0) | {"root": (0, 0, 0.0)}, "in"),
        (0.64, cheer(0.9, crouch=0.6), "out"),
        (1.0, idle_pose(0.5), "io"),
    ],
}

# --------------------------------------------------------------------- set off
# A Set Off play ([USER], 2026-10-13: "let's pivot to animations based on the
# new model instead" of the old floating-bombs splash): a little crouch, a hop
# with both fists thrown up in a cheer -- no detonator, just "Boom!" -- eyes
# squeezed into happy arcs, the pigtails flicking up as she peaks, and a
# landing that settles back into stance A so the return to idle blends.
HAPPY_EYES = {"ウィンク": 1.0, "ウィンク右": 1.0}


def boom(k=1.0, crouch=0.0, lift=0.0, mouth=0.0):
    """k 0..1 raises both fists from the chest to above her head; crouch bends
    the knees; lift flicks the pigtails up (negative: they lag down)."""
    return pose(
        stance(drop=A_DROP + 0.06 * crouch, lean=A_LEAN - 13 * k + 6 * crouch, twist=-16 + 4 * k,
               head_turn=40 - 10 * k, head_nod=3 - 9 * k + 6 * crouch, head_tilt=A_HEAD_TILT * (1 - k),
               front=A_FRONT, back=A_BACK)
        + arms((-0.10 - 0.04 * k, -0.07 + 0.02 * k, 0.02 + 0.27 * k),
               (0.13 + 0.04 * k, -0.07 + 0.02 * k, 0.02 + 0.27 * k),
               near_pole=(-1.0, 0.2, -0.5), far_pole=(1.0, 0.2, -0.5),
               near_curl=(70, 35), far_curl=(70, 35))
        + pigtails(swing=-2 * k, lift=lift),
        {**HAPPY_EYES, "にこり": 1.0, "あ": mouth})


SETOFF = {
    "length": 0.85, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.15, boom(0.25, crouch=1.0, lift=-4, mouth=0.2), "io"),
        (0.32, boom(1.0, lift=4, mouth=0.9) | {"root": (0, 0, 0.075)}, "out"),
        (0.42, boom(1.0, lift=14, mouth=1.0) | {"root": (0, 0, 0.065)}, "io"),
        (0.55, boom(0.8, crouch=0.6, lift=6, mouth=0.6), "in"),
        (0.65, boom(0.45, crouch=0.4, lift=-3, mouth=0.3), "out"),
        (0.85, idle_pose(0.5), "io"),
    ],
}

# --------------------------------------------------------------------- stance B
# Cradling the bomb at her chest: the "cuter" stance, used where she is not in
# a fight (the merchant).


def cradle(breath=0.0, swing=0.0):
    b = breath
    return pose(
        stance(drop=0.05 + 0.005 * (1 - b), lean=3 + 1.2 * (1 - b), twist=-16, head_turn=44,
               head_nod=4 + 1.2 * (1 - b), head_tilt=-4)
        + arms((0.03, -0.15, -0.03 - 0.006 * (1 - b)), (0.14, -0.10, -0.03 - 0.006 * (1 - b)),
               near_pole=(-1, 0.1, -0.6), far_pole=(1, 0.3, -0.6), near_curl=(30, 10), far_curl=(30, 10))
        + pigtails(swing=swing),
        {"にこり": 0.75, "あ": 0.3}, held=0.0)


MERCHANT = {
    "length": 2.4, "fps": 10, "loop": True, "cradle": True,
    "keys": [
        (0.0, cradle(0.0, swing=-2), "io"),
        (1.2, cradle(1.0, swing=2), "io"),
        (2.4, cradle(0.0, swing=-2), "io"),
    ],
}

# --------------------------------------------------------------------- rest site
# Seated on the ground at the fire, knees up, hands on her knees, bomb beside her.
REST = pose(
    [("move", "センター", (0, 0, -0.34)),
     ("movew", "足ＩＫ.L", fwd(45, 0.22)),
     ("movew", "足ＩＫ.R", fwd(45, 0.20)),
     ("rotw", "上半身", Y, 8),
     ("rotw", "上半身", Z, -20),
     ("rotw", "首", Z, 8),
     ("rotw", "頭", Z, 12),
     ("rot", "頭", X, 6),
     ("rotw", BAG, Z, -25),
     ("hand", "R", "ひざ.R", (-0.01, -0.03, 0.04), (-0.5, 0, -1)),
     ("curl", "R", 35, 12),
     ("hand", "L", "ひざ.L", (0.0, -0.02, 0.04), (0.6, 0.2, -1)),
     ("curl", "L", 35, 12)],
    {"にこり": 0.8}, yaw=45, held=0.0, thrown=(-0.25, -0.12, BOMB_R))

# --------------------------------------------------------------------- character select
# A waist-up close-up of stance B: grinning, the bomb cradled at her chest,
# the face turned further toward the viewer than in combat.


def select_pose(breath=1.0, swing=0.0):
    """The close-up's pose at a point of its breath (1.0 and 0 swing: the still)."""
    p = cradle(breath, swing) | {"morphs": {"にやり": 0.9, "あ": 0.25}, "cradle": True}
    p["ops"] = [op if op[1] not in ("首", "頭") or op[0] != "rotw" or op[2] != Z
                else (op[0], op[1], op[2], op[3] * 0.55) for op in p["ops"]]
    return p


SELECT = select_pose()

#: The close-up's idle loop (select stage 2, 2026-10-15): HALF a breath, from
#: the still's pose (full breath, pigtails at rest) out to the exhale with the
#: pigtails swung. The game plays it forward then back, so every motion is a
#: cosine of the loop (eased at both ends) and the loop has no seam.
#: tools/select_loop.py renders it at the still's framing; frame 0 IS the still.
SELECT_LOOP = {
    "length": 2.0, "fps": 6, "loop": True, "cradle": True, "motion_end": 2.0,
    "keys": [
        (0.0, select_pose(1.0, 0.0), "io"),
        (2.0, select_pose(0.0, 3.0), "io"),
    ],
}
#: not in CLIPS: a half loop that does not close on its own (the game plays it
#: forward then back); only tools/select_loop.py renders it
SELECT_LOOPS = {"select_loop": SELECT_LOOP}

# --------------------------------------------------------------------- roster tile
# The character-select roster tile (132x195): a face close-up like the base
# cast's, head and shoulders, her face turned three-quarters toward the viewer
# and lifted a little, smiling with her mouth open. No bomb in frame.
PORTRAIT = pose(
    stance(head_turn=24, head_nod=-4, head_tilt=-3, twist=-18)
    + arms(NEAR_HANG, (0.20, -0.06, -0.10), near_pole=HANG_POLE, near_anchor=HIP, far_curl=FAR_CURL),
    {"にこり": 1.0, "あ": 0.35}, held=0.0)

# --------------------------------------------------------------------- jumpy dumpty
# A Jumpy Dumpty play ([USER], 2026-10-13: "the increased size would be fitting
# for her Jumpty Dumpty skill usage"): the small bomb goes away and the
# head-sized one appears between both hands; she sinks, swings it back over her
# near shoulder with both arms, then heaves it overhead toward the enemy, a
# heavier, slower toss than the attack's, and a fresh small bomb pops back into
# her hand as she settles into stance A. The free bomb is lifted out of the
# cells by pack.py and flown by the game (KleeMod.Vfx.ThrownProjectile), as the
# attack's is.
#: The big bomb's centre from the midpoint of her two fingertips (render.py).
BIG_AT = (0.0, -0.02, 0.0)


def two_hands(c, near_pole=(-0.6, 0.3, -0.6), far_pole=(0.6, 0.3, -0.6)):
    """Both wrists either side of a big bomb centred at `c` (from the chest):
    the near (right) one on its screen-left side, the far one on its right."""
    s = JUMPY_R + 0.035
    return arms((c[0] - s, c[1] - 0.01, c[2] - 0.02), (c[0] + s, c[1] + 0.02, c[2] - 0.02),
                near_pole=near_pole, far_pole=far_pole, near_curl=(40, 20), far_curl=(40, 20))


def heave(c, drop=0.0, lean=0.0, twist=-14.0, head_turn=50.0, head_nod=3.0, swing=0.0, lift=0.0,
          morphs=None, big=1.0, near_pole=(-0.6, 0.3, -0.6), far_pole=(0.6, 0.3, -0.6), **kw):
    return pose(
        stance(drop=A_DROP + drop, lean=A_LEAN + lean, twist=twist, head_turn=head_turn, head_nod=head_nod,
               head_tilt=A_HEAD_TILT, front=A_FRONT, back=A_BACK)
        + two_hands(c, near_pole=near_pole, far_pole=far_pole)
        + pigtails(swing=swing, lift=lift),
        morphs or {"にやり": 0.9, "あ": 0.2}, held=0.0, big=big, **kw)


#: Chest-relative bomb centres: gathered in front, swung back over the near
#: shoulder, and released high in front toward the enemy.
J_GATHER = (0.06, -0.12, -0.06)
J_BACK = (-0.19, 0.10, 0.12)
J_RELEASE = (0.29, -0.12, 0.03)


def jumpy_gather(k=1.0):
    return heave(J_GATHER, drop=0.02 * k, lean=-2 * k, morphs={"にやり": 1.0, "あ": 0.3}, big=k)


def jumpy_back():
    return heave(J_BACK, drop=0.05, lean=-20, twist=-4, head_turn=48, head_nod=-4, swing=-8, lift=-4,
                 morphs={"にやり": 1.0, "あ": 0.5}, near_pole=(-0.8, 0.0, -0.5), far_pole=(0.4, 0.2, -0.8))


def jumpy_release(big=1.0, big_thrown=None):
    return heave(J_RELEASE, drop=0.035, lean=14, twist=2, head_turn=36, head_nod=0, swing=10, lift=6,
                 morphs={"にやり": 1.0, "あ": 0.9}, big=big, big_thrown=big_thrown,
                 near_pole=(-0.2, 0.3, -1.0), far_pole=(0.3, 0.3, -1.0))


def jumpy_follow():
    return pose(
        stance(drop=A_DROP + 0.04, lean=A_LEAN + 12, twist=0, head_turn=38, head_tilt=A_HEAD_TILT,
               front=A_FRONT, back=A_BACK)
        + arms((0.22, -0.10, 0.02), (0.26, -0.04, -0.02), near_pole=(0, 0.3, -1),
               far_pole=(0.4, 0.3, -1.0), near_curl=(25, 10), far_curl=(25, 10))
        + pigtails(swing=6),
        {"にやり": 1.0, "あ": 0.5}, held=0.0)


JUMPY = {
    "length": 1.2, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.06, jumpy_gather(0.0), "io"),
        (0.18, jumpy_gather(1.0), "out"),
        (0.45, jumpy_back(), "io"),
        (0.55, jumpy_back(), "io"),
        (0.66, jumpy_release(1.0), "in"),
        (0.70, jumpy_release(0.0, big_thrown=(0.62, -0.10, 0.78)), "lin"),
        (0.80, jumpy_follow() | {"big_thrown": (1.02, -0.10, 0.98), "big_spin": 90}, "out"),
        (0.85, jumpy_follow(), "io"),
        (0.98, jumpy_follow(), "io"),
        (1.10, idle_pose(0.5) | {"held": 1.0}, "out"),
        (1.2, idle_pose(0.5), "io"),
    ],
}

CLIPS = {
    "idle": IDLE,
    "idle_low": IDLE_LOW,
    "attack": ATTACK,
    "hurt": HURT,
    "death": DEATH,
    "cast": CAST,
    "setoff": SETOFF,
    "jumpy": JUMPY,
    "merchant": MERCHANT,
}

# --------------------------------------------------------------------- scale reference
# Milestone 2's upright stance A, without the bomb: the still pack.py measures
# her on-screen height on, so the ruled scale (about 165 px hat to boot at
# 1080p) is checked on a standing figure and a lower battle stance never reads
# as a smaller Klee.
STAND = pose(
    stance()
    + arms(NEAR_HANG, (0.24, -0.02, 0.02), near_pole=HANG_POLE, near_anchor=HIP, far_curl=FAR_CURL),
    SMIRK, held=0.0)

STILLS = {"rest": REST, "select": SELECT, "portrait": PORTRAIT, "stance_a": IDLE["keys"][0][1],
          "stand": STAND}

