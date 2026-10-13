"""Varka's poses and clips, in WORLD terms, for tools/char_render/render.py.

Pure data plus a few builders; no bpy, so it imports anywhere. The pose
language is tools/klee_render/clips.py's (+X screen right, toward the enemy;
-Y toward the viewer; +Z up; the root yaw turns his front toward screen right,
so his right side, .R, is nearest the camera), plus BLADES:

  blades  {"R": blade, "L": blade} -- his two claymores ([USER], 2026-10-13:
          "Varka is a dual wielder, carrying TWO claymores, one in each
          hand"), the near (right) hand's and the far (left) hand's. A blade:
            at      world offset from `anchor`'s head to the point the hand
                    closes on (anchor "ground" = the feet's origin)
            anchor  a bone (default 上半身2, the upper chest) or "ground"
            dir     world direction guard -> tip
            roll    degrees about the blade (0: the flat faces the viewer)
            hand    False = the blade lies free (planted, laid down)
            pole    the elbow's bend direction (world)
            grip    where on the handle the hand closes (default: the
                    blade's own grip from chars.py; the pommel to rest on)
            curl    (finger, thumb) degrees
          A blade missing from a pose is hidden.

A CLIP is {length, fps, loop, keys: [(t, pose, ease)], events, trails, bursts}:
`events` names marked times (the impacts; `main` is the one the hit lands
on), `trails` the windows in which a blade leaves a slash trail and `bursts`
the impact flashes (fx.py draws both, colourless). Every combat clip plants his feet
where stance A does, so blends in and out of idle never slide them.

THE SCALE: the model stands 2.05 units (import 0.08); every offset below is in
those units, about 1.86x Klee's. His ruled height is 78 in (chars.py).

The model is the official Varka pack (观海子, miHoYo); it is read in place from
the operator's scratch directory and NEVER enters the repo.
"""
from __future__ import annotations

import math

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
CH = "上半身2"
YAW = 14                 # chest a little off-centre toward the viewer, as the base cast's
#: the coat skirt's twelve hanging chains (xb_0_j hang from 下半身), the belt
#: tails, and the short cape on his right shoulder: swung for secondary motion
SKIRT = [f"xb_0_{j}" for j in range(12)]
TAILS = ["d.L", "d.R", "d2.L", "d2.R"]
CAPE = "pf_0_0"

# ------------------------------------------------------------------ stance A
# Knees a little bent, feet a little wider, weight forward. The near hand's
# claymore rests on his shoulder (blade up and back, angled behind his head);
# the leading blade stays low and forward toward the enemy. The shoulder rest
# keeps his footprint near his body (design review, 2026-10-13: the trailing
# rear blade made the old stance twice as wide as he is tall).
A_DROP = 0.10            # hips lowered: knees slightly bent
A_LEAN = 10.0            # upper body toward the enemy (weight forward)
A_FRONT = 0.34           # far foot toward the enemy
A_BACK = 0.31            # near foot back
A_FRONT_Y, A_BACK_Y = 0.03, -0.04
A_TWIST = -14.0
STERN = {"真面目": 0.55, "にやり": 0.15}
#: the leading blade (far hand): low before him, angled forward and down and
#: a little toward the viewer, its tip about knee height toward the enemy
LEAD_AT = (0.30, -0.04, -0.38)
LEAD_DIR = (0.68, -0.58, -0.44)
LEAD_ROLL = 30.0         # the flat turned partly off the viewer: edge-on, a blade reads as a hairline
LEAD_POLE = (0.4, 0.5, -1.0)
#: the near hand's blade on his shoulder: the hand before his chest, the
#: blade up and back over the shoulder, behind his head
REAR_AT = SHOULDER_AT = (-0.02, -0.24, -0.17)
REAR_DIR = SHOULDER_DIR = (-0.40, 0.55, 0.73)
REAR_POLE = SHOULDER_POLE = (0.1, -0.5, -1.0)
REAR_ROLL = -25.0


