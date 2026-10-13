"""Checks for the Klee mesh rig.

Static (no art, no engine; tier0/tests/test_klee_rig.py runs these):
  * the scene is what the generator writes now (byte-identical rerun);
  * every Polygon2D carries a flat `bones` array -- one weight array per
    bone, each as long as the polygon -- and every bone path is a Bone2D;
  * REST IS EXACT, statically: polygon == uv + the texture's top-left (the
    old centred sprite's corner), every vertex's weights sum to 1 with at
    most four bones, and every Bone2D's position equals its rest;
  * the contract: Visuals/Facing/Rig, Bounds, CenterPos, IntentPos,
    AnimationPlayer, AnimationTree, the eight states plus RESET, the
    one-shot lengths, the state machine block, and every track's node exists;
  * the model: one Sprite2D per sheet under Visuals/Facing/Model, its grid
    and anchor from klee_frames.json, and each state's frame track stepping
    through exactly the frames the manifest lists.

With art (`--art-root`): klee_cells.json still matches the PNGs, and every
texel the old sprite could draw (alpha > 0, grown one texel for filtering)
lies inside a mesh cell.

With `--godot`: MegaDot loads the scene headless and reports
get_bone_count() > 0 for every polygon (probe.gd), then renders RESET of the
mesh scene and of the layered reference at 1x and 2x, facing both ways, and
diffs them pixel by pixel.
"""
from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import rig

CONTRACT_NODES = ("Visuals", "Visuals/Facing", "Visuals/Facing/Rig", "Bounds",
                  "CenterPos", "IntentPos", "AnimationPlayer", "AnimationTree")
REST_TOLERANCE = 2
STATES = ("idle", "attack", "hurt", "death", "cast", "power", "idle_low", "setoff")

HEAD_RE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)"(?: parent="([^"]+)")?\]')


@dataclass
class Node:
    name: str
    type: str
    path: str
    props: dict[str, str] = field(default_factory=dict)


def parse_nodes(text: str) -> dict[str, Node]:
    nodes: dict[str, Node] = {}
    cur: Node | None = None
    for line in text.split("\n"):
        m = HEAD_RE.match(line)
        if m:
            name, typ, parent = m.groups()
            path = "." if parent is None else (name if parent == "." else f"{parent}/{name}")
            cur = Node(name, typ, path)
            nodes[path] = cur
            continue
        if line.startswith("["):
            cur = None
            continue
        if cur is not None and " = " in line:
            k, v = line.split(" = ", 1)
            cur.props[k] = v
    return nodes


def _floats(s: str) -> list[float]:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", s)]


def _inner(v: str) -> str:
    return v[v.index("(") + 1: v.rindex(")")]


def parse_vec_array(v: str) -> list[tuple[float, float]]:
    f = _floats(v[v.index("(") + 1: v.rindex(")")])
    return list(zip(f[0::2], f[1::2]))


def parse_bones(v: str) -> list[tuple[str, list[float]]]:
    """The flat `bones = [NodePath("a"), PackedFloat32Array(...), ...]`."""
    out = []
    for m in re.finditer(r'NodePath\("([^"]+)"\), PackedFloat32Array\(([^)]*)\)', v):
        out.append((m.group(1), _floats(m.group(2))))
    return out


def track_paths(text: str) -> dict[str, list[str]]:
    anims: dict[str, list[str]] = {}
    cur = None
    for line in text.split("\n"):
        m = re.match(r'^\[sub_resource type="Animation" id="Animation_(\w+)"\]', line)
        if m:
            cur = "RESET" if m.group(1) == "reset" else m.group(1)
            anims[cur] = []
            continue
        if line.startswith("["):
            cur = None
        m = re.match(r'^tracks/\d+/path = NodePath\("([^"]+)"\)', line)
        if m and cur:
            anims[cur].append(m.group(1))
    return anims


