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
    # 4'2" against 5'6"-5'10": 0.71-0.76 of an adult, hat to boot / to the feather,
    # measured standing (clips.STAND): the battle stance's crouch is pose, not scale.
    assert 0.68 <= m["hat_to_boot_px"] / BASE_ADULT_PX <= 0.78
    assert 0.68 <= m["full_px"] / BASE_ADULT_PX <= 0.78
    assert "stand" in next(j for j in build.JOBS if j["ppu"] == build.COMBAT_PPU)["stills"].split(",")
    # the battle stance is lower than standing, and wider
    a = frames["stance_a"]
    assert a["hat_to_boot_px"] < m["hat_to_boot_px"] and a["width_px"] > m["width_px"]


def _op(pose, kind, bone):
    return next(op for op in pose["ops"] if op[0] == kind and op[1] == bone)


def test_stance_a_is_wide_low_and_leans_toward_the_enemy():
    # [USER], 2026-10-13: "Agreed on the Silhouette change" -- a wider, lower
    # stance leaning toward the enemy (screen right), a head-sized bomb held out
    # in front; the chest stays turned a little off-centre toward the viewer.
    idle, stand = clips.idle_pose(0.0), clips.STAND
    assert _op(idle, "movew", "足ＩＫ.L")[2][0] > _op(stand, "movew", "足ＩＫ.L")[2][0]
    assert _op(idle, "movew", "足ＩＫ.R")[2][0] < _op(stand, "movew", "足ＩＫ.R")[2][0]
    assert _op(idle, "move", "センター")[2][2] < _op(stand, "move", "センター")[2][2]
    lean = [op for op in idle["ops"] if op[:3] == ("rotw", "上半身", clips.Y)][0][3]
    assert lean >= 10, "leans toward the enemy (+X)"
    twist = [op for op in idle["ops"] if op[:3] == ("rotw", "上半身", clips.Z)][0][3]
    assert twist < 0 and idle["yaw"] == clips.YAW, "chest still off-centre toward the viewer"
    assert idle["held"] == 1.0 and idle["big"] == 0.0
    near = next(op for op in idle["ops"] if op[:2] == ("hand", "R"))
    assert near[2] == clips.CH and near[3][0] > 0, "the bomb hand reaches toward the enemy"


def test_the_normal_bomb_is_60_percent_of_her_head_and_jumpy_dumptys_is_head_sized():
    # [USER], 2026-10-13: "Actually - the new attack is probably too big. ...
    # It's noticeably smaller than her head. I think the increased size would
    # be fitting for her Jumpty Dumpty skill usage." In the owner's Genshin
    # reference her normal-attack bomb is about 60% of her head's width.
    assert 0.20 <= clips.HEAD_W <= 0.24, "hair and face across the screen, measured on the model"
    assert abs(2 * clips.BOMB_R / clips.HEAD_W - 0.6) < 0.01
    assert clips.JUMPY_R == 0.115 and clips.JUMPY_R > 1.6 * clips.BOMB_R
    render = (ROOT / "tools" / "klee_render" / "render.py").read_text(encoding="utf-8")
    # the held, thrown, dropped and cradled bombs are all the normal one
    assert render.count("make_jumpy_dumpty(C.BOMB_R,") == 3
    assert render.count("make_jumpy_dumpty(C.JUMPY_R,") == 2
    # and the shipped manifest's bomb sprites carry those sizes: the attack's
    # about 60% of the head at render, Jumpy Dumpty's about the head's
    ppu = build.COMBAT_PPU
    sheets = rig.load_frames()["sheets"]
    small = sheets["attack"]["thrown"]["size"][0] / ppu
    large = sheets["jumpy"]["thrown"]["size"][0] / ppu
    assert 2 * clips.BOMB_R * 0.9 <= small <= 2 * clips.BOMB_R * 1.3, small
    assert 2 * clips.JUMPY_R * 0.9 <= large <= 2 * clips.JUMPY_R * 1.3, large


def test_jumpy_dumpty_heaves_the_big_bomb_two_handed_and_ends_in_idle():
    jd = clips.CLIPS["jumpy"]
    assert 1.0 <= jd["length"] <= 1.4 and not jd["loop"], "a heavier toss than the 1.0 s attack"
    first, last = jd["keys"][0][1], jd["keys"][-1][1]
    assert first == clips.idle_pose(0.5) and last == clips.idle_pose(0.5)
    poses = [k[1] for k in jd["keys"]]
    held_big = [p for p in poses if p["big"] == 1.0]
    assert held_big and all(p["held"] == 0.0 for p in held_big), "the small bomb is put away"
    for p in held_big:          # both hands on it, either side
        near = next(op for op in p["ops"] if op[:2] == ("hand", "R"))[3]
        far = next(op for op in p["ops"] if op[:2] == ("hand", "L"))[3]
        assert far[0] - near[0] > 2 * clips.JUMPY_R
    flying = [p["big_thrown"] for p in poses if p["big_thrown"] is not None]
    assert len(flying) >= 2 and flying[-1][0] > flying[0][0], "thrown toward the enemy"
    assert all(p["thrown"] is None for p in poses), "the small bomb is not thrown"
    assert "jumpy" in pack.COMBAT and pack.THROWN_FILES["jumpy"] == "klee_bomb_big.png"
    assert "jumpy" in next(j for j in build.JOBS if j["ppu"] == build.COMBAT_PPU)["clips"].split(",")


