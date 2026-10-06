# Klee's scaling pass

Paper, 2026-10-05, main session. **RULED 2026-10-05, all six picks at their
defaults** ([USER]: "Yep, I agree across the board. Let's send this."). [USER]
opened it: "Yes, agreed - let's look at Klee's scaling."

**Draft 4,** after the second reviews by GPT and Fable. Both reviewed draft
3. What changed:
- **One measurement corrected (sec.1).** The turn table's "enemy HP" is
  enemy HP plus Block (GPT). A field for HP alone is being added.
- **The turn-2 sentence is corrected (Fable).** Her second turn does more
  than a base character's in acts 1 and 2. In act 3 it does not.
- **Secret Base no longer predicts a turn-2 change (Fable).** The tempo fix
  is now tested directly, with a staging-only relic in round 1.
- **Round 1 has three arms on two seeds:**
  - A and C;
  - A, B and C, the comparison GPT asked for;
  - A and C with the tempo relic.
- **Suite 2 waits** until a round moves the turn-2 figure (Fable).
- **The grading changes.** Boom Badge is graded on earlier kills (GPT), and
  Witch's Homework is ruled once a combat in words.
- **Two hypotheses are labelled as hypotheses.**

This paper proposes card changes for `klee-next`. Each change comes with a
prediction, which a round grades. Under the freeze, nothing here touches
`main`'s cards (the measurement paper, sec.6).

## 1. What falls behind

**Her damage arrives a turn late.** At the start of every turn, each fight
line records the enemies' total HP plus Block (`enemy_pool_by_turn`,
`PlayTelemetry.cs`). This table shows the share of the turn-1 total still
standing, in normal fights, from the suite-1 telemetry on the paired seeds.
A fight already won counts as 0.

| Act | Klee, turn 2 | Base five, turn 2 | Klee, turn 3 | Base five, turn 3 |
|---|---|---|---|---|
| 1 | 0.76 | 0.61 | 0.37 | 0.26 |
| 2 | 0.92 | 0.66 | 0.54 | 0.39 |
| 3 | 0.90 | 0.57 | 0.66 | 0.32 |

- **Turn 1:** in acts 2 and 3, Klee's first turn removes about a tenth. A
  base character's removes a third to two fifths.
