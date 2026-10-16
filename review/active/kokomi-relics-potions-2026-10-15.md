# Kokomi's own relics and potions (2026-10-15)

Kit census pick 1, ruled (a) on 2026-10-15 ([USER]: "Agreed on all of the
above!"): Claude designs Kokomi a full set in the base shape. Kokomi is at
Prototype, so the set is Claude's and carries no pick. Today she rolls the
Silent's relics and potions; her own are the Tamakushi Casket and its Ancient
upgrade only (`review/active/kit-census-2026-10-15.md` sec.3).

## The shape

Every base character has, beside its starter, one Common, two Uncommon, three
Rare and one Shop relic, and three potions (Common, Uncommon, Rare). Klee and
Varka match it. Each of Kokomi's three lanes (Plans, Stings and reactions,
Companions) gets at least one relic, and the set leans on her known weakness:
the setup turn, when Energy goes into Plans and little is left for Block
(round 9 "Next").

## Relics

| Rarity | Name | Text | Lane | Base relic it is sized against |
|---|---|---|---|---|
| Common | Sango Pearl | The first card you plan each combat costs 0. | Plans | Lantern-size: about 1 Energy a fight, on the setup turn |
| Uncommon | Resistance Armband | The first time you play a Companion each turn, gain 4 Block. | Companions | Regalite (first card created each turn: Block) |
| Uncommon | Electro Sigil | At the start of each combat, apply Electro to ALL enemies. | Reactions | Twisted Funnel (4 Poison to ALL): her first Hydro hit on each makes Electro-Charged, 4 Poison |
| Rare | Everlasting Moonglow | After your first Plan each turn is carried out, return it to your Hand unless it Exhausts. | Plans | Andrius's Howl, Bookmark: one card back a turn, still paid for |
| Rare | Ocean-Hued Clam | Whenever you trigger an Elemental Reaction, Mend 1. | Reactions | Her long-fight deaths; Mend cannot pass her HP at the start of the fight |
| Rare | Kurage Lantern | Your Stings and Wards are not Ethereal. | Stings | Bends a rule: save Stings for The Shape of Water or a reaction turn |
| Shop | Resistance Muster Roll | At the start of each combat, choose 1 of 3 random Inazuma Companions to add to your Hand. It costs 0 this turn. | Companions | Favonius Duty Roster (Varka's Shop relic) |

Readings a builder needs:
- **Sango Pearl:** "plan" is writing a card onto the Bake-Kurage. Cost the card
  0 when it is written as a Plan, the first time in each fight (a refund of the
  Energy paid is acceptable if the cost cannot be changed at the moment of
  choice). Played normally, the card costs its usual amount and the Pearl
  waits.
- **Everlasting Moonglow:** "first" is the first Plan carried out at the start
  of the turn (order written). Change of Plans carrying a Plan out early
  counts as that turn's first if it comes first. A Plan carried out twice
  returns once. An Exhaust card (Sting, Ward, Turnabout) is not returned.
- **Ocean-Hued Clam:** every named reaction she triggers, Plans and Stings
  included. Mend's existing ceiling applies.
- **Kurage Lantern:** Stings and Wards made while she holds it are not
  Ethereal; they still Exhaust when played or carried out.
- No relic writes or carries out a Plan by itself (brief rule 4, "Nothing
  happens by itself").

## Potions

| Rarity | Name | Text |
|---|---|---|
| Common | Bottled Shoal | Add 3 Stings to your Hand. |
| Uncommon | Bottled Tide | The Bake-Kurage carries out every waiting Plan now. |
| Rare | A Stunning Stratagem | Next turn, every Plan is carried out twice. |

A Stunning Stratagem is Kokomi's special dish in Genshin. Bottled Tide is the
setup-turn escape: a turn of Plans lands at once when the fight cannot wait.

## What changes for her pools

Her relic offer becomes these seven, and her potion pool becomes these three.
The Silent borrow leaves her offer, as pick 2 of the census ruled ("drop the
whole Silent borrow from each kit once it has its own full set"). The starter
and its Ancient upgrade are unchanged.

## What to watch in her next round

Take rates of each relic and potion (`tools/offer_report.py`), whether Sango
Pearl's free Plan changes setup-turn Block, and whether Everlasting Moonglow
makes one Plan the whole fight.
