#!/usr/bin/env python3
"""Generate the METER COST BADGE glyphs for Encore and Charge (Tier O, procedural).

WHAT THIS IS FOR. `Vfx/MeterCostBadge.cs` paints a card's meter price into the
base game's own second-cost slot (`%StarIcon` / `%StarLabel`). Sparks wear
Klee's `klee/powers/spark.png` there -- the icon her counter already wears --
so a Spark price says SPARK and never STAR. Encore and Charge shipped with NO
glyph at all: the badge hid the icon and painted a bare coloured number, and
the two meters' numbers are both cyan-adjacent (the Salon ribbon's fill and
the Charge gauge's fill), so nothing but hue separated them. R225 item 5,
[USER]: "I would prefer glyphs regardless, let's do it now."

DRAWN HERE RATHER THAN FETCHED, for the reason `gen_salon_glyphs.py` gives:
these are pure geometry. There is no wiki illustration of "the Encore meter"
or "the Charge meter" -- they are OUR systems, not Genshin ones -- and a Tier F
crop of a character render would be both wrong for the job (a portrait does not
survive a 30px cost slot) and undistributable. Registered in
art_lint.GENERATOR_OWNED so no plan row can claim these out-paths.

SILHOUETTE FIRST, HUE SECOND. The badge is read at roughly the size of the
energy orb's number, and at that size hue is the thing a colour-blind player
loses and a busy board hides. So the three glyphs are separated by SHAPE:

  * Sparks   -- a round five-petal bloom (Klee's own, unchanged here).
  * Encore   -- a stage CURTAIN: a swagged valance with two tied-back drapes
                under it. Wide and flat across the top, and the only glyph in
                the set with a HOLE in it -- the stage opening between the
                drapes -- which is what carries it at 16px.
  * Charge   -- a DROPLET FILLED TO A LINE: pointed at the top, round at the
                bottom, with the lower two thirds bright and the top third
                sunk back. That is the gauge it spends, drawn as a level, and
                the pointed apex is what no other glyph in the set has.

COMPOSITION MATCHES SPARK, because these three sit in the same slot on
different cards and a mismatched pair would read as one of them being broken:
a soft dark disc, alpha feathering from ~r70 to the edge, with a two-tone motif
over it (bright fill, darker rim). Sampled off `spark.png` itself -- disc
~(150,65,65) at alpha 254 in the middle and 53 at r112, motif fill (234,124,123)
over a (168,54,54) rim -- and re-expressed as ratios of each meter's own colour
so the disc, the motif and the NUMBER beside it all sit on one hue.

The hues are the badge's own `ColorFor`, i.e. the values the Salon stage ribbon
(`furina/ui/salon_stage.tscn`, %Seg1) and the Charge gauge (`GaugeBridge`, the
`kokomi_charge` spec) are already drawn with. One edit moves both if [USER]
moves a meter's colour.

256x256 masters, matching every other file in `<character>/powers/`; the pck
build copies those directories wholesale, so no build_pck edit is needed.
Deterministic (no randomness) so the pck build is reproducible.

Usage: .venv/Scripts/python tools/gen_meter_glyphs.py
       .venv/Scripts/python tools/gen_meter_glyphs.py --sheet   (+ review page)
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "ImageGen" / "images"
SHEET = ROOT / "art" / "contact_sheet_eb220_meter_glyphs.html"

SIZE = 256                  # the size every other powers/ master ships at
SS = 4                      # supersample factor for the motif draw pass
UNITS = 16.0                # author every shape in 0..16 glyph units

# MeterCostBadge.ColorFor, verbatim. Encore = the Salon ribbon's fill,
# Charge = the second-row gauge's fill.
ENCORE = (0.35, 0.75, 1.00)
CHARGE = (0.44, 0.78, 0.84)


def _mix(color, target, t):
    return tuple(round(c + (b - c) * t) for c, b in zip(color, target))


def _rgb(hue, value, saturation):
    """A meter hue at a given brightness, desaturated toward grey.

    `saturation` 1.0 keeps the hue as authored; lower values pull it toward
    neutral, which is what the disc needs -- spark.png's backdrop is a
    desaturated dark version of its own pink, not a second bright shape.
    """
    lit = tuple(min(255, round(c * 255 * value)) for c in hue)
    grey = round(sum(lit) / 3)
    return _mix(lit, (grey, grey, grey), 1.0 - saturation)


def _disc(hue):
    """The soft dark backdrop, at final resolution.

    Alpha is flat across the middle and feathers from r=70 to the edge, which
    is spark.png's own falloff (254 at r68, 191 at r88, 120 at r108, 53 at
    r112). Built per pixel rather than with a blur so the profile is stated
    rather than tuned.
    """
    body = _rgb(hue, 0.62, 0.42)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    px = img.load()
    mid = (SIZE - 1) / 2.0
    flat, edge = 70.0, 127.0
    for y in range(SIZE):
        for x in range(SIZE):
            r = math.hypot(x - mid, y - mid)
            if r >= edge:
                continue
            if r <= flat:
                a = 254
            else:
                t = (r - flat) / (edge - flat)
                a = round(254 * (1.0 - t) ** 1.35)
            px[x, y] = (*body, a)
    return img


def _canvas():
    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _s(points):
    k = SIZE * SS / UNITS
    return [(x * k, y * k) for x, y in points]


def _bez(a, b, c, steps=24):
    """A quadratic Bezier from a to c bending toward b, as points.

    Both glyphs are CURVED shapes, and the first cut of this file drew them as
    sparse polygons: the droplet came out a hexagonal gem and the curtain came
    out a pair of trousers. Sampling the curve is the fix -- the outline is
    authored as control points and expanded here, so the silhouette survives
    the LANCZOS downscale to badge size instead of stairstepping into facets.
    """
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1])
            for t in (i / steps for i in range(steps + 1))]


def _shape(draw, points, fill, rim):
    """A filled polygon with a darker rim, the two-tone spark.png wears.

    The rim is drawn as a wide outline on the SAME polygon, so it eats into
    the shape rather than growing it -- a glyph that grows by its rim loses
    the gap in the curtain, which is the whole silhouette.
    """
    pts = _s(points)
    draw.polygon(pts, fill=fill)
    draw.line(pts + [pts[0]], fill=rim, width=round(SIZE * SS / UNITS * 0.42),
              joint="curve")


def _finish(motif, hue, out: Path) -> None:
    motif = motif.resize((SIZE, SIZE), Image.LANCZOS)
    img = _disc(hue)
    img.alpha_composite(motif)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"  wrote {out.relative_to(ROOT)}  ({SIZE}x{SIZE})")


def encore() -> Path:
    """Furina's Encore: a stage curtain.

    A swagged valance across the top and two tied-back drapes under it.
    CHUNKY on purpose, the lesson gen_salon_glyphs.py records: a curtain drawn
    at true proportions is a set of thin folds, and thin folds are a glyph that
    technically exists. Three things have to survive the downscale -- the flat
    top, the two drapes, and the opening between them.
    """
    fill = _rgb(ENCORE, 1.00, 1.00)
    rim = _rgb(ENCORE, 0.52, 0.90)
    img, d = _canvas()

    # A drape, TIED BACK: it meets the valance, is pulled OUT at the tie about
    # two fifths down, and falls back to a hem well above the bottom of the
    # frame. The gap between the two is therefore an EYE -- widest at the tie,
    # closing above and below -- and that hole is what the eye picks up at
    # 16px, far more reliably than any fold detail inside the cloth.
    #
    # THE GAP IS WIDE ON PURPOSE. The first cut hung two straight-sided legs
    # from a full-width bar with a narrow slot between them and read as a pair
    # of TROUSERS: same silhouette, same waistband. A stage opening that is
    # wider than either drape is what stops that, so the drapes are narrow, the
    # opening is over half the width at the tie, and the hems stop short.
    def drape(sign):
        x = lambda u: 8.0 + sign * u          # noqa: E731  (mirror about x=8)
        outer = _bez((x(6.7), 3.4), (x(7.0), 9.0), (x(5.9), 13.6))
        hem = _bez((x(5.9), 13.6), (x(4.5), 14.9), (x(2.7), 13.1))
        inner = _bez((x(2.7), 13.1), (x(4.7), 9.2), (x(2.9), 3.4))
        _shape(d, outer + hem + inner, fill, rim)

    drape(-1)
    drape(+1)

    # Valance, drawn AFTER the drapes so it overlaps them the way a pelmet
    # hangs in front of the cloth. Its bottom edge is SCALLOPED into three
    # swags: a plain bar is a waistband, and three swags is the shape the word
    # "theatre" is drawn with everywhere else.
    top = [(1.2, 1.6), (14.8, 1.6), (14.8, 3.6)]
    swags = []
    for i in range(3):
        x0 = 14.8 - i * 4.533
        swags += _bez((x0, 3.6), (x0 - 2.27, 6.1), (x0 - 4.533, 3.6), steps=16)
    _shape(d, top + swags + [(1.2, 3.6)], fill, rim)

    out = IMAGES / "furina" / "powers" / "encore.png"
    _finish(img, ENCORE, out)
    return out


def charge() -> Path:
    """Kokomi's Charge: a droplet filled to a line.

    The droplet is the shape the game's own hydro badge uses, so the meter
    reads as HERS; the fill line is what makes it a METER rather than an aura.
    The level is drawn at two thirds because a half-full droplet reads as a
    two-tone accident and a nearly-full one reads as a solid shape.
    """
    fill = _rgb(CHARGE, 1.00, 1.00)
    rim = _rgb(CHARGE, 0.50, 0.90)
    sunk = _rgb(CHARGE, 0.58, 0.55)
    # Apex, then one flank down to the round belly and back up the other:
    # a pointed top over a near-circular bottom, sampled off two Beziers so
    # the flanks are FLAT-ish where the eye reads the point and the bottom is
    # genuinely round. A ten-point polygon of the same outline came out a
    # faceted gem.
    body = (_bez((8.0, 0.9), (10.4, 5.0), (12.6, 9.4))
            + _bez((12.6, 9.4), (12.6, 14.2), (8.0, 15.1))
            + _bez((8.0, 15.1), (3.4, 14.2), (3.4, 9.4))
            + _bez((3.4, 9.4), (5.6, 5.0), (8.0, 0.9)))

    img, d = _canvas()
    _shape(d, body, sunk, rim)

    # The level. Clipped to the droplet by drawing the bright body into a
    # scratch layer and pasting only the band below the line, so the fill
    # cannot spill past the silhouette at any level.
    lit, ld = _canvas()
    _shape(ld, body, fill, rim)
    k = SIZE * SS / UNITS
    band = lit.crop((0, round(7.4 * k), SIZE * SS, SIZE * SS))
    img.alpha_composite(band, (0, round(7.4 * k)))

    out = IMAGES / "kokomi" / "powers" / "charge.png"
    _finish(img, CHARGE, out)
    return out


SHEET_HTML = """<!doctype html>
<meta charset="utf-8">
<title>EB-220 meter glyphs -- contact sheet</title>
<style>
 body {{ background:#1b1b20; color:#ddd; font:14px/1.5 system-ui, sans-serif;
        margin:32px; }}
 h1 {{ font-size:18px; }} p {{ max-width:60em; color:#aaa; }}
 table {{ border-collapse:collapse; margin-top:18px; }}
 th, td {{ padding:10px 16px; text-align:center; border-bottom:1px solid #333; }}
 th {{ color:#888; font-weight:normal; }}
 td.n {{ text-align:left; color:#eee; }}
 .card {{ background:#3a3630; padding:8px; border-radius:4px; display:inline-block; }}
 img {{ image-rendering:auto; vertical-align:middle; }}
</style>
<h1>EB-220 -- Encore and Charge wear a glyph</h1>
<p>The meter cost badge sits in the base game's second-cost slot, beside the
energy orb. Column headings are the on-card pixel sizes to judge at; the last
column is the master. Sparks is the SHIPPED glyph and is here as the control:
the two new ones have to be distinguishable from it, and from each other, in
silhouette rather than in hue.</p>
<table>
<tr><th></th><th>16px</th><th>24px</th><th>32px</th><th>48px</th><th>master</th></tr>
{rows}
</table>
"""


def sheet(paths) -> None:
    rows = []
    for name, path in paths:
        rel = "../" + str(path.relative_to(ROOT)).replace("\\", "/")
        cells = "".join(
            f'<td><span class="card"><img src="{rel}" width="{w}" '
            f'height="{w}"></span></td>' for w in (16, 24, 32, 48))
        rows.append(f'<tr><td class="n">{name}</td>{cells}'
                    f'<td><img src="{rel}" width="128" height="128"></td></tr>')
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text(SHEET_HTML.format(rows="\n".join(rows)), encoding="utf-8")
    print(f"  wrote {SHEET.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sheet", action="store_true",
                    help="also write the review contact sheet (gitignored)")
    args = ap.parse_args()

    print("meter cost badge glyphs ->", IMAGES)
    made = [("Encore (furina/powers/encore.png)", encore()),
            ("Charge (kokomi/powers/charge.png)", charge())]
    if args.sheet:
        sheet([("Sparks -- SHIPPED control (klee/powers/spark.png)",
                IMAGES / "powers" / "spark.png")] + made)


if __name__ == "__main__":
    main()
