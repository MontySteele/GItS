"""The Bake-Kurage's clips, as numbers: pure data, no bpy, imports anywhere.

Kokomi's jellyfish (art polish pick 5 (a), item 4, ruled 2026-10-21:
"Agreed on all 5 defaults") replaces the tweened static 64x128 sprite cut
from the summon art (tools/cut_kurage_summon.py, which still makes the
docket icon) with a frame sheet. No 3D model of the Bake-Kurage exists in
the art sources (the 观海 Kokomi pack is the body PMX alone, scratch
models/SOURCES.md), so tools/kurage_render/render.py builds a stylised one
in Blender from primitives: a glowing, translucent bell in cyan to
electric blue with a white-blue core at its crown, faint ribs and a bright
rim, six wispy tentacles and six finer threads, three pale frilled oral arms,
a few bubbles and sparkles, all in the Hydro palette of the old sprite and of
KokomiSwarm's jellyfish. No pink: the user's reference (2026-10-22, "too
solid, too pink") is light and water, not a solid toy.

A clip is keyed BELL STATES, eased between as the character clips are
(toon.EASE: io, out, in, lin):

  sx, sz   the bell's width and height scale (squash and stretch)
  pinch    0..1, the rim drawn in (the swimming stroke)
  tilt     degrees, the bell tipped toward screen right (+) or left (-)
  trail    the tentacles swept back (+, behind a forward lunge) or flung
           forward (-, recoiling from a hit)
  sway     the tentacles' wave amplitude (1 at rest)
  droop    0..1, death: the tentacles hang limp and the bell sags
  lift     units the whole jellyfish rises (+) or sinks (-) in its cell

On top of the keys, `pulse(t)` (idle and the others alike) is the bell's
breathing contraction, and `wave(t, s, phase)` the travelling wave down each
tentacle. Every periodic term closes over IDLE's 3.0 s so the loop has no
seam.

Scale: the scene draws the cell at 0.5 (2x textures, as every kit's frames);
PPU texture px per unit, so the jellyfish stands about 250 px tall in the
texture, the old sprite's 128 on screen. The anchor (0, 0) is the old
sprite's centre, which bake_kurage.tscn's Rig sits on.
"""
from __future__ import annotations

import math

PPU = 100.0              # texture px per unit (2x of the screen)
#: the camera's fixed window, in units round the anchor: every frame of every
#: clip renders on the same canvas, so one cell and one origin serve them all
VIEW_X = (-1.2, 1.2)
VIEW_Z = (-1.45, 1.55)
PITCH = 6.0              # degrees the camera looks down, into the bell a little

# ------------------------------------------------------------------ the body
BELL_R = 0.62            # the bell's radius at the rim (62 px at 1x: the old sprite's bell)
BELL_TOP = 1.27          # the crown's height over the anchor
BELL_RIM = 0.66          # the rim's height over the anchor
BELL_CENTRE = 0.92       # squash and tilt pivot about this height
TENTACLES = 6
TENTACLE_LEN = (1.70, 1.95)    # shortest, longest
ORAL_ARMS = 3
ORAL_LEN = 0.95

#: sRGB colours (render.py linearises them)
COLORS = {
    "bell_core": (0.16, 0.56, 1.00),      # the bell's body where it faces the camera: thin and blue
    "bell_edge": (0.72, 0.97, 1.00),      # its silhouette, brighter than the body
    "rib": (0.70, 0.95, 1.00),            # the faint ribs inside the bell
    "rim": (0.80, 0.99, 1.00),            # the bright band round the rim
    "pearl": (0.97, 1.00, 1.00),          # the white-blue core at the crown
    "aura": (0.42, 0.80, 1.00),           # the core's soft glow
    "tentacle": (0.60, 0.90, 1.00),       # pale-blue wisps
    "thread": (0.78, 0.96, 1.00),         # the finer threads between them
    "oral": (0.70, 0.94, 1.00),           # pale frilled oral arms
    "bubble": (0.82, 0.98, 1.00),
    "sparkle": (0.92, 1.00, 1.00),
    "glint": (1.00, 1.00, 1.00),
    "glow": (0.38, 0.80, 1.00),           # the halo pack.py draws round the silhouette
}
OUTLINE_PX = 2.2         # texture px: the old outline's reach, which bounds the glow (pack.py)
GLOW_PX = 7.0            # texture px: the halo's blur radius

