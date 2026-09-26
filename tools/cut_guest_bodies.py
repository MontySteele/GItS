"""Cut the Guest Stars' stage bodies.

The Guest Cast (2026-09-25, review/active/furina-guest-batch-2026-09-25.md)
put eight Fontaine characters on Furina's stage as performers, and the
supporting pool (2026-09-26, review/active/furina-supporting-pool-2026-09-26.md)
added Lyney and Escoffier for ten. Until this tool each one wore the base
game's Osty rig. This gives them what the Salon trio
has: a pre-scaled sprite and a scene with the trio's four animations.

Produces the gitignored art (Tier F, private builds only):

    ImageGen/images/furina/salon/guest_<name>.png   (one per guest)
    ImageGen/images/furina/salon/guests.json        (sizes, the shape of
                                                     members.json)

and the git-tracked scenes:

    klee-mod/pck-src/furina/model/guest_<name>.tscn

The trio's tool (tools/cut_salon_members.py) stays as it is; one producer per
out-path.

TWO SOURCES, chosen per guest in SOURCES below.

  game  art/raw/Character_<Name>_Game.png, the wiki's in-game model render:
        the figure alone, no splash FX, standing on the character-screen
        backdrop (a starry nebula, OPAQUE -- the file has no alpha). Keyed by
        art_process.matte(), the same matte `cut` plan rows use on the Archive
        enemy captures, with GAME_CUT's knobs. The render stands the figure
        on a mirror floor, so the matte keeps the shoes' REFLECTION (it is
        figure-coloured, not backdrop); the work image is cut at the guest's
        SOLE ROW, read off the render at 3x, so the feet are the ground line.
        Three automatic passes follow, one parameter set for every guest:
        drop_reflections() (the reflection under a RAISED foot, which the
        sole row cannot reach), keep_islands() (stray specks) and despill()
        (the nebula's blue-lilac cast on edges and pale cloth).
  wish  art/raw/Character_<Name>_Full_Wish.png, the transparent Wish render,
        its own alpha as the matte. It carries the splash FX, so the figure
        stands inside an effects cloud. The fallback for a guest whose `game`
        cut failed the 2x check (holes in the figure, backdrop or stars left,
        a blue halo on the edges); the reason is on its SOURCES line.

HEIGHT. The guests are people standing beside Furina, so they are sized off
HER body, not off the trio's 144 px creatures: Furina's combat scene
(klee-mod/pck-src/furina/model/combat.tscn) is 280 px tall (Bounds offset_top
-280, body layer 280 px), and a guest is 80% of that, 224 px. The whole alpha
bounding box is scaled to that height; nothing is cropped off the figure.

EDGES. Resampled in PREMULTIPLIED alpha, so a transparent pixel's colour
cannot bleed into its neighbours as a fringe, then every pixel under
ALPHA_FLOOR is cleared to transparent black. The bounding box is measured at
BBOX_ALPHA so a near-invisible haze does not widen the crop.

SCENES. One template (SCENE_TEMPLATE below), filled per guest: the trio's
usher.tscn with the Rig at half the sprite height, Bounds the sprite's width
and height, and the animation offsets scaled by TARGET_H / 144.

`--art-root` points the source and the ImageGen output at the art-bearing
main checkout (a worktree has no ImageGen tree and must not link one); the
scenes are always written under this checkout.

Usage: .venv/Scripts/python tools/cut_guest_bodies.py [--check] [--art-root PATH]
"""
from __future__ import annotations

import argparse
import filecmp
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import art_process  # noqa: E402

RAW_REL = Path("art") / "raw"
OUT_REL = Path("ImageGen") / "images" / "furina" / "salon"
SCENE_DIR = ROOT / "klee-mod" / "pck-src" / "furina" / "model"
FURINA_SCENE = SCENE_DIR / "combat.tscn"

