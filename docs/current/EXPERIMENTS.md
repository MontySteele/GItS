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
- **Charge reads per turn (`EB-78`)** — **DRAFT, unrun**, §5's prediction slots
  blank; §5.1 is where *repeatable reads dominant* becomes a number.
  **Instrument:** `resources.note_charge_read` — emit-only, count-only, tagged
  per source. **Cell:** resolved Charge reads per completed player turn.
  **Status:** descriptive, so it grades no design and cannot on its own fire a
  nerf; it moves no version and opens no window. Its payoff-reach sequencing
  gate is discharged. Under R212(2) the §5 slate is drafted and committed
  DRAFTED by Claude, then countersigned in batch →
  `review/active/charge-reads-per-turn-registration-2026-08-13.md`.
- **`KLEESPARK-W4` — the strict Rare Power's whole fight, and `W1''`'s longer
  batch (`EB-223`)** — **DRAFTED 2026-08-30, NOT RUN.** Registration
  `review/active/klee-sparks-2026-08-29.md` §19, committed before any run under
  R212(2) and offered for batch countersign; the grader
  (`review/qa/blindplay/kleespark-w4/grade.py`) is owed as its own commit before
  the session, in §17's shape. **Instrument:** `understudy.blindplay session`
  over a live dev build, graded by that committed mechanical script off the
  run's own pages, replies and transcript; it moves no `RT/D/P/C` stamp.
  **Cell:** the installed `+proto` dev build, one capped batch, one seed rolled
  and read back off the wire (R95). **Arm:** `KLEESPARK-W3`'s exact granted
  deck — the derived **8 makers : 5 sinks = 1.600** — **plus
  `proto_true_spark_knight`** (Spark Knight's Oath, Rare Power, 2 Energy,
  *"Your Attacks that do not already cost [Spark] cost 3 [Spark] instead of
  their Energy cost"*, the price a constant at `C.SPARK_ATTACK_POWER_PRICE` =
  3). The Power carries no top-level `gain_spark` or `spend_spark`, so the
  counted ratio is unchanged; the deck is 24 cards against `W3`'s 23. **ONE
  registration serving TWO owed reads, with the linkages registered separately
  so neither contaminates the other:** `W1'''` continues `W1''`'s SPLIT (1 of
  19 combat pages) at the longer batch and is graded on **PRE-POWER pages
  only**, where the deck is `W3`'s deck exactly; `K1'''`/`K2'''`/`K3'''` are
  graded on **POST-POWER pages only** and are UNREACHED if the Power never
  resolves. **Slate:** `W1'''` ≥ 3 pre-Power pages holding two affordable uses
  with a non-damage destination among them (1–2 SPLIT, 0 MISS); `K1'''` ≥ 2
  converted Attacks actually paid at 3 on pages printing a bank ≥ 3, its
  denominator printed (1 SPLIT, 0 MISS, UNREACHED on a zero denominator);
  `K2'''` both halves of §5's own observable — every converted Attack's cost
  corner printing Spark 3 / Energy 0 on every post-Power page, AND one page on
  which Energy buys a Skill or Power while the bank buys a converted Attack
  (one half SPLIT, neither MISS); `K3'''` ≥ 1 post-Power page where a converted
  Attack and a price-2 non-damage sink were both affordable and the sink was
  the play (0 with denominator ≥ 3 MISS, 0 with 1–2 SPLIT, denominator 0
  UNREACHED); `K4'''` RECORDED and NOT GRADED. **Why a whole fight and not a
  staged turn:** R222 (a)'s own words — *"an investment Power needs fight
  history before its wording or its price can be judged"* — and `P3` already
  read the only thing a staged board can read about it. **§12.2's D4 objection
  is recorded, not withdrawn:** the Power is now the window's one variable and
  the ratio is what is held fixed, so this read can say what the Power does at
  a known ratio and can NOT compare itself to `W3`, attribute anything to the
  Power alone, or treat the pre/post-Power split as a controlled contrast.
  **What the grades permit:** `K1'''`+`K2'''`+`K3'''` all PREDICTED makes the
  Power an ADVANCE-to-sheet CANDIDATE — a numbered proposal to [USER], never a
  Claude decision; a `K2'''` or `K3'''` MISS RETURNS to a staged round (and, for
  `K2'''` half (i), files an `EB-164`-family display defect); and **`K1'''` MISS
  with a NON-ZERO denominator is the ONE registered outcome on this slate that
  may reopen §5's wording and the price of 3 to [USER]** — R222 closed that
  question and no other slot here may reopen it. **Budget:** `--max-actions 80`,
  Codex cap **90 calls** (`W3` spent 45 for 4 fights ≈ 11.25/fight, so ~8 fights
  and ~0.85 meter points per call), starting only at ≤ 8% of the five-hour
  window and ≤ 35% of the week, under `EB-227`'s stop lines of 85% and 50%; one
  session, no second. **Contaminations, §19.5:** granted not drafted; `+proto`,
  so the automatic Spark rule is NOT live and 3 is the only price a converted
  Attack carries; Neow's unskippable boon, taken by a registered deck-neutral
  rule (`W3` took Silken Tress); Pounding Surprise and Endless Fireworks are
  income the ratio cannot count, so every income figure is a FLOOR; one seed for
  the whole batch, so the fights are not independent; the additive starter and
  the fourteenth card move draw frequency, not the ratio. **Sequencing:** after
  the morning's merges, at the next game-time slot. Guardrail-7 and R217 G ride
  the whole row.
- **Kokomi stability band (D5)** — no band is declared, so it rides DARK
  (`band = None`). The declaration is QUEUE `S4-G6`; its grading playtest is
  `docs/current/playtest/kokomi-playtest-protocol.md` (unrun, Answers block
  blank).

New registrations add a pointer here and land their packet under
`review/active/`. When one is graded, it moves to the **Graded** table above —
the packet and its raw results stay where they are, unedited (R101b), and the
long active-entry narrative goes to the commit message that moved it.
