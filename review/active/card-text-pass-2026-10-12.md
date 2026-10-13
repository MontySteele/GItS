# Card text pass: one voice across the four kits, 2026-10-12

[USER]:
- "In general, Kokomi's cards have a lot of text ... can we do a pass and see if we can clean them up at all? And make sure they're all using standardized language where possible."
- Then: "do a review of the card text to unify the language after all recent changes."

**Evidence.** Two censuses (gitignored): `scratchpad/kokomi-text/census.md` covers Kokomi's 89 cards; `scratchpad/text-census/census.md` covers Klee, Furina, Varka, every Companion, the relics and potions. They quote every card as the player sees it and group every phrasing of the same idea. The base game's own text was read from its English loc table, 624 descriptions.

## What the numbers say

- **Nothing is broken.**
  - All texts are under the 120-character ceiling, except Durin's Principle of Purity (a known exception) and two Varka relics: Boreas's Fang at 171 and Wolf's Gravestone at 205.
  - No British spelling appears in any card, relic or potion. The one British word left, "grey silt", is on a Teyvat event page.
- **Kokomi is long because of her two-line cards, not because of wordiness.**
  - Her median card is 65 characters, against 51 for a base Uncommon, and 27 of her 89 cards are longer than 90% of base cards.
  - Most of those carry "Or plan:", which is two cards' worth of text by design.
  - So the trims below are small, and the bigger win is saying each idea one way everywhere.
- **The real problem is inconsistency.** The same idea is worded several ways, often across kits. The list follows.

## The house rules (my calls; each one ends a split)

1. **Piles are golded and capitalized, as in the base game:** [gold]Hand[/gold], Draw Pile, Discard Pile, Exhaust Pile.
   - The base golds "Hand" 103 times and never writes "your hand".
   - We write lowercase "hand" on 19 items, Kokomi's 18 included.
   - The lint gains "Hand".
2. **Status and Curse are capitalized**, as in the base game. That fixes 5 Klee cards and 3 of Kokomi's.
3. **Energy is the icon, never the word**, as in the base game (69 descriptions). That fixes 2 Kokomi cards and Klee's Sparkling Burst.
4. **"Whenever" for a repeating trigger; "When" only for a one-time one.**
   - Diona's Icy Paws and Banner of the West Wind move to "Whenever".
5. **Word order for first-time triggers is "The first time each turn you ..."**, as Klee and Varka write it. Furina's "The first time you Drain each turn" moves to that order.
6. **Delayed effects:**
   - "Next turn, ..." for something that happens once;
   - "At the start of your turn, ..." for something that repeats.
   - "At the start of your next turn" and a trailing "next turn" go.
