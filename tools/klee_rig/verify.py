"""Checks for Klee's generated combat scene.

Static (no art, no engine; tier0/tests/test_klee_rig.py runs these):
  * the scene is what the generator writes now (byte-identical rerun);
  * the contract: Visuals/Facing, Bounds, CenterPos, IntentPos,
    AnimationPlayer, AnimationTree, the eight states plus RESET, the
    one-shot lengths, the state machine block, and every track's node exists;
  * the model: one Sprite2D per sheet under Visuals/Facing/Model, its grid
    and anchor from klee_frames.json, and each state's frame track stepping
    through exactly the frames the manifest lists.

With `--godot`: MegaDot loads the scene headless (probe.gd), steps the
AnimationTree through idle, attack, hurt, setoff and death and reads back
which sheet shows at which frame, and checks the merchant loop autoplays.
"""
from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import rig

CONTRACT_NODES = ("Visuals", "Visuals/Facing", "Visuals/Facing/Model", "Bounds",
                  "CenterPos", "IntentPos", "AnimationPlayer", "AnimationTree")
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
    if "Visuals/Facing/Rig" in nodes or any(n.type in ("Skeleton2D", "Polygon2D") for n in nodes.values()):
        bad.append("the retired splash rig is back in the scene")
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


def godot_problems(art_root: Path, work: Path | None) -> list[str]:
    """MegaDot loads the scene headless and drives its tree (probe.gd)."""
    from . import engine

    bad = []
    work = work or Path(tempfile.mkdtemp(prefix="klee_rig_"))
    engine.make_project(work, art_root)
    engine.import_project(work)
    code, log = engine.run(work, ["--headless", "--script", "res://probe.gd", "--", "res://klee/model/combat.tscn"])
    print("\n".join(l for l in log.splitlines() if l.startswith("PROBE|")))
    if code != 0:
        bad.append(f"probe exit {code}")
    return bad


def main(art_root: Path, godot: bool, work: str | None) -> int:
    text = rig.SCENE.read_text(encoding="utf-8")
    problems = []
    if rig.render_scene() != text:
        problems.append("combat.tscn is stale against the generator")
    problems += static_problems(text)
    if godot:
        problems += godot_problems(art_root, Path(work) if work else None)
    for p in problems:
        print("FAIL", p)
    print("klee scene verify:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0
