"""Upgrade application: local/docs delta sheets -> upgraded Card copies.

Committed character sheets are design artifacts; the real-Ironclad sheet is a
gitignored DLL-derived reference (grammar: docs/upgrade-conventions.md). This
module is only the mechanical applier. An upgraded card is requested as
`<id>+` through loader.get_card, so deck lists stay plain strings and every
existing consumer keeps working.

Delta semantics are PER-KEY, not guessed from values: each key in the
dispatch below names which effect field it moves and how (bump vs
replace). A key this module does not know is a loud error -- the sheet
and the applier drifting apart must fail the suite, not silently ship
un-upgraded cards.

UNAPPLIABLE is the naming slot for sheet entries whose deltas target
numbers the engine encodes as CONSTANTS rather than card fields. It is
EMPTY today and deliberately kept empty rather than deleted (see the set
itself, below, for the history of the three cards that once sat in it and
how each left). The rule it carries is unconditional and does not depend
on the set having members: anything named here is skipped -- visibly, and
the rest policy refuses to spend a rest on it -- rather than
approximated, because a wrong number wearing the right name is how sim
findings stop being trustworthy.
"""

from __future__ import annotations

import copy
from functools import lru_cache
from pathlib import Path

import yaml

from tier0 import constants as C
from tier0.content import local_reference

_DOCS = Path(__file__).parents[2] / "docs"
_GAME_REF = local_reference.game_ref_dir()
UPGRADE_SHEETS = (_DOCS / "klee-upgrades.yaml",
                  _DOCS / "furina-upgrades.yaml",
                  # v0.2 Kokomi sheet pass (2026-07-24): rest-smith needs
                  # upgrade targets or her tier05 runs are structurally
                  # behind. Cross-session note: docs/archive/kokomi-session-worknote.md
                  _DOCS / "kokomi-upgrades.yaml",
                  # Calibration pass (2026-07-24): the ANCHOR had 0/6 pool and
                  # 0/10 starter upgradable while every designed character had
                  # 100%, so rest-smithing, Sand Castle, Yummy Cookie, War
                  # Paint and Whetstone were all dead branches on the very
                  # character the world is calibrated against -- measured 0
                  # upgraded cards and 0 smiths in 300 runs. Real base-game
                  # numbers; the tier 0 battery never upgrades, so the frozen
                  # scorecard and the anchor lock are untouched.
                  _DOCS / "ref-ironclad-upgrades.yaml",
                  # EB-30m / R127: the three Ancients. Registered HERE and
                  # nowhere else, on the ref-ironclad precedent directly
                  # above -- `gen_klee_cards.UPGRADE_SHEETS` names the three
                  # character files and must keep not naming this one, because
                  # the Ancients' C# classes are hand-written and codegen
                  # seeing a delta for them would try to regenerate them.
                  # The Dusty Tome grants its card already upgraded, so for
                  # these three the `+` form is the played card rather than a
                  # smithing option.
                  _DOCS / "ancient-upgrades.yaml")
EXTERNAL_UPGRADE_SHEETS = (_GAME_REF / "ironclad-upgrades.yaml",
                           _GAME_REF / "silent-upgrades.yaml")
SUFFIX = "+"


# =============================================================================
# THE PROTOTYPE-STAGE DEFAULT UPGRADE (EB-283 / EB-277)
# =============================================================================
#
# WHAT WENT WRONG. No prototype row upgraded. Klee's offered none at a campfire
# or a reward (`OnUpgrade` was an empty body under R24's "no ratified delta"
# comment) and Kokomi's upgraded to a card identical to the base (`EB-277`), so
# a run under either arm had no campfire choice at all and the Light Door's
# "Upgrade 2 random cards" did nothing anybody could see.
#
# WHY A RULE AND NOT A SHEET. R24 abolished codegen upgrade DEFAULTS for
# SHIPPED cards, and that stands: a shipped upgrade is a ruled number, and a
# default is how `cant_catch_me` shipped +3 against a ruled +2. A prototype row
# is the opposite kind of object -- the slice packets say in their own sec.1
# that no number in them is a claim, and their sec.7 puts upgrades out of scope
# at Paper. So the choice here is not "ruled number versus default", it is "a
# campfire that does something versus a campfire that does nothing", and a
# stated blanket rule is the honest form of the first. An AUTHORED `upgrade:`
# block on the row always wins, which is how a Balance-stage ruling replaces
# this without the rule having to be removed.
#
# WHERE IT LIVES, AND WHY HERE. Both engines have to apply the SAME deltas or a
# smithed prototype is two different cards. This module is the sim's applier
# and `tools/gen_prototype_cards.py` imports this function for the mod's, so
# there is one implementation and no mirror to keep in step. It reads EFFECTS
# AND COST ONLY -- never the row's `description`, which the sim strips at load
# (loader, EB-215) and therefore cannot see. That is the whole reason the rule
# is written in terms of ops rather than of printed text.
#
# FIVE ARMS, NOT FOUR (2026-09-02). `proto_fr_` is the Furina reframe, which is
# an arm on exactly the terms the other four are -- its own compile property,
# its own switch class, its own slice packet whose sec.1 says no number in it
# is a claim -- so the argument above applies to it unchanged. It is listed
# rather than left out because the alternative is five rows whose campfire
# hands the card back, which is `EB-277` verbatim, and inventing five
# per-row deltas here would be a Balance-stage ruling written by a build.
PROTOTYPE_DEFAULT_PREFIXES = ("proto_ko_", "proto_kk_", "proto_mc_",
                              "proto_mi_", "proto_fr_")

#: The rule, as the `EB-283` row states it, named rather than buried in the
#: walk below.
PROTOTYPE_DAMAGE_DELTA = 3
PROTOTYPE_MULTI_HIT_DAMAGE_DELTA = 1     # +1 PER HIT, the base game's own idiom
PROTOTYPE_BLOCK_DELTA = 3
PROTOTYPE_BOMB_SIZE_DELTA = 2
PROTOTYPE_PAYLOAD_MINE_DELTA = 1
PROTOTYPE_GROW_DELTA = 1
PROTOTYPE_POWER_DELTA = 1
PROTOTYPE_MEND_DELTA = 2
PROTOTYPE_COST_DELTA = -1
PROTOTYPE_COST_FLOOR = 2                 # "a card of cost 2 or more"
PROTOTYPE_ADDED_DRAW = 1                 # the last clause's default, below
PROTOTYPE_PLAN_DRAW_DELTA = 1            # the Plan line's own draw (`EB-315`)

