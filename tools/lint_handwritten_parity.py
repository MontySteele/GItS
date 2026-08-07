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
    `: base(N, CardType...)`, `.UpgradeValueBy(Nm)`, `EnergyCost.UpgradeBy(N)`,
    plus the numbers that are NOT DynamicVars -- `GainEncore(owner, N)`, and
    the Fanfare rider's step in both its spellings (the `/ M` in the
    CalculatedDamageVar multiplier and `fanfareStep: M` in the hover tip).
  Mismatch in any category is a finding; any finding exits 1.

Ancient-rarity cards have NO sheet row and never will -- the sim models
neither events nor relics, so they are game-side-only content. They get the
other half of the gate: ANCIENT_WITNESS pins each one's numbers by value, so
"outside the sheets" stops meaning "outside every check". See that table.

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
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_klee_cards as gen  # HAND_WRITTEN, pascal(), sheet paths
from tools.effect_walk import iter_effects  # noqa: E402  (the shared walk)

CARDS_DIR = gen.REPO / "klee-mod" / "KleeCode" / "Cards"

# --------------------------------------------------------------------------
# Sheet side: per-op rules -> expected numbers
# --------------------------------------------------------------------------

# Keys that may appear on an effect without carrying a number we must check.
IGNORABLE_KEYS = {"op", "target", "if", "note", "zone"}


class Unparseable(Exception):
    """A sheet construct with no parity rule. Always a loud failure."""


class Expected:
    """The sheet-side numbers a hand-written card must show in C#.

    One object rather than a growing tuple of parallel lists. Furina's kit
    Burst added two categories at once -- the Encore literal, which is NOT a
    DynamicVar, and the Fanfare rider's (per, step) pair, which lands in two
    unrelated C# spellings -- and a five-positional-argument walk was going to
    get one of them transposed eventually.
    """

    def __init__(self) -> None:
        self.vars: list[int] = []
        self.hits: list[int] = []
        self.encore: list[int] = []
        self.fanfare_riders: list[tuple[int, int]] = []


FANFARE_RIDER_RE = re.compile(r"(\d+)_per_(\d+)_fanfare")


def fanfare_rider(card: dict, eff: dict) -> tuple[int, int]:
    """`bonus_formula: N_per_M_fanfare` on a non-self damage -> (N, M).

    This is the ONE rider grammar with a parity rule, and it has one because
    the generator has one: gen_klee_cards.fanfare_calc_rider renders it as
    CalculationBaseVar(amount) + ExtraDamageVar(N) + a CalculatedDamageVar
    whose multiplier divides ReadableFanfare by M. `let_the_people_rejoice` is
    hand-written and follows that shape by hand, which is exactly the copy this
    file exists to police.

    The two scope guards are gen's own, restated so a card that falls outside
    them fails loudly rather than being measured against the wrong C# shape:
    self-target damage never renders through the rider path, and a salon-deploy
    card renders its replacement multiplier instead (salon_calc_rider).
    """
    formula = eff.get("bonus_formula")
    if eff.get("target") == "self":
        raise Unparseable(
            f"bonus_formula '{formula}' on a self-target damage (not the "
            "CalculatedDamageVar path)")
    if gen.salon_deploy_card(card):
        raise Unparseable(
            f"bonus_formula '{formula}' on a salon-deploy card (renders "
            "through the salon replacement multiplier, not the rider path)")
    m = FANFARE_RIDER_RE.fullmatch(str(formula))
    if not m:
        raise Unparseable(f"bonus_formula '{formula}' has no parity rule")
    return int(m.group(1)), int(m.group(2))


