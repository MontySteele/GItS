# Klee Pass 4 — Design-Pass Brief ("The Statline Reconciliation")

**Date:** 2026-07-21. **Authorized:** user ruling this session — *"let's go
with the design spec. Scaling needs a nerf, and utility needs a buff"*,
followed by *"this might actually need a design pass."*
**Origin:** the v1 planned-vs-shipped review round (8 parallel audits).
**Governing docs:** klee-character-design.md §2/§4/§7, principles v1.10
§3.3–3.4, pass3-ratification.md, klee-errata-report.md (V01_MEDIAN lock).
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2, A6_INSTRUMENT_VERSION 2.

**Status: NOTHING IN THIS DOC IS RULED.** Every number is a measurement or
a proposal. Per house rule, balance numbers, band/metric redefinitions and
instrument version bumps are user calls; this brief ships the evidence and
the asks.

---

## 0. Why this is a design pass and not a number tweak

The review found Klee's declared identity and her measured identity have
come apart, and the gap cannot be closed by tuning card numbers alone —
because **one half of it is a conflict between the design doc and the
instrument that scores it.**

Declared (§2): elite pair **A1 4.5 + A6 4.0**, A2 capped **≤4.0 and always
< A1**.
Measured (1000 fights, seed 42, archetype-deck median = round-3 canon):

| Axis | Declared | Measured | Status |
|---|---|---|---|
| A1 Frontload | 4.5 | 4.117 | short 0.38 |
| A2 Scaling | **≤4.0**, < A1 | **4.097** | **ceiling breached** |
| A6 Utility | **4.0** | **3.587** | short 0.41; never reached 4.0 in ANY pass (1.7 → 3.4 → 3.59) |
| A7 Setup tax | 3.5 | 2.102 | short 1.40 |
| A5 Velocity | 3.5 | 3.043 | short 0.46 (flagged pass 3, never closed) |

Her actual axes ≥4.0 are **A1 and A2** — so her second elite axis is
empirically **Scaling**, the axis the doc explicitly capped, and Utility
never arrived. The `A1 > A2` invariant now holds by **0.020** (was 0.3 at
pass-3 freeze, 0.24 post-errata): it has shrunk ~90% and is inside noise.

**Why nothing failed:** the ≤4.0 ceiling and the "exactly two elite axes
(A1, A6)" *pairing* were never encoded. `axes.heuristic_flags` counts how
many axes are ≥4.0 without caring **which**, so an A1+A2 character and an
A1+A6 character are indistinguishable to it. The ±0.3 V01_MEDIAN lock
absorbs all drift to date.

---

## 1. The A6 conflict (the load-bearing finding)

A6 v2 = `3.0 × (0.5·aoe_ratio + 0.3·debuff_ratio + 0.2·uptime_additive)`.

Decomposed per deck (300 fights, seed 42, baseline REF_IRONCLAD starter):

| deck | A6 | aoe ×0.5 | debuff ×0.3 | uptime ×0.2 |
|---|---|---|---|---|
| demolition_weighted | 3.630 | **1.672** | **0.080** | 1.749 |
| spark_weighted | 3.208 | 1.404 | **0.000** | 1.837 |
| reaction_weighted | 3.908 | 1.920 | 0.058 | 1.626 |
| **median** | **3.630** | 1.672 | 0.058 | 1.749 |

Raw: swarm DPT 18.8 vs baseline 11.3. Debuff stacks **0.52/fight vs
baseline 9.06**. Aura uptime 0.749 vs baseline 0.000.

**The entire shortfall is the debuff term.** Her AoE is 1.4–1.9× baseline
and her application uptime is category-leading against a baseline of zero.

Two hard constraints on any fix:

1. **A6 cannot reach 4.0 on uptime alone.** Uptime is a fraction of enemy
   intents; even a physically perfect 1.0 only lifts the score by 0.151, to
   **3.761**. The remaining distance MUST come from debuff or AoE.
2. **Klee's design rationale never claimed debuff.** §2 justifies A6 4.0 as
   *"Excellent AoE / poor precision (random targeting is the tax)."* The
   instrument spends 30% of the axis on a thing her identity says she
   doesn't do. **She is being marked down on a component her own design
   rationale disclaims.**

Sensitivity — what each term must reach for A6 = 4.0, others held:

| term | now | needed | factor | feasible? |
|---|---|---|---|---|
| aoe | 1.672 | 1.932 | 1.16× | yes (swarm DPT 18.8 → 21.8) |
| debuff | 0.058 | 0.491 | 8.50× | yes in absolute terms (0.52 → 4.45 stacks/fight) |
| uptime | 1.749 | 2.399 | 1.37× | **impossible** (implies uptime 1.399 > 1.0) |

### 1a. The debuff shortfall is NOT a package artifact

Checked by two independent routes, because the obvious objection is that
the hand-authored packages simply omit her debuff cards:

- **Sheet:** only **4 of 76** cards apply a debuff — `spooked` (common,
  generic), `trip_wire` (uncommon, demolition), `surprise_visit` (uncommon,
  generic), `explosive_frags` (rare, `detonation_vuln`). Packages contain
  `spooked` (demolition, reaction) and nothing at all (spark → 0.000).
- **Draft layer:** 200 assigned-policy tier05 runs per archetype (ad-hoc,
  **unstamped, not a ratified measurement**) draft a mean of **0.1 debuff
  cards per run** in demolition and spark, and **0.0** in reaction.

So the drafter independently doesn't value them. A6's debuff term reads
~zero for Klee under both sims, by two different routes. This is a real
property of the character, not a measurement artifact.

---

## 2. What the draft layer says about the packages (a null result)

The related worry — that tier0's fixed packages misrepresent real decks —
was tested and **largely did not replicate.** Same 200-run basis:

| archetype | companions/run | zero-companion runs | run winrate |
|---|---|---|---|
| demolition | 1.1 (median 1) | 33% | 57% |
| spark | 0.9 (median 1) | 36% | 50% |
| reaction | 3.7 (median 4) | 0% | 52% |

tier0 models demolition and spark at **0** companions against a drafted
mean of ~1, and a third of real runs genuinely end companion-free. The
packages mildly understate companion access but are defensible; the round-3
"plausible drafts" restructure holds up. **Recorded as a null result so it
is not re-litigated.**

Construction, for the record: tier0 `build_player` = starting deck (10) +
fixed package (15) = **25 cards**, identical every fight, across the
6-encounter battery. No drafting, no upgrades applied, no relics beyond
`relic_hooks`. Only `reaction_weighted` carries companions (7 rows, 6
distinct). tier05 is the layer that models acquisition.

---

## 3. The A2 side

Per-deck A2 (300 fights, seed 42) and the ratified per-deck bands:

| deck | A2 | band | headroom |
|---|---|---|---|
| demolition_weighted | 4.475 | ≤4.8 | ok |
| spark_weighted | **4.127** | ≤4.5 | ok |
| reaction_weighted | 3.202 | ≤3.5 | ok |

**Canon A2 is the median = spark_weighted exactly.** Consequences:

- **Nerfing demolition does nothing to canon** until it drops below 4.127.
- Only a spark change moves the median, and only down to a floor of 3.202
  (reaction's value), below which the median pins to reaction.
- Spark's in-package scaling drivers: `spark_knight_style`
  (`zero_cost_attacks_up` 2, cap 4), `endless_fireworks` (`spark_per_turn`
  1), `gleeful_barrage` (`times_formula: 2_plus_sparks`).

**Collision warning (binding on sequencing):** `gleeful_barrage` was JUST
re-costed 4→3 at R39, and that is what resolved spark tank_boss to 58.7% in
the ratified [45, 65] band. **A further spark-scaling nerf re-opens the band
R39 just closed**, and bundling it with an A6 change violates
one-variable-per-measurement-window.

### 3a. A verified mechanism worth exploiting

**Swarm fights never reach turn 10 in any deck (0/120, all three decks,
all encounters checked).** A2 only counts fights with `turns >= 10` (fed by
attrition / gauntlet / tank_boss). Therefore **the A6 AoE term and the A2
window are provably disjoint.**

An AoE-led buff consequently moves **A6 toward 4.0** and **A1 toward 4.5**
(also short) and **widens the A1>A2 margin** off its current 0.020 — without
touching A2 or re-opening spark's freshly-settled band. It does not by
itself bring A2 under the 4.0 ceiling.

---

## 4. Decision-ready asks (for red-pen)

**A1 — the A6 instrument vs. Klee's identity.** Pick one:
   (a) **Reweight A6** so it measures what the doc claims (AoE + uptime
       heavy, debuff light). **Cross-character cost:** the instrument is
       SHARED; `A6_INSTRUMENT_VERSION` v2's own comment records "Furina
       measured 3.6 under it". A v3 renumbers Furina's A6, archives v2
       numbers, and must never be compared unlabeled.
   (b) **Print debuff into Klee's kit** so she genuinely earns the 30%.
       Contradicts "poor precision" as her stated utility tax — an
       identity change, not a number.
   (c) **AoE-led buff** (needs swarm DPT 18.8 → 21.8, +16%): identity-
       consistent, also fixes A1, provably A2-neutral. Reaches 4.0 only if
       the debuff term is also reweighted or topped up — see the
       sensitivity table.
   (d) Some mix — e.g. (c) for the bulk plus a modest (b) top-up.

**A2 — the A2 ceiling.** Trim spark scaling (which lever, and how much),
accepting that it re-opens the R39 tank_boss band? Or does an improved A1
(and therefore a wider A1>A2 margin) change the disposition of the ≤4.0
ceiling itself?

**A3 — §3.4 archetype band.** All three archetypes sit outside the
"15–20 tagged cards" rule (**28 / 22 / 14**) with no amendment anywhere in
the v1→v1.10 log. Reaction's 14 is rationalized in the character doc
("enablers live in the companion pool") but never formally waived. Amend
the band, or accept the deviation on record?

**A4 — the unmeasured co-op claim.** The reaction archetype is declared
**co-op-primary, boss-weak solo**. Its solo numbers are healthy (tank_boss
52.1% vs ≥35% floor; run winrate 52%, between demolition 57% and spark
50%), so "playable solo with above-average drafting" is met. But
`TIER2-VALIDATE: reaction co-op` is deferred and **no tier can model a
second player** — the archetype's declared home is the one condition no
instrument in the repo can see. Does this pass proceed on the co-op claim
as an assertion, or does co-op modelling enter scope first?

**A5 — arming the encodings.** The ≤4.0 ceiling and the elite-axis pairing
are still unencoded. Land them as hard suite failures now (suite goes red,
`validate.ps1` S7 blocks deploy until the rebalance lands), or as
report-only flags until the pass closes?

---

## 5. Pre-registered measurements (run only after A1/A2 are ruled)

One variable per window; null results binding.

1. **A6 window.** Whichever of (a)–(d) is ruled, measured ALONE at 1000
   fights / seed 42: full 7-axis median, A6 component decomposition, and
   the V01_MEDIAN ±0.3 lock re-checked on every axis.
   *Prediction to beat:* A6 median ≥ 4.0 with A2 unmoved within ±0.05
   (the disjointness claim in §3a — if A2 moves more than that, the
   mechanism is wrong and the finding is void).
2. **A2 window.** Separately: median A2 ≤ 4.0, A1−A2 margin, and the
   spark tank_boss winrate re-checked against the ratified [45, 65] band
   at ≥1000 fights (band checks are meaningless below that).
3. **Regression locks**, per the standing lesson that a mechanic ruling is
   not done until its lock exists AND has been seen to FAIL against the
   bug it claims to catch.

## 6. Already landed this session (instrumentation only, no balance change)

- `tier0/tests/test_klee.py::test_pool_composition` — locks 4/32/25/15 = 76
  and the `sparks_n_splash` kit identity, mirroring Furina's.
- `tier0/tests/test_klee.py::test_archetype_tag_counts` — locks 28/22/14/19
  as a drift detector; deliberately does NOT assert §3.4's 15–20 band
  (see ask A3).
- Both verified to FAIL against the drift they catch (replayed the
  pre-M7-R1 world by hiding `snap`; both assert, then pass on restore).
- `docs/klee-cards.yaml` stale headers corrected: `COMMON (31)` → 32,
  `Spark (10)` → 11. The sheet was right; the counters were stale.
- Full repo suite: **241 passed** (repo root, tier0 + tier05 + tools).

## 7. Out of scope for this pass

Relics/potions/artifact sets (separate chat per user), art red-pen and the
`KleePlaceholderArt` question, telemetry/sim-trust instrumentation, the
S1 pipeline-step→C#-hook sweep, and every other v1 review item not listed
in §4. Recorded in memory `klee-v1-review-gaps` so they are not lost.
