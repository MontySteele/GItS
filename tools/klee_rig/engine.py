"""A throwaway MegaDot project for probing and rendering the rig.

Nothing here touches the install, the pck build or a running game: the
project is a scratch directory holding the generated scene, a layered
REFERENCE scene (the old five centred Sprite2Ds, rebuilt from the cutter's
manifest), the five combat PNGs copied from `<art-root>`, and the two GDScript
drivers in tools/klee_rig/godot/. The editor is tools/build_pck.ps1's
(override with GITS_MEGADOT).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import rig
from .cells import LAYER_DIR

HERE = Path(__file__).resolve().parent


def megadot() -> Path:
    env = os.environ.get("GITS_MEGADOT")
    if env:
        return Path(env)
    text = (rig.ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")
    m = re.search(r"\[string\]\$MegaDot = '([^']+)'", text)
    if not m:
        raise SystemExit("cannot find the MegaDot path in tools/build_pck.ps1; set GITS_MEGADOT")
    return Path(m.group(1))


def reference_scene(cells: dict) -> str:
    """The old layered composite: one centred Sprite2D per layer at the
    manifest offset, under the same Rig transform and contract nodes."""
    ids = rig.EXT_IDS
    out = ['[gd_scene load_steps=8 format=3]', ""]
    for name, rec in cells["layers"].items():
        tex = next(l["texture"] for l in rig.load_spec()["layers"] if l["name"] == name)
        out.append(f'[ext_resource type="Texture2D" path="{rig.TEX_DIR}/{tex}" id="{ids[name]}"]')
    out += ["", '[sub_resource type="Animation" id="Animation_reset"]', "length = 0.001", "",
            '[sub_resource type="AnimationLibrary" id="Lib"]',
            '_data = {\n&"RESET": SubResource("Animation_reset")\n}', "",
            '[node name="KleeCombat" type="Node2D"]', "",
            '[node name="Visuals" type="Node2D" parent="."]', "",
            '[node name="Facing" type="Node2D" parent="Visuals"]', "",
            '[node name="Rig" type="Node2D" parent="Visuals/Facing"]', "position = Vector2(0, -140)", ""]
    for name, rec in cells["layers"].items():
        w, h = rec["texture"]
        x, y = rec["topleft"][0] + w / 2, rec["topleft"][1] + h / 2
        out += [f'[node name="{name}" type="Sprite2D" parent="Visuals/Facing/Rig"]',
                f"position = {rig.vec2((x, y))}", f'texture = ExtResource("{ids[name]}")', ""]
    out += ['[node name="AnimationPlayer" type="AnimationPlayer" parent="."]',
            'libraries = {\n&"": SubResource("Lib")\n}', ""]
    return "\n".join(out)


def make_project(work: Path, art_root: Path, scene_text: str | None = None) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    (work / "project.godot").write_text(
        'config_version=5\n\n[application]\n\nconfig/name="KleeRigScratch"\n\n'
        "[display]\n\nwindow/size/viewport_width=320\nwindow/size/viewport_height=320\n",
        encoding="utf-8", newline="\n")
    model = work / "klee" / "model"
    (model / "layers").mkdir(parents=True, exist_ok=True)
    for layer in rig.load_spec()["layers"]:
        src = art_root / LAYER_DIR / layer["texture"]
        dst = model / "layers" / layer["texture"]
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)
    # the model's frame sheets and the merchant scene that also draws one
    frames_src = art_root / "ImageGen" / "images" / "model" / "frames"
    (model / "frames").mkdir(parents=True, exist_ok=True)
    for rec in rig.load_frames()["sheets"].values():
        src, dst = frames_src / rec["file"], model / "frames" / rec["file"]
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)
    (model / "merchant_character.tscn").write_text(rig.MERCHANT_SCENE.read_text(encoding="utf-8"),
                                                   encoding="utf-8", newline="\n")
    text = scene_text if scene_text is not None else rig.SCENE.read_text(encoding="utf-8")
    (model / "combat.tscn").write_text(text, encoding="utf-8", newline="\n")
    (model / "reference.tscn").write_text(reference_scene(rig.load_cells()), encoding="utf-8", newline="\n")
    for gd in ("probe.gd", "render.gd"):
        shutil.copyfile(HERE / "godot" / gd, work / gd)
    return work


def run(work: Path, args: list[str], timeout: int = 600) -> tuple[int, str]:
    proc = subprocess.run([str(megadot()), "--path", str(work), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    return proc.returncode, proc.stdout + proc.stderr


def import_project(work: Path) -> None:
    code, log = run(work, ["--headless", "--import"])
    if code != 0:
        raise SystemExit(f"MegaDot import failed ({code}):\n{log[-3000:]}")


def render(work: Path, passes: list[dict]) -> str:
    job = work / "job.json"
    job.write_text(json.dumps({"passes": passes}), encoding="utf-8")
    code, log = run(work, ["--script", "res://render.gd", "--", str(job)])
    if code != 0 or "RENDER|done" not in log:
        raise SystemExit(f"MegaDot render failed ({code}):\n{log[-3000:]}")
    return log
