# `KLEESPARK-R2` — turn manifest and prediction slate

Six staged boards, **R222 D's minimal repaired staged round** for the Klee
Sparks arm. The registration is `docs/current/EXPERIMENTS.md` →
**`KLEESPARK-R2`**; the arm's packet is
`review/active/klee-sparks-2026-08-29.md`, whose §11.7 items 1, 2 and 7 are
what this round exists to discharge, and whose §13 will carry the results.

**This file, the six boards, `slots.yaml` and the slate below were committed
BEFORE anything was staged, deployed or read**, for the same reason a
prediction slate is (R212): a board written after a reading is not a board, it
is a result.

## What is different from `KLEESPARK-R1`, stated up front

1. **The seeds are PINNED IN ADVANCE**, not written back after the first
   staging. `KLEESPARK-R1` could not put an AoE card in front of more than one
   body (§11.6 item 4) because the encounter is the seed's and the seed gave one
   body. Two of these six boards need three bodies, so their seeds are drawn
   from encounters ALREADY RECORDED ON DISK by earlier rounds. Every board's
   seed is in its turn file and in the table below.
2. **Every counting slot is machine-readable** (`slots.yaml`, `EB-202`), and
   `round --plan-only` computed each one's ceiling over these six boards before
   the round was accepted. `KLEESPARK-R1`'s `P1` carried a threshold of 4
   against a ceiling of 3 and nobody could see it until the pair read.
3. **The local seat sits in the SHADOW chair** (`--seat-mode shadow`, R222 B).
   Its forms are recorded and graded and are NEVER replayed; the deciding
   tester is the fresh-Opus reader, and the replay is what its form says.
4. **The round may stop early** (R221 B, `--first`), and the plan below is what
   it stops against.

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

**The Rare Power is NOT staged on any board of this round**, per §11.7 item 3:
it was left as built and sent to whole-fight play, and staging it again here
would ask a question that has already been answered `(a)`.

## The boards

Every board is `exact_hand: true` and `prototype: true`. The bank is written
with `set_power` on `SPARK_POWER`; an empty bank is the power's ABSENCE rather
than a zero, which is `klee-sparks-r1/t01`'s precedent. Player energy is Klee's
base 3 on every board, so nothing here moves two variables at once.

| turn | seed | bank | enemies | hand | what the board is | slots |
|---|---|---|---|---|---|---|
| `t01` | `JH4T8MSN10KS` | 3 | 1 | Fwoosh!, Bang Bang!, Firework Finale, Kaboom!, Duck and Cover | **A** — three prices (1/2/3) the bank cannot all pay | `S1` |
| `t02` | `R805DJ56LZHM` | **0** | 1 | Fwoosh!, 2× Kaboom!, Duck and Cover, Jumpy Dumpty | **B** — the dry sink, NO generator in hand | `S2` |
| `t03` | `YX7PB48WR7R4` | 2 | 1 | Bang Bang!, 2× Kaboom!, Duck and Cover | **C** — a 2-price on a bank of exactly 2, no Bomb out | `S4` |
| `t04` | `NMQLUYZDLV` | 2 | **3** | Dodoco Blast, Fwoosh!, Kaboom!, Duck and Cover | **D** — AoE and single-target, both affordable | `S1`, `S3` |
| `t05` | `XT4BE7LFY5XH` | **0** | 1 | Firework Finale, Ka-pow!, 2× Kaboom!, Duck and Cover | **E** — the dry sink at two prices | `S2` |
| `t06` | `R7W86HG7WHUD` | 2 | **3** | Dodoco Blast, Bang Bang!, Kaboom!, Duck and Cover | **F** — three bodies, both sinks priced 2 | `S1`, `S3`, `S4` |

