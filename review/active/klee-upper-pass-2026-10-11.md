# Klee's Uncommons and Rares: an underperformer pass, 2026-10-11

After the Commons pass (`klee-commons-pass-2026-10-11.md`, ruled), [USER] said: "It seems like we hit fertile ground here. Let's also do an audit for the uncommon and rare cards as well."

## The evidence

- **Klee census** (`klee-pool-census.md`, session scratchpad): take and play rates from 61 Klee runs since 2026-10-03. The average card is taken about 25% of the times it is offered.
- **Second census** (`klee-census-2.md`): reactions, Companion cards and statuses, from 975 telemetry fights (796 solo).
- **Prices** use the same yardsticks as the Commons pass:
  - a Spark is worth about 1.2 Energy;
  - Bomb growth is damage a turn or more late, like a Kokomi Plan, so it is priced at about 1.25 times on-turn damage.
- **Co-op-only cards are out of scope:** Hide Here!, Pass the Match, Shrapnel, Knights of Favonius and Sparks for Everyone. They are judged by the paired co-op round, not by solo take rates.

**The one new fact.** In solo, Klee's only source of enemy auras is her Companion cards:
- 217 of the 218 solo fights in which she played no Companion card had no reaction at all.
- Her decks hold about 1 Companion card at the act-1 boss and 2 at the act-2 boss.
- Companion cards are taken 10% of the times they are offered.

So every card that pays off on "if a Bomb triggered an Elemental Reaction" is, in solo, a Companion card in disguise.

## Working: no change

These are taken 40% or more, or played in most fights held:
- **Uncommons:** Big Badda Boom 63%, Klee's Secret Base 55%, Survival Rulebook 54%, Boom-Boom Strike 50%, Mine, All Mine! 47%, Dodoco Tag 44%, Behind Jean's Desk 42%. Also Jumpy Dumpty Mk.III (78% played), Return to Sender, Perfect Timing and Stoke the Fuse.
- **Rares:** Alice's Recipe 86%, Spark Knight 85%, Fireworks Finale 76%, Alice's Detonator 78% (reworked tonight), Favonius Escort, Red Knight, Windblume Fireworks, The Big One, Half a Mountain, Dodoco and Chained Reactions.

Kitchen Alchemy (7%) stays: you judged it "quite good".

## Proposals: priced wrong, by number only

| Card | Today | Taken | Why it's weak | New |
|---|---|---|---|---|
| Cover Your Ears! (U) | 2 Sparks: ALL enemies lose 6 [8] Strength this turn | 20%; 2 records say NEVER AGAIN | 2 Sparks is about 2.4 Energy. Silent's Piercing Wail does this for 1 Energy at Common | 1 Spark |
| Sparkling Burst (U) | 2 Sparks: gain 1 Energy, 1 more if a Bomb went off | 28%, played in 25% of fights held; 3 NEVER AGAIN | It spends about 2.4 Energy to get back 1 or 2 | 1 Spark: gain 1 [2] Energy, 1 more if a Bomb went off |
| Blazing Delight (R) | 2 Energy and 3 Sparks: at the start of your turn, gain 1 Energy and draw 1 | 47%, but played in 26% of fights held | At about 5.6 Energy, it pays back only in a long fight | 2 Energy and 1 [0] Spark |
| Witch's Homework (U) | Largest Bomb grows 8 [11]; draw 1 if it is now 20 or more | 11% | Late damage at less than the on-turn rate. Common Chain Fuse now grows every Bomb 9 | Grows 12 [15] |
| Treasure Map (U) | 1 [0] Energy: put a Set off card from your discard pile into your hand; largest Bomb grows 3 | 17%; 1 NEVER AGAIN | Paying 1 Energy to fetch, usually, a Ka-pow! | Costs 0; upgrade grows 6 |
| Taste Test (U) | 2 Energy: deal damage equal to all your Bombs on the enemy; they don't go off. 2 [1] Confiscated | 7% | Common Simmer now does more for 1 Energy and a Dazed | Deals twice your Bombs on the enemy |
| Flash Point (U) | Set off. Deal 7 [10]. On a reaction: 1 Spark, draw 1 | 13% | Common Sizzle is now 8 [11]; in solo, the reaction branch needs a Companion | Deal 9 [12] |
| Party Poppers (U, Power) | Whenever you play a card that costs Sparks, place a Bomb 5 [6] | 6%, but played in 72% of fights held | Klee's Secret Base places a Bomb 6 every turn, unconditionally, for the same Energy | Bomb 7 [9] |
| Sparks 'n' Splash (R, Power) | 3 Energy: at the start of your turn, your largest Bomb deals its size without going off | 3% of 33 | 3 Energy for a power that needs a Bomb kept in place | Costs 2 |
| All of My Treasures! (R) | 2 Energy (upgrade: Retain): place a Bomb the size of your largest on ALL enemies | 5% | Half a Mountain doubles the largest Bomb for 1 Energy and is taken 31% | Costs 2 [1]; the upgrade lowers the cost instead of adding Retain |