7. **The reaction verb is "triggers"**, as in "If it triggers an Elemental Reaction". Klee uses it 5 times and Varka's "causes" 2 times; Varka moves to "triggers".
8. **Amounts are "additional"** (the lint's rule). Klee's held-back "N more" rows, Team Effort and Sparkling Burst, finally move. "Lose 1 more" style text stays where "more" means "again".
9. **Keywords and card names are golded wherever they appear in prose:**
   - "sets off" becomes [gold]Set off[/gold] (Sparkborne Magic, Pass the Match, Knights of Favonius, Fireworks Stand);
   - card names: Alice's Mine, Pop!, Four Winds' Ascension.
10. **A Guest Star's hover says what its card face says,** in the same words, without parentheses. Today Navia's and Neuvillette's hovers carry an act the card face omits, and Neuvillette's says "more".
11. **"Whenever an Elemental Reaction happens" means any reaction on the board; "you trigger" means only your own.**
    - Dahlia's Favonian Favor pays only for reactions you trigger, so it will say "Whenever you trigger an Elemental Reaction".
    - Navia keeps "happens", since she pays on any reaction.
12. **American English goes into `text-conventions.md`** as a written rule, with your words. The "grey" on the event page becomes "gray".

**Relics:**
- **Boreas's Fang:** "At the start of each combat, your starting Knight's element becomes current. The first time each combat you gain Oath, add Four Winds' Ascension to your Hand." The reshuffle clause from today's build goes into its hover.
- **Wolf's Gravestone:** says the same, plus "It is upgraded and costs 0 this turn."
- **Tamakushi Casket:** loses its second sentence: "At the start of your turn, if a Plan is waiting, gain 3 Block."

## Kokomi: one verb for planning

- **Today, putting a card on the Bake-Kurage is worded five ways:**
  - "write ... as a Plan";
  - "when written";
  - "when you wrote this";
  - "play on the Bake-Kurage";
  - "play a card on the Bake-Kurage".
- **Her cards already print "Or plan:".** So the verb is **plan**: "plan a card", "when planned". Carrying it out stays "the Bake-Kurage carries out", and "Plan waiting" stays.

| Card | Today | After |
|---|---|---|
| Divine Strategy | The first time each turn you play a card on the Bake-Kurage, the line above its Plan happens now too. | The first time each turn you plan a card, its first line also happens now. |
| Treatise | Once a turn, when you play a card you could write as a Plan instead of writing it, draw 1 card. | The first time each turn you play a card you could have planned, draw 1 card. |
| Grand Design | Write up to 3 cards from your hand as Plans. They cost 0. | Plan up to 3 cards from your Hand. They cost 0. |
| Watatsumi Resistance | Whenever you write a Companion card as a Plan, add a Sting to your hand. | Whenever you plan a Companion card, add a Sting to your Hand. |
| Kelp Wall | ... Or plan: Gain 9 Block, plus 3 for each status or curse in your hand when written. | ... Or plan: Gain 9 Block, plus 3 for each Status or Curse in your Hand when planned. |
| Flank | ... Or plan: Deal 9 Hydro damage to each enemy that intended to attack when you wrote this. | ... Or plan: Deal 9 Hydro damage to each enemy that intended to attack when planned. |
| Opening Gambit | ... Or plan: Apply 1 Vulnerable to ALL enemies. The Plan after this one deals double damage. | ... Or plan: Apply 1 Vulnerable to ALL enemies. Your next Plan deals double damage. |
| Second Wave | ... Or plan: The Plan after this one is carried out twice. | ... Or plan: Your next Plan is carried out twice. |
| Call the Generals | Choose 1 of 3 random Rare Inazuma Companion cards. Add it to your hand. It is Ethereal. It costs 0 this turn. | Choose 1 of 3 random Rare Inazuma Companions to add into your Hand. It is Ethereal and costs 0 this turn. |
| Sangonomiya's Orders, Orders from the Shrine, Watatsumi Muster | ... a random Common Inazuma Companion card to your hand. It is Ethereal. | ... a random Common Inazuma Companion to your Hand. It is Ethereal. |
| Gorou, Juuga | ... Or plan: Gain 6 Block instead. | ... Or plan: Gain 6 Block. |
| Riptide | Deal 11 Hydro damage to ALL enemies, 3 additional damage to debuffed ones. ... | Deal 11 Hydro damage to ALL enemies. Debuffed enemies take 3 additional. ... |
| Riptide Ruin | Deal 9 Hydro damage to ALL enemies twice. Add 3 Dazed into your Discard Pile. | Deal 11 [14] Hydro damage to ALL enemies twice. (You asked whether it needs the Dazed; it goes, with 2 more damage a hit.) |
| Tidecleanse | Exhaust up to 2 statuses or curses in your hand. Apply 1 Weak. | Exhaust up to 2 Statuses or Curses in your Hand. Apply 1 Weak. |
| Tactical Relay, War Council | ... Energy | ... the energy icon |

Plan-only cards (Masterstroke, Tactical Relay, Crystal Collapse) keep "Play on the Bake-Kurage. Plan: ...". It is the one place the pet must be named. Crystal Collapse's lowercase "play" after "Plan:" is capitalized.

## Ruled 2026-10-12

[USER]: "On Kokomi: Let's stick with "Plan" for consistency."

- **Pick 1 (a):** "plan" is her one verb: "plan a card", "when planned". The twelve house rules and the table above are built as written.

## For [USER] (ruled above)

1. **Kokomi's planning verb.**
   - **(a) Default:** "plan" everywhere, as above.
   - (b) Keep "write" and make it consistent ("write a card", "when written").
