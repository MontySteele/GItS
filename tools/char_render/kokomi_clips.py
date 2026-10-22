"""Kokomi's poses and clips, in WORLD terms, for tools/char_render/render.py.

Pure data plus a few builders; no bpy, so it imports anywhere. The pose
language is tools/klee_render/clips.py's (+X screen right, toward the enemy;
-Y toward the viewer; +Z up; the root yaw turns her front toward screen right,
so her right side, .R, is nearest the camera and her left arm, .L, is the far
arm, the one toward the enemy).

PHASE A (2026-10-14): the surfaces every kit needs -- combat idle, low-HP
idle, attack, cast, hurt, death (the router's seven states need it), the shop
loop, the rest seat, the select close-up, the roster tile and the ground
shadow. Her signature clip, `ascension` (Nereid's Ascension), came with the
art polish (2026-10-21). The look is Klee's, Varka's and Furina's (style H1 + H3 lite, on the
left of the field facing right, a little tilted).

Her official pack carries no catalyst (scratch models/kokomi/unpacked: the
body PMX alone), so she fights with an open hand: the far hand held palm up
before her where her catalyst would float. Her attack is a push of water from
that hand, and the water is a PHANTOM as Furina's rapier is: render.py records
a line from her far hand's knuckles along the hand (`PHANTOM`), and fx.py
draws the jet (the "thrust" streak) and a short sweep from it, in the neutral
heat layer the game tints Hydro.

THE BODY (probed on the PMX 2026-10-14, raw units x 0.08): the same 观海 bone
set and the same proportions as Furina's (chest 上半身2 1.106 up, neck 1.276,
head 1.352, shoulder 1.252, wrist 0.414 out at rest), so Furina's hand offsets
read the same on her. Rest height 1.6261 units (no hat; Furina's 1.7224 counts
hers). Her ruled height is 63 in (chars.py).

HER CLOTH (the PMX's physics chains; nothing simulates them in a headless
render, so a pose places them):
  * TAILS: the two long back tails of her skirt (左/右后摆, 21 bones each from
    the hips), swung for secondary motion as Furina's coat tails are.
  * SLEEVES: her long hanging sleeves (左/右袖, 17 bones each from the
    elbow). They hang down and back from the elbow at rest; posed rigidly
    they would follow the forearm and stick out wherever the arm is raised,
    so every pose re-aims each sleeve's root toward SLEEVE_HANG after the
    arms are placed (`drape`). Eyes-on at the first render: the sleeves are
    the part of her the pose language has never moved.

The model is the official Kokomi pack (观海, miHoYo); it is read in place from
the operator's scratch directory and NEVER enters the repo.
"""
from __future__ import annotations

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
CH = "上半身2"
YAW = 16
#: the skirt's two long back tails (chain roots, parented to the hips). The
#: names are the IMPORTED ones: mmd_tools renames the PMX's 左X / 右X to
#: X.L / X.R (her Blender probe, 2026-10-13), so the PMX's 左后摆_0_1 is
#: 后摆_0_1.L here (fixed 2026-10-14, before her first render).
TAILS = ["后摆_0_1.L", "后摆_0_1.R"]
#: the long sleeves (chain roots, parented to each elbow), side -> bone
SLEEVES = {"L": "袖_0_1.L", "R": "袖_0_1.R"}
#: where a sleeve hangs from the elbow: down and a little behind her (world)
SLEEVE_HANG = (0.0, 0.55, -1.0)
#: the water jet: a line from the far hand's knuckles along the hand, this
#: long (units; a short push of water, shorter than Furina's rapier)
PHANTOM = {"L": 0.45}

# ------------------------------------------------------------------ stance A
A_DROP, A_LEAN, A_TWIST = 0.03, 1.0, -16.0
A_FRONT, A_BACK = 0.07, 0.06
CALM = {"にこり": 0.6, "なごみ": 0.3}
#: the far hand palm up before her at the waist, forward of her: where her
#: catalyst floats. Never above the shoulder or straight out (Furina's
#: "salute" lesson, 2026-10-13, applies to every kit).
FAR = (0.22, -0.20, 0.0)
FAR_POLE = (0.2, 0.6, -1.0)
#: the wrist turned palm up and a little toward the viewer (aimw: the hand
#: along this world direction, rolled about it). Rolled the full -90 the palm
#: was edge-on to the camera and the splayed thumb and fingers read as a dark
#: spiky tangle at game size (user, 2026-10-22); at -50 the open palm shows,
#: as in the select pose.
FAR_AIM = ((0.8, -0.3, -0.1), -50.0)
#: the far hand's finger curl (fingers, thumb): straight and together, the
#: thumb not cocked away from the palm
FAR_CURL = (12, 0)
#: the near hand relaxed beside her hip, a little in front, the elbow out to
#: her side. Until 2026-10-22 it sat low before her waist at
#: (0.02, -0.17, -0.22), where the hand sank into the front of the dress and
#: the forearm read as a thin sliver (the select pose's fault, user
#: 2026-10-20; "we do need to fix her arm in-combat still", 2026-10-22).
NEAR = (-0.12, -0.15, -0.18)
NEAR_POLE = (-1.0, 0.3, -0.2)


