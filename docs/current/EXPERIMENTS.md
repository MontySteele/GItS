# EXPERIMENTS

Standing measurement law, plus pointers to the active registrations. The
registration packets themselves live under `review/active/` — one home, not two.

## Measurement law

### Stamp law
- **Every published number is world-stamped, and worlds are not comparable.**
  `RUNTEMPLATE`, `DRAFTER_VERSION`, and `POLICY` bumps archive their
  predecessors; check the stamp before quoting anything (R68).
- Run experiments through a `Cell` (`tier05/cells.py`) — it carries the stamp a
  report needs to be citable. **A report without a stamp is not citable.**
- **Frozen calibration surfaces must not be retuned.** The encounter battery,
  the pilots' `block: 1.2`, and `understudy/policy_v0.py` are frozen; editing one
  retroactively moves every archived number measured against it.

### Instrument visibility — one variable per window (D4)
- A prediction must **name the instrument that can SEE the changed object**, and
  confirm it can. The sim is one-seat; a C#-only change never gets a sim
  prediction; `support` is never linted because no instrument sees it.
- Change one variable per measurement window **where a causal answer will
  actually change the next decision** (R207). The drafter/constants version is
  part of the variable set — a scorer change **is** a version bump in the same
  edit (`DRAFTER_VERSION` in `tier0/constants.py`). Where nothing turns on
  attributing a movement to one edit, several variables may share a window; the
  stamp then labels the world, and a number taken in it is attributable to the
  window rather than to any one edit inside it. **The null-scratch call is
  Claude's, disclosed (R212):** where the scratch read is null — no interval
  separation on any arm — Claude shares the window without asking, and the row
  and the PR text carry the scratch hash and that null read.
- **A published standing baseline is spent where it buys something, not owed at
  every bump (R207).** A **standing table** is published at a meaningful product
  milestone, or when a pending decision needs one. Intermediate attribution
  comes from **commit-hash scratch comparisons** — build a throwaway world at
  one commit, read it, compare it against another commit, and publish neither.
  **Its honest limit is that a scratch comparison is not citable the way a
  stamped baseline is:** scratch worlds are never pushed, so a scratch read
  cannot be re-read later without rebuilding the world it was taken in. Nothing
  here relaxes stamping or citability — see *Versioning* below — and every
  already-registered read stands as registered.
- **An engine legality fix is absorbed at the next planned bump, not
  re-baselined on its own ([USER], 2026-08-30, on `EB-182`).** `EB-182`
  made a priced `choose_one` mode unofferable when the bank cannot pay it;
  shipped `deep_breath`'s second mode used to overdraw Encore into HP and
  now is simply not offered below 3 Encore, which moves tier 0.5 numbers for
  any arm holding the card. None of the four stamps names an engine rule, so
  no stamp moved; published numbers stand (R101b); the next planned
  `RT/D/P/C` bump carries the re-baseline that absorbs it, and until then a
  read of an arm holding `deep_breath` says which side of the fix it is on.

### Versioning
- **Version stamps are mandatory exactly as before (R207 left this untouched):**
  any change to a published-world variable bumps its stamp, and a report without
  a stamp is not citable. What R207 relaxed is when a **standing baseline** is
  published, not when a stamp is bumped.
- The run-cell stamp is `RT/D/P/C`, read live via `tier05/cells.py`:
  `RUNTEMPLATE_VERSION`, `DRAFTER_VERSION`, `CONSTANTS_VERSION` in
  `tier0/constants.py`, and `POLICY_VERSION` in `tier05/draft.py`. The
  scorecard's `A6_INSTRUMENT_VERSION` lives separately in `tier0/harness/axes.py`
  and is not part of the run-cell stamp. v1 and v2 A6 numbers are discontinuous
  and must never be compared unlabeled.

### Pre-registration + blind grading
- A measurement that a playtest will grade is **pre-registered from design
  intent**, with its contamination stated, and **never revised against the
  playtest that grades it** (D5 — the Kokomi stability band, which lands DARK,
  `band = None`).
- **Prediction slates are DRAFTED by Claude (R212)** from written design intent
  and committed as their own commit, labelled DRAFTED, **before any seed run**;
  [USER] countersigns in batch, or vetoes within five days. Pre-registration
  holds on commit-before-run, not on authorship. The grade still goes in blind.
- **Countersign once — restamp-and-hold is abolished (R212).** The packet's own
  world-check refuses to run on a moved world. A moved world means re-drafting
  the affected slots and disclosing the diff in the row; it never means
  re-signing an already-countersigned slate.

### The blind-QA funnel — the seat control, and stopping early (R221)

Two rules that reach the staged-turn funnel only (`understudy/staged_turn.py`,
`understudy/local_tester.py`), and neither one reaches a sim measurement. Both
were written because a round of that funnel is expensive in the two scarcest
things the house has — game time and model time — and neither is spent well by
a phase order that leaves the game idle while a model reads.

**R221 A — the fresh-Opus control form is a CALIBRATION ARM and it has an
end.** Every packet in this funnel is read twice: once by the local tester seat
(`understudy/local_tester.py`) and once by a fresh Opus grader with no repo
access and the packet inline. The second read exists to answer ONE question —
does the local seat read a board the way a frontier reader reads it? — and that
is a calibration question, not a standing chair. **The control retires to the
spot-check rate** — the same `turn 1 and every Nth after it` cadence
`--seat-spot-check` already runs the Codex seat at (R220 G, `N = 4`) — **on the
criterion R222 B fixes (ex-QUEUE `M62`), and on no other ground.** Until that
criterion is met the control rides every packet of every round. Three clauses go
with it:

- **It never retires mid-round.** The round that meets the criterion is graded
  whole with the control still on. Retirement takes effect from the NEXT
  round's plan, which is committed before any board of that round is staged.
- **Agreement is counted per TURN, on the verdict** — the local seat's verdict
  and the control's verdict on the same packet, SURVIVES against SURVIVES or
  REFUSED against REFUSED. It is not a prose comparison and does not pretend to
  be one.
- **It is reversible on the same rule.** A later round whose agreement falls
  back below the criterion puts the control back on from the following round.
  A retired control is a rate, not a deletion.

The first calibration round is **`KLEESPARK-R1`** (2026-08-29): verdict
agreement **4 of 8**, with five `intent_insensitive` refusals from the local
seat, one `misread`, and two replay lines the bridge refused for a null target.
The Codex pair read returned the tester seat itself. **The control therefore
STANDS.**

**R222 B — the roles invert for the local seat, and `M62` is answered.** Under
R221 A the fresh-Opus form was the CONTROL and the local seat was the tester.
`KLEESPARK-R1` returned the seat, so from R222 the two swap for the local seat
and for it only: **the fresh-Opus form DECIDES — its verdict is the graded
one — and the local seat reads in SHADOW.** A shadow form is **RECORDED and
NEVER GRADED**: it is filed with the round's records, it does not enter a
tally, it decides nothing, and **it is never replayed** unless a pick says so
in so many words. Nothing else about R221 A moves — the control does not retire
mid-round, agreement is still counted per TURN on the VERDICT, and the rule is
still reversible — and **the shadow forms are what that per-turn agreement is
now counted on**: the seat's shadow verdict against the deciding fresh-Opus
verdict, packet by packet.

The seat comes back as a DECIDING tester when **both** halves of `M62`'s answer
are met, and not on either alone: the criterion **≥ 6/8 verdict agreement over
one round**, AND a **requalification battery covering target selection, printed
costs, and intent sensitivity** — because fixing `target: null` alone does not
address the semantic failures the round found. The mechanical half of the fault
is BACKLOG `EB-203`. `M62` and `M63` leave the QUEUE on this ruling.

**R223 — the battery's PASS MARK, per category and never a total.** [USER],
2026-08-29: *"targets 6/6, others >= 4/6 works for me"*. The battery half of
R222 B is therefore met at **targets 6 of 6, costs 4 of 6, intent 4 of 6, and
all three must hold**. There is no total to trade against: a seat may not buy
back the blind spot that returned it (targets, `EB-203`) with the two
categories it still reads, which a 15-of-18 total would have let it do. The
mark lives in `understudy/battery/battery.yaml`'s `threshold:` block, beside
the boards it grades; `local_tester qualify` applies it, prints PASS/FAIL per
category and overall, and **exits 0 on PASS and 1 on FAIL**. The seat's first
live requalification — 10 of 18, targets 2, costs 5, intent 3 — reads **FAIL**
under it, on targets and on intent.

**R222 C — the funnel REFUSES a bad form and never repairs one** (`M63`'s
default, taken). A form that fails the pre-seal check is refused whole; no
field of it is rewritten, not even a mechanical one, and nothing is re-read on
a repaired copy. Editing a grader's answer is editing the measurement, and the
funnel does not do it.

**R221 B — sequential stopping: a round may stop early, and what it stops is
which boards are RUN.** The rule is part of the registration and is fixed
before any board is staged; it may not be chosen, loosened or tightened once a
grade is in.

- **A round stages its boards in a PRE-REGISTERED ORDER.** The order is the
  smallest set of boards whose predictions cover every registered slot at least
  twice, first — ties broken by closeness score, the closer decision first —
  and the remaining boards after it, by the same rule. `--first N` says how
  many of that order the round runs before it stops to look; the default is
  **4**, raised automatically where the twice-over cover needs more.
