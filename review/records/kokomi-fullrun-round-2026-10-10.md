# Kokomi whole-run round and card review, 2026-10-10

[USER] asked whether Kokomi had had "a reasonable balance review of her current card selection" before his next look. The last one was 10-05: two per-act seats, which we now know play worse. This round is the review.
- Five whole-run Sonnet seats on the base-five baseline's seeds, plus the Ironclad control, A0.
- Build 0.2.4779+next.
- The packet, records and scripts are in the session scratchpad (`kokomi-fullrun-r1/`), which is gitignored.
- A Fable reviewer reviewed the round. The main session accepted the review with two corrections, listed at the end.

## Result: 0 of 5, and well short of base

| Seed | Kokomi | Base character, same seed | Varka r3 |
|---|---|---|---|
| CYHZM9S0VPW6 | floor 33, The Insatiable | floor 48 (Silent) | won |
| DJCAV76ZKAUN | floor 17, Ceremonial Beast (entered 30/80) | floor 48 (Defect) | floor 48 |
| 30KMHAVG9SMQ | floor 43, Knight trio elite | floor 48 | floor 40 |
| YEWA0B7AVE45 | floor 33, Knowledge Demon | floor 46 | floor 40 |
| R41TX5Q0ZQYN | floor 17, Ceremonial Beast (entered 43/80) | floor 48 | won |
| Ironclad control | floor 48, the Queen | | |

Her mean death floor is 28.6. The base five's is 47.6 on the same seeds (0 wins, but all five reached act 3), and Varka's is 44.8.

## Why she loses

**Boss fights are the gap, not hallways.**
- Her damage a turn in normal fights is 0.86 / 0.90 / 1.00 of base by act.
- At the act-1 boss: 22.7 against 30.6. At the act-2 boss: **26.9 against 58.4**.
- Ceremonial Beast takes her 13 turns; Regent and Varka took 7 and 6.

**Plans don't grow.**
- A Plan deals its printed number once, a turn late.
- Plan damage per fight falls: 22.0 in act 1, 16.8 in act 2, 5.7 in act 3, while she plays the same number of Plan cards.
- The only thing in her kit that grows with turns is Casket Strength. It was 3 or more on 18% of turns.
- Late-game damage came from her on-turn cards, borrowed cards (Thundering Verdict did 570 in one run) and Electro-Charged Poison. The 10-08 review said the same from save files: "she loses them on length".

**Her pool is not the cause.**
- 7 of her 21 Commons deal damage, about what each base character has.
- They are taken more often than her utility Commons (38% against 24%).
- Their numbers are at base rate: Deep Current 16.6 a play, Undertow 15.0.

**Act 1 bleeds from fight length, not missing Block.**
- She takes about 3.5 turns per act-1 fight against base's 3.0. The extra half turn is one more enemy swing, which is the whole HP gap.
- Her Block per fight equals base's (9.2 against 8.4).
- Measured against the whole-run Ironclad control rather than the per-act base five, her act-1 HP loss is 1.27× rather than 2.1×. Both act-1 boss deaths entered the fight low, after an elite.

## Card by card (summary; full table in the review)

- **Keep:**
  - **Commons:** Deep Current, Driftglass, Massed Volley, Undertow, Press the Advantage, Feint, Breakwater, Nip, Bubble Ward, Current Read.
  - **Uncommons:** Ambush, Surging Shoal, Riptide, Flank, Flotsam Surge, Opening Gambit, Pearl Current, Treatise.
  - **Rares:** Sango Isshin, The Moon.
- **Retune (Claude ships):**
  - **Jellyfish Drift:** Plan 2 → 3 [4] to ALL. At 2 it is a third of Astral Pulse.
  - **Change of Plans:** cost 1 → 0. It was played in 1 of 14 fights where it was held.
  - **Nereid's Ascension:** cost 3 → 2. It was held in 5 fights and played in none. The brief says cost 2 and the sheet says 3, so this also fixes a drift.
