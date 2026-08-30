# `KLEESPARK-BT1` — turn manifest and prediction slate

Four staged boards, **`EB-224`'s staging round for *Bag of Tricks***. The
registration is `docs/current/EXPERIMENTS.md` → **`KLEESPARK-BT1`**; the arm's
packet is `review/active/klee-sparks-2026-08-29.md`, whose **§21** carries this
registration in prose and whose **§22** will carry the results. The row this
round discharges the first half of is `BACKLOG.md` → `EB-224`, whose next
action reads *stage, grade, replay, whole-fight*; this round is **stage, grade
and replay**, and the whole fight stays owed.

**This file, the four boards, `slots.yaml` and the slate below were committed
BEFORE anything was staged, deployed or read**, for the same reason a
prediction slate is (R212 item 2): a board written after a reading is not a
board, it is a result. [USER] countersigns in batch or vetoes.

## The arm on the board — one row, and the first of its kind

`proto_spark_mode_bombs` — **Bag of Tricks**, 0 Energy, Skill, Uncommon:

> *Choose one: Place 1 **Bomb** dealing 5 | Spend 3 **Sparks**: place 3 **Bombs**
> dealing 5.*

It is **the first row in the tree whose price sits at the HEAD OF A MODE**
rather than at the card's top level. The doctrine seat held the arm on that
clause twice (klee-slice-1 packet §6.1, §6.1.1); R225 amended the written
clause on 2026-08-30 to read *top level **or** the head of a `choose_one` mode,
and nothing nested or conditional*, and the arm proceeds. It runs on `EB-182`'s
mode-price machinery: **an unaffordable mode is not offered** on the
choose-a-card screen — omission, not greying, because the 0.111.0 decompile
gives that screen no per-option disabled state — a card stays playable while
any mode is affordable, and a fully priced-out card is refused with the price
and the bank named.

The other prototype rows in these hands are `proto_spark_finisher` (Firework
Finale, Spend 3 Sparks, 18 to one) on `t02` and `proto_pop_spark` (Powder Pop,
place 1 Bomb and gain 1 Spark) on `t04`. Everything else is a **shipped** Klee
card: Quick Fuse, Kaboom!, Duck and Cover.

**`C.SPARK_ALT_COST_ENABLED` in tier 0 and `-p:PrototypeCards=true` in C#**, as
every Sparks round has run.

## The question this round exists to answer

Two halves, and they are not the same question:

1. **Does a price of 3 that buys Bomb PLACEMENT create a real
   spend-versus-hold / one-versus-three decision?** — i.e. is the expensive
   mode *taken* on a board where three Bombs plainly pay, and *declined* on a
   board where the same bank has a better home?
2. **Is the mode-head price LEGIBLE?** — does the face show the price, is the
   unaffordable mode omitted per `EB-182`, and does the bank get debited
   exactly once when the mode is taken?

**What this round does NOT ask.** Whether the card is fun; whether 3 is the
right number; anything about win rate. Nothing measured on a prototype row is
quotable anywhere (R215 B), and a staged board is comparable to no run
(Guardrail-7).

## The boards

Every board is `exact_hand: true` and `prototype: true`. Player HP is 42/62,
Block 0, Energy 3 and the enemy is set to 40 HP on all four, so **the only
things that move across the round are the bank and one card in hand**. The bank
is written with `set_power` on `SPARK_POWER`. Every seed is a
`KLEESPARK-R2` seed **recorded one-body on a Klee run**, and every board of
this round wants one body — so unlike `KLEESPARK-R2`'s `P3`, no slot here can
go UNREACHED on an encounter roll.

