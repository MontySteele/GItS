"""Is the PILOT losing these runs, or the world?

`pilot_regret` (spec §6) only catches a strictly-dominated SINGLE play, so it
cannot answer the question it keeps getting asked. This audits the decision
that actually kills runs: ending a player turn with damage incoming that
block still sitting in hand would have absorbed.

Per ended player turn it records the uncovered incoming damage, the best
PLAYABLE block still in hand, and the leftover energy, then rolls those up
against the HP the run layer actually lost. A near-zero missed-block figure
means tactical play is not the leak and the difficulty question is about the
world (rosters, pool depth, run structure) instead.

    python -m tools.pilot_error_audit --character ref_ironclad --runs 300

Note it wraps `pilot.policy.make_pilot`, so it runs SERIALLY (the wrap has to
be in the process doing the fighting); keep --runs modest.
"""

from __future__ import annotations

import argparse
import collections
import warnings

from tier0 import constants as C
from tier0.engine.combat import card_playable
from tier0.pilot import policy
from tier05 import draft, model

AUDIT: collections.Counter = collections.Counter()

_real_make_pilot = policy.make_pilot


def _audit_turn_end(state) -> None:
    p = state.player
    shortfall = max(0.0, policy._incoming_damage(state) - p.block)
    AUDIT["turns"] += 1
    AUDIT["spare_energy"] += p.energy
    if shortfall <= 0:
        return
    AUDIT["turns_taking_damage"] += 1
    # `card_playable` already accounts for the energy actually left, so any
    # hit here is block the pilot could have had for free and did not take.
    best = max((policy._raw_block(state, c) for c in p.hand
                if card_playable(state, c)), default=0.0)
    if best > 0:
        AUDIT["turns_with_missed_block"] += 1
        AUDIT["missed_block"] += min(shortfall, best)


def _wrapped_make_pilot(weights):
    inner = _real_make_pilot(weights)

    def pilot(state):
        card = inner(state)
        if card is None:                 # the pilot has ended its turn
            _audit_turn_end(state)
        return card

    return pilot


def audit(character: str, archetype: str, pilot_id: str, runs: int, seed: int,
          realistic: bool = True, n_acts: int | None = None) -> None:
    policy.make_pilot = _wrapped_make_pilot
    model.make_pilot = _wrapped_make_pilot
    try:
        res = model.run_many(character, archetype, pilot_id,
                             draft.POLICIES["assigned"], runs, seed,
                             grant_relics=realistic, grant_potions=realistic,
                             n_acts=n_acts)
    finally:
        policy.make_pilot = _real_make_pilot
        model.make_pilot = _real_make_pilot

    turns = max(1, AUDIT["turns"])
    hp_lost = sum(max(0, f.hp_start - f.hp_end)
                  for r in res for f in r.fight_stats)
    plays = sum(f.cards_played for r in res for f in r.fight_stats)
    regrets = sum(f.regrets for r in res for f in r.fight_stats)

    print(f"=== pilot audit: {character}/{archetype}, {runs} runs, seed {seed}"
          f"{' (realistic)' if realistic else ' (bare)'} ===")
    print(f"  winrate                  {sum(r.won for r in res) / runs:.1%}")
    print(f"  player turns             {AUDIT['turns']}")
    print(f"  turns taking damage      {AUDIT['turns_taking_damage']} "
          f"({AUDIT['turns_taking_damage'] / turns:.1%})")
    print(f"  ...ending with PLAYABLE  {AUDIT['turns_with_missed_block']} "
          f"({AUDIT['turns_with_missed_block'] / turns:.1%} of turns)")
    print(f"     block still in hand")
    print(f"  HP lost across the runs  {hp_lost}")
    print(f"  HP that block would      {AUDIT['missed_block']:.0f} "
          f"({AUDIT['missed_block'] / max(1, hp_lost):.1%} of it)")
    print(f"     have saved")
    print(f"  spare energy at turn end {AUDIT['spare_energy'] / turns:.2f}"
          f"/turn")
    print(f"  spec pilot_regret        {regrets}/{plays} plays "
          f"({regrets / max(1, plays):.1%}) -- weak instrument, see docstring")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--character", default="ref_ironclad")
    ap.add_argument("--archetype", default=None)
    ap.add_argument("--runs", type=int, default=300)
    ap.add_argument("--seed", type=int, default=C.DEFAULT_SEED)
    ap.add_argument("--acts", type=int, default=None)
    ap.add_argument("--bare", action="store_true",
                    help="drop relics + potions (the historical bare world)")
    args = ap.parse_args(argv)
    from tier05.runner import resolve_plan
    archetype, pilot_id = resolve_plan(args.character, args.archetype)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        audit(args.character, archetype, pilot_id, args.runs, args.seed,
              realistic=not args.bare, n_acts=args.acts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
