# Roster anchor table under DRAFTER_VERSION 14 — PROPOSED

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

> # ARCHIVE BANNER — every combat number here is pre-CONSTANTS-6
>
> **Appended 2026-08-06 (Track V, wave 8). `CONSTANTS_VERSION` 5 → 6 was
> approved by [USER] on 2026-08-06 (Q14 / R117, verbatim *"14) Yes"*), for
> the v6 batch "Frozen unified + α boss-room scope + shop-slot spec" as one
> batch boundary.** The Frozen rules changed twice inside it: Errata Batch 2
> (`db3318e` — Frozen is a duration counter, both engines) and the α
> boss-room scope (Q13 / R117, verbatim *"I'd say A"* — in a boss room only
> minion-flagged creatures freeze; every other creature takes Vulnerable).
> Frozen appears across the roster's fights, so **every tier-0 / tier-0.5
> combat number in this document measured before the batch is archive — for
> every character, not only the rows earlier banners covered — and is NOT
> comparable to output taken under 6.** Quote these numbers only with the
> pre-v6 label attached. Nothing above or below is rewritten (R101b); the v6
> re-baseline sweep is Track M's, after the v6 code lands. Source of the
> bump: `tier0/constants.py`, the `CONSTANTS_VERSION 6` note.

> # ARCHIVE BANNER — the Furina rows here are pre-CONSTANTS-5
>
> **Appended 2026-08-06 (Track W). Every Furina tier-0.5 number in this
> document was measured under `CONSTANTS_VERSION 4` or earlier and is NOT
> comparable to output taken under 5. Quote these rows only with that label
> attached.**
>
> `CONSTANTS_VERSION` 4 → 5 was **APPROVED by [USER] on 2026-08-06** (reply to
> the Second Wind open one-liner (3),
> `docs/surplus-week-manifest-2026-08-05.md`) for **R110's S-1 erratum, family
> X3**: `encore_performance` lost its `{op: energy}` refund and its printed
> cost moved 1 → 0. A Furina **rare** that changed cost and stopped returning
> energy re-prices the turns of every Furina deck that could ever be offered
> it — her energy curve, not one cell. Under the constant's own comparability
> criterion (stated at the v2 bump, restated at v4: *the size of the edit is
> not what decides, comparability is*) and on the **R87(3) precedent** that a
> stamp bump archives every number the stamp governs, **every Furina row here
> is archive — not a cheaper sample of the same world.**
>
> **Nothing above or below is rewritten** (R101b): the numbers stand exactly as
> published, with this note on top. **Non-Furina rows are untouched by the
> bump** — Klee, Kokomi, `ref_ironclad`, `real_ironclad` and `real_silent`
> draft no Furina card, and neither `DRAFTER_VERSION` nor `RUNTEMPLATE` moves
> (no offer-time price and no map shape changed). The **Furina re-baseline is
> a COMPUTE decision for the next measurement sprint**; nothing was
> re-measured for this banner and none is owed by it. Source of the bump:
> `tier0/constants.py`, the `CONSTANTS_VERSION 5` note.