| turn | seed | bank | hand | what the board is | slots |
|---|---|---|---|---|---|
| `t01` | `JH4T8MSN10KS` | **3** | Bag of Tricks, Quick Fuse, Kaboom!, Duck and Cover | **A** — three Bombs pay (22 against 12) and nothing else wants the bank | `B1` |
| `t02` | `R805DJ56LZHM` | **3** | Bag of Tricks, **Firework Finale**, Quick Fuse, Duck and Cover | **B** — `t01` with one card swapped: the bank buys the mode **or** the rival, and the rival is worth more (23 against 15) | `B2` |
| `t03` | `YX7PB48WR7R4` | **2** | Bag of Tricks, Quick Fuse, Kaboom!, Duck and Cover | **C** — `t01` at a bank one short, with no `gain_spark` in hand: the priced mode must be OMITTED and the card must stay playable | `B3` |
| `t04` | `XT4BE7LFY5XH` | **2** | Bag of Tricks, **Powder Pop**, Quick Fuse, Kaboom! | **D** — one short, but the hand holds the missing Spark: affordability must RECOMPUTE inside the turn | `B3` |

**The matched pairs are the design.** `t01`/`t02` is the *bank ≥ 3* pair and it
turns on one swapped card, so a reader who takes the priced mode on both is
taking it out of habit rather than off the board. `t01`/`t03` is the
*bank ≥ 3 versus bank < 3* pair and it turns on one number. `t03`/`t04` splits
the omission rule's two halves: withheld when short, opened when the bank is
raised mid-turn.

**Why Quick Fuse is in three of the four hands.** Bombs detonate at the START of
the player's turn (`combat.py`'s turn-start sweep), so a Bomb placed now is
next turn's damage. Quick Fuse (0 Energy, shipped Common, `detonate` on one
enemy) makes the Bomb payload readable ON THIS TURN, which is the only way a
one-turn packet can put 15 damage and 5 damage side by side. It prices no
Sparks and moves no slot.