**Where the seeds came from, and the one thing they are not.** `NMQLUYZDLV`
drew Twig Slime (S) + Leaf Slime (M) + Leaf Slime (S) on six recorded stagings
(`kokomi-slice1-t03..t05`, `-r2-t03..t05`, `-r3-t03..t05`); `R7W86HG7WHUD` drew
the same three on `kokomi-slice1-r4-t03` and `-t04`. The other four are
`KLEESPARK-R1` seeds recorded one-body on a Klee run. **Those three-body
records are from KOKOMI runs, and whether the Act-1 encounter roll is
character-independent is not established by this file.** If a staging draws
fewer than three bodies, the packet records what it drew, `S3` goes UNREACHED
on that board, and the round says so rather than smoothing it.

**The three-body boards level the enemy HP** with `set_hp {who: lowest_hp}`
three times, which raises the three lowest in turn to 30. The slimes roll small
and different, and an AoE that kills two outright would turn the board's
question into arithmetic.

## The counting slots (`slots.yaml`), and their ceilings

Computed by `local_tester round --plan-only` over these six boards, before
anything was staged:

```
SLOT OK   S1: threshold 2, ceiling 3 of 6 board(s)  [t06, t04, t01]
SLOT OK   S2: threshold 2, ceiling 2 of 6 board(s)  [t02, t05]
SLOT OK   S3: threshold 2, ceiling 2 of 6 board(s)  [t06, t04]
SLOT OK   S4: threshold 2, ceiling 2 of 6 board(s)  [t06, t03]
```

## The DRAFTED prediction slate

**DRAFTED by Claude from written intent (R212)** — the intent is packet §11.6
("what this round could not do") and §11.7 items 1, 2 and 7, all countersigned
by [USER] under R222. Committed before any board was staged; [USER]
countersigns in batch or vetoes within five days. Every falsifier below is
mechanical: it is read off a form, a replay record, or
`review/qa/klee-sparks-r2-round-summary.json`, and no model is in the loop.

**`P1` — the price creates a visible spend-versus-hold choice.**
On **at least 2** of the `S1` boards that are RUN, the DECIDING form's answer to
question 2 names a Spark-priced card DIFFERENT from the Spark-priced card its
chosen line plays.
*Falsifier:* fewer than 2 such boards.
*Decision (R206):* PREDICTED → §11.7 item 1's answer `(d)` is confirmed on the
instrument that can now ask the question, and the tight set of five stands as
built. MISSED → the set does not produce a choice even where the arithmetic
says it should, and §11.6's option (e) — re-author one or two sinks away from
damage — goes to [USER] as a live pick.
*This is `KLEESPARK-R1`'s `P1` re-posed against a reachable threshold; the
published MISS is untouched and is not re-graded (R101b).*

**`P2` — a dry sink reads as a dead card, not a playable one.**
On **both** `S2` boards, the DECIDING form's chosen line plays NO Spark-priced
card, and no falsifier fires claiming a Spark-priced card is free or affordable
(`misreads.free_card_misreads`).
*Falsifier:* on either board, a chosen line containing a `spend_spark` card, or
a misread naming one.
*Decision:* PREDICTED → §11.7 item 2's sanity check is discharged; how OFTEN a
dry sink happens, and whether it frustrates, stays with whole-fight play, and
`PICK 1` closes on the staged half. MISSED → the price is not legible at an
empty bank, which is a FACE defect, and `PICK 8` (display) reopens as a live
pick with the failure attached.

**`P3` — at three bodies the AoE sink is chosen over the single-target one.**
On **both** `S3` boards, the DECIDING form's chosen line plays the
`all_enemies` sink (Dodoco Blast) and not the other affordable Spark sink.
*Falsifier:* on either board, a chosen line that plays the non-AoE Spark sink
and not the AoE one. A board that draws fewer than three live enemies is
UNREACHED, not MISSED, and is recorded as such.
*Decision:* PREDICTED → the AoE rows are priced correctly against single-target
at three bodies and `PICK 3`'s candidate set needs no repricing from this
round. MISSED → 2 Sparks is the wrong price for a board sweep even at three
bodies, and the two AoE rows' price goes to [USER] as a repricing pick.

