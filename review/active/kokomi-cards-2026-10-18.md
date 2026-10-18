# Kokomi: every card placed, and what changes, 2026-10-18

This follows `review/active/kokomi-archetypes-2026-10-18.md`, where the user ruled three archetypes
(pick 1 (a)): **Grand Strategy** (plan a lot, win the morning), **Read the Tide** (answer intents,
turn Block into damage, not a turtle), and **the Shoal** (the "Silent-like Sting / Ward strategy").
Companions sit in the middle. Picks 2 and 3 were taken at their defaults and are reopened here
against the actual cards. The user's Exhaust question (2026-10-18: "we have plenty of cards that
exhaust, but no character that makes use of strong Exhaust synergies") is answered in sec.3,
because the Shoal is where it fits.

## 1. Where every card goes

Card texts are in `docs/prototype-surface.yaml`; the census is the archetypes paper's sec.1.

| Group | Count | Cards |
|---|---|---|
| **Grand Strategy** | 18 | Feint, Turning Tide, Breakwater, Press the Advantage, *Draft the Orders (new)*, Tideturn, Opening Gambit, Second Wave, Change of Plans, Pincer, *Undertide Lance (threshold)*, Following Current, Masterstroke, Sango Isshin, Shoal of Spears, Battle Formation, Nereid's Ascension, Grand Design |
| **Read the Tide** | 22 | Kelp Wall, Coral Crash, Undertow, *Coral Bulwark (intent)*, Brine Sting, Flank, Evening Watch, Prepared Retreat, Tide Wall, Undercurrent Snare, Drowning Pressure, Spearhead, Ambush, Riptide, War Council, Turnabout, Tidal Rebuke, Tidal Riposte, Sea's Reproach, At Water's Edge, Watatsumi's Grace, The Moon a Ship |
| **The Shoal** | 21 | Jellyfish Drift, Kurage's Wake, Watatsumi Drill, Bubble Ward, Shoal Call, Tidecleanse, Brine Spray, Kurage Barrage, The Shape of Water, Flotsam Surge, Sea Glass Harvest, Endless Shoal, Kurage Bloom, Kurage Canopy, Watchful Shoal, *Tidepool (new)*, *Receding Tide (new)*, *The Tide Returns (new)*, All Streams Flow to the Sea, Grand Strategist, Dawn Tide |
| **Companions** | 9 | Orders from the Shrine, Watatsumi Muster, Call the Generals, Sangonomiya's Orders, Treatise, and the four Gorou cards |
| **Co-op** | 5 | unchanged |
| **Glue** | 8 | Tidal Surge, Tidal Screen, Surging Shoal, Read the Field, Steady Tide, Resolve of Watatsumi, Riptide Ruin, Tamakushi's Wrath |

Each card is listed once: 18 + 22 + 21 + 9 + 5 + 8 = 83, the 78-card pool plus the five co-op cards.
Some cards serve two groups. Endless Shoal and Kurage Canopy (listed under the Shoal) turn
carried-out Plans into Stings and Wards, which makes them the Strategy–Shoal bridge. Treatise
(listed under Companions) also rewards planning. The pool stays 78 (20 / 38 / 20).

**A correction to the archetypes paper.** Placed card by card, only four of her 18 powers are truly
free-standing: Kurage Vanguard, Resolve of Watatsumi, Kurage Bloom and Watatsumi's Grace. The paper's
"about half" was too high. The "spam powers" feel comes from something else. Following Current,
Dawn Tide, Sea's Reproach, Tidal Riposte and At Water's Edge each pay off an action **every** Kokomi
deck already takes: carrying out a Plan, applying Hydro, applying Weak, blocking. They're archetype
cards whose condition is free, which is the same problem as the Plan-count payoffs. The fix is the
same too: the archetypes get enablers and payoffs that a deck has to build toward (below). Most of
those powers stay; they become rewarding once a deck leans their way.

## 2. The changes (six cards)

**Grand Strategy: make a heavy planning turn affordable, and reward going past normal.**
1. **Shell of Sanctuary → Draft the Orders** (Common Skill, 1): "Gain 5 [8] Block. The next card
   you plan this turn costs 1 less." This is the archetype's Common enabler. Shell of Sanctuary was
   plain Block with no reason to pick it over Coral Bulwark.
