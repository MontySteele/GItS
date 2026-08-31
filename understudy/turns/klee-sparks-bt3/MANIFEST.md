# `KLEESPARK-BT3` — turn manifest and prediction slate

**REGISTERED — NOT RUN. Claude drafts (R212 item 2), [USER] countersigns in
batch.** Two staged boards, `slots.yaml` and the slate below were committed
**before anything was staged, deployed or read**, for the same reason a
prediction slate is. Nothing here has been run; no board has been staged; the
game has not been launched and the Codex seat has not been called.

This is `EB-224`'s **third** staging round for *Bag of Tricks*, drafted from
**R230**'s written intent. The round it repairs is `KLEESPARK-BT2` THE RERUN —
registration at `review/active/klee-sparks-2026-08-29.md` §24.9, results at
§24.9.5–§24.9.10. This round's registration in prose is **§25** of the same
packet, and the whole fight registered beside it there is `KLEESPARK-W5`,
which runs AFTER this round.

## What R230 ruled, and what this round is for

R230 (2026-08-30) took the four-item pick list at §24.9.9 at **option (3),
QUALIFIED**: the refund loop is accepted as the card's **deliberate bridge
mechanic** and the design intent is rewritten to say so. The arm does not
return to design a second time. Two things follow, and this round is the first
of them.

**1. The corrected economics, which is what the ruling turns on.** §24.9.9 had
said the priced mode is *"net-free where an ordinary Attack lands the same
turn"*. That was wrong. On a bank of 3 with a detonator in hand:

- **free mode** — one Bomb, the Attack pops it, *Pounding Surprise* pays 1:
  the bank goes **3 → 4**;
- **priced mode** — three Bombs, the Attack pops all three, the relic pays 3:
  the bank goes **3 → 0 → 3**.

The player ends on **3 instead of 4**. The trade is **one net Spark for two
extra Bombs — 10 extra damage** — behind a **three-Spark up-front liquidity
requirement** the free mode does not carry. A same-turn detonator changes
**when** that liquidity returns and **whether** another sink can be chained
onto it; it does not make the two modes equivalent.

**2. The `F2` registration correction, owed before any re-pose.** R229's second
predicate has graded UNREACHED three rounds running and has never been
answered. As written (`understudy/turns/klee-sparks-bt2r/MANIFEST.md`, `F2`) it
demands a next-turn bank of **exactly 3** — but that board also granted *Mine
Toss*, which places a Bomb of its own, so the proposed line put **four** Bombs
down and the refund was **4**. The reader forecast 4 and was right; the
predicate would have failed it anyway. R230, verbatim: *"a re-posed `F2` must
grade the refund ATTRIBUTABLE TO Bag of Tricks' own Bombs — at least 3 — or
else the extra Bomb source must leave the board entirely."*

**This round takes the second repair, which is the one with no arithmetic in
it.** *Mine Toss* is gone from both boards; nothing in either hand places a
Bomb except the card under test, and neither board starts with a Bomb on it.
Every Spark the relic pays back is therefore attributable to *Bag of Tricks*
**by construction rather than by subtraction**, and `G1`'s predicate below is
written both ways — the attributable form AND the construction that makes it
unarguable — so it reads the same whichever way it is checked.

**The published boards and MANIFEST of `klee-sparks-bt2r` are NOT edited
(R101b).** They are the record of a run that has already happened and they
stand as published. This is a new document.

## The arm on the board

`proto_spark_mode_bombs` — **Bag of Tricks**, 0 Energy, Skill, Uncommon:

> *Choose one: Place 1 **Bomb** dealing 5 | Spend 3 **Sparks**: place 3
> **Bombs** dealing 5.*

`C.SPARK_ALT_COST_ENABLED` in tier 0 and `-p:PrototypeCards=true` in C#, as
every Sparks round has run. Everything else in both hands is a **shipped** Klee
card: Duck and Cover, Spirited Away, Run Away!. There is no *Quick Fuse*, no
*Mine Toss* and no Attack on any board of this round.

## The boards

Both are `exact_hand: true`, `prototype: true` and `replay_next_turn: true`.
Both seeds are recorded ONE-BODY on a Klee run across three earlier rounds, and
both boards want one body.

