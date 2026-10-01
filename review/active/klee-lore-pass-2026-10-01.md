# Klee lore pass (2026-10-01)

[USER] asked for a check for "blinding gaps in her lore regarding the Knights
of Favonius, Hexenzirkel / Little Hexenzirkel / Hexerei ties that aren't
properly expressed through her current card pool, or anything else, as well
as ... generic-sounding card names that could be reflavored."

Read against: her 78 cards, her 5 co-op cards and her Ancient
(`docs/prototype-surface.yaml`, `proto_ko_` rows); her 13 Klee-only
companion cards (`personal_pool: klee`); the brief's own lore audit
(`review/active/klee-brief-2026-09-01.md` §2, §7). Facts come from a sourced
fact sheet built today; the main sources are the game's own text mirrored at
gi.yatta.moe (her profile, stories and voice lines), plus event guides for
Luna III (v6.2, Hexerei) and Luna VII (v6.6, the Little Hexenzirkel).

## 1. The verdict: no blinding gap in the people; the gap is in the names

**The people are covered, mostly through her companion cards.**

| Lore thread | Where it lives now |
|---|---|
| Knights of Favonius | Jean — Lion's Fang (Rare stand-in), Kaeya, Noelle, Diona, Barbara, Fischl and Sucrose stand-ins; Sorry, Jean...; Favonius Escort; Grounded; Fish Blasting's Confiscated; the co-op Rare Knights of Favonius |
| Alice and the Hexenzirkel | Alice's Recipe, Alice's Detonator, Alice's Introduction Magic, her Ancient; Nicole — Ladder of Divine Ascent (the first playable Hexenzirkel member, v6.6) |
| Little Hexenzirkel (v6.6) | Prune, Qiqi, Sayu and Yaoyao as Klee-only companions; Witches' Circle and Coven Errand |
| Hexerei (v6.2) | Boom Badge (her new kit's Boom Badges); Sparks banking to 3 |
| Her kit | Kaboom! (Ka-pow!), Jumpy Dumpty, Sparks 'n' Splash, Pounding Surprise (starter relic), Sparkling Burst, All of My Treasures!, Chained Reactions, Explosive Frags, Blazing Delight |

**Three soft spots:**

- **Her own cards barely say who she is.** The people live on companion cards.
  Her 78 personal cards name Jean once, Alice three times, Dodoco five times,
  and nobody else. Albedo, her caretaker and the person she is closest to
  after Alice, is not named on any of her own cards. The coven is named once
  ("Witches' Circle", which is not what the game calls it).
- **About twenty names are generic.** Some are generic in Klee's voice, which
  is right for her: Pop!, Bang Bang!, Run Away!, Look Out!, Sit Tight. Others
  read like any character's card: Ammo Scavenging, Rapid Fire, Flash Point,
  Split Charge, Hair Trigger, Blast Shield, Return to Sender, Shrapnel,
  Aftershock, Careful Arrangement, Big Bounce, Bottomless Bag, Countdown.
  The Fuse names (Chain Fuse, Quick Fuse, Stoke the Fuse) are fine: Alice
  taught her "how to choose fuses" (her character story 5).
- **Vermillion Pact has no referent** (the earlier audit's point). There is
  no confirmed lore tie to the Crimson Witch set either.

**Unused canon names:** her constellations Exquisite Compound (C3) and Nova
Burst (C5); Sparkborne Magic (her Hexerei passive); Boom-Boom Strike (the
charged attack her Boom Badges power); Hexerei: Secret Rite (the party bonus
for two or more Hexerei characters); Witch's Homework (Alice's trials for
her, v6.2); Albedo's door sign "Experiment in Progress" (it means "come back
later, Klee"); Windtrace (Mondstadt's hide-and-seek); Kaeya's "Favonius
Survival Rulebook", written for her; and the lizard tails Albedo told her
dry into gunpowder.

## 2. The renames (names only; no text or number changes)

Each new name was checked against the sheet and the code for collisions; none
is in use. Pounding Surprise is not available: it is her starter relic.

| Card | Rename to | Why it fits the card |
|---|---|---|
| Patience, Klee! (end of turn, no Set off: largest Bomb grows) | **Experiment in Progress** | Albedo's sign: wait, don't touch, it's still cooking |
| Witches' Circle (Companion played: place a Bomb) | **Little Hexenzirkel** | the coven by its real name; companions are her friends |
| One More Charge (grows 8; if 20 or more, draw 1) | **Witch's Homework** | Alice's trials: reach the bar, get the reward |
| Bang Bang! (Set off, 8 damage, place a Bomb 4) | **Boom-Boom Strike** | her v6.2 charged attack; pairs with Boom Badge |
| Vermillion Pact (one reaction spreads to every Bomb) | **Sparkborne Magic** | her Hexerei passive; replaces the referent-less name |
| Careful Arrangement (merge all Bombs into one) | **Exquisite Compound** | C3; a compound is things combined |
| Big Bounce (overflow damage hits another enemy) | **Nova Burst** | C5; the blast that spills over |
| Hiding Spot (Block, a Mine on a random enemy) | **Windtrace** | Mondstadt's hide-and-seek, where she hides and traps |
| Ammo Scavenging (place a Bomb; draw per Bomb set off) | **Lizard-Tail Gunpowder** | Albedo's tip; scavenged powder, which is what the card does |
| Run Away! (Block, more if a Bomb went off) | *keep* | the brief maps her title Fleeing Sunlight here |
| Duck and Run (Block 7, Set off) | **Survival Rulebook** | Kaeya's rules for dodging Jean, which are mostly "blow it up, then hide" |

Ten renames, one deliberate keep. Each move puts a canon name where the
card's effect already is, so no player has to relearn a card.

**Not renamed, on purpose:** Half a Mountain (the Red Knight story: she
reshaped the Stormbearer Mountains); The Big One; Fish Blasting, Fish Fry and
Fish-Flavored Bait (her hobby, her catch and her dish); Sorry, Jean...;
Where Did I Put It?; the Dodoco cards (five is plenty; the earlier audit
flagged the count).

## 3. One co-op name

Hexerei: Secret Rite turns on when two or more Hexerei characters share a
party. That is a co-op rule in the source game, and our Varka is Hexerei too
(game8's list). Her co-op Rare **Sparks for Everyone** ("the first time each
turn one of your Bombs goes off, each other player gains 1 Energy") could be
named **Secret Rite**. Sparks for Everyone is a good name already, so this is
a taste call.

## 4. Left for the status-and-dedupe paper

- **Albedo's stand-in has no Klee hook.** "Albedo — Tectonic Tide" deals 4 to
  an enemy whenever a reaction happens; the brief planned "Isotoma reads
  explosions", the man who cleans up after her. That is a text change, so it
  belongs with the next card batch.
- **Return to Sender, Rapid Fire, Flash Point, Split Charge, Hair Trigger,
  Blast Shield, Shrapnel, Aftershock, Countdown and Bottomless Bag** keep
  their names for now. Several are dedupe candidates; renaming a card that
  may be cut is wasted work.

## Picks

1. **The ten renames in §2.** (a, default) all ten; (b) a subset (name the
   ones to drop); (c) none.
2. **Sparks for Everyone → Secret Rite.** (a, default) keep Sparks for
   Everyone; (b) rename.
3. **Albedo's stand-in re-hook** goes into the status-and-dedupe paper (a,
   default), or stays as is (b).