def walk_effects(effects: list, exp: Expected, card: dict) -> None:
    for eff in effects:
        op = eff.get("op")
        keys = set(eff) - IGNORABLE_KEYS - {"op"}

        if op == "damage":
            exp.vars.append(int(eff["amount"]))
            keys.discard("amount")
            for bonus in ("bonus_vs_aura", "bonus_vs_bombed"):
                if bonus in eff:
                    exp.vars.append(int(eff[bonus]))
                    keys.discard(bonus)
            if "bonus_formula" in eff:
                per, _step = fanfare_rider(card, eff)
                # The per-step lands as ExtraDamageVar, i.e. one more base
                # value; the step itself is not a var and is checked on its own
                # two C# spellings (see extract_cs).
                exp.vars.append(per)
                exp.fanfare_riders.append((per, _step))
                keys.discard("bonus_formula")
            times = eff.get("times", 1)
            keys.discard("times")
            if not isinstance(times, int):
                raise Unparseable(f"damage times '{times}' is not a literal int")
            if times != 1:
                exp.hits.append(times)
        elif op == "block":
            exp.vars.append(int(eff["amount"]))
            keys.discard("amount")
        elif op == "place_bomb":
            exp.vars.append(int(eff["bomb_damage"]))
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
                exp.vars.append(int(eff["amount"]))
                keys.discard("amount")
        elif op == "gain_spark":
            exp.vars.append(int(eff["amount"]))
            keys.discard("amount")
        elif op == "gain_encore":
            # NOT a DynamicVar, and that is why it needed its own category
            # rather than a row in `vars`. Both emitters -- the generator's
            # _stmt_gain_encore and the hand-written Burst -- pass the amount
            # as a bare int argument to FurinaResources.GainEncore, so a
            # var-only comparison read the sheet's 6 as a MISSING var and the
            # C# 6 as nothing at all. Two errors that cancel is how a number
            # goes unchecked in both directions at once.
            exp.encore.append(int(eff["amount"]))
            keys.discard("amount")
        elif op == "conditional":
            walk_effects(eff.get("then", []), exp, card)
            walk_effects(eff.get("else", []), exp, card)
            keys -= {"then", "else"}
        elif op == "apply_power":
            # Power amount -> a DynamicVar on the card (generated cards emit
            # "PowerAmount"; hand-written sparks_n_splash follows the idiom).
            # power/max_stacks/splash_procs_per_turn carry no card-side
            # number -- caps are enforced in the power class and cross-checked
            # by gen_klee_cards' APPLY_POWERS registry.
            exp.vars.append(int(eff["amount"]))
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

# A var whose value is a NAMED CONSTANT rather than a literal, e.g.
#   new DynamicVar("PowerAmount", KokomiConstants.GarmentTurns)
# This is the better C# -- the card reads the constant instead of copying it --
# but a literal-only regex sees no var at all and reports the card as having
# fewer values than the sheet, which is indistinguishable from a DELETED
# effect. So the constant is resolved to its value and compared like any other.
# Resolution is sound because lint_constant_parity separately pins every
# mirrored C# constant to its tier0 twin BY VALUE; together the two lints give
# sheet -> C# constant -> tier0 constant end to end.
NAMED_VAR_CONST_RE = re.compile(
    r'new\s+DynamicVar\("\w+",\s*((?:\w+\.)?\w+)\s*\)')
CONST_DECL_RE = re.compile(
    r'(?:^|\n)\s*(?:public|internal)\s+(?:static\s+)?class\s+(\w+)'
    r'|public\s+const\s+int\s+(\w+)\s*=\s*(-?\d+)\s*;')

_const_cache: dict[str, int] | None = None


def cs_constants() -> dict[str, int]:
    """Every `public const int` in the mod, keyed `Class.Member` AND `Member`.

    CLASS-QUALIFIED, not flat, and the reason is on the record: the first
    version of this resolver used bare member names and immediately tripped its
    own collision guard -- `BurstMax` is 70 on Furina's constants and 20 on
    Kokomi's. Two characters' meters under one name is exactly the ambiguity
    that would make a resolver quietly pick the wrong one.

    Bare names are still registered as a convenience for unqualified
    references, but ONLY when unambiguous; a colliding bare name is dropped, so
    an unqualified use of it resolves to nothing and reads as a missing value
    rather than as a wrong one.
    """
    global _const_cache
    if _const_cache is None:
        qualified: dict[str, int] = {}
        bare: dict[str, list[int]] = {}
        for path in sorted((gen.REPO / "klee-mod" / "KleeCode").rglob("*.cs")):
            cls = "?"
            for klass, name, value in CONST_DECL_RE.findall(
                    path.read_text(encoding="utf-8")):
                if klass:
                    cls = klass
                    continue
                qualified[f"{cls}.{name}"] = int(value)
                bare.setdefault(name, []).append(int(value))
        found = dict(qualified)
        for name, values in bare.items():
            if len(set(values)) == 1:
                found.setdefault(name, values[0])
        _const_cache = found
    return _const_cache
COST_RE = re.compile(r':\s*base\(\s*(\d+)\s*,')
HIT_RE = re.compile(r'\.WithHitCount\(\s*(\d+)\s*\)')
UPG_RE = re.compile(r'\.UpgradeValueBy\(\s*(\d+(?:\.\d+)?)m\s*\)')
COST_UPG_RE = re.compile(r'EnergyCost\.UpgradeBy\(\s*(-?\d+)\s*\)')

