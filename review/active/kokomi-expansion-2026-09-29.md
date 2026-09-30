# Kokomi expansion, batch one: four decks

Paper, 2026-09-29. Main session design. **All four picks RULED 2026-09-29,
[USER]: "The defaults work here".** Built in both engines (2026-09-29), with the §5 sim run on the built rows; readings and results in `docs/notes/prototype-surface-provenance.md`, "expansion batch one". The kit's rules
are in `review/active/kokomi-brief-2026-09-01.md` §2; this paper adds cards
only and changes no rule.

## 1. Why

[USER], on the feed-pass build: "My initial reaction to the new Kokomi
version is that I like it! ... I think that this needs a little thought to
make sure actually have multiple archetypes and playstyles represented in the
deck". On the four-deck plan: "Overall this makes sense. I worry a bit about
'defense becomes a deck' leading to unkillable block-only strategies, but
Ironclad already has a version that's fine... I think it's because of the
general difficulty of assembling the whole package in one run."

The pool today is 48 cards (20 Common / 23 Uncommon / 5 Rare). Read against
the four decks:

- **Plan volume with the Casket** is a real deck: five 0-cost feeders, Feint,
  Sango Isshin, Tideturn, the queue tools and seven Casket readers.
- **The Big Plan** exists only as parts (Opening Gambit, Second Wave, Surging
  Shoal, Ambush, Nereid's Ascension). Nothing rewards a short queue, and the
  Casket counts Plans, so many cheap Plans beat a few big ones.
- **Tide Control** has about ten Weak or Vulnerable sources and three payoffs
  (Undertow, Riptide, The Clouds Like Waves Rippling).
- **Dusk Guard** is a role, not a deck: Block cards and nothing that pays off
  holding Block.

## 2. The shape of the batch

The base five each offer 20 Common, 38 Uncommon, 27 Rare (`game_ref/<char>.json`).
Her Commons are already at 20, so the batch is Uncommon and Rare only: **12
Uncommon and 10 Rare, 22 cards; with one Rare replaced (pick 3), the pool
goes to 69 (20 / 35 / 14).** The
remaining Rares, toward the 78 target, wait for a round of play on this batch.

The Big Plan gets its own axis instead of a count: its cards read **the
Energy paid for the Plans waiting**, which the 0-cost feeders never add to.
The Casket keeps counting Plans; one Rare (Grand Design) lets a big Plan feed
it too, so the relic is not the volume deck's alone.

Every damaging card of hers applies Hydro (brief §4); the faces below leave
that implicit, as the sheet does. Each two-half card keeps the halves rule:
the now-line answers this turn, the Plan buys what a head start buys.

## 3. The cards

**The Big Plan (4 Uncommon, 4 Rare)**
- **Weight of the Plan** (Attack, 1, U): Deal 5 [7] damage, plus 3 for each
  Energy paid for the Plans waiting.
- **Lull** (Skill, 1, U): Gain 7 [10] Block. Plan: If it is the only Plan
  carried out this morning, gain 2 Energy.
- **Undertide Lance** (Attack, 2, U): Deal 8 [11] damage to ALL enemies.
  Plan: Deal 16 [20] damage, doubled if no other Plan is carried out this
  morning.
- **Measured Breath** (Skill, 1, U): Gain 6 [9] Block. If no Plan is
  waiting, draw 2.
- **Grand Design** (Power, 1, R): Whenever the Bake-Kurage carries out a Plan
  that cost 2 or more, the Casket gains 2 more.
- **The Long Game** (Power, 1 [0], R): At the start of your turn, if exactly
  one Plan is waiting, gain 1 Energy.
- **Masterstroke** (Attack, 3, R): Retain. Play on the Bake-Kurage. Plan:
  Deal 30 [40] damage.
- **All Streams Flow to the Sea** (Skill, 2, R; her C5): Exhaust. Cancel all
  your Plans; their cards go to your discard pile. Your next Plan this turn
  is carried out once, plus once for each Plan cancelled.

**Tide Control (4 Uncommon, 3 Rare)**
- **Drowning Pressure** (Attack, 1, U): Deal 4 [6] damage for each debuff on
  the enemy.
- **Salt in the Wound** (Skill, 0, U): Apply 1 Vulnerable. If the enemy has
  Weak, draw 1 [2].
- **Undercurrent Snare** (Skill, 1, U): Apply 2 Weak. Plan: Apply 1 [2]
  Vulnerable to ALL enemies.
- **Tidal Resonance** (Skill, 1, U): Apply Hydro to ALL enemies. Draw 1 for
  each enemy that already had an element. The setup card for a Pyro, Electro
  or Cryo companion.
- **At Water's Edge** (Power, 2 [1], R; her C1): Whenever a reaction happens
  on an enemy, apply 1 Weak and 1 Vulnerable to it.
- **Ceremonial Garment** (Power, 2, R): Your Attacks deal 1 [2] more damage
  for each debuff on their target.
- **Suffocating Deep** (Attack, 2, R): Deal 6 [9] damage to ALL enemies.
  Double each enemy's Weak and Vulnerable. Exhaust.

**Dusk Guard (3 Uncommon, 2 Rare)**
- **Coral Crash** (Attack, 1, U): Deal damage equal to your Block. (Body
  Slam, at Uncommon where Ironclad has it at Common.)
- **Evening Watch** (Skill, 1, U): Draw 1. Dusk Plan: Gain 5 [7] Block for
  each enemy intending to attack.
- **Brace for the Tide** (Skill, 1, U): Exhaust. Dusk Plan: Double your
  Block.
- **Watatsumi's Grace** (Power, 2, R): At the end of your turn, keep up to
  10 [15] of your Block. **Replaces The Clouds Like Waves Rippling**, the
  defensive Power the Block census asked for; the old card leaves the pool.
- **Tidal Riposte** (Power, 1, R): Whenever an enemy's attack is fully
  Blocked, deal 5 [7] damage to it.

**Plan volume (1 Uncommon, 1 Rare)**
- **Shoal Call** (Skill, 1, U): Add 2 Nips to your hand. [They are
  upgraded.]
- **Kurage Swarm** (Power, 2 [1], R): Whenever you write a Plan that costs 0,
  the Casket gains 1.


## 4. Keeping Dusk Guard killable

[USER]'s worry is the Barricade loop: keep every point of Block and add more
each turn until nothing gets through. Four guards, in the cards above:

1. **Retention is capped.** Watatsumi's Grace keeps 10 [15], not all of it.
   Above the cap, Block still resets, so a wall cannot grow without end.
2. **The multiplier is spent.** Brace for the Tide doubles once and Exhausts.
3. **The pieces sit at Rare and Uncommon,** where drafts rarely meet them
   together: the retention Power and the Block-to-damage Power are both Rare.
   That is the assembly difficulty [USER] named for Ironclad.
4. **The deck's win condition is damage from Block** (Coral Crash, Tidal
   Riposte), so it has to keep attacking; there is no card that wins by
   stalling.

The sim reads it: in fights where Grace and Coral Crash are both held, count
turns with more than 30 Block carried and the fight length, against the
other three decks.

## 5. What the sim must show before the build

1. Each deck, drafted with a focused pilot, reaches act-won within 10 points
   of Plan volume.
2. The Big Plan's cost reading: 0-cost feeders never scale Weight of the Plan
   (by construction), and a Big Plan deck beats a volume deck with the same
   relic when Grand Design is held.
3. Dusk Guard: §4's check; no fight routinely past turn 15 on Block alone.
4. No new card is dominant or dead (pick and play rates, as for Varka).

## Picks

1. **The batch: 22 cards, 12 Uncommon and 10 Rare, as above.** Default: yes,
   with the remaining Rares after a round of play.
2. **The Big Plan reads Energy paid, not Plan count.** Default: yes.
3. **Watatsumi's Grace replaces The Clouds Like Waves Rippling.** Default:
   yes (the Block census, 2026-09-29, found no defensive Power in her pool
   that saves a turn).
4. **Dusk Guard's four guards (§4).** Default: all four.
