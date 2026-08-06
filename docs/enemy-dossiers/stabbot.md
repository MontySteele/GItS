# Stabbot — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Stabbot`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** none of its own. Stabbot has **no encounter that generates it** — it exists only as a `Fabricator` spawn inside `FabricatorNormal`, where it is one of the two members of the Fabricator's *aggro* spawn pool (the other is Zapbot). It is listed in that encounter's possible-monsters set for bestiary purposes only.
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The simplest state machine in the Act 3 construct family: **one move, wired to follow itself.** There is no randomness, no branch, no conditional, no opener exception. From the moment a Stabbot is on the board it shows the same intent every turn until it dies.

- **Stab** — displays a *single-attack* intent (damage number) **plus** a *debuff* intent, side by side. It attacks, then applies **Frail 1**.

That is the entire kit. The player never has to read a Stabbot's intent after the first time; the only question a Stabbot ever poses is *how many of them are there.*

**Arrival timing matters more than the pattern.** The enemy turn iterates a snapshot of the enemy list taken when that turn begins, so a Stabbot fabricated *during* the enemy turn does **not** act on the turn it appears. It drops into its slot (there is a scripted fall-in placement when it is added to the room), telegraphs Stab, and the player gets exactly one turn to remove it before the first stab lands. Every add is therefore a one-turn clock, and the fight is a question of whether the party's per-turn clear rate keeps up with the Fabricator's per-turn spawn rate.

