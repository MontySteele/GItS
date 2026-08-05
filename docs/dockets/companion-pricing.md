# Docket — companion pricing

**Status:** DOCKET. Candidates only. **Nothing in this file is ratified.**
Zero design authority. Opened 2026-08-06 (Track R) against the sitting of
2026-08-06 (`docs/sitting-record-predraft-2026-08-06.md`); ruling R111.

---

## 1. X10 — the Metallicize treadmill — **CANDIDATE, NOT RATIFIED**

**Verdict, verbatim:** *"10 of the same Companion at common seems exceptionally
unlikely. May be worth moving to Uncommon and adjusting power up."*

### Why this is a candidate and not a change

**"May be worth" is not a ratification**, and R111 declines to upgrade it into
one. The verdict does two separate things and only the first is settled:

1. **Settled:** the exploit line's reachability argument is rejected. Ten
   copies of one common companion is judged exceptionally unlikely in a real
   run, so the finding does not stand as a live degeneracy.
2. **Not settled:** whether `gorou_heart_of_the_clan` should move to
   **Uncommon** with a **power adjustment upward**. That is a pricing decision
   with a number in it, and it gets **priced at a sitting**.

### The candidate, stated once so the sitting has something to price

- Card: `gorou_heart_of_the_clan`.
- Proposed direction: Common → **Uncommon**, power adjusted **up** to match the
  new slot.
- Magnitude: **none proposed.** No number is written here, deliberately.
- Blocked on: a sitting. Nothing else.

**Mechanism, from `review/redteam/exploit-ledger.md` (X10):** turn-start
Metallicize is uncapped, never decays, and is granted *after* the block clear —
one common outruns every ramp in the roster. Pin:
`tier0/tests/test_s13_exploit_pins.py::test_x10_metallicize_treadmill_is_outpaced`,
which stays xfail(strict) because a candidate is not a fix.

---

## 2. Not in this docket, and it needs a home

**X2's mechanical audit (R109) has no docket assigned by the sitting.** The
cycling-rarity law — *"infinite cycling engines gated to Uncommon rarity or
higher. If this is Common, it needs a bump"* — comes with a rarity check owed
on `sayu_naptime` and on every self-replacing 0-cost non-exhaust companion, and
Common instances are to be **flagged for a bump**.

That is companion-rarity work and it is plausibly this docket's business, but
the routing was not given and Track R does not assign it. **Recorded here as
unrouted**, so it is visible rather than lost, and surfaced to the coordinator.
No findings are collected under it until someone routes it.
