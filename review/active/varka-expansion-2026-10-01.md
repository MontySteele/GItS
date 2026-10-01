# Varka expansion: his own relics, and the pool to 78

Paper, 2026-10-01. Main session design. The kit's rules are in
`review/active/varka-paper-kit-2026-09-28.md` §3; this paper adds cards,
relics and potions and changes no rule.

## 1. Why

[USER], after the co-op run: "I feel like my exact build (use the card that
summons random Knights to mix and match elements + power-stacking) might be
run-specific, so I'm curious how it feels at a full-density card pool." And
on 2026-10-01: "I think it's time we look at the relics and expansion so any
future changes are based on realistic deckbuilding."

Today the pool is 41 cards (15 Common / 18 Uncommon / 8 Rare); every kit's
target is 78. At 41 a draft sees the same few cards, so neither seat records
nor your run say much about balance. His relic pool is the Silent's six
(Ninja Scroll, Paper Krane, Ring of the Snake, Tingsha, Tough Bandages,
Twisted Funnel) plus Boreas's Fang (#776's finding); none of the six serves
him.

What the two seat rounds and your run said the pool lacks
(`review/records/varka-open-oath-round-2026-10-01.md`,
`varka-oath-round-2026-09-29.md`):

- **Turns with no aura source have no decision.** Both seats, most fights'
  first turn: "no applier in hand, Strike/Defend by rote".
- **Block runs thin into act 2** (both rounds).
- **Rares are 8**, so build-arounds rarely appear.
- **Hydro and Pyro have two Knights each**; Cryo has three.
- **Your build had no name.** Knights' Roll Call plus Powers was a Knights
  deck the paper called "support cards, not an archetype ... the name waits
  for a distinct turn". This batch gives it one (pick 2).

## 2. The shape

**37 cards: 5 Common, 17 Uncommon, 15 Rare, for a pool of 78 (20 / 35 /
23)**, the same split as Kokomi's target. Each new card serves one of five
decks:

1. **Focus**: one element all fight, its Oath read by the payoffs.
2. **Switch**: changing element pays.
3. **Gale**: many Swirls.
4. **Muster** (new, pick 2): many Knights played; your Roll Call build.
5. **Ascension** (inside Focus): more copies of Four Winds' Ascension.

The numbers are first drafts for the sim and seats.

## 3. The cards

**Common (5).** The first two are aura sources for turn one.

| Card | Cost, type | Text | Deck |
|---|---|---|---|
| Pathfinder's Mark | 0 Skill | Apply your current element to an enemy (a random one of the four if you have none). [ALL enemies] | All |
| Cavalry Charge | 1 Attack | Deal 7 [10] damage as your current element. | Focus |
| West Wind Shield | 1 Skill | Gain 5 [7] Block, plus 2 for each enemy with an aura. | Gale; Block |
| Knightly Strike | 1 Attack | Deal 7 [10] damage. If you played a Knight this turn, deal 4 more. | Muster |
| Amber: Sharpshooter | 1 Attack, Pyro Knight | Deal 9 [12] Pyro damage. | Pyro |

**Uncommon (17)**

| Card | Cost, type | Text | Deck |
|---|---|---|---|
| Lion's Roar | 2 Attack | Deal 8 [11] damage to ALL enemies, plus 1 for each Oath of your current element. | Focus |
| Vow of the Blade | 1 Skill | Gain 1 Oath of your current element. Draw 1 [2] card(s). | Focus |
| Bulwark of Oaths | 2 Skill | Gain 12 [15] Block, plus 1 for each Oath of your current element. | Focus; Block |
| Unwavering Banner | 1 Power | Only Knights and cards that name it can change your current element. [Innate] | Focus |
| Shifting Gale | 1 Attack | Deal 6 [8] damage. If your current element changed this turn, deal it twice. | Switch |
| Cycle of Seasons | 1 Power | Whenever your current element changes, deal 4 [6] damage to ALL enemies. | Switch |
| Four Banners | 2 Attack | Deal 5 [6] damage for each element you have Oath in. | Switch |
| Eye Wall | 1 Skill | Gain 6 [8] Block. Whenever you Swirl this turn, gain 3 Block. | Gale; Block |
| Pressure Front | 1 Skill | Apply your current element to ALL enemies. [Retain] | Gale |
| Crosscurrent | 1 Skill | Swirl an enemy's fresh aura. This Swirl pays twice. [Draw 1] | Gale |
| Assembly at the Cathedral | 1 Power | Whenever you play a Knight, deal 3 [4] damage to a random enemy. | Muster |
| Shield Wall of Favonius | 1 Skill | Gain 5 [7] Block, plus 4 for each Knight you played this turn. | Muster; Block |
| Call Up the Reserves | 0 Skill | Put a Knight from your discard pile into your hand. [It costs 0 this turn.] | Muster |
| Barbara: Wellspring Hymn | 2 Skill, Hydro Knight | Gain 14 [18] Block. Apply Hydro to ALL enemies. | Hydro |
| Amber: Ace Pilot | 1 Skill, Pyro Knight | Draw 2 [3] cards. Apply Pyro to an enemy. | Pyro |
| Lisa: Pulsating Witch | 1 Skill, Electro Knight | Apply Electro to ALL enemies. Gain 6 [9] Block. | Electro |
| Dawn Patrol | 0 Skill | Gain 1 Energy. Draw 1 card. Exhaust. [Draw 2] | All |

