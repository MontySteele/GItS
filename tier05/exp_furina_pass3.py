"""Furina sheet pass 3 — ARCHIVED pre-registered experiment battery.

Selector v5 superseded the character-depth experiment this file describes.
Do not use its W0/world labels for current balance; use exp_furina_modes.

Registered in furina-sheet-pass-3-plan.md BEFORE running (null results
binding). Blocks:

W0. Ceiling designation experiment (R33): FORCED-self vs
    FORCED-companion designation (oracle arms via effects.SPOTLIGHT_FORCE;
    heuristic v2 bypassed, not trusted) x SPOTLIGHT_BASE_MULT {1.25, 1.5}
    on the companion arms x depth {5, 3}. Exercise-counter law
    (DECISIONS 87) applied as a REGISTERED VALIDITY GATE: companion cells
    must READ the knob, self cells must not, else the cell is INVALID and
    the run stops. Registered reading: outward designation is
    value-rational at a (depth, mult) dose iff battery-mean winrate delta
    (companion - self) >= 0; single-encounter wins >= 2pt flagged as
    NICHE. R14: diagnostics feeding a ruling, no acceptance targets.

WORLD. The shipping-world check, re-run after each design window (no
    overrides — measures current constants + selector v3): §8
    criterion-2 delete-test (spotlight_weighted vs companions-only
    probe) + criterion 1 (self_carry must not beat the archetypes).
    NOTE: under selector v3 the companions-only probe designates its
    full-kit Chevreuse in crowd fights and reads SPOTLIGHT_BASE_MULT —
    the probe is STRONGER than its pass-2 (v2, self-aimed) archive; a
    delete-test pass in this world is a harder, more honest bar. Never
    compare selector-v2 and selector-v3 numbers unlabeled.

CAP. FANFARE_CAP re-check {0.25, 0.5, 0.75} — runs AFTER the W1 flip
    (E2's confirmation is pre-flip only). Registered rule unchanged:
    0.5 stays unless fanfare punisher leaves [10%, 55%].

Usage: python -m tier05.exp_furina_pass3 [w0|world|cap]
Seed 20260720 throughout; deterministic.
"""

from __future__ import annotations

import sys

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.pilot.policy import make_pilot

SEED = 20260720
FIGHTS = 1000
ENCOUNTERS = ("punisher", "swarm", "attrition", "tank_boss")
NICHE_PT = 2.0


def _depth5_ids() -> list[str]:
    return list(loader.character_packages("furina")["spotlight_weighted"])


def _depth3_ids() -> list[str]:
    """Depth-5 minus one interdiction + the grenades, replaced by
    non-machinery Furina glue (deck size and machinery held fixed)."""
    ids = _depth5_ids()
    ids.remove("chevreuse_interdiction_fire")
    ids.remove("chevreuse_bursting_grenades")
    return ids + ["courtroom_drama", "macaron_break"]


def _cell(deck_ids: list[str], force: str, mult: float,
          fights: int) -> tuple[dict[str, float], int]:
    """One W0 cell: returns per-encounter winrates + knob read count."""
    pilot = make_pilot(loader.pilot_weights("spotlight"))
    default_mult = C.SPOTLIGHT_BASE_MULT
    effects.reset_knob_reads()
    effects.SPOTLIGHT_FORCE = force
    C.SPOTLIGHT_BASE_MULT = mult
    try:
        wr = {}
        for enc in ENCOUNTERS:
            wins = 0
            for i in range(fights):
                player = loader.build_player_from_ids(
                    "furina", loader.starting_deck("furina") + deck_ids)
                state = run_fight(player, loader.build_encounter(enc),
                                  pilot, seed=SEED + i)
                stats = metrics.extract(state, player.max_hp)
                wins += 1 if stats.won else 0
            wr[enc] = wins / fights
    finally:
        effects.SPOTLIGHT_FORCE = None
        C.SPOTLIGHT_BASE_MULT = default_mult
    return wr, effects.KNOB_READS.get("SPOTLIGHT_BASE_MULT", 0)