- Each change is about one upgrade's worth, and none changes what the card does.
- **Not proposed:** Look Out! and Klee Can Explain!. Their value is Block, and Klee stays fast and fragile by ruling.

## Proposals that change a card's shape

**Exquisite Compound** (U, 1 Energy) is taken 1% of 88 offers, which is more offers than any other Uncommon.
- Today: "Move all your Bombs onto the enemy as one Bomb. It grows by 5."
- The merge is the defect. Each Bomb that goes off pays a Spark, so merging three Bombs into one throws away two Sparks.
- Proposed: "Move all your Bombs onto the enemy. Each grows by 4 [6]." The card is still about collecting your Bombs for one big hit, and it now scales with how many you have.

**Tag Along** (U) and **Adventure Club** (R) are taken 0% of 36 and 0% of 22.
- Tag Along adds a random Companion card at 1 Energy, the Infernal Blade shape, which is weak in the base game too.
- [USER]: "it would be much better if it let you pick what it generated."
- Proposed:
  - Tag Along: "Choose 1 of 3 Companion cards to add to your hand. It costs 0 this turn."
  - Adventure Club: "Choose 2 of 4. They cost 0 this turn."

## Waits for a Companion pass

These cards pay off on Companion cards or on reactions, which in solo come only from Companion cards:
- **Uncommons:** Come Back and Play! 4%, Little Hexenzirkel 5%, Team Effort 18%, Wait For It... 2%.
- **Rares:** Alice's Introduction Magic 0%, Aftershock 0%, Sparkborne Magic 0%.

A number change can't fix a payoff whose trigger is missing from the deck. The Companion cards were last reviewed long ago. You set the standard for them:
- "I am fine with Common Companions being 'bad' (worse than base game Colorless' since you see them in a brand-new card slot; they should mostly offer off-character elements and effects at a Common-ish energy rate."
- "The Uncommons and Rares should be Colorless-tier (generally a little better than a character's own at the same rarity)."

**The next paper** holds the 86 Companion cards (`proto_mc_*`, `proto_mi_*`, `proto_mf_*`) to that bar, card by card, with these seven payoffs read alongside.

**Also waiting on a round:** the status cards (Finders Keepers 6%, Damage Report 13%). Tonight's change gives Confiscated Exhaust, which cuts their fuel. Read them after the round, not before.

## How it is checked

One whole-run Klee seat round on the five base-five seeds, after the Commons build and this one. Lines:
- the changed cards are taken in at least 20% of offers, pooled;
- no act-1 boss deaths in five;
- act-1 normal fights are no shorter than 10% below base.

## For [USER]

Klee is at Balance, so these are your picks.

1. **The ten number changes in the first table.**
   - **(a) Default:** all ten.
   - (b) Only the three Spark prices: Cover Your Ears!, Sparkling Burst and Blazing Delight.
   - (c) None.
2. **Exquisite Compound.**
   - **(a) Default:** no merge; each Bomb grows 4 [6].
   - (b) Keep the merge and grow by 10 [14].
3. **Tag Along and Adventure Club.**
   - **(a) Default:** choose 1 of 3 (Adventure Club: 2 of 4), same Energy costs.
   - (b) The same choice, and Tag Along costs 0.
   - (c) Random as today, but Tag Along costs 0.
4. **Companions.**
   - **(a) Default:** a Companion pass is the next paper, held to your Common / Colorless-tier bar. The seven Companion and reaction payoffs wait for it.
   - (b) Change the seven payoffs by number now, and run the Companion pass after.

## Ruled 2026-10-11

[USER]: "Agreed on all defaults - looks good!"

- Pick 1 (a): all ten number changes.
- Pick 2 (a): Exquisite Compound drops the merge; each Bomb grows 4 [6].
- Pick 3 (a): Tag Along chooses 1 of 3, and Adventure Club 2 of 4, at today's costs.
- Pick 4 (a): the Companion pass is the next paper.

Built into `klee-next`.
