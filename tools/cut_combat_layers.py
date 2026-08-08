"""Cut a character render into animated combat-model layers.

Animation sprint 2, Track B1 (2026-07-24). Generalization of
tools/cut_klee_combat_layers.py, which was written for exactly one artwork.
Klee's fences become config #1 (tools/combat_layer_fences/klee.yaml); Furina
is config #2; Kokomi's kickoff is already in the tree, which was the
third-instance-incoming signal that made generalizing worth it now.

    .venv/Scripts/python tools/cut_combat_layers.py klee
    .venv/Scripts/python tools/cut_combat_layers.py furina
    .venv/Scripts/python tools/cut_combat_layers.py klee --check

`--check` re-cuts into a temp dir and diffs against what is on disk. Klee's
output is byte-identical to the pre-generalization tool's, and that is the
regression this flag exists to protect: the generalization must not have
quietly changed the shipped art.

METHOD (unchanged from the Klee tool; the docstring there is the long form).
Alpha connected components make every free-floating element its own island
for free; islands whose mean saturation is low join a designated layer
instead. The one merged blob is hard-partitioned by hand-digitized fence
polylines + seeded flood fill; leftover pixels (the fence lines themselves)
are assigned by priority dilation so outlines stay with the object in front.
Hard partition => at-rest recomposition is pixel-exact by construction
(asserted). Lower layers are then inpainted (edge-extension onion peel) where
movers cover them, sized for the worst-case relative idle amplitude in that
character's combat.tscn.

Fence coordinates are specific to one artwork revision (each config names its
source and that source's URL is in art/SOURCES.tsv). If the source image
changes, re-digitize.
"""
from collections import deque
from pathlib import Path
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(__file__).resolve().parent / "combat_layer_fences"


# ---------------------------------------------------------------- config ---

class Config:
    """A per-character fence config. Validated on load, loudly."""

    def __init__(self, name, raw):
        self.name = name
        self.source = ROOT / raw["source"]
        self.out_dir = ROOT / raw["out_dir"]
        self.file_prefix = raw["file_prefix"]
        self.alpha_threshold = int(raw.get("alpha_threshold", 16))
        self.combat_box = tuple(raw["combat_box"])
        self.master_pad = int(raw.get("master_pad", 4))
        self.combat_pad = int(raw.get("combat_pad", 2))

        self.layers = list(raw["layers"])
        self.names = {int(l["id"]): l["name"] for l in self.layers}
        self.by_name = {l["name"]: int(l["id"]) for l in self.layers}
        self.priority = {int(l["id"]): int(l["dilate_priority"])
                         for l in self.layers}

        if len(self.names) != len(self.layers):
            raise SystemExit(f"[{name}] duplicate layer id")
        if len(self.by_name) != len(self.layers):
            raise SystemExit(f"[{name}] duplicate layer name")
        if sorted(self.priority.values()) != list(range(1, len(self.layers) + 1)):
            raise SystemExit(
                f"[{name}] dilate_priority must be a permutation of "
                f"1..{len(self.layers)} -- got {sorted(self.priority.values())}")

        fences = raw.get("fences", {})
        self.fence_width = int(fences.get("width", 3))
        self.fence_lines = [
            [tuple(p) for p in line["points"]]
            for line in fences.get("lines", [])
        ]
        self.seeds = [(self._id(s["layer"], "seed"), tuple(s["at"]))
                      for s in raw["seeds"]]

        self.unreached_layer = self._id(raw["unreached_layer"], "unreached_layer")

        sat = raw.get("satellites")
        self.satellites = None
        if sat:
            self.satellites = (
                self._id(sat["low_saturation_layer"], "satellites"),
                float(sat["saturation_threshold"]),
                self._id(sat["other_layer"], "satellites"),
            )

        self.fill_behind = [
            (self._id(f["layer"], "fill_behind"), int(f["radius"]),
             [self._id(n, "fill_behind") for n in f["covered_by"]])
            for f in raw.get("fill_behind", [])
        ]

    def _id(self, layer_name, where):
        if layer_name not in self.by_name:
            raise SystemExit(
                f"[{self.name}] {where} names unknown layer {layer_name!r}; "
                f"known: {sorted(self.by_name)}")
        return self.by_name[layer_name]


