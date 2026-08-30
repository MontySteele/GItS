# `KLEESPARK-BT2` — THE RERUN (`klee-sparks-bt2r`)

> **THIS IS NOT A NEW ROUND AND NOT A RE-ROLL.** It is `KLEESPARK-BT2` run
> again on an instrument that can now record its answers. The three boards,
> their seeds, their hands, their assumptions, their forecast questions,
> `slots.yaml`'s two counting slots and the whole `F1`–`F5` slate below are
> **byte-identical to `understudy/turns/klee-sparks-bt2/` except for the turn
> ids**, which carry an `r` so that the first run's sealed records under
> `review/qa/klee-sparks-bt2-t0*/` are not written over. **The first run's
> grades stand exactly as published (R101b)** — packet §24 — and nothing here
> re-reads, re-scores or withdraws one.
>
> **What changed is the INSTRUMENT and only the instrument** (`EB-239`):
> `understudy/seat.py`'s `form_schema()` now declares a `forecast` field, and
> the local tester prints the same schema, so a reader has somewhere to write
> the answers the page has been asking for since `EB-236` item (d). The
> registration in prose is packet **§24.9**.
>
> **Drafted by Claude under R212 item 2 and committed BEFORE the run;
> [USER] batch-countersigns.** Nothing below is re-signed: a moved world means
> re-draft and disclose, and the world that moved is the form schema.

# `KLEESPARK-BT2` — turn manifest and prediction slate

**REGISTERED — NOT RUN. Claude drafts (R212 item 2), [USER] countersigns in
batch.** Three staged boards, `slots.yaml` and the slate below were committed
**before anything was staged, deployed or read**, for the same reason a
prediction slate is. Nothing here has been run; no board has been staged; the
game has not been launched and the Codex seat has not been called.

This is `EB-224`'s **repaired** staging round for *Bag of Tricks*, drafted
under **R229**. The round it repairs is `KLEESPARK-BT1` — registration at
`review/active/klee-sparks-2026-08-29.md` §21, results at §22. This round's
registration in prose is **§23** of the same packet.

## What R229 settled, and what this round is for

`KLEESPARK-BT1` found, off its own `t01` replay, that the priced mode
**refunded its own price inside the same turn**: the bank read 3 → 0 on the
mode and **3 again** after the detonator. Klee's starter relic *Pounding
Surprise* pays **+1 Spark for every Bomb that detonates**
(`klee-mod/KleeCode/Relics/PoundingSurprise.cs`; the sim's twin is the
`spark_on_detonation` hook at `tier0/engine/effects.py:874`), and the priced
mode places exactly three Bombs. The registration had not controlled for it,
and **the blind page did not print relics at all**, so no reader could see it.

R229's ruling, in three parts:

1. *Bag of Tricks* **stays under test in the SHIPPED world** — the starter
   relic is kept, and the round is run with it.
2. The refund is accepted as an **observed TEST CONDITION**, not a design
   approval. Nothing about it licenses a re-price.
3. The arm is **AT RISK under a PRE-REGISTERED RETURN CONDITION**, written
   below as a graded predicate with a number.

Two engineering rows were closed before this round could be drafted, and both
are what let it be written honestly: `EB-238` puts the run's relics on the
page, and `EB-237` lets `slot_plan` see a price that sits at a mode head.
`EB-236` is the check that refuses a board claiming an exclusivity it does not
have — and it refuses `KLEESPARK-BT1`'s `t02`.

## The arm on the board

`proto_spark_mode_bombs` — **Bag of Tricks**, 0 Energy, Skill, Uncommon:

> *Choose one: Place 1 **Bomb** dealing 5 | Spend 3 **Sparks**: place 3
> **Bombs** dealing 5.*

`C.SPARK_ALT_COST_ENABLED` in tier 0 and `-p:PrototypeCards=true` in C#, as
every Sparks round has run. The other prototype row in these hands is
`proto_spark_finisher` (Firework Finale, Spend 3 Sparks, 18 to one) on `t01`
and `t02`. Everything else is a **shipped** Klee card: Kaboom!, Mine Toss,
Duck and Cover, Spirited Away, Run Away!.

**There is no *Quick Fuse* on any board of this round, deliberately.**
`KLEESPARK-BT1` put a free single-purpose `detonate` in three of four hands,
which makes the refund read as a property of one strange card. It is not: any
Attack that gets HP damage through pops the target's Bombs
(`tier0/engine/effects.py`'s `_detonate_bombs_on_hit`; the C# twin is
`Powers/BombPower.cs` with `IBombDetonationListener`). `t01`'s detonator is
**Kaboom!**, a basic card in the starting deck.

