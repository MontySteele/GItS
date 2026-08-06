# Roster anchors, v14 recipe under CONSTANTS 6 — THE quotable standing table (R118 / 10.2)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> # QUARANTINE BANNER — the core-attainment columns are quarantined pending
> # re-registration (queue row 10.7 / Q18, [USER] 2026-08-06)
>
> **Carried forward 2026-08-06 (Track M, wave 8) from
> `docs/roster-anchor-v14-2026-08-05.md`'s banner, which governs this table
> equally.** [USER] approved both halves of queue row 10.7 (2026-08-06;
> verbatim words in this file's git history) — the **`RA-G1`/`RA-G2`
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
>
> ---
>
> ### ADDENDUM, 2026-08-06 — the `tto` column JOINS this quarantine (`Q18` / R121)
>
> **Same banner, extended; not a second banner.** [USER] countersigned `Q18`
> and quarantined `tto` (2026-08-06, dispatch (e),
> `docs/dispatch-2026-08-06e-six-replies.md`). The rider the banner above left open —
> *"whether it joins the quarantine is [USER]'s to say at `Q18`"* — is
> answered **YES**.
>
> **What changes:** the **`tto`** column moves from *flagged* to
> **QUARANTINED**, on exactly the terms stated above — numbers stand as
> published, nothing rewritten; not quotable, not gradable, not readable as
> input to any decision. **What does not change:** everything else. The
> `core attain` / `core 95%` columns were already quarantined and stay so;
> win, act-1, acts, deck and fights remain untouched by this banner.
>
> **When it lifts:** `Q18` countersigned the re-registration
> (`docs/payoff-reach-reregistration-draft-2026-08-06.md`) together with a
> **fixed six-step execution order in which no step reorders**. The lift is
> **step (6)** — *"the quarantine — now including tto — lifts on the graded
> read"* — after the sprint runs under DRAFTER 14 (step 3) and is graded
> blind-first (step 4). Nothing lifts earlier, and the lift is a paper act at
> the queue row, not here. Ruling: `tier0/DECISIONS.md` **R121**.

**Designation (R118, queue row 10.2, [USER] approved together with its
rider):** the roster-anchor v14 n=3000 table **as re-produced under v6** is
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
| ref_ironclad§ | generic | 14 | 20260729 | 3000 | **13.83%** | [12.6, 15.1] | **72.47%** | [70.8, 74.0] | 26.10% | [24.6, 27.7] | 9.74 | 1.26 | 23.8 | 15.9 |
| real_ironclad | generic | 14 | 20260729 | 3000 | **8.53%** | [7.6, 9.6] | **69.87%** | [68.2, 71.5] | 69.23% | [67.6, 70.9] | 8.33 | 1.06 | 22.1 | 14.2 |
| real_silent | generic | 14 | 20260729 | 3000 | **1.70%** | [1.3, 2.2] | **60.90%** | [59.1, 62.6] | 62.47% | [60.7, 64.2] | 7.37 | 0.75 | 21.5 | 11.6 |

† QUARANTINED — see the banner. ‡ ~~flagged-not-quarantined per the Q18
rider~~ **QUARANTINED 2026-08-06 — the rider is answered YES
(`Q18` / R121); see the banner's addendum.** Legend struck, not rewritten
(R101b). § **The `ref_ironclad` row is the SHIELDED re-measurement, republished
2026-08-06 — see "Republication note" below. It is the ONLY row this document
has ever moved; the other eleven stand exactly as first published.**

~~Ordering facts a reader may take from the winrate column, both continuous
with the archived tables: `furina/salon` (11.20%) sits at the top —
`ref_ironclad/generic`, its archived co-leader, has moved (see the factual
note below and the sweep doc)~~ **Superseded 2026-08-06 by the republication
below; struck, not rewritten (R101b).** Ordering facts a reader may take from
the winrate column as it now stands: **`ref_ironclad/generic` (13.83%
[12.6, 15.1]) sits at the top, alone** — it clears `furina/salon` (11.20%
[10.1, 12.4]) with no interval overlap at this n (z = +3.08), where the
archived tables had the two as co-leaders. `kokomi/assist` (0.63%) sits at the
bottom, below the `real_silent` floor (1.70% [1.3, 2.2] vs 0.63% [0.4, 1.0] —
these intervals do NOT overlap at this n). `furina/fanfare` (2.23% [1.8, 2.8])
and `real_silent` still overlap.

## Factual note — `ref_ironclad` under the Track V archetype tags (the 10.2 rider)

Reported as fact; **interpretation stays quarantined with the columns.**
Under the rider's tags (`ref_ironclad`'s `archetype_package` now carries
`Card.archetypes`), the core-attainment column **can see the anchor** —
against a structural 0.00% / `tto = None` on all runs in every pre-tag table.
[USER]'s stated reason for the tags — the instrumentation could not read the
anchor at all without them — is confirmed by the reading itself, and **that
conclusion is untouched by the shield**: the instrument still reads the tags,
which is the whole of what the shield left alone.

