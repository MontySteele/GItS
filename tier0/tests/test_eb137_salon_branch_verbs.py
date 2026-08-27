"""EB-137: the two salon verbs are legal branch ops, and now say so twice.

`salon_rotate` and `salon_perform` went into `BRANCH_OPS` with EB-118 sec.5.5
and were never given a row in `BRANCH_FIELDS` or an arm in `_branch_text`.
Both omissions are silent until the first salon verb reaches a branch, and
then they fail in the two worst ways a generator can:

  * `_branch_op_reason` does `set(eff) - BRANCH_FIELDS[eff["op"]]`, so a
    missing row raised `KeyError` and took the whole sheet down instead of
    naming the bad field on the offending card;
  * `_branch_text`'s `else` arm is a hard `SystemExit` -- correct as a
    backstop, but it means a perfectly legal row could not be printed at all.

So the three legs here are: both shapes EMIT, both shapes PRINT, and a bad
field BLOCKS BY NAME rather than raising. The printed copy is PROVISIONAL
under R212(7) -- it mirrors the top-level `build_description` arms word for
word, and the lint that proves it cosmetic is `gen_roster_cards.py --check`.
"""

from __future__ import annotations

import pytest

from tools import gen_klee_cards as gen

VERBS = ("salon_rotate", "salon_perform")

# The C# each verb resolves to inside a branch -- the same call the top-level
# arm makes, which is the point of the branch resolver.
EMITTED = {
    "salon_rotate": "SalonMemberPower.RotateLeftmost(Owner.Creature, {n});",
    "salon_perform": ("await SalonMemberPower.PerformLeftmost("
                      "choiceContext, Owner.Creature, {n});"),
}

PRINTED = {
    "salon_rotate": "moves to the back",
    "salon_perform": "performs now",
}


def _row() -> dict:
    """A card with no upgrade deltas of any kind, so the branch helpers that
    read the card (`conditional_bonus_upgrade`, `branch_draw_upgrade`,
    `encore_upgrade`) all answer zero and nothing but the salon arm is under
    test."""
    return {"id": "eb137_probe", "effects": [], "upgrade": {}}


def _emit(eff: dict) -> str:
    lines: list[str] = []
    gen._emit_branch_op(_row(), eff, lines, ctx={}, in_then=True,
                        cb_state={}, spotlight_capable=False)
    return "\n".join(lines)


# --- 1. the field table exists, and agrees with the top-level validator ----

@pytest.mark.parametrize("op", VERBS)
def test_the_verb_has_a_branch_field_row(op):
    assert op in gen.BRANCH_OPS
    # `amount` is OPTIONAL -- one rotation and one act are the natural units.
    assert gen.BRANCH_FIELDS[op] == {"op", "amount"}


@pytest.mark.parametrize("op", VERBS)
def test_the_bare_and_counted_shapes_are_both_legal(op):
    assert gen._branch_op_reason({"op": op}, "conditional branch") is None
    assert gen._branch_op_reason({"op": op, "amount": 3},
                                 "conditional branch") is None


@pytest.mark.parametrize("op", VERBS)
def test_a_non_positive_or_non_literal_amount_blocks(op):
    """`amount` is optional, not unchecked -- the same bar the top-level
    validator applies."""
    for bad in (0, -1, "2", 1.5, None):
        reason = gen._branch_op_reason({"op": op, "amount": bad},
                                       "conditional branch")
        assert reason is not None, bad
        assert "positive literal int" in reason, bad


@pytest.mark.parametrize("op", VERBS)
def test_a_bad_field_blocks_by_name_instead_of_raising(op):
    """The defect this file exists for: before the BRANCH_FIELDS rows landed
    this line raised `KeyError` out of the generator. A blocked card must say
    which field it did not understand."""
    reason = gen._branch_op_reason({"op": op, "amount": 1, "member": "furina"},
                                   "conditional branch")
    assert reason is not None
    assert "member" in reason
    assert op in reason


# --- 2. both shapes emit ---------------------------------------------------

@pytest.mark.parametrize("op", VERBS)
def test_the_bare_shape_emits_the_default_of_one(op):
    assert _emit({"op": op}) == EMITTED[op].format(n=1)


@pytest.mark.parametrize("op", VERBS)
def test_the_counted_shape_emits_its_literal(op):
    assert _emit({"op": op, "amount": 3}) == EMITTED[op].format(n=3)


# --- 3. both shapes print --------------------------------------------------

@pytest.mark.parametrize("op", VERBS)
def test_the_bare_shape_prints_a_singular_clause(op):
    txt = gen._branch_text(_row(), [{"op": op}], in_then=True)
    assert txt == ("the leftmost member of your [gold]Salon[/gold] "
                   f"{PRINTED[op]}.")


@pytest.mark.parametrize("op", VERBS)
def test_the_counted_shape_prints_its_count(op):
    txt = gen._branch_text(_row(), [{"op": op, "amount": 3}], in_then=True)
    assert txt == ("the leftmost member of your [gold]Salon[/gold] "
                   f"{PRINTED[op]}, 3 times.")


@pytest.mark.parametrize("op", VERBS)
def test_the_clause_is_never_empty(op):
    """The `_branch_text` else arm exists because an op with no text arm
    renders "If a reaction triggered: ." -- an empty clause on a shipped
    card. Neither salon verb can reach it any more."""
    for eff in ({"op": op}, {"op": op, "amount": 2}):
        txt = gen._branch_text(_row(), [eff], in_then=True)
        assert txt.strip() not in ("", ".")
