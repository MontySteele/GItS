# Kokomi slice 2, round 2 — turn manifest

**STAGING IS HELD ON QUEUE `M67`, as of 2026-08-30 — and `M67` is no longer the
accrual rule.** R226
answered accrual — uncapped, 1 per Exhaust of one of her own cards, Companions
included, spent only by the Bake-Kurage — and added that **no card prints a
Charge price**. `M67` is re-scoped to that clause's CONSEQUENCE, and under its
default option (1) **these four boards are MOOT**: both re-boarded arms price
Charge (`t01`/`t02` arm 1, `t03`/`t04` arm 4), so they retire with their arms.
A round-2 run was scheduled on 2026-08-30 and stopped here unstaged — no board
staged, no model called. Nothing is deleted until `M67` is ruled, because the
consequence reaches two ADVANCED arms and is [USER]'s to see. Everything below
is the design of the boards and is unchanged; the round-1 prescriptions it
encodes carry to `KURAGEMEM002`'s board design, not to a re-stage here.

Four staged turns, two matched pairs. **This round exists only to answer the
two RETURNs round 1 left**, and it changes nothing else: the two arms that
ADVANCED (`t03`/`t04` threshold, `t05`/`t06` mode) are not re-run, no printed
card number moved anywhere (R213 freeze), and no register row is minted or
closed here. `EB-183`, the fifth pair, is deliberately **not built** — the run's
own reading (packet §9, *the fifth pair, sequenced*) says arm 4's board has to
be proved able to separate a Muster arm at all before anything is built against
it. *(That reading was PICK 3 when this file was written; §9 was renumbered at
`a1df7d6`, which took three of the five picks as iteration calls and left two —
the surviving second of which is now `M67`.)*

