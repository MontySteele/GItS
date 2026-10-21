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
  model/frames/furina_gfx_<guest>.png one effect per guest star (fx.GUEST_EFFECTS:
                                      Furina's "guest-star pizazz", 2026-10-16),
                                      the manifest's `guest_fx`; no render needed:
                                      `--guest-fx-only` repacks just these into the
                                      committed manifest, `--guest-fx-sheet <png>`
                                      draws their review sheet
  model/frames/furina_<spend|drain|repay>.png  Furina's stage effects
                                      (fx.STAGE_EFFECTS), the manifest's
                                      `effects`; `--stage-fx-only [name ...]`
                                      repacks them alone, as --guest-fx-only
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
                "furina": ("idle", "idle_low", "attack", "cast", "hurt", "death", "rejoice"),
                "kokomi": ("idle", "idle_low", "attack", "cast", "hurt", "death", "ascension"),
                "yae": ("idle", "idle_low", "attack", "cast", "hurt", "death")}
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
                          "merchant": "furina_merchant.png"},
               "kokomi": {"idle": "kokomi_idle.png", "idle_low": "kokomi_idle_low.png",
                          "attack": "kokomi_attack.png", "cast": "kokomi_cast.png", "hurt": "kokomi_hurt.png",
                          "death": "kokomi_death.png", "ascension": "kokomi_ascension.png",
                          "merchant": "kokomi_merchant.png"},
               "yae": {"idle": "yae_idle.png", "idle_low": "yae_idle_low.png",
                       "attack": "yae_attack.png", "cast": "yae_cast.png", "hurt": "yae_hurt.png",
                       "death": "yae_death.png", "merchant": "yae_merchant.png"}}
FX_FILES = {"varka": {"attack": "varka_attack_fx.png", "ascension": "varka_ascension_fx.png"},
            "furina": {"attack": "furina_attack_fx.png"},
            "kokomi": {"attack": "kokomi_attack_fx.png", "ascension": "kokomi_ascension_fx.png"},
            "yae": {"attack": "yae_attack_fx.png"}}
#: effect sprite clips a combat clip places (its spec's `effects`)
EFFECT_FILES = {"varka": {"ground_burst": "varka_ground_burst.png"}}
#: effect sprite clips no clip places, played by the game on a stage event
#: (fx.STAGE_EFFECTS: Furina's Spend, Drain and Repay)
STAGE_FILES = {"furina": {"spend": "furina_spend.png", "drain": "furina_drain.png", "repay": "furina_repay.png"}}
#: one effect sprite clip per guest star, played by the game when the guest
#: acts (fx.GUEST_EFFECTS; KleeMod.Vfx.FurinaGuestFx)
GUEST_FX_FILES = {"furina": {"charlotte": "furina_gfx_charlotte.png",
                             "chevreuse": "furina_gfx_chevreuse.png",
                             "clorinde": "furina_gfx_clorinde.png",
                             "escoffier": "furina_gfx_escoffier.png",
                             "freminet": "furina_gfx_freminet.png",
                             "lynette": "furina_gfx_lynette.png",
                             "lyney": "furina_gfx_lyney.png",
                             "navia": "furina_gfx_navia.png",
                             "neuvillette": "furina_gfx_neuvillette.png",
                             "sigewinne": "furina_gfx_sigewinne.png",
                             "wriothesley": "furina_gfx_wriothesley.png"}}
SHADOW_FILES = {"varka": "varka_shadow.png", "furina": "furina_shadow.png", "kokomi": "kokomi_shadow.png",
                "yae": "yae_shadow.png"}
REST_FILES = {"varka": "varka_rest.png", "furina": "furina_rest.png", "kokomi": "kokomi_rest.png",
              "yae": "yae_rest.png"}
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


