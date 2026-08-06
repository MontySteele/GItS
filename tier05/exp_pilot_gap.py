"""The pilot gap — Furina's greedy pilot against one that runs the wheel.

Registered in docs/archive/sprint-pilot-gap-2026-07-28.md. MEASURE ONLY: no lever, no
card change, no constant change. Every lever this battery informs is [USER]
red-pen and out of scope.

WHY. Playtest 3 beat ascension 0 effortlessly on the first try with a
saturated Encore runway. The sim, on the same build, reports the opposite --
half the upkeeps dry, a low winrate on the salon arm. The arithmetic is not in
question (constant parity, both mirrors reviewed), so the divergence is in the
PILOT. Furina's kit is a flywheel: every Encore point prints Fanfare twice
(once gained, once spent), Fanfare feeds the Focus term on member numbers,
Chevalmarin's bow converts the boosted stage back into Encore, and
center_stage pays 2 per card while she holds the Spotlight. A human banks
Encore, deploys early and keeps the Spotlight. A stage that is dry half the
time is a stage nobody is stoking.

If that is right, every quoted Furina row is a FLOOR and not a ceiling, and
any nerf priced against the current pilot is priced against the wrong Furina.
THE GAP IS THE DELIVERABLE.

PRE-REGISTERED READINGS, recorded in the brief before any run:
  R-A  stoker salon winrate rises >= +25 points over greedy AND dry rate
       falls below ~25% -> the loop is pilot-shaped; nerf pricing moves to
       the stoker arm.
  R-B  winrate moves < +10 points -> the loop is NOT pilot-skill-shaped; the
       co-op seat dynamic becomes the leading hypothesis and a FUTURE brief
       instruments that.
  R-C  anything between -> report both worlds; the ruling decides.

Winrate may saturate, so turns-to-kill and hp-left are registered UP FRONT as
the re-cut metrics rather than reached for after saturation is discovered.

A stoker that comes back WORSE than greedy is a REPORTABLE RESULT, not a
failed sprint -- it would be strong evidence for R-B. The binding Kokomi v0.4
W1 null result (a bank-before-spending rule of this same shape measured worse,
priest act-1 33% -> 27%) is why this sprint measures the stoker instead of
assuming it.

LABELLING. Never quote a stoker row against a greedy row without both labels.
That rule is enforced structurally rather than by discipline: `pilot_override`
lands in `Cell.stamp()`, so any table printed off a non-default pilot names it
in its own mandatory stamp line.

Usage: python -m tier05.exp_pilot_gap [p1|p2|p3|p4|all] [--runs N] [--jobs N]
"""

from __future__ import annotations

import statistics
import sys

from tier0 import constants as C
from tier05 import cells, encore_telemetry, fanfare_telemetry

# The ratified cell, on Furina's salon plan, which is what every arm below
# varies from. Only the PILOT differs between arms -- same seed, same route,
# same policy, same loadout, same assigned draft -- so a difference between
# two rows is a difference in how the cards got played.
BASE = cells.CANONICAL.but(name="pilot-gap", character="furina",
                           archetype="salon")

# (label, pilot id, what it holds fixed). The two ablations exist because
# salon_stoker changes two things at once: "the stoker wins" and "her salon
# pilot was under-weighting the Spotlight all along" are different findings
# with different levers behind them.
ARMS: tuple[tuple[str, str, str], ...] = (
    ("greedy", "salon", "the shipped pilot; every Furina row on record"),
    ("stoker", "salon_stoker", "stoke 1.0 + spotlight 0.4 -> 1.0"),
    ("stoke-only", "salon_stoke_only", "stoke 1.0, spotlight HELD at 0.4"),
    ("spot-only", "salon_spot_only", "no stoke term, spotlight 1.0"),
)

# Track 3's accounting split. Both legs of the double-count, and everything
# that is not one of them.
DOUBLE_COUNT_LEGS = ("encore_gained", "encore_spent")