**What the shield changed about this number, stated so the prose stays true
(2026-08-06, R121 `Q19`).** The figure this note originally quoted —
~~**60.73% [59.0, 62.5], tto 7.43**~~ — was the TAGGED-SCORER reading and is
preserved here struck rather than rewritten (R101b). The table's cell now
carries the shielded reading, **26.10% [24.6, 27.7], tto 9.74**. Nothing
about the instrument moved; the DECK it reads did. Core attainment is a
property of what the drafter assembled, so a scorer that no longer chases the
anchor's tagged cards attains the core less often and later. Both readings
remain **QUARANTINED** — the drop from 60.73% to 26.10% is a fact about two
drafters, not a finding anyone may grade until the banner lifts.

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

## Republication note, 2026-08-06 — the `ref_ironclad` row is now the SHIELDED reading (R121 `Q19`, option (a))

**Authority.** R121 `Q19`: [USER] directed the shield, plus a dated note
asking future sim work to diagnose why the winrate went down. The shield
landed
(`tier05/draft.py::_core_advance_view`: `score_offer`'s +3.0 core-advance
bonus is blind to the anchor arm's tags; `core_complete` and every other
reader still sees them), and the `ref_ironclad` arm **alone** was re-measured
under this document's own recipe — `n=3000`, `seed 20260729`,
`RT7/D14/P3/C6`, same per-arm harness body, checkpoint
`review/r121-shield/shielded-arm-9.json`.

**The tripwire fired, and [USER] released the republication anyway.** R121's
stated tripwire was that a shielded reading which does not restore the
archived ordering stops the track. It did not restore it — it **overshot**:
13.83% is **z = +3.16 above the archived 11.13%**, past the sweep's 12-arm
Bonferroni bar of 2.87. The track stopped and surfaced three options; [USER]
called option (a) defensible and released it (2026-08-06). Option (a)
was *land the shield as-is and republish with a dated note naming the
confound.* This is that note. The addendum on R121 records the discharge.

**All three readings of this arm, preserved together.** Nothing below is
rewritten; the row above is the only cell this table has moved.

| reading | scorer sees the tags? | constants | win | 95% | act-1 | core attain† | tto‡ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| archived, pre-rider (v5 half) | no tags existed | **C5** | 11.13% | — | 71.23% | 0.00% | None |
| tagged — this table as first published | yes | C6 | 7.50% | [6.6, 8.5] | 64.77% | 60.73% | 7.43 |
| **shielded — the row above** | **no (bonus only)** | **C6** | **13.83%** | **[12.6, 15.1]** | **72.47%** | **26.10%** | **9.74** |

**The confound, stated plainly, because it is why this row and not the
archived one is the baseline.** The archived 11.13% lives in a **different
constants world**: it is a CONSTANTS 5 measurement, and every shielded
reading is CONSTANTS 6. So "the tags moved the anchor" and "C5→C6 moved the
anchor" are **not separated** by the paired halves — the sweep's attribution
rested on the other eleven arms being statistically unmoved, which is
evidence about those arms and not about this one. **An untagged-under-C6
reading of this arm did not exist before this one.** A second,
diagnostic-only measurement that shields the WHOLE of `score_offer` — the
scorer seeing exactly the pre-rider cards — reads **13.20%** (z = +2.45 vs
11.13%; `review/r121-shield/probe-full-shield.json`, **not** committed
behaviour), so the residual is not a leftover tag-reading term in the scorer.

**Therefore: this row is the honest untagged-C6 baseline going forward.** The
archived 11.13% is quotable only as a C5 number and never as this row's
predecessor across the constants bump. `DRAFTER_VERSION` is **not** bumped by
the shield and the non-bump is flagged at the constant itself
(`tier0/constants.py`, above `DRAFTER_VERSION = 14`).

**The open question is `EB-46`**, in `docs/current/BACKLOG.md`:
separate the tag effect from the v6 effect on this arm. It is a diagnosis
question for future sim work — no deadline, no design authority, and nothing
in this table waits on it. † ‡ Both columns remain **QUARANTINED** under the
banner at the head of this document, in both their old and new readings.
