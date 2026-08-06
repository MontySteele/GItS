# Magi Knight — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `MagiKnight`
- **Kind:** elite
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `KnightsElite` — a fixed three-body elite. Always spawns `FlailKnight` (first slot), `SpectralKnight` (second slot), `MagiKnight` (third slot). No randomization: the encounter's "all possible monsters" list and its generated list are the same three, in the same order.
- **Proposed fight class:** `spike`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Magi Knight runs a five-state move machine with **zero randomness**. Every edge is a hard-wired follow-up, so once you have seen two turns you can predict the whole fight.

The five states:

1. **Power Shield** — shows an *attack* intent **and** a *defend* intent on the same turn. Hits once, then gains Block. Initial state.
2. **Dampen** — shows a *debuff* intent (no number). Applies the Dampen power to every player and plays a taunt line.
3. **Ram / Spear** — shows a *single-attack* intent. One medium hit.
4. **Prep** — shows a *defend* intent. Gains Block, plays the shield-cast animation, no damage. **Hidden from the bestiary** (the bestiary page for this enemy deliberately omits it), but fully visible in combat as a plain block turn.
5. **Magic Bomb** — shows a *single-attack* intent. One very large hit, plus a visible ranged wind-up (the model repositions itself relative to the left-most player before the cast).

Wiring: Power Shield → Dampen → Ram → Prep → Bomb → **Ram** → Prep → Bomb → … forever.

Two structural consequences:

- **Power Shield and Dampen have no inbound edges.** They are opening-only. Magi Knight applies Dampen exactly **once** per fight, on turn 2, and never re-applies it (see the caster caveat under Gimmicks).
- **From turn 3 onward the enemy is a strict 3-turn metronome:** Ram → Prep → Bomb. The Prep turn is a pure block turn, and it exists to telegraph the Bomb one full turn in advance.

Observed sequence:

| Turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | … |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Move | Power Shield | Dampen | Ram | Prep | **Bomb** | Ram | Prep | **Bomb** | Ram | 3-cycle |
| Intent shown | attack + defend | debuff | attack | defend | attack | attack | defend | attack | attack | |
| Damage (base) | 6 | — | 10 | — | **35** | 10 | — | **35** | 10 | |

Note that the intent for a move is rolled before the turn it is performed, and a monster that has not yet acted cannot transition away, so the turn-1 Power Shield is guaranteed and the machine never "skips" a state.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP (fixed, no roll — min HP equals max HP) | 82 | **89** (Tough Enemies) |
| Power Shield damage | 6 | **7** (Deadly Enemies) |
| Power Shield Block | 5 | **9** (Tough Enemies) |
| Prep Block | 5 | **9** (Tough Enemies) — same value as Power Shield's |
| Ram / Spear damage | 10 | **11** (Deadly Enemies) |
| Magic Bomb damage | 35 | **40** (Deadly Enemies) |
| Dampen amount | 1 application, no stacks, no duration | not ascension-scaled |

Steady-state damage output per 3-turn cycle (single player, before player modifiers): **45** base / **51** at the Deadly tier, of which **78%** arrives on one turn. Average is ~15/turn; the actual shape is 10 / 0 / 35.

Self-block totals 10 (base) or 18 (Tough tier) across the opening two block turns, then 5/9 every third turn thereafter — it is not a wall, but the Prep block does soak a full turn of the player's damage right before the Bomb, which is exactly the turn the player would rather be racing.

Encounter context (the other two bodies, for pool math): Flail Knight 101 HP (108 Tough), Spectral Knight 93 HP (97 Tough). Combined `KnightsElite` pool: **276** base / **294** at the Tough tier. Magi Knight is the *smallest* health bar of the three and the one carrying the largest single hit.

Damage taken by this enemy reads as armor rather than flesh (cosmetic only).

## Gimmicks

