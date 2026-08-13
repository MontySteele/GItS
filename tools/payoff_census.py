"""The canonical PAYOFF CENSUS -- R137 step (2a), BACKLOG `EB-56`.

Answers, over the five base-game pools and nothing else: **which cards are
archetype payoffs, and at what rarity** -- and turns that space into candidate
reach bands. It does NOT aim any GItS archetype inside those bands; that is
[USER]'s Q-C answer (`docs/current/QUEUE.md`, row Q-C), not this file's.

    game_ref/payoff_census.json   LOCAL artifact. Per-card classification,
                                  card names included. Gitignored reference
                                  material -- never committed, the same rule
                                  and the same reason as
                                  game_ref/role_tempo_canon.json (.gitignore
                                  "Extracted / decompiled base-game material
                                  is REFERENCE ONLY", §0.3).
    stdout                        The committed-safe aggregate: counts,
                                  percentages, shapes and the derived bands.
                                  Pasted into the review packet by hand.

WHY THE RUBRIC IS IN THIS FILE AND NOT IN PROSE
------------------------------------------------
R137 requires the classification rubric to ship WITH the census for
ratification, "precisely enough that a second classifier would reproduce your
census from it". Prose cannot carry that promise; a predicate can. Every rule
below is one named function, applied mechanically to fields that came off the
decompiled body, and the review packet's rubric section is a reading of THIS
code rather than a parallel description of it.

INPUTS (both local, both gitignored)
------------------------------------
  game_ref/<character>.json       tools/extract_base_game_pool.py output. The
                                  MENTION side: every `<XPower>`/`<XOrb>` type
                                  the body names, its Cmd vocabulary, keywords,
                                  printed vars, rarity, type, cost -- and,
                                  since `EB-63`, the token cards it creates or
                                  names (`creates`, `card_refs`) and what its
                                  computed magnitudes count (`calc_vars`).
                                  Re-extract before censusing: an older
                                  extract is refused, not silently used.
  game_ref/role_tempo_canon.json  tools/canon_role_tempo.py output. Used for
                                  ONE field: `tokens`, the GENERATE side
                                  (`PowerCmd.Apply<X>` / `OrbCmd.Channel<X>`).
                                  The mention/generate split is the whole
                                  hinge of the payoff predicate and the plain
                                  pool dump cannot express it.

USAGE
-----
    python tools/payoff_census.py --game-ref <path-to-a-checkout>/game_ref

A worktree has no `game_ref/` of its own and must never be given one (CLAUDE.md
forbids linking a gitignored asset directory into a worktree), so the path is
an argument rather than a constant.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CHARACTERS = ("Ironclad", "Silent", "Defect", "Necrobinder", "Regent")

# `tier0/constants.py:800`. Quoted, not re-derived: the census converts its
# own counts into REACH through this table and nothing else.
RARITY_ODDS = {"common": 0.60, "uncommon": 0.35, "rare": 0.05}
DRAFTABLE = ("common", "uncommon", "rare")

# --- RUBRIC R1: what a LAYER is -------------------------------------------
#
# Canon declares no archetypes at all, so an archetype cannot be read off a
# label the way a GItS sheet's `archetype:` field is read. R90/1c already
# settled the stand-in: the canon PACKAGE, "the subset of a canon pool whose
# card bodies name one mechanic layer, on either side of the mechanic". This
# file generalises that from the five hand-named packages to every layer the
# pools actually carry, so no archetype is admitted or erased by hand.
#
# Most layers name themselves -- a Power type or an Orb type. Six do not:
# they are command shapes with no type name, and a census that could not see
# them would miss the summon layer, the star layer and the exhaust layer
# outright. A seventh source, the token-creation family, is DERIVED per pool
# rather than listed here -- see `token_markers` below.
def _any(card: dict, *calls: str) -> bool:
    return any(x in card["cmds"] or x in card["generic_cmds"] for x in calls)


# marker -> (does the card TOUCH this layer, does the card MAKE it BIGGER).
# The second predicate is the generate side and it is always "makes the layer
# bigger", never "touches it": `OrbCmd.Evoke` touches the orb layer and
# SHRINKS it, so a rule that read every `OrbCmd.` call as generation would
# classify Defect's cash-in cards as their own enablers.
MARKERS = {
    "Osty": (lambda c: _any(c, "OstyCmd.Summon"),
             lambda c: _any(c, "OstyCmd.Summon")),
    "Stars": (lambda c: _any(c, "ForgeCmd.Forge", "PlayerCmd.GainStars"),
              lambda c: _any(c, "ForgeCmd.Forge", "PlayerCmd.GainStars")),
    "OrbLayer": (lambda c: any(x.startswith("OrbCmd.") for x in
                               c["cmds"] + c["generic_cmds"]),
                 lambda c: _any(c, "OrbCmd.Channel", "OrbCmd.AddSlots")),
    "Exhaust": (lambda c: "Exhaust" in c["keywords"]
                or _any(c, "CardCmd.Exhaust"),
                lambda c: "Exhaust" in c["keywords"]
                or _any(c, "CardCmd.Exhaust")),
    "Discard": (lambda c: _any(c, "CardCmd.Discard", "CardCmd.DiscardAndDraw",
                               "CardSelectCmd.FromHandForDiscard"),
                lambda c: _any(c, "CardCmd.Discard",
                               "CardCmd.DiscardAndDraw",
                               "CardSelectCmd.FromHandForDiscard")),
    "GeneratedCard": (
        lambda c: _any(c, "CardPileCmd.AddGeneratedCardToCombat",
                       "CardPileCmd.AddGeneratedCardsToCombat"),
        lambda c: _any(c, "CardPileCmd.AddGeneratedCardToCombat",
                       "CardPileCmd.AddGeneratedCardsToCombat")),
}

# --- RUBRIC R1(b): the TOKEN-CREATION layer family -------------------------
#
# AMENDED 2026-08-10 by [USER]'s ruling on the EB-56 packet. The six markers
# above are a fixed list, and a whole kind of layer was missing from it: a
# character whose plan is to CONJURE a card that is not in her own pool. The
# Silent's shiv is the plain case. Twelve of her cards name the token and
# eight of them make one, so the layer is as broad as her poison layer -- and
# the census could not see one card of it, because no marker in the list above
# is about card creation.
#
# THE FAMILY IS DERIVED, NOT LISTED. There is no token name in this file, and
# there must not be: a committed tool may not carry a table of base-game card
# names (`tools/extract_base_game_pool.py`, the IP note). Instead the layers of
# a pool are read off the pool's own extraction -- one layer per token type
# some card of that pool creates. Whatever the five pools create gets a layer
# by the same rule, and each layer then faces the same MIN_LAYER admission
# test as every other layer. Nothing is special-cased for the shiv.
#
# WHAT THE EXTRACTION CAN AND CANNOT SEE, stated because it bounds the family.
# `extract_base_game_pool` recognises THREE creation spellings:
# `<Token>.CreateInHand(...)` and `CreateCard<Token>` (`TOKEN_CREATE`), and
# since R178 the static factory `<Token>.Create(...)` (`TOKEN_FACTORY`, which
# is admitted only for a name that resolves to a card type). A pool that makes
# its token some FOURTH way would have token MENTIONS in the extract but no
# token CREATIONS, and admitting such a layer would be the worst available
# error: with the generate side blind, every enabler of the layer would read
# as a payoff of it, which is exactly what P1's strict form exists to prevent.
# So the family is keyed on creation, and a mention-only token is a stated
# blind spot rather than a bad archetype. As of R178 no such blind spot is
# open — the one the packet named (§6.5) was the third spelling, and closing
# it opened one layer with two payoffs and changed no other pool.
TOKEN_PREFIX = "Token:"


def _token_touch(token: str):
    """MENTION side: the card NAMES the token, in any of three spellings.

    It creates one; or it hover-tips the token's card (`FromCard<Token>`),
    which is how canon prints "this makes/uses that card" without making one;
    or its computed magnitude counts cards carrying the token's own CardTag,
    which is a card literally reading the token count off a pile.
    """
    tag = f"CardTag.{token}"

    def touch(card: dict) -> bool:
        return (token in card["creates"]
                or token in card["card_refs"]
                or any(tag in cv["reads"] for cv in card["calc_vars"]))
    return touch


def _token_generate(token: str):
    """GENERATE side: the card MAKES one. Naming it is not making it."""
    return lambda card: token in card["creates"]


def token_markers(pool: list[dict]) -> dict:
    """The token layers of ONE pool, derived from that pool's own extract."""
    return {f"{TOKEN_PREFIX}{token}":
            (_token_touch(token), _token_generate(token))
            for token in sorted({t for c in pool for t in c["creates"]})}