- **Flagged, no change yet:**
  - Shell Guard (played in 29% of fights held).
  - Read the Field (10%).
  - Masterstroke (0 plays).
  - Ceremonial Garment (0 of 4 offers taken).
  - Abyssal Salvage (NEVER AGAIN).
  - Sea Glass Harvest (0 of 5 taken after its retune).
  - Tidal Screen (one NEVER AGAIN).
- **Never taken despite offers:** Tidecleanse (0 of 9), Coral Crash, Vanguard, Coral Bulwark, Brine Sting. Seats skip plain Block cards for every character.
- **Never offered:** 11 of 21 Rares. No verdict.

## Defects, checked in source

- **Real (Claude fixes):**
  - The seat page's Casket line disappears with the Watatsumi Casket (Touch of Orobas). The page matches the relic by text, and the upgraded relic's text differs (`blindplay_render.py:1245`).
  - Treatise prints no line when it draws, so a no-draw looks silent.
  - Nothing on the Plan list says that Strength is read when the Plan is written.
- **Rule or seat error (no change):**
  - Plan hits ignore her own Weak and Shrink. That is the ruled Plan hit; the target's Vulnerable still counts.
  - Frozen on a boss gives Vulnerable instead, by the boss rule.
  - The Moon's Mend never heals above the HP she entered with, and the tip says so.
  - Kyouka's turn count, Tide Wall's "asked for" line, and the stunned slug that still attacked: all rule or seat error.
- **Unverified:** Fairy in a Bottle may not have saved the control at death. No klee-mod hook touches death or HP loss. This needs a live repro, as does Wax Lizard Tail.

## What changes (Claude ships)

1. Jellyfish Drift Plan 3 [4]. Change of Plans cost 0. Nereid's Ascension cost 2.
2. Seat-page fixes:
   - the Casket line also matches the Watatsumi Casket;
   - a Treatise draw line;
   - "Strength is read when the Plan is written" on the Plan list.
3. Telemetry: the Casket count, and Plans written and carried out, per fight.
4. Backlog: a Fairy in a Bottle repro beside the Wax Lizard Tail line.

These three card changes are worth a few points a turn in act 1. They do nothing about the act-2 boss gap of 31.5 damage a turn. That gap is pick 1.

**The main session's corrections to the review:**
- The review proposed per-act seats for the next round so the format matches the base-five baseline. [USER] has ruled whole-run seats for every kit (#1045). So the next round stays whole-run and is compared with the whole-run Ironclad control. A whole-run rerun of the base-five baseline on these five seeds is added, so every kit has a matching base number.
- On pick 2 (b): [USER] vetoed free combat-start setup for Klee (the Bomb relic, 2026-10-05). That is noted beside the option.

## For [USER]

1. **The long-fight engine (the act-2 boss gap).**
   - **(a) Default:** the Casket gives 2 per Plan carried out instead of 1 (brief sec.9 marks this number as moved by play; you said "1 strength per point seems fine; we can adjust"). Read it on the next round before your run. Expected: about +10 to 15 damage a turn in the back half of a boss fight, roughly 40% of the gap.
   - (b) Play the build as it is first, with the engine paper after your run.
   - (c) A new engine, such as "Plans deal +1 for each Plan carried out this combat". This is a design direction and needs a paper.
2. **The act-1 boss** (2 of 5 deaths, both entered under 55% HP).
   - **(a) Default:** take the tempo fixes above and re-read.
   - (b) The Bake-Kurage starts each combat with Kurage's Oath's Plan written. This conflicts with your "no free setup on the starter" stance.
   - (c) Accept that act 1 is where she is fragile.
3. **The status sub-theme** (10-08 pick 4, now with offer data: Tidecleanse 0 of 9, Sea Glass Harvest 0 of 5, Abyssal Salvage NEVER AGAIN).
   - **(a) Default:** swap Abyssal Salvage and Tidecleanse for two "plan the reaction" cards after your run.
   - (b) Swap now.
   - (c) Keep all seven.
4. **Rarity of the damage Plans.** Ambush is taken 75% of the time and Surging Shoal 2 of 2.
   - **(a) Default:** leave rarities. The take rates are a symptom of pick 1.
   - (b) Ambush to Common, and Coral Crash to Uncommon.
