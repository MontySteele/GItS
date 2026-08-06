# Sludge Spinner — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `SludgeSpinner`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `SludgeSpinnerWeak` — a **weak** (early-act) encounter that spawns exactly **one** Sludge Spinner in an unnamed default slot. No adds, no summons, no allies anywhere in the kit.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Three move states, all of them attacks, all of them feeding a single shared random branch. There are no HP thresholds, no phase changes, no "first turn only" branches, and no turn-count triggers.

The three moves:

1. **Oil Spray** — shows an *attack + debuff* intent pair. One hit, then **Weak 1** applied to the player side.
2. **Slam** — shows a *single-attack* intent. One blunt hit, the biggest of the three, nothing else attached.
3. **Rage** — shows an *attack + buff* intent pair. The smallest hit, then **+3 Strength to itself**, permanent and unbounded.

**The opener is fixed: turn 1 is always Oil Spray.** The machine's initial state is the Oil Spray state, and the state machine is barred from transitioning away before the first move has been performed. So every Sludge Spinner fight begins with a hit plus Weak, without exception.

After that the three moves all funnel into one random-branch node with **equal weight (1 each)** and **`CannotRepeat`** on all three branches. `CannotRepeat` compares against only the *immediately previous* logged move, so the rule in practice is: **never the same move twice in a row, otherwise a coin flip between the remaining two.**

| Turn | 1 | 2 | 3+ |
| --- | --- | --- | --- |
| Move | Oil Spray (guaranteed) | 50/50 Slam or Rage | 50/50 between the two moves that are not the previous one |

Because the branch is uniform over a "not the last one" chain, the long-run distribution is **1/3 each**. Expect roughly one Rage (+3 Strength) every three turns, i.e. an average ramp near **+1 Strength per turn** across a long fight, and roughly one Weak application every three turns after the guaranteed opener.

Consequences of the no-repeat rule worth planning around:

- Slam can never occur on consecutive turns, so the maximum-damage turn is never back-to-back.
- After a Rage, the next turn is a coin flip between Oil Spray and Slam — the Strength gained is therefore *always* spent on the very next attack, whichever it is.
- The player never faces a fully unknown turn: they face a known set of two, and the intent display resolves it a turn in advance anyway.

**Rage is hidden from the bestiary.** The model explicitly suppresses the Rage move from bestiary display while showing the other two. The Strength ramp is discoverable only in play (or from the buff icon), which is a deliberate information asymmetry rather than a mechanical one — the intent itself still shows a buff icon during the fight.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Initial HP roll (min–max) | 37–39 | **41–42** at the Tough-Enemies tier |
| Oil Spray damage | 8 | **9** at the Deadly-Enemies tier |
| Slam damage | 11 | **12** at the Deadly-Enemies tier |
| Rage damage | 6 | **7** at the Deadly-Enemies tier |
| Rage Strength gain | +3 | +3 (no ascension scaling) |
| Weak applied by Oil Spray | 1 stack | 1 stack (no ascension scaling) |

HP is a genuine roll across a 3-wide band (37/38/39), narrowing to a 2-wide band (41/42) at the Tough tier. Damage feedback reads as **stone**.

Weak is the standard counter-style debuff: **the player's attacks deal 75% damage** while it is up, and it ticks down at the end of the enemy's turn — so one stack taxes exactly the player's next turn.

Strength escalation, assuming the steady-state ~1 Rage per 3 turns:

| Rages so far | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| Strength | 0 | +3 | +6 | +9 | +12 |
| Oil Spray | 8 | 11 | 14 | 17 | 20 |
| Slam | 11 | 14 | 17 | 20 | 23 |
| Rage | 6 | 9 | 12 | 15 | 18 |

Against a 37–42 HP body, most runs never reach the third row. The ramp exists to punish decks that cannot close, not to define the normal shape of the fight.

## Gimmicks

