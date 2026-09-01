"""Payoff reach, all nine roster archetypes — the registered sprint's reader.

The instrument of `review/records/payoff-reach-reregistration.md` §6.4, built
because that section names the build as owed: the only committed reach printer
is `tier05/exp_furina_ghostcheck.py`, whose payoff column is
`draft._reads_fanfare` — Furina-fanfare-specific, and blind to eight of the
nine arms. This file is the generic one. It ADDS NO CLASSIFIER and reads no
new field: supply comes from the sheets' own `role: payoff` + `archetypes`,
and realized reach comes from `draft._generic_core_counts`, the function
`core_complete` and `_core_progress` already share. Both legs classify payoff
membership through ONE shared predicate, `draft.is_on_plan_payoff` — §6.5's
amended `T3` (`M28`, R196) fires on a disagreement between the two legs, so a
second copy of that rule here would manufacture the fault it detects.

READER AND PRINTER ONLY. Nothing here scores a draft, and the registration's
`DRAFTER_VERSION = 14` pin is untouched — running this cannot move a pick.

Two legs, exactly as §6.4 states them:

  LEG 1, STATIC — over the three committed GItS sheets, per archetype:
    * draftable payoff SUPPLY (`role: payoff` and the archetype tag, over the
      reward pool, so basic / token / kit / companion rows are out);
    * the census R7 OFFER figure, same formula and the same `RARITY_ODDS`;
    * the Q-B (B-ii) arithmetic counterfactual — the same payoffs, same COUNT,
      relabelled to the rarity the odds favour most;
    * the P5(a) / P5(b) band-hit verdicts against the ruled aim (R185).
  No sim, no run, no stamp: it reads authored content exactly as the canonical
  census read canonical content.

  LEG 2, SIM — realized on-plan payoff cards per finished deck, per arm, at the
  ratified cell. Reported against the aimed band's bracket, and it is NOT part
  of the P5 pass/fail (§6.2: every possible drafter lands inside that bracket).
  It is what grades Q-A: realized reach against the blind-draft offer floor.
  It also carries `T3`'s membership audit — see below.

ABOVE THE CANONICAL SCALE, THIS READER REPORTS AND NEVER TRIPS (§6.1, amended
at `M28` / R196). `TOP` is the observed maximum of nine canonical archetypes
drawn from five base-game pools, not a boundary of the possible, and the
authored sheets read above it on both axes. So a supply above the canonical
ceiling of 3, an offer above TOP's 0.0214, and a realized reach above that
same ceiling are each printed at their RAW VALUE plus their MULTIPLE of the
canonical figure, to one decimal. No categorical band is created above TOP on
either axis. `REACH_CEILING` is a reporting DIVISOR here and nothing else.

`T3` IS CLASSIFIER INTEGRITY AND CONTAINS NO REACH QUANTITY (§6.5, same
amendment). Every deck card reconstructs to a reward-pool base id under
`base_id`'s normalization — the upgrade suffix §6.5 names, and since `EB-124`
the run-applied enchantment mark as well; each such id's on-plan payoff
membership is compared between the deck-side and the static reading, both
through `draft.is_on_plan_payoff`; `T3` fires iff any id's membership differs.
The two sets that do not reconstruct — anchor-shield cards and external-source
on-plan payoffs — are excluded from the comparison and reported on their own
lines.

The registered run is 600/arm at seed 11, hunter, assigned, realistic — the
canonical cell (§6.5). Control C1 is the two `real_*` anchors and runs in the
PRIMARY CHECKOUT ONLY (`game_ref/` is gitignored and a worktree has none);
control C2 is `--policy blind`, `draft.blind_policy`.

Usage:
  python -m tier05.exp_payoff_reach --leg static
  python -m tier05.exp_payoff_reach --leg sim  [--runs N] [--seed N]
                                              [--route NAME] [--jobs N]
                                              [--policy assigned|blind]
  python -m tier05.exp_payoff_reach --controls    # ... and both controls

`--controls` appends the two registered controls to the report: C1, the two
canonical anchor arms at the same cell, and C2, the same nine arms under
`blind`. They print AFTER the tripwire report and their own tripwire state is
labelled a diagnostic, because §6.5's stop condition is defined over the nine
roster arms and a control must never be able to look like part of it.
"""

from __future__ import annotations

import statistics
import sys

from tier0 import constants as C
from tier0.content import enchantments, loader, upgrades
from tier05 import cells, draft, expcli, rewards

# The nine arms of §6.5, in roster ship order. One per ruled aim, no more and
# no fewer.
ARMS: tuple[tuple[str, str], ...] = (
    ("klee", "demolition"), ("klee", "reaction"), ("klee", "spark"),
    ("furina", "salon"), ("furina", "spotlight"), ("furina", "fanfare"),
    ("kokomi", "priest"), ("kokomi", "commander"), ("kokomi", "assist"),
)

