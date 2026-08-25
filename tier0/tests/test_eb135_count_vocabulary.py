"""EB-135: `amount_formula.count:` is checked at LOAD, like every other name.

THE GAP. `loader._validate_effect_vocabulary` checked `op:` against
`effects.OPS` and `if:` through `is_known_predicate`, and stopped. Meanwhile
`_calc_amount` resolved `formula["count"]` through `_runtime_count`, which
raises `unknown runtime count` the first time the card RESOLVES — verbatim the
failure that function's own docstring says it was written to end. For a Rare
that means in front of a player rather than in a test, and on the co-op seat
there is no sim backstop at all. It was the one grammar the check existed for
that it did not cover.

FOUR SPELLINGS REACH THE SAME RAISE, so all four are checked against one
registry rather than one of them being singled out:

    amount_formula: {count: <token>}     -> _calc_amount
    times_formula:  {count: <token>}     -> _calc_amount, same door
    amount: "<token>"                    -> _amount's last arm
    times:  "<token>"                    -> _amount, same arm

TWO OTHER GRAMMARS WEAR THOSE KEYS and the check knows about both — it found
them by being run over the reference pools rather than by being reasoned
about, which is why they are pinned here:

  * `apply_power`'s `amount_formula` is `{target_power: <name>}`, resolved by
    `_power_amount_formula`. `ic_dominate` and `ic_molten_fist` print it. A
    naive count check refuses both and takes `real_ironclad` — a MEASUREMENT
    ANCHOR — off the board on any machine holding `game_ref/`.
  * `exhaust_from` reads `amount: "all"` itself, before `_amount` ever sees
    it (the pool size, Stoke's whole-hand shape). `ic_fiend_fire` and
    `ic_second_wind` print it.

Both live only in the gitignored reference tree, so neither is visible to this
worktree's own suite — the structurally-invisible-defect shape exactly. The
sets that carve them out (`POWER_FORMULA_OPS`, `AMOUNT_ALL_OPS`) are named in
the engine so the carve-out is a declaration rather than an `if` nobody can
find, and the 326 reference rows were validated by hand against this code
before it landed.

NOTHING ABOUT RESOLUTION MOVES. No sheet changes, no number changes; only
WHEN a typo is reported moves, which is the whole point.
"""

from __future__ import annotations

import pytest

from tier0.content import loader
from tier0.engine import effects


def _effect(**kw):
    return dict(kw)


# --- the filing shape ------------------------------------------------------

def test_a_typod_count_is_refused_at_load_naming_card_and_token():
    with pytest.raises(ValueError) as exc:
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "damage", "target": "enemy",
             "amount_formula": {"base": 5, "per": 1, "count": "exhuast_pile"}}])
    msg = str(exc.value)
    assert "probe_card" in msg, msg
    assert "exhuast_pile" in msg, msg
    assert "amount_formula" in msg, msg


def test_a_missing_count_key_is_refused_too():
    """`formula["count"]` is a KeyError, not even a named raise, at resolve."""
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "block", "amount_formula": {"base": 5, "per": 1}}])


@pytest.mark.parametrize("effect", [
    {"op": "damage", "target": "enemy", "amount": 1,
     "times_formula": {"base": 1, "per": 1, "count": "exhuast_pile"}},
    {"op": "draw", "amount": "hand_sizes"},
    {"op": "damage", "target": "enemy", "amount": 1, "times": "salon_member"},
])
def test_the_sibling_spellings_are_refused_as_well(effect):
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [effect])


def test_a_typo_inside_a_branch_is_refused():
    """The recursion already reaches every nested body; the count check rides
    it, so an unreachable-today branch — where a typo survives longest — is
    covered."""
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "conditional", "if": "has_spark",
             "then": [{"op": "block", "amount_formula": {"count": "nope"}}]}])


def test_a_typo_inside_a_mode_body_is_refused():
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "choose_one", "modes": [
                {"label": "A", "effects": [{"op": "draw", "amount": 1}]},
                {"label": "B", "effects": [
                    {"op": "draw", "amount": "hand_sizze"}]}]}])


# --- the legal vocabulary still loads --------------------------------------

@pytest.mark.parametrize("token", sorted(effects.RUNTIME_COUNT_NAMES))
def test_every_registered_count_passes(token):
    loader._validate_effect_vocabulary("probe_card", [
        {"op": "block", "amount_formula": {"base": 0, "per": 1,
                                           "count": token}}])


@pytest.mark.parametrize("key", sorted(effects.exhaust_selection_counts([])))
def test_the_prefix_family_passes(key):
    token = effects.EXHAUST_SELECTION_PREFIX + key
    assert effects.is_known_count(token)
    loader._validate_effect_vocabulary("probe_card", [
        {"op": "block", "amount_formula": {"count": token}}])


def test_a_bad_prefix_key_is_refused():
    assert not effects.is_known_count(
        effects.EXHAUST_SELECTION_PREFIX + "attaks")
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "block", "amount_formula": {
                "count": effects.EXHAUST_SELECTION_PREFIX + "attaks"}}])


@pytest.mark.parametrize("val", ["X", "X_plus_2", "-X", "hand_size", 3])
def test_the_amount_grammar_passes(val):
    loader._validate_effect_vocabulary("probe_card", [
        {"op": "draw", "amount": val}])


@pytest.mark.parametrize("val", ["X_plus_", "X_plus_two", "-", "Y"])
def test_a_broken_amount_formula_is_refused(val):
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "draw", "amount": val}])


# --- the two other grammars wearing the same keys --------------------------

def test_the_power_reading_formula_is_not_a_count():
    """`ic_dominate` / `ic_molten_fist`. A count check that did not know this
    refuses two reference-pool cards and takes a MEASUREMENT ANCHOR with
    them."""
    assert "apply_power" in effects.POWER_FORMULA_OPS
    loader._validate_effect_vocabulary("probe_card", [
        {"op": "apply_power", "power": "strength", "target": "self",
         "amount_formula": {"target_power": "vulnerable"}}])


def test_a_power_formula_naming_nothing_is_refused():
    with pytest.raises(ValueError, match="target_power"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "apply_power", "power": "strength", "target": "self",
             "amount_formula": {"base": 1}}])


def test_exhaust_from_reads_amount_all_itself():
    """`ic_fiend_fire` / `ic_second_wind`. `_op_exhaust_from` resolves "all"
    as the pool size before `_amount` is ever called."""
    assert "exhaust_from" in effects.AMOUNT_ALL_OPS
    loader._validate_effect_vocabulary("probe_card", [
        {"op": "exhaust_from", "amount": "all"}])


def test_amount_all_anywhere_else_is_refused():
    with pytest.raises(ValueError, match="unknown runtime count"):
        loader._validate_effect_vocabulary("probe_card", [
            {"op": "draw", "amount": "all"}])


# --- the state-free contract -----------------------------------------------

def test_the_checkers_are_pure_and_state_free():
    """`is_known_predicate`'s contract, held by its two new siblings: no
    `CombatState`, no side effects, safe to call from the loader."""
    assert effects.is_known_count("exhaust_pile") is True
    assert effects.is_known_count("exhuast_pile") is False
    assert effects.is_known_count(None) is False
    assert effects.is_known_count(7) is False
    assert effects.is_known_amount(0) is True
    assert effects.is_known_amount(True) is False
    assert effects.is_known_amount(None) is False
