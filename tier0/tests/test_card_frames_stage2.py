"""Card frames stage 2 (2026-10-20), the parts checkable without a game.

[USER]: "Agreed on all of the card / orb / energy mockup picks, including
Kokomi's (b)". Pinned here: the two generators own every out-path they write
(art_lint L11), the cost-orb generator reads the kit numbers from the one C#
table, and the split-frame shader declares every uniform the C# sets.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import gen_energy_orb_layers as orbs          # noqa: E402
import gen_kit_energy_icons as icons          # noqa: E402
from tools.art_lint import GENERATOR_OWNED    # noqa: E402

SHADER = ROOT / "klee-mod" / "pck-src" / "shared" / "companion_split_frame.gdshader"
SPLIT_CS = (ROOT / "klee-mod" / "KleeCode" / "Vfx" / "CompanionSplitFrame.cs").read_text(encoding="utf-8")


def test_every_placed_orb_layer_is_owned_by_the_orb_generator():
    assert set(orbs.APPLY_DIRS) == {"set_a_fontaine", *orbs.KIT_SETS}
    for rel in orbs.APPLY_DIRS.values():
        for _, layer, _, _ in orbs.LAYERS:
            assert GENERATOR_OWNED.get(f"{rel}/{layer}.png") == "gen_energy_orb_layers.py", rel


def test_every_kit_icon_is_owned_by_the_icon_generator():
    for rel in icons.KIT_DIRS.values():
        for name in (icons.COST_FILE, icons.TEXT_FILE):
            assert GENERATOR_OWNED.get(f"{rel}/{name}") == "gen_kit_energy_icons.py", rel


def test_the_icon_generator_reads_every_kit_tint_from_the_table():
    tints = icons.kit_tints()
    assert set(tints) == {"klee", "furina", "kokomi", "varka", "yae"}
    assert tints["klee"] == (0.065, 1.3, 1.15)
    assert tints["kokomi"] == (0.03, 0.38, 1.55)


def test_the_kit_orb_sets_are_the_ruled_shapes():
    # Klee scalloped (12 petals), Kokomi B, Varka three lobes, Yae five petals.
    assert orbs.KIT_SETS["klee_pyro"][2] == (7, 12)
    assert orbs.KIT_SETS["kokomi_pearl"][1]["body_inner"] == (250, 214, 200)
    assert orbs.KIT_SETS["varka_anemo"][2] == (3, 0)
    assert orbs.KIT_SETS["yae_electro"][2] == (5, 5)


def test_the_shader_declares_every_uniform_the_csharp_sets():
    text = SHADER.read_text(encoding="utf-8")
    assert text.startswith("shader_type canvas_item;")
    declared = set(re.findall(r"^uniform \w+ (\w+)", text, re.M))
    used = set(re.findall(r'SetShaderParameter\("(\w+)"', SPLIT_CS))
    assert used == declared, (used, declared)
    assert '"shared/companion_split_frame.gdshader"' in SPLIT_CS
