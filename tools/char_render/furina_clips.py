"""Furina's poses and clips, in WORLD terms, for tools/char_render/render.py.

Pure data plus a few builders; no bpy, so it imports anywhere. The pose
language is tools/klee_render/clips.py's (+X screen right, toward the enemy;
-Y toward the viewer; +Z up; the root yaw turns her front toward screen right,
so her right side, .R, is nearest the camera and her left arm, .L, is the far
arm, the one toward the enemy).

The look is Klee's and Varka's (review/active/klee-visual-paper-2026-10-12.md):
style H1 + H3 lite, on the left of the field facing right, a little tilted.
Her official pack carries no sword (scratch models/furina/unpacked: the
Salon trio, cakes, a statue and a scene, no weapon), so she fights as the
performer she is: the far arm swept toward the enemy palm-open, the near hand
at her hip. Her attack is her rapier's thrust done with an empty hand, and
the blade is a PHANTOM: render.py records a line from her far hand along
her forearm (`PHANTOM`) as if it were a blade, and fx.py draws the slash
trail and the impact flash from it -- the golden line of her in-game thrust
(scratch furina-art/reference/NOTES.md: Character Details 3, f24 and f48).

A CLIP is {length, fps, loop, keys: [(t, pose, ease)], events, trails, bursts}
as in varka_clips.py. Every combat clip starts and ends in stance A, so blends
in and out of idle never slide her feet.

THE SCALE: the model stands 1.72 units with her hat (import 0.08); the chest
bone (上半身2) is 1.10 up, the shoulders 1.22, an arm reaches 0.40 from the
shoulder. Her ruled height is 63 in (chars.py).

The model is the official Furina pack (观海, miHoYo); it is read in place from
the operator's scratch directory and NEVER enters the repo.
"""
from __future__ import annotations

import math

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
CH = "上半身2"
YAW = 18
#: the coat's long back tails (HB2..HB4 chains hang from the hips): swung for
#: secondary motion
TAILS = ["HB2_0_1", "HB3_0_1", "HB4_0_1"]
#: the phantom rapier: a line from the far hand's knuckles along the hand,
#: this long (units; about half her height, a rapier's blade)
PHANTOM = {"L": 0.72}

# ------------------------------------------------------------------ stance A
A_DROP, A_LEAN, A_TWIST = 0.035, -2.0, -18.0
A_FRONT, A_BACK = 0.10, 0.10
SMUG = {"にやり": 0.7, "口角上げ": 0.3}
#: the far hand held low and loose at her waist, forward of her, palm turned
#: up in an open "presenting" gesture ([USER], 2026-10-13: the old far arm,
#: straight out at shoulder height palm down, read as a salute; no arm above
#: the shoulder, none straight out palm down, in any frame of idle)
FAR = (0.24, -0.20, -0.08)
IDLE_FAR_POLE = (0.2, 0.6, -1.0)
#: the wrist turned palm up (aimw: the hand along this world direction,
#: rolled -90 degrees about it)
FAR_AIM = ((0.8, -0.2, 0.0), -90.0)
#: the attack's own elbow pole (the thrust, kept as ruled)
FAR_POLE = (0.0, 0.4, -1.0)
#: the near hand on her hip, akimbo: the elbow out behind her, the hand
#: turned in on her waist
NEAR = (-0.13, -0.06, -0.15)
NEAR_POLE = (-1.0, 0.3, 0.0)
NEAR_AIM = ((0.6, 0.0, -1.0), 0.0)


def add(v, dv):
    return tuple(a + b for a, b in zip(v, dv))


def rot_z(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1], v[2])


def stance(drop=A_DROP, lean=A_LEAN, twist=A_TWIST, head_turn=38.0, head_nod=-3.0, head_tilt=-4.0,
           front=A_FRONT, back=A_BACK, back_lift=0.035, front_lift=0.0, sway=0.0):
    """Feet planted (far foot toward the enemy), the rear heel up, chest
    toward the viewer, head to the right and a little tilted."""
    return [
        ("move", "センター", (sway, 0, -drop)),
        ("movew", "足ＩＫ.L", (front, 0.02, front_lift)),
        ("movew", "足ＩＫ.R", (-back, -0.02, back_lift)),
        ("rotw", "上半身", Y, lean),
        ("rotw", "上半身", Z, twist),
        ("rotw", "首", Z, head_turn * 0.4),
        ("rotw", "頭", Z, head_turn * 0.6),
        ("rot", "頭", X, head_nod),
        ("rotw", "頭", Y, head_tilt),
    ]