#: THE FLAG/COUNTED SPLIT, in the ONE place both engines read it.
#:
#: A power's `amount` is two different things on two different rows. On
#: `Rally` it is the number the face prints ("Apply 1 Weak"); on
#: `Alice's Recipe` it is a bare ON switch for a rule with no number in it.
#: `_proto_power` told the two apart by `amount > 1`, which is right for every
#: flag and wrong for exactly the counted powers a row happens to print at 1 --
#: so `Rally` and `Exposed Flank` read as "this row prints no number" and got
#: no upgrade at all. [USER] found it from the other end ("Neither does
#: Rally").
#:
#: The set is the base game's own STACKING debuffs and buffs, whose amount is
#: always a count. A mod power is NOT admitted by default: its `amount` is a
#: flag far more often than not, and an entry here has to be a deliberate row
#: rather than a guess, for the same reason `_proto_power`'s doc gives.
COUNTED_POWERS: frozenset[str] = frozenset({
    "weak", "vulnerable", "frail", "strength", "dexterity", "poison",
})


def _proto_hit(effects: list[dict]) -> dict | None:
    """The one effect a prototype `damage` delta binds to.

    The first top-level non-self `damage` carrying a literal amount, else the
    first `set_off` carrying literal damage of its own (`EB-280` made those the
    same number in the same var). A formula-scaled hit has no literal to bump
    and is skipped: `formula_base` is its key, and that is a ruling rather than
    a default.
    """
    hit = next((fx for fx in effects
                if fx.get("op") == "damage" and fx.get("target") != "self"
                and isinstance(fx.get("amount"), int)), None)
    if hit is not None:
        return hit
    return next((fx for fx in effects
                 if fx.get("op") == "set_off"
                 and isinstance(fx.get("damage"), int)
                 and fx["damage"] > 0), None)


def _proto_grow(effects: list[dict]) -> dict | None:
    """The one effect a prototype `grow` delta binds to: the first printed
    grow amount, whichever of the two overhaul ops prints it."""
    return next((fx for fx in effects
                 if (fx.get("op") == "grow_bombs"
                     and isinstance(fx.get("amount"), int))
                 or (fx.get("op") == "merge_bombs"
                     and isinstance(fx.get("growth"), int))), None)


def _proto_power(effects: list[dict]) -> dict | None:
    """The one effect a prototype `power_amount` delta binds to, or None.

    THE `> 1` TEST IS THE LOAD-BEARING PART. A power's `amount` is a printed
    number on some rows (Grounded's 6 Block, Orders' Tide +2, a Garment's 2
    turns) and a bare ON FLAG on others -- Alice's Recipe, Sparks 'n' Splash,
    The Art of War and Treatise all apply `amount: 1` to a power whose whole
    body is a rule with no number in it. Bumping a flag to 2 means nothing at
    best and stacks a rule at worst, and no field on the row tells the two
    apart. So `amount: 1` reads as "this row prints no power number", the row
    falls through to the cost clause, and a Balance-stage `upgrade:` block is
    what gives such a card a real one.

    THE FIRST top-level application is tested and no other, because that is the
    one BOTH appliers bind a `power_amount` delta to (this module's
    `power_amount` branch, and the codegen's `power_upgrade_effect`). Asking
    the question of a later effect would decide the key off one number and
    then move a different one.
    """
    first = next((fx for fx in effects
                  if fx.get("op") in ("apply_power", "buff_next_attack")), None)
    if first is None or not isinstance(first.get("amount"), int):
        return None
    if first["amount"] > 1:
        return first
    # A COUNTED power prints its amount even at 1 (`COUNTED_POWERS`): Rally's
    # "Apply 1 Weak" is a number, Alice's Recipe's `amount: 1` is a switch.
    return first if first.get("power") in COUNTED_POWERS else None


# =============================================================================
# THE PLAN LINE IS A PRINTED LINE TOO (`EB-315`)
# =============================================================================
#
# WHAT WENT WRONG, in [USER]'s words playing the Kokomi arm: *"Plan cards often
# seem to lack upgrades, though (Kurage's Oath, Ambush) - I thought we had a
# test for that?"* The rule above reads a row's `effects:` and nothing else, so
# a Kokomi row whose whole body is its `plan:` line had no printed number the
# rule could see: five of the seven Plan-only rows fell all the way through to
# a clause that withholds ("a row with NO now-line at all"), and the two that
# did get something got it from cost or Exhaust rather than from what the card
# says it does. Worse on the NINE two-line rows, because those looked fine: the
# now-line upgraded and the plan clause kept a literal, so `Feint+` dealt 9
# damage at dawn no matter how often it was smithed.
#
# THE FIX IS THE SAME RULE, RUN TWICE. A Plan line is the second half of a
# printed face -- the same op vocabulary, the same numbers, read by the player
# off the same card -- so it takes the same per-op deltas, under keys prefixed
# `plan_` so a two-line row can move BOTH halves without either applier having
# to guess which line a bare `damage` meant.
#
# WHAT THE PLAN LINE ADDS THAT THE NOW-LINE HAS NOT GOT, and each is one line:
#
#   * `damage_per_companion_last_turn` is a PER-INSTANCE number, so it takes
#     the multi-hit delta (+1) and not the flat one (+3) -- the same reading
#     `_proto_hit` already applies to a `times: N` attack.
#   * `draw` gets a default here and deliberately does NOT get one on the
#     now-line. On a now-line the rule's last clause ADDS a draw, so bumping a
#     printed one would collide with it (`_DEBT_ALREADY_DRAWS`); a Plan line is
#     never the target of that clause, so its printed draw is just a number.
#   * `energy` gets NO default in either place. +1 Energy is a whole turn's
#     tempo and the arm is priced against it; that is a ruling, and the one row
#     that prints it (Battle Plan) reaches a campfire through its draw clause.
#   * `damage_quarter_max_hp` and `plan_twice` print no literal the rule may
#     move (the first has no amount at all, the second is a duration). Both
#     rows that carry them cost 2 and take the cost clause instead.
#
#: Which `plan:` op each `plan_*` key binds to, in order, in the ONE place both
#: appliers read it. Mirrors `apply_upgrade`'s branches below and
#: `gen_klee_cards.PLAN_UPGRADE_VARS`; the three move together or a smithed
#: prototype is two different cards.
PLAN_DELTA_OPS: dict[str, tuple[str, ...]] = {
    "plan_damage": ("damage", "damage_per_companion_last_turn"),
    "plan_block": ("block",),
    "plan_mend": ("mend",),
    "plan_power_amount": ("apply_power",),
    "plan_draw": ("draw",),
}


def _plan_default_delta(plan: list[dict]) -> dict:
    """The Prototype-stage upgrade for one row's `plan:` LINE, or `{}`.

    Pure, and the plan list only. Each key binds to the FIRST clause of its op
    -- the same one-owner rule the now-line keeps -- because both appliers bind
    it there and a key that decided off one clause and moved another would
    upgrade a number the face does not print.
    """
    delta: dict = {}

    hit = _proto_hit(plan)
    if hit is not None:
        delta["plan_damage"] = PROTOTYPE_DAMAGE_DELTA
    elif any(fx.get("op") == "damage_per_companion_last_turn"
             and isinstance(fx.get("amount"), int) for fx in plan):
        # Per COMPANION, so the base game's per-instance idiom (+1) rather
        # than the flat hit delta -- see the block comment above.
        delta["plan_damage"] = PROTOTYPE_MULTI_HIT_DAMAGE_DELTA
    if any(fx.get("op") == "block" and isinstance(fx.get("amount"), int)
           for fx in plan):
        delta["plan_block"] = PROTOTYPE_BLOCK_DELTA
    if any(fx.get("op") == "mend" and isinstance(fx.get("amount"), int)
           for fx in plan):
        delta["plan_mend"] = PROTOTYPE_MEND_DELTA
    if _proto_power(plan) is not None:
        delta["plan_power_amount"] = PROTOTYPE_POWER_DELTA
    if any(fx.get("op") == "draw" and isinstance(fx.get("amount"), int)
           for fx in plan):
        delta["plan_draw"] = PROTOTYPE_PLAN_DRAW_DELTA
    return delta