def load_config(name):
    path = CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        have = sorted(p.stem for p in CONFIG_DIR.glob("*.yaml"))
        raise SystemExit(f"no fence config {path}; have: {have}")
    return Config(name, yaml.safe_load(path.read_text(encoding="utf-8")))


# ------------------------------------------------------------ primitives ---

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


# ------------------------------------------------------------------ cut ----

def partition(cfg, rgba):
    """Hard-partition the foreground into layer ids. Covers fg exactly."""
    H, W = rgba.shape[:2]
    fg = rgba[..., 3] > cfg.alpha_threshold
    labels, ncomp = components(fg)
    if ncomp == 0:
        raise SystemExit(f"[{cfg.name}] source has no foreground pixels")
    blob = 1 + int(np.argmax(np.bincount(labels[labels > 0])[1:]))

    fence_im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fence_im)
    for line in cfg.fence_lines:
        d.line(line, fill=255, width=cfg.fence_width)
    fence = np.asarray(fence_im) > 0

    part = np.zeros((H, W), np.uint8)
    open_px = (labels == blob) & ~fence
    for lid, (sx, sy) in cfg.seeds:
        if not (0 <= sx < W and 0 <= sy < H):
            raise SystemExit(f"[{cfg.name}] seed {lid}@({sx},{sy}) out of bounds")
        assert open_px[sy, sx], f"seed {lid}@({sx},{sy}) not open"
        if part[sy, sx]:
            assert part[sy, sx] == lid, \
                f"seed {lid}@({sx},{sy}) hit region {part[sy, sx]} - fences leak"
            continue
        flood(open_px, part, lid, sx, sy)

    # unreached enclaves (cut off from every seed)
    part[open_px & (part == 0)] = cfg.unreached_layer

    # satellite components: low-saturation islands join one layer, rest another
    if cfg.satellites is not None:
        low_lid, thresh, other_lid = cfg.satellites
        sat = (np.max(rgba[..., :3], axis=2) - np.min(rgba[..., :3], axis=2))
        for comp in range(1, ncomp + 1):
            if comp == blob:
                continue
            m = labels == comp
            part[m] = low_lid if sat[m].mean() < thresh else other_lid
    elif ncomp > 1:
        raise SystemExit(
            f"[{cfg.name}] source has {ncomp - 1} satellite component(s) but "
            "the config declares no `satellites` rule")

    # leftover px (the fence lines): priority dilation, foreground object wins
    left = fg & (part == 0)
    while left.any():
        assigned = {}
        for y, x in zip(*np.nonzero(left)):
            cand = [part[y + dy, x + dx]
                    for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if 0 <= y + dy < H and 0 <= x + dx < W
                    and part[y + dy, x + dx]]
            if cand:
                assigned[(y, x)] = max(cand, key=lambda v: cfg.priority[v])
        if not assigned:
            raise SystemExit(f"unassignable px remain: {int(left.sum())}")
        for (y, x), v in assigned.items():
            part[y, x] = v
            left[y, x] = False

    assert ((part > 0) == fg).all(), "partition must cover fg exactly"
    return part