# ======================================================================
# shared reductions
# ======================================================================

def _fight_cuts(results: list) -> dict:
    """The pre-registered re-cut metrics, taken at FIGHT level.

    Run winrate is the headline and it saturates; these do not. Turns-to-kill
    is computed over WON fights only -- a loss ends when she dies, so folding
    losses in would report "died fast" as "killed fast", and the metric is
    about how quickly the engine closes a fight it is going to close.
    """
    fights = [f for r in results for f in r.fight_stats]
    won = [f for f in fights if f.won]
    return {
        "fights": len(fights),
        "fight_win": len(won) / len(fights) if fights else 0.0,
        "turns_to_kill": statistics.mean(f.turns for f in won) if won else 0.0,
        "hp_left": statistics.mean(f.hp_end for f in won) if won else 0.0,
        "dmg": statistics.mean(f.total_damage_dealt for f in fights)
        if fights else 0.0,
        "cards_played": statistics.mean(f.cards_played for f in fights)
        if fights else 0.0,
    }


def _encore_agg(results: list) -> dict:
    return encore_telemetry.aggregate(
        [tr for r in results for _, tr in r.encore_traces])


def _fanfare_agg(results: list) -> dict:
    return fanfare_telemetry.aggregate(
        [tr for r in results for _, tr in r.fanfare_traces])


def _by_act(results: list, attr: str) -> dict[int, list]:
    out: dict[int, list] = {}
    for res in results:
        for act_i, tr in getattr(res, attr):
            out.setdefault(act_i, []).append(tr)
    return out


def _arms(base: cells.Cell) -> list[tuple[str, str, cells.Cell, dict]]:
    """Every arm, run once. Cached across cells so a full `all` invocation
    does not fly the same four batteries four times."""
    global _CACHE
    if _CACHE is None:
        _CACHE = []
        for label, pilot, note in ARMS:
            cell = base.but(name=f"pilot-gap[{label}]", pilot_override=pilot)
            _CACHE.append((label, note, cell, cell.arm()))
    return _CACHE


_CACHE: list | None = None


# ======================================================================
# P1 -- the gap
# ======================================================================

def p1(base: cells.Cell) -> None:
    print("=" * 78)
    print("P1. THE GAP — the same assigned salon draft, flown four ways")
    print(f"    {base.but(name='pilot-gap').stamp()}")
    print(f"    {base.describe(subject='furina/salon', varying=())}")
    print("    Only the PILOT differs between rows. Same seed, same route, "
          "same policy, same loadout.")
    print("=" * 78)
    print("\n  ROSTER RE-MEASURE: these salon rows are taken AFTER Casting Call "
          "(A12, the cap-raise\n  power) landed, so they retire the owed "
          "post-box_seats salon re-measurement. Any\n  salon number quoted "
          "from before 2026-07-28 predates a cap that is now a per-player "
          "stat.")

    print(f"\n  {'arm':>11} {'win':>7} {'act-1':>7} {'acts':>6} {'deck':>6} "
          f"{'fights/run':>11}   what it changes")
    for label, note, cell, a in _arms(base):
        print(f"  {label:>11} {a['win']:>6.1%} {a['act1']:>6.1%} "
              f"{a['acts']:>6.2f} {a['decksize']:>6.1f} {a['fights']:>11.1f}"
              f"   {note}")

    print("\n  RE-CUTS, registered before the run in case winrate saturates. "
          "turns-to-kill and\n  hp-left are over WON fights only (a loss ends "
          "when she dies; folding those in\n  reports 'died fast' as 'killed "
          "fast').")
    print(f"\n  {'arm':>11} {'fight win':>10} {'turns/kill':>11} "
          f"{'hp left':>8} {'dmg/fight':>10} {'cards/fight':>12}")
    for label, _note, _cell, a in _arms(base):
        cuts = _fight_cuts(a["results"])
        print(f"  {label:>11} {cuts['fight_win']:>9.1%} "
              f"{cuts['turns_to_kill']:>11.2f} {cuts['hp_left']:>8.1f} "
              f"{cuts['dmg']:>10.1f} {cuts['cards_played']:>12.1f}")

    rows = {label: a for label, _n, _c, a in _arms(base)}
    delta = (rows["stoker"]["win"] - rows["greedy"]["win"]) * 100
    dry = _encore_agg(rows["stoker"]["results"]).get("dry_rate", 0.0)
    # ASCII only in these prints: the console this runs on is cp1252, and a
    # U+2212 MINUS SIGN here crashed the first full-scale invocation AFTER
    # the four batteries had already been flown.
    print(f"\n  PRE-REGISTERED READING: stoker - greedy = "
          f"{delta:+.1f} winrate points, stoker dry rate {dry:.1%}.")
    if delta >= 25 and dry < 0.25:
        verdict = ("R-A. The loop is pilot-shaped: the playtest reproduces "
                   "in sim once the pilot\n    runs the wheel, and all nerf "
                   "pricing moves to the stoker arm.")
    elif delta < 10:
        verdict = ("R-B. The loop is NOT pilot-skill-shaped. The co-op seat "
                   "dynamic becomes the\n    leading hypothesis for the "
                   "playtest power level; a FUTURE brief instruments it.")
    else:
        verdict = ("R-C. Between the two. Both worlds are reported below and "
                   "the ruling decides\n    which one prices the lever.")
    print(f"    => {verdict}")