def stance(drop=A_DROP, lean=A_LEAN, twist=A_TWIST, head_turn=34.0, head_nod=4.0, head_tilt=-2.0,
           front=A_FRONT, back=A_BACK, sway=0.0):
    """Feet planted wide (far foot toward the enemy), chest toward the viewer,
    head to the right."""
    return [
        ("move", "センター", (sway, 0, -drop)),
        ("movew", "足ＩＫ.L", (front, A_FRONT_Y, 0)),
        ("movew", "足ＩＫ.R", (-back, A_BACK_Y, 0)),
        ("rotw", "上半身", Y, lean),
        ("rotw", "上半身", Z, twist),
        ("rotw", "首", Z, head_turn * 0.4),
        ("rotw", "頭", Z, head_turn * 0.6),
        ("rot", "頭", X, head_nod),
        ("rotw", "頭", Y, head_tilt),
    ]


def cloth(swing=0.0, flare=0.0):
    """Secondary motion: the coat skirt and belt tails swing about the world
    Y axis (sideways on screen); `flare` lifts the skirt's front and back
    edges (a jump, a landing)."""
    ops = []
    for j, b in enumerate(SKIRT):
        side = math.cos(2 * math.pi * (j + 0.5) / 12)      # +1 front, -1 back of the ring
        ops.append(("rotw", b, Y, swing + flare * (1 if side > 0 else -1) * abs(side)))
    for b in TAILS:
        ops.append(("rotw", b, Y, swing * 1.4))
    ops.append(("rotw", CAPE, Y, swing * 0.8))
    return ops


def blade(at, d, pole, anchor=CH, roll=0.0, hand=True, grip=None, curl=(80, 40)):
    b = {"at": tuple(at), "dir": tuple(d), "pole": tuple(pole), "anchor": anchor, "roll": roll,
         "hand": hand, "curl": tuple(curl)}
    if grip is not None:
        b["grip"] = grip
    return b


def pose(ops, morphs=None, yaw=YAW, blades=None, root=(0, 0, 0), root_rot=0.0):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "blades": dict(blades or {}),
            "root": tuple(root), "root_rot": root_rot}


def add(v, dv):
    return tuple(a + b for a, b in zip(v, dv))


def idle_pose(breath=0.0, swing=0.0, blink=0.0):
    """breath 0..1: the in-breath raises the chest and lifts both blades a hair."""
    b = breath
    m = dict(STERN)
    if blink:
        m["まばたき"] = blink
    lift = (0, 0, 0.012 * b)
    return pose(
        stance(drop=A_DROP + 0.012 * (1 - b), lean=A_LEAN + 2.0 * (1 - b), head_nod=4.0 + 2.0 * (1 - b))
        + cloth(swing),
        m,
        blades={"L": blade(add(LEAD_AT, lift), LEAD_DIR, LEAD_POLE, roll=LEAD_ROLL),
                "R": blade(add(REAR_AT, lift), REAR_DIR, REAR_POLE, roll=REAR_ROLL)})


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
# Shoulders down, head low; the shoulder blade has slid down, and both tips
# drag on the ground before him.


def low_pose(breath=0.0, swing=0.0):
    b = breath
    return pose(
        stance(drop=A_DROP + 0.03 + 0.01 * (1 - b), lean=A_LEAN + 9 + 3 * (1 - b), head_turn=28,
               head_nod=16 + 3 * (1 - b))
        + cloth(swing),
        {"困る": 0.6, "真面目": 0.3, "あ": 0.2},
        blades={"L": blade((0.28, -0.04, -0.48 - 0.01 * (1 - b)), (0.88, -0.06, -0.47), (0.4, 0.4, -1.0), roll=LEAD_ROLL),
                "R": blade((0.02, -0.24, -0.50 - 0.01 * (1 - b)), (0.58, -0.40, -0.71), (-0.2, -0.4, -1.0),
                           roll=REAR_ROLL)})


