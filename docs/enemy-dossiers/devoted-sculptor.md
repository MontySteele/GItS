# Devoted Sculptor — behavior dossier

- **Class:** `DevotedSculptor`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `DevotedSculptorWeak` — a solo encounter. Exactly one Devoted Sculptor, no partner, no pool roll, no size variation. It is flagged as a *weak* encounter, so it is drawn from the pool used for the first two monster rooms of Act 3 (Glory sets `NumberOfWeakEncounters` to 2). The "weak" flag is a placement tag only; it does not reduce the body's stats.
- **Proposed fight class:** `spike`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Sculptor runs the minimal two-state machine: a one-shot opener, then an infinite self-loop on a single attack. There is no randomness, no branching, no HP threshold, and no re-roll — the RNG handle the state machine offers is never consulted by this monster.

1. **Forbidden Incantation** (buff intent) — turn 1 only. Applies Ritual 9 to itself, with a scream VFX and a spoken banter line.
2. **Savage** (single-target attack intent) — turn 2 onward.
3. Savage's follow-up state points at *itself*, so the machine never leaves it. The Incantation is cast exactly once per fight and is never revisited.

The intent icon is therefore never a guess: buff on turn 1, attack on every turn thereafter, forever. The attack intent's number is recomputed live from the creature's current modifiers rather than the printed base, so the player is shown the true, Strength-inflated damage each turn — the escalation is fully telegraphed, one turn at a time.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Starting HP | 162 (fixed — min and max are the same) | 172 (Tough Enemies tier and above) |
| Savage damage (printed) | 12 | 15 (Deadly Enemies tier and above) |
| Forbidden Incantation → Ritual amount | 9 | 9 (no ascension scaling) |
| Block gained | none | none |

Note the HP band has zero width: `MaxInitialHp` is defined as `MinInitialHp`, so every Devoted Sculptor in every run has exactly the same HP for a given ascension tier. There is no roll to plan around.

**How Ritual resolves.** Ritual is a counter-type buff that, at the end of each of the owner's side's turns, converts into that many stacks of permanent Strength — and it persists, so it fires again every subsequent turn. There is a deliberate one-turn grace: on the turn an enemy has Ritual applied to it, the end-of-turn trigger is skipped once. So Ritual 9 applied on turn 1 does *not* pay out at the end of turn 1; the first +9 Strength lands at the end of turn 2, after the first Savage has already resolved.

That produces this curve (nothing else applied, base / Deadly Enemies):

| Sculptor's turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Action | Incantation | Savage | Savage | Savage | Savage | Savage | Savage |
| Strength when it swings | 0 | 0 | 9 | 18 | 27 | 36 | 45 |
| Damage | — | 12 / 15 | 21 / 24 | 30 / 33 | 39 / 42 | 48 / 51 | 57 / 60 |

Cumulative damage taken if the player blocks nothing (base numbers): 12 by turn 2, 33 by turn 3, 63 by turn 4, 102 by turn 5, 150 by turn 6, 207 by turn 7. Growth is linear at +9 per turn, uncapped, undecaying, and steep enough that the second attack is already 75% larger than the first.

**Ritual 9 is the outlier.** Only three monsters in the game apply Ritual to themselves: the Calcified Cultist (2), the Damp Cultist (5), and this one (9). The Sculptor's slope is more than four times the Act 1 attacker's on a body four times as large, which is the whole design statement — it is the Act 1 cultist pattern re-tuned so that mitigation stops being a viable answer within three swings.

## Gimmicks

