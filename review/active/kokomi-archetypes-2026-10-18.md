# Kokomi: what her deck is building towards, 2026-10-18

The user, after a co-op run:

> "she seems to have a healthy conceptual foundation but it never really congealed in a way that
> felt good. I never really had a clear sense of what my deck was supposed to be building towards
> besides 'spam powers so good numbers happen.' I don't think that her unique character mechanics
> (Plan) need to change, but I think we need to do a design round on her card pool to go over her
> intended play patterns and archetypes and see what it is she's intended to feel like."

This paper does that design round at the level of direction: which archetypes she has, what a turn
in each looks like, and which cards belong to each. Plan, the Bake-Kurage, the starter and the
Casket stay as they are. A card-by-card paper follows once the map is ruled.

## 1. Where the pool is now

Her draftable pool is 76 cards, 20 Common / 38 Uncommon / 18 Rare (`docs/prototype-surface.yaml`,
`character: kokomi`). Here's each card sorted by what it rewards (a card can sit in two):

| Theme | Cards | Examples |
|---|---|---|
| Plan count and order (the Tactician) | 17 | Feint, Breakwater, Tideturn, Second Wave, Opening Gambit, Battle Formation, Nereid's Ascension, Grand Design, Shoal of Spears, Sango Isshin |
| Stings and Wards (the Shoal) | 12 | Jellyfish Drift, Kurage's Wake, Shoal Call, Kurage Barrage, The Shape of Water, Watchful Shoal, Endless Shoal, Kurage Bloom |
| Weak and Vulnerable | 9 | Undertow, Drowning Pressure, Spearhead, Suffocating Deep, At Water's Edge, Sea's Reproach |
| Reading enemy attacks (Counter, Intent) | 8 | Kelp Wall, Brine Sting, Flank, Tide Wall, Prepared Retreat, Turnabout |
| Inazuma Companions | 8 | Orders from the Shrine, Watatsumi Muster, Sangonomiya's Orders, Call the Generals, the Gorou cards |
| Co-op | 5 | Coordinated Strike, Joint Orders, Tactical Relay, Sangonomiya's Counsel, Kurage's Mercy |
| Block into damage | 4 | Coral Crash, Tidal Rebuke, Tidal Riposte, Watatsumi's Grace |
| Reactions | 3 | All Streams Flow to the Sea, Grand Strategist, Dawn Tide |
| **Generic: good in any deck, points at nothing** | **16** | Coral Bulwark, Shell of Sanctuary, Tidal Surge, Surging Shoal, Undertide Lance, Riptide Ruin, Tamakushi's Wrath, Kurage Vanguard, Resolve of Watatsumi |

What the table says:

1. **Eight themes over 76 cards, so none has a spine.** A base character runs about three
   archetypes over 85 cards. Kokomi's next four themes after the top two are 3 to 9 cards each: too
   thin to draft into, too many to ignore. A draft is then mostly the generic sixteen plus whatever
   theme cards show up, which plays as "good numbers".
2. **The biggest theme doesn't ask you to build anything.** Every Kokomi deck plans one or two
   cards a turn, so a card that pays "per Plan waiting" or "per Plan carried out" pays in any of her
   decks. The Tactician payoffs reward playing Kokomi at all, not committing to a plan-heavy deck.
3. **The powers aren't too many; they point nowhere.** She has 18 powers in 76 cards. The base five
   have 17 to 20 in 85 (`game_ref/role_tempo_canon.json`), so the count is normal. But about half of
   hers are free-standing value that works anywhere: Kurage Vanguard (4 damage a turn), Resolve of
   Watatsumi (2 Strength), Kurage Bloom (a Sting a turn), Watatsumi's Grace (keep Block). With nothing
   for a deck to aim at, the best play is to stack them. That is "spam powers so good numbers happen".
4. **The two loops the user named on 2026-10-13 aren't two different turns.** "Archetypes centered
   around Plans vs reaction-driven Sting effects, with Companion cards in the middle." Stings have
   Plan lines too, and the Sting cards mostly don't care about reactions. So a Shoal turn and a
   Tactician turn look the same: play some cards, plan some cards.

