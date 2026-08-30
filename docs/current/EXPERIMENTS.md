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
| `KLEESPARK-R2` R222 D's minimal repaired staged round | 2026-08-29 | dev build `0.2.1517+proto.dirty`, game `v0.111.0`, world `main` @ `712c75e` | **3 PREDICTED (`P1`, `P2`, `P5`) / 0 SPLIT / 0 MISS / 2 UNREACHED (`P3`, `P4`)**. `P1` — the re-posed spend-versus-hold slot, asked at a threshold of 2 against a ceiling of 3 — came in **3 of 3**: every `S1` board's deciding form named a DIFFERENT Spark-priced card as its second line. **ERRATUM 2026-08-29 (relayed review; packet §13.1): the grade STANDS and is NOT re-graded (R101b), its LABEL is superseded.** Neither `S1`'s registered predicate nor `P1`'s grading predicate asks for a hold — both ask for a choice BETWEEN SINKS. On `t01` both candidate lines spend all three Sparks; `t04` says the turn *"did not present me with a decision — it presented me with a sum"*; `t06`'s two candidates are both priced 2 and the AoE dominates. No affordable sink was deliberately skipped on any board. `P1` therefore reads **alternative sinks are legible, 3 of 3**, and it does not overturn `KLEESPARK-W1`'s whole-fight `W1` = 0 and `W3` = 0. **Disclosure, same review:** the DECIDING reader was fresh Opus and all eight Spark rows are `authored_by: [claude]`, so this round's deciding read is SAME-FAMILY with the author — operationally authorised by R222 B, and NOT author-disjoint under R217 C. What that should cost a round is QUEUE `M64`; nothing here is re-graded on it. `P2` — the dry sink with no generator anywhere in hand, which `KLEESPARK-R1` could not stage — came in **2 of 2**, with no reader on any board calling a priced card free or affordable. `P5` PREDICTED at **3 of 5** shadow-versus-deciding verdict agreement on the first set (3 of 6 over the round), below `M62`'s ≥ 6/8 bar, so the local seat stays in the SHADOW chair. **Both UNREACHED slots are instrument findings, not readings about the cards.** `P3`: one of its two three-body boards drew ONE enemy — a seed recorded three-body on six earlier KOKOMI stagings gave Klee one body — and a board that cannot be asked is UNREACHED by the slate's own rule; `EB-208` is the defect, because `EB-202`'s ceiling is computed off the DECLARED board and no check in the funnel can see the gap. `P4`: its dedicated board `t03` posed the question and its form was then REFUSED for `intent_insensitive`, and a refused form is not replayed, so the slot's own denominator produced no replay — **absence of a counterexample is not PREDICTED**. **ANSWERED OUT OF SLOT and recorded as such:** `t01`'s live replay paid Bang Bang!'s printed 2 off a bank of exactly 2 (bank 3 → Fwoosh! → 2 → Bang Bang! → 0; Seapunk 45 → 20, a fall of exactly 7 + 8 + 5 + 5) with no Bomb on the board, so §12.8 item 1's candidate — *"Bang Bang! may be charging 1 for a printed 2"* — is explained by the whole fight's detonation and there is no pricing defect. That evidence does NOT move `P4`, which stays UNREACHED as published. Pair read: **3 ADVANCE / 2 RETURN / 0 ESCALATE, overall RETURN — on the INSTRUMENT, not on the arm's design**. **Second finding, `EB-209`:** in the shadow chair R221 B's stopping rule reads SHADOW grades, because the deciding forms do not exist while the round runs; it changed nothing here (all four slots UNDECIDED, all six boards run, zero UNRUN) and could stop a later round on a reading that decides nothing. **`--lanes 2` was attempted first and FAILED**: lane 1 asked for `NMQLUYZDLV` and the run read back lane 0's `R7W86HG7WHUD`, so `t04` was refused by `seed_not_honoured` and the round stopped at its second board; the round was re-run whole on one lane and nothing was carried over. **R221's timing claim gets its first number** (§13.5): 372 s wall clock for six boards — stage 89 s, read+grade 295 s, replay 124 s over three surviving lines — so the pipeline hid ~73 s of the 89 s of game-bound work, about 16% of the round, because a read is ~3× a stage and the round is model-bound. Codex budget spent: **3 calls** (two spot-check seat reads, one pair read). Three picks at §13.6 | packet `review/active/klee-sparks-2026-08-29.md` §13; slate and boards `understudy/turns/klee-sparks-r2/` (`MANIFEST.md`, `slots.yaml`); forms, verdicts and replays under `review/qa/klee-sparks-r2-t0*/`; round summary `review/qa/klee-sparks-r2-round-summary.json`; pair read `review/qa/klee-sparks-r2-pair-review-codex-gpt-5.6-sol.md` and its prompt beside it |

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
- **Kokomi stability band (D5)** — no band is declared, so it rides DARK
  (`band = None`). The declaration is QUEUE `S4-G6`; its grading playtest is
  `docs/current/playtest/kokomi-playtest-protocol.md` (unrun, Answers block
  blank).

New registrations add a pointer here and land their packet under
`review/active/`. When one is graded, it moves to the **Graded** table above —
the packet and its raw results stay where they are, unedited (R101b), and the
long active-entry narrative goes to the commit message that moved it.
