# Klee's scaling pass

Paper, 2026-10-05, main session. Picks open. [USER]: "Yes, agreed - let's
look at Klee's scaling."

Suite 1 (`review/records/klee-suite-1-2026-10-05.md`) showed that Klee falls
behind the base characters as the run goes on. This paper explains why, and
proposes three card changes for `klee-next`. Each change comes with a
prediction, and suite 2 grades the predictions on the same five seeds. Under
the freeze, nothing here touches `main`'s cards (the measurement paper, sec.6).

## 1. What falls behind: Klee's Bombs

Klee's damage a turn on the paired seeds, split into Bombs and Mines going
off, and everything else. All fights are counted, from the suite-1
telemetry:

| Act | Bombs + Mines | Everything else | Klee total | Base five total |
|---|---|---|---|---|
| 1 | 11.4 | 12.3 | 23.7 | 23.0 |
| 2 | 14.3 | 20.7 | 35.1 | 39.6 |
| 3 | 14.5 | 22.7 | 37.2 | 52.7 |
| Growth, act 1 to act 3 | ×1.27 | ×1.85 | ×1.57 | ×2.29 |

**Klee's cards scale nearly as well as a base character. Her Bombs barely
scale at all.** Bomb damage is half her act-1 damage, so the whole kit is
held back. Big Badda Boom grows (20.9, 34.8 and 36.9 a play), but only
because it copies Bomb damage.

For comparison, each base character's main damage source grows over the
run, on these same seeds (`tools/telemetry_report.py`, damage a play in act 1
and act 3):

| Card | Act 1 | Act 3 |
|---|---|---|
| Ironclad Strike | 7.4 | 21.5 |
| Ironclad Whirlwind | 40.4 | 56.9 |
| Silent Shiv | 5.6 | 11.1 |
| Defect Strike | 5.9 | 11.2 |
| Necrobinder The Scythe | 27.6 | 67.8 |

## 2. Why the Bombs stay flat

1. **Nothing raises how fast Bombs grow, except at Rare.**
   - A Bomb grows 4 at the start of each of her turns
     (`KleeOverhaulLaw.BombGrowth`), from the first fight to the last.
   - Each base character has 1-cost Uncommon Powers that raise its damage
     for the rest of the fight (`game_ref/*.json`):
     - Ironclad: Inflame.
     - Silent: Accuracy and Noxious Fumes.
     - Defect: Storm, Thunder and Hailstorm.
     - Necrobinder: Friendship and Haunt.
     - Regent: Furnace, which grows Sovereign Blade.
   - Klee has eight Uncommon Powers, and none raises Bomb damage without
     a condition:
     - Experiment in Progress pays only on turns she sets nothing off.
     - Klee's Secret Base pays only when no enemy has a Bomb. A seat put it
       on the NEVER AGAIN list.
     - Little Hexenzirkel, Party Poppers and Finders Keepers place a small
       Bomb when something else happens.
   - Her only steady growth Power is Alice's Recipe, a 2-cost Rare.
     Act-3 fights are barely longer than act-1 fights (median 3.5 turns
     against 3), so her Bombs end those fights only a little bigger.
2. **Her other growth cards each work once, and only when combined with other cards.**
   - Boom Badge, Half a Mountain, The Big One and Witch's Homework each
     grow or multiply a Bomb once. They pay only when a big Bomb and a Set
     off card are on hand that same turn.
   - The seats passed on them:
     - Witch's Homework three times out of three (lane 2, act 1).
     - The Big One, Half a Mountain and Sparks 'n' Splash once each.
   - Two seats took Boom Badge and never played it: "it never lined up in
     hand" (lane 1), and "it was in the discard whenever the Sparks were"
     (lane 2).
3. **Nothing carries over between fights.**
   - Base cards that grow for the rest of the run do exist. On these seeds,
     The Scythe's damage a play rises 2.5 times by act 3 (above).
   - Defect's Genetic Algorithm does the same for Block.
   - Klee has no card like that.

A fourth cause is left alone in this pass. Klee's Strength does not add to
her Bombs (`EB-343`, R248). So base-game Strength from relics, potions and
Bennett skips her biggest damage source. Changing that would change a rule,
which means you play it. It is pick 4, for after suite 2.

## 3. What does not change: her flat numbers

Your first read was "scaling being low and flat numbers being high enough to
somewhat balance it out". The paired seeds back the first half of that, but
not the second. In act 1, Klee deals 1.03 times a base character's damage
and loses 1.31 times its HP. Two of the five runs died at the act-1 boss. So
her act-1 numbers are not high. They are level, and her act-1 defence is
already behind.

Cutting flat damage now would turn two act-1 boss deaths into more. This
pass only adds scaling. A trim comes later, and only if suite 2 shows act-1
damage above 1.15 times the base characters'.

