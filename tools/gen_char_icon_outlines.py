#!/usr/bin/env python3
"""Generate the top-panel character-icon OUTLINE textures (derived, procedural).

`CharacterModel.IconOutlineTexture` is a real base-game surface -- it is read
by `NMultiplayerVoteContainer` (the co-op vote icon's "Outline" TextureRect)
and by `NAncientDialogueLine` ("Icon/Outline"). All three of our characters
returned the FILL `char_icon.png` for it, which is why both surfaces rendered
the icon twice instead of icon-over-halo (EB-37).

WHAT AN OUTLINE ACTUALLY IS HERE -- measured, not assumed
--------------------------------------------------------
Read out of the shipped game pack (`SlayTheSpire2.pck`, v0.107.1) by decoding
`images/ui/top_panel/character_icon_ironclad_outline.png` and its fill twin:

    fill     85x85 (padded to 88x88 for block compression), BC7, full colour
    outline  85x85 (same padding), DXT5, RGB is (255,255,255) at EVERY pixel

So it is not a stroke and not an edge detect. It is the fill's own silhouette,
re-emitted as PURE WHITE with the shape carried entirely by alpha, grown
outward so it reads as a halo behind the icon:

    fill opaque pixels          2924
    outline opaque pixels       4007
    fill pixels NOT covered        0   (the outline is a strict superset)
    best circular dilation      r = 4..5 px on an 85px canvas (r=4 leaves 115
                                outline pixels uncovered and adds none; r=5
                                covers all but 3 and adds 196)

`OUTLINE_RADIUS_FRAC` below is that measurement expressed against the canvas
(4.5 / 85), so it stays right if an icon is ever authored at another size.

The dilation runs on the GRAYSCALE alpha (max over a circular neighbourhood),
not on a binarised mask, which keeps the source's antialiased edge instead of
manufacturing a hard one.

INPUTS are the three shipped fills. Klee's historical layout is
ImageGen/images/ui/; Furina and Kokomi use ImageGen/images/<character>/ui/,
the same split `build_pck.ps1` and `art_lint.GENERATOR_OWNED` already carry.

Outputs are not in art/plan.tsv because they are DERIVED, not wiki-sourced --
the same arrangement `gen_transition_wipe.py` uses. `build_pck.ps1` picks them
up from the ui/ dirs like every other ui texture, and all three paths are
registered in `art_lint.GENERATOR_OWNED` so no plan row can claim them.

Deterministic: same fill in, same bytes out.

Usage: .venv/Scripts/python tools/gen_char_icon_outlines.py [--check]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# 4.5px of dilation on the base game's 85px icon canvas. Expressed as a
# fraction so an icon authored at another size gets the same visual weight.
OUTLINE_RADIUS_FRAC = 4.5 / 85

# character -> (fill path, outline path). Klee's historical ImageGen layout has
# no character segment; see build_pck.ps1's "Klee's historical art layout"
# block, which this deliberately mirrors rather than normalising.
ICONS = {
    "klee":   ("ImageGen/images/ui/char_icon.png",
               "ImageGen/images/ui/char_icon_outline.png"),
    "furina": ("ImageGen/images/furina/ui/char_icon.png",
               "ImageGen/images/furina/ui/char_icon_outline.png"),
    "kokomi": ("ImageGen/images/kokomi/ui/char_icon.png",
               "ImageGen/images/kokomi/ui/char_icon_outline.png"),
}


def circular_dilate(alpha: np.ndarray, radius: int) -> np.ndarray:
    """Grayscale morphological dilation over a disc of `radius` pixels.

    Grayscale rather than binary on purpose: the fills are antialiased cutouts,
    and a binarised dilation would hand back a hard-edged halo that reads as a
    jaggy at 88px. Shifting the whole array per offset is O(r^2) array ops on a
    ~88x88 image -- trivial, and it avoids a scipy dependency the repo does not
    have (OPERATIONS: the suite's imports are pytest/pyyaml/pillow/numpy).
    """
    h, w = alpha.shape
    out = np.zeros_like(alpha)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy > radius * radius:
                continue
            ys, ye = max(0, dy), h + min(0, dy)
            xs, xe = max(0, dx), w + min(0, dx)
            sys_, sye = max(0, -dy), h + min(0, -dy)
            sxs, sxe = max(0, -dx), w + min(0, -dx)
            np.maximum(out[ys:ye, xs:xe], alpha[sys_:sye, sxs:sxe],
                       out=out[ys:ye, xs:xe])
    return out


def build_outline(fill_path: Path) -> Image.Image:
    """White silhouette of `fill_path`, dilated to the measured base-game halo."""
    fill = Image.open(fill_path).convert("RGBA")
    alpha = np.array(fill.split()[3])
    radius = max(1, round(min(fill.size) * OUTLINE_RADIUS_FRAC))
    grown = circular_dilate(alpha, radius)
    rgb = np.full(grown.shape + (3,), 255, dtype=np.uint8)
    return Image.fromarray(np.dstack([rgb, grown]), "RGBA")


def main(argv):
    check = "--check" in argv[1:]
    missing, stale = [], []
    for name, (fill_rel, out_rel) in ICONS.items():
        fill_path = ROOT / fill_rel
        out_path = ROOT / out_rel
        if not fill_path.exists():
            # Tier F art is gitignored and absent on a fresh clone / CI runner.
            print(f"SKIPPED: {name} -- no fill at {fill_rel}")
            missing.append(name)
            continue
        img = build_outline(fill_path)
        if check:
            if not out_path.exists():
                stale.append(f"{out_rel} does not exist")
            else:
                have = Image.open(out_path).convert("RGBA")
                if have.tobytes() != img.tobytes():
                    stale.append(f"{out_rel} differs from a fresh derivation")
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        opaque = int((np.array(img.split()[3]) > 128).sum())
        print(f"wrote {out_path} ({img.width}x{img.height}, "
              f"{opaque} opaque px)  [{name}]")

    if check and stale:
        for s in stale:
            print("STALE: " + s, file=sys.stderr)
        return 1
    if check:
        print(f"gen_char_icon_outlines --check: OK "
              f"({len(ICONS) - len(missing)} derived, {len(missing)} skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
