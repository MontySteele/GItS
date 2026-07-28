#!/usr/bin/env python3
"""Generate the Salon role-chip glyphs (Tier O, procedural).

D1's role chip is "glyph + live tick value" under each member: the glyph says
WHAT the member does (sword = damage, shield = block, droplet = hydro
application) and the number says how much it does right now.

These are drawn here rather than fetched because they are pure geometry --
there is no wiki art for "a small sword icon", and a Tier F crop would be
both wrong for the job and undistributable. Registered in
art_lint.GENERATOR_OWNED so no plan row can claim these out-paths.

WHITE ON TRANSPARENT, deliberately. The bridge tints each chip with its
member's accent hue through Sprite2D.Modulate, which means one master per
role serves every hue AND the dry state greys the glyph for free by the same
modulate path that greys the sprite. A pre-tinted master would need three
files per role and a fourth for dry, all of which would go stale the first
time a hue is adjusted.

Deterministic (no randomness at all) so the pck build is reproducible.

Usage: .venv/Scripts/python tools/gen_salon_glyphs.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ImageGen" / "images" / "furina" / "salon"

# 4x the on-screen size. The chip renders around 8px tall in combat, and
# downscaling a 32px master is what keeps the diagonal edges of the sword
# from stairstepping at the size the player actually sees.
SIZE = 32
SS = 4                      # supersample factor for the draw pass
WHITE = (255, 255, 255, 255)


def _canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (255, 255, 255, 0))
    return img, ImageDraw.Draw(img)


def _finish(img: Image.Image, name: str) -> None:
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name)
    print(f"  wrote {name}")


def _scaled(points):
    """Author every shape in 0..16 glyph units; the canvas is SIZE*SS."""
    k = SIZE * SS / 16.0
    return [(x * k, y * k) for x, y in points]


def sword() -> None:
    """Crabaletta's role: damage. A blade on the rising diagonal with a short
    guard, which reads as a weapon at chip size where a detailed hilt does
    not."""
    img, d = _canvas()
    # Blade: a 45-degree bar with a pointed tip at the top right. The point
    # is what separates this from the shield's mass at 10px -- an unpointed
    # bar reads as a stick.
    #
    # Everything here is deliberately CHUNKY. The first cut was drawn at
    # true sword proportions and disappeared at chip size -- a 1-unit blade
    # is a quarter of a pixel once the master is downscaled to ~10px, which
    # is a glyph that technically exists.
    #
    # The blade is a PARALLEL-SIDED quad with a separate tip triangle, not
    # one polygon that tapers along its length. A tapering polygon looked
    # right at 128px and vanished at 10px, because most of its area was the
    # half-unit-wide end.
    d.polygon(_scaled([(3.6, 10.4), (10.6, 3.4), (12.6, 5.4), (5.6, 12.4)]),
              fill=WHITE)
    d.polygon(_scaled([(10.4, 3.2), (12.8, 5.6), (15.2, 0.8)]), fill=WHITE)
    # Crossguard: perpendicular to the blade, i.e. along the OTHER diagonal.
    d.polygon(_scaled([(2.8, 9.6), (6.0, 12.8), (5.0, 13.8), (1.8, 10.6)]),
              fill=WHITE)
    # Grip: the blade axis continued below the guard, ending in a pommel.
    d.polygon(_scaled([(1.0, 14.4), (3.4, 12.0), (4.4, 13.0), (2.0, 15.4)]),
              fill=WHITE)
    _finish(img, "glyph_damage.png")


def shield() -> None:
    """Usher's role: block. The game's own Block badge is a shield, so this
    borrows the silhouette the player has already learned."""
    img, d = _canvas()
    d.polygon(_scaled([(8, 1.2), (14, 3.2), (14, 7.6), (11.6, 12.4),
                       (8, 15.0), (4.4, 12.4), (2, 7.6), (2, 3.2)]),
              fill=WHITE)
    _finish(img, "glyph_block.png")


def droplet() -> None:
    """Chevalmarin's role: hydro application. A teardrop -- the same shape
    the aura badge uses, at a size where only the silhouette survives."""
    img, d = _canvas()
    d.polygon(_scaled([(8, 1.0), (10.6, 5.2), (12.2, 8.4), (12.2, 10.6),
                       (10.4, 13.4), (8, 14.4), (5.6, 13.4), (3.8, 10.6),
                       (3.8, 8.4), (5.4, 5.2)]),
              fill=WHITE)
    _finish(img, "glyph_support.png")


def main() -> None:
    print("salon role-chip glyphs ->", OUT)
    sword()
    shield()
    droplet()


if __name__ == "__main__":
    main()
