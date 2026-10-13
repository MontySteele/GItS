"""The kit-model renderer's config (tools/char_render/chars.py): the parts that
need no Blender and no model.

The official model packs never enter the repo, so nothing here renders. What
can be held: every kit has a stance in the shared pose language, the scale
follows the law (canon height over an adult, docs/current/LAW.md), and the
overlay shells that broke Klee's protect mask are recognised.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("char_render_chars", ROOT / "tools" / "char_render" / "chars.py")
chars = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chars)

OPS = {"rot", "move", "rotw", "aimw", "movew", "hand", "curl"}


def test_every_kit_has_a_stance_in_the_pose_language():
    assert set(chars.CHARS) == {"furina", "kokomi", "varka"}
    for name, cfg in chars.CHARS.items():
        st = cfg["stance"]
        assert {"yaw", "morphs", "ops", "prop"} <= set(st), name
        assert {op[0] for op in st["ops"]} <= OPS, name
        assert (st["prop"] is None) == (cfg["prop"] is None), name
        assert cfg["pmx"].startswith(f"{name}/unpacked/"), name


def test_scale_is_canon_height_over_an_adult():
    # Klee's ruled 4'2" lands on the ruled ~170 px (visual paper, pick 2)
    assert 168 <= chars.body_px(50.0) <= 176
    for name, cfg in chars.CHARS.items():
        px = chars.body_px(cfg["height_in"])
        assert 200 <= px <= 270, name
    # the ppu is solved per model, never shared: packs differ in scale
    assert chars.target_ppu("kokomi", 1.626) != chars.target_ppu("furina", 1.722)


def test_overlay_shells_are_hidden_and_face_parts_unlined():
    assert chars.is_overlay("髮+") and chars.is_overlay("裙摆+")
    assert not chars.is_overlay("髮")
    assert chars.NO_LINE_MATS <= chars.FACE_MATS
