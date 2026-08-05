"""SLICE 11 fixture: two follow-ups on the v14 generic limb.

(1) PROTOTYPE STABILITY. `core_complete` is fed `loader.peek_card` results in
    model.py -- SHARED prototypes, not copies. Every limb reads mutable Card
    fields (`effects`, `archetypes`, `role`). If a run mutated a prototype,
    every later `core_complete` would answer differently with no error. This
    snapshots the limb inputs, runs runs, and re-reads them.

(2) THE 'generic' ANCHOR. `core_complete(deck, "generic")` is what gates
    `plan_live` on the generic anchor arms. This reports the final-deck
    on-plan / payoff counts so the online rate can be read as a distribution
    rather than a single pass/fail.

Run: PYTHONPATH=. python review/redteam/fixtures/track_o/s11_generic_anchor_probe.py
"""
from __future__ import annotations

from collections import Counter

from tier0.content import loader
from tier05 import draft, model

WATCH = ["kaboom", "grand_salon", "rapturous_applause", "the_sea_is_my_stage",
         "crescendo", "remote_detonator", "salon_debut", "limelight"]


def snapshot():
    out = {}
    for cid in WATCH:
        c = loader.peek_card(cid)
        out[cid] = (tuple(c.archetypes), c.role, c.rarity,
                    draft._fanfare_generation(c), draft._grants_fanfare_floor(c),
                    draft._reads_fanfare(c), repr(c.effects))
    return out


def main():
    before = snapshot()
    for seed in range(12):
        model.run_one("furina", "fanfare", "fanfare",
                      draft.assigned_policy, seed)
        model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy, seed)
    after = snapshot()
    drift = [cid for cid in WATCH if before[cid] != after[cid]]
    print("prototype drift after 24 runs:", drift or "NONE")

    for ch in ("klee", "furina", "kokomi"):
        dist = Counter()
        for seed in range(40):
            res = model.run_one(ch, "generic", "generic",
                                draft.assigned_policy, seed)
            deck = [loader.peek_card(cid) for cid in res.deck_ids]
            dist[draft._generic_core_counts(deck, "generic")] += 1
        online = sum(v for k, v in dist.items() if k[0] >= 4 and k[1] >= 1)
        print(f"{ch:7s}/generic final (on_plan,payoffs) dist="
              f"{dict(sorted(dist.items()))} online={online}/40")


if __name__ == "__main__":
    main()
