# Difficulty calibration — working notes

Phase after the relic/potion/ancient layer (`docs/relic-potion-layer-plan.md`).
The runs are now "realistic" (full player-side power budget), so per the
ratified order we calibrate difficulty against a character that carries a real
loadout, never against the bare 3.0 starter. This doc is the running log of
that phase: instruments built, signals found, decisions taken.

## Instrument: `tools/realistic_axis_scores.py`

The standing scorecard (`tier0/harness`) fingerprints a **bare deck on the
frozen battery** — no relics, no potions. That is the character's *identity*
anchor (REF_IRONCLAD starter = 3.0 on every axis), but it is not what a real
run feels like. This tool measures the 7 axes with the **full power budget on**,
against the same 3.0 baseline, two ways — they answer different questions, so
we always show both:

- **Surface 1 — RUN FIGHTS.** Pool the `FightStats` from the actual Act-1 run
  fights (relics + potions live, real roster, HP carrying, potions spent, Fairy
  one-shot). Purest "in a real run."
  - *Caveat (stated, not faked):* A4 sustain here counts only **in-combat**
    heals — Blood Vial (`combat_start_heal`), blood potion, Encore absorb.
    **Between-fight** heals live in the run economy and never emit a combat
    `heal` event, so they are invisible to this surface: **Burning Blood**
    (post-won-fight, the innate Ironclad relic — the big one), **campfire
    rests**, **Regal Pillow**, **Meal Ticket**, **Book of Five Rings**.
  - *Caveat:* the real roster has no attrition/swarm/tank_boss pools, so
    A2/A3/A6 fall back to the pooled sample and read noisier than on the
    battery.
- **Surface 2 — BATTERY, FULL LOADOUT.** Re-run the calibrated 5-encounter
  battery, but equip the player with a real run's drafted deck + that run's
  relics' combat effects + a representative potion belt (`node_kind=elite` so
  both defensive AND offensive potion policies are live). Keeps the curated
  pools intact, so the axes stay well-defined and directly comparable to 3.0 —
  with everything on.
  - *Approximations (stated):* relic max-HP pickups are not re-applied (battery
    uses base max HP); each independent battery fight starts with a **fresh**
    copy of the belt (it does not deplete across fights the way a run does), so
    A4's potion contribution is an upper edge.

Boundary intact: the frozen battery's own anchor path (`build_player`) is never
touched; this tool feeds relics/potions in through `build_player_from_ids` as a
**measurement**, exactly the seam the run layer uses. Anchor lock unaffected.

Re-runnable: `python -m tools.realistic_axis_scores --runs N --sample K --fights F`.

## First measurement (200 runs, seed 11, sample 20, fights 100)

7-axis scores, everything on. `starter` = bare-deck identity anchor.

**klee** (run win 11%)
| axis | starter | run-fights | batt+loadout med [p10–p90] |
|---|---|---|---|
| A1 Frontload | 4.1 | 4.3 | 6.0 [4.8–7.6] |
| A2 Scaling   | 3.0 | 4.6 | 3.0 [2.2–3.6] |
| A3 Block econ| 2.4 | 6.5 | 2.1 [1.3–4.4] |
| A4 Sustain   | 0.5 | 0.5 | 0.5 [0.5–0.7] |
| A5 Velocity  | 3.0 | 3.1 | 3.1 [3.0–3.2] |
| A6 Utility   | 3.2 | 3.5 | 4.2 [3.6–6.4] |
| A7 Setup tax | 3.3 | 3.8 | 3.4 [2.9–4.2] |

**real_ironclad** (win 40%)
| axis | starter | run-fights | batt+loadout |
|---|---|---|---|
| A1 | 3.0 | 3.7 | 5.0 [3.9–6.8] |
| A2 | 3.0 | 2.8 | 4.1 [3.0–5.0] |
| A3 | 3.0 | 6.3 | 2.4 [1.4–3.7] |
| A4 | 3.0 | 3.9 | 4.6 [4.6–4.8] |
| A5 | 3.0 | 3.1 | 3.2 |
| A6 | 3.0 | 3.2 | 4.4 [3.4–6.1] |
| A7 | 3.0 | 3.5 | 3.2 [2.2–4.8] |

**ref_ironclad** (win 16%): starter flat 3.0 → run-fights lifts A3 to 6.3, A7 to
4.1; batt+loadout pushes A1 5.1 / A4 4.6.

### Signals

1. **A3 splits hard by surface** (Klee 2.4 → **6.5** run-fights → 2.1 battery;
   both Ironclads → 6.3 run-fights). The real Act-1 roster hits much harder than
   the calibrated battery, so the same block absorbs far more damage per energy.
   Not the characters getting blocky — the **encounters are spikier than the
   battery they descended from**. This is the first concrete calibration lever:
   the run roster's damage profile has drifted above the battery's.