- **After the first set is graded and replayed, each slot is read once.** A
  slot is **DECIDED** when it carries **two or more grades that all agree** —
  all PREDICTED, or all MISSED. **Any SPLIT, or fewer than two grades, leaves
  it UNDECIDED.** A refusal is a grade like any other; an unrun board
  contributes none.
- **The remaining boards run only if they carry an UNDECIDED slot.** Every
  other board is recorded **UNRUN** — in `review/qa/ledger.tsv` and in the
  packet's results section — **with its seed still pinned**, so a later round
  runs exactly that board rather than a re-rolled one.
- **Stopping never changes a grade.** It changes only which boards are run.
  Nothing already graded is re-read, re-scored or withdrawn, and a slot that
  reads DECIDED off two agreeing grades is not thereby better evidence than two
  agreeing grades — it is exactly two agreeing grades, which is what the
  packet reports.

**Checked against the standing law, and it holds.** *Blind grading* is
untouched: the stopping rule reads VERDICTS, which are `staged_turn grade`'s
mechanical output, and it never reads a form before that form is graded — the
reader is blind at read time either way. *R101b* is untouched: nothing already
published is re-read or rewritten, and an UNRUN board is a board with no record
rather than a struck one. *Pre-registration* is satisfied because the order,
the `N`, and the decided rule are all committed with the round's plan
(`local_tester round --plan-only`) before the first stage, which is the same
commit-before-run discipline a prediction slate carries. *Guardrail-7* is
unaffected: a stopped round produces fewer diagnostic replays, and a replay was
never a comparison or a balance reading to begin with. The one honest cost is
**power**, and it is named rather than hidden: a slot decided on two agreeing
grades has two, and a round that ran every board would have had more. That is
the trade [USER] authorised — *"makes sense, only run the rest if needed"* —
and the ledger prints the UNRUN rows so the trade is visible in the record.

### Decision linkage (R206)
- **Every registration names the DECISION each outcome would change** — slot by
  slot, in the packet, before the run. A prediction with no decision attached to
  its outcomes is not registered.
- **If every plausible outcome leaves the next action unchanged, the experiment
  is not run.** An interesting number is not a reason; the reason is the act the
  number selects between. This reaches registrations only — a sweep is
  engineering tuning and is governed below.

### What registration law does NOT reach: engineering tuning
- A **sweep** is not a registered experiment and is not blind-graded — there is
  no prediction to grade, and nothing above reaches it. Three rules underneath
  that law carry over verbatim, and a sweep that skips them is not citable.
  **(1) Stamp law (R68):** every printed row carries its cell's `RT/D/P/C`; a
  sweep taken across a bump is two sweeps, and an unstamped row cannot say
  which. **(2) The dead-knob gate (R67, with R33):** a swept knob nothing READ
  produces a flat table indistinguishable from "the knob does not matter", so
  the point is refused rather than printed — and the gate may not be satisfied
  by adding a read. **(3) Look-first:** rows print in GRID ORDER, never sorted
  by outcome, and the adoption rule is fixed before any row is read, because
  picking the grid maximum of a noisy sweep afterwards is the forking-paths
  defect with extra steps. `tier05/sweeps.py` covers the `constants.py` knobs
  and `tier05/pilot_weight_sweep.py` the pilot weights filed outside it; both
  write their expected outcome down in advance, since a null that was predicted
  is a result and a null that was not is an unfalsifiable instrument. **`W4`
  finding, `P11` (2026-08-26):** making the scorer payout-aware puts `_score`
  through `exhaust_future_value`, so `discover_scope` reclassified all four
  exhaust-gate weights `pair_own` → `shared` and that gate now has **no
  sweepable surface left** — whether to sweep a shared weight anyway is
  [USER]'s call, not an integration's.

## Graded

The published record. A graded registration stands as published and is never
re-read against a later world or a later ruling (R101b); its packet and its raw
results file stay in `review/active/`, unedited. The narrative each entry
carried while it was active is in the commit message that retired it.