# CONTROL C1 (§6.5, PROPOSED AUTHORISED) — the canonical-pool anchor arms.
#
# §6.5 names them `(real_ironclad, starter)` and `(real_silent, starter)`.
# `starter` is a TIER-0 DECK PACKAGE name — it is how STATE names the scoring
# anchor, `("ref_ironclad", "starter")` under the `generic` pilot — and tier
# 0.5 has no such archetype: `runner.resolve_plan("real_ironclad", "starter")`
# raises, because the extracted anchor sheets tag every card `generic` and
# `generic` is the only plan either anchor has. So the registered pair's only
# constructible tier-0.5 form is the one below. Recorded rather than silently
# translated: it is a naming reconciliation between two layers, and it changes
# neither the pool being drafted nor the cell being run.
#
# WHAT THIS CONTROL CAN AND CANNOT JOIN. On the SIM axis it is the join §6.5
# claims: realized reach out of the ACTUAL Ironclad and Silent pools the
# census measured, under the same drafter, the same cell and the same reader.
# On the STATIC axis it is NOT like-for-like with the bands, and the reason is
# in the census's own rubric: the bands were derived over IDENTITY archetypes
# and rubric R3(b) EXCLUDES generic layers, while the tier-0.5 anchor sheets
# carry `generic` and nothing else. So a static read here counts every
# payoff-role card in the pool, not one identity archetype's payoffs, and it
# is printed as a denominator for the reach column rather than as a band read.
C1_ARMS: tuple[tuple[str, str], ...] = (
    ("real_ironclad", "generic"), ("real_silent", "generic"),
)

# The aims, RULED 2026-08-12 (R185). Quoted, never re-derived here.
AIMS: dict[tuple[str, str], str] = {
    ("klee", "demolition"): "MEDIUM",
    ("klee", "reaction"): "HIGH",
    ("klee", "spark"): "LOW",
    ("furina", "salon"): "MEDIUM",
    ("furina", "spotlight"): "HIGH",
    ("furina", "fanfare"): "LOW",
    ("kokomi", "priest"): "MEDIUM",
    ("kokomi", "commander"): "HIGH",
    ("kokomi", "assist"): "LOW",
}

# §6.1's candidate bands: (blind-draft offer, supply ceiling). Order statistics
# over the nine canonical archetypes under the ruled LOOSE rule.
BANDS: dict[str, tuple[float, int]] = {
    "LOW": (0.0019, 1),
    "MEDIUM": (0.0058, 1),
    "HIGH": (0.0097, 2),
    "TOP": (0.0214, 3),
}

# §6.5 P5(b): the half-open offer interval a band NAME means. Read off the
# neighbouring band figures above; TOP's offer closes the top interval.
OFFER_INTERVALS: dict[str, tuple[float, float]] = {
    "LOW": (0.0, BANDS["MEDIUM"][0]),
    "MEDIUM": (BANDS["MEDIUM"][0], BANDS["HIGH"][0]),
    "HIGH": (BANDS["HIGH"][0], BANDS["TOP"][0]),
}

# §6.5 P5(a): supply tolerance, one card either way.
SUPPLY_TOLERANCE = 1

# §6.5 tripwire T2.
DECK_SIZE_WINDOW = (12, 30)

# §6.5 tripwire T1 — the registration's own world-stamp string, quoted.
#
# RE-STAMPED AT THE `P12` FREEZE (§6.6, 2026-08-24): `RT10 / D14 / P7 / C9` ->
# `RT12 / D14 / P7 / C11`. That is the act §6.6's approved ordering (ii)
# reserved — settle first, re-stamp §6 to the world the batch left behind,
# THEN freeze — and it moved no version integer: the world moved first, by
# `RT` 10->11->12 and `C` 9->10->11, each an authorized bump fingerprinted
# against this fence when it landed. `D14`, the registration's actual pin, is
# inside the string unchanged and was never re-pinned.
#
# Left stale the tripwire fired on every arm of every run, because the string
# named a superseded world — a stale citation, not a finding, and a tripwire
# that fires unconditionally carries no information. A literal rather than a
# read of `cells`: `T1`'s whole job is to catch the live world DIVERGING from
# the registered one, and a condition that recomputed both sides from the same
# live source could never fire.
REGISTERED_STAMP = "RT12 / D14 / P7 / C11"

# The canonical supply ceiling. Since `M28` (R196) this is a REPORTING DIVISOR
# and nothing else: §6.5's amended `T3` contains no reach quantity at all, and
# realized reach above this figure is reported at its raw value and its
# multiple of it (§6.1), never tripped. It is deliberately still read from
# `BANDS["TOP"]` so the divisor and the band cannot drift apart.
REACH_CEILING = BANDS["TOP"][1]

# §6.1's other canonical figure: TOP's offer. Same role — a divisor for the
# above-scale report, never a threshold.
OFFER_CEILING = BANDS["TOP"][0]

# The rarity `RARITY_ODDS` favours most -- the 0.60 slot, the left end of the
# 12x spread §6.3's Q-B reasoning names. Read live, never hard-coded.
FAVOURED_RARITY = max(C.RARITY_ODDS, key=lambda r: C.RARITY_ODDS[r])

DRAFTABLE = tuple(sorted(C.RARITY_ODDS, key=lambda r: -C.RARITY_ODDS[r]))

