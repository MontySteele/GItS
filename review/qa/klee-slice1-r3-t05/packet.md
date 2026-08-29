# Staged turn `klee-slice1-r3-t05`

staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun

You are looking at one turn of a card battle, exactly as the game prints it. Everything you are allowed to know is on this page.

## You

- HP 42/62
- Block 0
- Energy 2
- Burst: 20
- Spark 3 — At 3 Sparks, your Attacks cost 0. Playing one consumes 3 Sparks.

## Your hand

Spark, and the costs below. Spark's own text reads: "At 3 Sparks, your Attacks cost 0. Playing one consumes 3 Sparks." Your bank is 3. 2 cards in your hand are shown at a cost LOWER than the cost printed on the card; each of them says so on its own line. Playing one of them at the shown cost consumes 3, so a bank of 3 covers 1 of the 2; anything after that costs what its card prints.

### Imaginary Friend

- Cost: 1
- Gain 5 Block. Gain 3 Burst Energy. Burst +5. Elemental Skill.
- (card text read from: bridge)

### Kaboom!

- Cost: 0
- The cost printed on this card is 1; it is showing 0 here.
- Deal 7 damage. Applies Pyro.
- (card text read from: bridge)

### Rapid Fire

- Cost: 0
- The cost printed on this card is 2; it is showing 0 here.
- Deal 4 damage to random enemies four times. Applies Pyro.
- (card text read from: bridge)

### Duck and Cover

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

## The other side

### Nibbit

- HP 43/43
- Intent: Aggressive, 12, This enemy intends to Attack for 12 damage.

## Disclosures

- A decision-closeness falsifier reads this turn with a dominance threshold of 0.5.
- You are not being asked whether this turn is fun.
- The hand is EXACTLY the list below and nothing else. The hand the game dealt is emptied before these cards are given, and a packet whose live hand is not this list is refused rather than written.
- The encounter is GENERATED. This file can write the enemy's HP and Block and cannot write its INTENT -- the packet records whichever telegraph the game actually drew, and the mirrored board below declares a telegraphed ATTACK as the falsifier's input. If the live intent differs, the closeness reading is a reading of the DECLARED board and the packet is a picture of the LIVE one; they are two records, not one.
- Every card is granted unupgraded. An upgrade moves printed numbers, so an upgraded grant is a different board.
- The Spark bank is written to 3 through SPARK_POWER, which is how the live game holds Sparks. At 3 Sparks the next Attack played costs 0 and consumes all 3.
- The player has no Strength and the enemy carries no aura, Vulnerable or Weak. Every Klee attack applies Pyro, and a reaction on top of a hit would move every number the falsifier scores.
- The Burst meter is written to 20 of 40 through the registered resource. Where a card's face prints a Burst rider, that printed rider IS the whole of what playing the card adds to the meter on top of the card's own text -- nothing further is added behind it.
