# Klee and Furina: their own relics and potions (paper)

**Ask ([USER], 2026-09-27):** "I think that we're now at the point where we can
look into character-specific ones for Klee and Furina, and consider them for
Kokomi later once the character identity solidifies and the card pool is
handled. Co-op relics and potions can be a later item entirely."

**Stage:** Paper, ruled; to be built. The numbers are first drafts.

**Ruled 2026-09-27: all four picks at their defaults, with the two Rare potions
raised.** [USER]: "I mostly like 711 and the defaults - the Rare potions look a
bit undertuned to me relative to the effects. In Klee's case, a Set Off card
already pops all mines on a boss, so the potion just reads 'get one free Set
Off' as a Rare. In Furina's case, the numeric value of 'each performer performs
twice at the end of the turn' sounds a bit low - perhaps it should instead read
'each performer performs twice right now'."

So Jumpy Juice doubles every Bomb, which no card does, and Encore Elixir acts
now, twice. Both faces are changed in the tables below.

## What they have today

Klee and Furina own no relic or potion beyond their starter and their Ancient
upgrade. Both borrow the Silent's pools (`InheritedSilentRelics.cs`;
`PotionPool => SilentPotionPool` in `Klee.cs` and `Furina.cs`):

- **Relics:** Ring of the Snake (never reachable), Tingsha and Tough Bandages
  (discard payoffs), Twisted Funnel (Poison), Paper Krane, and Ninja Scroll
  (Shivs). Helical Dart and Snecko Skull were already dropped. Half of these
  pay off mechanics neither character has.
- **Potions:** Poison Potion, Cunning Potion (Shivs) and Ghost in a Jar.
- **Ancients:** both need repair.
  - Klee's Dodoco Tales does nothing beyond her starter under her ruleset. Its
    opening three Sparks are switched off, because a free bank would hand her
    many-small-bombs plan its first turn before any Bomb had gone off
    (`UpgradedStarterRelics.cs`; `BACKLOG.md`).
  - Furina's The Curtain Never Falls is built on her retired Spotlight kit.

## The base game's shape

This comes from a census of the v0.111 decompile. Every base character's own
pool is the same:

- **8 relics:** 1 Starter, 1 Common, 2 Uncommon, 3 Rare, 1 Shop.
  - The **Common** is a small plus to the character's core number: Snecko
    Skull (+1 Poison), Data Disk (+1 Focus), Fencing Manual (Forge 10).
  - The **Uncommons** each serve one plan.
  - The **Rares** bend a rule: Emotion Chip, Lunar Pastry, Charon's Ashes.
  - The **Shop** relic hands out a free opening resource or doubles one
    mechanic: Ninja Scroll, Runic Capacitor, Brimstone.