2. **Undertide Lance** (Uncommon Attack, 2) keeps its now-line ("Deal 9 [12] Hydro damage to ALL
   enemies"). Its Plan becomes "Deal 9 [12] Hydro damage to ALL enemies. If 3 or more Plans are
   carried out this turn, deal it twice." This is the first threshold payoff: it's better in a deck
   that writes three Plans than in one that writes one.

**Read the Tide: one more card that reads intents, at Common.**
3. **Coral Bulwark** (Common Skill, 1): "Gain 8 [11] Block. If an enemy intends to attack, gain 3
   more." It was plain Block. Now the archetype's Common Block looks at intents like the rest of it.

**The Shoal becomes the Exhaust archetype (sec.3).**
4. **Kurage Vanguard → Tidepool** (Uncommon Power, 1): "Whenever a card is Exhausted, gain 2 [3]
   Block." It's the Feel No Pain of the deck. Kurage Vanguard was a free-standing 4 damage a turn,
   and Dawn Tide and Following Current remain her other Hydro sources.
5. **Pearl Current → Receding Tide** (Uncommon Power, 2 [1]): "Whenever a card is Exhausted, draw 1
   card." It's the Dark Embrace of the deck. Pearl Current was a generic multi-hit.
6. **Suffocating Deep → The Tide Returns** (Rare Attack, 2): "Deal 3 [4] Hydro damage for each
   card Exhausted this combat." It's the Knife Trap of the deck. Suffocating Deep was one of eight
   Read the Tide Rares, the most of any group, so this evens the Rares out (Strategy 6, Tide 7,
   Shoal 4 plus the bridges).

Nothing else changes, and no number moves outside these six.

## 3. Exhaust, and why the Shoal

The user is right: in our five kits, 80 cards Exhaust and **none** rewards it (a search of every
row's text for "whenever … Exhaust", "Exhaust pile" and the like). The base game rewards it in the
Ironclad's archetype (Feel No Pain, Dark Embrace, Ashen Strike, Pact's End, Howl from Beyond), in
the Silent's Knife Trap, and in four relics (read from the decompile's `AfterCardExhausted`
users).

Kokomi's Shoal already Exhausts more than any deck in the mod, without trying:
- every Sting and Ward is Exhaust;
- every Inazuma Companion she generates is Ethereal, so it Exhausts at end of turn;
- Flotsam Surge's Dazed are Ethereal;
- Tidecleanse Exhausts Statuses and Curses.

So the three new cards pay off what the Shoal and her Companion middle already do. They give the
Silent-like deck its engine, the same way Knife Trap and After Image do for Shivs. That also covers
the Companion middle: a Companion-heavy Kokomi feeds Tidepool and Receding Tide through Ethereal.

**Loop check** (the standing rule: close a loop only if trivial to assemble). Receding Tide plus
Stings draws a card per Sting. Stings come only from generators, never from the deck, so the draw
is bounded by how many Stings the turn made. It is not a loop. If a seat finds one, the fix is a
per-turn cap, not a cut.

## 4. Read the Tide against the turtle guardrails

- **No new Block carry-over.** Watatsumi's Grace stays capped at "keep up to 10 [15]".
- **Every build-around wins by damage.** Turnabout, Tidal Rebuke, Tidal Riposte and Sea's Reproach
  all deal damage. The only Block-only Rare left is The Moon a Ship (Block plus Mend), which is a
  defensive card, not a win condition.
- **The clock is real.** The tier05 boss pools (`tier05/content/act*_pool.yaml`) give every boss
  but one 2 to 3 Strength per cycle and 170 to 510 HP, so a deck that only blocks loses to the
  ramp. The seat check stays: Read the Tide's normal fights should run no more than about one turn
  longer than base's.

## 5. Next

Build the six changes. Then run five Kokomi seats, briefed to draft toward an archetype (one lane
per archetype, two lanes free). Then a run of yours.

## Picks

1. **The six changes, as a set.**
   - **(a, default)** Build all six.
   - (b) Build the Strategy and Tide changes (1–3) only, and hold the Exhaust layer for a separate
     look.
2. **Exhaust payoffs count any card, or only her own.**
   - **(a, default)** Any card Exhausted, so Ethereal Companions, Dazed and partner-made cards
     count. That's simple and generous, and it ties in the Companion middle.
   - (b) Only Stings and Wards. That's tighter, but it shuts out the Companions.
3. **Picks 2 and 3 of the archetypes paper, now that the cards are on the table.**
   - **(a, default)** Confirm both. Stings keep their Plan lines (Endless Shoal and Kurage Canopy stay
     the bridge). Of the four free-standing powers, only Kurage Vanguard is replaced. Resolve of
     Watatsumi and Kurage Bloom stay as glue, and Watatsumi's Grace stays as Read the Tide's capped
     defence.
   - (b) Also repoint Kurage Bloom ("At the start of your turn, add a Sting to your Hand") to an
     Exhaust payoff.
