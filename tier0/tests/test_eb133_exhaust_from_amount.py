"""EB-133: `exhaust_from` with a non-literal `amount:` blocks by name, not by
stack trace.

THE DEFECT. `blocked_reason`'s `exhaust_from` arm deliberately licenses
`amount != 1` on the CHOSEN branch — `CardSelectCmd.FromHand` takes a count,
so N distinct victims in one prompt is exactly the sim's "pick the worst,
remove it, repeat" without the loop. What it never checked is that the value
IS a count. `{op: exhaust_from, select: chosen, amount: all}` therefore walked
past every refusal in the function and met `str(int(eff.get("amount", 1)))`
in the chosen emitter — a `ValueError`, thrown by the one mechanism whose
entire job is to name what cannot be expressed.

The row is LEGAL tier0 grammar. `_op_exhaust_from` reads
`n = len(pool) if n == "all" else _amount(state, n)`
(`tier0/engine/effects.py:1995-1999`), which is Stoke's whole-hand shape, and
`_amount` accepts the `X` / `X_plus_N` formulas besides. The first author to
write one got a stack trace where the design promises a named blocker line.

WHY IT IS REFUSED RATHER THAN EMITTED. Emitting a pool-sized selection means
committing to what `CardSelectorPrefs`' count means when it is not a literal
— whether it clamps to the hand, whether a screen answerable exactly one way
is shown at all — and no decompile of the game is available in this tree to
read that contract off. No committed row prints the shape, so an emitted body
would be a guess at a call contract inside C# that no card would ever compile.
That is the failure every closed map in the generator exists to prevent. The
loop stays available to whoever has the dll; until then the generator says so.

The tests below are the red half: the crash shape must never crash again.
"""

from __future__ import annotations

import pytest
import yaml

from tools import gen_klee_cards as gen

SHEETS = ["docs/klee-cards.yaml", "docs/furina-cards.yaml",
          "docs/kokomi-cards.yaml"]


def _card(effect: dict) -> dict:
    return {
        "id": "fabricated_exhaust_all", "name": "Fabricated", "cost": 1,
        "type": "skill", "rarity": "common", "effects": [effect],
    }


# --- the filing shape ------------------------------------------------------

def test_chosen_exhaust_all_returns_a_reason_and_does_not_raise():
    """The exact row that produced the stack trace."""
    reason = gen.blocked_reason(
        _card({"op": "exhaust_from", "select": "chosen", "amount": "all"}),
        gen.KOKOMI_PROFILE)
    assert reason is not None, "amount: all generated silently"
    assert "exhaust_from" in reason and "all" in reason, reason


@pytest.mark.parametrize("amount", ["all", "X", "X_plus_2", 1.5, None])
@pytest.mark.parametrize("select", ["chosen", "random", None])
def test_no_non_int_amount_ever_raises(amount, select):
    """Every non-literal amount on either branch answers with a REASON.

    Parameterised over both branches on purpose: the random branch happened to
    refuse `all` already (through its `amount > 1` clause, since `"all" != 1`),
    but it refused it for the wrong reason and by luck of a `!=` comparison
    against a string. The guard now names the real problem on both."""
    effect = {"op": "exhaust_from", "amount": amount}
    if select is not None:
        effect["select"] = select
    reason = gen.blocked_reason(_card(effect), gen.KOKOMI_PROFILE)
    assert isinstance(reason, str) and reason, (
        f"amount={amount!r} select={select!r} produced {reason!r}")


# --- the licensed shapes are untouched -------------------------------------

def test_a_literal_count_on_the_chosen_branch_still_generates():
    """The clause EB-133 tightened exists to let `cleansing_tide` and
    `moonlit_offering` have upgrade paths; tightening it must not take those
    back."""
    for amount in (1, 2, 3):
        card = _card({"op": "exhaust_from", "select": "chosen",
                      "amount": amount})
        assert gen.blocked_reason(card, gen.KOKOMI_PROFILE) is None, amount


def test_the_random_status_branch_still_generates():
    card = _card({"op": "exhaust_from", "filter": "status", "amount": 1})
    assert gen.blocked_reason(card, gen.KLEE_PROFILE) is None


def test_a_random_count_above_one_still_names_the_re_pool_loop():
    card = _card({"op": "exhaust_from", "filter": "status", "amount": 2})
    reason = gen.blocked_reason(card, gen.KLEE_PROFILE)
    assert reason is not None and "re-pool" in reason, reason


# --- the premise -----------------------------------------------------------

def test_no_committed_row_prints_a_non_int_exhaust_amount():
    """If this goes red the refusal is stranding a live card and the answer
    becomes the C# loop, not the guard. Read EB-133 before deleting it."""
    offenders = []
    for sheet in SHEETS:
        for row in yaml.safe_load(open(sheet, encoding="utf-8")):
            if not isinstance(row, dict):
                continue
            stack = list(row.get("effects") or []) + list(row.get("sly") or [])
            while stack:
                eff = stack.pop()
                if not isinstance(eff, dict):
                    continue
                for key in ("effects", "then", "else"):
                    stack.extend(eff.get(key) or [])
                for mode in eff.get("modes") or []:
                    stack.extend(mode.get("effects") or [])
                if eff.get("op") == "exhaust_from" and not isinstance(
                        eff.get("amount", 1), int):
                    offenders.append((sheet, row.get("id"), eff))
    assert offenders == [], offenders