# `gain_encore` never becomes a DynamicVar on either emitter, so a var regex
# cannot see it. The literal shape only -- a generated card's
# `(IsUpgraded ? 4 : 3)` deliberately does not match, because an upgraded
# hand-written Encore card would be a new shape needing its own rule.
ENCORE_RE = re.compile(
    r'FurinaResources\.GainEncore\(\s*[\w.]+\s*,\s*(\d+)\s*\)')
# The Fanfare rider's STEP, in both places the shape puts it: the multiplier
# lambda that divides the meter, and the hover tip that prints the arithmetic.
# Checking one and not the other is how a face and a hit disagree, which is
# the exact playtest bug the CalculatedDamageVar conversion was for.
FANFARE_DIV_RE = re.compile(r'ReadableFanfare\([^)]*\)\s*/\s*(\d+)')
FANFARE_TIP_RE = re.compile(
    r'fanfarePer:\s*(\d+)\s*,\s*fanfareStep:\s*(\d+)')


def extract_cs(text: str) -> dict:
    consts = cs_constants()
    const_vars = [consts[name] for name in NAMED_VAR_CONST_RE.findall(text)
                  if name in consts]
    return {
        "vars": [int(float(v)) for v in VAR_RE.findall(text)
                 + NAMED_VAR_RE.findall(text)] + const_vars,
        "cost": [int(c) for c in COST_RE.findall(text)],
        "hits": [int(h) for h in HIT_RE.findall(text)],
        "upgrade_vars": [int(float(v)) for v in UPG_RE.findall(text)],
        "upgrade_cost": [int(c) for c in COST_UPG_RE.findall(text)],
        # Furina categories. Empty on every other character's cards, so they
        # cost nothing to assert everywhere.
        "encore": [int(n) for n in ENCORE_RE.findall(text)],
        "fanfare_div": [int(n) for n in FANFARE_DIV_RE.findall(text)],
        "fanfare_tip": [(int(a), int(b)) for a, b in FANFARE_TIP_RE.findall(text)],
        # Burst-energy spike: sheet `skill_tag` must land as the ISkillTagCard
        # marker or the card silently generates no burst energy.
        "skill_tag": "ISkillTagCard" in text,
        # Keyword sprint: skill_tag must ALSO land as the ElementalSkill
        # display keyword (playtest finding: the tag was invisible on cards).
        "skill_kw": "KleeKeywords.ElementalSkill" in text,
        # Elemental UI pass: every Klee Attack is catalyst-Pyro, so it needs
        # both the visible aura badge and the board-aware preview helper.
        "pyro_aura_kw": "KleeKeywords.AppliesPyro" in text,
        "reaction_tips": "KleeCardTooltips.ForCard" in text and "Element.Pyro" in text,
        "bomb_tips": "includesBombRules: true" in text,
        # Kit sprint: sheet `kit_card` + `requires: burst_energy_full` land as
        # the custom-resource cost, which supplies the full-meter gate (the
        # DRAIN moved onto the play hook, 2026-07-24 -- see BurstResource
        # DrainOnPlay); sheet tag `burst` lands as Retain (the sim's turn-end
        # filter).
        "kit_cost": "SetCanonicalCost" in text,
        "retain": "CardKeyword.Retain" in text,
        # Kit cards return to the kit, NO PILE (tier0 combat.py play_card:
        # `if card.kit_card: pass`). See kit_no_pile() for why this is its own
        # gate rather than one more row here.
        "kit_pile": ("GetResultPileTypeForCardPlay" in text
                     and "PileType.None" in text),
    }


def furina_number_findings(exp: "Expected", got: dict, where) -> list[str]:
    """The numbers that are neither DynamicVars nor hit counts.

    Split out because both call sites need them and neither should be the one
    that remembers to. All three categories are empty on a card that has no
    Encore and no Fanfare rider, so asserting them on every hand-written card
    costs nothing and means a future Klee/Kokomi card that grows one is checked
    the day it does.
    """
    findings: list[str] = []
    if Counter(got["encore"]) != Counter(exp.encore):
        findings.append(
            f"gain_encore: sheet {sorted(exp.encore)}, {where} "
            f"FurinaResources.GainEncore {sorted(got['encore'])} -- the Encore "
            "amount is a bare int argument, so a var-only compare cannot see it")
    exp_steps = [step for _per, step in exp.fanfare_riders]
    if Counter(got["fanfare_div"]) != Counter(exp_steps):
        findings.append(
            f"fanfare rider step: sheet bonus_formula {sorted(exp_steps)}, "
            f"{where} ReadableFanfare(...)/N {sorted(got['fanfare_div'])} -- "
            "the divisor is what the card actually resolves")
    if sorted(got["fanfare_tip"]) != sorted(exp.fanfare_riders):
        findings.append(
            f"fanfare rider tip: sheet bonus_formula {sorted(exp.fanfare_riders)}, "
            f"{where} FurinaRiderTips fanfarePer/fanfareStep "
            f"{sorted(got['fanfare_tip'])} -- the hover tip prints the "
            "arithmetic, so a stale pair says one thing and the hit does another")
    return findings


