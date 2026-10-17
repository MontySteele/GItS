# LAW

The rules that constrain future work: design, engineering and art. A line is
here only if it limits what new work may do. Shipped numbers and behavior live
in the YAML sheet and the code; status in `STATE.md`; open picks in
`QUEUE.md`; measurement method (Balance stage only) in `EXPERIMENTS.md`; who
decides what, and the working norms, in `CLAUDE.md`. The long version with
every provenance note is in git (`git show 764b98d5:docs/current/LAW.md`).

Changing this file is [USER]'s call.

## Pillars (a conflict resolves upward)

1. **Spire first.** This is a good StS2 mod that happens to be Genshin. StS2
   conventions (energy, rarity, intents, keyword style) win over Genshin
   fidelity when they conflict.
2. **Reactions are earned, not given** (Combat, below).
3. **Co-op is amplified, never required.** Every character clears solo.

A character's identity is not law: it lives in the character's brief, named
in `STATE.md`, and is revised there.

**Never added:** elemental resistance matrices; crit rate or crit damage as
stats; Energy Recharge or Elemental Mastery as numeric stats; stamina;
cooldowns; any open-world system.

## Combat: elements and reactions

- **No character card applies an off-element aura.** Off-element access comes
  only from Companions, a co-op partner, or a guest on Furina's stage, which
  costs a seat and a card. **Varka is the exception:** his own deck carries all
  five of his elements by design ([USER], 2026-10-15: "Varka has many
  'off-element' cards by design as his deck has anemo, pyro, hydro, electro and
  cryo in it").
- **Amplifiers are per-hit and consume the aura.** No reaction ever produces a
  persistent or compounding damage multiplier.
- **One aura per enemy, lasting 2 player turns,** refreshed by a same-element
  hit. Anemo and Geo leave no aura; they only trigger. Every reaction consumes
  its aura, Swirl and Crystallize included.
- **Frozen** is a per-creature counter that ticks down each turn. On a non-boss
  enemy it is −50% to its next action's damage, and the first Attack hit
  against it Shatters (direct HP damage; it cannot shatter the Freeze it just
  applied). In boss rooms only minions can be Frozen; anyone else gets
  Vulnerable instead.
- **Auras and Bombs land beside Artifact** without using a charge. Frozen and
  reaction-applied Vulnerable, Weak and Poison are real debuffs and Artifact
  negates them.
- **Hard crowd control is payoff-tier only.** No reaction and no Companion
  makes an intent-skip or stun at repeatable Common rates; a full stun costs
  at least what the base game charges and loses power with repeated use in a
  combat. Companions never source hard CC.
- **Reaction damage is credited to the player who triggered it.** Auras sit on
  shared enemies, so cross-player reactions need no special case.
- **Overload's splash, Swirl's flat 2 and Electro-Charged bypass Block** and
  are not modified by Strength or Vulnerable. Shatter is a separate bonus on
  the first Attack hit against a Frozen enemy.
- **Application cadence is set per character:** catalyst-grade (every attack
  applies, low numbers) or skill-grade (only some cards apply, higher
  numbers). The base Strike and Defend apply nothing for anyone.
- **Effects that empower another card or a guest boost numbers only,** never
  energy, draw or extra actions.

## Companions, shop and rewards

- **Companions are the mod's colorless content.** Treat them as the only
  colorless pool in design; in code the base pool is overridden only in the
  shop.
- **Companions route power through your character, never around it.** The
  delete-test always holds: remove your character's own cards from a winning
  deck and it must fall apart. A character may make Companions central only
  through its own enabling cards, which the delete-test removes.
- **Rarity:** a 4-star Companion is at most Uncommon power. A 5-star is a
  Rare, exactly one card per 5-star, and a support payoff (buff, amplify,
  aura), never its own scaling damage engine. The Featured Banner (per nation
  per run) gates 5-star availability; the designed roster may grow.
- **A character's personal-pool Companions are its kit** and may be
  deck-defining, within the rarity guardrails; the delete-test still governs
  them. They may also enter through an optional, declinable run-start offer.
- **The free Companion reward is enabler-grade and random,** about half from
  the character's nation. Its value is off-element access, so a weak roll is
  never a dead pick.
- **The shop sells two Companions, both Uncommon or higher:** one home-nation,
  one any nation. Price (50 / 75 / 150 by rarity, no colorless surcharge),
  the rarity floor and shelf order govern the shop together.
- **An empty Companion slot is left out,** never filled with a base colorless
  card.
- **Neutral energy, draw and deck-thinning are legal Companion utility** when
  one-shot, costed and Exhaust-gated.
- **Cycling engines are Uncommon or higher.** A card that replaces itself at no
  net energy or hand cost is a cycling engine, whatever else it does.
- **A character from an unreleased nation sits in the nation it operates in**
  until its home sheet exists.
- **Artifacts, if built, are relics with 2-piece set bonuses,** themed on
  reactions, not characters. No 4-piece sets, no stat rolls.

## Roster

- **A character may be both playable and a Companion card.**
- **Every character is built to the template:** an element and a cadence
  declared before card design; one signature subsystem; three archetypes that
  compete for card slots; a 78-card pool; its own relics and potions; two
  Ancient cards (one added by Darv's Dusty Tome, one replacing a starter card
  through Orobas's Archaic Tooth).
- **Co-op depth comes from multiplayer-only cards,** never from changes to a
  character's base kit, which plays the same solo and in co-op.
- **Official HoYoverse art may ship in a free, clearly unofficial public
  build; no HoYoverse audio ships.** The mod is never monetized or presented
  as official, and every image keeps its source row in `art/SOURCES.tsv`.
  Builds stay private until the distribution point is ruled
  (`review/active/distribution-readiness-2026-10-12.md`).
- **Naming:** constellation names for Rares and upgrades, talent names for
  relics, voice lines for flavor.

## Card authoring

- **True in-combat healing is Rare and Exhausts,** both together. Below Rare,
  sustain is Block or a buffer. A pet's own bar may be restored at any
  rarity. Potions and small relic trickles are exempt.
- **Ancient cards** (reached only through an act-2 Ancient, never rolled) may
  grant per-turn gains that their owner's resource rules otherwise ban: a
  bounded, opt-in, once-per-run spike. No other rarity, relic or event
  inherits this.
- **No strict domination between adjacent rarities:** a card must not be a
  strictly better copy of another at similar weight. Prefer base-game "twist"
  shapes over supersets.
- **Threshold cards pay a flat printed bonus once,** not a proportional read.
  Charge and meter bars are Uncommon or higher. On a Balance sheet, a
  threshold is never lowered.
- **At most two new keywords per character** beyond the shared element system.
- **Upgraded starter cards get a distinct name,** not a "+".
- **Copies inherit their printed bounds,** and copy effects never make an
  energy-positive loop.
- **An Ancient gap is fixed with real content,** never by removing the option.
- **The `register` column guides art selection only;** no engine reads it.

## Engineering

- **Every C# balance constant is classified, mirrored or unmirrored.** A
  mirrored constant matches tier0 and is parity-linted; a mismatch is fixed in
  both engines.
- **A shared-schema change** (a field read by both engines, or by the loader
  and codegen) updates every consumer in the same change, and the PR says so.
- **Versions are read live** from their source (`constants.py`,
  `release_info.json`). `manifest.json` is MAJOR.AUTO: MAJOR (`0.2`) moves
  only on [USER]'s release; AUTO is the commit count. Dirty builds add
  `+dirty`, Teyvat-frame dev builds `+proto`, staging builds `+next`, all as
  semver build metadata, never a `-` before the patch.
- **State-reading riders snapshot state at cast.** Rules read the resource,
  never its display.
- **Every meter is declared bounded or unbounded,** with any cap read from
  `constants.py`.
- **A structurally invisible defect gets a machine-readable list and a lint**
  (empty starting relics, pool rarity coverage, Ancient coverage, required
  nodes); the list checks itself for rot.
- **Look for an existing solution in BaseLib and the decompiled game before
  building infrastructure.** Derive from BaseLib abstractions, not raw game
  types. Other mods are reading material only; never copy their scenes, art
  or code.
- **Build output never goes under the game's `mods/` tree.** Custom models
  declare localization through `ILocalizationProvider.Localization`. An id is
  an API: changing one means sweeping its loc keys, asset paths, saves and
  epoch strings.

## Art and visuals

- **Ship pre-sized art,** with no runtime downscaling, except where a layout
  depends on a per-player count; then the bound is written down and asserted.
- **Visuals bind to slots and events, never to values:** a number a kit change
  moves must not be able to break a display.
- **Never write `Visuals.Scale`** (a sign flip inverts the hitbox). A mirror
  goes above the animated node. A node the bridge depends on has a boot check.
- **No Spine.** Rigs are Godot-native.
- **Art reuse:** a duplicated pick fails `art_lint` unless it is on the
  allowlist. Crop reuse is judged by eye. Environment art may serve as a card
  face when the place is central to the card.
- **Scale by real heights:** a character's size is its canon height over an
  adult's.

## Process

- **A watch item** names the mechanism, the quantity watched and the trigger.
  It does not come back until the trigger fires, and then it comes back with
  a reading.
- **A decision paper is self-contained;** it carries the context it needs.
