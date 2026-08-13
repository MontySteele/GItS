# M17 — force-first-copy paired winrate, **re-registered under `P7`**: DRAFT

> **Lifecycle: DRAFT, awaiting [USER]'s countersign at QUEUE `M17`. UNRUN.**
> This is the second of the two drafts `M17` says do not exist yet. It is a
> **new registration standing beside** the frozen `EB-17p` packet — not a
> re-grade of it, not an amendment to it.
>
> **R101b holds absolutely.** `review/active/eb17p-registration-draft-2026-08-08.md`
> and `review/active/eb17p-results-2026-08-10.txt` are **untouched** by this
> packet. Their §13 grade stands as published. Where this packet quotes them it
> quotes them; it never edits them.
>
> **Prediction slots (§8) are BLANK and are [USER]'s.** So is the redesign
> trigger (§8.1). Per EXPERIMENTS law and the R121 precedent, predictions are
> authored design-side and land as their own commit **before** any seed in the
> registered range is run. Nothing in this file may be run until they exist.

---

## 0. Plain-English summary

Back in August we ran an experiment on five of Klee's cards. For each card we
took 2,400 runs, forced one copy of that card into the deck, and compared
against the same 2,400 runs without it — same seeds, same maps, same relics,
one card different. One of the five arms was a deliberately blank card (a spare
copy of Klee's basic attack) so we could tell "this card is bad" apart from
"any extra card dilutes the deck".

That experiment is finished and graded. But two things have happened since:

1. **The world moved.** The experiment ran in the world stamped
   `RT9/D14/P6/C8`. What ships today is **`RT10/D14/P7/C9`** — three of the
   four fields changed. By our own stamp law, the old numbers are not today's
   numbers.
2. **One arm turned out to be measuring the pilot, not the card.**
   `borrowed_brilliance` was drawn 40,396 times and played **zero** times. That
   was the simulated pilot refusing to value the card, not the card being
   unplayable. `P7` (R176) fixed the pilot's valuation, and the base card now
   plays about **6.1%** of the time (60 of 981, measured).

So R180 ruled: re-run it. **The same five cards, not a narrowed set** — because
the blank-card arm and the other three arms are what make any one number
readable, and dropping them would leave a single-card experiment that cannot be
graded against anything.

This document is that re-run, written out in full so it can be countersigned.
It is the same instrument, the same protocol and the same five arms as before,
re-stamped to today's world. **What is deliberately empty is the prediction
table** — those are [USER]'s, they get written down before anything runs, and
the results are graded blind against them afterwards.

**When it runs matters**, and §9.1 says so: the payoff-reach sprint goes first
under the approved settle-first plan, and this sweep runs after it, in a world
that has not moved in between.

---

## 1. Provenance and what has changed

**Parent.** `EB-17p`, `review/active/eb17p-registration-draft-2026-08-08.md`,
countersigned and graded 2026-08-10 (3 PREDICTED / 1 SPLIT / 1 MISS). The
register's phrase is unchanged: *"two decks on the same seeds, one with a copy
forced in, one without."*

**Authority for this packet.** QUEUE `M17`, **R180 (2026-08-12)**: the two
trigger-fired cards are split; `elemental_ecstasy` goes to redesign, and
`borrowed_brilliance` is *"remeasured before any design act — specifically by
re-running the REGISTERED five-card sweep, re-registered under `P7`, **never a
narrowed single-card experiment**"*.

**The three things that changed since the parent ran:**

| | parent (`EB-17p`) | this packet |
|---|---|---|
| world stamp | `RT9 / D14 / P6 / C8` | **`RT10 / D14 / P7 / C9`** |
| `borrowed_brilliance` base-card play rate | **0 plays / 40,396 draws** (§13.8) | ~**6.1%** (60 / 981, measured under `P7`) |
| status of §13's Δ figures | the published grade | **`P6` reads**; `P7` moves every Klee number |

**What has NOT changed, and may not:** the arm set (§5), the estimand (§2.3),
the pairing (§4), the metric definitions (§6) and the grading discipline (§9).
Those are copied forward deliberately. A re-registration that also redesigned
the instrument would answer a different question and would not be comparable to
anything, including itself.

**What this packet is NOT.** It is not a re-grade of `EB-17p` §13, not an
erratum to it, and not a claim that its grade was wrong. `EB-17p` measured its
world correctly. This measures a different world.

---

## 2. Questions

**Q1 (primary).** For a named card `X`, does forcing one copy of `X` into the
deck at run start change the run's winrate, holding the seed fixed, **at
`RT10/D14/P7/C9`**? Estimand: **Δ = P(win | forced) − P(win | not forced)**,
paired by seed.

**Q2 (secondary, descriptive).** Within the forced arm, the card's own flow —
`draws_per_fight`, `played_when_drawn_rate`, `dead_in_hand_rate`,
`force_first_copy_rate` (`metrics.card_flow_profile`, per card id).

**Q3 (secondary).** Compliance — does the assignment survive the run (§6.3).

**Q4 (new here, and the reason R180 ordered the re-run).** Does
`borrowed_brilliance`'s §13.8 anomaly clear under `P7`? Specifically: is the
bare form's `played_when_drawn_rate` **non-zero** in this world, and does its
Δ-vs-filler move relative to the parent's −0.17 pp?

**Q4 is graded as a descriptive question with a stated direction, not as a
comparison to the parent's number.** The parent's −0.17 pp was taken at `P6`
and may not be subtracted from anything measured here — stamp law (R68). What
Q4 asks is what this world says, and [USER]'s §8 prediction for that arm is
what it is graded against.

**Not asked here.** Whether any observed Δ justifies a redesign of any card.
That is the design act, downstream of the grade, and [USER]'s — exactly as in
the parent (§1, "Not asked here").

---

## 3. World, cell and arms

**Stamp, pinned: `RT10 / D14 / P7 / C9`.**

| field | value | source |
|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **10** | `tier0/constants.py` — the enchant events (R82 / M7) |
| `D` `DRAFTER_VERSION` | **14** | `tier0/constants.py` — held at 14; the payoff-reach pin (R121) |
| `P` `POLICY_VERSION` | **7** | `tier05/draft.py` — R176, the pilot valuation fix |
| `C` `CONSTANTS_VERSION` | **9** | `tier0/constants.py` — slot-2 rarity floor + the X7/X8 promotions |

Read live via `tier05.cells` and reprinted by `Cell.stamp()` on every table.
**Pinned for this experiment**; a bump in any of the four before execution
re-registers (§9, S1). **`RT` and `C` are the live risk here, not `D`** — see
§9.1.

**Base cell.** `cells.CANONICAL.but(character="klee", archetype="reaction",
name="m17p7")` — the ratified cell (R68): seed 11, route `hunter`, policy
`assigned`, realistic loadout (relics + potions), all registered acts. Same
cell as the parent, for the same reason: all four register-named cards are Klee
cards tagged `archetypes: [reaction]`, and `assigned` is the policy under which
"the deck the plan wanted" is a well-defined control.

**Note on the cell's `P7` meaning.** Under `P6` the `assigned` policy's scorer
did not value `copy_companion_in_hand` / `replay_next_companion`; under `P7` it
does (R176). The cell name is the same; **the pilot inside it is not the same
pilot**, and that is the whole point of the re-run.

**Arms.** Six, exactly as the parent:

| arm | `force_cards` | role |
|---|---|---|
| `control` | `None` | anchor; byte-identical to the unmodified world |
| `forced(friendly_visit)` | `[friendly_visit]` | register card 1 |
| `forced(study_buddy)` | `[study_buddy]` | register card 2 |
| `forced(borrowed_brilliance)` | `[borrowed_brilliance]` | register card 3 — **the card R180 ordered re-measured** |
| `forced(elemental_ecstasy)` | `[elemental_ecstasy]` | register card 4 |
| `forced(kaboom)` | `[kaboom]` | **filler / deck-dilution negative control** |

`control` is run **once** and reused as the paired partner for every `X`, as in
the parent.

---

## 4. Seeds and pairing

- Base seed **11** (the ratified cell). Run *i* of a batch is a pure function of
  `seed + i` (`tier05/model.py`), so pairing is **by index**: run *i* of
  `forced(X)` and run *i* of `control` share seed `11 + i`.
- Registered seed range: `11 … 11 + N − 1`, `N` from §7.
- **Excluded, explicitly:** `424242 …`, the `--smoke` seed base the sweep
  script uses for "does it run" checks (`tier05/exp_eb17p_forced_copy.py`,
  parent §10). Any pre-run check uses `--smoke` and its banner; nothing below
  it may be quoted.
- **The same seeds as the parent are used again, deliberately.** They are the
  ratified cell's seeds. This is **not** a paired comparison against the
  parent's runs — the worlds differ, so a seed number means a different run in
  each. Same seeds, different world, no cross-world pairing. Stated here so
  nobody constructs one at grading time.

---

## 5. The sweep — which cards

**The set is fixed by R180 and may not be narrowed.** All five, in the
register's order, plus the filler:

| id | name | rarity | cost | note |
|---|---|---|---|---|
| `friendly_visit` | Friendly Visit | common | 1 | Block 5 + companion cost −1 + draw 1 |
| `study_buddy` | Study Buddy | uncommon | 1 | Block 6 + replay-next-companion |
| `borrowed_brilliance` | Borrowed Brilliance | uncommon | 1 | free temp copy of a companion in hand |
| `elemental_ecstasy` | "Sweet Dreams" | uncommon | 2 | aura refresh + per-aura draw + conditional Block 8 |
| **`kaboom`** | "Kaboom!" | basic | 1 | **deck-size negative control** |

**5.1 The filler stays `kaboom`.** [USER] chose it on 2026-08-10 and the
reasoning is unchanged: it is a duplicate of Klee's own starting Strike
(`tier0/content/characters/klee.yaml`), so forcing a copy changes the deck's
*size* and its *ratio of basics to everything else*, and nothing else. Its own
Δ-vs-control is the size of pure dilution in this cell, and it is the first row
read at the grade (§9). A test pins that Klee's starter still contains `kaboom`
(`tier05/tests/test_eb17p_force_cards.py`); if it ever stops, the negative
control has quietly become a real card and the test fails.

**5.2 Card-id family.** Every read pools `X` with `X+` (`upgrades.SUFFIX`),
because a smith node rewrites the id in place. A read keyed on the bare id
would score an upgraded forced copy as an absent one.

**5.3 One arm, two names.** "Sweet Dreams" and "Elemental Ecstasy" are the same
card; the sheet renamed it for display on 2026-07-20 and kept the id
(`docs/klee-cards.yaml:178-183`). One registered arm, not two.

**5.4 If the `elemental_ecstasy` redesign lands first.** Then this arm measures
a different card and the packet is re-stamped (`C10`) before it runs; the
consequences of that ordering are laid out in the companion packet
`review/active/m17-elemental-ecstasy-redesign-2026-08-13.md` §6, and the choice
is [USER]'s. **The arm is not dropped under either ordering.**

---

## 6. Metrics — unchanged from the parent

### 6.1 Primary (Q1)
Per card `X`, over the `N` seed-matched pairs:
`delta_win` = winrate(`forced(X)`) − winrate(`control`), with exact McNemar on
the discordant pairs (`b`, `c`) as the test and a paired bootstrap (resampling
*pairs*, own RNG stream, own seed, never a run seed) for the interval.
Discordant and concordant counts are printed; a Δ with no discordant count
beside it is not citable. Unpaired Wilson intervals per arm are printed for
continuity and are **not** the test.

### 6.1b Co-primary — card versus filler
`delta_vs_filler(X) = winrate(forced(X)) − winrate(forced(kaboom))`, paired by
seed index over the same `N` pairs, same machinery. **Retained as a co-primary**
— [USER] added it on the parent's countersign, and it is the contrast that
distinguished "this card is harmful" from "this card is doing nothing" in
§13.4. Both co-primaries are graded; neither may be dropped after the read
because the other was more flattering.

**What §6.1b does not inherit.** Both of its arms are treated, so a §6.1b delta
is **internally valid and externally unanchored** — it may not be quoted against
any archived winrate. If S2 fires, §6.1 is void and §6.1b survives only as a
comparison of two treated arms, and the report must say so.

**No multiplicity correction is registered**, for either contrast, for the
parent's reason: the grade is not a hunt for a significant row. Each card is
graded against a direction and a threshold [USER] wrote down before any number
existed. A row that was not predicted and turns up significant is a hypothesis
for a new registration, not a finding.

### 6.2 Secondary run-level
`delta_act1`, `delta_acts`, `delta_decksize`, `delta_fights` — same pairing,
same reporting shape.

### 6.3 Compliance and contamination census (Q3)
Forced arm: share of runs whose FINAL deck still holds the `X` family; share
removed at rest; share upgraded; mean family copies. Control arm: share of runs
that drafted the `X` family on their own. **This bounds what the design can
see**: a control arm that already holds `X` often attenuates ITT Δ by
construction.

### 6.4 Pre-registered secondary subgroup
Δ restricted to pairs where the control run never acquired the `X` family, with
its own `n`. **Secondary. It may not be promoted to primary after the read.**
(For `kaboom` this subgroup is empty by construction — the parent's was `n = 2`
— and it is reported and disregarded.)

### 6.5 Card-flow read (Q2, Q4)
`metrics.card_flow_profile` over the forced arm's `fight_stats`, restricted to
the `X` family: `draws_per_fight`, `played_when_drawn_rate`,
`dead_in_hand_rate`, `force_first_copy_rate`, printed per form **and**
family-pooled.

**The `borrowed_brilliance` bare-form line is the Q4 read** and the script
already prints it per form, so no new column is needed.

**Instrument visibility (D4), confirmed.** `RunResult.fight_stats` carries the
EB-17 counters through to tier 0.5 and `card_flow_profile` consumes them
unchanged; this is the same one-seat sim instrument the parent used, on the
same objects. No C#-only limb, no `support` term.

---

## 7. Sizing

Unchanged from the parent, and for the same reasons.

**Variance model.** Binary outcome at the run level; for a paired binary
contrast the variance is carried by the discordant pairs,
`SE(Δ) = sqrt(d / N)`. Minimum detectable Δ at two-sided α = 0.05, power 0.80
(factor 2.80):

| pairs `N` | MDE at `d = 0.11` (conservative) | MDE at `d = 0.05` (optimistic) | runs (1 control + 5 treated) |
|---|---|---|---|
| 600 (ratified cell) | 3.8 pp | 2.6 pp | 3,600 |
| 1,200 | 2.7 pp | 1.8 pp | 7,200 |
| **2,400 (proposed default)** | **1.9 pp** | **1.3 pp** | **14,400** |
| 4,800 | 1.4 pp | 0.9 pp | 28,800 |

> **`N` — PROPOSED at 2,400 pairs per card**, the parent's registered value:
> 2,400 runs on each of six arms, 14,400 runs total. **[USER] confirms or
> moves it.**

**A note the parent could not have written.** The parent's §7.1 declined to
register the optimistic column for the card-versus-filler contrast on the
grounds that the correlation between two treated arms was unknown; §13.5
recorded that this refusal *"was correct as discipline and wrong as a guess"* —
the filler contrast resolved best (`d ≈ 0.051–0.092`). **This packet still
registers only the conservative figure**, 1.9 pp at `N = 2,400`, because the
realised `d` in that table is a `P6` observation and `P7` may move it. Quoting
a `P6` discordant rate as this packet's sizing assumption would be exactly the
cross-stamp borrowing §4 forbids.

**`N` is fixed at countersign and may not be extended after a read.** Adding
runs because an interval "almost" excluded a threshold is optional stopping;
S4 is the only path from a null to more data, and it goes back through [USER].

> **COST CEILING — [USER] slot. PROPOSED at 4 hours wall-clock,
> stop-and-report**, the parent's value. The parent's actual run took **2
> minutes 57 seconds** for the full 14,400 runs, so the ceiling was never
> approached; it is retained as discipline, not as a live constraint.

Stop-and-report means what it says: if the sweep is still running at the
ceiling it stops and reports what it has, the partial result is graded as
partial, the arms that finished are not promoted to the whole answer, and any
grade drawn from fewer than the registered `N` quotes its own realised MDE.

---

## 8. Predictions — **BLANK. [USER]'s, before any number is read**

Per EXPERIMENTS (*"pre-registered from design intent … never revised against
the playtest that grades it"*) and the R121 precedent that predictions are
authored design-side and appended **as their own commit before any measurement
runs**. **Drafting them here would be the retro-fit that authority forbids, so
the cells below are empty.**

For **each** arm, [USER] states a direction and a threshold for **both**
co-primaries — an ungraded co-primary is just a number nobody committed to.

| card | §6.1 sign of Δ vs control | threshold (pp) that counts as a real move | §6.1b sign of Δ vs filler | confidence |
|---|---|---|---|---|
| `friendly_visit` | **[USER]** | **[USER]** | **[USER]** | **[USER]** |
| `study_buddy` | **[USER]** | **[USER]** | **[USER]** | **[USER]** |
| `borrowed_brilliance` | **[USER]** | **[USER]** | **[USER]** | **[USER]** |
| `elemental_ecstasy` ("Sweet Dreams") | **[USER]** | **[USER]** | **[USER]** | **[USER]** |
| `kaboom` (filler, negative control) | **[USER]** | **[USER]** | — (it is the baseline) | **[USER]** |

**Q4 slot — `borrowed_brilliance` bare-form play rate. [USER].** A direction
and a threshold for `played_when_drawn_rate` on the un-upgraded form. The
measured `P7` figure quoted by R180 is ~**6.1%** (60/981); that figure came
from a different read and is **not** a prediction, and [USER] may set the
threshold anywhere.

**A note for whoever transcribes [USER]'s words.** In the parent, [USER] wrote
directions against the control plus one statement about the filler, and the
filler column followed by arithmetic rather than by a second judgement — which
was recorded so a grader could see it was not an independent prediction scored
as a separate success. **If [USER] works the same way this time, record it the
same way.**

### 8.1 The redesign trigger — **[USER] slot**

The parent's trigger (§8.1 there) was: a card is a redesign candidate if
**either (a)** the filler-adjusted result is confidently below −2 pp — read as
the §6.1b interval's **upper** bound below −2 pp — **or (b)** the card performs
no better than filler (Δ vs filler ≤ 0) while its family-pooled
`dead_in_hand_rate` is ≥ 25%.

**It is reproduced here as context, not as a filled slot.** [USER] either
carries it forward verbatim, amends it, or writes a new one. Two constraints
apply to whatever is written:

- **A trigger must be expressible in §6's columns**, or it cannot be graded as
  registered. A trigger naming a quantity this sweep does not measure requires
  a new column in a re-registration — never a metric quietly added at grading
  time. (The parent's two clauses both are; anything new must be checked
  before the predictions are committed.)
- **The trigger names a candidate, not a verdict.** Firing it redesigns
  nothing. Whether to redesign, reprice or retire a card is a design act,
  downstream of the grade, and [USER]'s.

**One consequence worth naming before it is written.** If the trigger carries
forward unchanged and fires again for `borrowed_brilliance` under `P7`, R180's
"remeasure before any design act" condition is discharged and the design act
becomes available. If it does **not** fire under `P7`, that is the finding
R180 was asking for, and `borrowed_brilliance` needs no redesign. Both outcomes
are useful; neither is predicted here.

---

## 9. Grading procedure and stop conditions

**Blind.** The runner writes one report; grading compares it against §8's
committed table **without editing §8**. The predictions commit must exist
before the sweep is launched, and the sweep's report is not opened by the
author of the predictions before the grade is recorded.

**Order of operations:**
1. Countersign this packet. **OPEN — [USER], QUEUE `M17`.**
2. Confirm the §10 engineering prerequisites still hold at the new stamp,
   suite green. (They are built; §10 is a re-verification, not a rebuild.)
3. [USER] fills the §7 `N` and cost ceiling.
4. §8's predictions are committed — **their own commit, nothing else in it.**
5. Run the sweep at the pinned stamp. Report only; read nothing into it.
6. Blind grade against §8; the grade is its own commit.
7. Any design act is downstream of the grade and is [USER]'s.

**Order of reading, at the grade** — this order and no other, because reading
them in any other order lets one number colour the next:

1. The **compliance census** (§6.3), per card. If a card's assignment did not
   survive, or the control arm drafted it constantly, that card's grade is
   settled here as *underpowered by contamination* and its deltas are not
   graded at all (S4).
2. The **filler's §6.1 row** — the size of pure dilution in this cell.
3. Each card's **§6.1** delta against control, versus its §8 prediction.
4. Each card's **§6.1b** delta against filler, versus its §8 prediction.
5. The §6.2 secondaries, the §6.4 subgroup and the §6.5 card-flow columns, as
   description — **including the Q4 bare-form line.**

A card is graded **PREDICTED** only if both co-primaries land as §8 said they
would. One right and one wrong is **SPLIT**, with which half went wrong named —
not rounded to whichever half agreed.

**Stop conditions / tripwires — the run stops and re-registers if:**

- **S1.** Any of `RT/D/P/C` differs at launch from **`RT10/D14/P7/C9`**.
- **S2.** The `force_cards=None` byte-identity pin fails — the control arm is
  then not an anchor and nothing in the report is comparable to the roster
  table.
- **S3.** The staged `EB-43` / **`DRAFTER 15`** change has landed. The R121
  order places D15 at step (5), after blind-first grading of the payoff-reach
  sprint; a sweep run across that landing is a sweep run in two worlds.
  (`EB-43` = `D15` is registered law. **`EB-28` = `D16` and `EB-32` = `P8` are
  plausible inference and are NOT registered law** — R180 says so explicitly,
  and this tripwire does not silently extend to them.)
- **S4.** Compliance (§6.3) collapses — the forced copy fails to survive to the
  final deck in a large share of runs, or the control arm's natural acquisition
  is so common that ITT cannot separate the arms. The grade is recorded as
  **underpowered by contamination, not null**, and any re-run is a new
  registration.
- **S5.** A null read at the registered `N` is graded as **"no move larger than
  the §7 MDE"** — never as "no effect". The MDE is quoted with it, and §6.1b
  quotes the conservative 1.9 pp figure at `N = 2,400`.
- **S6 (new here).** **The `elemental_ecstasy` redesign lands after this packet
  is countersigned but before it runs.** That is a `CONSTANTS_VERSION` bump, so
  S1 catches it mechanically; S6 exists to name the expected case rather than
  leave it to be discovered as a surprise. The remedy is a re-stamp of §3 and a
  fresh look at §8's `elemental_ecstasy` row, because the prediction would have
  been written about a different card.

### 9.1 Sequencing — when this may run

**This sweep does not run during the payoff-reach freeze window unless the
world is identical to the one it is registered against.**

The registered experiment order, per the approved **settle-first** plan
(`payoff-reach-reregistration.md` §6.6 P12; EXPERIMENTS, Active registrations):

1. The open `RT`/`C` window lands — `M14`'s batch (`EB-70`, the `EB-82`
   conversion, the `EB-85` batch, `EB-69`) — and a dependency re-check passes.
2. The payoff-reach registration re-stamps its §6 **if the world moved**, then
   the freeze begins: **no `RT`/`D`/`P`/`C` bump lands on the sprint's branch
   until its graded read.**
3. The payoff-reach sprint runs under the pinned `D14`, and is graded
   blind-first.
4. **This sweep runs after that**, at whatever `RT/D/P/C` is live at that
   moment — which must be re-verified against §3 and is an S1 event if it
   differs.
5. Then the staged `EB-43` / D15 lands with its re-baseline (R121 step 5). This
   sweep must be graded before that, or S3 fires.

**Why this ordering and not the reverse.** Both registrations are pinned at
`D14`; both want one world for the duration; and R180 states the `P7` remeasure
*"slots in after payoff-reach under the pinned D14 — that ordering is the
experiment order"*. This packet does not propose changing it.

**The interaction with the redesign, in one line.** If [USER] chooses
redesign-first (companion packet §6, Route 2), the redesign is a `C` bump and
therefore cannot land inside the freeze either — it lands before the freeze
begins or after the payoff-reach graded read, and this packet is re-stamped to
`C10` before it runs.

---

## 10. Engineering prerequisites — built, re-verification owed

All of the parent's five prerequisites are **already built and in the tree**;
nothing new is owed. What is owed before step (5) is a **re-verification at the
new stamp**, not a rebuild:

1. `force_cards` on `model.run_one` / `run_many` / `_setup_run` / `Cell`,
   applied at the end of `_setup_run`, default `None` — **built**.
2. The `force_cards=None` byte-identity test (the precondition for S2) —
   **built**, and it must pass at `RT10/D14/P7/C9`, not merely at `RT9/.../C8`.
3. The forced-id-present + run-start-RNG-unchanged test — **built**.
4. `tier05/exp_eb17p_forced_copy.py`, the sweep script — **built**; it takes
   `--runs`, `--jobs` and the `--smoke` flag that moves every arm onto the
   §4-excluded seed base and prints a banner saying nothing below it may be
   quoted. **The script is reused as-is; no arm, column or default is edited
   for this packet.** Only the cell name and the stamp differ, and both come
   from the live world.
5. Pairing helpers (`mcnemar_exact`, paired bootstrap) in `tier05/stats.py` —
   **built**.

**Re-verification checklist for step (2):** run the full suite green; confirm
the byte-identity test passes at the pinned stamp; confirm
`tier05/tests/test_eb17p_force_cards.py`'s `kaboom`-in-starter pin still holds
after the `C9` X7/X8 rarity promotions (the promotions moved Commons to
Uncommons and did not touch Klee's starter, so this is expected to pass — it is
listed because "expected to pass" is not "checked").

---

## 11. Known limits, declared

- **ITT, not per-protocol.** A removed or upgraded copy stays in its assigned
  arm; assignment is at run start and compliance is measured, never enforced.
- **Deck dilution is confounded with the card** without the filler arm; with
  it, dilution is measured, not assumed away.
- **One cell.** `klee/reaction`, `assigned`, `hunter`, realistic. Nothing here
  generalises to another plan, another route, or the adaptive policy.
- **One seat.** The sim models one seat; nothing about co-op is measurable here.
- **The filler contrast is unanchored.** Both of its arms are treated, so a
  §6.1b delta may not be set beside any archived winrate.
- **Two copies look alike.** When a treated run ends holding two copies of the
  swept family, nothing distinguishes the forced copy from a drafted one; §6.3's
  columns are counts of the **family**, and are labelled that way in the output.
- **No cross-stamp comparison.** Nothing in this packet's output may be
  differenced against `EB-17p` §13. The two reads describe two worlds. Where
  this packet's grade wants to say "it moved", the honest sentence is "the
  earlier world read X, this world reads Y", with both stamps printed.
- **`P7` is not validated by this sweep.** This measures cards under `P7`; it
  does not test whether `P7`'s valuation is *right*. That is a different
  question and would be a different registration.

---

## Countersign line — one word, [USER]: COUNTERSIGN / REVISE / DECLINE

`________`

**Slots open at this draft:** §7 `N`, §7 cost ceiling, §8's full prediction
table including the Q4 slot, and §8.1's trigger. **The packet is NOT cleared to
launch and no seed in the registered range may be run.**

— drafted 2026-08-13 on branch `overnight-burn-2026-08-12`, per QUEUE `M17` /
R180. Zero design authority exercised: every threshold, direction and taste
call is [USER]'s. The frozen `EB-17p` registration and results file were read
and not edited (R101b).