# --------------------------------------------------------------------------
# Kit-card invariants, BOTH sheets
# --------------------------------------------------------------------------

# Where a hand-written card can live. Furina's sit in a per-character
# subdirectory; Klee's sit directly in Cards/.
CS_SEARCH_DIRS = (CARDS_DIR, CARDS_DIR / "Furina", CARDS_DIR / "Kokomi")


def kit_no_pile() -> list[str]:
    """Every `kit_card` row, in EVERY sheet, must declare PileType.None.

    tier0 combat.py play_card ends the kit branch with

        if card.kit_card:
            pass                  # returns to the kit, no pile

    -- unconditional on card TYPE. The C# default is type-derived, so a
    Power-shaped kit card lands on PileType.None by luck while an
    Attack-shaped one lands in the DISCARD pile and recirculates: it
    reshuffles into the draw pile, and the kit-grant machinery only dedups
    against the HAND, so every cast permanently adds a Burst to the deck.
    That is exactly how Furina's `let_the_people_rejoice` shipped broken
    while Klee's `sparks_n_splash` looked fine (playtest 2026-07-24).

    THIS RUNS ACROSS EVERY SHEET ON PURPOSE. When it was written, the parity
    lint above walked only gen.HAND_WRITTEN (Klee), so Furina's hand-written
    cards had no parity gate at all -- the gap the bug came through -- and this
    closed the one invariant that had already burned us, for every character,
    on the day it was found. The wider gate arrived afterwards in two pieces
    (A8's roster loop, EB-3's encore/fanfare rules). This check stays anyway:
    it is a SHEET sweep, not a registry sweep, so it catches a kit card whose
    row exists before anyone remembers to register the class.
    """
    findings: list[str] = []
    # Kokomi joined 2026-07-25 with ceremonial_garment, which is the third
    # distinct card TYPE to carry a kit Burst (Power / Attack / Skill). Only
    # Klee's Power leaves combat by default, so two of the three shipped
    # roster Bursts needed this override to avoid recirculating -- the odds
    # that a fourth character gets it right unprompted are not good.
    for sheet in (gen.REPO / "docs" / "klee-cards.yaml",
                  gen.REPO / "docs" / "furina-cards.yaml",
                  gen.REPO / "docs" / "kokomi-cards.yaml"):
        if not sheet.is_file():
            continue
        for row in yaml.safe_load(sheet.read_text(encoding="utf-8")) or []:
            if not row.get("kit_card"):
                continue
            name = f"{gen.pascal(row['id'])}.cs"
            paths = [d / name for d in CS_SEARCH_DIRS if (d / name).is_file()]
            if not paths:
                findings.append(
                    f"{row['id']}: sheet says kit_card but no C# file named "
                    f"{name} in {[str(d.relative_to(gen.REPO)) for d in CS_SEARCH_DIRS]}")
                continue
            text = paths[0].read_text(encoding="utf-8")
            if not ("GetResultPileTypeForCardPlay" in text
                    and "PileType.None" in text):
                findings.append(
                    f"{row['id']}: sheet kit_card, but "
                    f"{paths[0].relative_to(gen.REPO)} does not override "
                    "GetResultPileTypeForCardPlay to PileType.None "
                    "(the card will enter a pile and recirculate as loot)")
    return findings


