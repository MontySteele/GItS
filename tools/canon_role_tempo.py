"""The canon role x tempo baseline, read STRUCTURALLY out of the local dll.

Track A / T1 + T3 (docs/track-a-kickoff-brief.md). Produces three things:

  game_ref/role_tempo_canon.json   LOCAL artifact. Per-card classification for
                                   all five canon pools, card names included.
                                   Gitignored reference material -- never
                                   committed, same rule as every other
                                   game_ref/ output (.gitignore:28).
  docs/role-tempo-baseline.md      COMMITTED. Percentages and shapes only. No
                                   card names, no card text, no numbers off
                                   any card face.
  docs/role-tempo-floors.yaml      COMMITTED. The machine-readable floors the
                                   coverage lint reads. Percentages only.

WHY STRUCTURAL AND NOT TEXT
----------------------------
The brief says "on card text for canon", because the chat session's classifier
was a regex over the wiki. The DLL is better information and safer material:
a card's Cmds, DynamicVars, TargetType and the POWER/ORB/SUMMON models it
reaches for say what it does without any of its printed text entering this
process. The known wiki misses the brief lists ($Dexterity -> block,
@IE/@SE/@ST -> velocity, $Plating -> block, "Another player"/"an ally" ->
support) are not patched here; they are STRUCTURALLY ABSENT, because
DexterityPower and PlatingPower are read off their own models and an ally
target is `TargetType.AnyAlly` in the constructor. That is the reconciliation
those four fixes were reaching for.

The recursion is what makes the tag-through real on this side. Zap channels a
LightningOrb; nothing about Zap's own body says "scaling damage". The orb's
model does, so the orb's model is read, and Zap inherits it -- charter A0.1,
executed rather than asserted.

HOW THE FLOORS ARE DERIVED, in one paragraph
---------------------------------------------
A cell is (solve x fight-band). A cell is MANDATORY when all five canon pools
are non-zero in it; a cell any canon character sits at zero in is an identity
statement, not a debt (the charter's own example: Klee at zero sustain is
Silent-shaped). The floor for a mandatory cell is the MINIMUM of the five
canon percentages. Both halves are forced by the same requirement -- the
brief's stop-and-surface says a floor that would fail a canon character means
the derivation is wrong -- and a minimum-of-canon floor cannot, by
construction. `utility` is never linted (A0.2). `support` is never linted
either: the sim is one-seat, so those cells are play-graded only (D4).

USAGE
-----
    python tools/canon_role_tempo.py            # needs the game + ilspycmd
    python tools/canon_role_tempo.py --from-json  # re-derive from game_ref/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import extract_base_game_pool as extract      # noqa: E402
from tools import role_tempo as rt                        # noqa: E402

CHARACTERS = ("Ironclad", "Silent", "Defect", "Necrobinder", "Regent")
OUT_JSON = REPO / "game_ref" / "role_tempo_canon.json"
OUT_DOC = REPO / "docs" / "role-tempo-baseline.md"
OUT_FLOORS = REPO / "docs" / "role-tempo-floors.yaml"

# --- structural signals -----------------------------------------------------
#
# Each entry is (regex, role). Applied to a decompiled model's source -- a
# card, a Power, an Orb or a summoned creature, all four read the same way,
# which is what lets the tag-through recurse without a second vocabulary.
SIGNALS = (
    (re.compile(r"DamageCmd\.Attack|CreatureCmd\.Damage\b|"
                r"new (?:Damage|ExtraDamage|CalculatedDamage|OstyDamage)Var"),
     "frontload"),
    (re.compile(r"CreatureCmd\.GainBlock|new (?:Block|CalculatedBlock)Var|"
                r"StaticHoverTip\.Block|ModifyBlock"), "block"),
    (re.compile(r"CreatureCmd\.Heal\b|CreatureCmd\.GainMaxHp|"
                r"new (?:Heal|MaxHp)Var|PreventDamage"), "sustain"),
    (re.compile(r"CardPileCmd\.Draw|PlayerCmd\.GainEnergy|CardCmd\.AutoPlay|"
                r"CardPileCmd\.AutoPlayFromDrawPile|new (?:Cards|Energy)Var|"
                r"ModifyEnergyCost|CardCmd\.Retain"), "velocity"),
    # Co-op. Three independent spellings, all of them the game's own: an ally
    # TargetType, the MultiplayerOnly constraint, and a power that walks the
    # owner's teammates.
    (re.compile(r"TargetType\.(?:AnyAlly|AllAllies)|"
                r"CardMultiplayerConstraint\.MultiplayerOnly|"
                r"GetTeammatesOf"), "support"),
)
# A model that MODIFIES output rather than producing it is scaling. On a card
# this is reached through the Power it applies, never off the card's own body.
SCALING_IN_POWER = re.compile(
    r"ModifyDamage(?:Additive|Multiplicative)|ModifyOrbValue|"
    r"ModifyBlock(?:Additive|Multiplicative)|AfterSideTurnStart|"
    r"PowerCmd\.Apply<\w+Power>")
DEBUFF = re.compile(r"PowerType\.Debuff")
# Accumulated state: the base-game grammar for "base + extra * count".
ACCUMULATES = re.compile(r"new Calculat(?:ed|ion)\w*Var|CalculationBase|"
                         r"ExhaustPile|CombatState\.\w*Count")
# The three token layers the five pools actually own.
REACHES = (
    (re.compile(r"PowerCmd\.Apply<(\w+Power)>"), "Power"),
    (re.compile(r"OrbCmd\.Channel<(\w+Orb)>"), "Orb"),
    (re.compile(r"HoverTipFactory\.FromOrb<(\w+Orb)>"), "Orb"),
)
SUMMONS = re.compile(r"OstyCmd\.Summon")
CONSUMES_ONLY = re.compile(r"OrbCmd\.Evoke|ForgeCmd\.Forge|PlayerCmd\.GainStars")

# EVERY mechanic type a card's body so much as NAMES, generate or read. The
# `tokens` list above is the GENERATE side only (PowerCmd.Apply, OrbCmd.Channel)
# and a package needs both halves: Catalyst never applies Poison, it reads the
# stack and doubles it, and a poison package that cannot see Catalyst is not the
# poison package. Type NAMES only -- no card text, no numbers (R90/1c keeps the
# committed side percentages-only exactly as before).
MENTIONS = re.compile(r"\b(\w+(?:Power|Orb))\b")
# Mechanic layers that are commands rather than types, so MENTIONS cannot see
# them. Each maps a call shape to the marker name a package matches on.
#
# THERE IS NO `ForgeStars` MARKER, AND THERE MUST NOT BE ONE (EB-192, R231).
# It used to sit here as `ForgeCmd\.|GainStars|\bStars\b`, and it was an
# invented union of two unrelated Regent mechanics: Stars (a spendable
# resource) and Forge (a growing 0-cost attack card, `ForgeCmd.Forge`, which
# never touches a Star). No `ForgeStars` symbol exists in the 0.111.0
# assembly. See `docs/current/research/regent-stars-economy.md` §0 and §3.1.
# The Star layer is drawn as a curated package instead -- REGENT_STARS below
# says why a regex over card bodies structurally cannot draw it.
MECHANIC_MARKERS = (
    (re.compile(r"\bOsty\w*\b|OstyCmd\."), "Osty"),
    (re.compile(r"OrbCmd\.|\bOrbs?\b"), "OrbLayer"),
    (re.compile(r"ExhaustPile|CardPileCmd\.Exhaust|CardLocation\.Exhaust"),
     "ExhaustLayer"),
)


class Reader:
    """Reads and memoises decompiled models by short type name."""

    def __init__(self, root: Path):
        self.root = root
        self._cache: dict[str, str] = {}

    def source(self, short_name: str) -> str:
        if short_name not in self._cache:
            paths = sorted(self.root.rglob(f"{short_name}.cs"))
            self._cache[short_name] = paths[0].read_text(encoding="utf-8") if paths else ""
        return self._cache[short_name]


def roles_of(src: str) -> set[str]:
    return {role for pattern, role in SIGNALS if pattern.search(src)}


def token_roles(reader: Reader, type_name: str, kind: str,
                depth: int = 0) -> set[str]:
    """What one token cashes into -- the tag-through, one level at a time.

    Depth-limited at 2: DemonForm applies Strength applies nothing, which is
    the deepest real chain, and an unbounded walk on decompiled source is a
    cycle waiting to happen.
    """
    src = reader.source(type_name)
    if not src:
        return set()
    roles = roles_of(src)
    if kind == "Power":
        if DEBUFF.search(src):
            # A debuff delivers no role of its own; it is the sheets'
            # `utility` voice and A0.2 protects that space from the lint.
            return {"utility"}
        if SCALING_IN_POWER.search(src):
            roles.add("scaling")
    if kind == "Orb":
        # An orb sits on the board and fires on its own schedule. Whatever it
        # does, it does repeatedly -- which is the definition of the scaling
        # half of the charter's demand curve.
        roles.add("scaling")
    if depth < 2:
        for pattern, sub_kind in REACHES:
            for name in set(pattern.findall(src)):
                roles |= token_roles(reader, name, sub_kind, depth + 1)
    return roles


def classify_canon(card: dict, src: str, reader: Reader) -> dict:
    """One canon card -> the same shape tools/role_tempo.py produces for ours."""
    direct = roles_of(src)
    inherited: set[str] = set()
    tokens: list[str] = []
    for pattern, kind in REACHES:
        for name in sorted(set(pattern.findall(src))):
            tokens.append(name)
            inherited |= token_roles(reader, name, kind)
    if SUMMONS.search(src):
        tokens.append("Osty")
        # The summon's own creature model is where its numbers live; the card
        # only says how big. Necrobinder is Furina's designated summon-economy
        # anchor, so this branch is the one her Salon is measured against.
        inherited |= token_roles(reader, "Osty", "Summon") or {"frontload",
                                                               "block"}
    if card["type"] == "Power":
        direct.add("scaling")

    roles = (direct | inherited) or {"utility"}
    cost = card["cost"] if card["cost"] >= 0 else 3     # X costs are -1
    reads_state = bool(ACCUMULATES.search(src)) or bool(
        CONSUMES_ONLY.search(src))
    has_body = bool(card["vars"].get("Damage") or card["vars"].get("Block")
                    or card["vars"].get("Cards") or card["vars"].get("Energy")
                    or card["vars"].get("Summon"))

    early = cost <= 1 and card["type"] != "Power" and has_body
    late = (card["type"] == "Power" or cost >= 3 or reads_state
            or bool(tokens))
    fight = set()
    if early:
        fight.add("early")
    if late:
        fight.add("late")
    if cost == 2 or not fight or fight == {"early", "late"}:
        fight.add("mid")

    rarity = card["rarity"].lower()
    payoff = reads_state or (bool(tokens) and not card["orbs"])
    run = set()
    if rarity in ("basic", "common") or (rarity == "uncommon" and not payoff):
        run.add("early")
    if rarity in ("rare", "ancient") or payoff:
        run.add("late")
    mentions = set(MENTIONS.findall(src))
    for pattern, marker in MECHANIC_MARKERS:
        if pattern.search(src):
            mentions.add(marker)
    return {
        "name": card["name"],
        "rarity": rarity,
        "mentions": sorted(mentions),
        "type": card["type"].lower(),
        "cost": card["cost"],
        "solve": sorted(roles),
        "direct": sorted(direct),
        "inherited": sorted(inherited),
        "tokens": tokens,
        "aoe": card["target"] in ("AllEnemies",),
        "fight": [b for b in rt.FIGHT_BANDS if b in fight],
        "run": [b for b in rt.RUN_BANDS if b in run] or ["early"],
        "mp_only": card["mp_only"],
    }


# --- aggregation ------------------------------------------------------------

def pool_percentages(cards: list[dict]) -> dict:
    """Percentages for one pool. Within-pool only -- the charter's caveat."""
    n = len(cards)
    solve = Counter(r for c in cards for r in c["solve"])
    cells = Counter((r, b) for c in cards for r in c["solve"]
                    for b in c["fight"])
    run_cells = Counter((r, b) for c in cards for r in c["solve"]
                        for b in c["run"])
    rarity_cells = Counter((r, c["rarity"]) for c in cards for r in c["solve"])
    multi = sum(1 for c in cards if len(c["solve"]) > 1)
    return {
        "n": n,
        "multi_solve_pct": round(100 * multi / n, 1),
        "aoe_pct": round(100 * sum(1 for c in cards if c["aoe"]) / n, 1),
        "solve": {r: round(100 * k / n, 1) for r, k in solve.items()},
        "fight_cells": {f"{r}|{b}": round(100 * k / n, 1)
                        for (r, b), k in cells.items()},
        "run_cells": {f"{r}|{b}": round(100 * k / n, 1)
                      for (r, b), k in run_cells.items()},
        "rarity_cells": {f"{r}|{b}": round(100 * k / n, 1)
                         for (r, b), k in rarity_cells.items()},
        "rarities": {r: k for r, k in Counter(
            c["rarity"] for c in cards).items()},
    }


