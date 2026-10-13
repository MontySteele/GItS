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
         root_rot=0.0):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "held": held,
            "thrown": thrown, "thrown_spin": thrown_spin, "root": root, "root_rot": root_rot}


# --------------------------------------------------------------------- stance A
# Battle idle: the near (right) arm hangs at her side on screen-left, elbow a
# little out, the bomb held by its cap beside her hip; the far hand is forward
# at chest height, loosely closed (milestone 1's flat palm was a curl that never
# ran: the finger bones are spelled with full-width digits).
#
# The near hand is placed from her right HIP, not the chest: placed from the
# chest (milestone 2 as first shipped) it swung across her belly, the upper arm
# hid behind the coat, and screen-left read as armless ([USER], 2026-10-13: "why
# do the idle loop ones have no right arm (Left side)?").
HIP = "足.R"
NEAR_HANG = (-0.09, -0.06, 0.06)
HANG_POLE = (-1.0, 0.5, 0.0)
FAR_READY = (0.24, -0.02, 0.02)
FAR_CURL = (55, 30)
SMIRK = {"にやり": 0.6}


def idle_pose(breath=0.0, sway=0.0, blink=0.0, swing=0.0):
    """breath 0..1: in-breath raises the chest a hair and lifts the arms."""
    b = breath
    m = dict(SMIRK)
    if blink:
        m["ウィンク"] = blink
        m["ウィンク右"] = blink
    return pose(
        stance(drop=0.055 + 0.006 * (1 - b), lean=4.0 + 1.5 * (1 - b), head_nod=3.0 + 1.5 * (1 - b),
               sway=0.004 * sway)
        + arms((NEAR_HANG[0], NEAR_HANG[1], NEAR_HANG[2] - 0.008 * (1 - b)),
               (FAR_READY[0] - 0.006 * (1 - b), FAR_READY[1], FAR_READY[2] - 0.014 * (1 - b)),
               near_pole=HANG_POLE, near_anchor=HIP, far_curl=FAR_CURL)
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
        stance(drop=0.075 + 0.006 * (1 - b), lean=11 + 2 * (1 - b), twist=-12, head_turn=40,
               head_nod=13 + 2 * (1 - b), front=0.09, back=0.09)
        + arms((-0.08, -0.05, 0.0 - 0.006 * (1 - b)), (0.15, -0.03, -0.12 - 0.01 * (1 - b)),
               near_pole=HANG_POLE, near_anchor=HIP, far_pole=(0.4, 0.4, -1.0), far_curl=(55, 28))
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
        stance(drop=0.07, lean=-6 * k + 4 * (1 - k), twist=-6, head_turn=50, front=0.13, back=0.12)
        + arms((-0.20, -0.06, 0.25), (0.27, -0.02, 0.10), near_pole=(-0.4, -0.6, -0.6), far_curl=(30, 12))
        + pigtails(swing=-6 * k),
        {"にやり": 0.9, "あ": 0.2})


def release(held=1.0, thrown=None):
    return pose(
        stance(drop=0.08, lean=12, twist=4, head_turn=34, front=0.14, back=0.12)
        + arms((0.24, -0.08, 0.16), (-0.08, 0.06, -0.12), near_pole=(0, 0.3, -1),
               far_pole=(0.6, 0.3, -0.5), near_curl=(12, 4), far_curl=(45, 15))
        + pigtails(swing=8),
        {"にやり": 1.0, "あ": 0.6}, held=held, thrown=thrown)


def follow(held=0.0):
    return pose(
        stance(drop=0.075, lean=10, twist=0, head_turn=40, front=0.14, back=0.12)
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
        [("movew", "センター", (-0.03 * k, 0, -0.055 - 0.01 * k)),
         ("movew", "足ＩＫ.L", (0.08, 0.015, 0)),
         ("movew", "足ＩＫ.R", (-0.10, -0.01, 0)),
         ("rotw", "上半身", Y, 4 - 22 * k),
         ("rotw", "上半身", Z, -14 - 4 * k),
         ("rotw", "首", Z, 20 - 4 * k),
         ("rotw", "頭", Z, 30 - 6 * k),
         ("rot", "頭", X, 3 + 4 * k),
         ("rotw", "頭", Y, -10 * k),
         ("rotw", BAG, Z, -25)]
        + arms((0.06 - 0.01 * k, -0.11, -0.16 + 0.20 * k), (0.24 - 0.10 * k, -0.04, 0.02 + 0.06 * k),
               near_pole=(-0.6, 0.2, -0.6), far_pole=(0.6, 0.3, -1), near_curl=(55, 25), far_curl=(55, 25))
        + pigtails(swing=-12 * k, lift=6 * k),
        {"はぅ": 1.0 * k, "あ": 0.4 * k, "にやり": 0.6 * (1 - k)})


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
                    thrown=(0.10, -0.12, 0.06))
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
    return pose(ops, {"はぅ": 1.0, "あ": 0.35, "困る": 0.6}, held=0.0, thrown=(0.30, -0.14, 0.05),
                thrown_spin=200)


DEATH = {
    "length": 2.0, "fps": 20, "loop": False, "motion_end": 1.4,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.12, recoil(1.0), "out"),
        (0.25, recoil(1.0) | {"held": 0.0, "thrown": (0.06, -0.12, 0.45)}, "io"),
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
        stance(drop=0.055 + 0.05 * crouch, lean=4 - 8 * k, twist=-16, head_turn=46, head_nod=3 - 8 * k,
               front=0.10, back=0.09)
        + arms((NEAR_HANG[0] - 0.01 * k, NEAR_HANG[1], NEAR_HANG[2] + 0.05 * k),
               (0.20 - 0.04 * k, -0.06, 0.02 + 0.30 * k),
               near_pole=HANG_POLE, near_anchor=HIP, far_pole=(0.4, 0.4, -1), far_curl=(40 - 22 * k, 14))
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
    {"にこり": 0.8}, yaw=45, held=0.0, thrown=(-0.17, -0.12, 0.05))

# --------------------------------------------------------------------- character select
# A waist-up close-up of stance B: grinning, the bomb cradled at her chest,
# the face turned further toward the viewer than in combat.
SELECT = cradle(1.0) | {"morphs": {"にやり": 0.9, "あ": 0.25}, "cradle": True}
SELECT["ops"] = [op if op[1] not in ("首", "頭") or op[0] != "rotw" or op[2] != Z
                 else (op[0], op[1], op[2], op[3] * 0.55) for op in SELECT["ops"]]

CLIPS = {
    "idle": IDLE,
    "idle_low": IDLE_LOW,
    "attack": ATTACK,
    "hurt": HURT,
    "death": DEATH,
    "cast": CAST,
    "merchant": MERCHANT,
}

STILLS = {"rest": REST, "select": SELECT, "stance_a": IDLE["keys"][0][1]}

