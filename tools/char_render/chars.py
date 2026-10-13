"""Per-character config and first-look poses for tools/char_render/render.py.

Pure data plus small builders; no bpy, so it imports anywhere (tests too).
The pose language is tools/klee_render/clips.py's: +X is screen right (toward
the enemy), -Y toward the viewer, +Z up; the root yaw turns the figure's front
toward screen right, so the right side (.R) is nearest the camera.

A POSE is a dict:
  yaw     root yaw in degrees (0 = facing the camera)
  morphs  {shape key: value}
  ops     ordered bone ops on a pose cleared to rest:
            ("rotw", bone, world_axis, deg)      rotate about the bone head
            ("aimw", bone, world_dir[, twist])   point head->tail along a world dir
            ("movew", bone, world_delta)
            ("move", bone, armature_delta)
            ("rot", bone, armature_axis, deg)
            ("hand", side, anchor_bone, world_offset, elbow_pole_world)
            ("curl", side, finger_deg, thumb_deg)
  prop    None, or {"side": "R"|"L", "dir": world_dir, "grip": units from the
          prop origin along its blade toward the tip, "roll": deg} -- the
          character's prop (Varka's claymore) placed in that hand.

THE MODELS NEVER ENTER THE REPO. Each pack's terms (scratchpad
models/SOURCES.md) forbid redistribution and commercial use; the PMX is read
in place from the operator's scratch directory and only rendered PNGs leave it.

SCALE (docs/current/LAW.md, "Scale by real heights"): body px at 1080p =
canon height / ADULT_IN * BASE_ADULT_PX. Genshin publishes no heights; the
figures below are [USER]'s ruled heights (2026-10-13) (Klee's ruled
4'2" = 50 in is the anchor this law was ruled on). The official MMD packs are
NOT at one common scale (Klee's 2021 pack and the 观海 packs differ by ~1.4x
at the head bone), so each character's ppu is solved from its own measured
rest height, never shared.

PROPORTIONS (ruled 2026-10-13): [USER]: "Hmm. Ok, let's give Varka the height
boost and use these proportion. (a)." The reference is modelmetrics.net's
"Genshin Impact - Character Heights" chart (v1.0, 2026), which measures the
official models head to foot without shoes, hair or hats. Its centimetres are
model sizes, not canon heights; only their ratios are used, anchored on
Furina = 63 in (scale 63 / 150.5 in per chart cm). That puts Neuvillette at
76.4 in against his canon 192 cm (75.6 in). Klee, Furina and Kokomi keep their
ruled heights (the chart is within 3% of each). Varka moves to 82 in (chart
196.4 cm, a size above the other tall males) at his next re-render; until then
`ruled_height_in` holds it. GUEST_HEIGHTS_IN holds Furina's guest stars from
the same chart.
"""
from __future__ import annotations

import math

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

ADULT_IN = 68.0          # 5'8": the middle of the 5'6"-5'10" adults the law names
BASE_ADULT_PX = 235.0    # the base adults' bodies at 1080p (Klee visual paper, pick 2)
COMBAT_SCALE = 0.5       # combat textures are drawn at 0.5 (2x for 4K), as Klee's
IMPORT_SCALE = 0.08      # mmd_tools import scale, as tools/klee_render/render.py
OUTLINE_PX = 2.2         # texture px at combat scale (1.1 screen px), as Klee's

#: Materials common to the 观海 packs (Kokomi 2021, Furina 2023, Varka 2026).
FACE_MATS = {"颜", "顏1", "颜2", "顏2", "二重", "睫", "睫眉", "眉", "白目", "目", "目光", "星目", "口舌", "齿", "齒"}
#: Drawn without a hull: the eyes and mouth parts sit inside the face.
NO_LINE_MATS = {"二重", "睫", "睫眉", "眉", "白目", "目", "目光", "星目", "口舌", "齿", "齒"}


# Furina's guest stars, chart cm x 63 / 150.5 (see PROPORTIONS above).
GUEST_HEIGHTS_IN = {
    "sigewinne": 52.0, "escoffier": 62.9, "chevreuse": 63.0,
    "charlotte": 63.1, "lynette": 63.3, "freminet": 66.0, "lyney": 66.7,
    "clorinde": 69.2, "navia": 70.0, "wriothesley": 76.1, "neuvillette": 76.4,
}