IDLE_LOW = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, low_pose(0.0, swing=-1.0), "io"),
        (1.5, low_pose(1.0, swing=1.0), "io"),
        (3.0, low_pose(0.0, swing=-1.0), "io"),
    ],
}

# ------------------------------------------------------------------ attack
# An X cut at the enemy (design review, 2026-10-13). Strike 1: the leading
# blade is hauled up and back over his head and cleaves diagonally down to
# low front-right (impact 1, frame 6). Strike 2, the main one: the near blade
# comes off his shoulder, from behind over the top and DOWN in front of him,
# crossing the first cut (impact 2, frame 11) and ending low in front. At both
# impacts the striking blade points right, toward the enemy, between chest
# and knee height. Then he puts the near blade back on his shoulder.


def atk(lead, rear, lean=A_LEAN, twist=A_TWIST, drop=A_DROP, head_turn=34.0, swing=0.0, morphs=None):
    return pose(stance(drop=drop, lean=lean, twist=twist, head_turn=head_turn) + cloth(swing),
                morphs or {"怒り": 0.5, "真面目": 0.4},
                blades={"L": lead, "R": rear})


SHOULDER = blade(SHOULDER_AT, SHOULDER_DIR, SHOULDER_POLE, roll=REAR_ROLL)
#: strike 1, the lead blade: wound up high and back, over the top, cleaved down
LEAD_UP = blade((0.02, 0.02, 0.30), (-0.45, 0.12, 0.88), (0.6, 0.3, -0.4), roll=LEAD_ROLL)
LEAD_OVER = blade((0.22, -0.02, 0.24), (0.42, -0.06, 0.90), (0.6, 0.3, -0.6), roll=LEAD_ROLL)
LEAD_DOWN = blade((0.44, -0.06, -0.30), (0.90, -0.12, -0.42), (0.3, 0.5, -1.0), roll=LEAD_ROLL)
#: strike 2, the near blade: off the shoulder to high behind, over the top,
#: down in front through the enemy, crossing the first cut steeper
REAR_BACK = blade((-0.04, -0.20, 0.30), (-0.62, 0.10, 0.78), (-0.2, -0.3, -1.0), roll=REAR_ROLL)
REAR_OVER = blade((0.16, -0.24, 0.34), (0.30, -0.12, 0.95), (0.0, -0.4, -1.0), roll=REAR_ROLL)
REAR_DOWN = blade((0.30, -0.30, -0.02), (0.62, -0.18, -0.76), (-0.2, -0.4, -1.0), roll=REAR_ROLL)
REAR_LOW = blade((0.32, -0.28, -0.20), (0.75, -0.20, -0.63), (-0.2, -0.4, -1.0), roll=REAR_ROLL)
#: back to the shoulder: tip up in front first, so the turn never sweeps under
REAR_RAISE = blade((0.10, -0.28, -0.04), (0.22, -0.20, 0.95), (0.0, -0.5, -1.0), roll=REAR_ROLL)

