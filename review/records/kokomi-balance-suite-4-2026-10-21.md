# Kokomi Balance suite 4, 2026-10-21

Build: main c9f6ca17a (0.2.6129): the taste audit's ten cards
(`review/active/kokomi-taste-audit-2026-10-21.md`), her new visuals (Plan
carry-out effects, the swarm, Nereid's Ascension clip, the rendered
Bake-Kurage), on top of suites 1 to 3's changes. Five Sonnet 5.5 seats,
whole runs, A0, the five suite seeds, all drafting freely. Lane 1's first
seat tripped the bridge's three-refusal stop at the act 1 boss (it tried to
Plan three cards with no Plan line); the count was cleared and a second seat
played the same run on from that fight.

| Seed (base character) | End floor (cause) | Suite 3 | Base |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 48 (Test Subject, act 3 boss) | 33 | 48 |
| CYHZM9S0VPW6 (Silent) | **won** | 33 | 48 |
| DJCAV76ZKAUN (Defect) | 39 (Constructs, act 3) | 30 | 48 |
| YEWA0B7AVE45 (Necrobinder) | **won** | 44 | 46 |
| R41TX5Q0ZQYN (Regent) | 48 (Aeonglass, act 3 boss) | won | 48 |
| **All** | 46.2, 2 wins | 37.6, 1 win | 47.6, 0 wins |

Every run passed the act 2 boss (suite 3: two of five).

## Against the base five

`tools/telemetry_report.py --character Kokomi --character base5 --since
2026-10-21T18:55`, the five baseline run instances, baseline window
2026-10-05.

| Act | dmg/turn (base) | ratio | HP lost % (base) | ratio | bar |
|---|---|---|---|---|---|
| 1 | 18.5 (19.6) | 0.94 | 7.5 (4.7) | 1.61 | outside (HP) |
| 2 | 29.8 (33.0) | 0.90 | 10.0 (12.8) | 0.78 | outside (HP, under base) |
| 3 | 47.6 (47.0) | 1.01 | 12.5 (12.1) | 1.03 | within |

Damage is within the bar in every act. Act 1 HP lost is 7.5% of max a
normal fight against base 4.7%: about 2 HP a fight on 80. Act 2 loses less
HP than base.

Bosses (median damage a turn): act 1 33.0, act 2 51.0 (suite 3: 40.9; base
58.4), act 3 46.6.

## The changed cards

Played: Shoal Call 52 times (the most-played new card), Undertow, Flotsam
Surge, Suffocating Deep, Sea's Reproach+, Resolve of Watatsumi, Watatsumi's
Grace. Not met: Riptide Ruin, Coral Crash. Powers and Plans that add damage
to another card are credited to that card (Sting, the Plan), so Resolve,
Reproach and Grace show 0 in the per-card table.

## What the seats said

- Best turns: Opening Gambit+ then Princess of Watatsumi+ (54, 81 after
  Vulnerable); Masterstroke first under Nereid's Ascension (126); Shoal Call
  then Shoal of Spears (40 to 72) with Breakwater counting the planned
  Stings (17 to 28 Block); Grand Design wiping all three Decimillipede
  segments in one morning. Lane 4: most fights fell to Powers, Shoal Call,
  then one AoE.
- Losses: act 3 attrition with no rest (lane 3), Test Subject's third form
  (lane 1), Aeonglass's Wither fed by many cheap plays (lane 5).
- Weak: Following Current (two more "never enough Plans"; lane 2 won with
  two copies), Treatise, Kurage Canopy, Kelp Wall's Plan (0 or 4), Sea Glass
  Harvest.

## Defects and legibility (to check or fix)

- Crystal Collapse was refused with "no Companion has been played", though
  its text plays a random Common one when none was (lanes 1, 1b, 5).
- Shoal Call: two seats tried to play it on the Bake-Kurage ("Plan 3
  Stings"); the bridge's hint offered it.
- Opening Gambit's doubling did not apply to a Plan flipped to its now-line
  (lane 3: 15, expected 30), with no warning.
- Press the Advantage's number and Vulnerable: a third seat unsure.
- Grand Design's planned cards gave no Casket Block (lane 5, again).
- Nothing on a card says it cannot be Planned; Kurage's Oath's Plan line
  was read as Block (lane 4).

## Next

[USER]'s pick: promote on this suite, or one more act-1 pass first.