| turn | seed | bank | HP | body | hand | Energy | what the board is | slot |
|---|---|---|---|---|---|---|---|---|
| `t01` | `YX7PB48WR7R4` | **3** | **24**/62 | 40 | Bag of Tricks, Duck and Cover, Spirited Away, Run Away! | 2 of 3 needed | **A** — the delayed refund with the pressure ON: a telegraphed 16 into 24 HP, so the Block lines are urgent and the bank's payout is a whole enemy turn away | `C1` |
| `t02` | `R805DJ56LZHM` | **3** | **40**/62 | 46 | the same four cards | 2 of 3 | **B** — the same question with the pressure OFF. If the liquidity cost can only be named where the player is nearly dead, the cost is the telegraph's and not the card's | `C1` |

**Why two boards and not one.** `F2` has graded UNREACHED three rounds running,
and twice because a single deciding form was REFUSED. A slot posed on one board
has a denominator of one and one refusal takes it to zero, which is exactly
what happened at §24 and again at §24.9. Two boards is the cheapest repair:
one refusal leaves the slot a board still standing.

**Every board forces a trade.** Each hand costs 0 + 1 + 2 + 0 = **3 Energy
against 2**, which `EB-236`'s `no_forced_trade` check requires and which
`KLEESPARK-BT1` never did — its four boards all let the Energy pay for the
whole hand and seven of its eight forms were refused `intent_insensitive`.
**The Energy is the round's one other change, and it is disclosed:** dropping
*Mine Toss* out of `klee-sparks-bt2r-t03`'s hand would have left three cards
costing 3 against 3 available, so the Energy moves 3 → 2, which is the minimum
that keeps the trade forced. No card is added.

## `EB-240`'s `expects:` block — declared here, and it is new

Both boards carry a structured `expects:` declaration, and the stage refuses on
a mismatch before a packet is written. It is here because `klee-sparks-bt2r`
printed two assumptions that were false:

- every board asserted *"the run carries Klee's starting relic and no other"*
  while the page printed **two**, *Pounding Surprise* and *Fishing Rod* (the
  run-start gift the staging path takes; it does nothing in a combat). Both are
  now DECLARED and compared against the wire's relic list.
  **DISCLOSURE (`EB-243`, R212 re-draft, 2026-08-30).** Both boards registered
  the gift as *Fishing Rod*; read off the wire before this round ran, the gift
  is *Stone Humidifier* on `t01`'s seed `YX7PB48WR7R4` and *Scroll Boxes* on
  `t02`'s seed `R805DJ56LZHM` — a DIFFERENT gift on each, so it is seed-derived
  and not a constant of the staging path, which is what the single registered
  name assumed. Both `expects.relics` blocks are **re-drafted to what is true
  now and the change is disclosed, never re-signed**: the R231 countersign
  stands, the slate `G1`–`G4` is untouched, no threshold moves, and the
  `hp.first` legs (40 and 46) matched the wire unchanged. The re-draft was
  committed BEFORE the round ran.
- every board wrote `set_hp: {who: first, amount: 55}` and the bodies read
  **45 / 46 / 40**. These boards write **no enemy HP at all**: they declare the
  body the seed is recorded at (40 and 46) and the stage refuses on a different
  one, rather than writing a number the game may not take. Every `set_hp` the
  boards DO write — the player's — is read back automatically.

**If the stage refuses on either declaration, the round STOPS at that board and
nothing is read.** The declaration is corrected from the observed value, the
correction is disclosed in the results section, and the board is re-staged from
the corrected file — a re-attempt with nothing read, on `EB-191`'s precedent,
and not a re-roll.

## The counting slots (`slots.yaml`), and their ceilings

Computed by `local_tester round --plan-only` over these two boards, before
anything was staged:

```
round of 2 board(s) in R221 B's pre-registered order; seat spot-check every 4; first set = 2; lanes = 1
   1  FIRST  SEAT  lane0  klee-sparks-bt3-t01   slots=C1  closeness=0.135
   2  FIRST        lane0  klee-sparks-bt3-t02   slots=C1  closeness=0.135
preflights: every board passes face-defect and assumption checks
SLOT OK   C1: threshold 2, ceiling 2 of 2 board(s)  [klee-sparks-bt3-t01, klee-sparks-bt3-t02]
board design: every board forces a trade, and every declared exclusive pair is exclusive
```