# --------------------------------------------------------------------------
# The ROSTER hand-written cards (gen.HAND_WRITTEN_ROSTER)
# --------------------------------------------------------------------------
#
# ADDED BY ADDENDUM A8, 2026-07-26, because the gap this file's own docstring
# described as "its own piece of work" then shipped a defect through it.
#
# R74 deleted `ceremonial_garment`'s entry splash from docs/kokomi-cards.yaml
# (7 damage to all enemies, applies_element). Every other card in that ruling
# batch followed the sheet for free -- they are generated. The Garment is
# hand-written, so the generator never looked at it, and the mod kept casting a
# 7-point hydro AoE that the simulator had already stopped modelling. E2/E2b
# measured one Burst; the build shipped another. Nothing failed:
# lint_constant_parity compares CONSTANTS, this lint walked only gen.HAND_WRITTEN
# (Klee), and there is no C# test project.
#
# The Furina argument for deferring was real -- her ops (encore, fanfare,
# spotlight) genuinely have no parity rule. It was applied too broadly.
# `ceremonial_garment`'s ops are `apply_power`, which has had a rule since the
# first version of this file. The card was excluded by CHARACTER when it should
# have been excluded by PARSEABILITY.
#
# So: every card in HAND_WRITTEN_ROSTER is linted, and a card whose ops have no
# rule must say so HERE, by name, with a reason. Checked in both directions --
# a deferral whose ops have since become parseable is a stale exemption, and a
# stale exemption is how the next one of these gets waved through.
#
# EMPTY as of EB-3. It held exactly one entry, `let_the_people_rejoice`, whose
# reason was "Furina's encore/fanfare ops have no parity rule -- teaching them
# is a Furina pass, not this one". That pass is this one: walk_effects now
# rules `gain_encore` and the `N_per_M_fanfare` damage rider, so the Burst's
# 8 / 1 / 4 / 6 are all compared against docs/furina-cards.yaml and the
# deferral had to come out. Kept as a named, empty table rather than deleted:
# the stale-deferral check below is what forces the next entry back out again,
# and a table that does not exist cannot go stale.
ROSTER_DEFERRED: dict[str, str] = {}

# Categories in extract_cs() that are KLEE-SPECIFIC and must not be asserted
# against another character's card: the Pyro aura keyword, the Pyro reaction
# preview, and the Bomb tooltip are all Klee mechanics, and ElementalSkill is
# Klee's skill-tag display keyword. Kokomi is catalyst-HYDRO with her own
# rider tips (KokomiRiderTips.cs). Asserting Klee's idioms on her cards would
# fail every one of them for being correct, which is how a lint gets disabled.
CHARACTER_NEUTRAL_ONLY = True


def _roster_sheets() -> dict:
    """card id -> row, across every roster sheet."""
    rows: dict = {}
    for profile in gen.PROFILES.values():
        if not profile.sheet.is_file():
            continue
        for row in yaml.safe_load(profile.sheet.read_text(encoding="utf-8")) or []:
            rows[row["id"]] = row
    return rows


def _find_cs(card_id: str) -> Path | None:
    name = f"{gen.pascal(card_id)}.cs"
    for directory in CS_SEARCH_DIRS:
        if (directory / name).is_file():
            return directory / name
    return None