REST = {"sx": 1.0, "sz": 1.0, "pinch": 0.0, "tilt": 0.0, "trail": 0.0, "sway": 1.0, "droop": 0.0, "lift": 0.0}
LOOP = 3.0               # every periodic term closes over this


def state(**kw) -> dict:
    out = dict(REST)
    out.update(kw)
    return out


EASE = {
    "io": lambda u: u * u * (3 - 2 * u),
    "out": lambda u: 1 - (1 - u) ** 2,
    "in": lambda u: u * u,
    "lin": lambda u: u,
}


def at(clip: dict, t: float) -> dict:
    """The bell state at time t: the keys eased between."""
    keys = clip["keys"]
    for (t0, a, _e0), (t1, b, e1) in zip(keys, keys[1:]):
        if t0 <= t <= t1 + 1e-9:
            u = 0.0 if t1 == t0 else EASE[e1](max(0.0, min(1.0, (t - t0) / (t1 - t0))))
            return {k: a[k] + (b[k] - a[k]) * u for k in REST}
    return dict(keys[-1][1])


def pulse(t: float) -> float:
    """The breathing contraction, 0..1, twice per loop: a quick draw-in and a
    slow release, as a jellyfish swims."""
    ph = (t / (LOOP / 2)) % 1.0
    return math.sin(math.pi * min(1.0, ph / 0.35)) ** 2 if ph < 0.35 else 0.0


def wave(t: float, s: float, phase: float) -> float:
    """The travelling wave down a tentacle, at fraction s of its length."""
    return math.sin(2 * math.pi * t / LOOP - 2.4 * s + phase)


IDLE = {
    "length": 3.0, "fps": 12, "loop": True,
    "keys": [(0.0, state(), "io"), (3.0, state(), "io")],
}

# The lunge (the Rig's position track carries it 30 px toward the enemy):
# an anticipation squash, the stretch as it shoots forward with the tentacles
# swept back, an overshoot, and settle.
ATTACK = {
    "length": 0.5, "fps": 20, "loop": False,
    "keys": [
        (0.0, state(), "io"),
        (0.12, state(sx=1.20, sz=0.80, pinch=0.0, tilt=-4, trail=-0.2), "out"),
        (0.22, state(sx=0.80, sz=1.24, pinch=0.8, tilt=14, trail=0.8, sway=0.5), "out"),
        (0.36, state(sx=1.07, sz=0.94, pinch=0.2, tilt=4, trail=0.4), "io"),
        (0.5, state(), "io"),
    ],
}

# Struck: squashed flat and knocked back, the tentacles flung forward.
HURT = {
    "length": 0.4, "fps": 20, "loop": False,
    "keys": [
        (0.0, state(), "io"),
        (0.06, state(sx=1.18, sz=0.80, tilt=-14, trail=-0.55, sway=1.4), "out"),
        (0.20, state(sx=0.94, sz=1.07, tilt=6, trail=0.3, sway=1.3), "io"),
        (0.4, state(), "io"),
    ],
}

# Spent: a last squash, then the bell sags and deflates and the tentacles go
# limp as it sinks (the scene fades it out over the same second).
DEATH = {
    "length": 1.0, "fps": 15, "loop": False,
    "keys": [
        (0.0, state(), "io"),
        (0.12, state(sx=1.16, sz=0.82, tilt=-10, trail=-0.45, sway=1.3), "out"),
        (0.5, state(sx=1.20, sz=0.66, tilt=12, droop=0.7, sway=0.4, lift=-0.08), "io"),
        (1.0, state(sx=1.26, sz=0.52, tilt=18, droop=1.0, sway=0.1, lift=-0.2), "io"),
    ],
}

CLIPS = {"idle": IDLE, "attack": ATTACK, "hurt": HURT, "death": DEATH}


def times(clip: dict) -> list[float]:
    """The frame times, as the character renderer's: [0, length) at fps."""
    return [round(i / clip["fps"], 6) for i in range(int(round(clip["length"] * clip["fps"])))]