**`P4` — Bang Bang! spends exactly 2 on a bank of exactly 2.**
On **both** `S4` boards, WHERE THE REPLAYED LINE PLAYS BANG BANG!: the game
accepts the play at a bank of 2 and the post-play Spark bank reads exactly 0.
*Falsifier:* a refusal of the play at bank 2, or a post-play bank other than 0,
on either board. Where no run board's replayed line plays Bang Bang! at all,
`P4` is **UNGRADED** and is recorded UNGRADED — it is not scored PREDICTED by
the absence of a counterexample.
*Decision:* PREDICTED → `W1`'s price-arithmetic candidate is settled with no
code change and leaves the list. MISSED → an engine defect in
`effects.spend_sparks` / `card_playable` at a price of 2, filed to `BACKLOG`
and blocking any further Sparks registration until it is fixed.

**`P5` — the shadow seat does not yet reach `M62`'s bar.**
The per-turn verdict agreement in
`review/qa/klee-sparks-r2-round-summary.json` — the shadow local seat's verdict
against the deciding fresh-Opus verdict — is **below 4 of 5** on the first set,
which is `M62`'s ≥ 6/8 criterion at this round's size.
*Falsifier:* agreement of 4 or 5 out of 5 comparable boards.
*Decision:* PREDICTED → the seat stays in the shadow chair and
`local_tester qualify`'s battery remains its route back, unchanged. MISSED →
the first half of `M62`'s two-part criterion is met on one round, and the seat's
return goes to [USER] as a PICK together with the battery scorecard, because
`M62` requires BOTH halves and a round alone does not return the seat.

## The reading schedule, printed before any reading

`local_tester round … --seat-mode shadow --seat-spot-check 4 --first` (default,
raised to 5 by the twice-over cover):

```
round of 6 board(s) in R221 B's pre-registered order; seat spot-check every 4; first set = 5
   1  FIRST  SEAT  klee-sparks-r2-t06   slots=S1,S3,S4  closeness=0.168
   2  FIRST        klee-sparks-r2-t04   slots=S1,S3  closeness=0.168
   3  FIRST        klee-sparks-r2-t02   slots=S2  closeness=0.000
   4  FIRST        klee-sparks-r2-t03   slots=S4  closeness=0.192
   5  FIRST  SEAT  klee-sparks-r2-t05   slots=S2  closeness=0.280
   6    ...        klee-sparks-r2-t01   slots=S1  closeness=0.022
```

**`t01` runs only if `S1` is UNDECIDED after the first set**, and is otherwise
recorded UNRUN with its seed still pinned. **Two Codex seat reads** (positions 1
and 5) plus the pair read is the whole Codex budget for this round: three calls.

## The closeness readings, on the declared boards

Taken before staging. `DOMINANCE_GAP` is 0.5 throughout.

| turn | gap | top line | runner-up | lines |
|---|---|---|---|---|
| `t01` | 0.0224 | 31.200 | 30.500 | 19 |
| `t02` | 0.0000 | 31.600 | 31.600 | 11 |
| `t03` | 0.1922 | 30.700 | 24.800 | 15 |
| `t04` | 0.1676 | 35.200 | 29.300 | 11 |
| `t05` | 0.2796 | 21.100 | 15.200 | 7 |
| `t06` | 0.1676 | 35.200 | 29.300 | 11 |

**All six SURVIVE**: no line dominates by more than the derived gap.

## What the boards still cannot do

**The tier0 mirror runs FLAG-OFF**, exactly as in round 1: it applies the
shipped base rule (an Attack goes free at a bank of 3 and eats the bank) that
the live `+proto` build has retired. That reaches **`t01` alone** here, the only
board at a bank of 3. The error runs one way — the mirror is RICHER than the
live board, and richer lines only make the dominance falsifier stricter. The
packet and the replay read the LIVE game. Five of six boards sit below a bank
of 3 and the two engines agree there.

**It still cannot draft.** `loader._pool_substitutions` returns `{}` for Klee,
so nothing here was picked by a drafter; the hands are granted by id.

**It still cannot ask a face-and-turn question.** A staged single turn shows one
hand with no memory of what the bank was held for; §11.6 item 1 is unchanged by
anything in this round, and whole-fight play remains the instrument for it.
