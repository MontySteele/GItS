#!/usr/bin/env python3
"""Generate the Mods-screen identity badge, res://klee/mod_image.png (EB-161).

`NModInfoContainer` loads `res://<mod id>/mod_image.png` if it exists and
otherwise leaves the texture null (docs/current/BACKLOG.md EB-161; the finding
is dispatch3's S20 P5) -- unlike every other UI surface this repo ships, that
path is the pck ROOT, not `<mod id>/ui/...`, which is why this is its own
out-path and its own copy block in tools/build_pck.ps1, not a plan.tsv row
under ui/.

SIZE, MEASURED NOT ASSUMED. Nothing in this repo's reach (no game_ref
decompile, no local mod install) states the pixel size `NModInfoContainer`
expects. `lamali292/Downfall` (pinned in review/dispatch3/s12-public-patterns
as the reference public StS2 mod, and its `mod_image.png` cited by name in the
S20 P5 finding) is a real, released mod on that same screen; its five submod
badges plus its own top-level badge are byte-measured 420x420 (Champ,
Guardian, Hexaghost, Automaton, Awakened, and Downfall itself, fetched via
`gh api repos/lamali292/Downfall/contents/<name>/mod_image.png?ref=32e6113`
and opened with Pillow, 2026-09-02) -- six for six, so treated as the shipped
convention rather than one mod's private choice.

WHY A COMPOSITE, AND WHY select_portrait AND NOT selection_splash.
"Teyvat Spire Roster" (Klee/manifest.json name) bundles three characters, so
a single badge naming only one of them undersells what installing this mod
gets you -- unlike Downfall's badges, which are one submod each. The three
existing `<character>/ui/select_portrait.png` files (already GENERATOR_OWNED
by gen_furina_stills.py / gen_kokomi_stills.py for Furina and Kokomi, and by
art/plan.tsv's `select_portrait` row for Klee) are EXACTLY this problem
already solved once: a small per-character identity thumbnail, framed on the
face, meant to sit in a list next to text -- the character-select row is the
same shape of screen as the Mods row. `selection_splash.png` was tried first
and rejected on inspection: Furina's and Kokomi's canvases are 1920x1200 with
the character living in a narrow off-center band (Furina's opaque bbox is
x:348-972 of 1920; a geometric-center square crop caught mostly padding and
the top of her GENSHIN IMPACT wordmark instead of her face), which a
select_portrait crop never has to fight because it is already tightly framed.

Deterministic (no randomness): three already-produced, already-approved
crops, top-anchored to a square (the face sits at the top of a select_portrait
image in every one of the three, by the same convention that anchors Klee's
own select_portrait plan row 'top'), scaled to 420 and cut into three equal
vertical bands in roster order -- Klee (the mod id and its namesake), then
Furina, then Kokomi.

Registered in art_lint.GENERATOR_OWNED so no plan row can claim this path,
same as every other derived UI surface. Tier F: the three source crops are
Tier F art/SOURCES.tsv (or GENERATOR_OWNED) provenance, and a composite of
Tier F pixels is not cleaner than its inputs.

Usage: .venv/Scripts/python tools/gen_mod_image.py [--check]
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SIZE = 420

# roster order: Klee is the mod id and its namesake, then Furina, then Kokomi
# -- the same order Klee/manifest.json's description names the roster in.
SOURCES = {
    "klee":   "ImageGen/images/ui/select_portrait.png",
    "furina": "ImageGen/images/furina/ui/select_portrait.png",
    "kokomi": "ImageGen/images/kokomi/ui/select_portrait.png",
}
OUT = "ImageGen/images/mod_image.png"


def top_square(im: Image.Image, size: int) -> Image.Image:
    """Top-anchored square crop, scaled to `size`.

    select_portrait sources frame the face near the top of a taller-than-wide
    canvas (art/plan.tsv anchors Klee's own row 'top' for the same reason), so
    a top-anchored square keeps the face and drops leg/hem instead of the
    reverse.
    """
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    cropped = im.crop((left, 0, left + side, side))
    return cropped.resize((size, size), Image.LANCZOS)


def build() -> Image.Image | None:
    """The 420x420 triptych, or None if a source is missing."""
    order = list(SOURCES)
    strip_w = SIZE // len(order)
    band_left = (SIZE - strip_w) // 2
    composite = Image.new("RGB", (strip_w * len(order), SIZE), (255, 255, 255))
    for i, name in enumerate(order):
        src = ROOT / SOURCES[name]
        if not src.exists():
            print(f"SKIPPED: mod_image -- no {name} source at {SOURCES[name]}")
            return None
        im = Image.open(src).convert("RGBA")
        sq = top_square(im, SIZE).convert("RGB")
        band = sq.crop((band_left, 0, band_left + strip_w, SIZE))
        composite.paste(band, (i * strip_w, 0))
    return composite.resize((SIZE, SIZE), Image.LANCZOS)


def main(argv):
    check = "--check" in argv[1:]
    img = build()
    if img is None:
        # Tier F art is gitignored and absent on a fresh clone / CI runner --
        # the same tolerance every other generator in this file gives.
        return 0
    out_path = ROOT / OUT
    if check:
        if not out_path.exists():
            print(f"STALE: {OUT} does not exist", file=sys.stderr)
            return 1
        have = Image.open(out_path).convert("RGB")
        if have.tobytes() != img.tobytes():
            print(f"STALE: {OUT} differs from a fresh derivation", file=sys.stderr)
            return 1
        print(f"gen_mod_image --check: OK ({SIZE}x{SIZE})")
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"wrote {out_path} ({img.width}x{img.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