## 4. The three changes

Each change goes on a card the seats skipped or disliked, so no card is
added and the pool stays at 78. Each card was offered on these seeds in
suite 1, so suite 2 will see it again.

**A. Klee's Secret Base: her Inflame.**
- The new text: "Your Bombs grow 2 [3] more at the start of your turn."
- The rest is unchanged: 1-cost Uncommon Power.
- How it stacks:
  - It stacks with copies of itself.
  - Under Alice's Recipe, each of her two growths includes it (6, twice).
- Why this card: it is the card a seat put on the NEVER AGAIN list. Seats
  took or bought it twice on these seeds (lane 1, act 2; lane 3, act 1).
- How it compares with Inflame. Inflame's +2 lands on every hit, at once.
  This card's +2 lands on every Bomb, every turn, and builds up until the
  Bomb goes off. A Bomb held two turns comes out 4 bigger, so two Bombs
  held two turns come out 8 bigger.
- **Prediction:** in runs that play it, Bombs and Mines deal about 4 more
  damage a turn from act 2 on.

**B. Witch's Homework: the card that grows over the run.**
- The new text: "Place a Bomb 4. Exhaust. When this Bomb goes off, this
  card's Bomb grows 2 [3] for the rest of the run."
- The rest is unchanged: 1-cost Uncommon Skill.
- It grows only when its own Bomb goes off. A Bomb removed, or one that
  jumps, does not count. So the card rewards cashing in, not holding.
- It follows Genetic Algorithm: Exhaust caps it at one growth a fight.
- Why this card: seats passed it three times out of three. As it stands it
  is "your largest Bomb grows by 8", a one-time growth.
- **Prediction:** when it is taken in act 1, its Bomb is placed at about 30
  by act 3. On top of that come the 4 a turn every Bomb grows.

**C. Boom Badge: Retain.**
- The new text keeps everything (2 Sparks [1], double the next Set off this
  turn) and adds Retain.
- The badge can then wait in hand for the big Bomb. The combination drops
  from three cards on one turn to two.
- **Prediction:** a run holding it plays it in at least half of its act-2
  and act-3 fights. In suite 1 it was played 0 times.

**Considered and left out:**
- The Big One at a lower cost: it was passed once, which is too little to
  tell.
- Alice's Recipe at 1 cost: it was never offered on these seeds.
- A higher Bomb growth for everyone: this raises Bomb damage evenly in
  every act, while the gap is in acts 2 and 3. It is also a rule change.
- Ka-pow!, the only Set off card she starts with, has no upgrade. A change
  to it is a starter change, so it is yours to make. This pass does not ask
  for one.

## 5. How suite 2 grades it

Suite 2 uses the same five seeds, the same seats (one Sonnet seat per act,
at A0) and the same report. Klee's suite-1 figures are the starting line.

| Measure | Suite 1 | Predicted |
|---|---|---|
| Bombs + Mines damage a turn, act 1 / 2 / 3 | 11.4 / 14.3 / 14.5 | about 11.5 / 16 / 19 |
| Damage a turn against the base five, act 2 / 3 | 0.91 / 0.72 | about 1.0 / 0.85 |
| HP lost against the base five, act 3 | 1.81 | about 1.5 |
| Runs reaching act 3 | 2 of 5 | 3 of 5 |

**Read these with care:**
- Five runs is a small sample. Act 3 had only 8 normal fights in suite 1.
- Runs reaching act 3 is the noisiest line. A seat can win or lose a run on
  one bad turn.
- Act 1 should not move. Scaling cards rarely matter before the first boss,
  and the two act-1 boss deaths (lanes 3 and 4) are helped only if one of
  these cards comes early.
- If act 3 reaches 0.85 but not the bar (within 15%), that already shows
  the direction is right. The next pass would then take up pick 4 or a
  second Uncommon.

The changes are built on `klee-next` and deployed with
`tools/deploy_round.py --staging` as a `+next` build. They reach `main` in one
promotion PR that carries the suite-2 record.

## Picks

1. **The diagnosis.** Klee lacks a Bomb scaling source below Rare, so her
   Bombs stay flat while her cards grow. Default: agree.
2. **No flat cuts in this pass.** A trim waits for suite 2, and happens only
   if act-1 damage goes above 1.15 times the base characters'. Default: yes.
3. **The three changes** (A to C in sec.4), built on `klee-next` and graded
   by suite 2. Default: all three. You can also take some and drop the
   rest.
4. **Strength adds to Bomb growth** (each point of Strength makes Bombs grow
   1 more a turn), as an option for the pass after suite 2. It is a rule
   change, so you would play it. Default: hold, and decide after suite 2.