ATTACK = {
    "length": 0.95, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.16, atk(LEAD_UP, SHOULDER, lean=-4, twist=-8, drop=A_DROP + 0.03, head_turn=40, swing=-3), "io"),
        (0.24, atk(LEAD_OVER, SHOULDER, lean=A_LEAN, twist=-14, drop=A_DROP + 0.04, swing=1), "in"),
        (0.30, atk(LEAD_DOWN, SHOULDER, lean=A_LEAN + 12, twist=-18, drop=A_DROP + 0.06, swing=3), "out"),
        (0.38, atk(LEAD_DOWN, REAR_BACK, lean=A_LEAN + 2, twist=-10, drop=A_DROP + 0.05, head_turn=38, swing=-2,
                   morphs={"怒り": 0.6, "真面目": 0.3}), "io"),
        (0.47, atk(LEAD_DOWN, REAR_OVER, lean=A_LEAN + 6, twist=-14, drop=A_DROP + 0.04, swing=1,
                   morphs={"怒り": 0.6, "あ": 0.3}), "in"),
        (0.55, atk(LEAD_DOWN, REAR_DOWN, lean=A_LEAN + 14, twist=-20, drop=A_DROP + 0.07, head_turn=30, swing=4,
                   morphs={"怒り": 0.7, "あ": 0.5}), "out"),
        (0.64, atk(LEAD_DOWN, REAR_LOW, lean=A_LEAN + 12, twist=-18, drop=A_DROP + 0.07, head_turn=30, swing=2), "io"),
        (0.80, atk(blade(LEAD_AT, LEAD_DIR, LEAD_POLE, roll=LEAD_ROLL), REAR_RAISE, lean=A_LEAN + 2, swing=-1), "io"),
        (0.95, idle_pose(0.5), "io"),
    ],
    # the impacts the game should time its hit to; "main" is the second
    "events": {"impact": [0.30, 0.55], "main": 0.55},
    "trails": [{"blade": "L", "from": 0.16, "to": 0.32}, {"blade": "R", "from": 0.40, "to": 0.58}],
    "bursts": [{"t": 0.30, "blade": "L", "kind": "slash", "scale": 0.8},
               {"t": 0.55, "blade": "R", "kind": "slash", "scale": 1.0}],
}

# ------------------------------------------------------------------ cast
# Both blades raised and crossed before him: a knightly salute.


def salute(k=1.0):
    return pose(
        stance(drop=A_DROP - 0.02 * k, lean=A_LEAN - 8 * k, twist=A_TWIST - 4 * k, head_turn=34 - 6 * k,
               head_nod=4 - 4 * k)
        + cloth(-1.5 * k),
        {"真面目": 0.9},
        blades={"L": blade((0.20, -0.30, -0.02), (-0.36, -0.06, 0.93), (0.8, 0.2, -0.6), roll=20),
                "R": blade((0.02, -0.34, -0.02), (0.42, -0.06, 0.90), (-0.8, 0.2, -0.6), roll=-20)})


CAST = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.32, salute(1.0), "io"),
        (0.70, salute(1.0), "io"),
        (1.0, idle_pose(0.5), "io"),
    ],
}

# ------------------------------------------------------------------ hurt
# A flinch back behind the crossed blades.


def guard(k=1.0):
    return pose(
        stance(drop=A_DROP + 0.03 * k, lean=A_LEAN - 20 * k, twist=A_TWIST - 6 * k, head_turn=30 - 8 * k,
               head_nod=4 + 8 * k, head_tilt=-2 - 6 * k)
        + cloth(-5 * k),
        {"まばたき": 0.8 * k, "怒り": 0.6, "あ": 0.3 * k},
        blades={"L": blade((0.22, -0.28, -0.20), (-0.45, -0.06, 0.89), (0.8, 0.2, -0.6), roll=20),
                "R": blade((0.02, -0.32, -0.18), (0.50, -0.06, 0.86), (-0.8, 0.2, -0.6), roll=-20)})


HURT = {
    "length": 0.8, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.10, guard(1.0), "out"),
        (0.32, guard(0.85), "io"),
        (0.80, idle_pose(0.5), "io"),
    ],
}

# ------------------------------------------------------------------ death
# Stagger, drive both blades point-down into the ground either side, sink to
# one knee between them and let go, head bowed. Holds from 1.6 s. The planted
# tips go below the ground line; pack.py clips every pixel under the feet
# anchor, so they read as driven in.
PLANT_L = (0.62, 0.06, 1.60)       # the far blade's grip, from the ground origin: tip ~0.2 in
PLANT_R = (-0.44, -0.16, 1.42)
PLANT_L_DIR = (0.18, 0.02, -0.98)
PLANT_R_DIR = (-0.15, -0.02, -0.99)


