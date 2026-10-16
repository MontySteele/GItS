# Yae review r1: the Rites round, 2026-10-14

These are the first seats on the ruled Rites build (#1286, deployed as 0.2.5475).
Nine blind Sonnet seats played at A0, each on its own seed. The seat
records are in the session scratchpad (`seats/archive/yae-rites-*`). Raw
transcripts are not kept. Your rule for this round was: "If we have a build
we actually like, do the full 5 - otherwise just 2 as a sanity check for 'does
this survive act 1 now and do the cards work'".

## Result: 0 wins in 9, two cleared act 1

| Run | End |
|---|---|
| r1 | Died in act 1, floor 8 (Cubex Construct) |
| r2 | Died in act 1, floor 11 (Snapping Jaxfruit and Flyconid) |
| r3 | Died to the act-1 boss (Waterfall Giant), floor 17 |
| r4 | Died to the act-1 boss (Ceremonial Beast), floor 17 |
| r5 | Died in act 1, floor 8 (Gremlin Merc) |
| r6 | Beat both bosses; died in act 3, floor 42 (four Scrolls of Biting) |
| r7 | Died to the act-1 boss (Waterfall Giant at 121 of 240), floor 17 |
| r8 | Died in act 1, floor 8 (three Raiders) |
| r9 | Beat the Ceremonial Beast; died in act 2, floor 22 (the Bowlbug room) |

**Do the cards work? Yes.** No run crashed or got stuck. Each Rite fired as
written. Red Ink stayed on a card and survived a reshuffle, and Tenko fired
under the current Rite.

**Does she survive act 1? Sometimes.** Before the Rites she went 0 for 6,
and all six died in act 1. Now two of nine cleared it, and one of those
reached floor 42. The other seven died the same way: a slow loss of HP over
several fights, then one big turn she could not Block. The base-five
baseline (2026-10-05) had all five seats reach act 3.

## What played well

- **Wildfire is the Rite the seats liked.** In run 5, Foxfire Sweep and
  Grafted Branch killed one Corpse Slug. The others ate it and were stunned,
  turn after turn. In run 2, Twin Sakura and Sweep killed both Inklets at the
  end of the turn, before they attacked.
- **Thunder Rite's Tenko** was named the best card twice (runs 4 and 7). In
  run 4, Foxfire Lure, Twin Sakura and a Tenko took a Nibbit from 21 HP to 6,
  and the end-of-turn strikes finished it.
- **Warding carried the act-2 run (r9).** Shrine Maiden's Guard switched the
  shrine to Warding, and Mikage Thunder's Tenko then made 20 to 29 Block a
  turn.
- **Exact lethals off end-of-turn strikes.** Seats planned around them, and
  this was what Yae is meant to feel like. Thunderbolt Tithe and Yakan
  Offering were the cards the seats were happiest to draw.

## What did not

- **A plant pays too slowly to fund act 1.**
  - A Level-1 Sakura in Thunder strikes 3 a turn for three turns, so 1 Energy
    and a card buy 9 damage over three turns. A Strike is 6 damage now.
  - Defect's Zap is the nearest base card. Its Lightning hits 3 every turn
    with no end, and 8 more when it is pushed out.
  - Seats won their fights but spent too many turns planting instead of
    blocking. HP fell like this in four runs: 72 → 53 → 39 → 30 → 10, then
    72 → 62 → 46 → 28 → 6, then 72 → 54 → 40 → 26 → 13, then 72 → 62 → 47 → 37 → 6.
- **The Level cap of 3 makes four cards blank.** Once three Sakura stand at
  Level 3, Yakan Evocation, Twin Sakura, Rooted Shrine and Grafted Branch
  still print as if they raise Levels, but they do nothing (run 4). That cap
  also limits "Levels are the scaling" to a 5-damage strike.
- **A Rite switch hides its cost.** Four seats were surprised. Foxfire Sweep
  says "Rite: Wildfire", and nothing showed that against one enemy the Sakura
  would now hit for 1 or 2 instead of 3 or 5. One seat put Manuscript Pile on
  its never-again list because Offering replaced Thunder.
- **Tenko does nothing with no Sakura standing,** and the card does not say
  so (run 4).
- **The Edit and Publish half rarely mattered** in act 1 (runs 1, 7). Never
  again: Sakura Seal (two cards for what Yakan Evocation does), Fox Trick
  (Artifact ate its Weak), Mischievous Teasing, and Kitsune Rite ("a nothing
  card").
- **Seat harness:** in three runs, card numbers like "Strike (1)" pointed to a
  different copy after a play or an Edit. The page promised they do not
  shift. A fix is in review.

## Changes Claude builds (no pick, #1291)

1. **A Rite card shows what the shrine will do.** Example: "Rite: Wildfire
   (your Sakura: 2 to ALL)". The same line goes on the Rite badge.
2. **Tenko says "(no Sakura)"** when none is standing. No card is made
   unplayable.
3. **Sakura Seal costs 0** (it was 1). It is two cards for one plant, so it
   should not also cost a full Energy.
4. **Kitsune Rite:** "Tenko. Draw 1 card." It is Uncommon, so the cantrip is
   allowed there.

## Picks

**Ruled 2026-10-14.** [USER]: "1) agreed on a) 2) How about we uncap the
level entirely and just let anything that raises the cap stick cumulatively.
Level becomes Yae's version of Focus where most bonuses are transitory or
per-Sakura, except for specific Rare effects that are global. 3) Agreed here,
unless the Yae changes finish before the current seats, in which case I'd
rather you do 3 Kokomi and 2 Yae to have time for an extra Yae round before
I'm back."

*How Claude reads pick 2:*
- No Level cap. Levels are per Sakura and vanish when it withers.
- Fox's Mooncall (Rare) is the global source: "Your Sakura are planted 1
  Level higher." Each copy adds 1.
- Sakura Grove's global "+2 a strike" was Uncommon. It becomes "At the start
  of your turn, your newest Sakura gains a Level."
- Mikage Thunder's "+1 for the rest of combat" becomes "Each Sakura gains a
  Level. Tenko."

The options as they were offered:

1. **What a Sakura does when it withers.**
   - **(a, default) Last Bloom:** when a Sakura withers, it strikes once more
     under the current Rite. A plant then pays 12 over its life at Level 1
     instead of 9, and Deadline Extension and "lasts 1 more turn" become
     choices about timing rather than plain upside. This is the nearest
     thing to Defect's evoke, without copying orbs.
   - (b) Sakura last 4 turns instead of 3.
   - (c) No change. Fix only the numbers and the display.
2. **The Level cap.**
   - **(a, default)** Raise it to 5 (Fox's Mooncall: 6), so the cards that
     raise Levels keep working through a long fight.
   - (b) No cap.
   - (c) Keep 3, and have those cards print "(at Level 3: nothing)".
3. **What follows.**
   - **(a, default)** Claude builds the no-pick list and your picks
     tonight. Kokomi's five to eight seats go first, then Yae runs two seats
     on any free lanes, then you play her.
   - (b) You play the current Yae build first.
