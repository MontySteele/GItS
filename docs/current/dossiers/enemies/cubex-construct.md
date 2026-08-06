# Cubex Construct — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `CubexConstruct`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounters:**
  - `CubexConstructNormal` — a single Cubex Construct, alone.
  - `ConstructMenagerieNormal` — one `PunchConstruct` plus **two** Cubex Constructs. (Only `CubexConstructNormal` is listed in Overgrowth's own encounter table; the Menagerie is the shared-construct fight it also appears in.)
- **Proposed fight class:** `spike`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Cubex runs a four-state move machine with **zero randomness**. Every transition is a hard-wired follow-up, so once you have seen one loop you know every intent for the rest of the fight.

The four moves:

1. **Charge Up** (initial state, played exactly once) — shows a *buff* intent only. It unburrows, starts a charge loop, and gains **+2 Strength**. No damage this turn.
2. **Repeater Blast** — shows an *attack* intent **and** a *buff* intent together. One hit, then **+2 Strength after the hit resolves**.
3. **Repeater Blast (second copy)** — mechanically identical to #2, a separate state purely so the machine can count to three.
4. **Expel Blast** — shows a *multi-attack* intent (damage × 2). Two hits. **No Strength gain.**

Wiring: Charge Up → Blast → Blast → Expel → **Blast** → Blast → Expel → … forever. **Charge Up has no inbound edge** — it is reachable only as the opening state and can never recur. After turn 1 the enemy is locked in a three-beat rhythm: *blast, blast, double-hit*.

Because the Strength buff on Repeater Blast lands *after* that turn's damage, the number the player sees on the intent is always the value that will actually hit; the buff icon next to it is the warning about the *following* turn. Intent damage is strength-aware (it is computed through the same damage pipeline the attack uses), so the displayed number visibly climbs each cycle.

| Turn | Move | Intent shown | Strength when it hits | Damage dealt | Strength after |
| --- | --- | --- | --- | --- | --- |
| 1 | Charge Up | buff | — | 0 | 2 |
| 2 | Repeater Blast | attack + buff | 2 | **9** | 4 |
| 3 | Repeater Blast | attack + buff | 4 | **11** | 6 |
| 4 | Expel Blast | attack ×2 | 6 | **11 × 2 = 22** | 6 |
| 5 | Repeater Blast | attack + buff | 6 | **13** | 8 |
| 6 | Repeater Blast | attack + buff | 8 | **15** | 10 |
| 7 | Expel Blast | attack ×2 | 10 | **15 × 2 = 30** | 10 |
| 8 | Repeater Blast | attack + buff | 10 | **17** | 12 |
| 9 | Repeater Blast | attack + buff | 12 | **19** | 14 |
| 10 | Expel Blast | attack ×2 | 14 | **19 × 2 = 38** | 14 |

(Base values, single player, no ascension, no player-side modifiers.) Cumulative incoming damage: 9 / 20 / 42 / 55 / 70 / **100** by turn 7, 174 by turn 10. **Each three-turn cycle adds a flat +4 Strength**, which is +4 to every future single blast and **+8** to every future Expel.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | **65** (fixed — min and max are the same value) | **70** at the *Tough Enemies* tier |
| Repeater Blast damage | 7 | **8** at the *Deadly Enemies* tier |
| Expel Blast damage | 5, **twice** | **6**, twice, at the *Deadly Enemies* tier |
| Charge Up Strength gain | +2 | not ascension-scaled |
| Repeater Blast Strength gain | +2 (post-hit) | not ascension-scaled |
| Opening Block | 13 | not ascension-scaled |
| Opening Artifact | 1 | not ascension-scaled (but see multiplayer) |

HP is a **fixed 65 (70)** — unlike most normals there is no roll and no per-body variance, so the fight's clock is exactly the same every time you meet it. That makes it unusually easy to plan a kill turn around.

At the *Deadly Enemies* tier the ramp table above shifts to 10 / 12 / (12×2 = 24) / 14 / 16 / (16×2 = 32) / 18 / 20 / (20×2 = 40) — the same shape, roughly +1 per blast and +2 per Expel turn.

## Gimmicks

- **Starts burrowed with 13 Block.** It enters the room underground and gains 13 Block before anyone acts. That block is only ever granted once, on room entry — the Cubex never blocks again for the whole fight. In practice it is a flat 13-damage tax on the player's opening turn, which matters precisely because the opening turn is when the player most wants to bank damage against the ramp.
- **1 Artifact on entry.** The first debuff aimed at it is eaten and the Artifact is consumed. This is a targeted counter to the obvious answer: the whole fight is a Strength ramp, so the natural play is Weak (or a Strength-reduction effect) — and the *first* such card is guaranteed to whiff. Players who lead with their debuff are effectively down a card; players who spend a cheap throwaway debuff to strip the Artifact first get full value from the real one.
- **The ramp is unbounded and never resets.** There is no Strength cap, no decay, no "vent" turn, and no HP-threshold branch. The Strength counter only ever goes up, +4 per three-turn cycle, for as long as the fight lasts.
- **Turn 1 is free damage-wise but is not a free turn.** Charge Up deals nothing, so the player gets one clean setup turn — but 13 Block on the enemy means that setup turn buys less than it looks like.
- **Expel is the only multi-hit and the only non-buffing move.** Every third turn the incoming damage roughly doubles relative to the surrounding blast turns while the enemy's Strength stands still. Thin-Block and per-hit mitigation behave very differently on Expel turns than on blast turns; the two-hit split also interacts badly with player-side flat damage reduction (it is applied twice at half the benefit each).
- **Deterministic to the end.** No summons, no allies, no enrage, no revive, no RNG in the move machine. The player can count exactly how many turns they have and exactly what each one costs.
- The burrowed / charging / attacking visual states are cosmetic (they gate which hurt animation plays and drive an audio loop that reacts to the enemy taking damage); they carry no mechanical effect.

## Scaling by act / ascension

- **Act:** none. Cubex Construct is Act 1 content. Its damage and HP do not read the act index; the only act-derived factor that touches it is the multiplayer scaler below (act index 0 → factor **1.1**).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP 65 → **70**.
  - *Deadly Enemies* tier: Repeater Blast 7 → **8**, Expel Blast 5 → **6** (per hit, so +2 per Expel turn).
  - The Strength gains, the opening Block, and the Artifact stack are **not** ascension-scaled — the *shape* of the fight is identical at every ascension, only its two constants move.

## Multiplayer / seat-count adjustments

- **HP scales by (player count × 1.1)** for an Act 1 room, applied at creature creation. A 2-player Cubex sits at **143** HP (157 in the `ConstructMenagerie` sense of two of them: 286 combined), a 3-player Cubex at **214** (rounded from 214.5). At the *Tough Enemies* tier: 154 / 231.
- **The opening 13 Block scales the same way** — monster-move block is multiplied by (player count × act factor). 13 → **28** at 2 players, **42** at 3. The opening-turn tax is therefore proportionally the same per seat, not diluted.
- **Artifact scales with seats:** the stack is granted as `1 + (players − 1)`, so a 2-player fight starts it with **2** Artifact and a 3-player fight with **3**. Stripping it costs the party one throwaway debuff *per seat present* before any real debuff lands — in 3-player co-op that is a serious speed bump on the party's main counterplay.
- **Damage does not scale per seat, but it is applied to every seat.** Both moves target *all* opposing player creatures rather than picking one. Repeater Blast hits **every** player for its listed damage; Expel Blast hits **every** player **twice**. So the party's *total* incoming damage is the table above multiplied by seat count, while each individual seat sees exactly the single-player numbers.
- **Strength gain is seat-count independent** — the ramp table is unchanged at any seat count.
- Net effect: HP goes up ~2.2× / 3.3× while the ramp rate stays flat, so more seats means **more turns spent in the late, steep part of the curve**. This is the worst possible interaction for this particular enemy: the multiplayer scaler lengthens exactly the fight you least want to lengthen.

## Fight-class reasoning — `spike`

Per turn, this fight asks for one thing that grows without bound: raw mitigation on a schedule the player can read but cannot alter. The three-beat rhythm produces a genuine spike every third turn — Expel roughly doubles that cycle's incoming damage in a single telegraphed turn (22, then 30, then 38 at base), and because the two Strength gains land on the blast turns bracketing it, each Expel arrives +8 harder than the last. There is no wall to chew through (65 fixed HP, no block after turn 1) and no way to outlast the ramp, so the correct answer is to kill it inside two or three cycles and to spend defense on the Expel turns specifically rather than smoothing it out; `attrition` would be exactly the wrong read, since every extra turn is strictly worse than the one before it. `gimmick` over-weights the burrow-and-Artifact opening, which is a one-turn tax rather than a puzzle — the Artifact just delays the anti-Strength counterplay by a card, it does not change what the fight demands.
