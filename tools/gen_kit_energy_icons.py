#!/usr/bin/env python3
"""Generate every kit's card cost orb and inline text orb (card frames stage 2).

[USER], 2026-10-20: "Agreed on all of the card / orb / energy mockup picks"
(sheet 2, row 3, "proposed"): each kit's cost orb is the base Ironclad cost orb
recoloured through the kit's own frame material, so the orb keeps the base
game's orb-to-frame relationship (both start from the same crimson).

Tier F: the inputs are the base game's own icons, read out of the installed
`SlayTheSpire2.pck`, so the outputs are private-build art like the
multiplayer hands (`gen_multiplayer_hands.py`). Neither enters git.

WHAT THE GAME READS
-------------------
A kit card pool answers BaseLib's id-derived `EnergyColorName`, so
`EnergyIconHelper.GetPath` and the rich-text `energyIcons` formatter ask
BaseLib's `ICustomEnergyIconPool` hook, which returns
`KitCardPool.BigEnergyIconPath` (`res://<kit>/ui/energy_cost.png`, the orb on
the card face and in energy hover tips) and `TextEnergyIconPath`
(`res://<kit>/ui/energy_text_icon.png`, the orb drawn inline in text). The
inputs are the base pair those two replace:

    res://images/atlases/ui_atlas.sprites/card/energy_ironclad.tres  (an AtlasTexture
        region of ui_atlas_0.png, BPTC-compressed)
    res://images/packed/sprite_fonts/ironclad_energy_icon.png

THE RECOLOUR is `res://shaders/hsv.gdshader`'s arithmetic (rotate hue in YIQ
by 1 - h of a turn, scale chroma by s, brightness by v), with each kit's h, s
and v read from `klee-mod/KleeCode/CardFrameColors.cs`, the one table, so a
retuned frame regenerates a matching orb.

WHERE THE FILES GO
------------------
`ImageGen/images/<kit>/ui/` (Klee's historical `ImageGen/images/ui/`), which
`tools/build_pck.ps1`'s per-character ui loop packs at `res://<kit>/ui/`:

    energy_cost.png        the 74x74 cost orb
    energy_text_icon.png   the inline text orb

Usage:
    .venv/Scripts/python tools/gen_kit_energy_icons.py [--check]
        [--art-root <checkout>] [--game-dir <install>]

With no game pck the tool prints SKIPPED and exits 0, like every other Tier F
generator on a runner. Deterministic: same pck and table in, same bytes out.
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
TABLE = ROOT / "klee-mod" / "KleeCode" / "CardFrameColors.cs"

COST_ATLAS_TRES = "images/atlases/ui_atlas.sprites/card/energy_ironclad.tres"
TEXT_ICON_PNG = "images/packed/sprite_fonts/ironclad_energy_icon.png"

#: Kit -> its ui directory under the art root.
KIT_DIRS = {
    "klee": "ImageGen/images/ui",
    "furina": "ImageGen/images/furina/ui",
    "kokomi": "ImageGen/images/kokomi/ui",
    "varka": "ImageGen/images/varka/ui",
    "yae": "ImageGen/images/yae/ui",
}
#: The two files written per kit. Spelled out so art_lint's L11 rot check
#: finds each GENERATOR_OWNED basename in this file.
COST_FILE = "energy_cost.png"
TEXT_FILE = "energy_text_icon.png"

# --- the hsv shader, in numpy ------------------------------------------------
# GLSL mat3(a, b, c) takes COLUMNS, and `col.rgb *= hue_shift` is v * M.
YIQ = np.array([[0.2989, 0.5870, 0.1140],
                [0.5959, -0.2774, -0.3216],
                [0.2115, -0.5229, 0.3114]])
IYIQ = np.linalg.inv(YIQ)


def shade(img: Image.Image, h: float, s: float, v: float) -> Image.Image:
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255
    yiq = a[..., :3] @ YIQ.T
    hue = (1.0 - h) * 2 * np.pi
    c, sn = np.cos(hue), np.sin(hue)
    y, i, q = yiq[..., 0], yiq[..., 1], yiq[..., 2]
    out = np.stack([y, (c * i - sn * q) * s, (sn * i + c * q) * s], -1) * v
    rgb = np.clip(out @ IYIQ.T, 0, 1)
    res = np.concatenate([rgb, a[..., 3:]], -1)
    return Image.fromarray((res * 255 + 0.5).astype(np.uint8), "RGBA")


def kit_tints(table: Path = TABLE) -> dict:
    """kit -> (h, s, v), read from CardFrameColors.cs's Tint rows."""
    text = table.read_text(encoding="utf-8")
    rows = re.findall(
        r'new\("([a-z]+)",\s*([0-9.]+)f,\s*([0-9.]+)f,\s*([0-9.]+)f,\s*new Color', text)
    tints = {k: (float(h), float(s), float(v)) for k, h, s, v in rows}
    missing = set(KIT_DIRS) - set(tints)
    if missing:
        raise SystemExit(f"{table}: no Tint row for {sorted(missing)}")
    return {k: tints[k] for k in KIT_DIRS}