| Registration | Graded | Cell | Grade | Record |
|---|---|---|---|---|
| `EB-17p` force-first-copy paired winrate | 2026-08-10 | `RT9/D14/P6/C8` | 3 PREDICTED / 1 SPLIT / 1 MISS (`borrowed_brilliance`, wrong sign). §8.1's redesign trigger fired for `borrowed_brilliance` and `elemental_ecstasy`; R180 split them | packet `review/active/eb17p-registration-draft-2026-08-08.md` §13, §13.8; raw `review/active/eb17p-results-2026-08-10.txt` |
| payoff-reach re-registration (the `RARITY_ODDS` fence) | 2026-08-24 | `RT12/D14/P7/C11` | `P5`: 0 PREDICTED / 0 SPLIT / **9 MISS**, every arm ABOVE its window on both axes. Q-A SPLIT, Q-B SPLIT. Tripwires `T1`–`T4` all silent. The design call it raised was `M37`, ruled the same day (R199) | packet `review/active/payoff-reach-reregistration.md` §7–§8; raw `review/active/payoff-reach-results-2026-08-24.txt` |
| force-first-copy re-registered under `P7` (`M17`) | 2026-08-26 | `RT12/D17/P10/C19` | 4 PREDICTED / 1 SPLIT / 0 MISS; `Q4` PREDICTED on both halves (bare-form play rate 5.99%). §8.1's redesign trigger silent for **every** card — for `elemental_ecstasy` by 0.17 pp, on a delta whose sign is not established at that `N`. `C2` landed at Block 5, `a49bf20` | packet `review/active/m17-sweep-reregistration-p7-2026-08-13.md` §12; raw `review/active/m17-sweep-results-2026-08-26.txt` |
| shop companion channel re-run (`S4-G10`) | 2026-08-26 | `RT12/D17/P10/C19` | 2 PREDICTED / 1 SPLIT / 2 MISS over 6,000 runs. The redesign trigger FIRED on condition 4 alone, mean winrate Δ −0.07 pp; conditions 1–3 did not. The design call it raised is open at QUEUE `M14` | packet `review/active/shop-rerun-registration-2026-08-10.md` §8; raw `review/active/shop-rerun-results-2026-08-26.txt` |
| `KLEESPARK-R1` the Sparks arm on a live board | 2026-08-29 | dev build `0.2.1481+proto`, world `main` @ `d974303` | 2 PREDICTED (`P3`, `P6`) / 2 SPLIT (`P2`, `P4`) / 2 MISS (`P1`, `P5`). `P1`'s registered decision FIRED and PICK 4 is reopened; `P5`'s FIRED and the pilot's Spark probe needs playability before any further sim reading. `P2` and `P4` each have one half the instrument could not reach — no badge on a packet, and no dry-sink board without the generator — so PICK 8 and PICK 1 both stay open. Pair read: 6 ADVANCE / 2 RETURN / 0 ESCALATE, arm ADVANCE, and a RETURN on the LOCAL tester seat's first live use. **ERRATUM 2026-08-29 (relayed review, packet §11.5): both MISSES carry an instrument correction and NEITHER grade is re-graded (R101b).** `P1`'s threshold of 4 was unreachable — only three of the eight boards could pose the question (`t07`'s bank of 4 pays both its sinks), so the MISS cannot establish that the tight set is thin, and whether its decision-fire stands is CONTESTED and on the pick list; the instrument defect is `EB-202`. `P5`'s per-turn spend rate is confounded by fight length (294 vs 243 turns) and by income (the arm converts four generators out of the deck, so gains fall 276 → 235 by construction); normalized, ON spent 90.6% of generated against OFF's 88.0%, and `P5`'s registered decision fires unchanged. **ANSWERED by R222 (2026-08-29), packet §11.7:** `P1`'s MISS stands as an audit record and is an instrument defect (`EB-202`), NOT a trigger — PICK 4 is not reopened and the set is left intact for whole-fight play. **The arm's next registration precondition:** whole-fight Codex play on the Sparks arm runs FIRST, and only then may a minimal repaired staged round be registered — dry sinks with no generator in hand, and a genuinely multi-enemy AoE board. **`P5`'s rerun metrics-to-be, registered now:** `spent / available Sparks` and `affordable sinks skipped` per turn, replacing the confounded raw per-turn spend rate; the rerun waits on pilot playability and carries no repricing from the 40-versus-25 figure | packet `review/active/klee-sparks-2026-08-29.md` §11; raw `review/active/klee-sparks-r1-sim-2026-08-29.txt`, forms and replays under `review/qa/klee-sparks-r1-t0*/`, pair read `review/qa/klee-sparks-r1-pair-review-codex-gpt-5.6-sol.md` |
| `KLEESPARK-W1` the Sparks arm across a WHOLE FIGHT | 2026-08-29 | dev build `0.2.1517+proto.dirty`, game `v0.111.0`, seed `21H4Y89QDRP6`, six priced rows granted into the starting deck | 1 PREDICTED (`W2`, on its boundary at 0.50) / 1 SPLIT (`W4`, on its boundary at 50.0%) / 2 MISS (`W1` = 0 named trade-offs, `W3` = 0 affordable sinks skipped). The bank never once held two affordable uses, so the decision the arm exists to create did not occur and was never declined — yet the tester named the spend-versus-hold tension unprompted in its run record. Legible as a shape, inert as a decision. `W1`'s and `W3`'s registered decisions FIRE: the minimal repaired staged round of 7(c) is warranted and needs the three boards at §12.9 pick 2. Two non-slot findings: a defect candidate on `Bang Bang!`'s price, and Kokomi's Bake-Kurage panel rendering on a Klee run | packet `review/active/klee-sparks-2026-08-29.md` §12; records, pages, grader and grades under `review/qa/klee-sparks-wholefight-1/`; house record `review/qa/blindplay/kleespark-w1/record.md` |
| `KLEESPARK-R2` R222 D's minimal repaired staged round | 2026-08-29 | dev build `0.2.1517+proto.dirty`, game `v0.111.0`, world `main` @ `712c75e` | **3 PREDICTED (`P1`, `P2`, `P5`) / 0 SPLIT / 0 MISS / 2 UNREACHED (`P3`, `P4`)**. `P1` — the re-posed spend-versus-hold slot, asked at a threshold of 2 against a ceiling of 3 — came in **3 of 3**: every `S1` board's deciding form named a DIFFERENT Spark-priced card as its second line. **ERRATUM 2026-08-29 (relayed review; packet §13.1): the grade STANDS and is NOT re-graded (R101b), its LABEL is superseded.** Neither `S1`'s registered predicate nor `P1`'s grading predicate asks for a hold — both ask for a choice BETWEEN SINKS. On `t01` both candidate lines spend all three Sparks; `t04` says the turn *"did not present me with a decision — it presented me with a sum"*; `t06`'s two candidates are both priced 2 and the AoE dominates. No affordable sink was deliberately skipped on any board. `P1` therefore reads **alternative sinks are legible, 3 of 3**, and it does not overturn `KLEESPARK-W1`'s whole-fight `W1` = 0 and `W3` = 0. **Disclosure, same review:** the DECIDING reader was fresh Opus and all eight Spark rows are `authored_by: [claude]`, so this round's deciding read is SAME-FAMILY with the author — operationally authorised by R222 B, and NOT author-disjoint under R217 C. What that should cost a round is QUEUE `M64`; nothing here is re-graded on it. `P2` — the dry sink with no generator anywhere in hand, which `KLEESPARK-R1` could not stage — came in **2 of 2**, with no reader on any board calling a priced card free or affordable. `P5` PREDICTED at **3 of 5** shadow-versus-deciding verdict agreement on the first set (3 of 6 over the round), below `M62`'s ≥ 6/8 bar, so the local seat stays in the SHADOW chair. **Both UNREACHED slots are instrument findings, not readings about the cards.** `P3`: one of its two three-body boards drew ONE enemy — a seed recorded three-body on six earlier KOKOMI stagings gave Klee one body — and a board that cannot be asked is UNREACHED by the slate's own rule; `EB-208` is the defect, because `EB-202`'s ceiling is computed off the DECLARED board and no check in the funnel can see the gap. `P4`: its dedicated board `t03` posed the question and its form was then REFUSED for `intent_insensitive`, and a refused form is not replayed, so the slot's own denominator produced no replay — **absence of a counterexample is not PREDICTED**. **ANSWERED OUT OF SLOT and recorded as such:** `t01`'s live replay paid Bang Bang!'s printed 2 off a bank of exactly 2 (bank 3 → Fwoosh! → 2 → Bang Bang! → 0; Seapunk 45 → 20, a fall of exactly 7 + 8 + 5 + 5) with no Bomb on the board, so §12.8 item 1's candidate — *"Bang Bang! may be charging 1 for a printed 2"* — is explained by the whole fight's detonation and there is no pricing defect. That evidence does NOT move `P4`, which stays UNREACHED as published. Pair read: **3 ADVANCE / 2 RETURN / 0 ESCALATE, overall RETURN — on the INSTRUMENT, not on the arm's design**. **Second finding, `EB-209`:** in the shadow chair R221 B's stopping rule reads SHADOW grades, because the deciding forms do not exist while the round runs; it changed nothing here (all four slots UNDECIDED, all six boards run, zero UNRUN) and could stop a later round on a reading that decides nothing. **`--lanes 2` was attempted first and FAILED**: lane 1 asked for `NMQLUYZDLV` and the run read back lane 0's `R7W86HG7WHUD`, so `t04` was refused by `seed_not_honoured` and the round stopped at its second board; the round was re-run whole on one lane and nothing was carried over. **R221's timing claim gets its first number** (§13.5): 372 s wall clock for six boards — stage 89 s, read+grade 295 s, replay 124 s over three surviving lines — so the pipeline hid ~73 s of the 89 s of game-bound work, about 16% of the round, because a read is ~3× a stage and the round is model-bound. Codex budget spent: **3 calls** (two spot-check seat reads, one pair read). Three picks at §13.6 — **all three ANSWERED by R224 (2026-08-30), and NOTHING in this row is re-graded**: item 1 (`EB-208`'s fix shape) = **(c) sequenced behind (a)** — the live-count preflight first, the character/build/context-keyed seed ledger when a Klee three-body seed hunt happens; item 2 (`P4`) = **(a)**, so §12.8 item 1 stays an out-of-slot observation, `P4` stays **UNREACHED as published** (R101b) and the arithmetic question closes; item 3 (the next gate) = **(e)** — accept `P2` as the round's answer, record `P1` only as *"alternative sinks are legible"* and not as a spend-versus-hold result (the §13.1 erratum), take no top-up round, and resolve the two open questions about the SINK SET before the arm advances unchanged | packet `review/active/klee-sparks-2026-08-29.md` §13; slate and boards `understudy/turns/klee-sparks-r2/` (`MANIFEST.md`, `slots.yaml`); forms, verdicts and replays under `review/qa/klee-sparks-r2-t0*/`; round summary `review/qa/klee-sparks-r2-round-summary.json`; pair read `review/qa/klee-sparks-r2-pair-review-codex-gpt-5.6-sol.md` and its prompt beside it |
| `KLEESPARK-W2` the mixed-pool whole fight | 2026-08-30 | dev build `0.2.1600+proto.dirty`, game `v0.111.0`, seed `488GKZJSHC34`, **eleven** rows granted into the starting deck | **0 PREDICTED / 0 SPLIT / 1 MISS (`W1'`) / 3 UNREACHED (`W2'`, `W3'`, `W4'`)**, plus `W5'` RECORDED and NOT GRADED. §14.4's proof, run on the deck option (5) built: the seven-rung prototype ladder, the three `EB-218` Spark-only twins (Set It Off, Dig In, Powder Smoke) and Rummage. `proto_true_spark_knight` was LEFT OUT on §12.2's published D4 grounds ~~and stays [USER]'s at §11.7 pick 3~~ (**ERRATUM 2026-08-30, relayed review, fact-checked — R101b: the exclusion STANDS, the disposition line is struck and nothing is re-graded.** §11.7 pick 3 was ANSWERED by R222 (`13a0537`) option (a), *"leave the Rare Power as built and re-read it in whole-fight play"*, so what is outstanding is that whole-fight read — engineering work, filed as `EB-223`, not an open decision). **`W1'` MISS on one number: the printed Spark bank never exceeded 1 across all twelve combat pages** — nine printed no Spark at all and three printed 1 — **against a cheapest non-damage price of 2.** Two priced titles were simultaneously affordable exactly once (`turn-009`, bank 1, Fwoosh! and Ka-pow!) and both are damage sinks, so even the qualifier-free count is 1 against a threshold of 3. The mixed pool was in hand and unreachable: Dig In on four consecutive pages at bank 0, Set It Off and Powder Smoke on three at bank 0–1, **Rummage never drawn**. `W2'` UNREACHED by its registered condition — no page ever showed a non-damage and a damage sink affordable at once, because no non-damage sink was ever affordable; `W3'` UNREACHED by §14.4 condition 1 (a hold prediction on a board that never offered a choice measures the generator), and its BARE detector is 0 as well, all three `end turn` pages carrying a bank of 0; `W4'` UNREACHED BY CONSTRUCTION as printed before the run (Powder Keg unbuilt, so option (5) put no redesigned card at price 3), with neither price-3 face ever bought. `W5'` = **6 of 8 plays, 75.0%**, against `W1`'s 50.0%. **`W1'`'s registered decision FIRES: the null is the GENERATOR's and not the sink set's, twice over on two different decks, and no re-price of §4.2's table may be taken off this run.** The run stopped at **17 of 40 funded actions** on `tool_blocked` at the SECOND Monster room's first frame — `W1`'s ending — so §14.4 condition 1's *capped batch* was funded and did not happen; **two whole-fight sessions in a row have now ended at the first frame after the first fight**. 21 Codex calls of a 45 cap; 2 grammar refusals, both recovered; leak audit 21 observations, 1 hit and it is `W1`'s known false positive. Two non-slot findings: the Spark-arithmetic candidate returns in a new place (`turn-009`/`turn-010` each printed bank 1 and each paid a printed 1, `turn-011` printed 0) with the same benign detonation explanation `KLEESPARK-R2` settled the `Bang Bang!` instance on, recorded as a candidate and not a defect; and **§12.8 item 2 is GONE** — zero of the 21 observations contain `Bake-Kurage`. Three picks at §16.11 | packet `review/active/klee-sparks-2026-08-29.md` §16; record, grader and grades under `review/qa/blindplay/kleespark-w2/` |
| `KURAGEMEM002` the Kurage-memory TEACHING PASS | 2026-08-30 | dev build `0.2.1627+proto.dirty`, game `v0.111.0`, world `kuragemem002-rerun` @ `10799139` (an integration of `eb214-muster-keyword` and `eb216-wire-snapshot`, neither on `main`), seed `KURAGEMEM002`, the Oath granted into the starting deck | **1 PREDICTED (`P3`) / 0 SPLIT / 0 MISS / 3 UNREACHED (`P1`, `P2`, `P4`)**, plus `P6` RECORDED AND NOT GRADED. Judgment **1 ADVANCE / 3 RETURN / 0 ESCALATE**. `P3` is the row's own acceptance and it came in **5 of 10 qualifying turns with 2 Musters** against a threshold of 3-with-1, where `KURAGEMEM001` read 0 of 10 with 0 of six Musters: `M54`(1)'s diagnosis — the failure was WORDING and not dose — **is carried on its own terms**, and `EB-214` CLOSES. The grader records one qualification that changes no verdict: the comprehension is **retrospective**, articulated in the run record as a regret rather than held before the first Muster, and `P3`'s threshold does not ask for the sacrifice-versus-recruit half to be priced at the moment of choosing. **The three UNREACHED are an INSTRUMENT finding and the display is not what returned.** The memory section was on 34 of the 60 observation pages and the blocked page printed both halves of `P4`'s question in full; what is missing is the QUESTION. `blindplay session`'s reply schema is two fields, `command` and `thinking`, so the tester writes the reason for the play it is making and **is never asked what the jellyfish will do next turn** — §13.5's own third record requirement is a requirement on the record that nothing enforces, and `KURAGEMEM001` met it by accident. Filed as `EB-229`. Under the slate's own rule an UNREACHED slot is not a pass and nothing is inferred from an absence, so **no registered decision fired and NO [USER] row opens**: §13.9.4's four-item pick list needs a `P3` RETURN, and its fifth item needs a `P4` half-(b) RETURN on the threshold rather than an UNREACHED. **`P5` and `P6` were NOT RE-POSED and their `KURAGEMEM001` grades stand as published (R101b)**; `P6`'s two advance statements (`turn-040`, `turn-064`) name what the memory will DO and never which body, and are filed unbladed for whoever registers `P6`'s own rerun. **First record to carry `EB-216`'s objective side**: 32 wire snapshots — 12 EMPTY, 12 FIRES-NEXT, 8 BLOCKED — handed to both graders and never to the tester. Codex budget spent **67 of a cap of 70**; the guard read `5h 41% / week 17%` before and `5h 6% / week 18%` after (the five-hour window rolled over mid-run) and never refused. Leak audit 66 observations, 1 hit, and it is `KURAGEMEM001`'s known false positive. The local seat's SHADOW read (SPLIT / SPLIT / MISS, 0 of 3 agreement) is recorded and decides nothing (R222 B). R225's soak gate read `fights=3 defects=0` before the run. Two undiagnosed tester observations: the end-of-turn pulse preview alternating between Block and damage (`KURAGEMEM001` said this too, on a display that did not touch that line), and a harness sequencing report that the fight-record prompt arrived before the Muster selection screens resolved | packet `review/active/kokomi-kurage-memory-2026-08-29.md` §13.9; sealed record, wire snapshots and meter ledger `review/qa/blindplay/20260830-083819/`; deciding read `review/qa/kuragemem002-pair-review-codex-gpt-5.6-sol.md`, `P3` read `review/qa/kuragemem002-p3-read-opus-5-fresh.md`, shadow `review/qa/kuragemem002-shadow-read-local-qwen3.md`, both prompts and the wire table beside them |
| `KLEESPARK-S1` the Spark arm measured DRAFTED, in the sim (`EB-205`) | 2026-08-30 | `RT12/D18/P11/C21`, cell `klee/demolition`, hunter, `assigned`, realistic, 600 runs, seed 11, `jobs=1` | **2 PREDICTED (`S1`, `S5`) / 0 SPLIT / 3 MISS (`S2`, `S3`, `S4`) / 0 UNREACHED.** R225 item 1's sim half: the shipped Klee pool under `SPARK_ALT_COST_ENABLED` — substituted starter, PICK 4's one-for-one pool substitutions, the three `EB-218` Spark-only twins, nothing granted or forced, `proto_true_spark_knight` excluded on §12.2's grounds as `W2` excluded it — against a paired flag-OFF control that is RECORDED and NOT GRADED. **`S1` PREDICTED and it is the finding: on a DRAFTED deck the per-fight peak Spark bank has a median of 5.0 and 90.7% of 8,428 fights peak at ≥ 2**, against `W2`'s printed ceiling of 1 on its granted deck — so **in the sim, income is not the governor**, and `W1'`'s null is a property of `W2`'s two-makers-to-eleven-sinks grant rather than of the one-for-one economy. `W1'` is NOT re-graded and stands as published (R101b). **`S2` (0.62% of 34,597 turns) and `S3` (3.2% of 600 decks) MISS as ONE finding, and §17.4 registered its reading before the run: a SCORER finding, not an income finding** — the drafter almost never TAKES the three migrated twins, so the destination was usually not in the deck at all and `S2`'s bank number is an offer number; it goes to `BACKLOG` as an instrument row and the live deck GRANTS its non-damage sinks. `S2`'s registered UNREACHED condition was `S3` exactly 0, and `S3` was 19, so the slot grades MISS as registered. **`S4` MISS on the branch §17.4 printed for it** — the ratio ROSE (medians 1.000 / 1.000 / **1.500** at floors 5 / 10 / 15) instead of falling, because under the flag a `gain_spark` is priced at `SPARK_ALT_VALUE` = 4.00 for the first time and the drafter can finally see a generator; the registered reading is that `W2`'s 2:11 was an artefact of granting and the drafted economy is generator-rich. **`S5` PREDICTED at 0 of 600: Rummage is UNREACHABLE BY DRAFT** (no `SPARK_ALT_POOL_SUBS` entry), so §14.4 condition 3's Rummage half must be GRANTED live. **What the LIVE controlled-ratio registration INHERITS is exactly one number — `1.500` makers per sink, `S4`'s floor-15 median, i.e. 3 : 2** — and nothing else: no re-price of §4.2's table, no new sink row (R225), no win rate or comparison (R215 B), no presentation claim. Two blind spots are printed with it: the maker count is a FLOOR on both arms, because §17.2's sheet-only definition cannot see `crackle`'s `discard_for_sparks` or — since **C21** (`EB-219`) — **Klee's kit Spark declaration**, which is where Prune's two printed `gain_spark` ops went; and the control's 0.000 medians are a scorer fact (`STATIC_SPARK_VALUE` = 0.0), which is why it is not graded. **STAMP DISCLOSURE (§17.5):** §17.3 declared C20, copied from a `STATE.md` Live cell that was stale at `HEAD`; the tree was C21 before the registration, during the run and after it, so the world did not move, the read is published stamped C21 where it was taken, and `STATE.md` is corrected as hygiene | packet `review/active/klee-sparks-2026-08-29.md` §17 (registration §17.1–§17.4, results §17.5–§17.7); record, raw JSON and unedited driver stdout under `review/qa/kleespark-s1/`; instrument `tier05/exp_klee_sparks_s1.py` |
| `KLEESPARK-W3` the live controlled-ratio whole fight (`EB-205`) | 2026-08-30 | dev build `0.2.1610+proto.dirty`, game `v0.111.0`, seed `LEA0X16MF2WQ`, **thirteen** cards granted into the starting deck | **1 PREDICTED (`W6''`) / 1 SPLIT (`W1''`) / 2 MISS (`W2''`, `W3''`) / 1 UNREACHED BY CONSTRUCTION (`W4''`)**, plus `W5''` RECORDED and NOT GRADED. R225 item 1's LIVE half, and the first whole-fight session that was a BATCH: **four fights, 19 combat pages, 40 of 40 funded actions, termination `max_actions`** — `EB-221` and `EB-222` are the difference from `W1`'s and `W2`'s two `tool_blocked` endings. The deck is DERIVED rather than picked: the sinks are the ones §14.4 condition 3 and R224 item 19 name (the three `EB-218` twins, Rummage — which `S5` proved undraftable — and the cheapest damage sink, which is the substituted starter's own Ka-pow!), five of them; times `S4`'s inherited **1.500** rounded UP because the inherited number is a FLOOR, that is eight makers — all six shipped `gain_spark` rows the arm's pool still offers plus a second Powder Pop. **8 : 5 = 1.600 against `W2`'s granted 2 : 11 = 0.182**, deck 23 against 21. **`W6''` PREDICTED and it is the finding: the median per-fight peak printed Spark bank is 4.0** (peaks 5 / 0 / 3 / 9) against a registered floor of 2, `W2`'s printed ceiling of 1 and `S1`'s sim median of 5.0, which was a comparator and never a threshold. **So income is not the governor on a representative deck on EITHER engine, `EB-205` is DISCHARGED, and Klee PICK 1 does NOT reopen** — the one registered condition that would have reopened it was a `W6''` MISS. `W1''` SPLIT at **1 of 19** combat pages (`turn-030`, bank 3, Ka-pow! and Dig In both affordable), whose registered act is a LONGER BATCH and not a new row. **`W2''` MISS and `W3''` MISS AUTHORISE NOTHING**: both MISS branches are written *"MISS with `W1''` PREDICTED"* and `W1''` is SPLIT, so no re-price of §4.2's table and no new sink row comes off this run — the choice was posed once and declined once (the tester took Ka-pow! for an exact 36-Bomb detonation), and `W3''`'s bare detector is 0. `W4''` UNREACHED as printed before the run; **Rummage was never played**. `W5''` = **6 of 15 plays, 40.0%**, against `W1`'s 50.0% and `W2`'s 75.0%. The controlled variable is CHECKED rather than assumed: the three cards added mid-run (Sucrose — Catalyst Conversion, Endless Fireworks off a potion, Eager to Help) carry no top-level `gain_spark` or `spend_spark`, so the deck read 8 : 5 on every page of every fight. Four operator actions are declared — `embark` left the run on **Neow**, which cannot be skipped and two of whose three boons rewrite the deck this registration controls, so the operator took the only deck-neutral option (Silken Tress) and advanced to the map — and `EB-191` fired (run seed read back `None`; re-read off the wire from the same process before the session started and written into the sidecar, or the record would have said `arms_granted: (none)` about thirteen granted cards). Three non-slot findings: **a printed face that disagreed with itself inside one run** — `All of My Treasures!` printed *4 damage* per Bomb on `turn-029` and *6* on `turn-037`, where the sheet and the body both say 6 and the differing frame faced a debuffing enemy, so `{Damage:diff()}` renders a live modifier the body does not read — recorded as a DEFECT CANDIDATE with an inferred mechanism, moving no grade; income helped by **two sources the ratio cannot count** (Pounding Surprise's +1 per detonation and Endless Fireworks' `spark_per_turn`), so `W6''` is a FLOOR and never a ceiling; and one whole fight (fight 2) ran at a bank of **zero**. **45 of 45 Codex calls**, meter 5h 3% → 41% and week 11% → 17% with `EB-227`'s guard never refusing; R225's soak gate passed first (`fights=3 defects=0`); leak audit 45 observations, 1 hit and it is `W1`'s known false positive | packet `review/active/klee-sparks-2026-08-29.md` §18 (registration §18.1–§18.5, results §18.6–§18.10); record, grader and grades under `review/qa/blindplay/kleespark-w3/` |
| `KLEESPARK-W4` the strict Rare Power's whole fight, and `W1''`'s longer batch (`EB-223`) | 2026-08-30 | dev build `0.2.1676+proto.dirty`, game `v0.111.0`, seed `KGU5LKM77PB5`, **fourteen** cards granted into the starting deck | **0 PREDICTED / 0 SPLIT / 1 MISS (`W1'''`) / 3 UNREACHED (`K1'''`, `K2'''`, `K3'''`)**, plus `K4'''` RECORDED and NOT GRADED. `EB-223`'s owed whole-fight read of `proto_true_spark_knight` and `W1''`'s registered longer batch, run as ONE session behind §19.1's pre/post-Power page partition. **The run's first fact is that the partition never happened: *Spark Knight's Oath* was DRAWN — in hand on seven combat pages — and NEVER PLAYED**, so there are 50 pre-Power pages, 0 post-Power pages, and every `K` slot grades UNREACHED by §19.4's own rule. §19.5 contamination 6 registered that outcome and its reading in advance, and under the slate's own rule an UNREACHED slot is not a pass and not a fail: **the ADVANCE-to-sheet candidate is neither reached nor refused, §5's wording and the price of 3 are NOT reopened** (the one registered reopening condition was a `K1'''` MISS on a NON-ZERO denominator, and the denominator is zero), and **no [USER] row opens on the Power**. The tester's own reason is recorded as R217 G iteration feedback and grades nothing: *"I would avoid narrow powers such as Spark Knight's Oath … the Oath repeatedly sat dead while costing too much tempo."* **`W1'''` MISS at 0 of 50 pre-Power combat pages** — a denominator of 50 against §19.4's ≥ 30 branch — against `W3`'s SPLIT at 1 of 19 on the same 8 : 5 = 1.600 deck. **Its registered decision FIRES: the choice is not posed at the inherited ratio even at double the batch, and it returns to [USER] as a numbered pick between §14.3's options** (packet §20.5, six options; no QUEUE row minted, one batch per sitting). The zero's mechanical shape is recorded with it: two priced titles were in hand together on only 4 of 50 pages, all four at a bank of 0, and **the deck's one printed damage sink, Ka-pow!, reached the hand on exactly one page in fifty**, while an affordable non-damage sink sat in hand on 9. `K4'''` records what no slot claims: per-fight peak printed banks **3 / 13 / 8 / 3 / 8 / 0, median 5.5** over six fights (beside `W3`'s 4.0, and NOT a comparison — §19.2 item 1), and an attack share of **15 of 39 successful plays, 38.5%**. **The batch happened**: six fights, 50 combat pages (7 / 6 / 8 / 14 / 11 / 4), **80 of 80 funded actions, termination `max_actions`, zero refusals and zero stalls**. The controlled variable is CHECKED, not assumed: of 22 distinct titles that reached the hand, every one carrying a top-level `gain_spark` or `spend_spark` is one of the twelve granted rows, so the ratio held at 1.600 on every page — while **Prune — Little Witch's Hunt**, drafted mid-run, mints Spark as a C21 kit declaration the maker count cannot see, so every income figure is a FLOOR. **86 Codex calls of a cap of 90**; the registered precondition read `5h 0% / week 18%` before (against ≤ 8% / ≤ 35%, so no cut cap) and `5h 40% / week 25%` after, with `EB-227`'s guard never refusing; R225's soak gate passed first (`bounded seed=V4823EVDU888 actions=51 fights=3 defects=0`); the pck contract check was empty AND the stop rule was checked — every printed Spark price matched the sheet on all 50 combat pages; `EB-191` did not fire; leak audit 86 observations, 1 hit and it is `W1`'s known false positive. Two operator actions, by §19.5's registered Neow rule: the boons were Nutritious Oyster / Neow's Talisman / Silver Crucible and the only deck-neutral one, **Nutritious Oyster**, was taken | packet `review/active/klee-sparks-2026-08-29.md` §20 (registration §19.1–§19.7, results §20.1–§20.5); record, wire snapshots, grader and grades under `review/qa/blindplay/kleespark-w4/` |
| `KLEESPARK-BT1` *Bag of Tricks* staged, graded and replayed (`EB-224`) | 2026-08-30 | dev build `0.2.1676+proto.dirty`, game `v0.111.0`, world `eb224-staging` @ `acb543b9` (the registration commit; not on `main`), four staged boards, seeds `JH4T8MSN10KS` / `R805DJ56LZHM` / `YX7PB48WR7R4` / `XT4BE7LFY5XH` | **2 PREDICTED (`P1`, `P5`) / 0 SPLIT / 0 MISS / 3 UNREACHED (`P2`, `P3`, `P4`)**. Judgment **2 ADVANCE / 3 RETURN / 0 ESCALATE, overall RETURN — on the INSTRUMENT, not on the arm's design**. `EB-224`'s STAGE + GRADE + REPLAY half for `proto_spark_mode_bombs`, the first row in the tree priced at a MODE HEAD (R225's amended clause, on `EB-182`'s machinery); the whole fight stays owed. Four boards matched in pairs, everything held constant but the bank and one card: `t01` bank 3 with no rival sink, `t02` `t01` with Firework Finale swapped in at the same price of 3, `t03` bank 2 with no `gain_spark` in hand, `t04` bank 2 with the missing Spark in hand. **`P1` PREDICTED at 1 of 1 and it is the first finding: on `t01` the deciding form takes the PRICED mode** — *“I spent 3 Sparks with Bag of Tricks to place 3 Bombs on Seapunk”* — and names what it declined, *“the single-Bomb option … to preserve all 3 Sparks”*. **`P5` PREDICTED at 1 of 1 and it is the second: the mode-head price is charged once and pays out what it prints.** `t01`'s replay offered BOTH mode texts at a bank of 3, the post-play bank read exactly **0**, and the payload was three Bombs at 5 — established twice, by `bomb: 15` on the target and by the detonation delivering exactly 15 (the wire has no bomb-COUNT field). That is the live half of the codegen gap `EB-224`'s build closed. **`P2`, `P3` and `P4` are UNREACHED by the slate's own registered rule** — a REFUSED deciding form grades UNREACHED, not MISSED (`EB-209`) — and under that rule an UNREACHED slot is not a pass and not a fail, **so no registered decision fires, nothing is re-priced and NO [USER] row opens on the slate**. `P1` and `P2` were registered as ONE finding read together, so **`P1` alone does NOT establish that the decision is board-driven** and is not reported as if it did; the pair read says it in its own words: *“P1 was predicted, but P2 was unreached; this round does not show that the decision changed with the board rather than reflecting a habit.”* **ANSWERED OUT OF SLOT and recorded as such:** `t02`'s refused deciding line is *“Bag of Tricks [mode: Place 1 Bomb dealing 5] → Quick Fuse → Firework Finale → Duck and Cover”*, exactly `P2`'s predicate, and `t04`'s refused form plans the raise — *“Powder Pop … to place a Bomb and reach 3 Sparks, then Bag of Tricks choosing ‘Spend 3 Sparks’”* — which `P3` printed in advance as a correct reading. **That evidence moves neither slot, both stay UNREACHED as published (R101b).** **The round's RETURN is a REGISTRATION defect and it is stated as one: 7 of 8 forms were REFUSED for `intent_insensitive`** (3 of 4 deciding, 4 of 4 shadow). Every board gave ONE enemy on a fixed telegraph, 3 Energy and a hand of at most two Energy-costed cards, so the whole hand was always playable and the telegraph never forced a trade — the readers say so themselves (*“with enough energy to play both costed cards and both zero-cost cards, a different telegraphed intent would not have changed this line”*). Holding everything but the bank constant is what bought that. Filed as a `BACKLOG` candidate (a board-design rule for resource rounds, and the falsifier's reach on a board whose question is not defensive); nothing minted. **Second non-slot finding, and the consequential one: the priced mode REFUNDED ITS OWN PRICE inside the turn.** `t01`'s bank read 3 → **0** on the mode and **3 again** after Quick Fuse, because Klee's STARTER RELIC *Pounding Surprise* pays +1 Spark per Bomb detonated (`Klee.cs:152` seats it; `Relics/PoundingSurprise.cs` `OnBombDetonated` gains it) and the mode places exactly 3 Bombs. So wherever the Bombs it buys detonate the same turn the mode is **net-free**. The registration did not control the starter relic and the blind page does not print relics. **It is NOT a defect — the relic behaved as built — and it changes NO grade** (`P5` asks for the bank immediately after the play, when it was 0; `P1` asks which mode was chosen), but it is a board confound and a design question, and it is what returns to [USER] as a four-item numbered pick at packet §22.6. `KLEESPARK-W3` §18.9 had already named this relic as one of *“two sources the ratio cannot count”*; this is the first record where it lands on the card under test. **Grading chair:** a DESIGN round, so under `M64` (1) / R224 the **Codex seat decided EVERY board** (`--seat-spot-check 1`) and fresh-Opus was NOT seated — the row is `authored_by: [claude]` and an ADVANCE resting on a same-family read is not author-disjoint (R217 C). The local seat sat SHADOW; its verdict agreement with the deciding chair is **3 of 4** and is RECORDED AND NOT GRADED (`M62` is not at issue at that denominator). **5 Codex calls of a cap of 15** — four deciding reads and one pair read, exactly the plan; the meter read `5h 40% / week 25%` before and `5h 48% / week 26%` after, and `EB-227`'s guard (85% / 50%) never refused. **Nothing was deployed:** the installed build already carried the row, proven read-only before staging (`ProtoSparkModeBombs` ×4 in `klee.dll`'s UTF-8 metadata, *“Bag of Tricks”* and `proto_spark_mode_bombs` once each in its UTF-16 strings). **`EB-191` FIRED**: `t04` failed to stage on the first pass with `seed_not_honoured` (the run read the seed back as `None`), nothing had been read, and the board was re-staged alone from the unchanged committed file and read in its pre-registered position — a re-attempt, not a re-roll. Two blind spots printed before the run held: the tier0 mirror's `closeness` enumerator cannot see a `choose_one` MODE, so all four gaps bound card SETS and not this round's choice; and `slot_plan._spark_prices` reads a TOP-LEVEL `spend_spark` only, so the row under test is invisible to `affordable_spark_uses` and every board predicate is written about the OTHER Spark cards | packet `review/active/klee-sparks-2026-08-29.md` §22 (registration §21.1–§21.8, results §22.1–§22.7); slate and boards `understudy/turns/klee-sparks-bt1/` (`MANIFEST.md`, `slots.yaml`); forms, verdicts and the one replay under `review/qa/klee-sparks-bt1-t0*/`; pair read `review/qa/klee-sparks-bt1-pair-review-codex-gpt-5.6-sol.md` and its prompt beside it |
| `KLEESPARK-BT2` the repaired *Bag of Tricks* round, under R229's return condition (`EB-224`) | 2026-08-30 | dev build `0.2.1676+proto.dirty`, game `v0.111.0`, world `r229-2026-08-30` @ `94e1a4a5`, three staged boards, seeds `JH4T8MSN10KS` / `R805DJ56LZHM` / `YX7PB48WR7R4` | **0 PREDICTED / 0 SPLIT / 1 MISS (`F4`) / 4 UNREACHED (`F1`, `F2`, `F3`, `F5`)**. Judgment **0 ADVANCE / 5 RETURN / 0 ESCALATE, overall RETURN — on the INSTRUMENT, not on the arm's design**, which is the second instrument RETURN in a row on this arm. **R229'S PRE-REGISTERED RETURN CONDITION DID NOT FIRE:** (a) requires `F1` PREDICTED and `F1` is UNREACHED; (b) is a conjunction and both halves fail — the `t03` form DID name a cost (*“It gave up 12 additional Block from Spirited Away”*) and there is no next-turn bank reading at all. **The arm neither advances nor returns: it stays under test and AT RISK where R229 put it, with the condition standing and unanswered, and NO [USER] row opens.** **Why nothing was reached: all six forms were REFUSED, every one of them for `forecast_missing`.** The round's new machinery — `EB-229`'s staged twin, a pre-commit forecast asked at the top of the page and answered BEFORE the line — shipped only its PACKET half. `qa_packet` prints the three questions and `staged_turn` refuses a form that answers fewer than it was asked, but `understudy/seat.py`'s `form_schema()` is strict (`additionalProperties: false`, nine required properties) and **carries no `forecast` field**; the local tester's schema has the same gap. There was no box to answer into. **Both readers answered anyway, in prose, in the wrong box** — `t02` Q1 opens *“Forecast: 3; yes; 1”* and `t03` Q1 closes *“My forecasts were: 0 Spark at the end of this turn, 4 Spark at the start of next turn…”* — which is what proves the packet half works and locates the defect in the form. A forecast smuggled into a past-tense answer is not a pre-commitment and the falsifier is right to refuse it. **`F4` is graded MISS at 0 of 3 and not UNREACHED**, because its registered falsifier IS a `forecast_missing` refusal and a slot whose falsifier could only ever grade UNREACHED would be unfalsifiable by construction; `F1`, `F2`, `F3` and `F5` take the ordinary rule (`EB-209`). **NO LINE WAS REPLAYED**, so this round has no wire readings, no post-play bank number and no next-turn reading — `t03`'s `replay_next_turn`, the one turn of the future the round was built to buy, does not exist. `t03`'s deciding form was ALSO refused `target_missing` (`EB-203`), having played *Bag of Tricks* at no target. **ANSWERED OUT OF SLOT and recorded as such (R101b), none of it graded:** on `t01` the deciding line is the priced mode → Kaboom! → Firework Finale and says *“spent the Sparks gained from the Bomb detonations on Firework Finale”*, with the shadow reader naming the relic outright — *“the bombs detonating under Pounding Surprise restore 3 Sparks”* — which is `F1`'s predicate as PROSE and not as the wire reading `F1` asks for; and on `t02` the deciding line pays for BOTH priced uses on the board `EB-236` certified as having no order that buys both, a claim that reads unpayable on paper (the mode takes the bank to 0 and Firework Finale must be paid before it can detonate anything) and that only a replay could settle. **`EB-238` CLOSES on this round:** the staged page printed the run's relics and a form quoted one. It also exposed a printed falsehood — every board asserts *“the run carries Klee's starting relic and no other”* and the page prints TWO, *Pounding Surprise* and *Fishing Rod*; Fishing Rod does nothing in combat and moves no number here, so no grade is affected, but the assumption is false as printed and the preflight cannot see it. **Grading chair:** a DESIGN round, so under `M64` (1) / R224 the **Codex seat decided every board** (`--seat-spot-check 1`), fresh-Opus was NOT seated (`authored_by: [claude]`, R217 C), and the local seat sat SHADOW — refused on all three boards for the same structural reason, so shadow-versus-deciding agreement has **0 comparable turns** and says nothing about `M62`. **4 Codex calls of a cap of 9** — three deciding reads and one pair read, exactly the plan; the meter read `5h 48% / week 26%` before and `5h 59% / week 28%` after, and `EB-227`'s guard never refused. **Nothing was deployed**, the installed build already carrying the row, proven read-only off `mods\klee\manifest.json` and `release_info.json` before staging. Every seed came back as requested on the FIRST attempt (no `EB-191`), and all three previously unverified `give_card` ids — `KLEEMOD-MINE_TOSS`, `KLEEMOD-SPIRITED_AWAY`, `KLEEMOD-RUN_AWAY` — staged live. The pair read agreed slot for slot, including `F4`'s exemption, and on the condition: *“DID NOT FIRE… Neither registered predicate is satisfied”*. **What this licenses:** one engineering row, the forecast's FORM half in both schemas. **What it does not:** anything about the card — no re-price, no re-wording, no sheet move, no change to §4.2 or to R225's clause, no removal of *Pounding Surprise*, and no claim about win rate, balance or fun (§23.5, R215 B, Guardrail-7) | packet `review/active/klee-sparks-2026-08-29.md` §24 (registration §23); slate and boards `understudy/turns/klee-sparks-bt2/` (`MANIFEST.md`, `slots.yaml`, `t01`–`t03`); forms and verdicts under `review/qa/klee-sparks-bt2-t0*/`; pair read `review/qa/klee-sparks-bt2-pair-review-codex-gpt-5.6-sol.md` and its prompt beside it |
| `KLEESPARK-BT2` **THE RERUN** — the same three boards on a form that can carry a forecast (`EB-224`) | 2026-08-30 | dev build `0.2.1676+proto.dirty`, game `v0.111.0`, world `r229-2026-08-30` @ `bac66284` (the registration commit), the SAME three boards byte-identical to `klee-sparks-bt2/` except their turn ids, seeds `JH4T8MSN10KS` / `R805DJ56LZHM` / `YX7PB48WR7R4` | **3 PREDICTED (`F1`, `F4`, `F5`) / 0 SPLIT / 1 MISS (`F3`) / 1 UNREACHED (`F2`)**. Judgment **2 ADVANCE / 3 RETURN / 0 ESCALATE, overall RETURN — and this time on the ARM'S DESIGN, not on the instrument.** **R229'S PRE-REGISTERED RETURN CONDITION FIRED, on (a): `F1` is PREDICTED.** On `t01` the deciding line is *Bag of Tricks* [priced mode] → *Kaboom!* → *Firework Finale* → *Spirited Away*, and the live replay reads the Spark bank **3 → 0 on the mode → 3 after the Attack → 0 on Firework Finale**, with the body 45 → 23 → **5** HP: 40 damage, **both 3-Spark uses paid and resolved inside one turn**, the second bought entirely out of *Pounding Surprise*'s refund. **THE ARM RETURNS TO DESIGN.** (b) is not satisfied — `F2` is UNREACHED — and the finding is reported as ONE, not two. A RETURN moves no number by itself (§23.5, R215 B, Guardrail-7): it returns the arm to [USER] as the four-item numbered pick list at §24.9.9 (re-price / restructure so the mode's own Bombs cannot pay for it / accept the refund as the card's point and write the intent / drop the arm), on which Claude recommends 3 and picks nothing. **THIS IS A RERUN AND NOT A RE-ROLL:** §24's grades stand exactly as published (R101b) and the boards, seeds, slate, thresholds and return condition are unchanged; what changed is the INSTRUMENT — `EB-239` closed, so `seat.form_schema()` declares a `forecast` field (nullable-and-required on `target`'s rule, `additionalProperties` still `False`) and the local tester prints the same schema. **`forecast_missing` refused nothing this time:** all six forms carried three answers against three questions, where §24's six carried none. **`F5` PREDICTED is the legibility half:** `t01`'s reader forecast `0` and `3` BEFORE choosing its line and the wire read 0 and 3, off a page that prints the relic (`EB-238`). **`F3` MISSED at 0 of 1, and the clause matters:** exactly one priced use was paid — on `t02` the game itself refused the second, *“Card 'Firework Finale' cannot be played: BlockedByCardLogic”*, which **vindicates `EB-236`'s certification on the wire** and settles §24.5 item 2's unresolved reading; the slot missed on its OTHER clause, the second answer naming neither priced use. §23.4's rationale for filing a MISS here belongs to the clause that did not fire, so **nothing is minted on it**. **`F2` UNREACHED for the third round running:** `t03`'s deciding form was refused `no_second_line` (Q2 reads *“none”*) and `intent_insensitive`, so no replay ran and the `replay_next_turn` reading still does not exist — a reading about the reader, not the instrument. **Grading chair unchanged:** Codex decided every board (`--seat-spot-check 1`, `M64` (1) / R224), fresh-Opus not seated (`authored_by: [claude]`, R217 C), local seat SHADOW at **1 of 3** comparable turns — nothing about `M62` at that denominator. **4 Codex calls** (3 deciding + 1 pair), exactly the plan, against a cap of 5 (9 minus §24's 4); the meter read `5h 59%` / week 28% immediately before, the five-hour window **rolled over at 16:36 EDT mid-round**, and the round finished at `5h 1%` / week 28% — recorded, not smoothed. **Nothing was deployed.** Every seed came back on the first attempt (no `EB-191`). **Out of slot, graded nowhere:** every board declares `set_hp: {who: first, amount: 55}` and the live bodies read 45 / 46 / 40 — identical in §24, so the boards are reproduced exactly, and it moves no grade (the largest line is 40 against 45, so *no lethal line* holds by 5); it is `EB-240`'s shape of blind spot. **What this licenses:** the pick list, and nothing else. **What it does not:** any re-price, re-wording, sheet move, change to §4.2 or R225's clause, removal of *Pounding Surprise*, or claim about win rate, balance or fun | packet `review/active/klee-sparks-2026-08-29.md` §24.9 (registration §24.9.1–§24.9.4, results §24.9.5–§24.9.10; the round it reruns is §23/§24); boards `understudy/turns/klee-sparks-bt2r/`; forms, verdicts and the two replays under `review/qa/klee-sparks-bt2r-t0*/`; pair read `review/qa/klee-sparks-bt2r-pair-review-codex-gpt-5.6-sol.md` and its prompt beside it |
| `KURAGECAD-S1` the Kurage memory's CADENCE measured DRAFTED, in the sim (`EB-234`) | 2026-08-30 | `RT12/D18/P11/C21`, cell `kokomi/commander`, hunter, `assigned`, realistic, 600 runs, seed 11, `jobs=1` | **5 PREDICTED (`C1`–`C5`) / 3 SPLIT (`C6`, `C7`, `C8`) / 1 MISS (`C9`) / 0 UNREACHED.** The memory fires on **60.9%** of 78,126 player turns and the rate CLIMBS act 1 → act 3 (47.1% → 71.2%); both entry doors are live (Exhaust 61% / Muster 39% of 108,177 enrolments); the BLOCK is an act-1 state (19.2% → 3.8%); Memory/Order spam does not appear on the sim seat (copies 12.0% of plays, memory-only turns 1.7%) — with §15.4's own caveat that a pilot which never plays toward the queue makes that nearly a tautology. **SPLITs:** the free replay is the majority of fires (57.2%, median fired price 0); the uncapped queue is short at the median (2) and long in the tail (p95 9, max 31), which returns to [USER] as the cap pick; the drafted deck holds a median 3 Exhaust cards. **`C9` MISS**, and §15.2's Ethereal paragraph is STRUCK not rewritten (R101b): the seam read missed `curse_clumsy`, an event-granted CURSE tagged `ethereal`, so 165 of 600 decks hold one — but 0 of 108,177 enrolments did, because the door refuses junk, and `EB-234`'s Ethereal half stays unanswerable in the sim. Three engine repairs are disclosed with the arm (§15.2). No balance claim (R213 B / R215 B): the ON/OFF columns are not two samples of one population | packet `review/active/kokomi-kurage-memory-2026-08-29.md` §15, §15.5–§15.6; raw `review/qa/kuragecad-s1/` |


