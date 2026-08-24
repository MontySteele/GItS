"""Payoff reach, all nine roster archetypes — the registered sprint's reader.

The instrument of `review/active/payoff-reach-reregistration.md` §6.4, built
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

The registered run is 600/arm at seed 11, hunter, assigned, realistic — the
canonical cell (§6.5). Control C1 is the two `real_*` anchors and runs in the
PRIMARY CHECKOUT ONLY (`game_ref/` is gitignored and a worktree has none);
control C2 is `--policy blind`, `draft.blind_policy`.

Usage:
  python -m tier05.exp_payoff_reach --leg static
  python -m tier05.exp_payoff_reach --leg sim  [--runs N] [--seed N]
                                              [--route NAME] [--jobs N]
                                              [--policy assigned|blind]
"""

from __future__ import annotations

import statistics
import sys

from tier0 import constants as C
from tier0.content import loader
from tier05 import cells, draft, rewards

# The nine arms of §6.5, in roster ship order. One per ruled aim, no more and
# no fewer.
ARMS: tuple[tuple[str, str], ...] = (
    ("klee", "demolition"), ("klee", "reaction"), ("klee", "spark"),
    ("furina", "salon"), ("furina", "spotlight"), ("furina", "fanfare"),
    ("kokomi", "priest"), ("kokomi", "commander"), ("kokomi", "assist"),
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

# §6.5 tripwires T2 / T3.
DECK_SIZE_WINDOW = (12, 30)
REACH_CEILING = BANDS["TOP"][1]

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


def band_of(offer: float) -> str:
    """Which band an offer figure actually lands in -- reported beside the
    aim so a miss says WHERE it went, not only that it went."""
    for name, (lo, hi) in OFFER_INTERVALS.items():
        if lo <= offer < hi:
            return name
    return "TOP+" if offer > BANDS["TOP"][0] else "TOP"


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
    }


def tripwires(cell, static: dict, sim: dict | None) -> list[str]:
    """T1-T4 of §6.5. A fired tripwire STOPS the sprint and re-registers; it
    is never a footnote, so it is returned rather than printed inline."""
    fired = []
    v = cell.versions
    arm = f"{static['character']}/{static['archetype']}"
    stamp = f"RT{v['RT']} / D{v['D']} / P{v['P']} / C{v['C']}"
    if stamp != "RT10 / D14 / P7 / C9":
        fired.append(f"T1: world stamp is {stamp}, registered against "
                     "RT10 / D14 / P7 / C9")
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
        # The registered statistic is the ARM's realized reach -- §6.4 leg 2's
        # per-arm figure, which is the mean at sim["reach"], the same number
        # the printer grades and the same grain T2 reads deck size at. It is
        # NOT the per-run maximum: max_reach is one deck, and one deck is not
        # an arm. Reading the max here halted the sprint on ordinary data
        # (four arms fired at 20 runs/arm with maxima 8/5/7/11 while every
        # arm's mean sat inside the ceiling). A per-deck outlier check may be
        # wanted, but it is a DISTINCT tripwire and goes back through the
        # registration rather than riding under T3's wording.
        if sim["reach"] > REACH_CEILING:
            fired.append(f"T3: {arm} realized reach {sim['reach']:.2f} "
                         f"exceeds the TOP supply ceiling {REACH_CEILING} — "
                         "an instrument fault, not a finding")
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
    print(f"  {'arm':>20} {'aim':>7} {'supply':>7} {'P5a':>5} "
          f"{'offer':>9} {'lands':>7} {'P5b':>5} {'cf offer':>9} "
          f"{'cf delta':>9}")
    for arm in ARMS:
        s = rows[arm]
        band = AIMS[arm]
        a_ok = "PASS" if grade_supply(s["supply"], band) else "FAIL"
        b_ok = "PASS" if grade_offer(s["offer"], band) else "FAIL"
        print(f"  {'/'.join(arm):>20} {band:>7} {s['supply']:>7d} {a_ok:>5} "
              f"{s['offer']:>9.4f} {band_of(s['offer']):>7} {b_ok:>5} "
              f"{s['cf_offer']:>9.4f} {s['cf_delta']:>+9.4f}")
    print("\n  P5(a) supply within the band ceiling +/- 1 card; P5(b) offer in "
          "the band's\n  half-open interval. Missing BOTH is the redesign "
          "trigger (§6.5); missing one\n  is reported, not triggered. cf = the "
          "Q-B (B-ii) counterfactual: same payoff\n  COUNT, relabelled to "
          f"{FAVOURED_RARITY}.")


def _print_sim(rows: dict[tuple[str, str], dict],
               static: dict[tuple[str, str], dict]) -> None:
    print(f"\n  LEG 2 — SIM (realized on-plan reach; reported, not P5-graded)")
    print(f"  {'arm':>20} {'aim':>7} {'deck':>6} {'on-plan':>8} "
          f"{'reach':>7} {'floor':>7} {'x floor':>8} {'ceil':>5} "
          f"{'none':>6} {'win':>7}")
    for arm in ARMS:
        if arm not in rows:
            continue
        r, s, band = rows[arm], static[arm], AIMS[arm]
        floor = BANDS[band][0] * r["decksize"]
        mult = r["reach"] / floor if floor else float("inf")
        print(f"  {'/'.join(arm):>20} {band:>7} {r['decksize']:>6.1f} "
              f"{r['on_plan']:>8.2f} {r['reach']:>7.2f} {floor:>7.3f} "
              f"{mult:>8.1f} {BANDS[band][1]:>5d} "
              f"{r['held_none']:>6.1%} {r['win']:>6.1%}")
    print("\n  floor = the aimed band's blind-draft offer x the observed deck "
          "size; the\n  bracket's right edge is the band's supply ceiling. "
          "Q-A's registered\n  prediction: reach > floor in all nine arms, "
          ">= 3x floor everywhere, and\n  >= 1.0 in the three HIGH arms. "
          "Grading is blind-first and lives in the\n  registration, not here.")


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
