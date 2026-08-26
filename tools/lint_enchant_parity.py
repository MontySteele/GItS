#!/usr/bin/env python3
"""Parity lint: tier0's enchantment vocabulary vs what the mod's cards allow.

WHY THIS EXISTS (EB-84). `BACKLOG` opened the C# enchantment leg on the
premise that "no C# enchant surface exists at all". That premise is wrong in
the most useful possible way: the surface exists and it is the *base game's*.
`sts2.dll` ships `MegaCrit.Sts2.Core.Models.EnchantmentModel` plus a concrete
class for every one of the eight enchantments tier0's CATALOG names, the deck
enchant screen that grants them, save/load, and the hooks that pay them out
(`Hook.ModifyDamage` / `Hook.ModifyBlock` consult `cardSource.Enchantment`
before any other modifier). LAW's standing rule -- sweep BaseLib and the
decompiled game before building infrastructure -- says the mod must not grow
a second one. So there is nothing to *port*.

What there IS, and what this lint holds, is an ELIGIBILITY correspondence.
Every one of the eight gates on a fact about the card:

    Sharp / Vigorous / Corrupted   CanEnchantCardType == Attack
    Souls' Power                   card carries the LOCAL Exhaust keyword
    Nimble                         card.GainsBlock
    Swift / Sown / Perfect Fit     no card-level restriction at all

and tier0 gates the same eight on its own predicates in
`tier0.content.enchantments.CATALOG`. Where the two disagree, one of two
things is true and both are worth knowing: either a mod card is misreporting
a fact about itself to the game (a defect this repo can fix), or tier0's
predicate does not match the enchantment the game actually ships (a sim-side
finding, and NOT something to paper over on the C# side).

The three card-level facts are readable from committed source, so this runs
on a runner with no game installed -- the same bargain
`test_roster_runtime_contracts.py` takes. The game-side rules are transcribed
into GAME_RULES below with their decompiled citation; that table is the part
a human re-checks when the game updates, and STATE pins the build it was
read against.

Run: python tools/lint_enchant_parity.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tier0.content import enchantments, loader        # noqa: E402
from tools.gen_klee_cards import pascal               # noqa: E402

MOD = REPO / "klee-mod" / "KleeCode" / "Cards"

# Where a card class may live: the generated tree and its hand-written
# neighbour, per profile. Order matters only for the error message.
CARD_DIRS = [
    MOD, MOD / "Generated",
    MOD / "Furina", MOD / "Furina" / "Generated",
    MOD / "Kokomi", MOD / "Kokomi" / "Generated",
]
MANIFESTS = [
    MOD / "Generated" / "manifest.json",
    MOD / "Furina" / "Generated" / "manifest.json",
    MOD / "Kokomi" / "Generated" / "manifest.json",
]

# The game's own eligibility rule for each shipped enchantment, transcribed
# from the decompiled `MegaCrit.Sts2.Core.Models.Enchantments.*` (v0.107.1,
# the build STATE pins). The value is the card fact the rule reads:
#
#   "attack"  -> CanEnchantCardType(cardType) == CardType.Attack
#   "exhaust" -> CanEnchant: GetKeywordsWithSources(Local) has Exhaust
#   "block"   -> CanEnchant: card.GainsBlock
#   None      -> base CanEnchant only (no card-level restriction)
#
# Base CanEnchant additionally refuses Status / Curse / Quest and a card that
# already holds an enchantment; tier0's `eligible` refuses curse / status /
# kit cards for the same reason, so those two agree by construction and are
# not re-checked per card here.
GAME_RULES = {
    "sharp": "attack",          # Sharp.CanEnchantCardType
    "vigorous": "attack",       # Vigorous.CanEnchantCardType
    "corrupted": "attack",      # Corrupted.CanEnchantCardType
    "souls_power": "exhaust",   # SoulsPower.CanEnchant
    "nimble": "block",          # Nimble.CanEnchant -> card.GainsBlock
    "swift": None,              # Swift: no override
    "sown": None,               # Sown: no override
    "perfect_fit": None,        # PerfectFit: no override
}

# Accepted disagreements between tier0's predicate and the game's rule. Each
# entry is (enchantment, sim-says, why) and each one is a finding somebody
# already looked at -- the point of the table is that an UNLISTED
# disagreement fails the lint. Nothing here is fixable on the C# side; every
# row is tier0's model of an enchantment the game implements differently.
#
# THE TABLE IS EMPTY, and that is the EB-85 result rather than a table nobody
# has filled in. The EB-84 sweep recorded three eligibility splits here --
# Nimble Skill-only, Nimble on `block_next_turn`, Swift Power-only -- and all
# three were tier0 being narrower than the shipped enchantment. They were
# stamp-gated (each moves what an enchant event may target) and were fixed in
# the RUNTEMPLATE window on 2026-08-13, so every one of the eight now agrees
# on every mod card. An entry added here in future needs the same thing the
# three had: the decompiled class, the card fact it reads, and why the sim
# cannot follow it.
KNOWN_DIVERGENCES: dict[tuple[str, str], str] = {}


# ELIGIBILITY is not the only correspondence that can drift. An enchantment
# that pays out through a damage hook also carries a PRECONDITION on the hit
# it is willing to modify, and that precondition is a second, independent
# thing each engine states in its own vocabulary. Corrupted is the one shipped
# enchantment that has one (EB-85's sixth finding, deliberately left outside
# the EB-84 eligibility batch):
#
#     MegaCrit.Sts2.Core.Models.Enchantments.Corrupted
#         public override decimal EnchantDamageMultiplicative(DamageProps props)
#         {
#             if (!props.IsPoweredAttack()) return 1m;
#             ...
#
# and tier0 says the same thing by placing its multiplier inside
# `engine/effects._op_damage`'s `card.type == "attack"` branch. The two agree
# TODAY and nothing pinned it, which is exactly the shape that rots: either
# side can move alone and the sim silently starts paying Corrupted on a hit
# the game refuses, or stops paying one it allows.
#
# THE TABLE IS THE PIN, and `tier0/tests/test_eb85_corrupted_precondition.py`
# is what bites on it. Same bargain as GAME_RULES above: the C# half is a
# transcription carrying its decompiled citation, because decompiling
# `sts2.dll` needs the game installed and ilspycmd
# (`tools/extract_base_game_pool.py`) and this repo's gates run where neither
# exists. What the pin buys is that the transcription and tier0's branch
# cannot move INDEPENDENTLY -- the test hard-codes the guard line it expects
# to read here, so re-transcribing after a re-decompile goes red until
# somebody re-derives the sim side too, and an AST read of `effects.py` goes
# red if the multiplier leaves the branch or a second unguarded reader of the
# rider appears.
#
#   cs_class / cs_hook -- the decompiled class and the hook the guard opens
#   cs_guard           -- that opening early-return, verbatim
#   cs_predicate       -- the DamageProps predicate the guard reads
#   sim_branch         -- the `effects.py` `if` test that must enclose the
#                         sim's rider read
#   sim_field          -- the `state.Card` rider field that branch guards
GAME_DAMAGE_PRECONDITIONS: dict[str, dict[str, str]] = {
    "corrupted": {
        "cs_class": "MegaCrit.Sts2.Core.Models.Enchantments.Corrupted",
        "cs_hook": "EnchantDamageMultiplicative",
        "cs_guard": "if (!props.IsPoweredAttack()) return 1m;",
        "cs_predicate": "IsPoweredAttack",
        "sim_branch": 'card.type == "attack"',
        "sim_field": "enchant_damage_mult",
        "why": (
            "IsPoweredAttack() is the game's 'this is a powered Move hit off "
            "an Attack card' test. tier0 has no DamageProps, and its nearest "
            "total statement of the same fact is the card-type branch that "
            "already gates every other attack-only damage rider. Corrupted's "
            "own 2 HP self-damage row is dealt Unblockable | Unpowered | Move "
            "in game and so fails the C# guard; in tier0 it fails the branch "
            "too, because a `target: self` damage op returns out of "
            "`_op_damage` before the branch is reached."),
    },
}


# `blocked` carries TWO different facts under one key, and until EB-69 they
# were indistinguishable because only one of them had ever occurred. A card
# blocked with the reason "hand-written" IS shipped -- codegen skips it because
# a human wrote the class (Klee's eight, `let_the_people_rejoice`,
# `ceremonial_garment`). A card blocked with any OTHER reason names an
# unimplemented C# runtime grammar and ships NO CLASS AT ALL; EB-69 produced
# the first five of those (`grant_sly_this_turn`, a `discards_this_turn`
# CalculatedVar, a `1_per_2_charge` block rider, and `recall_to_draw` from
# discard -- see BACKLOG `EB-122`). Folding both into "ids the mod ships a
# class for" made this lint demand a .cs file that codegen deliberately did not
# write, so the reason string is read rather than assumed.
HAND_WRITTEN_REASON = "hand-written"


def _mod_card_ids() -> set[str]:
    """Every sheet id the mod ships a class for (generated or hand-written)."""
    ids: set[str] = set()
    for path in MANIFESTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        ids.update(data.get("generated", []))
        ids.update(data.get("companions", []))
        ids.update(data.get("guest_stars", []))
        ids.update(cid for cid, why in (data.get("blocked") or {}).items()
                   if why == HAND_WRITTEN_REASON)
    return ids


def _source_index() -> dict[str, Path]:
    """Class name -> its .cs file. First directory wins; none collide today."""
    out: dict[str, Path] = {}
    for d in CARD_DIRS:
        for p in sorted(d.glob("*.cs")):
            out.setdefault(p.stem, p)
    return out


_CANONICAL_VARS = re.compile(
    r"protected override IEnumerable<DynamicVar> CanonicalVars =>(.*?);\s*\n\s*\n",
    re.S)
_BLOCK_VAR = re.compile(r"\bnew (?:Calculated)?BlockVar\(")
_CTOR_TYPE = re.compile(r":\s*base\([^)]*?CardType\.(\w+)")


def cs_facts(text: str) -> dict:
    """The three card-level facts the game's enchant rules read.

    Read from source text rather than from the sheet on purpose: the sheet is
    what tier0 already knows, and the whole question is whether what the mod
    COMPILED still says the same thing.
    """
    m = _CANONICAL_VARS.search(text)
    canonical = m.group(1) if m else ""
    ctor = _CTOR_TYPE.search(text)
    return {
        # BaseLib's CustomCardModel auto-detects GainsBlock from a
        # BlockVar/CalculatedBlockVar in CanonicalVars; a card whose Block is
        # conditional declares the override by hand (gen_klee_cards, EB-84).
        "block": bool(_BLOCK_VAR.search(canonical))
                 or "override bool GainsBlock => true" in text,
        "attack": ctor is not None and ctor.group(1) == "Attack",
        # `exhaust: true` rides CanonicalKeywords, which is a LOCAL keyword
        # source -- the one SoulsPower.CanEnchant reads.
        "exhaust": "CardKeyword.Exhaust" in text,
        "type_found": ctor is not None,
    }


def sim_reason(name: str, card, sim_ok: bool) -> str | None:
    """Which KNOWN_DIVERGENCES key explains THIS card's split, if any.

    Deliberately narrow, and currently answers None for everything, because
    KNOWN_DIVERGENCES is empty (EB-85 closed all three). The narrowness is
    the lesson worth keeping: a reason that fits any card of the right type
    swallows the real splits the lint exists to catch -- the first draft
    returned "block-next-turn" for every Skill and so passed while a
    hand-broken GainsBlock sat in the tree. Whoever adds the next row adds
    the branch that recognises it HERE, keyed on the specific card fact.
    """
    return None


def findings() -> list[str]:
    out: list[str] = []

    catalog = set(enchantments.CATALOG)
    for name in sorted(catalog - set(GAME_RULES)):
        out.append(
            f"UNMAPPED ENCHANTMENT: {name!r} is in tier0's CATALOG but has no "
            f"row in GAME_RULES. The vocabulary is the base game's; adding a "
            f"name here means naming the game class it rides and the card "
            f"fact its CanEnchant reads.")
    for name in sorted(set(GAME_RULES) - catalog):
        out.append(
            f"STALE ENCHANTMENT: {name!r} has a GAME_RULES row but tier0's "
            f"CATALOG no longer holds it. Either the sim dropped it or it was "
            f"renamed; a rule with no sim twin checks nothing.")

    sources = _source_index()
    index = loader._card_index()
    checked = 0
    for cid in sorted(_mod_card_ids()):
        card = index.get(cid)
        if card is None:
            out.append(
                f"MISSING SHEET ROW: the mod manifests list {cid!r} but no "
                f"tier0 card loads under that id.")
            continue
        path = sources.get(pascal(cid))
        if path is None:
            out.append(
                f"MISSING CLASS: {cid!r} is manifested but no "
                f"{pascal(cid)}.cs exists under klee-mod/KleeCode/Cards/.")
            continue
        if card.kit_card or card.rarity == "curse" or card.type == "status":
            # tier0 refuses these three outright; the game has no card fact
            # that says "kit card", it simply never puts one in a deck, and
            # the enchant screen offers deck cards only. Comparing them would
            # report a disagreement about a card neither engine can enchant.
            continue
        facts = cs_facts(path.read_text(encoding="utf-8"))
        if not facts["type_found"]:
            out.append(
                f"UNREADABLE CARD TYPE: {path.name} declares no "
                f"`CardType.<x>` in its base constructor call, so the "
                f"Attack-only enchantments cannot be checked against it.")
            continue
        checked += 1
        for name in sorted(catalog & set(GAME_RULES)):
            rule = GAME_RULES[name]
            game_ok = True if rule is None else facts[rule]
            sim_ok = enchantments.eligible(card, name)
            if game_ok == sim_ok:
                continue
            key = (name, sim_reason(name, card, sim_ok))
            if key in KNOWN_DIVERGENCES:
                continue
            out.append(
                f"ELIGIBILITY SPLIT on {cid!r} ({path.name}) for {name!r}: "
                f"tier0 says {sim_ok}, the game's rule ({rule or 'none'}) "
                f"says {game_ok}. Either the class misreports the fact -- "
                f"GainsBlock, CardType, the Exhaust keyword -- or tier0's "
                f"predicate has drifted from the shipped enchantment. Fix the "
                f"class, or record the divergence in KNOWN_DIVERGENCES with "
                f"the reason.")
    if not checked:
        out.append(
            "NOTHING CHECKED: no manifested card resolved to a readable "
            "class. The lint would pass vacuously; that is a failure.")
    return out


def main() -> int:
    bad = findings()
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    print(f"enchant parity OK: {len(enchantments.CATALOG)} enchantments, "
          f"{len(_mod_card_ids())} mod cards, "
          f"{len(KNOWN_DIVERGENCES)} recorded divergence(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