def prototype_default_delta(card_id: str, cost, effects: list[dict],
                            exhaust: bool = False,
                            plan: list[dict] | None = None) -> dict:
    """The Prototype-stage upgrade for one row, or `{}`.

    Pure, and effects+plan+cost only (see the two block comments above). Empty
    for any id outside `PROTOTYPE_DEFAULT_PREFIXES`, and empty for a row the
    rule finds no printed number on whose cost is below `PROTOTYPE_COST_FLOOR`
    -- the rule's own last clause is "a card of cost 2 or more WITH NO NUMBER
    costs 1 less", so a 0- or 1-cost row with no number has nothing to move and
    gets no upgrade rather than an invented one.

    `EB-315`: BOTH PRINTED LINES ARE WALKED, and the fall-through clauses at
    the bottom fire only when neither printed one. That is the same shape the
    rule always had -- Exhaust and the added draw are what a row with NO number
    gets -- read on the whole face instead of on half of it.
    """
    if not card_id.startswith(PROTOTYPE_DEFAULT_PREFIXES):
        return {}
    delta: dict = {}

    hit = _proto_hit(effects)
    if hit is not None:
        times = hit.get("times", 1)
        delta["damage"] = (PROTOTYPE_MULTI_HIT_DAMAGE_DELTA
                           if isinstance(times, int) and times > 1
                           else PROTOTYPE_DAMAGE_DELTA)
    if any(fx.get("op") == "block" and isinstance(fx.get("amount"), int)
           for fx in effects):
        delta["block"] = PROTOTYPE_BLOCK_DELTA
    bomb = next((fx for fx in effects if fx.get("op") == "plant_bomb"), None)
    if bomb is not None:
        delta["bomb_size"] = PROTOTYPE_BOMB_SIZE_DELTA
        if int(bomb.get("payload_mine_all", 0)) > 0:
            delta["payload_mine"] = PROTOTYPE_PAYLOAD_MINE_DELTA
    if _proto_grow(effects) is not None:
        delta["grow"] = PROTOTYPE_GROW_DELTA
    if _proto_power(effects) is not None:
        delta["power_amount"] = PROTOTYPE_POWER_DELTA
    if any(fx.get("op") == "mend" and isinstance(fx.get("amount"), int)
           for fx in effects):
        delta["mend"] = PROTOTYPE_MEND_DELTA

    # `EB-315`. The row's OTHER printed line, under its own keys.
    delta.update(_plan_default_delta(plan or []))

    # "Spark costs unchanged": `spend_spark` is never a key here, and the
    # clause below reads the ENERGY cost, which is the only cost this rule
    # moves.
    if not delta and isinstance(cost, int) and cost >= PROTOTYPE_COST_FLOOR:
        delta["cost"] = PROTOTYPE_COST_DELTA
    if delta:
        return delta

    # THE TWO LAST CLAUSES, in this order, and both are [USER]'s applied
    # defaults from playing the arm ("'Change of Plans' has no upgrade?").
    # Before them a 0- or 1-cost row printing no number got nothing at all,
    # which is a card whose upgrade slot is a blank rather than a choice.
    #
    #   1. Exhaust comes off. The classic shape, and it is the strongest thing
    #      an upgrade can say about a card whose numbers are all elsewhere.
    #   2. Otherwise the card draws one more.
    #
    # The draw is withheld twice, and neither is a third clause -- both are the
    # codegen refusing to emit something, which is a fact about the rule's
    # reach rather than about its design:
    #
    #   * a row that ALREADY draws. Both appliers bind an added draw to one
    #     `Cards` var, so a second is a collision the codegen names outright
    #     (`delta 'add: draw' on a card with an existing draw`).
    #   * a row with NO now-line at all -- a Kokomi Plan-only card. The added
    #     effect is emitted as an `IsUpgraded`-gated tail on the effects walk,
    #     and such a row has no walk: its whole body is `KokomiPlan.Schedule`.
    #     The delta would declare a `Cards` var nothing reads (which
    #     `lint_generated_structure` L2 says in as many words) and the upgrade
    #     would do nothing. It would also be wrong on its own terms: the row's
    #     target type is the jellyfish ALONE precisely because it does nothing
    #     when played, and a now-line draw would contradict the card's own
    #     printed "Play on the Bake-Kurage."
    #
    # Such a row keeps no default upgrade rather than a generated-wrong one.
    # `EB-315` is why reaching here is now RARE rather than the Plan-only norm:
    # a Plan line's own numbers are read above, so a row only falls this far
    # when NEITHER line prints one -- `damage_quarter_max_hp` and `plan_twice`
    # are the two clauses that can do it, and both rows carrying them cost 2
    # and take the cost clause first. A row that falls all the way through says
    # so on the row, with `no_upgrade:` and a reason, and the surface's gate
    # (`tier0/tests/test_prototype_surface.py`) is what makes that mandatory.
    if exhaust:
        return {"remove": "exhaust"}
    if not effects or any(fx.get("op") == "draw" for fx in effects):
        return {}
    return {"add": {"op": "draw", "amount": PROTOTYPE_ADDED_DRAW}}


def _external_pool_for(sheet: Path) -> Path:
    """The pool an external upgrades sheet rides with (<char>_pool.yaml).

    The deltas name pool card ids, so a game_ref holding only extractor
    output (extract_base_game_pool run, build_official_sheet not yet) must
    read as ABSENT here, exactly as it does in the loader -- otherwise
    has_upgrade says yes to ids get_card cannot resolve.
    """
    return sheet.with_name(sheet.name.split("-")[0] + "_pool.yaml")

