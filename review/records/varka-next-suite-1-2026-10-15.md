# Varka Balance suite 1 (varka-next), 2026-10-15

Build: `varka-next` 57bee10c3 (0.2.5636+next), today's main merged in (#1344).
Change set under test: `review/active/varka-next-2026-10-13.md`, three
changes, each with its prediction quoted below.
Seeds, seats and grading: A0, one Sonnet 5.5 seat per lane for the whole run,
normal fights against the base five's counted runs on the same seeds
(`review/records/base-five-baseline-2026-10-05.md`). "Suite N-1" is the last
Varka round on these seeds, `review/records/varka-round-3-2026-10-10.md`.

| Seed (base character) | End floor (cause) | Round 3 (10-10) | Base | Act 1 dmg / HP | Act 2 dmg / HP | Act 3 dmg / HP |
|---|---|---|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 40 (Slimed Berserker) | 40 | 48 | 17.7 / 10.0 | 34.0 / 13.8 | 34.2 / 15.0 |
| CYHZM9S0VPW6 (Silent) | **won** (Queen, 48/85) | won | 48 | 17.3 / 4.4 | 25.4 / 8.8 | 48.0 / 3.5 |
| DJCAV76ZKAUN (Defect) | 48 (Test Subject, phase 3) | 48 | 48 | 19.0 / 8.8 | 27.8 / 4.2 | 46.8 / 13.8 |
| YEWA0B7AVE45 (Necrobinder) | 48 (Test Subject #C55) | 40 | 46 | 19.5 / 5.0 | 43.5 / 1.2 | 43.0 / 3.5 |
| R41TX5Q0ZQYN (Regent) | **won** (Aeonglass) | won | 48 | 18.4 / 0.0 | 36.8 / 8.8 | 37.3 / 10.0 |
| **All** (fights per act) | 46.4, 2 wins | 45.2, 2 wins | 47.6, 0 wins | dmg 0.95, HP 1.07 (31) | dmg 0.98, HP 0.51 (26) | dmg 0.89, HP 0.82 (28) |

Ratios are the kit's median damage a turn and HP lost per fight over the base
five's, normal fights, by act (`tools/telemetry_report.py --character Varka
--since 2026-10-15T22:15 --until 2026-10-16T06:00 --baseline-since
2026-10-05 --baseline-until 2026-10-06` with the five
`--baseline-run-instance` tokens; 116 fights). Round 3's: damage 1.04 / 1.02 /
0.96, HP 0.50 / 0.70 / 0.99; the payoff round before it: damage 1.05 / 0.91 /
0.69, HP 0.36 / 0.60 / 0.72. Per-seed cells are median damage a turn / HP lost
per fight as % of max HP, after the end-of-combat effects.

All five runs reached act 3, as the base five's did, and every damage ratio is
within 15% of base. Act 1 HP is the one number outside the earlier rounds'
spread (1.07 against 0.36 and 0.50), though small in absolute terms (5.0% of
max HP a fight against base 4.7%). This build also carries five days of main,
so the change set is not isolated.

## The predictions, graded

1. **Eula: Icetide Vortex as an Attack.** "Eula's pick rate and its damage per
   play rise slightly, and no suite metric moves by more than the
   suite-to-suite spread." **SPLIT.** Taken 5 of 10 offers (before tonight, 5
   of 49). Damage per play fell: unupgraded 10.6 / 10.0 / 9.7 by act against
   13.5 / 19.0 / 16.8 on 2026-10-10. Act 1 HP is the one metric outside the
   spread.
2. **Twin Gales pays twice on a match.** "Its take rate rises, and runs that
   hold it deal more Swirl payout damage per fight." **UNGRADED:** offered
   once, not taken; one fight held it. Five seeds cannot test a Rare Power.
3. **Tempest Charge, Costs 1 less for each Swirl this turn.** "Played after at
   least one Swirl in most of its plays ... its pick rate in the suite is no
   lower than the old copy's. Varka's end floors and act-by-act HP stay within
   the suite-to-suite spread." **SPLIT.** End floors hold (46.4 against 45.2,
   2 wins each). Taken 1 of 5 offers against 24 of 69 before (too few to
   call). Its 18 plays deal 11.5 to 20 a play; telemetry does not log the cost
   paid, so "after a Swirl" rests on lane 5's record (a free Tempest Charge+
   after Rising Gale).

What the seats said (scratch `seats/archive/varkanext-suite-l1..l5`): Swirl
chains against groups and Oath-ordered element plays were the best turns.
Legibility: the "Oath 5 -> 0" line reads as a loss when you switch element
(Oath is kept per element); Four Winds' Ascension shows "Deals 0 damage" at
fight start and its preview counts only the second hit; Dandelion Breeze's
Block needs an aura at end of turn and does not say so; Kaeya's Hidden
Strength+ preview loses its [Cryo] tag. Weakest: Charged Lunge, Razor:
Awakening (forces Electro), Unwavering Banner.

## Picks

1. **Promote `varka-next` to main (#1258).**
   - **(a) Default:** promote. The suite holds him at the round-3 level (2
     wins, all five to act 3, damage within 15%); Eula's take rate rose, and
     nothing graded broke. Twin Gales stays ungraded until a later suite sees
     it.
   - (b) Hold, and run a second suite to settle act 1 HP and Eula's damage per
     play first.

Raw transcripts: `review/qa/blindplay/` (local, gitignored).