2. **A1 balloons under the full loadout** (all three → 5–6). Vajra/strength
   relics + fire potions + drafted payoffs all frontload; everything-on reads
   TOO_STRONG on A1 by construction.
3. **Klee A4 stays 0.5 on every surface.** Relics+potions took her 0→11% win,
   but her sustain axis never moves — her survival is between-fight (Fairy,
   reactive blood potions) and roster-dodging, not a healing statline. Identity
   hole intact; the run economy is what patches it. (See A4 caveat above:
   Klee has no Burning Blood, so even the invisible between-fight bucket is
   near-empty for her.)
4. **Full-loadout statlines trip TOO_STRONG / NO_WEAKNESS** across the board —
   expected. The 3.0 baseline is the right zero-point for *identity*; a loaded
   mid/late run naturally sits above it. Do NOT read these flags as balance
   breaks — they are the flags firing on a deliberately-above-baseline sample.

## Investigation: roster hardness, and the A3-throughput blind spot

Static enemy-hardness table (cycle-avg attack DPT / peak burst / HP), battery
vs Act-1 roster (`scratchpad/roster_hardness.py`):

- Act-1 **normals are SOFTER** in sustained DPT than battery normals (3.3–7.3 vs
  4–10). The difficulty is not in the normals.
- Act-1 **elites/boss are far spikier**: peak burst 23–28 (Bygone 23, Phantasmal
  28, Vantom Dismember 27) vs the battery's normal-fight peaks of 9–12. The
  battery has exactly one burst check (BURST CHECK, 24) and its A3 pool is the
  gentlest fight in the set (ATTRITION, 4 DPT sustained).
- **Boss-archetype mismatch:** the battery's `tank_boss` (A2/curve anchor) is a
  240-HP / 6.7-DPT SPONGE that rewards scaling; Vantom is a 173-HP (−28%) /
  peak-27 BURST RACE won by frontload. This is why run-fights A2 sags below
  starter for both Ironclads — the roster never gives scaling a long fight.

So the run-fights A3 = 6.3–6.5 was largely an **instrument-pool artifact**: the
battery anchors A3 on a 4-DPT grinder, the run pools everything incl. 15–23-DPT
elites, so block soaks more per energy. Surface-2 A3 ≈ 2.1 (measured on the real
attrition pool) is the true block identity.

### THE headline finding: A3 measures throughput, the roster kills by burst

Burst-defense probe (`tools/burst_defense.py`, 480 fights/char, full loadout,
spike turn = incoming ≥ 20). Block ceiling = max wall raised in one turn:

| char | block ceiling p50/p90 | wall coverage on spike | HP eaten/spike med·p90 | spike intact |
|---|---|---|---|---|
| ref_ironclad  | 11 / 21 | 39% | 15 · 23 | 4% |
| real_ironclad | 10 / 17 | 31% | 17 · 24 | 1% |
| klee          | 10 / 16 | 39% | 15 · 23 | 0% |

Spikes are 23–28. **No character can raise a 25 wall** (best ceiling p90 = 21);
all eat ~15–17/spike and survive one intact ~never. A3's throughput average —
anchored on the ATTRITION grinder — reports all three as competent blockers
while none can answer the roster's real question ("wall 27 now"). **A3 is
measuring the wrong quantity for the whole cast** (user's insight, 2026-07-21:
"a lot easier to put up 5 block per turn than 25 block in a specific turn").

**The A3 × A4 interaction the sim cannot see.** Klee's block ceiling (10/16) is
barely below the Ironclads' — block ceiling is not where she is uniquely doomed.
What makes the same ~15/spike LETHAL for her and survivable for them is A4:
across a run's ~6 spike fights that is ~90 HP torn off; the Ironclads heal it
back (Burning Blood + rests + bigger bar), Klee (A4=0.5, no innate heal) does
not — it is permanent and cumulative. The sim scores "block: okay-ish
(throughput)" and "sustain: low-but-bounded (0.5 floor)" as two INDEPENDENT
mediocre axes; on a burst roster they MULTIPLY into a death spiral neither axis
flags alone. This is why potions (which add BOTH burst block AND Fairy/heal)
moved Klee 0→11% while her axis fingerprint never moved.

### Next (calibration levers, from the above)

1. The 7 axes were calibrated on the battery's profile (sustained grind +
   scaling); the Act-1 roster tests a DIFFERENT profile (burst survival +
   frontload). Before tuning numbers, decide what the roster should test.
2. A3 needs a burst/on-demand companion signal (the `burst_defense` probe is a
   candidate), and the battery's attrition-only A3 anchor should get a
   burst-check counterpart — else the sim keeps over-crediting thin-wall decks.
3. Weigh whether the axis model should represent A3×A4 as an interaction (a
   "spike survivability" derived metric) rather than two independent axes,
   since that interaction is where fragile-no-heal identities actually die.
   NOTE: axis-model changes touch the frozen normalization — user red-pen.
