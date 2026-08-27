"""Draw the synthetic rig's layers.

Every pixel here is generated from primitives at run time -- ellipse, capsule,
rounded box, diamond -- so the bake-off carries no game, Genshin, fetched, or
licensed art of any kind, and the whole corpus regenerates from this file.

Determinism is a measured property of this lane, so the drawing is
deterministic by construction: no randomness, no timestamps, fixed 4x
supersample-then-box-filter for edges, and Pillow's default PNG writer with
`optimize=False` (which emits no tIME chunk).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from .spec import PARTS, Part

#: Supersample factor. 4 is enough to hide the stair-steps at these sizes and
#: keeps the biggest intermediate under 400x400.
SS = 4

#: Padding around each part, in final pixels. Rotation happens about the
#: sprite centre, so a part needs slack or its corners clip on a spin track.
PAD = 6


def _draw_shape(draw: ImageDraw.ImageDraw, part: Part, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    color = part.color
    if part.shape == "ellipse":
        draw.ellipse(box, fill=color)
    elif part.shape == "capsule":
        radius = (x1 - x0) // 2
        draw.rounded_rectangle(box, radius=radius, fill=color)
    elif part.shape == "roundrect":
        radius = max(4 * SS, (x1 - x0) // 5)
        draw.rounded_rectangle(box, radius=radius, fill=color)
    elif part.shape == "diamond":
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        draw.polygon([(cx, y0), (x1, cy), (cx, y1), (x0, cy)], fill=color)
    else:  # pragma: no cover - the Literal keeps this unreachable
        raise ValueError(f"unknown shape {part.shape!r}")


def render_part(part: Part) -> Image.Image:
    """One RGBA layer, `part.size` plus `PAD` on every side."""
    w = part.size[0] + 2 * PAD
    h = part.size[1] + 2 * PAD
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(big)
    box = (
        PAD * SS,
        PAD * SS,
        (PAD + part.size[0]) * SS - 1,
        (PAD + part.size[1]) * SS - 1,
    )
    _draw_shape(draw, part, box)
    return big.resize((w, h), Image.LANCZOS)


def render_composite() -> Image.Image:
    """The whole figure flattened into one billboard.

    The particles/tweens approach animates a single body rather than eight
    layers; without this it would have nothing to animate, and comparing it
    against the layered rig would be comparing a different subject.
    """
    parts = sorted(PARTS, key=lambda p: p.z)
    xs: list[float] = []
    ys: list[float] = []
    for part in parts:
        w = part.size[0] + 2 * PAD
        h = part.size[1] + 2 * PAD
        xs += [part.rest[0] - w / 2, part.rest[0] + w / 2]
        ys += [part.rest[1] - h / 2, part.rest[1] + h / 2]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    canvas = Image.new("RGBA", (int(right - left), int(bottom - top)), (0, 0, 0, 0))
    for part in parts:
        layer = render_part(part)
        px = int(part.rest[0] - layer.width / 2 - left)
        py = int(part.rest[1] - layer.height / 2 - top)
        canvas.alpha_composite(layer, (px, py))
    return canvas


#: Everything this module can produce. `composite` and `mote` are the
#: particle approach's inputs; the rest are the layer approaches'.
ALL_LAYERS: tuple[str, ...] = tuple(p.name for p in PARTS) + ("composite", "mote")


def write_layers(out_dir: Path, want: set[str] | None = None) -> dict[str, Path]:
    """Write the requested layers. Returns name -> path.

    `want` matters for package cost, not for tidiness: the export preset every
    project here uses is `export_filter="all_resources"` -- the same one
    `tools/build_pck.ps1:97` uses -- so ANY png sitting in the project ships in
    the pack whether a scene references it or not. Measured on a first run that
    generated all layers into every project: the layered pack carried
    `sprig_composite.ctex` (6032 B) and `sprig_mote.ctex` (94 B) that its scene
    never names. Writing only what an approach references keeps the four
    package numbers comparable.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    selected = set(ALL_LAYERS) if want is None else set(want)
    unknown = selected - set(ALL_LAYERS)
    if unknown:
        raise ValueError(f"unknown layer(s): {sorted(unknown)}")

    written: dict[str, Path] = {}
    for part in PARTS:
        if part.name not in selected:
            continue
        path = out_dir / f"sprig_{part.name}.png"
        render_part(part).save(path, "PNG", optimize=False)
        written[part.name] = path
    if "composite" in selected:
        composite = out_dir / "sprig_composite.png"
        render_composite().save(composite, "PNG", optimize=False)
        written["composite"] = composite
    if "mote" in selected:
        # A 4x4 white square is the particle billboard. Generating it rather
        # than reusing a part layer keeps the particle approach's inputs
        # honest: it needs a mote texture no other approach needs.
        mote = out_dir / "sprig_mote.png"
        Image.new("RGBA", (4, 4), (255, 255, 255, 255)).save(mote, "PNG", optimize=False)
        written["mote"] = mote
    return written


def layer_size(part: Part) -> tuple[int, int]:
    """Final pixel size of a part's layer, padding included."""
    return part.size[0] + 2 * PAD, part.size[1] + 2 * PAD
