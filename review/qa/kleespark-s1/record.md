# `KLEESPARK-S1` — the Klee Spark arm measured DRAFTED, in the sim

**Registration:** `review/active/klee-sparks-2026-08-29.md` §17, slate §17.4,
committed DRAFTED before the instrument and before this run (R212(2)).
**Instrument:** `tier05/exp_klee_sparks_s1.py`, committed before this run.
**Raw record:** `record.json` beside this file; the driver's own stdout is
`stdout.txt`, unedited.

**Cell:** `klee/demolition` (pilot `demolition`), route `hunter`, policy
`assigned`, relics + potions, all registered acts — **600 runs, seed 11,
`jobs=1`**. Ran to completion inside the driver's 600-second allowance, well
inside §17.3's registered 30-minute budget.

**World stamp: `RT12 / D18 / P11 / C21`**, read live off `cells.world_stamp()`.

> **STAMP DISCLOSURE, §17.3's own rule.** §17.3 declared the expected stamp as
> `RT12/D18/P11/C20`, copied from `STATE.md`'s Live cell. **`STATE.md` was
> stale at `HEAD`**: `CONSTANTS_VERSION` is **21**, bumped 2026-08-30 by
> `EB-219` (Prune's Sparks moved off her face into Klee's kit declaration, at
> parity on all four yields). **The world did not move under this read** — it
> was C21 before the registration was written, during the run and after it —
> so what differed is the registration's transcription, not the world. The read
> is published stamped **C21**, which is where it was taken, and `STATE.md`'s
> Live cell is corrected as hygiene in the same commit. Nothing is re-run and
> no threshold moves.

**Guardrail-7 and R215 B:** every number here is a FLOOR produced by a scoring
pilot. The win rates are diagnostics, they grade nothing, and they are not
comparable to any published arm.

## The two arms

| | flag OFF — CONTROL, NOT GRADED | flag ON — the ARM, GRADED |
|---|---|---|
| runs / fights / player turns | 600 / 9,237 / 37,009 | 600 / 8,428 / 34,597 |
| peak Spark bank, median | **3.0** | **5.0** |
| peak Spark bank, mean | 3.48 | 5.94 |
| fights peaking ≥ 2 | 86.3% | **90.7%** |
| turns with a NON-DAMAGE sink affordable | 0.00% | **0.62%** (216 turns) |
| turns with ANY priced sink affordable | 0.44% | **20.50%** |
| decks holding a non-damage sink | 0.0% | **3.2%** (19 of 600) |
| decks holding any prototype row | 0.0% | 99.8% |
| median maker:sink at floor 5 | 0.000 (n=577) | **1.000** (n=576) |
| median maker:sink at floor 10 | 0.000 (n=532) | **1.000** (n=538) |
| median maker:sink at floor 15 | 0.000 (n=503) | **1.500** (n=510) |
| runs holding Rummage | 0 | **0** |
| mean deck size | 25.2 | 23.8 |
| runs won (diagnostic, R215 B) | 5.5% | 1.7% |

## The slate, graded against §17.4's registered thresholds and no others

| slot | grade | read | registered threshold |
|---|---|---|---|
| `S1` per-fight peak Spark bank | **PREDICTED** | median peak **5.0**; **90.7%** of 8,428 fights peaked ≥ 2 | median ≥ 2 AND ≥ 60% of fights peak ≥ 2 |
| `S2` turns with a non-damage sink affordable | **MISS** | **0.62%** of 34,597 player turns (216 turns) | ≥ 15% PREDICTED, 5–15% SPLIT, < 5% MISS |
| `S3` decks holding ≥ 1 non-damage sink | **MISS** | **3.2%** of 600 runs (19 decks) | ≥ 50% PREDICTED, 20–50% SPLIT, < 20% MISS |
| `S4` maker:sink at floors 5 / 10 / 15 | **MISS** | medians **1.000 / 1.000 / 1.500**; the ratio ROSE and floor 15 sits ABOVE the band | median FALLS 5 → 15 AND floor-15 median in [0.30, 0.80] |
| `S5` Rummage | **PREDICTED** | **0.0%** — 0 of 600 decks | exactly 0.0% PREDICTED, anything > 0 MISS |

**2 PREDICTED / 0 SPLIT / 3 MISS / 0 UNREACHED.**

## What the live registration INHERITS, and what it does not

**INHERITS: `1.500` makers per sink**, the floor-15 median of the drafted decks
under the arm. §17.4 registered that *any* graded outcome of `S4` hands the live
controlled-ratio deck its ratio, so the live registration takes **3 makers to 2
sinks** as a derived number rather than as a pick. `W2`'s granted deck ran the
inverse of it — **2 makers to 11 sinks** — and this read says that composition
was an artefact of granting, not a property of the economy.

**DOES NOT INHERIT** — and none of this may be read off this run:

- **No re-price of §4.2's table, and no new sink row.** R225 forbids both until
  the income question is answered; `S1` answers it in the sim only, and the
  live half is unrun.
- **No win rate, no comparison, no balance claim** (R215 B). The 1.7%/5.5%
  column is a diagnostic of a scoring pilot, not of the arm.
- **No legibility, presentation or fun claim.** The sim has no display; the arm
  has a cost badge the sim cannot see. Guardrail-7 applies whole.
- **No claim that a human would spend the bank the way the pilot did.** `P11`'s
  Spark literacy is a hold-versus-spend term, not a player.

## Registered blind spots that the run made concrete

1. **`_is_maker` reads a top-level `gain_spark` and nothing else** (§17.2's own
   definition). Two real Spark sources therefore do NOT count toward the ratio:
   `crackle`'s `discard_for_sparks`, and — since **C21** — **Klee's kit
   declaration** (`effects.klee_personal_companion_spark`), which is where
   `prune_witch_hunt`'s two `gain_spark` ops went. The inherited 1.500 is
   therefore a **floor on generation**, never a ceiling, on both arms equally.
2. **`S2`'s denominator is every player turn, not every turn of a deck that
   holds the card.** `S3` = 3.2% is most of `S2`'s 0.62%: the destination was
   usually not in the deck at all, so `S2` MISSED on an OFFER fact rather than
   on a bank fact. §17.4's UNREACHED condition for `S2` was `S3` = 0 exactly,
   and `S3` was 19, so the slot grades MISS as registered and is not rewritten.
3. **The flag-OFF control's maker:sink medians read 0.000 at every floor**, and
   that is a scorer fact, not a data fault: `draft.STATIC_SPARK_VALUE` is
   **0.0**, so with the flag off a `gain_spark` is worth literally nothing to
   the drafter and the median shipped deck drafts none. It is why the control
   is RECORDED and NOT GRADED.