def kneel_ops(k=1.0):
    return [
        ("move", "センター", (0, 0, -A_DROP - 0.52 * k)),
        ("movew", "足ＩＫ.L", (A_FRONT, A_FRONT_Y, 0)),
        ("movew", "足ＩＫ.R", (-A_BACK - 0.10 * k, A_BACK_Y, 0.02 * k)),
        ("rotw", "上半身", Y, A_LEAN + 14 * k),
        ("rotw", "上半身", Z, A_TWIST),
        ("rotw", "首", Z, 34 * 0.4),
        ("rotw", "頭", Z, 34 * 0.6 - 6 * k),
        ("rot", "頭", X, 4 + 30 * k),
        ("rotw", "頭", Y, -2),
    ]


def planted(hand):
    return {"L": blade(PLANT_L, PLANT_L_DIR, (0.8, 0.3, -0.4), anchor="ground", hand=hand),
            "R": blade(PLANT_R, PLANT_R_DIR, (-0.8, 0.3, -0.4), anchor="ground", hand=hand)}


def death_stab():
    return pose(stance(drop=A_DROP + 0.10, lean=A_LEAN + 6, head_nod=14) + cloth(4),
                {"困る": 0.7, "まばたき": 0.6, "あ": 0.3}, blades=planted(True))


def death_swing():
    """Between the guard and the stab: both blades swept out and down to his
    sides, so the turn from points-up to points-down never tangles in front of him."""
    return pose(stance(drop=A_DROP + 0.06, lean=A_LEAN + 2, head_nod=10) + cloth(-2),
                {"困る": 0.6, "まばたき": 0.7, "あ": 0.3},
                blades={"L": blade((0.36, -0.10, -0.06), (0.72, -0.04, -0.69), (0.8, 0.3, -0.6)),
                        "R": blade((-0.30, -0.12, -0.06), (-0.72, -0.04, -0.69), (-0.8, 0.3, -0.6))})


def death_kneel(k=1.0, swing=0.0):
    ops = kneel_ops(k) + [
        ("hand", "R", "ひざ.R", (0.02, -0.05, 0.10), (-0.6, 0.2, -0.6)),
        ("curl", "R", 30, 10),
        ("hand", "L", "ひざ.L", (-0.02, -0.04, 0.12), (0.6, 0.3, -0.6)),
        ("curl", "L", 30, 10),
    ] + cloth(swing)
    return pose(ops, {"困る": 0.7, "まばたき": 1.0}, blades=planted(False))


DEATH = {
    "length": 2.2, "fps": 15, "loop": False, "motion_end": 1.6,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.14, guard(1.0), "out"),
        (0.30, death_swing(), "io"),
        (0.45, death_stab(), "in"),
        (0.62, death_stab(), "io"),
        (1.15, death_kneel(1.0, swing=3), "in"),
        (1.35, death_kneel(0.96, swing=-2), "out"),
        (1.6, death_kneel(1.0), "io"),
    ],
}

# ------------------------------------------------------------------ ascension
# Four Winds' Ascension: a crouch, a leap with both blades raised overhead,
# and a crash down that drives both into the ground before him (the impact);
# then he rises back into stance A. He leaps straight up, so he lands where he
# stood and the return to idle never slides.


def asc(blades, root_z=0.0, drop=A_DROP, lean=A_LEAN, twist=A_TWIST, tuck=0.0, flare=0.0, head_nod=4.0,
        morphs=None):
    ops = [
        ("move", "センター", (0, 0, -drop)),
        ("movew", "足ＩＫ.L", (A_FRONT - 0.06 * tuck, A_FRONT_Y, 0.22 * tuck)),
        ("movew", "足ＩＫ.R", (-A_BACK + 0.06 * tuck, A_BACK_Y, 0.30 * tuck)),
        ("rotw", "上半身", Y, lean),
        ("rotw", "上半身", Z, twist),
        ("rotw", "首", Z, 34 * 0.4),
        ("rotw", "頭", Z, 34 * 0.6),
        ("rot", "頭", X, head_nod),
        ("rotw", "頭", Y, -2),
    ] + cloth(0.0, flare)
    return pose(ops, morphs or {"怒り": 0.7, "あ": 0.5}, blades=blades, root=(0, 0, root_z))


