"""The character-select background scene, shared by the rig generators.

[USER], 2026-10-14: "during character select, none of the art pieces for the
base game's characters are static; the character does a small idle loop with
particle effects. Let's investigate if we could do the same somehow for our
characters, focusing on Klee, Varka and Furina".

Stage 1 of that (the research report's option (c)): the still close-up
`select_closeup.png` (rendered from the model by klee_render/pack.py or
char_render/pack.py) breathes on an AnimationPlayer that autoplays a looping
clip, and two or three CPUParticles2D emitters per element drift over it, in
the shape of the base game's `char_select_bg_<id>.tscn` (a centred 1920x1080
Control; Ironclad's embers, Defect's fireflies: 2-5 emitters, `preprocess` so
they are already in the air, `local_coords`, an additive CanvasItemMaterial).

Each kit's rig generator (`python -m tools.<char>_rig gen`) is the ONE producer
of its `klee-mod/pck-src/<char>/ui/char_select_bg_<char>.tscn`; build_pck.ps1
only overlays it. This module only spells the text.

Constraints the text is written around:
  * no scripts (a script resource cannot ship in a mod pck), so the loop is an
    autoplaying AnimationPlayer, as `merchant_character.tscn` already does;
  * no base-game `res://images/vfx/*` textures and no new PNGs: every particle
    texture is a GradientTexture2D sub-resource, so the scene costs text only;
  * every character's select assets are preloaded together (AssetSets.cs:215),
    so the counts stay at base levels (at most ~30 particles an emitter).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from tools.klee_rig.rig import color, fnum, num, vec2

NL = "\n"
#: Stage 2 (2026-10-15): tools/select_loop.py renders the close-up as a loop
#: and commits this manifest (sizes, the moving box, the grid; no pixels).
LOOP_MANIFEST = Path(__file__).resolve().parent / "select_loop.json"
WIDTH, HEIGHT = 1920, 1080
#: Breath cycle (s). StaticPortraitIdle breathes rest/shop portraits on 2.4 s;
#: a close-up is larger on screen, so it breathes slower.
BREATH_LENGTH = 3.6
#: Peak scale of the splash about its figure's bottom centre: a vertical
#: stretch of 0.9% (about 9 px at the head of a ~1040 px figure) and a hair of
#: width, so the chest rises rather than the frame zooming.
BREATH_SCALE = (1.003, 1.009)
#: Lateral sway (px), on its own phase inside the same loop.
SWAY_PX = 2.0
ANIMATION = "select_idle"
#: Godot's ease-in-out transition value for a key.
EASE_IN_OUT = -2.0


@dataclass(frozen=True)
class Tex:
    """A radial GradientTexture2D: `stops` are (offset, alpha) on white."""
    tid: str
    width: int
    height: int
    stops: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class Emitter:
    name: str
    tex: str
    position: tuple[float, float]
    amount: int
    lifetime: float
    extents: tuple[float, float]
    direction: tuple[float, float]
    spread: float
    velocity: tuple[float, float]
    gravity: tuple[float, float]
    scale: tuple[float, float]
    ramp: tuple[tuple[float, tuple[float, float, float, float]], ...]
    additive: bool = True
    behind: bool = False  # drawn between the backdrop and the splash
    angle: tuple[float, float] = (0.0, 0.0)
    angular_velocity: tuple[float, float] = (0.0, 0.0)
    tangential: tuple[float, float] = (0.0, 0.0)
    damping: tuple[float, float] = (0.0, 0.0)
    hue: tuple[float, float] = (0.0, 0.0)
    scale_curve: tuple[tuple[float, float], ...] = ()
    align: bool = False  # the texture's Y axis follows the velocity


@dataclass(frozen=True)
class Element:
    textures: tuple[Tex, ...]
    emitters: tuple[Emitter, ...] = field(default_factory=tuple)


SOFT_DOT = (0.0, 1.0), (0.35, 0.55), (1.0, 0.0)
HARD_DOT = (0.0, 1.0), (0.6, 0.9), (1.0, 0.0)
RING = (0.0, 0.0), (0.55, 0.12), (0.8, 0.85), (0.9, 0.5), (1.0, 0.0)
PULSE = (0.0, 0.0), (0.5, 1.0), (1.0, 0.0)
#: a jellyfish bell: bright crown, soft skirt
JELLY = (0.0, 0.9), (0.45, 0.65), (0.8, 0.22), (1.0, 0.0)
#: a jellyfish's swim: the bell swells and settles twice over its life
BOB = (0.0, 0.5), (0.25, 1.0), (0.5, 0.75), (0.75, 1.0), (1.0, 0.6)


def _element(fig_x: float) -> dict[str, Element]:
    """Each element's emitters, placed around a figure centred at x."""
    return {
        # Pyro: embers rising off the bottom edge, a few fast sparks arcing up
        # and falling back, and a slow warm glow breathing behind the figure.
        "pyro": Element(
            textures=(Tex("Tex_dot", 32, 32, SOFT_DOT), Tex("Tex_spark", 8, 32, HARD_DOT)),
            emitters=(
                Emitter("Glow", "Tex_dot", (fig_x, 760), 2, 4.0, (120, 120), (0, -1), 0, (0, 6),
                        (0, 0), (14.0, 18.0),
                        ((0.0, (1, 0.45, 0.15, 0)), (0.5, (1, 0.5, 0.18, 0.22)), (1.0, (1, 0.45, 0.15, 0))),
                        behind=True, scale_curve=PULSE),
                Emitter("Embers", "Tex_dot", (960, 1110), 28, 9.0, (1000, 40), (0, -1), 25, (30, 70),
                        (8, -18), (0.12, 0.3),
                        ((0.0, (1, 0.85, 0.4, 0)), (0.15, (1, 0.62, 0.22, 1)), (0.7, (0.92, 0.28, 0.1, 0.8)),
                         (1.0, (0.4, 0.05, 0, 0))),
                        tangential=(-6, 6), hue=(-0.02, 0.03)),
                Emitter("Sparks", "Tex_spark", (fig_x, 1100), 10, 3.5, (600, 20), (0, -1), 18, (140, 240),
                        (0, 45), (0.6, 1.1),
                        ((0.0, (1, 0.95, 0.7, 0)), (0.1, (1, 0.9, 0.55, 1)), (1.0, (1, 0.4, 0.1, 0))),
                        align=True),
            ),
        ),
        # Anemo: teal wind streaks crossing behind the figure, a few leaves
        # tumbling across in front, and slow teal motes drifting sideways.
        "anemo": Element(
            textures=(Tex("Tex_dot", 32, 32, SOFT_DOT), Tex("Tex_streak", 128, 6, SOFT_DOT),
                      Tex("Tex_leaf", 24, 12, HARD_DOT)),
            emitters=(
                Emitter("Streaks", "Tex_streak", (-120, 520), 12, 5.0, (40, 440), (1, -0.05), 4, (380, 560),
                        (0, -6), (0.8, 1.6),
                        ((0.0, (0.56, 1, 0.84, 0)), (0.3, (0.56, 1, 0.84, 0.45)), (1.0, (0.56, 1, 0.84, 0))),
                        behind=True),
                Emitter("Leaves", "Tex_leaf", (-60, 500), 7, 9.0, (30, 480), (1, -0.15), 12, (150, 240),
                        (0, 22), (0.8, 1.3),
                        ((0.0, (0.5, 0.82, 0.42, 0)), (0.1, (0.5, 0.82, 0.42, 0.95)),
                         (0.85, (0.62, 0.86, 0.4, 0.9)), (1.0, (0.62, 0.86, 0.4, 0))),
                        additive=False, angle=(0, 360), angular_velocity=(-180, 180), tangential=(-15, 15),
                        hue=(-0.04, 0.04)),
                Emitter("Motes", "Tex_dot", (960, 560), 16, 10.0, (1100, 480), (1, 0), 20, (20, 50),
                        (0, 0), (0.08, 0.2),
                        ((0.0, (0.56, 1, 0.84, 0)), (0.3, (0.6, 1, 0.86, 0.8)), (1.0, (0.56, 1, 0.84, 0))),
                        ),
            ),
        ),
        # Hydro: a soft blue light pulsing behind the figure, bubbles rising
        # and wobbling off the bottom edge, and fine droplets glinting upward.
        "hydro": Element(
            textures=(Tex("Tex_dot", 32, 32, SOFT_DOT), Tex("Tex_bubble", 48, 48, RING)),
            emitters=(
                Emitter("Glow", "Tex_dot", (fig_x, 720), 2, 4.5, (140, 140), (0, -1), 0, (0, 6),
                        (0, 0), (15.0, 20.0),
                        ((0.0, (0.36, 0.72, 1, 0)), (0.5, (0.36, 0.72, 1, 0.25)), (1.0, (0.36, 0.72, 1, 0))),
                        behind=True, scale_curve=PULSE),
                Emitter("Bubbles", "Tex_bubble", (960, 1120), 18, 10.0, (1000, 30), (0, -1), 10, (40, 80),
                        (0, -6), (0.35, 0.8),
                        ((0.0, (0.65, 0.85, 1, 0)), (0.12, (0.7, 0.88, 1, 0.75)), (0.85, (0.7, 0.9, 1, 0.6)),
                         (1.0, (0.8, 0.95, 1, 0))),
                        tangential=(-10, 10), damping=(0, 2)),
                Emitter("Droplets", "Tex_dot", (960, 640), 24, 8.0, (1000, 460), (0, -1), 30, (10, 30),
                        (0, -4), (0.06, 0.15),
                        ((0.0, (0.55, 0.82, 1, 0)), (0.3, (0.75, 0.92, 1, 0.9)), (1.0, (0.55, 0.82, 1, 0))),
                        ),
            ),
        ),
        # Kokomi's Hydro, the reef (2026-10-19): a pearl-aqua light behind the
        # figure, Furina's bubbles at fewer and slower, and a few soft
        # coral-violet jellyfish (her Bake-Kurage) drifting up and pulsing,
        # so the two Hydro kits do not share one screen.
        "reef": Element(
            textures=(Tex("Tex_dot", 32, 32, SOFT_DOT), Tex("Tex_bubble", 48, 48, RING),
                      Tex("Tex_jelly", 48, 40, JELLY)),
            emitters=(
                Emitter("Glow", "Tex_dot", (fig_x, 700), 2, 5.0, (150, 150), (0, -1), 0, (0, 5),
                        (0, 0), (16.0, 21.0),
                        ((0.0, (0.5, 0.86, 0.95, 0)), (0.5, (0.55, 0.86, 0.95, 0.22)), (1.0, (0.5, 0.86, 0.95, 0))),
                        behind=True, scale_curve=PULSE),
                Emitter("Bubbles", "Tex_bubble", (960, 1120), 14, 11.0, (1000, 30), (0, -1), 10, (35, 70),
                        (0, -5), (0.3, 0.7),
                        ((0.0, (0.7, 0.9, 1, 0)), (0.12, (0.75, 0.92, 1, 0.7)), (0.85, (0.8, 0.94, 1, 0.55)),
                         (1.0, (0.85, 0.96, 1, 0))),
                        tangential=(-8, 8), damping=(0, 2)),
                Emitter("Jellies", "Tex_jelly", (960, 1000), 7, 14.0, (950, 120), (0, -1), 8, (14, 26),
                        (0, -2), (0.7, 1.3),
                        ((0.0, (1, 0.72, 0.86, 0)), (0.15, (1, 0.74, 0.88, 0.5)), (0.8, (0.78, 0.7, 1, 0.42)),
                         (1.0, (0.7, 0.7, 1, 0))),
                        tangential=(-4, 4), hue=(-0.03, 0.03), scale_curve=BOB),
            ),
        ),
        # Electro (Yae, 2026-10-19): a slow violet light pulsing behind the
        # figure, sakura petals drifting down and across in front (her
        # Sacred Sakura), and small violet sparks flicking upward, fast and
        # short-lived, as static off the Electro.
        "electro": Element(
            textures=(Tex("Tex_dot", 32, 32, SOFT_DOT), Tex("Tex_petal", 20, 12, HARD_DOT),
                      Tex("Tex_spark", 6, 24, HARD_DOT)),
            emitters=(
                Emitter("Glow", "Tex_dot", (fig_x, 700), 2, 4.0, (130, 130), (0, -1), 0, (0, 6),
                        (0, 0), (15.0, 19.0),
                        ((0.0, (0.69, 0.42, 1, 0)), (0.5, (0.72, 0.45, 1, 0.24)), (1.0, (0.69, 0.42, 1, 0))),
                        behind=True, scale_curve=PULSE),
                Emitter("Petals", "Tex_petal", (1100, -40), 12, 11.0, (900, 30), (-0.35, 1), 20, (40, 80),
                        (-6, 14), (0.7, 1.2),
                        ((0.0, (1, 0.74, 0.84, 0)), (0.1, (1, 0.76, 0.86, 0.95)),
                         (0.85, (0.98, 0.7, 0.82, 0.85)), (1.0, (0.98, 0.7, 0.82, 0))),
                        additive=False, angle=(0, 360), angular_velocity=(-120, 120), tangential=(-12, 12),
                        hue=(-0.03, 0.02)),
                Emitter("Sparks", "Tex_spark", (fig_x, 900), 14, 1.6, (520, 260), (0, -1), 35, (60, 140),
                        (0, 0), (0.5, 1.0),
                        ((0.0, (0.85, 0.7, 1, 0)), (0.08, (0.9, 0.78, 1, 1)), (0.4, (0.66, 0.4, 1, 0.7)),
                         (1.0, (0.55, 0.3, 1, 0))),
                        align=True, damping=(40, 80), hue=(-0.02, 0.02)),
            ),
        ),
    }


