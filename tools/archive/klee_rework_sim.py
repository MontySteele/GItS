"""Measure the 4 proposed dead-card reworks BEFORE proposing them for red-pen
(house rule: no unmeasured changes). Patches the live card index in-process,
then reports, for generic + reaction drafts: run winrate, and each reworked
card's offered/picked rate (did it come back from the dead?).

Proposed reworks (draft numbers, for ratification):
  alchemical_curiosity  C  draw 2                 -> dmg 4 + draw 1  (pyro cantrip)
  study_of_explosions   C  scry 2 + burst 5       -> dmg 4 rnd + burst 5 (free ping)
  surprise_visit        U  vuln 2                 -> block 4 + weak 1 ALL (mitigation)
  secret_stash          R  add 2 demo commons     -> dmg 8 ALL + add 2 (body + value)
"""
from __future__ import annotations
import sys
from collections import defaultdict
from tier0.content import loader
from tier05 import draft, model

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REWORKS = {
    "alchemical_curiosity": [
        {"op": "damage", "amount": 4, "target": "enemy"},
        {"op": "draw", "amount": 1}],
    "study_of_explosions": [
        {"op": "damage", "amount": 4, "target": "random_enemy"},
        {"op": "burst_energy", "amount": 5}],
    "surprise_visit": [
        {"op": "block", "amount": 4},
        {"op": "apply_power", "power": "weak", "amount": 1, "target": "all_enemies"}],
    "secret_stash": [
        {"op": "damage", "amount": 8, "target": "all_enemies"},
        {"op": "add_card", "pool": "demolition_commons", "amount": 2,
         "zone": "hand", "cost_override": 0}],
}
IDS = list(REWORKS)
ARCHES = ["generic", "reaction"]
RUNS = 150
SEED = 11


def measure():
    out = {}
    for arch in ARCHES:
        res = model.run_many("klee", arch, "generic", draft.POLICIES["assigned"],
                             RUNS, SEED, grant_relics=True, grant_potions=True,
                             n_acts=1)   # §10: Act-1 instrument, pinned
        won = sum(1 for r in res if r.won)
        off = defaultdict(int)
        pick = defaultdict(int)
        for r in res:
            for d in r.decisions:
                for c in d["offers"]:
                    off[c.id] += 1
                if d["picked"]:
                    pick[d["picked"]] += 1
        out[arch] = {"win": won / len(res),
                     "rates": {cid: (off[cid], pick[cid]) for cid in IDS}}
    return out


def show(label, data):
    print(f"\n=== {label} ===")
    for arch in ARCHES:
        d = data[arch]
        print(f"  {arch:<10} winrate {d['win']:.0%}")
        for cid in IDS:
            o, p = d["rates"][cid]
            r = f"{p/o:.0%}" if o else "  -"
            print(f"      {cid:<22} offered {o:>4}  picked {p:>3}  ({r})")


if __name__ == "__main__":
    base = measure()
    # apply reworks to the cached index (get_card deepcopies from it)
    idx = loader._card_index()
    for cid, fx in REWORKS.items():
        idx[cid].effects = [dict(e) for e in fx]
    after = measure()

    show("BASELINE (current cards)", base)
    show("AFTER REWORKS", after)

    print("\n--- winrate delta ---")
    for arch in ARCHES:
        b, a = base[arch]["win"], after[arch]["win"]
        print(f"  {arch:<10} {b:.0%} -> {a:.0%}  ({a-b:+.0%})")
