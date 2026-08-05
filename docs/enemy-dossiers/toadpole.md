# Toadpole — behavior dossier

- **Class:** `Toadpole`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0 — the alternate Act 1 biome, unlocked rather than default)
- **Encounter:** `ToadpolesWeak` — a *weak* (early-act) encounter that spawns exactly **two** Toadpoles, one flagged front and one flagged back. Toadpole appears in no other encounter.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Toadpole runs a three-move state machine with **zero randomness**. Every transition is a hard-wired follow-up; the only branch in the whole AI is a one-time positional check on the first turn. Once you have seen two turns you can predict the rest of the fight exactly.

The three moves:

1. **Spiken** — shows a *buff* intent. Plays a cast animation and gives **itself 2 Thorns**. No damage, no block.
2. **Spike Spit** — shows a *multi-attack* intent (damage × 3). **First strips its own 2 Thorns**, then lands three hits under a single spin animation.
3. **Whirl** — shows a *single-attack* intent. One hit.

Wiring is a closed loop: Whirl → Spiken → Spike Spit → Whirl → … forever. There is no exit, no HP threshold, no enrage, and no state that can be skipped.

The positional branch picks the entry point:

- **The front Toadpole starts on Spiken.**
- **The back Toadpole starts on Whirl.**

That offsets the two bodies by one step, so they are never in phase. Observed sequence:

| Body | Turn 1 | Turn 2 | Turn 3 | Turn 4 | Turn 5 | Turn 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Front | **Spiken** | Spike Spit | Whirl | Spiken | Spike Spit | Whirl |
| Back | **Whirl** | Spiken | Spike Spit | Whirl | Spiken | Spike Spit |

The consequence that matters is the Thorns window. Thorns is granted at the end of a monster turn and stripped at the start of that same body's *next* move, so it is live for exactly one player turn out of every three, per body — and because the two are offset, at most one Toadpole is spiked at a time:

| Player turn | Front spiked? | Back spiked? |
| --- | --- | --- |
| 1 | no | no |
| 2 | **yes** | no |
| 3 | no | **yes** |
| 4 | no | no |
| 5 | **yes** | no |
| 6 | no | **yes** |

So the fight is a rotating "don't punch that one" light, with one clean turn in every three where neither body is protected.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per body) | 21–25 | 22–26 (Tough-Enemies tier) |
| Whirl damage | 7 | 8 (Deadly-Enemies tier) |
| Spike Spit damage | 3, **three times** (9 total) | 4 × 3 (12 total) at the Deadly-Enemies tier |
| Spiken Thorns gained | 2 | 2 — **not** ascension-scaled |
| Spike Spit self-Thorns removed | 2 | 2 |
| Block | none, ever | — |

HP is rolled per body inside the band, and the game prefers a distinct max-HP value for each enemy on the side when the band allows — the two Toadpoles will normally show different HP totals. Combined pool: **42–50** base, **44–52** at the Tough-Enemies tier. That is a genuinely small pool; this is a first-or-second-room encounter.

Incoming damage per turn for the pair, from the offset table above (base / Deadly-Enemies tier):

| Turn | Front | Back | Pair total |
| --- | --- | --- | --- |
| 1 | Spiken (0) | Whirl (7 / 8) | **7 / 8** |
| 2 | Spike Spit (9 / 12) | Spiken (0) | **9 / 12** |
| 3 | Whirl (7 / 8) | Spike Spit (9 / 12) | **16 / 20** |
| 4+ | repeats the 3-turn cycle | | |

Average sustained output is ~10.7/turn base and ~13.3/turn at the Deadly tier, but it arrives in a lumpy 7 → 9 → 16 rhythm. Every third turn is roughly double the previous one, and it is telegraphed a full turn ahead by the deterministic loop. Kill either body and the survivor's contribution flattens to its own 0 / 9 / 7 (or 0 / 12 / 8) cycle.

## Gimmicks