MIN_LAYER = 6          # R3(a). See `sensitivity()` -- 5 / 6 / 8 all reported.
GENERIC_POOLS = 3      # R3(b). Broad in this many pools -> generic, not an
                       # identity. See `archetypes()`.


def mentions(card: dict, markers: dict) -> set[str]:
    """R2, the MENTION side: every layer the card's body so much as names."""
    out = set(card["powers"]) | set(card["orbs"])
    for marker, (touch, _gen) in markers.items():
        if touch(card):
            out.add(marker)
    return out


def generates(card: dict, tokens: list[str], markers: dict) -> set[str]:
    """R2, the GENERATE side: the apply/channel/create half only.

    `tokens` is `canon_role_tempo.classify_canon`'s own generate list --
    `PowerCmd.Apply<X>` and `OrbCmd.Channel<X>`. KNOWN OVERREACH, stated
    rather than patched: that function also folds in
    `HoverTipFactory.FromOrb<X>`, which is a mention and not a channel, so an
    orb layer can read as generated by a card that only points at it. It costs
    the census orb-side P1 payoffs in the Defect pool and nowhere else; the
    packet's judgment-call section names the affected cards.
    """
    out = set(tokens)
    for marker, (_touch, gen) in markers.items():
        if gen(card):
            out.add(marker)
    return out


