# Furina co-op check, 2026-10-15/16

**Why.** The overnight queue [USER] approved on 2026-10-15 ("you're good to
queue all of these"): a Furina pair against a base pair on shared seeds, the
co-op half of a kit's check (memory: kits are judged solo against the base
five, co-op by a paired round). A co-op run is not a run of record
(`docs/current/operations/understudy-seats.md`), so this is a check, not a
grade.

**Setup.** Build 0.2.5630 (main), A0, Sonnet 5.5 seats, one per player,
`embark --coop`. Furina + Klee (Hydro with Pyro, so Vaporize) against
Ironclad + Silent, on the first three base-five baseline seeds.

| Seed | Furina + Klee | Ironclad + Silent |
|---|---|---|
| 30KMHAVG9SMQ | lost, floor 45, Aeonglass (act 3 boss) at 547/1331 | lost, floor 45, Aeonglass at 648/1331 (a first attempt ended when the host game crashed on floor 26) |
| CYHZM9S0VPW6 | lost, floor 23, three Decimillipedes (act 2 elite) | lost, floor 16, The Kin (act 1 boss) |
| DJCAV76ZKAUN | cut on floor 17: the host froze in the act 1 boss fight after 7 wins | not run |

**Read.** On the two seeds both pairs finished, the Furina pair went as far
or further (45 and 45; 23 and 16). Two seeds are too few to say more than
that she is not a weak partner. The best turns in both of her seats were
Vaporize: Klee's Pyro aura, then Furina's banked Fanfare spent as Hydro.

**What the seats hit** (records: scratch `seats/archive/coop-s1-*`,
`coop-s2-*`, `coop-s3-*`, `coop-s1r-*`):
- A partner's kill mid-turn voids the other seat's queued play ("Skipped",
  "not found among alive enemies"); all four pairs of seats hit it.
- The page names a partner's HP cost "Test Host (you) ... your own HP cost".
- Aeonglass's Withers ended both seed-1 runs. One seat reported their damage
  ignores Block; the decompile says it does not (`Wither.cs`: `Unpowered |
  Move`, no `Unblockable`), and its own last turn adds up (two Wither+3, 24
  damage, against 17 Block and 2 HP).
- Harness: two Silent seats looped `proceed` past the act 2 Ancient and hit
  the refusal stop; a fresh seat inherits the stop until the coordinator
  clears it. One host crashed (log ends mid-turn, no error) and one froze
  (bridge timeouts, no managed main thread: the `EB-489` shape).

Raw transcripts: `review/qa/blindplay/` (local, gitignored).
