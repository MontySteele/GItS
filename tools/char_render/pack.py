"""Pack a kit's rendered frames into the game's sheets and stills (Varka first).

    python tools/char_render/pack.py --char varka --renders <scratch dir> [--art-root <dir>] [--check]

The kit twin of tools/klee_render/pack.py, sharing its helpers (the trim, the
height measure, the roster-tile crop, the ground shadow) and adding what a
bladed kit needs. Reads what tools/klee_render/post.py painted from
tools/char_render/render.py's raw frames and writes, under
<art-root>/ImageGen/images/<char>/:

  model/frames/<char>_<clip>.png      one sheet per combat clip and the shop loop,
                                      cells in reading order; a clip too big for
                                      one MAX_SHEET texture continues on
                                      <char>_<clip>_p2.png, ... (`pages`)
  model/frames/<char>_<clip>_fx.png   the clip's neutral slash trails and impact
                                      bursts (fx.py), from its first live frame
                                      to its last, tinted per element by the game
  model/frames/<char>_shadow.png      the ground shadow (Klee's look)
  model/<char>_rest.png               the seated rest-site still, padded so
                                      BaseLib's centred sprite puts his seat on
                                      the rest-site anchor
  ui/select_closeup.png               the character-select close-up, 1920x1080
  ui/select_portrait.png (+_locked)   the roster tile, 132x195, a face close-up

and the committed manifest tools/char_render/<char>_frames.json (cells, pages,
counts, times, anchors, events, the fx layers' frame ranges -- no pixels),
which the game-side generator reads. Every pixel below the ground line (the
feet anchor + GROUND_SLACK) is cut: the planted blades' tips read as driven
into the ground, never as hanging below the floor.

Scale contract: combat frames at chars.target_ppu (canon height over an adult,
docs/current/LAW.md) drawn at 0.5; the shop at 1.7x from a 1.5x texture; the
rest site at 1.33x through BaseLib's 0.5 container; select a close-up.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def _load(path: Path, name: str):
    """A sibling script by path under a private name, so no sys.path entry
    shadows another module called `pack`, `fx` or `chars`."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CH = _load(HERE / "chars.py", "char_render_chars")
FX = _load(HERE / "fx.py", "char_render_fx")
KP = _load(ROOT / "tools" / "klee_render" / "pack.py", "klee_render_pack")

COMBAT = ("idle", "idle_low", "attack", "cast", "hurt", "death", "ascension")
COMBAT_SCALE = CH.COMBAT_SCALE
MERCHANT_SCALE = KP.MERCHANT_SCALE
MAX_SHEET = 4096
PAD = 2
#: texture px (at the combat scale) below the feet anchor kept: the boot
#: soles reach about 4 px under it
GROUND_SLACK = 6.0
#: Spelled out, not formatted: art_lint's GENERATOR_OWNED rot check greps the
#: producer for every out-path's basename.
SHEET_FILES = {"varka": {"idle": "varka_idle.png", "idle_low": "varka_idle_low.png", "attack": "varka_attack.png",
                         "cast": "varka_cast.png", "hurt": "varka_hurt.png", "death": "varka_death.png",
                         "ascension": "varka_ascension.png", "merchant": "varka_merchant.png"}}
FX_FILES = {"varka": {"attack": "varka_attack_fx.png", "ascension": "varka_ascension_fx.png"}}
SHADOW_FILES = {"varka": "varka_shadow.png"}
REST_FILES = {"varka": "varka_rest.png"}


def manifest_path(char: str) -> Path:
    return HERE / f"{char}_frames.json"


def ground_clip(im: Image.Image, origin_y: float, s: float) -> Image.Image:
    """Clear every texel more than GROUND_SLACK (scaled) below the ground line."""
    y = int(math.ceil(origin_y + GROUND_SLACK * s))
    if y >= im.height:
        return im
    out = im.copy()
    out.paste(Image.new("RGBA", (im.width, im.height - y), (0, 0, 0, 0)), (0, y))
    return out


def page_name(file: str, page: int) -> str:
    return file if page == 0 else file.replace(".png", f"_p{page + 1}.png")