## The boards

Every board is `exact_hand: true` and `prototype: true`. The body is 55 HP on
all three and **no line on any board is lethal**. Every seed is a
`KLEESPARK-BT1` seed, recorded ONE-BODY on a Klee run, and every board here
wants one body.

| turn | seed | bank | HP | hand | Energy | what the board is | slot |
|---|---|---|---|---|---|---|---|
| `t01` | `JH4T8MSN10KS` | **3** | 42/62 | Bag of Tricks, **Kaboom!**, Firework Finale, Duck and Cover, Spirited Away | 3 of 4 needed | **A** — the exact *priced mode → ordinary Attack → rival price-3 sink* sequence. The bank returns before the turn ends. **This is the return-condition board.** | `C1` |
| `t02` | `R805DJ56LZHM` | **3** | 42/62 | Bag of Tricks, Firework Finale, Mine Toss, Duck and Cover, Spirited Away | 3 of 4 | **B** — `KLEESPARK-BT1`'s `t02` REPAIRED: the same exclusivity claim, and this time no order of play buys both | `C1` |
| `t03` | `YX7PB48WR7R4` | **3** | **24**/62 | Bag of Tricks, Mine Toss, Duck and Cover, Spirited Away, Run Away! | 3 of 4 | **C** — no Attack and no detonator, so the Bombs SIT: a delayed refund against a telegraphed 16 into 24 HP. The turn is ended and the next turn's bank is read | `C2` |

**Every board forces a trade.** Each hand costs 4 Energy against 3, which is
the thing `KLEESPARK-BT1` never did: its four boards all let 3 Energy pay for
the whole hand, so the telegraph forced no choice, and `intent_insensitive`
refused **seven of its eight forms**. `EB-236`'s `no_forced_trade` check
refuses a resource board that does not force one, and all four of that round's
boards fail it.

**Why `t02`'s claim holds where `KLEESPARK-BT1`'s did not.** The only Attack in
that hand is *Firework Finale* itself, and it has to be paid for before it can
pop anything. Priced mode first → bank 0, three Bombs sit, nothing in hand can
detonate them. Finale first → bank 0, its 18 lands on a body carrying at most
the one Bomb Mine Toss placed, so the relic pays at most 1 and the bank reaches
1, not 3. `EB-236` walks **every** order of play, relic gains included, and
finds none that buys both.

## The forecast — asked before the line, and it is new machinery

`EB-229` found that a blind run's three forecast slots went UNREACHED **not
because the display failed but because the question is never asked**: the
schema is `command` and `thinking`, and the staged form's four questions are
all past tense. This round is the STAGED TWIN of that row.