def add(v, dv):
    return tuple(a + b for a, b in zip(v, dv))


def stance(drop=A_DROP, lean=A_LEAN, twist=A_TWIST, head_turn=34.0, head_nod=2.0, head_tilt=-3.0,
           front=A_FRONT, back=A_BACK, back_lift=0.0, sway=0.0):
    """Feet close and planted (far foot toward the enemy), upright, chest
    toward the viewer, head to the right and a little tilted."""
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


def hands(far=FAR, near=NEAR, far_pole=FAR_POLE, near_pole=NEAR_POLE, far_curl=(12, 4), near_curl=(25, 10),
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


def cloth(swing=0.0, sleeve_swing=0.0):
    """The back tails swing about the world Y axis (sideways on screen); each
    sleeve hangs from its elbow (SLEEVE_HANG), swung back by `sleeve_swing`
    (positive trails the sleeves behind a forward motion). Applied last: the
    sleeves hang from wherever the arms ended up."""
    ops = [("rotw", b, Y, swing * (1.0 + 0.2 * i)) for i, b in enumerate(TAILS)]
    hang = (0.0, SLEEVE_HANG[1] + 0.01 * sleeve_swing, SLEEVE_HANG[2])
    ops += [("aimw", SLEEVES[s], hang) for s in ("R", "L")]
    return ops


def pose(ops, morphs=None, yaw=YAW, root=(0, 0, 0)):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "root": tuple(root), "root_rot": 0.0}


def idle_pose(breath=0.0, swing=0.0, blink=0.0):
    """Stance A, the strategist at ease: the far hand palm up before her, the
    near hand low. breath 0..1: the in-breath lifts the chest, and the open
    hand floats up a hair, as if buoyed."""
    b = breath
    m = dict(CALM)
    if blink:
        m["まばたき"] = blink
    return pose(stance(drop=A_DROP + 0.006 * (1 - b), lean=A_LEAN - 1.0 * b, head_nod=2 - 1.5 * b,
                       head_tilt=-3 - 1.0 * b, sway=0.006 * b)
                + hands(far=add(FAR, (0.004 * b, 0.0, 0.018 * b)), near=add(NEAR, (0, 0, 0.006 * b)),
                        far_curl=(FAR_CURL[0] + 2 - 4 * b, FAR_CURL[1]), far_aim=FAR_AIM)
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
# Worn but composed: shoulders and head low, the far hand drawn in to her
# chest, the near hand hanging, a troubled brow.


def low_pose(breath=0.0, swing=0.0):
    b = breath
    return pose(stance(drop=A_DROP + 0.03 + 0.006 * (1 - b), lean=A_LEAN + 8 + 1.5 * (1 - b), head_turn=28,
                       head_nod=14 + 2 * (1 - b))
                + hands(far=(0.12, -0.16, 0.00 + 0.01 * b), near=(-0.08, -0.05, -0.34),
                        far_pole=(0.6, 0.2, -1.0), far_curl=(35, 15), near_curl=(20, 5))
                + cloth(swing),
                {"悲しむ": 0.6, "困る": 0.5})


IDLE_LOW = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, low_pose(0.0, swing=-0.8), "io"),
        (1.5, low_pose(1.0, swing=0.8), "io"),
        (3.0, low_pose(0.0, swing=-0.8), "io"),
    ],
}

# ------------------------------------------------------------------ attack
# A push of water from the open hand (her catalyst's normal attack: the water
# gathers at her hand and bursts at the target). The far hand draws in to her
# chest, palm up, gathering; then pushes out level at the enemy, palm forward,
# as she leans in a little (no lunge: she does not close the distance). The
# phantom jet (PHANTOM) sweeps the push; the hit lands at full extension.