- **Turn 2 shows the flat Bombs** (Fable's reading):
  - Her second turn removes 0.39, 0.38 and 0.24 in acts 1, 2 and 3.
  - The base five's removes 0.35, 0.27 and 0.25.
  - In acts 1 and 2, waiting buys her a bigger second turn. By act 3 it
    buys nothing extra.
- **Why it happens:** a Bomb placed on turn 1 deals nothing until a later
  Set off, so enemies get an extra attack.
- **It answers the act-1 puzzle:** she deals as much damage a turn as a
  base character and gains more Block, yet loses 1.31 times the HP.
- **Act-3 normal fights:** she loses 18.1 HP a fight, against their 10.8.
- **Caveat (GPT):** enemy Block counts in the figure, so the shares are not
  exact HP removed. The gap between Klee and the base five is large, and
  Block affects both. A field for HP alone (`enemy_hp_by_turn`) is being
  added, and round 1 is graded on it.

**Her Bombs barely grow over the run.** Damage a turn, all fights:

| Act | Bombs + Mines | Klee's cards | Klee total | Base five total |
|---|---|---|---|---|
| 1 | 11.4 | 12.3 | 23.7 | 23.0 |
| 2 | 14.3 | 20.7 | 35.1 | 39.6 |
| 3 | 14.5 | 22.7 | 37.2 | 52.7 |
| Growth, act 1 to act 3 | ×1.27 | ×1.85 | ×1.57 | ×2.29 |

- **The base five's main cards grow over the run.** On the same seeds,
  damage a play from act 1 to act 3:
  - Ironclad Strike: 7.4 to 21.5.
  - Silent Shiv: 5.6 to 11.1.
  - Defect Strike: 5.9 to 11.2.
  - The Scythe: 27.6 to 67.8.
- **Big Badda Boom** grows only because it copies Bomb damage.

**These are one problem seen twice.** Most of her damage comes from Bombs,
and Bomb damage is both delayed and flat. A fix has to make Bombs pay
sooner, as well as bigger.

**Boss-entry HP** (`hp_start`) was fine:
- She entered act-1 bosses at 86 to 100% and act-2 bosses at 54 to 83%.
  The base five entered at 54 to 95%.
- Fatal fights are now logged (#938), so her boss deaths can be read from
  round 1 on.

**Her Strength.** The telemetry did not log the player's Strength; it does
since #938.
- The seat records show very little: Vajra (+1) in two runs and one
  Strength Potion.
- Fable's caveat stands: seats may skip Strength partly because it does
  nothing for her Bombs. So "she holds little" understates what pick 4
  would be worth.

## 2. Why her Bombs are slow and flat

1. **Set off cards limit her first turn** (Fable).
   - She starts with one Set off card, Ka-pow!, and every suite-1 lane held
     it for lethal.
   - Setting off a Bomb on the turn it is placed gives up its growth of 4
     (`KleeOverhaulLaw.BombGrowth`) and leaves a small hit.
   - So her first turn places Bombs, and enemies attack once more.
2. **No Uncommon card makes ordinary Bombs better.**
   - Each base character has 1-cost Uncommon Powers that improve its damage
     (`game_ref/*.json`):
     - Ironclad: Inflame.
     - Silent: Accuracy and Noxious Fumes.
     - Defect: Storm, Thunder and Hailstorm.
     - Necrobinder: Friendship and Haunt.
     - Regent: Furnace.
   - Klee's eight Uncommon Powers all pay only under a condition. Her
     steady growth Power is Alice's Recipe, a 2-cost Rare.
3. **Her payoff cards are weak or hard to line up.**
   - **Weak:** Witch's Homework (+8 to the largest Bomb) and Half a
     Mountain (double it) grow a Bomb that stays on the board, with no
     same-turn condition. Seats passed them. Witch's Homework was offered
     three times in lane 2's act 1 and never taken.
   - **Hard to line up:** Boom Badge needs 2 Sparks, a big Bomb and a Set
     off card on the same turn. Two seats took it and never played it.
4. **Nothing carries over between fights.** The Scythe grows for the whole
   run. Klee has nothing like it.

## 3. What does not change, and what the changes aim at

**Her flat numbers stay.**
- In act 1 she deals 1.03 times a base character's damage and loses 1.31
  times its HP.
- Two of five runs died at the act-1 boss.

If a later suite shows act-1 damage above 1.15 times, that is a signal to
review, not an automatic cut.

**Prefer raising her floor to raising her ceiling.** This is a working
hypothesis (Fable), not a finding:
- An Opus seat has won on seeds where Sonnet lost, so part of the gap may
  be how hard she is to pilot.
- If so, tuning with multipliers until Sonnet reaches par could leave a
  good human over par.
- So this pass prefers changes that make an ordinary hand work.

## 4. The changes

No card is added, and the pool stays at 78. Each card below was offered on
these seeds in suite 1.

**A. Klee's Secret Base: her Accuracy.**
- The new text: "Your Bombs are placed 3 [4] bigger."
- The rest is unchanged: 1-cost Uncommon Power. It stacks with copies of
  itself.
- **What counts as placing:**
  - Mines are Bombs, so every Mine counts, including Jumpy Dumpty's Mine on
    every enemy.
  - Every card that says "place" counts, as do the Bombs from All of My
    Treasures!, Return to Sender and Aftershock.
  - A merge and a jump do not count.
- **Card faces show the raised number,** as Shivs do under Accuracy. Under
  it, Pop! prints Bomb 8.
- **Loops checked (Fable asked):**
  - Chained Reactions grows Bombs and places none, so the two cannot feed
    each other.
  - Aftershock places at most one Bomb a turn.
- **Why this shape:**
  - It pays at once, including on Mines and on Bombs placed and set off on
    the same turn.
  - It grows with how many Bombs her deck places.
  - Unlike draft 1's growth version, it does not reward waiting.
- **What it does not fix (Fable):** her turn-1 limit is Set off cards, not
  Bomb size. And the Power is rarely in play on turn 1. So it no longer
  predicts a turn-2 change.
- **Prediction:** in fights where it is in play, Bombs and Mines deal about
  4 more damage a turn.

**C. Boom Badge: Retain, and Badges do not stack.**
- The new text keeps "2 Sparks [1], double the next Set off this turn", and
  adds Retain and "Does not stack". Today two Badges give ×4.
- **Prediction:** a run holding it plays it in at least half of its act-2
  and act-3 fights, against 0 plays in suite 1. A play counts as useful if
  it kills an enemy that turn or adds at least 15 damage (GPT: doubling a
  Bomb 9 for a kill now beats waiting for a Bomb 15).

**B. Witch's Homework: tried in round 1, not yet promoted.**
- The new text: "Place a Bomb 6. When it goes off, this card's Bomb is 2
  [3] larger for the rest of the run. Exhaust."
- **Rulings:**
  - It grows at most once a combat, whatever replays it.
  - It counts after a jump, and after a merge (Exquisite Compound).
  - A copy (All of My Treasures!) does not count.
- **Where the reviewers stand:** GPT recommended revising and testing it.
  Draft 3 wrongly listed GPT as for dropping it. Fable backs it.
- **Its cost is real:** 1 Energy for one more Bomb than Pop! gives for 0.
- **Given at embark, it gets its best case.** Success in round 1 qualifies
  it for more testing, not for promotion. Before promotion, one run picks
  it up at the start of act 2.
- **Prediction:** given at embark, it is about 25 by act 3. That is less
  than the 36 it would reach if it went off in every fight.

**D. The tempo relic: a test, not a starter change** (Fable).
- The test text: "At the start of each combat, place a Bomb 6 on a random
  enemy." It goes on a staging-only copy of Pounding Surprise, given at
  embark in one arm of round 1.
- The Bomb is placed before her first turn, so it has grown to 10 when she
  first acts. Turn 1 then holds a real choice: Ka-pow! it now, or cook it.
- Pick 5 stays yours. Round 1 gives it a number.
- **Prediction:** in act-2 and act-3 normal fights, the enemy HP left at
  the start of turn 2 falls from about 0.9 to about 0.8.

**Considered and left out:**
- **A higher Bomb growth rate:** it pays only Bombs that wait, and it is a
  rule change.
- **The Big One at a lower cost:** it was passed once, too little to tell.
- **Alice's Recipe at 1 cost:** it was never offered on these seeds.
- **Ka-pow!'s missing upgrade:** a starter change.
- **Sparks:** you never felt short of them, but seats find Spark-cost cards
  dead at the start of a fight.
  - A hypothesis, not a finding: the Spark economy is not the main cause of
    her losses.
  - Round 1's first-Set off turn and its Spark-card plays will test that.

## 5. How it is graded

**Instruments.** Fatal fights and the player's Strength are logged (#938).
Enemy HP without Block (`enemy_hp_by_turn`) is being added. All three are
deployed with the `klee-next` build.

**Round 1: three arms on two seeds.**
- **The design:** two of the five baseline seeds, three arms each, six
  Sonnet runs. Five lanes run at once, and the sixth when a lane frees.

| Arm | Given at embark | What it reads |
|---|---|---|
| 1 | A, C | the floor fixes alone |
| 2 | A, B, C | B's effect, against arm 1 on the same seed |
| 3 | A, C, the tempo relic | the tempo fix, against arm 1 on the same seed |

- **Comparisons:**
  - Each arm is compared with the other arms on its seed, and with that
    seed's suite-1 run.
  - The arms run as a package. A and C are read across all three arms, not
    in isolation.
- **What is read:**
  - **Acts 2 and 3 only** (Fable). The runs start with extra cards, so
    their act 1 is not comparable.
  - Turn-2 enemy HP left (the new HP-only field).
  - Fight length in turns.
  - Bomb damage a turn.
  - HP lost.
  - Boss-entry HP.
  - Each card's plays.
  - Each Boom Badge play's result.
  - The turn of her first Set off.

**Gate changed after round 1** (ruled 2026-10-05,
`review/records/klee-scaling-round-1-2026-10-05.md` pick 1).
- Suite 2 now waits for a round where, in act-2 and act-3 normal fights,
  Klee's damage a turn and HP lost are within 15% of the base character's
  run on the same seed, on both seeds, and she reaches the act-3 boss on
  both.
- The turn-2 prediction below stays missed.
- Secret Base v3 replaces change A, and the relic stays off the starter.

**Suite 2 waits for a round that moves turn 2** (Fable; superseded above).
- Draft 3's own table predicted a miss of the bar in act 3.
- A suite cost about 12M tokens, and rounds are cheap.
- So rounds repeat until the turn-2 figure moves, and the suite is spent on
  a build expected to pass.
- The suite then runs the same five seeds as suite 1. The promotion suite
  adds two runs on fresh seeds, read against the pooled base five, so the
  kit is not tuned to five maps.

**Read these with care:**
- Two seeds with one run per arm is a small sample. A clear gap between
  arms on both seeds counts. A gap on one seed does not.
- Whether a run reaches act 3 depends on the seed more than on these
  cards.

## Picks

1. **The diagnosis.** Klee's Bomb damage arrives a turn late, limited by
   Set off cards on turn 1, and is flat across the run. No card below Rare
   improves ordinary Bombs. Default: agree.
2. **No flat cuts in this pass.** Default: yes.
3. **The changes.** Default: A ("Your Bombs are placed 3 [4] bigger") and C
   (Retain; Badges do not stack) go to `klee-next`. B (Witch's Homework,
   Bomb 6, run-long growth) is tried in round 1 only.
4. **Strength and Bombs** ("positive Strength adds to a Bomb when it is
   placed"). A rule change, so you would play it. Default: hold until
   round 1's Strength numbers are in.
5. **A Bomb at the start of each fight,** on Pounding Surprise. A starter
   change, so it is yours. Default: test it in round 1 as a staging relic,
   and decide on its number.
6. **Grading.** Default: round 1 as three arms on two seeds, read on acts 2
   and 3. Suite 2 runs only after a round moves the turn-2 figure. Two
   fresh seeds at promotion.
