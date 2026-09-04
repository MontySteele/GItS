Status: RECORD

# X9READ-S1, re-read after EB-242: W9 fires again, by 1.76 points

Run 2026-09-04 on [USER]'s word ("M69: sounds good!"), taking M69's default:
re-read after `EB-242`, then rule. The registration is unchanged
(`review/records/charge-reads-per-turn-registration-2026-08-13.md`, §5.3
thresholds and §5.4's `W9`), the cell is the same (`tier05/exp_x9read_s1.py`,
`CELL`, 600 runs per archetype, seed 11, three arms, 1,800 runs), and the
first record stands as published (R101b); this file is the second reading
beside it, not a rewrite of it. The command was
`python -m tier05.exp_x9read_s1 --runs 600 --seed 11 --json <scratch>`; the
JSON is a scratch artifact and its numbers are here.

## 1. The slate, graded against §5.3

| | Result | Threshold | Grade |
|---|---|---|---|
| X1 | mean 0.521 reads per turn over 106,414 sampled player turns | 1.0 to 2.0 PREDICTED | **MISS** (under 1.0) |
| X2 | p90 2.00 reads per turn | <= 3 | PREDICTED |
| X3 | max 7 reads in one turn | <= 8 | PREDICTED |
| X4 | garment 45.76% of 55,430 completed-turn reads | < 50% | PREDICTED |
| X5 | bonus_formula 6.00% of completed-turn reads | < 15% | PREDICTED |
| X6 | 276 of 175,643 attack plays carry both reads (0.16%) | < 5% | PREDICTED |
| X7 | turns 1 to 5 mean 0.439, turns 6+ mean 0.839, gap +0.399 | rises, gap < 1.0 | PREDICTED |

6 PREDICTED / 0 SPLIT / 1 MISS / 0 UNREACHED. The first record graded the
same slate with the pilot reads `EB-242` removed still counted; X1's MISS is
in the same direction as before (fewer reads than intended, not more).

## 2. W9

| Limb | Reading | Fires at | Result |
|---|---|---|---|
| A, repeatable readers (garment + bonus_formula) | 51.76% of completed-turn reads | > 50% | **FIRES**, margin +1.76 pp |
| B, double reads | 0.16% of attack plays | > 50% | no, margin -49.84 pp |

Severity indicator, gating nothing: p50 0.00 reads per turn, QUIET. The
Kurage pulse is 48.24% of completed-turn reads; 79,675 sampled turns carry
no pulse. The first record read Limb A at 58.91% with the pilot reads and
estimated 51.68% without them; the re-read's 51.76% is that estimate.

## 3. What it means, in two sentences

The pilot reads were the difference between 58.91% and 51.76%, and what is
left is the shipped Charge machinery reading itself at half of one read per
turn, with a median turn that reads nothing. `W9` is a candidate and not a
verdict (§5.4); it fires by 1.76 points on a meter whose shipped kit the
Plan overhaul retires (`review/active/kokomi-brief-2026-09-01.md` §2: no
bank, no pulse), so the read budget it asks about is a budget for machinery
the arm no longer runs.

## 4. The pick, for [USER] (M69 closes on it)

1. **R188 STANDS, no read budget (default).** Severity is QUIET, the margin
   is under two points, and the machinery measured is the shipped Kokomi's,
   which the overhaul replaces; a budget written now binds nothing the arm
   plays. M69 retires with the ruling.
2. **A dedupe/cap options packet** on the shipped Charge reads, two pages,
   before the overhaul's arm is judged. Spends design time on a kit that is
   being replaced.
3. **Re-read once more when the Plan arm reaches Balance**, against the
   arm's own reads, and rule then. Keeps M69 open with a stated trigger.

## 5. Ruled

R255, 2026-09-04: pick 1. R188 stands, no read budget; M69 closed. [USER]'s
words are in the ruling commit.