OVERHEAD = {"L": blade((0.10, 0.00, 0.50), (-0.30, 0.08, 0.95), (0.8, 0.3, 0.2), roll=10),
            "R": blade((-0.02, -0.06, 0.48), (-0.55, 0.02, 0.83), (-0.8, 0.3, 0.2), roll=-10)}
SLAMMED = {"L": blade((0.52, -0.02, -0.46), (0.89, -0.06, -0.45), (0.3, 0.5, -1.0), roll=LEAD_ROLL),
           "R": blade((0.40, -0.22, -0.48), (0.85, -0.12, -0.51), (-0.3, 0.3, -1.0), roll=REAR_ROLL)}
CROUCH = {"L": blade((0.24, -0.02, -0.50), (0.90, -0.06, -0.42), LEAD_POLE, roll=LEAD_ROLL),
          "R": blade((0.04, -0.26, -0.34), (-0.20, 0.30, 0.93), SHOULDER_POLE, roll=REAR_ROLL)}

ASCENSION = {
    "length": 1.3, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.18, asc(CROUCH, drop=A_DROP + 0.12, lean=A_LEAN + 10, head_nod=0), "io"),
        (0.42, asc(OVERHEAD, root_z=0.55, drop=A_DROP - 0.04, lean=-6, tuck=1.0, flare=-6, head_nod=-6), "out"),
        (0.50, asc(OVERHEAD, root_z=0.58, drop=A_DROP - 0.04, lean=-4, tuck=1.0, flare=-8, head_nod=-6), "io"),
        (0.64, asc(SLAMMED, root_z=0.0, drop=A_DROP + 0.22, lean=A_LEAN + 20, flare=8, head_nod=10,
                   morphs={"怒り": 0.9, "あ": 0.8}), "in"),
        (0.82, asc(SLAMMED, drop=A_DROP + 0.20, lean=A_LEAN + 18, flare=3, head_nod=8), "out"),
        (1.3, idle_pose(0.5), "io"),
    ],
    "events": {"impact": [0.64], "main": 0.64},
    "trails": [{"blade": "L", "from": 0.48, "to": 0.66}, {"blade": "R", "from": 0.48, "to": 0.66}],
    "bursts": [{"t": 0.64, "blade": "both", "kind": "ground", "scale": 1.3}],
}

# ------------------------------------------------------------------ stance B
# Where he is not fighting (the shop, character select): upright and regal,
# both claymores planted point-down, one either side, his hands resting on the
# hilts. Each claymore is nearly his height, so a hand at chest height puts
# the tip a little into the ground (pack.py cuts it at the ground line).
B_L = (0.42, -0.10, 1.56)        # grips at his chest; the tips ~0.3 and ~0.1 into the ground
B_R = (-0.32, -0.18, 1.45)


def regal(breath=0.0, swing=0.0, head_turn=30.0):
    b = breath
    return pose(
        [("move", "センター", (0, 0, -0.02 - 0.006 * (1 - b))),
         ("movew", "足ＩＫ.L", (0.12, 0.02, 0)),
         ("movew", "足ＩＫ.R", (-0.10, -0.02, 0)),
         ("rotw", "上半身", Y, 1.0 + 1.2 * (1 - b)),
         ("rotw", "上半身", Z, -16),
         ("rotw", "首", Z, head_turn * 0.4),
         ("rotw", "頭", Z, head_turn * 0.6),
         ("rot", "頭", X, -2 + 1.5 * (1 - b)),
         ("rotw", "頭", Y, -2)]
        + cloth(swing),
        {"真面目": 0.4, "にこり": 0.25},
        blades={"L": blade(add(B_L, (0, 0, -0.004 * (1 - b))), (0.06, 0.02, -1.0), (0.8, 0.4, -0.4),
                           anchor="ground", curl=(70, 30)),
                "R": blade(add(B_R, (0, 0, -0.004 * (1 - b))), (-0.06, -0.02, -1.0), (-0.8, 0.2, -0.4),
                           anchor="ground", curl=(70, 30))})


