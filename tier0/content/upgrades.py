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

UNAPPLIABLE lists the sheet entries whose deltas target numbers the
engine encodes as CONSTANTS rather than card fields (Catalytic
Conversion's per-reaction energy, Durin's ping, Nicole's per-turn block).
Those upgrades exist in the design and cannot yet be expressed per-card
in the Tier 0 DSL. They are skipped -- visibly, and the rest policy
refuses to spend a rest on them -- rather than approximated, because a
wrong number wearing the right name is how sim findings stop being
trustworthy. DSL gap, logged for the M7 report.
"""

from __future__ import annotations

import copy
from functools import lru_cache
from pathlib import Path

import yaml

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
                  _DOCS / "ref-ironclad-upgrades.yaml")
EXTERNAL_UPGRADE_SHEETS = (_GAME_REF / "ironclad-upgrades.yaml",
                           _GAME_REF / "silent-upgrades.yaml")
SUFFIX = "+"

# Deltas the engine cannot express per-card yet (constants-encoded).
# catalytic_conversion LEFT this set with R37 (2026-07-20): its upgrade is
# now {innate: true}, which IS sim-expressible -- the R24 no-unmeasured-
# upgrades law is satisfied rather than waived.
# nicole_celestial_gift LEFT this set with G-C2 (2026-07-25), the same way
# catalytic_conversion left it with R37: its delta moved from
# {block_per_turn: +2} -- unexpressible, because CELESTIAL_GIFT_BLOCK is a
# constant rather than a card field -- to {buff: +2}, which the `buff` grammar
# already binds to the first top-level apply_power. The R24 no-unmeasured-
# upgrades law is satisfied rather than waived.
#
# Kept as an empty set rather than deleted, per the standing curated-set
# discipline: the invariant "every draftable card has an applicable upgrade"
# is now asserted positively by tools/lint_upgrade_coverage.py, and the next
# unexpressible delta has somewhere to be named instead of being tolerated
# silently.
UNAPPLIABLE: frozenset[str] = frozenset()


@lru_cache(maxsize=1)
def _upgrade_index() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for sheet in (*UPGRADE_SHEETS, *EXTERNAL_UPGRADE_SHEETS):
        if not sheet.exists():
            continue
        entries = yaml.safe_load(sheet.read_text(encoding="utf-8")) or {}
        dupes = set(entries) & set(merged)
        if dupes:
            raise ValueError(f"{sheet.name}: duplicate upgrade ids {sorted(dupes)}")
        merged.update(entries)
    return merged


def has_upgrade(card_id: str) -> bool:
    """Can this card be upgraded AND can the sim express the result?"""
    delta = _upgrade_index().get(card_id)
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
    """Mutate a (deep-copied) base card into its upgraded form."""
    base_id = card.id
    delta = _upgrade_index().get(base_id)
    if (not isinstance(delta, dict) or not delta
            or "_unexpressible" in delta or base_id in UNAPPLIABLE):
        raise ValueError(f"no applicable upgrade for {base_id!r}")
    card.id = base_id + SUFFIX
    card.name = card.name + SUFFIX

    top = card.effects
    everywhere = list(_iter_effects(top))

    for key, val in delta.items():
        ok = True
        if key == "cost":
            card.cost = max(0, card.cost + val)
        elif key == "remove" and val == "exhaust":
            card.exhaust = False
        elif key == "remove" and val == "self_damage":
            card.effects = [fx for fx in top
                            if not (fx.get("op") == "damage"
                                    and fx.get("target") == "self")]
        elif key == "add":
            card.effects.append(copy.deepcopy(val))
        elif key == "innate":
            # R37 (Catalytic Conversion+): boolean, only True is a ruling.
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
            # Was `fanfare_cap` against raise_fanfare_cap; both retired with
            # the spend/cap grammar ("The Tide Turns", F-A4/F-A5). An upgrade
            # that used to buy ceiling now buys baseline.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "gain_fanfare_floor"),
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
            # Discovery-parity upgrade: the generated card costs 0 this
            # combat (kickoff §9 upgrade grammar).
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
        elif key == "bonus_per_detonation":
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
