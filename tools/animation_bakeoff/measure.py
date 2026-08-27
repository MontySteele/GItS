"""Join the generated projects, the probe output, and the exported packs into
one comparison table.

    python -m tools.animation_bakeoff.measure \\
        --projects <dir> --exports <dir> --out review/dispatch3/lane-a

Reads only; it produces `bakeoff-results.json` and `bakeoff-matrix.md`. Every
number in the output is either read out of a file this run produced or counted
from generated source -- nothing here is estimated, and an input that is absent
is reported as `null` rather than filled in.
"""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

from . import approaches, pck
from .spec import BONES, PARTS, REQUIRED_MOTIONS, ROUTED_STATES, hand_authored_numbers

PROBE_PREFIX = "PROBE|"


def probe_facts(log: Path) -> dict[str, object]:
    """Parse the `PROBE|` lines the editor-side probe printed."""
    if not log.exists():
        return {}
    facts: dict[str, object] = {"animations": [], "states": [], "dependencies": []}
    for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if PROBE_PREFIX not in raw:
            continue
        body = raw[raw.index(PROBE_PREFIX) + len(PROBE_PREFIX) :].strip()
        if body.startswith("animation="):
            fields = dict(part.split("=", 1) for part in body.split("|") if "=" in part)
            facts["animations"].append(  # type: ignore[union-attr]
                {
                    "name": fields.get("animation"),
                    "length": float(fields.get("length", 0)),
                    "tracks": int(fields.get("tracks", 0)),
                    "loop": int(fields.get("loop", 0)),
                }
            )
        elif body.startswith("state="):
            facts["states"].append(body.split("=", 1)[1])  # type: ignore[union-attr]
        elif body.startswith("dependency="):
            facts["dependencies"].append(body.split("=", 1)[1])  # type: ignore[union-attr]
        elif "=" in body:
            key, value = body.split("=", 1)
            if key in (
                "nodes",
                "animations",
                "states",
                "dependencies",
                "missing_dependencies",
                "sprites",
                "bone2d",
                "polygons",
                "skinned_polygons",
                "emitters",
            ):
                # scalar counts; the list keys above already hold the detail
                facts[f"{key}_count"] = int(value)
            else:
                facts[key] = value
    return facts


def builder_lines(key: str) -> int:
    """How many lines of generator the approach's own builder costs."""
    source, _ = inspect.getsourcelines(approaches.BUILDERS[key])
    return len(source)


