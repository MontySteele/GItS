# Kokomi level pass: the big numbers down, the odd cards up, 2026-10-12

**Your run on the jellyfish build:**
- "a lot of my draft picks boiled down to 'take the big number and ignore the weird cards.'"
- "I won by assembling too much block to die + some strength scaling and beating everything to death with strength-boosted AoE + block-to-damage cards. Nice vibe, but drafting felt kinda autopilot."
- "Change of Plans is way too good at Common."
- "a pass over the card deck for overly situational effects and overly powerful-per-energy cards + the text cleanup. Then another review once things are levelled out."

**Evidence.** `scratchpad/kokomi-pass/packet.md` (gitignored). It covers:
- your run: seed 9XE8RGZPQ7SR, 27 fights, its telemetry, and the run file with every offer;
- 526 seat fights since the re-founding;
- a per-Energy table for all 89 cards.

## What your run shows

- **Two cards dealt a fifth of your damage, both by turning Block into damage.**
  - Tidal Rebuke+ (12.8%): 0 cost upgraded, Retain, ALL enemies, 23.5 a play.
  - Coral Crash (7.6%): 0 cost, 20.5 a play.
  - Base Body Slam does the same single-target job for 1 Energy (0 upgraded). Coral Crash is Body Slam with the cost already paid, at Common.
- **Your Strength came from Companions, not from Kokomi.** Arlecchino's Masque took you from 3 to 20 Strength in the last boss fight. Her own Strength card, Resolve of Watatsumi, reached 3 or more in only 10% of seat fights. That part is the Companion flavor working, so it stays.
- **Her mechanic was optional.** You planned 0.32 cards a turn, and 10 of 27 fights planned none. The plan-reading cards you passed explain it:
  - Tide Wall (4 times), Press the Advantage (3), Feint, Flank, Kelp Wall, Tideturn and Shoal of Spears.
  - Seats skipped the same cards: Flank 0 of 22, Tideturn 1 of 23, Shoal of Spears 0 of 13, Drowning Pressure 0 of 17, Gorou's War Banner 1 of 57, Crystal Collapse 0 of 15.
- **Change of Plans:** you held 4 copies and played it 16 times. In 3 fights it carried out nothing and only drew.

## 1. Down: the big numbers

| Card | Today | After | Why |
|---|---|---|---|
| Coral Crash (C) | 0: damage equal to your Block [plus 4] | **1 [0]**: damage equal to your Block | Body Slam's price. It's 1.7 to 2.2 times the Common rate at the median 13 Block a turn. |
| Tidal Rebuke (R) | 1 [0], Retain: damage equal to your Block to ALL enemies | **2 [1]**, Retain | Noelle's Uncommon version costs 2 [1]. With a 0-cost upgrade it was your top damage source. |
| Flotsam Surge (U) | 1: 13 [17] to ALL; 2 Dazed | **10 [13]** to ALL; 2 Dazed | 13 to ALL for 1 Energy is nearly twice the ALL-enemies rate (7 per Energy). It is the pass's "big number". |
| Steady Tide (U) | 13 [16] Block, Ethereal; Or plan: draw 3 | **11 [14]** Block | 1.4 to 1.7 times the Block rate. Ethereal earns some of that, not all. |
| Change of Plans (C → **U**) | 0, Exhaust: carry out your first Plan now; draw 2 [3] | Unchanged text, **Uncommon** | Your call. Draw 1 at Common would still be a 0-cost cycler, which you don't want at Common. |
| Riptide Ruin (R) | 9 to ALL twice, 3 Dazed | 11 [14] to ALL twice, no Dazed | Already agreed. It's in this build. |

Tamakushi's Wrath (30, or plan 18 to ALL, taken 85%) stays. It is a 2-cost Ethereal Rare, and its big number is the Rare's job.

## 2. Up: the odd cards get a floor

These cards do nothing unless a condition holds, and the condition rarely does. The fix is a floor, not a new rule.

**Cards that count Plans waiting.** "Waiting" means planned earlier this same turn, which happens 0.3 to 0.45 times a turn.
- **Tideturn** (U, 1): "Deal 8 [10] Hydro damage, plus 8 [10] for each Plan waiting." Today it deals 0 with none waiting.
- **Shoal of Spears** (R, 1): "Deal 5 [6] Hydro damage to ALL enemies, plus once more for each Plan waiting." It always hits at least once.

**Debuff payoffs.** Nothing in her pool reliably puts debuffs on, so the payoff brings its own:
- **Drowning Pressure** (U, 1): "Apply 1 Weak and 1 Vulnerable. Deal 3 [4] Hydro damage for each Weak and Vulnerable on the enemy." Its floor is 6.
- **Sea's Reproach** (R Power): 3 → **5 [7]** per Weak or Vulnerable applied. At 3 it was below an Uncommon.

**Situational Plans, made plain:**
- **Flank** (U, 1): "Deal 8 [11] Hydro damage. Or plan: Deal 11 [14] Hydro damage to each enemy that intends to attack." It reads intents when carried out, as Tide Wall does. That drops "when you wrote this", which seats misread.
- **Kelp Wall** (C, 1): "Gain 5 [7] Block. Draw 1 card. Or plan: Gain 12 [15] Block." The status count goes. Four seats called it her weakest card, and statuses are rare in her decks. Tidecleanse and Sea Glass Harvest stay as tech against status enemies.

**Gorou's dead pair:**
- **General's War Banner** (C, 1): "Gain 7 [10] Block. Or plan: Gain 1 [2] Strength." Today it's 2 Dexterity for 2 turns, or 3 Strength this turn, taken 1 of 57. The new version gives her own slow Strength line.
- **Crystal Collapse** (U, 1, plan only): "Plan: Play a copy of the last Companion card you played." It drops "other" and "this turn", so it works when the copy is carried out next turn.

**Companion picker:**
- **Orders from the Shrine** (C): "Choose 1 of 3 random Common Inazuma Companions to add into your Hand. It is Ethereal." Today it's a random pick, taken 2 of 42. Choosing is the point.
- **Its cost moves 0 → 1 [0].** A 0-cost card that hands you a card is a cycler, which you don't want at Common.

**Left for the next review:**
- the Exhaust-Pile pair (Moon's Reflection, Reserves);
- the Block support Powers (Brace for the Tide, Watatsumi's Grace, Tidal Riposte), which Block decks did not need;
- the Sting payoffs (Endless Shoal, All Streams);
- Watchful Shoal.

None of these is broken. They're narrow, and a narrow card can wait for the next round's numbers. Ceremonial Garment and At Water's Edge get more to work with from the debuff changes above.

## 3. Text

The card-text pass (#1172) brings the house rules and her one planning verb. Every card changed here is written to them. Its one open pick (plan or write) applies to these cards too.

## After the build

A two-seat Kokomi round on the new build. Then the review you asked for, "once things are levelled out", read against the same numbers:
- Plans per turn;
- the share of damage from Block-to-damage;
- take rates for the cards in section 2.

## Ruled 2026-10-12

[USER]: "On the Kokomi level paper - agreed on all defaults"

- **Pick 1 (a):** all of section 1's trims.
- **Pick 2 (a):** all of section 2's floors.

The cards are written to the card-text pass's house rules, with "plan" as the verb.

## For [USER] (ruled above)

1. **The trims in section 1.**
   - **(a) Default:** all of them.
   - (b) Coral Crash and Tidal Rebuke only.
2. **The floors in section 2.**
   - **(a) Default:** all of them.
   - (b) The Plan-counting and debuff cards only. Flank, Kelp Wall, Gorou's pair and Orders wait for the review.
