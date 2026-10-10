# Varka: Hydro becomes the Block-payoff element, 2026-10-10

[USER] on the Hydro pick (#1017): "Block is fine if boring. I do wonder if we have a conflict between making Hydro Varka desirable but also printing enough Anemo Block that he's functional without it. So the Hydro Varka style might need fewer 'generate block' effects and more 'Block Payoff' effects - details depending on how many actual block cards he has in total compared to other characters."

## The census

Counts are of draftable pools; starters are not included. My working is in the session scratchpad (`block-census.md`). The base-five numbers come from `game_ref`, and Varka's from `VarkaRoster.Pool()`.

| | Cards that give Block | Share of pool | Block payoffs |
|---|---|---|---|
| Base five (mean) | 11.4 of 85 | 13.4% | Ironclad 3, the others 0 |
| Varka | 14 of 78 | 17.9% | 1 (Retaliating Tide) |
| Varka without Hydro | 9 of 78 | 11.5% | 0 |
| Kokomi | 14 of 78 | 17.9% | 5 |
| Furina | 8 of 78 | 10.3% | 0 |

Varka also has three Block Powers that work in any element: Windborne Resolve, Dawn Wind's March and Oathbound Aegis. He prints more Block than any base character. Without his five Hydro cards he sits at the base level.

**The answer to the conflict:** Varka is functional without Hydro. A non-Hydro Varka has base-level Block plus three Block Powers, and two seats built 31- and 37-Block turns from Windborne Resolve alone. So Hydro does not need to supply Block; it can reward having it. Seats skip Hydro (7–9% take rate) because today it only does what Defend does.

## The change (Claude ships; the two Commons stay)

Hydro goes from five Block cards and one payoff to four and three. Rippling Guard, Gleeful Songs and Wellspring Hymn stay as they are: they are the entry points that make the Block a payoff needs.

1. **Tidal Bulwark becomes Hydro's Body Slam.**
   - Today: Skill, 1. "Apply Hydro. Gain 4 Block, plus 2 for each Hydro Oath."
   - New: Attack, 1. "Deal damage equal to your Block, plus 2 [3] for each Hydro Oath. Apply Hydro."
   - Body Slam is a base Common at 1 [0]. This card's Oath bonus pays for Uncommon.
2. **Barbara: Whisper of Water keeps its Block between turns.**
   - Today: "Apply Hydro. Gain 4 [6] Block. For 2 turns, at the start of your turn gain 4 [6] Block."
   - New: "Apply Hydro. Gain 4 [6] Block. Your Block is not removed at the start of your next turn."
   - This is the base game's Blur. It turns a 12-Block card into one that pays off the turn's other Block cards.
3. **Retaliating Tide** is already the Rare payoff. It is unchanged.

Overall, Varka's Block cards go from 14 to 13, still above the base five, and his payoffs go from 1 to 3.

## When it ships

- This builds on `klee-next` **after your Varka run tonight**, so your run grades the version the seats graded.
- After that, two seats with a forced Barbara start (`--varka-knight hydro`), graded on three lines:
  1. Tidal Bulwark and Whisper are taken from rewards.
  2. Tidal Bulwark hits for 15 or more at least once a fight in a deck that holds it.
  3. No seat reads Whisper's retention as permanent.

## For [USER]

1. **Is "Hydro = Block payoffs" the direction you meant?** Default: yes, as above.
2. **Should Wellspring Hymn also become a payoff?** For example: "Whenever you gain Block, gain 1 Hydro Oath" as a Power, which would feed Tidal Bulwark and Retaliating Tide. Default: no. Its cleanse is the only one in the pool.
