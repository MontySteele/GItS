# Globe Head — behavior dossier

- **Class:** `GlobeHead`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `GlobeHeadNormal` — a solo encounter. One Globe Head, one slot, no minions, no reinforcements. The encounter pre-loads the Galvanized affliction overlay art, which is the tell that the card-tax is the point of the fight.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

There is no randomness in this AI at all. Three moves are wired into a closed ring, each one naming the next as its follow-up, and the machine starts on Shocking Slap:

> **Shocking Slap → Thunder Strike → Galvanic Burst → Shocking Slap → …**

No weights, no repeat limits, no HP-threshold branch, no cooldowns, no conditional nodes. Once the player has seen one full lap they know every turn of the rest of the fight, including the turn they will die on. The state machine's only nuance is the standard "the first move never transitions away," which simply means turn 1 is always the Slap.

| Turn (mod 3) | Move | Telegraph shown | Effect |
| --- | --- | --- | --- |
| 1, 4, 7, … | **Shocking Slap** | single-attack intent **+ debuff** icon | one hit, then **2 Frail** on every opposing player |
| 2, 5, 8, … | **Thunder Strike** | multi-attack intent, **×3** | three separate hits |
| 3, 6, 9, … | **Galvanic Burst** | single-attack intent **+ buff** icon | one hit, then **+2 Strength on itself, permanently** |

**Galvanic Burst is deliberately hidden from the bestiary listing.** The codex shows only Shocking Slap and Thunder Strike, so a player reading the bestiary will not learn that the enemy buffs itself every third turn — they have to discover the ramp in play.

### Why the cycle order matters

The ordering is not arbitrary. Frail is a two-tick counter that ticks down at the end of each enemy turn, so the Frail applied on a Slap turn is live for exactly the player turn that precedes **Thunder Strike**. The fight therefore lands its widest, most block-hungry attack into a player whose Block is being cut by 25%, every single lap. Then Galvanic Burst arrives on a clean turn and raises the whole ring.

Strength is added per hit, so **Thunder Strike absorbs the ramp three times over**. It starts as the weakest turn in the cycle (18 vs 13/16) and becomes the largest by a wide margin.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| HP | **148**, fixed (min = max, no roll) | **158** at the *Tough Enemies* tier |
| Shocking Slap damage | 13 | 14 at the *Deadly Enemies* tier |
| Thunder Strike damage | 6 **×3 hits** (18 total) | 7 ×3 (21 total) at the *Deadly Enemies* tier |
| Galvanic Burst damage | 16 | 17 at the *Deadly Enemies* tier |
| Frail applied by Shocking Slap | 2 | — (fixed) |
| Strength gained by Galvanic Burst | +2 | — (fixed) |
| Galvanic Power counter at combat start | 6 | — (fixed) |

It gains **no Block, ever** — there is no defensive move in the kit. It reads as armored on hit (a cosmetic damage-sfx classification, not damage reduction).

### The damage curve (single player, base tier)

| Turn | Move | Strength | Incoming | Notes |
| --- | --- | --- | --- | --- |
| 1 | Slap | 0 | 13 | +2 Frail |
| 2 | Thunder Strike | 0 | 6/6/6 = **18** | into Frail'd Block |
| 3 | Galvanic Burst | 0 → 2 | 16 | |
| 4 | Slap | 2 | 15 | +2 Frail |
| 5 | Thunder Strike | 2 | 8/8/8 = **24** | into Frail'd Block |
| 6 | Galvanic Burst | 2 → 4 | 18 | |
| 7 | Slap | 4 | 17 | +2 Frail |
| 8 | Thunder Strike | 4 | 10/10/10 = **30** | into Frail'd Block |
| 9 | Galvanic Burst | 4 → 6 | 20 | |
| 10 | Slap | 6 | 19 | |
| 11 | Thunder Strike | 6 | 12/12/12 = **36** | |

Cumulative incoming is 47 by the end of lap 1, 104 by lap 2, 171 by lap 3. A deck that needs four laps (turn 12+) to chew through 148 HP is taking ~40 a turn by then and has almost certainly lost. **The fight's real clock is roughly nine turns**, i.e. ~17 damage per turn of throughput.

## Gimmicks

