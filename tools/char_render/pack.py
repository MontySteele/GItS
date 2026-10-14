"""Pack a kit's rendered frames into the game's sheets and stills (Varka first).

    python tools/char_render/pack.py --char varka --renders <scratch dir> [--art-root <dir>] [--check]

The kit twin of tools/klee_render/pack.py, sharing its helpers (the trim, the
height measure, the roster-tile crop, the ground shadow) and adding what a
bladed kit needs. Reads what tools/klee_render/post.py painted from
tools/char_render/render.py's raw frames and writes, under
<art-root>/ImageGen/images/<char>/:

  model/frames/<char>_<clip>.png      one sheet per combat clip and the shop loop:
                                      each frame trimmed to its own texels and
                                      shelf-packed in reading order (`frames`:
                                      page, rect, offset in the clip's cell); a
                                      clip too big for one MAX_SHEET texture
                                      continues on <char>_<clip>_p2.png, ... (`pages`)
  model/frames/<char>_<clip>_fx.png   the clip's neutral slash trails and impact
                                      bursts (fx.py), from its first live frame
                                      to its last, tinted per element by the game
  model/frames/<char>_ground_burst.png  an effect clip of its own (fx.ground_burst):
                                      the manifest's `effects` says which clip
                                      places it, from which frame, and where (the
                                      Ascension: at the blade's point and,
                                      mirrored, under the target)
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

#: each kit's combat clips; COMBAT is Varka's (the first kit), kept by name
COMBAT_CLIPS = {"varka": ("idle", "idle_low", "attack", "cast", "hurt", "death", "ascension"),
                "furina": ("idle", "idle_low", "attack", "cast", "hurt", "death", "rejoice")}
COMBAT = COMBAT_CLIPS["varka"]
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
                         "ascension": "varka_ascension.png", "merchant": "varka_merchant.png"},
               "furina": {"idle": "furina_idle.png", "idle_low": "furina_idle_low.png",
                          "attack": "furina_attack.png", "cast": "furina_cast.png", "hurt": "furina_hurt.png",
                          "death": "furina_death.png", "rejoice": "furina_rejoice.png",
                          "merchant": "furina_merchant.png"}}
FX_FILES = {"varka": {"attack": "varka_attack_fx.png", "ascension": "varka_ascension_fx.png"},
            "furina": {"attack": "furina_attack_fx.png"}}
#: effect sprite clips a combat clip places (its spec's `effects`)
EFFECT_FILES = {"varka": {"ground_burst": "varka_ground_burst.png"}}
#: effect sprite clips no clip places, played by the game on a stage event
#: (fx.STAGE_EFFECTS: Furina's Spend, Drain and Repay)
STAGE_FILES = {"furina": {"spend": "furina_spend.png", "drain": "furina_drain.png", "repay": "furina_repay.png"}}
SHADOW_FILES = {"varka": "varka_shadow.png", "furina": "furina_shadow.png"}
REST_FILES = {"varka": "varka_rest.png", "furina": "furina_rest.png"}
#: Furina's guest stars, one still each (render.py --guests), under model/guests/
#: (spelled out, not formatted, for art_lint's GENERATOR_OWNED rot check)
GUEST_FILES = {"furina": {"charlotte": "guest_charlotte.png",
                          "chevreuse": "guest_chevreuse.png",
                          "clorinde": "guest_clorinde.png",
                          "escoffier": "guest_escoffier.png",
                          "freminet": "guest_freminet.png",
                          "lynette": "guest_lynette.png",
                          "lyney": "guest_lyney.png",
                          "navia": "guest_navia.png",
                          "neuvillette": "guest_neuvillette.png",
                          "sigewinne": "guest_sigewinne.png",
                          "wriothesley": "guest_wriothesley.png"}}


#: the alpha a texel needs to widen a sheet's cell: the toon pass leaves a
#: faint 1-3/255 haze past the outline that no screen shows, and a union box
#: over every frame pays for it on every cell
ALPHA_FLOOR = 4
#: how phase B's generator imports the sheets (Godot's compress/mode 2)
TEXTURE_IMPORT = "vram_compressed"


def tight_box(frames: list, floor: int = ALPHA_FLOOR):
    """The union box of every texel at alpha >= floor across the frames."""
    box = None
    for im in frames:
        b = im.getchannel("A").point(lambda v: 255 if v >= floor else 0).getbbox()
        if b is None:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    return box


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


def shelf(sizes: list, max_sheet: int = MAX_SHEET):
    """Pack (w, h) rects in reading order onto shelves: a page about as wide
    as it is tall (never over max_sheet), a new shelf when a row is full, a
    new page when a shelf would run off the bottom. Returns ([(page, x, y)],
    [(page_w, page_h)])."""
    area = sum(w * h for w, h in sizes)
    W = min(max_sheet, max(max(w for w, _h in sizes), math.ceil(math.sqrt(area * 1.15))))
    place, pages = [], []
    page, x, y, row_h, used_w = 0, 0, 0, 0, 0
    for w, h in sizes:
        if x and x + w > W:                      # next shelf
            x, y, row_h = 0, y + row_h, 0
        if y + h > max_sheet:                    # next page
            pages.append((used_w, y))
            page, x, y, row_h, used_w = page + 1, 0, 0, 0, 0
        place.append((page, x, y))
        x += w
        row_h = max(row_h, h)
        used_w = max(used_w, x)
    pages.append((used_w, y + row_h))
    return place, pages


def sheets_for(frames: list, origin, file: str):
    """Every frame trimmed to its OWN visible texels (tight_box, plus PAD),
    shelf-packed onto as few MAX_SHEET pages as it takes. The record keeps
    the clip's logical cell (the union box) and origin, and per frame the
    page, its rect on that page and its offset inside the cell: in Godot an
    AtlasTexture with region = rect and margin = (offset, cell - rect size)
    draws it exactly where the untrimmed cell would. Returns
    ([(file, sheet)], record)."""
    ux0, uy0, ux1, uy1 = tight_box(frames)
    ux0, uy0 = max(0, ux0 - PAD), max(0, uy0 - PAD)
    ux1, uy1 = min(frames[0].width, ux1 + PAD), min(frames[0].height, uy1 + PAD)
    boxes = []
    for im in frames:
        b = tight_box([im]) or (ux0, uy0, ux0 + 1, uy0 + 1)
        boxes.append((max(ux0, b[0] - PAD), max(uy0, b[1] - PAD), min(ux1, b[2] + PAD), min(uy1, b[3] + PAD)))
    place, sizes = shelf([(b[2] - b[0], b[3] - b[1]) for b in boxes])
    sheets = [Image.new("RGBA", sz, (0, 0, 0, 0)) for sz in sizes]
    recs = []
    for im, b, (pg, x, y) in zip(frames, boxes, place):
        sheets[pg].paste(im.crop(b), (x, y))
        recs.append({"page": pg, "rect": [x, y, b[2] - b[0], b[3] - b[1]], "offset": [b[0] - ux0, b[1] - uy0]})
    out, pages = [], []
    for pg, sheet in enumerate(sheets):
        name = page_name(file, pg)
        out.append((name, sheet))
        pages.append({"file": name, "count": sum(1 for r in recs if r["page"] == pg), "size": list(sheet.size)})
    rec = {"cell": [ux1 - ux0, uy1 - uy0], "count": len(frames), "pages": pages, "frames": recs,
           # whole texels, so a sprite's offset never lands between two
           "origin": [round(origin[0] - ux0), round(origin[1] - uy0)]}
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


def ground_point(meta: dict, side: str, t: float):
    """Where a blade meets the ground line at time t, in the clip's canvas px:
    the point at which its base-to-tip line crosses the feet anchor's row (its
    tip when the tip is above the ground)."""
    s = min((x for x in meta["blades"] if x.get(side)), key=lambda x: abs(x["t"] - t))
    (bx, by), (tx, ty) = s[side]
    gy = meta["origin_px"][1]
    if ty <= gy or ty == by:
        return tx, ty
    k = max(0.0, min(1.0, (gy - by) / (ty - by)))
    return bx + (tx - bx) * k, gy


def effect_uses(meta: dict, clip: str) -> list[dict]:
    """The manifest record of each effect a clip places: the clip, the start
    frame, and every place (`blade_tip`: an offset in texture px from the
    clip's feet anchor; `target`: the target's feet anchor), with `flip_h` on
    the mirrored copy."""
    out = []
    for e in meta.get("effects", []):
        places = []
        for n, where in enumerate(e["places"]):
            rec = {"at": where, "flip_h": bool(e.get("mirror")) and n > 0}
            if where == "blade_tip":
                gx, gy = ground_point(meta, e["blade"], e["t"])
                rec.update({"blade": e["blade"],
                            "offset_px": [round(gx - meta["origin_px"][0]), round(gy - meta["origin_px"][1])]})
            places.append(rec)
        out.append({"name": e["name"], "clip": clip, "start_frame": frame_of(meta, e["t"]),
                    "mirror": bool(e.get("mirror")), "both_positions": set(e["places"]) == {"blade_tip", "target"},
                    "places": places})
    return out


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


#: the select close-up's frame: the figure's top this far down, and anything
#: the still marks to keep in frame (stance B's crossguards) at least
#: SELECT_KEEP px above the bottom and SELECT_SIDE px in from the right
SELECT_TOP, SELECT_KEEP, SELECT_SIDE = 36, 48, 24


def select_closeup(R: Path, target_h: int = 2150):
    """1920x1080, the figure right of centre, bleeding off the bottom (Klee's
    framing). When the still records its blades' crossguards (render.py
    arms_crossed, stance B), the figure is drawn smaller if it must be, so
    both crossguards sit inside the frame, and moved left if its right edge
    would leave it. The manifest gets where the crossguards and the chin land."""
    meta = json.loads((R / "select.json").read_text(encoding="utf-8"))
    sel = Image.open(R / "select.png").convert("RGBA")
    sel = ground_clip(sel, meta["origin_px"][1], float(meta["ppu"]) / FX.REF_PPU)
    bx, by, bx1, by1 = KP.alpha_box([sel])
    sel = sel.crop((bx, by, bx1, by1))
    guards = {s: g["guard_box_px"] for s, g in ((meta.get("arms_crossed") or {}).get("hilts") or {}).items()}
    if guards:
        low = max(g[3] for g in guards.values()) - by
        target_h = min(target_h, math.floor((1080 - SELECT_KEEP - SELECT_TOP) * sel.height / low))
    k = target_h / sel.height
    sel = sel.resize((round(sel.width * k), target_h), Image.LANCZOS)
    cx = min(1260, 1920 - SELECT_SIDE - (sel.width - sel.width // 2))
    x0 = cx - sel.width // 2
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    canvas.paste(sel, (x0, SELECT_TOP), sel)
    rec = {"size": [1920, 1080], "figure_h": target_h}

    def to_canvas(x, y):
        return [round((x - bx) * k + x0, 1), round((y - by) * k + SELECT_TOP, 1)]
    if guards:
        rec["guards_px"] = {s: to_canvas(g[0], g[1]) + to_canvas(g[2], g[3]) for s, g in sorted(guards.items())}
        rec["chin_px"] = to_canvas(0, meta["arms_crossed"]["chin_px"])[1]
    return canvas, rec


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
                        "(never committed). Cells, per-frame rects, pages, counts, times, anchors and events only; the sheets "
                        f"live in ImageGen/images/{char}/model/frames.",
                "char": char, "combat_scale": COMBAT_SCALE, "merchant_scale": MERCHANT_SCALE,
                # the texture budget pick (visual paper, pick 1, default): sheets stay
                # 2x and the game imports them VRAM-compressed
                "texture_import": TEXTURE_IMPORT, "sheets": {}, "fx": {}, "effects": {}}
    uses = []
    writes = []
    for clip in (*COMBAT_CLIPS[char], "merchant"):
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
              f"{[tuple(p['size']) for p in rec['pages']]}  origin {rec['origin']}")
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
        uses += effect_uses(meta, clip)

    # the effect clips the combat clips place (fx.ground_burst), drawn at the combat ppu
    for name, file in EFFECT_FILES.get(char, {}).items():
        mine = [u for u in uses if u["name"] == name]
        assert mine, f"{name}: no clip places it"
        ppu = manifest["sheets"][mine[0]["clip"]]["ppu"]
        fps = manifest["sheets"][mine[0]["clip"]]["fps"]
        frames, origin = FX.ground_burst(ppu, fps)
        esheets, erec = sheets_for(frames, origin, file)
        erec.update({"fps": fps, "ppu": ppu, "length": round(len(frames) / fps, 4), "loop": False,
                     "heat": "R=G=B heat (1 core, ~0.5 glow), A coverage; tint per element",
                     "anchor": "origin is the ground point: put it on each place's point",
                     "uses": [{k: v for k, v in u.items() if k != "name"} for u in mine]})
        manifest["effects"][name] = erec
        writes += [(out_frames / n, im) for n, im in esheets]
        print(f"effect {name}: {erec['count']} frames  cell {erec['cell']}  origin {erec['origin']}  uses {erec['uses']}")

    # the stage's own effect clips (fx.STAGE_EFFECTS), at the combat ppu: no
    # clip places them; the game plays each on its stage event (phase B)
    for name, file in STAGE_FILES.get(char, {}).items():
        ppu = manifest["sheets"]["idle"]["ppu"]
        frames, origin, to = FX.STAGE_EFFECTS[name](ppu, FX.STAGE_FPS)
        esheets, erec = sheets_for(frames, origin, file)
        erec.update({"fps": FX.STAGE_FPS, "ppu": ppu, "length": round(len(frames) / FX.STAGE_FPS, 4), "loop": False,
                     "heat": "R=G=B heat (1 core, ~0.5 glow), A coverage; tint per element",
                     "tint": FX.STAGE_TINTS[name], "uses": [],
                     "anchor": "origin is Furina's chest" + ("; `to` the first guest seat" if to else "")})
        if to:
            # the far end, in the trimmed cell's px (as `origin`)
            erec["to"] = [round(to[0] - origin[0] + erec["origin"][0]), round(to[1] - origin[1] + erec["origin"][1])]
        manifest["effects"][name] = erec
        writes += [(out_frames / n, im) for n, im in esheets]
        print(f"stage {name}: {erec['count']} frames  cell {erec['cell']}  origin {erec['origin']}  to {erec.get('to')}")

    # the scale check, on the upright reference still (the pose library's STAND)
    st = json.loads((R / "stand.json").read_text(encoding="utf-8"))
    manifest["measure"] = KP.body_metrics(R / "stand.png", st, COMBAT_SCALE)
    sa = json.loads((R / "stance_a.json").read_text(encoding="utf-8"))
    manifest["stance_a"] = KP.body_metrics(R / "stance_a.png", sa, COMBAT_SCALE)
    # the neck joint's height over the feet: the crouch measure (the shoulder
    # blade rises over his head in stance A, so the alpha top is no measure)
    for key, m in (("measure", st), ("stance_a", sa)):
        manifest[key]["neck_px"] = round((m["origin_px"][1] - m["head_px"][1]) * COMBAT_SCALE, 1)
    # the chest, between the hips and the neck, as an offset from the feet
    # anchor at 1080p: where an effect clip anchored "on her" goes (Furina's
    # Spend, Drain and Repay)
    manifest["stance_a"]["chest_px"] = [round(((sa["hips_px"][i] + sa["head_px"][i]) / 2 - sa["origin_px"][i])
                                              * COMBAT_SCALE, 1) for i in (0, 1)]
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

    # stance B's crossed arms (render.py arms_crossed), as measured on the
    # deformed mesh: the merchant loop's first frame and the select still
    crossed = {}
    for name in ("merchant", "select"):
        g = json.loads((R / f"{name}.json").read_text(encoding="utf-8")).get("arms_crossed")
        if g:
            crossed[name] = g
    if crossed:
        manifest["arms_crossed"] = crossed

    sel, srec = select_closeup(R)
    writes.append((art / "ui" / "select_closeup.png", sel))
    manifest["select"] = {"file": "select_closeup.png", **srec}

    locked_variant = _load(ROOT / "tools" / "char_stills.py", "char_stills").locked_variant
    pm = json.loads((R / "portrait.json").read_text(encoding="utf-8"))
    tile = KP.portrait_tile(Image.open(R / "portrait.png").convert("RGBA"), pm)
    writes.append((art / "ui" / "select_portrait.png", tile))
    writes.append((art / "ui" / "select_portrait_locked.png", locked_variant(tile)))
    manifest["portrait"] = {"file": "select_portrait.png", "size": list(KP.PORTRAIT_SIZE), "ppu": pm["ppu"]}

    # the guest stars: one trimmed still each, its feet anchor and its size
    # at 1080p (combat scale), drawn at Furina's px per inch (chars.guest_ppu)
    if GUEST_FILES.get(char):
        manifest["guests"] = {}
        for g, file in GUEST_FILES[char].items():
            gm = json.loads((R / f"guest_{g}.json").read_text(encoding="utf-8"))
            s = float(gm["ppu"]) / FX.REF_PPU
            im = ground_clip(Image.open(R / f"guest_{g}.png").convert("RGBA"), gm["origin_px"][1], s)
            b = tight_box([im])
            b = (max(0, b[0] - PAD), max(0, b[1] - PAD), min(im.width, b[2] + PAD), min(im.height, b[3] + PAD))
            still = im.crop(b)
            writes.append((art / "model" / "guests" / file, still))
            metrics = KP.body_metrics(R / f"guest_{g}.png", gm, COMBAT_SCALE)
            manifest["guests"][g] = {
                "file": file, "size": list(still.size), "ppu": gm["ppu"], "height_in": gm["height_in"],
                "feet": [round(gm["origin_px"][0] - b[0]), round(gm["origin_px"][1] - b[1])],
                "head_px": round((gm["origin_px"][1] - gm["head_px"][1]) * COMBAT_SCALE, 1),
                "full_px": metrics["full_px"], "width_px": round(still.width * COMBAT_SCALE, 1),
                # the share of each forearm and hand the camera sees (render.py forearms_visible)
                "forearms_visible": gm.get("forearms_visible")}
            print(f"guest {g:12s} {gm['height_in']:5.1f} in  full {metrics['full_px']:6.1f} px  "
                  f"head {manifest['guests'][g]['head_px']:6.1f} px  width {manifest['guests'][g]['width_px']} px")

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
