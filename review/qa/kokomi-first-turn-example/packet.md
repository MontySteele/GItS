# Staged turn `kokomi-first-turn-example`

staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun

You are looking at one turn of a card battle, exactly as the game prints it. Everything you are allowed to know is on this page.

## You

- HP 62/70
- Block 0
- Energy 3
- Charge: 8

## Your hand

### Coral Guard

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

### Tactical Retreat

- Cost: 0
- Draw 1 card. Discard 1 random card.
- (card text read from: bridge)

### Water's Edge

- Cost: 1
- Deal 6 damage. Applies Hydro.
- (card text read from: bridge)

### Gorou — Inuzaka All-Round Defense

- Cost: 0
- Deal 6 damage. Exhaust.
- (card text read from: bridge)

### Coral Guard

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

### Pearl Barrage

- Cost: 1
- Exhaust 1 card from your hand. Deal 5 damage. Scales with the total cost of the cards you just Exhausted. Applies Hydro.
- (card text read from: bridge)

### Coral Guard

- Cost: 1
- Gain 5 Block.
- (card text read from: bridge)

### Bake-Kurage

- Cost: 1
- Summon Bake-Kurage for 1 turn. Gain 1 Charge. Burst +5. Elemental Skill.
- (card text read from: bridge)

### All Streams Flow to the Sea

- Cost: 1
- Deal 9 damage. Scales with Charge. Applies Hydro.
- (card text read from: bridge)

### Gorou — General's War Banner

- Cost: 1
- Gain 4 Block. Your next Attack deals 3 more damage.
- (card text read from: bridge)

## The other side

### Shrinker Beetle

- HP 32/40
- Intent: Strategic, This enemy intends to apply a Debuff to you.

## Disclosures

- A decision-closeness falsifier reads this turn with a dominance threshold of 0.5.
- You are not being asked whether this turn is fun.
- THE GAME DEALS ITS OWN OPENING HAND ON TOP OF THIS ONE, and the first live run of this file is what proved it: five granted cards arrive beside the five Kokomi drew, so the staged hand is TEN. There is no dev door that empties a hand, so the divergence is recorded rather than fixed. The packet is a picture of the live ten; `closeness --observed` scores the live ten; the declared board below is the five-card reading available with no game running, and it is the smaller question.
- The encounter is GENERATED. This file writes the first living enemy's HP and Block, and it cannot write its INTENT -- the packet records whichever telegraph the game actually drew, and the mirrored board below declares a single-hit attack as the falsifier's input. If the live intent differs, the closeness reading is a reading of the DECLARED board and the packet is a picture of the LIVE one; they are two records, not one.
- Every card is granted unupgraded. Upgrades move Pearl Barrage's base and Coral Guard's Block, so an upgraded grant is a different board.
- Charge is written to 8 through the registered resource. All Streams Flow reads it at one point per two Charge, so the bank is what makes that card a live choice rather than a small attack.
- The player has no Strength and the enemy no Vulnerable or aura. A reaction on top of a hit would change every number the falsifier scores.