def hands(far=FAR, near=NEAR, far_pole=FAR_POLE, near_pole=NEAR_POLE, far_curl=(8, 0), near_curl=(30, 10),
          far_anchor=CH, near_anchor=CH, far_aim=None, near_aim=None):
    """Both hands by IK; `*_aim` (world direction, roll) then turns that
    wrist, e.g. palm up."""
    ops = [("hand", "R", near_anchor, near, near_pole), ("curl", "R", near_curl[0], near_curl[1])]
    if near_aim:
        ops.append(("aimw", "手首.R", near_aim[0], near_aim[1]))
    ops += [("hand", "L", far_anchor, far, far_pole), ("curl", "L", far_curl[0], far_curl[1])]
    if far_aim:
        ops.append(("aimw", "手首.L", far_aim[0], far_aim[1]))
    return ops


def cloth(swing=0.0):
    """The coat tails swing about the world Y axis (sideways on screen)."""
    return [("rotw", b, Y, swing * (1.0 + 0.2 * i)) for i, b in enumerate(TAILS)]


def pose(ops, morphs=None, yaw=YAW, root=(0, 0, 0)):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "root": tuple(root), "root_rot": 0.0}


def turned(p, deg):
    """Pose p turned rigidly `deg` degrees about the vertical through her
    feet (a pirouette): the root's yaw and every WORLD vector of the pose
    turn with it; bone-local ops ride along with the root."""
    q = dict(p)
    q["yaw"] = p["yaw"] + deg
    if deg % 360 == 0:
        return q
    ops = []
    for op in p["ops"]:
        k = op[0]
        if k in ("rotw", "aimw", "movew"):
            op = (k, op[1], rot_z(op[2], deg)) + tuple(op[3:])
        elif k == "hand":
            op = (k, op[1], op[2], rot_z(op[3], deg), rot_z(op[4], deg))
        ops.append(op)
    q["ops"] = ops
    q["root"] = rot_z(p["root"], deg)
    return q


def idle_pose(breath=0.0, swing=0.0, blink=0.0):
    """Stance A, a diva at ease: the near hand on her hip, the far hand low and
    open, palm up. breath 0..1: the in-breath lifts the chest and the open
    hand a hair, and her weight drifts onto the front foot (the hips sway)."""
    b = breath
    m = dict(SMUG)
    if blink:
        m["まばたき"] = blink
    return pose(stance(drop=A_DROP + 0.008 * (1 - b), lean=A_LEAN - 1.0 * b, head_nod=-3 - 1.5 * b,
                       head_tilt=-4 - 1.5 * b, sway=0.008 * b)
                + hands(far=add(FAR, (0.006 * b, 0.0, 0.014 * b)), near=add(NEAR, (0, 0, 0.006 * b)),
                        far_pole=IDLE_FAR_POLE, far_curl=(14 - 4 * b, 0), far_aim=FAR_AIM, near_aim=NEAR_AIM)
                + cloth(swing), m)


IDLE = {
    "length": 2.8, "fps": 12, "loop": True,
    "keys": [
        (0.0, idle_pose(0.0, swing=-1.5), "io"),
        (1.4, idle_pose(1.0, swing=1.5), "io"),
        (1.75, idle_pose(0.8, swing=1.2), "io"),
        (1.82, idle_pose(0.77, swing=1.1, blink=1.0), "io"),
        (1.9, idle_pose(0.74, swing=1.0), "io"),
        (2.8, idle_pose(0.0, swing=-1.5), "io"),
    ],
}

# ------------------------------------------------------------------ low HP
# The performance flags: shoulders and head low, the far hand fallen to her
# chest, the near one hanging, a sad brow.


def low_pose(breath=0.0, swing=0.0):
    b = breath
    return pose(stance(drop=A_DROP + 0.03 + 0.006 * (1 - b), lean=A_LEAN + 9 + 1.5 * (1 - b), head_turn=30,
                       head_nod=14 + 2 * (1 - b), back_lift=0.01)
                + hands(far=(0.14, -0.16, 0.00 + 0.01 * b), near=(-0.10, -0.04, -0.34),
                        far_pole=(0.6, 0.2, -1.0), far_curl=(35, 15), near_curl=(20, 5))
                + cloth(swing),
                {"悲しむ": 0.7, "困る": 0.4})