# ======================================================================
# P2 -- the Encore battery, both pilots, per act
# ======================================================================

def p2(base: cells.Cell) -> None:
    print("\n" + "=" * 78)
    print("P2. Encore economy under each pilot, per act")
    print(f"    runway{encore_telemetry.RUNWAY_SATURATED_TURNS}+ is the new "
          f"column: upkeeps arriving with "
          f"{encore_telemetry.RUNWAY_SATURATED_TURNS} turns of the WHOLE")
    print("    stage's bill in hand. It is the direct sim analogue of the bar "
          "a playtester sees --\n    nobody reads a meter as 'full', they "
          "read it as 'I am not going to run out'.")
    print(f"    constants: SALON_TICK_ENCORE_COST {C.SALON_TICK_ENCORE_COST}, "
          f"SALON_MEMBER_SLOTS {C.SALON_MEMBER_SLOTS} (+ Casting Call), "
          f"SALON_DRY_DAMAGE_MULT {C.SALON_DRY_DAMAGE_MULT}")
    print("=" * 78)

    for label, _note, cell, a in _arms(base):
        print(f"\n  pilot {cell.pilot}  ({label})   {cell.stamp()}")
        print(encore_telemetry.format_row(
            "all acts", _encore_agg(a["results"])))
        for act_i, traces in sorted(
                _by_act(a["results"], "encore_traces").items()):
            print(encore_telemetry.format_row(
                f"act {act_i + 1}", encore_telemetry.aggregate(traces)))


# ======================================================================
# P3 -- where the Fanfare comes from, both pilots
# ======================================================================

def p3(base: cells.Cell) -> None:
    print("\n" + "=" * 78)
    print("P3. Fanfare per-source shares, greedy against stoker")
    print("    The 38d7769 census ran over a HAND-BUILT deck driven straight "
          "through run_fight.\n    These are drafted decks in realistic runs, "
          "so the shares are what the drafter\n    actually assembles rather "
          "than what the table reported building.")
    print("=" * 78)

    for label, _note, cell, a in _arms(base):
        agg = _fanfare_agg(a["results"])
        by_source = agg.get("by_source", {})
        total = sum(by_source.values()) or 1
        combats = agg.get("combats_counted", 1) or 1
        print(f"\n  pilot {cell.pilot}  ({label})   {cell.stamp()}")
        print(f"    mean at read {agg.get('mean_at_read', 0.0):5.1f}   "
              f"floors {agg.get('floor_granted_per_combat', 0.0):5.1f}/combat"
              f"   read-at-cap {agg.get('read_at_cap', 0.0):5.1%}")
        for source, amount in by_source.items():
            print(f"    {source:<16} {amount / combats:6.1f}/combat  "
                  f"{amount / total:6.1%} of generation")