> # QUARANTINE BANNER — the core-attainment columns are quarantined pending
> # re-registration (queue row 10.7, [USER] 2026-08-06)
>
> **Appended 2026-08-06 (Track S2, the 10.7 search).** [USER], verbatim
> (2026-08-06, queue row 10.7): *"Let's yes to both and see if it turns up on
> local."* — (b) the **`RA-G1`/`RA-G2` core-attainment columns are
> QUARANTINED** until the payoff-reach/`RARITY_ODDS` sprint's registration
> document is found or re-established.
>
> **What is quarantined:** in §2 (`RA-G1`), the **`core attain`** column and
> its printed interval (**`core 95%`**); in §3 (`RA-G2`), the
> **`core D13` / `core D14` / `Δ` / `z`** columns. These cells sit in the
> measurement neighbourhood of "payoff reach"
> (`docs/sitting-prep-2026-08-05.md` §10.7), and the registration that fences
> that neighbourhood cannot be produced. **Flagged, not quarantined by this
> banner** (the authority names the core-attainment columns and nothing else):
> the `tto` columns come from the same uncommitted throwaway harness
> (`RunResult.time_to_online`, §1) — whether they ride the quarantine is the
> coordinator's paper call, surfaced in the hunt report.
>
> **What quarantine means:** the numbers **stand exactly as published —
> nothing is rewritten** (R101b). They are quarantined-pending-re-registration:
> not quotable, not gradable, and not readable as input to any decision until
> the fence is re-established. The 2026-08-06 search (branch
> `findings/track-s2-registration-hunt`, report
> `docs/registration-hunt-report-2026-08-06.md`) did **NOT** find the
> registration; the clean re-registration draft is
> `docs/payoff-reach-reregistration-draft-2026-08-06.md`, awaiting [USER]
> countersign. Lifting this quarantine is a paper act recorded at the queue
> row, not here. Every other column of both tables (win, act-1, acts, deck,
> fights, decks-differ) is untouched by this banner.

**Status: PROPOSED. Filed as successor CANDIDATE to the archived standing
roster table.** Designation is [USER]'s (F4 pattern). Nothing in this document
is ratified, and nothing here is a design recommendation: Track G carried
**zero design authority**. Numbers only.

**Track:** G ("Last Call, Round Two" addendum). **Date:** 2026-08-05.
**Branch:** `findings/track-g` off `origin/main` = `8daedb7`.
**World:** `RT7 / D14 / P3 / C4`.

---

## 0. Why this table exists

E1 (`d294b51`, "Four enablers and no payoff was never an assembled deck",
landed on main in `b940190`) split the **generic limb** of
`tier05/draft.py::core_complete` into two limbs: `DRAFT_CORE_SIZE` on-plan
enabler-or-payoff cards **and at least one on-plan card whose role is
`payoff`** (`GENERIC_PAYOFF_COVERAGE = 1`). `_core_progress` took the matching
shape — `(assembly + payoff) / 2` instead of `assembly` alone.

That limb is live for every archetype **without** a dedicated branch, i.e. for
seven: `assist`, `commander`, `demolition`, `generic`, `priest`, `salon`,
`spark`. `reaction`, `spotlight` and `fanfare` each keep their own branch and
were untouched.

`core_complete` gates `tier05/model.py`'s `plan_live` flag (the plan-live
divergence check) and `_core_progress` feeds `score_offer`'s **+3.0
core-advance bonus**, so those seven arms draft differently under v14. By the
R87(3) precedent, **every drafter-layer number recorded for those seven arms
before this bump is archive.** This document is the re-measurement.

---

## 1. Methodology

- **Script:** the anchor set is the twelve arms declared in
  `tier05/exp_roster_anchors.py::ARMS` — the same twelve the sim-hygiene log
  (`docs/sprint-sim-hygiene-log-2026-07-29.md`) ran for its D12→D13 pair and
  the Kokomi-instrument log (`docs/sprint-kokomi-instrument-log-2026-07-29.md`)
  ran at n=3000.
- **Cell:** the standard gate cell — `cells.CANONICAL` (`--realistic`, i.e.
  relics + potions granted; pilot `assigned` policy; all registered acts) with
  `route=hunter`, `seed=11`, `runs=1500`.
- **Added column:** `core_complete` **attainment** — the fraction of runs whose
  drafted deck ever satisfied `draft.core_complete`, read off
  `RunResult.time_to_online`, which `model.py` sets on the first reward screen
  where the check passes. `tto` is the mean fights-elapsed at that moment,
  over attaining runs only. This is a **read** of the instrument E1 changed; it
  is not a claim about how many payoffs any archetype ought to hold.
- **Pairing:** the D13 half was produced by a second worktree detached at
  `d45510a` — the last pre-v14 point on main — running the identical harness
  at the identical seed. `run_many` seeds run *i* as `seed + i`, so run *i* in
  the two worlds is the same world with a different drafter; the pair is a
  comparison, not two measurements.
