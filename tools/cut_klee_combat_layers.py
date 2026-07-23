"""Cut the Klee wish splash into animated combat-model layers.

Animation sprint 1, Track B (2026-07-23). Produces the gitignored layer art:

    ImageGen/images/model/layers/klee_layer_{smoke,floaters,dumpty,body,dodoco}.png
    ImageGen/images/model/layers/layers.json            (full-res masters)
    ImageGen/images/model/layers/combat/klee_combat_*.png
    ImageGen/images/model/layers/combat/layers_combat.json  (shipped, 240x280 box)

from ImageGen/images/model/character_klee_full_wish.png (1069x1245).

Method: alpha connected components make every free-floating element (bell
bombs, flowers, launch trails, clovers) a "floaters" island for free; gray
low-saturation islands join the smoke instead. The one merged blob
(Klee + giant Jumpy Dumpty + blast smoke + Dodoco) is hard-partitioned by the
hand-digitized fence polylines below + seeded flood fill; leftover pixels
(fence lines, slivers) are assigned by priority dilation
dodoco > dumpty > body > smoke > floaters, so outlines stay with the object
in front. Hard partition = at-rest recomposition is pixel-exact by
construction (asserted).

Fill-behind: lower layers are inpainted (edge-extension onion peel) where
movers cover them — smoke 32 px behind dumpty/body/dodoco, body 20 px behind
dodoco — sized for the worst-case relative idle amplitudes in
klee-mod/pck-src/klee/model/combat.tscn (~27 source px) plus AA slack.

The fence coordinates are specific to this artwork revision (see
art/SOURCES.tsv for its URL). If the source image changes, re-digitize.

Usage: .venv/Scripts/python tools/cut_klee_combat_layers.py
"""
from collections import deque
from pathlib import Path
import json
import os

from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ImageGen" / "images" / "model" / "character_klee_full_wish.png"
OUT = ROOT / "ImageGen" / "images" / "model" / "layers"

# ---- fence polylines (full-res px, digitized 2026-07-23) -------------------
F1_DUMPTY_SMOKE = [
    (450, 0), (470, 60), (485, 110), (500, 150), (507, 200), (500, 250),
    (494, 300), (490, 340), (497, 375), (492, 398),
]
F2_DUMPTY_BODY = [
    (0, 525), (80, 520), (150, 510), (230, 500), (270, 497), (295, 480),
    (302, 464), (330, 462), (360, 466), (390, 472), (410, 468), (430, 455),
    (450, 440), (470, 420), (485, 408), (492, 398),
]
F3_BODY_SMOKE = [
    (492, 398), (500, 410), (510, 404), (540, 397), (575, 394), (610, 401),
    (635, 414), (650, 431), (662, 440), (668, 425), (678, 415), (692, 410),
    (705, 415), (715, 428), (718, 445), (712, 462), (703, 478), (695, 490),
    (690, 500), (695, 505), (705, 508), (720, 510), (735, 501), (752, 493),
    (766, 494), (780, 500), (793, 505), (804, 508), (812, 512), (816, 520),
    (810, 528), (796, 534), (780, 539), (762, 544), (748, 549), (740, 556),
    (732, 566), (724, 578), (714, 590), (702, 602), (688, 614), (672, 626),
    (662, 645), (658, 662), (658, 678), (660, 690),
]
F4_DODOCO = [
    (628, 678), (640, 670), (650, 678), (662, 695), (668, 720), (676, 745),
    (680, 770), (688, 782), (705, 788), (722, 795), (735, 808), (738, 825),
    (730, 838), (715, 848), (695, 852), (675, 850), (658, 842), (655, 850),
    (640, 852), (628, 845), (615, 832), (605, 815), (602, 790), (605, 772),
    (592, 765), (585, 745), (596, 730), (608, 725), (613, 700), (628, 678),
]

