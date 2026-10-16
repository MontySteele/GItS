"""Yae Miko's poses and clips, in WORLD terms, for tools/char_render/render.py.

Pure data plus a few builders; no bpy, so it imports anywhere. The pose
language is tools/klee_render/clips.py's (+X screen right, toward the enemy;
-Y toward the viewer; +Z up; the root yaw turns her front toward screen right,
so her right side, .R, is nearest the camera and her left arm, .L, is the far
arm, the one toward the enemy).

PHASE A (2026-10-14), a TEMPORARY model: the surfaces every kit needs and
nothing card-specific -- combat idle, low-HP idle, attack, cast, hurt, death
(the router's seven states need it), the shop loop, the rest seat, the select
close-up, the roster tile and the ground shadow. Kokomi's phase A
(kokomi_clips.py) is the template. Card clips wait until her build is final.

Her official pack carries no gohei or catalyst (scratch models/yae/unpacked:
the body PMX alone), so she fights with an open hand. Stance A is the Guuji at
ease: weight on the back foot, the near hand on her hip, the far hand before
her chest palm up, where an ofuda would sit. Her attack is a flick of that
hand at the enemy (her normal attack is a fox spirit loosed from the hand),
and the spirit is a PHANTOM as Furina's rapier is: render.py records a line
from her far hand's knuckles along the hand (`PHANTOM`), and fx.py draws the
streak, in the neutral heat layer the game tints Electro. Her cast plants a
Sesshou Sakura: the near hand up before her face in a seal, the far hand swept
down to the ground before her.

THE BODY (read off the PMX 2026-10-14 with no Blender, raw units x 0.08): the
观海 bone set, about 1.13x Kokomi's frame (chest 上半身2 1.268 up, neck 1.448,
head 1.523, shoulder 1.415, wrist 0.463 out at rest; Kokomi's 1.106, 1.276,
1.352, 1.252, 0.414), so Kokomi's hand offsets read on her at x `S`. Rest
height 1.8057 units (her ears and hair ornament on top). Height 70 in
(chars.py), Navia's: the two packs share a head-bone height to 0.2%.

HER CLOTH (the PMX's physics chains; nothing simulates them in a headless
render, so a pose places them). mmd_tools renames 左X / 右X to X.L / X.R on
import, so the names here are the imported ones:
  * ROBE: her long skirt is twelve 13-bone columns round her hips
    (后摆_0_0 .. 后摆_0_11, from 下半身, to mid-calf); the back six swing for
    secondary motion (`TAILS`) as Kokomi's tails do. Kneeling or seated, the
    front columns and the short front panel (スカート) would hang through her
    thighs, so `seated` lays them forward and down over her lap; whatever
    passes the ground line is cut by pack.py and reads as cloth on the floor.
  * SLEEVES: her hanging sleeves (袖_0_1.L/.R, 16 bones each from the
    elbow, a 4-bone tassel off the 14th). Every pose re-aims each sleeve's
    root toward SLEEVE_HANG after the arms are placed (`cloth`), Kokomi's rule.
  * the back ribbon (后带_0_1) swings with the robe.
Eyes-on at the first render: the robe in the seated and kneeling poses, the
sleeves, and the flick's streak.

The model is the official Yae Miko pack (观海, miHoYo); it is read in place
from the operator's scratch directory and NEVER enters the repo.
"""
from __future__ import annotations

import math

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
CH = "上半身2"
YAW = 16
#: her frame over Kokomi's (shoulder height 1.415 / 1.252): Kokomi's offsets x S
S = 1.13
#: the back columns of her robe and the back ribbon (chain roots, from the hips)
TAILS = ["后摆_0_4", "后摆_0_5", "后摆_0_6", "后摆_0_7", "后带_0_1"]
#: the robe's front columns and the short front panel: laid over her lap when
#: she kneels or sits (`seated`)
FRONT = ["后摆_0_0", "后摆_0_1", "后摆_0_10", "后摆_0_11",
         "スカート_0_0", "スカート_0_1", "スカート_0_2", "スカート_0_3", "スカート_0_4"]