# --- RUBRIC R4: what a PAYOFF is ------------------------------------------
#
# HOUSE PRECEDENT, not a fresh definition. `DRAFTER_VERSION` 10 fixed the
# fanfare limb of `core_complete` by requiring "at least one card that READS
# the meter", having found that generation coverage and floor coverage are
# "neither of which is a payoff" (`tier0/constants.py`, the v10 stamp); v14
# applied the same fix to the generic limb. A payoff READS. That is the whole
# idea, and the three predicates below are three spellings of it.

def p1_read_not_make(layer: str, ment: set[str], gen: set[str]) -> bool:
    """The card names the layer and creates NOTHING -- so it can only read.

    Strict on purpose. A card that names layer L while generating some OTHER
    token is a SECOND-HAND MENTION (`second_hand`, below), because the usual
    reason a body names a power it does not apply is that it is hover-tipping
    the power its own power grants downstream. Reading those as payoffs would
    turn the plainest enablers in canon into payoffs of their own layer.
    """
    return layer in ment and layer not in gen and not gen


def p2_computed_magnitude(card: dict) -> bool:
    """The printed number is ABSENT because it is computed at play time.

    `new CalculatedDamageVar(...)` carries `CalculationBase` / `ExtraDamage`
    instead of a literal `Damage`. A card whose own output is a function of
    combat state is a payoff of whatever state that is, by construction.
    """
    return "CalculationBase" in card["vars"]


def p3_consumption(card: dict) -> bool:
    """The card SPENDS the layer's accumulated bodies."""
    return any(x.startswith("OrbCmd.Evoke") for x in card["cmds"])


def second_hand(layer: str, ment: set[str], gen: set[str]) -> bool:
    """Names the layer, does not make it, but makes something else."""
    return layer in ment and layer not in gen and bool(gen)


