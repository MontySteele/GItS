# Decimillipede (Middle Segment) — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `DecimillipedeSegmentMiddle`
- **Kind:** elite
- **Act:** Act 2 (`Hive`, act index 1)
- **Encounter:** `DecimillipedeElite` — a fixed three-slot fight (`segment1` / `segment2` / `segment3`) holding one Front, one **Middle**, and one Back segment. There is no other encounter, no variant size, and no solo appearance. The three bodies are one creature drawn as three.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## What "Middle Segment" actually is

**All combat logic lives in the shared segment base class.** Front, Middle and Back are three separate classes for one reason: each has to point at a different visual scene. The Middle Segment's *only* class-level difference from its siblings is that when the worm attacks it shakes **two** body-driver nodes (a left and a right one) instead of the one driver Front and Back each shake — it is the segment with a neighbour on both sides.

Every number, every move, every intent, the HP band, the revive rule and the ascension bumps below are **identical across all three segments**. Treat this dossier as the dossier for a Decimillipede segment generally; the Middle's distinctness is cosmetic. What *is* Middle-specific is its **place in the starting rotation** (below).

## Intent pattern

Each segment runs a **fixed, randomness-free three-move cycle**:

1. **Writhe** — *multi-attack* intent, damage × 2.
2. **Constrict** — *single-attack* intent + *debuff* intent. Damage, then Weak on the players it hit.
3. **Bulk** — *single-attack* intent + *buff* intent. Damage, then permanent **Strength +2 on itself**.

Wiring: Writhe → Constrict → Bulk → Writhe → … forever. No branch, no HP threshold, no re-roll while the segment is alive. The state machine must perform its initial state before it may transition, so a segment's first turn is always its assigned starting move.

**The worm is deliberately de-synchronised, and the Middle is the +1.** At encounter generation the game rolls one index in the 3-cycle for the **Front** segment, gives the **Middle** segment `(roll + 1) mod 3`, and the **Back** segment `(roll + 2) mod 3`. Index 0 = Writhe, 1 = Bulk, 2 = Constrict. Consequences:

- All three moves are live **every single turn** of the fight. The party always eats one Writhe, one Constrict and one Bulk per round; only *which body* is doing which rotates.
- The Middle Segment's opening move is therefore never the same as Front's or Back's, and is fully determined once you have read either sibling's first intent.
- The per-turn incoming total is constant in *composition* and rising in *magnitude* — one segment gains +2 Strength every round, forever.

| Turn | Front | **Middle** | Back | Party takes (base, before Strength) |
| --- | --- | --- | --- | --- |
| 1 | Writhe | **Bulk** | Constrict | 5×2 + 6 + 8 = **24**, 1 Weak, +2 Str on Middle |
| 2 | Constrict | **Writhe** | Bulk | **24**, 1 Weak, +2 Str on Back |
| 3 | Bulk | **Constrict** | Writhe | **24**, 1 Weak, +2 Str on Front |

(The offset shown is one of three seeds; the shape is identical in all of them.)

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per segment) | 40–46 | 46–52 (*Tough Enemies* tier) |
| Writhe damage | 5, **twice** (10 total) | 6, twice (12) — *Deadly Enemies* tier |
| Constrict damage | 8 | 9 (*Deadly Enemies* tier) |
| Constrict Weak applied | 1 | 1 — not ascension-scaled |
| Bulk damage | 6 | 7 (*Deadly Enemies* tier) |
| Bulk self-Strength | +2 | +2 — not ascension-scaled |
| Reattach heal | 25 | 25 — not ascension-scaled |

- **No block move of any kind**, no defensive powers. Total pool: **120–138** base across the three bodies (**138–156** at the Tough-Enemies tier) — but see Reattach, which makes "total pool" a soft number.
- HP is **forced even and forced distinct**: after the segments are placed, each rounds its max HP up to an even value and then steps upward in 2s until no teammate shares it, wrapping back to the bottom of the band if it runs off the top. So the three bodies sit on three different even totals (e.g. 42 / 44 / 46). You cannot clear the worm with three identical hits, and the "which one dies first" decision is partly made by the roll.
- Strength is added **per hit**, so Writhe scales at double rate. A segment at +6 Strength deals 11×2 = 22 on Writhe versus 14 on Constrict — its "light" move outgrows its heavy one, the same escalation shape the Corpse Slug uses.
- One Constrict lands every turn, so **Weak uptime is continuous from turn 1** and is re-applied before it can lapse. The player is effectively permanently Weak for the whole fight.

Party-facing escalation (base numbers, no ascension, all three alive, summed across the round):

| Round | Team Strength | Round damage |
| --- | --- | --- |
| 1 | 0 / 0 / 0 | 24 |
| 2 | one segment at +2 | ~28 |
| 3 | two at +2 | ~32 |
| 4 | +2 / +2 / +2 | ~36 |
| 7 | +4 / +4 / +4 | ~48 |

Roughly **+4 damage per round, compounding, with no cap** — under permanent Weak.

## Gimmicks

