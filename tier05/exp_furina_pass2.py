"""Furina sheet pass 2 — the pre-registered experiment battery.

Registered in furina-sheet-pass-2-plan.md BEFORE running (null results
binding). Blocks:

E1. SPOTLIGHT_BASE_MULT sweep {1.0, 1.25} x §8 criterion-2 delete-test
    (R16.2). Decision rule (registered): if exactly one value passes the
    delete-test on all four encounters, it wins; if both pass, 1.0 wins
    unless spotlight_weighted's punisher/tank_boss floors at 1.0 fall
    more than 2pt below their 1.25 values; if neither passes, the CARD
    numbers iterate (§2.2a knob order), not the base mult.
    Criterion 1 (self_carry) is re-checked in the same sweep.

E2. FANFARE_CAP_FRACTION confirmation re-sweep {0.25, 0.5, 0.75} with
    the 6-blood uncapper, under the E1 winner. The ratified 0.5 STAYS
    unless its punisher winrate leaves [10%, 55%].

E3. A6 instrument v1-vs-v2 derivation table (R18): ref anchor, Klee
    re-derived, Furina re-scored. v1 composite recomputed from the same
    raws so the discontinuity is measured, not estimated.

E4. Graded-encounter EP battery (R21, registration (i)): tank_boss at
    enemy-HP grades x0.6..x1.4; per seed, ascending ladder until first
    loss; score = grades cleared (0-5). Arms differ ONLY in
    encore_performance vs courtroom_drama (warm-body control).

Usage: python -m tier05.exp_furina_pass2 [e1|e2|e3|e4]
Seed 20260720 throughout; deterministic.
"""

from __future__ import annotations

import statistics
import sys

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import axes, metrics
from tier0.pilot.policy import make_pilot

SEED = 20260720
FIGHTS = 1000
ENCOUNTERS = ("punisher", "swarm", "attrition", "tank_boss")
MULTS = (1.0, 1.25)
FLOOR_ENCOUNTERS = ("punisher", "tank_boss")
FLOOR_TOLERANCE_PT = 2.0


def _battery(character: str, deck: str, pilot_id: str, fights: int,
             seed: int) -> dict[str, list[metrics.FightStats]]:
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    out = {}
    for enc in ENCOUNTERS:
        stats = []
        for i in range(fights):
            player = loader.build_player(character, deck)
            state = run_fight(player, loader.build_encounter(enc), pilot,
                              seed=seed + i)
            stats.append(metrics.extract(state, player.max_hp))
        out[enc] = stats
    return out


def _winrates(stats_by_enc) -> dict[str, float]:
    return {enc: metrics.summarize(stats)["winrate"]
            for enc, stats in stats_by_enc.items()}


def e1() -> float:
    print("=" * 72)
    print("E1. SPOTLIGHT_BASE_MULT sweep x delete-test "
          f"({FIGHTS} fights/cell)")
    print("=" * 72)
    configs = [("spotlight_weighted", "spotlight"),
               ("spotlight_companions_only", "spotlight"),
               ("self_carry", "fanfare"),
               ("salon_weighted", "salon"),
               ("fanfare_weighted", "fanfare")]
    default = C.SPOTLIGHT_BASE_MULT
    results: dict[float, dict[str, dict[str, float]]] = {}
    for m in MULTS:
        C.SPOTLIGHT_BASE_MULT = m
        results[m] = {}
        for deck, pilot in configs:
            results[m][deck] = _winrates(
                _battery("furina", deck, pilot, FIGHTS, SEED))
            row = "  ".join(f"{e}: {results[m][deck][e]:.1%}"
                            for e in ENCOUNTERS)
            print(f"  mult {m:.2f}  {deck:<28} {row}")
        print()
    C.SPOTLIGHT_BASE_MULT = default

    passes = {}
    for m in MULTS:
        full = results[m]["spotlight_weighted"]
        probe = results[m]["spotlight_companions_only"]
        per_enc = {e: full[e] >= probe[e] for e in ENCOUNTERS}
        passes[m] = all(per_enc.values())
        detail = "  ".join(
            f"{e}: {full[e]:.1%} vs {probe[e]:.1%} "
            f"({(full[e] - probe[e]) * 100:+.1f}pt)" for e in ENCOUNTERS)
        print(f"  delete-test @ mult {m:.2f}: "
              f"{'PASS' if passes[m] else 'FAIL'}  {detail}")

    print("\n  criterion 1 (self_carry must NOT beat the archetypes):")
    for m in MULTS:
        for e in ENCOUNTERS:
            sc = results[m]["self_carry"][e]
            best = max(results[m]["salon_weighted"][e],
                       results[m]["spotlight_weighted"][e])
            if sc > best:
                print(f"    mult {m:.2f} {e}: VIOLATION "
                      f"(self {sc:.1%} > archetypes {best:.1%})")
    print("    (no line above a mult = holds everywhere)")

    if passes[1.0] and passes[1.25]:
        floors_ok = all(
            (results[1.0]["spotlight_weighted"][e]
             - results[1.25]["spotlight_weighted"][e]) * 100
            >= -FLOOR_TOLERANCE_PT
            for e in FLOOR_ENCOUNTERS)
        chosen = 1.0 if floors_ok else 1.25
    elif passes[1.0] or passes[1.25]:
        chosen = 1.0 if passes[1.0] else 1.25
    else:
        chosen = None
    print(f"\n  REGISTERED DECISION RULE -> "
          f"{'chosen mult ' + str(chosen) if chosen is not None else 'NEITHER PASSES: iterate card numbers'}")
    return chosen