def classify(card: dict, tokens: list[str], markers: dict,
             strict_p2: bool = False) -> dict:
    """`strict_p2` is THE open rubric choice, and it is [USER]'s to settle.

    P2/P3 say "this card's number is computed from state" but not FROM WHICH
    state, so the layer has to be attributed by some rule, and there are
    exactly two defensible ones:

      LOOSE (shipped default) -- attribute to every layer the card mentions.
        Over-attributes: a card carrying the Exhaust keyword whose magnitude
        is really computed off HP loss reads as an Exhaust payoff.
      STRICT (`--strict-p2`) -- attribute only to layers the card does NOT
        generate, so "reads" and "makes" stay disjoint for P2 as they already
        are for P1. Under-attributes: a card that channels an orb AND scales
        off the orb count stops counting as an orb payoff at all.

    Neither is obviously right and picking one silently would be exactly the
    self-serving rubric R137 refuses. Both are computed; the packet reports
    the delta; the ratification names one.
    """
    ment, gen = mentions(card, markers), generates(card, tokens, markers)
    calc, consume = p2_computed_magnitude(card), p3_consumption(card)
    payoff_of, second, generator_of = set(), set(), set()
    for layer in ment:
        state_read = (calc or consume) and not (strict_p2 and layer in gen)
        if p1_read_not_make(layer, ment, gen) or state_read:
            payoff_of.add(layer)
        elif second_hand(layer, ment, gen):
            second.add(layer)
        else:
            generator_of.add(layer)
    return {
        "name": card["name"],
        "rarity": card["rarity"].lower(),
        "type": card["type"].lower(),
        "cost": card["cost"],
        "mentions": sorted(ment),
        "generates": sorted(gen),
        "payoff_of": sorted(payoff_of),
        "second_hand_of": sorted(second),
        "generator_of": sorted(generator_of),
        "p1": sorted(l for l in ment if p1_read_not_make(l, ment, gen)),
        "p2": calc,
        "p3": consume,
        # R5: a P2/P3 payoff that names no layer is a payoff of something the
        # extraction cannot see (a card-NAME subset, a pile size). Counted,
        # never assigned to an archetype.
        "unresolved": (calc or consume) and not ment,
    }


# --- RUBRIC R3: which layers are ARCHETYPES -------------------------------

def archetypes(rows: list[dict], min_layer: int = MIN_LAYER) -> dict:
    """A layer is an archetype of its pool iff it is BROAD.

    BROAD: at least `min_layer` cards in the pool mention it, on either side
    of the mechanic. Below that it is a card, not a plan. The smallest package
    R90/1c ratified is 8 cards (`ironclad_strength`); 6 is deliberately one
    notch more permissive, so a real-but-small canon archetype is not erased
    by the threshold. `sensitivity()` reports 5 / 6 / 8 side by side.

    BREADTH IS THE ONLY ADMISSION RULE, and the first draft of this file got
    that wrong. It also required "at least one payoff", on the reasoning that
    an uncashed layer is a common effect rather than a plan. Two things broke.
    (i) It made every admitted archetype carry >= 1 payoff BY CONSTRUCTION, so
    the floor of the band derivation would have been a definition wearing a
    measurement's clothes. (ii) It silently deleted the Necrobinder summon
    layer -- every summon card GENERATES, and the cards that cash the summon
    count read a board state the extraction cannot see, so the layer scored
    zero payoffs and vanished. A zero is a FINDING here, not an exclusion
    criterion, and `unresolved` is where its missing half is counted.

    Generic-vs-identity is reported, never used to admit or reject: a layer
    that is broad in `GENERIC_POOLS` or more of the five pools is a shared
    effect of the game (Exhaust, Vulnerable, Weak, Strength), not a pool's
    identity. `label_generic()` applies that across pools.
    """
    breadth = Counter(l for r in rows for l in r["mentions"])
    out = {}
    for layer, k in breadth.items():
        if k >= min_layer:
            out[layer] = {
                "mentions": k,
                "payoffs": [r for r in rows if layer in r["payoff_of"]],
                "generators": [r for r in rows if layer in r["generator_of"]],
                "second_hand": [r for r in rows
                                if layer in r["second_hand_of"]],
            }
    return out


# --- RUBRIC R7: census -> candidate reach bands ---------------------------

