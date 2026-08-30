# Staged turn `klee-sparks-bt2r-t03`

staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun

You are looking at one turn of a card battle, exactly as the game prints it. Everything you are allowed to know is on this page.

## You

- HP 24/62
- Block 0
- Energy 3
- Spark 3 — A resource. Cards that print a Spark price spend it.
- Relic — Pounding Surprise: Whenever a Bomb detonates, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- Relic — Stone Humidifier: Whenever you Rest at a Rest Site, raise your Max HP by 5.

## Before you decide

Answer these BEFORE you choose a line, and write the answers into your form's `forecast` list in this order. They are predictions, not questions about what you did:

1. If you spend 3 Sparks on Bag of Tricks this turn, what number will your Spark bank show at the very END of this turn?
2. What will your Spark bank show at the START of your next turn, on the line you are about to play?
3. How much damage, if any, will the enemy have taken by the start of your next turn, on the line you are about to play?

## Your hand

### Bag of Tricks

- Cost: 0
- Choose one: Place 1 Bomb dealing 5 | Spend 3 Sparks: place 3 Bombs dealing 5.
- (card text read from: bridge)

### Mine Toss

- Cost: 1
- Place a Bomb on EACH enemy dealing 5 damage. Burst +5. Elemental Skill.
- (card text read from: bridge)

### Duck and Cover

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

### Spirited Away

- Cost: 2
- Gain 12 Block.
- (card text read from: bridge)

### Run Away!

- Cost: 0
- Gain 4 Block.
- (card text read from: bridge)

## The other side

### Shrinker Beetle

- HP 40/40
- Intent: Strategic, This enemy intends to apply a Debuff to you.

## Disclosures

- A decision-closeness falsifier reads this turn with a dominance threshold of 0.5.
- You are not being asked whether this turn is fun.
- The hand is EXACTLY the list below and nothing else. The hand the game dealt is emptied before these cards are given, and a packet whose live hand is not this list is refused rather than written.
- The Spark bank is written to 3 through SPARK_POWER, which is how the live game holds Sparks. 3 is the mode's printed price exactly.
- The run carries Klee's starting relic and no other. It is printed on the page: that relic pays 1 Spark for every Bomb that detonates, and a reader who cannot see it cannot do the turn's arithmetic.
- The encounter is GENERATED. This file can write the enemy's HP and Block and cannot write its INTENT -- the packet records whichever telegraph the game actually drew, and the mirrored board below declares a telegraphed ATTACK as the falsifier's input.
- Every card is granted unupgraded. An upgrade moves printed numbers, so an upgraded grant is a different board.
- No Bomb is on the board when the turn starts. Every Bomb the packet shows is one this turn's line places.
- The player has no Strength and the enemy carries no aura, Vulnerable or Weak. Every Klee attack applies Pyro, and a reaction on top of a hit would move every number the falsifier scores.
- The turn is ended after the graded line and the board is read once more, so the reading that follows is taken after the enemy has taken its telegraphed turn.