ELEMENTS = ("pyro", "anemo", "hydro", "reef", "electro")


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------


def _floats(xs) -> str:
    return "PackedFloat32Array(" + ", ".join(num(x) for x in xs) + ")"


def _tex_blocks(t: Tex) -> str:
    offsets = [o for o, _ in t.stops]
    colors = ", ".join(f"1, 1, 1, {num(a)}" for _, a in t.stops)
    return NL.join([
        f'[sub_resource type="Gradient" id="Gradient_{t.tid}"]',
        f"offsets = {_floats(offsets)}",
        f"colors = PackedColorArray({colors})",
        "",
        f'[sub_resource type="GradientTexture2D" id="{t.tid}"]',
        f'gradient = SubResource("Gradient_{t.tid}")',
        f"width = {t.width}",
        f"height = {t.height}",
        "fill = 1",
        "fill_from = Vector2(0.5, 0.5)",
        "fill_to = Vector2(1, 0.5)",
        "",
    ])


def _ramp_block(e: Emitter) -> str:
    offsets = [o for o, _ in e.ramp]
    colors = ", ".join(", ".join(num(c) for c in rgba) for _, rgba in e.ramp)
    return NL.join([
        f'[sub_resource type="Gradient" id="Ramp_{e.name}"]',
        f"offsets = {_floats(offsets)}",
        f"colors = PackedColorArray({colors})",
        "",
    ])


