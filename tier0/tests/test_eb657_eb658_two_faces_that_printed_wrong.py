"""`EB-657` and `EB-658`: two Kokomi faces that printed something the card did
not do, both closed by moving the FACE and nothing else.

`EB-657` (Feint). Both branch amounts of a conditional hit are literals by
construction (`gen_klee_cards._branch_amount`), so nothing folded them: the r25
lane-2 seat read "Deal 5 damage ... deal 10 instead" beside a Strike printed at
4 under the same Shrink, and the card dealt 7. `EB-624`'s answer, one card over
(Undertow), is the one taken -- a `FoldedDamageVar` per arm, printed and
nothing else, while the HIT stays the play-time `IsUpgraded` swap.

`EB-658` (Flank). "Each enemy that intends to attack" is read when the Plan is
WRITTEN and not when it is carried out (R250's rule for an aimed Plan, applied
to a set: `kokomi_plan` snapshots the set at `schedule`), so a Plan written
against a Summon intent dealt nothing the next morning and the face never said
why. The rule is untouched in both engines; the sentence now says when it
reads.

The printed NUMBERS need a live combat no headless harness here can build
(`KleeTests/README.md`, "The headless boundary"). What is pinned is the wiring:
which vars the generator declares, that each takes its own delta, that the hit
still swaps at play time, and that the two sheets say what the emitted C# says.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.gen_klee_cards import folded_branch_damage

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


def _sheet_row(card_id: str) -> dict:
    sheet = yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
    rows = sheet["cards"] if isinstance(sheet, dict) else sheet
    return next(r for r in rows if r["id"] == card_id)


# ---------------------------------------------------------------------------
# `EB-657`. FEINT'S TWO PRINTED NUMBERS ARE LIVE
# ---------------------------------------------------------------------------

def test_feints_face_prints_both_branches_as_folded_vars():
    row = _sheet_row("proto_kk_feint")
    face = row["description"]
    assert face == ("Deal {PlainDamage:diff()} damage. If a [gold]Plan[/gold] "
                    "was carried out this turn, deal {BranchDamage:diff()} "
                    "damage instead.")
    # The static swap the seat read is gone from this row entirely.
    assert "{IfUpgraded:show:" not in face

    src = (GENERATED / "ProtoKkFeint.cs").read_text(encoding="utf-8")
    assert face in src
    assert 'new FoldedDamageVar("PlainDamage", 5m, ValueProp.Move)' in src
    assert 'new FoldedDamageVar("BranchDamage", 10m, ValueProp.Move)' in src


def test_each_arm_takes_its_own_delta():
    """5 -> 7 and 10 -> 13, which is what `conditional_then_damage` exists for.
    A single delta on both printed vars would split the face from the hit on
    the first forge, and it would only show on an upgraded copy."""
    src = (GENERATED / "ProtoKkFeint.cs").read_text(encoding="utf-8")
    assert 'DynamicVars["PlainDamage"].UpgradeValueBy(2m);' in src
    assert 'DynamicVars["BranchDamage"].UpgradeValueBy(3m);' in src


def test_the_hit_is_untouched_and_still_swaps_at_play_time():
    """The vars are PRINTED and nothing else (`FoldedDamageVar`'s own rule), so
    this pass can print no number the card does not deal."""
    src = (GENERATED / "ProtoKkFeint.cs").read_text(encoding="utf-8")
    assert "(IsUpgraded ? 7m : 5m)" in src
    assert "(IsUpgraded ? 13m : 10m)" in src
    assert src.count("DamageCmd.Attack") == 2


def test_the_pair_is_a_shape_and_not_a_card_special_case():
    """Two aimed arms, a prototype row, and nothing else takes it: a
    single-armed conditional has no second number to disagree with, and a
    shipped row is outside the arm's quarantine (`calculated_damage_var`)."""
    feint = _sheet_row("proto_kk_feint")
    both = feint["effects"][0]
    assert [n for n, _b, _d in folded_branch_damage(feint, both)] == [
        "PlainDamage", "BranchDamage"]

    single = _sheet_row("proto_ko_sizzle")
    for eff in single["effects"]:
        assert folded_branch_damage(single, eff) == []

    shipped = dict(feint, id="feint")
    assert folded_branch_damage(shipped, both) == []


# ---------------------------------------------------------------------------
# `EB-658`. FLANK SAYS WHEN IT READS THE INTENTS
# ---------------------------------------------------------------------------

def test_flanks_face_names_the_moment_the_intents_are_read():
    row = _sheet_row("proto_kk_flank")
    assert row["description"] == (
        "Deal 8 damage. [gold]Plan[/gold]: Deal 8 damage to each enemy that "
        "intended to attack when you wrote this.")
    src = (GENERATED / "ProtoKkFlank.cs").read_text(encoding="utf-8")
    assert "intended to attack when you wrote this." in src
    assert "intends to attack." not in src


def test_flanks_rule_did_not_move():
    """A FACE PASS AND NOTHING ELSE: the aim is the same aim, and both engines
    still resolve it where they resolved it before."""
    row = _sheet_row("proto_kk_flank")
    assert row["plan"] == [{"op": "damage", "amount": 8,
                            "target": "enemies_intending_attack"}]

    sim = (REPO / "tier0" / "engine" / "kokomi_plan.py").read_text(
        encoding="utf-8")
    # The set is snapshotted at WRITING time, which is the fact the face now
    # states -- `schedule` rewrites the clause into a fixed body.
    assert 'c.get("target") == "enemies_intending_attack"' in sim
