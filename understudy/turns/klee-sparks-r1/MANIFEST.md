# `KLEESPARK-R1` — turn manifest

Eight staged turns, the first LIVE round of the Klee Sparks arm. The
registration is `docs/current/EXPERIMENTS.md` → **`KLEESPARK-R1`**, committed
before this file existed; the packet is
`review/active/klee-sparks-2026-08-29.md`, and its §10.9 prediction slate is
countersigned by [USER] as `M51` (2026-08-29).

**This file and the eight boards were committed BEFORE anything was staged,
deployed, or read**, for the same reason a prediction slate is: a board
written after a reading is not a board, it is a result.

## The arm on the board

`C.SPARK_ALT_COST_ENABLED` in tier 0 and `-p:PrototypeCards=true` in C#. Eight
rows on `docs/prototype-surface.yaml` with `character: klee`:

| id | printed name | price | what it is |
|---|---|---|---|
| `proto_pop_spark` | Powder Pop | — (gains 1) | starter Basic, the generator |
| `proto_kaboom_sink` | Ka-pow! | 1 | starter Basic, the sink |
| `proto_spark_strike` | Fwoosh! | 1 | Common, 8 to one |
| `proto_spark_sweep` | Tinder Toss | 1 | Common, 4 to all |
| `proto_spark_double_tap` | Bang Bang! | 2 | Common, 5 ×2 random |
| `proto_spark_blast` | Dodoco Blast | 2 | Uncommon, 7 to all |
| `proto_spark_finisher` | Firework Finale | 3 | Uncommon, 18, Exhaust |
| `proto_true_spark_knight` | Spark Knight's Oath | (3/Attack) | Rare Power, strict |

## The boards

Every board is `exact_hand: true` and `prototype: true`. The bank is written
with the `set_power` op on `SPARK_POWER`, the precedent for which is
`understudy/scenarios/set-power-sparks.yaml`. Player energy is Klee's base 3
on every turn, so nothing in the round moves two variables at once.

| turn | bank | hand | what the board is |
|---|---|---|---|
| `t01` | **0** | Ka-pow!, Powder Pop, Kaboom!, Duck and Cover, Jumpy Dumpty | turn one, the substituted starter dealt |
| `t02` | 1 | Ka-pow!, Fwoosh!, 2× Kaboom!, Duck and Cover | two sinks priced 1 against a bank of 1 |
| `t03` | 2 | Fwoosh!, Bang Bang!, 2× Kaboom!, Duck and Cover | a price-1 beside a price-2 |
| `t04` | 3 | **Spark Knight's Oath**, Kaboom!, Jumpy Dumpty, Duck and Cover | the Rare Power, bank CAN pay |
| `t05` | 1 | **Spark Knight's Oath**, Ka-pow!, 2× Kaboom!, Duck and Cover | the Rare Power, bank SHORT |
| `t06` | 2 | Dodoco Blast, Tinder Toss, Kaboom!, Duck and Cover | the two AoE sinks |
| `t07` | 4 | Firework Finale, Fwoosh!, Powder Pop, Duck and Cover | a deep bank that buys both |
| `t08` | **0** | Powder Pop, Ka-pow!, Tinder Toss, Kaboom!, Duck and Cover | empty bank with the generator in hand |

**Two constraints the round put on itself, and they are limits rather than
targets.** The empty bank appears on exactly TWO boards (`t01`, `t08`) — the
cap the round set, not a claim about how often Klee's bank is empty. The Rare
Power appears on exactly TWO boards (`t04`, `t05`), one paying and one short,
because a deck holds one Rare and staging it more often would say otherwise.

**Where the boards fall on the slate, counted before any form was read and
recorded so it cannot be re-counted afterwards.** Four of the eight (`t02`,
`t03`, `t06`, `t07`) open with two or more Spark uses in hand that the bank
can each individually afford. That is exactly P1's threshold, which is
uncomfortable and is stated rather than smoothed: the count fell out of
covering the shapes the round was asked to cover (a starter opening, the two
prices, the two Power halves, the AoE pair, a deep bank, a second dry bank),
and no board was added or removed after the count was taken. **P1 is graded on
what a GRADER SEES on the page, not on this count**; the count is here so that
the board-set's contribution to the answer is visible.

## What the boards could not do

**The tier0 mirror runs FLAG-OFF, and on three boards it disagrees with the
live build.** `staged_turn.build_combat_state` runs in this tree, where
`C.SPARK_ALT_COST_ENABLED` is `False`, so the mirror still applies the SHIPPED
base rule — an Attack goes free at a bank of 3 and eats 3 Sparks — which the
live `+proto` build has retired. That reaches `t04` (bank 3) and `t07` (bank
4); `t01`, `t02`, `t03`, `t05`, `t06` and `t08` all sit under a bank of 3 and
the two engines agree there. **The error runs one way**: the mirror is RICHER
than the live board, and richer lines can only make the dominance falsifier
stricter, never laxer. The packet and the replay read the LIVE game and are
unaffected. Fixing it means a per-turn flag on the mirror, which is owed and
unbuilt.

**The enemies are the seed's and not this file's.** Each file writes HP and
Block and cannot write the intent or the enemy count; the mirrored board
declares a telegraphed attack as the falsifier's input, and the packet records
whatever the game drew. Where the live encounter differs from the declared
mirror, they are two records and not one.

## The closeness readings, on the declared boards

Taken before staging. `DOMINANCE_GAP` is 0.5 throughout.

| turn | gap | top line | runner-up | lines |
|---|---|---|---|---|
| `t01` | 0.0382 | 44.520 | 42.820 | 20 |
| `t02` | 0.0377 | 29.200 | 28.100 | 23 |
| `t03` | 0.0489 | 30.700 | 29.200 | 23 |
| `t04` | 0.1154 | 37.700 | 33.350 | 14 |
| `t05` | 0.2100 | 28.100 | 22.200 | 23 |
| `t06` | 0.1313 | 19.800 | 17.200 | 11 |
| `t07` | 0.1568 | 37.620 | 31.720 | 15 |
| `t08` | 0.1249 | 26.420 | 23.120 | 15 |

**All eight SURVIVE**: no line dominates by more than the derived gap.

## The reading schedule, printed before any reading

The tester seat is the LOCAL Qwen seat (`understudy.local_tester`), its first
live use, available for the staged single-turn tester seat only. The Codex
seat spot-checks at `--seat-spot-check 4`, **the shipped default** — `M58` is
open on what that rate should be and this round does not answer it, it
discloses that it used the default. Any turn `understudy/resource_order.py`
flags routes to the seat as well, regardless of the rate.

```
round of 8 turn(s), seat spot-check every 4
   1  SEAT  klee-sparks-r1-t01
   2        klee-sparks-r1-t02
   3        klee-sparks-r1-t03
   4        klee-sparks-r1-t04
   5  SEAT  klee-sparks-r1-t05
   6        klee-sparks-r1-t06
   7        klee-sparks-r1-t07
   8        klee-sparks-r1-t08
```

A fresh-Opus form is taken on every packet as well. Every one of these rows is
`authored_by: [claude]`, so that read is **SAME-FAMILY** (packet §7) and is
recorded as such — never as the deciding read.

## The seeds

Not pinned in the files at commit time, deliberately. A `seed:` placeholder is
an operator trap (round 3 of Klee slice 1 lost a staging attempt to one), so
the key is ABSENT until the game has rolled a fight and the seed it actually
used is written back. The seeds and the encounters they produced are recorded
in the packet's round-1 section, beside whatever refusals the staging took.