def atk(far, near, far_pole=FAR_POLE, near_pole=NEAR_POLE, drop=A_DROP, lean=A_LEAN, twist=A_TWIST,
        front=A_FRONT, back=A_BACK, back_lift=0.0, head_turn=34.0, head_nod=2.0, swing=0.0, sleeve=0.0,
        morphs=None, yaw=YAW, far_aim=None, far_curl=(6, 0)):
    return pose(stance(drop=drop, lean=lean, twist=twist, front=front, back=back, back_lift=back_lift,
                       head_turn=head_turn, head_nod=head_nod)
                + hands(far=far, near=near, far_pole=far_pole, near_pole=near_pole, far_curl=far_curl,
                        near_curl=(20, 8), far_aim=far_aim)
                + cloth(swing, sleeve),
                morphs or {"真面目": 0.4, "にこり": 0.2}, yaw=yaw)


#: the push: the far arm out level at the enemy, the open hand's fingers
#: pointing at the target (the jet runs along the hand: render.py
#: phantom_points), weight onto the front foot
PUSH = (0.50, -0.06, 0.10)
PUSH_AIM = ((1.0, -0.1, 0.05), 0.0)
LEAN_IN = dict(drop=0.05, lean=6.0, twist=-8.0, front=0.10, back=0.08, back_lift=0.02, head_turn=40, head_nod=0,
               yaw=24)

ATTACK = {
    "length": 1.0, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        # gather: the far hand drawn in to her chest, palm up, weight back
        (0.18, atk((0.10, -0.18, 0.06), (-0.14, -0.12, -0.18), far_pole=(0.4, 0.4, -1.0), drop=0.04, lean=-3,
                   twist=-20, swing=-1.5, far_aim=FAR_AIM, far_curl=(20, 0), yaw=18,
                   morphs={"真面目": 0.5, "まばたき": 0.3}), "out"),
        (0.28, atk((0.16, -0.18, 0.08), (-0.15, -0.09, -0.16), far_pole=(0.4, 0.4, -1.0), drop=0.04, lean=-2,
                   twist=-18, swing=-1.0, far_aim=FAR_AIM, far_curl=FAR_CURL, yaw=20), "io"),
        # the push (impact, frame 8)
        (0.40, atk(PUSH, (-0.18, -0.04, -0.12), far_pole=(0.0, 0.5, -1.0), swing=3, sleeve=6, far_aim=PUSH_AIM,
                   **LEAN_IN), "in"),
        (0.52, atk(add(PUSH, (0.01, 0.0, 0.01)), (-0.18, -0.04, -0.10), far_pole=(0.0, 0.5, -1.0), swing=2,
                   sleeve=4, far_aim=PUSH_AIM, **{**LEAN_IN, "drop": 0.055}), "out"),
        # recover: the hand sinks back to the stance's low open palm
        (0.72, atk((0.30, -0.18, 0.02), (-0.12, -0.15, -0.19), far_pole=FAR_POLE, drop=0.035, lean=2, twist=-14,
                   swing=-1, far_aim=FAR_AIM, yaw=18), "io"),
        (0.88, idle_pose(0.5), "out"),
        (1.0, idle_pose(0.5), "io"),
    ],
    "events": {"impact": [0.40], "main": 0.40},
    # the push sweeps a short ribbon off the hand; the jet itself is a streak
    "trails": [{"blade": "L", "from": 0.28, "to": 0.40, "age": 0.10, "inner": 0.2, "taper": 0.6}],
    "bursts": [{"t": 0.40, "blade": "L", "kind": "thrust", "scale": 0.9}],
}

# ------------------------------------------------------------------ cast
# A plan set in motion: she lifts the far hand, palm up, calling the tide up
# around her; the near hand to her chest; up on her toes a little.


def call(k=1.0):
    return pose(stance(drop=A_DROP - 0.02 * k, lean=A_LEAN - 4 * k, twist=A_TWIST - 3 * k, head_nod=2 - 10 * k,
                       back_lift=0.03 * k)
                + hands(far=(0.20 - 0.02 * k, -0.12, 0.16 + 0.22 * k), near=(-0.02, -0.15, 0.02 * k),
                        far_pole=(0.2, 0.4, -1.0), near_pole=(-0.8, 0.0, -0.6), far_curl=(10, 0),
                        near_curl=(25, 10), far_aim=((0.4, -0.3, 0.2), -90.0))
                + cloth(-1.5 * k, 2 * k),
                {"笑い": 0.5 * k, "にこり": 0.6, "あ": 0.2 * k})


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

