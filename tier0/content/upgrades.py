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

_DOCS = Path(__file__).parents[2] / "docs"
_GAME_REF = Path(__file__).parents[2] / "game_ref"
UPGRADE_SHEETS = (_DOCS / "klee-upgrades.yaml",
                  _DOCS / "furina-upgrades.yaml")
EXTERNAL_UPGRADE_SHEETS = (_GAME_REF / "ironclad-upgrades.yaml",)
SUFFIX = "+"

# Deltas the engine cannot express per-card yet (constants-encoded).
# catalytic_conversion LEFT this set with R37 (2026-07-20): its upgrade is
# now {innate: true}, which IS sim-expressible -- the R24 no-unmeasured-
# upgrades law is satisfied rather than waived.
UNAPPLIABLE = frozenset({
    "durin_witchs_flame",     # WITCHS_FLAME_DMG is a constant
    "nicole_celestial_gift",  # CELESTIAL_GIFT_BLOCK is a constant
})


@lru_cache(maxsize=1)
def _upgrade_index() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for sheet in (*UPGRADE_SHEETS, *EXTERNAL_UPGRADE_SHEETS):
        if not sheet.exists():
            continue
        entries = yaml.safe_load(sheet.read_text()) or {}
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
            ok = _bump_first((fx for fx in top if fx.get("op") == "damage"
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
        elif key == "draw":
            # ALL draw ops, branches included ("both branches" is sheet law).
            hits = [fx for fx in everywhere if fx.get("op") == "draw"]
            for fx in hits:
                fx["amount"] += val
            ok = bool(hits)
        elif key == "energy":
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") == "energy"), "amount", val)
        elif key == "times":
            ok = _bump_first((fx for fx in everywhere
                              if fx.get("op") == "damage"), "times", val)
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
        elif key == "spark":
            ok = _bump_first((fx for fx in top if fx.get("op") == "gain_spark"),
                             "amount", val)
        elif key == "discard":
            # R36 grammar: moves the chosen-discard count on Crackle's op.
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "discard_for_sparks"),
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
        elif key == "fanfare_cap":
            ok = _bump_first((fx for fx in top
                              if fx.get("op") == "raise_fanfare_cap"),
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
            hit = next((fx for fx in top if fx.get("op")
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
