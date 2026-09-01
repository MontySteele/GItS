#!/usr/bin/env python3
"""Recount a character's art source census: sources, (source, anchor) SLOTS, deficit.

    python tools/art_source_census.py --character kokomi
    python tools/art_source_census.py --character kokomi --art-root ../GItS
    python tools/art_source_census.py --character kokomi --tsv docs/current/art/kokomi-source-census.tsv

WHY THIS EXISTS (`EB-121`). `kokomi-art-pass-requirements.md` §2 priced her
sheet at "33 viable distinct sources yielding 70 slots" by hand on 2026-07-25.
`EB-69` then took her personal faces 62 -> 76 and the hand figure went 8 spare
-> 6 SHORT. A hand figure cannot be re-derived, only re-guessed, so the recount
is a tool: it reads the SAME two files the pipeline reads (`art/plan.tsv` for
what is claimed, `art/raw/` for the pixels) and computes the slot count from
geometry rather than from memory.

THE UNIT IS A SLOT, NOT A SOURCE. §2's own finding: "a large source backs
several distinct faces, a small transparent icon backs exactly one". A slot is
one (source, anchor) pair that renders distinct pixels.

HOW A SOURCE'S SLOTS ARE COMPUTED. `art_process.cover` scales the source to
FILL the card and crops around a fractional anchor, clamping the crop inside
the image -- so any anchor nearer an edge than half the crop renders IDENTICAL
pixels (§2, "Anchors are computed, not chosen"). The valid centre range is
therefore [f/2, 1 - f/2] where f is the fraction of the source's cropped axis
the card covers. Two knobs turn that range into a count, and BOTH are read off
the shipped plan rather than invented here:

  ANCHOR_STEP  the tightest anchor spacing the plan actually ships (Portrait's
               five anchors across a 0.347-wide range).
  REUSE_CAP    the most anchors the plan actually takes from any ONE source.
               This is the CROP-REUSE BUDGET, and it is a TASTE call, not a
               geometric one -- §6 open question 1 asks [USER] for the number
               and has never been answered. `--reuse-cap` re-runs the census at
               any candidate answer, which is the point: the deficit is a
               function of this number, not of the inventory.

The grid reproduces the shipped plan exactly on six of its eight multi-anchor
sources (Portrait, Introduction Card, Card, Game, Showcase, Character Card),
which is what licenses using it to price the unclaimed ones.

Stdlib + Pillow + PyYAML. `art/raw/` is gitignored Tier F and exists only on
the art-bearing main checkout; `--art-root` points there from a worktree
(NEVER link it in -- operations/worktrees.md). Without the pixels the census
still runs off `NATIVE_DIMS` below and says so.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from art_fetch import read_plan                                    # noqa: E402
from art_lint import BANNED_SOURCE_FAMILIES, UNDERSIZE_EXEMPT_REGISTERS  # noqa: E402

# The tightest anchor spacing the SHIPPED plan uses: Sangonomiya Kokomi
# Portrait.png takes five anchors (y0.33 y0.41 y0.50 y0.59 y0.67) across a
# valid centre range 0.347 wide. Anything tighter than this has never been
# reviewed by eye, so the census will not price it.
ANCHOR_STEP = 0.085

# The most anchors the SHIPPED plan takes from any one source -- four sources
# are at six (Card, Game, Showcase, Character Card). See the module docstring:
# this is the crop-reuse BUDGET and it belongs to [USER], not to this tool.
REUSE_CAP = 6

# Sources whose usable centre range is narrower than geometry allows, because
# something in the pixels must be cropped OUT. Hand-entered with the reason,
# the same way `art_lint.BANNED_SOURCE_FAMILIES` is: no rule can see a
# wordmark.
RESTRICTED_RANGE = {
    # 1080x1920, her best art, but the GENSHIN IMPACT wordmark sits top-centre
    # and a miHoYo logo bottom-right; a 500x380 `cover` takes a horizontal
    # band, and anchors inside [0.24, 0.74] exclude both (§2).
    "Sangonomiya Kokomi Card.png": (0.24, 0.74),
}

# Fallback geometry for a checkout with no `art/raw/`. Measured 2026-08-26 on
# the main checkout; the tool prefers real pixels whenever it can reach them
# and prints which of the two it used.
NATIVE_DIMS = {
    "Sangonomiya Kokomi Portrait.png": (4900, 5700),
    "Sangonomiya Kokomi Introduction Card.jpg": (2250, 2250),
    "Sangonomiya Kokomi Profile.png": (2400, 1320),
    "Sangonomiya Kokomi Wish.png": (2048, 1024),
    "Character Sangonomiya Kokomi Full Wish.png": (1568, 1553),
    "Sangonomiya Kokomi Card.png": (1080, 1920),
    "Character Sangonomiya Kokomi Game.png": (964, 1736),
    "Sangonomiya Kokomi Character Card Showcase.png": (700, 2646),
    "Namecard Background Sangonomiya Kokomi The Deep.png": (840, 400),
    "Sangonomiya Kokomi Multi Wish.png": (320, 1024),
    "Sangonomiya Kokomi Character Card.png": (420, 720),
    "Sangonomiya Kokomi Character Card Platinum.png": (420, 720),
    "Sangonomiya Kokomi Character Card Golden.png": (420, 720),
    "Bake-Kurage Summon.png": (420, 720),
    "Item Sango Pearl Wild.png": (797, 798),
    "Sangonomiya Kokomi Vision.png": (400, 400),
    "Item Sango Pearl.png": (256, 256),
    "Item Sangonomiya Kokomi The Deep.png": (256, 256),
    "Sangonomiya Kokomi Item.png": (256, 256),
    "Sangonomiya Kokomi Expression 1.png": (420, 420),
    "Sangonomiya Kokomi Expression 2.png": (420, 420),
    "Sangonomiya Kokomi Expression 3.png": (420, 420),
    "Side by Side We Venture Character Kokomi.png": (263, 315),
    "Icon Emoji Paimon's Paintings 09 Sangonomiya Kokomi 1.png": (300, 300),
    "Icon Emoji Paimon's Paintings 09 Sangonomiya Kokomi 2.png": (300, 300),
    "Icon Emoji Paimon's Paintings 09 Sangonomiya Kokomi 3.png": (300, 300),
    "Icon Emoji Paimon's Paintings 09 Sangonomiya Kokomi 4.png": (300, 300),
    "Icon Emoji Paimon's Paintings 13 Sangonomiya Kokomi 1.png": (300, 300),
    "Icon Emoji Paimon's Paintings 13 Sangonomiya Kokomi 2.png": (300, 300),
    "Icon Emoji Paimon's Paintings 13 Sangonomiya Kokomi 3.png": (300, 300),
    "Icon Emoji Paimon's Paintings 24 Sangonomiya Kokomi 1.png": (340, 340),
    "Icon Emoji Paimon's Paintings 25 Sangonomiya Kokomi 1.png": (340, 340),
    "Icon Emoji Paimon's Paintings 25 Sangonomiya Kokomi 2.png": (340, 340),
    "Icon Emoji Paimon's Paintings 39 Sangonomiya Kokomi.png": (340, 340),
    "Talent Nereid's Ascension.png": (128, 128),
    "Talent Kurage's Oath.png": (128, 128),
    "Talent Princess of Watatsumi.png": (128, 128),
    "Ceremonial Garment Buff Icon.png": (100, 100),
    "Nereid's Ascension Preview.gif": (480, 270),
    "Kurage's Oath Preview.gif": (480, 270),
    "Nereid's Ascension Ceremonial Garment Water Preview.gif": (480, 270),
    "Nereid's Ascension Ceremonial Garment Attack Preview.gif": (480, 270),
}

# `Bake-Kurage Summon.png` is filed `vfx` in the plan and IS one -- but §2
# names it explicitly as the one piece of kit art that is a full-size render
# rather than a sigil, and the plan already claims it at rank 1 for
# `bake_kurage`. Every other `vfx` source for her is a sigil or a clip
# thumbnail and is priced at ZERO slots (§2, "vfx IS A DEAD REGISTER FOR HER").
VFX_EXCEPTIONS = {"Bake-Kurage Summon.png"}

SHEETS = {"kokomi": "kokomi-cards.yaml", "furina": "furina-cards.yaml",
          "klee": "klee-cards.yaml"}

# Which `art/raw/` filenames belong to a character. A census that only read
# `art/plan.tsv` would report the pool as exactly the size of the bill by
# construction -- the sources nobody shortlisted are precisely the headroom
# the recount is looking for, and one of hers (Paimon's Paintings 39) is
# fetched, on disk and mentioned nowhere in the plan.
RAW_FAMILIES = {
    "kokomi": ("kokomi", "sango", "kurage", "nereid", "watatsumi",
               "ceremonial_garment"),
}


def native_dims(title, raw_dir):
    """(w, h, source) for a source title -- real pixels if reachable."""
    if raw_dir is not None:
        path = raw_dir / title.replace(" ", "_")
        if path.exists():
            try:
                from PIL import Image
                with Image.open(path) as im:
                    return im.width, im.height, "pixels"
            except Exception:                      # unreadable gif frame etc.
                pass
    dims = NATIVE_DIMS.get(title)
    return (dims[0], dims[1], "table") if dims else (None, None, "unknown")


def centre_range(sw, sh, cw, ch):
    """Valid `cover` anchor centre range, and which axis it runs along.

    Mirrors `art_process.cover`: scale = max(cw/sw, ch/sh), then crop cw*ch
    around the anchor, clamped. The cropped axis is the one the scale does NOT
    saturate; the other axis has no freedom at all.
    """
    scale = max(cw / sw, ch / sh)
    tw, th = round(sw * scale), round(sh * scale)
    if th - ch >= tw - cw:                      # vertical freedom -> y anchor
        axis, f = "y", ch / th
    else:
        axis, f = "x", cw / tw
    return axis, scale, max(0.0, f / 2), min(1.0, 1 - f / 2)


def anchor_grid(lo, hi, cap):
    """`n` anchors spread evenly across [lo, hi], endpoints included.

    Reproduces the shipped plan exactly on Portrait, Introduction Card, Card,
    Game, Showcase and Character Card -- see the module docstring.
    """
    span = hi - lo
    n = min(cap, int(span / ANCHOR_STEP) + 1)
    if n <= 1:
        return [round((lo + hi) / 2, 2)]
    return [round(lo + span * i / (n - 1), 2) for i in range(n)]


def parse_anchor(focus):
    """The anchor fraction a plan row claims, or None for a whole-source mode.

    `cover_autocrop` and `contain` have no anchor: they consume the WHOLE
    source, which is exactly why item and sticker sources are one slot each.
    """
    for part in str(focus).split(","):
        part = part.split("@", 1)[0].strip()
        if part[:1] in "xy":
            try:
                return float(part[1:])
            except ValueError:
                return None
    return None


def banned(title):
    low = title.lower()
    return any(low.startswith(p.lower()) for p, _ in BANNED_SOURCE_FAMILIES)


def census(character, art_root, reuse_cap):
    raw_dir = (art_root / "art" / "raw") if art_root else None
    if raw_dir is not None and not raw_dir.is_dir():
        raw_dir = None

    rows = [r for r in read_plan()
            if f"/cards/{character}/" in r["out"].replace("\\", "/")]
    if not rows:
        sys.exit(f"no plan rows for character '{character}'")
    claimed = [r for r in rows if r["pick"] == "auto" or r["rank"] == 1]
    cw, ch = claimed[0]["w"], claimed[0]["h"]

    # Every source the plan mentions for her at ANY rank is inventory; the
    # dead ranks are where the vfx sigils and the unclaimed stickers live, and
    # a census that only looked at rank 1 would report the pool as exactly the
    # size of the bill by construction.
    reg_of, claims, pixels = {}, {}, {}
    for r in rows:
        reg_of.setdefault(r["title"], r["register"])
    for r in claimed:
        claims.setdefault(r["title"], []).append(parse_anchor(r["focus"]))

    # Sources sitting in art/raw/ that the plan never names at any rank. Their
    # register is inferred from the plan sibling sharing the longest leading
    # word run -- "Icon Emoji Paimon's Paintings 39 ..." lands on `sticker`
    # from its 09/13/24/25 siblings. No sibling, no register, priced at zero
    # and SAID so rather than guessed.
    unplanned = set()
    if raw_dir is not None:
        fams = RAW_FAMILIES.get(character, (character,))
        for path in sorted(raw_dir.iterdir()):
            if not path.is_file():
                continue
            low = path.name.lower()
            if not any(f in low for f in fams):
                continue
            title = path.name.replace("_", " ")
            if title in reg_of:
                continue
            unplanned.add(title)
            words = title.split()
            best, best_n = None, 0
            for known in reg_of:
                kw = known.split()
                n = 0
                while n < min(len(words), len(kw)) and words[n] == kw[n]:
                    n += 1
                if n > best_n:
                    best, best_n = known, n
            reg_of[title] = reg_of[best] if (best and best_n >= 3) else None

    out = []
    for title in sorted(reg_of):
        reg = reg_of[title] or "?"
        sw, sh, src = native_dims(title, raw_dir)
        pixels[src] = pixels.get(src, 0) + 1
        used = claims.get(title, [])
        rec = {"title": title, "register": reg, "w": sw, "h": sh, "dims_from": src,
               "used": len(used), "slots": 0, "axis": "-", "lo": "", "hi": "",
               "anchors": [], "free": [], "planned": title not in unplanned,
               "note": "" if title not in unplanned else "NOT IN plan.tsv; "}
        out.append(rec)

        if reg_of[title] is None:
            rec["note"] += "no register could be inferred -- not priced"
            continue
        if banned(title):
            rec["note"] += "BANNED family (art_lint L9)"
            continue
        if sw is None:
            rec["note"] += "no dimensions -- not priced"
            continue
        # L8's test verbatim: BOTH dimensions short. Short on one axis is
        # normal and shipped -- a 420x720 TCG card is portrait-shaped by
        # construction and `cover` crops its height anyway. Only a source
        # smaller than the card in width AND height is upscaled however it is
        # cropped, and that is what makes her `vfx` register dead (S2): every
        # sigil is 128x128 and every clip frame 480x270.
        if sw < cw and sh < ch and reg not in UNDERSIZE_EXEMPT_REGISTERS:
            rec["note"] += f"undersize {sw}x{sh} < {cw}x{ch} BOTH ways (art_lint L8)"
            continue
        if reg == "vfx" and title not in VFX_EXCEPTIONS:
            rec["note"] += "vfx sigil/clip -- dead register (S2)"
            continue
        if reg in UNDERSIZE_EXEMPT_REGISTERS:
            # item/sticker are rendered `contain` / `cover_autocrop`: the whole
            # source, one picture, one slot. No anchor spread exists.
            rec.update(slots=1, anchors=["(whole)"], note="single-anchor register")
            rec["free"] = [] if used else ["(whole)"]
            continue

        axis, scale, lo, hi = centre_range(sw, sh, cw, ch)
        if title in RESTRICTED_RANGE:
            rlo, rhi = RESTRICTED_RANGE[title]
            lo, hi = max(lo, rlo), min(hi, rhi)
            rec["note"] = f"range restricted to [{rlo}, {rhi}] -- see RESTRICTED_RANGE"
        grid = anchor_grid(lo, hi, reuse_cap)
        taken = [a for a in used if a is not None]
        whole = len(used) - len(taken)          # autocrop rows: one picture each
        free = [a for a in grid
                if all(abs(a - t) > ANCHOR_STEP / 2 for t in taken)]
        if whole:
            # An autocrop row renders the source's own composition, which is
            # closest to the centre anchor; retire that one so the sheet never
            # offers a near-duplicate of a face already shipped.
            mid = min(free, key=lambda a: abs(a - 0.5), default=None)
            if mid is not None:
                free.remove(mid)
        rec.update(slots=len(grid), axis=axis, lo=round(lo, 4), hi=round(hi, 4),
                   anchors=grid, free=free)
        if scale > 1.0:
            rec["note"] = (rec["note"] + "; " if rec["note"] else "") \
                + f"upscale x{scale:.2f}"
    return out, pixels, (cw, ch)


def faces(character):
    """The character's canonical face ids, or None if the sheet is unreadable."""
    try:
        import yaml
    except ImportError:
        return None
    path = ROOT / "docs" / SHEETS.get(character, "")
    if not path.exists():
        return None
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return {r["id"] for r in rows if isinstance(r, dict) and "id" in r}


