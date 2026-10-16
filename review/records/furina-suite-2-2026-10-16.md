# Furina Balance suite 2, 2026-10-16

Build: `furina-next` 56e08e6ee (0.2.5662+next), the three Powers of the
furina-next paper (`review/active/furina-next-2026-10-15.md`, ruled "ship it"):
Crescendo, Standing Room Only, Prima Donna. Before the suite, the C# runaway
test (Standing Room Only with Full House, Showstopper and three damaging
guests, #1350) gave 7 Strength in one turn from a 200 Fanfare bank.
Seeds, seats and grading as suite 1 (`review/records/furina-suite-1-2026-10-15.md`):
A0, one Sonnet 5.5 seat per lane for the whole run, normal fights against the
base five's counted runs on the same seeds.

| Seed (base character) | Suite 2 end floor (cause) | Suite 1 | Base |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 24 (4 Exoskeletons, act 2) | 39 | 48 |
| CYHZM9S0VPW6 (Silent) | 48 (Queen, act 3 boss, round 7) | 44 | 48 |
| DJCAV76ZKAUN (Defect) | 24 (Spiny Toad, act 2) | 17 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 33 (Knowledge Demon, act 2 boss) | 48 | 46 |
| R41TX5Q0ZQYN (Regent) | 33 (Kaiser Crab, act 2 boss) | 33 | 48 |
| **Mean** | 32.4 | 36.2 | 47.6 |

No run won. Lane 4's seat declared a wasted turn in the fight that ended it.

Normal fights against base (`tools/telemetry_report.py --character Furina
--since 2026-10-16T01:00 --until 2026-10-16T12:00 --feed bot` with suite 1's
baseline flags):

| Act | n | dmg/t (base) | ratio | net HP % (base hp %) | ratio | Suite 1 ratios |
|---|---|---|---|---|---|---|
| 1 | 32 | 21.3 (19.6) | 1.09 | 10.3 (4.7) | 2.19 | 1.05 / 1.65 |
| 2 | 24 | 29.2 (33.0) | 0.89 | 19.6 (12.8) | 1.53 | 0.98 / 1.05 |
| 3 | 7 | 32.0 (47.0) | 0.68 | 17.9 (12.1) | 1.48 | 0.75 / 1.53 |

Act 3 is one run (lane 2), seven fights.

## The predictions, graded

1. **Taken in a quarter of offers: HIT.** 5 of 11 (45%) against 4 of 46.
   Crescendo 4 of 7 (in four of five decks, played 11 times), Standing Room
   Only 1 of 2 (played twice), Prima Donna 0 of 2 (`--offers --since
   2026-10-16T01:00`).
2. **Act 3 damage at least 0.85 of base: MISS** (0.68, one run). Acts 1 and 2
   stay within 15% (1.09, 0.89).
3. **Elite and boss damage on turns 5+ up a quarter: MISS.** Turn 5: 25.4
   (8 turns) against the paper's 26; turns 7+: 41.9 (15) against 39. Both
   samples are small.
4. **Net HP not up in any act: MISS.** Act 1 2.19 (was 1.65), act 2 1.53 (was
   1.05); act 3 1.48 (was 1.53).
5. **Three of five reach act 3: MISS.** One did.
6. **Draw and act 3 production: HIT.** 6.17 cards a turn (was 5.74); Fanfare
   produced a turn 6.3 / 8.8 / 10.6 by act, act 3 above act 2 (scratch
   `furina-gap/s2.py`; production = Fanfare spent + Fanfare left at the end).

By the paper's own rule, "If 1 holds and 2 or 3 does not, the engines are
taken but too small." That reading needs a correction from the seat records:
the bank is now growing, and it goes unspent.

## What the seats said

Records: scratch `seats/archive/furina-suite2-l1..l5`.

- **The bank sits unspent.** Lane 2 had "Fanfare 87-117 and no Rising
  Applause+ in hand" in its last fight, and Rising Applause was "often in the
  discard pile with 40-117 Fanfare unspent". Lane 5 died at 4 HP holding 49
  Fanfare "and no Stage+/Star Turn drawn". Crescendo was played "on a free
  turn" as an automatic card. Production went up; her ways to spend it did
  not.
- **Block and HP.** Lane 2's deck was "Block-poor all run", down to 3 HP
  several times. Lane 1 "knowingly underblocked for Fanfare; this is where the
  run was lost". Drain cards lock at low HP ("would take you to 0 HP"), the
  same complaint as suite 1.
- **Standing Room Only** (lane 3): "a setup tax I played in the wrong
  fights"; "I never wanted Standing Room Only after it turned up". Prima
  Donna was never taken.
- **Best cards:** Singer of Many Waters (heals 12 to 21, decided two fights),
  All the World's a Stage+, Star Turn played for 0 off the bank.
- **Weakest:** Endless Waltz again ("just a worse Strike"), Critics' Darling
  ("never mattered", two lanes), Regina of All Waters, The Masquerade.

## Reading

Suite 2 is worse than suite 1 on the same seeds (mean end floor 32.4 against
36.2; act 3 reached 1 of 5 against 3 of 5), but two seeds improved and
suite-to-suite noise is large (suite 1 noted act 3 damage of 28.6, 41.7 and
35.0 over three rounds). What the suite does show: Crescendo is taken and does
its job, the act 3 bank and production now grow, and the payoff is not
there. The gap has moved from making Fanfare to converting it, plus the HP
she pays to make it. Standing Room Only and Prima Donna did not get a fair
test (two plays, none).

## Picks

1. **What to do with furina-next.**
   - **(a) Default:** do not promote. Keep Crescendo on `furina-next`; a
     second paper on spending the bank (how often a payoff is in hand when
     the bank is large, and the Drain lock at low HP), which also rewrites or
     replaces Standing Room Only and Prima Donna; then suite 3 on these
     seeds.
   - (b) Promote Crescendo alone to main (taken in four of five decks, act 3
     production up), drop the other two, and write the spending paper from
     there.
   - (c) Promote all three as they are.

Raw transcripts: `review/qa/blindplay/` (local, gitignored).