**Rare (15)**

| Card | Cost, type | Text | Deck |
|---|---|---|---|
| Oath Unto Death | 3 Power | Whenever you gain Oath of your current element, gain 1 more. [Innate] | Focus |
| Storm's Reckoning | 3 Attack | Deal 4 [5] damage to ALL enemies for each Oath of your current element. Its Oath becomes 0. | Focus |
| Grand Master's Verdict | 3 Attack | Deal 15 [20] damage. Double your current element's Oath. Exhaust. | Focus |
| Oathbound Aegis | 2 Power | At the end of your turn, gain Block equal to your total Oath, up to 15 [20]. | Focus/Switch; Block |
| Weathervane | 2 Power | At the start of your turn, you may choose an element you have Oath in; it becomes your current element. [Innate] | Switch |
| Tempest of the Four Winds | 2 Attack | Deal 4 [5] damage four times, as Pyro, Hydro, Cryo and Electro. | Switch |
| Twin Gales | 1 Power | Your Swirls pay both your current element and the element Swirled. [Innate] | Gale/Switch |
| Downburst | 2 Attack | Deal 12 [16] damage. If it Swirls, the copies it spreads arrive fresh. | Gale (pick 3) |
| Eye of Stormterror | 2 Power | The first 3 times you Swirl each turn, draw 1 card. [Innate] | Gale |
| Charge of the Knights | 2 Attack | Deal 5 [6] damage for each Knight you played this combat. | Muster |
| Unbroken Line | 2 Power | The first Knight you play each turn costs 0. [Innate] | Muster |
| The Order Answers | 2 [1] Power | At the start of your turn, add a random Knight to your hand. | Muster |
| The Whole Order | 2 [1] Skill | Add a Pyro, a Hydro, a Cryo and an Electro Knight to your hand. They cost 0 this turn. Exhaust. | Muster |
| Oath of Fealty | 1 [0] Skill | Gain Oath of your current element equal to the Knights you played this combat. Exhaust. | Muster to Focus |
| Wolfpack | 1 Power | Whenever you play Four Winds' Ascension, add a copy of it to your discard pile. [Innate] | Ascension |

Notes:

- **Pathfinder's Mark** is a 0-cost Oath. That is deliberate: it is the
  turn-one decision the seats asked for. It is the card to watch.
- **Unwavering Banner** protects a Focus deck from the open Oath: a
  Mondstadt companion's Pyro no longer drags him off Cryo. It is a choice,
  not a fix, because the open rule is what feeds Switch.
- **Muster's random Knights** come from his own Knights (the starter-only
  four excluded), so they read his elements.
- **Power costs** follow the cost sweep: Powers sit at 1, 2 and 3; only two
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
intended: the Ascension in the opening hand is a small plus. Relic and
potion applications gain no Oath (§3's terms).

## 5. What the build and the sim must show

1. Both engines build the 37 cards, 7 relics and 3 potions; the Silent
   borrow leaves his relic and potion pools (pick 1).
2. A paired sim of the stock drafter on the 41-card pool against the 78:
   fights won and Oath per fight. Each of the five decks, forced, wins within
   10 points of the default drafter.
3. Then two Sonnet seats, one act per seat, as in the last two rounds. Then
   you play.

## Picks

1. **His relics replace the Silent's six, and the three potions replace the
   Silent's.** (a) Yes. **Default.** (b) Keep the borrow beside them for now.
2. **Muster becomes his fourth deck** (Knights played as the payoff: eight
   cards above, plus Roll Call and Grand Master's Order). (a) Yes.
   **Default.** (b) No: Knights stay support cards and these eight are
   re-aimed at Focus and Gale.
3. **Downburst bends the Swirl rule** (its spread copies arrive fresh, so a
   second Anemo card can chain). (a) Yes, as a Rare. **Default.** (b) No:
   Downburst is a plain 12 [16] Swirl attack.
4. **Banner of the West Wind** lets Oath follow the switch, which makes
   Switch nearly free. (a) Yes, as a Rare relic. **Default.** (b) Replace it
   with "The first time each combat your current element changes, gain 1
   Energy and draw 2."