def _curve_block(e: Emitter) -> str:
    pts = ", ".join(f"Vector2({num(x)}, {num(y)}), 0.0, 0.0, 0, 0" for x, y in e.scale_curve)
    return NL.join([
        f'[sub_resource type="Curve" id="Curve_{e.name}"]',
        f"_data = [{pts}]",
        f"point_count = {len(e.scale_curve)}",
        "",
    ])


def _track(i: int, path: str, times, values: list[str]) -> list[str]:
    return [
        f'tracks/{i}/type = "value"',
        f"tracks/{i}/imported = false",
        f"tracks/{i}/enabled = true",
        f'tracks/{i}/path = NodePath("{path}")',
        f"tracks/{i}/interp = 1",
        f"tracks/{i}/loop_wrap = true",
        f"tracks/{i}/keys = {{",
        f'"times": PackedFloat32Array({", ".join(fnum(t) for t in times)}),',
        f'"transitions": PackedFloat32Array({", ".join(fnum(EASE_IN_OUT) for _ in times)}),',
        '"update": 0,',
        f'"values": [{", ".join(values)}]',
        "}",
    ]


def _animation_blocks() -> str:
    half = BREATH_LENGTH / 2
    q = BREATH_LENGTH / 4
    scale_vals = [vec2((1, 1)), vec2(BREATH_SCALE), vec2((1, 1))]
    pos_vals = [vec2((0, 0)), vec2((SWAY_PX, 0)), vec2((-SWAY_PX, 0)), vec2((0, 0))]
    reset = [
        '[sub_resource type="Animation" id="Animation_reset"]',
        'resource_name = "RESET"',
        "length = 0.001",
        *_track(0, "Splash:scale", [0.0], [vec2((1, 1))]),
        *_track(1, "Splash:position", [0.0], [vec2((0, 0))]),
        "",
    ]
    idle = [
        '[sub_resource type="Animation" id="Animation_select_idle"]',
        f'resource_name = "{ANIMATION}"',
        f"length = {fnum(BREATH_LENGTH)}",
        "loop_mode = 1",
        *_track(0, "Splash:scale", [0.0, half, BREATH_LENGTH], scale_vals),
        *_track(1, "Splash:position", [0.0, q, 3 * q, BREATH_LENGTH], pos_vals),
        "",
        '[sub_resource type="AnimationLibrary" id="AnimationLibrary_select"]',
        "_data = {",
        '&"RESET": SubResource("Animation_reset"),',
        f'&"{ANIMATION}": SubResource("Animation_select_idle")',
        "}",
        "",
    ]
    return NL.join(reset + idle)