#: the hanging sleeves (chain roots, parented to each elbow), side -> bone
SLEEVES = {"L": "袖_0_1.L", "R": "袖_0_1.R"}
#: where a sleeve hangs from the elbow: down and a little behind her (world)
SLEEVE_HANG = (0.0, 0.55, -1.0)
#: the fox spirit's streak: a line from the far hand's knuckles along the
#: hand, this long (units; between Kokomi's jet, 0.45, and Furina's rapier)
PHANTOM = {"L": 0.55}

# ------------------------------------------------------------------ stance A
A_DROP, A_LEAN, A_TWIST = 0.03, -2.0, -16.0
A_FRONT, A_BACK = 0.09, 0.08
SMUG = {"にやり": 0.5, "じと目": 0.25}
#: the far hand before her chest, palm up, where the ofuda sits. Never above
#: the shoulder or straight out (Furina's "salute" lesson, 2026-10-13).
FAR = (0.20, -0.21, -0.04)
FAR_POLE = (0.2, 0.6, -1.0)
#: the wrist turned palm up (aimw: the hand along this world direction,
#: rolled -90 degrees about it)
FAR_AIM = ((0.8, -0.3, 0.1), -90.0)
#: the near hand on her hip, elbow out
NEAR = (-0.15, -0.05, -0.17)
NEAR_POLE = (-1.0, 0.3, 0.0)


def add(v, dv):
    return tuple(a + b for a, b in zip(v, dv))


def fwd(yaw, d=1.0):
    """Her front at this root yaw, d long (world)."""
    r = math.radians(yaw)
    return (math.sin(r) * d, -math.cos(r) * d, 0.0)


def stance(drop=A_DROP, lean=A_LEAN, twist=A_TWIST, head_turn=34.0, head_nod=1.0, head_tilt=-5.0,
           front=A_FRONT, back=A_BACK, back_lift=0.0, sway=0.0):
    """Feet planted a little apart (far foot toward the enemy), weight back,
    chest toward the viewer, head to the right and tilted, as if amused."""
    return [
        ("move", "センター", (sway, 0, -drop)),
        ("movew", "足ＩＫ.L", (front, 0.02, 0)),
        ("movew", "足ＩＫ.R", (-back, -0.02, back_lift)),
        ("rotw", "上半身", Y, lean),
        ("rotw", "上半身", Z, twist),
        ("rotw", "首", Z, head_turn * 0.4),
        ("rotw", "頭", Z, head_turn * 0.6),
        ("rot", "頭", X, head_nod),
        ("rotw", "頭", Y, head_tilt),
    ]


def hands(far=FAR, near=NEAR, far_pole=FAR_POLE, near_pole=NEAR_POLE, far_curl=(12, 4), near_curl=(30, 10),
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


def cloth(swing=0.0, sleeve_swing=0.0, seated_yaw=None):
    """The robe's back columns and the ribbon swing about the world Y axis
    (sideways on screen); with `seated_yaw` (the pose's root yaw) the front
    columns lie forward and down over her lap. Each sleeve then hangs from its
    elbow (SLEEVE_HANG), swung back by `sleeve_swing` (positive trails the
    sleeves behind a forward motion). Applied last: the cloth hangs from
    wherever the body ended up."""
    ops = [("rotw", b, Y, swing * (1.0 + 0.15 * i)) for i, b in enumerate(TAILS)]
    if seated_yaw is not None:
        f = fwd(seated_yaw, 0.8)
        ops += [("aimw", b, (f[0], f[1], -0.6)) for b in FRONT]
    hang = (0.0, SLEEVE_HANG[1] + 0.01 * sleeve_swing, SLEEVE_HANG[2])
    ops += [("aimw", SLEEVES[s], hang) for s in ("R", "L")]
    return ops


def pose(ops, morphs=None, yaw=YAW, root=(0, 0, 0)):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "root": tuple(root), "root_rot": 0.0}