def roster_handwritten_parity() -> list[str]:
    rows = _roster_sheets()
    upgrades = gen.upgrade_deltas()
    findings: list[str] = []

    for card_id in sorted(gen.HAND_WRITTEN_ROSTER):
        row = rows.get(card_id)
        if row is None:
            findings.append(
                f"{card_id}: in HAND_WRITTEN_ROSTER but has no row in any sheet")
            continue
        path = _find_cs(card_id)
        if path is None:
            findings.append(
                f"{card_id}: hand-written, but no C# file named "
                f"{gen.pascal(card_id)}.cs in "
                f"{[str(d.relative_to(gen.REPO)) for d in CS_SEARCH_DIRS]}")
            continue

        exp = Expected()
        parseable = True
        reason = ""
        try:
            if str(row.get("cost")) == "X":
                raise Unparseable("X cost has no parity rule")
            exp_cost = int(row["cost"])
            walk_effects(row.get("effects", []), exp, row)
            exp_upg_vars, exp_upg_cost = expected_upgrade(upgrades.get(card_id))
        except Unparseable as e:
            parseable, reason = False, str(e)

        if card_id in ROSTER_DEFERRED:
            if parseable:
                findings.append(
                    f"{card_id}: STALE DEFERRAL -- it is listed in "
                    "ROSTER_DEFERRED, but its sheet row now parses cleanly. "
                    "Delete the entry so the card is actually linted.")
            continue
        if not parseable:
            findings.append(
                f"{card_id}: UNPARSEABLE -- {reason}. Extend walk_effects, or "
                "add a ROSTER_DEFERRED entry naming the reason. Do not skip "
                "the card silently -- that is how the R74 splash shipped.")
            continue

        got = extract_cs(path.read_text(encoding="utf-8"))
        where = path.relative_to(gen.REPO)

        if got["cost"] != [exp_cost]:
            findings.append(
                f"{card_id}: cost: sheet {exp_cost}, {where} base(...) {got['cost']}")
        if Counter(got["vars"]) != Counter(exp.vars):
            findings.append(
                f"{card_id}: base values: sheet {sorted(exp.vars)}, "
                f"{where} vars {sorted(got['vars'])} -- an EXTRA C# value is a "
                "deleted sheet effect that is still being played")
        if Counter(got["hits"]) != Counter(exp.hits):
            findings.append(
                f"{card_id}: hit counts: sheet {sorted(exp.hits)}, "
                f"{where} WithHitCount {sorted(got['hits'])}")
        findings.extend(
            f"{card_id}: {d}" for d in furina_number_findings(exp, got, where))
        if Counter(got["upgrade_vars"]) != Counter(exp_upg_vars):
            findings.append(
                f"{card_id}: upgrade deltas: sheet {sorted(exp_upg_vars)}, "
                f"{where} UpgradeValueBy {sorted(got['upgrade_vars'])}")
        exp_upg_cost_list = [] if exp_upg_cost is None else [exp_upg_cost]
        if got["upgrade_cost"] != exp_upg_cost_list:
            findings.append(
                f"{card_id}: cost delta: sheet {exp_upg_cost_list}, "
                f"{where} EnergyCost.UpgradeBy {got['upgrade_cost']}")

        exp_skill_tag = "skill_tag" in row.get("tags", [])
        if got["skill_tag"] != exp_skill_tag:
            findings.append(
                f"{card_id}: skill_tag: sheet {exp_skill_tag}, {where} "
                f"ISkillTagCard {got['skill_tag']} (a missing marker generates "
                "no burst energy)")
        exp_kit = bool(row.get("kit_card")) or bool(row.get("requires"))
        if got["kit_cost"] != exp_kit:
            findings.append(
                f"{card_id}: kit cost: sheet kit_card/requires {exp_kit}, "
                f"{where} SetCanonicalCost {got['kit_cost']}")
        exp_retain = "burst" in row.get("tags", [])
        if got["retain"] != exp_retain:
            findings.append(
                f"{card_id}: retain: sheet burst tag {exp_retain}, {where} "
                f"CardKeyword.Retain {got['retain']}")
        exp_kit_card = bool(row.get("kit_card"))
        if got["kit_pile"] != exp_kit_card:
            findings.append(
                f"{card_id}: kit pile: sheet kit_card {exp_kit_card}, {where} "
                f"PileType.None override {got['kit_pile']}")

    # The registry must be COMPLETE, or the next hand-written card is invisible
    # to this file exactly the way the Garment was. Any .cs sitting in a
    # character card directory (not Generated/) whose name matches a sheet row
    # is a hand-written card and must be registered.
    known = gen.HAND_WRITTEN | gen.HAND_WRITTEN_ROSTER
    by_class = {gen.pascal(cid): cid for cid in rows}
    for directory in CS_SEARCH_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.cs")):
            card_id = by_class.get(path.stem)
            if card_id is not None and card_id not in known:
                findings.append(
                    f"{card_id}: {path.relative_to(gen.REPO)} is a hand-written "
                    "card with a sheet row, but is in neither HAND_WRITTEN nor "
                    "HAND_WRITTEN_ROSTER, so nothing compares it to the sheet")
    return findings


# --------------------------------------------------------------------------
# The SHEETLESS hand-written cards: Ancient-rarity (EB-3)
# --------------------------------------------------------------------------
#
# Everything above compares C# to a ratified sheet. The Ancients have no sheet
# row: they are game-side-only content (DECISIONS 2026-07-23) and Dusty Tome
# is their single acquisition door. (The 2026-07-23 wording said "the sim
# models neither events nor relics"; tier05 has modelled both since the
# relic-content pass -- the sheetless status now rests on tier0's
# no-passive-accrual law, which bars the Ancients' per-turn shapes.) That is a real answer to "where does
# this number come from", and it left them with no gate at all -- `+5 Encore
# per turn` on AllTheWorldsAStage existed in exactly one place in the repo, so
# any edit to it was self-consistent by definition.
#
# So they get the other half of the gate, borrowed from lint_constant_parity's
# UNMIRRORED table: a WITNESS. The pin is not a claim that the number is
# right -- nothing can make that claim about an Ancient, and PrincessOfWatatsumi
# says so in its own docstring ("no instrument can tell us it is wrong"). It is
# a claim that the number is what it was when someone last looked. Changing an
# Ancient now means changing it twice, in the card and here, which is precisely
# the friction the sheets provide for everything else.
#
# CHECKED IN BOTH DIRECTIONS, like every table in this file: an Ancient card
# with no pin is a finding, a pin with no card is a finding, and a pinned card
# that has since acquired a sheet row is a finding (it belongs in
# HAND_WRITTEN_ROSTER, where it would be compared instead of witnessed).
#
# Categories are extract_cs's, so the pins and the sheet comparisons read the
# same C# through the same regexes.
ANCIENT_WITNESS: dict[str, dict] = {
    "AllTheWorldsAStage": {
        "why": "Furina's Ancient, the Encore engine (user ruling 2026-07-23, "
               "act-2 Darv softlock fix). +5 Encore at the start of each turn, "
               "+2 on the Tome's upgrade. Read at its upgraded numbers, since "
               "DustyTome.AfterObtained upgrades what it grants.",
        "cost": [1],
        "vars": [5],
        "hits": [],
        "upgrade_vars": [2],
        "upgrade_cost": [],
        # The Encore drip is applied by EncorePerTurnPower, not by a
        # GainEncore call on the card, so this stays empty: the 5 above IS the
        # drip, carried as the power's PowerAmount.
        "encore": [],
        "fanfare_div": [],
        "fanfare_tip": [],
    },
    "PrincessOfWatatsumi": {
        "why": "Kokomi's Ancient, the deliberate parallel to Furina's: +3 "
               "Charge per turn, +1 on upgrade. 3 rather than 5 because Charge "
               "is banked and never spent, so it compounds against the Kurage "
               "pulse multiplier instead of adding to a total (its docstring "
               "carries the argument).",
        "cost": [1],
        "vars": [3],
        "hits": [],
        "upgrade_vars": [1],
        "upgrade_cost": [],
        "encore": [],
        "fanfare_div": [],
        "fanfare_tip": [],
    },
    "JumpyDumptyMkOmega": {
        "why": "Klee's Ancient, top of the Jumpy Dumpty family. 12 damage to "
               "random enemies 3 times, plus a 12-damage Bomb on EVERY enemy; "
               "+4/+4 on upgrade. Same ruling and the same reason for having "
               "no sheet row as the other two.",
        "cost": [2],
        "vars": [12, 12],
        "hits": [3],
        "upgrade_vars": [4, 4],
        "upgrade_cost": [],
        "encore": [],
        "fanfare_div": [],
        "fanfare_tip": [],
    },
}

