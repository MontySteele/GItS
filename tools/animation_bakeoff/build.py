"""Generate one self-contained Godot project per approach.

    python -m tools.animation_bakeoff.build --out <dir> [--approach layered]

Each project is a complete, minimal Godot 4 project whose only job is to import
the synthetic art and export a `.pck` -- the same job `tools/build_pck.ps1`'s
scratch project does, and deliberately the same `project.godot` /
`export_presets.cfg` shape (`tools/build_pck.ps1:82-116`), so the bake-off
measures the approaches rather than measuring a different pipeline.

This lane does NOT run, edit, or import `tools/build_pck.ps1`. It borrows the
editor path and the two headless flags and nothing else.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import approaches, art
from .spec import BONES, PARTS, REQUIRED_MOTIONS, ROUTED_STATES, all_motions, hand_authored_numbers

TEX_DIR = "res://sprig/art"

PROJECT_GODOT = """; Bake-off project (dispatch3 lane A). Generated -- do not hand-edit.
; Its only job is to import the synthetic rig and export a .pck, matching the
; scratch project tools/build_pck.ps1 writes.
config_version=5

[application]

config/name="SprigBakeoff{suffix}"

[rendering]

renderer/rendering_method="mobile"
"""

EXPORT_PRESETS = """[preset.0]

name="pck"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter="*.gd,bakeoff-manifest.json"
export_path="sprig.pck"
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

binary_format/embed_pck=false
"""

# Editor-side evidence. Live capture is not available to this lane (the game is
# in use), so the strongest available proof that a scene is real is: load it
# headless, walk it, and print what is actually there. Runs INSIDE the
# synthetic project only; the shipped pck rule "no scripts in scenes" is
# untouched -- this is a project script, not a scene script, and the export
# preset filters `*.gd` out of the pack.
PROBE_GD = """extends SceneTree

# Bake-off probe (dispatch3 lane A). Generated -- do not hand-edit.
# Prints machine-readable PROBE| lines and exits non-zero if the scene did not
# load, so a broken scene is a build failure rather than a silent zero.

func _count(node: Node) -> int:
\tvar n := 1
\tfor c in node.get_children():
\t\tn += _count(c)
\treturn n


func _all(node: Node, acc: Array) -> Array:
\tacc.append(node)
\tfor c in node.get_children():
\t\t_all(c, acc)
\treturn acc