# Deltas the engine cannot express per-card yet (constants-encoded).
# catalytic_conversion LEFT this set with R37 (2026-07-20): its upgrade is
# now {innate: true}, which IS sim-expressible -- the R24 no-unmeasured-
# upgrades law is satisfied rather than waived.
# nicole_celestial_gift LEFT this set with G-C2 (2026-07-25), the same way
# catalytic_conversion left it with R37: its delta moved from
# {block_per_turn: +2} -- unexpressible, because CELESTIAL_GIFT_BLOCK is a
# constant rather than a card field -- to {buff: +2}. The R24 no-unmeasured-
# upgrades law is satisfied rather than waived.
#   That {buff: +2} was itself SUPERSEDED on 2026-07-26 by {cost: -1}, ratified
#   with the card's redesign (docs/klee-upgrades.yaml:111-124 records the
#   reason). So the delta named above is history, not the live sheet row, and
#   nothing in the tree binds `buff` for this card any more.
# durin_witchs_flame was never a member under that id in any reachable commit;
# it carries {power_amount: +2} and upgrades normally.
#
# Kept as an empty set rather than deleted, per the standing curated-set
# discipline: the invariant "every draftable card has an applicable upgrade"
# is now asserted positively by tools/lint_upgrade_coverage.py, and the next
# unexpressible delta has somewhere to be named instead of being tolerated
# silently.
UNAPPLIABLE: frozenset[str] = frozenset()


@lru_cache(maxsize=1)
def _shipped_upgrade_index() -> dict[str, dict]:
    """Every delta keyed by SHIPPED card id: the sheets, and nothing else.

    Split out of `_upgrade_index` when `EB-213` gave the prototype surface
    an upgrade channel and, with it, a cycle that only a checkout carrying
    `game_ref/` can reach. See `_upgrade_index` below for the whole shape
    of it; this half is the one a base-game id may be answered from
    without touching a prototype row, which is what breaks the loop.
    """
    merged: dict[str, dict] = {}
    for sheet in (*UPGRADE_SHEETS, *EXTERNAL_UPGRADE_SHEETS):
        if not sheet.exists():
            continue
        if (sheet in EXTERNAL_UPGRADE_SHEETS
                and not _external_pool_for(sheet).exists()):
            continue
        entries = yaml.safe_load(sheet.read_text(encoding="utf-8")) or {}
        dupes = set(entries) & set(merged)
        if dupes:
            raise ValueError(f"{sheet.name}: duplicate upgrade ids {sorted(dupes)}")
        merged.update(entries)
    return merged


@lru_cache(maxsize=1)
def _prototype_upgrade_index() -> dict[str, dict]:
    """The `EB-213` half: deltas carried on a reachable prototype ROW."""
    return _prototype_deltas(_shipped_upgrade_index())


@lru_cache(maxsize=1)
def _upgrade_index() -> dict[str, dict]:
    """Both halves, for every caller that ITERATES the whole index.

    THE TWO HALVES ARE SEPARATE BECAUSE THE MERGED ONE CANNOT BE BUILT ON
    THE PATH THAT ASKS FOR IT. `loader._card_index` folds in the
    gitignored `game_ref/` reference rows, and `_external_cards` asks
    `has_upgrade` of every one of them -- the atomic-coverage rule. Under
    `EB-213` that question built this index, which reads the prototype
    surface through `loader.prototype_cards`, which asks `_card_index`
    for the shipped ids it may not collide with. `_card_index` ->
    `_external_cards` -> `has_upgrade` -> here -> `prototype_cards` ->
    `_card_index`, and `lru_cache` does not memoize a call still in
    flight, so it is unbounded.

    IT IS INVISIBLE WITHOUT `game_ref/`. `_external_cards` returns early
    on a tree that has no reference layer, so CI, every fresh clone and
    every worktree load the content tree cleanly and only the art-bearing
    main checkout raises -- as a `RecursionError` inside PyYAML, naming
    neither end of the cycle. `test_eb213_upgrade_index_reentrancy` is the
    lock, and it fakes the reference layer so a tree without one still
    runs it.

    The repair is that a lookup by id answers from ONE half
    (`_delta_for` below): a `proto_` id from the prototype half, anything
    else from the sheets. `has_upgrade("bash")` therefore never reads a
    prototype row, and the cycle has no first step. This function is the
    union and is for iteration only -- it is not on the `_card_index`
    path and must never be put back on it.
    """
    return {**_shipped_upgrade_index(), **_prototype_upgrade_index()}



def _prototype_deltas(merged: dict[str, dict]) -> dict[str, dict]:
    """Deltas carried ON the row by the quarantined prototype surface.

    `EB-213`. Every sheet above keys its upgrades by shipped card id in a
    `docs/<character>-upgrades.yaml`. The prototype surface keys them on the
    row instead, because R213 B deletes a prototype row WHOLE when its slice
    is accepted or rejected, and a `proto_` key in a shipped upgrades file
    would be a second place to remember. Reading them here is what makes
    `has_upgrade` -- and so the rest-smith and every other upgrade site --
    true of a SUBSTITUTED prototype. Without it the substituted Kurage's Oath
    could not be smithed at all and its ruled upgraded value was prose.

    NOT a hole in the quarantine, and the REACHABILITY filter is what keeps it
    honest rather than a promise. A row is registered here only if some live,
    flagged door already resolves its plain id -- the substitution table, or
    the Spark arm's starter substitution -- because this index is what
    `has_upgrade` answers from and `get_card` must be able to honour every yes
    it gives. On a flag-off tree (which is every shipped tree) no prototype id
    is reachable and none is registered, so the index is byte-identical to
    what it was before EB-213. Nothing here puts a row in `_card_index`:
    pools, rewards, drafts, digests and every version stamp remain
    structurally unable to see one.

    Note the inline `upgrade:` key is DEPRECATED and IGNORED on the shipped
    sheets (R20, `_card_index`) and that is unchanged -- this reads the
    prototype surface and nothing else.
    """
    from tier0.content import loader           # late: loader imports us
    reachable = set(loader._substituted_card_index())
    if C.SPARK_ALT_COST_ENABLED:
        # The Spark arm's own door (`_card_prototype`): with that flag on any
        # `proto_` id resolves, because its starter substitution hands one out
        # by id string.
        reachable |= {c.id for c in loader.prototype_cards()}
    # EB-283. The three OVERHAUL arms open the same door by id -- their whole
    # starter and pool ARE prototype rows -- so a row those flags make
    # reachable is a row a rest site can offer to smith, and it has to have an
    # answer here or the campfire is empty. Same reachability discipline as the
    # two clauses above: on a flag-off tree (every shipped tree) none of these
    # sets contributes and the index is byte-identical to what it was.
    if C.KLEE_OVERHAUL:
        reachable |= set(C.KLEE_OVERHAUL_STARTER_IDS)
        reachable |= set(C.KLEE_OVERHAUL_POOL_IDS)
    if C.KOKOMI_OVERHAUL:
        reachable |= set(C.KOKOMI_OVERHAUL_STARTER_IDS)
        reachable |= set(C.KOKOMI_OVERHAUL_POOL_IDS)
    if C.COMPANION_OVERHAUL:
        reachable |= set(C.MONDSTADT_OVERHAUL_POOL_IDS)
        reachable |= set(C.INAZUMA_OVERHAUL_POOL_IDS)
        # The stand-ins are in NO pool by design (see `COMPANION_STANDIN_IDS`),
        # and they are still REACHABLE: the hand-off puts one in a deck, and a
        # card in a deck must have a campfire answer like any other.
        reachable |= set(C.COMPANION_STANDIN_IDS)
    deltas: dict[str, dict] = {}
    for card in loader.prototype_cards():
        if card.id not in reachable:
            continue
        # EB-315: the row's own OPT-OUT wins over everything, including the
        # rule -- a row that says it cannot upgrade must not be smithable in
        # one engine and base-only in the other.
        if getattr(card, "no_upgrade", None):
            continue
        # EB-283: the row's own block wins; the Prototype rule fills in for a
        # row that has none, so a staged card is never un-smithable for want
        # of a number nobody has ruled yet.
        authored = dict(card.upgrade) if card.upgrade else {}
        delta = authored or prototype_default_delta(
            card.id, card.cost, card.effects,
            bool(getattr(card, "exhaust", False)),
            list(getattr(card, "plan", None) or []))
        if not delta:
            continue
        if card.id in merged:
            raise ValueError(
                f"prototype row {card.id!r} carries an `upgrade:` block and "
                "an upgrades sheet already rules that id -- one id, one delta")
        deltas[card.id] = delta
    return deltas


