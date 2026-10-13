"""Klee's combat scene: spec + occupancy grid + frame manifest -> combat.tscn.

Pure text generation, no pixels and no engine: `klee.yaml` (bones, skin rules,
motion), `klee_cells.json` (the committed occupancy grid `cells.py` made
from the art) and `klee_frames.json` (the committed manifest of the frame
sheets tools/klee_render renders from the official model) go in, the scene
text comes out.

Two figures live in the scene. `Visuals/Facing/Model` is Klee herself since
milestone 2 (2026-10-12): one Sprite2D per frame sheet, cross-faded by
self_modulate and stepped by a discrete `frame` track. `Visuals/Facing/Rig`
is the older skinned-mesh rig of the floating splash, kept as alt-art for her
Set Off plays: invisible (modulate alpha 0) in every state but `setoff`. Every number is rounded and
every collection is walked in a fixed order, so two runs are byte-identical.

Engine facts this file is written around (MegaDot 4.5.1, measured in the
animation bake-off, commit 09864c273, and the Skeleton2D spike,
tools/skeleton2d_spike/README.md):

* a Polygon2D's skin is the FLAT `bones = ["Path", PackedFloat32Array(...),
  ...]` array; a `bones/0/path` line is discarded by the parser without an
  error and the mesh never deforms;
* a skinned Polygon2D ignores its own transform, so every mesh sits at the
  Skeleton2D's origin (both are children of Rig, both untransformed) and all
  layer motion -- including the layer offsets the old scene keyed on the
  sprites -- is carried by bones;
* scalar animation keys must be spelled as floats (`0.0`, not `0`).

At rest every bone's pose equals its rest, every skin matrix is the
identity, weights sum to exactly 1, and polygon == uv + texture top-left, so
the meshes draw the textures exactly where the old centred Sprite2Ds did.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = HERE / "klee.yaml"
CELLS = HERE / "klee_cells.json"
FRAMES = HERE / "klee_frames.json"
SCENE = ROOT / "klee-mod" / "pck-src" / "klee" / "model" / "combat.tscn"
TEX_DIR = "res://klee/model/layers"
RIG = "Visuals/Facing/Rig"
MODEL = "Visuals/Facing/Model"
FRAME_DIR = "res://klee/model/frames"
NL = "\n"

#: The router contract (CreatureAnimationRouter.cs) plus `setoff`.
ANIMATION_ORDER = ("idle", "attack", "hurt", "death", "cast", "power", "idle_low", "setoff")
#: The one-shots on the base game's clock (the paper's census: attack
#: 0.93-1.5 s, cast 0.97-1.8, hurt 0.73-1.0, die 1.87-4.17). The death seam
#: measures the clip, so ModdedPlayerDeathSeam follows this number on its own.
ONE_SHOT_LENGTHS = {"attack": 1.0, "hurt": 0.8, "death": 2.0, "cast": 1.0, "power": 1.0, "setoff": 1.2}
#: Sheet name (manifest key) -> its Sprite2D under Model.
SHEET_NODE = {"idle": "Idle", "idle_low": "IdleLow", "attack": "Attack", "hurt": "Hurt",
              "death": "Death", "cast": "Cast"}
PROP_KIND = {":position": "vec2", ":rotation": "float", ":modulate": "color",
             ":self_modulate": "color", ":frame": "int"}
PROP_ORDER = [":position", ":rotation", ":modulate", ":self_modulate", ":frame"]


def node_rest(path: str):
    """RESET value of a node track. The splash rig rests INVISIBLE; the model
    rests on its idle sheet's first frame."""
    node, prop = path.split(":")
    prop = ":" + prop
    if prop == ":position":
        return (0.0, -140.0)
    if prop == ":rotation":
        return 0.0
    if prop == ":frame":
        return 0
    if node == RIG and prop == ":modulate":
        return (1.0, 1.0, 1.0, 0.0)
    if prop == ":self_modulate":
        return (1.0, 1.0, 1.0, 1.0 if node == f"{MODEL}/Idle" else 0.0)
    return (1.0, 1.0, 1.0, 1.0)


# ---------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------


def num(v: float) -> str:
    v = round(float(v), 4)
    if v == 0:
        return "0"
    if v == int(v):
        return str(int(v))
    return repr(v)


def fnum(v: float) -> str:
    text = repr(round(float(v), 6))
    if text == "-0.0":
        text = "0.0"
    return text if ("." in text or "e" in text) else text + ".0"