BASE = cells.CANONICAL.but(name="payoff-reach")


# ---------------------------------------------------------------------------
#  Leg 1 -- the static leg
# ---------------------------------------------------------------------------

def _offer(payoffs_at: dict[str, int], sizes: dict[str, int]) -> float:
    """`sum_r ODDS[r] * payoffs_at_r / pool_size_at_r` -- census R7, verbatim.

    The census's own `tools/payoff_census.offer_reach` computes this over a
    canonical pool; this is the same arithmetic over an authored sheet, which
    is the whole point of the static leg being comparable to the bands.
    """
    return sum(C.RARITY_ODDS[r] * payoffs_at.get(r, 0) / sizes[r]
               for r in DRAFTABLE if sizes.get(r))


def static_leg(character: str, archetype: str,
               pool: dict[str, list] | None = None) -> dict:
    """Supply, offer and the Q-B counterfactual for one archetype's sheet.

    `pool` is `rarity -> [Card]`, defaulting to the character's real reward
    pool. It is injectable so a test can pin the arithmetic on a fixture
    instead of on live content that a sheet edit would move.

    THE COUNTERFACTUAL (Q-B, reading B-ii). "The same payoff cards sit at the
    rarity the odds favour most, holding the payoff COUNT fixed." Implemented
    as a RELABEL of those cards: they leave their own rarity's pool and join
    the favoured one, so both the payoff counts and the pool sizes move
    together. That is the only internally consistent reading -- a card cannot
    be common for the odds term and uncommon for the pool-size term. The delta
    it prints is the size of the prize in-rarity composition offers; it is
    arithmetic over the odds table and not a behavioural result, exactly as
    §6.3 states.
    """
    if pool is None:
        pool = rewards.character_pool(character)
    sizes = {r: len(pool.get(r, ())) for r in DRAFTABLE}
    payoffs_at = {
        r: sum(1 for c in pool.get(r, ())
               if draft.is_on_plan_payoff(c, archetype))
        for r in DRAFTABLE}
    supply = sum(payoffs_at.values())

    moved = {r: payoffs_at.get(r, 0) for r in DRAFTABLE if r != FAVOURED_RARITY}
    cf_sizes = {r: sizes[r] - moved.get(r, 0) for r in DRAFTABLE}
    cf_sizes[FAVOURED_RARITY] += sum(moved.values())
    cf_payoffs = {r: 0 for r in DRAFTABLE}
    cf_payoffs[FAVOURED_RARITY] = supply

    offer = _offer(payoffs_at, sizes)
    cf_offer = _offer(cf_payoffs, cf_sizes)
    return {
        "character": character, "archetype": archetype,
        "sizes": sizes, "payoffs_at": payoffs_at,
        "supply": supply, "offer": offer,
        "cf_offer": cf_offer, "cf_delta": cf_offer - offer,
    }


def grade_supply(supply: int, band: str) -> bool:
    """P5(a): supply within the band's ceiling +/- 1 card."""
    ceiling = BANDS[band][1]
    return abs(supply - ceiling) <= SUPPLY_TOLERANCE


def grade_offer(offer: float, band: str) -> bool:
    """P5(b): offer inside the band's half-open interval."""
    lo, hi = OFFER_INTERVALS[band]
    return lo <= offer < hi or (band == "HIGH" and offer == hi)


def above_scale(value: float, canonical: float) -> str:
    """§6.1's reporting rule for a figure above the canonical scale.

    "An archetype whose offer exceeds TOP's 0.0214, or whose supply exceeds
    the canonical ceiling of 3, is reported at its raw value and its multiple
    of the canonical figure, per arm, with the multiple printed to one decimal
    place." The raw value is printed by the caller in its own column; this
    returns the multiple, or the empty string when the figure is inside the
    canonical scale and there is nothing to report.

    No band, no bucket, no label: a bucketed scale invented after the readings
    exist would be a design band authored against seen data, and the ratio
    carries the whole finding while inventing nothing.
    """
    if not canonical or value <= canonical:
        return ""
    return f"{value / canonical:.1f}x"


def band_of(offer: float) -> str:
    """Which band an offer figure actually lands in -- reported beside the
    aim so a miss says WHERE it went, not only that it went.

    ABOVE THE CANONICAL SCALE THERE IS NO BAND (§6.1, amended at `M28`/R196).
    The four bands are order statistics over nine canonical archetypes and
    `TOP` is that sample's observed maximum, not a boundary of the possible;
    inventing a fifth label for what sits above it would be a design band
    authored against seen data. So an offer above `TOP` is labelled by its
    MULTIPLE of `TOP` -- `2.9x TOP`, to one decimal -- which is a
    measurement, not a category. `TOP` itself is still a band and still
    named.
    """
    for name, (lo, hi) in OFFER_INTERVALS.items():
        if lo <= offer < hi:
            return name
    if offer > OFFER_CEILING:
        return f"{offer / OFFER_CEILING:.1f}x TOP"
    return "TOP"


# ---------------------------------------------------------------------------
#  Leg 2 -- the sim leg
# ---------------------------------------------------------------------------

