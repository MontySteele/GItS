"""Furina strength battery — playtest 3 follow-up (2026-07-28).

Playtest 3 read: "quite strong now and trivially crushed ascension 0", with
80-90 Fanfare held and 6-7 cards played per turn by the end. Three theories
were put forward, and this file measures what can be measured about each:

  T1  Fanfare gives too much -- the scaling should be lower, or the ramp
      harder to build.
  T2  Encore is too easy to build compared with the Necrobinder summon
      mechanic, whose deck normally holds one or two enablers.
  T3  The loop works but archetypes collapse into good-stuff piles: all
      three engines feed each other, so specialising buys nothing.

READ THIS BEFORE READING ANY NUMBER BELOW. The sim's absolute winrate is
NOT evidence about strength here. The salon arm wins 15% of realistic runs
while the table crushed ascension 0, so something in the model is not
reaching the state the playtest reached -- cell S0 exists to say WHICH
thing, and until it does, every other cell is a RELATIVE instrument. A
sweep row that moves winrate by 8 points tells you the knob matters. The
same row's absolute 15% tells you nothing about the game.

R14: diagnostics feeding a ruling. No acceptance targets in this file, and
no balance change is proposed by it.

Usage: python -m tier05.exp_furina_strength [s0|s1|s2|s3|all] [--runs N]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from tier0 import constants as C
from tier05 import draft, encore_telemetry, fanfare_telemetry, model, sweeps

SEED = 20260728
RUNS = 150

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "docs" / "furina-cards.yaml"

# The playtest's own numbers, as the target the model is being checked
# against. Quoted, not measured -- one table, one pilot, one run.
PLAYTEST_FANFARE = (80, 90)
PLAYTEST_CARDS_PER_TURN = (6, 7)


def _runs(archetype: str, pilot_id: str, n: int, policy=None) -> list:
    return model.run_many(
        "furina", archetype, pilot_id, policy or draft.assigned_policy,
        n, SEED, grant_relics=True, grant_potions=True)


def _cards_per_turn(results: list) -> float:
    plays = sum(s.cards_played for r in results for s in r.fight_stats)
    turns = sum(s.turns for r in results for s in r.fight_stats)
    return plays / turns if turns else 0.0


def _by_act(results: list, attr: str) -> dict[int, list]:
    out: dict[int, list] = {}
    for res in results:
        for act_i, tr in getattr(res, attr):
            out.setdefault(act_i, []).append(tr)
    return out


# =====================================================================
# S0 -- does the model ever reach the state that broke?
# =====================================================================

def s0(runs: int = RUNS) -> None:
    print("=" * 78)
    print(f"S0. Divergence audit — does the sim reach the playtest's state? "
          f"({runs} runs/arm, seed {SEED})")
    print(f"    playtest reported {PLAYTEST_FANFARE[0]}-{PLAYTEST_FANFARE[1]} "
          f"Fanfare held and {PLAYTEST_CARDS_PER_TURN[0]}-"
          f"{PLAYTEST_CARDS_PER_TURN[1]} cards/turn late.")
    print("    If the sim never gets there, every sweep below is measuring a "
          "different game and")
    print("    its ABSOLUTE numbers are not admissible. The deltas still are.")
    print("=" * 78)

    for archetype in ("salon", "fanfare"):
        results = _runs(archetype, archetype, runs)
        wr = sum(r.won for r in results) / len(results)
        print(f"\n  assigned {archetype} — winrate {wr:.1%}, "
              f"{_cards_per_turn(results):.2f} cards/turn (all acts)")
        for act_i, traces in sorted(_by_act(results, "fanfare_traces").items()):
            agg = fanfare_telemetry.aggregate(traces)
            if not agg:
                continue
            act_runs = [r for r in results
                        if any(a == act_i for a, _ in r.fanfare_traces)]
            # BOTH readings of "80-90 Fanfare per turn", because the report
            # is ambiguous and the two differ by a lot. HELD is what the
            # Focus term reads (and what the cap binds); GENERATED per turn
            # is throughput, which the phrase "per turn" more naturally
            # means. Reporting one and calling it the answer would be a
            # category error dressed as a finding.
            per_turn = (agg["requested"] / agg["turns"]
                        if agg.get("turns") else 0.0)
            print(f"    act {act_i + 1}: HELD at read "
                  f"{agg['mean_at_read']:5.1f} (peak {agg['peak_fraction']:.2f} "
                  f"of cap)   GENERATED {per_turn:5.1f}/turn   "
                  f"cards/turn {_cards_per_turn(act_runs):.2f}   "
                  f"(n={agg['reads']} reads)")
        deepest = max(_by_act(results, "fanfare_traces"), default=0)
        agg = fanfare_telemetry.aggregate(
            _by_act(results, "fanfare_traces")[deepest])
        if agg:
            per_turn = (agg["requested"] / agg["turns"]
                        if agg.get("turns") else 0.0)
            for label, value in (("HELD", agg["mean_at_read"]),
                                 ("GENERATED/turn", per_turn)):
                gap = PLAYTEST_FANFARE[0] / value if value else float("inf")
                print(f"    act {deepest + 1} vs table: "
                      f"{PLAYTEST_FANFARE[0]} is {gap:5.1f}x the sim's "
                      f"{label} {value:.1f}")
            print(f"    NOTE: the C# cap is MaxHp/2 + grants, so a HELD 80-90 "
                  f"needs ~160+ max HP or\n          cap grants, and only 3 "
                  f"cards in the pool raise the floor/cap at all. That "
                  f"points\n          at the GENERATED reading -- but it is "
                  f"the table's number to disambiguate.")


# =====================================================================
# S1 -- T1: is the uncapped Focus term the engine?
# =====================================================================

def s1(runs: int = RUNS) -> None:
    """SALON_FOCUS_PER is Fanfare -> member numbers. LOWER means MORE
    scaling (it is a divisor), so the sweep runs from generous to stingy.

    Read as a delta, per the header. The question this answers is "does
    this knob carry the archetype's output", not "what should it be".
    """
    print("=" * 78)
    print(f"S1 (T1). SALON_FOCUS_PER sweep — {runs} runs/cell, seed {SEED}")
    print(f"    shipped value {C.SALON_FOCUS_PER}: +1 to EVERY member number "
          f"per {C.SALON_FOCUS_PER} Fanfare held, uncapped.")
    print("    lower = more scaling. The playtest's 80-90 Fanfare is +8/+9 "
          "per member per tick at the shipped value.")
    print("=" * 78)

    def cell(value):
        results = _runs("salon", "salon", runs)
        return {
            "winrate": sum(r.won for r in results) / len(results),
            "cards_per_turn": _cards_per_turn(results),
            "acts": sum(r.acts_completed for r in results) / len(results),
            "damage": sum(s.total_damage_dealt
                          for r in results for s in r.fight_stats)
                      / max(1, sum(len(r.fight_stats) for r in results)),
        }

    print(f"\n  {'FOCUS_PER':>10} {'winrate':>9} {'acts':>6} "
          f"{'cards/turn':>11} {'dmg/fight':>10}")
    base = None
    for value, res in sweeps.sweep("SALON_FOCUS_PER", (5, 10, 20, 40), cell):
        if base is None:
            base = res["winrate"]
        print(f"  {value:>10} {res['winrate']:>8.1%} {res['acts']:>6.2f} "
              f"{res['cards_per_turn']:>11.2f} {res['damage']:>10.1f}")
    print("\n  (5 is twice the shipped scaling, 40 is a quarter of it. A flat "
          "column means the term\n   is not what carries her; a steep one "
          "means T1 has found the lever.)")


# =====================================================================
# S2 -- T2: how much Encore does the POOL hand out?
# =====================================================================

_ENCORE_GRANT_OPS = {"gain_encore"}
_ENCORE_SPEND_OPS = {"spend_encore"}


def _walk(effects):
    for fx in effects or []:
        yield fx
        for key in ("then", "else", "effects"):
            yield from _walk(fx.get(key))


def _sheet_rows() -> list[dict]:
    """The sheet is the source of truth for "what does the POOL offer",
    which is the T2 question -- tier0's card index is keyed for play, not
    for census, and does not carry the Furina pool as a set."""
    return yaml.safe_load(SHEET.read_text(encoding="utf-8"))


def s2(runs: int = RUNS) -> None:
    print("=" * 78)
    print(f"S2 (T2). Encore access census — how many cards even DO this? "
          f"({runs} runs, seed {SEED})")
    print("    The Necrobinder comparison cannot be MEASURED here: no summon "
          "data for that character")
    print("    exists in game_ref, which holds the Ironclad only. The claim "
          "'one or two enablers' is")
    print("    taken as given and Furina's own count is measured against it.")
    print("=" * 78)

    rows = _sheet_rows()
    grants: dict[str, list[str]] = {}
    spends: list[str] = []
    for row in rows:
        ops = {fx.get("op") for fx in _walk(row.get("effects"))}
        if ops & _ENCORE_GRANT_OPS:
            grants.setdefault(row.get("rarity", "?"), []).append(row["id"])
        if ops & _ENCORE_SPEND_OPS:
            spends.append(row["id"])
    total_grants = sum(len(v) for v in grants.values())
    print(f"\n  pool size {len(rows)}")
    print(f"  cards that GRANT Encore: {total_grants} "
          f"({total_grants / len(rows):.0%} of the pool)")
    for rarity in ("basic", "common", "uncommon", "rare"):
        ids = grants.get(rarity, [])
        if ids:
            print(f"    {rarity:<10} {len(ids):>2}  {', '.join(sorted(ids))}")
    print(f"  cards that SPEND Encore: {len(spends)}  "
          f"{', '.join(sorted(spends)) if spends else '(none)'}")
    print("\n  The upkeep is the only other sink, and it is automatic. Every "
          "point above what the\n  stage burns is a free damage buffer, "
          "because absorption is not a decision.")

    results = _runs("salon", "salon", runs)
    every = [tr for r in results for _, tr in r.encore_traces]
    agg = encore_telemetry.aggregate(every)
    print(f"\n  MEASURED, salon arm: {agg['gained_per_combat']:.1f} gained "
          f"vs {agg['drained_per_combat']:.1f} drained per combat "
          f"({agg['spent_per_combat']:.1f} spent + "
          f"{agg['absorbed_per_combat']:.1f} absorbed)")
    print(f"  ratio {agg['gain_drain_ratio']:.2f}; ends combat holding "
          f"{agg['mean_end_encore']:.1f}")


# =====================================================================
# S3 -- T3: does specialising pay?
# =====================================================================

def s3(runs: int = RUNS) -> None:
    """The good-stuff test.

    `adaptive_policy` drafts by card quality and IGNORES the archetype label
    by construction -- it is the good-stuff pile in policy form. If a
    focused draft cannot beat it, the archetypes are decorative: there is no
    payoff for specialising, which is exactly T3.
    """
    print("=" * 78)
    print(f"S3 (T3). Does specialising pay? — {runs} runs/arm, seed {SEED}")
    print("    adaptive drafts by card quality and never sees the archetype "
          "label: the good-stuff pile.")
    print("    If focused arms do not beat it, specialising buys nothing.")
    print("=" * 78)

    rows = []
    for archetype in ("salon", "fanfare", "spotlight"):
        res = _runs(archetype, archetype, runs)
        rows.append((f"assigned {archetype}", res))
    rows.append(("adaptive (good stuff)",
                 _runs("salon", "salon", runs, draft.adaptive_policy)))

    print(f"\n  {'arm':<24} {'winrate':>9} {'acts':>6} {'cards/turn':>11}")
    for label, res in rows:
        wr = sum(r.won for r in res) / len(res)
        acts = sum(r.acts_completed for r in res) / len(res)
        print(f"  {label:<24} {wr:>8.1%} {acts:>6.2f} "
              f"{_cards_per_turn(res):>11.2f}")

    # Deck composition: how MIXED is what each policy actually drafts? A
    # focused arm that ends up with the same register spread as good-stuff
    # is the collapse T3 describes, whatever the winrates say.
    print(f"\n  {'arm':<24} {'mean deck':>10}  archetype mix of drafted cards")
    for label, res in rows:
        counts: dict[str, int] = {}
        size = 0
        for r in res:
            size += len(r.deck_ids)
            for cid in r.deck_ids:
                for arch in _archetypes_of(cid):
                    counts[arch] = counts.get(arch, 0) + 1
        total = sum(counts.values()) or 1
        mix = "  ".join(f"{k} {v / total:.0%}"
                        for k, v in sorted(counts.items(),
                                           key=lambda kv: -kv[1])[:4])
        print(f"  {label:<24} {size / len(res):>10.1f}  {mix}")


_ARCH_CACHE: dict[str, tuple[str, ...]] = {}


def _archetypes_of(card_id: str) -> tuple[str, ...]:
    if not _ARCH_CACHE:
        for row in _sheet_rows():
            _ARCH_CACHE[row["id"]] = tuple(row.get("archetypes") or ())
    return _ARCH_CACHE.get(re.sub(r"\+$", "", card_id), ())


# =====================================================================
# S1B -- T1, at the TABLE's Fanfare level rather than the sim's
# =====================================================================

def s1b(runs: int = RUNS) -> None:
    """S1's flatness has a built-in floor: the Focus term's contribution is
    proportional to Fanfare HELD, and the sim holds ~28 where the table
    reported 80-90. Sweeping the term in a world that never gets there
    UNDERSTATES it by construction.

    So raise the ceiling instead. FANFARE_CAP_FRACTION is cap = fraction of
    max HP; at the shipped 0.5 the meter peaks at 0.81 of its cap, so the
    cap IS close to binding. Lifting it lets the meter run to something
    nearer the table's report, and the question becomes: does the archetype
    get sharply better when Fanfare is allowed to be large?
    """
    print("=" * 78)
    print(f"S1B (T1). FANFARE_CAP_FRACTION sweep — {runs} runs/cell, "
          f"seed {SEED}")
    print(f"    shipped {C.FANFARE_CAP_FRACTION} (cap = that fraction of max "
          f"HP). The meter already peaks at 0.81 of cap,")
    print("    so this is close to binding. Raising it is the only way to ask "
          "S1's question at the")
    print("    Fanfare level the table actually played at.")
    print("=" * 78)

    def cell(value):
        results = _runs("salon", "salon", runs)
        traces = [tr for r in results for _, tr in r.fanfare_traces]
        agg = fanfare_telemetry.aggregate(traces)
        return {
            "winrate": sum(r.won for r in results) / len(results),
            "acts": sum(r.acts_completed for r in results) / len(results),
            "held": agg.get("mean_at_read", 0.0),
            "at_cap": agg.get("read_at_cap", 0.0),
            "damage": sum(s.total_damage_dealt
                          for r in results for s in r.fight_stats)
                      / max(1, sum(len(r.fight_stats) for r in results)),
        }

    print(f"\n  {'CAP_FRACTION':>13} {'winrate':>9} {'acts':>6} "
          f"{'mean held':>10} {'at-cap':>8} {'dmg/fight':>10}")
    for value, res in sweeps.sweep("FANFARE_CAP_FRACTION",
                                   (0.5, 1.0, 2.0, 4.0), cell):
        print(f"  {value:>13} {res['winrate']:>8.1%} {res['acts']:>6.2f} "
              f"{res['held']:>10.1f} {res['at_cap']:>7.1%} "
              f"{res['damage']:>10.1f}")
    print("\n  (If winrate climbs with the ceiling, Fanfare IS the engine and "
          "T1 is right --\n   the term is only flat in S1 because the sim "
          "never gets to spend it.)")


# =====================================================================
# S1C -- where does the Fanfare actually COME from? (T1 x T2)
# =====================================================================

def s1c(runs: int = RUNS) -> None:
    """S1B says the ceiling is not the limiter, so Fanfare is GENERATION
    limited -- which makes "where does it come from" the question T1's
    "harder to build" actually turns on.

    Both Encore channels are swept together because they are one economy:
    every point of Encore generates Fanfare on the way in AND on the way
    out, so a card that grants 3 Encore is worth 6 Fanfare across its life.
    With 19 of 78 cards granting Encore (S2), this is the join between T2
    and T1 -- and cell (0, 0) is the counterfactual "Encore stops feeding
    Fanfare at all".
    """
    print("=" * 78)
    print(f"S1C (T1 x T2). Encore -> Fanfare conversion — {runs} runs/cell, "
          f"seed {SEED}")
    print(f"    shipped: {C.FANFARE_PER_ENCORE_GAINED} Fanfare per Encore "
          f"GAINED, {C.FANFARE_PER_ENCORE_SPENT} per Encore SPENT.")
    print("    Every point of Encore therefore prints Fanfare twice. 19 of "
          "78 cards grant Encore.")
    print("=" * 78)

    def cell(gained, spent):
        results = _runs("salon", "salon", runs)
        traces = [tr for r in results for _, tr in r.fanfare_traces]
        agg = fanfare_telemetry.aggregate(traces)
        return {
            "winrate": sum(r.won for r in results) / len(results),
            "acts": sum(r.acts_completed for r in results) / len(results),
            "held": agg.get("mean_at_read", 0.0),
            "damage": sum(s.total_damage_dealt
                          for r in results for s in r.fight_stats)
                      / max(1, sum(len(r.fight_stats) for r in results)),
        }

    print(f"\n  {'gained':>7} {'spent':>6} {'winrate':>9} {'acts':>6} "
          f"{'mean held':>10} {'dmg/fight':>10}")
    for row, res in sweeps.sweep_pairs(
            ("FANFARE_PER_ENCORE_GAINED", "FANFARE_PER_ENCORE_SPENT"),
            ((1, 1), (1, 0), (0, 1), (0, 0)), cell):
        print(f"  {row[0]:>7} {row[1]:>6} {res['winrate']:>8.1%} "
              f"{res['acts']:>6.2f} {res['held']:>10.1f} "
              f"{res['damage']:>10.1f}")
    print("\n  ((0, 0) is the counterfactual: Encore stops feeding Fanfare "
          "entirely. The distance\n   from (1, 1) to (0, 0) is how much of "
          "her ramp the Encore economy is paying for.)")


# =====================================================================
# S5 -- if not Fanfare, then what? The stage itself.
# =====================================================================

def s5(runs: int = RUNS) -> None:
    """S1, S1B and S1C between them say the Fanfare channel is SHALLOW: 8x
    the scaling moves 5 points, the ceiling moves nothing, and cutting the
    Encore economy out of Fanfare entirely moves 1.4. Something else is
    carrying the archetype, and the obvious candidate is the stage itself --
    three members ticking every turn for their printed numbers, before any
    scaling term touches them.

    SALON_MEMBER_SLOTS is the size of that engine. This sweep is the
    counterfactual for "how much of her is just the stage existing", and it
    is the lever A12 deliberately made bigger.
    """
    print("=" * 78)
    print(f"S5. SALON_MEMBER_SLOTS sweep — {runs} runs/cell, seed {SEED}")
    print(f"    shipped {C.SALON_MEMBER_SLOTS}. Box Seats adds +1 (+2 "
          f"upgraded) on top of this.")
    print("=" * 78)

    def cell(value):
        results = _runs("salon", "salon", runs)
        every = [tr for r in results for _, tr in r.encore_traces]
        agg = encore_telemetry.aggregate(every)
        return {
            "winrate": sum(r.won for r in results) / len(results),
            "acts": sum(r.acts_completed for r in results) / len(results),
            "damage": sum(s.total_damage_dealt
                          for r in results for s in r.fight_stats)
                      / max(1, sum(len(r.fight_stats) for r in results)),
            "dry": agg.get("dry_rate", 0.0),
        }

    print(f"\n  {'SLOTS':>6} {'winrate':>9} {'acts':>6} {'dmg/fight':>10} "
          f"{'dry upkeeps':>12}")
    for value, res in sweeps.sweep("SALON_MEMBER_SLOTS", (1, 2, 3, 4), cell):
        print(f"  {value:>6} {res['winrate']:>8.1%} {res['acts']:>6.2f} "
              f"{res['damage']:>10.1f} {res['dry']:>11.1%}")
    print("\n  (A steep column here means the archetype's power is the STAGE, "
          "not the scaling --\n   and that A12's cap raise is a bigger lever "
          "than any Fanfare number.)")


# =====================================================================
# S4 -- calibration: is 16.7% high?
# =====================================================================

def s4(runs: int = RUNS) -> None:
    """The absolute winrate means nothing on its own; against the roster it
    means everything. The reference Ironclad is the frozen baseline this
    world is calibrated on, so "how many times the reference" is the honest
    statement of Furina's power."""
    print("=" * 78)
    print(f"S4. Roster calibration — {runs} runs/arm, seed {SEED}, same world")
    print("    'Furina is too strong' is a comparative claim. This is the "
          "comparison.")
    print("=" * 78)

    arms = (
        ("furina / salon", "furina", "salon", "salon"),
        ("furina / fanfare", "furina", "fanfare", "fanfare"),
        ("klee", "klee", "generic", "generic"),
        ("kokomi", "kokomi", "generic", "generic"),
        ("ref_ironclad", "ref_ironclad", "generic", "generic"),
        ("real_ironclad", "real_ironclad", "generic", "generic"),
    )
    print(f"\n  {'arm':<20} {'winrate':>9} {'acts':>6} {'vs ref_IC':>10}")
    rows = []
    for label, character, archetype, pilot_id in arms:
        try:
            results = model.run_many(
                character, archetype, pilot_id, draft.assigned_policy,
                runs, SEED, grant_relics=True, grant_potions=True)
        except Exception as exc:                     # noqa: BLE001
            print(f"  {label:<20} SKIPPED: {exc}")
            continue
        rows.append((label,
                     sum(r.won for r in results) / len(results),
                     sum(r.acts_completed for r in results) / len(results)))
    ref = next((wr for label, wr, _ in rows if label == "ref_ironclad"), None)
    for label, wr, acts in rows:
        ratio = f"{wr / ref:>9.1f}x" if ref else "        --"
        print(f"  {label:<20} {wr:>8.1%} {acts:>6.2f} {ratio}")


def main(argv: list[str]) -> None:
    cell = argv[1] if len(argv) > 1 else "all"
    runs = RUNS
    if "--runs" in argv:
        runs = int(argv[argv.index("--runs") + 1])
    for name, fn in (("s0", s0), ("s1", s1), ("s1b", s1b), ("s2", s2),
                     ("s1c", s1c), ("s3", s3), ("s4", s4), ("s5", s5)):
        if cell in (name, "all"):
            fn(runs)


if __name__ == "__main__":
    main(sys.argv)
