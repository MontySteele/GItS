"""Structural gate on the GENERATED C# cards.

Why this lint exists (2026-07-28, playtest-2 batch 1 review)
-----------------------------------------------------------
Twice in one commit cycle a generated card lost a real mechanism while the
entire suite stayed green:

  * B1  -- Thunderous Ovation's `bonus_formula` rider sat on a BLOCK op, and
           every rider predicate in the generator gated on `op == "damage"`.
           The card shipped a flat 6.
  * R87 -- a `times`-var insertion captured GrandFinale's `BonusPer` lines
           into the wrong branch by indentation, so the shipped Klee rare
           lost `new DynamicVar("BonusPer", 2m)` -- while `OnUpgrade` and the
           description still referenced it.

Both were invisible to 1296 passing tests for the SAME reason: the assertions
on generated cards read the RENDERED TEXT, and in both cases the text is
identical with and without the mechanism. Pinning each escapee after the fact
does not close the class -- the next silent drop is a var nobody pinned.

So the gate here reads the emitted artifact STRUCTURALLY, and it is written to
be generator-independent on purpose: it parses the .cs the generator produced
rather than calling back into the generator that produced it. A bug that makes
the emitter drop something cannot also make this lint stop looking for it.

Three laws:

  L1  DANGLING VAR   -- every DynamicVar the file REFERENCES (in the body via
                        `DynamicVars.X` / `DynamicVars["X"]`, or in the
                        localization text via a `{X:...}` token) must be
                        DECLARED. This is the exact shape of the GrandFinale
                        near-miss, and it is a runtime crash or a silently
                        dead upgrade, not a cosmetic defect.

  L2  ORPHAN VAR     -- every var DECLARED must be referenced somewhere. A var
                        emitted and then never read is a rider that got half
                        way out of the generator: the number exists but
                        nothing spends it.

  L3  SHEET COVERAGE -- a curated table of sheet mechanics that can vanish
                        WITHOUT CHANGING THE TEXT, each with the marker its
                        implementation must leave in the emitted source. This
                        is the structurally-invisible-defect pattern (curated
                        list + lint) applied to codegen: when a human catch
                        finds a new silent-drop shape, it gets a row here so
                        the machine catches the next one.

L3 is deliberately NOT a whitelist of every sheet field. Field coverage is
already total and already enforced -- `card_level_reason` and the per-op field
checks in gen_klee_cards.py refuse anything they do not understand. The hole
this closes is the one downstream of that: the field IS understood, the
emitter DID run, and the mechanism still is not in the file.

Run:  python tools/lint_generated_structure.py
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.effect_walk import iter_effects  # noqa: E402
from tools.gen_klee_cards import (  # noqa: E402
    FURINA_PROFILE,
    KLEE_PROFILE,
    KOKOMI_PROFILE,
    CharacterProfile,
    pascal,
)

PROFILES = (KLEE_PROFILE, FURINA_PROFILE, KOKOMI_PROFILE)

# `new DamageVar(...)` declares the var named "Damage"; the typed subclasses
# are uniformly <Name>Var. `new DynamicVar("Foo", ...)` / `new
# CalculatedVar("Foo", ...)` declare the name they are handed.
_NAMED_DECL = re.compile(r'new\s+(?:Dynamic|Calculated)Var\(\s*"([A-Za-z]\w*)"')
_TYPED_DECL = re.compile(r"new\s+([A-Za-z]\w*)Var\(\s*(?!\")")

# References: body lookups in either idiom, plus localization text tokens.
_BODY_REF = re.compile(r'DynamicVars(?:\.([A-Za-z]\w*)|\[\s*"([A-Za-z]\w*)"\s*\])')
_TEXT_REF = re.compile(r"\{([A-Za-z]\w*)[:}]")

# `{IfUpgraded:show:a|b}` is BaseLib's runtime upgrade-swap token, not a var --
# it is resolved by SimpleLoc and has no CanonicalVars declaration.
PSEUDO_TOKENS = frozenset({"IfUpgraded"})

# CalculationBase / CalculationExtra / ExtraDamage are the input slots of a
# Calculated*Var triple: the Calculated var reads them off the card itself
# rather than by name, so a card may declare them and never mention them
# again. They are exempt from L2 ONLY when the file actually declares a
# Calculated var to consume them -- otherwise they are a genuine orphan, which
# is precisely the "half a rider" shape B1 shipped.
CALCULATION_INPUTS = frozenset({"CalculationBase", "CalculationExtra", "ExtraDamage"})
_CALCULATED_CONSUMER = re.compile(r"new\s+Calculated\w*Var\(")


@dataclass(frozen=True)
class Mechanic:
    """One sheet mechanic that is invisible in the rendered card text."""

    name: str
    applies: Callable[[dict], bool]
    markers: tuple[str, ...]
    why: str


def _effects(card: dict) -> list[dict]:
    """The card's WHOLE effect tree (L4): every mechanic in the table below
    is just as invisible-in-the-text when it sits in a conditional's `then:`
    as when it sits at the top level, and the emitter has to leave its
    marker either way. Nothing on the live sheets is branch-nested today,
    so adopting the shared walk changed no verdict -- which is the point of
    adopting it before something is."""
    return list(iter_effects(card.get("effects")))


def _has_literal_times(card: dict) -> bool:
    """A multi-hit attack whose hit count is a plain integer on the sheet."""
    return any(
        isinstance(e.get("times"), int) and e["times"] > 1
        for e in _effects(card)
        if e.get("op") == "damage"
    )


def _has_bonus_formula(card: dict) -> bool:
    return any(e.get("bonus_formula") is not None for e in _effects(card))


# The curated table. Each row is a mechanic that a reader CANNOT catch by
# reading the card face, because the face says the same thing whether the
# mechanism is there or not.
MECHANICS = (
    Mechanic(
        name="exhaust",
        applies=lambda c: bool(c.get("exhaust")),
        markers=("CardKeyword.Exhaust",),
        why=(
            "the game auto-renders the Exhaust banner from the keyword, so a "
            "card that lost the keyword reads EXACTLY like one that never had "
            "it -- B3's whole question"
        ),
    ),
    Mechanic(
        name="innate",
        applies=lambda c: bool(c.get("innate")),
        markers=("CardKeyword.Innate",),
        why=(
            "A9: Innate drives opening-hand placement. A card missing it plays "
            "identically once drawn; the only symptom is that it is not there "
            "on turn 1"
        ),
    ),
    Mechanic(
        name="times",
        applies=_has_literal_times,
        markers=("WithHitCount",),
        why=(
            "A5: hit count lives on the command, not in the sentence. Drop "
            "WithHitCount and a 3x2 attack quietly becomes a 2"
        ),
    ),
    Mechanic(
        name="bonus_formula",
        applies=_has_bonus_formula,
        # Two legal rails, on purpose. A ratio against a CAPPED resource
        # (N_per_M_fanfare, N_per_M_charge) becomes a Calculated var triple
        # with a multiplier. A slope on an UNCAPPED running counter
        # (2_per_detonation_this_combat) becomes a BonusPer var multiplied
        # inline at play, because there is no bounded resource to divide.
        # Either rail satisfies the law; emitting NEITHER is the defect.
        markers=(
            "CalculatedDamageVar",
            "CalculatedBlockVar",
            "CalculationBaseVar",
            "BonusPer",
        ),
        why=(
            "B1 exactly: the rider is a Calculated var triple. Without it the "
            "card emits its flat printed number and the face still reads as "
            "though it scales"
        ),
    ),
    # --- Fanfare rework (2026-07-28). Three rows, required by the brief's
    # gate clause: "add L3 rows for any new invisible mechanic -- the negative
    # floor and the keyword grants qualify."
    Mechanic(
        name="retain",
        applies=lambda c: bool(c.get("retain")),
        markers=("CardKeyword.Retain",),
        why=(
            "Track C.1: Retain is what makes Slip Backstage's Encore sink "
            "schedulable -- she holds it until the buffer is deep enough to "
            "pay without the wound. A card that lost the keyword plays "
            "IDENTICALLY the turn it is played; the only symptom is that it "
            "was discarded on some earlier turn the player meant to bank it. "
            "The exhaust/innate row above, one field over"
        ),
    ),
    Mechanic(
        name="fanfare_keywords",
        applies=lambda c: any(
            e.get("op") in ("raise_fanfare_cap", "gain_fanfare_floor")
            for e in _effects(c)),
        markers=("RaiseFanfareCap", "GainFanfareFloor"),
        why=(
            "Track B: these two keywords ARE the value that used to arrive "
            "invisibly -- every Power silently granted 5 Fanfare floor (rares "
            "8) and no card said so. The whole track is that grant becoming a "
            "printed line. A generated card that dropped the call would print "
            "the keyword and grant nothing, which is strictly worse than the "
            "invisible rule it replaced: the face would now be LYING rather "
            "than merely silent"
        ),
    ),
    Mechanic(
        name="crash_fanfare",
        applies=lambda c: any(e.get("op") == "crash_fanfare"
                              for e in _effects(c)),
        markers=("DropFanfareToFloor",),
        why=(
            "Track C.2: the Hyperbeam's PRICE. Drop this call and The Final "
            "Verdict still deals damage equal to Fanfare and simply never "
            "pays for it -- a card that reads as a costed finisher and "
            "behaves as a free one. The damage half is visible on screen and "
            "the cost half is a number moving in a meter, so nothing about "
            "playing the card would look wrong"
        ),
    ),
)


def canonical_vars_block(source: str) -> str:
    """The body of the CanonicalVars initializer, or "" if the card has none.

    Scoping matters: `new BlockVar(...)` also appears INLINE as an argument to
    CreatureCmd.GainBlock in conditional branches, and that is not a
    declaration of anything. Reading the whole file would call it one and then
    report the card's own conditional block as an orphan var.
    """
    head = source.find("CanonicalVars")
    if head < 0:
        return ""
    open_brace = source.find("{", head)
    if open_brace < 0:
        return ""
    depth = 0
    for i in range(open_brace, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[open_brace : i + 1]
    return ""


def declared_vars(source: str) -> set[str]:
    """Var names this file declares in CanonicalVars."""
    block = canonical_vars_block(source)
    names = set(_NAMED_DECL.findall(block))
    for typed in _TYPED_DECL.findall(block):
        # `new List<DynamicVar>` and friends are not declarations.
        if typed in ("Dynamic", "Calculated"):
            continue
        names.add(typed)
    return names


def referenced_vars(source: str) -> set[str]:
    """Var names this file reads, from the body and from the card text."""
    names: set[str] = set()
    for dotted, indexed in _BODY_REF.findall(source):
        names.add(dotted or indexed)
    names |= set(_TEXT_REF.findall(source))
    return names - PSEUDO_TOKENS


def structural_problems(source: str, where: str) -> list[str]:
    """L1 + L2 for a single generated file."""
    problems = []
    declared = declared_vars(source)
    referenced = referenced_vars(source)

    for name in sorted(referenced - declared):
        problems.append(
            f"{where}: L1 DANGLING VAR -- '{name}' is referenced but never "
            f"declared in CanonicalVars. Declared: {sorted(declared)}"
        )

    exempt = (
        CALCULATION_INPUTS if _CALCULATED_CONSUMER.search(source) else frozenset()
    )
    for name in sorted(declared - referenced - exempt):
        problems.append(
            f"{where}: L2 ORPHAN VAR -- '{name}' is declared but nothing reads "
            f"it. Either the effect that spends it was dropped, or the var is "
            f"dead weight on the card face."
        )
    return problems


def coverage_problems(card: dict, source: str, where: str) -> list[str]:
    """L3 for a single generated file."""
    problems = []
    for mech in MECHANICS:
        if not mech.applies(card):
            continue
        if any(marker in source for marker in mech.markers):
            continue
        problems.append(
            f"{where}: L3 MISSING MECHANIC -- the sheet rules '{mech.name}' "
            f"but the generated source carries none of "
            f"{list(mech.markers)}. This is invisible in the card text: "
            f"{mech.why}."
        )
    return problems


def generated_sources(profile: CharacterProfile) -> list[tuple[dict, str, str]]:
    """(sheet card, source text, human label) for every card actually emitted."""
    manifest = json.loads(profile.manifest.read_text(encoding="utf-8"))
    emitted = set(manifest.get("generated", []))
    cards = yaml.safe_load(profile.sheet.read_text(encoding="utf-8")) or []

    rows = []
    for card in cards:
        if not isinstance(card, dict) or card.get("id") not in emitted:
            continue
        path = profile.out_dir / f"{pascal(card['id'])}.cs"
        if not path.exists():
            # The manifest claims it; the file is gone. That is its own defect
            # and worth reporting rather than skipping past.
            rows.append((card, "", f"{profile.character_id}/{card['id']}"))
            continue
        rows.append(
            (
                card,
                path.read_text(encoding="utf-8"),
                f"{profile.character_id}/{path.name}",
            )
        )
    return rows


def problems(profile: CharacterProfile) -> list[str]:
    found = []
    for card, source, where in generated_sources(profile):
        if not source:
            found.append(
                f"{where}: manifest lists this card as generated but "
                f"{profile.out_dir.name}/{pascal(card['id'])}.cs does not exist"
            )
            continue
        found += structural_problems(source, where)
        found += coverage_problems(card, source, where)
    return found


def all_problems() -> list[str]:
    found = []
    for profile in PROFILES:
        found += problems(profile)
    return found


def main() -> int:
    found = all_problems()
    for line in found:
        print(line)
    if found:
        print(f"\nFAIL: {len(found)} structural problem(s) in generated cards")
        return 1
    total = sum(len(generated_sources(p)) for p in PROFILES)
    print(f"CLEAN: {total} generated cards pass L1/L2/L3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