def deck_reach(deck: list, archetype: str) -> tuple[int, int]:
    """(on-plan enabler+payoff, on-plan payoff) for one finished deck.

    A one-line pass-through to `draft._generic_core_counts` ON PURPOSE: the
    reader must count what the drafter's own payoff limb counts, and a second
    implementation here is exactly the drift `_generic_core_counts` was
    consolidated to prevent.
    """
    return draft._generic_core_counts(deck, archetype)


def base_id(card_id: str) -> str:
    """The printed card an id reconstructs to. Stated as its own function
    because `T3` is phrased over base ids and a reader must be able to see
    the whole of what "normalized" means.

    A tier-0.5 deck-list id carries TWO independent decorations, and both
    come off here:

      * the upgrade suffix, `<id>+` (`upgrades.SUFFIX`, R20's one upgrade
        convention) -- §6.5's "explicit upgrade normalization";
      * the run-applied enchantment mark, `<id>@<name>[-<amount>]`
        (`tier0.content.enchantments`, R82 reopened), which an EVENT attaches
        to a card already sitting in the run deck.

    THE SECOND ONE IS `EB-124`, FIXED 2026-08-24 AND FOR FUTURE RUNS ONLY.
    Normalizing the upgrade suffix alone is what §6.5 prescribed, but an
    enchanted REWARD-POOL card then failed to reconstruct and fell into
    `membership_audit`'s `external` set -- which is printed under the label
    "on-plan payoffs that entered the deck from outside the reward pool",
    something an enchanted pool card is not. At the graded 2026-08-24 read
    all 122 ids on those lines carried an `@` and genuinely external on-plan
    payoffs numbered ZERO in every arm, so the line reported a hole of ~14
    ids per arm when the hole its stated cause could explain was empty.
    THE GRADE ITSELF DOES NOT MOVE, and that was verified before this fix
    rather than assumed: an enchantment moves neither `role` nor
    `archetypes`, which are the whole of `draft.is_on_plan_payoff`, so
    returning the 122 to the compared set yields zero membership
    disagreements and `T3` fires under neither normalization. The published
    record stands as published (`R101b`) and nothing in the results artifact
    or the registration is edited on the strength of this.

    The order is split-then-strip, never the reverse: the mark sits INSIDE
    the upgrade suffix by design (`x@sharp-2+`), and `enchantments.split` is
    the engine's own door past it -- the same function
    `loader._card_prototype` uses -- so the reader reconstructs an id exactly
    the way the loader does instead of growing a second opinion about id
    shape. An unregistered enchantment name still raises out of `split`: a
    deck-list id nothing can build is a defect, and a reader that quietly
    normalized it to something would hide it.
    """
    plain, _, _ = enchantments.split(card_id)
    return (plain[:-len(upgrades.SUFFIX)]
            if plain.endswith(upgrades.SUFFIX) else plain)


def _is_anchor_shielded(card) -> bool:
    """Is this a card the anchor tag shield strips `archetypes` from?

    §6.5 names this set `draft._anchor_tag_shield`. There is no function by
    that name: the shield is R121's `draft.ANCHOR_TAG_SHIELD_CHARACTER`
    applied in `draft.behavioural_archetypes` and `draft._core_advance_view`,
    and the predicate it applies is the one written out here. The registration
    names the SET correctly and the symbol loosely; the set is what `T3`
    excludes, so the set is what this reads. Read off `draft`, never
    re-hard-coded, so a change to the shield reaches this exclusion.
    """
    return (card.character == draft.ANCHOR_TAG_SHIELD_CHARACTER
            and bool(card.archetypes))


def membership_audit(decks: list[list], character: str, archetype: str,
                     pool: dict[str, list] | None = None) -> dict:
    """§6.5's `T3`, as amended at `M28` (R196). NO reach quantity enters it.

    For every card in every finished deck of one arm, reconstruct a
    reward-pool base id under `base_id` above, then compare that id's on-plan
    payoff membership as classified on the DECK side against its membership in
    the arm's STATIC pool. `T3` fires iff any base id's membership differs.

    Both sides call `draft.is_on_plan_payoff` -- the one registered predicate
    -- so a disagreement cannot be a threshold judgement, a sampling artefact
    or a design finding. It can only mean the two legs are counting different
    objects under one predicate, which is the drift the shared predicate
    exists to prevent. The deck side reads the card as the deck holds it
    (upgraded form included) and the static side reads the printed pool row;
    that is the whole content of "after upgrade normalization", and it is why
    an upgrade that quietly moved `role` or `archetypes` would show up here.

    Two sets of cards do NOT reconstruct and are therefore NOT `T3` inputs.
    They are counted and returned so the printer can put them on their own
    lines, because silently dropping them is how an integrity check learns to
    pass:

      * `anchor_shield` -- cards the R121 anchor tag shield strips
        `archetypes` from, by design. Their deck-side membership is a
        deliberate blindness, not a drift.
      * `external` -- ON-PLAN PAYOFFS that entered the deck from outside the
        reward pool: event grants, tokens, guest stars, starters. They have
        no static row to be compared against. Non-payoff cards from outside
        the pool are simply not inputs and are not reported: they carry no
        membership claim for the two legs to disagree about.
    """
    if pool is None:
        pool = rewards.character_pool(character)
    static_by_id = {c.id: c for cards in pool.values() for c in cards}

    disagree: dict[str, tuple[bool, bool]] = {}
    anchor_shield: set[str] = set()
    external: set[str] = set()
    compared: set[str] = set()
    for deck in decks:
        for card in deck:
            if _is_anchor_shielded(card):
                anchor_shield.add(base_id(card.id))
                continue
            bid = base_id(card.id)
            row = static_by_id.get(bid)
            if row is None:
                if draft.is_on_plan_payoff(card, archetype):
                    external.add(bid)
                continue
            compared.add(bid)
            deck_member = draft.is_on_plan_payoff(card, archetype)
            static_member = draft.is_on_plan_payoff(row, archetype)
            if deck_member != static_member:
                disagree[bid] = (deck_member, static_member)
    return {
        "compared": sorted(compared),
        "disagree": dict(sorted(disagree.items())),
        "anchor_shield": sorted(anchor_shield),
        "external": sorted(external),
    }