IDLE_LOW = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, low_pose(0.0, swing=-1.0), "io"),
        (1.5, low_pose(1.0, swing=1.0), "io"),
        (3.0, low_pose(0.0, swing=-1.0), "io"),
    ],
}

# ------------------------------------------------------------------ attack
# Her rapier's thrust with an empty hand (reference NOTES.md, Character
# Details 3 f24/f48: the sword arm locked out level at the target, side-on,
# the rear foot lifted, a long golden line along the blade). The far hand
# draws back to her shoulder, flicks a small circle -- the flourish -- and
# drives straight out at the enemy as she lunges onto the front foot, the near
# arm flung back and up for balance. The phantom blade (PHANTOM) sweeps the
# flourish and the thrust; the hit lands at full extension.


def atk(far, near, far_pole=FAR_POLE, near_pole=(0.0, 0.4, -1.0), drop=A_DROP, lean=A_LEAN, twist=A_TWIST,
        front=A_FRONT, back=A_BACK, back_lift=0.035, head_turn=38.0, head_nod=-3.0, swing=0.0, morphs=None,
        yaw=YAW, far_aim=None):
    return pose(stance(drop=drop, lean=lean, twist=twist, front=front, back=back, back_lift=back_lift,
                       head_turn=head_turn, head_nod=head_nod)
                + hands(far=far, near=near, far_pole=far_pole, near_pole=near_pole, far_curl=(4, 0),
                        near_curl=(12, 4), far_aim=far_aim)
                + cloth(swing),
                morphs or {"にやり": 0.5, "怒り目": 0.3}, yaw=yaw)


#: the lunge: front foot out, knees bent, the far arm locked level at the enemy
LUNGE = dict(drop=0.11, lean=8.0, twist=-4.0, front=0.24, back=0.18, back_lift=0.06, head_turn=46, head_nod=0,
             yaw=34)
THRUST = (0.60, -0.02, 0.12)
BALANCE = (-0.36, 0.06, 0.30)

ATTACK = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        # draw back: the far hand to her shoulder, wrist cocked, weight back
        (0.16, atk((0.10, -0.16, 0.22), (-0.16, -0.02, -0.18), far_pole=(0.3, 0.3, -1.0), drop=0.06, lean=-6,
                   twist=-22, back_lift=0.0, swing=-2, yaw=24), "out"),
        # the flourish: a small circle up and over
        (0.24, atk((0.20, -0.20, 0.32), (-0.20, 0.0, -0.10), far_pole=(0.3, 0.3, -1.0), drop=0.06, lean=-4,
                   twist=-20, back_lift=0.0, swing=-1, yaw=26), "io"),
        (0.30, atk((0.26, -0.14, 0.18), (-0.24, 0.02, 0.0), far_pole=(0.2, 0.4, -1.0), drop=0.07, lean=-2,
                   twist=-16, back_lift=0.0, yaw=28), "io"),
        # the thrust: out at the enemy as she lunges (impact, frame 8)
        (0.40, atk(THRUST, BALANCE, far_pole=(0.0, 0.5, -1.0), swing=4, **LUNGE), "in"),
        (0.52, atk(add(THRUST, (0.0, 0.0, 0.01)), add(BALANCE, (0, 0, 0.03)), far_pole=(0.0, 0.5, -1.0),
                   swing=2, **{**LUNGE, "drop": 0.12}), "out"),
        # recover: the arm sweeps down and in, the palm turning up, back to
        # the stance's low open hand (never held out at shoulder height)
        (0.70, atk((0.32, -0.16, -0.02), (-0.16, 0.0, -0.20), far_pole=IDLE_FAR_POLE, drop=0.05, lean=0, twist=-16,
                   back_lift=0.02, swing=-1, yaw=22, far_aim=FAR_AIM), "io"),
        (0.88, idle_pose(0.5), "out"),
        (1.0, idle_pose(0.5), "io"),
    ],
    "events": {"impact": [0.40], "main": 0.40},
    # the flourish leaves a ribbon from near her hand out to the point; the
    # thrust (which sweeps no area: it runs along the blade) is a streak
    "trails": [{"blade": "L", "from": 0.14, "to": 0.40, "age": 0.16, "inner": 0.15, "taper": 0.6}],
    "bursts": [{"t": 0.40, "blade": "L", "kind": "thrust", "scale": 1.0}],
}

