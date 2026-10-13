"""The relic/potion icon lint bites, and HEAD is clean (2026-10-12).

Varka's seven relics and three potions drew placeholders for eleven days
because their icon paths are built by helpers no string-reading gate followed.
The synthetic arms below are that defect, watched fail.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools import lint_relic_potion_icons as lint   # noqa: E402


def _row(bases, body, abstract=False):
    return {"bases": bases, "abstract": abstract, "static": False,
            "body": body, "file": REPO / "x.cs"}


def _world():
    return {
        "VarkaArmRelics": _row([], 'internal static string Icon(string slug) '
                                   '=> "varka/relics/" + slug + ".png";'),
        "VarkaArmRelic": _row(["CustomRelicModel"],
                              "KleePck.Path(VarkaArmRelics.Icon(Slug))",
                              abstract=True),
        "Banner": _row(["VarkaArmRelic"], 'protected override string Slug => "banner";'),
        "Elixir": _row(["ArmPotion"], 'ArmPotions.Image("varka", "elixir")'),
        "ArmPotion": _row(["CustomPotionModel"], "", abstract=True),
        "Fang": _row(["CustomRelicModel"], 'KleePck.Path("varka/relics/fang.png")'),
        "Klee": _row(["CustomRelicModel"], 'KleePck.Path("klee/relics/charm.png")'),
        "Bare": _row(["CustomRelicModel"], "no icon override"),
    }


PLAN = {"ImageGen/images/varka/relics/banner.png",
        "ImageGen/images/varka/potions/elixir.png",
        "ImageGen/images/varka/relics/fang.png",
        "ImageGen/images/relics/charm.png"}


def test_head_is_clean():
    assert lint.findings() == []


def test_every_spelling_resolves_and_a_bare_class_bites():
    found = lint.findings(known=_world(), plan=PLAN, debt={})
    assert len(found) == 1, found
    assert found[0].startswith("Bare") and "no icon path" in found[0]


def test_a_built_path_with_no_plan_row_bites():
    plan = PLAN - {"ImageGen/images/varka/relics/banner.png",
                   "ImageGen/images/varka/potions/elixir.png"}
    found = lint.findings(known=_world(), plan=plan, debt={"Bare": "test"})
    assert len(found) == 2
    assert any("varka/relics/banner.png" in f for f in found)
    assert any("varka/potions/elixir.png" in f for f in found)


def test_debt_rots():
    found = lint.findings(known=_world(), plan=PLAN,
                          debt={"Bare": "test", "Fang": "now planned",
                                "Gone": "cut"})
    assert any(f.startswith("Fang: on ICON_DEBT") for f in found)
    assert any(f.startswith("Gone: on ICON_DEBT") for f in found)