# The guests in StagePerformer order (FurinaStage.cs): the Guest Cast's eight,
# then the supporting pool's two. The key is the file stem; the value is the
# wiki name in the render's file name.
GUESTS = {
    "neuvillette": "Neuvillette",
    "clorinde": "Clorinde",
    "navia": "Navia",
    "chevreuse": "Chevreuse",
    "wriothesley": "Wriothesley",
    "sigewinne": "Sigewinne",
    "charlotte": "Charlotte",
    "lynette": "Lynette",
    "lyney": "Lyney",
    "escoffier": "Escoffier",
}

# The matte for a `game` render, in art_process's `cut` spec grammar.
# Tolerance 100, not the Archive rows' default 30: at 30 and 45 the nebula's
# bright horizon band survives across the frame's full width, and at 60 a
# floor shadow survives beside Navia; 100 clears both with no hole in the
# pale areas (Sigewinne's hair and stockings, Neuvillette's hair, Chevreuse's
# boots). rekey=1 as on the Archive rows. The chroma gate stays at its
# default: raising it to 30 holes Sigewinne's bows, and 60 takes Navia's hat.
GAME_CUT = "cut@100;rekey=1"

# art_process.matte() solves at CUT_WORK_MAX on the long edge; the renders are
# portrait, so the work image is this many rows tall and the sole rows below
# are rows of it.
WORK_H = art_process.CUT_WORK_MAX

# Per guest: ("game", sole row) or ("wish", None). The sole row is the lowest
# row of the lower shoe, read at 3x off the keyed work image; everything below
# it is the mirror floor's reflection.
#
# All eight ship from `game` (2026-09-25): "a matching cast is worth more
# than" Charlotte's residual edge haze, which does not show at in-game size.
# `wish` stays as the fallback kind for a future guest.
SOURCES: dict[str, tuple[str, int | None]] = {
    "neuvillette": ("game", 875),
    "clorinde": ("game", 872),
    "navia": ("game", 873),
    "chevreuse": ("game", 873),
    "wriothesley": ("game", 875),
    "sigewinne": ("game", 870),
    # A grey-lilac haze stays down the outside of both legs at 2x: the
    # render's bloom there is opaque and 20 px wide, so despill greys it
    # rather than removing it. Accepted: invisible at in-game size.
    "charlotte": ("game", 872),
    "lynette": ("game", 872),
    # The supporting pool's two (2026-09-26), same knobs, no per-guest
    # exception. Escoffier's polearm hangs tip-down between her legs and the
    # mirror floor draws its reflected tip in the 30 rows above the sole row.
    # drop_reflections() reads it as a third foot run and clears 1045 of its
    # 1088 px; keep_islands() takes the last 43. The leg beside it keeps every
    # pixel (measured 2026-09-26).
    # Lyney keeps a two-pixel nebula sparkle on the toe of his right boot:
    # it touches the boot, so it is not an island. Accepted like Charlotte's
    # haze; it does not show at in-game size.
    "lyney": ("game", 874),
    "escoffier": ("game", 873),
}

# ---- the three passes after the matte, ONE parameter set for every guest ----
#
# REFLECTION UNDER A RAISED FOOT. A staggered stance puts one sole above the
# sole row, and the mirror floor's image of that foot fills the rows between.
# The reflection is BLURRED where the shoe is not: per foot (an x-run of
# opaque pixels at the sole row), the mean luminance gradient per row, over a
# REFL_WIN-row window, stays under REFL_FLAT all the way up from the sole to
# where the real shoe begins. A run of at least REFL_MIN_ROWS such rows is
# dropped, across the foot's columns widened by REFL_MARGIN (the reflection
# is wider than the sole) but never into the other foot's columns. Measured
# on the eight: raised feet flat for 16-30 rows, every planted foot 0-5.
OPAQUE = 128
REFL_FLAT = 12
REFL_WIN = 5
REFL_MIN_ROWS = 10
REFL_SKIP = 2        # the sole cut's own feathered rows
REFL_MARGIN = 10
FOOT_ROWS = 3        # rows above the sole that define a foot's x-run
FOOT_GAP = 3         # columns of gap that still join one run

