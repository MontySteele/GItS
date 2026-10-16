# furina-next paper 3, 2026-10-16: blank Repays and act 1 bleeding

Furina is a Balance kit. These changes go on a fresh `furina-next` (cut from
`main` after the suite 3 promotion, #1369) and reach `main` only through a
promotion PR with a suite 4 record graded against the predictions below.

**Why.** Suite 3 (`review/records/furina-suite-3-2026-10-16.md`), ruled
"Let's promote as-is ... In the meantime we can do a paper round on the
findings." Her mean end floor rose to 42.8 and the act 3 bank is now spent.
Two findings are left.

## 1. What the numbers say

Suites 1 to 3, 15 runs (scratch `furina-gap/p3.py`):

- **She takes about 2.4 times the base five's damage in acts 1 and 2, on
  the same pressure.** Normal fights, per turn: incoming 8.5 against 8.2 in
  act 1 and 12.8 against 12.4 in act 2; fights last the same 3 to 3.6 turns;
  damage taken 4.4 against 1.8 in act 1 and 6.9 against 3.3 in act 2. Her
  HP lost is enemy damage, not her own Drains: in act 1 she takes 12.7
  damage a fight and ends 11.6 HP down. Suite 3's net HP ratios were
  2.00 and 1.30 of base.
- **Some of that is the design.** Fanfare comes from HP lost, and seats say
  so: "banking Fanfare by taking damage (not blocking)" (suite 3, lane 4);
  "knowingly underblocked for Fanfare" (suite 2, lane 1). Her printed Block
  pool is the smallest of any kit (12 cards, 41 Block; wave record
  2026-10-13).
- **Four of five suite 3 NEVER AGAIN cards are Repays with nothing to
  return**: Endless Waltz (two seats), Hymn of Many Waters, Pneuma Refrain.
  A Repay returns only drained HP. In act 1 she is often healthy and has
  drained little, so the card reads "Repays 0". These are not rare cards:
  over the three suites Pneuma Refrain was played 67 times, Hymn 39, Clean
  Slate 27, Endless Waltz 26.

The two problems meet in act 1: the turns where her Repay cards are blank
are the turns she is bleeding.

## 2. The change

**One rule: a Repay that cannot return all its HP gains 1 Block for each HP
it could not return, unless the card says otherwise.** Hymn of Many
Waters and Grand Entrance already print this (the code's `StageFloor.Block`);
the rule makes it every Repay's default. So a healthy Furina's Repay cards are Block cards, and an injured
one's are heals, which is the shape the kit always meant.

- **Keeps its own floor:** Cleansing Torrent, which prints damage for an
  unreturned Repay, keeps the damage instead of Block.
- **"Repay all"** (Singer of Many Waters, Grand Absolution) has no number,
  so it has no floor: all of nothing is nothing.
- **Covered by the rule:** Pneuma Refrain, Clean Slate, Ebb and Flow,
  Fountain of Lucine, Coup de Théâtre's kill Repay, Ousia / Pneuma's Pneuma
  face, Charlotte's and Sigewinne's acts, Salon Solitaire's Repay 1 each
  turn. Their texts lose nothing; the rule is one keyword tip line ("Any
  HP a Repay cannot return becomes Block.").
- **Hymn of Many Waters and Grand Entrance** drop the clause they print,
  since the rule now says it.

| Card | Today | furina-next |
|---|---|---|
| **Pneuma Refrain** (Uncommon Skill, 1) | Repay 5. Draw 2 cards. | Repay 4 [6]. Draw 2 cards. (One less, because it now always pays 4 Block when healthy.) |
| **Endless Waltz** (Uncommon Attack, 1 [0]) | Deal X damage, plus Y for each time you Repaid this turn. | Repay 2. Deal X damage, plus Y for each time you Repaid this turn. (It starts its own count, so it is never a worse Strike.) |

Universal Revelry and Critics' Darling ("whenever you Repay, that much")
keep reading the HP actually returned, not the Block.

## 3. Predictions (written before suite 4)

Same five seeds, one Sonnet seat per lane, on the `furina-next` staging
build.

1. Net HP lost per normal fight in act 1 falls from 2.00 to at most 1.60 of
   base, and act 2 from 1.30 to at most 1.15.
2. No seat names a Repay card as NEVER AGAIN.
3. Block gained a turn in act 1 normal fights rises at least a quarter
   (suites 1 to 3: 3.2).
4. Act 3 damage stays at least 0.85 of base, and at least four of five runs
   reach act 3 (suite 3: 0.95, four).

## Picks

1. **The rule.**
   - **(a) Default:** an unreturned Repay gains Block, as above, with the
     two card rows.
   - (b) An unreturned Repay gains Fanfare instead of Block: never blank,
     but it feeds the bank, not the bleeding.
   - (c) No rule; fix only Pneuma Refrain and Endless Waltz by hand.
2. **Act 1 Block beyond the rule.**
   - **(a) Default:** nothing more; the rule is the Block change, and
     taking hits for Fanfare stays her identity.
   - (b) Also add 2 Block to her three Common Block cards that print the
     least (Velvet Curtain, Stage Directions, Tearful Monologue).
