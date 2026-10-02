# Seat round: the repeatable Casket and Klee's status-pile defence (2026-10-02)

Build 0.2.4204. It has four changes:
- Open the Casket costs 1 Energy and no longer exhausts (#827).
- Plans flip with a click instead of a turn-start screen (#827).
- Klee's three defence cards, Up in Smoke!, Behind Jean's Desk and Kitchen Alchemy (#826).
- Legacy cleanup stage 5 (#822, #824).

This is the first round on the four-kit review's pick 4a: fixed seeds, an Ironclad control on the Kokomi seeds, and the save-file numbers in the record. Each seat was Sonnet, played one act and handed off. All runs were at ascension 0. The raw records are gitignored, in the session scratchpad as `w12-lane1` to `w12-lane4`, `w12c-lane1`, `w12c-lane4` and `w12k-lane2`.

The Klee and Kokomi seeds are last round's (`klee-kokomi-round-2026-10-01.md`), so each run has a before and after.

## Results, from the game's save files

"Door" is HP entering the boss fight. "Normal fights" is the mean HP lost per normal fight.

| Run | Seed | Normal fights | Act-1 boss | Act-2 boss | Act-3 boss | Last round, same seed |
|---|---|---|---|---|---|---|
| Kokomi lane 3 | 5JNWQ9G4YNV7 | 10.2 | Waterfall Giant: door 51, 7 turns, won | The Insatiable: door 39, 7 turns, won | Queen: door 73, 11 turns, **won at 5 HP** | died to the Queen |
| Ironclad control | 5JNWQ9G4YNV7 | 4.6 | Waterfall Giant: door 72, 9 turns, won | The Insatiable: door 90, 4 turns, won | Queen: door 90, 12 turns, **won at 60 HP** | |
| Kokomi lane 4 | LURXU1TGSM38 | 18.1 | Waterfall Giant: door 91, 11 turns, won | Knowledge Demon: door 92, 10 turns, **died** (boss at about 92 of 379) | | died to the act-1 boss |
| Ironclad control | LURXU1TGSM38 | 14.3 | Lagavulin Matriarch (a different boss): won | Knowledge Demon: door 104, 6 turns, won | Queen: door 72, 6 turns, **died** (boss at 380 of 400) | |
| Klee lane 1 | QRK0WY8GG6RY | 8.7 | Lagavulin Matriarch: door 46, 9 turns, **died** | | | died on floor 25 |
| Klee lane 2 | 4S949HRNQFGH | 9.8 | Lagavulin Matriarch: door 53, 6 turns, won | Kaiser Crab: door 37, 7 turns, **died** | | died to Kaiser Crab |
| Klee, forced deck | 4S949HRNQFGH | 11.1 | Lagavulin Matriarch: door 56, 9 turns, won | Kaiser Crab: door 43, 9 turns, **died** (crabs at 32 of 408) | | |

The forced-deck Klee run had the three new cards placed in its starting deck. Kokomi's first full win came in lane 3.

A fixed seed fixes the map but not always the boss: on LURXU1TGSM38, Ironclad met the Matriarch where Kokomi met the Waterfall Giant.

## Kokomi against the control, same boss

| Boss | Kokomi damage per turn | Ironclad damage per turn |
|---|---|---|
| The Insatiable (321) | about 46 (7 turns) | about 80 (4 turns) |
| Knowledge Demon (379) | about 29 (10 turns, lost) | about 63 (6 turns) |

Kokomi now gets one act further on both seeds and won a run. But on the same boss she still deals about half Ironclad's damage per turn, which is the four-kit review's §2.8 finding: smaller now, not closed. Her one win came late in act 3, when an upgraded Nereid's Ascension carried out the first Plan twice and Strength reached 15 to 21. Her normal fights cost about as much as the control's on one seed and twice as much on the other.

## What played well

- **The Casket is now a decision.**
  - Seats opened it at a count of 4 or more, sometimes 5 or more.
  - They opened it before writing damage Plans, because a Plan takes in her Strength when it is written.
  - They weighed the Energy cost in acts 1 and 2. In act 3, relics paid 4 to 6 Energy a turn and the cost stopped mattering.
- **Click-to-flip costs nothing.** No seat flipped a Plan across the whole round. Seats wrote a Plan when they wanted its Plan line and played the card normally when they wanted its now-line. The flip is a safety net.
- **Klee's Bomb timing.**
  - Alice's Recipe grew three Bombs from 33 to 105 while the seat stayed behind Block, and Big Badda Boom then did 222.
  - Seats held Ka-pow! for a stun threshold (the Eel's Shriek at 70 HP).
- **Behind Jean's Desk and Up in Smoke! work when drafted.** The forced-deck seat called Behind Jean's Desk "strong": 14 Block, and with Tuning Fork several hits taken for 0. It called Up in Smoke! "fair", at its best on two-enemy bosses.

## What did not

- **Kitchen Alchemy was unplayable: 0 plays in 2 acts.** It needs a status in hand, and one rarely is there:
  - Dazed exhausts itself.
  - Statuses enemies add go to the discard pile.
  - Confiscated arrives only after a shuffle.

  Reworked: "ALL enemies lose 1 [2] Strength. Exhaust every status in your hand; they lose 1 more for each." Always playable.
- **Seats don't draft Klee's defence.** The two normal Klee seats passed on all three new cards: Behind Jean's Desk twice, and Up in Smoke! at 10 HP. Both Klee lane-2 runs took Pael's Claw, which makes Defends exhaust, and ran out of Block on the act-2 boss. Seats preferring damage is also true of the control. So this is about the instrument as much as the kit.
- **Klee's Sparks pile up** to 9 and then 15, with only Tinder Toss, Dig In and Boom-Boom Strike to spend them on. All four Klee runs reported it. Item for the Klee final pass.
- **The Queen walls every kit.** Her Chains of Binding plus Frail, Weak and Vulnerable for 99 turns: Kokomi survived on 5 HP, and the second Ironclad dealt 20 damage to her and died.

## Text fixes (added to the batch)

- Frozen says "next action deals 50% less", but the Shatter removes it first. Two seats were caught by this.
- A Plan's preview counts Vulnerable that may be gone when it lands (42 shown, 28 landed).
- Opening Gambit written as the last Plan has nothing to double, and nothing warns you.
- Tide Wall's Plan adds only the front enemy's attack; a trap against a boss and its minion.
- Mend heals only HP lost this combat. Check that the text says so ("Mend 6" healed 0 once).
- Bomb damage into an enemy's Block is swallowed, and no Bomb text says so.
- Hair Trigger with no Bomb out does nothing, with no warning.
- The Battleworn Dummy's Setting 3 (300 HP in 3 turns) can't be won and gives nothing.

## Watch list (additions)

- Behind Jean's Desk: [USER] called it "quite strong" and the forced seat agreed. Nerf candidate after one more round.
- Nereid's Ascension+ (Innate; the first Plan carried out twice): 94 and about 168 on single Plans.
- Pearl Current under Clorinde's Night Vigil (19 per hit).

## Next

1. Deploy the Kitchen Alchemy rework. Klee's next round places all three cards in two decks, because seats won't draft them.
2. Kokomi: [USER]'s run on this build is the rule-change test. The damage gap (about half the control's per turn on the same boss) is the open question for a paper after that run, not before.