# ------------------------------------------------------------------ cast
# Salon Solitaire's call: she rises onto her toes, the far hand lifted high,
# palm up, calling her company up; the near hand to her heart.


def call(k=1.0):
    return pose(stance(drop=A_DROP - 0.02 * k, lean=A_LEAN - 4 * k, twist=A_TWIST - 4 * k, head_nod=-3 - 10 * k,
                       back_lift=0.035 + 0.04 * k, front_lift=0.0)
                + hands(far=(0.24 - 0.04 * k, -0.10, 0.30 + 0.24 * k), near=(-0.02, -0.15, 0.03 * k),
                        far_pole=(0.2, 0.4, -1.0), near_pole=(-0.8, 0.0, -0.6), far_curl=(10, 0),
                        near_curl=(25, 10))
                + cloth(-1.5 * k),
                {"笑い": 0.6 * k, "にこり": 0.5, "あ": 0.3 * k})


CAST = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.16, call(0.7), "out"),
        (0.28, call(1.0), "out"),
        (0.70, call(1.0), "io"),
        (1.0, idle_pose(0.5), "io"),
    ],
}

# ------------------------------------------------------------------ hurt


def flinch(k=1.0):
    return pose(stance(drop=A_DROP + 0.03 * k, lean=A_LEAN - 14 * k, twist=A_TWIST - 6 * k, head_turn=38 - 10 * k,
                       head_nod=-3 - 8 * k, head_tilt=-4 - 8 * k, back_lift=0.035 * (1 - k))
                + hands(far=(0.16 - 0.04 * k, -0.18, 0.10), near=(-0.04, -0.16, 0.04),
                        far_pole=(0.6, 0.2, -1.0), near_pole=(-0.8, 0.1, -0.6), far_curl=(40, 15),
                        near_curl=(40, 15))
                + cloth(-5 * k),
                {"まばたき": 0.8 * k, "困る": 0.7, "あ": 0.4 * k})


HURT = {
    "length": 0.8, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.08, flinch(1.0), "out"),
        (0.30, flinch(0.85), "io"),
        (0.80, idle_pose(0.5), "io"),
    ],
}

# ------------------------------------------------------------------ death
# A swoon, played to the house: the back of the far hand to her brow, a sway
# back, then she sinks to her knees and folds, head bowed. Holds from 1.6 s.


def swoon(k=1.0):
    return pose(stance(drop=A_DROP + 0.04 * k, lean=A_LEAN - 10 * k, head_nod=-14 * k, head_tilt=-4 - 6 * k,
                       back_lift=0.0)
                + hands(far=(0.10, -0.12, 0.12), near=(-0.20, -0.02, -0.16), far_anchor="頭",
                        far_pole=(0.6, 0.2, -1.0), far_curl=(20, 5), near_curl=(15, 5))
                + cloth(-3 * k),
                {"悲しむ": 0.8, "まばたき": 0.9 * k})


def kneel(k=1.0, slump=0.0, swing=0.0):
    """Down on both knees, shins back, sitting toward her heels; `slump` folds
    her forward over her knees."""
    return pose([
        ("move", "センター", (0, 0, -0.50 * k - 0.08 * slump)),
        ("movew", "足ＩＫ.L", (0.05, 0.02, 0.0)),
        ("movew", "足ＩＫ.R", (-0.30 * k, -0.02, 0.02 * k)),
        ("rotw", "上半身", Y, 8 * k + 24 * slump),
        ("rotw", "上半身", Z, A_TWIST),
        ("rotw", "首", Z, 30 * 0.4),
        ("rotw", "頭", Z, 30 * 0.6),
        ("rot", "頭", X, 10 * k + 22 * slump),
        ("rotw", "頭", Y, -4),
        ("hand", "R", "ひざ.R", (0.02, -0.05, 0.08), (-0.6, 0.2, -0.6)),
        ("curl", "R", 25, 8),
        ("hand", "L", "ひざ.L", (-0.02, -0.04, 0.10), (0.6, 0.3, -0.6)),
        ("curl", "L", 25, 8),
    ] + cloth(swing), {"悲しむ": 0.8, "まばたき": 1.0})


DEATH = {
    "length": 2.2, "fps": 15, "loop": False, "motion_end": 1.6,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.12, flinch(1.0), "out"),
        (0.40, swoon(1.0), "io"),
        (0.62, swoon(1.0), "io"),
        (1.05, kneel(1.0, swing=3), "in"),
        (1.25, kneel(1.0, slump=0.5, swing=-2), "out"),
        (1.6, kneel(1.0, slump=1.0), "io"),
    ],
}