def sim_leg(cell) -> dict:
    """Realized reach for one arm at one cell. Runs the cell."""
    a = cell.arm()
    decks = [[loader.peek_card(cid) for cid in ids] for ids in a["decks"]]
    counts = [deck_reach(d, cell.archetype) for d in decks]
    reach = [p for _, p in counts]
    return {
        "n": len(decks),
        "decksize": a["decksize"],
        "win": a["win"],
        "on_plan": statistics.mean(o for o, _ in counts),
        "reach": statistics.mean(reach),
        "reach_sd": statistics.pstdev(reach) if len(reach) > 1 else 0.0,
        "held_none": sum(1 for p in reach if p == 0) / len(reach),
        "max_reach": max(reach),
        "audit": membership_audit(decks, cell.character, cell.archetype),
    }


def tripwires(cell, static: dict, sim: dict | None) -> list[str]:
    """T1-T4 of §6.5. A fired tripwire STOPS the sprint and re-registers; it
    is never a footnote, so it is returned rather than printed inline."""
    fired = []
    v = cell.versions
    arm = f"{static['character']}/{static['archetype']}"
    stamp = f"RT{v['RT']} / D{v['D']} / P{v['P']} / C{v['C']}"
    if stamp != REGISTERED_STAMP:
        fired.append(f"T1: world stamp is {stamp}, registered against "
                     f"{REGISTERED_STAMP}")
    if static["supply"] == 0:
        fired.append(f"T4: {arm} has "
                     "zero draftable payoff cards — this is a content "
                     "question for [USER], not a grade")
    if sim is not None:
        lo, hi = DECK_SIZE_WINDOW
        # T2 and T3 are per-ARM, and §6.5 phrases both as "any arm's ...", so
        # the arm is named in the message exactly as T4 above names it. It is
        # not decoration: without it two arms with the same number emit
        # byte-identical strings and collapse under the de-duplication below,
        # and a reader cannot tell how many arms fired, nor which.
        if not lo <= sim["decksize"] <= hi:
            fired.append(f"T2: {arm} mean deck size {sim['decksize']:.1f} is "
                         f"outside {lo}-{hi}; the band floors would be "
                         "extrapolated, not read")
        # T3, as AMENDED at `M28` (R196). No reach quantity enters it: reach
        # above the canonical ceiling is what the authored sheets print, so it
        # is REPORTED with its multiple (§6.1) and never tripped. What fires
        # here is classifier integrity — a reward-pool base id whose on-plan
        # payoff membership differs between the deck-side and the static
        # reading, after upgrade normalization and after the two excluded sets
        # are taken out. That cannot be produced by ordinary data.
        #
        # The premise the amendment replaced, kept as a warning: the tripwire
        # used to fire on realized reach above 3. It halted the sprint on
        # ordinary content, first on the per-deck maximum (a defect, fixed
        # 2026-08-13) and then on the arm mean (the premise itself, which the
        # static leg's own supplies of 3–14 contradict).
        for bid, (deck_member, static_member) in sim["audit"]["disagree"].items():
            fired.append(
                f"T3: {arm} base id {bid!r} classifies as "
                f"{'on-plan payoff' if deck_member else 'not a payoff'} on the "
                f"deck side and "
                f"{'on-plan payoff' if static_member else 'not a payoff'} in "
                "the static pool — the two legs are counting different "
                "objects under one predicate, an instrument fault, not a "
                "finding")
    return fired


def dedupe_fired(fired: list[str]) -> list[str]:
    """Collapse the arm-INDEPENDENT tripwire, and only that one.

    T1 reads the same live stamp for every arm, so it fires nine times or
    none: a stop is a stop, and repeating it nine times would bury the
    arm-specific ones under it. It is collapsed to its first occurrence.

    T2/T3/T4 are per-arm and are NOT collapsed. De-duplicating them by message
    text — which is what this did to the whole list — hid arms: their messages
    carried a number and no arm name, so two arms at the same figure emitted
    byte-identical strings and printed as one line. At the registered seed
    seven arms over the ceiling reported as four. All three now name their arm
    (T4 always did), so nothing collides by text either; keeping the narrowing
    is what makes the count honest if a future message ever drops the name.
    """
    return ([f for f in dict.fromkeys(fired) if f.startswith("T1")]
            + [f for f in fired if not f.startswith("T1")])


