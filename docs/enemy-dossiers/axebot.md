# Axebot — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Axebot`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `AxebotsNormal` — a single-slot encounter (`front`) that spawns exactly **one** Axebot. The plural name is a tell: the fight is one body at a time, but you will fight three of them.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Axebot runs a three-state move machine with **zero randomness**. Every transition is a hard-wired follow-up, so the intent shown is always fully determined.

The three moves:

1. **Boot Up** — shows a *defend* intent and a *buff* intent together. Gains Block and gains Strength.
2. **Hammer Uppercut** — shows a *single-attack* intent and a *debuff* intent together. One heavy hit, then applies Weak and Frail.
3. **One-Two** — shows a *multi-attack* intent (damage × 2). Two hits, one animation.

Wiring: Boot Up → Hammer Uppercut → One-Two → Hammer Uppercut → One-Two → … forever. **Boot Up has no inbound edge**, so once the machine leaves it, it can never return. Boot Up is only ever reachable as an *initial* state.

Which state the machine starts in depends on whether this body is the original or a replacement:

- **The original Axebot starts on Hammer Uppercut.** It never plays Boot Up at all. Turn 1 is the heavy hit + Weak + Frail; thereafter it alternates One-Two / Hammer Uppercut for the rest of its life.
- **A respawned Axebot starts on Boot Up.** It spends its first turn blocking and buffing, then falls into the same Uppercut/One-Two alternation.

So the observed sequence across a whole fight is:

| Body | Turn 1 | Turn 2 | Turn 3 | Turn 4 | … |
| --- | --- | --- | --- | --- | --- |
| #1 (original) | Uppercut | One-Two | Uppercut | One-Two | alternating |
| #2 (respawn) | **Boot Up** | Uppercut | One-Two | Uppercut | alternating |
| #3 (respawn) | **Boot Up** | Uppercut | One-Two | Uppercut | alternating |

A monster that spawns mid-turn does not act on the turn it appeared, and a replacement created during the player's turn immediately rolls and displays its Boot Up intent. Practically: kill the Axebot on your turn, and you see the new body standing there telegraphing "block + buff" before your next turn begins.

## Numbers

| Value | Base | Deadly-Enemies tier |
| --- | --- | --- |
| Starting HP roll (per body) | 70–78 | 76–86 (Tough-Enemies tier; independent bump) |
| Boot Up Block | 10 | 15 |
| Boot Up Strength gain | +3 × multiplier (see below) | +4 × multiplier |
| One-Two damage | 9, **twice** | 10, twice |
| Hammer Uppercut damage | 12 | 14 |
| Hammer Uppercut Weak | 2 | 2 (no ascension scaling) |
| Hammer Uppercut Frail | 2 | 2 (no ascension scaling) |

HP is rolled per body inside the band, and the game prefers a distinct max-HP value per enemy on the side when the band allows — each respawn therefore re-rolls its own HP rather than inheriting the previous body's.

**The Strength multiplier is the interesting number.** Boot Up grants `base Strength gain × (2 − remaining stock)`. The original body carries 2 stock, so its multiplier would be zero — which is exactly why it is routed away from Boot Up entirely. The first respawn carries 1 stock (multiplier ×1) and the second carries 0 stock (multiplier ×2). Strength does not carry across bodies — each replacement is a fresh creature — but the escalating multiplier bakes the ramp in anyway.

Resulting effective damage (base / Deadly-Enemies tier), before Weak/Frail and before any player modifiers:

| Body | Strength | Hammer Uppercut | One-Two (per hit × 2) | One-Two total |
| --- | --- | --- | --- | --- |
| #1 | 0 | 12 / 14 | 9 / 10 | 18 / 20 |
| #2 | +3 / +4 | 15 / 18 | 12 / 14 | 24 / 28 |
| #3 | +6 / +8 | 18 / 22 | 15 / 18 | 30 / 36 |

Total health pool across all three bodies: **210–234** base, **228–258** at the Tough-Enemies tier — a normal-fight nameplate hiding an elite-sized bar.

Weak reduces the affected creature's damage output to 75%; Frail reduces block gained to 75%. Both are 2-turn counters. Because Hammer Uppercut lands every *other* turn and applies 2 turns of each, uptime on both is effectively **continuous** from the fight's first turn onward — the refresh always arrives before the counter runs out.

## Gimmicks