# ------------------------------------------------------------------ Let the People Rejoice
# The signature clip (reference NOTES.md: the burst, f24-f30): she gathers,
# spins once on the spot with her arms drawn in, and opens into the
# performer's flourish -- up on the front toe, the rear leg lifted behind, back
# arched, the far arm flung high and the near arm wide, a delighted smile --
# holds it for the house, and settles back into the stance.


def gather():
    return pose(stance(drop=0.08, lean=4, twist=-10, head_nod=8, back_lift=0.0)
                + hands(far=(0.06, -0.16, 0.06), near=(-0.04, -0.16, 0.02), far_pole=(0.6, 0.2, -1.0),
                        near_pole=(-0.6, 0.2, -1.0), far_curl=(30, 10), near_curl=(30, 10))
                + cloth(-2),
                {"まばたき": 0.9, "にこり": 0.6})


def spin_pose(s):
    """s 0..1 through the pirouette: arms in, rising onto the toes."""
    rise = math.sin(math.pi * s)
    p = pose(stance(drop=0.08 - 0.10 * rise, lean=2 - 4 * rise, twist=-10, head_nod=4 - 10 * rise, front=0.04,
                    back=0.04, back_lift=0.10 * rise)
             + hands(far=(0.06, -0.14, 0.12 + 0.06 * rise), near=(-0.04, -0.14, 0.08 + 0.06 * rise),
                     far_pole=(0.6, 0.2, -1.0), near_pole=(-0.6, 0.2, -1.0), far_curl=(20, 5), near_curl=(20, 5))
             + cloth(6 * rise),
             {"にこり": 0.8, "まばたき": 0.4 * (1 - s)})
    return turned(p, 360.0 * s * s * (3 - 2 * s))


def flourish(k=1.0, wave=0.0):
    return pose(stance(drop=0.0, lean=-9 * k, twist=-12, head_turn=30, head_nod=-14 * k, head_tilt=-6,
                       front=0.08, back=0.16, back_lift=0.12 * k)
                + hands(far=(0.30, -0.06, 0.58 + 0.02 * wave), near=(-0.42, -0.02, 0.16 + 0.02 * wave),
                        far_pole=(0.0, 0.4, -1.0), near_pole=(0.0, 0.4, -1.0), far_curl=(6, 0), near_curl=(6, 0))
                + cloth(3 + 2 * wave),
                {"笑い": 1.0, "あ": 0.5})


SPIN_T0, SPIN_T1, SPIN_STEP = 0.14, 0.50, 0.03
_n = int(round((SPIN_T1 - SPIN_T0) / SPIN_STEP))
SPIN_KEYS = [(round(SPIN_T0 + SPIN_STEP * i, 6), spin_pose(i / _n), "lin") for i in range(_n + 1)]

REJOICE = {
    "length": 1.5, "fps": 20, "loop": False,
    "keys": [(0.0, idle_pose(0.5), "io"), (SPIN_T0, SPIN_KEYS[0][1], "io")] + SPIN_KEYS[1:] + [
        (0.60, flourish(1.0), "out"),
        (0.85, flourish(1.0, wave=1.0), "io"),
        (1.05, flourish(1.0), "io"),
        (1.30, idle_pose(0.5), "io"),
        (1.5, idle_pose(0.5), "io"),
    ],
    "events": {"main": 0.60},
}

# ------------------------------------------------------------------ stance B
# Where she is not fighting (the shop, character select): upright and pleased
# with herself, the near hand on her hip, the far hand turned up before her
# as if presenting the wares.


def regal(breath=0.0, swing=0.0, head_turn=30.0):
    b = breath
    return pose([("move", "センター", (0, 0, -0.01 - 0.005 * (1 - b))),
                 ("movew", "足ＩＫ.L", (0.07, 0.02, 0)),
                 ("movew", "足ＩＫ.R", (-0.06, -0.02, 0.02)),
                 ("rotw", "上半身", Y, -2.0 + 1.0 * (1 - b)),
                 ("rotw", "上半身", Z, -16),
                 ("rotw", "首", Z, head_turn * 0.4),
                 ("rotw", "頭", Z, head_turn * 0.6),
                 ("rot", "頭", X, -4 + 1.5 * (1 - b)),
                 ("rotw", "頭", Y, -5)]
                + hands(far=(0.28, -0.18, -0.04 + 0.01 * b), near=(-0.13, 0.02, -0.22),
                        far_pole=(0.3, 0.6, -1.0), near_pole=(-1.0, 0.2, 0.3), far_curl=(12, 0), near_curl=(45, 20),
                        far_aim=((0.8, -0.3, 0.1), -90.0))
                + cloth(swing),
                {"にやり": 0.6, "にこり": 0.3})


