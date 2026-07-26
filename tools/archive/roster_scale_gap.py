"""Are the tier 0.5 act rosters on the same scale as the cards fighting them?

The tier 0 battery is BEHAVIOURALLY calibrated -- PUNISHER (115 HP / atk 9
ramp +2) is frozen at "starter REF_IRONCLAD wins ~50-60%", TANK BOSS at
"starter loses, package decks win 78-93%". The tier 0.5 act rosters were then
swapped to raw StS2 statlines with PROGRESSION_GAP_COMPENSATOR deliberately
not carried over (acts.py header, §4). Nothing checks that the two worlds
still describe the same power level.

This runs the SAME deck against both and prints the winrates side by side, at
FULL HP with no run-layer power, so attrition and draft luck are out of the
picture and what is left is scale. A deck that clears the battery and reads
0% against a whole act is a calibration finding, not a difficulty one.

    python -m tools.roster_scale_gap --fights 300

Add --act N to restrict the roster half; --character/--deck to score someone
other than the Ironclad anchor.
"""

from __future__ import annotations

import argparse
import random
import warnings

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.pilot.policy import make_pilot
from tier05 import acts

BATTERY_ORDER = ("swarm", "attrition", "punisher", "burst_check", "tank_boss")


def _winrate(spawn, deck_ids, character, pilot, fights, rng) -> float:
    wins = turns = hp_left = 0
    for _ in range(fights):
        player = loader.build_player_from_ids(character, list(deck_ids))
        state = run_fight(player, spawn(rng), pilot, seed=rng.randrange(2 ** 31))
        wins += bool(state.player.alive and not state.living_enemies)
        turns += state.turn
        hp_left += max(0, state.player.hp)
    return wins / fights, turns / fights, hp_left / fights


def _row(label, spawn, deck_ids, character, pilot, fights, seed):
    wr, turns, hp = _winrate(spawn, deck_ids, character, pilot, fights,
                             random.Random(seed))
    flag = "   <-- unwinnable" if wr == 0.0 else ""
    print(f"  {label:<36} win {wr:6.1%}   turns {turns:5.1f}   "
          f"HP left {hp:5.1f}{flag}")
    return wr


def compare(character: str, deck_name: str, pilot_id: str, fights: int,
            seed: int, only_act: int | None = None) -> None:
    deck = loader.starting_deck(character)
    if deck_name != "starter":
        deck = deck + loader.character_packages(character)[deck_name]
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    print(f"\n=== {character}/{deck_name} ({len(deck)} cards), "
          f"{fights} fights/encounter, full HP, no relics or potions ===")

    print("  -- tier 0 frozen battery (what the cards were calibrated on) --")
    for enc in BATTERY_ORDER:
        _row(enc, lambda r, e=enc: loader.build_encounter(e), deck, character,
             pilot, fights, seed)

    for act in range(acts.n_acts()):
        if only_act is not None and act != only_act - 1:
            continue
        print(f"  -- tier 0.5 act {act + 1} roster "
              f"(raw StS2, no compensator) --")
        pools = acts.pools(act)
        specs = ([("easy", s) for s in pools["easy"]]
                 + [("hard", s) for s in pools["hard"]]
                 + [("elite", s) for s in pools["elite"]]
                 + [("boss", s) for s in acts.boss_pool(act)])
        for tier, spec in specs:
            _row(f"{tier}: {spec['id']}",
                 lambda r, s=spec: acts.spawn(s, r), deck, character, pilot,
                 fights, seed)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--character", default="ref_ironclad")
    ap.add_argument("--deck", default=None,
                    help="package name; default = starter AND every package")
    ap.add_argument("--pilot", default="generic")
    ap.add_argument("--fights", type=int, default=300)
    ap.add_argument("--seed", type=int, default=C.DEFAULT_SEED)
    ap.add_argument("--act", type=int, default=None,
                    help="only this act's roster (1-based)")
    args = ap.parse_args(argv)
    decks = ([args.deck] if args.deck
             else ["starter"] + list(loader.character_packages(args.character)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for deck in decks:
            compare(args.character, deck, args.pilot, args.fights, args.seed,
                    args.act)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
