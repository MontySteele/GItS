"""BACKLOG: "Wildfire Oath's damage has no preview on the card that applies
Pyro; a seat mis-added a lethal by 1." Every Varka row that applies Pyro,
and every shared Companion row that does, ends its face in
`{InCombat:{VarkaWildfire}|}`; `VarkaOath.WildfireLine` prints
"(Wildfire Oath deals N)" while a live Varka holds the power. C# twin:
`VarkaWaveWildfireTests`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

from pathlib import Path

from tier0.tests.test_arm_keyword_tips import PROTOTYPE_DIR, gen, proto

REPO = Path(__file__).resolve().parents[2]
OATH = REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype" / "VarkaOath.cs"


def test_the_varka_pyro_rows_carry_the_line():
    rows = {r["id"]: r for r in proto._rows()}
    for rid in ("proto_vk_ember_cleave", "proto_vk_amber_sharpshooter",
                "proto_vk_diluc_searing_onslaught", "proto_vk_kindled_edge",
                "proto_vk_blazing_charge", "proto_vk_amber_fiery_rain",
                "proto_vk_tempest_of_the_four_winds"):
        assert gen.applies_pyro(rows[rid]), rid
    for rid in ("proto_vk_stoke_the_flames", "proto_vk_wildfire_oath",
                "proto_vk_shatter"):
        assert not gen.applies_pyro(rows[rid]), rid


def test_the_generated_face_fills_the_token():
    src = (PROTOTYPE_DIR / "ProtoVkEmberCleave.cs").read_text(
        encoding="utf-8")
    assert "{InCombat:{VarkaWildfire}|}" in src
    assert ('description.Add("VarkaWildfire", '
            "VarkaOath.WildfireLine(this));") in src
    oath = OATH.read_text(encoding="utf-8")
    # The localization census (2026-10-23, step 2): a keyed row.
    assert r'"\n(Wildfire Oath deals {Damage})"' in oath
