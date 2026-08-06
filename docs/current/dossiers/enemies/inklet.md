# Inklet — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Inklet`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `InkletsNormal` — spawns exactly **three** Inklets. The middle body is flagged as such at spawn time and starts its move cycle one step ahead of its siblings.
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Three moves, one branch point, and a hard alternation. Every Inklet's cycle is:

1. **Jab** — single-attack intent, one small hit.
2. **Whirlwind** — multi-attack intent shown as damage × 3; three small hits under one animation.
3. **Piercing Gaze** — single-attack intent, one large hit.

Wiring: **Jab → random branch → (Whirlwind *or* Piercing Gaze) → Jab → random branch → …** forever. Whirlwind and Piercing Gaze both return unconditionally to Jab, and only Jab feeds the branch. So an Inklet's turns strictly alternate *small filler* and *one of two payloads*; it can never play two payload moves back-to-back, and it can never chain two Jabs.

The branch is a flat coin flip between the two payloads, weighted 1:1. Both branches are nominally marked "cannot repeat," but because a Jab is always logged in between, the repeat-guard never actually suppresses either option — **Piercing Gaze can and does appear on consecutive payload turns.** Treat it as an independent 50/50 every other turn, per body.

Which foot the body starts on is the only per-body difference:

| Body | Turn 1 | Turn 2 | Turn 3 | Turn 4 | Turn 5 | … |
| --- | --- | --- | --- | --- | --- | --- |
| Left (outer) | Jab | 50/50 payload | Jab | 50/50 payload | Jab | alternating |
| **Middle** | **Whirlwind** | Jab | 50/50 payload | Jab | 50/50 payload | alternating |
| Right (outer) | Jab | 50/50 payload | Jab | 50/50 payload | Jab | alternating |

The middle Inklet's opener is fixed Whirlwind (not rolled), which means turn 1 is fully deterministic for the whole encounter: two Jabs and a Whirlwind, no variance. All the variance arrives on turn 2 and lands on the two outer bodies simultaneously.

There is one authoring wrinkle worth knowing for anyone modelling this: the encounter's starting state is **fixed per body, never randomized**. A second, unused init-branch exists in the data (it would have rolled Jab-up-to-twice against Whirlwind) but is not wired into the live machine.

**Piercing Gaze is deliberately hidden from the bestiary.** The bestiary entry advertises only Jab and Whirlwind, so a player consulting it will under-forecast the fight's ceiling by a wide margin — the 10-damage hit is a surprise by design.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per body) | 11–17 | 12–18 (*Tough Enemies* tier) |
| Jab damage | 3 | 4 (*Deadly Enemies* tier) |
| Whirlwind damage | 2, **three times** (6 total) | 3 × 3 (9 total) |
| Piercing Gaze damage | 10 | 11 (*Deadly Enemies* tier) |
| Slippery (combat start) | 1 stack | 1 stack (not ascension-scaled) |

HP is rolled per body and the game prefers **distinct** max-HP values across the enemy side when the band allows, so the three Inklets will normally show three different HP totals from within the band. Combined pool: **33–51 base** (typically ~42), **36–54** at the *Tough Enemies* tier. That is a small pool by Act 1 standards — the fight is not long.

Party-facing damage per turn, single-player, all three alive (base / *Deadly Enemies* tier):

| Turn | Composition | Total damage |
| --- | --- | --- |
| 1 | Jab + Jab + Whirlwind (fixed) | **12 / 17** |
| 2 | Jab (middle) + two payload rolls | best **15 / 22**, worst **23 / 26** |
| 3 | Two Jabs + one payload roll | **12 / 17** or **16 / 19** |
| 4 | Jab + two payload rolls | same band as turn 2 |

Worst realistic turn with all three alive is **two Piercing Gazes plus a Jab: 23 base, 26 at the Deadly tier** — a genuine spike for an early Act 1 room, arriving as soon as turn 2 and roughly a quarter of the time thereafter. Killing bodies collapses this quickly: each dead Inklet removes ~6–10 of the incoming per-turn total.

No Inklet ever gains Block, applies a debuff, buffs itself, summons, or reads its own HP. There are no thresholds, no enrage, and no revive. The kit is three attacks and one defensive passive.

## Gimmicks

