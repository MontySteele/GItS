# Varka: the Grand Master's Oath (paper kit)

**Stage: Paper** (rewritten 2026-09-29 for the Oath rework). Numbers are
placeholders for the sim; a number in brackets is the upgrade. The first
design (Absorb, four stacking Winds, Knights' Muster), its sims and the batch
one prototype are history: `git show 2fb06ed2:review/active/varka-paper-kit-2026-09-28.md`,
and the seat round that read it is `review/records/varka-round-1-2026-09-29.md`.

## 1. Why the rework

Round one found the old kit's choice real only after the first Wind, and
Varka the only one of nine characters with no defence beyond Defend (the
defence census of 2026-09-29, starters and starting relics included).
Talking it through, [USER] set a new direction instead of a Block patch:

- "I am envisioning that Varka only gets the benefits of one element at a
  time, not all four."
- "He should charge up his ascension by applying and swirling elements, and
  he can switch elements based on who he's drafted to meet the needs of each
  fight."
- "Muster sounds too useful for this concept, honestly... elements should be
  something you draft into."
- On Ascension: "add Four Winds' Ascension to his hand the first time he gets
  an Oath (treat it like Regent's Sword - it lives outside the deck)".
- On Oath: "Cards that read his Oath count can be quite strong but leave him
  with a deficit in other areas. The count should be going up, not down, over
  time, unless a card specifically does otherwise."

**The Genshin source** (KQM's quick guide): in his Skill state one claymore
hits Anemo and the other a teammate's element, **one element at a time**;
Four Winds' Ascension is a recharging special; each Swirl in the party gives
a stack of **Azure Fang's Oath** that powers it.

## 2. The promise

The Grand Master fights beside whichever Knights he has. He takes their
element as his own, one at a time, and every aura he lays down or Swirls
swears more of that element to his blade.

## 3. The rules

- **Swirl** is the shared rule: an Anemo hit on a fresh aura leaves it on
  that enemy, spent; spreads spent copies to every enemy lacking it; deals a
  flat 2 to every enemy. A spent aura still reacts with a new element.
- **His current element** is the element of the last Knight he played. The
  seat page and his status bar show it with its Oath. Before his first Knight
  he has none.
- **Oath, one count per element** (Pyro, Hydro, Electro, Cryo). He gains 1
  Oath of an element each time he applies it to an enemy and each time he
  Swirls an aura of it, whoever laid the aura. A count only goes up, unless
  a card says otherwise, and all four reset at the end of the fight.
- **Cards read only the current element's Oath.** Oath banked in the other
  elements waits until he switches back. Running two elements is allowed;
  juggling them is the cost.
- **A Swirl he makes pays his current element**, one effect:
  - **Pyro:** 3 damage to the enemy Swirled.
  - **Hydro:** gain 3 Block.
  - **Cryo:** 1 Vulnerable on the enemy Swirled.
  - **Electro:** 2 damage to ALL enemies.

  [USER], on the first draft's Weak and Energy: "Electro's energy cheating is
  way too good"; "I'm not convinced Varka needs a basic source of Weak".

## 4. Boreas's Fang and Four Winds' Ascension

- **Boreas's Fang** (starting relic): "The first time each combat you gain
  Oath, add Four Winds' Ascension to your hand." Regent's Forge is the model:
  it "adds Sovereign Blade to their hand if they haven't forged this combat."
- **Four Winds' Ascension** (Attack, 1; created, never in the deck): "Deal 6
  Anemo damage. Then deal 3 damage for each Oath of your current element, as
  that element." Played, it goes to the discard pile and comes back when he
  draws it. The Anemo hit Swirls a fresh aura first; the elemental hit then
  applies the current element (1 more Oath) or reacts with a spent aura.
- **The upgraded Fang** (every kit's starter relic upgrade) creates it
  upgraded: 9 Anemo, 4 per Oath.

## 5. The starter (80 HP, 99 gold)

Strike x4, Defend x4 (base game), and:
- **One starting Knight, at random each run**, from four starter-only cards.
  Like Survivor or Bodyguard, each is better than a Common and shows what its
  element does for him. Named for their Genshin Bursts, so none clashes with
  the pool Knights (named for Skills):
  - **Amber: Fiery Rain** (Skill, 1): Deal 9 [12] Pyro.
  - **Barbara: Shining Miracle** (Skill, 1): Apply Hydro to ALL enemies. Gain
    7 [10] Block.
  - **Lisa: Lightning Rose** (Skill, 1): Deal 6 [8] Electro. Draw 2.
  - **Kaeya: Glacial Waltz** (Skill, 1): Deal 6 [8] Cryo. Apply 1 [2]
    Vulnerable.
- **Windbound Execution** (Attack, 1): Deal 4 [6] Anemo to ALL enemies. His
  Genshin Skill; the starter's Swirl card.

**Turn one, worked (Barbara start, two slimes).** Shining Miracle paints both
Hydro (Hydro Oath 2; the Fang adds Ascension) and gives 7 Block. Windbound
Execution Swirls both (Hydro Oath 4; two Hydro payouts, 13 Block in all). The
third energy plays Ascension: 6 Anemo, which finds only spent auras, plus 12
Hydro, which refreshes the aura (Hydro Oath 5). That is strong for turn one;
the sim checks it first.

## 6. The pool (23 cards: 9 / 9 / 5)

Knights are Varka's personal-pool companions, all Skills; playing one sets his
current element.

**Common (9)**
- **Squall** (Attack, 1): Deal 4 [5] Anemo twice.
- **Updraft** (Attack, 1): Deal 8 [11] Anemo.
- **Gale Sweep** (Attack, 1): Deal 3 [5] Anemo to every enemy that has a fresh
  aura.
- **Wind Wall** (Skill, 1): Gain 7 [10] Block. If you have a current element,
  gain 3 more.
- **Favonius Drill** (Skill, 1): Gain 6 [9] Block. Apply your current element
  to an enemy.
- **Amber: Baron Bunny** (Knight, 1): Deal 6 [9] Pyro.
- **Barbara: Let the Show Begin** (Knight, 1): Apply Hydro to ALL enemies.
  Gain 3 [5] Block.
- **Lisa: Violet Arc** (Knight, 1): Deal 5 [7] Electro. Draw 1.
- **Kaeya: Frostgnaw** (Knight, 1): Deal 6 [9] Cryo.

**Uncommon (9)**
- **Tempest Charge** (Attack, 1): Deal 8 [11] Anemo. If it Swirls, draw 1.
- **Favonius Cut** (Attack, 2): Deal 14 [19] Anemo.
- **Grand Master's Order** (Skill, 0): The next Knight you play this turn is
  played twice. Exhaust. [Retain.]
- **Knights' Roll Call** (Skill, 1): Add a random Knight to your hand. It
  costs 0 this turn. [Choose the Knight.]
- **Tailwind Stride** (Skill, 1): Draw 2. If you have a current element, draw
  1 more. [Cost 0.]
- **Eye of the Storm** (Skill, 1): Gain 2 [3] Block for each Oath of your
  current element.
- **Stormward Stance** (Power, 1 [0]): While your current element has 4 or
  more Oath, your Anemo Attacks deal 3 more.
- **Oath of the Knights** (Power, 1): At the start of your turn, gain Block
  equal to your current element's Oath.
- **Rally to the Banner** (Skill, 1): Move all your Oath to your current
  element. Exhaust.

**Rare (5)**
- **Converging Winds** (Power, 2 [1]): Your Swirls react where they land (the
  spread hit is the flat 2 carrying the Swirled element; a reaction it sets
  off lands on that enemy only; a reaction from a spread never Swirls again).
- **Boreas Unbound** (Power, 2 [1]): Whenever your current element changes,
  gain 1 Energy.
- **Wall of Gales** (Skill, 2): Gain 16 [22] Block. Swirl every fresh aura.
- **Four Winds' Accord** (Skill, 1): Split your total Oath evenly among the
  four elements, rounding down, then gain 1 of each. Exhaust.
- **Sworn Brotherhood** (Power, 2 [1]): At the start of your turn, gain 1 Oath
  of every element.

The Mondstadt universal Sturm und Drang already supports many Swirls. Pool
target 78 comes after the prototype.

## 7. The archetypes

1. **Focus.** One element all fight: stack its Oath, let Ascension and the
   readers (Eye of the Storm, Oath of the Knights, Stormward Stance) grow. Rally
   to the Banner rescues a fight that forced a switch. Weakness: the wrong
   element for the fight stays wrong.
2. **Switch.** Change element to the fight's need: Hydro for a big hitter,
   Cryo's Vulnerable for a burst turn, Electro against a crowd. Boreas Unbound
   pays for each switch; Four Winds' Accord and Sworn Brotherhood keep every
   count alive. Weakness: every reader is smaller.
3. **Gale.** Many Swirls on many auras: Gale Sweep, Wall of Gales, Tempest
   Charge, Converging Winds. Oath grows fastest here, in whatever elements the
   board offers.
4. **Grand Master** (provisional): Knight repeats and Knight generation; kept
   only if it shows a distinct turn (pick 2).

**In co-op** a partner's auras are Swirl fuel. Swirling them gains Oath of
their element but does not change his current element, so a Klee partner
feeds Pyro Oath whether or not he is on Pyro.

## 8. Intended weakness

- **Nothing to Swirl, nothing to charge.** Enemies carry no auras of their own
  yet, so his Oath comes from his Knights and his partner. A draw without a
  Knight is a plain Anemo turn.
- **The wrong element.** A Focus deck whose element does not answer the fight
  (Pyro against a big hitter) has no Hydro Block to fall back on.
- **Before the first Oath** Ascension is not in hand.

## 9. What it costs to build

C#: the four Oath counts and the current element (one power), the created
Ascension and the Fang's grant, the random starter Knight at run start (and
its four starter-only cards, kept out of the pool by the starter-overlap
lint), payouts rewritten, Absorb and the Winds removed, 23 cards re-aimed or
new, and the seat page (current element, the four counts). The sim model
comes first (sec.10).

## 10. What the sim must show before a prototype

1. **Ascension's curve.** Oath per turn, and Ascension's damage per cast on
   turns 1 to 12, by starting Knight, focused and juggling. Flag any deck
   where Ascension alone passes 60 per cast by turn 8. Check the turn-one
   burst above.
2. **The starting Knights are even.** Win rate and act-1 HP loss by starting
   Knight; no element more than ten points behind the others.
3. **Readers pay for focus.** Eye of the Storm and Oath of the Knights against
   Defend, focused and juggling.
4. **Defence.** Act-1 elite HP loss against run 3 of round one, the best
   batch-one run.

## Picks

1. **What gains Oath.** (1) *Applying an element and Swirling an aura of it,
   1 each* [default]. (2) Swirling only (closer to Genshin; slower, and a
   Knight charges nothing by itself).
2. **Grand Master.** (1) *Provisional fourth archetype, kept only if it shows
   a distinct turn* [default]. (2) Drop it now; a later archetype can come
   from his Hexerei homework instead.
