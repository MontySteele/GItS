# Fat Gremlin — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `FatGremlin`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounter:** `GremlinMercNormal` — the encounter spawns **only** a Gremlin Merc at combat start (slot `merc`). Fat Gremlin (slot `fat`) and Sneaky Gremlin (slot `sneaky`) do not exist until the Merc dies.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Where it comes from

Fat Gremlin is not a monster you are shown at the start of the fight. The Gremlin Merc enters combat carrying a "surprise" buff and a per-player thievery counter. The thievery counter fires **after every one of the Merc's three moves**, stealing up to 20 gold from each player each time (capped at whatever gold that player actually has) and banking the running total on the counter.

When the Merc dies, the surprise buff resolves:

1. It **prevents combat from ending** — so the fight does not resolve on the Merc's death even though the board is momentarily empty.
2. It adds a **Sneaky Gremlin** to the `sneaky` slot and a **Fat Gremlin** to the `fat` slot.
3. Every gold total the Merc banked is transferred onto the Fat Gremlin as a per-player "heist" counter — one instance per player, each tagged with the player it was taken from, each carrying that player's stolen amount.

The Fat Gremlin is therefore best understood as a **loot bag with legs**: it is the physical carrier of the gold the Merc took off you, and it spawns already running for the exit.

## Intent pattern

Fat Gremlin runs a two-state move machine with **zero randomness and zero attacks**. It never deals damage, never gains block, never applies a debuff, and never buffs anything.

1. **Spawned (Stun intent)** — a wake-up animation. Mechanically a no-op; it flips the model's internal "awake" flag, which only changes which hurt animation plays. Deterministic follow-up → Flee.
2. **Flee (Escape intent)** — speaks a banter line, becomes non-interactable, plays the escape animation, and **leaves combat permanently**. Its follow-up is itself, so if the escape were ever interrupted it would simply re-telegraph the escape.

A monster added mid-turn does not act on the turn it appeared; it stands there displaying the intent it will perform on the enemies' *next* turn. The observed sequence is:

| Timing | Fat Gremlin state | Intent shown |
| --- | --- | --- |
| Player turn on which the Merc died | spawned, has not acted | **Stun** |
| Next enemy turn | performs wake-up (nothing happens) | intent flips to **Escape** |
| Player turn | still on the board, killable | **Escape** |
| Next enemy turn | flees — gone for good | — |

Practically the player gets **two of their own turns** to kill it: the turn it appears and the turn after. Those turns are shared with a Sneaky Gremlin that is genuinely attacking (see below), so the real window is "two turns of damage you must spend on the thing that isn't hitting you."

## Numbers

| Value | Base | Tough-Enemies tier |
| --- | --- | --- |
| Starting HP roll | 14–17 | 14–18 |
| Damage dealt | **none** | none |
| Block gained | **none** | none |
| Debuffs applied | **none** | none |
| Turns before it escapes | 2 (stun turn, then flee turn) | unchanged |

HP is rolled inside the band, with a preference for a max-HP value distinct from other enemies on its side where the band allows.

Its companion, for context on what the two-turn window actually costs:

| Sneaky Gremlin (slot `sneaky`) | Base | Ascension tier |
| --- | --- | --- |
| HP | 10–14 | 11–15 (Tough Enemies) |
| Tackle damage, every turn after its own stun turn | 9 | 10 (Deadly Enemies) |

And the Merc that precedes them, for the gold math:

| Gremlin Merc | Base | Tough-Enemies tier |
| --- | --- | --- |
| HP | 47–49 | 51–53 |
| "Gimme" | 7 × 2 hits | 8 × 2 |
| "Double Smash" | 6 × 2 hits, then Weak 2 | 7 × 2, then Weak 2 |
| "Hehe" | 8, then +2 Strength to self | 9, then +2 Strength |

The Merc's cycle is fixed: Gimme → Double Smash → Hehe → Gimme → … Each of those three moves triggers a steal, so the pot the Fat Gremlin ends up carrying is roughly *20 gold per Merc turn* until the player is broke or the Merc dies.

## Gimmicks

