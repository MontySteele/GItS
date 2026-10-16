# Furina Balance suite 3, 2026-10-16

Build: `furina-next` 34acfeff3 (0.2.5708+next): paper 1's three Powers
(Crescendo, Standing Room Only, Prima Donna) plus paper 2's spending changes
(`review/active/furina-next-2-2026-10-16.md`, as amended after GPT's review:
Bravura capped at 18 with its damage kept, Bring the House Down capped at 10
a guest, Bis! replaced by Extended Run). `main` was merged into `furina-next`
first (#1368). Seeds, seats and grading as suites 1 and 2: A0, one Sonnet 5.5
seat per lane for the whole run, normal fights against the base five's
counted runs (`review/records/base-five-baseline-2026-10-05.md`).

| Seed (base character) | Suite 3 end floor (cause) | Suite 2 | Suite 1 | Base |
|---|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 39 (Globe Head, act 3) | 24 | 39 | 48 |
| CYHZM9S0VPW6 (Silent) | 48 (Queen, act 3 boss) | 48 | 44 | 48 |
| DJCAV76ZKAUN (Defect) | 31 (Entomancer, act 2 elite) | 24 | 17 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 48 (Test Subject, act 3 boss) | 33 | 48 | 46 |
| R41TX5Q0ZQYN (Regent) | 48 (Aeonglass, act 3 boss, at 204 of 512) | 33 | 33 | 48 |
| **Mean** | **42.8** | 32.4 | 36.2 | 47.6 |

No run won (the base five won none either). Four of five reached act 3 and
three died at its boss. No crash or refusal stop.

Normal fights against base (`tools/telemetry_report.py --character Furina
--since 2026-10-16T14:00 --feed bot --baseline-since 2026-10-05
--baseline-until 2026-10-06` with the five `--baseline-run-instance` tokens):

| Act | n | dmg/t (base) | ratio | net HP % (base hp %) | ratio | Suite 2 / Suite 1 ratios |
|---|---|---|---|---|---|---|
| 1 | 33 | 19.8 (19.6) | 1.01 | 9.4 (4.7) | 2.00 | 1.09 / 2.19 ; 1.05 / 1.65 |
| 2 | 29 | 27.0 (33.0) | 0.82 | 16.7 (12.8) | 1.30 | 0.89 / 1.53 ; 0.98 / 1.05 |
| 3 | 21 | 44.8 (47.0) | 0.95 | 12.8 (12.1) | 1.06 | 0.68 / 1.48 ; 0.75 / 1.53 |

Act 3 is four runs this time (suite 2: one).

## The predictions, graded

Spend numbers from scratch `furina-gap/s3b.py` (the suite 1 and 2 numbers
are recomputed by the same script).

1. **Act 3 average capped Spend at least 9: MISS** (7.4, from 5.4). The
   average still counts Quick Flourish's fixed Spend 4, which made 39 of the
   suite's Spends. The cards that Spend up to a number averaged 13.2 in act 3
   (suite 2: 10.0) and were played three times as often (18 against 6).
2. **Big-bank turns with a spender in hand that is too small, under a third:
   HIT** (act 2: 8 of 27, act 3: 4 of 29). The split GPT asked for, of
   turns starting at 20+ Fanfare:

   | Act | Big-bank turns | No spender in hand | Spender too small | Useful spender, not played | Spent |
   |---|---|---|---|---|---|
   | 1 | 20 (S2: 20) | 45% (45%) | 0% (0%) | 10% (5%) | 9 |
   | 2 | 33 (S2: 32) | 18% (28%) | 24% (3%) | 9% (12%) | 16 |
   | 3 | 35 (S2: 12) | 17% (50%) | 11% (8%) | 17% (8%) | 19 |

   The first group fell well below the paper's 37 to 41% in acts 2 and 3, so
   by the paper's own rule access is not the next change. Act 1 is still 45%,
   with smaller banks and thinner decks.
3. **Bravura, Bring the House Down and Extended Run taken in a quarter of
   offers: MISS** (2 of 9, 22%). Bravura 2 of 4, Bring the House Down 0 of
   2, Extended Run 0 of 3 (`--offers --since 2026-10-16T14:00`).
4. **Act 3 normal-fight damage at least 0.85 of base: HIT** (0.95, four
   runs).
5. **Three of five reach act 3: HIT** (four).
6. **Net HP not above suite 1 in any act: MISS.** Act 1 2.00 (suite 1
   1.65), act 2 1.30 (1.05); act 3 1.06 (1.53).

**The bank is now spent.** In act 3 fights she won, the median Fanfare left
at the end was 1 (suite 1: 12, suite 2: 14, over 23 fights against 13 and 7).
Rising Applause still made the most Spends (72), then Quick Flourish (39) and
Let the People Rejoice (20).

## What the seats said

Records: scratch `seats/archive/fn-s3-l1..l5`.

- **The loop works.** Every seat named banking Fanfare and cashing it as its
  core decision, and every best turn was a cash-out: Let the People Rejoice
  for 70 and 95, Rising Applause at 53 and 68 Fanfare on two bosses, Verdict
  of the Oratrice at 47.
- **Repay cards with nothing to repay.** Four of five NEVER AGAIN lines are
  Repay cards that read "Repays 0": Endless Waltz (two seats), Hymn of Many
  Waters, Pneuma Refrain. At full HP, or early in a turn, they are blank.
- **Block is thin.** Lane 2 "almost no reliable Block" and survived three
  times on relics; lane 5 died holding 23 Fanfare with its Fanfare-to-Block
  cards in the discard pile; lane 3 spent an empower turn on attacks and
  died to the 35 that followed.
- **Not a bug:** lane 1 saw Thunderous Applause not trigger off Verdict of
  the Oratrice. Verdict deals damage equal to her Fanfare and spends none,
  so it is not a Spend; it works as printed.
- **Page lines worth a fix (BACKLOG):** a Hard To Kill cap is not shown on
  Let the People Rejoice's preview (lane 5); "past your line" is never
  defined on the page (lane 5); a word tip for Charlotte printed with no
  Charlotte card (lane 3).

## Reading

Suite 3 is her best suite on these seeds: mean end floor 42.8 against 36.2
and 32.4, four runs in act 3, act 3 damage at 0.95 of base, and the act 3
bank is spent where it used to sit. The new cards themselves were taken
less than predicted (Extended Run 0 of 3), so most of the gain is the
capped cards she already had (Soloist's Solicitation, Hold the Stage) now
being worth playing and spending bigger, together with Crescendo's
production. What is still wrong is HP in acts 1 and 2, the cost of making
Fanfare, and the Repay cards that are blank when she is healthy.

## Picks

1. **What to do with furina-next.**
   - **(a) Default:** promote it to main: paper 1's three Powers and paper
     2's spending changes. Then a short paper 3 on the two open problems:
     act 1 and 2 HP loss, and the Repay cards that read "Repays 0".
   - (b) Promote everything except Extended Run (taken 0 of 3); its Rare
     slot goes to paper 3.
   - (c) Do not promote yet; run paper 3 on `furina-next` first.

Raw transcripts: `review/qa/blindplay/` (local, gitignored).

**Ruled 2026-10-16.** [USER]: "I think this is a clear improvement over where
we were. Let's promote as-is, and then when the current Yae dedupe pass
lands, aim to get this into a private steam page. In the meantime we can do
a paper round on the findings." Pick 1 (a).
