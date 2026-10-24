#!/usr/bin/env python3
"""Generate the three REACTION power badges at full badge size (derived, procedural).

WHAT THIS IS FOR. Aftershock (Klee), Grand Strategist (Kokomi) and All Four
Winds (Varka) wore the wiki's reaction icons ("Pyro x Electro", "Pyro x
Hydro", four elements in a square). Fitted into a 256 square those are rows
of glyphs about half the height of a base badge, and at game size beside
Strength and Vulnerable they read as two dots (live look 2026-10-23).
[USER] picked one bold symbol per badge ("Sounds good - let's do (a)") and
approved these drafts ("These all look good!", 2026-10-24).

ONE ELEMENT MARK, FULL SIZE, PLUS A FRAME OF ITS OWN. The mark alone would be
the enemy element aura badge (`powers/aura_<element>.png`), so each badge
wears a frame that says what the power does:

  * Aftershock       -- the Pyro mark in a broken shockwave ring: a blast
                        that sets off another blast.
  * Grand Strategist -- the Hydro mark in a burst of eight short rays: each
                        reaction hits ALL enemies.
  * All Four Winds   -- the Anemo mark in a ring of the four Oath colours
                        (Pyro, Hydro, Electro, Cryo): every Oath read
                        together.

A dark outline round the whole badge, as the base badges have, keeps it off
a busy board. The marks are the aura badges themselves, so run art_process
first; this script reads `ImageGen/images/powers/aura_{pyro,hydro,anemo}.png`.
Deterministic, so the pck build is reproducible.

Usage: .venv/Scripts/python tools/gen_reaction_badges.py
       .venv/Scripts/python tools/gen_reaction_badges.py --sheet OUT.png
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "ImageGen" / "images"
N = 256
SS = 4  # supersampling for the frames

OUTS = {
    "aftershock": IMAGES / "powers" / "aftershock.png",
    "grand_strategist": IMAGES / "kokomi" / "powers" / "grand_strategist.png",
    "all_four_winds": IMAGES / "varka" / "powers" / "all_four_winds.png",
}


def _mark(element: str, size: int) -> Image.Image:
    src = IMAGES / "powers" / f"aura_{element}.png"
    return Image.open(src).convert("RGBA").resize((size, size), Image.LANCZOS)


def _frame(draw_fn) -> Image.Image:
    big = Image.new("RGBA", (N * SS, N * SS), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), N * SS / 2)
    return big.resize((N, N), Image.LANCZOS)


def _finish(frame: Image.Image, mark: Image.Image) -> Image.Image:
    frame.alpha_composite(mark, ((N - mark.width) // 2, (N - mark.height) // 2))
    edge = frame.split()[3].filter(ImageFilter.MaxFilter(13))
    out = Image.new("RGBA", (N, N), (20, 16, 24, 0))
    out.putalpha(edge.point(lambda v: min(v, 230)))
    out.alpha_composite(frame)
    return out


def aftershock() -> Image.Image:
    def ring(d, c):
        r, w = 120 * SS, 15 * SS
        for start in (-60, 30, 120, 210):
            d.arc((c - r, c - r, c + r, c + r), start, start + 70,
                  fill=(255, 196, 120, 255), width=w)
    return _finish(_frame(ring), _mark("pyro", 184))


def grand_strategist() -> Image.Image:
    def rays(d, c):
        r0, r1, w = 104 * SS, 126 * SS, 14 * SS
        for k in range(8):
            t = math.radians(k * 45 + 22.5)
            d.line((c + r0 * math.cos(t), c + r0 * math.sin(t),
                    c + r1 * math.cos(t), c + r1 * math.sin(t)),
                   fill=(150, 230, 255, 255), width=w)
    return _finish(_frame(rays), _mark("hydro", 180))


def all_four_winds() -> Image.Image:
    oath = [(255, 140, 80), (0, 190, 255), (210, 150, 255), (170, 235, 245)]

    def ring(d, c):
        r, w = 120 * SS, 15 * SS
        for k, col in enumerate(oath):
            s = -90 + k * 90 + 8
            d.arc((c - r, c - r, c + r, c + r), s, s + 74, fill=col + (255,), width=w)
    return _finish(_frame(ring), _mark("anemo", 184))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sheet", type=Path,
                    help="also write a review sheet: masters, then 64 and 40 px")
    args = ap.parse_args()

    made = {"aftershock": aftershock(), "grand_strategist": grand_strategist(),
            "all_four_winds": all_four_winds()}
    for name, img in made.items():
        OUTS[name].parent.mkdir(parents=True, exist_ok=True)
        img.save(OUTS[name])
        print(f"  wrote {OUTS[name].relative_to(ROOT)}")
    if args.sheet:
        sheet = Image.new("RGBA", (3 * 276, N + 80), (36, 34, 44, 255))
        for i, img in enumerate(made.values()):
            sheet.alpha_composite(img, (i * 276, 0))
            sheet.alpha_composite(img.resize((64, 64), Image.LANCZOS), (i * 276, N + 8))
            sheet.alpha_composite(img.resize((40, 40), Image.LANCZOS), (i * 276 + 80, N + 32))
        sheet.save(args.sheet)
        print(f"  wrote {args.sheet}")


if __name__ == "__main__":
    main()