MERCHANT = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, regal(0.0, swing=-1.0), "io"),
        (1.5, regal(1.0, swing=1.0), "io"),
        (3.0, regal(0.0, swing=-1.0), "io"),
    ],
}

# ------------------------------------------------------------------ rest site
# Sitting on the ground facing the fire, knees drawn up, her hands on them.
REST = pose(
    [("move", "センター", (0, 0, -0.84)),
     ("movew", "足ＩＫ.L", (0.48, 0.10, 0.0)),
     ("movew", "足ＩＫ.R", (0.42, -0.14, 0.0)),
     ("rotw", "上半身", Y, 12),
     ("rotw", "上半身", Z, -14),
     ("rotw", "首", Z, 8),
     ("rotw", "頭", Z, 12),
     ("rot", "頭", X, 4),
     ("rotw", "頭", Y, -6),
     ("hand", "R", "ひざ.R", (0.03, -0.05, 0.04), (-0.5, -0.2, -1)),
     ("curl", "R", 30, 10),
     ("hand", "L", "ひざ.L", (0.03, -0.02, 0.07), (0.6, 0.3, -1)),
     ("curl", "L", 30, 10)],
    {"にこり": 0.5}, yaw=40)

# ------------------------------------------------------------------ character select
# Confident and theatrical ([USER], 2026-10-13: the old close-up, a clenched
# raised hand and the head bowed, looked "scared"): chin up, shoulders open,
# a self-assured smirk, the near hand on her hip and the far hand open in a
# small flourish at hip height, palm up.


def select_pose(head_turn=16.0):
    return pose([("move", "センター", (0, 0, -0.01)),
                 ("movew", "足ＩＫ.L", (0.07, 0.02, 0)),
                 ("movew", "足ＩＫ.R", (-0.06, -0.02, 0.02)),
                 ("rotw", "上半身", Y, -4.0),
                 ("rotw", "上半身", Z, -16),
                 ("rotw", "首", Z, head_turn * 0.4),
                 ("rotw", "頭", Z, head_turn * 0.6),
                 ("rot", "頭", X, -12),
                 ("rotw", "頭", Y, -6)]
                + hands(far=(0.30, -0.10, -0.20), near=NEAR, far_pole=(0.3, 0.6, -1.0), near_pole=NEAR_POLE,
                        far_curl=(10, 0), near_curl=(30, 10), far_aim=((0.8, -0.3, -0.2), -90.0), near_aim=NEAR_AIM)
                + cloth(0),
                {"あ": 0.3, "口角上げ": 1.0, "にやり２": 0.5, "眼角上": 0.2})


SELECT = select_pose()

# ------------------------------------------------------------------ roster tile
# The face close-up is cut from the same confident pose.
PORTRAIT = select_pose(head_turn=18.0)

# ------------------------------------------------------------------ scale reference
STAND = pose(
    stance(drop=0.0, lean=0.0, twist=-14, head_turn=34, head_nod=0, head_tilt=0.0, front=0.06, back=0.05,
           back_lift=0.0)
    + [("hand", "R", "足.R", (-0.08, -0.03, -0.25), (-1.0, 0.5, 0.0)),
       ("hand", "L", "足.L", (0.08, -0.02, -0.25), (1.0, 0.5, 0.0))],
    dict(SMUG))

CLIPS = {
    "idle": IDLE,
    "idle_low": IDLE_LOW,
    "attack": ATTACK,
    "cast": CAST,
    "hurt": HURT,
    "death": DEATH,
    "rejoice": REJOICE,
    "merchant": MERCHANT,
}
#: the clips that start and end in stance A (feet where idle plants them)
FROM_IDLE = ("attack", "cast", "hurt", "rejoice")

STILLS = {"stance_a": IDLE["keys"][0][1], "stand": STAND, "rest": REST, "select": SELECT,
          "portrait": PORTRAIT, "stance_b": MERCHANT["keys"][0][1]}


