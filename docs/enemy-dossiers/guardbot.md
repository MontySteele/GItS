# Guardbot — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Guardbot`
- **Kind:** normal (non-elite, non-boss) — but never a starting monster; it only ever enters play as a Fabricator spawn
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `FabricatorNormal` only. The encounter generates exactly one Fabricator in the `fabricator` slot; the four surrounding slots (`bot1`, `bot2`, `bot3`, `bot4`) are filled at runtime by fabricated bots. Guardbot is one of the two **defense spawns** (the other is Noisebot); the two **aggro spawns** are Zapbot and Stabbot.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The simplest move machine in the family: **one state, self-looping, no randomness, no branches, no conditions.**

- **Guard Move** — shows a *defend* intent (the generic shield icon, no number). Plays a cast animation, then grants **15 Block to every Fabricator on its own side**.
- The state's follow-up is itself. There is no second move, no HP-threshold branch, no opener variant, no cooldown.

Three consequences worth writing down:

1. **The Guardbot never attacks.** Its lifetime damage output is zero at every ascension and every seat count. It contributes to the fight purely by moving HP-equivalent onto the Fabricator.
2. **It does not block itself.** The 15 Block goes to Fabricators only — the filter is by monster type, not "teammates" or "self." A Guardbot standing next to a dead-or-absent Fabricator does literally nothing on its turn. (In practice the Fabricator is always alive while a Guardbot exists — see *secondary enemy* below.)
3. **Slot order does not matter.** All creatures on a side have their Block cleared together at that side's turn start, before any of them act. So whether the Guardbot occupies `bot1` (acting before the Fabricator) or `bot4` (acting after), the 15 Block it grants is intact for the whole of the following player turn.

A monster added mid-turn does not act on the turn it spawned; a Guardbot fabricated during the enemy turn simply stands there telegraphing its shield until the next enemy turn.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 16–20 | **17–21** (Tough-Enemies tier) |
| Guard Move Block granted to the Fabricator | 15 | 15 (no ascension scaling) |
| Guard Move damage | — (none) | — |

HP is rolled inside the band per body, and the game prefers a distinct max-HP value per enemy currently on the side when the band still has unused values — two simultaneous Guardbots will normally sit at different HP totals.

Hits on it read as **armor** rather than flesh (cosmetic damage-SFX category), consistent with the rest of the Act 3 construct bestiary.

**The exchange rate is the number that matters.** A Guardbot costs 16–20 damage to remove and returns 15 Block per enemy turn to the Fabricator for as long as it lives. It pays for itself in roughly **1.3 turns** and is pure profit thereafter — which is the whole design. With two Guardbots up, the Fabricator's 150 HP body (155 at the Tough-Enemies tier) is effectively wearing +30 per turn.

The Block is granted **unpowered** (a non-card, non-move-flagged value). Two practical effects:

- It is not multiplied by monster-side Strength/Dexterity-analogue power modifiers.
- It is **not** touched by the multiplayer block scaler (see below), which only scales *powered* card-or-monster-move block. This is unusual for the act and is the single most important co-op fact about this enemy.

## Gimmicks

