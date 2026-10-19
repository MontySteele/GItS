"""The ground shadow fades with the body at death (in-game check 2026-10-16).

Klee, Varka, Furina and Yae (2026-10-19) each draw a Shadow sprite beside their Model under
Visuals/Facing. The death clip faded the Model only, so "a dark oval stays
on the ground where they stood". tools/klee_rig/rig.shadow_fade copies the
Model's alpha onto the Shadow; this reads the shipped (generated) scenes, which
the rigs' own determinism tests hold to their generators.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.klee_rig.rig import shadow_fade, Track

ROOT = Path(__file__).resolve().parents[2]
SHADOW = 'NodePath("Visuals/Facing/Shadow:modulate")'


def _animations(text: str) -> dict[str, str]:
    """resource_name -> the sub_resource block's text."""
    out = {}
    for block in text.split("[sub_resource ")[1:]:
        m = re.search(r'resource_name = "(\w+)"', block)
        if m and 'type="Animation"' in block.split("\n", 1)[0]:
            out[m.group(1)] = block
    return out


@pytest.mark.parametrize("who", ["klee", "varka", "furina", "yae"])
def test_the_shadow_fades_out_with_the_death_clip_and_nowhere_else(who):
    text = (ROOT / "klee-mod" / "pck-src" / who / "model" / "combat.tscn").read_text(encoding="utf-8")
    anims = _animations(text)
    death = anims["death"]
    assert SHADOW in death, f"{who}: the death clip does not drive the shadow"
    after = death[death.index(SHADOW):]
    values = re.search(r'"values": \[(.*?)\]\n', after).group(1)
    assert values.rstrip().endswith("Color(1, 1, 1, 0)"), values
    for name, block in anims.items():
        if name != "death":
            assert SHADOW not in block, f"{who}: {name} drives the shadow"


def test_shadow_fade_copies_only_the_alpha_and_skips_an_opaque_clip():
    model = "Visuals/Facing/Model"
    hurt = Track(f"{model}:modulate", "color", [0.0, 0.5], [(1, 0.4, 0.4, 1), (1, 1, 1, 1)], [1.0, 1.0])
    assert shadow_fade([hurt], model, "Visuals/Facing/Shadow") is None
    death = Track(f"{model}:modulate", "color", [0.0, 2.0], [(1, 0.6, 0.6, 1), (1, 1, 1, 0)], [1.0, 1.0])
    fade = shadow_fade([death], model, "Visuals/Facing/Shadow")
    assert fade.path == "Visuals/Facing/Shadow:modulate"
    assert fade.times == [0.0, 2.0]
    assert fade.values == [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0)]