## Active registrations (pointers — packets live in `review/active/`)

- **`EB-118` card-connectivity instrument** — static pre-registration at
  `review/active/eb118-richness-phase0-2026-08-23.md` §2, [USER]-approved
  2026-08-23. **Instrument:** `tools/card_connectivity_report.py` —
  deterministic, sheets-only, moves no `RT/D/P/C` version. **Cell:** eight
  pools (five canon through the `game_ref/` extraction surfaces, three mod)
  under one frozen classifier. **Status:** the paired baseline is TAKEN —
  `review/active/eb118-connectivity-baseline-2026-08-24.txt`, at `a2e389f` and
  as the first commit of the Phase-1 branch. All eight pools read and
  UNCLASSIFIED is zero in every one; the classifier is FROZEN from that commit,
  so if the vocabulary is later found wrong BOTH sides re-run under a new
  `VOCAB_VERSION`, never the post result alone. Directional predictions only
  (§2.4): no threshold is registered and none may be derived — meeting §2.5's
  five-canon precondition authorizes a PROPOSAL to [USER], not a gate.
  Registered blind spots at §2.6.
- **The regret margins (`M13`)** — **DRAFT, unrun**, §7's predictions blank.
  **Instrument:** `tools/regret_distribution.py`, a read-only pass over
  finished runs that moves no stamp. **Cell:** the margin-free gap distribution
  for `ROUTE_REGRET_MARGIN` and its drafter twin, whose `+1.0` R164 left
  unratified. **Status:** R181 settled the scope slots — control `C2`
  authorised with its build owed before the run, `C3` declined so `Q5` and §6's
  Option B are unavailable, and Option D (no margin) retained as the standing
  answer. Under R212(2) the §7 slate is Claude's to draft from written design
  intent and commit DRAFTED before the run, then countersigned in batch; the
  work is BACKLOG `M13` →
  `review/active/regret-margin-registration-2026-08-12.md`.