# layer ids: 1 smoke, 2 body, 3 dumpty, 4 dodoco, 5 floaters
NAMES = {1: "smoke", 2: "body", 3: "dumpty", 4: "dodoco", 5: "floaters"}
# smoke gets extra seeds: the under-arm bulge + wisp spikes are cut off from
# the main cloud by the arm itself, so they cannot flood from the top seed.
SEEDS = [
    (3, (300, 250)), (1, (650, 200)), (1, (750, 650)), (1, (700, 730)),
    (2, (500, 600)), (4, (640, 780)),
]


def flood(open_px, part, lid, sx, sy):
    H, W = open_px.shape
    q = deque([(sy, sx)])
    part[sy, sx] = lid
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and open_px[ny, nx] and not part[ny, nx]:
                part[ny, nx] = lid
                q.append((ny, nx))


def components(fg):
    H, W = fg.shape
    labels = np.zeros((H, W), np.int32)
    cur = 0
    for sy in range(H):
        for sx in np.nonzero(fg[sy] & (labels[sy] == 0))[0]:
            if labels[sy, sx]:
                continue
            cur += 1
            q = deque([(sy, sx)])
            labels[sy, sx] = cur
            while q:
                y, x = q.popleft()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < H and 0 <= nx < W and fg[ny, nx]
                                and not labels[ny, nx]):
                            labels[ny, nx] = cur
                            q.append((ny, nx))
    return labels, cur


def dilate(mask, n):
    m = mask.copy()
    for _ in range(n):
        g = m.copy()
        g[1:, :] |= m[:-1, :]
        g[:-1, :] |= m[1:, :]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    return m