def idle_pose(breath=0.0, swing=0.0, blink=0.0):
    """Stance A, the Guuji at ease: weight back, the near hand on her hip,
    the far hand palm up before her chest. breath 0..1: the in-breath lifts
    the chest and the open hand rises a hair."""
    b = breath
    m = dict(SMUG)
    if blink:
        m["まばたき"] = blink
    return pose(stance(drop=A_DROP + 0.006 * (1 - b), lean=A_LEAN - 1.0 * b, head_nod=1 - 1.5 * b,
                       head_tilt=-5 - 1.0 * b, sway=-0.006 * b)
                + hands(far=add(FAR, (0.004 * b, 0.0, 0.016 * b)), near=add(NEAR, (0, 0, 0.006 * b)),
                        far_curl=(14 - 4 * b, 4), far_aim=FAR_AIM)
                + cloth(swing),
                m)


IDLE = {
    "length": 2.8, "fps": 12, "loop": True,
    "keys": [
        (0.0, idle_pose(0.0, swing=-1.2), "io"),
        (1.4, idle_pose(1.0, swing=1.2), "io"),
        (1.75, idle_pose(0.8, swing=1.0), "io"),
        (1.82, idle_pose(0.77, swing=0.9, blink=1.0), "io"),
        (1.9, idle_pose(0.74, swing=0.8), "io"),
        (2.8, idle_pose(0.0, swing=-1.2), "io"),
    ],
}

# ------------------------------------------------------------------ low HP
# Still amused, but tired: shoulders and head low, the far hand drawn in to
# her chest, the near hand off her hip and hanging, a troubled brow.


def low_pose(breath=0.0, swing=0.0):
    b = breath
    return pose(stance(drop=A_DROP + 0.035 + 0.006 * (1 - b), lean=A_LEAN + 10 + 1.5 * (1 - b), head_turn=28,
                       head_nod=14 + 2 * (1 - b))
                + hands(far=(0.13, -0.18, 0.00 + 0.01 * b), near=(-0.09, -0.06, -0.38),
                        far_pole=(0.6, 0.2, -1.0), far_curl=(35, 15), near_curl=(20, 5))
                + cloth(swing),
                {"困る": 0.6, "にやり": 0.2, "じと目": 0.3})


IDLE_LOW = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, low_pose(0.0, swing=-0.8), "io"),
        (1.5, low_pose(1.0, swing=0.8), "io"),
        (3.0, low_pose(0.0, swing=-0.8), "io"),
    ],
}

# ------------------------------------------------------------------ attack
# A flick of the far hand: she draws it back across her chest, then sweeps it
# out at the enemy, fingers pointing at the target, loosing the fox spirit
# (the phantom streak, PHANTOM) as she shifts her weight forward. No lunge:
# she does not close the distance.


def atk(far, near, far_pole=FAR_POLE, near_pole=NEAR_POLE, drop=A_DROP, lean=A_LEAN, twist=A_TWIST,
        front=A_FRONT, back=A_BACK, back_lift=0.0, head_turn=34.0, head_nod=1.0, swing=0.0, sleeve=0.0,
        morphs=None, yaw=YAW, far_aim=None, far_curl=(6, 0)):
    return pose(stance(drop=drop, lean=lean, twist=twist, front=front, back=back, back_lift=back_lift,
                       head_turn=head_turn, head_nod=head_nod)
                + hands(far=far, near=near, far_pole=far_pole, near_pole=near_pole, far_curl=far_curl,
                        near_curl=(30, 10), far_aim=far_aim)
                + cloth(swing, sleeve),
                morphs or {"にやり": 0.6, "じと目": 0.2}, yaw=yaw)


#: the flick: the far arm out at the enemy a little below the shoulder, the
#: fingers pointing at the target (the streak runs along the hand: render.py
#: phantom_points), weight onto the front foot
FLICK = (0.54, -0.08, 0.06)
FLICK_AIM = ((1.0, -0.1, 0.0), 0.0)
#: the wind-up: the far hand drawn back across her chest, palm in
WIND = (0.02, -0.22, 0.06)
WIND_AIM = ((-0.4, -0.6, 0.4), 90.0)
LEAN_IN = dict(drop=0.05, lean=5.0, twist=-8.0, front=0.11, back=0.09, back_lift=0.02, head_turn=40, head_nod=0,
               yaw=24)

