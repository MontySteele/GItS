# Yae: a rate pass, her two Ancients, her relics and potions (2026-10-16)

Yae is a Prototype kit, so these are Claude's cards and carry no pick.
[USER]: "Let's do a design pass over the current Yae pool. Does anything look
too obviously weak or strong for its rarity / energy rate? And let's design
the two Yae Ancient cards, as well as the Ancient relic if that's still
missing. Plus potions and regular relics if those are as well."

**What is missing today:**
- **Her two Ancient cards.** `RosterAncientCards` has no Yae list, and
  `Patches/YaeDustyTomeGuardPatch.cs` stops Darv offering her a Dusty Tome
  (BACKLOG).
- **Her own relics and potions.** She rolls the Silent's
  (`YaeRelicPool.cs`).
- **The Ancient relic is not missing.** Enlightened Blessing, the Touch of
  Orobas upgrade of Meditations of a Yako, Publishes 2 after an elite or boss
  instead of 1 (`yae_shrine.PUBLISH_COUNT`).

**Numbers used below** (`tier0/engine/yae_shrine.py`):
- A Sakura acts at her turn end: 2 + Level damage, Foxfire 1 + Level to ALL,
  and Kitsune 2 + Level Block.
- It is planted at Level 1, with 3 turns, and the shrine holds 3.
- Its turns tick down only at turn end. Deadline Extension on a Sakura stops
  the tick for good (`if not eternal and not s.has(DEADLINE)`).
- So a fresh Sakura is about 3 damage a turn for 3 turns, 9 in all.

## 1. The rate pass: what reads off its rarity

Round 7 is the only seat round on this pool, and the eleven refill cards
have none. So this pass reads the texts against the base rates (a 1-cost
Common is about 9 damage or 8 Block) and against her own cards.

**Too strong**

| Card | Today | Why | Change |
|---|---|---|---|
| **Evergreen Charm** (C Skill 1) | Gain 7 Block. Edit your oldest Sakura: Deadline Extension. | On a Sakura, Deadline Extension means it never withers. That is Eternity (Rare, 3) for one Sakura, plus 7 Block, at Common. Taken 5 of 7. | Gain 7 Block. Your oldest Sakura lasts 2 more turns. (Kitsune's Blessing's "lasts 2 more turns" reading.) |
| **Fox Fire Draft+** (C Skill 0) | Edit every Sakura: Fox Fire. | Fox Fire on a Sakura deals 4 each time it acts, about 12 per Sakura. Upgraded, that is up to 36 damage for 0 at Common. | The upgrade becomes "your 2 newest Sakura". |
| **Thunderbolt Tithe+** (U Atk 1) | 4, plus 6 for each Sakura. | 22 damage for 1 with a full shrine. The base Tithe's 15 is right. | Upgrade to 4, plus 5 each (19). |
| **Editorial Priority** (U Power 1) | The first Annotated card you play each turn costs 0. | About 1 Energy a turn in a deck that Edits every turn. No base Uncommon Power is an Energy engine. | Moves to Rare (see Mischievous Teasing). |
| **Edict of Cleansing+** (U Power 1) | Sakura strikes deal 5 more to Weak or aura'd enemies. | A Level 1 strike is 3, so +5 nearly triples it. The base +3 already doubles it. | Upgrade to +4. |

**Too weak**

| Card | Today | Why | Change |
|---|---|---|---|
| **Mischievous Teasing** (R Skill 0) | Apply 2 Weak to ALL enemies. Draw 2. Exhaust. | Flagged in the dedupe paper: an Uncommon's effect. Taken 0 of 2. | Moves to Uncommon, unchanged. That keeps the pool at 20 / 38 / 20. |
| **Rewrite** (C Skill 1) | Discard up to 2, draw that many. Edit: Red Ink. | 1 Energy to swap two cards. The Silent's Acrobatics draws 3 for 1. | Draw 2 cards. Discard 1 card. Edit a card in your hand: Red Ink. |
| **Fox Trick** (C Skill 1) | Apply 2 Weak. Draw 1. | Below Backflip (5 Block, draw 2), and Weak is her fuel. | Apply 2 Weak. Draw 2 cards. (Upgrade: 3 Weak.) |

**Looked at and left alone:**
- **Shrine Maiden's Guard.** About 15 Block over three turns, which is strong
  at Common. She takes 1.93 times base damage in act 1, so the Block is meant.
- **Thunder Petal.** Better than her basic planter by 5 damage, as a drafted
  Common should be.
- **Daisesshou and Guardian of Narukami.** Big, but Rare and paid for with the
  shrine.
- **Offertory Box.** 3 Energy for 0, but it Exhausts and needs a full shrine.
- **Stellar Conduct.** Solo, it can only react off a Companion's element.
  Watch its take rate; no change on one round.