# ISLANDS. Anything under ISLAND_FRAC of the largest piece goes (Lynette's
# magenta speck, stray stars); a kept piece keeps a 2 px feathered fringe.
ISLAND_FRAC = 0.01

# DESPILL. The nebula tints what it touches blue-lilac. B is clamped to
# max(R, G) + SPILL_ALLOW and a magenta cast (min(R, B) over G) is pulled the
# same way, on three sets of pixels: every pixel within SPILL_EDGE of the
# silhouette; bright, pale pixels (white stockings, rim light) within
# SPILL_BRIGHT_BAND; and LOW-SATURATION pixels within SPILL_WIDE (Charlotte's
# leg glow, 20 px wide). Saturated cloth -- Neuvillette's coat (sat 0.56-0.83),
# Sigewinne's jacket, Lynette's bow -- is outside every set but the 3 px edge.
# The bright set is banded, not "anywhere": unbanded, it moved 644 px of
# Sigewinne's pale-blue HAIR toward grey and changed nothing else.
SPILL_ALLOW = 12
SPILL_EDGE = 3
SPILL_BRIGHT_BAND = 8
SPILL_BRIGHT_LUM = 150
SPILL_BRIGHT_SAT = 0.25
SPILL_WIDE = 24
SPILL_WIDE_SAT = 0.45

# Furina's body height in creature space (combat.tscn Bounds, -280..0). Read
# back from the scene on every run so the 80% cannot drift from her.
FURINA_BODY_H = 280
GUEST_SHARE = 0.8
TARGET_H = 224  # round(GUEST_SHARE * FURINA_BODY_H)

# The trio's height, which the usher.tscn animation offsets were authored at.
TRIO_H = 144

BBOX_ALPHA = 16    # alpha >= this counts toward the crop box
ALPHA_FLOOR = 8    # alpha below this is cleared after the resize


def source_path(art_root: Path, name: str) -> Path:
    kind = SOURCES[name][0]
    stem = "Game" if kind == "game" else "Full_Wish"
    return art_root / RAW_REL / f"Character_{GUESTS[name]}_{stem}.png"


def furina_body_height() -> int:
    """Furina's scene height, from her Bounds node."""
    text = FURINA_SCENE.read_text(encoding="utf-8")
    block = text[text.index('[node name="Bounds"'):]
    top = next(line for line in block.splitlines()
               if line.startswith("offset_top = "))
    return round(-float(top.split("=")[1]))