def guest_fx(char: str, ppu: float):
    """The guest effects (fx.GUEST_EFFECTS) at `ppu`, Furina's combat ppu:
    ({guest: record}, [(file, sheet)]). Each record is a packed clip as the
    stage effects' (cell, frames, pages, origin, fps, length) plus its tint
    and its anchor ("feet": the origin goes on the bottom of the creature's
    hitbox; "center": on its effect spawn point)."""
    recs, writes = {}, []
    for name, file in GUEST_FX_FILES.get(char, {}).items():
        frames, origin = FX.GUEST_EFFECTS[name](ppu, FX.STAGE_FPS)
        esheets, erec = sheets_for(frames, origin, file)
        erec.update({"fps": FX.STAGE_FPS, "ppu": ppu, "length": round(len(frames) / FX.STAGE_FPS, 4), "loop": False,
                     "heat": "R=G=B heat (1 core, ~0.5 glow), A coverage; tint per element",
                     "tint": FX.GUEST_TINTS[name], "anchor": FX.GUEST_ANCHOR[name]})
        recs[name] = erec
        writes += esheets
    return recs, writes


def stage_fx(char: str, name: str, ppu: float):
    """One stage effect (fx.STAGE_EFFECTS) at `ppu`, Furina's combat ppu:
    (record, [(file, sheet)])."""
    frames, origin, to = FX.STAGE_EFFECTS[name](ppu, FX.STAGE_FPS)
    esheets, erec = sheets_for(frames, origin, STAGE_FILES[char][name])
    erec.update({"fps": FX.STAGE_FPS, "ppu": ppu, "length": round(len(frames) / FX.STAGE_FPS, 4), "loop": False,
                 "heat": "R=G=B heat (1 core, ~0.5 glow), A coverage; tint per element",
                 "tint": FX.STAGE_TINTS[name], "uses": [],
                 "anchor": "origin is Furina's chest" + ("; `to` the first guest seat" if to else "")})
    if to:
        # the far end, in the trimmed cell's px (as `origin`)
        erec["to"] = [round(to[0] - origin[0] + erec["origin"][0]), round(to[1] - origin[1] + erec["origin"][1])]
    return erec, esheets


def stage_fx_only(char: str, names: list, art: Path, check: bool) -> int:
    """Repack the named stage effects alone into the committed manifest, which
    keeps every other record (and the effects' order): they need no render."""
    mpath = manifest_path(char)
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    ppu = manifest["sheets"]["idle"]["ppu"]
    sheets = []
    for name in names:
        assert name in STAGE_FILES.get(char, {}), f"{name}: not a stage effect of {char}"
        manifest["effects"][name], es = stage_fx(char, name, ppu)
        sheets += es
    text = json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"
    if check:
        if mpath.read_text(encoding="utf-8") != text:
            print(f"STALE: {mpath.name}'s effects {names} differ from fx.STAGE_EFFECTS")
            return 1
        print(f"{mpath.name}'s effects {names} are current")
        return 0
    for file, im in sheets:
        path = art / "model" / "frames" / file
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path, optimize=True)
        print("wrote", path)
    mpath.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", mpath.relative_to(ROOT))
    return 0


#: the review sheet: six key frames per guest, one row each, at game scale
SHEET_CELL = 330
SHEET_BACKDROP = (22, 24, 32, 255)


