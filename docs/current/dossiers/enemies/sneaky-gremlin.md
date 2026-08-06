# Sneaky Gremlin — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `SneakyGremlin`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `GremlinMercNormal` — the encounter generates **only** a Gremlin Merc at combat start (slot `merc`). Sneaky Gremlin (slot `sneaky`) and Fat Gremlin (slot `fat`) do not exist until the Merc dies.
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Where it comes from

Sneaky Gremlin is never on the board at the start of any fight. It is one half of the spawn wave the Gremlin Merc leaves behind. The Merc enters combat carrying a "surprise" buff; when the Merc dies that buff (a) blocks combat from resolving even though the board is momentarily empty, and (b) adds **both** a Sneaky Gremlin (`sneaky`) and a Fat Gremlin (`fat`) to the combat.

The two spawns are complementary and deliberately opposed:

- **Fat Gremlin** carries every coin the Merc stole and spends its two turns running for the exit. It has no attack whatsoever.
- **Sneaky Gremlin** carries nothing and does exactly one thing forever: hit you.

So Sneaky Gremlin's whole design role is to be the **cost of chasing the loot**. It is the reason the Fat Gremlin's escape window is expensive rather than free.

## Intent pattern

Sneaky Gremlin runs a two-state move machine with **zero randomness**. There is no roll, no HP threshold, no conditional branch, no reaction to player state — the sequence is identical in every run.

1. **Spawned (Stun intent)** — plays a wake-up animation and flips the model's internal "awake" flag. Mechanically a **no-op**: no damage, no block, no power. The awake flag only selects which hurt animation plays (asleep-hurt vs awake-hurt). Deterministic follow-up → Tackle.
2. **Tackle (single-attack intent)** — one attack for **9** damage. Its follow-up state is *itself*, so from here the enemy telegraphs and performs Tackle every single enemy turn until it dies.

A monster added mid-turn does not take a turn on the turn it appeared; it stands on the board displaying the intent it will perform on the enemies' *next* turn. Because the move machine also refuses to transition before its first move has been performed, the wake-up turn is always spent and can never be skipped.

| Timing | Sneaky Gremlin state | Intent shown |
| --- | --- | --- |
| Player turn on which the Merc died | spawned, has not acted | **Stun** |
| Next enemy turn | performs wake-up (nothing happens) | intent flips to **Attack 9** |
| Player turn | awake, killable | **Attack 9** |
| Every enemy turn thereafter | Tackle for 9 | **Attack 9** |

The practical read: the player gets **one completely free turn** after the spawn wave lands, and then eats 9 per turn until the body is gone.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 10–14 | 11–15 (*Tough Enemies*) |
| Tackle damage (every turn once awake) | **9** | **10** (*Deadly Enemies*) |
| Hits per attack | 1 | 1 |
| Block gained | **none** | none |
| Debuffs applied | **none** | none |
| Buffs / self-scaling | **none** | none |
| Free turns granted on spawn | 1 (the stun/wake-up turn) | unchanged |

HP is rolled inside the band, preferring a max-HP value distinct from the other enemies on its side where the band allows — so in the paired spawn it will usually read as a visibly different HP number from the Fat Gremlin.

Companion numbers, since this enemy is never fought alone:

| Fat Gremlin (slot `fat`) | Base | Tough-Enemies tier |
| --- | --- | --- |
| HP | 14–17 | 14–18 |
| Damage | none | none |
| Turns before it escapes with the party's gold | 2 | unchanged |

| Gremlin Merc (slot `merc`) | Base | Tough-Enemies tier |
| --- | --- | --- |
| HP | 47–49 | 51–53 |
| "Gimme" | 7 × 2 hits | 8 × 2 |
| "Double Smash" | 6 × 2 hits, then Weak 2 | 7 × 2, then Weak 2 |
| "Hehe" | 8, then +2 Strength to self | 9, then +2 Strength |

The Merc's cycle is fixed (Gimme → Double Smash → Hehe → repeat) and each of its moves also steals up to 20 gold per player, so the size of the Fat Gremlin's pot is a function of how long the Merc lived.

## Gimmicks