- **Dampen — the headline.** When applied, it immediately scans every card in that player's combat state and **downgrades every upgraded card**, recording each card's old upgrade level. There is no stack count and no turn counter: it is a persistent state, not a timed debuff.
- **Dampen is caster-keyed and reversible.** The power keeps a set of casters. When a caster dies, it is dropped from that set, and when the set empties, the power removes itself — and on removal it **re-applies every recorded upgrade level**. In this encounter Magi Knight is the only creature that casts it, so *killing Magi Knight restores the party's upgrades mid-fight*. That makes the smallest health bar in the trio also the correct first kill, which is the real puzzle of the fight.
- **Dampen only snapshots at apply time.** Cards upgraded *after* the debuff lands (in-combat upgrade effects) are not downgraded, and are not touched on removal either. A player with mid-combat upgrade tools can partially route around it.
- **Re-cast is a no-op by design.** If the power is already present, the move only adds the caster to the set rather than re-applying — so in any future encounter that fields multiple Dampen casters, the debuff survives until the *last* of them dies. Within `KnightsElite` there is only ever one caster.
- **The Prep turn is an honest tell.** It shows a defend intent and does nothing else, and the game hides it from the bestiary specifically so its role reads as a wind-up rather than as a listed move. In practice it is a free player turn that also announces "35–40 damage next turn."
- **The Bomb is a ranged attack visually.** The cast repositions the attacker toward the left-most player creature before firing. Purely presentational — it does not change targeting or damage.
- No summons, no HP-threshold branch, no enrage, no self-buff (no Strength gain anywhere in the kit). Everything above is the whole kit.

## Scaling by act / ascension

- **Act:** none. Magi Knight is Act 3 content only and reads no act index directly; the only act-derived factor that touches it is the multiplayer scaler below (Act 3 non-boss factor, 1.2).
- **Ascension:** two independent, tier-keyed bumps, and they split cleanly.
  - *Tough Enemies* tier — **durability**: HP 82 → 89, and **both** block values 5 → 9. That is a near-doubling of its self-block, and the Prep-turn block is what most delays the kill that would strip Dampen.
  - *Deadly Enemies* tier — **damage**: Power Shield 6 → 7, Ram 10 → 11, Bomb 35 → **40**.
  - Dampen is unscaled at every ascension — it is binary, so there is nothing to scale.

## Multiplayer / seat-count adjustments

- **HP scales by seats × act factor.** Enemy max HP is multiplied by (player count × 1.2) for an Act 3 non-boss room. Magi Knight lands at roughly **197 HP at 2 players** and **295 at 3** (base), or **214 / 320** at the Tough tier. Across the whole `KnightsElite` trio that is roughly **662** at 2 players and **994** at 3.
- **Block scales the same way.** Block gained by enemies from monster moves is multiplied by (player count × 1.2). The 5 Block on Power Shield and Prep becomes **12 at 2 players** and **18 at 3**; at the Tough tier that is **21.6 / 32.4**. The Prep turn stops being a courtesy and becomes a real speed bump on the race to strip Dampen.
- **Damage does not scale, but it is applied per seat.** Monster attacks target *all* player creatures rather than picking one, with the target list refreshed between hits. Power Shield, Ram, and Bomb therefore each hit **every** player for their full listed damage — a 3-player table eats 35–40 per seat on every Bomb turn, not 35–40 split.
- **Dampen hits every seat.** The move iterates all targets and applies the debuff to each player independently, each with its own downgraded-card ledger. One removal condition (Magi Knight's death) clears all of them at once.
- Net effect: seat count makes the fight *much* longer (HP × seats × 1.2, three bodies) and makes the party's upgrade tax last proportionally longer, while the Bomb's per-seat lethality stays flat. More turns under Dampen is the real co-op cost, not the raw HP.

## Fight-class reasoning — `spike`

From turn 3 onward this enemy asks exactly one question on a three-turn clock: *can you have 35–40 points of mitigation ready on the beat?* Ram turns are chip, Prep turns are free, and the Bomb turn is 78% of its total output landing in one packet, telegraphed a full turn ahead by a block-only wind-up that exists for no other reason. The Dampen opener is gimmick-flavored and it does reshape the fight — it makes the smallest health bar the correct first target and turns the kill order into the puzzle — but it is a one-shot binary tax with no per-turn demand of its own; it changes *how good your cards are* while the Bomb changes *what you must do this turn*. `gimmick` would over-weight a debuff that is cast once and self-reverses on death, `attrition` misreads a 45-damage cycle that is really a 35-damage turn, and `mixed` would blur the one thing the demand curve needs from this enemy: a hard, periodic, perfectly-telegraphed defensive peak.
