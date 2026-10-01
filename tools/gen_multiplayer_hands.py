#!/usr/bin/env python3
"""Generate the multiplayer treasure-room hands for Klee, Furina, Kokomi and Varka.

Tier F: every output is a recolour of the base game's own hand art, read out
of the installed `SlayTheSpire2.pck`, so it is private-build art exactly like
its input. Neither the base textures nor the outputs ever enter git.

WHAT THE GAME READS
-------------------
In a co-op treasure room `NHandImage` draws each player's arm from
`CharacterModel.ArmPointingTexture` and its rock/paper/scissors siblings. The
four paths are non-virtual, id-derived getters (decompiled `CharacterModel`):

    ImageHelper.GetImagePath("ui/hands/multiplayer_hand_"
                             + Id.Entry.ToLowerInvariant() + "_<pose>.png")

and `GetImagePath` prepends `res://images/`. BaseLib prefixes our model ids
(KLEE -> KLEEMOD-KLEE), so the twelve resources are

    res://images/ui/hands/multiplayer_hand_kleemod-<character>_<pose>.png

Until this tool, Furina and Kokomi had nothing at that path (no hand drawn)
and Klee borrowed the Ironclad's through `KleeAssetPathFallback.cs`.

WHERE THE FILES GO
------------------
`ImageGen/images/hands/<resource file name>`. `tools/build_pck.ps1`'s hands
block copies that directory to `images/ui/hands/` in the pck work project, so
the exported pack carries the engine path itself -- the same mechanism the
retired map-ground block used for `res://images/packed/map/`. The names are
new, so nothing in the base pack is overridden.

THE RECIPE (approved by [USER], 2026-09-27: "The hands you drew out look good
to me"). Each character recolours one base character's arm in HSV:

  * Klee   <- the Silent's arm: green sleeve -> red, lower wrap -> red cuff,
              upper wrap -> brown glove, brown skin -> fair (`klee_pose`).
  * Furina <- the Regent's arm: orange glove -> white glove, blue sleeve ->
              navy coat.
  * Kokomi <- the Necrobinder's arm: magenta sleeve -> lavender, sallow skin
              -> pale.
  * Varka  <- the Ironclad's gauntleted arm, UNCHANGED (2026-09-30 co-op
              playtest: he drew no hand at a chest). A stand-in until a Varka
              recolour is drawn and approved; it copies the base pixels, so
              there is no recipe to approve.

The arithmetic below is the prototype's, verbatim (float64 HSV round trip,
truncating `astype(uint8)` on the way out), so the outputs match the approved
drafts pixel for pixel. Do not "tidy" it: rounding instead of truncating, or
a different HSV implementation, moves pixels the approval was given on.

Deterministic: same base pck in, same bytes out.

Usage:
    .venv/Scripts/python tools/gen_multiplayer_hands.py [--check]
        [--art-root <checkout>] [--game-dir <install>]

`--art-root` lets a worktree write into (or check) the main checkout's
gitignored `ImageGen/`. `--game-dir` defaults to klee-mod/local.props's
`GameDir`, then to the default Steam path. With no game pck the tool prints
SKIPPED and exits 0, like every other Tier F generator on a runner.
"""
from __future__ import annotations

import argparse
import io
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "probe_spine_pck"))
import pck_read  # noqa: E402

DEFAULT_GAME_DIR = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2")
OUT_DIR = "ImageGen/images/hands"
POSES = ("point", "rock", "paper", "scissors")

# Output file -> (base character, pose). Spelled out rather than built from a
# loop so art_lint's L11 rot check finds every GENERATOR_OWNED basename here.
OUTPUTS = {
    "multiplayer_hand_kleemod-klee_point.png":       ("silent", "point"),
    "multiplayer_hand_kleemod-klee_rock.png":        ("silent", "rock"),
    "multiplayer_hand_kleemod-klee_paper.png":       ("silent", "paper"),
    "multiplayer_hand_kleemod-klee_scissors.png":    ("silent", "scissors"),
    "multiplayer_hand_kleemod-furina_point.png":     ("regent", "point"),
    "multiplayer_hand_kleemod-furina_rock.png":      ("regent", "rock"),
    "multiplayer_hand_kleemod-furina_paper.png":     ("regent", "paper"),
    "multiplayer_hand_kleemod-furina_scissors.png":  ("regent", "scissors"),
    "multiplayer_hand_kleemod-kokomi_point.png":     ("necrobinder", "point"),
    "multiplayer_hand_kleemod-kokomi_rock.png":      ("necrobinder", "rock"),
    "multiplayer_hand_kleemod-kokomi_paper.png":     ("necrobinder", "paper"),
    "multiplayer_hand_kleemod-kokomi_scissors.png":  ("necrobinder", "scissors"),
    "multiplayer_hand_kleemod-varka_point.png":      ("ironclad", "point"),
    "multiplayer_hand_kleemod-varka_rock.png":       ("ironclad", "rock"),
    "multiplayer_hand_kleemod-varka_paper.png":      ("ironclad", "paper"),
    "multiplayer_hand_kleemod-varka_scissors.png":   ("ironclad", "scissors"),
}


