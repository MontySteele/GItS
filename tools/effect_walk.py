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
    generator's `includes_bomb_rules` scan walked the top level, so the
    card shipped `includesBombRules: false` -- it named a mechanic and
    withheld the rules text for it, and `lint_handwritten_parity` computed
    `exp_bomb_tips` with the SAME flat scan, so the gate agreed with the
    defect instead of catching it. FIXED (L4a): both scans walk this tree
    now, in one commit with the regen, because deepening either alone turns
    the other into a red gate.
  * `pearl_barrage` (kokomi) reads `amount_formula: {base: 5, ...}`. The
    role/tempo classifier's `pays_at_zero` test only ever looked at a
    literal `amount:`, so a card with a printed floor of 5 was tagged
    "deals nothing at an empty pile" -- see `printed_floor` below, which is
    the normalization half of the same bug.
  * `rider_tip_args` (generator) matched only the fanfare/salon/companion
    rider formulas, so `1_per_2_charge` on `all_streams_flow` rendered no
    rate anywhere. Not a recursion miss, but the same shape: one scanner's
    private vocabulary standing in for the sheet's. FIXED (L4b): the charge
    branch renders through `KokomiRiderTips.ForChargeRider`.

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

# The modal (`choose_one`) shape, EB-118: `modes:` is a list of MODE DICTS,
# each `{label:, effects:}` -- one level deeper than a branch, which is why
# it cannot just join BRANCH_KEYS. Every mode body is printed text the player
# can always reach, so it is a branch for every question this walk answers.
MODES_KEY = "modes"
MODE_EFFECTS_KEY = "effects"


def iter_effects(effects: Any) -> Iterator[dict]:
    """Yield every effect in a row's effect TREE, branches and modes included.

    Accepts an effects list or a whole card row (dict with `effects`), so a
    caller cannot silently pass the wrong thing and get an empty walk. The
    conditional (or the modal) itself is yielded BEFORE its sub-lists -- a
    scanner that keys on `op == "conditional"` must still see it.
    """
    if isinstance(effects, dict) and "effects" in effects:
        effects = effects.get("effects")
    for fx in effects or ():
        if not isinstance(fx, dict):
            continue
        yield fx
        for key in BRANCH_KEYS:
            yield from iter_effects(fx.get(key))
        for mode in fx.get(MODES_KEY) or ():
            if isinstance(mode, dict):
                yield from iter_effects(mode.get(MODE_EFFECTS_KEY))


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


# --- the unified Sly grammar (EB-71, R174), sheet-row side ------------------
#
# `tier0.engine.state` owns this grammar for Card OBJECTS; these two helpers
# are the same reading for SHEET ROWS, which is what everything in `tools/`
# holds. Kept here rather than imported from tier0 because the scanners in
# this package walk raw yaml (no loader, no dataclass) and because the
# generator is deliberately tier0-free; `SLY_AUTOPLAY_OP` is pinned against
# `tier0.engine.state.SLY_AUTOPLAY_OP` in tier0/tests/test_eb71_cs_parity.py
# the way lint_constant_parity pins the C# mirrors.
#
# One `sly:` list carries two things. Ordinary riders are an authored effect
# list a discard RESOLVES (Kokomi's Assist lane). The reserved marker
# `{op: sly_autoplay}` is the base-game `CardKeyword.Sly` -- the discarded
# card is auto-played, which is a card PLAY and not an effect list, so it is
# never dispatched as an op and never priced as one. A scanner that reads a
# row's Sly as printed effects wants `sly_riders()`; the marker is worth
# exactly zero to it.
SLY_AUTOPLAY_OP = "sly_autoplay"


def sly_riders(row: Any) -> list[dict]:
    """The AUTHORED half of a sheet row's Sly -- the effects a discard runs."""
    sly = row.get("sly") if isinstance(row, dict) else row
    if not isinstance(sly, list):
        return []       # a malformed/retired `sly:` prints no riders; the
                        # generator blocks the row by name (_sly_marker_reason)
    return [fx for fx in sly
            if isinstance(fx, dict) and fx.get("op") != SLY_AUTOPLAY_OP]


def sly_autoplays(row: Any) -> bool:
    """True when a sheet row prints the base-game auto-play keyword."""
    sly = row.get("sly") if isinstance(row, dict) else row
    if not isinstance(sly, list):
        return False
    return any(isinstance(fx, dict) and fx.get("op") == SLY_AUTOPLAY_OP
               for fx in sly)


def iter_card_effects(row: Any) -> Iterator[dict]:
    """Every PRINTED effect of a card ROW — the played face's tree AND the
    Sly branch's tree.

    EB-134, the sheet-side half. `sly:` is a card-LEVEL effect list, not an
    effect-level one, so `iter_effects` (which walks `then`/`else`/`modes`
    from inside an effect) cannot reach it however deep it recurses. Every
    scanner that asked a CAPABILITY question — "can this card retrieve from
    the exhaust pile at all" — through `iter_effects` alone was therefore
    answering it about the played face only, and a Sly rider is printed text
    the player can always reach.

    Use this for capability questions. Keep `iter_effects` for questions
    about the PLAYED face, and `iter_effects_top` for questions about the
    unconditional face — the choice is per-question and each spelling says
    which question is being asked, which is this module's whole point.

    The reserved `{op: sly_autoplay}` marker is filtered by `sly_riders`: it
    is a card PLAY rather than an effect list (EB-71 / R174).
    """
    if not isinstance(row, dict):
        yield from iter_effects(row)
        return
    yield from iter_effects(row.get("effects"))
    yield from iter_effects(sly_riders(row))


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