**How Stabbots arrive (the Fabricator's side of the contract):**

- The Fabricator can fabricate only while **fewer than 4 living teammates** are on the board — four bot slots, hard cap.
- While under the cap it randomly picks (50/50) between **Fabricate** (spawns one *defensive* bot — Guardbot or Noisebot — **and** one *aggro* bot — Zapbot or Stabbot) and **Fabricating Strike** (attacks, then spawns one *aggro* bot). Either way, **one aggro bot per Fabricator turn**, every turn, until the board is full.
- The spawner **excludes whatever it spawned last** from the pool. With a two-entry aggro pool that makes the aggro spawns a strict alternation: Stabbot, Zapbot, Stabbot, Zapbot… A player who just saw a Zapbot arrive knows the next add is a Stabbot.
- At the 4-bot cap the Fabricator switches to Disintegrate (attack only) until a slot frees up — so **killing a Stabbot re-opens the spawner**.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 18–23 | **19–24** (Tough-Enemies tier) |
| Stab damage | 11 | **12** (Deadly-Enemies tier) |
| Stab Frail applied | 1 | 1 (no ascension scaling) |
| Block | — | never gains any |

HP is rolled inside the band per body, and the game prefers a distinct max-HP value per enemy currently on that side when the band allows — so simultaneous Stabbots will usually sit at different HP totals rather than dying to the same damage breakpoint.

**Frail is worth its own paragraph, because the stack count is a trap.** Frail multiplies block *gained* (from cards and from monster moves) by **0.75** — flat, regardless of how many stacks are on you. Stacks are a **duration counter**, not an intensity dial: 4 Frail is not 4× weaker block, it is the same 25% tax for longer. The counter ticks down once at the end of each enemy turn, and a debuff freshly applied to a player skips its next tick — so a single stab's Frail 1 survives through the player's following turn and expires at the end of the next enemy turn.

The consequence: **one Stabbot alone maintains ~100% Frail uptime** (it applies 1 per turn while the counter ticks 1 per turn). **Two or more Stabbots overshoot** — the counter accrues faster than it drains and Frail becomes a bank the player cannot clear by waiting, persisting for several turns even after the last Stabbot dies.

Damage feedback reads as armor rather than flesh — cosmetic, consistent with the Act 3 construct bestiary.

## Gimmicks

- **It is a minion, not a monster.** The Fabricator marks every bot it makes with a minion-style buff that makes the bearer a *secondary enemy*: a secondary enemy cannot sustain the combat by itself and dies out when no primary enemy remains. **Kill the Fabricator and every Stabbot on the board goes with it.** The corollary is the real lesson of the fight: HP spent on Stabbots is HP not spent on the only target that ends the encounter.
- **Its death does not end anything, and its death helps the enemy.** A Stabbot dying frees a bot slot, which un-gates the Fabricator's fabricate branch and lets it resume spawning instead of falling back to its attack-only move. Clearing adds is not progress toward victory; it is progress toward *more adds*.
- **The debuff is the payload, the damage is the pressure.** 11 is a middling Act 3 hit on its own, but the Frail rider means each Stabbot simultaneously deals damage and makes the answer to that damage worse. Two Stabbots on the board means block cards are permanently at 75% while ~22–24 raw damage per turn arrives on top of the Fabricator and whatever defensive bot is out.
- **No block, no buff, no scaling, no ramp.** A Stabbot on turn 10 is identical to a Stabbot on turn 1. Nothing about this enemy gets worse over time except its count.
- **Its intent is never hidden or misleading.** Unlike the Fabricator (whose Fabricating Strike is deliberately kept out of the bestiary listing), the Stabbot has exactly one publicly-shown move.

## Scaling by act / ascension

- **Act:** none. Stabbot is Act 3 content only, reachable only through `FabricatorNormal`. Its numbers do not read the act index; the act index enters only through the multiplayer scaler below.
- **Ascension:** two independent, tier-keyed bumps, both single-point.
  - *Tough Enemies* tier: HP band 18–23 → **19–24**.
  - *Deadly Enemies* tier: Stab 11 → **12**.
  - Frail amount does **not** scale. The spawn cadence, the 4-slot cap, and the alternation rule are **not** ascension-scaled either — ascension makes each bot marginally tankier and marginally sharper, but does not make the swarm denser.
- The Fabricator's own ascension bumps (bigger HP, harder Fabricating Strike and Disintegrate) change the fight around the Stabbot far more than the Stabbot's own two-point drift does.

## Multiplayer / seat-count adjustments

- **HP scales hard, and it scales on spawn.** Enemy max HP is multiplied by (player count × an act factor); for a non-boss Act 3 room that factor is **1.2**. Scaling is applied at creature creation, so **every fabricated Stabbot is scaled** — mid-combat adds are not cheap copies. A 2-player Stabbot is roughly **43–55 HP** (2 × 1.2 × an 18–23 roll) and a 3-player Stabbot roughly **65–83**. That is the single most important co-op fact about this enemy: at 1 player a Stabbot is a one-card problem; at 3 players it is a two-or-three-card problem arriving every other turn.
- **Damage does not scale, but it lands on every seat.** Monster attacks target all opposing player creatures rather than picking one, with the valid-target list refreshed per hit. Stab therefore hits **each** player for its listed 11/12 — the party takes 11 × seats per Stabbot per turn.
- **Frail lands on every seat too.** The debuff is applied to the full player-creature list, not to a single victim, so there is no "tank eats the debuff" play: every Stabbot Frails the whole party every turn.
- **Block scaling is irrelevant here** — Stabbot never gains block. (It matters enormously for its Guardbot slot-mate, which is fabricated alongside it.)
- Net effect at higher seat counts: the adds get 2.4×/3.6× tankier while the party's clear rate per player stays flat and the incoming damage-plus-Frail per seat is unchanged. The board therefore fills faster and stays full, which is precisely the state the Fabricator wants.

## Fight-class reasoning — `swarm`

Stabbot has no turn worth surviving and no ramp worth outlasting — 11 damage on a fixed loop is not a spike, and a 20-HP body is not an attrition pool. What it demands per turn is **board clearance under a spawn clock**: the Fabricator adds an aggro bot every single turn until four slots are full, each new Stabbot gives the party exactly one turn of grace before it starts stabbing, and killing one re-opens the spawner rather than closing the fight. That is the defining swarm question — can your per-turn removal rate (ideally AoE, and in co-op AoE that clears 43–83 HP bodies) outpace the generator's per-turn add rate — and Stabbot's low HP, zero defense, and identical repeating intent are exactly the properties that make it a unit of that arithmetic rather than a threat in itself. The Frail rider pushes toward `mixed`, but it is a tax that scales with *how many Stabbots you failed to kill*, so it reinforces the swarm read instead of competing with it; `attrition` would be the right call only if the correct play were to grind the adds, and it emphatically is not — the correct play is to ignore or AoE them and delete the Fabricator, whose death kills every bot on the board at once.