def _resize_premultiplied(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """LANCZOS in premultiplied space; returns float RGBA in 0..255."""
    a = rgba[..., 3:4] / 255.0
    pre = rgba[..., :3] * a
    chans = [pre[..., i] for i in range(3)] + [rgba[..., 3]]
    out = [np.asarray(Image.fromarray(c.astype(np.float32), "F")
                      .resize(size, Image.LANCZOS)) for c in chans]
    alpha = np.clip(out[3], 0, 255)
    safe = np.where(alpha > 0, alpha / 255.0, 1.0)
    rgb = np.stack([np.clip(out[i] / safe, 0, 255) for i in range(3)], -1)
    return np.concatenate([rgb, alpha[..., None]], -1)


def cut_one(src: Image.Image) -> Image.Image:
    """Crop an RGBA figure to its alpha box and scale it to TARGET_H."""
    rgba = np.asarray(src.convert("RGBA")).astype(np.float64)
    mask = Image.fromarray(((rgba[..., 3] >= BBOX_ALPHA) * 255).astype(np.uint8))
    box = mask.getbbox()
    if box is None:
        raise SystemExit("render has no opaque pixels")
    x0, y0, x1, y1 = box
    crop = rgba[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    size = (max(1, round(w * TARGET_H / h)), TARGET_H)
    out = _resize_premultiplied(crop, size)
    clear = out[..., 3] < ALPHA_FLOOR
    out[clear] = 0
    return Image.fromarray(np.rint(out).astype(np.uint8), "RGBA")


def foot_runs(alpha: np.ndarray, sole: int) -> list[tuple[int, int]]:
    """x-runs of opaque pixels in the FOOT_ROWS rows ending at the sole."""
    band = (alpha[sole - FOOT_ROWS + 1:sole + 1] >= OPAQUE).any(0)
    runs: list[tuple[int, int]] = []
    for x in np.nonzero(band)[0].tolist():
        if runs and x - runs[-1][1] <= FOOT_GAP:
            runs[-1] = (runs[-1][0], x)
        else:
            runs.append((x, x))
    return runs


def _row_detail(a: np.ndarray, x0: int, x1: int) -> np.ndarray:
    """Mean luminance gradient of the opaque pixels in each row, x0..x1."""
    lum = a[..., :3].mean(-1)
    grad = (np.abs(np.diff(lum, axis=1, append=lum[:, -1:]))
            + np.abs(np.diff(lum, axis=0, append=lum[-1:])))
    grad, solid = grad[:, x0:x1 + 1], a[:, x0:x1 + 1, 3] >= OPAQUE
    n = solid.sum(1)
    return np.where(n > 0, (grad * solid).sum(1) / np.maximum(n, 1), 0.0)


def drop_reflections(work: Image.Image) -> Image.Image:
    """Clear the flat, blurred reflection under a raised foot (see REFL_*)."""
    a = np.asarray(work).astype(np.float64).copy()
    sole = a.shape[0] - 1
    runs = foot_runs(a[..., 3], sole)
    for i, (x0, x1) in enumerate(runs):
        raw = _row_detail(a, x0, x1)
        detail = np.convolve(raw, np.ones(REFL_WIN) / REFL_WIN, mode="same")
        y = sole - REFL_SKIP
        while y > 0 and detail[y] < REFL_FLAT:
            y -= 1
        if sole - REFL_SKIP - y < REFL_MIN_ROWS:
            continue                       # a planted foot: nothing below it
        # The window lags the shoe's edge by up to half its width; step up
        # through rows that are flat on their own, to the shoe's last row.
        while y > 0 and raw[y] < REFL_FLAT:
            y -= 1
        lo = max(x0 - REFL_MARGIN, runs[i - 1][1] + 1 if i else 0)
        hi = min(x1 + REFL_MARGIN,
                 runs[i + 1][0] - 1 if i + 1 < len(runs) else a.shape[1] - 1)
        a[y + 1:, lo:hi + 1, 3] = 0
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def keep_islands(work: Image.Image) -> Image.Image:
    """Keep the largest piece and any piece over ISLAND_FRAC of it."""
    a = np.asarray(work).copy()
    pieces = art_process._components(a[..., 3] >= BBOX_ALPHA)
    if not pieces:
        return work
    floor = ISLAND_FRAC * int(pieces[0].sum())
    keep = np.zeros(a.shape[:2], bool)
    for i, piece in enumerate(pieces):
        if i == 0 or piece.sum() >= floor:
            keep |= piece
    a[~art_process._dilate(keep, 2), 3] = 0
    return Image.fromarray(a, "RGBA")


def despill(work: Image.Image) -> Image.Image:
    """Pull the nebula's blue-lilac cast toward neutral (see SPILL_*)."""
    a = np.asarray(work).astype(np.float64).copy()
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    solid = al >= OPAQUE

    def near(k: int) -> np.ndarray:
        return (al > 0) & ~art_process._erode(solid, k)

    hi, lo = a[..., :3].max(-1), a[..., :3].min(-1)
    lum = a[..., :3].mean(-1)
    sat = (hi - lo) / np.maximum(hi, 1)
    m = near(SPILL_EDGE)
    m |= (near(SPILL_BRIGHT_BAND) & (lum >= SPILL_BRIGHT_LUM)
          & (sat <= SPILL_BRIGHT_SAT))
    m |= near(SPILL_WIDE) & (sat <= SPILL_WIDE_SAT)
    b2 = np.where(m, np.minimum(b, np.maximum(r, g) + SPILL_ALLOW), b)
    magenta = np.minimum(r, b2) - g
    pull = np.where(m & (magenta > SPILL_ALLOW), magenta - SPILL_ALLOW, 0.0)
    a[..., 0] = r - pull
    a[..., 2] = b2 - pull
    return Image.fromarray(np.clip(np.rint(a), 0, 255).astype(np.uint8), "RGBA")


def key_game(src: Image.Image, sole: int) -> Image.Image:
    """Key a `game` render with art_process.matte(), cut it at the sole, and
    run the three passes."""
    work = art_process.matte(src.convert("RGBA"), GAME_CUT)
    if work.height != WORK_H:
        raise SystemExit(f"game render keyed to {work.size}; the sole rows "
                         f"assume a portrait render {WORK_H} rows tall")
    work = work.crop((0, 0, work.width, sole + 1))
    return despill(keep_islands(drop_reflections(work)))


def body(art_root: Path, name: str) -> Image.Image:
    src = source_path(art_root, name)
    if not src.exists():
        raise SystemExit(f"source missing: {src}")
    kind, sole = SOURCES[name]
    img = Image.open(src)
    return cut_one(key_game(img, sole) if kind == "game" else img)


def build_art(art_root: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name in GUESTS:
        sprite = body(art_root, name)
        path = out_dir / f"guest_{name}.png"
        sprite.save(path)
        meta[name] = {"file": path.name, "w": sprite.width, "h": sprite.height}
        fill = (np.asarray(sprite)[..., 3] > 128).mean()
        print(f"  {name:12s} {SOURCES[name][0]:4s} {sprite.width:3d}x"
              f"{sprite.height:3d}  fill {fill * 100:.0f}%")
    (out_dir / "guests.json").write_text(
        json.dumps({"target_h": TARGET_H, "guests": meta}, indent=2),
        encoding="utf-8")
    return meta


# --------------------------------------------------------------- scenes --

def _n(v: float) -> str:
    """A Godot scene number: integers bare, else one decimal."""
    v = round(v, 1)
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def _vec(x: float, y: float) -> str:
    return f"Vector2({_n(x)}, {_n(y)})"


def scene_text(name: str, w: int, h: int) -> str:
    """usher.tscn, re-proportioned for a w x h sprite."""
    k = h / TRIO_H
    rest = -h / 2

    def at(dx=0.0, dy=0.0):
        return _vec(dx * k, rest + dy * k)

    return SCENE_TEMPLATE.format(
        name=name,
        Title=name.capitalize(),
        rest=at(),
        idle=", ".join(at(dy=d) for d in (0, -3, 0, 1, 0)),
        attack=", ".join(at(dx=d) for d in (0, 30, -4, 0)),
        hurt=", ".join(at(dx=d) for d in (0, -8, 6, -3, 2, 0)),
        death=", ".join(at(dy=d) for d in (0, 10)),
        half_w=_n(w / 2),
        top=_n(-h),
    )


def build_scenes(meta: dict, scene_dir: Path) -> None:
    scene_dir.mkdir(parents=True, exist_ok=True)
    for name, m in meta.items():
        (scene_dir / f"guest_{name}.tscn").write_text(
            scene_text(name, m["w"], m["h"]), encoding="utf-8", newline="\n")


# ----------------------------------------------------------------- main --

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild to a temp dir and diff against shipped files")
    ap.add_argument("--art-root", default=str(ROOT),
                    help="checkout holding art/raw and ImageGen")
    args = ap.parse_args()
    art_root = Path(args.art_root).resolve()
    out_dir = art_root / OUT_REL

    measured = furina_body_height()
    if measured != FURINA_BODY_H or round(GUEST_SHARE * measured) != TARGET_H:
        raise SystemExit(
            f"Furina's scene is {measured} px tall; FURINA_BODY_H/TARGET_H "
            f"({FURINA_BODY_H}/{TARGET_H}) are stale")

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            meta = build_art(art_root, tmp / "art")
            build_scenes(meta, tmp / "scenes")
            bad = []
            for produced, shipped_dir in (
                    *((p, out_dir) for p in (tmp / "art").iterdir()),
                    *((p, SCENE_DIR) for p in (tmp / "scenes").iterdir())):
                shipped = shipped_dir / produced.name
                if not shipped.exists():
                    bad.append(f"MISSING on disk: {shipped}")
                elif not filecmp.cmp(produced, shipped, shallow=False):
                    bad.append(f"DIFFERS: {shipped}")
            for line in bad:
                print("  " + line)
            print("byte-identical" if not bad else f"{len(bad)} mismatch(es)")
            return 1 if bad else 0

    print(f"{art_root / RAW_REL} -> {out_dir}")
    meta = build_art(art_root, out_dir)
    build_scenes(meta, SCENE_DIR)
    print(f"scenes -> {SCENE_DIR}")
    return 0


SCENE_TEMPLATE = """\
[gd_scene load_steps=22 format=3]

[ext_resource type="Texture2D" path="res://furina/salon/guest_{name}.png" id="1_{name}"]

[sub_resource type="Animation" id="Animation_reset"]
length = 0.001
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0),
"transitions": PackedFloat32Array(1),
"update": 0,
"values": [{rest}]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:rotation")
tracks/1/interp = 1
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0),
"transitions": PackedFloat32Array(1),
"update": 0,
"values": [0.0]
}}
tracks/2/type = "value"
tracks/2/imported = false
tracks/2/enabled = true
tracks/2/path = NodePath("Visuals/Rig:modulate")
tracks/2/interp = 1
tracks/2/loop_wrap = true
tracks/2/keys = {{
"times": PackedFloat32Array(0),
"transitions": PackedFloat32Array(1),
"update": 0,
"values": [Color(1, 1, 1, 1)]
}}

[sub_resource type="Animation" id="Animation_idle"]
resource_name = "idle"
length = 3.0
loop_mode = 1
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 2
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.75, 1.5, 2.25, 3),
"transitions": PackedFloat32Array(1, 1, 1, 1, 1),
"update": 0,
"values": [{idle}]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:rotation")
tracks/1/interp = 2
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0, 0.75, 1.5, 2.25, 3),
"transitions": PackedFloat32Array(1, 1, 1, 1, 1),
"update": 0,
"values": [0.0, 0.018, 0.0, -0.018, 0.0]
}}

[sub_resource type="Animation" id="Animation_attack"]
resource_name = "attack"
length = 0.5
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.15, 0.35, 0.5),
"transitions": PackedFloat32Array(0.5, 1.6, 1, 1),
"update": 0,
"values": [{attack}]
}}

[sub_resource type="Animation" id="Animation_hurt"]
resource_name = "hurt"
length = 0.4
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:position")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.06, 0.14, 0.22, 0.32, 0.4),
"transitions": PackedFloat32Array(1, 1, 1, 1, 1, 1),
"update": 0,
"values": [{hurt}]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:modulate")
tracks/1/interp = 1
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0, 0.05, 0.35),
"transitions": PackedFloat32Array(1, 1, 1),
"update": 0,
"values": [Color(1, 1, 1, 1), Color(1, 0.45, 0.4, 1), Color(1, 1, 1, 1)]
}}

[sub_resource type="Animation" id="Animation_death"]
resource_name = "death"
length = 1.0
tracks/0/type = "value"
tracks/0/imported = false
tracks/0/enabled = true
tracks/0/path = NodePath("Visuals/Rig:modulate")
tracks/0/interp = 1
tracks/0/loop_wrap = true
tracks/0/keys = {{
"times": PackedFloat32Array(0, 0.15, 1),
"transitions": PackedFloat32Array(1, 1, 1),
"update": 0,
"values": [Color(1, 1, 1, 1), Color(1, 0.62, 0.6, 1), Color(1, 1, 1, 0)]
}}
tracks/1/type = "value"
tracks/1/imported = false
tracks/1/enabled = true
tracks/1/path = NodePath("Visuals/Rig:rotation")
tracks/1/interp = 1
tracks/1/loop_wrap = true
tracks/1/keys = {{
"times": PackedFloat32Array(0, 1),
"transitions": PackedFloat32Array(1, 1),
"update": 0,
"values": [0.0, 0.22]
}}
tracks/2/type = "value"
tracks/2/imported = false
tracks/2/enabled = true
tracks/2/path = NodePath("Visuals/Rig:position")
tracks/2/interp = 1
tracks/2/loop_wrap = true
tracks/2/keys = {{
"times": PackedFloat32Array(0, 1),
"transitions": PackedFloat32Array(1, 1),
"update": 0,
"values": [{death}]
}}

[sub_resource type="AnimationLibrary" id="AnimationLibrary_{name}"]
_data = {{
&"RESET": SubResource("Animation_reset"),
&"attack": SubResource("Animation_attack"),
&"death": SubResource("Animation_death"),
&"hurt": SubResource("Animation_hurt"),
&"idle": SubResource("Animation_idle")
}}

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_attack"]
animation = &"attack"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_death"]
animation = &"death"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_hurt"]
animation = &"hurt"

[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_idle"]
animation = &"idle"

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_start_idle"]
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_hurt"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_hurt_idle"]
switch_mode = 2
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_death_end"]
switch_mode = 2
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_hurt_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_idle_attack"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_attack_idle"]
switch_mode = 2
advance_mode = 2

[sub_resource type="AnimationNodeStateMachineTransition" id="Transition_attack_death"]
advance_mode = 0

[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_{name}"]
states/End/position = Vector2(628, 153)
states/Start/position = Vector2(186, 153)
states/attack/node = SubResource("AnimationNodeAnimation_attack")
states/attack/position = Vector2(327, 64)
states/death/node = SubResource("AnimationNodeAnimation_death")
states/death/position = Vector2(470, 153)
states/hurt/node = SubResource("AnimationNodeAnimation_hurt")
states/hurt/position = Vector2(327, 278)
states/idle/node = SubResource("AnimationNodeAnimation_idle")
states/idle/position = Vector2(327, 153)
transitions = ["Start", "idle", SubResource("Transition_start_idle"), "idle", "death", SubResource("Transition_idle_death"), "idle", "hurt", SubResource("Transition_idle_hurt"), "hurt", "idle", SubResource("Transition_hurt_idle"), "death", "End", SubResource("Transition_death_end"), "hurt", "death", SubResource("Transition_hurt_death"), "idle", "attack", SubResource("Transition_idle_attack"), "attack", "idle", SubResource("Transition_attack_idle"), "attack", "death", SubResource("Transition_attack_death")]

[node name="Guest{Title}Visuals" type="Node2D"]

[node name="Visuals" type="Node2D" parent="."]
unique_name_in_owner = true

[node name="Rig" type="Node2D" parent="Visuals"]
position = {rest}

[node name="Body" type="Sprite2D" parent="Visuals/Rig"]
texture = ExtResource("1_{name}")

[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = -{half_w}
offset_top = {top}
offset_right = {half_w}
offset_bottom = 0.0
mouse_filter = 2

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {{
&"": SubResource("AnimationLibrary_{name}")
}}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_{name}")
anim_player = NodePath("../AnimationPlayer")
"""


if __name__ == "__main__":
    sys.exit(main())
