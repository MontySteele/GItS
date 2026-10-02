# Seat round: Opus plays Klee on the final-pass seeds (w16, 2026-10-02)

[USER] asked whether the deck had gotten worse or Sonnet was just a weak Klee
player: "Prior to the status changes, Opus (you) reliably got to the end of
act 3 on Klee". On 2026-09-26 (build 0.2.3841) two full Opus runs won one
run and died once in act 3 (`klee-later-acts-2026-09-26.md`).

The seats were Opus, and Claude is the kit's author, so these runs are
[USER]'s instrument, not a blind grade. Each seat played one act and passed
a handoff note to the next, as the Sonnet seats did, at ascension 0, on the
w15 seeds, with no cards forced into the deck.
- Lane 1 ran on 0.2.4228.
- Lane 2 ran on 0.2.4232: #841 had landed, so the bridge defined words
  again for each new seat (`new-seat`), and Grounded's tooltip said what it
  pays.

The raw records are gitignored, in this session's scratchpad under
`w16-opus-lane1` and `w16-opus-lane2`.

## Results

| Lane | Seed | Act 1 | Act 2 | Act 3 | Sonnet on this seed (w15) |
|---|---|---|---|---|---|
| 1 | QRK0WY8GG6RY | Lagavulin Matriarch beaten, 20/81 | the Ancient healed to 81; died on floor 25 to Spiny Toad at 6 HP | | lost the act-2 boss with it at 11/321 |
| 2 | 4S949HRNQFGH | Matriarch beaten, 56/70 | Kaiser Crab beaten, 27/70 | **won**: Test Subject beaten on floor 48, 13/70 | died on floor 31 |

This is Klee's first seat win since the status package, after eleven Sonnet
losses. One Opus run won and one lost before the act-2 boss, which matches
the 2026-09-26 Opus pair. The deck can still win. Sonnet is the weaker Klee
player, but not the whole story: lane 1 lost the way the Sonnet runs did.

## What decided the two runs

- **Lane 1 drafted for damage and had no Block when it mattered.** By act 2
  its 26-card deck had 4 Defends, Diona, Dig In+ and Cover Your Ears!.
  Louse Progenitor took it from 34 to 6 over three turns with no Block card
  in hand. The seat also popped a Mine early with Perfect Timing, which is
  itself a Set off, and said the screen was clear and the misread its own.
- **Lane 2 found a Spark engine.** Boom Badge and Booby Trap came in act 1,
  and Fireworks Finale, Bottomless Bag and Quick Fuse+ in act 2. In act 3
  Whispering Earring, Party Poppers+ and Blast Shield+ made the winning
  turn: twelve Blast Shields for 136 Block and a 98 Bomb stack, then Big
  Badda Boom+ for 18 + 98 + 100.

## What played well

- **Choosing when to set off** was the real decision in every act: "each Bomb
  grows 4 a turn, so holding is always a trade against the incoming hit."
  Lane 1 held seven Bombs through the act-1 boss and set them all off with
  one Ka-pow! for 185 into 149.
- **The Bomb's damage number on the enemy was exact.** "Deals 59 with Melt
  (sizes 25)" already counts Vulnerable and the reaction. Both act-1 seats
  said every number they predicted landed.
- **Shriek stuns:** both runs set off Bombs to stop the Terror Eel exactly
  under its 70 line.
- **Act-3 boss:** the seat killed the 100 HP form early on purpose, because
  it gains Strength whenever you play a Skill.

## What did not

- **Sparks sit idle in act 1** until a spender is drafted: 3 to 8 a fight on
  lane 1, and nothing spent for five fights on lane 2. This is unchanged
  from w15.
- **NEVER AGAIN:**
  - Tinder Toss (lane 1, act 1): no Retain, so it fires early.
  - Playdate (lane 1, act 2): the Companion discount never applied.
  - Sit Tight (lane 2, act 1): its Spark cost starved Boom Badge.
  - Klee's Secret Base+ (lane 2, acts 2 and 3): "it needs no Bombs
    anywhere, and in this deck that never happens."
- **Elements were mostly unused on lane 1:** everything was Pyro until
  Kaeya at fight 7.
- **Blast Shield loop:** twelve plays in one turn is a lot for a Common.
  Party Poppers+ and Whispering Earring made it. Watch it, no change yet.

## The bridge gap this round found (fixed in #841)

The lane 1 act-2 seat reported "Grounded", "Companion" and the Bomb's "If its
enemy dies, it jumps to another" as never defined. All three are defined.
The bridge's short page defines a word the first time the lane meets it, and
`--define` read only the current screen. So every per-act seat after the
first, Sonnet's included, played without the definitions the
first seat saw. #841 added `blindplay new-seat`, made `--define` fall back to
the glossary, and made Grounded's tooltip say what it pays.

## Readability, for the fix batch

New lines, added to `BACKLOG.md` in this PR:
- **The reaction log contradicts the damage.** It printed "Melt ... No hit
  came with it, so there was nothing to amplify" beside a hit multiplied by
  1.75, on three fights (lane 2, act 1).
- **The Bomb's number ignores Boom Badge+.** It kept printing the undoubled
  number after Boom Badge+ was played (lane 2, act 2).
- **Jean+ is switched off by Dodoco+.** A Mine going off on the enemy's turn
  counts as "a Bomb went off last turn", and Jean+'s face does not say so
  (lane 2, act 2).
- **Perfect Timing's replay** did not visibly fire when its first Set off
  killed the target (lane 2, act 2).
- **A Mine going off before an attack** spends the aura set up for the big
  Bomb. Also, the Mine text does not say whether the enemy's other Bombs go
  with it (lane 2, acts 1 and 2).
- **Return to Sender** turns only its own Block into a Bomb; the page
  printed "8 Block left" (lane 2, act 3).
- **Between the act-3 boss's forms,** targeted cards are refused with "every
  enemy is dead or waiting to revive", and the board shows no enemy (lane 2,
  act 3).

Already in BACKLOG from lane 1 (#841):
- "Put Bomb 1" in the played-log;
- Louse Progenitor's Weak fold;
- Mine Spark accounting.

## Next

Nothing in this round changes the kit. The finish line is still [USER]'s
own run on the current build; fun through act 3 moves Klee to Balance.