def vec2(v) -> str:
    return f"Vector2({num(v[0])}, {num(v[1])})"


def color(v) -> str:
    return "Color(" + ", ".join(num(c) for c in v) + ")"


# ---------------------------------------------------------------------------
# spec
# ---------------------------------------------------------------------------


def load_spec(path: Path = SPEC) -> dict:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=loader)


def load_cells(path: Path = CELLS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_frames(path: Path = FRAMES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class Bone:
    name: str
    parent: str | None
    at: tuple[float, float]          # rig space
    tip: tuple[float, float] | None  # rig space; None == point / no segment
    children: list[str] = field(default_factory=list)


class Rig:
    def __init__(self, spec: dict, cells: dict):
        self.spec = spec
        self.cells = cells
        sw, sh = spec["source_canvas"]
        bw, bh = spec["combat_box"]
        self.sx, self.sy = bw / sw, bh / sh
        self.bw, self.bh = bw, bh
        self.bones: dict[str, Bone] = {}
        for b in spec["bones"]:
            tip = b.get("tip")
            self._add(Bone(b["name"], b["parent"], self.to_rig(b["at"]),
                           self.to_rig(tip) if tip else None))
            if b["name"] == "FloatersRoot":
                for k, c in enumerate(cells["layers"]["Floaters"]["islands"]):
                    self._add(Bone(f"Floater{k}", "FloatersRoot",
                                   (round(c[0], 3), round(c[1], 3)), None))
        self.order = list(self.bones)

    def _add(self, bone: Bone) -> None:
        assert bone.name not in self.bones, bone.name
        if bone.parent is not None:
            self.bones[bone.parent].children.append(bone.name)
        self.bones[bone.name] = bone

    def to_rig(self, p) -> tuple[float, float]:
        return (round(p[0] * self.sx - self.bw / 2, 3), round(p[1] * self.sy - self.bh / 2, 3))

    def to_source(self, p) -> tuple[float, float]:
        return ((p[0] + self.bw / 2) / self.sx, (p[1] + self.bh / 2) / self.sy)

    def local(self, name: str) -> tuple[float, float]:
        b = self.bones[name]
        if b.parent is None:
            return b.at
        p = self.bones[b.parent].at
        return (round(b.at[0] - p[0], 3), round(b.at[1] - p[1], 3))

    def path(self, name: str) -> str:
        chain = []
        cur: str | None = name
        while cur is not None:
            chain.append(cur)
            cur = self.bones[cur].parent
        return "/".join(reversed(chain))

    @property
    def floater_count(self) -> int:
        return len(self.cells["layers"]["Floaters"]["islands"])


# ---------------------------------------------------------------------------
# meshes
# ---------------------------------------------------------------------------


@dataclass
class Mesh:
    layer: str
    texture: str
    polygon: list[tuple[float, float]]
    uv: list[tuple[float, float]]
    quads: list[tuple[int, int, int, int]]
    weights: dict[str, list[float]]  # bone -> per-vertex weight (only bones used)


def _point_in_poly(x: float, y: float, poly) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


def _seg_dist(p, a, b) -> float:
    if b is None:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
    return math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy)


def _quantise(ws: dict[str, float]) -> dict[str, float]:
    """Round to 3 decimals and make the decimal sum exactly 1 (the largest
    weight absorbs the residue), so the rest pose is the identity."""
    q = {k: round(v, 3) for k, v in ws.items() if round(v, 3) > 0}
    if not q:
        k = max(ws, key=lambda k: ws[k])
        return {k: 1.0}
    top = max(q, key=lambda k: (q[k], k))
    q[top] = round(1.0 - sum(v for k, v in q.items() if k != top), 3)
    return q


def _weights_distance(rig: Rig, rule: dict, p) -> dict[str, float]:
    allowed = rule["bones"]
    sp = rig.to_source(p)
    for region in rule.get("regions", ()):
        if _point_in_poly(sp[0], sp[1], region["polygon"]):
            allowed = region["bones"]
            break
    power, fall = float(rule["power"]), float(rule["falloff"])
    raw = {}
    for name in allowed:
        b = rig.bones[name]
        raw[name] = 1.0 / (_seg_dist(p, b.at, b.tip) + fall) ** power
    best = sorted(raw, key=lambda k: (-raw[k], k))[:4]
    tot = sum(raw[k] for k in best)
    return _quantise({k: raw[k] / tot for k in best})


def _smooth(per_vertex: list[dict[str, float]], quads, iterations: int) -> list[dict[str, float]]:
    """Diffuse weights along mesh edges so a region boundary becomes a band a
    few cells wide instead of a hard step. A hard step shears the one row of
    cells it crosses, and on a cell grid that shear draws as a staircase."""
    nbrs: list[set[int]] = [set() for _ in per_vertex]
    for q in quads:
        for i in range(4):
            a, b = q[i], q[(i + 1) % 4]
            nbrs[a].add(b)
            nbrs[b].add(a)
    cur = [dict(pv) for pv in per_vertex]
    for _ in range(iterations):
        nxt = []
        for v, pv in enumerate(cur):
            acc = dict(pv)
            for n in sorted(nbrs[v]):
                for k, w in cur[n].items():
                    acc[k] = acc.get(k, 0.0) + w
            tot = 1 + len(nbrs[v])
            nxt.append({k: w / tot for k, w in acc.items()})
        cur = nxt
    out = []
    for pv in cur:
        best = sorted(pv, key=lambda k: (-pv[k], k))[:4]
        tot = sum(pv[k] for k in best)
        out.append(_quantise({k: pv[k] / tot for k in best}))
    return out


def build_mesh(rig: Rig, layer: dict) -> Mesh:
    name = layer["name"]
    rec = rig.cells["layers"][name]
    w, h = rec["texture"]
    tlx, tly = rec["topleft"]
    c = rec["cell"]
    rule = rig.spec["skin"][name]
    rows = rec["rows"]
    keyed: dict[tuple[int, int, int], int] = {}
    cells = []
    for gy, row in enumerate(rows):
        for gx, ch in enumerate(row):
            if ch == ".":
                continue
            isl = 0 if ch == "#" else ord(ch) - 97
            cells.append((isl, gx, gy))
    corner_keys = set()
    for isl, gx, gy in cells:
        for dx, dy in ((0, 0), (1, 0), (1, 1), (0, 1)):
            corner_keys.add((isl, gx + dx, gy + dy))
    for k in sorted(corner_keys, key=lambda k: (k[0], k[2], k[1])):
        keyed[k] = len(keyed)
    uv = []
    for isl, gx, gy in sorted(keyed, key=lambda k: keyed[k]):
        uv.append((float(min(gx * c, w)), float(min(gy * c, h))))
    polygon = [(tlx + u, tly + v) for u, v in uv]
    quads = []
    for isl, gx, gy in sorted(cells, key=lambda k: (k[0], k[2], k[1])):
        quads.append((keyed[(isl, gx, gy)], keyed[(isl, gx + 1, gy)],
                      keyed[(isl, gx + 1, gy + 1)], keyed[(isl, gx, gy + 1)]))
    # weights
    mode = rule["mode"]
    per_vertex: list[dict[str, float]] = []
    keys_in_order = sorted(keyed, key=lambda k: keyed[k])
    for idx, p in enumerate(polygon):
        if mode == "single":
            per_vertex.append({rule["bone"]: 1.0})
        elif mode == "islands":
            per_vertex.append({f"Floater{keys_in_order[idx][0]}": 1.0})
        elif mode == "vertical":
            top, bot = rig.bones[rule["top"]], rig.bones[rule["bottom"]]
            t = (p[1] - top.at[1]) / (bot.at[1] - top.at[1])
            t = max(0.0, min(1.0, t))
            per_vertex.append(_quantise({rule["top"]: 1.0 - t, rule["bottom"]: t}))
        elif mode == "distance":
            per_vertex.append(_weights_distance(rig, rule, p))
        else:
            raise ValueError(f"{name}: unknown skin mode {mode!r}")
    if int(rule.get("smooth", 0)):
        per_vertex = _smooth(per_vertex, quads, int(rule["smooth"]))
    used = [b for b in rig.order if any(b in pv for pv in per_vertex)]
    weights = {b: [pv.get(b, 0.0) for pv in per_vertex] for b in used}
    return Mesh(name, layer["texture"], polygon, uv, quads, weights)


def build_meshes(rig: Rig) -> list[Mesh]:
    return [build_mesh(rig, layer) for layer in rig.spec["layers"]]


# ---------------------------------------------------------------------------
# animations
# ---------------------------------------------------------------------------


@dataclass
class Track:
    path: str
    kind: str                 # "vec2" | "float" | "color" | "int"
    times: list[float]
    values: list
    transitions: list[float]
    interp: int = 1
    update: int = 0           # 1 = discrete (the sheet's frame index)


PROP = {"rot": "rotation", "pos": "position", "scale": "scale"}

#: Per-island float: amplitudes (rig px) and phases (fraction of the loop)
#: vary by island index so the bells never bob in lockstep.
FLOATER_WAVES = {
    "bob":   {"amp_y": (2.4, 1.6, 3.0, 2.0), "amp_x": (0.6, -0.8, 0.4, -0.5), "scale": 1.0},
    "drift": {"amp_y": (1.0, 0.7, 1.2, 0.8), "amp_x": (0.3, -0.3, 0.2, -0.2), "scale": 1.0},
}


def _wave_samples(length: float, wave: dict):
    cycles = int(wave.get("cycles", 1))
    period = length / cycles
    n = 8 * cycles
    times = [round(length * j / n, 4) for j in range(n + 1)]
    phase = float(wave.get("phase", 0.0))
    s = [math.sin(2 * math.pi * (t - phase) / period) for t in times]
    s[-1] = s[0]  # exact loop closure
    return times, s


def _bone_value(rig: Rig, bone: str, prop: str, v):
    if prop == "rot":
        return math.radians(float(v))
    if prop == "pos":
        lx, ly = rig.local(bone)
        return (lx + float(v[0]), ly + float(v[1]))
    return (float(v[0]), float(v[1]))


def _expand(rig: Rig, anim: dict, tr: dict) -> list[Track]:
    length = float(anim["length"])
    if "floaters" in tr:
        cfg = FLOATER_WAVES[tr["floaters"]]
        out = []
        for k in range(rig.floater_count):
            ay = cfg["amp_y"][k % 4]
            ax = cfg["amp_x"][k % 4]
            phase = round(((k * 0.37) % 1.0) * length, 4)
            sub = {"bone": f"Floater{k}", "prop": "pos",
                   "wave": {"amp": [ax, ay], "phase": phase}}
            out += _expand(rig, anim, sub)
        return out
    prop = tr["prop"]
    if "node" in tr or "model" in tr:
        node = tr["node"] if "node" in tr else tr["model"]
        base = RIG if "node" in tr else MODEL
        path = base + (f"/{node}" if node else "") + f":{prop}"
        kind = {"position": "vec2", "rotation": "float", "modulate": "color"}[prop]
        conv = (lambda v: (float(v[0]), float(v[1]))) if kind == "vec2" else \
               (lambda v: tuple(float(c) for c in v)) if kind == "color" else float
        return [_make(tr, length, path, kind, conv)]
    bones = tr["bone"] if isinstance(tr["bone"], list) else [tr["bone"]]
    out = []
    for bone in bones:
        assert bone in rig.bones, bone
        path = f"{RIG}/Skeleton/{rig.path(bone)}:{PROP[prop]}"
        kind = "float" if prop == "rot" else "vec2"
        out.append(_make(tr, length, path, kind, lambda v, b=bone: _bone_value(rig, b, prop, v)))
    return out


def _make(tr: dict, length: float, path: str, kind: str, conv) -> Track:
    if "wave" in tr:
        wave = tr["wave"]
        times, s = _wave_samples(length, wave)
        amp = wave["amp"]
        if kind == "float":
            base = float(wave.get("base", 0.0))
            raw = [base + float(amp) * x for x in s]
        else:
            base = wave.get("base", [0.0, 0.0])
            raw = [(base[0] + amp[0] * x, base[1] + amp[1] * x) for x in s]
        values = [conv(v) for v in raw]
        return Track(path, kind, times, values, [1.0] * len(times), interp=2)
    times, values, trans = [], [], []
    for key in tr["keys"]:
        times.append(float(key[0]))
        values.append(conv(key[1]))
        trans.append(float(key[2]) if len(key) > 2 else 1.0)
    assert times == sorted(times) and times[-1] <= length + 1e-9, path
    return Track(path, kind, times, values, trans, interp=1)


def sheet_tracks(rig: Rig, frames: dict, anim: dict) -> list[Track]:
    """Show this state's sheet (self_modulate alpha 1, every other sheet 0)
    and step its frame at the times the renderer drew them."""
    sheet = anim["sheet"]
    rec = frames["sheets"][sheet]
    length = float(anim["length"])
    out = []
    for name in rig.spec["model"]["sheets"]:
        a = 1.0 if name == sheet else 0.0
        out.append(Track(f"{MODEL}/{SHEET_NODE[name]}:self_modulate", "color", [0.0], [(1.0, 1.0, 1.0, a)], [1.0]))
    if "hold_frame" in anim:
        times, values = [0.0], [int(anim["hold_frame"])]
    else:
        times = [float(t) for t in rec["times"]]
        values = list(range(len(times)))
        assert times[-1] < length + 1e-9, f"{sheet}: frames run past the state's length"
        if anim.get("loop"):
            assert abs(len(times) / rec["fps"] - length) < 1e-6, f"{sheet}: loop length != frames / fps"
    out.append(Track(f"{MODEL}/{SHEET_NODE[sheet]}:frame", "int", times, values, [1.0] * len(times),
                     interp=0, update=1))
    return out


def build_animations(rig: Rig, frames: dict | None = None) -> dict[str, tuple[dict, list[Track]]]:
    frames = frames or load_frames()
    out = {}
    for name in ANIMATION_ORDER:
        anim = rig.spec["animations"][name]
        tracks: list[Track] = []
        for tr in anim.get("tracks", ()):
            tracks += _expand(rig, anim, tr)
        tracks += sheet_tracks(rig, frames, anim)
        paths = [t.path for t in tracks]
        assert len(paths) == len(set(paths)), f"{name}: duplicate track"
        out[name] = (anim, tracks)
    return out


def reset_tracks(rig: Rig, anims) -> list[Track]:
    """RESET is derived: every property any animation drives, at rest."""
    seen: list[str] = []
    for _anim, tracks in anims.values():
        for t in tracks:
            if t.path not in seen:
                seen.append(t.path)
    node_paths = [p for p in seen if "/Skeleton/" not in p]
    bone_paths = [p for p in seen if "/Skeleton/" in p]
    order = {f"{RIG}/Skeleton/{rig.path(b)}": i for i, b in enumerate(rig.order)}
    bone_paths.sort(key=lambda p: (order[p.split(":")[0]], p))
    node_paths.sort(key=lambda p: (p.count("/"), PROP_ORDER.index(p[p.index(":"):]), p))
    out = []
    for p in node_paths:
        prop = p[p.index(":"):]
        v = node_rest(p)
        if p.startswith(f"{RIG}/") and prop == ":position":
            raise AssertionError(f"layer node position is not animatable on a skinned mesh: {p}")
        kind = PROP_KIND[prop]
        if kind == "int":
            out.append(Track(p, kind, [0.0], [v], [1.0], interp=0, update=1))
        else:
            out.append(Track(p, kind, [0.0], [v], [1.0]))
    for p in bone_paths:
        node, prop = p.split(":")
        bone = node.rsplit("/", 1)[1]
        if prop == "rotation":
            out.append(Track(p, "float", [0.0], [0.0], [1.0]))
        elif prop == "position":
            out.append(Track(p, "vec2", [0.0], [rig.local(bone)], [1.0]))
        else:
            out.append(Track(p, "vec2", [0.0], [(1.0, 1.0)], [1.0]))
    return out


# ---------------------------------------------------------------------------
# scene text
# ---------------------------------------------------------------------------


def _lit(kind: str, v) -> str:
    if kind == "vec2":
        return vec2(v)
    if kind == "color":
        return color(v)
    if kind == "int":
        return str(int(v))
    return fnum(v)


def animation_block(anim_id: str, name: str | None, length: float, loop: bool,
                    tracks: list[Track]) -> str:
    lines = [f'[sub_resource type="Animation" id="{anim_id}"]']
    if name:
        lines.append(f'resource_name = "{name}"')
    lines.append(f"length = {fnum(length)}")
    if loop:
        lines.append("loop_mode = 1")
    for i, t in enumerate(tracks):
        lines += [
            f'tracks/{i}/type = "value"',
            f"tracks/{i}/imported = false",
            f"tracks/{i}/enabled = true",
            f'tracks/{i}/path = NodePath("{t.path}")',
            f"tracks/{i}/interp = {t.interp}",
            f"tracks/{i}/loop_wrap = true",
            f"tracks/{i}/keys = {{",
            '"times": PackedFloat32Array(' + ", ".join(num(x) for x in t.times) + "),",
            '"transitions": PackedFloat32Array(' + ", ".join(num(x) for x in t.transitions) + "),",
            f'"update": {t.update},',
            '"values": [' + ", ".join(_lit(t.kind, v) for v in t.values) + "]",
            "}",
        ]
    return NL.join(lines)


# ---------------------------------------------------------------------------
# the state machine
# ---------------------------------------------------------------------------
#: States as the router names them, with their editor positions.
SM_STATES = {"idle": (327, 153), "attack": (327, 64), "hurt": (327, 278), "death": (470, 153),
             "cast": (186, 64), "power": (470, 64), "idle_low": (327, 365), "setoff": (186, 278)}
#: One-shots the router travels to; each returns to idle at its end.
SM_ONE_SHOTS = ("attack", "hurt", "cast", "power", "setoff")
#: Every live state can cut straight to any one-shot or to death, so a hit
#: during a throw shows at once rather than queueing behind it.
SM_SOURCES = ("idle", "idle_low", "attack", "hurt", "cast", "power", "setoff")
SM_TARGETS = ("attack", "hurt", "death", "cast", "power", "setoff")


def xfade(src: str, dst: str) -> float:
    """Cross-fade times from the base skeletons' SpineAnimationMix (census
    1c): default 0.05 s, 0.1 s from idle into an attack, ~0.03 s into a hurt,
    0.1 s out of one. Set Off fades itself (its clip cross-fades the two
    figures), and a hurt cuts straight to death as the base does."""
    if dst == "setoff" or (src == "setoff" and dst == "idle"):
        return 0.0
    if src == "hurt" and dst == "death":
        return 0.0
    if dst == "hurt":
        return 0.03
    if dst == "attack" and src in ("idle", "idle_low"):
        return 0.1
    if src == "hurt" and dst == "idle":
        return 0.1
    return 0.05


def _transition(tid: str, xf: float, switch: int, advance: int, cond: str | None = None) -> str:
    lines = [f'[sub_resource type="AnimationNodeStateMachineTransition" id="{tid}"]']
    if xf:
        lines.append(f"xfade_time = {fnum(xf)}")
    if switch:
        lines.append(f"switch_mode = {switch}")
    lines.append(f"advance_mode = {advance}")
    if cond:
        lines.append(f'advance_condition = &"{cond}"')
    return NL.join(lines)


def state_machine() -> str:
    """The AnimationTree graph. advance_mode 1 (enabled) is what lets
    `Travel` use a transition and so cross-fade; the old scene's were 0
    (disabled), so every Travel teleported and every clip snapped."""
    blocks = []
    for st in SM_STATES:
        blocks.append(f'[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_{st}"]'
                      + NL + f'animation = &"{st}"')
    edges = [("Start", "idle", _transition("Transition_start_idle", 0, 0, 2))]
    for src in SM_SOURCES:
        for dst in SM_TARGETS:
            if src != dst:
                edges.append((src, dst, _transition(f"Transition_{src}_{dst}", xfade(src, dst), 0, 1)))
    for src in SM_ONE_SHOTS:
        edges.append((src, "idle", _transition(f"Transition_{src}_idle", xfade(src, "idle"), 2, 2)))
    edges.append(("idle", "idle_low", _transition("Transition_idle_idle_low", 0.4, 0, 2, "low_hp")))
    edges.append(("idle_low", "idle", _transition("Transition_idle_low_idle", 0.4, 0, 2, "healthy")))
    edges.append(("death", "End", _transition("Transition_death_end", 0, 2, 0)))
    blocks += [e[2] for e in edges]
    sm = ['[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_klee"]',
          "states/End/position = Vector2(628, 153)",
          "states/Start/position = Vector2(186, 153)"]
    for st in sorted(SM_STATES):
        x, y = SM_STATES[st]
        sm.append(f'states/{st}/node = SubResource("AnimationNodeAnimation_{st}")')
        sm.append(f"states/{st}/position = Vector2({x}, {y})")
    ids = [e[2].split('id="')[1].split('"')[0] for e in edges]
    sm.append("transitions = [" + ", ".join(f'"{e[0]}", "{e[1]}", SubResource("{i}")'
                                             for e, i in zip(edges, ids)) + "]")
    blocks.append(NL.join(sm))
    return (NL + NL).join(blocks)


STATE_MACHINE = state_machine()

#: Bounds/CenterPos/IntentPos fit the figure (about 177 px to the feather at
#: 1080p, klee_frames.json "measure"): the base Silent's are a 244 px box for
#: a 224 px figure, CenterPos at ~0.65 of the height.
TAIL_NODES = """[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = -120.0
offset_top = -200.0
offset_right = 120.0
offset_bottom = 0.0
mouse_filter = 2

[node name="CenterPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, -100)

[node name="IntentPos" type="Marker2D" parent="."]
unique_name_in_owner = true
position = Vector2(0, -270)

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {
&"": SubResource("AnimationLibrary_klee")
}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_klee")
anim_player = NodePath("../AnimationPlayer")
metadata/idle_desync = true"""


def _model_nodes(rig: Rig, frames: dict) -> list[str]:
    """Visuals/Facing/Model and one Sprite2D per sheet. The sprite's offset
    puts the cell's feet anchor on the node origin; scale 0.5 because the
    sheets are drawn at 2x for a 4K screen."""
    sc = frames["combat_scale"]
    out = ['[node name="Model" type="Node2D" parent="Visuals/Facing"]']
    for name in rig.spec["model"]["sheets"]:
        rec = frames["sheets"][name]
        node = SHEET_NODE[name]
        ox, oy = rec["origin"]
        lines = [f'[node name="{node}" type="Sprite2D" parent="{MODEL}"]']
        if name != "idle":
            lines.append("self_modulate = Color(1, 1, 1, 0)")
        lines += [
            f'texture = ExtResource("{SHEET_IDS[name]}")',
            "centered = false",
            f"offset = {vec2((-ox, -oy))}",
            f"scale = {vec2((sc, sc))}",
            f"hframes = {rec['hframes']}",
            f"vframes = {rec['vframes']}",
        ]
        out.append(NL.join(lines))
    return out


SHEET_IDS = {name: f"{6 + i}_{name}" for i, name in enumerate(
    ("idle", "idle_low", "attack", "hurt", "death", "cast"))}


def _bone_nodes(rig: Rig) -> list[str]:
    out = [f'[node name="Skeleton" type="Skeleton2D" parent="{RIG}"]']
    for name in rig.order:
        b = rig.bones[name]
        parent = f"{RIG}/Skeleton" + (f"/{rig.path(b.parent)}" if b.parent else "")
        lx, ly = rig.local(name)
        if b.tip is not None:
            dx, dy = b.tip[0] - b.at[0], b.tip[1] - b.at[1]
            length, angle = math.hypot(dx, dy), math.atan2(dy, dx)
        else:
            length, angle = 4.0, -math.pi / 2
        out.append(NL.join([
            f'[node name="{name}" type="Bone2D" parent="{parent}"]',
            f"position = {vec2((lx, ly))}",
            f"rest = Transform2D(1, 0, 0, 1, {num(lx)}, {num(ly)})",
            "auto_calculate_length_and_angle = false",
            f"length = {fnum(round(length, 3))}",
            f"bone_angle = {fnum(round(math.degrees(angle), 3))}",
        ]))
    return out


def _polygon_node(rig: Rig, mesh: Mesh, ext_id: str) -> str:
    bones = []
    for b, ws in mesh.weights.items():
        bones.append(f'NodePath("{rig.path(b)}")')
        bones.append("PackedFloat32Array(" + ", ".join(num(w) for w in ws) + ")")
    return NL.join([
        f'[node name="{mesh.layer}" type="Polygon2D" parent="{RIG}"]',
        f'texture = ExtResource("{ext_id}")',
        "skeleton = NodePath(\"../Skeleton\")",
        "polygon = PackedVector2Array(" + ", ".join(f"{num(x)}, {num(y)}" for x, y in mesh.polygon) + ")",
        "uv = PackedVector2Array(" + ", ".join(f"{num(x)}, {num(y)}" for x, y in mesh.uv) + ")",
        "polygons = [" + ", ".join("PackedInt32Array(" + ", ".join(str(i) for i in q) + ")" for q in mesh.quads) + "]",
        "bones = [" + ", ".join(bones) + "]",
    ])


EXT_IDS = {"Smoke": "1_smoke", "Floaters": "2_floaters", "Dumpty": "3_dumpty",
           "Body": "4_body", "Dodoco": "5_dodoco"}


def render_scene(spec: dict | None = None, cells: dict | None = None,
                 frames: dict | None = None) -> str:
    rig = Rig(spec or load_spec(), cells or load_cells())
    frames = frames or load_frames()
    meshes = build_meshes(rig)
    anims = build_animations(rig, frames)
    for name, length in ONE_SHOT_LENGTHS.items():
        assert float(anims[name][0]["length"]) == length, f"{name} length changed"

    subs = [animation_block("Animation_reset", None, 0.001, False, reset_tracks(rig, anims))]
    for name in ANIMATION_ORDER:
        anim, tracks = anims[name]
        subs.append(animation_block(f"Animation_{name}", name, float(anim["length"]),
                                    bool(anim.get("loop")), tracks))
    lib = sorted(["RESET", *ANIMATION_ORDER], key=lambda n: (n != "RESET", n))
    subs.append('[sub_resource type="AnimationLibrary" id="AnimationLibrary_klee"]' + NL
                + "_data = {" + NL
                + ("," + NL).join(f'&"{n}": SubResource("Animation_{"reset" if n == "RESET" else n}")' for n in lib)
                + NL + "}")
    subs.append(STATE_MACHINE)

    ext = [(m.layer, m.texture) for m in meshes]
    sheets = rig.spec["model"]["sheets"]
    load_steps = len(ext) + len(sheets) + sum(s.count("[sub_resource") for s in subs) + 1
    out = [f"[gd_scene load_steps={load_steps} format=3]", ""]
    for layer, tex in ext:
        out.append(f'[ext_resource type="Texture2D" path="{TEX_DIR}/{tex}" id="{EXT_IDS[layer]}"]')
    for name in sheets:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{frames["sheets"][name]["file"]}" '
                   f'id="{SHEET_IDS[name]}"]')
    out.append("")
    for s in subs:
        out += [s, ""]
    nodes = [
        '[node name="KleeCombat" type="Node2D"]',
        '[node name="Visuals" type="Node2D" parent="."]\nunique_name_in_owner = true',
        '[node name="Facing" type="Node2D" parent="Visuals"]\nunique_name_in_owner = true',
        f'[node name="Rig" type="Node2D" parent="Visuals/Facing"]\nmodulate = Color(1, 1, 1, 0)\n'
        f'position = {vec2(rig.spec["rig_position"])}',
        *_bone_nodes(rig),
        *[_polygon_node(rig, m, EXT_IDS[m.layer]) for m in meshes],
        *_model_nodes(rig, frames),
        TAIL_NODES,
    ]
    for n in nodes:
        out += [n, ""]
    return NL.join(out).rstrip(NL) + NL


