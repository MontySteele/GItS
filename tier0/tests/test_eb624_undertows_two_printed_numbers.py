"""`EB-624`: Undertow's face is the base game's conditional again.

[USER]'s Kokomi act-1 run of 2026-09-07 read `EB-598`'s one-number face --
"Deal 10 damage, already including 3 if the enemy has a debuff" -- as a
sentence arguing with itself. It was not wrong; it was `EB-441` working, the
number live against the hovered body and the clause explaining where part of
it came from. But the base game never writes a conditional that way. It writes
`FLATTEN`'s shape: two numbers, both live, and the reader picks.

SO THE FACE PRINTS TWO NUMBERS AND THE RULE DOES NOT MOVE. `PlainDamage` is
the hit with no rider, `DebuffDamage` the hit with it, and both are folded the
way the one number was -- the game's own dealer hook (they are
`FoldedDamageVar`s, which subclass Strike's `DamageVar`) and
`SimDamagePipeline.TargetMods` on the target's side. The hit is still the one
`CalculatedDamageVar` whose multiplier asks about a debuff, so nothing about
what the card DOES changed and there is still exactly one hit.

WHAT THIS FILE PINS. The sim's side of "both printed numbers are the delivered
ones": the delivered damage under a Weak Kokomi and a Vulnerable target is the
folded base with no debuff and the folded base+bonus with one, which is what
the two printed halves claim. The C# side is
`KleeTests/Prototype/Round16Tests.cs` (the two vars, the tokens, the upgrade,
and the fold's call sites); the printed NUMBERS themselves need a live combat,
which no headless harness here can build.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier05 import rewards

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def overhaul(monkeypatch):
    """The Kokomi arm ON, caches cleared both ways --
    the fixture in test_kokomi_overhaul.py verbatim, and for its reasons."""
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


def _undertow():
    return next(c for c in loader.prototype_cards()
                if c.id == "proto_kk_undertow")


def _delivered(debuffed: bool, weak: bool, vulnerable: bool) -> int:
    from tier0.tests.conftest import make_state

    state = make_state()
    state.player = loader.build_player("kokomi")
    if weak:
        state.player.powers["weak"] = 1
    enemy = state.enemies[0]
    if vulnerable:
        enemy.powers["vulnerable"] = 2
    elif debuffed:
        enemy.powers["poison"] = 3
    hp = enemy.hp
    effects.resolve_card(state, _undertow())
    return hp - enemy.hp


def test_the_two_printed_numbers_are_the_two_the_card_delivers(overhaul):
    """The bare board: the face's 7 and 10 are the hit's 7 and 10."""
    assert _delivered(debuffed=False, weak=False, vulnerable=False) == 7
    assert _delivered(debuffed=True, weak=False, vulnerable=False) == 10


def test_both_halves_fold_a_weak_kokomi_and_a_vulnerable_target(overhaul):
    """THE ROW'S ACCEPTANCE, on the board it names. A Vulnerable target is
    itself a debuff, so it buys the rider AND multiplies the total: the
    printed `DebuffDamage` is what lands, and `PlainDamage` is what lands on
    the same fold with the rider unbought.

    Both printed halves take the same fold as the number they replace, so a
    seat reading either one reads the hit. The sim's fold is the twin of the
    C#'s -- `SimDamagePipeline.TargetMods` is named for it -- and this is the
    arithmetic both are held to."""
    # Weak 1 on Kokomi, Vulnerable 2 on the body. Weak cuts the dealer's side,
    # Vulnerable raises the target's, and the debuff is bought by the same
    # Vulnerable.
    with_rider = _delivered(debuffed=True, weak=True, vulnerable=True)
    # The same fold with nothing on the body: the rider is unbought and no
    # target term applies.
    without_rider = _delivered(debuffed=False, weak=True, vulnerable=False)

    # One hit either way -- two would be two aura applications and two
    # reaction rolls, which is `EB-441`'s standing reason for the rider shape.
    assert with_rider > without_rider
    # The bonus rides INSIDE the fold rather than beside it, which is the
    # claim the face's second number makes: the pair differ by more than the
    # printed 3 once the target's multiplier is on.
    assert with_rider - without_rider > 3


def test_the_face_is_the_base_games_conditional(overhaul):
    """The sheet and the emitted C#: two tokens, and no `already including`
    clause left on this row."""
    import yaml

    sheet = yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    rows = sheet["cards"] if isinstance(sheet, dict) else sheet
    row = next(r for r in rows if r["id"] == "proto_kk_undertow")
    face = row["description"]
    assert face == ("Deal {PlainDamage:diff()} damage. If the enemy has a "
                    "debuff, deal {DebuffDamage:diff()} instead.")
    assert "already including" not in face

    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "Generated" / "ProtoKkUndertow.cs").read_text(encoding="utf-8")
    assert face in src
    assert 'new FoldedDamageVar("PlainDamage", 7m, ValueProp.Move)' in src
    assert 'new FoldedDamageVar("DebuffDamage", 10m, ValueProp.Move)' in src
    # The RULE is untouched: one hit, through the calculated var the rider's
    # multiplier decides.
    assert src.count("DamageCmd.Attack") == 1
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in src
    assert "KokomiOverhaulKit.HasDebuff(target) ? 1 : 0" in src


def test_the_upgrade_moves_every_number_the_row_carries(overhaul):
    """Three vars now hold the base: the one that is dealt and the two that
    are printed. A delta that moved only the first would split the face from
    the hit on the first forge, and it would only show on an upgraded copy."""
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "Generated" / "ProtoKkUndertow.cs").read_text(encoding="utf-8")
    assert "DynamicVars.CalculationBase.UpgradeValueBy(3m);" in src
    assert 'DynamicVars["PlainDamage"].UpgradeValueBy(3m);' in src
    assert 'DynamicVars["DebuffDamage"].UpgradeValueBy(3m);' in src


def test_the_tip_that_carried_the_pair_is_gone(overhaul):
    """`EB-484` put the pair on a hover tip because a face is registered once
    and cannot branch. It never had to branch. With both numbers printed and
    live, a tip restating the SHEET's 7 and 10 beside a face printing the
    folded ones would be `EB-441`'s own defect on the other surface."""
    tips = (REPO / "klee-mod" / "KleeCode" / "Cards"
            / "KokomiRiderTips.cs").read_text(encoding="utf-8")
    assert "ForDebuffRider" not in tips
    # The KEY is gone as a declaration; the paragraph explaining why it went
    # still names it, which is the file's own convention for a retired rule.
    assert "public const string DebuffRiderKey" not in tips
    mod = (REPO / "klee-mod" / "KleeCode"
           / "KleeMod.cs").read_text(encoding="utf-8")
    assert "DebuffRiderKey" not in mod
    undertow = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
                / "Generated" / "ProtoKkUndertow.cs").read_text(
                    encoding="utf-8")
    assert "ForDebuffRider" not in undertow
