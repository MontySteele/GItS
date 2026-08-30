# Staged turn `funnel-bench-1-t06`

staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun

You are looking at one turn of a card battle, exactly as the game prints it. Everything you are allowed to know is on this page.

## You

- HP 40/62
- Block 0
- Energy 3
- Spark 2 — A resource. Cards that print a Spark price spend it.

## Your hand

### Dodoco Blast

- Cost: 0
- Spend 2 Sparks. Deal 7 damage to ALL enemies. Applies Pyro.
- (card text read from: bridge)

### Bang Bang!

- Cost: 0
- Spend 2 Sparks. Deal 5 damage to random enemies twice. Applies Pyro.
- (card text read from: bridge)

### Kaboom!

- Cost: 1
- Deal 7 damage. Applies Pyro.
- (card text read from: bridge)

### Duck and Cover

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

## The other side

### Twig Slime (S)

- HP 9/9
- Intent: Aggressive, 4, This enemy intends to Attack for 4 damage.

### Leaf Slime (M)

- HP 32/32
- Intent: Strategic, 2, This enemy intends to give you 2 Status cards.

### Leaf Slime (S)

- HP 15/15
- Intent: Aggressive, 3, This enemy intends to Attack for 3 damage.

## Disclosures

- A decision-closeness falsifier reads this turn with a dominance threshold of 0.5.
- You are not being asked whether this turn is fun.
- The hand is EXACTLY the list below and nothing else. The hand the game dealt is emptied before these cards are given, and a packet whose live hand is not this list is refused rather than written.
- The Spark bank is written to 2 through SPARK_POWER, which is how the live game holds Sparks.
- The encounter is GENERATED. This file can write each enemy's HP and can write only the FIRST enemy's Block, and it cannot write any intent or how many enemies there are -- the packet records whichever encounter and telegraphs the game actually drew.
- Every card is granted unupgraded. An upgrade moves printed numbers, so an upgraded grant is a different board.
- The player has no Strength and no enemy carries an aura, Vulnerable or Weak. Every Klee attack applies Pyro, and a reaction on top of a hit would move every number the falsifier scores.
