# Story events: the reward pass, 2026-10-19

GPT's audit of the 32 story events (Klee, Varka, Furina, Kokomi; Yae has
none) found the chains worth keeping and several rewards generous. [USER]
added two concerns and ruled all four defaults ("Yep, agreed on all of the
above!"):

1. **Named cards become rarity offers.** "We sometimes give specific card
   rewards ... when the game usually limits it to rarity + type. I think this
   supplies overly easy access to very specific archetypes or enablers."
2. **The story room is no longer the act's first event room** but a rising
   chance: 1/3 at the act's first event room, 2/3 at the second, certain at
   the third. One roll on the run's seed (co-op shares it, a reload cannot
   reroll it); an act with fewer event rooms takes the chain's skip branch.
3. **Every option is repriced against base-game events** (this paper).
4. **Telemetry logs each story choice** (event, option, HP, Gold, deck size
   at the time), and the next seat rounds judge the prices.

The fixes that needed no ruling (Serpent's Bones removing its own curse, the
Mk.Omega Bomb filter, Found You's hidden Doubt clean, the Max HP warning,
three lore lines) are a separate PR.

## The yardsticks (installed StS2 events, read from its code)

- **A random relic** costs 11 HP (The Round Tea Party) or 8 Max HP (Unrest
  Site). **No base event sells a guaranteed Rare relic.**
- **Two transforms** cost all your Gold, with at least 100 (Morphic Grove).
- **Free:** two random upgrades or one removal (Doors of Light and Dark); a
  9 heal and a chosen upgrade (Sapphire Seed); one chosen transform or
  upgrade (Aroma of Chaos).
- **A relic with a curse:** a random relic plus Clumsy, a curse that stays
  (This or That).
- **Card removal for Gold:** 125 Gold (Zen Weaver).

Our three-combat curses (Confinement, Overdue Reports, Stage Fright, Public
Address) are lighter than a curse that stays, and are priced as such.

## The rules this paper applies

- **A card reward is "Choose 1 of 3 random [rarity] cards"**, with a type
  only where the scene names one; a Companion's scene offers Companions of
  that rarity. Not upgraded in acts 1 and 2 unless HP is paid for it; act-3
  finales offer upgraded cards, as act 3's card rewards upgrade more often.
- **A random relic costs 10 to 12 HP.** A guaranteed Rare relic is sold only
  as an act-3 finale or a chain payoff, at 18 HP.
- **Two transforms cost 100 Gold** (locked under 100).
- **A relic is never paired with a three-combat curse**; it takes a curse
  that stays (Doubt), the This or That shape.

## The changes (everything not listed stays)