#: The guest stars' packs (scratch models/<guest>/unpacked/, all 观海
#: adaptations on the shared bone set, probed 2026-10-13: every bone chars.py
#: and toon.py pose is present in all eleven; none has a 手先 bone). `head`
#: is the 頭 bone's height over the lowest vertex in raw PMX units, the
#: measure each guest is scaled by (hats, ears and Sigewinne's antennae left
#: out); `face` and `hide` add to FACE_MATS / the hidden overlays.
FURINA_HEAD = 16.763
GUESTS = {
    "charlotte": {"pmx": "charlotte/unpacked/夏洛蒂.pmx", "head": 16.638},
    "chevreuse": {"pmx": "chevreuse/unpacked/夏沃蕾.pmx", "head": 16.639},
    "clorinde": {"pmx": "clorinde/unpacked/克洛琳德.pmx", "head": 18.931},
    "escoffier": {"pmx": "escoffier/unpacked/爱可菲.pmx", "head": 17.134},
    # his pack wears the diving helmet; the guest still shows his face
    "freminet": {"pmx": "freminet/unpacked/菲米尼.pmx", "head": 17.567,
                 "hide": {"头盔", "头盔表情1", "头盔表情2", "头盔表情3", "头盔表情4"}},
    "lynette": {"pmx": "lynette/unpacked/【琳妮特】.pmx", "head": 16.630},
    "lyney": {"pmx": "lyney/unpacked/林尼.pmx", "head": 17.541},
    "navia": {"pmx": "navia/unpacked/娜维娅.pmx", "head": 19.067},
    "neuvillette": {"pmx": "neuvillette/unpacked/那维莱特.pmx", "head": 20.676, "face": {"眉影"}},
    "sigewinne": {"pmx": "sigewinne/unpacked/希格雯.pmx", "head": 12.061},
    "wriothesley": {"pmx": "wriothesley/unpacked/莱欧斯利.pmx", "head": 20.327, "face": {"眉影"}},
}


def guest_ppu(guest: str, furina_ppu: float) -> float:
    """A guest's texture px per unit: Furina's, times the guest's height over
    hers (GUEST_HEIGHTS_IN over 63 in), over the guest's head-bone height
    over hers -- so every guest stands at the same px per inch as Furina."""
    return furina_ppu * (GUEST_HEIGHTS_IN[guest] / CHARS["furina"]["height_in"]) * (FURINA_HEAD / GUESTS[guest]["head"])


def body_px(height_in: float) -> float:
    return height_in / ADULT_IN * BASE_ADULT_PX


def is_overlay(mat_name: str) -> bool:
    """The `+` materials are duplicate shells (hair sphere-map highlights,
    Furina's translucent skirt layers) authored as BLENDED transparency over
    the real surface. Style G's toon pass would paint them opaque over the
    hair, and EEVEE writes no AOV from a blended surface (Klee's 表情 lesson),
    so they are hidden, not shaded."""
    return mat_name.endswith("+")


def fwd(yaw, d):
    r = math.radians(yaw)
    return (math.sin(r) * d, -math.cos(r) * d, 0)


def stance(drop=0.05, lean=3.0, twist=-14.0, head_turn=40.0, head_nod=2.0, head_tilt=0.0,
           front=0.12, back=0.10, front_y=0.02, back_y=-0.02, sway=0.0, back_lift=0.0):
    """Feet planted (far foot toward the enemy), chest toward the viewer,
    head to the right. `twist` turns the upper body toward the camera;
    `back_lift` raises the rear foot (weight forward, light on the feet)."""
    return [
        ("move", "センター", (sway, 0, -drop)),
        ("movew", "足ＩＫ.L", (front, front_y, 0)),
        ("movew", "足ＩＫ.R", (-back, back_y, back_lift)),
        ("rotw", "上半身", Y, lean),
        ("rotw", "上半身", Z, twist),
        ("rotw", "首", Z, head_turn * 0.4),
        ("rotw", "頭", Z, head_turn * 0.6),
        ("rot", "頭", X, head_nod),
        ("rotw", "頭", Y, head_tilt),
    ]


def arms(near, far, near_anchor="上半身2", far_anchor="上半身2", near_pole=(-0.6, 0.4, -0.2),
         far_pole=(0.2, 0.5, -1.0), near_curl=(40, 15), far_curl=(40, 15)):
    return [
        ("hand", "R", near_anchor, near, near_pole),
        ("curl", "R", near_curl[0], near_curl[1]),
        ("hand", "L", far_anchor, far, far_pole),
        ("curl", "L", far_curl[0], far_curl[1]),
    ]


def pose(ops, morphs=None, yaw=14.0, prop=None):
    return {"yaw": yaw, "morphs": dict(morphs or {}), "ops": ops, "prop": prop}


REST = pose([], {}, yaw=0.0)

# ------------------------------------------------------------------ Furina
# Theatrical: weight on the front foot, rear heel up, the far arm swept out
# toward the enemy palm-open like a bow to the house, the near hand at her hip.
FURINA_STANCE = pose(
    stance(drop=0.035, lean=-2.0, twist=-18, head_turn=38, head_nod=-3, head_tilt=-4,
           front=0.10, back=0.10, back_lift=0.035)
    + arms((-0.12, 0.00, -0.30), (0.46, -0.12, 0.30), near_anchor="上半身2",
           near_pole=(-1.0, 0.3, 0.0), far_pole=(0.0, 0.4, -1.0), near_curl=(30, 10), far_curl=(8, 0)),
    {"にやり": 0.7, "口角上げ": 0.3}, yaw=16)