# --- canon PACKAGES (R90/1c) ------------------------------------------------
#
# THE POPULATION FIX. The first pass compared a GItS archetype (11-32 cards,
# all pointed at one plan) against a whole canon character (88 cards spread
# across everything it does). An archetype's per-cell density is structurally
# higher than a whole pool's, so the bar was generous by construction and
# Furina cleared some floors by 40-60 points. R90 (Ruling 1c) rules the
# comparison population to be the canon PACKAGE: the subset of a canon pool
# that touches one mechanic layer. Those run the same order of size as a GItS
# archetype -- so the two sides are finally the same kind of object. Both
# spans move with the DLL and with the sheets, so neither is written down
# here; §5 of docs/role-tempo-baseline.md derives and prints them.
#
# A card is IN a package when its own decompiled body names the layer, on
# either side of the mechanic: the card that applies Poison and the card that
# reads the stack are both poison cards. Membership is therefore structural,
# for four of the five packages.
#
# THE FIFTH IS CURATED, AND THE REASON IS STRUCTURAL TOO (EB-192, R231).
# A Star price is not a call in a card's body at all: it is a second COST
# FIELD on the model (`CardModel.CanonicalStarCost`, checked beside energy in
# `PlayerCombatState.HasEnoughResourcesFor`), and not one spender's rules text
# mentions its price -- the badge carries it. So a regex over card bodies can
# see the eleven generators and NONE of the twenty-three spenders, which is
# how the old `ForgeStars` union came to be half Forge cards. The population
# is instead taken from the decompile-sourced census in
# `docs/current/research/regent-stars-economy.md` -- §2 (every generator),
# §3.5 (every spender), §3.6 (the readers). That note is the authority; the
# lists below are it, and `tier0/tests/test_role_tempo_coverage.py` fails if
# they drift from it or admit a card the census does not carry.
class Curated(frozenset):
    """An explicit member list, cited to a decompile-sourced census.

    Used where structural membership is not merely inconvenient but wrong:
    the layer leaves no mark in the card bodies the classifier can read.
    """


