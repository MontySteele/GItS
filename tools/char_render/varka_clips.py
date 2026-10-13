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
the impact flashes (fx.py draws both, colourless). Every combat clip starts and
ends with his feet where stance A plants them, so blends in and out of idle never
slide them; a spin turns him on the spot (`turned`), and his two blades always
move as one pair (`pair`).

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
# A tight, ready battle stance ([USER], 2026-10-13: the first takes were "a
# little lame ... floppy"): knees bent, weight forward, both claymores held in
# a low guard, angled down and back at his sides, tips off the ground. The two
# blades mirror each other about his body (the far one behind his legs, the
# near one before them), so on screen they read as a parallel pair. Only the
# chest breathes; the blades stay fixed in his hands.
A_DROP = 0.13            # hips lowered: knees bent
A_LEAN = 12.0            # upper body toward the enemy (weight forward)
A_FRONT = 0.34           # far foot toward the enemy
A_BACK = 0.31            # near foot back
A_FRONT_Y, A_BACK_Y = 0.03, -0.04
A_TWIST = -14.0
STERN = {"真面目": 0.55, "にやり": 0.15}
#: the low guard, both hands at his hips, both blades down and back
GUARD_L_AT = (-0.10, 0.10, -0.42)
GUARD_R_AT = (-0.04, -0.22, -0.46)
GUARD_DIR = (-0.62, 0.52, -0.40)       # the far blade's; the near blade mirrors it in Y
GUARD_POLE = (-0.4, 0.7, -0.5)
LEAD_ROLL, REAR_ROLL = 20.0, -20.0


def unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def mirror(v):
    """The near hand's twin of a far-hand vector: the same, reflected in Y."""
    return (v[0], -v[1], v[2])


def pair(at_l, d_l, pole=GUARD_POLE, at_r=None, roll=LEAD_ROLL, d_r=None, pole_r=None):
    """Both blades IN SYNC: by default the near (R) blade mirrors the far (L)
    one about his body (direction and pole reflected in Y), so on screen they
    run parallel and move as one; `d_r` gives a crossed pair instead (an X)."""
    at_r = at_r if at_r is not None else mirror(at_l)
    d_r = d_r if d_r is not None else mirror(d_l)
    pole_r = pole_r if pole_r is not None else mirror(pole)
    return {"L": blade(at_l, unit(d_l), unit(pole), roll=roll),
            "R": blade(at_r, unit(d_r), unit(pole_r), roll=-roll)}


def stance(drop=A_DROP, lean=A_LEAN, twist=A_TWIST, head_turn=34.0, head_nod=4.0, head_tilt=-2.0,
           front=A_FRONT, back=A_BACK, sway=0.0, lift=0.0, tuck=0.0):
    """Feet planted wide (far foot toward the enemy), chest toward the viewer,
    head to the right. `lift` raises both feet (a hop), `tuck` draws them in
    under him."""
    return [
        ("move", "センター", (sway, 0, -drop)),
        ("movew", "足ＩＫ.L", (front * (1 - 0.6 * tuck), A_FRONT_Y, lift + 0.20 * tuck)),
        ("movew", "足ＩＫ.R", (-back * (1 - 0.6 * tuck), A_BACK_Y, lift + 0.26 * tuck)),
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


def rot_z(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (c * v[0] - s * v[1], s * v[0] + c * v[1], v[2])


def turned(p, deg):
    """Pose p turned rigidly `deg` degrees about the vertical through his
    feet (a spin): the root's yaw turns, and every WORLD vector of the pose
    (world-axis rotations, foot moves, hand offsets, every blade's grip
    offset, direction and elbow pole) turns with it. Bone-local ops
    ("rot", "move") ride along with the root. A whole turn changes the yaw
    only: the same picture."""
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
    q["blades"] = {s: {**b, "at": rot_z(b["at"], deg), "dir": rot_z(b["dir"], deg), "pole": rot_z(b["pole"], deg)}
                   for s, b in p["blades"].items()}
    q["root"] = rot_z(p["root"], deg)
    return q


def idle_pose(breath=0.0, swing=0.0, blink=0.0):
    """breath 0..1: the in-breath raises the chest a hair; the blades ride
    with the hands, fixed in the grip."""
    b = breath
    m = dict(STERN)
    if blink:
        m["まばたき"] = blink
    lift = (0, 0, 0.008 * b)
    return pose(
        stance(drop=A_DROP + 0.010 * (1 - b), lean=A_LEAN + 1.5 * (1 - b), head_nod=4.0 + 1.5 * (1 - b))
        + cloth(swing),
        m,
        blades=pair(add(GUARD_L_AT, lift), GUARD_DIR, at_r=add(GUARD_R_AT, lift)))


IDLE = {
    "length": 2.8, "fps": 12, "loop": True,
    "keys": [
        (0.0, idle_pose(0.0, swing=-1.0), "io"),
        (1.4, idle_pose(1.0, swing=1.0), "io"),
        (1.75, idle_pose(0.8, swing=0.8), "io"),
        (1.82, idle_pose(0.77, swing=0.7, blink=1.0), "io"),
        (1.9, idle_pose(0.74, swing=0.6), "io"),
        (2.8, idle_pose(0.0, swing=-1.0), "io"),
    ],
}

# ------------------------------------------------------------------ low HP
# The same guard, worn down: shoulders and head low, both tips lowered
# together toward the ground before his feet (still clear of it).


def low_pose(breath=0.0, swing=0.0):
    b = breath
    return pose(
        stance(drop=A_DROP + 0.03 + 0.008 * (1 - b), lean=A_LEAN + 8 + 2 * (1 - b), head_turn=28,
               head_nod=16 + 2 * (1 - b))
        + cloth(swing),
        {"困る": 0.6, "真面目": 0.3, "あ": 0.2},
        blades=pair(add(GUARD_L_AT, (0.04, 0, -0.06 - 0.006 * (1 - b))), (-0.50, 0.58, -0.46),
                    at_r=add(GUARD_R_AT, (0.04, 0, -0.06 - 0.006 * (1 - b)))))


IDLE_LOW = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, low_pose(0.0, swing=-1.0), "io"),
        (1.5, low_pose(1.0, swing=1.0), "io"),
        (3.0, low_pose(0.0, swing=-1.0), "io"),
    ],
}