def offer_reach(payoffs: list[dict], pool: list[dict]) -> float:
    """Expected payoffs of ONE layer per single card offered, under
    `RARITY_ODDS`.

    This is the conversion the whole sprint turns on. Curtain Call's
    prediction 4 measured that promoting payoffs OUT of common CUTS reach,
    because reach is not a count of payoffs -- it is a count weighted by how
    often the offer stream shows them. That weighting is exactly this sum:

        sum over rarity r of  ODDS[r] * payoffs_at_r / pool_size_at_r

    Basic and Ancient are excluded: neither is in the normal card-reward
    stream, so neither has an offer weight to carry.

    WHAT THIS NUMBER IS AND IS NOT. It is the chance that ONE offered card is
    a payoff of L -- i.e. the BLIND-DRAFT floor. It is not what a plan-
    committed deck reaches, because a committed drafter picks on-plan and
    that selection model is not ratified anywhere. The census therefore
    brackets rather than predicts: floor = this number times cards drafted,
    ceiling = the layer's whole draftable payoff count (a perfect drafter
    takes them all). Every canon archetype lives inside its own bracket, and
    the bracket is the band.
    """
    sizes = Counter(c["rarity"].lower() for c in pool)
    got = Counter(p["rarity"] for p in payoffs)
    return sum(RARITY_ODDS[r] * got.get(r, 0) / sizes[r]
               for r in DRAFTABLE if sizes.get(r))


CENSUS_FIELDS = ("creates", "card_refs", "calc_vars")


def require_census_fields(pool: list[dict], character: str) -> None:
    """Refuse a pool extracted BEFORE the token layer existed.

    The three fields below arrived with `EB-63` on 2026-08-10. An extract made
    before that has none of them, and every token predicate would then read
    "this card creates nothing" -- so the run would quietly produce the OLD
    census while claiming the AMENDED rubric. Same failure, and the same
    refusal, as the pool/canon name check below: a stale input is not a small
    input, it is a different world.
    """
    missing = [f for f in CENSUS_FIELDS if pool and f not in pool[0]]
    if missing:
        raise SystemExit(
            f"STOP: the {character} extract predates the token-creation layer "
            f"(no {', '.join(missing)} on its cards). Re-run "
            f"tools/extract_base_game_pool.py --characters "
            f"Ironclad,Silent,Defect,Necrobinder,Regent before censusing.")


def build(game_ref: Path, strict_p2: bool = False) -> dict:
    canon = json.loads((game_ref / "role_tempo_canon.json")
                       .read_text(encoding="utf-8"))["cards"]
    out: dict[str, dict] = {}
    for character in CHARACTERS:
        pool = json.loads((game_ref / f"{character.lower()}.json")
                          .read_text(encoding="utf-8"))
        tokens = {c["name"]: c["tokens"] for c in canon[character]}
        missing = [c["name"] for c in pool if c["name"] not in tokens]
        if missing:
            raise SystemExit(
                f"STOP: {character} pool and role_tempo_canon.json disagree on "
                f"{len(missing)} card names -- the two extractions are not of "
                f"the same pool and the mention/generate split would be "
                f"joined across worlds. First few: {missing[:5]}")
        require_census_fields(pool, character)
        markers = MARKERS | token_markers(pool)
        rows = [classify(c, tokens[c["name"]], markers, strict_p2)
                for c in pool]
        arch = archetypes(rows)
        out[character] = {
            "n": len(rows),
            "min_layer": MIN_LAYER,
            "strict_p2": strict_p2,
            "rarities": dict(Counter(r["rarity"] for r in rows)),
            "cards": rows,
            "archetypes": {
                layer: {
                    "mentions": blk["mentions"],
                    "payoff_names": [p["name"] for p in blk["payoffs"]],
                    "payoffs_by_rarity": dict(
                        Counter(p["rarity"] for p in blk["payoffs"])),
                    "payoffs_draftable": sum(
                        1 for p in blk["payoffs"]
                        if p["rarity"] in DRAFTABLE),
                    "generators": len(blk["generators"]),
                    "second_hand": [s["name"] for s in blk["second_hand"]],
                    "offer_reach": round(offer_reach(blk["payoffs"], pool), 5),
                }
                for layer, blk in sorted(arch.items())
            },
            "unresolved": [r["name"] for r in rows if r["unresolved"]],
        }
    label_generic(out)
    return out