# Every card that GAINS Stars -- census §2 (`PlayerCmd.GainStars`,
# `StarNextTurnPower`, or `GenesisPower`). Eleven.
STAR_GENERATORS = (
    "Venerate", "GatherLight", "Glow", "HiddenCache", "SolarStrike",
    "Convergence", "KnockoutBlow", "RoyalGamble", "ShiningStrike", "BigBang",
    "Genesis",
)
# Every card that carries a Star PRICE -- census §3.5 (`CanonicalStarCost >= 0`
# or `HasStarCostX`). Twenty-three. `RoyalGamble` is deliberately in both
# lists: it pays 5 and gains 9. One census name, the co-op-only
# `Constellation`, is not in `extract_base_game_pool`'s Regent extract at all
# (that pass reads 88 of the pool's 91 cards), so the package materialises at
# 35 of 36 members. The list stays the CENSUS -- membership is its
# intersection with whatever the pool extract carries -- because shrinking the
# census to match an extractor gap would hide the gap.
STAR_SPENDERS = (
    "FallingStar", "AstralPulse", "CloakOfStars", "CrescentSpear",
    "GuidingStar", "Alignment", "Constellation", "Devastate", "GammaBlast",
    "ParticleWall", "Quasar", "Reflect", "Resonance", "RoyalGamble",
    "Stardust", "Comet", "DecisionsDecisions", "DyingStar", "NeutronAegis",
    "SevenStars", "TheSmith", "MeteorShower", "TheSealedThrone",
)
# Cards that READ Stars without spending them -- census §3.6, card side only
# (the two relic payoffs it also lists are not in a card pool). `Radiate`
# scales on Stars gained this turn, `CrescentSpear` on how many Star-costed
# cards the deck holds, and the two Powers are named there by their power
# type, which is what their card applies.
STAR_READERS = ("Radiate", "CrescentSpear", "ChildOfTheStars", "BlackHole")
REGENT_STARS = Curated(STAR_GENERATORS + STAR_SPENDERS + STAR_READERS)

PACKAGES = {
    "silent_poison": (
        "Silent", ("PoisonPower",),
        "Silent's poison package: a stacking counter on the ENEMY that ticks "
        "on its own and is read/multiplied by payoffs. The canon shape for a "
        "meter whose whole job is to grow and then be cashed."),
    "defect_orbs": (
        "Defect", ("OrbLayer", "FocusPower"),
        "Defect's orb package: persistent entities that sit on the board and "
        "fire on their own schedule, plus the Power that scales them. Canon's "
        "BOUNDED-slot precedent (orb slots) and its unbounded scaler (Focus) "
        "are both in here -- the pair R91/2b's bounded/unbounded property is "
        "named against."),
    "necro_summons": (
        "Necrobinder", ("Osty",),
        "Necrobinder's summon package. FURINA'S DESIGNATED ANCHOR, unchanged "
        "from the charter (A1): a card deploys a persistent body, the body "
        "acts on its own schedule, and the pool is built around how many are "
        "out. That is the Salon, in canon."),
    "ironclad_strength": (
        "Ironclad", ("StrengthPower", "VigorPower"),
        "Ironclad's strength package: an UNBOUNDED per-attack additive that "
        "every attack in the deck inherits. The canon unbounded-meter "
        "precedent named in R91/2b."),
    "regent_stars": (
        "Regent", REGENT_STARS,
        "Regent's Stars package: a per-combat bank that cards gain, spend as "
        "a second printed price, and read. The canon shape for a meter with a "
        "spend verb on it. Forge is NOT in here -- it is a separate Regent "
        "mechanic and the old package fused the two (EB-192)."),
}