def w0() -> None:
    print("=" * 72)
    print(f"W0. Ceiling designation experiment (R33; {FIGHTS} fights/enc; "
          "forced arms, R14)")
    print("=" * 72)
    depths = {5: _depth5_ids(), 3: _depth3_ids()}
    results: dict[tuple, dict[str, float]] = {}
    for depth, ids in depths.items():
        cells = [("self", C.SPOTLIGHT_BASE_MULT)] + [
            ("companion", m) for m in (1.25, 1.5)]
        for force, mult in cells:
            wr, reads = _cell(ids, force, mult, FIGHTS)
            key = (depth, force, mult)
            results[key] = wr
            row = "  ".join(f"{e}: {wr[e]:.1%}" for e in ENCOUNTERS)
            label = (f"depth {depth} {force:<9}"
                     + (f" mult {mult:.2f}" if force == "companion"
                        else "          "))
            print(f"  {label}  {row}  [knob reads: {reads}]")
            # REGISTERED VALIDITY GATE (exercise-counter law, DECISIONS 87)
            if force == "companion" and reads == 0:
                print("  !! INVALID CELL: forced-companion never read the "
                      "knob — stopping (no silent E1 repeat)")
                sys.exit(1)
            if force == "self" and reads != 0:
                print("  !! INVALID CELL: forced-self read the knob — "
                      "stopping (oracle leak)")
                sys.exit(1)
        print()

    print("  registered reading (companion - self, battery mean; "
          f"niche flag at +{NICHE_PT:.0f}pt on any encounter):")
    for depth in depths:
        base = results[(depth, "self", C.SPOTLIGHT_BASE_MULT)]
        for mult in (1.25, 1.5):
            comp = results[(depth, "companion", mult)]
            deltas = {e: (comp[e] - base[e]) * 100 for e in ENCOUNTERS}
            mean = sum(deltas.values()) / len(deltas)
            niches = [e for e, d in deltas.items() if d >= NICHE_PT]
            verdict = ("VALUE-RATIONAL" if mean >= 0
                       else "not value-rational")
            detail = "  ".join(f"{e}: {d:+.1f}pt" for e, d in deltas.items())
            print(f"    depth {depth} mult {mult:.2f}: mean {mean:+.2f}pt "
                  f"-> {verdict}"
                  + (f"  NICHE: {','.join(niches)}" if niches else ""))
            print(f"      {detail}")


def world() -> None:
    print("=" * 72)
    print(f"WORLD. Shipping-world delete-test + criterion 1 "
          f"(selector v3, current constants; {FIGHTS} fights/enc)")
    print("=" * 72)
    configs = [("spotlight_weighted", "spotlight"),
               ("spotlight_companions_only", "spotlight"),
               ("self_carry", "fanfare"),
               ("salon_weighted", "salon"),
               ("fanfare_weighted", "fanfare")]
    packages = loader.character_packages("furina")
    wr: dict[str, dict[str, float]] = {}
    for deck, pilot_id in configs:
        pilot = make_pilot(loader.pilot_weights(pilot_id))
        wr[deck] = {}
        for enc in ENCOUNTERS:
            wins = 0
            for i in range(FIGHTS):
                player = loader.build_player_from_ids(
                    "furina",
                    loader.starting_deck("furina") + list(packages[deck]))
                state = run_fight(player, loader.build_encounter(enc),
                                  pilot, seed=SEED + i)
                wins += 1 if metrics.extract(state, player.max_hp).won else 0
            wr[deck][enc] = wins / FIGHTS
        row = "  ".join(f"{e}: {wr[deck][e]:.1%}" for e in ENCOUNTERS)
        print(f"  {deck:<28} {row}")
    full, probe = wr["spotlight_weighted"], wr["spotlight_companions_only"]
    per = {e: full[e] >= probe[e] for e in ENCOUNTERS}
    detail = "  ".join(f"{e}: {(full[e] - probe[e]) * 100:+.1f}pt"
                       for e in ENCOUNTERS)
    print(f"\n  delete-test: {'PASS' if all(per.values()) else 'FAIL'}  "
          f"{detail}")
    print("  criterion 1 (self_carry must NOT beat the archetypes):")
    bad = False
    for e in ENCOUNTERS:
        best = max(wr["salon_weighted"][e], wr["spotlight_weighted"][e])
        if wr["self_carry"][e] > best:
            bad = True
            print(f"    {e}: VIOLATION (self {wr['self_carry'][e]:.1%} > "
                  f"archetypes {best:.1%})")
    if not bad:
        print("    holds everywhere")