- **Reattach (the headline).** Every segment enters combat carrying a revive-style power set to **25**. When a segment is reduced to 0 HP, it is **not removed from combat**: it is forced immediately into a do-nothing "dead" state, its body switches to a shrivelled sprite, and it becomes **non-interactable — it cannot be hit and cannot receive powers while down**. On its next turn it performs nothing. On the turn after, it telegraphs a **heal intent**, plays the reattach animation, and **heals back to 25 HP**, re-entering the fight.
- **The revive costs the worm about two turns of output and gives it back a body.** Sequence from the kill: turn of death (already spent) → one blank turn → reattach turn (heal, no attack) → back to attacking. So killing one segment removes roughly one third of the incoming damage for **two rounds only**, then that third returns at 25 HP.
- **Strength survives the death.** The revived segment keeps whatever Strength it had banked from prior Bulks — the buff is not stripped by dying. Chip-killing a segment does not reset its escalation.
- **After reattaching, the segment re-enters the cycle at a random move**, chosen from the three with a no-immediate-repeat rule, rather than resuming where it left off. This is the *only* randomness in the fight, and it means a revive **breaks the clean one-of-each-per-turn rotation** — after a kill the party may face two Constricts (double Weak) or two Writhes (a damage spike) in the same round. Killing a segment therefore makes incoming damage *lumpier*, not just smaller.
- **The fight only ends on a simultaneous finish.** A segment's death triggers the fatal/end-of-combat check **only if every other segment is already dead**. Killing them one at a time in isolation can never win: the first one back up resets the problem. You must land the final blow on the last segment while the other two are still in their down window — a **two-turn kill window**, once you have put two of them down.
- **No summons, no HP-threshold branch, no enrage** beyond the Strength ramp. Everything above is the whole kit.
- Cosmetic/technical notes: segments do not fade after death and are not removed by Doom effects; the worm has its own compendium/bestiary layout (individual segments are hidden from the compendium and shown as one entry); segments cannot be scaled by size-changing effects; all three bodies play the attack shake together on any segment's attack, so the animation reads as one creature.

## Scaling by act / ascension

- **Act:** none. The Decimillipede is Act 2 (`Hive`) elite content exclusively and appears nowhere else. Its numbers do not read the act index; the only act-derived factor that touches it is the multiplayer scaler below (act index 1 → ×1.2).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 40–46 → **46–52** per segment (+18 across the worm).
  - *Deadly Enemies* tier: Writhe 5 → **6** per hit (**+2 per cast**, because it hits twice), Constrict 8 → **9**, Bulk 6 → **7**. Round-one party damage goes 24 → **28**.
  - **Not** ascension-scaled: Writhe hit count, the Weak amount, the Bulk Strength gain (+2), and the Reattach heal (25). Note the shape — the revive threshold stays at 25 while the bodies get up to 6 HP fatter each, so at high ascension the revive is *proportionally* cheaper to re-clear but the escalation clock runs faster.

## Multiplayer / seat-count adjustments

- **HP scales hard.** Enemy max HP is multiplied by (player count × act factor); for a non-boss **Act 2** room that factor is **1.2**. A 2-player segment sits at roughly **96–110** HP and a 3-player segment at roughly **144–166**. A 3-player worm is a pool of **~450 HP** with revives on top. The even/distinct-HP pass runs against these scaled values, so the three bodies stay on three different totals.
- **The Reattach heal scales too.** It is flagged as a multiplayer-scaling power, so the 25 becomes 25 × players × 1.2 — **60** at two seats, **90** at three. A revived segment in co-op comes back at a meaningful fraction of a fresh body, not at chip HP.
- **Damage and Strength do not scale, but attacks are applied per seat.** Writhe, Constrict and Bulk each resolve against the opposing side rather than a single chosen player, and the Constrict Weak lands on the players it hit. Per-seat incoming damage is therefore close to solo — the co-op difficulty is entirely on the HP/revive side.
- **The block scaler is inert here** — the segments have no block move.
- **Segment count is fixed at 3** regardless of seat count.
- **Net effect: co-op makes the gimmick strictly worse.** The win condition is a same-window triple kill, and both levers that govern it move against the party — bodies get 2.4×/3.6× fatter while the revive heal grows by the same factor and the down window stays at two turns. Co-op parties must coordinate a burst finish across three staggered bodies; raw throughput alone will lose to the revive.

## Fight-class reasoning — `mixed`

Per turn the fight demands three different things at once, and no single label covers them. First, **sustained damage spread across three near-identical bodies** whose HP totals are deliberately unequal — a swarm-shaped targeting problem where you must bring all three low *together* rather than efficiently. Second, **defence against a compounding attrition clock**: a guaranteed one-of-each-move round for 24 base damage rising roughly +4 per round with no cap, all of it taken under permanent Weak and with no way to remove the Strength (it survives death). Third, a **gimmick kill-timing gate**: the fight cannot end except by a simultaneous finish inside a two-turn window, and each partial kill re-randomises the rotation, so a botched attempt buys two quiet turns and then hands back a healed, still-buffed body plus a chance at a doubled Writhe or doubled Weak round. `attrition` is the near-miss — the Strength ramp really is the thing that kills you — but calling it attrition would tell Track B to model a flat rising-damage curve and miss that the *player's* per-turn job alternates between spreading damage and holding a burst, which is what actually decides the fight.