def guest_fx_sheet(char: str, ppu: float) -> Image.Image:
    """Every guest effect's six key frames (first to last, evenly), tinted as
    the game tints them, at the combat scale on a dark backdrop. A red tick
    marks the anchor (a "feet" effect's anchor sits lower in its row)."""
    from PIL import ImageDraw
    names = list(GUEST_FX_FILES[char])
    sheet = Image.new("RGBA", (120 + 6 * SHEET_CELL, len(names) * SHEET_CELL), SHEET_BACKDROP)
    d = ImageDraw.Draw(sheet)
    for r, name in enumerate(names):
        frames, origin = FX.GUEST_EFFECTS[name](ppu, FX.STAGE_FPS)
        n = len(frames)
        d.text((8, r * SHEET_CELL + SHEET_CELL // 2 - 6), f"{name}\n{n / FX.STAGE_FPS:.2f} s",
               fill=(220, 220, 220, 255))
        for j, fi in enumerate(round(i * (n - 1) / 5) for i in range(6)):
            im = FX.tint(frames[fi], FX.hex_rgb(FX.GUEST_TINTS[name]))
            im = im.resize((round(im.width * COMBAT_SCALE), round(im.height * COMBAT_SCALE)), Image.LANCZOS)
            ox, oy = origin[0] * COMBAT_SCALE, origin[1] * COMBAT_SCALE
            ax = 120 + j * SHEET_CELL + SHEET_CELL // 2
            ay = r * SHEET_CELL + SHEET_CELL // 2 + (60 if FX.GUEST_ANCHOR[name] == "feet" else 0)
            sheet.alpha_composite(im, (max(0, round(ax - ox)), max(0, round(ay - oy))))
            d.line((ax - 5, ay, ax + 5, ay), fill=(255, 80, 80, 255))
            d.line((ax, ay - 5, ax, ay + 5), fill=(255, 80, 80, 255))
            d.text((120 + j * SHEET_CELL + 4, r * SHEET_CELL + 4), f"frame {fi}", fill=(150, 150, 150, 255))
    return sheet.convert("RGB")


def guest_fx_only(char: str, art: Path, check: bool) -> int:
    """Repack the guest effects alone into the committed manifest, which keeps
    every other record: they need no render."""
    mpath = manifest_path(char)
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    recs, sheets = guest_fx(char, manifest["sheets"]["idle"]["ppu"])
    manifest["guest_fx"] = recs
    text = json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"
    if check:
        if mpath.read_text(encoding="utf-8") != text:
            print(f"STALE: {mpath.name}'s guest_fx differs from fx.GUEST_EFFECTS")
            return 1
        print(f"{mpath.name}'s guest_fx is current")
        return 0
    for name, im in sheets:
        path = art / "model" / "frames" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path, optimize=True)
        print("wrote", path)
    mpath.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", mpath.relative_to(ROOT))
    return 0


def rest_still(R: Path):
    """BaseLib centres the texture at y = -0.1 h inside a 0.5 container, so a
    point at (w/2, 0.6 h) of the texture lands on the anchor: pad so the seat
    (the hips' head) is that point (Klee's rule).

    NO GROUND CLIP. The combat clips cut below the feet anchor so planted
    blades read as driven into the floor; a seated still has no floor at that
    line (the rig's origin sits above the boots and the hem), and the cut drew
    Varka's sword tips, cloak and seat, and Furina's coat hem, on one flat
    edge, so he seemed to float in front of the log (in-game check
    2026-10-16). The still keeps every texel it rendered."""
    meta = json.loads((R / "rest.json").read_text(encoding="utf-8"))
    rest = Image.open(R / "rest.png").convert("RGBA")
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