- **3 potions**, one each at Common, Uncommon and Rare:
  - Common: a refill of the character's resource (Star Potion, Focus Potion).
  - Uncommon: a burst of its mechanic (King's Courage, Potion of Capacity).
  - Rare: one big rule-bending turn (Essence of Darkness, Cosmic Concoction).

The proposal gives each of ours exactly that: seven new relics beside the
starter, three potions, and the Ancient repaired. It replaces the Silent borrow
(pick 1).

## Klee

Her rules: Bombs grow 4 a turn, only Set off fires them, and Sparks come only
from explosions. Her plans are Cook (one big Bomb), Spray (many small ones) and
React (a companion's aura). Her weakness is Block on demand.

| Tier | Name | Effect (draft) | Serves |
|---|---|---|---|
| Common | Dodoco Charm | Whenever you place a Bomb, it is 1 bigger. | All plans (the Snecko Skull slot) |
| Uncommon | Clover Charm | Whenever one of your Mines goes off, gain 3 Block. | Mines; her weakness |
| Uncommon | Fresh Catch | At the start of each combat, apply Hydro to a random enemy. | React: one free aura a fight |
| Rare | Alice's Guidebook | At the start of your turn, your largest Bomb grows 3 more. | Cook |
| Rare | Fireworks Stand | Whenever one card sets off 3 or more Bombs, gain 1 energy. | Spray |
| Rare | Alice's Teapot | The first Bomb you set off each turn reacts as if its enemy had Hydro. | React without a companion |
| Shop | Dodoco Army | At the start of each combat, place a Mine 2 on ALL enemies. | Hallways (the Ninja Scroll slot) |

| Tier | Potion | Effect (draft) |
|---|---|---|
| Common | Bottled Sparks | Gain 3 Sparks. |
| Uncommon | Blasting Powder | Every Bomb on every enemy grows 6. |
| Rare | Jumpy Juice | Double every Bomb on every enemy. |

**Ancient (Dodoco Tales), repaired:** "Whenever a Bomb goes off, gain 1 Spark.
The first time each turn, gain 2 instead." That is one extra Spark a turn, all
of it earned, with no opening bank.

Notes:

- **Alice's Teapot** answers the React supply problem from the seat rounds
  without changing rule 5, which you kept. It is a Rare discovery rather than a
  default.
- **Jumpy Juice** doubles every Bomb on every enemy. No card does that; the
  nearest is Alice's Recipe, which doubles growth. It is a Cook payoff that
  still needs her Set off card, so rule 7 stands. (It set every Bomb off
  before [USER]'s ruling, which read as one free Set off.)

## Furina

Her rules:
- Up to three performers sit in seats.
- The front one absorbs hits and regains 1 Fanfare a turn.
- Raise fills the back one, and Spend pays from the back one.
- A performer at 0 Bows, acting once more as it leaves.
- Performers behind the front fade above 5.

Her plans are the Salon (summon and defend), the Ovation (read a fat bar) and
the Guest Cast (Hydro and reactions). Her weakness is a big single hit, and an
empty stage.

| Tier | Name | Effect (draft) | Serves |
|---|---|---|---|
| Common | Opera Glasses | Your Usher starts each combat at 5 Fanfare instead of 3. | All plans |
| Uncommon | Stagehand's Gloves | Whenever a performer Bows, gain 3 Block. | Salon; her weakness |
| Uncommon | Guest Book | The first Guest Star you summon each combat arrives with 3 more Fanfare. | Guest Cast |
| Rare | Grand Theater Program | The applause no longer fades. | Ovation (breaks rule 12) |
| Rare | Curtain Call Bouquet | A performer that Bows acts twice as it leaves. | Expend (bends rule 9) |
| Rare | Palais Ledger | A Spend your back performer can't cover is paid by the performers in front of it, back to front. | Spend (bends rule 8) |
| Shop | Opening Night | At the start of each combat, summon a random performer behind your Usher. | Every fight's opening (the Ninja Scroll slot) |

| Tier | Potion | Effect (draft) |
|---|---|---|
| Common | Bottled Applause | Your back performer gains 6 Fanfare. On an empty stage, a random performer arrives holding it. |
| Uncommon | Curtain Water | Each of your performers gains 4 Fanfare. |
| Rare | Encore Elixir | Each of your performers acts twice, now. |

**Ancient (The Curtain Never Falls), rebuilt for the Stage:** "Start each
combat with Usher at 3 Fanfare. Your front performer regains 2 Fanfare at the
start of your turn instead of 1, from your first turn." It upgrades rule 4, as
the base Ancients upgrade their starter's one number. The name and art stay. It
no longer shares a relic with the Spotlight kit. Ethereal Spotlight leaves her
pool under the Stage, where nothing can use it.

## The build, after the picks

- Relic icons and potion art go through the art pipeline, as the cards did.
- Tips: each new relic and potion gets its tip, and the seat glossary is kept in
  step.
- Tests: C# tests for each effect, plus a pool test that the Silent borrow is
  gone under the arms, if pick 1 is (a).
- Kokomi keeps the Silent borrow until her review pass designs her own set.
- Then a seat round. Relic and potion offers are random, so the seats also get
  the new relics given at embark, to see them in play.

## Picks

1. **Scope.**
   - **(a, default)** Each gets a full pool of its own in the base game's shape
     (8 relics, 3 potions), and the Silent borrow goes.
   - **(b)** Add the new relics beside the borrow.
   - **(c)** Relics only for now; keep the Silent potions.
2. **Klee's set:**
   - **(a, default)** as drafted.
   - **(b)** as drafted without Alice's Teapot; React stays companion-only.
3. **Furina's set:**
   - **(a, default)** as drafted.
   - **(b)** as drafted without Grand Theater Program; the fade stays
     unbreakable.
4. **The Ancients:**
   - **(a, default)** repaired as drafted.
   - **(b)** Dodoco Tales keeps its opening three Sparks; the Spray concern is
     accepted for an Ancient.