def has_upgrade(card_id: str, *, shipped_only: bool = False) -> bool:
    """Can this card be upgraded AND can the sim express the result?

    An enchantment mark is looked PAST (R82 reopened): enchanting a card
    never costs it its upgrade path, and the two decorations compose in
    either order (see content/enchantments.py).

    `shipped_only` ANSWERS FROM THE SHEETS AND NEVER READS A PROTOTYPE ROW,
    and it has exactly one caller: `loader._external_cards`, which asks this
    of every gitignored `game_ref/` row to enforce the atomic-coverage rule.
    Those ids are base-game ids and can never be prototype ones, so the
    answer is identical -- what the flag buys is that the question does not
    build `_upgrade_index`'s prototype half, which reads the surface through
    `loader.prototype_cards`, which asks `_card_index` for the shipped ids it
    may not collide with, which is the caller. See `_upgrade_index` for the
    whole cycle and why no checkout without `game_ref/` can see it.
    """
    from tier0.content import enchantments      # late: enchantments imports us
    card_id = enchantments.split(card_id)[0]
    delta = (_shipped_upgrade_index().get(card_id) if shipped_only
             else _upgrade_index().get(card_id))
    return (isinstance(delta, dict)
            and bool(delta)
            and "_unexpressible" not in delta
            and card_id not in UNAPPLIABLE
            and not card_id.endswith(SUFFIX))


def _iter_effects(effects: list[dict]):
    for fx in effects:
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                yield from _iter_effects(fx[branch])


def _bump_first(candidates, field: str, delta: int) -> bool:
    for fx in candidates:
        if field in fx and isinstance(fx[field], int):
            fx[field] += delta
            return True
    return False