def load_loop(char: str) -> dict | None:
    """The rendered loop's manifest entry for `char`, or None (the scene then
    breathes the still, stage 1)."""
    if not LOOP_MANIFEST.exists():
        return None
    return json.loads(LOOP_MANIFEST.read_text(encoding="utf-8")).get(char)


def pingpong(frames: int) -> list[int]:
    """Frame order of one loop: out to the last frame and back to the one
    after the first (the first comes round again), so no frame shows twice
    in a row and the loop has no seam."""
    return list(range(frames)) + list(range(frames - 2, 0, -1))


def _loop_animation_blocks(loop: dict) -> str:
    seq = pingpong(loop["frames"])
    step = 1.0 / loop["fps"]
    length = len(seq) * step
    times = [i * step for i in range(len(seq))]

    def track(vals, times_):
        return [
            'tracks/0/type = "value"',
            "tracks/0/imported = false",
            "tracks/0/enabled = true",
            'tracks/0/path = NodePath("LoopSprite:frame")',
            "tracks/0/interp = 0",
            "tracks/0/loop_wrap = true",
            "tracks/0/keys = {",
            f'"times": PackedFloat32Array({", ".join(fnum(t) for t in times_)}),',
            f'"transitions": PackedFloat32Array({", ".join("1.0" for _ in times_)}),',
            '"update": 1,',
            f'"values": [{", ".join(str(v) for v in vals)}]',
            "}",
        ]
    lines = [
        '[sub_resource type="Animation" id="Animation_reset"]',
        'resource_name = "RESET"',
        "length = 0.001",
        *track([0], [0.0]),
        "",
        '[sub_resource type="Animation" id="Animation_select_idle"]',
        f'resource_name = "{ANIMATION}"',
        f"length = {fnum(length)}",
        "loop_mode = 1",
        *track(seq, times),
        "",
        '[sub_resource type="AnimationLibrary" id="AnimationLibrary_select"]',
        "_data = {",
        '&"RESET": SubResource("Animation_reset"),',
        f'&"{ANIMATION}": SubResource("Animation_select_idle")',
        "}",
        "",
    ]
    return NL.join(lines)