- **Galvanic Power — the Power-card tax.** The Globe Head enters combat carrying a counter at **6**, and that counter afflicts **every Power card in every player's combat deck with Galvanized**, applied at combat start and again to any Power card that enters combat later (generated, added mid-fight, etc.). Playing a Galvanized card deals **6 damage to its own owner**. This is the entire identity of the encounter: the Globe Head does not care what your deck does, it cares how many Power cards you were planning to set up with.
  - The self-damage is flagged as unpowered and move-typed, so it is **not** amplified by anything the player has and it **is** stoppable by Block — but on the turn a player wants to deploy Powers they are usually spending their whole hand on the deployment, not on defense. A three-Power setup turn costs 18 unmitigated HP on top of whatever the Globe Head is swinging.
  - The counter never decays and never spends. It is 6 per Power card, all fight, regardless of how many are played.
  - It reads as a card affliction with its own overlay, so the player can see the tax on the cards themselves before committing.
- **Frail is timed onto the multi-hit.** As above: the 25% Block cut is always live for the Thunder Strike turn. A player who blocks reactively will be short exactly on the turn the fight spreads damage across three hits.
- **The three-hit shape punishes flat mitigation.** Per-hit reduction effects get triple value on Thunder Strike; a single large Block wall gets no special benefit and is being taxed by Frail at the same time. The alternation between "one 13–19 hit" and "three 6–12 hits" means no single mitigation tool is efficient on both.
- **The buff is permanent and uncapped.** Nothing removes the Strength, nothing caps the laps, and the enemy never spends it. Stalling is strictly losing.
- No summons, no death rattle, no self-heal, no enrage threshold, no block, no HP-gated behaviour change. Everything this enemy does is on the metronome.

## Scaling by act / ascension

- **Act:** none. Globe Head is Act 3 content only and none of its numbers read the act index. The act index is consumed only by the multiplayer HP scaler below (Act 3, non-boss → factor **1.2**).
- **Ascension:** two independent tier-keyed flat swaps.
  - *Tough Enemies* tier: HP 148 → **158** (≈ +0.6 turns of throughput at ~17/turn).
  - *Deadly Enemies* tier: Slap 13 → 14, Thunder Strike 6 → 7 per hit (**18 → 21 total**, the biggest single jump in the kit), Galvanic Burst 16 → 17.
  - **Nothing else scales.** Frail stays 2, Strength gain stays +2, the Galvanic counter stays 6, and the move ring is identical. Ascension steepens the curve slightly and lengthens the race by one lap-ish; it does not change a single decision.

## Multiplayer / seat-count adjustments

- **HP multiplies hard.** Enemy max HP is scaled by (player count × act factor), Act 3 non-boss = **1.2**. That puts the Globe Head at roughly **355** HP at 2 players, **532** at 3, **710** at 4 (≈379 / 568 / 758 at the Tough tier). Scaling is applied at creature creation, before any move resolves.
- **Damage does not scale, but it lands per seat.** Each attack resolves against every opposing player creature, so Slap, Thunder Strike and Galvanic Burst each hit *everyone* for the listed number, and Shocking Slap's **2 Frail is applied to every player**. Party-wide incoming grows linearly with seat count on top of the HP inflation.
- **The Galvanic tax is explicitly per-seat.** The combat-start pass walks every allied creature that is a player and afflicts that player's Power cards; the mid-combat hook does the same for any newly-arriving Power card regardless of owner. **Every seat pays 6 per Power card**, so a party running two Power-heavy builds pays the tax twice over.
- **The Strength ramp is seat-count independent**, which is where co-op bites: the body has 2.4–4.8× the HP but gains Strength on the same three-turn metronome. A 4-player fight that takes ~20 turns sees the Globe Head reach +12 or more Strength, i.e. Thunder Strike at 18×3 = 54 *per seat*. Seat count converts this from a nine-turn race into a genuinely dangerous late-fight ramp — the sharpest co-op difficulty delta in its cohort.
- **The block scaler is irrelevant here** — it has no Block move for the multiplayer block multiplier to touch. Co-op gives this enemy nothing except a longer runway for its own buff.

## Fight-class reasoning — `attrition`

The demand is the same every single turn and it is "have mitigation ready and be putting ~17 damage a turn into one 148 HP body" — there is no board to clear, no random branch to react to, no burst turn that a single defensive card answers, and no window where the correct play changes. What the encounter tests is whether a deck can hold a steady mitigation-plus-throughput line for nine turns against a curve that rises 3–6 points per lap, with two throttles on the player's usual answers: Frail lands precisely on the Block the multi-hit turn needs, and the Galvanic tax charges 6 HP per Power card to anyone whose plan was to scale rather than to race. It is not `spike` (the largest hit is 16–21 and it is on a public timetable), not `swarm` or `gimmick` in the primary sense (one body, and the Galvanized tax is a build tax layered on a straight race rather than the puzzle the fight is about), and not `mixed` because the per-turn ask never actually changes shape — only its size does. The correct Track B read is a flat, steadily-rising demand curve with a hard failure cliff around turn 10.
