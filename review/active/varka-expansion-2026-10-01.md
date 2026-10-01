# Varka expansion: his own relics, and the pool to 78

Paper, 2026-10-01, revised the same day. Main session design. **All four picks
RULED 2026-10-01 at their defaults, [USER]: "Agreed on all four. You're good to
proceed."** The kit's rules
are in `review/active/varka-paper-kit-2026-09-28.md` §3; this paper adds
cards, relics and potions, re-aims five Knights, and changes no rule.

## 1. Why

[USER], after the co-op run: "I feel like my exact build (use the card that
summons random Knights to mix and match elements + power-stacking) might be
run-specific, so I'm curious how it feels at a full-density card pool." And
on 2026-10-01: "I think it's time we look at the relics and expansion so any
future changes are based on realistic deckbuilding."

Today the pool is 41 cards (15 / 18 / 8); every kit's target is 78. His
relic pool is the Silent's six plus Boreas's Fang (#776); none of the six
serves him.

What the two seat rounds and your run said the pool lacks
(`review/records/varka-open-oath-round-2026-10-01.md`,
`varka-oath-round-2026-09-29.md`):

- **Turns with no aura source have no decision** (both seats, most fights'
  first turn).
- **Block runs thin into act 2** (both rounds).
- **Rares are 8**, so build-arounds rarely appear.

**The revision.** [USER] on the first draft: "I do also wonder if we're
making too many Knight cards ... whether we've printed too many Knight Block
cards and not enough diversity to make these feel separate, as opposed to
making each element stand out such that a mono-element deck is a viable
goal." The count agreed: 7 of 13 pool Knights were "apply an element, gain
Block", and nothing read one element by name, so mono-Pyro and mono-Cryo
played the same. This version gives each element a role, matching its Swirl
payout, and a payoff of its own, and cuts the Knights deck from eleven cards
to six. Then: "I think it's fine to allow for each element to have one core
defensive card as long as they are meaningfully different, and have 4
flavors of starter that are 'element + block' since you only get one of them
anyway ... We should do a pass over the Knights and make sure they're all
independently 'interesting' while also opening up viable identities for
each element." The Knight table in §3 is that pass.

## 2. The shape

**37 cards: 5 Common, 17 Uncommon, 15 Rare, for a pool of 78 (20 / 35 /
23).** The base five are 20 / 35 / 25 each (co-op cards excluded,
`game_ref/<char>.json`), so 23 Rares sits just under them.

**The four elements each have a job**, the one its Swirl already pays:

| Element | Swirl pays | Its Knights | Its defensive Knight | Element payoffs |
|---|---|---|---|---|
| Pyro | damage | hit, and reward re-applying Pyro | Baron Bunny: Block now, fire next turn | Blazing Charge (U), Wildfire Oath (R) |
| Hydro | Block | block and cleanse | Whisper of Water: Block now and next turn | Tidal Bulwark (U), Unbroken Tide (R) |
| Cryo | Vulnerable | debuff | Mika: Weak, defence by control | Glacial Edict (U), Absolute Zero (R) |
| Electro | AoE | AoE and draw | Infinite Circuit: Block for each Attack played | Static Field (U), Thundering Verdict (R) |

Each element keeps exactly one defensive Knight, and the four defend in four
different ways. The four starter-only Knights stay "element plus 8 Block":
a run has one of them, so they never sit side by side.

The element payoffs read their own element's Oath by name, at a better rate
than the generic readers, which read the current element. A mono-element
deck takes its element's two payoffs, its three Knights and the generic
Focus readers; a Switch or Gale deck takes the generic cards.

**The decks across the 78** (a card can serve two, so these overlap):

| Deck | About | Reads |
|---|---|---|
| One element (x4) | 5 each, plus the Focus readers | that element's Oath |
| Focus (generic) | 16 | the current element's Oath |
| Gale | 15 | Swirls |
| Switch | 11 | changing element |
| Muster | 6 | Knights played |
| Generic | 6 | |

Block now lives in Hydro, in one defensive Knight per element, in Noelle (a
Geo Knight, below) and in a handful of generic cards, not in every Knight.

## 3. The cards

**The Knight pass: all thirteen pool Knights** (ids and art unchanged; new
ones marked). Each one asks a different question of the turn.

| Knight | Element, rarity | Text | Its question |
|---|---|---|---|
| Amber: Baron Bunny | Pyro, C | 6 [8] Block. Next turn, deal 6 [8] Pyro damage to ALL enemies. (unchanged) | Block now or damage now? |
| Amber: Sharpshooter (new) | Pyro, C | Deal 8 [11] Pyro damage. If the enemy already has Pyro, deal it again. | Lay Pyro first, then shoot |
| Diluc: Searing Onslaught | Pyro, U | Deal 6 [8] Pyro damage twice. If either hit sets off a reaction, gain 1 Energy. | Feed him another element first |
| Barbara: Gleeful Songs | Hydro, C | Apply Hydro to ALL enemies. Gain 5 [7] Block. (Block was 3) | Set up a Gale turn |
| Barbara: Whisper of Water | Hydro, U | Apply Hydro. 4 [6] Block now and 4 [6] next turn. (unchanged) | Plan a turn ahead |
| Barbara: Wellspring Hymn (new) | Hydro, U | Remove your Weak, Frail and Vulnerable. Gain 7 [10] Block. Apply Hydro to an enemy. | When are the debuffs worth a card? |
| Kaeya: Heart of the Abyss | Cryo, C | Deal 6 [9] Cryo damage. Apply 1 Vulnerable. (was damage only) | Open for the finisher |
| Mika: Suppressive Barrage | Cryo, C | Apply Cryo and 2 [3] Weak to an enemy. (was Cryo and 6 Block) | Which enemy hits hardest? |
| Eula: Icetide Vortex | Cryo, U | 10 [14] Cryo damage; 1 Cryo Oath per Cryo enemy. (unchanged) | Spread Cryo first |
| Lisa: Infinite Circuit | Electro, C | Apply Electro. 4 [5] Block, plus 3 [4] per Attack played this turn. (unchanged) | Play it last |
| Razor: Awakening | Electro, C | Deal 4 [6] Electro damage to ALL enemies. Enemies that already have Electro take 3 more. (was 7 to one) | Lay Electro first |
| Lisa: Pulsating Witch (new) | Electro, U | Apply Electro to ALL enemies. Draw 1 card for each enemy. [Retain] | Better in a crowd |
| Noelle: Steadfast Maid (new) | Geo, U | Gain 9 [12] Block. Draw 1 card. | The Knight that keeps your element |

**Common (5)**

| Card | Cost, type | Text | Deck |
|---|---|---|---|
| Pathfinder's Mark | 0 Skill | Apply your current element to an enemy (a random one of the four if you have none). [ALL enemies] | All |
| Cavalry Charge | 1 Attack | Deal 7 [10] damage as your current element. | Focus |
| West Wind Shield | 1 Skill | Gain 5 [7] Block, plus 2 for each enemy with an aura. | Gale; Block |
| Knightly Strike | 1 Attack | Deal 7 [10] damage. If you played a Knight this turn, deal 4 more. | Muster |
| Amber: Sharpshooter | 1 Attack, Pyro Knight | Deal 8 [11] Pyro damage. If the enemy already has Pyro, deal it again. | Pyro |

**Uncommon (17)**

| Card | Cost, type | Text | Deck |
|---|---|---|---|
| Blazing Charge | 1 Attack | Deal 5 [7] Pyro damage, plus 2 for each Pyro Oath. | Pyro |
| Tidal Bulwark | 1 Skill | Apply Hydro to an enemy. Gain 4 [6] Block, plus 2 for each Hydro Oath. | Hydro |
| Glacial Edict | 1 Skill | Apply Cryo to an enemy, and 1 Weak and 1 Vulnerable, plus 1 of each for every 4 [3] Cryo Oath. | Cryo |
| Static Field | 1 Power | The first time each turn you apply Electro, draw 2 [3] cards. | Electro |
| Barbara: Wellspring Hymn | 1 Skill, Hydro Knight | Remove your Weak, Frail and Vulnerable. Gain 7 [10] Block. Apply Hydro to an enemy. | Hydro |
| Lisa: Pulsating Witch | 1 Skill, Electro Knight | Apply Electro to ALL enemies. Draw 1 card for each enemy. [Retain] | Electro |
| Noelle: Steadfast Maid | 1 Skill, Geo Knight | Gain 9 [12] Block. Draw 1 card. | Muster; Block |
| Vow of the Blade | 1 Skill | Gain 1 Oath of your current element. Draw 1 [2] card(s). | Focus |
| Unwavering Banner | 1 Power | Only Knights and cards that name it can change your current element. [Innate] | Focus |
| Shifting Gale | 1 Attack | Deal 6 [8] damage. If your current element changed this turn, deal it twice. | Switch |
| Cycle of Seasons | 1 Power | Whenever your current element changes, deal 4 [6] damage to ALL enemies. | Switch |
| Four Banners | 2 Attack | Deal 5 [6] damage for each element you have Oath in. | Switch |
| Eye Wall | 1 Skill | Gain 6 [8] Block. Whenever you Swirl this turn, gain 3 Block. | Gale; Block |
| Pressure Front | 1 Skill | Apply your current element to ALL enemies. [Retain] | Gale |
| Crosscurrent | 1 Skill | Swirl an enemy's fresh aura. This Swirl pays twice. [Draw 1] | Gale |
| Assembly at the Cathedral | 1 Power | Whenever you play a Knight, deal 3 [4] damage to a random enemy. | Muster |
| Dawn Patrol | 0 Skill | Gain 1 Energy. Draw 1 card. Exhaust. [Draw 2] | All |

**Noelle** is Geo, which is not an Oath element (§3 of the kit paper): she
counts as a Knight for Muster, Grand Master's Order and Knightly Guard, but
gains no Oath and does not change his element (and so is never "a Knight of
your current element" for Favonian Standard). She is
the one Knight a focused deck can play without leaving its element, and the
one plain Block Knight.

**Rare (15)**

| Card | Cost, type | Text | Deck |
|---|---|---|---|
| Wildfire Oath | 2 Power | While your current element is Pyro, your Swirls' damage hits ALL enemies, plus 1 for each Pyro Oath. [Innate] | Pyro |
| Unbroken Tide | 3 [2] Power | While your current element is Hydro, your Block is not removed at the start of your turn. | Hydro |
| Absolute Zero | 2 Power | While your current element is Cryo, your Swirls apply Vulnerable and Weak to ALL enemies. [Innate] | Cryo |
| Thundering Verdict | 2 Attack | Deal 8 [11] Electro damage to ALL enemies, plus 2 for each Electro Oath. | Electro |
| Oath Unto Death | 3 Power | Whenever you gain Oath of your current element, gain 1 more. [Innate] | Focus |
| Grand Master's Verdict | 3 Attack | Deal 15 [20] damage. Double your current element's Oath. Exhaust. | Focus |
| Wolfpack | 1 Power | Whenever you play Four Winds' Ascension, add a copy of it to your discard pile. [Innate] | Focus (Ascension) |
| Oathbound Aegis | 2 Power | At the end of your turn, gain Block equal to your total Oath, up to 15 [20]. | Focus/Switch; Block |
| Weathervane | 2 Power | At the start of your turn, you may choose an element you have Oath in; it becomes your current element. [Innate] | Switch |
| Tempest of the Four Winds | 2 Attack | Deal 4 [5] damage four times, as Pyro, Hydro, Cryo and Electro. | Switch |
| Twin Gales | 1 Power | Your Swirls pay both your current element and the element Swirled. [Innate] | Gale/Switch |
| Downburst | 2 Attack | Deal 12 [16] damage. If it Swirls, the copies it spreads arrive fresh. | Gale (pick 3) |
| Eye of Stormterror | 2 Power | The first 3 times you Swirl each turn, draw 1 card. [Innate] | Gale |
| Charge of the Knights | 2 Attack | Deal 5 [6] damage for each Knight you played this combat. | Muster |
| The Order Answers | 2 [1] Power | At the start of your turn, add a random Knight to your hand. | Muster |

**Muster is six cards**: Knights' Roll Call, Grand Master's Order, Knightly
Strike, Assembly at the Cathedral, Charge of the Knights and The Order
Answers. It needs no Knights of its own beyond the twelve elemental ones and
Noelle, and because each element's Knights now do different things, a
random Knight is a real roll rather than another Block card.

Notes:

- **Pathfinder's Mark** is a 0-cost Oath. That is deliberate: it is the
  turn-one decision the seats asked for. It is the card to watch.
- **Unwavering Banner** protects a one-element deck from the open Oath: a
  Mondstadt companion's Pyro no longer drags him off Cryo.
- **The element payoffs read their element by name**, so Blazing Charge in a
  Cryo deck reads 0. That is the price of the better rate.
- **Random Knights** (The Order Answers, the shop relic) come from his pool
  Knights, Noelle included, the starter-only four excluded.
- **Power costs** follow the cost sweep: Powers sit at 1, 2 and 3; two
  upgrades lower a cost.

## 4. His relics and potions

The base characters' shape (census in
`review/active/relics-potions-klee-furina-2026-09-27.md`): Starter, Common, 2
Uncommon, 3 Rare, Shop, plus 3 potions. The Ancient (Wolf's Gravestone) is
built (#779).

| Tier | Name | Effect (draft) | Serves |
|---|---|---|---|
| Common | Knight's Commission | At the start of each combat, your starting Knight's element becomes your current element, with 1 Oath. | All (his core number) |
| Uncommon | Windblume Garland | Whenever your current element changes, gain 4 Block. | Switch; Block |
| Uncommon | Dandelion Seeds | At the start of your turn, if no enemy has an aura, apply your current element to a random enemy. | No-aura turns |
| Rare | Banner of the West Wind | When your current element changes, the old element's Oath moves to the new one. | Switch (bends §3; pick 4) |
| Rare | Stormterror's Scale | Your Swirls pay twice. | Gale |
| Rare | Andrius's Howl | Four Winds' Ascension returns to your hand at the start of your turn after you play it. | Ascension |
| Shop | Favonius Duty Roster | At the start of each combat, add a random Knight to your hand. It costs 0 this turn. | Muster (the Ninja Scroll slot) |

| Tier | Potion | Effect (draft) |
|---|---|---|
| Common | Bottled Resolve | Choose an element. It becomes your current element; gain 3 Oath of it. |
| Uncommon | Bottled Gale | Swirl every fresh aura. |
| Rare | Elixir of the Four Winds | This turn, your cards read your total Oath across all four elements. |

Knight's Commission's Oath triggers Boreas's Fang on turn one, which is
intended. Relic and potion applications gain no Oath (§3's terms).

## 5. What the build and the sim must show

1. Both engines build the 37 cards, the five re-aimed Knights, 7 relics and
   3 potions; the Silent borrow leaves his relic and potion pools (pick 1).
2. A paired sim of the stock drafter on the 41-card pool against the 78:
   fights won and Oath per fight. Each deck forced (the four one-element
   decks, Gale, Switch, Muster) wins within 10 points of the default drafter.
3. Then two Sonnet seats, one act per seat. Then you play.

## Picks

1. **His relics replace the Silent's six, and the three potions replace the
   Silent's.** (a) Yes. **Default.** (b) Keep the borrow beside them for now.
2. **Each element gets a job and two payoffs; Muster stays a small sixth
   deck** (six cards, above). (a) Yes. **Default.** (b) Elements as in the
   first draft (every Knight apply-and-Block), with Muster at eleven.
3. **Downburst bends the Swirl rule** (its spread copies arrive fresh, so a
   second Anemo card can chain). (a) Yes, as a Rare. **Default.** (b) No:
   Downburst is a plain 12 [16] Swirl attack.
4. **Banner of the West Wind** lets Oath follow the switch, which makes
   Switch nearly free. (a) Yes, as a Rare relic. **Default.** (b) Replace it
   with "The first time each combat your current element changes, gain 1
   Energy and draw 2."