# ======================================================================
# P4 -- Track 3: loop decomposition (log arithmetic only)
# ======================================================================

def p4(base: cells.Cell) -> None:
    """The first two nerf candidates' price tags, computed WITHOUT
    implementing either.

    THE DOUBLE-COUNT. Encore prints Fanfare on the way in (`encore_gained`)
    and again on the way out (`encore_spent`), so a card granting 3 Encore
    silently prints 6 Fanfare. The counterfactual drops the SMALLER leg,
    which is the conservative direction: it prices the cheaper of the two
    single-count rules and therefore cannot overstate what the nerf buys.

    This is pure accounting over emitted events. Nothing is implemented, no
    constant moves, and the lever pick between these two and everything else
    is red-pen.
    """
    print("\n" + "=" * 78)
    print("P4. Loop decomposition — nerf price tags, nothing implemented")
    print("=" * 78)

    for label, _note, cell, a in _arms(base):
        agg = _fanfare_agg(a["results"])
        src = agg.get("by_source", {})
        total = sum(src.values()) or 1
        legs = {k: src.get(k, 0) for k in DOUBLE_COUNT_LEGS}
        centre = src.get("center_stage", 0)
        print(f"\n  pilot {cell.pilot}  ({label})   {cell.stamp()}")
        if legs["encore_gained"]:
            both = sum(legs.values())
            smaller = min(legs, key=lambda k: legs[k])
            single = total - legs[smaller]
            print(f"    Encore double-count      {both / total:6.1%} of all "
                  f"generation "
                  f"({legs['encore_gained']} gained + {legs['encore_spent']} "
                  f"spent)")
            print(f"    single-count counterfactual   drops '{smaller}' (the "
                  f"smaller leg): total generation")
            print(f"      {total} -> {single}, i.e. "
                  f"{(single / total) - 1:+.1%} Fanfare generated")
        else:
            # THE NERF SHIPPED. The Fanfare rework (Track A, 2026-07-28)
            # DELETED the `encore_gained` leg, so this cell's counterfactual
            # has nothing left to remove and would print a meaningless
            # "+0.0%". Saying so is the honest output: a price tag for a
            # change already made is not a price tag, and printing one would
            # invite someone to quote a no-op as evidence the nerf is cheap.
            print("    Encore double-count      GONE. Track A deleted the "
                  "`encore_gained` leg, so Encore\n      now pays the meter "
                  "ONCE, on the way out. The counterfactual this cell used to"
                  "\n      price is the shipped world; the pre-nerf numbers "
                  "(47.2% greedy / 61.6%\n      stoker, -11.7% / -16.3%) are "
                  "ARCHIVE, in docs/archive/sprint-pilot-gap-log-2026-07-28.md.")
            print(f"    encore_spent             "
                  f"{legs['encore_spent'] / total:6.1%} of all generation "
                  f"(the surviving leg)")
            print(f"    encore_absorbed          "
                  f"{src.get('encore_absorbed', 0) / total:6.1%} of all "
                  f"generation (the leg Track A ADDED)")
        print(f"    center_stage             {centre / total:6.1%} of all "
              f"generation")
    print("\n  The lever pick is [USER] red-pen; this cell exists so the pick "
          "is made against a\n  price rather than a guess.")


# ======================================================================

CELLS = {"p1": p1, "p2": p2, "p3": p3, "p4": p4}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    base, rest = cells.parse_overrides(args, BASE)
    which = [a for a in rest if a in CELLS] or list(CELLS)
    for name in CELLS:
        if name in which:
            CELLS[name](base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
