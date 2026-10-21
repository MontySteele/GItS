"""The Bake-Kurage's creature scene: frame manifest -> bake_kurage.tscn.

`tools/kurage_render/kurage_frames.json` (the committed manifest
tools/kurage_render/pack.py writes beside the sheet) goes in;
klee-mod/pck-src/kokomi/model/bake_kurage.tscn comes out, byte-identically
on every run. `python -m tools.kokomi_rig gen` writes it with her other
scenes.

THE CONTRACT this scene keeps is the one the hand-written scene it replaces
kept (art polish, 2026-10-21), because three readers depend on it:

  * BakeKurageMonster (Powers/Prototype/BakeKuragePet.cs) and the engine:
    %Visuals is mandatory, `Bounds` (120x160) is the pet's placement beside
    Kokomi, and the AnimationTree carries the four states the router travels
    (idle, attack, hurt, death).
  * KokomiPlanFx.Pulse tweens `Visuals/Rig:scale` and
    `Visuals/Rig/Body:self_modulate`, so no animation here keys either.
  * The Rig sits at (0, -80): the anchor the sheet's origin is drawn on, the
    old sprite's centre.

What changed: `Body` steps a frame sheet (idle drift and tentacle sway, an
attack squash and stretch, a hurt recoil, a deflating death) where it was one
static sprite. The Rig's own tracks stay as they were -- the 3 s bob and sway,
the 30 px lunge, the hurt shake and flash, the death's sink and fade -- so
the jellyfish moves on screen as before and its frames carry the body.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.klee_rig.rig import vec2
from tools.varka_rig.rig import NL, Track, _steps, _transition, animation_block, atlas_block, clip_of, sub

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRAMES = ROOT / "tools" / "kurage_render" / "kurage_frames.json"
SCENE = ROOT / "klee-mod" / "pck-src" / "kokomi" / "model" / "bake_kurage.tscn"
FRAME_DIR = "res://kokomi/model/frames"
RIG = "Visuals/Rig"
BODY = "Visuals/Rig/Body"
REST_Y = -80.0
STATES = ("idle", "attack", "hurt", "death")
WHITE = (1.0, 1.0, 1.0, 1.0)


def load_frames(path: Path = FRAMES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _at(y: float = 0.0, x: float = 0.0):
    return (x, REST_Y + y)


def rig_tracks(name: str) -> list[Track]:
    """The Rig's own motion per state: the hand-written scene's, unchanged."""
    if name == "idle":
        ts = [0, 0.75, 1.5, 2.25, 3]
        return [Track(f"{RIG}:position", "vec2", ts, [_at(), _at(-6), _at(), _at(6), _at()], [1] * 5, interp=2),
                Track(f"{RIG}:rotation", "float", ts, [0.0, 0.035, 0.0, -0.035, 0.0], [1] * 5, interp=2)]
    if name == "attack":
        return [Track(f"{RIG}:position", "vec2", [0, 0.15, 0.35, 0.5], [_at(), _at(0, 30), _at(0, -4), _at()],
                      [0.5, 1.6, 1, 1])]
    if name == "hurt":
        return [Track(f"{RIG}:position", "vec2", [0, 0.06, 0.14, 0.22, 0.32, 0.4],
                      [_at(), _at(0, -8), _at(0, 6), _at(0, -3), _at(0, 2), _at()], [1] * 6),
                Track(f"{RIG}:modulate", "color", [0, 0.05, 0.35], [WHITE, (1, 0.45, 0.4, 1), WHITE], [1] * 3)]
    assert name == "death"
    # the frames tip and deflate it; the Rig sinks and fades it
    return [Track(f"{RIG}:modulate", "color", [0, 0.15, 1], [WHITE, (1, 0.62, 0.6, 1), (1, 1, 1, 0)], [1] * 3),
            Track(f"{RIG}:position", "vec2", [0, 1], [_at(), _at(16)], [1, 1])]


def build(frames: dict):
    clip = clip_of("kurage", frames, 1)
    anims = {}
    for name in STATES:
        rec = frames["clips"][name]
        first, count = rec["first"], rec["count"]
        times = [float(t) for t in rec["times"]]
        assert len(times) == count and times[-1] < rec["length"]
        tracks = rig_tracks(name) + [_steps(BODY, times, clip.atlases[first:first + count])]
        for t in tracks:
            assert not t.path.endswith((":scale", ":self_modulate")), "KokomiPlanFx.Pulse owns these"
        anims[name] = (rec, tracks)
    return clip, anims


def reset_tracks(clip) -> list[Track]:
    return [Track(f"{RIG}:position", "vec2", [0.0], [_at()], [1.0]),
            Track(f"{RIG}:rotation", "float", [0.0], [0.0], [1.0]),
            Track(f"{RIG}:modulate", "color", [0.0], [WHITE], [1.0]),
            _steps(BODY, [0.0], clip.atlases[:1])]


#: the hand-written scene's graph: idle to each one-shot, back on its end
EDGES = [("Start", "idle", 0, 2), ("idle", "death", 0, 0), ("idle", "hurt", 0, 0), ("hurt", "idle", 2, 2),
         ("death", "End", 2, 0), ("hurt", "death", 0, 0), ("idle", "attack", 0, 0), ("attack", "idle", 2, 2),
         ("attack", "death", 0, 0), ("attack", "hurt", 0, 0)]
SM_STATES = {"attack": (327, 64), "death": (470, 153), "hurt": (327, 278), "idle": (327, 153)}


def state_machine() -> list[str]:
    blocks = [f'[sub_resource type="AnimationNodeAnimation" id="AnimationNodeAnimation_{st}"]' + NL
              + f'animation = &"{st}"' for st in sorted(SM_STATES)]
    ids = []
    for src, dst, switch, adv in EDGES:
        tid = f"Transition_{src.lower()}_{dst.lower()}"
        ids.append(tid)
        blocks.append(_transition(tid, 0, switch, adv))
    sm = ['[sub_resource type="AnimationNodeStateMachine" id="AnimationNodeStateMachine_kurage"]',
          "states/End/position = Vector2(628, 153)",
          "states/Start/position = Vector2(186, 153)"]
    for st in sorted(SM_STATES):
        x, y = SM_STATES[st]
        sm.append(f'states/{st}/node = SubResource("AnimationNodeAnimation_{st}")')
        sm.append(f"states/{st}/position = Vector2({x}, {y})")
    sm.append("transitions = [" + ", ".join(f'"{s}", "{d}", SubResource("{i}")'
                                             for (s, d, _w, _a), i in zip(EDGES, ids)) + "]")
    blocks.append(NL.join(sm))
    return blocks


TAIL = """[node name="Bounds" type="Control" parent="."]
unique_name_in_owner = true
layout_mode = 3
anchors_preset = 0
offset_left = -60.0
offset_top = -160.0
offset_right = 60.0
offset_bottom = 0.0
mouse_filter = 2

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
unique_name_in_owner = true
libraries = {
&"": SubResource("AnimationLibrary_kurage")
}