MERCHANT = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, regal(0.0, swing=-1.0), "io"),
        (1.5, regal(1.0, swing=1.0), "io"),
        (3.0, regal(0.0, swing=-1.0), "io"),
    ],
}

# ------------------------------------------------------------------ rest site
# Sitting upright on the ground facing the fire (design review, 2026-10-13:
# the first take reclined and read as lying down): the near knee up with his
# forearm on it, the far leg folded flat; both claymores planted upright
# behind him, point-down, leaning a little apart. The planted tips go under the
# ground line and are cut there, as the death clip's.
REST = pose(
    [("move", "センター", (0, 0, -1.04)),
     ("movew", "足ＩＫ.L", (0.62, 0.16, 0.0)),
     ("movew", "足ＩＫ.R", (0.52, -0.22, 0.0)),
     ("rotw", "上半身", Y, 6),
     ("rotw", "上半身", Z, -14),
     ("rotw", "首", Z, 8),
     ("rotw", "頭", Z, 12),
     ("rot", "頭", X, 4),
     ("hand", "R", "ひざ.R", (0.04, -0.06, 0.04), (-0.5, -0.2, -1)),
     ("curl", "R", 35, 12),
     ("hand", "L", "ひざ.L", (0.04, -0.02, 0.10), (0.6, 0.3, -1)),
     ("curl", "L", 35, 12)]
    + cloth(0.0, flare=20.0),
    {"にこり": 0.35, "真面目": 0.2}, yaw=40,
    blades={"L": blade((-0.40, 0.34, 1.52), (0.10, 0.04, -0.99), (0, 0, -1), anchor="ground", hand=False),
            "R": blade((-0.52, 0.10, 1.30), (-0.14, -0.02, -0.99), (0, 0, -1), anchor="ground", hand=False)})

# ------------------------------------------------------------------ character select
# A waist-up close-up of stance B, his face turned further toward the viewer.
SELECT = regal(1.0, head_turn=16.0)
SELECT["morphs"] = {"真面目": 0.3, "にこり": 0.45}

# ------------------------------------------------------------------ roster tile
# Head and shoulders, the face three-quarters toward the viewer; no blades.
PORTRAIT = pose(
    stance(drop=0.0, lean=0.0, twist=-18, head_turn=20, head_nod=-3, head_tilt=-2, front=0.10, back=0.08)
    + [("hand", "R", "足.R", (-0.10, -0.06, -0.10), (-1.0, 0.5, 0.0)),
       ("hand", "L", "足.L", (0.10, -0.04, -0.10), (1.0, 0.5, 0.0))],
    {"にこり": 0.5, "真面目": 0.2})

# ------------------------------------------------------------------ scale reference
# Upright, arms at his sides, no blades: the still pack.py measures his
# on-screen height on, so the crouched battle stance never reads as a shorter
# Varka.
STAND = pose(
    stance(drop=0.0, lean=0.0, twist=-14, head_turn=34, head_nod=2, head_tilt=0.0, front=0.12, back=0.10)
    + [("hand", "R", "足.R", (-0.12, -0.04, -0.30), (-1.0, 0.5, 0.0)),
       ("hand", "L", "足.L", (0.12, -0.02, -0.30), (1.0, 0.5, 0.0))],
    dict(STERN))

CLIPS = {
    "idle": IDLE,
    "idle_low": IDLE_LOW,
    "attack": ATTACK,
    "cast": CAST,
    "hurt": HURT,
    "death": DEATH,
    "ascension": ASCENSION,
    "merchant": MERCHANT,
}
#: the clips that start and end in stance A (feet where idle plants them)
FROM_IDLE = ("attack", "cast", "hurt", "ascension")

STILLS = {"stance_a": IDLE["keys"][0][1], "stand": STAND, "rest": REST, "select": SELECT,
          "portrait": PORTRAIT, "stance_b": MERCHANT["keys"][0][1]}
