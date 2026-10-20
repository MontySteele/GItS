# Story events: the reward pass, 2026-10-19

GPT's audit of the 32 story events (Klee, Varka, Furina, Kokomi; Yae has
none) found the chains worth keeping and several rewards generous. [USER]
added two concerns and ruled all four defaults ("Yep, agreed on all of the
above!"):

1. **Named cards become rarity offers.** "We sometimes give specific card
   rewards ... when the game usually limits it to rarity + type. I think this
   supplies overly easy access to very specific archetypes or enablers."
2. **The story room is no longer the act's first event room.** One roll per
   act, on the run's seed, makes it the 1st, 2nd or 3rd event room with equal
   odds (cumulative 1/3, 2/3, certain; not a fresh 2/3 roll after a miss,
   which would give 7/9 by the second room). Co-op shares the roll and a
   reload cannot reroll it; an act with fewer event rooms takes the chain's
   skip branch.
3. **Every option is repriced against base-game events** (this paper).
4. **Telemetry logs each story choice**: event, option, act, floor, HP and
   max HP, Gold and deck size at the time, and the cards offered and the card
   taken (or the relic or potion gained). The next seat rounds judge the
   prices on that.

The fixes that needed no ruling (Serpent's Bones removing its own curse, the
Mk.Omega Bomb filter, Found You's hidden Doubt clean, the Max HP warning,
three lore lines) are a separate PR.

## The yardsticks (installed StS2 events, read from its code)

- **A random relic** costs 11 HP (The Round Tea Party) or 8 Max HP (Unrest
  Site). **A guaranteed Rare relic** is sold for Gold, not HP: Welcome to
  Wongo's offers a revealed Rare for 200 Gold. No base event gives one for
  HP, so the 18 HP below is a judgment to test, not a conversion.
- **Two transforms** cost all your Gold, with at least 100 (Morphic Grove).
  100 Gold is cheaper whenever you hold more than 100; that discount is
  deliberate, a judgment to test.
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
| Knights Come Looking (K3) | Noelle | Noelle+ | Choose 1 of 3 upgraded Common Companions (free) |
| Knights Come Looking (K3) | Kaeya | Kaeya+ | 6 HP: choose 1 of 3 upgraded Uncommon Companions |
| Knights Come Looking (K3) | Albedo | Albedo+ | 12 HP: choose 1 of 3 upgraded Rare Companions |
| Mom's Last Note (K3) | Try the trick | 10 HP: Alice's Introduction Magic+ | 10 HP: choose 1 of 3 upgraded Rare cards |
| Dispatch from Mondstadt (V1) | Request reinforcements | Choose 1 of 3 Knights | Choose 1 of 3 Uncommon Companions (pick 3) |
| The Rearguard (V1) | Take the rear | 10 HP: choose 1 of 3 Knights | 10 HP: choose 1 of 3 Rare cards |
| Wolf of the North (V2) | Ask after the pack | Razor+ | Choose 1 of 3 Uncommon Attacks |
| Acting Grand Master (V3) | Let her lead | Jean+ | 10 HP: choose 1 of 3 upgraded Rare Companions |
| Acting Grand Master (V3) | Full report | Remove every Curse, 25 Gold each | 50 Gold each |
| Long Way Home (V3) | Eula / Noelle / Diluc | Eula+ / Noelle+ / Diluc+ | Choose 1 of 3 upgraded Uncommon Attacks / Skills / Powers |
| An Empty House (F1) | Take a costume | Random relic + Stage Fright | Random relic + Doubt |
| Steambird Clipping (F1) | Cast the sequel | Choose 1 of 3 Guest Stars | Unchanged: 3 random Guest Stars (pick 3) |
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
| Tide Comes In (Ko3) | Shape a whole shoal | 6 HP: Kurage Canopy+ | 6 HP: choose 1 of 3 upgraded Uncommon Powers |

**Kept on purpose.**
- **The First Exam's upgraded Four Winds' Ascension** (8 HP). It is Varka's
  Basic, which no reward offers, so a rarity offer cannot replace it, and an
  extra copy of his starter is not an archetype key.
- **Mom's Last Note's free Rare relic**, a named exception to the 18 HP
  rule. It appears only if Klee saved the chest in act 2 (paying 5 HP for a
  potion instead of the relic or the transforms then), and saving it hides
  the three Bomb upgrades (`KleeStory.cs:380`); on the day its alternatives
  are a heal and a paid card. A delayed payoff for an earlier cost, to test.
- **The Second Satchel's Overdue Reports removal.** The curse expires after
  three combats, not at the act's end, and with the story room now later in
  the act a late act-1 copy can reach it; it is also how the story resolves.
- **The Other Commander's Rare-card offer.** It is already a rarity offer and
  pays a Doubt that stays.
- **The 75 Gold-plus-curse options and the potions-plus-curse options.**
  Light curses for modest rewards are the intended shape.

Each option offering a choice of three must still be weighed on what it
offers: three Rares to choose from can beat one particular Rare. Randomizing
removes guaranteed access to one enabler; it does not by itself make a
reward smaller, which is why prices stay on the paid ones.

## Picks

1. **The table as written.**
   - **(a, default)** Build it.
   - (b) Build it, but keep one named card per character as a signature
     moment: Klee's Alice's Recipe, Varka's Jean+, Furina's Let the People
     Rejoice+ and Kokomi's Treatise+, each at the price above.
2. **Finale Rares.**
   - **(a, default)** 18 HP for a Rare relic in act 3 (Empty Throne, Endgame),
     as a price to test.
   - (b) Make them random relics at 12 HP, like act 2.
3. **Where the scene promises a kind of reward.**
   - **(a, default)** Keep the kind, randomly: Varka's "Request
     reinforcements" offers 3 random Uncommon Companions; Furina's "Cast the
     sequel" keeps 3 random Guest Stars (her core cards, no one guaranteed).
   - (b) Any Uncommon card for both, as first drafted.