# ---------------------------------------------------------------------------
#  Printer
# ---------------------------------------------------------------------------

def _print_static(rows: dict[tuple[str, str], dict]) -> None:
    print(f"\n  LEG 1 — STATIC (sheets only; no run, no stamp)")
    print(f"  {'arm':>20} {'aim':>7} {'supply':>7} {'x sup':>9} {'P5a':>5} "
          f"{'offer':>9} {'lands':>9} {'P5b':>5} "
          f"{'cf offer':>9} {'cf delta':>9}")
    for arm in ARMS:
        s = rows[arm]
        band = AIMS[arm]
        a_ok = "PASS" if grade_supply(s["supply"], band) else "FAIL"
        b_ok = "PASS" if grade_offer(s["offer"], band) else "FAIL"
        print(f"  {'/'.join(arm):>20} {band:>7} {s['supply']:>7d} "
              f"{above_scale(s['supply'], REACH_CEILING):>9} {a_ok:>5} "
              f"{s['offer']:>9.4f} {band_of(s['offer']):>9} {b_ok:>5} "
              f"{s['cf_offer']:>9.4f} {s['cf_delta']:>+9.4f}")
    print("\n  P5(a) supply within the band ceiling +/- 1 card; P5(b) offer in "
          "the band's\n  half-open interval. Missing BOTH is the redesign "
          "trigger (§6.5); missing one\n  is reported, not triggered. cf = the "
          "Q-B (B-ii) counterfactual: same payoff\n  COUNT, relabelled to "
          f"{FAVOURED_RARITY}.")
    print(f"\n  ABOVE THE CANONICAL SCALE (§6.1). Each axis is reported at its "
          f"RAW value plus its\n  MULTIPLE of the canonical figure, to one "
          f"decimal: `x sup` against the supply\n  ceiling of {REACH_CEILING}, "
          f"and `lands` against TOP's offer of {OFFER_CEILING} once the\n  "
          "figure leaves the banded range. TOP is the observed maximum of nine "
          "canonical\n  archetypes, not a boundary of the possible, and NO "
          "categorical band is created\n  above it on either axis — a bucket "
          "invented after the readings exist would be a\n  design band "
          "authored against seen data.")


def _print_sim(rows: dict[tuple[str, str], dict],
               static: dict[tuple[str, str], dict]) -> None:
    print(f"\n  LEG 2 — SIM (realized on-plan reach; reported, not P5-graded)")
    print(f"  {'arm':>20} {'aim':>7} {'deck':>6} {'on-plan':>8} "
          f"{'reach':>7} {'x ceil':>7} {'floor':>7} {'x floor':>8} "
          f"{'ceil':>5} {'none':>6} {'win':>7}")
    for arm in ARMS:
        if arm not in rows:
            continue
        r, s, band = rows[arm], static[arm], AIMS[arm]
        floor = BANDS[band][0] * r["decksize"]
        mult = r["reach"] / floor if floor else float("inf")
        print(f"  {'/'.join(arm):>20} {band:>7} {r['decksize']:>6.1f} "
              f"{r['on_plan']:>8.2f} {r['reach']:>7.2f} "
              f"{above_scale(r['reach'], REACH_CEILING):>7} "
              f"{floor:>7.3f} {mult:>8.1f} {BANDS[band][1]:>5d} "
              f"{r['held_none']:>6.1%} {r['win']:>6.1%}")
    print("\n  floor = the aimed band's blind-draft offer x the observed deck "
          "size; the\n  bracket's right edge is the band's supply ceiling. "
          "Q-A's registered\n  prediction: reach > floor in all nine arms, "
          ">= 3x floor everywhere, and\n  >= 1.0 in the three HIGH arms. "
          "Grading is blind-first and lives in the\n  registration, not here.")
    print(f"  x ceil = realized reach as a MULTIPLE of the canonical supply "
          f"ceiling ({REACH_CEILING}),\n  §6.1's reporting rule, printed only "
          "where reach exceeds it. Since `M28` (R196)\n  reach above that "
          "ceiling is REPORTED and never tripped: it is what the authored\n"
          "  sheets print, not evidence of miscounting.")
    _print_exclusions(rows)


