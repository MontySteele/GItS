# Varka: the Grand Master's Oath (paper kit)

**Stage: Paper** (rewritten 2026-09-29 for the Oath rework). Numbers are
placeholders for the sim; a number in brackets is the upgrade. The first
design (Absorb, four stacking Winds, Knights' Muster), its sims and the batch
one prototype are history: `git show 2fb06ed2:review/active/varka-paper-kit-2026-09-28.md`,
and the seat round that read it is `review/records/varka-round-1-2026-09-29.md`.
The Oath sims are draft PR #768.

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
- On play: "Oath cards are strong, but you need to think carefully before
  spreading your deckbuilding thin without a Switch card."

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
- **His current element** is the element of the last Knight he played (or a
  card that says it changes it). The seat page and his status bar show it
  with its Oath. Before his first Knight he has none.
- **Oath, one count per element** (Pyro, Hydro, Electro, Cryo), **counted per
  card, not per enemy**. A card that applies an element gains 1 Oath of it,
  however many enemies it hits, including an application that reacts
  instead of leaving an aura. A card that Swirls gains 1 Oath of each element
  it Swirls, whoever laid the aura. Four Winds' Ascension's own elemental hit
  gains none. A count only goes up, unless a card says otherwise, and all
  four reset at the end of the fight. (The sim's first model counted per
  enemy and let Ascension feed itself; Ascension then ran past 100 in pack
  fights.)
- **Cards read only the current element's Oath.** Oath banked in the other
  elements waits until he switches back. Running two elements is allowed;
  juggling them is the cost, and the Switch cards (sec.7) are what pay for it.
- **A Swirl he makes pays his current element**, one effect:
  - **Pyro:** 3 damage to the enemy Swirled.
  - **Hydro:** gain 3 Block.
  - **Cryo:** 1 Vulnerable on the enemy Swirled.
  - **Electro:** to be chosen by the sim, [USER]: "Either aoe electro, or draw
    power, seems fine - we can sim both." E-AoE: 3 damage to ALL enemies.
    E-Draw: draw 1 card.

  [USER], on the first draft's Weak and Energy: "Electro's energy cheating is
  way too good"; "I'm not convinced Varka needs a basic source of Weak".

## 4. Boreas's Fang and Four Winds' Ascension

- **Boreas's Fang** (starting relic): "The first time each combat you gain
  Oath, add Four Winds' Ascension to your hand." Regent's Forge is the model:
  it "adds Sovereign Blade to their hand if they haven't forged this combat."
- **Four Winds' Ascension** (Attack, 1; created, never in the deck): "Deal 6
  Anemo damage. Then deal 3 damage for each Oath of your current element, as
  that element." Played, it goes to the discard pile and comes back when he
  draws it. The Anemo hit Swirls a fresh aura first (1 Oath, as any Swirl);
  the elemental hit then refreshes the aura or reacts with a spent one, and
  gains no Oath. Playing it now keeps it circulating; holding it waits for a
  bigger count.
- **The upgraded Fang** (every kit's starter relic upgrade) creates it
  upgraded: 9 Anemo, 4 per Oath.

## 5. The starter (80 HP, 99 gold)

Strike x4, Defend x4 (base game), and:
- **One starting Knight, at random each run**, from four starter-only cards,
  each "Gain 8 [11] Block. Apply its element to an enemy." ([USER]: "Starter
  cards can be a little better than that. Let's bump it to 8 (11) block +
  painting an element.") Named for Genshin Bursts and passives, so none
  clashes with a pool Knight or a Mondstadt companion:
  **Amber: Fiery Rain** (Pyro), **Barbara: Melody Loop** (Hydro), **Lisa:
  Lightning Rose** (Electro), **Kaeya: Glacial Waltz** (Cryo).
- **Windbound Execution** (Attack, 1): Deal 4 [6] Anemo to ALL enemies. His
  Genshin Skill; the starter's Swirl card.

**Why equal Block.** The sim traced every starting gap to Block: with Barbara
alone giving 7, Hydro won 50% of act-1 runs and the others 7 to 16%; with
her Block removed, all four sat within 10 points; with 5 on each, three of
four sat within 9 (Electro trailed, hence its payout test). Varka is short
enough of defence that Block on the starter decides the start.

## 6. The pool (41 cards: 16 / 17 / 8)

Knights are Varka's personal-pool companions, all Skills unless marked;
playing one sets his current element. Every element has at least two pool
Knights, so a focused deck can be drafted. **New** marks batch two.

**Common (16)**
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
- **New. Razor: Claw and Thunder** (Knight, 1): Deal 7 [10] Electro.
- **New. Mika: Starfrost Swirl** (Knight, 1): Apply Cryo to an enemy. Gain
  6 [9] Block.
- **New. Jean: Dandelion Breeze** (Skill, 1): Gain 7 [10] Block. Swirl one
  enemy's fresh aura (no damage). His Block that still charges.
- **New. Knightly Guard** (Skill, 1): Gain 8 [11] Block. If you played a
  Knight this turn, gain 1 Oath of your current element.
- **New. Oathsworn Strike** (Attack, 1): Deal 6 [9] damage, plus 1 for each
  Oath of your current element. The Common reader.
- **New. Crosswind** (Attack, 1): Deal 7 [10] Anemo. If it Swirls, gain 4 [6]
  Block.
- **New. Rising Gale** (Attack, 0): Deal 4 [6] Anemo. If it Swirls, draw 1.

**Uncommon (17)**
- **Tempest Charge** (Attack, 1): Deal 8 [11] Anemo. If it Swirls, draw 1.
- **Favonius Cut** (Attack, 2): Deal 14 [19] Anemo.
- **Grand Master's Order** (Skill, 0): The next Knight you play this turn is
  played twice. Exhaust. [Retain.]
- **Knights' Roll Call** (Skill, 1): Add a random Knight to your hand. It
  costs 0 this turn. [Choose the Knight.]
- **Tailwind Stride** (Skill, 1): Draw 2. If you have a current element, draw
  1 more. [Cost 0.]
- **Eye of the Storm** (Skill, 1): Gain 2 [3] Block for each Oath of your
  current element. **Exhaust** ([USER]: "A simple fix for scaling Block with
  Hydro Oath is to give that card exhaust").
- **Stormward Stance** (Power, 1 [0]): While your current element has 4 or
  more Oath, your Anemo Attacks deal 3 more.
- **Oath of the Knights** (Power, 1): At the start of your turn, gain Block
  equal to your current element's Oath.
- **Rally to the Banner** (Skill, 1): Move all your Oath to your current
  element. Exhaust.
- **New. Diluc: Searing Onslaught** (Knight, Attack, 2): Deal 6 [8] Pyro
  twice.
- **New. Eula: Icetide Vortex** (Knight, 2): Deal 10 [14] Cryo. Gain 1 Oath of
  Cryo for each enemy with a Cryo aura.
- **New. Barbara: Whisper of Water** (Knight, 1): Apply Hydro to an enemy.
  Gain 4 [6] Block now and 4 [6] next turn.
- **New. Favonian Standard** (Power, 1): Whenever you play a Knight of your
  current element, gain 3 [4] Block. Focus's defence.
- **New. Change of Guard** (Skill, 1): Choose an element you have Oath in; it
  becomes your current element. Gain Block equal to its Oath. Exhaust. A
  switch without a Knight, paid in Block.
- **New. Storm Surge** (Attack, 2): Deal 5 [7] Anemo to ALL enemies. Each
  enemy it Swirls takes 5 more.
- **New. Tailwind Guard** (Skill, 1): Gain 3 [4] Block for each element you
  have Oath in. The juggler's Block.
- **New. Unfurled Banner** (Skill, 1): Put Four Winds' Ascension from your
  discard pile into your hand. It costs 0 this turn. Exhaust.

**Rare (8)**
- **Converging Winds** (Power, 2 [1]): Your Swirls react where they land (the
  spread hit is the flat 2 carrying the Swirled element; a reaction it sets
  off lands on that enemy only; a reaction from a spread never Swirls again).
- **Boreas Unbound** (Power, 2 [1]): Whenever your current element changes,
  gain 1 Energy. The sim's only card that makes a mid-fight switch pay.
- **Wall of Gales** (Skill, 2): Gain 16 [22] Block. Swirl every fresh aura.
- **Four Winds' Accord** (Skill, 1): Split your total Oath evenly among the
  four elements, rounding down, then gain 1 of each. Exhaust.
- **Sworn Brotherhood** (Power, 2 [1]): At the start of your turn, gain 1 Oath
  of every element.
- **New. Northwind Avatar** (Attack, 3): Deal 12 [16] Anemo, then 12 [16] of
  your current element, plus 2 for each of its Oath. His Burst.
- **New. Dawn Wind's March** (Power, 2 [1]): Whenever you gain Oath of your
  current element, gain 2 Block. Focus's defensive engine.
- **New. Azure Devour** (Attack, 2): Deal 4 damage for each Oath of your
  current element. Exhaust. The Focus finisher.

The Mondstadt universal Sturm und Drang already supports many Swirls. Pool
target 78 comes after the prototype.

## 7. The archetypes

1. **Focus.** One element all fight: stack its Oath and let Ascension and the
   readers grow (Oathsworn Strike, Eye of the Storm, Oath of the Knights,
   Stormward Stance, Favonian Standard, Dawn Wind's March, Azure Devour).
   Strong, and thin: the wrong element for the fight stays wrong.
2. **Switch.** The element you open each fight with is the ordinary choice;
   a mid-fight switch is the costly juggle, and the Switch cards pay for it:
   Boreas Unbound (Energy), Change of Guard (Block), Tailwind Guard (Block for
   breadth), Rally to the Banner, Four Winds' Accord and Sworn Brotherhood
   (Oath). [USER]: "you need to think carefully before spreading your
   deckbuilding thin without a Switch card."
3. **Gale.** Many Swirls: Gale Sweep, Storm Surge, Crosswind, Rising Gale,
   Tempest Charge, Wall of Gales, Converging Winds. Oath grows fastest here,
   in whatever elements the board offers.

Grand Master's Order and Knights' Roll Call are support cards, not an
archetype ([USER] agreed 2026-09-29); the name waits for a distinct turn.

**In co-op** a partner's auras are Swirl fuel. Swirling them gains Oath of
their element but does not change his current element.

## 8. Intended weakness

- **Nothing to Swirl, nothing to charge.** Enemies carry no auras of their own
  yet, so his Oath comes from his Knights and his partner.
- **Focus is only as safe as its readers.** A focused deck with Oath of the
  Knights or Favonian Standard turns its count into Block; one without them
  has only its starter Knight and Wind Wall.
- **Before the first Oath** Ascension is not in hand.

## 9. What it costs to build

C#: the four Oath counts and the current element (one power), the created
Ascension and the Fang's grant, the random starter Knight at run start (four
starter-only cards, kept out of the pool by the starter-overlap lint), the
payouts, Absorb and the Winds removed, 41 cards re-aimed or new, and the seat
page (current element, the four counts). The sim model is draft PR #768.

## 10. What the sim has shown

Draft PR #768, stylised act 1, n = 400 per cell; read the gaps, not the
levels. Raw output: the PR body, sec.8.

Round one (per-enemy Oath, then R3b): per-card Oath keeps Ascension in
check; the starter gap is Block; a focused reader pays about 1.7 times a
juggling one; without Boreas Unbound a mid-fight switch never pays.

Round two (this paper: 41 cards, 8 [11] starter Knights, both Electro
payouts):

1. **Electro: E-AoE wins.** Act won, drafted, focused pilot: Pyro 26.5,
   Hydro 48.8, Electro 37.0 with E-AoE (22.2 with E-Draw), Cryo 41.2. On the
   starter deck alone Cryo leads (39.8) and the gap runs the other way, so
   the drafted gap comes from the pool.
2. **The starts are not within 10 points, and the pool's Block Knights
   explain the order.** Pool Knights that give Block: Hydro two (Let the
   Show Begin, Whisper of Water), Cryo one (Starfrost Swirl), Electro none,
   Pyro none. The act-won order is the same, and Pyro also has the only
   single-target payout. Pick 2 below.
3. **Switching is right sometimes, as intended.** With Boreas Unbound,
   switching and switching back beats staying in 55% of paired states for
   Pyro to Hydro before a 12+ hit, and 66% for Pyro to Electro against 3+
   enemies. Tailwind Guard alone brings the Hydro switch-back to break-even.
   Change of Guard helps more as a Block card that pays out the current
   Oath than as a switch. A Cryo switch never pays.
4. **Ascension's curve holds.** Casts past 60 by turn 8 in 0 to 2 of about
   3,000 drafted fights per start; mean cast at turns 7 to 8 is 25 to 29
   focused. The outliers were Hydro decks carrying Whisper of Water, Favonius
   Drill and Oath of the Knights, and juggling decks with Rally and Sworn
   Brotherhood.
5. **Readers against Defend (5 Block for 1).** Eye of the Storm 8.8 per play;
   Oath of the Knights 29 Block a fight; Favonian Standard 7.7 a fight (about
   1.5 Defends for a Power); Dawn Wind's March 14.3 a fight for 2 Energy.
   Standard and March are the weak two.
6. **Juggling is weak everywhere** (2 to 9% act won against 26 to 49%). The
   sim pilot's draft weights for the juggler are crude, so this is a floor,
   but [USER]'s intent ("think carefully before spreading your deckbuilding
   thin without a Switch card") wants juggling to cost, not to lose.
7. **Low play rates among the 18 new cards:** Unfurled Banner 0.45 plays per
   fight held and Azure Devour 0.36 (both Exhaust, so at most 1, and the
   pilot holds them), Northwind Avatar 0.56 (3 Energy). No new card looks
   dominant.

## Picks

1. **Electro's payout: E-AoE (3 damage to ALL).** Default, from sec.10 item 1.
   E-Draw put Electro 26.6 points behind Hydro.
2. **Even the starts through the pool's Knights, without making them
   same-y. RULED 2026-09-29, [USER]: "Good on both Varka defaults" (Lisa and
   Baron Bunny as below; re-sim pending).** [USER]: "I don't want all of this feeling too same-y. What is
   Lisa's card becomes some other scaling block mechanic, like 'gain 4 block
   per attack played this turn'". Default:
   - **Lisa: Violet Arc** (Knight, 1): "Apply Electro to an enemy. Gain 3 [4]
     Block for each Attack you played this turn." Lisa's Conductive stacks
     build per hit; it rewards playing her last in an Attack-heavy turn,
     which is the Electro pack deck. 3 rather than 4 so two Attacks (6 [8])
     sits near a Defend+ and three (9 [12]) is the payoff; the sim settles it.
   - **Amber: Baron Bunny** (Knight, 1): "Gain 6 [8] Block. Next turn, deal
     6 [8] Pyro to ALL enemies." The decoy takes the hits, then goes up. Not
     Barbara's "apply to ALL, gain Block" twice over: Block now, AoE Pyro
     later, which also covers Pyro's single-target Swirl payout.
   Then re-sim; if Pyro still trails by more than 10, its Swirl payout
   becomes 3 damage to every enemy that Swirl touched.
3. **Lift the two weak Focus readers.** Default: Favonian Standard 3 [4] to
   4 [5] Block; Dawn Wind's March 2 to 3 Block per Oath gain.
4. **Northwind Avatar** at 3 Energy is rarely played. Default: cost 2, damage
   10 [14] and 10 [14], plus 2 per Oath.
