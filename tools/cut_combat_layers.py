"""Cut a character render into animated combat-model layers.

Animation sprint 2, Track B1 (2026-07-24). Generalization of
tools/cut_klee_combat_layers.py, which was written for exactly one artwork.
Klee's fences become config #1 (tools/combat_layer_fences/klee.yaml); Furina
is config #2; Kokomi's kickoff is already in the tree, which was the
third-instance-incoming signal that made generalizing worth it now.

    .venv/Scripts/python tools/cut_combat_layers.py klee
    .venv/Scripts/python tools/cut_combat_layers.py furina
    .venv/Scripts/python tools/cut_combat_layers.py teyvat/azhdaha
    .venv/Scripts/python tools/cut_combat_layers.py --all --check
    .venv/Scripts/python tools/cut_combat_layers.py --all --verify

`--check` re-cuts into a temp dir and diffs against what is on disk. Klee's
output is byte-identical to the pre-generalization tool's, and that is the
regression this flag exists to protect: the generalization must not have
quietly changed the shipped art. `--verify` asks the other question: stack the
SHIPPED layers back up at their manifest offsets and diff against the source,
which is what catches an offset that drifted from the PNG beside it.

MOTION PASS TWO (2026-09-17) added configs #3-#8, the six bespoke boss rigs
under `combat_layer_fences/teyvat/`, and with them four optional config keys:
`layer_path` (where a layer lands inside `out_dir`), `manifest_path` (send the
manifest somewhere COMMITTED, because `ImageGen/` is gitignored and a worktree
has none of it), `combat_box: null` (skip the combat derivatives -- a 240x280
enemy plate IS the combat plate), and `min_cover_alpha` on a `fill_behind`
entry (stop the inpaint at pixels the mover does not fully hide, which is what
makes a recomposition provably exact). `--art-root` points the source and the
output at another checkout, so a worktree can cut against the main tree's art.
Every default is what configs #1 and #2 already shipped.

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

    def __init__(self, name, raw, art_root=None, repo_root=None):
        art_root = Path(art_root or ROOT)
        repo_root = Path(repo_root or ROOT)
        self.name = name
        self.source = art_root / raw["source"]
        self.out_dir = art_root / raw["out_dir"]
        self.file_prefix = raw["file_prefix"]
        self.alpha_threshold = int(raw.get("alpha_threshold", 16))
        # A config with NO `combat_box` skips the combat derivatives entirely.
        # Klee's and Furina's sources are 1000-px masters that have to be
        # resampled down to the combat box; a Teyvat boss plate IS already the
        # 240x280 combat plate, so a derivative would be the same pixels under
        # a second name and a second manifest nothing reads.
        box = raw.get("combat_box")
        self.combat_box = tuple(box) if box else None
        self.master_pad = int(raw.get("master_pad", 4))
        self.combat_pad = int(raw.get("combat_pad", 2))
        # Where a layer PNG lands inside `out_dir`, and what the manifest is
        # called. The defaults are exactly what configs #1 and #2 shipped.
        self.layer_path = raw.get("layer_path", "{prefix}_layer_{name}.png")
        # The manifest is the one output a WORKTREE needs: `ImageGen/` is
        # gitignored and a worktree never has it, but
        # `gen_teyvat_creature_scenes.py` has to know every layer's offset to
        # write a scene. So a config may send it somewhere COMMITTED, outside
        # the art tree, and `--check` diffs it there.
        manifest = raw.get("manifest_path")
        self.manifest_path = (repo_root / manifest) if manifest else None
        # Does `--verify` GATE on the recomposition, or only report it?
        # Configs #1 and #2 inpaint under semi-transparent cover
        # (`min_cover_alpha` 0) and resample a second time for the combat box,
        # so neither stacks back up to its master and neither ever claimed to.
        # A config that sets this is promising that it does.
        self.recompose_exact = bool(raw.get("recompose_exact", False))

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

        # `min_cover_alpha` defaults to 0, which is exactly what configs #1 and
        # #2 shipped: fill under every covered pixel. Raise it and the inpaint
        # stops at pixels the mover does not FULLY hide -- which is the only
        # place the fill can change what the plate looks like AT REST, because
        # a semi-transparent cover pixel lets the new paint through. A config
        # that wants a provably pixel-exact recomposition sets it to 255.
        self.fill_behind = [
            (self._id(f["layer"], "fill_behind"), int(f["radius"]),
             [self._id(n, "fill_behind") for n in f["covered_by"]],
             int(f.get("min_cover_alpha", 0)))
            for f in raw.get("fill_behind", [])
        ]

    def _id(self, layer_name, where):
        if layer_name not in self.by_name:
            raise SystemExit(
                f"[{self.name}] {where} names unknown layer {layer_name!r}; "
                f"known: {sorted(self.by_name)}")
        return self.by_name[layer_name]


def config_path(name):
    return CONFIG_DIR / f"{name}.yaml"


def load_config(name, art_root=None, repo_root=None):
    path = config_path(name)
    if not path.exists():
        have = sorted(str(p.relative_to(CONFIG_DIR).with_suffix(""))
                      .replace("\\", "/") for p in CONFIG_DIR.rglob("*.yaml"))
        raise SystemExit(f"no fence config {path}; have: {have}")
    return Config(name, yaml.safe_load(path.read_text(encoding="utf-8")),
                  art_root=art_root, repo_root=repo_root)


#: Every config the gate re-cuts, in the order `--check-all` walks them. A cut
#: is only a gate if something runs it: a fence that nobody re-cuts is a
#: comment, and the whole point of `--check` is that the shipped pixels are
#: provably what the committed fences say.
ALL_CONFIGS = (
    "klee",
    "furina",
    "teyvat/azhdaha",
    "teyvat/all_devouring_narwhal",
    "teyvat/rhodeia_of_loch",
    "teyvat/emperor_of_fire_and_iron",
    "teyvat/golden_wolflord",
    "teyvat/everlasting_lord_of_arcane_wisdom",
)


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


def cut(cfg, out_dir, manifest_path=None):
    rgba = np.asarray(Image.open(cfg.source).convert("RGBA")).astype(np.float64)
    H, W = rgba.shape[:2]
    part = partition(cfg, rgba)

    layers = {}
    for lid in sorted(cfg.names):
        m = part == lid
        img = np.zeros_like(rgba)
        img[m] = rgba[m]
        layers[cfg.names[lid]] = (img, m)

    for lid, radius, covered_by, min_cover_alpha in cfg.fill_behind:
        name = cfg.names[lid]
        img, m = layers[name]
        cover = np.zeros_like(m)
        for other in covered_by:
            cover |= (part == other)
        if min_cover_alpha:
            cover &= rgba[..., 3] >= min_cover_alpha
        behind = dilate(m, radius) & cover
        layers[name] = (onion_fill(img, m, behind), m | behind)

    os.makedirs(out_dir, exist_ok=True)
    pfx = cfg.file_prefix
    PAD = cfg.master_pad
    meta = {}
    for name, (img, m) in layers.items():
        ys, xs = np.nonzero(m)
        x0, x1 = max(0, xs.min() - PAD), min(W, xs.max() + 1 + PAD)
        y0, y1 = max(0, ys.min() - PAD), min(H, ys.max() + 1 + PAD)
        relative = cfg.layer_path.format(prefix=pfx, name=name)
        destination = out_dir / relative
        os.makedirs(destination.parent, exist_ok=True)
        Image.fromarray(np.clip(img[y0:y1, x0:x1], 0, 255).astype(np.uint8),
                        "RGBA").save(destination)
        meta[name] = {"file": relative,
                      "w": int(x1 - x0), "h": int(y1 - y0),
                      "offset_x": round((x0 + x1) / 2 - W / 2, 1),
                      "offset_y": round((y0 + y1) / 2 - H / 2, 1)}
        print(f"{name:9s} {x1 - x0}x{y1 - y0} "
              f"offset=({meta[name]['offset_x']:+.1f},{meta[name]['offset_y']:+.1f})")
    manifest = json.dumps({"canvas": [W, H], "layers": meta}, indent=2) + "\n"
    if manifest_path is None:
        (out_dir / "layers.json").write_text(manifest[:-1], encoding="utf-8")
    else:
        os.makedirs(Path(manifest_path).parent, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(manifest)

    if cfg.combat_box is None:
        return

    # combat-scale derivatives: the same box the static model used
    os.makedirs(out_dir / "combat", exist_ok=True)
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
        art = tmp / "art"
        manifest = (tmp / "manifest.json") if cfg.manifest_path else None
        cut(cfg, art, manifest)
        bad, seen = [], 0
        pairs = [(p, cfg.out_dir / p.relative_to(art))
                 for p in sorted(art.rglob("*")) if not p.is_dir()]
        if manifest:
            pairs.append((manifest, cfg.manifest_path))
        for produced, shipped in pairs:
            rel = shipped.name if produced is manifest else \
                produced.relative_to(art)
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


def verify(cfg):
    """Stack the shipped layers back up and diff against the source.

    The hard partition makes this exact BY CONSTRUCTION (`partition` asserts it
    covers the foreground and no pixel twice), but "by construction" is an
    argument and this is a measurement -- and it is the measurement that would
    catch a manifest offset that drifted from the PNG beside it, which no
    assertion inside the cut can see.

    Composited in PREMULTIPLIED alpha, which is what the screen does; straight
    "over" arithmetic gets a transparent destination wrong and would report a
    fault that is not there.
    """
    manifest_path = cfg.manifest_path or (cfg.out_dir / "layers.json")
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    W, H = manifest["canvas"]
    pre = np.zeros((H, W, 3))
    acc = np.zeros((H, W))
    for name, entry in manifest["layers"].items():
        img = np.asarray(Image.open(cfg.out_dir / entry["file"]).convert("RGBA")
                         ).astype(np.float64)
        h, w = img.shape[:2]
        if (w, h) != (entry["w"], entry["h"]):
            raise SystemExit(f"[{cfg.name}] {name}: manifest says {entry['w']}x"
                             f"{entry['h']}, the file is {w}x{h}")
        x0 = int(round(entry["offset_x"] + W / 2 - w / 2))
        y0 = int(round(entry["offset_y"] + H / 2 - h / 2))
        sa = np.zeros((H, W))
        sp = np.zeros((H, W, 3))
        sa[y0:y0 + h, x0:x0 + w] = img[..., 3] / 255.0
        sp[y0:y0 + h, x0:x0 + w] = img[..., :3] * (img[..., 3:4] / 255.0)
        pre = sp + pre * (1 - sa)[..., None]
        acc = sa + acc * (1 - sa)

    source = np.asarray(Image.open(cfg.source).convert("RGBA")).astype(np.float64)
    # The pixels the cut KEEPS. Anything at or below `alpha_threshold` is
    # background by the config's own definition and is dropped on purpose.
    keep = source[..., 3] > cfg.alpha_threshold
    drgb = (np.abs(source[..., :3] * (source[..., 3:4] / 255.0) - pre)
            .max(axis=2) * keep)
    dalpha = np.abs(source[..., 3] / 255.0 - acc) * 255 * keep
    print(f"recomposed {int(keep.sum())} kept px: rgb max {drgb.max():.4f}, "
          f"alpha max {dalpha.max():.4f}, "
          f"{int((~keep & (source[..., 3] > 0)).sum())} sub-threshold px dropped")
    if drgb.max() > 0 or dalpha.max() > 0:
        print("  NOT pixel-exact"
              + ("" if cfg.recompose_exact else " (not claimed by this config)"))
        return 1 if cfg.recompose_exact else 0
    return 0


def run(name, do_check, art_root, repo_root, do_verify=False):
    cfg = load_config(name, art_root=art_root, repo_root=repo_root)
    if not cfg.source.exists():
        raise SystemExit(f"[{cfg.name}] source missing: {cfg.source}")
    print(f"[{cfg.name}] {cfg.source} -> {cfg.out_dir}")
    if do_verify:
        return verify(cfg)
    if do_check:
        return check(cfg)
    cut(cfg, cfg.out_dir, cfg.manifest_path)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("character", nargs="?",
                    help="fence config stem in tools/combat_layer_fences/ "
                         "(a subdirectory is part of the stem: teyvat/azhdaha)")
    ap.add_argument("--check", action="store_true",
                    help="re-cut to a temp dir and diff against shipped art")
    ap.add_argument("--verify", action="store_true",
                    help="stack the shipped layers back up at their manifest "
                         "offsets and diff against the source")
    ap.add_argument("--all", action="store_true",
                    help=f"every config: {', '.join(ALL_CONFIGS)}")
    # THE ART TREE IS NOT IN A WORKTREE. `ImageGen/` is gitignored and lives
    # only in the main checkout, so a worktree cutting a layer has to be told
    # where the pixels are. The repo half -- the fences and the committed
    # manifests -- always resolves against THIS checkout.
    ap.add_argument("--art-root", default=str(ROOT),
                    help="checkout holding ImageGen/ (default: this one)")
    args = ap.parse_args()

    if args.all == bool(args.character):
        raise SystemExit("name one config, or pass --all; not both, not neither")

    names = ALL_CONFIGS if args.all else (args.character,)
    worst = 0
    for name in names:
        worst = max(worst, run(name, args.check, args.art_root, ROOT,
                               do_verify=args.verify))
    return worst


if __name__ == "__main__":
    sys.exit(main())