# ------------------------------------------------------------------ ascension
# Nereid's Ascension, her signature (art polish pick 5 (a), ruled 2026-10-21:
# "Agreed on all 5 defaults"): she gathers her hands low before her, eyes
# closed, then raises both arms and calls the Bake-Kurage up; a ring of water
# rises round her feet with soft jellyfish lights drifting up out of it
# (fx.py's "tide" burst, the clip's own element layer, which the game tints
# Hydro). Up on her toes at the top, a held breath, then the arms come down
# to stance A. 26 frames, as long as Varka's ascension. The game also plays it
# when Kurage's Oath is carried out as a Plan (KokomiPlan.ResolveEntry).


def rise(far, near, drop=A_DROP, lean=A_LEAN, twist=A_TWIST, head_nod=2.0, head_tilt=-3.0, back_lift=0.0,
         far_pole=(1.0, 0.3, -0.4), near_pole=(-1.0, 0.3, -0.4), curl=(10, 2), swing=0.0, sleeve=0.0,
         morphs=None):
    return pose(stance(drop=drop, lean=lean, twist=twist, head_nod=head_nod, head_tilt=head_tilt,
                       back_lift=back_lift)
                + hands(far=far, near=near, far_pole=far_pole, near_pole=near_pole, far_curl=curl,
                        near_curl=curl)
                + cloth(swing, sleeve),
                morphs or {"にこり": 0.6})


#: both arms raised in a wide V, palms open to the sky
CALL_FAR = (0.36, -0.10, 0.40)
CALL_NEAR = (-0.28, -0.08, 0.38)
CALL = dict(lean=A_LEAN - 6, twist=A_TWIST - 2, head_nod=-12, head_tilt=-2, back_lift=0.035, curl=(6, 0))
CALL_FACE = {"笑い": 0.6, "にこり": 0.5, "あ": 0.3}
#: the ring of water at her feet and its jellyfish lights (fx.py "tide")
TIDE_T, TIDE_LEN = 0.34, 0.92

ASCENSION = {
    "length": 1.3, "fps": 20, "loop": False,
    "keys": [
        (0.0, idle_pose(0.5), "io"),
        # gather: the hands drawn together low before her, eyes closed, a dip
        (0.22, rise((0.08, -0.21, -0.12), (0.03, -0.21, -0.14), drop=A_DROP + 0.04, lean=A_LEAN + 4,
                    head_nod=12, far_pole=(0.6, 0.3, -0.8), near_pole=(-0.6, 0.3, -0.8), curl=(20, 8),
                    swing=-1.5, morphs={"まばたき": 0.9, "にこり": 0.4}), "io"),
        # the call: the arms sweep out and up
        (0.40, rise((0.30, -0.16, 0.18), (-0.20, -0.14, 0.16), drop=A_DROP - 0.01, lean=A_LEAN - 3,
                    head_nod=-4, swing=1.5, sleeve=3, morphs={"にこり": 0.6, "笑い": 0.3}), "out"),
        # the top: both arms up, up on her toes, the Bake-Kurage called
        (0.56, rise(CALL_FAR, CALL_NEAR, swing=2.5, sleeve=5, morphs=CALL_FACE, **CALL), "out"),
        # held, floating up a hair on the breath
        (0.96, rise(add(CALL_FAR, (0.01, 0, 0.02)), add(CALL_NEAR, (-0.01, 0, 0.02)), swing=-1.5, sleeve=2,
                    morphs=CALL_FACE, **CALL), "io"),
        # the arms come down and she settles back into stance A
        (1.14, rise((0.24, -0.18, 0.04), (-0.12, -0.15, -0.17), drop=A_DROP, lean=A_LEAN - 1, head_nod=1,
                    far_pole=FAR_POLE, near_pole=NEAR_POLE, swing=-0.5), "io"),
        (1.3, idle_pose(0.5), "io"),
    ],
    "events": {"main": TIDE_T},
    "trails": [],
    # the clip's element layer: the ring of water and its lights, centred on
    # her feet (render.py passes the burst through; fx.py draws it)
    "bursts": [{"t": TIDE_T, "kind": "tide", "len": TIDE_LEN, "scale": 1.0}],
}

# ------------------------------------------------------------------ hurt