def floors4k(encounters=("punisher", "tank_boss")) -> None:
    """Delete-test dire-floor cells at 4000 fights (pre-declared resolver).

    At dire floors (~0-2%) the 1000-fight battery has ~±0.9pt CI per arm
    — sub-point deltas are unresolvable at battery n. This block re-runs
    ONLY the named floor pairs at 4000 fights and its result is DECLARED
    THE RECORD for those cells before running (no optional stopping: one
    run, whatever it says)."""
    print("=" * 72)
    print(f"FLOORS-4K. Delete-test floor cells {encounters} at 4000 "
          "fights (pre-declared resolver)")
    print("=" * 72)
    packages = loader.character_packages("furina")
    pilot = make_pilot(loader.pilot_weights("spotlight"))
    for enc in encounters:
        wr = {}
        for deck in ("spotlight_weighted", "spotlight_companions_only"):
            wins = 0
            for i in range(4000):
                player = loader.build_player_from_ids(
                    "furina", loader.starting_deck("furina")
                    + list(packages[deck]))
                state = run_fight(player, loader.build_encounter(enc),
                                  pilot, seed=SEED + i)
                wins += 1 if metrics.extract(state, player.max_hp).won else 0
            wr[deck] = wins / 4000
            print(f"  {deck:<28} {enc}: {wr[deck]:.2%}")
        d = (wr["spotlight_weighted"]
             - wr["spotlight_companions_only"]) * 100
        print(f"  {enc} delta (full - probe): {d:+.2f}pt -> "
              f"{'PASS' if d >= 0 else 'FAIL'} on this cell (the record)")


def a6terms() -> None:
    """A6 v2 composite decomposition per deck (diagnostic for the pass-3
    report ask: which term carries the shortfall). Recomputes the same
    raws the scorecard uses and prints the three anchored terms."""
    from tier0.harness import axes
    print("=" * 72)
    print("A6-TERMS. v2 composite decomposition (1000 fights/config)")
    print("=" * 72)

    def battery(char, deck, pilot_id):
        pilot = make_pilot(loader.pilot_weights(pilot_id))
        out = {}
        for enc in ENCOUNTERS:
            stats = []
            for i in range(FIGHTS):
                player = loader.build_player(char, deck)
                state = run_fight(player, loader.build_encounter(enc),
                                  pilot, seed=SEED + i)
                stats.append(metrics.extract(state, player.max_hp))
            out[enc] = stats
        return out

    base = axes.raw_axes(battery("ref_ironclad", "starter", "generic"))
    print(f"  {'config':<28} {'aoe-term':>9} {'deb-term':>9} "
          f"{'app-term':>9} {'A6 v2':>7}")
    for deck, pilot_id in (("salon_weighted", "salon"),
                           ("spotlight_weighted", "spotlight"),
                           ("fanfare_weighted", "fanfare")):
        raw = axes.raw_axes(battery("furina", deck, pilot_id))
        aoe = raw["A6_aoe"] / max(1e-9, base["A6_aoe"])
        deb = raw["A6_debuff"] / max(1e-9, base["A6_debuff"])
        app = 1.0 + raw["A6_app"] - base["A6_app"]
        score = 3.0 * (0.5 * aoe + 0.3 * deb + 0.2 * app)
        print(f"  {deck:<28} {1.5 * aoe:>9.2f} {0.9 * deb:>9.2f} "
              f"{0.6 * app:>9.2f} {score:>7.2f}")
    print("  (terms are weight-scaled: they sum to the score; baseline "
          "deck sums to exactly 3.00)")


def cap() -> None:
    print()
    print("=" * 72)
    print("CAP. FANFARE_CAP re-check post-flip (W1 changed Encore flux; "
          "500 fights/cell)")
    print("=" * 72)
    default_cap = C.FANFARE_CAP_FRACTION
    pilot = make_pilot(loader.pilot_weights("fanfare"))
    package = loader.character_packages("furina")["fanfare_weighted"]
    for frac in (0.25, 0.5, 0.75):
        C.FANFARE_CAP_FRACTION = frac
        wr = {}
        for enc in ENCOUNTERS:
            wins = 0
            for i in range(500):
                player = loader.build_player_from_ids(
                    "furina", loader.starting_deck("furina") + list(package))
                state = run_fight(player, loader.build_encounter(enc),
                                  pilot, seed=SEED + i)
                wins += 1 if metrics.extract(state, player.max_hp).won else 0
            wr[enc] = wins / 500
        row = "  ".join(f"{e}: {wr[e]:.1%}" for e in ENCOUNTERS)
        mark = "  <- ratified" if frac == default_cap else ""
        print(f"    cap {frac:.2f}x maxHP   {row}{mark}")
    C.FANFARE_CAP_FRACTION = default_cap
    print("    ratified 0.5 stays unless punisher leaves [10%, 55%] "
          "(registered rule)")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "w0"
    if which == "w0":
        w0()
    elif which == "world":
        world()
    elif which in ("punisher4k", "floors4k"):
        floors4k()
    elif which == "a6":
        a6terms()
    elif which == "cap":
        cap()