- **Slippery (the headline).** Each Inklet applies 1 stack of a counter-style buff to itself as soon as it enters the room. While a stack is up, **any single instance of HP loss against that body is clamped to exactly 1**, and the stack is consumed by the first hit that gets damage past its (nonexistent) block. Net effect: the first damaging hit on each Inklet deals 1, full stop, and the second hit onward is normal.
- **Therefore: overkill is punished, multi-hit is king.** A 20-damage single strike into a fresh Inklet deals 1. A 3-hit, 2-damage attack deals 1 + 2 + 2 = 5 into the same body. Three bodies means three separate stacks to strip, so wide multi-hit and AoE clear this room several times faster than single-target burst — this is the archetypal "teach the player about hit count" Act 1 encounter, and it is one of the first four rooms a brand-new save is force-fed (the first-run room order pins `InkletsNormal` at normal-encounter index 3).
- **Chip damage is a resource.** Any 1-damage tick — a stray hit, a retaliate, an attack already reduced to near-nothing — is worth as much as a haymaker for stripping Slippery, so cheap throwaway damage has unusually high value here.
- **Blocking your way through does not strip it.** The stack only decrements on *unblocked* damage received by the owner, so the player cannot burn it off passively; it must be spent by an actual hit landing.
- **The hidden big hit.** Piercing Gaze at 10 (11) is not shown in the bestiary and roughly matches an outer Inklet's own max HP. Two of them in one turn is the fight's whole damage story.
- **Fragile bodies, front-loaded threat.** With 11–17 HP each and no defensive move beyond the one-shot Slippery, every Inklet is a one-card kill once its stack is gone. The fight's difficulty is entirely in the first two turns; from turn 3 on it is usually already won.

## Scaling by act / ascension

- **Act:** none. Inklet is Act 1 content only and reads no act index of its own; the only act-derived factor touching it is the multiplayer scaler below (Act 1 factor = 1.1).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 11–17 → **12–18** per body (+3 across the encounter).
  - *Deadly Enemies* tier: Jab 3 → 4, Whirlwind 2 → 3 per hit (6 → **9** total), Piercing Gaze 10 → 11.
  - Slippery is **not** ascension-scaled, the body count is **not** ascension-scaled, and the move wiring is identical at every ascension. The Deadly tier's largest proportional jump is Whirlwind (+50%), which is also the move the bestiary *does* show.

## Multiplayer / seat-count adjustments

- **HP scales by seats.** On entering combat with more than one player, each body's max HP is multiplied by (player count × act factor); Act 1 non-boss uses **1.1**. A 2-player Inklet sits at roughly 24–37 HP and a 3-player Inklet at roughly 36–56 — combined pools of about 73–112 and 109–168 respectively.
- **Slippery scales by seats too.** The stack count is multiplied by player count on application, so each Inklet carries **1 stack per player**: 2 stacks at two seats, 3 at three. The first *N* damaging hits on each body deal 1 apiece. Across three bodies at three seats that is **nine wasted hits** before the fight starts behaving normally — the multi-hit lesson gets proportionally harsher, not gentler, as the party grows.
- **Damage does not scale, but it is applied per seat.** Monster attacks resolve against every opposing player creature rather than picking one, so each Inklet's Jab hits everyone for its listed value and Whirlwind hits everyone three times. Per-seat incoming damage is therefore the same as the solo table above regardless of party size.
- **Block scaling is irrelevant here** — no Inklet move grants Block.
- Net effect at higher seat counts: the fight gets meaningfully longer on both axes (HP × seats × 1.1 *and* Slippery × seats) while per-player incoming damage stays flat. More turns alive means more payload rolls, so the expected number of Piercing Gaze turns the party eats rises roughly in step with seat count.

## Fight-class reasoning — `swarm`

What this fight demands per turn is **distributed kill throughput, not a defensive wall**: three separate low-HP bodies each carrying their own Slippery stack, so the correct play is to spread cheap, many-instance damage across all three rather than concentrate a big number into one. The Slippery passive is doing gimmick-shaped work, but it exists specifically to make single-target burst the wrong answer against a group — it is a multiplicity tax, and it scales with body count and seat count, which is the defining property of a swarm. Incoming damage is likewise swarm-textured: many small packets from several sources (12 fixed on turn 1, ~15–23 thereafter), where each kill immediately removes a chunk of the per-turn total, so tempo on offense *is* the defense. `gimmick` would over-weight Slippery and ignore that the room's ask is plainly "clear three bodies fast," and `spike` over-reads the twin-Piercing-Gaze turn, which is a real 23-damage threat but only reachable while all three bodies are still standing.