# ---------------------------------------------------------------------------
# the merchant scene
# ---------------------------------------------------------------------------
MERCHANT_SCENE = ROOT / "klee-mod" / "pck-src" / "klee" / "model" / "merchant_character.tscn"


def render_merchant_scene(frames: dict | None = None) -> str:
    """Klee at the shop: stance B (the bomb cradled) breathing on a loop.

    The base merchant rig is the combat skeleton at ~1.7x with its own
    `relaxed_loop` (census T2); its feet sit on the node origin. BaseLib adds
    this scene's ROOT as the NMerchantCharacter's first child and also copies
    the root's transform onto the merchant node itself, so the root is a bare
    Node2D and the scale lives on the sheet sprite below it. The idle needs no
    script: the AnimationPlayer autoplays it (MerchantSpineBindingPatch skips
    the base's Spine binding, which would otherwise try to play it).
    """
    frames = frames or load_frames()
    rec = frames["sheets"]["merchant"]
    sc = frames["merchant_scale"]
    ox, oy = rec["origin"]
    times = [float(t) for t in rec["times"]]
    assert abs(len(times) / rec["fps"] - rec["length"]) < 1e-6
    anim = animation_block("Animation_relaxed", "relaxed_loop", float(rec["length"]), True,
                           [Track("Sheet:frame", "int", times, list(range(len(times))), [1.0] * len(times),
                                  interp=0, update=1)])
    reset = animation_block("Animation_reset", None, 0.001, False,
                            [Track("Sheet:frame", "int", [0.0], [0], [1.0], interp=0, update=1)])
    lib = ('[sub_resource type="AnimationLibrary" id="AnimationLibrary_merchant"]' + NL + "_data = {" + NL
           + '&"RESET": SubResource("Animation_reset"),' + NL
           + '&"relaxed_loop": SubResource("Animation_relaxed")' + NL + "}")
    out = [
        "[gd_scene load_steps=5 format=3]", "",
        f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{rec["file"]}" id="1_sheet"]', "",
        reset, "", anim, "", lib, "",
        '[node name="KleeMerchant" type="Node2D"]', "",
        NL.join([
            '[node name="Sheet" type="Sprite2D" parent="."]',
            'texture = ExtResource("1_sheet")',
            "centered = false",
            f"offset = {vec2((-ox, -oy))}",
            f"scale = {vec2((sc, sc))}",
            f"hframes = {rec['hframes']}",
            f"vframes = {rec['vframes']}",
        ]), "",
        NL.join([
            '[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
            "libraries = {",
            '&"": SubResource("AnimationLibrary_merchant")',
            "}",
            'autoplay = "relaxed_loop"',
        ]),
    ]
    return NL.join(out) + NL
