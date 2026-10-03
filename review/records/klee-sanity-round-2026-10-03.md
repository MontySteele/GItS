# Seat round: Klee sanity check before Balance (w17, 2026-10-03)

[USER] (co-op paper, pick 1): "push the new build with the most recent
changes, give it one last playtest as a sanity check, and if nothing turns
up, then we move to Balance."

Build 0.2.4269: everything through #857. For Klee that adds Jumpy Dumpty
without Innate (#844), element wording and hit effects, and the cast/power
motion (a 0.25 s wait per Skill). Two Sonnet seats, act 1 with a handoff,
ascension 0, on the w15/w16 seeds. Raw records are gitignored, in this
session's scratchpad under `w17-lane1` and `w17-lane2`.

## Results

| Lane | Seed | Act 1 | w15 Sonnet | w16 Opus |
|---|---|---|---|---|
| 1 | QRK0WY8GG6RY | died to Lagavulin Matriarch, floor 17, in at 49/81, boss left ~99/222 | beat it, 69/81 | beat it, 20/81 |
| 2 | 4S949HRNQFGH | died to Lagavulin Matriarch, floor 17, in at 28/74, boss left ~50/222 | beat it, 5/74 | beat it, 56/70 |

Both runs lost the act-1 boss, on seeds where all four earlier seats beat it.

## What decided it

- **Fewer Bomb turns.** Lane 2: "roughly half of all turns had no Set off in
  hand"; those were Strike and Defend turns. The turn-1 Dumpty lines in the
  records fell from 9 and 11 (w15) to 5 and 8. Jumpy Dumpty losing Innate is
  the one Klee card change since w15 and the likeliest cause. Two runs cannot
  separate it from the draft.
- **Confiscated clogs long fights.** Lane 1 ended with three Confiscated and
  no Block in hand against 22 incoming. Behind Jean's Desk is NEVER AGAIN for
  the second Sonnet round running (w15 lane 1 too).
- **Chip damage on the way.** Lane 2 left the Haunted Ship fight at 6/74 and
  had one rest to recover.

## What played well

- Holding Ka-pow! while Bombs grow, then Set off: Terror Eel 89 to 50 in one
  turn, stunned on its line; the boss's 3 sleeping turns turned into about
  45 Bomb damage.
- Klee Can Explain! turning a Confiscated into Pop! to land the Eel exactly
  at 70.
- The "Written:" face beside the board number under Weak read clearly.

## What did not

- Sparks idle in act 1 until a spender is drafted (unchanged from w15/w16).
- NEVER AGAIN: Behind Jean's Desk (lane 1); Second Surprise (lane 2: "only
  Dumpty and Booby Trap make Mines").
- Readability, already in BACKLOG: "Put Bomb 1" in the play log; Set off hits
  only the targeted enemy's Bombs.

## Next

Something turned up, so Klee does not move to Balance on this round. The
choice is [USER]'s, since Jumpy Dumpty's Innate was his ruling.