# WHICH CANON PACKAGE EACH GItS ARCHETYPE IS MEASURED AGAINST.
#
# R90/1c: "an archetype gets compared to the canon thing that is shaped like
# it." This table is that comparison, and it is a DESIGN CLAIM in exactly the
# sense ENTITY_PAYOFFS is -- so it carries the same discipline: one line of
# provenance each, hand-auditable, and no entry is derived from anything the
# lint later measures. An archetype with no named anchor falls back to
# `min over all five packages`, which is the old min-of-canon safety rule with
# the population repaired.
#
# THE ABSENCES ARE DELIBERATE AND THEY ARE THE RISKY PART OF THIS TABLE.
# Leaving an archetype unanchored SILENCES findings, because the default floor
# set is four lax cells -- so every omission below is stated rather than left
# to be discovered:
#
#   */generic      -- the basics-and-glue bucket on all three sheets. It is not
#                     a mechanic package and canon has no analogue for "the
#                     cards that hold the deck together"; measuring it against
#                     one would be inventing a comparison. Default floors.
#   kokomi/assist  -- the co-op archetype. There IS no canon support package:
#                     `support` runs 0-4.5% in every package and is never
#                     linted anyway (one-seat sim, D4). Anchoring it would
#                     manufacture a bar out of noise. Default floors, and its
#                     real finding is R92/3c's support gap, which is a rework
#                     input rather than a lint cell.
#
# Five archetypes lost pinned findings when the population changed, and four of
# those five are in the two classes above. The fifth (kokomi/priest) kept its
# anchor and its findings. The delta is itemised in the sprint log rather than
# absorbed silently.
ARCHETYPE_ANCHORS = {
    ("furina", "salon"): (
        "necro_summons",
        "Charter A1 names Necrobinder Furina's summon-economy anchor and R91 "
        "leaves that designation standing. The Salon deploys typed persistent "
        "bodies that act on their own schedule; so does Osty."),
    ("furina", "fanfare"): (
        "silent_poison",
        "Fanfare is a counter that accrues off other plays and is cashed by "
        "readers -- structurally the poison package's shape, not the summon "
        "package's. Note the shape match is about the METER, not about the "
        "magnitudes: sizing lives in Track B (R90/1b)."),
    ("furina", "spotlight"): (
        "ironclad_strength",
        "The Spotlight is a multiplier applied to a card's printed number, "
        "which is the strength package's job with a selector in front of it."),
    ("klee", "demolition"): (
        "necro_summons",
        "A bomb is a persistent entity placed now that acts later on its own "
        "schedule. Same object class as a summon; the payoff shape is where "
        "the two are compared."),
    ("klee", "spark"): (
        "regent_stars",
        "Sparks accumulate and are SPENT at a threshold for a free attack. A "
        "generate-bank-spend resource is Regent's Stars shape: gained by some "
        "cards, priced onto others, read by a few."),
    ("klee", "reaction"): (
        "silent_poison",
        "Apply a state to the enemy, then play the card that cashes it. That "
        "is the elemental-reaction loop and it is also, exactly, the poison "
        "package's loop."),
    ("kokomi", "priest"): (
        "defect_orbs",
        "The Bake-Kurage is a board entity that pulses on its own each turn "
        "end -- an orb with a jellyfish drawn on it."),
    ("kokomi", "commander"): (
        "regent_stars",
        "Charge is generated, banked and SPENT through Burst. A meter with a "
        "spend verb is Regent's Stars shape, and Stars is the canon bank that "
        "is also a printed price."),
}


def package_members(cards: list[dict],
                    selector: tuple[str, ...] | Curated) -> list[dict]:
    """The package's membership out of one canon pool.

    Two selector shapes, and which one a package uses is a statement about
    the mechanic rather than a convenience: a tuple of MARKERS matches any
    card whose decompiled body names the layer, and a `Curated` set matches
    card NAMES against a census, for a layer that leaves no readable mark in
    a card body at all (EB-192 / R231 -- see REGENT_STARS).
    """
    if isinstance(selector, Curated):
        return [c for c in cards if c["name"] in selector]
    wanted = set(selector)
    return [c for c in cards if wanted & set(c.get("mentions") or ())]


def derive_package_stats(cards_by_char: dict[str, list[dict]]) -> dict:
    """{package: percentages}, computed over the package's own membership."""
    out: dict[str, dict] = {}
    for name, (character, selector, _why) in PACKAGES.items():
        members = package_members(cards_by_char[character], selector)
        if not members:
            continue
        stats = pool_percentages(members)
        stats["character"] = character
        out[name] = stats
    return out


def derive_floors(per_char: dict[str, dict]) -> dict:
    """min-of-canon over the cells every canon pool is non-zero in."""
    floors: dict[str, float] = {}
    identity_cells: dict[str, list[str]] = {}
    keys = set()
    for stats in per_char.values():
        keys |= set(stats["fight_cells"])
    for key in sorted(keys):
        role = key.split("|")[0]
        if role in rt.UNLINTED or role == "support":
            continue
        values = [stats["fight_cells"].get(key, 0.0)
                  for stats in per_char.values()]
        if min(values) <= 0:
            identity_cells[key] = sorted(
                name for name, stats in per_char.items()
                if not stats["fight_cells"].get(key))
            continue
        floors[key] = min(values)
    return {"mandatory": floors, "identity_only": identity_cells}


# --- entry points -----------------------------------------------------------