def layout(n: int, cw: int, ch: int, max_sheet: int = MAX_SHEET):
    """(cols, rows per page, pages): Klee's near-square grid when one sheet
    holds every cell, else as many full-width pages as it takes."""
    cols = max(1, min(n, max_sheet // cw, math.ceil(math.sqrt(n * ch / cw))))
    if math.ceil(n / cols) * ch <= max_sheet:
        return cols, math.ceil(n / cols), 1
    cols = max(1, min(n, max_sheet // cw))
    rpp = max(1, max_sheet // ch)
    return cols, rpp, math.ceil(n / (cols * rpp))


def sheets_for(frames: list, origin, file: str):
    """Trim every frame to the union alpha box, lay the cells out (paging if
    need be) and return ([(file, sheet)], record)."""
    x0, y0, x1, y1 = KP.alpha_box(frames)
    x0, y0 = max(0, x0 - PAD), max(0, y0 - PAD)
    x1, y1 = min(frames[0].width, x1 + PAD), min(frames[0].height, y1 + PAD)
    cw, ch = x1 - x0, y1 - y0
    n = len(frames)
    cols, rpp, npages = layout(n, cw, ch)
    per = cols * rpp
    out, pages = [], []
    for p in range(npages):
        chunk = frames[p * per:(p + 1) * per]
        rows = math.ceil(len(chunk) / cols)
        sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
        for i, im in enumerate(chunk):
            sheet.paste(im.crop((x0, y0, x1, y1)), ((i % cols) * cw, (i // cols) * ch))
        name = page_name(file, p)
        out.append((name, sheet))
        pages.append({"file": name, "count": len(chunk), "hframes": cols, "vframes": rows})
    rec = {"cell": [cw, ch], "count": n, "pages": pages,
           # whole texels, so a sprite's offset never lands between two
           "origin": [round(origin[0] - x0), round(origin[1] - y0)]}
    return out, rec


def load_clip(R: Path, clip: str):
    meta = json.loads((R / f"{clip}.json").read_text(encoding="utf-8"))
    assert not meta.get("keys_only"), f"{clip}: a --keys-only render is a preview, not frames"
    s = float(meta["ppu"]) / FX.REF_PPU
    frames = [ground_clip(Image.open(R / clip / f"f_{i:03d}.png").convert("RGBA"), meta["origin_px"][1], s)
              for i in range(len(meta["times"]))]
    return meta, frames


def frame_of(meta: dict, t: float) -> int:
    """The frame whose time is nearest t."""
    return min(range(len(meta["times"])), key=lambda i: abs(meta["times"][i] - t))


def rest_still(R: Path):
    """BaseLib centres the texture at y = -0.1 h inside a 0.5 container, so a
    point at (w/2, 0.6 h) of the texture lands on the anchor: pad so the seat
    (the hips' head) is that point (Klee's rule)."""
    meta = json.loads((R / "rest.json").read_text(encoding="utf-8"))
    s = float(meta["ppu"]) / FX.REF_PPU
    rest = ground_clip(Image.open(R / "rest.png").convert("RGBA"), meta["origin_px"][1], s)
    rb = KP.alpha_box([rest])
    rest = rest.crop(rb)
    hx, hy = meta["hips_px"][0] - rb[0], meta["hips_px"][1] - rb[1]
    half_w = math.ceil(max(hx, rest.width - hx)) + PAD
    H = math.ceil(max(hy / 0.6, (rest.height - hy) / 0.4)) + PAD
    top = round(0.6 * H - hy)
    canvas = Image.new("RGBA", (2 * half_w, H), (0, 0, 0, 0))
    canvas.paste(rest, (round(half_w - hx), top))
    return canvas, {"size": list(canvas.size), "ppu": meta["ppu"], "seat_px": [half_w, round(0.6 * H)]}


def select_closeup(R: Path, target_h: int = 2150):
    """1920x1080, the figure right of centre, bleeding off the bottom (Klee's framing)."""
    meta = json.loads((R / "select.json").read_text(encoding="utf-8"))
    sel = Image.open(R / "select.png").convert("RGBA")
    sel = ground_clip(sel, meta["origin_px"][1], float(meta["ppu"]) / FX.REF_PPU)
    sel = sel.crop(KP.alpha_box([sel]))
    k = target_h / sel.height
    sel = sel.resize((round(sel.width * k), target_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    canvas.paste(sel, (1260 - sel.width // 2, 36), sel)
    return canvas, {"size": [1920, 1080], "figure_h": target_h}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--char", default="varka", choices=sorted(SHEET_FILES))
    ap.add_argument("--renders", required=True, help="render.py --out dir, painted by post.py")
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--check", action="store_true", help="only report; write nothing")
    args = ap.parse_args(argv)
    char, R = args.char, Path(args.renders)
    art = Path(args.art_root) / "ImageGen" / "images" / char
    out_frames = art / "model" / "frames"
    files = SHEET_FILES[char]
    manifest = {"_doc": f"Generated by tools/char_render/pack.py from renders of the official {char} model "
                        "(never committed). Cells, pages, counts, times, anchors and events only; the sheets "
                        f"live in ImageGen/images/{char}/model/frames.",
                "char": char, "combat_scale": COMBAT_SCALE, "merchant_scale": MERCHANT_SCALE, "sheets": {}, "fx": {}}
    writes = []
    for clip in (*COMBAT, "merchant"):
        meta, frames = load_clip(R, clip)
        sheets, rec = sheets_for(frames, meta["origin_px"], files[clip])
        rec.update({"fps": meta["fps"], "length": meta["length"], "loop": meta["loop"],
                    "motion_end": meta.get("motion_end"), "times": meta["times"], "ppu": meta["ppu"]})
        ev = meta.get("events") or {}
        if ev:
            rec["events"] = ev
            rec["impact_frames"] = [frame_of(meta, t) for t in ev.get("impact", [])]
            if "main" in ev:
                rec["main_frame"] = frame_of(meta, ev["main"])
        manifest["sheets"][clip] = rec
        writes += [(out_frames / name, im) for name, im in sheets]
        print(f"{clip:10s} {rec['count']:3d} frames  cell {rec['cell']}  pages "
              f"{[(p['hframes'], p['vframes']) for p in rec['pages']]}  origin {rec['origin']}")
        if clip in FX_FILES.get(char, {}):
            layers, first, pad = FX.clip_fx(meta)
            assert layers, f"{clip}: no trail or burst marked"
            origin = (meta["origin_px"][0] + pad, meta["origin_px"][1] + pad)
            fsheets, frec = sheets_for(layers, origin, FX_FILES[char][clip])
            frec.update({"first_frame": first, "fps": meta["fps"],
                         "heat": "R=G=B heat (1 core, ~0.5 glow), A coverage; tint per element"})
            manifest["fx"][clip] = frec
            writes += [(out_frames / name, im) for name, im in fsheets]
            print(f"  fx      frames {first}..{first + frec['count'] - 1}  cell {frec['cell']}  "
                  f"origin {frec['origin']}")

    # the scale check, on the upright reference still (varka_clips.STAND)
    st = json.loads((R / "stand.json").read_text(encoding="utf-8"))
    manifest["measure"] = KP.body_metrics(R / "stand.png", st, COMBAT_SCALE)
    sa = json.loads((R / "stance_a.json").read_text(encoding="utf-8"))
    manifest["stance_a"] = KP.body_metrics(R / "stance_a.png", sa, COMBAT_SCALE)
    manifest["target_body_px"] = round(CH.body_px(CH.CHARS[char]["height_in"]), 1)
    print("standing at 1080p:", manifest["measure"], " stance A:", manifest["stance_a"],
          " target", manifest["target_body_px"])

    # the ground shadow: one texture, placed per figure (Klee's look)
    full_h = manifest["measure"]["full_px"]
    combat = KP.shadow_for(Image.open(R / "stance_a.png").convert("RGBA"), sa["origin_px"], full_h, COMBAT_SCALE)
    mm = json.loads((R / "merchant.json").read_text(encoding="utf-8"))
    shop_k = (mm["ppu"] * MERCHANT_SCALE) / (sa["ppu"] * COMBAT_SCALE)
    m0 = ground_clip(Image.open(R / "merchant" / "f_000.png").convert("RGBA"), mm["origin_px"][1],
                     float(mm["ppu"]) / FX.REF_PPU)
    merchant = KP.shadow_for(m0, mm["origin_px"], full_h * shop_k, MERCHANT_SCALE)
    tw, th = round(combat["size"][0] / COMBAT_SCALE), round(combat["size"][1] / COMBAT_SCALE)
    writes.append((out_frames / SHADOW_FILES[char], KP.shadow_texture(tw, th)))
    manifest["shadow"] = {"file": SHADOW_FILES[char], "texture": [tw, th], "combat": combat, "merchant": merchant}
    print("shadow    ", manifest["shadow"])

    rest, rrec = rest_still(R)
    writes.append((art / "model" / REST_FILES[char], rest))
    manifest["rest"] = {"file": REST_FILES[char], **rrec}
    print("rest      ", rrec)

    sel, srec = select_closeup(R)
    writes.append((art / "ui" / "select_closeup.png", sel))
    manifest["select"] = {"file": "select_closeup.png", **srec}

    locked_variant = _load(ROOT / "tools" / "char_stills.py", "char_stills").locked_variant
    pm = json.loads((R / "portrait.json").read_text(encoding="utf-8"))
    tile = KP.portrait_tile(Image.open(R / "portrait.png").convert("RGBA"), pm)
    writes.append((art / "ui" / "select_portrait.png", tile))
    writes.append((art / "ui" / "select_portrait_locked.png", locked_variant(tile)))
    manifest["portrait"] = {"file": "select_portrait.png", "size": list(KP.PORTRAIT_SIZE), "ppu": pm["ppu"]}

    text = json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"
    mpath = manifest_path(char)
    if args.check:
        current = mpath.read_text(encoding="utf-8") if mpath.exists() else ""
        if current != text:
            print(f"STALE: {mpath.name} differs from these renders")
            return 1
        print(f"{mpath.name} matches these renders")
        return 0
    for path, im in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path, optimize=True)
        print("wrote", path)
    mpath.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", mpath.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