# ------------------------------------------------------------------ attack
# One compact spin, then a double cleave ([USER], 2026-10-13: "Varka's a highly
# acrobatic character who tends to do spins and attack with both claymores in
# sync at the same time"). Both blades move together throughout, rigid in his
# grip, and every move is a short, hard snap between held key poses:
#   wind-up    a crouch, both blades drawn back at his hips (frame 2)
#   the spin   a full turn on the spot with a small hop, both blades held out
#              behind him at waist height, so they sweep a flat ring; the
#              first impact is where they pass the enemy's side (frame 6)
#   the cleave both blades come up over his head together and down in front
#              of him in a parallel V at the enemy: the main impact (frame 11)
#   back to the low guard.


def atk(blades, lean=A_LEAN, twist=A_TWIST, drop=A_DROP, head_turn=34.0, swing=0.0, lift=0.0, tuck=0.0,
        morphs=None, turn=0.0, hop=0.0):
    p = pose(stance(drop=drop, lean=lean, twist=twist, head_turn=head_turn, lift=lift, tuck=tuck) + cloth(swing),
             morphs or {"怒り": 0.5, "真面目": 0.4}, blades=blades, root=(0, 0, hop))
    return turned(p, turn)


#: the spin: both blades held out behind him at waist height, tips a little
#: low, so the ring they sweep is a shallow cone that reads from the side
SPIN_DIR = (-0.92, 0.12, -0.32)
SPIN = pair((-0.26, 0.10, -0.34), SPIN_DIR, pole=(-0.3, 0.8, -0.4), at_r=(-0.24, -0.18, -0.44))
#: the wind-up: the same blade line, the hands drawn further back and low
WIND = pair((-0.30, 0.10, -0.44), SPIN_DIR, pole=(-0.3, 0.8, -0.5), at_r=(-0.28, -0.18, -0.52))
#: over the top: both blades up and a little back over his head
OVER = pair((-0.02, 0.10, 0.40), (-0.40, 0.10, 0.91), pole=(0.2, 0.8, 0.2), at_r=(-0.06, -0.14, 0.34),
            d_r=(-0.16, -0.10, 0.98))
#: the cleave: both down in front of him at the enemy, a parallel V
CLEAVE = pair((0.40, 0.08, -0.18), (0.92, 0.14, -0.34), pole=(0.2, 0.8, -0.6), at_r=(0.38, -0.14, -0.30),
              d_r=(0.80, -0.14, -0.58))
SETTLE = pair((0.38, 0.08, -0.23), (0.90, 0.14, -0.40), pole=(0.2, 0.8, -0.6), at_r=(0.36, -0.14, -0.35),
              d_r=(0.78, -0.14, -0.62))
#: on the way back to the guard: both blades swung out to his sides, low, so
#: the turn from forward to back never drags a tip through the ground
SIDE = pair((0.04, 0.16, -0.34), (0.0, 0.95, -0.28), pole=(-0.2, 0.9, -0.4), at_r=(0.04, -0.24, -0.38))