## 2. Proposed map: three archetypes, three different turns

The rule for each archetype: **it plans for a different reason.** Plan stays the shared verb, and the
archetype is why you use it.

**A. The Grand Strategy: plan a lot, then win the morning.** A turn that looks quiet (block,
write three or four Plans) followed by a morning that ends the fight. This is the brief's "she wins
the fight before it starts". To make it a real build, its payoffs must need more Plans than a normal
deck writes: thresholds ("if 3 or more Plans were carried out") and multipliers on one big Plan (Second
Wave, Opening Gambit, Masterstroke). It also needs ways to afford a heavy planning turn (Grand Design,
War Council's Energy, Treatise's draw). Build-arounds: Nereid's Ascension, Battle Formation,
Masterstroke. *Feel: the slow, satisfying setup and the big reveal.*

**B. Read the Tide: answer what the enemy is about to do.** Plans that read intents and attacks:
Flank, Brine Sting, Tide Wall, Undercurrent Snare, Turnabout, Prepared Retreat. Block that turns into
damage: Coral Crash, Tidal Rebuke, Tidal Riposte. Weak and Vulnerable as the control layer. This
archetype absorbs the Counter, Block-into-damage and Debuff themes (21 cards today), which already
share a turn: look at the intents, pick the answer, let them hit the wall. Build-arounds: Turnabout,
Tidal Riposte, Sea's Reproach. *Feel: the tactician who has already seen your move.*

**C. The Shoal: play now, play many.** Stings and Wards are free plays, and this archetype is the one
that mostly does **not** plan. It wins through many small hits in one turn, and its Hydro sets up
reactions for the partner or for Companions. That makes it the reaction archetype the user named, so
the three Reaction cards fold in here. Build-arounds: Watchful Shoal, The Shape of Water, Endless
Shoal. *Feel: a flurry of jellyfish.*

**The bridge, and the middle.** The A–C bridge already exists and is good: Endless Shoal and Kurage
Canopy turn carried-out Plans into Stings and Wards. Inazuma Companions stay in the middle as the
user ruled: every archetype can take them, and Crystal Collapse and Treatise reward them. The co-op
five stay as they are.

**What moves.** The generic sixteen are where the room comes from. Each is rewritten to point at one
archetype, or cut for a card that does. The free-standing powers get the same treatment, except two or
three kept as glue, the way the Ironclad keeps a Strength power. Target shape, close to a base
character: about 18 cards per archetype (with 2 or 3 build-around Rares each), about 8 Companion
cards, the 5 co-op cards, and about 10 glue cards. The pool stays 78 (20 / 38 / 20), including the
two Ancients.

## 3. What this does not change

Plan, the Bake-Kurage, the open Plan (flip a waiting Plan to its now-line), the starter deck, the
Tamakushi Casket, the Ancients, her relics and potions, and her story are all unchanged. Numbers stay
as they are; the card paper sets them.

## 4. Next

The card paper: each of the 76 cards placed in A, B, C, Companion, co-op or glue, with a rewrite or a
replacement for every generic card and free-standing power, under the target shape above. Then a
five-seat round and a run of yours.

## Picks

1. **The archetype map.**
   - **(a, default)** Three archetypes (Grand Strategy, Read the Tide, the Shoal), with Companions in
     the middle and the co-op five as they are.
   - (b) Four: Weak and Vulnerable stays its own archetype, separate from Read the Tide.
   - (c) Two, as named on 2026-10-13: Plans vs Stings, with Read the Tide's cards split between them.
2. **The Shoal and planning.**
   - **(a, default)** Stings and Wards keep their Plan lines. The Shoal plans less by choice, and the
     bridge cards stay meaningful.
   - (b) Stings and Wards lose their Plan lines, so the Shoal is the one archetype that never plans.
     That's cleaner, but it costs the bridge.
3. **The free-standing powers.**
   - **(a, default)** Rewrite all but two or three to point at one archetype.
   - (b) Keep them all as glue and fix only the thin themes.