def _print_exclusions(rows: dict[tuple[str, str], dict]) -> None:
    """`T3`'s two excluded sets, on their own lines, as §6.5 requires.

    They are printed whether or not `T3` fires. An integrity condition that
    hides what it declined to look at is not one: these two lines are how a
    reader sees the size of the hole in the comparison, and a swelling
    `external` line is itself information even though it can never fire `T3`.
    """
    print("\n  T3 EXCLUSIONS — cards that do not reconstruct to a reward-pool "
          "base id and\n  are therefore not T3 inputs (§6.5). Reported, never "
          "tripped.")
    for arm in ARMS:
        if arm not in rows:
            continue
        a = rows[arm]["audit"]
        print(f"  {'/'.join(arm):>20}  compared {len(a['compared']):>3} ids · "
              f"anchor-shield {len(a['anchor_shield']):>2}"
              f"{' ' + ', '.join(a['anchor_shield']) if a['anchor_shield'] else ''}")
        print(f"  {'':>20}  external-source on-plan payoffs "
              f"{len(a['external']):>2}"
              f"{' ' + ', '.join(a['external']) if a['external'] else ''}")
    print("  anchor-shield = R121 strips `archetypes` from these by design. "
          "external-source =\n  on-plan payoffs that entered from outside the "
          "reward pool (event grants, tokens,\n  guest stars, starters), which "
          "have no static row to be compared against.")


def _print_c1(rows: dict[tuple[str, str], dict],
              static: dict[tuple[str, str], dict]) -> None:
    """CONTROL C1 — the two canonical-pool anchor arms, at the same cell.

    NO BAND COLUMN AND NO P5 VERDICT, deliberately. The census excluded
    generic layers (rubric R3(b)) and these sheets carry only `generic`, so
    grading them against the bands would be comparing a whole-pool payoff
    count with an identity archetype's. What the control is FOR is the reach
    column: the same drafter, the same cell and the same reader, run over the
    pools the bands were derived from.
    """
    print("\n  CONTROL C1 — canonical-pool anchors (§6.5; primary checkout "
          "only, `game_ref/`)")
    print(f"  {'arm':>22} {'pool':>6} {'payoffs':>8} {'offer':>9} "
          f"{'deck':>6} {'reach':>7} {'x ceil':>7} {'none':>6} {'win':>7}")
    for arm in C1_ARMS:
        if arm not in rows:
            continue
        r, s = rows[arm], static[arm]
        print(f"  {'/'.join(arm):>22} {sum(s['sizes'].values()):>6d} "
              f"{s['supply']:>8d} {s['offer']:>9.4f} "
              f"{r['decksize']:>6.1f} {r['reach']:>7.2f} "
              f"{above_scale(r['reach'], REACH_CEILING):>7} "
              f"{r['held_none']:>6.1%} {r['win']:>6.1%}")
    print("  `payoffs` is every payoff-role card in the pool under the ONE "
          "registered\n  predicate — the anchor sheets carry a single "
          "`generic` archetype, so there is no\n  identity layer to narrow it "
          "to, and the census's own bands excluded exactly\n  that layer. "
          "Reported as the reach column's denominator, never as a band read.")


