"""The Bake-Kurage's frame sheet (tools/kurage_render) and its scene
(tools/kokomi_rig/kurage.py), art polish 2026-10-21.

No Blender and no art: the clips are numbers, and the scene is text from the
committed manifest tools/kurage_render/kurage_frames.json.

  * the clips run forward, the idle loop closes, the frame counts are small;
  * the shipped scene is the generator's, from the real manifest;
  * it keeps the hand-written scene's contract: %Visuals, Visuals/Rig at
    (0, -80), Visuals/Rig/Body, the 120x160 Bounds and the four states;
  * no animation keys Rig:scale or Body:self_modulate (KokomiPlanFx.Pulse
    tweens them) and each state steps its own frames;
  * the sheet has one producer and is no bigger than the kits' sheets.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

from tools import art_lint  # noqa: E402
from tools.kokomi_rig import kurage  # noqa: E402


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = _load(ROOT / "tools" / "kurage_render" / "clips.py", "kurage_clips_t")
MANIFEST = json.loads(kurage.FRAMES.read_text(encoding="utf-8"))


def _anim(text: str, name: str) -> str:
    return text.split(f'[sub_resource type="Animation" id="Animation_{name}"]', 1)[1].split("\n[", 1)[0]


def test_the_clips_run_forward_and_the_idle_closes():
    assert set(C.CLIPS) == set(kurage.STATES)
    for name, clip in C.CLIPS.items():
        ts = [k[0] for k in clip["keys"]]
        assert ts == sorted(ts) and ts[0] == 0.0 and ts[-1] <= clip["length"], name
        assert all(set(k[1]) == set(C.REST) for k in clip["keys"]), name
        assert clip["keys"][0][1] == C.REST, f"{name} starts at rest"
    idle = C.CLIPS["idle"]
    assert idle["loop"] and idle["length"] == C.LOOP
    assert C.at(idle, 0.0) == C.at(idle, idle["length"])
    assert abs(C.pulse(0.0) - C.pulse(C.LOOP)) < 1e-9
    for s in (0.0, 0.5, 1.0):
        assert abs(C.wave(0.0, s, 1.3) - C.wave(C.LOOP, s, 1.3)) < 1e-9
    # the attack squashes before it stretches; the death deflates
    atk = [C.at(C.ATTACK, t) for t in (0.12, 0.22)]
    assert atk[0]["sx"] > 1 > atk[1]["sx"] and atk[1]["sz"] > 1
    assert C.at(C.DEATH, 1.0)["sz"] < 0.6 and C.at(C.DEATH, 1.0)["droop"] == 1.0


def test_the_manifest_is_the_clips_and_the_sheet_is_small():
    assert [n for n in MANIFEST["clips"]] == list(C.CLIPS)
    n = 0
    for name, rec in MANIFEST["clips"].items():
        assert rec["first"] == n and rec["times"] == C.times(C.CLIPS[name]), name
        n += rec["count"]
    assert n == MANIFEST["count"] == len(MANIFEST["frames"]) == 69
    assert MANIFEST["scale"] == 0.5 and MANIFEST["texture_import"] == "vram_compressed"
    for page in MANIFEST["pages"]:
        assert max(page["size"]) <= 2048, "no larger than the kits' sheets"
    # on screen it is the old sprite's size: about 64 wide at the bell, 128 tall
    cw, ch = MANIFEST["cell"]
    assert ch * MANIFEST["scale"] < 150


def test_the_shipped_scene_is_the_generators():
    text = kurage.render_scene()
    assert kurage.SCENE.read_text(encoding="utf-8") == text
    assert kurage.render_scene() == text
    assert 'path="res://kokomi/model/frames/kokomi_kurage.png"' in text


def test_the_scene_keeps_the_pets_contract():
    text = kurage.SCENE.read_text(encoding="utf-8")
    assert '[node name="Visuals" type="Node2D" parent="."]\nunique_name_in_owner = true' in text
    assert '[node name="Rig" type="Node2D" parent="Visuals"]\nposition = Vector2(0, -80)' in text
    assert '[node name="Body" type="Sprite2D" parent="Visuals/Rig"]' in text
    for side, v in (("left", "-60.0"), ("top", "-160.0"), ("right", "60.0"), ("bottom", "0.0")):
        assert f"offset_{side} = {v}" in text
    for st in kurage.STATES:
        assert f'animation = &"{st}"' in text
    # KokomiPlanFx.Pulse tweens these two; no animation may fight it
    assert ":scale" not in text and ":self_modulate" not in text
    fx = (ROOT / "klee-mod" / "KleeCode" / "Vfx" / "Prototype" / "KokomiPlanFx.cs").read_text(encoding="utf-8")
    assert '"Visuals/Rig"' in fx and '"Body"' in fx


def test_each_state_steps_its_own_frames():
    text = kurage.SCENE.read_text(encoding="utf-8")
    for name, rec in MANIFEST["clips"].items():
        block = _anim(text, name)
        ids = re.findall(r'SubResource\("Atlas_kurage_(\d+)"\)', block)
        assert [int(i) for i in ids] == list(range(rec["first"], rec["first"] + rec["count"])), name
        assert 'NodePath("Visuals/Rig/Body:texture")' in block


def test_the_sheet_has_one_producer_and_ships_compressed():
    path = "ImageGen/images/kokomi/model/frames/kokomi_kurage.png"
    assert art_lint.GENERATOR_OWNED[path] == "kurage_render/pack.py"
    assert "kokomi_kurage.png" in (ROOT / "tools" / "kurage_render" / "pack.py").read_text(encoding="utf-8")
    ps = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8-sig")
    block = ps.split("$kokomiFrames = Join-Path $src 'kokomi\\model\\frames'", 1)[1].split("\n}\n", 1)[0]
    assert "-Filter *.png" in block and "Write-TextureImport" in block
    # the docket icon keeps its own producer
    assert art_lint.GENERATOR_OWNED["ImageGen/images/kokomi/summon/bake_kurage.png"] == "cut_kurage_summon.py"