def test_every_combat_clip_that_leaves_idle_keeps_her_feet_planted():
    # Feet are IK targets; if a key moved them, the blend out of idle would slide them.
    feet = [("movew", "足ＩＫ.L"), ("movew", "足ＩＫ.R")]
    a = clips.idle_pose(0.5)
    for name in ("idle", "idle_low", "attack", "hurt", "cast", "setoff", "jumpy"):
        clip = clips.CLIPS[name]
        for _t, pose, _e in clip["keys"]:
            for kind, bone in feet:
                assert _op(pose, kind, bone)[2] == _op(a, kind, bone)[2], (name, _t, bone)
        if name not in ("idle", "idle_low"):
            assert clip["keys"][0][1] == a and clip["keys"][-1][1]["ops"] == a["ops"], name


def test_style_is_h1_plus_h3_lite():
    # [USER], 2026-10-13: "Let's do H1 + H3 lite."
    # the shader half is the shared toon.py's STYLE (one STYLE for every kit)
    render = (ROOT / "tools" / "char_render" / "toon.py").read_text(encoding="utf-8")
    assert '"shadow": (0.52, 0.37, 0.40)' in render and '"mid_at": 0.30, "light_at": 0.52' in render
    assert '"light": (0.94, 0.92, 0.91)' in render
    post = _load("post")
    assert post.H3_KNEE == 20.0 and abs(post.H3_SQUEEZE - 0.808) < 1e-9
    import numpy as np
    rgb = np.array([[[0.86, 0.13, 0.08], [0.5, 0.5, 0.5]]], np.float32)
    lab0, lab1 = post.to_lab(rgb), post.to_lab(post.h3_lite(rgb))
    c0, c1 = np.hypot(lab0[..., 1], lab0[..., 2]), np.hypot(lab1[..., 1], lab1[..., 2])
    assert abs(c1[0, 0] - (20 + (c0[0, 0] - 20) * post.H3_SQUEEZE)) < 0.5   # chroma squeezed
    assert abs(lab1[0, 0, 0] - lab0[0, 0, 0]) < 0.5                          # L* kept
    assert abs(c1[0, 1] - c0[0, 1]) < 0.5                                     # a grey untouched


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


def test_set_off_is_a_short_cheer_that_lands_back_in_stance_a():
    # Set Off plays a clip of the model (owner, 2026-10-13: "let's pivot to
    # animations based on the new model instead" of the old splash art):
    # 0.8-0.9 s, eyes squeezed happy at the peak, ending on the idle pose so
    # the return to idle blends.
    so = clips.CLIPS["setoff"]
    assert 0.8 <= so["length"] <= 0.9 and not so["loop"]
    first, last = so["keys"][0][1], so["keys"][-1][1]
    assert first == clips.idle_pose(0.5) and last == clips.idle_pose(0.5)
    peak = max(so["keys"], key=lambda k: k[1].get("root", (0, 0, 0))[2])[1]
    assert peak["root"][2] > 0.04, "no hop"
    assert all(peak["morphs"].get(m) == 1.0 for m in clips.HAPPY_EYES)
    assert "setoff" in pack.COMBAT and rig.load_frames()["sheets"]["setoff"]["count"] == 17


def test_the_roster_tile_is_packed_from_the_model_at_its_size():
    # The character-select tile is a face close-up rendered from the model and
    # downsampled once; pack.py owns it and its locked twin (one producer).
    assert pack.PORTRAIT_SIZE == (132, 195)
    assert 0 < pack.PORTRAIT_HAT_AT < pack.PORTRAIT_NECK_AT < 0.5   # the face in the upper half
    assert "portrait" in clips.STILLS
    job = next(j for j in build.JOBS if "portrait" in j["stills"].split(","))
    assert job["ppu"] / build.COMBAT_PPU * 330 > 4 * 195, "not rendered well above the tile's size"
    assert rig.load_frames()["portrait"]["size"] == [132, 195]
    plan = (ROOT / "art" / "plan.tsv").read_text(encoding="utf-8")
    assert not any(l.split("\t")[1:2] == ["ImageGen/images/ui/select_portrait.png"]
                   for l in plan.splitlines() if not l.startswith("#"))