- **`jobs`:** `--jobs 8` in both halves. `run_many`'s docstring and
  `tier05/tests/test_runner.py` pin `jobs` as result-invariant (chunked by run
  index, one `Random` per run); the Kokomi-instrument sprint re-verified it
  empirically at `--jobs 0/8/1`.
- **`game_ref/`:** gitignored, so a fresh worktree cannot build `real_ironclad`
  or `real_silent` (it fails as `KeyError: 'real_ironclad'` inside a worker,
  surfacing as `BrokenProcessPool`). Both worktrees were given a **directory
  junction** to the primary checkout's `game_ref/`; use is read-only.
- Wilson intervals are `tier05.stats.wilson95`. `z` is a two-proportion test on
  the D13→D14 difference. With **36 comparisons** in §3 the Bonferroni bar is
  |z| ≥ 3.2; |z| ≥ 1.96 is nominal only.

### Exact repro

```
# v14 half (this branch, or any tree at DRAFTER_VERSION 14)
git -C <repo> checkout 8daedb7
python -m tier05.exp_roster_anchors --runs 1500 --seed 11 --route hunter --jobs 8

# D13 half
git worktree add --detach <wt-d13> d45510a
mklink /J <wt-d13>\game_ref <repo>\game_ref     # Windows; ln -s elsewhere
cd <wt-d13>; python -m tier05.exp_roster_anchors --runs 1500 --seed 11 --route hunter --jobs 8
```

`exp_roster_anchors` prints win / act-1 / acts / deck / fights with intervals.
The **core-attainment and deck-fingerprint columns below came from two
throwaway harnesses** driving the same `cells.CANONICAL.but(...)` arms and
reducing `RunResult.time_to_online` and `RunResult.deck_ids`; they add no
repo-visible behaviour and were not committed. Their bodies are quoted in the
Track G report.

---

## 2. G1 — the v14 roster anchor table

> **IDENTIFIER NOTE, 2026-08-06 (housekeeping sweep, Track X).** `G1`/`G2` in
> this document are **section labels of Last Call's Track G**: canonical
> qualified forms **`RA-G1`** and **`RA-G2`**. They are not gates and not S4's
> `S4-G1`/`S4-G2`. Resolver: `docs/registry/identifiers.md` §2.1; the
> designate-or-hold ask on this table is `docs/registry/user-queue.md` §5 row
> 10.2.

All rows: **DRAFTER_VERSION 14**, `RT7/D14/P3/C4`, `cell=roster-anchors`,
`seed=11`, `n=1500`, `route=hunter`, realistic loadout.

