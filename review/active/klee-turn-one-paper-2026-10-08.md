# Klee's turn one: a short paper, 2026-10-08

Asked for by suite 4 (`review/records/klee-suite-4-2026-10-08.md`, pick 2).
[USER]: "My initial thought is to turn reducing bomb growth to 2 per turn,
but giving 3 sparks rather than 1 on turn 1 to make non-bomb decks more
consistent. But I'm open to your suggestions as well."

The two rules in question (`review/active/klee-brief-2026-09-01.md` sec.3):
rule 1, every Bomb grows by 4 at the start of her turn; rule 4, she starts
every combat with 1 Spark.

## 1. Turn one is a choice to wait, not a lack of cards

Act-2 and act-3 normal fights in suites 3 and 4 (67 fights, fight
telemetry, `cards_played`):

| Turn-one play | Fights |
|---|---|
| Jumpy Dumpty (the starter Bomb) | 67 of 67 |
| Ka-pow! (the starter Set off) | **0 of 67** (13 on turn two) |
| Any Set off card | 16 of 67 |
| Explosive Spark | 2 of 67 |

Every seat places the starter Bomb on turn one and holds Ka-pow! while it
grows. With growth at 4, a Bomb 8 cashed on turn one is 8; on turn three it
is 16. Waiting is right by the numbers, so turn one deals 5 to 11.

**The tier-0.5 sim shows the other side.** Its pilot sets Bombs off as soon
as it can (`tier0/pilot/policy.py`: "The pilot has no cook-or-cash
policy"). That Klee deals 45 on turn one of an act-3 fight, near the sim's
base Ironclad (49). So her decks can deal early damage; rule 1 pays her
not to. (3,000 runs a variant, seed 42, worktree at `klee-next` aeb2c069;
the sim cannot reproduce the seats' cooking, so its numbers are direction,
not a measurement.)

## 2. The proposal, through the sim

Same 3,000 seeds for each; the pilot cashes early, so these show what each
change costs a player who already plays fast.

| Variant | Act-3 turn-one damage | Win rate | Mean floor |
|---|---|---|---|
| A. Today (growth 4, 1 Spark) | 44.6 | 5.1% | 24.3 |
| B. Growth 2 | 44.5 | 3.6% | 22.4 |
| C. 3 opening Sparks | 44.9 | 5.4% | 24.6 |
| D. [USER]'s proposal (B + C) | 45.1 | 3.9% | 22.7 |
| E. D, and every placed Bomb +2 | 46.3 | 4.8% | 24.3 |
| F. Growth 3, 2 opening Sparks | 44.6 | 4.6% | 23.6 |

(Win-rate standard error about 0.4 points.)

- **Growth 2 costs the fast player** about 1.5 points of win rate: her
  Bombs are smaller whenever she cashes. That is the price of taking away
  the reason to wait, and it lands on the play style we want.
- **3 opening Sparks is close to free** and does what [USER] asked: a deck
  that is not built on Bombs has Sparks to spend on turn one (Explosive
  Spark, Tinder Toss, Boom Badge).
- **+2 on every placed Bomb pays the growth loss back** (E is level with
  today). A Bomb cashed the turn it lands is bigger; a Bomb held three
  turns grows 6 instead of 12. Cashing now is worth more, waiting worth
  less, which is the trade the tempo direction wants.

## 3. Recommendation

[USER]'s two rule changes, plus +2 on every card that places a Bomb or Mine,
**except Jumpy Dumpty**, the starter (starter basics are never changed
without [USER]'s pick). The starter's own sum: Jumpy Dumpty's Bomb 8 cashed
by Ka-pow! on turn one is 12 damage; held to turn three it is 16 under
growth 2, against 20 today. Waiting still pays, but half as much as it
does now, and the drafted placers at +2 and 3 Sparks in hand give turn one
something to spend on.

- **Rules:** rule 1 growth 4 to 2 (Alice's Recipe still doubles it, to 4);
  rule 4 opening Sparks 1 to 3. Both edited in place in the brief.
- **Cards:** every drafted Bomb or Mine placer's size +2 on the sheet
  (base and upgrade), printed on the card. Placers inside other effects
  (Jumpy Dumpty Mk.III's per-hit Bomb, Secret Base's turn-start Bomb)
  get +2 the same way. Jumps and copies of an existing Bomb do not.
- **Risk:** Cook's big boss turns get smaller (The Big One's x4 on a pile
  that grew 2 a turn). The round reads boss fights separately.

## Picks

1. **The change.**
   - **Default (a):** growth 2, 3 opening Sparks, +2 on every placer except
     Jumpy Dumpty, built on `klee-next`.
   - (b) [USER]'s proposal as stated: growth 2 and 3 opening Sparks only.
   - (c) (a), and Jumpy Dumpty +2 too (Bomb 8 to 10): a starter change.
2. **The round.** **Default:** suite 5 on the same five seeds, read on
   turn-one damage, turn-one Set off plays, fight length, and boss fights
   separately.
