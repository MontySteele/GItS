# The payoff-reach predictions commit — **DRAFT, awaiting [USER] sign-off**

> **Lifecycle: DRAFT.** This file is not a registration and nothing in it
> operates. It is the *text* of the single predictions commit that R121's
> execution-order step (2) requires and that
> `review/active/payoff-reach-reregistration.md` §5 re-shaped (R137). No
> measurement was run to produce it. **No GItS roster number of any kind was
> read** — not the sheets' payoff counts, not the instrument, not a tier-0.5
> figure. That abstention is the point: predictions are authored before any
> number is read, and this file is the thing being authored.
>
> **What is already settled and appears here only as carried context:**
> the payoff-classification rubric (RATIFIED R178), the candidate bands
> (`review/active/payoff-census-2026-08-08.md` §5), and the nine band aims
> (RULED R185, the packet's §7.2 table adopted as written). None of those is
> being re-asked.
>
> **What [USER] is actually signing** is the list in §0.2 — the Q-A / Q-B
> direction-and-threshold predictions and the sample plan. Everything on that
> list is marked **PROPOSED**. The drafter of this file holds no design
> authority and takes no position beyond proposing.
>
> **Plain-English version of this file:** the one-page sign-off note prepared
> alongside it. This file is the register-side text; that note is the thing to
> read first.

---

## 0. How this file is used

### 0.1 The post-sign-off path, and it is mechanical

1. [USER] signs the one-liner (approve / amend / decline), amending any
   PROPOSED item inline.
2. An agent applies the amendments to §A of this file **and to nothing else**.
3. §A is appended **verbatim** to `review/active/payoff-reach-reregistration.md`
   as its `## 6`, in **one commit** — that commit *is* R121's step (2). The
   `DRAFT` banner at the head of this file is not appended; §A is
   self-contained by construction.
4. This file is then deleted in the same commit (its content now lives in the
   registration) and the QUEUE `Q-C` row closes.
5. The world freezes per §A.6.6 and the sprint becomes runnable under the
   pinned `DRAFTER_VERSION = 14`.
6. Steps (3)–(6) of the countersigned order run unchanged: sprint under D14 →
   blind-first grading → staged D15 (`EB-43`) lands with its re-baseline →
   the `RA-G1`/`RA-G2`/`tto` quarantine lifts on the graded read.

Nothing in that path requires a judgment call. If a step needs one, the draft
is wrong and comes back here.

### 0.2 The complete list of PROPOSED items awaiting [USER]

| # | item | where |
|---|---|---|
| **P1** | Which reading of **Q-A** the sprint answers — A-i (intervention) or A-ii (observational). They are not the same experiment and the registration's own text supports both. | §A.6.3 |
| **P2** | Which reading of **Q-B** the sprint answers — B-i (sheet intervention) or B-ii (arithmetic counterfactual). | §A.6.3 |
| **P3** | The **Q-A direction + threshold** prediction, as drafted for the selected reading. | §A.6.3 |
| **P4** | The **Q-B direction + threshold** prediction, as drafted for the selected reading. | §A.6.3 |
| **P5** | The **band-hit criterion** — how a band NAME (LOW/MEDIUM/HIGH) becomes a pass/fail against an instrument number. The bands are brackets on two axes; the instrument prints one number. The mapping is a choice and it is not made anywhere yet. | §A.6.2 |
| **P6** | The **instrument plan**: a static sheet leg (supply/offer over the three GItS sheets, same arithmetic as the census) plus a sim leg (realized on-plan payoff reach per deck), and the **generic reach reader that must be built** because the only committed reach printer is Furina-fanfare-specific. | §A.6.4 |
| **P7** | **n, seed, route, policy, loadout** — proposed at the ratified cell's own values. | §A.6.5 |
| **P8** | **Arms** — nine roster arms plus the anchor arms. | §A.6.5 |
| **P9** | **Controls**: the canonical-pool anchor arm (proposed authorised) and the blind-pick negative control (proposed **authorised with build owed**, on the `M13`/R181 `C2` precedent — or declined, which costs the sprint its empirical offer floor). | §A.6.5 |
| **P10** | **Cost ceiling** — proposed 4h wall-clock, on the EB-17p precedent. | §A.6.5 |
| **P11** | **Tripwire thresholds** T1–T4 and the redesign trigger. | §A.6.5 |
| **P12** | **World-freeze scope and its sequencing** against the still-open `RT`/`C` window that QUEUE `M14` is waiting on. This is a scheduling call, not a measurement one, and it is the only item here that touches another row. | §A.6.6 |

Twelve items. Nine of them (P5–P12 and the reading selections) are
housekeeping the house shape already fixes elsewhere; the two that carry real
content are **P3 and P4**.

### 0.3 Ambiguities found, stated rather than resolved

Recorded here because a drafter who quietly picks one reading of an ambiguous
question is doing exactly what R137 refused.

- **Q-A and Q-B are both phrased as "can reach be BOUGHT …" — a verb that
  wants an intervention, in a sprint whose drafter version is PINNED.**
  EXPERIMENTS' D4 rule is explicit that *"a scorer change **is** a version
  bump in the same edit"*, so a literal drafter-layer arm cannot run under
  `D14` without leaving the pin. Both readings are drafted in §A.6.3; the
  choice is P1/P2.
- **"In-rarity composition" (Q-B) is unspecified as to WHOSE composition** —
  the GItS sheets (an intervention on our own content) or a counterfactual
  recomputation over the existing sheets (arithmetic only). Both drafted.
- **The aims are band names; the bands are brackets on two axes; the
  instrument prints one number.** Nothing in the census packet or the
  registration says what it means to HIT a band. Drafted as P5 with a
  proposed criterion and its two rejected alternatives named.
- **A stale line-number citation, not a substantive ambiguity.** The
  registration's §3 pins `DRAFTER_VERSION = 14` at `tier0/constants.py:978`;
  the live line is **1195**. The value is unchanged and correct; only the
  line moved. §A.6.6 quotes the live location. Left uncorrected in §3 itself
  because that section is inside a countersigned frozen record.
- **One arithmetic disagreement inside the ratified census packet, reported
  and not touched.** `payoff-census-2026-08-08.md` §6.3 and its §7 summary say
  **22** payoff-shaped cards remain unattributed after R178; §7.2's standing
  caveat still says **23**, the pre-R178 figure. This does not move any band
  or any aim — it is a prose remnant of the re-issue. It is [USER]'s packet
  and R101b-adjacent, so it is named here rather than edited.

---

# §A — THE APPENDMENT BLOCK (append verbatim as `## 6` of the registration)

---

## 6. Predictions — R121 step (2), R137-re-methodized

**This section is the predictions commit.** It lands as one commit, appended
to this registration, **before the sprint's instrument runs**. Steps (3)–(6)
of the countersigned execution order are untouched by it and no step reorders.

Authored 2026-08-12. Aims per **R185**; rubric per **R178**; bands per
`review/active/payoff-census-2026-08-08.md` §5. Q-A / Q-B predictions per
[USER]'s sign-off of the same date.

### 6.1 (2b) The candidate bands, carried over with their amendment history

Derived over **identity archetypes carrying ≥ 1 payoff** in the five canonical
pools — n = **9** under the ruled **LOOSE** attribution rule (n = 7 under
`--strict-p2`). Generic layers are excluded (rubric R3(b)); zero-payoff
identity layers are a named blind spot, not a data point (census §5.3).

Each band is a **bracket**, never a point: blind-draft offer floor
(offer × cards drafted) on the left, supply ceiling on the right.

| band | offer | ceiling | N=15 | N=20 | N=25 |
|---|---|---|---|---|---|
| **LOW** (p25) | 0.0019 | 1 | 0.03 – 1 | 0.04 – 1 | 0.05 – 1 |
| **MEDIUM** (median) | 0.0058 | 1 | 0.09 – 1 | 0.12 – 1 | 0.14 – 1 |
| **HIGH** (p75) | 0.0097 | 2 | 0.15 – 2 | 0.19 – 2 | 0.24 – 2 |
| **TOP** (max) | 0.0214 | 3 | 0.32 – 3 | 0.43 – 3 | 0.53 – 3 |

In one sentence: a canonical archetype prints **1–3 draftable payoff cards**,
**none of them common** in any of the five pools, and its offer stream shows
one on roughly **0.6–6% of 3-card reward screens**.

**Amendment history, carried because the bands are order statistics over nine
points and two of them have already moved.**

| amendment | what changed | which band moved |
|---|---|---|
| **1** — token-creation layer (2026-08-10 ruling) | band population 7 → 8; `Token:Shiv` admitted in the Silent pool | **LOW** only: offer 0.0058 → 0.0019 (the new member's offer was the joint lowest, so the bottom quarter got heavier). Ceiling unchanged at 1. |
| **2** — third creation spelling re-extraction (**R178**, 2026-08-12) | band population 8 → 9; `Token:Soul` admitted in the Necrobinder pool; unattributed 23 → 22; resolved payoffs 17 → 19 | **MEDIUM** only: offer 0.0097 → 0.0058 (the new member's 0.0039 sat below the old median and pulled the middle down). Ceiling unchanged at 1; N=20 floor 0.19 → 0.12; 3-card-screen reading 2.9% → 1.7%. |

LOW, HIGH and TOP were untouched by amendment 2; MEDIUM, HIGH and TOP were
untouched by amendment 1. **HIGH and TOP have never moved.** Neither
amendment narrowed the space — LOW and TOP are the edges and neither moved —
so the bracket an archetype can be aimed into is the bracket it always was.
What moved is where the middle of canon sits inside it, and it sits lower
than the first two issues said.

**MEDIUM is rule-dependent and that is on the record (census §5.4).** Under
the ruled LOOSE rule the median reads offer 0.0058 / supply 1; under STRICT it
reads 0.0097 / 2. The mechanism is population size — LOOSE carries two
low-supply archetypes STRICT drops, and with nine points the median sits on a
different member under each — not disagreement about any card. **MEDIUM is
therefore the only band that would read differently had [USER] ruled STRICT,
and three of the nine aims are MEDIUM.** The edges are identical under both
rules on both axes. This is a caveat carried into the sprint, not a
reopening: the ruled rule is LOOSE and the table above is the LOOSE table.

**Standing caveat, carried unchanged.** Both axes are **lower bounds** while
22 payoff-shaped cards in the five pools sit unattributed (census §6.3). A
tenth archetype would move a band again by the same mechanism and with the
same lack of significance. **Aims are placed against the band NAMES and their
brackets, never against the third decimal of an offer figure**, and the
grading in §6.5 honours that.

### 6.2 (2c) part one — the aims: **RULED (R185)**

Not proposals. [USER] ruled these on 2026-08-12, adopting the census packet's
§7.2 table as written over a conflicting relayed ordering. They are the **Q-C
answer**, and this commit is their vehicle.

| character | archetype | ruled band (R185) |
|---|---|---|
| Klee | Demolition | **MEDIUM** |
| Klee | Reaction | **HIGH** |
| Klee | Spark | **LOW** |
| Furina | Salon | **MEDIUM** |
| Furina | Spotlight | **HIGH** |
| Furina | Fanfare | **LOW** |
| Kokomi | Priest | **MEDIUM** |
| Kokomi | Commander | **HIGH** |
| Kokomi | Assist | **LOW** |

Three MEDIUM, three HIGH, three LOW — one of each per character, and no
archetype is aimed at TOP. TOP is retained in §6.1 as the ceiling of the
observed canonical space, not as an aim.

**P5 — the band-hit criterion. PROPOSED.** A band is a bracket on two axes
and the sim instrument prints one number, so "did the aim land" needs a stated
rule or the grade is unfalsifiable. Proposed rule, in two parts, both graded:

- **(a) SUPPLY, static.** The archetype's draftable payoff-card count on its
  own GItS sheet lies within the band's supply figure ± 1 card
  (LOW/MEDIUM → 1, so 0–2; HIGH → 2, so 1–3; the aim fails outside that).
  Graded off the static leg (§6.4), not the sim.
- **(b) OFFER, static.** The archetype's `Σ_r RARITY_ODDS[r] × payoffs_at_r /
  pool_size_at_r` over its own sheet lies in the half-open interval between
  the neighbouring band figures — LOW: [0, 0.0058); MEDIUM: [0.0058, 0.0097);
  HIGH: [0.0097, 0.0214]. Same formula as census R7, `RARITY_ODDS` quoted
  from `tier0/constants.py:900` and not re-derived.

The realized sim reach (§6.4's second leg) is **reported against** the band
bracket at the observed deck size and is **not** part of the pass/fail. That
is deliberate: the bracket's left edge is a blind-draft floor and its right
edge is a perfect-drafter ceiling, so a committed drafter landing between them
confirms nothing — every possible drafter lands between them.

*Two alternatives rejected, named so the choice is visible:* grading on the
sim number alone (unfalsifiable, per the sentence above); grading on exact
band figures with no tolerance (the §6.1 caveat says the third decimal is
noise over nine order statistics, so a zero-tolerance grade would grade the
noise).

### 6.3 (2c) part two — Q-A and Q-B: direction and threshold. **PROPOSED.**

The registration's §2 defines the two questions from Curtain Call's
prediction 4: reach *"must be bought at the drafter/odds layer or by in-rarity
composition, not by promotion."* Both are drafted below under both available
readings, because both readings are supported by that text and picking one
silently is the retro-fit the registration's own authority forbids.

#### Q-A — can reach be bought at the drafter / odds layer?

**Reading A-i (INTERVENTION).** Arms that change the archetype scorer or the
offer odds, graded on Δreach. **This reading cannot run under the pin.** A
scorer change is a `DRAFTER_VERSION` bump in the same edit (EXPERIMENTS, D4);
an odds change is a `CONSTANTS_VERSION` bump. Either leaves `D14`, and the
countersigned order puts the staged D15 landing at step (5), *after* the
sprint. Choosing A-i therefore requires one of: (a) running the D15 arm as a
declared delta cell stamped `D15` beside a `D14` baseline inside one window —
which pre-empts step (5) and needs [USER] to say so explicitly; or (b)
re-setting the pin. Neither is proposed here.

**Reading A-ii (OBSERVATIONAL) — PROPOSED as the sprint's reading.** `D14`
*already is* the drafter-layer intervention: its stamp records that the
generic `core_complete` limb "now requires an on-plan payoff", and
`GENERIC_PAYOFF_COVERAGE = 1` (`tier05/draft.py:1219`) is the bar it sets.
So Q-A is answerable without moving anything: does a drafter that values
payoffs lift realized reach materially above the blind-draft offer floor the
census computes? If yes, the drafter layer buys reach and prediction 4's
"not by promotion" has a positive counterpart. If no, the drafter layer is
not where reach is bought either, and the remaining arm is Q-B.

> **Q-A prediction (A-ii), PROPOSED.**
> **Direction: POSITIVE.** Realized on-plan payoff reach under the `assigned`
> policy exceeds the blind-draft offer floor of the archetype's aimed band,
> at the observed deck size, in **all nine** roster arms.
> **Threshold: ≥ 3×** that floor in every arm, and **≥ 1.0 payoff per deck**
> in the three HIGH-aimed arms (Klee Reaction, Furina Spotlight, Kokomi
> Commander).
> **Reasoning, from the repo's own artefacts and not from taste.** The floor
> is a *blind* draft; the arms run a plan-committed policy against a scorer
> whose payoff limb is weighted equally with assembly (`tier05/draft.py:416-424`).
> The 3× is the conservative multiple: the LOW floor at N=20 is 0.04 payoffs,
> so 3× is 0.12 — a bar a committed drafter clears trivially if the term does
> anything at all, which makes a MISS here genuinely informative rather than
> a coin-flip. The ≥ 1.0 clause on HIGH is the `GENERIC_PAYOFF_COVERAGE = 1`
> bar restated as an outcome: if the D14 limb works, a HIGH-aimed plan holds
> its one payoff on average.
> **What a MISS would mean:** the payoff limb is not reaching, and the D15
> staged change at step (5) is doing more work than the re-baseline assumes.

#### Q-B — can reach be bought by in-rarity composition?

**Reading B-i (SHEET INTERVENTION).** Move GItS payoffs *within* a rarity so
they sit where the odds already put offers, then re-measure. This is a content
edit to the three sheets and therefore a design act, not a measurement; it
also cannot be graded blind against predictions authored before the edit
exists. **Not proposed.**

**Reading B-ii (ARITHMETIC COUNTERFACTUAL) — PROPOSED as the sprint's
reading.** Q-B is answered off the static leg with no sim and no content edit:
for each of the nine archetypes, recompute the census OFFER figure under the
counterfactual that its payoff cards sit at the rarity the odds favour most,
holding the payoff COUNT fixed. The delta between actual and counterfactual
offer is the size of the prize in-rarity composition is offering. This is the
exact mirror of prediction 4 — which measured promotion *out* of common
cutting offer frequency — run in the direction the follow-on names.

> **Q-B prediction (B-ii), PROPOSED.**
> **Direction: POSITIVE and LARGE.** The counterfactual offer figure exceeds
> the actual figure for every archetype whose payoffs are not already at the
> favoured rarity.
> **Threshold: the median archetype's offer at least DOUBLES**, and at least
> one archetype's counterfactual offer crosses a band boundary upward.
> **Reasoning.** `RARITY_ODDS` is `{common 0.60, uncommon 0.35, rare 0.05}`
> (`tier0/constants.py:900`) — a 12× spread between the favoured and the
> disfavoured slot. The census's single strongest regularity is that **not one
> canonical payoff in any of the five pools is common** (census §3.1), so the
> canonical bands are themselves built entirely out of the disfavoured slots.
> If the GItS sheets inherited that shape, the headroom is arithmetically
> enormous and doubling is a low bar. If they did not, the prediction misses
> and the interesting finding is that our sheets already differ from canon.
> **The honest weakness, stated:** this is arithmetic over the odds table, not
> a behavioural result. It bounds the prize; it does not show a drafter
> collecting it. Called out rather than dressed up.
> **What a MISS would mean:** neither arm of prediction 4's "must be bought"
> has headroom, and the follow-on's premise is wrong.

**One cross-cutting note.** A-ii and B-ii between them answer the follow-on's
question without moving a single version stamp. That is a property worth
naming: it is why the sprint is runnable under the pin at all, and it is the
reason A-i and B-i are drafted-but-not-proposed rather than simply omitted.

### 6.4 (2d) part one — the instrument. **PROPOSED.**

**§4 item 2's free parameters are filled here; §4 items 2–3 are otherwise
"unchanged" and are restated concretely below so this commit is
self-contained.**

**Leg 1 — the STATIC leg (grades P5(a), P5(b) and Q-B).** Compute, over the
three committed GItS sheets (`docs/klee-cards.yaml`,
`docs/furina-cards.yaml`, `docs/kokomi-cards.yaml`), per archetype: draftable
payoff supply (`role: payoff` ∧ archetype ∧ rarity ≠ basic) and the census R7
OFFER figure. Same formula, same `RARITY_ODDS` source. No sim, no run, no
stamp — it reads authored content, exactly as the census read canonical
content.

**Leg 2 — the SIM leg (reports realized reach; grades Q-A).** Realized on-plan
payoff cards per finished deck, per arm. `tier05/draft._generic_core_counts`
already returns exactly this pair for a deck and an archetype
(`tier05/draft.py:383-391`), so the reader is a printer over an existing
function, not new classification logic.

**The build that is owed, named because D4 requires the instrument to be able
to SEE the object.** The only committed reach printer is
`tier05/exp_furina_ghostcheck.py`, and its payoff column is
`draft._reads_fanfare` — **Furina-fanfare-specific**. It cannot see eight of
the nine arms. A generic reach printer over `_generic_core_counts` must be
built **before the run and after this commit**, on the `M13`/R181 precedent
that a control may be authorised with its build owed. It adds no classifier
and reads no new field.

### 6.5 (2d) part two — arms, n, seed, route, cost ceiling, controls, tripwire. **PROPOSED.**

**Arms — nine roster arms.**

`klee/demolition`, `klee/reaction`, `klee/spark`, `furina/salon`,
`furina/spotlight`, `furina/fanfare`, `kokomi/priest`, `kokomi/commander`,
`kokomi/assist` — the nine aimed in §6.2, one per aim, no more and no fewer.

**Sample plan — proposed at the ratified cell's own values, which is the
conservative default in every case.**

| parameter | proposed | why this value |
|---|---|---|
| `n` | **600 per arm** (9 arms = 5,400 runs; 7,800 with controls) | `cells.CANONICAL`'s own `runs` (R68). The ghost check's 200 is a *declared* reduction; a registered sprint takes the ratified number. |
| `seed` | **11** | `cells.CANONICAL.seed`. Reach is a compositional statistic, so a seed change is not a comparability repair here — but keeping the ratified seed costs nothing and keeps the arms reproducible against every other canonical-cell read. |
| `route` | **`hunter`** | `cells.CANONICAL.route`. |
| `policy` | **`assigned`** | The plan-committed drafter. Q-A is *about* what a plan-committed drafter reaches for; `adaptive` would answer a different question. |
| loadout | **realistic** (relics + potions) | `cells.CANONICAL.realistic = True`. A bare run is a different world, not a cheaper sample of this one. |
| acts | **all registered acts** (`n_acts = None`) | Canonical. Reach is measured on the finished deck. |
| cell naming | every arm derived with `Cell.but(...)`, so each row's stamp names its own delta | R68; the stamp is mandatory and a report without one is not citable. |

**Controls.**

- **C1 — canonical-pool anchor arm. PROPOSED AUTHORISED.**
  `(real_ironclad, starter)` and `(real_silent, starter)` at the same cell.
  These two draft from the *actual* Ironclad and Silent pools the census
  measured, so they are the one available join between the sim's realized
  reach and the census's derived bands. They depend on the gitignored
  `game_ref/` tree and therefore run in the primary checkout only, never in a
  worktree.
- **C2 — blind-pick negative control. PROPOSED AUTHORISED, BUILD OWED.**
  A policy that takes uniformly at random from each offer screen, giving the
  offer floor **empirically** rather than by arithmetic. `draft.POLICIES`
  currently holds only `assigned` and `adaptive`
  (`tier05/draft.py:1659`), so this is a small build owed before the run — the
  same shape R181 authorised for `M13`'s `C2`. **Declining it is a live
  option**: the cost is that Q-A's floor stays the census's computed floor,
  which the sprint would then be comparing a sim number against an arithmetic
  one. Stated so the cost of declining is visible.

**Cost ceiling — PROPOSED 4 hours wall-clock** for the whole registered range,
on the EB-17p precedent (which registered a 4h ceiling and held to it). If the
range does not finish inside it, the run **stops and reports what it has**;
it does not silently extend and it does not silently shrink `n`.

**Tripwire — stop and re-register if any of these fires.**

| id | condition | why it is a stop rather than a footnote |
|---|---|---|
| **T1** | The world stamp at any arm is not `RT10 / D14 / P7 / C9` | The pin is the registration's; a moved stamp means the sprint is measuring a different world than the one it was registered against. |
| **T2** | Mean finished deck size in any arm falls outside **12–30 cards** | The §6.1 brackets are quoted at N=15/20/25. Outside that span the band floors are being extrapolated, not read. |
| **T3** | Any arm's realized reach exceeds the TOP supply ceiling of **3** | The reach reader would then be counting something the ratified rubric would not call a payoff, which is an instrument fault and not a finding. |
| **T4** | The static leg finds any archetype with **zero** draftable payoff cards | A zero is a finding about the sheet (census §5.3 calls the canonical zeros blind spots), but it makes every offer-based grade for that arm degenerate. It stops the sprint and goes to [USER] as a content question. |

**Redesign trigger — PROPOSED.** If an archetype misses its aimed band on
**both** P5(a) and P5(b), that archetype's sheet composition goes to `QUEUE`
as a design row. Missing one of the two is reported, not triggered — the two
axes answer different questions and disagreeing is informative on its own.

**Grading is blind-first (step 4).** The predictions above are graded as
PREDICTED / SPLIT / MISS against the run output before any narrative is
written, in the EB-17p §13 shape. Per D5, nothing above is revised against the
run that grades it.

### 6.6 The pin, the contamination statement, and the freeze

**Pin — VERIFIED LIVE 2026-08-12.** `DRAFTER_VERSION = 14` at
**`tier0/constants.py:1195`**. (The registration's §3 cites line 978; the
value is unchanged and the line has moved — §3 is inside a frozen record and
is not edited for it.) The full world stamp at this commit is
**`RT10 / D14 / P7 / C9`**: `RUNTEMPLATE_VERSION = 10`
(`tier0/constants.py:708`), `CONSTANTS_VERSION = 9`
(`tier0/constants.py:1059`), `POLICY_VERSION = 7` (`tier05/draft.py:1454`),
read live through `tier05/cells.py`. The staged D15 change
(`staged/d15-spotlight-payoff`, `EB-43`) stays staged: it lands at step (5),
with its re-baseline, after this sprint runs.

**Contamination statement (D4 / D5), restated.** The bands in §6.1 were
derived from canonical CONTENT only — the extracted pools under `game_ref/` —
never from the sprint's instrument and never from a tier-0.5 number. The aims
in §6.2 were placed against band names, not against any GItS reading. The
predictions in §6.3 were authored with **no** GItS payoff count and **no**
instrument output in hand. One variable per window: the world is frozen for
the duration (below), so the only thing that moves between this commit and the
graded read is the measurement itself.

**Blind discipline, untouched.** Steps (3)–(6) of the countersigned execution
order run as written and in that order: (3) the sprint runs under D14;
(4) blind-first grading; (5) staged D15 (`EB-43`) lands with its re-baseline;
(6) the `RA-G1` / `RA-G2` / `tto` quarantine lifts on the graded read. **No
step reorders.**

**P12 — the freeze. PROPOSED.** From this commit until the graded read, no
`RT` / `D` / `P` / `C` bump lands on the sprint's branch. **The sequencing
call this raises, named because it touches another row:** QUEUE `M14` records
that the `RT`/`C` window is still open — `EB-70`, the `EB-82` conversion, the
`EB-85` batch and `EB-69` all move what a cell measures — and `M14`'s own
predictions are deliberately held until that window settles. The same logic
applies here, so the two available orderings are:

- **(i) run first.** Freeze now, run the sprint inside the current
  `RT10/D14/P7/C9` window, then let the open batch land. The sprint's numbers
  are then measured in a world that changes shortly after — acceptable,
  because the sprint's grades are about *reach composition*, and none of the
  open items touches the payoff role, the sheets' archetype fields or
  `RARITY_ODDS`.
- **(ii) settle first.** Let the open batch land, re-stamp this section if the
  world moved, then freeze and run — the exact sequence `M14` is following.
  Costs delay; buys one world for both registrations.

**(ii) is the conservative default and is what is PROPOSED**, on the ground
that it is the sequence [USER] already chose for the neighbouring
registration.

### 6.7 Data held — status at this commit, verified 2026-08-12

**All five canonical pools are extracted and present.** The R178 re-extraction
ran `tools/extract_base_game_pool.py` over
`Ironclad,Silent,Defect,Necrobinder,Regent` and the primary checkout's
gitignored `game_ref/` now holds `ironclad.json`, `silent.json`,
`defect.json`, `necrobinder.json` and `regent.json`, plus the derived
`payoff_census.json` / `payoff_census_strict.json` and `role_tempo_canon.json`.

**This supersedes the note at the end of §5**, which recorded — correctly at
its ruling date, 2026-08-08 — that only Ironclad and Silent were held and that
Defect, Necrobinder and Regent needed one `--characters` extraction run riding
the next `EB-47` sitting. **That extraction has run.** It ran twice, in fact:
once for the 2026-08-10 re-issue and again for the R178 third-creation-spelling
re-extraction, which regenerated all five pools and diffed them field by field
(six changed fields, all `creates` in the Necrobinder pool; the other four
byte-identical). The `EB-47` Windows-batch dependency is discharged.

**The standing constraint on that data is unchanged.** `game_ref/` is
gitignored base-game material, REFERENCE ONLY, primary-checkout-local. **A
worktree has no `game_ref/` and must never be given one** — which is why the
census tool takes the path as an argument and why control C1 runs in the
primary checkout only.

---

*(end of §A — nothing below this line is appended to the registration)*

---

## 1. Provenance of this draft

Drafted 2026-08-12, branch `overnight-burn-2026-08-12`, against
`review/active/payoff-reach-reregistration.md` §5 (R137's re-methodized step
(2)) and `review/active/payoff-census-2026-08-08.md` §5 / §7 (R178 rubric,
R185 aims). **Zero design authority exercised.** No measurement was run, no
GItS roster number was read, and the pinned `DRAFTER_VERSION = 14` was
verified in the live tree rather than quoted from prose.