The round is run with `--first 0` — **every board runs** — and with
`--seat-spot-check 1`, which is the deciding-chair setting below and not the
default the plan above prints.

## The DRAFTED prediction slate

**DRAFTED by Claude from written intent (R212 item 2)** — the intent is R230 as
recorded at packet §24.9.11 and `review/active/sitting-2026-08-30.md` §R230,
and the rewritten design intent in `docs/prototype-surface.yaml` under *ARM 4:
two prices for one card*. Committed before any board is staged; [USER]
countersigns in batch or vetoes.

**`G1` — `F2` RE-POSED under R230's corrected predicate: the locked liquidity
costs something, and it comes back.**
On a board whose replayed line takes the priced mode: **(i)** the deciding
form's THIRD answer names a concrete thing this turn gave up — Block not
gained, or a card not played for want of Energy — **AND (ii)** the next-turn
wire reading shows the Spark bank at **3 or more**, every Spark of which is
attributable to *Bag of Tricks*' own three Bombs, there being no other Bomb
source in the hand or on the board.
*Threshold:* **2 of 2 boards.**
*Where exactly one board's deciding form is REFUSED, `G1` grades on the
remaining board at 1 of 1 and the round's results say so; where both are
refused, `G1` is UNREACHED.*
*Falsifier:* the third answer names no cost; or the next-turn bank reads below
3 on a line that took the priced mode.
*UNREACHED where the replayed line does not take the priced mode (`EB-209`,
`KLEESPARK-R2`'s `P4` lesson). **Absence of a counterexample is not a pass.***

**`G2` — the pressure control: the cost is the card's and not the telegraph's.**
`G1`'s two halves are read board by board. `G2` is the comparison BETWEEN them:
on `t02`, where the incoming 16 lands on 40 HP rather than 24, the third answer
still names a concrete thing given up.
*Threshold:* 1 of 1 (`t02`).
*Falsifier:* `t02`'s third answer names nothing, or names only the incoming
damage.
*UNREACHED where `t02`'s form is refused or its line does not take the priced
mode.*
*`G2` is a SUBSET of `G1` by construction and is reported as such — it is not
a second independent observation and the results section says so.*

**`G3` — the forecast is asked, and answered before the line.**
On **both** boards the DECIDING form carries a non-empty `forecast` with one
answer per registered question, and no form is refused `forecast_missing`.
*Threshold:* 2 of 2.
*Falsifier:* a missing or short forecast on either board.
*This is the staged forecast channel's denominator on its second round —
`EB-239` closed the schema gap that MISSED this slot's twin (`F4`) at 0 of 3 in
§24. It is a reading about the INSTRUMENT and moves no design slot.*

**`G4` — the forecast is CORRECT on the delayed arithmetic.**
On a board whose line takes the priced mode: the first forecast answer reads
**0** (the bank at the end of THIS turn) and the second reads **3** (the bank
at the start of the NEXT turn, after the Bombs pop and the relic pays).
*Threshold:* 1 of 2 — one board is enough to establish that the arithmetic is
legible, and the round does not claim more.
*Falsifier:* both boards' lines take the priced mode and neither pair of
numbers is right.
*UNREACHED where no line takes the priced mode, or where `G3` is MISSED on
every board.*
*A MISS is a LEGIBILITY finding — the page shows the relic, the turn is ended
for the reader, and the reader still could not do the arithmetic — filed to
`BACKLOG`, never a re-price.*

**RECORDED AND NOT GRADED:** the shadow-versus-deciding verdict agreement. A
two-board denominator decides nothing about the seat's chair and `M62` is not
at issue here.

## What each result decides (R206)

- **`G1` PREDICTED** — the delayed half of R230's intent is graded for the
  first time in four rounds and holds: the liquidity is a real cost and the
  refund is the mode's own. `EB-224`'s staged half is DISCHARGED and
  `KLEESPARK-W5`, the whole fight registered at §25, is the next and last
  thing the row owes.
- **`G1` MISSED on (i)** — a reader that takes the priced mode with a
  telegraphed swing coming and can name nothing it cost is evidence that the
  liquidity requirement is not experienced as one. **This does NOT return the
  arm**: R230 ruled the direction and this round does not reopen it. It returns
  to [USER] as a NUMBERED PICK on the written INTENT — whether the "real
  liquidity, locked up" clause survives a board where nobody felt it — and the
  whole fight is not run until that pick is answered.
- **`G1` MISSED on (ii)** — the next-turn bank reads below 3 with no other Bomb
  source anywhere. That is an ENGINE finding, not a design one: either the
  turn-start sweep did not pop all three Bombs or the relic did not pay for all
  three. It is filed to `BACKLOG` as a defect and it BLOCKS the whole fight.
- **`G1` UNREACHED on both boards** — nothing is inferred from the absence and
  no [USER] row opens; the act is a repaired board, not a reading.
- **`G3` MISSED** — the forecast channel is still not working after `EB-239`,
  which is an instrument row and blocks `KLEESPARK-W5`'s use of the same
  channel.

## UNREACHED, ruled in advance

- A **REFUSED deciding form grades its slot UNREACHED, not MISSED** (`EB-209`).
- `G1`, `G2` and `G4` are UNREACHED — never PREDICTED — where the replayed line
  does not reach the play they are about.
- **Any slot UNREACHED** → not a pass and not a fail, nothing is inferred from
  the absence, and no [USER] row opens on it.
- Where the `EB-227` meter guard refuses mid-round, **the round STOPS at that
  board** and the results section records how many boards were read, rather
  than finishing on a cheaper chair.
- Where the `EB-240` preflight refuses a stage, the round stops at that board
  under the rule above.

## What a MISS does NOT license

**A MISS licenses nothing on its own.** Specifically it does NOT license: a
re-price of the mode's 3; a change to §4.2's price table; a new sink row
(R225); any amendment to, or re-reading of, R225's mode-head clause; the
removal or suppression of *Pounding Surprise*; any LAW or measurement-law
change; or any claim about win rate, balance or fun (R215 B, Guardrail-7).
**R230's ruled direction is not reopened by any result of this round** — it was
ruled on the rerun's evidence and this round measures the half that ruling left
owed.

## Who grades, and who does not

**The Codex seat decides every board** (`--seat-spot-check 1`). This is a
DESIGN round, so under `M64` (1) / R224 the deciding chair is the Codex seat on
every board. **Fresh-Opus is NOT seated**: the row is `authored_by: [claude]`
and a same-family deciding read would not be author-disjoint under R217 C.
**The local seat sits SHADOW** (`--seat-mode shadow`, R222 B): read, recorded,
never deciding and never replayed.

## The Codex budget, the meter and the stop lines

- **Plan: 2 deciding seat reads + 1 pair read = 3 Codex calls expected, cap 6
  for the round.** Two boards is the minimum that survives one refusal on the
  slot the round exists to grade.
- **`EB-227`'s guard** refuses at 85% of the five-hour window and 50% of the
  week; the operator reads the meter immediately before the round and records
  both readings with the results.
- **Preconditions, each of which stops the round:** the game lock
  `gits-game.lock` under the user's Temp directory absent; Steam running; the
  installed dev build carrying the row, proven read-only off the deployed
  `mods\klee\manifest.json` and the installed `klee.dll` before anything is
  staged; and R225's three-fight soak gate green.

## What these boards still cannot do

**The tier0 mirror cannot see a mode.** `closeness` enumerates CARD SETS, so
its 0.135 gaps bound card sets and **not** the choice this round is about. Both
boards SURVIVE (`DOMINANCE_GAP` 0.5). The mirror cannot see the relic either —
it scores through the pilot's surface with no run layer — which is one more
reason those numbers bound nothing here.

**One turn plus one reading is not a fight.** `t01` and `t02` each buy exactly
ONE turn of the future. `EB-224`'s whole fight stays owed and is registered
separately as `KLEESPARK-W5` at packet §25, which runs after this round and
carries R230's pre-registered collapse condition.

**Nothing here is quotable as balance.** Every number this round produces is
about a PROTOTYPE row (R215 B) and every reader sentence is R217 G iteration
feedback: one model's account, never validation and never balance evidence.
