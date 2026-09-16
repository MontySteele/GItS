"""`EB-498`: a conditional clause prints a live number, and `EB-388`: under
Guest Cast that number is the multiplied one.

THE FIND (`EB-498`, Klee r17). *Shinobu -- Thundergrust* printed "Deal 8
damage. If you are below half HP, deal 5 additional damage" at 29 of 62 HP and
removed 13. Neither number was a lie on its own; the FACE was, because the 8
renders through the card's one `CalculationBase` triple and the 5 was a
LITERAL. A literal folds nothing -- not Strength, not Weak, not the enemy's
Vulnerable, not the Spotlight -- so the card under-reported itself by whatever
those came to, on the one screen a player prices a turn from.

WHY THE TRIPLE COULD NOT CARRY IT. A card has ONE `CalculationBase` and a
Companion row already spends it on the top-level clause and the Spotlight fold
(`calc_rider`). The row's own next action names the answer: `EB-438`'s shape --
a second DECLARED var family, which `EB-624` had already built as
`FoldedDamageVar` for the two-armed case. This is that family on the one-armed
"additional" shape, plus its block twin.

`EB-388`'s HALF. The emitted play has always wrapped a Companion row's branch
leg in `SpotlightSystem.PrintedDamage` / `PrintedBlock`, so under Guest Cast
the leg already PAYS the multiplied number -- Furina r2 run 2 and r3 both read
faces that printed the unmultiplied one (Freminet printing 6 Block and paying
9). The Spotlight is deliberately not a `Hook.ModifyDamage` participant
(`PrintedDamageDelta`'s own note: routing it through the hook would fold
Strength into the multiplier and change the resolved hit), so the two folded
vars apply it themselves, before the hooks and in the play's own order. It is
the IDENTITY on anything that is not a spotlighted Companion row, which is why
every Klee, Kokomi and Furina-Stage face reads exactly what it read before.

WHAT IS NOT HERE. A `random_enemy` or `all_enemies` branch keeps its literal:
the first has no body for the preview to fold and the second would print one
number for a board that takes several (`debuff_calc_rider`'s rule, and
`folded_branch_damage`'s own). And a MODAL row is untouched -- both of a
modal's arms are printed, so a one-sided declaration would be a half-face.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.gen_klee_cards import folded_branch_damage

REPO = Path(__file__).resolve().parents[2]
GENERATED = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
             / "Generated")
SHEET = REPO / "docs" / "prototype-surface.yaml"

#: The row's own census: one aimed-damage row and four Block rows, plus the
#: Set-off row that shares the damage shape. `proto_mc_fischl_nightrider` is
#: the one the aim rule excludes -- Oz hits a RANDOM enemy.
DAMAGE_ROWS = ("proto_mi_shinobu_thundergrust", "proto_ko_sizzle")
BLOCK_ROWS = ("proto_ko_run_away", "proto_mc_noelle_breastplate",
              "proto_mi_shinobu_grass_ring")


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in yaml.safe_load(SHEET.read_text(encoding="utf-8"))
            if isinstance(r, dict) and "id" in r}


def _source(stem: str) -> str:
    return (GENERATED / f"{stem}.cs").read_text(encoding="utf-8")


def test_the_one_armed_shape_declares_its_own_damage_var():
    """The shape, read off the sheet rather than off a card list."""
    rows = _rows()
    for rid in DAMAGE_ROWS:
        card = rows[rid]
        folded = [t for eff in card["effects"]
                  for t in folded_branch_damage(card, eff)]
        assert [(n, cls) for n, _b, _d, cls in folded] == [
            ("BranchDamage", "FoldedDamageVar")], rid


def test_and_the_block_arm_takes_the_block_twin():
    rows = _rows()
    for rid in BLOCK_ROWS:
        card = rows[rid]
        folded = [t for eff in card["effects"]
                  for t in folded_branch_damage(card, eff)]
        assert [(n, cls) for n, _b, _d, cls in folded] == [
            ("BranchBlock", "FoldedBlockVar")], rid


def test_a_random_aim_keeps_its_literal():
    """Fischl's Oz hits a RANDOM enemy, so the preview has no body to fold and
    the face would print a number about a creature nobody has chosen."""
    card = _rows()["proto_mc_fischl_nightrider"]
    assert [t for eff in card["effects"]
            for t in folded_branch_damage(card, eff)] == []


def test_shinobus_face_prints_the_branch_as_a_var():
    """THE ROW'S ACCEPTANCE, on the card it was filed from: the printed number
    matches the hit, because both are now the same number folded once."""
    src = _source("ProtoMiShinobuThundergrust")
    assert "{CalculatedDamage:diff()}" in src
    assert "{BranchDamage:diff()}" in src
    assert 'new FoldedDamageVar("BranchDamage", 5m, ValueProp.Move)' in src
    # THE HIT IS UNTOUCHED, which is what makes this a display fix and not a
    # rules change: the play still deals `PrintedDamage(this, 5m)`, and the var
    # is printed and nothing else.
    assert "SpotlightSystem.PrintedDamage(this, 5m)" in src


def test_the_block_rows_print_theirs_too():
    for stem, amount in (("ProtoKoRunAway", "4m"),
                         ("ProtoMcNoelleBreastplate", "4m"),
                         ("ProtoMiShinobuGrassRing", "4m")):
        src = _source(stem)
        assert "{BranchBlock:diff()}" in src, stem
        assert f'new FoldedBlockVar("BranchBlock", {amount}, ' \
               "ValueProp.Move)" in src, stem


def test_both_vars_fold_the_spotlight_before_the_hooks():
    """`EB-388`'s half, read where it is written. The order is
    `SpotlitBlockVar`'s and for its reason: the play hands the command the
    PRINTED number and the game's terms apply to that, so a percentage must not
    compound against the wrong base."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "FrontFoldedDamageVar.cs").read_text(encoding="utf-8")
    assert "SpotlightSystem.PrintedDamage(card, BaseValue)" in src
    assert "SpotlightSystem.PrintedBlock(card, BaseValue)" in src
    assert "public sealed class FoldedBlockVar : BlockVar" in src


def test_a_modal_row_is_not_given_a_one_sided_pair():
    """Both of a modal's arms are printed, so a single declaration would be
    half a face. Itto's Superlative Superstrength is the row that bites."""
    card = _rows()["proto_itto_superlative_superstrength_either"]
    for eff in card["effects"]:
        assert len(folded_branch_damage(card, eff)) in (0, 2)