## 2. The two Ancient cards

Every other kit follows the same shape. Orobas's Archaic Tooth turns a starter
card into a big version of itself, and Darv's Dusty Tome adds a Power that
bends one of the kit's rules.

**Archaic Tooth, on Yakan Evocation: "Yakan Evocation: Sesshou Sakura"**
(her Elemental Skill's full name).
- Skill, Ancient, costs 1, 0 upgraded.
- "Plant a **Foxfire Sakura** at Level 3. Edit it: **Deadline Extension**."
- A totem that hits ALL enemies for 4 at every turn end and never withers. It
  is built only from parts she already has, so there is no new rule.
- A second play is a full-shrine-style plant of its kind. It Levels that
  Foxfire Sakura, or the new one stands beside it. Either is fine.

**Dusty Tome: "Yae Publishing House"**
- Power, Ancient, costs 2, 1 upgraded (Divine Strategy's cost).
- "Your **Edits** write their Annotation twice."
- This bends the Edit rule, the half of her kit no Rare bends yet. Layers
  already add up, so Red Ink gives 6 and Fox Fire 8. Footnote draws 2,
  Royalties gives 2 Energy, and Reprint plays the card three times (still
  once a combat).
- Deadline Extension twice is the same as once.
- I rejected "your Sakura also act at the start of your turn": turns tick only
  at turn end, so it just doubles her damage instead of bending a rule.

With both cards in, `YaeDustyTomeGuardPatch` and its BACKLOG line are deleted.

**The starter's Annotations carry over.** [USER] (2026-10-16): "let's make
it so that any existing annotations on the starter card carry over to the
Ancient version. I can already see that being a complaint." The base game's
Archaic Tooth already does this: it makes the Ancient, upgrades it if the
starter was upgraded, and enchants it with a copy of the starter's
enchantment, so every Annotation Published on Yakan Evocation stays on
Yakan Evocation: Sesshou Sakura (`YaeAncientsRelicsTests` pins it).

## 3. Her relics (the base shape: 1 Common, 2 Uncommon, 3 Rare, 1 Shop)

| Rarity | Name | Text | Lane | Sized against |
|---|---|---|---|---|
| Common | Kitsune Mask | At the start of each combat, apply 1 Weak to ALL enemies. | Weak | Bag of Marbles. It aims at her act-1 bleeding and turns on her Weak cards. |
| Uncommon | Sacred Sakura Branch | At the start of each combat, plant a Sakura. | Shrine | Anchor-size: about 9 damage over three turns, on the turn she is slowest. |
| Uncommon | Proofreader's Glasses | The first time you Edit a card each turn, draw 1 card. | Edit | One card a turn, paid for with an Edit. |
| Rare | Electroculus | Your Sakura's strikes deal 1 more damage. | Shrine | A third more on a Level 1 strike. A Foxfire's hit on ALL counts; Kitsune Block does not. |
| Rare | Saiguu's Inkstone | At the start of your turn, Edit a random card in your hand: Red Ink. | Edit | One free Edit a turn. Serialization, Bestseller and Editor-in-Chief read it. |
| Rare | Kagura Bell | Whenever you Tenko, each Sakura gains a Level. | Tenko | Turns Tenko from a refresh into growth. |
| Shop | Fox Ofuda | You can have 1 more Sakura. | Shrine | Sakura Channeling's words, and half its size. |

**The offer.** Her offer becomes Meditations, her seven and Enlightened
Blessing. The Silent borrow stops being offered (members only), as for Klee,
Furina and Varka (`Relics.ArmRelicPools.Offer`).

## 4. Her potions (Common, Uncommon, Rare)

| Rarity | Name | Text |
|---|---|---|
| Common | Bottled Sakura | Plant 2 Sakura. |
| Uncommon | Fox's Inkwell | Edit a card in your hand with an Annotation of your choice. |
| Rare | Narukami Sake | Each Sakura gains 2 Levels. Tenko. |

**Readings for the builder:**
- "Choose an Annotation" is Reborn as Guuji Yae's existing modal.
- Electroculus adds to the strike's size before Edict and Fox Fire.
- Kagura Bell Levels after the Tenko's strikes.
- Fox Ofuda stacks with Channeling.
- Saiguu's Inkstone skips cards Red Ink would do nothing on, as Edits already
  do.
- Icons and Ancient art come from Inazuma sources only (kit art from its own
  nation).

## Not in this paper

- **The Sakura display, the Power badges and the card trail** stay as their
  BACKLOG lines.
- **Grand Theater Program** (Furina, Rare: "At the start of your turn, gain 1
  Fanfare") reads small for a Rare. She prints about one Fanfare per HP she
  drains. She is at Balance, so a number change there is [USER]'s pick, for
  her next paper.