- **Block laundering (the headline).** The Guardbot converts its own small HP bar into recurring mitigation on a much larger body. Damage you spend killing the Guardbot is damage not spent on the Fabricator, and damage you spend on the Fabricator is partly refunded to it every turn the Guardbot lives. That is a target-priority puzzle rather than a survival puzzle.
- **Secondary enemy.** The Fabricator applies a minion marker to everything it spawns. A creature carrying that marker is a *secondary enemy*: it **cannot keep the fight alive on its own** and dies automatically once no living primary enemy remains. So killing the Fabricator wins the fight outright regardless of how many bots are standing — and every point of damage put into a Guardbot is, in the limit, wasted. The marker also survives its owner's death and does not itself trigger a fatal cascade, so the cleanup is the "no primary enemy alive" rule doing the work, not a death trigger.
- **Overkill is wasted, and so is *any* kill.** Because the Guardbot is disposable, the Fabricator can simply build another. The only permanent progress in the fight is damage on the Fabricator.
- **Spawn cadence and the field cap.** The Fabricator keeps fabricating only while **fewer than 4 creatures on its side are alive** (that count includes the Fabricator itself, i.e. while fewer than 3 bots are up). At or above that line it switches to a repeating single attack and stops summoning. Its Fabricate move spawns **one defense bot and then one aggro bot**; its Fabricating Strike spawns one aggro bot. Field cap is therefore the Fabricator plus 4 bots, exactly matching the four bot slots.
- **The anti-repeat filter is effectively neutered for defense spawns.** The Fabricator remembers only the *single* most recently spawned bot and excludes it from the next roll. Because a Fabricate always rolls the defense bot immediately after the previous aggro bot was recorded, the remembered bot is almost always an aggro type when the defense roll happens — so nothing is filtered out and Guardbot vs. Noisebot is a fair coin flip every time, **including back-to-back Guardbots**. Two Guardbots on the field simultaneously (30 Block/turn on the Fabricator) is a normal, not a freak, outcome.
- **It has no bestiary quirks of its own** — no summons, no powers applied at spawn (contrast Zapbot, which arrives pre-charged), no debuffs, no enrage, no death rattle. The single Guard Move is the entire kit.
- **Read it against its sibling.** Noisebot (the other defense spawn) taxes the player's *deck*; Guardbot taxes the player's *clock*. Drawing Guardbot is the "this fight will take two more turns" outcome; drawing Noisebot is the "your next two draws are worse" outcome.

## Scaling by act / ascension

- **Act:** none. Guardbot is Act 3 content only, it reads no act index, and the only act-derived factor that touches it is the multiplayer HP scaler below.
- **Ascension:**
  - *Tough Enemies* tier: HP band 16–20 → **17–21**. That is the only ascension change it receives.
  - *Deadly Enemies* tier: **no effect** — it has no damage value to raise.
  - The 15 Block is **not** ascension-scaled, and the defense-spawn odds are not ascension-scaled.
  - Net: the Guardbot is one of the few enemies in the act that is very nearly ascension-invariant. The Fabricator fight gets harder at higher ascension almost entirely through the Fabricator's own numbers (155 HP, 21 Fabricating Strike, 13 Disintegrate) and through the aggro bots, not through this one.

## Multiplayer / seat-count adjustments

- **Its HP scales; its output does not.** On creature creation with more than one player, enemy max HP is multiplied by (player count × an act factor); for a non-boss Act 3 room that factor is **1.2**. A 2-player Guardbot sits at roughly 38–48 HP (2 × 1.2 × a 16–20 roll) and a 3-player Guardbot at roughly 58–72. Scaling is applied at creation, so **every fabricated body is scaled** — mid-combat spawns are not cheap.
- **The 15 Block does not scale.** The multiplayer block scaler only multiplies *powered* card-or-monster-move block; the Guardbot's grant is flagged unpowered and slips past it. At 3 players the Guardbot is roughly 3.6× as expensive to remove while still returning exactly 15 Block per turn — its exchange rate collapses from ~1.3 turns to ~4 turns to break even. **In co-op the Guardbot is a worse investment for the enemy team and a worse target for the player team simultaneously**: it stops being worth killing at all, and the correct play converges hard on ignoring it and racing the Fabricator.
- **Nothing it does is per-seat.** It has no attack and no debuff, so the "monster moves hit every player creature" rule never engages. It is the one bot in the encounter whose threat profile is completely unchanged by seat count.
- **It still soaks AoE.** In co-op the encounter fields more scaled bodies for longer; any card that hits all enemies is spending a large share of its output on creatures that will evaporate for free when the Fabricator dies.

## Fight-class reasoning — `gimmick`

The Guardbot asks the player for nothing defensively — it deals zero damage, applies no debuff, and adds no status to the deck — so on the per-turn demand curve it contributes no mitigation requirement at all. What it demands instead is a *decision*: every turn it lives, 15 of your damage on the Fabricator is refunded, and every turn you spend removing it is a turn the Fabricator spends free, all while the minion rule means anything you kill that is not the Fabricator was arithmetically wasted. That is a rules-modifier enemy, not a pressure enemy — it changes what "correct targeting" means rather than what "surviving the turn" means, and in co-op the change is severe enough to flip the answer (kill it in single-player, ignore it at 3 seats). `attrition` would be the tempting second choice, but attrition implies a sustained tax on the player's HP and resources, and this thing never touches either; `swarm` belongs to the encounter as a whole (the Fabricator's own dossier is `mixed`), not to this unit.