def static_problems(text: str) -> list[str]:
    bad: list[str] = []
    nodes = parse_nodes(text)
    for p in CONTRACT_NODES:
        if p not in nodes:
            bad.append(f"contract node missing: {p}")
    cells = rig.load_cells()
    skel = "Visuals/Facing/Rig/Skeleton"
    if nodes.get(skel, Node("", "", "")).type != "Skeleton2D":
        bad.append("no Skeleton2D at " + skel)
    for path, n in nodes.items():
        if n.type == "Bone2D":
            pos = _floats(_inner(n.props["position"]))
            rest = _floats(_inner(n.props["rest"]))
            if rest != [1, 0, 0, 1, *pos]:
                bad.append(f"{path}: position {pos} != rest {rest}")
    for name, rec in cells["layers"].items():
        n = nodes.get(f"Visuals/Facing/Rig/{name}")
        if n is None or n.type != "Polygon2D":
            bad.append(f"layer {name} is not a Polygon2D")
            continue
        if any(k in n.props for k in ("position", "scale", "rotation", "offset")):
            bad.append(f"{name}: a skinned Polygon2D must sit untransformed")
        if any(k.startswith("bones/") for k in n.props):
            bad.append(f"{name}: bones/N/... lines are dropped by the parser")
        poly = parse_vec_array(n.props["polygon"])
        uv = parse_vec_array(n.props["uv"])
        tx, ty = rec["topleft"]
        if len(poly) != len(uv) or any(abs(px - (ux + tx)) > 1e-6 or abs(py - (uy + ty)) > 1e-6
                                       for (px, py), (ux, uy) in zip(poly, uv)):
            bad.append(f"{name}: polygon != uv + topleft (rest pose would not match)")
        w, h = rec["texture"]
        if any(not (0 <= u <= w and 0 <= v <= h) for u, v in uv):
            bad.append(f"{name}: uv outside the texture")
        bones = parse_bones(n.props.get("bones", ""))
        if not bones:
            bad.append(f"{name}: no bones (flat bones array missing)")
            continue
        for bpath, ws in bones:
            if len(ws) != len(poly):
                bad.append(f"{name}: bone {bpath} has {len(ws)} weights for {len(poly)} vertices")
            if nodes.get(f"{skel}/{bpath}", Node("", "", "")).type != "Bone2D":
                bad.append(f"{name}: bone path {bpath} is not a Bone2D")
        for i in range(len(poly)):
            col = [ws[i] for _b, ws in bones if i < len(ws)]
            if abs(sum(col) - 1.0) > 1e-6 or sum(1 for c in col if c > 0) > 4:
                bad.append(f"{name}: vertex {i} weights {col}")
                break
    anims = track_paths(text)
    for s in ("RESET", *STATES):
        if s not in anims:
            bad.append(f"animation missing: {s}")
    for a, paths in anims.items():
        for p in paths:
            if p.split(":")[0] not in nodes:
                bad.append(f"{a}: track to missing node {p}")
    for a, length in rig.ONE_SHOT_LENGTHS.items():
        if f'resource_name = "{a}"\nlength = {rig.fnum(length)}\n' not in text:
            bad.append(f"{a}: length is not {length}")
    if rig.STATE_MACHINE not in text:
        bad.append("state machine block differs from the contract")
    frames = rig.load_frames()
    spec = rig.load_spec()
    for name in spec["model"]["sheets"]:
        rec = frames["sheets"][name]
        n = nodes.get(f"{rig.MODEL}/{rig.SHEET_NODE[name]}")
        if n is None or n.type != "Sprite2D":
            bad.append(f"sheet {name}: no Sprite2D under {rig.MODEL}")
            continue
        if n.props.get("hframes") != str(rec["hframes"]) or n.props.get("vframes") != str(rec["vframes"]):
            bad.append(f"sheet {name}: grid differs from klee_frames.json")
        if rec["hframes"] * rec["vframes"] < rec["count"]:
            bad.append(f"sheet {name}: {rec['count']} frames do not fit its grid")
    for state, anim in spec["animations"].items():
        if "hold_frame" in anim:
            continue
        want = len(frames["sheets"][anim["sheet"]]["times"])
        block = text[text.index(f'resource_name = "{state}"'):]
        block = block[:block.index("[sub_resource")]
        node = rig.SHEET_NODE[anim["sheet"]]
        i = block.index(f'NodePath("{rig.MODEL}/{node}:frame")')
        times = block[i:].split('"times": PackedFloat32Array(', 1)[1].split(")", 1)[0]
        if len(times.split(",")) != want:
            bad.append(f"{state}: frame track has {len(times.split(','))} keys, manifest {want}")
    return bad


def coverage_problems(art_root: Path) -> list[str]:
    """Every texel the old sprite drew lies inside the mesh."""
    import numpy as np
    from PIL import Image

    from . import cells as cells_mod

    bad = []
    spec, cells = rig.load_spec(), rig.load_cells()
    if cells_mod.dump(cells_mod.extract(spec, art_root)) != rig.CELLS.read_text(encoding="utf-8"):
        bad.append("klee_cells.json is stale against the art (run extract)")
    for layer in spec["layers"]:
        rec = cells["layers"][layer["name"]]
        a = np.asarray(Image.open(art_root / cells_mod.LAYER_DIR / layer["texture"]).convert("RGBA"))[..., 3]
        lit = cells_mod._grow(a > 0, 1)
        c = rec["cell"]
        covered = np.zeros_like(lit)
        for gy, row in enumerate(rec["rows"]):
            for gx, ch in enumerate(row):
                if ch != ".":
                    covered[gy * c:(gy + 1) * c, gx * c:(gx + 1) * c] = True
        miss = int((lit & ~covered).sum())
        if miss:
            bad.append(f"{layer['name']}: {miss} drawn texels outside the mesh")
    return bad