- **Charge reads per turn (`EB-78`)** — **SLATE DRAFTED, unrun**: §5 is
  `X9READ-S1`, seven slots `X1`–`X7`, and §5.4 is where *repeatable reads
  dominant* became a number — `p50` > 5 reads per turn AND the repeatable
  sources > 50% of reads, or the ruled double read > 50% of attack plays.
  **Instrument:** `resources.note_charge_read` — emit-only, count-only, tagged
  per source. **Cell:** resolved Charge reads per completed player turn.
  **Status:** descriptive, so it grades no design and cannot on its own fire a
  nerf; it moves no version and opens no window. Its payoff-reach sequencing
  gate is discharged. Under R212(2) the §5 slate is drafted and committed
  DRAFTED by Claude, then countersigned in batch →
  `review/active/charge-reads-per-turn-registration-2026-08-13.md`.
- **Kokomi stability band (D5)** — no band is declared, so it rides DARK
  (`band = None`). The declaration is QUEUE `S4-G6`; its grading playtest is
  `docs/current/playtest/kokomi-playtest-protocol.md` (unrun, Answers block
  blank).
- **`KOKOMI-SLICE1-WF` — the six ADVANCED slice-1 arms across whole fights** —
  **DRAFTED 2026-08-30, unrun, not countersigned.** Drafted by Claude from
  written design intent and committed before any seed is spent (R212(2)); it
  is offered for batch countersign. **Why:** the six arms' four rounds of
  ADVANCE feed nothing registered — they land only on the accept-to-sheet
  signoff, which is the prototype surface's own deletion rule (R213 B), a
  one-way door with no measurement in front of it. **Unit:** one complete
  fight, Codex seat, `understudy.blindplay session` with the arm granted by
  `understudy.embark --arm`; **30 Codex calls per fight** (`--max-actions 24`,
  `--max-refusals 2`, worst case 28), three fights, 90-call ceiling.
  **Slate:** eight slots, `WF1`–`WF8`, every falsifier counting plays, turns
  or sentences off the run's own artefacts — cadence and stacked rotations for
  arm A, whether 3 energy binds and is named for the three priced Companion
  arms, and whether the Block mode is ever taken, ever named, and ever handed
  back by the memory replay for the two exclusive arms. **Contaminations:**
  granted deck, `+proto` build, `C.KURAGE_MEMORY` ON as a deliberate second
  variable with its error direction stated (the kit makes a priced Companion
  easier to afford, so *the price binds* is a floor and *it does not* is
  confounded), and the GPT seat under R217 C/G. **Sequenced after** `M67` and
  after `KURAGEMEM002`'s rerun; F3 additionally behind `EB-184`. Thoma —
  Blazing Ooyoroi, the slice's one open RETURN, is excluded. No board staged,
  no seed pinned →
  `review/active/kokomi-slice-1-2026-08-27.md`, *Whole-fight blind play*.

