"""The damage previews pass (2026-10-13).

[USER]: "Are there any other cards, in any pool, that don't show how much
damage they actually do when accounting for conditional modifiers?"

Display only: each row gains an in-combat line over a display var that the
play never reads. These pins read the sheet and the generated C# (CI-visible;
the arithmetic pins are `KleeTests/Prototype/DamagePreviews20261013Tests.cs`).
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


def _deals(token: str) -> str:
    return "{InCombat:\\n(Deals {" + token + ":diff()} damage)|}"


#: (row id, generated class, the line the face ends with, the var it declares)
CASES = [
    ("proto_ko_big_badda_boom", "ProtoKoBigBaddaBoom",
     "{InCombat:\\n(Then deals {BombEcho:diff()} damage)|}",
     "new SetOffEchoDamageVar()"),
    ("proto_ko_fireworks_finale", "ProtoKoFireworksFinale",
     _deals("TotalDamage"),
     "new HitsTotalDamageVar(static card => SparkPower.SparksAtPlay("),
    ("proto_ko_taste_test", "ProtoKoTasteTest", _deals("BombHit"),
     "new BombReadDamageVar(ProtoBombPower.BombRead.TargetTotalDouble)"),
    ("proto_ko_simmer", "ProtoKoSimmer", _deals("BombHit"),
     "new BombReadDamageVar(ProtoBombPower.BombRead.Largest)"),
    ("proto_ko_the_big_one", "ProtoKoTheBigOne",
     "{InCombat:\\n([gold]Bombs[/gold]: {SetOffBombs} damage)|}",
     "new SetOffBombsVar(4)"),
    ("proto_ko_team_effort", "ProtoKoTeamEffort", _deals("BonusHit"),
     "new CompanionBonusDamageVar(6)"),
    ("proto_mc_noelle_sweeping_time", "ProtoMcNoelleSweepingTime",
     _deals("CalculatedDamage"),
     "new FrontFoldedDamageVar(ValueProp.Move).WithMultiplier("),
    ("proto_kk_shoal_of_spears", "ProtoKkShoalOfSpears",
     _deals("TotalDamage"),
     "new HitsTotalDamageVar(static card => KokomiPlan.ChainPlansHeld("),
    ("proto_kk_drowning_pressure", "ProtoKkDrowningPressure",
     _deals("PressureHit"), "new DebuffsAfterDamageVar()"),
    ("proto_fs_bravura", "ProtoFsBravura", _deals("TotalDamage"),
     "new HitsTotalDamageVar(static card => 0 + 1 * "
     "(FurinaStage.SpentOrUpTo(card, 18) / FurinaStageLaw.BravuraSpentPer))"),
]


@pytest.mark.parametrize("row_id,cls,line,var", CASES)
def test_the_face_prints_its_live_total(row_id, cls, line, var):
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    row = sheet[sheet.index("{id: " + row_id + ","):]
    row = row[:row.index("\n\n")]
    assert line + '",' in row
    src = (GEN / f"{cls}.cs").read_text(encoding="utf-8")
    assert line + '"),' in src
    assert var in src


def test_no_number_moved():
    """Display only: the hits and upgrades the plays read are untouched."""
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    for needle in ("{op: set_off, target: enemy, damage: 12}",
                   "{op: multiply_set_off, multiplier: 4}",
                   "{op: damage, amount: 5, target: all_enemies, "
                   "times: sparks_spent}",
                   "bonus_if: {if: companion_played_this_turn, amount: 6}",
                   "amount_formula: {base: 0, per: 3, count: "
                   "weak_vuln_stacks_on_target}",
                   "{op: damage, amount: 5, target: all_enemies,\n"
                   "              times: chain_plans_held_plus_one}"):
        assert needle in sheet, needle
