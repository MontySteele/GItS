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
                    blade's own grip from chars.py); on a free blade, the
                    point of it placed at `at` (stance B: the pommel's top)
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
those units, about 1.86x Klee's. His ruled height is 82 in (chars.py).

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
# One continuous spin-to-slam ([USER], round 3: "he half-twirls once, then
# instantly flips to slam them down ... make this smoother, with the twirl
# also raising the blades and the slam showing him spinning back, so it reads
# as one continuous animation rather than two halves"). From the wind-up, one
# turn on the spot carries both blades, rigid in his grip and in sync, up a
# rising helix: level behind him at the start, past the enemy's side a little
# raised (the light impact, frame 7), over his head as the last fifth of the
# turn begins, and on down in front of him as the turn brings him back round to
# face the enemy (the main impact, frame 12). The yaw and the blades' pitch are
# smooth curves of one parameter s, keyed every 0.025 s (half a frame), so
# there is no hold and no snap at the top: the turn eases in from the wind-up
# and eases out into the slam, and the blades keep accelerating over the top.
# The level spin and the overhead arc down in front follow his own string
# (scratch reference/NOTES.md: Talent Demo 2, Talent Demo 3, Character
# Details 3).


def atk(blades, lean=A_LEAN, twist=A_TWIST, drop=A_DROP, head_turn=34.0, swing=0.0, lift=0.0, tuck=0.0,
        morphs=None, turn=0.0, hop=0.0):
    p = pose(stance(drop=drop, lean=lean, twist=twist, head_turn=head_turn, lift=lift, tuck=tuck) + cloth(swing),
             morphs or {"怒り": 0.5, "真面目": 0.4}, blades=blades, root=(0, 0, hop))
    return turned(p, turn)


def hermite(x, knots):
    """A C1 curve through (x, y) knots (finite-difference slopes, flat at the
    ends): no velocity jump at any knot."""
    xs, ys = [k[0] for k in knots], [k[1] for k in knots]
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    i = max(j for j in range(len(xs) - 1) if xs[j] <= x)
    m = [0.0] + [(ys[j + 1] - ys[j - 1]) / (xs[j + 1] - xs[j - 1]) for j in range(1, len(xs) - 1)] + [0.0]
    h = xs[i + 1] - xs[i]
    u = (x - xs[i]) / h
    return ((2 * u ** 3 - 3 * u ** 2 + 1) * ys[i] + (u ** 3 - 2 * u ** 2 + u) * h * m[i]
            + (-2 * u ** 3 + 3 * u ** 2) * ys[i + 1] + (u ** 3 - u ** 2) * h * m[i + 1])


#: the spin-to-slam: s runs 0..1 from SPIN_T0 to SPIN_T1
SPIN_T0, SPIN_T1 = 0.10, 0.60
SPIN_STEP = 0.025
#: the blades' pitch in his body's frame, degrees: -18 is level behind him
#: (tips a little low), 90 straight up, 200 down in front at the enemy
PITCH_FROM, PITCH_TO, PITCH_POW = -18.0, 200.0, 2.5


def spin_turn(s):
    """The root's turn: one full turn, easing in from the wind-up and out into the slam."""
    return 360.0 * s * s * (3 - 2 * s)


def spin_pitch(s):
    """The blades' pitch: rising steadily through the turn and accelerating
    over the top into the slam (no hold at the top)."""
    return PITCH_FROM + (PITCH_TO - PITCH_FROM) * s ** PITCH_POW


def helix(a):
    """Both blades at pitch `a` (degrees, his body's frame at turn 0): the far
    blade's line runs over the top of him in his own vertical plane, the near
    blade mirrors it, and both hands ride an arc from behind his hips over his
    head to before his knees."""
    r = math.radians(a)
    c, f = math.cos(r), math.sin(r)
    x = 0.02 - 0.36 * c
    z = -0.06 + 0.609 * f - 0.129 * f * f
    k = (a - PITCH_FROM) / (PITCH_TO - PITCH_FROM)
    return pair((x, 0.10, z), (-c, 0.12, f), pole=(-0.3 + 0.5 * k, 0.8, -0.35 + 0.5 * f),
                at_r=(x + 0.02, -0.18, z - 0.08))


SPIN_BODY = {   # body curves over s (knots), C1 through the join
    "lean": [(0, A_LEAN + 12), (0.5, A_LEAN + 4), (0.76, A_LEAN - 12), (1.0, A_LEAN + 22)],
    "twist": [(0, -6.0), (0.4, A_TWIST), (0.76, A_TWIST), (1.0, -18.0)],
    "drop": [(0, A_DROP + 0.12), (0.3, A_DROP + 0.03), (0.76, A_DROP - 0.03), (1.0, A_DROP + 0.10)],
    "hop": [(0, 0.0), (0.2, 0.0), (0.5, 0.10), (0.8, 0.04), (1.0, 0.0)],
    "tuck": [(0, 0.0), (0.2, 0.25), (0.8, 0.20), (1.0, 0.0)],
    "lift": [(0, 0.0), (0.2, 0.02), (0.8, 0.02), (1.0, 0.0)],
    "head_turn": [(0, 38.0), (0.5, 34.0), (0.76, 38.0), (1.0, 30.0)],
    "swing": [(0, -3.0), (0.4, 6.0), (0.76, -2.0), (1.0, 5.0)],
}


def spin_pose(s):
    b = {k: hermite(s, v) for k, v in SPIN_BODY.items()}
    b["hop"] = min(0.10, max(0.0, b["hop"]))
    morphs = {"怒り": 0.6 + 0.2 * s, "真面目": 0.3 * (1 - s), "あ": 0.6 * s ** 2}
    return atk(helix(spin_pitch(s)), morphs=morphs, turn=spin_turn(s), **b)


_n = int(round((SPIN_T1 - SPIN_T0) / SPIN_STEP))
SPIN_KEYS = [(round(SPIN_T0 + SPIN_STEP * i, 6), spin_pose(i / _n), "lin") for i in range(_n + 1)]

#: after the slam: the blades sink a hair further (the settle), then swing out
#: to his sides, low, so the turn from forward to back never drags a tip
#: through the ground, and he is back in the guard
SETTLE = helix(PITCH_TO + 5)
SIDE = pair((0.04, 0.16, -0.34), (0.0, 0.95, -0.28), pole=(-0.2, 0.9, -0.4), at_r=(0.04, -0.24, -0.38))

ATTACK = {
    "length": 1.05, "fps": 20, "loop": False,
    "keys": [(0.0, idle_pose(0.5), "io")]
    + [(SPIN_KEYS[0][0], SPIN_KEYS[0][1], "io")] + SPIN_KEYS[1:]
    + [
        (0.68, atk(SETTLE, turn=360, lean=A_LEAN + 20, twist=-18, drop=A_DROP + 0.12, head_turn=30, swing=2,
                   morphs={"怒り": 0.7, "あ": 0.3}), "out"),
        (0.80, atk(SIDE, turn=360, lean=A_LEAN + 6, drop=A_DROP + 0.04, swing=-2), "io"),
        (0.92, turned(idle_pose(0.5), 360), "out"),
        (1.05, turned(idle_pose(0.5), 360), "io"),
    ],
    # the light impact as the rising blades pass the enemy's side (half the
    # turn), the main one at the slam
    "events": {"impact": [0.35, 0.60], "main": 0.60},
    # one ribbon per blade, spiralling up through the turn and down into the slam
    "trails": [{"blade": "L", "from": 0.12, "to": 0.62, "age": 0.22},
               {"blade": "R", "from": 0.12, "to": 0.62, "age": 0.22}],
    "bursts": [{"t": 0.35, "blade": "both", "kind": "slash", "scale": 0.7},
               {"t": 0.60, "blade": "both", "kind": "slash", "scale": 1.0}],
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
# Four Winds' Ascension ([USER], round 3: "let's drop the twirl and instead
# show him jumping up and then driving one blade into the ground, with a
# mirrored ground particle effect on him and the target enemy"). As his own
# Special E does it (scratch reference/NOTES.md, Character Details 3, left):
# a crouch; a jump straight up, the lead (far, left-hand) blade swung up over
# his head and the near blade held back and out for balance, knees tucked;
# then down, the lead blade chopping over the top and on until it is driven
# point-first, near vertical, into the ground in front of him (toward the
# enemy) as he lands: the impact. A hard landing settle, low beside the
# planted blade, the other blade still back. Then he pulls it out and is back
# in the guard. No turn: he lands where he stood. The ground burst is its own
# sprite clip (fx.ground_burst), placed by the game twice from the impact
# frame: at the blade's point, and mirrored under the target.


def asc(blades, hop=0.0, drop=A_DROP, lean=A_LEAN, twist=A_TWIST, tuck=0.0, flare=0.0, head_nod=4.0,
        morphs=None, swing=0.0, head_turn=34.0):
    return pose(stance(drop=drop, lean=lean, twist=twist, head_turn=head_turn, head_nod=head_nod, tuck=tuck)
                + cloth(swing, flare),
                morphs or {"怒り": 0.7, "あ": 0.5}, blades=blades, root=(0, 0, hop))


#: the driving blade is the lead (far, left-hand) one, 1.86 from grip to tip
DRIVE = "L"
#: where it stands at the impact, from the ground under his feet: the grip
#: at his raised hand, the blade near vertical, its point driven about a
#: fifth of its length into the ground in front of him (pack.py cuts what is
#: under the ground line), low enough that he can crouch beside it
DRIVE_AT = (0.62, 0.04, 1.42)
DRIVE_DIR = (0.28, 0.02, -0.96)
DRIVE_POLE = (0.3, 0.8, -0.6)
#: the balance blade: the near one, back and out behind him
BAL_AT, BAL_DIR, BAL_POLE = (-0.20, -0.30, -0.10), (-0.86, -0.42, 0.18), (-0.4, -0.8, -0.3)
BAL_LOW_AT, BAL_LOW_DIR = (-0.24, -0.30, -0.28), (-0.88, -0.40, -0.14)


def drive(at, d, pole=DRIVE_POLE, anchor=CH, bal_at=BAL_AT, bal_dir=BAL_DIR, roll=LEAD_ROLL):
    """The lead blade at `at`/`d`, the near blade held back for balance."""
    return {"L": blade(at, unit(d), unit(pole), anchor=anchor, roll=roll),
            "R": blade(bal_at, unit(bal_dir), unit(BAL_POLE), roll=-roll)}


CROUCH = pair((-0.22, 0.10, -0.48), (-0.80, 0.34, -0.46), pole=(-0.3, 0.8, -0.5), at_r=(-0.18, -0.20, -0.54))
LEAP = dict(lean=-2, tuck=1.0, flare=-6, head_nod=-4, swing=4)
#: the drive, after the impact: the blade stays where it went in
PLANTED = drive(DRIVE_AT, DRIVE_DIR, anchor="ground", bal_at=BAL_LOW_AT, bal_dir=BAL_LOW_DIR)

ASCENSION = {
    "length": 1.3, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        # the crouch: both blades low and back, weight down
        (0.14, asc(CROUCH, drop=A_DROP + 0.18, lean=A_LEAN + 12, head_nod=0, swing=-3), "io"),
        # take-off: the lead blade swings up behind him, the near one goes back
        (0.22, asc(drive((-0.06, 0.10, 0.30), (-0.55, 0.12, 0.83), pole=(0.2, 0.8, 0.0)),
                   hop=0.42, drop=A_DROP - 0.04, **LEAP), "out"),
        # the top (hips 0.80 up, 0.39 of his height): the lead blade over his head
        (0.32, asc(drive((0.04, 0.10, 0.48), (0.08, 0.10, 0.99), pole=(0.3, 0.8, 0.1)),
                   hop=0.80, drop=A_DROP - 0.04, **LEAP), "out"),
        # coming down, the blade over the top and forward
        (0.40, asc(drive((0.26, 0.08, 0.36), (0.80, 0.06, 0.59), pole=(0.3, 0.8, -0.2)),
                   hop=0.62, drop=A_DROP - 0.02, lean=A_LEAN + 4, tuck=0.7, flare=-3, head_nod=4), "in"),
        (0.46, asc(drive((0.44, 0.06, 0.28), (0.62, 0.04, -0.78)),
                   hop=0.24, drop=A_DROP + 0.04, lean=A_LEAN + 14, tuck=0.3, flare=2, head_nod=8), "in"),
        # the impact: he lands and the point goes in (frame 10)
        (0.50, asc(PLANTED, drop=A_DROP + 0.30, lean=A_LEAN + 22, flare=8, head_nod=10, swing=5,
                   morphs={"怒り": 0.9, "あ": 0.8}), "in"),
        # the hard landing: lower still beside the planted blade
        (0.58, asc(PLANTED, drop=A_DROP + 0.42, lean=A_LEAN + 26, flare=4, head_nod=12, swing=2,
                   morphs={"怒り": 0.8, "あ": 0.4}), "out"),
        (0.74, asc(PLANTED, drop=A_DROP + 0.34, lean=A_LEAN + 22, flare=2, head_nod=8), "io"),
        # he pulls it out ...
        (0.86, asc(drive(add(DRIVE_AT, (0, 0, 0.42)), DRIVE_DIR, anchor="ground"),
                   drop=A_DROP + 0.10, lean=A_LEAN + 10), "io"),
        (0.94, asc(drive((0.30, 0.08, 0.05), (0.80, 0.15, -0.58)), drop=A_DROP + 0.06, lean=A_LEAN + 8), "io"),
        # ... and both swing out low to his sides, back to the guard
        (1.04, atk(SIDE, lean=A_LEAN + 6, drop=A_DROP + 0.04, swing=-2), "io"),
        (1.16, idle_pose(0.5), "out"),
        (1.3, idle_pose(0.5), "io"),
    ],
    "events": {"impact": [0.50], "main": 0.50},
    # one ribbon, the lead blade's chop over the top and down into the ground
    "trails": [{"blade": DRIVE, "from": 0.30, "to": 0.52, "age": 0.18}],
    "bursts": [],
    # the ground burst (fx.ground_burst), its own sprite clip: the game places
    # it twice from the impact frame, at the blade's point and, mirrored,
    # under the target
    "effects": [{"name": "ground_burst", "t": 0.50, "blade": DRIVE, "mirror": True,
                 "places": ["blade_tip", "target"]}],
}

# ------------------------------------------------------------------ stance B
# Where he is not fighting (the shop, character select): upright and at ease,
# his arms crossed over his chest, both claymores planted point-down in the
# ground either side of him, standing on their own.
#: [USER], 2026-10-13: "I dont think the "hands over sword" thing is working
#: for Varka. Can we have him cross his arms instead, with his swords infront
#: of him? And let's have the facial expression be more of a slight smile or
#: smirk." The near (right) forearm crosses in front, its hand tucked under
#: the far upper arm; the far (left) forearm lies behind it, its hand closing
#: round the near elbow. render.py arms_crossed measures that no forearm or
#: gauntlet goes into the other arm or his chest.
#: Then, on the swords planted before his legs: "the swords are off-screen
#: (rendered too low and cropped - the hilts are blending into his pants /
#: torso)". So they flank him: one outside his near leg, one outside his far
#: leg, planted shallow, each crossguard at about his hip and its pommel at
#: about his lower ribs. arms_crossed also measures each hilt against his
#: silhouette on the canvas (a gap of background between them), and pack.py
#: frames the select close-up so both crossguards sit inside it.
B_L = (0.62, -0.02, 1.52)        # the pommels' tops, from the ground under him
B_R = (-0.62, -0.04, 1.52)
B_L_DIR = (0.03, 0.0, -1.0)      # guard to point: the points a hair apart
B_R_DIR = (-0.03, 0.0, -1.0)
POMMEL_TOP = {"L": 0.338, "R": 0.354}        # chars.CHARS["varka"]["blades"][side]["pommel"][1]
#: the wrists, from his upper chest's head, and where each elbow bends
CROSS_R = (0.10, -0.24, -0.05)
CROSS_L = (-0.08, -0.215, -0.09)
POLE_R = (-1.0, -0.2, -0.6)
POLE_L = (1.0, -0.2, -0.6)
#: each hand points across, tucked back under the other upper arm; the far
#: hand turned TUCK_TWIST_L about itself, so its thumb lies along the near
#: forearm instead of rising into the near upper arm
TUCK_R = (1.0, 0.6, 0.1)
TUCK_L = (-1.0, 0.6, 0.1)
TUCK_TWIST_L = -40.0
TUCK_CURL = (70, 30)
TUCK_CURL_L = (85, 60)     # the far hand closes round the near elbow, its thumb laid down
#: the slight smirk ([USER]'s reference: a closed mouth, one corner raised,
#: relaxed brows, a steady gaze)
SMIRK = {"にやり": 0.45, "真面目": 0.1, "なごみ": 0.12}


def crossed_arms():
    return [("hand", "R", CH, CROSS_R, POLE_R),
            ("aimw", "手首.R", TUCK_R),
            ("curl", "R", *TUCK_CURL),
            ("hand", "L", CH, CROSS_L, POLE_L),
            ("aimw", "手首.L", TUCK_L, TUCK_TWIST_L),
            ("curl", "L", *TUCK_CURL_L)]


def regal(breath=0.0, swing=0.0, head_turn=30.0):
    b = breath
    p = pose(
        [("move", "センター", (0, 0, -0.02 - 0.006 * (1 - b))),
         ("movew", "足ＩＫ.L", (0.12, 0.02, 0)),
         ("movew", "足ＩＫ.R", (-0.10, -0.02, 0)),
         ("rotw", "上半身", Y, 1.0 + 1.2 * (1 - b)),
         ("rotw", "上半身", Z, -16),
         ("rotw", "首", Z, head_turn * 0.4),
         ("rotw", "頭", Z, head_turn * 0.6),
         ("rot", "頭", X, -2 + 1.5 * (1 - b)),
         ("rotw", "頭", Y, -2)]
        + crossed_arms()
        + cloth(swing),
        dict(SMIRK),
        blades={"L": blade(B_L, unit(B_L_DIR), (0, 0, -1), anchor="ground", hand=False, grip=POMMEL_TOP["L"]),
                "R": blade(B_R, unit(B_R_DIR), (0, 0, -1), anchor="ground", hand=False, grip=POMMEL_TOP["R"])})
    p["arms_crossed"] = True
    return p


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

# ------------------------------------------------------------------ roster tile
# Head and shoulders, the face three-quarters toward the viewer; no blades.
PORTRAIT = pose(
    stance(drop=0.0, lean=0.0, twist=-18, head_turn=20, head_nod=-3, head_tilt=-2, front=0.10, back=0.08)
    + [("hand", "R", "足.R", (-0.10, -0.06, -0.10), (-1.0, 0.5, 0.0)),
       ("hand", "L", "足.L", (0.10, -0.04, -0.10), (1.0, 0.5, 0.0))],
    dict(SMIRK))

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