def pack_facts(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    pack = pck.read(path)
    ctex = [e for e in pack.entries if e.path.endswith(".ctex")]
    scenes = [e for e in pack.entries if e.path.endswith((".scn", ".remap"))]
    return {
        "bytes": pack.total_bytes,
        "resources": len(pack.entries),
        "payload_bytes": pack.payload_bytes,
        "texture_resources": len(ctex),
        "texture_bytes": sum(e.size for e in ctex),
        "scene_resources": len(scenes),
        "scene_bytes": sum(e.size for e in scenes),
        "engine_version": ".".join(str(n) for n in pack.engine_version),
        "pack_format": pack.format_version,
    }


def collect(projects: Path, exports: Path) -> dict[str, object]:
    results_path = exports / "export-results.json"
    export_results: dict[str, object] = {}
    if results_path.exists():
        export_results = json.loads(results_path.read_text(encoding="utf-8-sig"))

    rows: dict[str, object] = {}
    for key in approaches.APPROACH_KEYS:
        manifest_path = projects / key / "bakeoff-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        probe = probe_facts(exports / f"{key}-probe.log")
        packs = {run: pack_facts(exports / f"{key}-{run}.pck") for run in ("warm1", "warm2", "cold")}
        run_meta = export_results.get(key, {}) if isinstance(export_results, dict) else {}
        shas = {}
        if isinstance(run_meta, dict):
            for run, info in (run_meta.get("packs") or {}).items():
                shas[run] = info.get("sha256")

        distinct = {s for s in shas.values() if s}
        rows[key] = {
            "source": {
                "builder_lines": builder_lines(key),
                "shared_hand_authored_numbers": manifest.get("shared_hand_authored_numbers"),
                "extra_hand_authored_numbers": manifest.get("extra_hand_authored_numbers"),
                "art_files": manifest.get("art_files"),
                "art_bytes": manifest.get("art_bytes"),
                "scene_bytes": manifest.get("scene_bytes"),
                "scene_lines": manifest.get("scene_lines"),
                "textures_referenced": manifest.get("textures_referenced"),
                "textures_generated_unused": manifest.get("textures_generated_unused"),
            },
            "scene": {
                "node_count": manifest.get("node_count"),
                "track_count": manifest.get("track_count"),
                "probe_node_count": probe.get("nodes_count"),
                "probe_animation_count": probe.get("animations_count"),
                "probe_state_count": probe.get("states_count"),
                "probe_dependency_count": probe.get("dependencies_count"),
                "probe_missing_dependencies": probe.get("missing_dependencies_count"),
                "probe_ok": probe.get("ok") == "1",
                "probe_sprites": probe.get("sprites_count"),
                "probe_bone2d": probe.get("bone2d_count"),
                "probe_polygons": probe.get("polygons_count"),
                "probe_skinned_polygons": probe.get("skinned_polygons_count"),
                "probe_emitters": probe.get("emitters_count"),
                "animations": probe.get("animations"),
                "states": probe.get("states"),
            },
            "fidelity": manifest.get("fidelity"),
            "packs": packs,
            "repeatability": {
                "sha256": shas,
                "warm_repeatable": bool(shas.get("warm1")) and shas.get("warm1") == shas.get("warm2"),
                "cold_repeatable": bool(shas.get("warm1")) and shas.get("warm1") == shas.get("cold"),
                "distinct_hashes": len(distinct),
            },
            "failure_mode": (run_meta or {}).get("failure_mode"),
            "editor_exit_codes": {
                "import": (run_meta or {}).get("import_exit"),
                "probe": (run_meta or {}).get("probe_exit"),
                "cold_import": (run_meta or {}).get("cold_import_exit"),
            },
        }

    return {
        "rig": {
            "parts": len(PARTS),
            "part_names": [p.name for p in PARTS],
            "bones": len(BONES),
            "bone_names": [b.name for b in BONES],
        },
        "motions": {
            "required": list(REQUIRED_MOTIONS),
            "routed_today": list(ROUTED_STATES),
            "shared_hand_authored_numbers": hand_authored_numbers(),
        },
        "approaches": rows,
    }


def _cell(value: object) -> str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def render_matrix(data: dict[str, object]) -> str:
    keys = list(approaches.APPROACH_KEYS)
    rows = data["approaches"]  # type: ignore[index]

    def line(label: str, get) -> str:
        return "| " + " | ".join([label] + [_cell(get(rows[k])) for k in keys]) + " |"

    head = "| measure | " + " | ".join(keys) + " |"
    rule = "|---" * (len(keys) + 1) + "|"
    out = [
        "## Joined capability matrix",
        "",
        "One synthetic rig, one motion suite, four renderings. Every number is",
        "measured from this run; `UNKNOWN` means the input was absent.",
        "",
        head,
        rule,
        line("generator lines (builder only)", lambda r: r["source"]["builder_lines"]),
        line("scene bytes", lambda r: r["source"]["scene_bytes"]),
        line("scene lines", lambda r: r["source"]["scene_lines"]),
        line("nodes in scene", lambda r: r["scene"]["node_count"]),
        line("nodes at load (probe)", lambda r: r["scene"]["probe_node_count"]),
        line("animation value tracks", lambda r: r["scene"]["track_count"]),
        line("animations (probe)", lambda r: r["scene"]["probe_animation_count"]),
        line("state-machine states (probe)", lambda r: r["scene"]["probe_state_count"]),
        line("Sprite2D at load (probe)", lambda r: r["scene"]["probe_sprites"]),
        line("Bone2D at load (probe)", lambda r: r["scene"]["probe_bone2d"]),
        line("Polygon2D at load (probe)", lambda r: r["scene"]["probe_polygons"]),
        line("...of those actually skinned", lambda r: r["scene"]["probe_skinned_polygons"]),
        line("GPUParticles2D at load (probe)", lambda r: r["scene"]["probe_emitters"]),
        line("source art files", lambda r: r["source"]["art_files"]),
        line("source art bytes", lambda r: r["source"]["art_bytes"]),
        line("shared hand-authored numbers", lambda r: r["source"]["shared_hand_authored_numbers"]),
        line("extra hand-authored numbers", lambda r: r["source"]["extra_hand_authored_numbers"]),
        line("tracks expressed as written", lambda r: (r["fidelity"] or {}).get("expressed")),
        line("tracks relocated", lambda r: len((r["fidelity"] or {}).get("relocated", []))),
        line("tracks dropped", lambda r: len((r["fidelity"] or {}).get("dropped", []))),
        line("pck bytes", lambda r: (r["packs"]["warm1"] or {}).get("bytes")),
        line("pck resources", lambda r: (r["packs"]["warm1"] or {}).get("resources")),
        line("pck texture bytes", lambda r: (r["packs"]["warm1"] or {}).get("texture_bytes")),
        line("pck scene bytes", lambda r: (r["packs"]["warm1"] or {}).get("scene_bytes")),
        line("re-export byte-identical", lambda r: r["repeatability"]["warm_repeatable"]),
        line("cold re-export byte-identical", lambda r: r["repeatability"]["cold_repeatable"]),
        line("probe reported ok", lambda r: r["scene"]["probe_ok"]),
        "",
    ]
    return "\n".join(out)


def render_evidence(exports: Path) -> str:
    """The raw `PROBE|` lines, stripped of console colour and shell noise.

    Committed alongside the matrix so the handoff's numbers can be checked
    without re-running the editor. The full editor logs stay in the scratch
    tree; they are megabytes of progress bars and belong nowhere near a repo.
    """
    out = [
        "# Editor-side probe evidence",
        "",
        "Produced by `tools/animation_bakeoff/export_bakeoff.ps1`, which loads each",
        "scene in the headless MegaDot 4.5.1 editor and walks it. Live capture was",
        "NOT available for this run (the game was in use), so this is the strongest",
        "runtime evidence the lane has -- it proves the scene loads, instantiates,",
        "and carries the animations, states, and rig nodes claimed for it. It does",
        "NOT prove anything about how the motion looks.",
        "",
    ]
    for key in approaches.APPROACH_KEYS:
        log = exports / f"{key}-probe.log"
        out.append(f"## {key}")
        out.append("")
        out.append("```")
        if log.exists():
            for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
                if PROBE_PREFIX in raw:
                    out.append(raw[raw.index(PROBE_PREFIX) :].strip())
        else:
            out.append("(no probe log)")
        out.append("```")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", required=True, type=Path)
    parser.add_argument("--exports", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    data = collect(args.projects, args.exports)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "probe-evidence.md").write_text(
        render_evidence(args.exports), encoding="utf-8", newline="\n"
    )
    (args.out / "bakeoff-results.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    (args.out / "bakeoff-matrix.md").write_text(
        render_matrix(data), encoding="utf-8", newline="\n"
    )
    print(render_matrix(data))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