# ------------------------------------------------------------------ the guest stars
# Each guest star's one still: a calm rest at the same scale, each with a
# small lore-flavoured variation so no two stand alike ([USER], 2026-10-13:
# "they could use slightly more differentiated poses"). No arm is held out
# at shoulder height. Offsets are in Furina's units and scaled by `k`, the
# guest's head-bone height over hers; FW, BK, RT and LT are the guest's own
# front, back, right (near) and left (far) at the guest yaw.
GUEST_YAW = 24
_g = math.radians(GUEST_YAW)
FW = (math.sin(_g), -math.cos(_g), 0.0)
BK = tuple(-c for c in FW)
RT = (FW[1], -FW[0], 0.0)
LT = tuple(-c for c in RT)


def _v(*terms):
    return tuple(sum(s * vec[i] for s, vec in terms) for i in range(3))


def _sc(t, k):
    return tuple(c * k for c in t)


def _gbody(k, lean=-1.0, twist=-14, head=(12, 18), nod=0.0, tilt=0.0, sway=0.0, front=0.06, back=0.05):
    return [("move", "センター", (sway * k, 0, -0.01 * k)),
            ("movew", "足ＩＫ.L", (front * k, 0.02 * k, 0)),
            ("movew", "足ＩＫ.R", (-back * k, -0.02 * k, 0)),
            ("rotw", "上半身", Y, lean), ("rotw", "上半身", Z, twist),
            ("rotw", "首", Z, head[0]), ("rotw", "頭", Z, head[1]),
            ("rot", "頭", X, nod), ("rotw", "頭", Y, tilt)]


def _rest(side, k, curl=(25, 10), out=0.0):
    """An arm hanging easy at the side (the old neutral still)."""
    if side == "R":
        return [("hand", "R", "足.R", (-0.07 * k - out * k, -0.03 * k, -0.24 * k), (-1.0, 0.5, 0.0)), ("curl", "R", *curl)]
    return [("hand", "L", "足.L", (0.07 * k + out * k, -0.02 * k, -0.24 * k), (1.0, 0.5, 0.0)), ("curl", "L", *curl)]


def _hand(side, k, off, pole, curl=(25, 10), anchor=CH, aim=None):
    ops = [("hand", side, anchor, _sc(off, k), pole), ("curl", side, *curl)]
    if aim:
        ops.append(("aimw", f"手首.{side}", aim[0], aim[1]))
    return ops


def _neuvillette(k):    # upright, the near hand at his chest, on his lapel; the far arm easy at his side
    # ([USER], 2026-10-13: "where are Siegwinne and Neuvillette's arms?" --
    # his hands clasped behind his back hid both arms from the front)
    return (_gbody(k, lean=-2, head=(10, 14), nod=-3)
            + _hand("R", k, _v((0.13, FW), (0.03, LT), (-0.02, Z)), _v((1, RT), (0.3, BK), (-0.8, Z)), curl=(30, 10),
                    aim=(_v((1, LT), (0.4, Z), (0.2, FW)), 0))
            + _rest("L", k, curl=(30, 12)),
            {"真面目": 0.4})


def _wriothesley(k):    # arms crossed
    return (_gbody(k, lean=-1, head=(12, 16))
            + _hand("R", k, _v((0.12, FW), (0.09, LT), (-0.05, Z)), _v((1, RT), (0.4, FW), (-0.6, Z)), curl=(30, 10))
            + _hand("L", k, _v((0.14, FW), (0.09, RT), (-0.02, Z)), _v((1, LT), (0.4, FW), (-0.6, Z)), curl=(30, 10)),
            {"にやり": 0.4})


def _clorinde(k):       # upright and poised, shoulders back, chin up, the near hand on her hip
    # ([USER], 2026-10-13: "Clorinde looks weird as though she's hunched
    # over" -- the hand reached across to her far hip, rounding her near
    # shoulder, and her head was bowed under the hat)
    return (_gbody(k, lean=-6, head=(12, 18), nod=-14)
            + [("rot", "首", X, -10)]
            + _hand("R", k, _v((0.10, RT), (0.04, BK), (-0.22, Z)), _v((1, RT), (0.3, BK), (0.2, Z)), curl=(55, 20))
            + _rest("L", k),
            {"怒り目": 0.2})


def _navia(k):          # the near hand on her hip, a confident lean back
    return (_gbody(k, lean=-4, twist=-16, head=(12, 20), tilt=-6, sway=0.012)
            + _hand("R", k, NEAR, NEAR_POLE, curl=(30, 10), aim=NEAR_AIM)
            + _rest("L", k, out=0.01),
            {"にこり": 0.6, "笑い": 0.3})


