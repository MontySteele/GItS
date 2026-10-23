# Varka text audit, 2026-10-23

The writing review, kit two (ruled 2026-10-23, `localization-2026-10-19.md`;
format: `kokomi-text-audit-2026-10-22.md`; kit one:
`klee-text-audit-2026-10-23.md`).

Read: every Varka card face, Ancient card, relic, potion, power badge and
keyword tip, from `tools/player_text_census.py` and
`tools/lint_text_conventions.py --census`, against
`docs/current/text-conventions.md`. Story events, dialogue and barks wait
for the story pass.

## 1. Length

88 cards, median 63, 18 over the 80 target, 4 over 100, none over 120. The
longest (Unwavering Banner 115, Marching Orders 113, Stoke the Flames 111)
are three clauses each, and each clause earns its place. Varka's text is the
tidiest of the kits; most of what follows is one-word drift.

## 2. Fixes (no number or rule changes)

1. **"for each", never "per"** (base wording; Kokomi's audit fixed the
   same). Four Winds' Ascension and Dandelion Gale: "Then deal 3 damage per
   Oath of your current element" becomes "Then deal 3 damage for each Oath
   of your current element". Northwind Avatar: "plus 2 per Oath" becomes
   "plus 2 for each Oath". Azure Devour, Eye of the Storm and Oathsworn
   Strike already say "for each". Four Winds' Ascension is a starter card;
   this is wording only. `text-conventions.md` quotes the old "per" in its
   current-element row and is updated to match.
2. **A single-target card names no target** (rule 3). Razor: Awakening:
   "Deal 6 [8] Electro damage to an enemy." becomes "Deal 6 [8] Electro
   damage."
3. **Glacial Edict reads in the shape Deep Freeze uses.** "Apply Cryo to an
   enemy, and 1 Weak and 1 Vulnerable, plus 1 of each for every 3 [2] Cryo
   Oath." becomes "Apply Cryo, 1 Weak and 1 Vulnerable to an enemy. Apply 1
   more of each for every 3 [2] Cryo Oath."
4. **Frost Ward says who gets the Weak.** "For each enemy with an aura,
   apply 1 Weak and gain 3 [4] additional Block." becomes "Apply 1 Weak to
   each enemy with an aura and gain 3 [4] additional Block for each." (the
   code applies it to each aura-wearing enemy).
5. **Unwavering Banner prints one rule on both faces.** The card says "Only
   Knights change your current element. Whenever another card would ..."; its
   badge says "Only Knights can change ..." and, upgraded, "When another card
   would". Both become the card's words.
6. **"current element" is one span** (the conventions table). Boreas's Fang
   and Wolf's Gravestone: "your starting Knight's element becomes current"
   becomes "your starting Knight's element becomes your current element".
   Knight's Commission: "gain 2 Oath in your starting Knight's element"
   becomes "gain 2 Oath of your starting Knight's element".
7. **No semicolons outside an either/or** (rule 14). Bottled Resolve:
   "Choose an element. It becomes your current element; gain 3 Oath of it."
   becomes "... It becomes your current element. Gain 3 Oath of it."
8. **No contraction on a face.** Twin Gales: "If it's your current element,
   it pays twice." becomes "If that is your current element, it pays twice."
9. **The Four Winds' Ascension tip.** "Played, it goes to your Discard Pile
   and returns after a reshuffle." becomes "When played, it goes to your
   Discard Pile and comes back after a reshuffle."

## 3. One idea, two spellings: reading every element's Oath

- All Four Winds (Ancient): "Your cards read your Oath of every element
  together."
- Elixir of the Four Winds: "This turn, your cards read your total Oath
  across all four elements."

Oathbound Aegis already says "half your total Oath", so "total Oath" is the
word the kit has: "Your cards read your total Oath." and "This turn, your
cards read your total Oath."

## 4. "Jean — Wind Companion"

The card is a Varka Skill, not a Knight; its row says the em dash is there on
purpose because a colon marks a Knight. But "Wind Companion" after a name
reads as a Companion card, which it is not, and it is the only Varka card
whose title is a description rather than a name. Its id is already
`jean_dandelion_breeze`, Jean's burst.

## 5. Klee, carried from the base wording

The base game writes "Choose 1 of 3 random cards to add into your Hand." (5
uses, "to add to your" 0). Kokomi and Varka match it; Klee's Adventure Club
and Tag Along say "to add to your Hand". Built here, after Klee's PR lands.

## Picks

1. **Section 2's nine fixes and section 5.** (a, default) build them all.
   (b) all but named ones.
2. **Every element's Oath.** (a, default) "total Oath" on both. (b) keep
   both spellings.
3. **Jean's card.** (a, default) renamed "Dandelion Breeze", a plain card
   name like Favonius Cut; the Knights keep the colon. (b) keep "Jean — Wind
   Companion".
