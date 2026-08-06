# Snapping Jaxfruit — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `SnappingJaxfruit`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `SnappingJaxfruitNormal` — tagged `Mushroom`, and it is **not** a solo fight. The encounter always spawns exactly two bodies: one Snapping Jaxfruit and one **Flyconid**. The Jaxfruit never appears in any other encounter list, and no other act references it.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

This is the simplest move machine in the bestiary: **one state, one move, wired to itself.**

- The state machine is constructed with a single move state (`ENERGY_ORB_MOVE`) which is also the initial state, and that state's follow-up is itself.
- The machine only transitions after a first move has been performed, and the transition target is the same state. There is no random branch, no repeat guard, no HP threshold, no enrage, no alternate opener.

So the intent is **Energy Orb every single turn, forever, from turn 1**, and it is 100% predictable from the moment combat starts.

The intent icon is a **combined attack + buff** display: a single-attack intent showing the damage number, plus a buff marker. The buff half is the Jaxfruit buffing *itself*, not its partner — the player sees "it will hit me for N and get stronger" every turn.

Per-turn resolution order matters and is fixed:

1. Deal the attack.
2. **Then** gain +2 Strength.

Because the buff lands *after* the hit, the number shown on the intent for turn *N* is already the post-buff value from turn *N−1*. The displayed intent number does include the Jaxfruit's current Strength — the intent's damage calculation runs the same damage-modification path as the real hit, so what you read is what you take (before your own Vulnerable/Weak/block).

The Jaxfruit is a stationary plant. It has no attack animation, only a cast; it plays a looping idle hum from the moment it enters the room until it is removed, which is the audio tell that it is still alive.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 31–33 | **34–36** (Tough Enemies) |
| Energy Orb damage (turn 1) | 3 | **4** (Deadly Enemies) |
| Strength gained per turn | +2 | +2 (**not** ascension-scaled) |
| Block | — | it never gains block, ever |

Effective Energy Orb damage by turn, before player-side modifiers:

| Turn | Strength going in | Base damage | Deadly-Enemies damage |
| --- | --- | --- | --- |
| 1 | 0 | 3 | 4 |
| 2 | +2 | 5 | 6 |
| 3 | +4 | 7 | 8 |
| 4 | +6 | 9 | 10 |
| 5 | +8 | 11 | 12 |
| 6 | +10 | 13 | 14 |
| 8 | +14 | 17 | 18 |
| 10 | +18 | 21 | 22 |

Cumulative damage taken if it is simply ignored: 15 by end of turn 3 (base), 35 by turn 5, 64 by turn 8, 105 by turn 10. The ramp is linear and **unbounded** — there is no cap on the Strength stack and no condition that ever removes it.

Encounter partner, for context on the real per-turn load (Flyconid, base / Deadly-Enemies tier): 47–49 HP (51–53 at Tough Enemies); a Smash for 12/11; a spore attack for 9/8 that also applies 2 Frail; and a spore skill that applies 2 Vulnerable with no damage. Vulnerable multiplies damage received by 1.5×; Frail multiplies block gained by 0.75×. Both of those land on the party from the Flyconid and both make the Jaxfruit's escalating orb strictly worse — a turn-6 orb under Vulnerable is 19–21 damage from an enemy the player may have written off as chip.

## Gimmicks

- **The whole enemy is one gimmick: an unbounded self-Strength escalator on a fragile body.** 31–33 HP is the smallest health pool in its encounter and near the floor for Act 1; the design contract is explicit — you are *meant* to be able to kill it quickly, and the +2/turn is the price of not doing so.
- **Nothing turns the ramp off.** No cool-down turn, no "recharge" state, no self-damage, no threshold at which it stops. Strength accrues on the turn it attacks, which is every turn.
- **It never blocks and never debuffs.** All of its output is raw damage, and all of its defense is the player's willingness to spend removal on the *other* enemy first.
- **The buff intent is a real telegraph, not flavor.** Because attack-then-buff is the fixed order, a player who reads intents sees the damage number climb by exactly 2 (or 2 at any ascension) every turn, with no variance to hide behind.
- **The orb visual retargets to the local player.** In co-op the projectile VFX is aimed at whoever is looking at the screen; that is cosmetic only and does not describe who takes the damage (see below).
- No summons, no allies of its own, no death rattle, no revive, no HP-threshold branch.

## Scaling by act / ascension

- **Act:** none. Act 1 content exclusively; the numbers do not read the act index. The only act-derived factor that touches it is the multiplayer scaler below (Act 1 factor = 1.1).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 31–33 → **34–36**. That is roughly one extra turn of survival for a mid-power Act 1 deck, which is exactly the resource the fight is measuring.
  - *Deadly Enemies* tier: Energy Orb base damage 3 → **4**. This shifts the entire ramp table up by 1 at every turn, not just turn 1.
  - The **+2 Strength per turn does not scale with ascension.** The slope of the escalator is constant across the whole ladder; ascension only moves the intercept and the kill deadline.

## Multiplayer / seat-count adjustments

- **HP scales hard.** Enemy max HP is multiplied by (player count × act factor), and the Act 1 factor is **1.1**. A 2-player Jaxfruit sits at roughly **68–73** HP (2 × 1.1 × a 31–33 roll), a 3-player one at roughly **102–109**; at the Tough-Enemies tier, ~75–79 and ~112–119. Its defining fragility is therefore substantially *undone* in co-op — the same escalator now sits behind a health bar that takes two to three times as long to remove.
- **Damage does not scale, but it is applied per seat.** The Energy Orb is built to target *all* opposing player creatures, with the target list refreshed per hit. Every player takes the full listed number each turn — the damage is not split. Party-wide damage per turn is therefore (ramp value × seat count), so at 3 players the turn-5 orb is 33 points of party damage at base, 36 at the Deadly-Enemies tier.
- **The Strength gain is seat-count independent.** It is not on the list of powers that scale with player count, so the slope stays +2/turn at any seat count while the HP wall grows — the ramp table above is unchanged, it just runs for more turns.
- **Block scaling is irrelevant here** — the Jaxfruit gains no block, so the multiplayer block multiplier never fires on it.
- Net effect: co-op makes this enemy meaningfully more dangerous than its single-player profile suggests. Same escalator, same slope, 2–3× the time to shut it off, and every tick charged to every seat.

## Fight-class reasoning — `gimmick`

What this enemy demands per turn is not mitigation, it is a **kill-order decision made correctly on turn 1**: the Jaxfruit is the softest target on the field (31–33 HP) and the only one whose threat grows without bound, while the Flyconid in front of it is the bigger body with the scarier printed numbers. The entire fight is that one puzzle — focus the 3-damage plant before the 12-damage mushroom, or pay a linearly compounding tax for the rest of the combat — and a player who solves it sees a trivial encounter while a player who reads intent numbers greedily sees a 17-damage orb on turn 8 through Vulnerable. `spike` is wrong because there is no single burst turn to block for; the curve is a smooth ramp with no peak. `attrition` is wrong because the intended answer is a fast removal, not sustained throughput — and the Jaxfruit's own health pool is far too small to grind against. `mixed` would be defensible at the *encounter* level (the Flyconid contributes a genuine debuff-and-chip layer), but the Jaxfruit's own contribution to the demand curve is a single solve-me rule, so `gimmick` is the honest label for this body.