def claimed_ids(character):
    """Asset ids holding an EFFECTIVE (rank 1) plan row on the character's cards."""
    return {r["asset_id"] for r in read_plan()
            if f"/cards/{character}/" in r["out"].replace("\\", "/")
            and (r["pick"] == "auto" or r["rank"] == 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", default="kokomi")
    ap.add_argument("--art-root", type=Path, default=ROOT,
                    help="checkout whose art/raw/ holds the pixels; a worktree "
                         "has none, so point this at the main checkout by "
                         "ABSOLUTE path (never link it in -- operations/worktrees.md)")
    ap.add_argument("--reuse-cap", type=int, default=REUSE_CAP,
                    help=f"crop-reuse budget: max anchors from one source "
                         f"(default {REUSE_CAP}, the shipped plan's own maximum)")
    ap.add_argument("--tsv", type=Path, default=None,
                    help="also write the per-source table here")
    args = ap.parse_args()

    recs, pixels, (cw, ch) = census(args.character, args.art_root, args.reuse_cap)
    viable = [r for r in recs if r["slots"]]
    dead = [r for r in recs if not r["slots"]]

    print(f"art source census -- {args.character}  "
          f"(card {cw}x{ch}, step {ANCHOR_STEP}, reuse cap {args.reuse_cap})")
    print(f"dimensions from: " + ", ".join(f"{k}={v}" for k, v in sorted(pixels.items())))
    print()
    hdr = f"{'source':62s} {'reg':8s} {'native':11s} {'ax':3s} {'slots':>5s} {'used':>4s} {'free':>4s}  note"
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(recs, key=lambda r: (-r["slots"], r["register"], r["title"])):
        native = f"{r['w']}x{r['h']}" if r["w"] else "?"
        print(f"{r['title'][:62]:62s} {r['register']:8s} {native:11s} {r['axis']:3s} "
              f"{r['slots']:5d} {r['used']:4d} {len(r['free']):4d}  {r['note']}")

    by_reg = {}
    for r in viable:
        b = by_reg.setdefault(r["register"], [0, 0, 0])
        b[0] += 1
        b[1] += r["slots"]
        b[2] += r["used"]
    print()
    print(f"{'register':10s} {'sources':>7s} {'slots':>6s} {'used':>5s} {'free':>5s}")
    for reg in sorted(by_reg):
        n, s, u = by_reg[reg]
        print(f"{reg:10s} {n:7d} {s:6d} {u:5d} {s - u:5d}")
    tot_s = sum(r["slots"] for r in viable)
    tot_u = sum(r["used"] for r in viable)
    print(f"{'TOTAL':10s} {len(viable):7d} {tot_s:6d} {tot_u:5d} {tot_s - tot_u:5d}")
    free_n = sum(len(r["free"]) for r in viable)
    if free_n != tot_s - tot_u:
        # A plan row whose anchor sits BETWEEN two grid anchors retires only
        # the one it lands nearest, so the offerable count and the subtraction
        # disagree by however many rows are off-grid. The free_anchors column
        # is the operative list; the subtraction is the conservative number.
        print(f"offerable free anchors: {free_n} (subtraction says "
              f"{tot_s - tot_u}; some claims sit OFF the grid -- see free_anchors)")
    print(f"\n{len(dead)} source(s) priced at zero slots "
          f"(banned / undersize / dead vfx register)")

    bill = faces(args.character)
    if bill is not None:
        held = claimed_ids(args.character)
        unfilled = sorted(bill - held)
        offsheet = sorted(held - bill)
        gap = tot_s - len(bill)
        verdict = f"{gap:+d} slots" + (" HEADROOM" if gap >= 0 else " SHORT")
        print(f"\nbill: {len(bill)} faces on the personal sheet; "
              f"{len(bill) - len(unfilled)} hold a rank-1 plan row; "
              f"{len(unfilled)} unfilled")
        if unfilled:
            print("  unfilled: " + ", ".join(unfilled))
        if offsheet:
            # A rank-1 row for an id the sheet no longer carries still CONSUMES
            # its slot -- the picture exists and was kept deliberately. It is
            # counted in `used` and is why `used` can exceed the filled faces.
            print("  rank-1 rows for ids NOT on the sheet (slot still "
                  "consumed): " + ", ".join(offsheet))
        print(f"capacity {tot_s} slots vs {len(bill)} faces  ->  {verdict}")

    if args.tsv:
        lines = ["source\tregister\tnative_w\tnative_h\tdims_from\taxis\t"
                 "centre_lo\tcentre_hi\tslots\tclaimed\tfree_anchors\tnote"]
        for r in sorted(recs, key=lambda r: (-r["slots"], r["register"], r["title"])):
            lines.append("\t".join(str(x) for x in (
                r["title"], r["register"], r["w"] or "", r["h"] or "",
                r["dims_from"], r["axis"], r["lo"], r["hi"], r["slots"],
                r["used"], " ".join(str(a) for a in r["free"]), r["note"])))
        args.tsv.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nwrote {args.tsv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
