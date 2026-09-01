"""`KLEESPARK-R1` slots P5 and P6 — the Spark economy on a drafted-shape deck.

THE TWO SLOTS, verbatim from the countersigned slate at
`review/ruled/klee-sparks-2026-08-29.md` sec.10.9:

  P5  Does the pilot's SPEND RATE rise when the flag is on and the tight set
      is drafted?  Predicted YES.
  P6  Does the bank sit IDLE above the cheapest price for 3+ consecutive
      turns in a drafted deck?  Predicted NO.

Both are sim questions, and the sim can see them: they are counts of gains,
spends and turns in an event log. Neither is a balance claim, and under
R215 B no number a prototype row produces is quotable anywhere.
Guardrail-7 applies whole -- these are FLOORS and diagnostics.

WHY THE DECK IS ASSEMBLED BY ID RATHER THAN DRAFTED, and this is the
registered blind spot on both slots. `loader._pool_substitutions` returns `{}`
for Klee: the Kokomi arm has a pool seam and the Spark arm does not, so
`rewards.character_pool` can never offer a `proto_` Spark row and the tier 0.5
drafter structurally cannot draft one. A "drafted deck" therefore cannot be
produced by drafting. What is built instead is the deck PICK 4 describes as
the endpoint -- the substituted ten plus the tight set -- and the OFF arm is
the same ten plus the five SHIPPED rows PICK 4 converts, one for one, plus the
shipped Rare. That is the honest A/B the flag allows, and it is not a claim
about what a drafter would pick.

THE ONE-FOR-ONE MAP (the surface's own header):
    Fwoosh!          <- sparkly_treasure
    Bang Bang!       <- spark_collection
    Tinder Toss      <- pocket_fireworks
    Dodoco Blast     <- sugar_rush
    Firework Finale  <- cant_catch_me
    Spark Knight's Oath <- true_spark_knight

WHAT "IDLE" MEANS HERE, stated before the number is read. A turn is IDLE when
it ENDS with a bank at or above the cheapest Spark price the DECK prints and
no Spark was spent during it. Cheapest-in-DECK rather than cheapest-in-HAND is
a deliberate over-count: a deck price the hand does not hold still counts the
turn as idle, so the streak this reports is at least as long as the true one.
The error runs ONE WAY and it runs AGAINST P6's predicted NO, which is the
conservative direction for a slot predicting NO.

On the OFF arm no card prints a Spark price at all, so the cheapest price is
the retired base rule's own threshold (`C.SPARKS_FOR_FREE_ATTACK`): off the
flag, three Sparks is the only thing a bank can be "enough" for.

Usage: python -m tier05.exp_klee_sparks_r1 [--fights N] [--seed N]
"""

from __future__ import annotations

import sys

from tier0 import constants as C
from tier0.content import loader
from tier05 import expcli

# The tight set, as ids on `docs/prototype-surface.yaml`.
TIGHT_SET = [
    "proto_spark_strike",       # Fwoosh!,         price 1
    "proto_spark_double_tap",   # Bang Bang!,      price 2
    "proto_spark_sweep",        # Tinder Toss,     price 1
    "proto_spark_blast",        # Dodoco Blast,    price 2
    "proto_spark_finisher",     # Firework Finale, price 3
    "proto_true_spark_knight",  # Spark Knight's Oath, the strict Rare Power
]

# The shipped rows PICK 4 converts, in the same order, so the two arms differ
# in the ARM and not in how many cards were added.
SHIPPED_SET = [
    "sparkly_treasure",
    "spark_collection",
    "pocket_fireworks",
    "sugar_rush",
    "cant_catch_me",
    "true_spark_knight",
]

ENCOUNTER = "punisher"
PILOT = "demolition"


def _deck(flag_on: bool) -> list[str]:
    """The starter the flag produces, plus the arm's six added cards."""
    spec = loader._character_index()["klee"]
    return list(loader._starter_ids(spec)) + list(
        TIGHT_SET if flag_on else SHIPPED_SET)


def _cheapest_price(deck: list[str], flag_on: bool) -> int:
    """The smallest Spark price anything in this deck can be asked for."""
    from tier0.engine import combat
    if not flag_on:
        return C.SPARKS_FOR_FREE_ATTACK
    prices = [combat.spark_cost(loader.peek_card(cid)) for cid in deck]
    prices = [p for p in prices if p > 0]
    return min(prices) if prices else C.SPARKS_FOR_FREE_ATTACK


