# Varka seat round: the element identities (2026-10-01)

Build 0.2.4112: the element identities (#793: Electro's discard-and-spend
cards, the X-cost Thundering Verdict, Retaliating Tide, Wildfire's one big
hit, the switch warnings), on the 78-card pool. Two Sonnet seats, one act per
seat with handoff notes, ascension 0, game-rolled seeds. Raw records are
gitignored (session scratchpad `w8-lane1/`, `w8-lane2/`).

## Results

| Lane | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| 1 | The Kin beaten, 50/87 | The Insatiable beaten, 65/97 | died on floor 48 to Queen and Torch Head Amalgam (Queen 266/400) |
| 2 | Vantom beaten, 47/80 | Kaiser Crab beaten, 17/80 | the lane died on floor 45 (bridge state timeout) at 13 HP, with 44 incoming |

Both runs reached act 3 again, and neither won.

## What played well

- **Reaction ordering is still the best decision in the kit.** For example,
  lane 1 played Charged Lunge+, Windbound, then Four Winds' Ascension last,
  taking the Effigy from 62 to dead.
- **Electro now has a deck.** Swapping Hydro and Electro made Poison: it
  stacked to 15, ignored Block, and won fights on both lanes (the Frog Knight,
  191 HP; the Kaiser Crab finish). The X-cost Thundering Verdict decided most
  of lane 2's act 2: at X=4, 27 per hit stunned the Tunneler through 32 Block.
- **The Oath burst still wins bosses.** Lane 1 beat The Insatiable on one
  turn: Rally to the Banner moved 18 Oath to Electro, then Four Winds'+ hit
  for 118.

## What did not

- **Hands with no element are dead hands.** Both lanes, every act. Favonius
  Drill, Oath of the Knights, Four Winds' Ascension and the Wind Wall and
  Knightly Guard bonuses all read a current element. Lane 1 wasted 7 Energy
  on a boss's turn 1 (10 Energy, no applier).
- **Block cannot keep up.** Weak, Frail and multi-hit enemies beat every
  Block card. Lane 1's death was 48 incoming against 13 Block. Lane 1's act 1
  was the exception: Block outran a weak boss, and the turns were safe and
  dull.
- **A one-card plan.** Four Winds'+ with Andrius's Howl hit for 33 to 58 every
  turn, "and once the boss's debuffs stopped me surviving long enough to set
  it up, nothing else in the deck carried the fight."
- **Readability:**
  - Thundering Verdict prints no per-hit number.
  - The Four Winds' log does not split its Swirl, base and Oath parts.
  - The Oath panel says "no current element yet" while Oath is above 0.
  - Melody Loop applies Hydro but does not set the element.

## What to change

1. **The element-less turn is the kit's main hole,** confirmed again. Options
   for a short paper: the Fang sets a current element at combat start (the
   starter Knight's), or cards that read the current element fall back to
   the element with the most Oath.
2. **Bugs to check:**
   - Weathervane's chooser appeared at the end of the turn, not the start of
     the next.
   - Sworn Brotherhood+'s "every element" seemed to raise only the current
     one.
   - Amber's preview said 27 into a Hydro aura and dealt 18.
3. **Faces:**
   - Thundering Verdict prints its per-hit damage.
   - The Oath panel's empty-element line counts Oath.
4. **Bridge:** the lane death on a state timeout (lane 2); `play` without a
   target spent a whole turn.