def e2(mult: float) -> None:
    print()
    print("=" * 72)
    print(f"E2. FANFARE_CAP_FRACTION confirmation re-sweep "
          f"(6-blood uncapper; mult {mult:.2f}; 500 fights/cell)")
    print("=" * 72)
    default_mult = C.SPOTLIGHT_BASE_MULT
    default_cap = C.FANFARE_CAP_FRACTION
    C.SPOTLIGHT_BASE_MULT = mult
    for frac in (0.25, 0.5, 0.75):
        C.FANFARE_CAP_FRACTION = frac
        wr = _winrates(_battery("furina", "fanfare_weighted", "fanfare",
                                500, SEED))
        row = "  ".join(f"{e}: {wr[e]:.1%}" for e in ENCOUNTERS)
        mark = "  <- ratified" if frac == default_cap else ""
        print(f"    cap {frac:.2f}x maxHP   {row}{mark}")
    C.FANFARE_CAP_FRACTION = default_cap
    C.SPOTLIGHT_BASE_MULT = default_mult
    print("    ratified 0.5 stays unless punisher leaves [10%, 55%] "
          "(registered rule)")


def e3() -> None:
    print()
    print("=" * 72)
    print(f"E3. A6 instrument v1 vs v2 (R18; {FIGHTS} fights/config)")
    print("=" * 72)
    base_stats = _battery("ref_ironclad", "starter", "generic", FIGHTS, SEED)
    base_raw = axes.raw_axes(base_stats)

    def both(raw):
        v1 = 3.0 * (0.7 * raw["A6_aoe"] / max(1e-9, base_raw["A6_aoe"])
                    + 0.3 * raw["A6_debuff"] / max(1e-9, base_raw["A6_debuff"]))
        v2 = axes.normalize(raw, base_raw)["A6_utility"]
        return v1, v2, raw["A6_app"]

    rows = [("ref_ironclad", "starter", "generic")]
    for char in ("klee", "furina"):
        rows.append((char, "starter", "generic"))
        rows += [(char, deck, pilot)
                 for deck, pilot in loader.archetype_decks(char).items()]
    print(f"  {'config':<38} {'uptime':>7} {'A6 v1':>7} {'A6 v2':>7}")
    per_char: dict[str, list[tuple[float, float]]] = {}
    for char, deck, pilot in rows:
        raw = (base_raw if (char, deck) == ("ref_ironclad", "starter")
               else axes.raw_axes(_battery(char, deck, pilot, FIGHTS, SEED)))
        v1, v2, app = both(raw)
        if deck != "starter":
            per_char.setdefault(char, []).append((v1, v2))
        print(f"  {char + '/' + deck:<38} {app:>6.1%} {v1:>7.2f} {v2:>7.2f}")
    for char, pairs in per_char.items():
        med1 = statistics.median(p[0] for p in pairs)
        med2 = statistics.median(p[1] for p in pairs)
        print(f"  {char} archetype-median A6: v1 {med1:.2f} -> v2 {med2:.2f} "
              f"(discontinuous BY DESIGN; label everything)")


GRADES = (0.6, 0.8, 1.0, 1.2, 1.4)
LADDER_SEEDS = 400


def _graded_fight(deck_ids: list[str], pilot, grade: float,
                  seed: int) -> bool:
    player = loader.build_player_from_ids(
        "furina", loader.starting_deck("furina") + deck_ids)
    enemies = loader.build_encounter("tank_boss")
    for en in enemies:
        en.hp = int(en.hp * grade)
        en.max_hp = int(en.max_hp * grade)
    state = run_fight(player, enemies, pilot, seed=seed)
    return bool(state.player.alive) and not state.living_enemies


def e4() -> None:
    print()
    print("=" * 72)
    print(f"E4. Graded-encounter EP battery (R21 reg (i); tank_boss x "
          f"{GRADES}; {LADDER_SEEDS} seeds/arm)")
    print("=" * 72)
    package = loader.character_packages("furina")["spotlight_weighted"]
    arms = {
        "+EP": package,
        "control": [("courtroom_drama" if c == "encore_performance" else c)
                    for c in package],
    }
    pilot = make_pilot(loader.pilot_weights("spotlight"))
    print(f"  arms differ only in: encore_performance vs courtroom_drama")
    scores: dict[str, list[int]] = {}
    for arm, ids in arms.items():
        arm_scores = []
        for r in range(LADDER_SEEDS):
            cleared = 0
            for g_i, grade in enumerate(GRADES):
                if _graded_fight(ids, pilot, grade, SEED + r * 7 + g_i):
                    cleared += 1
                else:
                    break
            arm_scores.append(cleared)
        scores[arm] = arm_scores
    print(f"  {'arm':<9} {'median':>7} {'mean':>7} {'P90':>5} "
          f"{'full-clear':>10}")
    for arm, s in scores.items():
        s_sorted = sorted(s)
        p90 = s_sorted[int(0.9 * (len(s_sorted) - 1))]
        print(f"  {arm:<9} {statistics.median(s):>7.1f} "
              f"{statistics.mean(s):>7.2f} {p90:>5} "
              f"{sum(1 for x in s if x == len(GRADES)) / len(s):>9.1%}")
    print("\n  registration (i): +EP should lift P90 more than median. "
          "If the arms do not separate, the registration STAYS OPEN.")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    chosen = None
    if which in ("e1", "all"):
        chosen = e1()
    if which in ("e2", "all"):
        e2(chosen if chosen is not None else C.SPOTLIGHT_BASE_MULT)
    if which in ("e3", "all"):
        e3()
    if which in ("e4", "all"):
        e4()