ATK_SPIN = dict(lean=A_LEAN + 4, drop=A_DROP + 0.02, swing=6, lift=0.02, tuck=0.25, hop=0.10,
                morphs={"怒り": 0.6, "真面目": 0.3})

ATTACK = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.10, atk(WIND, lean=A_LEAN + 14, twist=-6, drop=A_DROP + 0.12, head_turn=38, swing=-3), "out"),
        (0.18, atk(SPIN, turn=60, **ATK_SPIN), "in"),
        (0.30, atk(SPIN, turn=180, **ATK_SPIN), "lin"),
        (0.40, atk(SPIN, turn=300, **ATK_SPIN), "lin"),
        (0.45, atk(SPIN, turn=360, lean=A_LEAN + 4, drop=A_DROP + 0.06, swing=3, morphs={"怒り": 0.6}), "out"),
        (0.50, atk(OVER, turn=360, lean=-6, drop=A_DROP - 0.04, head_turn=38, swing=-2,
                   morphs={"怒り": 0.6, "あ": 0.3}), "out"),
        (0.55, atk(CLEAVE, turn=360, lean=A_LEAN + 22, twist=-18, drop=A_DROP + 0.10, head_turn=30, swing=5,
                   morphs={"怒り": 0.8, "あ": 0.6}), "in"),
        (0.62, atk(SETTLE, turn=360, lean=A_LEAN + 20, twist=-18, drop=A_DROP + 0.11, head_turn=30, swing=2,
                   morphs={"怒り": 0.7, "あ": 0.3}), "out"),
        (0.76, atk(SIDE, turn=360, lean=A_LEAN + 6, drop=A_DROP + 0.04, swing=-2), "io"),
        (0.88, turned(idle_pose(0.5), 360), "out"),
        (1.0, turned(idle_pose(0.5), 360), "io"),
    ],
    # the impacts the game should time its hit to; "main" is the second
    "events": {"impact": [0.30, 0.55], "main": 0.55},
    # the spin's two trails sweep a flat ring; the cleave's two run parallel
    "trails": [{"blade": "L", "from": 0.18, "to": 0.42}, {"blade": "R", "from": 0.18, "to": 0.42},
               {"blade": "L", "from": 0.47, "to": 0.57}, {"blade": "R", "from": 0.47, "to": 0.57}],
    "bursts": [{"t": 0.30, "blade": "both", "kind": "slash", "scale": 0.8},
               {"t": 0.55, "blade": "both", "kind": "slash", "scale": 1.0}],
}

# ------------------------------------------------------------------ cast
# Both blades raised and crossed before him: a knightly salute. They rise
# together, up past his sides (never one after the other), then cross.


def salute(k=1.0):
    return pose(
        stance(drop=A_DROP - 0.02 * k, lean=A_LEAN - 8 * k, twist=A_TWIST - 4 * k, head_turn=34 - 6 * k,
               head_nod=4 - 4 * k)
        + cloth(-1.5 * k),
        {"真面目": 0.9},
        blades=pair((0.20, -0.30, -0.02), (-0.36, -0.06, 0.93), pole=(0.8, 0.2, -0.6), at_r=(0.02, -0.34, -0.02),
                    d_r=(0.42, -0.06, 0.90), pole_r=(-0.8, 0.2, -0.6)))


def raised():
    """Halfway up: both blades up beside him, parallel."""
    return pose(stance(drop=A_DROP, lean=A_LEAN - 4, head_turn=32) + cloth(-1),
                {"真面目": 0.8},
                blades=pair((0.02, 0.16, -0.12), (-0.10, 0.40, 0.91), pole=(-0.6, 0.6, -0.5),
                            at_r=(0.0, -0.28, -0.12)))


CAST = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.14, raised(), "out"),
        (0.26, salute(1.0), "out"),
        (0.70, salute(1.0), "io"),
        (0.82, raised(), "io"),
        (1.0, idle_pose(0.5), "out"),
    ],
}

# ------------------------------------------------------------------ hurt
# A flinch: his body snaps back, the guard held firm, both blades lifted
# together a little in his fixed grip.


def flinch(k=1.0):
    return pose(
        stance(drop=A_DROP + 0.03 * k, lean=A_LEAN - 18 * k, twist=A_TWIST - 6 * k, head_turn=30 - 8 * k,
               head_nod=4 + 8 * k, head_tilt=-2 - 6 * k)
        + cloth(-5 * k),
        {"まばたき": 0.8 * k, "怒り": 0.6, "あ": 0.3 * k},
        blades=pair(add(GUARD_L_AT, (-0.04 * k, 0, 0.06 * k)), (-0.66, 0.54, -0.30 + 0.05 * (1 - k)),
                    at_r=add(GUARD_R_AT, (-0.04 * k, 0, 0.06 * k))))


