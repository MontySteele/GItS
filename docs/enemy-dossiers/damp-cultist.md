# Damp Cultist — behavior dossier

- **Class:** `DampCultist`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `CultistsNormal` — a fixed two-body pair, one `CalcifiedCultist` + one `DampCultist`. No slot names are assigned; the composition is hard-coded, never rolled.
- **Proposed fight class:** `spike`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Two states, **zero randomness**, and only one transition edge that ever fires:

1. **Incantation** (buff intent) — the opening turn, always. Applies a stack of Ritual to itself, plays the caw-caw banter line, and does no damage.
2. **Dark Strike** (single-attack intent) — one hit on the player side.

Wiring: Incantation → Dark Strike → Dark Strike → … forever. Dark Strike's follow-up is **itself**, and nothing points back at Incantation, so the buff turn happens exactly once per fight and can never recur. From turn 2 onward the intent is the attack icon every single turn, and its displayed number is the Strength-modified value — the player can read the ramp directly off the intent.

This is the same skeleton the Calcified Cultist runs (one Incantation, then Dark Strike on loop). The two cultists differ only in their numbers, and they differ in opposite directions.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 51–53 | **52–54** (Tough Enemies) |
| Ritual applied by Incantation | 5 | **6** (Deadly Enemies) |
| Dark Strike base damage | 1 | **3** (Deadly Enemies) |
| Block | none, ever | — |

HP is rolled inside the band, and the game prefers a max-HP value distinct from the other creature on the side when the band allows.

**Ritual is the whole enemy.** It is a counter-style buff that, at the end of each of the owner's side-turns, grants Strength equal to its amount — but it explicitly **skips the turn it was applied on** when an enemy applied it. So the Incantation turn produces no Strength; the first payout lands at the end of turn 2, and every turn thereafter.

Effective Dark Strike damage (Strength at the moment of the attack, before Weak/Vulnerable and before player modifiers):

| Turn | Move | Strength | Damage (base) | Damage (Deadly tier) |
| --- | --- | --- | --- | --- |
| 1 | Incantation | 0 | — | — |
| 2 | Dark Strike | 0 | 1 | 3 |
| 3 | Dark Strike | +5 | 6 | 9 |
| 4 | Dark Strike | +10 | 11 | 15 |
| 5 | Dark Strike | +15 | 16 | 21 |
| 6 | Dark Strike | +20 | 21 | 27 |
| 7 | Dark Strike | +25 | 26 | 33 |
| *n* ≥ 2 | Dark Strike | 5(*n*−2) | 1 + 5(*n*−2) | 3 + 6(*n*−2) |

Cumulative damage taken from this body alone through turn 7: **81** base, **108** at the Deadly tier. Through turn 10 it is 216 / 306 — well past lethal for any Act 1 loadout. The ramp is unbounded and there is no cap or reset anywhere in the kit.

**The pair, for context.** The Calcified Cultist is the mirror image: ~38–41 HP (39–42 Tough tier), Dark Strike **9** (11 Deadly tier), Ritual **2**. It hurts immediately and ramps slowly; the Damp Cultist is harmless immediately and ramps 2.5× faster off a body that has ~30% more HP. Combined incoming damage for the encounter, base tier: 10 on turn 2, 17 on turn 3, 24 on turn 4, 31 on turn 5, 38 on turn 6 — a clean linear +7/turn escalation, of which the Damp Cultist owns +5.

## Gimmicks

- **Delayed-start ramp.** The one-turn Ritual grace period is a real tempo gift: the player gets two effectively free turns (the buff turn plus a 1-damage turn) to set up. Everything after that is on a linear clock.
- **The threat is priority, not survival.** Nothing in the kit rewards blocking it — the correct play is to remove this body first even though it is the *tougher* of the two and the *less* immediately dangerous, because its slope is 2.5× the partner's. The encounter is essentially a target-selection puzzle disguised as a stat check.
- **Strength, not raw damage.** Because the ramp is Strength, it is answerable by Strength-reduction and by Weak, and it multiplies with nothing else the enemy has. A 1-damage base attack means every point of incoming damage past turn 2 is Strength the player could have denied.
- **No block, no summons, no debuffs applied to the player, no HP-threshold branch, no enrage, no death rattle.** Incantation and Dark Strike are the entire kit.
- Cosmetics: fur-type damage feedback, swamp-colored banter VFX, and an attack SFX that gets progressively more intense each time it swings — an audio tell that tracks the ramp.

## Scaling by act / ascension

- **Act:** none. Damp Cultist is Act 1 content only and appears in exactly one encounter. Its numbers do not read the act index; the only act-derived factor touching it is the multiplayer scaler below (Act 1 factor **1.1**).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 51–53 → **52–54**. A one-point shift — cosmetically the smallest ascension HP bump in the act.
  - *Deadly Enemies* tier: Dark Strike 1 → **3** and Ritual 5 → **6**. This is the bump that matters: it changes the ramp slope from +5/turn to +6/turn *and* triples the floor, so the turn-*n* damage goes from 1+5(*n*−2) to 3+6(*n*−2) — roughly a 30% steeper curve that starts ~2 damage higher.
  - Ritual's skip-the-application-turn rule is not ascension-scaled; the grace turn survives at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales hard.** Enemy max HP is multiplied by (player count × act factor) on combat entry; the Act 1 non-boss factor is **1.1**. Two players puts a Damp Cultist at roughly **112–117** HP, three players at roughly **168–175**. The Calcified partner scales the same way, so the pair's combined pool goes from ~90 to ~200 (2p) or ~300 (3p).
- **Damage does not scale, but it lands on every seat.** Monster attacks target all opposing player creatures, so Dark Strike hits **each** player for its full Strength-modified value every turn. Party-wide incoming damage from this body is therefore turn-*n* damage × seat count, while its health bar is also × seat count × 1.1 — the ramp and the kill-window scale together, which is a strictly worse trade than it looks because the extra turns needed to chew through the scaled HP are spent at the *far* end of the ramp where each turn costs 5 more per seat than the last.
- **Ritual and Strength are seat-count independent** — the ramp table above is unchanged at any seat count.
- The block scaler in the multiplayer model is inert here: this enemy never gains block.

## Fight-class reasoning — `spike`

The per-turn demand curve this enemy draws is nearly flat for two turns and then rises without limit, which is the defining shape of a spike rather than a grind: turns 1–2 ask for essentially nothing (0 damage, then 1), and by turn 6 a single unanswered attack is 21 per seat against an Act 1 health pool. What the fight demands is a *kill by a deadline* — burst damage aimed at this specific body, or Strength denial to flatten the slope — and the penalty for missing the deadline is not gradual erosion but a hit that ends the run. It is not `attrition`, because its early chip damage is trivial and there is nothing to outlast; it is not `swarm` (two bodies) and not `gimmick` (Ritual is a stat ramp with an obvious counter, not a puzzle). `mixed` is the honest label for the *encounter* — the Calcified partner supplies flat sustained pressure while this one supplies the escalation — but for this enemy in isolation the demand is unambiguously the spike half of that pair.