def godot_problems(art_root: Path, work: Path | None) -> list[str]:
    import numpy as np
    from PIL import Image

    from . import engine

    bad = []
    work = work or Path(tempfile.mkdtemp(prefix="klee_rig_"))
    engine.make_project(work, art_root)
    engine.import_project(work)
    code, log = engine.run(work, ["--headless", "--script", "res://probe.gd", "--", "res://klee/model/combat.tscn"])
    lines = [l for l in log.splitlines() if l.startswith("PROBE|")]
    print("\n".join(lines))
    if code != 0:
        bad.append(f"probe exit {code}")
    out = work / "rest"
    out.mkdir(exist_ok=True)
    passes = []
    for scale in (1, 2):
        for facing in (1, -1):
            for kind in ("combat", "reference"):
                passes.append({"scene": f"res://klee/model/{kind}.tscn", "out": out.as_posix(),
                               "prefix": f"{kind}_s{scale}_f{facing}_", "scale": scale,
                               "w": 300 * scale, "h": 340 * scale,
                               "origin": [150 * scale, 320 * scale], "facing": facing,
                               # The splash rig rests invisible since milestone
                               # 2; setoff at 0.6 s shows it alone, at rest.
                               "jobs": [["setoff", [0.6]] if kind == "combat" else ["RESET", [0]]]})
    # Facing parity: CreatureFacing flips Visuals/Facing's x scale. A posed
    # frame flipped must be the mirror image of the unflipped one, or the
    # skin is being computed in the wrong space under a negative scale.
    for facing in (1, -1):
        passes.append({"scene": "res://klee/model/combat.tscn", "out": out.as_posix(),
                       "prefix": f"posed_f{facing}_", "scale": 1, "w": 300, "h": 340,
                       "origin": [150, 320], "facing": facing,
                       "jobs": [["setoff", [0.27]], ["death", [0.6]]]})
    engine.render(work, passes)
    for anim in ("setoff", "death"):
        a = np.asarray(Image.open(out / f"posed_f1_{anim}_000.png"), dtype=np.int16)
        b = np.asarray(Image.open(out / f"posed_f-1_{anim}_000.png"), dtype=np.int16)[:, ::-1]
        d = np.abs(a - b)
        print(f"FACING|{anim}|max_diff={int(d.max())}|pixels_differing={int((d.max(axis=2) > 8).sum())}")
        if int((d.max(axis=2) > 8).sum()) > 0.01 * int((a[..., 3] > 0).sum()):
            bad.append(f"{anim}: flipped pose is not the mirror of the unflipped pose")
    for scale in (1, 2):
        for facing in (1, -1):
            a = np.asarray(Image.open(out / f"combat_s{scale}_f{facing}_setoff_000.png"), dtype=np.int16)
            b = np.asarray(Image.open(out / f"reference_s{scale}_f{facing}_RESET_000.png"), dtype=np.int16)
            d = np.abs(a - b)
            print(f"REST|scale={scale}|facing={facing}|max_diff={int(d.max())}|"
                  f"pixels_differing={int((d.max(axis=2) > 0).sum())}|opaque={int((b[..., 3] > 0).sum())}")
            # 2/255 is the GPU's barycentric UV interpolation (a textured
            # triangle pair vs the sprite's quad), measured on 0.6% of
            # opaque pixels; anything a misplaced vertex could cause is far larger.
            if int(d.max()) > REST_TOLERANCE:
                bad.append(f"rest pose differs from the layered composite at {scale}x facing {facing} "
                           f"(max {int(d.max())})")
    return bad


def main(art_root: Path, godot: bool, work: str | None) -> int:
    text = rig.SCENE.read_text(encoding="utf-8")
    problems = []
    if rig.render_scene() != text:
        problems.append("combat.tscn is stale against the generator")
    problems += static_problems(text)
    if (art_root / "ImageGen").is_dir():
        problems += coverage_problems(art_root)
    else:
        print(f"SKIP coverage: no ImageGen/ under {art_root}")
    if godot:
        problems += godot_problems(art_root, Path(work) if work else None)
    for p in problems:
        print("FAIL", p)
    print("klee rig verify:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0