def derive_package_floors(per_pkg: dict[str, dict]) -> dict:
    """The R90/1c floors: canon PACKAGES as the comparison population.

    Two layers, and the second is the whole point of the ruling:

    * `default` -- the min over all five packages, for a GItS archetype with
      no named anchor. This is the OLD rule with the population repaired, and
      it keeps the standing stop-and-surface guarantee by construction: a
      min-of-canon floor cannot fail any canon package.
    * `anchored` -- for an archetype that names an anchor in
      ARCHETYPE_ANCHORS, the floor is THE ANCHOR PACKAGE'S OWN COVERAGE in
      that cell. Not the min with `default`, and the difference is the whole
      ruling: `default` is by construction <= every package's value, so
      `min(anchor, default)` is identically `default` and anchoring would be a
      no-op wearing a table. An anchored archetype is measured against the
      canon thing shaped like it, at that thing's real number.

      The canon package clears its own floor with EQUALITY and nothing else,
      so the standing rule ("a floor that would fail the canon package itself
      means the derivation is wrong") is satisfied exactly at the boundary,
      with zero margin. `check_package_floors` asserts it every run rather
      than trusting the arithmetic.

    Mandatory/identity split is per population, unchanged in spirit: a cell a
    population sits at ZERO in is an identity statement for anything measured
    against that population, never a debt.
    """
    keys = set()
    for stats in per_pkg.values():
        keys |= set(stats["fight_cells"])
    default: dict[str, float] = {}
    identity: dict[str, list[str]] = {}
    for key in sorted(keys):
        role = key.split("|")[0]
        if role in rt.UNLINTED or role in rt.NEVER_LINTED:
            continue
        values = [stats["fight_cells"].get(key, 0.0)
                  for stats in per_pkg.values()]
        if min(values) <= 0:
            identity[key] = sorted(
                name for name, stats in per_pkg.items()
                if not stats["fight_cells"].get(key))
            continue
        default[key] = min(values)

    anchored: dict[str, dict] = {}
    for (character, archetype), (pkg, _why) in ARCHETYPE_ANCHORS.items():
        stats = per_pkg.get(pkg)
        if not stats:
            continue
        cells: dict[str, float] = {}
        pkg_identity: list[str] = []
        for key in sorted(keys):
            role = key.split("|")[0]
            if role in rt.UNLINTED or role in rt.NEVER_LINTED:
                continue
            have = stats["fight_cells"].get(key, 0.0)
            if have <= 0:
                pkg_identity.append(key)
                continue
            cells[key] = have
        anchored[f"{character}/{archetype}"] = {
            "package": pkg,
            "n": stats["n"],
            "mandatory": cells,
            "identity_only": pkg_identity,
        }
    return {"default": default, "identity_only": identity,
            "anchored": anchored}


def check_package_floors(per_pkg: dict, floors: dict) -> list[str]:
    """STANDING RULE: a floor that fails the canon population is wrong.

    Returns the violations. Empty is the only acceptable result; anything else
    is a stop-and-surface, not a number to adjust.
    """
    bad = []
    for name, stats in per_pkg.items():
        for cell, floor in floors["default"].items():
            have = stats["fight_cells"].get(cell, 0.0)
            if have < floor:
                bad.append(f"default floor {cell} {floor:.1f}% fails canon "
                           f"package {name} ({have:.1f}%)")
    for who, block in floors["anchored"].items():
        stats = per_pkg[block["package"]]
        for cell, floor in block["mandatory"].items():
            have = stats["fight_cells"].get(cell, 0.0)
            if have < floor:
                bad.append(f"{who} floor {cell} {floor:.1f}% fails its own "
                           f"anchor {block['package']} ({have:.1f}%)")
    return bad


def build(from_json: bool) -> dict:
    per_char: dict[str, dict] = {}
    cards_by_char: dict[str, list[dict]] = {}
    if from_json:
        payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        cards_by_char = payload["cards"]
    else:
        dll = extract.game_dll()
        with extract.decompiled_project(dll) as root:
            reader = Reader(root)
            for character in CHARACTERS:
                names, sources = extract.read_pool(root, character)
                # The pool's resolved token types -- what `read_pool` added to
                # `sources` beyond the pool's own names. `parse_card` needs it
                # to admit the third creation spelling (R178).
                tokens = set(sources) - set(names)
                rows = []
                for name in names:
                    card = extract.parse_card(sources[name], name, tokens)
                    if card is None:
                        continue
                    rows.append(classify_canon(card, sources[name], reader))
                cards_by_char[character] = rows
                print(f"  {character}: {len(rows)} cards classified",
                      file=sys.stderr)
    for character, rows in cards_by_char.items():
        per_char[character] = pool_percentages(rows)
    per_pkg = derive_package_stats(cards_by_char)
    package_floors = derive_package_floors(per_pkg)
    violations = check_package_floors(per_pkg, package_floors)
    if violations:
        print("STOP-AND-SURFACE: a package-derived floor fails the canon "
              "package it was derived from. The derivation is wrong; do NOT "
              "adjust the number.", file=sys.stderr)
        for line in violations:
            print("    " + line, file=sys.stderr)
        raise SystemExit(2)
    return {"cards": cards_by_char, "stats": per_char,
            "packages": per_pkg,
            "pool_floors": derive_floors(per_char),
            "floors": package_floors}


def write_local(payload: dict) -> None:
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"  wrote {OUT_JSON.relative_to(REPO)}  "
          "(gitignored -- reference only, do not commit)")


def _cell(key: str) -> str:
    """A cell name inside a markdown TABLE. The `|` in `block|early` is a
    column separator to every renderer alive, so it is escaped here rather
    than in nine call sites -- the first version of this file shipped tables
    that rendered as garbage for exactly that reason."""
    return "`" + key.replace("|", r"\|") + "`"


def _table(per_char: dict, extract_key: str, rows: list[str]) -> list[str]:
    heads = list(per_char)
    out = ["| cell | " + " | ".join(heads) + " |",
           "|---|" + "---|" * len(heads)]
    for key in rows:
        vals = [f"{per_char[c][extract_key].get(key, 0.0):.1f}"
                for c in heads]
        out.append(f"| {_cell(key)} | " + " | ".join(vals) + " |")
    return out


def _span(values) -> str:
    """`lo–hi`, or a bare number when the span is a point. An en dash, to
    match the surrounding prose."""
    lo, hi = min(values), max(values)
    return f"{lo}" if lo == hi else f"{lo}–{hi}"


def gits_archetype_sizes() -> list[int]:
    """Every DECLARED GItS archetype's card count, off the three sheets.

    This is the other half of the R90/1c size comparison, and it is derived
    for the same reason the canon half is: both sides move. The doc used to
    carry a hand-written span for each, and both went stale -- the canon side
    when the DLL grew, the GItS side every time a sheet did.
    """
    sizes: list[int] = []
    for path in rt.SHEETS.values():
        rows = rt.load_rows(path)
        for archetype in rt.declared_archetypes(path):
            sizes.append(len([r for r in rows
                              if archetype in (r.get("archetypes") or [])]))
    return sorted(sizes)