- **It has no gimmick of its own.** No block, no buff, no debuff, no summon, no threshold, no enrage, no escape, no gold interaction. Read in isolation it is the plainest possible statline: small body, fixed attack, forever.
- **The gimmick is positional.** Its value to the encounter is entirely that it arrives *simultaneously with* the Fat Gremlin and shares the player's two-turn heist window. The Fat Gremlin punishes you for killing the thing that is hitting you; the Sneaky Gremlin punishes you for chasing the thing that isn't.
- **One guaranteed grace turn.** The stun/wake-up turn is unconditional and cannot be shortened, which is what makes the loot chase possible at all: the party's first post-Merc turn is completely free of incoming damage.
- **Damage-to-HP ratio is unusually aggressive for Act 1.** A 10–14 HP body that deals 9 per turn will out-trade almost any single card left unanswered, but it dies to one competent hit. The correct answer is always "remove it", never "block it down" — there is nothing to grind.
- **Nothing it does gets worse over time.** Tackle does not escalate, does not multi-hit, and gains no Strength. The fight's difficulty curve after the Merc dies is flat and fully readable from turn one.
- **The wake-up is a genuine tell, not just flavour.** The one turn of Stun intent is the game telling the player exactly how much slack they have to spend on the Fat Gremlin before the bill starts.

## Scaling by act / ascension

- **Act:** none. Sneaky Gremlin is Act 1 content only and none of its numbers read the act index. The only act-derived factor that touches it is the multiplayer HP scaler below (Act 1 factor = **1.1**).
- **Ascension:**
  - *Tough Enemies* tier: HP band 10–14 → **11–15** (a flat +1 to both ends of the band). Damage unchanged at this tier.
  - *Deadly Enemies* tier: Tackle **9 → 10**. HP unchanged at this tier. This is unusual for the gremlin trio — the Merc and the Fat Gremlin read only the Tough-Enemies tier, so Sneaky Gremlin is the only member of the encounter whose *damage* moves on the Deadly tier.
  - At both tiers combined: an 11–15 HP body dealing 10 per turn.
  - The one free wake-up turn is **not** ascension-scaled and is never removed.

## Multiplayer / seat-count adjustments

- **HP scales per seat; damage does not.** On entering combat with more than one player, enemy max HP is multiplied by (player count × act factor), and the Act 1 factor is **1.1**. A 2-player Sneaky Gremlin sits at roughly **22–31 HP** (2 × 1.1 × a 10–14 roll) and a 3-player one at roughly **33–46**. Its Tackle stays at 9 (10 on the Deadly tier) regardless of seat count.
- **The attack is untargeted and lands on the whole opposing side.** Monster attacks resolve against every opposing creature rather than picking a victim, so Tackle is effectively **9 damage to each player, every turn** — party-wide damage output multiplies with seat count while the enemy's own damage number never changes.
- Net effect per seat: the body gets ~2.2× / ~3.3× harder to remove while the cost of *not* removing it goes up in lockstep. Two seats means roughly 18 party HP per turn out of a body that now needs a real card to kill instead of a chip hit — this is the member of the trio that scales worst for the party.
- **It has no per-player powers.** Unlike the Merc (which applies a separate thievery counter to each player) and the Fat Gremlin (which carries a separate heist counter per victim), Sneaky Gremlin holds no per-seat state at all.
- **It is the seat-count reason the heist gets harder.** With more seats, both spawns' HP inflate against the same two-turn escape clock, and the tax for splitting damage is now 9 to every seat rather than 9 total.

## Fight-class reasoning — `swarm`

Per turn, Sneaky Gremlin demands exactly one thing and never varies it: **remove a small body before its flat 9 lands again**. There is no telegraphed burst to prepare for, so `spike` is wrong; nothing escalates and the body dies far too fast for a grind, so `attrition` is wrong; the enemy itself has no mechanic to solve, so `gimmick` belongs to its Fat Gremlin twin and not to it. What it actually asks for is target-priority and kill-throughput against one of two bodies that appear on the same turn — cheap-body clearing pressure, with an untargeted attack that hits every seat — which is the `swarm` demand curve in miniature, and the label that keeps its per-turn ask (damage to clear bodies, not mitigation) legible to Track B.