- **It is the loot, not the threat.** Killing the Fat Gremlin before it escapes causes each heist counter to pay out as an extra gold reward, credited to the specific player it was stolen from and marked in the run history as loot returned. Let it go and that gold is simply gone.
- **Escaping also taxes the fight's normal gold reward.** The encounter overrides the standard escape-to-reward rule with a bespoke one:
  - Fat Gremlin killed (never escaped) → **100%** of the combat's gold reward.
  - Fat Gremlin escaped, but the Merc had stolen nothing (e.g. the party was already at 0 gold) → **50%**.
  - Fat Gremlin escaped *and* the Merc had stolen gold → **0%**.
  So letting it run costs you twice: the stolen pot *and* the room's own payout.
- **The Merc's death is a fake-out.** Because the surprise buff blocks combat resolution, dropping the Merc does not end the fight; it converts a straightforward damage race into a two-turn timed heist with a live attacker on the board.
- **Two-body split of attention.** The Sneaky Gremlin (10–14 HP, 9 damage per turn once awake) is the punishment for going all-in on the Fat Gremlin, and the Fat Gremlin is the punishment for reflexively killing the thing that is hitting you. Both spawn stunned on the same turn, so the player must pick a target order immediately.
- **Kill timing on the Merc is a real decision.** Every extra Merc turn is another ~20 gold per player onto the pot — which is a *bigger prize* if you can catch the Fat Gremlin and a bigger loss if you cannot. A player who knows the fight can deliberately delay or deliberately rush the Merc kill depending on their remaining burst.
- **Nothing about it is a combat threat.** Zero offense, zero defense, no summons, no thresholds, no enrage. Its entire design pressure is on the reward line, not the HP line.

## Scaling by act / ascension

- **Act:** none. Fat Gremlin is Act 1 content only and its numbers do not read the act index; the only act-derived factor touching it is the multiplayer scaler below (Act 1 factor = 1.1).
- **Ascension:**
  - *Tough Enemies* tier: HP band 14–17 → **14–18**. That is the whole of its ascension scaling — a single point of headroom at the top of the band.
  - *Deadly Enemies* tier: no effect on Fat Gremlin (it has no damage numbers to scale). It does bump Sneaky Gremlin's tackle 9 → 10, and the Tough-Enemies tier raises the Merc's numbers as tabled above.
  - The escape timer is **not** ascension-scaled: two turns at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales hard, and this is the real difficulty knob for this enemy.** On entering combat with more than one player, enemy max HP is multiplied by (player count × act factor); for Act 1 that factor is **1.1**. A 2-player Fat Gremlin sits at roughly **31–40 HP** (2 × 1.1 × a 14–18 roll) and a 3-player one at roughly **46–59**. The escape window stays at two turns regardless. The gimmick therefore gets meaningfully harder per seat: more than double the burst required, same clock.
- **Block scaling is irrelevant here** — it gains none.
- **The heist is per-seat and per-victim.** The Merc applies its thievery counter separately to *each* player and steals from each of them on every move, so a 3-player party feeds three independent pots onto one Fat Gremlin. Killing it pays each player back their own amount; letting it escape wipes all of them at once. One body, party-wide consequence.
- **The gold-proportion penalty is encounter-wide, not per-seat** — if the Fat Gremlin escapes, the whole party's combat gold reward is cut to 50% or 0%.
- Sneaky Gremlin's 9 damage per turn is applied to every player creature (monster attacks target the whole opposing side rather than picking one), so the pressure to abandon the heist and clear the attacker rises with seat count while the burst needed to complete the heist also rises.

## Fight-class reasoning — `gimmick`

The Fat Gremlin never asks the player to survive anything: it has no attack, no block, and no debuff, so on a pure damage-in/damage-out reading it does not exist. What it demands is a **precise two-turn burst check against a moving reward**, taken while a separate enemy is actively hitting you — the per-turn ask is target-selection and tempo, not mitigation or throughput. The correct play changes based on information outside the HP bars (how much gold the Merc banked, whether you can kill 31–40 HP in two turns at two seats, whether eating another 9-damage tackle is worth the pot), which is exactly the shape of a puzzle rather than a race. `spike` and `attrition` are both plainly wrong since it deals no damage at all; `swarm` overstates a two-body board; `mixed` would blur the fact that the encounter's entire distinctive demand is this single timed-heist mechanic layered on an otherwise ordinary Act 1 attacker.
