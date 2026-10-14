"""The kit-model renderer (tools/char_render): the parts that need no Blender
and no model.

The official model packs never enter the repo, so nothing here renders. What
can be held: every kit has a stance in the shared pose language, the scale
follows the law (canon height over an adult, docs/current/LAW.md), the
overlay shells that broke Klee's protect mask are recognised, Varka's pose
library is well formed (two claymores, feet planted, impacts marked), the
trail layer is deterministic and tintable, the committed manifest was
packed at his ruled height (82 in), and his hands rest on the pommels in
stance B (review/active/varka-visual-paper-2026-10-13.md).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
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
        assert 200 <= px <= 290, name
    # the ppu is solved per model, never shared: packs differ in scale
    assert chars.target_ppu("kokomi", 1.626) != chars.target_ppu("furina", 1.722)
    # Varka's ruled 82 in ([USER], 2026-10-13: "let's give Varka the height
    # boost and use these proportion"): ~283.4 px, from his model's measured
    # 2.05 unit rest height; the interim ruled_height_in is gone
    assert chars.CHARS["varka"]["height_in"] == 82.0 and "ruled_height_in" not in chars.CHARS["varka"]
    assert abs(chars.body_px(82.0) - 283.4) < 0.1
    assert abs(build.combat_ppu("varka") * build.REST_HEIGHT["varka"] * chars.COMBAT_SCALE - 283.4) < 0.5


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
    # stance A ([USER], 2026-10-13, "less floppy"): a low guard, both blades
    # down and back at his sides, mirrored about his body so they read as one
    # parallel pair, tips off the ground
    for idle in (vc.idle_pose(0.0), vc.low_pose(0.0)):
        lead, rear = idle["blades"]["L"], idle["blades"]["R"]
        for b in (lead, rear):
            assert b["dir"][0] < -0.3 and -0.6 < b["dir"][2] < -0.2, "down and back, tips clear"
        assert np.allclose(lead["dir"], vc.mirror(rear["dir"])), "the pair mirror each other"


def _same_but_turned(p, q):
    """p and q are one picture: equal but for whole turns of the yaw."""
    return (p["yaw"] - q["yaw"]) % 360 == 0 and {**p, "yaw": 0} == {**q, "yaw": 0}


def test_every_combat_clip_that_leaves_idle_keeps_his_feet_planted():
    feet = [("movew", "足ＩＫ.L"), ("movew", "足ＩＫ.R")]
    a = vc.idle_pose(0.5)
    for name in ("idle", "idle_low", "cast", "hurt"):
        for _t, pose, _e in vc.CLIPS[name]["keys"]:
            for kind, bone in feet:
                assert _op(pose, kind, bone)[2] == _op(a, kind, bone)[2], (name, _t, bone)
    for name in vc.FROM_IDLE:
        clip = vc.CLIPS[name]
        assert clip["keys"][0][1] == a and _same_but_turned(clip["keys"][-1][1], a), name
    # the attack's spin turns on the spot: at most a small hop, the feet never
    # further out than the guard's footprint, and planted at the main impact
    reach = max(np.hypot(*_op(a, *f)[2][:2]) for f in feet)
    for _t, pose, _e in vc.CLIPS["attack"]["keys"]:
        assert pose["root"][0] == 0 and pose["root"][1] == 0 and 0 <= pose["root"][2] <= 0.12, _t
        for f in feet:
            assert np.hypot(*_op(pose, *f)[2][:2]) <= reach + 1e-9, (_t, f)
    for t in (vc.CLIPS["attack"]["events"]["main"],):
        pose = next(k[1] for k in vc.CLIPS["attack"]["keys"] if abs(k[0] - t) < 1e-9)
        for f in feet:
            assert np.hypot(*_op(pose, *f)[2][:2]) == pytest.approx(np.hypot(*_op(a, *f)[2][:2])), (t, f)
    # the leap goes straight up, no higher than half his height: he lands where he stood
    asc = vc.CLIPS["ascension"]["keys"]
    assert all(k[1]["root"][0] == 0 and k[1]["root"][1] == 0 for k in asc)
    assert 0.4 < max(k[1]["root"][2] for k in asc) <= 0.5 * build.REST_HEIGHT["varka"]


def _angle(u, v):
    u, v = np.asarray(u, float), np.asarray(v, float)
    return np.degrees(np.arccos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1)))


def _body_dir(pose, side):
    """A blade's direction in his body's frame (the root's yaw taken out)."""
    return vc.rot_z(pose["blades"][side]["dir"], -(pose["yaw"] - vc.YAW))


def test_the_two_blades_move_in_sync():
    # [USER], 2026-10-13: "attack with both claymores in sync at the same time
    # ... rather than just raising them one after the other." Between any two
    # keys of a combat clip both blades turn through the same angle (in the
    # world, and in his body's frame), so neither lags or leads the other.
    for name in ("attack", "cast", "hurt", "idle", "idle_low"):
        keys = vc.CLIPS[name]["keys"]
        for (t0, p0, _), (t1, p1, _) in zip(keys, keys[1:]):
            turn = [_angle(p0["blades"][s]["dir"], p1["blades"][s]["dir"]) for s in ("L", "R")]
            body = [_angle(_body_dir(p0, s), _body_dir(p1, s)) for s in ("L", "R")]
            assert abs(turn[0] - turn[1]) < 15, (name, t0, t1, turn)
            assert abs(body[0] - body[1]) < 15, (name, t0, t1, body)
    # the spin is a rising helix ([USER], round 3): through the turn the blades
    # hold one line in his body's own vertical plane and only climb, from
    # level behind him, over the top, to down in front
    spin = [k[1] for k in vc.CLIPS["attack"]["keys"] if vc.SPIN_T0 - 1e-9 <= k[0] <= vc.SPIN_T1 + 1e-9]
    assert len(spin) >= 15
    pitch = [np.degrees(np.arctan2(_body_dir(p, "L")[2], -_body_dir(p, "L")[0])) % 360 for p in spin]
    pitch = [a - 360 if a > 270 else a for a in pitch]
    assert all(b > a for a, b in zip(pitch, pitch[1:])), pitch
    assert pitch[0] < 0 and pitch[-1] > 180 and any(abs(a - 90) < 15 for a in pitch), "level, over the top, down"
    turns = [k[1]["yaw"] for k in vc.CLIPS["attack"]["keys"]]
    assert max(turns) - min(turns) >= 360, "a full turn"
    # (the ascension drives ONE blade, [USER] round 3, the other held back for
    # balance, so it is not a synced pair and is left out above)


def _tip_height(pose, side):
    """A blade tip's height over the ground, roughly: the chest's rest height
    (lowered by the crouch, raised by the hop) plus the grip offset plus the
    blade along its direction. Enough to see a jump in its speed."""
    b = pose["blades"][side]
    spec = chars.CHARS["varka"]["blades"][side]
    reach = spec["grip"] - spec["tip"]
    drop = -next(op for op in pose["ops"] if op[0] == "move" and op[1] == "センター")[2][2]
    base = 0.0 if b["anchor"] == "ground" else 1.45 - drop + pose["root"][2]
    return base + b["at"][2] + reach * b["dir"][2]


def test_the_attack_is_one_continuous_motion():
    # [USER], round 3: "he half-twirls once, then instantly flips to slam them
    # down ... so it reads as one continuous animation rather than two halves".
    # Through the spin-to-slam join the root's yaw speed and each blade tip's
    # vertical speed change by no more than a fraction of their peak from one
    # half-frame step to the next: no hold at the top, no snap into the slam.
    keys = [k for k in vc.CLIPS["attack"]["keys"] if vc.SPIN_T0 - 1e-9 <= k[0] <= vc.SPIN_T1 + 1e-9]
    ts = [k[0] for k in keys]
    assert all(abs((b - a) - vc.SPIN_STEP) < 1e-6 for a, b in zip(ts, ts[1:])), "evenly keyed"
    yaw = np.array([k[1]["yaw"] for k in keys])
    vy = np.diff(yaw) / vc.SPIN_STEP
    assert (vy >= 0).all() and vy.max() > 600, "one way round, fast"
    assert np.abs(np.diff(vy)).max() <= 0.25 * vy.max(), np.abs(np.diff(vy)).max()
    for side in ("L", "R"):
        tip = np.array([_tip_height(k[1], side) for k in keys])
        vt = np.diff(tip) / vc.SPIN_STEP
        assert np.abs(np.diff(vt)).max() <= 0.35 * np.abs(vt).max(), (side, np.abs(np.diff(vt)).max())
    # the overhead is passed mid-motion, not held: the yaw is still turning there
    top = max(range(len(keys)), key=lambda i: _tip_height(keys[i][1], "L"))
    assert 0 < top < len(keys) - 1 and vy[top - 1] > 0.25 * vy.max()
    # and one ribbon per blade spans the whole of it
    trails = vc.CLIPS["attack"]["trails"]
    assert sorted(w["blade"] for w in trails) == ["L", "R"]
    for w in trails:
        assert w["from"] <= vc.SPIN_T0 + 0.05 and w["to"] >= vc.SPIN_T1


def test_the_ascension_jumps_and_drives_one_blade_into_the_ground():
    # [USER], round 3: "drop the twirl and instead show him jumping up and then
    # driving one blade into the ground, with a mirrored ground particle effect
    # on him and the target enemy"
    clip = vc.CLIPS["ascension"]
    keys = clip["keys"]
    assert all((k[1]["yaw"] - vc.YAW) % 360 == 0 for k in keys), "no twirl"
    hop = max(k[1]["root"][2] for k in keys)
    assert 0.4 < hop <= 0.5 * build.REST_HEIGHT["varka"], "a jump, under half his height"
    t = clip["events"]["main"]
    imp = next(k[1] for k in keys if abs(k[0] - t) < 1e-9)
    assert imp["root"][2] == 0, "landed on the impact"
    d, bal = imp["blades"][vc.DRIVE], imp["blades"]["R" if vc.DRIVE == "L" else "L"]
    assert d["anchor"] == "ground" and d["hand"] and d["dir"][2] < -0.9, "point-first, near vertical"
    assert -0.40 <= _tip_height(imp, vc.DRIVE) <= 0.02, "its point at the ground line (cut below it)"
    assert d["at"][0] > 0.3, "in front of him, toward the enemy"
    assert bal["dir"][0] < -0.5, "the other blade held back for balance"
    # the ground burst is its own clip, placed twice from the impact
    (e,) = clip["effects"]
    assert e["name"] == "ground_burst" and e["mirror"] and set(e["places"]) == {"blade_tip", "target"}
    assert abs(e["t"] - t) < 1e-9 and e["blade"] == vc.DRIVE
    frames, origin = fx.ground_burst()
    again, _ = fx.ground_burst()
    assert len(frames) >= 8 and all(np.array_equal(np.asarray(a), np.asarray(b)) for a, b in zip(frames, again))
    for im in frames:
        arr = np.asarray(im)
        assert (arr[..., 0] == arr[..., 1]).all() and (arr[..., 1] == arr[..., 2]).all(), "colourless"
    first = np.asarray(frames[1])[..., 3]
    ox, oy = round(origin[0]), round(origin[1])
    assert first[oy - 4:oy + 4, ox - 4:ox + 4].max() > 200, "it starts at the ground point"


def test_the_impacts_are_marked_and_the_trails_cover_them():
    atk = vc.CLIPS["attack"]
    assert 0.95 <= atk["length"] <= 1.1, "19 to 22 frames at 20 fps"
    imp = atk["events"]["impact"]
    assert len(imp) == 2 and imp[0] < imp[1] and atk["events"]["main"] == imp[1], "the main impact is the second"
    asc = vc.CLIPS["ascension"]
    assert len(asc["events"]["impact"]) == 1 and asc["events"]["main"] == asc["events"]["impact"][0]
    for clip in (atk, asc):
        for t in clip["events"]["impact"]:
            assert abs(t * clip["fps"] - round(t * clip["fps"])) < 1e-6, (t, "an impact lands on a frame")
            assert any(abs(k[0] - t) < 1e-9 for k in clip["keys"]), (t, "an impact is a key")
        for w in clip["trails"]:
            assert w["blade"] in ("L", "R") and 0 <= w["from"] < w["to"] <= clip["length"]
    for t in imp:
        for side in ("L", "R"):
            assert any(w["from"] <= t <= w["to"] and w["blade"] == side for w in atk["trails"]), (t, side)
        assert any(abs(b["t"] - t) < 1e-9 for b in atk["bursts"]), t
    # both blades strike toward the enemy (right): the light hit as they rise
    # past his side, the main one between chest and knee height
    light, main = (next(k[1] for k in atk["keys"] if abs(k[0] - t) < 1e-9) for t in imp)
    for side in ("L", "R"):
        b = light["blades"][side]
        assert b["dir"][0] > 0.5 and -0.2 < b["dir"][2] < 0.6, (side, b["dir"], "rising past the enemy's side")
        b = main["blades"][side]
        assert b["dir"][0] > 0.5, (side, b["dir"])
        assert -0.65 < b["dir"][2] < 0.15 and -0.5 < b["at"][2] < 0.0, (side, b)
    # the two blades' trails run over the same windows: a twin ribbon
    assert sorted((w["from"], w["to"]) for w in atk["trails"] if w["blade"] == "L") == \
        sorted((w["from"], w["to"]) for w in atk["trails"] if w["blade"] == "R")
    # the slam and the drive come from over his head
    before = [k[1] for k in atk["keys"] if imp[1] - 0.15 <= k[0] < imp[1]]
    assert any(all(p["blades"][s]["dir"][2] > 0.8 for s in ("L", "R")) for p in before), "over the top"
    t = asc["events"]["main"]
    before = [k[1] for k in asc["keys"] if t - 0.2 <= k[0] < t]
    assert any(p["blades"][vc.DRIVE]["dir"][2] > 0.8 for p in before), "the driven blade comes over the top"
    assert any(w["blade"] == vc.DRIVE and w["from"] <= t <= w["to"] for w in asc["trails"])


def test_stance_b_crosses_his_arms_with_both_blades_planted_in_front():
    # [USER], 2026-10-13: "Can we have him cross his arms instead, with his
    # swords infront of him? And let's have the facial expression be more of
    # a slight smile or smirk."
    p = vc.MERCHANT["keys"][0][1]
    assert p.get("arms_crossed")
    b = p["blades"]
    for side in ("L", "R"):
        # planted point-down, standing free (no hand on it), the pommel's top
        # (chars.py) at about his waist, in front of him
        assert b[side]["anchor"] == "ground" and not b[side]["hand"] and b[side]["dir"][2] < -0.95
        assert b[side]["grip"] == chars.CHARS["varka"]["blades"][side]["pommel"][1]
        assert 1.15 <= b[side]["at"][2] <= 1.35, b[side]["at"]
        assert b[side]["at"][1] < -0.3, "in front of him (toward the viewer)"
    assert b["L"]["at"][0] > 0 > b["R"]["at"][0], "side by side"
    # each hand is posed across his chest, to the other side
    hands = {op[1]: op for op in p["ops"] if op[0] == "hand"}
    assert set(hands) == {"L", "R"} and all(op[2] == vc.CH for op in hands.values())
    assert hands["R"][3][0] > 0 > hands["L"][3][0], "each wrist crosses to the other side"
    assert hands["R"][3][1] < hands["L"][3][1], "the near forearm in front"
    for name in ("select", "portrait"):
        assert vc.STILLS[name]["morphs"] == vc.SMIRK, name
    assert vc.SMIRK.get("にやり", 0) > 0 and all(v <= 0.5 for v in vc.SMIRK.values()), "a slight smirk"
    assert vc.SELECT["blades"] == vc.regal(1.0)["blades"], "the select close-up is stance B too"
    assert vc.SELECT.get("arms_crossed")
    # no other clip crosses his arms or plants both blades free
    for name, clip in vc.CLIPS.items():
        if name != "merchant":
            assert not any(k[1].get("arms_crossed") for k in clip["keys"]), name
    # the rest site: both blades planted upright behind him, and he sits upright
    for bl in vc.REST["blades"].values():
        assert not bl["hand"] and bl["anchor"] == "ground" and bl["dir"][2] < -0.95
        assert bl["at"][0] < 0, "behind him, away from the fire"
    assert abs(_op(vc.REST, "rotw", "上半身")[3]) <= 15, "upright, not reclining"


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
def test_shelf_packs_in_order_and_pages_what_does_not_fit():
    place, pages = pack.shelf([(300, 330)] * 20)
    assert len(pages) == 1 and pages[0][0] <= pack.MAX_SHEET
    assert [p[1:] for p in place[:2]] == [(0, 0), (300, 0)], "reading order"
    place, pages = pack.shelf([(1200, 1100)] * 19)
    assert len(pages) > 1 and all(w <= pack.MAX_SHEET and h <= pack.MAX_SHEET for w, h in pages)
    assert sorted({p[0] for p in place}) == list(range(len(pages)))
    assert pack.page_name("varka_attack.png", 0) == "varka_attack.png"
    assert pack.page_name("varka_attack.png", 2) == "varka_attack_p3.png"


def test_each_frame_is_trimmed_to_its_own_texels_and_lands_where_its_cell_would():
    frames = []
    for k in range(3):
        im = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
        im.paste(Image.new("RGBA", (20, 30), (255, 0, 0, 255)), (10 + 60 * k, 50))
        frames.append(im)
    sheets, rec = pack.sheets_for(frames, (100, 90), "x.png")
    pad = pack.PAD
    assert rec["cell"] == [140 + 2 * pad, 30 + 2 * pad] and rec["origin"] == [90 + pad, 40 + pad]
    for k, fr in enumerate(rec["frames"]):
        x, y, w, h = fr["rect"]
        assert (w, h) == (20 + 2 * pad, 30 + 2 * pad), "its own box, not the union"
        assert fr["offset"] == [60 * k, 0]
        page = sheets[fr["page"]][1]
        assert np.array_equal(np.asarray(page.crop((x, y, x + w, y + h))),
                              np.asarray(frames[k].crop((10 - pad + fr["offset"][0], 50 - pad, 10 - pad + fr["offset"][0] + w, 50 - pad + h))))


def test_ground_clip_cuts_below_the_feet_anchor_only():
    im = Image.new("RGBA", (10, 40), (255, 0, 0, 255))
    out = np.asarray(pack.ground_clip(im, 20.0, 1.0))
    assert (out[:26, :, 3] == 255).all() and (out[26:, :, 3] == 0).all()


def test_the_packer_names_every_sheet_it_writes():
    files = pack.SHEET_FILES["varka"]
    assert set(files) == {*pack.COMBAT, "merchant"}
    assert set(pack.COMBAT) | {"merchant"} == set(vc.CLIPS)
    assert set(pack.FX_FILES["varka"]) == {"attack", "ascension"}
    assert set(pack.EFFECT_FILES["varka"]) == {"ground_burst"}
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
        assert len(rec["frames"]) == rec["count"]
        for p in rec["pages"]:
            assert p["size"][0] <= pack.MAX_SHEET and p["size"][1] <= pack.MAX_SHEET
        for fr in rec["frames"]:
            x, y, w, h = fr["rect"]
            pw, ph = rec["pages"][fr["page"]]["size"]
            assert x + w <= pw and y + h <= ph, (clip, fr)
            assert fr["offset"][0] + w <= rec["cell"][0] and fr["offset"][1] + h <= rec["cell"][1], (clip, fr)
    target = chars.body_px(chars.CHARS["varka"]["height_in"])
    assert abs(m["measure"]["hat_to_boot_px"] / target - 1) < 0.06, m["measure"]
    assert m["stance_a"]["neck_px"] < m["measure"]["neck_px"], "the battle stance crouches"
    assert m["sheets"]["attack"]["main_frame"] == m["sheets"]["attack"]["impact_frames"][1]
    for clip in ("attack", "ascension"):
        f = m["fx"][clip]
        assert 0 <= f["first_frame"] and f["first_frame"] + f["count"] <= m["sheets"][clip]["count"]
    # the ascension's ground burst: its own clip, placed twice from the impact,
    # at the blade's point and mirrored under the target
    gb = m["effects"]["ground_burst"]
    assert gb["count"] == len(gb["frames"]) and gb["loop"] is False
    (use,) = gb["uses"]
    assert use["clip"] == "ascension" and use["start_frame"] == m["sheets"]["ascension"]["main_frame"]
    assert use["mirror"] and use["both_positions"]
    places = {p["at"]: p for p in use["places"]}
    assert set(places) == {"blade_tip", "target"} and places["target"]["flip_h"] and not places["blade_tip"]["flip_h"]
    dx, dy = places["blade_tip"]["offset_px"]
    assert dx > 0 and abs(dy) <= 8, "on the ground, in front of him"
    assert m["portrait"]["size"] == [132, 195]
    assert m["texture_import"] == "vram_compressed", "visual paper, pick 1 (a)"
    # the low guard keeps stance A tight: no wider than the reviewed 295 px at 1080p
    assert m["stance_a"]["width_px"] <= 300, m["stance_a"]


def test_his_crossed_arms_clear_each_other_and_the_blades_hide_neither_face_nor_arms():
    # render.py arms_crossed measures the deformed mesh in stance B (the shop
    # loop's first frame and the select still): how far any forearm or hand
    # vertex sinks behind the surface of the other arm or of his body (a
    # forearm through a forearm, a gauntlet through his chest), and, on the
    # canvas (y px, down), his chin, his crossed forearms and each blade's top.
    m = json.loads(pack.manifest_path("varka").read_text(encoding="utf-8"))
    crossed = m["arms_crossed"]
    assert set(crossed) == {"merchant", "select"}
    for still, g in crossed.items():
        for side in ("L", "R"):
            # stacked forearms touch: a skin's depth (0.015 units, ~1.5 cm)
            # at most, and only at a few vertices past 0.01
            assert g[side]["into_other_arm"] <= 0.015 and g[side]["into_other_arm_n"] <= 3, (still, side, g[side])
            assert g[side]["into_body"] <= 0.015 and g[side]["into_body_n"] <= 3, (still, side, g[side])
        top, bottom = g["forearms_px"]
        assert g["chin_px"] < top, ("his forearms are under his chin", still)
        assert set(g["blade_top_px"]) == {"L", "R"}
        for side, y in g["blade_top_px"].items():
            # every blade's highest point is under his crossed forearms: the
            # blades cover neither them nor his face
            assert y > bottom, ("a blade reaches his arms", still, side, y, bottom)


def test_tight_box_ignores_the_faint_haze():
    im = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    im.putpixel((2, 2), (255, 255, 255, 3))
    im.paste(Image.new("RGBA", (10, 10), (255, 255, 255, 255)), (15, 15))
    assert pack.tight_box([im]) == (15, 15, 25, 25)
    assert pack.tight_box([im], floor=1) == (2, 2, 25, 25)