def apply_upgrade(card) -> "Card":  # noqa: F821 - avoids circular import
    """Mutate a (deep-copied) base card into its upgraded form.

    The enchantment mark is looked PAST and then put back, which is the same
    rule `has_upgrade` above states and the reason the two are read together:
    `has_upgrade` learned it when R82 reopened and this did not, so from
    RUNTEMPLATE 10 -- when enchantments entered the run layer and enchanted
    cards started reaching upgrade sites -- the pair disagreed about the same
    card. `has_upgrade("x@sharp-2")` answered True off the plain row while
    this looked up the decorated id, missed, and raised "no applicable
    upgrade". `_best_upgrade_target` scores its candidates by calling this,
    so an Ironclad hand holding one enchanted upgradable card killed the run.
    """
    from tier0.content import enchantments      # late: enchantments imports us
    base_id, mark, amount = enchantments.split(card.id)
    delta = _upgrade_index().get(base_id)
    if (not isinstance(delta, dict) or not delta
            or "_unexpressible" in delta or base_id in UNAPPLIABLE):
        raise ValueError(f"no applicable upgrade for {base_id!r}")
    upgraded = base_id + SUFFIX
    # `decorate` re-attaches the mark INSIDE the suffix (`x@sharp-2+`), which
    # is the one spelling `split` round-trips; rebuilding it here by hand is
    # how the two decorations drift apart.
    card.id = (enchantments.decorate(upgraded, mark, amount) if mark
               else upgraded)
    card.name = card.name + SUFFIX

    top = card.effects
    everywhere = list(_iter_effects(top))

    for key, val in delta.items():
        ok = True
        if key == "cost":
            card.cost = max(0, card.cost + val)
        elif key == "remove" and val == "exhaust":
            card.exhaust = False
        elif key == "remove" and val == "ethereal":
            # EB-118: the mined "Remove Ethereal" keyword upgrade (n=13,
            # docs/upgrade-conventions.md row 4) -- the base card carries the
            # downside and the upgrade BUYS IT OFF, which is why it removes
            # rather than adding a number. Canon precedent: Apparition,
            # EchoForm and VoidForm all `RemoveKeyword(CardKeyword.Ethereal)`
            # in OnUpgrade and change nothing else.
            #
            # Guarded where `remove: exhaust` above is not: the key is new, so
            # there is no row to grandfather, and a delta that removes a
            # keyword the card never printed is a sheet error that must fail
            # here rather than generate an upgraded copy identical to its base.
            # The FIELD only. The `tags: [ethereal]` spelling belongs to
            # Statuses, Curses and tokens, whose rarities are outside
            # RARITY_ODDS and which therefore have no upgrade path at all.
            ok = card.ethereal
            card.ethereal = False
        elif key == "remove" and val == "self_damage":
            card.effects = [fx for fx in top
                            if not (fx.get("op") == "damage"
                                    and fx.get("target") == "self")]
        elif key == "add":
            # APPEND is the default and is what every rider row wants: a
            # `{draw: 1}` or `{gain_encore: 2}` bought by the upgrade reads
            # last on the face and resolves last.
            #
            # `add_before` (below) is for the one shape append cannot spell:
            # an upgrade whose new line resolves in the MIDDLE of the ruled
            # body. send_the_runner+ is ruled "draw 2 -> discard 1 chosen ->
            # exhaust 1 chosen" ([USER], D2a), and an append loaded it as
            # draw/exhaust/discard -- the player exhausted before being asked
            # what to throw, which is a different card.
            #
            # It names the OP it must precede rather than an index, so a
            # later edit to the base body cannot silently slide the insertion
            # somewhere else: the op is either still there (insert before it)
            # or it is not (ok stays False and the applier raises).
            before = delta.get("add_before")
            if before is None:
                card.effects.append(copy.deepcopy(val))
            else:
                at = next((i for i, e in enumerate(top)
                           if e.get("op") == before), None)
                ok = at is not None
                if ok:
                    card.effects.insert(at, copy.deepcopy(val))
        elif key == "add_before":
            # Position modifier for `add`, consumed by the branch above. It
            # is validated and applied there, so all this branch owes is
            # order-independence: sheet key order must not decide whether the
            # position is honoured.
            ok = "add" in delta and isinstance(val, str)
        elif key == "innate":
            # R37 (Catalytic Converter+): boolean, only True is a ruling.
            if val is not True:
                raise ValueError(f"innate delta on {base_id!r} must be true")
            card.innate = True
        elif key == "retain":
            if val is not True:
                raise ValueError(f"retain delta on {base_id!r} must be true")
            card.retain = True
        elif key == "condition" and val == "unconditional":
            # Hoist the conditional's then-branch into the effect list.
            out = []
            for fx in top:
                if fx.get("op") == "conditional":
                    out.extend(fx.get("then", []))
                else:
                    out.append(fx)
            card.effects = out
        elif key == "damage":
            # chain_attack is a damage op whose repeat count is decided by
            # the kills it scores, so its printed number upgrades like any
            # other attack's.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") in ("damage", "chain_attack")
                              and fx.get("target") != "self"), "amount", val)
            if not ok:
                # EB-280 / EB-283: a Set off Attack's own hit is card damage
                # in the same slot and the same var, so a `damage` delta lands
                # on it when the row has no plain damage op (Ka-pow!). The
                # codegen binds it the same way round -- plain damage first --
                # so the two engines cannot upgrade different numbers.
                ok = _bump_first((fx for fx in top
                                  if fx.get("op") == "set_off"
                                  and int(fx.get("damage", 0) or 0) > 0),
                                 "damage", val)
        elif key == "bomb_size":
            # EB-283, the overhaul Bomb's printed size (`plant_bomb.size`).
            # Distinct from `bomb_damage`, which is the SHIPPED Bomb's
            # `place_bomb.bomb_damage` -- two ops, two fields, two arms.
            ok = _bump_first((fx for fx in top if fx.get("op") == "plant_bomb"),
                             "size", val)
        elif key == "payload_mine":
            ok = _bump_first((fx for fx in top if fx.get("op") == "plant_bomb"),
                             "payload_mine_all", val)
        elif key == "grow":
            # One key, two ops: `grow_bombs.amount` and `merge_bombs.growth`
            # are both "how much the Bombs grow", and a row carries at most
            # one of them.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "grow_bombs"), "amount", val)
            if not ok:
                ok = _bump_first((fx for fx in top
                                  if fx.get("op") == "merge_bombs"),
                                 "growth", val)
        elif key == "mend":
            ok = _bump_first((fx for fx in top if fx.get("op") == "mend"),
                             "amount", val)
        elif key in PLAN_DELTA_OPS:
            # `EB-315`. The PLAN line's own numbers, one key per op, bound to
            # the FIRST clause of that op -- the same one-owner rule every key
            # above keeps, and the same one `gen_klee_cards.plan_var_effects`
            # keeps on the other side, so both engines move the same clause.
            #
            # `plan` and not `everywhere`: a Plan line is a flat list of typed
            # clauses by construction (`kokomi_plan.plan_shape_reason` refuses
            # anything else), so there are no branches to reach into and a
            # nested spelling would be a row neither engine can load.
            plan_line = list(getattr(card, "plan", None) or [])
            ok = False
            for plan_op in PLAN_DELTA_OPS[key]:
                ok = _bump_first((fx for fx in plan_line
                                  if fx.get("op") == plan_op), "amount", val)
                if ok:
                    break
        elif key == "block":
            ok = _bump_first((fx for fx in top if fx.get("op") == "block"),
                             "amount", val)
        elif key == "conditional_block":
            hits = [fx for fx in everywhere
                    if fx.get("op") == "block"
                    and isinstance(fx.get("amount"), int)]
            for fx in hits:
                fx["amount"] += val
            ok = bool(hits)
        elif key == "heal":
            ok = _bump_first((fx for fx in top if fx.get("op") == "heal"),
                             "amount", val)
        elif key == "cards":
            # The COUNT on an add_card op -- "create N more of the token".
            # Distinct from `draw` because creating a card and drawing one
            # are different resources: a created token adds to the deck's
            # total, a drawn one does not.
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") == "add_card"), "amount", val)
        elif key == "created_upgraded":
            # HiddenDaggers+ / StormOfSteel+: the tokens they create arrive
            # upgraded. Boolean, and only True is a ruling -- the same shape
            # `innate` and `retain` use.
            if val is not True:
                raise ValueError(
                    f"created_upgraded delta on {base_id!r} must be true")
            hits = [fx for fx in everywhere if fx.get("op") == "add_card"]
            for fx in hits:
                fx["upgraded"] = True
            ok = bool(hits)
        elif key == "autoplay_upgrade_first":
            # KnifeTrap+: upgrade each card before auto-playing it.
            if val is not True:
                raise ValueError(
                    f"autoplay_upgrade_first delta on {base_id!r} must be true")
            hits = [fx for fx in everywhere
                    if fx.get("op") == "autoplay_from_exhaust"]
            for fx in hits:
                fx["upgrade_first"] = True
            ok = bool(hits)
        elif key == "draw":
            # ALL draw ops, branches included ("both branches" is sheet law).
            # draw_to_hand_size counts: Expertise's upgrade raises the hand
            # size it draws TO, which is the same var on the same op family.
            hits = [fx for fx in everywhere
                    if fx.get("op") in ("draw", "draw_to_hand_size")]
            for fx in hits:
                fx["amount"] += val
            ok = bool(hits)
        elif key == "draw_and_discard":
            # ONE DynamicVar read by two ops (Prepared: draw N, discard N).
            # Bumping only one of them would upgrade half a card, so this
            # key exists to make "the same number, in both places" sayable.
            # Requires BOTH -- a row with only one of the ops is a
            # mis-derived key, not a partial success.
            draws = [fx for fx in everywhere if fx.get("op") == "draw"]
            discards = [fx for fx in everywhere if fx.get("op") == "discard"]
            for fx in draws + discards:
                fx["amount"] += val
            ok = bool(draws) and bool(discards)
        elif key == "x_plus":
            # An X-cost card whose upgrade adds to the value X resolves to
            # (Malaise: `if (IsUpgraded) powerAmount++`). Every X-reading
            # amount on the row moves together, sign preserved -- the card
            # spends one number in two places and the upgrade must not be
            # able to split them.
            hits = []
            for fx in everywhere:
                amt = fx.get("amount")
                if not isinstance(amt, str):
                    continue
                sign, body = ("-", amt[1:]) if amt.startswith("-") else ("", amt)
                if body == "X":
                    fx["amount"] = f"{sign}X_plus_{val}"
                elif body.startswith("X_plus_"):
                    n = int(body[len("X_plus_"):]) + val
                    fx["amount"] = f"{sign}X_plus_{n}"
                else:
                    continue
                hits.append(fx)
            ok = bool(hits)
        elif key == "energy":
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") == "energy"), "amount", val)
        elif key == "times":
            # BouncingFlask repeats an apply_power, not a damage op -- the
            # RepeatVar is the same var class either way.
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") in ("damage", "apply_power")),
                             "times", val)
        elif key == "conditional_damage":
            hits = [fx for fx in everywhere
                    if fx.get("op") == "damage"
                    and fx.get("target") != "self"
                    and isinstance(fx.get("amount"), int)]
            for fx in hits:
                fx["amount"] += val
            ok = bool(hits)
        elif key == "formula_per":
            hit = next((fx for fx in everywhere
                        if fx.get("op") == "damage"
                        and isinstance(fx.get("amount_formula"), dict)
                        and isinstance(fx["amount_formula"].get("per"), int)),
                       None)
            ok = hit is not None
            if hit:
                hit["amount_formula"]["per"] += val
        elif key == "formula_base":
            # The BASE term of an amount_formula: `base + per * count`. Added
            # by F4 (Neap Tide addendum) because only `formula_per` existed,
            # and the two are not interchangeable design decisions. A count
            # that is uncapped and only grows -- the exhaust pile, exactly the
            # shape R80 makes dangerous on Charge -- makes bumping `per` a
            # resource-curve move on an unbounded quantity, while bumping
            # `base` pays on turn one and stops. Both are legitimate; which one
            # a card takes is a ruling, and before this key the tooling made
            # that ruling by having only one option.
            hit = next((fx for fx in everywhere
                        if fx.get("op") == "damage"
                        and isinstance(fx.get("amount_formula"), dict)
                        and isinstance(fx["amount_formula"].get("base"), int)),
                       None)
            ok = hit is not None
            if hit:
                hit["amount_formula"]["base"] += val
        elif key == "target_power_per":
            hit = next((fx for fx in everywhere
                        if fx.get("op") == "damage"
                        and isinstance(fx.get("bonus_per_target_power"), dict)
                        and isinstance(
                            fx["bonus_per_target_power"].get("per"), int)),
                       None)
            ok = hit is not None
            if hit:
                hit["bonus_per_target_power"]["per"] += val
        elif key == "damage_growth":
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") == "grow_damage"),
                             "amount", val)
        elif key == "on_exhaust_energy":
            ok = card.on_exhaust_energy > 0
            card.on_exhaust_energy += val
        elif key == "max_hp":
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") == "gain_max_hp"),
                             "amount", val)
        elif key == "upgrade_scope":
            if val != "all":
                raise ValueError(
                    f"upgrade_scope on {base_id!r} must be 'all'")
            hit = next((fx for fx in everywhere
                        if fx.get("op") == "upgrade_in_hand"), None)
            ok = hit is not None
            if hit:
                hit["scope"] = val
        elif key == "exhaust_select":
            if val != "chosen":
                raise ValueError(
                    f"exhaust_select on {base_id!r} must be 'chosen'")
            hit = next((fx for fx in everywhere
                        if fx.get("op") == "exhaust_from"), None)
            ok = hit is not None
            if hit:
                hit["select"] = val
        elif key == "exhaust":
            # How many cards an `exhaust_from` takes. F4 (Neap Tide addendum)
            # is the first card to use it, and adding it here closed a gap
            # rather than opened one: gen_klee_cards.exhaust_upgrade has read
            # `exhaust: +N` off the upgrade sheets since the Kokomi codegen
            # landed, and NOTHING on the sim side applied it. The key was live
            # in C# and dead in Python -- so the first card to take it would
            # have upgraded in the mod and not in the simulator, silently, and
            # every measurement of that upgrade would have been of the wrong
            # card. Same defect class as the `energy` upgrade the F batch
            # caught, one layer further out.
            hit = next((fx for fx in everywhere
                        if fx.get("op") == "exhaust_from"), None)
            ok = hit is not None
            if hit:
                hit["amount"] = hit.get("amount", 1) + val
                # The random branch cannot express amount > 1 in C# (the
                # re-pooling loop was never built), so an upgrade that raises
                # the count on a random exhaust would ship a card the mod
                # cannot render. Fail here rather than at generation time,
                # where the card would simply be blocked with a vague reason.
                if hit.get("amount", 1) > 1 and hit.get("select") != "chosen":
                    raise ValueError(
                        f"exhaust delta on {base_id!r} raises a RANDOM "
                        "exhaust_from above 1; only the chosen branch is "
                        "expressible in C#")
        elif key == "spark":
            ok = _bump_first((fx for fx in top if fx.get("op") == "gain_spark"),
                             "amount", val)
        elif key == "kit_spark":
            # EB-219 / LAW:145. The upgrade of a PERSONAL COMPANION whose Spark
            # grant lives in its owner's kit rather than on its face. There is
            # nothing on the face to bump -- that is the point of the clause --
            # so this key applies NO effect delta and is not a silent no-op
            # either: the engine expresses it at play time by reading the
            # upgraded flag (effects.klee_personal_companion_spark), the same
            # shape the `condition` key uses, and the codegen emits the matching
            # play-time comment rather than flagging a missing upgrade path.
            #
            # THE VALUE IS CHECKED RATHER THAN TRUSTED. The sheet number and the
            # engine constant are two writings of one fact, and a sheet that
            # said +2 while the kit minted +1 would be exactly the class of
            # defect this file's `exhaust` branch was added to stop (a key live
            # in one engine and dead in the other). So the row must name a card
            # the kit actually reaches, and must agree with the constant.
            if card.personal_pool is None:
                raise ValueError(
                    f"upgrade {base_id!r}: key 'kit_spark' is only meaningful "
                    "on a personal_pool companion -- no kit declares a trigger "
                    "for a shared row")
            if val != C.KLEE_COMPANION_SPARK_UPGRADED_BONUS:
                raise ValueError(
                    f"upgrade {base_id!r}: kit_spark {val:+d} disagrees with "
                    "KLEE_COMPANION_SPARK_UPGRADED_BONUS "
                    f"{C.KLEE_COMPANION_SPARK_UPGRADED_BONUS:+d}; the sheet and "
                    "the kit are two writings of one number")
        elif key == "discard":
            # R36 grammar: moves the chosen-discard count on Crackle's op.
            #
            # G6 (Neap Tide v2.1) extends it to the PLAIN `discard` op, which
            # Kokomi's Sly lane uses and Klee's Spark lane does not. Ordered,
            # not merged: `discard_for_sparks` is tried first so every Klee
            # card keeps binding exactly where it always did, and the plain op
            # is the fallback. No card carries both ops today, so the order is
            # a guarantee rather than a tiebreak -- but it is written as an
            # order anyway, because a future card carrying both should move
            # the Spark op (where the discard is priced against Sparks) and
            # not silently start moving a bare discard count instead.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "discard_for_sparks"),
                             "amount", val)
            if not ok:
                ok = _bump_first((fx for fx in top
                                  if fx.get("op") == "discard"),
                                 "amount", val)
        elif key == "sparks":
            # R36 grammar: moves the Spark cap on the SAME op ("discard 2,
            # add 2 Sparks"). Distinct from "spark" (gain_spark) on purpose:
            # these Sparks stay priced by the discard count.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "discard_for_sparks"),
                             "sparks", val)
        elif key == "encore":
            # ALL gain_encore ops, branches included (mirrors "draw": a
            # conditional Encore rider is still the card's Encore story).
            hits = [fx for fx in everywhere if fx.get("op") == "gain_encore"]
            for fx in hits:
                fx["amount"] += val
            ok = bool(hits)
        elif key == "encore_cost":
            ok = card.encore_cost > 0
            card.encore_cost = max(0, card.encore_cost + val)
        elif key == "fanfare_floor":
            # The "Fanfare +X" keyword's upgrade. Once retired in favour of
            # `fanfare_cap` and back again: the cap grammar died with F-A4/F-A5
            # and the floor replaced it, and the Fanfare rework (Track B,
            # 2026-07-28) brought the cap back as the OTHER keyword, so both
            # keys are now live and they are NOT interchangeable -- one buys
            # baseline, one buys headroom, and a card prints exactly one.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "gain_fanfare_floor"),
                             "amount", val)
        elif key == "fanfare_cap":
            # The "Fanfare Cap +X" keyword's upgrade (Track B, 2026-07-28).
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "raise_fanfare_cap"),
                             "amount", val)
        elif key == "floor_drop":
            # The Hyperbeam's price (Track C.2, 2026-07-28). NEGATIVE deltas
            # are the normal direction here -- the upgrade makes the hole
            # SHALLOWER -- which is why it needs its own key rather than
            # riding a generic amount bump whose sign convention says
            # "bigger is better".
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "crash_fanfare"),
                             "amount", val)
        elif key == "block_next_turn":
            # The Charlotte-precedent second half. `block` deliberately hits
            # only the first op, so a card whose upgrade moves BOTH halves
            # (Sayu's daruma) needs this to say so explicitly.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "block_next_turn"),
                             "amount", val)
        elif key == "kurage_turns":
            # v0.4: Bake-Kurage+ keeps the jellyfish out longer. Duration is
            # the ONLY thing an upgrade may move here -- the pulse numbers
            # are constants, and the +1 Charge is untouchable under the
            # resource-curve law (upgrades never move Charge/conscript).
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "summon_kurage"),
                             "amount", val)
        elif key == "generate_cost_override":
            # Discovery-parity upgrade: the generated card costs 0 THIS TURN
            # (R114 / FLAG-2(ii): effects.py owns the lifetime and the mod's
            # SetThisTurn was ruled the correct leg; "this combat" here was
            # the drifted claim).
            hit = next((fx for fx in top
                        if fx.get("op") == "generate_guest_star"), None)
            ok = hit is not None
            if hit:
                hit["cost_override"] = val
        elif key == "generated":
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "generate_guest_star"),
                             "amount", val)
        elif key == "burst_energy":
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "burst_energy"),
                             "amount", val)
        elif key in ("weak", "vulnerable"):
            word = "vuln" if key == "vulnerable" else "weak"
            ok = _bump_first((fx for fx in top if fx.get("op") == "apply_power"
                              and word in fx.get("power", "")), "amount", val)
        elif key == "kurage_ward":
            # R130 (2026-08-07): at ward 5 the Oath's upgrade sells the +2 the
            # ruling prints, so the delta needs a key. NAME-MATCHED like weak /
            # vulnerable rather than routed through the generic `power_amount`:
            # the ward is a named quantity in this card's coupling pin (value
            # = ward x pulses per play), and a delta that says which power it
            # moves cannot land on the wrong apply_power if the row ever grows
            # a second one.
            ok = _bump_first((fx for fx in top if fx.get("op") == "apply_power"
                              and fx.get("power") == "kurage_ward"),
                             "amount", val)
        elif key in ("power_amount", "amp_percent", "splash_damage",
                     "duration", "buff"):
            # `everywhere`, not `top`: a power applied inside a conditional
            # is still the card's only power application, and the base game
            # upgrades its DynamicVar the same way either side of the branch.
            # Added 2026-07-27 for the Silent's Bubble Bubble ("if the target
            # is Poisoned, apply Poison"), whose whole effect is nested.
            # Top-level is still preferred so a card with both is unchanged.
            hit = next((fx for fx in top if fx.get("op")
                        in ("apply_power", "buff_next_attack")), None)
            if hit is None:
                hit = next((fx for fx in everywhere if fx.get("op")
                            in ("apply_power", "buff_next_attack")), None)
            ok = hit is not None
            if hit:
                # Single-application powers encode max_stacks == amount
                # (the cap is in POWER UNITS — pass-2 fix; a stale cap
                # would silently swallow the upgrade).
                if hit.get("max_stacks") == hit["amount"]:
                    hit["max_stacks"] += val
                hit["amount"] += val
        elif key in ("bonus", "bonus_vs_bombed", "bomb_damage"):
            ok = _bump_first(everywhere, key, val)   # field name == key
        elif key == "conditional_bonus":
            cond = next((fx for fx in top if fx.get("op") == "conditional"),
                        None)
            ok = bool(cond) and _bump_first(
                (fx for fx in cond["then"]
                 if fx.get("op") in ("damage", "block")), "amount", val)
        elif key == "chance":
            hit = next((fx for fx in everywhere if "chance" in fx), None)
            ok = hit is not None
            if hit:
                hit["chance"] = val                      # replace, not bump
        elif key == "cards":
            ok = _bump_first((fx for fx in top if fx.get("op") == "add_card"),
                             "amount", val)
        elif key == "copy_cost_override":
            hit = next((fx for fx in top
                        if fx.get("op") in ("copy_companion_in_hand",
                                            "copy_spotlighted_in_hand")), None)
            ok = hit is not None
            if hit:
                hit["cost_override"] = val
        elif key == "bombs":
            hit = next((fx for fx in top if fx.get("op") == "place_bomb"
                        and isinstance(fx.get("amount"), str)), None)
            ok = hit is not None
            if hit:                                      # X_plus_1 -> X_plus_2
                n = int(hit["amount"].rsplit("_", 1)[1])
                hit["amount"] = f"X_plus_{n + val}"
        elif key in ("bonus_per_detonation", "bonus_slope"):
            # One implementation, two names. `bonus_per_detonation` was named
            # for its only user when it was written and is in fact generic --
            # it steepens whatever bonus_formula the card carries. Rather than
            # rename it and churn every Klee upgrade row, `bonus_slope` is the
            # name new rows use (Fanfare rework Track C.3, 2026-07-28), and
            # the old name stays valid for the rows already written against it.
            hit = next((fx for fx in top if "bonus_formula" in fx), None)
            ok = hit is not None
            if hit:
                n, _, rest = hit["bonus_formula"].partition("_per_")
                hit["bonus_formula"] = f"{int(n) + val}_per_{rest}"
        else:
            raise ValueError(
                f"upgrade sheet key {key!r} on {base_id!r} is unknown to the "
                f"applier -- extend the dispatch or fix the sheet")
        if not ok:
            raise ValueError(
                f"upgrade {base_id!r}: key {key!r} found no matching effect")
    return card
