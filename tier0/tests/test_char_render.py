"""The kit-model renderer (tools/char_render): the parts that need no Blender
and no model.

The official model packs never enter the repo, so nothing here renders. What
can be held: every kit has a stance in the shared pose language, the scale
follows the law (canon height over an adult, docs/current/LAW.md), the
overlay shells that broke Klee's protect mask are recognised, Varka's pose
library is well formed (two claymores, feet planted, impacts marked), the
trail layer is deterministic and tintable, and the committed manifest was
packed at his ruled height (review/active/varka-visual-paper-2026-10-13.md).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "tools" / "char_render"


def _load(name: str):
    """By file path under a private name (script names like `pack` would
    shadow other modules on sys.path)."""
    spec = importlib.util.spec_from_file_location(f"char_render_{name}", HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


chars = _load("chars")
vc = _load("varka_clips")
fx = _load("fx")
pack = _load("pack")
build = _load("build")

OPS = {"rot", "move", "rotw", "aimw", "movew", "hand", "curl"}
EASES = {"io", "out", "in", "lin"}


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
    # Varka's ruled 78 in: ~270 px, from his model's measured 2.05 unit rest height
    assert abs(chars.body_px(78.0) - 269.6) < 0.5
    assert abs(build.combat_ppu("varka") * build.REST_HEIGHT["varka"] * chars.COMBAT_SCALE - 269.6) < 0.5


def test_overlay_shells_are_hidden_and_face_parts_unlined():
    assert chars.is_overlay("髮+") and chars.is_overlay("裙摆+")
    assert not chars.is_overlay("髮")
    assert chars.NO_LINE_MATS <= chars.FACE_MATS


# ------------------------------------------------------------------ Varka's clips
def _op(pose, kind, bone):
    return next(op for op in pose["ops"] if op[0] == kind and op[1] == bone)


def test_every_varka_clip_runs_forward_and_every_loop_closes():
    for name, clip in vc.CLIPS.items():
        times = [k[0] for k in clip["keys"]]
        assert times == sorted(times) and times[0] == 0.0, name
        assert times[-1] <= clip["length"] + 1e-9, name
        for _t, pose, ease in clip["keys"]:
            assert ease in EASES, name
            assert {"yaw", "morphs", "ops", "blades", "root"} <= set(pose), name
            assert {op[0] for op in pose["ops"]} <= OPS, name
        if clip["loop"]:
            assert times[-1] == clip["length"], name
            assert clip["keys"][0][1] == clip["keys"][-1][1], f"{name}: loop does not close"


def test_he_carries_a_claymore_in_each_hand():
    # [USER], 2026-10-13: "Varka is a dual wielder, carrying TWO claymores, one in each hand."
    assert set(chars.CHARS["varka"]["blades"]) == {"R", "L"}
    pmx = {b["pmx"] for b in chars.CHARS["varka"]["blades"].values()}
    assert pmx == {"varka/unpacked/武器.pmx", "varka/unpacked/剑.pmx"}
    for b in chars.CHARS["varka"]["blades"].values():
        assert b["tip"] < b["base"] < 0 < b["grip"], "tip along -Y, past the guard, grip on the handle"
    for name, clip in vc.CLIPS.items():
        for _t, pose, _e in clip["keys"]:
            assert set(pose["blades"]) == {"R", "L"}, (name, _t)
            for side, b in pose["blades"].items():
                assert abs(np.linalg.norm(b["dir"]) - 1) < 0.08, (name, _t, side)
    # the leading (far-hand) blade is higher than the trailing one in stance A
    idle = vc.idle_pose(0.0)
    assert idle["blades"]["L"]["at"][2] > idle["blades"]["R"]["at"][2]
    assert idle["blades"]["L"]["dir"][0] > 0 > idle["blades"]["R"]["dir"][0], "lead forward, rear trailing"


def test_every_combat_clip_that_leaves_idle_keeps_his_feet_planted():
    feet = [("movew", "足ＩＫ.L"), ("movew", "足ＩＫ.R")]
    a = vc.idle_pose(0.5)
    for name in ("idle", "idle_low", "attack", "cast", "hurt"):
        for _t, pose, _e in vc.CLIPS[name]["keys"]:
            for kind, bone in feet:
                assert _op(pose, kind, bone)[2] == _op(a, kind, bone)[2], (name, _t, bone)
    for name in vc.FROM_IDLE:
        clip = vc.CLIPS[name]
        assert clip["keys"][0][1] == a and clip["keys"][-1][1] == a, name
    # the leap goes straight up: he lands where he stood
    assert all(k[1]["root"][0] == 0 and k[1]["root"][1] == 0 for k in vc.CLIPS["ascension"]["keys"])
    assert max(k[1]["root"][2] for k in vc.CLIPS["ascension"]["keys"]) > 0.4


def test_the_impacts_are_marked_and_the_trails_cover_them():
    atk = vc.CLIPS["attack"]
    assert 0.8 <= atk["length"] <= 1.0
    imp = atk["events"]["impact"]
    assert len(imp) == 2 and imp[0] < imp[1] and atk["events"]["main"] == imp[1], "the main impact is the second"
    asc = vc.CLIPS["ascension"]
    assert len(asc["events"]["impact"]) == 1 and asc["events"]["main"] == asc["events"]["impact"][0]
    for clip in (atk, asc):
        for t in clip["events"]["impact"]:
            assert any(w["from"] <= t <= w["to"] for w in clip["trails"]), t
            assert any(abs(b["t"] - t) < 1e-9 for b in clip["bursts"]), t
        for w in clip["trails"]:
            assert w["blade"] in ("L", "R") and 0 <= w["from"] < w["to"] <= clip["length"]
    assert {w["blade"] for w in atk["trails"]} == {"L", "R"}, "one arc per blade"
    assert {w["blade"] for w in asc["trails"]} == {"L", "R"}, "a twin arc"


def test_stance_b_plants_both_blades_with_his_hands_on_them():
    b = vc.MERCHANT["keys"][0][1]["blades"]
    for side in ("L", "R"):
        assert b[side]["anchor"] == "ground" and b[side]["hand"] and b[side]["dir"][2] < -0.95
    assert b["L"]["at"][0] > 0 > b["R"]["at"][0], "one either side"
    assert all(not bl["hand"] for bl in vc.REST["blades"].values()), "laid down at the rest site"


# ------------------------------------------------------------------ the trail layer
def _meta(ppu=263.4):
    """A synthetic clip: one blade sweeping a quarter circle, a burst at the end."""
    import math
    track = []
    for i in range(41):
        t = i / 80
        a = math.radians(-80 + 90 * i / 40)
        cx, cy = 200, 300
        track.append({"t": round(t, 6), "L": [[cx + 60 * math.cos(a), cy + 60 * math.sin(a)],
                                              [cx + 260 * math.cos(a), cy + 260 * math.sin(a)]], "R": None})
    return {"canvas": [500, 500], "origin_px": [200, 480], "ppu": ppu, "fps": 20,
            "times": [i / 20 for i in range(11)], "trails": [{"blade": "L", "from": 0.1, "to": 0.4}],
            "bursts": [{"t": 0.4, "blade": "L", "kind": "slash", "scale": 1.0}], "blades": track}


def test_the_trail_layer_is_neutral_deterministic_and_spans_its_window():
    m = _meta()
    frames, first, pad = fx.clip_fx(m)
    again, first2, _ = fx.clip_fx(m)
    assert first == first2 == 3 and len(frames) == len(again)
    assert all(np.array_equal(np.asarray(a), np.asarray(b)) for a, b in zip(frames, again))
    for im in frames:
        arr = np.asarray(im)
        assert im.size == (500 + 2 * pad, 500 + 2 * pad)
        on = arr[..., 3] > 0
        assert on.any()
        assert (arr[..., 0] == arr[..., 1]).all() and (arr[..., 1] == arr[..., 2]).all(), "colourless"
    assert max(np.asarray(im)[..., 0].max() for im in frames) >= 240, "a white-hot core"
    assert fx.clip_fx({**m, "trails": [], "bursts": []})[0] == []


def test_tint_keeps_alpha_and_the_white_core():
    im = Image.fromarray(np.array([[[255, 255, 255, 200], [128, 128, 128, 90]]], np.uint8), "RGBA")
    for hexc in fx.ELEMENTS.values():
        c = fx.hex_rgb(hexc)
        out = np.asarray(fx.tint(im, c))
        assert out[0, 0, 3] == 200 and out[0, 1, 3] == 90
        assert (out[0, 0, :3] == 255).all(), "the core stays white"
        assert np.allclose(out[0, 1, :3] / 255, c, atol=0.01), "the glow takes the element"
    assert set(fx.ELEMENTS) == {"anemo", "pyro", "hydro", "electro", "cryo"}


# ------------------------------------------------------------------ the packer
def test_layout_pages_a_clip_too_big_for_one_sheet():
    assert pack.layout(20, 300, 330) == (5, 4, 1)          # Klee-sized: one near-square sheet
    cols, rpp, pages = pack.layout(19, 1200, 1100)
    assert cols == 3 and rpp == 3 and pages == 3
    assert cols * 1200 <= pack.MAX_SHEET and rpp * 1100 <= pack.MAX_SHEET
    assert pack.page_name("varka_attack.png", 0) == "varka_attack.png"
    assert pack.page_name("varka_attack.png", 2) == "varka_attack_p3.png"


def test_ground_clip_cuts_below_the_feet_anchor_only():
    im = Image.new("RGBA", (10, 40), (255, 0, 0, 255))
    out = np.asarray(pack.ground_clip(im, 20.0, 1.0))
    assert (out[:26, :, 3] == 255).all() and (out[26:, :, 3] == 0).all()


def test_the_packer_names_every_sheet_it_writes():
    files = pack.SHEET_FILES["varka"]
    assert set(files) == {*pack.COMBAT, "merchant"}
    assert set(pack.COMBAT) | {"merchant"} == set(vc.CLIPS)
    assert set(pack.FX_FILES["varka"]) == {"attack", "ascension"}
    job = build.jobs("varka")
    assert set(job[0]["clips"].split(",")) == set(pack.COMBAT)
    assert {"stance_a", "stand"} <= set(job[0]["stills"].split(","))


def test_the_manifest_was_packed_at_his_ruled_height():
    path = pack.manifest_path("varka")
    m = json.loads(path.read_text(encoding="utf-8"))
    for clip in pack.COMBAT:
        rec = m["sheets"][clip]
        assert abs(rec["ppu"] - build.combat_ppu("varka")) < 0.01, clip
        assert sum(p["count"] for p in rec["pages"]) == rec["count"] == len(rec["times"])
        for p in rec["pages"]:
            assert p["hframes"] * rec["cell"][0] <= pack.MAX_SHEET and p["vframes"] * rec["cell"][1] <= pack.MAX_SHEET
    target = chars.body_px(chars.CHARS["varka"]["height_in"])
    assert abs(m["measure"]["hat_to_boot_px"] / target - 1) < 0.06, m["measure"]
    assert m["stance_a"]["hat_to_boot_px"] < m["measure"]["hat_to_boot_px"], "the battle stance crouches"
    assert m["sheets"]["attack"]["main_frame"] == m["sheets"]["attack"]["impact_frames"][1]
    for clip in ("attack", "ascension"):
        f = m["fx"][clip]
        assert 0 <= f["first_frame"] and f["first_frame"] + f["count"] <= m["sheets"][clip]["count"]
    assert m["portrait"]["size"] == [132, 195]
