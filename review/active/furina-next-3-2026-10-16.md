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
- **Four of five suite 3 NEVER AGAIN cards are Repay cards**: Endless
  Waltz (two seats), Hymn of Many Waters, Pneuma Refrain. A Repay returns
  only drained HP, so with nothing drained the face reads "Repays 0". They
  are not all blank, though (corrected after GPT's review):
  - **Hymn of Many Waters** already gives 9 Block with nothing drained (6
    printed, 3 from its fallback). Its complaint is the preview, which
    leads with "Repays 0" and not the Block.
  - **Pneuma Refrain** still draws 2; its Repay part is what goes blank.
  - **Endless Waltz** is truly blank: its bonus counts only Repays that
    returned HP.
  - Charlotte, Sigewinne and Grand Entrance already turn an unreturned
    Repay into Block, like Hymn.

  These cards are played a lot: over the three suites Pneuma Refrain 67
  times, Hymn 39, Clean Slate 27, Endless Waltz 26.

So there are two problems in act 1: she takes more damage than her Block can
cover, and the Repay cards undersell or lose their value when nothing is
drained.

## 2. The change

**One rule: a Repay that cannot return all its HP gains 1 Block for each HP
it could not return, unless the card says otherwise.** Hymn of Many
Waters and Grand Entrance already print this (the code's `StageFloor.Block`);
the rule makes it every Repay's default. With nothing drained a Repay card
is a Block card; with drained HP it returns that HP first. (It reads off
drained HP, not her HP: at 30 HP with nothing drained she gets Block, not
healing.)

- **Keeps its own floor:** Cleansing Torrent, which prints damage for an
  unreturned Repay, keeps the damage instead of Block.
- **"Repay all"** (Singer of Many Waters, Grand Absolution) has no number,
  so it has no floor: all of nothing is nothing.
- **Newly covered:** Pneuma Refrain, Clean Slate, Ebb and Flow, Fountain of
  Lucine, Coup de Théâtre's kill Repay, Ousia / Pneuma's Pneuma face,
  Endless Waltz, and **Salon Solitaire, her starter relic**: its "Repay 1"
  each turn end now gives 1 Block when nothing is drained. That is a small
  baseline gain on every run, named here so it is not missed.
- **Already covered, applied once:** Hymn of Many Waters, Grand Entrance,
  Charlotte and Sigewinne keep the Block they give today; the rule never
  adds a second floor. Hymn and Grand Entrance drop the clause they print.
- **Fontaine Teardrop** (relic) prints exactly this rule today ("Whenever
  you Repay more than you have drained, gain the rest as Block"), so it
  would go blank. It becomes: "An unreturned Repay gains 2 Block for each
  HP instead of 1." (pick 1).
- **No Vigor floor is left on a card.** The code's Vigor floor names two
  cards that no longer exist; nothing changes there.
- **The preview leads with the Block.** A Repay with nothing to return
  reads "Repay 0: gain 3 Block", not "Repays 0" (GPT's point: some of the
  complaint is how the cards say what they do).
- The rule is one keyword tip line: "Any HP a Repay cannot return becomes
  Block." 

| Card | Today | furina-next |
|---|---|---|
| **Pneuma Refrain** (Uncommon Skill, 1) | Repay 5. Draw 2 cards. | Repay 4 [6]. Draw 2 cards. (One less, because it now always pays 4 Block when healthy.) |
| **Endless Waltz** (Uncommon Attack, 1; upgrade adds to Y) | Deal X damage, plus Y for each time you Repaid this turn. | Repay 2. Deal X damage, plus Y for each time you Repaid this turn. |

Endless Waltz keeps today's counting: only a Repay that returned HP counts.
So its own Repay 2 counts only when there is drained HP to return. With
nothing earlier this turn: nothing drained, 6 damage and 2 Block; 1
drained, 9 damage, 1 HP back and 1 Block; 2 or more, 9 damage and 2 HP
back. Its guaranteed gain is the 2 Block; the bonus stays a reward for
Draining first. (The first draft said it "starts its own count"; GPT
showed it does not when nothing is drained.)

Universal Revelry and Critics' Darling ("whenever you Repay, that much")
keep reading the HP actually returned, not the Block.

## 3. Predictions (written before suite 4)

Same five seeds, one Sonnet seat per lane, on the `furina-next` staging
build.

1. Net HP lost per normal fight in act 1 falls from 2.00 to at most 1.60 of
   base, and act 2 from 1.30 to at most 1.15.
2. Damage taken a turn in act 1 normal fights falls from 4.4 to at most
   3.5, and the record names the Block the Repay floor gave (per act, and
   two concrete turns).
3. Block gained a turn in act 1 normal fights rises at least a quarter
   (suites 1 to 3: 3.2).

A seat still calling a Repay card situational is not by itself a miss.
4. Act 3 damage stays at least 0.85 of base, and at least four of five runs
   reach act 3 (suite 3: 0.95, four).

## Picks

1. **The rule.**
   - **(a) Default:** an unreturned Repay gains Block, as above, with the
     two card rows, the Fontaine Teardrop change and the Block-first
     preview.
   - (b) An unreturned Repay gains Fanfare instead of Block: never blank,
     but it feeds the bank, not the bleeding.
   - (c) No rule; fix only Pneuma Refrain and Endless Waltz by hand.
2. **Act 1 Block beyond the rule.**
   - **(a) Default:** nothing more; the rule is the Block change, and
     taking hits for Fanfare stays her identity.
   - (b) Also add 2 Block to her three Common Block cards that print the
     least (Velvet Curtain, Stage Directions, Tearful Monologue).