[node name="AnimationTree" type="AnimationTree" parent="."]
unique_name_in_owner = true
active = true
callback_mode_discrete = 0
tree_root = SubResource("AnimationNodeStateMachine_kurage")
anim_player = NodePath("../AnimationPlayer")"""


def render_scene(frames: dict | None = None) -> str:
    frames = frames or load_frames()
    clip, anims = build(frames)
    subs = [atlas_block(a) for a in clip.atlases]
    subs.append(animation_block("Animation_reset", None, 0.001, False, reset_tracks(clip)))
    for name in STATES:
        rec, tracks = anims[name]
        subs.append(animation_block(f"Animation_{name}", name, float(rec["length"]), bool(rec["loop"]), tracks))
    subs.append('[sub_resource type="AnimationLibrary" id="AnimationLibrary_kurage"]' + NL + "_data = {" + NL
                + ("," + NL).join(['&"RESET": SubResource("Animation_reset")']
                                  + [f'&"{n}": SubResource("Animation_{n}")' for n in sorted(STATES)])
                + NL + "}")
    subs += state_machine()
    load_steps = len(clip.pages) + sum(s.count("[sub_resource") for s in subs) + 1
    out = [f"[gd_scene load_steps={load_steps} format=3]", ""]
    for ext_id, file in clip.pages:
        out.append(f'[ext_resource type="Texture2D" path="{FRAME_DIR}/{file}" id="{ext_id}"]')
    out.append("")
    for s in subs:
        out += [s, ""]
    ox, oy = frames["origin"]
    sc = frames["scale"]
    nodes = [
        '[node name="BakeKurageVisuals" type="Node2D"]',
        '[node name="Visuals" type="Node2D" parent="."]\nunique_name_in_owner = true',
        NL.join(['[node name="Rig" type="Node2D" parent="Visuals"]', f"position = {vec2(_at())}"]),
        NL.join(['[node name="Body" type="Sprite2D" parent="Visuals/Rig"]',
                 f"texture = {sub(clip.atlases[0])}",
                 "centered = false",
                 f"offset = {vec2((-ox, -oy))}",
                 f"scale = {vec2((sc, sc))}"]),
        TAIL,
    ]
    for n in nodes:
        out += [n, ""]
    return NL.join(out).rstrip(NL) + NL