- **Stock / respawn (the headline).** The Axebot enters combat carrying 2 stacks of a counter-style buff that acts as spare bodies. On death, if stacks remain, a brand-new Axebot is added to the same slot with one fewer stack, plays a respawn animation, and takes over. That buff also explicitly **prevents combat from ending** while stacks remain, so there is no way to "win early" by killing the visible body — the fight is three sequential Axebots, full stop.
- **Death is a reset that costs you tempo.** Killing a body doesn't relieve pressure so much as re-time it: the replacement spends a turn gaining Block and Strength, so the player's reward for a kill is one calmer turn followed by a permanently harder enemy.
- **Overkill is wasted.** Because each body is a fresh creature with a fresh HP roll, damage that overshoots a kill does not carry into the next body. Big single-turn burst is structurally punished; consistent, right-sized damage is rewarded.
- **The double debuff is the real damage.** Weak + Frail with ~100% uptime means the player is fighting a ~230-HP pool at 75% offense while defending at 75% block efficiency. The Axebot's raw numbers are unremarkable for Act 3; the debuff tax is what makes the arithmetic hostile.
- **Block only ever appears once per body,** on the opening Boot Up turn, and never again — so the Axebot is not a wall in any sustained sense. It is a soft target that keeps coming back.
- **Armored damage feedback.** Hits on it read as armor rather than flesh; cosmetic, but it reinforces the construct read consistent with Act 3's mechanical bestiary.
- No summons, no allies, no HP-threshold branch, no enrage. Everything above is the whole kit.

## Scaling by act / ascension

- **Act:** none. Axebot is Act 3 content only. Its numbers do not read the act index; the only act-derived factor that touches it is the multiplayer scaler below.
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 70–78 → **76–86**, per body. Across three bodies that is roughly +18 to +24 total health.
  - *Deadly Enemies* tier: Boot Up Block 10 → 15, Boot Up Strength 3 → 4, One-Two 9 → 10, Hammer Uppercut 12 → 14.
  - Weak and Frail amounts are **not** ascension-scaled, and the stock count is **not** ascension-scaled — you always fight exactly three bodies at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales hard.** On entering combat with more than one player, enemy max HP is multiplied by (player count × an act factor); for a non-boss Act 3 room that factor is **1.2**. A 2-player Axebot body sits at roughly 168–187 HP (2 × 1.2 × a 70–78 roll) and a 3-player body at roughly 252–281. Multiply by three bodies: a 3-player fight has a combined pool north of 750 HP. The scaling is applied on creature creation, so **every respawn is scaled too** — the replacements are not cheap.
- **Block scales the same way.** The multiplayer scaler inflates block gained by enemies from monster moves by the same (player count × act factor). Boot Up's 10 Block becomes 24 at 2 players and 36 at 3; at the Deadly-Enemies tier that opening block is 36 / 54.
- **Damage does not scale, but it is applied per seat.** Monster attacks target *all* opposing player creatures rather than picking one, and the hit list is refreshed per hit. So One-Two hits **every** player twice for its listed damage, and Hammer Uppercut hits every player once. Weak and Frail are likewise applied to every player creature, not one.
- **Strength gain is seat-count independent** — the ramp table above is unchanged at any seat count.
- Net effect: at higher seat counts the fight gets *longer* (HP × seats × 1.2, three times over) while per-seat incoming damage stays flat and both debuffs stay on everyone. That is a strictly worse trade for the party than the HP multiplier suggests, because a longer fight means more bodies reached and therefore more turns spent under the +6-Strength version of the enemy.

## Fight-class reasoning — `attrition`

Nothing this enemy does asks for a defensive spike: the biggest single turn it ever presents is a 30–36 point One-Two from its third body, and that turn is telegraphed a full turn ahead by a deterministic alternation the player can read from turn two. What it asks for instead is *unbroken* per-turn mitigation across a ~230 HP pool (750+ in three-player co-op) while permanent Frail makes each block card buy 25% less and permanent Weak makes each attack card close 25% less of the clock — the fight is a sustained tax on both halves of the deck simultaneously. The stock/respawn mechanic is gimmick-flavored in presentation, but in demand terms it is pure attrition: it triples the health bar, invalidates overkill burst, and steps the enemy's damage up each time you "win," so the correct answer is throughput and consistency rather than any single big turn. `gimmick` would over-weight the respawn animation and under-sell the actual per-turn ask, and `spike` is plainly wrong — there is no burst to survive, only a grind to outlast.