ATTACK = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        # wind-up: the far hand drawn back across her chest, weight back
        (0.18, atk(WIND, NEAR, far_pole=(0.6, 0.2, -1.0), drop=0.04, lean=-5, twist=-22, swing=-1.5,
                   far_aim=WIND_AIM, far_curl=(25, 8), yaw=14, morphs={"にやり": 0.7, "じと目": 0.4}), "out"),
        (0.28, atk(add(WIND, (0.08, 0.0, 0.0)), NEAR, far_pole=(0.6, 0.2, -1.0), drop=0.04, lean=-4, twist=-20,
                   swing=-1.0, far_aim=WIND_AIM, far_curl=(18, 6), yaw=16), "io"),
        # the flick (impact, frame 8)
        (0.40, atk(FLICK, NEAR, far_pole=(0.0, 0.5, -1.0), swing=3, sleeve=6, far_aim=FLICK_AIM,
                   morphs={"にやり": 0.8, "ウィンク": 0.5}, **LEAN_IN), "in"),
        (0.52, atk(add(FLICK, (0.01, 0.0, -0.01)), NEAR, far_pole=(0.0, 0.5, -1.0), swing=2, sleeve=4,
                   far_aim=FLICK_AIM, morphs={"にやり": 0.8, "ウィンク": 0.3}, **{**LEAN_IN, "drop": 0.055}), "out"),
        # recover: the hand back to the stance's open palm
        (0.72, atk((0.30, -0.20, 0.0), NEAR, far_pole=FAR_POLE, drop=0.035, lean=0, twist=-14, swing=-1,
                   far_aim=FAR_AIM, yaw=18), "io"),
        (0.88, idle_pose(0.5), "out"),
        (1.0, idle_pose(0.5), "io"),
    ],
    "events": {"impact": [0.40], "main": 0.40},
    # the flick sweeps a short ribbon off the hand; the spirit itself is a streak
    "trails": [{"blade": "L", "from": 0.28, "to": 0.40, "age": 0.10, "inner": 0.2, "taper": 0.6}],
    "bursts": [{"t": 0.40, "blade": "L", "kind": "thrust", "scale": 0.9}],
}

# ------------------------------------------------------------------ cast
# She plants a Sesshou Sakura: the near hand up before her face in a seal,
# the far hand swept down and out to the ground before her, palm down.


def plant(k=1.0):
    return pose(stance(drop=A_DROP + 0.03 * k, lean=A_LEAN + 6 * k, twist=A_TWIST - 2 * k, head_nod=1 + 6 * k,
                       head_tilt=-5 + 2 * k)
                + hands(far=(0.20 + 0.10 * k, -0.20, -0.04 - 0.30 * k), near=(0.0, -0.20, 0.04 + 0.16 * k),
                        far_pole=(0.2, 0.4, -1.0), near_pole=(-0.8, 0.0, -0.6), far_curl=(10, 0),
                        near_curl=(20, 10), far_aim=((0.6, -0.2, -0.8), 0.0))
                + cloth(-1.5 * k, 2 * k),
                {"にやり": 0.5, "なごみ": 0.4 * k, "じと目": 0.2})


CAST = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.16, plant(0.6), "out"),
        (0.30, plant(1.0), "out"),
        (0.70, plant(1.0), "io"),
        (1.0, idle_pose(0.5), "io"),
    ],
}

# ------------------------------------------------------------------ hurt


