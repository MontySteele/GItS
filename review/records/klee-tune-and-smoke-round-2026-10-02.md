# Seat round: Klee's tuned defence cards, and an act-1 smoke on the other three kits (w14, 2026-10-02)

Build 0.2.4218, which is main after legacy cleanup stage 6 (#832 to #835).
Since the w13 round it carries two changes:
- the defence tune (#831): Behind Jean's Desk is 11 [14], Up in Smoke!
  costs 0, and Kitchen Alchemy's upgrade adds Retain;
- the cleanup's engine deletions, which is why the other three kits got a
  smoke test.

All seats were Sonnet, played one act each with a handoff, at ascension 0.
The raw records are gitignored, in this session's scratchpad: `w14-lane1`,
`w14-lane2`, `w14-lane3`, `w14-lane4`, `w14-lane1v`.

- **Klee:** on the w12/w13 seeds, with the three defence cards placed in
  the starting deck by `embark --arm`. Granted cards make the deck one the
  generators never produced, so these runs judge the cards, not the kit's
  win rate.
- **Smoke tests:** Kokomi on her winning seed, Furina and Varka on seeds
  the game rolled.

## Results

| Seat | Seed | Act 1 | Act 2 | Same seed before |
|---|---|---|---|---|
| Klee lane 1 | QRK0WY8GG6RY | died on floor 14 (Terror Eel elite took 73 to 11; no rest site after floor 5) | | died to the act-1 boss (w12, w13) |
| Klee lane 2 | 4S949HRNQFGH | Lagavulin Matriarch beaten, no damage taken, 53/66 | died to Kaiser Crab, round 4 (Rocket's 33 into 16 Block at 13 HP) | died to Kaiser Crab (w12); floor 29 (w13) |
| Kokomi smoke | 5JNWQ9G4YNV7 | Waterfall Giant beaten, 21/80 | | won the run (w12) |
| Furina smoke | AQ6HSD7PLZWJ | died to Lagavulin Matriarch (37/222 left) | | |
| Varka smoke | 5E0SY4K9WL73 | Ceremonial Beast beaten, 68/80 | | |

**The smoke test passed.** None of the three seats saw an error, a
placeholder text, or a card that did nothing or something its text does
not say. The cleanup broke nothing a seat could reach in act 1.

Klee has not won a seat run since the status package (w10, w12, w13, w14:
nine runs at A0). The best reached the act-2 boss, as two earlier runs did.

## Klee's three cards, after the tune

| Card | Lane 1 | Lane 2 act 1 | Lane 2 act 2 | Read |
|---|---|---|---|---|
| Up in Smoke! (0, Weak 2 to ALL, a Dazed) | played 3 of ~10; "fair (strong at low HP)" | 2 of ~9; "fair" | 1 of ~7; "weak" | Now fair. At cost 0 the seats still pass it for a Defend most turns. |
| Behind Jean's Desk (1, 11 Block, a Confiscated) | 3 of ~11; "strong" | 4 of ~9; "strong ... the best block in the deck" | 3 of ~6; "strong" | Settled. At 11 it is still the best Block card, and the Confiscated is felt but fair. |
| Kitchen Alchemy (1, ALL lose 1 [2] Strength, +1 per status exhausted) | 1 of ~9; "weak", NEVER AGAIN | 1 of ~8; "weak", NEVER AGAIN | removed at the first shop | **Dead.** |

Kitchen Alchemy was played twice in about 26 hands across both rounds since
the rework. Act-1 enemies rarely carry Strength, and a status is rarely in
hand when it is. Two of the three seats named it as the card they would
never draft again. The Retain upgrade never came into play.

## What played well

- **Bomb timing still carries Klee.**
  - The Big One ("Your Bombs deal quadruple damage") ended a 63 HP Haunted
    Ship and a 124 HP Terror Eel in one card each.
  - The Matriarch fell for no damage taken: three setup turns while it
    slept, then Big Badda Boom from 222 to 34.
  - Tinder Toss, Ka-pow! and Pocket Match took the Eel across its
    Shriek-70 threshold for a stun.
- **Klee Can Explain! turned a Confiscated into Pop! for exact lethal.**
  This is the status package working as designed.
- **Act-2 rescue turn:** Once More!, Countdown, Return to Sender and Tuning
  Fork made 31 Block at 11 HP against the Entomancer.
- **Kokomi:** Open the Casket at 4, then two Undertows for 20 each, was her
  best boss turn.
- **Varka:** Tempest of the Four Winds fetched back by Liquid Memories,
  under Cycle of Seasons, for 9 hits, then Violet Storm+ for 6 x 16, took
  the Ceremonial Beast from 190 to 31 in one turn.

## What did not

- **Sparks pile up.** They sat at 2 to 8 at the end of every act-1 fight
  in both Klee lanes. They were spent only once lane 2 drafted Fireworks
  Finale in act 2, and Finale then killed Louse Progenitor. This matches
  w10, w12 and w13. A defensive Spark sink is still the open question for
  the Klee final pass.
- **Klee's losses were Block on the boss turn,** not damage. Lane 2 came
  up 4 Block short on Kaiser Crab's turn 4. Lane 1 lost 62 HP to one elite.
- **Furina:** Weak and Frail cut Defend to 1-2 and Strike to 3-4 late in
  the boss fight, and her stage kept being emptied by hits.
- **Where Did I Put It?** found a Set off card about 1 time in 5 and printed
  no reason when it found none. Lane 2 named it NEVER AGAIN in act 2.
- **Pael's Eye** exhausts the whole hand for the extra turn, finishers
  included. That is the base-game Ancient working as written.

## Readability, for the fix batch

- Furina's seat never saw her own Frail or Dexterity loss printed on the
  page, so the Block collapse was unexplained.
- Furina's stage log prints "Usher joined the stage" twice before "took its
  Bow to make room" on a Gala Premiere turn.
- Varka: Cycle of Seasons' damage prints on the line of the card that
  changed his element (in BACKLOG since #837).
- Kokomi: the Casket shows "(1)" on the relic between fights. The relic's
  counter is combat-only (`TamakushiCasket.ShowCounter`), so the page reads
  it before combat state clears.
- The Waterfall Giant's phase change (Death Blow 39 the turn after "0 HP")
  gives no warning that the fight goes on. This is base-game behaviour; the
  page could say so.
- Bombs set off into an enemy's Block are swallowed (a 29 Bomb did 13), and
  no Bomb text says so. Already in the w12 batch.
- Tuning Fork prints "(7)" with no "of 10".

## Next

1. Kitchen Alchemy needs a new job or a cut. Its slot goes into the Klee
   final-pass paper, together with her HP and a defensive Spark sink, so
   the three are read together.
2. Kokomi, Furina and Varka: the cleanup is cleared. Nothing waits on a
   seat round for them; Kokomi's next step is still [USER]'s run.
