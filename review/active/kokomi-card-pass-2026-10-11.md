# Kokomi's dead cards: a buff pass, 2026-10-11

[USER] (2026-10-11): "On Kokomi - it sounds like we have a lot of dead card picks. Let's do what we did for Klee and survey for weak or unpicked cards to buff. Otherwise good to take the defaults and hold for now."

## The evidence

The census is `kokomi-card-census.md` in the session scratchpad, which is gitignored:
- 20 whole-run Sonnet seat runs (rounds 1 to 4), 332 fights and 323 card-reward screens;
- seat records for all 20 runs;
- one user run, which is too short to use.

**Her pool as a whole is drafted at base rates or better.**

| | Common | Uncommon | Rare |
|---|---|---|---|
| Kokomi, rounds 1–4 | 28% | 23% | 27% |
| Base five, whole-run | 21% | 24% | 17% |
| Base five, per-act | 26% | 21% | 24% |

**So this pass is about the dead cards, not her overall level.** Two groups:
- 24 cards were offered 4 or more times and never taken: 4 Common, 13 Uncommon and 7 Rare.
- Seven more cards are taken rarely, or are taken but almost never played.

**Working: no change.** These are taken 40% or more, or played in most fights held:
- Jellyfish Drift, Nip, Deep Current, Shell Guard, Shell of Sanctuary and Bubble Ward;
- Surging Shoal, Flood Tide, Riptide, Opening Gambit, Ambush, Flank, Tide Wall and Flotsam Surge;
- Nereid's Ascension, Grand Design, Masterstroke, Kurage Swarm and Riptide Ruin.

The same yardsticks as the Klee passes apply: 10 damage per Energy to one enemy, 7 to ALL, 6 to 9 Block, and Plans at 1.3 times on-turn (your ruling). Changes are about one upgrade's worth unless a card's shape is the problem.

## The one structural finding: her debuff cards count kinds, and she has two

These five cards were offered 39 times in rounds 3 and 4 and taken 0 times:
- Drowning Pressure, "5 damage for each debuff on the enemy";
- Ceremonial Garment, "+2 for each debuff";
- Sea's Reproach, Suffocating Deep and At Water's Edge.

A "debuff" is counted by kind, not by stacks (`kokomi_plan.debuff_count`). Kokomi applies only Weak and Vulnerable, so the most any of them ever reads is 2:
- Drowning Pressure tops out at 10 for 1 Energy, a Strike;
- Suffocating Deep doubles stacks that the payoffs never read.

The group has payoffs but no engine, and its multiplier is capped.

**The fix (pick 1):** the payoffs count stacks of Weak and Vulnerable ("for each Weak and Vulnerable on the enemy"), at a lower rate per stack. At Water's Edge becomes the engine:

| Card | Today | Proposed |
|---|---|---|
| Drowning Pressure (U, 1) | 5 [7] for each debuff on the enemy | 3 [4] for each Weak and Vulnerable on the enemy |
| Ceremonial Garment (R, 1, Power) | Attacks +2 [3] for each debuff on the target | Attacks +1 [2] for each Weak and Vulnerable on the target |
| At Water's Edge (R, 2 [1], Power) | Whenever an Elemental Reaction happens on an enemy, 1 Weak and 1 Vulnerable on it | "The first time each turn you deal Hydro damage to an enemy, apply 1 Weak and 1 Vulnerable to it." In solo she has no reactions, so the old trigger never fires |
| Suffocating Deep (R, 2, Exhaust) | 6 [9] to ALL; 1 Weak and 1 Vulnerable on each, then double them | 10 [13] to ALL, same rider. It becomes the group's burst: 2 Weak and 2 Vulnerable on everything, read 4 times |
| Sea's Reproach (R, 2 [1], Power) | Whenever you apply Weak or Vulnerable, deal 3 | Costs 1 [0] |

**How big it gets:** at 2 Weak and 2 Vulnerable, Drowning Pressure deals 12, and Vulnerable takes that to 18 for 1 Energy. That is a payoff for building the engine, not a Common rate.

## The status answers: they work only after the hand is already clogged

In rounds 3 and 4, act-2 Toxic and Dazed hurt her (round 3 record), yet her status cards were taken 0 of 45 times:

| Card | Today | Taken | Proposed |
|---|---|---|---|
| Tidecleanse (C, 0) | Apply 1 Weak. Plan: Exhaust up to 2 statuses or curses in your hand | 1 of 30 | Adds "Draw 1 card." It is never a dead draw |
| Kelp Wall (C, 1) | Draw 1. Plan: 7 [10] Block, +3 per status or curse in hand | 0 of 16 | Plan 9 [12]. The 1.3 ratio was missed here |
| Sea Glass Harvest (U, 1) | 8 [11] Block. Plan: transform statuses and curses in hand into Sea Glass | 0 of 13 | 10 [13] Block |
| Abyssal Salvage (U, 1, Power) | Whenever a status or curse is Exhausted, the Casket gains 1 | 0 of 13 | "Whenever you draw a status, Exhaust it. The Casket gains 1." It becomes the answer itself, not a payoff for other answers (Klee's Damage Report is the same shape) |

## Priced short, by number

| Card | Today | Taken | Proposed |
|---|---|---|---|
| Massed Volley (C, 1) | 3 [4] Hydro, 3 times | 0 of 6; 2 NEVER AGAIN | 4 [5], 3 times. 12 is a Common Attack, and multi-hit is how Casket Strength pays |
| Coral Crash (C, 1 [0]) | Hydro damage equal to your Block | 0 of 11 | Costs 0, and the upgrade adds 4 damage. Plan Block lands at the start of your turn, so this is her cash-out for it |
| Change of Plans (C, 0, Exhaust) | Carry out your first Plan now. Draw 1 | 0 of 21 | Draw 2. Exhaust stays (your ruling: it would otherwise cash every Plan the turn it is written) |
| Pincer (U, 1) | 4 [5] twice. Plan: next turn, your first Attack is played twice | 0 of 8 | 5 [6] twice |
| Tideturn (U, 1) | 4 [5] for each Plan waiting | 0 of 14 | 6 [8] each. Two Plans waiting is the usual board, so 12 |
| Weight of the Plan (U, 1) | 5 [7], +3 for each Energy paid for Plans waiting | 0 of 9 | 8 [10], +4 each. Most Plans cost 0, so the base number is what lands |
| Salt in the Wound (U, 0) | Apply 1 [2] Vulnerable. If the enemy has Weak, draw 1 | 0 of 10 | "Draw 1 card, or 2 if the enemy has Weak" |
| Undercurrent Snare (U, 1) | Apply 2 Weak. Plan: 1 [2] Vulnerable to ALL | 0 of 8 | Costs 0 |
| Tidal Resonance (U, 1) | Hydro on ALL; draw 1 for each enemy that already had an element | 0 of 9 | Costs 0 |
| Turning Tide (U, 0) | Draw 1 [2]. Plan: discard any number, draw that many | 0 of 19 | Draw 2 [3] |
| Coral Tithe (U, 0) | Empty the Casket: 1 Energy and draw 1 for every 3 [2] | 0 of 6 | For every 2; the upgrade adds Retain in place of lowering the ratio |
| Undertide Lance (U, 2) | 6 [9] to ALL. Plan: 14 [18] to the front enemy, doubled if alone | 1 of 8 | Now line 9 [12]. 6 for 2 Energy was 0.43 of the ALL yardstick |
| Watatsumi's Grace (R, 2, Power) | At end of turn, keep up to 10 [15] of your Block | 0 of 5 | Costs 1 |
| Kurage School (R, 1 [0], Exhaust) | Copy each 0-cost Plan card in your hand | 0 of 4 | Costs 0; upgrade adds Retain |
| Treatise (U, 1, Power) | First Plan card each turn: draw 1 [Innate] | 0 of 9, but played in 68% of fights held | Costs 0 [Innate]. A cheap engine piece is what a Plan deck drafts early |

**Left alone:**
- **Second Wave** (1 of 10) and **Read the Field** (taken, played in 28%). Each has one strong line the numbers can't show, and seats named Read the Field once. Watch them in your run.
- **Tidal Rebuke** is the Rare Coral Crash (ALL enemies, Retain).
- **Gorou's Crystal Collapse** waits with the Companion-count cards (Companion paper, pick 2).
- **Co-op-only cards** are judged by a paired round: Joint Orders, Coordinated Strike, Tactical Relay, Sangonomiya's Counsel and Kurage's Mercy.

## For [USER]

1. **Debuff payoffs count stacks of Weak and Vulnerable, not kinds.** At Water's Edge becomes the engine and Suffocating Deep the burst, with the five rows above.
   - **(a) Default:** yes.
   - (b) Keep counting kinds and only raise the numbers. The payoffs then stay capped at 2.
2. **Abyssal Salvage becomes a status answer:** "Whenever you draw a status, Exhaust it. The Casket gains 1."
   - **(a) Default:** yes.
   - (b) Keep the payoff shape, and raise it to 2 Casket per Exhaust.
3. **The status-answer and priced-short tables as listed:** 18 cards, by number or cost.
   - **(a) Default:** yes.
   - (b) The Commons only, then re-measure.

After the build, two Kokomi seats play a round before your full run, as for Klee.