def flinch(k=1.0):
    return pose(stance(drop=A_DROP + 0.03 * k, lean=A_LEAN - 12 * k, twist=A_TWIST - 6 * k, head_turn=34 - 10 * k,
                       head_nod=1 - 9 * k, head_tilt=-5 - 6 * k)
                + hands(far=(0.15 - 0.04 * k, -0.20, 0.08), near=(-0.04, -0.18, 0.04),
                        far_pole=(0.6, 0.2, -1.0), near_pole=(-0.8, 0.1, -0.6), far_curl=(40, 15),
                        near_curl=(40, 15))
                + cloth(-4 * k, -3 * k),
                {"まばたき": 0.8 * k, "困る": 0.7, "い": 0.4 * k})


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
# She staggers, a hand to her chest, and sinks to her knees, head bowed.
# Holds from 1.6 s.


def stagger(k=1.0):
    return pose(stance(drop=A_DROP + 0.05 * k, lean=A_LEAN + 12 * k, head_nod=1 + 14 * k, head_tilt=-7)
                + hands(far=(0.07, -0.16, 0.02), near=(-0.13, -0.07, -0.34), far_pole=(0.6, 0.2, -1.0),
                        far_curl=(35, 12), near_curl=(15, 5))
                + cloth(-3 * k),
                {"悲しむ": 0.8, "まばたき": 0.6 * k})


def kneel(k=1.0, slump=0.0, swing=0.0):
    """Down on both knees, shins back, sitting toward her heels (Kokomi's at
    x S); `slump` folds her forward over her knees. The robe's front lies
    over her lap."""
    return pose([
        ("move", "センター", (0, 0, -0.57 * k - 0.09 * slump)),
        ("movew", "足ＩＫ.L", (0.06, 0.02, 0.0)),
        ("movew", "足ＩＫ.R", (-0.34 * k, -0.02, 0.02 * k)),
        ("rotw", "上半身", Y, 8 * k + 24 * slump),
        ("rotw", "上半身", Z, A_TWIST),
        ("rotw", "首", Z, 28 * 0.4),
        ("rotw", "頭", Z, 28 * 0.6),
        ("rot", "頭", X, 10 * k + 22 * slump),
        ("rotw", "頭", Y, -4),
        ("hand", "R", "ひざ.R", (0.02, -0.06, 0.09), (-0.6, 0.2, -0.6)),
        ("curl", "R", 25, 8),
        ("hand", "L", "ひざ.L", (-0.02, -0.05, 0.11), (0.6, 0.3, -0.6)),
        ("curl", "L", 25, 8),
    ] + cloth(swing, seated_yaw=YAW), {"悲しむ": 0.8, "まばたき": 1.0})


DEATH = {
    "length": 2.2, "fps": 15, "loop": False, "motion_end": 1.6,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.12, flinch(1.0), "out"),
        (0.45, stagger(1.0), "io"),
        (0.62, stagger(1.0), "io"),
        (1.05, kneel(1.0, swing=2), "in"),
        (1.25, kneel(1.0, slump=0.5, swing=-1.5), "out"),
        (1.6, kneel(1.0, slump=1.0), "io"),
    ],
}

# ------------------------------------------------------------------ stance B
# Where she is not fighting (the shop, character select): the Guuji receiving
# a visitor -- upright, hands folded into her sleeves before her waist, head
# tilted, a knowing smile.


def demure(breath=0.0, swing=0.0, head_turn=28.0):
    b = breath
    return pose([("move", "センター", (0, 0, -0.01 - 0.005 * (1 - b))),
                 ("movew", "足ＩＫ.L", (0.06, 0.02, 0)),
                 ("movew", "足ＩＫ.R", (-0.05, -0.02, 0)),
                 ("rotw", "上半身", Y, -2.0 + 1.0 * (1 - b)),
                 ("rotw", "上半身", Z, -16),
                 ("rotw", "首", Z, head_turn * 0.4),
                 ("rotw", "頭", Z, head_turn * 0.6),
                 ("rot", "頭", X, 3 + 1.5 * (1 - b)),
                 ("rotw", "頭", Y, -9)]
                + hands(far=(0.07, -0.21, -0.27 + 0.006 * b), near=(0.02, -0.22, -0.28 + 0.006 * b),
                        far_pole=(0.8, 0.3, -0.6), near_pole=(-0.8, 0.3, -0.6), far_curl=(30, 12),
                        near_curl=(30, 12))
                + cloth(swing),
                {"にやり": 0.5, "なごみ": 0.4})


