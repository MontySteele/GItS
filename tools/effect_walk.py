"""The shared sheet-effect walk for `tools/` (S1 sweep lint L4).

WHY THIS EXISTS. A card row's `effects` is a TREE, not a list: a
`conditional` op carries `then:` and `else:` lists whose contents are as
real as anything printed at the top level. Every scanner in `tools/` that
answered a question by iterating `card["effects"]` directly was therefore
answering it about the top level ONLY, and said so nowhere. The S1 parity
sweep found three live instances of that one mistake, in three unrelated
tools, because each tool had rediscovered the flat loop for itself:

  * `sparkly_explosion` (klee) places two Bombs and names them, but the
    `place_bomb` sits in the kill-conditional's `then:` branch. The
    generator's `includes_bomb_rules` scan walks the top level, so the
    shipped card carries `includesBombRules: false` -- it names a
    mechanic and withholds the rules text for it. `lint_handwritten_parity`
    computes `exp_bomb_tips` with the SAME flat scan, so the gate agrees
    with the defect instead of catching it (both-sides-wrong: see the
    TOP_LEVEL_ONLY entry there).
  * `pearl_barrage` (kokomi) reads `amount_formula: {base: 5, ...}`. The
    role/tempo classifier's `pays_at_zero` test only ever looked at a
    literal `amount:`, so a card with a printed floor of 5 was tagged
    "deals nothing at an empty pile" -- see `printed_floor` below, which is
    the normalization half of the same bug.
  * `rider_tip_args` (generator) matched only the fanfare/salon/companion
    rider formulas, so `1_per_2_charge` on `all_streams_flow` rendered no
    rate anywhere. Not a recursion miss, but the same shape: one scanner's
    private vocabulary standing in for the sheet's.

So: ONE walk, imported, rather than N private ones. `iter_effects` yields
the whole tree; `printed_floor` normalizes `amount` vs
`amount_formula.base` so "what does this line pay with the meter at zero"
has a single answer.

A top-level-only read is still legitimate -- a gated benefit is not an
unconditional one, and `lint_strict_domination` depends on that. Those
sites are REGISTERED, with a reason, in
`tools/lint_effect_branch_scans.py`; they are not left to be recognised.

Import as `from tools import effect_walk` (package import) or, from a
path-invoked script that has already put the repo root on `sys.path`,
`import effect_walk`.
"""

from __future__ import annotations

from typing import Any, Iterator

# The keys a `conditional` op hangs its sub-lists off. Curated rather than
# "any value that is a list of dicts": a future op with a `targets:` list of
# dicts is not a branch, and guessing would make this walk report effects
# that never resolve.
BRANCH_KEYS = ("then", "else")


def iter_effects(effects: Any) -> Iterator[dict]:
    """Yield every effect in a row's effect TREE, branches included.

    Accepts an effects list or a whole card row (dict with `effects`), so a
    caller cannot silently pass the wrong thing and get an empty walk. The
    conditional itself is yielded BEFORE its branches -- a scanner that keys
    on `op == "conditional"` must still see it.
    """
    if isinstance(effects, dict) and "effects" in effects:
        effects = effects.get("effects")
    for fx in effects or ():
        if not isinstance(fx, dict):
            continue
        yield fx
        for key in BRANCH_KEYS:
            yield from iter_effects(fx.get(key))


def branch_effects(effects: Any) -> list[dict]:
    """Only the effects nested inside a branch -- the flat-scan blind spot."""
    top = list(iter_effects_top(effects))
    return [fx for fx in iter_effects(effects) if not any(fx is t for t in top)]


def iter_effects_top(effects: Any) -> Iterator[dict]:
    """The flat read, spelled out. Named so a deliberate top-level-only scan
    reads as a CHOICE in the source rather than as an oversight."""
    if isinstance(effects, dict) and "effects" in effects:
        effects = effects.get("effects")
    for fx in effects or ():
        if isinstance(fx, dict):
            yield fx


def printed_floor(fx: dict) -> int | None:
    """What this effect pays with every meter it reads at ZERO, or None.

    `amount: 5` and `amount_formula: {base: 5, per: 1, count: ...}` are the
    same promise to the player -- five, before the meter says anything --
    and the sheets use both spellings. A scanner that reads only the first
    calls the second a zero (the `pearl_barrage` miss). None means "no
    printed floor on this line", which is NOT the same as zero: `amount: 0`
    with a bonus_formula is the sheets' explicit "pays nothing on an empty
    meter" idiom and returns 0.
    """
    amount = fx.get("amount")
    if isinstance(amount, bool):
        return None
    if isinstance(amount, int):
        return amount
    formula = fx.get("amount_formula")
    if isinstance(formula, dict):
        base = formula.get("base")
        if isinstance(base, int) and not isinstance(base, bool):
            return base
        return 0        # a formula with no base pays nothing at zero
    return None