def _loop_sprite(loop: dict) -> str:
    bx, by, _bw, _bh = loop["box"]
    k = 1.0 / loop["scale"]
    return NL.join([
        '[node name="LoopSprite" type="Sprite2D" parent="."]',
        f"position = {vec2((bx, by))}",
        f"scale = {vec2((round(k, 5), round(k, 5)))}",
        'texture = ExtResource("3_loop")',
        "centered = false",
        f"hframes = {loop['grid'][0]}",
        f"vframes = {loop['grid'][1]}",
    ]) + NL


def _emitter_node(e: Emitter) -> str:
    lines = [f'[node name="{e.name}" type="CPUParticles2D" parent="."]']
    if e.additive:
        lines.append('material = SubResource("Material_additive")')
    lines += [
        f"position = {vec2(e.position)}",
        f"amount = {e.amount}",
        f'texture = SubResource("{e.tex}")',
        f"lifetime = {fnum(e.lifetime)}",
        f"preprocess = {fnum(e.lifetime)}",
        "local_coords = true",
        "emission_shape = 3",
        f"emission_rect_extents = {vec2(e.extents)}",
        f"direction = {vec2(e.direction)}",
        f"spread = {fnum(e.spread)}",
        f"gravity = {vec2(e.gravity)}",
        f"initial_velocity_min = {fnum(e.velocity[0])}",
        f"initial_velocity_max = {fnum(e.velocity[1])}",
    ]
    if e.angular_velocity != (0.0, 0.0):
        lines += [f"angular_velocity_min = {fnum(e.angular_velocity[0])}",
                  f"angular_velocity_max = {fnum(e.angular_velocity[1])}"]
    if e.tangential != (0.0, 0.0):
        lines += [f"tangential_accel_min = {fnum(e.tangential[0])}",
                  f"tangential_accel_max = {fnum(e.tangential[1])}"]
    if e.damping != (0.0, 0.0):
        lines += [f"damping_min = {fnum(e.damping[0])}", f"damping_max = {fnum(e.damping[1])}"]
    if e.angle != (0.0, 0.0):
        lines += [f"angle_min = {fnum(e.angle[0])}", f"angle_max = {fnum(e.angle[1])}"]
    if e.align:
        lines.append("particle_flag_align_y = true")
    lines += [f"scale_amount_min = {fnum(e.scale[0])}", f"scale_amount_max = {fnum(e.scale[1])}"]
    if e.scale_curve:
        lines.append(f'scale_amount_curve = SubResource("Curve_{e.name}")')
    lines.append(f'color_ramp = SubResource("Ramp_{e.name}")')
    if e.hue != (0.0, 0.0):
        lines += [f"hue_variation_min = {fnum(e.hue[0])}", f"hue_variation_max = {fnum(e.hue[1])}"]
    return NL.join(lines) + NL