def write_docs(payload: dict) -> None:
    per_char, floors = payload["stats"], payload["floors"]
    cell_keys = sorted({k for s in per_char.values() for k in s["fight_cells"]})
    lines = [
        "# Role x Tempo baseline — the five canon pools",
        "",
        "MACHINE-GENERATED by `tools/canon_role_tempo.py` from the local",
        "`sts2.dll`. Track A / T1+T3 of the Axis-Validity session",
        "(`docs/axis-validity-session-charter.md` §3).",
        "",
        "**Everything below is a PERCENTAGE or a shape.** No card name, no card",
        "text and no number off any card face appears here or in",
        "`docs/role-tempo-floors.yaml` — the per-card classification lives in",
        "`game_ref/role_tempo_canon.json`, which is gitignored reference",
        "material (.gitignore:28) and stays on the machine that has the game.",
        "",
        "## 0. Wiki-vs-DLL reconciliation (counts only)",
        "",
        "The charter's canon numbers were wiki-derived and it flagged them as",
        "running high. They do. Per-pool printed card counts, DLL:",
        "",
        "| pool | DLL total | basic | common | uncommon | rare | ancient | "
        "charter's wiki count |",
        "|---|---|---|---|---|---|---|---|",
    ]
    WIKI = {"Ironclad": 91, "Silent": 92, "Defect": 91,
            "Necrobinder": 91, "Regent": 91}
    for name, stats in per_char.items():
        r = stats["rarities"]
        lines.append(
            f"| {name} | {stats['n']} | {r.get('basic', 0)} | "
            f"{r.get('common', 0)} | {r.get('uncommon', 0)} | "
            f"{r.get('rare', 0)} | {r.get('ancient', 0)} | {WIKI[name]} |")
    total = sum(s["n"] for s in per_char.values())
    over = {name: WIKI[name] - stats["n"] for name, stats in per_char.items()}
    overage = _span(over.values())
    # The shape of the overage, DERIVED. This sentence used to say "flat, not
    # concentrated" in hand-written prose, and the 0.111.0 pools falsified it
    # the day they landed (the overages went 1/1/0/0/0). Nothing here is
    # written down that the table above does not already carry.
    if min(over.values()) == max(over.values()):
        over_shape = (f"and the overage is flat at {max(over.values())} per "
                      "pool rather than concentrated in one of them")
    else:
        over_shape = ("and the overage is uneven — "
                      + ", ".join(f"{name} {n}" for name, n
                                  in sorted(over.items(), key=lambda kv:
                                            (-kv[1], kv[0])))
                      + f", the largest being {max(over.values())}")
    draftable_each = sorted({
        sum(stats["rarities"].get(r, 0)
            for r in ("common", "uncommon", "rare"))
        for stats in per_char.values()})
    draftable = sum(
        stats["rarities"].get(r, 0) for stats in per_char.values()
        for r in ("common", "uncommon", "rare"))
    each = (f"5 × {draftable_each[0]}" if len(draftable_each) == 1
            else " + ".join(str(x) for x in draftable_each))
    mix = sorted({tuple(stats["rarities"].get(r, 0) for r in
                        ("common", "uncommon", "rare", "ancient"))
                  for stats in per_char.values()})
    lines += [""]
    lines += textwrap.wrap(
        f"DLL total across the five pools: **{total}**. The wiki route's own "
        f"per-pool numbers sum to **{sum(WIKI.values())}**, so the wiki runs "
        f"{overage} high per pool, {over_shape}. An overage of that size is "
        "what a wiki-lists-a-few-extra story looks like and not what a "
        "we-are-reading-a-different-pool story would.", 74,
        break_on_hyphens=False, break_long_words=False)
    lines += [
        "",
        "**The charter's \"402 canon cards total\" was an arithmetic slip and is**",
        "**now CORRECTED (R92/3a).** Its own per-pool wiki figures sum to 456;",
        f"the DLL sum is **{total}** and the draftable subtotal is "
        f"**{draftable}**",
        f"({each} common+uncommon+rare). R92/3a corrected the charter header to",
        "the sums of the day (439/410, the 0.107 pools); the live figures are",
        "the two above.",
        "The correction is to a header count and nothing else: **no GItS",
        "coverage percentage moved.** The canon percentages here are all",
        "within-pool, and they do move when the DLL's pools do — the 0.111.0",
        "pools moved many of them.",
        "",
    ]
    if len(mix) == 1:
        c, u, ra, a = mix[0]
        lines += [
            "The pools are startlingly regular: **every** character ships "
            "exactly",
            f"{c} common, {u} uncommon, {ra} rare and {a} ancient. Rarity mix "
            "is therefore",
            "not an identity lever in canon at all — a fact worth having before",
            "anyone argues a GItS pool's shape from its rarity split.",
        ]
    else:
        lines += [
            "The pools no longer share one rarity mix; the per-pool split is "
            "in the",
            "table above. Anyone arguing a GItS pool's shape from its rarity",
            "split should read that table rather than a single canon figure.",
        ]
    lines += [
        "",
        "## 1. `solve` coverage, per pool (% of pool, multi-tagged)",
        "",
    ]
    roles = [r for r in rt.SOLVE]
    heads = list(per_char)
    lines += ["| role | " + " | ".join(heads) + " |",
              "|---|" + "---|" * len(heads)]
    for role in roles:
        lines.append(f"| {role} | " + " | ".join(
            f"{per_char[c]['solve'].get(role, 0.0):.1f}" for c in heads) + " |")
    lines += [
        "| **multi-solve** | " + " | ".join(
            f"{per_char[c]['multi_solve_pct']:.1f}" for c in heads) + " |",
        "| **aoe** (modifier) | " + " | ".join(
            f"{per_char[c]['aoe_pct']:.1f}" for c in heads) + " |",
        "",
        "`support` is present in every canon pool and is the amendment A0 adds",
        "to the vocabulary. It is also the one row here that no prediction in",
        "this track may touch: the sim is one-seat, so support cells are",
        "play-graded only (D4 clause, written in at birth).",
        "",
        "## 2. The (solve × fight-band) matrix (% of pool)",
        "",
    ]
    lines += _table(per_char, "fight_cells", cell_keys)
    lines += [
        "",
        "## 3. The (solve × run-band) matrix (% of pool)",
        "",
    ]
    run_keys = sorted({k for s in per_char.values() for k in s["run_cells"]})
    lines += _table(per_char, "run_cells", run_keys)
    lines += [
        "",
        "## 4. The (solve × rarity) matrix (% of pool)",
        "",
    ]
    rar_keys = sorted({k for s in per_char.values() for k in s["rarity_cells"]})
    lines += _table(per_char, "rarity_cells", rar_keys)
    per_pkg = payload["packages"]
    pkg_keys = sorted({k for s in per_pkg.values() for k in s["fight_cells"]})
    pkg_span = _span([s["n"] for s in per_pkg.values()])
    gits_sizes = gits_archetype_sizes()
    gits_span = _span(gits_sizes)
    lines += [
        "",
        "## 5. The canon PACKAGES — the comparison population (R90/1c)",
        "",
        "**This section is the repair.** §§2–4 above are whole-pool numbers, and",
        "the first lint run applied them to an archetype's sub-pool: a "
        f"{_span([s['n'] for s in per_char.values()])}-card",
        f"canon character spread across everything it does, versus {gits_span}",
        "GItS cards all pointed at one plan. An archetype's per-cell density is",
        "structurally higher, the bar was generous by construction, and Furina",
        "cleared some floors by 40–60 points. R90 rules the comparison",
        "population to be the canon **package** instead.",
        "",
        "A package is the subset of a canon pool whose card bodies name one",
        "mechanic layer, **on either side** — the card that applies Poison and",
        "the card that reads the stack are both poison cards. Membership is",
        "structural (`mentions` off the decompiled body) for four of the five.",
        "",
        "**`regent_stars` is the exception, and it is disclosed rather than",
        "hidden (EB-192 / R231).** A Star price is a second COST FIELD on the",
        "card model, not a call in its body, and no spender’s rules text names",
        "its price — so a body regex sees the generators and none of the",
        "spenders. What this package used to be, `regent_forge`, was a regex",
        "union that fused Stars with the unrelated **Forge** card and ran about",
        "half Forge-only. Membership now comes from the decompile-sourced census",
        "in `docs/current/research/regent-stars-economy.md` (§2 every generator,",
        "§3.5 every spender, §3.6 the readers), held as an explicit list in",
        "`tools/canon_role_tempo.py::REGENT_STARS` and locked to that note by",
        "test. The list is base-game material and stays out of this file, which",
        "is percentages-only exactly as before.",
        "",
        "| package | character | cards | what shape it is |",
        "|---|---|---|---|",
    ]
    for name, (character, _selector, why) in PACKAGES.items():
        if name not in per_pkg:
            continue
        short = why.split(":", 1)[-1].strip().split(".")[0]
        lines.append(f"| `{name}` | {character} | {per_pkg[name]['n']} | "
                     f"{short}. |")
    lines += [
        "",
        f"**The sizes are the point**: {pkg_span} cards against the "
        f"{len(gits_sizes)} declared",
        f"GItS archetypes at {gits_span}. The two sides are finally the same",
        "kind of object. Both spans are derived here, from the packages in the",
        "table above and from the three sheets, so neither can go stale.",
        "",
        "### The (solve × fight-band) matrix, per PACKAGE (% of package)",
        "",
    ]
    lines += _table(per_pkg, "fight_cells", pkg_keys)
    lines += [
        "",
        "Read the `necro_summons` column beside `silent_poison` and the",
        "charter's §2 diagnosis stops being a claim. The summon package covers",
        "block at every band (27.3 / 36.4 / 45.5) and frontload at every band;",
        "the poison package covers almost nothing but damage and late scaling.",
        "They are two legitimate canon shapes, and an archetype measured",
        "against the wrong one is measured against nothing.",
        "",
        "## 5.1 Necrobinder — Furina's designated summon-economy anchor",
        "",
        "Charter A1 named him and **R91 leaves that designation standing**: the",
        "Salon deploys typed persistent bodies that act on their own schedule,",
        "and so does Osty. What moves is only the population — `necro_summons`",
        "(the package) rather than the whole Necrobinder pool.",
        "",
    ]
    necro = payload["cards"]["Necrobinder"]
    summ = [c for c in necro if "Osty" in c["tokens"]]
    pkg_summ = package_members(necro, PACKAGES["necro_summons"][1])
    lines += [
        f"- **{len(summ)} of {len(necro)} cards** SUMMON "
        f"({100*len(summ)/len(necro):.1f}% of the pool); "
        f"**{len(pkg_summ)}** are in the package, i.e. summon *or* read the "
        "summon layer.",
        "- What the summon cashes into: "
        + ", ".join(f"`{r}`" for r in sorted(
            {r for c in summ for r in c["inherited"]}) or ["(nothing)"]) + ".",
        "  Read off the summoned creature's own model, not authored.",
        "- Summon-carrier band spread: "
        + ", ".join(f"`fight:{b}` {100*sum(1 for c in summ if b in c['fight'])/len(summ):.0f}%"
                    for b in rt.FIGHT_BANDS) + ".",
        "",
        "**THE SHAPE THAT MATTERS FOR THE SALON:** the canon summon delivers",
        "more than one role — it attacks *and* shields, visibly — so a card",
        "that deploys one inherits a role at the band it deploys at, whatever",
        "the deck around it looks like. That is the charter's §2 diagnosis with",
        "a number under it, and it is the comparison Furina's typed members are",
        "measured against.",
        "",
        "## 6. The floors, and why they are shaped this way",
        "",
        "Two layers, both derived from §5's packages and nothing else.",
        "",
        "**DEFAULT floors** apply to a GItS archetype that names no anchor. A",
        "cell is mandatory when **all five packages** are non-zero in it and the",
        "floor is the **minimum of the five** — the old rule with the population",
        "repaired. A min-of-canon floor cannot fail any canon package, which is",
        "what the standing stop-and-surface rule requires.",
        "",
        f"**{len(floors['default'])} default-mandatory cells; "
        f"{len(floors['identity_only'])} identity-only cells.** The default set",
        "is small, and that is a finding rather than a weakness: across five",
        "canon packages the only universally-covered jobs are *deal damage at "
        "every band* and *scale late*. Everything else is identity.",
        "",
        "| default mandatory cell | floor (% of population) |",
        "|---|---|",
    ]
    for key, val in sorted(floors["default"].items()):
        lines.append(f"| {_cell(key)} | {val:.1f} |")
    lines += [
        "",
        "| identity-only cell (never linted by default) | packages at zero |",
        "|---|---|",
    ]
    for key, who in sorted(floors["identity_only"].items()):
        lines.append(f"| {_cell(key)} | {', '.join(who)} |")
    lines += [
        "",
        "**ANCHORED floors** apply to an archetype that names a canon package",
        "in `tools/canon_role_tempo.py::ARCHETYPE_ANCHORS`. The floor is **the",
        "anchor package's own coverage** in that cell — not the min with the",
        "default, because the default is by construction ≤ every package and",
        "`min(anchor, default)` would be identically the default, i.e. anchoring",
        "wearing a table and doing nothing. The anchor package clears its own",
        "floor with **equality and nothing else**, so the standing rule is",
        "satisfied exactly at the boundary and `check_package_floors` asserts it",
        "on every run.",
        "",
        "A cell the anchor sits at zero in is an identity statement **for that",
        "archetype** and is not linted for it. That is how Silent-shaped",
        "identities survive: an archetype anchored to the poison package is not",
        "asked for block at fight-early, because canon's poison package has",
        "none either.",
        "",
        "| archetype | anchor package | n | mandatory cells | not linted for it |",
        "|---|---|---|---|---|",
    ]
    for who, block in sorted(floors["anchored"].items()):
        cells = ", ".join(f"{_cell(k)} {v:.1f}"
                          for k, v in sorted(block["mandatory"].items()))
        idn = ", ".join(_cell(k) for k in block["identity_only"]) or "—"
        lines.append(f"| `{who}` | `{block['package']}` | {block['n']} | "
                     f"{cells} | {idn} |")
    lines += [
        "",
        "The anchor claims themselves — one line of provenance each — live in",
        "`ARCHETYPE_ANCHORS` and are design facts, reviewed the same way",
        "`ENTITY_PAYOFFS` is.",
        "",
        "## 7. What this baseline cannot see",
        "",
        "- **No magnitude.** A 3-damage card at fight-early counts exactly as",
        "  much as a 12-damage one. Weighting cells by size would be authoring",
        "  balance numbers, a hard non-goal of this track. Magnitude is Track",
        "  B's curve, and R90/1b moves the Fanfare size-and-timing question",
        "  there explicitly — this file cannot answer it and never could.",
        "- **A package is not a declared archetype.** Canon does not declare",
        "  archetypes at all; a package is the closest structural stand-in and",
        "  it is drawn by mechanic layer, not by plan. Two canon cards in the",
        "  same package can be pulling in different directions.",
        "- **Small populations move fast.** `ironclad_strength` is 8 cards, so",
        "  one card is 12.5 points. Anchored floors off small packages are",
        "  sharp bars; they are reported at full precision rather than rounded",
        "  into comfort.",
        "- **`tools/extract_base_game_pool.py::_solve` disagrees with A0.**",
        "  That function tags AoE damage as `utility`, which the charter's",
        "  amendment retires (`aoe` is a modifier, not a role). It is",
        "  DELIBERATELY NOT CHANGED here: it feeds the reference anchors' seven-",
        "  axis scores, and re-tagging them would move measurements this track",
        "  is a non-goal for. The two classifiers coexist and this note is the",
        "  record that the divergence is known.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    floors_doc = [
        "# Role x tempo coverage floors -- MACHINE-GENERATED by",
        "# tools/canon_role_tempo.py from the five canon PACKAGES in the local",
        "# sts2.dll. Read by tools/lint_role_tempo_coverage.py.",
        "#",
        "# PERCENTAGES ONLY. No card name, no card text, no card number: this",
        "# file is committed and game_ref/ is not (.gitignore:28).",
        "#",
        "# R90/1c: the comparison population is a canon PACKAGE (the cards that",
        "# touch one mechanic layer, generate side and read side both), not a",
        # ASCII spans here: this file is a YAML comment block written in the
        # same plain ASCII as the rest of its header.
        f"# whole canon pool. Packages run {pkg_span.replace('–', '-')} cards, "
        "the same order as",
        f"# a GItS archetype ({gits_span.replace('–', '-')}). Both spans are "
        "derived; see sec. 5",
        "# of docs/role-tempo-baseline.md.",
        "#",
        "# `default:` -- for an archetype with no named anchor. A cell is",
        "# mandatory when all five packages are non-zero in it; the floor is the",
        "# MINIMUM of the five, so no canon package can fail it.",
        "#",
        "# `anchored:` -- for an archetype that names the canon package shaped",
        "# like it (ARCHETYPE_ANCHORS). The floor is that package's OWN coverage,",
        "# which it clears with equality and nothing else. Cells the anchor sits",
        "# at zero in are identity statements for that archetype.",
        "#",
        "# NEVER LINTED: `utility` (protected free space, charter A0.2),",
        "# `support` (one-seat sim, play-graded only, D4), `sustain` (R91/2d --",
        "# canon carries 0.0-2.3% under the structural definition; zero sustain",
        "# is a legal identity).",
        "",
        "packages:",
    ]
    for name in PACKAGES:
        if name not in per_pkg:
            continue
        floors_doc.append(f"  {name}: {{character: {per_pkg[name]['character']}"
                          f", n: {per_pkg[name]['n']}}}")
    floors_doc += ["", "default:", "  mandatory:"]
    for key, val in sorted(floors["default"].items()):
        floors_doc.append(f"    \"{key}\": {val:.1f}")
    floors_doc += ["  identity_only:"]
    for key, who in sorted(floors["identity_only"].items()):
        floors_doc.append(f"    \"{key}\": [{', '.join(who)}]")
    floors_doc += ["", "anchored:"]
    for who, block in sorted(floors["anchored"].items()):
        floors_doc += [f"  \"{who}\":",
                       f"    package: {block['package']}",
                       f"    n: {block['n']}",
                       "    mandatory:"]
        for key, val in sorted(block["mandatory"].items()):
            floors_doc.append(f"      \"{key}\": {val:.1f}")
        floors_doc.append("    identity_only: ["
                          + ", ".join(f'"{k}"' for k in block["identity_only"])
                          + "]")
    floors_doc += ["", "never_linted: [utility, support, sustain]", ""]
    OUT_FLOORS.write_text("\n".join(floors_doc), encoding="utf-8")
    print(f"  wrote {OUT_DOC.relative_to(REPO)} and "
          f"{OUT_FLOORS.relative_to(REPO)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from-json", action="store_true",
                    help="re-derive the docs from game_ref/role_tempo_canon."
                         "json instead of decompiling again")
    args = ap.parse_args(argv)
    payload = build(args.from_json)
    write_local(payload)
    write_docs(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
