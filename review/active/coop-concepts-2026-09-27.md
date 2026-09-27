# Co-op concepts: each character's team role (paper)

**Ask ([USER], 2026-09-27):** "start looking more carefully at
character-specific multiplayer concepts, like Furina sharing Fanfare or Klee
providing DEF shred or energy restoration analogs as they do in Genshin."

**Stage:** Paper, ruled. The four cards below are to be built, and the first
two-seat co-op round tests the co-op cards.

**Ruled 2026-09-27, all four picks at their defaults.** [USER]: "Sparks for
Everyone may be too strong (in a deck that's actively trying to farm sparks
anyway, this reads 'give all other players +1 energy per turn') but might also
be fine at 2 cost. Otherwise it sounds good. I'm fine with these defaults.
Likewise I think giving Kokomi a Rare + Exhaust co-op heal is also fine."

So Sparks for Everyone keeps cost 2 at every level. Its upgrade is Innate, not
cost −1, and the co-op seat round watches it for strength. Kokomi's pair,
including a Rare ally heal that Exhausts, is designed in her review pass.

## What the base game does

Every base character has **five** multiplayer-only cards, and the colorless pool
has eleven more. This comes from a census of the v0.111 decompile: every class
flagged `CardMultiplayerConstraint.MultiplayerOnly`. Nearly all of them fall into
a handful of team roles:

| Role | Base examples |
|---|---|
| Give an ally Block | Lift, Rally, Constellation |
| Give an ally energy or draw | Believe In You (2 energy, cost 0), Energy Surge, Huddle Up, Plot |
| Buff an ally's damage | Blaze (5 Strength), Coordinate (5 temporary Strength) |
| A debuff that only an ally's hits cash in | Flanking and Knockdown (x2 from allies), Tag Team, Underworld |
| Take hits for an ally | Tank, Intercept, Demonic Shield |
| Gain from what an ally does | Sneaky (Block per ally Attack), Beacon of Hope |

Ours have three each (the 2026-09-25 co-op set in
`review/records/coop-set-2026-09-25.md`, #661). Two more per character brings
them level with the base game.

## What already works across players

- **Elemental reactions should already cross players.** An aura is a power on
  the enemy (`klee-mod/KleeCode/Powers/AuraPower.cs`). A reaction fires on the
  element of whoever deals the hit (`ElementOf(cardSource, dealer)`), not on who
  applied the aura. So Furina's Hydro on an enemy followed by Klee's Pyro Attack
  should Vaporize.
  - This is read from the code, not yet seen in play. The first co-op seat round
    checks it.
  - If it holds, it is the most Genshin-like interaction the roster has, and it
    needs no new card.
- **The existing co-op set:**
  - Klee's allies can set off her Bombs: Pass the Match, and Knights of Favonius.
  - Klee shields an ally from her largest Bomb: Hide Here!.
  - Furina's stage shields allies: Guest of Honor, and Share the Spotlight.
  - Furina's stage gains from ally Attacks: The People of Fontaine.
  - Kokomi's Plans give allies Block, draw and damage.

## The gap, character by character

- **Furina.** Her Genshin job is party-wide damage, driven by Fanfare that the
  whole party's HP swings build. Ours only shields allies and feeds on their
  Attacks; no card turns her Fanfare into ally damage.
- **Klee.** Her Genshin team gifts are DEF shred from her mines (C2) and energy
  for the party (C6). Ours shares her Bombs and gives Block, but nothing shreds
  for allies and nothing gives energy.
- **Kokomi.** Her Genshin job is healing and steady Hydro. Healing is legal only
  on a Rare that Exhausts (`LAW.md`, content authoring), and the rest belongs to
  her own review (see pick 4).

## Proposed cards

Numbers are first drafts, priced against the base cards named beside them.

| Character | Name | Cost | Type | Rarity | Face (draft) | Priced against |
|---|---|---|---|---|---|---|
| Furina | Raise a Toast | 1 | Skill | Uncommon | Another player gains temporary Strength equal to your front performer's Fanfare, up to 6. | Coordinate (5 for 1) |
| Furina | The Crowd Roars | 2 | Power | Rare | Whenever another player loses HP, your front performer gains 1 Fanfare. | People of Fontaine (1 per ally Attack) |
| Klee | Shrapnel | 1 | Skill | Uncommon | Place a Mine 4. While an enemy holds your Mine, other players' Attacks deal 50% more damage to it. | Flanking (x2 for allies, cost 2) |
| Klee | Sparks for Everyone | 2 | Power | Rare | The first time each turn one of your Bombs goes off, each other player gains 1 energy. (Upgrade: Innate.) | Believe In You (2 energy once), Energy Surge |

Notes:

- **Raise a Toast** is Furina's burst in one card: the stage's Fanfare becomes
  an ally's damage for a turn. It reads the bar without spending it, so her
  stage is not punished for helping.
- **The Crowd Roars** is her Genshin Fanfare source: HP swings on the party
  charge the stage.
  - It rewards the pair when her partner takes hits, and it pairs with Guest of
    Honor, which moves those hits onto her stage.
  - Only HP loss counts, not gains, because healing is rare in this game.
- **Shrapnel** is a Flanking that Klee's Mines carry. A Mine goes off just
  before its enemy attacks, so the shred lasts exactly the players' turn, as
  Flanking's does. It is cheaper than Flanking, and weaker (x1.5).
- **Sparks for Everyone** is her C6. One energy per ally per turn is strong, so
  it is a Rare Power at cost 2. The Bomb has to go off, so she still has to play
  her own game.
- **Kokomi's pair** waits for her review (pick 4).

## The first co-op seat round (no pick; it runs once the harness lands)

Two blind seats, Klee and Furina, play at A0 through the new `embark --coop`
(branch `coop-seats`). The round:

- checks cross-player reactions;
- checks the six existing co-op cards, dressed in with `give_card` if the
  draft does not offer them;
- reports what played well, what did not, and what to change, as today's seat
  rounds did.

The four cards above are built only after the picks, and then tested in a
second co-op round.

## Picks

1. **Direction.** (a, default) Each character's co-op cards take the team role
   they play in Genshin: Furina buffs damage, Klee shreds and gives energy,
   Kokomi heals and sustains. They grow to five cards, as the base characters
   have. (b) Keep three each and only repair what the co-op round finds.
2. **Furina's pair.** (a, default) Raise a Toast and The Crowd Roars as drafted.
   (b) Raise a Toast only. (c) Neither.
3. **Klee's pair.** (a, default) Shrapnel and Sparks for Everyone as drafted.
   (b) Shrapnel only; energy for allies is too strong. (c) Neither.
4. **Kokomi.** (a, default) Her co-op pair is designed in the Kokomi review and
   polish pass, which is the next kit job. A real ally heal is on the table
   there, as a Rare that Exhausts. (b) Design her pair now, with Block and
   Hydro only and no healing.