def flinch(k=1.0):
    return pose(stance(drop=A_DROP + 0.03 * k, lean=A_LEAN - 13 * k, twist=A_TWIST - 6 * k, head_turn=34 - 10 * k,
                       head_nod=2 - 9 * k, head_tilt=-3 - 8 * k)
                + hands(far=(0.14 - 0.04 * k, -0.18, 0.08), near=(-0.04, -0.16, 0.04),
                        far_pole=(0.6, 0.2, -1.0), near_pole=(-0.8, 0.1, -0.6), far_curl=(40, 15),
                        near_curl=(40, 15))
                + cloth(-4 * k, -3 * k),
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
# She staggers, a hand to her chest, and sinks to her knees, head bowed.
# Holds from 1.6 s.


def stagger(k=1.0):
    return pose(stance(drop=A_DROP + 0.05 * k, lean=A_LEAN + 10 * k, head_nod=2 + 14 * k, head_tilt=-6)
                + hands(far=(0.06, -0.14, 0.02), near=(-0.12, -0.06, -0.30), far_pole=(0.6, 0.2, -1.0),
                        far_curl=(35, 12), near_curl=(15, 5))
                + cloth(-3 * k),
                {"悲しむ": 0.8, "まばたき": 0.6 * k})


def kneel(k=1.0, slump=0.0, swing=0.0):
    """Down on both knees, shins back, sitting toward her heels; `slump` folds
    her forward over her knees."""
    return pose([
        ("move", "センター", (0, 0, -0.50 * k - 0.08 * slump)),
        ("movew", "足ＩＫ.L", (0.05, 0.02, 0.0)),
        ("movew", "足ＩＫ.R", (-0.30 * k, -0.02, 0.02 * k)),
        ("rotw", "上半身", Y, 8 * k + 24 * slump),
        ("rotw", "上半身", Z, A_TWIST),
        ("rotw", "首", Z, 28 * 0.4),
        ("rotw", "頭", Z, 28 * 0.6),
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
        (0.45, stagger(1.0), "io"),
        (0.62, stagger(1.0), "io"),
        (1.05, kneel(1.0, swing=2), "in"),
        (1.25, kneel(1.0, slump=0.5, swing=-1.5), "out"),
        (1.6, kneel(1.0, slump=1.0), "io"),
    ],
}

# ------------------------------------------------------------------ stance B
# Where she is not fighting (the shop, character select): the Divine Priestess
# receiving a visitor -- upright, hands folded before her at the waist, a
# gentle smile. The elbows bend and the folded hands sit at her waist, just
# under the bow; until 2026-10-22 they hung at full arm's length low before
# her, and the straight arms made "weird images" (user, 2026-10-22).


def demure(breath=0.0, swing=0.0, head_turn=28.0):
    b = breath
    return pose([("move", "センター", (0, 0, -0.01 - 0.005 * (1 - b))),
                 ("movew", "足ＩＫ.L", (0.05, 0.02, 0)),
                 ("movew", "足ＩＫ.R", (-0.04, -0.02, 0)),
                 ("rotw", "上半身", Y, -1.0 + 1.0 * (1 - b)),
                 ("rotw", "上半身", Z, -16),
                 ("rotw", "首", Z, head_turn * 0.4),
                 ("rotw", "頭", Z, head_turn * 0.6),
                 ("rot", "頭", X, 3 + 1.5 * (1 - b)),
                 ("rotw", "頭", Y, -7)]
                + hands(far=(0.06, -0.28, -0.06 + 0.006 * b), near=(0.02, -0.29, -0.07 + 0.006 * b),
                        far_pole=(0.6, 1.0, -0.3), near_pole=(-0.6, 1.0, -0.3), far_curl=(20, 8),
                        near_curl=(20, 8))
                + cloth(swing),
                {"にこり": 0.7, "なごみ": 0.4})


MERCHANT = {
    "length": 3.0, "fps": 10, "loop": True,
    "keys": [
        (0.0, demure(0.0, swing=-0.8), "io"),
        (1.5, demure(1.0, swing=0.8), "io"),
        (3.0, demure(0.0, swing=-0.8), "io"),
    ],
}

# ------------------------------------------------------------------ rest site
# Sitting on the ground facing the fire, knees drawn up, her hands on them
# (Furina's seat: the two share a skeleton to the centimetre).
REST = pose(
    [("move", "センター", (0, 0, -0.80)),
     ("movew", "足ＩＫ.L", (0.46, 0.10, 0.0)),
     ("movew", "足ＩＫ.R", (0.40, -0.14, 0.0)),
     ("rotw", "上半身", Y, 10),
     ("rotw", "上半身", Z, -14),
     ("rotw", "首", Z, 8),
     ("rotw", "頭", Z, 12),
     ("rot", "頭", X, 6),
     ("rotw", "頭", Y, -6),
     ("hand", "R", "ひざ.R", (0.03, -0.05, 0.04), (-0.5, -0.2, -1)),
     ("curl", "R", 30, 10),
     ("hand", "L", "ひざ.L", (0.03, -0.02, 0.07), (0.6, 0.3, -1)),
     ("curl", "L", 30, 10)] + cloth(0.0),
    {"にこり": 0.5, "なごみ": 0.5}, yaw=40)

# ------------------------------------------------------------------ character select
# Composed and sure of the plan: chin level, a knowing smile, the far hand
# open and low before her, palm up, and the near hand relaxed at her hip.
# The near hand was at her chest until 2026-10-19; there its fingers sank
# into the bow and its forearm read as a flat band across the dress, so it
# came down to stance A's old NEAR (the brooch now shows). Under this pose's
# twist that put the forearm as a thin sliver sunk into the dress (user,
# 2026-10-20), so the hand moved out beside her hip: SELECT_NEAR. Stance A's
# NEAR followed it on 2026-10-22.

#: the near hand beside her hip, a little in front, the elbow out to her side
SELECT_NEAR = (-0.10, -0.15, -0.18)
SELECT_NEAR_POLE = (-1.0, 0.3, -0.2)


def select_pose(head_turn=16.0, breath=1.0, swing=0.0):
    """breath 1.0 and swing 0 is the still; the loop (SELECT_LOOP) breathes out
    from there: the chest settles, the chin dips a hair, the open hand sinks
    and the skirt tails and sleeves sway."""
    b = 1.0 - breath
    return pose([("move", "センター", (0, 0, -0.01 - 0.005 * b)),
                 ("movew", "足ＩＫ.L", (0.05, 0.02, 0)),
                 ("movew", "足ＩＫ.R", (-0.04, -0.02, 0)),
                 ("rotw", "上半身", Y, -2.0 + 1.0 * b),
                 ("rotw", "上半身", Z, -16),
                 ("rotw", "首", Z, head_turn * 0.4),
                 ("rotw", "頭", Z, head_turn * 0.6),
                 ("rot", "頭", X, -4 + 1.5 * b),
                 ("rotw", "頭", Y, -6 - 0.8 * b)]
                + hands(far=(0.26, -0.14, -0.12 - 0.014 * b), near=add(SELECT_NEAR, (0, 0, -0.004 * b)),
                        far_pole=(0.3, 0.6, -1.0), near_pole=SELECT_NEAR_POLE, far_curl=(10 + 3 * b, 0),
                        near_curl=(25, 10), far_aim=((0.8, -0.3, -0.1), -90.0))
                + cloth(swing, sleeve_swing=-4.0 * swing),
                {"にこり": 0.7, "口角上げ": 0.5, "なごみ": 0.2})


SELECT = select_pose()

#: The close-up's idle loop (select stage 2; Kokomi's 2026-10-19): HALF a
#: breath, from the still's pose out to the exhale with the tails and sleeves
#: swung. The game plays it forward then back, so every motion is a cosine of
#: the loop (eased at both ends) and the loop has no seam.
#: tools/select_loop.py renders it at the still's framing; frame 0 IS the still.
SELECT_LOOP = {
    "length": 2.0, "fps": 6, "loop": True, "motion_end": 2.0,
    "keys": [
        (0.0, select_pose(), "io"),
        (2.0, select_pose(breath=0.0, swing=2.5), "io"),
    ],
}
#: not in CLIPS: a half loop that does not close on its own (the game plays it
#: forward then back); only tools/select_loop.py renders it
SELECT_LOOPS = {"select_loop": SELECT_LOOP}

# ------------------------------------------------------------------ roster tile
# The face close-up is cut from the same pose.
PORTRAIT = select_pose(head_turn=18.0)

# ------------------------------------------------------------------ scale reference
STAND = pose(
    stance(drop=0.0, lean=0.0, twist=-14, head_turn=34, head_nod=0, head_tilt=0.0, front=0.05, back=0.04)
    + [("hand", "R", "足.R", (-0.08, -0.03, -0.25), (-1.0, 0.5, 0.0)),
       ("hand", "L", "足.L", (0.08, -0.02, -0.25), (1.0, 0.5, 0.0))]
    + cloth(0),
    dict(CALM))

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