| character | plan | DRAFTER | seed | n | win | win 95% | act-1 | act-1 95% | core attain | core 95% | tto | acts | deck | fights |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee | demolition | 14 | 11 | 1500 | **7.47%** | [6.2, 8.9] | **83.47%** | [81.5, 85.3] | 92.07% | [90.6, 93.3] | 5.23 | 1.17 | 25.4 | 15.4 |
| klee | spark | 14 | 11 | 1500 | **5.73%** | [4.7, 7.0] | **79.07%** | [76.9, 81.0] | 63.80% | [61.3, 66.2] | 8.64 | 1.05 | 24.5 | 14.5 |
| klee | reaction | 14 | 11 | 1500 | **9.13%** | [7.8, 10.7] | **86.00%** | [84.2, 87.7] | 83.20% | [81.2, 85.0] | 4.27 | 1.26 | 22.1 | 16.0 |
| furina | salon | 14 | 11 | 1500 | **10.87%** | [9.4, 12.5] | **59.20%** | [56.7, 61.7] | 62.87% | [60.4, 65.3] | 5.87 | 0.95 | 22.7 | 12.7 |
| furina | spotlight | 14 | 11 | 1500 | **3.33%** | [2.5, 4.4] | **60.93%** | [58.4, 63.4] | 82.47% | [80.5, 84.3] | 3.83 | 0.80 | 22.5 | 11.8 |
| furina | fanfare | 14 | 11 | 1500 | **2.40%** | [1.7, 3.3] | **55.60%** | [53.1, 58.1] | 44.20% | [41.7, 46.7] | 7.86 | 0.72 | 20.6 | 11.0 |
| kokomi | priest | 14 | 11 | 1500 | **2.27%** | [1.6, 3.2] | **42.33%** | [39.9, 44.9] | 47.93% | [45.4, 50.5] | 7.00 | 0.56 | 21.4 | 9.5 |
| kokomi | commander | 14 | 11 | 1500 | **3.07%** | [2.3, 4.1] | **51.53%** | [49.0, 54.1] | 30.13% | [27.9, 32.5] | 8.49 | 0.70 | 22.3 | 10.7 |
| kokomi | assist | 14 | 11 | 1500 | **0.67%** | [0.4, 1.2] | **32.80%** | [30.5, 35.2] | 7.87% | [6.6, 9.3] | 9.47 | 0.37 | 19.8 | 7.9 |
| ref_ironclad | generic | 14 | 11 | 1500 | **10.73%** | [9.3, 12.4] | **68.33%** | [65.9, 70.6] | 0.00% | [0.0, 0.3] | — | 1.13 | 22.3 | 15.0 |
| real_ironclad | generic | 14 | 11 | 1500 | **8.47%** | [7.2, 10.0] | **69.13%** | [66.7, 71.4] | 68.33% | [65.9, 70.6] | 8.36 | 1.04 | 22.0 | 14.0 |
| real_silent | generic | 14 | 11 | 1500 | **1.60%** | [1.1, 2.4] | **61.47%** | [59.0, 63.9] | 63.13% | [60.7, 65.5] | 7.21 | 0.76 | 21.7 | 11.7 |

**Stamp:** `cell=roster-anchors[jobs=8,runs=1500] seed=11 runs=1500 RT7/D14/P3/C4`

Two ordering facts a reader should take from the winrate column, both of which
were also true of the archived D13 table and are therefore *not* v14 news:
`furina/salon` (10.87%) and `ref_ironclad/generic` (10.73%) sit at the top;
`kokomi/assist` (0.67%) sits at the bottom, an order of magnitude below the
`real_silent` floor (1.60%). The floor arm and `furina/fanfare` (2.40%
[1.7, 3.3] vs 1.60% [1.1, 2.4]) still have overlapping intervals at this n.

---

## 3. G2 — the paired D13 → D14 diff

Same seeds, same cell, both predicate versions. n=1500 per cell.
`decks differ` is the fraction of the 1500 seed-matched run pairs whose final
drafted deck (`RunResult.deck_ids`, order-sensitive) is not identical between
the two worlds — the direct, non-proxy answer to "did draft behaviour move".