| Event (act) | Option | Now | Proposed |
|---|---|---|---|
| Starsnatch Cliff (K1) | Just one little bomb | Fish Blasting | Choose 1 of 3 Common Attacks |
| Mom's Marks (K1) | Try the recipe | 10 HP: Alice's Recipe | 10 HP: choose 1 of 3 Rare cards |
| Found You! (K2) | Ask nicely | Dodoco Tag+ | Choose 1 of 3 Uncommon Attacks |
| Found You! (K2) | Grab and run | 8 HP: random relic | 11 HP: random relic |
| Alice's Cache (K2) | Open it! | 15 HP: Rare relic | 12 HP: random relic |
| Alice's Cache (K2) | Leave it | 50 Gold: transform 2 | 100 Gold: transform 2 |
| Alice's Cache (K2) | Save it | 5 HP: potion | same, plus "Mom's chest will still be there." |
| Knights Come Looking (K3) | Kaeya / Noelle / Albedo | Kaeya+ / Noelle+ / Albedo+ | Choose 1 of 3 upgraded Uncommon / Common / Rare Companions |
| Mom's Last Note (K3) | Try the trick | 10 HP: Alice's Introduction Magic+ | 10 HP: choose 1 of 3 upgraded Rare cards |
| Dispatch from Mondstadt (V1) | Request reinforcements | Choose 1 of 3 Knights | Choose 1 of 3 Uncommon cards |
| The Rearguard (V1) | Take the rear | 10 HP: choose 1 of 3 Knights | 10 HP: choose 1 of 3 Rare cards |
| Wolf of the North (V2) | Ask after the pack | Razor+ | Choose 1 of 3 Uncommon Attacks |
| Second Satchel (V2) | Sign by lamplight | 8 HP: upgrade 2, remove every Overdue Reports | 8 HP: upgrade 2 (the Reports have expired by act 2) |
| Acting Grand Master (V3) | Let her lead | Jean+ | 10 HP: choose 1 of 3 upgraded Rare Companions |
| Acting Grand Master (V3) | Full report | Remove every Curse, 25 Gold each | 50 Gold each |
| Long Way Home (V3) | Eula / Noelle / Diluc | Eula+ / Noelle+ / Diluc+ | Choose 1 of 3 upgraded Uncommon Attacks / Skills / Powers |
| An Empty House (F1) | Take a costume | Random relic + Stage Fright | Random relic + Doubt |
| Steambird Clipping (F1) | Cast the sequel | Choose 1 of 3 Guest Stars | Choose 1 of 3 Uncommon cards |
| The Understudy (F2) | Teach her the ending | 6 HP: Understudy's Debut+ | 6 HP: choose 1 of 3 upgraded Uncommon cards |
| Oratrice's Echo (F2) | Plead guilty | 12 HP: Rare relic | 12 HP: random relic |
| Oratrice's Echo (F2) | Performance | 50 Gold: transform 2 | 100 Gold: transform 2 |
| Letter from the Court (F2) | Keep it | Tearful Monologue | Choose 1 of 3 Common Skills |
| Curtain Call (F3) | Give them the finale | 10 HP: Let the People Rejoice+ | 10 HP: choose 1 of 3 upgraded Rare cards |
| An Empty Throne (F3) | Sit in it | 15 HP: Rare relic | 18 HP: Rare relic |
| Room with No One (Ko1) | Read the top book | Treatise+ | Choose 1 of 3 Uncommon Powers |
| Serpent's Bones (Ko2) | Lay a hand on it | 4 Max HP: Rare relic | 8 Max HP: random relic |
| Report from Gorou (Ko2) | Send for reinforcements | Choose 1 of 3 Gorou cards | Choose 1 of 3 Uncommon Companions |
| Endgame (Ko3) | Offer her last piece | 15 HP: Rare relic | 18 HP: Rare relic |
| Endgame (Ko3) | Trade pieces | 50 Gold: transform 2 | 100 Gold: transform 2 |
| Tide Comes In (Ko3) | Shape a whole shoal | 6 HP: Kurage Canopy+ | Choose 1 of 3 upgraded Uncommon Powers (free) |

**Kept on purpose.**
- **The First Exam's upgraded Four Winds' Ascension** (8 HP). It is Varka's
  Basic, which no reward offers, so a rarity offer cannot replace it, and an
  extra copy of his starter is not an archetype key.
- **Mom's Last Note's free Rare relic.** It is the payoff Klee bought in act
  2 by saving the chest, and it competes with three Bomb upgrades.
- **The Other Commander's Rare-card offer.** It is already a rarity offer and
  pays a Doubt that stays.
- **The 75 Gold-plus-curse options and the potions-plus-curse options.**
  Light curses for modest rewards are the intended shape.

## Picks

1. **The table as written.**
   - **(a, default)** Build it.
   - (b) Build it, but keep one named card per character as a signature
     moment: Klee's Alice's Recipe, Varka's Jean+, Furina's Let the People
     Rejoice+ and Kokomi's Treatise+, each at the price above.
2. **Finale Rares.**
   - **(a, default)** 18 HP for a Rare relic in act 3 (Empty Throne, Endgame).
   - (b) Make them random relics at 12 HP, like act 2.
