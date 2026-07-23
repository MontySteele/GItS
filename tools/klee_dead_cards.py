"""Bucket 3 (the real fix): which of Klee's cards does the bot NEVER draft?

For each of the 4 draft contexts the sim can run (generic goodstuff + the 3
committed archetypes), play many runs and tally, per card, how often it was
OFFERED on a reward screen vs how often it was PICKED. A card offered a lot
and picked ~never is dead deck space.

Classification:
  DEAD      -- offered >= MIN and picked <5% in EVERY context incl. its own
               archetype. Genuinely useless; a redesign candidate.
  LOCKED    -- dead in generic but alive (>=20%) in its own archetype. Working
               as designed: a synergy card that needs its plan.
  (blank)   -- picked reasonably somewhere; fine.

CAVEAT, load-bearing: DRAFTER_VERSION 3 gives conservative value to enemy
Weak/Vulnerable, Bombs, and safe conditional Block. Draw, energy, and resource
engines still read as zero printed power because a measured flat proxy made
both reference characters draft worse decks; those effects need deck context.
That is why we also run each card's OWN archetype: a card dead in generic but
taken in its archetype is locked, not dead. Truly-dead = dead even where it
belongs.
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

ARCHES = ["generic", "demolition", "spark", "reaction"]
RUNS = 120
SEED = 11
MIN_OFFERED = 8      # need enough looks to trust a 0% pick
LOW = 0.05
ALIVE = 0.20


def tally(arch):
    res = model.run_many("klee", arch, "generic", draft.POLICIES["assigned"],
                         RUNS, SEED, grant_relics=True, grant_potions=True)
    off = defaultdict(int)
    pick = defaultdict(int)
    for r in res:
        for d in r.decisions:
            for c in d["offers"]:
                off[c.id] += 1
            if d["picked"]:
                pick[d["picked"]] += 1
    return off, pick


def main():
    per = {a: tally(a) for a in ARCHES}
    # universe = every card offered anywhere
    ids = set()
    for a in ARCHES:
        ids |= set(per[a][0])

    def card(cid):
        try:
            return loader.get_card(cid)
        except Exception:
            return None

    rows = []
    for cid in ids:
        c = card(cid)
        if c is None:
            continue
        tot_off = sum(per[a][0].get(cid, 0) for a in ARCHES)
        tot_pick = sum(per[a][1].get(cid, 0) for a in ARCHES)
        gen_off, gen_pick = per["generic"][0].get(cid, 0), per["generic"][1].get(cid, 0)
        own = next((a for a in ("demolition", "spark", "reaction")
                    if a in c.archetypes), None)
        own_off = per[own][0].get(cid, 0) if own else 0
        own_pick = per[own][1].get(cid, 0) if own else 0
        rate = tot_pick / tot_off if tot_off else 0.0
        gen_rate = gen_pick / gen_off if gen_off else None
        own_rate = own_pick / own_off if own_off else None
        klee = getattr(c, "character", None) == "klee"
        # classify
        cls = ""
        if tot_off >= MIN_OFFERED and rate < LOW:
            if own_rate is not None and own_rate < LOW:
                cls = "DEAD"
            elif own_rate is None:                 # generic-only card
                cls = "DEAD"
        if not cls and gen_rate is not None and gen_rate < LOW and own_rate is not None and own_rate >= ALIVE:
            cls = "locked"
        rows.append({
            "id": cid, "klee": klee, "rar": c.rarity,
            "role": c.role, "arch": ",".join(c.archetypes),
            "pw": draft._static_power(c), "off": tot_off, "pick": tot_pick,
            "rate": rate, "gen_rate": gen_rate, "own": own,
            "own_rate": own_rate, "cls": cls})

    def fr(x):
        return "  -" if x is None else f"{x:>3.0%}"

    print(f"\n=== KLEE dead-card scan ({RUNS} runs x {len(ARCHES)} archetypes, "
          f"seed {SEED}) ===")
    print("DEAD = offered>=8 & picked<5% even in its own archetype.\n")

    dead = [r for r in rows if r["cls"] == "DEAD" and r["klee"]]
    dead.sort(key=lambda r: (-r["off"], r["id"]))
    print(f"--- DEAD (Klee-owned): {len(dead)} ---")
    print(f"  {'card':<22}{'rar':<9}{'role':<9}{'arch':<18}"
          f"{'pw':>4}{'off':>5}{'pk%':>5}{'gen':>5}{'own':>10}")
    for r in dead:
        print(f"  {r['id']:<22}{r['rar']:<9}{r['role']:<9}{r['arch']:<18}"
              f"{r['pw']:>4.1f}{r['off']:>5}{r['rate']:>5.0%}"
              f"{fr(r['gen_rate']):>5} {(r['own'] or '-'):>6}:{fr(r['own_rate'])}")

    locked = [r for r in rows if r["cls"] == "locked" and r["klee"]]
    locked.sort(key=lambda r: (-r["off"], r["id"]))
    print(f"\n--- LOCKED (dead in generic, alive in its archetype): {len(locked)} ---")
    for r in locked:
        print(f"  {r['id']:<22}{r['arch']:<18}gen {fr(r['gen_rate'])}  "
              f"{r['own']}:{fr(r['own_rate'])}")

    # also: the lowest overall pick-rate Klee cards regardless of class
    klee_rows = [r for r in rows if r["klee"] and r["off"] >= MIN_OFFERED]
    klee_rows.sort(key=lambda r: r["rate"])
    print(f"\n--- Klee cards by overall pick rate (bottom 15) ---")
    print(f"  {'card':<22}{'rar':<9}{'pw':>4}{'off':>5}{'pk%':>6}  gen / own")
    for r in klee_rows[:15]:
        print(f"  {r['id']:<22}{r['rar']:<9}{r['pw']:>4.1f}{r['off']:>5}"
              f"{r['rate']:>6.0%}  {fr(r['gen_rate'])} / {fr(r['own_rate'])}"
              f" ({r['own'] or 'generic'})")


if __name__ == "__main__":
    main()