def _print_c2(blind: dict[tuple[str, str], dict],
              assigned: dict[tuple[str, str], dict]) -> None:
    """CONTROL C2 — the blind-pick negative control (§6.5).

    "A policy that takes uniformly at random from each offer screen, giving
    the offer floor EMPIRICALLY rather than by arithmetic." So the column that
    matters is `blind reach` beside the band's arithmetic floor: it says
    whether the floor Q-A is graded against is the floor a blind draft
    actually produces in this world.

    REPORTED, NOT GRADED. Q-A's registered threshold is stated against the
    ARITHMETIC floor (§6.3), and §6.5 registered C2 with declining it as a
    live option precisely because the grade does not depend on it. Re-grading
    Q-A against this column would be swapping the registered comparator after
    the readings exist.
    """
    print("\n  CONTROL C2 — blind-pick negative control (`--policy blind`), "
          "same arms and cell")
    print(f"  {'arm':>20} {'aim':>7} {'deck':>6} {'blind':>7} "
          f"{'arith floor':>11} {'blind/arith':>11} {'assigned':>9} "
          f"{'asg/blind':>9} {'none':>6}")
    for arm in ARMS:
        if arm not in blind:
            continue
        b, band = blind[arm], AIMS[arm]
        floor = BANDS[band][0] * b["decksize"]
        a = assigned.get(arm)
        print(f"  {'/'.join(arm):>20} {band:>7} {b['decksize']:>6.1f} "
              f"{b['reach']:>7.2f} {floor:>11.3f} "
              f"{(b['reach'] / floor if floor else float('inf')):>11.1f} "
              f"{(a['reach'] if a else float('nan')):>9.2f} "
              f"{(a['reach'] / b['reach'] if a and b['reach'] else float('inf')):>9.2f} "
              f"{b['held_none']:>6.1%}")
    print("  `arith floor` = the aimed band's blind-draft offer x the observed "
          "deck size —\n  the comparator Q-A is REGISTERED against. `blind` is "
          "the same quantity measured\n  instead of computed. Both are printed "
          "because the whole point of the control is\n  the gap between them; "
          "neither this table nor that gap re-grades Q-A.")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    leg = "both"
    if "--leg" in args:
        i = args.index("--leg")
        if i + 1 >= len(args):
            raise SystemExit("--leg needs a value (static | sim | both)")
        leg = args[i + 1]
        del args[i:i + 2]
    if leg not in ("static", "sim", "both"):
        raise SystemExit(f"unknown leg {leg!r} (static | sim | both)")
    controls = "--controls" in args
    if controls:
        args.remove("--controls")
    policy = BASE.policy
    if "--policy" in args:
        i = args.index("--policy")
        if i + 1 >= len(args):
            raise SystemExit("--policy needs a value")
        policy = args[i + 1]
        del args[i:i + 2]
    base, rest = cells.parse_overrides(args, BASE.but(policy=policy))
    if rest:
        raise SystemExit(f"unknown arguments: {' '.join(rest)}")

    cells.print_header(base, "PAYOFF REACH — NINE ROSTER ARMS",
                       f"{len(ARMS)} arms, aims ruled R185, "
                       f"predictions committed R186")
    print("  Reader only: no drafter scoring is touched and the "
          "DRAFTER_VERSION = 14 pin\n  is untouched. Blind-first grading "
          "happens in the registration, never here.")

    statics = {arm: static_leg(*arm) for arm in ARMS}
    if leg in ("static", "both"):
        _print_static(statics)

    sims: dict[tuple[str, str], dict] = {}
    if leg in ("sim", "both"):
        for character, archetype in ARMS:
            cell = base.but(character=character, archetype=archetype)
            sims[(character, archetype)] = sim_leg(cell)
        _print_sim(sims, statics)

    fired: list[str] = []
    for arm in ARMS:
        cell = base.but(character=arm[0], archetype=arm[1])
        fired += tripwires(cell, statics[arm], sims.get(arm))
    fired = dedupe_fired(fired)
    if fired:
        print(f"\n  TRIPWIRES FIRED ({len(fired)}) — the sprint STOPS and "
              "re-registers:")
        for f in fired:
            print(f"    {f}")
    else:
        print("\n  tripwires T1–T4: none fired.")

    if not controls:
        return 0

    # The two registered controls. They run AFTER the tripwire report on
    # purpose: the tripwire table of §6.5 is defined over the nine roster
    # arms, and a control's rows must never be able to look like part of the
    # stop condition. Their own tripwire state is reported separately below,
    # explicitly as a diagnostic.
    c1_static = {arm: static_leg(*arm) for arm in C1_ARMS}
    c1_sims: dict[tuple[str, str], dict] = {}
    if leg in ("sim", "both"):
        for arm in C1_ARMS:
            pool_size = sum(c1_static[arm]["sizes"].values())
            if not pool_size:
                # `game_ref/` is gitignored and a worktree has none (§6.7). An
                # empty pool here is that absence, and reporting a reach
                # number off it would be reporting a control that did not run.
                print(f"\n  CONTROL C1 {'/'.join(arm)}: SKIPPED — the "
                      "canonical pool is empty in this checkout. §6.7: "
                      "`game_ref/`\n  is gitignored, a worktree has none and "
                      "must never be given one, so C1 runs in\n  the PRIMARY "
                      "CHECKOUT only. This is the absence, stated, not a "
                      "reading of zero.")
                continue
            try:
                c1_sims[arm] = sim_leg(base.but(character=arm[0],
                                                archetype=arm[1]))
            except Exception as exc:                 # noqa: BLE001
                # A CONTROL cannot destroy a registered read that already
                # completed — §6.5's stop condition is the tripwire table over
                # the nine roster arms, and this is neither. The exception is
                # PRINTED rather than swallowed, and the arm is reported
                # BLOCKED rather than reported at a quietly reduced `n`: the
                # sample plan forbids silently shrinking `n`, and dropping the
                # runs that failed would be exactly that.
                print(f"\n  CONTROL C1 {'/'.join(arm)}: BLOCKED at the "
                      f"registered cell — {type(exc).__name__}: {exc}")
                print("  The arm is NOT reported at a reduced n. An engine "
                      "defect reachable only from a\n  control's own pool is "
                      "a defect to file, not a result to quote, and it is\n  "
                      "neither a tripwire nor a finding about payoff reach.")
    if c1_sims:
        _print_c1(c1_sims, c1_static)

    if leg in ("sim", "both"):
        blind_base = base.but(policy="blind")
        blind = {arm: sim_leg(blind_base.but(character=arm[0],
                                             archetype=arm[1]))
                 for arm in ARMS}
        _print_c2(blind, sims)
        c_fired = dedupe_fired(
            [f"C1 {f}" for arm in c1_sims
             for f in tripwires(base.but(character=arm[0], archetype=arm[1]),
                                c1_static[arm], c1_sims[arm])]
            + [f"C2 {f}" for arm in ARMS
               for f in tripwires(blind_base.but(character=arm[0],
                                                 archetype=arm[1]),
                                  statics[arm], blind[arm])])
        print("\n  CONTROL-ARM TRIPWIRE STATE — DIAGNOSTIC. §6.5's tripwire "
              "table is defined over\n  the nine roster arms; a control "
              "cannot stop the sprint. Printed because a\n  control that "
              "quietly tripped its own integrity check would make its rows "
              "worth\n  less, and hiding that is how a control becomes "
              "decoration.")
        for f in (c_fired or ["    (none)"]):
            print(f"    {f}" if f.strip() != "(none)" else f)
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
