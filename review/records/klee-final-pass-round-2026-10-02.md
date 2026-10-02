# Seat round: Klee's final pass (w15, 2026-10-02)

Build 0.2.4228, which is main after #839, the final pass:
- HP 70;
- Cover Your Ears! in;
- Where Did I Put It? out;
- Blast Shield moved to Common.

There were two Sonnet seats, one act per seat with a handoff, at ascension
0, on the w12/w13/w14 Klee seeds. Nothing was forced into the deck, so the
seats drafted for themselves. The raw records are gitignored, in this
session's scratchpad: `w15-lane1` and `w15-lane2`.

## Results

| Lane | Seed | Act 1 | Act 2 | This seed before |
|---|---|---|---|---|
| 1 | QRK0WY8GG6RY | Lagavulin Matriarch beaten, 69/81 | died to The Insatiable, whose Sandpit countdown ran out with the boss at **11/321** | died in act 1 in w12, w13 and w14 |
| 2 | 4S949HRNQFGH | Matriarch beaten, 5/74 | died on floor 31 to Bowlbug Rock, Bowlbug Silk and Slumbering Beetle | Kaiser Crab (w12, w14), the same floor-29 room (w13) |

Klee is still without a seat win: eleven runs since the status package.
This is the first round where both runs cleared act 1. Lane 1's seed
reached the act-2 boss for the first time and lost it by one card: the
seat played Defend where the Frantic Escape in hand would have pushed
Sandpit back a turn, and it said this was its own misread. Lane 2 won the
act-1 boss at 5 HP and died in act 2 with Relax, Cover Your Ears! and
Bennett already spent.

## What the pass changed

- **Seats now draft defence.** Last round both seats passed every Block
  card. This round lane 1 took Diona, Return to Sender, Up in Smoke!, Qiqi,
  Blast Shield, Windtrace, Run Away! and Cover Your Ears!, and bought
  Behind Jean's Desk. Lane 2 took Barbara, Cover Your Ears!, Survival
  Rulebook, Sayu, Bennett, Klee Can Explain! and Blast Shield.
- **Sparks no longer pile up in act 2.** Lane 1, act 2: "Sparks no longer
  pile up unused: Blast Shield, Booby Trap+, Cover Your Ears!, Bag all
  spent them." Lane 2 ended every act-2 fight on 0 Sparks. In act 1 they
  still sat at 2 to 6 before a spender was drafted.
- **Cover Your Ears! works where it was aimed.** It was played about seven
  times across both runs:
  - 8x2 became 4x2 on The Insatiable;
  - 9x2 became 3x2 on the Matriarch, for 0 taken;
  - 24 became 10 on the Beetle;
  - 17 became 11 on the Hunter Killer.

  It is dead as an opener, because a fight starts on 1 Spark and it costs
  2. Lane 2 drew it unplayable in three act-1 openers. That is acceptable
  for a boss-turn card, but it is the card's one complaint.
- **Blast Shield at Common** was taken in both runs and played about eight
  times, 6 Block each (4 under Frail).
- **HP 70** shows in the margins: lane 2 won the act-1 boss at 5, and
  lane 1 won the Infested Prism elite at 2.

## What did not

- **Forbidden Fun** was named NEVER AGAIN by both lane-2 seats. With the
  Haunted Ship's Dazed it left six Dazed in the deck by the boss, and its
  10 damage fell to 6 or 2 under Strength loss. It stays on the watch list
  as a Dazed loader for the status package.
- **Behind Jean's Desk** was named NEVER AGAIN by lane 1 in act 1: "11
  block that shuffles a dead Confiscated into the deck." The w14 seats
  rated it strong. It stays as is.
- **Run Away!** was named NEVER AGAIN by lane 1 in act 2: "0 cost 3 Block
  that never changed a fight."
- **Setup turns against a sleeping boss** were the act-1 NOTHING turns:
  play Qiqi or Dumpty, then end turn.

## Readability, for the fix batch

- **Hand Drill gave no Vulnerable when a Bomb broke the boss's Block,** only
  when a Pyro card's hit did (lane 2 act 1). Check whether a Bomb hit
  reaches the base relic's break-Block hook.
- **Tender** (the Hunter Killer's debuff: each card played costs 1 Strength
  and 1 Dexterity this turn) printed only "Tender 3". Card faces updated
  only after each play.
- **Fireworks Finale** printed "2 damage per Spark. Written: 5" with no word
  that the player's Strength loss lowered it.
- **Big Badda Boom** ("damage equal to what your Bombs dealt") does not say
  whether Bombs set off earlier in the turn count.
- **Spiny Toad's Thorns** showed on its panel on turn 1 only.
- **Set off hits only the targeted enemy's Bombs.** Seen again; this is the
  standing item from the w10 batch.
