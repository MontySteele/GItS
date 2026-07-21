#!/usr/bin/env python3
"""Parity lint: hand-written C# cards vs the ratified sheets.

Hand-written cards bypass R24's enforcement entirely: gen_klee_cards.py
guarantees generated cards match docs/klee-cards.yaml + docs/klee-upgrades.yaml
BY CONSTRUCTION, but a hand-written card's numbers live in two places with no
automated bridge. That is the exact drift class R24 abolished for generated
cards (cant_catch_me shipped +3 block against a ratified +2), one enforcement
layer short. The R23 batch was verified by hand once; this lint is that
verification, made permanent.

How it works, per card in gen_klee_cards.HAND_WRITTEN:
  sheet side -- per-op rules turn the card's effects into expected numbers:
    the multiset of DynamicVar base values, the multiset of extra hit counts,
    and the energy cost; klee-upgrades.yaml gives the expected upgrade deltas.
  C# side -- the standard idioms are regex-extracted from the card file:
    `new XxxVar(Nm...)` / `new DynamicVar("Name", Nm)`, `.WithHitCount(N)`,
    `: base(N, CardType...)`, `.UpgradeValueBy(Nm)`, `EnergyCost.UpgradeBy(N)`.
  Mismatch in any category is a finding; any finding exits 1.

UNPARSEABLE discipline (tier0's UNAPPLIABLE, applied to linting): an op,
field, or upgrade key without a parity rule FAILS LOUDLY naming itself --
never a silent skip. Adding a hand-written card with a new mechanic forces
extending this lint, which is the point: every future hand-written card (the
Burst and power cards are coming) inherits the gate.

Run: python tools/lint_handwritten_parity.py   (needs the repo venv: pyyaml)
Wired into klee-mod/build/validate.ps1 (S6), so it gates deploy.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_klee_cards as gen  # HAND_WRITTEN, pascal(), sheet paths

CARDS_DIR = gen.REPO / "klee-mod" / "KleeCode" / "Cards"

# --------------------------------------------------------------------------
# Sheet side: per-op rules -> expected numbers
# --------------------------------------------------------------------------

# Keys that may appear on an effect without carrying a number we must check.
IGNORABLE_KEYS = {"op", "target", "if", "note", "zone"}


class Unparseable(Exception):
    """A sheet construct with no parity rule. Always a loud failure."""


def walk_effects(effects: list, exp_vars: list, exp_hits: list) -> None:
    for eff in effects:
        op = eff.get("op")
        keys = set(eff) - IGNORABLE_KEYS - {"op"}

        if op == "damage":
            exp_vars.append(int(eff["amount"]))
            keys.discard("amount")
            for bonus in ("bonus_vs_aura", "bonus_vs_bombed"):
                if bonus in eff:
                    exp_vars.append(int(eff[bonus]))
                    keys.discard(bonus)
            times = eff.get("times", 1)
            keys.discard("times")
            if not isinstance(times, int):
                raise Unparseable(f"damage times '{times}' is not a literal int")
            if times != 1:
                exp_hits.append(times)
        elif op == "block":
            exp_vars.append(int(eff["amount"]))
            keys.discard("amount")
        elif op == "place_bomb":
            exp_vars.append(int(eff["bomb_damage"]))
            keys.discard("bomb_damage")
            # A multi-bomb placement is a loop count in code, not a DynamicVar;
            # nothing reliable to extract. Only the 1-bomb shape has a rule.
            if eff.get("amount", 1) != 1:
                raise Unparseable("place_bomb amount != 1 (loop count is not extractable)")
            keys.discard("amount")
        elif op == "draw":
            if "amount_formula" in eff:
                keys.discard("amount_formula")  # formula-driven: no literal var
            else:
                exp_vars.append(int(eff["amount"]))
                keys.discard("amount")
        elif op == "gain_spark":
            exp_vars.append(int(eff["amount"]))
            keys.discard("amount")
        elif op == "conditional":
            walk_effects(eff.get("then", []), exp_vars, exp_hits)
            walk_effects(eff.get("else", []), exp_vars, exp_hits)
            keys -= {"then", "else"}
        elif op == "apply_power":
            # Power amount -> a DynamicVar on the card (generated cards emit
            # "PowerAmount"; hand-written sparks_n_splash follows the idiom).
            # power/max_stacks/splash_procs_per_turn carry no card-side
            # number -- caps are enforced in the power class and cross-checked
            # by gen_klee_cards' APPLY_POWERS registry.
            exp_vars.append(int(eff["amount"]))
            keys -= {"amount", "power", "max_stacks", "splash_procs_per_turn"}
        elif op == "refresh_all_auras":
            pass  # no numbers
        else:
            raise Unparseable(f"op '{op}' has no parity rule")

        if keys:
            raise Unparseable(f"op '{op}' has unhandled field(s) {sorted(keys)}")


def expected_upgrade(delta: dict | None) -> tuple[list[int], int | None]:
    """(multiset of UpgradeValueBy deltas, cost delta or None)."""
    if not delta:
        return [], None
    values, cost = [], None
    for key, value in delta.items():
        if key == "cost":
            cost = int(value)
        elif isinstance(value, int):
            values.append(value)
        else:
            raise Unparseable(f"upgrade key '{key}: {value}' is structural (no parity rule)")
    return values, cost


# --------------------------------------------------------------------------
# C# side: idiom extraction
# --------------------------------------------------------------------------

VAR_RE = re.compile(r'new\s+[A-Z]\w*Var\(\s*(\d+(?:\.\d+)?)m?\b')
NAMED_VAR_RE = re.compile(r'new\s+DynamicVar\("\w+",\s*(\d+(?:\.\d+)?)m?\)')
COST_RE = re.compile(r':\s*base\(\s*(\d+)\s*,')
HIT_RE = re.compile(r'\.WithHitCount\(\s*(\d+)\s*\)')
UPG_RE = re.compile(r'\.UpgradeValueBy\(\s*(\d+(?:\.\d+)?)m\s*\)')
COST_UPG_RE = re.compile(r'EnergyCost\.UpgradeBy\(\s*(-?\d+)\s*\)')


def extract_cs(text: str) -> dict:
    return {
        "vars": [int(float(v)) for v in VAR_RE.findall(text) + NAMED_VAR_RE.findall(text)],
        "cost": [int(c) for c in COST_RE.findall(text)],
        "hits": [int(h) for h in HIT_RE.findall(text)],
        "upgrade_vars": [int(float(v)) for v in UPG_RE.findall(text)],
        "upgrade_cost": [int(c) for c in COST_UPG_RE.findall(text)],
        # Burst-energy spike: sheet `skill_tag` must land as the ISkillTagCard
        # marker or the card silently generates no burst energy.
        "skill_tag": "ISkillTagCard" in text,
        # Keyword sprint: skill_tag must ALSO land as the ElementalSkill
        # display keyword (playtest finding: the tag was invisible on cards).
        "skill_kw": "KleeKeywords.ElementalSkill" in text,
        # Kit sprint: sheet `kit_card` + `requires: burst_energy_full` land as
        # the custom-resource cost (the CanAfford gate AND the meter spend);
        # sheet tag `burst` lands as Retain (the sim's turn-end filter).
        "kit_cost": "SetCanonicalCost" in text,
        "retain": "CardKeyword.Retain" in text,
    }


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

def lint() -> int:
    cards = {c["id"]: c for c in yaml.safe_load(gen.SHEET.read_text(encoding="utf-8"))}
    upgrades = yaml.safe_load(gen.UPGRADES_SHEET.read_text(encoding="utf-8"))

    findings: list[str] = []

    def fail(card_id: str, detail: str) -> None:
        findings.append(f"{card_id}: {detail}")

    for card_id in sorted(gen.HAND_WRITTEN):
        row = cards.get(card_id)
        if row is None:
            fail(card_id, "in HAND_WRITTEN but has no sheet row")
            continue

        path = CARDS_DIR / f"{gen.pascal(card_id)}.cs"
        if not path.is_file():
            fail(card_id, f"no hand-written file at {path.relative_to(gen.REPO)}")
            continue
        got = extract_cs(path.read_text(encoding="utf-8"))

        # Sheet-side expectations (UNPARSEABLE is itself a finding).
        exp_vars: list[int] = []
        exp_hits: list[int] = []
        try:
            if str(row.get("cost")) == "X":
                raise Unparseable("X cost has no parity rule")
            exp_cost = int(row["cost"])
            walk_effects(row.get("effects", []), exp_vars, exp_hits)
            exp_upg_vars, exp_upg_cost = expected_upgrade(upgrades.get(card_id))
        except Unparseable as e:
            fail(card_id, f"UNPARSEABLE -- {e}; extend this lint, do not skip the card")
            continue

        if got["cost"] != [exp_cost]:
            fail(card_id, f"cost: sheet {exp_cost}, C# base(...) {got['cost']}")
        if Counter(got["vars"]) != Counter(exp_vars):
            fail(card_id, f"base values: sheet {sorted(exp_vars)}, C# vars {sorted(got['vars'])}")
        if Counter(got["hits"]) != Counter(exp_hits):
            fail(card_id, f"hit counts: sheet {sorted(exp_hits)}, C# WithHitCount {sorted(got['hits'])}")
        if Counter(got["upgrade_vars"]) != Counter(exp_upg_vars):
            fail(card_id, f"upgrade deltas: sheet {sorted(exp_upg_vars)}, "
                          f"C# UpgradeValueBy {sorted(got['upgrade_vars'])}")
        exp_upg_cost_list = [] if exp_upg_cost is None else [exp_upg_cost]
        if got["upgrade_cost"] != exp_upg_cost_list:
            fail(card_id, f"cost delta: sheet {exp_upg_cost_list}, "
                          f"C# EnergyCost.UpgradeBy {got['upgrade_cost']}")
        exp_skill_tag = "skill_tag" in row.get("tags", [])
        if got["skill_tag"] != exp_skill_tag:
            fail(card_id, f"skill_tag: sheet {exp_skill_tag}, "
                          f"C# ISkillTagCard {got['skill_tag']} "
                          "(a missing marker generates no burst energy)")
        if got["skill_kw"] != exp_skill_tag:
            fail(card_id, f"skill keyword: sheet skill_tag {exp_skill_tag}, "
                          f"C# KleeKeywords.ElementalSkill {got['skill_kw']} "
                          "(the display keyword is how players see the tag)")
        exp_kit = bool(row.get("kit_card")) or bool(row.get("requires"))
        if got["kit_cost"] != exp_kit:
            fail(card_id, f"kit cost: sheet kit_card/requires {exp_kit}, "
                          f"C# SetCanonicalCost {got['kit_cost']} "
                          "(no resource cost = no full-meter gate, no spend)")
        exp_retain = "burst" in row.get("tags", [])
        if got["retain"] != exp_retain:
            fail(card_id, f"retain: sheet burst tag {exp_retain}, "
                          f"C# CardKeyword.Retain {got['retain']} "
                          "(the sim's turn-end filter keeps burst cards in hand)")

    if findings:
        print(f"handwritten-parity: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1

    print(f"handwritten-parity: OK ({len(gen.HAND_WRITTEN)} cards)")
    return 0


if __name__ == "__main__":
    sys.exit(lint())
