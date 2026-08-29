# Staged turn `klee-sparks-r1-t07`

staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun

You are looking at one turn of a card battle, exactly as the game prints it. Everything you are allowed to know is on this page.

## You

- HP 42/62
- Block 0
- Energy 3
- Spark 4 — A resource. Cards that print a Spark price spend it.

## Your hand

### Firework Finale

- Cost: 0
- Spend 3 Sparks. Deal 18 damage. Exhaust. Applies Pyro.
- (card text read from: bridge)

### Fwoosh!

- Cost: 0
- Spend 1 Spark. Deal 8 damage. Applies Pyro.
- (card text read from: bridge)

### Powder Pop

- Cost: 0
- Place a Bomb dealing 5 damage. Gain 1 Spark. Burst +5. Elemental Skill.
- (card text read from: bridge)

### Duck and Cover

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

## The other side

### Sludge Spinner

- HP 39/39
- Intent: Aggressive, 8, This enemy intends to Attack for 8 damage.

## Disclosures

- A decision-closeness falsifier reads this turn with a dominance threshold of 0.5.
- You are not being asked whether this turn is fun.
- The hand is EXACTLY the list below and nothing else. The hand the game dealt is emptied before these cards are given, and a packet whose live hand is not this list is refused rather than written.
- The Spark bank is written to 4 through SPARK_POWER, which is how the live game holds Sparks.
- The encounter is GENERATED. This file can write the enemy's HP and Block and cannot write its INTENT -- the packet records whichever telegraph the game actually drew, and the mirrored board below declares a telegraphed ATTACK as the falsifier's input.
- Every card is granted unupgraded. An upgrade moves printed numbers, so an upgraded grant is a different board.
- The player has no Strength and the enemy carries no aura, Vulnerable or Weak. Every Klee attack applies Pyro, and a reaction on top of a hit would move every number the falsifier scores.
