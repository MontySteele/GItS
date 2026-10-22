# Kokomi Balance suite 5, 2026-10-22

Build: main 4891f5dd7 (0.2.6139), the defence pass
(`review/active/kokomi-next-2026-10-19.md`, "Defence pass, 2026-10-22"):
Tamakushi Casket 1 Block a Plan [Watatsumi 2], Watatsumi's Grace and Kurage
Canopy ignore Stings and Wards, Canopy uses Battle Formation's condition,
Tide Wall's Plan 4 [6]. Five Sonnet 5.5 seats, whole runs, A0, the five
suite seeds, all drafting freely. No refusal stops.

| Seed (base character) | End floor (cause) | Suite 4 | Base |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 48 (Test Subject, act 3 boss) | 48 | 48 |
| CYHZM9S0VPW6 (Silent) | 48 (Queen, act 3 boss) | won | 48 |
| DJCAV76ZKAUN (Defect) | 33 (Kaiser Crab, act 2 boss) | 39 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 44 (Frog Knight, act 3) | won | 46 |
| R41TX5Q0ZQYN (Regent) | 40 (Frog Knight, act 3) | 48 | 48 |
| **All** | 42.6, 0 wins | 46.2, 2 wins | 47.6, 0 wins |

Four of five passed the act 2 boss.

## Against the base five

`tools/telemetry_report.py --character Kokomi --character base5 --since
2026-10-22T02:00`, the five baseline run instances, baseline window
2026-10-05 (the same call reproduces suite 4's table exactly).

| Act | dmg/turn (base) | ratio | HP lost % (base) | ratio | Suite 4 ratios |
|---|---|---|---|---|---|
| 1 | 17.5 (19.6) | 0.89 | 6.9 (4.7) | 1.47 | 0.94 / 1.61 |
| 2 | 26.3 (33.0) | 0.80 | 12.1 (12.8) | 0.95 | 0.90 / 0.78 |
| 3 | 35.9 (47.0) | 0.76 | 16.4 (12.1) | 1.35 | 1.01 / 1.03 |

Damage is outside the bar in acts 2 and 3; act 1 and act 3 HP are outside.

Bosses (median damage a turn): act 1 21.1, act 2 48.2, act 3 19.9 (two
fights).

## What the pass changed in these runs

No seat drafted Kurage Canopy or Watatsumi's Grace; one (lane 1) took Tide
Wall+. The Casket is the only change every run met, at 1 Block a Plan
instead of 2, so most of the damage drop is likely the draft and seed
variance rather than the pass. Every deck held Breakwater; Shoal Call was in
one (suite 4's most-played new card). Seats do not plan Block the way [USER] does (suite 4 record,
and his run on 0.2.6135), so this suite cannot say whether the pass fixed
the defence he saw; it says the seats got weaker, mostly at act 3 Frog
Knight and the bosses.

## What the seats said

- Best turns: Grand Design+ planning Spearhead's Vulnerable before
  Masterstroke ("61 after Vulnerable", one-shot The Lost); three Plans
  waiting turning Tideturn into about 48; Brine Sting+ planned under
  Nereid's Ascension killing three Scrolls; Grand Design into Breakwater+
  for 19 to 26 Block.
- Losses: act 3 Frog Knight's Plating and Strength (lanes 4 and 5);
  Kaiser Crab's back attack and Frail (lane 3); Queen's Block with Torch
  Head doing the damage (lane 2); Test Subject's second form (lane 1, three
  potions unused).
- Weak: Sea's Reproach (lane 4: "no immediate effect"), Slack Water (a
  starter card), Brine Sting+'s Plan on a turn nobody attacks, Watchful
  Shoal, Frantic Escape (a status).

## Defects and legibility

- Fixed (#1528): the seat page's Casket row still said 2 Block.
- Kelp Wall+'s Plan preview said "deals 0" against an enemy not attacking,
  then dealt 4 (lane 5).
- Mend: Escoffier and The Moon print "(0 will land)" while HP is at or
  below combat-start HP; two seats could not tell why (lanes 2, 5).
- Plan pages rarely show a Plan's total once Resolve of Watatsumi+ and
  Following Current stack (lane 1).
- Grand Design+'s picker seemed to list too few cards (lane 2).
- Planned hits stood in Tunneler's Block but Rocket's Crab Rage Block was
  gone by the time the Plan landed; nothing says why (lane 5).

## Next

[USER]'s run on the defence pass decides Balance. The seats' numbers are
for his read, not a reason to undo the pass.