- **Ritual, not Strength.** The buff is one step removed from the damage: it is a per-turn Strength *generator* that persists. Stripping or reducing the Strength stacks does not stop the growth — the Ritual counter re-pays every turn, so Strength reduction is a one-off refund against a recurring cost. Anything that removes or zeroes the Ritual counter itself is worth an order of magnitude more here than in any Act 1 ritual fight.
- **One buff turn, then pure pressure.** It does not trade attack turns for buff turns. It pays once on turn 1 and attacks every turn afterward, so there are no free turns after the opener.
- **Turn 1 is the only safe turn** — a single unpressured setup turn, and it is the same turn the player learns (via the intent) that the ramp is +9.
- **A deceptively soft first hit.** The printed 12 is low for Act 3 and lands before any Strength has accrued. A player reading the first swing rather than the Ritual number will badly misprice the fight; by the third swing the same enemy is hitting for 21 and by the fifth for 39.
- **No defense, no utility, no interaction.** No block, no debuff application, no summon, no heal, no partner. The kit is "buy compounding interest at a very high rate, then swing."
- **Single-target only.** Savage resolves through the standard single-target monster attack path with a blunt hit effect; it never splits or hits the whole table.
- **Fat but not tanky-by-design.** 162/172 HP is a large pool for a normal encounter, but it is the fight's actual clock — the HP total is what sets the deadline, not a defensive layer.

## Scaling by act / ascension

- **Act:** none intrinsic. Act 3 content only, one variant, and the model never reads the act index for its own numbers (the act index enters only through the multiplayer scalers below, where Act 3's factor is used).
- **Ascension:** two independent bumps, each keyed to a named ascension tier rather than a raw level. The Tough Enemies tier raises HP 162 → 172. The Deadly Enemies tier raises Savage 12 → 15. **The Ritual amount stays at 9 at every ascension**, so high ascension shifts the whole damage curve up by a flat 3 per swing and adds one more swing's worth of HP to chew through — but the *slope* is identical at ascension 0 and at ascension max. Ascension makes the deadline arrive slightly earlier and every payment slightly larger; it does not change the shape.

## Multiplayer / seat-count adjustments

- **HP scales.** On combat entry, enemy max HP is multiplied by (player count × an act-scaling factor); Act 3's non-boss factor is 1.2. A 2-player Sculptor sits at roughly 389 HP (413 at Tough Enemies) and a 3-player one at roughly 583 HP (619). This is the single biggest lever seat count pulls here, and it pulls in the enemy's favour.
- **Savage damage does not scale** with seat count, and neither does the Ritual amount — Ritual is not opted into the multiplayer power scaler, so it is 9 at every table size.
- **Block scaling does not apply** — the multiplayer block scaler only touches enemies that gain block, and this one gains none.
- **Targeting:** Savage is a single-target attack resolved through the standard monster-targeting path, so it hits one seat per activation. The Incantation is a self-buff with no seat choice at all (it is applied through a context that would throw if a choice were required).
- Net effect, and it is severe: seat count buys the Sculptor 2.4× or 3.6× more turns alive at unchanged per-hit damage, and every extra turn alive is another +9 Strength on an uncapped curve. A fight that ends on turn 5 solo runs to turn 8 or 9 at three seats, by which time the same single-target swing is doing 66–84. The damage does spread across seats, which blunts any one player's spike, but the integral grows quadratically in turns while the HP pool grows only linearly in players — multiplayer is where this enemy is at its most dangerous, and the tell is that the last two swings of a 3-seat fight are individually larger than the entire solo fight's output.

## Fight-class reasoning — `spike`

What this fight demands per turn is close to nothing for two turns and then more than a deck can pay, with no plateau in between: 12, then 21, then 30, then 39, on a body with 162 HP and no defensive layer. That is a deadline, not a grind — the player is not choosing how much mitigation to buy each turn, they are choosing whether they can close the kill before the curve crosses their block ceiling, which happens around the fourth or fifth swing. Sustain answers do not scale against a +9-per-turn generator (block bought this turn is worth strictly less than block bought last turn, and Strength removal is a refund against a recurring charge), so the fight rewards burst damage, Ritual removal, or one very large defensive turn placed correctly. It is `spike` rather than `attrition` because the per-turn demand is flat-then-vertical and the fight is decided by a single crossing point, and rather than `gimmick` because Ritual is a known, printed, fully telegraphed keyword — the enemy hides nothing, it just charges compound interest at a rate Act 3 decks are not built to service.