def _lyney(k):          # the far hand raised to his hat brim
    return (_gbody(k, lean=-1, head=(12, 16), nod=4)
            + _rest("R", k)
            + _hand("L", k, _v((0.07, FW), (0.08, LT), (0.15, Z)), _v((1, LT), (-0.5, Z)), anchor="頭", curl=(30, 10)),
            {"にやり": 0.6})


def _lynette(k):        # arms loose, head tilted, deadpan
    return (_gbody(k, lean=1, head=(10, 12), tilt=12, nod=2)
            + _rest("R", k, curl=(15, 5), out=-0.01) + _rest("L", k, curl=(15, 5), out=-0.01),
            {"じと目": 0.5})


def _freminet(k):       # shy: head down, hands together low in front
    return (_gbody(k, lean=3, head=(8, 10), nod=10, tilt=4)
            + _hand("R", k, _v((0.14, FW), (0.01, LT), (-0.28, Z)), _v((1, RT), (0.3, BK)), curl=(35, 15))
            + _hand("L", k, _v((0.15, FW), (0.01, RT), (-0.27, Z)), _v((1, LT), (0.3, BK)), curl=(35, 15)),
            {"困る": 0.4})


def _charlotte(k):      # both hands up before her face, framing a photo
    return (_gbody(k, lean=-1, head=(12, 16))
            + _hand("R", k, _v((0.22, FW), (-0.16, Z)), _v((1, RT), (-1.0, Z)), anchor="頭", curl=(8, 0),
                    aim=(_v((0.3, FW), (1.0, Z)), 90))
            + _hand("L", k, _v((0.24, FW), (0.12, LT), (0.02, Z)), _v((1, LT), (-1.0, Z)), anchor="頭", curl=(8, 0),
                    aim=(_v((0.3, FW), (1.0, Z)), -90)),
            {"にこり": 0.6, "ウィンク": 1.0})


def _chevreuse(k):      # weight settled on the rear leg, the far hand on her hip
    return (_gbody(k, lean=-1, twist=-12, head=(12, 18), sway=-0.015, front=0.09)
            + _rest("R", k)
            + _hand("L", k, _v((0.12, LT), (0.02, BK), (-0.17, Z)), _v((1, LT), (0.4, BK)), curl=(30, 10)),
            {"真面目": 0.5})


def _sigewinne(k):      # hands clasped in front of her at the waist, held clear of her body, cheerful
    # ([USER], 2026-10-13: "where are Siegwinne and Neuvillette's arms?" --
    # her hands sat against her front and her forearms sank behind it)
    return (_gbody(k, lean=-2, head=(12, 18), tilt=-10, nod=-4)
            + _hand("R", k, _v((0.20, FW), (0.015, LT), (-0.20, Z)), _v((1, RT), (0.2, BK), (-0.4, Z)), curl=(40, 15))
            + _hand("L", k, _v((0.21, FW), (0.015, RT), (-0.19, Z)), _v((1, LT), (0.2, BK), (-0.4, Z)), curl=(40, 15)),
            {"笑い": 0.7, "にこり": 0.5})


def _escoffier(k):      # the far hand lifted at waist height, palm up, presenting a dish
    return (_gbody(k, lean=-1, head=(12, 18))
            + _rest("R", k)
            + _hand("L", k, FAR, IDLE_FAR_POLE, curl=(14, 0), aim=FAR_AIM),
            {"にこり": 0.5})


def _neutral(k):
    return (_gbody(k) + _rest("R", k) + _rest("L", k), {"にこり": 0.35})


GUEST_POSES = {"neuvillette": _neuvillette, "wriothesley": _wriothesley, "clorinde": _clorinde, "navia": _navia,
               "lyney": _lyney, "lynette": _lynette, "freminet": _freminet, "charlotte": _charlotte,
               "chevreuse": _chevreuse, "sigewinne": _sigewinne, "escoffier": _escoffier}


def guest_pose(k=1.0, name=None):
    """A guest star's one still: standing easy, facing right like Furina, in
    that guest's own variation (GUEST_POSES; `name` None is the plain rest).
    `k` scales every offset to the guest's own size."""
    ops, morphs = GUEST_POSES.get(name, _neutral)(k)
    return pose(ops, morphs, yaw=GUEST_YAW)