**Nothing in this file rates an arm.** The designer of these rows may not grade
them (R213's first guard). The columns record what was set and why; the
four-question form is somebody else's. Under R215 B no number measured on a
prototype row is quotable — the closeness column is the exception, because it
reads the **turn** and not the sheet.

## What round 1 asked for, in the reviewer's own words

Round 1 graded sixteen forms across two graders and its pair read returned two
of the four arms. **Both RETURNs returned the BOARD, not the card**, and each
came with a prescription. This round is those two prescriptions and nothing
more.

* **Arm 1, the spend shape** (round 1 `t01`/`t02`) — *"Only the numbers
  changed: both halves presented the same damage-versus-Block allocation, with
  the prototype simply offering more damage while consuming Charge."* What it
  needs: *"include another current-turn Charge use or reader so spending six
  Charge creates an observable sacrifice rather than merely a future
  hypothetical."*
* **Arm 4, the formation shape** (round 1 `t07`/`t08`) — *"Both shipped and
  prototype halves chose the identical three cheap cards; replacing Charge gain
  with a Charge payment did not alter the realized decision."* What it needs:
  *"give Muster an observable near-term payoff and a credible window to choose
  it, so Levy's Charge payment competes with known value rather than
  unspecified randomness under incoming damage."*

## The two repairs, one per arm

**A pair is re-staged together**, so each arm's shipped control is re-staged
beside its returned prototype on the same seed.

**NO SEED IS PINNED IN THIS ROUND, and that is not an omission.** A re-set
board is a new board and its encounter is a fresh roll; round 1's four seeds
belong to round 1's four boards. Slice 1's round 4 also found that a seed is
only reproducible within one game build (`R95`, extended to the encounter
itself), so a carried seed would not even have carried. Every file here reads
`staged: pending` with no `seed:` key, and the operator discovers the seed on
the **shipped** half of each pair and stages the prototype half with
`--seed <that run_seed>`.

### Arm 1 — one more energy, so the reader and the spender share a turn

Round 1's arm-1 board held the card under test (1), Coral Guard (1), Water's
Edge (1) and **Gyorin Formation** (2 — Block that READS the bank at one per two
Charge and never spends it) against **two** energy. That is the flaw the
reviewer's sentence names: at two energy, taking the reader-Block was the whole
turn, so the card under test and the other Charge use could never be played
together, and what the spend cost was always a next-turn question.

**The energy goes from two to three. That is the whole repair** — the same
hand, the same shipped cards, one more energy — and it turns the spend into a
this-turn price:

| line, at a bank of 8 | shipped half (`t01`) | prototype half (`t02`) |
|---|---|---|
| reader-Block first, then the card | 10 Block, 9 damage | 10 Block, 12 damage |
| the card first, then reader-Block | 10 Block, 9 damage | **7 Block**, 12 damage |
| the bank at end of turn | **8** | **2** |

Gyorin Formation reads `6 + charge // 2`. On the shipped half the two orders
are identical, because neither card touches the bank. On the prototype half
they are **three Block apart**, because the spend has already emptied what the
reader-Block reads. That is an observable sacrifice inside the turn, which is
what was asked for — and it is the same structure the reviewer credited on the
arm that ADVANCED (*"sequencing between a Charge reader and spender"*, at *"a
concrete three-damage sequencing penalty"*), asked here of a flat spender.

**Two other numbers move with it, and both are consequences.** The enemy goes
to **24 HP**, which sits above the 18 the prototype half can now produce, so no
line is lethal on either half. And the player goes to **30/70** against a
telegraph of 12: without Block the turn ends at 18, at 7 Block it ends at 25,
at 10 Block it ends at 28. At 48/70 three Block was a rounding error; here it is
three hit points a grader can see.

**Only shipped cards stand beside the arm.** Gyorin Formation, Coral Guard and
Water's Edge are all shipped Kokomi rows; a second prototype on the board would
confound the attribution the pair exists to make.

### Arm 4 — a payoff the turn can reach, and a cost that is printed

Round 1's arm-4 board held the order (2) plus **three** 1-cost cards against
three energy. Those three were a complete turn — 15 damage and 5 Block for
exactly the energy available — so the order was never worth its two, and on
both halves *the card under test was never played at all*. An arm whose card
nobody plays has not been asked anything.

**Three things changed, one per clause of the prescription.**

1. **The three-cheap-cards line is gone.** One of the three 1-costs is replaced
   by a **0-cost Companion** — Shinobu — Grass Ring of Sanctification, 4 Block,
   a shipped Inazuma Companion row. The alternatives now cost two energy rather
   than three, so the order has a window to be chosen in at all. This is slice
   1 round 4's repair for the identical failure, applied to a different hand.
2. **The payoff is near-term and the cost is printed.** A Muster transforms
   cards ALREADY IN HAND and never takes one that is already a Companion, so
   this hand holds **exactly two** cards it can take — All Streams Flow to the
   Sea and Coral Guard. Muster 2 takes both, and what the order costs is
   therefore a known number rather than a roll: **9 damage** (the reader at a
   bank of 8) and **5 Block**. A Mustered Companion costs one less, so the
   recruits are affordable on the turn that makes them; the payoff no longer
   sits a turn away. Three energy stays the budget, and it is also the guard
   that keeps the pool's 3-cost recruit unaffordable after a 2-cost order.
3. **A Companion is in hand, printed and immediate.** The 0-cost Companion is
   not a Muster victim, costs nothing to play, and shows on the face of the
   board what a recruit looks like. The order is weighed against known value on
   both sides of the trade.

**And the window is credible, which is the clause the telegraph answers.** The
incoming hit is **8**. Coral Guard (5, one energy) and the Companion already in
hand (4, no energy) cover **nine** between them, so the whole attack can be
answered for ONE of the three energy and the other two are free for the order.
A set-up turn is affordable here, which is what makes declining it a choice.
The player sits at 40/70 so that no line on the board is close to fatal either.

**What the two halves now differ by, at a bank of 8.** The shipped order takes
both takeable cards and PAYS a Charge on top: bank 8 → **9**, and the reader it
consumed is gone. The prototype order takes the same two victims and COSTS six:
bank 8 → **2** — the outlet and the fuel leave together. Either half can
instead cash the reader FIRST for 9 and then give the order, which leaves
Muster one victim, one recruit and one whiff; that trade is the same on both
halves, and the bank at the end of it is not.

**The one thing this board still cannot write** is which recruits the game
rolls. Muster's pick is the game's. What the board CAN write, and now does, is
the cost side and the timing — which is exactly what the prescription asked
for.

**The `set_hp` note from round 1 is honoured rather than repeated.** Round 1's
arm 4 asked for a 46 HP body and settled at 37 because `set_hp` clamps at a
creature's maximum and no single Act-1 body reaching 46 telegraphed anything
worth defending against. Both boards here are designed **below** the maxima the
run actually rolled — 24 and 26 against Nibbit's 42 and Sludge Spinner's 38 —
so the staging can reach them without a hunt.

## The lethal check, at TRUE card values

Card values: Water's Edge 6, Coral Guard 5 Block, All Streams Flow to the Sea
`5 + charge // 2` = **9** at a bank of 8, Gyorin Formation `6 + charge // 2`
Block now plus 6 at the start of the next turn, Sounding Line 12 for a spend of
6, the Companion in hand 4 Block. Kokomi has no Strength on these boards and
neither enemy carries an aura, so every number is the printed number.

| turn | energy | Charge | enemy HP | largest damage the board can produce | headroom |
|---|---|---|---|---|---|
| `t01` | 3 | 8 | 24 | All Streams Flow (**9**) + Water's Edge (**6**) = **15**, one energy idle | 9 |
| `t02` | 3 | 8 | 24 | Sounding Line (**12**) + Water's Edge (**6**) = **18**, one energy idle | 6 |
| `t03` | 3 | 8 | 26 | the reader first (**9**), then the order, then a 0-cost recruit — the pool's largest 0-cost hit is **7** → **16** | 10 |
| `t04` | 3 | 8 | 26 | the same line, and the spend does not add damage → **16** | 10 |

Two things the table does not hide. On arm 1 the ORDER of the two plays changes
the prototype half's Block and not the shipped half's — that is the spend, and
it is the arm. On arm 4 the recruits' identity is the game's roll, so the last
column is the **pool's ceiling** rather than a number this file can write: the
largest single recruit hit in the pool is 14 at a cost of 1 after Muster's
discount, and the largest 3-cost recruit lands at 2 after it — neither is
affordable behind a 2-cost order with three energy, and the 0-cost ceiling of 7
is. Even taking the 1-cost 14 in place of the 7, the board's total is 23 against
26 and no line is lethal.

## The map from filename to turn id

The turn id is printed into the design-blind packet, so it is deliberately
opaque: `spend` or `formation` inside an id would tell the grader which arm it
was holding. The **filename** names the arm, because only the tooling and the
packet-writer read filenames.

| file | turn id | arm | card under test | seed |
|---|---|---|---|---|
| `spend-shipped.yaml` | `kokomi-slice2-r2-t01` | 1 — spend, baseline | `all_streams_flow` (shipped) | `staged: pending` |
| `spend-prototype.yaml` | `kokomi-slice2-r2-t02` | 1 — spend | `proto_charge_spend_strike` | `staged: pending` |
| `formation-shipped.yaml` | `kokomi-slice2-r2-t03` | 4 — formation, baseline | `mass_mobilization` (shipped) | `staged: pending` |
| `formation-prototype.yaml` | `kokomi-slice2-r2-t04` | 4 — formation | `proto_charge_muster_price` | `staged: pending` |

## Closeness

`DOMINANCE_GAP` is 0.5, and this is the DECLARED reading — nothing has been
staged, so there is no observed one to take yet. **All four SURVIVE.** What
that means exactly: no single line on the board is worth more than twice the
runner-up in the pilot's own scoring currency, so the falsifier does not refuse
the turn. It is not a claim that the turn is good, interesting, or better than
its twin, and it is not comparable between two rows of the table — R213 F
allows the reading only as a refusal.

| turn | gap | top1 / top2 | lines |
|---|---|---|---|
| `t01` | 0.0000 | 20.700 / 20.700 | 11 |
| `t02` | 0.0000 | 23.700 / 23.700 | 11 |
| `t03` | 0.1957 | 18.400 / 14.800 | 13 |
| `t04` | 0.1957 | 18.400 / 14.800 | 13 |

Two disclosures the numbers make necessary, both carried forward from round 1
unchanged:

1. **The pilot does not price Charge as a cost.** It has a Spark
   hold-versus-spend term and no Charge equivalent, so on these boards a spend
   looks free and a spender scores high. The error runs ONE WAY — an
   over-valued spender is a spender more likely to dominate its board, and
   dominance is what the falsifier refuses — so a SURVIVE here is the
   conservative direction. Building the term is a `POLICY_VERSION` change with
   a re-baseline attached and is not this round's to make.
2. **Arm 4's two halves still read identically to the pilot**, at 0.1957 on
   both. The pilot values a Muster order by what it puts in hand, not by what
   the recruits do when played, so it cannot see the near-term payoff this
   board was re-set to create. What HAS changed is that the order now appears
   in the pilot's ranked lines at all rather than being absent from them. The
   blind graders and the pair read remain the only reading this arm has.

## What is waiting

Nothing here is staged. In order, and all of it needs the live game and the
art-bearing main checkout, which this worktree may not touch:

1. **A dev build** carrying the prototype rows (`klee-mod/build/deploy_proto.ps1`).
2. **Staging both pairs**, shipped half first to discover the seed, then the
   prototype half with `--seed <that value>`. **If a seed's fight telegraphs
   anything but a single-body attack, re-roll** — here the intent is the
   question, so a wrong telegraph is a wrong board. Pin the seed into each file
   and into this manifest, and re-declare the live body if it differs from the
   design, so the declared and observed closeness readings read one board.
3. **`closeness --observed`** on all four once staged, beside the declared
   reading above.
4. **Blind grading** — a fresh grader per packet on the four-question form,
   design-blind, and the R217 C independent seat (a different model family) on
   all four.
5. **Replay** of every graded line (`staged_turn execute`, EB-170).
6. **The pair read** — shipped half against prototype half, arm by arm.

And the same seat guardrail: seat testimony is iteration feedback, never
validation, never balance evidence, never approval (R217 G).