def onion_fill(img, have, want):
    H, W = have.shape
    img = img.copy()
    have = have.copy()
    for _ in range(64):
        todo = want & ~have
        if not todo.any():
            break
        acc = np.zeros_like(img)
        cnt = np.zeros((H, W), np.float64)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)):
            sh = np.zeros_like(img)
            sc = np.zeros((H, W), np.float64)
            ys0, ys1 = max(dy, 0), H + min(dy, 0)
            xs0, xs1 = max(dx, 0), W + min(dx, 0)
            sh[ys0:ys1, xs0:xs1] = img[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            sc[ys0:ys1, xs0:xs1] = have[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            acc += sh * sc[..., None]
            cnt += sc
        ring = todo & (cnt > 0)
        img[ring] = acc[ring] / cnt[ring][..., None]
        have |= ring
    return img


def main():
    rgba = np.asarray(Image.open(SRC).convert("RGBA")).astype(np.float64)
    H, W = rgba.shape[:2]
    fg = rgba[..., 3] > 16
    labels, ncomp = components(fg)
    blob = 1 + int(np.argmax(np.bincount(labels[labels > 0])[1:]))

    fence_im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fence_im)
    for line in (F1_DUMPTY_SMOKE, F2_DUMPTY_BODY, F3_BODY_SMOKE, F4_DODOCO):
        d.line(line, fill=255, width=3)
    fence = np.asarray(fence_im) > 0

    part = np.zeros((H, W), np.uint8)
    open_px = (labels == blob) & ~fence
    for lid, (sx, sy) in SEEDS:
        assert open_px[sy, sx], f"seed {lid}@({sx},{sy}) not open"
        if part[sy, sx]:
            assert part[sy, sx] == lid, \
                f"seed {lid}@({sx},{sy}) hit region {part[sy, sx]} - fences leak"
            continue
        flood(open_px, part, lid, sx, sy)

    # unreached enclaves (cut off from every seed) are background stuff
    part[open_px & (part == 0)] = 1

    # satellite components: gray wisps join smoke, everything else floats
    sat = (np.max(rgba[..., :3], axis=2) - np.min(rgba[..., :3], axis=2))
    for comp in range(1, ncomp + 1):
        if comp == blob:
            continue
        m = labels == comp
        part[m] = 1 if sat[m].mean() < 35 else 5

    # leftover px (fence lines): priority dilation, foreground object wins
    prio = {4: 5, 3: 4, 2: 3, 1: 2, 5: 1}
    left = fg & (part == 0)
    while left.any():
        assigned = {}
        for y, x in zip(*np.nonzero(left)):
            cand = [part[y + dy, x + dx]
                    for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if 0 <= y + dy < H and 0 <= x + dx < W
                    and part[y + dy, x + dx]]
            if cand:
                assigned[(y, x)] = max(cand, key=lambda v: prio[v])
        if not assigned:
            raise SystemExit(f"unassignable px remain: {int(left.sum())}")
        for (y, x), v in assigned.items():
            part[y, x] = v
            left[y, x] = False

    assert ((part > 0) == fg).all(), "partition must cover fg exactly"

    layers = {}
    for lid, name in NAMES.items():
        m = part == lid
        img = np.zeros_like(rgba)
        img[m] = rgba[m]
        layers[name] = (img, m)

    smoke_img, smoke_m = layers["smoke"]
    behind = dilate(smoke_m, 32) & ((part == 2) | (part == 3) | (part == 4))
    layers["smoke"] = (onion_fill(smoke_img, smoke_m, behind), smoke_m | behind)
    body_img, body_m = layers["body"]
    behind_b = dilate(body_m, 20) & (part == 4)
    layers["body"] = (onion_fill(body_img, body_m, behind_b), body_m | behind_b)

    os.makedirs(OUT / "combat", exist_ok=True)
    meta, PAD = {}, 4
    for name, (img, m) in layers.items():
        ys, xs = np.nonzero(m)
        x0, x1 = max(0, xs.min() - PAD), min(W, xs.max() + 1 + PAD)
        y0, y1 = max(0, ys.min() - PAD), min(H, ys.max() + 1 + PAD)
        Image.fromarray(np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8),
                        "RGBA").save(OUT / f"klee_layer_{name}.png")
        meta[name] = {"file": f"klee_layer_{name}.png",
                      "w": int(x1 - x0), "h": int(y1 - y0),
                      "offset_x": round((x0 + x1) / 2 - W / 2, 1),
                      "offset_y": round((y0 + y1) / 2 - H / 2, 1)}
        print(f"{name:9s} {x1 - x0}x{y1 - y0} "
              f"offset=({meta[name]['offset_x']:+.1f},{meta[name]['offset_y']:+.1f})")
    (OUT / "layers.json").write_text(
        json.dumps({"canvas": [W, H], "layers": meta}, indent=2))

    # combat-scale derivatives: same 240x280 box the static model used
    CW, CH = 240, 280
    cmeta = {}
    for name, (img, m) in layers.items():
        full = np.zeros((H, W, 4), np.float64)
        full[m] = img[m]
        small = Image.fromarray(np.clip(full, 0, 255).astype(np.uint8),
                                "RGBA").resize((CW, CH), Image.LANCZOS)
        sa = np.asarray(small)
        ys, xs = np.nonzero(sa[..., 3] > 2)
        P = 2
        x0, x1 = max(0, xs.min() - P), min(CW, xs.max() + 1 + P)
        y0, y1 = max(0, ys.min() - P), min(CH, ys.max() + 1 + P)
        small.crop((x0, y0, x1, y1)).save(OUT / "combat" / f"klee_combat_{name}.png")
        cmeta[name] = {"file": f"klee_combat_{name}.png",
                       "w": int(x1 - x0), "h": int(y1 - y0),
                       "offset_x": round((x0 + x1) / 2 - CW / 2, 1),
                       "offset_y": round((y0 + y1) / 2 - CH / 2, 1)}
        print(f"combat {name:9s} {x1 - x0}x{y1 - y0} "
              f"offset=({cmeta[name]['offset_x']:+.1f},{cmeta[name]['offset_y']:+.1f})")
    (OUT / "combat" / "layers_combat.json").write_text(
        json.dumps({"canvas": [CW, CH], "layers": cmeta}, indent=2))
    print("The combat.tscn sprite offsets must match layers_combat.json.")


if __name__ == "__main__":
    main()