`forecast:` on a turn file is a list of questions, printed at the **top** of
the blind packet under *Before you decide*, numbered, and answered into the
form's `forecast` list in the same order **before** the line is chosen. A form
that skips it on a board that asked is REFUSED `forecast_missing`; a board that
asks nothing prints no such block and is graded exactly as before. The
questions are asked CONDITIONALLY (*"if you spend 3 Sparks on Bag of
Tricks…"*), so asking them does not recommend a line.

`replay_next_turn: true` on `t03` makes the replay end the turn after the
graded line and take **one more reading**. A staged single turn has no next
turn (packet §11.6 item 1), which is why `KLEESPARK-BT1` could say nothing
about a delayed refund.

## The counting slots (`slots.yaml`), and their ceilings

Computed by `local_tester round --plan-only` over these three boards, before
anything was staged:

```
round of 3 board(s) in R221 B's pre-registered order; seat spot-check every 1; first set = 3; lanes = 1
   1  FIRST  SEAT  lane0  klee-sparks-bt2r-t02   slots=C1  closeness=0.019
   2  FIRST  SEAT  lane0  klee-sparks-bt2r-t01   slots=C1  closeness=0.031
   3  FIRST  SEAT  lane0  klee-sparks-bt2r-t03   slots=C2  closeness=0.117
preflights: every board passes face-defect and assumption checks
SLOT OK   C1: threshold 2, ceiling 2 of 3 board(s)  [klee-sparks-bt2r-t02, klee-sparks-bt2r-t01]
SLOT OK   C2: threshold 1, ceiling 1 of 3 board(s)  [klee-sparks-bt2r-t03]
board design: every board forces a trade, and every declared exclusive pair is exclusive
```

`--first 0` — **every board runs.** R221 B's sequential stopping is switched
off, because every threshold equals its ceiling and each board is the only one
of its kind: stopping early would leave a question unasked rather than an
answer duplicated.

## The DRAFTED prediction slate

**DRAFTED by Claude from written intent (R212 item 2)** — the intent is R229's
three parts above, `KLEESPARK-BT1` §22.4 item 1, and `EB-224`'s acceptance
line. Committed before any board is staged; [USER] countersigns in batch or
vetoes.

**`F1` — THE RETURN CONDITION, first clause: the refund arrives inside the
turn.**
On `t01`, the DECIDING form's `chosen_line` plays *Bag of Tricks* with `choose`
naming the priced mode, plays an Attack at the same enemy, and plays *Firework
Finale* — all three in one turn — AND the replay's wire readings show the Spark
bank at **0** immediately after the mode and **at or above 3** immediately
after the Attack resolves.
*Threshold:* 1 of 1.
*Falsifier:* the bank does not reach 3 again after the detonation; or the line
cannot pay for both.
*UNREACHED — not PREDICTED — where the deciding form is REFUSED, or where the
replayed line does not take the priced mode (`EB-209`; `KLEESPARK-R2`'s `P4`
lesson).*

**`F2` — THE RETURN CONDITION, second clause: the price costs something across
the turn and the next.**
On `t03`, where the replayed line takes the priced mode: the deciding form's
THIRD answer names a concrete thing this turn gave up — Block not gained, or a
card not played for want of Energy — AND the next-turn reading shows the Spark
bank back at **3** at the start of the next turn.
*Threshold:* 1 of 1.
*Falsifier:* the third answer names no cost; or the next-turn bank is not 3.
*UNREACHED where the replayed line does not take the priced mode.*

> **`F1` AND `F2` ARE ONE FINDING AND ARE READ TOGETHER, AND THEY ARE THE
> RETURN CONDITION R229 PRE-REGISTERED.** Written as a graded predicate, with
> the numbers, so it cannot be argued afterwards:
>
> **THE ARM RETURNS TO DESIGN IF EITHER**
> **(a) `F1` is PREDICTED — the bank reads ≥ 3 again after the detonation, on
> the same turn, and the reader pays for both priced uses; OR**
> **(b) `F2`'s form names NO cost given up AND `F2`'s next-turn bank reads 3.**
>
> (a) is *"immediate detonation restores enough bank to play the competing
> sink"*: 3 is the competing sink's exact price and is the number. (b) is
> *"the price otherwise imposes no meaningful opportunity cost across the turn
> and the next"*: the bank comes back one turn later and the reader can name
> nothing it cost. Either one RETURNS the arm. Both PREDICTED is the strongest
> form of the return and is reported as one finding, not two.

**`F3` — the exclusive pair, where the board actually has one.**
On `t02`, the DECIDING form's `chosen_line` pays for **exactly one** of *Bag of
Tricks*'s priced mode and *Firework Finale*, and its SECOND answer names the
other as the line it seriously considered and declined.
*Threshold:* 1 of 1.
*Falsifier:* both priced uses paid in one turn; or the second answer names
neither of them.
*A MISS here is an INSTRUMENT finding and not a design one:* `EB-236`'s check
says no order of play buys both on this board, so a form that does is a defect
in the check or in the build, filed to `BACKLOG`, and it blocks the whole
fight until fixed.

**`F4` — the forecast is asked, and answered before the line.**
On **all three** boards the DECIDING form carries a non-empty `forecast` with
one answer per registered question, and no form is refused `forecast_missing`.
*Threshold:* 3 of 3.
*Falsifier:* a missing or short forecast on any board.
*This is `EB-229`'s staged twin and the slot exists to give the mechanism a
denominator. It is a reading about the INSTRUMENT and moves no design slot.*

**`F5` — the forecast is CORRECT on the board whose arithmetic is the
finding.**
On `t01`, where the reader's line takes the priced mode: the first forecast
answer reads **0** and the second reads **3**.
*Threshold:* 1 of 1.
*Falsifier:* either number is wrong.
*UNREACHED where the line does not take the priced mode, or where `F4` is
MISSED on `t01`.*
*A MISS is a LEGIBILITY finding — the page shows the relic and the reader
still could not do the arithmetic — filed to `BACKLOG`, not a re-price.*

**RECORDED AND NOT GRADED:** the shadow-versus-deciding verdict agreement. A
three-board denominator decides nothing about the seat's chair and `M62` is not
at issue here.

## UNREACHED, ruled in advance

- A **REFUSED deciding form grades its slot UNREACHED, not MISSED** (`EB-209`).
- `F1`, `F2` and `F5` are UNREACHED — never PREDICTED — where the replayed line
  does not reach the play they are about. **Absence of a counterexample is not
  a pass.**
- **Any slot UNREACHED** → not a pass and not a fail, nothing is inferred from
  the absence, and no [USER] row opens on it.
- Where the `EB-227` meter guard refuses mid-round, **the round STOPS at that
  board** and the results section records how many boards were read, rather
  than finishing on a cheaper chair.

## What a MISS does NOT license

**A MISS licenses nothing on its own.** Specifically it does NOT license: a
re-price of the mode's 3; a change to §4.2's price table; a new sink row
(R225); any amendment to, or re-reading of, R225's mode-head clause; the
removal or suppression of *Pounding Surprise*; any LAW or measurement-law
change; or any claim about win rate, balance or fun (R215 B, Guardrail-7).
Claude does not reprice a row on a staged read, and this is registered before
the run so it cannot be argued after it.

**A RETURN under the condition above returns the arm TO DESIGN — to [USER], as
a numbered pick list.** It does not itself change a number, and Claude picks
nothing on it.

## Who grades, and who does not

**The Codex seat decides every board** (`--seat-spot-check 1`). This is a
DESIGN round — an ADVANCE for the arm rests on it — so under `M64` (1) / R224
the deciding chair is the Codex seat on every board, and the round costs more
Codex calls than the standing three for exactly that reason.

**The local seat sits in the SHADOW chair** (`--seat-mode shadow`, R222 B): it
reads every packet, it is graded, it is never the deciding verdict and it is
never replayed.

**Fresh-Opus is NOT the deciding chair here.** R222 B seats it for INSTRUMENT
rounds; `M64` (1) takes it out of a round on which an ADVANCE rests. The row is
`authored_by: [claude]`, so a same-family deciding read would not be
author-disjoint under R217 C.

## The Codex budget, and the meter

- **Plan: 3 deciding seat reads + 1 pair read = 4 Codex calls expected, cap 9
  for the round** (≈3 per board). Three boards is the minimum that carries the
  three distinct questions — the immediate refund, the exclusive pair, and the
  delayed refund; a fourth would add a duplicate and a call.
- **The meter, read while this registration was drafted:** `5h 48%`, resetting
  **16:36 EDT**; the round is planned for after that reset. `EB-227`'s guard
  refuses at **85%** of the five-hour window and 50% of the week, and the
  operator reads the meter again immediately before the round.
- **Preconditions, each of which stops the round:** the game lock
  `gits-game.lock` under the user's Temp directory absent; Steam running; the
  installed dev build carrying the row, proven read-only off the deployed
  `mods\klee\manifest.json` and the installed `klee.dll` before anything is
  staged.

## What these boards still cannot do

**The tier0 mirror cannot see a mode.** `closeness` enumerates CARD SETS, so
its lines read *"Bag of Tricks + Kaboom! + Firework Finale"* without saying
which mode. Every gap below is a bound on card sets and **not** on the choice
this round is about; the packet and every replay read the LIVE game.

| turn | gap | top line | runner-up | lines |
|---|---|---|---|---|
| `t01` | 0.0313 | 38.3 | 37.1 | 5 |
| `t02` | 0.0194 | 36.1 | 35.4 | 5 |
| `t03` | 0.1174 | 40.9 | 36.1 | 5 |

**All three SURVIVE**: no line dominates by more than the derived gap
(`DOMINANCE_GAP` 0.5).

**The mirror cannot see the relic either.** `closeness` scores the board
through the pilot's own surface with no run layer, so the refund is invisible
to it; that is one more reason the numbers above bound card sets and nothing
else.

**It still cannot draft, and one turn plus one reading is not a fight.**
`loader._pool_substitutions` returns `{}` for Klee, so nothing here is picked
by a drafter, and `t03` buys exactly ONE turn of the future and no more.
`EB-224`'s whole fight stays owed and this round does not touch it.