| character | plan | limb | win D13 | win D14 | Δ | z | act-1 D13 | act-1 D14 | Δ | z | core D13 | core D14 | Δ | z | tto D13 | tto D14 | decks differ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee | demolition | generic | 7.20% | 7.47% | +0.27 | +0.28 | 82.80% | 83.47% | +0.67 | +0.49 | 95.87% | 92.07% | **−3.80** | **−4.37** | 3.72 | 5.23 | **11.67%** |
| klee | spark | generic | 5.53% | 5.73% | +0.20 | +0.24 | 79.07% | 79.07% | +0.00 | +0.00 | 65.67% | 63.80% | −1.87 | −1.07 | 8.37 | 8.64 | 4.33% |
| furina | salon | generic | 10.27% | 10.87% | +0.60 | +0.53 | 58.73% | 59.20% | +0.47 | +0.26 | 71.73% | 62.87% | **−8.87** | **−5.18** | 4.47 | 5.87 | 7.87% |
| kokomi | priest | generic | 2.33% | 2.27% | −0.07 | −0.12 | 42.53% | 42.33% | −0.20 | −0.11 | 48.07% | 47.93% | −0.13 | −0.07 | 7.00 | 7.00 | 2.53% |
| kokomi | commander | generic | 3.00% | 3.07% | +0.07 | +0.11 | 51.40% | 51.53% | +0.13 | +0.07 | 34.13% | 30.13% | −4.00 | −2.35 | 8.45 | 8.49 | 2.20% |
| kokomi | assist | generic | 0.60% | 0.67% | +0.07 | +0.23 | 33.00% | 32.80% | −0.20 | −0.12 | 9.60% | 7.87% | −1.73 | −1.68 | 9.72 | 9.47 | 2.53% |
| ref_ironclad | generic | generic | 10.73% | 10.73% | +0.00 | 0.00 | 68.33% | 68.33% | +0.00 | 0.00 | 0.00% | 0.00% | +0.00 | 0.00 | — | — | **0.00%** |
| real_ironclad | generic | generic | 8.13% | 8.47% | +0.33 | +0.33 | 69.40% | 69.13% | −0.27 | −0.16 | 72.47% | 68.33% | −4.13 | −2.48 | 6.23 | 8.36 | **12.47%** |
| real_silent | generic | generic | 1.67% | 1.60% | −0.07 | −0.14 | 61.87% | 61.47% | −0.40 | −0.23 | 63.47% | 63.13% | −0.33 | −0.19 | 6.70 | 7.21 | 8.60% |
| klee | reaction | *own* | 9.13% | 9.13% | +0.00 | 0.00 | 86.00% | 86.00% | +0.00 | 0.00 | 83.20% | 83.20% | +0.00 | 0.00 | 4.27 | 4.27 | — |
| furina | spotlight | *own* | 3.33% | 3.33% | +0.00 | 0.00 | 60.93% | 60.93% | +0.00 | 0.00 | 82.47% | 82.47% | +0.00 | 0.00 | 3.83 | 3.83 | — |
| furina | fanfare | *own* | 2.40% | 2.40% | +0.00 | 0.00 | 55.60% | 55.60% | +0.00 | 0.00 | 44.20% | 44.20% | +0.00 | 0.00 | 7.86 | 7.86 | — |

**Stamps:** D13 `cell=roster-anchors[jobs=8,runs=1500] seed=11 runs=1500
RT7/D13/P3/C4` · D14 `... RT7/D14/P3/C4`.

### 3.1 What separated

- **Nothing in the winrate column.** Largest |z| is 0.53 (`furina/salon`,
  +0.60). Nothing in the act-1 column either; largest |z| is 0.49. On this
  evidence **E1 did not move run outcome for any arm on the roster at n=1500**.
  This is the same shape the D12→D13 pair took at n=3000, and it is the reason
  the incomparability note is a *hygiene* rule rather than a *magnitude* claim:
  the archived numbers are archive because the instrument moved, not because
  the outcomes did.
- **The instrument moved, and it moved in one direction.** `core_complete`
  attainment fell on **every** generic-limb arm that moved at all — it is a
  strictly stricter predicate, so it must. Two arms clear the Bonferroni bar of
  |z| ≥ 3.2: **`furina/salon` −8.87pp (z = −5.18)** and **`klee/demolition`
  −3.80pp (z = −4.37)**. `real_ironclad` (−4.13, z = −2.48) and
  `kokomi/commander` (−4.00, z = −2.35) are nominal only.
- **Time-to-online moved with it, always later**: `klee/demolition` 3.72 → 5.23
  fights, `furina/salon` 4.47 → 5.87, `real_ironclad` 6.23 → 8.36. Mechanically
  necessary in the same way; recorded because a plan that comes online ~1.5
  fights later is `plan_live=True` for ~1.5 more fights, which is what the
  divergence check reads.

### 3.2 Arms where draft behaviour did NOT move — three distinct causes

