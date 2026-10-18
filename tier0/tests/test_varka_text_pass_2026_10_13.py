"""VARKA TEXT PASS (2026-10-13): the live damage previews from the
damage-preview census, display only. The play reads every number it read
before; the generated faces fold Strength, Weak and Vulnerable the way a
damage var does. C# twin: klee-mod/KleeTests/Prototype/VarkaTextPassTests.cs.
"""
from __future__ import annotations

from pathlib import Path

from tier0.content import yaml_memo
from tools import gen_klee_cards as gen

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
SHEET = REPO / "docs" / "prototype-surface.yaml"


def _row(row_id: str) -> dict:
    rows = yaml_memo.safe_load(SHEET.read_text(encoding="utf-8"))
    return next(r for r in rows if isinstance(r, dict) and r.get("id") == row_id)


def _cs(cls: str) -> str:
    return (GENERATED / f"{cls}.cs").read_text(encoding="utf-8")


FOLDED = {
    "ProtoVkChargedLunge": ("6m", "Electro"),
    "ProtoVkEmberCleave": ("9m", "Pyro"),
    "ProtoVkChainLightning": ("8m", "Electro"),
    # Varka pool audit (2026-10-13): 6 [8], was 4 [5].
    "ProtoVkTempestOfTheFourWinds": ("6m", "None"),
    "ProtoVkVioletStorm": ("6m", "Electro"),
    "ProtoVkKindledEdge": ("7m", "Pyro"),
    "ProtoVkRazorClawAndThunder": ("6m", "Electro"),
}


def test_plain_vkbase_hits_fold_like_damage_vars():
    for cls, (amount, element) in FOLDED.items():
        cs = _cs(cls)
        assert (f'new FoldedDamageVar("VkBase", {amount}, ValueProp.Move, '
                f'carries: Element.{element})') in cs, cls
        assert 'new DynamicVar("VkBase"' not in cs, cls


def test_stoke_the_flames_rider_is_not_folded():
    # Its VkBase is a bonus a later Pyro Attack carries, not a hit of its
    # own: folding Strength onto it would print the Strength twice.
    assert 'new DynamicVar("VkBase", 5m)' in _cs("ProtoVkStokeTheFlames")


def test_kindled_edge_prints_its_follow_up_as_a_folded_leg():
    face = _row("proto_vk_kindled_edge")["description"]
    assert face.endswith("deal {VkAgain:diff()} additional damage.")
    # Varka pool audit (2026-10-13): the bonus is its own 5 [7] VkAmount.
    cs = _cs("ProtoVkKindledEdge")
    assert 'new VarkaFollowUpDamageVar("VkAgain", "VkAmount")' in cs
    assert 'new DynamicVar("VkAmount", 5m)' in cs
    assert 'DynamicVars["VkAmount"].UpgradeValueBy(2m);' in cs


def test_razors_bonus_folds_inside_its_hit():
    cs = _cs("ProtoVkRazorClawAndThunder")
    assert ('new VarkaBonusDamageVar("VkAmount", 3m, "VkBase", '
            'Element.Electro)') in cs
    row = _row("proto_vk_razor_claw_and_thunder")
    assert row["effects"] == [{"op": "varka", "kind": "awakening",
                               "target": "enemy", "base": 6, "amount": 3}]


def test_blazing_charge_and_storm_battery_print_a_live_total():
    line = "{InCombat:\n(Deals {VkHit:diff()} damage)|}"
    for row_id in ("proto_vk_blazing_charge", "proto_vk_storm_battery"):
        assert _row(row_id)["description"].endswith(line), row_id
    assert "new VarkaHitDamageVar(Element.Pyro)" in _cs("ProtoVkBlazingCharge")
    assert "new VarkaStormBatteryDamageVar()" in _cs("ProtoVkStormBattery")


def test_no_number_moved():
    # Display only: the sheet numbers the census read are the ones printed.
    assert _row("proto_vk_blazing_charge")["effects"][0]["base"] == 8
    assert _row("proto_vk_storm_battery")["effects"][0]["per"] == 2
    assert _row("proto_vk_violet_storm")["effects"][0]["base"] == 6
    assert gen.VARKA_FOLDED_BASE_KINDS["tempest"] == "None"
