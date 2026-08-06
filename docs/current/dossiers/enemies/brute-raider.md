# Brute Raider — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `BruteRubyRaider`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `RubyRaidersNormal` — a normal-tier fight that rolls **3 distinct raiders** out of a 5-member pool (Axe, Assassin, Brute, Crossbow, Tracker), each capped at one copy. The Brute is therefore present in a majority — but not all — of Ruby Raider fights, and always alongside two different raiders.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Brute runs a two-state move machine with no randomness and no branching at all. It is a strict, fully predictable alternation:

1. **Beat** (attack intent, single target) — its opening move and its odd-numbered turn.
2. **Roar** (buff intent) — its follow-up, gaining Strength.
3. Roar's follow-up points back at Beat, closing the loop.

So the cycle is Beat → Roar → Beat → Roar → … forever, starting on Beat. There is no HP-threshold branch, no "first turn is special" case beyond starting on the attack, and no re-roll — the state machine's follow-up chaining fully determines the next move, so the intent shown to the player is never a coin flip.

One presentation detail worth carrying into any clone: **Roar is deliberately hidden from the bestiary**. The bestiary entry advertises only the Beat attack; the escalation is something the player is meant to discover in the fight, not read off a stat page.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Starting HP roll | 30–33 | 31–34 (Tough Enemies tier and above) |
| Beat damage | 7 | 8 (Deadly Enemies tier and above) |
| Roar Strength gain | +3 | +3 (no ascension scaling) |
| Block gained | none | none |

HP is rolled per-instance inside the min/max band, and the game prefers to hand each enemy on the side a **distinct** max HP when the band allows it — so in a raider pack the Brute's exact HP varies run to run within its window.

Strength is the ordinary permanent counter buff: it adds flat damage to the owner's attacks, does not decay at end of turn, and is not capped. Because it stacks, the Beat number the player sees climbs by 3 every full cycle.

Effective Beat damage over the fight (base / Deadly Enemies), assuming nothing is applied to it:

| Brute's turn | 1 | 3 | 5 | 7 | 9 |
| --- | --- | --- | --- | --- | --- |
| Beat hits for | 7 / 8 | 10 / 11 | 13 / 14 | 16 / 17 | 19 / 20 |

Cumulative damage taken if the player blocks nothing: 7 by turn 1, 17 by turn 3, 30 by turn 5, 46 by turn 7. In other words the Brute's total output roughly doubles every two cycles, and by turn 7 a single Beat exceeds a typical starting Block card.

## Gimmicks

- **Self-ramp, nothing else.** The Brute has no block, no debuff, no summon, no minion interaction, and no synergy hook into the other raiders. Its entire kit is "hit, then get bigger."
- **Half-uptime attacker.** It only actually attacks every other turn, so its DPS at parity with a flat 7-damage enemy is reached around its third attack. Early on it is the *least* threatening body on the field; late it is the only one that matters.
- **Debuff-shaped weakness.** Because all of its output routes through Strength-modified attacks, Weak-style damage reduction and Strength-removal effects scale against it far better than against the pack's flat-damage members. Conversely, ignoring it while clearing the other two raiders is the classic way this fight goes wrong.
- **Roar turns are free turns.** A player who reads the alternation knows exactly which turns need no block from this enemy, which makes the Brute the natural target for a big setup or focus-fire turn.
- Damage feedback is armored-hit flavored (it reads as a heavy, armored body) — cosmetic, but it signals "not the squishy one" on sight.

## Scaling by act / ascension

- **Act:** none. The Brute is Act 1 content only; there is no per-act variant, and its numbers do not read the act index.
- **Ascension:** two independent bumps, each keyed to a named ascension tier rather than a raw level number. The "tough enemies" tier raises the HP band by 1 at both ends (30–33 → 31–34). The "deadly enemies" tier raises Beat from 7 to 8. The Roar's +3 Strength is untouched at every ascension, so higher ascensions make the Brute start harder but do not make it ramp faster.

## Multiplayer / seat-count adjustments

- **HP scales, damage does not.** On entering combat with more than one player, enemy max HP is multiplied by (player count × an act-scaling factor); in Act 1 that factor is 1.1. So a 2-player Brute sits around 66–75 HP (2 × 1.1 × a 30–34 roll) and a 3-player Brute around 99–112. Its Beat damage and its Strength gain are seat-count independent.
- **Block scaling does not apply** to this enemy — the multiplayer scaler that inflates enemy block only touches enemies that gain block, and the Brute gains none.
- **Targeting:** Beat is a single-target attack resolved through the standard monster-targeting path, so with multiple seats it hits one player per activation rather than splitting or hitting all. Roar is a self-buff and involves no seat choice.
- Net effect: at higher seat counts the Brute lives roughly proportionally longer while dealing the same damage per hit to one seat at a time — which means it accumulates *more* Strength before dying, and the ramp table above shifts several rows deeper into the fight. The multiplayer version of this fight is meaningfully more dangerous than the HP multiplier alone suggests.

## Fight-class reasoning — `attrition`

The Brute never threatens a burst: its opening hit is 7–8 and it is idle every other turn, so no single turn of this fight demands a large defensive spike. What it demands instead is *sustained* per-turn mitigation on a rising curve plus a kill clock — the player must either remove it inside the first three or four cycles or accept that every subsequent block card buys less than the one before. That is the defining shape of an attrition unit: pressure that is trivially survivable turn-to-turn and lethal if the fight runs long, punishing low-damage or slow-setup decks specifically. The label is for the unit; the surrounding `RubyRaidersNormal` encounter reads as `mixed` overall, since the Brute's ramp sits next to a burst attacker and a multi-hit member, and the Brute is the reason that pack cannot simply be out-blocked.