**No line on any board is lethal.** The enemy is 40 on all four and the largest
total is 30.0 (`t01`'s mirrored top line).

## The counting slots (`slots.yaml`), and their ceilings

Computed by `local_tester round --plan-only` over these four boards, before
anything was staged:

```
round of 4 board(s) in R221 B's pre-registered order; seat spot-check every 1; first set = 4; lanes = 1
   1  FIRST  SEAT  lane0  klee-sparks-bt1-t01   slots=B1  closeness=0.000
   2  FIRST  SEAT  lane0  klee-sparks-bt1-t02   slots=B2  closeness=0.000
   3  FIRST  SEAT  lane0  klee-sparks-bt1-t03   slots=B3  closeness=0.000
   4  FIRST  SEAT  lane0  klee-sparks-bt1-t04   slots=B3  closeness=0.000
preflights: every board passes face-defect and assumption checks
SLOT OK   B1: threshold 1, ceiling 1 of 4 board(s)  [klee-sparks-bt1-t01]
SLOT OK   B2: threshold 1, ceiling 1 of 4 board(s)  [klee-sparks-bt1-t02]
SLOT OK   B3: threshold 2, ceiling 2 of 4 board(s)  [klee-sparks-bt1-t03, klee-sparks-bt1-t04]
```

`--first 0` — **every board runs**. R221 B's sequential stopping is deliberately
switched off, because every threshold here equals its ceiling and each board is
the only one of its kind: stopping early would leave a question unasked rather
than an answer duplicated.

## The DRAFTED prediction slate

**DRAFTED by Claude from written intent (R212 item 2)** — the intent is the
klee-slice-1 packet §6.1/§6.1.1 (the arm as authored and twice held), R225's
amended clause, and `EB-224`'s acceptance line. Committed before any board was
staged; [USER] countersigns in batch or vetoes within five days.

Every falsifier is mechanical: it is read off a form, off an `execute-*.json`
replay record, or off `review/qa/klee-sparks-bt1-round-summary.json`, and no
model is in the grading loop.

**`P1` — the expensive mode is TAKEN where three Bombs pay.**
On `t01`, the DECIDING form's `chosen_line` plays *Bag of Tricks* and its
`choose` key names the priced mode (*"Spend 3 Sparks: place 3 Bombs dealing
5"*).
*Threshold:* 1 of 1.
*Falsifier:* the line omits Bag of Tricks, or its `choose` names the free mode.
*A REFUSED deciding form on `t01` grades this slot **UNREACHED**, not MISSED*
— a refused form is not a reading (R221 B; `EB-209`).

**`P2` — the expensive mode is DECLINED where the bank has a better home.**
On `t02`, the DECIDING form's `chosen_line` plays *Bag of Tricks* with its
`choose` key naming the FREE mode (*"Place 1 Bomb dealing 5"*), **and** plays
*Firework Finale*.
*Threshold:* 1 of 1.
*Falsifier:* the `choose` key names the priced mode; or Bag of Tricks is played
on the free mode and Firework Finale is not, leaving the bank unspent on a
board where the whole question is where it goes.
*UNREACHED on a refused deciding form, as `P1`.*

> **`P1` AND `P2` ARE ONE FINDING AND ARE READ TOGETHER.** Both PREDICTED is
> the only result that says the decision is REAL — driven by the board rather
> than by a habit of buying the expensive thing or a habit of hoarding. Either
> one alone is not that result and is not reported as one, and this is
> registered here so it cannot be assembled afterwards.

**`P3` — the price is legible below the bank.**
On **both** `B3` boards (`t03`, `t04`), the DECIDING form contains no claim that
the priced mode is available at a bank of 2 — no answer names three Bombs as a
thing it can do this turn *without first raising the bank* — and
`misreads.free_card_misreads` fires on neither board.
*Threshold:* 2 of 2.
*Falsifier:* on either board, a form asserting the 3-Bomb mode as playable off
the printed face at a bank of 2, or a `free_card_misreads` hit.
*`t04` is not a counterexample when the form plans **Powder Pop first**: the
board is built so the bank CAN reach 3 inside the turn, and saying so is a
correct reading, not a misread. The falsifier is a claim of availability
WITHOUT the raise.*

**`P4` — below the price the mode is not offered, and the card is still
playable.**
On `t03`, WHERE THE REPLAYED DECIDING LINE PLAYS BAG OF TRICKS: the play is
accepted, and the modal record in `execute-*.json` either raises no
selection screen at all or raises one whose `offered` list **does not contain**
*"Spend 3 Sparks: place 3 Bombs dealing 5"*.
*Threshold:* 1 of 1.
*Falsifier:* the priced mode appears among the offers at a bank of 2, or the
play is refused.
*Where `t03`'s replayed line does not play Bag of Tricks at all, `P4` is
**UNREACHED** and is recorded UNREACHED — it is **not** scored PREDICTED by the
absence of a counterexample. This is `KLEESPARK-R2`'s `P4` lesson, applied in
advance.*

**`P5` — the mode price is charged exactly once, and pays out what it prints.**
On `t01`, WHERE THE REPLAYED DECIDING LINE PLAYS BAG OF TRICKS ON THE PRICED
MODE: the `offered` list contains **both** mode texts, the post-play Spark bank
reads exactly **0**, and the target carries **3** Bombs.
*Threshold:* 1 of 1.
*Falsifier:* fewer than two offers at a bank of 3; a post-play bank other than
0; a Bomb count other than 3.
*UNREACHED — not PREDICTED — where the replayed line does not play the priced
mode. `P5` is the mode-head DEBIT check: `EB-224`'s build closed a codegen gap
where a priced mode paid out undebited, and this is the live half of that.*

**RECORDED AND NOT GRADED:** the shadow-versus-deciding verdict agreement
(`round-summary.json`). `M62`'s two-part criterion is not at issue in this
round and a four-board denominator decides nothing about the seat's chair.

## What each result DECIDES, and what a MISS does NOT license

- **`P1` and `P2` both PREDICTED** → the mode price poses a real
  one-versus-three decision at the staged surface. `EB-224`'s staged half is
  discharged and the row advances to its remaining next action — the whole
  fight — **unchanged**. No number moves.
- **Either `P1` or `P2` MISSED** → the decision is not posed at the staged
  surface, and it returns to [USER] as a numbered pick list in the results
  section. **A MISS licenses nothing on its own.** Specifically it does NOT
  license: a re-price of the mode's 3; a change to §4.2's price table; a new
  sink row (R225); any amendment to, or re-reading of, R225's mode-head clause;
  any LAW change; any claim about win rate, balance or fun (R215 B,
  Guardrail-7). Claude does not reprice a row on a staged read, and this is
  registered before the run so that it cannot be argued afterwards.
- **`P3` MISSED** → the price is not legible below the bank, which is a FACE
  finding, and it goes to `BACKLOG` as a defect candidate with the failing form
  attached — not to a re-price.
- **`P4` or `P5` MISSED** → an `EB-182`/codegen defect on this row, filed to
  `BACKLOG`, and it **blocks** `EB-224`'s whole-fight step until fixed. A
  display or debit defect is engineering; it is not a design result and it
  moves no design slot.
- **Any slot UNREACHED** → it is not a pass and not a fail, nothing is inferred
  from the absence, and no [USER] row opens on it.

## Who grades, and who does not

**The Codex seat decides every board.** This is a **DESIGN round** — an
ADVANCE for the arm rests on it — so under `M64` (1)/R224 the deciding chair is
the Codex seat on **every** board (`--seat-spot-check 1`), and the round costs
more Codex calls than the standing three for exactly that reason.

**The local seat sits in the SHADOW chair** (`--seat-mode shadow`, R222 B): it
reads every packet, it is graded, it is never the deciding verdict and it is
never replayed.

**Fresh-Opus is NOT the deciding chair here.** R222 B seats it for INSTRUMENT
rounds; `M64` (1) takes it out of a round on which an ADVANCE rests, and this
is one. The author of this row is Claude (`authored_by: [claude]` on the sheet
and stated there), so a same-family deciding read would not be author-disjoint
under R217 C — which is the whole reason the split exists.

## The Codex budget, and the meter before the run

- **Plan:** 4 boards × 1 deciding seat read = **4 calls**, plus **1** pair read
  of the graded round = **5 calls expected**, against a **cap of 15** for the
  round. Four boards is the minimum that carries the four distinct questions;
  a fifth board would add a duplicate and a Codex call.
- **The meter, read before anything was staged:**
  `5h 40% (resets 16:36 EDT) · week 25% (resets Sep 05 17:58)`.
- `EB-227`'s guard refuses at **85%** of the five-hour window and **50%** of the
  week. The round's expected spend is well inside both; if the guard refuses
  mid-round the round STOPS at that board and the packet records how many
  boards were read, rather than finishing on a cheaper chair.

## What these boards still cannot do

**The tier0 mirror cannot see a mode.** `closeness` enumerates CARD SETS, so
its lines say *"Bag of Tricks + Quick Fuse + Kaboom!"* without saying which
mode — which is why `t02`'s mirrored top line is not the line `P2` predicts.
Every gap below is therefore a bound on card sets and **not** on the choice this
round is about, and the packet and every replay read the LIVE game.

| turn | gap | top line | runner-up | lines |
|---|---|---|---|---|
| `t01` | 0.0000 | 30.000 | 30.000 | 15 |
| `t02` | 0.0000 | 22.400 | 22.400 | 15 |
| `t03` | 0.0000 | 19.000 | 19.000 | 15 |
| `t04` | 0.0000 | 30.020 | 30.020 | 15 |

**All four SURVIVE**: no line dominates by more than the derived gap
(`DOMINANCE_GAP` 0.5).

**`slot_plan` cannot see a mode price either.** `_spark_prices` reads a
top-level `spend_spark` and nothing else, so *Bag of Tricks* is invisible to
`affordable_spark_uses` on every board here. `slots.yaml` says so at length and
writes every predicate about the OTHER Spark cards; `affordable_spark_uses == 0`
reads *"no other Spark sink"*, never *"no Spark sink"*. Making `slot_plan`
mode-aware is engineering this round does not need and does not do.

**It still cannot draft, and it still cannot ask a face-and-turn question.**
`loader._pool_substitutions` returns `{}` for Klee, so nothing here was picked
by a drafter; and a staged single turn has no memory of what a bank was held
for. §11.6 item 1 is unchanged, and whole-fight play — `EB-224`'s remaining
next action — is the instrument for it.
