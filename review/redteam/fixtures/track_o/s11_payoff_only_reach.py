"""SLICE 11 fixture: is a ZERO-ENABLER core reachable by the real drafter?

v14 closed "DRAFT_CORE_SIZE on-plan cards, none of which is a payoff". The
mirror case -- DRAFT_CORE_SIZE on-plan cards, none of which is an ENABLER --
is still ONLINE, because a payoff counts toward both limbs of
`_generic_core_counts`. This measures how often the assigned drafter
actually lands there, per generic-limb archetype.

Run: PYTHONPATH=. python review/redteam/fixtures/track_o/s11_payoff_only_reach.py [N]
"""
from __future__ import annotations

import sys
from collections import Counter

from tier0.content import loader
from tier05 import draft, model

ARMS = [
    ("klee", "demolition"), ("klee", "spark"),
    ("furina", "salon"),
    ("kokomi", "priest"), ("kokomi", "commander"), ("kokomi", "assist"),
    ("furina", "generic"), ("klee", "generic"), ("kokomi", "generic"),
]


def measure(character, archetype, n):
    tally = Counter()
    for seed in range(n):
        res = model.run_one(character, archetype, archetype,
                            draft.assigned_policy, seed)
        deck = [loader.peek_card(cid) for cid in res.deck_ids]
        on_plan, payoffs = draft._generic_core_counts(deck, archetype)
        enablers = on_plan - payoffs
        complete = draft.core_complete(deck, archetype)
        tally["runs"] += 1
        if complete:
            tally["online"] += 1
            if enablers == 0:
                tally["online_zero_enabler"] += 1
    return tally


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"n={n} runs/arm, assigned policy, DRAFTER_VERSION 14")
    for ch, ar in ARMS:
        t = measure(ch, ar, n)
        online = t["online"]
        zero = t["online_zero_enabler"]
        pct = (100.0 * zero / online) if online else float("nan")
        print(f"{ch:7s}/{ar:11s} online={online:4d}/{t['runs']:4d} "
              f"zero-enabler-online={zero:4d} ({pct:5.1f}% of online decks)")


if __name__ == "__main__":
    main()
