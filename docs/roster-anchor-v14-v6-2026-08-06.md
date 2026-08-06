# Roster anchors, v14 recipe under CONSTANTS 6 — THE quotable standing table (R118 / 10.2)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> # QUARANTINE BANNER — the core-attainment columns are quarantined pending
> # re-registration (queue row 10.7 / Q18, [USER] 2026-08-06)
>
> **Carried forward 2026-08-06 (Track M, wave 8) from
> `docs/roster-anchor-v14-2026-08-05.md`'s banner, which governs this table
> equally.** [USER], verbatim (2026-08-06, queue row 10.7): *"Let's yes to
> both and see if it turns up on local."* — the **`RA-G1`/`RA-G2`
> core-attainment columns are QUARANTINED** until the payoff-reach/
> `RARITY_ODDS` registration is re-established.
>
> **What is quarantined here:** the **`core attain`** column and its printed
> interval (**`core 95%`**). These cells sit in the measurement neighbourhood
> of "payoff reach" and the registration that fences that neighbourhood
> cannot be produced (the 10.7 search: COMPLETE, NOT FOUND; re-registration
> draft `docs/payoff-reach-reregistration-draft-2026-08-06.md` awaits the
> `Q18` countersign). **Flagged, not quarantined** (the authority names the
> core-attainment columns and nothing else, per the Q18 rider): the **`tto`**
> column — whether it joins the quarantine is [USER]'s to say at `Q18`.
>
> **What quarantine means:** the numbers stand exactly as published — nothing
> is rewritten (R101b). They are quarantined-pending-re-registration: not
> quotable, not gradable, and not readable as input to any decision until the
> fence is re-established. **Lifting this quarantine is a paper act recorded
> at the queue row, not here.** Every other column (win, act-1, acts, deck,
> fights) is untouched by this banner.

