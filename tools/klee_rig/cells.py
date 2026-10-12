"""Occupancy grid extraction: combat layer PNGs -> klee_cells.json.

The only step that needs pixels. It runs where the art lives (the main
checkout's `ImageGen/`, reached from a worktree with `--art-root`, the same
door `cut_combat_layers.py` uses) and writes a small committed JSON, so the
scene generator, the tests and CI need no art at all.

What it records, per layer:

* the texture size and where the texture's top-left sits in rig space (from
  the cutter's `layers_combat.json` manifest, so the mesh lands exactly where
  the old centred Sprite2D drew the same texture);
* a cell grid at the layer's pitch: a cell is OCCUPIED when any texel inside
  it, grown by one texel for the bilinear footprint, has alpha > 0; the
  occupied set is then dilated by one cell, so every pixel the old sprite
  drew is inside a triangle at rest (tested by `verify.coverage`);
* for the Floaters layer, which island owns each cell: 8-connected
  components of alpha > 2, islands under `floater_min_mass` folded into the
  nearest big one, each cell given to the island holding most of its alpha,
  and every big island's alpha-weighted centroid (its bone's joint).

Row strings use '.' for empty, '#' for occupied, and 'a'.. for an island.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import numpy as np

LAYER_DIR = Path("ImageGen/images/model/layers/combat")
MANIFEST = LAYER_DIR / "layers_combat.json"


def _components(mask: np.ndarray) -> tuple[np.ndarray, int]:
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not lab[y, x]:
                n += 1
                lab[y, x] = n
                q = deque([(y, x)])
                while q:
                    cy, cx = q.popleft()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = cy + dy, cx + dx
                            if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                                lab[yy, xx] = n
                                q.append((yy, xx))
    return lab, n


def _grow(mask: np.ndarray, r: int) -> np.ndarray:
    out = mask.copy()
    h, w = mask.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            sh = np.zeros_like(mask)
            ys = slice(max(0, dy), h + min(0, dy))
            yd = slice(max(0, -dy), h + min(0, -dy))
            xs = slice(max(0, dx), w + min(0, dx))
            xd = slice(max(0, -dx), w + min(0, -dx))
            sh[yd, xd] = mask[ys, xs]
            out |= sh
    return out


def _cell_grid(alpha: np.ndarray, cell: int) -> np.ndarray:
    h, w = alpha.shape
    gw, gh = -(-w // cell), -(-h // cell)
    lit = _grow(alpha > 0, 1)
    occ = np.zeros((gh, gw), bool)
    for gy in range(gh):
        for gx in range(gw):
            occ[gy, gx] = lit[gy * cell:(gy + 1) * cell, gx * cell:(gx + 1) * cell].any()
    return _grow(occ, 1)


def _islands(alpha: np.ndarray, cell: int, occ: np.ndarray, min_mass: float):
    lab, n = _components(alpha > 2)
    mass = np.bincount(lab.ravel(), weights=alpha.ravel() / 255.0, minlength=n + 1)
    big = [i for i in range(1, n + 1) if mass[i] >= min_mass]
    # Order islands top-to-bottom, left-to-right by centroid: a stable naming.
    cents = {}
    for i in big:
        ys, xs = np.nonzero(lab == i)
        wts = alpha[ys, xs].astype(np.float64)
        cents[i] = (float((xs * wts).sum() / wts.sum()), float((ys * wts).sum() / wts.sum()))
    big.sort(key=lambda i: (round(cents[i][1]), round(cents[i][0])))
    rank = {old: k for k, old in enumerate(big)}
    # Every alpha texel -> nearest big island (by texel distance to its pixels).
    big_mask = np.isin(lab, big)
    bys, bxs = np.nonzero(big_mask)
    bl = np.array([rank[v] for v in lab[bys, bxs]])
    h, w = alpha.shape
    owner = np.full((h, w), -1, np.int32)
    owner[bys, bxs] = bl
    for y, x in zip(*np.nonzero((alpha > 0) & ~big_mask)):
        d = (bxs - x) ** 2 + (bys - y) ** 2
        owner[y, x] = bl[int(np.argmin(d))]
    gh, gw = occ.shape
    labels = np.full((gh, gw), -1, np.int32)
    cell_cent = []
    for gy in range(gh):
        for gx in range(gw):
            if not occ[gy, gx]:
                continue
            blk_o = owner[gy * cell:(gy + 1) * cell, gx * cell:(gx + 1) * cell]
            blk_a = alpha[gy * cell:(gy + 1) * cell, gx * cell:(gx + 1) * cell].astype(np.float64)
            votes = np.zeros(len(big))
            for k in range(len(big)):
                votes[k] = blk_a[blk_o == k].sum()
            if votes.max() > 0:
                labels[gy, gx] = int(np.argmax(votes))
            else:
                cell_cent.append((gy, gx))
    # Empty dilation cells take the nearest labelled cell's island.
    lys, lxs = np.nonzero(labels >= 0)
    for gy, gx in cell_cent:
        d = (lxs - gx) ** 2 + (lys - gy) ** 2
        k = int(np.argmin(d))
        labels[gy, gx] = labels[lys[k], lxs[k]]
    centroids = [[round(cents[i][0], 2), round(cents[i][1], 2)] for i in big]
    return labels, centroids


def extract(spec: dict, art_root: Path) -> dict:
    from PIL import Image

    manifest = json.loads((art_root / MANIFEST).read_text(encoding="utf-8"))
    cw, ch = manifest["canvas"]
    out = {"canvas": [cw, ch], "layers": {}}
    for layer in spec["layers"]:
        name, cell = layer["name"], int(layer["cell"])
        entry = manifest["layers"][name.lower()]
        assert entry["file"] == layer["texture"], (entry["file"], layer["texture"])
        img = Image.open(art_root / LAYER_DIR / layer["texture"]).convert("RGBA")
        alpha = np.asarray(img)[..., 3].astype(np.int32)
        h, w = alpha.shape
        assert (w, h) == (entry["w"], entry["h"]), name
        # Texture top-left in rig space: the old Sprite2D was centred on the
        # manifest offset, which is itself relative to the box centre (= Rig).
        tl = [entry["offset_x"] - w / 2, entry["offset_y"] - h / 2]
        assert all(v == int(v) for v in tl), (name, tl)
        occ = _cell_grid(alpha, cell)
        rec = {"texture": [w, h], "topleft": [int(tl[0]), int(tl[1])], "cell": cell}
        if spec["skin"][name]["mode"] == "islands":
            labels, cents = _islands(alpha, cell, occ, float(spec["floater_min_mass"]))
            rec["rows"] = ["".join("." if v < 0 else chr(97 + v) for v in row) for row in labels]
            rec["islands"] = [[round(c[0] + tl[0], 2), round(c[1] + tl[1], 2)] for c in cents]
        else:
            rec["rows"] = ["".join("#" if v else "." for v in row) for row in occ]
        out["layers"][name] = rec
    return out


def dump(data: dict) -> str:
    """Stable JSON: one grid row per line so a diff reads as a picture."""
    lines = ["{", f'  "canvas": {json.dumps(data["canvas"])},', '  "layers": {']
    names = list(data["layers"])
    for li, name in enumerate(names):
        rec = data["layers"][name]
        lines.append(f'    "{name}": {{')
        lines.append(f'      "texture": {json.dumps(rec["texture"])},')
        lines.append(f'      "topleft": {json.dumps(rec["topleft"])},')
        lines.append(f'      "cell": {rec["cell"]},')
        if "islands" in rec:
            lines.append(f'      "islands": {json.dumps(rec["islands"])},')
        lines.append('      "rows": [')
        for ri, row in enumerate(rec["rows"]):
            lines.append(f'        "{row}"' + ("," if ri < len(rec["rows"]) - 1 else ""))
        lines.append("      ]")
        lines.append("    }" + ("," if li < len(names) - 1 else ""))
    lines += ["  }", "}"]
    return "\n".join(lines) + "\n"
