# Varka: defence lives in Anemo

Paper, 2026-10-01. Main session design, on [USER]'s direction. **Ruled
2026-10-01**, [USER]: "Everything else looks good!"; Tailwind Guard left as
it is (§3).

## 1. Why

[USER] asked whether non-Hydro Varka finds "block decent in act 1 and too
scarce in act 3", and whether drafting across four elements makes him hard to
build. The measurement (main session, 2026-10-01; `tools/varka_expansion_sim.py`,
500 seeds, the act-3 pool at 80 HP, Block divided by incoming damage):

- **Block is short in every hard fight.** The default drafter covers 0.66 of
  act-1 elites, 0.63 of the act-2 boss and 0.55 of act-3 elites.
- **Split drafts are worse.** In act 3, decks across 3+ elements cover 0.55
  to 0.71, against 0.65 to 0.84 for 1 to 2 elements. The default drafter
  ends with Oath cards in all four elements in 73% of runs.
- **Only Hydro holds** (1.03 to 1.47 in acts 2 and 3). The switch deck's act-3
  Block leans on one Rare: Oathbound Aegis supplies 18% of it, under a cap of
  15.
- **The cause:** almost all of his scaling Block reads the *current* element's
  Oath, so splitting Oath across elements dilutes all of it.

The seats said the same in three rounds, and named a second hole: a hand with
no current element is a dead hand (four of his cards read it).

[USER]'s direction: "the simpler fix is to just move more of the defense kit
into his universal Anemo cards so that each element can draft additional
support from its pool but we don't need to spam out 30 different defense
cards covering each element. It's fine if we leave some of that (especially in
Hydro) but let's not waste all of the deck space doing 4x the work. His Anemo
roster can be bigger than the 4 other elements if we need it to be."

## 2. The shape

Each element keeps its one defensive Knight (Hydro its three and Tidal
Bulwark). The new defence is Anemo, so every draft sees it. It splits in two
by what it reads:

- **Mono decks** keep the current-element scalers: Eye of the Storm, Oath of
  the Knights.
- **Split and switch decks** get Block that reads **total** Oath or element
  changes, which a split draft does not dilute.

No caps on the new cards; [USER] dislikes them.

## 3. The cards (3 in, 3 out; one re-aimed; the pool stays 78 at 20 / 35 / 23)

| Card | Type, cost, rarity | Text | Replaces |
|---|---|---|---|
| Gale Mantle | Skill, 1, C | Gain 5 [8] Block, plus half your total Oath. | Squall (C, "Deal 4 twice", a vanilla filler) |
| Gust Ward | Skill, 0, U | Gain 4 [6] Block. Draw 1 card. | Four Banners (U; a seat: "2 energy for 10 to 15", "never earned a play") |
| Windborne Resolve | Power, 1, U | Whenever your current element changes, gain 5 [7] Block. | Favonian Standard (U; a seat's NEVER AGAIN, "dead draw") |
| Oathbound Aegis (re-aimed) | Power, 2 [1], R | At the end of your turn, gain Block equal to half your total Oath. | was "equal to your total Oath, up to 15 [20]" |

- **Gale Mantle** is the split deck's Common: it is never worse than a
  Defend, and it grows with every Oath he has, in any element. "Half" rounds
  down. At 40 total Oath it gives 25.
- **Gust Ward** is cheap Block that also digs out of a dead hand.
- **Windborne Resolve** is the Block twin of Cycle of Seasons (damage on a
  change), for the switch deck.
- **Tailwind Guard stays 3 [4] per element.** The draft raised it to 4 [5];
  [USER]: "sounds potentially insanely strong at 16 block for 1 energy
  flat, but it does require some setup and is uncommon... possibly fine.?"
  The main session kept the old numbers: at four elements it already gives
  12 [16], and Gale Mantle and Windborne Resolve now carry the switch deck.
- **Oathbound Aegis** loses its cap. Half the total is the price of that: at
  40 Oath it gives 20 a turn. The upgrade is a cost cut.

## 4. The element-less turn (pick 2)

Four of his cards read the current element (Favonius Drill, Oath of the
Knights, Four Winds' Ascension, Wind Wall's bonus). A seat wasted 7 Energy on a
boss's first turn with no applier in hand. **Proposed: Boreas's Fang makes
the starter Knight's element current at the start of each combat.** Any
Knight or element card then switches it, as now. It is one line on the
starting relic, and it ends the dead turn 1.

## 5. Checks before the build

Rerun the Block probe (`scratchpad/varka-block/block_probe.py` from the
measurement, or the sim tool) on the new pool. The bars are the default
drafter's act-3 Block over incoming up from 0.55 to 0.72, without Hydro mono
running past 1.5, and no turn-cap stalls (the sim's only stalls were Block
decks).

## Picks (ruled)

1. **The Anemo defence (§3).** Ruled: yes, Tailwind Guard unchanged.
2. **Boreas's Fang sets the starter Knight's element at combat start (§4).**
   Ruled: yes.