**Designation (R118, queue row 10.2, [USER] verbatim *"Yes, and rider
yes."*):** the roster-anchor v14 n=3000 table **as re-produced under v6** is
the quotable standing table — the designation names the recipe and its v6
re-run, not the archived v5 read. This document is that re-run. All numbers
below are **measured-under-v6 / DRAFTER 14**.

## Recipe

The n=3000 standing-table recipe of record
(`docs/sprint-kokomi-instrument-log-2026-07-29.md` Task 1 — the same twelve
arms, the same fresh seed chosen there so the larger n is an independent
confirmation rather than a superset of seed 11):

```
python -m tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729
```

run at main `745139b` (CONSTANTS 6), driven per-arm through
`cells.CANONICAL.but(name="roster-anchors", runs=3000, seed=20260729,
jobs=0).but(character=…, archetype=…)` with one JSON checkpoint per arm
(`review/v6-rebaseline/v6-arm-*.json`) so an interruption cannot lose the
batch. `--jobs` is result-invariant (`run_many` chunks by run index). The
`core attain` / `tto` columns are the same read the v14 doc added —
`RunResult.time_to_online`, set by `tier05/model.py` on the first reward
screen where `draft.core_complete` passes; `tto` is mean fights-elapsed over
attaining runs only. Harness body: `anchor_arm.py`, quoted in
`docs/v6-rebaseline-sweep-2026-08-06.md` §appendix (the v14 doc's
throwaway-harness precedent, this time with its body committed in the sweep
log).

**Recipe-literal note, recorded rather than smoothed over:** the designation
says "the v14 n=3000 table"; the archived v14 doc
(`docs/roster-anchor-v14-2026-08-05.md`) is itself n=1500/seed 11, and the
only n=3000 recipe on record is the D13 standing table's
(`--runs 3000 --jobs 0 --seed 20260729`). This re-run follows the n=3000
literal with the D13 recipe's seed, which is also what the wave-8 dispatch
ordered. The v14 n=1500/seed-11 surface is swept by the same battery's
paired halves (see the sweep doc).

**Per-arm stamp (R68), shared suffix:** `seed=20260729 runs=3000
RT7/D14/P3/C6` (full per-arm stamps in the checkpoints).

## RA-G1 (v6) — the quotable table

All rows: DRAFTER 14, `RT7/D14/P3/C6`, seed 20260729, n=3000, route hunter,
realistic loadout. Bracketed columns are 95% Wilson intervals
(`tier05.stats.wilson95`); two rows whose intervals overlap have NOT
separated at this n.

| character | plan | DRAFTER | seed | n | win | win 95% | act-1 | act-1 95% | core attain† | core 95%† | tto‡ | acts | deck | fights |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee | demolition | 14 | 20260729 | 3000 | **6.67%** | [5.8, 7.6] | **82.53%** | [81.1, 83.9] | 91.13% | [90.1, 92.1] | 5.21 | 1.14 | 25.1 | 15.1 |
| klee | spark | 14 | 20260729 | 3000 | **4.73%** | [4.0, 5.6] | **79.80%** | [78.3, 81.2] | 62.57% | [60.8, 64.3] | 8.81 | 1.04 | 24.4 | 14.4 |
| klee | reaction | 14 | 20260729 | 3000 | **7.37%** | [6.5, 8.4] | **85.60%** | [84.3, 86.8] | 85.80% | [84.5, 87.0] | 4.28 | 1.21 | 22.0 | 15.7 |
| furina | salon | 14 | 20260729 | 3000 | **11.20%** | [10.1, 12.4] | **60.60%** | [58.8, 62.3] | 63.97% | [62.2, 65.7] | 5.85 | 0.98 | 23.0 | 13.0 |
| furina | spotlight | 14 | 20260729 | 3000 | **2.23%** | [1.8, 2.8] | **59.57%** | [57.8, 61.3] | 82.57% | [81.2, 83.9] | 3.70 | 0.76 | 22.3 | 11.6 |
| furina | fanfare | 14 | 20260729 | 3000 | **2.23%** | [1.8, 2.8] | **58.17%** | [56.4, 59.9] | 43.50% | [41.7, 45.3] | 7.77 | 0.74 | 21.0 | 11.3 |
| kokomi | priest | 14 | 20260729 | 3000 | **2.47%** | [2.0, 3.1] | **42.83%** | [41.1, 44.6] | 48.33% | [46.5, 50.1] | 6.80 | 0.56 | 21.4 | 9.4 |
| kokomi | commander | 14 | 20260729 | 3000 | **3.00%** | [2.4, 3.7] | **51.33%** | [49.5, 53.1] | 28.23% | [26.7, 29.9] | 8.47 | 0.69 | 22.2 | 10.6 |
| kokomi | assist | 14 | 20260729 | 3000 | **0.63%** | [0.4, 1.0] | **35.30%** | [33.6, 37.0] | 9.17% | [8.2, 10.3] | 9.55 | 0.40 | 19.9 | 8.1 |
| ref_ironclad | generic | 14 | 20260729 | 3000 | **7.50%** | [6.6, 8.5] | **64.77%** | [63.0, 66.5] | 60.73% | [59.0, 62.5] | 7.43 | 0.98 | 22.9 | 13.7 |
| real_ironclad | generic | 14 | 20260729 | 3000 | **8.53%** | [7.6, 9.6] | **69.87%** | [68.2, 71.5] | 69.23% | [67.6, 70.9] | 8.33 | 1.06 | 22.1 | 14.2 |
| real_silent | generic | 14 | 20260729 | 3000 | **1.70%** | [1.3, 2.2] | **60.90%** | [59.1, 62.6] | 62.47% | [60.7, 64.2] | 7.37 | 0.75 | 21.5 | 11.6 |

† QUARANTINED — see the banner. ‡ flagged-not-quarantined per the Q18 rider.

Ordering facts a reader may take from the winrate column, both continuous
with the archived tables: `furina/salon` (11.20%) sits at the top —
`ref_ironclad/generic`, its archived co-leader, has moved (see the factual
note below and the sweep doc); `kokomi/assist` (0.63%) sits at the bottom,
below the `real_silent` floor (1.70% [1.3, 2.2] vs 0.63% [0.4, 1.0] — these
intervals do NOT overlap at this n). `furina/fanfare` (2.23% [1.8, 2.8])
and `real_silent` still overlap.

## Factual note — `ref_ironclad` under the Track V archetype tags (the 10.2 rider)

Reported as fact; **interpretation stays quarantined with the columns.**
Under the rider's tags (`ref_ironclad`'s `archetype_package` now carries
`Card.archetypes`), the core-attainment column **can see the anchor: 60.73%
[59.0, 62.5], tto 7.43** — against a structural 0.00% / `tto = None` on all
runs in every pre-tag table. [USER]'s stated reason for the tags — the
instrumentation could not read the anchor at all without them — is
confirmed by the reading itself.

**Second half of the fact, stated so nobody discovers it later:** the tags
are not instrumentation-only in effect. `draft.core_complete` gates
`plan_live` and `_core_progress` feeds `score_offer`'s +3.0 core-advance
bonus, so tagging the anchor's package changed how the anchor **drafts**:
in the paired v5↔v6 halves of this same battery (same seed, same n),
`ref_ironclad` moved **win 11.13% → 7.50% (z = −4.84)** and **act-1 71.23%
→ 64.77% (z = −5.37)** — the only arm in the sweep to clear the Bonferroni
bar, and the movement is attributable to the tags, not to Frozen-α or the
shop conditioning (every other arm is statistically unmoved; five are
bit-identical). Where that leaves the anchor's role is not this table's to
say; it is surfaced in the sweep doc and the hand-back.