# ------------------------------------------------------------------ Kokomi
# Calm catalyst stance: feet close, upright, the far hand raised before her
# at shoulder height palm up (where the catalyst floats), the near hand low.
KOKOMI_STANCE = pose(
    stance(drop=0.03, lean=1.0, twist=-16, head_turn=34, head_nod=2, head_tilt=-3,
           front=0.07, back=0.06)
    + arms((-0.10, -0.06, -0.36), (0.30, -0.18, 0.16), near_pole=(-1.0, 0.3, 0.0),
           far_pole=(0.2, 0.5, -1.0), near_curl=(25, 10), far_curl=(12, 4)),
    {"にこり": 0.6}, yaw=16)

# ------------------------------------------------------------------ Varka
# Heavy and wide: knees bent, feet apart, the claymore held two-handed low
# before him with the blade angled down toward the enemy's feet.
VARKA_STANCE = pose(
    stance(drop=0.15, lean=8.0, twist=-14, head_turn=34, head_nod=4,
           front=0.30, back=0.26, front_y=0.03, back_y=-0.04)
    + arms((0.14, -0.26, -0.30), (0.26, -0.22, -0.24), near_pole=(-0.8, -0.2, -0.6),
           far_pole=(0.6, 0.2, -1.0), near_curl=(70, 30), far_curl=(70, 30)),
    {"真面目": 0.6}, yaw=14,
    prop={"side": "R", "dir": (0.80, -0.10, -0.58), "grip": 0.12, "roll": 0.0})

#: One entry per kit. `pmx` is relative to the operator's models root
#: (scratchpad models/<char>/unpacked/...). `expressions` maps the roles a
#: clip will need to this model's morph names (probed 2026-10-13).
CHARS = {
    "furina": {
        "pmx": "furina/unpacked/【芙宁娜】.pmx",
        "height_in": 63.0,          # ruled 2026-10-13
        "hand_tip": "中指１",        # no 手先 bone in the 观海 packs: the middle finger's base stands in
        "face_mats": FACE_MATS,
        "no_line_mats": NO_LINE_MATS,
        "expressions": {"smile": "にこり", "smirk": "にやり", "happy_eyes": "笑い", "blink": "まばたき",
                        "wince": ("まばたき", "困る"), "sad": "悲しむ", "shock": "びっくり"},
        "stance": FURINA_STANCE,
        "prop": None,
        # the full clip set (render.py --clips): her pose library. Her pack
        # has no sword, so she has no blades; her attack's trail follows a
        # phantom rapier off her far hand (furina_clips.PHANTOM).
        "clips": "furina_clips",
        "blades": {},
        "hide_mats": set(),
        "camera_height": 0.8,
    },
    "kokomi": {
        "pmx": "kokomi/unpacked/珊瑚宫心海.pmx",
        "height_in": 63.0,          # ruled 2026-10-13
        "hand_tip": "中指１",
        "face_mats": FACE_MATS,
        "no_line_mats": NO_LINE_MATS,
        "expressions": {"smile": "にこり", "smirk": "にやり", "happy_eyes": "笑い", "blink": "まばたき",
                        "wince": ("まばたき", "困る"), "sad": "悲しむ", "shock": "びっくり", "star_eyes": "星目"},
        "stance": KOKOMI_STANCE,
        "prop": None,
    },
    "varka": {
        "pmx": "varka/unpacked/法尔伽.pmx",
        "height_in": 78.0,          # ruled 2026-10-13: his custom in-game model is tall
        # 82 in ruled later the same day (PROPORTIONS above); 78 stays live
        # until his re-render, because the packed manifest was built at 78.
        "ruled_height_in": 82.0,
        "hand_tip": "中指１",
        "face_mats": FACE_MATS,
        "no_line_mats": NO_LINE_MATS,
        "expressions": {"smile": "にこり", "smirk": "にやり", "happy_eyes": "笑い", "blink": "まばたき",
                        "wince": ("まばたき", "怒り"), "stern": "真面目", "shock": "びっくり", "star_eyes": "星目"},
        "stance": VARKA_STANCE,
        "prop": "varka/unpacked/武器.pmx",     # "Claymore"; 剑.pmx ("Varka_Sword") is the other blade
        # the full clip set (render.py --clips): his pose library, and his two
        # claymores, one per hand ([USER], 2026-10-13: a dual wielder). Each
        # blade's local frame as imported: tip along -Y, the flat in the XY
        # plane; `grip` is where the palm closes on the handle, `base` the
        # blade just past the guard and `tip` its point (measured on the
        # meshes, 2026-10-13). The longer Varka_Sword leads in the far hand.
        "clips": "varka_clips",
        "blades": {
            "R": {"pmx": "varka/unpacked/武器.pmx", "grip": 0.08, "base": -0.36, "tip": -1.49},
            "L": {"pmx": "varka/unpacked/剑.pmx", "grip": 0.06, "base": -0.38, "tip": -1.80},
        },
        "hide_mats": set(),
        "camera_height": 1.0,
    },
}


def target_ppu(char: str, rest_height_units: float) -> float:
    """Texture px per model unit at combat scale so the rest-pose height lands
    on the canon body px at 1080p."""
    return body_px(CHARS[char]["height_in"]) / COMBAT_SCALE / rest_height_units