MERCHANT = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, demure(0.0, swing=-0.8), "io"),
        (1.5, demure(1.0, swing=0.8), "io"),
        (3.0, demure(0.0, swing=-0.8), "io"),
    ],
}

# ------------------------------------------------------------------ rest site
# Seiza by the fire, as a shrine's Guuji sits: on her heels, knees forward,
# hands in her lap, the robe laid over her thighs.
REST_YAW = 40
_back = fwd(REST_YAW, -0.24)
REST = pose(
    [("move", "センター", (0, 0, -0.68)),
     ("movew", "足ＩＫ.L", (_back[0] + 0.04, _back[1], 0.0)),
     ("movew", "足ＩＫ.R", (_back[0] - 0.04, _back[1], 0.0)),
     ("rotw", "上半身", Y, 4),
     ("rotw", "上半身", Z, -14),
     ("rotw", "首", Z, 8),
     ("rotw", "頭", Z, 12),
     ("rot", "頭", X, 6),
     ("rotw", "頭", Y, -6),
     ("hand", "R", "ひざ.R", (0.0, -0.06, 0.08), (-0.5, -0.2, -1)),
     ("curl", "R", 30, 10),
     ("hand", "L", "ひざ.L", (0.0, -0.04, 0.10), (0.6, 0.3, -1)),
     ("curl", "L", 30, 10)] + cloth(0.0, seated_yaw=REST_YAW),
    {"にやり": 0.4, "なごみ": 0.5}, yaw=REST_YAW)

# ------------------------------------------------------------------ character select
# Sly and sure: chin level, a knowing half-lidded smile, the near hand raised
# under her chin, the far hand on her hip.


def select_pose(head_turn=16.0):
    return pose([("move", "センター", (0, 0, -0.01)),
                 ("movew", "足ＩＫ.L", (0.06, 0.02, 0)),
                 ("movew", "足ＩＫ.R", (-0.05, -0.02, 0)),
                 ("rotw", "上半身", Y, -3.0),
                 ("rotw", "上半身", Z, -16),
                 ("rotw", "首", Z, head_turn * 0.4),
                 ("rotw", "頭", Z, head_turn * 0.6),
                 ("rot", "頭", X, -3),
                 ("rotw", "頭", Y, -8)]
                + hands(far=(0.15, -0.05, -0.17), near=(0.02, -0.17, 0.20), far_pole=(1.0, 0.3, 0.0),
                        near_pole=(-0.8, 0.0, -0.6), far_curl=(30, 10), near_curl=(35, 15))
                + cloth(0),
                {"にやり": 0.6, "口角上げ": 0.4, "じと目": 0.25})


SELECT = select_pose()

# ------------------------------------------------------------------ roster tile
# The face close-up is cut from the same pose.
PORTRAIT = select_pose(head_turn=18.0)

# ------------------------------------------------------------------ scale reference
STAND = pose(
    stance(drop=0.0, lean=0.0, twist=-14, head_turn=34, head_nod=0, head_tilt=0.0, front=0.06, back=0.05)
    + [("hand", "R", "足.R", (-0.09, -0.03, -0.28), (-1.0, 0.5, 0.0)),
       ("hand", "L", "足.L", (0.09, -0.02, -0.28), (1.0, 0.5, 0.0))]
    + cloth(0),
    dict(SMUG))

CLIPS = {
    "idle": IDLE,
    "idle_low": IDLE_LOW,
    "attack": ATTACK,
    "cast": CAST,
    "hurt": HURT,
    "death": DEATH,
    "merchant": MERCHANT,
}
#: the clips that start and end in stance A (feet where idle plants them)
FROM_IDLE = ("attack", "cast", "hurt")

STILLS = {"stance_a": IDLE["keys"][0][1], "stand": STAND, "rest": REST, "select": SELECT,
          "portrait": PORTRAIT, "stance_b": MERCHANT["keys"][0][1]}