- **`EB183-MF` — Muster's Charge subsidy asked at the FUNNEL, the fifth matched
  pair (`EB-183`)** — **DRAFTED 2026-08-30, unrun, not countersigned.** Drafted
  by Claude from written design intent and committed before any board is staged
  or any seed is spent (R212 item 2); offered for batch countersign. **Why:**
  R216 D deferred Muster's Charge subsidy into R213 E1, and that deferral has
  TWO readings. Slice 2 asked the first — the subsidy's SIGN, on a card — and
  those four arms retired under R227 / `M67` (1), which retired arms that PRICE
  Charge. The second reading prices nothing: *recruits from an order that paid
  for them pay no Charge when they Exhaust*, a property of the exhaust FUNNEL
  and of no effect list. R213 E1 stays open until both are asked. **Unit:** one
  staged turn per half, blind-graded, shipped half first to discover the seed;
  the deciding read must be GPT, since the row is `authored_by: [claude]`
  (R217 C). **Slate:** `MF1` the face teaches the waiver (1 of 1 forms), `MF2`
  the deciding second line on the prototype half DIFFERS from the shipped
  half's — a match answers R213 E1's second reading NULL, which closes the gate
  — `MF3` the grader's stated reason mentions the bank at all, `MF4` recorded
  and not graded (was a recruit played at all). **Contaminations:** granted
  deck and a hand set through a dev door, `+proto` build, FOUR energy rather
  than the four pairs' three (the difference lands one play later, on a
  recruit's rotation), no seed pinned, and a closeness reading that cannot
  separate the halves — the pilot values an order by what it puts in hand, so
  the blind seat is the pair's only reading. **Gate:** [USER]'s countersign on
  the R226 reading in §1 as well as on the slate, then game time. Boards
  `understudy/turns/eb183-muster-funnel/`; no board staged, no seed pinned →
  `review/active/eb183-muster-funnel-2026-08-30.md` §4.