def _texture_rect(name: str, ext: str, extra: list[str]) -> str:
    return NL.join([
        f'[node name="{name}" type="TextureRect" parent="."]',
        "layout_mode = 0",
        f"offset_right = {num(WIDTH)}.0",
        f"offset_bottom = {num(HEIGHT)}.0",
        *extra,
        f'texture = ExtResource("{ext}")',
        "expand_mode = 1",
        "stretch_mode = 6",
    ]) + NL


def render_select_scene(char: str, root: str, tint: tuple[float, float, float, float],
                        element: str, figure_x: float, loop: dict | None = None) -> str:
    """`res://<char>/ui/char_select_bg_<char>.tscn`.

    `figure_x` is the close-up figure's horizontal centre in the 1920x1080
    still: the breath pivots on its bottom centre, and the element's glow
    sits behind it.

    `loop` is the rendered loop's manifest entry (load_loop), or None for
    stage 1: the still breathing on the AnimationPlayer. With it, the Splash
    is the close-up with the moving region cleared (select_closeup_static.png)
    and a Sprite2D steps through the loop's sheet over that region, forward
    then back; the pose carries the breath, so the stage-1 tracks are gone.
    The particles stay on top either way. A loop whose static_file is null
    (the moving box holds the whole figure, so the plate would be blank)
    has no Splash at all: the sheet is the figure.
    """
    el = _element(figure_x)[element]
    behind = [e for e in el.emitters if e.behind]
    front = [e for e in el.emitters if not e.behind]
    subs = [_tex_blocks(t) for t in el.textures]
    subs.append('[sub_resource type="CanvasItemMaterial" id="Material_additive"]\nblend_mode = 1\n')
    for e in el.emitters:
        subs.append(_ramp_block(e))
        if e.scale_curve:
            subs.append(_curve_block(e))
    subs.append(_loop_animation_blocks(loop) if loop else _animation_blocks())
    load_steps = 3 + sum(s.count("[sub_resource") for s in subs)

    art = loop["static_file"] if loop else "select_closeup.png"
    exts = [f'[ext_resource type="Texture2D" path="res://{char}/ui/select_bg.png" id="2_bg"]']
    if art:
        exts.insert(0, f'[ext_resource type="Texture2D" path="res://{char}/ui/{art}" id="1_art"]')
    else:
        load_steps -= 1
    if loop:
        exts.append(f'[ext_resource type="Texture2D" path="res://{char}/ui/{loop["sheet_file"]}" id="3_loop"]')
        load_steps += 1
    head = NL.join([f"[gd_scene load_steps={load_steps} format=3]", "", *exts, ""])
    root_node = NL.join([
        f'[node name="{root}" type="Control"]',
        "layout_mode = 3",
        "anchors_preset = 8",
        "anchor_left = 0.5",
        "anchor_top = 0.5",
        "anchor_right = 0.5",
        "anchor_bottom = 0.5",
        "offset_left = -960.0",
        "offset_top = -540.0",
        "offset_right = 960.0",
        "offset_bottom = 540.0",
        "grow_horizontal = 2",
        "grow_vertical = 2",
        "pivot_offset = Vector2(960, 540)",
        "",
    ])
    nodes = [root_node,
             _texture_rect("Backdrop", "2_bg", []).replace(
                 "stretch_mode = 6\n", f"stretch_mode = 6\nself_modulate = {color(tint)}\n")]
    nodes += [_emitter_node(e) for e in behind]
    if art:
        nodes.append(_texture_rect("Splash", "1_art", [f"pivot_offset = {vec2((figure_x, HEIGHT))}"]))
    if loop:
        nodes.append(_loop_sprite(loop))
    nodes += [_emitter_node(e) for e in front]
    nodes.append(NL.join([
        '[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
        "libraries = {",
        '&"": SubResource("AnimationLibrary_select")',
        "}",
        f'autoplay = "{ANIMATION}"',
        "",
    ]))
    return head + NL + NL.join(subs) + NL + NL.join(nodes)