def label_generic(payload: dict) -> None:
    """R3(b), reported not enforced: broad in >=GENERIC_POOLS pools = generic.

    Vulnerable, Weak, Strength and Exhaust are things the GAME does; Poison,
    Doom, Orbs, Stars and Osty are things a CHARACTER is. The census keeps
    both and says which is which, because a band derived over the generic
    layers would be a band about Slay the Spire and not about an archetype.
    """
    spread = Counter(l for blk in payload.values() for l in blk["archetypes"])
    for blk in payload.values():
        for layer, a in blk["archetypes"].items():
            a["pools_broad_in"] = spread[layer]
            a["kind"] = "generic" if spread[layer] >= GENERIC_POOLS \
                else "identity"


def sensitivity(game_ref: Path) -> dict:
    """R3(a) is a threshold, so it gets reported at three settings, not one."""
    canon = json.loads((game_ref / "role_tempo_canon.json")
                       .read_text(encoding="utf-8"))["cards"]
    out: dict[int, dict[str, int]] = {}
    for k in (5, 6, 8):
        per = {}
        for character in CHARACTERS:
            pool = json.loads((game_ref / f"{character.lower()}.json")
                              .read_text(encoding="utf-8"))
            tokens = {c["name"]: c["tokens"] for c in canon[character]}
            require_census_fields(pool, character)
            markers = MARKERS | token_markers(pool)
            rows = [classify(c, tokens[c["name"]], markers) for c in pool]
            per[character] = len(archetypes(rows, k))
        out[k] = per
    return out


