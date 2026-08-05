# Leaf Slime (S) — behavior dossier

- **Class:** `LeafSlimeS`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounters:** `SlimesWeak` (weak/early-Act-1 pool), `SlimesNormal`, `SlitheringStranglerNormal`
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Where it comes from

Leaf Slime (S) is the small green half of the Act 1 slime family. It never appears alone; every encounter that can spawn it spawns it alongside other slimes:

| Encounter | Composition | Leaf Slime (S) role |
| --- | --- | --- |
| `SlimesWeak` (tagged weak; Act 1 has 3 weak rooms, and on a player's very first run this is forced into the second normal-encounter slot) | 3 bodies: one small slime, one medium slime, one small slime — the two smalls are one Leaf and one Twig (order randomised), the medium is a coin-flip Leaf/Twig | one of two smalls |
| `SlimesNormal` | 4 bodies: Twig Slime (M), Leaf Slime (M), plus both smalls (Leaf + Twig) in a randomised order | one of two smalls |
| `SlitheringStranglerNormal` | Slithering Strangler plus a secondary roll; on the "small slimes" branch it adds **two** smalls drawn independently, so a double Leaf Slime (S) is possible | filler body |

The whole family carries the `Slimes` encounter tag and a slimy hit sound/impact VFX; nothing about the tag alters its numbers.

## Intent pattern

Two moves, no timer, no thresholds, no reactive behaviour, and no self-buffs. The move machine is a random branch feeding two moves, each of which loops straight back into the branch:

1. **Tackle** — a single-hit attack (attack intent showing the damage number).
2. **Goop** — a cast that puts **1 Slimed** into the target's discard pile (status-card intent showing "1").

Both branches are registered with equal weight and with the "cannot repeat" rule. With only two options that rule collapses into **strict alternation**: whichever move it rolls on turn 1 (a true 50/50, since the log is empty), the other is guaranteed next, and it ping-pongs Tackle → Goop → Tackle → Goop for the rest of the fight. The only randomness in the whole enemy is that first coin flip.

Practical consequence: after turn 1 the intent is fully predictable a turn in advance, and it deals damage **on exactly half of its turns**. Its effective damage rate is 1.5–2 per turn averaged.

| Turn | Intent |
| --- | --- |
| 1 | Tackle *or* Goop (50/50) |
| 2 | the other one |
| 3 | back to the turn-1 move |
| … | alternating forever |

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 11–15 | 12–16 (*Tough Enemies*) |
| Tackle damage | **3** | **4** (*Deadly Enemies*) |
| Goop status output | 1 Slimed to discard | unchanged |
| Block gained | **none** | none |
| Debuffs / powers applied | **none** (Slimed is a card, not a debuff) | none |

HP is rolled inside the band at spawn.

**What Slimed actually costs.** Slimed is a 1-cost Status card with Exhaust that draws 1 card when played. It is not a permanently dead card — it is an energy tax: paying 1 energy replaces it and removes it from the combat deck for good. Left unplayed it clogs a draw. So each Goop turn charges the player roughly one energy (or one bad draw) rather than a hard tempo loss, and the clog is self-clearing if the player is willing to pay.

For scale against its own family, the medium Leaf Slime runs the same two-beat shape but harder and *deterministically* (fixed Sticky → Clump → Sticky … cycle, starting on the status move):

| Leaf Slime (M), for context | Base | Ascension tier |
| --- | --- | --- |
| HP | 32–35 | 33–36 (*Tough Enemies*) |
| Clump Shot damage | 8 | 9 (*Deadly Enemies*) |
| Sticky Shot | 2 Slimed to discard | unchanged |

## Gimmicks

- **Alternation is the whole design.** It is a metronome: half its turns are 3 damage, half are one Slimed. There is no ramp, no enrage, no death trigger, no summon, no minion link, no block.
- **Status pressure is additive across the board, damage is not.** In a 4-body slime room the Slimed cards land from multiple slimes on overlapping turns; because the mediums throw 2 each, a bad turn can deposit 4–6 Slimed at once. The small's contribution of 1 is individually trivial and collectively real.
- **AoE is disproportionately good here and the encounter is built to advertise it.** Two smalls at 11–15 HP sitting next to two mediums is the game's early tutorial for sweep effects; single-target decks are punished by having to spend whole turns on 12-HP bodies while the mediums keep firing.
- **No block anywhere in the family**, so nothing about the fight rewards damage-timing or big single hits over chip damage — kill order is purely about removing intent-slots from the board.
- **It is a legal first-run enemy.** `SlimesWeak` is force-placed as the second encounter of a brand-new player's first run, so this monster's numbers are effectively tuning for a starter deck.

## Scaling by act / ascension

- **Act:** none. Leaf Slime (S) is Act 1 content only and reads no act index. The act index enters only through the multiplayer HP/block scaler below (Act 1 factor 1.1).
- **Ascension:**
  - *Tough Enemies* tier: HP band 11–15 → **12–16**. One point at each end.
  - *Deadly Enemies* tier: Tackle 3 → **4**, a 33% bump to its only damage number — proportionally the largest ascension swing it has.
  - Nothing else scales: the alternation, the Slimed count (1), and the move set are identical at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales with seats.** On combat entry, enemy max HP is multiplied by (player count × act factor); Act 1's factor is **1.1**. So a 2-player Leaf Slime (S) sits around **24–33 HP** and a 3-player one around **36–50 HP**, up from an 11–15 solo roll. In a 4-body slime room that multiplies across every body at once, which is what makes this encounter's seat scaling felt.
- **Tackle hits every seat.** Monster attacks in this game target the whole opposing side rather than picking one player, so Tackle is 3 (4 at *Deadly Enemies*) to **each** player, not 3 split among them. Party-wide incoming damage from one small slime is 3 × seat count.
- **Goop hits every seat.** The status move deposits 1 Slimed into **each** player's discard pile. A 3-seat party takes 3 Slimed per Goop turn from this one body — and the encounter's mediums are doing the same at 2 each.
- **Block scaling is irrelevant** — it gains none, so the multiplayer block multiplier never touches it.
- Net: per-seat, the fight is *identical* in what it demands per turn (same damage, same status), while enemy HP roughly doubles/triples. Seat count therefore lengthens the fight without softening the pressure, and lengthening is exactly what compounds a status-clog enemy.

## Fight-class reasoning — `swarm`

Every turn this enemy asks the player to answer a body, not a spike: 3 damage is below any meaningful mitigation threshold, and one Slimed is below any meaningful clog threshold — the demand only becomes real because there are three or four of these on the board simultaneously, and because half of them are chattering statuses into your deck while the other half chip. The correct per-turn play is board-clearing efficiency (AoE, cheap kills, target order that removes intent-slots) rather than block-stacking or burst, which is the defining ask of a swarm. `spike` is wrong because its single hit never threatens; `attrition` is wrong because the damage is too low and the fight is short — the deck pollution is an energy tax, not a grind. `gimmick` overstates a strict two-move alternation with no puzzle in it, and `mixed` would hide the fact that the status half and the damage half both resolve to the same demand: kill the small bodies fast.