# --- HSV, float64, the prototype's own implementation ----------------------

def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    df = mx - mn
    h = np.zeros_like(mx)
    nz = df > 1e-6
    rr = (mx == r) & nz
    gg = (mx == g) & nz & ~rr
    bb = nz & ~rr & ~gg
    h[rr] = ((g - b)[rr] / df[rr]) % 6
    h[gg] = ((b - r)[gg] / df[gg]) + 2
    h[bb] = ((r - g)[bb] / df[bb]) + 4
    h = h / 6
    s = np.where(mx > 1e-6, df / np.maximum(mx, 1e-6), 0)
    return np.stack([h, s, mx], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    out = np.zeros(hsv.shape)
    for k, (a, b, c) in enumerate([(v, t, p), (q, v, p), (p, v, t),
                                   (p, q, v), (t, p, v), (v, p, q)]):
        sel = i == k
        out[..., 0][sel] = a[sel]
        out[..., 1][sel] = b[sel]
        out[..., 2][sel] = c[sel]
    return out


def band(h, lo, hi):
    """Hue band in degrees; wraps through 0 when lo > hi."""
    lo /= 360
    hi /= 360
    return (h >= lo) & (h < hi) if lo < hi else (h >= lo) | (h < hi)


def _to_float(img: Image.Image):
    return np.array(img.convert("RGBA")).astype(float) / 255


def _to_image(a) -> Image.Image:
    return Image.fromarray((a * 255).astype(np.uint8), "RGBA")


def recolor(img: Image.Image, rules) -> Image.Image:
    """Apply (lo_deg, hi_deg, min_sat, fn) rules in order, all masks taken
    from the ORIGINAL hsv; fn maps (h, s, v) of the masked pixels to new."""
    a = _to_float(img)
    hsv = rgb_to_hsv(a[..., :3])
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    new = hsv.copy()
    for lo, hi, smin, fn in rules:
        m = band(h, lo, hi) & (s >= smin)
        nh, ns, nv = fn(h[m], s[m], v[m])
        new[..., 0][m] = nh
        new[..., 1][m] = ns
        new[..., 2][m] = nv
    a[..., :3] = np.clip(hsv_to_rgb(new), 0, 1)
    return _to_image(a)


FURINA_RULES = [
    # orange glove -> white glove
    (0, 60, 0.3, lambda h, s, v: (h * 0 + 0.6, s * 0.06, 0.62 + 0.38 * v)),
    # blue sleeve -> navy coat
    (180, 270, 0.15,
     lambda h, s, v: (h * 0 + 0.635, np.minimum(1, s * 1.25), v * 0.62)),
]

KOKOMI_RULES = [
    # magenta sleeve -> lavender
    (290, 360, 0.15,
     lambda h, s, v: (h * 0 + 0.70, s * 0.45, np.minimum(1, 0.45 + 0.6 * v))),
    # sallow skin -> pale
    (0, 70, 0.0,
     lambda h, s, v: (h * 0 + 0.06, s * 0.5, np.minimum(1, 0.5 + 0.5 * v))),
]


def klee_pose(img: Image.Image) -> Image.Image:
    """The Silent's arm as Klee's: red sleeve, red cuff, brown glove, fair skin.

    The Silent's arm carries two bandage wraps; the lower becomes a red cuff
    and the upper a brown glove, so the wrap mask is split at the thinnest
    wrap row inside the middle half of the wrap's vertical extent.
    """
    a = _to_float(img)
    hsv = rgb_to_hsv(a[..., :3])
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    al = a[..., 3] > 0.3
    wrap = band(h, 40, 80) & al & (s < 0.45)
    skin = band(h, 0, 40) & al & (s >= 0.3)
    sleeve = band(h, 100, 180) & (s >= 0.15)
    rows = np.where(wrap.any(1))[0]
    wr = wrap.sum(1)
    lo, hi = rows.min(), rows.max()
    span = np.arange(lo, hi + 1)
    mid = lo + np.argmin(wr[lo:hi + 1]
                         + (span < lo + (hi - lo) * 0.3) * 10 ** 6
                         + (span > lo + (hi - lo) * 0.8) * 10 ** 6)
    lower = wrap.copy()
    lower[:mid] = False
    upper = wrap & ~lower
    new = hsv.copy()

    def put(m, nh, ns, nv):
        new[..., 0][m] = nh
        new[..., 1][m] = ns[m] if hasattr(ns, "shape") else ns
        new[..., 2][m] = nv[m] if hasattr(nv, "shape") else nv

    red_s = np.minimum(1, s * 2.1)
    red_v = np.minimum(1, v * 1.25)
    put(sleeve, 0.005, red_s, red_v)
    put(lower, 0.005, np.full_like(s, 0.8), np.minimum(1, 0.25 + v * 0.7))
    put(upper, 0.06, np.maximum(s, 0.45), v * 0.42)
    put(skin, 0.06, s * 0.55, np.minimum(1, 0.5 + 0.55 * v))
    a[..., :3] = np.clip(hsv_to_rgb(new), 0, 1)
    return _to_image(a)


RECIPES = {
    "silent": klee_pose,
    "regent": lambda img: recolor(img, FURINA_RULES),
    "necrobinder": lambda img: recolor(img, KOKOMI_RULES),
    # Varka's stand-in: the Ironclad's arm as the base game draws it.
    "ironclad": lambda img: img.convert("RGBA"),
}


# --- reading the base hands out of the game pck ----------------------------

_REMAP_PATH_RE = re.compile(r'^path="res://([^"]+)"', re.M)


def _decode_ctex(data: bytes) -> Image.Image:
    """A Godot 4 CompressedTexture2D ('GST2' + header) holding a lossless
    PNG or WebP payload. Find the payload by signature and hand it to Pillow."""
    if data[:4] != b"GST2":
        raise ValueError(f"not a GST2 ctex (magic {data[:4]!r})")
    riff = data.find(b"RIFF")
    png = data.find(b"\x89PNG\r\n\x1a\n")
    if riff >= 0 and (png < 0 or riff < png):
        (size,) = struct.unpack("<I", data[riff + 4:riff + 8])
        payload = data[riff:riff + 8 + size]
    elif png >= 0:
        payload = data[png:]
    else:
        raise ValueError("ctex has neither a PNG nor a WebP payload")
    img = Image.open(io.BytesIO(payload))
    img.load()
    return img


def read_base_hands(pck_path: Path) -> dict:
    """(base character, pose) -> PIL image, for the four base arms we use."""
    f, _hdr, entries = pck_read.parse(str(pck_path))
    try:
        by_path = {e.path: e for e in entries}
        out = {}
        for base, pose in sorted(set(OUTPUTS.values())):
            imp_path = f"images/ui/hands/multiplayer_hand_{base}_{pose}.png.import"
            imp = by_path.get(imp_path)
            if imp is None:
                raise FileNotFoundError(f"{pck_path}: no {imp_path}")
            m = _REMAP_PATH_RE.search(pck_read.read(f, imp).decode("utf-8"))
            if not m or m.group(1) not in by_path:
                raise FileNotFoundError(
                    f"{pck_path}: {imp_path} remaps to a missing ctex")
            out[(base, pose)] = _decode_ctex(pck_read.read(f, by_path[m.group(1)]))
        return out
    finally:
        f.close()


def game_dir_for(art_root: Path) -> Path:
    props = art_root / "klee-mod" / "local.props"
    if props.is_file():
        m = re.search(r"<GameDir>([^<]+)</GameDir>",
                      props.read_text(encoding="utf-8", errors="replace"))
        if m:
            return Path(m.group(1).strip())
    return DEFAULT_GAME_DIR


def build_all(pck_path: Path) -> dict:
    """output file name -> generated image."""
    base = read_base_hands(pck_path)
    return {name: RECIPES[b](base[(b, pose)]) for name, (b, pose) in OUTPUTS.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the outputs exist and equal a fresh derivation")
    ap.add_argument("--art-root", type=Path, default=ROOT,
                    help="checkout whose ImageGen/ to write or check")
    ap.add_argument("--game-dir", type=Path, default=None,
                    help="game install holding SlayTheSpire2.pck")
    args = ap.parse_args(argv)

    art_root = args.art_root.resolve()
    game_dir = args.game_dir or game_dir_for(art_root)
    pck_path = game_dir / "SlayTheSpire2.pck"
    if not pck_path.is_file():
        # Tier F input: absent on a fresh clone / CI runner.
        print(f"SKIPPED: no game pack at {pck_path}")
        return 0

    images = build_all(pck_path)
    out_dir = art_root / OUT_DIR
    if args.check:
        stale = []
        for name, img in images.items():
            path = out_dir / name
            if not path.is_file():
                stale.append(f"{OUT_DIR}/{name} does not exist")
                continue
            have = Image.open(path).convert("RGBA")
            if have.size != img.size or have.tobytes() != img.tobytes():
                stale.append(f"{OUT_DIR}/{name} differs from a fresh derivation")
        for s in stale:
            print("STALE: " + s, file=sys.stderr)
        if stale:
            return 1
        print(f"gen_multiplayer_hands --check: OK ({len(images)} hands)")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, img in images.items():
        img.save(out_dir / name)
        print(f"wrote {OUT_DIR}/{name} ({img.width}x{img.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