- **`KLEESPARK-BT3` and `KLEESPARK-W5` — the two cells R230 left owed
  (`EB-224`)** — **DRAFTED 2026-08-30, unrun, not countersigned.** Drafted by
  Claude from written design intent and committed before any board is staged
  or any seed is spent (R212 item 2); offered for batch countersign.
  **Why:** R230 took §24.9.9's pick at option (3) QUALIFIED — *Bag of Tricks*
  keeps its refund loop as a deliberate BRIDGE mechanic — and left exactly two
  things owed: the `F2` repair, and the whole fight.
  **`KLEESPARK-BT3`**, first: two staged boards
  (`understudy/turns/klee-sparks-bt3/`, seeds `YX7PB48WR7R4` /
  `R805DJ56LZHM`), taking R230's SECOND repair — *Mine Toss* leaves the board,
  so nothing but the mode under test places a Bomb and the refund is
  attributable by construction rather than by subtraction. Slate `G1`–`G4`:
  the re-posed `F2` at 2 of 2 with a one-refusal rule written in advance, a
  pressure control that is a declared subset of it, the forecast channel's
  denominator, and the delayed arithmetic. Counting slot `C1`, threshold 2,
  ceiling 2. Codex seat decides both boards (`M64` (1) / R224), local seat
  SHADOW, 3 calls expected of a cap of 6. First round to declare `EB-240`'s
  `expects:` block — both relics and each seed's recorded body, refused at
  stage on a mismatch. **`KLEESPARK-W5`**, after it: one whole fight carrying
  **R230's PRE-REGISTERED COLLAPSE CONDITION in graded-predicate form** —
  priced-mode takes ≥ 90% of opportunity pages on a denominator of ≥ 4, ZERO
  free-mode takes, and ZERO pages naming a reason to preserve the extra Spark;
  all three, and the arm RETURNS TO DESIGN again; fewer than 4 opportunity
  pages is UNREACHED and infers nothing. Slots `B1`–`B4` graded, `B5` recorded
  and not graded. **First registration to switch `EB-229`'s blind-run forecast
  channel ON**, with its error direction declared: asking *what are you giving
  up* every turn makes clause (iii) harder to satisfy, so a collapse that
  fires is a FLOOR. `EB-235` is deliberately NOT folded in — the Rare Power is
  not granted and grades nothing here. Contaminations: granted deck, `+proto`
  build, *Pounding Surprise* present by design, the Neow deck-neutral rule,
  `EB-191`, and every income figure a floor. 45-call cap →
  `review/active/klee-sparks-2026-08-29.md` §25.