# What a pin must cover. Every numeric category extract_cs produces -- listed
# explicitly so that adding a category to the extractor breaks every pin at
# once (a pin silently missing the newest category is a pin that stopped
# witnessing the thing it was added for).
WITNESSED_CATEGORIES = (
    "cost", "vars", "hits", "upgrade_vars", "upgrade_cost",
    "encore", "fanfare_div", "fanfare_tip",
)

ANCIENT_CTOR_RE = re.compile(r":\s*base\s*\([^;]*CardRarity\.Ancient", re.S)


def ancient_witness() -> list[str]:
    """Every Ancient-rarity card class, against its pinned numbers."""
    findings: list[str] = []
    sheet_ids = {gen.pascal(cid) for cid in _roster_sheets()}
    seen: set[str] = set()

    for directory in CS_SEARCH_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.cs")):
            text = path.read_text(encoding="utf-8")
            ctors = ANCIENT_CTOR_RE.findall(text)
            if not ctors:
                continue
            where = path.relative_to(gen.REPO)
            seen.add(path.stem)
            # One card class per file is the house pattern for card files; the
            # one multi-class file (SpotlightCards.cs) holds Tokens, not
            # Ancients. Counted on CONSTRUCTORS, not on the string: three of
            # the four Ancients name CardRarity.Ancient in their docstrings too,
            # explaining that reward/transform/shop generation filters it out.
            if len(ctors) != 1:
                findings.append(
                    f"{path.stem}: {where} declares {len(ctors)} "
                    "CardRarity.Ancient constructors; the witness extractor is "
                    "per-FILE and cannot attribute numbers to one of several "
                    "classes. Split the file.")
                continue
            pin = ANCIENT_WITNESS.get(path.stem)
            if pin is None:
                findings.append(
                    f"{path.stem}: {where} is an Ancient-rarity card with no "
                    "sheet row and no ANCIENT_WITNESS pin, so nothing in the "
                    "repo notices if its numbers change. Add a pin with a "
                    "`why`.")
                continue
            if path.stem in sheet_ids:
                findings.append(
                    f"{path.stem}: pinned in ANCIENT_WITNESS, but it now has a "
                    "sheet row. A card with a ruled source must be COMPARED, "
                    "not witnessed -- move it to gen.HAND_WRITTEN_ROSTER and "
                    "delete the pin.")
                continue
            missing = [k for k in WITNESSED_CATEGORIES if k not in pin]
            if missing:
                findings.append(
                    f"{path.stem}: ANCIENT_WITNESS pin is missing "
                    f"{missing}; a pin must cover every extracted category.")
                continue
            if not pin.get("why"):
                findings.append(
                    f"{path.stem}: ANCIENT_WITNESS pin has no `why`. The "
                    "reason is the whole value of a witness.")
            got = extract_cs(text)
            for key in WITNESSED_CATEGORIES:
                if Counter(got[key]) != Counter(pin[key]):
                    findings.append(
                        f"{path.stem}: {key}: pinned {sorted(pin[key])}, "
                        f"{where} {sorted(got[key])} -- an Ancient has no "
                        "sheet to arbitrate this, so the pin IS the record. "
                        "If the change is intended, update the pin in the "
                        "same commit.")

    for name in sorted(set(ANCIENT_WITNESS) - seen):
        findings.append(
            f"{name}: pinned in ANCIENT_WITNESS, but no Ancient-rarity card "
            f"file named {name}.cs was found in "
            f"{[str(d.relative_to(gen.REPO)) for d in CS_SEARCH_DIRS]}. A pin "
            "outliving its card is how the next exemption gets waved through.")
    return findings


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

