"""A throwaway MegaDot project for probing and rendering Klee's scenes.

Nothing here touches the install, the pck build or a running game: the
project is a scratch directory holding the generated scenes, the frame PNGs
they draw (copied from `<art-root>`), and the two GDScript drivers in
tools/klee_rig/godot/. The editor is tools/build_pck.ps1's
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


def make_project(work: Path, art_root: Path, scene_text: str | None = None) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    (work / "project.godot").write_text(
        'config_version=5\n\n[application]\n\nconfig/name="KleeRigScratch"\n\n'
        "[display]\n\nwindow/size/viewport_width=320\nwindow/size/viewport_height=320\n",
        encoding="utf-8", newline="\n")
    model = work / "klee" / "model"
    # the model's frame sheets, the thrown bomb and the shadow, and the
    # merchant scene that also draws a sheet
    frames_src = art_root / "ImageGen" / "images" / "model" / "frames"
    (model / "frames").mkdir(parents=True, exist_ok=True)
    manifest = rig.load_frames()
    files = [rec["file"] for rec in manifest["sheets"].values()]
    files += [x["file"] for x in (rig.thrown_of(manifest), rig.shadow_of(manifest)) if x]
    for name in files:
        src, dst = frames_src / name, model / "frames" / name
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)
    (model / "merchant_character.tscn").write_text(rig.MERCHANT_SCENE.read_text(encoding="utf-8"),
                                                   encoding="utf-8", newline="\n")
    text = scene_text if scene_text is not None else rig.SCENE.read_text(encoding="utf-8")
    (model / "combat.tscn").write_text(text, encoding="utf-8", newline="\n")
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