func _initialize() -> void:
\tvar path = "res://sprig/SCENE_NAME.tscn"
\tvar packed = ResourceLoader.load(path)
\tif packed == null:
\t\tprint("PROBE|error=scene_load_failed")
\t\tquit(2)
\t\treturn
\tvar root = packed.instantiate()
\tif root == null:
\t\tprint("PROBE|error=instantiate_failed")
\t\tquit(3)
\t\treturn
\tprint("PROBE|scene=", path)
\tprint("PROBE|nodes=", _count(root))
\tvar deps = ResourceLoader.get_dependencies(path)
\tprint("PROBE|dependencies=", deps.size())
\tfor d in deps:
\t\tprint("PROBE|dependency=", d)
\tvar player = root.get_node_or_null("AnimationPlayer")
\tif player == null:
\t\tprint("PROBE|error=no_animation_player")
\t\tquit(4)
\t\treturn
\tvar names = player.get_animation_list()
\tprint("PROBE|animations=", names.size())
\tfor n in names:
\t\tvar a = player.get_animation(n)
\t\tprint("PROBE|animation=", n, "|length=", a.length, "|tracks=", a.get_track_count(), "|loop=", a.loop_mode)
\tvar tree = root.get_node_or_null("AnimationTree")
\tif tree == null:
\t\tprint("PROBE|error=no_animation_tree")
\t\tquit(5)
\t\treturn
\tvar sm = tree.tree_root
\tvar states = sm.get_node_list()
\tprint("PROBE|states=", states.size())
\tfor s in states:
\t\tprint("PROBE|state=", s)
\tvar missing = 0
\tfor d in deps:
\t\tvar dep_path = d.get_slice("::", 2)
\t\tif dep_path == "":
\t\t\tdep_path = d
\t\tif not ResourceLoader.exists(dep_path):
\t\t\tmissing += 1
\t\t\tprint("PROBE|missing_dependency=", dep_path)
\tprint("PROBE|missing_dependencies=", missing)
\t# Rig census. `skinned` is the load-bearing one: a Polygon2D whose bone
\t# weights failed to deserialise reports 0 here while every other signal --
\t# import, export, scene load -- stays green.
\tvar sprites = 0
\tvar bones = 0
\tvar polygons = 0
\tvar skinned = 0
\tvar emitters = 0
\tfor n in _all(root, []):
\t\tif n is Bone2D:
\t\t\tbones += 1
\t\telif n is Polygon2D:
\t\t\tpolygons += 1
\t\t\tif n.get_bone_count() > 0:
\t\t\t\tskinned += 1
\t\telif n is GPUParticles2D:
\t\t\temitters += 1
\t\telif n is Sprite2D:
\t\t\tsprites += 1
\tprint("PROBE|sprites=", sprites)
\tprint("PROBE|bone2d=", bones)
\tprint("PROBE|polygons=", polygons)
\tprint("PROBE|skinned_polygons=", skinned)
\tprint("PROBE|emitters=", emitters)
\tprint("PROBE|ok=1")
\troot.free()
\tquit(0)
"""


def project_dir(out: Path, key: str) -> Path:
    return out / key


def write_project(out: Path, key: str) -> dict[str, object]:
    root = project_dir(out, key)
    art_dir = root / "sprig" / "art"
    root.mkdir(parents=True, exist_ok=True)
    art_dir.mkdir(parents=True, exist_ok=True)

    # Scene first, art second: the scene decides which layers exist, so the
    # project carries exactly the textures its own approach references.
    result = approaches.build(key, TEX_DIR)
    want = {Path(t).stem.removeprefix("sprig_") for t in result.textures}
    written = art.write_layers(art_dir, want)

    scene_path = root / "sprig" / f"{key}.tscn"
    scene_path.write_text(result.scene_text, encoding="utf-8", newline="\n")

    (root / "project.godot").write_text(
        PROJECT_GODOT.format(suffix=key.capitalize()), encoding="utf-8", newline="\n"
    )
    (root / "export_presets.cfg").write_text(EXPORT_PRESETS, encoding="utf-8", newline="\n")
    (root / "probe.gd").write_text(
        PROBE_GD.replace("SCENE_NAME", key), encoding="utf-8", newline="\n"
    )

    # Textures the scene actually references, so the failure-mode experiment
    # knows exactly which file to delete. `unused` should stay empty; if it
    # ever fills, the pack is carrying art no scene names (see
    # `art.write_layers`).
    used = list(result.textures)
    unused = sorted(
        f"{TEX_DIR}/{p.name}" for p in art_dir.iterdir() if f"{TEX_DIR}/{p.name}" not in used
    )

    manifest = {
        "approach": key,
        "scene": f"sprig/{key}.tscn",
        "scene_bytes": len(result.scene_text.encode("utf-8")),
        "scene_lines": result.scene_text.count("\n"),
        "node_count": result.node_count,
        "track_count": result.scene_text.count('/type = "value"'),
        "textures_referenced": used,
        "textures_generated_unused": unused,
        "art_files": len(written),
        "art_bytes": sum(p.stat().st_size for p in art_dir.iterdir()),
        "fidelity": result.fidelity.as_dict(),
        "shared_hand_authored_numbers": hand_authored_numbers(),
        "extra_hand_authored_numbers": result.extra_numbers,
    }
    (root / "bakeoff-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def write_all(out: Path) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=True)
    manifests = {key: write_project(out, key) for key in approaches.APPROACH_KEYS}
    index = {
        "rig": {
            "parts": [p.name for p in PARTS],
            "bones": [b.name for b in BONES],
            "shapes": sorted({p.shape for p in PARTS}),
        },
        "motions": {
            "required": list(REQUIRED_MOTIONS),
            "routed_today": list(ROUTED_STATES),
            "emitted": [m.name for m in all_motions()],
        },
        "shared_hand_authored_numbers": hand_authored_numbers(),
        "approaches": manifests,
    }
    (out / "bakeoff-index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="directory to generate into")
    parser.add_argument(
        "--approach",
        choices=approaches.APPROACH_KEYS,
        help="generate only this approach (default: all four)",
    )
    args = parser.parse_args(argv)

    if args.approach:
        args.out.mkdir(parents=True, exist_ok=True)
        manifest = write_project(args.out, args.approach)
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        index = write_all(args.out)
        for key, manifest in index["approaches"].items():  # type: ignore[union-attr]
            print(
                f"{key:10s} nodes={manifest['node_count']:3d} "
                f"tracks={manifest['track_count']:3d} "
                f"scene={manifest['scene_bytes']:6d}B "
                f"dropped={len(manifest['fidelity']['dropped']):2d} "
                f"relocated={len(manifest['fidelity']['relocated']):2d}"
            )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