def lint() -> int:
    cards = {c["id"]: c for c in yaml.safe_load(gen.SHEET.read_text(encoding="utf-8"))}
    # gen.upgrade_deltas() is the merged index across every upgrade sheet
    # (klee + furina), matching tier0/content/upgrades.py. It replaced the
    # single-sheet read when the Fontaine companions entered Klee's slot.
    upgrades = gen.upgrade_deltas()

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
        exp = Expected()
        try:
            if str(row.get("cost")) == "X":
                raise Unparseable("X cost has no parity rule")
            exp_cost = int(row["cost"])
            walk_effects(row.get("effects", []), exp, row)
            exp_upg_vars, exp_upg_cost = expected_upgrade(upgrades.get(card_id))
        except Unparseable as e:
            fail(card_id, f"UNPARSEABLE -- {e}; extend this lint, do not skip the card")
            continue

        if got["cost"] != [exp_cost]:
            fail(card_id, f"cost: sheet {exp_cost}, C# base(...) {got['cost']}")
        if Counter(got["vars"]) != Counter(exp.vars):
            fail(card_id, f"base values: sheet {sorted(exp.vars)}, C# vars {sorted(got['vars'])}")
        if Counter(got["hits"]) != Counter(exp.hits):
            fail(card_id, f"hit counts: sheet {sorted(exp.hits)}, C# WithHitCount {sorted(got['hits'])}")
        for detail in furina_number_findings(
                exp, got, path.relative_to(gen.REPO)):
            fail(card_id, detail)
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
        exp_pyro_ui = row.get("type") == "attack"
        if got["pyro_aura_kw"] != exp_pyro_ui:
            fail(card_id, f"aura keyword: sheet catalyst Attack {exp_pyro_ui}, "
                          f"C# KleeKeywords.AppliesPyro {got['pyro_aura_kw']}")
        if got["reaction_tips"] != exp_pyro_ui:
            fail(card_id, f"reaction previews: sheet catalyst Attack {exp_pyro_ui}, "
                          f"C# KleeCardTooltips/Element.Pyro {got['reaction_tips']}")
        # L4: branch-aware, mirroring `gen_klee_cards.emit`'s
        # `includes_bomb_rules` exactly -- both now walk the whole effect
        # TREE. A branch-gated `place_bomb` (sparkly_explosion's kill
        # conditional) still puts Bombs on the face, so it still owes the
        # rules text; the two flat scans this replaced agreed with each other
        # about the wrong answer, which is why the gate never caught it.
        exp_bomb_tips = any(e.get("op") in {
            "place_bomb", "detonate", "modify_bombs", "move_bombs",
            "chance_bomb_per_detonation"
        } for e in iter_effects(row.get("effects", [])))
        if got["bomb_tips"] != exp_bomb_tips:
            fail(card_id, f"Bomb tooltip: sheet Bomb mechanic {exp_bomb_tips}, "
                          f"C# includesBombRules {got['bomb_tips']}")
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
        exp_kit_card = bool(row.get("kit_card"))
        if got["kit_pile"] != exp_kit_card:
            fail(card_id, f"kit pile: sheet kit_card {exp_kit_card}, "
                          f"C# PileType.None override {got['kit_pile']} "
                          "(kit cards return to the kit, no pile)")

    findings.extend(roster_handwritten_parity())
    findings.extend(kit_no_pile())
    findings.extend(ancient_witness())

    if findings:
        print(f"handwritten-parity: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1

    linted = len(gen.HAND_WRITTEN) + len(
        gen.HAND_WRITTEN_ROSTER - set(ROSTER_DEFERRED))
    print(f"handwritten-parity: OK ({linted} cards linted, "
          f"{len(ANCIENT_WITNESS)} sheetless Ancients witnessed, "
          f"{len(ROSTER_DEFERRED)} deferred by name)")
    return 0


if __name__ == "__main__":
    sys.exit(lint())