1. **`klee/reaction`, `furina/spotlight`, `furina/fanfare` — byte-identical.**
   Every column, both worlds. Expected: each has a dedicated `core_complete`
   branch that E1 did not touch. This is the **negative control** and it
   passed: the change reached exactly the seven archetypes it was scoped to.

2. **`ref_ironclad/generic` — byte-identical, and this one is a finding.**
   `decks differ = 0/1500`. Its `core_complete` attainment is **0.00% in BOTH
   worlds**, and `time_to_online` is `None` on all 1500 runs in both. Cause:
   `rewards.character_pool` builds `ref_ironclad`'s pool from
   `character_packages("ref_ironclad")["archetype_package"]`, six cards, and
   **none of the six carries any entry in `Card.archetypes`** (roles: 3 glue,
   2 enabler, 1 payoff; `archetypes` is empty on all six). The generic limb
   tests `archetype in c.archetypes`, so `on_plan` is structurally 0, and
   `core_complete` has been unreachable — and `_core_progress` pinned at 0.0,
   so `score_offer`'s +3.0 core-advance bonus has never fired — for the
   `ref_ironclad` anchor in **both** worlds. E1 could not move an arm whose
   first limb already returned 0. **This is pre-existing and is not caused by
   E1**; it is flagged here because a reader comparing the core-attainment
   column across characters would otherwise read `ref_ironclad` 0.00% as a v14
   regression. Whether the reference anchor's package *should* carry archetype
   tags is a design question and is **not answered here**.

3. **`kokomi/priest` — the deck moved (2.53% of pairs) but the predicate did
   not** (core −0.13pp, z = −0.07; `tto` 7.00 → 7.00 to two decimals). The
   +3.0 bonus re-ordered a few offers, but essentially every priest deck that
   assembled `DRAFT_CORE_SIZE` on-plan cards already held ≥1 payoff, so the new
   limb is close to non-binding on this arm. `kokomi/commander` (2.20% decks
   differ, core −4.00) and `kokomi/assist` (2.53%, core −1.73) sit between the
   two behaviours.

### 3.3 The quantitative form of the incomparability note

The R87(3) archive rule applied to seven arms. Measured, that archive covers:

- **draft output** differing on **0.00% – 12.47%** of seed-matched runs
  (`ref_ironclad` 0.00 · `commander` 2.20 · `priest` 2.53 · `assist` 2.53 ·
  `spark` 4.33 · `salon` 7.87 · `real_silent` 8.60 · `demolition` 11.67 ·
  `real_ironclad` 12.47);
- **`core_complete` attainment** shifted by **0.00 – 8.87 percentage points**,
  always downward, two of nine past a 36-comparison Bonferroni bar;
- **run outcome** (win, act-1) shifted by **no more than 0.67pp on any arm**,
  with **no |z| above 0.53**.

The honest one-line summary: *the seven arms are formally archive and are
measurably drafting differently, and none of that difference has reached the
winrate at n=1500.*

---

## 4. Scope fences honoured

- **No design authority exercised.** No constant was changed, no card was
  changed, no ruling is proposed. The only repo-visible artifact of Track G is
  this document.
- **`RARITY_ODDS` was not read for a decision and not touched.** The
  pre-registered payoff-reach / `RARITY_ODDS` sprint is a separate sprint with
  its own written predictions; nothing above is graded against them, and no
  statement about how many payoffs an archetype should reach for, or about
  rarity, appears in this document. The `core attain` column is reported as a
  reading of the instrument E1 changed and for no other purpose.
- **The game was not launched.** Every number here is tier 0.5 sim.

---

## 5. What this document does NOT establish

- It does not designate a standing roster table. That is [USER]'s call.
- It does not compare across versions except in §3, and §3's two halves were
  produced from the same seed in the same session on the same machine. Nothing
  here may be quoted against a table taken at a different `n`, seed, or world
  stamp.
- It does not separate any arm from any other arm on winrate; several intervals
  in §2 overlap and the table prints the widths so that they cannot be dropped.