# --- reading the base icons out of the game pck -----------------------------
_REMAP = re.compile(r'^path(?:\.[a-z0-9]+)?="res://([^"]+)"', re.M)
_REGION = re.compile(r"region = Rect2\(([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\)")
_ATLAS = re.compile(r'path="res://([^"]+)"')


def _decode_ctex(data: bytes) -> Image.Image:
    """A Godot 4 CompressedTexture2D: a lossless PNG/WebP payload, or BPTC/DXT5/RGBA8."""
    if data[:4] != b"GST2":
        raise ValueError(f"not a GST2 ctex (magic {data[:4]!r})")
    (data_format,) = struct.unpack("<I", data[36:40])
    if data_format in (1, 2):
        riff = data.find(b"RIFF")
        png = data.find(b"\x89PNG\r\n\x1a\n")
        if riff >= 0 and (png < 0 or riff < png):
            (size,) = struct.unpack("<I", data[riff + 4:riff + 8])
            payload = data[riff:riff + 8 + size]
        else:
            payload = data[png:]
        img = Image.open(io.BytesIO(payload))
        img.load()
        return img.convert("RGBA")
    w, h, _mips, fmt = struct.unpack("<HHII", data[40:52])
    raw = data[52:]
    if fmt == 22:   # BPTC_RGBA (BC7)
        return Image.frombytes("RGBA", (w, h), raw[:w * h], "bcn", 7)
    if fmt == 17:   # DXT5
        return Image.frombytes("RGBA", (w, h), raw[:w * h], "bcn", 3)
    if fmt == 5:    # RGBA8
        return Image.frombytes("RGBA", (w, h), raw[:w * h * 4])
    raise ValueError(f"unsupported ctex format {fmt} (data format {data_format})")


def read_base_icons(pck_path: Path) -> tuple[Image.Image, Image.Image]:
    """(the base Ironclad cost orb, the base Ironclad text orb)."""
    f, _hdr, entries = pck_read.parse(str(pck_path))
    try:
        by_path = {e.path: e for e in entries}

        def texture(res: str) -> Image.Image:
            imp = pck_read.read(f, by_path[res + ".import"]).decode("utf-8")
            for p in _REMAP.findall(imp):
                if p in by_path:
                    return _decode_ctex(pck_read.read(f, by_path[p]))
            raise FileNotFoundError(f"{pck_path}: {res} remaps to no ctex in the pack")

        tres = pck_read.read(f, by_path[COST_ATLAS_TRES]).decode("utf-8")
        atlas_res = _ATLAS.search(tres).group(1)
        x, y, w, h = (round(float(n)) for n in _REGION.search(tres).groups())
        cost = texture(atlas_res).crop((x, y, x + w, y + h))
        text = texture(TEXT_ICON_PNG)
        return cost, text
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
    """out-path relative to the art root -> generated image."""
    cost, text = read_base_icons(pck_path)
    out = {}
    for kit, (h, s, v) in kit_tints().items():
        out[f"{KIT_DIRS[kit]}/{COST_FILE}"] = shade(cost, h, s, v)
        out[f"{KIT_DIRS[kit]}/{TEXT_FILE}"] = shade(text, h, s, v)
    return out


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
    pck_path = (args.game_dir or game_dir_for(art_root)) / "SlayTheSpire2.pck"
    if not pck_path.is_file():
        print(f"SKIPPED: no game pack at {pck_path}")
        return 0

    images = build_all(pck_path)
    if args.check:
        stale = []
        for rel, img in images.items():
            path = art_root / rel
            if not path.is_file():
                stale.append(f"{rel} does not exist")
                continue
            have = Image.open(path).convert("RGBA")
            if have.size != img.size or have.tobytes() != img.tobytes():
                stale.append(f"{rel} differs from a fresh derivation")
        for line in stale:
            print(f"STALE: {line}")
        if stale:
            print("rerun: gen_kit_energy_icons.py [--art-root <checkout>]")
            return 1
        print(f"OK: {len(images)} kit energy icons match their derivations")
        return 0

    for rel, img in images.items():
        path = art_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        print(f"wrote {rel} ({img.width}x{img.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
