# Calcified Cultist — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `CalcifiedCultist`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `CultistsNormal` — a fixed, non-random two-body encounter: exactly one Calcified Cultist and exactly one Damp Cultist, every time. There is no pool roll and no size variation.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Calcified Cultist runs the simplest possible move machine: a one-shot opener followed by an infinite loop of a single attack. No randomness, no branching, no HP thresholds, no re-rolls.

1. **Incantation** (buff intent) — turn 1 only. Applies Ritual to itself.
2. **Dark Strike** (single-target attack intent) — turn 2 onward.
3. Dark Strike's follow-up state points at *itself*, so it never leaves. Incantation is cast exactly once per fight and is never revisited.

Because the follow-up chaining is fully deterministic, the intent icon is never a guess: the player sees a buff on turn 1 and an attack on every turn after that, forever. The displayed attack number is computed live from the creature's current modifiers, so the intent accurately shows the Strength-inflated damage rather than the printed base — the player is told the escalation is happening.

Both moves appear in the bestiary; nothing about this enemy is hidden from the stat page.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Starting HP roll | 38–41 | 39–42 (Tough Enemies tier and above) |
| Dark Strike damage (printed) | 9 | 11 (Deadly Enemies tier and above) |
| Incantation → Ritual amount | 2 | 2 (no ascension scaling) |
| Block gained | none | none |

**How Ritual resolves.** Ritual is a counter-type buff that, at the end of each of the owner's side's turns, converts into that many stacks of permanent Strength — and it stays on, so it fires again every subsequent turn. There is a deliberate one-turn grace: the turn on which an enemy applies Ritual to itself, the end-of-turn trigger is skipped. So Ritual 2 applied on turn 1 does *not* pay out at the end of turn 1; the first +2 Strength lands at the end of turn 2, after the first Dark Strike has already resolved.

That produces this curve (nothing else applied, base / Deadly Enemies):

| Cultist's turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Action | Incantation | Strike | Strike | Strike | Strike | Strike | Strike |
| Strength when it swings | 0 | 0 | 2 | 4 | 6 | 8 | 10 |
| Damage | — | 9 / 11 | 11 / 13 | 13 / 15 | 15 / 17 | 17 / 19 | 19 / 21 |

Cumulative damage taken if the player blocks nothing: 9 by turn 2, 20 by turn 3, 33 by turn 4, 48 by turn 5, 65 by turn 6 (base numbers). Growth is linear at +2 per turn and unbounded — Strength here has no cap and no decay.

**The partner matters to the read.** The Damp Cultist in the same encounter uses an identical state machine with the numbers inverted: much more HP (51–54), a near-trivial printed strike (1, or 3 at Deadly Enemies), and a much larger Ritual (5, or 6 at Deadly Enemies). The Damp Cultist therefore starts as a non-threat and out-scales the Calcified one around its fourth or fifth swing, while the Calcified Cultist is the one hitting hard *now*. Kill-order pressure is the whole encounter: the fragile front-loaded body is the one you want dead, and the fat one is the one you can't afford to leave alive.

## Gimmicks

- **Ritual, not Strength.** The buff is one step removed from the damage — it is a per-turn Strength *generator* that persists. Removing or reducing the Strength stacks does not stop the growth; the Ritual counter keeps re-paying every turn. Anything that strips or blocks the Ritual counter itself is worth far more here than Strength reduction, which is a one-off refund against a recurring cost.
- **One buff turn, then pure pressure.** Unlike the alternating ramp-attackers elsewhere in Act 1, this enemy does not trade attack turns for buff turns. It pays once on turn 1 and then attacks every single turn thereafter, so there are no free turns after the opener.
- **Turn 1 is the only safe turn.** The whole fight's tempo hinges on that: the player gets exactly one unpressured turn from this body to set up.
- **No defense, no utility.** It has no block, no debuff application, no summon, no healing, no interaction with its partner. The kit is "buy compounding interest, then swing."
- **Fragile.** At 38–42 HP it is the low-HP member of its own encounter by a wide margin; it is fully removable in the first two or three player turns by most decks, and that is clearly the intended out.
- **Escalating attack audio.** Each Dark Strike plays with a rising "strength" parameter, so the hits audibly get heavier over the fight — a non-numeric tell that the ramp is running.

## Scaling by act / ascension

- **Act:** none. Act 1 content only, no per-act variant, and the model never reads the act index for its own numbers (the act index only enters through the multiplayer HP scaler below).
- **Ascension:** two independent bumps, each keyed to a named ascension tier rather than a raw level. The "tough enemies" tier raises the HP band by 1 at both ends (38–41 → 39–42). The "deadly enemies" tier raises Dark Strike from 9 to 11. The Ritual amount stays at 2 at every ascension — so high ascension makes the opening hits harder and the body slightly tankier, but the *slope* of the ramp is identical at ascension 0 and ascension max. Note the contrast with the partner: the Damp Cultist's ascension bump does touch its Ritual (5 → 6), so the encounter as a whole ramps faster at high ascension even though this member does not.

## Multiplayer / seat-count adjustments

- **HP scales, damage does not.** On combat entry, enemy max HP is multiplied by (player count × an act-scaling factor); Act 1's factor is 1.1. A 2-player Calcified Cultist sits around 84–92 HP and a 3-player one around 125–139. Dark Strike's printed damage and the Ritual amount are seat-count independent.
- **Block scaling does not apply** — the multiplayer block scaler only touches enemies that gain block, and this one gains none.
- **Targeting:** Dark Strike is a single-target attack resolved through the standard monster-targeting path, so it hits one seat per activation rather than splitting or hitting the table. Incantation is a self-buff with no seat choice.
- Net effect, and it is a real one: seat count buys the cultist proportionally more turns alive at the same per-hit damage, and every extra turn alive is another +2 Strength. The ramp table above shifts several rows deeper before the body dies, so the average damage per swing over the fight is meaningfully higher in multiplayer than the flat HP multiplier suggests. The fight also spreads that damage across seats, which blunts the spike but makes the total harder to no-sell with one player's block.

## Fight-class reasoning — `attrition`

Every turn from turn 2 onward this enemy demands mitigation, and the amount it demands rises by a fixed 2 per turn with no ceiling — there is never a burst turn to brace for and never an idle turn to bank on. That is a sustained-cost profile, not a spike one: the player's real decision is a kill clock, because each block card bought buys strictly less than the previous one, and the encounter's second body is running the same clock on a steeper slope behind it. Low-damage or slow-setup decks lose here not to any single hit but to the integral of a linear curve, which is the defining shape of attrition. The label is for this unit; the `CultistsNormal` encounter as a whole is also `attrition` — two deterministic ramps with staggered onsets — but with an unusually sharp kill-order test layered on top.