- **`KURAGECAD-W1` — the Kurage memory's cadence across a WHOLE FIGHT
  (`EB-234`, second leg)** — **DRAFTED AND COMMITTED, NOT RUN, NOT
  COUNTERSIGNED.** The slate is `review/active/kokomi-kurage-memory-2026-08-29.md`
  §15.8, drafted under R212 item 2 and committed before anything is staged; the
  ruling that authorised it authorised **the drafting and the RHYTHM shape
  only, and explicitly did not countersign a blank registration**, so the
  countersign is a later batch act.
  Its sim sibling `KURAGECAD-S1` is finished and sits in the published table
  above; the live leg inherits from it the staging SHAPE and **no threshold**.
  **Unit:** one `understudy.blindplay session` on a `+proto` build, Codex seat,
  Kokomi's flagged starter plus five GRANTED rows (§15.8.2 — three Exhaust
  printers, the sim's own median and not above it, so a jam observed live is a
  FLOOR). **Slate:** `K1` readability off the live page — does anything fire
  next turn, and where does the Charge run out — which folds in `EB-198`'s blind
  read deliberately, for the page mirror only (§15.8.6); `K2` the live beat on a
  deliberately wide band (≥ 25% of combat pages), with `S1`'s 60.9% riding as a
  COMPARATOR that one fight can neither confirm nor refute; `K3` the tail —
  zero jam episodes AND the longest-queue page still readable — which is the ruled
  live re-read of the UNCAPPED queue and licenses no cap in either direction;
  `K4` steering INTO the memory; `K5` the block named and unblocked on the first
  page it bites; `K6` the four levers RECORDED AND NOT GRADED, because one fight
  cannot ground them. **`EB-229`'s forecast channel is ON** with three
  prospective questions and its error direction declared one way: the asking
  points the player at the element every turn, so a PASS on `K1`/`K3`(ii)/`K4`/
  `K5` is a CEILING and a jam episode observed is a FLOOR. **Ethereal is
  DEFERRED by the same ruling — no slot demands a carrier. Gate: GAME TIME** — a `+proto`
  build, the deploy, an operator and the seat's window; 45-call cap →
  `review/active/kokomi-kurage-memory-2026-08-29.md` §15.8.

New registrations add a pointer here and land their packet under
`review/active/`. When one is graded, it moves to the **Graded** table above —
the packet and its raw results stay where they are, unedited (R101b), and the
long active-entry narrative goes to the commit message that moved it.