def cut(cfg, out_dir):
    rgba = np.asarray(Image.open(cfg.source).convert("RGBA")).astype(np.float64)
    H, W = rgba.shape[:2]
    part = partition(cfg, rgba)

    layers = {}
    for lid in sorted(cfg.names):
        m = part == lid
        img = np.zeros_like(rgba)
        img[m] = rgba[m]
        layers[cfg.names[lid]] = (img, m)

    for lid, radius, covered_by in cfg.fill_behind:
        name = cfg.names[lid]
        img, m = layers[name]
        cover = np.zeros_like(m)
        for other in covered_by:
            cover |= (part == other)
        behind = dilate(m, radius) & cover
        layers[name] = (onion_fill(img, m, behind), m | behind)

    os.makedirs(out_dir / "combat", exist_ok=True)
    pfx = cfg.file_prefix
    PAD = cfg.master_pad
    meta = {}
    for name, (img, m) in layers.items():
        ys, xs = np.nonzero(m)
        x0, x1 = max(0, xs.min() - PAD), min(W, xs.max() + 1 + PAD)
        y0, y1 = max(0, ys.min() - PAD), min(H, ys.max() + 1 + PAD)
        Image.fromarray(np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8),
                        "RGBA").save(out_dir / f"{pfx}_layer_{name}.png")
        meta[name] = {"file": f"{pfx}_layer_{name}.png",
                      "w": int(x1 - x0), "h": int(y1 - y0),
                      "offset_x": round((x0 + x1) / 2 - W / 2, 1),
                      "offset_y": round((y0 + y1) / 2 - H / 2, 1)}
        print(f"{name:9s} {x1 - x0}x{y1 - y0} "
              f"offset=({meta[name]['offset_x']:+.1f},{meta[name]['offset_y']:+.1f})")
    (out_dir / "layers.json").write_text(
        json.dumps({"canvas": [W, H], "layers": meta}, indent=2),
        encoding="utf-8")

    # combat-scale derivatives: the same box the static model used
    CW, CH = cfg.combat_box
    P = cfg.combat_pad
    cmeta = {}
    for name, (img, m) in layers.items():
        full = np.zeros((H, W, 4), np.float64)
        full[m] = img[m]
        small = Image.fromarray(np.clip(full, 0, 255).astype(np.uint8),
                                "RGBA").resize((CW, CH), Image.LANCZOS)
        sa = np.asarray(small)
        ys, xs = np.nonzero(sa[..., 3] > 2)
        x0, x1 = max(0, xs.min() - P), min(CW, xs.max() + 1 + P)
        y0, y1 = max(0, ys.min() - P), min(CH, ys.max() + 1 + P)
        small.crop((x0, y0, x1, y1)).save(
            out_dir / "combat" / f"{pfx}_combat_{name}.png")
        cmeta[name] = {"file": f"{pfx}_combat_{name}.png",
                       "w": int(x1 - x0), "h": int(y1 - y0),
                       "offset_x": round((x0 + x1) / 2 - CW / 2, 1),
                       "offset_y": round((y0 + y1) / 2 - CH / 2, 1)}
        print(f"combat {name:9s} {x1 - x0}x{y1 - y0} "
              f"offset=({cmeta[name]['offset_x']:+.1f},{cmeta[name]['offset_y']:+.1f})")
    (out_dir / "combat" / "layers_combat.json").write_text(
        json.dumps({"canvas": [CW, CH], "layers": cmeta}, indent=2),
        encoding="utf-8")
    print("The combat.tscn sprite offsets must match layers_combat.json.")


def check(cfg):
    """Re-cut into a temp dir and diff against what is on disk."""
    import filecmp
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cut(cfg, tmp)
        bad, seen = [], 0
        for produced in sorted(tmp.rglob("*")):
            if produced.is_dir():
                continue
            rel = produced.relative_to(tmp)
            shipped = cfg.out_dir / rel
            seen += 1
            if not shipped.exists():
                bad.append(f"MISSING on disk: {rel}")
            elif not filecmp.cmp(produced, shipped, shallow=False):
                bad.append(f"DIFFERS: {rel}")
        print()
        for line in bad:
            print("  " + line)
        print(f"{seen - len(bad)}/{seen} outputs byte-identical")
        return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("character", help="fence config stem in tools/combat_layer_fences/")
    ap.add_argument("--check", action="store_true",
                    help="re-cut to a temp dir and diff against shipped art")
    args = ap.parse_args()

    cfg = load_config(args.character)
    if not cfg.source.exists():
        raise SystemExit(f"[{cfg.name}] source missing: {cfg.source}")
    print(f"[{cfg.name}] {cfg.source.relative_to(ROOT)} -> "
          f"{cfg.out_dir.relative_to(ROOT)}")

    if args.check:
        return check(cfg)
    cut(cfg, cfg.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