def _walk(log: list[dict], threshold: int, cheapest: int) -> dict:
    """Per-turn bank, gains, spends and the longest idle streak.

    The bank is reconstructed from the log rather than read off the final
    state, because what P6 asks about is the bank AT THE END OF EACH TURN and
    only the log carries that history. `gain_spark` and `spend_spark` both
    print a running `total`; the base rule's automatic consume
    (`sparks_spent`) prints none, so it is subtracted at the threshold, which
    is exactly what `combat.play_card` took.
    """
    bank = 0
    gained = spent = auto = refused = 0
    turns: list[tuple[int, bool]] = []      # (bank at turn end, spent here)
    turn = None
    spent_this_turn = False
    for row in log:
        t = row.get("turn")
        if turn is None:
            turn = t
        if t != turn:
            turns.append((bank, spent_this_turn))
            turn, spent_this_turn = t, False
        ev = row.get("event")
        if ev == "gain_spark":
            bank = row.get("total", bank + row.get("amount", 0))
            gained += row.get("amount", 0)
        elif ev == "spend_spark":
            bank = row.get("total", bank - row.get("amount", 0))
            spent += row.get("amount", 0)
            spent_this_turn = True
        elif ev == "sparks_spent":
            bank = max(0, bank - threshold)
            auto += threshold
            spent_this_turn = True
        elif ev == "spend_spark_refused":
            refused += 1
    if turn is not None:
        turns.append((bank, spent_this_turn))

    longest = run = 0
    for held, did_spend in turns:
        if held >= cheapest and not did_spend:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return {"turns": len(turns), "gained": gained, "spent": spent,
            "auto": auto, "refused": refused, "longest_idle": longest}


def _arm(flag_on: bool, fights: int, seed: int) -> dict:
    from tier0.engine.combat import run_fight
    from tier0.pilot.policy import make_pilot

    loader._card_prototype.cache_clear()
    original = C.SPARK_ALT_COST_ENABLED
    C.SPARK_ALT_COST_ENABLED = flag_on
    try:
        deck = _deck(flag_on)
        cheapest = _cheapest_price(deck, flag_on)
        pilot = make_pilot(loader.pilot_weights(PILOT))
        stages = loader.encounter_stages(ENCOUNTER)
        total = {"turns": 0, "gained": 0, "spent": 0, "auto": 0,
                 "refused": 0, "longest_idle": 0, "wins": 0}
        for i in range(fights):
            player = loader.build_player_from_ids("klee", list(deck))
            state = run_fight(player, loader.build_encounter(stages[0]),
                              pilot, seed=seed + i)
            walked = _walk(state.log, C.SPARKS_FOR_FREE_ATTACK, cheapest)
            for k in ("turns", "gained", "spent", "auto", "refused"):
                total[k] += walked[k]
            total["longest_idle"] = max(total["longest_idle"],
                                        walked["longest_idle"])
            total["wins"] += int(all(not e.alive for e in state.enemies))
        total["cheapest_price"] = cheapest
        return total
    finally:
        C.SPARK_ALT_COST_ENABLED = original
        loader._card_prototype.cache_clear()


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fights", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args(argv)

    print("KLEESPARK-R1 slots P5/P6 — Spark economy, tight set vs shipped")
    print(f"  encounter {ENCOUNTER}, pilot {PILOT}, "
          f"{args.fights} fight(s) per arm from seed {args.seed}")
    print("  NOT A BALANCE READ (R215 B). Counts only; Guardrail-7 applies.")
    print()

    rows = {}
    for label, flag in (("flag OFF (shipped rows)", False),
                        ("flag ON  (tight set)", True)):
        r = _arm(flag, args.fights, args.seed)
        rows[flag] = r
        per = (r["spent"] + r["auto"]) / r["turns"] if r["turns"] else 0.0
        gain = r["gained"] / r["turns"] if r["turns"] else 0.0
        print(f"{label}")
        print(f"    player turns        {r['turns']}")
        print(f"    Sparks gained       {r['gained']}  ({gain:.2f}/turn)")
        print(f"    Sparks spent        {r['spent']} priced "
              f"+ {r['auto']} auto-consumed  ({per:.2f}/turn)")
        print(f"    refused spends      {r['refused']}")
        print(f"    cheapest price      {r['cheapest_price']}")
        print(f"    longest idle streak {r['longest_idle']} turn(s)")
        print(f"    fights won          {r['wins']}/{args.fights}")
        print()

    off, on = rows[False], rows[True]
    off_rate = (off["spent"] + off["auto"]) / off["turns"] if off["turns"] else 0
    on_rate = (on["spent"] + on["auto"]) / on["turns"] if on["turns"] else 0
    print(f"P5  spend rate {off_rate:.2f}/turn OFF -> {on_rate:.2f}/turn ON: "
          f"{'ROSE' if on_rate > off_rate else 'DID NOT RISE'}")
    print(f"P6  longest idle streak ON = {on['longest_idle']} turn(s): "
          f"{'3 OR MORE' if on['longest_idle'] >= 3 else 'UNDER 3'}")
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    sys.exit(main())
