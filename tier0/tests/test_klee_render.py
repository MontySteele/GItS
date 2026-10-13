"""Klee's model renders (tools/klee_render): the parts that need no Blender,
no model and no art.

The model itself never enters the repo, so nothing here can render. What can
be held: the pose library is well-formed (keys in time order, loops that
close), the packer's file list and the combat sheets agree, and the committed
manifest was rendered at the scale build.py names -- the ruled 0.72 of an
adult (review/active/klee-visual-paper-2026-10-12.md, pick 2).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from tools.klee_rig import rig

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    """By file path under a private name: `build`, `pack` and `clips` are
    script names, and a sys.path entry would shadow any other module so named."""
    spec = importlib.util.spec_from_file_location(f"klee_render_{name}",
                                                  ROOT / "tools" / "klee_render" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


build, clips, pack = _load("build"), _load("clips"), _load("pack")

BASE_ADULT_PX = 235   # the census's base adult bodies at 1080p (paper, pick 2)


def test_every_clip_runs_forward_and_every_loop_closes():
    for name, clip in clips.CLIPS.items():
        times = [k[0] for k in clip["keys"]]
        assert times == sorted(times) and times[0] == 0.0, name
        assert times[-1] <= clip["length"] + 1e-9, name
        for _t, pose, ease in clip["keys"]:
            assert ease in ("io", "out", "in", "lin"), name
            assert {"yaw", "morphs", "ops", "held", "thrown"} <= set(pose), name
        if clip["loop"]:
            assert times[-1] == clip["length"], name
            assert clip["keys"][0][1] == clip["keys"][-1][1], f"{name}: loop does not close"


def test_the_packer_names_every_sheet_the_scene_draws():
    assert set(pack.SHEET_FILES) == {*pack.COMBAT, "merchant"}
    assert set(rig.load_spec()["model"]["sheets"]) == set(pack.COMBAT)
    frames = rig.load_frames()
    for clip, rec in frames["sheets"].items():
        assert rec["file"] == pack.SHEET_FILES[clip]


def test_the_manifest_was_rendered_at_the_ruled_scale():
    frames = rig.load_frames()
    for clip in pack.COMBAT:
        assert frames["sheets"][clip]["ppu"] == build.COMBAT_PPU, clip
    assert frames["combat_scale"] == pack.COMBAT_SCALE
    m = frames["measure"]
    # 4'2" against 5'6"-5'10": 0.71-0.76 of an adult, hat to boot / to the feather.
    assert 0.68 <= m["hat_to_boot_px"] / BASE_ADULT_PX <= 0.78
    assert 0.68 <= m["full_px"] / BASE_ADULT_PX <= 0.78


def test_split_thrown_lifts_the_free_bomb_out_of_the_cells_once():
    """The thrown bomb is flown by the game (KleeMod.Vfx.ThrownProjectile):
    a detached run right of the figure is erased from every cell and the
    first one becomes the sprite, with where it sat. A second pass is a no-op."""
    from PIL import Image

    cw, ch = 40, 20
    sheet = Image.new("RGBA", (cw * 2, ch * 2), (0, 0, 0, 0))
    red = Image.new("RGBA", (1, 1), (255, 0, 0, 255))
    for i in range(4):
        x0, y0 = (i % 2) * cw, (i // 2) * ch
        for x in range(2, 14):                      # the figure
            for y in range(2, 18):
                sheet.paste(red, (x0 + x, y0 + y))
        if i in (1, 2):                             # the bomb in flight
            bx = 20 + 8 * (i - 1)
            for x in range(bx, bx + 4):
                for y in range(5, 9):
                    sheet.paste(red, (x0 + x, y0 + y))
    rec = {"cell": [cw, ch], "hframes": 2, "count": 4, "times": [0.0, 0.05, 0.1, 0.15]}
    out, bomb, thrown = pack.split_thrown(sheet, rec)
    assert bomb.size == (4, 4)
    assert thrown == {"frame": 1, "time": 0.05, "file": pack.BOMB_FILE, "size": [4, 4], "at": [22.0, 7.0]}
    for i in range(4):
        x0, y0 = (i % 2) * cw, (i // 2) * ch
        cell = out.crop((x0, y0, x0 + cw, y0 + ch)).getchannel("A")
        assert pack.column_runs(cell) == [(2, 14)], i
    assert pack.split_thrown(out, rec)[1:] == (None, None)


def test_the_scene_throws_from_where_the_bomb_left_her_hand():
    frames = rig.load_frames()
    thrown = frames["sheets"][pack.THROWN_CLIP]["thrown"]
    assert thrown["file"] == pack.BOMB_FILE
    ox, oy = frames["sheets"]["attack"]["origin"]
    sc = frames["combat_scale"]
    node = rig._projectile_node(frames)[0]
    assert 'parent="Visuals/Facing"' in node and "visible = false" in node
    assert f"position = {rig.vec2(((thrown['at'][0] - ox) * sc, (thrown['at'][1] - oy) * sc))}" in node
    assert f"metadata/release = {rig.fnum(thrown['time'])}" in node
