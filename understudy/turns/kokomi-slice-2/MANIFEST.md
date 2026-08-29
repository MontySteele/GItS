# Kokomi slice 2 — the map from turn id to arm

**R217 F, executing R213 E1.** Eight turns in four matched pairs. The ids are
opaque on purpose: they are printed into the design-blind packet a grader
reads, so nothing in one may say which arm it belongs to. This file is the map,
and it is not shown to a grader.

**Nothing here is staged.** Every seed is unpinned and every row reads
`staged: pending`. The prototype halves need a dev build carrying the
quarantined rows (`klee-mod\build\deploy_proto.ps1`); the shipped halves could
be staged on a release build, but the live game belongs to another session and
this branch was built in a worktree.

**The seed rule.** Within a pair, the first half staged rolls a seed and
`stage` records it; every other half of that pair must then be staged with
`--seed <that value>`. Two halves on two seeds are two different fights, and
the pair has measured the encounter instead of the card. If the seed's fight
telegraphs anything but an attack, re-roll — the intent is the question here.

## The map

| turn | file | arm | card under test | staged |
|---|---|---|---|---|
| `kokomi-slice2-t01` | `spend-shipped.yaml` | 1 — spend | `all_streams_flow` (shipped) | pending |
| `kokomi-slice2-t02` | `spend-prototype.yaml` | 1 — spend | `proto_charge_spend_strike` | pending |
| `kokomi-slice2-t03` | `threshold-shipped.yaml` | 2 — threshold | `read_the_current` (shipped) | pending |
| `kokomi-slice2-t04` | `threshold-prototype.yaml` | 2 — threshold | `proto_charge_threshold_strike` | pending |
| `kokomi-slice2-t05` | `mode-shipped.yaml` | 3 — mode | `coral_guard` (shipped) | pending |
| `kokomi-slice2-t06` | `mode-prototype.yaml` | 3 — mode | `proto_charge_mode_guard` | pending |
| `kokomi-slice2-t07` | `formation-shipped.yaml` | 4 — formation | `mass_mobilization` (shipped) | pending |
| `kokomi-slice2-t08` | `formation-prototype.yaml` | 4 — formation | `proto_charge_muster_price` | pending |

## The boards, and the arithmetic that says no line is lethal

Every board: player 48/70, no Block, turn 3, one enemy telegraphing an attack,
`exact_hand: true`. The enemy's HP is written ABOVE the largest total damage
the board can produce at true values, so "just kill it" never ends the turn.

Kokomi has no Strength on these boards and the enemy carries no aura, so every
number below is the printed number. All Streams Flow to the Sea reads
`5 + charge // 2`.

| pair | energy | Charge | enemy HP | largest damage the board can produce | headroom |
|---|---|---|---|---|---|
| 1 (`t01`) | 2 | 8 | 34 | All Streams Flow (5+4=**9**) + Water's Edge (**6**) = **15** | 19 |
| 1 (`t02`) | 2 | 8 | 34 | Sounding Line (**12**) + Water's Edge (**6**) = **18** | 16 |
| 2 (`t03`) | 2 | 12 | 40 | Read the Current (7+6=**13**) + All Streams Flow (5+6=**11**) = **24** | 16 |
| 2 (`t04`) | 2 | 12 | 40 | All Streams Flow first at 12 Charge (**11**) then Fathom the Tide (7+6=**13**) = **24**; the other order pays 13 then 8 = 21 | 16 |
| 3 (`t05`) | 2 | 8 | 34 | Water's Edge (**6**) + All Streams Flow (**9**) = **15** | 19 |
| 3 (`t06`) | 2 | 8 | 34 | Water's Edge (**6**) + All Streams Flow (**9**) = **15** — Twin Tides deals none | 19 |
| 4 (`t07`) | 3 | 8 | 46 | three 1-cost plays: Water's Edge (**6**) + All Streams Flow at 8 Charge (**9**) = **15**; or the order plus one recruit, and the largest single Inazuma Companion hit is **14** | 31 |
| 4 (`t08`) | 3 | 8 | 46 | same three 1-cost plays = **15**; or the order (bank 8 → 2) plus one recruit at **14** | 31 |

Two things the table does not hide. In pair 2 the ORDER of the two plays
changes the prototype half's total and not the shipped half's — that is the
spend, and it is the arm. In pair 4 the recruit's identity is the game's roll,
so the "largest single hit" column is the pool's ceiling rather than a number
this file can write.

**Why the Charge bank is 8 on three pairs and 12 on one.** Eight is above the
six every prototype price charges, so a spend leaves a bank behind and the
shipped readers stay live on both halves — the spend and the read are both real
answers to the same energy. Pair 2 is the exception and it is forced: its
shipped twin's threshold sits at ten, so at eight that card's bonus half is
DEAD and the pair would be comparing a live card against a dead one. At twelve
both halves clear their bar for the same 13, and the only difference left
between them is whether the bank survives.

**Why Coral Guard.** It is the one standalone Block on these boards, in hand
wherever it is not the card under test, because a Charge payoff nothing
competes with is not a decision. A second flat-Block card would make "defend"
the answer by arithmetic rather than by choice.

## Closeness (declared boards, `staged_turn closeness`, 2026-08-29)

Run on all eight. **All eight SURVIVE** against `DOMINANCE_GAP` 0.5. Per-turn
JSON in `review/qa/<turn id>/closeness.json`.

| turn | gap | top1 / top2 | lines |
|---|---|---|---|
| `t01` | 0.0000 | 14.800 / 14.800 | 7 |
| `t02` | 0.0000 | 17.800 / 17.800 | 7 |
| `t03` | 0.2101 | 23.800 / 18.800 | 10 |
| `t04` | 0.2101 | 23.800 / 18.800 | 10 |
| `t05` | 0.0000 | 14.800 / 14.800 | 7 |
| `t06` | 0.1293 | 23.200 / 20.200 | 7 |
| `t07` | 0.2850 | 20.700 / 14.800 | 11 |
| `t08` | 0.2850 | 20.700 / 14.800 | 11 |

**Read this as a refusal that did not fire, and nothing else** (R213 F). Two
disclosures the numbers make necessary:

1. **The pilot does not price Charge as a cost.** It has a Spark
   hold-versus-spend term and no Charge equivalent, so on these boards a spend
   looks free and a spender is scored high. The error runs ONE WAY — an
   over-valued spender is a spender more likely to dominate its board, and
   dominance is what the falsifier refuses — so a SURVIVE here is
   conservative and a refusal would have been suspect. Building the term is a
   `POLICY_VERSION` change with a re-baseline attached and is not this
   slice's to make.
2. **Pair 4's two halves read identically, and neither top line contains the
   card under test.** The pilot values a Muster order by what it puts in hand,
   not by what the recruits do later, so at three energy it prefers three
   1-cost plays on both halves. The pair is therefore not separated by this
   instrument at all; the blind seat is the only reading it has.