def select_placer(R: Path, target_h: int = 2150):
    """The close-up's framing as a function: (place, rec). `place(im, at=(0, 0))`
    puts an image rendered at the select still's camera and scale (its pixel
    (0, 0) at `at` on the still's canvas) onto the 1920x1080 close-up, ground
    clip, crop, scale and position exactly as the still's. The still itself
    is `place(still)`; tools/select_loop.py places the loop's frames the same
    way, so frame 0 is the still."""
    meta = json.loads((R / "select.json").read_text(encoding="utf-8"))
    s = float(meta["ppu"]) / FX.REF_PPU
    sel = Image.open(R / "select.png").convert("RGBA")
    sel = ground_clip(sel, meta["origin_px"][1], s)
    bx, by, bx1, by1 = KP.alpha_box([sel])
    sel = sel.crop((bx, by, bx1, by1))
    guards = {g: v["guard_box_px"] for g, v in ((meta.get("arms_crossed") or {}).get("hilts") or {}).items()}
    if guards:
        low = max(g[3] for g in guards.values()) - by
        target_h = min(target_h, math.floor((1080 - SELECT_KEEP - SELECT_TOP) * sel.height / low))
    k = target_h / sel.height
    new_w = round(sel.width * k)
    cx = min(1260, 1920 - SELECT_SIDE - (new_w - new_w // 2))
    x0 = cx - new_w // 2
    rec = {"size": [1920, 1080], "figure_h": target_h}

    def to_canvas(x, y):
        return [round((x - bx) * k + x0, 1), round((y - by) * k + SELECT_TOP, 1)]
    if guards:
        rec["guards_px"] = {g: to_canvas(v[0], v[1]) + to_canvas(v[2], v[3]) for g, v in sorted(guards.items())}
        rec["chin_px"] = to_canvas(0, meta["arms_crossed"]["chin_px"])[1]

    def place(im: Image.Image, at=(0, 0)) -> Image.Image:
        pad = 96            # a moving frame may reach past the still's canvas
        base = Image.new("RGBA", (sel.width + bx + pad * 2 + im.width, sel.height + by + pad * 2 + im.height),
                         (0, 0, 0, 0))
        # the still's canvas, shifted by `pad`, holds the frame at `at`
        base.paste(im, (round(at[0]) + pad, round(at[1]) + pad))
        base = ground_clip(base, meta["origin_px"][1] + pad, s)
        part = base.crop((bx + pad, by + pad, bx1 + pad, by1 + pad))
        part = part.resize((new_w, target_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        canvas.paste(part, (x0, SELECT_TOP), part)
        return canvas
    return place, rec


def select_closeup(R: Path, target_h: int = 2150):
    """1920x1080, the figure right of centre, bleeding off the bottom (Klee's
    framing). When the still records its blades' crossguards (render.py
    arms_crossed, stance B), the figure is drawn smaller if it must be, so
    both crossguards sit inside the frame, and moved left if its right edge
    would leave it. The manifest gets where the crossguards and the chin land."""
    place, rec = select_placer(R, target_h)
    return place(Image.open(R / "select.png").convert("RGBA")), rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--char", default="varka", choices=sorted(SHEET_FILES))
    ap.add_argument("--renders", help="render.py --out dir, painted by post.py")
    ap.add_argument("--art-root", default=str(ROOT))
    ap.add_argument("--check", action="store_true", help="only report; write nothing")
    ap.add_argument("--guest-fx-only", action="store_true",
                    help="repack only the guest effects into the committed manifest (no renders)")
    ap.add_argument("--stage-fx-only", nargs="*", metavar="NAME",
                    help="repack only these stage effects (default all) into the committed manifest (no renders)")
    ap.add_argument("--guest-fx-sheet", metavar="PNG", help="draw the guest effects' review sheet and exit")
    args = ap.parse_args(argv)
    char = args.char
    art = Path(args.art_root) / "ImageGen" / "images" / char
    if args.guest_fx_sheet:
        ppu = json.loads(manifest_path(char).read_text(encoding="utf-8"))["sheets"]["idle"]["ppu"]
        guest_fx_sheet(char, ppu).save(args.guest_fx_sheet, optimize=True)
        print("wrote", args.guest_fx_sheet)
        return 0
    if args.guest_fx_only:
        return guest_fx_only(char, art, args.check)
    if args.stage_fx_only is not None:
        return stage_fx_only(char, args.stage_fx_only or list(STAGE_FILES.get(char, {})), art, args.check)
    if not args.renders:
        ap.error("--renders is required")
    R = Path(args.renders)
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
    for name in STAGE_FILES.get(char, {}):
        erec, esheets = stage_fx(char, name, manifest["sheets"]["idle"]["ppu"])
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

    # the guest stars' effects (fx.GUEST_EFFECTS), at the combat ppu
    if GUEST_FX_FILES.get(char):
        recs, gsheets = guest_fx(char, manifest["sheets"]["idle"]["ppu"])
        manifest["guest_fx"] = recs
        writes += [(out_frames / n, im) for n, im in gsheets]

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