def guard(k=1.0):
    """The crossed guard (the death clip's first beat): both blades up and
    crossed before him."""
    return pose(
        stance(drop=A_DROP + 0.03 * k, lean=A_LEAN - 20 * k, twist=A_TWIST - 6 * k, head_turn=30 - 8 * k,
               head_nod=4 + 8 * k, head_tilt=-2 - 6 * k)
        + cloth(-5 * k),
        {"まばたき": 0.8 * k, "怒り": 0.6, "あ": 0.3 * k},
        blades=pair((0.22, -0.28, -0.20), (-0.45, -0.06, 0.89), pole=(0.8, 0.2, -0.6), at_r=(0.02, -0.32, -0.18),
                    d_r=(0.50, -0.06, 0.86), pole_r=(-0.8, 0.2, -0.6)))


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
# Four Winds' Ascension, the signature: a crouch, a leaping spin (one full
# turn in the air, about a third of his height up) with both blades raised
# overhead together, and a crash down into a synced double strike before him
# (the impact); then a snap back to the low guard. He leaps straight up, so he
# lands where he stood and the return to idle never slides.


def asc(blades, hop=0.0, drop=A_DROP, lean=A_LEAN, twist=A_TWIST, tuck=0.0, flare=0.0, head_nod=4.0,
        morphs=None, turn=0.0, swing=0.0):
    p = pose(stance(drop=drop, lean=lean, twist=twist, head_nod=head_nod, tuck=tuck) + cloth(swing, flare),
             morphs or {"怒り": 0.7, "あ": 0.5}, blades=blades, root=(0, 0, hop))
    return turned(p, turn)


#: overhead: both blades straight up together, hands high, held rigid through the turn
OVERHEAD = pair((0.06, 0.10, 0.46), (-0.10, 0.22, 0.97), pole=(-0.4, 0.8, 0.0), at_r=(-0.04, -0.14, 0.44))
#: wound back over his head for the crash
WOUND = pair((-0.02, 0.10, 0.42), (-0.42, 0.10, 0.90), pole=(0.2, 0.8, 0.2), at_r=(-0.06, -0.14, 0.36))
#: slammed: both down before him at the enemy, a parallel V, tips just clear
SLAMMED = pair((0.44, 0.08, -0.24), (0.90, 0.14, -0.38), pole=(0.2, 0.8, -0.6), at_r=(0.42, -0.14, -0.36),
               d_r=(0.78, -0.14, -0.60))
CROUCH = pair((-0.22, 0.10, -0.48), (-0.80, 0.34, -0.46), pole=(-0.3, 0.8, -0.5), at_r=(-0.18, -0.20, -0.54))
LEAP = dict(drop=A_DROP - 0.04, lean=-2, tuck=1.0, flare=-6, head_nod=-4, swing=4)

ASCENSION = {
    "length": 1.3, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        (0.16, asc(CROUCH, drop=A_DROP + 0.16, lean=A_LEAN + 12, head_nod=0, swing=-3), "out"),
        (0.24, asc(OVERHEAD, hop=0.30, **LEAP), "out"),
        (0.32, asc(OVERHEAD, hop=0.60, turn=120, **LEAP), "lin"),
        (0.40, asc(OVERHEAD, hop=0.66, turn=240, **LEAP), "lin"),
        (0.48, asc(OVERHEAD, hop=0.56, turn=360, **LEAP), "lin"),
        (0.54, asc(WOUND, hop=0.36, turn=360, drop=A_DROP - 0.04, lean=-8, tuck=0.6, flare=-4, head_nod=-6), "out"),
        (0.60, asc(SLAMMED, turn=360, drop=A_DROP + 0.24, lean=A_LEAN + 22, flare=8, head_nod=10, swing=5,
                   morphs={"怒り": 0.9, "あ": 0.8}), "in"),
        (0.74, asc(SLAMMED, turn=360, drop=A_DROP + 0.22, lean=A_LEAN + 20, flare=3, head_nod=8, swing=2), "out"),
        (1.00, atk(SIDE, turn=360, lean=A_LEAN + 6, drop=A_DROP + 0.06, swing=-2), "io"),
        (1.14, turned(idle_pose(0.5), 360), "out"),
        (1.3, turned(idle_pose(0.5), 360), "io"),
    ],
    # on a frame (12 at 20 fps), so the main frame is the slam itself
    "events": {"impact": [0.60], "main": 0.60},
    "trails": [{"blade": "L", "from": 0.50, "to": 0.62}, {"blade": "R", "from": 0.50, "to": 0.62}],
    "bursts": [{"t": 0.60, "blade": "both", "kind": "ground", "scale": 1.3}],
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
     ("rotw", "上半身", Y, 14),
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