- **Zero defense.** No Block move, no plating, no thorns, no artifact, no retaliation, no damage reduction of any kind. Every point of damage the player deals lands on the body. This is the single most important structural fact: unlike the Sewer Clam, there is no throughput *floor* — chip damage is fully additive.
- **The two riders pull in the same direction.** Oil Spray's Weak slows the player's clock; Rage's Strength speeds up the enemy's. The kit has exactly one strategy — extend the fight and tax the player for the extension — and it applies that strategy through two different moves so that any given turn contributes to it.
- **Weak on the opener is the real design lever.** Because turn 1 is a guaranteed Oil Spray and Weak taxes the *next* player turn, the player's first real offensive turn is always at 75% output. A deck that wants to burst this enemy down in two turns is guaranteed to have one of those two turns discounted.
- **Rage is a soft enrage with no trigger.** It is not gated on HP, turn count, or player behavior — it just comes up about a third of the time. There is no way to prevent it, delay it, or play around it beyond killing faster.
- **Strength persists and stacks without limit,** so a stalled fight (heavy block deck, no damage) degenerates: the Spinner's floor move (Rage, 6) eventually exceeds the player's ceiling of block. This is the one way this weak-tier enemy actually kills.
- **Nothing here is targeted or positional.** No move cares about slot, no move cares about which enemy is which — it is always alone anyway.

## Scaling by act / ascension

- **Act:** none. Sludge Spinner is Underdocks (Act 1) content only, and none of its numbers read the act index. Act index enters only through the multiplayer HP scaler below (Act 1 factor = **1.1**).
- **Ascension:** two independent tier-keyed bumps on different halves of the kit.
  - *Tough Enemies* tier: HP band 37–39 → **41–42**. That is roughly a **+9%** body, and it also removes the low roll — the worst case at this tier (41) is above the best case below it (39).
  - *Deadly Enemies* tier: all three attacks +1 (8→9, 11→12, 6→7). This raises the whole escalation table by 1 without changing its slope.
  - The **Strength gain and the Weak stack are not ascension-scaled**. Ascension makes the Spinner fatter and each individual hit harder; it does not make it ramp faster or debuff harder. The compounding half of the kit is identical at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales by seats × act factor.** On combat entry, enemy max HP is multiplied by (player count × 1.1) for an Act 1 non-boss room. A 2-seat Spinner sits near **81–86 HP** (2 × 1.1 × 37–39), a 3-seat Spinner near **122–129**; at the Tough-Enemies tier, roughly **90–92** and **135–139**.
- **No block to scale.** The general co-op enemy-block multiplier is irrelevant here — the Spinner never gains Block — so the seat-count HP multiplier is the *entire* defensive adjustment. This makes the co-op version of this fight unusually clean: it is exactly the solo fight with a longer body.
- **Weak is applied to the whole player side.** The move receives the full list of player creatures as its targets and applies Weak to that list, so Oil Spray debuffs **every seat at once**, not one seat. The debuff cost of the fight therefore scales *with* the party while the enemy's HP also scales — the tax stays proportional rather than diluting.
- **The attack is single-target.** Only one seat takes the damage on any given move; per-seat incoming pressure drops as seats are added, since damage numbers are seat-count independent.
- **Net effect on the co-op curve:** longer fight, same per-turn damage split across more players, but **table-wide Weak roughly every third turn** and a Strength ramp that now has 2–3× as many turns to compound in. At 3 seats a fight that runs 9–10 turns can see the Spinner at +9 to +12 Strength, i.e. Slam landing for 20–23 on a single unlucky seat. The co-op failure mode is the same as solo — stall out and get run over — but the longer body makes reaching it far more likely.

## Fight-class reasoning — `attrition`

What this fight demands per turn is **uninterrupted damage throughput while paying a recurring tax on it**: the Spinner has no Block, no dodge, and no defensive move at all, so nothing about the fight is a puzzle to solve or a spike to survive — it is purely a question of whether the player's damage clock beats the Spinner's Strength clock over a handful of turns. The guaranteed Oil Spray opener means the player's first offensive turn is always discounted 25%, and every subsequent Oil Spray re-applies that tax, so the fight is explicitly built to measure sustained output rather than a single burst. `spike` is wrong because the biggest hit in the kit (11 base, never twice in a row, always telegraphed) never requires an emergency block turn, and `gimmick` over-reads a plain unbounded Strength stack that has no trigger, no counterplay, and no interaction beyond "kill it sooner." The escalation is a clock on the attrition check, not a phase — which is the same shape as the Sewer Clam, with the throughput floor removed and a damage tax put in its place.