- **Self-Thorns as a targeting puzzle (the headline).** Thorns here retaliates against *each attack hit received*, dealing its amount back to whoever swung. Two Thorns is trivial against one big hit and brutal against a multi-hit card: a five-hit flurry into a spiked Toadpole costs the player 10. The fight's real per-turn question is not "how much damage" but "which body, with which card shape."
- **The retaliation is not a loop.** The reflected damage is flagged as unpowered, so it does not re-trigger the player's own Thorns-style effects or take a hurt animation; it is a flat tax on the attacker.
- **The Toadpole spends its own buff to attack.** Spike Spit strips the 2 Thorns before hitting. Thorns is therefore self-limiting and cannot stack across cycles — it never exceeds 2, and it is always gone on the turn the multi-attack lands. This is the mirror-image of the usual "buff then cash in" pattern: the buff is defensive and the cash-in is offensive.
- **Thorns is a counter-type buff with no natural decay.** It does not tick down at end of turn; the only thing that removes it is the Toadpole's own Spike Spit. If a spiked body is killed before it spits, that instance simply never comes off.
- **Offset spawns make the tell rotational.** Front and back are the same monster with a different entry point. The player is never facing two spiked bodies, and never more than one turn away from a clean window.
- **Visual tell beyond the icon.** Spiked Toadpoles swap to an entirely separate "buffed" animation set — idle, hurt, attack and death all change while Thorns is up. The state is readable at a glance without checking power icons, which matters for an early-act teaching fight.
- **Cosmetic-only variation.** Each Toadpole randomizes its eye and body-pattern skin on spawn. No mechanical effect; it exists so the two identical bodies are visually distinguishable.
- Hits on it read as slime. No summons, no allies, no block, no debuffs applied to the player, no HP-threshold branch. Everything above is the whole kit.

## Scaling by act / ascension

- **Act:** none. Toadpole is Underdocks (Act 1) content only, and its numbers do not read the act index. The only act-derived factor that touches it is the multiplayer scaler below, which uses the Act 1 value of 1.1.
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 21–25 → **22–26** per body (+1 to the floor and ceiling; ~+2 across the pair).
  - *Deadly Enemies* tier: Whirl 7 → 8, Spike Spit 3 → 4 per hit (9 → 12 per turn). The peak turn goes 16 → 20.
  - **Thorns is not ascension-scaled.** It is 2 at every ascension level, which means the signature gimmick gets relatively *weaker* as the rest of the fight scales up.

## Multiplayer / seat-count adjustments

- **HP scales hard.** On entering combat with more than one player, enemy max HP is multiplied by (player count × an act factor); for Act 1 that factor is **1.1**. A 2-player Toadpole body sits at roughly 46–55 HP (2 × 1.1 × a 21–25 roll) and a 3-player body at roughly 69–83. Across two bodies: ~92–110 at two seats, ~139–165 at three.
- **Block scaling does not apply.** The multiplayer scaler inflates enemy *block*, and the Toadpole gains none — so the seat-count adjustment is pure health and nothing else on the enemy's defensive side.
- **Damage does not scale, but it is applied per seat.** Monster attacks target *all* living opposing player creatures rather than picking one, and the target list is refreshed between hits. Whirl hits **every** player for its listed damage; Spike Spit hits every player three times. Per-seat incoming damage is therefore identical to solo.
- **Thorns does not scale with seat count** and it retaliates only against the creature that actually swung — the reflect is 2 per hit no matter how many players are in the fight, and it lands on whichever player attacked.
- Net effect: at higher seat counts the fight gets *longer* (roughly 2.2× the pool at two seats, 3.3× at three) while per-seat damage and the Thorns tax stay flat. The gimmick dilutes: a bigger HP bar means more attack cards thrown per Thorns window in absolute terms, but the party's shared health total grows faster than the reflect does. Co-op Toadpoles are meaningfully easier per seat than solo ones.

## Fight-class reasoning — `gimmick`

The damage here is small and fully deterministic — a 7 / 9 / 16 loop against a 42–50 HP pool, telegraphed a turn ahead, with no block, no debuffs, and no burst that can plausibly kill a healthy Act 1 player. What the fight actually demands each turn is a targeting-and-card-shape decision: one of the two bodies is wearing 2 Thorns on a rotating schedule, so the player must either route damage into the unspiked one, spend the clean third turn on the spiked one, or knowingly eat 2 per hit — and multi-hit decks pay a much larger tax for getting that wrong than single-hit decks do. That read-the-buff-and-pick-a-target question is the entire encounter, which is `gimmick` by definition. `swarm` overstates two non-summoning bodies, `attrition` is wrong against a sub-50 HP pool that dies in three or four turns, and `spike` is wrong because the largest turn in the fight is 16 (20 at the Deadly tier) and arrives on a fixed, visible schedule.