def report(payload: dict, sens: dict) -> None:
    """The COMMITTED-SAFE view: counts, percentages, shapes.

    No card text and no number off any card face is printed here. Card NAMES
    appear only where the packet's judgment-call sections need them, which is
    the same line `docs/reserved-card-names.txt` and the tier0 atlas already
    stand on; the per-card sheet stays in the gitignored JSON.
    """
    print("=== PER-POOL CENSUS =======================================")
    for character, blk in payload.items():
        arch = blk["archetypes"]
        n_pay = len({p for a in arch.values() for p in a["payoff_names"]})
        print(f"\n{character}: {blk['n']} cards, {len(arch)} archetypes, "
              f"{n_pay} distinct payoff cards, "
              f"{len(blk['unresolved'])} unresolved-layer payoffs")
        print(f"  {'archetype':<20}{'kind':>9}{'ment':>5}{'gen':>5}{'pay':>5}"
              f"{'  C/U/R':>10}{'2nd':>5}{'reach/offer':>13}")
        for layer, a in sorted(arch.items(),
                               key=lambda kv: (kv[1]["kind"],
                                               -kv[1]["offer_reach"])):
            r = a["payoffs_by_rarity"]
            cur = f"{r.get('common',0)}/{r.get('uncommon',0)}/{r.get('rare',0)}"
            print(f"  {layer:<20}{a['kind']:>9}{a['mentions']:>5}"
                  f"{a['generators']:>5}"
                  f"{len(a['payoff_names']):>5}{cur:>10}"
                  f"{len(a['second_hand']):>5}{a['offer_reach']:>13.4f}")

    print("\n=== R3(a) THRESHOLD SENSITIVITY (archetypes per pool) =====")
    print(f"  {'min_layer':<12}" + "".join(f"{c:>14}" for c in CHARACTERS))
    for k, per in sens.items():
        print(f"  {k:<12}" + "".join(f"{per[c]:>14}" for c in CHARACTERS))

    print("\n=== R7 CANDIDATE BANDS ====================================")
    print("  Derived over IDENTITY archetypes carrying >=1 payoff. Generic")
    print("  layers are excluded (a band over Exhaust/Vulnerable would be a")
    print("  band about the game, not about an archetype); a zero-payoff")
    print("  identity layer is a blind-spot finding, listed below the bands.")
    rows = [(c, l, a) for c, blk in payload.items()
            for l, a in blk["archetypes"].items()
            if a["kind"] == "identity" and a["payoff_names"]]
    zeros = [(c, l) for c, blk in payload.items()
             for l, a in blk["archetypes"].items()
             if a["kind"] == "identity" and not a["payoff_names"]]
    counts = sorted(a["payoffs_draftable"] for _, _, a in rows)
    reaches = sorted(a["offer_reach"] for _, _, a in rows)

    def pct(xs, q):
        return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]
    print(f"  n = {len(rows)} canon archetypes across 5 pools")
    print("\n  AXIS 1 -- SUPPLY: draftable payoff cards the pool prints for")
    print("  the layer. This is the CEILING a perfect drafter could reach.")
    print("    min %d   p25 %d   median %d   p75 %d   max %d"
          % (counts[0], pct(counts, .25), pct(counts, .5), pct(counts, .75),
             counts[-1]))
    print("\n  AXIS 2 -- OFFER: P(one offered card is a payoff of the layer),")
    print("  weighted by RARITY_ODDS. Curtain Call's prediction 4 is a")
    print("  statement about THIS axis, not axis 1.")
    print("    min %.4f  p25 %.4f  median %.4f  p75 %.4f  max %.4f"
          % (reaches[0], pct(reaches, .25), pct(reaches, .5),
             pct(reaches, .75), reaches[-1]))
    print("    as P(a 3-card reward screen shows >=1): min %.1f%%  "
          "median %.1f%%  max %.1f%%"
          % (100 * (1 - (1 - reaches[0]) ** 3),
             100 * (1 - (1 - pct(reaches, .5)) ** 3),
             100 * (1 - (1 - reaches[-1]) ** 3)))
    print("\n  THE BANDS -- blind-draft FLOOR (offer x N) to supply CEILING:")
    print(f"  {'band':<18}{'offer':>8}{'ceil':>6}" +
          "".join(f"{'N=' + str(n):>14}" for n in (15, 20, 25)))
    for label, q in (("LOW (p25)", .25), ("MEDIUM (median)", .5),
                     ("HIGH (p75)", .75), ("TOP (max)", 1.0)):
        v, c = pct(reaches, q), pct(counts, q)
        print(f"  {label:<18}{v:>8.4f}{c:>6}" +
              "".join(f"{str(round(v * n, 2)) + '-' + str(c):>14}"
                     for n in (15, 20, 25)))
    print("\n  Identity archetypes with ZERO payoffs in view (blind spot, not")
    print("  a zero): " + (", ".join(f"{c}/{l}" for c, l in zeros) or "none"))
    print("  R5 unresolved-layer payoffs, per pool: " + ", ".join(
        f"{c} {len(blk['unresolved'])}" for c, blk in payload.items()))
    print("\n  These are the SPACE, not an aim. Which roster archetype sits")
    print("  high / medium / low inside it is [USER]'s Q-C answer (R137 2c).")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game-ref", type=Path, default=REPO / "game_ref",
                    help="path to a checkout's gitignored game_ref/ "
                         "(a worktree has none of its own)")
    ap.add_argument("--strict-p2", action="store_true",
                    help="the STRICT P2/P3 layer-attribution variant (see "
                         "classify.__doc__) -- the open rubric choice")
    ap.add_argument("--no-write", action="store_true",
                    help="report only; do not write the local JSON")
    args = ap.parse_args(argv)
    if not args.game_ref.exists():
        sys.exit(f"no game_ref at {args.game_ref} -- pass --game-ref")
    payload = build(args.game_ref, args.strict_p2)
    if not args.no_write:
        out = args.game_ref / ("payoff_census_strict.json"
                               if args.strict_p2 else
                               "payoff_census.json")
        out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        print(f"wrote {out}  (gitignored -- reference only, never commit)\n")
    report(payload, sensitivity(args.game_ref))
    return 0


if __name__ == "__main__":
    sys.exit(main())
